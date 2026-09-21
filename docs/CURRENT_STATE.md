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
| Atomic checkpoint + resume | `PASS` | `sofia/core/checkpoint.py`; survives a host killed mid-write |
| AgentRegistry / Factory / Runner / ownership | `PASS` | 25 agents registered, 0 spec-only, 0 capability gaps |
| Voice Team (7 roles) | `PASS` (wiring) | `sofia/voice/`, 27 tests |
| Reel Production Team (17 roles) | `PASS` (wiring) | `sofia/reel/`, 41 tests |
| Growth Engine connection | `PASS` | `sofia/reel/growth.py` |
| GPU priority arbiter | `PASS` | light work proceeds, heavy work waits |
| Repair router | `PASS` | every defect maps to a component + resume point |
| Publishing HOLD | `PASS` | no publish path exists; asserted by test |
| Voice campaign harness | `PASS` | 66 clips (22 × RU/UA/EN) ran end to end in 30 s |
| Reel batch harness | `PASS` | 5 controlled + 5 random ran in 160 s |
| Readiness preflight | `PASS` | `scripts/preflight.py` names 10 blockers here |
| Cross-language identity check | `PASS` (wiring) | RU↔UA, RU↔EN, UA↔EN run in the campaign |
| Champion vs Challenger trial | `PASS` | identity regression sinks a challenger; nothing auto-promotes |
| Growth feedback loop | `PASS` | director reports every Reel; shadow stays out of REAL |
| Editing QA | `PASS` | 12 real measurements on the delivered file, not the plan |
| Cover composition QA | `PASS` | 9 real measurements; a black or horizontal cover now FAILs |
| SFX handling | `PASS` | optional by design, but a declared cue is verified |
| CI | `PASS` | `.github/workflows/tests.yml` runs suite + registry drift check |

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
| Reel benchmark *quality* (5 controlled + 5 random) | `NOT_MEASURED` | harness ran; 0/10 runs had every critical category measured |
| Voice campaign *quality* (66 clips) | `NOT_MEASURED` | harness ran; 0/66 clips had WER and identity measured |
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

## Benchmark harnesses (run, but nothing measurable here)

Both harnesses were executed at full scale on this machine to prove the
machinery, not to claim quality.

**Voice campaign** — 22 clips × RU/UA/EN = 66 clips, 30 s wall.
Verdict `NOT_MEASURED` for every language: 0/22 clips had both WER and identity
measured, because there is no ASR and no voiceprint. `mean_wer` and
`mean_identity` are `null`. Prosody *was* genuinely measured on all 66 clips
(durations 0.55 s – 12.72 s), and the repair loop ran its two rounds per clip.

**Reel batch** — 5 controlled (one plan repeated) + 5 random (sampled from a
3-plan pool), 160 s wall, mean 16.0 s per Reel, wall-time spread 15.4–17.5 s on
identical input. All 10 produced a real final file. Verdict `NOT_MEASURED`:
0/10 runs had every critical category measured. Blocker histogram — `reel.video`,
`reel.voice`, `reel.lipsync`, `reel.subtitles`, `reel.cover` and
`reel.perceptual` blocked on all 10. Estimated GPU cost 739 s/Reel, peak VRAM
24 GB (both `PREDICTED` from the shot plan, not observed — there is no GPU here).

A late honesty fix matters here: both harnesses originally reported
`first_pass_rate: 0%` when *nothing had been measured*, which reads as "the
voice is bad" rather than "there was no instrument". A rate is now reported
only when the critical verifiers actually ran on enough clips or runs;
otherwise the verdict is `NOT_MEASURED` and every rate is `null`.

## Running this on the studio machine

1. `cp config/studio.example.json config/studio.json` and fill in real paths.
2. `python scripts/preflight.py --config config/studio.json` — exits non-zero
   until every verifier is present. On this container it names 10 blockers.
3. `python scripts/run_voice_benchmark.py --workdir <dir> --config config/studio.json`
4. `python scripts/run_reel_batch.py --workdir <dir> --config config/studio.json`

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
5. **Benchmarks reported `0%` for unmeasured runs.** A pass rate was computed
   whenever enough clips existed, even if no verifier had run — so an absent
   instrument read as a quality result. Rates now require the verifiers to have
   produced numbers; otherwise `NOT_MEASURED` and `null`.
6. **The editor reported ffmpeg missing when a usable binary existed.** It only
   consulted `PATH`, ignoring an installed `imageio-ffmpeg`. Fixed.

A review pass over the new code found nine more, all fixed with regression
tests:

7. **Challengers were indistinguishable.** Arms were named from the backend's
   own `name`, which is the same hardcoded string for every challenger sharing
   a runner class, so trial output could not be attributed. Arms are now named
   by the key they were registered under.
8. **A retried Reel counted as several Reels** in growth memory, skewing every
   shadow statistic. One Reel is now one entry with an `attempts` count, and
   diagnostic runs are flagged separately.
9. **A crashed champion produced a cherry-picked baseline** that would unfairly
   sink a genuinely better challenger. Now `NOT_MEASURED`.
10. **Cross-language identity demanded reference audio** it never reads — the
    comparison is against a voiceprint — turning comparable pairs into false
    `NOT_MEASURED`.
11. **`--languages ru` could never exit zero**, because the run was judged
    against pairs that had no clips.
12. **The per-pair summary printed the first clip's verdict**, so it could show
    `RU-UA PASS` under a `FAIL` header. It now shows the worst per pair.
13. **Shadow memory was write-only** — never saved, never reloaded, never read
    by the next decision. Now persisted separately from REAL records and used
    as a hook hypothesis.
14. **The challenger trial's audio lookup used int keys** while `ReelAssets`
    stores voice clips under string keys, which would have silently produced an
    empty trial.
15. **Growth bookkeeping failures were swallowed silently**, making a broken
    analytics sink look like a studio that produced nothing. They are recorded
    and surfaced in `director.status()`.

## Resume is safe against an interrupted host

The owner's studio machine reported `GOVERNOR [CRITICAL] host_unstable_safe_hold
— Kernel-Power 41` on 2026-09-19: the host loses power mid-operation. That is a
hardware fault on their side, unrelated to this branch, but it names a failure
mode this code had to survive and did not.

Resume decided a piece of work was finished if its file **existed and was not
empty**. A run killed mid-write leaves exactly that. Measured on real artifacts:

- **MP4** — any truncation makes the file undecodable (`moov atom not found`),
  yet it is present and large, so resume reused it. A Reel would be assembled
  from a fragment.
- **WAV** — worse, because it fails *silently*: the RIFF header still declares
  the original length, so a 2%-truncated voice clip decoded to 0.43 s instead
  of 21.5 s with no error at all. At 1% truncation the duration looks almost
  right and nothing downstream would notice.

`sofia/core/artifacts.py` now answers "is this complete", not "is this
present": a WAV must contain every frame its header declares, a PPM must hold a
full pixel buffer, and a video must decode to a non-zero duration with a video
stream. An artifact that cannot be verified at all is treated as unusable
rather than as good. `analyse_wav` validates too, so a truncated clip is caught
by the critics and not only on resume.

The same audit found a second defect: **an interrupted append destroyed the
whole stage journal.** Appends are the only writer, so a power loss can tear
only the last line — but `json.loads` on that fragment raised and took the
entire history with it. The journal is preserved evidence under NO-DELETE, and
losing all of it because one append was cut is worse than losing the cut entry.
A torn tail is now tolerated and *reported* (`journal_integrity`, surfaced in
`director.status()`), while corruption anywhere other than the tail still
raises, because nothing in normal operation can produce that.

One hypothesis from the same audit did **not** hold and was deliberately not
"fixed": lease staleness uses a PID, and a hard reset can let the OS reuse it,
so a dead holder can look alive. In this design the director always claims
under the same owner name, so it reclaims its own Reel after a reboot; only a
*different* owner is refused, which is the intended "one Reel, one owner" rule.
The logic is imprecise but causes no real failure, so it was left alone rather
than padded with boot-id detection.

## Security review

An independent review pass over the whole branch found **no HIGH or MEDIUM
vulnerabilities**. The pipeline adds no network listener, no auth surface, no
crypto, and no unsafe deserialization: there is no `pickle`, `yaml`, `eval`,
`exec` or `shell=True` anywhere, all state loading is `json.loads`, and every
subprocess call passes an argv list.

It did identify two latent gaps — not reachable from an untrusted input today,
because every identifier comes from a CLI flag or the operator's own config,
but live the moment anything else supplies one (a job queue, a watched folder,
a web UI). Both are now fixed rather than deferred:

- **`reel_id` reached nine filesystem paths unsanitised**, even though this
  branch's own `checkpoint.py` and `ownership.py` already ran it through a
  sanitiser. All three now share `sofia/core/paths.safe_component`, so
  `--reel-id ../../escaped` writes `.._.._escaped.mp4` **inside** the workdir
  instead of escaping it. Verified end to end.
- **ffmpeg argument construction was under-escaped.** The concat list wrote
  `file '<path>'` with no quote escaping — and a concat list is a script, so a
  quote in a filename could rewrite it. Quotes now use the format's own
  escape and a newline is refused outright. The filter escaper handled only
  `:` and `'`, missing `,` `;` `[` `]`, which separate filters and delimit pad
  labels in a filtergraph.

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
