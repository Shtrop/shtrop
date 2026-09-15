"""The Voice Team critics.

Four logical roles, each one a real check that produces a
:class:`~sofia.core.gates.GateResult`:

* :class:`PronunciationCritic` — pronunciation, stress, WER, numbers, names,
  borrowed words;
* :class:`VoiceIdentityCritic` — the voice is still *Sofia*, across RU/UA/EN;
* :class:`ProsodyCritic` — rhythm, pauses, emotion, robotic delivery,
  overacting;
* :class:`SemanticCritic` — the spoken result did not change the script's
  meaning.

All four are fail-closed: when the backend they need is absent or errors, they
return ``NOT_MEASURED`` / ``ERROR`` on a *critical* gate, which blocks.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from sofia.core.errors import BackendUnavailableError
from sofia.core.gates import GateResult, threshold_gate
from sofia.core.verdict import Evidence, Measurement, Verdict
from sofia.voice import text as T
from sofia.voice.audio import AudioStats, analyse_wav
from sofia.voice.backends import VoiceBackends
from sofia.voice.contracts import (
    Language,
    VoiceArtifact,
    VoiceBrief,
    VoiceDefect,
    VoiceDiagnosis,
)


@dataclass(frozen=True)
class VoiceThresholds:
    """Acceptance thresholds. These are floors — never lower them to pass."""

    max_wer: float = 0.08
    max_wer_talking: float = 0.05
    min_identity: float = 0.82
    min_identity_cross_language: float = 0.78
    max_clipping_ratio: float = 0.0005
    min_true_peak_dbfs: float = -30.0
    max_true_peak_dbfs: float = -1.0
    min_rms_dbfs: float = -27.0
    max_rms_dbfs: float = -12.0
    max_longest_pause_s: float = 1.2
    min_dynamic_range_db: float = 4.0
    max_dynamic_range_db: float = 30.0
    max_duration_drift: float = 0.35


@dataclass
class CriticOutcome:
    """A critic's gate result plus any localised diagnoses it produced."""

    result: GateResult
    diagnoses: tuple[VoiceDiagnosis, ...] = ()


# --------------------------------------------------------------------------
class PronunciationCritic:
    """Checks what was actually *said* against what was written."""

    name = "voice.pronunciation"
    role = "PronunciationCritic"

    def __init__(self, backends: VoiceBackends, thresholds: VoiceThresholds) -> None:
        self.backends = backends
        self.thresholds = thresholds

    def review(self, artifact: VoiceArtifact) -> CriticOutcome:
        brief = artifact.brief
        transcript = artifact.transcript
        if transcript is None:
            try:
                if artifact.audio_path is None:
                    raise BackendUnavailableError("no audio artifact to transcribe")
                transcript = self.backends.asr.transcribe(
                    Path(artifact.audio_path), brief.language
                )
                artifact.transcript = transcript
            except BackendUnavailableError as exc:
                return CriticOutcome(
                    GateResult(
                        name=self.name,
                        verdict=Verdict.NOT_MEASURED,
                        critical=True,
                        reason=f"pronunciation cannot be verified: {exc}",
                        measurement=Measurement.not_measured("wer", source="asr"),
                    ),
                    (
                        VoiceDiagnosis(
                            VoiceDefect.NOT_MEASURED,
                            detail=str(exc),
                            critic=self.role,
                        ),
                    ),
                )

        alignment = T.word_error_rate(brief.text, transcript, brief.language)
        wer = Measurement(
            name="wer",
            value=alignment.wer,
            evidence=Evidence.MEASURED_LOCAL,
            source=self.backends.asr.name,
            detail={
                "substitutions": list(alignment.substitutions),
                "deletions": list(alignment.deletions),
                "insertions": list(alignment.insertions),
            },
        )
        artifact.measurements.append(wer)

        limit = (
            self.thresholds.max_wer_talking
            if brief.style.startswith("reel-talking")
            else self.thresholds.max_wer
        )
        diagnoses: list[VoiceDiagnosis] = []

        mismatch = T.language_mismatch(brief.text, transcript, brief.language)
        if mismatch:
            diagnoses.append(
                VoiceDiagnosis(
                    VoiceDefect.WRONG_LANGUAGE,
                    locus=brief.text[:60],
                    detail=mismatch,
                    critic=self.role,
                )
            )

        stress_bad = T.stress_violations(brief.text, dict(brief.lexicon), transcript)
        for word in stress_bad:
            diagnoses.append(
                VoiceDiagnosis(
                    VoiceDefect.WRONG_STRESS,
                    locus=word,
                    detail=f"required spoken form {brief.lexicon[word]!r} not heard",
                    critic=self.role,
                )
            )

        content = T.check_content_preserved(
            brief.text,
            transcript,
            brief.language,
            required=brief.must_pronounce,
            aliases=dict(brief.lexicon),
        )
        for num in content.missing_numbers:
            diagnoses.append(
                VoiceDiagnosis(
                    VoiceDefect.NUMBER_READING,
                    locus=num,
                    detail="number not heard in transcript",
                    critic=self.role,
                )
            )
        for nm in content.missing_names:
            diagnoses.append(
                VoiceDiagnosis(
                    VoiceDefect.NAME_READING,
                    locus=nm,
                    detail="proper name not heard in transcript",
                    critic=self.role,
                )
            )
        for req in content.missing_required:
            diagnoses.append(
                VoiceDiagnosis(
                    VoiceDefect.BORROWED_WORD,
                    locus=req,
                    detail="must-pronounce term not heard in transcript",
                    critic=self.role,
                )
            )

        if alignment.wer > limit:
            for bad in alignment.bad_words()[:6]:
                diagnoses.append(
                    VoiceDiagnosis(
                        VoiceDefect.MISPRONOUNCED_WORD,
                        locus=bad,
                        detail=f"WER {alignment.wer:.3f} exceeds {limit:.3f}",
                        critic=self.role,
                        measurement=wer,
                    )
                )

        if diagnoses:
            worst = diagnoses[0].defect
            return CriticOutcome(
                GateResult(
                    name=self.name,
                    verdict=Verdict.FAIL,
                    critical=True,
                    reason=(
                        f"{len(diagnoses)} pronunciation defect(s); first={worst.value} "
                        f"wer={alignment.wer:.3f}"
                    ),
                    measurement=wer,
                    threshold=limit,
                ),
                tuple(diagnoses),
            )
        return CriticOutcome(
            threshold_gate(
                self.name, wer, limit, critical=True, higher_is_better=False
            )
        )


# --------------------------------------------------------------------------
class VoiceIdentityCritic:
    """Checks the clip is still Sofia — especially across RU / UA / EN.

    Two things must hold and both need a real model:

    1. a Sofia reference voiceprint exists for the language (a generic
       multilingual fallback voice is **not** Sofia);
    2. the measured speaker similarity clears the identity floor.

    Missing either one is ``NOT_MEASURED`` on a critical gate, which blocks.
    """

    name = "voice.identity"
    role = "VoiceIdentityCritic"

    def __init__(self, backends: VoiceBackends, thresholds: VoiceThresholds) -> None:
        self.backends = backends
        self.thresholds = thresholds

    def review(self, artifact: VoiceArtifact) -> CriticOutcome:
        lang = artifact.brief.language
        voiceprint = self.backends.voiceprint(lang)

        if voiceprint.is_generic_fallback:
            return CriticOutcome(
                GateResult(
                    name=self.name,
                    verdict=Verdict.FAIL,
                    critical=True,
                    reason=(
                        f"no Sofia reference voiceprint for {lang.label}; a generic "
                        "fallback voice is not Sofia"
                    ),
                    measurement=Measurement.not_measured(
                        "identity_similarity", source="voiceprint"
                    ),
                ),
                (
                    VoiceDiagnosis(
                        VoiceDefect.IDENTITY_DRIFT,
                        locus=lang.label,
                        detail="missing canonical Sofia voiceprint for this language",
                        critic=self.role,
                    ),
                ),
            )

        try:
            if artifact.audio_path is None:
                raise BackendUnavailableError("no audio artifact")
            score = self.backends.speaker.similarity(
                Path(artifact.audio_path), voiceprint
            )
        except BackendUnavailableError as exc:
            return CriticOutcome(
                GateResult(
                    name=self.name,
                    verdict=Verdict.NOT_MEASURED,
                    critical=True,
                    reason=f"voice identity cannot be verified: {exc}",
                    measurement=Measurement.not_measured(
                        "identity_similarity", source="speaker-embedding"
                    ),
                ),
                (
                    VoiceDiagnosis(
                        VoiceDefect.NOT_MEASURED,
                        locus=lang.label,
                        detail=str(exc),
                        critic=self.role,
                    ),
                ),
            )

        measurement = Measurement(
            name="identity_similarity",
            value=float(score),
            evidence=Evidence.MEASURED_LOCAL,
            source=self.backends.speaker.name,
            detail={"language": lang.value, "speaker": voiceprint.speaker},
        )
        artifact.measurements.append(measurement)
        floor = self.thresholds.min_identity
        result = threshold_gate(self.name, measurement, floor, critical=True)
        if result.verdict is Verdict.PASS:
            return CriticOutcome(result)
        return CriticOutcome(
            result,
            (
                VoiceDiagnosis(
                    VoiceDefect.IDENTITY_DRIFT,
                    locus=lang.label,
                    detail=f"similarity {score:.3f} < {floor:.3f}",
                    critic=self.role,
                    measurement=measurement,
                ),
            ),
        )

    def cross_language(
        self, reference: VoiceArtifact, other: VoiceArtifact
    ) -> CriticOutcome:
        """Compare Sofia in one language against Sofia in another (RU↔UA, RU↔EN)."""

        name = (
            f"{self.name}.cross."
            f"{reference.brief.language.label}-{other.brief.language.label}"
        )
        ref_print = self.backends.voiceprint(reference.brief.language)
        if ref_print.is_generic_fallback or other.audio_path is None:
            return CriticOutcome(
                GateResult(
                    name=name,
                    verdict=Verdict.NOT_MEASURED,
                    critical=True,
                    reason="cross-language identity needs a real reference and audio",
                    measurement=Measurement.not_measured("cross_identity"),
                )
            )
        try:
            score = self.backends.speaker.similarity(Path(other.audio_path), ref_print)
        except BackendUnavailableError as exc:
            return CriticOutcome(
                GateResult(
                    name=name,
                    verdict=Verdict.NOT_MEASURED,
                    critical=True,
                    reason=f"cross-language identity not measurable: {exc}",
                    measurement=Measurement.not_measured("cross_identity"),
                )
            )
        measurement = Measurement(
            name="cross_identity",
            value=float(score),
            evidence=Evidence.MEASURED_LOCAL,
            source=self.backends.speaker.name,
            detail={
                "from": reference.brief.language.value,
                "to": other.brief.language.value,
            },
        )
        return CriticOutcome(
            threshold_gate(
                name,
                measurement,
                self.thresholds.min_identity_cross_language,
                critical=True,
            )
        )


# --------------------------------------------------------------------------
class ProsodyCritic:
    """Rhythm, pauses, emotion, robotic delivery and overacting.

    This critic works from decoded PCM using only the standard library, so it
    produces genuine ``MEASURED_LOCAL`` numbers on any machine.
    """

    name = "voice.prosody"
    role = "ProsodyCritic"

    def __init__(self, backends: VoiceBackends, thresholds: VoiceThresholds) -> None:
        self.backends = backends
        self.thresholds = thresholds

    def review(self, artifact: VoiceArtifact) -> CriticOutcome:
        if not artifact.audio_path or not Path(artifact.audio_path).exists():
            return CriticOutcome(
                GateResult(
                    name=self.name,
                    verdict=Verdict.MISSING,
                    critical=True,
                    reason="no audio artifact to analyse",
                )
            )
        try:
            stats = analyse_wav(artifact.audio_path)
        except Exception as exc:  # noqa: BLE001 - unreadable audio blocks
            return CriticOutcome(
                GateResult(
                    name=self.name,
                    verdict=Verdict.ERROR,
                    critical=True,
                    reason=f"audio could not be analysed: {type(exc).__name__}: {exc}",
                )
            )

        t = self.thresholds
        brief = artifact.brief
        diagnoses: list[VoiceDiagnosis] = []
        problems: list[str] = []

        rate = Measurement(
            "speech_rate_sps",
            stats.speech_rate_sps,
            Evidence.MEASURED_LOCAL,
            unit="syll/s",
            source="stdlib-pcm",
        )
        artifact.measurements.extend(
            [
                rate,
                Measurement("true_peak_dbfs", stats.true_peak_dbfs, Evidence.MEASURED_LOCAL, unit="dBFS", source="stdlib-pcm"),
                Measurement("rms_dbfs", stats.rms_dbfs, Evidence.MEASURED_LOCAL, unit="dBFS", source="stdlib-pcm"),
                Measurement("longest_pause_s", stats.longest_pause_s, Evidence.MEASURED_LOCAL, unit="s", source="stdlib-pcm"),
                Measurement("dynamic_range_db", stats.dynamic_range_db, Evidence.MEASURED_LOCAL, unit="dB", source="stdlib-pcm"),
                Measurement("duration_s", stats.duration_s, Evidence.MEASURED_LOCAL, unit="s", source="stdlib-pcm"),
            ]
        )

        lo, hi = brief.pace.target_sps
        if stats.speech_rate_sps < lo or stats.speech_rate_sps > hi:
            problems.append(
                f"speech rate {stats.speech_rate_sps:.2f}/s outside {brief.pace.value} "
                f"window [{lo}, {hi}]"
            )
            diagnoses.append(
                VoiceDiagnosis(
                    VoiceDefect.PACE_OFF,
                    detail=problems[-1],
                    critic=self.role,
                    measurement=rate,
                )
            )

        if stats.longest_pause_s > t.max_longest_pause_s:
            problems.append(f"dead air {stats.longest_pause_s:.2f}s")
            diagnoses.append(
                VoiceDiagnosis(
                    VoiceDefect.BAD_PAUSES, detail=problems[-1], critic=self.role
                )
            )

        if stats.dynamic_range_db < t.min_dynamic_range_db:
            problems.append(
                f"flat delivery: dynamic range {stats.dynamic_range_db:.1f} dB"
            )
            diagnoses.append(
                VoiceDiagnosis(
                    VoiceDefect.ROBOTIC, detail=problems[-1], critic=self.role
                )
            )
        elif stats.dynamic_range_db > t.max_dynamic_range_db:
            problems.append(
                f"unstable delivery: dynamic range {stats.dynamic_range_db:.1f} dB"
            )
            diagnoses.append(
                VoiceDiagnosis(
                    VoiceDefect.OVERACTED, detail=problems[-1], critic=self.role
                )
            )

        if stats.clipping_ratio > t.max_clipping_ratio:
            problems.append(f"clipping ratio {stats.clipping_ratio:.5f}")
            diagnoses.append(
                VoiceDiagnosis(
                    VoiceDefect.CLIPPING, detail=problems[-1], critic=self.role
                )
            )

        if not (t.min_true_peak_dbfs <= stats.true_peak_dbfs <= t.max_true_peak_dbfs):
            problems.append(f"true peak {stats.true_peak_dbfs:.1f} dBFS out of range")
            diagnoses.append(
                VoiceDiagnosis(
                    VoiceDefect.LOUDNESS, detail=problems[-1], critic=self.role
                )
            )
        if not (t.min_rms_dbfs <= stats.rms_dbfs <= t.max_rms_dbfs):
            problems.append(f"programme loudness {stats.rms_dbfs:.1f} dBFS out of range")
            diagnoses.append(
                VoiceDiagnosis(
                    VoiceDefect.LOUDNESS, detail=problems[-1], critic=self.role
                )
            )

        if brief.target_duration_s:
            drift = abs(stats.duration_s - brief.target_duration_s) / brief.target_duration_s
            if drift > t.max_duration_drift:
                problems.append(
                    f"duration {stats.duration_s:.2f}s drifts {drift:.0%} from target"
                )
                diagnoses.append(
                    VoiceDiagnosis(
                        VoiceDefect.PACE_OFF, detail=problems[-1], critic=self.role
                    )
                )

        artifact.meta["audio_stats"] = stats.to_dict()
        if problems:
            return CriticOutcome(
                GateResult(
                    name=self.name,
                    verdict=Verdict.FAIL,
                    critical=True,
                    reason="; ".join(problems),
                    measurement=rate,
                    detail={"stats": stats.to_dict()},
                ),
                tuple(diagnoses),
            )
        return CriticOutcome(
            GateResult(
                name=self.name,
                verdict=Verdict.PASS,
                critical=True,
                reason=(
                    f"rate={stats.speech_rate_sps:.2f}/s peak={stats.true_peak_dbfs:.1f}dBFS "
                    f"rms={stats.rms_dbfs:.1f}dBFS pause_max={stats.longest_pause_s:.2f}s"
                ),
                measurement=rate,
                detail={"stats": stats.to_dict()},
            )
        )


# --------------------------------------------------------------------------
class SemanticCritic:
    """The spoken result must not change the script's meaning."""

    name = "voice.semantic"
    role = "SemanticCritic"

    def __init__(self, backends: VoiceBackends, thresholds: VoiceThresholds) -> None:
        self.backends = backends
        self.thresholds = thresholds

    def review(self, artifact: VoiceArtifact) -> CriticOutcome:
        brief = artifact.brief
        transcript = artifact.transcript
        if transcript is None:
            try:
                if artifact.audio_path is None:
                    raise BackendUnavailableError("no audio artifact to transcribe")
                transcript = self.backends.asr.transcribe(
                    Path(artifact.audio_path), brief.language
                )
                artifact.transcript = transcript
            except BackendUnavailableError as exc:
                return CriticOutcome(
                    GateResult(
                        name=self.name,
                        verdict=Verdict.NOT_MEASURED,
                        critical=True,
                        reason=f"semantic verification impossible: {exc}",
                        measurement=Measurement.not_measured("semantic_retention"),
                    ),
                    (
                        VoiceDiagnosis(
                            VoiceDefect.NOT_MEASURED,
                            detail=str(exc),
                            critic=self.role,
                        ),
                    ),
                )

        content = T.check_content_preserved(
            brief.text,
            transcript,
            brief.language,
            required=brief.must_pronounce,
            aliases=dict(brief.lexicon),
        )
        ref = set(T.expand_numbers(T.tokenize(brief.text, brief.language), brief.language))
        hyp = set(T.expand_numbers(T.tokenize(transcript, brief.language), brief.language))
        retention = len(ref & hyp) / len(ref) if ref else 1.0
        measurement = Measurement(
            "semantic_retention",
            retention,
            Evidence.MEASURED_LOCAL,
            source="lexical-content-check",
            detail={
                "missing_numbers": list(content.missing_numbers),
                "missing_names": list(content.missing_names),
                "missing_required": list(content.missing_required),
                "invented_words": list(content.extra_content_words),
            },
        )
        artifact.measurements.append(measurement)

        diagnoses: list[VoiceDiagnosis] = []
        losses = (
            list(content.missing_numbers)
            + list(content.missing_names)
            + list(content.missing_required)
        )
        for locus in losses:
            diagnoses.append(
                VoiceDiagnosis(
                    VoiceDefect.SEMANTIC_DRIFT,
                    locus=locus,
                    detail="meaning-bearing item absent from the spoken result",
                    critic=self.role,
                    measurement=measurement,
                )
            )
        if content.extra_content_words:
            diagnoses.append(
                VoiceDiagnosis(
                    VoiceDefect.SEMANTIC_DRIFT,
                    locus=", ".join(content.extra_content_words[:5]),
                    detail="content words present in speech but absent from the script",
                    critic=self.role,
                    measurement=measurement,
                )
            )

        if diagnoses:
            return CriticOutcome(
                GateResult(
                    name=self.name,
                    verdict=Verdict.FAIL,
                    critical=True,
                    reason=(
                        f"semantic drift: {len(diagnoses)} item(s); "
                        f"retention={retention:.3f}"
                    ),
                    measurement=measurement,
                ),
                tuple(diagnoses),
            )
        return CriticOutcome(
            GateResult(
                name=self.name,
                verdict=Verdict.PASS,
                critical=True,
                reason=f"meaning preserved; retention={retention:.3f}",
                measurement=measurement,
            )
        )


#: Names of the critical voice gates. A clip PASSes only when every one of
#: these is present and passing — the registry uses this for fail-closed
#: aggregation, so a critic that silently never ran becomes MISSING.
CRITICAL_VOICE_GATES: tuple[str, ...] = (
    PronunciationCritic.name,
    VoiceIdentityCritic.name,
    ProsodyCritic.name,
    SemanticCritic.name,
)
