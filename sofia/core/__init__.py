"""Core primitives shared by every Sofia team: verdicts, gates, checkpoints."""

from sofia.core.verdict import Evidence, Verdict, Measurement
from sofia.core.gates import Gate, GateResult, GateReport, evaluate_gates
from sofia.core.checkpoint import CheckpointStore, StageState
from sofia.core.errors import SofiaError, OwnershipError, GateError

__all__ = [
    "Evidence",
    "Verdict",
    "Measurement",
    "Gate",
    "GateResult",
    "GateReport",
    "evaluate_gates",
    "CheckpointStore",
    "StageState",
    "SofiaError",
    "OwnershipError",
    "GateError",
]
