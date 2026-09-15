"""Executable agent infrastructure: specs, registry, factory, runner, ownership."""

from sofia.agents.base import (
    EXCLUSIVE_CAPABILITIES,
    AgentContext,
    AgentResult,
    AgentSpec,
    Capability,
    agent,
)
from sofia.agents.factory import AgentFactory
from sofia.agents.ownership import Lease, OwnershipRegistry
from sofia.agents.registry import AgentRegistry, RegistryAudit, RegistryError
from sofia.agents.runner import AgentRunner, AgentTimeout, ExecutionRecord

__all__ = [
    "EXCLUSIVE_CAPABILITIES",
    "AgentContext",
    "AgentResult",
    "AgentSpec",
    "Capability",
    "agent",
    "AgentFactory",
    "AgentRegistry",
    "AgentRunner",
    "AgentTimeout",
    "ExecutionRecord",
    "Lease",
    "OwnershipRegistry",
    "RegistryAudit",
    "RegistryError",
]
