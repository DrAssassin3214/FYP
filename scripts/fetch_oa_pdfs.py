"""Download open-access PDFs listed in data/fulltext_manifest.json (the user approved the six ranking studies on 2026-10-07).

One plain GET per file with an honest User-Agent, no retries against a refusal, no workaround for blocks: a 403/503 or a response that is not a
PDF is recorded and the file is skipped. Files go to Research_Papers/6_Ranking_Studies_OpenAccess/<study>_<doi-slug>.pdf and are checked
for the %PDF header. Run: python scripts/fetch_oa_pdfs.py six
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Research_Papers" / "6_Ranking_Studies_OpenAccess"


def main(which: str) -> int:
    man = json.loads((ROOT / "data" / "fulltext_manifest.json").read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    log = []
    with requests.Session() as s:
        s.headers["User-Agent"] = "FYP-literature-reader/1.0 (mailto:omkarmoze4@gmail.com)"
        for row in man[which]:
            url = row.get("pdf_url") or ""
            tag = row.get("study") or row.get("work_id")
            if not url:
                log.append((tag, "no open-access PDF link"))
                continue
            try:
                r = s.get(url, timeout=60, allow_redirects=True)
            except Exception as e:
                log.append((tag, f"request failed: {type(e).__name__}"))
                continue
            if r.status_code != 200 or not r.content.startswith(b"%PDF"):
                log.append((tag, f"not saved: HTTP {r.status_code}, {'PDF header' if r.content.startswith(b'%PDF') else 'not a PDF'}"))
                continue
            path = OUT / f"{tag}_{re.sub(r'[^A-Za-z0-9]+', '-', row['doi'])[:60]}.pdf"
            path.write_bytes(r.content)
            log.append((tag, f"saved {path.name} ({len(r.content) / 1e6:.2f} MB)"))
    for t, m in log:
        print(t, m)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "six"))
