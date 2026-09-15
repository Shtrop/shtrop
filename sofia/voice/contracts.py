"""Data contracts for the Sofia Voice Team."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Sequence

from sofia.core.verdict import Measurement, Verdict


class Language(str, enum.Enum):
    """Languages in which one canonical Sofia voice must exist."""

    RU = "ru"
    UA = "uk"
    EN = "en"

    @property
    def label(self) -> str:
        return {"ru": "RU", "uk": "UA", "en": "EN"}[self.value]


class Emotion(str, enum.Enum):
    NEUTRAL = "neutral"
    WARM = "warm"
    EXCITED = "excited"
    CONFIDING = "confiding"
    SERIOUS = "serious"
    PLAYFUL = "playful"


class Pace(str, enum.Enum):
    SLOW = "slow"
    NATURAL = "natural"
    FAST = "fast"

    @property
    def target_sps(self) -> tuple[float, float]:
        """Acceptable syllable-nucleus rate window, syllables/second."""
        return {"slow": (2.2, 4.2), "natural": (3.2, 6.2), "fast": (4.5, 8.0)}[self.value]


@dataclass(frozen=True)
class VoiceBrief:
    """What the VoiceDirector decides before a single sample is generated.

    This is the role's actual output: language, emotion, pace, tone, style and
    scene context, plus the pronunciation hints the critics will hold the
    generator to.
    """

    language: Language
    text: str
    emotion: Emotion = Emotion.NEUTRAL
    pace: Pace = Pace.NATURAL
    tone: str = "sofia-signature"
    style: str = "reel-talking"
    scene_context: str = ""
    must_pronounce: tuple[str, ...] = ()
    lexicon: Mapping[str, str] = field(default_factory=dict)
    target_duration_s: Optional[float] = None
    speaker_profile: str = "sofia"

    def with_text(self, text: str) -> "VoiceBrief":
        return VoiceBrief(
            language=self.language,
            text=text,
            emotion=self.emotion,
            pace=self.pace,
            tone=self.tone,
            style=self.style,
            scene_context=self.scene_context,
            must_pronounce=self.must_pronounce,
            lexicon=self.lexicon,
            target_duration_s=self.target_duration_s,
            speaker_profile=self.speaker_profile,
        )

    def to_dict(self) -> dict:
        return {
            "language": self.language.value,
            "text": self.text,
            "emotion": self.emotion.value,
            "pace": self.pace.value,
            "tone": self.tone,
            "style": self.style,
            "scene_context": self.scene_context,
            "must_pronounce": list(self.must_pronounce),
            "lexicon": dict(self.lexicon),
            "target_duration_s": self.target_duration_s,
            "speaker_profile": self.speaker_profile,
        }


class VoiceDefect(str, enum.Enum):
    """Diagnosis categories the repair router understands.

    Each maps to the *narrowest* thing that must be redone — never "regenerate
    everything".
    """

    MISPRONOUNCED_WORD = "MISPRONOUNCED_WORD"
    WRONG_STRESS = "WRONG_STRESS"
    NUMBER_READING = "NUMBER_READING"
    NAME_READING = "NAME_READING"
    BORROWED_WORD = "BORROWED_WORD"
    HIGH_WER = "HIGH_WER"
    SEMANTIC_DRIFT = "SEMANTIC_DRIFT"
    IDENTITY_DRIFT = "IDENTITY_DRIFT"
    WRONG_LANGUAGE = "WRONG_LANGUAGE"
    ROBOTIC = "ROBOTIC"
    OVERACTED = "OVERACTED"
    BAD_PAUSES = "BAD_PAUSES"
    PACE_OFF = "PACE_OFF"
    CLIPPING = "CLIPPING"
    LOUDNESS = "LOUDNESS"
    NOT_MEASURED = "NOT_MEASURED"


class RepairScope(str, enum.Enum):
    """How much has to be regenerated to fix a defect."""

    WORD = "word"
    PHRASE = "phrase"
    SENTENCE = "sentence"
    PROSODY = "prosody"
    LANGUAGE = "language"
    IDENTITY = "identity"
    MIX = "mix"
    NONE = "none"


#: Narrowest scope that can genuinely fix each defect.
DEFECT_SCOPE: Mapping[VoiceDefect, RepairScope] = {
    VoiceDefect.MISPRONOUNCED_WORD: RepairScope.WORD,
    VoiceDefect.WRONG_STRESS: RepairScope.WORD,
    VoiceDefect.NUMBER_READING: RepairScope.PHRASE,
    VoiceDefect.NAME_READING: RepairScope.WORD,
    VoiceDefect.BORROWED_WORD: RepairScope.WORD,
    VoiceDefect.HIGH_WER: RepairScope.SENTENCE,
    VoiceDefect.SEMANTIC_DRIFT: RepairScope.SENTENCE,
    VoiceDefect.IDENTITY_DRIFT: RepairScope.IDENTITY,
    VoiceDefect.WRONG_LANGUAGE: RepairScope.LANGUAGE,
    VoiceDefect.ROBOTIC: RepairScope.PROSODY,
    VoiceDefect.OVERACTED: RepairScope.PROSODY,
    VoiceDefect.BAD_PAUSES: RepairScope.PROSODY,
    VoiceDefect.PACE_OFF: RepairScope.PROSODY,
    VoiceDefect.CLIPPING: RepairScope.MIX,
    VoiceDefect.LOUDNESS: RepairScope.MIX,
    VoiceDefect.NOT_MEASURED: RepairScope.NONE,
}


@dataclass(frozen=True)
class VoiceDiagnosis:
    """A single, addressable defect.

    ``locus`` names the exact word/phrase/sentence at fault so the repair agent
    regenerates only that span.
    """

    defect: VoiceDefect
    locus: str = ""
    detail: str = ""
    critic: str = ""
    measurement: Optional[Measurement] = None

    @property
    def scope(self) -> RepairScope:
        return DEFECT_SCOPE[self.defect]

    def to_dict(self) -> dict:
        return {
            "defect": self.defect.value,
            "scope": self.scope.value,
            "locus": self.locus,
            "detail": self.detail,
            "critic": self.critic,
            "measurement": self.measurement.to_dict() if self.measurement else None,
        }


@dataclass
class VoiceArtifact:
    """A generated audio candidate and everything measured about it."""

    brief: VoiceBrief
    audio_path: Optional[str]
    backend: str
    generation_s: float = 0.0
    transcript: Optional[str] = None
    measurements: list[Measurement] = field(default_factory=list)
    attempts: int = 1
    meta: dict[str, Any] = field(default_factory=dict)

    def measurement(self, name: str) -> Optional[Measurement]:
        for m in self.measurements:
            if m.name == name:
                return m
        return None

    def to_dict(self) -> dict:
        return {
            "brief": self.brief.to_dict(),
            "audio_path": self.audio_path,
            "backend": self.backend,
            "generation_s": round(self.generation_s, 3),
            "transcript": self.transcript,
            "attempts": self.attempts,
            "measurements": [m.to_dict() for m in self.measurements],
            "meta": dict(self.meta),
        }


@dataclass
class VoiceVerdict:
    """The Voice Team's final, fail-closed answer for one clip."""

    verdict: Verdict
    artifact: Optional[VoiceArtifact]
    report: Any = None  # sofia.core.gates.GateReport
    diagnoses: Sequence[VoiceDiagnosis] = ()
    repairs: Sequence[Mapping[str, Any]] = ()
    reason: str = ""

    @property
    def passed(self) -> bool:
        return self.verdict is Verdict.PASS

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict.value,
            "reason": self.reason,
            "artifact": self.artifact.to_dict() if self.artifact else None,
            "report": self.report.to_dict() if self.report is not None else None,
            "diagnoses": [d.to_dict() for d in self.diagnoses],
            "repairs": [dict(r) for r in self.repairs],
        }
