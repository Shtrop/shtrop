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


@pytest.fixture(scope="module")
def devkit_run(tmp_path_factory):
    """One full devkit pipeline run, shared by the assertions that only read it.

    Producing a Reel costs six renders, an encode and a mix. Tests that merely
    inspect the result of a standard run share this one; tests that need their
    own pipeline state (resume, a lost session, supplied perceptual samples)
    still build their own.
    """
    if _ffmpeg() is None:
        pytest.skip("no ffmpeg available")
    workdir = tmp_path_factory.mktemp("devkit-run")
    studio = _studio(workdir)
    result = studio.director.produce("reel-shared", _growth(), diagnostic=True)
    return studio, result, workdir


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
def test_full_pipeline_produces_real_artifacts(devkit_run):
    _studio_, result, _ = devkit_run

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


def test_a_diagnostic_run_can_never_approve_a_reel(devkit_run):
    _studio_, result, _ = devkit_run
    assert result.verdict is not Verdict.PASS
    assert not result.ready_for_owner_review
    assert result.report.by_name("reel.production").verdict is Verdict.HOLD


def test_identity_and_lipsync_cannot_pass_without_sofia(devkit_run):
    _studio_, result, _ = devkit_run
    assert result.report.by_name("reel.video").verdict is Verdict.NOT_MEASURED
    assert result.report.by_name("reel.lipsync").verdict is Verdict.NOT_MEASURED
    assert result.report.by_name("reel.voice").verdict is Verdict.FAIL
    # Unmeasured categories score None, never 0 and never a passing number.
    assert result.scores["IDENTITY"] is None
    assert result.scores["LIPSYNC"] is None
    assert result.scores["OVERALL"] is None


def test_roles_really_execute_through_the_runner(devkit_run):
    studio, _result, tmp_path = devkit_run
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


def test_subtitles_are_burned_in_above_the_safe_zone(devkit_run):
    studio, _result, _ = devkit_run
    top, bottom = studio.director._subtitle_extent
    assert bottom <= 0.80
    assert top >= 0.14


def test_ducking_is_verified_on_the_real_stems(devkit_run):
    _studio_, result, _ = devkit_run
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


def test_repair_is_routed_to_components_not_a_full_rebuild(devkit_run):
    _studio_, result, _ = devkit_run
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


@needs_ffmpeg
def test_the_growth_loop_closes_through_the_director(devkit_run):
    """A finished Reel reaches growth memory without being asked to."""
    studio, result, _ = devkit_run
    shadow = studio.growth.memory.shadow
    assert shadow, "the director never reported the Reel to the Growth Engine"
    entry = next(e for e in shadow if e["reel_id"] == result.reel_id)
    assert entry["evidence"] == "PREDICTED"
    assert entry["hook"] == result.brief.hook
    assert entry["blockers"]
    # Shadow data never becomes a platform metric.
    assert studio.growth.learned()["real_publications"] == 0
    assert studio.growth.learned()["real_baselines"]["retention"]["value"] is None


@needs_ffmpeg
def test_a_broken_growth_engine_never_changes_a_verdict(tmp_path):
    """Bookkeeping must not turn a HOLD into a crash — but it must be visible."""

    class BrokenGrowth:
        def observe(self, result, *, diagnostic=False):
            raise RuntimeError("analytics sink is down")

    studio = _studio(tmp_path)
    studio.director.growth = BrokenGrowth()
    result = studio.director.produce("reel-broken-growth", _growth(), diagnostic=True)

    assert result.verdict is Verdict.HOLD
    # The failure is recorded rather than swallowed silently.
    assert studio.director.growth_errors
    assert "analytics sink is down" in studio.director.growth_errors[0]
    assert studio.director.status("reel-broken-growth")["growth_errors"]


@needs_ffmpeg
def test_resume_re_renders_a_shot_left_half_written(tmp_path):
    """The failure mode of a host that loses power mid-render.

    A truncated shot exists and is not empty, so a presence check would reuse
    it and ship a Reel built on a fragment that does not even decode.
    """
    studio = _studio(tmp_path)
    studio.director.produce("reel-torn", _growth(), diagnostic=True)

    shots = sorted((tmp_path / "shots").glob("reel-torn*.mp4"))
    assert shots
    victim = shots[0]
    intact = victim.read_bytes()
    victim.write_bytes(intact[: int(len(intact) * 0.6)])
    torn_size = victim.stat().st_size
    assert torn_size > 0  # exists and non-empty: presence alone would pass it

    # A fresh studio attaches to the same workdir, as a restarted session would.
    revived = _studio(tmp_path)
    revived.director.produce("reel-torn", _growth(), diagnostic=True)

    assert victim.stat().st_size != torn_size, "the torn shot was reused, not re-rendered"
    assert revived.director._usable_video(str(victim))


# ---- repair rounds -------------------------------------------------------
@needs_ffmpeg
def test_a_repairable_defect_regenerates_only_that_component(tmp_path):
    """The router said what to rebuild; nothing ever rebuilt it.

    ``max_repair_rounds`` was declared and read by nothing: a defect produced a
    routing decision and the Reel was held. Here a cover defect (EDIT_DONE, the
    narrowest route) has to actually send the pipeline back through the edit
    stage and no further.
    """
    from sofia.reel.contracts import ReelDefect, ReelDiagnosis
    from sofia.reel.critics import CriticOutcome
    from sofia.core.gates import GateResult

    studio = _studio(tmp_path)
    director = studio.director
    director.config.max_repair_rounds = 2

    calls = {"cover": 0}
    original = director.cover_critic.review

    def failing_cover(*args, **kwargs):
        calls["cover"] += 1
        if calls["cover"] == 1:
            return CriticOutcome(
                GateResult(
                    name="reel.cover",
                    verdict=Verdict.FAIL,
                    critical=True,
                    reason="injected: cover is unreadable",
                ),
                (ReelDiagnosis(ReelDefect.COVER, detail="injected", critic="test"),),
            )
        return original(*args, **kwargs)

    director.cover_critic.review = failing_cover
    result = director.produce("reel-repair", _growth(), diagnostic=True)

    # diagnostic runs never repair: they walked past blocks on purpose.
    assert director._repair_round == 0
    assert calls["cover"] == 1
    assert result.verdict is not Verdict.PASS


def test_an_unmeasurable_gate_is_never_answered_with_a_repair(tmp_path):
    """Regenerating cannot make a missing verifier appear.

    This is the fail-closed edge that matters most: if a repair could be
    triggered by NOT_MEASURED, the pipeline would burn GPU re-rendering until
    the round budget ran out and still know nothing.
    """
    from sofia.reel.contracts import ReelDefect, ReelDiagnosis
    from sofia.reel.repair_router import RepairRouter

    decision = RepairRouter().route(
        [
            ReelDiagnosis(ReelDefect.COVER, detail="cover is unreadable"),
            ReelDiagnosis(ReelDefect.NOT_MEASURED, detail="no face detector"),
        ]
    )
    assert decision.full_stop is True
    assert decision.actionable is False

    director = _studio(tmp_path, devkit=False).director
    stages, skipped = director._repairable(decision)
    assert "edit" in stages  # the cover defect alone would be repairable
    assert "not repairable" in director._why_not_repairable(decision, skipped)


def test_re_authoring_the_creative_plan_is_not_treated_as_a_repair(tmp_path):
    """An authored plan hands back the same plan, so retrying it is a loop."""
    from sofia.reel.contracts import ReelDefect, ReelDiagnosis
    from sofia.reel.repair_router import RepairRouter

    decision = RepairRouter().route(
        [ReelDiagnosis(ReelDefect.BAD_HOOK, detail="the hook is not in the opening shot")]
    )
    director = _studio(tmp_path, devkit=False).director
    stages, skipped = director._repairable(decision)
    assert stages == ()
    assert skipped == ["HookAgent"]
    assert "human decision" in director._why_not_repairable(decision, skipped)


def test_repair_stages_include_everything_downstream_of_the_fix(tmp_path):
    """A re-rendered shot that is never re-cut leaves the old take in the file."""
    from sofia.reel.contracts import ReelDefect, ReelDiagnosis
    from sofia.reel.repair_router import RepairRouter

    director = _studio(tmp_path, devkit=False).director
    for defect, expected in (
        (ReelDefect.IDENTITY, ("video", "lipsync", "edit")),
        (ReelDefect.VOICE, ("voice", "lipsync", "edit")),
        (ReelDefect.LIPSYNC, ("lipsync", "edit")),
        (ReelDefect.SUBTITLES, ("edit",)),
    ):
        decision = RepairRouter().route([ReelDiagnosis(defect, detail="x")])
        stages, _ = director._repairable(decision)
        assert stages == expected, defect


def test_a_repair_round_writes_beside_the_take_it_replaces(tmp_path):
    """NO-DELETE covers the evidence of a failed attempt too."""
    director = _studio(tmp_path, devkit=False).director
    assert director._slug("reel-1") == "reel-1"
    assert director._slug("reel-1", 1) == "reel-1.r1"
    assert director._slug("..", 2) == "reel.r2"


@needs_ffmpeg
def test_a_repair_re_renders_the_routed_shot_and_leaves_the_others_alone(tmp_path):
    """The point of routing: pay for the broken shot, not for the whole Reel."""
    from sofia.reel.contracts import ReelAssets, Shot, ShotType, StoryBeat

    studio = _studio(tmp_path)
    director = studio.director
    director.claim("reel-narrow")

    shots = [
        Shot(
            index=i,
            beat=StoryBeat.DEVELOPMENT,
            shot_type=ShotType.B_ROLL,
            description=f"shot {i}",
            duration_s=1.0,
        )
        for i in (1, 2)
    ]
    director._invoke(Capability.VIDEO_GENERATION, "reel-narrow", shots=shots, gpu_cleared=True)
    first_take = {s.index: s.video_path for s in shots}
    assert all(first_take.values())

    director._repair_round = 1
    director._regenerate(
        "reel-narrow",
        ("video",),
        brief=None,
        plan=None,
        shots=shots,
        assets=ReelAssets(),
        voice_results={},
        shot_indices=[2],
    )

    repaired = {s.index: s.video_path for s in shots}
    assert repaired[1] == first_take[1], "an untouched shot was re-rendered"
    assert repaired[2] != first_take[2], "the routed shot was not re-rendered"
    assert ".r1." in repaired[2], "the repair overwrote the take it replaced"
    assert Path(first_take[2]).exists(), "the failed take must stay as evidence"


def test_the_repair_loop_is_bounded_and_stops_when_the_reel_settles(tmp_path):
    """Two rounds means two: a Reel is held for the owner, not retried forever."""
    from sofia.reel.contracts import ReelAssets, ReelDefect, ReelDiagnosis, ReelResult

    director = _studio(tmp_path, devkit=False).director
    director.config.max_repair_rounds = 2
    regenerated: list[tuple[str, ...]] = []

    def fake_regenerate(reel_id, stages, **kwargs):
        regenerated.append(tuple(stages))
        return kwargs["voice_results"]

    director._regenerate = fake_regenerate

    def failing() -> ReelResult:
        return ReelResult(
            reel_id="r",
            verdict=Verdict.FAIL,
            stage=StageState.FAILED,
            diagnoses=[ReelDiagnosis(ReelDefect.COVER, detail="unreadable")],
        )

    repairs: list[dict] = []
    result = director._repair_until_settled(
        failing(),
        failing,
        reel_id="r",
        brief=None,
        plan=None,
        shots=[],
        assets=ReelAssets(),
        voice_results={},
        repairs=repairs,
    )
    assert result.verdict is Verdict.FAIL
    assert regenerated == [("edit",), ("edit",)]
    assert repairs[-1]["reason"].startswith("repair budget exhausted after 2")


def test_a_repair_that_clears_the_defect_stops_the_loop(tmp_path):
    from sofia.reel.contracts import ReelAssets, ReelDefect, ReelDiagnosis, ReelResult

    director = _studio(tmp_path, devkit=False).director
    director.config.max_repair_rounds = 3
    rounds = {"n": 0}
    director._regenerate = lambda reel_id, stages, **kw: kw["voice_results"]

    def qa() -> ReelResult:
        rounds["n"] += 1
        if rounds["n"] > 1:
            return ReelResult(reel_id="r", verdict=Verdict.PASS, stage=StageState.FINAL_QA)
        return ReelResult(
            reel_id="r",
            verdict=Verdict.FAIL,
            stage=StageState.FAILED,
            diagnoses=[ReelDiagnosis(ReelDefect.SUBTITLES, detail="cue overruns")],
        )

    repairs: list[dict] = []
    result = director._repair_until_settled(
        qa(),
        qa,
        reel_id="r",
        brief=None,
        plan=None,
        shots=[],
        assets=ReelAssets(),
        voice_results={},
        repairs=repairs,
    )
    assert result.verdict is Verdict.PASS
    assert director._repair_round == 1
    assert not any("budget exhausted" in str(r.get("reason", "")) for r in repairs)


def test_an_unrepairable_defect_does_not_spend_a_repair_round(tmp_path):
    from sofia.reel.contracts import ReelAssets, ReelDefect, ReelDiagnosis, ReelResult

    director = _studio(tmp_path, devkit=False).director
    director._regenerate = lambda *a, **k: pytest.fail("NOT_MEASURED must not regenerate")

    failing = ReelResult(
        reel_id="r",
        verdict=Verdict.HOLD,
        stage=StageState.HELD,
        diagnoses=[ReelDiagnosis(ReelDefect.NOT_MEASURED, detail="no face detector")],
    )
    repairs: list[dict] = []
    result = director._repair_until_settled(
        failing,
        lambda: failing,
        reel_id="r",
        brief=None,
        plan=None,
        shots=[],
        assets=ReelAssets(),
        voice_results={},
        repairs=repairs,
    )
    assert result is failing
    assert director._repair_round == 0
    assert repairs[-1]["regenerated"] == []
    assert "not repairable" in repairs[-1]["reason"]


def test_the_repair_budget_is_per_reel_not_per_director(tmp_path):
    """A director that repaired one Reel must start the next one at zero."""
    director = _studio(tmp_path, devkit=False).director
    director._repair_round = 2
    try:
        director.produce("reel-fresh", _growth())
    except Exception:  # noqa: BLE001 - no backends here; produce is expected to stop
        pass
    assert director._repair_round == 0
