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


def _basis(r: Mapping, m: Optional[Mapping]) -> str:
    if m and m.get("basis") == "literature-seed":
        return "literature seed (RII class, not a probability)"
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
          f"- Placed on the matrix: **{s['n_on_matrix']}**"
          + (" (" + ", ".join(f"{s['levels'][k]} {k}" for k in LEVELS if s["levels"].get(k)) + ")" if s["n_on_matrix"] else ""),
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
                mx=_md((f"{m['level']} (p{m['p_class']} x i{m['impact_class']})" + (" [literature seed]" if m.get("basis") == "literature-seed" else "")) if m else "not placed"),
                ev=_md(", ".join(_t(e) for e in (r.get("evidence_ids") or [])) or "none")))
    else:
        L.append("No risks in the register.")
    L.append("")

    L += ["## Risk matrix", ""]
    if matrix:
        cells: dict[tuple[int, int], list[str]] = {}
        for m in matrix.values():
            cells.setdefault((m["p_class"], m["impact_class"]), []).append(m["risk_id"])
        L += ["Probability class (rows) by impact class (columns). Impact is the expected delay if the risk occurs, as a "
              "fraction of the planned duration, binned by the edges you entered. Ordinal prioritisation only.", "",
              "| p class \\ impact | 1 | 2 | 3 | 4 | 5 |", "|---|---|---|---|---|---|"]
        for pc in range(5, 0, -1):
            L.append(f"| {pc} | " + " | ".join(
                _SQUARE[matrix_level(pc, ic)] + " " + (", ".join(_md(x) for x in cells.get((pc, ic), [])) or "") for ic in range(1, 6)) + " |")
        L += ["", "Colour key: " + "  ".join(f"{_SQUARE[k]} {k}" for k in LEVELS)]
        L += ["", "| Risk | p | p class | Expected delay (d) | Impact class | Score | Level |", "|---|---|---|---|---|---|---|"]
        for m in sorted(matrix.values(), key=lambda x: -x["score"]):
            seed = m.get("basis") == "literature-seed"
            L.append(f"| {_md(m['risk_id'])} | {'literature seed' if seed else format(m['p'], 'g')} | {m['p_class']} | "
                     f"{'literature seed' if seed else format(m['expected_delay_if_occurs_days'], '.2f')} | "
                     f"{m['impact_class']} | {m['score']} | {m['level']} |")
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
        L += [f"- {s['n_seeded']} risk(s) marked ""literature seed"" have no probability or delay entered. Their matrix "
              "cell is a relative ranking from survey Relative Importance Index values in the evidence store (the rank band "
              "is used for both axes; a rule flag raises the probability class by one). An importance index is neither a "
              "probability nor a delay, so treat these cells as a starting point and replace them with your own numbers."]
    L += ["- Probabilities and delays are inputs from you, site records or cited sources, each labelled with its Source. "
          "No number here was produced by AI.",
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
    literature seed (RII class, not a probability); 'case'/'note' carry the ILLUSTRATIVE flag."""
    matrix = {m["risk_id"]: m for m in result["matrix"]}
    case_name = _t((result.get("project") or {}).get("name"))
    note = "ILLUSTRATIVE: placeholder numbers, not evidence" if _is_illustrative(result) else ""
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["id", "name", "category", "status", "basis", "p", "p_source", "delay_kind", "delay_min",
                "delay_most_likely", "delay_max", "delay_source", "expected_delay_days", "p_class", "impact_class",
                "score", "level", "evidence_ids", "case", "note"])
    for r in result["risks"]:
        p, d, m = r.get("p") or {}, r.get("delay") or {}, matrix.get(r["id"]) or {}
        seed = m.get("basis") == "literature-seed"
        w.writerow([_csv_safe(x) for x in [
            r["id"], r["name"], r["category"], r["status"], _basis(r, m or None),
            p.get("value", ""), p.get("source", ""), d.get("kind", ""), d.get("a", ""), d.get("m", ""), d.get("b", ""),
            d.get("source", ""), "" if seed else m.get("expected_delay_if_occurs_days", ""), m.get("p_class", ""),
            m.get("impact_class", ""), m.get("score", ""), m.get("level", ""),
            ";".join(_t(e) for e in (r.get("evidence_ids") or [])), case_name, note]])
    return buf.getvalue()
