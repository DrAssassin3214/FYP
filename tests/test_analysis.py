"""Tests for the quantitative analysis flow (app/analysis.py), its service wrappers, report and HTTP routes."""
import copy

import pytest

from app import service
from app.analysis import MAX_N, parse_analysis


@pytest.fixture(scope="module")
def example_result():
    return service.run_analysis(service.example_analysis_case())


@pytest.fixture(scope="module")
def client():
    from gui.api import create_app

    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture(autouse=True)
def offline(tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)


def base_case(**over):
    c = service.example_analysis_case()
    c.update(over)
    return c


def problems_of(case):
    with pytest.raises(service.CaseError) as e:
        parse_analysis(case)
    return " | ".join(e.value.problems)


# ---------- the illustrative example, end to end ----------
def test_example_result_has_every_section(example_result):
    r = example_result
    for k in ("summary", "cost", "event_emv", "sensitivity", "convergence", "value_at_stake", "option_suggestions",
              "mitigation_checks", "decision", "command", "decision_stability", "decision_sensitivity", "assumptions",
              "audit", "explanation", "report_markdown"):
        assert r[k], k
    assert r["options_source"] == "generated" and len(r["decision"]["options"]) == 23     # ACCEPT + 22


def test_example_command_and_infeasible_option(example_result):
    c = example_result["command"]
    assert c["command"] == "AUTHORIZE MITIGATION" and c["selected_option_id"] != "ACCEPT"
    rows = {o["option_id"]: o for o in example_result["decision"]["options"]}
    mech = rows["O-M-MECH"]
    assert not mech["admissible"] and any("infeasible" in x for x in mech["rejected_because"])
    assert rows[c["selected_option_id"]]["total_expected_cost"] == min(o["total_expected_cost"] for o in rows.values() if o["admissible"])
    assert example_result["decision_stability"]["stable"]


def test_wording_never_claims_optimality(example_result):
    text = example_result["report_markdown"].lower() + " " + example_result["command"]["reason"].lower()
    assert "is optimal" not in text and "optimal option" not in text and "best option" not in text
    assert "not a claim of optimality" in text and "illustrative" in text


def test_result_is_reproducible_and_input_is_not_modified():
    case = service.example_analysis_case()
    before = copy.deepcopy(case)
    a, b = service.run_analysis(case), service.run_analysis(case)
    assert case == before
    assert a["audit"]["input_hash_sha256"] == b["audit"]["input_hash_sha256"]
    assert a["decision"] == b["decision"] and a["command"] == b["command"]
    case["cost"]["cost_per_delay_day"]["value"] = 9000
    assert service.run_analysis(case)["audit"]["input_hash_sha256"] != a["audit"]["input_hash_sha256"]


def test_every_non_literature_input_is_listed(example_result):
    listed = {a["input"] for a in example_result["assumptions"]}
    assert "[cost].cost_per_delay_day" in listed and "[cost].ld_per_day_after_deadline" in listed
    assert any(i.startswith("[mitigations]") and i.endswith(".p_after") for i in listed)
    assert any(i.startswith("[mitigations]") and i.endswith(".cost") for i in listed)


# ---------- no mitigation, no effect, user options ----------
def test_without_mitigations_no_recommendation_is_made():
    case = base_case(mitigations=[])
    r = service.run_analysis(case)
    assert r["command"]["command"] == "NO RESPONSE EVALUATED" and "not a recommendation to accept" in r["command"]["reason"]
    assert r["options_source"] == "none" and r["decision_stability"] is None
    assert r["option_suggestions"]["targets"]                      # still says where the money is and what to enter


def test_mitigation_without_effect_is_reported_and_left_out():
    case = base_case()
    case["mitigations"] = [{"id": "M-X", "risk_id": "R-MAT", "action": "ask the supplier nicely", "cost": {"value": 100, "source": "User Input"}}]
    r = service.run_analysis(case)
    assert any("M-X: no modelled effect" in w for w in r["warnings"])
    assert r["command"]["command"] == "NO RESPONSE EVALUATED"


def test_user_defined_options_are_used_as_given():
    case = base_case(options=[{"id": "OPT-A", "label": "Buffer only", "mitigation_ids": ["M-BUF"]}])
    r = service.run_analysis(case)
    assert r["options_source"] == "user"
    assert [o["option_id"] for o in r["decision"]["options"]] == ["ACCEPT", "OPT-A"]


def test_deadline_criterion_and_constraints():
    case = base_case()
    case["simulation"]["criterion"] = "min_deadline_exceedance"
    case["constraints"] = {"max_p_exceed_deadline": 0.05, "max_mitigation_budget": 20000}
    r = service.run_analysis(case)
    assert r["criterion"] == "min_deadline_exceedance"
    assert r["command"]["command"] == "NO ADMISSIBLE OPTION"        # no response gets P(T > 20) under 5% in the example
    assert all(not o["admissible"] for o in r["decision"]["options"])


# ---------- input validation: problems are listed, never corrected ----------
def test_missing_cost_is_a_problem():
    c = base_case()
    del c["cost"]
    assert "cost.cost_per_delay_day: input required" in problems_of(c)


@pytest.mark.parametrize("mutate,expected", [
    (lambda c: c["mitigations"][0].pop("cost"), "cost: input required"),
    (lambda c: c["mitigations"][0].update(p_after={"value": 1.5, "source": "Expert Judgment"}), "p_after: probability must be between 0 and 1"),
    (lambda c: c["mitigations"][0].update(p_after={"value": 0.2}), "source is required"),
    (lambda c: c["mitigations"][0].update(risk_id="R-NOPE"), "target risk 'R-NOPE'"),
    (lambda c: c["mitigations"][0].update(strategy="pray"), "unknown strategy"),
    (lambda c: c["mitigations"].append(dict(c["mitigations"][0])), "duplicate id"),
    (lambda c: c["mitigations"][2]["secondary_risks"][0].pop("delay"), "secondary risk would be silently left out"),
    (lambda c: c.update(options=[{"id": "X", "mitigation_ids": ["M-NOPE"]}]), "unknown or invalid mitigation"),
    (lambda c: c.update(options=[{"id": "X", "mitigation_ids": ["M-BUF", "M-SUP"]}]), "at most one per risk"),
    (lambda c: c["activity"].pop("deadline_days"), "liquidated damages need activity.deadline_days"),
    (lambda c: c["simulation"].update(n=MAX_N + 1), "simulation.n: must be a whole number"),
    (lambda c: c["simulation"].update(criterion="best"), "unknown 'best'"),
    (lambda c: c.update(constraints={"max_p_exceed_deadline": 1.5}), "constraints.max_p_exceed_deadline"),
    (lambda c: c["cost"].update(cost_per_delay_day={"value": -5, "source": "User Input"}), "must be 0 or more"),
])
def test_invalid_inputs_are_reported(mutate, expected):
    c = base_case()
    mutate(c)
    assert expected in problems_of(c)


def test_deadline_criterion_needs_a_deadline():
    c = base_case()
    del c["activity"]["deadline_days"]
    c["cost"].pop("ld_per_day_after_deadline")
    c["simulation"]["criterion"] = "min_deadline_exceedance"
    assert "needs activity.deadline_days" in problems_of(c)


def test_incomplete_register_risks_are_left_out_with_a_note():
    c = base_case()
    c["risks"].append({"id": "R-DES", "name": "Design changes"})            # no probability or delay yet
    r = service.run_analysis(c)
    assert any("R-DES" in w and "left out of the simulation" in w for w in r["warnings"])
    assert "R-DES" not in {x["risk_id"] for x in r["event_emv"]}


# ---------- HTTP routes ----------
def test_analyze_route_wraps_the_service(client):
    case = service.example_analysis_case()
    d = client.post("/api/analyze", json=case).get_json()
    ref = service.run_analysis(case)
    assert d["command"] == ref["command"] and d["decision"] == ref["decision"] and d["cost"] == ref["cost"]


def test_analyze_route_reports_problems_with_422(client):
    c = service.example_analysis_case()
    del c["cost"]
    resp = client.post("/api/analyze", json=c)
    assert resp.status_code == 422 and resp.get_json()["ok"] is False
    assert any("cost_per_delay_day" in p for p in resp.get_json()["problems"])


def test_report_catalogue_and_example_routes(client):
    rep = client.post("/api/analysis-report", json=service.example_analysis_case())
    assert rep.status_code == 200 and rep.data.decode().startswith("# Delay cost and response analysis")
    assert "analysis.md" in rep.headers["Content-Disposition"]
    cat = client.get("/api/mitigation-catalogue").get_json()["entries"]
    assert cat == service.mitigation_catalogue() and len(cat) >= 10
    assert client.get("/api/example-analysis").get_json() == service.example_analysis_case()
    for path in ("/api/models", "/api/explain", "/api/audit"):          # the routes removed earlier stay removed
        assert client.post(path, json={}).status_code in (404, 405)
