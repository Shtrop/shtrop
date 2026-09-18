# Передача на машину студии

Пакет промптов готов, но кадры рендерятся только там, где есть GPU, ComfyUI и Sofia LoRA/PuLID —
то есть на машине студии. Этот файл нужен сессии Claude, запущенной локально на Windows.

## Что уже сделано (облачная сессия)

- 6 сессий × 10 кадров = 60 промптов: `sessions/*.json` -> `build/<slug>/{BRIEF.md,batch.json,prompts/*.txt}`
- Раннер одной сессии: `tools/run_session.py`
- Прогон всех сессий на рабочий стол: `tools/run_all.ps1`
- Ветка: `claude/sofia-photosessions-u4c3r1` в `github.com/Shtrop/shtrop`

## Что осталось (локальная сессия)

1. **Preflight** по навыку `sofia-ai-studio-controller`: `control_flags\PUBLISHING_STATE.json`,
   `NO_DELETE.flag`, `PUBLISHING_DISABLED.flag`, активные локи, `nvidia-smi`, отсутствие активного
   `gpu_render`. Публикацию не включать, флаги не снимать.
2. **Подставить реальные параметры.** В `common/persona_lock.json` заменить
   `TODO_FROM_STUDIO_WORKFLOW` (sampler) и `TODO_FROM_PERSONA_CONFIG` (вес Sofia LoRA, вес PuLID)
   на значения из актуальных persona/config файлов студии. Затем `python tools\build_prompts.py`.
3. **Проверочный прогон** — один кадр, чтобы убедиться в идентичности лица:
   ```powershell
   powershell -ExecutionPolicy Bypass -File tools\run_all.ps1 -Sessions golden_gym -Variants 1
   ```
4. **Полный прогон** после проверки:
   ```powershell
   powershell -ExecutionPolicy Bypass -File tools\run_all.ps1
   ```
   Кадры лягут в `%USERPROFILE%\Desktop\Фотосессия\<сессия>\`, отчёт — в `run_manifest.json`.
5. **QA:** `photo_qa` + `identity_guardian` по каждому кадру, FAIL -> `photo_regen`
   (не подменять соседним кадром).
6. **Публикация не выполняется.** Только запись на диск. Публикация — отдельным решением
   владельца через Master Publish Gate.

## Готовый запрос для локальной сессии

```text
Используй навык sofia-ai-studio-controller. Задача: отрендерить готовый пакет фотосессий Sofia
и положить кадры на рабочий стол в папку «Фотосессия».

1. Preflight по навыку: PUBLISHING_STATE.json, NO_DELETE.flag, PUBLISHING_DISABLED.flag, локи,
   nvidia-smi, отсутствие активного gpu_render. Публикацию не включать.
2. Возьми пакет промптов: github.com/Shtrop/shtrop, ветка claude/sofia-photosessions-u4c3r1,
   каталог sofia/photosessions. Если клона нет — склонируй вне боевого дерева студии.
   Прочитай sofia/photosessions/HANDOFF.md и действуй по нему.
3. Замени TODO_FROM_* в common/persona_lock.json на реальные sampler, вес Sofia LoRA и PuLID
   из актуальных persona/config файлов студии, затем python tools\build_prompts.py.
4. Сначала проверочный прогон одного кадра:
   powershell -ExecutionPolicy Bypass -File tools\run_all.ps1 -Sessions golden_gym -Variants 1
   Покажи результат. Если лицо совпадает с каноном — полный прогон без -Sessions и -Variants.
   Если workflow не нашёлся автоматически, передай -Workflow <путь к API-формату>.
5. Прогони photo_qa и identity_guardian, FAIL отправь в photo_regen.
6. Ничего не публикуй. В конце дай путь к папке и отчёт: сколько кадров, сколько FAIL.
```
