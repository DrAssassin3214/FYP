"""Site facts worked out from entered dates, counts and pick-lists (hand-checked)."""
from app.productivity.site_plan import derive_site_facts
from app.productivity.work_plan import build_work_plan


def _d(site=None, ctx=None, **kw):
    return derive_site_facts({"site": site or {}, "context": ctx or {}}, **kw)


def test_nothing_entered_derives_nothing():
    assert _d()["facts"] == {}


def test_monsoon_overlap_boundaries():
    ev = [{"name": "M", "kind": "monsoon", "from": "2026-06-10", "to": "2026-09-30"}]
    assert _d(ctx={"start": "2026-09-30", "finish": "2026-10-05", "events": ev})["facts"]["monsoon_overlap"] is True   # touches last day
    assert _d(ctx={"start": "2026-10-01", "finish": "2026-10-05", "events": ev})["facts"]["monsoon_overlap"] is False
    assert "monsoon_overlap" not in _d(ctx={"start": "2026-10-01", "finish": "2026-10-05", "events": []})["facts"]


def test_gang_and_money_dates():
    f = _d({"gang_pay_due": "2026-10-10", "gang_paid_on": "2026-10-10"})["facts"]
    assert f["gang_payment_overdue"] is False                      # paid on the due date is on time
    f = _d({"gang_pay_due": "2026-10-10"}, {"start": "2026-10-10"})["facts"]
    assert f["gang_payment_overdue"] is False                      # due the day the task starts: not yet overdue
    f = _d({"gang_pay_due": "2026-10-09"}, {"start": "2026-10-10"})["facts"]
    assert f["gang_payment_overdue"] is True
    assert _d({"client_pay_due": "2026-10-01", "client_pay_expected": "2026-10-01"})["facts"]["payment_delay_expected"] is False


def test_migrant_is_more_than_half():
    assert _d({"migrant_workers": 5}, workers_total=10)["facts"]["gang_mostly_migrant"] is False
    assert _d({"migrant_workers": 6}, workers_total=10)["facts"]["gang_mostly_migrant"] is True


def test_height_compression_rework_and_readiness():
    assert _d({"floor_level": 0})["facts"]["work_at_height"] is False
    assert _d({"floor_level": 0}, scaffolding_needed=True)["facts"]["work_at_height"] is True
    assert _d({"normal_duration_days": 10}, duration_days=10)["facts"]["schedule_compressed"] is False
    assert _d({"rework_items": 0})["facts"]["prior_rework_history"] is False
    f = _d({"readiness": [{"kind": "design", "ready_by": "2026-10-11"}, {"kind": "frames", "ready_by": "2026-10-10"}]},
           {"start": "2026-10-10"})["facts"]
    assert f["design_incomplete"] is True and f["frames_on_site"] is True


def test_bad_input_is_rejected():
    for site in ({"floor_level": -1}, {"gang_pay_due": "10/10/2026"}, {"wall_location": "roof"}, {"readiness": [{"kind": "x"}]}):
        try:
            _d(site)
        except ValueError:
            continue
        raise AssertionError(site)


def test_build_work_plan_site_only_and_empty():
    assert build_work_plan({}, None, {}) is None
    p = build_work_plan({"site": {"rework_items": 2}}, None, {})
    assert p["derived_facts"]["prior_rework_history"] is True


def test_labour_cost_uses_ssr_maharashtra_wages():
    # hand check: 10 masons x 677 + 18 helpers x 615 + 2 bhisti x 648 = 6770 + 11070 + 1296 = 19136 per day; x 100 days
    from app.productivity.india_norms import selectable_norms
    from app.productivity.labour_plan import plan_work
    p = plan_work(selectable_norms()["IS7272-1brick"], 1000, "m3", 100, {"masons": 8, "helpers": 18, "bhisti": 2})
    assert {g["group"]: g["labour_cost_per_day"] for g in p["groups"]} == {"masons": 6770, "helpers": 11070, "bhisti": 1296}
    assert p["ssr"]["labour_cost_per_day"] == 19136 and p["ssr"]["labour_cost_for_task"] == 1913600
