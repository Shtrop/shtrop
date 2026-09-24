"""Fail-closed gate evaluation.

The single most important rule in the studio: a *critical* gate that is
missing, errored or not measured is a **FAIL**. It is never downgraded to an
advisory warning, and a high secondary score can never average away a hard
gate failure.
"""

from __future__ import annotations

import time
import traceback
from dataclasses import dataclass, field
from typing import Callable, Iterable, Mapping, Optional, Sequence

from sofia.core.errors import GateError
from sofia.core.verdict import Evidence, Measurement, Verdict


@dataclass(frozen=True)
class GateResult:
    """Outcome of one gate."""

    name: str
    verdict: Verdict
    critical: bool
    reason: str = ""
    measurement: Optional[Measurement] = None
    threshold: Optional[float] = None
    duration_s: float = 0.0
    detail: Mapping[str, object] = field(default_factory=dict)

    @property
    def blocking(self) -> bool:
        """True when this result must stop the artifact from passing."""
        return self.critical and self.verdict.blocks_release

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "verdict": self.verdict.value,
            "critical": self.critical,
            "reason": self.reason,
            "threshold": self.threshold,
            "duration_s": round(self.duration_s, 4),
            "measurement": self.measurement.to_dict() if self.measurement else None,
            "detail": dict(self.detail),
        }


@dataclass
class Gate:
    """A single named check.

    ``check`` returns a :class:`GateResult`, or raises. A raising critical gate
    yields ``Verdict.ERROR`` and blocks; a critical gate that was never
    registered yields ``Verdict.MISSING`` and also blocks.
    """

    name: str
    check: Callable[..., GateResult]
    critical: bool = True
    threshold: Optional[float] = None
    timeout_s: Optional[float] = None
    description: str = ""

    def run(self, *args, **kwargs) -> GateResult:
        started = time.monotonic()
        try:
            result = self.check(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001 - deliberate: any failure blocks
            return GateResult(
                name=self.name,
                verdict=Verdict.ERROR,
                critical=self.critical,
                reason=f"{type(exc).__name__}: {exc}",
                duration_s=time.monotonic() - started,
                detail={"traceback": traceback.format_exc(limit=6)},
            )
        if not isinstance(result, GateResult):
            return GateResult(
                name=self.name,
                verdict=Verdict.ERROR,
                critical=self.critical,
                reason=(
                    f"gate {self.name!r} returned {type(result).__name__}, "
                    "expected GateResult"
                ),
                duration_s=time.monotonic() - started,
            )
        elapsed = time.monotonic() - started
        if self.timeout_s is not None and elapsed > self.timeout_s:
            return GateResult(
                name=self.name,
                verdict=Verdict.ERROR,
                critical=self.critical,
                reason=f"gate exceeded timeout ({elapsed:.2f}s > {self.timeout_s}s)",
                duration_s=elapsed,
            )
        # A gate cannot lie about its own criticality or name.
        return GateResult(
            name=self.name,
            verdict=result.verdict,
            critical=self.critical,
            reason=result.reason,
            measurement=result.measurement,
            threshold=result.threshold if result.threshold is not None else self.threshold,
            duration_s=elapsed,
            detail=result.detail,
        )


@dataclass(frozen=True)
class GateReport:
    """Aggregated verdict over a set of gates."""

    verdict: Verdict
    results: Sequence[GateResult]
    blocking: Sequence[GateResult] = field(default_factory=tuple)
    missing_critical: Sequence[str] = field(default_factory=tuple)

    @property
    def passed(self) -> bool:
        return self.verdict is Verdict.PASS

    def failures(self) -> list[GateResult]:
        return [r for r in self.results if r.verdict.blocks_release]

    def by_name(self, name: str) -> Optional[GateResult]:
        for r in self.results:
            if r.name == name:
                return r
        return None

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict.value,
            "blocking": [r.name for r in self.blocking],
            "missing_critical": list(self.missing_critical),
            "results": [r.to_dict() for r in self.results],
        }


def threshold_gate(
    name: str,
    measurement: Measurement,
    minimum: float,
    *,
    critical: bool = True,
    higher_is_better: bool = True,
    advisory_reason: str = "",
) -> GateResult:
    """Build a :class:`GateResult` from a measurement and a threshold.

    ``NOT_MEASURED`` never becomes ``0`` and never becomes a PASS.
    """

    if not measurement.measured:
        return GateResult(
            name=name,
            verdict=Verdict.NOT_MEASURED,
            critical=critical,
            reason=f"{measurement.name} was not measured ({measurement.source or 'no source'})",
            measurement=measurement,
            threshold=minimum,
        )
    if measurement.evidence is Evidence.PREDICTED and critical:
        # A predicted number cannot satisfy a hard gate on its own.
        return GateResult(
            name=name,
            verdict=Verdict.HOLD,
            critical=critical,
            reason=(
                f"{measurement.name} is PREDICTED; a critical gate requires "
                "REAL or MEASURED_LOCAL evidence"
            ),
            measurement=measurement,
            threshold=minimum,
        )
    value = float(measurement.value)  # type: ignore[arg-type]
    ok = value >= minimum if higher_is_better else value <= minimum
    comparator = ">=" if higher_is_better else "<="
    return GateResult(
        name=name,
        verdict=Verdict.PASS if ok else Verdict.FAIL,
        critical=critical,
        reason=(
            f"{measurement.name}={value:.4f} {comparator} {minimum:.4f}"
            if ok
            else f"{measurement.name}={value:.4f} violates {comparator} {minimum:.4f}"
            + (f" ({advisory_reason})" if advisory_reason else "")
        ),
        measurement=measurement,
        threshold=minimum,
    )


def evaluate_gates(
    results: Iterable[GateResult],
    *,
    required_critical: Sequence[str] = (),
) -> GateReport:
    """Aggregate gate results fail-closed.

    Args:
        results: the gate results that were actually produced.
        required_critical: names of gates that **must** be present. A name that
            does not appear in ``results`` produces a synthetic
            ``Verdict.MISSING`` critical result — a missing critical verifier is
            a FAIL, not a skip.

    Returns:
        A :class:`GateReport` whose verdict is ``PASS`` only when every critical
        gate is present and passing.
    """

    collected = list(results)
    seen = {r.name for r in collected}
    missing = [name for name in required_critical if name not in seen]
    for name in missing:
        collected.append(
            GateResult(
                name=name,
                verdict=Verdict.MISSING,
                critical=True,
                reason="required critical verifier did not run",
            )
        )

    duplicates = _duplicate_names(collected)
    if duplicates:
        collected.append(
            GateResult(
                name="gate_integrity",
                verdict=Verdict.ERROR,
                critical=True,
                reason=f"duplicate gate results: {sorted(duplicates)}",
            )
        )

    blocking = [r for r in collected if r.blocking]
    if blocking:
        verdict = _worst_verdict([r.verdict for r in blocking])
    elif any(r.verdict.blocks_release for r in collected):
        # Only non-critical (advisory) problems remain.
        verdict = Verdict.PASS
    else:
        verdict = Verdict.PASS
    return GateReport(
        verdict=verdict,
        results=tuple(collected),
        blocking=tuple(blocking),
        missing_critical=tuple(missing),
    )


_SEVERITY = {
    Verdict.PASS: 0,
    Verdict.REPAIR: 1,
    Verdict.HOLD: 2,
    Verdict.NOT_MEASURED: 3,
    Verdict.BLOCKED: 4,
    Verdict.FAIL: 5,
    Verdict.MISSING: 6,
    Verdict.ERROR: 7,
}


def _worst_verdict(verdicts: Sequence[Verdict]) -> Verdict:
    if not verdicts:
        raise GateError("cannot aggregate an empty verdict set")
    return max(verdicts, key=lambda v: _SEVERITY[v])


def _duplicate_names(results: Sequence[GateResult]) -> set[str]:
    seen: set[str] = set()
    dupes: set[str] = set()
    for r in results:
        if r.name in seen:
            dupes.add(r.name)
        seen.add(r.name)
    return dupes


def worst(verdicts: Sequence[Verdict]) -> Verdict:
    """Public helper: the most severe verdict in ``verdicts``."""
    return _worst_verdict(verdicts)
