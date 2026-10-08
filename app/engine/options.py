"""Option generation and the decision command.

This module answers two questions the cost layer (emv.py) and the comparison layer (decision.py) leave open:

  1. WHICH responses are worth considering?   -> value_at_stake(), break_even_targets(), suggest_options()
  2. WHAT should the site manager be told?     -> build_options(), decision_command(), decision_sensitivity()

Integrity rules kept here (the project's non-negotiable rules):
  * No effect size, probability, delay or cost is ever invented.  suggest_options() lists candidate actions from
    data/mitigation_catalogue.json and says exactly which inputs must be elicited; it does not fill them in.
    Research_Notes/D_mitigation.md section 7 found no transferable risk-reduction factor for masonry mitigations.
  * Every number produced here is a Derived Calculation from the user's own inputs (the risk register and the cost
    model), and says so in its `basis` field.
  * The command never calls a result optimal.  It states what is preferred under the stated criterion among the
    options actually evaluated, and how stable that choice is.

Two ways of measuring the money at stake in a risk, deliberately kept apart:
  event EMV_i      = p_i * (E[D_i] * Cd + direct_i)                    analytic; exact only for additive linear cost
  value at stake_i = E[C | accept]  -  E[C | risk i removed]           simulated with common random numbers; also
                                                                       holds when liquidated damages make cost non-linear
For independent risks and no liquidated damages the two agree within sampling error (tested).
"""
from __future__ import annotations

import json
from dataclasses import replace
from itertools import combinations
from pathlib import Path
from typing import Optional, Sequence

from .decision import CRITERIA, Constraints, Option, compare_options
from .emv import cost_summary, event_emv
from .models import Activity, CostModel, Mitigation, Param, Risk, Source
from .simulation import simulate

CATALOGUE_PATH = Path(__file__).resolve().parents[2] / "data" / "mitigation_catalogue.json"
_BASIS_DERIVED = "Derived Calculation from the entered risk register and cost model"


def load_catalogue(path: Optional[Path] = None) -> list[dict]:
    """Candidate response actions (no numbers).  Missing file = empty catalogue, never an error."""
    p = Path(path) if path else CATALOGUE_PATH
    if not p.exists():
        return []
    return json.loads(p.read_text(encoding="utf-8-sig")).get("entries", [])


# ------------------------------------------------------------------------------------------ value at stake
def value_at_stake(activity: Activity, risks: Sequence[Risk], cost: CostModel, n: int = 10_000, seed: int = 12345,
                   occurrence_correlation=None) -> list[dict]:
    """For every risk: how much expected cost disappears if that risk could not occur at all.

    This is the ceiling on what ANY response to the risk can be worth under a minimum-expected-cost criterion:
    a response costing more than `value_at_stake` cannot pay for itself even if it removed the risk completely
    (it ignores secondary risks a response may add).  Computed on the same random draws as the base run, so the
    difference is not sampling noise.  Sorted largest first.
    """
    deadline = activity.deadline_days.value if activity.deadline_days else None
    base = simulate(activity, risks, n, seed, occurrence_correlation)
    base_cost = cost_summary(base, cost, deadline)["expected_cost"]
    emv = {r["risk_id"]: r for r in event_emv(risks, cost)}
    rows = []
    for r in risks:
        removed = [replace(x, p=Param(0.0, Source.DERIVED, note="risk removed to measure value at stake")) if x.risk_id == r.risk_id else x
                   for x in risks]
        res = simulate(activity, removed, n, seed, occurrence_correlation)
        c = cost_summary(res, cost, deadline)["expected_cost"]
        rows.append({
            "risk_id": r.risk_id,
            "name": r.name,
            "p": r.p.value,
            "event_emv": emv[r.risk_id]["emv"],
            "value_at_stake": max(0.0, base_cost - c),
            "expected_delay_days_at_stake": max(0.0, float(base.delay.mean() - res.delay.mean())),
            "share_of_expected_cost": (max(0.0, base_cost - c) / base_cost) if base_cost > 0 else 0.0,
            "basis": _BASIS_DERIVED + "; simulated with common random numbers",
        })
    return sorted(rows, key=lambda x: (-x["value_at_stake"], x["risk_id"]))


# ------------------------------------------------------------------------------------------ break-even targets
def break_even_targets(risk: Risk, cost: CostModel, mitigation_cost: float) -> dict:
    """What a response costing `mitigation_cost` must achieve on `risk` before it can pay for itself.

    Analytic, additive linear cost (no liquidated damages, no secondary risks).  These are THRESHOLDS to give an
    expert to judge, not predictions: if the expert believes the response cannot get below them, it will not pay.
    """
    cd = cost.cost_per_delay_day.value
    direct = risk.direct_cost_if_occurs.value
    p = risk.p.value
    mean_d = risk.delay.mean()
    conditional = mean_d * cd + direct
    emv = p * conditional
    out = {
        "risk_id": risk.risk_id, "mitigation_cost": mitigation_cost, "event_emv": emv,
        "basis": _BASIS_DERIVED + "; analytic, linear cost, no secondary risks",
    }
    if emv <= 0:
        out.update(can_pay_off=False, reason="the risk carries no expected cost under the entered inputs",
                   required_reduction_fraction=None, max_p_after_if_only_p_changes=None,
                   max_mean_delay_after_if_only_delay_changes=None)
        return out
    frac = mitigation_cost / emv
    can = frac < 1.0
    out["can_pay_off"] = can
    out["required_reduction_fraction"] = frac
    if not can:
        out["reason"] = ("costs at least as much as the whole expected cost of the risk, so it cannot pay for itself "
                         "even if it removed the risk completely")
        out["max_p_after_if_only_p_changes"] = None
        out["max_mean_delay_after_if_only_delay_changes"] = None
        return out
    out["reason"] = f"must cut the expected cost of this risk by more than {frac * 100:.1f}%"
    out["max_p_after_if_only_p_changes"] = (p - mitigation_cost / conditional) if conditional > 0 else None
    if cd > 0 and p > 0:
        out["max_mean_delay_after_if_only_delay_changes"] = ((emv - mitigation_cost) / p - direct) / cd
    else:
        out["max_mean_delay_after_if_only_delay_changes"] = None
    return out


# ------------------------------------------------------------------------------------------ per-mitigation check
def mitigation_net_benefit(risk: Risk, mitigation: Mitigation, cost: CostModel) -> dict:
    """The simple 'does this response pay for itself' test for ONE mitigation on ITS risk, in expected money:

        net benefit = EMV(risk before) - EMV(risk after) - EMV(secondary risks) - mitigation cost

    Analytic and easy to explain, but exact only for additive linear cost (no liquidated damages) and a single
    response.  When liquidated damages are modelled, or several responses interact, use the simulated option
    comparison instead (this function says so in `basis`).
    """
    cd = cost.cost_per_delay_day.value

    def emv(p: float, mean_delay: float, direct: float) -> float:
        return p * (mean_delay * cd + direct)

    direct = risk.direct_cost_if_occurs.value
    before = emv(risk.p.value, risk.delay.mean(), direct)
    p2 = mitigation.p_after.value if mitigation.p_after is not None else risk.p.value
    d2 = mitigation.delay_after.mean() if mitigation.delay_after is not None else risk.delay.mean()
    after = emv(p2, d2, direct)
    secondary = sum(emv(s.p.value, s.delay.mean(), s.direct_cost_if_occurs.value) for s in mitigation.secondary_risks)
    gross = before - after
    net = gross - secondary - mitigation.cost.value
    ld = cost.ld_per_day_after_deadline.value > 0
    return {
        "mitigation_id": mitigation.mitigation_id, "risk_id": risk.risk_id, "feasible": mitigation.feasible,
        "emv_before": before, "emv_after": after, "gross_benefit": gross, "secondary_risk_emv": secondary,
        "mitigation_cost": mitigation.cost.value, "net_benefit": net,
        "pays_for_itself": bool(mitigation.feasible and net > 0),
        "basis": (_BASIS_DERIVED + "; analytic, linear cost, this response alone"
                  + ("; liquidated damages are modelled, so rely on the simulated option comparison" if ld else "")),
    }


# ------------------------------------------------------------------------------------------ candidate options
def suggest_options(activity: Activity, risks: Sequence[Risk], cost: CostModel,
                    mitigations: Sequence[Mitigation] = (), catalogue: Optional[Sequence[dict]] = None,
                    top_n: int = 5, n: int = 10_000, seed: int = 12345, occurrence_correlation=None) -> dict:
    """Where to look for responses, in order of money at stake, and what each candidate needs from the user.

    For each of the `top_n` costliest risks it returns the catalogue actions that target it.  Nothing here has an
    effect size: `inputs_required` says what to elicit, and `max_justified_spend` is the ceiling from
    value_at_stake().  An action the user has already modelled (mitigation with a matching catalogue_id) is
    marked `modelled`.
    """
    catalogue = load_catalogue() if catalogue is None else list(catalogue)
    stake = value_at_stake(activity, risks, cost, n, seed, occurrence_correlation)
    modelled_ids = {m.catalogue_id for m in mitigations if m.catalogue_id}
    modelled_risks = {m.risk_id for m in mitigations}
    targets, no_entry = [], []
    for row in stake[:max(0, top_n)]:
        if row["value_at_stake"] <= 0:
            continue
        cands = []
        for e in catalogue:
            if row["risk_id"] in (e.get("applies_to") or []):
                cands.append({
                    "catalogue_id": e["catalogue_id"], "measure": e["measure"], "strategy": e.get("strategy", "mitigate"),
                    "mechanism": e.get("mechanism", ""), "quantified_evidence": e.get("quantified_evidence", "N"),
                    "evidence_summary": e.get("evidence_summary", ""), "evidence_ids": list(e.get("evidence_ids") or []),
                    "inputs_required": list(e.get("inputs_required") or []),
                    "secondary_risks_to_consider": list(e.get("secondary_risks_to_consider") or []),
                    "note": e.get("note", ""),
                    "status": "modelled" if e["catalogue_id"] in modelled_ids else "needs expert input",
                    "effect_values": None,       # never filled in here
                })
        item = {**row, "max_justified_spend": row["value_at_stake"], "candidate_actions": cands,
                "already_has_a_mitigation": row["risk_id"] in modelled_risks}
        targets.append(item)
        if not cands:
            no_entry.append(row["risk_id"])
    return {
        "targets": targets,
        "risks_without_catalogue_entry": no_entry,
        "note": ("Candidate actions only. No effect size or cost is supplied: enter p after, delay after and cost "
                 "(with a Source, normally Expert Judgment) to have an action evaluated. max_justified_spend is the "
                 "expected cost that disappears if the risk were removed entirely; a response costing more cannot "
                 "pay for itself under a minimum-expected-cost criterion."),
    }


# ------------------------------------------------------------------------------------------ option set
def build_options(mitigations: Sequence[Mitigation], max_size: int = 3, max_options: int = 40) -> tuple[list[Option], dict]:
    """ACCEPT is added by compare_options.  Here: every modelled mitigation alone, then combinations of mitigations
    that target DIFFERENT risks (two responses to the same risk are alternatives, never a combination).

    Mitigations with no modelled effect (neither p_after nor delay_after) are left out and reported, because they
    would only add cost.  Infeasible mitigations are kept as single options so the comparison shows them removed
    with the reason.
    """
    skipped_no_effect = [m.mitigation_id for m in mitigations if m.p_after is None and m.delay_after is None and m.feasible]
    usable = [m for m in mitigations if m.feasible and (m.p_after is not None or m.delay_after is not None)]
    infeasible = [m for m in mitigations if not m.feasible]
    opts: list[Option] = []

    def make(ms: Sequence[Mitigation]) -> Option:
        ids = tuple(m.mitigation_id for m in ms)
        label = " + ".join(m.action or m.mitigation_id for m in ms)
        return Option("O-" + "+".join(ids), label, ids)

    for m in usable:
        opts.append(make([m]))
    for size in range(2, max(2, max_size) + 1):
        for combo in combinations(usable, size):
            if len({m.risk_id for m in combo}) == size:
                opts.append(make(combo))
    for m in infeasible:
        opts.append(make([m]))
    truncated = len(opts) > max_options
    if truncated:
        opts = opts[:max_options]
    return opts, {"skipped_no_effect": skipped_no_effect, "n_generated": len(opts), "truncated": truncated,
                  "max_size": max_size, "max_options": max_options}


# ------------------------------------------------------------------------------------------ the command
def decision_command(decision: dict, currency: str = "INR") -> dict:
    """Plain command for the site manager, derived only from compare_options() output.

    AUTHORIZE MITIGATION : an option other than ACCEPT is preferred under the stated criterion.
    ACCEPT RISK          : ACCEPT is preferred (no evaluated response is better under the criterion).
    NO ADMISSIBLE OPTION : every option, ACCEPT included, violates a constraint.
    """
    rows = {o["option_id"]: o for o in decision["options"]}
    sel_id = decision.get("selected_option_id")
    crit = decision["criterion"]
    accept = rows.get("ACCEPT")
    if sel_id is None:
        return {"command": "NO ADMISSIBLE OPTION", "selected_option_id": None, "criterion": crit,
                "reason": "Every evaluated option violates a constraint, including accepting the risk. Relax a constraint "
                          "or add an option.", "figures": {}}
    sel = rows[sel_id]
    others = [o for o in decision["options"] if o["admissible"] and o["option_id"] != sel_id]
    runner = None
    if others:
        key = {"min_expected_total_cost": "total_expected_cost", "min_deadline_exceedance": "p_exceed_deadline",
               "min_p90_duration": "P90"}[crit]
        runner = min(others, key=lambda o: (o[key] is None, o[key]))
    fig = {
        "mitigation_cost": sel["mitigation_cost"],
        "total_expected_cost": sel["total_expected_cost"],
        "expected_cost_saving_vs_accept": accept["total_expected_cost"] - sel["total_expected_cost"],
        "expected_delay_avoided_days": sel.get("expected_delay_avoided_days"),
        "P90_change_vs_accept_days": sel["P90_change_vs_accept"],
        "mitigation_cost_per_day_avoided": sel.get("mitigation_cost_per_day_avoided"),
        "delay_cost_per_day": sel.get("delay_cost_per_day"),
        "currency": currency,
    }
    if sel_id == "ACCEPT":
        best = min((o for o in decision["options"] if o["option_id"] != "ACCEPT" and o["admissible"]),
                   key=lambda o: o["total_expected_cost"], default=None)
        gap = (best["total_expected_cost"] - accept["total_expected_cost"]) if best else None
        reason = (f"Under the criterion '{CRITERIA[crit]}', accepting the risk is preferred among the "
                  f"{sum(1 for o in decision['options'] if o['admissible'])} admissible options evaluated.")
        if best is not None:
            reason += (f" The closest alternative, '{best['label']}', has a total expected cost {gap:,.0f} {currency} higher.")
        fig["closest_alternative_id"] = best["option_id"] if best else None
        fig["closest_alternative_extra_cost"] = gap
        return {"command": "ACCEPT RISK", "selected_option_id": sel_id, "criterion": crit, "reason": reason, "figures": fig}
    reason = (f"Under the criterion '{CRITERIA[crit]}', '{sel['label']}' is preferred among the "
              f"{sum(1 for o in decision['options'] if o['admissible'])} admissible options evaluated: it costs "
              f"{sel['mitigation_cost']:,.0f} {currency} and changes total expected cost by "
              f"{-fig['expected_cost_saving_vs_accept']:+,.0f} {currency} compared with accepting the risk.")
    if runner is not None:
        fig["runner_up_id"] = runner["option_id"]
        fig["runner_up_label"] = runner["label"]
        fig["runner_up_extra_cost"] = runner["total_expected_cost"] - sel["total_expected_cost"]
        fig["runner_up_extra_cost_share"] = ((runner["total_expected_cost"] - sel["total_expected_cost"]) / sel["total_expected_cost"]
                                             if sel["total_expected_cost"] > 0 else None)
    return {"command": "AUTHORIZE MITIGATION", "selected_option_id": sel_id, "criterion": crit, "reason": reason, "figures": fig}


def selection_stability(activity: Activity, risks: Sequence[Risk], options: Sequence[Option],
                        mitigations: Sequence[Mitigation], cost: CostModel, criterion: str,
                        constraints: Constraints, n: int, seeds: Sequence[int], occurrence_correlation=None) -> dict:
    """Re-run the whole comparison with different random seeds.  If the preferred option changes with the seed, the
    choice is within simulation noise and should not be presented as a firm result."""
    picks = []
    for s in seeds:
        out = compare_options(activity, risks, options, mitigations, cost, criterion, constraints, n, int(s),
                              occurrence_correlation)
        picks.append(out["selected_option_id"])
    return {"seeds": [int(s) for s in seeds], "selected_option_ids": picks, "stable": len(set(picks)) == 1,
            "note": "Same inputs, different random seeds. A choice that changes with the seed is not a firm result."}


def decision_sensitivity(activity: Activity, risks: Sequence[Risk], options: Sequence[Option],
                         mitigations: Sequence[Mitigation], cost: CostModel, criterion: str, constraints: Constraints,
                         n: int, seed: int, multipliers: Sequence[float] = (0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 4.0),
                         occurrence_correlation=None) -> dict:
    """Which option is preferred as the cost of a delay day is scaled up and down.  Shows where the decision flips
    between ACCEPT and a response, so the reader can judge how close the entered cost per day is to that point."""
    rows = []
    cd = cost.cost_per_delay_day
    ld = cost.ld_per_day_after_deadline
    for k in multipliers:
        c2 = replace(cost, cost_per_delay_day=Param(cd.value * k, Source.DERIVED, note=f"{k}x the entered cost per day"),
                     ld_per_day_after_deadline=ld)
        out = compare_options(activity, risks, options, mitigations, c2, criterion, constraints, n, seed,
                              occurrence_correlation)
        sel = out["selected_option_id"]
        rows.append({"multiplier": float(k), "cost_per_delay_day": cd.value * k, "selected_option_id": sel,
                     "command": ("NO ADMISSIBLE OPTION" if sel is None else "ACCEPT RISK" if sel == "ACCEPT" else "AUTHORIZE MITIGATION")})
    flips = [(a["multiplier"], b["multiplier"]) for a, b in zip(rows, rows[1:]) if a["selected_option_id"] != b["selected_option_id"]]
    return {"rows": rows, "flip_between_multipliers": flips,
            "note": ("Cost per delay day scaled while everything else is held fixed (liquidated damages are not scaled). "
                     "A flip between two multipliers means the preferred option depends on the cost per day entered.")}
