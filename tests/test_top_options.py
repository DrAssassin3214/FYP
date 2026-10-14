"""The decision lists at most TOP_N ranked options and never changes which one is selected."""
from app import service
from app.engine.decision import TOP_N


def _run():
    return service.run_analysis(service.example_analysis_case())


def test_top_options_capped_and_selected_first():
    d = _run()["decision"]
    top = d["top_option_ids"]
    assert 1 <= len(top) <= TOP_N == d["top_n"]
    assert top[0] == d["selected_option_id"]
    assert d["options_not_shown"] == len(d["options"]) - len(top)


def test_ranks_follow_the_criterion_and_skip_rejected():
    d = _run()["decision"]
    key = {"min_expected_total_cost": "total_expected_cost", "min_deadline_exceedance": "p_exceed_deadline",
           "min_p90_duration": "P90"}[d["criterion"]]
    adm = sorted((o for o in d["options"] if o["admissible"]), key=lambda o: o["rank"])
    assert [o["rank"] for o in adm] == list(range(1, len(adm) + 1))
    vals = [o[key] for o in adm]
    assert vals == sorted(vals)
    assert all(o["rank"] is None for o in d["options"] if not o["admissible"])


def test_many_options_are_capped():
    case = service.example_analysis_case()
    r = service.run_analysis(case)
    n_all = len(r["decision"]["options"])
    assert n_all > TOP_N, "example case should evaluate more options than the shortlist"
    assert len(r["decision"]["top_option_ids"]) == TOP_N
