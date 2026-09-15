"""Editing QA.

The brief asks the EditorAgent for a strong first frame, a fast hook, no dead
time, sensible pacing, beat sync, ducking, safe zones, subtitles, transitions
and a cover. Ducking, safe zones, subtitles and the cover have their own
critics. This module covers the rest, and it measures them rather than assuming
them:

* **first frame** — decoded and analysed, so a black or flat opener is caught;
* **dead time** — the longest silence in the actual mix;
* **pacing** — shot-length distribution and cut rate from the real shot list;
* **aspect** — the delivered frame must be vertical;
* **beat sync** — cut points against the music grid.

Beat sync is reported but does not fail the gate: landing cuts on the beat is a
craft signal, not a correctness property, and a reel with deliberate off-beat
cuts is not broken. Everything else here is a hard failure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Sequence

from sofia.core.errors import BackendUnavailableError
from sofia.reel.contracts import Shot
from sofia.reel.frames import FrameStats, analyse_frame
from sofia.voice.audio import analyse_wav


@dataclass(frozen=True)
class EditThresholds:
    """Floors for the editing gate."""

    max_hook_s: float = 3.0
    min_shots: int = 3
    max_shots: int = 8
    #: A reel that rests on one shot for this fraction of its runtime drags.
    max_single_shot_fraction: float = 0.40
    min_cuts_per_10s: float = 1.2
    max_cuts_per_10s: float = 6.0
    #: Silence longer than this inside the programme is dead air.
    max_dead_air_s: float = 0.9
    #: A first frame must clear these or it is not worth stopping for.
    min_first_frame_contrast: float = 0.06
    min_first_frame_sharpness: float = 0.010
    #: Vertical delivery: height/width must be at least this.
    min_aspect_ratio: float = 1.5
    #: Cuts within this of a beat count as on-beat.
    beat_tolerance_s: float = 0.12


@dataclass
class EditIssues:
    """What is wrong with the edit, by category."""

    first_frame: list[str] = field(default_factory=list)
    pacing: list[str] = field(default_factory=list)
    dead_time: list[str] = field(default_factory=list)
    framing: list[str] = field(default_factory=list)
    not_measured: list[str] = field(default_factory=list)
    #: Craft signals that are reported but never fail the gate.
    advisory: list[str] = field(default_factory=list)
    measurements: dict[str, float] = field(default_factory=dict)

    @property
    def blocking(self) -> list[str]:
        return self.first_frame + self.pacing + self.dead_time + self.framing

    @property
    def ok(self) -> bool:
        return not self.blocking and not self.not_measured

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "first_frame": list(self.first_frame),
            "pacing": list(self.pacing),
            "dead_time": list(self.dead_time),
            "framing": list(self.framing),
            "not_measured": list(self.not_measured),
            "advisory": list(self.advisory),
            "measurements": dict(self.measurements),
        }


def beat_grid(bpm: float, duration_s: float) -> list[float]:
    """Beat times for a constant-tempo bed."""
    if bpm <= 0:
        return []
    interval = 60.0 / bpm
    times: list[float] = []
    t = 0.0
    while t <= duration_s:
        times.append(round(t, 4))
        t += interval
    return times


def cut_points(shots: Sequence[Shot]) -> list[float]:
    """Times where one shot becomes the next."""
    cuts: list[float] = []
    cursor = 0.0
    for shot in shots[:-1]:
        cursor += shot.duration_s
        cuts.append(round(cursor, 4))
    return cuts


def check_pacing(shots: Sequence[Shot], t: EditThresholds, issues: EditIssues) -> None:
    """Shot count, hook speed and cut rhythm, from the real shot list."""

    if not shots:
        issues.pacing.append("edit has no shots")
        return

    total = sum(s.duration_s for s in shots)
    issues.measurements["runtime_s"] = round(total, 2)
    issues.measurements["shots"] = len(shots)

    if len(shots) < t.min_shots:
        issues.pacing.append(
            f"{len(shots)} shot(s); a reel needs at least {t.min_shots} meaningful shots"
        )
    elif len(shots) > t.max_shots:
        issues.pacing.append(
            f"{len(shots)} shots is busier than {t.max_shots}; the story will not land"
        )

    hook = shots[0].duration_s
    issues.measurements["hook_s"] = round(hook, 2)
    if hook > t.max_hook_s:
        issues.pacing.append(
            f"opening shot runs {hook:.1f}s before the first cut; the hook must land "
            f"within {t.max_hook_s:.0f}s"
        )

    if total > 0:
        longest = max(shots, key=lambda s: s.duration_s)
        fraction = longest.duration_s / total
        issues.measurements["longest_shot_fraction"] = round(fraction, 3)
        if fraction > t.max_single_shot_fraction:
            issues.pacing.append(
                f"shot {longest.index} holds {fraction:.0%} of the runtime; the edit "
                "drags on one image"
            )

        rate = (len(shots) - 1) / (total / 10.0)
        issues.measurements["cuts_per_10s"] = round(rate, 2)
        if rate < t.min_cuts_per_10s:
            issues.pacing.append(f"only {rate:.1f} cuts per 10s; the edit is static")
        elif rate > t.max_cuts_per_10s:
            issues.pacing.append(f"{rate:.1f} cuts per 10s; the edit is frantic")


def check_dead_time(mix_path: Optional[str], t: EditThresholds, issues: EditIssues) -> None:
    """Dead air measured in the delivered mix, not assumed from the plan."""

    if not mix_path or not Path(mix_path).exists():
        issues.not_measured.append(
            "no analysable mix; dead time cannot be measured from the delivered audio"
        )
        return
    try:
        stats = analyse_wav(mix_path)
    except Exception as exc:  # noqa: BLE001 - unreadable audio blocks
        issues.not_measured.append(f"mix could not be analysed: {exc}")
        return

    issues.measurements["longest_silence_s"] = round(stats.longest_pause_s, 3)
    issues.measurements["silence_ratio"] = round(stats.silence_ratio, 3)
    if stats.longest_pause_s > t.max_dead_air_s:
        issues.dead_time.append(
            f"{stats.longest_pause_s:.2f}s of dead air in the mix "
            f"(limit {t.max_dead_air_s:.1f}s)"
        )


def check_first_frame(
    final_path: Optional[str],
    editor,
    workdir: Path,
    t: EditThresholds,
    issues: EditIssues,
) -> Optional[FrameStats]:
    """The opening frame decides whether anyone sees the rest."""

    if not final_path or not Path(final_path).exists():
        issues.not_measured.append("no final file; the first frame cannot be inspected")
        return None
    out = Path(workdir) / "qa" / "first_frame.ppm"
    try:
        editor.extract_frame(Path(final_path), 0.0, out)
        stats = analyse_frame(out)
    except (BackendUnavailableError, ValueError, OSError) as exc:
        issues.not_measured.append(f"first frame could not be decoded: {exc}")
        return None

    issues.measurements["first_frame_brightness"] = round(stats.brightness, 4)
    issues.measurements["first_frame_contrast"] = round(stats.contrast, 4)
    issues.measurements["first_frame_sharpness"] = round(stats.sharpness, 5)
    issues.measurements["first_frame_edges"] = round(stats.edge_density, 4)

    if stats.is_black_frame:
        issues.first_frame.append(
            f"the reel opens on a black frame (brightness {stats.brightness:.3f})"
        )
    elif stats.is_flat or stats.contrast < t.min_first_frame_contrast:
        issues.first_frame.append(
            f"the opening frame is flat (contrast {stats.contrast:.3f} < "
            f"{t.min_first_frame_contrast})"
        )
    if stats.sharpness < t.min_first_frame_sharpness:
        issues.first_frame.append(
            f"the opening frame is soft (sharpness {stats.sharpness:.4f} < "
            f"{t.min_first_frame_sharpness})"
        )
    if stats.blown_ratio > 0.35:
        issues.first_frame.append(
            f"{stats.blown_ratio:.0%} of the opening frame is blown out"
        )

    # Vertical delivery.
    if stats.width:
        aspect = stats.height / stats.width
        issues.measurements["aspect_ratio"] = round(aspect, 3)
        if aspect < t.min_aspect_ratio:
            issues.framing.append(
                f"delivered at {stats.width}x{stats.height} (aspect {aspect:.2f}); "
                "a reel must be vertical"
            )
    return stats


def check_beat_sync(
    shots: Sequence[Shot],
    bpm: Optional[float],
    t: EditThresholds,
    issues: EditIssues,
) -> None:
    """How many cuts land on the music grid. Reported, never fatal."""

    cuts = cut_points(shots)
    if not cuts:
        return
    if not bpm:
        issues.advisory.append(
            "music tempo unknown, so beat sync was not evaluated"
        )
        return
    total = sum(s.duration_s for s in shots)
    grid = beat_grid(bpm, total)
    if not grid:
        return
    on_beat = sum(
        1 for c in cuts if min(abs(c - b) for b in grid) <= t.beat_tolerance_s
    )
    ratio = on_beat / len(cuts)
    issues.measurements["cuts_on_beat"] = round(ratio, 3)
    if ratio < 0.5:
        issues.advisory.append(
            f"{on_beat}/{len(cuts)} cuts land on the beat at {bpm:.0f} BPM; "
            "tightening them would help the rhythm"
        )


def analyse_edit(
    *,
    final_path: Optional[str],
    shots: Sequence[Shot],
    mix_path: Optional[str],
    editor,
    workdir: Path,
    music_bpm: Optional[float] = None,
    thresholds: Optional[EditThresholds] = None,
) -> EditIssues:
    """Run every editing check and return what it found."""

    t = thresholds or EditThresholds()
    issues = EditIssues()
    check_pacing(shots, t, issues)
    check_first_frame(final_path, editor, workdir, t, issues)
    check_dead_time(mix_path, t, issues)
    check_beat_sync(shots, music_bpm, t, issues)
    return issues
