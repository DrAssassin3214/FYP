"""Screen the records in data/supplement_new.jsonl and add them to data/literature.db incrementally.

Why incremental: scripts/build_literature_db.py rebuilds from a full raw harvest, but the raw rows rejected earlier are no longer
on disk (only their screening rows are). This script keeps everything already in the database, applies the SAME screening rules
(build_literature_db.screen) to the new records only, drops anything already known (same DOI or title), inserts the rest, and
appends the included ones to data/openalex_corpus.jsonl. New works have no row in table `review` yet: run the relevance review
on them (write their decisions into data/review_decisions.tsv) and then scripts/apply_review.py.

Run: python scripts/add_new_records.py [--export-batches DIR]   (the option writes review batch files for the pending works)
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_literature_db as b  # noqa: E402

ROOT = b.ROOT
DB = ROOT / "data" / "literature.db"
NEW = ROOT / "data" / "supplement_new.jsonl"
CORPUS = ROOT / "data" / "openalex_corpus.jsonl"


def insert_work(db: sqlite3.Connection, r: dict) -> None:
    w = b.wid(r)
    db.execute("INSERT INTO work VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
               (w, r.get("doi") or None, r["title"], r.get("year"), r.get("venue") or None, r.get("cited_by_count") or 0,
                int(bool(r.get("is_oa"))), r["abstract"], len(r["abstract"]), r.get("landing_url"), r.get("oa_pdf_url"),
                "none", r["topic_bucket"], r["_tier"]))
    for i, a in enumerate(dict.fromkeys(r.get("authors") or [])):
        row = db.execute("SELECT author_id FROM author WHERE name=?", (a,)).fetchone()
        aid = row[0] if row else db.execute("INSERT INTO author(name) VALUES (?)", (a,)).lastrowid
        db.execute("INSERT OR IGNORE INTO work_author VALUES (?,?,?)", (w, aid, i))
    for c in dict.fromkeys(r.get("concepts") or []):
        row = db.execute("SELECT concept_id FROM concept WHERE name=?", (c,)).fetchone()
        cid = row[0] if row else db.execute("INSERT INTO concept(name) VALUES (?)", (c,)).lastrowid
        db.execute("INSERT OR IGNORE INTO work_concept VALUES (?,?)", (w, cid))
    for t, in_title in r["_themes"].items():
        db.execute("INSERT INTO work_theme VALUES (?,?,?)", (w, t, int(in_title)))
    if r.get("matched_query"):
        db.execute("INSERT OR IGNORE INTO work_query VALUES (?,?)", (w, r["matched_query"]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--export-batches", default="")
    a = ap.parse_args()
    db = sqlite3.connect(DB)
    db.execute("PRAGMA foreign_keys = ON")
    db.execute("""CREATE TABLE IF NOT EXISTS review (work_id TEXT PRIMARY KEY, decision TEXT NOT NULL CHECK (decision IN ('K','D')),
                  reason TEXT, reviewer TEXT NOT NULL, depth TEXT NOT NULL)""")
    if NEW.exists():
        known_ids = {r[0] for r in db.execute("SELECT work_id FROM screening")}
        known_doi = {r[0].lower() for r in db.execute("SELECT doi FROM work WHERE doi IS NOT NULL")}
        known_title = {b.norm(r[0]) for r in db.execute("SELECT title FROM screening")}
        rows = [json.loads(ln) for ln in open(NEW, encoding="utf-8") if ln.strip()]
        fresh = [r for r in rows if b.wid(r) not in known_ids and not (r.get("doi") and r["doi"].lower() in known_doi)
                 and b.norm(r.get("title")) not in known_title]
        kept, log = b.screen(fresh)
        for w, title, bucket, dec, reason in log:
            db.execute("INSERT INTO screening VALUES (?,?,?,?,?,?)", (w, title, bucket, dec, reason, b.RULES_VERSION))
        for r in kept:
            insert_work(db, r)
        with open(CORPUS, "a", encoding="utf-8") as f:
            for r in sorted(kept, key=b.wid):
                out = {k: v for k, v in r.items() if not k.startswith("_")}
                out["themes"], out["tier"] = sorted(r["_themes"]), r["_tier"]
                f.write(json.dumps(out, ensure_ascii=False) + "\n")
        db.commit()
        NEW.rename(NEW.with_suffix(".done.jsonl")) if not NEW.with_suffix(".done.jsonl").exists() else None
        print(f"new rows {len(rows)}; already known {len(rows) - len(fresh)}; screened {len(fresh)}; included {len(kept)}")
    pending = db.execute("SELECT w.work_id, w.tier, w.title, w.abstract FROM work w LEFT JOIN review r USING(work_id) "
                         "WHERE r.work_id IS NULL ORDER BY w.work_id").fetchall()
    print(f"works awaiting relevance review: {len(pending)}")
    if a.export_batches and pending:
        out_dir = Path(a.export_batches)
        out_dir.mkdir(parents=True, exist_ok=True)
        rx = list(b.STRONG_RX.values())
        lines = []
        for w, tier, title, ab in pending:
            if tier == 1:
                lines.append(f"{w}|{title[:115]}")
            else:
                sn = ""
                for r in rx:
                    m = r.search(ab)
                    if m:
                        sn = ab[max(0, m.start() - 60):m.end() + 60].replace("\n", " ")
                        break
                lines.append(f"{w}|T2|{title[:100]}|..{sn}..")
        for k in range(0, len(lines), 300):
            (out_dir / f"n{k // 300:02d}.txt").write_text("\n".join(lines[k:k + 300]), encoding="utf-8")
        print("wrote", (len(lines) + 299) // 300, "review batch files to", out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
