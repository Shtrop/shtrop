"""Studio assembly: both teams on one execution infrastructure.

``build_studio`` wires the AgentFactory, registers the Voice Team and the Reel
Production Team, and returns everything the ReelDirector needs. It also reports
an honest readiness audit: which roles are executable, which capabilities are
covered, and which backends this machine actually has.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Optional

from sofia.agents.base import AgentContext, AgentResult, AgentSpec, Capability
from sofia.agents.factory import AgentFactory
from sofia.agents.runner import AgentRunner
from sofia.core.durable import atomic_write_json
from sofia.reel.backends import ReelBackends, detect_reel_backends
from sofia.reel.critics import ReelThresholds
from sofia.reel.director import ReelDirector, ReelDirectorConfig
from sofia.reel.gpu import GpuArbiter
from sofia.reel.growth import GrowthEngine, GrowthMemory
from sofia.reel.stages import CreativeSource, UnavailableCreative
from sofia.reel.team import build_reel_agents
from sofia.voice.backends import VoiceBackends, detect_backends
from sofia.voice.contracts import Language
from sofia.voice.critics import VoiceThresholds
from sofia.voice.pipeline import VoiceTeam, build_voice_agents

#: Capabilities both teams must cover for the studio to be considered wired.
REQUIRED_CAPABILITIES: tuple[Capability, ...] = tuple(Capability)


@dataclass
class Studio:
    """Everything wired together."""

    workdir: Path
    factory: AgentFactory
    runner: AgentRunner
    voice_team: VoiceTeam
    director: ReelDirector
    growth: GrowthEngine
    voice_backends: VoiceBackends
    reel_backends: ReelBackends
    gpu: GpuArbiter

    def audit(self) -> dict:
        """What is executable, what is spec-only, what this machine can do."""

        registry_audit = self.factory.registry.audit(REQUIRED_CAPABILITIES)
        return {
            "agents": {
                "total": len(self.factory.registry),
                "executing": list(registry_audit.executing),
                "spec_only": list(registry_audit.spec_only),
                "capabilities_covered": list(registry_audit.capabilities_covered),
                "capabilities_missing": list(registry_audit.capabilities_missing),
                "conflicts": list(registry_audit.conflicts),
            },
            "teams": {
                "voice": [s.name for s in self.factory.registry.team("voice")],
                "reel": [s.name for s in self.factory.registry.team("reel")],
            },
            "backends": {
                "voice": self.voice_backends.status(),
                "reel": self.reel_backends.status(),
            },
            "gpu": self.gpu.status(),
            "voice_readiness": self.voice_team.readiness()["languages"],
            "growth": self.growth.status(),
            "publishing": "HOLD",
        }

    def save_audit(self, path: str | Path) -> Path:
        return atomic_write_json(path, self.audit())


def build_studio(
    workdir: str | Path,
    *,
    language: Language = Language.RU,
    creative: Optional[CreativeSource] = None,
    voice_config: Optional[str | Path] = None,
    reel_config: Optional[str | Path] = None,
    growth_memory: Optional[str | Path] = None,
    sofia_references: Optional[Mapping[str, str]] = None,
    lock_dir: Optional[str | Path] = None,
    voice_backends: Optional[VoiceBackends] = None,
    reel_backends: Optional[ReelBackends] = None,
) -> Studio:
    """Assemble the studio for this machine, failing closed where it cannot run."""

    root = Path(workdir)
    root.mkdir(parents=True, exist_ok=True)

    vb = voice_backends or detect_backends(voice_config)
    rb = reel_backends or detect_reel_backends(reel_config)
    gpu = GpuArbiter(lock_dir=Path(lock_dir) if lock_dir else None)

    voice_team = VoiceTeam(vb, root, thresholds=VoiceThresholds())
    growth = GrowthEngine(
        memory=GrowthMemory.load(growth_memory) if growth_memory else GrowthMemory(),
        publishing_hold=True,
    )

    factory = AgentFactory(root)
    director = ReelDirector(
        ReelDirectorConfig(
            workdir=root,
            language=language,
            sofia_references=dict(sofia_references or {}),
        ),
        voice_team=voice_team,
        backends=rb,
        creative=creative or UnavailableCreative(),
        ownership=factory.ownership,
        gpu=gpu,
        thresholds=ReelThresholds(),
        growth=growth,
    )

    factory.add_team(build_voice_agents(voice_team))
    factory.add_team(build_reel_agents(director))
    factory.add_team([_growth_agent(growth)])
    runner = factory.build_runner(gpu_arbiter=gpu)
    director.runner = runner

    return Studio(
        workdir=root,
        factory=factory,
        runner=runner,
        voice_team=voice_team,
        director=director,
        growth=growth,
        voice_backends=vb,
        reel_backends=rb,
        gpu=gpu,
    )


def _growth_agent(growth: GrowthEngine) -> AgentSpec:
    """The Growth Engine's own executable role.

    It hands the ReelDirector TREND / TARGET KPI / AUDIENCE / HOOK HYPOTHESIS.
    While publishing is on HOLD it works from historical analytics plus shadow
    planning, and everything it returns is labelled as such.
    """

    def _run(ctx: AgentContext) -> AgentResult:
        growth_input = growth.brief_director(
            trend=ctx.get("trend", ""),
            audience=ctx.get("audience", ""),
            hook_hypothesis=ctx.get("hook_hypothesis", ""),
            target_kpi=ctx.get("target_kpi"),
        )
        return AgentResult(
            ok=bool(growth_input.trend),
            output=growth_input,
            notes=f"trend={growth_input.trend!r} evidence={growth_input.evidence}",
        )

    return AgentSpec(
        name="sofia.growth.engine",
        role="GrowthEngine",
        capabilities=(Capability.GROWTH_INPUT,),
        impl=_run,
        team="growth",
        timeout_s=300,
        description="Supplies trend, audience, KPI target and hook hypothesis.",
    )
