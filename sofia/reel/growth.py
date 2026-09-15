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
from typing import Mapping, Optional, Sequence

from sofia.core.verdict import Evidence, Measurement
from sofia.reel.contracts import GrowthInput


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
    """

    records: list[PublicationRecord] = field(default_factory=list)
    source: str = "historical-analytics"

    @classmethod
    def load(cls, path: str | Path) -> "GrowthMemory":
        p = Path(path)
        if not p.exists():
            return cls(records=[], source=f"{p} (absent)")
        data = json.loads(p.read_text(encoding="utf-8"))
        records = [
            PublicationRecord(
                content_id=r["content_id"],
                permalink=r.get("permalink", ""),
                hook=r.get("hook", ""),
                format=r.get("format", ""),
                published_at=r.get("published_at", ""),
                metrics=dict(r.get("metrics", {})),
            )
            for r in data.get("records", [])
        ]
        return cls(records=records, source=str(p))

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

    def record_outcome(self, reel_id: str, verdict: str, scores: Mapping[str, float]) -> dict:
        """Shadow-plan entry: what we would learn if this were published.

        Explicitly ``PREDICTED`` — it never enters the REAL metric stream, and
        it never becomes evidence that the pipeline works on the platform.
        """
        return {
            "reel_id": reel_id,
            "verdict": verdict,
            "scores": dict(scores),
            "evidence": Evidence.PREDICTED.value,
            "note": (
                "shadow planning only; no publication occurred, so no REAL metric "
                "exists for this reel"
            ),
        }

    def status(self) -> dict:
        return {
            "publishing_hold": self.publishing_hold,
            "historical_records": len(self.memory.records),
            "memory_source": self.memory.source,
            "baselines": {
                kpi: self.memory.baseline(kpi).to_dict()
                for kpi in ("retention", "saves", "shares")
            },
        }
