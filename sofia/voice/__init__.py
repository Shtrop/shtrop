"""Sofia Voice Team: one canonical Sofia voice in RU, UA and EN."""

from sofia.voice.backends import VoiceBackends, Voiceprint, detect_backends
from sofia.voice.contracts import (
    Emotion,
    Language,
    Pace,
    RepairScope,
    VoiceArtifact,
    VoiceBrief,
    VoiceDefect,
    VoiceDiagnosis,
    VoiceVerdict,
)
from sofia.voice.critics import (
    CRITICAL_VOICE_GATES,
    PronunciationCritic,
    ProsodyCritic,
    SemanticCritic,
    VoiceIdentityCritic,
    VoiceThresholds,
)
from sofia.voice.director import VoiceDirector
from sofia.voice.generator import VoiceGenerator
from sofia.voice.pipeline import VoiceTeam, build_voice_agents
from sofia.voice.repair import RepairPlan, VoiceRepairAgent

__all__ = [
    "CRITICAL_VOICE_GATES",
    "Emotion",
    "Language",
    "Pace",
    "PronunciationCritic",
    "ProsodyCritic",
    "RepairPlan",
    "RepairScope",
    "SemanticCritic",
    "VoiceArtifact",
    "VoiceBackends",
    "VoiceBrief",
    "VoiceDefect",
    "VoiceDiagnosis",
    "VoiceDirector",
    "VoiceGenerator",
    "VoiceIdentityCritic",
    "VoiceRepairAgent",
    "VoiceTeam",
    "VoiceThresholds",
    "VoiceVerdict",
    "Voiceprint",
    "build_voice_agents",
    "detect_backends",
]
