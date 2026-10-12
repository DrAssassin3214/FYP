import numpy as np
import pytest
from dataclasses import replace

from app.engine.models import Activity, DelayDist, Param, Source
from app.engine.simulation import simulate
from app.productivity.model import ProductivityModel, Term, Variable, load_models, model_from_dict
from app.productivity.predictor import CrewConversion, build_baseline


def toy(**kw):
    d = dict(model_id="T1", name="toy", citation="test", form="linear", intercept=30.0,
             terms=(Term("x", -2.0),), variables=(Variable("x", "%", 0.0, 10.0),), output_unit="m2/day",
             crew_size_in_data=2)
    d.update(kw)
    return ProductivityModel(**d)


def test_linear_prediction_and_range_warnings():
    m = toy()
    p = m.predict({"x": 4})
    assert p.value == pytest.approx(22.0) and not p.extrapolated and p.basis == "per_crew_of_2"
    hi = m.predict({"x": 12})
    assert hi.extrapolated and any("above the range" in w for w in hi.warnings)
    with pytest.raises(ValueError):
        m.predict({})


def test_missing_validity_range_is_flagged_not_hidden():
    m = toy(variables=(Variable("x", "%", None, None),))
    assert any("not reported" in w for w in m.predict({"x": 3}).warnings)


def test_nonpositive_prediction_flagged():
    p = toy().predict({"x": 20})
    assert p.value < 0 and p.extrapolated and any("<= 0" in w for w in p.warnings)


def test_loglog_form_and_undeclared_variable():
    m = toy(form="loglog", intercept=1.0, terms=(Term("x", 0.5),), variables=(Variable("x"),))
    assert m.predict({"x": 4}).value == pytest.approx(np.exp(1.0 + 0.5 * np.log(4)))
    with pytest.raises(ValueError):
        m.predict({"x": 0})
    with pytest.raises(ValueError):
        toy(terms=(Term("y", 1.0),)).predict({"y": 1})


def test_curated_file_loads_and_matches_paper_equation():
    models = load_models()
    m = models["M03-brick-rework"]
    assert m.predict({"rework_cost_pct": 4.51}).value == pytest.approx(34.36 - 1.71 * 4.51)
    assert m.r2 == 0.78 and m.n == 40 and m.crew_size_in_data == 2
    assert any("not reported" in w for w in m.predict({"rework_cost_pct": 4.5}).warnings)


def test_baseline_from_manual_range():
    b = build_baseline(1200, 3, manual={"min": 20, "most_likely": 25, "max": 30, "source": "Expert Judgment"})
    assert b.planned_days == pytest.approx(1200 / (3 * 25))
    assert b.dist.a == pytest.approx(1200 / (3 * 30)) and b.dist.b == pytest.approx(1200 / (3 * 20))
    with pytest.raises(ValueError):
        build_baseline(1200, 3, manual={"min": 30, "most_likely": 25, "max": 20})


def test_baseline_from_models_scales_crew_and_warns():
    m = toy()
    pred = m.predict({"x": 4})                       # 22 m2/day for a 2-worker crew
    b = build_baseline(1000, 2, predictions=[(pred, m)], conversion=CrewConversion(workers_per_crew=4))
    assert b.productivity_per_crew["mode"] == pytest.approx(44.0)
    assert b.dist is None and any("deterministic" in w for w in b.warnings)
    assert any("scaled linearly" in w for w in b.warnings)
    b2 = build_baseline(1000, 2, predictions=[(pred, m)], conversion=CrewConversion(2), single_model_spread_pct=20)
    assert b2.dist is not None and b2.dist.a < b2.planned_days < b2.dist.b


def test_two_models_give_epistemic_range_and_unit_conversion():
    m1, m2 = toy(), toy(model_id="T2", intercept=26.0, output_unit="m3/day", output_basis="per_worker",
                        crew_size_in_data=None)
    preds = [(m1.predict({"x": 4}), m1), (m2.predict({"x": 4}), m2)]
    with pytest.raises(ValueError):
        build_baseline(1000, 2, predictions=preds, conversion=CrewConversion(2))      # needs wall thickness
    b = build_baseline(1000, 2, predictions=preds, conversion=CrewConversion(2, wall_thickness_m=0.23))
    assert b.used_models == ["T1", "T2"] and "pooled estimate across 2 published models" in b.basis


def test_sample_size_weighting_pulls_toward_the_larger_study():
    big = toy(model_id="BIG", intercept=100.0, terms=(Term("x", 0.0),), n=1000)     # constant 100
    small = toy(model_id="SMALL", intercept=10.0, terms=(Term("x", 0.0),), n=10)    # constant 10
    preds = [(big.predict({"x": 1}), big), (small.predict({"x": 1}), small)]
    equal = build_baseline(1000, 1, predictions=preds, conversion=CrewConversion(2), weighting="equal")
    weighted = build_baseline(1000, 1, predictions=preds, conversion=CrewConversion(2), weighting="sample_size")
    assert equal.productivity_per_crew["mode"] == pytest.approx(55.0)
    assert weighted.productivity_per_crew["mode"] == pytest.approx((100 * 1000 + 10 * 10) / 1010, rel=1e-6)
    assert weighted.productivity_per_crew["mode"] > equal.productivity_per_crew["mode"]
    assert weighted.dist.a == pytest.approx(equal.dist.a) and weighted.dist.b == pytest.approx(equal.dist.b)
    assert "sample-size-weighted" in weighted.basis and "equally weighted" in equal.basis


def test_sample_size_weighting_warns_when_n_missing():
    m1 = toy(model_id="A", n=50)
    m2 = toy(model_id="B", n=None)
    preds = [(m1.predict({"x": 1}), m1), (m2.predict({"x": 1}), m2)]
    b = build_baseline(1000, 1, predictions=preds, conversion=CrewConversion(2), weighting="sample_size")
    assert any("no sample size" in w for w in b.warnings)


def test_bad_weighting_rejected():
    m = toy()
    with pytest.raises(ValueError):
        build_baseline(1000, 1, predictions=[(m.predict({"x": 1}), m)], conversion=CrewConversion(2),
                       weighting="nonsense")


def test_unsupported_unit_rejected():
    m = toy(output_unit="man-hour/m2")
    with pytest.raises(ValueError):
        build_baseline(1000, 2, predictions=[(m.predict({"x": 1}), m)], conversion=CrewConversion(2))


def test_baseline_distribution_flows_into_simulation():
    b = build_baseline(1200, 3, manual={"min": 20, "most_likely": 25, "max": 30})
    a = Activity("A", "x", b.planned_param(), baseline_dist=b.dist)
    r = simulate(a, [], n=50_000, seed=3)
    assert r.duration.min() >= b.dist.a - 1e-9 and r.duration.max() <= b.dist.b + 1e-9
    assert r.duration.mean() == pytest.approx(b.dist.mean(), rel=0.01)
    assert r.latent_delay is not None
    both = Activity("A", "x", b.planned_param(), baseline_dist=b.dist, productivity_cv=Param(0.1, Source.ASSUMPTION))
    with pytest.raises(ValueError):
        both.validate()
