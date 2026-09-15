"""Backend adapters for the Voice Team.

Three capabilities cannot be faked in software: synthesis (TTS), transcription
(ASR) and speaker identity (embedding + reference voiceprint). Each is a
protocol here with a real adapter for the studio machine and an explicit
unavailable adapter for machines that lack the models.

The unavailable adapters **raise**. They never return a neutral or optimistic
value, because a critic that cannot measure must report ``NOT_MEASURED`` /
``ERROR`` and thereby block — that is the fail-closed rule in practice.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Protocol, Sequence, runtime_checkable

from sofia.core.errors import BackendUnavailableError
from sofia.voice.contracts import Language, VoiceBrief


# --------------------------------------------------------------------------
# Protocols
# --------------------------------------------------------------------------
@runtime_checkable
class TTSBackend(Protocol):
    """Synthesises speech for a :class:`VoiceBrief`."""

    name: str

    def available(self) -> bool: ...

    def synthesize(self, brief: VoiceBrief, out_path: Path) -> Path: ...


@runtime_checkable
class ASRBackend(Protocol):
    """Transcribes audio back to text, for WER and semantic verification."""

    name: str

    def available(self) -> bool: ...

    def transcribe(self, audio_path: Path, language: Language) -> str: ...


@runtime_checkable
class SpeakerEmbeddingBackend(Protocol):
    """Produces a speaker embedding and compares it to Sofia's voiceprint."""

    name: str

    def available(self) -> bool: ...

    def similarity(self, audio_path: Path, reference: "Voiceprint") -> float: ...


@dataclass(frozen=True)
class Voiceprint:
    """A canonical Sofia reference for one language.

    ``reference_clips`` are real recordings/approved clips of Sofia. Without
    them there is no Sofia identity to compare against, and a generic fallback
    voice is explicitly **not** Sofia.
    """

    speaker: str
    language: Language
    reference_clips: tuple[str, ...] = ()
    embedding_path: Optional[str] = None

    @property
    def available(self) -> bool:
        if self.embedding_path and Path(self.embedding_path).exists():
            return True
        return any(Path(c).exists() for c in self.reference_clips)

    @property
    def is_generic_fallback(self) -> bool:
        """True when no Sofia reference exists for this language.

        A generic multilingual TTS voice is not Sofia. The identity critic
        must fail closed in that case rather than accepting a stranger.
        """
        return not self.available


# --------------------------------------------------------------------------
# Unavailable adapters (this container, and any machine without the models)
# --------------------------------------------------------------------------
class UnavailableTTS:
    """A TTS backend that is honest about not existing."""

    def __init__(self, reason: str = "no local TTS backend configured") -> None:
        self.name = "unavailable-tts"
        self.reason = reason

    def available(self) -> bool:
        return False

    def synthesize(self, brief: VoiceBrief, out_path: Path) -> Path:
        raise BackendUnavailableError(
            f"cannot synthesize {brief.language.label} speech: {self.reason}"
        )


class UnavailableASR:
    def __init__(self, reason: str = "no local ASR backend configured") -> None:
        self.name = "unavailable-asr"
        self.reason = reason

    def available(self) -> bool:
        return False

    def transcribe(self, audio_path: Path, language: Language) -> str:
        raise BackendUnavailableError(f"cannot transcribe audio: {self.reason}")


class UnavailableSpeakerEmbedding:
    def __init__(self, reason: str = "no speaker-embedding model configured") -> None:
        self.name = "unavailable-speaker-embedding"
        self.reason = reason

    def available(self) -> bool:
        return False

    def similarity(self, audio_path: Path, reference: Voiceprint) -> float:
        raise BackendUnavailableError(
            f"cannot measure voice identity: {self.reason}"
        )


# --------------------------------------------------------------------------
# Real adapters for the studio machine
# --------------------------------------------------------------------------
class XTTSHttpBackend:
    """Adapter for the studio's local XTTS service.

    The studio runs XTTS locally (see the studio map). This adapter speaks to
    it over HTTP and writes a WAV. It reports ``available() is False`` whenever
    the service cannot be reached, which makes every dependent critic fail
    closed instead of silently degrading to a generic voice.
    """

    def __init__(
        self,
        endpoint: str = "http://127.0.0.1:5681/api/tts",
        *,
        speaker_wavs: Optional[dict[str, Sequence[str]]] = None,
        timeout_s: float = 120.0,
    ) -> None:
        self.name = "xtts-http"
        self.endpoint = endpoint
        self.speaker_wavs = {k: tuple(v) for k, v in (speaker_wavs or {}).items()}
        self.timeout_s = timeout_s

    def available(self) -> bool:
        import urllib.error
        import urllib.request

        try:
            req = urllib.request.Request(self.endpoint, method="HEAD")
            with urllib.request.urlopen(req, timeout=3):  # noqa: S310 - localhost
                return True
        except Exception:  # noqa: BLE001 - unreachable service is simply unavailable
            return False

    def synthesize(self, brief: VoiceBrief, out_path: Path) -> Path:
        import urllib.error
        import urllib.request

        refs = self.speaker_wavs.get(brief.language.value) or self.speaker_wavs.get(
            brief.speaker_profile, ()
        )
        if not refs:
            raise BackendUnavailableError(
                f"no Sofia reference clips registered for {brief.language.label}; "
                "a generic fallback voice is not Sofia"
            )
        payload = json.dumps(
            {
                "text": brief.text,
                "language": brief.language.value,
                "speaker_wav": list(refs),
                "emotion": brief.emotion.value,
                "pace": brief.pace.value,
                "style": brief.style,
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:  # noqa: S310
                data = resp.read()
        except Exception as exc:  # noqa: BLE001
            raise BackendUnavailableError(f"XTTS request failed: {exc}") from exc
        if not data:
            raise BackendUnavailableError("XTTS returned an empty response")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(data)
        return out_path


class WhisperCliBackend:
    """Adapter for a local whisper-family CLI used as the ASR reference."""

    def __init__(self, binary: str = "whisper", model: str = "large-v3") -> None:
        self.name = f"whisper-cli:{model}"
        self.binary = binary
        self.model = model

    def available(self) -> bool:
        return shutil.which(self.binary) is not None

    def transcribe(self, audio_path: Path, language: Language) -> str:
        if not self.available():
            raise BackendUnavailableError(f"{self.binary} is not on PATH")
        out_dir = audio_path.parent / "_asr"
        out_dir.mkdir(parents=True, exist_ok=True)
        cmd = [
            self.binary,
            str(audio_path),
            "--model",
            self.model,
            "--language",
            language.value,
            "--output_format",
            "txt",
            "--output_dir",
            str(out_dir),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if proc.returncode != 0:
            raise BackendUnavailableError(f"ASR failed: {proc.stderr.strip()[:400]}")
        txt = out_dir / (audio_path.stem + ".txt")
        if not txt.exists():
            raise BackendUnavailableError("ASR produced no transcript file")
        return txt.read_text(encoding="utf-8").strip()


@dataclass
class VoiceBackends:
    """The set of backends the Voice Team was given."""

    tts: TTSBackend
    asr: ASRBackend
    speaker: SpeakerEmbeddingBackend
    voiceprints: dict[Language, Voiceprint]

    @classmethod
    def unavailable(cls, reason: str) -> "VoiceBackends":
        """A fully unavailable set — every critical voice gate will block."""
        return cls(
            tts=UnavailableTTS(reason),
            asr=UnavailableASR(reason),
            speaker=UnavailableSpeakerEmbedding(reason),
            voiceprints={
                lang: Voiceprint(speaker="sofia", language=lang)
                for lang in Language
            },
        )

    def voiceprint(self, language: Language) -> Voiceprint:
        return self.voiceprints.get(
            language, Voiceprint(speaker="sofia", language=language)
        )

    def status(self) -> dict:
        return {
            "tts": {"name": self.tts.name, "available": self.tts.available()},
            "asr": {"name": self.asr.name, "available": self.asr.available()},
            "speaker": {
                "name": self.speaker.name,
                "available": self.speaker.available(),
            },
            "voiceprints": {
                lang.label: {
                    "available": self.voiceprint(lang).available,
                    "generic_fallback": self.voiceprint(lang).is_generic_fallback,
                }
                for lang in Language
            },
        }


def detect_backends(config_path: Optional[str | Path] = None) -> VoiceBackends:
    """Wire real backends if this machine has them; otherwise fail closed.

    On the studio machine (XTTS + whisper + Sofia reference clips present) this
    returns live adapters. On any machine without them it returns adapters that
    raise, so no clip can ever be marked PASS on a box that cannot measure it.
    """

    cfg: dict = {}
    if config_path and Path(config_path).exists():
        cfg = json.loads(Path(config_path).read_text(encoding="utf-8"))

    tts: TTSBackend = XTTSHttpBackend(
        endpoint=cfg.get("tts_endpoint", "http://127.0.0.1:5681/api/tts"),
        speaker_wavs=cfg.get("speaker_wavs", {}),
    )
    if not tts.available():
        tts = UnavailableTTS("XTTS service is not reachable on this machine")

    asr: ASRBackend = WhisperCliBackend(
        binary=cfg.get("asr_binary", "whisper"), model=cfg.get("asr_model", "large-v3")
    )
    if not asr.available():
        asr = UnavailableASR("no whisper-family ASR binary on PATH")

    speaker: SpeakerEmbeddingBackend = UnavailableSpeakerEmbedding(
        "speaker-embedding model not configured; identity cannot be measured"
    )

    voiceprints: dict[Language, Voiceprint] = {}
    for lang in Language:
        clips = tuple(cfg.get("reference_clips", {}).get(lang.value, ()))
        voiceprints[lang] = Voiceprint(
            speaker="sofia",
            language=lang,
            reference_clips=clips,
            embedding_path=cfg.get("embeddings", {}).get(lang.value),
        )
    return VoiceBackends(tts=tts, asr=asr, speaker=speaker, voiceprints=voiceprints)
