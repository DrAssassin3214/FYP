"""MSP XML import and the critical-path pass, checked against hand-worked values."""
import pytest

from app.schedule import ScheduleError, analyse, parse_mspdi

NS = "http://schemas.microsoft.com/project"


def _xml(tasks, minutes_per_day=480, extra=""):
    body = "".join(tasks)
    return (f'<?xml version="1.0" encoding="UTF-8"?><Project xmlns="{NS}"><Name>Test block</Name>'
            f"<MinutesPerDay>{minutes_per_day}</MinutesPerDay>{extra}<Tasks>{body}</Tasks></Project>").encode()


def _t(uid, name, days, preds=(), summary=0, level=1, critical=None):
    links = "".join(f"<PredecessorLink><PredecessorUID>{p}</PredecessorUID><Type>{ty}</Type><LinkLag>{int(lag * 4800)}</LinkLag></PredecessorLink>"
                    for p, ty, lag in preds)
    crit = f"<Critical>{critical}</Critical>" if critical is not None else ""
    return (f"<Task><UID>{uid}</UID><ID>{uid}</ID><Name>{name}</Name><OutlineLevel>{level}</OutlineLevel><Summary>{summary}</Summary>"
            f"<Duration>PT{int(days * 8)}H0M0S</Duration><Start>2026-01-01T08:00:00</Start><Finish>2026-01-09T17:00:00</Finish>{links}{crit}</Task>")


def _diamond():
    return _xml([_t(1, "A", 5), _t(2, "B Brick masonry wall", 3, [(1, 1, 0)]), _t(3, "C", 2, [(1, 1, 0)]), _t(4, "D", 4, [(2, 1, 0), (3, 1, 0)])])


def test_diamond_float_and_critical():
    r = analyse(parse_mspdi(_diamond()))
    by = {t["uid"]: t for t in r["tasks"]}
    assert r["project"]["finish_days"] == pytest.approx(12.0)
    assert by[3]["total_float_days"] == pytest.approx(1.0) and not by[3]["critical"]
    assert by[2]["total_float_days"] == pytest.approx(0.0) and by[2]["critical"]
    assert r["project"]["critical_tasks"] == 3
    assert by[2]["masonry_like"] and not by[3]["masonry_like"]


def test_activity_block_uses_float_and_labels_sources():
    r = analyse(parse_mspdi(_diamond()))
    a = {t["uid"]: t for t in r["tasks"]}[3]["activity"]
    assert a["planned_duration_days"] == {"value": 2.0, "source": "User Input", "note": a["planned_duration_days"]["note"]}
    assert a["deadline_days"]["value"] == pytest.approx(3.0) and a["deadline_days"]["source"] == "Derived Calculation"


def test_lag_ss_and_hours_per_day():
    # 6-hour working day: 12 h = 2 days; SS link with 1 day lag (1 day = 360 min = 3600 tenths)
    x = (f'<Project xmlns="{NS}"><MinutesPerDay>360</MinutesPerDay><Tasks>'
         "<Task><UID>1</UID><ID>1</ID><Name>P</Name><Duration>PT12H0M0S</Duration></Task>"
         "<Task><UID>2</UID><ID>2</ID><Name>Q</Name><Duration>PT6H0M0S</Duration>"
         "<PredecessorLink><PredecessorUID>1</PredecessorUID><Type>3</Type><LinkLag>3600</LinkLag></PredecessorLink></Task>"
         "</Tasks></Project>").encode()
    r = analyse(parse_mspdi(x))
    by = {t["uid"]: t for t in r["tasks"]}
    assert by[1]["duration_days"] == pytest.approx(2.0) and by[2]["duration_days"] == pytest.approx(1.0)
    assert by[2]["es"] == pytest.approx(1.0)
    assert r["project"]["finish_days"] == pytest.approx(2.0)      # P ends at 2; Q ends at 2 -> both critical


def test_summary_tasks_are_not_scheduled():
    x = _xml([_t(1, "Phase", 9, summary=1), _t(2, "A", 5, level=2), _t(3, "B", 4, [(2, 1, 0)], level=2)])
    r = analyse(parse_mspdi(x))
    s = [t for t in r["tasks"] if t["summary"]][0]
    assert "total_float_days" not in s and r["project"]["finish_days"] == pytest.approx(9.0)
    assert (s["es"], s["ef"]) == (0.0, 9.0)


def test_loop_is_an_error():
    with pytest.raises(ScheduleError, match="loop"):
        analyse(parse_mspdi(_xml([_t(1, "A", 1, [(2, 1, 0)]), _t(2, "B", 1, [(1, 1, 0)])])))


@pytest.mark.parametrize("data,msg", [
    (b"\xd0\xcf\x11\xe0 native mpp", "native .mpp"),
    (b"not xml at all", "not valid XML"),
    (b'<?xml version="1.0"?><!DOCTYPE x [<!ENTITY a "b">]><Project xmlns="http://schemas.microsoft.com/project"/>', "DOCTYPE"),
    (b"<Other/>", "not a Microsoft Project"),
    (_xml([]), "no tasks"),
])
def test_bad_files_are_refused_with_a_plain_message(data, msg):
    with pytest.raises(ScheduleError, match=msg):
        parse_mspdi(data)


def test_msp_critical_flag_disagreement_is_reported():
    x = _xml([_t(1, "A", 5, critical=1), _t(2, "B", 3, [(1, 1, 0)], critical=0)])
    r = analyse(parse_mspdi(x))
    assert any("disagrees with MSP" in w for w in r["warnings"])


def test_warns_that_calendars_are_not_modelled():
    assert any("task and resource calendars" in w for w in analyse(parse_mspdi(_diamond()))["warnings"])


def test_api_import_route():
    from gui.api import create_app
    c = create_app().test_client()
    r = c.post("/api/schedule/import", data=_diamond(), content_type="application/xml")
    j = r.get_json()
    assert r.status_code == 200 and j["ok"] and j["project"]["leaf_tasks"] == 4
    bad = c.post("/api/schedule/import", data=b"junk", content_type="application/xml")
    assert bad.status_code == 422 and bad.get_json()["problems"]
