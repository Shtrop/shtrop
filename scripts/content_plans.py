#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Authored content plans for Sofia Reels.

These are real creative work, not templates: each has one idea, one hook, a
genuine SETUP -> DEVELOPMENT -> PAYOFF arc and a stated function for every
scene. The pool is deliberately small and honest about it — a batch benchmark
sampling four plans measures pipeline behaviour across content, not the full
variety a season of Reels would have.
"""

from __future__ import annotations

from sofia.reel.contracts import ShotType, StoryBeat
from sofia.reel.stages import ContentPlan, ScriptLine
from sofia.voice.contracts import Emotion

PLAN_RU = ContentPlan(
    idea=(
        "Признание вместо совета: не техника вытянула съёмку, а решение "
        "остановиться и послушать себя."
    ),
    purpose=(
        "Удержание через честный процесс: показать зрителю-создателю, что "
        "проблема не в оборудовании, и дать ему разрешение переснимать."
    ),
    hook="Ты правда думаешь, что дело в камере?",
    story_arc=(
        "SETUP: остывший капучино и четвёртый дубль. "
        "DEVELOPMENT: свет и камера те же, менялась только она. "
        "PAYOFF: помогла тишина, а не свет."
    ),
    cta="Сохрани, если ты тоже переснимаешь.",
    caption=(
        "Дело было не в камере. Четыре дубля, остывший капучино и тишина — "
        "вот что реально помогло переснять."
    ),
    cover_concept=(
        "Крупный тёплый кадр с изумрудным акцентом, текст хука в верхней "
        "трети, вне зоны интерфейса."
    ),
    music_brief="Тёплый минорный пад, 96 BPM, без ударных в хуке.",
    sfx_brief="Один мягкий акцент на переходе к payoff.",
    author="authored-by-model (AI ANALYSIS), reviewed against Sofia persona canon",
    lines=[
        ScriptLine(
            beat=StoryBeat.HOOK,
            text="Ты правда думаешь, что дело в камере?",
            emotion=Emotion.EXCITED,
            on_screen="Крупный план: Sofia смотрит прямо в камеру, вопрос в лоб",
            duration_s=2.8,
            shot_type=ShotType.TALKING,
        ),
        ScriptLine(
            beat=StoryBeat.SETUP,
            text="Этот дубль я переснимала четыре раза.",
            emotion=Emotion.CONFIDING,
            on_screen="Деталь: остывший капучино, пенка осела, рядом наушники",
            duration_s=3.0,
            shot_type=ShotType.DETAIL,
        ),
        ScriptLine(
            beat=StoryBeat.DEVELOPMENT,
            text="Свет был тот же. Камера та же. Менялась только я.",
            emotion=Emotion.SERIOUS,
            on_screen="B-roll: рабочий стол, свет не двигается, время идёт",
            duration_s=4.5,
            shot_type=ShotType.B_ROLL,
        ),
        ScriptLine(
            beat=StoryBeat.DEVELOPMENT,
            text="Я перестала себя слышать и записала ещё восемь дублей.",
            emotion=Emotion.CONFIDING,
            on_screen="Средний план: Sofia снимает наушники с шеи, пауза",
            duration_s=4.0,
            shot_type=ShotType.MEDIUM,
        ),
        ScriptLine(
            beat=StoryBeat.PAYOFF,
            text="Помог не свет. Помогла тишина.",
            emotion=Emotion.WARM,
            on_screen="Payoff: Sofia выдыхает, лёгкая улыбка, изумрудный акцент",
            duration_s=4.2,
            shot_type=ShotType.PAYOFF,
        ),
        ScriptLine(
            beat=StoryBeat.CTA,
            text="Сохрани, если ты тоже переснимаешь.",
            emotion=Emotion.PLAYFUL,
            on_screen="Деталь: рука тянется к чашке, текст призыва в кадре",
            duration_s=3.0,
            shot_type=ShotType.DETAIL,
        ),
    ],
)

PLAN_SILENCE = ContentPlan(
    idea=(
        "Тишина как рабочий инструмент: пауза в речи держит внимание сильнее, "
        "чем ещё одно слово."
    ),
    purpose=(
        "Дать конкретный приём, который зритель может применить в следующем "
        "же дубле, и показать его на слух."
    ),
    hook="Убери одно слово — и тебя дослушают.",
    story_arc=(
        "SETUP: я говорила без пауз и теряла зрителя. "
        "DEVELOPMENT: одна пауза перед главным словом. "
        "PAYOFF: досматривают до конца."
    ),
    cta="Попробуй в следующем дубле.",
    caption=(
        "Пауза перед главным словом работает лучше, чем ещё одно слово. "
        "Проверила на своих дублях."
    ),
    cover_concept="Тёплый кадр, текст хука в верхней трети, изумрудный акцент.",
    music_brief="Минимальный пад, без ударных, чтобы пауза была слышна.",
    sfx_brief="Полная тишина в момент паузы — это и есть эффект.",
    author="authored-by-model (AI ANALYSIS)",
    lines=[
        ScriptLine(
            beat=StoryBeat.HOOK,
            text="Убери одно слово, и тебя дослушают.",
            emotion=Emotion.EXCITED,
            on_screen="Крупный план: Sofia говорит в камеру, затем замолкает",
            duration_s=2.6,
            shot_type=ShotType.TALKING,
        ),
        ScriptLine(
            beat=StoryBeat.SETUP,
            text="Раньше я говорила без единой паузы.",
            emotion=Emotion.CONFIDING,
            on_screen="B-roll: волна аудио без просветов на экране",
            duration_s=3.4,
            shot_type=ShotType.B_ROLL,
        ),
        ScriptLine(
            beat=StoryBeat.DEVELOPMENT,
            text="Потом поставила одну паузу перед главным словом.",
            emotion=Emotion.SERIOUS,
            on_screen="Деталь: палец над клавишей, курсор режет дорожку",
            duration_s=4.0,
            shot_type=ShotType.DETAIL,
        ),
        ScriptLine(
            beat=StoryBeat.DEVELOPMENT,
            text="И перестала бояться, что меня выключат.",
            emotion=Emotion.WARM,
            on_screen="Средний план: Sofia выдыхает, плечи опускаются",
            duration_s=3.8,
            shot_type=ShotType.MEDIUM,
        ),
        ScriptLine(
            beat=StoryBeat.PAYOFF,
            text="Тишина держит лучше, чем ещё одно слово.",
            emotion=Emotion.WARM,
            on_screen="Payoff: Sofia смотрит в камеру, лёгкая пауза, улыбка",
            duration_s=4.2,
            shot_type=ShotType.PAYOFF,
        ),
        ScriptLine(
            beat=StoryBeat.CTA,
            text="Попробуй в следующем дубле.",
            emotion=Emotion.PLAYFUL,
            on_screen="Деталь: рука тянется к кнопке записи",
            duration_s=2.8,
            shot_type=ShotType.DETAIL,
        ),
    ],
)


PLAN_LIGHT = ContentPlan(
    idea=(
        "Один источник света и белая стена дают больше, чем комплект "
        "оборудования, если правильно встать."
    ),
    purpose=(
        "Снять у зрителя оправдание «нет света» и дать проверяемый приём: "
        "расстояние до стены важнее мощности лампы."
    ),
    hook="Дорогой свет не спасёт, если ты стоишь не там.",
    story_arc=(
        "SETUP: одна лампа и белая стена. "
        "DEVELOPMENT: два шага ближе к стене меняют картинку. "
        "PAYOFF: дело было в расстоянии, а не в лампе."
    ),
    cta="Сделай два шага и сравни.",
    caption=(
        "Одна лампа, белая стена и два шага. Расстояние до стены меняет свет "
        "сильнее, чем цена лампы."
    ),
    cover_concept="Половина кадра в тени, половина в тёплом свете, текст сверху.",
    music_brief="Спокойный пад, лёгкий пульс на переходе.",
    sfx_brief="Один мягкий акцент на смене положения.",
    author="authored-by-model (AI ANALYSIS)",
    lines=[
        ScriptLine(
            beat=StoryBeat.HOOK,
            text="Дорогой свет не спасёт, если ты стоишь не там.",
            emotion=Emotion.EXCITED,
            on_screen="Крупный план: половина лица в тени, Sofia в камеру",
            duration_s=2.9,
            shot_type=ShotType.TALKING,
        ),
        ScriptLine(
            beat=StoryBeat.SETUP,
            text="У меня одна лампа и белая стена.",
            emotion=Emotion.NEUTRAL,
            on_screen="Деталь: лампа и пустая белая стена",
            duration_s=3.0,
            shot_type=ShotType.DETAIL,
        ),
        ScriptLine(
            beat=StoryBeat.DEVELOPMENT,
            text="Я сделала два шага ближе к стене.",
            emotion=Emotion.CONFIDING,
            on_screen="B-roll: тень на стене смягчается, свет становится ровным",
            duration_s=4.4,
            shot_type=ShotType.B_ROLL,
        ),
        ScriptLine(
            beat=StoryBeat.DEVELOPMENT,
            text="Ничего больше не меняла. Ни лампу, ни камеру.",
            emotion=Emotion.SERIOUS,
            on_screen="Средний план: Sofia стоит у стены, свет ровный",
            duration_s=4.0,
            shot_type=ShotType.MEDIUM,
        ),
        ScriptLine(
            beat=StoryBeat.PAYOFF,
            text="Дело было в расстоянии, а не в лампе.",
            emotion=Emotion.WARM,
            on_screen="Payoff: Sofia улыбается, мягкий свет на лице",
            duration_s=4.0,
            shot_type=ShotType.PAYOFF,
        ),
        ScriptLine(
            beat=StoryBeat.CTA,
            text="Сделай два шага и сравни.",
            emotion=Emotion.PLAYFUL,
            on_screen="Деталь: рука отмеряет два шага по полу",
            duration_s=2.7,
            shot_type=ShotType.DETAIL,
        ),
    ],
)


#: The pool a batch benchmark samples from. Small, and documented as such.
PLAN_POOL: tuple[tuple[str, ContentPlan], ...] = (
    ("camera", PLAN_RU),
    ("silence", PLAN_SILENCE),
    ("light", PLAN_LIGHT),
)
