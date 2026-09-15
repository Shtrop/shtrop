"""Dev backends. See the package docstring: these never produce Sofia.

Every artifact they emit is tagged ``NOT_SOFIA``. Because no Sofia voiceprint or
face reference exists for them, the identity critics fail or cannot measure, so
a reel assembled from these backends can never reach PASS. That is the point:
the pipeline is exercised for real while the gates stay honest.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from sofia.core.errors import BackendUnavailableError
from sofia.devkit.media import animate_still, music_bed_wav, render_still, speech_like_wav
from sofia.reel.backends import (
    FfmpegEditor,
    ReelBackends,
    UnavailableLipSync,
    UnavailableVideo,
)
from sofia.reel.contracts import Shot, ShotType
from sofia.reel.shots import GeneratorProfile
from sofia.voice.backends import (
    UnavailableASR,
    UnavailableSpeakerEmbedding,
    VoiceBackends,
    Voiceprint,
)
from sofia.voice.contracts import Language, VoiceBrief

#: Provenance stamped on every dev artifact.
NOT_SOFIA = "NOT_SOFIA:devkit-procedural"

#: Visual motif per shot type, so the dev reel at least has visual variety.
_MOTIF = {
    ShotType.FACE_CRITICAL: "radial",
    ShotType.TALKING: "radial",
    ShotType.PAYOFF: "radial",
    ShotType.MEDIUM: "gradient",
    ShotType.B_ROLL: "diagonal",
    ShotType.DETAIL: "bars",
    ShotType.TRANSITION: "gradient",
}


@dataclass
class DevVideoBackend:
    """Renders a real, moving MP4 per shot — abstract, with no face in it."""

    ffmpeg: str
    workdir: Path
    width: int = 540
    height: int = 960
    name: str = "devkit-procedural-video"
    #: This renderer runs on CPU, so it never queues behind a production render.
    requires_gpu: bool = False

    def available(self) -> bool:
        return bool(self.ffmpeg)

    def render(self, shot: Shot, profile: GeneratorProfile, out_path: Path) -> Path:
        if not self.available():
            raise BackendUnavailableError("no ffmpeg for the dev video backend")
        stills = Path(self.workdir) / "stills"
        still = render_still(
            stills / f"{out_path.stem}.ppm",
            width=self.width,
            height=self.height,
            motif=_MOTIF.get(shot.shot_type, "gradient"),
            seed=shot.index * 17 + 3,
        )
        try:
            animate_still(
                still,
                out_path,
                duration_s=shot.duration_s,
                ffmpeg=self.ffmpeg,
                width=self.width,
                height=self.height,
                zoom_to=1.10 if shot.shot_type.needs_face else 1.05,
            )
        except RuntimeError as exc:
            raise BackendUnavailableError(
                f"dev render failed for shot {shot.index}: {exc}"
            ) from exc
        # Provenance is recorded on the shot itself, so downstream QA and the
        # final report can see this was never a Sofia render.
        shot.source_ref = shot.source_ref or NOT_SOFIA
        return out_path


@dataclass
class DevTTSBackend:
    """Synthesises speech-shaped audio. Not a voice clone, and not Sofia."""

    name: str = "devkit-speech-like-tts"
    seed: int = 11

    def available(self) -> bool:
        return True

    def synthesize(self, brief: VoiceBrief, out_path: Path) -> Path:
        duration = brief.target_duration_s or 2.5
        return speech_like_wav(
            brief.text,
            out_path,
            duration_s=duration,
            seed=self.seed + len(brief.text),
            base_f0=195.0 if brief.language is Language.EN else 185.0,
        )


@dataclass
class DevMusicBed:
    """Generates a quiet pad to sit under the voice."""

    name: str = "devkit-music-bed"
    #: Constant tempo of the generated bed, so cuts can be checked against it.
    bpm: float = 96.0

    def generate(self, out_path: Path, duration_s: float) -> Path:
        return music_bed_wav(out_path, duration_s=duration_s, bpm=self.bpm)


def build_dev_voice_backends() -> VoiceBackends:
    """Dev TTS with **no** ASR, **no** speaker model and **no** voiceprints.

    The missing verifiers are deliberate: pronunciation, semantic and identity
    therefore report NOT_MEASURED / FAIL, which is the truthful answer on a
    machine that cannot measure them.
    """

    return VoiceBackends(
        tts=DevTTSBackend(),
        asr=UnavailableASR("devkit has no ASR; pronunciation cannot be verified"),
        speaker=UnavailableSpeakerEmbedding(
            "devkit has no speaker-embedding model; identity cannot be verified"
        ),
        voiceprints={
            lang: Voiceprint(speaker="sofia", language=lang) for lang in Language
        },
    )


def build_dev_reel_backends(ffmpeg: str, workdir: Path) -> ReelBackends:
    """Dev video + real ffmpeg editor, and **no** lip-sync backend."""

    return ReelBackends(
        video=DevVideoBackend(ffmpeg=ffmpeg, workdir=Path(workdir)),
        lipsync=UnavailableLipSync(
            "devkit has no lip-sync model; talking shots cannot be synced or verified"
        ),
        editor=FfmpegEditor(binary=ffmpeg, probe_binary="ffprobe"),
    )
