"""AgentRegistry — the single source of truth for who can actually run.

Gaps this closes (and only these; the rest of the architecture is untouched):

* **duplicate detection** — two agents with the same name is an error;
* **capability conflict** — two agents claiming the same *exclusive*
  capability is an error;
* **routing** — resolve a capability to the one agent that implements it;
* **spec-only vs executing** — a role with no implementation is reported as
  spec-only and can never be routed to.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, Optional, Sequence

from sofia.agents.base import EXCLUSIVE_CAPABILITIES, AgentSpec, Capability
from sofia.core.errors import SofiaError


class RegistryError(SofiaError):
    """Raised for duplicate names, capability conflicts or missing routes."""


@dataclass(frozen=True)
class RegistryAudit:
    """Snapshot of what the registry can and cannot do."""

    executing: tuple[str, ...]
    spec_only: tuple[str, ...]
    capabilities_covered: tuple[str, ...]
    capabilities_missing: tuple[str, ...]
    conflicts: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "executing": list(self.executing),
            "spec_only": list(self.spec_only),
            "capabilities_covered": list(self.capabilities_covered),
            "capabilities_missing": list(self.capabilities_missing),
            "conflicts": list(self.conflicts),
        }


class AgentRegistry:
    """Holds :class:`AgentSpec` objects and routes capabilities to them."""

    def __init__(self) -> None:
        self._agents: dict[str, AgentSpec] = {}

    # ---- registration ----------------------------------------------------
    def register(self, spec: AgentSpec, *, replace: bool = False) -> AgentSpec:
        if spec.name in self._agents and not replace:
            raise RegistryError(f"duplicate agent name: {spec.name!r}")
        if not spec.capabilities:
            raise RegistryError(f"agent {spec.name!r} declares no capabilities")
        for cap in spec.capabilities:
            if cap not in EXCLUSIVE_CAPABILITIES:
                continue
            holder = self._exclusive_holder(cap, ignoring=spec.name)
            if holder is not None:
                raise RegistryError(
                    f"capability conflict: {cap.value!r} is exclusive and already "
                    f"held by {holder!r}; {spec.name!r} may not also claim it"
                )
        self._agents[spec.name] = spec
        return spec

    def register_all(self, specs: Iterable[AgentSpec], *, replace: bool = False) -> None:
        for spec in specs:
            self.register(spec, replace=replace)

    def _exclusive_holder(self, cap: Capability, *, ignoring: str = "") -> Optional[str]:
        for name, spec in self._agents.items():
            if name == ignoring:
                continue
            if cap in spec.capabilities:
                return name
        return None

    # ---- lookup ----------------------------------------------------------
    def __contains__(self, name: object) -> bool:
        return name in self._agents

    def __iter__(self) -> Iterator[AgentSpec]:
        return iter(sorted(self._agents.values(), key=lambda s: s.name))

    def __len__(self) -> int:
        return len(self._agents)

    def get(self, name: str) -> AgentSpec:
        try:
            return self._agents[name]
        except KeyError as exc:
            raise RegistryError(f"no agent named {name!r}") from exc

    def providers(self, cap: Capability) -> list[AgentSpec]:
        return [s for s in self if cap in s.capabilities]

    def resolve(self, cap: Capability) -> AgentSpec:
        """Route a capability to exactly one executable agent."""
        providers = [s for s in self.providers(cap) if s.executable]
        if not providers:
            declared = self.providers(cap)
            if declared:
                raise RegistryError(
                    f"capability {cap.value!r} is declared by "
                    f"{[s.name for s in declared]} but none is executable "
                    "(spec-only agent cannot be routed to)"
                )
            raise RegistryError(f"no executable agent provides {cap.value!r}")
        if len(providers) > 1 and cap in EXCLUSIVE_CAPABILITIES:
            raise RegistryError(
                f"capability conflict on {cap.value!r}: {[s.name for s in providers]}"
            )
        if len(providers) > 1:
            # Deterministic routing: highest specificity first (fewest
            # capabilities), then name. Never random.
            providers.sort(key=lambda s: (len(s.capabilities), s.name))
        return providers[0]

    def team(self, team: str) -> list[AgentSpec]:
        return [s for s in self if s.team == team]

    # ---- audit -----------------------------------------------------------
    def executing(self) -> list[str]:
        return [s.name for s in self if s.executable]

    def spec_only(self) -> list[str]:
        return [s.name for s in self if not s.executable]

    def audit(self, required: Sequence[Capability] = ()) -> RegistryAudit:
        covered: list[str] = []
        missing: list[str] = []
        conflicts: list[str] = []
        for cap in required or list(Capability):
            try:
                self.resolve(cap)
                covered.append(cap.value)
            except RegistryError as exc:
                if "conflict" in str(exc):
                    conflicts.append(f"{cap.value}: {exc}")
                missing.append(cap.value)
        return RegistryAudit(
            executing=tuple(self.executing()),
            spec_only=tuple(self.spec_only()),
            capabilities_covered=tuple(covered),
            capabilities_missing=tuple(missing),
            conflicts=tuple(conflicts),
        )

    def to_dict(self) -> dict:
        return {"agents": [s.to_dict() for s in self]}
