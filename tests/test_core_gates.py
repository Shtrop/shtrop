"""Fail-closed behaviour is the studio's most important invariant."""

import pytest

from sofia.core.gates import Gate, GateResult, evaluate_gates, threshold_gate, worst
from sofia.core.verdict import Evidence, Measurement, Verdict


def _pass(name="a", critical=True):
    return GateResult(name=name, verdict=Verdict.PASS, critical=critical)


def test_missing_critical_gate_blocks():
    report = evaluate_gates([_pass("a")], required_critical=("a", "identity"))
    assert report.verdict is Verdict.MISSING
    assert report.missing_critical == ("identity",)
    assert not report.passed


def test_all_critical_present_and_passing_is_a_pass():
    report = evaluate_gates(
        [_pass("a"), _pass("b")], required_critical=("a", "b")
    )
    assert report.verdict is Verdict.PASS


def test_non_critical_failure_does_not_block():
    results = [_pass("a"), GateResult("advisory", Verdict.FAIL, critical=False)]
    report = evaluate_gates(results, required_critical=("a",))
    assert report.verdict is Verdict.PASS
    assert report.blocking == ()


def test_a_high_secondary_score_cannot_average_away_a_hard_failure():
    results = [
        GateResult("identity", Verdict.FAIL, critical=True),
        GateResult("sharpness", Verdict.PASS, critical=True),
        GateResult("aesthetics", Verdict.PASS, critical=False),
    ]
    report = evaluate_gates(results, required_critical=("identity", "sharpness"))
    assert report.verdict is Verdict.FAIL


def test_raising_gate_becomes_error_and_blocks():
    def boom(_):
        raise RuntimeError("model exploded")

    result = Gate(name="identity", check=boom).run(None)
    assert result.verdict is Verdict.ERROR
    assert result.blocking
    assert "model exploded" in result.reason


def test_gate_cannot_downgrade_its_own_criticality():
    def sneaky(_):
        return GateResult("identity", Verdict.FAIL, critical=False)

    result = Gate(name="identity", check=sneaky, critical=True).run(None)
    assert result.critical is True
    assert result.blocking


def test_gate_returning_wrong_type_is_an_error():
    result = Gate(name="x", check=lambda _: "fine").run(None)
    assert result.verdict is Verdict.ERROR


def test_duplicate_gate_results_are_an_integrity_error():
    report = evaluate_gates([_pass("a"), _pass("a")], required_critical=("a",))
    assert report.verdict is Verdict.ERROR


def test_not_measured_never_becomes_zero_or_pass():
    m = Measurement.not_measured("wer")
    result = threshold_gate("voice.pronunciation", m, 0.05, higher_is_better=False)
    assert result.verdict is Verdict.NOT_MEASURED
    assert result.measurement.value is None
    assert result.blocking


def test_predicted_evidence_cannot_satisfy_a_critical_gate():
    m = Measurement("identity", 0.99, Evidence.PREDICTED, source="model guess")
    result = threshold_gate("voice.identity", m, 0.8, critical=True)
    assert result.verdict is Verdict.HOLD


def test_measured_local_satisfies_a_critical_gate():
    m = Measurement("identity", 0.91, Evidence.MEASURED_LOCAL, source="embedding")
    assert threshold_gate("voice.identity", m, 0.8, critical=True).verdict is Verdict.PASS


def test_measurement_rejects_value_without_evidence():
    with pytest.raises(ValueError):
        Measurement("wer", None, Evidence.MEASURED_LOCAL)
    with pytest.raises(ValueError):
        Measurement("wer", 0.1, Evidence.NOT_MEASURED)


def test_worst_verdict_ordering():
    assert worst([Verdict.PASS, Verdict.FAIL, Verdict.HOLD]) is Verdict.FAIL
    assert worst([Verdict.FAIL, Verdict.ERROR]) is Verdict.ERROR


# ---- path component sanitisation -----------------------------------------
def test_a_path_component_can_never_escape_its_directory():
    from pathlib import Path

    from sofia.core.paths import safe_component

    for hostile in (
        "../../../../etc/cron.d/x",
        "..",
        ".",
        "",
        "reel/../../x",
        "a\\b",
        "a\x00b",
    ):
        component = safe_component(hostile)
        assert "/" not in component and "\\" not in component
        assert set(component) != {"."}
        assert component
        # Joining it can only ever stay inside the parent.
        joined = (Path("/work") / component).resolve()
        assert str(joined).startswith("/work/")


def test_safe_component_preserves_ordinary_names():
    from sofia.core.paths import safe_component

    assert safe_component("sofia-reel-001.v2") == "sofia-reel-001.v2"
