# CURRENT_STATE

_Last updated: 2026-09-15. Verdicts follow the studio convention:_
`PASS` · `WARN` · `FAIL` · `BLOCKED` · `NOT_MEASURED`.

## Where this was built, and what that limits

This repository was developed in a **remote Linux container**, not on the
studio machine. That is the single most important fact for reading every
verdict below.

| Checked | Result |
|---|---|
| Repository at session start | empty — `README.md` only, one commit |
| GPU | **absent** — no `nvidia-smi`, no `/dev/nvidia*`, no torch |
| ComfyUI / Wan2.2 | **absent** |
| XTTS | **absent** |
| Sofia LoRA / PuLID / reference clips | **absent** |
| Lip-sync champion runner | **absent** |
| ASR (whisper-family) | **absent** |
| Speaker-embedding model | **absent** |
| ffmpeg | installed during the session (`imageio-ffmpeg` 7.0.2) |
| Host | 4 vCPU, 15 GB RAM |

The real studio (`D:\AI_CONTENT\Sofia`, RTX 5090, ComfyUI, XTTS, Sofia LoRA) is
on the owner's Windows machine and was **not reachable** from here. Nothing in
this session read, changed or ran anything in the live studio. The documents
named in the request — `CURRENT_STATE`, the last Codex independent review,
`sofia_media_worldclass`, `sofia_content_creator`, `sofia_growth_engine` — do
not exist in this environment; only the `sofia-ai-studio-controller` skill was
available, and its policies were followed.

**Therefore: no Sofia voice, no Sofia face and no Sofia Reel was or could be
produced here.** Every identity gate in this repository reports
`FAIL`/`NOT_MEASURED` on this machine, which is the correct fail-closed answer,
not a defect.

## What is implemented and proven

| Component | State | Evidence |
|---|---|---|
| Fail-closed gate engine | `PASS` | `sofia/core/gates.py`, 13 tests |
| Atomic checkpoint + resume | `PASS` | `sofia/core/checkpoint.py`, 9 tests |
| AgentRegistry / Factory / Runner / ownership | `PASS` | 25 agents registered, 0 spec-only, 0 capability gaps |
| Voice Team (7 roles) | `PASS` (wiring) | `sofia/voice/`, 27 tests |
| Reel Production Team (17 roles) | `PASS` (wiring) | `sofia/reel/`, 41 tests |
| Growth Engine connection | `PASS` | `sofia/reel/growth.py` |
| GPU priority arbiter | `PASS` | light work proceeds, heavy work waits |
| Repair router | `PASS` | every defect maps to a component + resume point |
| Publishing HOLD | `PASS` | no publish path exists; asserted by test |

## What is NOT proven

| Item | State | Why |
|---|---|---|
| RU voice quality | `NOT_MEASURED` | no XTTS, no ASR, no Sofia voiceprint |
| UA Sofia clone | `NOT_MEASURED` | same, plus no Ukrainian reference clips |
| EN voice quality | `NOT_MEASURED` | same |
| Cross-language identity RU↔UA / RU↔EN | `NOT_MEASURED` | no speaker-embedding model |
| Video identity / face drift | `NOT_MEASURED` | no ComfyUI, no Sofia LoRA |
| Lip-sync quality | `NOT_MEASURED` | no champion runner on this machine |
| Cover face / brand QA | `NOT_MEASURED` | no face detector |
| Reel benchmark (5 controlled + 5 random) | `BLOCKED` | requires the studio machine |
| Any platform metric | `NOT_MEASURED` | publishing is on HOLD; no publication occurred |

These are recorded as `NOT_MEASURED`, never as `0` and never as a pass.

## First end-to-end run

Run on procedural dev media (`--devkit`), because Sofia's real generators are
not present. Command:

```
python scripts/run_e2e_reel.py --workdir <dir> --devkit
```

Outcome: **`HOLD`** — stage `HELD`. This is the honest result, not a failure of
the pipeline.

| Gate | Verdict | Basis |
|---|---|---|
| `reel.decode` | `PASS` | real 21.5 s H.264 + AAC vertical file |
| `reel.story` | `PASS` | SETUP→DEVELOPMENT→PAYOFF over 6 shots |
| `reel.edit` | `PASS` | 6 shots, hook lands in 2.8 s |
| `reel.audio_mix` | `PASS` | voice measured 12.0 dB over music, peak −9.5 dBFS |
| `reel.video` | `NOT_MEASURED` | identity never measurable without Sofia |
| `reel.voice` | `FAIL` | pronunciation, identity and semantics all unverifiable |
| `reel.lipsync` | `NOT_MEASURED` | no lip-sync model |
| `reel.subtitles` | `NOT_MEASURED` | no ASR, so text could only be compared to the script |
| `reel.cover` | `NOT_MEASURED` | no face detector |
| `reel.perceptual` | `HOLD` | reviewed; footage does not depict the scripted scenes |

10 roles executed through `AgentRunner` with per-invocation records in
`logs/agent_execution.jsonl`.

## Defects found and fixed during this session

1. **Clipping detector missed full-scale audio.** At 16-bit, a sample written
   as `0.999` quantises to `0.99896`, just under the old threshold. Fixed.
2. **Subtitles burned inside the bottom safe zone.** Burning an `.srt` lets the
   renderer invent a script resolution, so the declared margin and font size
   were scaled by an arbitrary factor. Fixed by emitting ASS with explicit
   `PlayResX/Y`. *Found by perceptual review, not by the numeric gates.*
3. **Resume re-rendered everything.** Shots were rebuilt from the plan each run
   and never rehydrated from the checkpoint. Fixed.
4. **CPU renderers queued behind the GPU.** Work was gated twice, once by the
   runner and once by the director. Fixed.

## Safety posture (unchanged by this session)

- Publishing remains **HOLD**. No publisher, limit or canonical flag was touched.
- No quality threshold was lowered.
- The VIDEO Champion was not modified; new lip-sync models (LongCat, HighSync)
  are representable only as Challengers.
- Nothing was deleted.
- No agent was created for the sake of a headcount: every registered role is
  invoked by the pipeline.

## Next step (requires the studio machine)

Run the same code on `D:\AI_CONTENT\Sofia` with real backends wired:

```
python scripts/run_e2e_reel.py --workdir D:\AI_CONTENT\Sofia\reels\e2e
```

with a config supplying XTTS endpoint, Sofia reference clips per language, a
whisper model, a speaker-embedding model, ComfyUI workflows and the lip-sync
runner. Then run `sofia.voice.benchmark.run_all` for the RU/UA/EN acceptance
campaigns. Until that happens, every quality number in this repository stays
`NOT_MEASURED`.
