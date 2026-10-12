"""Explanations of a result.

Primary explanation: built deterministically from the engine's own trace (no LLM), because
explanations that merely sound plausible can raise trust without improving decisions (E-notes).
Optional LLM narrative: allowed only as a secondary text, and every number in it is checked
against the numbers in the trace (guard G6).  Numbers not found are flagged, never silently kept.
"""
from __future__ import annotations

import json
import re
from typing import Any, Iterable, Mapping, Optional

from .guard import LLMClient

_ID_TOKEN = re.compile(r"\b[A-Za-z]{1,4}[-_]?[A-Za-z]{0,4}\d+[A-Za-z0-9\-]*\b")
_CURRENCY_PREFIX = re.compile(r"(?<![A-Za-z])(?:INR|Rs\.?|₹)\s*(?=\d)")
_NUM = re.compile(r"(?<![\w.])[-+]?\d[\d,]*\.?\d*%?")


def collect_numbers(obj: Any, out: Optional[set] = None) -> set[float]:
    out = set() if out is None else out
    if isinstance(obj, bool) or obj is None:
        return out
    if isinstance(obj, (int, float)):
        out.add(float(obj))
    elif isinstance(obj, Mapping):
        for k, v in obj.items():
            if isinstance(k, (int, float)):
                out.add(float(k))
            collect_numbers(v, out)
    elif isinstance(obj, (list, tuple, set)):
        for v in obj:
            collect_numbers(v, out)
    return out


def numbers_in(text: str) -> list[tuple[str, float]]:
    text = _CURRENCY_PREFIX.sub(" ", text)              # "INR999999", "Rs5000", "₹1,200": keep the amount, drop the prefix
    text = _ID_TOKEN.sub(" ", text)                     # ignore evidence / option / risk ids such as M01, R-MAT, O-A
    found = []
    for m in _NUM.finditer(text):
        raw = m.group(0)
        s = raw.rstrip("%").replace(",", "")
        try:
            found.append((raw, float(s) if not raw.endswith("%") else float(s)))
        except ValueError:
            continue
    return found


def check_numbers(text: str, trace: Mapping, rel_tol: float = 0.006, abs_tol: float = 0.051) -> list[str]:
    """Return the numbers in `text` that cannot be matched to any number in the trace (also allowing
    a value shown as a percentage of a fraction, or a fraction shown as a percentage)."""
    allowed = collect_numbers(trace)
    cand = set(allowed) | {v * 100 for v in allowed} | {v / 100 for v in allowed}
    bad = []
    for raw, val in numbers_in(text):
        if not any(abs(val - a) <= max(abs_tol, rel_tol * abs(a)) for a in cand):
            bad.append(raw)
    return bad


def explain_deterministic(result: Mapping) -> list[str]:
    """Plain-language explanation assembled from the numbers in the result, with no model involved."""
    s, c, d = result["summary"], result["cost"], result["decision"]
    b = result["baseline"]
    L = []
    L.append(f"Planned baseline duration is {b['planned_days']:.1f} working days ({b['basis']}).")
    L.append(f"Adding the modelled risks, the simulated mean duration is {s['mean']:.1f} days; the expected delay is "
             f"{s['expected_delay']:.1f} days. P50 is {s['percentiles']['P50']:.1f}, P80 {s['percentiles']['P80']:.1f}, "
             f"P90 {s['percentiles']['P90']:.1f} and P95 {s['percentiles']['P95']:.1f} days.")
    if "p_exceed_deadline" in s:
        L.append(f"The probability of finishing later than the deadline is {s['p_exceed_deadline'] * 100:.1f}% "
                 "under the stated inputs.")
    if result.get("sensitivity"):
        t = result["sensitivity"][0]
        L.append(f"The risk most strongly associated with total delay is {t['risk_id']} (rank correlation "
                 f"{t['spearman_with_total_delay']:.2f}; mean contribution {t['mean_contribution_days']:.2f} days). "
                 "This is a statistical association, not proof of cause.")
    L.append(f"Expected delay cost is {c['expected_cost']:,.0f} {c['currency']} (P90 {c['P90']:,.0f}).")
    sel = d.get("selected_option_id")
    opts = {o["option_id"]: o for o in d["options"]}
    if sel:
        o = opts[sel]
        L.append(f"Under the criterion '{d['criterion']}', option '{o['label']}' is preferred among the "
                 f"{sum(1 for x in d['options'] if x['admissible'])} admissible options evaluated: total expected cost "
                 f"{o['total_expected_cost']:,.0f}, P90 duration {o['P90']:.1f} days.")
        if sel != "ACCEPT":
            L.append(f"Compared with accepting the risks, it changes P90 by {o['P90_change_vs_accept']:+.1f} days and total "
                     f"expected cost by {o['total_expected_cost_change_vs_accept']:+,.0f}.")
    else:
        L.append("No evaluated option satisfies all constraints under the stated assumptions.")
    rejected = [(o["label"], "; ".join(o["rejected_because"])) for o in d["options"] if o["rejected_because"]]
    for lab, why in rejected:
        L.append(f"Option '{lab}' was removed: {why}.")
    n_assump = len(result.get("assumptions") or [])
    L.append(f"{n_assump} inputs are user, expert or assumed values; the result depends on them and is a simulation, "
             "not a validated prediction.")
    return L


def build_explain_prompt(result: Mapping) -> str:
    trace = {"summary": result["summary"], "cost": result["cost"], "baseline": result["baseline"],
             "decision": {k: result["decision"][k] for k in ("criterion", "selected_option_id", "statement", "options")},
             "sensitivity": result["sensitivity"][:5]}
    return ("Explain the following risk-analysis result to a construction site manager in 6-10 plain sentences. "
            "Use ONLY numbers present in the JSON (you may round). Do not add new numbers, probabilities, costs or "
            "recommendations beyond the stated decision. Do not say the option is optimal. Mention that inputs marked as "
            "assumptions drive the result.\nJSON:\n" + json.dumps(trace, default=float))


def explain_with_llm(client: LLMClient, result: Mapping) -> dict:
    prompt = build_explain_prompt(result)
    text = client.complete(prompt)
    trace = {"summary": result["summary"], "cost": result["cost"], "baseline": result["baseline"],
             "decision": result["decision"], "sensitivity": result["sensitivity"], "n": result.get("n_used")}
    bad = check_numbers(text, trace)
    return {"text": text, "unmatched_numbers": bad, "verified": not bad, "model_id": client.model_id, "prompt": prompt,
            "note": "Secondary narrative. Numbers that do not match the engine trace are flagged; rely on the deterministic explanation."}
