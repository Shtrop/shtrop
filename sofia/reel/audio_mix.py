"""Voice/music timeline assembly and ducking.

The voice track is laid out on the Reel's timeline from the individual verified
clips, and the music bed is ducked under it. Ducking is then *verified* by
measuring the stems (see :class:`~sofia.reel.critics.AudioMixCritic`) rather
than assumed from the filter graph.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Sequence

from sofia.voice.audio import read_wav_mono, write_wav


def build_voice_track(
    clips: Sequence[tuple[str, float]],
    out_path: str | Path,
    *,
    total_s: float,
    rate: int = 22050,
) -> Path:
    """Place ``(path, start_s)`` voice clips onto one timeline."""

    n = max(1, int(total_s * rate))
    track = [0.0] * n
    for path, start_s in clips:
        samples, clip_rate = read_wav_mono(path)
        if clip_rate != rate:
            samples = resample(samples, clip_rate, rate)
        offset = int(start_s * rate)
        for i, value in enumerate(samples):
            j = offset + i
            if 0 <= j < n:
                track[j] += value
    peak = max((abs(s) for s in track), default=0.0)
    if peak > 0.99:
        scale = 0.99 / peak
        track = [s * scale for s in track]
    return write_wav(out_path, track, rate)


def resample(samples: Sequence[float], src: int, dst: int) -> list[float]:
    """Linear resample. Adequate for layout; the encoder does the real work."""

    if src == dst:
        return list(samples)
    ratio = dst / src
    out_len = int(len(samples) * ratio)
    out: list[float] = []
    last = len(samples) - 1
    for i in range(out_len):
        pos = i / ratio
        lo = int(pos)
        hi = min(lo + 1, last)
        frac = pos - lo
        out.append(samples[lo] * (1 - frac) + samples[hi] * frac)
    return out


def duck_offline(
    voice_path: str | Path,
    music_path: str | Path,
    out_path: str | Path,
    *,
    target_headroom_db: float = 12.0,
    attack_s: float = 0.08,
    release_s: float = 0.35,
    rate: int = 22050,
) -> Path:
    """Mix voice over music with envelope-following ducking, stdlib only.

    Used when no encoder-side sidechain is available. The music is attenuated
    wherever the voice is present so the voice keeps ``target_headroom_db`` of
    separation.
    """

    voice, v_rate = read_wav_mono(voice_path)
    music, m_rate = read_wav_mono(music_path)
    if v_rate != rate:
        voice = resample(voice, v_rate, rate)
    if m_rate != rate:
        music = resample(music, m_rate, rate)

    n = max(len(voice), len(music))
    voice += [0.0] * (n - len(voice))
    music += [0.0] * (n - len(music))

    # Envelope of the voice, smoothed with separate attack and release.
    attack = math.exp(-1.0 / max(1.0, attack_s * rate))
    release = math.exp(-1.0 / max(1.0, release_s * rate))
    env = 0.0
    duck_floor = 10.0 ** (-target_headroom_db / 20.0)
    out = [0.0] * n
    for i in range(n):
        level = abs(voice[i])
        coeff = attack if level > env else release
        env = coeff * env + (1.0 - coeff) * level
        # Full music when silent, attenuated to the floor when the voice is up.
        gain = 1.0 - (1.0 - duck_floor) * min(1.0, env / 0.12)
        out[i] = voice[i] + music[i] * gain

    peak = max((abs(s) for s in out), default=0.0)
    if peak > 0.95:
        scale = 0.95 / peak
        out = [s * scale for s in out]
    return write_wav(out_path, out, rate)
