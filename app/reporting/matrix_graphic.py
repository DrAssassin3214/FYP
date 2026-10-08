"""Graphical exports of the risk matrix: a colour-coded 5x5 SVG and a standalone, printable HTML report.

Only the ordinal classes already in the result are drawn; nothing is recomputed. Colours are fixed (not theme
dependent) so the file looks the same when pasted into a report or printed.
"""
from __future__ import annotations

from html import escape as _esc
from typing import Mapping, Optional

from app.engine.matrix import DEFAULT_LABELS, matrix_level
from app.reporting.register_report import (AI_NOTE, CLASS1_NOTE, SEED_NOTE, TIER_LABEL, _is_illustrative, _mx_text,
                                           _response_rows, settings_text)

def esc(v) -> str:
    """HTML-escape any value (None -> empty, non-strings coerced) so odd types never raise."""
    return _esc("" if v is None else str(v))


FILL = {"Low": "#4fcf6f", "Moderate": "#ffd93d", "High": "#ff9626", "Extreme": "#ff4b4b"}
INK = "#1a1a17"
MUTED = "#6b6b62"
LEVELS = ("Low", "Moderate", "High", "Extreme")


def matrix_svg(result: Mapping) -> str:
    matrix = result.get("matrix") or []
    names = {r["id"]: r.get("name") or r["id"] for r in result.get("risks", [])}
    cells: dict[tuple[int, int], list[dict]] = {}
    for m in matrix:
        cells.setdefault((m["p_class"], m["impact_class"]), []).append(m)

    x0, y0, cw, ch = 150, 78, 120, 84                    # grid origin and cell size
    W, H = x0 + 5 * cw + 30, y0 + 5 * ch + 146
    title = (result.get("project") or {}).get("name") or "Untitled case"
    act = (result.get("activity") or {}).get("name") or ""
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
         f'font-family="Segoe UI, Arial, sans-serif" role="img" aria-label="Risk matrix, probability class by impact class">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="24" y="34" font-size="20" font-weight="600" fill="{INK}">Risk matrix</text>',
         f'<text x="24" y="56" font-size="12.5" fill="{MUTED}">{esc(title)}{" · " + esc(act) if act else ""}</text>']

    for pc in range(5, 0, -1):
        y = y0 + (5 - pc) * ch
        o.append(f'<text x="{x0 - 14}" y="{y + ch / 2 - 2}" font-size="13" font-weight="600" text-anchor="end" fill="{INK}">{pc}</text>')
        o.append(f'<text x="{x0 - 14}" y="{y + ch / 2 + 14}" font-size="10.5" text-anchor="end" fill="{MUTED}">{esc(DEFAULT_LABELS[pc - 1])}</text>')
        for ic in range(1, 6):
            x = x0 + (ic - 1) * cw
            lvl = matrix_level(pc, ic)
            o.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" fill="{FILL[lvl]}" stroke="#ffffff" stroke-width="3"/>')
            o.append(f'<text x="{x + cw - 9}" y="{y + 16}" font-size="9.5" text-anchor="end" fill="{INK}" fill-opacity=".55">{lvl}</text>')
            if pc == 1 and ic in (4, 5):
                o.append(f'<g><title>Review: the level is capped by the scoring rule (probability class 1 is Low whatever the impact)</title>'
                         f'<path d="M{x + cw - 3} {y + ch - 3} L{x + cw - 3} {y + ch - 20} L{x + cw - 20} {y + ch - 3} Z" fill="{INK}" fill-opacity=".35"/></g>')
            items = cells.get((pc, ic), [])
            per_row = 3
            for k, m in enumerate(items[:9]):
                bw, bh = 34, 20
                cx = x + 10 + (k % per_row) * (bw + 4)
                cy = y + 26 + (k // per_row) * (bh + 4)
                seed = m.get("basis") == "literature-seed"
                dash = ' stroke-dasharray="3 2"' if seed else ""
                chip_fill = "#d9d9d0" if seed else "#ffffff"
                label = esc(str(m["risk_id"]).replace("R-", ""))
                what = f"{TIER_LABEL}, not an assessed level · score {m['score']}" if seed else f"score {m['score']} ({m['level']})"
                o.append(f'<g><title>{esc(m["risk_id"])} – {esc(names.get(m["risk_id"], ""))} · {esc(what)}</title>'
                         f'<rect x="{cx}" y="{cy}" width="{bw}" height="{bh}" rx="3" fill="{chip_fill}" stroke="{INK}" stroke-width="1.2"{dash}/>'
                         f'<text x="{cx + bw / 2}" y="{cy + 14}" font-size="10.5" font-weight="600" text-anchor="middle" fill="{INK}">{label}</text></g>')
            if len(items) > 9:
                o.append(f'<text x="{x + 10}" y="{y + ch - 6}" font-size="10" fill="{INK}">+{len(items) - 9} more</text>')

    for ic in range(1, 6):
        o.append(f'<text x="{x0 + (ic - 1) * cw + cw / 2}" y="{y0 + 5 * ch + 20}" font-size="13" font-weight="600" text-anchor="middle" fill="{INK}">{ic}</text>')
    o.append(f'<text x="{x0 + 2.5 * cw}" y="{y0 + 5 * ch + 40}" font-size="12" text-anchor="middle" fill="{INK}">Impact class (expected delay if it occurs ÷ planned duration)</text>')
    o.append(f'<text transform="translate(28 {y0 + 2.5 * ch}) rotate(-90)" font-size="12" text-anchor="middle" fill="{INK}">Probability class</text>')

    ly = y0 + 5 * ch + 66
    for i, lv in enumerate(LEVELS):
        lx = x0 + i * 112
        o.append(f'<rect x="{lx}" y="{ly}" width="16" height="16" fill="{FILL[lv]}"/><text x="{lx + 22}" y="{ly + 13}" font-size="12" fill="{INK}">{lv}</text>')
    seeded = (result.get("summary") or {}).get("n_seeded", 0)
    note = "Ordinal prioritisation only – a label, not a quantity." + (
        f" Grey dashed boxes: {TIER_LABEL}, placed from the survey RII rank, not from entered numbers; the cell colour is not an assessed level." if seeded else "")
    o.append(f'<text x="{x0}" y="{ly + 40}" font-size="10.5" fill="{MUTED}">{esc(note)}</text>')
    o.append(f'<text x="{x0}" y="{ly + 56}" font-size="10.5" fill="{MUTED}">Dark corner: probability class 1 is always Low whatever the impact (Assumption: level = p class x impact class, thresholds 5 / 10 / 15).</text>')
    o.append("</svg>")
    return "".join(o)


def _cell(v) -> str:
    return esc("" if v is None else str(v))


def register_html(result: Mapping, evidence_index: Optional[Mapping[str, str]] = None) -> str:
    """Standalone HTML report: graphical matrix, register table, rule flags and notes. Prints cleanly (A4)."""
    evidence_index = evidence_index or {}
    proj, act = result.get("project") or {}, result.get("activity") or {}
    s = result["summary"]
    pd = act.get("planned_duration_days")
    matrix = {m["risk_id"]: m for m in result["matrix"]}
    rows = []
    for r in result["risks"]:
        m = matrix.get(r["id"])
        if m and m.get("basis") == "literature-seed":
            mx = f'<span class="lv tier">{esc(_mx_text(m))}</span>'
        elif m:
            mx = f'<span class="lv" style="background:{FILL[m["level"]]}">{esc(m["level"])}</span> p{m["p_class"]} × i{m["impact_class"]}'
        else:
            mx = "not placed"
        p, d = r.get("p"), r.get("delay")
        ptxt = f'{p["value"]:g} <small>({esc(p["source"])})</small>' if p else "–"
        dtxt = (f'{d["a"]:g} / {d["m"]:g} / {d["b"]:g} d <small>({esc(d["source"])})</small>' if d and d.get("kind") != "fixed"
                else (f'{d["m"]:g} d <small>({esc(d["source"])})</small>' if d else "–"))
        rows.append(f"<tr><td>{_cell(r['id'])}</td><td>{_cell(r['name'])}</td><td>{_cell(r['category'])}</td>"
                    f"<td>{ptxt}</td><td>{dtxt}</td><td>{mx}</td><td>{_cell(', '.join(str(e) for e in (r.get('evidence_ids') or [])))}</td></tr>")
    fired = (result.get("rules") or {}).get("fired") or []
    rules = "".join(f"<li><b>{esc(f['rule_id'])}</b> flags {esc(f.get('risk_id', ''))} as {esc(f['level'])}</li>" for f in fired) \
        or "<li>No rule fired on the facts entered.</li>"
    notes = "".join(f"<li>{esc(w)}</li>" for w in result["warnings"]) or "<li>none</li>"
    cited = sorted({str(e) for r in result["risks"] for e in (r.get("evidence_ids") or [])})
    refs = "".join(f"<li><b>{esc(e)}</b>: {esc(evidence_index.get(e, 'reference not found in the evidence corpus'))}</li>" for e in cited)
    resp = _response_rows(result["risks"])
    resp_html = ("<table><thead><tr><th>ID</th><th>Owner</th><th>Early-warning sign (trigger)</th><th>Response type</th><th>Response action</th><th>Review date</th></tr></thead><tbody>"
                 + "".join(f"<tr><td>{_cell(r['id'])}</td><td>{_cell(r.get('owner'))}</td><td>{_cell(r.get('trigger'))}</td><td>{_cell(r.get('response_type'))}</td>"
                           f"<td>{_cell(r.get('response_action'))}</td><td>{_cell(r.get('review_date'))}</td></tr>" for r in resp)
                 + "</tbody></table>") if resp else "<p>No owner, trigger or response entered yet.</p>"
    hc = result.get("high_consequence") or []
    hc_html = (f"<p>{esc(CLASS1_NOTE)}</p>" + ("<table><thead><tr><th>Risk</th><th>p (as entered)</th><th>p class</th><th>Level</th></tr></thead><tbody>"
               + "".join(f"<tr><td>{_cell(x['risk_id'])}</td><td>{x['p']:g}</td><td>{x['p_class']}</td><td>{_cell(x['level'])}</td></tr>" for x in hc)
               + "</tbody></table>" if hc else "<p>No risk with entered numbers is in impact class 5.</p>"))
    seed_note = f"<li>{esc(SEED_NOTE)}</li>" if s.get("n_seeded") else ""
    legend = "".join(f'<span><i style="background:{FILL[k]}"></i>{k} {s["levels"].get(k, 0)}</span>' for k in LEVELS)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Risk register and matrix</title>
<style>
@page {{ size: A4; margin: 14mm; }}
body {{ font: 13px/1.5 "Segoe UI", Arial, sans-serif; color: {INK}; max-width: 1000px; margin: 24px auto; padding: 0 16px; }}
h1 {{ font: 400 30px Georgia, serif; margin: 0 0 4px; }} h2 {{ font-size: 15px; margin: 26px 0 8px; border-bottom: 1px solid #ccc; padding-bottom: 4px; }}
.sub {{ color: {MUTED}; }} table {{ border-collapse: collapse; width: 100%; font-size: 12px; }}
th, td {{ border: 1px solid #d5d5cc; padding: 5px 7px; text-align: left; vertical-align: top; }} th {{ background: #f1f1e8; }}
.lv {{ padding: 1px 7px; border-radius: 2px; font-weight: 600; }} .lv.tier {{ background: #e6e6df; font-weight: 400; border: 1px dashed {MUTED}; }} small {{ color: {MUTED}; }}
.legend span {{ margin-right: 16px; }} .legend i {{ display: inline-block; width: 12px; height: 12px; margin-right: 5px; vertical-align: -1px; }}
svg {{ max-width: 100%; height: auto; }} li {{ margin: 2px 0; }}
</style></head><body>
<h1>Risk register and matrix</h1>
{'<p><b>ILLUSTRATIVE case: every number is a placeholder, not evidence and not site data.</b></p>' if _is_illustrative(result) else ''}
<div class="sub">{esc(proj.get('name') or 'Untitled case')}{' · ' + esc(proj.get('location')) if proj.get('location') else ''} ·
Activity: {esc(act.get('name') or '')}{f' · planned {pd["value"]:g} working days ({esc(pd["source"])})' if pd else ''}</div>
<p>{s['n_risks']} risks in the register, {s['n_on_matrix']} placed on the matrix: {s['n_seeded']} at a {esc(TIER_LABEL)} (survey ranking, not entered numbers) and {s.get('n_on_matrix_entered', s['n_on_matrix'] - s['n_seeded'])} from entered numbers.
{s['n_flagged']} flagged as elevated by the site-fact rules.</p>
<h2>Risk matrix</h2>{matrix_svg(result)}<p class="legend">{legend}</p>
<p class="sub">{esc(settings_text(result))}</p>
<h2>Risk register</h2>
<table><thead><tr><th>ID</th><th>Risk</th><th>Category</th><th>p (Source)</th><th>Delay if it occurs: min / likely / max (Source)</th><th>Matrix</th><th>Evidence</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<h2>Responses</h2>{resp_html}
<h2>High-consequence list</h2>{hc_html}
<h2>Rules that fired</h2><ul>{rules}</ul>
<h2>Notes and limits</h2><ul>{notes}{seed_note}<li>{esc(AI_NOTE)}</li><li>The matrix is a prioritisation aid, not a quantity.</li></ul>
{f'<h2>Evidence cited</h2><ul>{refs}</ul>' if refs else ''}
</body></html>"""
