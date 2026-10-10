"""Online literature search for candidate responses: HTTP is always mocked (the sandbox has no internet and the
tests must never call a real network)."""
import io
import json
import re
import urllib.error

import pytest

from app import online_search as osr

OPENALEX = {"results": [
    {"id": "https://openalex.org/W1", "doi": "https://doi.org/10.1000/ABC.1", "title": "Buffer stock and masonry delay",
     "publication_year": 2019,
     "authorships": [{"author": {"display_name": "A. Rao"}}, {"author": {"display_name": "B. Singh"}}],
     "primary_location": {"source": {"display_name": "Journal of Construction"}, "landing_page_url": "https://x.example/1"},
     "abstract_inverted_index": {"Buffers": [0], "reduce": [1], "delay": [2, 5], "of": [3], "material": [4], "by": [6], "30": [7]}},
    {"id": "https://openalex.org/W2", "doi": None, "title": "No DOI paper", "publication_year": 2020, "authorships": [],
     "primary_location": None, "abstract_inverted_index": None},
]}
CROSSREF = {"status": "ok", "message": {"items": [
    {"DOI": "10.1000/abc.1", "title": ["Buffer stock and masonry delay"], "author": [{"given": "A.", "family": "Rao"}],
     "issued": {"date-parts": [[2019, 5]]}, "container-title": ["J Constr"], "URL": "http://dx.doi.org/10.1000/abc.1",
     "abstract": "<jats:p>Abstract Costs rose 12% in the study.</jats:p>"},
    {"DOI": "10.2000/xyz", "title": ["Crew size and productivity"], "author": [{"name": "Org"}],
     "issued": {"date-parts": [[2021]]}, "container-title": ["Build Mgmt"]},
]}}


class FakeResp(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *a): return False


def fake_urlopen_factory(calls):
    def fake(req, timeout=None):
        url = req.full_url if hasattr(req, "full_url") else req
        calls.append((url, timeout, dict(req.header_items()) if hasattr(req, "header_items") else {}))
        body = OPENALEX if "openalex" in url else CROSSREF
        return FakeResp(json.dumps(body).encode())
    return fake


def offline(req, timeout=None):
    raise urllib.error.URLError("no route")


def test_parse_openalex_rebuilds_abstract():
    r = osr.parse_openalex(OPENALEX)
    assert r[0]["abstract_snippet"] == "Buffers reduce delay of material delay by 30"
    assert r[0]["doi"] == "10.1000/abc.1" and r[0]["url"] == "https://doi.org/10.1000/abc.1"
    assert r[0]["venue"] == "Journal of Construction" and r[0]["year"] == 2019 and r[0]["authors"] == ["A. Rao", "B. Singh"]
    assert r[0]["source_api"] == "OpenAlex" and r[1]["abstract_snippet"] == "" and r[1]["doi"] == ""


def test_parse_crossref():
    r = osr.parse_crossref(CROSSREF)
    assert r[0]["title"] == "Buffer stock and masonry delay" and r[0]["year"] == 2019 and r[0]["venue"] == "J Constr"
    assert "<" not in r[0]["abstract_snippet"] and r[0]["source_api"] == "Crossref"
    assert r[1]["authors"] == ["Org"] and r[1]["url"] == "https://doi.org/10.2000/xyz"


def test_search_dedupes_by_doi_and_caps(monkeypatch):
    calls = []
    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen_factory(calls))
    res = osr.search_literature("buffer masonry", limit=50)
    assert res["ok"] and len(res["results"]) == 3          # abc.1 merged; No DOI; xyz
    merged = [x for x in res["results"] if x["doi"] == "10.1000/abc.1"]
    assert len(merged) == 1 and merged[0]["source_api"] == "OpenAlex + Crossref"
    assert len(calls) == 2 and all(c[1] == 10 for c in calls)
    assert "per-page=10" in calls[0][0] and "rows=10" in calls[1][0]
    assert all("FYP-BrickworkRiskTool" in c[2].get("User-agent", "") for c in calls)


def test_offline_error_path(monkeypatch):
    monkeypatch.setattr("urllib.request.urlopen", offline)
    res = osr.search_literature("x")
    assert res["ok"] is False and res["offline"] is True and res["message"]
    out = osr.find_options_online([{"id": "R-MAT", "name": "Material"}], [])
    assert out["ok"] is False and out["offline"] is True and "papers, not recommendations" in out["note"]


def test_bad_json_is_treated_as_unreachable(monkeypatch):
    monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout=None: FakeResp(b"<html>"))
    assert osr.search_literature("x")["offline"] is True


def test_no_number_extraction(monkeypatch):
    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen_factory([]))
    out = osr.find_options_online([{"id": "R-MAT", "name": "Material"}], [])
    allowed = {"title", "authors", "year", "venue", "doi", "url", "abstract_snippet", "source_api"}
    for r in out["risks"]:
        for s in r["sources"]:
            assert set(s) == allowed
    blob = json.dumps(out).lower()
    for k in ("cost_value", "effect", "p_after", "delay_after", "probability", "extracted"):
        assert f'"{k}' not in blob
    # numbers inside abstract text stay text; nothing is parsed out of it
    assert not any(isinstance(v, (int, float)) for s in out["risks"][0]["sources"] for k, v in s.items() if k != "year")


def test_no_network_at_import():
    import subprocess, sys
    code = ("import urllib.request as u\n"
            "def boom(*a, **k): raise SystemExit('network call at import')\n"
            "u.urlopen = boom\n"
            "import app.online_search, gui.api\n"
            "gui.api.create_app()\n")
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


@pytest.fixture(scope="module")
def client():
    from gui.api import create_app
    app = create_app(); app.config["TESTING"] = True
    return app.test_client()


def test_endpoint_with_risk_ids_and_case(client, monkeypatch):
    calls = []
    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen_factory(calls))
    d = client.post("/api/online-options", json={"risk_ids": ["R-MAT"]}).get_json()
    assert d["ok"] and d["risks"][0]["risk_id"] == "R-MAT" and d["risks"][0]["catalogue_options"]
    assert "mitigation" in d["risks"][0]["query"] and "brick masonry" in d["risks"][0]["query"]
    d2 = client.post("/api/online-options", json={"case": {"risks": [{"id": "R-MAT"}, {"id": "R-MAT"}]}}).get_json()
    assert len(d2["risks"]) == 1


def test_endpoint_offline_is_clean_json(client, monkeypatch):
    monkeypatch.setattr("urllib.request.urlopen", offline)
    r = client.post("/api/online-options", json={"risk_ids": ["R-MAT"]})
    d = r.get_json()
    assert r.status_code == 200 and d["ok"] is False and d["offline"] is True and d["message"]


@pytest.mark.parametrize("body,raw", [({}, None), ({"risk_ids": "R-MAT"}, None), ({"risk_ids": [1]}, None),
                                       ({"risk_ids": ["NOPE"]}, None), ({"case": {"risks": []}}, None),
                                       ({"case": {"risks": 5}}, None), (None, b"{bad"), (None, b"[1]")])
def test_endpoint_clean_errors(client, monkeypatch, body, raw):
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: pytest.fail("network called"))
    r = client.post("/api/online-options", json=body) if raw is None else client.post("/api/online-options", data=raw, content_type="application/json")
    assert r.status_code == 422 and r.get_json()["ok"] is False and r.get_json()["problems"]


def test_endpoint_host_check(client):
    r = client.post("/api/online-options", json={"risk_ids": ["R-MAT"]}, headers={"Host": "evil.example"})
    assert r.status_code == 403


def test_other_endpoints_do_not_touch_network(client, monkeypatch):
    from app import service
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: pytest.fail("network called"))
    case = service.example_analysis_case()
    assert client.post("/api/analyze", json=case).status_code == 200
    assert client.post("/api/run", json=case).status_code == 200
    assert client.get("/api/mitigation-catalogue").status_code == 200


def test_option_suggestions_do_not_use_llm(monkeypatch):
    from app import analysis, service
    import app.ai_layer.clients as clients
    monkeypatch.setattr(clients, "get_client", lambda *a, **k: pytest.fail("LLM client reached"))
    r = analysis.run_analysis(service.example_analysis_case(), {})
    assert r["option_suggestions"]["targets"]
    src = open(analysis.__file__, encoding="utf-8").read()
    assert not re.search(r"get_client|generate_candidates|explain_with_llm", src)
