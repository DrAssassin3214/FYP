import json
from copy import deepcopy

import pytest

from app.ai_layer.guard import StubLLM
from app.engine.matrix import DEFAULT_P_EDGES, classify
from app.reporting.register_report import register_csv
from app.service import (CaseError, evidence_lookup, example_case, matrix_legend, parse_case, risk_library,
                         rule_library, run_case, run_case_file, suggest_risks, template_case, _store)


def test_example_case_builds_the_register_and_matrix_and_is_reproducible():
    a, b = run_case(example_case()), run_case(example_case())
    assert a == b
    s = a["summary"]
    assert s["n_risks"] == s["n_complete"] == s["n_on_matrix"] == 7 and s["n_incomplete"] == 0
    assert a["warnings"] == [] and a["rule_base_issues"] == []
    assert sum(s["levels"].values()) == 7


def test_matrix_rows_match_the_engine_classification():
    case = example_case()
    res = run_case(case)
    pc = parse_case(case)
    expect = {m["risk_id"]: m for m in classify(pc["risks"], pc["planned"].value, pc["impact_edges"])}
    assert {m["risk_id"]: m for m in res["matrix"]} == expect
    mat = expect["R-MAT"]                     # p = 0.5 -> class 3 with the default edges; mean delay 3.5 d of 16 d
    assert mat["p_class"] == 3 and mat["impact_class"] == 5
    assert mat["expected_delay_if_occurs_days"] == pytest.approx(3.5)
    assert list(DEFAULT_P_EDGES) == matrix_legend()["probability_bin_edges"]


def test_example_case_file_matches_the_service_example():
    from pathlib import Path

    f = Path(__file__).resolve().parents[1] / "examples" / "example_case.json"
    assert json.loads(f.read_text(encoding="utf-8-sig")) == example_case()


def test_every_evidence_id_cited_by_the_example_exists_in_the_corpus():
    store = _store()
    for r in example_case()["risks"]:
        for e in r["evidence_ids"]:
            assert e in store, f"{r['id']} cites {e}, which is not in the evidence corpus"


def test_blank_template_is_a_valid_empty_register():
    res = run_case(template_case())
    assert res["summary"]["n_risks"] == 0 and res["matrix"] == []
    assert any("planned activity duration" in w for w in res["warnings"])


def test_a_risk_without_numbers_stays_in_the_register_but_off_the_matrix():
    c = example_case()
    c["risks"].append({"id": "R-DES", "name": "Design changes / incomplete drawings", "category": "Design", "status": "literature-supported",
                       "evidence_ids": ["M06"], "p": {"value": None, "source": ""},
                       "delay": {"kind": "pert", "a": None, "m": None, "b": None, "source": ""}})
    c["use_literature_seed"] = False
    res = run_case(c)
    row = next(r for r in res["risks"] if r["id"] == "R-DES")
    assert row["complete"] is False and row["p"] is None and row["delay"] is None
    assert res["summary"]["n_incomplete"] == 1 and res["summary"]["n_on_matrix"] == 7
    assert any("R-DES" in w and "probability and delay range not entered" in w for w in res["warnings"])
    assert "R-DES" not in {m["risk_id"] for m in res["matrix"]}


def test_only_one_of_p_and_delay_entered_is_reported_as_what_is_missing():
    c = example_case()
    c["risks"][0]["delay"]["b"] = None
    c["use_literature_seed"] = False
    res = run_case(c)
    assert any("R-MAT" in w and "delay range not entered" in w and "probability" not in w for w in res["warnings"])


def test_wrong_values_are_problems_not_silent_defaults():
    c = example_case()
    c["risks"][0]["p"]["value"] = 1.7
    with pytest.raises(CaseError) as e:
        run_case(c)
    assert any("probability must be in [0,1]" in p for p in e.value.problems)

    c = example_case()
    c["risks"][1]["p"]["source"] = None
    del c["risks"][1]["p"]["source"]
    with pytest.raises(CaseError) as e:
        run_case(c)
    assert any("source is required" in p for p in e.value.problems)

    c = example_case()
    c["risks"][2]["delay"] = dict(c["risks"][2]["delay"], a=5, m=2, b=1)
    with pytest.raises(CaseError):
        run_case(c)

    c = example_case()
    c["risks"].append(deepcopy(c["risks"][0]))
    with pytest.raises(CaseError) as e:
        run_case(c)
    assert any("duplicate id" in p for p in e.value.problems)

    c = example_case()
    c["activity"]["planned_duration_days"]["value"] = -3
    with pytest.raises(CaseError):
        run_case(c)


def test_impact_edges_are_validated_and_needed_for_the_matrix():
    c = example_case()
    c["impact_bin_edges_fraction"] = [0.1, 0.05, 0.2, 0.3]
    with pytest.raises(CaseError) as e:
        run_case(c)
    assert any("impact_bin_edges_fraction" in p for p in e.value.problems)

    c = example_case()
    c["impact_bin_edges_fraction"] = None
    res = run_case(c)
    assert res["matrix"] == [] and any("impact bin edges are not defined" in w for w in res["warnings"])

    c = example_case()
    c["activity"]["planned_duration_days"] = {"value": None, "source": "User Input"}
    res = run_case(c)
    assert res["matrix"] == [] and any("planned activity duration" in w for w in res["warnings"])


def test_rule_flags_for_risks_missing_from_the_register_are_reported():
    c = example_case()
    c["risks"] = [r for r in c["risks"] if r["id"] != "R-PLAN"]
    res = run_case(c)
    assert res["summary"]["n_flagged_missing"] == 1
    assert any("RL-PLAN" in w and "R-PLAN" in w and "not in the risk register" in w for w in res["warnings"])
    # a flagged risk that IS in the register but has no numbers yet is not reported as missing
    c["risks"].append({"id": "R-PLAN", "name": "Poor planning", "category": "Management", "status": "literature-supported",
                       "evidence_ids": ["M01"], "p": {"value": None, "source": ""}, "delay": {"kind": "pert", "source": ""}})
    res = run_case(c)
    assert res["summary"]["n_flagged_missing"] == 0


def test_unknown_facts_are_not_evaluable_never_guessed():
    c = example_case()
    c["facts"] = {}
    res = run_case(c)
    assert res["rules"]["fired"] == [] and res["rules"]["not_evaluable"]


def test_the_planned_duration_feeds_the_material_stock_rule():
    c = example_case()
    c["facts"] = {"material_stock_days": 2}
    fired = [f["rule_id"] for f in run_case(c)["rules"]["fired"]]
    assert "RL-MAT2" in fired
    c["activity"]["planned_duration_days"]["value"] = 2
    assert "RL-MAT2" not in [f["rule_id"] for f in run_case(c)["rules"]["fired"]]


def test_register_exports_contain_every_risk_with_its_source():
    res = run_case(example_case())
    md = res["report_markdown"]
    assert md.startswith("# Risk register and matrix") and "R-MAT" in md and "(Assumption)" in md
    assert "No number here was produced by AI" in md
    rows = register_csv(res).strip().splitlines()
    assert rows[0].startswith("id,name,category") and len(rows) == 8


def test_run_case_file_writes_the_register_files(tmp_path):
    f = tmp_path / "case.json"
    f.write_text(json.dumps(example_case()), encoding="utf-8")
    out = tmp_path / "out"
    run_case_file(f, out)
    assert (out / "register.md").exists() and (out / "register.csv").exists() and (out / "result.json").exists()


def test_libraries_are_present():
    assert len(risk_library()) >= 8 and len(rule_library()) >= 8
    assert {"R-LAB", "R-PAY"} <= {r["id"] for r in risk_library()}


def test_offline_suggestions_return_library_risks_and_evidence_without_numbers():
    out = suggest_risks("Brick masonry", "labour shortage payment")
    assert out["mode"] == "offline-retrieval" and {"R-LAB", "R-PAY"} <= {r["id"] for r in out["library_risks"]}
    assert out["evidence"]


def test_guarded_llm_suggestions_are_unverified_and_carry_no_numbers():
    stub = StubLLM(json.dumps({"risks": [{"name": "Scaffold delay", "category": "Equipment", "mechanism": "x",
                                          "evidence_ids": ["M01", "M999"], "p": 0.4}]}))
    out = suggest_risks("Brick masonry", "tools equipment scaffolding labour", client=stub)
    cand = out["candidates"][0]
    assert cand["status"] == "AI-suggested-unverified" and "p" in cand["rejected_numeric_fields"]
    assert any("M999" in i for i in cand["issues"])


def test_evidence_lookup_by_id_and_query():
    assert [r["id"] for r in evidence_lookup(ids=["M01"])] == ["M01"]
    assert evidence_lookup(query="labour productivity India")


def test_literature_seed_places_unnumbered_library_risks_on_the_matrix_as_a_ranking():
    from app.literature_seed import seed_for

    c = example_case()
    c["risks"].append({"id": "R-TOOL", "name": "Tools and equipment delay", "p": {"value": None}, "delay": {"kind": "pert"}})
    c["risks"].append({"id": "R-DES-X", "name": "Not in the seed table"})
    res = run_case(c)
    expect = seed_for("R-TOOL")
    row = next(r for r in res["risks"] if r["id"] == "R-TOOL")
    assert row["complete"] is False and row["seed"]["rank"] == expect["rank"] and row["seed"]["impact_class"] == expect["impact_class"]
    mx = next(m for m in res["matrix"] if m["risk_id"] == "R-TOOL")
    assert mx["basis"] == "literature-seed" and mx["p"] is None and mx["p_class"] == mx["impact_class"] == expect["impact_class"]
    assert res["summary"]["n_seeded"] == 1 and res["summary"]["n_on_matrix"] == 8
    assert any("R-TOOL" in w and "literature seed" in w for w in res["warnings"])
    assert any("R-DES-X" in w and "not on the matrix yet" in w for w in res["warnings"])   # no seed -> stays off


def test_entered_numbers_replace_the_seed_and_a_rule_flag_raises_probability_class():
    res = run_case(example_case())
    assert all(r["seed"] is None for r in res["risks"]) and res["summary"]["n_seeded"] == 0
    from app.literature_seed import seed_for
    assert seed_for("R-TOOL", elevated=True)["p_class"] == seed_for("R-TOOL")["p_class"] + 1
    assert seed_for("R-MAT")["p_class"] == 5 and seed_for("R-MAT", elevated=True)["p_class"] == 5   # capped
    assert seed_for("R-NOPE") is None                                   # not in the dataset


def test_literature_seed_uses_only_direct_values_from_seed_studies_averaged_per_study():
    from app.literature_seed import load_dataset, seed_observations, seed_table
    data = load_dataset()
    roles = {s["id"]: s["role"] for s in data["studies"]}
    obs = seed_observations(data)
    assert obs and all(roles[o["study"]] == "seed" and o["mapping"] == "direct" for o in obs)
    t = seed_table()
    # R-SAFE: M01 has two direct items (0.809, 0.764) -> one study mean; "accidents" (related) is ignored
    assert t["R-SAFE"]["study_means"] == {"M01": 0.7865} and t["R-SAFE"]["mean_rii"] == 0.7865
    # held-out validation studies never feed the seed
    assert not ({"M10", "M15", "M14", "A10", "A21", "HAS25"} & {o["study"] for o in obs})
    classes = [v["class"] for v in t.values() if v["class"] is not None]
    n = len(classes)
    assert n >= 28 and all(classes.count(k) in (n // 5, n // 5 + 1) for k in (1, 2, 3, 4, 5))   # equal-count bands
    # the ten core risks keep their mean RII when the library grows (their values do not depend on the new risks)
    assert t["R-MAT"]["mean_rii"] == 0.7889 and t["R-WX"]["mean_rii"] == 0.6934


def test_library_covers_the_literature_and_every_risk_is_traceable_to_evidence():
    lib = risk_library()
    ids = [r["id"] for r in lib]
    assert len(lib) >= 35 and len(set(ids)) == len(ids)
    assert {"Labour", "Management", "Material", "Safety", "Weather", "External", "Site"} <= {r["category"] for r in lib}
    assert all(r["existence_evidence"] and r["evidence_note"] and r["scope"] in ("activity", "project") for r in lib)
    from app.literature_seed import load_dataset
    rows = load_dataset()["rows"]
    mapped = {r["risk"] for r in rows if r.get("risk")}
    assert mapped <= set(ids)                                        # every mapped factor points at a library risk
    assert set(ids) <= mapped                                        # and every library risk has at least one paper value behind it


def test_adding_the_whole_library_with_no_numbers_places_the_seeded_risks_and_keeps_the_rest_off():
    c = example_case()
    c["risks"] = [{"id": r["id"], "name": r["name"], "category": r["category"]} for r in risk_library()]
    res = run_case(c)
    s = res["summary"]
    assert s["n_risks"] == len(risk_library()) and s["n_complete"] == 0
    assert s["n_seeded"] == s["n_on_matrix"] and 28 <= s["n_seeded"] < s["n_risks"]
    assert all(m["basis"] == "literature-seed" and m["p"] is None for m in res["matrix"])
    unseeded = [r["id"] for r in res["risks"] if not r["seed"]]
    assert unseeded and all(any(w.startswith(f"{u}: not on the matrix yet") for w in res["warnings"]) for u in unseeded)


def test_graphical_exports_draw_the_matrix_and_the_report():
    import xml.dom.minidom
    from app.reporting.matrix_graphic import register_html
    c = example_case()
    c["risks"].append({"id": "R-TOOL", "name": "Tools and equipment delay"})
    res = run_case(c)
    svg = res["matrix_svg"]
    xml.dom.minidom.parseString(svg)                                   # well-formed
    assert svg.count("<rect") >= 25 and ">MAT<" in svg and ">TOOL<" in svg and "stroke-dasharray" in svg
    html = register_html(res)
    assert "<svg" in html and "Risk register" in html and "literature seed" in html
