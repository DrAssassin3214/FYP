"""Build the FULL evidence corpus for the AI layer: every record gathered during the literature
review, not just the curated workbook rows.

This is the "use maximum data" side of the AI refinement.  It does NOT fit a new statistical model
from these files -- most of them are per-paper SUMMARIES (equations, quotes, findings) rather than
raw observations, so there is nothing to refit; pooling summaries into a fabricated new equation
would be inventing evidence.  What "maximum data" means here is: every note the six research agents
wrote (Research_Notes/A..F_*.md) and every structured record they extracted (P1/P2/P3 *.json), all
loaded into the retrieval corpus the AI layer can cite from and the guard (G1) can verify against.
Nothing here changes what the deterministic engine computes.

Parsing three record styles found in the notes, in one pass per file:
  heading   "### ID - description"                              (A, B, C, P1, P2, P3 notes)
  bold      "**ID - description**"                                (D, E notes)
  table_row "| ID | col | col | ... |"                            (E's summary table, F notes)
A record's body runs until the next record-start line (any style) or the next '## ' section
heading.  This is intentionally simple pattern-matching, not an NLP parse: anything not marked up in
one of the three styles is not captured as its own record (it stays in the .md file, just not in the
AI's retrieval index).  Bodies are capped in length to keep the offline store fast.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

from .evidence import EvidenceRecord, EvidenceStore

_HEADING = re.compile(r"^###\s+([A-Z]{1,2}\d{1,3}(?:-\d{1,3})?)\b\s*-?\s*(.*)$")
_BOLD = re.compile(r"^\*\*([A-Z]{1,2}\d{1,3})\b\s*-?\s*(.*?)\*\*")
_TABLE_ROW = re.compile(r"^\|\s*([A-Z]{1,2}\d{1,3})\s*\|\s*(.*)\|?\s*$")
_SECTION_BOUNDARY = re.compile(r"^##\s+\S")
_MAX_BODY_CHARS = 1600

NOTES_FILES = ("A_masonry_india.md", "B_methods.md", "C_economics_decision.md", "D_mitigation.md",
              "E_ai_layer.md", "F_novelty_validation.md", "P1_masonry_models.md", "P2_modifiers.md",
              "P3_india_norms.md")


def _match_start(line: str) -> tuple[str, str] | None:
    for pat in (_HEADING, _BOLD, _TABLE_ROW):
        m = pat.match(line)
        if m:
            return m.group(1), m.group(2).strip()
    return None


def parse_markdown_notes(path: Path) -> list[EvidenceRecord]:
    """One EvidenceRecord per '### ID', '**ID' or '| ID |' record-start line found in `path`."""
    lines = Path(path).read_text(encoding="utf-8-sig").splitlines()
    records: list[EvidenceRecord] = []
    cur_id: str | None = None
    cur_title = ""
    cur_body: list[str] = []

    def flush():
        if cur_id is not None:
            text = (cur_title + "\n" + "\n".join(cur_body)).strip()[:_MAX_BODY_CHARS]
            records.append(EvidenceRecord(cur_id, cur_title or cur_id, "", "", "notes: " + path.name, text))

    for line in lines:
        m = _match_start(line)
        if m:
            flush()
            cur_id, cur_title = m
            cur_body = []
        elif cur_id is not None:
            if _SECTION_BOUNDARY.match(line):
                flush()
                cur_id = None
                cur_body = []
            else:
                cur_body.append(line)
    flush()
    return records


def _p1_p2_records(path: Path) -> list[EvidenceRecord]:
    rows = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    out = []
    for r in rows:
        cit = f"{r.get('authors', '')} ({r.get('year', '')}). {r.get('title', '')}. {r.get('journal', '')}."
        bits = [r.get("equation_text") or r.get("functional_form"), r.get("output_name") or r.get("modifier_name"),
                r.get("output_unit") or r.get("output_definition"), r.get("validity_range_text"), r.get("limitations")]
        text = " | ".join(str(b) for b in bits if b)
        ctx = f"{r.get('country', '')}; {r.get('activity') or r.get('trade_activity', '')}"
        out.append(EvidenceRecord(r["id"], cit.strip(), r.get("doi") or "", ctx.strip("; "),
                                  r.get("evidence_depth", "NC"), text[:_MAX_BODY_CHARS]))
    return out


def _productivity_registry_records(path: Path) -> list[EvidenceRecord]:
    rows = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    out = []
    for r in rows:
        text = " | ".join(str(x) for x in (r.get("name"), r.get("validity_text"), r.get("limitations"),
                                          r.get("usage_note")) if x)
        ctx = f"{r.get('country', '')}; {r.get('activity', '')}"
        out.append(EvidenceRecord(r["model_id"], r.get("citation", ""), r.get("doi") or "", ctx.strip("; "),
                                  r.get("evidence_depth", "NC"), text[:_MAX_BODY_CHARS]))
    return out


def _india_norms_records(path: Path) -> list[EvidenceRecord]:
    rows = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    out = []
    for r in rows:
        roles = ", ".join(f"{k}={v}" for k, v in (r.get("roles") or {}).items())
        text = " | ".join(str(x) for x in (r.get("wall_type"), roles, r.get("role_unit"), r.get("conditions"),
                                          r.get("location_in_source")) if x)
        out.append(EvidenceRecord(r["item_id"], r.get("citation", ""), r.get("url") or "",
                                  f"India; {r.get('wall_type', '')}", r.get("evidence_depth", "NC"),
                                  text[:_MAX_BODY_CHARS]))
    return out


def _openalex_records(path: Path) -> list[EvidenceRecord]:
    """data/openalex_corpus.jsonl: bulk-harvested real paper metadata (scripts/harvest_openalex.py).
    Evidence depth is set from what was actually obtained for each record -- 'full text (downloaded
    PDF)' only when a verified PDF was saved; otherwise 'abstract only' or 'metadata only (title/DOI/
    citation count from OpenAlex; abstract not available)', never claimed as more than that."""
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            eid = "OA-" + r["id"].rsplit("/", 1)[-1]           # e.g. OA-W2903322537, namespaced to avoid collisions
            cit = f"{'; '.join(r.get('authors') or []) or 'Authors NR'} ({r.get('year') or 'n.d.'}). {r.get('title', '')}. {r.get('venue', '')}."
            depth = ("full text (downloaded PDF): " + r["local_path"]) if r.get("downloaded") else \
                    ("abstract only (OpenAlex)" if r.get("abstract") else "metadata only (no abstract available from OpenAlex)")
            text = r.get("abstract") or ""
            if r.get("concepts"):
                text += " | Concepts (OpenAlex): " + ", ".join(r["concepts"])
            out.append(EvidenceRecord(eid, cit, r.get("doi", ""), r.get("topic_bucket", ""), depth, text[:_MAX_BODY_CHARS]))
    return out


def _p3_records(path: Path) -> list[EvidenceRecord]:
    rows = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    out = []
    for r in rows:
        cit = f"{r.get('issuer_or_authors', '')} ({r.get('year', '')}). {r.get('title', '')}."
        val = " ".join(str(x) for x in (r.get("value_min"), r.get("value_typical"), r.get("value_max")) if x is not None)
        text = " | ".join(str(x) for x in (r.get("measure"), val, r.get("unit"), r.get("conditions"),
                                          r.get("location_in_source"), r.get("caveat")) if x)
        ctx = f"{r.get('country', '')}; {r.get('wall_type', '')}"
        out.append(EvidenceRecord(r["id"], cit.strip(), r.get("doi_or_url") or "", ctx.strip("; "),
                                  r.get("evidence_depth", "NC"), text[:_MAX_BODY_CHARS]))
    return out


def _fulltext_records(dir_path: Path) -> list[EvidenceRecord]:
    """Research_Notes/fulltext_review/P*.md: one note per curated PDF, written after reading its whole text layer.
    Two records per paper: FT-Pnn (citation, design, relevance, limits) and FT-Pnn-N (every number captured, section 4).
    Depth is stated as it was: the text layer was read; figures were NOT viewed (marked NC in the notes)."""
    out: list[EvidenceRecord] = []
    depth = "full text (text layer read; figures not viewed)"
    for f in sorted(Path(dir_path).glob("P[0-9][0-9].md")):
        txt = f.read_text(encoding="utf-8-sig")
        secs = {m.group(1): m.group(2).strip() for m in re.finditer(r"^## (\d)\b[^\n]*\n(.*?)(?=^## \d|\Z)", txt, re.S | re.M)}
        head = txt.splitlines()[0].lstrip("# ").strip()
        cit = (secs.get("1") or head)[:400]
        m = re.search(r"10\.\d{4,9}/[^\s,;)]+", cit)
        doi = m.group(0).rstrip(".") if m else ""
        body = "\n".join(f"{k}: {secs[k]}" for k in ("3", "5", "6") if k in secs)
        out.append(EvidenceRecord(f"FT-{f.stem}", f"{head}. {cit}", doi, "", depth, body[:_MAX_BODY_CHARS]))
        if "4" in secs:
            out.append(EvidenceRecord(f"FT-{f.stem}-N", f"{head} (numbers as printed)", doi, "", depth, secs["4"][:6000]))
    return out


def build_full_store(root: Path, quiet_on_missing: bool = True) -> tuple[EvidenceStore, list[str]]:
    """Everything found: the curated workbook (R##/M##) plus every research-notes file and P1-P3
    JSON extract under `root`.  Returns (store, messages) where messages lists what was loaded or
    skipped (e.g. a file that does not exist yet) -- never silently pretend a source was used."""
    root = Path(root)
    store = EvidenceStore()
    msgs: list[str] = []

    def _load(label: str, path: Path, parser) -> None:
        if not path.exists():
            if not quiet_on_missing:
                msgs.append(f"not found (skipped): {path}")
            return
        n0 = len(store)
        for rec in parser(path):
            store.add_or_merge(rec)
        msgs.append(f"{label}: {len(store) - n0} new / merged records (from {path.name})")

    _load("workbook", root / "Literature_Evidence_Package.xlsx", lambda p: EvidenceStore.from_workbook(p).all())
    notes_dir, data_dir = root / "Research_Notes", root / "data"
    for name in NOTES_FILES:
        _load(f"notes:{name}", notes_dir / name, parse_markdown_notes)
    _load("P1 models (JSON)", notes_dir / "P1_models.json", _p1_p2_records)
    _load("P2 modifiers (JSON)", notes_dir / "P2_modifiers.json", _p1_p2_records)
    _load("P3 benchmarks (JSON)", notes_dir / "P3_benchmarks.json", _p3_records)
    _load("productivity model registry", data_dir / "productivity_models.json", _productivity_registry_records)
    _load("India labour norms", data_dir / "india_labour_norms.json", _india_norms_records)
    _load("full-text reviews of curated PDFs", notes_dir / "fulltext_review", _fulltext_records)
    _load("OpenAlex bulk harvest", data_dir / "openalex_corpus.jsonl", _openalex_records)

    msgs.append(f"TOTAL: {len(store)} evidence records")
    return store, msgs
