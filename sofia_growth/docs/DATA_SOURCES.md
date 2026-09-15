# Как дать Growth Engine реальные метрики

Движок посчитан и проверен, но **данные Sofia живут только на машине студии**.
Облачная сессия к ним доступа не имеет. Ниже — точный порядок действий локально.

## Шаг 1. Собрать то, что уже выгружено

Второй analytics pipeline не создаётся: скрипт читает существующие выгрузки.

```powershell
cd D:\AI_CONTENT\Sofia
python <путь>\sofia_growth\tools\ingest_insights.py `
    --studio "D:\AI_CONTENT\Sofia" `
    --out <путь>\sofia_growth\data\followers_snapshots.json `
    --account <handle>
```

Автопоиск идёт по шаблонам: `post_insights.csv`, `ig_insights.jsonl`,
`content_queue.db`, `*insights*.{csv,jsonl,db}`, `*analytics*.{db,csv,jsonl}`,
`*followers*.{csv,jsonl}`. Каталог `backups` пропускается.

Нестандартный путь добавляется явно (флаг повторяемый):

```powershell
python ingest_insights.py --source D:\Sofia_Logs\runner\insights_export.csv --source ...
```

Сначала полезно посмотреть, что найдено, ничего не записывая:

```powershell
python ingest_insights.py --studio "D:\AI_CONTENT\Sofia" --dry-run
```

### Что скрипт понимает

Имена метрик сопоставляются по словарю алиасов, включая нотацию Graph API:
`follower_count`, `accounts_reached`, `profile_views`, `shares_dm`, `saved`,
`ig_reels_avg_watch_time`, `ig_reels_video_view_total_time` и другие.
Вложенный ответ Insights (`data[].name` + `values[].value/end_time`)
разворачивается корректно — имя метрики не теряется.

Одна публикация, встречающаяся в нескольких источниках, склеивается по
`media_id` (иначе `permalink`): без этого охват и атрибуция удвоились бы.

### Чего скрипт не делает

- Не ходит в сеть, не использует токены, не публикует.
- Не пишет в canonical state студии — только в указанный `--out`.
- Не угадывает содержимое таблиц: SQLite-таблица без даты и без известных
  метрик пропускается, а не интерпретируется наугад.
- Не подставляет `0` вместо отсутствующего значения. `NULL`/`UNKNOWN` → поле
  просто не пишется и попадает в `NOT_MEASURED`.

## Шаг 2. Если account-level метрик в выгрузках нет

`followers`, `profile_visits`, `unfollows` часто отсутствуют в пост-выгрузках:
это account-level Insights. Их отдаёт **существующий** collector студии через
канонический путь аутентификации.

Порядок:

1. Найти в студии текущий collector (каталоги `analytics`, `workflows`, `agent_team_v2`)
   — тот, что уже ходит в Graph API. Новый коннектор не писать.
2. Запустить его штатной командой, чтобы он обновил свою выгрузку.
3. Повторить шаг 1 — `ingest_insights.py` подхватит обновлённый файл.

Токены остаются внутри канонического пути студии. Никуда их копировать,
передавать в чат или коммитить не нужно и нельзя.

Нужные account-level метрики (`period=day`): `follower_count`, `reach`,
`profile_views`, `follows_and_unfollows`, `views`. Медиа-метрики Reels:
`reach`, `shares`, `saved`, `likes`, `comments`, `ig_reels_avg_watch_time`,
`ig_reels_video_view_total_time`.

## Шаг 3. Посчитать KPI и обновить память

```powershell
python sofia_growth\tools\growth_kpi.py `
    --snapshots sofia_growth\data\followers_snapshots.json `
    --days 30 --summary --write-memory
```

Коды возврата: `0` — все KPI измерены, `1` — часть в `NOT_MEASURED`,
`2` — данных нет вовсе.

## Шаг 4. Пересобрать бэклог с учётом замеров

```powershell
python sofia_growth\tools\trend_radar.py --top 8
```

Радар сам подхватит `data/growth_memory.json`. Форматы с подтверждённым
результатом получают метку `REAL` и поднимаются над догадками; формат с
вердиктом `DROP` уходит вниз списка.

## Шаг 5. Убедиться, что цикл цел

```powershell
python sofia_growth\tests\run_e2e.py
```

Прогон использует синтетические данные во временном каталоге и проверяет
всю цепочку, включая fail-closed поведение без источников. Реальные файлы
в `data/` он не трогает.

## Lineage: без него атрибуции не будет

Чтобы движок мог сказать, *какой тренд* принёс подписчиков, в выгрузке
публикаций должны быть `trend_id` или `format_id` рядом с `media_id`.
Если студия их не пишет, атрибуция честно останется `NOT_MEASURED`:
угадывать связь публикации с трендом задним числом движок не будет.

Минимальный вариант — добавить эти два поля в существующий publish package
и в `content_queue.db`, чтобы они доезжали до выгрузки Insights.

## Приватность: почему снимки не коммитятся

Репозиторий `Shtrop/shtrop` сейчас **публичный**, поэтому
`sofia_growth/data/followers_snapshots.json` добавлен в `.gitignore`:
реальные метрики аккаунта не попадут в открытый доступ случайным коммитом.

Следствие: облачная сессия и еженедельный Routine **не увидят** эти данные и
будут считать KPI как `NOT_MEASURED`. Выбор за владельцем:

| Вариант | Что даёт | Цена |
|---|---|---|
| Оставить как есть | Метрики не публикуются | KPI считаются только локально |
| Сделать репозиторий приватным, убрать строку из `.gitignore` | Облачный анализ и еженедельный отчёт по реальным данным | Нужно переключить видимость репозитория |
| Коммитить агрегаты без абсолютных чисел | Компромисс | Часть KPI (baseline, вехи) останется `NOT_MEASURED` |

Решение принимает владелец. Движок работает в любом из вариантов.
