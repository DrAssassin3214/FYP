"""Harvest REAL paper metadata at scale from OpenAlex (https://openalex.org), a free, open scholarly
database (no key needed). This does NOT invent papers: every record has a verifiable OpenAlex ID and,
where present, a DOI. Integrity rules from the rest of this project apply:
  - a paper is recorded with whatever OpenAlex actually reports (title, authors, year, venue, DOI,
    citation count, abstract, OA status) -- nothing is guessed or filled in.
  - "downloaded" is only ever set True after a PDF was actually fetched and looked like a PDF.
  - abstracts are reconstructed from OpenAlex's inverted index only when present; otherwise NR.

Output: data/openalex_corpus.jsonl (one JSON object per unique work) and a download log.
Every one of the 14 topic buckets is run to completion; if the output file already exists, buckets
already present in it are skipped and new results are appended, so this script is safe to re-run.
Run: python scripts/harvest_openalex.py
"""
from __future__ import annotations

import json
import os
import re
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT_JSONL = ROOT / "data" / "openalex_corpus.jsonl"
PDF_ROOT = ROOT / "Research_Papers" / "6_Bulk_Harvest"
LOG = ROOT / "data" / "harvest_log.txt"
MAILTO = "omkarmoze4@gmail.com"          # OpenAlex's "polite pool" wants a contact email
UA = f"FYP-literature-harvester/1.0 (mailto:{MAILTO})"
MIN_YEAR = 1995
# Optional personal OpenAlex API key (free, own budget separate from the shared per-IP daily
# allowance -- see https://help.openalex.org/api/authentication/). Read from the environment only,
# never hardcoded here, so it is not committed or bundled if this script is shared.
OPENALEX_API_KEY = os.environ.get("OPENALEX_API_KEY", "")

# Query buckets mirror the topic groups already established in Research_Notes (A-F, P1-P3) plus the
# case study (brick masonry, India). Each bucket name becomes the paper's "topic_bucket" tag and the
# PDF subfolder it is filed under.
BUCKETS: dict[str, list[str]] = {
    "01_Construction_Delay_Causes": [
        "construction delay causes analysis", "construction project delay factors developing countries",
        "construction schedule delay risk factors", "causes of delay in building construction projects",
        "construction delay prediction machine learning",
    ],
    "02_Monte_Carlo_Schedule_Risk": [
        "Monte Carlo simulation construction schedule risk", "probabilistic schedule risk analysis construction",
        "Monte Carlo simulation project duration PERT", "schedule risk analysis Monte Carlo simulation",
        "vectorized Monte Carlo simulation project risk", "Beta-PERT distribution project duration",
    ],
    "03_Risk_Matrix_Probability_Impact": [
        "probability impact risk matrix construction", "risk matrix project management",
        "fuzzy probability impact matrix risk assessment", "risk prioritization matrix engineering projects",
    ],
    "04_EMV_Contingency_Decision": [
        "expected monetary value project risk management", "contingency estimation construction project risk",
        "cost contingency Monte Carlo simulation construction", "decision tree analysis project risk management",
        "risk response strategy selection construction project", "risk based cost estimation construction",
    ],
    "05_AI_LLM_Construction_Risk": [
        "artificial intelligence construction risk management", "machine learning construction delay prediction",
        "large language model construction project management", "generative AI construction industry applications",
        "explainable AI construction management", "deep learning construction project risk",
        "natural language processing construction risk identification",
    ],
    "06_Rule_Based_Expert_Systems": [
        "rule based expert system construction risk", "knowledge based system construction management",
        "expert system project risk assessment", "hybrid expert system simulation construction",
    ],
    "07_Risk_Response_Mitigation": [
        "risk response strategy construction project", "risk mitigation construction project management",
        "risk treatment strategy selection project", "construction risk allocation contract",
    ],
    "08_Masonry_Brickwork_Blockwork_Productivity": [
        "masonry labor productivity construction", "bricklaying productivity construction",
        "block laying productivity construction", "construction labor productivity regression model",
        "factors affecting construction labour productivity", "masonry crew productivity model",
    ],
    "09_India_Construction_Management": [
        "Indian construction industry delay", "India construction labour productivity",
        "construction project management India case study", "Indian construction project risk",
    ],
    "10_Weather_Overtime_Productivity_Modifiers": [
        "weather effect construction labor productivity", "heat stress construction worker productivity",
        "overtime construction labor productivity", "temperature humidity construction productivity",
    ],
    "11_Sensitivity_Dependency_Simulation_Methods": [
        "sensitivity analysis project schedule risk", "correlation dependency Monte Carlo simulation project",
        "copula dependence modeling risk analysis", "Bayesian network project risk assessment",
    ],
    "12_Decision_Support_Systems_Construction": [
        "decision support system construction project management", "multi criteria decision analysis construction risk",
        "AHP TOPSIS construction risk assessment", "construction project risk decision making framework",
    ],
    "13_Cost_Overrun_Estimation": [
        "cost overrun construction project prediction", "construction cost estimation risk factors",
        "earned value management construction project", "construction budget overrun causes",
    ],
    "14_Systematic_Reviews_Construction_Risk": [
        "systematic literature review construction risk management", "review artificial intelligence construction industry",
        "review project schedule risk simulation", "bibliometric analysis construction risk research",
    ],
}


def reconstruct_abstract(inv_index: dict | None) -> str:
    if not inv_index:
        return ""
    positions: dict[int, str] = {}
    for word, idxs in inv_index.items():
        for i in idxs:
            positions[i] = word
    return " ".join(positions[i] for i in sorted(positions))


def clean(s: str) -> str:
    return unicodedata.normalize("NFKC", s or "").strip()


def _get_with_retry(session: requests.Session, params: dict, bucket: str, q: str, max_attempts: int = 8):
    """OpenAlex's polite pool still rate-limits bursts of requests; back off and retry on 429/5xx
    instead of treating a rate limit as "no results" (which silently starves later buckets). Logs
    the server's own Retry-After value (when present) so a persistent block is diagnosable rather
    than just "still rate-limited"."""
    for attempt in range(max_attempts):
        try:
            r = session.get("https://api.openalex.org/works", params=params, timeout=30)
            if r.status_code == 429 or r.status_code >= 500:
                retry_after = r.headers.get("Retry-After")
                wait = float(retry_after) if retry_after else (3 * (2 ** attempt))
                wait = min(wait, 120)
                with open(LOG, "a", encoding="utf-8") as f:
                    f.write(f"[{bucket}] {r.status_code} on {q!r} (attempt {attempt + 1}/{max_attempts}); "
                            f"Retry-After={retry_after!r}; sleeping {wait:.0f}s\n")
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            if attempt == max_attempts - 1:
                with open(LOG, "a", encoding="utf-8") as f:
                    f.write(f"[{bucket}] query failed after {max_attempts} attempts: {q!r}: {e}\n")
                return None
            time.sleep(3 * (2 ** attempt))
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"[{bucket}] query still rate-limited after {max_attempts} attempts: {q!r}\n")
    return None


def fetch_bucket(bucket: str, queries: list[str], per_query_pages: int, seen_ids: set) -> list[dict]:
    session = requests.Session()
    session.headers["User-Agent"] = UA
    out = []
    for q in queries:
        cursor = "*"
        for _page in range(per_query_pages):
            params = {"search": q, "per-page": 200, "cursor": cursor, "mailto": MAILTO,
                      "filter": f"from_publication_date:{MIN_YEAR}-01-01"}
            if OPENALEX_API_KEY:
                params["api_key"] = OPENALEX_API_KEY
            data = _get_with_retry(
                session,
                params,
                bucket, q,
            )
            if data is None:
                break
            for w in data.get("results", []):
                oid = w.get("id")
                if not oid or oid in seen_ids:
                    continue
                seen_ids.add(oid)
                best_oa = w.get("best_oa_location") or {}
                prim = w.get("primary_location") or {}
                source = (prim.get("source") or {}).get("display_name") or (best_oa.get("source") or {}).get("display_name") or ""
                out.append({
                    "id": oid,
                    "doi": (w.get("doi") or "").replace("https://doi.org/", "") if w.get("doi") else "",
                    "title": clean(w.get("display_name") or w.get("title") or ""),
                    "authors": [clean((a.get("author") or {}).get("display_name", "")) for a in (w.get("authorships") or [])][:8],
                    "year": w.get("publication_year"),
                    "venue": clean(source),
                    "cited_by_count": w.get("cited_by_count", 0) or 0,
                    "is_oa": bool((w.get("open_access") or {}).get("is_oa")),
                    "oa_pdf_url": best_oa.get("pdf_url") or "",
                    "landing_url": prim.get("landing_page_url") or w.get("id"),
                    "abstract": reconstruct_abstract(w.get("abstract_inverted_index"))[:2500],
                    "concepts": [c.get("display_name") for c in (w.get("concepts") or [])[:6]],
                    "topic_bucket": bucket,
                    "matched_query": q,
                    "downloaded": False,
                    "download_attempted": False,
                    "local_path": "",
                })
            cursor = data.get("meta", {}).get("next_cursor")
            if not cursor or not data.get("results"):
                break
            time.sleep(1.0)
        time.sleep(1.5)
    return out


def safe_filename(title: str, oid: str) -> str:
    base = re.sub(r"[^\w\- ]", "", title)[:80].strip().replace(" ", "_")
    tail = oid.rsplit("/", 1)[-1]
    return f"{base or 'untitled'}_{tail}.pdf"


def try_download(session: requests.Session, rec: dict, bucket_dir: Path) -> bool:
    url = rec.get("oa_pdf_url")
    if not url:
        return False
    existing = bucket_dir / safe_filename(rec["title"], rec["id"])
    if existing.exists() and existing.stat().st_size >= 2000:   # already fetched by an earlier, interrupted run
        rec["downloaded"] = True
        rec["local_path"] = str(existing.relative_to(ROOT))
        return True
    try:
        resp = session.get(url, timeout=(8, 20), headers={"User-Agent": UA}, allow_redirects=True, stream=True)
        if resp.status_code != 200:
            resp.close()
            return False
        chunks = resp.iter_content(65536)
        first = next(chunks, b"")
        ctype = resp.headers.get("content-type", "").lower()
        if not (first[:4] == b"%PDF" or ("pdf" in ctype and first)):
            resp.close()
            return False
        fname = safe_filename(rec["title"], rec["id"])
        path = bucket_dir / fname
        with open(path, "wb") as f:
            f.write(first)
            for chunk in chunks:
                f.write(chunk)
        resp.close()
        if path.stat().st_size < 2000:  # too small to be a real paper; drop it
            path.unlink(missing_ok=True)
            return False
        rec["downloaded"] = True
        rec["local_path"] = str(path.relative_to(ROOT))
        return True
    except Exception as e:  # noqa: BLE001
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"download failed [{rec['id']}] {url}: {e}\n")
        return False


def main(resume: bool = True):
    """Harvest every bucket in BUCKETS to completion (no early cutoff -- "at least 2000" is a floor,
    not a ceiling, so every topic area gets its own queries run in full). If data/openalex_corpus.jsonl
    already exists and `resume` is true, buckets already present in it are treated as already fully
    harvested and are skipped; new results are appended, not written over the existing ones."""
    ROOT.joinpath("data").mkdir(exist_ok=True)
    PDF_ROOT.mkdir(parents=True, exist_ok=True)
    seen_ids: set = set()
    all_recs: list[dict] = []
    done_buckets: set = set()

    if resume and OUT_JSONL.exists():
        with open(OUT_JSONL, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                all_recs.append(r)
                seen_ids.add(r["id"])
                done_buckets.add(r["topic_bucket"])
        print(f"Resuming: {len(all_recs)} existing records already cover buckets {sorted(done_buckets)}")

    def save_checkpoint():
        """Atomic rewrite so a crash mid-write can never leave a truncated corpus file."""
        tmp = OUT_JSONL.with_suffix(".jsonl.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            for r in all_recs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        tmp.replace(OUT_JSONL)

    LOG.write_text("", encoding="utf-8")
    remaining = {b: q for b, q in BUCKETS.items() if b not in done_buckets}
    print(f"Harvesting metadata across {len(remaining)} remaining topic buckets ...", flush=True)
    for bucket, queries in remaining.items():
        recs = fetch_bucket(bucket, queries, per_query_pages=3, seen_ids=seen_ids)
        all_recs.extend(recs)
        save_checkpoint()          # metadata for this bucket is now safe on disk
        print(f"  {bucket}: +{len(recs)} unique, running total {len(all_recs)}", flush=True)

    session = requests.Session()
    # Only records from THIS run are queued (download_attempted is False); older records lack the flag.
    to_try = [r for r in all_recs if r.get("oa_pdf_url") and not r["downloaded"] and r.get("download_attempted") is False]
    print(f"Attempting PDF downloads: {len(to_try)} queued", flush=True)

    def _dl(rec):
        bucket_dir = PDF_ROOT / rec["topic_bucket"]
        bucket_dir.mkdir(parents=True, exist_ok=True)
        ok = try_download(session, rec, bucket_dir)
        rec["download_attempted"] = True
        return ok

    done = 0
    with ThreadPoolExecutor(max_workers=24) as ex:
        futs = [ex.submit(_dl, r) for r in to_try]
        for _ in as_completed(futs):
            done += 1
            if done % 100 == 0:
                save_checkpoint()
                print(f"  downloads attempted: {done}/{len(to_try)}", flush=True)

    save_checkpoint()
    n_ok = sum(1 for r in all_recs if r["downloaded"])
    print(f"PDFs actually downloaded and verified (total): {n_ok}", flush=True)
    print(f"Wrote {len(all_recs)} total records to {OUT_JSONL}", flush=True)


if __name__ == "__main__":
    main()
