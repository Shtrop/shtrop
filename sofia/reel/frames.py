"""Frame measurement using only the standard library.

A frame decoded to binary PPM is just RGB bytes, so brightness, contrast,
sharpness, colourfulness and edge density are all computable without numpy or
PIL. That matters because it turns "strong first frame" from an assertion into
a measurement that runs on any machine.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FrameStats:
    """Objective measurements of a single frame."""

    path: str
    width: int
    height: int
    brightness: float       # mean luma, 0..1
    contrast: float         # luma standard deviation, 0..1
    sharpness: float        # mean gradient magnitude, 0..1
    colourfulness: float    # mean chroma spread, 0..1
    edge_density: float     # fraction of pixels on a strong edge
    dark_ratio: float       # fraction below 8% luma
    blown_ratio: float      # fraction above 97% luma

    @property
    def is_black_frame(self) -> bool:
        """A frame nobody would stop scrolling for."""
        return self.brightness < 0.04 or self.dark_ratio > 0.97

    @property
    def is_flat(self) -> bool:
        """Almost no tonal variation — a hold frame, a fade, or a blank."""
        return self.contrast < 0.05

    def to_dict(self) -> dict:
        return dict(self.__dict__)


def read_ppm(path: str | Path) -> tuple[bytearray, int, int]:
    """Read a binary PPM (P6) into raw RGB bytes."""

    data = Path(path).read_bytes()
    if not data.startswith(b"P6"):
        raise ValueError(f"not a binary PPM: {path}")

    # Header fields are whitespace-separated and may be split by comments.
    fields: list[int] = []
    i = 2
    while len(fields) < 3:
        while i < len(data) and data[i : i + 1].isspace():
            i += 1
        if data[i : i + 1] == b"#":
            while i < len(data) and data[i : i + 1] != b"\n":
                i += 1
            continue
        start = i
        while i < len(data) and not data[i : i + 1].isspace():
            i += 1
        fields.append(int(data[start:i]))
    i += 1  # single whitespace byte after maxval

    width, height, maxval = fields
    if maxval != 255:
        raise ValueError(f"unsupported PPM maxval {maxval}")
    expected = width * height * 3
    pixels = bytearray(data[i : i + expected])
    if len(pixels) < expected:
        raise ValueError(f"truncated PPM: {len(pixels)} of {expected} bytes")
    return pixels, width, height


def analyse_frame(
    path: str | Path,
    *,
    step: int = 2,
    region: tuple[float, float] | None = None,
) -> FrameStats:
    """Measure a frame, or a horizontal band of one.

    ``step`` subsamples the grid; at 2 this reads a quarter of the pixels,
    which is plenty for frame-level statistics and keeps a 1080x1920 frame
    well under a second in pure Python.

    ``region`` is ``(top, bottom)`` as fractions of height. Measuring just the
    band where text will sit answers a question the whole-frame numbers cannot:
    whether *that part* of the image is busy enough to swallow the text.
    """

    pixels, width, height = read_ppm(path)

    y_start, y_end = 0, height
    if region is not None:
        top, bottom = region
        y_start = max(0, min(height - 1, int(round(top * height))))
        y_end = max(y_start + 1, min(height, int(round(bottom * height))))

    luma: list[float] = []
    chroma: list[float] = []
    dark = blown = 0
    rows = range(y_start, y_end, step)
    cols = range(0, width, step)

    for y in rows:
        base = y * width * 3
        for x in cols:
            i = base + x * 3
            r, g, b = pixels[i] / 255.0, pixels[i + 1] / 255.0, pixels[i + 2] / 255.0
            # Rec. 601 luma, which is what perceptual brightness tracks.
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            luma.append(lum)
            chroma.append(max(r, g, b) - min(r, g, b))
            if lum < 0.08:
                dark += 1
            elif lum > 0.97:
                blown += 1

    n = len(luma) or 1
    mean = sum(luma) / n
    variance = sum((v - mean) ** 2 for v in luma) / n
    contrast = math.sqrt(variance)

    # Gradient magnitude on the subsampled grid.
    cols_n = len(cols)
    rows_n = len(rows)
    gradients: list[float] = []
    strong = 0
    for ry in range(rows_n - 1):
        row = ry * cols_n
        for rx in range(cols_n - 1):
            here = luma[row + rx]
            dx = abs(luma[row + rx + 1] - here)
            dy = abs(luma[row + cols_n + rx] - here)
            g = math.hypot(dx, dy)
            gradients.append(g)
            if g > 0.08:
                strong += 1

    sharpness = sum(gradients) / len(gradients) if gradients else 0.0
    edge_density = strong / len(gradients) if gradients else 0.0

    return FrameStats(
        path=str(path),
        width=width,
        height=height,
        brightness=mean,
        contrast=contrast,
        sharpness=sharpness,
        colourfulness=sum(chroma) / n,
        edge_density=edge_density,
        dark_ratio=dark / n,
        blown_ratio=blown / n,
    )
