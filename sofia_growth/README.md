# sofia_growth — Growth Engine Sofia

Замкнутый цикл: **TREND → CONTENT → PUBLICATION → INSIGHTS → GROWTH MEMORY → NEXT CONTENT DECISION**.

Дополняет студию `D:\AI_CONTENT\Sofia`, но **не является её частью** и ничего в ней не меняет.

## Границы безопасности

- Только чтение и расчёт. Скрипты не ходят в сеть, не публикуют, не используют токены.
- Ничего не удаляют: запись только в явно указанный `--out`, через temp → atomic replace.
- Не пишут в canonical state студии (`control_flags`, `agent_team_v2\state`, `CODEX_*`).
- Не снимают `FROZEN`, не трогают `PUBLISHING_DISABLED.flag`, не включают автопост.
- `PREDICTED` никогда не выдаётся за `REAL`; `NOT_MEASURED` никогда не превращается в `0`.
- Второй analytics pipeline не создаётся: движок читает выгрузки существующего.

## Структура

| Путь | Что |
|---|---|
| `tools/growth_cycle.py` | **Весь недельный цикл одной командой** |
| `tools/ingest_insights.py` | Собирает реальные выгрузки Insights в единый снимок |
| `tools/growth_kpi.py` | KPI, rolling-окна, лучшие/худшие посты, атрибуция, growth memory |
| `tools/trend_radar.py` | Ранжирует тренды в backlog; измеренное побеждает априорное |
| `tools/plan_builder.py` | Собирает следующий контент-план из бэклога и памяти |
| `tests/run_e2e.py` | Проверка всей цепочки на синтетике (34 проверки) |
| `tests/make_fixtures.py` | Генератор синтетических источников для E2E |
| `docs/DATA_SOURCES.md` | **Как дать движку реальные метрики** — начинать отсюда |
| `data/followers_snapshots.json` | Реальные снимки аккаунта (создаётся ingest-скриптом) |
| `data/growth_memory.json` | Измеренные исходы форматов: `SCALE` / `KEEP` / `DROP` |
| `data/trend_radar.json` | Машиночитаемые трендовые сигналы, обновляются еженедельно |
| `data/hook_bank.json` | Банк хуков первого кадра по форматам |
| `data/persona_guardrails.json` | Канон персоны и brand safety для скоринга |
| `trends/TREND_RADAR_<дата>.md` | Отчёт по трендам с источниками |
| `strategy/GROWTH_PLAYBOOK.md` | Система роста: уравнение, рычаги, правила |
| `plans/CONTENT_PLAN_<дата>_14d.md` | Двухнедельный план с гипотезами |

## Быстрый старт

Требуется Python 3.11+, внешних зависимостей нет. Подробности — в
[`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md).

```bash
# Весь цикл: Insights → KPI → память → бэклог → план → отчёт владельцу
python3 sofia_growth/tools/growth_cycle.py --studio "D:\AI_CONTENT\Sofia"

# Проверить, что цикл цел (синтетика, реальные данные не трогает)
python3 sofia_growth/tests/run_e2e.py
```

Стадии по отдельности, если нужно вмешаться в середину:

```bash
python3 sofia_growth/tools/ingest_insights.py --studio "D:\AI_CONTENT\Sofia"
python3 sofia_growth/tools/growth_kpi.py --days 30 --summary --write-memory
python3 sofia_growth/tools/trend_radar.py --top 8
python3 sofia_growth/tools/plan_builder.py --days 14
```

`growth_cycle.py` помечает каждую стадию как `OK`, `SKIPPED` или `BLOCKED`.
Стадия без данных не подменяется нулями: отчёт честно покажет `NOT_MEASURED`
и `GROWTH LOOP: PARTIAL`.

Коды возврата:

| Код | `ingest_insights.py` | `growth_kpi.py` | `trend_radar.py` |
|---|---|---|---|
| 0 | источники прочитаны | все KPI измерены | радар свежий |
| 1 | — | часть KPI `NOT_MEASURED` | — |
| 2 | источников нет, `BLOCKED` | данных нет вовсе | радар устарел (>14 дн.) |

## Как память замыкает цикл

`growth_kpi.py --write-memory` записывает по каждому формату/тренду вердикт
из **реальных** данных:

| Вердикт | Условие | Влияние на следующий план |
|---|---|---|
| `SCALE` | ≥3 публикаций, sends per reach ≥3% | Поднимается на первое место, метка `REAL` |
| `KEEP` | ≥3 публикаций, sends per reach ≥1% | Остаётся в ядре |
| `DROP` | ≥3 публикаций, sends per reach <1% | Опускается в самый низ бэклога |
| `INSUFFICIENT` | <3 публикаций | Не влияет: одна публикация ничего не доказывает |

Измеренный результат всегда важнее эвристики: формат с подтверждёнными
данными ранжируется выше догадки, даже если априорный score у догадки выше.

## Недельный ритм

1. **Пн** — обновить `data/trend_radar.json` свежими сигналами.
2. **Пт** — `python3 sofia_growth/tools/growth_cycle.py --studio "D:\AI_CONTENT\Sofia"`:
   соберёт метрики, обновит память, пересоберёт бэклог и выдаст план на следующие
   две недели вместе с отчётом.
3. **Вт-пт** — производство по плану через штатный pipeline с полными gates.

Формат с вердиктом `DROP` в новый план не попадёт: движок перестаёт его
предлагать, как только данные показали, что он не работает.

Стухший радар (>14 дней) в план не идёт: скрипт вернёт код 2 и пометит `WARN`.
