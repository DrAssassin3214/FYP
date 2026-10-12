"""Tests for option generation and the decision command (app/engine/options.py) and the memoised Beta quantile.

Hand-checked numbers: a risk with p = 0.5 and PERT(1, 3, 8) has mean delay (1 + 4*3 + 8)/6 = 3.5 days, so at
8,000 per day its event EMV is 0.5 * 3.5 * 8000 = 14,000.
"""
import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
from scipy import stats

from app.engine import simulation
from app.engine.decision import Constraints, Option, compare_options
from app.engine.emv import event_emv
from app.engine.models import Activity, CostModel, DelayDist, Mitigation, Param, Risk, Source
from app.engine.options import (CATALOGUE_PATH, break_even_targets, build_options, decision_command, decision_sensitivity,
                                load_catalogue, mitigation_net_benefit, selection_stability, suggest_options, value_at_stake)

P = lambda v, s=Source.ASSUMPTION: Param(v, s)
ROOT = Path(__file__).resolve().parents[1]


def act(t0=16.0, deadline=None):
    return Activity("A1", "test", P(t0), deadline_days=P(deadline) if deadline else None)


def risk(rid, p, a=1, m=3, b=8, direct=0.0):
    return Risk(rid, rid, P(p), DelayDist("pert", a, m, b), direct_cost_if_occurs=P(direct))


COST = CostModel(P(8000, Source.USER), "INR")
MAT, LAB, WX = risk("R-MAT", 0.5), risk("R-LAB", 0.35, 1, 2, 6), risk("R-WX", 0.2, 1, 2, 7)


def mit(mid, rid, cost, p_after=None, delay_after=None, **kw):
    return Mitigation(mid, rid, mid, cost=P(cost, Source.USER), p_after=P(p_after, Source.EXPERT) if p_after is not None else None,
                      delay_after=delay_after, **kw)


# ---------- value at stake ----------
def test_value_at_stake_equals_event_emv_for_independent_linear_cost():
    rows = value_at_stake(act(), [MAT, LAB, WX], COST, n=60_000, seed=5)
    emv = {r["risk_id"]: r["emv"] for r in event_emv([MAT, LAB, WX], COST)}
    assert emv["R-MAT"] == pytest.approx(14_000)
    for r in rows:
        assert r["value_at_stake"] == pytest.approx(emv[r["risk_id"]], rel=0.04)
    assert [r["risk_id"] for r in rows] == ["R-MAT", "R-LAB", "R-WX"]          # largest first


def test_value_at_stake_exceeds_event_emv_when_liquidated_damages_apply():
    cost = CostModel(P(8000, Source.USER), "INR", P(5000, Source.USER))
    rows = value_at_stake(act(16, deadline=18), [MAT, LAB], cost, n=40_000, seed=5)
    emv = {r["risk_id"]: r["emv"] for r in event_emv([MAT, LAB], cost)}
    assert all(r["value_at_stake"] > emv[r["risk_id"]] for r in rows)


def test_value_at_stake_zero_for_zero_probability_risk():
    rows = value_at_stake(act(), [MAT, risk("R-ZERO", 0.0)], COST, n=5_000, seed=5)
    assert next(r for r in rows if r["risk_id"] == "R-ZERO")["value_at_stake"] == 0.0


# ---------- break-even targets ----------
def test_break_even_targets_hand_checked():
    b = break_even_targets(MAT, COST, 5_000)
    assert b["can_pay_off"] and b["event_emv"] == pytest.approx(14_000)
    assert b["required_reduction_fraction"] == pytest.approx(5_000 / 14_000)
    assert b["max_p_after_if_only_p_changes"] == pytest.approx(0.5 - 5_000 / (3.5 * 8_000))
    assert b["max_mean_delay_after_if_only_delay_changes"] == pytest.approx(2.25)


def test_break_even_cannot_pay_off_when_cost_exceeds_the_whole_risk():
    b = break_even_targets(MAT, COST, 14_000)
    assert not b["can_pay_off"] and "cannot pay for itself" in b["reason"]
    assert b["max_p_after_if_only_p_changes"] is None


def test_break_even_risk_without_cost():
    b = break_even_targets(risk("R-ZERO", 0.0), COST, 100)
    assert not b["can_pay_off"] and b["required_reduction_fraction"] is None


# ---------- per-mitigation net benefit ----------
def test_net_benefit_probability_reduction():
    k = mitigation_net_benefit(MAT, mit("M1", "R-MAT", 6_000, p_after=0.2), COST)
    assert k["emv_before"] == pytest.approx(14_000) and k["emv_after"] == pytest.approx(5_600)
    assert k["net_benefit"] == pytest.approx(2_400) and k["pays_for_itself"]


def test_net_benefit_counts_secondary_risks_and_feasibility():
    sec = Risk("S", "congestion", P(0.3), DelayDist("fixed", 0, 1, 0))
    k = mitigation_net_benefit(MAT, mit("M2", "R-MAT", 6_000, p_after=0.2, secondary_risks=(sec,)), COST)
    assert k["secondary_risk_emv"] == pytest.approx(0.3 * 1 * 8_000)
    assert k["net_benefit"] == pytest.approx(0.0, abs=1e-9) and not k["pays_for_itself"]
    bad = mitigation_net_benefit(MAT, mit("M3", "R-MAT", 0, p_after=0.0, feasible=False, infeasible_reason="x"), COST)
    assert not bad["pays_for_itself"]


def test_net_benefit_agrees_with_simulated_comparison_when_cost_is_linear():
    m = mit("M1", "R-MAT", 6_000, p_after=0.2)
    out = compare_options(act(), [MAT, LAB], [Option("O1", "buffer", ("M1",))], [m], COST, n=200_000, seed=9)
    o1 = next(r for r in out["options"] if r["option_id"] == "O1")
    analytic = mitigation_net_benefit(MAT, m, COST)["net_benefit"]          # 2,400
    # the paired difference has a standard error of about 30 at this n, so 150 is a five-sigma band
    assert -o1["total_expected_cost_change_vs_accept"] == pytest.approx(analytic, abs=150)


# ---------- option set ----------
def test_build_options_singles_then_combinations_over_different_risks():
    ms = [mit("M1", "R-MAT", 100, p_after=0.2), mit("M2", "R-MAT", 100, p_after=0.3), mit("M3", "R-LAB", 100, p_after=0.1)]
    opts, notes = build_options(ms)
    ids = [o.option_id for o in opts]
    assert ids[:3] == ["O-M1", "O-M2", "O-M3"]
    assert "O-M1+M3" in ids and "O-M2+M3" in ids and "O-M1+M2" not in ids      # two responses to one risk are alternatives
    assert not notes["truncated"] and notes["skipped_no_effect"] == []


def test_build_options_skips_no_effect_keeps_infeasible_as_single_and_truncates():
    ms = [mit("M1", "R-MAT", 100, p_after=0.2), mit("M2", "R-LAB", 100),                     # M2 has no modelled effect
          mit("M3", "R-WX", 100, p_after=0.0, feasible=False, infeasible_reason="no supplier")]
    opts, notes = build_options(ms)
    assert notes["skipped_no_effect"] == ["M2"]
    assert [o.option_id for o in opts] == ["O-M1", "O-M3"]                                   # infeasible kept alone, never combined
    many = [mit(f"M{i}", f"R{i}", 1, p_after=0.1) for i in range(8)]
    opts2, notes2 = build_options(many, max_size=3, max_options=10)
    assert len(opts2) == 10 and notes2["truncated"]


# ---------- the command ----------
def _decision(ms, cost=COST, **kw):
    opts, _ = build_options(ms)
    return compare_options(act(), [MAT, LAB], opts, ms, cost, n=30_000, seed=3, **kw), opts


def test_command_authorize_accept_and_none():
    good, _ = _decision([mit("M1", "R-MAT", 2_000, p_after=0.2)])
    c = decision_command(good)
    assert c["command"] == "AUTHORIZE MITIGATION" and c["selected_option_id"] == "O-M1"
    assert c["figures"]["expected_cost_saving_vs_accept"] > 0 and "optimal" not in c["reason"].lower()

    dear, _ = _decision([mit("M1", "R-MAT", 1_000_000, p_after=0.0)])
    c2 = decision_command(dear)
    assert c2["command"] == "ACCEPT RISK" and c2["figures"]["closest_alternative_extra_cost"] > 0

    none, _ = _decision([mit("M1", "R-MAT", 2_000, p_after=0.2)], constraints=Constraints(max_mitigation_budget=-1))
    c3 = decision_command(none)
    assert c3["command"] == "NO ADMISSIBLE OPTION" and c3["selected_option_id"] is None


def test_command_reports_the_gap_to_the_runner_up():
    out, _ = _decision([mit("M1", "R-MAT", 2_000, p_after=0.2), mit("M2", "R-MAT", 2_500, p_after=0.2)])
    f = decision_command(out)["figures"]
    assert f["runner_up_extra_cost"] > 0 and f["runner_up_id"]


def test_selection_stability_and_cost_sensitivity_flip():
    ms = [mit("M1", "R-MAT", 6_000, p_after=0.2)]
    opts, _ = build_options(ms)
    st = selection_stability(act(), [MAT, LAB], opts, ms, COST, "min_expected_total_cost", Constraints(), 20_000, [1, 2, 3])
    assert st["stable"] and st["selected_option_ids"] == ["O-M1"] * 3
    ds = decision_sensitivity(act(), [MAT, LAB], opts, ms, COST, "min_expected_total_cost", Constraints(), 20_000, 1)
    by = {r["multiplier"]: r["command"] for r in ds["rows"]}
    assert by[0.25] == "ACCEPT RISK" and by[4.0] == "AUTHORIZE MITIGATION" and ds["flip_between_multipliers"]


# ---------- candidate actions: no invented numbers ----------
def test_suggest_options_lists_actions_without_effect_values():
    ms = [mit("M1", "R-MAT", 6_000, p_after=0.2, catalogue_id="C-BUFFER")]
    s = suggest_options(act(), [MAT, LAB, WX], COST, ms, n=10_000, seed=2, top_n=3)
    assert [t["risk_id"] for t in s["targets"]] == ["R-MAT", "R-LAB", "R-WX"]
    top = s["targets"][0]
    assert top["max_justified_spend"] == top["value_at_stake"] > 0
    status = {a["catalogue_id"]: a["status"] for a in top["candidate_actions"]}
    assert status["C-BUFFER"] == "modelled" and status["C-SUPPLIER"] == "needs expert input"
    for t in s["targets"]:
        for a in t["candidate_actions"]:
            assert a["effect_values"] is None and a["inputs_required"]


def test_catalogue_contains_no_effect_sizes_or_costs_and_points_at_real_records():
    entries = load_catalogue()
    assert CATALOGUE_PATH.exists() and len(entries) >= 10
    forbidden = {"p_after", "delay_after", "cost", "effect", "effect_size", "reduction", "probability"}
    library = {r["id"] for r in json.loads((ROOT / "data" / "risk_library_masonry.json").read_text(encoding="utf-8-sig"))}
    from app.ai_layer.corpus import build_full_store

    store, _ = build_full_store(ROOT)
    for e in entries:
        assert not (set(e) & forbidden), e["catalogue_id"]
        assert set(e["applies_to"]) <= library, e["catalogue_id"]
        assert all(i in store for i in e["evidence_ids"]), (e["catalogue_id"], [i for i in e["evidence_ids"] if i not in store])
        assert e["quantified_evidence"] in {"Y", "P", "N"} and e["inputs_required"]
    assert len({e["catalogue_id"] for e in entries}) == len(entries)


# ---------- the memoised Beta quantile must not change any number ----------
def test_cached_pert_quantile_is_identical_to_scipy():
    u = np.random.default_rng(1).random((5_000, 3))[:, 1]            # a strided column, as simulate() passes it
    d = DelayDist("pert", 1, 3, 8)
    alpha, beta = 1 + 4 * 2 / 7, 1 + 4 * 5 / 7
    ref = 1 + 7 * stats.beta.ppf(u, alpha, beta)
    assert np.array_equal(simulation.delay_ppf(d, u), ref)
    assert np.array_equal(simulation.delay_ppf(d, u), ref)            # second call served from the cache
    assert not simulation._beta_ppf(u, alpha, beta).flags.writeable    # cached arrays are read-only
