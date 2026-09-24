"""Voice/music timeline assembly and ducking.

The voice track is laid out on the Reel's timeline from the individual verified
clips, and the music bed is ducked under it. Ducking is then *verified* by
measuring the *delivered* mix (see :func:`measure_ducking`) rather than assumed
from the filter graph or inferred from the stems.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

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


@dataclass(frozen=True)
class Ducking:
    """How far the voice sits over the bed, in the file that will play."""

    headroom_db: float
    loudest_gap_at_s: float
    speech_windows: int
    gap_windows: int

    def to_dict(self) -> dict:
        return {
            "headroom_db": round(self.headroom_db, 2),
            "loudest_gap_at_s": round(self.loudest_gap_at_s, 2),
            "speech_windows": self.speech_windows,
            "gap_windows": self.gap_windows,
        }


#: With no bed audible in any gap the ratio goes to infinity, and "60 dB clear"
#: already means nothing is fighting the voice.
MAX_HEADROOM_DB = 60.0


def measure_ducking(
    voice_path: str | Path,
    mix_path: str | Path,
    *,
    window_s: float = 0.25,
    silence_db: float = -45.0,
    speech_floor_db: float = 20.0,
) -> Optional[Ducking]:
    """Measure voice-over-bed separation in the delivered mix.

    Comparing the voice and music *stems* says what the mix was asked to be and
    stays true whether or not the ducking step ran, so it cannot verify
    anything. This reads the delivered file instead, and needs no source
    separation to do it: the voice track says *when* someone is speaking, and
    the mix is read in those windows and in the gaps between them. A gap holds
    the bed and nothing else, so

        median speech level  /  loudest gap level

    is how far the voice sits above the bed that a listener hears. The loudest
    gap is used rather than the average so a single moment where the bed swells
    is what the gate sees.

    The voice stem is used only for timing, which survives encoding — unlike
    the samples themselves. (Cancelling the voice out of the mix by least
    squares was tried first and does not survive a real ffmpeg chain: on a
    measured devkit mix the residual came out three times larger than the music
    stem could account for, so it could not tell a loud bed from a mix it had
    failed to decompose.)

    Returns ``None`` when the mix cannot be judged this way — different sample
    rates, almost no speech, or no gap in which the bed is audible on its own.
    The caller reports that as NOT_MEASURED.
    """

    voice, v_rate = read_wav_mono(voice_path)
    mix, m_rate = read_wav_mono(mix_path)
    if not voice or not mix or v_rate != m_rate:
        return None
    n = min(len(voice), len(mix))
    frame = max(1, int(window_s * v_rate))
    if n < frame * 4:
        return None

    def rms(signal: Sequence[float], start: int) -> float:
        return math.sqrt(
            sum(s * s for s in signal[start : start + frame]) / frame
        )

    floor = 10.0 ** (silence_db / 20.0)
    starts = range(0, n - frame + 1, frame)
    voice_levels = {start: rms(voice, start) for start in starts}
    active = sorted(v for v in voice_levels.values() if v > floor)
    if not active:
        return None
    # "Speaking" means within `speech_floor_db` of this voice's own speech
    # level, not merely above an absolute floor: the decay tail of a word is
    # above the floor, and a bed that is louder than a dying syllable is not a
    # defect.
    reference = active[len(active) // 2] * 10.0 ** (-speech_floor_db / 20.0)

    speech: list[float] = []
    gaps: list[tuple[float, float]] = []
    for start, level in voice_levels.items():
        if level > reference:
            speech.append(rms(mix, start))
        elif level <= floor:
            gaps.append((rms(mix, start), start / v_rate))
    if len(speech) < 3 or not gaps:
        return None

    loudest_gap, at = max(gaps)
    speech.sort()
    median_speech = speech[len(speech) // 2]
    headroom = (
        MAX_HEADROOM_DB
        if loudest_gap <= 1e-9
        else min(MAX_HEADROOM_DB, 20.0 * math.log10(median_speech / loudest_gap))
    )
    return Ducking(headroom, at, len(speech), len(gaps))
