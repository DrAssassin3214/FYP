"""Regression tests for the defects found in the 2026-10-09 validation report (F1-F6)."""
import copy
import json
from pathlib import Path

import pytest

from app import cli, service
from app.engine.models import Activity, Param, Source
from app.engine.simulation import convergence, simulate

ROOT = Path(__file__).resolve().parents[1]


def _case():
    return service.example_analysis_case()


# F1 ------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("content", [None, b"", b"{not json", b"\xff\xfe{\x00}\x00", b"\xff\xfe\xfd"])
def test_analyze_reports_a_bad_case_file_in_one_line_not_a_traceback(tmp_path, capsys, content):
    f = tmp_path / "case.json"
    if content is not None:
        f.write_bytes(content)
    assert cli.main(["analyze", str(f)]) == 2
    err = capsys.readouterr().err
    assert err.startswith("error:") and "Traceback" not in err


def test_analyze_on_a_folder_and_on_a_file_as_out(tmp_path, capsys):
    assert cli.main(["analyze", str(tmp_path)]) == 2
    good = tmp_path / "ok.json"
    c = _case()
    c["simulation"] = {"n": 500, "seed": 1}
    good.write_text(json.dumps(c), encoding="utf-8")
    blocker = tmp_path / "afile"
    blocker.write_text("x")
    assert cli.main(["analyze", str(good), "--out", str(blocker)]) == 2
    assert "Traceback" not in capsys.readouterr().err


def test_analyze_still_writes_outputs_for_a_good_case(tmp_path):
    good = tmp_path / "ok.json"
    c = _case()
    c["simulation"] = {"n": 500, "seed": 1}
    good.write_text(json.dumps(c), encoding="utf-8")
    assert cli.main(["analyze", str(good), "--out", str(tmp_path / "o")]) == 0
    assert (tmp_path / "o" / "analysis.md").exists() and (tmp_path / "o" / "analysis.json").exists()


# F2 / F3 -------------------------------------------------------------------------------------------------------
def _set(c, path, value):
    cur = c
    for k in path[:-1]:
        cur = cur[k]
    cur[path[-1]] = value


BAD_SHAPES = [
    (["mitigations"], True), (["mitigations"], 5),
    (["options"], True), (["options"], 5),
    (["constraints"], 5), (["constraints"], [1]),
    (["simulation"], 5), (["simulation"], [1]),
    (["simulation", "correlation"], 5),
    (["mitigations", 0, "secondary_risks"], 5), (["mitigations", 0, "secondary_risks"], True),
    (["mitigations", 0, "evidence_ids"], 5), (["mitigations", 0, "evidence_ids"], [1, "a", [2]]),
    (["mitigations", 0, "evidence_ids"], [[1]]), (["mitigations", 0, "evidence_ids"], [{"a": 1}]),
]


@pytest.mark.parametrize("path,value", BAD_SHAPES)
def test_wrong_shape_inputs_give_a_case_error_not_a_crash(path, value):
    c = _case()
    c["simulation"] = {"n": 300, "seed": 1}
    _set(c, path, value)
    with pytest.raises(service.CaseError) as e:
        service.run_analysis(c)
    assert e.value.problems


def test_mixed_int_and_text_evidence_ids_are_accepted_as_text():
    c = _case()
    c["simulation"] = {"n": 300, "seed": 1}
    c["mitigations"][0]["evidence_ids"] = [7, "M01"]
    res = service.run_analysis(c)
    assert res["ok"]


def test_a_bare_string_evidence_id_is_one_id_not_its_characters():
    from app import analysis

    problems: list = []
    assert analysis._evidence_ids("M01", "m", problems) == ("M01",) and not problems


# F4 ------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("n", [1, 2, 5, 9, 10, 11])
def test_convergence_handles_tiny_n(n):
    res = simulate(Activity("A", "a", Param(10.0, Source.USER)), _two_risks(), n, 3)
    rows = convergence(res)
    assert rows and rows[-1]["n"] == n and all(r["n"] >= 1 for r in rows)
    assert [r["n"] for r in rows] == sorted(set(r["n"] for r in rows))


def _two_risks():
    return service.parse_case(service.example_case())["risks"][:2]


# F5 ------------------------------------------------------------------------------------------------------------
def test_risk_ids_with_the_same_crc32_are_refused():
    import zlib

    assert zlib.crc32(b"plumless") == zlib.crc32(b"buckeroo")
    a, b = _two_risks()
    from dataclasses import replace

    with pytest.raises(ValueError, match="same CRC32"):
        simulate(Activity("A", "a", Param(10.0, Source.USER)), [replace(a, risk_id="plumless"), replace(b, risk_id="buckeroo")], 100, 1)


# F6 ------------------------------------------------------------------------------------------------------------
def test_example_analysis_case_file_matches_the_service_example():
    f = ROOT / "examples" / "example_analysis_case.json"
    assert json.loads(f.read_text(encoding="utf-8-sig")) == service.example_analysis_case()
