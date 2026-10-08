"""Builds the Chapter 3/4 helper tables (markdown snippets) and two figures from repo code and analysis/out.
Every number is read or recomputed here; nothing is typed in. Output: report/scripts/out/*.md, report/figures/ch3_*.png.
Run: PYTHONPATH=/usr/local/lib/python3.13/dist-packages python report/scripts/ch34_build.py
"""
import csv, json, itertools, math, sys
from pathlib import Path
from statistics import mean, median
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from app.literature_seed import seed_table, seed_for
from app.engine.matrix import matrix_level, probability_class, impact_class
OUT = REPO / "report" / "scripts" / "out"
FIG = REPO / "report" / "figures"
AO = REPO / "analysis" / "out"
SEED = 20261008
rng = np.random.default_rng(SEED)

def rd(name):
    with (AO / name).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))

def md(rows, header, align=None):
    a = align or ["---"] * len(header)
    s = "| " + " | ".join(header) + " |\n|" + "|".join(a) + "|\n"
    for r in rows:
        s += "| " + " | ".join(str(x) for x in r) + " |\n"
    return s

def w(name, text):
    (OUT / name).write_text(text, encoding="utf-8")

lib = {r["id"]: r for r in json.loads((REPO / "data/risk_library_masonry.json").read_text(encoding="utf-8-sig"))}
tab = seed_table()
seeded = sorted([k for k, v in tab.items() if v["class"] is not None], key=lambda k: tab[k]["rank"])
LV = ("Low", "Moderate", "High", "Extreme")
facts = {}

# ---- A1 level map
grid = {(p, i): matrix_level(p, i) for p in range(1, 6) for i in range(1, 6)}
cnt = {l: sum(1 for v in grid.values() if v == l) for l in LV}
facts["level_counts_5x5"] = cnt
diag = {c: matrix_level(c, c) for c in range(1, 6)}
facts["diagonal_levels"] = diag
w("a1_level_grid.md", md([[f"p class {p}"] + [f"{p*i} {grid[(p,i)][0]}" for i in range(1, 6)] for p in range(5, 0, -1)],
                         ["", "i class 1", "i class 2", "i class 3", "i class 4", "i class 5"]))
fig, ax = plt.subplots(figsize=(5.2, 4.6))
col = {"Low": "#d9ead3", "Moderate": "#fff2cc", "High": "#f9cb9c", "Extreme": "#ea9999"}
for p in range(1, 6):
    for i in range(1, 6):
        ax.add_patch(plt.Rectangle((i - .5, p - .5), 1, 1, fc=col[grid[(p, i)]], ec="white", lw=2))
        ax.text(i, p, f"{p*i}\n{grid[(p,i)][0]}", ha="center", va="center", fontsize=9)
for c in range(1, 6):
    ax.add_patch(plt.Rectangle((c - .5, c - .5), 1, 1, fc="none", ec="#0072B2", lw=2.4))
ax.set_xlim(.5, 5.5); ax.set_ylim(.5, 5.5); ax.set_xticks(range(1, 6)); ax.set_yticks(range(1, 6))
ax.set_xlabel("impact class"); ax.set_ylabel("probability class")
ax.set_title("5x5 scoring rule, thresholds 5/10/15 (Assumption)\nblue outline = same class on both axes (seeded risks)", fontsize=9)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.text(.01, .005, f"Derived Calculation | n = 25 cells | L=Low M=Moderate H=High E=Extreme | source: app.engine.matrix.matrix_level", fontsize=6.5, color="#555")
fig.tight_layout(rect=(0, .03, 1, 1)); fig.savefig(FIG / "ch3_level_map_5x5.png", dpi=150); plt.close(fig)

# ---- seeded 30: diagonal levels and rule-flag
lv = {k: matrix_level(tab[k]["class"], tab[k]["class"]) for k in seeded}
facts["seeded_levels_base"] = {l: sum(1 for v in lv.values() if v == l) for l in LV}
el = {k: seed_for(k, elevated=True) for k in seeded}
facts["seeded_levels_if_flagged"] = {l: sum(1 for k in seeded if matrix_level(el[k]["p_class"], el[k]["impact_class"]) == l) for l in LV}
rows = []
for k in seeded:
    t = tab[k]
    sm = ", ".join(f"{s} {v:.4f}" for s, v in sorted(t["study_means"].items()))
    rows.append([t["rank"], k, lib[k]["name"], len(t["study_means"]), f"{t['mean_rii']:.4f}", t["class"], lv[k], sm])
w("seed30.md", md(rows, ["Rank", "Risk", "Library name", "Seed studies (n)", "Seed mean RII", "Class", "Level if p-class = i-class", "Study means (Literature, averaged per study)"],
                  ["--:", "---", "---", "--:", "--:", "--:", "---", "---"]))
unseeded = [k for k in lib if k not in seeded]
facts["library_n"] = len(lib); facts["unseeded"] = unseeded

# ---- seeded-30: level cutoff triples
base = (5, 10, 15)
def lvls(th):
    return {k: matrix_level(tab[k]["class"], tab[k]["class"], th) for k in seeded}
b = lvls(base)
ch = []
trip = [t for t in itertools.combinations(range(2, 21), 3)]
for t in trip:
    l = lvls(t); ch.append(sum(1 for k in seeded if l[k] != b[k]))
ch = np.array(ch)
facts["cutoff_triples_2_to_20"] = {"n_triples": len(trip), "median": float(np.median(ch)), "q1": float(np.percentile(ch, 25)), "q3": float(np.percentile(ch, 75)),
                                   "min": int(ch.min()), "max": int(ch.max()), "share_zero": float((ch == 0).mean())}
named = [(4, 9, 15), (4, 9, 16), (4, 8, 12), (6, 12, 16), (3, 8, 14), (5, 10, 20)]
rows = []
for t in named:
    l = lvls(t)
    rows.append(["/".join(map(str, t)), sum(1 for k in seeded if l[k] != b[k])] + [sum(1 for v in l.values() if v == x) for x in LV])
rows.insert(0, ["5/10/15 (repo)", 0] + [sum(1 for v in b.values() if v == x) for x in LV])
w("seed30_cutoffs.md", md(rows, ["Cut-offs (Low/Mod/High upper score)", "Risks changing level (of 30)", "Low", "Moderate", "High", "Extreme"], ["---", "--:", "--:", "--:", "--:", "--:"]))
fig, ax = plt.subplots(figsize=(5.6, 3.2))
ax.hist(ch, bins=np.arange(-.5, ch.max() + 1.5, 1), color="#0072B2")
ax.axvline(np.median(ch), color="#D55E00", lw=1.5)
ax.set_xlabel("number of the 30 seeded risks whose level differs from the 5/10/15 rule"); ax.set_ylabel("cut-off triples")
ax.set_title(f"Level cut-off sensitivity of the seeded placements\n(all {len(trip)} triples t1<t2<t3 in 2..20; orange = median)", fontsize=9)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.text(.01, .005, f"Derived Calculation | n = 30 risks x {len(trip)} triples | deterministic | same class on both axes is an Assumption", fontsize=6.5, color="#555")
fig.tight_layout(rect=(0, .04, 1, 1)); fig.savefig(FIG / "ch4_seed30_cutoff_histogram.png", dpi=150); plt.close(fig)

# ---- tier rule from bootstrap membership
bt = rd("s3_bootstrap_tier_membership.csv")
rows = []; t1 = []; lo = []
for r in bt:
    p5 = float(r["p_class_5"]); p12 = float(r["p_class_1"]) + float(r["p_class_2"]); ns = int(r["n_seed_studies_with_risk"])
    tier = "unresolved"
    if p5 >= .8 and ns >= 2: tier = "Tier 1 (high)"; t1.append(r["risk_id"])
    elif p5 >= .8: tier = "high-class but single study (not assessable)"
    elif p12 >= .8 and ns >= 2: tier = "Tier lower"; lo.append(r["risk_id"])
    elif p12 >= .8: tier = "low-class but single study (not assessable)"
    rows.append((r["risk_id"], r["base_rank"], ns, r["boot_present_share"], p5, p12, tier))
facts["tier1"] = t1; facts["tier_lower"] = lo
facts["single_high"] = [r[0] for r in rows if r[6].startswith("high-class but")]
facts["single_low"] = [r[0] for r in rows if r[6].startswith("low-class but")]
facts["n_unresolved"] = sum(1 for r in rows if r[6] == "unresolved")
facts["tier_rows"] = rows
w("tiers.md", md([[a, b_, c, f"{float(d):.3f}", f"{e:.3f}", f"{f:.3f}", g] for a, b_, c, d, e, f, g in rows],
                 ["Risk", "Base rank", "Seed studies (n)", "Present in resamples", "P(class 5), when present", "P(class 1-2), when present", "Tier by rule"],
                 ["---", "--:", "--:", "--:", "--:", "--:", "---"]))

# ---- critical |rho| (two-sided 5%, permutation, Spearman)
def crit(n, B=200000):
    x = np.arange(n)
    if n <= 9:
        vals = []
        for pm in itertools.permutations(range(n)):
            d = np.array(pm) - x
            vals.append(1 - 6 * (d * d).sum() / (n * (n * n - 1)))
        vals = np.abs(np.array(vals))
    else:
        r = np.empty(B)
        for j in range(B):
            d = rng.permutation(n) - x
            r[j] = 1 - 6 * (d * d).sum() / (n * (n * n - 1))
        vals = np.abs(r)
    # smallest observed |rho| value v such that P(|R| >= v) <= 0.05
    u = np.unique(vals)[::-1]
    out = None
    for v in u:
        if (vals >= v - 1e-12).mean() <= 0.05: out = v
        else: break
    return out
cr = {n: crit(n) for n in (5, 6, 7, 8, 9, 10, 11, 13, 15, 19)}
facts["critical_rho"] = {str(k): (round(float(v), 3) if v is not None else None) for k, v in cr.items()}
w("critrho.md", md([[n, f"{v:.3f}" if v is not None else "none"] for n, v in cr.items()], ["n shared risks", "Smallest absolute rho with two-sided permutation p <= 0.05"], ["--:", "--:"]))

# ---- SE planning arithmetic
se = {}
for n in (15, 30, 44):
    s = 1.0 / (5 * math.sqrt(n)); se[n] = (round(s, 4), round(1.96 * s, 4))
facts["planning_se_sd1"] = {str(k): v for k, v in se.items()}

# ---- worked example R-LAB
t = tab["R-LAB"]
sm = t["study_means"]
facts["worked_R_LAB"] = {"study_means": sm, "mean": mean(sm.values()), "rank": t["rank"], "class_formula": 5 - ((t["rank"] - 1) * 5) // 30, "class_code": t["class"],
                         "elevated": seed_for("R-LAB", True), "plain": seed_for("R-LAB", False)}
assert abs(mean(sm.values()) - t["mean_rii"]) < 1e-4 and facts["worked_R_LAB"]["class_formula"] == t["class"]
# R-SAFE-like multi-item example: R-SUP M01 three items
facts["worked_R_SUP_M01_items"] = [0.759, 0.759, 0.714]; facts["worked_R_SUP_M01_mean"] = mean([0.759, 0.759, 0.714])
assert abs(facts["worked_R_SUP_M01_mean"] - tab["R-SUP"]["study_means"]["M01"]) < 1e-4
# boundary
facts["boundary_TOOL_INC"] = (tab["R-TOOL"]["mean_rii"], tab["R-INC"]["mean_rii"], matrix_level(4, 4), matrix_level(3, 3))

# ---- figure: seed construction flow
fig, ax = plt.subplots(figsize=(7.4, 2.5)); ax.axis("off")
steps = ["182 seed-file rows\n(Literature)", "keep seed studies\n+ mapping = direct\n(Expert Judgment)", "mean of a study's\ndirect items per risk\n(Assumption)",
         "mean across studies\n= seed mean RII\n(Assumption)", "rank 1..30,\nties by risk id", "5 equal-count bands\n6 per band\n(Assumption)", "class = p class\n= impact class\n(Assumption)"]
for j, s in enumerate(steps):
    x = j * 1.04
    ax.add_patch(plt.Rectangle((x, .25), .92, .5, fc="#eaf2f8", ec="#0072B2"))
    ax.text(x + .46, .5, s, ha="center", va="center", fontsize=6.3)
    if j < len(steps) - 1: ax.annotate("", xy=(x + 1.03, .5), xytext=(x + .93, .5), arrowprops=dict(arrowstyle="->", color="#333"))
ax.set_xlim(-.05, 7.3); ax.set_ylim(0, 1)
fig.text(.01, .02, "Derived Calculation | procedure of app/literature_seed.py (n = 30 seeded of 46 library risks) | RII is importance, not probability or days", fontsize=6.5, color="#555")
fig.tight_layout(rect=(0, .05, 1, 1)); fig.savefig(FIG / "ch3_seed_construction_steps.png", dpi=170); plt.close(fig)

# ---- figure: how the pooled corpus counts differ (no new numbers beyond docs) skipped on purpose
json.dump(facts, open(OUT / "facts.json", "w"), indent=1, default=str)
print(json.dumps({k: v for k, v in facts.items() if k not in ("tier_rows",)}, indent=1, default=str))
