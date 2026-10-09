# Sofia AI Studio — project instructions

Отвечать владельцу по-русски.

## Skill routing

Проектные навыки лежат в `.claude/skills/` и подхватываются Claude Code автоматически. Маршрутизация по типу задачи:

| Тип задачи | Навык |
|---|---|
| Любая задача по Sofia AI Studio — читать всегда первым | `sofia-ai-studio-master` |
| Генерация, оценка, ремонт, приёмка медиа: фото, видео, аудио, липсинк, Reels, Stories, монтаж | `sofia-media-worldclass` |
| Улучшения, research, эксперименты, champion/challenger, новые возможности и агенты | `sofia-improvement-engine` |
| Сбой, GPU, VRAM, locks, scheduler, БД, секреты, мониторинг, backup/restore, инцидент | `sofia-sre-security` |
| Контент-план, идеи, хуки, сценарии, подписи, persona, continuity, арки | `sofia-content-creator` |
| Тренды, рост, подписчики, follower conversion, growth-эксперименты | `sofia-ai-studio-master` → раздел **Sofia Growth & Trend Engine** и `.claude/skills/sofia-ai-studio-master/references/growth-and-trend-engine.md` |

`sofia-ai-studio-master` — конституция: его правила безопасности, доказательств и границ автономности имеют приоритет над специализированными навыками при конфликте.

## Обязательный порядок перед значимым действием

1. Прочитать `sofia-ai-studio-master`.
2. Прочитать специализированный навык по таблице выше.
3. Проверить живое состояние: `control_flags\PUBLISHING_STATE.json`, `CODEX_FINAL_KNOWN_GOOD_STATE.json`, `CODEX_PRODUCTION_RELEASE_GATE.md`, `agent_team_v2\state\SOFIA_AGENT_TEAM_RUNTIME_STATUS.json`, `agent_team_v2\state\company_state.json`, `http://127.0.0.1:5681/api/production-state`.
4. Проверить флаги: `NO_DELETE.flag`, `PUBLISHING_DISABLED.flag`, `PUBLISH_GATE_REQUIRED.flag`, `QUALITY_GATE_REQUIRED.flag`, игровой режим, активные локи.

Порядок доверия к источникам: `RUNTIME → CODE → DB → LOGS → RAW TESTS → CURRENT_STATE → LATEST INDEPENDENT REVIEW → OLD REPORTS`.

## Жёсткие ограничения

- `NO-DELETE`: не удалять файлы и журналы, не обходить `.claude\hooks\block_delete.py`.
- Публикация fail-closed: не снимать `FROZEN`, не удалять `PUBLISHING_DISABLED.flag`, не включать автопост без отдельной явной команды владельца.
- Не трогать production pipelines без явного запроса на конкретный контур.
- Не выдавать `PREDICTED`/`AI ANALYSIS` за `REAL` метрики. Отсутствие данных — `NOT_MEASURED`, не `0`.
- Не выполнять `git push` без команды владельца.
