"""Procedural media generation using only the standard library plus ffmpeg.

Stills are written as binary PPM (which ffmpeg reads natively), animated with a
slow Ken Burns move, and paired with synthesised audio. Nothing here depicts a
person; see the package docstring.
"""

from __future__ import annotations

import math
import random
import subprocess
from pathlib import Path
from typing import Optional, Sequence

from sofia.voice.audio import write_wav

#: Sofia's signature palette, used so the dev footage at least reads as the
#: right brand family: cappuccino warmth and emerald.
CAPPUCCINO = (198, 162, 124)
ESPRESSO = (58, 41, 32)
EMERALD = (26, 122, 94)
CREAM = (238, 226, 210)


def render_still(
    out_path: str | Path,
    *,
    width: int = 540,
    height: int = 960,
    motif: str = "gradient",
    accent: Sequence[int] = EMERALD,
    base: Sequence[int] = ESPRESSO,
    highlight: Sequence[int] = CAPPUCCINO,
    seed: int = 0,
) -> Path:
    """Write a vertical still as binary PPM."""

    rng = random.Random(seed)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    cx, cy = width * 0.5, height * 0.38
    radius = min(width, height) * 0.45
    pixels = bytearray(width * height * 3)

    for y in range(height):
        v = y / (height - 1)
        for x in range(width):
            u = x / (width - 1)
            if motif == "gradient":
                t = v
            elif motif == "radial":
                d = math.hypot(x - cx, y - cy) / radius
                t = min(1.0, d)
            elif motif == "diagonal":
                t = min(1.0, max(0.0, (u + v) * 0.5))
            elif motif == "bars":
                t = 0.25 + 0.5 * (math.sin(v * math.pi * 6.0) * 0.5 + 0.5)
            else:
                t = v

            r = int(base[0] + (highlight[0] - base[0]) * (1.0 - t))
            g = int(base[1] + (highlight[1] - base[1]) * (1.0 - t))
            b = int(base[2] + (highlight[2] - base[2]) * (1.0 - t))

            # Accent band, placed outside the subtitle safe zone.
            if motif != "bars" and 0.18 < v < 0.30:
                k = 1.0 - abs(v - 0.24) / 0.06
                r = int(r + (accent[0] - r) * 0.55 * k)
                g = int(g + (accent[1] - g) * 0.55 * k)
                b = int(b + (accent[2] - b) * 0.55 * k)

            # Soft grain so the encoder has real detail to work with.
            n = rng.randint(-6, 6)
            idx = (y * width + x) * 3
            pixels[idx] = _clamp(r + n)
            pixels[idx + 1] = _clamp(g + n)
            pixels[idx + 2] = _clamp(b + n)

    with open(out, "wb") as fh:
        fh.write(f"P6\n{width} {height}\n255\n".encode("ascii"))
        fh.write(bytes(pixels))
    return out


def _clamp(value: int) -> int:
    return 0 if value < 0 else (255 if value > 255 else value)


def animate_still(
    still: str | Path,
    out_path: str | Path,
    *,
    duration_s: float,
    ffmpeg: str,
    fps: int = 24,
    width: int = 540,
    height: int = 960,
    zoom_to: float = 1.08,
    audio: Optional[str | Path] = None,
) -> Path:
    """Turn a still into a real, moving MP4 with a slow push-in."""

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    frames = max(2, int(round(duration_s * fps)))
    zoom_expr = f"1+({zoom_to - 1.0})*on/{frames}"
    vf = (
        f"zoompan=z='{zoom_expr}':d={frames}:x='iw/2-(iw/zoom/2)':"
        f"y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps},"
        f"format=yuv420p"
    )
    cmd = [ffmpeg, "-y", "-loop", "1", "-i", str(still)]
    if audio:
        cmd += ["-i", str(audio)]
    else:
        # Silent track, declared as an input before any output options.
        cmd += [
            "-f", "lavfi",
            "-i", "anullsrc=channel_layout=mono:sample_rate=48000",
        ]
    cmd += [
        "-vf", vf,
        "-t", f"{duration_s:.3f}",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-r", str(fps),
        "-c:a", "aac",
        "-b:a", "160k" if audio else "96k",
        "-shortest",
    ]
    cmd.append(str(out))
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    if proc.returncode != 0 or not out.exists():
        raise RuntimeError(f"animation failed: {proc.stderr.strip()[-600:]}")
    return out


def speech_like_wav(
    text: str,
    out_path: str | Path,
    *,
    duration_s: float,
    rate: int = 22050,
    seed: int = 0,
    base_f0: float = 185.0,
    target_rms_dbfs: float = -18.0,
) -> Path:
    """Synthesise speech-shaped audio: syllable envelope + formant-ish spectrum.

    This is **not** a voice clone and not intelligible speech. It exists so the
    prosody, loudness and mix analysers measure real PCM.
    """

    rng = random.Random(seed)
    syllables = max(2, _estimate_syllables(text))
    n = int(duration_s * rate)
    samples = [0.0] * n

    # Lay out syllable nuclei with small natural jitter, and put real pauses at
    # punctuation so the pause analyser has something true to find.
    boundaries = _syllable_slots(text, syllables, duration_s, rng)
    f0 = base_f0
    for start, end, stressed in boundaries:
        centre = (start + end) / 2.0
        f0 = base_f0 * (1.0 + rng.uniform(-0.06, 0.06)) * (1.12 if stressed else 1.0)
        for i in range(int(start * rate), min(n, int(end * rate))):
            t = i / rate
            # Raised-cosine syllable envelope.
            span = max(1e-3, (end - start) / 2.0)
            env = max(0.0, math.cos(math.pi * (t - centre) / (2 * span)))
            env = env * env * (1.0 if stressed else 0.78)
            value = (
                0.55 * math.sin(2 * math.pi * f0 * t)
                + 0.28 * math.sin(2 * math.pi * f0 * 2 * t + 0.4)
                + 0.14 * math.sin(2 * math.pi * f0 * 3 * t + 1.1)
                + 0.08 * math.sin(2 * math.pi * 720 * t)
                + 0.05 * rng.uniform(-1.0, 1.0)
            )
            samples[i] += env * value

    _normalise_rms(samples, target_rms_dbfs)
    return write_wav(out_path, samples, rate)


def music_bed_wav(
    out_path: str | Path,
    *,
    duration_s: float,
    rate: int = 22050,
    target_rms_dbfs: float = -30.0,
    bpm: float = 96.0,
) -> Path:
    """A soft pad with a pulse, quiet enough to sit under a voice."""

    n = int(duration_s * rate)
    samples = [0.0] * n
    chord = (146.83, 174.61, 220.0, 293.66)  # D3 F3 A3 D4 — warm minor pad
    beat = 60.0 / bpm
    for i in range(n):
        t = i / rate
        value = sum(math.sin(2 * math.pi * f * t) for f in chord) / len(chord)
        # Gentle tremolo plus a soft pulse on the beat.
        trem = 0.85 + 0.15 * math.sin(2 * math.pi * 0.25 * t)
        phase = (t % beat) / beat
        pulse = 1.0 + 0.25 * math.exp(-12.0 * phase)
        fade = min(1.0, t / 1.2, max(0.0, (duration_s - t) / 1.5))
        samples[i] = value * trem * pulse * fade
    _normalise_rms(samples, target_rms_dbfs)
    return write_wav(out_path, samples, rate)


def _normalise_rms(samples: list[float], target_dbfs: float) -> None:
    n = len(samples)
    if not n:
        return
    rms = math.sqrt(sum(s * s for s in samples) / n)
    if rms <= 1e-9:
        return
    target = 10.0 ** (target_dbfs / 20.0)
    gain = target / rms
    peak = max(abs(s) for s in samples) * gain
    if peak > 0.95:
        gain *= 0.95 / peak
    for i in range(n):
        samples[i] *= gain


_VOWELS = set("аеёиоуыэюяіїєaeiouy")


def _estimate_syllables(text: str) -> int:
    return sum(1 for ch in text.lower() if ch in _VOWELS)


def _syllable_slots(
    text: str, syllables: int, duration_s: float, rng: random.Random
) -> list[tuple[float, float, bool]]:
    """Distribute syllables over the clip, leaving gaps at punctuation."""

    pause_after = [i for i, ch in enumerate(text) if ch in ",.!?—:;"]
    pause_budget = min(0.30 * duration_s, 0.22 * max(1, len(pause_after)))
    speech_time = max(0.2, duration_s - pause_budget)
    slot = speech_time / syllables
    slots: list[tuple[float, float, bool]] = []
    cursor = 0.02
    for i in range(syllables):
        length = slot * rng.uniform(0.85, 1.15)
        stressed = i % 3 == 0
        slots.append((cursor, min(duration_s, cursor + length), stressed))
        cursor += length
        # Insert a pause roughly where punctuation falls in the text.
        if pause_after and i and i % max(1, syllables // (len(pause_after) + 1)) == 0:
            cursor += min(0.28, pause_budget / max(1, len(pause_after)))
        if cursor >= duration_s:
            break
    return slots
