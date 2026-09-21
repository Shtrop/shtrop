"""Artifact integrity.

A file existing is not a PASS — and a file existing is not even a *finished
render*. On a host that can lose power mid-write, a partially written artifact
is left behind: it exists, it is not empty, and resume would happily reuse it.

That is not hypothetical. A truncated MP4 does not decode at all (`moov atom
not found`), and a truncated WAV is worse: the RIFF header still declares the
original length, so a naive decode silently returns a shorter clip with no
error whatsoever.

Everything here answers one question: is this file *complete*, not merely
present.
"""

from __future__ import annotations

import wave
from pathlib import Path
from typing import Callable, Optional

from sofia.core.errors import SofiaError


class ArtifactInvalid(SofiaError):
    """An artifact exists but is incomplete or undecodable."""


def validate_wav(path: str | Path) -> None:
    """Raise unless the WAV's data chunk holds every frame its header claims.

    ``wave`` trusts the header, so a file cut short mid-write decodes without
    complaint and simply returns fewer frames. Comparing the declared frame
    count against the bytes actually present is what catches it.
    """

    p = Path(path)
    if not p.exists():
        raise ArtifactInvalid(f"audio artifact does not exist: {p}")
    if p.stat().st_size == 0:
        raise ArtifactInvalid(f"audio artifact is empty: {p}")
    try:
        with wave.open(str(p), "rb") as wf:
            declared = wf.getnframes()
            frame_size = wf.getnchannels() * wf.getsampwidth()
            available = len(wf.readframes(declared))
    except wave.Error as exc:
        raise ArtifactInvalid(f"audio artifact is not a readable WAV: {exc}") from exc

    if frame_size <= 0:
        raise ArtifactInvalid(f"audio artifact declares a zero frame size: {p}")
    expected = declared * frame_size
    if available < expected:
        missing = (expected - available) / float(expected)
        raise ArtifactInvalid(
            f"audio artifact is truncated: {available} of {expected} bytes "
            f"({missing:.1%} missing) — written by an interrupted run"
        )


def validate_ppm(path: str | Path) -> None:
    """Raise unless the PPM holds a full frame of pixels."""

    from sofia.reel.frames import read_ppm

    p = Path(path)
    if not p.exists() or p.stat().st_size == 0:
        raise ArtifactInvalid(f"image artifact is missing or empty: {p}")
    try:
        read_ppm(p)
    except (ValueError, OSError) as exc:
        raise ArtifactInvalid(f"image artifact is not a complete PPM: {exc}") from exc


def validate_video(path: str | Path, probe: Optional[Callable[[Path], dict]]) -> None:
    """Raise unless the video decodes and carries a real duration.

    ``probe`` is the editor backend's probe. Without one the file cannot be
    verified, and an unverifiable artifact is treated as unusable rather than
    as good — the whole point is not to reuse something that may be half
    written.
    """

    p = Path(path)
    if not p.exists():
        raise ArtifactInvalid(f"video artifact does not exist: {p}")
    if p.stat().st_size == 0:
        raise ArtifactInvalid(f"video artifact is empty: {p}")
    if probe is None:
        raise ArtifactInvalid(
            f"no probe available to verify {p}; refusing to assume it is complete"
        )
    try:
        info = probe(p)
    except Exception as exc:  # noqa: BLE001 - any probe failure means unusable
        raise ArtifactInvalid(f"video artifact does not decode: {exc}") from exc

    duration = float(info.get("format", {}).get("duration", 0.0) or 0.0)
    if duration <= 0.0:
        raise ArtifactInvalid(f"video artifact decodes to zero duration: {p}")
    if not any(s.get("codec_type") == "video" for s in info.get("streams", [])):
        raise ArtifactInvalid(f"video artifact has no video stream: {p}")


def is_usable(
    path: Optional[str | Path],
    *,
    kind: str,
    probe: Optional[Callable[[Path], dict]] = None,
) -> bool:
    """Whether a previously produced artifact can be reused as finished work.

    Returns False for anything missing, empty, truncated or undecodable, so a
    resumed run re-does that piece instead of building on a fragment.
    """

    if not path:
        return False
    try:
        if kind == "wav":
            validate_wav(path)
        elif kind == "ppm":
            validate_ppm(path)
        elif kind == "video":
            validate_video(path, probe)
        else:
            raise ArtifactInvalid(f"unknown artifact kind: {kind!r}")
    except ArtifactInvalid:
        return False
    return True
