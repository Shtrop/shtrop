"""Path-component sanitisation.

Identifiers such as a reel id reach the filesystem from a CLI flag today, but
the moment anything else supplies one — a job queue, a watched folder, a web
UI — an unsanitised component is a path-traversal bug. Sanitising at the point
of use costs nothing and does not depend on knowing who the caller will be
tomorrow, so every component goes through here.
"""

from __future__ import annotations

_ALLOWED_EXTRA = "-_."


def safe_component(name: str, *, fallback: str = "unnamed") -> str:
    """Reduce ``name`` to a single safe path component.

    Keeps alphanumerics plus ``-``, ``_`` and ``.``; everything else becomes an
    underscore. Separators and parent references cannot survive, so the result
    can never escape the directory it is joined to.
    """

    cleaned = "".join(c if c.isalnum() or c in _ALLOWED_EXTRA else "_" for c in name)
    # A component of dots would still be a traversal ("..", "."), and an empty
    # one would silently collapse into its parent directory.
    if not cleaned or set(cleaned) <= {"."}:
        return fallback
    return cleaned
