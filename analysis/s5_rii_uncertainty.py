"""S5. RII uncertainty: spread of each risk's RII across the studies that report it (direct mappings, one value per study).
This is between-study spread (different scales, samples, countries), NOT a sampling error of any one survey, and RII is an
importance index: nothing here is a probability or a number of days."""
from __future__ import annotations

import time

import numpy as np
from scipy import stats

import common as C


def main():
    t0 = time.time()
    data = C.load_data(); roles = C.roles(data)
    allm = C.per_study_risk_means(data, ("direct",))
    seedm = {s: d for s, d in allm.items() if roles[s] == "seed"}
    base = C.risk_means(seedm); order = C.order(base)
    # scale-free: within-study percentile rank, studies with >= 5 risks
    pct = {}
    for s, d in allm.items():
        if len(d) >= 5:
            v = np.array(list(d.values())); pct[s] = dict(zip(d, stats.rankdata(v) / len(v)))
    risks = sorted({r for d in allm.values() for r in d})
    rows = []
    for r in risks:
        va = {s: d[r] for s, d in allm.items() if r in d}
        vs = {s: v for s, v in va.items() if roles[s] == "seed"}
        pv = {s: d[r] for s, d in pct.items() if r in d}
        def st(v):
            a = np.array(list(v.values()))
            return (len(a), a.mean(), a.min(), a.max(), a.max() - a.min(), a.std(ddof=1) if len(a) > 1 else float("nan"))
        n_all, m_all, lo, hi, rg, sd = st(va)
        n_s = len(vs)
        rows.append({"risk_id": r, "seed_rank": order.index(r) + 1 if r in base else None, "n_studies_all": n_all, "studies_all": " ".join(sorted(va)),
                     "mean_rii_all": m_all, "min_rii": lo, "max_rii": hi, "range_rii": rg, "sd_rii_between_studies": sd,
                     "n_seed_studies": n_s, "seed_mean_rii": np.mean(list(vs.values())) if vs else None,
                     "seed_range_rii": (max(vs.values()) - min(vs.values())) if n_s > 1 else None,
                     "n_studies_pct_rank": len(pv), "pct_rank_range": (max(pv.values()) - min(pv.values())) if len(pv) > 1 else None,
                     "n": n_all})
    rows.sort(key=lambda x: (x["seed_rank"] is None, x["seed_rank"] or 0, x["risk_id"]))
    C.write_csv("s5_rii_spread_by_risk", rows, list(rows[0]))

    # compare with the gaps that decide the repo's bands
    ms = np.array([base[r] for r in order]); gaps = ms[:-1] - ms[1:]
    multi = [r for r in rows if r["n_seed_studies"] >= 2]
    sds = [r["sd_rii_between_studies"] for r in rows if r["n_studies_all"] >= 2]
    rngs = [r["seed_range_rii"] for r in multi]
    cmp = {"n_seeded_risks": len(order), "median_gap_between_adjacent_seed_ranks": float(np.median(gaps)),
           "overall_spread_of_seed_means_max_minus_min": float(ms.max() - ms.min()),
           "n_risks_with_>=2_seed_studies": len(multi), "median_seed_range_those_risks": float(np.median(rngs)),
           "median_between_study_sd_all_studies_n>=2": float(np.median(sds)), "n_risks_with_>=2_studies_any": len(sds),
           "share_of_risks_with_>=2_seed_studies_whose_range_exceeds_the_median_adjacent_gap": float(np.mean(np.array(rngs) > np.median(gaps)))}
    C.write_csv("s5_spread_vs_band_gaps", [{"statistic": k, "value": v, "n": len(order)} for k, v in cmp.items()], ["statistic", "value", "n"])
    C.write_json("s5_summary", {**cmp, "widest_seed_ranges": [(r["risk_id"], round(r["seed_range_rii"], 4), r["n_seed_studies"]) for r in sorted(multi, key=lambda x: -x["seed_range_rii"])[:6]],
                                "note": "between-study spread; scales differ across studies (1-4, 1-5, pooled), see s4_study_coverage.csv"},
                 {"risks_all": len(risks), "seeded_risks": len(order), "studies": len(allm)})

    import matplotlib.pyplot as plt
    sh = {s: m for s, m in zip(sorted(allm), ["o", "s", "^", "D", "v", "P", "X", "*", "<", ">", "h"])}
    col = {s: C.PALETTE11[i] for i, s in enumerate(sorted(allm))}
    rr = [r for r in rows if r["seed_rank"] is not None]
    fig, ax = plt.subplots(figsize=(8.2, 0.3 * len(rr) + 1.8))
    for i, r in enumerate(rr):
        vals = {s: d[r["risk_id"]] for s, d in allm.items() if r["risk_id"] in d}
        if len(vals) > 1:
            ax.hlines(i, min(vals.values()), max(vals.values()), color="#CCCCCC", lw=3, zorder=1)
        for s, v in vals.items():
            ax.scatter(v, i, marker=sh[s], s=38, color=col[s], zorder=3, edgecolor="white" if roles[s] == "seed" else "black", linewidth=0.5)
        ax.scatter(r["seed_mean_rii"], i, marker="|", s=140, color="black", zorder=4)
    ax.set_yticks(range(len(rr)), [f"{r['risk_id']} (n={r['n_studies_all']})" for r in rr], fontsize=7); ax.invert_yaxis()
    ax.set_xlabel("RII as printed in each study (scales differ); black tick = seed mean; black edge = held-out study")
    handles = [plt.Line2D([], [], marker=sh[s], ls="", color=col[s], label=f"{s} ({roles[s]})", markersize=5) for s in sorted(allm)]
    ax.legend(handles=handles, fontsize=6.5, ncol=1, loc="center left", bbox_to_anchor=(1.01, 0.5))
    C.save_fig(fig, "s5_rii_spread", f"n = {len(rr)} seeded risks, {len(allm)} studies; n per row = studies reporting the risk", "S5 Between-study spread of RII per risk (rows ordered by seed rank)")
    return cmp


if __name__ == "__main__":
    print(main())
