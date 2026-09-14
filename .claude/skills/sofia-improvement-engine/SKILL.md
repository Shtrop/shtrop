---
name: sofia-improvement-engine
description: Цикл самоулучшения Sofia AI Studio - обнаружение разрывов, интернет-research, гипотезы, эксперименты, champion/challenger, benchmark, meta-critic, promotion и rollback. Использовать при запросах улучшить качество или метрику, исследовать новые техники и модели, добавить возможность или агента, провести эксперимент, сравнить варианты, продвинуть или откатить challenger, разобрать повторяющийся отказ, наполнить capability registry или improvement backlog.
---

# Sofia Improvement Engine

Навык отвечает на вопрос «как студия становится лучше» — безопасно и с доказательствами.

## ЦИКЛ

```
OBSERVE
→ DETECT GAP
→ INTERNET RESEARCH
→ HYPOTHESIS
→ PRE-REGISTER EXPERIMENT
→ CANDIDATE
→ RESTRICTED SANDBOX
→ BENCHMARK
→ META-CRITIC
→ PROMOTE / REJECT
→ MEMORY
→ MONITOR
```

Этапы не пропускаются. Переход к `PROMOTE` без `BENCHMARK` и `META-CRITIC` запрещён.

## КОМПОНЕНТЫ

- **ResearchAgent** — ищет актуальные техники под конкретный зафиксированный gap, а не «вообще».
- **Trend Scouts** — поставляют сигналы в Growth & Trend Engine и в backlog улучшений.
- **Capability Registry** — реестр того, что студия умеет, с доказательством и датой последней проверки.
- **Artifact Acquisition** — контролируемое получение внешних артефактов (модели, веса, код).
- **Agent Factory** — сборка нового агента под задачу из проверенных компонентов.
- **Agent Registry** — реестр действующих агентов, их зоны ответственности и владельцы ресурсов.
- **Experiment Engine** — регистрация, прогон и учёт экспериментов.
- **Champion / Challenger** — действующий вариант против претендента.
- **Failure Memory** — журнал отказов, включая отклонённых кандидатов и причины.
- **Promotion / Rollback** — перевод challenger в champion и гарантированный откат.
- **Improvement Backlog** — очередь разрывов с приоритетом `P0`–`P3`.

## ПРАВИЛО ВНЕШНЕГО КОДА

Запрещено:

```
INTERNET → PIP INSTALL PRODUCTION
```

Единственный допустимый путь:

```
research
→ quarantine
→ source / hash / license / security check
→ restricted worker / sandbox
→ test
→ benchmark
→ promote / reject
```

Зафиксировано: **`venv != OS security sandbox`.** Виртуальное окружение изолирует зависимости, а не процесс.

Пока нет настоящей OS isolation, исполнение произвольного кода из интернета = `BLOCKED`. Это не обходится срочностью задачи, просьбой ускорить или тем, что «пакет популярный».

## CHAMPION / CHALLENGER

Champion остаётся действующим, пока challenger не победил по заранее объявленному primary KPI на достаточной выборке.

Правило порядка: **`CHAMPION BEFORE CHALLENGER`** — сначала зафиксировать baseline champion на тех же данных, потом сравнивать. Сравнение с историческим числом из старого отчёта не является benchmark.

**`ROLLBACK BEFORE RISK`** — план отката существует и проверен до промоушена, а не после инцидента.

## ЭКСПЕРИМЕНТЫ

Каждый эксперимент регистрируется до прогона: `hypothesis`, `control`, `variant`, `sample`, `primary KPI`, `secondary KPI`. Результат записывается независимо от исхода.

Недостаточная выборка — `NOT_MEASURED`. Улучшение primary KPI при деградации secondary KPI — не победа, а предмет отдельного решения.

## META-CRITIC

Meta-critic проверяет не артефакт, а само суждение: корректность метрики, отсутствие подгонки гипотезы, наличие baseline, репрезентативность выборки, отсутствие утечки между control и variant.

Meta-critic имеет право вернуть `BLOCKED` даже при формально выигравшем challenger.

## FAILURE MEMORY

Хранить: симптом, root cause, затронутый контур, что помогло, что не помогло, отклонённых кандидатов и причины отказа.

Повторное появление известного симптома — повод искать системную причину, а не применять прошлый workaround второй раз.

## ГРАНИЦЫ

Improvement Engine не публикует контент, не ослабляет quality gates ради прохождения эксперимента и не меняет persona. Изменения вне явно указанного контура требуют решения владельца.
