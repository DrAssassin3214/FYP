"""Charts for the analysis export (matplotlib PNG, embedded in a self-contained HTML page).

Built only from a run_analysis() result: every plotted value is a field the analysis returned (histogram, summary,
sensitivity, value_at_stake, event_emv, decision, decision_sensitivity).  Nothing is computed here beyond choosing
which returned rows to show.  Each chart carries its Source / Derived Calculation label and, for an ILLUSTRATIVE
case, the ILLUSTRATIVE banner.  The wording never calls a result optimal.

    pngs = chart_pngs(result)            {name: PNG bytes}; a chart whose data is absent is left out
    html = analysis_html(result)         one file: banner, command, charts with captions and data tables, report text
"""
from __future__ import annotations

import base64
import html
import io
from typing import Mapping

MAX_OPTIONS_SHOWN = 10
PREFERRED_WORDING = "preferred under the stated criterion"
ILLUS_TEXT = "ILLUSTRATIVE case: every number is a placeholder, not evidence and not site data"
COLORS = {"light": {"c1": "#2a78d6", "c2": "#eb6834", "ink": "#2b2a28", "muted": "#7d7b76", "grid": "#e6e5df", "crit": "#d03b3b"}}

TITLES = {
    "histogram": "Simulated activity duration",
    "tornado_delay": "Contribution to expected delay, by risk",
    "tornado_cost": "Value at stake (expected cost), by risk",
    "event_emv": "Event EMV per risk",
    "options": "Expected total cost per option",
    "decision_sensitivity": "Preferred option against cost per delay day",
}


def is_illustrative(result: Mapping) -> bool:
    proj = result.get("project") or {}
    return "illustrative" in f"{proj.get('name', '')} {proj.get('notes', '')}".lower()


def _names(result: Mapping) -> dict:
    return {v["risk_id"]: v.get("name") or "" for v in result.get("value_at_stake") or []}


def _risk_label(rid: str, names: Mapping) -> str:
    if rid == "LATENT_PRODUCTIVITY":
        return "Latent productivity factor"
    return f"{rid} {names[rid]}" if names.get(rid) else rid


def option_label(o: Mapping) -> str:
    return " + ".join(o.get("mitigations") or []) or "Accept (no response)"


def options_shown(result: Mapping, limit: int = MAX_OPTIONS_SHOWN) -> list:
    """ACCEPT and the preferred option always, then the admissible options with the lowest total expected cost."""
    opts = (result.get("decision") or {}).get("options") or []
    sel = (result.get("decision") or {}).get("selected_option_id")
    keep = [o for o in opts if o["option_id"] in ("ACCEPT", sel)]
    rest = sorted((o for o in opts if o not in keep and o.get("admissible")), key=lambda o: o["total_expected_cost"])
    keep += rest[: max(0, limit - len(keep))]
    return sorted(keep, key=lambda o: o["total_expected_cost"])


def caption(name: str, result: Mapping) -> str:
    n, seed = result.get("n_used"), result.get("seed")
    cps = ((result.get("event_emv") or [{}])[0]).get("cost_per_day_source") or "see assumptions"
    base = {
        "histogram": f"Derived Calculation of the {n:,} simulated durations (seed {seed}); percentiles from summary.",
        "tornado_delay": f"Derived Calculation: mean delay each risk adds in the simulation ({n:,} runs, seed {seed}).",
        "tornado_cost": f"Derived Calculation: expected cost removed if the risk could not occur (same random draws), cost per day Source: {cps}.",
        "event_emv": f"Derived Calculation: event EMV = p x (expected delay x cost per day + direct cost); cost per day Source: {cps}.",
        "options": f"Derived Calculation on the same random draws for every option; each option is the {PREFERRED_WORDING} only if marked.",
        "decision_sensitivity": "Derived Calculation: the comparison repeated with the cost per delay day scaled, all else fixed.",
    }[name]
    return base + " Input numbers keep the Source label they were entered with."


# ------------------------------------------------------------------------------------------ matplotlib
def _plt():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def _finish(fig, name: str, result: Mapping) -> bytes:
    if is_illustrative(result):
        fig.text(0.01, 0.985, ILLUS_TEXT, ha="left", va="top", fontsize=8, color="#8a5300", fontweight="bold")
    fig.text(0.01, 0.01, caption(name, result)[:150], ha="left", va="bottom", fontsize=6.5, color=COLORS["light"]["muted"])
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130)
    _plt().close(fig)
    return buf.getvalue()


def _fig(name: str, height: float = 3.9):
    plt = _plt()
    fig, ax = plt.subplots(figsize=(7.6, height))
    fig.subplots_adjust(top=0.84, bottom=0.2, left=0.3, right=0.95)
    ax.set_title(TITLES[name], fontsize=11, loc="left", color=COLORS["light"]["ink"])
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="x", color=COLORS["light"]["grid"], linewidth=0.8)
    ax.set_axisbelow(True)
    return fig, ax


def _hbars(result, name, rows, xlabel, color):
    fig, ax = _fig(name, 1.6 + 0.38 * max(len(rows), 1))
    ax.barh([r[0] for r in rows][::-1], [r[1] for r in rows][::-1], color=color)
    for i, r in enumerate(rows[::-1]):
        ax.text(r[1], i, " " + r[2], va="center", fontsize=8, color=COLORS["light"]["ink"])
    ax.set_xlabel(xlabel, fontsize=8)
    ax.tick_params(labelsize=8)
    ax.margins(x=0.18)
    return _finish(fig, name, result)


def chart_pngs(result: Mapping) -> dict:
    """PNG bytes per chart.  A chart whose data the result does not carry is left out."""
    c, out = COLORS["light"], {}
    cur = (result.get("cost") or {}).get("currency", "")
    names = _names(result)

    h, s = result.get("histogram"), result.get("summary") or {}
    if h:
        fig, ax = _fig("histogram")
        e = h["edges"]
        ax.bar(e[:-1], [x * 100 for x in h["share"]], width=[b - a for a, b in zip(e[:-1], e[1:])], align="edge", color=c["c1"], edgecolor="white", linewidth=0.4)
        dl = ((result.get("activity") or {}).get("deadline_days") or {}).get("value")
        marks = [("P50", s.get("percentiles", {}).get("P50"), c["ink"], ":"), ("P90", s.get("percentiles", {}).get("P90"), c["ink"], "--"), ("Deadline", dl, c["crit"], "-")]
        for lab, x, col, ls in marks:
            if x is not None:
                ax.axvline(x, color=col, linestyle=ls, linewidth=1.6, label=f"{lab} {x:.1f} d")
        ax.legend(fontsize=8, frameon=False)
        ax.set_xlabel("Activity duration (working days)", fontsize=8)
        ax.set_ylabel("Share of runs (%)", fontsize=8)
        ax.tick_params(labelsize=8)
        out["histogram"] = _finish(fig, "histogram", result)

    sens = [r for r in result.get("sensitivity") or [] if r.get("mean_contribution_days") is not None]
    if sens:
        rows = sorted(sens, key=lambda r: -r["mean_contribution_days"])
        out["tornado_delay"] = _hbars(result, "tornado_delay",
                                      [(_risk_label(r["risk_id"], names), r["mean_contribution_days"], f"{r['mean_contribution_days']:.2f} d ({r['share_of_expected_delay'] * 100:.0f}%)") for r in rows],
                                      "Mean delay contributed (working days)", c["c1"])
    vas = result.get("value_at_stake") or []
    if vas:
        rows = sorted(vas, key=lambda r: -r["value_at_stake"])
        out["tornado_cost"] = _hbars(result, "tornado_cost",
                                     [(_risk_label(r["risk_id"], names), r["value_at_stake"], f"{r['value_at_stake']:,.0f}") for r in rows], f"Value at stake ({cur})", c["c2"])
    emv = result.get("event_emv") or []
    if emv:
        rows = sorted(emv, key=lambda r: -r["emv"])
        out["event_emv"] = _hbars(result, "event_emv",
                                  [(_risk_label(r["risk_id"], names), r["emv"], f"{r['emv']:,.0f} (p {r['p']:g})") for r in rows], f"Event EMV ({cur})", c["c2"])

    shown = options_shown(result)
    if shown:
        sel = result["decision"].get("selected_option_id")
        fig, ax = _fig("options", 1.8 + 0.4 * len(shown))
        labs = [option_label(o) + (f"  [{PREFERRED_WORDING}]" if o["option_id"] == sel and sel != "ACCEPT" else "") for o in shown][::-1]
        mit = [o["mitigation_cost"] for o in shown][::-1]
        res_ = [o["residual_expected_cost"] for o in shown][::-1]
        ax.barh(labs, mit, color=c["c2"], label="Mitigation cost")
        ax.barh(labs, res_, left=mit, color=c["c1"], label="Residual expected cost")
        for i, o in enumerate(shown[::-1]):
            ax.text(o["total_expected_cost"], i, f" {o['total_expected_cost']:,.0f}" + (" *" if o["option_id"] == sel else ""), va="center", fontsize=8, fontweight="bold" if o["option_id"] == sel else "normal")
        ax.set_xlabel(f"Total expected cost ({cur}); * = {PREFERRED_WORDING}", fontsize=8)
        ax.legend(fontsize=8, frameon=False, loc="lower right")
        ax.tick_params(labelsize=7)
        ax.margins(x=0.15)
        fig.subplots_adjust(left=0.42)
        out["options"] = _finish(fig, "options", result)

    ds = result.get("decision_sensitivity")
    if ds and ds.get("rows"):
        rows = ds["rows"]
        order = []
        for r in rows:
            if r["selected_option_id"] not in order:
                order.append(r["selected_option_id"])
        opts = {o["option_id"]: o for o in result["decision"]["options"]}
        order.sort(key=lambda i: opts[i]["mitigation_cost"] if i in opts else 0)
        fig, ax = _fig("decision_sensitivity", 3.4)
        ax.step([r["cost_per_delay_day"] for r in rows], [order.index(r["selected_option_id"]) for r in rows], where="mid", color=c["c1"], linewidth=1.6)
        for r in rows:
            ax.plot(r["cost_per_delay_day"], order.index(r["selected_option_id"]), "o", color=c["c1"], mfc="white" if r["selected_option_id"] == "ACCEPT" else c["c1"])
        ax.set_yticks(range(len(order)))
        ax.set_yticklabels([option_label(opts[i]) if i in opts else i for i in order], fontsize=7)
        ax.set_xlabel(f"Cost per delay day ({cur}); preferred option under the stated criterion", fontsize=8)
        ax.tick_params(axis="x", labelsize=8)
        ax.grid(axis="y", color=c["grid"], linewidth=0.8)
        fig.subplots_adjust(left=0.42)
        out["decision_sensitivity"] = _finish(fig, "decision_sensitivity", result)
    return out


# ------------------------------------------------------------------------------------------ HTML
def _table(head, rows) -> str:
    th = "".join(f"<th>{html.escape(str(x))}</th>" for x in head)
    tr = "".join("<tr>" + "".join(f"<td>{html.escape(str(x))}</td>" for x in r) + "</tr>" for r in rows)
    return f"<table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>"


def chart_tables(result: Mapping) -> dict:
    """Text alternative for each chart: the returned values behind it."""
    names, s, out = _names(result), result.get("summary") or {}, {}
    dl = ((result.get("activity") or {}).get("deadline_days") or {}).get("value")
    pc = s.get("percentiles") or {}
    out["histogram"] = _table(["Statistic", "Working days"], [(k, f"{pc[k]:.2f}") for k in ("P50", "P80", "P90", "P95") if k in pc]
                              + ([("Deadline", f"{dl:g}"), ("P(duration > deadline)", f"{s['p_exceed_deadline'] * 100:.1f}%")] if dl is not None and "p_exceed_deadline" in s else []))
    out["tornado_delay"] = _table(["Risk", "Mean delay (d)", "Share of expected delay"],
                                  [(_risk_label(r["risk_id"], names), f"{r['mean_contribution_days']:.2f}", f"{r['share_of_expected_delay'] * 100:.1f}%") for r in result.get("sensitivity") or []])
    out["tornado_cost"] = _table(["Risk", "Value at stake"], [(_risk_label(r["risk_id"], names), f"{r['value_at_stake']:,.0f}") for r in result.get("value_at_stake") or []])
    out["event_emv"] = _table(["Risk", "p", "Event EMV"], [(_risk_label(r["risk_id"], names), f"{r['p']:g}", f"{r['emv']:,.0f}") for r in result.get("event_emv") or []])
    sel = (result.get("decision") or {}).get("selected_option_id")
    out["options"] = _table(["Option", "Mitigation cost", "Residual expected cost", "Total expected cost", "Note"],
                            [(option_label(o), f"{o['mitigation_cost']:,.0f}", f"{o['residual_expected_cost']:,.0f}", f"{o['total_expected_cost']:,.0f}",
                              PREFERRED_WORDING if o["option_id"] == sel else "") for o in options_shown(result)])
    ds = result.get("decision_sensitivity")
    if ds:
        out["decision_sensitivity"] = _table(["Multiplier", "Cost per delay day", "Preferred option", "Command"],
                                             [(f"{r['multiplier']:g}x", f"{r['cost_per_delay_day']:,.0f}", r["selected_option_id"], r["command"]) for r in ds["rows"]])
    return out


def analysis_html(result: Mapping) -> str:
    """Self-contained HTML (base64 PNG charts, text tables, the Markdown report text).  Works offline."""
    pngs, tables = chart_pngs(result), chart_tables(result)
    proj = (result.get("project") or {}).get("name") or "untitled case"
    cmd = result["command"]
    parts = [f"<h1>Analysis charts: {html.escape(proj)}</h1>"]
    if is_illustrative(result):
        parts.append(f'<p class="illus"><strong>{ILLUS_TEXT}.</strong></p>')
    parts.append(f"<p><strong>{html.escape(cmd['command'])}</strong>. {html.escape(cmd['reason'])}</p>")
    for name, png in pngs.items():
        b64 = base64.b64encode(png).decode("ascii")
        alt = f"{TITLES[name]}. The values are in the table below the chart."
        parts.append(f'<figure><img alt="{html.escape(alt)}" src="data:image/png;base64,{b64}" style="max-width:100%">'
                     f"<figcaption>{html.escape(caption(name, result))}</figcaption></figure>"
                     f"<details><summary>Data table: {html.escape(TITLES[name])}</summary>{tables[name]}</details>")
    parts.append("<h2>Report text</h2><pre>" + html.escape(result.get("report_markdown") or "") + "</pre>")
    css = ("body{font-family:system-ui,sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem;color:#222}"
           "table{border-collapse:collapse;font-size:.85rem}td,th{border:1px solid #ccc;padding:3px 8px;text-align:left}"
           ".illus{background:#fff5de;border:1px solid #eecb7c;padding:.5rem .8rem}pre{white-space:pre-wrap;font-size:.8rem}"
           "figcaption{font-size:.8rem;color:#555}figure{margin:1.5rem 0 .5rem}")
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f"<title>Analysis charts</title><style>{css}</style></head><body>{''.join(parts)}</body></html>")
