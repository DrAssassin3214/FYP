"""Regression tests for the legacy quantitative modules (simulation, EMV, productivity, India norms)."""
import numpy as np
import pytest

from app.engine.emv import cost_summary, event_emv, simulated_cost
from app.engine.models import Activity, CostModel, DelayDist, Param, Risk, Source
from app.engine.simulation import analytic_moments, simulate, summarise
from app.productivity.india_norms import crew_output_per_day, load_norms
from app.productivity.predictor import build_baseline


def P(v):
    return Param(v, Source.USER)


def risk(rid, p, a, m, b, kind="pert", direct=0.0):
    return Risk(rid, rid, P(p), DelayDist(kind, a, m, b), direct_cost_if_occurs=P(direct))


def act(t0=20.0, **kw):
    return Activity("A", "a", P(t0), **kw)


RISKS = [risk("R1", 0.2, 1, 3, 8, direct=100.0), risk("R2", 0.5, 0, 2, 6, "triangular"), risk("R3", 0.1, 5, 5, 5, "fixed")]


# ---- H3: CPWD mason classes ------------------------------------------------------------------
def test_h3_cpwd_mason_classes_are_summed_and_reported():
    item = load_norms()["CPWD-FPS-superstructure-1brick"]
    assert item.roles["mason_1st_class"] == 0.47 and item.roles["mason_2nd_class"] == 0.47
    assert item.mason_days_per_unit() == pytest.approx(0.94)           # 0.47 + 0.47, hand value
    out = crew_output_per_day(item, masons=2)
    assert out.output_per_day == pytest.approx(2 / 0.94)               # 2.1277 m3/day, NOT 2/0.47 = 4.255
    assert out.mason_days_per_unit == {"mason_1st_class": 0.47, "mason_2nd_class": 0.47}
    assert out.mason_days_per_unit_total == pytest.approx(0.94)
    assert out.required_masons_by_class == {"mason_1st_class": pytest.approx(1.0), "mason_2nd_class": pytest.approx(1.0)}
    assert out.required_support["coolie"] == pytest.approx(2 * 1.8 / 0.94)
    assert "0.47" in out.basis and "mason_2nd_class" in out.basis
    # same physical work as IS 7272 (single 'mason' constant 0.94) -> same output
    assert crew_output_per_day(load_norms()["IS7272-1brick"], 2).output_per_day == pytest.approx(out.output_per_day)


def test_h3_modular_item_hand_calc():
    item = load_norms()["CPWD-modular-superstructure"]            # 0.44 + 0.44
    assert crew_output_per_day(item, masons=2).output_per_day == pytest.approx(2 / 0.88)


# ---- L8: simulation inputs -------------------------------------------------------------------
def test_l8_self_pair_does_not_overwrite_diagonal():
    from app.engine.simulation import _correlation_matrix
    with pytest.raises(ValueError, match="self-correlation"):
        _correlation_matrix(["R1", "R2"], {("R1", "R1"): 0.3})
    mat = _correlation_matrix(["R1", "R2"], {("R1", "R1"): 1.0, ("R1", "R2"): 0.2})
    assert mat[0, 0] == 1.0 and mat[1, 1] == 1.0 and mat[0, 1] == 0.2
    base = simulate(act(), RISKS[:2], 2000, 1, {("R1", "R2"): 0.2})
    withself = simulate(act(), RISKS[:2], 2000, 1, {("R1", "R1"): 1.0, ("R1", "R2"): 0.2})
    assert np.array_equal(base.delay, withself.delay)
    assert withself.occurrence[:, 0].mean() == pytest.approx(0.2, abs=0.03)


@pytest.mark.parametrize("rho", [1.0, -1.0])
def test_l8_singular_correlation_is_clear_valueerror(rho):
    with pytest.raises(ValueError, match="singular|positive definite"):
        simulate(act(), RISKS[:2], 100, 1, {("R1", "R2"): rho})


@pytest.mark.parametrize("rho", [float("nan"), 1.5])
def test_l8_bad_rho_rejected(rho):
    with pytest.raises(ValueError):
        simulate(act(), RISKS[:2], 100, 1, {("R1", "R2"): rho})


@pytest.mark.parametrize("seed", [-1, 1.5, True, "7"])
def test_l8_bad_seed_rejected(seed):
    with pytest.raises(ValueError, match="seed"):
        simulate(act(), RISKS, 100, seed)


# ---- L9: EMV validation and negative-delay rule ----------------------------------------------
def test_l9_negative_baseline_delay_never_gives_negative_cost():
    dist = DelayDist("pert", 12, 14, 20)                     # planned 16: many runs finish early
    a = act(16.0, baseline_dist=dist)
    res = simulate(a, [], 20000, 5)
    assert (res.delay < 0).any()                               # physical delay array is left honest
    cost = CostModel(P(1000.0))
    c = simulated_cost(res, cost)
    assert (c >= 0).all()
    assert np.array_equal(c, 1000.0 * np.maximum(res.delay, 0))      # documented rule: no credit for early finish
    assert cost_summary(res, cost)["expected_cost"] >= 0


@pytest.mark.parametrize("bad", [-1.0, float("nan"), float("inf")])
def test_l9_cost_model_validated(bad):
    res = simulate(act(), RISKS, 100, 1)
    with pytest.raises(ValueError):
        simulated_cost(res, CostModel(P(bad)))
    with pytest.raises(ValueError):
        event_emv(RISKS, CostModel(P(bad)))
    with pytest.raises(ValueError):
        simulated_cost(res, CostModel(P(10.0), ld_per_day_after_deadline=P(bad)))


def test_l9_event_emv_rejects_bad_probability_and_direct_cost():
    for r in (risk("X", 1.2, 1, 2, 3), risk("X", float("nan"), 1, 2, 3), risk("X", 0.5, 1, 2, 3, direct=-5.0),
              risk("X", 0.5, 1, 2, 3, direct=float("inf"))):
        with pytest.raises(ValueError):
            event_emv([r], CostModel(P(10.0)))


# ---- L10: spread validation ------------------------------------------------------------------

@pytest.mark.parametrize("spread", [100, 150, -5, float("nan"), float("inf"), True])
def test_l10_spread_must_be_in_0_100(spread):
    with pytest.raises(ValueError, match="single_model_spread_pct"):
        build_baseline(1000, 2, manual={"min": 5, "most_likely": 6, "max": 7}, single_model_spread_pct=spread)


def test_l10_valid_spread_gives_valid_pert():
    from app.productivity.model import load_models
    from app.productivity.predictor import CrewConversion
    m = load_models()["P1-01-ouga-kampala"]
    pred = m.predict({"work_height_m": 1.5, "porters_per_layer": 2, "exed": 1})
    b = build_baseline(1000, 2, predictions=[(pred, m)], conversion=CrewConversion(workers_per_crew=4, hours_per_day=8), single_model_spread_pct=99.0)
    b.dist.validate()
    assert b.dist.a <= b.dist.m <= b.dist.b


# ---- Independent re-derivation ---------------------------------------------------------------
def test_emv_matches_hand_calculation():
    cd = 2500.0
    rows = event_emv(RISKS, CostModel(P(cd)))
    # PERT(1,3,8) mean=(1+12+8)/6=3.5 ; triangular(0,2,6) mean=8/3 ; fixed 5
    hand = 0.2 * (3.5 * cd + 100.0) + 0.5 * (8 / 3 * cd) + 0.1 * (5 * cd)
    assert sum(r["emv"] for r in rows) == pytest.approx(hand)
    assert sum(r["p"] * r["expected_delay_if_occurs_days"] for r in rows) * cd + 0.2 * 100.0 == pytest.approx(hand)


def test_monte_carlo_mean_within_3_standard_errors_of_analytic():
    res = simulate(act(), RISKS, 200_000, 99)
    exact = 0.2 * 3.5 + 0.5 * 8 / 3 + 0.1 * 5
    am = analytic_moments(RISKS)
    assert am["expected_delay"] == pytest.approx(exact)
    se = res.delay.std(ddof=1) / np.sqrt(res.n)
    assert abs(res.delay.mean() - exact) < 3 * se
    assert res.delay.var(ddof=1) == pytest.approx(am["variance"], rel=0.03)


def test_p90_equals_numpy_quantile_and_seeds_reproduce():
    r1 = simulate(act(), RISKS, 10_000, 7)
    r2 = simulate(act(), RISKS, 10_000, 7)
    r3 = simulate(act(), RISKS, 10_000, 8)
    assert np.array_equal(r1.duration, r2.duration)
    assert not np.array_equal(r1.duration, r3.duration)
    s = summarise(r1)
    assert s["percentiles"]["P90"] == np.quantile(r1.duration, 0.9)
    assert s["delay_percentiles"]["P90"] == np.quantile(r1.duration - 20.0, 0.9)
