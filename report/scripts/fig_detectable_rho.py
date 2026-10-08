#!/usr/bin/env python3
"""Figure 7.1: smallest two-sided 5% |rho| detectable at n shared risks (out/critical_rho.csv) with the observed
leave-one-study-out rho values of analysis S4 (analysis/out/s4_leave_one_study_out.csv). Derived Calculation."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
crit = [(int(r["n_shared_risks"]), float(r["critical_abs_rho_two_sided_5pct"])) for r in csv.DictReader(open(ROOT / "report/scripts/out/critical_rho.csv"))]
obs = [(r["study"], r["role"], int(r["n_shared_risks"]), float(r["spearman_rho"])) for r in csv.DictReader(open(ROOT / "analysis/out/s4_leave_one_study_out.csv")) if r["spearman_rho"] and int(r["n_shared_risks"]) >= 5]
fig, ax = plt.subplots(figsize=(6.4, 4.0), dpi=200)
ax.set_facecolor("white")
x = [c[0] for c in crit]; y = [c[1] for c in crit]
ax.fill_between(x, [-v for v in y], y, color="#e8e8e8", label="no significant correlation possible\n(two-sided 5%)")
ax.plot(x, y, color="#555555", lw=1.5); ax.plot(x, [-v for v in y], color="#555555", lw=1.5)
for study, role, n, rho in obs:
    held = role == "held-out"
    ax.scatter(n, rho, s=46, marker="o" if held else "s", color="#0072B2" if held else "#D55E00", zorder=3, edgecolor="white", linewidth=1)
    ax.annotate(study, (n, rho), textcoords="offset points", xytext=(6, 4), fontsize=8, color="#222222")
ax.axhline(0, color="#999999", lw=0.8)
ax.set_xlabel("Number of risks shared with the comparison list (n)", fontsize=9)
ax.set_ylabel("Spearman rho", fontsize=9)
ax.set_ylim(-1.05, 1.05); ax.set_xlim(4, 20.5)
ax.tick_params(labelsize=8)
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.scatter([], [], marker="o", color="#0072B2", label="held-out study vs seed (circle)")
ax.scatter([], [], marker="s", color="#D55E00", label="seed study vs other seed studies (square)")
ax.legend(fontsize=7.5, frameon=False, loc="lower right")
fig.text(0.01, 0.005, "Derived Calculation; 6 comparisons with n >= 5 (S4), 200,000 permutations (n > 8), seed 20261008", fontsize=6.5, color="#555555")
fig.tight_layout(rect=(0, 0.02, 1, 1))
out = ROOT / "report/figures/fig7_1_detectable_rho.png"
fig.savefig(out); print(out)
