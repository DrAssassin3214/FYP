"""Build a Schedule from rows typed into the schedule grid (MSP-style entry), then reuse the same critical-path pass.

Row: {"name", "outline_level", "duration_days", "predecessors": "3FS+2d, 5SS"}.  The row number is the task ID, as in MSP.
Predecessor syntax follows MSP: an ID alone means finish-to-start; FS/SS/FF/SF after it sets the type; "+2d"/"-1d" is a lag.
A row is a summary task when the next row sits one outline level deeper (as in MSP); a leaf with duration 0 is a milestone.
Dates run through the project calendar (working weekdays and holiday exceptions, see calendar.py) from the project start.
"""
from __future__ import annotations

import re
from datetime import date

from .mspdi import Link, Schedule, ScheduleError, Task

MAX_ROWS = 2000
_PRED = re.compile(r"^\s*(\d+)\s*(FS|SS|FF|SF)?\s*(?:([+-])\s*(\d+(?:\.\d+)?)\s*d?)?\s*$", re.I)


def parse_predecessors(text, n_rows: int, own_id: int) -> list:
    out = []
    for part in re.split(r"[;,]", str(text or "")):
        if not part.strip():
            continue
        m = _PRED.match(part)
        if not m:
            raise ScheduleError(f"Task {own_id}: predecessor “{part.strip()}” is not understood. Write it like 3, 3FS, 5SS+2d or 4FF-1d.")
        pid = int(m.group(1))
        if pid == own_id:
            raise ScheduleError(f"Task {own_id} cannot be its own predecessor.")
        if not 1 <= pid <= n_rows:
            raise ScheduleError(f"Task {own_id}: predecessor {pid} does not exist (rows are 1 to {n_rows}).")
        lag = float(m.group(4) or 0) * (-1 if m.group(3) == "-" else 1)
        out.append(Link(pred_uid=pid, type=(m.group(2) or "FS").upper(), lag_days=lag))
    return out


def add_workdays(start: date, n: float, cal=None) -> date:
    """Date of working-day offset n (0 = first working day on or after `start`)."""
    from .calendar import Calendar
    return (cal or Calendar(None)).nth_workday(start, max(0, int(round(n))))


def build_schedule(payload: dict) -> Schedule:
    rows = payload.get("tasks")
    if not isinstance(rows, list) or not rows:
        raise ScheduleError("Add at least one task row.")
    if len(rows) > MAX_ROWS:
        raise ScheduleError(f"At most {MAX_ROWS} rows are accepted.")
    tasks = []
    for i, r in enumerate(rows, 1):
        if not isinstance(r, dict):
            raise ScheduleError(f"Row {i} is not a task.")
        name = str(r.get("name") or "").strip() or f"Task {i}"
        try:
            lvl = int(r.get("outline_level") or 1)
            dur = float(r.get("duration_days") or 0)
        except (TypeError, ValueError):
            raise ScheduleError(f"Row {i}: level and duration must be numbers.")
        if not 1 <= lvl <= 9:
            raise ScheduleError(f"Row {i}: outline level must be between 1 and 9.")
        if i == 1 and lvl != 1:
            lvl = 1
        if tasks and lvl > tasks[-1].outline_level + 1:
            lvl = tasks[-1].outline_level + 1
        if not 0 <= dur <= 100000:
            raise ScheduleError(f"Row {i}: duration must be 0 or more days.")
        tasks.append(Task(uid=i, id=i, name=name[:200], outline_level=lvl, duration_days=dur,
                          links=parse_predecessors(r.get("predecessors"), len(rows), i)))
    for i, t in enumerate(tasks):
        t.summary = i + 1 < len(tasks) and tasks[i + 1].outline_level > t.outline_level
        t.milestone = (not t.summary) and t.duration_days == 0
        if t.summary:
            t.links = []
    return Schedule(name=str(payload.get("name") or "Project")[:120], hours_per_day=8.0, tasks=tasks, warnings=[])


def fill_dates(res: dict, start_text, calendar=None) -> None:
    """Start and finish dates from the working-day offsets, through the project calendar."""
    from .calendar import Calendar
    try:
        start = date.fromisoformat(str(start_text)[:10])
    except ValueError:
        return
    cal = Calendar(calendar)
    for r in res["tasks"]:
        if "es" in r:
            k0 = int(round(r["es"]))
            r["start"] = cal.nth_workday(start, k0).isoformat()
            r["finish"] = cal.nth_workday(start, max(int(round(r["ef"])) - 1, k0) if r["ef"] > r["es"] else k0).isoformat()
    res["project"]["start"] = start.isoformat()
    res["calendar"] = cal.data
