import pytest

from app.productivity.india_norms import crew_output_per_day, load_norms
from app.productivity.model import load_models
from app.productivity.predictor import CrewConversion, build_baseline
from app.service import CaseError, india_norm_output, india_norms


def test_norms_load_and_are_traceable():
    norms = load_norms()
    item = norms["IS7272-1brick"]
    assert item.roles["mason"] == 0.94 and item.mason_role() == "mason"
    assert "IS 7272" in item.citation and item.evidence_depth.startswith("full text")
    assert norms["CPWD-FPS-superstructure-1brick"].mason_role() == "mason_1st_class"


def test_crew_output_matches_mason_pace_and_flags_understaffing():
    norms = load_norms()
    out = crew_output_per_day(norms["IS7272-1brick"], masons=3)
    assert out.output_per_day == pytest.approx(3 / 0.94)
    assert out.required_support["mazdoor"] == pytest.approx(3 * 1.8 / 0.94)
    assert out.understaffed == {}                                  # no support declared -> nothing to flag
    short = crew_output_per_day(norms["IS7272-1brick"], masons=3, support={"mazdoor": 2, "bhisti": 1})
    assert short.understaffed["mazdoor"] == pytest.approx(3 * 1.8 / 0.94 - 2)
    assert "bhisti" not in short.understaffed                       # 1 provided >= 3*0.2/0.94 required


def test_nonpositive_masons_rejected():
    with pytest.raises(ValueError):
        crew_output_per_day(load_norms()["IS7272-1brick"], masons=0)


def test_service_wraps_norms_and_rejects_unknown_item():
    out = india_norm_output("CPWD-modular-superstructure", 2, {"coolie": 5})
    assert out["output_per_day"] == pytest.approx(2 / 0.44)
    with pytest.raises(CaseError):
        india_norm_output("nope", 2)


def test_p1_ouga_model_hourly_and_double_count_warning():
    models = load_models()
    m = models["P1-01-ouga-kampala"]
    pred = m.predict({"work_height_m": 1.5, "porters_per_layer": 2, "exed": 1})
    assert pred.value == pytest.approx(0.53 - 0.08 * 1.5 + 0.40 * 2 + 0.36 * 1)
    assert any("double-count" in w or "double counts" in w for w in pred.warnings)
    conv = CrewConversion(workers_per_crew=4, hours_per_day=8)
    b = build_baseline(1000, 2, predictions=[(pred, m)], conversion=conv)
    assert b.productivity_per_crew["mode"] == pytest.approx(pred.value * 8 * 4)
    with pytest.raises(ValueError):
        build_baseline(1000, 2, predictions=[(pred, m)], conversion=CrewConversion(workers_per_crew=4))  # no hours_per_day


def test_out_of_range_height_flagged_for_ouga_model():
    m = load_models()["P1-01-ouga-kampala"]
    pred = m.predict({"work_height_m": 8.0, "porters_per_layer": 2, "exed": 0})
    assert pred.extrapolated and any("above the range" in w for w in pred.warnings)
