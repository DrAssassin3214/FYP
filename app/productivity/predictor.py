"""Turn published-model predictions (or a user-supplied range) into the planned baseline duration
and its distribution, in WORKING DAYS.

    T0 = quantity / (crews * productivity_per_crew)

Spread of the baseline comes from (in this order of preference):
  1. the user's own min / most likely / max productivity (Source = User Input / Expert Judgment),
  2. the spread of predictions across several applicable published models (epistemic spread),
  3. an explicit user-set +/- spread around a single prediction.
With a single model and no spread the baseline is deterministic and that is stated.
"""
from __future__ import annotations

import math

from dataclasses import dataclass, field
from typing import Mapping, Optional, Sequence

from app.engine.models import DelayDist, Param, Source

from .model import Prediction, ProductivityModel

SUPPORTED_UNITS = ("m2/day", "m3/day", "bricks/day", "m2/hour", "m2/hr")


@dataclass
class CrewConversion:
    workers_per_crew: int                       # workers (masons + helpers counted as in the source's crew) in YOUR crew
    wall_thickness_m: Optional[float] = None    # needed for m3/day
    bricks_per_m2: Optional[float] = None       # needed for bricks/day
    hours_per_day: Optional[float] = None       # needed for m2/hour or m2/hr


def to_m2_per_day_per_crew(pred: Prediction, model: ProductivityModel, conv: CrewConversion) -> tuple[float, list[str]]:
    """Convert a model output to m2 of wall per day for the user's crew.  Returns (value, warnings)."""
    warns = list(pred.warnings)
    unit = pred.unit.lower().replace("²", "2").replace("³", "3")
    if unit not in SUPPORTED_UNITS:
        raise ValueError(f"{pred.model_id}: output unit '{pred.unit}' cannot be converted automatically "
                         f"(supported: {SUPPORTED_UNITS}); give a conversion or use a manual productivity range")
    y = pred.value
    if unit in ("m2/hour", "m2/hr"):
        if not conv.hours_per_day:
            raise ValueError(f"{pred.model_id}: m2/hour output needs hours_per_day")
        y = y * conv.hours_per_day
    elif unit == "m3/day":
        if not conv.wall_thickness_m:
            raise ValueError(f"{pred.model_id}: m3/day output needs wall_thickness_m")
        y = y / conv.wall_thickness_m
    elif unit == "bricks/day":
        if not conv.bricks_per_m2:
            raise ValueError(f"{pred.model_id}: bricks/day output needs bricks_per_m2")
        y = y / conv.bricks_per_m2
    if model.output_basis == "per_worker":
        y = y * conv.workers_per_crew
    elif model.crew_size_in_data:
        per_worker = y / model.crew_size_in_data
        y = per_worker * conv.workers_per_crew
        if model.crew_size_in_data != conv.workers_per_crew:
            warns.append(f"crew scaled linearly from {model.crew_size_in_data} to {conv.workers_per_crew} workers "
                         "(assumption A13: no congestion or learning effects)")
    else:
        warns.append("crew size in the source data not reported; prediction used for your crew as is")
    return y, warns


@dataclass
class BaselineResult:
    planned_days: float
    dist: Optional[DelayDist]                   # durations (a, m, b); None = deterministic
    productivity_per_crew: dict                  # min / mode / max in m2/day/crew
    basis: str
    used_models: list[str]
    warnings: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)

    def planned_param(self) -> Param:
        return Param(round(self.planned_days, 4), Source.DERIVED, tuple(self.used_models),
                     f"quantity / (crews x productivity); basis: {self.basis}")


def build_baseline(
    quantity: float,
    crews: int,
    *,
    predictions: Sequence[tuple[Prediction, ProductivityModel]] = (),
    conversion: Optional[CrewConversion] = None,
    manual: Optional[Mapping] = None,            # {"min","most_likely","max","source"} in m2/day/crew
    single_model_spread_pct: Optional[float] = None,
    weighting: str = "equal",                    # "equal" | "sample_size"
) -> BaselineResult:
    if quantity <= 0 or crews < 1:
        raise ValueError("quantity must be > 0 and crews >= 1")
    if single_model_spread_pct is not None:
        sp = single_model_spread_pct
        if isinstance(sp, bool) or not isinstance(sp, (int, float)) or not math.isfinite(sp) or not (0 <= sp < 100):
            raise ValueError(f"single_model_spread_pct must be a number in [0, 100) percent, got {sp!r}")
    warns: list[str] = []
    used: list[str] = []
    srcs: list[str] = []
    if manual:
        lo, mo, hi = float(manual["min"]), float(manual["most_likely"]), float(manual["max"])
        if not (0 < lo <= mo <= hi):
            raise ValueError("manual productivity must satisfy 0 < min <= most_likely <= max")
        basis = f"manual range ({manual.get('source', 'User Input')})"
        srcs.append(str(manual.get("source", "User Input")))
    else:
        if not predictions:
            raise ValueError("no productivity source: give a manual range or at least one model prediction")
        if conversion is None:
            raise ValueError("conversion (workers per crew) is required for model predictions")
        if weighting not in ("equal", "sample_size"):
            raise ValueError("weighting must be 'equal' or 'sample_size'")
        vals: list[float] = []
        wts: list[float] = []
        for pred, model in predictions:
            v, w = to_m2_per_day_per_crew(pred, model, conversion)
            if v <= 0:
                raise ValueError(f"{pred.model_id}: predicted productivity <= 0; check inputs")
            vals.append(v)
            warns += [f"{pred.model_id}: {x}" for x in w]
            used.append(pred.model_id)
            srcs.append(model.citation)
            if weighting == "sample_size":
                if not model.n:
                    warns.append(f"{pred.model_id}: no sample size (n) reported; given weight 1 in the pooled average")
                wts.append(float(model.n) if model.n else 1.0)
            else:
                wts.append(1.0)
        mo = sum(v * w for v, w in zip(vals, wts)) / sum(wts)
        if len(vals) > 1:
            lo, hi = min(vals), max(vals)
            how = "sample-size-weighted" if weighting == "sample_size" else "equally weighted"
            basis = (f"{how} pooled estimate across {len(vals)} published models "
                    f"(models: {', '.join(f'{m.model_id} n={m.n or chr(63)}' for _, m in predictions)}); "
                    "spread shown is the full disagreement range across models, not a variability estimate")
        elif single_model_spread_pct:
            lo, hi = mo * (1 - single_model_spread_pct / 100), mo * (1 + single_model_spread_pct / 100)
            basis = f"one published model with a user-set +/-{single_model_spread_pct}% spread (Assumption)"
        else:
            lo = hi = mo
            basis = "one published model, deterministic (no spread available)"
            warns.append("baseline duration is deterministic; add a spread to represent productivity uncertainty")
    t_mode = quantity / (crews * mo)
    t_min, t_max = quantity / (crews * hi), quantity / (crews * lo)
    dist = None if t_min == t_max else DelayDist("pert", t_min, t_mode, t_max, source=Source.DERIVED,
                                                 evidence_ids=tuple(used))
    return BaselineResult(t_mode, dist, {"min": lo, "mode": mo, "max": hi}, basis, used, warns, srcs)
