"""Relevance / consistency guards G-1 .. G-10 (committee 2026-10-08).

Every count is READ FROM DATA, never typed in here, so a later change to a data file shows up as one failing
test with a clear message and forces a conscious update of the documents. Checksums are the exception on
purpose: they pin the seed rows (rii / rank / mapping) so that nothing can change them silently.
"""
import csv
import hashlib
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from app.ai_layer.guard import NUMERIC_KEYS, SUSPECT_KEYS
from app.literature_seed import load_dataset, seed_table
from app.reporting.matrix_graphic import register_html
from app.reporting.register_report import register_csv
from app.service import SOURCES, example_case, risk_library, rule_library, run_case

ROOT = Path(__file__).resolve().parents[1]
SEED_SHA = "9fc2fe05b49e908d8a83bfd933aaf1a531df53ec0fe4d1ce80f65f925fe78710"
SEED_SHA_FULL = "9e834e7dda17d784d1708e00d750177e569db187988a642a983d2864b4bac795"


def _counts():
    data = load_dataset()
    lib = risk_library()
    seeded = {k for k, v in seed_table().items() if v["class"] is not None}
    roles = [s["role"] for s in data["studies"]]
    return {"risks": len(lib), "seeded": len(seeded), "unseeded": len(lib) - len(seeded), "rows": len(data["rows"]),
            "studies": len(data["studies"]), "rules": len(rule_library()), "seed_studies": roles.count("seed"),
            "heldout_studies": roles.count("held-out") + roles.count("validation")}


def _sha(rows):
    return hashlib.sha256(json.dumps(rows, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------- G-1
def test_g1_counts_are_consistent_with_each_other():
    c = _counts()
    assert c["seeded"] + c["unseeded"] == c["risks"] and c["seed_studies"] + c["heldout_studies"] == c["studies"]
    lib = risk_library()
    assert c["unseeded"] == sum(1 for r in lib if r.get("seed_status"))
    assert len({r["id"] for r in lib}) == c["risks"] and len({r["id"] for r in rule_library()}) == c["rules"]
    assert c["seeded"] > 0 and c["rows"] > 0 and c["rules"] > 0


# --------------------------------------------------------------------------- G-2
DOCS_IN_SCOPE = ["README.md", "docs/case_schema.md", "gui/README_GUI.md"]


def _doc_numbers(pattern):
    out = []
    for d in DOCS_IN_SCOPE:
        text = (ROOT / d).read_text(encoding="utf-8-sig")
        out += [(d, int(m.group(1))) for m in re.finditer(pattern, text)]
    return out


def test_g2_current_docs_state_the_counts_in_the_data():
    c = _counts()
    for pattern, key in ((r"(\d+) site-fact rules", "rules"), (r"(\d+) rows", "rows"), (r"(\d+) studies", "studies")):
        found = _doc_numbers(pattern)
        assert found, f"no document states '{pattern}'"
        assert all(n == c[key] for _, n in found), f"{pattern}: docs say {found}, data says {c[key]}"
    risk_nums = [(d, n) for d, n in _doc_numbers(r"(\d+) (?:library )?risks") if n >= 10]
    assert risk_nums and {n for _, n in risk_nums} <= {c["risks"], c["seeded"], c["unseeded"]}, \
        f"risk counts in docs {risk_nums} vs data {c}"
    assert any(n == c["risks"] for _, n in risk_nums)


# --------------------------------------------------------------------------- G-3
def test_g3_seed_rows_are_frozen():
    rows = load_dataset()["rows"]
    msg = "seed rows changed: needs a supervisor decision and a re-run of the statistics"
    assert _sha([[r["study"], r["factor"], r["rii"], r["rank"]] for r in rows]) == SEED_SHA, msg
    assert _sha([[r["study"], r["factor"], r["rii"], r["rank"], r.get("risk"), r.get("mapping")] for r in rows]) == SEED_SHA_FULL, msg


# --------------------------------------------------------------------------- G-4
WITHDRAWN = [r"held out for validation", r"out-of-sample test", r"predicts study", r"(?<!not a )(?<!not )validated prediction",
             r"validation of the tool", r"built from every factor", r"No number here was produced by AI"]
SCAN = ["app", "gui", "scripts", "examples", "README.md", "docs/case_schema.md", "gui/README_GUI.md"]
SUFFIX = {".py", ".js", ".html", ".md", ".json", ".css", ".bat", ".txt"}


def test_g4_withdrawn_wording_does_not_occur():
    hits = []
    for entry in SCAN:
        base = ROOT / entry
        files = [base] if base.is_file() else [f for f in base.rglob("*") if f.is_file() and f.suffix in SUFFIX and "__pycache__" not in f.parts]
        for f in files:
            text = f.read_text(encoding="utf-8-sig", errors="ignore")
            for pat in WITHDRAWN:
                for m in re.finditer(pat, text, flags=re.I):
                    hits.append(f"{f.relative_to(ROOT)}: '{m.group(0)}'")
    assert not hits, "withdrawn wording found: " + "; ".join(hits)


def test_g4_handoff_only_mentions_withdrawn_wording_on_lines_that_say_so():
    in_withdrawn_table = False
    for line in (ROOT / "docs/Project_Handoff_Summary.md").read_text(encoding="utf-8-sig").splitlines():
        if line.startswith("|") and re.search(r"withdrawn wording", line, flags=re.I):
            in_withdrawn_table = True                    # header of the section 8.11 table
        elif not line.startswith("|"):
            in_withdrawn_table = False
        for pat in WITHDRAWN:
            if re.search(pat, line, flags=re.I):
                assert in_withdrawn_table or re.search(r"withdrawn|superseded", line, flags=re.I), line[:160]


# --------------------------------------------------------------------------- G-5
def _full_library_case():
    c = example_case()
    c["risks"] += [{"id": r["id"], "name": r["name"], "category": r["category"]} for r in risk_library()
                   if r["id"] not in {x["id"] for x in c["risks"]}]
    return c


@pytest.mark.parametrize("case_fn", [example_case, _full_library_case])
def test_g5_every_exported_number_has_a_source(case_fn):
    res = run_case(case_fn())
    recs = list(csv.DictReader(io.StringIO(register_csv(res))))
    assert recs
    for r in recs:
        if r["p"] != "":
            assert r["p_source"] in SOURCES, r["id"]
        if any(r[k] != "" for k in ("delay_min", "delay_most_likely", "delay_max")):
            assert r["delay_source"] in SOURCES, r["id"]
        if r["expected_delay_days"] != "":
            assert r["expected_delay_source"] == "Derived Calculation", r["id"]
        if r["p_class"] != "":
            assert r["basis"], r["id"]
        if r["basis"].startswith("literature seed"):
            assert r["level"] == "" and r["tier"].startswith("literature tier (Assumption)"), r["id"]
    md, html = res["report_markdown"], register_html(res)
    assert "(Source: " in md.split("Planned duration:")[1].split("\n")[0]
    for text in (md, html):
        assert "Impact edges" in text and "Source:" in text.split("Impact edges")[1][:200]
        assert "Probability edges" in text and "(Source: Assumption, tool default)" in text
    for r in res["risks"]:
        if r["p"]:
            line = next(ln for ln in md.splitlines() if ln.startswith(f"| {r['id']} |"))
            assert any(f"({s})" in line for s in SOURCES), line
            cell = re.search(rf"<td>{re.escape(r['id'])}</td>.*?</tr>", html, flags=re.S).group(0)
            assert any(f"({s})" in cell for s in SOURCES), r["id"]


# --------------------------------------------------------------------------- G-6
def test_g6_legacy_modules_are_not_imported_by_the_live_app():
    code = r'''
import json, sys
import gui.api
app = gui.api.create_app(); app.config["TESTING"] = True
c = app.test_client()
assert c.get("/api/health").status_code == 200
ex = c.get("/api/example").get_json()
assert c.post("/api/run", json=ex).status_code == 200
assert c.post("/api/suggest-risks", json={"activity_name": "Brick masonry", "query": "labour shortage"}).status_code == 200
import app.cli
bad = [m for m in sys.modules if m in ("app.engine.simulation", "app.engine.emv", "app.engine.decision", "app.reporting.report", "app.ai_layer.explain") or m.startswith("app.productivity")]
print(json.dumps(bad))
'''
    env = dict(os.environ, PYTHONPATH=os.pathsep.join(filter(None, [str(ROOT), os.environ.get("PYTHONPATH", "")])))
    out = subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=env, capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, out.stderr[-800:]
    assert json.loads(out.stdout.strip().splitlines()[-1]) == []


def test_g6_front_end_does_not_load_legacy_screens():
    js = (ROOT / "gui/static/js/app.js").read_text(encoding="utf-8") + (ROOT / "gui/static/index.html").read_text(encoding="utf-8")
    for legacy in ("simulation", "cost", "decision", "mitigation", "productivity", "explain"):
        assert f"screens/{legacy}.js" not in js, legacy


# --------------------------------------------------------------------------- G-7
def test_g7_the_example_stays_illustrative_everywhere():
    from app.reporting.register_report import _is_illustrative
    c = example_case()
    assert "ILLUSTRATIVE" in c["project"]["name"]
    for r in c["risks"]:
        for k in ("p", "delay"):
            assert r[k]["source"] == "Assumption" and "ILLUSTRATIVE" in r[k]["note"], (r["id"], k)
    assert c["impact_bin_edges_source"]["source"] == "Assumption" and "ILLUSTRATIVE" in c["impact_bin_edges_source"]["note"]
    res = run_case(c)
    assert _is_illustrative(res)
    assert all(r["note"] for r in csv.DictReader(io.StringIO(register_csv(res))))
    assert "ILLUSTRATIVE case" in res["report_markdown"] and "ILLUSTRATIVE case" in register_html(res)


# --------------------------------------------------------------------------- G-8
def test_g8_rule_base_sanity():
    rules = rule_library()
    for r in rules:
        assert r["source"] == "Assumption" or (r["source"] in ("Literature", "Historical Data") and r.get("evidence_ids")), r["id"]
        assert r.get("level", "elevated") in ("elevated", "normal"), r["id"]
    by_risk = {}
    for r in rules:
        by_risk.setdefault(r["risk_id"], []).append(r)
    for rid, rs in by_risk.items():
        for a in rs:
            for b in rs:
                if a["id"] < b["id"] and a.get("level", "elevated") != b.get("level", "elevated"):
                    assert a.get("priority", 0) != b.get("priority", 0), f"{a['id']} and {b['id']} on {rid}: equal priority, different levels"
    facts = {c["fact"] for r in rules for k in ("all_of", "any_of") for c in r.get(k) or []}
    facts |= {c["other_fact"] for r in rules for k in ("all_of", "any_of") for c in r.get(k) or [] if c.get("other_fact")}
    facts.discard("planned_duration_days")
    js = (ROOT / "gui/static/js/screens/rules.js").read_text(encoding="utf-8")
    missing = [f for f in sorted(facts) if f"{f}: {{" not in js]
    assert not missing, f"facts without a FACT_INFO label: {missing}"
    lib_ids = {r["id"] for r in risk_library()}
    assert {r["risk_id"] for r in rules} <= lib_ids


# --------------------------------------------------------------------------- G-9
def test_g9_unseeded_library_risks_are_labelled_and_have_no_seed_rows():
    seeded = {k for k, v in seed_table().items() if v["class"] is not None}
    mapped = {r["risk"] for r in load_dataset()["rows"] if r.get("risk")}
    new_eight = ["R-FRONT", "R-VT", "R-MORT", "R-GPAY", "R-OPEN", "R-SCAF", "R-FEST", "R-HEAT"]
    assert not (set(new_eight) & mapped), "the new risks must have no seed rows"
    for r in risk_library():
        if r["id"] not in seeded:
            assert r.get("seed_status"), f"{r['id']} is not seeded and has no seed_status"
        if r.get("seed_status"):
            assert r["id"] not in seeded, r["id"]            # a marked risk has no direct seed-study value
            assert r["existence_evidence"], r["id"]


def test_g9_new_risk_evidence_ids_exist_in_the_corpus():
    from app.service import _store
    store = _store()
    for r in risk_library():
        if r.get("seed_status"):
            assert all(e in store for e in r["existence_evidence"]), r["id"]


# --------------------------------------------------------------------------- G-10
def test_g10_ai_path_cannot_carry_numbers():
    from app.ai_layer.guard import RiskCandidate, promote
    from app.engine.models import DelayDist, Param, Source
    from gui.api import create_app
    cand = RiskCandidate("Shortage", "Material", "x", ("M01",))
    with pytest.raises(ValueError):
        promote(cand, "R1", Param(0.3, Source.DERIVED), DelayDist("pert", 1, 3, 8, source=Source.EXPERT))
    with pytest.raises(ValueError):
        promote(cand, "R1", Param(0.3, Source.EXPERT), DelayDist("pert", 1, 3, 8, source=Source.DERIVED))
    app = create_app(); app.config["TESTING"] = True
    out = app.test_client().post("/api/suggest-risks", json={"activity_name": "Brick masonry", "query": "labour shortage payment"}).get_json()
    banned = {k.lower() for k in NUMERIC_KEYS | SUSPECT_KEYS}

    def walk(o, path=""):
        if isinstance(o, dict):
            for k, v in o.items():
                assert str(k).lower() not in banned, f"numeric-looking key '{k}' at {path}"
                walk(v, f"{path}/{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{path}[{i}]")
    walk(out)
