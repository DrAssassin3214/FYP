"""Generate Chapter 5 tables from the data files (no hand-typed values).
Writes report/tables/rules_table.md, library_categories.md, library_by_category.md, seed_status.md"""
import json, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "report" / "tables"; OUT.mkdir(exist_ok=True)
rules = json.loads((ROOT/"data/rules_masonry.json").read_text(encoding="utf-8-sig"))
lib = json.loads((ROOT/"data/risk_library_masonry.json").read_text(encoding="utf-8-sig"))
libname = {r["id"]: r["name"] for r in lib}
OPS = {"gt":">","ge":">=","lt":"<","le":"<=","eq":"=","ne":"!=","in":"in"}
def cond(c):
    rhs = c.get("other_fact") or (str(c["value"]).lower() if isinstance(c.get("value"), bool) else c.get("value"))
    return f"`{c['fact']}` {OPS[c['op']]} {'`'+rhs+'`' if c.get('other_fact') else rhs}"
lines = ["| Rule | Condition (in words) | Formal condition | Risk flagged | Level | Pri. | Source | Conf. |", "|---|---|---|---|---|---|---|---|"]
for r in rules:
    allc = " AND ".join(cond(c) for c in r.get("all_of", []))
    anyc = " OR ".join(cond(c) for c in r.get("any_of", []))
    f = allc + ((" AND (" + anyc + ")") if allc and anyc else anyc)
    lines.append(f"| {r['id']} | {r['description']} | {f} | {r['risk_id']} | {r['level']} | {r.get('priority',0)} | {r['source']} | {r['confidence']} |")
(OUT/"rules_table.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
c = collections.Counter(r["category"] for r in lib)
seed = json.loads((ROOT/"data/literature_seed.json").read_text(encoding="utf-8-sig"))
seeded = {x["risk"] for x in seed["rows"] if x.get("risk") and x.get("mapping")=="direct" and next(s for s in seed["studies"] if s["id"]==x["study"])["role"]=="seed"}
cat_lines = ["| Category | Risks | With seed value | Without |", "|---|---|---|---|"]
for k, n in sorted(c.items(), key=lambda kv: (-kv[1], kv[0])):
    s = sum(1 for r in lib if r["category"]==k and r["id"] in seeded)
    cat_lines.append(f"| {k} | {n} | {s} | {n-s} |")
cat_lines.append(f"| **Total** | **{len(lib)}** | **{sum(1 for r in lib if r['id'] in seeded)}** | **{sum(1 for r in lib if r['id'] not in seeded)}** |")
(OUT/"library_categories.md").write_text("\n".join(cat_lines)+"\n", encoding="utf-8")
# per-rule count per risk
print(len(rules), "rules;", len(lib), "risks;", len(seeded), "seeded")
print(collections.Counter(r["level"] for r in rules), collections.Counter(r["source"] for r in rules), collections.Counter(r["confidence"] for r in rules))
print("risks with rules:", len({r['risk_id'] for r in rules}), sorted({r['risk_id'] for r in rules}))
print("unseeded:", [r["id"] for r in lib if r["id"] not in seeded])
print("scope:", collections.Counter(r.get("scope") for r in lib))
print("facts:", len({c['fact'] for r in rules for c in r.get('all_of',[])+r.get('any_of',[]) } | {c['other_fact'] for r in rules for c in r.get('all_of',[])+r.get('any_of',[]) if c.get('other_fact')}))
# unseeded risks table
added = {"R-FRONT","R-VT","R-MORT","R-GPAY","R-OPEN","R-SCAF","R-FEST","R-HEAT"}
rule_by_risk = collections.defaultdict(list)
for r in rules: rule_by_risk[r["risk_id"]].append(r["id"])
ul = ["| Risk | Name | Category | Scope | Added 2026-10-08 | Rules that flag it |", "|---|---|---|---|---|---|"]
for r in lib:
    if r["id"] not in seeded:
        ul.append(f"| {r['id']} | {r['name']} | {r['category']} | {r.get('scope','')} | {'yes' if r['id'] in added else 'no'} | {', '.join(rule_by_risk.get(r['id'], [])) or 'none'} |")
(OUT/"unseeded_table.md").write_text("\n".join(ul)+"\n", encoding="utf-8")
