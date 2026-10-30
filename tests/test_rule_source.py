import copy
import json
from pathlib import Path

from app import service

ROOT = Path(__file__).resolve().parents[1]


def _first_rule():
    return copy.deepcopy(json.loads((ROOT / "data" / "rules_masonry.json").read_text(encoding="utf-8"))[0])


def test_bundled_rules_all_load_without_problems():
    rules = json.loads((ROOT / "data" / "rules_masonry.json").read_text(encoding="utf-8"))
    assert len(rules) == 22
    out = service.run_case(service.example_case())
    assert out["rule_base_issues"] == []


def test_unknown_rule_source_is_a_problem():
    rule = _first_rule()
    rule["source"] = "Typo"
    probs = []
    r = service._rule(rule, "rules[0]", probs)
    assert r is None
    assert any("Typo" in p and "rules[0]" in p and "Assumption" in p for p in probs)


def test_non_text_rule_source_is_a_problem():
    rule = _first_rule()
    rule["source"] = 7
    probs = []
    assert service._rule(rule, "rules[0]", probs) is None
    assert any("unknown source" in p for p in probs)


def test_missing_rule_source_still_defaults_to_assumption():
    rule = _first_rule()
    rule.pop("source")
    probs = []
    r = service._rule(rule, "rules[0]", probs)
    assert probs == [] and r is not None
    assert r.source.value == "Assumption"
