"""Consistency and outlier check of every data file the tool reads (exit 1 on a finding).

    python scripts/check_data.py

It reads only files in the repository (no database, no network).  It checks what could make the tool print a wrong
number or a dangling citation: duplicate ids, references to risks / studies / evidence ids that do not exist,
RII values outside (0, 1], ranks that do not match the RII order inside a study, and rules over unknown facts.
It never edits a file.
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app import service  # noqa: E402
from app.engine.rules import check_rule_base  # noqa: E402


def load(name):
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8-sig"))


def main() -> int:
    bad: list[str] = []
    lib, rules = load("risk_library_masonry.json"), load("rules_masonry.json")
    seed, cat = load("literature_seed.json"), load("mitigation_catalogue.json")["entries"]
    evidence = set(service.evidence_index_from_workbook())
    risk_ids = [r["id"] for r in lib]

    for k, n in Counter(risk_ids).items():
        if n > 1:
            bad.append(f"library: duplicate risk id {k}")
    for r in lib:
        for key in ("id", "name", "category", "description", "existence_evidence", "scope"):
            if not r.get(key):
                bad.append(f"library {r.get('id')}: '{key}' is empty")
        for e in r.get("existence_evidence", []):
            if evidence and e not in evidence:
                bad.append(f"library {r['id']}: evidence id {e} not in the evidence workbook")

    for e in check_rule_base(service.parse_case({})["rules"], sorted(service._known_fact_names())):
        bad.append(f"rules: {e}")
    for r in rules:
        if r["risk_id"] not in risk_ids:
            bad.append(f"rule {r['id']}: risk {r['risk_id']} is not in the library")
        for e in r.get("evidence_ids", []):
            if evidence and e not in evidence:
                bad.append(f"rule {r['id']}: evidence id {e} not in the evidence workbook")

    studies = {s["id"]: s for s in seed["studies"]}
    seen = Counter()
    by_study = defaultdict(list)
    for row in seed["rows"]:
        seen[(row["study"], row["factor"])] += 1
        if row["study"] not in studies:
            bad.append(f"seed row {row['study']}/{row['factor']}: study not defined")
        if not isinstance(row["rii"], (int, float)) or not 0 < row["rii"] <= 1:
            bad.append(f"seed row {row['study']}/{row['factor']}: rii {row['rii']} outside (0, 1]")
        if row.get("risk") and row["risk"] not in risk_ids:
            bad.append(f"seed row {row['study']}/{row['factor']}: risk {row['risk']} is not in the library")
        by_study[row["study"]].append(row)
    for k, n in seen.items():
        if n > 1:
            bad.append(f"seed: duplicate row {k}")
    for sid, rows in by_study.items():
        # within a study a higher RII must never have a worse (larger) rank
        ranked = [r for r in rows if isinstance(r.get("rank"), int)]
        for a in ranked:
            for b in ranked:
                if a["rii"] > b["rii"] and a["rank"] > b["rank"]:
                    bad.append(f"seed {sid}: '{a['factor']}' has higher RII than '{b['factor']}' but a worse rank")
                    break

    for c in cat:
        for rid in c.get("applies_to", []):
            if rid not in risk_ids:
                bad.append(f"mitigation {c['catalogue_id']}: applies to unknown risk {rid}")
        for e in c.get("evidence_ids", []):
            if evidence and e not in evidence:
                bad.append(f"mitigation {c['catalogue_id']}: evidence id {e} not in the evidence workbook")

    print(f"checked: {len(lib)} risks, {len(rules)} rules, {len(seed['rows'])} seed rows in {len(studies)} studies, "
          f"{len(cat)} catalogue entries, {len(evidence)} evidence ids")
    for b in bad:
        print("FINDING:", b)
    print("OK" if not bad else f"{len(bad)} finding(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
