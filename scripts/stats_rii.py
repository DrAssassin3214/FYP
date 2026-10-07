"""Statistical analysis of the RII dataset (data/literature_seed.json).

Run: python scripts/stats_rii.py [out.json]
Every number is computed from the published RII values; nothing is simulated except the permutation / bootstrap
resampling, which uses a fixed seed. RII is an importance rating, so all results concern the RANKING only.
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path
from statistics import mean

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.literature_seed import load_dataset, seed_table  # noqa: E402

DATA = load_dataset()
RISKS = [r["id"] for r in json.loads((ROOT / "data" / "risk_library_masonry.json").read_text(encoding="utf-8-sig"))]
ROLE = {s["id"]: s["role"] for s in DATA["studies"]}
NSAMP = {"M01": 44, "M06": 201, "A14": 163, "A15": 90, "M15": 47, "M14": 83}   # numeric respondent counts (A02 not reported)
RNG = np.random.default_rng(20261006)


def study_means(roles=("seed",)) -> dict[str, dict[str, float]]:
    """risk -> {study: mean of that study's DIRECT values}."""
    out: dict[str, dict[str, float]] = {k: {} for k in RISKS}
    for rid in RISKS:
        for sid in sorted({r["study"] for r in DATA["rows"] if r.get("risk") == rid and r.get("mapping") == "direct"}):
            if ROLE[sid] in roles:
                out[rid][sid] = mean(r["rii"] for r in DATA["rows"] if r["study"] == sid and r.get("risk") == rid and r.get("mapping") == "direct")
    return out


def ranks_desc(d: dict[str, float]) -> dict[str, float]:
    ids = list(d)
    rk = stats.rankdata([-d[i] for i in ids], method="average")
    return dict(zip(ids, rk))


def perm_p(x: list[float], y: list[float], n_perm: int = 20000) -> float:
    """Two-sided permutation p-value for Spearman rho (exact enumeration when n <= 8)."""
    rho0 = stats.spearmanr(x, y)[0]
    n = len(x)
    if n <= 8:
        vals = [stats.spearmanr(x, [y[i] for i in perm])[0] for perm in itertools.permutations(range(n))]
    else:
        vals = [stats.spearmanr(x, RNG.permutation(y))[0] for _ in range(n_perm)]
    return float(np.mean(np.abs(vals) >= abs(rho0) - 1e-12))


seed = study_means(("seed",))
allm = study_means(("seed", "validation"))
res: dict = {}

# 1. descriptive statistics of the seed values (per risk, across seed studies) and of all values
desc = []
for rid in RISKS:
    v = list(seed[rid].values())
    va = list(allm[rid].values())
    if not v:
        continue                                                   # no seed-study value: the risk is not seeded
    desc.append({"risk": rid, "n_seed_studies": len(v), "seed_mean": mean(v), "seed_sd": float(np.std(v, ddof=1)) if len(v) > 1 else None,
                 "seed_min": min(v), "seed_max": max(v), "n_all_studies": len(va), "all_mean": mean(va),
                 "all_sd": float(np.std(va, ddof=1)) if len(va) > 1 else None, "all_min": min(va), "all_max": max(va)})
res["descriptive"] = desc
sm = {d["risk"]: d["seed_mean"] for d in desc}
am = {d["risk"]: d["all_mean"] for d in desc}
SEEDED = [r for r in RISKS if r in sm]

# 2. are the ten seed means different from each other? spread, and one-way test using the underlying direct observations
obs = [r for r in DATA["rows"] if ROLE[r["study"]] == "seed" and r.get("mapping") == "direct" and r.get("risk")]
groups = [[o["rii"] for o in obs if o["risk"] == rid] for rid in SEEDED]
kw = stats.kruskal(*groups)
top9 = [g for rid, g in zip(SEEDED, groups) if rid != "R-WX"]
kw9 = stats.kruskal(*top9)
res["difference_tests"] = {
    "n_observations": len(obs),
    "kruskal_all10": {"H": float(kw.statistic), "p": float(kw.pvalue), "df": len(SEEDED) - 1},
    "kruskal_without_R-WX": {"H": float(kw9.statistic), "p": float(kw9.pvalue), "df": len(SEEDED) - 2},
    "range_all10": max(sm.values()) - min(sm.values()),
    "range_without_R-WX": max(v for k, v in sm.items() if k != "R-WX") - min(v for k, v in sm.items() if k != "R-WX"),
    "wx_vs_rest": None,
}
wx = [o["rii"] for o in obs if o["risk"] == "R-WX"]
rest = [o["rii"] for o in obs if o["risk"] != "R-WX"]
mw = stats.mannwhitneyu(wx, rest, alternative="less")
res["difference_tests"]["wx_vs_rest"] = {"n_wx": len(wx), "n_rest": len(rest), "median_wx": float(np.median(wx)), "median_rest": float(np.median(rest)),
                                         "U": float(mw.statistic), "p_one_sided": float(mw.pvalue)}

# 3. robustness of the seed ranking
base_rank = ranks_desc(sm)
studies_seed = sorted({s for rid in RISKS for s in seed[rid]})
loo = []
for drop in studies_seed:
    m = {}
    for rid in SEEDED:
        v = [x for s, x in seed[rid].items() if s != drop]
        if v:
            m[rid] = mean(v)
    common = [r for r in SEEDED if r in m]
    rho = stats.spearmanr([sm[r] for r in common], [m[r] for r in common])[0]
    rk = ranks_desc(m)
    loo.append({"dropped": drop, "n_risks": len(common), "rho_vs_full_seed": float(rho), "max_rank_shift": max(abs(rk[r] - base_rank[r]) for r in common)})
res["leave_one_study_out"] = loo

boot = {rid: [] for rid in SEEDED}
for _ in range(5000):
    pick = RNG.choice(studies_seed, size=len(studies_seed), replace=True)
    m = {}
    for rid in SEEDED:
        v = [seed[rid][s] for s in pick if s in seed[rid]]
        if v:
            m[rid] = mean(v)
    if len(m) < 3:
        continue
    rk = ranks_desc(m)                                            # ranks among the risks present in this resample ...
    for rid in m:                                                 # ... scaled to the full 1..N range, so sparse risks are not discarded
        boot[rid].append(1 + (rk[rid] - 1) / (len(m) - 1) * (len(SEEDED) - 1))
res["bootstrap_rank"] = [{"risk": rid, "base_rank": base_rank[rid], "median": float(np.median(boot[rid])),
                          "p2_5": float(np.percentile(boot[rid], 2.5)) if boot[rid] else None, "p97_5": float(np.percentile(boot[rid], 97.5)) if boot[rid] else None, "n_resamples": len(boot[rid])} for rid in SEEDED]

# weighted vs unweighted seed
w = {}
for rid in SEEDED:
    items = [(s, x) for s, x in seed[rid].items() if s in NSAMP]
    w[rid] = (sum(NSAMP[s] * x for s, x in items) / sum(NSAMP[s] for s, _ in items)) if items else sm[rid]
res["weighted_vs_unweighted"] = {"rho": float(stats.spearmanr([sm[r] for r in SEEDED], [w[r] for r in SEEDED])[0]),
                                 "weights": "respondent counts: M01 44, M06 201, A14 163, A15 90 (A02 not reported, left unweighted via fallback)",
                                 "weighted_means": {r: w[r] for r in SEEDED}}

# 4. agreement between the held-out studies and the seed (rho, Kendall tau, permutation p, bootstrap CI for rho)
val = []
for sid in [s for s in ROLE if ROLE[s] == "validation"]:
    common = [r for r in SEEDED if sid in allm[r]]
    if len(common) < 4:
        val.append({"study": sid, "n": len(common), "tested": False})
        continue
    x = [sm[r] for r in common]
    y = [allm[r][sid] for r in common]
    rho, p_t = stats.spearmanr(x, y)
    tau, p_tau = stats.kendalltau(x, y)
    bs = []
    for _ in range(4000):
        idx = RNG.integers(0, len(common), len(common))
        if len(set(idx)) < 3 or len(set(np.array(x)[idx])) < 2 or len(set(np.array(y)[idx])) < 2:
            continue
        bs.append(stats.spearmanr(np.array(x)[idx], np.array(y)[idx])[0])
    val.append({"study": sid, "n": len(common), "tested": True, "rho": float(rho), "p_t": float(p_t), "p_perm": perm_p(x, y),
                "tau": float(tau), "p_tau": float(p_tau), "ci95_lo": float(np.percentile(bs, 2.5)), "ci95_hi": float(np.percentile(bs, 97.5)),
                "critical_rho_5pct": float(stats.t.ppf(0.975, len(common) - 2) / np.sqrt(len(common) - 2 + stats.t.ppf(0.975, len(common) - 2) ** 2))})
res["validation"] = val

# 5. agreement among all studies (pairwise Spearman over shared risks) and manager-vs-worker
sids = ["M01", "M06", "A02", "A14", "A15", "M10", "M15", "M14"]
pair = []
for a, b in itertools.combinations(sids, 2):
    common = [r for r in RISKS if a in allm[r] and b in allm[r]]
    if len(common) >= 4:
        rho, p = stats.spearmanr([allm[r][a] for r in common], [allm[r][b] for r in common])
        pair.append({"a": a, "b": b, "n": len(common), "rho": float(rho), "p": float(p)})
res["pairwise_agreement"] = pair
rhos = [q["rho"] for q in pair]
res["pairwise_summary"] = {"n_pairs": len(pair), "mean_rho": float(np.mean(rhos)), "median_rho": float(np.median(rhos)), "min": float(min(rhos)), "max": float(max(rhos))}

# Kendall's W over the studies that cover the same risks (complete block only)
block_risks = [r for r in RISKS if all(s in allm[r] for s in ("M01", "M10", "M15", "M14"))]
if len(block_risks) >= 4:
    mat = np.array([[allm[r][s] for r in block_risks] for s in ("M01", "M10", "M15", "M14")])
    k, n = mat.shape
    rk = np.array([stats.rankdata(-row) for row in mat])
    s_ = float(((rk.sum(axis=0) - rk.sum(axis=0).mean()) ** 2).sum())
    W = 12 * s_ / (k ** 2 * (n ** 3 - n))
    chi2 = k * (n - 1) * W
    res["kendall_w"] = {"studies": ["M01", "M10", "M15", "M14"], "risks": block_risks, "k": k, "n": n, "W": float(W), "chi2": float(chi2),
                        "p": float(stats.chi2.sf(chi2, n - 1))}

# 6. do all studies (seed + held-out) change the picture? pooled ranking vs seed ranking
common = SEEDED
rho_all = stats.spearmanr([sm[r] for r in common], [am[r] for r in common])[0]
res["pooled_vs_seed"] = {"rho": float(rho_all), "pooled_means": am}

# 7. scale-free pooling: normalised within-study rank (0 = most important, 1 = least) averaged over all studies that cover >= 4 risks
norm = {r: [] for r in RISKS}
for sid in ROLE:
    cov = [r for r in RISKS if sid in allm[r]]
    if len(cov) < 4:
        continue
    rk = ranks_desc({r: allm[r][sid] for r in cov})
    for r in cov:
        norm[r].append((rk[r] - 1) / (len(cov) - 1))
pooled_rank = {r: float(np.mean(v)) for r, v in norm.items() if v}
_both = [r for r in SEEDED if r in pooled_rank]
res["pooled_rank_vs_seed"] = {"rho": float(stats.spearmanr([sm[r] for r in _both], [-pooled_rank[r] for r in _both])[0]),
                              "mean_normalised_rank": pooled_rank, "n_studies_per_risk": {r: len(v) for r, v in norm.items()}}
res["pooled_rank_order"] = sorted(pooled_rank, key=lambda r: pooled_rank[r])

out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs" / "rii_statistics.json"
out.write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")
print("wrote", out)
