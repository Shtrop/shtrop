"""Voice acceptance benchmark.

Runs a language's representative corpus through the Voice Team and records
PASS / REPAIR / HOLD / FAIL per clip. It never reports a rate it did not
measure: clips that could not be produced are counted as ``BLOCKED`` and the
campaign is marked ``NOT_MEASURED`` rather than being scored out of the clips
that happened to work.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from sofia.core.durable import atomic_write_json
from sofia.core.gates import GateResult
from sofia.core.verdict import Verdict
from sofia.voice.contracts import Language, VoiceVerdict
from sofia.voice.corpus import CorpusItem, corpus_for, coverage
from sofia.voice.pipeline import VoiceTeam

#: A campaign is only acceptable if it ran on at least this many clips.
MIN_CLIPS_PER_LANGUAGE = 20


@dataclass
class ClipOutcome:
    clip: CorpusItem
    verdict: Verdict
    reason: str
    repairs: int
    audio_path: Optional[str]
    wer: Optional[float] = None
    identity: Optional[float] = None
    duration_s: Optional[float] = None
    generation_s: float = 0.0

    def to_dict(self) -> dict:
        return {
            "clip": self.clip.to_dict(),
            "verdict": self.verdict.value,
            "reason": self.reason,
            "repairs": self.repairs,
            "audio_path": self.audio_path,
            "wer": self.wer,
            "identity": self.identity,
            "duration_s": self.duration_s,
            "generation_s": round(self.generation_s, 3),
        }


@dataclass
class CampaignReport:
    """Per-language acceptance result."""

    language: Language
    outcomes: list[ClipOutcome] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)
    wall_s: float = 0.0

    # ---- tallies ---------------------------------------------------------
    def count(self, verdict: Verdict) -> int:
        return sum(1 for o in self.outcomes if o.verdict is verdict)

    @property
    def total(self) -> int:
        return len(self.outcomes)

    @property
    def produced(self) -> int:
        """Clips that actually reached verification."""
        return sum(1 for o in self.outcomes if o.audio_path)

    @property
    def verified(self) -> int:
        """Clips whose critical verifiers actually produced a number.

        A clip that was synthesised but could not be transcribed or compared to
        a voiceprint is *not* verified, however good its audio looks.
        """
        return sum(
            1 for o in self.outcomes if o.wer is not None and o.identity is not None
        )

    @property
    def measurable(self) -> bool:
        """Whether a pass rate from this campaign would mean anything.

        Requires enough clips, none blocked, *and* that the critical verifiers
        actually ran. Without that last condition a campaign where nothing
        could be measured would report ``0%`` and read as a quality result
        rather than as an absent measurement.
        """
        return (
            self.produced >= MIN_CLIPS_PER_LANGUAGE
            and self.count(Verdict.BLOCKED) == 0
            and self.verified >= MIN_CLIPS_PER_LANGUAGE
        )

    @property
    def first_pass_rate(self) -> Optional[float]:
        if not self.measurable:
            return None
        first = sum(
            1 for o in self.outcomes if o.verdict is Verdict.PASS and o.repairs == 0
        )
        return first / self.total

    @property
    def final_pass_rate(self) -> Optional[float]:
        if not self.measurable:
            return None
        return self.count(Verdict.PASS) / self.total

    @property
    def repair_rate(self) -> Optional[float]:
        if not self.measurable:
            return None
        return sum(1 for o in self.outcomes if o.repairs > 0) / self.total

    @property
    def verdict(self) -> Verdict:
        """Campaign verdict, fail-closed."""
        if not self.outcomes:
            return Verdict.NOT_MEASURED
        if self.count(Verdict.BLOCKED):
            return Verdict.BLOCKED
        if not self.measurable:
            # Either too few clips reached verification, or the critical
            # verifiers never ran. Reporting FAIL here would blame the voice for
            # a missing instrument.
            return Verdict.NOT_MEASURED
        if self.count(Verdict.FAIL):
            return Verdict.FAIL
        if self.count(Verdict.HOLD):
            return Verdict.HOLD
        return Verdict.PASS

    def mean(self, attr: str) -> Optional[float]:
        values = [
            getattr(o, attr) for o in self.outcomes if getattr(o, attr) is not None
        ]
        return sum(values) / len(values) if values else None

    def to_dict(self) -> dict:
        return {
            "language": self.language.label,
            "verdict": self.verdict.value,
            "coverage": coverage(self.language),
            "clips_total": self.total,
            "clips_produced": self.produced,
            "clips_verified": self.verified,
            "measurable": self.measurable,
            "unmeasurable_reason": (
                None
                if self.measurable
                else (
                    f"only {self.verified}/{self.total} clip(s) had both WER and "
                    f"identity measured; rates would not mean anything"
                )
            ),
            "tally": {
                v.value: self.count(v)
                for v in (
                    Verdict.PASS,
                    Verdict.REPAIR,
                    Verdict.HOLD,
                    Verdict.FAIL,
                    Verdict.BLOCKED,
                )
            },
            "first_pass_rate": self.first_pass_rate,
            "repair_rate": self.repair_rate,
            "final_pass_rate": self.final_pass_rate,
            "mean_wer": self.mean("wer"),
            "mean_identity": self.mean("identity"),
            "wall_s": round(self.wall_s, 2),
            "outcomes": [o.to_dict() for o in self.outcomes],
        }


def run_campaign(
    team: VoiceTeam,
    language: Language,
    *,
    limit: Optional[int] = None,
    report_dir: Optional[Path] = None,
) -> CampaignReport:
    """Run the acceptance campaign for one language."""

    items: Sequence[CorpusItem] = corpus_for(language)
    if limit:
        items = items[:limit]
    report = CampaignReport(language=language)
    started = time.monotonic()

    for item in items:
        brief = team.director.brief(
            item.text,
            language,
            scene=item.scene,
            emotion=item.emotion,
            pace=item.pace,
        )
        verdict: VoiceVerdict = team.produce(brief, clip_id=item.clip_id)
        artifact = verdict.artifact
        outcome = ClipOutcome(
            clip=item,
            verdict=verdict.verdict,
            reason=verdict.reason,
            repairs=len(verdict.repairs),
            audio_path=artifact.audio_path if artifact else None,
            generation_s=artifact.generation_s if artifact else 0.0,
        )
        if artifact:
            wer = artifact.measurement("wer")
            ident = artifact.measurement("identity_similarity")
            dur = artifact.measurement("duration_s")
            outcome.wer = wer.value if wer else None
            outcome.identity = ident.value if ident else None
            outcome.duration_s = dur.value if dur else None
        report.outcomes.append(outcome)

    report.wall_s = time.monotonic() - started
    if report_dir:
        atomic_write_json(
            Path(report_dir) / f"voice_campaign_{language.value}.json",
            report.to_dict(),
        )
    return report


def run_all(
    team: VoiceTeam, *, limit: Optional[int] = None, report_dir: Optional[Path] = None
) -> dict[Language, CampaignReport]:
    return {
        lang: run_campaign(team, lang, limit=limit, report_dir=report_dir)
        for lang in Language
    }


def summarise(reports: dict[Language, CampaignReport]) -> dict:
    return {
        lang.label: {
            "verdict": rep.verdict.value,
            "clips": rep.total,
            "produced": rep.produced,
            "verified": rep.verified,
            "measurable": rep.measurable,
            "first_pass_rate": rep.first_pass_rate,
            "final_pass_rate": rep.final_pass_rate,
            "mean_wer": rep.mean("wer"),
            "mean_identity": rep.mean("identity"),
        }
        for lang, rep in reports.items()
    }


# --------------------------------------------------------------------------
# Cross-language identity
#
# One canonical Sofia must survive the language change. Measuring each language
# against its own voiceprint is not enough: three separate voices can each
# match their own reference and still be three different people. These checks
# compare a clip in one language against the reference of another.
# --------------------------------------------------------------------------
#: The pairs that matter. RU is the champion, so RU↔UA and RU↔EN carry the
#: acceptance decision; UA↔EN is reported for completeness.
DEFAULT_PAIRS: tuple[tuple[Language, Language], ...] = (
    (Language.RU, Language.UA),
    (Language.RU, Language.EN),
    (Language.UA, Language.EN),
)


@dataclass
class CrossLanguageReport:
    """Identity across languages, pair by pair."""

    results: list[Any] = field(default_factory=list)  # list[GateResult]
    samples_per_pair: int = 0

    @property
    def verdict(self) -> Verdict:
        from sofia.core.gates import evaluate_gates

        if not self.results:
            return Verdict.NOT_MEASURED
        return evaluate_gates(self.results).verdict

    def by_pair(self) -> dict[str, str]:
        return {r.name: r.verdict.value for r in self.results}

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict.value,
            "samples_per_pair": self.samples_per_pair,
            "results": [r.to_dict() for r in self.results],
        }


def run_cross_language(
    team: VoiceTeam,
    reports: Mapping[Language, CampaignReport],
    *,
    pairs: Sequence[tuple[Language, Language]] = DEFAULT_PAIRS,
    samples: int = 3,
    report_dir: Optional[Path] = None,
) -> CrossLanguageReport:
    """Check that Sofia in one language is still Sofia in another.

    For each ``(reference_language, other_language)`` pair this takes up to
    ``samples`` produced clips of the other language and compares them against
    the reference language's Sofia voiceprint.
    """

    from sofia.voice.contracts import VoiceArtifact, VoiceBrief

    out = CrossLanguageReport(samples_per_pair=samples)

    for reference_language, other_language in pairs:
        # Only the other language needs audio: the comparison is against the
        # reference language's *voiceprint*, not against one of its clips.
        other_clips = _produced(reports.get(other_language))[:samples]

        if not other_clips:
            out.results.append(
                GateResult(
                    name=(
                        f"voice.identity.cross."
                        f"{reference_language.label}-{other_language.label}"
                    ),
                    verdict=Verdict.NOT_MEASURED,
                    critical=True,
                    reason=(
                        f"no produced {other_language.label} clips; cross-language "
                        "identity cannot be compared"
                    ),
                )
            )
            continue

        # Carries the reference *language* only; cross_language resolves that
        # to the canonical Sofia voiceprint and never reads this audio.
        reference = VoiceArtifact(
            brief=VoiceBrief(language=reference_language, text=""),
            audio_path=None,
            backend="voiceprint",
        )
        for outcome in other_clips:
            other = VoiceArtifact(
                brief=VoiceBrief(language=other_language, text=outcome.clip.text),
                audio_path=outcome.audio_path,
                backend="campaign",
            )
            result = team.identity.cross_language(reference, other)
            # Name the clip so a failure points at a specific take.
            out.results.append(
                GateResult(
                    name=f"{result.result.name}#{outcome.clip.clip_id}",
                    verdict=result.result.verdict,
                    critical=True,
                    reason=result.result.reason,
                    measurement=result.result.measurement,
                    threshold=result.result.threshold,
                )
            )

    if report_dir:
        atomic_write_json(Path(report_dir) / "voice_cross_language.json", out.to_dict())
    return out


def _produced(report: Optional[CampaignReport]) -> list[ClipOutcome]:
    if report is None:
        return []
    return [o for o in report.outcomes if o.audio_path]
