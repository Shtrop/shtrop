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


# ---- artifact integrity after an interrupted run -------------------------
# A host that loses power mid-write leaves a file that exists and is not empty.
# Presence is not completeness, and reusing a fragment silently corrupts a Reel.


def _wav(path, seconds=1.0, rate=22050):
    import math

    from sofia.voice.audio import write_wav

    return write_wav(
        path,
        [0.2 * math.sin(2 * math.pi * 220 * i / rate) for i in range(int(rate * seconds))],
        rate,
    )


def test_a_truncated_wav_is_not_usable(tmp_path):
    from sofia.core.artifacts import is_usable

    good = _wav(tmp_path / "good.wav")
    assert is_usable(good, kind="wav")

    cut = tmp_path / "cut.wav"
    cut.write_bytes(good.read_bytes()[: int(good.stat().st_size * 0.5)])
    # It exists and is far from empty — presence alone would pass it.
    assert cut.exists() and cut.stat().st_size > 1000
    assert not is_usable(cut, kind="wav")


def test_a_barely_truncated_wav_is_still_caught(tmp_path):
    """The dangerous case: 1% missing decodes almost-right and looks fine."""
    from sofia.core.artifacts import is_usable

    good = _wav(tmp_path / "good.wav", seconds=5.0)
    cut = tmp_path / "cut.wav"
    cut.write_bytes(good.read_bytes()[: int(good.stat().st_size * 0.99)])
    assert not is_usable(cut, kind="wav")


def test_analysing_a_truncated_wav_raises_rather_than_returning_short_audio(tmp_path):
    """wave trusts the header, so a cut file otherwise decodes silently."""
    import pytest

    from sofia.core.artifacts import ArtifactInvalid
    from sofia.voice.audio import analyse_wav

    good = _wav(tmp_path / "good.wav", seconds=4.0)
    cut = tmp_path / "cut.wav"
    cut.write_bytes(good.read_bytes()[: int(good.stat().st_size * 0.25)])
    with pytest.raises(ArtifactInvalid):
        analyse_wav(cut)


def test_a_truncated_ppm_is_not_usable(tmp_path):
    from sofia.core.artifacts import is_usable

    width, height = 20, 20
    full = tmp_path / "f.ppm"
    full.write_bytes(
        f"P6\n{width} {height}\n255\n".encode() + bytes(width * height * 3)
    )
    assert is_usable(full, kind="ppm")

    cut = tmp_path / "c.ppm"
    cut.write_bytes(full.read_bytes()[: len(full.read_bytes()) // 2])
    assert not is_usable(cut, kind="ppm")


def test_video_without_a_probe_is_treated_as_unusable(tmp_path):
    """Unverifiable is not the same as good — refuse to assume."""
    from sofia.core.artifacts import is_usable

    v = tmp_path / "v.mp4"
    v.write_bytes(b"\x00" * 5000)
    assert not is_usable(v, kind="video", probe=None)


def test_a_video_that_does_not_decode_is_not_usable(tmp_path):
    from sofia.core.artifacts import is_usable

    def probe(path):
        raise RuntimeError("moov atom not found")

    v = tmp_path / "v.mp4"
    v.write_bytes(b"\x00" * 5000)
    assert not is_usable(v, kind="video", probe=probe)


def test_a_video_decoding_to_zero_duration_is_not_usable(tmp_path):
    from sofia.core.artifacts import is_usable

    v = tmp_path / "v.mp4"
    v.write_bytes(b"\x00" * 5000)
    assert not is_usable(
        v,
        kind="video",
        probe=lambda p: {"format": {"duration": "0"}, "streams": [{"codec_type": "video"}]},
    )


def test_a_complete_video_is_usable(tmp_path):
    from sofia.core.artifacts import is_usable

    v = tmp_path / "v.mp4"
    v.write_bytes(b"\x00" * 5000)
    assert is_usable(
        v,
        kind="video",
        probe=lambda p: {
            "format": {"duration": "21.5"},
            "streams": [{"codec_type": "video"}, {"codec_type": "audio"}],
        },
    )


# ---- journal survives an interrupted append ------------------------------
def test_a_torn_journal_tail_does_not_destroy_the_history(tmp_path):
    """Power loss mid-append can only tear the last line.

    The journal is preserved evidence; losing all of it because one append was
    interrupted would be worse than losing the interrupted entry.
    """
    store = CheckpointStore(tmp_path)
    for stage in (
        StageState.BRIEF_DONE,
        StageState.SCRIPT_DONE,
        StageState.SHOTS_DONE,
    ):
        store.advance("r1", stage, "director")

    path = tmp_path / "r1.journal.jsonl"
    path.write_bytes(path.read_bytes() + b'{"at": 1.0, "stage": "VOI')

    entries = store.journal("r1")
    assert [e["stage"] for e in entries] == [
        "BRIEF_DONE",
        "SCRIPT_DONE",
        "SHOTS_DONE",
    ]


def test_a_torn_tail_is_reported_not_hidden(tmp_path):
    store = CheckpointStore(tmp_path)
    store.advance("r1", StageState.BRIEF_DONE, "director")
    path = tmp_path / "r1.journal.jsonl"
    path.write_bytes(path.read_bytes() + b'{"at": 1.0, "sta')

    report = store.journal_integrity("r1")
    assert report["torn_tail"] is True
    assert report["entries"] == 1
    assert "losing power" in report["detail"]


def test_an_intact_journal_reports_clean(tmp_path):
    store = CheckpointStore(tmp_path)
    store.advance("r1", StageState.BRIEF_DONE, "director")
    report = store.journal_integrity("r1")
    assert report["torn_tail"] is False
    assert report["detail"] == ""
    assert report["entries"] == 1


def test_corruption_away_from_the_tail_still_raises(tmp_path):
    """Nothing in normal operation can damage a line that is not last."""
    store = CheckpointStore(tmp_path)
    store.advance("r1", StageState.BRIEF_DONE, "director")
    store.advance("r1", StageState.SCRIPT_DONE, "director")

    path = tmp_path / "r1.journal.jsonl"
    lines = path.read_text(encoding="utf-8").splitlines()
    lines[0] = '{"at": broken'
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with pytest.raises(CheckpointError):
        store.journal("r1")


def test_a_missing_journal_reports_absent_rather_than_torn(tmp_path):
    report = CheckpointStore(tmp_path).journal_integrity("never-existed")
    assert report["exists"] is False
    assert report["torn_tail"] is False


# ---- durable writes ------------------------------------------------------
def test_an_interrupted_write_leaves_the_previous_version_intact(tmp_path):
    """The host loses power mid-write; the old file must still be readable.

    ``Path.write_text`` truncates first, so the crash window costs the whole
    file. The atomic helper writes elsewhere and renames, so a reader sees one
    version or the other and never a splice.
    """
    from sofia.core.durable import atomic_write_json

    target = tmp_path / "state.json"
    atomic_write_json(target, {"records": ["first"]})

    class Unserialisable:
        pass

    with pytest.raises(TypeError):
        atomic_write_json(target, {"records": [Unserialisable()]})

    assert json.loads(target.read_text(encoding="utf-8")) == {"records": ["first"]}


def test_an_interrupted_write_leaves_no_temp_file_behind(tmp_path, monkeypatch):
    """A stray temp file would be picked up as an artifact on the next resume.

    The interrupt is injected at ``os.replace`` — the last moment before the
    swap — so the temp file definitely exists when it lands.
    """
    import os

    from sofia.core import durable

    target = tmp_path / "sub" / "cues.ass"
    durable.atomic_write_text(target, "ok")

    def interrupted(*args, **kwargs):
        raise KeyboardInterrupt("power loss")

    monkeypatch.setattr(os, "replace", interrupted)
    with pytest.raises(KeyboardInterrupt):
        durable.atomic_write_text(target, "half written")

    monkeypatch.undo()
    assert target.read_text(encoding="utf-8") == "ok"
    assert [p.name for p in target.parent.iterdir() if p.name.startswith(".tmp-")] == []
