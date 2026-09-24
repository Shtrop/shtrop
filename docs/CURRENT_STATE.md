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
| Fail-closed gate engine | `PASS` | `sofia/core/gates.py`, 15 tests |
| Durable state | `PASS` | every durable write goes through `sofia/core/durable.py`; checkpoint, journal and resume survive a host killed mid-write |
| AgentRegistry / Factory / Runner / ownership | `PASS` | 25 agents registered, 0 spec-only, 0 capability gaps |
| Voice Team (7 roles) | `PASS` (wiring) | `sofia/voice/`, 33 tests |
| Reel Production Team (17 roles) | `PASS` (wiring) | `sofia/reel/`, 109 tests |
| Growth Engine connection | `PASS` | `sofia/reel/growth.py` |
| GPU priority arbiter | `PASS` | light work proceeds; heavy work waits, including the Champion/Challenger trial |
| Repair router | `PASS` | every defect maps to a component + resume point, and the director re-runs it within a bounded budget |
| Publishing HOLD | `PASS` | no publish path exists; asserted by test |
| Voice campaign harness | `PASS` | 66 clips (22 × RU/UA/EN) ran end to end in 30 s |
| Reel batch harness | `PASS` | 5 controlled + 5 random ran in 160 s |
| Readiness preflight | `PASS` | `scripts/preflight.py` names 10 blockers here |
| Cross-language identity check | `PASS` (wiring) | RU↔UA, RU↔EN, UA↔EN run in the campaign |
| Champion vs Challenger trial | `PASS` | identity regression sinks a challenger; nothing auto-promotes |
| Growth feedback loop | `PASS` | director reports every Reel; shadow stays out of REAL |
| Editing QA | `PASS` | 17 real measurements, including the delivered runtime and the voice clips as placed |
| Cover composition QA | `PASS` | 9 real measurements; a black or horizontal cover now FAILs |
| SFX handling | `PASS` | optional by design, but a declared cue is verified |
| CI | `PASS` | `.github/workflows/tests.yml` runs suite + registry drift check |
| Quality scorecard | `PASS` | the 8/10 floors are enforced; `PASS` and *world-class* are separate claims |
| Backend measurement contract | `PASS` | `preflight.py --measurement-contract`; the gates and the trial read one list |

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
| World-class (every category ≥ 8/10) | `NOT_MEASURED` | hook strength and retention are audience outcomes; nothing here can measure them |

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

Following the same fault forward: **the writes themselves were not atomic.**
`Path.write_text` truncates the file before the new bytes land, so a power loss
inside that window leaves neither version. Checkpoints already wrote through a
temp-file-and-rename, but nothing else did — including
`GrowthMemory.save`, the *only* store of REAL publication records, which
NO-DELETE exists to protect. Every durable write in `sofia/` now goes through
`sofia/core/durable.py` (write to a temp file in the target directory, fsync,
`os.replace`): growth memory, ownership leases, `.ass`/`.srt` subtitle files
(libass renders a truncated one without complaining), the ffmpeg concat list
and every saved report. JSON is serialised *before* the file is touched, so an
unencodable object fails with the previous version still on disk.

Two reads of that state were fail-open and are now fail-closed:

- **A torn growth-memory file read as an empty history**, which is not "unknown
  baseline" but "zero publications" — the exact NOT_MEASURED-to-0 conversion
  the policy forbids. It now raises `GrowthMemoryError` naming the file.
- **A torn lease file read as `None`**, which is the same answer as "nobody
  owns this Reel", so a second director could take over live work. An
  unreadable lease now raises; only an empty one (how `release` hands a task
  back under NO-DELETE) still means free.

A third defect surfaced while fixing the first: `save` dropped each
publication's evidence label and `load` assumed `REAL`, so a `PREDICTED` record
came back as a REAL publication and fed a REAL baseline. The label is now
persisted and read back, and `GrowthMemory` rejects any non-REAL record in
`records` at construction — predictions belong in `shadow`.

One hypothesis from the same audit did **not** hold and was deliberately not
"fixed": lease staleness uses a PID, and a hard reset can let the OS reuse it,
so a dead holder can look alive. In this design the director always claims
under the same owner name, so it reclaims its own Reel after a reboot; only a
*different* owner is refused, which is the intended "one Reel, one owner" rule.
The logic is imprecise but causes no real failure, so it was left alone rather
than padded with boot-id detection.

## Two voices could play at once and no gate would see it

A voice clip is generated for its shot's duration, but a real text-to-speech
model returns whatever length the words take, and the prosody gate tolerates a
drift of a third. The clips are then laid on the timeline at their shots' start
times and **summed**, so a clip that overruns does not push the next one along
— it plays over it.

Nothing could detect that. It is not dead air, every word is still present in
the subtitles, and the mix level looks normal. The devkit hides it too: its
procedural voice returns exactly the requested length every time, so the
end-to-end run has never produced an overlap.

The clips are now measured as placed, from the clips themselves, and an overlap
beyond 0.05 s blocks the edit gate — as does speech running past the end of the
reel. If the placement is not reported at all, that is `NOT_MEASURED`, not a
clean timeline.

## "Ducking is verified, not assumed" was assumed

`AudioMixCritic` computed voice RMS minus music RMS over the whole programme,
from the two **input** stems. That quantity is a property of the source
material: it is identical whether the ducking step ran, failed, or was never
called, so the gate could not detect a mix where ducking never happened. And
the whole-file average hides a local defect — measured, a bed 3.5 dB *louder*
than the voice for one second of a 22-second Reel reported "voice 9.7 dB over
music, PASS".

It now measures the delivered mix: speech windows against the loudest gap
between phrases, where the bed is audible on its own. No source separation
needed, because only the *timing* comes from the voice stem. A mix with no gap
at all is `NOT_MEASURED`.

The first attempt was to cancel the voice out of the mix by least squares. It
works on synthetic mixes and does **not** survive a real ffmpeg chain: on a
measured devkit mix the residual came out three times larger than the music
stem could account for (the encoder's 4.8 ms filter delay and gain changes are
only part of it), so it could not distinguish a loud bed from a mix it had
failed to decompose. It was dropped rather than shipped with a guard that
would have had to guess.

## A challenger was not held to every metric the champion is

`REQUIRED_METRICS` in the Champion/Challenger trial carried the comment "a
challenger must be measured on every metric the champion is held to" above a
hand-maintained copy of the lip-sync gate's list. The copy had drifted: it was
missing `av_offset_ms`. A challenger with perfect mouth shapes at the wrong
time measured clean on everything the trial looked at and could be recommended
to the owner. `LOWER_IS_BETTER` still listed `av_offset_ms`, which is what a
dropped entry looks like.

Both lists now come from one contract, `sofia/reel/measurements.py`, so they
cannot drift again — and that contract closes a second gap. Nothing in this
package writes `Shot.measurements`; they come from the studio machine's models.
The names the gates expect were written down nowhere, so an integrator wiring a
real generator would have met a permanently blocked pipeline with nothing to
fix. `preflight.py --measurement-contract` now prints them, and the exported
registry carries them.

## The gates measured the plan and called it the delivery

The editing and subtitle gates reasoned from the shot list: pacing, cut rate,
hook speed, and the video duration that subtitle cues are checked against. That
is only sound while the delivered file *is* the planned programme. Nothing
checked that. A Reel that lost one shot during assembly is still inside the
allowed 15–30 s, so the decode gate passes it, the pacing numbers describe a
programme nobody will watch, and the cues are verified against a runtime the
file does not have.

The director now probes the final file once and both gates use that number. The
edit gate blocks when the delivered runtime drifts more than 0.5 s from the
plan, and `verify_cues` reports `NOT_MEASURED` when the runtime is unknown
instead of skipping the overrun check in silence — it used to accept
``video_duration_s=None`` and return a clean subtitle track.

While fixing this the editing gate's verdict order was corrected to match the
cover gate: a measured defect outranks a check that could not run. Both block
either way, but the reason the owner reads should name what is wrong rather
than what was unknown.

## A Reel could open on silence and pass the hook check

`check_pacing` enforced "the first cut lands within 3 s" — a fact about the
plan. `check_dead_time` measured the longest silence *inside* the programme,
and the pause statistics skip leading silence deliberately, because they exist
to find gaps between words. Between them, nothing knew when the hook was
actually heard: a Reel opening on two silent seconds passed both.

`AudioStats` now reports `leading_silence_s`, and the edit gate blocks when
speech starts later than 0.75 s into the delivered mix. This is the measurable
half of "hook" — whether the hook is *strong* is still an audience outcome, and
still reported as `--` in the scorecard.

## The heavy experiment did not wait for the GPU

"Production first, heavy experiments wait" was enforced for the director and
for nothing else. `run_trial`, the Champion/Challenger benchmark, is the heavy
experiment the rule was written for, and it rendered every arm over every
talking shot without consulting the arbiter at all — on the studio machine it
would have competed with a production render for the same card.

`GpuArbiter.wait_for` already existed and was called by nothing. A trial now
waits on it per shot and, when the wait times out, records that shot as a
failure rather than starting anyway; an arm with failures can never be
promoted, so a starved trial measures nothing instead of measuring badly.
`Studio.lipsync_trial` attaches the arbiter so a caller cannot forget it.

## The repair router routed nothing

Same class of defect as the two dead thresholds, found by the same scan for
declared-and-never-read fields: `ReelDirectorConfig.max_repair_rounds` promised
bounded repair rounds, and no repair round existed. The router computed a
correct decision — narrowest component, last good checkpoint, shot indices —
the director recorded it, and then held the Reel. Nothing was ever rebuilt.

`ReelDirector` now executes the decision: it re-runs only the stages the routed
component needs plus what consumes them, only for the routed shots, and asks
the same gates again. It refuses to repair an unmeasurable gate, refuses to
re-author a human's creative plan, tags each round's artifacts `.rN` so the
failed take survives, and stops at the round budget with the reason recorded.
See REEL_PRODUCTION_TEAM.md for the full table and rules.

## Two thresholds that were declared and never read

`ReelThresholds` is headed "Hard floors. Never lower one to make a Reel pass."
Two of its fields — `min_hook_score` and `min_category_score`, the brief's rule
that no critical category may score under 8/10 — were read by nothing in the
codebase. The rule was documented and unenforced.

They are enforced now, in `sofia/reel/scorecard.py`, which also separates two
claims the pipeline had been making with one word. `PASS` means every hard gate
held; *world-class* means every category scores 8+. `HOOK` and `RETENTION` have
no local instrument (hook strength and retention are audience outcomes, and
publishing is on HOLD), so they are reported as `--` and the world-class claim
comes back `NOT_MEASURED` rather than `False` — and never as `True`. A category
that was measured and fell below its floor outranks that and reports `FAIL`.

The devkit end-to-end run now prints both lines, e.g.:

```
SCORES:  STORY=8.0 IDENTITY=-- VOICE=4.0 LIPSYNC=-- EDITING=-- COVER=-- REALISM=4.0 HOOK=-- RETENTION=-- OVERALL=--
WORLD-CLASS: FAIL — below the floor: REALISM=4.0 (floor 8.0), VOICE=4.0 (floor 8.0)
```

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
