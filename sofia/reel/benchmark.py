"""Reel batch benchmark.

Collects what the studio needs to decide whether the pipeline is repeatable:
first-pass rate, repair rate, final pass rate, GPU time, peak VRAM, wall-clock
generation time and how often a human had to step in.

The same honesty rule as the voice campaign applies: a rate is reported only if
the critical verifiers actually ran. One successful Reel is not repeatability,
and a batch where nothing could be measured is ``NOT_MEASURED`` rather than
``0%``.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Mapping, Optional, Sequence

from sofia.core.durable import atomic_write_json
from sofia.core.verdict import Verdict
from sofia.reel.contracts import GrowthInput, ReelResult
from sofia.reel.shots import estimated_cost

#: Below this the batch says nothing about repeatability.
MIN_BATCH = 5


@dataclass
class ReelRun:
    """One Reel produced by the batch."""

    reel_id: str
    arm: str  # "controlled" | "random"
    plan_name: str
    verdict: Verdict
    reason: str
    wall_s: float
    repairs: int
    blocking: tuple[str, ...] = ()
    unmeasured: tuple[str, ...] = ()
    estimated_gpu_s: Optional[float] = None
    peak_vram_gb: Optional[float] = None
    final_path: Optional[str] = None
    scores: Mapping[str, Optional[float]] = field(default_factory=dict)

    @property
    def first_pass(self) -> bool:
        return self.verdict is Verdict.PASS and self.repairs == 0

    @property
    def needed_human(self) -> bool:
        """A run a person must look at before it can go anywhere.

        Anything the pipeline could not settle by itself counts: an
        unmeasurable gate, a hold, a hard failure.
        """
        return self.verdict is not Verdict.PASS

    def to_dict(self) -> dict:
        return {
            "reel_id": self.reel_id,
            "arm": self.arm,
            "plan": self.plan_name,
            "verdict": self.verdict.value,
            "reason": self.reason,
            "wall_s": round(self.wall_s, 2),
            "repairs": self.repairs,
            "blocking": list(self.blocking),
            "unmeasured": list(self.unmeasured),
            "estimated_gpu_s": self.estimated_gpu_s,
            "peak_vram_gb": self.peak_vram_gb,
            "final_path": self.final_path,
            "scores": dict(self.scores),
        }


@dataclass
class BatchReport:
    runs: list[ReelRun] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)
    wall_s: float = 0.0

    def arm(self, name: str) -> list[ReelRun]:
        return [r for r in self.runs if r.arm == name]

    @property
    def total(self) -> int:
        return len(self.runs)

    @property
    def verified(self) -> int:
        """Runs where every critical category actually produced a verdict."""
        return sum(1 for r in self.runs if not r.unmeasured)

    @property
    def measurable(self) -> bool:
        return self.total >= MIN_BATCH and self.verified >= MIN_BATCH

    def _rate(self, predicate: Callable[[ReelRun], bool]) -> Optional[float]:
        if not self.measurable:
            return None
        return sum(1 for r in self.runs if predicate(r)) / self.total

    @property
    def first_pass_rate(self) -> Optional[float]:
        return self._rate(lambda r: r.first_pass)

    @property
    def repair_rate(self) -> Optional[float]:
        return self._rate(lambda r: r.repairs > 0)

    @property
    def final_pass_rate(self) -> Optional[float]:
        return self._rate(lambda r: r.verdict is Verdict.PASS)

    @property
    def manual_intervention_rate(self) -> Optional[float]:
        return self._rate(lambda r: r.needed_human)

    def mean(self, attr: str) -> Optional[float]:
        values = [getattr(r, attr) for r in self.runs if getattr(r, attr) is not None]
        return sum(values) / len(values) if values else None

    @property
    def verdict(self) -> Verdict:
        if not self.runs:
            return Verdict.NOT_MEASURED
        if not self.measurable:
            return Verdict.NOT_MEASURED
        if any(r.verdict is Verdict.FAIL for r in self.runs):
            return Verdict.FAIL
        if any(r.verdict is not Verdict.PASS for r in self.runs):
            return Verdict.HOLD
        return Verdict.PASS

    def blocking_histogram(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for run in self.runs:
            for name in run.blocking:
                counts[name] = counts.get(name, 0) + 1
        return dict(sorted(counts.items(), key=lambda kv: -kv[1]))

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict.value,
            "runs_total": self.total,
            "runs_verified": self.verified,
            "measurable": self.measurable,
            "unmeasurable_reason": (
                None
                if self.measurable
                else (
                    f"only {self.verified}/{self.total} run(s) had every critical "
                    f"category measured (need >= {MIN_BATCH}); rates would not "
                    "mean anything"
                )
            ),
            "arms": {
                arm: {
                    "runs": len(self.arm(arm)),
                    "passed": sum(
                        1 for r in self.arm(arm) if r.verdict is Verdict.PASS
                    ),
                }
                for arm in ("controlled", "random")
            },
            "first_pass_rate": self.first_pass_rate,
            "repair_rate": self.repair_rate,
            "final_pass_rate": self.final_pass_rate,
            "manual_intervention_rate": self.manual_intervention_rate,
            "mean_wall_s": self.mean("wall_s"),
            "mean_estimated_gpu_s": self.mean("estimated_gpu_s"),
            "peak_vram_gb": max(
                (r.peak_vram_gb for r in self.runs if r.peak_vram_gb is not None),
                default=None,
            ),
            "blocking_histogram": self.blocking_histogram(),
            "total_wall_s": round(self.wall_s, 1),
            "runs": [r.to_dict() for r in self.runs],
        }


def _summarise(result: ReelResult) -> tuple[tuple[str, ...], tuple[str, ...]]:
    report = result.report
    if report is None:
        return (), ("no gate report",)
    blocking = tuple(r.name for r in report.blocking)
    unmeasured = tuple(
        r.name
        for r in report.results
        if r.verdict in (Verdict.NOT_MEASURED, Verdict.MISSING, Verdict.ERROR)
    )
    return blocking, unmeasured


def run_batch(
    director,
    growth: GrowthInput,
    plans: Sequence[tuple[str, object]],
    *,
    controlled: int = 5,
    random_runs: int = 5,
    prefix: str = "bench",
    diagnostic: bool = False,
    report_dir: Optional[Path] = None,
    seed: int = 7,
) -> BatchReport:
    """Run a controlled arm and a random arm through the same director.

    ``plans`` is ``(name, ContentPlan)``. The controlled arm repeats the first
    plan, which measures pipeline variance on identical input; the random arm
    samples the pool, which measures behaviour across content.
    """

    import random as _random

    if not plans:
        raise ValueError("a batch needs at least one content plan")
    rng = _random.Random(seed)
    schedule: list[tuple[str, str, object]] = []
    for i in range(controlled):
        name, plan = plans[0]
        schedule.append(("controlled", name, plan))
    for i in range(random_runs):
        name, plan = rng.choice(list(plans))
        schedule.append(("random", name, plan))

    report = BatchReport()
    started = time.monotonic()

    for index, (arm, plan_name, plan) in enumerate(schedule):
        reel_id = f"{prefix}-{arm}-{index:02d}"
        director.creative.content_plan = plan  # AuthoredPlan swap
        director.idea_agent.creative.content_plan = plan
        run_started = time.monotonic()
        result = director.produce(reel_id, growth, diagnostic=diagnostic)
        wall = time.monotonic() - run_started
        blocking, unmeasured = _summarise(result)
        cost = estimated_cost(result.assets.shots) if result.assets.shots else {}
        report.runs.append(
            ReelRun(
                reel_id=reel_id,
                arm=arm,
                plan_name=plan_name,
                verdict=result.verdict,
                reason=result.reason,
                wall_s=wall,
                repairs=len(result.repairs),
                blocking=blocking,
                unmeasured=unmeasured,
                estimated_gpu_s=cost.get("estimated_gpu_s"),
                peak_vram_gb=cost.get("peak_vram_gb"),
                final_path=result.assets.final,
                scores=result.scores,
            )
        )

    report.wall_s = time.monotonic() - started
    if report_dir:
        atomic_write_json(Path(report_dir) / "reel_batch.json", report.to_dict())
    return report
