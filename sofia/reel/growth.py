"""Growth Engine connection.

The ReelDirector does not invent its own trend: it receives TREND, TARGET KPI,
AUDIENCE and HOOK HYPOTHESIS from the Growth Engine. While publishing is on
HOLD there are no fresh platform metrics, so the engine runs on historical
analytics plus shadow planning — and everything it returns is labelled
accordingly, never as ``REAL`` platform data.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from sofia.core.durable import atomic_write_json
from sofia.core.errors import SofiaError
from sofia.core.verdict import Evidence, Measurement
from sofia.reel.contracts import GrowthInput


class GrowthMemoryError(SofiaError):
    """Raised when the growth memory file cannot be trusted.

    Never downgraded to "no history": an unreadable file means the baseline is
    unknown, which is a different thing from a baseline of zero.
    """


@dataclass
class PublicationRecord:
    """One historical publication and what it actually did."""

    content_id: str
    permalink: str
    hook: str
    format: str
    published_at: str
    metrics: Mapping[str, float]
    evidence: Evidence = Evidence.REAL

    def kpi(self, name: str) -> Optional[float]:
        value = self.metrics.get(name)
        return float(value) if value is not None else None


@dataclass
class GrowthMemory:
    """Historical analytics the next Reel decision is based on.

    Empty memory is reported as empty. It is never padded with zeros, and a
    prediction is never promoted to a measured metric.

    ``records`` holds REAL publications. ``shadow`` holds what the pipeline
    produced while publishing was on HOLD. They are separate lists on purpose:
    a shadow entry must never be counted in a baseline, however many of them
    accumulate.
    """

    records: list[PublicationRecord] = field(default_factory=list)
    shadow: list[dict] = field(default_factory=list)
    source: str = "historical-analytics"

    def __post_init__(self) -> None:
        # The invariant the whole class rests on. A single mislabelled entry
        # would turn a prediction into a REAL baseline, so it is checked where
        # the list is built rather than trusted by convention.
        for record in self.records:
            if record.evidence is not Evidence.REAL:
                raise GrowthMemoryError(
                    f"publication {record.content_id!r} is labelled "
                    f"{record.evidence.value}; only REAL publications belong in "
                    "records (use shadow for anything predicted)"
                )

    @classmethod
    def load(cls, path: str | Path) -> "GrowthMemory":
        p = Path(path)
        if not p.exists():
            return cls(records=[], source=f"{p} (absent)")
        raw = p.read_text(encoding="utf-8")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            # A half-written file is the one thing that must not read as an
            # empty history: that would silently erase every REAL publication
            # from the baseline instead of reporting that it is unknown.
            raise GrowthMemoryError(
                f"growth memory at {p} is not valid JSON ({exc}); "
                f"{len(raw)} bytes on disk. Refusing to continue with an "
                "empty history — restore the file or start a new one explicitly"
            ) from exc
        shadow = list(data.get("shadow", []))
        records = [
            PublicationRecord(
                content_id=r["content_id"],
                permalink=r.get("permalink", ""),
                hook=r.get("hook", ""),
                format=r.get("format", ""),
                published_at=r.get("published_at", ""),
                metrics=dict(r.get("metrics", {})),
                # Files written before the label was persisted only ever held
                # REAL records, so an absent key reads as REAL; a present one
                # is honoured, and __post_init__ rejects anything else.
                evidence=Evidence(r.get("evidence", Evidence.REAL.value)),
            )
            for r in data.get("records", [])
        ]
        return cls(records=records, shadow=shadow, source=str(p))

    def save(self, path: str | Path) -> Path:
        """Persist REAL publications and shadow entries side by side.

        They stay in separate keys so a reload can never mistake one for the
        other, each record carries its evidence label, and the write is atomic:
        this is the only store of REAL platform records, and losing power
        mid-write must not cost us the history.
        """
        return atomic_write_json(
            path,
            {
                "records": [
                    {
                        "content_id": r.content_id,
                        "permalink": r.permalink,
                        "hook": r.hook,
                        "format": r.format,
                        "published_at": r.published_at,
                        "metrics": dict(r.metrics),
                        "evidence": r.evidence.value,
                    }
                    for r in self.records
                ],
                "shadow": list(self.shadow),
            },
        )

    def baseline(self, kpi: str) -> Measurement:
        values = [r.kpi(kpi) for r in self.records]
        values = [v for v in values if v is not None]
        if not values:
            return Measurement.not_measured(
                f"baseline_{kpi}",
                source=self.source,
                reason="no historical publications with this metric",
            )
        return Measurement(
            name=f"baseline_{kpi}",
            value=sum(values) / len(values),
            evidence=Evidence.REAL,
            source=self.source,
            detail={"n": len(values)},
        )

    def best_hooks(self, kpi: str = "retention", top: int = 3) -> list[str]:
        scored = [
            (r.kpi(kpi), r.hook) for r in self.records if r.kpi(kpi) is not None
        ]
        scored.sort(reverse=True)
        return [hook for _, hook in scored[:top]]


@dataclass
class GrowthEngine:
    """Supplies the ReelDirector's input while publishing stays on HOLD."""

    memory: GrowthMemory = field(default_factory=GrowthMemory)
    publishing_hold: bool = True

    def brief_director(
        self,
        *,
        trend: str,
        audience: str,
        hook_hypothesis: str,
        target_kpi: Optional[Mapping[str, float]] = None,
    ) -> GrowthInput:
        """Build the growth input, honestly labelled."""

        kpi = dict(target_kpi or {})
        if not kpi:
            retention = self.memory.baseline("retention")
            if retention.measured:
                # Aim slightly above the measured historical baseline.
                kpi["retention"] = round(float(retention.value) * 1.1, 4)

        # With no REAL analytics to draw on, fall back to the hooks that at
        # least got a Reel to owner review. That is a statement about this
        # pipeline, not about any audience, so it is offered as a hypothesis.
        if not hook_hypothesis:
            prior = self.hooks_that_reached_review()
            if prior:
                hook_hypothesis = prior[-1]

        return GrowthInput(
            trend=trend,
            audience=audience,
            target_kpi=kpi,
            hook_hypothesis=hook_hypothesis,
            evidence=(
                "historical-analytics + shadow planning (publishing on HOLD)"
                if self.publishing_hold
                else "live analytics"
            ),
            shadow_planning=self.publishing_hold,
        )

    def record_outcome(
        self,
        reel_id: str,
        verdict: str,
        scores: Mapping[str, float],
        *,
        hook: str = "",
        trend: str = "",
        blockers: Sequence[str] = (),
        diagnostic: bool = False,
    ) -> dict:
        """Shadow-plan entry: what we would learn if this were published.

        Explicitly ``PREDICTED`` — it never enters the REAL metric stream, and
        it never becomes evidence that the pipeline works on the platform.
        One Reel yields one entry: a retry or a resumed run replaces the
        previous record rather than counting twice, so a Reel that needed three
        attempts does not look like three Reels.
        """
        entry = {
            "reel_id": reel_id,
            "verdict": verdict,
            "scores": dict(scores),
            "hook": hook,
            "trend": trend,
            "blockers": list(blockers),
            "diagnostic": diagnostic,
            "attempts": 1,
            "evidence": Evidence.PREDICTED.value,
            "note": (
                "shadow planning only; no publication occurred, so no REAL metric "
                "exists for this reel"
            ),
        }
        for i, existing in enumerate(self.memory.shadow):
            if existing.get("reel_id") == reel_id:
                entry["attempts"] = int(existing.get("attempts", 1)) + 1
                self.memory.shadow[i] = entry
                return entry
        self.memory.shadow.append(entry)
        return entry

    def observe(self, result: Any, *, diagnostic: bool = False) -> dict:
        """Close the loop: feed a finished Reel back into growth memory.

        While publishing is on HOLD there is nothing REAL to learn from, so what
        is recorded is the pipeline's own outcome — which hooks and trends got
        as far as owner review, and what blocked the rest. That is genuinely
        useful for the next decision and is never presented as audience data.
        """
        brief = getattr(result, "brief", None)
        report = getattr(result, "report", None)
        blockers = (
            [r.name for r in report.blocking] if report is not None else []
        )
        scores = {
            k: v for k, v in dict(getattr(result, "scores", {})).items() if v is not None
        }
        return self.record_outcome(
            getattr(result, "reel_id", ""),
            getattr(getattr(result, "verdict", None), "value", "UNKNOWN"),
            scores,
            hook=getattr(brief, "hook", "") if brief else "",
            trend=getattr(brief, "trend", "") if brief else "",
            blockers=blockers,
            diagnostic=diagnostic,
        )

    def hooks_that_reached_review(self) -> list[str]:
        """Hooks whose Reel passed every gate, newest last.

        Diagnostic runs are excluded: they can never pass, so counting them
        would say nothing.
        """
        return [
            e["hook"]
            for e in self.memory.shadow
            if e["verdict"] == "PASS" and e.get("hook") and not e.get("diagnostic")
        ]

    def learned(self) -> dict:
        """What the engine can honestly say it knows, by evidence class."""
        production = [e for e in self.memory.shadow if not e.get("diagnostic")]
        reached_review = [e for e in production if e["verdict"] == "PASS"]
        blocker_counts: dict[str, int] = {}
        for entry in self.memory.shadow:
            for name in entry.get("blockers", ()):
                blocker_counts[name] = blocker_counts.get(name, 0) + 1
        return {
            "real_publications": len(self.memory.records),
            "real_baselines": {
                kpi: self.memory.baseline(kpi).to_dict()
                for kpi in ("retention", "saves", "shares")
            },
            "shadow_reels": len(self.memory.shadow),
            "shadow_production_reels": len(production),
            "shadow_diagnostic_reels": len(self.memory.shadow) - len(production),
            "shadow_reached_owner_review": len(reached_review),
            "shadow_hooks_that_reached_review": [
                e["hook"] for e in reached_review if e["hook"]
            ],
            "most_common_blockers": dict(
                sorted(blocker_counts.items(), key=lambda kv: -kv[1])[:5]
            ),
            "evidence": Evidence.PREDICTED.value,
            "caveat": (
                "Shadow data describes this pipeline, not any audience. No "
                "publication occurred, so nothing here predicts platform "
                "performance."
            ),
        }

    def status(self) -> dict:
        return {
            "publishing_hold": self.publishing_hold,
            "historical_records": len(self.memory.records),
            "shadow_records": len(self.memory.shadow),
            "memory_source": self.memory.source,
            "baselines": {
                kpi: self.memory.baseline(kpi).to_dict()
                for kpi in ("retention", "saves", "shares")
            },
        }
