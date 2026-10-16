"""Quantity of work -> workers required (and materials), checked against what is available.

Replaces typing "workers required" and answering "are skilled masons short? yes/no" by hand: the site manager enters
the QUANTITY of masonry (m3 or m2, matching the norm), the planned duration comes from the activity, and the labour
constants of a published norm (IS 7272 / CPWD Analysis of Rates, see india_norms.py) give the work content in
person-days per role.  Everything here is arithmetic on those inputs:

    person-days (role group) = quantity x sum of the group's labour constants / efficiency
    workers required         = ceil(person-days / planned duration)
    shortfall                = max(0, required - available)
    duration with what is available = person-days / available, for the slowest group

INTEGRITY RULES (same as the rest of the tool):
  * Labour constants come only from the norm file; nothing is typed in from memory.  The norms are planning constants,
    not measured site output (see india_norms.py), so `efficiency` (default 1.0 = the norm exactly) is a USER INPUT.
  * Material conversion factors (bricks, cement, sand per unit of work) are NOT in the repository's data, so there are
    no defaults: each factor is a user input with a Source.
  * Units are never converted silently: the quantity's unit must equal the norm's unit basis.
"""
from __future__ import annotations

import math
from typing import Mapping, Optional, Sequence

from .india_norms import NormItem

GROUP_LABEL = {"masons": "Masons", "helpers": "Helpers (mazdoor / coolie)", "bhisti": "Bhisti (water carriers)"}
_EPS = 1e-9


def role_group(role: str) -> str:
    """Norm role name -> the group a site manager counts (all mason classes together, mazdoor = coolie)."""
    if role.startswith("mason"):
        return "masons"
    if role in ("mazdoor", "coolie"):
        return "helpers"
    if role in ("bhisti", "bhishti"):
        return "bhisti"
    return role


def _need_number(v, label: str, *, positive: bool = False) -> float:
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        raise ValueError(f"{label} must be a number")
    if v < 0 or (positive and v == 0):
        raise ValueError(f"{label} must be {'greater than' if positive else 'at least'} 0")
    return float(v)

RESOURCE_CLASSES = {
    "material": "Material (bricks, blocks)",
    "mortar": "Mortar material (sand, cement)",
    "equipment": "Equipment / tools (mixer, cutter, pump)",
    "machinery": "Machinery (hoist, material lift)",
    "scaffolding": "Scaffolding",
}


def _qty(m: Mapping, key: str, label: str) -> Optional[float]:
    return None if m.get(key) is None else _need_number(m.get(key), f"{label}.{key}")


def _plan_resources(resources: Sequence[Mapping], quantity: Optional[float], duration_days: Optional[float],
                    flags: list) -> list[dict]:
    """Classify each listed resource and compare QUANTITIES.

    material / mortar : required = quantity of work x per-unit-of-work factor (user input); on site = a quantity.
    equipment / machinery / scaffolding : required = a count (user input); on site = the count available (scaffolding:
    the amount erected).  Scaffolding also carries the user's declared inspection result `safe_passed`, because a
    count cannot show that it has passed a safety inspection.
    Without a quantity of work, materials cannot be sized (no required quantity, no flag); counts do not need it.
    Stock is never expressed in days.  The only time figure is the dealer's lead time.  The stock-out test is made on
    the SHARE OF THE WORK the stock supports: work is assumed to use material evenly over the planned duration, so
    the shortfall begins after (share x planned duration); if the dealer's lead time is not shorter than that, a new
    delivery cannot arrive before the shortfall begins (a tie counts as a stock-out, as before).
    """
    out = []
    for i, m in enumerate(resources):
        label = f"materials[{i}]"
        cls = str(m.get("class") or "material")
        if cls not in RESOURCE_CLASSES:
            raise ValueError(f"{label}.class must be one of {', '.join(RESOURCE_CLASSES)}")
        name = str(m.get("name") or "").strip() or f"Resource {i + 1}"
        have = _qty(m, "stock", label)
        lead = _qty(m, "lead_time_days", label)
        row = {"name": name, "class": cls, "class_label": RESOURCE_CLASSES[cls], "unit": str(m.get("unit") or ""),
               "source": str(m.get("source") or "User Input"), "on_site": have, "lead_time_days": lead,
               "required": None, "per_unit_of_work": None, "shortfall": None, "short": None,
               "work_supported_share": None, "stockout_before_delivery": None, "safe_passed": None}
        if cls in ("material", "mortar"):
            if m.get("per_unit_of_work") is not None:
                per = _need_number(m.get("per_unit_of_work"), f"{label}.per_unit_of_work")
                row["per_unit_of_work"] = per
                if quantity is not None:
                    row["required"] = quantity * per
        else:
            row["required"] = _qty(m, "required", label)
            row["unit"] = row["unit"] or "nos"
            if cls == "scaffolding" and m.get("safe_passed") is not None:
                if not isinstance(m.get("safe_passed"), bool):
                    raise ValueError(f"{label}.safe_passed must be true or false")
                row["safe_passed"] = m["safe_passed"]
        req = row["required"]
        if req is not None and have is not None:
            row["shortfall"] = max(0.0, req - have)
            row["short"] = bool(row["shortfall"] > _EPS)
            if cls in ("material", "mortar"):
                row["work_supported_share"] = 1.0 if req <= _EPS else min(1.0, have / req)
        if row["short"]:
            pct = 100.0 * row["shortfall"] / req
            msg = (f"{name}: {req:,.0f} {row['unit']} needed, {have:,.0f} on site, short by {row['shortfall']:,.0f} "
                   f"{row['unit']} ({pct:.0f}%).")
            level = "elevated"
            if row["work_supported_share"] is not None:
                share = row["work_supported_share"]
                supported_days = None if duration_days is None else share * duration_days
                if lead is not None and supported_days is not None:
                    row["stockout_before_delivery"] = bool(lead >= supported_days - _EPS)
                    msg += (f" Stock supports {100 * share:.0f}% of the work; the dealer's lead time is {lead:g} days, "
                            + ("so a new delivery cannot arrive before the shortfall begins."
                               if row["stockout_before_delivery"] else "so a delivery ordered now arrives in time."))
                    level = "elevated" if row["stockout_before_delivery"] else "normal"
                else:
                    msg += (f" Stock supports {100 * share:.0f}% of the work; enter the dealer's lead time "
                            "to judge the timing.")
                    level = "normal"
            flags.append({"level": level, "group": None, "message": msg})
        if cls == "scaffolding" and not row["short"]:
            if row["safe_passed"] is False:
                flags.append({"level": "elevated", "group": None,
                              "message": f"{name}: declared as not passed the safety inspection."})
            elif row["safe_passed"] is None and row["short"] is not None:
                flags.append({"level": "info", "group": None,
                              "message": f"{name}: quantity is enough; say whether it has passed the safety inspection."})
        if cls in ("material", "mortar") and quantity is None and row["per_unit_of_work"] is not None:
            flags.append({"level": "info", "group": None,
                          "message": f"{name}: enter the quantity of work to work out the quantity needed."})
        out.append(row)
    return out


def _resource_facts(rows: Sequence[Mapping]) -> dict:
    """Facts the rules read, derived only from rows that had both a required and an on-site quantity."""
    f: dict = {}
    mat = [r for r in rows if r["class"] == "material" and r["short"] is not None]
    mor = [r for r in rows if r["class"] == "mortar" and r["short"] is not None]
    eq = [r for r in rows if r["class"] == "equipment" and r["short"] is not None]
    mc = [r for r in rows if r["class"] == "machinery" and r["short"] is not None]
    if mat:
        f["material_short"] = any(r["short"] for r in mat)
        known = [r for r in mat if r["short"] and r["stockout_before_delivery"] is not None]
        f["material_stockout_before_delivery"] = (any(r["stockout_before_delivery"] for r in known)
                                                   if known else (False if not f["material_short"] else None))
        if f["material_stockout_before_delivery"] is None:
            del f["material_stockout_before_delivery"]
    if mor:
        f["mortar_short"] = any(r["short"] for r in mor)
        known = [r for r in mor if r["short"] and r["stockout_before_delivery"] is not None]
        if known:
            f["mortar_stockout_before_delivery"] = any(r["stockout_before_delivery"] for r in known)
        elif not f["mortar_short"]:
            f["mortar_stockout_before_delivery"] = False
    if eq:
        f["tools_shortage"] = any(r["short"] for r in eq)
    if mc:
        f["hoist_available"] = not any(r["short"] for r in mc)
    sc = [r for r in rows if r["class"] == "scaffolding" and r["short"] is not None]
    if sc:
        if any(r["short"] or r["safe_passed"] is False for r in sc):
            f["scaffolding_ready"] = False
        elif all(r["safe_passed"] is True for r in sc):
            f["scaffolding_ready"] = True          # enough erected AND declared safe; otherwise left unknown
    return f


def plan_work(norm: NormItem, quantity: float, unit: str, duration_days: float,
              available: Optional[Mapping[str, float]] = None, efficiency: float = 1.0,
              materials: Sequence[Mapping] = ()) -> dict:
    quantity = _need_number(quantity, "quantity", positive=True)
    duration_days = _need_number(duration_days, "planned duration (days)", positive=True)
    efficiency = _need_number(efficiency, "efficiency", positive=True)
    if unit != norm.unit_basis:
        raise ValueError(f"the quantity is in {unit!r} but norm {norm.item_id} is per {norm.unit_basis}; "
                         "pick a norm in the same unit (units are not converted automatically)")
    avail = {g: _need_number(v, f"available {g}") for g, v in (available or {}).items() if v is not None}

    by_group: dict[str, dict] = {}
    for role, c in norm.roles.items():
        g = by_group.setdefault(role_group(role), {"roles": {}, "constant": 0.0})
        g["roles"][role] = c
        g["constant"] += c

    groups = []
    for name, g in by_group.items():
        person_days = quantity * g["constant"] / efficiency
        frac = person_days / duration_days
        req = int(math.ceil(frac - _EPS))
        a = avail.get(name)
        short = None if a is None else max(0.0, req - a)
        groups.append({
            "group": name, "label": GROUP_LABEL.get(name, name), "norm_roles": dict(g["roles"]),
            "constant_per_unit": g["constant"], "person_days": person_days,
            "output_per_worker_day": (efficiency / g["constant"]) if g["constant"] > 0 else None,
            "required_workers": req, "required_fractional": frac,
            "available": a, "shortfall": short, "short": None if a is None else bool(short and short > _EPS),
            "days_with_available": (None if a is None else (person_days / a if a > 0 else None)),
        })

    entered = [g for g in groups if g["available"] is not None]
    req_total = sum(g["required_workers"] for g in groups)
    complete = len(entered) == len(groups)
    usable = sum(min(g["available"], g["required_workers"]) for g in entered) if complete else None

    implied, binding = None, None
    if entered:
        if any(g["available"] == 0 and g["person_days"] > 0 for g in entered):
            implied, binding = None, next(g["group"] for g in entered if g["available"] == 0)
        else:
            worst = max(entered, key=lambda g: g["days_with_available"])
            implied, binding = worst["days_with_available"], worst["group"]
    slip = None if implied is None else max(0.0, implied - duration_days)

    flags = []
    for g in entered:
        if g["short"]:
            pct = 100.0 * g["shortfall"] / g["required_workers"]
            msg = (f"{g['label']}: {g['required_workers']} needed to finish in {duration_days:g} days, "
                   f"{g['available']:g} available, short by {g['shortfall']:g} ({pct:.0f}%).")
            if g["available"] > 0:
                msg += (f" With {g['available']:g} the work takes {g['days_with_available']:.1f} days, "
                        f"{max(0.0, g['days_with_available'] - duration_days):.1f} more than planned.")
            else:
                msg += " With none available the work cannot be done."
            flags.append({"level": "elevated", "group": g["group"], "message": msg})
    if not entered:
        flags.append({"level": "info", "group": None,
                      "message": "No available workers entered: requirements are shown but not compared."})
    elif not complete:
        flags.append({"level": "info", "group": None,
                      "message": "Available workers not entered for every group: only the entered groups are compared."})

    mats, facts = _plan_resources(materials, quantity, duration_days, flags), {}
    facts["required_workers"] = req_total
    if complete:
        facts["available_workers"] = usable
    masons = next((g for g in groups if g["group"] == "masons"), None)
    if masons is not None and masons["short"] is not None:
        facts["skilled_masons_short"] = masons["short"]
    facts.update(_resource_facts(mats))

    return {
        "norm": {"item_id": norm.item_id, "title": norm.title, "citation": norm.citation, "unit_basis": norm.unit_basis,
                 "conditions": norm.conditions, "wall_type": norm.wall_type},
        "quantity": quantity, "unit": unit, "duration_days": duration_days, "efficiency": efficiency,
        "groups": groups, "required_total": req_total,
        "available_usable": usable, "available_entered_total": sum(g["available"] for g in entered) if entered else None,
        "implied_duration_days": implied, "slip_days": slip, "binding_group": binding,
        "materials": mats, "resource_classes": RESOURCE_CLASSES, "flags": flags, "derived_facts": facts,
        "basis": ("Derived Calculation: person-days = quantity x labour constants of the cited norm / efficiency; workers "
                  "required = person-days / planned duration, rounded up. `available_workers` counts only workers who can "
                  "be used (a surplus in one group does not cover a shortage in another). The norm is a planning constant, "
                  "not measured site output."),
    }


def plan_resources(resources: Sequence[Mapping], quantity: Optional[float] = None,
                   duration_days: Optional[float] = None) -> dict:
    """Resources only (no labour norm): the same classification and quantity comparison as plan_work, so equipment,
    machinery and scaffolding counts raise their flags without any quantity of work.  Materials need the quantity."""
    if quantity is not None:
        quantity = _need_number(quantity, "quantity", positive=True)
    if duration_days is not None:
        duration_days = _need_number(duration_days, "planned duration (days)", positive=True)
    flags: list = []
    mats = _plan_resources(resources, quantity, duration_days, flags)
    return {"resource_only": True, "norm": None, "quantity": quantity, "duration_days": duration_days, "groups": [],
            "required_total": None, "available_usable": None, "implied_duration_days": None, "slip_days": None,
            "binding_group": None, "materials": mats, "resource_classes": RESOURCE_CLASSES, "flags": flags,
            "derived_facts": _resource_facts(mats),
            "basis": "Derived Calculation: listed quantities and counts compared; see plan_work for the labour side."}


def norm_groups(norm: NormItem, efficiency: float = 1.0) -> list[dict]:
    """The norm's labour constants by group, and the output one worker of each group achieves per day
    (output per worker-day = 1 / constant, divided further by nothing: the norm itself, scaled by `efficiency`)."""
    out: dict[str, dict] = {}
    for role, c in norm.roles.items():
        g = out.setdefault(role_group(role), {"group": role_group(role), "roles": {}, "constant_per_unit": 0.0})
        g["roles"][role] = c
        g["constant_per_unit"] += c
    for g in out.values():
        g["label"] = GROUP_LABEL.get(g["group"], g["group"])
        g["output_per_worker_day"] = (efficiency / g["constant_per_unit"]) if g["constant_per_unit"] > 0 else None
    return list(out.values())
