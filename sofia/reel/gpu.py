"""GPU priority arbiter.

Production has priority. When the GPU is busy with an existing production
render, heavy Reel / video / lip-sync experiments **wait**; light work (voice
planning, research, script, editing planning) continues.

The arbiter never kills another job and never clears a lock by hand: it reads
the live device state plus the studio's own lock files and answers "may I run
this class of work right now".
"""

from __future__ import annotations

import enum
import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

from sofia.core.errors import SofiaError


class WorkClass(str, enum.Enum):
    """How expensive a unit of work is, and therefore how it is scheduled."""

    LIGHT = "LIGHT"      # research, script, planning, editing decisions, voice QA
    VOICE = "VOICE"      # TTS synthesis: modest VRAM, may run alongside light work
    HEAVY = "HEAVY"      # video generation, lip-sync, experiments

    @property
    def waits_for_production(self) -> bool:
        return self is WorkClass.HEAVY


class GpuBusy(SofiaError):
    """Raised when heavy work is requested while production holds the GPU."""


@dataclass(frozen=True)
class GpuState:
    available: bool
    name: str = ""
    total_vram_gb: Optional[float] = None
    used_vram_gb: Optional[float] = None
    utilisation_pct: Optional[float] = None
    temperature_c: Optional[float] = None
    reason: str = ""

    @property
    def free_vram_gb(self) -> Optional[float]:
        if self.total_vram_gb is None or self.used_vram_gb is None:
            return None
        return self.total_vram_gb - self.used_vram_gb

    def to_dict(self) -> dict:
        return {
            "available": self.available,
            "name": self.name,
            "total_vram_gb": self.total_vram_gb,
            "used_vram_gb": self.used_vram_gb,
            "free_vram_gb": self.free_vram_gb,
            "utilisation_pct": self.utilisation_pct,
            "temperature_c": self.temperature_c,
            "reason": self.reason,
        }


def probe_gpu() -> GpuState:
    """Read live GPU state via nvidia-smi, or report honestly that there is none."""

    if shutil.which("nvidia-smi") is None:
        return GpuState(available=False, reason="nvidia-smi not present on this machine")
    try:
        proc = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,memory.used,utilization.gpu,temperature.gpu",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except Exception as exc:  # noqa: BLE001
        return GpuState(available=False, reason=f"nvidia-smi failed: {exc}")
    if proc.returncode != 0 or not proc.stdout.strip():
        return GpuState(
            available=False, reason=f"nvidia-smi error: {proc.stderr.strip()[:200]}"
        )
    first = proc.stdout.strip().splitlines()[0]
    parts = [p.strip() for p in first.split(",")]
    try:
        return GpuState(
            available=True,
            name=parts[0],
            total_vram_gb=float(parts[1]) / 1024.0,
            used_vram_gb=float(parts[2]) / 1024.0,
            utilisation_pct=float(parts[3]),
            temperature_c=float(parts[4]),
        )
    except (IndexError, ValueError) as exc:
        return GpuState(available=False, reason=f"unparsable nvidia-smi output: {exc}")


@dataclass
class GpuArbiter:
    """Decides whether a class of work may start right now.

    ``lock_dir`` points at the studio's control-flag directory. A live
    ``gpu_render`` lock owned by production means heavy work waits — the
    arbiter will not clear it, because the owning process decides when it is
    done.
    """

    lock_dir: Optional[Path] = None
    min_free_vram_gb: float = 8.0
    max_utilisation_pct: float = 85.0
    max_temperature_c: float = 84.0
    production_locks: Sequence[str] = ("gpu_render", "company_tick", "ollama_heavy")

    def state(self) -> GpuState:
        return probe_gpu()

    def active_production_locks(self) -> list[str]:
        if self.lock_dir is None or not Path(self.lock_dir).exists():
            return []
        active: list[str] = []
        for lock in self.production_locks:
            for candidate in (
                Path(self.lock_dir) / f"{lock}.lock",
                Path(self.lock_dir) / f"{lock}.flag",
            ):
                if candidate.exists() and self._lock_is_live(candidate):
                    active.append(lock)
                    break
        return active

    def _lock_is_live(self, path: Path) -> bool:
        """A lock is live unless its recorded owner process is provably gone."""
        try:
            raw = path.read_text(encoding="utf-8").strip()
        except OSError:
            return True
        pid: Optional[int] = None
        if raw.isdigit():
            pid = int(raw)
        else:
            try:
                pid = int(json.loads(raw).get("pid"))
            except Exception:  # noqa: BLE001 - unparsable lock is treated as live
                return True
        if pid is None:
            return True
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except OSError:
            return True
        return True

    # ---- decisions -------------------------------------------------------
    def may_run(self, work: WorkClass, *, vram_gb: float = 0.0) -> tuple[bool, str]:
        """Answer, with a reason, whether ``work`` may start now."""

        if work is WorkClass.LIGHT:
            return True, "light work never waits for the GPU"

        locks = self.active_production_locks()
        if locks and work.waits_for_production:
            return False, f"production holds the GPU ({', '.join(locks)}); heavy work waits"

        state = self.state()
        if not state.available:
            if work is WorkClass.VOICE:
                return False, f"no GPU available: {state.reason}"
            return False, f"no GPU available for heavy work: {state.reason}"

        if state.temperature_c is not None and state.temperature_c > self.max_temperature_c:
            return False, f"GPU at {state.temperature_c:.0f}C, above the safety limit"
        if (
            state.utilisation_pct is not None
            and state.utilisation_pct > self.max_utilisation_pct
            and work.waits_for_production
        ):
            return False, f"GPU at {state.utilisation_pct:.0f}% utilisation; heavy work waits"
        free = state.free_vram_gb
        need = max(vram_gb, self.min_free_vram_gb)
        if free is not None and free < need:
            return False, f"only {free:.1f} GB VRAM free, {need:.1f} GB needed"
        return True, "GPU is free enough for this work"

    def require(self, agent_name: str, reel_id: str, *, work: WorkClass = WorkClass.HEAVY,
                vram_gb: float = 0.0) -> None:
        """Raise :class:`GpuBusy` unless the work may proceed."""
        ok, reason = self.may_run(work, vram_gb=vram_gb)
        if not ok:
            raise GpuBusy(f"{agent_name} (reel {reel_id}) cannot start: {reason}")

    def wait_for(
        self,
        work: WorkClass,
        *,
        vram_gb: float = 0.0,
        timeout_s: float = 0.0,
        poll_s: float = 15.0,
    ) -> tuple[bool, str]:
        """Politely wait for the GPU instead of competing with production."""

        deadline = time.monotonic() + timeout_s
        while True:
            ok, reason = self.may_run(work, vram_gb=vram_gb)
            if ok or timeout_s <= 0 or time.monotonic() >= deadline:
                return ok, reason
            time.sleep(min(poll_s, max(0.0, deadline - time.monotonic())))

    def status(self) -> dict:
        state = self.state()
        return {
            "gpu": state.to_dict(),
            "production_locks": self.active_production_locks(),
            "may_run": {
                w.value: dict(zip(("ok", "reason"), self.may_run(w))) for w in WorkClass
            },
        }
