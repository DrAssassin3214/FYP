"""Regression tests for the validation hardening of app.service / app.engine (audit 2026-10-08)."""
import json
import math
from copy import deepcopy

import pytest

from app.engine.matrix import impact_class
from app.engine.models import DelayDist
from app.engine.rules import Cond, Rule, evaluate_rules
from app.service import CaseError, example_case, parse_case, run_case


def problems_of(case):
    with pytest.raises(CaseError) as e:
        run_case(case)
    return e.value.problems


def has(problems, *needles):
    return any(all(n in p for n in needles) for p in problems)


# ------------------------------------------------------------------ H1 finite numbers
@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf"), "nan", "inf", "-inf"])
def test_h1_planned_duration_must_be_finite(bad):
    c = example_case()
    c["activity"]["planned_duration_days"]["value"] = bad
    assert has(problems_of(c), "planned_duration_days", "must be a finite number")


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), "nan", "inf"])
def test_h1_probability_must_be_finite(bad):
    c = example_case()
    c["risks"][0]["p"]["value"] = bad
    assert has(problems_of(c), "must be a finite number")


@pytest.mark.parametrize("kind,field", [("pert", "a"), ("pert", "m"), ("pert", "b"), ("pert", "lam"),
                                        ("triangular", "m"), ("uniform", "a"), ("uniform", "b"), ("fixed", "m")])
@pytest.mark.parametrize("bad", [float("nan"), "inf", "nan", float("-inf")])
def test_h1_every_delay_parameter_must_be_finite(kind, field, bad):
    c = example_case()
    d = {"kind": kind, "source": "Assumption"}
    d.update({"pert": dict(a=1, m=2, b=5), "triangular": dict(a=1, m=2, b=5),
              "uniform": dict(a=1, b=5), "fixed": dict(m=2)}[kind])
    d[field] = bad
    c["risks"][0]["delay"] = d
    assert has(problems_of(c), ".delay", "must be a finite number")


def test_h1_engine_models_also_refuse_non_finite_delays():
    for d in (DelayDist("pert", 1, float("nan"), 3), DelayDist("fixed", 0, float("inf"), 0),
              DelayDist("uniform", float("nan"), 0, 3), DelayDist("pert", 1, 2, 3, lam=float("inf"))):
        with pytest.raises(ValueError):
            d.validate()


# ------------------------------------------------------------------ M1 booleans
def test_m1_booleans_are_not_numbers():
    c = example_case()
    c["risks"][0]["p"]["value"] = True
    assert has(problems_of(c), "must be a number, not true")
    c = example_case()
    c["activity"]["planned_duration_days"]["value"] = False
    assert has(problems_of(c), "planned_duration_days", "must be a number, not false")
    c = example_case()
    c["risks"][0]["delay"]["b"] = True
    assert has(problems_of(c), "delay.b", "must be a number, not true")
    c = example_case()
    c["impact_bin_edges_fraction"] = [0.02, 0.05, True, 0.2]
    assert has(problems_of(c), "impact_bin_edges_fraction[2]", "not true")
    c = example_case()
    c["risks"][0]["delay"]["lam"] = True
    assert has(problems_of(c), "delay.lam", "not true")


# ------------------------------------------------------------------ H2 delay source required
def test_h2_delay_without_source_is_a_problem_not_expert_judgment():
    c = example_case()
    del c["risks"][0]["delay"]["source"]
    assert has(problems_of(c), "risks[0].delay", "source is required")
    c = example_case()
    c["risks"][0]["delay"]["source"] = "made up"
    assert has(problems_of(c), "risks[0].delay", "unknown source")


def test_h2_example_case_still_validates_with_assumption_sources():
    res = run_case(example_case())
    assert all(r["delay"]["source"] == "Assumption" and r["p"]["source"] == "Assumption" for r in res["risks"])
    mat = next(m for m in res["matrix"] if m["risk_id"] == "R-MAT")
    assert (mat["p_class"], mat["impact_class"], mat["level"]) == (3, 5, "High")


# ------------------------------------------------------------------ M2 / QA#4 / M3 incomplete risks
def _incomplete(p=None, delay=None):
    c = example_case()
    r = c["risks"][0]
    r["p"] = p if p is not None else {"value": None, "source": ""}
    r["delay"] = delay if delay is not None else {"kind": "pert", "a": None, "m": None, "b": None, "source": ""}
    c["risks"] = [r]
    return c


@pytest.mark.parametrize("bad", [-1, 1.5, "abc", 7, "nan"])
def test_m2_bad_probability_rejected_even_without_a_delay(bad):
    c = _incomplete(p={"value": bad, "source": "Assumption"})
    assert problems_of(c)


@pytest.mark.parametrize("bad", [-1, 1.5, "abc", 7, 0.3, True])
def test_m2_bare_probability_value_rejected(bad):
    c = example_case()
    c["risks"][0]["p"] = bad
    assert has(problems_of(c), "risks[0].p", "expected an object")


@pytest.mark.parametrize("bad", [5, "x", [1, 2], True])
def test_m2_non_object_delay_rejected(bad):
    c = example_case()
    c["risks"][0]["delay"] = bad
    assert has(problems_of(c), "risks[0].delay", "expected an object")


def test_m2_null_delay_and_unknown_status_and_entered_delay_values():
    c = example_case()
    c["risks"][0]["delay"] = None
    assert not any("risks[0]" in p for p in run_case(c)["warnings"] if "problem" in p)
    c = _incomplete()
    c["risks"][0]["status"] = "bogus"
    assert has(problems_of(c), "unknown status 'bogus'")
    c = _incomplete(delay={"kind": "pert", "a": "abc", "m": None, "b": None, "source": "Assumption"})
    assert has(problems_of(c), "delay.a")
    c = _incomplete(delay={"kind": "weird", "a": 1, "m": 2, "b": 3, "source": "Assumption"})
    assert has(problems_of(c), "unknown distribution kind")


def test_m3_partial_probability_is_kept_in_the_register_and_seed_is_flagged():
    c = _incomplete(p={"value": 0.05, "source": "User Input"})
    res = run_case(c)
    row = res["risks"][0]
    assert row["complete"] is False and row["delay"] is None
    assert row["p"]["value"] == 0.05 and row["p"]["source"] == "User Input"
    cell = res["matrix"][0]
    assert cell["basis"] == "literature-seed" and cell["risk_id"] == "R-MAT"
    assert "incomplete" in cell["note"] and "delay range not entered" in cell["note"]
    assert "0.05" in cell["note"]


def test_m3_delay_only_entered_has_no_p_but_notes_incompleteness():
    c = _incomplete(delay={"kind": "pert", "a": 1, "m": 2, "b": 5, "source": "Assumption"})
    res = run_case(c)
    assert res["risks"][0]["p"] is None
    assert "probability not entered" in res["matrix"][0]["note"]


# ------------------------------------------------------------------ M4 edges
def test_m4_exact_edge_goes_to_the_higher_class():
    E = [0.02, 0.05, 0.10, 0.20]
    assert impact_class(1.2, 12, E) == 4          # exactly 0.10 -> class 4 (was 3)
    assert impact_class(0.6, 3, E) == 5           # exactly 0.20 -> class 5 (was 4)
    assert DelayDist("pert", 0, 0.9, 3).mean() / 11 == pytest.approx(0.1)
    assert impact_class(DelayDist("pert", 0, 0.9, 3).mean(), 11, E) == 4
    assert impact_class(0.0999, 1, E) == 3        # clearly below stays below
    assert impact_class(0.2001, 1, E) == 5


def test_m4_brute_force_one_decimal_grid_matches_exact_arithmetic():
    from fractions import Fraction

    E = [0.02, 0.05, 0.10, 0.20]
    FE = [Fraction(2, 100), Fraction(5, 100), Fraction(10, 100), Fraction(20, 100)]
    for base10 in range(5, 400):                        # baselines 0.5 .. 39.9 days
        for d10 in range(0, 200):                       # delays 0.0 .. 19.9 days
            exact = Fraction(d10, 10) / Fraction(base10, 10)
            want = 1 + sum(1 for e in FE if exact >= e)
            assert impact_class(d10 / 10, base10 / 10, E) == want, (d10, base10)


def test_m4_non_finite_inputs_rejected_by_impact_class():
    for args in ((float("nan"), 10), (1, float("inf")), (float("inf"), 10)):
        with pytest.raises(ValueError):
            impact_class(*args, [0.02, 0.05, 0.1, 0.2])


# ------------------------------------------------------------------ M5 rule fact types
def _eval(rule, facts):
    return evaluate_rules([rule], facts)


NUM = Rule("RN", "d", "R-LAB", all_of=(Cond("req", "gt", other_fact="avail"),))
BOOL = Rule("RB", "d", "R-WX", all_of=(Cond("wet", "eq", True),))
LIT = Rule("RL", "d", "R-MAT", all_of=(Cond("stock", "lt", 5),))


@pytest.mark.parametrize("facts", [{"req": "10", "avail": "9"}, {"req": 10, "avail": "9"}, {"req": "10", "avail": 9},
                                   {"req": float("nan"), "avail": 5}, {"req": True, "avail": 0},
                                   {"req": float("inf"), "avail": 5}])
def test_m5_numeric_rules_need_real_finite_numbers(facts):
    out = _eval(NUM, facts)
    assert out["fired"] == [] and out["flags"] == {}
    ne = out["not_evaluable"]
    assert [x["rule_id"] for x in ne] == ["RN"] and ne[0]["reasons"]


@pytest.mark.parametrize("v", ["true", "yes", 1, 0, "True", [True]])
def test_m5_boolean_rules_need_real_booleans(v):
    out = _eval(BOOL, {"wet": v})
    assert out["fired"] == [] and out["not_evaluable"][0]["rule_id"] == "RB"
    assert _eval(BOOL, {"wet": True})["fired"][0]["rule_id"] == "RB"
    assert _eval(BOOL, {"wet": False}) ["not_evaluable"] == []


def test_m5_literal_numeric_threshold_and_valid_values_still_work():
    assert _eval(LIT, {"stock": 2})["fired"][0]["rule_id"] == "RL"
    assert _eval(LIT, {"stock": 9})["fired"] == []
    assert _eval(LIT, {"stock": "2"})["not_evaluable"][0]["rule_id"] == "RL"
    assert _eval(LIT, {"stock": True})["not_evaluable"][0]["rule_id"] == "RL"


def test_m5_through_the_service_a_string_fact_is_reported_not_silently_false():
    c = example_case()
    c["facts"]["required_workers"] = "10"
    c["facts"]["available_workers"] = "9"
    res = run_case(c)
    ne = {x["rule_id"]: x for x in res["rules"]["not_evaluable"]}
    assert "RL-LAB" in ne and ne["RL-LAB"]["reasons"]
    assert "RL-LAB" not in [f["rule_id"] for f in res["rules"]["fired"]]


# ------------------------------------------------------------------ M6 malformed shapes
@pytest.mark.parametrize("key,val", [("project", "s"), ("project", [1]), ("activity", "oops"), ("activity", 5),
                                     ("facts", "abc"), ("facts", [1, 2]), ("risks", {"a": 1}),
                                     ("risks", ["R-MAT", "R-LAB"]), ("risks", "R-MAT"), ("rules", "x"),
                                     ("rules", [5]), ("rules", {"a": 1})])
def test_m6_wrong_container_types_give_a_clean_problem_list(key, val):
    c = example_case()
    c[key] = val
    assert problems_of(c)


def test_m6_non_object_case_is_a_case_error():
    for bad in ([], "x", 5, None):
        with pytest.raises(CaseError):
            parse_case(bad)


@pytest.mark.parametrize("path,val", [(("project", "name"), 5), (("activity", "name"), 5), (("activity", "id"), True),
                                      (("project", "notes"), ["x"])])
def test_m6_non_string_names(path, val):
    c = example_case()
    c[path[0]][path[1]] = val
    assert has(problems_of(c), ".".join(path), "must be text")


@pytest.mark.parametrize("k", ["name", "category", "description"])
@pytest.mark.parametrize("val", [5, True, [1], {}])
def test_m6_non_string_risk_texts(k, val):
    c = example_case()
    c["risks"][0][k] = val
    assert has(problems_of(c), f"risks[0].{k}", "must be text")


@pytest.mark.parametrize("val", ["M01", 5, [1], {"a": 1}])
def test_m6_evidence_ids_must_be_a_list_of_strings(val):
    for where in ("risk", "p", "delay"):
        c = example_case()
        target = c["risks"][0] if where == "risk" else c["risks"][0][where]
        target["evidence_ids"] = val
        assert has(problems_of(c), "evidence_ids"), where


def test_m6_rule_shape_problems():
    base = {"id": "X", "risk_id": "R-MAT", "all_of": [{"fact": "a", "op": "gt", "value": 1}]}
    cases = [dict(base, priority="high"), dict(base, priority=True), dict(base, priority=1.5),
             dict(base, all_of=[{"fact": "a", "op": "??", "value": 1}]),
             dict(base, all_of="nope"), dict(base, all_of=[5]), dict(base, evidence_ids="M01"),
             {"risk_id": "R-MAT", "all_of": []}]
    for rule in cases:
        c = example_case()
        c["rules"] = [rule]
        probs = problems_of(c)
        assert probs and all(isinstance(p, str) for p in probs), rule
    c = example_case()
    c["rules"] = [dict(base, priority=3)]
    run_case(c)


def test_m6_in_operator_with_a_non_list_value_is_not_evaluable_not_a_crash():
    r = Rule("RI", "d", "R-X", all_of=(Cond("a", "in", 5),))
    assert evaluate_rules([r], {"a": 1})["not_evaluable"][0]["rule_id"] == "RI"


# ------------------------------------------------------------------ M9 exactly four edges
@pytest.mark.parametrize("edges", [[0.1], [0.1, 0.2], [0.01, 0.02, 0.05, 0.1, 0.2], [0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
                                   [], "abc", 0.1, [0.2, 0.1, 0.3, 0.4], [0.1, 0.1, 0.2, 0.3], [0.1, 0.2, 0.3, 1.0],
                                   [0, 0.1, 0.2, 0.3], [0.1, 0.2, float("nan"), 0.4], [0.1, 0.2, "inf", 0.4]])
def test_m9_service_requires_exactly_four_strictly_increasing_finite_edges(edges):
    c = example_case()
    c["impact_bin_edges_fraction"] = edges
    assert has(problems_of(c), "impact_bin_edges_fraction")


# ------------------------------------------------------------------ L1 / L2 / L4 / L5 / QA#14
def test_l1_planned_duration_fact_cannot_override_the_activity_value():
    c = example_case()
    c["facts"] = {"planned_duration_days": 5, "material_stock_days": 10}
    assert has(problems_of(c), "facts.planned_duration_days", "conflicts")
    c["facts"]["planned_duration_days"] = 16                        # same value: harmless
    assert "RL-MAT2" in [f["rule_id"] for f in run_case(c)["rules"]["fired"]]      # 10 < 16 (activity value)
    c["facts"] = {"material_stock_days": 20}                        # 20 < 16 is false -> does not fire
    assert "RL-MAT2" not in [f["rule_id"] for f in run_case(c)["rules"]["fired"]]
    assert parse_case(c)["facts"]["planned_duration_days"] == 16


def test_l2_unknown_fact_names_are_reported():
    c = example_case()
    c["facts"]["monsoon_overlapp"] = True
    res = run_case(c)
    assert any("unknown fact 'monsoon_overlapp'" in w for w in res["warnings"])
    assert run_case(example_case())["warnings"] == []
    c = example_case()
    c["rules"] = [{"id": "X1", "risk_id": "R-MAT", "all_of": [{"fact": "never_given", "op": "eq", "value": True}],
                   "source": "Assumption", "confidence": "Low"}]
    assert any("unknown fact 'never_given'" in i for i in run_case(c)["rule_base_issues"])


@pytest.mark.parametrize("val", ["false", "true", 0, 1, "no"])
def test_l4_use_literature_seed_must_be_a_real_boolean(val):
    c = example_case()
    c["use_literature_seed"] = val
    assert has(problems_of(c), "use_literature_seed", "true or false")
    c = example_case()
    c["seed_basis"] = "weird"
    assert has(problems_of(c), "seed_basis")


def test_l5_uniform_does_not_need_or_use_m():
    c = example_case()
    c["risks"][0]["delay"] = {"kind": "uniform", "a": 2, "b": 6, "source": "Assumption"}
    res = run_case(c)
    row = res["risks"][0]
    assert row["complete"] and row["delay"]["mean"] == 4.0
    c["risks"][0]["delay"]["m"] = 99                                 # ignored, even if absurd
    assert run_case(c)["risks"][0]["delay"]["mean"] == 4.0


def test_qa14_unknown_evidence_ids_are_warnings_not_errors():
    c = example_case()
    c["risks"][0]["evidence_ids"] = ["M01", "ZZ99"]
    res = run_case(c, {"M01": "cite", "M06": "cite", "M07": "x", "M15": "x", "M03": "x", "R08": "x", "M14": "x"})
    assert any("unknown evidence id 'ZZ99'" in w for w in res["warnings"])
    assert not any("'M01'" in w for w in res["warnings"])
    assert res["ok"] is True


# ------------------------------------------------------------------ results unchanged / JSON-safe
def test_example_case_results_are_unchanged_and_json_safe():
    res = run_case(example_case())
    got = {m["risk_id"]: (m["p_class"], m["impact_class"], m["level"]) for m in res["matrix"]}
    assert got == {"R-MAT": (3, 5, "High"), "R-LAB": (2, 4, "Moderate"), "R-RWK": (2, 4, "Moderate"),
                   "R-WX": (2, 4, "Moderate"), "R-SAFE": (2, 4, "Moderate"), "R-SKILL": (2, 4, "Moderate"),
                   "R-PLAN": (1, 3, "Low")}
    json.dumps({k: v for k, v in res.items() if k != "report_markdown"}, allow_nan=False)
    assert deepcopy(example_case()) == example_case()
