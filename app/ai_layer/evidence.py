"""Curated evidence store + offline keyword retriever.

The store is the ONLY source an LLM may cite.  IDs come from the project's evidence workbook
(Evidence_Matrix R##, Masonry_Productivity_Evidence M##) or from a JSON/CSV export, so every
citation the software prints resolves to a real, human-curated record.

Retrieval here is deliberately simple (token overlap) and offline.  The `Retriever` protocol lets
an embedding/vector retriever replace it later; the guard logic does not depend on which is used.
(Evidence note: lexical retrievers were competitive with semantic ones on domain text in the
literature reviewed, and retrieval grounding alone does not prevent unsupported output, hence the guard.)
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional, Protocol, Sequence


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    citation: str                      # authors, year, title, venue
    doi: str = ""
    context: str = ""                  # country / activity
    evidence_depth: str = "NC"         # full text / abstract only / NC
    text: str = ""                     # curated key statements (used for retrieval and quote checks)

    def searchable(self) -> str:
        return " ".join([self.citation, self.context, self.text]).lower()


class Retriever(Protocol):
    def retrieve(self, query: str, k: int = 5) -> list[EvidenceRecord]: ...


def _tokens(s: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", s.lower()) if len(t) > 2}


class EvidenceStore:
    def __init__(self, records: Iterable[EvidenceRecord] = ()):
        self._by_id: dict[str, EvidenceRecord] = {}
        self._index: Optional[dict[str, list[str]]] = None       # token -> ids, built on first retrieve
        for r in records:
            self.add(r)

    def add(self, rec: EvidenceRecord) -> None:
        if rec.evidence_id in self._by_id:
            raise ValueError(f"duplicate evidence id {rec.evidence_id}")
        self._by_id[rec.evidence_id] = rec
        self._index = None

    def add_or_merge(self, rec: EvidenceRecord) -> None:
        """Like add(), but if the id already exists, APPEND this record's text/citation instead of
        raising -- used when the same paper/item is described in more than one source file (e.g. a
        narrative note plus a structured JSON extract) so no information is dropped or overwritten."""
        self._index = None
        cur = self._by_id.get(rec.evidence_id)
        if cur is None:
            self._by_id[rec.evidence_id] = rec
            return
        merged_text = cur.text if rec.text in cur.text else (cur.text + "\n---\n" + rec.text if rec.text else cur.text)
        merged_ctx = cur.context or rec.context
        # Depths from different sources are combined, never silently replaced: free-form strings like
        # "full text" vs "abstract only" cannot be safely rank-ordered, so both are kept, visibly.
        if not rec.evidence_depth or rec.evidence_depth in ("", "NC") or rec.evidence_depth == cur.evidence_depth:
            merged_depth = cur.evidence_depth
        elif not cur.evidence_depth or cur.evidence_depth in ("", "NC"):
            merged_depth = rec.evidence_depth
        else:
            merged_depth = f"{cur.evidence_depth}; also: {rec.evidence_depth}"
        self._by_id[rec.evidence_id] = EvidenceRecord(rec.evidence_id, cur.citation or rec.citation,
                                                       cur.doi or rec.doi, merged_ctx, merged_depth, merged_text)

    def get(self, evidence_id: str) -> Optional[EvidenceRecord]:
        return self._by_id.get(evidence_id)

    def all(self) -> list[EvidenceRecord]:
        return list(self._by_id.values())

    def __contains__(self, evidence_id: str) -> bool:
        return evidence_id in self._by_id

    def __len__(self) -> int:
        return len(self._by_id)

    def build_index(self) -> None:
        """Token -> record ids. Built once (and again after any add), so a query costs a few dictionary
        lookups instead of re-tokenising every record; the corpus holds tens of thousands of records."""
        idx: dict[str, list[str]] = {}
        for eid, r in self._by_id.items():
            for t in _tokens(r.searchable()):
                idx.setdefault(t, []).append(eid)
        self._index = idx

    def retrieve(self, query: str, k: int = 5) -> list[EvidenceRecord]:
        """Records ranked by how many distinct query tokens they contain (ties broken by id)."""
        if self._index is None:
            self.build_index()
        counts: dict[str, int] = {}
        for t in _tokens(query):
            for eid in self._index.get(t, ()):
                counts[eid] = counts.get(eid, 0) + 1
        best = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:k]
        return [self._by_id[eid] for eid, _ in best]

    # ---- persistence ----
    @classmethod
    def from_json(cls, path: Path) -> "EvidenceStore":
        rows = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(EvidenceRecord(**r) for r in rows)

    def to_json(self, path: Path) -> None:
        Path(path).write_text(json.dumps([r.__dict__ for r in self._by_id.values()], indent=2), encoding="utf-8")

    @classmethod
    def from_workbook(cls, path: Path) -> "EvidenceStore":
        """Load R## (Evidence_Matrix) and M## (Masonry_Productivity_Evidence) rows."""
        import openpyxl

        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        store = cls()
        if "Evidence_Matrix" in wb.sheetnames:
            for row in wb["Evidence_Matrix"].iter_rows(min_row=2, values_only=True):
                if row and row[0] and str(row[0]).startswith("R") and row[3]:
                    cit = f"{row[1]} ({row[2]}). {row[3]}. {row[4]}"
                    text = " ".join(str(x) for x in (row[8], row[18], row[19]) if x)
                    store.add(EvidenceRecord(str(row[0]), cit, str(row[5] or ""), str(row[7] or ""), "targeted read", text))
        if "Masonry_Productivity_Evidence" in wb.sheetnames:
            for row in wb["Masonry_Productivity_Evidence"].iter_rows(min_row=2, values_only=True):
                if row and row[0] and str(row[0]).startswith("M") and row[3]:
                    cit = f"{row[1]} ({row[2]}). {row[3]}. {row[4]}"
                    text = " ".join(str(x) for x in (row[7], row[8], row[9], row[10]) if x)
                    store.add(EvidenceRecord(str(row[0]), cit, "", str(row[5] or ""), "targeted read", text))
        wb.close()
        return store
