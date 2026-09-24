"""The logical-agent contract.

A "role" in this studio is not a YAML file. It is a callable registered with a
capability set and executed by :mod:`sofia.agents.runner`, which enforces
timeouts, retries and task ownership. Several roles may be carried by one
process — what matters is that the role is *actually invoked* and leaves an
execution record.
"""

from __future__ import annotations

import enum
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Optional, Protocol, Sequence


class Capability(str, enum.Enum):
    """What an agent is allowed to do.

    Capabilities are used for routing *and* for conflict detection: two agents
    claiming the same exclusive capability is a registry error, not a silent
    last-one-wins.
    """

    # Voice team
    VOICE_DIRECTION = "voice.direction"
    VOICE_GENERATION = "voice.generation"
    VOICE_PRONUNCIATION_QA = "voice.qa.pronunciation"
    VOICE_IDENTITY_QA = "voice.qa.identity"
    VOICE_PROSODY_QA = "voice.qa.prosody"
    VOICE_SEMANTIC_QA = "voice.qa.semantic"
    VOICE_REPAIR = "voice.repair"

    # Reel team
    REEL_DIRECTION = "reel.direction"
    TREND_RESEARCH = "reel.trend"
    IDEA = "reel.idea"
    HOOK = "reel.hook"
    SCRIPT = "reel.script"
    STORYBOARD = "reel.storyboard"
    SHOT_DIRECTION = "reel.shots"
    VIDEO_GENERATION = "reel.video"
    LIPSYNC = "reel.lipsync"
    EDIT = "reel.edit"
    SUBTITLES = "reel.subtitles"
    MUSIC_SFX = "reel.music_sfx"
    COVER = "reel.cover"
    REEL_QA = "reel.qa"
    FINAL_GATE = "reel.final_gate"
    REPAIR_ROUTING = "reel.repair"
    GROWTH_INPUT = "reel.growth"


#: Capabilities that exactly one agent may hold. A second claim is a conflict.
EXCLUSIVE_CAPABILITIES: frozenset[Capability] = frozenset(
    {
        Capability.REEL_DIRECTION,
        Capability.FINAL_GATE,
        Capability.VOICE_DIRECTION,
        Capability.REPAIR_ROUTING,
    }
)


@dataclass(frozen=True)
class AgentContext:
    """Everything an agent may read while executing a task."""

    reel_id: str
    owner: str
    workdir: str
    attempt: int = 1
    params: Mapping[str, Any] = field(default_factory=dict)
    artifacts: Mapping[str, str] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.params.get(key, default)


@dataclass
class AgentResult:
    """What an agent returns."""

    ok: bool
    output: Any = None
    notes: str = ""
    artifacts: dict[str, str] = field(default_factory=dict)
    measurements: list[Any] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)
    duration_s: float = 0.0

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "notes": self.notes,
            "artifacts": dict(self.artifacts),
            "duration_s": round(self.duration_s, 4),
        }


class AgentCallable(Protocol):
    """The callable behind a role."""

    def __call__(self, ctx: AgentContext) -> AgentResult:  # pragma: no cover
        ...


@dataclass
class AgentSpec:
    """Declarative description of a role plus its executable implementation.

    ``impl`` is mandatory. A spec without an implementation is a *spec-only*
    agent and the registry refuses to mark it executable — that is exactly the
    distinction reported as "AGENTS ACTUALLY EXECUTING" vs "AGENT SPECS ONLY".
    """

    name: str
    role: str
    capabilities: tuple[Capability, ...]
    impl: Optional[AgentCallable] = None
    team: str = "unassigned"
    timeout_s: float = 300.0
    max_attempts: int = 1
    requires_gpu: bool = False
    description: str = ""
    tags: tuple[str, ...] = ()

    @property
    def executable(self) -> bool:
        return callable(self.impl)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "role": self.role,
            "team": self.team,
            "capabilities": [c.value for c in self.capabilities],
            "executable": self.executable,
            "timeout_s": self.timeout_s,
            "max_attempts": self.max_attempts,
            "requires_gpu": self.requires_gpu,
            "description": self.description,
            "tags": list(self.tags),
        }


def agent(
    name: str,
    role: str,
    capabilities: Sequence[Capability],
    **kwargs: Any,
) -> Callable[[AgentCallable], AgentSpec]:
    """Decorator turning a function into an :class:`AgentSpec`."""

    def wrap(fn: AgentCallable) -> AgentSpec:
        return AgentSpec(
            name=name,
            role=role,
            capabilities=tuple(capabilities),
            impl=fn,
            description=kwargs.pop("description", (fn.__doc__ or "").strip().split("\n")[0]),
            **kwargs,
        )

    return wrap
