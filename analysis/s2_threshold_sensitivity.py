"""S2. Threshold sensitivity on the ILLUSTRATIVE example case: shift the four probability edges, the four impact edges
and (extra) the level cut-offs, count how many of the 7 risks change class / level.
NOTE: app.service.run_case does not accept probability edges (app.engine.matrix.classify always uses DEFAULT_P_EDGES),
so probability-edge variants call app.engine.matrix.probability_class / matrix_level directly; the baseline and every
impact-edge variant are cross-checked against run_case (assert below)."""
from __future__ import annotations

import copy
import itertools
import time

import numpy as np

import common as C
from app.engine import matrix as M
from app.service import example_case, run_case

P0 = tuple(M.DEFAULT_P_EDGES)
TH0 = (5, 10, 15)
N_RANDOM = 5000


def main():
    t0 = time.time()
    case = example_case()
    baseline = case["activity"]["planned_duration_days"]["value"]
    I0 = tuple(case["impact_bin_edges_fraction"])
    risks = {r["id"]: r for r in case["risks"]}
    ids = list(risks)
    n = len(ids)
    p = {k: risks[k]["p"]["value"] for k in ids}
    md = {k: v["expected_delay_if_occurs_days"] for k, v in ((m["risk_id"], m) for m in run_case(case)["matrix"])}

    def evaluate(pe=P0, ie=I0, th=TH0):
        out = {}
        for k in ids:
            pc = M.probability_class(p[k], pe); ic = M.impact_class(md[k], baseline, ie)
            out[k] = (pc, ic, M.matrix_level(pc, ic, th))
        return out

    base = evaluate()
    rc = {m["risk_id"]: (m["p_class"], m["impact_class"], m["level"]) for m in run_case(case)["matrix"]}
    assert base == rc, (base, rc)

    def valid(e):
        return all(0 < a < b < 1 for a, b in zip(e, e[1:])) and 0 < e[0] and e[-1] < 1

    scenarios = []   # (group, name, pe, ie, th)
    for j in range(4):
        for d in (-0.10, -0.05, 0.05, 0.10):
            pe = list(P0); pe[j] = round(pe[j] + d, 4)
            if valid(pe):
                scenarios.append(("p_edge_single_shift", f"p edge {j + 1} ({P0[j]:g}) {d:+.2f}", tuple(pe), I0, TH0))
    for d in (-0.10, -0.05, 0.05, 0.10):
        pe = tuple(round(e + d, 4) for e in P0)
        if valid(pe):
            scenarios.append(("p_edges_all_shift", f"all four p edges {d:+.2f}", pe, I0, TH0))
    for name, pe in (("alt: 0.1/0.3/0.5/0.7", (0.1, 0.3, 0.5, 0.7)), ("alt: 0.25/0.45/0.65/0.85", (0.25, 0.45, 0.65, 0.85)),
                     ("alt: 0.05/0.15/0.35/0.65 (low-skewed)", (0.05, 0.15, 0.35, 0.65)),
                     ("alt: 0.35/0.65/0.85/0.95 (high-skewed)", (0.35, 0.65, 0.85, 0.95))):
        scenarios.append(("p_edge_alternative_set", name, pe, I0, TH0))
    for j in range(4):
        for f in (0.5, 0.75, 1.25, 1.5, 2.0):
            ie = list(I0); ie[j] = round(ie[j] * f, 6)
            if valid(ie):
                scenarios.append(("impact_edge_single_scale", f"impact edge {j + 1} ({I0[j]:g}) x{f:g}", P0, tuple(ie), TH0))
    for f in (0.5, 0.75, 1.25, 1.5, 2.0):
        scenarios.append(("impact_edges_all_scale", f"all four impact edges x{f:g}", P0, tuple(round(e * f, 6) for e in I0), TH0))
    for name, ie in (("alt: 0.05/0.10/0.20/0.30", (0.05, 0.10, 0.20, 0.30)), ("alt: 0.01/0.025/0.05/0.10", (0.01, 0.025, 0.05, 0.10)),
                     ("alt: equal width 0.2/0.4/0.6/0.8", (0.2, 0.4, 0.6, 0.8))):
        scenarios.append(("impact_edge_alternative_set", name, P0, ie, TH0))
    for th in ((4, 9, 15), (4, 8, 12), (6, 12, 16), (3, 8, 14), (5, 12, 19), (6, 10, 15), (5, 10, 20)):
        scenarios.append(("level_cutoff_alternative", f"cut-offs {th}", P0, I0, th))

    srows = []; lvl_changed = {}
    for g, name, pe, ie, th in scenarios:
        if g.startswith("impact_edge") and th == TH0 and pe == P0:      # cross-check impact edges through run_case
            c = copy.deepcopy(case); c["impact_bin_edges_fraction"] = list(ie)
            rcv = {m["risk_id"]: (m["p_class"], m["impact_class"], m["level"]) for m in run_case(c)["matrix"]}
            assert rcv == evaluate(pe, ie, th), name
        ev = evaluate(pe, ie, th)
        ch = [k for k in ids if ev[k][2] != base[k][2]]
        lvl_changed[name] = {k: int(ev[k][2] != base[k][2]) for k in ids}
        srows.append({"group": g, "scenario": name, "p_edges": "/".join(f"{e:g}" for e in pe),
                      "impact_edges": "/".join(f"{e:g}" for e in ie), "level_cutoffs": "/".join(map(str, th)),
                      "n_p_class_changed": sum(ev[k][0] != base[k][0] for k in ids),
                      "n_impact_class_changed": sum(ev[k][1] != base[k][1] for k in ids),
                      "n_level_changed": len(ch), "risks_level_changed": " ".join(ch), "n": n})
    C.write_csv("s2_threshold_scenarios", srows, list(srows[0]))

    # random jitter of edges (seeded)
    rng = np.random.default_rng(C.SEED)
    rr = {"p_edges_jitter_abs_0.05": [], "impact_edges_jitter_rel_50pct": [], "both": []}
    per_risk = {k: 0 for k in ids}
    for _ in range(N_RANDOM):
        pe = tuple(sorted(np.clip(np.array(P0) + rng.uniform(-0.05, 0.05, 4), 0.001, 0.999)))
        ie = tuple(sorted(np.array(I0) * rng.uniform(0.5, 1.5, 4)))
        for key, (a, b) in (("p_edges_jitter_abs_0.05", (pe, I0)), ("impact_edges_jitter_rel_50pct", (P0, ie)), ("both", (pe, ie))):
            ev = evaluate(a, b)
            ch = sum(ev[k][2] != base[k][2] for k in ids); rr[key].append(ch)
            if key == "both":
                for k in ids:
                    per_risk[k] += ev[k][2] != base[k][2]
    jrows = [{"scenario": k, "draws": N_RANDOM, "mean_n_level_changed": float(np.mean(v)), "median_n_level_changed": float(np.median(v)),
              "p95_n_level_changed": float(np.percentile(v, 95)), "max_n_level_changed": int(max(v)),
              "share_draws_no_change": float(np.mean(np.array(v) == 0)), "n": n} for k, v in rr.items()]
    C.write_csv("s2_threshold_random_jitter", jrows, list(jrows[0]))
    C.write_csv("s2_threshold_random_jitter_by_risk", [{"risk_id": k, "share_level_changed_both_jitter": per_risk[k] / N_RANDOM,
                                                       "draws": N_RANDOM, "n": n} for k in ids], ["risk_id", "share_level_changed_both_jitter", "draws", "n"])

    # exhaustive level cut-off triples
    chs = []
    for t in itertools.combinations(range(1, 25), 3):
        ev = evaluate(th=t); chs.append(sum(ev[k][2] != base[k][2] for k in ids))
    cut_summary = {"triples_tested": len(chs), "median_n_level_changed": float(np.median(chs)),
                   "iqr": [float(np.percentile(chs, 25)), float(np.percentile(chs, 75))]}

    # margins: how close is each risk to its nearest edge
    mrows = []
    for k in ids:
        ratio = md[k] / baseline
        dp = min(abs(p[k] - e) for e in P0); di = min(abs(ratio - e) / e for e in I0)
        mrows.append({"risk_id": k, "p": p[k], "nearest_p_edge_distance_abs": dp, "expected_delay_days": md[k],
                      "delay_over_baseline": ratio, "nearest_impact_edge_distance_rel": di,
                      "p_class": base[k][0], "impact_class": base[k][1], "level": base[k][2], "n": n})
    C.write_csv("s2_edge_margins", mrows, list(mrows[0]))

    by_group = {}
    for r in srows:
        by_group.setdefault(r["group"], []).append(r["n_level_changed"])
    summary = {"case": "ILLUSTRATIVE example (placeholders)", "n_scenarios": len(srows),
               "level_changes_out_of_7_by_group": {g: {"scenarios": len(v), "min": min(v), "median": float(np.median(v)), "max": max(v)} for g, v in by_group.items()},
               "random_jitter": {r["scenario"]: {k: r[k] for k in ("mean_n_level_changed", "p95_n_level_changed", "max_n_level_changed", "share_draws_no_change")} for r in jrows},
               "level_cutoff_triples_1_to_24": cut_summary,
               "probability_edges_not_exposed_by_run_case": True}
    C.write_json("s2_summary", summary, {"risks": n, "scenarios": len(srows), "random_draws": N_RANDOM})

    import matplotlib.pyplot as plt
    ntxt = f"n = {n} risks (example case); {len(srows)} named scenarios; {N_RANDOM} random edge draws"
    names = [r["scenario"] for r in srows]
    mat = np.array([[lvl_changed[nm][k] for k in ids] for nm in names])
    fig, ax = plt.subplots(figsize=(6.8, 0.22 * len(names) + 1.6))
    ax.imshow(mat, aspect="auto", cmap="Oranges", vmin=0, vmax=1)
    ax.set_xticks(range(n), ids, rotation=45, ha="right"); ax.set_yticks(range(len(names)), names, fontsize=6.5)
    for i, r in enumerate(srows):
        ax.text(n - 0.35, i, str(r["n_level_changed"]), va="center", fontsize=6.5, color="#333333")
    ax.set_xlim(-0.5, n + 0.2); ax.spines[:].set_visible(False)
    ax.set_title("shaded = that risk's matrix level differs from base; right-hand number = count of 7", fontsize=8)
    C.save_fig(fig, "s2_threshold_scenarios", ntxt, "S2 Threshold sensitivity by scenario, ILLUSTRATIVE example case")

    fig, axs = plt.subplots(1, 2, figsize=(9, 3.4))
    for i, (k, v) in enumerate(rr.items()):
        axs[0].hist(v, bins=np.arange(-0.5, n + 1.5, 1), alpha=0.55, color=C.OKABE[i], label=k.replace("_", " "))
    axs[0].set_xlabel("risks (of 7) with a level change"); axs[0].set_ylabel(f"draws (of {N_RANDOM})"); axs[0].legend(fontsize=6.5)
    axs[0].set_title("Random edge jitter")
    axs[1].barh(range(n), [per_risk[k] / N_RANDOM for k in ids], color=C.OKABE[0]); axs[1].set_yticks(range(n), ids); axs[1].invert_yaxis()
    axs[1].set_xlabel("share of draws, both edge sets jittered"); axs[1].set_xlim(0, 1)
    axs[1].set_title("Per-risk share with a level change")
    C.save_fig(fig, "s2_threshold_random", ntxt, "S2 Threshold jitter, ILLUSTRATIVE example case")
    return summary


if __name__ == "__main__":
    print(main())
