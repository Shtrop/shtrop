# -*- coding: utf-8 -*-
"""Representative acceptance corpus for the Sofia Voice benchmark.

Each language has >= 20 clips spanning short / medium / long lines and the full
emotional range, plus the hard cases that break TTS in practice: numbers,
proper names, borrowed words, questions and lists.

These are *acceptance* texts, not marketing copy. They exist so a language's
score is measured on a representative spread instead of on cherry-picked
sentences.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from sofia.voice.contracts import Emotion, Language, Pace


@dataclass(frozen=True)
class CorpusItem:
    """One benchmark clip specification."""

    clip_id: str
    text: str
    scene: str
    emotion: Emotion
    pace: Pace
    length: str  # short | medium | long
    hard_case: str = ""  # numbers | names | borrowed | question | list | ""

    def to_dict(self) -> dict:
        return {
            "clip_id": self.clip_id,
            "text": self.text,
            "scene": self.scene,
            "emotion": self.emotion.value,
            "pace": self.pace.value,
            "length": self.length,
            "hard_case": self.hard_case,
        }


def _item(i, text, scene, emotion, pace, length, hard="") -> CorpusItem:
    return CorpusItem(i, text, scene, emotion, pace, length, hard)


RU: tuple[CorpusItem, ...] = (
    _item("ru-01", "Привет.", "setup", Emotion.WARM, Pace.NATURAL, "short"),
    _item("ru-02", "Смотри, что получилось.", "hook", Emotion.EXCITED, Pace.FAST, "short"),
    _item("ru-03", "Я так больше не делаю.", "development", Emotion.SERIOUS, Pace.NATURAL, "short"),
    _item("ru-04", "Секунду, сейчас покажу.", "setup", Emotion.PLAYFUL, Pace.FAST, "short"),
    _item("ru-05", "Это заняло у меня двадцать пять минут.", "development", Emotion.NEUTRAL, Pace.NATURAL, "medium", "numbers"),
    _item("ru-06", "Я потратила 40% времени впустую.", "development", Emotion.SERIOUS, Pace.NATURAL, "medium", "numbers"),
    _item("ru-07", "Меня зовут Sofia, и я снимаю Reels каждый день.", "setup", Emotion.WARM, Pace.NATURAL, "medium", "names"),
    _item("ru-08", "Мой рабочий процесс держится на трёх вещах: свет, звук и монтаж.", "development", Emotion.CONFIDING, Pace.NATURAL, "medium", "list"),
    _item("ru-09", "А ты замечал, сколько времени уходит на дубли?", "hook", Emotion.PLAYFUL, Pace.FAST, "medium", "question"),
    _item("ru-10", "Капучино остыл, пока я переснимала этот кадр в четвёртый раз.", "development", Emotion.PLAYFUL, Pace.NATURAL, "medium"),
    _item("ru-11", "Честно? Я почти удалила этот проект.", "hook", Emotion.CONFIDING, Pace.NATURAL, "short"),
    _item("ru-12", "Наушники на шее — это не стиль, это привычка.", "development", Emotion.WARM, Pace.NATURAL, "medium"),
    _item("ru-13", "Здесь важен не свет, а терпение.", "payoff", Emotion.SERIOUS, Pace.SLOW, "short"),
    _item("ru-14", "Сохрани, если хочешь повторить.", "cta", Emotion.PLAYFUL, Pace.NATURAL, "short"),
    _item("ru-15", "Я перезаписывала этот дубль восемь раз, и каждый раз голос звучал иначе, потому что я уставала и переставала себя слышать.", "development", Emotion.CONFIDING, Pace.NATURAL, "long"),
    _item("ru-16", "Если ты только начинаешь, не покупай дорогой микрофон: сначала научись говорить в тишине, потом уже думай про технику и обработку.", "development", Emotion.WARM, Pace.NATURAL, "long", "list"),
    _item("ru-17", "Самое сложное в этой работе — не съёмка и не монтаж, а решение выложить то, что получилось, когда тебе кажется, что вышло недостаточно хорошо.", "payoff", Emotion.SERIOUS, Pace.SLOW, "long"),
    _item("ru-18", "Instagram показывает не лучшее видео, а то, которое досмотрели до конца.", "development", Emotion.NEUTRAL, Pace.NATURAL, "medium", "borrowed"),
    _item("ru-19", "Три шага: снять, послушать, переснять.", "development", Emotion.NEUTRAL, Pace.FAST, "short", "list"),
    _item("ru-20", "Ты правда думаешь, что дело в камере?", "hook", Emotion.EXCITED, Pace.FAST, "short", "question"),
    _item("ru-21", "AI помогает мне монтировать, но говорить за меня он пока не умеет.", "development", Emotion.PLAYFUL, Pace.NATURAL, "medium", "borrowed"),
    _item("ru-22", "И вот теперь — самое интересное.", "payoff", Emotion.EXCITED, Pace.NATURAL, "short"),
)

UA: tuple[CorpusItem, ...] = (
    _item("uk-01", "Привіт.", "setup", Emotion.WARM, Pace.NATURAL, "short"),
    _item("uk-02", "Дивись, що вийшло.", "hook", Emotion.EXCITED, Pace.FAST, "short"),
    _item("uk-03", "Я так більше не роблю.", "development", Emotion.SERIOUS, Pace.NATURAL, "short"),
    _item("uk-04", "Секунду, зараз покажу.", "setup", Emotion.PLAYFUL, Pace.FAST, "short"),
    _item("uk-05", "Це забрало в мене двадцять п'ять хвилин.", "development", Emotion.NEUTRAL, Pace.NATURAL, "medium", "numbers"),
    _item("uk-06", "Я витратила 40% часу намарно.", "development", Emotion.SERIOUS, Pace.NATURAL, "medium", "numbers"),
    _item("uk-07", "Мене звати Sofia, і я знімаю Reels щодня.", "setup", Emotion.WARM, Pace.NATURAL, "medium", "names"),
    _item("uk-08", "Мій робочий процес тримається на трьох речах: світло, звук і монтаж.", "development", Emotion.CONFIDING, Pace.NATURAL, "medium", "list"),
    _item("uk-09", "А ти помічав, скільки часу йде на дублі?", "hook", Emotion.PLAYFUL, Pace.FAST, "medium", "question"),
    _item("uk-10", "Капучино вихололо, поки я перезнімала цей кадр учетверте.", "development", Emotion.PLAYFUL, Pace.NATURAL, "medium"),
    _item("uk-11", "Чесно? Я мало не видалила цей проєкт.", "hook", Emotion.CONFIDING, Pace.NATURAL, "short"),
    _item("uk-12", "Навушники на шиї — це не стиль, це звичка.", "development", Emotion.WARM, Pace.NATURAL, "medium"),
    _item("uk-13", "Тут важливе не світло, а терпіння.", "payoff", Emotion.SERIOUS, Pace.SLOW, "short"),
    _item("uk-14", "Збережи, якщо хочеш повторити.", "cta", Emotion.PLAYFUL, Pace.NATURAL, "short"),
    _item("uk-15", "Я перезаписувала цей дубль вісім разів, і щоразу голос звучав інакше, бо я втомлювалася і переставала себе чути.", "development", Emotion.CONFIDING, Pace.NATURAL, "long"),
    _item("uk-16", "Якщо ти лише починаєш, не купуй дорогий мікрофон: спершу навчися говорити в тиші, а вже потім думай про техніку та обробку.", "development", Emotion.WARM, Pace.NATURAL, "long", "list"),
    _item("uk-17", "Найскладніше в цій роботі — не зйомка і не монтаж, а рішення викласти те, що вийшло, коли тобі здається, що вийшло недостатньо добре.", "payoff", Emotion.SERIOUS, Pace.SLOW, "long"),
    _item("uk-18", "Instagram показує не найкраще відео, а те, яке додивилися до кінця.", "development", Emotion.NEUTRAL, Pace.NATURAL, "medium", "borrowed"),
    _item("uk-19", "Три кроки: зняти, послухати, перезняти.", "development", Emotion.NEUTRAL, Pace.FAST, "short", "list"),
    _item("uk-20", "Ти справді думаєш, що річ у камері?", "hook", Emotion.EXCITED, Pace.FAST, "short", "question"),
    _item("uk-21", "AI допомагає мені монтувати, але говорити за мене він поки що не вміє.", "development", Emotion.PLAYFUL, Pace.NATURAL, "medium", "borrowed"),
    _item("uk-22", "І ось тепер — найцікавіше.", "payoff", Emotion.EXCITED, Pace.NATURAL, "short"),
)

EN: tuple[CorpusItem, ...] = (
    _item("en-01", "Hey.", "setup", Emotion.WARM, Pace.NATURAL, "short"),
    _item("en-02", "Look what happened.", "hook", Emotion.EXCITED, Pace.FAST, "short"),
    _item("en-03", "I don't do that anymore.", "development", Emotion.SERIOUS, Pace.NATURAL, "short"),
    _item("en-04", "One second, let me show you.", "setup", Emotion.PLAYFUL, Pace.FAST, "short"),
    _item("en-05", "That took me twenty five minutes.", "development", Emotion.NEUTRAL, Pace.NATURAL, "medium", "numbers"),
    _item("en-06", "I wasted 40% of my time on this.", "development", Emotion.SERIOUS, Pace.NATURAL, "medium", "numbers"),
    _item("en-07", "My name is Sofia, and I shoot Reels every single day.", "setup", Emotion.WARM, Pace.NATURAL, "medium", "names"),
    _item("en-08", "My whole workflow rests on three things: light, sound, and editing.", "development", Emotion.CONFIDING, Pace.NATURAL, "medium", "list"),
    _item("en-09", "Have you ever counted how long retakes actually take?", "hook", Emotion.PLAYFUL, Pace.FAST, "medium", "question"),
    _item("en-10", "My cappuccino went cold while I reshot this one frame for the fourth time.", "development", Emotion.PLAYFUL, Pace.NATURAL, "medium"),
    _item("en-11", "Honestly? I almost deleted this project.", "hook", Emotion.CONFIDING, Pace.NATURAL, "short"),
    _item("en-12", "Headphones around my neck aren't a style choice, they're a habit.", "development", Emotion.WARM, Pace.NATURAL, "medium"),
    _item("en-13", "It's not the light that matters here, it's patience.", "payoff", Emotion.SERIOUS, Pace.SLOW, "short"),
    _item("en-14", "Save this if you want to try it.", "cta", Emotion.PLAYFUL, Pace.NATURAL, "short"),
    _item("en-15", "I re-recorded this take eight times, and every single time my voice sounded different, because I got tired and stopped hearing myself.", "development", Emotion.CONFIDING, Pace.NATURAL, "long"),
    _item("en-16", "If you're just starting, don't buy an expensive microphone: first learn to speak in a quiet room, and only then worry about gear and processing.", "development", Emotion.WARM, Pace.NATURAL, "long", "list"),
    _item("en-17", "The hardest part of this job isn't the shooting or the editing, it's deciding to publish what you made when you're convinced it isn't good enough yet.", "payoff", Emotion.SERIOUS, Pace.SLOW, "long"),
    _item("en-18", "Instagram doesn't show the best video, it shows the one people finished watching.", "development", Emotion.NEUTRAL, Pace.NATURAL, "medium", "borrowed"),
    _item("en-19", "Three steps: shoot, listen, reshoot.", "development", Emotion.NEUTRAL, Pace.FAST, "short", "list"),
    _item("en-20", "You really think it's the camera?", "hook", Emotion.EXCITED, Pace.FAST, "short", "question"),
    _item("en-21", "AI helps me edit, but it still can't talk for me.", "development", Emotion.PLAYFUL, Pace.NATURAL, "medium", "borrowed"),
    _item("en-22", "And now, the interesting part.", "payoff", Emotion.EXCITED, Pace.NATURAL, "short"),
)

CORPUS: dict[Language, tuple[CorpusItem, ...]] = {
    Language.RU: RU,
    Language.UA: UA,
    Language.EN: EN,
}


def corpus_for(language: Language) -> Sequence[CorpusItem]:
    return CORPUS[language]


def coverage(language: Language) -> dict:
    """Prove the corpus really is representative before trusting its score."""

    items = CORPUS[language]
    lengths: dict[str, int] = {}
    emotions: dict[str, int] = {}
    hard: dict[str, int] = {}
    for it in items:
        lengths[it.length] = lengths.get(it.length, 0) + 1
        emotions[it.emotion.value] = emotions.get(it.emotion.value, 0) + 1
        if it.hard_case:
            hard[it.hard_case] = hard.get(it.hard_case, 0) + 1
    return {
        "clips": len(items),
        "lengths": lengths,
        "emotions": emotions,
        "hard_cases": hard,
    }
