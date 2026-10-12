"""India brick-masonry labour-output norms (IS 7272 Part I, CPWD Analysis of Rates).

These are official planning NORMS, not measured/fitted productivity data: they state how many
"X-days" a role (mason, mazdoor/coolie, bhisti) needs per unit of finished masonry, under stated
conditions (see each item's 'conditions'), not a distribution.  They are the best-sourced India
anchor found so far (full text, stable across CPWD editions per the review notes), so they are
exposed as a citable STARTING POINT — never applied automatically.

Deriving a crew's output per day from these constants requires a modelling choice that the norm
itself does not make (the norm gives labour input per unit output, not output per day for an
arbitrary crew).  The convention used here — output is paced by the mason count, provided the
mazdoor/bhisti ratio required by the norm is met — is the AUTHOR'S OWN inference (labelled as
such), not a value printed in the source.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Optional

DEFAULT_PATH = Path(__file__).resolve().parents[2] / "data" / "india_labour_norms.json"

_MASON_ROLES = ("mason", "mason_1st_class", "mason_2nd_class")


@dataclass(frozen=True)
class NormItem:
    item_id: str
    title: str
    citation: str
    wall_type: str
    unit_basis: str                  # 'm3' or 'm2'
    roles: dict                      # role name -> days per unit
    role_unit: str
    location_in_source: str
    evidence_depth: str
    conditions: str = ""
    doc_type: str = ""
    issuer: str = ""
    year: str = ""
    url: str = ""
    access: str = ""

    def mason_role(self) -> str:
        for r in _MASON_ROLES:
            if r in self.roles:
                return r
        raise ValueError(f"{self.item_id}: no mason role found in {list(self.roles)}")

    def mason_roles(self) -> tuple:
        """Every mason class present in the item (e.g. 1st AND 2nd class for CPWD analysis-of-rates items)."""
        found = tuple(r for r in _MASON_ROLES if r in self.roles)
        if not found:
            raise ValueError(f"{self.item_id}: no mason role found in {list(self.roles)}")
        return found

    def mason_days_per_unit(self) -> float:
        """Total mason-days per unit = SUM over mason classes (CPWD 6.4: 0.47 + 0.47 = 0.94, which equals the
        IS 7272 single 'mason' constant 0.94 for the same work)."""
        return sum(self.roles[r] for r in self.mason_roles())


def load_norms(path: Path = DEFAULT_PATH) -> dict[str, NormItem]:
    rows = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    out = {}
    for r in rows:
        item = NormItem(r["item_id"], r["title"], r["citation"], r["wall_type"], r["unit_basis"], dict(r["roles"]),
                        r["role_unit"], r["location_in_source"], r["evidence_depth"], r.get("conditions", ""),
                        r.get("doc_type", ""), r.get("issuer", ""), r.get("year", ""), r.get("url", ""),
                        r.get("access", ""))
        if item.item_id in out:
            raise ValueError(f"duplicate norm item id {item.item_id}")
        out[item.item_id] = item
    return out


@dataclass(frozen=True)
class CrewOutput:
    item_id: str
    output_per_day: float            # units (m3 or m2) per day for the STATED masons
    unit: str
    masons: float
    required_support: dict           # role -> support workers needed to keep pace, per the norm ratio
    provided_support: dict
    understaffed: dict                # role -> shortfall (provided < required), if any
    basis: str
    mason_days_per_unit: Optional[dict] = None  # mason class -> days per unit (as in the source), transparent breakdown
    mason_days_per_unit_total: float = 0.0   # sum of the classes
    required_masons_by_class: Optional[dict] = None    # mason class -> masons of that class needed for the stated crew


def crew_output_per_day(item: NormItem, masons: float, support: Optional[Mapping[str, float]] = None) -> CrewOutput:
    """output/day = masons / mason_days_per_unit, i.e. the norm's mason pace scaled to the crew's
    mason count.  This assumes the mazdoor/bhisti ratio the norm implies is actually met; if the
    user's declared support workers fall short, that role is reported in `understaffed` (a real,
    checkable understaffing condition, not a guess)."""
    if masons <= 0:
        raise ValueError("masons must be > 0")
    mclasses = item.mason_roles()
    by_class = {r: item.roles[r] for r in mclasses}
    mason_days = sum(by_class.values())          # all mason classes are required per unit, so they ADD
    output = masons / mason_days
    masons_by_class = {r: masons * d / mason_days for r, d in by_class.items()}
    support = dict(support or {})
    required, provided, short = {}, {}, {}
    for role, days in item.roles.items():
        if role in _MASON_ROLES:
            continue
        req = masons * (days / mason_days)
        required[role] = req
        prov = support.get(role)
        if prov is not None:
            provided[role] = prov
            if prov < req - 1e-9:
                short[role] = req - prov
    parts = " + ".join(f"{r} {d}" for r, d in by_class.items())
    basis = (f"output = masons / total mason labour constant ({parts} = {mason_days:g} {item.role_unit}); "
             "support-role requirement scaled by the same ratio (author's derivation, not printed in the source)")
    return CrewOutput(item.item_id, output, item.unit_basis + "/day", masons, required, provided, short, basis,
                      by_class, mason_days, masons_by_class)
