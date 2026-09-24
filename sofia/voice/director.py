"""VoiceDirector — decides language, emotion, pace, tone, style, scene context.

The director is the only role allowed to author a :class:`VoiceBrief`. It also
compiles the pronunciation lexicon that the PronunciationCritic will hold the
generator to, so "read this name this way" is a *contract*, not a hope.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Mapping, Optional, Sequence

from sofia.voice.contracts import Emotion, Language, Pace, VoiceBrief

#: Canonical renderings Sofia must use, per language. Extend from the studio's
#: persona/config files rather than inventing new ones here.
CANONICAL_LEXICON: Mapping[str, Mapping[str, str]] = {
    "ru": {
        "Sofia": "Софи",
        "Reels": "Рилс",
        "AI": "Эй Ай",
        "Instagram": "Инстаграм",
    },
    "uk": {
        "Sofia": "Софі",
        "Reels": "Рілс",
        "AI": "Ей Ай",
        "Instagram": "Інстаграм",
    },
    "en": {
        "Sofia": "Sofia",
        "Reels": "Reels",
    },
}

#: Scene intent -> (emotion, pace). The director maps story function to delivery.
_SCENE_DELIVERY: Mapping[str, tuple[Emotion, Pace]] = {
    "hook": (Emotion.EXCITED, Pace.FAST),
    "setup": (Emotion.WARM, Pace.NATURAL),
    "development": (Emotion.CONFIDING, Pace.NATURAL),
    "payoff": (Emotion.WARM, Pace.NATURAL),
    "cta": (Emotion.PLAYFUL, Pace.NATURAL),
    "broll": (Emotion.NEUTRAL, Pace.NATURAL),
}


@dataclass
class VoiceDirector:
    """Turns a line of script plus a scene intent into a full brief."""

    name: str = "sofia.voice.director"
    role: str = "VoiceDirector"
    default_tone: str = "sofia-signature"

    def brief(
        self,
        text: str,
        language: Language,
        *,
        scene: str = "development",
        style: str = "reel-talking",
        scene_context: str = "",
        must_pronounce: Sequence[str] = (),
        extra_lexicon: Optional[Mapping[str, str]] = None,
        target_duration_s: Optional[float] = None,
        emotion: Optional[Emotion] = None,
        pace: Optional[Pace] = None,
    ) -> VoiceBrief:
        default_emotion, default_pace = _SCENE_DELIVERY.get(
            scene, (Emotion.NEUTRAL, Pace.NATURAL)
        )
        lexicon = dict(CANONICAL_LEXICON.get(language.value, {}))
        if extra_lexicon:
            lexicon.update(extra_lexicon)
        # Only keep entries that actually occur in this line, so the critic is
        # not asked to verify words nobody said.
        lexicon = {k: v for k, v in lexicon.items() if _mentions(text, k)}

        return VoiceBrief(
            language=language,
            text=text.strip(),
            emotion=emotion or default_emotion,
            pace=pace or default_pace,
            tone=self.default_tone,
            style=style,
            scene_context=scene_context or scene,
            must_pronounce=tuple(must_pronounce),
            lexicon=lexicon,
            target_duration_s=target_duration_s or estimate_duration(text, language),
        )

    def brief_script(
        self,
        lines: Sequence[tuple[str, str]],
        language: Language,
        **kwargs: object,
    ) -> list[VoiceBrief]:
        """Brief a whole script given ``(scene, text)`` pairs."""
        return [
            self.brief(text, language, scene=scene, **kwargs)  # type: ignore[arg-type]
            for scene, text in lines
        ]


def _mentions(text: str, word: str) -> bool:
    return re.search(rf"\b{re.escape(word)}\b", text, flags=re.IGNORECASE) is not None


#: Rough syllables-per-word by language, used only to set a *target* duration.
_SYLLABLES_PER_WORD = {"ru": 2.6, "uk": 2.6, "en": 1.5}


def estimate_duration(text: str, language: Language, pace: Pace = Pace.NATURAL) -> float:
    """Predicted clip length. Marked PREDICTED wherever it is reported."""

    words = len(re.findall(r"[^\W\d_]+|\d+", text, flags=re.UNICODE))
    syllables = words * _SYLLABLES_PER_WORD.get(language.value, 2.0)
    lo, hi = pace.target_sps
    mid = (lo + hi) / 2.0
    return round(syllables / mid, 2) if mid else 0.0
