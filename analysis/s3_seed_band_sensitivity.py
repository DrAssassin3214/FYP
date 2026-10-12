"""S3. Seed-band sensitivity. Re-implements the repo's RII -> ordinal-class mapping (app.literature_seed) so that
alternative band cut-offs and study resamples can be tried, and asserts that the re-implementation reproduces
app.literature_seed.seed_table() exactly before anything else is computed.
RII is a survey importance index; the classes here are RANKING bands only (never a probability or a number of days)."""
from __future__ import annotations

import time
from bisect import bisect_right
from collections import Counter

import numpy as np
from scipy import stats

import common as C
from app.literature_seed import seed_table

B = 2000
SCALE_K = {"M01": 5, "A02": 4, "M06": 5, "A14": 5, "A15": None, "M15": 4, "M14": 5, "M10": None, "A10": 5, "A21": 5, "HAS25": None}
# scale k per the dataset's own 'scale' field; None = pooled / not recorded -> left unrescaled


def to5(cls, n_bands):
    return {r: int(round(1 + (c - 1) * 4 / (n_bands - 1))) for r, c in cls.items()}


def bands_equal_width(means, nb=5):
    lo, hi = min(means.values()), max(means.values()); w = (hi - lo) / nb
    return {r: min(nb, 1 + int((v - lo) / w)) for r, v in means.items()}


def bands_fixed(means, edges=(0.2, 0.4, 0.6, 0.8)):
    return {r: bisect_right(list(edges), v) + 1 for r, v in means.items()}


def compare(bm, bc, m, c):
    common = sorted(set(bm) & set(m))
    a = [bm[r] for r in common]; b = [m[r] for r in common]
    ca = [bc[r] for r in common]; cb = [c[r] for r in common]
    br = {r: i for i, r in enumerate(C.order({r: bm[r] for r in common}))}
    nr = {r: i for i, r in enumerate(C.order({r: m[r] for r in common}))}
    return {"n_common_risks": len(common), "spearman_means": C.spearman(a, b), "kendall_tau_means": C.kendall(a, b),
            "kendall_tau_classes": C.kendall(ca, cb), "n_class_changed": sum(x != y for x, y in zip(ca, cb)),
            "pct_class_changed": 100 * sum(x != y for x, y in zip(ca, cb)) / len(common),
            "max_rank_shift": max(abs(br[r] - nr[r]) for r in common),
            "risks_dropped": " ".join(sorted(set(bm) - set(m))), "risks_added": " ".join(sorted(set(m) - set(bm)))}


def main():
    t0 = time.time()
    data = C.load_data(); roles = C.roles(data)
    SEEDS = sorted(s for s, r in roles.items() if r == "seed")
    bs = C.per_study_risk_means(data, ("direct",), SEEDS)               # study -> risk -> mean
    sm = {}                                                              # risk -> study -> mean
    for s, d in bs.items():
        for rid, v in d.items():
            sm.setdefault(rid, {})[s] = v
    base_m = C.risk_means(bs); base_c = C.bands_equal_count(base_m); base_o = C.order(base_m)
    n_risk = len(base_m)
    st = seed_table()
    ok = all(abs(st[r]["mean_rii"] - round(base_m[r], 4)) < 1e-9 and st[r]["class"] == base_c[r] and st[r]["rank"] == base_o.index(r) + 1 for r in base_m)
    assert ok and sum(1 for v in st.values() if v["class"]) == n_risk, "re-implementation differs from app.literature_seed"
    per_band = Counter(base_c.values())

    # ---- band-rule / data variants -------------------------------------------------------------------------------
    V = {}
    V["repo rule: 5 equal-count bands (6 per band)"] = (base_m, base_c)
    V["3 equal-count bands (tertiles), mapped to classes 1/3/5"] = (base_m, to5(C.bands_equal_count(base_m, 3), 3))
    V["4 equal-count bands, mapped to 1-5"] = (base_m, to5(C.bands_equal_count(base_m, 4), 4))
    V["5 equal-width bands on mean RII"] = (base_m, bands_equal_width(base_m))
    V["fixed RII cut-offs 0.2/0.4/0.6/0.8"] = (base_m, bands_fixed(base_m))
    V["fixed RII cut-offs 0.60/0.65/0.70/0.75"] = (base_m, bands_fixed(base_m, (0.60, 0.65, 0.70, 0.75)))
    m = C.risk_means(C.per_study_risk_means(data, ("direct", "related"), SEEDS)); V["direct + related mappings"] = (m, C.bands_equal_count(m))
    m = C.risk_means(bs, min_studies=2); V[">= 2 seed studies per risk (re-banded)"] = (m, C.bands_equal_count(m))
    m = C.risk_means(C.per_study_risk_means(data, ("direct",), SEEDS, SCALE_K)); V["scale-rescaled (RII-1/k)/(1-1/k)"] = (m, C.bands_equal_count(m))
    pr = {}
    for s in SEEDS:                     # within-study percentile rank (scale-free) for studies with >= 3 risks
        d = bs.get(s, {})
        if len(d) >= 3:
            v = np.array(list(d.values())); rk = stats.rankdata(v) / len(v)
            pr[s] = dict(zip(d, rk))
    m = C.risk_means(pr); V["within-study percentile rank (studies with >= 3 risks)"] = (m, C.bands_equal_count(m))
    for s in SEEDS:
        m = C.risk_means({k: v for k, v in bs.items() if k != s}); V[f"drop seed study {s}"] = (m, C.bands_equal_count(m))
    vrows = []
    for name, (m, c) in V.items():
        r = compare(base_m, base_c, m, c)
        r.update({"variant": name, "n_risks_in_variant": len(m), "class_counts_1_to_5": " ".join(f"{k}:{v}" for k, v in sorted(Counter(c.values()).items())), "n": n_risk})
        vrows.append(r)
    flds = ["variant", "n_risks_in_variant", "n_common_risks", "spearman_means", "kendall_tau_means", "kendall_tau_classes",
            "n_class_changed", "pct_class_changed", "max_rank_shift", "class_counts_1_to_5", "risks_dropped", "risks_added", "n"]
    C.write_csv("s3_band_variants", vrows, flds)

    # ---- top-tier membership under alternative tier sizes (base data) ----------------------------------------------
    trows = []
    for tier_name, k in (("top 6 (repo class 5)", 6), ("top 10 (tertile)", 10), ("top 8 (quartile-ish)", 8)):
        trows.append({"tier": tier_name, "members": " ".join(base_o[:k]), "n_members": k, "n": n_risk})
    C.write_csv("s3_base_tiers", trows, ["tier", "members", "n_members", "n"])

    # ---- bootstrap over the seed studies ---------------------------------------------------------------------------
    rng = np.random.default_rng(C.SEED)
    P5 = {r: Counter() for r in base_m}                                  # risk -> class counts (repo rule)
    P3 = {r: Counter() for r in base_m}                                  # risk -> tertile counts
    present = Counter(); ranks = {r: [] for r in base_m}; taus = []; rhos = []; ncommon = []; keep = []
    top6 = Counter(); top10 = Counter()
    for _ in range(B):
        pick = rng.choice(SEEDS, size=len(SEEDS), replace=True)
        w = Counter(pick)
        mm = C.risk_means(bs, {s: float(c) for s, c in w.items()})
        c5 = C.bands_equal_count(mm); c3 = C.bands_equal_count(mm, 3); o = C.order(mm)
        for i, r in enumerate(o):
            present[r] += 1; ranks[r].append(i + 1); P5[r][c5[r]] += 1; P3[r][c3[r]] += 1
            top6[r] += c5[r] == 5; top10[r] += c3[r] == 3
        com = sorted(set(mm) & set(base_m)); a = [base_m[r] for r in com]; b = [mm[r] for r in com]
        taus.append(C.kendall(a, b)); rhos.append(C.spearman(a, b)); ncommon.append(len(com))
        keep.append(np.mean([c5[r] == base_c[r] for r in com]))
    brow = []
    for r in base_o:
        pr_ = present[r]
        brow.append({"risk_id": r, "base_rank": base_o.index(r) + 1, "base_class": base_c[r], "base_mean_rii": base_m[r],
                     "n_seed_studies_with_risk": len(sm[r]), "boot_present_share": pr_ / B,
                     "p_top_tier_repo_class5": top6[r] / pr_, "p_top_tertile": top10[r] / pr_,
                     "p_same_class_as_base": P5[r][base_c[r]] / pr_,
                     **{f"p_class_{k}": P5[r][k] / pr_ for k in range(1, 6)},
                     "rank_p2.5": np.percentile(ranks[r], 2.5), "rank_median": np.median(ranks[r]), "rank_p97.5": np.percentile(ranks[r], 97.5),
                     "n": n_risk, "n_boot": B})
    C.write_csv("s3_bootstrap_tier_membership", brow, list(brow[0]))
    taus = np.array(taus); rhos = np.array(rhos)
    rs = [{"statistic": "Kendall tau (bootstrap mean RII vs base mean RII, common risks)", "mean": np.nanmean(taus), "p2.5": np.nanpercentile(taus, 2.5), "p97.5": np.nanpercentile(taus, 97.5), "n": n_risk, "n_boot": B},
          {"statistic": "Spearman rho (same)", "mean": np.nanmean(rhos), "p2.5": np.nanpercentile(rhos, 2.5), "p97.5": np.nanpercentile(rhos, 97.5), "n": n_risk, "n_boot": B},
          {"statistic": "share of common risks keeping their repo class", "mean": np.mean(keep), "p2.5": np.percentile(keep, 2.5), "p97.5": np.percentile(keep, 97.5), "n": n_risk, "n_boot": B},
          {"statistic": "number of common risks per bootstrap sample", "mean": np.mean(ncommon), "p2.5": np.percentile(ncommon, 2.5), "p97.5": np.percentile(ncommon, 97.5), "n": n_risk, "n_boot": B}]
    C.write_csv("s3_bootstrap_rank_stability", rs, ["statistic", "mean", "p2.5", "p97.5", "n", "n_boot"])

    # exact leave-one-study-out (jackknife) rank stability
    jr = []
    for s in SEEDS:
        m = C.risk_means({k: v for k, v in bs.items() if k != s}); com = sorted(set(m) & set(base_m))
        a = [base_m[r] for r in com]; b = [m[r] for r in com]
        jr.append({"dropped_seed_study": s, "n_common_risks": len(com), "kendall_tau": C.kendall(a, b), "spearman_rho": C.spearman(a, b),
                   "n_repo_class_changed": sum(C.bands_equal_count(m)[r] != base_c[r] for r in com), "n": n_risk})
    C.write_csv("s3_leave_one_study_out_rank_stability", jr, list(jr[0]))

    # ties / closeness at the band boundaries of the repo rule
    gaps = []
    for i in range(1, n_risk):
        if (i * 5) // n_risk != ((i - 1) * 5) // n_risk:
            gaps.append({"boundary_between_ranks": f"{i}-{i + 1}", "upper_risk": base_o[i - 1], "lower_risk": base_o[i], "mean_rii_gap": base_m[base_o[i - 1]] - base_m[base_o[i]], "n": n_risk})
    C.write_csv("s3_band_boundary_gaps", gaps, list(gaps[0]))
    ties = {round(v, 4): [r for r in base_m if round(base_m[r], 4) == round(v, 4)] for v in set(base_m.values())}
    ties = {k: v for k, v in ties.items() if len(v) > 1}

    stable = [r for r in base_o if P5[r][base_c[r]] / present[r] >= 0.5]
    summary = {"reimplementation_matches_seed_table": ok, "n_seeded_risks": n_risk, "risks_per_band": dict(per_band), "seed_studies": SEEDS,
               "n_bootstrap": B, "bootstrap_unit": "seed STUDIES (5), resampled with replacement; a study drawn twice has weight 2",
               "bootstrap_kendall_tau_mean": float(np.nanmean(taus)), "bootstrap_kendall_tau_ci95": [float(np.nanpercentile(taus, 2.5)), float(np.nanpercentile(taus, 97.5))],
               "bootstrap_share_keeping_class_mean": float(np.mean(keep)),
               "risks_modal_class_equals_base": len(stable), "n_exact_mean_ties": {str(k): v for k, v in ties.items()},
               "top_class_p_ge_0.8": [r for r in base_o if top6[r] / present[r] >= 0.8],
               "variants_pct_class_changed": {v["variant"]: round(v["pct_class_changed"], 1) for v in vrows}}
    C.write_json("s3_summary", summary, {"seeded_risks": n_risk, "seed_studies": len(SEEDS), "bootstrap_resamples": B})

    import matplotlib.pyplot as plt
    ntxt = f"n = {n_risk} seeded risks; {len(SEEDS)} seed studies; {B} study-level bootstrap resamples"
    fig, ax = plt.subplots(figsize=(7.5, 0.26 * n_risk + 1.6))
    mat = np.array([[P5[r][k] / present[r] for k in range(5, 0, -1)] for r in base_o])
    im = ax.imshow(mat, aspect="auto", cmap="Blues", vmin=0, vmax=1)
    for (i, j), v in np.ndenumerate(mat):
        if v >= 0.05:
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=6.5, color="white" if v > 0.55 else "black")
    ax.set_xticks(range(5), [f"class {k}" for k in range(5, 0, -1)])
    ax.set_yticks(range(n_risk), [f"{r} (rank {i + 1}, base {base_c[r]}, {len(sm[r])} stud.)" for i, r in enumerate(base_o)], fontsize=6.5)
    ax.set_title("Share of bootstrap resamples placing the risk in each class (repo 5-band rule)", fontsize=8)
    C.save_fig(fig, "s3_bootstrap_tier_membership", ntxt, "S3 Class-membership frequency under study resampling")

    fig, axs = plt.subplots(1, 2, figsize=(11, 4.2), gridspec_kw={"width_ratios": [1.6, 1]})
    sel = [v for v in vrows if not v["variant"].startswith("repo rule")]
    axs[0].barh(range(len(sel)), [v["pct_class_changed"] for v in sel], color=C.OKABE[0])
    axs[0].set_yticks(range(len(sel)), [f"{v['variant']} (n={v['n_common_risks']})" for v in sel], fontsize=6.5); axs[0].invert_yaxis()
    axs[0].set_xlabel("% of common risks whose class differs from the repo rule"); axs[0].set_title("Alternative banding / data variants")
    axs[1].hist(taus[~np.isnan(taus)], bins=30, color=C.OKABE[2]); axs[1].set_xlabel("Kendall tau vs base ranking"); axs[1].set_ylabel(f"resamples (of {B})")
    axs[1].set_title("Rank stability over study bootstrap")
    C.save_fig(fig, "s3_variants_and_rank_stability", ntxt, "S3 Seed-band sensitivity")
    return summary


if __name__ == "__main__":
    print(main())
