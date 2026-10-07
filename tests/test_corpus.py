from pathlib import Path

import pytest

import json as _json

from app.ai_layer.corpus import _openalex_records, build_full_store, parse_markdown_notes
from app.ai_layer.evidence import EvidenceRecord, EvidenceStore

ROOT = Path(__file__).resolve().parents[1]


def test_merge_appends_instead_of_overwriting():
    s = EvidenceStore([EvidenceRecord("X1", "First citation", "", "ctx1", "abstract only", "first text")])
    s.add_or_merge(EvidenceRecord("X1", "", "10.1/x", "ctx2", "full text", "second text"))
    rec = s.get("X1")
    assert "first text" in rec.text and "second text" in rec.text
    assert rec.citation == "First citation" and rec.doi == "10.1/x" and rec.context == "ctx1"
    assert rec.evidence_depth == "abstract only; also: full text"   # both kept, never silently replaced
    s.add_or_merge(EvidenceRecord("X1", "ignored", "", "", "", "second text"))   # exact repeat, no duplication
    assert s.get("X1").text.count("second text") == 1


def test_indexed_retrieval_ranks_by_distinct_query_tokens_and_tracks_new_records():
    s = EvidenceStore([
        EvidenceRecord("A1", "Labour shortage on Indian sites", "", "India", "abstract only", "absenteeism reduces labour output"),
        EvidenceRecord("A2", "Rain delays", "", "India", "abstract only", "monsoon stoppage of masonry"),
        EvidenceRecord("A3", "Payment delays and labour", "", "", "abstract only", "labour paid late slows work"),
    ])
    # A1 matches 3 query tokens; A2 (context "India") and A3 ("labour") match 1 each, so they tie and sort by id
    assert [r.evidence_id for r in s.retrieve("labour shortage india", 3)] == ["A1", "A2", "A3"]
    assert [r.evidence_id for r in s.retrieve("labour shortage india", 1)] == ["A1"]
    assert [r.evidence_id for r in s.retrieve("monsoon", 3)] == ["A2"]
    assert s.retrieve("zzzz", 3) == []
    s.add(EvidenceRecord("A4", "Monsoon masonry", "", "", "abstract only", "monsoon monsoon"))    # index must be rebuilt
    assert [r.evidence_id for r in s.retrieve("monsoon masonry", 3)] == ["A2", "A4"]
    s.add_or_merge(EvidenceRecord("A3", "", "", "", "", "scaffolding hazards"))
    assert [r.evidence_id for r in s.retrieve("scaffolding", 3)] == ["A3"]


def test_parse_heading_style(tmp_path):
    f = tmp_path / "notes.md"
    f.write_text(
        "# Title\n\n## 1. Section\n\n### A01 - Some Paper (2020)\nLine one.\nLine two.\n\n"
        "### A02 - Another Paper (2021)\nBody two.\n\n## 2. Next section\nnot a record\n",
        encoding="utf-8",
    )
    recs = {r.evidence_id: r for r in parse_markdown_notes(f)}
    assert set(recs) == {"A01", "A02"}
    assert "Line one" in recs["A01"].text and "Line two" in recs["A01"].text
    assert "Body two" in recs["A02"].text
    assert "not a record" not in recs["A02"].text


def test_parse_bold_and_table_styles(tmp_path):
    f = tmp_path / "notes.md"
    f.write_text(
        "## 3. Detailed entries\n\n**E01 - A Paper Title (2024).**\n- point one\n- point two\n\n"
        "**E02 - Second Paper.**\n- other point\n\n## 4. Table\n\n"
        "| F01 | Some Author 2022 | Y | - |\n| F02 | Other Author 2023 | p | Y |\n",
        encoding="utf-8",
    )
    recs = {r.evidence_id: r for r in parse_markdown_notes(f)}
    assert set(recs) == {"E01", "E02", "F01", "F02"}
    assert "point one" in recs["E01"].text and "point two" in recs["E01"].text
    assert "Some Author 2022" in recs["F01"].text


def test_hyphenated_ids_like_p1_01(tmp_path):
    f = tmp_path / "notes.md"
    f.write_text("### P1-01 - Ouga et al. (2020)\nEquation text here.\n", encoding="utf-8")
    recs = {r.evidence_id: r for r in parse_markdown_notes(f)}
    assert "P1-01" in recs and "Equation text here" in recs["P1-01"].text


def test_openalex_records_depth_reflects_what_was_actually_obtained(tmp_path):
    f = tmp_path / "corpus.jsonl"
    rows = [
        {"id": "https://openalex.org/W1", "doi": "10.1/aaa", "title": "Downloaded Paper", "authors": ["A One"],
         "year": 2021, "venue": "J. Test", "cited_by_count": 5, "is_oa": True, "abstract": "abs text",
         "concepts": ["Construction"], "topic_bucket": "01_Bucket", "matched_query": "q1", "downloaded": True,
         "local_path": "Research_Papers/6_Bulk_Harvest/01_Bucket/x.pdf"},
        {"id": "https://openalex.org/W2", "doi": "", "title": "Abstract Only Paper", "authors": [], "year": 2020,
         "venue": "", "cited_by_count": 0, "is_oa": False, "abstract": "another abstract", "concepts": [],
         "topic_bucket": "02_Bucket", "matched_query": "q2", "downloaded": False, "local_path": ""},
        {"id": "https://openalex.org/W3", "doi": "", "title": "Metadata Only Paper", "authors": [], "year": None,
         "venue": "", "cited_by_count": 0, "is_oa": False, "abstract": "", "concepts": [], "topic_bucket": "03_Bucket",
         "matched_query": "q3", "downloaded": False, "local_path": ""},
    ]
    f.write_text("\n".join(_json.dumps(r) for r in rows), encoding="utf-8")
    recs = {r.evidence_id: r for r in _openalex_records(f)}
    assert set(recs) == {"OA-W1", "OA-W2", "OA-W3"}
    assert recs["OA-W1"].evidence_depth.startswith("full text (downloaded PDF)")
    assert recs["OA-W2"].evidence_depth == "abstract only (OpenAlex)"
    assert recs["OA-W3"].evidence_depth.startswith("metadata only")
    assert "A One" in recs["OA-W1"].citation and "2021" in recs["OA-W1"].citation
    assert "Authors NR" in recs["OA-W2"].citation


def test_build_full_store_reports_missing_sources_when_asked(tmp_path):
    store, msgs = build_full_store(tmp_path, quiet_on_missing=False)
    assert len(store) == 0
    assert any("not found" in m for m in msgs)
    assert any("TOTAL: 0" in m for m in msgs)


@pytest.mark.skipif(not (ROOT / "Research_Notes" / "A_masonry_india.md").exists(), reason="research notes not present")
def test_build_full_store_on_the_real_project_data():
    store, msgs = build_full_store(ROOT)
    assert len(store) > 200, f"expected a large merged corpus, got {len(store)}: {msgs}"
    for known in ("A01", "B01", "D01", "F01", "M01", "R18", "P1-01", "IS7272-1brick"):
        assert known in store, f"{known} missing; messages: {msgs}"
    # the productivity model registry's citation should have merged into the P1-01 notes record
    rec = store.get("P1-01")
    assert rec.text  # non-empty after merge


@pytest.mark.skipif(not (ROOT / "data" / "openalex_corpus.jsonl").exists(), reason="bulk harvest not run yet")
def test_screened_corpus_loads_into_the_store():
    store, msgs = build_full_store(ROOT)
    n_openalex = sum(1 for r in store.all() if r.evidence_id.startswith("OA-"))
    assert n_openalex > 2000, f"expected > 2000 screened records, got {n_openalex}: {msgs}"


DB = ROOT / "data" / "literature.db"


@pytest.mark.skipif(not DB.exists(), reason="literature.db not built")
def test_database_meets_the_3000_work_target():
    import sqlite3
    assert sqlite3.connect(DB).execute("SELECT COUNT(*) FROM work").fetchone()[0] > 3000


@pytest.mark.skipif(not DB.exists(), reason="literature.db not built (scripts/build_literature_db.py)")
def test_literature_db_is_consistent_with_its_screening_log_and_the_jsonl_export():
    import sqlite3
    db = sqlite3.connect(DB)
    n_work = db.execute("SELECT COUNT(*) FROM work").fetchone()[0]
    assert n_work > 2000
    # every included screening row is a work, every work has a screening row
    assert db.execute("SELECT COUNT(*) FROM screening WHERE decision = 'included'").fetchone()[0] == n_work
    assert db.execute("SELECT COUNT(*) FROM work w LEFT JOIN screening s USING(work_id) WHERE s.work_id IS NULL").fetchone()[0] == 0
    # no work without a theme, no duplicate DOI, abstracts long enough to screen
    assert db.execute("SELECT COUNT(*) FROM work WHERE work_id NOT IN (SELECT work_id FROM work_theme)").fetchone()[0] == 0
    assert db.execute("SELECT COUNT(*) FROM (SELECT doi FROM work WHERE doi IS NOT NULL GROUP BY doi HAVING COUNT(*) > 1)").fetchone()[0] == 0
    assert db.execute("SELECT MIN(abstract_len) FROM work").fetchone()[0] >= 200
    assert db.execute("PRAGMA foreign_key_check").fetchall() == []
    # the app reads the JSONL export: it must hold exactly the same works
    jsonl = ROOT / "data" / "openalex_corpus.jsonl"
    ids = {_json.loads(line)["id"].rsplit("/", 1)[-1] for line in jsonl.read_text(encoding="utf-8").splitlines() if line.strip()}
    assert ids == {r[0] for r in db.execute("SELECT work_id FROM work")}
    # the RII evidence in the database matches the seed file
    seed = _json.loads((ROOT / "data" / "literature_seed.json").read_text(encoding="utf-8"))
    assert db.execute("SELECT COUNT(*) FROM rii_row").fetchone()[0] == len({(x["study"], x["factor"]) for x in seed["rows"]})



def test_fulltext_notes_load_as_two_records_per_paper_with_honest_depth():
    notes = ROOT / "Research_Notes" / "fulltext_review"
    if not notes.exists():
        pytest.skip("no full-text review notes")
    from app.ai_layer.corpus import _fulltext_records
    recs = _fulltext_records(notes)
    n_files = len(list(notes.glob("P[0-9][0-9].md")))
    assert len(recs) >= n_files * 2 - 1 and n_files >= 24
    assert all(r.evidence_depth == "full text (text layer read; figures not viewed)" for r in recs)
    assert any(r.evidence_id == "FT-P13-N" and "0." in r.text for r in recs)


def test_all_studies_basis_seeds_every_library_risk_and_default_basis_is_unchanged():
    from app.literature_seed import seed_table
    default, pooled = seed_table(), seed_table("all")
    assert default == seed_table("seed")
    assert sum(1 for v in pooled.values() if v["rank"]) >= sum(1 for v in default.values() if v["rank"])
    assert all(1 <= v["class"] <= 5 for v in pooled.values() if v["class"])
    assert seed_table("nonsense") == default            # unknown basis falls back to the default
