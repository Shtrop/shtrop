# Sofia Reel Production Team

One Reel has exactly **one logical owner**: the `ReelDirector`. It holds the
brief, owns the lease, checkpoints every stage, routes repairs and answers for
the FinalGate verdict.

```
 Growth Engine ──► TREND · AUDIENCE · TARGET KPI · HOOK HYPOTHESIS
                          │
                 ┌────────▼──────────────────────────────────────┐
                 │              ReelDirector                     │
                 │  purpose · audience · trend · hook · arc      │
                 │  shot list · emotions · voice · continuity    │
                 │  expected KPI · single owner (lease)          │
                 └────────┬──────────────────────────────────────┘
                          │
  TrendAgent → IdeaAgent → HookAgent → ScriptAgent → StoryboardAgent
                          │
                   ShotDirector ──► source selection (face only where needed)
                          │
        ┌─────────────────┼──────────────────┐
        ▼                 ▼                  ▼
   VideoAgent         VoiceTeam         (B-roll / detail:
   (per profile)    (fail-closed)        no identity pipeline)
        │                 │
        └────► LipSyncAgent (champion; new models are Challengers only)
                          │
     EditorAgent → Music/SFX Agent → SubtitleAgent → CoverAgent
                          │
                    ReelCritic + Perceptual Review (BEST · RANDOM · FAIL)
                          │
                      FinalGate  ──► PASS → READY_FOR_OWNER_REVIEW
                          │           (publishing stays on HOLD)
                     RepairAgent ──► narrowest component, resume from
                                     the last good checkpoint
```

## Story is a requirement, not a preference

`validate_story` rejects a Reel that is one portrait plus subtitles. It
requires `SETUP → DEVELOPMENT → PAYOFF`, monotonic beats, a talking segment,
at least one B-roll or detail shot, and a described function for every scene.

## Shot types decide the pipeline

| Shot type | Identity gate | Lip-sync | Profile | VRAM |
|---|---|---|---|---|
| `FACE_CRITICAL` | strict | no | `identity_first_720p` | 22 GB |
| `TALKING` | strict | yes | `talking_720p_lipsync` | 24 GB |
| `PAYOFF` | strict | no | `payoff_720p` | 22 GB |
| `MEDIUM` | soft | no | `medium_720p` | 16 GB |
| `B_ROLL` | none | no | `broll_1080p_fast` | 12 GB |
| `DETAIL` | none | no | `detail_macro` | 10 GB |
| `TRANSITION` | none | no | editor-side | 0 GB |

Face is never demanded where it is not needed. On the reference six-shot plan
this routing saves **866 GPU-seconds** against forcing the talking pipeline
everywhere — and it removes the identity-failure surface entirely for B-roll
and detail shots. The identity threshold itself is never lowered; difficult
sources go `IDENTITY_FIRST` instead.

## FinalGate

`MP4 decode PASS != Reel PASS`. Decoding is one necessary check; these ten
categories are each critical and each fail-closed:

`reel.decode` · `reel.story` · `reel.video` · `reel.voice` · `reel.lipsync` ·
`reel.edit` · `reel.subtitles` · `reel.audio_mix` · `reel.cover` ·
`reel.perceptual`

A category that never ran is `MISSING`; one that could not be measured is
`NOT_MEASURED`. Both block.

### Perceptual review

Numbers can look fine while footage has dead eyes, a morphing face, a bad
mouth, fake motion or no story. `PerceptualReviewGate` requires that **BEST,
RANDOM and FAIL** samples were all actually looked at — reviewing only the best
results is not a review — and any flag holds the Reel.

This is not decorative. During the first end-to-end run it caught a defect the
numeric gates passed: the burned-in subtitles were rendering inside the bottom
platform-UI safe zone, because the renderer invents its own script resolution
when burning an `.srt`. Fixed by emitting ASS with explicit `PlayRes`.

## The scorecard, and what "world-class" would take

`PASS` and *world-class* are two different claims and are reported separately.
`PASS` means every hard gate held — no defect was found — and the Reel goes to
owner review. The brief's bar for world-class is stronger: every critical
category at 8/10 or better.

The 0–10 scores are derived from the gates, so they say what the gates can say:
8.0 for a category where every hard gate passed, 4.0 where one blocked, and
**`--` (null) where nothing could be measured** — never 0, which would read as
a measurement of badness.

Two categories the brief asks for have no local instrument at all:

| Category | Why it cannot be measured here |
| --- | --- |
| `HOOK` | Hook *strength* is an audience outcome. The gates check that a hook exists and is in the opening shot; whether it holds anyone is not visible without viewers. |
| `RETENTION` | Readable only from platform analytics on a published Reel, and publishing is on HOLD. |

They are listed in the scorecard as `--` rather than dropped: a scorecard that
quietly omits the two hardest numbers reads as if everything was covered.

Consequently `world_class` reports `NOT_MEASURED` — not `False` — however clean
the gates are, and says which categories are missing. A category that *was*
measured and came in under its floor outranks that: a known defect is a
stronger finding than an unknown, so the claim becomes `FAIL` and names it.
`OVERALL` still averages the locally measured categories, so it stays useful on
a real studio run.

Both floors (`min_category_score`, `min_hook_score`) live in `ReelThresholds`
and are now enforced by `sofia/reel/scorecard.py`. Until this they were
declared under the comment "Hard floors. Never lower one to make a Reel pass."
and read by nothing at all.

## Editing is measured, not assumed

`EditorAgent` is asked for a strong first frame, a fast hook, no dead time,
pacing, beat sync, ducking, safe zones, subtitles, transitions and a cover.
Ducking, safe zones, subtitles and the cover have their own critics; the rest
is measured by `sofia/reel/edit_qa.py` **from the delivered file**, not from the
plan:

| Check | How it is measured | Blocks? |
|---|---|---|
| Strong first frame | frame 0 decoded to PPM; brightness, contrast, sharpness, blown ratio | yes |
| Vertical delivery | aspect from the decoded frame | yes |
| Fast hook | opening shot ≤ 3 s, **and** speech starts within 0.75 s in the delivered mix | yes |
| Dead time | longest silence in the actual mix | yes |
| Pacing | shot count, cuts per 10 s, longest-shot share of runtime | yes |
| Delivered runtime | probed duration against the planned total (±0.5 s) | yes |
| Beat sync | cut points against the music grid | **no** — advisory |

Everything in this table except the first frame reasons from the shot list —
the *plan*. That is only sound if the file is the programme that was planned,
so the delivered runtime is probed and compared. A Reel that loses one shot in
assembly is still inside the allowed 15–30 s, so the decode gate passes it, and
every pacing number then describes a programme nobody will watch. The subtitle
gate is given the same probed runtime: cues are checked against the file that
will play, and if the runtime cannot be read the overrun check reports
`NOT_MEASURED` instead of silently passing.

"Fast hook" used to mean only "the first cut lands within 3 s", which is a
statement about the plan. The pause statistics ignore leading silence on
purpose — they exist to find gaps *between* words — so a Reel could open on two
silent seconds, the most expensive place in short form to spend them, and pass
both checks. The silence before the first word is now measured in the delivered
mix and blocks on its own.

Frame analysis is pure standard library (`sofia/reel/frames.py` reads binary
PPM), so a black or flat opener is caught on any machine, with no numpy or PIL.

Beat sync is deliberately advisory. Landing cuts on the beat is a craft signal,
not a correctness property — a reel with intentionally off-beat cuts is not
broken — so it is reported and never fails the gate. Every other check here is
hard, and a frame or mix that cannot be decoded is `NOT_MEASURED`, which blocks.

## The cover is measured too

A cover is checked in two halves, and the split is the point:

- **Composition** — exposure, contrast, sharpness, crop and how busy the band
  under the hook text is. Measured from the decoded image with the standard
  library, so it works on any machine.
- **Identity and brand** — is Sofia's face there, is it *her*, does it look like
  her channel. No honest stdlib proxy exists, so without a face model and a
  brand reference these stay `NOT_MEASURED`, which blocks.

A composition defect outranks "not measured": a black, washed-out or horizontal
cover is a **known-bad** answer and is reported as `FAIL`, not as an unknown.
Checking only the model-dependent half — as this gate originally did — let a
black cover sail through as merely unmeasured.

## SFX

SFX are optional by design; the brief asks for them only where they strengthen
a scene, so an empty list passes. But a *declared* SFX is checked: the file must
exist and must not peak above the programme ceiling. The field is either real or
it is not there — a list nothing populates and nothing verifies is decoration.

## Champion vs Challenger

A newer lip-sync model does not become champion by being newer. It enters as a
challenger, runs on the **same shots**, and is measured on the same required
metrics (`sofia/reel/challenger.py`).

A challenger is *recommended* only when it was measured on every required
metric, regressed on none, and improved at least one beyond noise. Two rules
have no exceptions:

- **Identity may never regress.** No improvement to mouth, jaw or teeth buys
  that back.
- **Nothing is promoted automatically.** A `PASS` means the owner should look.

Metrics aggregate **worst-case across shots**, not by average, so one bad take
is not smoothed away. A champion that crashed on some shots is reported as
`NOT_MEASURED` rather than being compared from a cherry-picked subset.

## Repair routing

A defect never triggers a full rebuild. Each maps to the narrowest component
and the last good checkpoint to resume from:

| Defect | Component | Resume from |
|---|---|---|
| `BAD_HOOK` / `BAD_SCRIPT` | HookAgent / ScriptAgent | `BRIEF_DONE` |
| `BAD_SOURCE` | ShotDirector | `SCRIPT_DONE` |
| `IDENTITY` / `SHOT` | VideoAgent (affected shots only) | `SHOTS_DONE` |
| `VOICE` / `PRONUNCIATION` | VoiceTeam (that clip / that word) | `SHOTS_DONE` |
| `LIPSYNC` | LipSyncAgent | `VIDEO_DONE` |
| `EDIT` | EditorAgent | `LIPSYNC_DONE` |
| `SUBTITLES` / `MUSIC` / `COVER` | respective agent | `EDIT_DONE` |
| `STORY_CONTINUITY` | ReelDirector | `BRIEF_DONE` |
| `NOT_MEASURED` | infrastructure | **not repairable** — fix the verifier |

### Repairs are executed, not only routed

The router computes the narrowest fix; `ReelDirector` now runs it. After a
blocking FinalGate the director re-runs **only** the stages the routed
component needs, plus what consumes them — a re-rendered shot is re-lip-synced
and re-cut, or the final file still carries the old take:

| Component | Stages re-run |
| --- | --- |
| `VideoAgent` | video → lipsync → edit |
| `VoiceTeam` | voice → lipsync → edit |
| `LipSyncAgent` | lipsync → edit |
| `EditorAgent` / `SubtitleAgent` / `Music/SFX` / `CoverAgent` | edit |

Only the routed shots are regenerated: every stage skips a shot whose artifact
is already usable, so clearing one shot's path is what makes it — and only it —
get paid for again.

Four rules keep this from becoming a retry loop that launders failures:

- **A repair never re-decides a verdict.** It rebuilds a component and asks the
  same gates again.
- **`NOT_MEASURED` is never repaired.** No amount of re-rendering makes a
  missing verifier appear, so an unmeasurable gate stops the loop immediately
  (`RepairDecision.full_stop`) instead of burning the round budget.
- **The creative plan is not regenerated.** `BAD_HOOK`, `BAD_SCRIPT` and
  `BAD_SOURCE` route to agents that, with an authored plan, would hand back the
  same plan; they are reported as needing a human.
- **The budget is `max_repair_rounds` (default 2), per Reel.** When it runs out
  the Reel is held for the owner and the report says so.

Each round tags its artifacts `.rN`, so a repair writes *beside* the take it
replaces. NO-DELETE covers the evidence of a failed attempt too.

A diagnostic run never repairs: it walked past blocks deliberately, so
repairing them would be chasing defects on purpose.

## Checkpoint and resume

Stages: `CREATED → BRIEF_DONE → SCRIPT_DONE → SHOTS_DONE → VOICE_DONE →
VIDEO_DONE → LIPSYNC_DONE → EDIT_DONE → FINAL_QA → READY_FOR_OWNER_REVIEW`.

Writes are atomic (temp → fsync → replace) and journalled; nothing is deleted.
A restarted session rehydrates finished renders from the checkpoint and does
not pay for them twice. Voice takes are reused too — reuse skips *generation*,
never *verification*.

**Presence is not completeness.** A host that loses power mid-write leaves a
file that exists and is not empty, and resume used to accept exactly that. Each
rehydrated artifact is now decoded before it is trusted: a WAV must contain
every frame its header declares (a truncated one otherwise decodes short and
silently), a video must decode to a non-zero duration, and anything that cannot
be verified is re-done rather than assumed good.

## GPU priority

Production has priority. `GpuArbiter` reads live device state plus the studio's
own lock files; it never kills a job and never clears a lock by hand (a lock is
live unless its owning process is provably gone).

| Work class | Behaviour |
|---|---|
| `LIGHT` — research, script, planning, editing decisions | never waits |
| `VOICE` — synthesis | needs a GPU, yields to production |
| `HEAVY` — video, lip-sync, experiments | **waits** for production |

"Experiments wait" was the half of that rule with nothing behind it.
`run_trial` — the Champion/Challenger benchmark, which is *the* heavy
experiment here — rendered every arm over every talking shot without ever
asking the arbiter. On the studio machine a benchmark would have taken the GPU
out from under a production render.

A trial now waits per shot (`GpuArbiter.wait_for`, which existed and was called
by nothing) and, if it never gets the GPU, records the shot as a failure rather
than starting anyway. An arm with failures is never promoted, so a starved
trial measures nothing instead of measuring badly. Run it through
`Studio.lipsync_trial`, which attaches the arbiter so it cannot be forgotten.

## Growth connection

The director does not invent its trend. While publishing is on HOLD the Growth
Engine works from historical analytics plus shadow planning, and everything it
returns is labelled — a shadow outcome is `PREDICTED` and never enters the
`REAL` metric stream.

The loop is closed in code: every finished Reel is reported back by the
director, so the next decision can see which hooks reached owner review and
which gates keep blocking. Guard rails on that feedback:

- `records` (REAL publications) and `shadow` (this pipeline's own outcomes) are
  separate lists and stay separate across a save/reload. A shadow entry never
  contributes to a baseline.
- One Reel is one entry. A retried or resumed Reel updates its record and
  increments `attempts` rather than counting as several Reels.
- Diagnostic runs are flagged and excluded from "reached owner review", since
  they can never pass.
- A prior winning hook is offered as a *hypothesis* only when the caller
  supplies none, and never overrides an explicit one.
- If the growth sink throws, the Reel's verdict is unchanged, but the error is
  recorded and surfaced in `director.status()` — a permanently broken analytics
  sink must not look like a studio that produced nothing.

## Publishing safety

`PUBLISHING_HOLD` is `True` and the best state the director can reach is
`READY_FOR_OWNER_REVIEW`. There is **no publish path in this code** — the
director has no `publish`, `post`, `upload` or `release` method, and a test
asserts it.
