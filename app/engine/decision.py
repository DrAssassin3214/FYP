"""Decision layer: compare accept / mitigation options with an explicit rule.

The engine never calls a result 'optimal'.  It reports the option that is
preferred *under the stated criterion and constraints* among the options that
were actually evaluated, and prints the rule it used.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Optional, Sequence

import numpy as np

from .emv import cost_summary
from .models import Activity, CostModel, Mitigation, Risk
from .simulation import SimResult, simulate, summarise

CRITERIA = {
    "min_expected_total_cost": "minimum total expected cost  TEC = C_mitigation + E[C_residual]",
    "min_deadline_exceedance": "minimum probability of exceeding the deadline",
    "min_p90_duration": "minimum P90 activity duration",
}


@dataclass(frozen=True)
class Option:
    option_id: str
    label: str
    mitigation_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class Constraints:
    max_p_exceed_deadline: Optional[float] = None    # e.g. 0.20; USER INPUT REQUIRED, no default
    max_mitigation_budget: Optional[float] = None    # currency; USER INPUT REQUIRED, no default


def apply_mitigations(risks: Sequence[Risk], mits: Sequence[Mitigation]) -> list[Risk]:
    """Return the residual risk list.  Only p and/or the delay distribution of the
    targeted risk change, and only to the values the user/expert supplied."""
    by_id = {r.risk_id: r for r in risks}
    seen: set[str] = set()
    extra: list[Risk] = []
    for m in mits:
        m.validate()
        if m.risk_id not in by_id:
            raise ValueError(f"{m.mitigation_id}: unknown risk {m.risk_id}")
        if m.risk_id in seen:
            raise ValueError(f"two mitigations target {m.risk_id} in one option")
        seen.add(m.risk_id)
        r = by_id[m.risk_id]
        if m.p_after is not None:
            r = replace(r, p=m.p_after)
        if m.delay_after is not None:
            r = replace(r, delay=m.delay_after)
        by_id[m.risk_id] = r
        extra.extend(m.secondary_risks)
    return list(by_id.values()) + extra


def evaluate_option(
    activity: Activity,
    risks: Sequence[Risk],
    option: Option,
    mitigations: dict[str, Mitigation],
    cost: CostModel,
    n: int,
    seed: int,
    occurrence_correlation=None,
) -> dict:
    mits = [mitigations[i] for i in option.mitigation_ids]
    infeasible = [m for m in mits if not m.feasible]
    residual = apply_mitigations(risks, mits)
    res: SimResult = simulate(activity, residual, n, seed, occurrence_correlation)
    deadline = activity.deadline_days.value if activity.deadline_days else None
    s = summarise(res, deadline_days=deadline)
    c = cost_summary(res, cost, deadline)
    c_mit = float(sum(m.cost.value for m in mits))
    return {
        "option_id": option.option_id,
        "label": option.label,
        "mitigations": list(option.mitigation_ids),
        "feasible": not infeasible,
        "infeasible_reason": "; ".join(m.infeasible_reason or m.mitigation_id for m in infeasible),
        "mitigation_cost": c_mit,
        "residual_expected_cost": c["expected_cost"],
        "total_expected_cost": c_mit + c["expected_cost"],
        "expected_duration": s["mean"],
        "expected_delay": s["expected_delay"],
        "P50": s["percentiles"]["P50"],
        "P80": s["percentiles"]["P80"],
        "P90": s["percentiles"]["P90"],
        "P95": s["percentiles"]["P95"],
        "p_exceed_deadline": s.get("p_exceed_deadline"),
        "cost_P90": c["P90"],
        "evidence_ids": sorted({e for m in mits for e in m.evidence_ids}),
    }


def compare_options(
    activity: Activity,
    risks: Sequence[Risk],
    options: Sequence[Option],
    mitigations: Sequence[Mitigation],
    cost: CostModel,
    criterion: str = "min_expected_total_cost",
    constraints: Constraints = Constraints(),
    n: int = 10_000,
    seed: int = 12345,
    occurrence_correlation=None,
) -> dict:
    if criterion not in CRITERIA:
        raise ValueError(f"unknown criterion {criterion}")
    if criterion == "min_deadline_exceedance" and activity.deadline_days is None:
        raise ValueError("criterion needs a deadline")
    if not any(o.option_id == "ACCEPT" for o in options):
        options = [Option("ACCEPT", "Accept (no response)")] + list(options)
    mit_map = {m.mitigation_id: m for m in mitigations}
    rows = [
        evaluate_option(activity, risks, o, mit_map, cost, n, seed, occurrence_correlation) for o in options
    ]

    # per-day break-even: mitigation cost per day of expected delay avoided, next to the delay cost per day
    accept = next(r for r in rows if r["option_id"] == "ACCEPT")
    for r in rows:
        avoided = accept["expected_delay"] - r["expected_delay"]
        r["expected_delay_avoided_days"] = avoided
        r["mitigation_cost_per_day_avoided"] = (r["mitigation_cost"] / avoided) if avoided > 1e-9 and r["mitigation_cost"] > 0 else None
        r["delay_cost_per_day"] = cost.cost_per_delay_day.value
        r["P90_change_vs_accept"] = r["P90"] - accept["P90"]
        r["total_expected_cost_change_vs_accept"] = r["total_expected_cost"] - accept["total_expected_cost"]

    # constraint check
    for r in rows:
        reasons = []
        if not r["feasible"]:
            reasons.append(f"infeasible ({r['infeasible_reason']})")
        if constraints.max_mitigation_budget is not None and r["mitigation_cost"] > constraints.max_mitigation_budget:
            reasons.append("exceeds mitigation budget")
        if constraints.max_p_exceed_deadline is not None:
            if r["p_exceed_deadline"] is None:
                reasons.append("deadline probability constraint set but no deadline given")
            elif r["p_exceed_deadline"] > constraints.max_p_exceed_deadline:
                reasons.append("violates deadline-probability limit")
        r["rejected_because"] = reasons
        r["admissible"] = not reasons

    keys = {
        "min_expected_total_cost": lambda r: r["total_expected_cost"],
        "min_deadline_exceedance": lambda r: r["p_exceed_deadline"],
        "min_p90_duration": lambda r: r["P90"],
    }
    admissible = [r for r in rows if r["admissible"]]
    selected = min(admissible, key=keys[criterion]) if admissible else None

    rule = (
        f"Criterion: {CRITERIA[criterion]}. Options evaluated: {len(rows)}. "
        f"Constraints: deadline-probability limit = {constraints.max_p_exceed_deadline}, "
        f"mitigation budget = {constraints.max_mitigation_budget}. "
        "Options that are infeasible or violate a constraint are removed before ranking."
    )
    if selected is None:
        statement = "No evaluated option satisfies all constraints under the stated assumptions."
    else:
        statement = (
            f"Under the stated criterion and assumptions, '{selected['label']}' is preferred among the "
            f"{len(admissible)} admissible options evaluated (total expected cost "
            f"{selected['total_expected_cost']:.0f} {cost.currency}, P90 duration {selected['P90']:.1f} days)."
        )
    return {
        "criterion": criterion,
        "rule": rule,
        "options": rows,
        "selected_option_id": selected["option_id"] if selected else None,
        "statement": statement,
        "caveat": "Result depends on user/expert inputs marked as assumptions; it is not a claim of optimality.",
    }
