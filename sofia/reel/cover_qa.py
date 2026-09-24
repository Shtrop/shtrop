"""Cover QA.

A cover is measured in two halves, and the split matters:

* **Composition** — exposure, contrast, sharpness, crop and how busy the band
  under the hook text is. All of this comes from the decoded image with the
  standard library, so it is measured on any machine.
* **Identity and brand** — is Sofia's face there, is it *her*, does it look like
  her channel. None of that has an honest stdlib proxy; it needs a face model
  and a brand reference, and without them it stays ``NOT_MEASURED``.

Reporting only the second half, as this module's predecessor did, meant a cover
that was black, blown out or horizontal sailed through as "not measured"
instead of being called what it was.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Optional

from sofia.reel.frames import FrameStats, analyse_frame


@dataclass(frozen=True)
class CoverThresholds:
    """Floors for the composition half of the cover gate."""

    min_brightness: float = 0.08
    max_brightness: float = 0.88
    min_contrast: float = 0.07
    min_sharpness: float = 0.010
    max_blown_ratio: float = 0.30
    max_dark_ratio: float = 0.80
    min_aspect_ratio: float = 1.5
    #: Above this, the band under the hook text is too busy for text to read.
    max_text_band_edges: float = 0.28
    #: The band where a cover's hook text sits, as fractions of height.
    text_band: tuple[float, float] = (0.60, 0.82)


@dataclass
class CoverIssues:
    composition: list[str] = field(default_factory=list)
    not_measured: list[str] = field(default_factory=list)
    measurements: dict[str, float] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.composition and not self.not_measured

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "composition": list(self.composition),
            "not_measured": list(self.not_measured),
            "measurements": dict(self.measurements),
        }


#: Metrics that need a face model or a brand reference. No stdlib proxy exists,
#: so their absence is NOT_MEASURED rather than a guess.
MODEL_DEPENDENT: tuple[str, ...] = (
    "face_present",
    "face_identity",
    "brand_consistency",
)

#: Floors for the model-dependent half, applied when a backend supplies them.
MODEL_FLOORS: Mapping[str, float] = {
    "face_present": 0.5,
    "face_identity": 0.70,
    "brand_consistency": 0.70,
}


def analyse_cover(
    cover_ppm: Optional[str],
    supplied: Mapping[str, Optional[float]],
    *,
    thresholds: Optional[CoverThresholds] = None,
) -> CoverIssues:
    """Measure the cover's composition and fold in any supplied model metrics."""

    t = thresholds or CoverThresholds()
    issues = CoverIssues()

    stats: Optional[FrameStats] = None
    if cover_ppm and Path(cover_ppm).exists():
        try:
            stats = analyse_frame(cover_ppm)
        except (ValueError, OSError) as exc:
            issues.not_measured.append(f"cover could not be decoded: {exc}")
    else:
        issues.not_measured.append(
            "no decodable cover image; composition cannot be measured"
        )

    if stats is not None:
        _check_composition(stats, cover_ppm, t, issues)

    for key in MODEL_DEPENDENT:
        value = supplied.get(key)
        if value is None:
            issues.not_measured.append(
                f"{key} needs a face/brand model and was not measured"
            )
            continue
        issues.measurements[key] = float(value)
        floor = MODEL_FLOORS[key]
        if float(value) < floor:
            issues.composition.append(f"{key}={float(value):.2f} below {floor:.2f}")

    return issues


def _check_composition(
    stats: FrameStats, path: Optional[str], t: CoverThresholds, issues: CoverIssues
) -> None:
    issues.measurements.update(
        {
            "brightness": round(stats.brightness, 4),
            "contrast": round(stats.contrast, 4),
            "sharpness": round(stats.sharpness, 5),
            "edge_density": round(stats.edge_density, 4),
            "blown_ratio": round(stats.blown_ratio, 4),
            "dark_ratio": round(stats.dark_ratio, 4),
        }
    )

    if stats.is_black_frame or stats.brightness < t.min_brightness:
        issues.composition.append(
            f"cover is essentially black (brightness {stats.brightness:.3f})"
        )
    elif stats.brightness > t.max_brightness:
        issues.composition.append(
            f"cover is washed out (brightness {stats.brightness:.3f})"
        )
    if stats.contrast < t.min_contrast:
        issues.composition.append(f"cover is flat (contrast {stats.contrast:.3f})")
    if stats.sharpness < t.min_sharpness:
        issues.composition.append(f"cover is soft (sharpness {stats.sharpness:.4f})")
    if stats.blown_ratio > t.max_blown_ratio:
        issues.composition.append(f"{stats.blown_ratio:.0%} of the cover is blown out")
    if stats.dark_ratio > t.max_dark_ratio:
        issues.composition.append(f"{stats.dark_ratio:.0%} of the cover is crushed")

    if stats.width:
        aspect = stats.height / stats.width
        issues.measurements["aspect_ratio"] = round(aspect, 3)
        if aspect < t.min_aspect_ratio:
            issues.composition.append(
                f"cover is {stats.width}x{stats.height} (aspect {aspect:.2f}); "
                "a reel cover must be vertical"
            )

    # Whether the band under the hook text is calm enough for text to read.
    if path:
        try:
            band = analyse_frame(path, region=t.text_band)
        except (ValueError, OSError):
            return
        issues.measurements["text_band_edges"] = round(band.edge_density, 4)
        issues.measurements["text_band_contrast"] = round(band.contrast, 4)
        if band.edge_density > t.max_text_band_edges:
            issues.composition.append(
                f"the band under the hook text is busy (edge density "
                f"{band.edge_density:.3f} > {t.max_text_band_edges}); text will not read"
            )
