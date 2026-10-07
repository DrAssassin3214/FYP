"""Statistical analysis of the TOOL: how reliable is the literature ranking that places risks on the matrix?

The tool turns survey importance indices (RII) into a rank and a 5-band class per risk (app/literature_seed.py), for two bases:
  seed : 5 seed studies, direct matches only (6 studies held out for validation)
  all  : all 11 studies, direct + related matches
This script measures, for each basis and each of the 38 library risks:
  * the point estimate (mean of per-study means), rank and class exactly as the app computes them;
  * a bootstrap over STUDIES (resample the studies with replacement, 5,000 times, recompute rank and class): 95% rank interval,
    how often the risk keeps its class, and how often it is even covered;
  * agreement between the two bases (Spearman, Kendall tau, exact and +-1 class agreement);
and it summarises the existing validation results in docs/rii_statistics.json (held-out studies, Kendall's W, leave-one-out).
The unit of analysis is the STUDY (n = 5 or 11): intervals are wide because few studies cover each risk, and that is reported, not hidden.

Run: python scripts/stats_tool.py -> docs/tool_statistics.json and docs/Tool_Statistical_Analysis.md
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.literature_seed import N_CLASSES, load_dataset, seed_observations, seed_table  # noqa: E402

B = 5000
RNG = np.random.default_rng(20261007)
# rows checked against the paper's own tables on 2026-10-07 (Research_Notes/fulltext_review/README.md); agent-reported, not re-keyed by hand
VERIFIED = {"M01": 28, "M06": 40, "M10": 33, "M14": 23, "M15": 24, "A10": 6, "A14": 5, "A21": 2}


def per_study(basis: str) -> dict[str, dict[str, float]]:
    obs = seed_observations(load_dataset(), basis)
    tmp: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for o in obs:
        tmp[o["risk"]][o["study"]].append(o["rii"])
    return {r: {s: mean(v) for s, v in d.items()} for r, d in tmp.items()}


def classes(means: dict[str, float]) -> tuple[dict[str, int], dict[str, int]]:
    order = sorted(means, key=lambda r: (-means[r], r))
    n = len(order)
    rank = {r: i + 1 for i, r in enumerate(order)}
    cls = {r: N_CLASSES - ((rank[r] - 1) * N_CLASSES) // n for r in order}
    return rank, cls


def bootstrap(ps: dict[str, dict[str, float]], studies: list[str]) -> dict[str, dict]:
    point = {r: mean(d.values()) for r, d in ps.items() if d}
    rank0, cls0 = classes(point)
    rk: dict[str, list[float]] = defaultdict(list)
    same: dict[str, int] = defaultdict(int)
    for _ in range(B):
        draw = [studies[i] for i in RNG.integers(0, len(studies), len(studies))]
        m = {}
        for r, d in ps.items():
            v = [d[s] for s in draw if s in d]
            if v:
                m[r] = mean(v)
        if len(m) < 5:
            continue
        rank, cls = classes(m)
        for r in m:
            if r in point:
                rk[r].append(rank[r] / len(m))                # rank as a share of the risks present, so draws of different size compare
                same[r] += cls[r] == cls0[r]
    out = {}
    for r in point:
        x = np.array(rk[r])
        lo, hi = (np.percentile(x, [2.5, 97.5]) if len(x) else (np.nan, np.nan))
        out[r] = {"mean_rii": point[r], "rank": rank0[r], "n_ranked": len(point), "class": cls0[r], "n_studies": len(ps[r]),
                  "rank_share_lo": float(lo), "rank_share_hi": float(hi), "covered": len(x) / B,
                  "class_kept": same[r] / max(len(x), 1)}
    return out


def main() -> int:
    data = load_dataset()
    studies_all = [s["id"] for s in data["studies"]]
    roles = {s["id"]: s["role"] for s in data["studies"]}
    res: dict = {"verified_rows": VERIFIED, "bases": {}}
    for basis in ("seed", "all"):
        ps = per_study(basis)
        used = sorted({s for d in ps.values() for s in d})
        bt = bootstrap(ps, used)
        t = seed_table(basis)
        assert all(bt[r]["rank"] == t[r]["rank"] and bt[r]["class"] == t[r]["class"] for r in bt), "bootstrap point estimate disagrees with the app"
        ks = np.array([v["class_kept"] for v in bt.values()])
        ns = np.array([v["n_studies"] for v in bt.values()])
        res["bases"][basis] = {"studies": used, "risks": bt,
                               "summary": {"n_risks": len(bt), "n_studies": len(used), "median_studies_per_risk": float(np.median(ns)),
                                           "risks_with_one_study": int((ns == 1).sum()), "mean_class_kept": float(ks.mean()),
                                           "share_class_kept_ge_50": float((ks >= 0.5).mean()),
                                           "median_rank_interval_width_share": float(np.nanmedian([v["rank_share_hi"] - v["rank_share_lo"] for v in bt.values()]))}}
    a, b = res["bases"]["seed"]["risks"], res["bases"]["all"]["risks"]
    common = sorted(set(a) & set(b))
    ra, rb = [a[r]["rank"] / a[r]["n_ranked"] for r in common], [b[r]["rank"] / b[r]["n_ranked"] for r in common]
    rho, p_rho = stats.spearmanr(ra, rb)
    tau, p_tau = stats.kendalltau(ra, rb)
    ca, cb = np.array([a[r]["class"] for r in common]), np.array([b[r]["class"] for r in common])
    res["agreement"] = {"n_common": len(common), "spearman": rho, "p_spearman": p_rho, "kendall_tau": tau, "p_tau": p_tau,
                        "exact_class": float((ca == cb).mean()), "within_one_class": float((abs(ca - cb) <= 1).mean())}
    old = json.loads((ROOT / "docs" / "rii_statistics.json").read_text(encoding="utf-8"))
    res["existing"] = {"validation": old["validation"], "kendall_w": old["kendall_w"], "leave_one_out": old["leave_one_study_out"],
                       "pairwise_summary": old["pairwise_summary"], "weighted_vs_unweighted_rho": old["weighted_vs_unweighted"]["rho"]}
    res["roles"] = roles
    (ROOT / "docs" / "tool_statistics.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")
    write_md(res, data)
    print("wrote docs/tool_statistics.json and docs/Tool_Statistical_Analysis.md")
    return 0


def f(x, d=2):
    return "NR" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{d}f}"


def pv(p):
    return "<0.001" if p < 0.001 else f"{p:.3f}"


def write_md(R: dict, data: dict) -> None:
    S, A = R["bases"]["seed"], R["bases"]["all"]
    names = {}
    try:
        names = {r["id"]: r["name"] for r in json.loads((ROOT / "data" / "risk_library_masonry.json").read_text(encoding="utf-8-sig"))}
    except Exception:
        pass
    L = ["# Statistical analysis of the tool's literature ranking", "",
         "Generated by `scripts/stats_tool.py` (fixed seed, 5,000 bootstrap draws). It measures how reliable the survey-based rank and class are that the "
         "tool uses to place library risks on the 5x5 matrix when no probability or delay is entered. The unit of analysis is the **study**, not the respondent: "
         "the tool averages each study's items first, then averages across studies.", "",
         "## 1. Data behind the ranking", "",
         f"The dataset holds {len(data['studies'])} RII studies and {len(data['rows'])} factor rows. Studies, their role, respondents and scale:", "",
         "| Study | Country | Role | n | Scale | Rows |", "|---|---|---|---|---|---:|"]
    cnt = defaultdict(int)
    for r in data["rows"]:
        cnt[r["study"]] += 1
    for s in data["studies"]:
        L.append(f"| {s['id']} | {s.get('country', '')} | {s['role']} | {s.get('n', 'NR')} | {s.get('scale', 'NR')} | {cnt[s['id']]} |")
    ver = sum(R["verified_rows"].values())
    L += ["", f"**Transcription check:** {ver} rows from {len(R['verified_rows'])} studies ({', '.join(f'{k} {v}' for k, v in R['verified_rows'].items())}) were compared with "
          "the papers' own tables on 2026-10-07 and all matched (agent-reported, see `Research_Notes/fulltext_review/README.md`). The rows of the other studies "
          "rest on earlier research notes: A02, A15 and HAS25 could not be downloaded (publisher servers refused), so their depth is lower.", "",
          "## 2. How the tool turns the data into a placement", "",
          "Per risk: mean of each study's items, then mean across studies, rank by that mean, five equal-count bands (class 5 = most important). "
          "The class is used for both matrix axes, so it is an **ordinal prioritisation**, not a probability or a delay. Two bases: **seed** "
          f"({S['summary']['n_studies']} studies, direct matches) and **all** ({A['summary']['n_studies']} studies, direct and related matches).", "",
          "## 3. Stability of the ranking (bootstrap over studies)", "",
          "| | Seed basis | All-studies basis |", "|---|---:|---:|",
          f"| Risks placed | {S['summary']['n_risks']} | {A['summary']['n_risks']} |",
          f"| Studies used | {S['summary']['n_studies']} | {A['summary']['n_studies']} |",
          f"| Median studies per risk | {f(S['summary']['median_studies_per_risk'], 1)} | {f(A['summary']['median_studies_per_risk'], 1)} |",
          f"| Risks resting on a single study | {S['summary']['risks_with_one_study']} | {A['summary']['risks_with_one_study']} |",
          f"| Mean share of draws keeping the same class | {S['summary']['mean_class_kept']:.0%} | {A['summary']['mean_class_kept']:.0%} |",
          f"| Risks that keep their class in at least half the draws | {S['summary']['share_class_kept_ge_50']:.0%} | {A['summary']['share_class_kept_ge_50']:.0%} |",
          f"| Median width of the 95% rank interval (share of the list) | {S['summary']['median_rank_interval_width_share']:.0%} | {A['summary']['median_rank_interval_width_share']:.0%} |", "",
          "Reading: an interval width of 50% of the list means a risk's rank is only known to within half the list. Few studies cover each risk, so classes are "
          "unstable for many risks; the placement is a starting order, which is how the tool labels it.", "",
          ("The all-studies basis places more risks but is " + ("LESS" if A["summary"]["mean_class_kept"] < S["summary"]["mean_class_kept"] else "more") +
           " stable than the seed basis here: the held-out studies bring different rankings (section 6), which widens the intervals. Using all the data therefore "
           "buys coverage (every library risk placed), not precision; the default stays on the seed basis."), "",
          "## 4. Per-risk results", "",
          "Rank is shown as rank/number ranked. The interval is the bootstrap 95% range of the rank as a share of the list (0% = top). 'Class kept' is the share of "
          "draws, among those in which a resampled study covers the risk, in which it stays in its class.", "",
          "| Risk | Name | Seed: rank | Class | Studies | 95% interval | Class kept | All: rank | Class | Studies | 95% interval | Class kept |",
          "|---|---|---:|---:|---:|---|---:|---:|---:|---:|---|---:|"]
    for rid in sorted(A["risks"]):
        s, a = S["risks"].get(rid), A["risks"][rid]
        sc = (f"{s['rank']}/{s['n_ranked']} | {s['class']} | {s['n_studies']} | {s['rank_share_lo']:.0%}-{s['rank_share_hi']:.0%} | {s['class_kept']:.0%}"
              if s else "not seeded | | | | ")
        L.append(f"| {rid} | {names.get(rid, '')[:38]} | {sc} | {a['rank']}/{a['n_ranked']} | {a['class']} | {a['n_studies']} | "
                 f"{a['rank_share_lo']:.0%}-{a['rank_share_hi']:.0%} | {a['class_kept']:.0%} |")
    g = R["agreement"]
    L += ["", "## 5. Do the two bases agree?", "",
          f"On the {g['n_common']} risks ranked in both: Spearman rho = {g['spearman']:.2f} (p {pv(g['p_spearman'])}), Kendall tau = {g['kendall_tau']:.2f} (p {pv(g['p_tau'])}); "
          f"same class for {g['exact_class']:.0%} of risks, within one class for {g['within_one_class']:.0%}. "
          "The all-studies basis adds the held-out studies and weaker 'related' matches, so agreement below 1 is expected; it shows how much the choice of basis moves the placement.", "",
          "## 6. Validation against held-out studies (default basis)", "",
          "| Held-out study | Risks compared | Spearman rho | p (permutation) | 95% CI for rho |", "|---|---:|---:|---:|---|"]
    for v in R["existing"]["validation"]:
        if v.get("tested"):
            L.append(f"| {v['study']} | {v['n']} | {v['rho']:.2f} | {pv(v['p_perm'])} | {v['ci95_lo']:.2f} to {v['ci95_hi']:.2f} |")
    kw = R["existing"]["kendall_w"]
    lo = min(x["rho_vs_full_seed"] for x in R["existing"]["leave_one_out"])
    ps = R["existing"]["pairwise_summary"]
    L += ["", f"Agreement among studies on shared risks: mean pairwise Spearman {ps['mean_rho']:.2f} (median {ps['median_rho']:.2f}, range {ps['min']:.2f} to {ps['max']:.2f}, {ps['n_pairs']} pairs); "
          f"Kendall's W = {kw['W']:.2f} over {kw['k']} studies and {kw['n']} risks (p {pv(kw['p'])}). "
          f"Dropping any one seed study keeps rho with the full seed ranking at {lo:.2f} or higher. Weighting by respondent numbers gives rho {R['existing']['weighted_vs_unweighted_rho']:.2f} with the unweighted ranking.", "",
          "## 7. What this means for using the tool", "",
          "* The placement is a **relative starting order**. Where studies agree, it is a defensible prioritisation; where a risk rests on one study or the interval spans much of the list, treat its class as provisional.",
          "* Held-out agreement is mixed: see the table in section 6. A result that is not significant, or negative, is reported as it is; it is why the tool states that a survey importance index is not a probability or a number of days.",
          "* Entering a probability and a delay range for a risk replaces its placement; the statistics above then no longer apply to that risk.",
          "* Pooling all studies uses all the data but removes the held-out check, so its agreement with other studies can no longer be tested.",
          "* RII scales differ between studies (1-4 vs 1-5) and several studies print only their top factors, so values are comparable as rankings, not as magnitudes.", ""]
    (ROOT / "docs" / "Tool_Statistical_Analysis.md").write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())

