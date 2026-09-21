"""The owner-facing 0-10 scorecard, and the world-class claim.

Two different questions get two different answers here, and conflating them is
how a pipeline starts calling its own output world-class:

``PASS``
    Every hard gate held, so the Reel may go to owner review. That is a
    statement about defects — nothing was found wrong.

``world class``
    A much stronger claim, and the brief's rule for it is explicit: every
    critical category scores at least 8/10. Two of those categories — how
    strong the hook is and how well the Reel retains an audience — have no
    local instrument at all. They are audience outcomes, readable only from
    published analytics, and publishing is on HOLD. So the claim is reported as
    NOT_MEASURED rather than assumed, however clean the gates are.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional

from sofia.core.verdict import Verdict

#: Categories derived from the FinalGate: each maps onto gates that ran locally.
LOCAL_CATEGORIES: dict[str, tuple[str, ...]] = {
    "STORY": ("reel.story",),
    "IDENTITY": ("reel.video",),
    "VOICE": ("reel.voice",),
    "LIPSYNC": ("reel.lipsync",),
    "EDITING": ("reel.edit", "reel.subtitles", "reel.audio_mix"),
    "COVER": ("reel.cover",),
    "REALISM": ("reel.perceptual",),
}

#: Categories the brief also asks for that nothing here can measure. They are
#: listed rather than dropped: a scorecard that quietly omits the two hardest
#: numbers reads as if everything was covered.
AUDIENCE_CATEGORIES: dict[str, str] = {
    "HOOK": (
        "hook strength is an audience outcome (how many keep watching past the "
        "first seconds); the gates can check that a hook exists and is in the "
        "opening shot, not that it works"
    ),
    "RETENTION": (
        "retention is measurable only from platform analytics on a published "
        "Reel, and publishing is on HOLD"
    ),
}

#: Passing every hard gate in a category earns this and no more: the gates
#: detect defects, they do not grade craft.
GATE_PASS_SCORE = 8.0
#: A category with a blocking finding. It already fails the gate; the number
#: exists so the scorecard is not silent about it.
GATE_FAIL_SCORE = 4.0


def score_categories(report: Any) -> dict[str, Optional[float]]:
    """Honest scorecard: a category that could not be measured scores ``None``.

    It is never rendered as 0 and never as a passing number.
    """

    scores: dict[str, Optional[float]] = {}
    for label, gates in LOCAL_CATEGORIES.items():
        found = [report.by_name(g) for g in gates]
        found = [f for f in found if f is not None]
        if not found or any(
            f.verdict in (Verdict.NOT_MEASURED, Verdict.MISSING, Verdict.ERROR)
            for f in found
        ):
            scores[label] = None
        elif all(f.verdict is Verdict.PASS for f in found):
            scores[label] = GATE_PASS_SCORE
        else:
            scores[label] = GATE_FAIL_SCORE

    for label in AUDIENCE_CATEGORIES:
        scores[label] = None

    measured = [scores[label] for label in LOCAL_CATEGORIES]
    scores["OVERALL"] = (
        round(sum(v for v in measured if v is not None) / len(measured), 1)
        if all(v is not None for v in measured)
        else None
    )
    return scores


def world_class(
    scores: Mapping[str, Optional[float]], thresholds: Any
) -> dict[str, Any]:
    """Whether this Reel may be called world-class, fail-closed.

    ``PASS`` requires every category — audience ones included — to be measured
    and at or above its floor. Anything unmeasured is ``NOT_MEASURED``: not a
    verdict of poor quality, and not permission to claim the opposite.
    """

    floors = {label: float(thresholds.min_category_score) for label in LOCAL_CATEGORIES}
    floors.update({label: float(thresholds.min_category_score) for label in AUDIENCE_CATEGORIES})
    floors["HOOK"] = float(thresholds.min_hook_score)

    below = [
        f"{label}={scores[label]:.1f} (floor {floors[label]:.1f})"
        for label in floors
        if scores.get(label) is not None and float(scores[label]) < floors[label]
    ]
    unmeasured = [label for label in floors if scores.get(label) is None]

    if below:
        verdict = Verdict.FAIL
        reason = "below the floor: " + ", ".join(sorted(below))
    elif unmeasured:
        verdict = Verdict.NOT_MEASURED
        reason = (
            "cannot be claimed: "
            + ", ".join(f"{label} is not measured" for label in sorted(unmeasured))
        )
    else:
        verdict = Verdict.PASS
        reason = (
            f"every category is at or above its floor "
            f"({thresholds.min_category_score:.1f}, hook {thresholds.min_hook_score:.1f})"
        )

    return {
        "verdict": verdict.value,
        "world_class": verdict is Verdict.PASS,
        "reason": reason,
        "below_floor": sorted(below),
        "not_measured": sorted(unmeasured),
        "why_not_measurable": {
            label: why
            for label, why in AUDIENCE_CATEGORIES.items()
            if label in unmeasured
        },
    }
