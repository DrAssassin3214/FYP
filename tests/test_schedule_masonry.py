"""Masonry-only import: the kept tasks keep their dates and float from the full programme; labour and material come only from them."""
import pytest

from app.schedule import analyse, parse_mspdi
from app.schedule.masonry import masonry_only
from tests.test_schedule_msp import NS, _t


def _project(extra=""):
    tasks = [_t(1, "Excavation", 5), _t(2, "Column and slab GF", 8, [(1, 1, 0)]), _t(3, "Brick masonry GF", 6, [(2, 1, 0)]),
             _t(4, "Plaster GF", 4, [(3, 1, 0)]), _t(5, "Electrical rough-in", 3, [(2, 1, 0)]),
             _t(6, "Brick masonry FF", 6, [(3, 1, 0), (5, 1, 0)]), _t(7, "Handover", 2, [(4, 1, 0), (6, 1, 0)])]
    return (f'<?xml version="1.0" encoding="UTF-8"?><Project xmlns="{NS}"><Name>Full</Name><MinutesPerDay>480</MinutesPerDay>{extra}'
            f"<Tasks>{''.join(tasks)}</Tasks></Project>").encode()


def test_kept_tasks_keep_dates_and_float_of_the_full_programme():
    sch = parse_mspdi(_project())
    full = {t["name"]: t for t in analyse(sch)["tasks"]}
    assert (full["Brick masonry GF"]["es"], full["Brick masonry GF"]["ef"]) == (13, 19)        # hand: 5+8 = 13, +6 = 19
    red, _, info = masonry_only(sch)
    r = analyse(red)
    names = [t["name"] for t in r["tasks"]]
    assert names[0].startswith("Programme start") and names[-1].startswith("Programme finish") and len(names) == 4
    assert info["kept"] == 2 and info["left_out"] == 5 and info["mode"] == "masonry"
    by = {t["name"]: t for t in r["tasks"]}
    for n in ("Brick masonry GF", "Brick masonry FF"):
        for k in ("es", "ef", "total_float_days", "critical"):
            assert by[n][k] == full[n][k], (n, k)
    assert r["project"]["finish_days"] == 27


def test_float_survives_when_a_left_out_successor_has_room():
    # masonry task whose only successor is a left-out task with slack
    x = _project().replace(b"<Name>Electrical rough-in</Name>", b"<Name>Electrical rough-in</Name>")
    sch = parse_mspdi(x)
    full = {t["name"]: t for t in analyse(sch)["tasks"]}
    sch2 = masonry_only(sch)[0]
    r = {t["name"]: t for t in analyse(sch2)["tasks"]}
    assert r["Brick masonry GF"]["total_float_days"] == full["Brick masonry GF"]["total_float_days"]


def test_no_masonry_task_keeps_everything():
    x = _project().replace(b"Brick masonry", b"Plain work")
    sch = parse_mspdi(x)
    red, _, info = masonry_only(sch)
    assert red is sch and info["mode"] == "all"


def test_labour_and_material_only_for_kept_tasks():
    extra = ("<Resources><Resource><UID>0</UID><Name></Name></Resource>"
             "<Resource><UID>1</UID><Name>Mason gang</Name><Type>1</Type></Resource>"
             "<Resource><UID>2</UID><Name>Fly-ash bricks</Name><Type>0</Type><MaterialLabel>nos</MaterialLabel></Resource>"
             "<Resource><UID>3</UID><Name>Electrician</Name><Type>1</Type></Resource></Resources>"
             "<Assignments><Assignment><TaskUID>3</TaskUID><ResourceUID>1</ResourceUID><Units>6</Units></Assignment>"
             "<Assignment><TaskUID>3</TaskUID><ResourceUID>2</ResourceUID><Units>12000</Units></Assignment>"
             "<Assignment><TaskUID>5</TaskUID><ResourceUID>3</ResourceUID><Units>2</Units></Assignment></Assignments>")
    sch = parse_mspdi(_project(extra))
    assert sch.report["resources"] == 3 and sch.report["assignments"] == 3
    _, res, info = masonry_only(sch)
    (rid, b), = res.items()
    assert b["labour"] == [{"name": "Mason gang", "units": 6.0}] and b["material"] == [{"name": "Fly-ash bricks", "quantity": 12000.0, "unit": "nos"}]
    assert info["assignments_used"] == 2                  # the electrician on a left-out task is not taken


def test_import_route_masonry_scope_and_all():
    from gui.api import create_app
    c = create_app().test_client()
    d = c.post("/api/schedule/import", data=_project(), content_type="application/xml").get_json()
    assert d["project"]["leaf_tasks"] == 4 and d["check"]["scope"]["left_out"] == 5
    a = c.post("/api/schedule/import?scope=all", data=_project(), content_type="application/xml").get_json()
    assert a["project"]["leaf_tasks"] == 7 and a["check"]["scope"]["mode"] == "all"
    assert pytest.approx(d["project"]["finish_days"]) == a["project"]["finish_days"]
