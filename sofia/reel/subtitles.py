"""Subtitle building and verification.

Subtitles must match the *actual speech*, be readable at reel pace, break on
sense boundaries, and stay inside the platform safe zones. All of that is
verifiable from the cue list and the voice timings, so it is measured here for
real rather than assumed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional, Sequence

from sofia.core.durable import atomic_write_text
from sofia.voice.contracts import Language
from sofia.voice.text import normalize

#: Readability limits for vertical short-form video.
MAX_CHARS_PER_LINE = 26
MAX_LINES_PER_CUE = 2
MAX_CHARS_PER_SECOND = 20.0
MIN_CUE_S = 0.6
MAX_CUE_S = 5.0
MIN_GAP_S = 0.04

#: Fractions of frame height that must stay clear of burned-in text.
SAFE_TOP = 0.14
SAFE_BOTTOM = 0.20


@dataclass
class Cue:
    index: int
    start_s: float
    end_s: float
    lines: list[str]

    @property
    def duration_s(self) -> float:
        return self.end_s - self.start_s

    @property
    def text(self) -> str:
        return " ".join(self.lines)

    @property
    def chars_per_second(self) -> float:
        return len(self.text) / self.duration_s if self.duration_s > 0 else float("inf")

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "start_s": round(self.start_s, 3),
            "end_s": round(self.end_s, 3),
            "lines": list(self.lines),
            "cps": round(self.chars_per_second, 2),
        }


def wrap_line(text: str, max_chars: int = MAX_CHARS_PER_LINE) -> list[str]:
    """Break on word boundaries, preferring a balanced two-line cue."""

    words = text.split()
    if not words:
        return [""]
    if len(text) <= max_chars:
        return [text]
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= max_chars or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def build_cues(
    segments: Sequence[tuple[str, float, float]],
    *,
    max_chars: int = MAX_CHARS_PER_LINE,
) -> list[Cue]:
    """Turn ``(text, start_s, end_s)`` speech segments into readable cues.

    A segment too long to read at reel pace is split into several cues, with
    time shared proportionally to character count so the text stays on the
    speech.
    """

    cues: list[Cue] = []
    idx = 1
    for text, start, end in segments:
        text = " ".join(text.split())
        if not text:
            continue
        duration = max(end - start, MIN_CUE_S)
        lines = wrap_line(text, max_chars)
        chunks: list[list[str]] = [
            lines[i : i + MAX_LINES_PER_CUE]
            for i in range(0, len(lines), MAX_LINES_PER_CUE)
        ]
        total_chars = sum(len(" ".join(c)) for c in chunks) or 1
        cursor = start
        for chunk in chunks:
            share = len(" ".join(chunk)) / total_chars
            length = max(MIN_CUE_S, min(MAX_CUE_S, duration * share))
            cue_end = min(end, cursor + length) if len(chunks) > 1 else end
            if cue_end - cursor < MIN_CUE_S:
                cue_end = cursor + MIN_CUE_S
            cues.append(Cue(idx, round(cursor, 3), round(cue_end, 3), chunk))
            idx += 1
            cursor = cue_end + MIN_GAP_S
    return cues


def to_srt(cues: Sequence[Cue]) -> str:
    out: list[str] = []
    for cue in cues:
        out.append(str(cue.index))
        out.append(f"{_ts(cue.start_s)} --> {_ts(cue.end_s)}")
        out.extend(cue.lines)
        out.append("")
    return "\n".join(out)


def write_srt(cues: Sequence[Cue], path: str | Path) -> Path:
    return atomic_write_text(path, to_srt(cues))


def parse_srt(path: str | Path) -> list[Cue]:
    raw = Path(path).read_text(encoding="utf-8")
    cues: list[Cue] = []
    for block in re.split(r"\n\s*\n", raw.strip()):
        lines = [ln for ln in block.splitlines() if ln.strip()]
        if len(lines) < 2:
            continue
        m = re.match(
            r"(\d\d):(\d\d):(\d\d),(\d\d\d)\s*-->\s*(\d\d):(\d\d):(\d\d),(\d\d\d)",
            lines[1],
        )
        if not m:
            continue
        g = [int(x) for x in m.groups()]
        start = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000.0
        end = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000.0
        cues.append(Cue(int(lines[0]), start, end, lines[2:]))
    return cues


def _ts(seconds: float) -> str:
    seconds = max(0.0, seconds)
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    if ms == 1000:
        ms, s = 0, s + 1
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


@dataclass
class SubtitleIssues:
    """Everything wrong with a cue list, by category."""

    text_mismatch: list[str] = field(default_factory=list)
    timing: list[str] = field(default_factory=list)
    readability: list[str] = field(default_factory=list)
    line_breaks: list[str] = field(default_factory=list)
    safe_zone: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(
            (
                self.text_mismatch,
                self.timing,
                self.readability,
                self.line_breaks,
                self.safe_zone,
            )
        )

    def all_issues(self) -> list[str]:
        return (
            self.text_mismatch
            + self.timing
            + self.readability
            + self.line_breaks
            + self.safe_zone
        )

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "text_mismatch": list(self.text_mismatch),
            "timing": list(self.timing),
            "readability": list(self.readability),
            "line_breaks": list(self.line_breaks),
            "safe_zone": list(self.safe_zone),
        }


def verify_cues(
    cues: Sequence[Cue],
    *,
    spoken_text: str,
    language: Language,
    video_duration_s: Optional[float] = None,
    text_top: float = 0.0,
    text_bottom: float = 1.0,
) -> SubtitleIssues:
    """Check cues against the real speech, the clock and the safe zones.

    ``spoken_text`` should be what was *actually said* (ideally the ASR
    transcript of the final mix), not the script — subtitles must match speech.
    """

    issues = SubtitleIssues()
    if not cues:
        issues.text_mismatch.append("no subtitle cues at all")
        return issues

    # --- text correctness against the real speech -------------------------
    cue_words = normalize(" ".join(c.text for c in cues), language).split()
    spoken_words = normalize(spoken_text, language).split()
    missing = [w for w in spoken_words if w not in set(cue_words)]
    invented = [w for w in cue_words if w not in set(spoken_words)]
    if missing:
        issues.text_mismatch.append(
            f"{len(missing)} spoken word(s) missing from subtitles: {missing[:6]}"
        )
    if invented:
        issues.text_mismatch.append(
            f"{len(invented)} subtitle word(s) never spoken: {invented[:6]}"
        )

    # --- timing -----------------------------------------------------------
    previous_end = -1.0
    for cue in cues:
        if cue.duration_s < MIN_CUE_S:
            issues.timing.append(
                f"cue {cue.index} lasts {cue.duration_s:.2f}s (< {MIN_CUE_S}s)"
            )
        if cue.duration_s > MAX_CUE_S:
            issues.timing.append(
                f"cue {cue.index} lasts {cue.duration_s:.2f}s (> {MAX_CUE_S}s)"
            )
        if cue.start_s < previous_end - 1e-6:
            issues.timing.append(f"cue {cue.index} overlaps the previous cue")
        if video_duration_s is not None and cue.end_s > video_duration_s + 0.05:
            issues.timing.append(
                f"cue {cue.index} ends at {cue.end_s:.2f}s, past the {video_duration_s:.2f}s video"
            )
        previous_end = cue.end_s

    # --- readability and line breaks --------------------------------------
    for cue in cues:
        if cue.chars_per_second > MAX_CHARS_PER_SECOND:
            issues.readability.append(
                f"cue {cue.index} runs at {cue.chars_per_second:.1f} chars/s "
                f"(> {MAX_CHARS_PER_SECOND})"
            )
        if len(cue.lines) > MAX_LINES_PER_CUE:
            issues.line_breaks.append(
                f"cue {cue.index} has {len(cue.lines)} lines (> {MAX_LINES_PER_CUE})"
            )
        for line in cue.lines:
            if len(line) > MAX_CHARS_PER_LINE:
                issues.line_breaks.append(
                    f"cue {cue.index} line is {len(line)} chars (> {MAX_CHARS_PER_LINE})"
                )
            if line.endswith((" -", " —")) or re.search(r"\b[а-яa-zії]-$", line):
                issues.line_breaks.append(
                    f"cue {cue.index} breaks mid-word or on a dangling hyphen"
                )

    # --- safe zones -------------------------------------------------------
    if text_top < SAFE_TOP:
        issues.safe_zone.append(
            f"subtitles start at {text_top:.2f} of frame height, inside the top "
            f"{SAFE_TOP:.0%} UI zone"
        )
    if text_bottom > 1.0 - SAFE_BOTTOM:
        issues.safe_zone.append(
            f"subtitles reach {text_bottom:.2f} of frame height, inside the bottom "
            f"{SAFE_BOTTOM:.0%} UI zone"
        )
    return issues


# --------------------------------------------------------------------------
# ASS output
#
# Burning an .srt makes the renderer invent a script resolution (commonly
# 384x288), so the font size and margins written here would be scaled by an
# arbitrary factor and land outside the safe zone. Emitting ASS with an
# explicit PlayResX/PlayResY ties what is burned in to what was verified.
# --------------------------------------------------------------------------
ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sofia,{font},{size},&H00FFFFFF,&H00FFFFFF,&H90000000,&H60000000,-1,0,0,0,100,100,0,0,1,{outline},1,2,{margin_l},{margin_r},{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def to_ass(
    cues: Sequence[Cue],
    *,
    width: int,
    height: int,
    safe_bottom: float = SAFE_BOTTOM,
    font: str = "DejaVu Sans",
    font_size: Optional[int] = None,
    side_margin_frac: float = 0.09,
) -> str:
    """Render cues as ASS, positioned above the bottom safe zone."""

    # ``safe_bottom`` is where the text's lower edge should sit, as a fraction
    # of frame height; ASS MarginV is measured up from the bottom edge.
    margin_v = max(16, int(round(height * (1.0 - safe_bottom))))
    size = font_size or max(16, int(round(height * 0.038)))
    side = max(16, int(round(width * side_margin_frac)))
    out = [
        ASS_HEADER.format(
            width=width,
            height=height,
            font=font,
            size=size,
            outline=max(1, round(size * 0.07)),
            margin_l=side,
            margin_r=side,
            margin_v=margin_v,
        )
    ]
    for cue in cues:
        text = r"\N".join(cue.lines)
        out.append(
            f"Dialogue: 0,{_ass_ts(cue.start_s)},{_ass_ts(cue.end_s)},Sofia,,0,0,0,,{text}"
        )
    return "\n".join(out) + "\n"


def write_ass(
    cues: Sequence[Cue],
    path: str | Path,
    *,
    width: int,
    height: int,
    safe_bottom: float = SAFE_BOTTOM,
    font_size: Optional[int] = None,
) -> Path:
    # Written atomically: a half-written .ass is not an error to libass, it
    # silently renders fewer cues, and on resume it would be reused as if it
    # were complete.
    return atomic_write_text(
        path,
        to_ass(
            cues,
            width=width,
            height=height,
            safe_bottom=safe_bottom,
            font_size=font_size,
        ),
    )


def _ass_ts(seconds: float) -> str:
    seconds = max(0.0, seconds)
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    cs = int(round((seconds - int(seconds)) * 100))
    if cs == 100:
        cs, s = 0, s + 1
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


def estimate_text_extent(
    cues: Sequence[Cue], *, height: int, safe_bottom: float, font_size: Optional[int] = None
) -> tuple[float, float]:
    """Where the burned-in text will actually sit, as fractions of frame height.

    Returned as ``(top, bottom)`` so the subtitle critic checks the real
    placement rather than a declared intention.
    """

    size = font_size or max(16, int(round(height * 0.038)))
    line_height = size * 1.25
    max_lines = max((len(c.lines) for c in cues), default=1)
    bottom_px = height * safe_bottom
    bottom = min(1.0, bottom_px / height)
    top = max(0.0, (bottom_px - max_lines * line_height) / height)
    return top, bottom
