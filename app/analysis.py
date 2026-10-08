"""Quantitative analysis of a case: Monte Carlo schedule risk, cost / EMV, response options and the decision.

    result = run_analysis(case_dict)

This is the second half of the case flow.  run_case() (app/service.py) identifies risks and builds the register and
the matrix instantly.  run_analysis() takes the SAME case, plus a cost model and (optionally) mitigations, and
returns:

    summary / cost / event_emv / sensitivity / convergence    the simulated schedule and its money value
    value_at_stake                                            money at stake per risk = ceiling on any response
    option_suggestions                                        where to look, candidate actions, what must be elicited
    mitigation_checks                                         per-response net benefit and break-even targets
    decision / command                                        options compared on the same random draws, and the
                                                              AUTHORIZE MITIGATION / ACCEPT RISK / ... command
    decision_stability / decision_sensitivity                 does the choice survive a new seed / a different cost per day
    assumptions / audit                                       every non-literature input, and an input hash

Case additions to docs/case_schema.md (all numbers are {"value", "source", ...} objects, working days):

    activity.deadline_days      optional {value, source}; needed for liquidated damages and deadline criteria
    risks[].direct_cost_if_occurs   optional {value, source}; cost incurred if the risk occurs, besides delay cost
    cost                        {cost_per_delay_day (required), ld_per_day_after_deadline (optional), currency}
    mitigations[]               {id, risk_id, action, strategy, cost (required), p_after and/or delay_after,
                                 secondary_risks[], feasible, infeasible_reason, time_to_implement_days,
                                 evidence_ids, mechanism, catalogue_id}
    options[]                   optional {id, label, mitigation_ids[]}; blank = generated from the mitigations
    constraints                 {max_p_exceed_deadline, max_mitigation_budget}, both optional, no defaults
    simulation                  {n, seed, criterion, correlation[{a, b, rho}]}

Integrity: nothing here supplies an effect size, probability, delay or cost.  A response with no modelled effect is
reported and left out, never given a made-up one.  The command says "preferred under the stated criterion among the
options evaluated", never "optimal".
"""
from __future__ import annotations

from dataclasses import replace
from typing import Any, Mapping, Optional

from app import service
from app.engine.audit import assumption_register, build_record, to_jsonable
from app.engine.decision import CRITERIA, Constraints, Option, compare_options
from app.engine.emv import cost_summary, event_emv
from app.engine.models import Activity, CostModel, Mitigation, Param, Risk, Source
from app.engine.options import (build_options, break_even_targets, decision_command, decision_sensitivity,
                                 mitigation_net_benefit, selection_stability, suggest_options, value_at_stake)
from app.engine.simulation import convergence, sensitivity, simulate, summarise

CaseError = service.CaseError
STRATEGIES = ("avoid", "mitigate", "transfer", "accept", "monitor")
DEFAULT_N = 10_000
MAX_N = 200_000
DEFAULT_SEED = 12345
_blank = service._blank
_param = service._param
_dist = service._dist


# ----------------------------------------------------------------------------------------------- parsing
def _int_setting(sim: Mapping, key: str, default: int, lo: int, hi: int, problems: list[str]) -> int:
    v = sim.get(key)
    if _blank(v):
        return default
    if isinstance(v, bool):
        problems.append(f"simulation.{key}: expected a whole number")
        return default
    try:
        f = float(v)
    except (TypeError, ValueError):
        problems.append(f"simulation.{key}: '{v}' is not a number")
        return default
    if f != int(f) or not (lo <= f <= hi):
        problems.append(f"simulation.{key}: must be a whole number from {lo} to {hi}")
        return default
    return int(f)


def _opt_number(d: Mapping, key: str, where: str, problems: list[str], lo: float, hi: Optional[float] = None) -> Optional[float]:
    v = d.get(key)
    if _blank(v):
        return None
    if isinstance(v, bool):
        problems.append(f"{where}.{key}: expected a number")
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        problems.append(f"{where}.{key}: '{v}' is not a number")
        return None
    if f < lo or (hi is not None and f > hi):
        problems.append(f"{where}.{key}: must be {'between ' + str(lo) + ' and ' + str(hi) if hi is not None else 'at least ' + str(lo)}")
        return None
    return f


def _mitigation(d: Mapping, where: str, problems: list[str], risk_ids: set[str]) -> Optional[Mitigation]:
    mid = d.get("id")
    if _blank(mid):
        problems.append(f"{where}: id is required")
        return None
    mid = str(mid)
    n0 = len(problems)
    rid = d.get("risk_id")
    if _blank(rid) or str(rid) not in risk_ids:
        problems.append(f"{where} ({mid}): target risk '{rid}' is not a complete risk in the register")
    strategy = d.get("strategy") or "mitigate"
    if strategy not in STRATEGIES:
        problems.append(f"{where} ({mid}): unknown strategy '{strategy}' (use one of {list(STRATEGIES)})")

    cost = None
    cd = d.get("cost")
    if not isinstance(cd, Mapping) or _blank(cd.get("value")):
        problems.append(f"{where} ({mid}).cost: input required (cost of carrying out the response, with a source)")
    else:
        cost = _param(cd, f"{where} ({mid}).cost", problems)

    p_after = None
    pa = d.get("p_after")
    if isinstance(pa, Mapping) and not _blank(pa.get("value")):
        p_after = _param(pa, f"{where} ({mid}).p_after", problems)
        if p_after is not None and not (0.0 <= p_after.value <= 1.0):
            problems.append(f"{where} ({mid}).p_after: probability must be between 0 and 1")
    delay_after = None
    da = d.get("delay_after")
    if isinstance(da, Mapping) and any(not _blank(da.get(k)) for k in ("a", "m", "b")):
        delay_after = _dist(da, f"{where} ({mid}).delay_after", problems)

    secondary: list[Risk] = []
    for j, s in enumerate(d.get("secondary_risks") or []):
        if not isinstance(s, Mapping):
            problems.append(f"{where} ({mid}).secondary_risks[{j}]: expected an object")
            continue
        sw = f"{where} ({mid}).secondary_risks[{j}]"
        n1 = len(problems)
        warn: list[str] = []
        sr = service._risk(s, sw, problems, warn)
        if sr is None and len(problems) == n1:
            problems.append(f"{sw}: probability and delay must both be entered, otherwise the secondary risk would be "
                            "silently left out of the evaluation")
        if sr is not None:
            dcost = s.get("direct_cost_if_occurs")
            if isinstance(dcost, Mapping) and not _blank(dcost.get("value")):
                dp = _param(dcost, f"{sw}.direct_cost_if_occurs", problems)
                if dp is not None:
                    sr = replace(sr, direct_cost_if_occurs=dp)
            secondary.append(sr)

    feasible = d.get("feasible", True)
    if not isinstance(feasible, bool):
        problems.append(f"{where} ({mid}).feasible: expected true or false")
        feasible = True
    tti = _opt_number(d, "time_to_implement_days", f"{where} ({mid})", problems, 0.0) or 0.0
    if len(problems) > n0 or cost is None:
        return None
    m = Mitigation(mid, str(rid), str(d.get("action") or mid), strategy, cost, p_after, delay_after, tuple(secondary),
                   feasible, str(d.get("infeasible_reason") or ""), tti, tuple(d.get("evidence_ids") or ()),
                   str(d.get("mechanism") or ""), str(d.get("catalogue_id") or ""))
    try:
        m.validate()
    except ValueError as e:
        problems.append(f"{where} ({mid}): {e}")
        return None
    return m


def parse_analysis(case: Mapping) -> dict:
    """Parse the analysis inputs.  Raises CaseError listing every problem found (nothing is corrected silently)."""
    pc = service.parse_case(case)                       # register problems raise here
    problems: list[str] = []
    warnings: list[str] = [w for w in pc["warnings"] if "not on the matrix yet" not in w and "risk matrix not computed" not in w]

    planned = pc["planned"]
    if planned is None:
        problems.append("activity.planned_duration_days: required for the analysis (value and source)")

    # risks, with the optional direct cost of occurrence
    built = {r.risk_id: r for r in pc["risks"]}
    risks: list[Risk] = []
    incomplete = []
    for raw in pc["raw_risks"]:
        rid = None if _blank(raw.get("id")) else str(raw["id"])
        r = built.get(rid)
        if r is None:
            if rid is not None:
                incomplete.append(rid)
            continue
        dc = raw.get("direct_cost_if_occurs")
        if isinstance(dc, Mapping) and not _blank(dc.get("value")):
            dp = _param(dc, f"risks[{rid}].direct_cost_if_occurs", problems)
            if dp is not None:
                if dp.value < 0:
                    problems.append(f"risks[{rid}].direct_cost_if_occurs: must be 0 or more")
                else:
                    r = replace(r, direct_cost_if_occurs=dp)
        risks.append(r)
    if not risks:
        problems.append("no complete risk in the register: enter probability and delay for at least one risk")
    if incomplete:
        warnings.append("left out of the simulation (probability or delay not entered): " + ", ".join(incomplete))

    # deadline
    a = case.get("activity") or {}
    deadline = None
    dd = a.get("deadline_days")
    if isinstance(dd, Mapping) and not _blank(dd.get("value")):
        deadline = _param(dd, "activity.deadline_days", problems)
        if deadline is not None and deadline.value <= 0:
            problems.append("activity.deadline_days must be greater than 0")
            deadline = None

    # cost model
    cost = None
    c = case.get("cost")
    cd = c.get("cost_per_delay_day") if isinstance(c, Mapping) else None
    if not isinstance(cd, Mapping) or _blank(cd.get("value")):
        problems.append("cost.cost_per_delay_day: input required (cost of one extra working day, with a source); it has no default")
    else:
        cdp = _param(cd, "cost.cost_per_delay_day", problems)
        if cdp is not None and cdp.value < 0:
            problems.append("cost.cost_per_delay_day: must be 0 or more")
            cdp = None
        ldp = Param(0.0, Source.USER, note="not modelled")
        ld = c.get("ld_per_day_after_deadline")
        if isinstance(ld, Mapping) and not _blank(ld.get("value")):
            p_ld = _param(ld, "cost.ld_per_day_after_deadline", problems)
            if p_ld is not None:
                if p_ld.value < 0:
                    problems.append("cost.ld_per_day_after_deadline: must be 0 or more")
                elif p_ld.value > 0 and deadline is None:
                    problems.append("cost.ld_per_day_after_deadline: liquidated damages need activity.deadline_days")
                else:
                    ldp = p_ld
        if cdp is not None:
            cost = CostModel(cdp, str(c.get("currency") or "INR"), ldp)

    # simulation settings
    sim = case.get("simulation") or {}
    n = _int_setting(sim, "n", DEFAULT_N, 1, MAX_N, problems)
    seed = _int_setting(sim, "seed", DEFAULT_SEED, 0, 2**31 - 1, problems)
    criterion = sim.get("criterion") or "min_expected_total_cost"
    if criterion not in CRITERIA:
        problems.append(f"simulation.criterion: unknown '{criterion}' (use one of {list(CRITERIA)})")
    elif criterion == "min_deadline_exceedance" and deadline is None:
        problems.append("simulation.criterion: 'min_deadline_exceedance' needs activity.deadline_days")
    ids = {r.risk_id for r in risks}
    corr: dict[tuple[str, str], float] = {}
    for i, row in enumerate(sim.get("correlation") or []):
        w = f"simulation.correlation[{i}]"
        if not isinstance(row, Mapping) or _blank(row.get("a")) or _blank(row.get("b")) or _blank(row.get("rho")):
            problems.append(f"{w}: expected a, b and rho")
            continue
        if row["a"] not in ids or row["b"] not in ids or row["a"] == row["b"]:
            problems.append(f"{w}: a and b must be two different complete risks in the register")
            continue
        try:
            rho = float(row["rho"])
        except (TypeError, ValueError):
            problems.append(f"{w}.rho: not a number")
            continue
        if not (-1.0 <= rho <= 1.0):
            problems.append(f"{w}.rho: must be between -1 and 1")
            continue
        corr[(str(row["a"]), str(row["b"]))] = rho

    # mitigations
    mits: list[Mitigation] = []
    seen: set[str] = set()
    for i, raw in enumerate(case.get("mitigations") or []):
        if not isinstance(raw, Mapping):
            problems.append(f"mitigations[{i}]: expected an object")
            continue
        if not _blank(raw.get("id")) and str(raw["id"]) in seen:
            problems.append(f"mitigations[{i}]: duplicate id '{raw['id']}'")
            continue
        if not _blank(raw.get("id")):
            seen.add(str(raw["id"]))
        m = _mitigation(raw, f"mitigations[{i}]", problems, ids)
        if m is not None:
            mits.append(m)
    by_id = {m.mitigation_id: m for m in mits}
    for m in mits:
        if m.p_after is None and m.delay_after is None and m.feasible:
            warnings.append(f"{m.mitigation_id}: no modelled effect (enter p after and/or delay after, normally as Expert "
                            "Judgment); it is left out of the options")

    # options and constraints
    options: list[Option] = []
    oids: set[str] = set()
    for i, raw in enumerate(case.get("options") or []):
        w = f"options[{i}]"
        if not isinstance(raw, Mapping) or _blank(raw.get("id")):
            problems.append(f"{w}: id is required")
            continue
        oid = str(raw["id"])
        if oid in oids:
            problems.append(f"{w}: duplicate option id '{oid}'")
            continue
        oids.add(oid)
        mids = [str(x) for x in (raw.get("mitigation_ids") or [])]
        unknown = [x for x in mids if x not in by_id]
        if unknown:
            problems.append(f"{w} ({oid}): unknown or invalid mitigation(s): {', '.join(unknown)}")
            continue
        targets = [by_id[x].risk_id for x in mids]
        if len(set(targets)) != len(targets):
            problems.append(f"{w} ({oid}): two mitigations target the same risk; an option may contain at most one per risk")
            continue
        options.append(Option(oid, str(raw.get("label") or oid), tuple(mids)))

    con = case.get("constraints") or {}
    max_p = _opt_number(con, "max_p_exceed_deadline", "constraints", problems, 0.0, 1.0)
    budget = _opt_number(con, "max_mitigation_budget", "constraints", problems, 0.0)
    if max_p is not None and deadline is None:
        problems.append("constraints.max_p_exceed_deadline needs activity.deadline_days")

    if problems:
        raise CaseError(problems)
    return {"project": pc["project"], "activity_info": pc["activity"], "planned": planned, "deadline": deadline,
            "risks": risks, "cost": cost, "n": n, "seed": seed, "criterion": criterion, "correlation": corr or None,
            "mitigations": mits, "options": options, "constraints": Constraints(max_p, budget), "warnings": warnings}


# ----------------------------------------------------------------------------------------------- running
def run_analysis(case: Mapping, evidence_index: Optional[Mapping[str, str]] = None) -> dict:
    pa = parse_analysis(case)
    risks, cost, mits = pa["risks"], pa["cost"], pa["mitigations"]
    n, seed, crit, corr = pa["n"], pa["seed"], pa["criterion"], pa["correlation"]
    activity = Activity(pa["activity_info"]["id"], pa["activity_info"]["name"], pa["planned"], deadline_days=pa["deadline"])
    deadline = pa["deadline"].value if pa["deadline"] else None
    warnings = list(pa["warnings"])
    try:
        res = simulate(activity, risks, n, seed, corr)
        summary = summarise(res, deadline_days=deadline)
        cost_sum = cost_summary(res, cost, deadline)
        stake = value_at_stake(activity, risks, cost, n, seed, corr)
        suggestions = suggest_options(activity, risks, cost, mits, n=n, seed=seed, occurrence_correlation=corr)

        if pa["options"]:
            options, build_notes, options_source = pa["options"], {"n_generated": len(pa["options"])}, "user"
        else:
            options, build_notes = build_options(mits)
            options_source = "generated" if options else "none"
        decision = compare_options(activity, risks, options, mits, cost, crit, pa["constraints"], n, seed, corr)

        n_eval = len(decision["options"])
        if n_eval <= 1:
            command = {"command": "NO RESPONSE EVALUATED", "selected_option_id": decision["selected_option_id"],
                       "criterion": crit, "figures": {},
                       "reason": ("Only accepting the risk was evaluated, because no mitigation with a modelled effect was "
                                  "entered. This is not a recommendation to accept: see option_suggestions for where the "
                                  "money is and what to enter for each candidate action.")}
            stability = sens_dec = None
        else:
            command = decision_command(decision, cost.currency)
            aux = selection_stability(activity, risks, options, mits, cost, crit, pa["constraints"], n,
                                      [seed + 1, seed + 2], corr)
            picks = [decision["selected_option_id"]] + aux["selected_option_ids"]
            stability = {**aux, "seeds": [seed] + aux["seeds"], "selected_option_ids": picks, "stable": len(set(picks)) == 1}
            sens_dec = decision_sensitivity(activity, risks, options, mits, cost, crit, pa["constraints"], min(n, 5000),
                                            seed, occurrence_correlation=corr)
            if not stability["stable"]:
                warnings.append("the preferred option changes with the random seed: the options are too close to separate "
                                "at this number of iterations, so do not present the choice as firm")
    except ValueError as e:
        raise CaseError([str(e)]) from e

    rmap = {r.risk_id: r for r in risks}
    checks = []
    for m in mits:
        chk = mitigation_net_benefit(rmap[m.risk_id], m, cost)
        chk["break_even"] = break_even_targets(rmap[m.risk_id], cost, m.cost.value)
        chk["action"] = m.action
        chk["catalogue_id"] = m.catalogue_id
        checks.append(chk)

    inputs = {"activity": activity, "risks": risks, "cost": cost, "mitigations": mits}
    assumptions = assumption_register(inputs)
    result = {
        "ok": True,
        "project": pa["project"],
        "activity": {"id": activity.activity_id, "name": activity.name,
                     "planned_duration_days": service._param_row(activity.baseline_duration_days),
                     "deadline_days": service._param_row(pa["deadline"])},
        "baseline": {"planned_days": activity.baseline_duration_days.value,
                     "basis": f"planned duration entered as {activity.baseline_duration_days.source.value}"},
        "n_used": n, "seed": seed, "criterion": crit,
        "summary": summary, "cost": cost_sum,
        "event_emv": event_emv(risks, cost), "sensitivity": sensitivity(res), "convergence": convergence(res),
        "value_at_stake": stake,
        "option_suggestions": suggestions,
        "mitigation_checks": checks,
        "options_source": options_source, "option_build_notes": build_notes,
        "decision": decision, "command": command,
        "decision_stability": stability, "decision_sensitivity": sens_dec,
        "assumptions": assumptions,
        "audit": build_record(inputs, {"command": command["command"], "selected_option_id": command["selected_option_id"]},
                              seed=seed, n=n, criterion=crit),
        "warnings": warnings,
    }
    result = to_jsonable(result)
    from app.ai_layer.explain import explain_deterministic
    from app.reporting.analysis_report import analysis_markdown

    result["explanation"] = explain_deterministic(result)
    result["report_markdown"] = analysis_markdown(result, evidence_index)
    return result


# ----------------------------------------------------------------------------------------------- example
def example_analysis_case() -> dict:
    """ILLUSTRATIVE analysis case: the register example plus a cost model, a deadline and six responses.
    Every number is a placeholder labelled Assumption.  NOT evidence, NOT site data, NOT an expert's estimate."""
    A = "Assumption"
    note = "ILLUSTRATIVE placeholder, not evidence"
    case = service.example_case()
    case["project"]["name"] = "ILLUSTRATIVE analysis example"
    case["activity"]["deadline_days"] = {"value": 20, "source": A, "note": note}
    case["cost"] = {"cost_per_delay_day": {"value": 8000, "source": A, "note": note},
                    "ld_per_day_after_deadline": {"value": 5000, "source": A, "note": note}, "currency": "INR"}

    def mit(mid, rid, action, cost, strategy="mitigate", p_after=None, delay_after=None, cat="", ev=(), **kw):
        d = {"id": mid, "risk_id": rid, "action": action, "strategy": strategy, "catalogue_id": cat,
             "evidence_ids": list(ev), "cost": {"value": cost, "source": A, "note": note}}
        if p_after is not None:
            d["p_after"] = {"value": p_after, "source": A, "note": note}
        if delay_after is not None:
            d["delay_after"] = {"kind": "pert", "a": delay_after[0], "m": delay_after[1], "b": delay_after[2], "source": A}
        d.update(kw)
        return d

    case["mitigations"] = [
        mit("M-BUF", "R-MAT", "Buffer stock of bricks and mortar materials", 6000, p_after=0.20, cat="C-BUFFER", ev=("D03", "D11")),
        mit("M-SUP", "R-MAT", "Second approved brick supplier", 3000, p_after=0.35, cat="C-SUPPLIER", ev=("D35",)),
        mit("M-GANG", "R-LAB", "Extra mason gang for the critical weeks", 9000, delay_after=(0, 1, 3), cat="C-CREW-UP",
            ev=("D12",), secondary_risks=[{"id": "S-CONG", "name": "Work-front congestion", "category": "Labour",
                                          "p": {"value": 0.30, "source": A, "note": note},
                                          "delay": {"kind": "pert", "a": 0, "m": 1, "b": 2, "source": A}}]),
        mit("M-COV", "R-WX", "Covers and sheltered work sequence for the rain period", 2500, p_after=0.12, cat="C-WEATHER", ev=("D20",)),
        mit("M-QC", "R-RWK", "Inspection hold point before each course", 1500, p_after=0.15, cat="C-QC", ev=("D03",)),
        mit("M-MECH", "R-SKILL", "Switch to larger blocks", 4000, strategy="avoid", p_after=0.10, cat="C-MECHANISE",
            ev=("D04",), feasible=False, infeasible_reason="no block supplier within delivery range (illustrative)"),
    ]
    case["constraints"] = {"max_p_exceed_deadline": None, "max_mitigation_budget": None}
    case["simulation"] = {"n": 10000, "seed": 12345, "criterion": "min_expected_total_cost"}
    return case
