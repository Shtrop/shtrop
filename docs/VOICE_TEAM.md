# Sofia Voice Team

One canonical Sofia voice in **RU**, **UA** and **EN**. Seven logical roles on
one execution infrastructure — they are agents in
[`AGENT_REGISTRY.json`](../sofia/registry/AGENT_REGISTRY.json), not separate
processes, and every one is invoked through
[`AgentRunner`](../sofia/agents/runner.py).

```
                        ┌──────────────────┐
                        │  VoiceDirector   │  language · emotion · pace
                        │                  │  tone · style · scene context
                        └────────┬─────────┘  + pronunciation lexicon
                                 │ VoiceBrief
                        ┌────────▼─────────┐
                        │  VoiceGenerator  │  the only caller of the TTS backend
                        └────────┬─────────┘  (never substitutes a fallback voice)
                                 │ VoiceArtifact (+ WAV)
        ┌────────────────┬───────┴────────┬─────────────────┐
        ▼                ▼                ▼                 ▼
┌───────────────┐ ┌─────────────┐ ┌──────────────┐ ┌───────────────┐
│ Pronunciation │ │   Identity  │ │   Prosody    │ │   Semantic    │
│    Critic     │ │   Critic    │ │   Critic     │ │   Critic      │
│ WER · stress  │ │ is it still │ │ rhythm·pause │ │ meaning must  │
│ numbers·names │ │   Sofia?    │ │ robotic vs   │ │ not change    │
│ borrowed words│ │  RU↔UA↔EN   │ │ overacted    │ │               │
└───────┬───────┘ └──────┬──────┘ └──────┬───────┘ └───────┬───────┘
        └────────────────┴───────┬───────┴─────────────────┘
                                 │ diagnoses (defect + locus)
                        ┌────────▼─────────┐
                        │ VoiceRepairAgent │  regenerates ONLY the
                        └────────┬─────────┘  word / phrase / sentence /
                                 │            prosody / language / identity
                                 └──► re-verify ──► PASS · REPAIR · HOLD · FAIL
```

## Fail-closed

A clip is `PASS` only when **every** critical gate is present and passing. Any
of these blocks, with no advisory-only exception:

| Condition | Verdict |
|---|---|
| pronunciation FAIL | `FAIL` |
| identity FAIL | `FAIL` |
| semantic verification FAIL | `FAIL` |
| a critical verifier raised | `ERROR` |
| a critical verifier never ran | `MISSING` |
| a critical verifier could not measure | `NOT_MEASURED` |

`NOT_MEASURED` is never coerced to `0` and never to a pass. The aggregation
lives in [`sofia/core/gates.py`](../sofia/core/gates.py); the required set is
`CRITICAL_VOICE_GATES`.

**A file existing is not a PASS.** `VoiceGenerator` raises if the backend
reports success but wrote no usable audio, and the artifact still has to clear
all four critics.

## Backends and what they gate

| Capability | Backend | If absent |
|---|---|---|
| synthesis | XTTS (studio) | generation `BLOCKED` |
| transcription | whisper-family CLI | pronunciation + semantic `NOT_MEASURED` → block |
| speaker identity | speaker-embedding model | identity `NOT_MEASURED` → block |
| Sofia voiceprint | reference clips per language | identity `FAIL` — *a generic fallback voice is not Sofia* |

Prosody is the exception: it is measured from decoded PCM with the standard
library alone ([`sofia/voice/audio.py`](../sofia/voice/audio.py)), so loudness,
clipping, pause structure and speech rate are real `MEASURED_LOCAL` numbers on
any machine.

## Per-language position

| | RU | UA | EN |
|---|---|---|---|
| Treated as | Champion | needs a real Ukrainian Sofia clone | separate acceptance campaign |
| Identity floor | 0.82 | 0.82 (and RU↔UA cross-check ≥ 0.78) | 0.82 (and RU↔EN cross-check) |
| Generic fallback acceptable | no | **no** | no |

### Cross-language identity

Each language matching its *own* voiceprint is not enough — three languages can
each match their own reference and still be three different people. So the
campaign also compares clips of one language against the **reference voiceprint
of another**, for RU↔UA, RU↔EN and UA↔EN.

`run_cross_language` is part of the acceptance run, not an optional extra: the
benchmark CLI reports its verdict alongside the per-language ones and only exits
zero when both are clean (a single-language run has no pair, so it is not judged
on one).

## Acceptance

Each language has a representative corpus of **22 clips** covering short /
medium / long lines, all six emotions, and the hard cases that break TTS in
practice — numbers, proper names, borrowed words, questions and lists. See
[`sofia/voice/corpus.py`](../sofia/voice/corpus.py).

`sofia.voice.benchmark.run_campaign` records `PASS / REPAIR / HOLD / FAIL /
BLOCKED` per clip. A campaign reports a rate **only** if at least 20 clips
actually reached verification and none was `BLOCKED`; otherwise the rates are
`null`, not zero.

WER is not optimised alone — a clip that clears WER but sounds robotic,
overacted or badly paced fails the prosody gate.
