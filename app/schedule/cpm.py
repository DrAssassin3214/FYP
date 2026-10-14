"""Critical-path calculation on an imported schedule, in working days, calendar-free.

Forward and backward pass over the leaf (non-summary) tasks with FS, SS, FF and SF links and lags.  Output per task:
early start/finish, late start/finish, total float and a critical flag (total float within 1e-9 of the minimum).
The result is checked against MSP's own Critical flag where the file carries it, and any disagreement is reported rather than hidden.
"""
from __future__ import annotations


from .mspdi import Schedule, ScheduleError

EPS = 1e-9
_MASONRY = ("brick", "block", "masonry", "walling", "wall", "partition", "parapet", "lintel", "sill band")


def analyse(sch: Schedule) -> dict:
    warnings = list(sch.warnings)
    by_uid = {t.uid: t for t in sch.tasks}
    leaf = [t for t in sch.tasks if not t.summary]
    leaf_ids = {t.uid for t in leaf}
    preds = {t.uid: [] for t in leaf}
    for t in leaf:
        for lk in t.links:
            if lk.pred_uid not in by_uid:
                warnings.append(f"Task {t.uid}: predecessor {lk.pred_uid} is not in the file; link ignored.")
            elif lk.pred_uid not in leaf_ids:
                warnings.append(f"Task {t.uid}: link to summary task {lk.pred_uid} ignored.")
            else:
                preds[t.uid].append(lk)
    succs = {u: [] for u in leaf_ids}
    for u, lks in preds.items():
        for lk in lks:
            succs[lk.pred_uid].append((u, lk))
    # topological order (Kahn); a cycle is an error the user must fix in MSP
    indeg = {u: len(p) for u, p in preds.items()}
    order, ready = [], [u for u, d in indeg.items() if d == 0]
    while ready:
        u = ready.pop()
        order.append(u)
        for v, _ in succs[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                ready.append(v)
    if len(order) != len(leaf):
        raise ScheduleError("The task links contain a loop (a task depends on itself through other tasks). Remove the loop in MSP and save again.")
    dur = {t.uid: max(0.0, t.duration_days) for t in leaf}
    es, ef = {}, {}
    for u in order:
        lo = 0.0
        for lk in preds[u]:
            p = lk.pred_uid
            if lk.type == "FS":
                c = ef[p] + lk.lag_days
            elif lk.type == "SS":
                c = es[p] + lk.lag_days
            elif lk.type == "FF":
                c = ef[p] + lk.lag_days - dur[u]
            else:  # SF
                c = es[p] + lk.lag_days - dur[u]
            lo = max(lo, c)
        es[u] = lo
        ef[u] = lo + dur[u]
    finish = max(ef.values())
    ls, lf = {}, {}
    for u in reversed(order):
        hi_f = finish
        for v, lk in succs[u]:
            if lk.type == "FS":
                c = ls[v] - lk.lag_days
            elif lk.type == "SS":
                c = ls[v] - lk.lag_days + dur[u]
            elif lk.type == "FF":
                c = lf[v] - lk.lag_days
            else:
                c = lf[v] - lk.lag_days + dur[u]
            hi_f = min(hi_f, c)
        lf[u] = hi_f
        ls[u] = hi_f - dur[u]
    rows = []
    min_tf = min(ls[u] - es[u] for u in order)
    n_msp_flag = n_disagree = 0
    for t in sch.tasks:
        row = {"uid": t.uid, "id": t.id, "name": t.name, "wbs": t.wbs, "outline_level": t.outline_level, "summary": t.summary,
               "milestone": t.milestone, "duration_days": round(t.duration_days, 4), "start": t.start, "finish": t.finish,
               "percent_complete": t.percent_complete,
               "predecessors": [{"uid": lk.pred_uid, "id": by_uid[lk.pred_uid].id if lk.pred_uid in by_uid else None,
                                 "type": lk.type, "lag_days": round(lk.lag_days, 4)} for lk in t.links]}
        if not t.summary:
            u = t.uid
            tf = ls[u] - es[u]
            crit = tf <= min_tf + EPS
            row.update({"es": round(es[u], 4), "ef": round(ef[u], 4), "ls": round(ls[u], 4), "lf": round(lf[u], 4),
                        "total_float_days": round(tf, 4), "critical": crit})
            row["msp"] = {"start": t.start, "finish": t.finish, "critical": t.msp_critical,
                          "total_slack_days": None if t.msp_slack_days is None else round(t.msp_slack_days, 4)}
            if t.msp_critical is not None:
                n_msp_flag += 1
                if bool(t.msp_critical) != crit:
                    n_disagree += 1
            row["activity"] = _activity_block(sch.name, t, tf)
            row["masonry_like"] = any(k in t.name.lower() for k in _MASONRY) and not t.milestone
        rows.append(row)
    if n_msp_flag and n_disagree:
        warnings.append(f"The critical flag disagrees with MSP's own for {n_disagree} of {n_msp_flag} tasks (MSP uses calendars and "
                        "constraints that are not modelled here). Check the tasks you care about in MSP.")
    # summary rows: span of the tasks nested under them (the rows that follow with a deeper outline level)
    for i, t in enumerate(sch.tasks):
        if not t.summary:
            continue
        kids = []
        for u in sch.tasks[i + 1:]:
            if u.outline_level <= t.outline_level:
                break
            if not u.summary:
                kids.append(u.uid)
        if kids:
            rows[i]["es"] = round(min(es[k] for k in kids), 4)
            rows[i]["ef"] = round(max(ef[k] for k in kids), 4)
    check = _check(sch, rows)
    return {"check": check, "project": {"name": sch.name, "hours_per_day": sch.hours_per_day, "finish_days": round(finish, 4),
                        "tasks": len(sch.tasks), "leaf_tasks": len(leaf), "critical_tasks": sum(1 for r in rows if r.get("critical"))},
            "tasks": rows, "warnings": warnings, "source_note": "Imported from a Microsoft Project XML file"}


def _activity_block(project: str, t, tf: float) -> dict:
    """What the analysis case receives for this task: planned duration as entered in the file, and the duration the task can
    reach before it pushes the project finish (planned + total float), labelled as derived."""
    return {"id": (t.wbs or f"T{t.id}"), "name": t.name,
            "planned_duration_days": {"value": round(t.duration_days, 4), "source": "User Input",
                                       "note": f"From the MSP schedule '{project}', task UID {t.uid}"},
            "deadline_days": {"value": round(t.duration_days + max(0.0, tf), 4), "source": "Derived Calculation",
                              "note": "Planned duration + total float from the critical-path pass: the longest this task can run before the project finish moves. Replace with the contract deadline if you have one."}}


SLACK_TOL = 0.01      # working days


def _check(sch: Schedule, rows: list) -> dict:
    """What was taken from the file, what was left out, and how the tool's float compares with MSP's own total slack.
    Dates are compared later (they need the calendar), see build.compare_dates."""
    rep = dict(sch.report or {})
    cmp_rows = [r for r in rows if "msp" in r and r["msp"]["total_slack_days"] is not None]
    diffs = []
    for r in cmp_rows:
        d = abs(r["total_float_days"] - r["msp"]["total_slack_days"])
        if d > SLACK_TOL:
            diffs.append({"id": r["id"], "name": r["name"], "tool_days": r["total_float_days"], "msp_days": r["msp"]["total_slack_days"]})
    not_modelled = []
    for k, label in (("constraints", "tasks with a date constraint (anything but As Soon As Possible)"), ("task_calendars", "tasks on their own calendar"),
                     ("manual", "manually scheduled tasks"), ("inactive", "inactive tasks"), ("baselines", "tasks carrying a baseline"),
                     ("assignments", "resource assignments"), ("resources", "resources")):
        if rep.get(k):
            not_modelled.append({"what": label, "count": rep[k]})
    return {"read": rep, "not_modelled": not_modelled, "slack_compared": len(cmp_rows), "slack_differences": diffs[:15],
            "slack_difference_count": len(diffs), "critical_compared": sum(1 for r in rows if r.get("msp", {}).get("critical") is not None)}
