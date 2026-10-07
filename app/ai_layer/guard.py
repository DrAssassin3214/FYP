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
  G5  the raw prompt, model id, retrieved ids and raw output are kept verbatim in an audit log.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Protocol, Sequence

from app.engine.models import DelayDist, Param, Risk, RiskStatus, Source

from .evidence import EvidenceRecord, EvidenceStore

NUMERIC_KEYS = {"p", "probability", "delay", "delay_days", "min_delay", "max_delay", "most_likely_delay",
                "cost", "cost_inr", "effect", "effect_size", "p_after", "reduction", "expected_delay"}


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


def parse_and_validate(raw: str, retrieved_ids: set[str], store: EvidenceStore) -> list[RiskCandidate]:
    try:
        data = json.loads(raw)
        items = data["risks"]
        if not isinstance(items, list):
            raise ValueError
    except (ValueError, KeyError, TypeError):
        return [RiskCandidate("(unparseable output)", "", "", (), issues=["LLM output was not valid JSON in the required schema"])]
    out: list[RiskCandidate] = []
    for it in items:
        if not isinstance(it, dict) or not it.get("name"):
            continue
        issues: list[str] = []
        cited = [str(x) for x in (it.get("evidence_ids") or [])]
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
        for eid, quote in (it.get("quotes") or {}).items():
            rec = store.get(eid)
            norm = lambda s: re.sub(r"\s+", " ", str(s)).strip().lower()
            if rec is None or norm(quote) not in norm(rec.text + " " + rec.citation):
                issues.append(f"G3: quote for {eid} not found in the stored record text")
        rejected = {k: v for k, v in it.items() if k.lower() in NUMERIC_KEYS}
        if rejected:
            issues.append("G2: numeric fields from the LLM were rejected; values require user/expert/cited input")
        out.append(RiskCandidate(str(it["name"]), str(it.get("category", "")), str(it.get("mechanism", "")),
                                 tuple(good), issues=issues, rejected_numeric_fields=rejected))
    return out


def generate_candidates(client: LLMClient, activity_name: str, query: str, store: EvidenceStore, k: int = 6) -> dict:
    records = store.retrieve(query, k)
    prompt = build_prompt(activity_name, records)
    raw = client.complete(prompt)
    candidates = parse_and_validate(raw, {r.evidence_id for r in records}, store)
    return {
        "candidates": candidates,
        "audit": {"timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                  "model_id": client.model_id, "prompt": prompt, "retrieved_ids": [r.evidence_id for r in records],
                  "raw_output": raw},
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
