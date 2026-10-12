import pytest

from app.engine.models import Source
from app.engine.rules import Cond, Rule, check_rule_base, evaluate_rules

SCHEMA = ["required_labour", "available_labour", "supplier_lead_time_days", "buffer_days", "monsoon_overlap"]

LABOUR = Rule("RL1", "Labour demand exceeds availability", "R-LAB", "elevated",
              all_of=(Cond("required_labour", "gt", other_fact="available_labour"),),
              source=Source.EXPERT, rationale="fewer masons than planned crews", confidence="Moderate", reviewer="tbd")
MAT = Rule("RM1", "Supplier lead time exceeds buffer", "R-MAT", "elevated",
           all_of=(Cond("supplier_lead_time_days", "gt", other_fact="buffer_days"),),
           source=Source.LITERATURE, evidence_ids=("M01",), confidence="Moderate")
RAIN = Rule("RW1", "Activity overlaps monsoon", "R-WX", "elevated", any_of=(Cond("monsoon_overlap", "eq", True),),
            source=Source.LITERATURE, evidence_ids=("R08",), confidence="Low")


def test_rules_fire_only_on_facts():
    out = evaluate_rules([LABOUR, MAT, RAIN], {"required_labour": 8, "available_labour": 6,
                                               "supplier_lead_time_days": 3, "buffer_days": 5, "monsoon_overlap": False})
    assert set(out["flags"]) == {"R-LAB"}
    assert out["flags"]["R-LAB"]["level"] == "elevated"
    assert out["fired"][0]["facts_used"] == {"required_labour": 8, "available_labour": 6}


def test_missing_facts_are_not_guessed():
    out = evaluate_rules([LABOUR, MAT], {"required_labour": 8})
    assert out["flags"] == {}
    ids = {x["rule_id"]: x["missing_facts"] for x in out["not_evaluable"]}
    assert ids["RL1"] == ["available_labour"] and "supplier_lead_time_days" in ids["RM1"]


def test_priority_and_conflict_resolution():
    hi = Rule("A", "d", "R1", "normal", all_of=(Cond("x", "gt", 0),), priority=2)
    lo = Rule("B", "d", "R1", "elevated", all_of=(Cond("x", "gt", 0),), priority=1)
    assert evaluate_rules([hi, lo], {"x": 1})["flags"]["R1"]["level"] == "normal"
    tie = Rule("C", "d", "R1", "elevated", all_of=(Cond("x", "gt", 0),), priority=2)
    out = evaluate_rules([hi, tie], {"x": 1})
    assert out["flags"]["R1"]["level"] == "conflict" and out["flags"]["R1"]["conflict"]


def test_consistency_checker():
    bad = [
        Rule("D1", "d", "R", "elevated", all_of=(Cond("nope", "gt", 1),)),
        Rule("D1", "d", "R", "elevated", all_of=(Cond("required_labour", "gt", 1),)),
        Rule("E1", "d", "R", "maybe", all_of=(Cond("required_labour", "??", 1),), confidence="Sure"),
        Rule("F1", "d", "R", "elevated", source=Source.LITERATURE, all_of=(Cond("required_labour", "gt", 1),)),
        Rule("G1", "d", "R", "normal", all_of=(Cond("required_labour", "gt", 5),)),
        Rule("G2", "d", "R", "elevated", all_of=(Cond("required_labour", "gt", 5),)),
        Rule("H1", "d", "R"),
    ]
    text = " | ".join(check_rule_base(bad, SCHEMA))
    for needle in ("duplicate rule id D1", "unknown fact 'nope'", "unknown level maybe", "confidence must be",
                   "no evidence ids", "contradictory levels", "no condition", "unknown operator ??"):
        assert needle in text, needle
    assert check_rule_base([LABOUR, MAT, RAIN], SCHEMA) == []


def test_unknown_operator_raises_at_evaluation():
    with pytest.raises(ValueError):
        evaluate_rules([Rule("X", "d", "R", all_of=(Cond("a", "??", 1),))], {"a": 1})
