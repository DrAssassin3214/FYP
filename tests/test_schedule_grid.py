"""Rows typed into the schedule grid (MSP-style entry): predecessor syntax, summaries, critical path and dates."""
import pytest

from app.schedule import ScheduleError, analyse
from datetime import date
from app.schedule.build import add_workdays, build_schedule, fill_dates, parse_predecessors



def rows(*r):
    return {"name": "T", "tasks": [{"name": n, "outline_level": lv, "duration_days": d, "predecessors": p} for n, lv, d, p in r]}


def test_pred_syntax():
    ls = parse_predecessors("2, 3SS+2d, 4ff-1.5d", 5, 5)
    assert [(l.pred_uid, l.type, l.lag_days) for l in ls] == [(2, "FS", 0), (3, "SS", 2), (4, "FF", -1.5)]


@pytest.mark.parametrize("bad", ["x", "9", "1", "2XX", "2+"])
def test_bad_predecessors(bad):
    with pytest.raises(ScheduleError):
        parse_predecessors(bad, 5, 1)


def test_diamond_by_hand():
    # A5 -> B3, C2 -> D4: path A-B-D = 12 d, C has 1 d float
    r = analyse(build_schedule(rows(("A", 1, 5, ""), ("B brick wall", 1, 3, "1"), ("C", 1, 2, "1"), ("D", 1, 4, "2, 3"))))
    by = {t["id"]: t for t in r["tasks"]}
    assert r["project"]["finish_days"] == pytest.approx(12)
    assert by[3]["total_float_days"] == pytest.approx(1) and not by[3]["critical"]
    assert by[2]["critical"] and by[2]["masonry_like"]


def test_summary_and_milestone():
    r = analyse(build_schedule(rows(("Phase", 1, 0, ""), ("A", 2, 4, ""), ("B", 2, 6, "2"), ("Done", 1, 0, "3"))))
    by = {t["id"]: t for t in r["tasks"]}
    assert by[1]["summary"] and by[1]["es"] == 0 and by[1]["ef"] == 10
    assert by[4]["milestone"] and r["project"]["finish_days"] == 10


def test_loop_is_refused():
    with pytest.raises(ScheduleError):
        analyse(build_schedule(rows(("A", 1, 1, "2"), ("B", 1, 1, "1"))))


def test_workdays_skip_weekend():
    assert add_workdays(date(2026, 10, 16), 1) == date(2026, 10, 19)   # Fri start, offset 1 = next working day Mon
    r = analyse(build_schedule(rows(("A", 1, 2, ""))))
    fill_dates(r, "2026-10-14")                                        # Wed: 2 d task ends Thu
    assert r["tasks"][0]["start"] == "2026-10-14" and r["tasks"][0]["finish"] == "2026-10-15"


def test_api_compute_route():
    from gui.api import create_app
    c = create_app().test_client()
    body = {**rows(("A", 1, 5, ""), ("B", 1, 3, "1")), "start": "2026-10-14"}
    d = c.post("/api/schedule/compute", json=body).get_json()
    assert d["ok"] and d["project"]["finish_days"] == 8 and d["tasks"][1]["activity"]["planned_duration_days"]["value"] == 3
    bad = c.post("/api/schedule/compute", json=rows(("A", 1, 1, "7")))
    assert bad.status_code == 422


def test_calendar_holiday_and_saturday():
    cal = {"workdays": [0, 1, 2, 3, 4, 5], "exceptions": [{"name": "Diwali", "from": "2026-11-09", "to": "2026-11-10", "working": False}]}
    r = analyse(build_schedule(rows(("A", 1, 6, ""), ("B", 1, 2, "1"))))
    fill_dates(r, "2026-11-05", cal)                       # Thu 5 Nov start, six-day week, Mon 9 + Tue 10 off
    a, b = r["tasks"]
    assert a["start"] == "2026-11-05" and a["finish"] == "2026-11-13"   # Thu Fri Sat, Wed Thu Fri
    assert b["start"] == "2026-11-14" and b["finish"] == "2026-11-16"   # Sat, then Mon 16 (Sun off; 9-10 already passed)


def test_calendar_errors():
    from app.schedule.calendar import clean_calendar
    for bad in ({"workdays": []}, {"hours_per_day": 0}, {"exceptions": [{"from": "x"}]}, {"exceptions": [{"from": "2026-02-02", "to": "2026-02-01"}]}):
        with pytest.raises(ScheduleError):
            clean_calendar(bad)


def test_msp_calendar_import():
    from app.schedule import parse_mspdi
    ns = "http://schemas.microsoft.com/project"
    wk = "".join(f"<WeekDay><DayType>{i}</DayType><DayWorking>{0 if i in (1,) else 1}</DayWorking></WeekDay>" for i in range(1, 8))
    x = (f'<Project xmlns="{ns}"><Name>P</Name><CalendarUID>1</CalendarUID><Calendars><Calendar><UID>1</UID><Name>Site</Name><IsBaseCalendar>1</IsBaseCalendar>'
         f'<WeekDays>{wk}</WeekDays><Exceptions><Exception><Name>Holi</Name><TimePeriod><FromDate>2026-03-04T00:00:00</FromDate><ToDate>2026-03-04T23:59:00</ToDate></TimePeriod><DayWorking>0</DayWorking></Exception></Exceptions>'
         f'</Calendar></Calendars><Tasks><Task><UID>1</UID><ID>1</ID><Name>A</Name><Duration>PT8H0M0S</Duration></Task></Tasks></Project>').encode()
    cal = parse_mspdi(x).calendar
    assert cal["workdays"] == [0, 1, 2, 3, 4, 5] and cal["exceptions"][0]["from"] == "2026-03-04" and cal["name"] == "Site"


def test_bundled_example_hand_values_and_consistency():
    """Masonry work-package example: hand-worked early start/finish (working days), and the XML file, the case's schedule rows
    and the case's activity (task 5, 16 d) all agree."""
    from pathlib import Path
    from app import service
    from app.schedule import parse_mspdi
    xml = analyse(parse_mspdi((Path(__file__).resolve().parents[1] / "examples" / "example_schedule_msp.xml").read_bytes()))
    by = {t["id"]: t for t in xml["tasks"]}
    hand = {3: (0, 2), 4: (2, 3), 5: (3, 19), 6: (7, 17), 7: (9, 13), 8: (19, 22), 10: (22, 32), 11: (32, 34), 12: (34, 50),
            13: (38, 48), 14: (40, 44), 15: (50, 53), 17: (53, 59)}
    for i, (a, b) in hand.items():
        assert (by[i]["es"], by[i]["ef"]) == (a, b), i
    assert xml["project"]["finish_days"] == 59 and xml["project"]["critical_tasks"] == 10
    case = service.example_analysis_case()
    rows = analyse(build_schedule({"name": "x", "tasks": case["schedule"]["rows"]}))
    assert [(t["es"], t["ef"]) for t in rows["tasks"] if "es" in t] == [(t["es"], t["ef"]) for t in xml["tasks"] if "es" in t]
    assert by[5]["duration_days"] == case["activity"]["planned_duration_days"]["value"] == 16 and by[5]["masonry_like"]


def test_example_case_marks_the_assessed_task():
    from app import service
    case = service.example_analysis_case()
    sch = case["schedule"]
    row = sch["rows"][sch["assessed"] - 1]
    assert row["name"] == "Brick masonry, ground-floor external walls" and row["duration_days"] == case["activity"]["planned_duration_days"]["value"]
    assert row["facts"] == case["facts"]          # one source: the assessed task's facts are the case's facts
