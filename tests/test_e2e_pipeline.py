"""End-to-end, fault and resume tests over the whole studio."""

import json
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sofia.agents.base import Capability
from sofia.core.checkpoint import StageState
from sofia.core.errors import OwnershipError
from sofia.core.verdict import Verdict
from sofia.reel.contracts import GrowthInput
from sofia.reel.critics import PerceptualSample
from sofia.reel.director import PUBLISHING_HOLD, TERMINAL_APPROVED_STATE
from sofia.reel.stages import AuthoredPlan
from sofia.studio import build_studio
from sofia.voice.contracts import Language

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))


def _ffmpeg():
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:  # noqa: BLE001
        return shutil.which("ffmpeg")


needs_ffmpeg = pytest.mark.skipif(_ffmpeg() is None, reason="no ffmpeg available")


def _plan():
    from run_e2e_reel import PLAN_RU

    return PLAN_RU


def _growth():
    return GrowthInput(
        trend="честный процесс",
        audience="создатели коротких видео",
        target_kpi={"retention_3s": 0.75},
        hook_hypothesis="прямой вопрос-возражение",
    )


def _studio(tmp_path, devkit=True):
    voice_backends = reel_backends = None
    references = {}
    music = None
    if devkit:
        from sofia.devkit.backends import (
            NOT_SOFIA,
            DevMusicBed,
            build_dev_reel_backends,
            build_dev_voice_backends,
        )

        voice_backends = build_dev_voice_backends()
        reel_backends = build_dev_reel_backends(_ffmpeg(), tmp_path)
        references = {"default": NOT_SOFIA}
        music = DevMusicBed()
    studio = build_studio(
        tmp_path,
        language=Language.RU,
        creative=AuthoredPlan(_plan()),
        sofia_references=references,
        voice_backends=voice_backends,
        reel_backends=reel_backends,
    )
    studio.director.music_backend = music
    studio.director.config.frame_width = 540
    studio.director.config.frame_height = 960
    return studio


# ---- wiring --------------------------------------------------------------
def test_every_registered_role_is_executable(tmp_path):
    audit = _studio(tmp_path, devkit=False).audit()
    assert audit["agents"]["spec_only"] == []
    assert audit["agents"]["capabilities_missing"] == []
    assert audit["agents"]["conflicts"] == []
    assert audit["agents"]["total"] >= 24


def test_both_teams_are_registered(tmp_path):
    teams = _studio(tmp_path, devkit=False).audit()["teams"]
    assert len(teams["voice"]) == 7
    assert len(teams["reel"]) >= 16


def test_one_reel_has_exactly_one_owner(tmp_path):
    studio = _studio(tmp_path, devkit=False)
    studio.director.claim("reel-1")
    studio.factory.ownership.assert_owner("reel-1", studio.director.name)
    with pytest.raises(OwnershipError):
        studio.factory.ownership.acquire("reel-1", "another.director")


def test_publishing_stays_on_hold(tmp_path):
    assert PUBLISHING_HOLD is True
    assert TERMINAL_APPROVED_STATE == "READY_FOR_OWNER_REVIEW"
    status = _studio(tmp_path, devkit=False).director.status("reel-1")
    assert status["publishing"] == "HOLD"


def test_director_has_no_publish_method(tmp_path):
    director = _studio(tmp_path, devkit=False).director
    for forbidden in ("publish", "post", "upload", "release"):
        assert not hasattr(director, forbidden)


# ---- real-backend run ----------------------------------------------------
def test_run_without_backends_blocks_and_never_passes(tmp_path):
    studio = _studio(tmp_path, devkit=False)
    result = studio.director.produce("reel-nb", _growth())
    assert result.verdict is Verdict.BLOCKED
    assert result.verdict is not Verdict.PASS
    assert studio.director.resume_point("reel-nb") is StageState.HELD


# ---- devkit end to end ---------------------------------------------------
@needs_ffmpeg
def test_full_pipeline_produces_real_artifacts(tmp_path):
    studio = _studio(tmp_path)
    result = studio.director.produce("reel-e2e", _growth(), diagnostic=True)

    final = Path(result.assets.final)
    assert final.exists() and final.stat().st_size > 100_000
    assert Path(result.assets.cover).exists()
    assert Path(result.assets.subtitles).exists()
    assert Path(result.assets.music).exists()
    assert len(result.assets.shots) == 6
    for shot in result.assets.shots:
        assert Path(shot.video_path).exists()

    # The file decodes with both streams, at the planned runtime.
    decode = result.report.by_name("reel.decode")
    assert decode.verdict is Verdict.PASS
    assert 15.0 <= decode.measurement.value <= 30.0


@needs_ffmpeg
def test_a_diagnostic_run_can_never_approve_a_reel(tmp_path):
    result = _studio(tmp_path).director.produce(
        "reel-diag", _growth(), diagnostic=True
    )
    assert result.verdict is not Verdict.PASS
    assert not result.ready_for_owner_review
    assert result.report.by_name("reel.production").verdict is Verdict.HOLD


@needs_ffmpeg
def test_identity_and_lipsync_cannot_pass_without_sofia(tmp_path):
    result = _studio(tmp_path).director.produce("reel-id", _growth(), diagnostic=True)
    assert result.report.by_name("reel.video").verdict is Verdict.NOT_MEASURED
    assert result.report.by_name("reel.lipsync").verdict is Verdict.NOT_MEASURED
    assert result.report.by_name("reel.voice").verdict is Verdict.FAIL
    # Unmeasured categories score None, never 0 and never a passing number.
    assert result.scores["IDENTITY"] is None
    assert result.scores["LIPSYNC"] is None
    assert result.scores["OVERALL"] is None


@needs_ffmpeg
def test_roles_really_execute_through_the_runner(tmp_path):
    studio = _studio(tmp_path)
    studio.director.produce("reel-exec", _growth(), diagnostic=True)
    executed = set(studio.runner.executed_agents())
    for role in (
        "sofia.reel.trend",
        "sofia.reel.idea",
        "sofia.reel.hook",
        "sofia.reel.script",
        "sofia.reel.storyboard",
        "sofia.reel.shot_director",
        "sofia.reel.voice",
        "sofia.reel.video",
        "sofia.reel.editor",
    ):
        assert role in executed, role
    log = tmp_path / "logs" / "agent_execution.jsonl"
    records = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    assert len(records) >= 9
    assert all(r["owner"] == studio.director.name for r in records)


@needs_ffmpeg
def test_subtitles_are_burned_in_above_the_safe_zone(tmp_path):
    studio = _studio(tmp_path)
    studio.director.produce("reel-subs", _growth(), diagnostic=True)
    top, bottom = studio.director._subtitle_extent
    assert bottom <= 0.80
    assert top >= 0.14


@needs_ffmpeg
def test_ducking_is_verified_on_the_real_stems(tmp_path):
    result = _studio(tmp_path).director.produce("reel-mix", _growth(), diagnostic=True)
    mix = result.report.by_name("reel.audio_mix")
    assert mix.verdict is Verdict.PASS
    assert mix.measurement.value >= 9.0


# ---- fault / resume ------------------------------------------------------
@needs_ffmpeg
def test_a_reel_resumes_instead_of_restarting(tmp_path):
    studio = _studio(tmp_path)
    studio.director.produce("reel-resume", _growth(), diagnostic=True)

    shots_dir = tmp_path / "shots"
    rendered = sorted(p.name for p in shots_dir.glob("reel-resume*.mp4"))
    assert len(rendered) == 6
    stamps = {p.name: p.stat().st_mtime_ns for p in shots_dir.glob("reel-resume*.mp4")}

    journal = studio.director.checkpoints.journal("reel-resume")
    assert [j["stage"] for j in journal][:4] == [
        "BRIEF_DONE",
        "SCRIPT_DONE",
        "SHOTS_DONE",
        "VOICE_DONE",
    ]

    # A fresh studio object attaches to the same workdir, as a restarted
    # session would, and must not re-render shots that already exist.
    second = _studio(tmp_path)
    second.director.produce("reel-resume", _growth(), diagnostic=True)
    after = {p.name: p.stat().st_mtime_ns for p in shots_dir.glob("reel-resume*.mp4")}
    assert after == stamps


@needs_ffmpeg
def test_checkpoint_survives_a_lost_session(tmp_path):
    studio = _studio(tmp_path)
    studio.director.produce("reel-crash", _growth(), diagnostic=True)
    del studio

    revived = _studio(tmp_path)
    cp = revived.director.checkpoints.load("reel-crash")
    assert cp is not None
    assert cp.stage in (StageState.HELD, StageState.FAILED, StageState.EDIT_DONE)
    assert revived.director.checkpoints.journal("reel-crash")


@needs_ffmpeg
def test_repair_is_routed_to_components_not_a_full_rebuild(tmp_path):
    result = _studio(tmp_path).director.produce(
        "reel-repair", _growth(), diagnostic=True
    )
    assert result.repairs
    decision = result.repairs[0]
    assert decision["components"]
    assert decision["resume_from"] != StageState.CREATED.value


@needs_ffmpeg
def test_perceptual_hold_even_when_structural_gates_pass(tmp_path):
    studio = _studio(tmp_path)
    samples = (
        PerceptualSample("BEST", "a.mp4", "r"),
        PerceptualSample("RANDOM", "b.mp4", "r"),
        PerceptualSample("FAIL", "c.mp4", "r", bad_story=True, fake_motion=True),
    )
    result = studio.director.produce(
        "reel-perc", _growth(), perceptual_samples=samples, diagnostic=True
    )
    assert result.report.by_name("reel.perceptual").verdict is Verdict.HOLD
    assert result.verdict is not Verdict.PASS
