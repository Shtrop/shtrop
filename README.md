# shtrop

Два независимых набора в одном репозитории. Они не пересекаются по коду и
запускаются в разных местах:

| Что | Где | Запускается |
|---|---|---|
| Диагностика инцидента `host_unstable_safe_hold` (Kernel-Power 41) | `sofia/*.ps1`, `sofia/RUNBOOK_host_safe_hold.md`, `sofia/COMMANDS.md` | на машине студии, Windows / PowerShell |
| Voice Team и Reel Production Team | пакет `sofia/` (`core/`, `agents/`, `voice/`, `reel/`, …), `docs/`, `scripts/`, `tests/` | где угодно, Python 3.11+ |

PowerShell-инструменты лежат файлами прямо в `sofia/`, Python-пакет — в
подкаталогах под ним; друг друга они не импортируют и не читают.

## sofia/ — диагностика host_unstable_safe_hold

Инструменты по инциденту Sofia AI Studio `host_unstable_safe_hold` (Kernel-Power 41).
Запускаются на машине студии; дерево студии не изменяют, кроме явно подтверждённого fix'а.

| Скрипт | Что делает | Меняет состояние |
|---|---|---|
| `diagnose_host_safe_hold.ps1` | Собирает доказательства: события 41/6008/1001, дампы, флаги, governor, GPU, корреляцию с рендерами, сервисы | Нет |
| `analyze_safehold_report.ps1` | Ставит диагноз по собранному отчёту: ранжирует гипотезы root cause и выдаёт следующий шаг | Нет |
| `watch_host_stability.ps1` | Набирает окно наблюдения (по умолчанию 24 ч) для выхода из hold | Нет |
| `analyze_minidump.ps1` | Достаёт код остановки и виновника из событий 1001 и заголовков дампов; отладчик не требуется | Нет |
| `apply_safehold_fix.ps1` | Обратимые fix'ы с файлом отката: power limit GPU, отключение сжатия памяти, исключение сбойных страниц памяти | Только с `-Confirm` |
| `check_memory_storage.ps1` | Проверка памяти и дисковой подсистемы под коды класса `memory` (`0x154` и др.): XMP/EXPO, WHEA, SMART, ошибки дисков | Нет |
| `lib_bugcheck.ps1` | Справочник bug check кодов с классификацией причины, подключается остальными | Нет |
| `get_sofia_tools.ps1` | Загружает все инструменты по SHA коммита в обход кэша CDN, показывает хэш каждого файла | Нет |

`sofia/COMMANDS.md` — шпаргалка со всеми командами.

`RUNBOOK_host_safe_hold.md` — порядок действий, пороги и критерии выхода из hold.

Ни один скрипт не снимает `HOST_SAFE_HOLD.flag`, не меняет publishing state,
не перезапускает сервисы, не трогает планировщик и ничего не удаляет.

## Voice Team & Reel Production Team

Executable agent infrastructure for two production teams:

- **[Voice Team](docs/VOICE_TEAM.md)** — one canonical Sofia voice in RU / UA / EN,
  with seven logical roles and fail-closed acceptance.
- **[Reel Production Team](docs/REEL_PRODUCTION_TEAM.md)** — a full Reel pipeline
  under a single `ReelDirector` that owns the finished Reel.

Read **[docs/CURRENT_STATE.md](docs/CURRENT_STATE.md)** first: it records what is
actually proven and what is explicitly `NOT_MEASURED`.

### Design rules enforced by code, not by documentation

1. **Fail-closed.** A critical verifier that is missing, errored or unmeasurable
   is a block, never an advisory warning. No critical gate is advisory-only.
2. **Evidence over assertion.** A file existing is not a `PASS`. Every number
   carries provenance (`REAL`, `MEASURED_LOCAL`, `PREDICTED`, `AI_ANALYSIS`,
   `NOT_MEASURED`), and `NOT_MEASURED` is never rendered as `0`.
3. **Measured on the delivered file.** A gate reads what will actually play, not
   the plan it was built from: the probed runtime, the encoded mix, the clips as
   they were placed.
4. **Single owner.** One Reel, one `ReelDirector`, one lease. A second director
   is rejected.
5. **Resumable.** Stage transitions are checkpointed atomically, so a lost
   session, GPU or render never restarts a Reel from zero.
6. **Targeted repair.** A defect regenerates the narrowest component that can
   fix it — a word, a shot, the cover — not the whole Reel, within a bounded
   round budget.
7. **Production has GPU priority.** Heavy work waits, including the
   Champion/Challenger benchmark; research, script, voice planning and editing
   decisions continue.
8. **Publishing stays on HOLD.** There is no publish path in this code. The
   best reachable state is `READY_FOR_OWNER_REVIEW`.

### Layout

```
sofia/
  core/       verdicts & evidence · fail-closed gates · atomic checkpoints
              durable writes (temp file → fsync → rename)
  agents/     capabilities · registry · factory · runner · ownership leases
  voice/      director · generator · 4 critics · repair · corpus · benchmark
  reel/       director · stages · shot routing · subtitles · audio mix
              critics & FinalGate · repair router · GPU arbiter · growth
              scorecard · backend measurement contract
  devkit/     NOT PRODUCTION — procedural media so the pipeline can be
              exercised without a GPU. Never produces Sofia.
  registry/   generated AGENT_REGISTRY.json / WORKFLOW_REGISTRY.json
scripts/      run_e2e_reel.py · export_registries.py · preflight.py
tests/        unit · integration · end-to-end · fault/resume
```

### Running

```bash
python -m pytest tests/ -q             # full suite
python scripts/export_registries.py    # regenerate the registries
python scripts/preflight.py --config config/studio.json
python scripts/preflight.py --measurement-contract
```

`preflight.py` answers the only question that matters before a production pass:
*what can this machine actually measure?* Anything it reports as missing is a
gate that will block, not a warning to note and move past. It exits non-zero
when the machine is not ready.

`--measurement-contract` prints what a video or lip-sync backend must attach to
each shot — `identity`, `face_drift`, `av_offset_ms` and the rest. Nothing in
this package writes those numbers; they come from the studio machine's models,
and a gate whose numbers never arrive is `NOT_MEASURED` and blocks.

### Benchmarks

```bash
python scripts/run_voice_benchmark.py --workdir <dir> --config config/studio.json
python scripts/run_reel_batch.py      --workdir <dir> --controlled 5 --random 5
```

The voice campaign runs 22 clips per language; the Reel batch runs a controlled
arm (one plan repeated, measuring variance) and a random arm (sampled from the
plan pool, measuring behaviour across content).

Both refuse to report a rate unless the critical verifiers actually ran. A
campaign where nothing could be measured is `NOT_MEASURED`, never `0%` — so a
missing instrument is never mistaken for a bad voice.

End-to-end, on the studio machine with real backends wired:

```bash
python scripts/run_e2e_reel.py --workdir <dir> --config config/studio.json
```

Copy [`config/studio.example.json`](config/studio.example.json) to
`config/studio.json` and fill in the real paths: XTTS endpoint, Sofia reference
clips per language, ASR and speaker-embedding models, ComfyUI workflows and the
lip-sync runner. Every field left empty makes the matching verifier report
`NOT_MEASURED`, which blocks.

Without those backends the same command blocks fail-closed, which is the
intended behaviour. To exercise the pipeline anyway on procedural media:

```bash
python scripts/run_e2e_reel.py --workdir <dir> --devkit
```

`--devkit` produces a genuinely playable MP4, real PCM audio and real subtitle
cues, but **nothing it makes is Sofia**: there is no face and no voice clone, so
every identity gate blocks and the run can never reach `PASS`.

### Requirements

Python 3.11+. The library itself uses only the standard library. `ffmpeg` is
needed for editing, and `pytest` plus `imageio-ffmpeg` for the full test suite.
