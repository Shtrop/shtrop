"""Data contracts for the Reel Production Team."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Sequence

from sofia.core.verdict import Measurement, Verdict
from sofia.voice.contracts import Emotion, Language


class ShotType(str, enum.Enum):
    """Not every shot needs Sofia's face.

    Routing by shot type is what saves GPU time, cuts identity failures and
    buys visual variety — one video model is not asked to generate everything.
    """

    FACE_CRITICAL = "FACE_CRITICAL"
    TALKING = "TALKING"
    MEDIUM = "MEDIUM"
    B_ROLL = "B_ROLL"
    DETAIL = "DETAIL"
    TRANSITION = "TRANSITION"
    PAYOFF = "PAYOFF"

    @property
    def needs_face(self) -> bool:
        return self in (ShotType.FACE_CRITICAL, ShotType.TALKING, ShotType.PAYOFF)

    @property
    def needs_lipsync(self) -> bool:
        return self is ShotType.TALKING

    @property
    def identity_gate(self) -> bool:
        """Whether the strict identity gate applies to this shot."""
        return self.needs_face


class StoryBeat(str, enum.Enum):
    """Every scene must have a function. SETUP -> DEVELOPMENT -> PAYOFF."""

    HOOK = "HOOK"
    SETUP = "SETUP"
    DEVELOPMENT = "DEVELOPMENT"
    PAYOFF = "PAYOFF"
    CTA = "CTA"


@dataclass
class Shot:
    """One shot with an explicit story function."""

    index: int
    beat: StoryBeat
    shot_type: ShotType
    description: str
    duration_s: float
    voice_line: str = ""
    emotion: Emotion = Emotion.NEUTRAL
    camera: str = ""
    generator_profile: str = ""
    source_ref: str = ""
    video_path: Optional[str] = None
    lipsync_path: Optional[str] = None
    measurements: list[Measurement] = field(default_factory=list)

    @property
    def function(self) -> str:
        return f"{self.beat.value}/{self.shot_type.value}"

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "beat": self.beat.value,
            "shot_type": self.shot_type.value,
            "description": self.description,
            "duration_s": self.duration_s,
            "voice_line": self.voice_line,
            "emotion": self.emotion.value,
            "camera": self.camera,
            "generator_profile": self.generator_profile,
            "source_ref": self.source_ref,
            "video_path": self.video_path,
            "lipsync_path": self.lipsync_path,
            "measurements": [m.to_dict() for m in self.measurements],
        }


@dataclass(frozen=True)
class GrowthInput:
    """What the Growth Engine hands the ReelDirector before anything is made."""

    trend: str
    audience: str
    target_kpi: Mapping[str, float]
    hook_hypothesis: str
    evidence: str = "historical-analytics"
    shadow_planning: bool = True

    def to_dict(self) -> dict:
        return {
            "trend": self.trend,
            "audience": self.audience,
            "target_kpi": dict(self.target_kpi),
            "hook_hypothesis": self.hook_hypothesis,
            "evidence": self.evidence,
            "shadow_planning": self.shadow_planning,
        }


@dataclass
class ReelBrief:
    """Everything the ReelDirector must know before producing.

    The director is accountable for the finished Reel, so purpose, audience,
    trend, hook, story arc, shots, emotions, voice, continuity and expected KPI
    all live here — not scattered across generators.
    """

    reel_id: str
    purpose: str
    audience: str
    language: Language
    trend: str
    hook: str
    story_arc: str
    cta: str
    growth: Optional[GrowthInput] = None
    target_duration_s: float = 22.0
    continuity_notes: str = ""
    expected_kpi: Mapping[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "reel_id": self.reel_id,
            "purpose": self.purpose,
            "audience": self.audience,
            "language": self.language.value,
            "trend": self.trend,
            "hook": self.hook,
            "story_arc": self.story_arc,
            "cta": self.cta,
            "growth": self.growth.to_dict() if self.growth else None,
            "target_duration_s": self.target_duration_s,
            "continuity_notes": self.continuity_notes,
            "expected_kpi": dict(self.expected_kpi),
        }


class ReelDefect(str, enum.Enum):
    """Diagnosis categories understood by the repair router.

    A Reel is never rebuilt from scratch for a single defect — each category
    maps to the narrowest component that must be redone.
    """

    BAD_HOOK = "BAD_HOOK"
    BAD_SCRIPT = "BAD_SCRIPT"
    BAD_SOURCE = "BAD_SOURCE"
    IDENTITY = "IDENTITY"
    VOICE = "VOICE"
    PRONUNCIATION = "PRONUNCIATION"
    LIPSYNC = "LIPSYNC"
    SHOT = "SHOT"
    EDIT = "EDIT"
    SUBTITLES = "SUBTITLES"
    COVER = "COVER"
    MUSIC = "MUSIC"
    STORY_CONTINUITY = "STORY_CONTINUITY"
    NOT_MEASURED = "NOT_MEASURED"


@dataclass(frozen=True)
class ReelDiagnosis:
    defect: ReelDefect
    locus: str = ""
    detail: str = ""
    critic: str = ""
    shot_index: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "defect": self.defect.value,
            "locus": self.locus,
            "detail": self.detail,
            "critic": self.critic,
            "shot_index": self.shot_index,
        }


@dataclass
class ReelAssets:
    """Every artifact path a Reel accumulates. A path is not a PASS."""

    shots: list[Shot] = field(default_factory=list)
    voice_clips: dict[str, str] = field(default_factory=dict)
    music: Optional[str] = None
    sfx: list[str] = field(default_factory=list)
    subtitles: Optional[str] = None
    cover: Optional[str] = None
    edit: Optional[str] = None
    final: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "shots": [s.to_dict() for s in self.shots],
            "voice_clips": dict(self.voice_clips),
            "music": self.music,
            "sfx": list(self.sfx),
            "subtitles": self.subtitles,
            "cover": self.cover,
            "edit": self.edit,
            "final": self.final,
        }


@dataclass
class ReelResult:
    """The ReelDirector's final, fail-closed answer."""

    reel_id: str
    verdict: Verdict
    stage: Any  # StageState
    brief: Optional[ReelBrief] = None
    assets: ReelAssets = field(default_factory=ReelAssets)
    report: Any = None  # GateReport
    diagnoses: Sequence[ReelDiagnosis] = ()
    repairs: Sequence[Mapping[str, Any]] = ()
    scores: Mapping[str, Optional[float]] = field(default_factory=dict)
    #: Whether this Reel may be called world-class, and why not if it may not.
    #: Deliberately separate from ``verdict``: passing every gate means no
    #: defect was found, which is a weaker statement.
    quality_claim: Mapping[str, Any] = field(default_factory=dict)
    reason: str = ""
    owner: str = ""

    @property
    def ready_for_owner_review(self) -> bool:
        return self.verdict is Verdict.PASS

    def to_dict(self) -> dict:
        return {
            "reel_id": self.reel_id,
            "verdict": self.verdict.value,
            "stage": getattr(self.stage, "value", str(self.stage)),
            "owner": self.owner,
            "reason": self.reason,
            "brief": self.brief.to_dict() if self.brief else None,
            "assets": self.assets.to_dict(),
            "report": self.report.to_dict() if self.report is not None else None,
            "diagnoses": [d.to_dict() for d in self.diagnoses],
            "repairs": [dict(r) for r in self.repairs],
            "scores": dict(self.scores),
            "quality_claim": dict(self.quality_claim),
        }
