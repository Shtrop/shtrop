# sofia_growth — цикл «тренды → контент → рост подписчиков»

Рабочий контур для отслеживания трендов и роста подписчиков Sofia.
Дополняет студию `D:\AI_CONTENT\Sofia`, но **не является её частью** и ничего в ней не меняет.

## Границы безопасности

- Только чтение и расчёт. Скрипты ничего не публикуют и не ходят в Instagram.
- Ничего не удаляют: запись только в явно указанный `--out`, через temp → atomic replace.
- Не пишут в canonical state студии (`control_flags`, `agent_team_v2\state`, `CODEX_*`).
- Не снимают `FROZEN`, не трогают `PUBLISHING_DISABLED.flag`, не включают автопост.
- `PREDICTED` никогда не выдаётся за `REAL`; `NOT_MEASURED` никогда не превращается в `0`.

## Структура

| Путь | Что это |
|---|---|
| `trends/TREND_RADAR_<дата>.md` | Отчёт по трендам с источниками и датой |
| `data/trend_radar.json` | Машиночитаемые сигналы — обновляется еженедельно |
| `data/persona_guardrails.json` | Рабочая копия канона персоны и brand safety для скоринга |
| `data/followers_snapshots.template.json` | Шаблон снимков аккаунта (копию назвать `followers_snapshots.json`) |
| `strategy/GROWTH_PLAYBOOK.md` | Система роста: уравнение, рычаги, правила, цикл |
| `plans/CONTENT_PLAN_<дата>_14d.md` | Двухнедельный план с брифами и гипотезами |
| `tools/trend_radar.py` | Ранжирует сигналы в backlog экспериментов |
| `tools/growth_kpi.py` | Считает KPI роста по снимкам и называет узкое место |

## Использование

Требуется Python 3.11+, внешних зависимостей нет.

```bash
# Backlog экспериментов из текущего радара
python3 sofia_growth/tools/trend_radar.py --top 8

# То же в файл и в JSON для агентов студии
python3 sofia_growth/tools/trend_radar.py --json --out sofia_growth/trends/backlog.json

# KPI роста за 14 дней
python3 sofia_growth/tools/growth_kpi.py --snapshots sofia_growth/data/followers_snapshots.json --days 14
```

Коды возврата:

| Код | `trend_radar.py` | `growth_kpi.py` |
|---|---|---|
| 0 | радар свежий | все метрики посчитаны |
| 1 | — | данные частичные |
| 2 | радар устарел (>14 дн.) | данных нет, вердикт `NOT_MEASURED` |

## Недельный ритм

1. **Пн** — обновить `data/trend_radar.json`, прогнать `trend_radar.py`, взять топ-3.
2. **Вт-пт** — производство и публикация по штатному pipeline с полными gates.
3. **Пт** — снимок в `followers_snapshots.json`, прогнать `growth_kpi.py`, записать вывод.

Стухший радар (>14 дней) в план не идёт: скрипт вернёт код 2 и пометит `WARN`.

## Как снимать данные для KPI

Источник — только Instagram Insights или официальный API аккаунта Sofia.
Поля снимка описаны в `data/followers_snapshots.template.json`. Отсутствующее поле
**пропускать**, а не ставить `0`: иначе расчёт узкого места врёт.
