"""Architecture diagrams for Chapter 5 (matplotlib only). Output: report/figures/ch5_*.png"""
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
OUT = Path(__file__).resolve().parents[1] / "figures"
INK, PAPER, ACC, GREY = "#1a1a1a", "#fbfaf5", "#8a4b00", "#e8e6dc"

def box(ax, x, y, w, h, text, fc=PAPER, ec=INK, fs=8.5, bold=False, ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.01", fc=fc, ec=ec, lw=1.1, ls=ls))
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=fs, color=INK, weight="bold" if bold else "normal", wrap=True)
def arrow(ax, p, q, text=None, ls="-"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=11, lw=1.1, color=INK, ls=ls))
    if text: ax.text((p[0]+q[0])/2, (p[1]+q[1])/2 + 0.012, text, ha="center", fontsize=7, color=ACC)
def canvas(w, h):
    fig, ax = plt.subplots(figsize=(w, h)); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off"); fig.patch.set_facecolor("white"); return fig, ax

# 1. layered architecture
fig, ax = canvas(9, 6.2)
ax.text(0.5, 0.97, "Layers of the tool (all on one computer, no network use for the core path)", ha="center", fontsize=10, weight="bold")
box(ax, 0.03, 0.80, 0.94, 0.12, "Presentation: gui/static (HTML, CSS, JavaScript modules; 7 screens)  |  hosted either in a browser tab (python -m gui)\nor in a Qt WebEngine window (gui/qt_app.py, PySide6) - same files, same server", fc=GREY, fs=8.5)
box(ax, 0.03, 0.60, 0.94, 0.14, "HTTP layer: gui/api.py (Flask, 127.0.0.1 only)\n/api/validate, /run, /report, /register-csv, /analyze, /suggest-risks, /evidence, /settings\nBad input gives HTTP 200 with ok:false or HTTP 422, not a stack trace", fc=GREY, fs=8.3)
box(ax, 0.03, 0.30, 0.45, 0.26, "Core (identification, register, matrix)\napp/service.py  parse_case -> run_case\napp/engine/rules.py  rule evaluation\napp/engine/matrix.py  classes and levels\napp/literature_seed.py  tier from RII\napp/reporting/*  md / csv / html / svg", fs=8.2, bold=False)
box(ax, 0.52, 0.30, 0.45, 0.26, "Optional decision layer\napp/analysis.py  run_analysis\napp/engine/simulation.py  Monte Carlo\napp/engine/emv.py  event EMV, cost\napp/engine/decision.py, options.py\ncommand: AUTHORIZE / ACCEPT ...", fs=8.2, ls="--")
box(ax, 0.03, 0.06, 0.28, 0.17, "AI evidence layer\napp/ai_layer/*\nretrieval, guard G1-G9,\nclients (Claude, Gemini)", fs=8)
box(ax, 0.36, 0.06, 0.28, 0.17, "Data files (JSON)\nrisk library, rules, literature seed,\nmitigation catalogue", fs=8)
box(ax, 0.69, 0.06, 0.28, 0.17, "Evidence corpus\nLiterature_Evidence_Package.xlsx,\nResearch_Notes/ (472 records)", fs=8)
for x in (0.25, 0.75): arrow(ax, (x, 0.78), (x, 0.74)); 
arrow(ax, (0.25, 0.60), (0.25, 0.56)); arrow(ax, (0.75, 0.60), (0.75, 0.56))
arrow(ax, (0.17, 0.23), (0.17, 0.30)); arrow(ax, (0.40, 0.23), (0.30, 0.30)); arrow(ax, (0.60, 0.23), (0.70, 0.30))
fig.savefig(OUT/"ch5_architecture_layers.png", dpi=170, bbox_inches="tight", facecolor="white"); plt.close(fig)

# 2. data flow of run_case
fig, ax = canvas(9.5, 5.4)
ax.text(0.5, 0.97, "Data flow of one edit: the interface sends the case, the service returns the register and matrix", ha="center", fontsize=10, weight="bold")
steps = [("Case JSON\n(project, activity,\nfacts, risks,\nimpact edges)", 0.02, 0.62), ("parse_case\ntype checks, Source\nrequired on numbers,\nproblems list", 0.215, 0.62), ("evaluate_rules\n22 rules on facts\nflag / not evaluable", 0.41, 0.62), ("classify\np class, impact class,\nscore, level\n(entered numbers)", 0.605, 0.62), ("seed_for\nliterature tier for risks\nwithout numbers\n(+1 if rule-flagged)", 0.80, 0.62)]
for t, x, y in steps: box(ax, x, y, 0.17, 0.26, t, fs=8)
for i in range(4): arrow(ax, (0.02+0.17+0.195*i+0.005, 0.75), (0.215+0.195*i-0.005, 0.75))
box(ax, 0.20, 0.26, 0.60, 0.18, "Result object: risks, matrix rows, summary (levels, counts),\nmatrix_settings (edges, thresholds, Source), rules (fired / not evaluable),\nwarnings, report_markdown, matrix_svg", fs=8.3, bold=False)
arrow(ax, (0.885, 0.62), (0.70, 0.44)); arrow(ax, (0.50, 0.62), (0.50, 0.44))
box(ax, 0.03, 0.04, 0.22, 0.14, "Screens (register, matrix,\nKPI strip, problems)", fs=8, fc=GREY)
box(ax, 0.30, 0.04, 0.22, 0.14, "register.md, register.csv,\nreport.html, matrix.svg/png", fs=8, fc=GREY)
box(ax, 0.57, 0.04, 0.18, 0.14, "Save: case JSON\n(the input, not the result)", fs=7.5, fc=GREY)
box(ax, 0.80, 0.04, 0.17, 0.14, "run_analysis\n(optional, needs\ncost inputs)", fs=8, ls="--")
for x in (0.14, 0.41, 0.885): arrow(ax, (min(max(x,0.30),0.70), 0.26), (x, 0.18))
ax.text(0.5, 0.0, "Problems found at parse time stop the run; the GUI then keeps the last valid result and shows the problem.", ha="center", fontsize=7.2, style="italic")
fig.savefig(OUT/"ch5_dataflow_run_case.png", dpi=170, bbox_inches="tight", facecolor="white"); plt.close(fig)

# 3. AI guard flow
fig, ax = canvas(9.5, 4.8)
ax.text(0.5, 0.96, "AI evidence layer: what may cross from the model to the register", ha="center", fontsize=10, weight="bold")
box(ax, 0.02, 0.60, 0.17, 0.25, "Activity name +\nquery", fs=8.5)
box(ax, 0.23, 0.60, 0.17, 0.25, "Offline retrieval\n(token overlap) over\nthe evidence store:\ntop k records", fs=8)
box(ax, 0.44, 0.60, 0.17, 0.25, "Prompt built from\nthose records only\n(no numbers asked)", fs=8)
box(ax, 0.65, 0.60, 0.15, 0.25, "LLM\n(Claude or Gemini,\nkey optional)", fs=8, ls="--")
box(ax, 0.84, 0.60, 0.14, 0.25, "raw JSON\nreply", fs=8.5)
for a, b in [(0.19, 0.23), (0.40, 0.44), (0.61, 0.65), (0.80, 0.84)]: arrow(ax, (a, 0.725), (b, 0.725))
box(ax, 0.10, 0.20, 0.80, 0.26, "parse_and_validate (guard)\nG8 shape check | G7 reject numbers in text | G2, G9 strip numeric keys\nG1 cited ids must be retrieved and in the store | G3 quotes must appear in the cited record\nG4 status stays AI-unverified | G5 prompt, model, ids, raw output logged", fs=8.3, fc=GREY)
arrow(ax, (0.91, 0.60), (0.80, 0.44))
box(ax, 0.05, 0.02, 0.40, 0.12, "Candidate: name, category, mechanism,\nvalid evidence ids, issues (no numbers)", fs=8)
box(ax, 0.55, 0.02, 0.40, 0.12, "Rejected items and stripped fields:\nlogged, never shown as values", fs=8, ls="--")
arrow(ax, (0.30, 0.22), (0.25, 0.14)); arrow(ax, (0.70, 0.22), (0.75, 0.14))
fig.savefig(OUT/"ch5_ai_guard_flow.png", dpi=170, bbox_inches="tight", facecolor="white"); plt.close(fig)

# 4. matrix decision flow
fig, ax = canvas(9.5, 4.6)
ax.text(0.5, 0.96, "Placement of one register risk on the matrix (priority of bases)", ha="center", fontsize=10, weight="bold")
box(ax, 0.35, 0.80, 0.30, 0.10, "Risk in register", fs=9, bold=True)
box(ax, 0.02, 0.48, 0.42, 0.22, "p AND delay entered (plus planned duration and edges):\np class from p; impact class from E[delay] / planned\nscore = p class x impact class; level\n(counted in the level totals)", fs=8)
box(ax, 0.55, 0.48, 0.44, 0.22, "Numbers not entered, library risk has a seed value:\ntier from RII rank (5 bands of 6) used on BOTH axes;\n+1 on p class if a rule flags it (cap 5)\nshown as 'literature tier (Assumption)'; not counted", fs=8)
box(ax, 0.30, 0.12, 0.40, 0.18, "Numbers not entered, no seed value (16 of 46 library\nrisks, and all custom risks): stays in the register,\noff the matrix, with a note", fs=8, ls="--")
arrow(ax, (0.45, 0.80), (0.22, 0.68)); arrow(ax, (0.55, 0.80), (0.78, 0.68)); arrow(ax, (0.60, 0.50), (0.55, 0.30), "no seed")
fig.savefig(OUT/"ch5_matrix_placement.png", dpi=170, bbox_inches="tight", facecolor="white"); plt.close(fig)
