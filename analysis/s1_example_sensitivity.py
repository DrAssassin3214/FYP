"""S1. One-at-a-time and joint sensitivity of the ILLUSTRATIVE example case (python -m app.cli example).
Inputs: app.service.example_case(), app.service.run_case, app.engine.matrix. All example numbers are placeholders
labelled Assumption; the results describe how the ordinal classification reacts to input changes, nothing more."""
from __future__ import annotations

import copy
import itertools
import time

import numpy as np

import common as C
from app.engine import matrix as M
from app.service import example_case, run_case

FACTORS = [0.5, 0.8, 1.2, 1.5]                    # -50 %, -20 %, +20 %, +50 %
GRID = [0.5, 0.8, 1.0, 1.2, 1.5]
N_RANDOM = 5000


def run(case):
    return {m["risk_id"]: m for m in run_case(case)["matrix"]}


def scaled(case, rid=None, fp=1.0, fd=1.0):
    c = copy.deepcopy(case)
    for r in c["risks"]:
        if rid is None or r["id"] == rid:
            r["p"]["value"] = min(1.0, r["p"]["value"] * fp)
            for k in ("a", "m", "b"):
                r["delay"][k] = r["delay"][k] * fd
    return c


def p_cls_tol(p, edges=M.DEFAULT_P_EDGES):
    """Probability class with the same 1e-9 relative edge tolerance impact_class uses (diagnostic only)."""
    return 1 + sum(1 for e in edges if p >= e or np.isclose(p, e, rtol=1e-9, atol=0))


def fast(p, mean_delay, baseline, i_edges):
    pc = M.probability_class(min(1.0, p)); ic = M.impact_class(mean_delay, baseline, i_edges)
    return pc, ic, pc * ic, M.matrix_level(pc, ic)


def main():
    t0 = time.time()
    base_case = example_case()
    baseline = base_case["activity"]["planned_duration_days"]["value"]
    i_edges = base_case["impact_bin_edges_fraction"]
    base = run(base_case)
    ids = list(base)
    n_risks = len(ids)
    p0 = {r["id"]: r["p"]["value"] for r in base_case["risks"]}
    md0 = {k: v["expected_delay_if_occurs_days"] for k, v in base.items()}

    # --- one at a time (run_case) ---------------------------------------------------------------------------
    rows = []
    mismatch = 0
    for rid in ids:
        for which in ("p", "delay", "p+delay"):
            for f in FACTORS:
                fp = f if which in ("p", "p+delay") else 1.0
                fd = f if which in ("delay", "p+delay") else 1.0
                out = run(scaled(base_case, rid, fp, fd))[rid]
                pin, mdin = min(1.0, p0[rid] * fp), md0[rid] * fd
                if fast(pin, mdin, baseline, i_edges) != (out["p_class"], out["impact_class"], out["score"], out["level"]):
                    mismatch += 1
                b = base[rid]
                others_changed = sum(run_level != base[k]["level"] for k, run_level in
                                     ((k, v["level"]) for k, v in run(scaled(base_case, rid, fp, fd)).items()) if k != rid)
                rows.append({"risk_id": rid, "perturbed_input": which, "factor": f, "pct_change": round((f - 1) * 100),
                             "p_in": pin, "expected_delay_days_in": mdin, "p_class": out["p_class"],
                             "impact_class": out["impact_class"], "score": out["score"], "level": out["level"],
                             "base_p_class": b["p_class"], "base_impact_class": b["impact_class"], "base_score": b["score"],
                             "base_level": b["level"], "p_class_changed": int(out["p_class"] != b["p_class"]),
                             "impact_class_changed": int(out["impact_class"] != b["impact_class"]),
                             "level_changed": int(out["level"] != b["level"]),
                             "other_risks_level_changed": others_changed,
                             "p_on_edge_float_ambiguous": int(out["p_class"] != p_cls_tol(pin)), "n": n_risks})
    C.write_csv("s1_oat_example", rows, list(rows[0]))

    # --- joint grid: every risk's p and every risk's delay days scaled together (run_case) --------------------
    jrows = []
    jsum = []
    for fp, fd in itertools.product(GRID, GRID):
        o = run(scaled(base_case, None, fp, fd))
        ch_lv = sum(o[k]["level"] != base[k]["level"] for k in ids)
        ch_p = sum(o[k]["p_class"] != base[k]["p_class"] for k in ids)
        ch_i = sum(o[k]["impact_class"] != base[k]["impact_class"] for k in ids)
        jsum.append({"factor_p": fp, "factor_delay": fd, "n_level_changed": ch_lv, "n_p_class_changed": ch_p,
                     "n_impact_class_changed": ch_i,
                     "levels": "/".join(f"{lv}:{sum(v['level'] == lv for v in o.values())}" for lv in ("Low", "Moderate", "High", "Extreme")),
                     "n": n_risks})
        for k in ids:
            jrows.append({"factor_p": fp, "factor_delay": fd, "risk_id": k, "p_class": o[k]["p_class"],
                          "impact_class": o[k]["impact_class"], "score": o[k]["score"], "level": o[k]["level"],
                          "base_level": base[k]["level"], "level_changed": int(o[k]["level"] != base[k]["level"]), "n": n_risks})
    C.write_csv("s1_joint_grid_by_risk", jrows, list(jrows[0]))
    C.write_csv("s1_joint_grid_summary", jsum, list(jsum[0]))

    # --- joint random: every risk gets its own independent p-factor and delay-factor ~ U(0.5,1.5) -------------
    rng = np.random.default_rng(C.SEED)
    fpm = rng.uniform(0.5, 1.5, (N_RANDOM, n_risks)); fdm = rng.uniform(0.5, 1.5, (N_RANDOM, n_risks))
    cnt = {k: {"lv": 0, "pc": 0, "ic": 0, "up": 0, "down": 0} for k in ids}
    order_lv = {"Low": 0, "Moderate": 1, "High": 2, "Extreme": 3}
    n_any = []
    for d in range(N_RANDOM):
        nch = 0
        for j, k in enumerate(ids):
            pc, ic, sc, lv = fast(p0[k] * fpm[d, j], md0[k] * fdm[d, j], baseline, i_edges)
            b = base[k]
            cnt[k]["pc"] += pc != b["p_class"]; cnt[k]["ic"] += ic != b["impact_class"]
            if lv != b["level"]:
                cnt[k]["lv"] += 1; nch += 1
                cnt[k]["up" if order_lv[lv] > order_lv[b["level"]] else "down"] += 1
        n_any.append(nch)
    # cross-check the fast path against run_case on 100 random draws
    chk = 0
    for d in range(100):
        c = copy.deepcopy(base_case)
        for j, r in enumerate(c["risks"]):
            r["p"]["value"] = min(1.0, r["p"]["value"] * fpm[d, j])
            for kk in ("a", "m", "b"):
                r["delay"][kk] *= fdm[d, j]
        o = run(c)
        for j, k in enumerate(ids):
            chk += fast(p0[k] * fpm[d, j], md0[k] * fdm[d, j], baseline, i_edges)[3] != o[k]["level"]
    assert chk == 0 and mismatch == 0, (chk, mismatch)
    rrows = [{"risk_id": k, "base_p": p0[k], "base_level": base[k]["level"], "share_level_changed": cnt[k]["lv"] / N_RANDOM,
              "share_level_up": cnt[k]["up"] / N_RANDOM, "share_level_down": cnt[k]["down"] / N_RANDOM,
              "share_p_class_changed": cnt[k]["pc"] / N_RANDOM, "share_impact_class_changed": cnt[k]["ic"] / N_RANDOM,
              "n_draws": N_RANDOM, "n": n_risks} for k in ids]
    C.write_csv("s1_joint_random_by_risk", rrows, list(rrows[0]))

    # --- break-even multipliers (smallest change of ONE input that moves that risk's class / level) ------------
    gridm = np.round(np.arange(0.30, 2.0001, 0.01), 2)
    brows = []
    for k in ids:
        b = base[k]
        for which in ("p", "delay"):
            def res(f):
                return fast(p0[k] * f, md0[k], baseline, i_edges) if which == "p" else fast(p0[k], md0[k] * f, baseline, i_edges)
            def first(pred, seq):
                return next((float(f) for f in seq if pred(res(f))), None)
            up = [f for f in gridm if f > 1]; dn = [f for f in gridm[::-1] if f < 1]
            brows.append({"risk_id": k, "input": which,
                          "up_class": first(lambda r: (r[0] if which == "p" else r[1]) != (b["p_class"] if which == "p" else b["impact_class"]), up),
                          "down_class": first(lambda r: (r[0] if which == "p" else r[1]) != (b["p_class"] if which == "p" else b["impact_class"]), dn),
                          "up_level": first(lambda r: r[3] != b["level"], up), "down_level": first(lambda r: r[3] != b["level"], dn),
                          "grid": "0.30-2.00 step 0.01 (None = no change inside the grid)", "n": n_risks})
    C.write_csv("s1_breakeven", brows, list(brows[0]))

    # --- summary + figures --------------------------------------------------------------------------------------
    oat = {w: {f: sum(r["level_changed"] for r in rows if r["perturbed_input"] == w and r["factor"] == f) for f in FACTORS}
           for w in ("p", "delay", "p+delay")}
    summary = {
        "case": "ILLUSTRATIVE example (all inputs are placeholders labelled Assumption)",
        "planned_duration_days": baseline, "impact_edges_fraction": i_edges, "p_edges": list(M.DEFAULT_P_EDGES),
        "base_matrix": {k: [base[k]["p_class"], base[k]["impact_class"], base[k]["score"], base[k]["level"]] for k in ids},
        "oat_level_changes_out_of_7_by_input_and_factor": {w: {str(f): v for f, v in d.items()} for w, d in oat.items()},
        "oat_other_risks_ever_changed": int(max(r["other_risks_level_changed"] for r in rows)),
        "oat_p_edge_float_ambiguous_cases": int(sum(r["p_on_edge_float_ambiguous"] for r in rows)),
        "joint_grid_max_level_changes": max(r["n_level_changed"] for r in jsum),
        "joint_grid_cells_with_any_change": sum(r["n_level_changed"] > 0 for r in jsum if not (r["factor_p"] == 1 and r["factor_delay"] == 1)),
        "joint_grid_cells_total_excluding_base": len(jsum) - 1,
        "joint_random": {"draws": N_RANDOM, "factor_range": [0.5, 1.5], "mean_n_risks_level_changed": float(np.mean(n_any)),
                         "share_draws_with_zero_changes": float(np.mean(np.array(n_any) == 0))},
        "fast_path_vs_run_case_mismatches": int(mismatch + chk)}
    C.write_json("s1_summary", summary, {"risks": n_risks, "oat_runs": len(rows), "joint_grid_cells": len(jsum), "random_draws": N_RANDOM})

    import matplotlib.pyplot as plt
    ntxt = f"n = {n_risks} risks (example case); {len(rows)} one-at-a-time runs; {N_RANDOM} random joint draws"
    fig, axs = plt.subplots(1, 3, figsize=(12, 3.8), sharey=True)
    for ax, w, ttl in zip(axs, ("p", "delay", "p+delay"), ("Probability only", "Delay days only", "Both")):
        for i, k in enumerate(ids):
            ys = []
            for f in [0.5, 0.8, 1.0, 1.2, 1.5]:
                if f == 1.0:
                    ys.append(base[k]["score"])
                else:
                    ys.append(next(r["score"] for r in rows if r["risk_id"] == k and r["perturbed_input"] == w and r["factor"] == f))
            ax.plot([-50, -20, 0, 20, 50], ys, marker="o", ms=3, lw=1.2, color=C.OKABE[i % 7], label=k)
        for th in (5, 10, 15):
            ax.axhline(th + 0.5, color="#999999", lw=0.6, ls="--")
        ax.set_title(ttl); ax.set_xlabel("change in input (%)")
    axs[0].set_ylabel("matrix score = p class x impact class\n(dashed: level cut-offs 5/10/15)")
    axs[2].legend(fontsize=7, ncol=1, loc="center left", bbox_to_anchor=(1.0, 0.5))
    C.save_fig(fig, "s1_oat_scores", ntxt, "S1 One-at-a-time sensitivity, ILLUSTRATIVE example case")

    fig, axs = plt.subplots(1, 2, figsize=(10, 3.9), gridspec_kw={"width_ratios": [1, 1.25]})
    mat = np.array([[next(r["n_level_changed"] for r in jsum if r["factor_p"] == fp and r["factor_delay"] == fd) for fp in GRID] for fd in GRID])
    im = axs[0].imshow(mat, origin="lower", cmap="Blues", vmin=0, vmax=n_risks)
    axs[0].set_xticks(range(5), [f"x{g}" for g in GRID]); axs[0].set_yticks(range(5), [f"x{g}" for g in GRID])
    for (i, j), v in np.ndenumerate(mat):
        axs[0].text(j, i, int(v), ha="center", va="center", color="white" if v > 3 else "black")
    axs[0].set_xlabel("all probabilities scaled"); axs[0].set_ylabel("all delay days scaled")
    axs[0].set_title(f"Risks with a level change (of {n_risks})")
    y = np.arange(n_risks)
    axs[1].barh(y, [r["share_level_down"] for r in rrows], color=C.OKABE[0], label="level lower")
    axs[1].barh(y, [r["share_level_up"] for r in rrows], left=[r["share_level_down"] for r in rrows], color=C.OKABE[1], label="level higher")
    axs[1].set_yticks(y, ids); axs[1].invert_yaxis(); axs[1].set_xlim(0, 1)
    axs[1].set_xlabel(f"share of {N_RANDOM} random joint draws (each input x U(0.5, 1.5))"); axs[1].legend(fontsize=7)
    axs[1].set_title("Level change, independent random factors")
    C.save_fig(fig, "s1_joint", ntxt, "S1 Joint sensitivity, ILLUSTRATIVE example case")
    return summary


if __name__ == "__main__":
    print(main())
