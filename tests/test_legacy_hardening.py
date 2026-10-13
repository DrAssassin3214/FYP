"""Regression tests for the legacy quantitative modules (simulation, EMV)."""
import numpy as np
import pytest

from app.engine.emv import event_emv
from app.engine.models import Activity, CostModel, DelayDist, Param, Risk, Source
from app.engine.simulation import analytic_moments, simulate, summarise


def P(v):
    return Param(v, Source.USER)


def risk(rid, p, a, m, b, kind="pert", direct=0.0):
    return Risk(rid, rid, P(p), DelayDist(kind, a, m, b), direct_cost_if_occurs=P(direct))


def act(t0=20.0, **kw):
    return Activity("A", "a", P(t0), **kw)


RISKS = [risk("R1", 0.2, 1, 3, 8, direct=100.0), risk("R2", 0.5, 0, 2, 6, "triangular"), risk("R3", 0.1, 5, 5, 5, "fixed")]


def test_l9_event_emv_rejects_bad_probability_and_direct_cost():
    for r in (risk("X", 1.2, 1, 2, 3), risk("X", float("nan"), 1, 2, 3), risk("X", 0.5, 1, 2, 3, direct=-5.0),
              risk("X", 0.5, 1, 2, 3, direct=float("inf"))):
        with pytest.raises(ValueError):
            event_emv([r], CostModel(P(10.0)))


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
