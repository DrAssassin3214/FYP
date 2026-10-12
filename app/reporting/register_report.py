"""Risk register and matrix export (Markdown and CSV), built only from a run_case result.

Nothing is computed here: every figure is copied from the result the service returned, with the Source
of each number printed next to it.
"""
from __future__ import annotations

import csv
import io
from typing import Mapping, Optional

from app.engine.matrix import matrix_level

LEVELS = ("Extreme", "High", "Moderate", "Low")
AI_NOTE = (
    "This tool does not generate probabilities, delays or costs. Each number shown was entered with the S"
    "ource printed next to it. The AI suggestion feature can propose risk names, mechanisms and evidence IDs only; its numeric fields and any figures in its text are rejected (guard rules G2, G7, G9).")
_SQUARE = {"Low": "🟩", "Moderate": "🟨", "High": "🟧", "Extreme": "🟥"}


def _t(v) -> str:
    """Coerce any value to text (None -> empty) so odd types never crash an export."""
    return "" if v is None else str(v)


def _md(v) -> str:
    """Make a value safe inside a Markdown table cell: escape pipes, flatten newlines."""
    return _t(v).replace("\\", "\\\\").replace("|", "\\|").replace("\r\n", "<br>").replace("\n", "<br>").replace("\r", "<br>")


_FORMULA_START = ("=", "+", "-", "@", "\t", "\r")


def _csv_safe(v):
    """Neutralise spreadsheet formula injection: a text cell starting with = + - @ TAB or CR gets a leading
    single quote. Numbers are passed through untouched."""
    if isinstance(v, bool) or v is None:
        return "" if v is None else v
    if isinstance(v, (int, float)):
        return v
    s = str(v)
    if s.startswith(_FORMULA_START) or s.lstrip(" ").startswith(_FORMULA_START):
        return "'" + s
    return s


def _is_illustrative(result: Mapping) -> bool:
    proj = result.get("project") or {}
    if "illustrative" in (_t(proj.get("name")) + " " + _t(proj.get("notes"))).lower():
        return True
    for r in result.get("risks") or []:
        for k in ("p", "delay"):
            if "illustrative" in _t((r.get(k) or {}).get("note")).lower():
                return True
    return False


def settings_text(result: Mapping) -> str:
    """One paragraph naming every setting that turns numbers into classes and levels, each with its Source."""
    ms = result.get("matrix_settings") or {}
    ie = ms.get("impact_edges")
    imp = ("Impact edges " + " / ".join(f"{x:g}" for x in ie) + " of planned duration (Source: "
           + _t(ms.get("impact_edges_source") or "not given")
           + (f", {_t(ms['impact_edges_note'])}" if ms.get("impact_edges_note") else "") + ")") if ie \
        else "Impact edges not entered (Source: not given)"
    pe = ms.get("p_edges") or [0.2, 0.4, 0.6, 0.8]
    th = ms.get("level_thresholds") or [5, 10, 15]
    return (imp + ". Probability edges " + " / ".join(f"{x:g}" for x in pe) + " (Source: Assumption, tool default). "
            "Level = probability class x impact class; thresholds " + " / ".join(f"{x:g}" for x in th)
            + " give Low / Moderate / High / Extreme (Source: Assumption, tool default). A value exactly on an edge "
            "goes to the higher class.")


TIER_LABEL = "literature tier (Assumption)"
CLASS1_NOTE = ("Assumption: level = probability class x impact class with the thresholds above. A risk in probability "
               "class 1 is Low whatever its impact (a known weakness of multiplicative risk matrices, Cox, 2008); "
               "risks with impact class 5 are therefore also listed separately. That list is a filter, not a score.")
SEED_NOTE = ("Placements marked literature tier (Assumption) come from survey Relative Importance Index values in the "
             "evidence store, not from entered numbers: the rank band (1-5) is used for both axes and a rule flag raises "
             "the probability class by one (both are Assumptions). An importance index is neither a probability nor a "
             "delay, so these cells are a starting point to replace with your own numbers.")


def _is_seed(m: Optional[Mapping]) -> bool:
    return bool(m) and m.get("basis") == "literature-seed"


def _mx_text(m: Optional[Mapping]) -> str:
    """Matrix column text: a level for entered numbers; 'literature tier (Assumption)' for seeded placements."""
    if not m:
        return "not placed"
    if _is_seed(m):
        return (f"{TIER_LABEL}: tier {m.get('tier', m['impact_class'])}, p{m['p_class']} x i{m['impact_class']}"
                + ("; p class +1 for rule flag (Assumption)" if m.get("raised_by_rule") else ""))
    return f"{m['level']} (p{m['p_class']} x i{m['impact_class']})"


def _response_rows(rows) -> list:
    return [r for r in rows if any(r.get(k) for k in ("owner", "trigger", "response_type", "response_action", "review_date"))]


def _basis(r: Mapping, m: Optional[Mapping]) -> str:
    if m and m.get("basis") == "literature-seed":
        return "literature seed (RII tier, not a probability; tier is an Assumption)"
    if r.get("p") and r.get("delay"):
        return "entered numbers"
    return "incomplete (probability and/or delay not entered)"


def _delay_text(d: Optional[Mapping]) -> str:
    if not d:
        return "not entered"
    k = d["kind"]
    if k == "fixed":
        return f"{d['m']:g} d fixed"
    if k == "uniform":
        return f"{d['a']:g}-{d['b']:g} d uniform"
    return f"{d['a']:g} / {d['m']:g} / {d['b']:g} d {'PERT' if k == 'pert' else 'triangular'}"


def _p_text(p: Optional[Mapping]) -> str:
    return "not entered" if not p else f"{p['value']:g}"


def generate_register_report(result: Mapping, evidence_index: Optional[Mapping[str, str]] = None) -> str:
    evidence_index = evidence_index or {}
    proj, act = result["project"], result["activity"]
    rows, matrix = result["risks"], {m["risk_id"]: m for m in result["matrix"]}
    L = [f"# Risk register and matrix: {_t(proj.get('name')).replace(chr(10), ' ') or 'untitled case'}", ""]
    if _is_illustrative(result):
        L += ["**ILLUSTRATIVE case: every number is a placeholder, not evidence and not site data.**", ""]
    meta = [_t(x).replace("\n", " ") for x in (proj.get("location"), proj.get("construction_type")) if x]
    if meta:
        L += [" · ".join(meta), ""]
    pd = act.get("planned_duration_days")
    L += [f"Activity: **{_md(act.get('name') or act.get('id'))}**. Planned duration: "
          + (f"**{pd['value']:g} working days** (Source: {_t(pd['source'])})." if pd else "not entered."), ""]
    if proj.get("notes"):
        L += ["\n".join("> " + ln for ln in _t(proj["notes"]).splitlines()) or "> ", ""]

    s = result["summary"]
    L += ["## Summary", "",
          f"- Risks in the register: **{s['n_risks']}** ({s['n_complete']} with probability and delay entered, "
          f"{s['n_incomplete']} still incomplete)",
          f"- Placed on the matrix: **{s['n_on_matrix']}**, of which **{s.get('n_seeded', 0)}** at a {TIER_LABEL} "
          "(from the survey ranking, not from entered numbers) and "
          f"**{s.get('n_on_matrix_entered', s['n_on_matrix'] - s.get('n_seeded', 0))}** from entered numbers"
          + (" (levels of the entered ones: " + ", ".join(f"{s['levels'][k]} {k}" for k in LEVELS if s["levels"].get(k)) + ")"
             if s["levels"] and any(s["levels"].values()) else ""),
          f"- Risks flagged as elevated by the site-fact rules: **{s['n_flagged']}**, of which "
          f"**{s['n_flagged_missing']}** are not in the register", ""]

    L += ["## Risk register", ""]
    if rows:
        L += ["| ID | Risk | Category | Status | Basis | p (Source) | Extra delay if it occurs (Source) | Matrix | Evidence |",
              "|---|---|---|---|---|---|---|---|---|"]
        for r in rows:
            m = matrix.get(r["id"])
            p, d = r.get("p"), r.get("delay")
            L.append("| {id} | {name} | {cat} | {st} | {basis} | {p} | {d} | {mx} | {ev} |".format(
                id=_md(r["id"]), name=_md(r["name"]), cat=_md(r["category"]), st=_md(r["status"]),
                basis=_md(_basis(r, m)),
                p=_md(_p_text(p) + (f" ({p['source']})" if p else "")),
                d=_md(_delay_text(d) + (f" ({d['source']})" if d else "")),
                mx=_md(_mx_text(m)),
                ev=_md(", ".join(_t(e) for e in (r.get("evidence_ids") or [])) or "none")))
    else:
        L.append("No risks in the register.")
    L.append("")

    resp = _response_rows(rows)
    L += ["## Responses", "",
          "Owner, early-warning sign, response type (avoid / reduce / transfer / accept) and action are text entered by "
          "the team. They carry no numbers and the tool does not quantify their effect.", ""]
    if resp:
        L += ["| ID | Owner | Early-warning sign (trigger) | Response type | Response action | Review date |",
              "|---|---|---|---|---|---|"]
        L += ["| {} | {} | {} | {} | {} | {} |".format(_md(r["id"]), _md(r.get("owner")), _md(r.get("trigger")),
                                                  _md(r.get("response_type")), _md(r.get("response_action")),
                                                  _md(r.get("review_date"))) for r in resp]
    else:
        L.append("No owner, trigger or response entered yet.")
    L.append("")

    L += ["## Risk matrix", ""]
    if matrix:
        cells: dict[tuple[int, int], list[str]] = {}
        for m in matrix.values():
            cells.setdefault((m["p_class"], m["impact_class"]), []).append(m["risk_id"] + ("†" if _is_seed(m) else ""))
        L += ["Probability class (rows) by impact class (columns). Impact is the expected delay if the risk occurs, as a "
              "fraction of the planned duration, binned by the edges you entered. Ordinal prioritisation only.", "",
              settings_text(result), "",
              "| p class \\ impact | 1 | 2 | 3 | 4 | 5 |", "|---|---|---|---|---|---|"]
        for pc in range(5, 0, -1):
            L.append(f"| {pc} | " + " | ".join(
                _SQUARE[matrix_level(pc, ic)] + " " + (", ".join(_md(x) for x in cells.get((pc, ic), [])) or "") for ic in range(1, 6)) + " |")
        L += ["", "Colour key: " + "  ".join(f"{_SQUARE[k]} {k}" for k in LEVELS)
              + (f"  ·  † = {TIER_LABEL}: placed from the survey ranking, not an assessed level" if any(_is_seed(m) for m in matrix.values()) else "")]
        L += ["", CLASS1_NOTE]
        entered = [m for m in matrix.values() if not _is_seed(m)]
        seeded = [m for m in matrix.values() if _is_seed(m)]
        L += ["", "| Risk | p | p class | Expected delay (d) | Impact class | Score | Level |", "|---|---|---|---|---|---|---|"]
        for m in sorted(entered, key=lambda x: -x["score"]):
            L.append(f"| {_md(m['risk_id'])} | {format(m['p'], 'g')} | {m['p_class']} | "
                     f"{format(m['expected_delay_if_occurs_days'], '.2f')} | {m['impact_class']} | {m['score']} | {m['level']} |")
        if seeded:
            L += ["", f"### {TIER_LABEL[0].upper() + TIER_LABEL[1:]}", "",
                  "Not an assessed level: the tier is the survey rank band (1 = least important, 5 = most important); the "
                  "score is tier x tier, kept for ordering only (Assumption).", "",
                  "| Risk | Literature tier | p class | Impact class | Score (Assumption) |", "|---|---|---|---|---|"]
            for m in sorted(seeded, key=lambda x: -x["score"]):
                L.append(f"| {_md(m['risk_id'])} | {m.get('tier', m['impact_class'])} | {m['p_class']}"
                         f"{' (+1 rule flag)' if m.get('raised_by_rule') else ''} | {m['impact_class']} | {m['score']} |")
        hc = result.get("high_consequence")
        if hc is None:
            hc = sorted(({"risk_id": m["risk_id"], "p": m["p"], "p_class": m["p_class"], "impact_class": 5, "level": m["level"]}
                         for m in entered if m["impact_class"] == 5), key=lambda x: -x["p"])
        L += ["", "### High-consequence list (impact class 5, entered numbers only)", "",
              "A filter, not a score: every risk whose impact class is 5, whatever its level, sorted by p."]
        if hc:
            L += ["", "| Risk | p (Source: as entered) | p class | Level |", "|---|---|---|---|"]
            L += [f"| {_md(x['risk_id'])} | {format(x['p'], 'g')} | {x['p_class']} | {x['level']} |" for x in hc]
        else:
            L += ["", "No risk with entered numbers is in impact class 5."]
    else:
        L.append("The matrix was not computed. See the notes below.")
    L.append("")

    fired = result["rules"].get("fired") or []
    L += ["## Rules that fired", ""]
    if fired:
        for f in fired:
            L.append(f"- **{_md(f['rule_id'])}** flags {_md(f.get('risk_id', ''))} as {f['level']}; facts used: "
                     + ", ".join(f"{k} = {v}" for k, v in f["facts_used"].items()))
    else:
        L.append("No rule fired on the facts entered.")
    L.append("")

    L += ["## Notes and limits", ""]
    L += [f"- {_t(w).replace(chr(10), ' ')}" for w in result["warnings"]] or ["- none"]
    if s.get("n_seeded"):
        L += [f"- {s['n_seeded']} risk(s) marked {TIER_LABEL} have no probability or delay entered. " + SEED_NOTE]
    L += ["- Probabilities and delays are inputs from you, site records or cited sources, each labelled with its Source. "
          + AI_NOTE,
          "- The matrix is a prioritisation aid, not a quantity.", ""]

    cited = sorted({_t(e) for r in rows for e in (r.get("evidence_ids") or [])})
    if cited:
        L += ["## Evidence cited", ""]
        L += [f"- **{_md(e)}**: {_md(evidence_index.get(e, 'reference not found in the evidence corpus'))}" for e in cited]
        L.append("")
    return "\n".join(L)


def register_csv(result: Mapping) -> str:
    """CSV text (no BOM; callers encode as utf-8-sig so Excel on Windows decodes unicode). Every text cell
    is neutralised against formula injection. 'basis' says whether p/delay are entered numbers or a
    literature seed (RII tier, not a probability); seeded rows have an empty `level` and a `tier` text instead;
    'case'/'note' carry the ILLUSTRATIVE flag."""
    matrix = {m["risk_id"]: m for m in result["matrix"]}
    case_name = _t((result.get("project") or {}).get("name"))
    note = "ILLUSTRATIVE: placeholder numbers, not evidence" if _is_illustrative(result) else ""
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["id", "name", "category", "status", "basis", "p", "p_source", "delay_kind", "delay_min",
                "delay_most_likely", "delay_max", "delay_source", "expected_delay_days", "p_class", "impact_class",
                "score", "level", "evidence_ids", "case", "note", "delay_note", "expected_delay_source", "tier",
                "owner", "trigger", "response_type", "response_action", "review_date"])
    for r in result["risks"]:
        p, d, m = r.get("p") or {}, r.get("delay") or {}, matrix.get(r["id"]) or {}
        seed = m.get("basis") == "literature-seed"
        w.writerow([_csv_safe(x) for x in [
            r["id"], r["name"], r["category"], r["status"], _basis(r, m or None),
            p.get("value", ""), p.get("source", ""), d.get("kind", ""), d.get("a", ""), d.get("m", ""), d.get("b", ""),
            d.get("source", ""), "" if seed else m.get("expected_delay_if_occurs_days", ""), m.get("p_class", ""),
            m.get("impact_class", ""), m.get("score", ""), "" if seed else m.get("level", ""),
            ";".join(_t(e) for e in (r.get("evidence_ids") or [])), case_name, note, d.get("note", ""),
            "Derived Calculation" if (not seed and m.get("expected_delay_if_occurs_days") is not None) else "",
            f"{TIER_LABEL}: tier {m.get('tier', m.get('impact_class'))}" if seed else "",
            r.get("owner", ""), r.get("trigger", ""), r.get("response_type", ""), r.get("response_action", ""),
            r.get("review_date", "")]])
    return buf.getvalue()
