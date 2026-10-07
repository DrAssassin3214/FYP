"""Statistical analysis with every study brought to ONE common level (within-study z-scores).

Why: RII depends on the rating scale (1-4 gives lower values than 1-5) and on the respondents, so raw RII from different
studies is not comparable (study means here range from 0.59 to 0.75). Each study's values are therefore standardised:
    z = (RII - mean RII of the study's factors) / SD of the study's factors
so that every study has mean 0 and SD 1 over its own factor list. A risk's score in a study is the mean z of its DIRECT factors.

Which studies can be standardised honestly?
  complete list (used in Analysis A):  M06 (40 of 40), M10 (33 of 35), M14 (23), M15 (24)
  truncated list (added in Analysis B, flagged): M01 lists only the 28 factors with RII > 0.7 (of 38), so its z-scores are
      distorted (the lowest factors are cut off); A02 (14 selected values), A14 and A15 (top factors only), A10, A21 and
      HAS25 (a few values) are partial lists and are not standardised.

Run: python scripts/stats_standardised.py [out.json]
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path
from statistics import mean

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.literature_seed import load_dataset  # noqa: E402

DATA = load_dataset()
RISKS = [r["id"] for r in json.loads((ROOT / "data" / "risk_library_masonry.json").read_text(encoding="utf-8-sig"))]
COMPLETE = ["M06", "M10", "M14", "M15"]
TRUNCATED = ["M01"]
RNG = np.random.default_rng(20261007)


def study_stats(sid: str) -> tuple[float, float, int]:
    v = [r["rii"] for r in DATA["rows"] if r["study"] == sid]
    return float(np.mean(v)), float(np.std(v, ddof=1)), len(v)


def z_scores(studies: list[str]) -> dict[str, dict[str, float]]:
    """risk -> {study: mean z of the study's DIRECT factors for that risk}."""
    out: dict[str, dict[str, float]] = {k: {} for k in RISKS}
    for sid in studies:
        m, sd, _ = study_stats(sid)
        for rid in RISKS:
            vals = [(r["rii"] - m) / sd for r in DATA["rows"] if r["study"] == sid and r.get("risk") == rid and r.get("mapping") == "direct"]
            if vals:
                out[rid][sid] = float(np.mean(vals))
    return out


def analyse(studies: list[str], label: str) -> dict:
    z = z_scores(studies)
    rows = []
    for rid in RISKS:
        v = list(z[rid].values())
        k = len(v)
        mu = float(np.mean(v)) if v else None
        sd = float(np.std(v, ddof=1)) if k > 1 else None
        ci = None
        if k > 1:
            h = float(stats.t.ppf(0.975, k - 1) * sd / np.sqrt(k))
            ci = [mu - h, mu + h]
        rows.append({"risk": rid, "k": k, "studies": sorted(z[rid]), "pooled_z": mu, "sd_between_studies": sd, "ci95": ci,
                     "min": min(v) if v else None, "max": max(v) if v else None})
    have = [r for r in rows if r["pooled_z"] is not None]
    order = sorted(have, key=lambda r: -r["pooled_z"])
    for i, r in enumerate(order, 1):
        r["rank"] = i

    # additive two-way model z = risk + study (unbalanced), F-test for the risk effect
    long = pd.DataFrame([{"risk": rid, "study": sid, "z": zz} for rid in RISKS for sid, zz in z[rid].items()])
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    model = smf.ols("z ~ C(risk) + C(study)", data=long).fit()
    an = sm.stats.anova_lm(model, typ=2)
    anova = {"n_cells": int(len(long)), "F_risk": float(an.loc["C(risk)", "F"]), "df_risk": int(an.loc["C(risk)", "df"]),
             "p_risk": float(an.loc["C(risk)", "PR(>F)"]), "df_resid": int(an.loc["Residual", "df"]),
             "r2": float(model.rsquared), "adj_r2": float(model.rsquared_adj)}
    # robustness: the same model using only risks covered by at least two studies (drops single-study extremes)
    multi = [rid for rid in RISKS if len(z[rid]) >= 2]
    sub = long[long["risk"].isin(multi)]
    if sub["risk"].nunique() >= 3 and sub["study"].nunique() >= 2:
        m_sub = smf.ols("z ~ C(risk) + C(study)", data=sub).fit()
        a_sub = sm.stats.anova_lm(m_sub, typ=2)
        anova["k2plus"] = {"n_risks": int(sub["risk"].nunique()), "n_cells": int(len(sub)), "F": float(a_sub.loc["C(risk)", "F"]),
                           "df": int(a_sub.loc["C(risk)", "df"]), "df_resid": int(a_sub.loc["Residual", "df"]), "p": float(a_sub.loc["C(risk)", "PR(>F)"]),
                           "adj_r2": float(m_sub.rsquared_adj)}
    # permutation test for the risk effect (shuffle risk labels within each study)
    f0 = anova["F_risk"]
    cnt = 0
    nperm = 3000
    for _ in range(nperm):
        sh = long.copy()
        sh["risk"] = sh.groupby("study")["risk"].transform(lambda s: RNG.permutation(s.values))
        m2 = smf.ols("z ~ C(risk) + C(study)", data=sh).fit()
        cnt += sm.stats.anova_lm(m2, typ=2).loc["C(risk)", "F"] >= f0 - 1e-12
    anova["p_risk_permutation"] = float((cnt + 1) / (nperm + 1))

    # leave-one-study-out cross-prediction on the common scale
    loso = []
    for held in studies:
        rest = [s for s in studies if s != held]
        rz = z_scores(rest)
        pred = {r: float(np.mean(list(rz[r].values()))) for r in RISKS if rz[r]}
        obs = {r: z[r][held] for r in RISKS if held in z[r]}
        common = [r for r in obs if r in pred]
        if len(common) >= 4:
            rho, p = stats.spearmanr([pred[r] for r in common], [obs[r] for r in common])
            loso.append({"held_out": held, "n": len(common), "rho": float(rho), "p": float(p)})
    # bootstrap rank intervals (resample studies)
    boot = {r["risk"]: [] for r in have}
    for _ in range(5000):
        pick = RNG.choice(studies, size=len(studies), replace=True)
        mm = {}
        for rid in RISKS:
            v = [z[rid][s] for s in pick if s in z[rid]]
            if v:
                mm[rid] = float(np.mean(v))
        pres = [r["risk"] for r in have if r["risk"] in mm]
        if len(pres) < 3:
            continue
        rk = stats.rankdata([-mm[x] for x in pres])                  # ranks among the risks present, scaled to 1..N
        for x, kk in zip(pres, rk):
            boot[x].append(1 + (kk - 1) / (len(pres) - 1) * (len(have) - 1))
    for r in have:
        b = boot[r["risk"]]
        r["boot_rank_lo"], r["boot_rank_hi"], r["boot_n"] = (float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5)), len(b)) if b else (None, None, 0)

    return {"label": label, "studies": studies, "per_risk": rows, "anova": anova, "leave_one_study_out": loso}


res = {"study_stats": {sid: dict(zip(("mean", "sd", "n"), study_stats(sid))) for sid in COMPLETE + TRUNCATED},
       "analysis_A": analyse(COMPLETE, "A: complete factor lists (M06, M10, M14, M15)"),
       "analysis_B": analyse(COMPLETE + TRUNCATED, "B: A plus M01 (truncated list, flagged)")}

# comparison with the seed ranking (raw RII from the India / Sri Lanka seed studies) and with raw pooled RII
sys.path.insert(0, str(ROOT))
from app.literature_seed import seed_table  # noqa: E402
seed = {k: v["mean_rii"] for k, v in seed_table().items() if v["mean_rii"] is not None}
for key in ("analysis_A", "analysis_B"):
    a = res[key]
    pz = {r["risk"]: r["pooled_z"] for r in a["per_risk"] if r["pooled_z"] is not None}
    common = [r for r in RISKS if r in pz and r in seed]
    rho, p = stats.spearmanr([seed[r] for r in common], [pz[r] for r in common])
    a["vs_seed"] = {"n": len(common), "rho": float(rho), "p": float(p)}
    raw = {}
    for rid in RISKS:
        vals = [mean(r["rii"] for r in DATA["rows"] if r["study"] == s and r.get("risk") == rid and r.get("mapping") == "direct")
                for s in a["studies"] if any(r["study"] == s and r.get("risk") == rid and r.get("mapping") == "direct" for r in DATA["rows"])]
        if vals:
            raw[rid] = float(np.mean(vals))
    c2 = [r for r in RISKS if r in raw and r in pz]
    a["raw_vs_z_pooling"] = {"n": len(c2), "rho": float(stats.spearmanr([raw[r] for r in c2], [pz[r] for r in c2])[0]), "raw_pooled_means": raw}

# agreement between the standardised studies (pairwise)
pairs = []
zB = z_scores(COMPLETE + TRUNCATED)
for a_, b_ in itertools.combinations(COMPLETE + TRUNCATED, 2):
    common = [r for r in RISKS if a_ in zB[r] and b_ in zB[r]]
    if len(common) >= 4:
        rho, p = stats.spearmanr([zB[r][a_] for r in common], [zB[r][b_] for r in common])
        pairs.append({"a": a_, "b": b_, "n": len(common), "rho": float(rho), "p": float(p)})
res["pairwise"] = pairs
res["pairwise_summary"] = {"n_pairs": len(pairs), "mean_rho": float(np.mean([q["rho"] for q in pairs])),
                           "median_rho": float(np.median([q["rho"] for q in pairs]))}
res["note"] = "Rank agreement between two studies is unchanged by standardisation (z is monotone within a study); what standardisation changes is the pooled magnitude, the confidence intervals and the model test."

out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs" / "rii_standardised_statistics.json"
out.write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")
print("wrote", out)
