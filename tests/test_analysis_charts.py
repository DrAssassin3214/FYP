"""Chart data and chart code for the 'Cost, options & decision' screen and the HTML chart export."""
import re
from pathlib import Path

import pytest

from app import service
from app.reporting.analysis_charts import (PREFERRED_WORDING, analysis_html, chart_pngs, chart_tables, options_shown)

ROOT = Path(__file__).resolve().parents[1]
JS = [ROOT / "gui/static/js/analysis_charts.js", ROOT / "gui/static/js/screens/analysis.js"]


@pytest.fixture(scope="module")
def res():
    return service.run_analysis(service.example_analysis_case())


@pytest.fixture(scope="module")
def client():
    from gui.api import create_app

    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_histogram_shape_and_consistency(res):
    h = res["histogram"]
    assert h["bins"] == 40 and len(h["counts"]) == 40 and len(h["edges"]) == 41 and len(h["share"]) == 40
    assert sum(h["counts"]) == h["n"] == res["n_used"]
    assert abs(sum(h["share"]) - 1) < 1e-9
    assert h["edges"] == sorted(h["edges"])
    assert h["edges"][0] == res["summary"]["min"] and h["edges"][-1] == res["summary"]["max"]
    assert "Derived Calculation" in h["basis"]


def test_histogram_is_deterministic_for_a_fixed_seed(res):
    again = service.run_analysis(service.example_analysis_case())
    assert again["histogram"] == res["histogram"]
    c = service.example_analysis_case()
    c["simulation"]["seed"] = 7
    assert service.run_analysis(c)["histogram"] != res["histogram"]


def test_other_chart_inputs_are_present_with_expected_fields(res):
    assert {"risk_id", "mean_contribution_days", "share_of_expected_delay"} <= set(res["sensitivity"][0])
    assert {"risk_id", "emv", "p"} <= set(res["event_emv"][0])
    assert {"risk_id", "value_at_stake", "name"} <= set(res["value_at_stake"][0])
    assert {"option_id", "mitigations", "mitigation_cost", "residual_expected_cost", "total_expected_cost"} <= set(res["decision"]["options"][0])
    assert {"multiplier", "cost_per_delay_day", "selected_option_id", "command"} <= set(res["decision_sensitivity"]["rows"][0])


def test_charts_only_use_entered_risks(res):
    entered = {r["id"] for r in service.example_analysis_case()["risks"]}
    ids = {r["risk_id"] for r in res["event_emv"]} | {r["risk_id"] for r in res["value_at_stake"]} | {r["risk_id"] for r in res["sensitivity"]}
    assert ids <= entered | {"LATENT_PRODUCTIVITY"}


def test_options_shown_is_bounded_and_keeps_accept_and_preferred(res):
    shown = options_shown(res)
    ids = [o["option_id"] for o in shown]
    assert len(shown) <= 10 and "ACCEPT" in ids and res["decision"]["selected_option_id"] in ids
    assert all(o["admissible"] for o in shown if o["option_id"] != "ACCEPT")


def test_png_charts_and_html_export(res):
    pngs = chart_pngs(res)
    assert set(pngs) == {"histogram", "tornado_delay", "tornado_cost", "event_emv", "options", "decision_sensitivity"}
    assert all(b[:8] == b"\x89PNG\r\n\x1a\n" for b in pngs.values())
    page = analysis_html(res)
    assert page.count("data:image/png;base64,") == 6 and "http://" not in page.replace("http://www.w3.org", "") and "https://" not in page
    assert "ILLUSTRATIVE" in page and "Derived Calculation" in page and PREFERRED_WORDING in page
    assert "optimal" not in page.split("<h2>Report text</h2>")[0].lower()   # the report text itself says "never optimal"
    assert set(chart_tables(res)) == set(pngs)


def test_endpoint_returns_html_and_reports_problems(client):
    ok = client.post("/api/analysis-charts-html", json=service.example_analysis_case())
    assert ok.status_code == 200 and ok.mimetype == "text/html" and b"data:image/png;base64," in ok.data
    bad = service.example_analysis_case()
    del bad["cost"]
    assert client.post("/api/analysis-charts-html", json=bad).status_code == 422
    api = client.post("/api/analyze", json=service.example_analysis_case()).get_json()
    assert len(api["histogram"]["counts"]) == 40


def test_no_options_case_has_no_sensitivity_chart():
    c = service.example_analysis_case()
    c["mitigations"] = []
    r = service.run_analysis(c)
    assert r["decision_sensitivity"] is None
    assert "decision_sensitivity" not in chart_pngs(r) and "histogram" in chart_pngs(r)


def test_js_references_chart_functions_and_no_external_urls():
    code = JS[0].read_text(encoding="utf-8")
    for fn in ("histogramChart", "tornadoDelayChart", "tornadoCostChart", "eventEmvChart", "optionsChart", "decisionSensitivityChart", "chartsSection"):
        assert f"function {fn}" in code, fn
    assert "chartsSection" in JS[1].read_text(encoding="utf-8")
    for f in JS:
        t = f.read_text(encoding="utf-8")
        assert not re.search(r"https?://|//cdn|plotly|Plotly", t), f.name
    assert "isIllustrative" in code and "aria-label" in code and "Derived Calculation" in code
    assert PREFERRED_WORDING in code and "optimal" not in code.lower()
