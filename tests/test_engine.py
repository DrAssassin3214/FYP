import numpy as np
import pytest

from app.engine.audit import assumption_register, build_record, input_hash
from app.engine.decision import Constraints, Option, compare_options
from app.engine.emv import cost_summary, event_emv
from app.engine.matrix import impact_class, matrix_level, probability_class
from app.engine.models import Activity, CostModel, DelayDist, Mitigation, Param, Risk, Source
from app.engine.simulation import convergence, delay_ppf, sensitivity, simulate, summarise

P = lambda v, s=Source.ASSUMPTION: Param(v, s)


def act(t0=20.0, deadline=None):
    return Activity("A1", "test", P(t0), deadline_days=P(deadline) if deadline else None)


def risk(rid, p, a=1, m=3, b=8, kind="pert", direct=0.0):
    return Risk(rid, rid, P(p), DelayDist(kind, a, m, b), direct_cost_if_occurs=P(direct))


# ---------- distribution maths ----------
@pytest.mark.parametrize("kind", ["pert", "triangular", "uniform"])
def test_conditional_mean_matches_analytic(kind):
    d = DelayDist(kind, 1, 3, 9)
    u = np.random.default_rng(1).random(400_000)
    x = delay_ppf(d, u)
    se = x.std() / np.sqrt(len(x))
    assert abs(x.mean() - d.mean()) < 4 * se
    assert x.min() >= 1 and x.max() <= 9


def test_fixed_and_degenerate_distributions():
    u = np.random.default_rng(2).random(10)
    assert np.all(delay_ppf(DelayDist("fixed", 0, 4, 0), u) == 4)
    assert np.all(delay_ppf(DelayDist("pert", 2, 2, 2), u) == 2)


def test_invalid_distributions_rejected():
    for bad in (DelayDist("pert", 5, 3, 8), DelayDist("triangular", -1, 2, 3), DelayDist("weird", 1, 2, 3)):
        with pytest.raises(ValueError):
            bad.validate()


# ---------- simulation ----------
def test_no_risk_returns_baseline():
    r = simulate(act(20), [], n=1000, seed=1)
    assert np.all(r.duration == 20)


def test_zero_and_certain_probability():
    r0 = simulate(act(20), [risk("R1", 0.0)], n=2000, seed=3)
    assert np.all(r0.delay == 0)
    r1 = simulate(act(20), [Risk("R1", "x", P(1.0), DelayDist("fixed", 0, 4, 0))], n=2000, seed=3)
    assert np.all(r1.duration == 24)


def test_reproducibility_and_seed_sensitivity():
    rs = [risk("R1", 0.3), risk("R2", 0.5)]
    a = simulate(act(), rs, n=5000, seed=42)
    b = simulate(act(), rs, n=5000, seed=42)
    c = simulate(act(), rs, n=5000, seed=43)
    assert np.array_equal(a.duration, b.duration)
    assert not np.array_equal(a.duration, c.duration)


def test_order_of_risks_does_not_change_result():
    rs = [risk("R1", 0.3), risk("R2", 0.5)]
    a = simulate(act(), rs, n=5000, seed=7)
    b = simulate(act(), rs[::-1], n=5000, seed=7)
    assert np.allclose(a.duration, b.duration)


def test_simulated_expected_delay_matches_analytic_sum():
    rs = [risk("R1", 0.3, 1, 3, 8), risk("R2", 0.5, 2, 4, 10, kind="triangular"), risk("R3", 0.1, 5, 10, 30)]
    r = simulate(act(), rs, n=200_000, seed=11)
    analytic = sum(x.p.value * x.delay.mean() for x in rs)
    se = r.delay.std(ddof=1) / np.sqrt(r.n)
    assert abs(r.delay.mean() - analytic) < 4 * se


def test_percentiles_monotone_and_deadline_probability():
    rs = [risk("R1", 0.6), risk("R2", 0.4)]
    r = simulate(act(20, deadline=22), rs, n=20_000, seed=5)
    s = summarise(r, deadline_days=22, delay_thresholds=(2, 5))
    ps = [s["percentiles"][k] for k in ("P10", "P50", "P80", "P85", "P90", "P95")]
    assert ps == sorted(ps)
    assert s["min"] >= 20 and s["max"] >= s["percentiles"]["P95"]
    assert 0 <= s["p_exceed_deadline"] <= 1
    assert s["p_exceed_deadline"] == pytest.approx(float((r.duration > 22).mean()))
    assert s["p_delay_exceeds"][2.0] >= s["p_delay_exceeds"][5.0]
    lo, hi = s["percentile_ci95"]["P90"]
    assert lo <= s["percentiles"]["P90"] <= hi


def test_iteration_count_reduces_standard_error():
    rs = [risk("R1", 0.5)]
    small = summarise(simulate(act(), rs, n=1_000, seed=1))["mean_se"]
    large = summarise(simulate(act(), rs, n=100_000, seed=1))["mean_se"]
    assert large < small / 5


def test_convergence_rows():
    r = simulate(act(), [risk("R1", 0.5)], n=10_000, seed=1)
    rows = convergence(r)
    assert rows[-1]["n"] == 10_000 and len(rows) == 10


def test_invalid_inputs():
    with pytest.raises(ValueError):
        simulate(act(0), [], n=10)
    with pytest.raises(ValueError):
        simulate(act(), [risk("R1", 1.2)], n=10)
    with pytest.raises(ValueError):
        simulate(act(), [risk("R1", 0.2), risk("R1", 0.3)], n=10)
    with pytest.raises(ValueError):
        simulate(act(), [], n=0)


def test_positive_correlation_widens_spread_but_not_mean():
    rs = [risk("R1", 0.5), risk("R2", 0.5)]
    ind = simulate(act(), rs, n=100_000, seed=9)
    cor = simulate(act(), rs, n=100_000, seed=9, occurrence_correlation={("R1", "R2"): 0.8})
    assert cor.delay.std() > ind.delay.std() * 1.05
    assert abs(cor.delay.mean() - ind.delay.mean()) < 0.15
    with pytest.raises(ValueError):
        simulate(act(), rs, n=10, occurrence_correlation={("R1", "R2"): 1.5})


def test_sensitivity_ranks_dominant_risk_first():
    big = risk("BIG", 0.5, 10, 20, 40)
    small = risk("SMALL", 0.5, 0, 1, 2)
    s = sensitivity(simulate(act(), [small, big], n=20_000, seed=2))
    assert s[0]["risk_id"] == "BIG"
    assert sum(x["share_of_expected_delay"] for x in s) == pytest.approx(1.0)


def test_simulated_moments_match_analytic_including_variance():
    from app.engine.simulation import analytic_moments
    rs = [risk("R1", 0.3, 1, 3, 8), risk("R2", 0.5, 2, 4, 10, kind="triangular"),
          risk("R3", 0.1, 5, 10, 30, kind="uniform"), risk("R4", 0.7, 0, 2, 6)]
    r = simulate(act(), rs, n=400_000, seed=21)
    am = analytic_moments(rs)
    assert abs(r.delay.mean() - am["expected_delay"]) < 4 * r.delay.std() / np.sqrt(r.n)
    assert r.delay.var(ddof=1) == pytest.approx(am["variance"], rel=0.02)


def test_latent_productivity_variability_is_separate_and_mean_preserving():
    from dataclasses import replace
    a = replace(act(20), productivity_cv=P(0.15))
    r = simulate(a, [], n=200_000, seed=4)
    assert abs(r.duration.mean() - 20) < 0.05                      # mean-1 multiplier
    assert r.duration.std() == pytest.approx(20 * 0.15, rel=0.03)
    assert r.latent_delay is not None
    rr = simulate(a, [risk("R1", 0.5)], n=20_000, seed=4)
    assert {x["risk_id"] for x in sensitivity(rr)} == {"R1", "LATENT_PRODUCTIVITY"}


def test_cvar_at_least_percentile_and_precision_loop():
    from app.engine.simulation import simulate_until_precise, quantile_ci
    rs = [risk("R1", 0.5), risk("R2", 0.4)]
    s = summarise(simulate(act(), rs, n=50_000, seed=6))
    assert s["cvar_90"] >= s["percentiles"]["P90"] and s["cvar_95"] >= s["percentiles"]["P95"]
    res = simulate_until_precise(act(), rs, tolerance_days=0.05, quantile=0.9, start_n=5_000, max_n=200_000, seed=6)
    lo, hi = quantile_ci(np.sort(res.duration), 0.9)
    assert (hi - lo) / 2 <= 0.05 or res.n >= 200_000


def test_break_even_fields():
    a, rs, cost, mits, opts = _decision_setup()
    out = compare_options(a, rs, opts, mits, cost, n=10_000, seed=3)
    o1 = next(r for r in out["options"] if r["option_id"] == "O1")
    acc = next(r for r in out["options"] if r["option_id"] == "ACCEPT")
    assert acc["mitigation_cost_per_day_avoided"] is None
    assert o1["mitigation_cost_per_day_avoided"] == pytest.approx(o1["mitigation_cost"] / o1["expected_delay_avoided_days"])


# ---------- economics ----------
def test_event_emv_sum_matches_simulated_cost():
    cost = CostModel(P(1000.0, Source.USER))
    rs = [risk("R1", 0.3, 1, 3, 8, direct=500), risk("R2", 0.5, 2, 4, 10)]
    r = simulate(act(), rs, n=300_000, seed=4)
    emv_sum = sum(x["emv"] for x in event_emv(rs, cost))
    c = cost_summary(r, cost)
    assert abs(c["expected_cost"] - emv_sum) < 0.01 * emv_sum


def test_zero_cost_cases():
    cost = CostModel(P(0.0, Source.USER))
    r = simulate(act(), [risk("R1", 0.5)], n=1000, seed=1)
    assert cost_summary(r, cost)["expected_cost"] == 0
    r0 = simulate(act(), [], n=100, seed=1)
    assert cost_summary(r0, CostModel(P(1000.0, Source.USER)))["expected_cost"] == 0


def test_liquidated_damages_term_and_jensen():
    rs = [risk("R1", 0.6, 2, 5, 12), risk("R2", 0.5, 1, 3, 8)]
    r = simulate(act(20, deadline=22), rs, n=200_000, seed=8)
    no_ld = CostModel(P(1000.0, Source.USER))
    ld = CostModel(P(1000.0, Source.USER), ld_per_day_after_deadline=P(3000.0, Source.USER))
    e0 = cost_summary(r, no_ld, 22)["expected_cost"]
    e1 = cost_summary(r, ld, 22)["expected_cost"]
    manual = 3000.0 * np.maximum(0, r.duration - 22).mean()
    assert e1 - e0 == pytest.approx(manual, rel=1e-9)
    naive = 3000.0 * max(0.0, r.duration.mean() - 22)         # plugging in E[T]
    assert manual > naive                                    # Jensen: E[max(0,X)] >= max(0,E[X])
    with pytest.raises(ValueError):
        cost_summary(r, ld)                                  # LD without deadline is rejected


# ---------- matrix ----------
def test_matrix_classes():
    assert probability_class(0.0) == 1 and probability_class(0.2) == 2 and probability_class(0.99) == 5
    assert impact_class(2, 20, (0.05, 0.1, 0.2, 0.4)) == 3
    assert matrix_level(1, 1) == "Low" and matrix_level(5, 5) == "Extreme"
    with pytest.raises(ValueError):
        probability_class(1.1)


# ---------- decision ----------
def _decision_setup():
    a = act(20, deadline=24)
    rs = [risk("R1", 0.6, 2, 5, 12)]
    cost = CostModel(P(1000.0, Source.USER))
    good = Mitigation("M1", "R1", "buffer stock", cost=P(2000, Source.USER), p_after=P(0.2, Source.EXPERT))
    dear = Mitigation("M2", "R1", "gold plating", cost=P(1_000_000, Source.USER), p_after=P(0.0, Source.EXPERT))
    bad = Mitigation("M3", "R1", "not feasible", cost=P(0, Source.USER), p_after=P(0.0, Source.EXPERT),
                     feasible=False, infeasible_reason="no supplier")
    opts = [Option("O1", "buffer", ("M1",)), Option("O2", "gold", ("M2",)), Option("O3", "impossible", ("M3",))]
    return a, rs, cost, [good, dear, bad], opts


def test_residual_risk_is_pathwise_no_worse_with_common_random_numbers():
    a, rs, cost, mits, opts = _decision_setup()
    out = compare_options(a, rs, opts, mits, cost, n=20_000, seed=3)
    rows = {r["option_id"]: r for r in out["options"]}
    assert rows["O1"]["expected_delay"] < rows["ACCEPT"]["expected_delay"]
    assert rows["O2"]["expected_delay"] == 0.0


def test_lower_probability_is_pathwise_no_worse():
    a, rs, _, _, _ = _decision_setup()
    from dataclasses import replace
    lower = [replace(rs[0], p=P(0.2))]
    base = simulate(a, rs, n=20_000, seed=3)
    mit = simulate(a, lower, n=20_000, seed=3)
    assert np.all(mit.delay <= base.delay + 1e-12)


def test_min_cost_rule_and_infeasible_removed():
    a, rs, cost, mits, opts = _decision_setup()
    out = compare_options(a, rs, opts, mits, cost, n=20_000, seed=3)
    assert out["selected_option_id"] == "O1"
    o3 = next(r for r in out["options"] if r["option_id"] == "O3")
    assert not o3["admissible"] and any("infeasible" in x for x in o3["rejected_because"])
    assert "optimal" not in out["statement"].lower()


def test_deadline_constraint_can_reject_cheapest_option():
    a, rs, cost, mits, opts = _decision_setup()
    out = compare_options(a, rs, opts, mits, cost, constraints=Constraints(max_p_exceed_deadline=0.0), n=20_000, seed=3)
    assert out["selected_option_id"] == "O2"          # only zero-delay option satisfies limit
    out2 = compare_options(a, rs, opts[:1], mits, cost, constraints=Constraints(max_p_exceed_deadline=0.0), n=5_000, seed=3)
    assert out2["selected_option_id"] is None and "No evaluated option" in out2["statement"]


def test_budget_constraint():
    a, rs, cost, mits, opts = _decision_setup()
    out = compare_options(a, rs, opts, mits, cost, constraints=Constraints(max_mitigation_budget=1000), n=5_000, seed=3)
    assert out["selected_option_id"] == "ACCEPT"


def test_two_mitigations_same_risk_rejected():
    a, rs, cost, mits, _ = _decision_setup()
    with pytest.raises(ValueError):
        compare_options(a, rs, [Option("X", "both", ("M1", "M2"))], mits, cost, n=100)


def test_secondary_risk_is_added():
    a, rs, cost, _, _ = _decision_setup()
    sec = risk("SEC", 0.5, 1, 2, 3)
    m = Mitigation("M9", "R1", "overtime", cost=P(0, Source.USER), p_after=P(0.0, Source.EXPERT), secondary_risks=(sec,))
    out = compare_options(a, rs, [Option("O9", "overtime", ("M9",))], [m], cost, n=20_000, seed=3)
    o9 = next(r for r in out["options"] if r["option_id"] == "O9")
    assert o9["expected_delay"] == pytest.approx(0.5 * 2.0, rel=0.1)


# ---------- audit ----------
def test_audit_hash_stable_and_assumptions_flagged():
    a, rs, cost, mits, _ = _decision_setup()
    inputs = {"activity": a, "risks": rs, "cost": cost, "mitigations": mits}
    assert input_hash(inputs) == input_hash(inputs)
    reg = assumption_register(inputs)
    assert any(x["source"] == "Assumption" for x in reg)
    rec = build_record(inputs, {"x": 1}, seed=1, n=10, criterion="min_expected_total_cost")
    assert rec["input_hash_sha256"] == input_hash(inputs) and rec["seed"] == 1
    changed = {"activity": act(21, deadline=24), "risks": rs, "cost": cost, "mitigations": mits}
    assert input_hash(changed) != input_hash(inputs)
