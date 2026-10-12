"""Analysis report (Markdown), built only from a run_analysis result.

Nothing is computed here: every figure is copied from the result the engine returned, with its Source and the
caveats printed beside it.  The wording never calls a result optimal.
"""
from __future__ import annotations

from typing import Mapping, Optional


def _m(v, nd: int = 0) -> str:
    return "n/a" if v is None else f"{v:,.{nd}f}"


def _pct(v, nd: int = 1) -> str:
    return "n/a" if v is None else f"{v * 100:.{nd}f}%"


def analysis_markdown(result: Mapping, evidence_index: Optional[Mapping[str, str]] = None) -> str:
    evidence_index = evidence_index or {}
    cur = result["cost"]["currency"]
    proj, act, s, c, d = result["project"], result["activity"], result["summary"], result["cost"], result["decision"]
    cmd = result["command"]
    L = [f"# Delay cost and response analysis: {proj.get('name') or 'untitled case'}", ""]
    pd, dl = act["planned_duration_days"], act.get("deadline_days")
    L += [f"Activity: **{act.get('name') or act['id']}**. Planned duration **{pd['value']:g} working days** (Source: {pd['source']})"
          + (f"; deadline **{dl['value']:g} days** (Source: {dl['source']})." if dl else "; no deadline entered."),
          f"Simulation: {result['n_used']:,} iterations, seed {result['seed']}. Decision criterion: {d['criterion']}.", ""]
    if proj.get("notes"):
        L += [f"> {proj['notes']}", ""]

    L += ["## Decision", "", f"**{cmd['command']}**", "", cmd["reason"], ""]
    f = cmd.get("figures") or {}
    if cmd["command"] == "AUTHORIZE MITIGATION":
        L += [f"- Mitigation cost: {_m(f['mitigation_cost'])} {cur}",
              f"- Expected total cost saving against accepting the risk: {_m(f['expected_cost_saving_vs_accept'])} {cur}",
              f"- Expected delay avoided: {_m(f['expected_delay_avoided_days'], 2)} days; P90 duration change: "
              f"{f['P90_change_vs_accept_days']:+.2f} days",
              f"- Mitigation cost per delay day avoided: {_m(f['mitigation_cost_per_day_avoided'])} {cur}, against a delay cost of "
              f"{_m(f['delay_cost_per_day'])} {cur} per day (a break-even guide when no liquidated damages apply)"]
        if f.get("runner_up_id"):
            L.append(f"- Closest alternative: {f['runner_up_label']}, with a total expected cost {_m(f['runner_up_extra_cost'])} {cur} "
                     f"higher ({_pct(f['runner_up_extra_cost_share'])}). A gap this small means the two are close; "
                     "judge them on the other columns too.")
        L.append("")
    st = result.get("decision_stability")
    if st:
        L += [f"Seed check: preferred option under seeds {st['seeds']} was {st['selected_option_ids']}; "
              + ("the choice is **stable**." if st["stable"] else "the choice **changes with the seed**, so it is not a firm result."), ""]
    L += [f"_{d['caveat']}_", ""]

    L += ["## Simulated schedule and cost", "",
          f"- Expected duration {s['mean']:.1f} days (expected delay {s['expected_delay']:.1f} days); "
          f"P50 {s['percentiles']['P50']:.1f}, P80 {s['percentiles']['P80']:.1f}, P90 {s['percentiles']['P90']:.1f}, "
          f"P95 {s['percentiles']['P95']:.1f} days."]
    if "p_exceed_deadline" in s:
        L.append(f"- Probability of finishing after the deadline: {_pct(s['p_exceed_deadline'])}.")
    L += [f"- Expected delay cost {_m(c['expected_cost'])} {cur} (P50 {_m(c['P50'])}, P90 {_m(c['P90'])}, P95 {_m(c['P95'])}).", ""]

    L += ["## Where the money is: event EMV and value at stake", "",
          "Event EMV is p x (expected delay if it occurs x cost per day + direct cost). Value at stake is the expected cost "
          "that disappears if the risk could not occur, simulated on the same random draws; it is the ceiling on what any "
          "response to that risk can be worth.", "",
          f"| Risk | p | Event EMV ({cur}) | Value at stake ({cur}) | Share of expected cost |", "|---|---|---|---|---|"]
    emv = {r["risk_id"]: r for r in result["event_emv"]}
    for r in result["value_at_stake"]:
        L.append(f"| {r['risk_id']} {r['name']} | {r['p']:g} | {_m(emv[r['risk_id']]['emv'])} | {_m(r['value_at_stake'])} | "
                 f"{_pct(r['share_of_expected_cost'])} |")
    L.append("")

    L += ["## Options compared", ""]
    src = {"user": "entered by the user", "generated": "generated from the mitigations (single responses, then combinations that "
           "target different risks)", "none": "none: no mitigation with a modelled effect"}[result["options_source"]]
    L += [f"Options: {src}. All options use the same random draws, so differences are not sampling noise.", "",
          f"| Option | Mitigation cost ({cur}) | Residual expected cost | Total expected cost | P90 (d) | P(T > deadline) | Admissible |",
          "|---|---|---|---|---|---|---|"]
    sel = d["selected_option_id"]
    for o in d["options"]:
        pe = "n/a" if o["p_exceed_deadline"] is None else _pct(o["p_exceed_deadline"])
        why = "yes" if o["admissible"] else "no: " + "; ".join(o["rejected_because"])
        mark = " **(preferred)**" if o["option_id"] == sel else ""
        L.append(f"| {o['label']}{mark} | {_m(o['mitigation_cost'])} | {_m(o['residual_expected_cost'])} | "
                 f"{_m(o['total_expected_cost'])} | {o['P90']:.1f} | {pe} | {why} |")
    L.append("")
    notes = result.get("option_build_notes") or {}
    if notes.get("truncated"):
        L += [f"Only the first {notes['max_options']} generated options were evaluated.", ""]
    ds = result.get("decision_sensitivity")
    if ds:
        L += ["### Does the choice depend on the cost per delay day?", "",
              "| Cost per delay day x | Cost per day | Preferred |", "|---|---|---|"]
        for r in ds["rows"]:
            L.append(f"| {r['multiplier']:g} | {_m(r['cost_per_delay_day'])} {cur} | {r['command']}: {r['selected_option_id']} |")
        L += ["", ds["note"], ""]

    if result["mitigation_checks"]:
        L += ["## Does each response pay for itself? (one response at a time)", "",
              f"| Response | Targets | EMV before | EMV after | Secondary risk EMV | Cost | Net benefit ({cur}) | Must achieve |",
              "|---|---|---|---|---|---|---|---|"]
        for k in result["mitigation_checks"]:
            be = k["break_even"]
            need = be["reason"]
            L.append(f"| {k['mitigation_id']} {k['action']} | {k['risk_id']} | {_m(k['emv_before'])} | {_m(k['emv_after'])} | "
                     f"{_m(k['secondary_risk_emv'])} | {_m(k['mitigation_cost'])} | {_m(k['net_benefit'])} | {need} |")
        L += ["", "Analytic and exact only for additive linear cost with no liquidated damages; with liquidated damages rely on the "
              "simulated comparison above.", ""]

    sug = result["option_suggestions"]
    L += ["## Where to look for responses", "", sug["note"], ""]
    for t in sug["targets"]:
        L += [f"### {t['risk_id']} {t['name']}: up to {_m(t['max_justified_spend'])} {cur} can be justified", ""]
        if not t["candidate_actions"]:
            L += ["No catalogue entry targets this risk; define a custom response.", ""]
        for a in t["candidate_actions"]:
            ev = ", ".join(a["evidence_ids"])
            L += [f"- **{a['measure']}** ({a['strategy']}; evidence quantified: {a['quantified_evidence']}; {a['status']}). "
                  f"{a['evidence_summary']} Evidence: {ev}. Needs: " + "; ".join(a["inputs_required"]) + "."]
        L.append("")

    L += ["## Inputs that are not literature or historical data", "",
          "| Input | Value | Source |", "|---|---|---|"]
    for a in result["assumptions"]:
        L.append(f"| {a['input']} | {a['value']:g} | {a['source']} |")
    L += ["", f"Input hash (SHA-256): `{result['audit']['input_hash_sha256']}`", ""]
    if result.get("warnings"):
        L += ["## Notes", ""] + [f"- {w}" for w in result["warnings"]] + [""]
    L += ["## Explanation", ""] + [f"- {x}" for x in result.get("explanation", [])]
    return "\n".join(L) + "\n"
