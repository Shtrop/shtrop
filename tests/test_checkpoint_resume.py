"""Checkpointing, resume and fault tolerance."""

import json

import pytest

from sofia.core.checkpoint import (
    Checkpoint,
    CheckpointStore,
    StageState,
    next_stage,
    remaining_stages,
)
from sofia.core.errors import CheckpointError


def test_resume_point_starts_at_created(tmp_path):
    store = CheckpointStore(tmp_path)
    assert store.resume_point("r1") is StageState.CREATED


def test_advance_and_resume(tmp_path):
    store = CheckpointStore(tmp_path)
    store.advance("r1", StageState.SCRIPT_DONE, "director")
    store.advance("r1", StageState.SHOTS_DONE, "director")
    assert store.resume_point("r1") is StageState.SHOTS_DONE
    assert remaining_stages(StageState.SHOTS_DONE)[0] is StageState.VOICE_DONE


def test_a_lost_session_resumes_instead_of_restarting(tmp_path):
    store = CheckpointStore(tmp_path)
    store.advance(
        "r1", StageState.VIDEO_DONE, "director", artifacts={"shot0": "/tmp/s0.mp4"}
    )
    # Simulate a brand-new process attaching to the same directory.
    reopened = CheckpointStore(tmp_path)
    cp = reopened.load("r1")
    assert cp.stage is StageState.VIDEO_DONE
    assert cp.artifact("shot0") == "/tmp/s0.mp4"
    assert reopened.resume_point("r1") is StageState.VIDEO_DONE


def test_stage_regression_is_rejected_by_default(tmp_path):
    store = CheckpointStore(tmp_path)
    store.advance("r1", StageState.EDIT_DONE, "director")
    with pytest.raises(CheckpointError):
        store.advance("r1", StageState.VOICE_DONE, "director")


def test_repair_may_roll_back_deliberately(tmp_path):
    store = CheckpointStore(tmp_path)
    store.advance("r1", StageState.EDIT_DONE, "director")
    cp = store.advance(
        "r1", StageState.VOICE_DONE, "director", allow_regression=True
    )
    assert cp.stage is StageState.VOICE_DONE


def test_another_owner_cannot_advance_the_reel(tmp_path):
    store = CheckpointStore(tmp_path)
    store.advance("r1", StageState.SCRIPT_DONE, "director-a")
    with pytest.raises(CheckpointError):
        store.advance("r1", StageState.SHOTS_DONE, "director-b")


def test_writes_are_atomic_and_journalled(tmp_path):
    store = CheckpointStore(tmp_path)
    for stage in (StageState.BRIEF_DONE, StageState.SCRIPT_DONE, StageState.SHOTS_DONE):
        store.advance("r1", stage, "director")
    journal = store.journal("r1")
    assert [j["stage"] for j in journal] == [
        "BRIEF_DONE",
        "SCRIPT_DONE",
        "SHOTS_DONE",
    ]
    # No partial temp files are left behind.
    assert not list(tmp_path.glob(".tmp-*"))


def test_corrupt_checkpoint_raises_rather_than_silently_restarting(tmp_path):
    store = CheckpointStore(tmp_path)
    store.advance("r1", StageState.SCRIPT_DONE, "director")
    (tmp_path / "r1.state.json").write_text("{not json", encoding="utf-8")
    with pytest.raises(CheckpointError):
        store.load("r1")


def test_next_stage_terminates():
    assert next_stage(StageState.FINAL_QA) is StageState.READY_FOR_OWNER_REVIEW
    assert next_stage(StageState.READY_FOR_OWNER_REVIEW) is None
