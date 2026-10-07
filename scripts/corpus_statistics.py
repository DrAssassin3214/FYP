"""Descriptive statistics, sample-size adequacy and a precision audit for the literature database.

What this does and does not claim:
  * Counts, shares, medians and the screening flow are computed from data/literature.db (reproducible).
  * The 95% margin of error is the standard worst-case (p = 0.5) formula for a share, with the finite-population
    correction. It says how precisely a SHARE OF THE CORPUS (e.g. "x% of studies use RII") is estimated. It says
    nothing about how well the corpus covers the whole literature (OpenAlex is one index, search phrases are mine).
  * Whether the screening rules keep the right papers is NOT known until a person reads a sample. `--draw` writes a
    random stratified sample to data/audit_sample.csv with an empty `relevant` column (Y/N). `--score` then reports the
    precision with a Wilson 95% interval. Until that column is filled, no precision figure is reported.

Run: python scripts/corpus_statistics.py            (writes docs/Literature_Database_Report.md)
     python scripts/corpus_statistics.py --draw     (write the audit sample)
     python scripts/corpus_statistics.py --score    (after filling the `relevant` column)
"""
from __future__ import annotations

import argparse
import csv
import math
import random
import sqlite3
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "literature.db"
AUDIT = ROOT / "data" / "audit_sample.csv"
REPORT = ROOT / "docs" / "Literature_Database_Report.md"
Z = 1.959964


def moe(n: int, N: int | None = None, p: float = 0.5) -> float:
    """95% margin of error for a proportion from n records (finite-population corrected when N is given)."""
    se = math.sqrt(p * (1 - p) / n)
    if N and N > n:
        se *= math.sqrt((N - n) / (N - 1))
    return Z * se


def sample_size(N: int, e: float = 0.05, p: float = 0.5) -> int:
    n0 = Z * Z * p * (1 - p) / (e * e)
    return math.ceil(n0 / (1 + (n0 - 1) / N))


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    ph = k / n
    d = 1 + Z * Z / n
    c = (ph + Z * Z / (2 * n)) / d
    h = Z * math.sqrt(ph * (1 - ph) / n + Z * Z / (4 * n * n)) / d
    return (c - h, c + h)


def q(db, sql, *a):
    return db.execute(sql, a).fetchall()


def draw(db) -> None:
    rows = q(db, "SELECT work_id, title, year, tier, abstract FROM work ORDER BY work_id")
    N = len(rows)
    n = sample_size(N, 0.05)
    rnd = random.Random(20261007)
    by_tier: dict[int, list] = {1: [], 2: []}
    for r in rows:
        by_tier[r[3]].append(r)
    pick = []
    for t, lst in by_tier.items():                      # proportional allocation across tiers
        k = round(n * len(lst) / N)
        pick += rnd.sample(lst, min(k, len(lst)))
    rnd.shuffle(pick)
    with open(AUDIT, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["work_id", "tier", "year", "title", "abstract", "relevant (Y/N)", "note"])
        for r in pick:
            w.writerow([r[0], r[3], r[2], r[1], r[4], "", ""])
    print(f"wrote {len(pick)} rows to {AUDIT} (n for +/-5% at 95% with N={N} is {n}). Fill 'relevant (Y/N)' then run --score.")


def score() -> None:
    with open(AUDIT, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    done = [r for r in rows if r["relevant (Y/N)"].strip().upper() in ("Y", "N")]
    if not done:
        print("no judgements filled in yet; nothing to score")
        return
    for label, sub in (("all", done), ("tier 1", [r for r in done if r["tier"] == "1"]), ("tier 2", [r for r in done if r["tier"] == "2"])):
        k = sum(1 for r in sub if r["relevant (Y/N)"].strip().upper() == "Y")
        lo, hi = wilson(k, len(sub))
        print(f"{label:7s} judged {len(sub):4d}  relevant {k:4d}  precision {k / max(len(sub), 1):.3f}  Wilson 95% CI [{lo:.3f}, {hi:.3f}]")
    print(f"{len(rows) - len(done)} of {len(rows)} sample rows still unjudged")


def report(db) -> None:
    N = q(db, "SELECT COUNT(*) FROM work")[0][0]
    meta = dict(q(db, "SELECT key, value FROM meta"))
    flow = q(db, "SELECT reason, COUNT(*) FROM screening GROUP BY reason ORDER BY COUNT(*) DESC")
    total = sum(c for _, c in flow)
    tiers = dict(q(db, "SELECT tier, COUNT(*) FROM work GROUP BY tier"))
    themes = q(db, "SELECT t.label, COUNT(*), SUM(wt.in_title) FROM work_theme wt JOIN theme t USING(theme_id) GROUP BY t.theme_id")
    years = q(db, "SELECT year, COUNT(*) FROM work WHERE year IS NOT NULL GROUP BY year ORDER BY year")
    cites = [r[0] for r in q(db, "SELECT cited_by FROM work")]
    cites_s = sorted(cites)
    qs = statistics.quantiles(cites_s, n=4)
    venues = q(db, "SELECT venue, COUNT(*) FROM work WHERE venue IS NOT NULL GROUP BY venue ORDER BY COUNT(*) DESC LIMIT 10")
    oa = q(db, "SELECT SUM(is_oa) FROM work")[0][0]
    rii_n = q(db, "SELECT COUNT(*) FROM rii_row")[0][0]
    rii_s = q(db, "SELECT COUNT(*) FROM rii_study")[0][0]
    single = sum(1 for _, c in q(db, "SELECT work_id, COUNT(*) FROM work_theme GROUP BY work_id") if c == 1)
    L = [f"# Literature database report", "",
         f"Generated by `scripts/corpus_statistics.py` from `data/literature.db` (screening rules {meta['rules_version']}). "
         "Counts are computed, not typed. Source: OpenAlex metadata; themes and tiers are derived by the regex rules in "
         "`scripts/build_literature_db.py` (derived, not reported by OpenAlex).", "",
         "## 1. Screening flow", "", f"| Step / reason | Records |", "|---|---:|", f"| Harvested (all search buckets) | {total} |"]
    L += [f"| {'Included' if r.startswith('INCLUDED') else 'Excluded'}: {r} | {c} |" for r, c in flow]
    L += [f"| **Database (included)** | **{N}** |", "",
          "Reason codes: DUPLICATE (same DOI or title); NO_ABSTRACT (< %s characters); NOT_CONSTRUCTION (no construction concept or phrase); "
          "STRUCTURAL (masonry as a structural material); OFF_TOPIC_ECON (firm-level economics); OUT_OF_SCOPE (found only by a dropped topic - "
          "Monte Carlo, EMV, response, cost, decision support - with no in-scope phrase in the title); NO_THEME (no theme term in the title and no "
          "specific theme phrase in the abstract). **Tier 1 (core)** = a theme term is in the title. **Tier 2 (context)** = only a specific phrase in the "
          "abstract matched; expect a visible share of loosely related records here (e.g. safety or health papers that mention risk), which the audit "
          "sample measures separately." % meta["min_abstract_chars"], "",
          f"Tier 1: {tiers.get(1, 0)} ({tiers.get(1, 0) / N:.1%}); tier 2: {tiers.get(2, 0)} ({tiers.get(2, 0) / N:.1%}).", ""]
    if q(db, "SELECT name FROM sqlite_master WHERE name='review'"):
        L +=["### Relevance review (every screened work read at title + abstract-snippet level)", "",
              "Each of the works that passed the keyword screening was judged K (keep) or D (drop) by reviewer agents reading the title and the "
              "abstract phrase that triggered the tier. This is **not** a full-text read, and the judgements are model output, not a human audit. "
              "Works judged D were removed from the database (reason codes REVIEW_*; the screening table keeps them).", ""]
        first = q(db, "SELECT COUNT(*) FROM review")[0][0]
        kept_t = dict(q(db, "SELECT tier, COUNT(*) FROM work GROUP BY tier"))
        # tier of dropped works is gone from `work`; recover it from the archived pre-review counts stored in meta when present
        pre = {1: int(meta.get("pre_review_tier1", 0)), 2: int(meta.get("pre_review_tier2", 0))}
        L += ["| Tier | Reviewed | Kept (K) | Agreement with keyword screening | 95% Wilson CI |", "|---|---:|---:|---:|---|"]
        for t in (1, 2):
            if pre[t]:
                k = kept_t.get(t, 0)
                lo, hi = wilson(k, pre[t])
                L.append(f"| {t} | {pre[t]} | {k} | {k / pre[t]:.1%} | {lo:.1%}-{hi:.1%} |")
        L += ["", f"{first} works reviewed. Read the kept share as the screening's provisional precision as judged by the reviewers; a human check of "
              "`data/audit_sample.csv` is still the independent test.", ""]
    L += ["## 2. Sufficiency of the sample size", "",
          f"The database holds N = {N} works (target: more than 3,000: **{'met' if N > 3000 else 'NOT met'}**).", "",
          f"* Worst-case 95% margin of error for a corpus share (e.g. the share of studies in a theme) is **±{moe(N):.1%}** "
          f"for the whole database and ±{moe(N // 10, N):.1%} for a subgroup of {N // 10} works (finite-population corrected).",
          f"* Tier 1 alone has {tiers.get(1, 0)} works (margin ±{moe(tiers.get(1, 0)):.1%}).",
          ("* **Shortfall: the database is below 3,000 after the relevance review.** A top-up harvest "
           "(`scripts/harvest_supplement.py`, then the review) is needed; the OpenAlex free daily budget was used up on 2026-10-07 (resets 00:00 UTC)." if N <= 3000 else ""),
          f"* An independent human audit of the screening needs n = {sample_size(N, 0.05)} judged records for ±5% (95%); "
          f"n = {sample_size(N, 0.03)} for ±3%. `--draw` writes that sample; the reviewers' judgements above are not a substitute.",
          "* This is sufficiency for **describing the corpus**. It is not a claim that the corpus covers all published work, "
          "and the RII ranking in the app rests on the studies in section 5, not on these metadata records.", "",
          "## 3. Content", "", "| Theme (a work can have several) | Works | Theme term in title |", "|---|---:|---:|"]
    L += [f"| {a} | {b} | {c} |" for a, b, c in themes]
    L += ["", f"{single} works ({single / N:.1%}) match exactly one theme.", "",
          "## 4. Time, venue, citations", "",
          f"Years {years[0][0]} to {years[-1][0]}; works per year: " + ", ".join(f"{y}: {c}" for y, c in years[-12:]) + " (last 12 years).",
          f"Open access: {oa} ({oa / N:.1%}). Citations (OpenAlex counts, skewed): median {statistics.median(cites)}, "
          f"quartiles {qs[0]:.0f} / {qs[2]:.0f}, max {max(cites)}. Medians are used because the distribution is heavy-tailed.", "",
          "Top venues: " + "; ".join(f"{v} ({c})" for v, c in venues) + ".", "",
          "## 5. Quantitative evidence behind the ranking (table `rii_row`)", "",
          f"{rii_s} studies and {rii_n} factor rows with relative importance indices are held in `rii_study` / `rii_row`. "
          "Their agreement tests (Spearman) are in `RII_Masonry_Literature.xlsx`, Validation sheet.", "",
          "## 6. Limits", "",
          "* Screening is keyword-based on title and abstract only; full texts were not read for the metadata records.",
          "* OpenAlex abstracts and counts can be incomplete or wrong; they are copied as reported.",
          "* The search phrases are the author's; a different phrase set would give a different corpus.",
          "* Relevance was judged from title and abstract snippets by model reviewers, not read in full and not checked by a human; "
          "a human audit sample is in `data/audit_sample.csv`."]
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("wrote", REPORT)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--draw", action="store_true")
    ap.add_argument("--score", action="store_true")
    a = ap.parse_args()
    if a.score:
        score()
        return 0
    db = sqlite3.connect(DB)
    draw(db) if a.draw else report(db)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

