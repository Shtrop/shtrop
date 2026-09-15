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

## Checkpoint and resume

Stages: `CREATED → BRIEF_DONE → SCRIPT_DONE → SHOTS_DONE → VOICE_DONE →
VIDEO_DONE → LIPSYNC_DONE → EDIT_DONE → FINAL_QA → READY_FOR_OWNER_REVIEW`.

Writes are atomic (temp → fsync → replace) and journalled; nothing is deleted.
A restarted session rehydrates finished renders from the checkpoint and does
not pay for them twice. Voice takes are reused too — reuse skips *generation*,
never *verification*.

## GPU priority

Production has priority. `GpuArbiter` reads live device state plus the studio's
own lock files; it never kills a job and never clears a lock by hand (a lock is
live unless its owning process is provably gone).

| Work class | Behaviour |
|---|---|
| `LIGHT` — research, script, planning, editing decisions | never waits |
| `VOICE` — synthesis | needs a GPU, yields to production |
| `HEAVY` — video, lip-sync, experiments | **waits** for production |

## Growth connection

The director does not invent its trend. While publishing is on HOLD the Growth
Engine works from historical analytics plus shadow planning, and everything it
returns is labelled — a shadow outcome is `PREDICTED` and never enters the
`REAL` metric stream.

## Publishing safety

`PUBLISHING_HOLD` is `True` and the best state the director can reach is
`READY_FOR_OWNER_REVIEW`. There is **no publish path in this code** — the
director has no `publish`, `post`, `upload` or `release` method, and a test
asserts it.
