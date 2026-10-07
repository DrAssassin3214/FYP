"""Case-file service: the single entry point used by the GUI and the command line.

    result = run_case(case_dict)     # risk register + rule flags + risk matrix, computed instantly

This tool covers three things: identifying risks (curated library, site-fact rules, guarded AI
suggestions over a cited evidence corpus), keeping the risk register, and placing the register on a
probability x impact matrix. A case is a plain dict / JSON file (schema in docs/case_schema.md).

Nothing in here invents a number: every numeric input carries a Source, values that are present but
wrong are rejected with a message, and a risk whose probability or delay is simply not entered yet is
kept in the register but left off the matrix, with a note saying what is missing.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping, Optional

from app.engine.audit import to_jsonable
from app.engine.matrix import DEFAULT_LABELS, DEFAULT_P_EDGES, classify, matrix_level
from app.reporting.matrix_graphic import matrix_svg
from app.literature_seed import seed_for, seed_table
from app.engine.models import DelayDist, Param, Risk, RiskStatus, Source
from app.engine.rules import _OPS, Cond, Rule, check_rule_base, evaluate_rules
from app.reporting.register_report import generate_register_report, register_csv

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [s.value for s in Source]
_SRC = {s.value: s for s in Source}
LEVELS = ("Extreme", "High", "Moderate", "Low")


class CaseError(ValueError):
    """Raised with a list of human-readable problems."""

    def __init__(self, problems: list[str]):
        super().__init__("; ".join(problems))
        self.problems = problems


# ----------------------------------------------------------------------------------- parsing helpers
_KINDS = ("pert", "triangular", "uniform", "fixed")
_REQUIRED = {"fixed": ("m",), "uniform": ("a", "b"), "pert": ("a", "m", "b"), "triangular": ("a", "m", "b")}


def _blank(v: Any) -> bool:
    return v is None or (isinstance(v, str) and v == "")


def _num(v: Any, where: str, problems: list[str]) -> Optional[float]:
    """A real, finite number (numeric strings such as "0.5" are accepted, as before).  Booleans, NaN and
    infinity are rejected with a message instead of being coerced."""
    if isinstance(v, bool):
        problems.append(f"{where} must be a number, not {'true' if v else 'false'}")
        return None
    try:
        x = float(v)
    except (TypeError, ValueError):
        problems.append(f"{where}: value '{v}' is not a number")
        return None
    if not math.isfinite(x):
        problems.append(f"{where} must be a finite number")
        return None
    return x


def _text(v: Any, where: str, problems: list[str]) -> str:
    if v is None:
        return ""
    if not isinstance(v, str):
        problems.append(f"{where} must be text, not {type(v).__name__}")
        return ""
    return v


def _ids(v: Any, where: str, problems: list[str]) -> tuple:
    """evidence_ids: a list of strings (a bare string like "M01" is rejected, not split into characters)."""
    if v is None:
        return ()
    if not isinstance(v, (list, tuple)):
        problems.append(f"{where} must be a list of evidence id strings")
        return ()
    if not all(isinstance(x, str) for x in v):
        problems.append(f"{where} must contain only strings")
        return ()
    return tuple(v)


def _source(src: Any, where: str, problems: list[str]) -> Optional[Source]:
    if src is None:
        problems.append(f"{where}: source is required (one of {SOURCES})")
        return None
    if not isinstance(src, str) or src not in _SRC:
        problems.append(f"{where}: unknown source '{src}' (use one of {SOURCES})")
        return None
    return _SRC[src]


def _param(d: Any, where: str, problems: list[str], default_source: Optional[Source] = None) -> Optional[Param]:
    if d is None:
        return None
    if not isinstance(d, Mapping):
        problems.append(f"{where}: expected an object with value and source")
        return None
    if d.get("value") is None:
        problems.append(f"{where}: value is missing")
        return None
    src = d.get("source")
    if src is None and default_source is not None:
        source = default_source
    else:
        source = _source(src, where, problems)
        if source is None:
            return None
    v = _num(d["value"], f"{where}.value", problems)
    ev = _ids(d.get("evidence_ids"), f"{where}.evidence_ids", problems)
    note = _text(d.get("note", ""), f"{where}.note", problems)
    if v is None:
        return None
    return Param(v, source, ev, note)


def _dist_kind(d: Mapping, where: str, problems: list[str]) -> Optional[str]:
    kind = d.get("kind")
    kind = "pert" if _blank(kind) else kind
    if not isinstance(kind, str) or kind not in _KINDS:
        problems.append(f"{where}: unknown distribution kind '{kind}' (use one of {list(_KINDS)})")
        return None
    return kind


def _dist(d: Any, where: str, problems: list[str]) -> Optional[DelayDist]:
    """A COMPLETE delay distribution.  Its source is required, exactly like p and the planned duration:
    a number without a Source is a problem, never silently labelled."""
    if not isinstance(d, Mapping):
        problems.append(f"{where}: delay distribution missing")
        return None
    n0 = len(problems)
    kind = _dist_kind(d, where, problems)
    src = _source(d.get("source"), where, problems)
    if kind is None:
        return None
    values: dict[str, float] = {}
    for k in _REQUIRED[kind]:
        v = d.get(k)
        if _blank(v):
            problems.append(f"{where}.{k}: value missing")
            continue
        x = _num(v, f"{where}.{k}", problems)
        if x is not None:
            values[k] = x
    lam = 4.0
    if not _blank(d.get("lam")):
        x = _num(d["lam"], f"{where}.lam", problems)
        lam = 4.0 if x is None else x
    ev = _ids(d.get("evidence_ids"), f"{where}.evidence_ids", problems)
    if len(problems) > n0 or src is None:
        return None
    if kind == "uniform":
        values["m"] = (values["a"] + values["b"]) / 2          # unused by the uniform; shown only as the midpoint
    try:
        dd = DelayDist(kind, values.get("a", 0.0), values["m"], values.get("b", 0.0), lam, src, ev)
        dd.validate()
    except (TypeError, ValueError) as e:
        problems.append(f"{where}: {e}")
        return None
    return dd


def _risk(d: Mapping, where: str, problems: list[str], warnings: list[str],
          partial: Optional[dict] = None) -> Optional[Risk]:
    """A risk is built only when its probability AND delay are both entered.  Missing numbers are
    reported as a note (the risk stays in the register, off the matrix unless the literature seed places it);
    wrong numbers are problems EVEN when the other number is missing.  The p that was entered is kept in
    `partial[risk_id]` so the register can still show it."""
    n0 = len(problems)
    rid = d.get("id")
    if _blank(rid) or isinstance(rid, bool) or not isinstance(rid, (str, int)):
        problems.append(f"{where}: id is required" if _blank(rid) else f"{where}: id must be text")
        return None
    for k in ("name", "category", "description"):
        _text(d.get(k), f"{where}.{k}", problems)
    ev = _ids(d.get("evidence_ids"), f"{where}.evidence_ids", problems)
    st = d.get("status")
    st = RiskStatus.EXPERT_USER.value if _blank(st) else st
    status = None
    try:
        status = RiskStatus(st)
    except (ValueError, TypeError):
        problems.append(f"{where}: unknown status '{st}'")

    missing = []
    pd = d.get("p")
    p = None
    if _blank(pd):
        missing.append("probability")
    elif not isinstance(pd, Mapping):
        problems.append(f"{where}.p: expected an object with value and source (got {type(pd).__name__} '{pd}')")
    elif _blank(pd.get("value")):
        missing.append("probability")
    else:
        p = _param(pd, f"{where}.p", problems)
        if p is not None and not (0.0 <= p.value <= 1.0):
            problems.append(f"{where}: {rid}: probability must be in [0,1]")
            p = None

    dd = d.get("delay")
    delay = None
    if _blank(dd):
        missing.append("delay range")
    elif not isinstance(dd, Mapping):
        problems.append(f"{where}.delay: expected an object with kind, min/most likely/max and source "
                        f"(got {type(dd).__name__} '{dd}')")
    else:
        kind = _dist_kind(dd, f"{where}.delay", problems)
        if kind is not None:
            needed = _REQUIRED[kind]
            if any(_blank(dd.get(k)) for k in needed):
                missing.append("delay range")
                for k in needed:                      # what WAS entered must still be a valid number
                    if not _blank(dd.get(k)):
                        _num(dd[k], f"{where}.delay.{k}", problems)
            else:
                delay = _dist(dd, f"{where}.delay", problems)

    if missing and len(problems) == n0:
        warnings.append(f"{rid}: not on the matrix yet, {' and '.join(missing)} not entered")
    if missing:
        if partial is not None:
            partial[str(rid)] = {"p": p, "missing": missing}
        return None
    if len(problems) > n0 or p is None or delay is None or status is None:
        return None
    r = Risk(str(rid), d.get("name") or str(rid), p, delay, d.get("category") or "", d.get("description") or "",
             status, evidence_ids=ev)
    try:
        r.validate()
    except ValueError as e:
        problems.append(f"{where}: {e}")
        return None
    return r


def _rule(d: Any, where: str, problems: list[str]) -> Optional[Rule]:
    if not isinstance(d, Mapping):
        problems.append(f"{where}: malformed rule (expected an object)")
        return None
    n0 = len(problems)

    def conds(key):
        lst = d.get(key)
        if lst is None:
            return ()
        if not isinstance(lst, (list, tuple)):
            problems.append(f"{where}.{key} must be a list of conditions")
            return ()
        out = []
        for j, c in enumerate(lst):
            w = f"{where}.{key}[{j}]"
            if not isinstance(c, Mapping):
                problems.append(f"{w}: expected an object with fact, op and value/other_fact")
                continue
            fact, op, other = c.get("fact"), c.get("op"), c.get("other_fact")
            if not isinstance(fact, str) or not fact:
                problems.append(f"{w}: fact is required and must be text")
            if not isinstance(op, str) or op not in _OPS:
                problems.append(f"{w}: unknown operator '{op}' (use one of {sorted(_OPS)})")
            if other is not None and not isinstance(other, str):
                problems.append(f"{w}: other_fact must be text")
            out.append(Cond(fact, op, c.get("value"), other))
        return tuple(out)

    rid, risk_id = d.get("id"), d.get("risk_id")
    for k, v in (("id", rid), ("risk_id", risk_id)):
        if not isinstance(v, str) or not v:
            problems.append(f"{where}: malformed rule ({k} is required and must be text)")
    all_of, any_of = conds("all_of"), conds("any_of")
    prio = d.get("priority", 0)
    prio = 0 if prio is None else prio
    pr = _num(prio, f"{where}.priority", problems)
    if pr is not None and pr != int(pr):
        problems.append(f"{where}.priority must be a whole number")
        pr = None
    ev = _ids(d.get("evidence_ids"), f"{where}.evidence_ids", problems)
    texts = [_text(d.get(k, ""), f"{where}.{k}", problems) for k in ("description", "rationale", "reviewer")]
    conf = d.get("confidence", "Uncertain")
    level = d.get("level", "elevated")
    if not isinstance(conf, str) or not isinstance(level, str):
        problems.append(f"{where}: level and confidence must be text")
    src = d.get("source", "Assumption")
    if len(problems) > n0:
        return None
    return Rule(rid, texts[0], risk_id, level, all_of, any_of, int(pr),
                _SRC.get(src, Source.ASSUMPTION) if isinstance(src, str) else Source.ASSUMPTION, ev,
                texts[1], conf, texts[2])


def load_json(name: str):
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8-sig"))


def risk_library() -> list[dict]:
    """Candidate risks for brick masonry with the evidence that supports their EXISTENCE.
    No probabilities or delay sizes: those are entered per case."""
    return load_json("risk_library_masonry.json")


def rule_library() -> list[dict]:
    return load_json("rules_masonry.json")


# ----------------------------------------------------------------------------------- templates
def template_case() -> dict:
    """Blank case."""
    return {
        "project": {"name": "", "location": "", "construction_type": "", "notes": ""},
        "activity": {"id": "MAS-01", "name": "Brick masonry",
                     "planned_duration_days": {"value": None, "source": "User Input"}},
        "facts": {},
        "risks": [],
        "impact_bin_edges_fraction": None,
    }


def example_case() -> dict:
    """ILLUSTRATIVE case: every number is a placeholder so the tool can be exercised end to end.
    It is NOT evidence and NOT Indian site data."""
    A = "Assumption"
    note = "ILLUSTRATIVE placeholder, not evidence"

    def risk(rid, name, cat, p, a, m, b, ev):
        return {"id": rid, "name": name, "category": cat, "status": "literature-supported", "evidence_ids": ev,
                "p": {"value": p, "source": A, "note": note},
                "delay": {"kind": "pert", "a": a, "m": m, "b": b, "source": A}}

    return {
        "project": {"name": "ILLUSTRATIVE example", "location": "n/a", "construction_type": "Residential building",
                    "notes": "Demonstration only. Every probability, delay and the planned duration is a placeholder "
                             "labelled Assumption, not site data and not evidence. The evidence IDs (M01, M02, ...) "
                             "point to real literature records supporting that each risk exists, not its size. "
                             "Its site facts cover every input of the bundled rules, so the rule engine flags the "
                             "risks that are in the register and nothing is left over. Replace all numbers with "
                             "your own before drawing any conclusion."},
        "activity": {"id": "MAS-01", "name": "Brick masonry, ground-floor walls",
                     "planned_duration_days": {"value": 16, "source": A, "note": note}},
        "facts": {"required_workers": 6, "available_workers": 5, "material_lead_time_days": 6,
                  "material_buffer_days": 3, "material_stock_days": 2, "tools_shortage": False,
                  "monsoon_overlap": True, "work_at_height": True, "payment_delay_expected": False,
                  "design_incomplete": False, "prior_rework_history": True, "schedule_compressed": True,
                  "skilled_masons_short": True},
        "risks": [risk("R-MAT", "Brick / material shortage", "Material", 0.50, 1, 3, 8, ["M01", "M06"]),
                  risk("R-LAB", "Labour absenteeism / shortage", "Labour", 0.35, 1, 2, 6, ["M01", "M07", "M15"]),
                  risk("R-RWK", "Rework due to workmanship", "Quality", 0.25, 1, 2, 5, ["M03", "M15"]),
                  risk("R-WX", "Rain / monsoon stoppage", "Weather", 0.20, 1, 2, 7, ["R08"]),
                  risk("R-PLAN", "Poor planning or unrealistic scheduling", "Management", 0.10, 1, 1, 3, ["M01"]),
                  risk("R-SAFE", "Unsafe conditions / work at height", "Safety", 0.30, 1, 2, 6, ["M01"]),
                  risk("R-SKILL", "Unskilled or unqualified labour", "Labour", 0.22, 1, 2, 5, ["M15", "M14"])],
        "impact_bin_edges_fraction": [0.02, 0.05, 0.10, 0.20],
    }


# ----------------------------------------------------------------------------------- parsing
def _known_fact_names() -> set:
    """The fact vocabulary of the bundled rule base, plus the planned duration (taken from the activity)."""
    names = {"planned_duration_days"}
    for r in rule_library():
        for k in ("all_of", "any_of"):
            for c in r.get(k) or ():
                names.add(c["fact"])
                if c.get("other_fact"):
                    names.add(c["other_fact"])
    return names


def parse_case(case: Mapping) -> dict:
    problems: list[str] = []
    warnings: list[str] = []
    if not isinstance(case, Mapping):
        raise CaseError(["the case must be a JSON object"])

    def section(key: str, what: str) -> Mapping:
        v = case.get(key)
        if v is None:
            return {}
        if not isinstance(v, Mapping):
            problems.append(f"{key}: expected an object ({what}), got {type(v).__name__}")
            return {}
        return v

    project = section("project", "name, location, ...")
    for k in ("name", "location", "construction_type", "notes"):
        _text(project.get(k), f"project.{k}", problems)
    a = section("activity", "id, name, planned_duration_days")
    _text(a.get("id"), "activity.id", problems)
    _text(a.get("name"), "activity.name", problems)
    facts_in = section("facts", "fact name -> value")

    planned = None
    pd = a.get("planned_duration_days")
    if isinstance(pd, Mapping) and not _blank(pd.get("value")):
        planned = _param(pd, "activity.planned_duration_days", problems)
        if planned is not None and planned.value <= 0:
            problems.append("activity.planned_duration_days must be greater than 0")
            planned = None
    elif pd is not None and not isinstance(pd, Mapping):
        problems.append("activity.planned_duration_days: expected an object with value and source")
    if planned is None and not problems:
        warnings.append("risk matrix not computed: the planned activity duration is not entered "
                        "(impact is measured as a fraction of it)")

    risks: list[Risk] = []
    partial: dict[str, dict] = {}
    risks_in = case.get("risks")
    if risks_in is None:
        risks_in = []
    elif not isinstance(risks_in, (list, tuple)):
        problems.append(f"risks: expected a list of risk objects, got {type(risks_in).__name__}")
        risks_in = []
    raw = []
    seen: set[str] = set()
    for i, r in enumerate(risks_in):
        if not isinstance(r, Mapping):
            problems.append(f"risks[{i}]: expected an object, got {type(r).__name__}")
            continue
        raw.append(r)
        if not _blank(r.get("id")) and str(r["id"]) in seen:
            problems.append(f"risks[{i}]: duplicate id '{r['id']}'")
            continue
        if not _blank(r.get("id")):
            seen.add(str(r["id"]))
        rr = _risk(r, f"risks[{i}]", problems, warnings, partial)
        if rr:
            risks.append(rr)

    edges = case.get("impact_bin_edges_fraction")
    if edges is not None:
        msg = "impact_bin_edges_fraction must be a list of exactly four numbers"
        if not isinstance(edges, (list, tuple)) or len(edges) != 4:
            problems.append(msg)
            edges = None
        else:
            n0 = len(problems)
            vals = [_num(x, f"impact_bin_edges_fraction[{j}]", problems) for j, x in enumerate(edges)]
            if len(problems) > n0:
                edges = None
            else:
                edges = vals
                if any(b <= a_ for a_, b in zip(edges, edges[1:])) or any(not (0 < x < 1) for x in edges):
                    problems.append("impact_bin_edges_fraction must be strictly ascending, unique values between 0 and 1")
                    edges = None

    use_seed = case.get("use_literature_seed")
    if use_seed is None:
        use_seed = True
    elif not isinstance(use_seed, bool):
        problems.append(f"use_literature_seed must be true or false, not {use_seed!r}")
        use_seed = True
    seed_basis = case.get("seed_basis")
    if not _blank(seed_basis) and seed_basis not in ("seed", "all"):
        problems.append("seed_basis must be 'seed' or 'all'")
    seed_basis = seed_basis if seed_basis in ("seed", "all") else "seed"

    facts = dict(facts_in)
    if planned is not None and "planned_duration_days" in facts:
        fv = facts["planned_duration_days"]
        ok = not isinstance(fv, bool) and isinstance(fv, (int, float)) and math.isfinite(fv) \
            and math.isclose(fv, planned.value, rel_tol=1e-9)
        if not ok:
            problems.append(f"facts.planned_duration_days ({fv!r}) conflicts with activity.planned_duration_days "
                            f"({planned.value:g}); remove it from facts, the activity's planned duration is used")
    if planned is not None:
        facts["planned_duration_days"] = planned.value        # the activity's value always wins

    rules_raw = case.get("rules")
    rules_raw = rule_library() if rules_raw is None else rules_raw
    rules: list[Rule] = []
    if not isinstance(rules_raw, (list, tuple)):
        problems.append(f"rules: expected a list of rule objects, got {type(rules_raw).__name__}")
    else:
        rules = [x for x in (_rule(r, f"rules[{i}]", problems) for i, r in enumerate(rules_raw)) if x]
    if problems:
        raise CaseError(problems)
    return {"project": dict(project), "activity": {"id": str(a.get("id") or "ACT"), "name": a.get("name") or ""},
            "planned": planned, "raw_risks": raw, "risks": risks, "rules": rules, "facts": facts,
            "impact_edges": edges, "warnings": warnings, "partial": partial, "use_seed": use_seed,
            "seed_basis": seed_basis}


# ----------------------------------------------------------------------------------- running
def _param_row(p: Optional[Param]) -> Optional[dict]:
    if p is None:
        return None
    return {"value": p.value, "source": p.source.value, "note": p.note}


def run_case(case: Mapping, evidence_index: Optional[Mapping[str, str]] = None) -> dict:
    """Parse the case and return the register, rule flags and matrix. Instant: nothing is simulated."""
    pc = parse_case(case)
    warnings = list(pc["warnings"])
    planned, risks, edges = pc["planned"], pc["risks"], pc["impact_edges"]

    used_facts = {f for r in pc["rules"] for c in r.conditions() for f in c.facts()}
    known_facts = _known_fact_names()
    problems = check_rule_base(pc["rules"], sorted(known_facts | set(pc["facts"])))
    for f in sorted(set(pc["facts"]) - known_facts - used_facts):
        warnings.append(f"unknown fact '{f}': no rule uses it (check the spelling)")
    if evidence_index:
        unknown_ev: list[str] = []
        for r in pc["raw_risks"]:
            for blk in (r, r.get("p"), r.get("delay")):
                if isinstance(blk, Mapping):
                    for e in blk.get("evidence_ids") or ():
                        if e not in evidence_index and e not in unknown_ev:
                            unknown_ev.append(e)
        for e in unknown_ev:
            warnings.append(f"unknown evidence id '{e}': not found in the evidence store")
    rule_out = evaluate_rules(pc["rules"], pc["facts"])
    in_register = {str(r["id"]) for r in pc["raw_risks"] if not _blank(r.get("id"))}
    flagged_missing = [rid for rid, fl in rule_out["flags"].items() if fl["level"] == "elevated" and rid not in in_register]
    for rid in flagged_missing:
        by = ", ".join(rule_out["flags"][rid]["rules"])
        warnings.append(f"rule(s) {by} flag risk '{rid}' as elevated, but it is not in the risk register")

    matrix: list[dict] = []
    if planned is not None and edges and risks:
        matrix = classify(risks, planned.value, edges)
    elif planned is not None and not edges:
        warnings.append("risk matrix not computed: impact bin edges are not defined (USER INPUT REQUIRED)")
    built = {r.risk_id: r for r in risks}

    # literature seed: risks whose numbers are not entered get a class-only placement from survey RII rankings
    seeds: dict[str, dict] = {}
    if pc["use_seed"]:
        for r in pc["raw_risks"]:
            rid = None if _blank(r.get("id")) else str(r["id"])
            if rid is None or rid in built:
                continue
            fl = rule_out["flags"].get(rid)
            sd = seed_for(rid, elevated=bool(fl and fl["level"] == "elevated"), basis=pc["seed_basis"])
            if sd:
                seeds[rid] = sd
                score = sd["p_class"] * sd["impact_class"]
                part = pc["partial"].get(rid) or {}
                note = ("starting placement from survey RII rank; ordinal only. Literature seed used because the "
                        f"numbers are incomplete ({' and '.join(part.get('missing') or ['numbers'])} not entered)")
                if part.get("p") is not None:
                    note += (f"; the entered p = {part['p'].value:g} is kept in the register but not used for "
                             "placement until the delay range is entered")
                matrix.append({"risk_id": rid, "p": None, "expected_delay_if_occurs_days": None,
                               "p_class": sd["p_class"], "impact_class": sd["impact_class"], "score": score,
                               "level": matrix_level(sd["p_class"], sd["impact_class"]), "basis": "literature-seed",
                               "note": note})
        if seeds:
            warnings[:] = [w for w in warnings if not any(w.startswith(f"{rid}: not on the matrix yet") for rid in seeds)]
            for rid, sd in seeds.items():
                warnings.append(f"{rid}: placed on the matrix from the literature seed (survey RII rank {sd['rank']} of "
                                f"{sd['n_seeded']}); enter probability and delay to replace it")
    by_mx = {m["risk_id"]: m for m in matrix}

    rows = []
    for r in pc["raw_risks"]:
        rid = None if _blank(r.get("id")) else str(r["id"])
        b = built.get(rid)
        fl = rule_out["flags"].get(rid)
        rows.append({
            "id": rid, "name": r.get("name") or rid, "category": r.get("category", ""),
            "description": r.get("description", ""), "status": r.get("status", RiskStatus.EXPERT_USER.value),
            "evidence_ids": list(r.get("evidence_ids") or []),
            "p": _param_row(b.p) if b else _param_row((pc["partial"].get(rid) or {}).get("p")),
            "delay": ({"kind": b.delay.kind, "a": b.delay.a, "m": b.delay.m, "b": b.delay.b, "lam": b.delay.lam,
                       "source": b.delay.source.value, "mean": b.delay.mean()} if b else None),
            "complete": b is not None,
            "seed": seeds.get(rid),
            "flag": {"level": fl["level"], "rules": fl["rules"]} if fl else None,
        })

    levels = {k: sum(1 for m in matrix if m["level"] == k) for k in LEVELS}
    n_flagged = sum(1 for fl in rule_out["flags"].values() if fl["level"] == "elevated")
    result = {
        "ok": True,
        "project": pc["project"],
        "activity": {"id": pc["activity"]["id"], "name": pc["activity"]["name"],
                     "planned_duration_days": _param_row(planned)},
        "risks": rows,
        "matrix": matrix,
        "summary": {"n_risks": len(rows), "n_complete": len(risks), "n_incomplete": len(rows) - len(risks),
                    "n_on_matrix": len(matrix), "n_seeded": len(seeds), "levels": levels, "n_flagged": n_flagged,
                    "n_flagged_missing": len(flagged_missing)},
        "rules": rule_out,
        "rule_base_issues": problems,
        "warnings": warnings,
    }
    result = to_jsonable(result)
    result["report_markdown"] = generate_register_report(result, evidence_index)
    result["matrix_svg"] = matrix_svg(result)
    return result


def run_case_file(path: str | Path, out_dir: Optional[str | Path] = None, evidence_index=None) -> dict:
    case = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    res = run_case(case, evidence_index)
    if out_dir:
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "register.md").write_text(res["report_markdown"], encoding="utf-8")
        (out / "register.csv").write_text(register_csv(res), encoding="utf-8-sig")
        (out / "result.json").write_text(json.dumps({k: v for k, v in res.items() if k != "report_markdown"}, indent=2), encoding="utf-8")
    return res


# ----------------------------------------------------------------------------------- evidence + AI
_FULL_STORE_CACHE: Optional[tuple] = None


def _store(workbook: Optional[Path] = None):
    """The evidence store used for retrieval and citation checking.  With an explicit `workbook`
    path this loads ONLY that workbook (used by tests that want a small, isolated store).  With no
    argument it returns the FULL corpus -- the curated workbook plus every research-notes file, the
    P1-P3 JSON extracts and the bulk literature harvest under the project root
    (app.ai_layer.corpus.build_full_store) -- built once and cached for the process."""
    from app.ai_layer.evidence import EvidenceStore

    if workbook is not None:
        p = Path(workbook)
        return EvidenceStore.from_workbook(p) if p.exists() else EvidenceStore()
    global _FULL_STORE_CACHE
    if _FULL_STORE_CACHE is None:
        from app.ai_layer.corpus import build_full_store

        _FULL_STORE_CACHE = build_full_store(ROOT)
    return _FULL_STORE_CACHE[0]


def evidence_corpus_report() -> dict:
    """What the full evidence store was built from, and how large it is."""
    _store()
    return {"total_records": len(_FULL_STORE_CACHE[0]), "sources": _FULL_STORE_CACHE[1]}


def evidence_lookup(ids: Optional[list] = None, query: Optional[str] = None, k: int = 20,
                    workbook: Optional[Path] = None) -> list[dict]:
    """Read-only access to the evidence store: by explicit id list, by a search query, or (with
    neither) the whole store."""
    store = _store(workbook)
    if ids:
        recs = [store.get(i) for i in ids]
        recs = [r for r in recs if r is not None]
    elif query:
        recs = store.retrieve(query, k)
    else:
        recs = store.all()
    return [{"id": r.evidence_id, "citation": r.citation, "doi": r.doi, "context": r.context,
             "evidence_depth": r.evidence_depth} for r in recs]


MATRIX_LEVEL_LABELS = ("Low", "Moderate", "High", "Extreme")   # order used by app.engine.matrix.matrix_level
MATRIX_SCORE_THRESHOLDS = (5, 10, 15)                          # matches the default in app.engine.matrix.matrix_level


def matrix_legend() -> dict:
    """The ordinal risk-matrix labelling scheme (classify() in app.engine.matrix)."""
    return {"probability_class_labels": list(DEFAULT_LABELS), "probability_bin_edges": list(DEFAULT_P_EDGES),
            "level_labels": list(MATRIX_LEVEL_LABELS), "level_score_thresholds": list(MATRIX_SCORE_THRESHOLDS),
            "note": "Ordinal prioritisation only; the matrix level is a label, not a quantity."}


def suggest_risks(activity_name: str, query: str, client=None, workbook: Optional[Path] = None, k: int = 6) -> dict:
    """AI-assisted risk identification.  With an LLM client: guarded candidates (unverified, no numbers,
    citations checked).  Without one: retrieval-only suggestions from the curated library and evidence store."""
    from app.ai_layer.guard import generate_candidates

    store = _store(workbook)
    if client is not None:
        out = generate_candidates(client, activity_name, query, store, k)
        return to_jsonable({"mode": "llm", "candidates": out["candidates"], "audit": out["audit"]})
    hits = store.retrieve(query, k)
    q = set(query.lower().split())
    lib = [r for r in risk_library() if q & set((r["name"] + " " + r["description"] + " " + r["category"]).lower().split())]
    return to_jsonable({"mode": "offline-retrieval",
                        "note": "No LLM configured (add a key in Settings). Showing curated library risks and evidence records that match the query; nothing here is a numeric estimate.",
                        "library_risks": lib, "evidence": [{"id": h.evidence_id, "citation": h.citation, "context": h.context} for h in hits]})


def evidence_index_from_workbook(path: Optional[Path] = None) -> dict[str, str]:
    """Citation text for every evidence id, for the report's 'Evidence cited' section.  With no path
    this draws on the FULL corpus; an explicit path restricts it to that one workbook."""
    if path is not None:
        from app.ai_layer.evidence import EvidenceStore

        p = Path(path)
        s = EvidenceStore.from_workbook(p) if p.exists() else EvidenceStore()
    else:
        s = _store()
    return {r.evidence_id: r.citation for r in s.all()}

