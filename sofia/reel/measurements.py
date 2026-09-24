"""What a video or lip-sync backend must hand back for a gate to run.

Every per-shot number the critics read comes from ``Shot.measurements``, and
nothing in this package writes them: they are supplied by the backend that did
the work, because the identity model, the artifact detector and the A/V sync
analyser live on the studio machine. A gate whose numbers never arrive reports
``NOT_MEASURED`` and blocks, which is correct — but an integrator wiring a real
generator then has no way to know *which* names were expected, and would see a
permanently blocked pipeline with nothing to fix.

So the contract lives here, in one place: the critics read these names, the
Champion/Challenger trial holds every arm to them, ``preflight.py`` prints them
and the exported registry carries them.
"""

from __future__ import annotations

from typing import Mapping

#: Per-shot measurements the video gate requires, with what each one means.
VIDEO_MEASUREMENTS: Mapping[str, str] = {
    "identity": (
        "similarity of the rendered face to the Sofia reference, 0-1. Required "
        "on face-critical and talking shots; B-roll and detail shots are not "
        "asked for it, which is what keeps GPU cost and the identity-failure "
        "surface down."
    ),
    "face_drift": (
        "how far identity moves across the shot, 0-1. A shot that starts as "
        "Sofia and ends as someone else passes a mean-identity check."
    ),
    "sharpness": "focus/detail of the rendered frames, 0-1.",
    "ai_artifact_score": (
        "how much the shot reads as generated, 0-1, lower is better: warped "
        "hands, melted edges, impossible motion."
    ),
}

#: Per-shot measurements the lip-sync gate requires. The Champion/Challenger
#: trial is held to exactly this list, so a challenger cannot win on the mouth
#: while nobody looked at its A/V sync.
LIPSYNC_MEASUREMENTS: Mapping[str, str] = {
    "phoneme_accuracy": "how well mouth shapes match the spoken phonemes, 0-1.",
    "mouth_quality": "mouth interior and lip rendering, 0-1.",
    "jaw_quality": "jaw motion plausibility, 0-1.",
    "teeth_quality": "teeth rendering, 0-1 — a classic lip-sync tell.",
    "eye_quality": "eye life; dead eyes read as fake however good the mouth is.",
    "identity": "face identity in the synced result, 0-1.",
    "face_drift": "identity movement across the synced shot, 0-1.",
    "av_offset_ms": (
        "audio/video offset in milliseconds, lower is better. Perfect mouth "
        "shapes at the wrong time are still bad lip-sync."
    ),
}

#: Metrics where a lower number is the better one.
LOWER_IS_BETTER: frozenset[str] = frozenset(
    {"face_drift", "ai_artifact_score", "av_offset_ms"}
)


def contract() -> dict:
    """The whole contract, for preflight output and the exported registry."""

    return {
        "video": dict(VIDEO_MEASUREMENTS),
        "lipsync": dict(LIPSYNC_MEASUREMENTS),
        "lower_is_better": sorted(LOWER_IS_BETTER),
        "note": (
            "Attach these to Shot.measurements as sofia.core.verdict.Measurement "
            "values. A missing one is NOT_MEASURED and blocks the gate; it is "
            "never treated as a pass."
        ),
    }
