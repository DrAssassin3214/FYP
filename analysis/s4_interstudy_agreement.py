"""S4. Inter-study agreement among the 11 studies in data/literature_seed.json, built so that no study is compared with
a seed that contains it:
  (a) pairwise Spearman on the risks two studies share (n shown), permutation p, Holm over the pairs with n >= 5;
  (b) leave-one-study-out: study X is compared with the mean-RII seed built from the OTHER seed studies only
      (the circular comparison, X inside its own seed, is shown only to quantify the inflation);
  (c) Kendall W (tie-corrected) on complete study x risk blocks, permutation p, Holm over the blocks tested.
Unit: one value per (study, risk) = mean of that study's items mapped 'direct' to the risk (as the repo averages).
All statistics are rank agreement between importance indices; they say nothing about probability or days."""
from __future__ import annotations

import itertools
import time

import numpy as np
from scipy import stats

import common as C

MIN_N = 5
N_PERM = 20000
EXACT_MAX_N = 8


def perm_p_spearman(x, y, rng):
    """Two-sided permutation p for Spearman (ranks of y permuted). Exact for n <= 8, else N_PERM draws (+1 correction)."""
    rx = stats.rankdata(x); ry = stats.rankdata(y); n = len(rx)
    cx = rx - rx.mean(); cy0 = ry - ry.mean()
    den = np.sqrt((cx ** 2).sum() * (cy0 ** 2).sum())
    r0 = abs((cx * cy0).sum() / den)
    if n <= EXACT_MAX_N:
        P = np.array(list(itertools.permutations(range(n))))
        r = np.abs((cx[None, :] * cy0[P]).sum(1) / den)
        return float(np.mean(r >= r0 - 1e-12)), "exact"
    P = rng.permuted(np.tile(cy0, (N_PERM, 1)), axis=1)
    r = np.abs((cx[None, :] * P).sum(1) / den)
    return float((np.sum(r >= r0 - 1e-12) + 1) / (N_PERM + 1)), f"{N_PERM} permutations"


def kendall_w(R):
    """R: m judges x n objects of (possibly tied) ranks. Tie-corrected W."""
    m, n = R.shape
    S = ((R.sum(0) - R.sum() / n) ** 2).sum()
    T = 0.0
    for row in R:
        _, c = np.unique(row, return_counts=True); T += (c ** 3 - c).sum()
    den = m ** 2 * (n ** 3 - n) - m * T
    return float(12 * S / den) if den > 0 else float("nan")


def perm_p_w(R, rng):
    w0 = kendall_w(R); m, n = R.shape; cnt = 0
    for _ in range(N_PERM):
        Q = R.copy()
        for i in range(m):
            Q[i] = rng.permutation(Q[i])
        cnt += kendall_w(Q) >= w0 - 1e-12
    return w0, float((cnt + 1) / (N_PERM + 1))


def main():
    t0 = time.time()
    rng = np.random.default_rng(C.SEED)
    data = C.load_data(); roles = C.roles(data)
    studies = [s["id"] for s in data["studies"]]
    allm = C.per_study_risk_means(data, ("direct",))                   # study -> risk -> mean
    n_items = {s: sum(1 for r in data["rows"] if r["study"] == s and r.get("risk") and r.get("mapping") == "direct") for s in studies}
    cover = [{"study": s, "role": roles[s], "n_risks_direct": len(allm.get(s, {})), "n_items_direct": n_items[s],
              "scale": next(x["scale"] for x in data["studies"] if x["id"] == s), "n": len(studies)} for s in studies]
    C.write_csv("s4_study_coverage", cover, list(cover[0]))

    # (a) pairwise -----------------------------------------------------------------------------------------------
    pairs = []
    for a, b in itertools.combinations(studies, 2):
        da, db = allm.get(a, {}), allm.get(b, {})
        com = sorted(set(da) & set(db)); n = len(com)
        x = [da[r] for r in com]; y = [db[r] for r in com]
        row = {"study_a": a, "study_b": b, "role_a": roles[a], "role_b": roles[b], "n_shared_risks": n,
               "spearman_rho": C.spearman(x, y) if n >= 3 else float("nan"), "kendall_tau": C.kendall(x, y) if n >= 3 else float("nan"),
               "perm_p_two_sided": None, "p_method": "not tested (n < %d)" % MIN_N, "holm_p": None, "tested": 0, "n": n}
        if n >= MIN_N and np.ptp(x) > 0 and np.ptp(y) > 0:
            row["perm_p_two_sided"], row["p_method"] = perm_p_spearman(x, y, rng); row["tested"] = 1
        pairs.append(row)
    tested = [r for r in pairs if r["tested"]]
    for r, h in zip(tested, C.holm([r["perm_p_two_sided"] for r in tested])):
        r["holm_p"] = h
    for r in pairs:
        r["holm_significant_0.05"] = int(r["holm_p"] is not None and r["holm_p"] < 0.05)
    C.write_csv("s4_pairwise_spearman", pairs, ["study_a", "study_b", "role_a", "role_b", "n_shared_risks", "spearman_rho", "kendall_tau",
                                                 "perm_p_two_sided", "p_method", "holm_p", "holm_significant_0.05", "n"])

    # (b) leave-one-study-out -------------------------------------------------------------------------------------
    SEEDS = [s for s in studies if roles[s] == "seed"]
    loso = []
    for x in studies:
        rest = {s: allm[s] for s in SEEDS if s != x and s in allm}
        seed_rest = C.risk_means(rest)
        seed_incl = C.risk_means({s: allm[s] for s in SEEDS if s in allm})
        dx = allm.get(x, {})
        com = sorted(set(dx) & set(seed_rest)); n = len(com)
        xs = [dx[r] for r in com]; ys = [seed_rest[r] for r in com]
        comc = sorted(set(dx) & set(seed_incl))
        row = {"study": x, "role": roles[x], "n_seed_studies_in_comparison_seed": len(rest), "n_shared_risks": n,
               "spearman_rho": C.spearman(xs, ys) if n >= 3 else float("nan"), "kendall_tau": C.kendall(xs, ys) if n >= 3 else float("nan"),
               "perm_p_two_sided": None, "p_method": "not tested (n < %d)" % MIN_N, "holm_p": None, "tested": 0,
               "circular_n_shared": len(comc), "circular_spearman_x_inside_own_seed": C.spearman([dx[r] for r in comc], [seed_incl[r] for r in comc]) if len(comc) >= 3 and roles[x] == "seed" else float("nan"),
               "n": n}
        if n >= MIN_N and np.ptp(xs) > 0 and np.ptp(ys) > 0:
            row["perm_p_two_sided"], row["p_method"] = perm_p_spearman(xs, ys, rng); row["tested"] = 1
        loso.append(row)
    tl = [r for r in loso if r["tested"]]
    for r, h in zip(tl, C.holm([r["perm_p_two_sided"] for r in tl])):
        r["holm_p"] = h
    for r in loso:
        r["holm_significant_0.05"] = int(r["holm_p"] is not None and r["holm_p"] < 0.05)
    C.write_csv("s4_leave_one_study_out", loso, ["study", "role", "n_seed_studies_in_comparison_seed", "n_shared_risks", "spearman_rho", "kendall_tau",
                                                  "perm_p_two_sided", "p_method", "holm_p", "holm_significant_0.05", "circular_n_shared",
                                                  "circular_spearman_x_inside_own_seed", "n"])

    # (c) Kendall W on complete blocks ----------------------------------------------------------------------------
    best = {}
    avail = [s for s in studies if len(allm.get(s, {})) >= 3]
    for m in range(3, len(avail) + 1):
        for sub in itertools.combinations(avail, m):
            R = set.intersection(*[set(allm[s]) for s in sub])
            if len(R) >= MIN_N:
                best.setdefault(m, []).append((len(R), sub, sorted(R)))
    wrows = []
    for m, lst in sorted(best.items()):
        for nR, sub, R in sorted(lst, key=lambda l: (-l[0], l[1])):
            M_ = np.array([stats.rankdata([allm[s][r] for r in R]) for s in sub])
            w0, p = perm_p_w(M_, rng)
            wrows.append({"n_studies_m": m, "studies": " ".join(sub), "n_risks": nR, "risks": " ".join(R), "kendall_W": w0,
                          "mean_pairwise_spearman_from_W": (m * w0 - 1) / (m - 1), "perm_p_one_sided": p, "n_permutations": N_PERM,
                          "n": nR})
    for r, h in zip(wrows, C.holm([r["perm_p_one_sided"] for r in wrows])):
        r["holm_p"] = h; r["holm_significant_0.05"] = int(h < 0.05)
    C.write_csv("s4_kendall_w", wrows, ["n_studies_m", "studies", "n_risks", "risks", "kendall_W", "mean_pairwise_spearman_from_W", "perm_p_one_sided",
                                        "n_permutations", "holm_p", "holm_significant_0.05", "n"])

    pt = [r for r in pairs if r["tested"]]
    summary = {"studies": len(studies), "pairs_total": len(pairs), "pairs_with_n_ge_%d" % MIN_N: len(pt),
               "pairs_n_distribution": {str(k): v for k, v in sorted({n: sum(1 for r in pairs if r["n_shared_risks"] == n) for n in {r["n_shared_risks"] for r in pairs}}.items())},
               "pairs_holm_significant": sum(r["holm_significant_0.05"] for r in pairs),
               "median_rho_tested_pairs": float(np.median([r["spearman_rho"] for r in pt])) if pt else None,
               "rho_range_tested_pairs": [min(r["spearman_rho"] for r in pt), max(r["spearman_rho"] for r in pt)] if pt else None,
               "loso_studies_tested": len(tl), "loso_holm_significant": [r["study"] for r in loso if r["holm_significant_0.05"]],
               "loso_rows": {r["study"]: {"n": r["n_shared_risks"], "rho": r["spearman_rho"], "holm_p": r["holm_p"], "circular_rho": r["circular_spearman_x_inside_own_seed"]} for r in loso},
               "kendall_w_blocks_tested": len(wrows), "kendall_w_holm_significant": sum(r["holm_significant_0.05"] for r in wrows),
               "holm_family_note": "Holm applied separately within each of the three families (pairs, leave-one-study-out, Kendall W blocks); blocks in the Kendall W family overlap, so they are not independent tests",
               "min_n_for_test": MIN_N, "n_permutations": N_PERM}
    C.write_json("s4_summary", summary, {"studies": len(studies), "pairs": len(pairs), "loso_studies": len(loso), "w_blocks": len(wrows)})

    import matplotlib.pyplot as plt
    k = len(studies); idx = {s: i for i, s in enumerate(studies)}
    Rm = np.full((k, k), np.nan); Nm = np.zeros((k, k), int)
    for r in pairs:
        i, j = idx[r["study_a"]], idx[r["study_b"]]
        Nm[i, j] = Nm[j, i] = r["n_shared_risks"]
        Rm[i, j] = Rm[j, i] = r["spearman_rho"] if r["n_shared_risks"] >= MIN_N else np.nan
    fig, ax = plt.subplots(figsize=(7.2, 6.2))
    im = ax.imshow(np.ma.masked_invalid(Rm), cmap="RdBu_r", vmin=-1, vmax=1)
    for i in range(k):
        for j in range(k):
            if i == j:
                continue
            r = next(q for q in pairs if {q["study_a"], q["study_b"]} == {studies[i], studies[j]})
            if r["n_shared_risks"] >= MIN_N:
                star = "*" if r["holm_significant_0.05"] else ""
                ax.text(j, i, f"{Rm[i, j]:.2f}{star}\nn={Nm[i, j]}", ha="center", va="center", fontsize=6)
            else:
                ax.text(j, i, f"n={Nm[i, j]}", ha="center", va="center", fontsize=6, color="#888888")
    lab = [f"{s}{'' if roles[s] == 'seed' else ' (h)'}" for s in studies]
    ax.set_xticks(range(k), lab, rotation=45, ha="right"); ax.set_yticks(range(k), lab)
    fig.colorbar(im, ax=ax, shrink=0.7, label="Spearman rho (cells with n >= %d)" % MIN_N)
    ax.set_title("* = Holm-adjusted permutation p < 0.05 over %d tested pairs; (h) = held-out study; grey = n < %d, not tested" % (len(pt), MIN_N), fontsize=7)
    C.save_fig(fig, "s4_pairwise_spearman", f"n = {k} studies, {len(pairs)} pairs; n per cell = shared risks", "S4 Pairwise study agreement on shared risks")

    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    xs_ = np.arange(len(loso))
    ax.bar(xs_ - 0.18, [0 if np.isnan(r["spearman_rho"]) else r["spearman_rho"] for r in loso], 0.36, color=C.OKABE[0], label="vs seed WITHOUT the study (non-circular)")
    ax.bar(xs_ + 0.18, [0 if np.isnan(r["circular_spearman_x_inside_own_seed"]) else r["circular_spearman_x_inside_own_seed"] for r in loso], 0.36, color="#BBBBBB", label="study inside its own seed (circular, seed studies only)")
    for i, r in enumerate(loso):
        ax.text(i - 0.18, (0 if np.isnan(r["spearman_rho"]) else r["spearman_rho"]) + (0.03 if (r["spearman_rho"] if not np.isnan(r["spearman_rho"]) else 0) >= 0 else -0.09),
                f"n={r['n_shared_risks']}" + ("*" if r["holm_significant_0.05"] else ""), ha="center", fontsize=6.5)
    ax.axhline(0, color="black", lw=0.6)
    ax.set_xticks(xs_, [f"{r['study']}{'' if r['role'] == 'seed' else ' (h)'}" for r in loso]); ax.set_ylabel("Spearman rho"); ax.set_ylim(-1, 1.1)
    ax.legend(fontsize=7, loc="lower right"); ax.set_title("* = Holm p < 0.05 (tested only if n >= %d); no bar = fewer than 3 shared risks" % MIN_N, fontsize=7.5)
    C.save_fig(fig, "s4_leave_one_study_out", f"n = {len(loso)} studies; n per bar = risks shared with the comparison seed", "S4 Leave-one-study-out rank agreement")
    return summary


if __name__ == "__main__":
    print(main())
