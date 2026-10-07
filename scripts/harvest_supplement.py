"""Add in-scope records to data/openalex_corpus.jsonl using OpenAlex TITLE+ABSTRACT search.

Why: the first harvest used OpenAlex's full-text search, so most hits were off-topic, and after screening
(scripts/build_literature_db.py) too few in-scope records were left for corpus-level statistics. This script
only asks for works whose TITLE or ABSTRACT contains the query phrase, so what comes back is about the topic.
Records are real OpenAlex metadata, nothing is generated. Existing ids are skipped; new ones get
topic_bucket '15_Supplement_<name>' and are appended in the same record format. No PDFs are downloaded.

Run: python scripts/harvest_supplement.py [--per-query 400]
Then: python scripts/build_literature_db.py
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import requests

from harvest_openalex import MAILTO, MIN_YEAR, clean, reconstruct_abstract

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "openalex_corpus.jsonl"
NEW = ROOT / "data" / "supplement_new.jsonl"         # new records wait here until add_new_records.py screens them
API = "https://api.openalex.org/works"

QUERIES: dict[str, list[str]] = {
    "delay_causes": ["construction delay causes", "causes of delay construction projects", "delay factors building projects",
                     "construction schedule delay factors", "project delay residential construction",
                     "time overrun construction projects", "critical delay factors relative importance index"],
    "risk_identification": ["construction risk identification", "risk factors construction projects",
                            "construction risk assessment probability impact", "risk matrix construction",
                            "construction risk ranking survey", "building project risk register",
                            "risk perception contractors construction"],
    "productivity_masonry": ["masonry productivity", "brickwork productivity", "bricklaying productivity",
                             "construction labour productivity factors", "labor productivity building construction",
                             "productivity loss construction workers", "construction worker productivity survey"],
    "india_developing": ["delay Indian construction projects", "India construction productivity",
                         "construction delay developing countries", "construction delay Sri Lanka",
                         "construction delay Pakistan", "construction delay Nigeria"],
    "expert_rule_ai": ["expert system construction delay", "rule-based construction risk", "fuzzy construction delay risk",
                       "machine learning construction delay", "large language model construction risk",
                       "knowledge-based construction risk"],
    "reviews": ["systematic review construction delay", "review construction risk management",
                "systematic review labour productivity construction"],
}


def record(w: dict, name: str, q: str) -> dict:
    loc = w.get("primary_location") or {}
    src = loc.get("source") or {}
    best = w.get("best_oa_location") or {}
    return {
        "id": w["id"], "doi": (w.get("doi") or "").replace("https://doi.org/", ""), "title": clean(w.get("title") or ""),
        "authors": [clean((a.get("author") or {}).get("display_name", "")) for a in w.get("authorships", [])][:12],
        "year": w.get("publication_year"), "venue": clean(src.get("display_name") or ""),
        "cited_by_count": w.get("cited_by_count") or 0, "is_oa": bool((w.get("open_access") or {}).get("is_oa")),
        "oa_pdf_url": best.get("pdf_url") or "", "landing_url": w.get("doi") or w["id"],
        "abstract": clean(reconstruct_abstract(w.get("abstract_inverted_index"))),
        "concepts": [c["display_name"] for c in (w.get("concepts") or []) if c.get("score", 0) >= 0.3][:8],
        "topic_bucket": "15_Supplement_" + name, "matched_query": q, "downloaded": False, "local_path": "",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-query", type=int, default=400)
    a = ap.parse_args()
    key = os.environ.get("OPENALEX_API_KEY", "")        # read from the environment only, never stored in a file
    seen = {json.loads(line)["id"] for line in open(CORPUS, encoding="utf-8") if line.strip()}
    if NEW.exists():
        seen |= {json.loads(line)["id"] for line in open(NEW, encoding="utf-8") if line.strip()}
    # also skip every work already screened out (data/literature.db keeps one screening row per harvested record),
    # so a top-up does not re-add records the screening or the relevance review rejected
    import sqlite3
    if (ROOT / "data" / "literature.db").exists():
        seen |= {"https://openalex.org/" + r[0] for r in sqlite3.connect(ROOT / "data" / "literature.db").execute("SELECT work_id FROM screening")}
    added = 0
    with open(NEW, "a", encoding="utf-8") as out, requests.Session() as s:
        s.headers["User-Agent"] = f"FYP-literature-harvester/1.0 (mailto:{MAILTO})"
        for name, qs in QUERIES.items():
            for q in qs:
                cursor, got, new, attempts = "*", 0, 0, 0
                while cursor and got < a.per_query:
                    p = {"filter": f"title_and_abstract.search:{q},publication_year:>{MIN_YEAR - 1},type:article,"
                                   "has_abstract:true,language:en",
                         "sort": "cited_by_count:desc", "per-page": 100, "cursor": cursor, "mailto": MAILTO}
                    if key:
                        p["api_key"] = key
                    r = s.get(API, params=p, timeout=40)
                    if r.status_code == 429 and "budget" in r.text:
                        print("OpenAlex free daily budget used up (resets 00:00 UTC); stopping. Re-run later: already-added ids are skipped.")
                        return 1
                    if r.status_code in (429, 500, 502, 503):
                        attempts += 1
                        if attempts > 6:
                            raise RuntimeError(f"OpenAlex kept returning {r.status_code}")
                        time.sleep(5 * attempts)
                        continue
                    attempts = 0
                    r.raise_for_status()
                    j = r.json()
                    for w in j["results"]:
                        got += 1
                        if w["id"] in seen or not w.get("title"):
                            continue
                        seen.add(w["id"])
                        out.write(json.dumps(record(w, name, q), ensure_ascii=False) + "\n")
                        new += 1
                    cursor = j["meta"].get("next_cursor")
                    if not j["results"]:
                        break
                added += new
                print(f"{name:22s} {q:55s} scanned {got:4d}  new {new:4d}", flush=True)
    print("added", added, "total unique ids", len(seen))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
