"""Keep only construction-relevant records in data/openalex_corpus.jsonl.

Why: the literature harvest searched OpenAlex by phrase, and OpenAlex matches phrases against full text, so a large
share of what came back is not about construction at all (medicine, marketing, machine learning, labour economics).
Those records would be offered to the AI layer as "evidence" for risks on a brick-masonry activity.

Rule (deliberately simple and transparent). A record is KEPT when any of these holds:
  1. one of its OpenAlex concepts is a construction / civil / building concept, or
  2. its TITLE contains a construction, building-trade or masonry phrase (see TITLE), or
  3. its ABSTRACT contains a construction-industry phrase (see ABSTRACT).
Everything else is moved, unchanged, to <archive>/openalex_corpus.removed_offtopic.jsonl (nothing is deleted), and the
original file is kept as <archive>/openalex_corpus.before_relevance_filter.jsonl.

Run: python scripts/filter_corpus.py [--archive PATH] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "openalex_corpus.jsonl"
DEFAULT_ARCHIVE = Path(r"C:\Users\Omkar\Desktop\FYP_backups\literature_archive")

STRONG_CONCEPTS = {"civil engineering", "construction engineering", "architectural engineering", "structural engineering",
                   "building", "building information modeling", "geotechnical engineering", "construction waste",
                   "formwork", "masonry"}
TITLE = re.compile(
    r"\b(construction (industry|project|projects|site|sites|worker|workers|delay|delays|management|schedule|sector|firm|firms|"
    r"company|companies|labou?r|productivity|cost|contractors?|work|materials?|safety|equipment)|"
    r"building (industry|project|projects|construction|site|sites|material|materials|sector|works?|craft\w*|trades?\w*|labou?r|"
    r"workers?|productivity|delays?|contractors?|firms?)|"
    r"masonry|brick|bricks|brickwork|blockwork|bricklay\w*|masons?|craftsm[ae]n|contractors?|civil engineering|precast|concrete|"
    r"scaffolding|rebar|formwork|earthwork\w*|outdoor workers?|"
    r"housing (project|projects|construction|delivery)|infrastructure projects?|building information model\w*|"
    r"project delay\w*|schedule delay\w*|cost overrun\w*|delay\w* (in|of) (construction|building|projects?)|"
    r"construction (and|&) demolition|site (management|productivity|workers?|safety))\b", re.I)
ABSTRACT = re.compile(
    r"\b(construction (industry|project|projects|site|sites|worker|workers|management|sector|firms?|companies|labou?r|activit\w*)|"
    r"building construction|masonry|brickwork|bricklay\w*|blockwork|craftsm[ae]n|civil engineering|construction delay\w*|"
    r"building sites?|residential construction|construction phase|building projects?)\b", re.I)


def reason(r: dict) -> str | None:
    concepts = {c.lower() for c in (r.get("concepts") or []) if c}
    if concepts & STRONG_CONCEPTS:
        return "concept"
    if TITLE.search(r.get("title") or ""):
        return "title"
    if ABSTRACT.search(r.get("abstract") or ""):
        return "abstract"
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", default=str(DEFAULT_ARCHIVE))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    arc = Path(a.archive)

    rows = [json.loads(line) for line in open(CORPUS, encoding="utf-8") if line.strip()]
    kept, removed, why = [], [], Counter()
    for r in rows:
        w = reason(r)
        (kept if w else removed).append(r)
        if w:
            why[w] += 1
    print(f"{len(rows)} records -> keep {len(kept)} ({dict(why)}), remove {len(removed)}")
    by_bucket = Counter(r["topic_bucket"] for r in kept)
    for b in sorted({r["topic_bucket"] for r in rows}):
        print(f"  {b:48s} kept {by_bucket[b]}")
    if a.dry_run:
        return 0

    arc.mkdir(parents=True, exist_ok=True)
    backup = arc / "openalex_corpus.before_relevance_filter.jsonl"
    if not backup.exists():
        backup.write_bytes(CORPUS.read_bytes())
    with open(arc / "openalex_corpus.removed_offtopic.jsonl", "a", encoding="utf-8") as f:      # append: earlier passes stay
        for r in removed:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp = CORPUS.with_suffix(".jsonl.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        for r in kept:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp.replace(CORPUS)
    print(f"wrote {len(kept)} records to {CORPUS}; removed records saved in {arc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
