"""Reel team: shot routing, story structure, subtitles, mix, repair, gates."""

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
from sofia.reel.growth import GrowthEngine, GrowthMemory
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
    import math

    from sofia.voice.audio import write_wav

    def tone(name, amp):
        return write_wav(
            tmp_path / name,
            [amp * math.sin(2 * math.pi * 200 * i / 22050) for i in range(22050)],
            22050,
        )

    voice = tone("v.wav", 0.10)
    music = tone("mu.wav", 0.09)  # only ~1 dB below the voice
    mix = tone("mix.wav", 0.18)
    outcome = AudioMixCritic(ReelThresholds()).review(
        voice_stem=str(voice), music_stem=str(music), final_mix=str(mix)
    )
    assert outcome.result.verdict is Verdict.FAIL
    assert "ducking" in outcome.result.reason


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
