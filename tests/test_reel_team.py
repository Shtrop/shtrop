"""Reel team: shot routing, story structure, subtitles, mix, repair, gates."""
import json

import pytest

from sofia.core.gates import GateResult, evaluate_gates
from sofia.core.checkpoint import StageState
from sofia.core.verdict import Evidence, Measurement, Verdict
from sofia.reel.contracts import (
    ReelBrief,
    ReelDefect,
    ReelDiagnosis,
    Shot,
    ShotType,
    StoryBeat,
)
from sofia.reel.critics import (
    FINAL_GATE_CATEGORIES,
    AudioMixCritic,
    CoverCritic,
    FinalGate,
    LipSyncCritic,
    PerceptualReviewGate,
    PerceptualSample,
    ReelThresholds,
    StoryCritic,
    VideoQACritic,
    sample_for_review,
)
from sofia.reel.backends import ReelBackends
from sofia.reel.gpu import GpuArbiter, WorkClass
from sofia.reel.growth import (
    GrowthEngine,
    GrowthMemory,
    GrowthMemoryError,
    PublicationRecord,
)
from sofia.reel.repair_router import RepairRouter
from sofia.reel.shots import estimated_cost, assign_profiles, profile_for, validate_story
from sofia.reel.subtitles import (
    build_cues,
    estimate_text_extent,
    parse_srt,
    to_ass,
    verify_cues,
    write_srt,
)
from sofia.voice.contracts import Language


def _shots():
    return [
        Shot(0, StoryBeat.HOOK, ShotType.TALKING, "hook to camera", 2.8,
             voice_line="Ты правда думаешь, что дело в камере?"),
        Shot(1, StoryBeat.SETUP, ShotType.DETAIL, "cappuccino macro", 3.0),
        Shot(2, StoryBeat.DEVELOPMENT, ShotType.B_ROLL, "desk timelapse", 4.5),
        Shot(3, StoryBeat.PAYOFF, ShotType.PAYOFF, "sofia exhales", 4.2),
    ]


# ---- shot routing --------------------------------------------------------
def test_only_face_shots_carry_the_identity_gate():
    assert ShotType.FACE_CRITICAL.identity_gate
    assert ShotType.TALKING.identity_gate
    assert not ShotType.B_ROLL.identity_gate
    assert not ShotType.DETAIL.identity_gate


def test_only_talking_shots_need_lipsync():
    assert ShotType.TALKING.needs_lipsync
    assert not ShotType.PAYOFF.needs_lipsync


def test_profiles_are_assigned_per_shot_type():
    shots = assign_profiles(_shots())
    assert shots[0].generator_profile == "talking_720p_lipsync"
    assert shots[1].generator_profile == "detail_macro"
    assert shots[2].generator_profile == "broll_1080p_fast"


def test_shot_routing_saves_gpu_against_an_all_face_pipeline():
    cost = estimated_cost(_shots())
    assert cost["saved_gpu_s"] > 0
    assert cost["estimated_gpu_s"] < cost["naive_all_face_gpu_s"]
    assert cost["face_critical_shots"] == 2


def test_cheap_shot_types_need_no_identity_pipeline():
    assert not profile_for(ShotType.B_ROLL).needs_identity_gate
    assert profile_for(ShotType.B_ROLL).vram_gb < profile_for(ShotType.TALKING).vram_gb


# ---- story ---------------------------------------------------------------
def test_a_good_arc_validates():
    assert validate_story(_shots()) == []


def test_one_portrait_plus_subtitles_is_not_a_reel():
    problems = validate_story(
        [Shot(0, StoryBeat.PAYOFF, ShotType.FACE_CRITICAL, "portrait", 20.0)]
    )
    assert any("SETUP" in p for p in problems)
    assert any("talking segment" in p for p in problems)
    assert any("B-roll" in p for p in problems)


def test_out_of_order_beats_are_rejected():
    shots = _shots()
    shots[1].beat = StoryBeat.PAYOFF
    shots[3].beat = StoryBeat.SETUP
    assert any("out of order" in p for p in validate_story(shots))


def test_a_scene_without_a_function_is_rejected():
    shots = _shots()
    shots[2].description = "   "
    assert any("no described function" in p for p in validate_story(shots))


def test_story_critic_flags_a_caption_the_shots_do_not_deliver():
    brief = ReelBrief(
        reel_id="r", purpose="p", audience="a", language=Language.RU,
        trend="t", hook="Ты правда думаешь, что дело в камере?",
        story_arc="arc", cta="Сохрани",
    )
    outcome = StoryCritic(ReelThresholds()).review(
        brief,
        _shots(),
        caption="Бесплатный курс по монтажу дронов и колористике недвижимости",
    )
    assert outcome.result.verdict is Verdict.FAIL


# ---- video / lipsync QA --------------------------------------------------
def test_video_qa_blocks_when_a_face_shot_has_no_identity_measurement(tmp_path):
    shots = _shots()
    for s in shots:
        path = tmp_path / f"{s.index}.mp4"
        path.write_bytes(b"x")
        s.video_path = str(path)
    outcome = VideoQACritic(
        ReelBackends.unavailable("none"), ReelThresholds()
    ).review(shots)
    assert outcome.result.verdict is Verdict.NOT_MEASURED
    assert outcome.result.blocking


def test_lipsync_requires_every_named_metric(tmp_path):
    shots = _shots()
    talking = shots[0]
    talking.lipsync_path = str(tmp_path / "ls.mp4")
    talking.measurements = [
        Measurement(m, 0.95, Evidence.MEASURED_LOCAL, source="t")
        for m in LipSyncCritic.REQUIRED[:-1]  # av_offset_ms missing
    ]
    outcome = LipSyncCritic(
        ReelBackends.unavailable("none"), ReelThresholds()
    ).review(shots)
    assert outcome.result.verdict is Verdict.NOT_MEASURED
    assert "av_offset_ms" in outcome.result.reason


def test_lipsync_not_applicable_without_a_talking_shot():
    shots = [s for s in _shots() if not s.shot_type.needs_lipsync]
    outcome = LipSyncCritic(
        ReelBackends.unavailable("none"), ReelThresholds()
    ).review(shots)
    assert outcome.result.verdict is Verdict.PASS


# ---- subtitles -----------------------------------------------------------
def _segments():
    return [
        ("Ты правда думаешь, что дело в камере?", 0.0, 2.8),
        ("Свет был тот же. Камера та же.", 2.9, 7.0),
    ]


def test_cues_are_readable_and_match_the_speech(tmp_path):
    cues = build_cues(_segments())
    spoken = " ".join(t for t, _, _ in _segments())
    issues = verify_cues(
        cues, spoken_text=spoken, language=Language.RU,
        video_duration_s=22.0, text_top=0.62, text_bottom=0.78,
    )
    assert issues.ok, issues.all_issues()


def test_subtitles_that_do_not_match_the_speech_are_rejected():
    cues = build_cues([("Совершенно другой текст здесь", 0.0, 3.0)])
    issues = verify_cues(
        cues, spoken_text="Ты правда думаешь, что дело в камере?",
        language=Language.RU, video_duration_s=22.0, text_top=0.62, text_bottom=0.78,
    )
    assert issues.text_mismatch


def test_subtitles_past_the_end_of_the_video_are_rejected():
    cues = build_cues(_segments())
    issues = verify_cues(
        cues, spoken_text=" ".join(t for t, _, _ in _segments()),
        language=Language.RU, video_duration_s=3.0, text_top=0.62, text_bottom=0.78,
    )
    assert issues.timing


def test_safe_zone_violations_are_rejected():
    cues = build_cues(_segments())
    issues = verify_cues(
        cues, spoken_text=" ".join(t for t, _, _ in _segments()),
        language=Language.RU, video_duration_s=22.0, text_top=0.02, text_bottom=0.99,
    )
    assert len(issues.safe_zone) == 2


def test_srt_round_trips(tmp_path):
    cues = build_cues(_segments())
    path = write_srt(cues, tmp_path / "s.srt")
    assert [c.lines for c in parse_srt(path)] == [c.lines for c in cues]


def test_ass_carries_an_explicit_script_resolution():
    ass = to_ass(build_cues(_segments()), width=1080, height=1920, safe_bottom=0.78)
    assert "PlayResX: 1080" in ass and "PlayResY: 1920" in ass
    # MarginV is measured up from the bottom edge.
    assert "422" in ass or "MarginV" in ass


def test_text_extent_lands_above_the_bottom_safe_zone():
    top, bottom = estimate_text_extent(
        build_cues(_segments()), height=1920, safe_bottom=0.78
    )
    assert bottom == pytest.approx(0.78, abs=0.01)
    assert 0.14 < top < bottom


# ---- audio mix -----------------------------------------------------------
def test_audio_mix_blocks_without_stems(tmp_path):
    from sofia.voice.audio import write_wav

    mix = write_wav(tmp_path / "m.wav", [0.2] * 22050, 22050)
    outcome = AudioMixCritic(ReelThresholds()).review(
        voice_stem=None, music_stem=None, final_mix=str(mix)
    )
    assert outcome.result.verdict is Verdict.NOT_MEASURED
    assert "stems" in outcome.result.reason


def test_audio_mix_fails_when_music_masks_the_voice(tmp_path):
    """A bed that was never ducked is as loud between the phrases as under them."""
    voice, music, mix = _mix_stems(tmp_path, bed_under_speech=0.16, bed_in_gaps=0.16)
    outcome = AudioMixCritic(ReelThresholds()).review(
        voice_stem=voice, music_stem=music, final_mix=mix
    )
    assert outcome.result.verdict is Verdict.FAIL
    assert "ducking" in outcome.result.reason


def test_the_mix_gate_reads_the_delivered_file_not_the_stems(tmp_path):
    """The stems are the same in both mixes; only the delivered file differs.

    Comparing stem levels was the old check, and it cannot tell these apart:
    it describes what the mix was asked to be and stays true whether or not the
    ducking step ever ran.
    """
    ducked = _mix_stems(tmp_path / "ducked")
    raw = _mix_stems(tmp_path / "raw", bed_under_speech=0.16, bed_in_gaps=0.16)

    from sofia.voice.audio import analyse_wav

    def stem_headroom(stems):
        return analyse_wav(stems[0]).rms_dbfs - analyse_wav(stems[1]).rms_dbfs

    # Identical by the measurement the gate used to make.
    assert stem_headroom(ducked) == pytest.approx(stem_headroom(raw), abs=0.01)

    critic = AudioMixCritic(ReelThresholds())
    good = critic.review(voice_stem=ducked[0], music_stem=ducked[1], final_mix=ducked[2])
    bad = critic.review(voice_stem=raw[0], music_stem=raw[1], final_mix=raw[2])
    assert good.result.verdict is Verdict.PASS
    assert bad.result.verdict is Verdict.FAIL


def test_a_mix_with_no_gap_cannot_be_judged(tmp_path):
    """Wall-to-wall speech leaves nowhere to hear the bed alone."""
    import math

    from sofia.voice.audio import write_wav

    rate = 22050
    tone = [0.2 * math.sin(2 * math.pi * 200 * i / rate) for i in range(rate * 3)]
    voice = write_wav(tmp_path / "v.wav", tone, rate)
    music = write_wav(tmp_path / "m.wav", [0.02 * t for t in tone], rate)
    mix = write_wav(tmp_path / "mix.wav", [1.02 * t for t in tone], rate)

    outcome = AudioMixCritic(ReelThresholds()).review(
        voice_stem=str(voice), music_stem=str(music), final_mix=str(mix)
    )
    assert outcome.result.verdict is Verdict.NOT_MEASURED
    assert "gap" in outcome.result.reason


# ---- cover / perceptual --------------------------------------------------
def test_cover_without_metrics_is_not_measured(tmp_path):
    cover = tmp_path / "c.jpg"
    cover.write_bytes(b"x")
    outcome = CoverCritic().review(str(cover), {})
    assert outcome.result.verdict is Verdict.NOT_MEASURED


def test_missing_cover_blocks():
    assert CoverCritic().review(None, {}).result.blocking


def test_perceptual_review_requires_all_three_buckets():
    outcome = PerceptualReviewGate().review(
        [PerceptualSample("BEST", "a.mp4", "reviewer")]
    )
    assert outcome.result.verdict is Verdict.NOT_MEASURED
    assert "RANDOM" in outcome.result.reason


def test_good_numbers_but_bad_looking_footage_holds():
    samples = [
        PerceptualSample("BEST", "a.mp4", "r"),
        PerceptualSample("RANDOM", "b.mp4", "r"),
        PerceptualSample("FAIL", "c.mp4", "r", dead_eyes=True, face_morph=True),
    ]
    outcome = PerceptualReviewGate().review(samples)
    assert outcome.result.verdict is Verdict.HOLD
    assert {d.defect for d in outcome.diagnoses} == {ReelDefect.SHOT}


def test_sampling_picks_best_random_and_worst():
    picks = sample_for_review(["a", "b", "c"], {"a": 0.1, "b": 0.5, "c": 0.9})
    assert picks["BEST"] == "c" and picks["FAIL"] == "a" and picks["RANDOM"] in "abc"


# ---- final gate ----------------------------------------------------------
def test_decode_pass_alone_is_not_a_reel_pass():
    report = evaluate_gates(
        [GateResult("reel.decode", Verdict.PASS, True)],
        required_critical=FINAL_GATE_CATEGORIES,
    )
    assert report.verdict is Verdict.MISSING
    assert len(report.missing_critical) == len(FINAL_GATE_CATEGORIES) - 1


def test_final_gate_passes_only_with_every_category():
    results = [GateResult(name, Verdict.PASS, True) for name in FINAL_GATE_CATEGORIES]
    assert FinalGate().evaluate(results).verdict is Verdict.PASS


def test_missing_final_file_is_missing_not_error():
    result = FinalGate.decode_gate(None, ReelBackends.unavailable("x"), ReelThresholds())
    assert result.verdict is Verdict.MISSING


# ---- repair router -------------------------------------------------------
def test_subtitle_defect_resumes_from_edit_not_from_zero():
    d = RepairRouter().route([ReelDiagnosis(ReelDefect.SUBTITLES, detail="typo")])
    assert d.resume_from is StageState.EDIT_DONE
    assert d.components == ["SubtitleAgent"]


def test_identity_defect_rebuilds_only_the_affected_shot():
    d = RepairRouter().route(
        [ReelDiagnosis(ReelDefect.IDENTITY, shot_index=3, detail="0.61")]
    )
    assert d.resume_from is StageState.SHOTS_DONE
    assert d.shot_indices == [3]


def test_router_rolls_back_to_the_earliest_affected_stage():
    d = RepairRouter().route(
        [
            ReelDiagnosis(ReelDefect.COVER, detail="unreadable"),
            ReelDiagnosis(ReelDefect.BAD_HOOK, detail="weak"),
        ]
    )
    assert d.resume_from is StageState.BRIEF_DONE


def test_unmeasurable_gate_cannot_be_repaired_by_regenerating():
    d = RepairRouter().route([ReelDiagnosis(ReelDefect.NOT_MEASURED, detail="no model")])
    assert not d.actionable and d.full_stop


def test_every_defect_has_a_route():
    for defect in ReelDefect:
        assert RepairRouter().route([ReelDiagnosis(defect)]).routes


# ---- gpu priority --------------------------------------------------------
def test_light_work_never_waits_for_the_gpu():
    ok, reason = GpuArbiter().may_run(WorkClass.LIGHT)
    assert ok and "never waits" in reason


def test_heavy_work_waits_for_a_live_production_lock(tmp_path):
    import os

    (tmp_path / "gpu_render.lock").write_text(str(os.getpid()), encoding="utf-8")
    arb = GpuArbiter(lock_dir=tmp_path)
    assert arb.active_production_locks() == ["gpu_render"]
    ok, reason = arb.may_run(WorkClass.HEAVY)
    assert not ok and "production holds the GPU" in reason
    # Light work still proceeds alongside production.
    assert arb.may_run(WorkClass.LIGHT)[0]


def test_a_lock_owned_by_a_dead_process_is_not_live(tmp_path):
    (tmp_path / "gpu_render.lock").write_text("999999", encoding="utf-8")
    assert GpuArbiter(lock_dir=tmp_path).active_production_locks() == []


# ---- growth --------------------------------------------------------------
def test_growth_reports_missing_baselines_as_not_measured():
    baseline = GrowthEngine(GrowthMemory()).memory.baseline("retention")
    assert baseline.value is None
    assert baseline.evidence.value == "NOT_MEASURED"


def test_shadow_planning_is_never_reported_as_a_real_metric():
    entry = GrowthEngine().record_outcome("r1", "HOLD", {"story": 8.0})
    assert entry["evidence"] == "PREDICTED"
    assert "no publication occurred" in entry["note"]


def test_growth_input_is_labelled_while_publishing_is_on_hold():
    gi = GrowthEngine().brief_director(
        trend="t", audience="a", hook_hypothesis="h"
    )
    assert gi.shadow_planning
    assert "HOLD" in gi.evidence


# ---- batch benchmark honesty ---------------------------------------------
def _run(verdict, *, repairs=0, unmeasured=(), arm="controlled"):
    from sofia.reel.benchmark import ReelRun

    return ReelRun(
        reel_id="r",
        arm=arm,
        plan_name="p",
        verdict=verdict,
        reason="",
        wall_s=10.0,
        repairs=repairs,
        unmeasured=tuple(unmeasured),
        estimated_gpu_s=700.0,
        peak_vram_gb=24.0,
    )


def test_a_batch_where_nothing_was_measured_reports_no_rates():
    from sofia.reel.benchmark import BatchReport

    report = BatchReport(runs=[_run(Verdict.HOLD, unmeasured=("reel.video",))] * 10)
    assert report.verified == 0
    assert not report.measurable
    assert report.first_pass_rate is None
    assert report.final_pass_rate is None
    assert report.manual_intervention_rate is None
    assert report.verdict is Verdict.NOT_MEASURED


def test_a_small_batch_says_nothing_about_repeatability():
    from sofia.reel.benchmark import MIN_BATCH, BatchReport

    report = BatchReport(runs=[_run(Verdict.PASS) for _ in range(MIN_BATCH - 1)])
    assert not report.measurable
    assert report.final_pass_rate is None


def test_a_measured_batch_reports_real_rates():
    from sofia.reel.benchmark import BatchReport

    runs = [_run(Verdict.PASS) for _ in range(6)] + [
        _run(Verdict.PASS, repairs=2),
        _run(Verdict.FAIL),
    ]
    report = BatchReport(runs=runs)
    assert report.measurable
    assert report.final_pass_rate == pytest.approx(7 / 8)
    assert report.first_pass_rate == pytest.approx(6 / 8)
    assert report.repair_rate == pytest.approx(1 / 8)
    assert report.manual_intervention_rate == pytest.approx(1 / 8)
    assert report.verdict is Verdict.FAIL


def test_manual_intervention_counts_anything_the_pipeline_could_not_settle():
    from sofia.reel.benchmark import BatchReport

    report = BatchReport(runs=[_run(Verdict.PASS)] * 5 + [_run(Verdict.HOLD)] * 5)
    assert report.manual_intervention_rate == pytest.approx(0.5)


def test_blocking_histogram_ranks_the_worst_offender_first():
    from sofia.reel.benchmark import BatchReport, ReelRun

    runs = [
        ReelRun("a", "controlled", "p", Verdict.HOLD, "", 1.0, 0,
                blocking=("reel.voice", "reel.video")),
        ReelRun("b", "controlled", "p", Verdict.HOLD, "", 1.0, 0,
                blocking=("reel.voice",)),
    ]
    assert list(BatchReport(runs=runs).blocking_histogram()) == [
        "reel.voice",
        "reel.video",
    ]


# ---- champion vs challenger ----------------------------------------------
def _arm(name, champion=False, **overrides):
    from sofia.reel.challenger import REQUIRED_METRICS, ArmResult

    metrics = {m: 0.90 for m in REQUIRED_METRICS}
    # The two metrics that are not a 0-1 quality score, and where lower wins.
    metrics["face_drift"] = 0.05
    metrics["av_offset_ms"] = 40.0
    metrics.update(overrides)
    return ArmResult(name=name, champion=champion, metrics=metrics)


def test_a_clearly_better_challenger_is_recommended_not_promoted():
    from sofia.reel.challenger import REQUIRED_METRICS, TrialReport

    better = _arm("longcat", **{m: 0.95 for m in REQUIRED_METRICS})
    better.metrics["face_drift"] = 0.02
    better.metrics["av_offset_ms"] = 25.0
    report = TrialReport(champion=_arm("champion", champion=True), challengers=[better])
    verdict, reason = report.recommendation(better)
    assert verdict is Verdict.PASS
    assert "not a promotion" in reason
    # Nothing is promoted automatically.
    assert report.to_dict()["promoted"] == []


def test_identity_regression_sinks_a_challenger_however_good_the_mouth():
    from sofia.reel.challenger import REQUIRED_METRICS, TrialReport

    challenger = _arm("highsync", **{m: 0.99 for m in REQUIRED_METRICS})
    challenger.metrics["identity"] = 0.80
    challenger.metrics["face_drift"] = 0.01
    report = TrialReport(champion=_arm("champion", champion=True))
    verdict, reason = report.recommendation(challenger)
    assert verdict is Verdict.FAIL
    assert "identity regressed" in reason


def test_a_challenger_that_only_ties_leaves_the_champion_standing():
    from sofia.reel.challenger import TrialReport

    report = TrialReport(champion=_arm("champion", champion=True))
    verdict, reason = report.recommendation(_arm("tie"))
    assert verdict is Verdict.HOLD
    assert "champion stands" in reason


def test_an_unmeasured_challenger_recommends_nothing():
    from sofia.reel.challenger import TrialReport

    challenger = _arm("unmeasured")
    challenger.metrics["phoneme_accuracy"] = None
    report = TrialReport(champion=_arm("champion", champion=True))
    verdict, _ = report.recommendation(challenger)
    assert verdict is Verdict.NOT_MEASURED


def test_a_challenger_that_crashed_on_a_shot_fails():
    from sofia.reel.challenger import TrialReport

    challenger = _arm("crashy")
    challenger.failures.append("shot 0: backend exploded")
    report = TrialReport(champion=_arm("champion", champion=True))
    assert report.recommendation(challenger)[0] is Verdict.FAIL


def test_an_unmeasured_champion_means_there_is_nothing_to_compare():
    from sofia.reel.challenger import TrialReport

    champ = _arm("champion", champion=True)
    champ.metrics["identity"] = None
    report = TrialReport(champion=champ)
    verdict, reason = report.recommendation(_arm("challenger"))
    assert verdict is Verdict.NOT_MEASURED
    assert "champion itself" in reason


def test_worst_case_across_shots_is_used_not_the_average():
    """One bad take must not be averaged away by good ones."""
    from pathlib import Path

    from sofia.reel.challenger import run_trial

    shots = [s for s in _shots() if s.shot_type.needs_lipsync]
    shots[0].video_path = "/dev/null"

    class Backend:
        name = "fake"

        def sync(self, video, audio, out):
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(b"x")
            return out

    calls = {"n": 0}

    def measure(path, shot):
        calls["n"] += 1
        # First shot good, second poor.
        value = 0.95 if calls["n"] == 1 else 0.60
        return {
            "phoneme_accuracy": value, "mouth_quality": value,
            "jaw_quality": value, "teeth_quality": value,
            "eye_quality": value, "identity": value, "face_drift": 0.02,
        }

    import tempfile

    workdir = Path(tempfile.mkdtemp())
    doubled = shots + [shots[0]]
    report = run_trial(
        Backend(), {}, doubled, {s.index: "/dev/null" for s in doubled}, workdir, measure
    )
    assert report.champion.metrics["phoneme_accuracy"] == pytest.approx(0.60)


# ---- growth feedback loop -------------------------------------------------
def test_shadow_outcomes_never_contaminate_real_baselines():
    engine = GrowthEngine()
    for i in range(5):
        engine.record_outcome(f"r{i}", "PASS", {"STORY": 8.0}, hook="hook")
    learned = engine.learned()
    assert learned["shadow_reels"] == 5
    assert learned["real_publications"] == 0
    assert learned["real_baselines"]["retention"]["value"] is None
    assert learned["evidence"] == "PREDICTED"
    assert "not any audience" in learned["caveat"]


def test_growth_learns_which_blockers_recur():
    engine = GrowthEngine()
    engine.record_outcome("r1", "HOLD", {}, blockers=["reel.voice", "reel.lipsync"])
    engine.record_outcome("r2", "HOLD", {}, blockers=["reel.voice"])
    assert list(engine.learned()["most_common_blockers"])[0] == "reel.voice"


def test_growth_observes_a_finished_reel():
    from sofia.core.gates import evaluate_gates
    from sofia.reel.contracts import ReelResult

    engine = GrowthEngine()
    brief = ReelBrief(
        reel_id="r1", purpose="p", audience="a", language=Language.RU,
        trend="honest process", hook="a hook", story_arc="arc", cta="cta",
    )
    result = ReelResult(
        reel_id="r1",
        verdict=Verdict.HOLD,
        stage=None,
        brief=brief,
        report=evaluate_gates([GateResult("reel.voice", Verdict.FAIL, True)]),
        scores={"STORY": 8.0, "IDENTITY": None},
    )
    entry = engine.observe(result)
    assert entry["hook"] == "a hook"
    assert entry["trend"] == "honest process"
    assert entry["blockers"] == ["reel.voice"]
    # Unmeasured scores are dropped, never recorded as 0.
    assert entry["scores"] == {"STORY": 8.0}
    assert engine.learned()["shadow_reels"] == 1


def test_challengers_are_told_apart_by_their_registered_name():
    """Challengers often share a runner class, so the backend's own name is
    the same string for all of them and cannot identify an arm."""
    from pathlib import Path
    import tempfile

    from sofia.reel.challenger import run_trial

    class SharedRunner:
        name = "latentsync-champion"  # every instance reports this

        def sync(self, video, audio, out):
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(b"x")
            return out

    shots = [s for s in _shots() if s.shot_type.needs_lipsync]

    def measure(path, shot):
        from sofia.reel.measurements import LIPSYNC_MEASUREMENTS

        return {m: 0.9 for m in LIPSYNC_MEASUREMENTS}

    report = run_trial(
        SharedRunner(),
        {"longcat": SharedRunner(), "highsync": SharedRunner()},
        shots,
        {s.index: "/dev/null" for s in shots},
        Path(tempfile.mkdtemp()),
        measure,
    )
    names = [c.name for c in report.challengers]
    assert names == ["longcat", "highsync"]
    assert all(c.backend == "latentsync-champion" for c in report.challengers)


def test_challenger_accepts_voice_clips_keyed_by_string():
    """ReelAssets.voice_clips is keyed by str(index); shots carry ints."""
    from pathlib import Path
    import tempfile

    from sofia.reel.challenger import run_trial
    from sofia.reel.measurements import LIPSYNC_MEASUREMENTS

    class Backend:
        name = "b"

        def sync(self, video, audio, out):
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(b"x")
            return out

    shots = [s for s in _shots() if s.shot_type.needs_lipsync]
    report = run_trial(
        Backend(), {}, shots,
        {str(s.index): "/dev/null" for s in shots},  # string keys
        Path(tempfile.mkdtemp()),
        lambda p, s: {m: 0.9 for m in LIPSYNC_MEASUREMENTS},
    )
    assert report.champion.failures == []
    assert report.champion.measured


def test_a_champion_that_crashed_on_shots_is_not_a_fair_baseline():
    from sofia.reel.challenger import TrialReport

    champ = _arm("champion", champion=True)
    champ.failures.append("shot 0: runner died")
    report = TrialReport(champion=champ)
    verdict, reason = report.recommendation(_arm("challenger"))
    assert verdict is Verdict.NOT_MEASURED
    assert "cherry-picked" in reason


def test_a_retried_reel_is_one_shadow_entry_not_several():
    engine = GrowthEngine()
    engine.record_outcome("r1", "HOLD", {}, blockers=["reel.voice"])
    engine.record_outcome("r1", "HOLD", {}, blockers=["reel.voice"])
    engine.record_outcome("r1", "PASS", {"STORY": 8.0}, hook="h")
    assert len(engine.memory.shadow) == 1
    assert engine.memory.shadow[0]["attempts"] == 3
    assert engine.memory.shadow[0]["verdict"] == "PASS"


def test_diagnostic_runs_are_separated_from_production_ones():
    engine = GrowthEngine()
    engine.record_outcome("r1", "PASS", {}, hook="real")
    engine.record_outcome("r2", "HOLD", {}, diagnostic=True)
    learned = engine.learned()
    assert learned["shadow_production_reels"] == 1
    assert learned["shadow_diagnostic_reels"] == 1
    # A diagnostic run can never pass, so it never supplies a winning hook.
    assert engine.hooks_that_reached_review() == ["real"]


def test_shadow_memory_survives_a_reload_and_stays_separate(tmp_path):
    engine = GrowthEngine()
    engine.record_outcome("r1", "PASS", {"STORY": 8.0}, hook="h")
    path = engine.memory.save(tmp_path / "history.json")

    reloaded = GrowthMemory.load(path)
    assert len(reloaded.shadow) == 1
    assert reloaded.records == []
    # A reload must never promote a shadow entry into a REAL baseline.
    assert reloaded.baseline("retention").value is None


def test_a_predicted_record_cannot_be_filed_as_a_real_publication():
    """``records`` is the REAL stream; a prediction there becomes a REAL baseline."""
    from sofia.core.verdict import Evidence
    from sofia.reel.growth import GrowthMemoryError, PublicationRecord

    with pytest.raises(GrowthMemoryError):
        GrowthMemory(
            records=[
                PublicationRecord(
                    content_id="c1",
                    permalink="",
                    hook="h",
                    format="reel",
                    published_at="2026-01-01",
                    metrics={"retention": 0.9},
                    evidence=Evidence.PREDICTED,
                )
            ]
        )


def test_a_publication_keeps_its_evidence_label_across_a_reload(tmp_path):
    """The label used to be dropped on save and assumed REAL on load."""
    from sofia.core.verdict import Evidence
    from sofia.reel.growth import PublicationRecord

    path = GrowthMemory(
        records=[
            PublicationRecord(
                content_id="c1",
                permalink="https://example/p",
                hook="h",
                format="reel",
                published_at="2026-01-01",
                metrics={"retention": 0.5},
            )
        ]
    ).save(tmp_path / "history.json")

    on_disk = json.loads(path.read_text(encoding="utf-8"))
    assert on_disk["records"][0]["evidence"] == Evidence.REAL.value

    # And a file that claims otherwise is refused rather than quietly upgraded.
    on_disk["records"][0]["evidence"] = Evidence.PREDICTED.value
    path.write_text(json.dumps(on_disk), encoding="utf-8")
    with pytest.raises(GrowthMemoryError):
        GrowthMemory.load(path)


def test_an_unreadable_history_is_an_error_not_an_empty_baseline(tmp_path):
    """A torn file must not read as "no publications" — that erases the baseline."""
    path = GrowthMemory(
        records=[
            PublicationRecord(
                content_id="c1",
                permalink="",
                hook="h",
                format="reel",
                published_at="2026-01-01",
                metrics={"retention": 0.5},
            )
        ]
    ).save(tmp_path / "history.json")

    full = path.read_text(encoding="utf-8")
    path.write_text(full[: len(full) // 2], encoding="utf-8")

    with pytest.raises(GrowthMemoryError):
        GrowthMemory.load(path)


def test_growth_offers_a_prior_winning_hook_when_none_is_supplied():
    engine = GrowthEngine()
    engine.record_outcome("r1", "PASS", {}, hook="Ты правда думаешь, что дело в камере?")
    brief = engine.brief_director(trend="t", audience="a", hook_hypothesis="")
    assert brief.hook_hypothesis == "Ты правда думаешь, что дело в камере?"


def test_an_explicit_hook_hypothesis_is_never_overridden():
    engine = GrowthEngine()
    engine.record_outcome("r1", "PASS", {}, hook="old hook")
    brief = engine.brief_director(trend="t", audience="a", hook_hypothesis="new idea")
    assert brief.hook_hypothesis == "new idea"


# ---- ffmpeg argument construction ----------------------------------------
def test_concat_entries_escape_quotes_and_refuse_newlines():
    """A concat list is a script, so a filename must not be able to rewrite it."""
    from pathlib import Path

    from sofia.core.errors import BackendUnavailableError
    from sofia.reel.backends import _concat_entry

    assert _concat_entry(Path("/a/b/reel.mp4")) == "file '/a/b/reel.mp4'"
    # The format's own escape: close, escaped quote, reopen.
    assert _concat_entry(Path("/a/it's/reel.mp4")) == "file '/a/it'\\''s/reel.mp4'"
    with pytest.raises(BackendUnavailableError):
        _concat_entry(Path("/a/b\nfile '/etc/passwd'\nc.mp4"))


def test_filter_paths_escape_every_filtergraph_separator():
    from sofia.reel.backends import _escape_filter_path

    escaped = _escape_filter_path("/a/b,c;d[e]:f'g/subs.ass")
    for special in ",;[]:'":
        assert f"\\{special}" in escaped
    # A comma must not be able to start a second filter.
    assert ",subtitles" not in escaped.replace("\\,", "")


def test_reel_artifact_paths_are_sanitised(tmp_path):
    """reel_id reaches nine filesystem paths; checkpoints already sanitise it."""
    from sofia.reel.director import ReelDirector

    slug = ReelDirector._slug("../../../../etc/cron.d/x")
    assert "/" not in slug
    assert ReelDirector._slug("..") == "reel"
    assert ReelDirector._slug("sofia-reel-001") == "sofia-reel-001"


# ---- editing QA ----------------------------------------------------------
def _ppm(path, width=54, height=96, fill=(190, 160, 130), noise=True):
    """Write a small binary PPM standing in for a real frame.

    A smooth vertical gradient with light grain, because real footage is not
    per-pixel white noise: noise at that amplitude genuinely is a texture that
    swallows overlaid text, and the cover gate is right to say so.
    """
    import random

    rng = random.Random(3)
    rows = []
    for y in range(height):
        # Gradient gives tonal range without per-pixel edges.
        shade = 1.0 - 0.88 * (y / max(1, height - 1))
        row = bytearray()
        for _ in range(width):
            r, g, b = (int(c * shade) for c in fill)
            if noise:
                n = rng.randint(-5, 5)
                r, g, b = (max(0, min(255, c + n)) for c in (r, g, b))
            row += bytes((r, g, b))
        rows.append(bytes(row))
    path.write_bytes(f"P6\n{width} {height}\n255\n".encode() + b"".join(rows))
    return path


class _StubEditor:
    """An editor that hands back a prepared frame."""

    def __init__(self, frame_path):
        self.frame_path = frame_path

    def extract_frame(self, video, at_s, out_path):
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(self.frame_path.read_bytes())
        return out_path


def test_frame_analysis_reads_a_real_ppm(tmp_path):
    from sofia.reel.frames import analyse_frame

    stats = analyse_frame(_ppm(tmp_path / "f.ppm"))
    assert stats.width == 54 and stats.height == 96
    assert 0.0 < stats.brightness < 1.0
    assert stats.sharpness > 0
    assert not stats.is_black_frame


def test_a_black_opening_frame_is_caught(tmp_path):
    from sofia.reel.frames import analyse_frame

    stats = analyse_frame(_ppm(tmp_path / "b.ppm", fill=(0, 0, 0), noise=False))
    assert stats.is_black_frame
    assert stats.is_flat


def test_edit_gate_fails_on_a_black_first_frame(tmp_path):
    from sofia.reel.critics import EditorCritic

    final = tmp_path / "reel.mp4"
    final.write_bytes(b"x")
    editor = _StubEditor(_ppm(tmp_path / "black.ppm", fill=(0, 0, 0), noise=False))
    outcome = EditorCritic().review(
        final_path=str(final), shots=_shots(), mix_path=None,
        editor=editor, workdir=tmp_path,
    )
    assert outcome.result.verdict in (Verdict.FAIL, Verdict.NOT_MEASURED)
    detail = outcome.result.measurement.detail
    assert any("black frame" in m for m in detail["first_frame"])


def test_edit_gate_fails_on_a_horizontal_delivery(tmp_path):
    from sofia.reel.critics import EditorCritic

    final = tmp_path / "reel.mp4"
    final.write_bytes(b"x")
    editor = _StubEditor(_ppm(tmp_path / "wide.ppm", width=96, height=54))
    outcome = EditorCritic().review(
        final_path=str(final), shots=_shots(), mix_path=None,
        editor=editor, workdir=tmp_path,
    )
    detail = outcome.result.measurement.detail
    assert any("must be vertical" in m for m in detail["framing"])


def test_edit_gate_flags_dead_air_in_the_real_mix(tmp_path):
    import math

    from sofia.reel.critics import EditorCritic
    from sofia.voice.audio import write_wav

    rate = 22050
    samples = []
    for i in range(int(rate * 5.0)):
        t = i / rate
        # Two seconds of silence in the middle of the programme.
        env = 0.0 if 1.5 < t < 3.5 else 0.3
        samples.append(env * math.sin(2 * math.pi * 200 * t))
    mix = write_wav(tmp_path / "mix.wav", samples, rate)

    final = tmp_path / "reel.mp4"
    final.write_bytes(b"x")
    outcome = EditorCritic().review(
        final_path=str(final), shots=_shots(), mix_path=str(mix),
        editor=_StubEditor(_ppm(tmp_path / "ok.ppm")), workdir=tmp_path,
    )
    assert outcome.result.verdict is Verdict.FAIL
    assert any("dead air" in m for m in outcome.result.measurement.detail["dead_time"])


def test_edit_gate_flags_a_reel_that_drags_on_one_shot():
    from sofia.reel.edit_qa import EditIssues, EditThresholds, check_pacing

    shots = _shots()
    shots[2].duration_s = 40.0  # one shot swallows the reel
    issues = EditIssues()
    check_pacing(shots, EditThresholds(), issues)
    assert any("drags on one image" in m for m in issues.pacing)


def test_edit_gate_flags_a_slow_hook():
    from sofia.reel.edit_qa import EditIssues, EditThresholds, check_pacing

    shots = _shots()
    shots[0].duration_s = 7.0
    issues = EditIssues()
    check_pacing(shots, EditThresholds(), issues)
    assert any("hook must land" in m for m in issues.pacing)


def test_edit_gate_flags_too_few_shots():
    from sofia.reel.edit_qa import EditIssues, EditThresholds, check_pacing

    issues = EditIssues()
    check_pacing(_shots()[:2], EditThresholds(), issues)
    assert any("at least" in m for m in issues.pacing)


def test_a_missing_edit_blocks_rather_than_passing(tmp_path):
    from sofia.reel.critics import EditorCritic

    outcome = EditorCritic().review(
        final_path=None, shots=_shots(), mix_path=None,
        editor=_StubEditor(_ppm(tmp_path / "f.ppm")), workdir=tmp_path,
    )
    assert outcome.result.blocking


def test_beat_sync_is_reported_but_never_fatal():
    from sofia.reel.edit_qa import EditIssues, EditThresholds, check_beat_sync

    issues = EditIssues()
    check_beat_sync(_shots(), 96.0, EditThresholds(), issues)
    # It lands in advisory, which is excluded from blocking.
    assert issues.advisory or "cuts_on_beat" in issues.measurements
    assert issues.blocking == []


def test_unknown_tempo_does_not_invent_a_beat_score():
    from sofia.reel.edit_qa import EditIssues, EditThresholds, check_beat_sync

    issues = EditIssues()
    check_beat_sync(_shots(), None, EditThresholds(), issues)
    assert "cuts_on_beat" not in issues.measurements
    assert any("tempo unknown" in m for m in issues.advisory)


def test_cut_points_and_beat_grid_line_up():
    from sofia.reel.edit_qa import beat_grid, cut_points

    shots = _shots()
    cuts = cut_points(shots)
    assert len(cuts) == len(shots) - 1
    assert cuts[0] == pytest.approx(shots[0].duration_s)
    grid = beat_grid(120.0, 2.0)
    assert grid == [0.0, 0.5, 1.0, 1.5, 2.0]


# ---- cover QA ------------------------------------------------------------
def test_a_black_cover_fails_even_with_no_face_model(tmp_path):
    """Composition is a known-bad answer, so it outranks 'not measured'."""
    from sofia.reel.critics import CoverCritic

    jpg = tmp_path / "cover.jpg"
    jpg.write_bytes(b"x")
    ppm = _ppm(tmp_path / "cover.ppm", fill=(0, 0, 0), noise=False)
    outcome = CoverCritic().review(str(jpg), {}, cover_ppm=str(ppm))
    assert outcome.result.verdict is Verdict.FAIL
    assert "black" in outcome.result.reason


def test_a_horizontal_cover_fails():
    from sofia.reel.cover_qa import analyse_cover
    import tempfile
    from pathlib import Path as _P

    tmp = _P(tempfile.mkdtemp())
    issues = analyse_cover(str(_ppm(tmp / "wide.ppm", width=96, height=54)), {})
    assert any("must be vertical" in m for m in issues.composition)


def test_a_busy_text_band_is_flagged(tmp_path):
    """Text over a noisy band will not read, whatever the face score says."""
    import random

    from sofia.reel.cover_qa import analyse_cover

    # Calm top, violently noisy band where the hook text would sit.
    rng = random.Random(1)
    width, height = 54, 96
    rows = []
    for y in range(height):
        row = bytearray()
        busy = 0.60 <= y / height <= 0.82
        for _ in range(width):
            if busy:
                v = rng.choice((0, 255))
                row += bytes((v, v, v))
            else:
                row += bytes((120, 100, 80))
        rows.append(bytes(row))
    path = tmp_path / "busy.ppm"
    path.write_bytes(f"P6\n{width} {height}\n255\n".encode() + b"".join(rows))

    issues = analyse_cover(str(path), {})
    assert any("will not read" in m for m in issues.composition)


def test_cover_composition_passes_but_identity_still_blocks(tmp_path):
    from sofia.reel.critics import CoverCritic

    jpg = tmp_path / "c.jpg"
    jpg.write_bytes(b"x")
    ppm = _ppm(tmp_path / "c.ppm")
    outcome = CoverCritic().review(str(jpg), {}, cover_ppm=str(ppm))
    assert outcome.result.verdict is Verdict.NOT_MEASURED
    assert outcome.result.blocking
    detail = outcome.result.measurement.detail
    # Composition really was measured, even though the gate blocks.
    assert detail["measurements"]["contrast"] > 0
    assert "aspect_ratio" in detail["measurements"]


def test_a_cover_with_every_metric_supplied_can_pass(tmp_path):
    from sofia.reel.critics import CoverCritic

    jpg = tmp_path / "c.jpg"
    jpg.write_bytes(b"x")
    ppm = _ppm(tmp_path / "c.ppm")
    outcome = CoverCritic().review(
        str(jpg),
        {"face_present": 1.0, "face_identity": 0.88, "brand_consistency": 0.82},
        cover_ppm=str(ppm),
    )
    assert outcome.result.verdict is Verdict.PASS
    assert outcome.result.measurement.value == pytest.approx(0.88)


def test_a_weak_supplied_identity_fails_the_cover(tmp_path):
    from sofia.reel.critics import CoverCritic

    jpg = tmp_path / "c.jpg"
    jpg.write_bytes(b"x")
    ppm = _ppm(tmp_path / "c.ppm")
    outcome = CoverCritic().review(
        str(jpg),
        {"face_present": 1.0, "face_identity": 0.40, "brand_consistency": 0.9},
        cover_ppm=str(ppm),
    )
    assert outcome.result.verdict is Verdict.FAIL


# ---- SFX -----------------------------------------------------------------
def _quiet_wav(path, amp=0.05, seconds=0.5):
    import math

    from sofia.voice.audio import write_wav

    rate = 22050
    return write_wav(
        path,
        [amp * math.sin(2 * math.pi * 400 * i / rate) for i in range(int(rate * seconds))],
        rate,
    )


def _mix_stems(tmp_path, *, bed_under_speech=0.02, bed_in_gaps=0.05):
    """A programme shaped like a real one: speech, pauses, and a bed.

    The music *stem* is always the raw bed at full level — that is what the
    mixer is handed. What changes between cases is the delivered mix: how much
    of that bed it actually leaves under the speech and between the phrases.
    """
    import math

    from sofia.voice.audio import write_wav

    rate = 22050
    raw_bed = 0.16
    voice, music, mix = [], [], []
    for i in range(int(rate * 6.0)):
        t = i / rate
        speaking = (t % 1.5) < 1.0
        v = 0.20 * math.sin(2 * math.pi * 200 * t) if speaking else 0.0
        bed = math.sin(2 * math.pi * 400 * t)
        level = bed_under_speech if speaking else bed_in_gaps
        voice.append(v)
        music.append(raw_bed * bed)
        mix.append(max(-1.0, min(1.0, v + level * bed)))
    tmp_path.mkdir(parents=True, exist_ok=True)
    return (
        str(write_wav(tmp_path / "v.wav", voice, rate)),
        str(write_wav(tmp_path / "m.wav", music, rate)),
        str(write_wav(tmp_path / "mix.wav", mix, rate)),
    )


def test_no_sfx_is_not_a_gap(tmp_path):
    """The brief asks for SFX only where they strengthen a scene."""
    voice, music, mix = _mix_stems(tmp_path)
    outcome = AudioMixCritic(ReelThresholds()).review(
        voice_stem=voice, music_stem=music, final_mix=mix, sfx=()
    )
    assert outcome.result.verdict is Verdict.PASS


def test_a_declared_sfx_that_does_not_exist_fails(tmp_path):
    voice, music, mix = _mix_stems(tmp_path)
    outcome = AudioMixCritic(ReelThresholds()).review(
        voice_stem=voice, music_stem=music, final_mix=mix,
        sfx=(str(tmp_path / "missing.wav"),),
    )
    assert outcome.result.verdict is Verdict.FAIL
    assert "does not exist" in outcome.result.reason


def test_an_sfx_louder_than_the_ceiling_fails(tmp_path):
    voice, music, mix = _mix_stems(tmp_path)
    loud = _quiet_wav(tmp_path / "bang.wav", amp=0.999)
    outcome = AudioMixCritic(ReelThresholds()).review(
        voice_stem=voice, music_stem=music, final_mix=mix, sfx=(str(loud),)
    )
    assert outcome.result.verdict is Verdict.FAIL
    assert "SFX peaks" in outcome.result.reason


def test_a_well_behaved_sfx_passes(tmp_path):
    voice, music, mix = _mix_stems(tmp_path)
    cue = _quiet_wav(tmp_path / "tick.wav", amp=0.10)
    outcome = AudioMixCritic(ReelThresholds()).review(
        voice_stem=voice, music_stem=music, final_mix=mix, sfx=(str(cue),)
    )
    assert outcome.result.verdict is Verdict.PASS


# ---- scorecard and the world-class claim ---------------------------------
def _passing_report():
    from sofia.core.gates import evaluate_gates

    return evaluate_gates(
        [GateResult(name, Verdict.PASS, True) for name in FINAL_GATE_CATEGORIES],
        required_critical=FINAL_GATE_CATEGORIES,
    )


def test_passing_every_gate_is_not_a_claim_to_be_world_class():
    """No defect found is a weaker statement than 8+/10 in every category.

    Hook strength and retention are audience outcomes. Nothing here can measure
    them while publishing is on HOLD, so the claim stays NOT_MEASURED however
    clean the gates are.
    """
    from sofia.reel.scorecard import score_categories, world_class

    scores = score_categories(_passing_report())
    assert scores["STORY"] == 8.0
    assert scores["HOOK"] is None and scores["RETENTION"] is None

    claim = world_class(scores, ReelThresholds())
    assert claim["world_class"] is False
    assert claim["verdict"] == Verdict.NOT_MEASURED.value
    assert sorted(claim["not_measured"]) == ["HOOK", "RETENTION"]
    assert "publishing is on HOLD" in claim["why_not_measurable"]["RETENTION"]


def test_a_measured_category_below_the_floor_outranks_an_unmeasured_one():
    """A known defect is a stronger finding than an unknown."""
    from sofia.reel.scorecard import world_class

    claim = world_class(
        {"STORY": 4.0, "IDENTITY": 8.0, "VOICE": None, "HOOK": None},
        ReelThresholds(),
    )
    assert claim["verdict"] == Verdict.FAIL.value
    assert claim["below_floor"] == ["STORY=4.0 (floor 8.0)"]


def test_world_class_is_claimable_only_with_every_category_measured():
    """The floors are the brief's, and they are enforced, not merely declared."""
    from sofia.reel.scorecard import (
        AUDIENCE_CATEGORIES,
        LOCAL_CATEGORIES,
        world_class,
    )

    scores = {label: 8.0 for label in LOCAL_CATEGORIES}
    scores.update({label: 8.0 for label in AUDIENCE_CATEGORIES})
    assert world_class(scores, ReelThresholds())["world_class"] is True

    scores["HOOK"] = 7.9
    claim = world_class(scores, ReelThresholds())
    assert claim["world_class"] is False
    assert claim["below_floor"] == ["HOOK=7.9 (floor 8.0)"]


def test_the_overall_score_survives_the_two_unmeasurable_categories():
    """OVERALL averages what was measured locally; it is not dragged to None."""
    from sofia.reel.scorecard import score_categories

    assert score_categories(_passing_report())["OVERALL"] == 8.0


# ---- the GPU rule applies to experiments too -----------------------------
def test_a_trial_waits_for_production_instead_of_competing_with_it():
    """A Champion/Challenger trial is exactly the heavy experiment that waits.

    ``run_trial`` rendered every arm without asking the arbiter at all, so on
    the studio machine a benchmark would have taken the GPU out from under a
    production render.
    """
    import tempfile
    from pathlib import Path

    from sofia.reel.challenger import run_trial

    class Backend:
        name = "fake"

        def sync(self, video, audio, out):  # pragma: no cover - must not run
            raise AssertionError("a trial started while production held the GPU")

    class BusyGpu:
        def __init__(self):
            self.asked = 0

        def wait_for(self, work, *, vram_gb=0.0, timeout_s=0.0, poll_s=15.0):
            self.asked += 1
            assert work is WorkClass.HEAVY
            return False, "production holds the GPU (gpu_render); heavy work waits"

    shots = [s for s in _shots() if s.shot_type.needs_lipsync]
    gpu = BusyGpu()
    report = run_trial(
        Backend(),
        {"challenger": Backend()},
        shots,
        {s.index: "/dev/null" for s in shots},
        Path(tempfile.mkdtemp()),
        lambda path, shot: {},
        gpu=gpu,
    )

    assert gpu.asked == 2 * len(shots)
    assert report.champion.failures and "production holds the GPU" in report.champion.failures[0]
    # A starved trial measures nothing, so it can never recommend a promotion.
    verdict, _ = report.recommendation(report.challengers[0])
    assert verdict is Verdict.NOT_MEASURED


def test_a_trial_with_no_arbiter_still_runs():
    """The arbiter is opt-in: tests and offline analysis do not need a GPU."""
    import tempfile
    from pathlib import Path

    from sofia.reel.challenger import run_trial

    class Backend:
        name = "fake"

        def sync(self, video, audio, out):
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(b"x")
            return out

    shots = [s for s in _shots() if s.shot_type.needs_lipsync][:1]
    report = run_trial(
        Backend(), {}, shots, {s.index: "/dev/null" for s in shots},
        Path(tempfile.mkdtemp()), lambda path, shot: {"identity": 0.9},
    )
    assert report.champion.failures == []


def test_a_reel_that_opens_on_silence_is_a_late_hook(tmp_path):
    """The pause statistics skip leading silence, so nothing saw this before.

    ``check_pacing`` only knows when the first *cut* lands. A Reel could open on
    two silent seconds — the worst place in short form to spend them — and pass
    both the hook check and the dead-air check.
    """
    import math

    from sofia.reel.edit_qa import EditIssues, EditThresholds, check_dead_time
    from sofia.voice.audio import write_wav

    rate = 22050

    def mix(lead_s: float, name: str) -> str:
        samples = []
        for i in range(int(rate * 5.0)):
            t = i / rate
            env = 0.0 if t < lead_s else 0.3
            samples.append(env * math.sin(2 * math.pi * 200 * t))
        return str(write_wav(tmp_path / name, samples, rate))

    late = EditIssues()
    check_dead_time(mix(2.0, "late.wav"), EditThresholds(), late)
    assert late.measurements["silence_before_speech_s"] == pytest.approx(2.0, abs=0.05)
    assert any("before the first word" in m for m in late.dead_time)
    # It is not counted twice: the silence is at the head, not inside the mix.
    assert not any("dead air in the mix" in m for m in late.dead_time)

    prompt = EditIssues()
    check_dead_time(mix(0.2, "prompt.wav"), EditThresholds(), prompt)
    assert prompt.dead_time == []


def test_an_edit_that_lost_a_shot_is_caught_by_the_delivered_runtime():
    """Pacing reasons from the shot list; the file is what people watch.

    A Reel that loses one shot in assembly is still inside the allowed
    15–30 s, so the decode gate passes it, and every pacing number then
    describes a programme that was never assembled.
    """
    from sofia.reel.edit_qa import EditIssues, EditThresholds, check_runtime

    shots = _shots()
    planned = sum(s.duration_s for s in shots)

    intact = EditIssues()
    check_runtime(shots, planned, EditThresholds(), intact)
    assert intact.pacing == []
    assert intact.measurements["runtime_drift_s"] == 0.0

    lost = EditIssues()
    check_runtime(shots, planned - shots[2].duration_s, EditThresholds(), lost)
    assert any("did not assemble the programme" in m for m in lost.pacing)

    unknown = EditIssues()
    check_runtime(shots, None, EditThresholds(), unknown)
    assert unknown.pacing == []
    assert any("could not be read" in m for m in unknown.not_measured)


def test_subtitles_are_checked_against_the_delivered_video_not_the_plan(tmp_path):
    """An unknown runtime used to skip the overrun check in silence."""
    from sofia.reel.subtitles import Cue, verify_cues

    cues = [Cue(1, 0.0, 3.0, ["раз два три"])]
    known = verify_cues(
        cues, spoken_text="раз два три", language=Language.RU, video_duration_s=2.0
    )
    assert any("past the" in m for m in known.timing)

    unknown = verify_cues(cues, spoken_text="раз два три", language=Language.RU)
    assert unknown.timing == []
    assert unknown.not_measured, "a skipped check must not read as a clean track"
    assert unknown.ok is False


def test_a_challenger_is_held_to_every_metric_the_gate_holds_the_champion_to():
    """The trial's metric list had drifted from the gate's and lost A/V sync.

    "A challenger must be measured on every metric the champion is held to" was
    the comment above a hand-maintained copy that was missing ``av_offset_ms``.
    A challenger with perfect mouth shapes at the wrong time measured clean.
    """
    from sofia.reel.challenger import REQUIRED_METRICS, TrialReport
    from sofia.reel.critics import LipSyncCritic

    assert set(REQUIRED_METRICS) == set(LipSyncCritic.REQUIRED)
    assert "av_offset_ms" in REQUIRED_METRICS

    deaf = _arm("challenger")
    deaf.metrics["av_offset_ms"] = None
    report = TrialReport(champion=_arm("champion", champion=True), challengers=[deaf])
    assert deaf.measured is False
    verdict, reason = report.recommendation(deaf)
    assert verdict is Verdict.NOT_MEASURED
    assert "av_offset_ms" in reason


def test_late_audio_is_a_regression_even_with_a_better_mouth():
    """``av_offset_ms`` is lower-is-better, so a bigger offset must not win."""
    from sofia.reel.challenger import TrialReport

    champion = _arm("champion", champion=True)
    late = _arm("challenger", phoneme_accuracy=0.99, mouth_quality=0.99)
    late.metrics["av_offset_ms"] = 120.0  # champion is at 40 ms

    report = TrialReport(champion=champion, challengers=[late])
    assert report.comparison(late)["av_offset_ms"] == "LOSS"
    verdict, reason = report.recommendation(late)
    assert verdict is Verdict.FAIL
    assert "av_offset_ms" in reason


def test_a_voice_clip_that_overruns_its_slot_plays_over_the_next_one():
    """Clips are summed onto the timeline, so an overrun is two voices at once.

    Nothing else would see it: it is not dead air, every word is still in the
    subtitles, and the mix level looks normal.
    """
    from sofia.reel.edit_qa import EditIssues, EditThresholds, check_voice_timeline

    # shot 0 gets 3s and returns 4.1s of speech; shot 1 starts at 3s.
    spans = [("shot0.wav", 0.0, 4.1), ("shot1.wav", 3.0, 2.5)]
    issues = EditIssues()
    check_voice_timeline(spans, 10.0, EditThresholds(), issues)
    assert any("two voices play at once" in m for m in issues.voice_timeline)
    assert issues.blocking

    fitting = EditIssues()
    check_voice_timeline(
        [("shot0.wav", 0.0, 2.9), ("shot1.wav", 3.0, 2.5)],
        10.0,
        EditThresholds(),
        fitting,
    )
    assert fitting.voice_timeline == []


def test_speech_running_past_the_end_of_the_reel_is_caught():
    from sofia.reel.edit_qa import EditIssues, EditThresholds, check_voice_timeline

    issues = EditIssues()
    check_voice_timeline([("last.wav", 18.0, 5.0)], 21.5, EditThresholds(), issues)
    assert any("past the end" in m for m in issues.voice_timeline)


def test_unreported_voice_placement_is_not_a_clean_timeline():
    from sofia.reel.edit_qa import EditIssues, EditThresholds, check_voice_timeline

    issues = EditIssues()
    check_voice_timeline(None, 21.5, EditThresholds(), issues)
    assert issues.voice_timeline == []
    assert any("could not be ruled out" in m for m in issues.not_measured)


def test_spoken_lines_with_nothing_placed_is_not_a_clean_timeline():
    from sofia.reel.edit_qa import EditIssues, EditThresholds, check_voice_timeline

    issues = EditIssues()
    check_voice_timeline([], 21.5, EditThresholds(), issues, _shots())
    assert any("could not be ruled out" in m for m in issues.not_measured)

    silent = EditIssues()
    quiet_shots = _shots()
    for shot in quiet_shots:
        shot.voice_line = ""
    check_voice_timeline([], 21.5, EditThresholds(), silent, quiet_shots)
    assert silent.not_measured == []
