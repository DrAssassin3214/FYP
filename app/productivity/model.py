"""Published productivity prediction models, applied as written.

Every model here must come from a paper whose equation and coefficients were read (see
data/productivity_models.json, each entry carries its citation, context, fit statistics and
validity range).  The code never invents a coefficient.  It also never hides extrapolation:
an input outside the range seen in the model's data, or a missing validity range, produces a
warning that is shown to the user and stored in the audit record.

Supported functional forms (enough for the regression models found so far):
    linear : y = b0 + sum_i b_i * x_i**p_i
    loglog : ln y = b0 + sum_i b_i * ln x_i
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Optional, Sequence


@dataclass(frozen=True)
class Variable:
    name: str
    unit: str = ""
    min: Optional[float] = None       # smallest value in the model's data, if reported
    max: Optional[float] = None
    description: str = ""


@dataclass(frozen=True)
class Term:
    var: str
    coef: float
    power: float = 1.0


@dataclass(frozen=True)
class Prediction:
    model_id: str
    value: float
    unit: str
    basis: str                          # e.g. 'per_crew_of_2', 'per_worker', 'per_crew'
    warnings: tuple[str, ...] = ()
    extrapolated: bool = False


@dataclass(frozen=True)
class ProductivityModel:
    model_id: str
    name: str
    citation: str
    form: str                           # 'linear' | 'loglog'
    intercept: float
    terms: tuple[Term, ...]
    variables: tuple[Variable, ...]
    output_unit: str                    # e.g. 'm2/day'
    output_basis: str = "per_crew"      # 'per_crew' | 'per_worker'
    crew_size_in_data: Optional[int] = None
    doi: str = ""
    country: str = ""
    activity: str = ""
    n: Optional[int] = None
    r2: Optional[float] = None
    rmse: Optional[float] = None
    mape: Optional[float] = None
    evidence_depth: str = "NC"
    validity_text: str = ""
    limitations: str = ""
    usage_note: str = ""             # always surfaced as a warning, e.g. a scaling caveat specific to this model

    def validate(self) -> None:
        if self.form not in ("linear", "loglog"):
            raise ValueError(f"{self.model_id}: unsupported form {self.form}")
        names = {v.name for v in self.variables}
        for t in self.terms:
            if t.var not in names:
                raise ValueError(f"{self.model_id}: term uses undeclared variable {t.var}")

    def required_inputs(self) -> list[str]:
        return [t.var for t in self.terms]

    def predict(self, inputs: Mapping[str, float]) -> Prediction:
        self.validate()
        missing = [v for v in self.required_inputs() if v not in inputs or inputs[v] is None]
        if missing:
            raise ValueError(f"{self.model_id}: missing inputs {missing}")
        warns: list[str] = []
        extrap = False
        vmap = {v.name: v for v in self.variables}
        for name in self.required_inputs():
            x, v = float(inputs[name]), vmap[name]
            if v.min is None and v.max is None:
                warns.append(f"validity range of '{name}' not reported in the source; extrapolation cannot be checked")
            else:
                if v.min is not None and x < v.min:
                    warns.append(f"'{name}' = {x} is below the range in the model's data ({v.min}-{v.max})")
                    extrap = True
                if v.max is not None and x > v.max:
                    warns.append(f"'{name}' = {x} is above the range in the model's data ({v.min}-{v.max})")
                    extrap = True
        if self.form == "linear":
            y = self.intercept + sum(t.coef * float(inputs[t.var]) ** t.power for t in self.terms)
        else:
            if any(float(inputs[t.var]) <= 0 for t in self.terms):
                raise ValueError(f"{self.model_id}: log-log model needs strictly positive inputs")
            y = math.exp(self.intercept + sum(t.coef * math.log(float(inputs[t.var])) for t in self.terms))
        if y <= 0:
            warns.append("predicted productivity is <= 0: the model is being used outside a sensible range")
            extrap = True
        basis = self.output_basis if self.output_basis != "per_crew" or not self.crew_size_in_data \
            else f"per_crew_of_{self.crew_size_in_data}"
        if self.usage_note:
            warns.append(self.usage_note)
        return Prediction(self.model_id, y, self.output_unit, basis, tuple(warns), extrap)

    def to_dict(self) -> dict:
        d = self.__dict__.copy()
        d["terms"] = [t.__dict__ for t in self.terms]
        d["variables"] = [v.__dict__ for v in self.variables]
        return d


def model_from_dict(d: Mapping) -> ProductivityModel:
    m = ProductivityModel(
        model_id=d["model_id"], name=d.get("name", ""), citation=d["citation"], form=d["form"],
        intercept=float(d.get("intercept") or 0.0),
        terms=tuple(Term(t["var"], float(t["coef"]), float(t.get("power", 1.0))) for t in d["terms"]),
        variables=tuple(Variable(v["name"], v.get("unit", ""), v.get("min"), v.get("max"), v.get("description", ""))
                        for v in d["variables"]),
        output_unit=d["output_unit"], output_basis=d.get("output_basis", "per_crew"),
        crew_size_in_data=d.get("crew_size_in_data"), doi=d.get("doi", ""), country=d.get("country", ""),
        activity=d.get("activity", ""), n=d.get("n"), r2=d.get("r2"), rmse=d.get("rmse"), mape=d.get("mape"),
        evidence_depth=d.get("evidence_depth", "NC"), validity_text=d.get("validity_text", ""),
        limitations=d.get("limitations", ""), usage_note=d.get("usage_note", ""))
    m.validate()
    return m


DEFAULT_PATH = Path(__file__).resolve().parents[2] / "data" / "productivity_models.json"


def load_models(path: Path = DEFAULT_PATH) -> dict[str, ProductivityModel]:
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    out: dict[str, ProductivityModel] = {}
    for r in rows:
        m = model_from_dict(r)
        if m.model_id in out:
            raise ValueError(f"duplicate model id {m.model_id}")
        out[m.model_id] = m
    return out
