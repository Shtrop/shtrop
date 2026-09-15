"""Sofia AI Studio — Voice Team and Reel Production Team.

This package contains the executable agent infrastructure for two production
teams:

* :mod:`sofia.voice` — the canonical Sofia Voice team (RU / UA / EN).
* :mod:`sofia.reel` — the Reel Production Team owned by a single ReelDirector.

Design rules that are enforced by code, not by documentation:

1. **Fail-closed.** A missing or erroring critical verifier is a FAIL, never an
   advisory warning. See :mod:`sofia.core.gates`.
2. **Evidence over assertion.** The existence of a file is never a PASS. Every
   verdict carries an evidence label (see :class:`sofia.core.verdict.Evidence`).
3. **Single owner.** One Reel has exactly one logical owner (the ReelDirector)
   holding a lease. See :mod:`sofia.agents.ownership`.
4. **Resumable.** Every stage transition is checkpointed atomically so a lost
   session, GPU or render never restarts the Reel from zero.
"""

__version__ = "0.1.0"

__all__ = ["__version__"]
