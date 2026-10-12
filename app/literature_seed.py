"""Literature seed: a starting place on the risk matrix for library risks whose numbers are not entered yet.

Data: data/literature_seed.json holds RII values copied from published surveys (the same file builds the Excel
workbook RII_Masonry_Literature.xlsx, so the app and the workbook cannot disagree).

Method:
  1. Keep only values from SEED studies (RII surveys from India / Sri Lanka) whose factor maps DIRECTLY to a tool risk.
  2. Per risk, average each study's direct items first (one study counts once), then average across studies.
  3. Rank the risks by that mean RII and split them into five equal-count bands (class 5 = most important).
  4. The band (the "literature tier", 1-5) is used for BOTH matrix axes, because a survey importance index measures
     neither probability nor days lost. A rule flag ("elevated") raises the probability class by one (capped at 5).
     Both steps are ASSUMPTIONS, labelled so in every output.
The placement is therefore a relative ranking, not an estimate. Numbers the user enters always replace it.

Basis "all" (opt-in, case field `seed_basis`): uses EVERY study in the dataset (seed and held-out) and both direct and
related mappings, with the same per-study averaging and banding. It pools the held-out studies, so no held-out
comparison remains for it (do not report basis "all" next to an agreement check), and "related" rows are weaker
matches. Default stays "seed".
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from statistics import mean
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
SEED_PATH = ROOT / "data" / "literature_seed.json"
N_CLASSES = 5


def load_dataset() -> dict:
    return json.loads(SEED_PATH.read_text(encoding="utf-8-sig"))


BASES = ("seed", "all")


def seed_observations(data: Optional[dict] = None, basis: str = "seed") -> list[dict]:
    """Rows the model uses. basis "seed": seed-study values that map directly to a tool risk.
    basis "all": every mapped row (direct or related) from every study."""
    data = data or load_dataset()
    if basis == "all":
        return [r for r in data["rows"] if r.get("risk") and r.get("mapping") in ("direct", "related")]
    roles = {s["id"]: s["role"] for s in data["studies"]}
    return [r for r in data["rows"] if roles.get(r["study"]) == "seed" and r.get("mapping") == "direct" and r.get("risk")]


@lru_cache(maxsize=1)
def _table_cached(mtime: float, basis: str) -> dict:
    data = load_dataset()
    obs = seed_observations(data, basis)
    risks = sorted({r["risk"] for r in data["rows"] if r.get("risk")})
    per_study: dict[str, dict[str, float]] = {}
    for rid in risks:
        studies = sorted({o["study"] for o in obs if o["risk"] == rid})
        per_study[rid] = {s: mean(o["rii"] for o in obs if o["risk"] == rid and o["study"] == s) for s in studies}
    seeded = {rid: mean(v.values()) for rid, v in per_study.items() if v}
    order = sorted(seeded, key=lambda r: (-seeded[r], r))
    n = len(order)
    out: dict[str, dict] = {}
    for rid in risks:
        mine = [o for o in obs if o["risk"] == rid]
        if rid in seeded:
            rank = order.index(rid) + 1
            cls = N_CLASSES - ((rank - 1) * N_CLASSES) // n          # equal-count bands, top rank -> class 5
            out[rid] = {"mean_rii": round(seeded[rid], 4), "rank": rank, "n_seeded": n, "class": cls,
                        "study_means": {s: round(v, 4) for s, v in per_study[rid].items()},
                        "observations": mine, "evidence_ids": sorted(per_study[rid]), "gap": None}
        else:
            out[rid] = {"mean_rii": None, "rank": None, "n_seeded": n, "class": None, "study_means": {},
                        "observations": [], "evidence_ids": [], "gap": "no direct RII in the seed studies"}
    return out


def seed_table(basis: str = "seed") -> dict[str, dict]:
    """risk_id -> {mean_rii, rank, n_seeded, class, study_means, observations, evidence_ids, gap}."""
    return _table_cached(SEED_PATH.stat().st_mtime, basis if basis in BASES else "seed")


def seed_for(risk_id: str, elevated: bool = False, basis: str = "seed") -> Optional[dict]:
    """Matrix placement for one risk, or None when the risk has no seed."""
    s = seed_table(basis).get(risk_id)
    if not s or s["class"] is None:
        return None
    p_class = min(N_CLASSES, s["class"] + 1) if elevated else s["class"]
    return {"p_class": p_class, "impact_class": s["class"], "tier": s["class"], "rank": s["rank"], "n_seeded": s["n_seeded"],
            "mean_rii": s["mean_rii"], "evidence_ids": s["evidence_ids"], "raised_by_rule": bool(elevated and p_class > s["class"])}

