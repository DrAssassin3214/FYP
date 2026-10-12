"""The ten ILLUSTRATIVE scenario files in examples/scenarios/ must load, run and stay labelled ILLUSTRATIVE."""
import json
from pathlib import Path

import pytest

from app import service

FILES = sorted((Path(__file__).resolve().parents[1] / "examples" / "scenarios").glob("S*.json"))


def test_there_are_ten_scenarios():
    assert len(FILES) == 10


@pytest.mark.parametrize("path", FILES, ids=[p.stem for p in FILES])
def test_scenario_runs_and_is_illustrative(path):
    case = json.loads(path.read_text(encoding="utf-8"))
    assert "ILLUSTRATIVE" in json.dumps(case["project"])
    assert service.run_case(case)["summary"]["n_on_matrix"] >= 1
    res = service.run_analysis(case)
    assert res["command"]["command"] in ("AUTHORIZE MITIGATION", "ACCEPT RISK")
