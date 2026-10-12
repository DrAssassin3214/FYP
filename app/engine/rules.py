"""Deterministic rule engine: flags which risks are relevant/elevated for an activity.

Design constraints (from the evidence review):
  * A rule states a LOGICAL condition over user-supplied facts (e.g. required_labour > available_labour).
    It carries no numeric probability and no numeric threshold invented by the software; any threshold
    is a fact/value the user or a cited source supplies.
  * The output is a qualitative flag (risk relevant / elevated).  Probabilities still come from the
    user, experts or cited data, and are entered separately with their Source.
  * Every rule has an ID, source type, evidence IDs, rationale, confidence and reviewer, and the rule
    base is checked for consistency (contradictions, unknown facts) before use.
Missing facts never fire a rule; they are reported as 'not evaluable' instead of being guessed.
"""
from __future__ import annotations

import math
import numbers
import operator
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Sequence

from .models import Source

_OPS = {"lt": operator.lt, "le": operator.le, "gt": operator.gt, "ge": operator.ge,
        "eq": operator.eq, "ne": operator.ne, "in": lambda a, b: a in b}
CONFIDENCE = ("High", "Moderate", "Low", "Uncertain")


@dataclass(frozen=True)
class Cond:
    fact: str
    op: str
    value: Any = None            # literal to compare with ...
    other_fact: Optional[str] = None   # ... or another fact

    def facts(self) -> set[str]:
        return {self.fact} | ({self.other_fact} if self.other_fact else set())


@dataclass(frozen=True)
class Rule:
    rule_id: str
    description: str
    risk_id: str                         # risk in the risk library this rule concerns
    level: str = "elevated"              # 'elevated' | 'normal'
    all_of: tuple[Cond, ...] = ()
    any_of: tuple[Cond, ...] = ()
    priority: int = 0
    source: Source = Source.ASSUMPTION
    evidence_ids: tuple[str, ...] = ()
    rationale: str = ""
    confidence: str = "Uncertain"
    reviewer: str = ""

    def conditions(self) -> tuple[Cond, ...]:
        return self.all_of + self.any_of


_NUMERIC_OPS = {"lt", "le", "gt", "ge"}


def _kind(v: Any) -> str:
    """'bool' | 'number' (finite real, not bool) | 'str' | 'bad-number' (NaN/inf) | 'other'."""
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, numbers.Real):
        return "number" if math.isfinite(v) else "bad-number"
    if isinstance(v, str):
        return "str"
    return "other"


_KIND_TEXT = {"bool": "true/false", "number": "a finite number", "str": "text", "bad-number": "NaN/infinite",
              "other": "an unsupported type"}


def _eval_detail(c: Cond, facts: Mapping[str, Any]) -> tuple[Optional[bool], list[str], list[str]]:
    """(result, bad_fact_names, reasons).  result is None when the condition is not evaluable: a fact is
    missing, or a fact does not have the type the rule needs (numeric comparisons need real finite numbers,
    true/false rules need real booleans).  A string such as "10" or "yes" is never coerced or compared."""
    if c.op not in _OPS:
        raise ValueError(f"unknown operator {c.op}")
    bad: list[str] = []
    reasons: list[str] = []
    if c.fact not in facts or facts[c.fact] is None:
        bad.append(c.fact)
    if c.other_fact and (c.other_fact not in facts or facts[c.other_fact] is None):
        bad.append(c.other_fact)
    if bad:
        return None, bad, [f"fact '{f}' is missing" for f in bad]
    lhs = facts[c.fact]
    if c.other_fact:
        rhs, rhs_name = facts[c.other_fact], c.other_fact
    else:
        rhs, rhs_name = c.value, None
    if c.op == "in":
        if not isinstance(rhs, (list, tuple, set, frozenset)):
            return None, [], [f"rule '{c.op}' needs a list of allowed values"]
        try:
            return bool(lhs in rhs), [], []
        except TypeError:
            return None, [c.fact], [f"fact '{c.fact}' cannot be compared with the list of allowed values"]
    lk, rk = _kind(lhs), _kind(rhs)
    if rhs_name is None and rhs is None:
        return None, [], ["the rule has no value to compare with"]
    if c.op in _NUMERIC_OPS:
        need = "number"
    else:                                   # eq / ne: the fact must have the same type as what it is compared with
        need = rk if rk in ("bool", "number", "str") else None
    if need is None:
        if rk == "bad-number" and rhs_name is not None:
            bad.append(rhs_name)
        elif rk == "other" and rhs_name is not None:
            bad.append(rhs_name)
        if bad:
            return None, bad, [f"fact '{bad[0]}' is {_KIND_TEXT[rk]}, not usable in a comparison"]
        return bool(_OPS[c.op](lhs, rhs)), [], []
    if lk != need:
        bad.append(c.fact)
        reasons.append(f"fact '{c.fact}' is {_KIND_TEXT[lk]}, the rule needs {_KIND_TEXT[need]}")
    if rk != need:
        if rhs_name is not None:
            bad.append(rhs_name)
            reasons.append(f"fact '{rhs_name}' is {_KIND_TEXT[rk]}, the rule needs {_KIND_TEXT[need]}")
        else:
            reasons.append(f"the rule's comparison value is {_KIND_TEXT[rk]}, not {_KIND_TEXT[need]}")
    if reasons:
        return None, bad, reasons
    return bool(_OPS[c.op](lhs, rhs)), [], []


def _eval(c: Cond, facts: Mapping[str, Any]) -> Optional[bool]:
    """True/False, or None if a needed fact is missing or of the wrong type (not evaluable)."""
    return _eval_detail(c, facts)[0]


def check_rule_base(rules: Sequence[Rule], fact_schema: Sequence[str]) -> list[str]:
    """Consistency check: duplicate ids, unknown facts, unknown levels/confidence,
    identical conditions with contradictory levels, and equal-priority conflicts."""
    issues: list[str] = []
    ids = [r.rule_id for r in rules]
    for i in {x for x in ids if ids.count(x) > 1}:
        issues.append(f"duplicate rule id {i}")
    schema = set(fact_schema)
    for r in rules:
        if r.level not in ("elevated", "normal"):
            issues.append(f"{r.rule_id}: unknown level {r.level}")
        if r.confidence not in CONFIDENCE:
            issues.append(f"{r.rule_id}: confidence must be one of {CONFIDENCE}")
        if not r.all_of and not r.any_of:
            issues.append(f"{r.rule_id}: rule has no condition")
        if r.source in (Source.LITERATURE, Source.HISTORICAL) and not r.evidence_ids:
            issues.append(f"{r.rule_id}: source is {r.source.value} but no evidence ids")
        for c in r.conditions():
            if c.op not in _OPS:
                issues.append(f"{r.rule_id}: unknown operator {c.op}")
            for f in c.facts():
                if f not in schema:
                    issues.append(f"{r.rule_id}: unknown fact '{f}'")
    for a in rules:
        for b in rules:
            if a.rule_id < b.rule_id and a.risk_id == b.risk_id and a.level != b.level \
                    and (a.all_of, a.any_of) == (b.all_of, b.any_of):
                issues.append(f"{a.rule_id} and {b.rule_id}: identical conditions, contradictory levels")
    return issues


def evaluate_rules(rules: Sequence[Rule], facts: Mapping[str, Any]) -> dict:
    """Return per-risk flags with the rules and facts that produced them."""
    fired: list[dict] = []
    not_evaluable: list[dict] = []
    for r in rules:
        det = [_eval_detail(c, facts) for c in r.all_of + r.any_of]
        all_res = [d[0] for d in det[:len(r.all_of)]]
        any_res = [d[0] for d in det[len(r.all_of):]]
        missing = sorted({f for d in det if d[0] is None for f in d[1]})
        reasons = [x for d in det if d[0] is None for x in d[2]]
        ok_all = all(v is True for v in all_res)
        ok_any = (not r.any_of) or any(v is True for v in any_res)
        if ok_all and ok_any:
            fired.append({"rule_id": r.rule_id, "risk_id": r.risk_id, "level": r.level, "priority": r.priority,
                          "facts_used": {f: facts[f] for c in r.conditions() for f in c.facts() if f in facts},
                          "source": r.source.value, "evidence_ids": list(r.evidence_ids),
                          "confidence": r.confidence, "rationale": r.rationale})
        elif (missing or reasons) and not any(v is False for v in all_res):
            not_evaluable.append({"rule_id": r.rule_id, "missing_facts": missing, "reasons": reasons})

    flags: dict[str, dict] = {}
    for f in fired:
        cur = flags.setdefault(f["risk_id"], {"level": None, "rules": [], "conflict": False})
        cur["rules"].append(f["rule_id"])
    for rid, cur in flags.items():
        cands = [f for f in fired if f["risk_id"] == rid]
        top = max(c["priority"] for c in cands)
        winners = [c for c in cands if c["priority"] == top]
        levels = {w["level"] for w in winners}
        cur["level"] = winners[0]["level"] if len(levels) == 1 else "conflict"
        cur["conflict"] = len(levels) > 1
    return {"flags": flags, "fired": fired, "not_evaluable": not_evaluable,
            "note": "Flags identify relevant/elevated risks; probabilities are entered separately with a Source."}
