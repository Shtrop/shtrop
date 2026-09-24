"""Writes that survive losing power halfway through.

The studio host has been rebooting without a clean shutdown (Kernel-Power 41),
and a plain ``Path.write_text`` truncates the file *before* the new bytes land.
Lose power in that window and the old content is gone while the new content was
never written — the file that remains is neither. For a render that only costs
GPU time; for the publication history it is unrecoverable data loss, which the
NO-DELETE policy exists to prevent.

Everything here writes to a temporary file in the destination directory, flushes
it to disk, and then renames it over the target. ``os.replace`` is atomic within
a filesystem, so a reader either sees the whole previous version or the whole
new one, never a splice of the two.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any


def atomic_write_text(path: str | Path, text: str, *, encoding: str = "utf-8") -> Path:
    """Replace ``path`` with ``text`` in one indivisible step."""

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(p.parent), prefix=".tmp-", suffix=p.suffix)
    try:
        with os.fdopen(fd, "w", encoding=encoding) as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, p)
    except BaseException:
        # A leftover temp file would be mistaken for an artifact on the next
        # resume, so it goes even when the failure is an interrupt.
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    return p


def atomic_write_json(
    path: str | Path,
    data: Any,
    *,
    indent: int = 2,
    sort_keys: bool = False,
) -> Path:
    """Serialise ``data`` first, then write it atomically.

    Serialising up front matters: an object that cannot be encoded raises here,
    with the previous file still intact, instead of after it has been truncated.
    """

    text = json.dumps(data, ensure_ascii=False, indent=indent, sort_keys=sort_keys)
    return atomic_write_text(path, text)
