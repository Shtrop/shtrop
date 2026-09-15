"""AgentRunner — the execution infrastructure.

Roles are proven to run because they run *through here*: every invocation is
timed, bounded by a timeout, retried per policy, ownership-checked and written
to an execution log that the final report reads back.
"""

from __future__ import annotations

import json
import signal
import threading
import time
import traceback
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator, Mapping, Optional

from sofia.agents.base import AgentContext, AgentResult, AgentSpec, Capability
from sofia.agents.ownership import OwnershipRegistry
from sofia.agents.registry import AgentRegistry, RegistryError
from sofia.core.errors import OwnershipError, SofiaError


class AgentTimeout(SofiaError):
    """Raised when an agent exceeds its declared timeout."""


@dataclass
class ExecutionRecord:
    """One proven invocation of a role."""

    agent: str
    role: str
    capability: str
    reel_id: str
    owner: str
    attempt: int
    ok: bool
    duration_s: float
    started_at: float
    notes: str = ""
    error: str = ""
    artifacts: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "agent": self.agent,
            "role": self.role,
            "capability": self.capability,
            "reel_id": self.reel_id,
            "owner": self.owner,
            "attempt": self.attempt,
            "ok": self.ok,
            "duration_s": round(self.duration_s, 4),
            "started_at": self.started_at,
            "notes": self.notes,
            "error": self.error,
            "artifacts": dict(self.artifacts),
        }


@contextmanager
def _deadline(seconds: Optional[float]) -> Iterator[None]:
    """Best-effort wall-clock timeout.

    Uses SIGALRM on the main thread (real interruption); elsewhere falls back to
    post-hoc elapsed checking, which the runner converts into a timeout error.
    """

    if not seconds or seconds <= 0:
        yield
        return
    is_main = threading.current_thread() is threading.main_thread()
    if not is_main or not hasattr(signal, "SIGALRM"):
        yield
        return

    def _handler(signum, frame):  # noqa: ANN001
        raise AgentTimeout(f"agent exceeded {seconds}s")

    old = signal.signal(signal.SIGALRM, _handler)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


class AgentRunner:
    """Executes registered agents with ownership, timeout and retry."""

    def __init__(
        self,
        registry: AgentRegistry,
        ownership: Optional[OwnershipRegistry] = None,
        *,
        log_path: Optional[str | Path] = None,
        gpu_arbiter: Any = None,
    ) -> None:
        self.registry = registry
        self.ownership = ownership
        self.log_path = Path(log_path) if log_path else None
        self.gpu_arbiter = gpu_arbiter
        self.records: list[ExecutionRecord] = []

    # ---- execution -------------------------------------------------------
    def run(
        self,
        capability: Capability,
        ctx: AgentContext,
        *,
        agent_name: Optional[str] = None,
    ) -> AgentResult:
        spec = (
            self.registry.get(agent_name)
            if agent_name
            else self.registry.resolve(capability)
        )
        if not spec.executable:
            raise RegistryError(f"agent {spec.name!r} is spec-only and cannot execute")
        if self.ownership is not None and ctx.reel_id:
            self.ownership.assert_owner(ctx.reel_id, ctx.owner)
        # A caller that has already performed a backend-aware GPU check passes
        # gpu_cleared, so the same work is not gated twice (a CPU-only renderer
        # must not queue behind a production GPU render).
        if (
            spec.requires_gpu
            and self.gpu_arbiter is not None
            and not ctx.get("gpu_cleared", False)
        ):
            try:
                self.gpu_arbiter.require(spec.name, ctx.reel_id)
            except Exception as exc:  # noqa: BLE001 - denial is recorded, then raised
                self._append(
                    ExecutionRecord(
                        agent=spec.name,
                        role=spec.role,
                        capability=capability.value,
                        reel_id=ctx.reel_id,
                        owner=ctx.owner,
                        attempt=0,
                        ok=False,
                        duration_s=0.0,
                        started_at=time.time(),
                        notes="not started: GPU arbiter denied",
                        error=f"{type(exc).__name__}: {exc}",
                    )
                )
                raise

        last_error: Optional[BaseException] = None
        for attempt in range(1, max(1, spec.max_attempts) + 1):
            attempt_ctx = AgentContext(
                reel_id=ctx.reel_id,
                owner=ctx.owner,
                workdir=ctx.workdir,
                attempt=attempt,
                params=ctx.params,
                artifacts=ctx.artifacts,
            )
            started = time.time()
            monotonic = time.monotonic()
            try:
                with _deadline(spec.timeout_s):
                    result = spec.impl(attempt_ctx)  # type: ignore[misc]
                elapsed = time.monotonic() - monotonic
                if spec.timeout_s and elapsed > spec.timeout_s:
                    raise AgentTimeout(
                        f"agent {spec.name!r} took {elapsed:.2f}s > {spec.timeout_s}s"
                    )
                if not isinstance(result, AgentResult):
                    raise SofiaError(
                        f"agent {spec.name!r} returned {type(result).__name__}, "
                        "expected AgentResult"
                    )
                result.duration_s = elapsed
                result.started_at = started
                self._record(spec, capability, attempt_ctx, result, elapsed, started)
                if result.ok or attempt >= spec.max_attempts:
                    return result
                last_error = SofiaError(result.notes or "agent reported failure")
            except BaseException as exc:  # noqa: BLE001 - recorded, then re-raised
                elapsed = time.monotonic() - monotonic
                last_error = exc
                self._record_error(spec, capability, attempt_ctx, exc, elapsed, started)
                if isinstance(exc, (OwnershipError, KeyboardInterrupt, SystemExit)):
                    raise
                if attempt >= spec.max_attempts:
                    raise
        if last_error is not None:
            raise last_error
        raise SofiaError(f"agent {spec.name!r} produced no result")

    def try_run(
        self, capability: Capability, ctx: AgentContext, **kwargs: Any
    ) -> AgentResult:
        """Like :meth:`run` but converts an exception into a failed result.

        Used only where a *non-critical* step may degrade. Critical gates never
        use this path.
        """
        try:
            return self.run(capability, ctx, **kwargs)
        except BaseException as exc:  # noqa: BLE001
            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                raise
            return AgentResult(ok=False, notes=f"{type(exc).__name__}: {exc}")

    # ---- records ---------------------------------------------------------
    def _record(
        self,
        spec: AgentSpec,
        capability: Capability,
        ctx: AgentContext,
        result: AgentResult,
        elapsed: float,
        started: float,
    ) -> None:
        rec = ExecutionRecord(
            agent=spec.name,
            role=spec.role,
            capability=capability.value,
            reel_id=ctx.reel_id,
            owner=ctx.owner,
            attempt=ctx.attempt,
            ok=result.ok,
            duration_s=elapsed,
            started_at=started,
            notes=result.notes,
            artifacts=dict(result.artifacts),
        )
        self._append(rec)

    def _record_error(
        self,
        spec: AgentSpec,
        capability: Capability,
        ctx: AgentContext,
        exc: BaseException,
        elapsed: float,
        started: float,
    ) -> None:
        rec = ExecutionRecord(
            agent=spec.name,
            role=spec.role,
            capability=capability.value,
            reel_id=ctx.reel_id,
            owner=ctx.owner,
            attempt=ctx.attempt,
            ok=False,
            duration_s=elapsed,
            started_at=started,
            error=f"{type(exc).__name__}: {exc}",
            notes=traceback.format_exc(limit=4),
        )
        self._append(rec)

    def _append(self, rec: ExecutionRecord) -> None:
        self.records.append(rec)
        if self.log_path is not None:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec.to_dict(), ensure_ascii=False) + "\n")

    def executed_agents(self) -> list[str]:
        """Agents that were genuinely invoked at least once."""
        seen: dict[str, None] = {}
        for rec in self.records:
            seen.setdefault(rec.agent, None)
        return list(seen)

    def stats(self) -> Mapping[str, Any]:
        return {
            "invocations": len(self.records),
            "agents": len(self.executed_agents()),
            "failures": sum(1 for r in self.records if not r.ok),
            "total_s": round(sum(r.duration_s for r in self.records), 3),
        }
