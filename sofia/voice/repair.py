"""VoiceRepairAgent — targeted repair, never blanket regeneration.

The agent receives a *diagnosis* and rewrites only what that diagnosis
implicates: a word, a phrase, a sentence, the prosody direction, the language
routing, or the identity/reference selection.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Sequence

from sofia.voice.contracts import (
    Emotion,
    Pace,
    RepairScope,
    VoiceBrief,
    VoiceDefect,
    VoiceDiagnosis,
)


@dataclass
class RepairPlan:
    """What the repair agent decided to change, and why."""

    scope: RepairScope
    brief: VoiceBrief
    changes: list[str] = field(default_factory=list)
    unrepairable: list[str] = field(default_factory=list)

    @property
    def actionable(self) -> bool:
        return bool(self.changes)

    def to_dict(self) -> dict:
        return {
            "scope": self.scope.value,
            "changes": list(self.changes),
            "unrepairable": list(self.unrepairable),
            "brief": self.brief.to_dict(),
        }


@dataclass
class VoiceRepairAgent:
    """Applies the narrowest fix that can plausibly clear the diagnosis."""

    name: str = "sofia.voice.repair"
    role: str = "VoiceRepairAgent"

    def plan(
        self, brief: VoiceBrief, diagnoses: Sequence[VoiceDiagnosis]
    ) -> RepairPlan:
        if not diagnoses:
            return RepairPlan(scope=RepairScope.NONE, brief=brief)

        scope = _widest_scope(d.scope for d in diagnoses)
        plan = RepairPlan(scope=scope, brief=brief)
        text = brief.text
        lexicon = dict(brief.lexicon)
        emotion = brief.emotion
        pace = brief.pace
        style = brief.style

        for diag in diagnoses:
            if diag.defect in (
                VoiceDefect.MISPRONOUNCED_WORD,
                VoiceDefect.WRONG_STRESS,
                VoiceDefect.NAME_READING,
                VoiceDefect.BORROWED_WORD,
            ):
                if not diag.locus:
                    plan.unrepairable.append(f"{diag.defect.value}: no locus given")
                    continue
                hint = _pronunciation_hint(diag.locus, brief)
                if hint and lexicon.get(diag.locus) != hint:
                    lexicon[diag.locus] = hint
                    plan.changes.append(
                        f"pin pronunciation of {diag.locus!r} -> {hint!r}"
                    )
                else:
                    # Re-spell the single word inline so the model re-reads it.
                    new_text = _respell_word(text, diag.locus)
                    if new_text != text:
                        text = new_text
                        plan.changes.append(f"re-spell word {diag.locus!r} in place")
                    else:
                        plan.unrepairable.append(
                            f"{diag.defect.value}: cannot localise {diag.locus!r} in text"
                        )

            elif diag.defect is VoiceDefect.NUMBER_READING:
                new_text = _spell_number_inline(text, diag.locus, brief)
                if new_text != text:
                    text = new_text
                    plan.changes.append(f"write number {diag.locus!r} out in words")
                else:
                    plan.unrepairable.append(
                        f"NUMBER_READING: {diag.locus!r} not found in text"
                    )

            elif diag.defect in (VoiceDefect.HIGH_WER, VoiceDefect.SEMANTIC_DRIFT):
                sentence = _sentence_containing(text, diag.locus)
                if sentence:
                    plan.changes.append(
                        f"regenerate sentence: {sentence[:60]!r}"
                    )
                else:
                    plan.changes.append("regenerate the whole line")

            elif diag.defect is VoiceDefect.WRONG_LANGUAGE:
                plan.changes.append(
                    f"force language routing to {brief.language.value!r} "
                    "and reselect the language-specific Sofia reference"
                )

            elif diag.defect is VoiceDefect.IDENTITY_DRIFT:
                plan.changes.append(
                    "IDENTITY_FIRST: reselect Sofia reference clips for "
                    f"{brief.language.label} and re-run with identity priority"
                )

            elif diag.defect is VoiceDefect.ROBOTIC:
                emotion = _warmer(emotion)
                style = "reel-talking-expressive"
                plan.changes.append(f"raise expressiveness -> {emotion.value}/{style}")

            elif diag.defect is VoiceDefect.OVERACTED:
                emotion = _calmer(emotion)
                style = "reel-talking"
                plan.changes.append(f"reduce overacting -> {emotion.value}/{style}")

            elif diag.defect is VoiceDefect.BAD_PAUSES:
                new_text = _tighten_pauses(text)
                if new_text != text:
                    text = new_text
                    plan.changes.append("tighten punctuation to remove dead air")
                else:
                    plan.changes.append("re-render with shorter inter-phrase pauses")

            elif diag.defect is VoiceDefect.PACE_OFF:
                pace = _adjust_pace(pace, diag.detail)
                plan.changes.append(f"retarget pace -> {pace.value}")

            elif diag.defect in (VoiceDefect.CLIPPING, VoiceDefect.LOUDNESS):
                plan.changes.append(
                    "re-render at safe gain and re-normalise (mix-only fix)"
                )

            elif diag.defect is VoiceDefect.NOT_MEASURED:
                plan.unrepairable.append(
                    "NOT_MEASURED: a critical verifier could not run; repair cannot "
                    "clear this — the backend must be fixed"
                )

        repaired = VoiceBrief(
            language=brief.language,
            text=text,
            emotion=emotion,
            pace=pace,
            tone=brief.tone,
            style=style,
            scene_context=brief.scene_context,
            must_pronounce=brief.must_pronounce,
            lexicon=lexicon,
            target_duration_s=brief.target_duration_s,
            speaker_profile=brief.speaker_profile,
        )
        plan.brief = repaired
        return plan


# ---- helpers -------------------------------------------------------------
_SCOPE_ORDER = [
    RepairScope.NONE,
    RepairScope.MIX,
    RepairScope.WORD,
    RepairScope.PHRASE,
    RepairScope.PROSODY,
    RepairScope.SENTENCE,
    RepairScope.LANGUAGE,
    RepairScope.IDENTITY,
]


def _widest_scope(scopes) -> RepairScope:
    best = RepairScope.NONE
    for s in scopes:
        if _SCOPE_ORDER.index(s) > _SCOPE_ORDER.index(best):
            best = s
    return best


def _pronunciation_hint(word: str, brief: VoiceBrief) -> Optional[str]:
    from sofia.voice.director import CANONICAL_LEXICON

    table = CANONICAL_LEXICON.get(brief.language.value, {})
    for key, value in table.items():
        if key.lower() == word.lower():
            return value
    return None


def _respell_word(text: str, word: str) -> str:
    """Insert a soft separator so the model re-reads a stuck word."""
    pattern = re.compile(rf"\b{re.escape(word)}\b", flags=re.IGNORECASE)
    if not pattern.search(text):
        return text
    return pattern.sub(lambda m: m.group(0), text, count=1)


def _spell_number_inline(text: str, number: str, brief: VoiceBrief) -> str:
    from sofia.voice.text import _NUMBER_WORDS, _spell_int

    digits = number.rstrip("%").replace(",", ".")
    if not digits.isdigit():
        return text
    table = _NUMBER_WORDS.get(brief.language.value, {})
    words = " ".join(_spell_int(int(digits), table))
    if not words or words == digits:
        return text
    return text.replace(number, words + ("%" if number.endswith("%") else ""), 1)


def _sentence_containing(text: str, locus: str) -> str:
    if not locus:
        return ""
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        if locus.lower() in sentence.lower():
            return sentence
    return ""


def _tighten_pauses(text: str) -> str:
    tightened = re.sub(r"\.{3,}", ".", text)
    tightened = re.sub(r"\s*—\s*", ", ", tightened)
    tightened = re.sub(r",\s*,+", ", ", tightened)
    return tightened


_WARMER = {
    Emotion.NEUTRAL: Emotion.WARM,
    Emotion.WARM: Emotion.CONFIDING,
    Emotion.SERIOUS: Emotion.WARM,
    Emotion.CONFIDING: Emotion.EXCITED,
    Emotion.PLAYFUL: Emotion.EXCITED,
    Emotion.EXCITED: Emotion.EXCITED,
}
_CALMER = {v: k for k, v in _WARMER.items()}


def _warmer(emotion: Emotion) -> Emotion:
    return _WARMER.get(emotion, Emotion.WARM)


def _calmer(emotion: Emotion) -> Emotion:
    return _CALMER.get(emotion, Emotion.NEUTRAL)


def _adjust_pace(pace: Pace, detail: str) -> Pace:
    too_fast = "outside" in detail and _rate_from(detail) is not None and _is_fast(detail)
    if too_fast:
        return Pace.SLOW if pace is Pace.NATURAL else Pace.NATURAL
    return Pace.NATURAL if pace is Pace.SLOW else Pace.FAST


def _rate_from(detail: str) -> Optional[float]:
    m = re.search(r"speech rate ([\d.]+)/s", detail)
    return float(m.group(1)) if m else None


def _is_fast(detail: str) -> bool:
    rate = _rate_from(detail)
    m = re.search(r"\[([\d.]+), ([\d.]+)\]", detail)
    if rate is None or not m:
        return False
    return rate > float(m.group(2))
