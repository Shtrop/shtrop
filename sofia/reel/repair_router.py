"""Repair router: rebuild the broken component, not the whole Reel.

Each defect maps to the narrowest stage that can fix it and to the checkpoint
the Reel must roll back to. Rolling back to ``VOICE_DONE`` to fix a subtitle
typo would throw away good renders; rolling back too little would leave the
defect in place. Both are bugs, so the mapping is explicit and tested.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Optional, Sequence

from sofia.core.checkpoint import StageState
from sofia.reel.contracts import ReelDefect, ReelDiagnosis


@dataclass(frozen=True)
class RepairRoute:
    """Where a defect sends the Reel."""

    defect: ReelDefect
    component: str
    resume_from: StageState
    scope: str
    regenerate_all: bool = False

    def to_dict(self) -> dict:
        return {
            "defect": self.defect.value,
            "component": self.component,
            "resume_from": self.resume_from.value,
            "scope": self.scope,
            "regenerate_all": self.regenerate_all,
        }


#: The canonical routing table. ``resume_from`` is the last *good* stage — the
#: Reel resumes from there rather than from zero.
ROUTES: Mapping[ReelDefect, RepairRoute] = {
    ReelDefect.BAD_HOOK: RepairRoute(
        ReelDefect.BAD_HOOK, "HookAgent", StageState.BRIEF_DONE, "hook + opening shot"
    ),
    ReelDefect.BAD_SCRIPT: RepairRoute(
        ReelDefect.BAD_SCRIPT, "ScriptAgent", StageState.BRIEF_DONE, "script lines"
    ),
    ReelDefect.BAD_SOURCE: RepairRoute(
        ReelDefect.BAD_SOURCE, "ShotDirector", StageState.SCRIPT_DONE, "source selection"
    ),
    ReelDefect.IDENTITY: RepairRoute(
        ReelDefect.IDENTITY,
        "VideoAgent",
        StageState.SHOTS_DONE,
        "affected face-critical shots only (IDENTITY_FIRST)",
    ),
    ReelDefect.SHOT: RepairRoute(
        ReelDefect.SHOT, "VideoAgent", StageState.SHOTS_DONE, "the single failing shot"
    ),
    ReelDefect.VOICE: RepairRoute(
        ReelDefect.VOICE, "VoiceTeam", StageState.SHOTS_DONE, "the failing voice clip"
    ),
    ReelDefect.PRONUNCIATION: RepairRoute(
        ReelDefect.PRONUNCIATION,
        "VoiceTeam",
        StageState.SHOTS_DONE,
        "the mispronounced word/phrase only",
    ),
    ReelDefect.LIPSYNC: RepairRoute(
        ReelDefect.LIPSYNC, "LipSyncAgent", StageState.VIDEO_DONE, "the talking shot"
    ),
    ReelDefect.EDIT: RepairRoute(
        ReelDefect.EDIT, "EditorAgent", StageState.LIPSYNC_DONE, "the edit timeline"
    ),
    ReelDefect.SUBTITLES: RepairRoute(
        ReelDefect.SUBTITLES, "SubtitleAgent", StageState.EDIT_DONE, "subtitle cues"
    ),
    ReelDefect.MUSIC: RepairRoute(
        ReelDefect.MUSIC, "Music/SFX Agent", StageState.EDIT_DONE, "music bed and ducking"
    ),
    ReelDefect.COVER: RepairRoute(
        ReelDefect.COVER, "CoverAgent", StageState.EDIT_DONE, "cover candidate"
    ),
    ReelDefect.STORY_CONTINUITY: RepairRoute(
        ReelDefect.STORY_CONTINUITY,
        "ReelDirector",
        StageState.BRIEF_DONE,
        "story arc and shot functions",
        regenerate_all=True,
    ),
    ReelDefect.NOT_MEASURED: RepairRoute(
        ReelDefect.NOT_MEASURED,
        "infrastructure",
        StageState.FINAL_QA,
        "no regeneration can fix an unmeasurable gate — fix the verifier",
    ),
}


@dataclass
class RepairDecision:
    """What the router decided for a batch of diagnoses."""

    routes: list[RepairRoute] = field(default_factory=list)
    resume_from: StageState = StageState.FINAL_QA
    components: list[str] = field(default_factory=list)
    unrepairable: list[str] = field(default_factory=list)
    shot_indices: list[int] = field(default_factory=list)

    @property
    def actionable(self) -> bool:
        return bool(self.routes) and not self.full_stop

    @property
    def full_stop(self) -> bool:
        """True when at least one defect cannot be fixed by regenerating anything."""
        return any(r.defect is ReelDefect.NOT_MEASURED for r in self.routes)

    def to_dict(self) -> dict:
        return {
            "resume_from": self.resume_from.value,
            "components": list(self.components),
            "shot_indices": list(self.shot_indices),
            "routes": [r.to_dict() for r in self.routes],
            "unrepairable": list(self.unrepairable),
        }


class RepairRouter:
    """Diagnoses -> the minimum work that can clear them."""

    name = "sofia.reel.repair_router"
    role = "RepairAgent"

    def route(self, diagnoses: Sequence[ReelDiagnosis]) -> RepairDecision:
        decision = RepairDecision()
        if not diagnoses:
            return decision

        earliest: Optional[StageState] = None
        for diag in diagnoses:
            route = ROUTES.get(diag.defect)
            if route is None:
                decision.unrepairable.append(
                    f"no repair route for defect {diag.defect.value}"
                )
                continue
            decision.routes.append(route)
            if route.component not in decision.components:
                decision.components.append(route.component)
            if diag.shot_index is not None and diag.shot_index not in decision.shot_indices:
                decision.shot_indices.append(diag.shot_index)
            if route.defect is ReelDefect.NOT_MEASURED:
                decision.unrepairable.append(
                    f"{diag.critic or 'critic'}: {diag.detail or 'gate not measurable'}"
                )
            if earliest is None or route.resume_from.rank < earliest.rank:
                earliest = route.resume_from

        decision.resume_from = earliest or StageState.FINAL_QA
        return decision
