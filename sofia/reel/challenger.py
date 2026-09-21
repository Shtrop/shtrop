"""Champion vs Challenger trials for lip-sync.

New technologies (LongCat, HighSync, whatever comes next) never replace the
proven champion because they are newer. They enter as challengers, run on the
*same* shots, and are measured on the same required metrics.

This module decides nothing on its own. It produces a recommendation; promoting
a challenger to champion is the owner's call, and a trial that could not be
measured recommends nothing at all.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Optional, Sequence

from sofia.core.durable import atomic_write_json
from sofia.core.errors import BackendUnavailableError
from sofia.core.paths import safe_component
from sofia.core.verdict import Evidence, Measurement, Verdict
from sofia.reel.contracts import Shot
from sofia.reel.gpu import GpuArbiter, WorkClass

#: A challenger must be measured on every metric the champion is held to.
REQUIRED_METRICS: tuple[str, ...] = (
    "phoneme_accuracy",
    "mouth_quality",
    "jaw_quality",
    "teeth_quality",
    "eye_quality",
    "identity",
    "face_drift",
)

#: Metrics where lower is better.
LOWER_IS_BETTER: frozenset[str] = frozenset({"face_drift", "av_offset_ms"})

#: Identity may never regress, however good the mouth looks.
IDENTITY_METRIC = "identity"

#: A win must clear this margin to count as a win rather than noise.
MEANINGFUL_MARGIN = 0.01


@dataclass
class ArmResult:
    """One backend's measured performance over the trial shots.

    ``name`` is the arm's identity in this trial — the key it was registered
    under. ``backend`` is what the implementation calls itself, which is often
    the *same string* for every challenger (they share a runner class), so it
    can never be used to tell arms apart.
    """

    name: str
    champion: bool
    backend: str = ""
    metrics: dict[str, Optional[float]] = field(default_factory=dict)
    wall_s: float = 0.0
    failures: list[str] = field(default_factory=list)

    @property
    def measured(self) -> bool:
        return all(self.metrics.get(m) is not None for m in REQUIRED_METRICS)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "backend": self.backend,
            "champion": self.champion,
            "measured": self.measured,
            "metrics": dict(self.metrics),
            "wall_s": round(self.wall_s, 2),
            "failures": list(self.failures),
        }


@dataclass
class TrialReport:
    """Champion against one or more challengers on identical shots."""

    champion: ArmResult
    challengers: list[ArmResult] = field(default_factory=list)
    shots: int = 0

    def comparison(self, challenger: ArmResult) -> dict[str, str]:
        """Per-metric verdict for one challenger against the champion."""
        out: dict[str, str] = {}
        for metric in REQUIRED_METRICS:
            champ = self.champion.metrics.get(metric)
            chal = challenger.metrics.get(metric)
            if champ is None or chal is None:
                out[metric] = "NOT_MEASURED"
                continue
            delta = chal - champ
            if metric in LOWER_IS_BETTER:
                delta = -delta
            if delta > MEANINGFUL_MARGIN:
                out[metric] = "WIN"
            elif delta < -MEANINGFUL_MARGIN:
                out[metric] = "LOSS"
            else:
                out[metric] = "TIE"
        return out

    def recommendation(self, challenger: ArmResult) -> tuple[Verdict, str]:
        """Whether this challenger is worth the owner's attention.

        ``PASS`` means: measured on every required metric, no regression on any
        of them, no identity regression at all, and a real win somewhere. It is
        a recommendation to consider, never a promotion.
        """

        if not self.champion.measured:
            return (
                Verdict.NOT_MEASURED,
                "the champion itself was not fully measured; there is nothing to "
                "compare against",
            )
        if self.champion.failures:
            # Worst-case aggregation only sees the shots an arm survived, so a
            # champion that crashed on most of them has a cherry-picked
            # baseline and would unfairly sink a better challenger.
            return (
                Verdict.NOT_MEASURED,
                f"the champion failed on {len(self.champion.failures)} shot(s), so "
                "its numbers come from a cherry-picked subset; rerun the trial",
            )
        if not challenger.measured:
            missing = [
                m for m in REQUIRED_METRICS if challenger.metrics.get(m) is None
            ]
            return (
                Verdict.NOT_MEASURED,
                f"challenger was not measured on {missing}",
            )
        if challenger.failures:
            return (
                Verdict.FAIL,
                f"challenger failed on {len(challenger.failures)} shot(s): "
                f"{challenger.failures[:2]}",
            )

        table = self.comparison(challenger)
        losses = [m for m, v in table.items() if v == "LOSS"]
        wins = [m for m, v in table.items() if v == "WIN"]

        if table.get(IDENTITY_METRIC) == "LOSS":
            return (
                Verdict.FAIL,
                "identity regressed; no improvement elsewhere can buy that back",
            )
        if losses:
            return (Verdict.FAIL, f"regressed on {losses}")
        if not wins:
            return (
                Verdict.HOLD,
                "no metric improved beyond noise; the champion stands",
            )
        return (
            Verdict.PASS,
            f"improved {wins} with no regression — worth the owner's review "
            "(this is a recommendation, not a promotion)",
        )

    def to_dict(self) -> dict:
        return {
            "shots": self.shots,
            "champion": self.champion.to_dict(),
            "challengers": [
                {
                    **c.to_dict(),
                    "comparison": self.comparison(c),
                    "recommendation": self.recommendation(c)[0].value,
                    "reason": self.recommendation(c)[1],
                }
                for c in self.challengers
            ],
            "promoted": [],
            "note": (
                "Nothing is promoted automatically. A PASS recommendation means "
                "the owner should look, not that the champion has changed."
            ),
        }


MeasureFn = Callable[[Path, Shot], Mapping[str, float]]


def run_trial(
    champion,
    challengers: Mapping[str, object],
    shots: Sequence[Shot],
    audio_for: Mapping[Any, str],
    workdir: Path,
    measure: MeasureFn,
    *,
    gpu: Optional[GpuArbiter] = None,
    gpu_timeout_s: float = 0.0,
) -> TrialReport:
    """Run every arm over the same shots and measure each identically.

    ``measure`` takes the synced video and its shot and returns the metric
    values. It is injected so the trial does not depend on any particular QA
    implementation.

    ``audio_for`` may be keyed by shot index or by its string form, because
    :class:`~sofia.reel.contracts.ReelAssets` stores voice clips under string
    keys while shots carry integer indices.
    """

    talking = [s for s in shots if s.shot_type.needs_lipsync]
    report = TrialReport(
        champion=_run_arm(
            champion, "champion", True, talking, audio_for, workdir, measure,
            gpu=gpu, gpu_timeout_s=gpu_timeout_s,
        ),
        shots=len(talking),
    )
    for name, backend in challengers.items():
        report.challengers.append(
            _run_arm(
                backend, name, False, talking, audio_for, workdir, measure,
                gpu=gpu, gpu_timeout_s=gpu_timeout_s,
            )
        )
    return report


def _run_arm(
    backend,
    label: str,
    is_champion: bool,
    shots: Sequence[Shot],
    audio_for: Mapping[Any, str],
    workdir: Path,
    measure: MeasureFn,
    *,
    gpu: Optional[GpuArbiter] = None,
    gpu_timeout_s: float = 0.0,
) -> ArmResult:
    arm = ArmResult(
        name=label,
        champion=is_champion,
        backend=str(getattr(backend, "name", "")),
    )
    started = time.monotonic()
    collected: dict[str, list[float]] = {m: [] for m in REQUIRED_METRICS}

    for shot in shots:
        audio = audio_for.get(shot.index) or audio_for.get(str(shot.index))
        if not audio:
            arm.failures.append(f"shot {shot.index}: no voice clip")
            continue
        out = (
            Path(workdir)
            / "challenger"
            / safe_component(label, fallback="arm")
            / f"shot{shot.index}.mp4"
        )
        if gpu is not None:
            # A trial is the heavy experiment the GPU rule exists for: it waits
            # for production rather than competing with it. Timing out is not a
            # reason to start anyway — the shot is recorded as unmeasured, and
            # an arm with failures can never be promoted.
            cleared, reason = gpu.wait_for(WorkClass.HEAVY, timeout_s=gpu_timeout_s)
            if not cleared:
                arm.failures.append(f"shot {shot.index}: GPU not available — {reason}")
                continue
        try:
            synced = backend.sync(Path(shot.video_path or ""), Path(audio), out)
            values = measure(Path(synced), shot)
        except BackendUnavailableError as exc:
            arm.failures.append(f"shot {shot.index}: {exc}")
            continue
        except Exception as exc:  # noqa: BLE001 - a crashing arm simply loses
            arm.failures.append(f"shot {shot.index}: {type(exc).__name__}: {exc}")
            continue
        for metric in REQUIRED_METRICS:
            value = values.get(metric)
            if value is not None:
                collected[metric].append(float(value))

    arm.wall_s = time.monotonic() - started
    for metric, values in collected.items():
        # Worst-case across shots: one bad take is not averaged away.
        if not values:
            arm.metrics[metric] = None
        elif metric in LOWER_IS_BETTER:
            arm.metrics[metric] = max(values)
        else:
            arm.metrics[metric] = min(values)
    return arm


def save_trial(report: TrialReport, path: str | Path) -> Path:
    return atomic_write_json(path, report.to_dict())
