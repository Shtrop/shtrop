"""Verdicts and evidence labels.

The studio policy is explicit: ``NOT_MEASURED`` must never be silently coerced
to ``0`` or to a PASS, and a model's opinion must never be presented as a
platform metric. These enums make that distinction part of the type system.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional


class Verdict(str, enum.Enum):
    """Outcome of a check, a stage or a whole artifact."""

    PASS = "PASS"
    REPAIR = "REPAIR"
    HOLD = "HOLD"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    NOT_MEASURED = "NOT_MEASURED"
    ERROR = "ERROR"
    MISSING = "MISSING"

    @property
    def is_pass(self) -> bool:
        return self is Verdict.PASS

    @property
    def blocks_release(self) -> bool:
        """Anything that is not an explicit PASS blocks release (fail-closed)."""
        return self is not Verdict.PASS


class Evidence(str, enum.Enum):
    """Provenance of a number.

    ``REAL`` is reserved for platform/API data tied to published content.
    Local QA measurements are ``MEASURED_LOCAL``. A model's judgement is
    ``AI_ANALYSIS`` or ``PREDICTED`` and can never be reported as a platform
    metric.
    """

    REAL = "REAL"
    MEASURED_LOCAL = "MEASURED_LOCAL"
    PREDICTED = "PREDICTED"
    AI_ANALYSIS = "AI_ANALYSIS"
    NOT_MEASURED = "NOT_MEASURED"

    @property
    def is_factual(self) -> bool:
        return self in (Evidence.REAL, Evidence.MEASURED_LOCAL)


@dataclass(frozen=True)
class Measurement:
    """A single measured value with its provenance.

    ``value`` is ``None`` when the metric could not be measured. Callers must
    check :attr:`measured` rather than defaulting to zero.
    """

    name: str
    value: Optional[float]
    evidence: Evidence
    unit: str = ""
    source: str = ""
    timestamp: Optional[str] = None
    detail: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.value is None and self.evidence is not Evidence.NOT_MEASURED:
            raise ValueError(
                f"measurement {self.name!r} has no value but claims evidence "
                f"{self.evidence.value}; use Evidence.NOT_MEASURED"
            )
        if self.value is not None and self.evidence is Evidence.NOT_MEASURED:
            raise ValueError(
                f"measurement {self.name!r} carries a value but is labelled "
                "NOT_MEASURED"
            )

    @property
    def measured(self) -> bool:
        return self.value is not None

    @classmethod
    def not_measured(cls, name: str, source: str = "", **detail: Any) -> "Measurement":
        return cls(
            name=name,
            value=None,
            evidence=Evidence.NOT_MEASURED,
            source=source,
            detail=detail,
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "value": self.value,
            "evidence": self.evidence.value,
            "unit": self.unit,
            "source": self.source,
            "timestamp": self.timestamp,
            "detail": dict(self.detail),
        }
