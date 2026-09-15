"""Voice Team: measurement, fail-closed verdicts and targeted repair."""

import math

import pytest

from sofia.core.errors import BackendUnavailableError
from sofia.core.verdict import Verdict
from sofia.voice import text as T
from sofia.voice.audio import analyse_wav, write_wav
from sofia.voice.backends import VoiceBackends, Voiceprint
from sofia.voice.contracts import (
    Emotion,
    Language,
    Pace,
    RepairScope,
    VoiceDefect,
    VoiceDiagnosis,
)
from sofia.voice.corpus import CORPUS, coverage
from sofia.voice.critics import ProsodyCritic, VoiceThresholds
from sofia.voice.director import VoiceDirector
from sofia.voice.pipeline import VoiceTeam
from sofia.voice.repair import VoiceRepairAgent


# ---- text / WER ----------------------------------------------------------
def test_wer_is_zero_when_numbers_are_spoken_out():
    a = T.word_error_rate("Это заняло 25 минут", "Это заняло двадцать пять минут", Language.RU)
    assert a.wer == 0.0


def test_wer_localises_the_bad_word():
    a = T.word_error_rate("двадцать пять минут", "двадцать девять минут", Language.RU)
    assert a.bad_words() == ["пять"]
    assert a.wer == pytest.approx(1 / 3)


def test_stress_marks_are_normalised_away():
    assert T.normalize("зво́нит") == "звонит"


def test_dropped_number_is_caught():
    c = T.check_content_preserved("Скидка 40% сегодня", "Скидка сегодня", Language.RU)
    assert c.missing_numbers == ("40%",)
    assert not c.ok


def test_correct_transliteration_is_not_a_missing_name():
    c = T.check_content_preserved(
        "Это Sofia", "Это Софи", Language.RU, aliases={"Sofia": "Софи"}
    )
    assert c.ok


def test_wrong_language_is_detected():
    assert "Latin" in T.language_mismatch("Привет всем", "Privet vsem", Language.RU)
    assert T.language_mismatch("Привет всем", "Привет всем", Language.RU) == ""


def test_ua_clip_read_by_a_russian_voice_is_detected():
    assert T.language_mismatch("Привіт усім", "Привэт всым", Language.UA)


# ---- audio ---------------------------------------------------------------
def _tone(path, duration=3.0, rate=22050, pause=(1.0, 1.4), amp=0.35):
    samples = []
    for i in range(int(rate * duration)):
        t = i / rate
        env = 0.0 if pause[0] < t < pause[1] else amp * (1 + 0.9 * math.sin(2 * math.pi * 4.5 * t))
        samples.append(env * math.sin(2 * math.pi * 180 * t))
    return write_wav(path, samples, rate)


def test_audio_analysis_finds_real_pauses(tmp_path):
    stats = analyse_wav(_tone(tmp_path / "a.wav"))
    assert stats.duration_s == pytest.approx(3.0, abs=0.05)
    assert stats.pause_count >= 1
    assert stats.longest_pause_s == pytest.approx(0.4, abs=0.1)
    assert not stats.clipping


def test_clipping_is_detected(tmp_path):
    samples = [0.999 if i % 2 else -0.999 for i in range(22050)]
    stats = analyse_wav(write_wav(tmp_path / "c.wav", samples, 22050))
    assert stats.clipping


def test_empty_or_missing_audio_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        analyse_wav(tmp_path / "nope.wav")
    (tmp_path / "empty.wav").write_bytes(b"")
    with pytest.raises(ValueError):
        analyse_wav(tmp_path / "empty.wav")


def test_prosody_critic_flags_dead_air(tmp_path):
    from sofia.voice.contracts import VoiceArtifact, VoiceBrief

    path = _tone(tmp_path / "gap.wav", duration=4.0, pause=(1.0, 3.0))
    brief = VoiceBrief(language=Language.RU, text="раз два три", pace=Pace.NATURAL)
    artifact = VoiceArtifact(brief=brief, audio_path=str(path), backend="test")
    critic = ProsodyCritic(VoiceBackends.unavailable("n/a"), VoiceThresholds())
    outcome = critic.review(artifact)
    assert outcome.result.verdict is Verdict.FAIL
    assert any(d.defect is VoiceDefect.BAD_PAUSES for d in outcome.diagnoses)


def test_prosody_critic_blocks_when_audio_is_missing():
    from sofia.voice.contracts import VoiceArtifact, VoiceBrief

    artifact = VoiceArtifact(
        brief=VoiceBrief(language=Language.RU, text="x"), audio_path=None, backend="t"
    )
    outcome = ProsodyCritic(
        VoiceBackends.unavailable("n/a"), VoiceThresholds()
    ).review(artifact)
    assert outcome.result.verdict is Verdict.MISSING
    assert outcome.result.blocking


# ---- identity ------------------------------------------------------------
def test_generic_fallback_voice_is_not_sofia():
    vp = Voiceprint(speaker="sofia", language=Language.UA)
    assert vp.is_generic_fallback


def test_identity_critic_fails_without_a_sofia_voiceprint(tmp_path):
    from sofia.voice.contracts import VoiceArtifact, VoiceBrief
    from sofia.voice.critics import VoiceIdentityCritic

    backends = VoiceBackends.unavailable("no models here")
    artifact = VoiceArtifact(
        brief=VoiceBrief(language=Language.UA, text="Привіт"),
        audio_path=str(_tone(tmp_path / "v.wav")),
        backend="t",
    )
    outcome = VoiceIdentityCritic(backends, VoiceThresholds()).review(artifact)
    assert outcome.result.verdict is Verdict.FAIL
    assert "not Sofia" in outcome.result.reason
    assert outcome.diagnoses[0].defect is VoiceDefect.IDENTITY_DRIFT


# ---- pipeline ------------------------------------------------------------
def test_pipeline_blocks_when_tts_is_unavailable(tmp_path):
    team = VoiceTeam(VoiceBackends.unavailable("no TTS"), tmp_path)
    verdict = team.speak("Привет", Language.RU, clip_id="c1")
    assert verdict.verdict is Verdict.BLOCKED
    assert verdict.artifact is None


def test_readiness_reports_every_blocker(tmp_path):
    team = VoiceTeam(VoiceBackends.unavailable("nothing installed"), tmp_path)
    readiness = team.readiness()["languages"]
    for lang in ("RU", "UA", "EN"):
        assert readiness[lang]["can_generate"] is False
        assert readiness[lang]["can_verify"] is False
        assert readiness[lang]["blockers"]


# ---- director + repair ---------------------------------------------------
def test_director_maps_scene_to_delivery():
    brief = VoiceDirector().brief("Смотри!", Language.RU, scene="hook")
    assert brief.emotion is Emotion.EXCITED and brief.pace is Pace.FAST


def test_director_only_pins_lexicon_entries_that_occur():
    brief = VoiceDirector().brief("Меня зовут Sofia", Language.RU)
    assert brief.lexicon == {"Sofia": "Софи"}


def test_repair_spells_a_number_and_touches_nothing_else():
    brief = VoiceDirector().brief("Это заняло 25 минут", Language.RU)
    plan = VoiceRepairAgent().plan(
        brief, [VoiceDiagnosis(VoiceDefect.NUMBER_READING, "25")]
    )
    assert "двадцать пять" in plan.brief.text
    assert plan.brief.emotion is brief.emotion
    assert plan.scope is RepairScope.PHRASE


def test_repair_of_robotic_delivery_changes_prosody_not_text():
    brief = VoiceDirector().brief("Помогла тишина.", Language.RU)
    plan = VoiceRepairAgent().plan(brief, [VoiceDiagnosis(VoiceDefect.ROBOTIC)])
    assert plan.brief.text == brief.text
    assert plan.scope is RepairScope.PROSODY


def test_unmeasurable_defect_is_not_repairable():
    brief = VoiceDirector().brief("Привет", Language.RU)
    plan = VoiceRepairAgent().plan(brief, [VoiceDiagnosis(VoiceDefect.NOT_MEASURED)])
    assert not plan.actionable
    assert plan.unrepairable


# ---- corpus --------------------------------------------------------------
@pytest.mark.parametrize("language", list(Language))
def test_each_language_has_a_representative_corpus(language):
    cov = coverage(language)
    assert cov["clips"] >= 20
    assert set(cov["lengths"]) == {"short", "medium", "long"}
    assert len(cov["emotions"]) >= 5
    assert {"numbers", "names", "borrowed"} <= set(cov["hard_cases"])


@pytest.mark.parametrize("language", list(Language))
def test_corpus_clip_ids_are_unique(language):
    ids = [c.clip_id for c in CORPUS[language]]
    assert len(ids) == len(set(ids))


# ---- benchmark honesty ---------------------------------------------------
def test_a_campaign_with_no_verifiers_reports_no_rates(tmp_path):
    """A batch where nothing could be measured must not read as ``0%``."""
    from sofia.voice.benchmark import CampaignReport, ClipOutcome
    from sofia.voice.corpus import corpus_for

    report = CampaignReport(language=Language.RU)
    for clip in corpus_for(Language.RU):
        report.outcomes.append(
            ClipOutcome(
                clip=clip,
                verdict=Verdict.HOLD,
                reason="identity and pronunciation unverifiable",
                repairs=2,
                audio_path=str(tmp_path / f"{clip.clip_id}.wav"),
                wer=None,
                identity=None,
            )
        )
    assert report.produced >= 20
    assert report.verified == 0
    assert not report.measurable
    assert report.first_pass_rate is None
    assert report.final_pass_rate is None
    assert report.verdict is Verdict.NOT_MEASURED


def test_a_campaign_with_real_measurements_reports_rates(tmp_path):
    from sofia.voice.benchmark import CampaignReport, ClipOutcome
    from sofia.voice.corpus import corpus_for

    report = CampaignReport(language=Language.RU)
    for i, clip in enumerate(corpus_for(Language.RU)):
        report.outcomes.append(
            ClipOutcome(
                clip=clip,
                verdict=Verdict.PASS if i % 2 == 0 else Verdict.FAIL,
                reason="",
                repairs=0,
                audio_path=str(tmp_path / f"{clip.clip_id}.wav"),
                wer=0.03,
                identity=0.9,
            )
        )
    assert report.measurable
    assert report.final_pass_rate == pytest.approx(
        report.count(Verdict.PASS) / report.total
    )
    assert report.verdict is Verdict.FAIL


# ---- cross-language identity ---------------------------------------------
def test_cross_language_pairs_cover_the_champion_comparisons():
    from sofia.voice.benchmark import DEFAULT_PAIRS

    pairs = {(a.label, b.label) for a, b in DEFAULT_PAIRS}
    # RU is the champion, so RU<->UA and RU<->EN carry the acceptance decision.
    assert ("RU", "UA") in pairs
    assert ("RU", "EN") in pairs


def test_cross_language_only_needs_audio_on_the_compared_side(tmp_path):
    """The reference side contributes a voiceprint, not a clip.

    Requiring reference audio would report NOT_MEASURED for a pair that is
    perfectly comparable.
    """
    from sofia.voice.benchmark import CampaignReport, ClipOutcome, run_cross_language
    from sofia.voice.corpus import corpus_for

    team = VoiceTeam(VoiceBackends.unavailable("no models"), tmp_path)
    reports = {lang: CampaignReport(language=lang) for lang in Language}
    # Only UA has audio; RU has none.
    for clip in corpus_for(Language.UA)[:1]:
        path = tmp_path / f"{clip.clip_id}.wav"
        _tone(path, duration=1.0)
        reports[Language.UA].outcomes.append(
            ClipOutcome(clip=clip, verdict=Verdict.HOLD, reason="", repairs=0,
                        audio_path=str(path))
        )
    cross = run_cross_language(
        team, reports, pairs=((Language.RU, Language.UA),), samples=1
    )
    # It was attempted, and blocked on the missing voiceprint rather than on a
    # missing reference clip.
    assert len(cross.results) == 1
    assert "no produced" not in cross.results[0].reason


def test_cross_language_blocks_without_a_reference_voiceprint(tmp_path):
    """Three languages each matching their own reference can still be three
    different people. Without a real voiceprint this is unmeasurable."""
    from sofia.voice.benchmark import CampaignReport, ClipOutcome, run_cross_language
    from sofia.voice.corpus import corpus_for

    team = VoiceTeam(VoiceBackends.unavailable("no models"), tmp_path)
    reports = {}
    for language in Language:
        rep = CampaignReport(language=language)
        for clip in corpus_for(language)[:3]:
            path = tmp_path / f"{clip.clip_id}.wav"
            _tone(path, duration=1.0)
            rep.outcomes.append(
                ClipOutcome(
                    clip=clip,
                    verdict=Verdict.HOLD,
                    reason="",
                    repairs=0,
                    audio_path=str(path),
                )
            )
        reports[language] = rep

    cross = run_cross_language(team, reports, samples=1)
    assert cross.results
    assert cross.verdict is Verdict.NOT_MEASURED
    assert all(r.critical for r in cross.results)


def test_cross_language_reports_not_measured_when_a_language_produced_nothing(tmp_path):
    from sofia.voice.benchmark import CampaignReport, run_cross_language

    team = VoiceTeam(VoiceBackends.unavailable("no models"), tmp_path)
    reports = {language: CampaignReport(language=language) for language in Language}
    cross = run_cross_language(team, reports, samples=1)
    assert cross.verdict is Verdict.NOT_MEASURED
    # The reason names which language had nothing to compare.
    assert all("no produced" in r.reason and "clips" in r.reason for r in cross.results)
