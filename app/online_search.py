"""Optional online literature search for candidate response (mitigation) options.  NO language model is involved.

Nothing here runs unless a user presses "Find options online" in the GUI (POST /api/online-options).  Importing this
module never touches the network.  Two free scholarly indexes are queried with the standard library only:

    OpenAlex  https://api.openalex.org/works?search=...&per-page=...
    Crossref  https://api.crossref.org/works?query=...&rows=...

For each risk the result is a list of CITED CANDIDATE SOURCES (title, authors, year, venue, DOI / URL, an abstract
snippet when the index returns one, and which index it came from), plus the catalogue options that target the risk.

Integrity: these are papers, not recommendations.  No cost, effect size, probability or delay is extracted, parsed or
inferred from a title or an abstract; the user must read the paper and enter their own cost / effect with a Source.
Offline (or any network failure) returns {"ok": False, "offline": True, "message": ...}; it never raises.
"""
from __future__ import annotations

import json
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Iterable, Optional

OPENALEX_URL = "https://api.openalex.org/works"
CROSSREF_URL = "https://api.crossref.org/works"
USER_AGENT = "FYP-BrickworkRiskTool/1.0 (offline-first student research tool)"
TIMEOUT_S = 10
MAX_PER_SOURCE = 10          # hard cap on results requested from each index
MAX_PER_RISK = 10            # hard cap on merged results returned per risk
MAX_RISKS = 8                # one request may search at most this many risks
SNIPPET_CHARS = 300
QUERY_TERMS = "mitigation brick masonry construction delay"
NOTE = ("Online search: needs internet; results are papers, not recommendations. No cost, effect size, probability or "
        "delay is taken from them. Read the paper and enter your own cost / effect with a Source.")


class OfflineError(Exception):
    """The index could not be reached (no network, DNS failure, timeout, HTTP error, unreadable reply)."""


# ------------------------------------------------------------------------------------------------ helpers
def build_query(risk_name: str, extra: Iterable[str] = ()) -> str:
    """Risk library name + fixed topic terms (+ optional catalogue measure words).  Plain words only."""
    words = " ".join([str(risk_name or "").strip(), *[str(x).strip() for x in extra], QUERY_TERMS])
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s\-]", " ", words)).strip()[:300]


def _norm_doi(doi: Any) -> str:
    d = str(doi or "").strip().lower()
    d = re.sub(r"^(https?://)?(dx\.)?doi\.org/", "", d)
    return d


def _snippet(text: Any) -> str:
    t = re.sub(r"<[^>]+>", " ", str(text or ""))          # Crossref abstracts are JATS XML
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"^abstract\s*", "", t, flags=re.I)
    return t if len(t) <= SNIPPET_CHARS else t[:SNIPPET_CHARS].rsplit(" ", 1)[0] + " ..."


def rebuild_abstract(inv: Any) -> str:
    """OpenAlex ships abstracts as {word: [positions]}; put the words back in order."""
    if not isinstance(inv, dict):
        return ""
    slots: dict[int, str] = {}
    for word, positions in inv.items():
        if isinstance(positions, list):
            for p in positions:
                if isinstance(p, int) and not isinstance(p, bool) and 0 <= p < 100000:
                    slots[p] = str(word)
    return " ".join(slots[i] for i in sorted(slots))


def _get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            raw = resp.read()
        data = json.loads(raw.decode("utf-8"))
    except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError, OSError) as e:
        raise OfflineError(str(getattr(e, "reason", None) or e)) from e
    except (ValueError, UnicodeDecodeError) as e:
        raise OfflineError("the index returned a reply that could not be read") from e
    if not isinstance(data, dict):
        raise OfflineError("the index returned an unexpected reply")
    return data


# ------------------------------------------------------------------------------------------------ parsers
def parse_openalex(data: dict) -> list[dict]:
    out = []
    for w in (data.get("results") or []) if isinstance(data, dict) else []:
        if not isinstance(w, dict) or not w.get("title"):
            continue
        authors = [((a.get("author") or {}).get("display_name") or "") for a in (w.get("authorships") or []) if isinstance(a, dict)]
        loc = w.get("primary_location") or {}
        venue = ((loc.get("source") or {}).get("display_name")) if isinstance(loc, dict) else None
        doi = _norm_doi(w.get("doi"))
        url = (f"https://doi.org/{doi}" if doi else (loc.get("landing_page_url") if isinstance(loc, dict) else None)
               or w.get("id") or "")
        out.append({"title": str(w["title"]).strip(), "authors": [a for a in authors if a][:6],
                    "year": w.get("publication_year") if isinstance(w.get("publication_year"), int) else None,
                    "venue": venue or "", "doi": doi, "url": url,
                    "abstract_snippet": _snippet(rebuild_abstract(w.get("abstract_inverted_index"))),
                    "source_api": "OpenAlex"})
    return out


def parse_crossref(data: dict) -> list[dict]:
    out = []
    items = ((data.get("message") or {}).get("items") or []) if isinstance(data, dict) else []
    for it in items:
        if not isinstance(it, dict):
            continue
        titles = it.get("title") or []
        title = titles[0] if isinstance(titles, list) and titles else (titles if isinstance(titles, str) else "")
        if not str(title).strip():
            continue
        authors = []
        for a in it.get("author") or []:
            if isinstance(a, dict):
                nm = " ".join(x for x in (a.get("given"), a.get("family")) if x) or a.get("name") or ""
                if nm:
                    authors.append(nm)
        year = None
        for k in ("issued", "published-print", "published-online", "created"):
            parts = ((it.get(k) or {}).get("date-parts") or [[None]])
            y = parts[0][0] if parts and isinstance(parts[0], list) and parts[0] else None
            if isinstance(y, int) and not isinstance(y, bool):
                year = y
                break
        ct = it.get("container-title") or []
        venue = ct[0] if isinstance(ct, list) and ct else (ct if isinstance(ct, str) else "")
        doi = _norm_doi(it.get("DOI"))
        out.append({"title": str(title).strip(), "authors": authors[:6], "year": year, "venue": venue or "",
                    "doi": doi, "url": f"https://doi.org/{doi}" if doi else (it.get("URL") or ""),
                    "abstract_snippet": _snippet(it.get("abstract")), "source_api": "Crossref"})
    return out


def merge_dedupe(*lists: list[dict], cap: int = MAX_PER_RISK) -> list[dict]:
    """Merge by DOI (case-insensitive); entries without a DOI are matched on normalised title.  The first copy wins,
    but a missing abstract / venue is filled from a later copy, and source_api lists every index that returned it."""
    seen: dict[str, dict] = {}
    order: list[str] = []
    for lst in lists:
        for r in lst:
            key = ("doi:" + r["doi"]) if r.get("doi") else "t:" + re.sub(r"\W+", " ", r["title"].lower()).strip()
            if key in seen:
                cur = seen[key]
                for f in ("abstract_snippet", "venue", "year"):
                    if not cur.get(f) and r.get(f):
                        cur[f] = r[f]
                if r["source_api"] not in cur["source_api"].split(" + "):
                    cur["source_api"] += " + " + r["source_api"]
            else:
                seen[key] = dict(r)
                order.append(key)
    return [seen[k] for k in order][:cap]


# ------------------------------------------------------------------------------------------------ search
def _query_url(base: str, key: str, query: str, size_key: str, size: int) -> str:
    return base + "?" + urllib.parse.urlencode({key: query, size_key: size})


def search_literature(query: str, limit: int = MAX_PER_SOURCE) -> dict:
    """Query both indexes.  Returns {"ok": True, "results": [...], "errors": [...]} when at least one index replied,
    otherwise {"ok": False, "offline": True, "message": ...}.  Never raises."""
    limit = max(1, min(MAX_PER_SOURCE, int(limit)))
    lists, errors = [], []
    for name, url, parser in (
        ("OpenAlex", _query_url(OPENALEX_URL, "search", query, "per-page", limit), parse_openalex),
        ("Crossref", _query_url(CROSSREF_URL, "query", query, "rows", limit) + "&select=DOI,title,author,issued,container-title,abstract,URL",
         parse_crossref),
    ):
        try:
            lists.append(parser(_get_json(url))[:limit])
        except OfflineError as e:
            errors.append(f"{name}: {e}")
    if not lists:
        return {"ok": False, "offline": True,
                "message": "No internet connection (or the literature indexes are unreachable). The tool works fully "
                           "offline; try again when you are online. " + "; ".join(errors)}
    return {"ok": True, "results": merge_dedupe(*lists), "errors": errors}


def _catalogue_matches(risk_id: str, catalogue: list[dict]) -> list[dict]:
    return [{"catalogue_id": e.get("catalogue_id"), "measure": e.get("measure"), "strategy": e.get("strategy", "mitigate"),
             "mechanism": e.get("mechanism", ""), "inputs_required": list(e.get("inputs_required") or [])}
            for e in catalogue if risk_id in (e.get("applies_to") or [])]


def find_options_online(risks: list[dict], catalogue: Optional[list[dict]] = None) -> dict:
    """risks: [{"id", "name"}].  Output per risk: cited candidate sources + matching catalogue options."""
    catalogue = catalogue or []
    risks = risks[:MAX_RISKS]
    per, offline_msg = [], None
    for r in risks:
        matches = _catalogue_matches(r["id"], catalogue)
        extra = [m["measure"] for m in matches[:1] if m.get("measure")]
        res = search_literature(build_query(r["name"], extra))
        if not res["ok"]:
            offline_msg = res["message"]
            break                                  # one failed risk means the network is down; stop calling
        per.append({"risk_id": r["id"], "risk_name": r["name"], "query": build_query(r["name"], extra),
                    "sources": res["results"], "index_errors": res["errors"], "catalogue_options": matches})
    if offline_msg is not None and not per:
        return {"ok": False, "offline": True, "message": offline_msg, "note": NOTE}
    return {"ok": True, "offline": False, "note": NOTE, "risks": per,
            "partial": offline_msg is not None, "message": offline_msg or ""}
