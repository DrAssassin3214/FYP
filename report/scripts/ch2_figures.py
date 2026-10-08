"""Figures for Chapter 2. Inputs: docs/Corpus_Statistical_Analysis.md (section 6a, values copied below) and
data/literature_seed.json (rows per study). Output: report/figures/fig2_*.png. Source label: Derived Calculation."""
import json, collections, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = pathlib.Path(__file__).resolve().parents[2]
out = root / "report" / "figures"
out.mkdir(exist_ok=True)

# Figure 2.1: share of corpus abstracts that mention each method (docs/Corpus_Statistical_Analysis.md, section 6a)
methods = [
    ("Questionnaire / survey", 46.9, 45.4, 48.5),
    ("Interview / Delphi / expert panel", 16.8, 15.7, 18.0),
    ("Systematic / literature review", 15.8, 14.7, 17.0),
    ("Case study", 15.2, 14.1, 16.4),
    ("Relative importance index (RII)", 10.6, 9.7, 11.6),
    ("Fuzzy logic / fuzzy AHP", 6.2, 5.5, 7.0),
    ("Machine learning / neural network", 5.7, 5.0, 6.5),
    ("AHP / MCDM", 4.3, 3.7, 5.0),
    ("Structural equation modelling", 2.9, 2.4, 3.5),
    ("Large language model / generative AI", 0.4, 0.2, 0.6),
]
methods = methods[::-1]
fig, ax = plt.subplots(figsize=(7.2, 4.0), dpi=200)
y = range(len(methods))
vals = [m[1] for m in methods]
err = [[m[1] - m[2] for m in methods], [m[3] - m[1] for m in methods]]
ax.barh(list(y), vals, xerr=err, color="#4c6a92", ecolor="#222222", capsize=2, height=0.62)
ax.set_yticks(list(y))
ax.set_yticklabels([m[0] for m in methods], fontsize=8)
for i, v in enumerate(vals):
    ax.text(v + 1.8, i, f"{v:.1f}%", va="center", fontsize=7.5)
ax.set_xlabel("Share of the 3,975 screened works whose title/abstract mentions the term (%)", fontsize=8)
ax.set_xlim(0, 56)
ax.tick_params(axis="x", labelsize=8)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(out / "fig2_methods_share.png")
plt.close(fig)

# Figure 2.2: seed rows entered per study, by role
d = json.load(open(root / "data" / "literature_seed.json"))
role = {s["id"]: s["role"] for s in d["studies"]}
cnt = collections.Counter(r["study"] for r in d["rows"])
order = ["M06", "M01", "A02", "A14", "A15", "M10", "M15", "M14", "A10", "A21", "HAS25"]
fig, ax = plt.subplots(figsize=(7.2, 3.4), dpi=200)
cols = ["#4c6a92" if role[k] == "seed" else "#c98b3c" for k in order]
ax.bar(order, [cnt[k] for k in order], color=cols)
for i, k in enumerate(order):
    ax.text(i, cnt[k] + 0.8, str(cnt[k]), ha="center", fontsize=8)
ax.set_ylabel("RII rows entered", fontsize=8)
ax.tick_params(labelsize=8)
ax.set_ylim(0, 48)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color="#4c6a92", label="seed study (builds the starting order)"),
                   Patch(color="#c98b3c", label="held-out study (comparison only)")], fontsize=7.5, frameon=False, loc="upper right")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(out / "fig2_rows_per_study.png")
plt.close(fig)
print(dict(cnt), sum(cnt.values()))
