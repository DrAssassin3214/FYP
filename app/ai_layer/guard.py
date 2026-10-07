"""Guardrails between an LLM and the deterministic engine.

What the LLM may do : propose candidate risks / mitigation options with a mechanism and citations.
What it may NOT do  : supply probabilities, delay ranges, costs or effect sizes; edit any parameter;
                      cite anything that was not retrieved from the curated evidence store.

Guard rules (each is enforced in code and tested):
  G1  every cited id must be in the retrieved set AND in the store, otherwise it is dropped and flagged;
  G2  any numeric field the LLM returns is stripped and logged as rejected (values come only from
      user / expert / cited data with a Source);
  G3  quoted text must appear in the cited record's stored text, otherwise the quote is flagged;
  G4  output is always AI_UNVERIFIED; only an explicit user confirmation can change the status;
  G5  the raw prompt, model id, retrieved ids and raw output are kept verbatim in an audit log;
  G7  a suggestion whose name, category or mechanism contains a probability, percentage, duration, day-count or
      currency figure is rejected (the AI may not smuggle numbers in as prose) and the rejection is logged;
  G8  every field is type-checked; one malformed item is dropped and logged, the other suggestions survive;
  G9  unknown numeric keys (likelihood, days, impact, ...) are dropped and logged like the listed ones (G2).
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Protocol, Sequence

from app.engine.models import DelayDist, Param, Risk, RiskStatus, Source

from .clients import extract_json
from .evidence import EvidenceRecord, EvidenceStore

NUMERIC_KEYS = {"p", "probability", "delay", "delay_days", "min_delay", "max_delay", "most_likely_delay",
                "cost", "cost_inr", "effect", "effect_size", "p_after", "reduction", "expected_delay"}
# keys an LLM tends to invent for the same purpose; dropped and logged under G9
SUSPECT_KEYS = {"likelihood", "days", "impact", "severity", "chance", "odds", "duration", "duration_days",
                "price", "budget", "score", "rating", "rii", "percent", "percentage", "min", "max", "mean",
                "most_likely", "expected_cost", "delay_range", "impact_days", "cost_estimate", "estimate"}

_NUMWORD = r"(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|thirty|forty|fifty|sixty|ninety|hundred)"
_UNIT = r"(?:working\s+|calendar\s+)?(?:days?|weeks?|months?|hours?|hrs?)"
FIGURE_PATTERNS = [
    (re.compile(r"\d\s*%|\bper\s?cent\b|\bpercent(?:age)?\b", re.I), "a percentage"),
    (re.compile(r"\b(?:probability|likelihood|chance|odds|p)\b\s*(?:of|is|=|:|at|about|around)?\s*(?:approximately\s+|~\s*)?(?:0?\.\d+|\d+)", re.I), "a probability figure"),
    (re.compile(r"\b0?\.\d+\s+(?:probability|likelihood|chance)", re.I), "a probability figure"),
    (re.compile(r"(?<![A-Za-z0-9])\d+(?:[.,]\d+)?\s*(?:-|to|–)?\s*(?:\d+(?:[.,]\d+)?\s*)?" + _UNIT + r"\b", re.I), "a duration / day-count"),
    (re.compile(r"\b" + _NUMWORD + r"(?:\s*(?:-|to|–)\s*" + _NUMWORD + r")?\s+" + _UNIT + r"\b", re.I), "a duration / day-count"),
    (re.compile(r"(?<![A-Za-z])(?:INR|Rs\.?|₹)\s*[\d,]", re.I), "a currency amount"),
    (re.compile(r"\d[\d,]*(?:\.\d+)?\s*(?:INR|Rs|rupees|lakhs?|crores?)\b", re.I), "a currency amount"),
]


def find_figures(text) -> list[str]:
    """Describe every probability / percentage / duration / currency figure found in free text."""
    if not isinstance(text, str):
        return []
    found = []
    for rx, label in FIGURE_PATTERNS:
        m = rx.search(text)
        if m and label not in found:
            found.append(label)
    return found


class LLMClient(Protocol):
    model_id: str

    def complete(self, prompt: str) -> str: ...


@dataclass
class RiskCandidate:
    name: str
    category: str
    mechanism: str
    evidence_ids: tuple[str, ...]
    status: RiskStatus = RiskStatus.AI_UNVERIFIED
    issues: list[str] = field(default_factory=list)
    rejected_numeric_fields: dict = field(default_factory=dict)


def build_prompt(activity_name: str, records: Sequence[EvidenceRecord]) -> str:
    ctx = "\n".join(f"[{r.evidence_id}] {r.citation} :: {r.text[:600]}" for r in records)
    return (
        "You assist a construction risk analyst. Use ONLY the evidence below.\n"
        f"Activity: {activity_name}\n"
        "Task: propose candidate schedule risks for this activity. For each give: name, category, mechanism, "
        "evidence_ids (only IDs listed below), optional quotes {id: exact quote}.\n"
        "Do NOT give probabilities, delay durations, costs or effect sizes. If the evidence does not support a risk, "
        "do not propose it; if nothing is supported, return an empty list.\n"
        'Return JSON only: {"risks": [{"name":..., "category":..., "mechanism":..., "evidence_ids": [...], "quotes": {...}}]}\n'
        f"EVIDENCE:\n{ctx}\n"
    )


def _is_number(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def parse_and_validate(raw: str, retrieved_ids: set[str], store: EvidenceStore,
                       log: Optional[list] = None) -> list[RiskCandidate]:
    """Validate an LLM reply. Rejected / dropped items are appended to `log` (a list of dicts with a rule id)."""
    log = log if log is not None else []
    try:
        data = extract_json(raw)
        items = data["risks"] if isinstance(data, dict) else data
        if not isinstance(items, list):
            raise ValueError
    except (ValueError, KeyError, TypeError):
        return [RiskCandidate("(unparseable output)", "", "", (), issues=["LLM output was not valid JSON in the required schema"])]
    norm = lambda s: re.sub(r"\s+", " ", str(s)).strip().lower()
    out: list[RiskCandidate] = []
    for n, it in enumerate(items):
        def drop(rule: str, why: str, name=None):
            log.append({"rule": rule, "item": n, "name": name if isinstance(name, str) else None, "reason": why})

        if not isinstance(it, dict):
            drop("G8", f"item is a {type(it).__name__}, not an object; dropped")
            continue
        name = it.get("name")
        if not isinstance(name, str):
            drop("G8", "name is missing or not text; item dropped")
            continue
        if not name.strip():
            continue
        bad_type = [f for f, t in (("category", str), ("mechanism", str)) if it.get(f) is not None and not isinstance(it.get(f), t)]
        eids = it.get("evidence_ids")
        if eids is not None and not isinstance(eids, list):
            bad_type.append("evidence_ids")
        quotes = it.get("quotes")
        if quotes is not None and not (isinstance(quotes, dict) and all(isinstance(v, str) for v in quotes.values())):
            bad_type.append("quotes")
        if bad_type:
            drop("G8", "wrong type for " + ", ".join(bad_type) + "; item dropped", name)
            continue
        figs = sorted({f for fld in ("name", "category", "mechanism") for f in find_figures(it.get(fld))})
        if figs:
            drop("G7", "free text contains " + ", ".join(figs) + "; the AI may not supply probabilities, delays or costs; suggestion rejected", name)
            continue
        issues: list[str] = []
        cited = []
        for e in eids or []:
            if not isinstance(e, str):
                issues.append(f"G8: evidence id {e!r} is not text; dropped")
                log.append({"rule": "G8", "item": n, "name": name, "reason": f"evidence id {e!r} is not text; dropped"})
            else:
                cited.append(e)
        good = []
        for e in cited:
            if e not in retrieved_ids:
                issues.append(f"G1: cited id {e} was not in the retrieved evidence; dropped")
            elif e not in store:
                issues.append(f"G1: cited id {e} not in the evidence store; dropped")
            else:
                good.append(e)
        if not good:
            issues.append("no valid supporting evidence: AI-suggested and unsupported")
        for eid, quote in (quotes or {}).items():
            rec = store.get(eid)
            if rec is None or norm(quote) not in norm(rec.text + " " + rec.citation):
                issues.append(f"G3: quote for {eid} not found in the stored record text")
        rejected = {k: v for k, v in it.items() if isinstance(k, str) and k.lower() in NUMERIC_KEYS}
        if rejected:
            issues.append("G2: numeric fields from the LLM were rejected; values require user/expert/cited input")
        extra = {k: v for k, v in it.items() if isinstance(k, str) and k not in rejected
                 and (k.lower() in SUSPECT_KEYS or (_is_number(v) and k not in ("name", "category", "mechanism")))}
        if extra:
            issues.append("G9: unknown numeric fields from the LLM were dropped: " + ", ".join(sorted(extra)))
            log.append({"rule": "G9", "item": n, "name": name, "reason": "unknown numeric keys dropped: " + ", ".join(sorted(extra))})
            rejected = {**rejected, **extra}
        out.append(RiskCandidate(name, str(it.get("category") or ""), str(it.get("mechanism") or ""),
                                 tuple(good), issues=issues, rejected_numeric_fields=rejected))
    return out


def generate_candidates(client: LLMClient, activity_name: str, query: str, store: EvidenceStore, k: int = 6) -> dict:
    records = store.retrieve(query, k)
    prompt = build_prompt(activity_name, records)
    raw = client.complete(prompt)
    guard_log: list = []
    candidates = parse_and_validate(raw, {r.evidence_id for r in records}, store, guard_log)
    return {
        "candidates": candidates,
        "audit": {"timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                  "model_id": client.model_id, "prompt": prompt, "retrieved_ids": [r.evidence_id for r in records],
                  "raw_output": raw, "guard_log": guard_log},
    }


def promote(candidate: RiskCandidate, risk_id: str, p: Param, delay: DelayDist, *, user_confirmed: bool = False,
            literature_supported: bool = False) -> Risk:
    """Turn a candidate into an engine Risk.  p and delay must be supplied by a person or a cited
    source (never Source.DERIVED from the LLM).  Status stays AI-unverified until explicitly confirmed (G4)."""
    if p.source == Source.DERIVED:
        raise ValueError("probability cannot be a derived/AI value; supply a user, expert or literature source")
    if delay.source == Source.DERIVED:
        raise ValueError("delay distribution cannot be a derived/AI value")
    status = RiskStatus.AI_UNVERIFIED
    if user_confirmed:
        status = RiskStatus.EXPERT_USER
        if literature_supported:
            if not candidate.evidence_ids:
                raise ValueError("cannot mark literature-supported without valid evidence ids")
            status = RiskStatus.LITERATURE_SUPPORTED
    return Risk(risk_id, candidate.name, p, delay, category=candidate.category, description=candidate.mechanism,
                status=status, evidence_ids=candidate.evidence_ids)


class StubLLM:
    """Offline stand-in used for tests and demos; returns a fixed string."""

    model_id = "stub-llm-v0"

    def __init__(self, output: str):
        self.output = output

    def complete(self, prompt: str) -> str:
        return self.output
