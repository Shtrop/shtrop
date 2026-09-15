"""AgentFactory — builds a wired registry + runner for a team.

The factory is deliberately thin: it collects the team's specs, registers them
(surfacing duplicates and capability conflicts), and hands back a runner. It
does not invent new architecture.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional, Sequence

from sofia.agents.base import AgentSpec, Capability
from sofia.agents.ownership import OwnershipRegistry
from sofia.agents.registry import AgentRegistry
from sofia.agents.runner import AgentRunner


class AgentFactory:
    """Assembles the execution infrastructure for one or more teams."""

    def __init__(self, workdir: str | Path) -> None:
        self.workdir = Path(workdir)
        self.workdir.mkdir(parents=True, exist_ok=True)
        self.registry = AgentRegistry()
        self.ownership = OwnershipRegistry(self.workdir / "leases")

    def add_team(self, specs: Iterable[AgentSpec], *, replace: bool = False) -> "AgentFactory":
        self.registry.register_all(specs, replace=replace)
        return self

    def build_runner(self, *, gpu_arbiter: object = None) -> AgentRunner:
        return AgentRunner(
            self.registry,
            self.ownership,
            log_path=self.workdir / "logs" / "agent_execution.jsonl",
            gpu_arbiter=gpu_arbiter,
        )

    def audit(self, required: Sequence[Capability] = ()) -> dict:
        return self.registry.audit(required).to_dict()
