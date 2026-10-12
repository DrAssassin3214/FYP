"""Monetary layer: event-level EMV and simulated expected cost.

Two different quantities, deliberately not conflated:
  event EMV_i  = p_i * ( E[D_i] * Cd + direct_i )        (analytic, per risk)
  E[C]         = mean over simulated runs of  Cd * delay + sum I_i * direct_i

For independent, additive risks the sum of event EMVs equals E[C] in expectation.
E[C] remains the reference when risks are correlated or when the cost model becomes
non-linear (e.g. a per-day cost that changes after a threshold); the sum of EMVs
then no longer applies.
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

import numpy as np

from .models import CostModel, Risk
from .simulation import SimResult


def _nonneg(value, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError(f"{label} must be a finite number >= 0, got {value!r}")
    return float(value)


def validate_cost_model(cost: CostModel) -> None:
    _nonneg(cost.cost_per_delay_day.value, "cost per delay day")
    _nonneg(cost.ld_per_day_after_deadline.value, "liquidated damages per day")


def _validate_risk_money(r: Risk) -> None:
    p = r.p.value
    if isinstance(p, bool) or not isinstance(p, (int, float)) or not math.isfinite(p) or not (0.0 <= p <= 1.0):
        raise ValueError(f"{r.risk_id}: probability must be a finite number in [0, 1], got {p!r}")
    _nonneg(r.direct_cost_if_occurs.value, f"{r.risk_id}: direct cost")


def event_emv(risks: Sequence[Risk], cost: CostModel) -> list[dict]:
    validate_cost_model(cost)
    cd = cost.cost_per_delay_day.value
    rows = []
    for r in risks:
        r.validate()
        _validate_risk_money(r)
        conditional = r.delay.mean() * cd + r.direct_cost_if_occurs.value
        rows.append(
            {
                "risk_id": r.risk_id,
                "p": r.p.value,
                "expected_delay_if_occurs_days": r.delay.mean(),
                "conditional_cost": conditional,
                "emv": r.p.value * conditional,
                "cost_per_day_source": cost.cost_per_delay_day.source.value,
            }
        )
    return rows


def simulated_cost(res: SimResult, cost: CostModel, deadline_days: Optional[float] = None) -> np.ndarray:
    """C = Cd * max(0, delay) + l * max(0, T - deadline) + direct costs.

    NEGATIVE-DELAY RULE: a run can finish earlier than planned (e.g. a baseline productivity
    distribution whose minimum duration is below the planned duration).  Early finish earns NO
    credit here: the delay used for cost is clipped at 0, so a cost can never be negative.  The
    simulated duration/delay arrays themselves are left untouched (they are the honest physical
    outcome); only the monetary layer is clipped.

    The liquidated-damages term is non-linear in T, so E[LD] is NOT l * max(0, E[T] - deadline)
    (Jensen's inequality) and cannot be recovered from event EMVs; use simulated cost.
    """
    validate_cost_model(cost)
    c = cost.cost_per_delay_day.value * np.maximum(res.delay, 0.0) + res.direct_cost
    ld = cost.ld_per_day_after_deadline.value
    if ld > 0:
        if deadline_days is None:
            raise ValueError("liquidated damages set but no deadline given")
        c = c + ld * np.maximum(0.0, res.duration - deadline_days)
    return c


def cost_summary(res: SimResult, cost: CostModel, deadline_days: Optional[float] = None) -> dict:
    c = simulated_cost(res, cost, deadline_days)
    return {
        "expected_cost": float(c.mean()),
        "std": float(c.std(ddof=1)) if len(c) > 1 else 0.0,
        "P50": float(np.quantile(c, 0.5)),
        "P80": float(np.quantile(c, 0.8)),
        "P90": float(np.quantile(c, 0.9)),
        "P95": float(np.quantile(c, 0.95)),
        "currency": cost.currency,
    }
