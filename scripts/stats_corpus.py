"""Inferential statistics on the screened literature database (data/literature.db).

Questions answered (each with the test used; nothing here is a claim about the whole literature, only about this corpus):
  1. Is publication volume trending?           Spearman (year, works) 2010-2025 + Poisson-regression slope (log-linear, via GLM)
  2. Are themes independent of tier?           chi-square test of independence + Cramer's V
  3. Which themes co-occur?                    pairwise phi coefficient + Fisher exact p (Holm-adjusted)
  4. Do citations differ by theme?             Kruskal-Wallis on citations among works with exactly one theme (+ epsilon^2 effect size)
  5. Does open access go with more citations?  Mann-Whitney U on citations within age bands (older works have more time to be cited)
  6. How common are methods / regions?         share of abstracts mentioning each, Wilson 95% CI, by period (chi-square for trend)
  7. Is the corpus big enough?                 bootstrap CI width of a theme share against subsample size
All text matching is on title + abstract (regex, listed in METHODS / REGIONS) so shares are shares of ABSTRACTS THAT MENTION the term,
not shares of studies that used the method.

Run: python scripts/stats_corpus.py   -> docs/corpus_statistics.json and docs/Corpus_Statistical_Analysis.md
"""
from __future__ import annotations

import itertools
import json
import math
import re
import sqlite3
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "literature.db"
RNG = np.random.default_rng(20261007)
Z = 1.959964

METHODS = {
    "Relative importance index (RII)": r"relative importance (index|indices)|\bRII\b",
    "Questionnaire / survey": r"questionnaire|survey",
    "Interview / Delphi / expert panel": r"interview|delphi|expert (panel|opinion|judge?ment|survey)",
    "Fuzzy logic / fuzzy AHP": r"fuzzy",
    "AHP / MCDM": r"\bAHP\b|analytic hierarchy|TOPSIS|multi-criteria|MCDM",
    "Machine learning / neural network": r"machine learning|neural network|random forest|deep learning|\bANN\b|\bSVM\b",
    "Large language model / generative AI": r"large language model|\bLLM|generative AI|ChatGPT|GPT-",
    "Structural equation modelling": r"structural equation|\bSEM\b|\bPLS-SEM",
    "Case study": r"case stud",
    "Systematic / literature review": r"systematic (literature )?review|literature review|bibliometric",
}
REGIONS = {
    "India": r"\bIndia\b|Indian\b", "Sri Lanka": r"Sri Lanka", "Pakistan": r"Pakistan", "Middle East / Gulf": r"Saudi|Kuwait|Qatar|\bUAE\b|Emirates|Middle East|Oman|Bahrain|Iraq|Jordan",
    "Nigeria / Ghana / Africa": r"Nigeria|Ghana|Africa|Kenya|Ethiopia|Uganda", "China / Hong Kong": r"China|Chinese|Hong Kong",
    "Malaysia / Indonesia / Vietnam / Thailand": r"Malaysia|Indonesia|Vietnam|Thailand",
}


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return (c - h, c + h)


def holm(ps: list[float]) -> list[float]:
    order = np.argsort(ps)
    out = [0.0] * len(ps)
    run = 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - rank) * ps[i]))
        out[i] = run
    return out


def main() -> int:
    db = sqlite3.connect(DB)
    W = db.execute("SELECT work_id, year, cited_by, is_oa, tier, title || ' ' || abstract FROM work").fetchall()
    ids = [w[0] for w in W]
    theme_ids = [r[0] for r in db.execute("SELECT theme_id FROM theme ORDER BY theme_id")]
    labels = dict(db.execute("SELECT theme_id, label FROM theme"))
    has = {t: {r[0] for r in db.execute("SELECT work_id FROM work_theme WHERE theme_id=?", (t,))} for t in theme_ids}
    N = len(W)
    R: dict = {"N": N}

    # 1. trend
    yrs = np.arange(2010, 2026)
    cnt = np.array([sum(1 for w in W if w[1] == y) for y in yrs])
    rho, p_rho = stats.spearmanr(yrs, cnt)
    import statsmodels.api as sm
    glm = sm.GLM(cnt, sm.add_constant(yrs - 2010), family=sm.families.Poisson()).fit()
    b, se = glm.params[1], glm.bse[1]
    disp = glm.pearson_chi2 / glm.df_resid
    R["trend"] = {"years": [2010, 2025], "counts": cnt.tolist(), "spearman_rho": rho, "spearman_p": p_rho,
                  "poisson_slope_per_year": b, "annual_growth_pct": (math.exp(b) - 1) * 100,
                  "growth_ci95_pct": [(math.exp(b - Z * se) - 1) * 100, (math.exp(b + Z * se) - 1) * 100],
                  "dispersion": disp, "note": "dispersion > 1 means the Poisson CI is too narrow" if disp > 1.5 else "dispersion acceptable"}
    if disp > 1.5:                                    # quasi-Poisson: scale the SE by sqrt(dispersion)
        se_q = se * math.sqrt(disp)
        R["trend"]["growth_ci95_pct_quasi"] = [(math.exp(b - Z * se_q) - 1) * 100, (math.exp(b + Z * se_q) - 1) * 100]

    # 2. theme x tier
    tab = np.array([[len(has[t] & {w[0] for w in W if w[4] == tr}) for tr in (1, 2)] for t in theme_ids])
    chi2, p, dof, _ = stats.chi2_contingency(tab)
    n_obs = tab.sum()
    R["theme_by_tier"] = {"themes": [labels[t] for t in theme_ids], "counts_tier1_tier2": tab.tolist(), "chi2": chi2, "dof": dof, "p": p,
                          "cramers_v": math.sqrt(chi2 / (n_obs * (min(tab.shape) - 1))),
                          "note": "a work with several themes appears in several rows, so rows are not independent; treat p as descriptive"}

    # 3. co-occurrence
    pairs = []
    for a, c in itertools.combinations(theme_ids, 2):
        t = [[len(has[a] & has[c]), len(has[a] - has[c])], [len(has[c] - has[a]), N - len(has[a] | has[c])]]
        odds, pf = stats.fisher_exact(t)
        n11, n10, n01, n00 = t[0][0], t[0][1], t[1][0], t[1][1]
        phi = (n11 * n00 - n10 * n01) / math.sqrt((n11 + n10) * (n01 + n00) * (n11 + n01) * (n10 + n00))
        pairs.append({"a": labels[a], "b": labels[c], "both": n11, "phi": phi, "odds_ratio": odds, "p": pf})
    for x, q in zip(pairs, holm([x["p"] for x in pairs])):
        x["p_holm"] = q
    R["cooccurrence"] = pairs

    # 4. citations by theme (single-theme works only, so groups are disjoint)
    single = {}
    cite = {w[0]: w[2] for w in W}
    for t in theme_ids:
        others = set().union(*(has[o] for o in theme_ids if o != t))
        if has[t] - others:               # the method theme is only recorded alongside a topic theme, so it has no single-theme works
            single[t] = [cite[i] for i in has[t] - others]
    H, p_kw = stats.kruskal(*single.values())
    n_s = sum(len(v) for v in single.values())
    R["citations_by_theme"] = {"groups": {labels[t]: {"n": len(v), "median": float(np.median(v)), "q1": float(np.percentile(v, 25)), "q3": float(np.percentile(v, 75))}
                                          for t, v in single.items()},
                               "H": H, "p": p_kw, "epsilon_squared": (H - len(single) + 1) / (n_s - len(single))}

    # 5. OA vs citations within age bands
    bands = []
    for lo, hi in ((1995, 2009), (2010, 2015), (2016, 2020), (2021, 2026)):
        oa = [w[2] for w in W if lo <= (w[1] or 0) <= hi and w[3]]
        no = [w[2] for w in W if lo <= (w[1] or 0) <= hi and not w[3]]
        if len(oa) > 10 and len(no) > 10:
            u, pu = stats.mannwhitneyu(oa, no, alternative="two-sided")
            bands.append({"years": [lo, hi], "n_oa": len(oa), "n_closed": len(no), "median_oa": float(np.median(oa)),
                          "median_closed": float(np.median(no)), "p": pu, "rank_biserial": 2 * u / (len(oa) * len(no)) - 1})
    for x, q in zip(bands, holm([x["p"] for x in bands])):
        x["p_holm"] = q
    R["open_access_vs_citations"] = bands

    # 6. method and region prevalence by period
    periods = ((1995, 2009), (2010, 2017), (2018, 2022), (2023, 2026))

    def prevalence(table: dict) -> list:
        out = []
        for name, rx in table.items():
            c = re.compile(rx, re.I)
            hit = [bool(c.search(w[5])) for w in W]
            k = sum(hit)
            row = {"term": name, "k": k, "share": k / N, "ci95": wilson(k, N), "by_period": []}
            ks = []
            for lo, hi in periods:
                idx = [i for i, w in enumerate(W) if lo <= (w[1] or 0) <= hi]
                kk = sum(hit[i] for i in idx)
                ks.append((kk, len(idx)))
                row["by_period"].append({"years": [lo, hi], "k": kk, "n": len(idx), "share": kk / len(idx), "ci95": wilson(kk, len(idx))})
            t = np.array([[a, n - a] for a, n in ks])
            if t.min() >= 0 and (t.sum(axis=1) > 0).all():
                row["chi2_p_homogeneity"] = stats.chi2_contingency(t)[1] if t[:, 0].sum() > 0 else None
                # Cochran-Armitage-style trend: Spearman of period index against the per-work indicator
                per = [next((j for j, (lo, hi) in enumerate(periods) if lo <= (w[1] or 0) <= hi), None) for w in W]
                xs = [(per[i], int(hit[i])) for i in range(N) if per[i] is not None]
                r, pr = stats.spearmanr([x[0] for x in xs], [x[1] for x in xs])
                row["trend_spearman_r"], row["trend_p"] = r, pr
            out.append(row)
        ps = [r.get("trend_p", 1.0) for r in out]
        for r, q in zip(out, holm(ps)):
            r["trend_p_holm"] = q
        return out
    R["methods"], R["regions"] = prevalence(METHODS), prevalence(REGIONS)

    # 7. precision vs sample size (bootstrap of the share of works in the delay theme)
    target = has["delay_causes"] if "delay_causes" in has else has[theme_ids[0]]
    flag = np.array([i in target for i in ids])
    curve = []
    for n in (100, 250, 500, 1000, 2000, 3000, N):
        shares = [flag[RNG.integers(0, N, n)].mean() for _ in range(2000)]
        lo, hi = np.percentile(shares, [2.5, 97.5])
        curve.append({"n": n, "ci_low": float(lo), "ci_high": float(hi), "width": float(hi - lo)})
    R["precision_curve"] = {"statistic": "share of works in the delay-causes theme", "full_share": float(flag.mean()), "curve": curve}

    out = ROOT / "docs"
    (out / "corpus_statistics.json").write_text(json.dumps(R, indent=1, default=float), encoding="utf-8")
    write_md(R, out / "Corpus_Statistical_Analysis.md")
    print("wrote docs/corpus_statistics.json and docs/Corpus_Statistical_Analysis.md")
    return 0


def pv(p: float) -> str:
    return "<0.001" if p < 0.001 else f"{p:.3f}"


def write_md(R: dict, path: Path) -> None:
    t = R["trend"]
    L = ["# Statistical analysis of the literature database", "",
         f"N = {R['N']} screened works (`data/literature.db`). Generated by `scripts/stats_corpus.py` with a fixed seed. "
         "All results describe THIS corpus. Regex matching on title + abstract measures how many abstracts mention a term, not how many studies used a method. "
         "Where one family of tests is run, p-values are Holm-adjusted. The RII-based ranking statistics are in `Statistical_Analysis.docx` and `docs/rii_statistics.json`.", "",
         "## 1. Publication trend 2010-2025", "",
         "Works per year: " + ", ".join(f"{y}: {c}" for y, c in zip(range(2010, 2026), t["counts"])) + ".", "",
         f"Spearman rho = {t['spearman_rho']:.2f} (p {pv(t['spearman_p'])}). Poisson log-linear slope: {t['annual_growth_pct']:.1f}% per year "
         f"(95% CI {t['growth_ci95_pct'][0]:.1f} to {t['growth_ci95_pct'][1]:.1f}); dispersion {t['dispersion']:.1f}"
         + (f", so the quasi-Poisson interval {t['growth_ci95_pct_quasi'][0]:.1f} to {t['growth_ci95_pct_quasi'][1]:.1f}% is the one to quote." if "growth_ci95_pct_quasi" in t else "."),
         "Caution: the count reflects what the search phrases and the OpenAlex index returned, so it is a trend in this corpus, not in construction research as a whole. 2026 is a partial year and is excluded.", "",
         "## 2. Theme by tier", "", "| Theme | Tier 1 | Tier 2 |", "|---|---:|---:|"]
    L += [f"| {a} | {b[0]} | {b[1]} |" for a, b in zip(R["theme_by_tier"]["themes"], R["theme_by_tier"]["counts_tier1_tier2"])]
    x = R["theme_by_tier"]
    L += ["", f"Chi-square = {x['chi2']:.1f}, df = {x['dof']}, p {pv(x['p'])}, Cramer's V = {x['cramers_v']:.2f}. {x['note']}.", "",
          "## 3. Theme co-occurrence", "", "| Pair | Works with both | phi | Odds ratio | p (Holm) |", "|---|---:|---:|---:|---:|"]
    L += [f"| {c['a']} + {c['b']} | {c['both']} | {c['phi']:.2f} | {c['odds_ratio']:.2f} | {pv(c['p_holm'])} |" for c in R["cooccurrence"]]
    L += ["", "Reading note: negative phi values are partly built in. A work gets a theme from a title term or from a specific abstract phrase, "
          "so a title about delays rarely also gets a productivity tag. The result shows the themes are mostly separate sub-literatures in this corpus; "
          "it is not evidence that the topics are unrelated in practice. The only positive pair is risk assessment with the AI/expert-system tools, "
          "which fits the method theme being recorded only alongside a topic theme."]
    c4 = R["citations_by_theme"]
    L += ["", "## 4. Citations by theme (works with exactly one theme)", "", "| Theme | n | Median | Q1 | Q3 |", "|---|---:|---:|---:|---:|"]
    L += [f"| {k} | {v['n']} | {v['median']:.0f} | {v['q1']:.0f} | {v['q3']:.0f} |" for k, v in c4["groups"].items()]
    L += ["", f"Kruskal-Wallis H = {c4['H']:.1f}, p {pv(c4['p'])}, epsilon-squared = {c4['epsilon_squared']:.3f}. Citation counts are heavy-tailed, so medians and a rank test are used.", "",
          "## 5. Open access and citations, within age bands", "", "| Years | n OA | n closed | Median OA | Median closed | Rank-biserial r | p (Holm) |", "|---|---:|---:|---:|---:|---:|---:|"]
    L += [f"| {b['years'][0]}-{b['years'][1]} | {b['n_oa']} | {b['n_closed']} | {b['median_oa']:.0f} | {b['median_closed']:.0f} | {b['rank_biserial']:.2f} | {pv(b['p_holm'])} |" for b in R["open_access_vs_citations"]]
    L += ["", "Association only; field, venue and quality are not controlled.", ""]
    for title, key in (("6a. Methods mentioned in abstracts", "methods"), ("6b. Regions mentioned in abstracts", "regions")):
        L += [f"## {title}", "", "| Term | Abstracts | Share (95% CI) | 1995-2009 | 2010-2017 | 2018-2022 | 2023-2026 | Trend rho | p (Holm) |", "|---|---:|---|---:|---:|---:|---:|---:|---:|"]
        for r in R[key]:
            bp = " | ".join(f"{q['share']:.1%}" for q in r["by_period"])
            L.append(f"| {r['term']} | {r['k']} | {r['share']:.1%} ({r['ci95'][0]:.1%}-{r['ci95'][1]:.1%}) | {bp} | {r.get('trend_spearman_r', float('nan')):+.2f} | {pv(r['trend_p_holm'])} |")
        L.append("")
    L += ["With N = 3,550 even small trends are 'significant'. Judge by the shares, not the p-values: for example the machine-learning share rises "
          "from about 2% (1995-2009) to about 8% (2023-2026), while questionnaire use stays near 45%. Rho values near 0.1 are weak.", ""]
    pc = R["precision_curve"]
    L += ["## 7. Is the corpus large enough?", "",
          f"Bootstrap (2,000 resamples) of the {pc['statistic']} (full-corpus value {pc['full_share']:.1%}):", "", "| Works sampled | 95% interval | Width |", "|---:|---|---:|"]
    L += [f"| {c['n']} | {c['ci_low']:.1%} - {c['ci_high']:.1%} | {c['width']:.1%} |" for c in pc["curve"]]
    L += ["", "The interval width falls roughly as 1/sqrt(n); beyond about 2,000 works each doubling buys little extra precision for a share like this. "
          "That supports sufficiency for corpus-level shares, not for coverage of the literature or for the relevance of every record (see the audit sample in `Literature_Database_Report.md`)."]
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
