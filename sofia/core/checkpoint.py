"""Atomic checkpoint store and the Reel stage state machine.

If a session, a GPU or a render dies, work resumes from the last committed
stage instead of restarting from zero. Writes are atomic (temp file -> fsync ->
os.replace) and nothing is ever deleted: superseded states are appended to a
journal.
"""

from __future__ import annotations

import enum
import json
import os
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator, Mapping, Optional, Sequence

from sofia.core.errors import CheckpointError


class StageState(str, enum.Enum):
    """Coarse-grained resumable stages of a Reel.

    The order of declaration is the canonical pipeline order; ``rank`` uses it.
    """

    CREATED = "CREATED"
    BRIEF_DONE = "BRIEF_DONE"
    SCRIPT_DONE = "SCRIPT_DONE"
    SHOTS_DONE = "SHOTS_DONE"
    VOICE_DONE = "VOICE_DONE"
    VIDEO_DONE = "VIDEO_DONE"
    LIPSYNC_DONE = "LIPSYNC_DONE"
    EDIT_DONE = "EDIT_DONE"
    FINAL_QA = "FINAL_QA"
    READY_FOR_OWNER_REVIEW = "READY_FOR_OWNER_REVIEW"
    HELD = "HELD"
    FAILED = "FAILED"

    @property
    def rank(self) -> int:
        return _STAGE_ORDER.index(self) if self in _STAGE_ORDER else -1

    @property
    def terminal(self) -> bool:
        return self in (
            StageState.READY_FOR_OWNER_REVIEW,
            StageState.HELD,
            StageState.FAILED,
        )


_STAGE_ORDER: tuple[StageState, ...] = (
    StageState.CREATED,
    StageState.BRIEF_DONE,
    StageState.SCRIPT_DONE,
    StageState.SHOTS_DONE,
    StageState.VOICE_DONE,
    StageState.VIDEO_DONE,
    StageState.LIPSYNC_DONE,
    StageState.EDIT_DONE,
    StageState.FINAL_QA,
    StageState.READY_FOR_OWNER_REVIEW,
)


def pipeline_stages() -> tuple[StageState, ...]:
    """The canonical forward stage order."""
    return _STAGE_ORDER


@dataclass
class Checkpoint:
    """A single persisted checkpoint."""

    reel_id: str
    stage: StageState
    owner: str
    updated_at: float = field(default_factory=time.time)
    payload: dict[str, Any] = field(default_factory=dict)
    history: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "reel_id": self.reel_id,
            "stage": self.stage.value,
            "owner": self.owner,
            "updated_at": self.updated_at,
            "payload": self.payload,
            "history": self.history,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Checkpoint":
        try:
            return cls(
                reel_id=data["reel_id"],
                stage=StageState(data["stage"]),
                owner=data.get("owner", ""),
                updated_at=float(data.get("updated_at", 0.0)),
                payload=dict(data.get("payload", {})),
                history=list(data.get("history", [])),
            )
        except (KeyError, ValueError) as exc:
            raise CheckpointError(f"corrupt checkpoint: {exc}") from exc

    def artifact(self, key: str) -> Optional[str]:
        return self.payload.get("artifacts", {}).get(key)


class CheckpointStore:
    """Filesystem-backed, atomic, append-only-journal checkpoint store."""

    def __init__(self, root: str | os.PathLike[str]) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    # ---- paths -----------------------------------------------------------
    def _state_path(self, reel_id: str) -> Path:
        return self.root / f"{_safe(reel_id)}.state.json"

    def _journal_path(self, reel_id: str) -> Path:
        return self.root / f"{_safe(reel_id)}.journal.jsonl"

    # ---- api -------------------------------------------------------------
    def exists(self, reel_id: str) -> bool:
        return self._state_path(reel_id).exists()

    def load(self, reel_id: str) -> Optional[Checkpoint]:
        path = self._state_path(reel_id)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CheckpointError(f"checkpoint {path} is not valid JSON: {exc}") from exc
        return Checkpoint.from_dict(data)

    def save(
        self,
        checkpoint: Checkpoint,
        *,
        allow_regression: bool = False,
    ) -> Checkpoint:
        """Persist ``checkpoint`` atomically.

        A backwards stage transition is rejected unless ``allow_regression`` is
        set (the repair router uses it deliberately when re-doing a component).
        """

        previous = self.load(checkpoint.reel_id)
        if previous is not None and not allow_regression:
            if (
                checkpoint.stage.rank >= 0
                and previous.stage.rank > checkpoint.stage.rank
            ):
                raise CheckpointError(
                    f"illegal stage regression for {checkpoint.reel_id}: "
                    f"{previous.stage.value} -> {checkpoint.stage.value}"
                )
        checkpoint.updated_at = time.time()
        entry = {
            "at": checkpoint.updated_at,
            "stage": checkpoint.stage.value,
            "owner": checkpoint.owner,
        }
        checkpoint.history = list(checkpoint.history) + [entry]
        _atomic_write_json(self._state_path(checkpoint.reel_id), checkpoint.to_dict())
        _append_jsonl(self._journal_path(checkpoint.reel_id), entry)
        return checkpoint

    def advance(
        self,
        reel_id: str,
        stage: StageState,
        owner: str,
        *,
        artifacts: Optional[Mapping[str, str]] = None,
        payload: Optional[Mapping[str, Any]] = None,
        allow_regression: bool = False,
    ) -> Checkpoint:
        current = self.load(reel_id) or Checkpoint(
            reel_id=reel_id, stage=StageState.CREATED, owner=owner
        )
        if current.owner and current.owner != owner:
            raise CheckpointError(
                f"reel {reel_id} is owned by {current.owner!r}, not {owner!r}"
            )
        merged = dict(current.payload)
        if payload:
            merged.update(payload)
        if artifacts:
            merged.setdefault("artifacts", {}).update(dict(artifacts))
        current.stage = stage
        current.owner = owner
        current.payload = merged
        return self.save(current, allow_regression=allow_regression)

    def resume_point(self, reel_id: str) -> StageState:
        """The stage a resuming director should continue *from*."""
        cp = self.load(reel_id)
        if cp is None:
            return StageState.CREATED
        return cp.stage

    def journal(self, reel_id: str) -> list[dict[str, Any]]:
        path = self._journal_path(reel_id)
        if not path.exists():
            return []
        out: list[dict[str, Any]] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                out.append(json.loads(line))
        return out

    def list_reels(self) -> list[str]:
        return sorted(p.name[: -len(".state.json")] for p in self.root.glob("*.state.json"))

    def iter_checkpoints(self) -> Iterator[Checkpoint]:
        for reel_id in self.list_reels():
            cp = self.load(reel_id)
            if cp is not None:
                yield cp


def next_stage(stage: StageState) -> Optional[StageState]:
    """The stage that follows ``stage`` in the canonical order."""
    if stage not in _STAGE_ORDER:
        return None
    idx = _STAGE_ORDER.index(stage)
    if idx + 1 >= len(_STAGE_ORDER):
        return None
    return _STAGE_ORDER[idx + 1]


def remaining_stages(stage: StageState) -> Sequence[StageState]:
    """Stages still to run after ``stage`` (used by resume)."""
    if stage not in _STAGE_ORDER:
        return ()
    return _STAGE_ORDER[_STAGE_ORDER.index(stage) + 1 :]


# ---- io helpers ----------------------------------------------------------
def _safe(name: str) -> str:
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in name)


def _atomic_write_json(path: Path, data: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def _append_jsonl(path: Path, entry: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        fh.flush()
        os.fsync(fh.fileno())
