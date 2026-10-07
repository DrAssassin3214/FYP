"""Probability-impact classification (prioritisation only, not a quantity).

The continuous probability p is always kept; the ordinal class is derived from
user-editable bin edges.  Default edges below are EQUAL-WIDTH ASSUMPTIONS, not
values taken from the literature.  The matrix level is a qualitative label and is
never used in the EMV or simulation calculations.
"""
from __future__ import annotations

from bisect import bisect_right
from typing import Sequence

from .models import Risk

DEFAULT_P_EDGES = (0.2, 0.4, 0.6, 0.8)          # ASSUMPTION: equal-width bins
DEFAULT_LABELS = ("Very low", "Low", "Medium", "High", "Very high")


def probability_class(p: float, edges: Sequence[float] = DEFAULT_P_EDGES) -> int:
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must be in [0,1]")
    return bisect_right(list(edges), p) + 1


def impact_class(expected_delay_days: float, baseline_days: float, edges_fraction: Sequence[float]) -> int:
    """Class of the conditional expected delay as a fraction of baseline duration.

    edges_fraction has NO default: impact thresholds must be user/expert input.
    """
    if baseline_days <= 0:
        raise ValueError("baseline must be > 0")
    return bisect_right(list(edges_fraction), expected_delay_days / baseline_days) + 1


def matrix_level(p_class: int, i_class: int, thresholds: Sequence[int] = (5, 10, 15)) -> str:
    """Score = p_class * i_class on a 5x5 grid; thresholds are ASSUMPTIONS (editable)."""
    score = p_class * i_class
    names = ("Low", "Moderate", "High", "Extreme")
    return names[bisect_right(list(thresholds), score - 1)] if score > 0 else names[0]


def classify(risks: Sequence[Risk], baseline_days: float, impact_edges_fraction: Sequence[float]) -> list[dict]:
    rows = []
    for r in risks:
        pc = probability_class(r.p.value)
        ic = impact_class(r.delay.mean(), baseline_days, impact_edges_fraction)
        rows.append(
            {
                "risk_id": r.risk_id,
                "p": r.p.value,
                "expected_delay_if_occurs_days": r.delay.mean(),
                "p_class": pc,
                "impact_class": ic,
                "score": pc * ic,
                "level": matrix_level(pc, ic),
                "note": "ordinal prioritisation only; not a monetary or time quantity",
            }
        )
    return rows
