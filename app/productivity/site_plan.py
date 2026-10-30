"""Site-condition facts worked out from data the site manager ENTERS, replacing Yes/No questions.

Every fact below used to be a typed Yes/No.  Now the rule engine receives a value only when it can be derived from a
date, a count or a pick-list choice, and each derived value carries its reason ("because ...") so the manager can see
why a flag was raised.  Nothing here invents a threshold: the only comparisons are "later than", "greater than zero",
"more than half" (the meaning of "mostly") and "below the ground floor index 1" (already the rule library's only
numeric floor value).  A value that cannot be derived is simply left out, so the rule is reported as not evaluable.

Inputs (all optional):
    site = {
        wall_location:     "external" | "internal" | "both"        -> external_walls_in_scope
        floor_level:       0 = ground floor, 1, 2 ...              -> masonry_floor_level, work_at_height
        normal_duration_days:  duration without acceleration       -> schedule_compressed
        rework_items:      rework items recorded on earlier work   -> prior_rework_history
        migrant_workers:   workers whose home is far from site     -> gang_mostly_migrant (vs the gang size)
        gang_pay_due, gang_paid_on:   dates                        -> gang_payment_overdue
        client_pay_due, client_pay_expected:   dates               -> payment_delay_expected
        readiness: [{kind, ready_by}]   kind in READINESS         -> work_front_ready, frames_on_site,
                                                                      mep_sleeve_layout_marked,
                                                                      lintel_level_plan_issued, design_incomplete
    }
    context = {start, finish: task dates; events: [{name, kind, from, to}]}  kind in EVENT_KINDS
"""
from __future__ import annotations

import math
from datetime import date
from typing import Mapping, Optional

EVENT_KINDS = {
    "monsoon": ("monsoon_overlap", "Monsoon / heavy rain period"),
    "summer": ("summer_overlap", "Extreme heat period"),
    "festival": ("festival_or_harvest_in_window", "Festival, harvest or election period"),
}
READINESS = {
    "work_front": ("work_front_ready", "Work front handed over (floor de-propped and cleared)"),
    "frames": ("frames_on_site", "Door and window frames on site"),
    "mep": ("mep_sleeve_layout_marked", "MEP sleeve and conduit layout marked"),
    "lintel": ("lintel_level_plan_issued", "Lintel and sill level plan issued"),
    "design": ("design_incomplete", "Drawings / design information issued"),
}
WALL_LOCATIONS = {"external": "External walls", "internal": "Internal walls", "both": "External and internal walls"}
SITE_FACTS = {f for f, _ in EVENT_KINDS.values()} | {f for f, _ in READINESS.values()} | {
    "external_walls_in_scope", "masonry_floor_level", "work_at_height", "payment_delay_expected",
    "gang_payment_overdue", "gang_mostly_migrant", "prior_rework_history", "schedule_compressed", "planned_daily_output"}


def _blank(v) -> bool:
    return v is None or (isinstance(v, str) and not v.strip())


def _date(v, label: str) -> Optional[date]:
    if _blank(v):
        return None
    try:
        return date.fromisoformat(str(v).strip()[:10])
    except ValueError:
        raise ValueError(f"{label} must be a date (year-month-day), got {v!r}")


def _count(v, label: str, *, integer: bool = False) -> Optional[float]:
    if _blank(v):
        return None
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0:
        raise ValueError(f"{label} must be a number, 0 or more")
    if integer and float(v) != int(v):
        raise ValueError(f"{label} must be a whole number")
    return float(v)


def derive_site_facts(work: Mapping, *, duration_days: Optional[float] = None, quantity: Optional[float] = None,
                      scaffolding_needed: bool = False, workers_total: Optional[float] = None) -> dict:
    site = work.get("site") or {}
    ctx = work.get("context") or {}
    if not isinstance(site, Mapping):
        raise ValueError("work.site must be an object")
    if not isinstance(ctx, Mapping):
        raise ValueError("work.context must be an object")
    facts: dict = {}
    why: dict = {}
    notes: list = []

    def put(fact, value, because):
        facts[fact] = value
        why[fact] = because

    start, finish = _date(ctx.get("start"), "task start"), _date(ctx.get("finish"), "task finish")

    # ---- seasons / events from the site calendar -------------------------------------------------------------
    events = ctx.get("events") or []
    if not isinstance(events, (list, tuple)):
        raise ValueError("work.context.events must be a list")
    for kind, (fact, label) in EVENT_KINDS.items():
        evs = []
        for e in events:
            if isinstance(e, Mapping) and e.get("kind") == kind:
                a, b = _date(e.get("from"), f"{label} start"), _date(e.get("to") or e.get("from"), f"{label} end")
                if a and b:
                    evs.append((str(e.get("name") or label), a, b))
        if not evs:
            continue
        if start is None or finish is None:
            notes.append(f"{label}: the task's dates are needed to see whether it overlaps.")
            continue
        hit = [n for n, a, b in evs if a <= finish and b >= start]
        put(fact, bool(hit), (f"the task ({start} to {finish}) overlaps {', '.join(hit)}" if hit else
                              f"the task ({start} to {finish}) is outside every {label.lower()} you entered"))

    # ---- wall location, floor, height ------------------------------------------------------------------------
    loc = site.get("wall_location")
    if not _blank(loc):
        if loc not in WALL_LOCATIONS:
            raise ValueError(f"work.site.wall_location must be one of {', '.join(WALL_LOCATIONS)}")
        put("external_walls_in_scope", loc in ("external", "both"), f"walls in this task: {WALL_LOCATIONS[loc].lower()}")
    floor = _count(site.get("floor_level"), "work.site.floor_level", integer=True)
    if floor is not None:
        put("masonry_floor_level", floor, "floor entered for this task (0 = ground floor)")
    if floor is not None or scaffolding_needed:
        at_height = bool(scaffolding_needed or (floor is not None and floor >= 1))
        put("work_at_height", at_height,
            "scaffolding is listed as needed" if scaffolding_needed else
            ("the work is above the ground floor" if at_height else "ground floor and no scaffolding listed"))

    # ---- people and money ------------------------------------------------------------------------------------
    mig = _count(site.get("migrant_workers"), "work.site.migrant_workers", integer=True)
    if mig is not None:
        if workers_total is None or workers_total <= 0:
            notes.append("Migrant workers: enter the workers available (Labour tab) so the share can be worked out.")
        else:
            if mig > workers_total:
                raise ValueError(f"work.site.migrant_workers ({mig:g}) is more than the gang ({workers_total:g})")
            put("gang_mostly_migrant", bool(2 * mig > workers_total), f"{mig:g} of {workers_total:g} workers are migrant")
    due, paid = _date(site.get("gang_pay_due"), "gang payment due date"), _date(site.get("gang_paid_on"), "gang paid on")
    if due is not None:
        if paid is not None:
            put("gang_payment_overdue", bool(paid > due), f"paid on {paid}, due {due}" + (" (late)" if paid > due else " (on time)"))
        elif start is not None:
            put("gang_payment_overdue", bool(due < start), f"due {due}, still unpaid when the task starts {start}")
        else:
            notes.append("Gang payment: the task start date is needed to judge an unpaid due date.")
    cdue, cexp = _date(site.get("client_pay_due"), "client payment due date"), _date(site.get("client_pay_expected"), "client payment expected date")
    if cdue is not None and cexp is not None:
        put("payment_delay_expected", bool(cexp > cdue), f"payment due {cdue}, expected {cexp}")

    # ---- history, schedule pressure, pace --------------------------------------------------------------------
    rw = _count(site.get("rework_items"), "work.site.rework_items", integer=True)
    if rw is not None:
        put("prior_rework_history", bool(rw > 0), f"{rw:g} rework item{'' if rw == 1 else 's'} recorded on earlier work")
    normal = _count(site.get("normal_duration_days"), "work.site.normal_duration_days")
    if normal is not None and duration_days is not None:
        put("schedule_compressed", bool(duration_days < normal), f"planned {duration_days:g} days against a normal {normal:g}")
    if quantity is not None and duration_days:
        put("planned_daily_output", quantity / duration_days, f"{quantity:g} to do in {duration_days:g} days")

    # ---- readiness items (date a prerequisite is ready, against the task start) --------------------------------
    items_in = site.get("readiness") or []
    if not isinstance(items_in, (list, tuple)):
        raise ValueError("work.site.readiness must be a list")
    by_kind: dict = {}
    items = []
    for i, it in enumerate(items_in):
        if not isinstance(it, Mapping):
            raise ValueError(f"work.site.readiness[{i}] must be an object")
        kind = it.get("kind")
        if kind not in READINESS:
            raise ValueError(f"work.site.readiness[{i}].kind must be one of {', '.join(READINESS)}")
        d = _date(it.get("ready_by"), f"work.site.readiness[{i}].ready_by")
        row = {"kind": kind, "label": READINESS[kind][1], "ready_by": None if d is None else d.isoformat(), "ready_at_start": None}
        if d is not None and start is not None:
            row["ready_at_start"] = bool(d <= start)
        items.append(row)
        by_kind.setdefault(kind, []).append(row)
    if by_kind and start is None:
        notes.append("Readiness dates are compared with the task start date, which is not known yet.")
    for kind, rows in by_kind.items():
        fact = READINESS[kind][0]
        flags_ = [r["ready_at_start"] for r in rows]
        if None in flags_:
            continue
        ok = all(flags_)
        late = [f"{r['ready_by']}" for r in rows if not r["ready_at_start"]]
        because = (f"ready by {', '.join(r['ready_by'] for r in rows)}, task starts {start}" if ok
                   else f"ready only on {', '.join(late)}, after the task starts {start}")
        put(fact, (not ok) if kind == "design" else ok, because)

    return {"facts": facts, "because": why, "notes": notes, "readiness": items}
