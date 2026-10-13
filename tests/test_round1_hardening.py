"""Round-1 audit fixes (docs/refine_round_1/triage.md): engine edge cases, analysis-side input validation, CLI errors.

Each test names the finding it covers.  Expected values are written out, not computed by the code under test.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from app import cli, service
from app.engine.matrix import impact_class, matrix_level, probability_class

ROOT = Path(__file__).resolve().parents[1]
EDGES = [0.02, 0.05, 0.1, 0.2]


def problems(case, fn=service.run_analysis):
    with pytest.raises(service.CaseError) as e:
        fn(case)
    return e.value.problems


def has(ps, *parts):
    return any(all(x in p for x in parts) for p in ps)


# ------------------------------------------------------------------------------------------------ A-01 matrix guards
@pytest.mark.parametrize("p", [True, False, float("nan"), -0.01, 1.01, "0.5", None])
def test_a01_probability_class_rejects_non_numbers_and_out_of_range(p):
    with pytest.raises(ValueError, match="p must be a number in"):
        probability_class(p)


def test_a01_probability_class_rejects_nan_and_unsorted_edges():
    with pytest.raises(ValueError, match="finite"):
        probability_class(0.5, (0.2, float("nan"), 0.6, 0.8))
    with pytest.raises(ValueError, match="ascending"):
        probability_class(0.5, (0.4, 0.2, 0.6, 0.8))


def test_a01_impact_class_rejects_negative_delay_and_bad_edges():
    with pytest.raises(ValueError, match="0 or more"):
        impact_class(-1, 10, EDGES)
    with pytest.raises(ValueError, match="finite"):
        impact_class(1, 10, [0.02, float("inf"), 0.1, 0.2])
    with pytest.raises(ValueError, match="ascending"):
        impact_class(1, 10, [0.2, 0.1, 0.05, 0.02])


@pytest.mark.parametrize("pc,ic", [(0, 1), (1, 0), (6, 1), (1, 6), (True, 2), (2.5, 2)])
def test_a01_matrix_level_rejects_classes_outside_1_to_5(pc, ic):
    with pytest.raises(ValueError, match="whole number from 1 to 5"):
        matrix_level(pc, ic)


# ------------------------------------------------------------------------------------------------ A-06 boundaries
@pytest.mark.parametrize("pc,ic,level", [
    (1, 3, "Low"), (1, 5, "Low"),                  # scores 3, 5
    (2, 3, "Moderate"), (2, 5, "Moderate"),        # scores 6, 10
    (3, 4, "High"), (3, 5, "High"),                # scores 12, 15
    (4, 4, "Extreme"), (5, 5, "Extreme"), (4, 5, "Extreme"),   # scores 16, 25, 20
    (3, 3, "Moderate"), (2, 4, "Moderate"),        # scores 9, 8
])
def test_a06_matrix_level_at_score_boundaries(pc, ic, level):
    assert matrix_level(pc, ic) == level


def test_a06_matrix_level_score_boundaries_5_6_10_11_15_16():
    # reachable scores on a 5x5 grid: 5 -> Low, 6 -> Moderate, 10 -> Moderate, 12 -> High, 15 -> High, 16 -> Extreme
    assert [matrix_level(1, 5), matrix_level(2, 3), matrix_level(2, 5), matrix_level(3, 4),
            matrix_level(3, 5), matrix_level(4, 4)] == ["Low", "Moderate", "Moderate", "High", "High", "Extreme"]


@pytest.mark.parametrize("p,cls", [(0.0, 1), (0.1999, 1), (0.2, 2), (0.3999, 2), (0.4, 3), (0.6, 4), (0.8, 5), (1.0, 5)])
def test_a06_probability_class_on_every_edge(p, cls):
    assert probability_class(p) == cls


# ------------------------------------------------------------------------------------------------ determinism (new finding)
def test_facts_used_order_is_independent_of_hash_randomisation():
    code = ("import json; from app import service; r = service.run_case(service.example_case());"
            "print(json.dumps([list(f['facts_used']) for f in r['rules']['fired']]))")
    outs = set()
    for seed in ("1", "2", "3"):
        env = dict(os.environ, PYTHONHASHSEED=seed, PYTHONPATH=str(ROOT))
        out = subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=env, capture_output=True, text=True, timeout=120)
        assert out.returncode == 0, out.stderr[-400:]
        outs.add(out.stdout.strip())
    assert len(outs) == 1


# ------------------------------------------------------------------------------------------------ A2 analysis validation
def ex():
    return service.example_analysis_case()


@pytest.mark.parametrize("n", [1, 5, 9])
def test_a2_01_small_simulation_n_is_rejected_with_a_message(n):
    c = ex()
    c["simulation"] = {"n": n}
    assert has(problems(c), "simulation.n", "from 10 to 200000")


def test_a2_01_n_10_runs():
    c = ex()
    c["simulation"] = {"n": 10}
    assert service.run_analysis(c)["command"]["command"]


@pytest.mark.parametrize("key,val", [("mitigations", 5), ("options", 5), ("simulation", 5), ("constraints", "x"),
                                     ("cost", "x")])
def test_a2_03_wrong_type_blocks_name_the_field(key, val):
    c = ex()
    c[key] = val
    assert has(problems(c), key, "expected")


def test_a2_03_correlation_must_be_a_list():
    c = ex()
    c["simulation"] = {"correlation": 5}
    assert has(problems(c), "simulation.correlation", "expected a list")


def test_a2_05_bare_string_evidence_ids_are_rejected_not_split():
    c = ex()
    c["mitigations"][0]["evidence_ids"] = "D03"
    assert has(problems(c), "evidence_ids", "list of evidence id strings")


def test_a2_05_option_mitigation_ids_bare_string():
    c = ex()
    c["options"] = [{"id": "o1", "mitigation_ids": "M-BUF"}]
    assert has(problems(c), "options[0]", "mitigation_ids", "list")


@pytest.mark.parametrize("bad", [float("nan"), float("inf")])
def test_a2_06_a2_07_non_finite_numbers_are_rejected(bad):
    c = ex()
    c["constraints"] = {"max_mitigation_budget": bad}
    assert has(problems(c), "constraints.max_mitigation_budget", "finite")
    c = ex()
    c["mitigations"][0]["time_to_implement_days"] = bad
    assert has(problems(c), "time_to_implement_days", "finite")


def test_a2_08_a2_09_a2_10_overflow_values_are_rejected_with_the_field_name():
    c = ex()
    c["cost"]["ld_per_day_after_deadline"] = {"value": 1e308, "source": "Assumption"}
    assert has(problems(c), "ld_per_day_after_deadline", "too large")
    c = ex()
    c["activity"]["planned_duration_days"] = {"value": 1e308, "source": "Assumption"}
    assert has(problems(c), "planned_duration_days", "too large")
    c = ex()
    c["risks"][0]["delay"].update(a=1e308, m=1e308, b=1e308)
    assert has(problems(c), "risks[0].delay", "too large")


def test_a2_11_bare_number_for_a_cost_block_is_a_problem_not_silently_ignored():
    c = ex()
    c["risks"][0]["direct_cost_if_occurs"] = 5
    assert has(problems(c), "direct_cost_if_occurs", "expected an object")
    c = ex()
    c["mitigations"][0]["p_after"] = 0.1
    assert has(problems(c), "p_after", "expected an object")
    c = ex()
    c["mitigations"][0]["delay_after"] = 5
    assert has(problems(c), "delay_after", "expected an object")


@pytest.mark.parametrize("key,val", [("strategy", 0), ("strategy", ["x"])])
def test_a2_12_falsy_strategy_is_not_replaced_by_the_default(key, val):
    c = ex()
    c["mitigations"][0][key] = val
    assert has(problems(c), "unknown strategy")


def test_a2_12_criterion_zero_is_rejected():
    c = ex()
    c["simulation"] = {"criterion": 0}
    assert has(problems(c), "simulation.criterion", "unknown")


# ------------------------------------------------------------------------------------------------ A2 register side
def risk(**kw):
    d = {"id": "R1"}
    d.update(kw)
    return {"risks": [d]}


def test_a2_04_evidence_ids_inside_incomplete_p_or_delay_are_validated():
    assert has(problems(risk(p={"value": None, "source": "Assumption", "evidence_ids": 5}), service.run_case),
               "p.evidence_ids")
    assert has(problems(risk(p={"value": 0.5, "source": "Assumption"},
                             delay={"kind": "pert", "a": 1, "source": "Assumption", "evidence_ids": [["a"]]}),
                        service.run_case), "delay.evidence_ids")


@pytest.mark.parametrize("v", ["٠.٥", "0_5", "０.５", "1e", "--1"])
def test_a2_17_only_plain_ascii_decimals_are_numbers(v):
    assert has(problems(risk(p={"value": v, "source": "Assumption"}), service.run_case), "risks[0].p.value", "not a number")


@pytest.mark.parametrize("v", ["0.5", " 0.5 ", "+0.5", ".5", "5e-1"])
def test_a2_17_ordinary_decimal_strings_still_work(v):
    res = service.run_case(risk(p={"value": v, "source": "Assumption"}))
    assert res["risks"][0]["p"]["value"] == 0.5


def test_a2_16_ids_differing_by_case_or_space_get_a_warning():
    res = service.run_case({"risks": [{"id": "r-mat"}, {"id": "R-MAT"}]})
    assert any("differ only by case or spaces" in w for w in res["warnings"])


def test_a2_18_line_breaks_in_single_line_fields_cannot_inject_markdown():
    res = service.run_case({"project": {"name": "Site A\r\n## Injected", "location": "x\ny"},
                            "impact_bin_edges_fraction": EDGES,
                            "impact_bin_edges_source": {"source": "Assumption", "note": "a\r\n## Heading"}})
    md = res["report_markdown"]
    assert "\n## Injected" not in md and "\n## Heading" not in md
    assert res["project"]["name"] == "Site A ## Injected"


# ------------------------------------------------------------------------------------------------ A2-14 API
def test_a2_14_validate_rejects_a_non_object_case():
    import gui.api
    c = gui.api.create_app().test_client()
    for body in ({"case": [1]}, {"case": "x"}, {"case": 5}):
        r = c.post("/api/validate", json=body)
        assert r.status_code in (400, 422), (body, r.status_code)
        assert "'case' must be a JSON object" in json.dumps(r.get_json())


# ------------------------------------------------------------------------------------------------ A2-02 / A2-13 CLI
def run_cli(argv, capsys):
    rc = cli.main(argv)
    out = capsys.readouterr()
    return rc, out.out, out.err


def test_a2_02_analyze_reports_errors_in_one_line_like_run(tmp_path, capsys):
    rc, _, err = run_cli(["analyze", str(tmp_path / "missing.json")], capsys)
    assert rc == 2 and "case file not found" in err and "Traceback" not in err
    rc, _, err = run_cli(["analyze", str(tmp_path)], capsys)
    assert rc == 2 and "is a folder" in err
    empty = tmp_path / "e.json"
    empty.write_bytes(b"")
    rc, _, err = run_cli(["analyze", str(empty)], capsys)
    assert rc == 2 and "is empty" in err
    u16 = tmp_path / "u.json"
    u16.write_bytes("{}".encode("utf-16"))
    rc, _, err = run_cli(["analyze", str(u16)], capsys)
    assert rc == 2 and "UTF-16" in err


def test_a2_02_analyze_out_pointing_at_a_file_and_bad_block(tmp_path, capsys):
    case = tmp_path / "a.json"
    case.write_text(json.dumps(ex()), encoding="utf-8")
    f = tmp_path / "afile"
    f.write_text("x")
    rc, _, err = run_cli(["analyze", str(case), "--out", str(f)], capsys)
    assert rc == 2 and "is a file; give a folder" in err
    bad = ex()
    bad["simulation"] = "x"
    case.write_text(json.dumps(bad), encoding="utf-8")
    rc, _, err = run_cli(["analyze", str(case)], capsys)
    assert rc == 2 and "Case has problems" in err and "simulation" in err


def test_a2_02_analyze_writes_valid_json(tmp_path, capsys):
    case = tmp_path / "a.json"
    case.write_text(json.dumps(ex()), encoding="utf-8")
    rc, out, _ = run_cli(["analyze", str(case), "--out", str(tmp_path / "o")], capsys)
    assert rc == 0 and out.strip()
    json.loads((tmp_path / "o" / "analysis.json").read_text(encoding="utf-8"), parse_constant=lambda c: pytest.fail(c))


def test_a2_13_run_with_only_seeded_risks_prints_a_complete_sentence(tmp_path, capsys):
    case = tmp_path / "c.json"
    case.write_text(json.dumps({"risks": [{"id": "R-MAT"}, {"id": "R-LAB"}]}), encoding="utf-8")
    rc, out, _ = run_cli(["run", str(case)], capsys)
    assert rc == 0
    assert not out.splitlines()[0].rstrip().endswith(":")


# ------------------------------------------------------------------------------------------------ B-10 CSV
def test_b10_csv_leaves_class_and_score_blank_for_tier_rows_and_rounds_delay():
    import csv
    import io
    from app.reporting.register_report import register_csv
    res = service.run_case(service.example_case() | {"risks": service.example_case()["risks"][:1] + [{"id": "R-LAB"}]})
    rows = {r["id"]: r for r in csv.DictReader(io.StringIO(register_csv(res)))}
    tier = rows["R-LAB"]
    assert tier["tier"].startswith("literature tier") and tier["level"] == ""
    assert tier["p_class"] == tier["impact_class"] == tier["score"] == ""
    entered = rows[service.example_case()["risks"][0]["id"]]
    assert entered["score"] and len(entered["expected_delay_days"].split(".")[-1]) <= 2


# ------------------------------------------------------------------------------------------------ C-08 / C-09 guards
def test_c09_check_numbers_no_longer_accepts_a_bare_number_scaled_by_100():
    from app.ai_layer.explain import check_numbers
    trace = {"mean": 120.4, "p_exceed": 0.123}
    assert check_numbers("The mean is 120.4 days.", trace) == []
    assert check_numbers("The chance is 12.3%.", trace) == []          # fraction shown as a percentage: stated by the % sign
    assert check_numbers("The mean is 1.2 days.", trace) == ["1.2"]    # invented: 120.4 / 100
    assert check_numbers("The mean is 12040 days.", trace) == ["12040"]


def test_c08_g3_empty_quote_and_quote_for_an_uncited_id_are_flagged():
    from tests.test_ai_guard import STORE, llm_out
    from app.ai_layer.guard import parse_and_validate
    empty = parse_and_validate(llm_out(quotes={"M01": ""}), {"M01"}, STORE)[0]
    assert any("G3" in i and "empty" in i for i in empty.issues)
    uncited = parse_and_validate(llm_out(evidence_ids=[], quotes={"M01": "Material shortage and tools delay"}), {"M01"}, STORE)[0]
    assert any("G3" in i and "does not cite" in i for i in uncited.issues)
    ok = parse_and_validate(llm_out(), {"M01"}, STORE)[0]
    assert ok.issues == []


# ------------------------------------------------------------------------------------------------ outlier warning
def test_delay_far_longer_than_the_activity_gets_a_unit_warning_not_a_rejection():
    c = service.example_case()                                        # planned duration 16 d
    c["risks"][0]["delay"].update(a=1, m=4, b=96)                      # 96 d = 6 x planned: looks like hours entered as days
    res = service.run_case(c)
    assert any(w.startswith(f"{c['risks'][0]['id']}: maximum delay 96 d") and "unit" in w for w in res["warnings"])
    assert res["summary"]["n_on_matrix"] >= 1                          # still computed; the person decides
    assert not any("maximum delay" in w for w in service.run_case(service.example_case())["warnings"])
