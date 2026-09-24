"""Creative and production stages of the Reel pipeline.

TREND -> IDEA -> CONTENT PURPOSE -> HOOK -> SCRIPT -> STORYBOARD -> SHOT LIST
-> SOURCE SELECTION.

Creative work needs a creative source. Rather than fabricating "ideas" from a
template and passing them off as authored, the stages take a
:class:`CreativeSource`. ``AuthoredPlan`` wraps a plan a human or a model
actually wrote; ``UnavailableCreative`` raises, so a Reel is never built on
invented filler.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Optional, Protocol, Sequence, runtime_checkable

from sofia.core.errors import BackendUnavailableError
from sofia.reel.contracts import (
    GrowthInput,
    ReelBrief,
    Shot,
    ShotType,
    StoryBeat,
)
from sofia.reel.shots import assign_profiles, estimated_cost, validate_story
from sofia.voice.contracts import Emotion, Language


@dataclass
class ScriptLine:
    """One spoken or silent beat of the script."""

    beat: StoryBeat
    text: str
    emotion: Emotion = Emotion.NEUTRAL
    on_screen: str = ""
    duration_s: float = 3.0
    shot_type: ShotType = ShotType.B_ROLL

    def to_dict(self) -> dict:
        return {
            "beat": self.beat.value,
            "text": self.text,
            "emotion": self.emotion.value,
            "on_screen": self.on_screen,
            "duration_s": self.duration_s,
            "shot_type": self.shot_type.value,
        }


@dataclass
class ContentPlan:
    """The authored creative plan for one Reel."""

    idea: str
    purpose: str
    hook: str
    story_arc: str
    cta: str
    caption: str
    lines: list[ScriptLine] = field(default_factory=list)
    cover_concept: str = ""
    music_brief: str = ""
    sfx_brief: str = ""
    author: str = "unattributed"

    def to_dict(self) -> dict:
        return {
            "idea": self.idea,
            "purpose": self.purpose,
            "hook": self.hook,
            "story_arc": self.story_arc,
            "cta": self.cta,
            "caption": self.caption,
            "cover_concept": self.cover_concept,
            "music_brief": self.music_brief,
            "sfx_brief": self.sfx_brief,
            "author": self.author,
            "lines": [ln.to_dict() for ln in self.lines],
        }


@runtime_checkable
class CreativeSource(Protocol):
    """Where idea / hook / script actually come from."""

    name: str

    def available(self) -> bool: ...

    def plan(self, brief_seed: GrowthInput, language: Language) -> ContentPlan: ...


class UnavailableCreative:
    """No creative source — the pipeline refuses to invent filler."""

    def __init__(self, reason: str = "no creative source configured") -> None:
        self.name = "unavailable-creative"
        self.reason = reason

    def available(self) -> bool:
        return False

    def plan(self, brief_seed: GrowthInput, language: Language) -> ContentPlan:
        raise BackendUnavailableError(f"cannot author a content plan: {self.reason}")


@dataclass
class AuthoredPlan:
    """A plan a human or a model actually wrote, passed in as data."""

    content_plan: ContentPlan
    name: str = "authored-plan"

    def available(self) -> bool:
        return bool(self.content_plan.lines)

    def plan(self, brief_seed: GrowthInput, language: Language) -> ContentPlan:
        if not self.available():
            raise BackendUnavailableError("the authored plan contains no script lines")
        return self.content_plan


# --------------------------------------------------------------------------
class TrendAgent:
    """Turns Growth Engine input into the trend the Reel will ride."""

    name = "sofia.reel.trend"
    role = "TrendAgent"

    def run(self, growth: GrowthInput) -> dict:
        if not growth.trend.strip():
            raise BackendUnavailableError("Growth Engine supplied no trend")
        return {
            "trend": growth.trend,
            "audience": growth.audience,
            "hook_hypothesis": growth.hook_hypothesis,
            "evidence": growth.evidence,
        }


class IdeaAgent:
    """Idea + content purpose, from the trend and the creative source."""

    name = "sofia.reel.idea"
    role = "IdeaAgent"

    def __init__(self, creative: CreativeSource) -> None:
        self.creative = creative

    def run(self, growth: GrowthInput, language: Language) -> ContentPlan:
        plan = self.creative.plan(growth, language)
        if not plan.purpose.strip():
            raise BackendUnavailableError("content plan has no stated purpose")
        return plan


class HookAgent:
    """Owns the first 1.5 seconds."""

    name = "sofia.reel.hook"
    role = "HookAgent"

    def run(self, plan: ContentPlan) -> str:
        if not plan.hook.strip():
            raise BackendUnavailableError("content plan has no hook")
        opening = next(
            (ln for ln in plan.lines if ln.beat in (StoryBeat.HOOK, StoryBeat.SETUP)),
            None,
        )
        if opening is None:
            raise BackendUnavailableError("script does not open on a hook or setup beat")
        return plan.hook


class ScriptAgent:
    """Validates the script is speakable and beat-complete."""

    name = "sofia.reel.script"
    role = "ScriptAgent"

    def run(self, plan: ContentPlan) -> list[ScriptLine]:
        if not plan.lines:
            raise BackendUnavailableError("content plan has no script lines")
        beats = {ln.beat for ln in plan.lines}
        missing = [
            b.value
            for b in (StoryBeat.SETUP, StoryBeat.DEVELOPMENT, StoryBeat.PAYOFF)
            if b not in beats
        ]
        if missing:
            raise BackendUnavailableError(
                f"script is missing beats: {missing}; a Reel needs SETUP, "
                "DEVELOPMENT and PAYOFF"
            )
        return list(plan.lines)


class StoryboardAgent:
    """Script lines -> described shots with an explicit function each."""

    name = "sofia.reel.storyboard"
    role = "StoryboardAgent"

    def run(self, lines: Sequence[ScriptLine]) -> list[Shot]:
        shots: list[Shot] = []
        for idx, line in enumerate(lines):
            description = line.on_screen.strip()
            if not description:
                raise BackendUnavailableError(
                    f"script line {idx} ({line.beat.value}) has no on-screen description; "
                    "every scene must have a function"
                )
            shots.append(
                Shot(
                    index=idx,
                    beat=line.beat,
                    shot_type=line.shot_type,
                    description=description,
                    duration_s=line.duration_s,
                    voice_line=line.text,
                    emotion=line.emotion,
                )
            )
        return shots


class ShotDirector:
    """Assigns the generator profile per shot type and reports GPU cost."""

    name = "sofia.reel.shot_director"
    role = "ShotDirector"

    def run(self, shots: Sequence[Shot]) -> tuple[list[Shot], dict]:
        assigned = assign_profiles(shots)
        problems = validate_story(assigned)
        if problems:
            raise BackendUnavailableError(
                "shot list does not form a story: " + "; ".join(problems)
            )
        return assigned, estimated_cost(assigned)


class SourceSelector:
    """Chooses the source image/reference for each shot.

    Face-critical shots get the canonical Sofia reference; cheap shot types get
    none, which is the whole point of shot-type routing.
    """

    name = "sofia.reel.source"
    role = "ShotDirector:source"

    def __init__(self, sofia_references: Mapping[str, str]) -> None:
        self.references = dict(sofia_references)

    def run(self, shots: Sequence[Shot]) -> list[Shot]:
        for shot in shots:
            if not shot.shot_type.needs_face:
                shot.source_ref = ""
                continue
            ref = self.references.get(shot.shot_type.value) or self.references.get(
                "default", ""
            )
            if not ref:
                raise BackendUnavailableError(
                    f"shot {shot.index} is {shot.shot_type.value} but no canonical "
                    "Sofia reference is registered; a stand-in face is not Sofia"
                )
            shot.source_ref = ref
        return list(shots)


def build_reel_brief(
    reel_id: str,
    plan: ContentPlan,
    growth: GrowthInput,
    language: Language,
    *,
    target_duration_s: float = 22.0,
    continuity_notes: str = "",
) -> ReelBrief:
    """Fold the creative plan and the growth input into the director's brief."""

    return ReelBrief(
        reel_id=reel_id,
        purpose=plan.purpose,
        audience=growth.audience,
        language=language,
        trend=growth.trend,
        hook=plan.hook,
        story_arc=plan.story_arc,
        cta=plan.cta,
        growth=growth,
        target_duration_s=target_duration_s,
        continuity_notes=continuity_notes,
        expected_kpi=dict(growth.target_kpi),
    )
