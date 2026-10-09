# Sofia Growth & Trend Engine — полная спецификация

Главная цель контура: не просто генерировать контент, а системно увеличивать `REACH`, `WATCH TIME`, `RETENTION`, `SHARES`, `SAVES`, `COMMENTS`, `PROFILE VISITS`, `FOLLOWS`, `FOLLOWER CONVERSION`.

Все метрики в этом контуре подчиняются общему Evidence Standard. Платформенные данные помечать `REAL`, локальные измерения `MEASURED_LOCAL`, оценки модели `PREDICTED` или `AI ANALYSIS`, отсутствие данных `NOT_MEASURED`. Не подставлять `0` вместо отсутствующего значения и не строить решения о росте на predicted-метриках, выданных за фактические.

## 1. CONTINUOUS TREND WATCH

Постоянно собирать fresh trend signals из доступных источников:

Instagram, TikTok, YouTube, Google Trends, Reddit, news/web, AI creator ecosystem, competitor creators.

Каждый тренд хранить со всеми полями:

| Поле | Смысл |
|---|---|
| `source` | Откуда получен сигнал |
| `timestamp` | Когда зафиксирован |
| `velocity` | Текущая скорость распространения |
| `growth rate` | Динамика скорости |
| `saturation` | Насколько рынок уже занят |
| `relevance_to_sofia` | Связь с персонажем и его миром |
| `audience_fit` | Соответствие текущей аудитории |
| `viral_potential` | Потенциал охвата |
| `confidence` | Достоверность самого сигнала |
| `expiry` | Когда тренд перестаёт быть актуальным |

Старый тренд автоматически теряет вес. Не воскрешать просроченный тренд без нового свежего сигнала.

## 2. TREND → CONTENT FIT

Не использовать тренд только потому, что он популярен.

Для каждого тренда считать: `SOFIA_FIT`, `AUDIENCE_FIT`, `BRAND_FIT`, `PRODUCTION_COST`, `SATURATION`, `EXPECTED_UPSIDE`.

Решающее правило: **высокий viral score + низкий Sofia fit = `REJECT`.**

Фиксировать причину отказа в growth memory: отклонённый тренд — это тоже данные.

## 3. DAILY OPPORTUNITY SCAN

Каждый день формировать список `TOP CONTENT OPPORTUNITIES`. Каждая позиция содержит:

```
TREND
FORMAT
HOOK
WHY_NOW
WHY_SOFIA
EXPECTED_METRIC
CONFIDENCE
```

`WHY_NOW` объясняет окно возможности, `WHY_SOFIA` — почему это именно её контент, а не любой аккаунт. Позиция без внятного `WHY_SOFIA` не попадает в план.

## 4. GROWTH EXPERIMENTS

Автоматически создавать эксперименты по осям: hook A/B, opening frame, длительность видео, caption, CTA, темп монтажа, музыка, время публикации, тема, визуальный стиль, голосовой стиль.

Каждый эксперимент описывается до прогона:

```
hypothesis
control
variant
sample
primary KPI
secondary KPI
result
```

Гипотеза регистрируется заранее (pre-registration). Подгонка гипотезы под полученный результат запрещена. Недостаточный `sample` — вердикт `NOT_MEASURED`, а не «вариант победил».

## 5. FOLLOWER CONVERSION

Считать отдельно две воронки:

```
views → profile visit
profile visit → follow
```

Оптимизировать именно follower conversion. **Не считать высокий view count автоматически хорошим результатом:** охват без перехода в профиль и без подписки означает, что hook работает, а обещание профиля — нет.

Разбирать падение по стадиям: падение `views → profile visit` указывает на контент и CTA, падение `profile visit → follow` — на профиль, шапку, закреп и общую витрину.

## 6. VIRALITY QUALITY

Viral-контент считается полезным, только если он одновременно:

- не ломает persona Sofia;
- не снижает content quality;
- не приводит нерелевантную аудиторию;
- не создаёт дешёвый clickbait profile.

Нарушение любого пункта — `REJECT`, независимо от метрик. Вирусный пост, приведший нерелевантную аудиторию, ухудшает будущий охват и учитывается в growth memory как отрицательный результат, а не как успех.

## 7. WINNER SCALING

Если формат доказанно работает, увеличить вероятность похожего контента. Но не копировать один и тот же Reel.

Хранить: winning hook, winning topic, winning format, winning duration, winning camera style, winning editing style.

Использовать variations: менять как минимум одну значимую ось при сохранении доказанного ядра.

## 8. FATIGUE DETECTION

Отслеживать: declining retention, declining engagement, declining follower conversion, topic saturation.

Если формат начинает выгорать — снижать его frequency. Раннее снижение частоты предпочтительнее резкой отмены: формат может восстановиться после паузы.

## 9. EXPLORATION / EXPLOITATION

Держать примерно `80–90%` proven strategies и `10–20%` experiments.

Автоматически корректировать соотношение по стабильности аккаунта: при нестабильных метриках или активном инциденте смещаться к exploitation, при стагнации проверенных форматов — к exploration.

## 10. CREATOR BENCHMARKING

Постоянно сравнивать aggregate performance patterns сильных creators: hook, duration, story structure, editing, visual language, CTA, posting cadence.

Заимствовать структурные паттерны. **Не копировать конкретный контент**, кадры, сценарии и тексты.

## 11. ACCOUNT HEALTH

Рост подписчиков не должен достигаться ценой spam, posting flood, повторяющегося контента или low-quality trend chasing.

Контролировать: frequency, content diversity, quality, audience fatigue. Ухудшение account health — блокирующий сигнал для growth-инициатив, даже если краткосрочные метрики растут.

## 12. WEEKLY GROWTH REVIEW

Раз в неделю отвечать на полный список:

- What gained followers?
- What lost attention?
- What had highest retention?
- What had highest shares?
- What had highest saves?
- What converted profile visits into follows?
- Which trend worked?
- Which trend failed?
- Which format is becoming saturated?
- What should Sofia test next week?

Ответ без данных — `NOT_MEASURED`, а не предположение.

## 13. MONTHLY STRATEGY UPDATE

Раз в месяц обновлять: content pillars, audience segments, best formats, worst formats, posting windows, story arcs, growth strategy.

**Не менять persona Sofia без отдельной причины.** Persona — не переменная стратегии.

## 14. GROWTH MEMORY

Хранить и переиспользовать: `topic_performance`, `hook_performance`, `reel_performance`, `story_performance`, `caption_performance`, `CTA_performance`, `posting_time_performance`, `follower_conversion`, `trend_performance`.

Growth memory — источник данных для weekly review, winner scaling и fatigue detection. Записи не удалять, включая отрицательные результаты.

## 15. SELF-IMPROVEMENT LINK

Обнаруженный разрыв (пример: low Reel retention) запускает цепочку:

```
detect gap
→ research current creator/video techniques
→ generate improvement hypothesis
→ test Challenger
→ compare
→ promote/reject
```

Цепочка исполняется через `sofia-improvement-engine` и подчиняется его правилам карантина: research не даёт права на установку внешнего кода в production.

## 16. NORTH STAR

Главная growth-метрика: **`SUSTAINABLE AUDIENCE GROWTH`.**

Не `MORE POSTS`, не `MORE VIEWS`. Нужен рост: relevant followers, retention, engagement, returning viewers.

## 17. SAFETY RULE

Growth Engine не имеет права автоматически:

- массово увеличивать posting frequency;
- покупать рекламу;
- покупать подписчиков;
- использовать spam;
- копировать creators;
- ослаблять quality gates.

Каждое из этих действий требует отдельного явного решения владельца. Growth-цель никогда не является основанием для ослабления gate.

## 18. FINAL GOAL

Sofia должна сама понимать: что сейчас в тренде; что подходит именно ей; что нравится её аудитории; что приводит новых подписчиков; что удерживает старых; что перестало работать; какой следующий эксперимент провести.

Цель: каждую неделю Sofia становится сильнее как creator, а не просто производит больше контента.
