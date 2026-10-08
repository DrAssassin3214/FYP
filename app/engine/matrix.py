"""Probability-impact classification (prioritisation only, not a quantity).

The continuous probability p is always kept; the ordinal class is derived from
user-editable bin edges.  Default edges below are EQUAL-WIDTH ASSUMPTIONS, not
values taken from the literature.  The matrix level is a qualitative label and is
never used in the EMV or simulation calculations.
"""
from __future__ import annotations

import math
from bisect import bisect_right
from typing import Sequence

from .models import Risk

DEFAULT_P_EDGES = (0.2, 0.4, 0.6, 0.8)          # ASSUMPTION: equal-width bins
DEFAULT_LABELS = ("Very low", "Low", "Medium", "High", "Very high")
EDGE_REL_TOL = 1e-9     # relative tolerance for "exactly on an edge" (absorbs binary floating-point rounding)


def probability_class(p: float, edges: Sequence[float] = DEFAULT_P_EDGES) -> int:
    """Class 1..5 from p.  Lower-edge-inclusive: a value exactly on an edge goes to the HIGHER class (0.2 -> 2).
    "Exactly on an edge" uses the same 1e-9 relative tolerance as impact_class, so a p that is 0.39999999999999997
    only because of binary rounding is still the 0.4 edge."""
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must be in [0,1]")
    n_reached = sum(1 for e in edges if p >= e or math.isclose(p, e, rel_tol=EDGE_REL_TOL, abs_tol=0.0))
    return n_reached + 1


def impact_class(expected_delay_days: float, baseline_days: float, edges_fraction: Sequence[float]) -> int:
    """Class of the conditional expected delay as a fraction of baseline duration.

    Convention (same as probability_class): classes are LOWER-edge-inclusive, so a ratio exactly on an
    edge belongs to the HIGHER class.  "Exactly on an edge" is judged with a relative tolerance of 1e-9, so
    that 1.2 d on 12 d (binary float 0.09999999999999999) is still the 0.10 edge and goes to the higher class.
    edges_fraction has NO default: impact thresholds must be user/expert input.
    """
    for name, v in (("expected delay", expected_delay_days), ("baseline", baseline_days)):
        if isinstance(v, bool) or not math.isfinite(v):
            raise ValueError(f"{name} must be a finite number")
    if baseline_days <= 0:
        raise ValueError("baseline must be > 0")
    ratio = expected_delay_days / baseline_days
    n_reached = sum(1 for e in edges_fraction if ratio >= e or math.isclose(ratio, e, rel_tol=EDGE_REL_TOL, abs_tol=0.0))
    return n_reached + 1


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
