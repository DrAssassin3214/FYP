"""Graphical exports of the risk matrix: a colour-coded 5x5 SVG and a standalone, printable HTML report.

Only the ordinal classes already in the result are drawn; nothing is recomputed. Colours are fixed (not theme
dependent) so the file looks the same when pasted into a report or printed.
"""
from __future__ import annotations

from html import escape as esc
from typing import Mapping, Optional

from app.engine.matrix import DEFAULT_LABELS, matrix_level

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
    W, H = x0 + 5 * cw + 30, y0 + 5 * ch + 130
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
            items = cells.get((pc, ic), [])
            per_row = 3
            for k, m in enumerate(items[:9]):
                bw, bh = 34, 20
                cx = x + 10 + (k % per_row) * (bw + 4)
                cy = y + 26 + (k // per_row) * (bh + 4)
                seed = m.get("basis") == "literature-seed"
                dash = ' stroke-dasharray="3 2"' if seed else ""
                label = esc(m["risk_id"].replace("R-", ""))
                o.append(f'<g><title>{esc(m["risk_id"])} – {esc(names.get(m["risk_id"], ""))}'
                         f'{" (literature seed)" if seed else ""} · score {m["score"]} ({esc(m["level"])})</title>'
                         f'<rect x="{cx}" y="{cy}" width="{bw}" height="{bh}" rx="3" fill="#ffffff" stroke="{INK}" stroke-width="1.2"{dash}/>'
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
        " Dashed boxes: placed from the literature seed (survey RII rank), not from entered numbers." if seeded else "")
    o.append(f'<text x="{x0}" y="{ly + 40}" font-size="10.5" fill="{MUTED}">{esc(note)}</text>')
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
            mx = f'<span class="lv" style="background:{FILL[m["level"]]}">{esc(m["level"])}</span> literature seed'
        elif m:
            mx = f'<span class="lv" style="background:{FILL[m["level"]]}">{esc(m["level"])}</span> p{m["p_class"]} × i{m["impact_class"]}'
        else:
            mx = "not placed"
        p, d = r.get("p"), r.get("delay")
        ptxt = f'{p["value"]:g} <small>({esc(p["source"])})</small>' if p else "–"
        dtxt = (f'{d["a"]:g} / {d["m"]:g} / {d["b"]:g} d <small>({esc(d["source"])})</small>' if d and d.get("kind") != "fixed"
                else (f'{d["m"]:g} d <small>({esc(d["source"])})</small>' if d else "–"))
        rows.append(f"<tr><td>{_cell(r['id'])}</td><td>{_cell(r['name'])}</td><td>{_cell(r['category'])}</td>"
                    f"<td>{ptxt}</td><td>{dtxt}</td><td>{mx}</td><td>{_cell(', '.join(r['evidence_ids']))}</td></tr>")
    fired = (result.get("rules") or {}).get("fired") or []
    rules = "".join(f"<li><b>{esc(f['rule_id'])}</b> flags {esc(f.get('risk_id', ''))} as {esc(f['level'])}</li>" for f in fired) \
        or "<li>No rule fired on the facts entered.</li>"
    notes = "".join(f"<li>{esc(w)}</li>" for w in result["warnings"]) or "<li>none</li>"
    cited = sorted({e for r in result["risks"] for e in r["evidence_ids"]})
    refs = "".join(f"<li><b>{esc(e)}</b>: {esc(evidence_index.get(e, 'reference not found in the evidence corpus'))}</li>" for e in cited)
    legend = "".join(f'<span><i style="background:{FILL[k]}"></i>{k} {s["levels"].get(k, 0)}</span>' for k in LEVELS)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Risk register and matrix</title>
<style>
@page {{ size: A4; margin: 14mm; }}
body {{ font: 13px/1.5 "Segoe UI", Arial, sans-serif; color: {INK}; max-width: 1000px; margin: 24px auto; padding: 0 16px; }}
h1 {{ font: 400 30px Georgia, serif; margin: 0 0 4px; }} h2 {{ font-size: 15px; margin: 26px 0 8px; border-bottom: 1px solid #ccc; padding-bottom: 4px; }}
.sub {{ color: {MUTED}; }} table {{ border-collapse: collapse; width: 100%; font-size: 12px; }}
th, td {{ border: 1px solid #d5d5cc; padding: 5px 7px; text-align: left; vertical-align: top; }} th {{ background: #f1f1e8; }}
.lv {{ padding: 1px 7px; border-radius: 2px; font-weight: 600; }} small {{ color: {MUTED}; }}
.legend span {{ margin-right: 16px; }} .legend i {{ display: inline-block; width: 12px; height: 12px; margin-right: 5px; vertical-align: -1px; }}
svg {{ max-width: 100%; height: auto; }} li {{ margin: 2px 0; }}
</style></head><body>
<h1>Risk register and matrix</h1>
<div class="sub">{esc(proj.get('name') or 'Untitled case')}{' · ' + esc(proj.get('location')) if proj.get('location') else ''} ·
Activity: {esc(act.get('name') or '')}{f' · planned {pd["value"]:g} working days ({esc(pd["source"])})' if pd else ''}</div>
<p>{s['n_risks']} risks in the register, {s['n_on_matrix']} placed on the matrix ({s['n_seeded']} from the literature seed).
{s['n_flagged']} flagged as elevated by the site-fact rules.</p>
<h2>Risk matrix</h2>{matrix_svg(result)}<p class="legend">{legend}</p>
<h2>Risk register</h2>
<table><thead><tr><th>ID</th><th>Risk</th><th>Category</th><th>p (Source)</th><th>Delay if it occurs: min / likely / max (Source)</th><th>Matrix</th><th>Evidence</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<h2>Rules that fired</h2><ul>{rules}</ul>
<h2>Notes and limits</h2><ul>{notes}<li>No number here was produced by AI. The matrix is a prioritisation aid, not a quantity.</li></ul>
{f'<h2>Evidence cited</h2><ul>{refs}</ul>' if refs else ''}
</body></html>"""
