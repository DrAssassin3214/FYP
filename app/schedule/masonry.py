"""Reduce an imported whole-project schedule to its masonry work package.

Only the brick and block tasks (by name, see cpm.is_masonry) and their labour and material assignments are kept. The rest of the programme
is not shown, but its *effect* on the kept tasks is: each kept task's earliest start that comes from left-out predecessors becomes a
start-to-start link from a "Programme start" milestone, and the room the left-out successors (and the project finish) leave it becomes a
link to a "Programme finish" milestone. So the kept tasks keep the same dates and total float as in the full programme (checked against
MS Project's own total slack by the Import check).
"""
from __future__ import annotations

from .cpm import analyse, is_masonry
from .mspdi import Link, Schedule, Task

EPS = 1e-9


def masonry_only(sch: Schedule):
    """Returns (reduced Schedule, resources by new task id, info dict). If no masonry task is found the schedule is returned unchanged."""
    full = analyse(sch)
    rows = {r["uid"]: r for r in full["tasks"]}
    leaf = {t.uid for t in sch.tasks if not t.summary}
    keep = {t.uid for t in sch.tasks if not t.summary and not t.milestone and is_masonry(t.name)}
    info = {"mode": "masonry", "tasks_in_file": len(sch.tasks), "masonry_found": len(keep)}
    if not keep:
        info.update(mode="all", note="No task name mentions brick, block, masonry, wall, partition, parapet or lintel, so the whole schedule was kept.")
        return sch, {}, info
    P = full["project"]["finish_days"]
    # summary rows that contain a kept task
    order, keep_rows = sch.tasks, []
    for i, t in enumerate(order):
        if t.uid in keep:
            keep_rows.append(t)
        elif t.summary:
            for u in order[i + 1:]:
                if u.outline_level <= t.outline_level:
                    break
                if u.uid in keep:
                    keep_rows.append(t)
                    break
    new_id = {t.uid: k + 2 for k, t in enumerate(keep_rows)}            # row 1 is the programme-start milestone
    n_last = len(keep_rows) + 2                                          # last row: programme-finish milestone
    succ = {u: [] for u in leaf}
    for v in sch.tasks:
        if v.uid in leaf:
            for lk in v.links:
                if lk.pred_uid in leaf:
                    succ[lk.pred_uid].append((v.uid, lk))
    S = Task(uid=1, id=1, name="Programme start (earlier non-masonry work)", outline_level=1, milestone=True)
    tasks, n_s, n_f = [S], 0, 0
    fin_links = []
    for t in keep_rows:
        nt = Task(uid=new_id[t.uid], id=new_id[t.uid], name=t.name, wbs=t.wbs, outline_level=t.outline_level, summary=t.summary,
                  milestone=t.milestone, duration_days=t.duration_days, start=t.start, finish=t.finish,
                  percent_complete=t.percent_complete, msp_critical=t.msp_critical, msp_slack_days=t.msp_slack_days)
        if not t.summary:
            d = max(0.0, t.duration_days)
            ext = 0.0
            for lk in t.links:                                           # predecessors that are left out
                if lk.pred_uid in keep or lk.pred_uid not in leaf:
                    if lk.pred_uid in keep:
                        nt.links.append(Link(new_id[lk.pred_uid], lk.type, lk.lag_days))
                    continue
                pr = rows[lk.pred_uid]
                c = {"FS": pr["ef"] + lk.lag_days, "SS": pr["es"] + lk.lag_days,
                     "FF": pr["ef"] + lk.lag_days - d, "SF": pr["es"] + lk.lag_days - d}[lk.type]
                ext = max(ext, c)
            if ext > EPS:
                nt.links.append(Link(1, "SS", round(ext, 6)))
                n_s += 1
            outs = succ.get(t.uid, [])
            dropped = [(v, lk) for v, lk in outs if v not in keep]
            if dropped or not outs:
                hi = P
                for v, lk in dropped:
                    vr = rows[v]
                    c = {"FS": vr["ls"] - lk.lag_days, "SS": vr["ls"] - lk.lag_days + d,
                         "FF": vr["lf"] - lk.lag_days, "SF": vr["lf"] - lk.lag_days + d}[lk.type]
                    hi = min(hi, c)
                fin_links.append(Link(nt.uid, "FS", round(max(0.0, P - hi), 6)))
                n_f += 1
        tasks.append(nt)
    F = Task(uid=n_last, id=n_last, name="Programme finish (later non-masonry work)", outline_level=1, milestone=True, links=fin_links)
    if P > EPS:
        F.links.append(Link(1, "SS", P))
    tasks.append(F)
    prev = 0
    for t in tasks:                                                      # keep outline levels contiguous after dropping rows
        t.outline_level = 1 if prev == 0 else min(t.outline_level, prev + 1)
        prev = t.outline_level
    red = Schedule(name=sch.name, hours_per_day=sch.hours_per_day, tasks=tasks, warnings=list(sch.warnings), calendar=sch.calendar,
                   project_start=sch.project_start, resources=sch.resources, assignments=sch.assignments, report=sch.report)
    # labour and material of the kept tasks only
    res = {}
    for a in sch.assignments or []:
        if a["task_uid"] in keep and a["res_uid"] in (sch.resources or {}):
            r = sch.resources[a["res_uid"]]
            bucket = res.setdefault(new_id[a["task_uid"]], {"labour": [], "material": []})
            if r["type"] == 1:
                bucket["labour"].append({"name": r["name"], "units": round(a["units"], 4)})
            elif r["type"] == 0:
                bucket["material"].append({"name": r["name"], "quantity": round(a["units"], 4), "unit": r["label"]})
    left = [t.name for t in sch.tasks if not t.summary and t.uid not in keep]
    info.update(kept=len(keep), left_out=len(left), left_out_examples=left[:8], start_links=n_s, finish_links=n_f,
                assignments_used=sum(len(b["labour"]) + len(b["material"]) for b in res.values()))
    return red, res, info
