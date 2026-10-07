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

from typing import Optional, Sequence

import numpy as np

from .models import CostModel, Risk
from .simulation import SimResult


def event_emv(risks: Sequence[Risk], cost: CostModel) -> list[dict]:
    cd = cost.cost_per_delay_day.value
    rows = []
    for r in risks:
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
    """C = Cd * delay + l * max(0, T - deadline) + direct costs.

    The liquidated-damages term is non-linear in T, so E[LD] is NOT l * max(0, E[T] - deadline)
    (Jensen's inequality) and cannot be recovered from event EMVs; use simulated cost.
    """
    c = cost.cost_per_delay_day.value * res.delay + res.direct_cost
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
