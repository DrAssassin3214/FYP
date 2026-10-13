"""Read-only audit of the evidence corpus against what the tool actually cites.

Outputs (in --out, default docs/audit/): corpus_audit.json, citation_matrix.csv, uncited_curated.csv,
seed_candidates.csv.  Changes nothing in data/.  Every mapping is copied from a data file; nothing is inferred
except the seed-candidate screen, which is labelled a title/abstract screen (not a full-text fit check).

    python scripts/audit_corpus.py --db <literature.db> [--jsonl <openalex_corpus.jsonl>]
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app.ai_layer.corpus import build_full_store  # noqa: E402


def jload(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db")
    ap.add_argument("--jsonl")
    ap.add_argument("--out", default=str(ROOT / "docs" / "audit"))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    store, _ = build_full_store(ROOT)
    curated = {r.evidence_id: r for r in store.all() if not r.evidence_id.startswith("OA-")}
    oa_in_repo = sum(1 for r in store.all() if r.evidence_id.startswith("OA-"))

    lib = jload(ROOT / "data/risk_library_masonry.json")
    rules = jload(ROOT / "data/rules_masonry.json")
    mit = jload(ROOT / "data/mitigation_catalogue.json")["entries"]
    seed = jload(ROOT / "data/literature_seed.json")
    studies = {s["id"]: s for s in seed["studies"]}

    # (paper id, risk id, channel) edges, each copied from a data file
    edges = set()
    for r in lib:
        for e in r.get("existence_evidence") or []:
            edges.add((e, r["id"], "risk_library.existence_evidence"))
    for ru in rules:
        for e in ru.get("evidence_ids") or []:
            edges.add((e, ru["risk_id"], "rules.evidence_ids"))
    for m in mit:
        for e in m.get("evidence_ids") or []:
            for rid in m.get("applies_to") or []:
                edges.add((e, rid, "mitigation.evidence_ids"))
    for row in seed["rows"]:
        if row.get("risk") and row.get("mapping"):
            edges.add((row["study"], row["risk"], f"seed_rows.{row['mapping']}"))

    cited = {e for e, _, _ in edges}
    risks = [r["id"] for r in lib]
    risk_papers = defaultdict(set)
    for e, rid, ch in edges:
        risk_papers[rid].add(e)

    resolvable = {e for e in cited if e in curated or e in studies}
    unresolved = sorted(cited - resolvable)
    uncited_curated = sorted(set(curated) - cited - {s for s in studies})

    res = {
        "risks_total": len(risks),
        "risks_with_no_paper": [r for r in risks if not risk_papers.get(r)],
        "risks_with_one_paper_only": [r for r in risks if len(risk_papers.get(r, ())) == 1],
        "risks_with_existence_evidence": sum(1 for r in lib if r.get("existence_evidence")),
        "distinct_papers_cited_anywhere": len(cited),
        "cited_but_not_resolvable_to_a_record": unresolved,
        "curated_records_in_repo": len(curated),
        "curated_records_uncited": len(uncited_curated),
        "openalex_records_in_repo_store": oa_in_repo,
        "seed_studies": {"total": len(studies), "by_role": {k: sorted(s for s, v in studies.items() if v["role"] == k)
                                                          for k in {v["role"] for v in studies.values()}}},
        "seed_rows_total": len(seed["rows"]),
        "seed_rows_direct": sum(1 for r in seed["rows"] if r.get("mapping") == "direct"),
        "seed_rows_with_no_risk": sum(1 for r in seed["rows"] if not r.get("risk")),
    }

    if a.db:
        c = sqlite3.connect(f"file:{a.db}?mode=ro", uri=True)
        res["db_work_rows"] = c.execute("select count(*) from work").fetchone()[0]
        res["db_screening_rows"] = c.execute("select count(*) from screening").fetchone()[0]
        res["db_review"] = dict(c.execute("select decision,count(*) from review group by 1").fetchall())
        res["db_works_pdf_status"] = dict(c.execute("select pdf_status,count(*) from work group by 1").fetchall())
        dois = {(d or "").lower().replace("https://doi.org/", "") for (d,) in c.execute("select doi from work")}
        titles = {re.sub(r"\W+", " ", t.lower()).strip() for (t,) in c.execute("select title from work")}
        in_db, not_in_db = [], []
        for e in sorted(cited):
            rec = curated.get(e)
            doi = (studies.get(e, {}).get("doi") or (getattr(rec, "doi", "") if rec else "") or "").lower()
            doi = doi.replace("https://doi.org/", "").strip()
            t = re.sub(r"\W+", " ", ((rec.citation if rec else studies.get(e, {}).get("title", "")) or "").lower())
            hit = (doi and doi in dois) or any(tt and tt in t for tt in titles if len(tt) > 30)
            (in_db if hit else not_in_db).append(e)
        res["cited_papers_found_in_db_by_doi_or_title"] = len(in_db)
        res["cited_papers_not_matched_in_db"] = not_in_db
        res["db_works_cited_by_tool_by_work_id"] = 0  # no data file stores an OpenAlex work id
        # seed-candidate screen: title/abstract only
        pat_m = re.compile(r"relative importance index|\bRII\b", re.I)
        pat_r = re.compile(r"india|sri lanka|bangladesh|pakistan|nepal|south asia", re.I)
        pat_t = re.compile(r"productiv|delay|masonry|brick|block|labou?r", re.I)
        cand = []
        for wid, doi, title, yr, venue, abs_, pdf, k in c.execute(
                "select w.work_id,w.doi,w.title,w.year,w.venue,w.abstract,w.pdf_status,r.decision "
                "from work w left join review r using(work_id)"):
            txt = f"{title}. {abs_ or ''}"
            if pat_m.search(txt) and pat_r.search(txt) and pat_t.search(txt):
                cand.append((wid, doi, title, yr, venue, pdf, k))
        res["seed_candidate_screen_hits"] = len(cand)
        with open(out / "seed_candidates.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["work_id", "doi", "title", "year", "venue", "pdf_status", "review", "screen"])
            for row in sorted(cand, key=lambda x: -(x[3] or 0)):
                w.writerow([*row, "title/abstract regex only: RII AND South-Asia AND productivity/delay/masonry"])

    with open(out / "citation_matrix.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["risk_id", "risk_name", "paper_id", "channel", "paper_citation_or_title", "doi"])
        names = {r["id"]: r["name"] for r in lib}
        for e, rid, ch in sorted(edges, key=lambda x: (x[1], x[0], x[2])):
            rec = curated.get(e)
            cit = rec.citation if rec else (studies[e]["authors"] + " " + str(studies[e]["year"]) + " " + studies[e]["title"]
                                            if e in studies else "UNRESOLVED: no record with this id")
            doi = (rec.doi if rec else studies.get(e, {}).get("doi", "")) or ""
            w.writerow([rid, names.get(rid, "?"), e, ch, cit[:200], doi])

    with open(out / "uncited_curated.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "citation", "doi", "depth"])
        for e in uncited_curated:
            r = curated[e]
            w.writerow([e, r.citation[:200], r.doi, r.depth if hasattr(r, "depth") else ""])

    (out / "corpus_audit.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps(res, indent=1)[:3500])


if __name__ == "__main__":
    main()
