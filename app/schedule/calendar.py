"""Project working-time calendar, as in MS Project's "Change Working Time": working weekdays plus dated exceptions
(holidays = non-working, or extra working days).  Durations stay in working days; the calendar turns working-day offsets
into dates.  Task calendars and resource calendars are not modelled."""
from __future__ import annotations

from datetime import date, timedelta

from .mspdi import ScheduleError

MAX_EXCEPTIONS = 500
WEEK = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")


def default_calendar() -> dict:
    return {"name": "Standard", "workdays": [0, 1, 2, 3, 4], "hours_per_day": 8.0, "exceptions": []}


def _d(x, what):
    try:
        return date.fromisoformat(str(x)[:10])
    except ValueError:
        raise ScheduleError(f"Calendar: {what} “{x}” is not a date (use year-month-day).")


def clean_calendar(cal) -> dict:
    """Validate a calendar dict from the GUI or an import; returns a normalised copy."""
    if cal is None:
        return default_calendar()
    if not isinstance(cal, dict):
        raise ScheduleError("Calendar must be an object.")
    wd = sorted({int(x) for x in (cal.get("workdays") if cal.get("workdays") is not None else [0, 1, 2, 3, 4]) if str(x).lstrip("-").isdigit() and 0 <= int(x) <= 6})
    if not wd:
        raise ScheduleError("Calendar: choose at least one working weekday.")
    try:
        hpd = float(8 if cal.get("hours_per_day") is None else cal["hours_per_day"])
    except (TypeError, ValueError):
        raise ScheduleError("Calendar: hours per day must be a number.")
    if not 0 < hpd <= 24:
        raise ScheduleError("Calendar: hours per day must be between 0 and 24.")
    ex = []
    for e in (cal.get("exceptions") or [])[:MAX_EXCEPTIONS]:
        if not isinstance(e, dict):
            continue
        a = _d(e.get("from"), "start date")
        b = _d(e.get("to") or e.get("from"), "end date")
        if b < a:
            raise ScheduleError(f"Calendar: exception “{e.get('name') or a}” ends before it starts.")
        if (b - a).days > 3660:
            raise ScheduleError("Calendar: an exception longer than ten years is not accepted.")
        ex.append({"name": str(e.get("name") or "")[:80], "from": a.isoformat(), "to": b.isoformat(), "working": bool(e.get("working"))})
    return {"name": str(cal.get("name") or "Standard")[:80], "workdays": wd, "hours_per_day": hpd, "exceptions": ex}


class Calendar:
    def __init__(self, cal: dict):
        c = clean_calendar(cal)
        self.data = c
        self.days = set(c["workdays"])
        self._off, self._on = set(), set()
        for e in c["exceptions"]:
            a, b = date.fromisoformat(e["from"]), date.fromisoformat(e["to"])
            for k in range((b - a).days + 1):
                (self._on if e["working"] else self._off).add(a + timedelta(days=k))
                (self._off if e["working"] else self._on).discard(a + timedelta(days=k))

    def is_working(self, d: date) -> bool:
        if d in self._off:
            return False
        return d in self._on or d.weekday() in self.days

    def workdays_before(self, start: date, d: date) -> int:
        """How many working days lie in [start, d): the 0-based working-day offset of the first working day on or after `d`
        when counting from `start`.  0 if `d` is on or before `start`."""
        n, x = 0, start
        while x < d:
            if self.is_working(x):
                n += 1
            x += timedelta(days=1)
        return n

    def workdays_inclusive(self, start: date, finish: date) -> int:
        """Working days in [start, finish] (both ends included); 0 if finish is before start."""
        n, x = 0, start
        while x <= finish:
            if self.is_working(x):
                n += 1
            x += timedelta(days=1)
        return n

    def nth_workday(self, start: date, k: int) -> date:
        """The date of the k-th (0-based) working day on or after `start`."""
        d, n = start, -1
        for _ in range(400000):
            if self.is_working(d):
                n += 1
                if n >= k:
                    return d
            d += timedelta(days=1)
        raise ScheduleError("Calendar: no working days found; check the working weekdays and exceptions.")
