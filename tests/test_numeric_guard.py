"""Numeric guard: absurdly large inputs are refused with a clear message; sane inputs are unchanged."""
import copy
import json
import hashlib

import pytest

from app import service
from app.analysis import CaseError, PLAUSIBLE_MAX, run_analysis


def _client():
    from gui.api import create_app
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def _huge_delay():
    case = service.example_analysis_case()
    d = case["risks"][0]["delay"]
    d["a"] = d["m"] = d["b"] = 1e308
    return case


def test_numeric_guard_huge_delay_service():
    with pytest.raises(CaseError) as ei:
        run_analysis(_huge_delay())
    msg = " ".join(ei.value.args[0] if isinstance(ei.value.args[0], list) else map(str, ei.value.args))
    assert "plausibility limit" in msg and "delay" in msg


def test_numeric_guard_huge_delay_http_422():
    r = _client().post("/api/analyze", json=_huge_delay())
    assert r.status_code == 422
    assert "plausibility limit" in json.dumps(r.get_json())


@pytest.mark.parametrize("path", [("risks", 0, "direct_cost_if_occurs"), ("cost", "cost_per_delay_day"),
                                  ("cost", "ld_per_day_after_deadline")])
def test_numeric_guard_other_caps(path):
    case = service.example_analysis_case()
    node = case
    for k in path[:-1]:
        node = node[k]
    node[path[-1]] = {"value": PLAUSIBLE_MAX * 10, "source": "Assumption"}
    with pytest.raises(CaseError) as ei:
        run_analysis(case)
    assert "plausibility limit" in str(ei.value.args)


def test_numeric_guard_sane_example_still_runs_and_is_deterministic():
    def h():
        r = run_analysis(service.example_analysis_case())
        r["audit"].pop("timestamp_utc", None)
        return hashlib.sha256(json.dumps(r, sort_keys=True, default=str).encode()).hexdigest()
    assert h() == h()
    r = run_analysis(service.example_analysis_case())
    assert r["ok"]


def test_numeric_guard_unknown_evidence_warning_parity():
    case = service.example_analysis_case()
    case["risks"][0].setdefault("p", {})["evidence_ids"] = ["NOPE-1"]
    expected = "unknown evidence id 'NOPE-1': not found in the evidence store"
    assert expected in service.run_case(copy.deepcopy(case), {"KNOWN": "x"})["warnings"]
    out = run_analysis(copy.deepcopy(case), {"KNOWN": "x"})
    assert expected in out["warnings"]
    assert out["ok"]                                   # warning only, never an error
    assert expected not in run_analysis(copy.deepcopy(case))["warnings"]   # no index given: no check
