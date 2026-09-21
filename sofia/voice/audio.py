"""Dependency-free WAV analysis.

Everything here is a genuine local measurement on real PCM samples
(:class:`~sofia.core.verdict.Evidence.MEASURED_LOCAL`) using only the standard
library, so prosody and loudness QA work on any machine — including one with no
GPU and no torch.

What is *not* here, deliberately: speaker identity. Voice identity requires a
speaker-embedding model and a Sofia reference voiceprint. There is no honest
stdlib proxy for it, so :mod:`sofia.voice.backends` declares it as a backend
protocol and the critic reports ``NOT_MEASURED`` (which is fail-closed) when no
backend is wired.
"""

from __future__ import annotations

import math
import struct
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from sofia.core.artifacts import validate_wav


#: Amplitude at or above which a sample counts as clipped.
CLIP_THRESHOLD = 0.998


@dataclass(frozen=True)
class AudioStats:
    """Objective measurements taken from decoded PCM."""

    path: str
    duration_s: float
    sample_rate: int
    channels: int
    peak: float
    rms: float
    true_peak_dbfs: float
    rms_dbfs: float
    clipped_samples: int
    clipping_ratio: float
    silence_ratio: float
    pause_count: int
    longest_pause_s: float
    speech_segments: int
    speech_rate_sps: float
    dynamic_range_db: float
    dc_offset: float

    @property
    def clipping(self) -> bool:
        return self.clipping_ratio > 0.0005

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


def read_wav_mono(path: str | Path) -> tuple[list[float], int]:
    """Decode a PCM WAV into normalised mono floats in [-1, 1]."""

    with wave.open(str(path), "rb") as wf:
        channels = wf.getnchannels()
        width = wf.getsampwidth()
        rate = wf.getframerate()
        frames = wf.readframes(wf.getnframes())

    if width == 1:
        # 8-bit PCM is unsigned.
        samples = [(b - 128) / 128.0 for b in frames]
    elif width == 2:
        count = len(frames) // 2
        samples = [v / 32768.0 for v in struct.unpack(f"<{count}h", frames[: count * 2])]
    elif width == 4:
        count = len(frames) // 4
        samples = [v / 2147483648.0 for v in struct.unpack(f"<{count}i", frames[: count * 4])]
    else:
        raise ValueError(f"unsupported sample width: {width} bytes")

    if channels > 1:
        mono = [
            sum(samples[i : i + channels]) / channels
            for i in range(0, len(samples) - channels + 1, channels)
        ]
    else:
        mono = samples
    return mono, rate


def analyse_wav(path: str | Path, *, silence_db: float = -45.0) -> AudioStats:
    """Measure loudness, clipping and pause structure of a WAV file."""

    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"audio artifact does not exist: {p}")
    if p.stat().st_size == 0:
        raise ValueError(f"audio artifact is empty: {p}")
    # A WAV cut short mid-write still declares its original length in the
    # header, so decoding it silently yields a shorter clip. Refuse it here so
    # every critic sees the problem, not just a resumed run.
    validate_wav(p)

    samples, rate = read_wav_mono(p)
    if not samples:
        raise ValueError(f"audio artifact decodes to zero samples: {p}")

    with wave.open(str(p), "rb") as wf:
        channels = wf.getnchannels()

    n = len(samples)
    duration = n / float(rate)
    peak = max(abs(s) for s in samples)
    mean = sum(samples) / n
    rms = math.sqrt(sum(s * s for s in samples) / n)
    # 16-bit full scale quantises to 32767/32768 = 0.99997, and a sample written
    # at "1.0" can land a quantisation step below, so the threshold sits just
    # under full scale (-0.017 dBFS) rather than exactly at it.
    clipped = sum(1 for s in samples if abs(s) >= CLIP_THRESHOLD)

    # Frame-wise energy at 20 ms for pause / speech-rate structure.
    frame = max(1, int(rate * 0.02))
    energies: list[float] = []
    for i in range(0, n - frame + 1, frame):
        window = samples[i : i + frame]
        energies.append(math.sqrt(sum(s * s for s in window) / frame))
    if not energies:
        energies = [rms]

    threshold = _dbfs_to_linear(silence_db)
    voiced = [e > threshold for e in energies]
    silence_ratio = 1.0 - (sum(voiced) / len(voiced))

    pause_count, longest_pause, speech_segments = _segment(voiced, frame / rate)
    peaks = _count_energy_peaks(energies)
    speech_time = max(1e-6, duration * (1.0 - silence_ratio))
    speech_rate = peaks / speech_time

    loud_frames = sorted((e for e in energies if e > threshold), reverse=True)
    if loud_frames:
        top = loud_frames[: max(1, len(loud_frames) // 10)]
        bottom = loud_frames[-max(1, len(loud_frames) // 10) :]
        dyn = _linear_to_dbfs(sum(top) / len(top)) - _linear_to_dbfs(
            sum(bottom) / len(bottom)
        )
    else:
        dyn = 0.0

    return AudioStats(
        path=str(p),
        duration_s=duration,
        sample_rate=rate,
        channels=channels,
        peak=peak,
        rms=rms,
        true_peak_dbfs=_linear_to_dbfs(peak),
        rms_dbfs=_linear_to_dbfs(rms),
        clipped_samples=clipped,
        clipping_ratio=clipped / n,
        silence_ratio=silence_ratio,
        pause_count=pause_count,
        longest_pause_s=longest_pause,
        speech_segments=speech_segments,
        speech_rate_sps=speech_rate,
        dynamic_range_db=dyn,
        dc_offset=mean,
    )


def write_wav(
    path: str | Path,
    samples: Sequence[float],
    rate: int = 22050,
) -> Path:
    """Write normalised float samples as 16-bit mono PCM."""

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    data = b"".join(
        struct.pack("<h", max(-32768, min(32767, int(s * 32767)))) for s in samples
    )
    with wave.open(str(p), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(data)
    return p


# ---- internals -----------------------------------------------------------
def _dbfs_to_linear(db: float) -> float:
    return 10.0 ** (db / 20.0)


def _linear_to_dbfs(value: float) -> float:
    if value <= 1e-9:
        return -120.0
    return 20.0 * math.log10(value)


def _segment(voiced: Sequence[bool], frame_s: float) -> tuple[int, float, int]:
    """Count internal pauses, the longest pause, and speech segments."""

    pauses = 0
    longest = 0.0
    segments = 0
    run = 0
    prev = None
    # Ignore leading/trailing silence when counting pauses.
    first = next((i for i, v in enumerate(voiced) if v), None)
    last = next((i for i in range(len(voiced) - 1, -1, -1) if voiced[i]), None)
    if first is None or last is None:
        return 0, len(voiced) * frame_s, 0
    for v in voiced[first : last + 1]:
        if prev is None or v != prev:
            if prev is False and run > 0:
                pauses += 1
                longest = max(longest, run * frame_s)
            if prev is True:
                segments += 1
            run = 0
        run += 1
        prev = v
    if prev is True:
        segments += 1
    elif prev is False and run > 0:
        pauses += 1
        longest = max(longest, run * frame_s)
    return pauses, longest, segments


def _count_energy_peaks(energies: Sequence[float]) -> int:
    """Approximate syllable nuclei as local energy maxima above the mean."""

    if len(energies) < 3:
        return 0
    mean = sum(energies) / len(energies)
    peaks = 0
    for i in range(1, len(energies) - 1):
        if (
            energies[i] > mean
            and energies[i] >= energies[i - 1]
            and energies[i] > energies[i + 1]
        ):
            peaks += 1
    return peaks
