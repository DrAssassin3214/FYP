"""Tests for the GUI's HTTP layer (gui/api.py) using Flask's built-in test client.

The API must only wrap app.service: every figure it returns has to equal the service's own output.
"""
import json

import pytest

from app import service
from app.ai_layer.guard import StubLLM


@pytest.fixture(scope="module")
def client():
    from gui.api import create_app

    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture(autouse=True)
def offline(tmp_path, monkeypatch):
    """Isolate from the real machine's saved settings (settings_store writes outside the project
    folder, so without this a developer's own configured API key would leak into these tests)."""
    monkeypatch.setenv("APPDATA", str(tmp_path))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)


def test_health_reports_offline_ai_mode(client):
    d = client.get("/api/health").get_json()
    assert d["ok"] is True and d["ai"]["mode"] == "offline"
    assert d["ai"]["label"] == "AI: offline mode (evidence retrieval only)"
    assert set(d["sources"]) == set(service.SOURCES) and d["evidence_records"] > 0


def test_template_and_example_are_the_service_cases(client):
    assert client.get("/api/template").get_json() == service.template_case()
    ex = client.get("/api/example").get_json()
    assert ex == service.example_case() and "ILLUSTRATIVE" in ex["project"]["name"]


def test_reference_data_routes(client):
    lib = client.get("/api/risk-library").get_json()
    assert [r["id"] for r in lib] == [r["id"] for r in service.risk_library()]
    assert client.get("/api/rules").get_json() == service.rule_library()
    meta = client.get("/api/meta").get_json()
    assert {f["name"] for f in meta["facts"]} >= {"required_workers", "available_workers", "monsoon_overlap"}
    assert meta["matrix"]["levels"]["5"]["5"] in {"Low", "Moderate", "High", "Extreme"}
    assert "criteria" not in meta and "strategies" not in meta


def test_removed_simulation_routes_are_gone(client):
    for path in ("/api/models", "/api/explain", "/api/audit"):
        assert client.post(path, json={}).status_code in (404, 405)


def test_evidence_lookup_by_ids_and_search(client):
    d = client.get("/api/evidence?ids=M01,NOT-AN-ID").get_json()
    assert [r["id"] for r in d["records"]] == ["M01"] and d["missing"] == ["NOT-AN-ID"]
    assert d["records"][0]["citation"] == service.evidence_index_from_workbook()["M01"]
    curated = client.get("/api/evidence").get_json()
    assert curated["records"] and curated["count"] >= len(curated["records"])
    assert not any(r["id"].startswith("OA-") for r in curated["records"])     # the bulk harvest is searched, not bulk-loaded
    hits = client.get("/api/evidence?q=labour productivity India").get_json()["records"]
    assert hits and all("id" in h for h in hits)


def test_validate_returns_the_live_register_and_matrix(client):
    d = client.post("/api/validate", json=service.example_case()).get_json()
    ref = service.run_case(service.example_case(), service.evidence_index_from_workbook())
    assert d["ok"] is True and d["result"]["matrix"] == ref["matrix"] and d["result"]["summary"] == ref["summary"]
    assert d["result"]["report_markdown"] == ref["report_markdown"]      # the Export preview


def test_validate_reports_problems_with_http_200(client):
    c = service.example_case()
    c["risks"][0]["p"]["value"] = 1.5
    r = client.post("/api/validate", json=c)
    d = r.get_json()
    assert r.status_code == 200 and d["ok"] is False and any("probability must be in [0,1]" in p for p in d["problems"])
    c = service.example_case()
    c["impact_bin_edges_fraction"] = [0.02, None, 0.1, 0.2]
    d = client.post("/api/validate", json=c).get_json()
    assert d["ok"] is False and any("impact_bin_edges_fraction" in p for p in d["problems"])


def test_blank_template_validates_with_a_note_not_an_error(client):
    d = client.post("/api/validate", json=service.template_case()).get_json()
    assert d["ok"] is True and d["result"]["summary"]["n_risks"] == 0


def test_run_ok_matches_service_and_accepts_a_wrapped_case(client):
    case = service.example_case()
    d = client.post("/api/run", json={"case": case}).get_json()
    ref = service.run_case(case, service.evidence_index_from_workbook())
    assert d["ok"] is True and d["matrix"] == ref["matrix"] and d["report_markdown"] == ref["report_markdown"]


def test_run_returns_422_with_service_problems(client):
    bad = service.example_case()
    bad["risks"][1]["p"]["value"] = 1.5
    r = client.post("/api/run", json=bad)
    assert r.status_code == 422 and "probability must be in [0,1]" in " | ".join(r.get_json()["problems"])
    assert client.post("/api/run", data="not json", content_type="application/json").status_code == 422


def test_suggest_risks_offline(client):
    r = client.post("/api/suggest-risks", json={"activity_name": "Brick masonry", "query": "labour shortage payment"})
    assert r.status_code == 200
    d = r.get_json()
    assert d["mode"] == "offline-retrieval" and d["ai"]["mode"] == "offline"
    assert {"R-LAB", "R-PAY"} <= {x["id"] for x in d["library_risks"]}
    for x in d["library_risks"]:              # retrieval never supplies numbers
        assert not ({"p", "probability", "delay", "cost"} & set(x))
    assert client.post("/api/suggest-risks", json={"query": "  "}).status_code == 422


def test_suggest_risks_guarded_llm_path(client, monkeypatch):
    stub = StubLLM(json.dumps({"risks": [{"name": "Scaffold delay", "category": "Equipment", "mechanism": "x",
                                          "evidence_ids": ["M01", "M999"], "p": 0.4}]}))
    monkeypatch.setattr("gui.api.get_client", lambda: stub)
    d = client.post("/api/suggest-risks", json={"query": "tools equipment scaffolding labour"}).get_json()
    assert d["mode"] == "llm"
    cand = d["candidates"][0]
    assert cand["status"] == "AI-suggested-unverified" and "p" in cand["rejected_numeric_fields"]
    assert any("M999" in i for i in cand["issues"])


def test_register_downloads(client):
    case = service.example_case()
    r = client.post("/api/report", json=case)
    assert r.status_code == 200 and r.mimetype == "text/markdown"
    assert 'filename="register.md"' in r.headers["Content-Disposition"]
    assert r.data.decode("utf-8").startswith("# Risk register and matrix")
    c = client.post("/api/register-csv", json=case)
    assert c.status_code == 200 and c.mimetype == "text/csv" and 'filename="register.csv"' in c.headers["Content-Disposition"]
    assert len(c.data.decode("utf-8").strip().splitlines()) == 8
    bad = service.example_case()
    bad["risks"][0]["p"]["value"] = 9
    assert client.post("/api/report", json=bad).status_code == 422


def test_index_and_static_assets_are_local(client):
    r = client.get("/")
    assert r.status_code == 200
    html = r.data.decode("utf-8")
    assert "http://" not in html.replace("http://www.w3.org", "") and "https://" not in html
    assert "plotly" not in html.lower()
    assert client.get("/static/js/app.js").mimetype == "text/javascript"
    assert client.get("/api/nope").status_code == 404
