# Runbook: ростовой контур Sofia (growth autopilot)

Цель — не «генератор с автопостингом», а замкнутый контур:

```
TREND -> AUDIENCE -> IDEA -> HOOK -> STORY -> MEDIA -> QA -> PUBLISH
      -> RETENTION / SHARES / SAVES / FOLLOWS -> LEARNING -> NEXT CONTENT
```

Вирусность не гарантируется и не обещается. Задача контура — системно повышать
вероятность роста по реальным данным. Всё, что нельзя измерить, считается
`NOT_MEASURED`, а не успехом.

---

## 0. Порядок приоритетов

| Приоритет | Что | Почему |
|---|---|---|
| 1 | Стабильность хоста | На хосте, который уходит в ресет, рост не строится: обрывается рендер и теряются артефакты |
| 2 | Производство и публикация | Без потока контента нечего измерять |
| 3 | Измерение | Без lineage и метрик обучение недостоверно |
| 4 | Обучение и эксперименты | Меняют следующее решение, а не отчёт |
| 5 | Масштабирование выигравших форматов | Только после того, как выигрыш доказан |

Пока стоит `HOST_SAFE_HOLD.flag`, пункт 1 не закрыт. Разработку ростового
контура это не останавливает, но выводить его в production поверх нестабильного
хоста нельзя: см. `RUNBOOK_host_safe_hold.md`.

---

## 1. Сначала измерить, потом строить

Главная ошибка развития студии — создать агента, который уже есть, или создать
агента, которого никто не вызывает. Поэтому любое изменение начинается с двух
read-only проверок.

```powershell
.\audit_agent_matrix.ps1                 # кто из агентов реален
.\audit_growth_readiness.ps1             # какие звенья контура замкнуты
```

Связать одно с другим:

```powershell
.\audit_agent_matrix.ps1 -OutDir C:\Temp\sofia_audit
.\audit_growth_readiness.ps1 -MatrixReport C:\Temp\sofia_audit\agent_matrix.json
```

Оба скрипта ничего не меняют: не трогают `control_flags`, `HOST_SAFE_HOLD.flag`,
publishing state, сервисы и планировщик, ничего не удаляют, пишут только в `-OutDir`.

---

## 2. Что считается настоящим агентом

Файл или класс доказательством агента **не является**. Проверка из пяти улик,
все обязательны:

| Улика | Что именно принимается |
|---|---|
| `RUNNER` | задача планировщика, живой процесс, регистрация в оркестраторе или точка входа |
| `EXECUTION` | след запуска в окне `-FreshHours` (по умолчанию 48 ч) |
| `OUTPUT` | свежий артефакт, который он произвёл |
| `CONSUMER` | этот артефакт читает кто-то ещё, кроме самого агента |
| `METRIC` | есть метрика успеха |

Классы `audit_agent_matrix.ps1`:

| Класс | Смысл | Что делать |
|---|---|---|
| `ACTIVE_REAL` | все пять улик | ничего, работает |
| `PARTIAL` | часть улик | дотянуть недостающую улику, не писать нового агента |
| `SPEC_ONLY` | есть спецификация/код, нет запуска | подключить к оркестратору либо признать спецификацией |
| `BROKEN` | запускается, но не производит output | чинить или перенаправить задачу существующему агенту |
| `DUPLICATE` | две независимые точки входа на одну роль | оставить одну, вторую в retire |
| `MISSING` | ничего нет | создавать — но только если функция действительно отсутствует |

**Создавать нового агента можно только для класса `MISSING`.** Для `PARTIAL`
и `SPEC_ONLY` правильное действие — подключить существующее.

Кандидаты на retire (точка входа есть, ссылок, запусков и планировщика нет)
перечисляются отдельно. Скрипт их **не удаляет**: NO-DELETE, решение за владельцем.

---

## 3. Что проверяет growth-аудит

`audit_growth_readiness.ps1` проверяет способности по артефактам данных, а не по
коду и не по markdown-спецификациям:

| § | Способность | Обязательные поля (сокращённо) |
|---|---|---|
| 2 | Audience Intelligence | segments, topics, retention, saves, shares, profile_visits, follows |
| 3 | Hook & Retention Lab | candidates, hook_type, selected, hold_rate, completion, rewatch |
| 4 | Pattern Memory | topic, hook, format, duration, pacing, cta, posting_time, music, cover |
| 5 | Content purpose | purpose, why_watch |
| 6 | Trend Radar | source, url, timestamp, freshness, velocity, saturation, confidence, expiry |
| 7 | Competitor Intelligence | hook, shot_structure, pace, story_structure, cta, cadence |
| 8 | Idea Scoring | 10 осей оценки идеи |
| 10 | Story Engine | hook, setup, tension, development, payoff |
| 11 | Retention Engine | retention_failure_reason, drop_off, watch_time, completion |
| 12 | Packaging | cover, first_frame, caption, cta, subtitles, music, thumbnail |
| 13 | Cadence | content_type, day, hour, reach, retention, shares, follows |
| 14 | Community Feedback | questions, objections, themes, requests |
| 15 | Follow Conversion | views, profile_visits, follows, follow_per_1000 |
| 16 | Experiment Engine | hypothesis, primary_kpi, control, challenger, sample, result, confidence, decision |
| 17 | Meta-Critic | sample_size, confounder, unknown, conclusion |
| 18 | Novelty Watch | location, outfit, camera_angle, pose, hook_type, topic, music, caption |
| 19 | Character Continuity | where, did, said, promised, outfits, interests, arcs |
| 27 | Winner Scaling | weight, saturation |
| 29 | Random Acceptance | identity, realism, story, hook, motion, voice, lip_sync, ai_tells, publishable |

Статусы:

- `PASS` — артефакт свежий и полей ≥ 80 %;
- `PARTIAL` — артефакт есть, но устарел или неполон; либо способность объявлена в коде и данных не производит;
- `FAIL` — ни данных, ни упоминания;
- `NOT_MEASURED` — формат не разобран. Это не провал и не успех.

Поля собираются объединением по нескольким свежим артефактам: веса законно лежат
в одном файле, насыщение — в другом.

---

## 4. Две проверки, которые нельзя подменить наличием файла

### Data lineage (§24)

Сквозная цепочка обязана существовать:

```
trend_id -> idea_id -> script_id -> asset_id -> reel_id -> publication_id -> analytics_id -> experiment_id
```

Без неё результат нельзя связать с решением, которое к нему привело, и любое
«этот хук лучше» остаётся догадкой. Аудит разбирает свежие записи и считает,
сколько цепочек полны.

### Learning contract (§25)

Запись засчитывается как доказанный случай обучения, только если в ней
одновременно есть все три звена:

1. опора на аналитику (`analytics_id`, метрика, наблюдение, выборка);
2. изменённая политика или вес (`policy`, `weight`, правило, порог);
3. принятое решение (`decision`, `applied`, следующее действие).

Отчёт без изменения политики обучением **не является**. Порог по умолчанию —
10 случаев, меняется параметром `-LearningCases`.

---

## 5. Порядок закрытия разрывов

Аудит выдаёт разрывы, отсортированные по приоритету метрик §26:

```
FOLLOW CONVERSION > SHARES > SAVES > RETENTION > WATCH TIME > PROFILE VISITS > REACH
```

Закрывать сверху вниз, по одному. Для каждого разрыва:

1. Посмотреть класс роли в `agent_matrix.json`.
2. `PARTIAL` / `SPEC_ONLY` → подключить существующее, нового агента не создавать.
3. `MISSING` → минимальная реализация: runner + артефакт с обязательными полями + потребитель + метрика.
4. Прогнать оба аудита заново и убедиться, что статус изменился.

Новый агент без потребителя и без метрики успеха — это будущий кандидат на retire.
Не создавать его вовсе лучше, чем создавать.

---

## 6. Эксперименты

Один эксперимент меняет **одну** вещь. Обязательные поля: `hypothesis`,
`primary_kpi`, `control`, `challenger`, `sample`, `result`, `confidence`, `decision`.

`UNKNOWN` — допустимое и частое решение. Больший охват сам по себе не означает
лучший хук: другой топик, другое время публикации, другая сила тренда и другой
состав аудитории объясняют разницу не хуже. При малой выборке решение —
`UNKNOWN`, а не победитель.

---

## 7. Границы

| Разрешено без владельца | Только владелец |
|---|---|
| Аудит, чтение, анализ | Снятие `HOST_SAFE_HOLD.flag` и `FROZEN` |
| Планирование, отбор трендов | Reboot, BIOS, драйверы |
| Эксперименты в dry-run | Секреты, деструктивные операции с БД |
| Разбор логов и метрик | Изменение политики публикации |

Аудиты не снимают флаги, не чистят `.lock`, не перезапускают сервисы и ничего
не удаляют. Исторические `FAIL` не переписываются.

---

## 8. Критерий готовности

Контур считается готовым, только когда одновременно:

- `PRODUCTION` = RUNNING и `PUBLICATION` = RUNNING (нет блокирующих флагов);
- `DATA LINEAGE` = PASS;
- `ANALYTICS -> DECISION` = PASS (не меньше 10 доказанных случаев);
- `FOLLOW CONVERSION` = MEASURED;
- `HOOK / RETENTION LOOP`, `AUDIENCE INTELLIGENCE`, `EXPERIMENT ENGINE` = PASS;
- `DEAD/DUPLICATE AGENTS` = 0.

Пока хост под `HOST_SAFE_HOLD`, первый пункт закрыт быть не может, и итоговый
вердикт честно остаётся `PARTIAL`.
