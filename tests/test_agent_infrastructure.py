"""The roles must really execute, with ownership, timeouts and retries."""

import time

import pytest

from sofia.agents.base import AgentContext, AgentResult, AgentSpec, Capability
from sofia.agents.factory import AgentFactory
from sofia.agents.ownership import OwnershipRegistry
from sofia.agents.registry import AgentRegistry, RegistryError
from sofia.agents.runner import AgentRunner, AgentTimeout
from sofia.core.errors import OwnershipError


def _spec(name, cap, impl=None, **kw):
    return AgentSpec(name=name, role=name, capabilities=(cap,), impl=impl, **kw)


def _ok(ctx):
    return AgentResult(ok=True, notes="done")


def test_duplicate_agent_name_is_rejected():
    reg = AgentRegistry()
    reg.register(_spec("a", Capability.IDEA, _ok))
    with pytest.raises(RegistryError, match="duplicate"):
        reg.register(_spec("a", Capability.HOOK, _ok))


def test_exclusive_capability_conflict_is_rejected():
    reg = AgentRegistry()
    reg.register(_spec("d1", Capability.REEL_DIRECTION, _ok))
    with pytest.raises(RegistryError, match="conflict"):
        reg.register(_spec("d2", Capability.REEL_DIRECTION, _ok))


def test_non_exclusive_capability_allows_several_providers_and_routes_deterministically():
    reg = AgentRegistry()
    reg.register(_spec("b2", Capability.IDEA, _ok))
    reg.register(_spec("b1", Capability.IDEA, _ok))
    assert {s.name for s in reg.providers(Capability.IDEA)} == {"b1", "b2"}
    # Deterministic: fewest capabilities first, then name. Never random.
    assert reg.resolve(Capability.IDEA).name == "b1"
    assert reg.resolve(Capability.IDEA).name == "b1"


def test_spec_only_agent_cannot_be_routed_to():
    reg = AgentRegistry()
    reg.register(_spec("planner", Capability.SCRIPT, impl=None))
    assert reg.spec_only() == ["planner"]
    with pytest.raises(RegistryError, match="spec-only"):
        reg.resolve(Capability.SCRIPT)


def test_audit_separates_executing_from_spec_only():
    reg = AgentRegistry()
    reg.register(_spec("real", Capability.HOOK, _ok))
    reg.register(_spec("paper", Capability.COVER, impl=None))
    audit = reg.audit((Capability.HOOK, Capability.COVER))
    assert audit.executing == ("real",)
    assert audit.spec_only == ("paper",)
    assert audit.capabilities_covered == ("reel.hook",)
    # A declared-but-unimplemented role leaves its capability uncovered.
    assert audit.capabilities_missing == ("reel.cover",)


def test_ownership_conflict(tmp_path):
    own = OwnershipRegistry(tmp_path)
    own.acquire("reel-1", "director-a")
    with pytest.raises(OwnershipError):
        own.acquire("reel-1", "director-b")


def test_owner_may_renew_its_own_lease(tmp_path):
    own = OwnershipRegistry(tmp_path)
    own.acquire("reel-1", "director-a")
    own.renew("reel-1", "director-a")
    own.assert_owner("reel-1", "director-a")


def test_stale_lease_from_a_dead_process_can_be_taken_over(tmp_path):
    own = OwnershipRegistry(tmp_path)
    # A lease recorded against a PID that does not exist, already expired.
    (tmp_path / "reel-1.lease").write_text(
        f"director-a\n{time.time() - 10_000}\n1.0\n999999\n", encoding="utf-8"
    )
    lease = own.current("reel-1")
    assert lease.stale
    own.acquire("reel-1", "director-b")
    own.assert_owner("reel-1", "director-b")


def test_runner_records_every_invocation(tmp_path):
    factory = AgentFactory(tmp_path)
    factory.add_team([_spec("worker", Capability.IDEA, _ok)])
    runner = factory.build_runner()
    factory.ownership.acquire("r1", "worker")
    runner.run(Capability.IDEA, AgentContext("r1", "worker", str(tmp_path)))
    assert runner.executed_agents() == ["worker"]
    assert runner.stats()["invocations"] == 1
    assert (tmp_path / "logs" / "agent_execution.jsonl").exists()


def test_runner_enforces_ownership(tmp_path):
    factory = AgentFactory(tmp_path)
    factory.add_team([_spec("worker", Capability.IDEA, _ok)])
    runner = factory.build_runner()
    factory.ownership.acquire("r1", "someone-else")
    with pytest.raises(OwnershipError):
        runner.run(Capability.IDEA, AgentContext("r1", "worker", str(tmp_path)))


def test_runner_retries_then_succeeds(tmp_path):
    calls = {"n": 0}

    def flaky(ctx):
        calls["n"] += 1
        return AgentResult(ok=calls["n"] >= 2, notes=f"attempt {calls['n']}")

    factory = AgentFactory(tmp_path)
    factory.add_team([_spec("flaky", Capability.IDEA, flaky, max_attempts=3)])
    runner = factory.build_runner()
    factory.ownership.acquire("r1", "flaky")
    result = runner.run(Capability.IDEA, AgentContext("r1", "flaky", str(tmp_path)))
    assert result.ok and calls["n"] == 2
    assert runner.stats()["invocations"] == 2


def test_runner_enforces_timeouts(tmp_path):
    def slow(ctx):
        time.sleep(0.4)
        return AgentResult(ok=True)

    factory = AgentFactory(tmp_path)
    factory.add_team([_spec("slow", Capability.IDEA, slow, timeout_s=0.1)])
    runner = factory.build_runner()
    factory.ownership.acquire("r1", "slow")
    with pytest.raises(AgentTimeout):
        runner.run(Capability.IDEA, AgentContext("r1", "slow", str(tmp_path)))
    assert runner.stats()["failures"] == 1


def test_agent_returning_the_wrong_type_fails_loudly(tmp_path):
    factory = AgentFactory(tmp_path)
    factory.add_team([_spec("bad", Capability.IDEA, lambda ctx: "nope")])
    runner = factory.build_runner()
    factory.ownership.acquire("r1", "bad")
    with pytest.raises(Exception):
        runner.run(Capability.IDEA, AgentContext("r1", "bad", str(tmp_path)))


def test_a_corrupt_lease_is_not_read_as_an_unowned_task(tmp_path):
    """Answering "nobody owns this" on damaged input invites a second director.

    A lease truncated by a hard reset used to parse as ``None``, which is the
    same answer as "free" — so the next process would take the Reel over while
    the original owner was still working on it.
    """
    own = OwnershipRegistry(tmp_path)
    own.acquire("r1", "director-a")

    path = tmp_path / "r1.lease"
    path.write_text(path.read_text(encoding="utf-8")[:6], encoding="utf-8")

    with pytest.raises(OwnershipError):
        own.current("r1")
    with pytest.raises(OwnershipError):
        own.acquire("r1", "director-b")


def test_a_released_lease_is_still_free(tmp_path):
    """Release truncates to empty (NO-DELETE); that stays a clean hand-back."""
    own = OwnershipRegistry(tmp_path)
    own.acquire("r1", "director-a")
    own.release("r1", "director-a")

    assert own.current("r1") is None
    assert own.acquire("r1", "director-b").owner == "director-b"
