"""Quantity of work -> workers required, shortfall flags and derived facts (app/productivity/labour_plan.py).

Hand calculation, IS 7272 brick masonry, 1,000 m3 over 100 days.  Constants per m3: mason 0.94, mazdoor 1.8, bhisti 0.2:
    person-days  masons 940, helpers 1,800, bhisti 200
    workers required  ceil(9.4) = 10, 18, 2  -> 30 in total
  with 8 masons, 18 helpers, 2 bhisti:
    masons short by 2 (20%); 940 / 8 = 117.5 days, 17.5 more than planned; usable workers 8 + 18 + 2 = 28
  bricks, 500 per m3 (user input): 1,000 m3 / 100 d = 10 m3/day -> 5,000 per day; 20,000 in stock lasts 4 days
"""
import copy

import pytest

from app import service
from app.productivity.india_norms import load_norms
from app.productivity.labour_plan import plan_work, role_group

NORM = load_norms()["IS7272-1brick"]
AVAIL = {"masons": 8, "helpers": 18, "bhisti": 2}
BRICKS = [{"name": "Bricks", "unit": "nos", "per_unit_of_work": 500, "stock": 20000, "lead_time_days": 6}]


def test_requirements_and_shortfall_by_hand():
    p = plan_work(NORM, 1000, "m3", 100, AVAIL, materials=BRICKS)
    g = {x["group"]: x for x in p["groups"]}
    assert g["masons"]["person_days"] == pytest.approx(940) and g["masons"]["required_workers"] == 10
    assert g["helpers"]["person_days"] == pytest.approx(1800) and g["helpers"]["required_workers"] == 18
    assert g["bhisti"]["person_days"] == pytest.approx(200) and g["bhisti"]["required_workers"] == 2
    assert p["required_total"] == 30 and p["available_usable"] == 28
    assert g["masons"]["shortfall"] == 2 and g["helpers"]["shortfall"] == 0
    assert p["implied_duration_days"] == pytest.approx(117.5) and p["slip_days"] == pytest.approx(17.5)
    assert p["binding_group"] == "masons"
    assert any(f["level"] == "elevated" and "short by 2 (20%)" in f["message"] for f in p["flags"])


def test_derived_facts_replace_the_yes_no_question():
    f = plan_work(NORM, 1000, "m3", 100, AVAIL, materials=BRICKS)["derived_facts"]
    assert f == {"required_workers": 30, "available_workers": 28, "skilled_masons_short": True,
                 "material_stock_days": pytest.approx(4.0), "material_lead_time_days": 6.0}


def test_no_shortfall_means_no_flag():
    p = plan_work(NORM, 1000, "m3", 100, {"masons": 10, "helpers": 20, "bhisti": 3})
    assert p["derived_facts"]["skilled_masons_short"] is False
    assert p["derived_facts"]["available_workers"] == 30            # surplus helpers/bhisti are not counted
    assert p["slip_days"] == 0 and not [f for f in p["flags"] if f["level"] == "elevated"]


def test_surplus_in_one_group_does_not_hide_a_shortage_in_another():
    p = plan_work(NORM, 1000, "m3", 100, {"masons": 8, "helpers": 40, "bhisti": 5})      # 53 workers vs 30 needed
    assert p["available_entered_total"] == 53 and p["available_usable"] == 8 + 18 + 2
    assert p["available_usable"] < p["required_total"]


def test_efficiency_scales_the_work_content():
    p = plan_work(NORM, 1000, "m3", 100, AVAIL, efficiency=0.8)         # 940 / 0.8 = 1,175 person-days -> ceil(11.75) = 12
    assert {x["group"]: x for x in p["groups"]}["masons"]["required_workers"] == 12


def test_rounding_up_only_when_needed():
    assert {x["group"]: x for x in plan_work(NORM, 100, "m3", 94)["groups"]}["masons"]["required_workers"] == 1   # exactly 1.0


def test_no_available_entered_compares_nothing():
    p = plan_work(NORM, 1000, "m3", 100)
    assert "available_workers" not in p["derived_facts"] and "skilled_masons_short" not in p["derived_facts"]
    assert p["implied_duration_days"] is None and p["flags"][0]["level"] == "info"


def test_zero_masons_available_cannot_do_the_work():
    p = plan_work(NORM, 1000, "m3", 100, {"masons": 0, "helpers": 18, "bhisti": 2})
    assert p["implied_duration_days"] is None and p["binding_group"] == "masons"
    assert any("cannot be done" in f["message"] for f in p["flags"])


def test_unit_must_match_the_norm():
    with pytest.raises(ValueError):
        plan_work(NORM, 1000, "m2", 100)


@pytest.mark.parametrize("q,d", [(0, 100), (-5, 100), (1000, 0), (float("nan"), 100), (True, 100)])
def test_rejects_bad_numbers(q, d):
    with pytest.raises(ValueError):
        plan_work(NORM, q, "m3", d)


def test_cpwd_norm_with_two_mason_classes_adds_them():
    n = load_norms()["CPWD-FPS-superstructure-1brick"]           # 0.47 + 0.47 = 0.94 mason-days per m3, coolie 1.8
    p = plan_work(n, 1000, "m3", 100)
    g = {x["group"]: x for x in p["groups"]}
    assert g["masons"]["person_days"] == pytest.approx(940) and g["helpers"]["person_days"] == pytest.approx(1800)
    assert role_group("mason_2nd_class") == "masons" and role_group("coolie") == "helpers"


def test_stock_shorter_than_lead_time_is_flagged_and_longer_is_not():
    short = plan_work(NORM, 1000, "m3", 100, materials=BRICKS)["materials"][0]
    assert short["daily_need"] == pytest.approx(5000) and short["stock_days"] == pytest.approx(4) and short["short_vs_lead_time"]
    ok = plan_work(NORM, 1000, "m3", 100, materials=[{**BRICKS[0], "stock": 40000}])["materials"][0]
    assert ok["stock_days"] == pytest.approx(8) and ok["short_vs_lead_time"] is False


# ---------- through the case service: the rules fire on the derived facts ----------
def _case(**work):
    c = copy.deepcopy(service.example_case())
    for k in ("required_workers", "available_workers", "skilled_masons_short", "material_stock_days", "material_lead_time_days"):
        c["facts"].pop(k, None)
    c["activity"]["planned_duration_days"] = {"value": 100, "source": "User Input"}
    c["work"] = {"quantity": 1000, "unit": "m3", "norm_id": "IS7272-1brick", "available": AVAIL, "materials": BRICKS, **work}
    return c


def test_shortage_triggers_the_flags_automatically():
    r = service.run_case(_case())
    f = r["rules"]["flags"]
    assert f["R-LAB"]["level"] == "elevated" and f["R-SKILL"]["level"] == "elevated" and f["R-MAT"]["level"] == "elevated"
    assert r["work_plan"]["required_total"] == 30


def test_enough_workers_does_not_trigger_the_labour_flags():
    r = service.run_case(_case(available={"masons": 10, "helpers": 18, "bhisti": 2}))
    f = r["rules"]["flags"]
    assert "R-LAB" not in f or f["R-LAB"]["level"] != "elevated"
    assert "R-SKILL" not in f or f["R-SKILL"]["level"] != "elevated"


def test_hand_typed_fact_that_disagrees_with_the_work_plan_is_rejected():
    c = _case()
    c["facts"]["required_workers"] = 6
    with pytest.raises(service.CaseError):
        service.run_case(c)


def test_work_plan_needs_a_planned_duration_and_a_known_norm():
    c = _case()
    del c["activity"]["planned_duration_days"]
    with pytest.raises(service.CaseError):
        service.run_case(c)
    with pytest.raises(service.CaseError):
        service.run_case(_case(norm_id="NOPE"))


def test_api_work_plan_and_norm_list():
    from gui.api import create_app
    c = create_app().test_client()
    ok = c.post("/api/work-plan", json={"duration_days": 100, "work": {"quantity": 1000, "unit": "m3", "norm_id": "IS7272-1brick", "available": AVAIL}}).get_json()
    assert ok["ok"] and ok["plan"]["required_total"] == 30 and ok["plan"]["slip_days"] == pytest.approx(17.5)
    assert c.post("/api/work-plan", json={"duration_days": 100, "work": {"quantity": 0, "norm_id": "IS7272-1brick"}}).status_code == 422
    assert c.post("/api/work-plan", json={"duration_days": 100, "work": {"quantity": 5}}).status_code == 422
    norms = c.get("/api/meta").get_json()["work_norms"]
    assert {n["item_id"] for n in norms} >= {"IS7272-1brick", "CPWD-FPS-superstructure-1brick"} and all(n["unit"] in ("m3", "m2") for n in norms)


def test_output_per_worker_day_comes_from_the_norm():
    # IS 7272: mason 0.94, mazdoor 1.8, bhisti 0.2 days per m3  ->  1/0.94, 1/1.8, 1/0.2 m3 per worker-day
    from app.productivity.labour_plan import norm_groups
    g = {x["group"]: x["output_per_worker_day"] for x in norm_groups(NORM)}
    assert g["masons"] == pytest.approx(1 / 0.94) and g["helpers"] == pytest.approx(1 / 1.8) and g["bhisti"] == pytest.approx(5.0)
    slow = {x["group"]: x["output_per_worker_day"] for x in norm_groups(NORM, 0.8)}
    assert slow["masons"] == pytest.approx(0.8 / 0.94)
    p = {x["group"]: x for x in plan_work(NORM, 1000, "m3", 100, AVAIL)["groups"]}
    assert p["masons"]["output_per_worker_day"] == pytest.approx(1 / 0.94)


def test_meta_lists_each_norm_with_its_per_group_output():
    from gui.api import create_app
    n = {x["item_id"]: x for x in create_app().test_client().get("/api/meta").get_json()["work_norms"]}
    g = {x["group"]: x for x in n["CPWD-FPS-superstructure-1brick"]["groups"]}
    assert g["masons"]["constant_per_unit"] == pytest.approx(0.94)            # 0.47 + 0.47 (two mason classes add)
    assert g["masons"]["output_per_worker_day"] == pytest.approx(1 / 0.94)
