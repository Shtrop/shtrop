"""Task ownership leases.

One Reel has exactly one logical owner. A second director attempting to mutate
the same Reel is rejected with :class:`~sofia.core.errors.OwnershipError`
rather than silently interleaving writes.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from sofia.core.durable import atomic_write_text
from sofia.core.errors import OwnershipError
from sofia.core.paths import safe_component


@dataclass(frozen=True)
class Lease:
    task_id: str
    owner: str
    acquired_at: float
    ttl_s: float
    pid: int

    @property
    def expired(self) -> bool:
        return time.time() > self.acquired_at + self.ttl_s

    @property
    def holder_alive(self) -> bool:
        """Whether the process that took the lease still exists."""
        try:
            os.kill(self.pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        except OSError:
            return True
        return True

    @property
    def stale(self) -> bool:
        """A lease is stale only if it expired *and* its holder is gone."""
        return self.expired and not self.holder_alive


class OwnershipRegistry:
    """In-memory + on-disk lease table.

    Stale locks are never cleared by hand: :meth:`acquire` takes over a lease
    only when it is both expired and its holder process is gone.
    """

    def __init__(self, root: str | os.PathLike[str]) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, task_id: str) -> Path:
        return self.root / f"{safe_component(task_id)}.lease"

    def current(self, task_id: str) -> Optional[Lease]:
        """The live lease, ``None`` if the task was released or never claimed.

        A lease we cannot read is *not* reported as free. Answering "nobody owns
        this" on damaged input is how two directors end up writing the same
        Reel, so an unreadable file raises instead.
        """
        path = self._path(task_id)
        if not path.exists():
            return None
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise OwnershipError(
                f"lease file for task {task_id!r} cannot be read ({exc}); "
                "refusing to treat the task as unowned"
            ) from exc
        if not raw.strip():
            # release() truncates rather than deleting, per NO-DELETE.
            return None
        try:
            owner, acquired_at, ttl_s, pid = raw.split("\n")[:4]
            return Lease(task_id, owner, float(acquired_at), float(ttl_s), int(pid))
        except ValueError as exc:
            raise OwnershipError(
                f"lease file for task {task_id!r} is corrupt ({exc}); "
                f"{len(raw)} bytes on disk. Inspect {path} and truncate it to "
                "release the task deliberately"
            ) from exc

    def acquire(self, task_id: str, owner: str, ttl_s: float = 3600.0) -> Lease:
        existing = self.current(task_id)
        if existing is not None and existing.owner != owner and not existing.stale:
            raise OwnershipError(
                f"task {task_id!r} is owned by {existing.owner!r} "
                f"(pid {existing.pid}, {'expired' if existing.expired else 'active'}); "
                f"{owner!r} may not take it over"
            )
        lease = Lease(task_id, owner, time.time(), ttl_s, os.getpid())
        atomic_write_text(
            self._path(task_id),
            f"{lease.owner}\n{lease.acquired_at}\n{lease.ttl_s}\n{lease.pid}\n",
        )
        return lease

    def assert_owner(self, task_id: str, owner: str) -> None:
        existing = self.current(task_id)
        if existing is None:
            raise OwnershipError(f"task {task_id!r} has no owner; acquire a lease first")
        if existing.owner != owner:
            raise OwnershipError(
                f"task {task_id!r} is owned by {existing.owner!r}, not {owner!r}"
            )

    def release(self, task_id: str, owner: str) -> None:
        self.assert_owner(task_id, owner)
        # NO-DELETE policy applies to artifacts and journals, not to transient
        # lease files; a released lease is truncated rather than removed.
        atomic_write_text(self._path(task_id), "")

    def renew(self, task_id: str, owner: str, ttl_s: float = 3600.0) -> Lease:
        self.assert_owner(task_id, owner)
        return self.acquire(task_id, owner, ttl_s)
