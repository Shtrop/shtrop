# Sofia AI Studio — Voice Team & Reel Production Team

Executable agent infrastructure for two production teams:

- **[Voice Team](docs/VOICE_TEAM.md)** — one canonical Sofia voice in RU / UA / EN,
  with seven logical roles and fail-closed acceptance.
- **[Reel Production Team](docs/REEL_PRODUCTION_TEAM.md)** — a full Reel pipeline
  under a single `ReelDirector` that owns the finished Reel.

Read **[docs/CURRENT_STATE.md](docs/CURRENT_STATE.md)** first: it records what is
actually proven and what is explicitly `NOT_MEASURED`.

## Design rules enforced by code, not by documentation

1. **Fail-closed.** A critical verifier that is missing, errored or unmeasurable
   is a block, never an advisory warning. No critical gate is advisory-only.
2. **Evidence over assertion.** A file existing is not a `PASS`. Every number
   carries provenance (`REAL`, `MEASURED_LOCAL`, `PREDICTED`, `AI_ANALYSIS`,
   `NOT_MEASURED`), and `NOT_MEASURED` is never rendered as `0`.
3. **Single owner.** One Reel, one `ReelDirector`, one lease. A second director
   is rejected.
4. **Resumable.** Stage transitions are checkpointed atomically, so a lost
   session, GPU or render never restarts a Reel from zero.
5. **Targeted repair.** A defect regenerates the narrowest component that can
   fix it — a word, a shot, the cover — not the whole Reel.
6. **Production has GPU priority.** Heavy work waits; research, script, voice
   planning and editing decisions continue.
7. **Publishing stays on HOLD.** There is no publish path in this code. The
   best reachable state is `READY_FOR_OWNER_REVIEW`.

## Layout

```
sofia/
  core/       verdicts & evidence · fail-closed gates · atomic checkpoints
  agents/     capabilities · registry · factory · runner · ownership leases
  voice/      director · generator · 4 critics · repair · corpus · benchmark
  reel/       director · stages · shot routing · subtitles · audio mix
              critics & FinalGate · repair router · GPU arbiter · growth
  devkit/     NOT PRODUCTION — procedural media so the pipeline can be
              exercised without a GPU. Never produces Sofia.
  registry/   generated AGENT_REGISTRY.json / WORKFLOW_REGISTRY.json
scripts/      run_e2e_reel.py · export_registries.py
tests/        unit · integration · end-to-end · fault/resume
```

## Running

```bash
python -m pytest tests/ -q             # full suite
python scripts/export_registries.py    # regenerate the registries
python scripts/preflight.py --config config/studio.json
```

`preflight.py` answers the only question that matters before a production pass:
*what can this machine actually measure?* Anything it reports as missing is a
gate that will block, not a warning to note and move past. It exits non-zero
when the machine is not ready.

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

## Requirements

Python 3.11+. The library itself uses only the standard library. `ffmpeg` is
needed for editing, and `pytest` plus `imageio-ffmpeg` for the full test suite.
