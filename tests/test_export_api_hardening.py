"""Regression tests for export / HTTP API / CLI / AI-guard hardening."""
import csv
import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

from app import service
from app.ai_layer import clients
from app.ai_layer.evidence import EvidenceRecord, EvidenceStore
from app.ai_layer.explain import check_numbers
from app.ai_layer.guard import RiskCandidate, parse_and_validate, promote
from app.engine.models import DelayDist, Param, RiskStatus, Source
from app.reporting.matrix_graphic import register_html
from app.reporting.register_report import register_csv
from gui.api import create_app

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def _case(**risk_over):
    c = service.example_case()
    c["risks"][0].update(risk_over)
    return c


# ------------------------------------------------------------------ 1. CSV formula injection + BOM
@pytest.mark.parametrize("lead", ["=", "+", "-", "@", "\t", "\r"])
def test_csv_cells_starting_with_formula_chars_are_neutralised(lead):
    res = service.run_case(_case(name=lead + "SUM(A1)", category=lead + "x"))
    rows = list(csv.reader(io.StringIO(register_csv(res))))
    assert rows[1][1] == "'" + lead + "SUM(A1)" and rows[1][2] == "'" + lead + "x"
    for row in rows[1:]:
        for cell in row:
            assert not cell.startswith(("=", "+", "-", "@", "\t", "\r"))


def test_register_csv_endpoint_has_bom_and_is_parseable(client):
    case = _case(name="=cmd|' /C calc'!A0 é")
    r = client.post("/api/register-csv", json=case)
    assert r.status_code == 200 and r.data.startswith(b"\xef\xbb\xbf")
    rows = list(csv.reader(io.StringIO(r.data.decode("utf-8-sig"))))
    assert rows[1][1].startswith("'=cmd") and "é" in rows[1][1]


# ------------------------------------------------------------------ 2. basis + illustrative flag
def test_csv_has_basis_and_illustrative_columns():
    res = service.run_case(service.example_case())
    rows = list(csv.DictReader(io.StringIO(register_csv(res))))
    assert {r["basis"] for r in rows} == {"entered numbers"}
    assert all("ILLUSTRATIVE" in r["note"] and r["case"] == "ILLUSTRATIVE example" for r in rows)
    assert "ILLUSTRATIVE" in res["report_markdown"] and "| Basis |" in res["report_markdown"]


def test_seeded_rows_leave_p_and_delay_empty_and_say_so():
    c = service.example_case()
    c["risks"][0].pop("p"), c["risks"][0].pop("delay")
    res = service.run_case(c)
    rows = list(csv.DictReader(io.StringIO(register_csv(res))))
    seeded = [r for r in rows if r["basis"].startswith("literature seed")]
    if not seeded:
        pytest.fail("no seeded row produced")
    s = seeded[0]
    assert "not a probability" in s["basis"]
    assert s["p"] == "" and s["delay_min"] == "" and s["delay_most_likely"] == "" and s["expected_delay_days"] == ""


# ------------------------------------------------------------------ 3. markdown escaping
def test_markdown_table_escapes_pipes_and_newlines():
    res = service.run_case(_case(name="A | B\nC"))
    md = res["report_markdown"]
    line = next(ln for ln in md.splitlines() if ln.startswith("| R-MAT"))
    assert "A \\| B<br>C" in line and line.count("|") - line.count("\\|") == 10


# ------------------------------------------------------------------ 4. robust escaping
def test_html_report_survives_odd_types_and_still_escapes():
    res = service.run_case(service.example_case())
    res["project"]["name"] = 12345
    res["risks"][0]["name"] = "<script>alert(1)</script>"
    res["risks"][0]["evidence_ids"] = ["M01", 7]
    res["risks"][0]["category"] = None
    html = register_html(res, {})
    assert "<script>alert(1)" not in html and "&lt;script&gt;" in html and "12345" in html


# ------------------------------------------------------------------ 5. HTTP API
POST_ROUTES = ["/api/validate", "/api/run", "/api/report", "/api/register-csv", "/api/matrix-svg", "/api/report-html",
               "/api/suggest-risks", "/api/settings/test", "/api/settings"]


@pytest.mark.parametrize("route", POST_ROUTES)
@pytest.mark.parametrize("body", ["[]", '"text"', "42", "null", "{not json", "", "[" * 100000, "[" * 60 + "]" * 60])
def test_every_post_route_returns_clean_json_error_for_odd_bodies(client, route, body):
    r = client.post(route, data=body, content_type="application/json")
    assert r.status_code in (400, 422), (route, body[:20], r.status_code)
    assert r.mimetype == "application/json" and r.get_json()["ok"] is False
    assert b"Traceback" not in r.data and b"<html" not in r.data.lower()


def test_validate_never_returns_html_for_odd_case_shapes(client):
    for case in ({"risks": 5}, {"risks": [1, "x"]}, {"project": []}, {"activity": "x"}, {"facts": [1]}):
        r = client.post("/api/validate", json=case)
        assert r.mimetype == "application/json" and r.status_code < 500


def test_settings_test_and_suggest_reject_wrong_types(client):
    r = client.post("/api/settings/test", json={"api_key": 123})
    assert r.status_code == 422 and "api_key must be a string" in r.get_json()["problems"][0]
    assert client.post("/api/suggest-risks", json={"query": ["a"]}).status_code == 422


def test_unhandled_exception_becomes_json_500(client, monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("secret detail")
    monkeypatch.setattr(service, "template_case", boom)
    r = client.get("/api/template")
    assert r.status_code == 500 and r.get_json() == {"ok": False, "error": "internal error"}
    assert b"secret" not in r.data


def test_masked_key_never_reveals_a_short_key(client, monkeypatch):
    monkeypatch.setattr(clients, "resolve_config", lambda *a, **k: ("sk-12345", None, "anthropic", "settings"))
    d = clients.describe_config()
    assert "12345" not in json.dumps(d) and d["configured"] is True
    monkeypatch.setattr(clients, "resolve_config", lambda *a, **k: ("sk-ant-abcdefghijklmnop", None, "anthropic", "settings"))
    assert "abcdefghijkl" not in clients.describe_config()["masked_key"]


@pytest.mark.parametrize("host,code", [("evil.example.com", 403), ("127.0.0.1:8811", 200), ("localhost:5000", 200),
                                       ("localhost", 200), ("127.0.0.1.evil.com", 403), ("[::1]:8811", 200)])
def test_host_header_is_checked(client, host, code):
    assert client.get("/api/health", headers={"Host": host}).status_code == code


# ------------------------------------------------------------------ 6. CLI
def _cli(*args):
    return subprocess.run([sys.executable, "-m", "app.cli", *args], cwd=ROOT, capture_output=True, text=True)


def test_cli_friendly_errors(tmp_path):
    empty = tmp_path / "empty.json"; empty.write_text("")
    lst = tmp_path / "list.json"; lst.write_text("[1]")
    bad = tmp_path / "bad.json"; bad.write_text("{oops")
    u16 = tmp_path / "u16.json"; u16.write_bytes(json.dumps(service.example_case()).encode("utf-16"))
    ok = tmp_path / "ok.json"; ok.write_text(json.dumps(service.example_case()))
    afile = tmp_path / "afile"; afile.write_text("x")
    for args in (["run", str(tmp_path / "missing.json")], ["run", str(empty)], ["run", str(tmp_path)],
                 ["run", str(bad)], ["run", str(lst)], ["run", str(u16)], ["run", str(ok), "--out", str(afile)],
                 ["run", str(ok), "--out", str(afile / "sub")]):
        p = _cli(*args)
        assert p.returncode == 2, args
        assert "Traceback" not in p.stderr and p.stderr.startswith("error:") and len(p.stderr.strip().splitlines()) == 1, (args, p.stderr)


def test_cli_writes_csv_with_bom(tmp_path):
    ok = tmp_path / "ok.json"; ok.write_text(json.dumps(service.example_case()))
    assert _cli("run", str(ok), "--out", str(tmp_path / "o")).returncode == 0
    assert (tmp_path / "o" / "register.csv").read_bytes().startswith(b"\xef\xbb\xbf")


# ------------------------------------------------------------------ 7. AI guard
STORE = EvidenceStore([EvidenceRecord("M01", "Cite A", "", "ctx", 2, "Brick supply delays were reported.")])


def _raw(*items):
    return json.dumps({"risks": list(items)})


def _item(**kw):
    d = {"name": "Brick shortage", "category": "Material", "mechanism": "Late deliveries stop work.", "evidence_ids": ["M01"]}
    d.update(kw)
    return d


@pytest.mark.parametrize("text", [
    "Occurs with 70% probability", "delays of about 5 days", "a two week stoppage", "costs INR999999", "costs Rs 5,000",
    "costs ₹5000", "probability of 0.35", "likelihood 0.4", "adds 3-5 working days", "cost of 2 lakh", "about 3 months"])
def test_g7_figures_in_free_text_reject_the_suggestion(text):
    log = []
    out = parse_and_validate(_raw(_item(mechanism=text), _item(name="Clean one")), {"M01"}, STORE, log)
    assert [c.name for c in out] == ["Clean one"]
    assert log and log[0]["rule"] == "G7"
    out = parse_and_validate(_raw(_item(name=text)), {"M01"}, STORE, log)
    assert out == []


def test_g7_does_not_reject_ordinary_text():
    out = parse_and_validate(_raw(_item(mechanism="Hoist breakdown during Phase 2 of the ISO 9001 audit")), {"M01"}, STORE, [])
    assert len(out) == 1


def test_g9_unknown_numeric_keys_are_dropped_and_logged():
    log = []
    out = parse_and_validate(_raw(_item(likelihood=0.9, days=4, impact=3, score=7, notes="x")), {"M01"}, STORE, log)
    c = out[0]
    assert {"likelihood", "days", "impact", "score"} <= set(c.rejected_numeric_fields) and "notes" not in c.rejected_numeric_fields
    assert any("G9" in i for i in c.issues) and log[0]["rule"] == "G9"
    assert c.status == RiskStatus.AI_UNVERIFIED


@pytest.mark.parametrize("bad", [
    _item(quotes=["a"]), _item(quotes="x"), _item(quotes={"M01": 5}), _item(evidence_ids=7), _item(evidence_ids="M01"),
    _item(name=123), _item(name=None), _item(mechanism=["a"]), _item(category={"a": 1}), "just a string", 42, None, [1]])
def test_g8_one_malformed_item_does_not_discard_the_others(bad):
    log = []
    out = parse_and_validate(_raw(_item(name="Good one"), bad, _item(name="Another good one")), {"M01"}, STORE, log)
    assert [c.name for c in out] == ["Good one", "Another good one"]
    assert log and log[0]["rule"] == "G8"


def test_g8_non_string_evidence_id_inside_list_is_dropped_not_fatal():
    out = parse_and_validate(_raw(_item(evidence_ids=["M01", 5, ["x"]])), {"M01"}, STORE, [])
    assert out[0].evidence_ids == ("M01",) and any("G8" in i for i in out[0].issues)


@pytest.mark.parametrize("wrapped", [
    "```json\n{raw}\n```", "```\n{raw}\n```", "Sure! Here you go:\n{raw}\nHope that helps.", "```json\n{raw}\n``` trailing prose"])
def test_clients_extract_json_handles_fences_and_prose(wrapped):
    raw = _raw(_item())
    out = parse_and_validate(wrapped.replace("{raw}", raw), {"M01"}, STORE, [])
    assert len(out) == 1 and out[0].name == "Brick shortage"


def test_extract_json_accepts_bare_array_and_rejects_prose():
    assert clients.extract_json('Result: [{"a": 1}] done') == [{"a": 1}]
    with pytest.raises(ValueError):
        clients.extract_json("no json here")
    out = parse_and_validate(json.dumps([_item()]), {"M01"}, STORE, [])
    assert len(out) == 1


def test_promote_still_refuses_derived_numbers_and_status_stays_unverified():
    c = RiskCandidate("x", "", "", ("M01",))
    with pytest.raises(ValueError):
        promote(c, "R-1", Param(0.3, Source.DERIVED), DelayDist("fixed", 2, 2, 2, source=Source.ASSUMPTION))


def test_l11_explain_check_numbers_no_longer_skips_currency_amounts():
    trace = {"cost": {"expected": 1000}}
    assert check_numbers("Cost is INR999999.", trace) and check_numbers("Rs5000 extra", trace)
    assert not check_numbers("Cost is INR 1000.", trace)
