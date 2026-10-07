"""Data models for the activity-level risk engine.

Every numerical input carries a Source so that assumptions are never silently
presented as evidence (master prompt, section 37).
"""
from __future__ import annotations

import math
import numbers
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Source(str, Enum):
    LITERATURE = "Literature"
    HISTORICAL = "Historical Data"
    USER = "User Input"
    EXPERT = "Expert Judgment"
    DERIVED = "Derived Calculation"
    ASSUMPTION = "Assumption"


class RiskStatus(str, Enum):
    LITERATURE_SUPPORTED = "literature-supported"
    EXPERT_USER = "expert/user-provided"
    AI_UNVERIFIED = "AI-suggested-unverified"


@dataclass(frozen=True)
class Param:
    """A number with provenance."""

    value: float
    source: Source
    evidence_ids: tuple[str, ...] = ()
    note: str = ""


@dataclass(frozen=True)
class DelayDist:
    """Delay magnitude *given occurrence*, in days.

    kind: 'pert' | 'triangular' | 'uniform' | 'fixed'
    a = minimum, m = most likely, b = maximum (uniform uses a,b; fixed uses m).
    lam is the Beta-PERT shape weight (4 is the conventional default).
    """

    kind: str
    a: float
    m: float
    b: float
    lam: float = 4.0
    source: Source = Source.ASSUMPTION
    evidence_ids: tuple[str, ...] = ()

    def validate(self) -> None:
        if self.kind not in {"pert", "triangular", "uniform", "fixed"}:
            raise ValueError(f"unknown distribution kind: {self.kind}")
        # only the parameters the kind actually uses are checked (uniform ignores m; fixed uses only m)
        used = {"fixed": ("m",), "uniform": ("a", "b")}.get(self.kind, ("a", "m", "b"))
        for name in used + (("lam",) if self.kind == "pert" else ()):
            v = getattr(self, name)
            if isinstance(v, bool) or not isinstance(v, numbers.Real):
                raise ValueError(f"{name} must be a number")
            if not math.isfinite(v):
                raise ValueError(f"{name} must be a finite number")
        if self.kind == "fixed":
            if self.m < 0:
                raise ValueError("fixed delay must be >= 0")
            return
        if self.a < 0:
            raise ValueError("minimum delay must be >= 0")
        if self.kind == "uniform":
            if self.b < self.a:
                raise ValueError("uniform requires b >= a")
            return
        if not (self.a <= self.m <= self.b):
            raise ValueError("require a <= m <= b")
        if self.kind == "pert" and self.lam <= 0:
            raise ValueError("PERT lambda must be > 0")

    def variance(self) -> float:
        """Analytical variance of the conditional delay (used to check the simulation)."""
        if self.kind == "fixed" or self.b == self.a:
            return 0.0
        if self.kind == "uniform":
            return (self.b - self.a) ** 2 / 12
        if self.kind == "triangular":
            a, m, b = self.a, self.m, self.b
            return (a * a + m * m + b * b - a * m - a * b - m * b) / 18
        s = self.b - self.a
        alpha = 1 + self.lam * (self.m - self.a) / s
        beta = 1 + self.lam * (self.b - self.m) / s
        return alpha * beta * s * s / ((alpha + beta) ** 2 * (alpha + beta + 1))

    def mean(self) -> float:
        """Analytical mean of the conditional delay."""
        if self.kind == "fixed":
            return self.m
        if self.kind == "uniform":
            return (self.a + self.b) / 2
        if self.kind == "triangular":
            return (self.a + self.m + self.b) / 3
        return (self.a + self.lam * self.m + self.b) / (self.lam + 2)


@dataclass(frozen=True)
class Risk:
    risk_id: str
    name: str
    p: Param                      # probability of occurrence during the activity (event probability)
    delay: DelayDist
    category: str = ""
    description: str = ""
    status: RiskStatus = RiskStatus.EXPERT_USER
    direct_cost_if_occurs: Param = Param(0.0, Source.ASSUMPTION, note="no direct cost entered")
    evidence_ids: tuple[str, ...] = ()

    def validate(self) -> None:
        pv = self.p.value
        if isinstance(pv, bool) or not isinstance(pv, numbers.Real) or not math.isfinite(pv):
            raise ValueError(f"{self.risk_id}: probability must be a finite number")
        if not (0.0 <= pv <= 1.0):
            raise ValueError(f"{self.risk_id}: probability must be in [0,1]")
        if self.direct_cost_if_occurs.value < 0:
            raise ValueError(f"{self.risk_id}: direct cost must be >= 0")
        self.delay.validate()


@dataclass(frozen=True)
class Activity:
    activity_id: str
    name: str
    baseline_duration_days: Param
    quantity: Optional[float] = None
    unit: str = ""
    deadline_days: Optional[Param] = None      # allowed total duration, days
    # Optional routine productivity variability as a coefficient of variation of a mean-1
    # lognormal multiplier on the baseline.  None = baseline is deterministic.  Risk-event
    # delays must then be elicited as the EXTRA delay beyond this routine variability.
    productivity_cv: Optional[Param] = None
    # Alternative to productivity_cv: the REALISED baseline duration (days) follows this distribution
    # (a, m, b are durations, not delays), typically derived from the spread of predicted productivity.
    # baseline_duration_days stays the PLANNED duration; delay is measured against it.
    baseline_dist: Optional[DelayDist] = None

    def validate(self) -> None:
        if self.baseline_duration_days.value <= 0:
            raise ValueError("baseline duration must be > 0")
        if self.baseline_dist is not None:
            self.baseline_dist.validate()
            if self.baseline_dist.a <= 0 and self.baseline_dist.kind != "fixed":
                raise ValueError("baseline duration distribution must have a minimum > 0")
            if self.productivity_cv is not None and self.productivity_cv.value > 0:
                raise ValueError("use either productivity_cv or baseline_dist, not both")
        if self.productivity_cv is not None and self.productivity_cv.value < 0:
            raise ValueError("productivity CV must be >= 0")
        if self.deadline_days is not None and self.deadline_days.value <= 0:
            raise ValueError("deadline must be > 0")


@dataclass(frozen=True)
class Mitigation:
    """A risk response.  Effect on the targeted risk is p -> p_after and/or
    delay -> delay_after.  None means 'unchanged'.  Effect sizes have no
    default: they must be supplied with a Source."""

    mitigation_id: str
    risk_id: str
    action: str
    strategy: str = "mitigate"            # avoid | mitigate | transfer | accept | monitor
    cost: Param = Param(0.0, Source.USER)
    p_after: Optional[Param] = None
    delay_after: Optional[DelayDist] = None
    secondary_risks: tuple[Risk, ...] = ()
    feasible: bool = True
    infeasible_reason: str = ""
    time_to_implement_days: float = 0.0
    evidence_ids: tuple[str, ...] = ()
    mechanism: str = ""

    def validate(self) -> None:
        if self.cost.value < 0:
            raise ValueError(f"{self.mitigation_id}: cost must be >= 0")
        if self.p_after is not None and not (0.0 <= self.p_after.value <= 1.0):
            raise ValueError(f"{self.mitigation_id}: p_after must be in [0,1]")
        if self.delay_after is not None:
            self.delay_after.validate()
        for r in self.secondary_risks:
            r.validate()


@dataclass(frozen=True)
class CostModel:
    cost_per_delay_day: Param                 # currency per day of delay (user input required)
    currency: str = "INR"
    # Liquidated damages per day of overrun beyond the activity deadline.  Default 0 = not modelled;
    # a real value is USER INPUT REQUIRED (contract-specific, no literature default).
    ld_per_day_after_deadline: Param = Param(0.0, Source.USER, note="not modelled")
