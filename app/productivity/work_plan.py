"""One entry point for everything the site manager's data can work out: labour from the quantity of work and a norm,
resources (materials, equipment, machinery, scaffolding) from quantities and counts, and site conditions from dates and
counts.  Used by both the case service and the GUI's API so the two cannot disagree."""
from __future__ import annotations

from typing import Mapping, Optional

from .labour_plan import plan_resources, plan_work
from .site_plan import SITE_FACTS, derive_site_facts


def _blank(v) -> bool:
    return v is None or (isinstance(v, str) and not v.strip())


def has_site_data(work: Mapping) -> bool:
    site = work.get("site")
    return isinstance(site, Mapping) and any(not _blank(v) and v != [] for v in site.values())


def build_work_plan(work: Mapping, duration_days: Optional[float], norms: Mapping) -> Optional[dict]:
    """Returns None when there is nothing to work out.  Raises ValueError (with a message for the user) on bad input."""
    nid = work.get("norm_id")
    qty = None if _blank(work.get("quantity")) else work.get("quantity")
    mats = work.get("materials") or []
    if not isinstance(mats, (list, tuple)) or not all(isinstance(m, Mapping) for m in mats):
        raise ValueError("work.materials: expected a list of objects")
    av = work.get("available")
    if av is not None and not isinstance(av, Mapping):
        raise ValueError('work.available: expected an object such as {"masons": 8, "helpers": 18, "bhisti": 2}')
    plan = None
    if not _blank(nid):
        if nid not in norms:
            raise ValueError(f"work.norm_id {nid!r} is not a known labour norm (choose one of: {', '.join(sorted(norms))})")
        if qty is not None and duration_days is not None:
            norm = norms[nid]
            eff = work.get("efficiency")
            plan = plan_work(norm, qty, str(work.get("unit") or norm.unit_basis), duration_days, av or None,
                             1.0 if _blank(eff) else eff, mats)
    if plan is None:
        if _blank(nid) and not mats and not has_site_data(work):
            return None
        plan = plan_resources(mats, qty, duration_days)
    scaff = any(r["class"] == "scaffolding" and (r["required"] or 0) > 0 for r in plan["materials"])
    total = None
    if av:
        vals = [v for v in av.values() if isinstance(v, (int, float)) and not isinstance(v, bool)]
        total = float(sum(vals)) if vals else None
    s = derive_site_facts(work, duration_days=duration_days, quantity=plan.get("quantity"), scaffolding_needed=scaff,
                          workers_total=total)
    plan["derived_facts"].update(s["facts"])
    plan["site"] = {"because": s["because"], "notes": s["notes"], "readiness": s["readiness"]}
    return plan


__all__ = ["build_work_plan", "has_site_data", "SITE_FACTS"]
