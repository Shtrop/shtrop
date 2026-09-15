"""Exception hierarchy for Sofia teams."""


class SofiaError(Exception):
    """Base class for every Sofia error."""


class OwnershipError(SofiaError):
    """Raised when an agent mutates an artifact it does not own."""


class GateError(SofiaError):
    """Raised when a gate cannot be evaluated at all.

    This is *not* swallowed into a WARN: an unevaluable critical gate is a FAIL
    (see :func:`sofia.core.gates.evaluate_gates`).
    """


class BackendUnavailableError(SofiaError):
    """Raised when a media backend (TTS, video, lip-sync) is not present.

    The caller must translate this into a critical ``ERROR`` gate result, never
    into a skip.
    """


class CheckpointError(SofiaError):
    """Raised when checkpoint state is corrupt or an illegal transition occurs."""
