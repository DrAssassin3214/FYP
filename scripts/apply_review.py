"""Apply the title/abstract relevance review to data/literature.db and the JSONL export.

The review (one K/D judgement per screened work, made by reviewer agents reading the title and the abstract context snippet
that triggered the tier; NOT the full text) is stored in data/review_decisions.tsv: work_id, decision (K/D), reason.
  * every reviewed work gets a row in table `review` (so 'what was read, by whom, to what depth' is queryable);
  * works judged D are removed from `work` (cascades to authors/concepts/themes) and their `screening` row becomes
    excluded / REVIEW_<reason>;
  * data/openalex_corpus.jsonl is rewritten to the remaining works.
Idempotent: re-running with the same file changes nothing.

Run: python scripts/apply_review.py
"""
from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "literature.db"
TSV = ROOT / "data" / "review_decisions.tsv"
JSONL = ROOT / "data" / "openalex_corpus.jsonl"
REVIEWER = "Claude reviewer agents (title + abstract context snippet)"


def main() -> int:
    rows = list(csv.DictReader(open(TSV, encoding="utf-8"), delimiter="\t"))
    db = sqlite3.connect(DB)
    db.execute("PRAGMA foreign_keys = ON")
    db.execute("""CREATE TABLE IF NOT EXISTS review (
        work_id TEXT PRIMARY KEY, decision TEXT NOT NULL CHECK (decision IN ('K','D')), reason TEXT,
        reviewer TEXT NOT NULL, depth TEXT NOT NULL)""")
    known = {r[0] for r in db.execute("SELECT work_id FROM screening")}
    for r in rows:
        if r["work_id"] not in known:
            raise SystemExit(f"unknown work_id in review file: {r['work_id']}")
        db.execute("INSERT OR REPLACE INTO review VALUES (?,?,?,?,?)",
                   (r["work_id"], r["decision"], r["reason"] or None, REVIEWER, "title + abstract snippet (not full text)"))
    # remember how many works per tier have been reviewed (kept or dropped) for the report: add the tiers of works
    # that are being reviewed for the first time in this run (their rows still exist in `work` at this point)
    seen = {r[0] for r in db.execute("SELECT work_id FROM review")}
    newly = [r["work_id"] for r in rows if r["work_id"] not in seen]
    if newly:
        add = {1: 0, 2: 0}
        for w in newly:
            t = db.execute("SELECT tier FROM work WHERE work_id=?", (w,)).fetchone()
            if t:
                add[t[0]] += 1
        for t in (1, 2):
            old = db.execute("SELECT value FROM meta WHERE key=?", (f"pre_review_tier{t}",)).fetchone()
            db.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", (f"pre_review_tier{t}", str(int(old[0]) + add[t] if old else add[t])))
    dropped = [r["work_id"] for r in rows if r["decision"] == "D"]
    for w in dropped:
        db.execute("DELETE FROM work WHERE work_id = ?", (w,))
        db.execute("UPDATE screening SET decision='excluded', reason='REVIEW_' || (SELECT reason FROM review WHERE work_id=?) WHERE work_id=?", (w, w))
    db.commit()
    keep = {r[0] for r in db.execute("SELECT work_id FROM work")}
    lines = [ln for ln in open(JSONL, encoding="utf-8") if ln.strip() and json.loads(ln)["id"].rsplit("/", 1)[-1] in keep]
    JSONL.write_text("".join(lines), encoding="utf-8")
    db.execute("VACUUM")
    print(f"reviewed {len(rows)}; dropped {len(dropped)}; works now {len(keep)}; jsonl lines {len(lines)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
