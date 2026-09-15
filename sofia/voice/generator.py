"""VoiceGenerator — the only role that calls a TTS backend."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from sofia.core.errors import BackendUnavailableError
from sofia.voice.backends import VoiceBackends
from sofia.voice.contracts import VoiceArtifact, VoiceBrief


@dataclass
class VoiceGenerator:
    """Synthesises a brief into an audio artifact.

    It never invents a fallback voice: if the configured Sofia backend cannot
    run, the error propagates so the critics block. Substituting a generic
    voice here is exactly the failure mode the Voice Team exists to prevent.
    """

    backends: VoiceBackends
    workdir: Path
    name: str = "sofia.voice.generator"
    role: str = "VoiceGenerator"

    def generate(
        self,
        brief: VoiceBrief,
        *,
        clip_id: str,
        attempt: int = 1,
        reuse: bool = True,
    ) -> VoiceArtifact:
        out = (
            Path(self.workdir)
            / "voice"
            / brief.language.value
            / f"{clip_id}.take{attempt}.wav"
        )
        started = time.monotonic()
        # Resume: an existing take is reused rather than re-synthesised, but it
        # is still put through every critic — reuse skips generation, never
        # verification.
        reused = reuse and out.exists() and out.stat().st_size > 0
        if not reused:
            self.backends.tts.synthesize(brief, out)
        elapsed = time.monotonic() - started
        if not out.exists() or out.stat().st_size == 0:
            raise BackendUnavailableError(
                f"TTS backend {self.backends.tts.name!r} reported success but wrote "
                f"no usable audio to {out}"
            )
        return VoiceArtifact(
            brief=brief,
            audio_path=str(out),
            backend=self.backends.tts.name,
            generation_s=elapsed,
            attempts=attempt,
            meta={"clip_id": clip_id, "reused": reused},
        )
