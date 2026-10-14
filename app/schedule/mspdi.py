"""Read a Microsoft Project schedule saved as XML (File > Save As > XML Format, the "MSPDI" format).

Only what the tool needs is read: project name and calendar hours per day, and for every task its ids, name, outline
level, summary / milestone flags, duration, start and finish dates, percent complete, MSP's own Critical flag and the
predecessor links (type and lag).  Native .mpp files are NOT read; Primavera .xer is not read yet.

Durations are converted to WORKING DAYS using the file's own minutes-per-day (default 480).  Calendars, resource
levelling and date constraints are not modelled; the caller is told so in `warnings`.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional

MAX_BYTES = 30 * 1024 * 1024
MAX_TASKS = 20000
_LINK_TYPES = {0: "FF", 1: "FS", 2: "SF", 3: "SS"}
_DUR = re.compile(r"^P(?:(\d+)D)?(?:T(?:(\d+(?:\.\d+)?)H)?(?:(\d+(?:\.\d+)?)M)?(?:(\d+(?:\.\d+)?)S)?)?$")


class ScheduleError(ValueError):
    """The file is not a usable MSP XML schedule; the message says why in plain words."""


@dataclass
class Link:
    pred_uid: int
    type: str = "FS"
    lag_days: float = 0.0


@dataclass
class Task:
    uid: int
    id: int
    name: str
    wbs: str = ""
    outline_level: int = 1
    summary: bool = False
    milestone: bool = False
    duration_days: float = 0.0
    start: str = ""
    finish: str = ""
    percent_complete: float = 0.0
    msp_critical: Optional[bool] = None
    msp_slack_days: Optional[float] = None     # MSP's own total slack, in working days of its hours-per-day
    links: list = field(default_factory=list)


@dataclass
class Schedule:
    name: str
    hours_per_day: float
    tasks: list
    warnings: list
    calendar: Optional[dict] = None
    project_start: str = ""
    report: Optional[dict] = None              # what was read and what was not (see parse_mspdi)


def _strip(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _child(el, name):
    for c in el:
        if _strip(c.tag) == name:
            return c
    return None


def _text(el, name, default=""):
    c = _child(el, name)
    return (c.text or "").strip() if c is not None and c.text is not None else default


def _bool(s):
    return s.strip().lower() in ("1", "true") if s else False


def _duration_hours(s: str) -> Optional[float]:
    m = _DUR.match((s or "").strip())
    if not m or not any(m.groups()):
        return None
    d, h, mi, sec = (float(x) if x else 0.0 for x in m.groups())
    return d * 24.0 + h + mi / 60.0 + sec / 3600.0   # a "D" part would be calendar days; MSP writes hours


def parse_mspdi(data: bytes) -> Schedule:
    if not isinstance(data, (bytes, bytearray)):
        raise ScheduleError("The file could not be read as bytes.")
    if len(data) > MAX_BYTES:
        raise ScheduleError(f"The file is larger than {MAX_BYTES // (1024 * 1024)} MB.")
    head = bytes(data[:4096]).lower()
    if data[:2] == b"\xd0\xcf":
        raise ScheduleError("This is a native .mpp file. In Microsoft Project use File > Save As and choose 'XML Format', then open that file.")
    if b"<!doctype" in bytes(data).lower()[:20000] or b"<!entity" in bytes(data).lower()[:20000]:
        raise ScheduleError("The file contains a DOCTYPE or ENTITY declaration, which this reader refuses for safety.")
    try:
        root = ET.fromstring(bytes(data))
    except ET.ParseError as e:
        raise ScheduleError(f"The file is not valid XML ({e}).")
    if _strip(root.tag) != "Project" or b"schemas.microsoft.com/project" not in head + bytes(data[:20000]).lower():
        raise ScheduleError("This is not a Microsoft Project XML file (expected a <Project> element in the Microsoft Project namespace).")
    warnings: list = []
    mpd = _text(root, "MinutesPerDay")
    try:
        minutes_per_day = float(mpd) if mpd else 480.0
    except ValueError:
        minutes_per_day = 480.0
    if minutes_per_day <= 0:
        minutes_per_day = 480.0
    hpd = minutes_per_day / 60.0
    tasks_el = _child(root, "Tasks")
    if tasks_el is None:
        raise ScheduleError("The file has no <Tasks> section.")
    tasks = []
    seen = set()
    rep = {"tasks_in_file": 0, "tasks_read": 0, "links_read": 0, "links_skipped": 0, "constraints": 0, "manual": 0, "inactive": 0,
           "task_calendars": 0, "baselines": 0, "assignments": 0, "resources": 0}
    for el in root:
        if _strip(el.tag) == "Resources":
            rep["resources"] = sum(1 for r in el if _strip(r.tag) == "Resource" and _text(r, "UID") not in ("0", ""))
        elif _strip(el.tag) == "Assignments":
            rep["assignments"] = sum(1 for a in el if _strip(a.tag) == "Assignment")
    for t in tasks_el:
        if _strip(t.tag) != "Task":
            continue
        uid_s = _text(t, "UID")
        if not uid_s.lstrip("-").isdigit():
            continue
        uid = int(uid_s)
        rep["tasks_in_file"] += 1
        if uid == 0 and not _text(t, "Name"):
            continue                       # MSP's hidden project-summary row without a name
        if uid in seen:
            raise ScheduleError(f"Task UID {uid} appears twice.")
        seen.add(uid)
        if len(tasks) >= MAX_TASKS:
            raise ScheduleError(f"More than {MAX_TASKS} tasks; split the schedule.")
        hours = _duration_hours(_text(t, "Duration"))
        if hours is None:
            warnings.append(f"Task {uid}: duration '{_text(t, 'Duration')}' not understood; taken as 0.")
            hours = 0.0
        if _text(t, "Manual") in ("1", "true") or _text(t, "ManualDuration"):
            rep["manual"] += 1
            warnings.append(f"Task {uid}: manually scheduled in MSP; its automatic duration is used.")
        if _text(t, "ConstraintType") not in ("", "0"):
            rep["constraints"] += 1                     # 0 = as soon as possible; anything else moves dates in MSP
        if _text(t, "Active") in ("0", "false"):
            rep["inactive"] += 1
        tcal = _text(t, "CalendarUID")
        if tcal and tcal not in ("-1", _text(root, "CalendarUID")):
            rep["task_calendars"] += 1
        if any(_strip(c.tag) == "Baseline" for c in t):
            rep["baselines"] += 1
        task = Task(uid=uid, id=int(_text(t, "ID") or 0), name=_text(t, "Name") or f"(task {uid})", wbs=_text(t, "WBS"),
                    outline_level=int(_text(t, "OutlineLevel") or 1), summary=_bool(_text(t, "Summary")),
                    milestone=_bool(_text(t, "Milestone")), duration_days=hours / hpd, start=_text(t, "Start"),
                    finish=_text(t, "Finish"), percent_complete=float(_text(t, "PercentComplete") or 0),
                    msp_critical=(_bool(_text(t, "Critical")) if _child(t, "Critical") is not None else None),
                    msp_slack_days=(float(_text(t, "TotalSlack")) / 10.0 / 60.0 / hpd if re.fullmatch(r"-?\d+(\.\d+)?", _text(t, "TotalSlack") or "x") else None))
        for pl in t:
            if _strip(pl.tag) != "PredecessorLink":
                continue
            pu = _text(pl, "PredecessorUID")
            if not pu.lstrip("-").isdigit():
                rep["links_skipped"] += 1
                continue
            ty = _LINK_TYPES.get(int(_text(pl, "Type") or 1))
            if ty is None:
                warnings.append(f"Task {uid}: unknown link type; taken as finish-to-start.")
                ty = "FS"
            lag_fmt = _text(pl, "LagFormat")
            if lag_fmt in ("19", "20", "21", "22", "35", "36", "37", "38"):    # percent / elapsed formats
                warnings.append(f"Task {uid}: a lag given as a percentage or elapsed time is ignored (taken as 0).")
                lag = 0.0
            else:
                lag = float(_text(pl, "LinkLag") or 0) / 10.0 / 60.0 / hpd      # tenths of a minute -> working days
            task.links.append(Link(int(pu), ty, lag))
            rep["links_read"] += 1
        tasks.append(task)
        rep["tasks_read"] += 1
    if not tasks:
        raise ScheduleError("The file has no tasks.")
    if not any(not t.summary for t in tasks):
        raise ScheduleError("The file has only summary tasks.")
    cal = _project_calendar(root, hpd, warnings)
    warnings.append("The project calendar (working days and holidays) is read; task and resource calendars, resource levelling and date "
                    "constraints in the MSP file are not modelled. Durations are working days from the file's hours per day.")
    return Schedule(name=_text(root, "Name") or _text(root, "Title") or "Imported schedule", hours_per_day=hpd, tasks=tasks,
                    warnings=warnings, calendar=cal, project_start=_text(root, "StartDate"), report=rep)


def _cal_el(root, uid):
    cals = _child(root, "Calendars")
    if cals is None:
        return None
    for c in cals:
        if _strip(c.tag) == "Calendar" and _text(c, "UID") == str(uid):
            return c
    return None


def _project_calendar(root, hpd, warnings):
    """Working weekdays and dated exceptions of the project's calendar (base calendars followed), or None."""
    uid = _text(root, "CalendarUID")
    el = _cal_el(root, uid) if uid else None
    if el is None:
        return None
    chain, seen = [], set()
    while el is not None and _text(el, "UID") not in seen:
        seen.add(_text(el, "UID"))
        chain.append(el)
        base = _text(el, "BaseCalendarUID")
        el = _cal_el(root, base) if base and base != "-1" else None
    days, exc = {}, []
    for c in reversed(chain):                       # base first, the project calendar overrides
        wds = _child(c, "WeekDays")
        for wd in (wds if wds is not None else []):
            dt = _text(wd, "DayType")
            if dt.isdigit() and 1 <= int(dt) <= 7:
                days[(int(dt) - 2) % 7] = _bool(_text(wd, "DayWorking"))
            elif dt == "0":
                tp = _child(wd, "TimePeriod")
                if tp is not None:
                    exc.append((_text(tp, "FromDate"), _text(tp, "ToDate"), _text(wd, "DayWorking"), _text(wd, "Name") or _text(c, "Name")))
        exs = _child(c, "Exceptions")
        for e in (exs if exs is not None else []):
            tp = _child(e, "TimePeriod")
            if tp is not None:
                exc.append((_text(tp, "FromDate"), _text(tp, "ToDate"), _text(e, "DayWorking"), _text(e, "Name")))
    if not days:
        return None
    out = []
    for a, b, w, nm in exc[:500]:
        if len(a) >= 10 and len(b) >= 10:
            out.append({"name": nm, "from": a[:10], "to": b[:10], "working": _bool(w)})
    wd = sorted(k for k, v in days.items() if v) or [0, 1, 2, 3, 4]
    return {"name": _text(_cal_el(root, uid), "Name") or "Project calendar", "workdays": wd, "hours_per_day": hpd, "exceptions": out}
