"""Reel critics and the FinalGate.

``MP4 decode PASS != Reel PASS``. Decoding is one necessary check among many;
the FinalGate additionally requires hook, story, identity, realism, video,
voice, lip-sync, edit, subtitles, audio mix, cover, caption↔visual consistency,
CTA and AI-artifact review — each of them critical and fail-closed.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Optional, Sequence

from sofia.core.errors import BackendUnavailableError
from sofia.core.gates import GateReport, GateResult, evaluate_gates, threshold_gate
from sofia.core.verdict import Evidence, Measurement, Verdict
from sofia.reel.backends import ReelBackends
from sofia.reel.contracts import (
    ReelAssets,
    ReelBrief,
    ReelDefect,
    ReelDiagnosis,
    Shot,
    ShotType,
    StoryBeat,
)
from sofia.reel.shots import validate_story
from sofia.reel.subtitles import parse_srt, verify_cues
from sofia.voice.audio import analyse_wav
from sofia.voice.contracts import Language
from sofia.voice.text import normalize


@dataclass(frozen=True)
class ReelThresholds:
    """Hard floors. Never lower one to make a Reel pass."""

    min_identity_face_critical: float = 0.70
    min_identity_talking: float = 0.72
    max_face_drift: float = 0.12
    min_lipsync_confidence: float = 0.80
    max_av_offset_ms: float = 80.0
    min_sharpness: float = 0.55
    max_ai_artifact_score: float = 0.25
    min_voice_over_music_db: float = 9.0
    max_true_peak_dbfs: float = -1.0
    min_duration_s: float = 15.0
    max_duration_s: float = 30.0
    min_hook_score: float = 8.0
    min_category_score: float = 8.0


@dataclass
class CriticOutcome:
    result: GateResult
    diagnoses: tuple[ReelDiagnosis, ...] = ()


def _blocked(
    name: str, reason: str, defect: ReelDefect, *, shot: Optional[int] = None
) -> CriticOutcome:
    """A check that could not run is NOT_MEASURED on a critical gate."""
    return CriticOutcome(
        GateResult(
            name=name,
            verdict=Verdict.NOT_MEASURED,
            critical=True,
            reason=reason,
            measurement=Measurement.not_measured(name),
        ),
        (ReelDiagnosis(defect, detail=reason, critic=name, shot_index=shot),),
    )


# --------------------------------------------------------------------------
class StoryCritic:
    """Hook, arc, scene function, CTA and caption↔visual consistency."""

    name = "reel.story"
    role = "ReelCritic:story"

    def __init__(self, thresholds: ReelThresholds) -> None:
        self.thresholds = thresholds

    def review(
        self, brief: ReelBrief, shots: Sequence[Shot], caption: str = ""
    ) -> CriticOutcome:
        problems = validate_story(shots)
        diagnoses = [
            ReelDiagnosis(ReelDefect.STORY_CONTINUITY, detail=p, critic=self.role)
            for p in problems
        ]

        if not brief.hook.strip():
            diagnoses.append(
                ReelDiagnosis(
                    ReelDefect.BAD_HOOK, detail="brief has no hook", critic=self.role
                )
            )
        else:
            first = shots[0] if shots else None
            if first is not None and first.beat not in (StoryBeat.HOOK, StoryBeat.SETUP):
                diagnoses.append(
                    ReelDiagnosis(
                        ReelDefect.BAD_HOOK,
                        detail="the hook is not in the opening shot",
                        critic=self.role,
                        shot_index=first.index,
                    )
                )

        if not brief.cta.strip():
            diagnoses.append(
                ReelDiagnosis(
                    ReelDefect.BAD_SCRIPT, detail="brief has no CTA", critic=self.role
                )
            )

        # caption <-> visual consistency: the caption may not promise something
        # no shot delivers.
        if caption:
            visual_words = set(
                normalize(" ".join(s.description for s in shots), brief.language).split()
            )
            spoken_words = set(
                normalize(" ".join(s.voice_line for s in shots), brief.language).split()
            )
            caption_words = [
                w
                for w in normalize(caption, brief.language).split()
                if len(w) > 4
            ]
            unsupported = [
                w
                for w in caption_words
                if w not in visual_words and w not in spoken_words
            ]
            if len(unsupported) > max(3, len(caption_words) // 2):
                diagnoses.append(
                    ReelDiagnosis(
                        ReelDefect.STORY_CONTINUITY,
                        locus=", ".join(unsupported[:6]),
                        detail="caption promises content that no shot or line delivers",
                        critic=self.role,
                    )
                )

        total = sum(s.duration_s for s in shots)
        if not (
            self.thresholds.min_duration_s <= total <= self.thresholds.max_duration_s
        ):
            diagnoses.append(
                ReelDiagnosis(
                    ReelDefect.EDIT,
                    detail=(
                        f"planned runtime {total:.1f}s outside "
                        f"[{self.thresholds.min_duration_s}, {self.thresholds.max_duration_s}]s"
                    ),
                    critic=self.role,
                )
            )

        measurement = Measurement(
            "planned_duration_s", total, Evidence.MEASURED_LOCAL, unit="s",
            source="shot-list",
        )
        if diagnoses:
            return CriticOutcome(
                GateResult(
                    name=self.name,
                    verdict=Verdict.FAIL,
                    critical=True,
                    reason="; ".join(d.detail for d in diagnoses[:4]),
                    measurement=measurement,
                ),
                tuple(diagnoses),
            )
        return CriticOutcome(
            GateResult(
                name=self.name,
                verdict=Verdict.PASS,
                critical=True,
                reason=f"SETUP->DEVELOPMENT->PAYOFF intact over {len(shots)} shots",
                measurement=measurement,
            )
        )


# --------------------------------------------------------------------------
class VideoQACritic:
    """Per-shot video quality and identity.

    The identity gate is strict on face-critical shots and is simply not
    applied to B-roll / detail / transition shots, which is what keeps GPU cost
    and identity failures down without weakening the gate where it matters.
    """

    name = "reel.video"
    role = "VideoAgent:qa"

    def __init__(self, backends: ReelBackends, thresholds: ReelThresholds) -> None:
        self.backends = backends
        self.thresholds = thresholds

    def review(self, shots: Sequence[Shot]) -> CriticOutcome:
        missing = [s.index for s in shots if not s.video_path]
        if missing:
            return _blocked(
                self.name,
                f"shots {missing} have no rendered video",
                ReelDefect.SHOT,
                shot=missing[0],
            )
        unreadable = [
            s.index for s in shots if not Path(str(s.video_path)).exists()
        ]
        if unreadable:
            return _blocked(
                self.name,
                f"shots {unreadable} reference a file that does not exist",
                ReelDefect.SHOT,
                shot=unreadable[0],
            )

        diagnoses: list[ReelDiagnosis] = []
        identity_values: list[float] = []
        for shot in shots:
            ident = _measure(shot, "identity")
            drift = _measure(shot, "face_drift")
            sharp = _measure(shot, "sharpness")
            artifacts = _measure(shot, "ai_artifact_score")

            if shot.shot_type.identity_gate:
                if ident is None:
                    return _blocked(
                        self.name,
                        f"shot {shot.index} is {shot.shot_type.value} but identity was "
                        "never measured",
                        ReelDefect.IDENTITY,
                        shot=shot.index,
                    )
                floor = (
                    self.thresholds.min_identity_talking
                    if shot.shot_type is ShotType.TALKING
                    else self.thresholds.min_identity_face_critical
                )
                identity_values.append(ident)
                if ident < floor:
                    diagnoses.append(
                        ReelDiagnosis(
                            ReelDefect.IDENTITY,
                            detail=f"identity {ident:.3f} < {floor:.2f}",
                            critic=self.role,
                            shot_index=shot.index,
                        )
                    )
                if drift is not None and drift > self.thresholds.max_face_drift:
                    diagnoses.append(
                        ReelDiagnosis(
                            ReelDefect.IDENTITY,
                            detail=f"face drift {drift:.3f} > {self.thresholds.max_face_drift}",
                            critic=self.role,
                            shot_index=shot.index,
                        )
                    )
            if sharp is not None and sharp < self.thresholds.min_sharpness:
                diagnoses.append(
                    ReelDiagnosis(
                        ReelDefect.SHOT,
                        detail=f"sharpness {sharp:.3f} below floor",
                        critic=self.role,
                        shot_index=shot.index,
                    )
                )
            if (
                artifacts is not None
                and artifacts > self.thresholds.max_ai_artifact_score
            ):
                diagnoses.append(
                    ReelDiagnosis(
                        ReelDefect.SHOT,
                        detail=f"AI artifact score {artifacts:.3f} too high",
                        critic=self.role,
                        shot_index=shot.index,
                    )
                )

        measurement = (
            Measurement(
                "min_identity",
                min(identity_values),
                Evidence.MEASURED_LOCAL,
                source="video-qa",
            )
            if identity_values
            else Measurement.not_measured("min_identity", source="no face-critical shot")
        )
        if diagnoses:
            return CriticOutcome(
                GateResult(
                    name=self.name,
                    verdict=Verdict.FAIL,
                    critical=True,
                    reason="; ".join(d.detail for d in diagnoses[:4]),
                    measurement=measurement,
                ),
                tuple(diagnoses),
            )
        return CriticOutcome(
            GateResult(
                name=self.name,
                verdict=Verdict.PASS,
                critical=True,
                reason=f"{len(shots)} shots pass video and identity QA",
                measurement=measurement,
            )
        )


def _measure(shot: Shot, name: str) -> Optional[float]:
    for m in shot.measurements:
        if m.name == name and m.measured:
            return float(m.value)  # type: ignore[arg-type]
    return None


# --------------------------------------------------------------------------
class LipSyncCritic:
    """Phoneme, mouth, jaw, teeth, eyes, identity, face drift and A/V timing."""

    name = "reel.lipsync"
    role = "LipSyncAgent:qa"
    REQUIRED = (
        "phoneme_accuracy",
        "mouth_quality",
        "jaw_quality",
        "teeth_quality",
        "eye_quality",
        "identity",
        "face_drift",
        "av_offset_ms",
    )

    def __init__(self, backends: ReelBackends, thresholds: ReelThresholds) -> None:
        self.backends = backends
        self.thresholds = thresholds

    def review(self, shots: Sequence[Shot]) -> CriticOutcome:
        talking = [s for s in shots if s.shot_type.needs_lipsync]
        if not talking:
            return CriticOutcome(
                GateResult(
                    name=self.name,
                    verdict=Verdict.PASS,
                    critical=True,
                    reason="no talking shot in this reel; lip-sync not applicable",
                )
            )
        for shot in talking:
            if not shot.lipsync_path:
                return _blocked(
                    self.name,
                    f"talking shot {shot.index} was never lip-synced",
                    ReelDefect.LIPSYNC,
                    shot=shot.index,
                )
            for metric in self.REQUIRED:
                if _measure(shot, metric) is None:
                    return _blocked(
                        self.name,
                        f"shot {shot.index}: required lip-sync metric {metric!r} "
                        "was not measured",
                        ReelDefect.LIPSYNC,
                        shot=shot.index,
                    )

        diagnoses: list[ReelDiagnosis] = []
        confidences: list[float] = []
        for shot in talking:
            for metric in (
                "phoneme_accuracy",
                "mouth_quality",
                "jaw_quality",
                "teeth_quality",
                "eye_quality",
            ):
                value = _measure(shot, metric)
                assert value is not None
                confidences.append(value)
                if value < self.thresholds.min_lipsync_confidence:
                    diagnoses.append(
                        ReelDiagnosis(
                            ReelDefect.LIPSYNC,
                            locus=metric,
                            detail=f"{metric}={value:.3f} below "
                            f"{self.thresholds.min_lipsync_confidence}",
                            critic=self.role,
                            shot_index=shot.index,
                        )
                    )
            offset = _measure(shot, "av_offset_ms")
            assert offset is not None
            if abs(offset) > self.thresholds.max_av_offset_ms:
                diagnoses.append(
                    ReelDiagnosis(
                        ReelDefect.LIPSYNC,
                        locus="av_offset_ms",
                        detail=f"A/V offset {offset:.0f} ms exceeds "
                        f"{self.thresholds.max_av_offset_ms:.0f} ms",
                        critic=self.role,
                        shot_index=shot.index,
                    )
                )
            ident = _measure(shot, "identity")
            if ident is not None and ident < self.thresholds.min_identity_talking:
                diagnoses.append(
                    ReelDiagnosis(
                        ReelDefect.IDENTITY,
                        detail=f"lip-sync degraded identity to {ident:.3f}",
                        critic=self.role,
                        shot_index=shot.index,
                    )
                )

        measurement = Measurement(
            "lipsync_confidence",
            min(confidences),
            Evidence.MEASURED_LOCAL,
            source=self.backends.lipsync.name,
        )
        if diagnoses:
            return CriticOutcome(
                GateResult(
                    name=self.name,
                    verdict=Verdict.FAIL,
                    critical=True,
                    reason="; ".join(d.detail for d in diagnoses[:4]),
                    measurement=measurement,
                ),
                tuple(diagnoses),
            )
        return CriticOutcome(
            threshold_gate(
                self.name,
                measurement,
                self.thresholds.min_lipsync_confidence,
                critical=True,
            )
        )


# --------------------------------------------------------------------------
class SubtitleCritic:
    """Subtitles must match the real speech and stay readable and in frame."""

    name = "reel.subtitles"
    role = "SubtitleAgent:qa"

    def review(
        self,
        subtitle_path: Optional[str],
        *,
        spoken_text: str,
        language: Language,
        video_duration_s: Optional[float],
        text_top: float,
        text_bottom: float,
        verified: bool = True,
    ) -> CriticOutcome:
        if not subtitle_path or not Path(subtitle_path).exists():
            return _blocked(
                self.name, "no subtitle file was produced", ReelDefect.SUBTITLES
            )
        if not spoken_text.strip():
            return _blocked(
                self.name,
                "no verified speech transcript to check subtitles against",
                ReelDefect.SUBTITLES,
            )
        cues = parse_srt(subtitle_path)
        issues = verify_cues(
            cues,
            spoken_text=spoken_text,
            language=language,
            video_duration_s=video_duration_s,
            text_top=text_top,
            text_bottom=text_bottom,
        )
        measurement = Measurement(
            "subtitle_issues",
            float(len(issues.all_issues())),
            Evidence.MEASURED_LOCAL,
            source="subtitle-verifier",
            detail=issues.to_dict(),
        )
        if not verified:
            # Structural checks did run and are reported, but the text was only
            # compared against the script. Subtitles must match real speech, so
            # this cannot be a PASS.
            return CriticOutcome(
                GateResult(
                    name=self.name,
                    verdict=Verdict.NOT_MEASURED,
                    critical=True,
                    reason=(
                        "subtitle text was compared to the script, not to a verified "
                        "transcript of what was actually said"
                        + (
                            f"; structural issues: {issues.all_issues()[:3]}"
                            if not issues.ok
                            else "; structural checks (timing, readability, line "
                            "breaks, safe zones) all passed"
                        )
                    ),
                    measurement=measurement,
                ),
                (
                    ReelDiagnosis(
                        ReelDefect.NOT_MEASURED,
                        detail="no ASR transcript available to verify subtitles",
                        critic=self.role,
                    ),
                ),
            )
        if issues.all_issues():
            return CriticOutcome(
                GateResult(
                    name=self.name,
                    verdict=Verdict.FAIL,
                    critical=True,
                    reason="; ".join(issues.all_issues()[:4]),
                    measurement=measurement,
                ),
                tuple(
                    ReelDiagnosis(
                        ReelDefect.SUBTITLES, detail=msg, critic=self.role
                    )
                    for msg in issues.all_issues()
                ),
            )
        if issues.not_measured:
            # A check that could not run is not a defect, and not a pass.
            return CriticOutcome(
                GateResult(
                    name=self.name,
                    verdict=Verdict.NOT_MEASURED,
                    critical=True,
                    reason="; ".join(issues.not_measured[:3]),
                    measurement=measurement,
                ),
                tuple(
                    ReelDiagnosis(
                        ReelDefect.NOT_MEASURED, detail=msg, critic=self.role
                    )
                    for msg in issues.not_measured
                ),
            )
        return CriticOutcome(
            GateResult(
                name=self.name,
                verdict=Verdict.PASS,
                critical=True,
                reason=f"{len(cues)} cues match the speech, timing and safe zones",
                measurement=measurement,
            )
        )


# --------------------------------------------------------------------------
class EditorCritic:
    """Strong first frame, fast hook, no dead time, sensible pacing, framing.

    Ducking, safe zones, subtitles and the cover have their own critics; this
    covers what is left of the EditorAgent's brief, and measures it from the
    delivered file rather than from the plan.
    """

    name = "reel.edit"
    role = "EditorAgent:qa"

    def __init__(self, thresholds: "EditThresholds | None" = None) -> None:
        from sofia.reel.edit_qa import EditThresholds

        self.thresholds = thresholds or EditThresholds()

    def review(
        self,
        *,
        final_path: Optional[str],
        shots: Sequence[Shot],
        mix_path: Optional[str],
        editor,
        workdir,
        music_bpm: Optional[float] = None,
        delivered_runtime_s: Optional[float] = None,
    ) -> CriticOutcome:
        from pathlib import Path as _Path

        from sofia.reel.edit_qa import analyse_edit

        if not final_path or not _Path(str(final_path)).exists():
            return _blocked(
                self.name, "no assembled edit exists", ReelDefect.EDIT
            )

        issues = analyse_edit(
            final_path=final_path,
            shots=shots,
            mix_path=mix_path,
            editor=editor,
            workdir=_Path(workdir),
            music_bpm=music_bpm,
            thresholds=self.thresholds,
            delivered_runtime_s=delivered_runtime_s,
        )
        measurement = Measurement(
            "edit_issues",
            float(len(issues.blocking)),
            Evidence.MEASURED_LOCAL,
            source="edit-qa",
            detail=issues.to_dict(),
        )

        # A defect that was measured outranks a check that could not run: both
        # block, but the reason the owner reads should name what is actually
        # wrong rather than what was merely unknown.
        if issues.blocking:
            return CriticOutcome(
                GateResult(
                    name=self.name,
                    verdict=Verdict.FAIL,
                    critical=True,
                    reason="; ".join(issues.blocking[:4]),
                    measurement=measurement,
                ),
                tuple(
                    ReelDiagnosis(ReelDefect.EDIT, detail=msg, critic=self.role)
                    for msg in issues.blocking
                ),
            )

        if issues.not_measured:
            return CriticOutcome(
                GateResult(
                    name=self.name,
                    verdict=Verdict.NOT_MEASURED,
                    critical=True,
                    reason="; ".join(issues.not_measured[:3]),
                    measurement=measurement,
                ),
                tuple(
                    ReelDiagnosis(
                        ReelDefect.NOT_MEASURED, detail=msg, critic=self.role
                    )
                    for msg in issues.not_measured
                ),
            )

        m = issues.measurements
        note = (
            f"hook {m.get('hook_s', 0):.1f}s, {m.get('shots', 0)} shots, "
            f"{m.get('cuts_per_10s', 0):.1f} cuts/10s, "
            f"dead air {m.get('longest_silence_s', 0):.2f}s"
        )
        if issues.advisory:
            note += f" (advisory: {issues.advisory[0]})"
        return CriticOutcome(
            GateResult(
                name=self.name,
                verdict=Verdict.PASS,
                critical=True,
                reason=note,
                measurement=measurement,
            )
        )


# --------------------------------------------------------------------------
class AudioMixCritic:
    """Music must not fight the voice; ducking is verified, not assumed."""

    name = "reel.audio_mix"
    role = "Music/SFX Agent:qa"

    def __init__(self, thresholds: ReelThresholds) -> None:
        self.thresholds = thresholds

    def review(
        self,
        *,
        voice_stem: Optional[str],
        music_stem: Optional[str],
        final_mix: Optional[str],
        sfx: Sequence[str] = (),
    ) -> CriticOutcome:
        if not final_mix or not Path(final_mix).exists():
            return _blocked(
                self.name, "no final audio mix to analyse", ReelDefect.MUSIC
            )
        try:
            mix = analyse_wav(final_mix)
        except Exception as exc:  # noqa: BLE001
            return CriticOutcome(
                GateResult(
                    name=self.name,
                    verdict=Verdict.ERROR,
                    critical=True,
                    reason=f"final mix could not be analysed: {exc}",
                ),
                (
                    ReelDiagnosis(
                        ReelDefect.MUSIC, detail=str(exc), critic=self.role
                    ),
                ),
            )

        diagnoses: list[ReelDiagnosis] = []
        if mix.true_peak_dbfs > self.thresholds.max_true_peak_dbfs:
            diagnoses.append(
                ReelDiagnosis(
                    ReelDefect.MUSIC,
                    detail=f"true peak {mix.true_peak_dbfs:.1f} dBFS above ceiling",
                    critic=self.role,
                )
            )
        if mix.clipping:
            diagnoses.append(
                ReelDiagnosis(
                    ReelDefect.MUSIC,
                    detail=f"mix clips ({mix.clipping_ratio:.5f} of samples)",
                    critic=self.role,
                )
            )

        # SFX are optional by design — the brief asks for them only where they
        # strengthen a scene. But a declared SFX must exist and must not fight
        # the voice, so an empty list passes and a broken one does not.
        for path in sfx:
            if not Path(path).exists():
                diagnoses.append(
                    ReelDiagnosis(
                        ReelDefect.MUSIC,
                        locus=path,
                        detail="declared SFX file does not exist",
                        critic=self.role,
                    )
                )
                continue
            try:
                cue = analyse_wav(path)
            except Exception as exc:  # noqa: BLE001 - an unreadable cue blocks
                diagnoses.append(
                    ReelDiagnosis(
                        ReelDefect.MUSIC,
                        locus=path,
                        detail=f"SFX could not be analysed: {exc}",
                        critic=self.role,
                    )
                )
                continue
            if cue.true_peak_dbfs > self.thresholds.max_true_peak_dbfs:
                diagnoses.append(
                    ReelDiagnosis(
                        ReelDefect.MUSIC,
                        locus=path,
                        detail=(
                            f"SFX peaks at {cue.true_peak_dbfs:.1f} dBFS, above the "
                            "programme ceiling"
                        ),
                        critic=self.role,
                    )
                )

        headroom: Optional[float] = None
        if voice_stem and music_stem and Path(voice_stem).exists() and Path(music_stem).exists():
            try:
                voice = analyse_wav(voice_stem)
                music = analyse_wav(music_stem)
                headroom = voice.rms_dbfs - music.rms_dbfs
            except Exception:  # noqa: BLE001 - stems optional, mix already checked
                headroom = None
        if headroom is None:
            return _blocked(
                self.name,
                "voice and music stems are required to verify ducking; "
                "a mixed-down file alone cannot prove the voice is clear",
                ReelDefect.MUSIC,
            )
        if headroom < self.thresholds.min_voice_over_music_db:
            diagnoses.append(
                ReelDiagnosis(
                    ReelDefect.MUSIC,
                    detail=(
                        f"voice sits only {headroom:.1f} dB over the music bed "
                        f"(need {self.thresholds.min_voice_over_music_db:.0f} dB); "
                        "ducking is insufficient"
                    ),
                    critic=self.role,
                )
            )

        measurement = Measurement(
            "voice_over_music_db",
            headroom,
            Evidence.MEASURED_LOCAL,
            unit="dB",
            source="stdlib-pcm",
        )
        if diagnoses:
            return CriticOutcome(
                GateResult(
                    name=self.name,
                    verdict=Verdict.FAIL,
                    critical=True,
                    reason="; ".join(d.detail for d in diagnoses[:3]),
                    measurement=measurement,
                ),
                tuple(diagnoses),
            )
        return CriticOutcome(
            GateResult(
                name=self.name,
                verdict=Verdict.PASS,
                critical=True,
                reason=(
                    f"voice {headroom:.1f} dB over music, peak "
                    f"{mix.true_peak_dbfs:.1f} dBFS"
                ),
                measurement=measurement,
            )
        )


# --------------------------------------------------------------------------
class CoverCritic:
    """Every reel needs its own cover candidate.

    Composition is measured here; face, identity and brand need models and stay
    ``NOT_MEASURED`` without them. A composition defect is reported as a FAIL
    even when the model metrics are absent — a black or horizontal cover is a
    known-bad answer, not an unknown one.
    """

    name = "reel.cover"
    role = "CoverAgent:qa"

    def __init__(self, thresholds=None) -> None:
        from sofia.reel.cover_qa import CoverThresholds

        self.thresholds = thresholds or CoverThresholds()

    def review(
        self,
        cover_path: Optional[str],
        measurements: Mapping[str, Optional[float]],
        *,
        cover_ppm: Optional[str] = None,
    ) -> CriticOutcome:
        from sofia.reel.cover_qa import analyse_cover

        if not cover_path or not Path(cover_path).exists():
            return _blocked(
                self.name, "no cover candidate was produced", ReelDefect.COVER
            )

        issues = analyse_cover(
            cover_ppm or cover_path, measurements, thresholds=self.thresholds
        )
        identity = issues.measurements.get("face_identity")
        measurement = (
            Measurement(
                "cover_identity",
                float(identity),
                Evidence.MEASURED_LOCAL,
                source="cover-qa",
                detail=issues.to_dict(),
            )
            if identity is not None
            else Measurement.not_measured(
                "cover_identity", source="cover-qa", **issues.to_dict()
            )
        )

        # A composition defect is a known-bad answer and outranks "unmeasured".
        if issues.composition:
            return CriticOutcome(
                GateResult(
                    name=self.name,
                    verdict=Verdict.FAIL,
                    critical=True,
                    reason="; ".join(issues.composition[:3]),
                    measurement=measurement,
                ),
                tuple(
                    ReelDiagnosis(ReelDefect.COVER, detail=msg, critic=self.role)
                    for msg in issues.composition
                ),
            )

        if issues.not_measured:
            return CriticOutcome(
                GateResult(
                    name=self.name,
                    verdict=Verdict.NOT_MEASURED,
                    critical=True,
                    reason="; ".join(issues.not_measured[:3]),
                    measurement=measurement,
                ),
                tuple(
                    ReelDiagnosis(
                        ReelDefect.NOT_MEASURED, detail=msg, critic=self.role
                    )
                    for msg in issues.not_measured
                ),
            )

        m = issues.measurements
        return CriticOutcome(
            GateResult(
                name=self.name,
                verdict=Verdict.PASS,
                critical=True,
                reason=(
                    f"composition ok (contrast {m.get('contrast', 0):.2f}, "
                    f"aspect {m.get('aspect_ratio', 0):.2f}); face, identity and "
                    "brand all measured and passing"
                ),
                measurement=measurement,
            )
        )


# --------------------------------------------------------------------------
@dataclass
class PerceptualSample:
    """One human/VLM look at an artifact.

    Numerical scores can all look fine while the footage has dead eyes, a
    morphing face, a bad mouth, fake motion or no story. Those are recorded
    here and any one of them blocks.
    """

    bucket: str  # BEST | RANDOM | FAIL
    artifact: str
    reviewer: str
    dead_eyes: bool = False
    face_morph: bool = False
    bad_mouth: bool = False
    fake_motion: bool = False
    bad_story: bool = False
    notes: str = ""

    @property
    def defects(self) -> list[str]:
        return [
            key
            for key in ("dead_eyes", "face_morph", "bad_mouth", "fake_motion", "bad_story")
            if getattr(self, key)
        ]

    def to_dict(self) -> dict:
        return {
            "bucket": self.bucket,
            "artifact": self.artifact,
            "reviewer": self.reviewer,
            "defects": self.defects,
            "notes": self.notes,
        }


class PerceptualReviewGate:
    """Requires BEST, RANDOM and FAIL samples to have actually been looked at."""

    name = "reel.perceptual"
    role = "ReelCritic:perceptual"
    BUCKETS = ("BEST", "RANDOM", "FAIL")

    def review(self, samples: Sequence[PerceptualSample]) -> CriticOutcome:
        present = {s.bucket for s in samples}
        missing = [b for b in self.BUCKETS if b not in present]
        if missing:
            return _blocked(
                self.name,
                f"perceptual review incomplete: {missing} bucket(s) never reviewed "
                "(looking only at the best results is not a review)",
                ReelDefect.NOT_MEASURED,
            )
        flagged = [s for s in samples if s.defects]
        measurement = Measurement(
            "perceptual_defects",
            float(len(flagged)),
            Evidence.AI_ANALYSIS,
            source="perceptual-review",
            detail={"samples": [s.to_dict() for s in samples]},
        )
        if flagged:
            return CriticOutcome(
                GateResult(
                    name=self.name,
                    verdict=Verdict.HOLD,
                    critical=True,
                    reason="; ".join(
                        f"{s.bucket}:{s.artifact}:{'/'.join(s.defects)}" for s in flagged[:4]
                    ),
                    measurement=measurement,
                ),
                tuple(
                    ReelDiagnosis(
                        _perceptual_defect(s.defects[0]),
                        locus=s.artifact,
                        detail=f"perceptual: {', '.join(s.defects)} ({s.notes})",
                        critic=self.role,
                    )
                    for s in flagged
                ),
            )
        return CriticOutcome(
            GateResult(
                name=self.name,
                verdict=Verdict.PASS,
                critical=True,
                reason=f"{len(samples)} samples reviewed across BEST/RANDOM/FAIL, none flagged",
                measurement=measurement,
            )
        )


def _perceptual_defect(flag: str) -> ReelDefect:
    return {
        "dead_eyes": ReelDefect.SHOT,
        "face_morph": ReelDefect.IDENTITY,
        "bad_mouth": ReelDefect.LIPSYNC,
        "fake_motion": ReelDefect.SHOT,
        "bad_story": ReelDefect.STORY_CONTINUITY,
    }.get(flag, ReelDefect.NOT_MEASURED)


def sample_for_review(
    artifacts: Sequence[str],
    scores: Mapping[str, float],
    *,
    rng: Optional[random.Random] = None,
) -> dict[str, Optional[str]]:
    """Pick the BEST, a RANDOM and the worst (FAIL) artifact to look at."""

    if not artifacts:
        return {"BEST": None, "RANDOM": None, "FAIL": None}
    rng = rng or random.Random(0)
    ranked = sorted(artifacts, key=lambda a: scores.get(a, 0.0))
    return {
        "BEST": ranked[-1],
        "FAIL": ranked[0],
        "RANDOM": rng.choice(artifacts),
    }


# --------------------------------------------------------------------------
#: The categories the FinalGate insists on. Every one is critical; a missing
#: one becomes Verdict.MISSING and blocks.
FINAL_GATE_CATEGORIES: tuple[str, ...] = (
    "reel.decode",
    "reel.story",
    "reel.video",
    "reel.voice",
    "reel.lipsync",
    "reel.edit",
    "reel.subtitles",
    "reel.audio_mix",
    "reel.cover",
    "reel.perceptual",
)


class FinalGate:
    """Aggregates every category fail-closed. Decoding alone is never enough."""

    name = "reel.final_gate"
    role = "FinalGate"

    def evaluate(self, results: Sequence[GateResult]) -> GateReport:
        return evaluate_gates(results, required_critical=FINAL_GATE_CATEGORIES)

    @staticmethod
    def decode_gate(
        final_path: Optional[str], backends: ReelBackends, thresholds: ReelThresholds
    ) -> GateResult:
        """Necessary, never sufficient: the file must at least decode."""

        if not final_path or not Path(final_path).exists():
            return GateResult(
                name="reel.decode",
                verdict=Verdict.MISSING,
                critical=True,
                reason="no final file exists",
            )
        try:
            info = backends.editor.probe(Path(final_path))
        except BackendUnavailableError as exc:
            return GateResult(
                name="reel.decode",
                verdict=Verdict.NOT_MEASURED,
                critical=True,
                reason=f"cannot decode the final file: {exc}",
            )
        streams = info.get("streams", [])
        has_video = any(s.get("codec_type") == "video" for s in streams)
        has_audio = any(s.get("codec_type") == "audio" for s in streams)
        duration = float(info.get("format", {}).get("duration", 0.0) or 0.0)
        problems = []
        if not has_video:
            problems.append("no video stream")
        if not has_audio:
            problems.append("no audio stream")
        if not (thresholds.min_duration_s <= duration <= thresholds.max_duration_s):
            problems.append(
                f"duration {duration:.1f}s outside "
                f"[{thresholds.min_duration_s}, {thresholds.max_duration_s}]s"
            )
        measurement = Measurement(
            "final_duration_s", duration, Evidence.MEASURED_LOCAL, unit="s", source="ffprobe"
        )
        if problems:
            return GateResult(
                name="reel.decode",
                verdict=Verdict.FAIL,
                critical=True,
                reason="; ".join(problems),
                measurement=measurement,
            )
        return GateResult(
            name="reel.decode",
            verdict=Verdict.PASS,
            critical=True,
            reason=(
                f"decodes: video+audio, {duration:.1f}s "
                "(decode PASS is necessary, not sufficient)"
            ),
            measurement=measurement,
        )
