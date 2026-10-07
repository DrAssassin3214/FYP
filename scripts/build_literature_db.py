"""Rebuild the literature database (data/literature.db) and the app's JSONL export from the OpenAlex harvest.

Why: the harvest was a flat file of 5,214 records tagged with the search bucket that found them. Most of the project
(simulation, EMV, cost overrun) was dropped, so the corpus is cut to what the lean app needs -- identifying risks,
ranking them (relative importance index, probability x impact) and the masonry labour/productivity evidence behind
them. Every record, kept or not, gets one row in `screening` with a reason code, so the counts are reproducible and the
selection can be audited (PRISMA-style flow, see docs/Literature_Database_Report.md).

Screening rules (RULES_VERSION below; applied in this order, a record stops at the first rule that fires):
  S1 DUPLICATE        same DOI, or same normalised title, as a record already seen (the better-documented copy is kept)
  S2 NO_ABSTRACT      abstract shorter than MIN_ABSTRACT characters: nothing to screen or cite beyond a title
  S3 NOT_CONSTRUCTION neither an OpenAlex construction concept nor a construction phrase in title/abstract (same test as
                      scripts/filter_corpus.py)
  S3b STRUCTURAL      title is about masonry as a structural material (seismic, strength, retrofit, heritage ...)
  S3c OFF_TOPIC_ECON  title is firm-level / macro economics that only shares the word "productivity"
  S4 OUT_OF_SCOPE     found only by a dropped topic (Monte Carlo, EMV, mitigation, cost, decision support) and the
                      title has none of the in-scope phrases (RESCUE)
  S5 NO_THEME         no theme term in the title and no specific theme phrase (STRONG) in the abstract
  otherwise INCLUDED, tier 1 (core) when a theme term is in the TITLE, tier 2 (context) when only a specific phrase in the abstract matched.

Inputs : data/openalex_corpus.jsonl (any earlier version; pass --source to use the archived copy), data/literature_seed.json
Outputs: data/literature.db, data/openalex_corpus.jsonl (included records only), data/screening_report.json
Run    : python scripts/build_literature_db.py [--source PATH] [--archive PATH] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sqlite3
from collections import Counter
from pathlib import Path

from filter_corpus import reason as construction_reason

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DEFAULT_ARCHIVE = Path(r"C:\Users\Omkar\Desktop\FYP_backups\literature_archive")
RULES_VERSION = "2026-10-07.1"
MIN_ABSTRACT = 200

# Buckets from the original harvest that belong to the lean app. The others (02 Monte Carlo, 04 EMV, 07 response,
# 11 sensitivity, 12 decision support, 13 cost overrun) are out of scope unless the title says otherwise.
CORE_BUCKETS = {"01", "03", "05", "06", "08", "09", "10", "14", "15"}   # 15 = supplement harvest (title/abstract search)

THEMES = {
    "delay_causes": ("Delay causes and factors",
                     r"\b(delay\w*|time overrun\w*|schedule (overrun|slippage|performance)|late completion|timely completion|"
                     r"project duration)\b"),
    "risk_assessment": ("Risk identification and assessment (RII, probability x impact, matrix)",
                        r"\brisk(s)? (factor|factors|identification|assessment|analysis|management|matrix|register|ranking|"
                        r"evaluation|perception|mapping)|relative importance|\bRII\b|probability[- ](and )?impact|"
                        r"critical (success )?factors|risk matri\w+"),
    "productivity": ("Labour productivity and masonry work",
                     r"\b(productivity|masonry|brickwork|bricklay\w*|blockwork|masons?|labou?r (productivity|output|efficiency|shortage)|"
                     r"craftsm[ae]n)\b"),
    "expert_rule_ai": ("Rule-based, expert-system and AI risk tools",
                       r"\b(expert system\w*|rule[- ]based|knowledge[- ]based|fuzzy|decision support|machine learning|"
                       r"large language model\w*|LLM\w*|neural network\w*)\b"),
}
THEME_RX = {k: re.compile(v[1], re.I) for k, v in THEMES.items()}

# tier-2 test: a theme counts from the ABSTRACT only when one of these specific phrases is present
STRONG = {
    "delay_causes": r"(construction|project|schedule|completion|time)\s+(delays?|overruns?)|delays? (in|of|to|on) (the )?(construction|building|projects?|completion)|"
                    r"causes? of (project |construction )?delays?|delay (factors|causes)|schedule (overrun|slippage)",
    "risk_assessment": r"risk (factors?|identification|assessment|matrix|register|ranking|analysis)|relative importance (index|indices)|\bRII\b|"
                       r"probability[- ](and )?impact|risk matri",
    "productivity": r"labou?r productivity|productivity (of|in|loss|factors?|improvement)|masonry|brickwork|bricklay|blockwork|worker productivity|"
                    r"construction productivity|crew productivity",
}
STRONG_RX = {k: re.compile(v, re.I) for k, v in STRONG.items()}
# firm-level / macro economics that only shares the word "productivity"
ECON = re.compile(r"\b(firms?|wages?|profitab\w*|total factor|macroeconomic|economic growth|GDP|stock market|agricultur\w*|ageing|aging)\b", re.I)

# in-scope phrases that rescue a record found by a dropped topic (checked against the TITLE only)
RESCUE = re.compile(r"delay|risk factor|risk identification|risk assessment|risk matrix|productivity|masonry|brick|"
                    r"relative importance|schedule overrun|time overrun", re.I)
STRUCTURAL = re.compile(r"\b(seismic|earthquake|compressive strength|shear wall|finite element|mortar|retrofit\w*|"
                        r"strengthen\w*|out-of-plane|in-plane|cracking|heritage|historic\w*|stone masonry|unreinforced masonry|"
                        r"URM|fib(re|er)s?|CFRP|thermal conductivity|hygrothermal|rammed earth|adobe|archaeolog\w*)\b", re.I)

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE meta        (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE theme       (theme_id TEXT PRIMARY KEY, label TEXT NOT NULL, pattern TEXT NOT NULL);
CREATE TABLE work (
    work_id      TEXT PRIMARY KEY,              -- OpenAlex id, e.g. W2063020385
    doi          TEXT,
    title        TEXT NOT NULL,
    year         INTEGER,
    venue        TEXT,
    cited_by     INTEGER NOT NULL DEFAULT 0,
    is_oa        INTEGER NOT NULL DEFAULT 0,
    abstract     TEXT,
    abstract_len INTEGER NOT NULL DEFAULT 0,
    landing_url  TEXT,
    oa_pdf_url   TEXT,
    pdf_status   TEXT NOT NULL,                 -- 'none' | 'archived' | 'in project'
    harvest_bucket TEXT NOT NULL,               -- search bucket that first found it (provenance only)
    tier         INTEGER NOT NULL CHECK (tier IN (1, 2))
);
CREATE TABLE author      (author_id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);
CREATE TABLE work_author (work_id TEXT NOT NULL REFERENCES work ON DELETE CASCADE, author_id INTEGER NOT NULL REFERENCES author,
                          position INTEGER NOT NULL, PRIMARY KEY (work_id, author_id));
CREATE TABLE concept     (concept_id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);
CREATE TABLE work_concept(work_id TEXT NOT NULL REFERENCES work ON DELETE CASCADE, concept_id INTEGER NOT NULL REFERENCES concept,
                          PRIMARY KEY (work_id, concept_id));
CREATE TABLE work_theme  (work_id TEXT NOT NULL REFERENCES work ON DELETE CASCADE, theme_id TEXT NOT NULL REFERENCES theme,
                          in_title INTEGER NOT NULL, PRIMARY KEY (work_id, theme_id));
CREATE TABLE work_query  (work_id TEXT NOT NULL REFERENCES work ON DELETE CASCADE, query TEXT NOT NULL, PRIMARY KEY (work_id, query));
CREATE TABLE screening (                        -- one row for EVERY harvested record, included or not
    work_id TEXT PRIMARY KEY, title TEXT NOT NULL, harvest_bucket TEXT NOT NULL,
    decision TEXT NOT NULL CHECK (decision IN ('included', 'excluded')),
    reason TEXT NOT NULL, rules_version TEXT NOT NULL
);
CREATE TABLE rii_study (study_id TEXT PRIMARY KEY, authors TEXT, year INTEGER, title TEXT, venue TEXT, doi TEXT, country TEXT,
                        context TEXT, masonry TEXT, n TEXT, scale TEXT, role TEXT, obtained TEXT);
CREATE TABLE rii_row   (study_id TEXT NOT NULL REFERENCES rii_study, factor TEXT NOT NULL, rii REAL, rank INTEGER, risk_id TEXT,
                        mapping TEXT, PRIMARY KEY (study_id, factor));
CREATE INDEX ix_work_year ON work(year);
CREATE INDEX ix_work_tier ON work(tier);
CREATE INDEX ix_work_doi  ON work(doi);
CREATE INDEX ix_wt_theme  ON work_theme(theme_id);
CREATE INDEX ix_screen    ON screening(decision, reason);
CREATE VIEW v_corpus_by_theme AS
    SELECT t.label AS theme, COUNT(*) AS works, SUM(wt.in_title) AS theme_in_title
    FROM work_theme wt JOIN theme t USING (theme_id) GROUP BY t.theme_id;
CREATE VIEW v_corpus_by_year AS SELECT year, COUNT(*) AS works FROM work GROUP BY year;
"""


def norm(t: str | None) -> str:
    return re.sub(r"[^a-z0-9]", "", (t or "").lower())


def wid(r: dict) -> str:
    return r["id"].rsplit("/", 1)[-1]


def quality(r: dict) -> tuple:
    return (len(r.get("abstract") or ""), r.get("cited_by_count") or 0, bool(r.get("downloaded") or r.get("archived_pdf")))


def screen(rows: list[dict]) -> tuple[list[dict], list[tuple[str, str, str, str, str]]]:
    """Returns (included records with _themes/_tier, one screening tuple per input record)."""
    # S1: choose the best copy per key first, so which duplicate survives never depends on file order
    best: dict[str, dict] = {}
    for r in rows:
        for k in filter(None, (("doi:" + r["doi"].lower()) if r.get("doi") else None, "t:" + norm(r.get("title")))):
            if k not in best or quality(r) > quality(best[k]):
                best[k] = r
    log, kept = [], []
    for r in rows:
        keys = [k for k in (("doi:" + r["doi"].lower()) if r.get("doi") else None, "t:" + norm(r.get("title"))) if k]
        title, abstract = r.get("title") or "", r.get("abstract") or ""
        b = r["topic_bucket"]
        if any(best[k] is not r for k in keys):
            reason = "DUPLICATE"
        elif len(abstract) < MIN_ABSTRACT:
            reason = "NO_ABSTRACT"
        elif not construction_reason(r):
            reason = "NOT_CONSTRUCTION"
        elif STRUCTURAL.search(title):
            reason = "STRUCTURAL"
        elif ECON.search(title):
            reason = "OFF_TOPIC_ECON"
        elif b[:2] not in CORE_BUCKETS and not RESCUE.search(title):
            reason = "OUT_OF_SCOPE"
        else:
            hits = {k: True for k, p in THEME_RX.items() if k != "expert_rule_ai" and p.search(title)}
            hits.update({k: False for k, p in STRONG_RX.items() if k not in hits and p.search(abstract)})
            if hits and THEME_RX["expert_rule_ai"].search(title + " " + abstract):    # method theme only alongside a topic theme
                hits["expert_rule_ai"] = bool(THEME_RX["expert_rule_ai"].search(title))
            if not hits:
                reason = "NO_THEME"
            else:
                r["_themes"], r["_tier"] = hits, 1 if any(hits.values()) else 2
                kept.append(r)
                reason = "INCLUDED_T%d" % r["_tier"]
        log.append((wid(r), title, b, "included" if reason.startswith("INCLUDED") else "excluded", reason))
    return kept, log


def build_db(path: Path, kept: list[dict], log: list, seed: dict, pdf_ids: set[str]) -> None:
    if path.exists():
        path.unlink()
    db = sqlite3.connect(path)
    db.executescript(SCHEMA)
    db.executemany("INSERT INTO meta VALUES (?,?)", [("rules_version", RULES_VERSION), ("min_abstract_chars", str(MIN_ABSTRACT)),
                   ("core_buckets", ",".join(sorted(CORE_BUCKETS))), ("source", "OpenAlex (openalex.org) harvest"),
                   ("note", "Metadata copied as reported by OpenAlex; themes/tier are DERIVED by the regex rules in "
                            "scripts/build_literature_db.py, not reported by OpenAlex.")])
    db.executemany("INSERT INTO theme VALUES (?,?,?)", [(k, v[0], v[1]) for k, v in THEMES.items()])
    db.executemany("INSERT INTO screening VALUES (?,?,?,?,?,?)", [(*x[:4], x[4], RULES_VERSION) for x in
                   [(w, t, b, d, rs) for w, t, b, d, rs in log]])
    authors, concepts = {}, {}
    for r in kept:
        w = wid(r)
        pdf = "in project" if w in pdf_ids else ("archived" if r.get("archived_pdf") else "none")
        db.execute("INSERT INTO work VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                   (w, r.get("doi") or None, r["title"], r.get("year"), r.get("venue") or None, r.get("cited_by_count") or 0,
                    int(bool(r.get("is_oa"))), r["abstract"], len(r["abstract"]), r.get("landing_url"), r.get("oa_pdf_url"),
                    pdf, r["topic_bucket"], r["_tier"]))
        for i, a in enumerate(dict.fromkeys(r.get("authors") or [])):
            aid = authors.setdefault(a, len(authors) + 1)
            db.execute("INSERT OR IGNORE INTO author VALUES (?,?)", (aid, a))
            db.execute("INSERT INTO work_author VALUES (?,?,?)", (w, aid, i))
        for c in dict.fromkeys(r.get("concepts") or []):
            cid = concepts.setdefault(c, len(concepts) + 1)
            db.execute("INSERT OR IGNORE INTO concept VALUES (?,?)", (cid, c))
            db.execute("INSERT INTO work_concept VALUES (?,?)", (w, cid))
        for t, in_title in r["_themes"].items():
            db.execute("INSERT INTO work_theme VALUES (?,?,?)", (w, t, int(in_title)))
        if r.get("matched_query"):
            db.execute("INSERT OR IGNORE INTO work_query VALUES (?,?)", (w, r["matched_query"]))
    for s in seed["studies"]:
        db.execute("INSERT INTO rii_study VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                   tuple(s.get(k) for k in ("id", "authors", "year", "title", "venue", "doi", "country", "context", "masonry",
                                            "n", "scale", "role", "obtained")))
    for x in seed["rows"]:
        db.execute("INSERT OR REPLACE INTO rii_row VALUES (?,?,?,?,?,?)",
                   (x["study"], x["factor"], x.get("rii"), x.get("rank"), x.get("risk"), x.get("mapping")))
    db.commit()
    db.close()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=str(DATA / "openalex_corpus.jsonl"))
    ap.add_argument("--archive", default=str(DEFAULT_ARCHIVE))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    src, arc = Path(a.source), Path(a.archive)

    rows = [json.loads(line) for line in open(src, encoding="utf-8") if line.strip()]
    kept, log = screen(rows)
    reasons = Counter(x[4] for x in log)
    print(f"{len(rows)} records -> included {len(kept)}")
    for k, v in sorted(reasons.items()):
        print(f"  {k:14s} {v}")
    if a.dry_run:
        return 0

    arc.mkdir(parents=True, exist_ok=True)
    backup = arc / "openalex_corpus.before_database_refine.jsonl"
    if not backup.exists():
        shutil.copy2(src, backup)
    seed = json.loads((DATA / "literature_seed.json").read_text(encoding="utf-8"))
    build_db(DATA / "literature.db", kept, log, seed, set())

    with open(DATA / "openalex_corpus.jsonl", "w", encoding="utf-8") as f:
        for r in sorted(kept, key=lambda r: wid(r)):
            out = {k: v for k, v in r.items() if not k.startswith("_")}
            out["themes"], out["tier"] = sorted(r["_themes"]), r["_tier"]
            f.write(json.dumps(out, ensure_ascii=False) + "\n")
    report = {"rules_version": RULES_VERSION, "input": len(rows), "included": len(kept), "by_reason": dict(reasons),
              "tier": dict(Counter(r["_tier"] for r in kept)),
              "by_theme": dict(Counter(t for r in kept for t in r["_themes"]))}
    (DATA / "screening_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("wrote data/literature.db, data/openalex_corpus.jsonl, data/screening_report.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


