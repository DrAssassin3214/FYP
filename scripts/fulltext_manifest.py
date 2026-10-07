"""Build a download manifest of open-access full texts, WITHOUT downloading anything.

Two lists:
  six   : the ranking studies with no PDF in the project (A02, A10, A14, A15, A21, HAS25), resolved by DOI through OpenAlex
  top   : database works that are tier 1, list an open-access PDF link and have >= MIN_CITES citations
For every entry it records the source URL, OpenAlex's reported licence and open-access status, and the size from an HTTP HEAD
request (Content-Length; NR when the server does not say). Nothing is saved except the manifest itself (data/fulltext_manifest.json).

Run: python scripts/fulltext_manifest.py            (set OPENALEX_API_KEY in the environment for the DOI lookups)
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
MAILTO = "omkarmoze4@gmail.com"
MIN_CITES = 20
SIX = {"A02": "10.29121/ijetmr.v5.i2.2018.168", "A10": "10.1007/s40030-025-00899-5", "A14": "10.1371/journal.pone.0278318",
       "A15": "10.1108/FEBE-03-2022-0009", "A21": "10.24294/jipd.v8i8.6208", "HAS25": "10.1186/s43065-025-00116-4"}


def head(s: requests.Session, url: str) -> dict:
    try:
        r = s.head(url, allow_redirects=True, timeout=20)
        size = r.headers.get("Content-Length")
        return {"status": r.status_code, "content_type": r.headers.get("Content-Type", "").split(";")[0],
                "bytes": int(size) if size and size.isdigit() else None, "final_url": r.url}
    except Exception as e:  # network trouble is data, not a crash
        return {"status": None, "content_type": "", "bytes": None, "error": type(e).__name__}


def main() -> int:
    key = os.environ.get("OPENALEX_API_KEY", "")
    out: dict = {"six": [], "top": []}
    with requests.Session() as s:
        s.headers["User-Agent"] = f"FYP-manifest/1.0 (mailto:{MAILTO})"
        for sid, doi in SIX.items():
            p = {"mailto": MAILTO}
            if key:
                p["api_key"] = key
            r = s.get(f"https://api.openalex.org/works/doi:{doi}", params=p, timeout=30)
            w = r.json() if r.status_code == 200 else {}
            loc = w.get("best_oa_location") or {}
            url = loc.get("pdf_url") or ""
            row = {"study": sid, "doi": doi, "title": w.get("title"), "is_oa": (w.get("open_access") or {}).get("is_oa"),
                   "oa_status": (w.get("open_access") or {}).get("oa_status"), "license": loc.get("license"),
                   "pdf_url": url, "landing_page": loc.get("landing_page_url") or f"https://doi.org/{doi}"}
            row.update(head(s, url) if url else {"status": None, "bytes": None, "note": "no open-access PDF link reported"})
            out["six"].append(row)
            time.sleep(0.2)
        db = sqlite3.connect(ROOT / "data" / "literature.db")
        rows = db.execute("SELECT work_id, doi, title, year, cited_by, oa_pdf_url FROM work WHERE tier=1 AND oa_pdf_url<>'' AND cited_by>=? "
                          "ORDER BY cited_by DESC", (MIN_CITES,)).fetchall()
        for w, doi, title, year, cites, url in rows:
            out["top"].append({"work_id": w, "doi": doi, "title": title, "year": year, "cited_by": cites, "pdf_url": url})
        print(f"checking sizes for {len(out['top'])} database works ...", file=sys.stderr)
        for i, row in enumerate(out["top"]):
            row.update(head(s, row["pdf_url"]))
    (ROOT / "data" / "fulltext_manifest.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    for r in out["six"]:
        print(r["study"], r["oa_status"], r["license"], r["status"], r.get("bytes"), r["pdf_url"][:90] or r.get("note"))
    ok = [r for r in out["top"] if r.get("status") == 200 and "pdf" in (r.get("content_type") or "").lower()]
    tot = sum(r["bytes"] or 0 for r in ok)
    print(f"top list: {len(out['top'])} listed, {len(ok)} answer 200 with a PDF content type, known size {tot / 1e6:.0f} MB "
          f"({sum(1 for r in ok if r['bytes'] is None)} without a stated size)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
