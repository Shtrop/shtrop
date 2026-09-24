"""Development kit — **NOT PRODUCTION CONTENT**.

These backends exist so the Reel pipeline can be exercised end to end on a
machine that has no GPU, no ComfyUI, no Wan2.2, no XTTS and no Sofia reference
assets. They produce media that is *structurally* real — a genuinely playable
MP4, genuine PCM audio, genuine cues — so that the edit, subtitle, audio-mix,
cover and decode stages are measured on real files instead of being assumed.

What they emphatically do **not** produce is Sofia. Every artifact carries
``NOT_SOFIA`` provenance:

* the voices are synthesised tones, not a Sofia voice clone;
* the footage is procedural, not a Sofia render, and contains no face;
* consequently every identity gate fails or cannot be measured, and a reel
  built from these backends can never reach PASS.

That is the intended behaviour. Use these only for pipeline verification, never
for anything an owner might mistake for publishable content.
"""

from sofia.devkit.backends import (
    NOT_SOFIA,
    DevMusicBed,
    DevTTSBackend,
    DevVideoBackend,
    build_dev_reel_backends,
    build_dev_voice_backends,
)
from sofia.devkit.media import animate_still, music_bed_wav, render_still, speech_like_wav

__all__ = [
    "NOT_SOFIA",
    "DevMusicBed",
    "DevTTSBackend",
    "DevVideoBackend",
    "animate_still",
    "build_dev_reel_backends",
    "build_dev_voice_backends",
    "music_bed_wav",
    "render_still",
    "speech_like_wav",
]
