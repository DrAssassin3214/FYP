#!/usr/bin/env python3
"""Generate report appendices A-J into report/chapters/90_appendix_*.md from the repository's real data.

Run:  PYTHONPATH=/usr/local/lib/python3.13/dist-packages python3 report/scripts/gen_appendices.py [--no-pytest]

A  data/literature_seed.json          (182 rows)
B  data/risk_library_masonry.json + app.literature_seed.seed_table()
C  data/rules_masonry.json
D  gui/api.py (route table parsed from source) + condensed case schema
E  pytest -v run now (raw log saved to report/scripts/out/pytest_log.txt), per-file counts
F,G,I,J  prose templates in report/scripts/templates/*.md with {{placeholders}} filled from data
H  Assumption register (rows defined here, sensitivity figures read from analysis/out/*.json when present)
Nothing here invents a number: every figure is read from a repo file or computed from one.
"""
from __future__ import annotations

import ast
import collections
import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "report" / "chapters"
TPL = Path(__file__).resolve().parent / "templates"
LOGDIR = Path(__file__).resolve().parent / "out"
LOGDIR.mkdir(exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

from app import literature_seed as LS  # noqa: E402


def esc(s) -> str:
    """Escape a value for a Markdown pipe-table cell."""
    return str(s).replace("|", "\\|").replace("\n", " ").strip()


def jload(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8-sig"))


SEED = jload("data/literature_seed.json")
LIB = jload("data/risk_library_masonry.json")
RULES = jload("data/rules_masonry.json")
ROLE = {s["id"]: s["role"] for s in SEED["studies"]}
ROLE_LABEL = {"seed": "seed", "validation": "held-out"}
LIBNAME = {r["id"]: r["name"] for r in LIB}
SEEDTAB = LS.seed_table()
for _r in LIB:
    SEEDTAB.setdefault(_r["id"], {"mean_rii": None, "rank": None, "class": None, "study_means": {}, "gap": "no survey rows"})
seeded_ids = [k for k, v in SEEDTAB.items() if v.get("mean_rii") is not None]

N_ROWS = len(SEED["rows"])
N_STUDIES = len(SEED["studies"])
N_SEED_STUDIES = sum(1 for s in SEED["studies"] if s["role"] == "seed")
N_RISKS = len(LIB)
N_SEEDED = len(seeded_ids)
N_UNSEEDED = N_RISKS - N_SEEDED
N_RULES = len(RULES)
N_MAPPED_RISKS = len({r["risk"] for r in SEED["rows"] if r.get("risk")})
CNT_MAP = collections.Counter(r.get("mapping") for r in SEED["rows"])
assert (N_ROWS, N_STUDIES, N_RISKS, N_RULES) == (182, 11, 46, 22), (N_ROWS, N_STUDIES, N_RISKS, N_RULES)
assert (N_SEEDED, N_UNSEEDED) == (30, 16)


def write(name: str, text: str) -> None:
    p = OUT / name
    p.write_text(text.rstrip() + "\n", encoding="utf-8")
    print(f"wrote {p.relative_to(ROOT)}  ({len(text.split())} words)")


def table(header, rows, align=None):
    out = ["| " + " | ".join(header) + " |"]
    out.append("|" + "|".join((":---" if (align and align[i] == "l") else ("---:" if (align and align[i] == "r") else "---")) for i in range(len(header))) + "|")
    for r in rows:
        out.append("| " + " | ".join(esc(c) for c in r) + " |")
    return "\n".join(out)


def fill(template_name: str, **kw) -> str:
    t = (TPL / template_name).read_text(encoding="utf-8")
    for k, v in kw.items():
        t = t.replace("{{" + k + "}}", str(v))
    left = re.findall(r"\{\{[a-z_0-9]+\}\}", t)
    assert not left, f"unfilled placeholders in {template_name}: {left}"
    return t


COMMON = dict(
    n_rows=N_ROWS, n_studies=N_STUDIES, n_seed_studies=N_SEED_STUDIES, n_heldout=N_STUDIES - N_SEED_STUDIES,
    n_risks=N_RISKS, n_seeded=N_SEEDED, n_unseeded=N_UNSEEDED, n_rules=N_RULES,
    n_mapped_risks=N_MAPPED_RISKS, n_direct=CNT_MAP["direct"], n_related=CNT_MAP["related"], n_unmapped=CNT_MAP[None],
    n_factor_rows=N_ROWS - CNT_MAP[None], n_activity=sum(1 for r in LIB if r["scope"] == "activity"),
    n_project=sum(1 for r in LIB if r["scope"] == "project"),
    n_cats=N_RISKS + 1,
    today=datetime.date.today().isoformat(),
)

# ------------------------------------------------------------------ A
def appendix_a():
    rows = []
    for i, r in enumerate(SEED["rows"], 1):
        mp = r.get("mapping")
        rows.append([
            i, f"{r['study']} ({ROLE_LABEL[ROLE[r['study']]]})", r["factor"],
            f"{r['rii']:.3f}", r["rank"] if r["rank"] is not None else "not printed",
            r.get("risk") or "none (unmapped)", mp if mp else "none",
        ])
    per_study = collections.Counter(r["study"] for r in SEED["rows"])
    st_rows = []
    for s in SEED["studies"]:
        st_rows.append([s["id"], ROLE_LABEL[s["role"]], s["year"], s["country"], s["n"], s["scale"], per_study[s["id"]]])
    txt = f"""# Appendix A. Literature seed table: all {N_ROWS} rows

This appendix reproduces every row of `data/literature_seed.json` in file order (Source: Literature; transcribed from the printed papers and checked row by row against the PDFs on 2026-10-08, see `docs/Audit_Corrections_2026-10-08.md` section 3). Generated by `report/scripts/gen_appendices.py`. No value has been altered. The RII is a survey importance index; it is not a probability and not a number of days. The rank is the rank printed in the source study, within that study's own list, and is not comparable between studies. "Mapped risk" is the library risk the team assigned (Source: Expert Judgment, single coder; the second-coder check is not done, see Appendix G). Mapping type "direct" means the factor is the same thing as the library risk; "related" means a looser match, and only "direct" rows of seed studies feed the literature seed. {CNT_MAP['direct']} rows are direct, {CNT_MAP['related']} related and {CNT_MAP[None]} unmapped (three are group-level rows or are noted as such in the file, one is the M14 item "No consumption"). The seed studies are a subset of the factors printed in several papers (for A14 only 5 of 39 factors were entered, for A15 5 of 32, for A02 14 of 35); M01 prints only factors with RII of 0.700 or more. These selection effects are discussed in Chapters 4 and 7.

**Table A.1.** The {N_STUDIES} studies in the seed file ({N_SEED_STUDIES} seed, {N_STUDIES - N_SEED_STUDIES} held-out) and the number of rows each contributes. Source: `data/literature_seed.json`, field `studies`; row counts are a Derived Calculation from the file.

{table(['Study', 'Role', 'Year', 'Country / context', 'N', 'Scale', 'Rows'], st_rows)}

**Table A.2.** The {N_ROWS} seed rows. "Not printed" means the paper does not print a rank for that row. Source: Literature (`data/literature_seed.json`, field `rows`); mapped risk and mapping type: Expert Judgment.

{table(['No.', 'Study (role)', 'Factor as printed', 'RII', 'Rank', 'Mapped risk', 'Mapping'], rows)}
"""
    write("90_appendix_A_seed_table.md", txt)


# ------------------------------------------------------------------ B
def appendix_b():
    rows = []
    for r in LIB:
        v = SEEDTAB[r["id"]]
        if v.get("mean_rii") is not None:
            status = f"seeded: rank {v['rank']} of {N_SEEDED}, class {v['class']}, {len(v['study_means'])} stud{'y' if len(v['study_means'])==1 else 'ies'}"
        else:
            status = "unseeded: " + r.get("seed_status", v.get("gap") or "no seed value")
        rows.append([r["id"], r["name"], r["category"], r["scope"], status, ", ".join(r["existence_evidence"])])
    cat = collections.Counter(r["category"] for r in LIB)
    cat_rows = [[c, n] for c, n in sorted(cat.items(), key=lambda x: (-x[1], x[0]))]
    unseeded = [r["id"] for r in LIB if SEEDTAB[r["id"]].get("mean_rii") is None]
    txt = f"""# Appendix B. Risk library: all {N_RISKS} risks

The risk library (`data/risk_library_masonry.json`) holds {N_RISKS} candidate delay risks for one brick or block masonry activity: 38 from the original compilation and 8 added on 2026-10-08 (R-FRONT, R-VT, R-MORT, R-GPAY, R-OPEN, R-SCAF, R-FEST, R-HEAT). {COMMON['n_activity']} are scoped to the activity and {COMMON['n_project']} to the project as a whole. "Seeded" means at least one direct survey row of a seed study maps to the risk, so the literature seed can place it at an ordinal tier; rank and class are those of `app.literature_seed.seed_table()` on the five seed studies (Derived Calculation, Assumption: five equal-count bands). "Unseeded" risks have no survey value; they stay off the matrix until probability and delay are entered, and carry the `seed_status` text from the library. Evidence IDs point to records in the evidence corpus (`Literature_Evidence_Package.xlsx`, `Research_Notes/`) and support that the risk exists, never its size. The masonry-specific form of the 8 added risks is labelled Expert Judgment, to be confirmed by the expert survey (Appendix F).

**Table B.1.** Library risks by category. Source: Derived Calculation from `data/risk_library_masonry.json`.

{table(['Category', 'Risks'], cat_rows)}

**Table B.2.** The {N_RISKS} library risks. Source: `data/risk_library_masonry.json` (name, category, scope, evidence IDs: Literature); seed status: Derived Calculation from `data/literature_seed.json`.

{table(['ID', 'Name', 'Category', 'Scope', 'Seed status', 'Evidence IDs'], rows)}

Unseeded risks ({N_UNSEEDED}): {', '.join(unseeded)}.
"""
    write("90_appendix_B_risk_library.md", txt)


# ------------------------------------------------------------------ C
OPS = {"lt": "<", "le": "<=", "gt": ">", "ge": ">=", "eq": "=", "ne": "!=", "in": "in"}


def cond(c):
    left = c["fact"]
    right = c["other_fact"] if "other_fact" in c else json.dumps(c.get("value"))
    right = right.replace("true", "yes").replace("false", "no") if isinstance(right, str) else right
    return f"{left} {OPS[c['op']]} {right}"


def rule_text(r):
    parts = []
    if r.get("all_of"):
        parts.append(" AND ".join(cond(c) for c in r["all_of"]))
    if r.get("any_of"):
        parts.append("any of: " + " OR ".join(cond(c) for c in r["any_of"]))
    return "; ".join(parts)


def appendix_c():
    rows = []
    for r in RULES:
        rows.append([r["id"], r["risk_id"], rule_text(r), r["level"], r.get("priority", 0), r["source"], ", ".join(r.get("evidence_ids", [])), r.get("confidence", "")])
    levels = collections.Counter(r["level"] for r in RULES)
    rat = [[r["id"], r["description"], r.get("rationale", "")] for r in RULES]
    txt = f"""# Appendix C. The {N_RULES} site-fact rules

The rule base (`data/rules_masonry.json`) turns site facts the engineer already knows (Yes / No / Unknown, or a number entered by the user) into a flag on a library risk. A rule is a logical condition on facts. It contains no probability, no delay and no numeric threshold other than comparisons between two entered facts or a Yes/No fact. All {N_RULES} rules carry Source = Assumption (a logical condition proposed by the team); the evidence IDs support that the risk exists, not the rule's size or trigger. Level "elevated" marks an observed shortfall; level "normal" marks the risk as relevant only. Where several rules fire on one risk the highest priority wins; equal priority with different levels is reported as a conflict (guard test G-8). A rule whose facts are missing is shown as "not evaluable", never guessed. For a risk placed from the literature seed, an "elevated" flag raises its probability class by one (cap 5); that step is an Assumption of the tool (register item AS-11, Appendix H). Rule levels: {levels['elevated']} elevated, {levels['normal']} normal.

**Table C.1.** The {N_RULES} rules: condition, flagged risk, level, priority and evidence. Source: `data/rules_masonry.json`. Conditions are rendered from the rule's `all_of` / `any_of` fields; "= yes" is a Boolean fact set to true.

{table(['Rule', 'Flags risk', 'Condition', 'Level', 'Priority', 'Source', 'Evidence IDs', 'Confidence'], rows)}

**Table C.2.** Description and rationale text of each rule as stored in the file. Source: `data/rules_masonry.json`.

{table(['Rule', 'Description', 'Rationale (as stored)'], rat)}
"""
    write("90_appendix_C_rules.md", txt)


# ------------------------------------------------------------------ D
ENDPOINT_PURPOSE = {
    ("GET", "/"): "Serves the single-page interface",
    ("GET", "/favicon.ico"): "Icon",
    ("GET", "/api/health"): "Liveness check; reports whether AI is offline and the number of curated evidence records",
    ("GET", "/api/meta"): "Version, counts and run settings for the interface",
    ("GET", "/api/template"): "Blank case JSON",
    ("GET", "/api/example"): "The ILLUSTRATIVE example case (placeholders, labelled Assumption)",
    ("GET", "/api/risk-library"): "The risk library (Appendix B) with seed placement",
    ("GET", "/api/rules"): "The site-fact rules (Appendix C)",
    ("GET", "/api/evidence"): "Evidence records (curated list, by ids, or search with ?q=)",
    ("GET", "/api/settings"): "Whether an AI key is configured (never returns the key)",
    ("POST", "/api/settings"): "Store the AI provider and key outside the project folder",
    ("POST", "/api/settings/test"): "One small real request to the provider to check the key",
    ("POST", "/api/validate"): "Check a case; always HTTP 200 with ok true/false and a problem list",
    ("POST", "/api/run"): "Run the register, rules and matrix on a case (HTTP 422 on problems)",
    ("POST", "/api/analyze"): "Optional decision layer: Monte Carlo schedule, delay cost / EMV, response comparison on user-entered numbers",
    ("POST", "/api/analysis-report"): "Markdown report of the optional decision layer",
    ("GET", "/api/mitigation-catalogue"): "Catalogue of candidate responses (text only, no effect sizes)",
    ("GET", "/api/example-analysis"): "ILLUSTRATIVE case with cost model, deadline and responses",
    ("POST", "/api/suggest-risks"): "Guarded AI suggestions: risk names, mechanisms and evidence IDs only",
    ("POST", "/api/report"): "register.md",
    ("POST", "/api/register-csv"): "register.csv",
    ("POST", "/api/matrix-svg"): "matrix.svg download",
    ("POST", "/api/report-html"): "report.html download",
}


def parse_routes():
    src = (ROOT / "gui" / "api.py").read_text(encoding="utf-8-sig").split("\n")
    routes = []
    for l in src:
        m = re.match(r'\s+@app\.(get|post)\("([^"]+)"\)', l)
        if m:
            routes.append((m.group(1).upper(), m.group(2)))
    return routes


def appendix_d():
    routes = parse_routes()
    missing = [r for r in routes if r not in ENDPOINT_PURPOSE]
    assert not missing, f"endpoints without description: {missing}"
    rows = [[m, p, ENDPOINT_PURPOSE[(m, p)]] for m, p in routes]
    n_api = sum(1 for _, p in routes if p.startswith("/api/"))
    txt = fill("D_schema_api.md", routes_table=table(["Method", "Path", "Purpose"], rows), n_routes=len(routes), n_api=n_api, **COMMON)
    write("90_appendix_D_schema_api.md", txt)


# ------------------------------------------------------------------ E
def appendix_e(run_pytest=True):
    log = LOGDIR / "pytest_log.txt"
    exe = None
    for cand in ("/root/.local/bin/pytest",):
        if os.path.exists(cand):
            exe = [cand]
    if exe is None:
        exe = [sys.executable, "-m", "pytest"]
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    if run_pytest:
        env = dict(os.environ)
        env["PYTHONPATH"] = f"{ROOT}:/usr/local/lib/python3.13/dist-packages"
        p = subprocess.run(exe + ["-v", "-rs", "-p", "no:cacheprovider", "--color=no"], cwd=ROOT, env=env, capture_output=True, text=True)
        log.write_text(p.stdout + p.stderr, encoding="utf-8")
    text = log.read_text(encoding="utf-8")
    res = collections.OrderedDict()
    for m in re.finditer(r"^(tests/\S+?\.py)::(.+?)\s+(PASSED|FAILED|SKIPPED|ERROR|XFAIL|XPASS)\b", text, re.M):
        f, _, st = m.groups()
        res.setdefault(f, collections.Counter())[st] += 1
    final = re.findall(r"=+ (.*?) in ([\d.]+)s.*=+\s*$", text, re.M)[-1]
    version = re.search(r"platform linux -- Python ([\d.]+), pytest-([\d.]+)", text)
    skips = re.findall(r"^SKIPPED \[(\d+)\] (\S+): (.*)$", text, re.M)
    rows = []
    totals = collections.Counter()
    for f, c in res.items():
        doc = ""
        try:
            tree = ast.parse((ROOT / f).read_text(encoding="utf-8-sig"))
            d = ast.get_docstring(tree) or ""
            doc = d.strip().split("\n")[0][:150]
        except Exception:
            pass
        n = sum(c.values())
        totals.update(c)
        rows.append([f.replace("tests/", ""), n, c["PASSED"], c["SKIPPED"], c["FAILED"] + c["ERROR"], doc])
    tot = sum(totals.values())
    mm = re.findall(r"(\d+) (passed|skipped|failed|error)", final[0])
    expect = {k: int(n) for n, k in mm}
    assert totals["PASSED"] == expect.get("passed", 0) and totals["SKIPPED"] == expect.get("skipped", 0), (dict(totals), expect)
    rows.append(["**Total**", f"**{tot}**", f"**{totals['PASSED']}**", f"**{totals['SKIPPED']}**", f"**{totals['FAILED'] + totals['ERROR']}**", ""])
    skip_rows = [[f, n, why] for n, f, why in skips]
    # relevance-guard test names
    guard = [m.group(1) for m in re.finditer(r"^tests/test_relevance_guard\.py::(.+?)\s+PASSED\b", text, re.M)]
    txt = fill(
        "E_test_log.md", stamp=stamp, py=version.group(1) if version else "n/a", pt=version.group(2) if version else "n/a",
        final_line=f"{final[0]} in {final[1]} s", tot=tot, passed=totals["PASSED"], skipped=totals["SKIPPED"], failed=totals["FAILED"] + totals["ERROR"],
        n_files=len(res), files_table=table(["Test file", "Tests", "Passed", "Skipped", "Failed", "Module docstring (first line)"], rows),
        skip_table=(table(["Reason location", "Count", "Reason"], skip_rows) if skip_rows else "No skip reasons were printed."),
        guard_list="\n".join(f"- `{g}`" for g in guard), n_guard=len(guard), **COMMON)
    write("90_appendix_E_test_log.md", txt)
    return dict(total=tot, passed=totals["PASSED"], skipped=totals["SKIPPED"], failed=totals["FAILED"] + totals["ERROR"], files=len(res))


# ------------------------------------------------------------------ F, G, J
SURVEY_ITEMS = [
    # (text from domain_expert.md section 4.1, nearest library risk)
    ("Bricks or blocks not on site when needed.", "R-MAT"),
    ("Sand or cement short, or mortar mixer not working.", "R-MORT"),
    ("Masons or helpers absent or fewer than planned on the day.", "R-LAB"),
    ("Skilled masons short, helpers doing mason work.", "R-SKILL"),
    ("Masons leave around festivals, harvest or elections.", "R-FEST"),
    ("Gang's weekly payment or labour contractor's bill paid late.", "R-GPAY"),
    ("Work front not released by the RCC/shuttering team (props, debris, slab not handed over).", "R-FRONT"),
    ("Hoist or material lift not available or broken.", "R-VT"),
    ("Scaffolding not available or not safe.", "R-SCAF"),
    ("Door/window frames, lintel casting or electrical/plumbing positions not ready when masonry reaches that level.", "R-OPEN"),
    ("Rain stopping external masonry.", "R-WX"),
    ("Extreme summer heat reducing working hours.", "R-HEAT"),
    ("Walls redone because of line, level, plumb, bond or opening errors.", "R-RWK"),
    ("Inspection or approval (consultant, QA) delayed before masonry can continue or be plastered.", "R-QLT"),
    ("Drawings for wall layout/openings not final or changed after start.", "R-DES"),
]


def appendix_f():
    ids = {r["id"] for r in LIB}
    assert len(SURVEY_ITEMS) == 15 and all(rid in ids for _, rid in SURVEY_ITEMS)
    items = [[i, t, rid, LIBNAME[rid]] for i, (t, rid) in enumerate(SURVEY_ITEMS, 1)]
    seeded = sum(1 for _, rid in SURVEY_ITEMS if SEEDTAB[rid].get("mean_rii") is not None)
    txt = fill("F_survey.md", items_table=table(["Item", "Wording shown to respondents", "Nearest library risk", "Library name"], items),
               n_items_seeded=seeded, n_items_unseeded=15 - seeded, **COMMON)
    write("90_appendix_F_survey_instrument.md", txt)


def appendix_g():
    write("90_appendix_G_second_coder.md", fill("G_second_coder.md", **COMMON))


def appendix_j():
    write("90_appendix_J_glossary.md", fill("J_glossary.md", **COMMON))


# ------------------------------------------------------------------ H
def read_json(rel):
    p = ROOT / rel
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def appendix_h():
    s2 = read_json("analysis/out/s2_summary.json")
    s3 = read_json("analysis/out/s3_summary.json")
    s1 = read_json("analysis/out/s1_summary.json")

    def var(label_start):
        if not s3:
            return None
        for k, v in s3["variants_pct_class_changed"].items():
            if k.startswith(label_start):
                return v
        return None

    def sens(txt_ok, txt_none="not tested (analysis output not available at generation time)"):
        return txt_ok if txt_ok else txt_none

    equal_count = var("3 equal-count")
    four = var("4 equal-count")
    eqw = var("5 equal-width")
    fixed = var("fixed RII cut-offs 0.2/")
    dr = var("direct + related")
    resc = var("scale-rescaled")
    pct = var("within-study percentile")
    p_alt = s2["level_changes_out_of_7_by_group"]["p_edge_alternative_set"] if s2 else None
    imp_alt = s2["level_changes_out_of_7_by_group"]["impact_edges_all_scale"] if s2 else None
    cut = s2["level_cutoff_triples_1_to_24"] if s2 else None
    pe = s1["oat_level_changes_out_of_7_by_input_and_factor"] if s1 else None
    imp_text = None
    csvp = ROOT / "analysis/out/s2_threshold_scenarios.csv"
    if csvp.exists():
        import csv
        sc = list(csv.DictReader(open(csvp, encoding="utf-8")))
        allsc = [x for x in sc if x["group"] == "impact_edges_all_scale"]
        alt = [x for x in sc if x["group"] == "impact_edge_alternative_set"]
        ic = [int(x["n_impact_class_changed"]) for x in allsc]
        lv = [int(x["n_level_changed"]) for x in allsc]
        altmax = max(alt, key=lambda x: int(x["n_level_changed"]))
        imp_text = (f"On the example, scaling all four impact edges by 0.5 to 2 changes the impact class of {min(ic)} to {max(ic)} of 7 risks but {'changes no level' if max(lv)==0 else 'changes the level of ' + str(min(lv)) + ' to ' + str(max(lv))}; "
                    f"the alternative edge set {altmax['impact_edges'].replace('/', ' / ')} changes {altmax['n_level_changed']} of 7 levels (analysis S2).")
    rows = [
        ["AS-01", "The seed's equal-count class (1 to 5) is used as BOTH the probability class and the impact class of a risk with no entered numbers.",
         "app/literature_seed.py; every literature-tier chip", "A survey importance index measures neither probability nor days; a placement needs some rule, and this is the simplest labelled one. It squares the rank (diagonal scores 1, 4, 9, 16, 25).",
         sens(f"Banding alternatives change {four}% (4 bands) to {fixed}% (fixed RII cut-offs) of the 30 seeded classes (analysis S3).") if s3 else sens(None)],
        ["AS-02", "Five equal-count bands of six risks each over the 30 seeded risks (class 5 = most important).", "app/literature_seed.py", "Avoids absolute RII cut-offs that put almost all risks in one band; equal counts are a display convention.",
         sens(f"3 equal-count bands change {equal_count}%, 5 equal-width bands {eqw}%, fixed cut-offs 0.2/0.4/0.6/0.8 {fixed}% of classes (analysis S3).") if s3 else sens(None)],
        ["AS-03", "Items of one study that map directly to a risk are averaged first; the per-study means are then averaged with equal study weight.", "app/literature_seed.py", "Counts each study once; ignores sample size and between-study heterogeneity.",
         sens(f"Dropping one seed study changes {min(var('drop seed study A14'), var('drop seed study A15'), var('drop seed study M06'), var('drop seed study M01'), var('drop seed study A02'))}% to {max(var('drop seed study A14'), var('drop seed study A15'), var('drop seed study M06'), var('drop seed study M01'), var('drop seed study A02'))}% of the classes of the risks that remain (analysis S3).") if s3 else sens(None)],
        ["AS-04", "Only 'direct' mappings of seed studies feed the seed; 'related' mappings and held-out studies are excluded (default basis 'seed').", "app/literature_seed.py", "Related rows are weaker matches; held-out studies are kept for the agreement check.",
         sens(f"Adding related mappings changes {dr}% of classes (analysis S3).") if s3 else sens(None)],
        ["AS-05", "Ties in mean RII are broken alphabetically by risk ID (R-MTH and R-STO tie at 0.7000).", "app/literature_seed.py", "A rank must be a total order for equal-count bands.", "Affects ranks of two risks only; not separately tested."],
        ["AS-06", "Raw RII values from 1-4 and 1-5 scales (and one pooled index) are averaged without rescaling.", "app/literature_seed.py", "Scale details are not recorded for every study; rescaling needs the scale of each.",
         sens(f"Rescaling (RII - 1/k)/(1 - 1/k) changes {resc}% of classes (analysis S3); within-study percentile rank changes {pct}%.") if s3 else sens(None)],
        ["AS-07", "Probability-class edges 0.2 / 0.4 / 0.6 / 0.8 (equal-width bins) for entered probabilities.", "app/engine/matrix.py DEFAULT_P_EDGES", "A conventional equal split of 0 to 1; not derived from data.",
         sens(f"On the ILLUSTRATIVE example, alternative edge sets change {p_alt['min']} to {p_alt['max']} of 7 levels (analysis S2).") if s2 else sens(None)],
        ["AS-08", "Impact is the expected delay if the risk occurs divided by the planned duration, binned by four user-entered edges (no default).", "app/engine/matrix.py", "Makes impact comparable across activities of different length. The edges are User Input with their own Source; the example's edges (0.02 / 0.05 / 0.10 / 0.20) are ILLUSTRATIVE.",
         sens(imp_text) if s2 else sens(None)],
        ["AS-09", "Score = probability class x impact class; level thresholds 5 / 10 / 15 give Low (up to 5), Moderate (6 to 10), High (11 to 15), Extreme (16 and above).", "app/engine/matrix.py matrix_level", "A common multiplicative convention; its known weaknesses are discussed in Chapter 7 (Cox, 2008).",
         sens(f"Over {cut['triples_tested']} alternative threshold triples the median number of the example's 7 levels that change is {cut['median_n_level_changed']:.0f} (IQR {cut['iqr'][0]:.0f} to {cut['iqr'][1]:.0f}) (analysis S2).") if s2 else sens(None)],
        ["AS-10", "The score is symmetric: probability class and impact class are interchangeable.", "app/engine/matrix.py", "Consequence of the product; not a statement about risk.", "Structural property of the rule (analysis S0/S1)."],
        ["AS-11", "A rule flag at level 'elevated' raises the probability class of a literature-tier risk by one, capped at 5.", "app/service.py; labelled Assumption in all exports", "Lets site facts move a seeded risk up the list; there is no source for the size of the step.", "Not tested; option of dropping the step is a supervisor decision (Audit Corrections, F02 / F18)."],
        ["AS-12", "The rule conditions themselves (for example stock days at or below lead time) are logical conditions proposed by the team.", "data/rules_masonry.json (all 22 rules carry Source = Assumption)", "Observed shortfalls are the conditions a site engineer can check; practitioner endorsement has not been collected.", "Not tested; planned in the expert survey (Chapter 8)."],
        ["AS-13", "A value exactly on an edge goes to the higher class; a relative tolerance of 1e-9 absorbs floating-point rounding (both axes).", "app/engine/matrix.py EDGE_REL_TOL", "Makes classification deterministic on decimal inputs such as 0.2.", "Verified by tests (Appendix E). The example risk R-WX (p = 0.20) sits exactly on the first edge, which drives many sensitivity counts."],
        ["AS-14", "Probability class 1 always gives level Low whatever the impact (1 x 5 = 5).", "app/engine/matrix.py", "Consequence of AS-09; the report lists impact-class-5 risks separately as a filter, not a score.", "Structural property of the rule."],
        ["AS-15", "Analysis design choices: sensitivity multipliers 0.5 to 1.5, 2,000 bootstrap resamples over 5 seed studies, permutation tests with 20,000 permutations, Holm correction, one fixed random seed (20261008).", "analysis/*.py", "Pre-specified so that no variant is chosen after seeing results; all variants are reported.", "Not applicable; these are analysis settings, not tool behaviour."],
        ["AS-16", "Example case inputs (probabilities, delay ranges, planned duration 16 days, site facts) are placeholders.", "examples, app/service.py example_case()", "A demonstration needs numbers; they are labelled ILLUSTRATIVE and are not evidence.", "Sensitivity of the example is reported in Chapter 6 (analysis S1/S2)."],
        ["AS-17", "Optional decision layer: 10,000 simulation runs and random seed 12345 by default; no default cost, effect size, probability or delay.", "app/analysis.py", "Run count and seed are tool defaults; every economic number must be entered with a Source.", "Decision stability under three seeds and cost-per-day sensitivity are produced by the tool itself."],
        ["AS-18", "For planning the proposed expert survey, the standard deviation of one Likert item is taken as 1 point.", "Appendix F", "M01's printed response counts give about 0.96 (methods review); used only to state the precision to expect.", "Planning figure only."],
    ]
    for r in rows:
        assert len(r) == 5
    txt = fill("H_assumptions.md", register_table=table(["ID", "Assumption", "Where used", "Why it was made", "Sensitivity or check"], rows), n_assump=len(rows), **COMMON)
    write("90_appendix_H_assumption_register.md", txt)


# ------------------------------------------------------------------ I
def appendix_i():
    from app import service
    case = service.example_case()
    res = service.run_case(case)
    m = res["matrix"]
    rows = []
    for r in m:
        rows.append([r["risk_id"], r["p"], r["p_class"], f"{r['expected_delay_if_occurs_days']:.2f}", r["impact_class"], r["score"], r["level"]])
    fired = res["rules"]["fired"] if isinstance(res.get("rules"), dict) and "fired" in res["rules"] else []
    fr = []
    for f in fired:
        fr.append([f.get("rule_id", f.get("id", "")), f.get("risk_id", ""), f.get("level", "")])
    summ = res["summary"]
    txt = fill("I_user_guide.md", example_matrix_table=table(["Risk", "p (as entered)", "p class", "Expected delay if it occurs (days)", "Impact class", "Score", "Level"], rows),
               fired_table=table(["Rule", "Flags risk", "Level"], fr) if fr else "(rule list not available)",
               planned=case["activity"]["planned_duration_days"]["value"], n_example_risks=len(case["risks"]),
               levels=", ".join(f"{v} {k}" for k, v in summ["levels"].items() if v), **COMMON)
    write("90_appendix_I_user_guide.md", txt)


if __name__ == "__main__":
    run_py = "--no-pytest" not in sys.argv
    appendix_a(); appendix_b(); appendix_c(); appendix_d()
    stats = appendix_e(run_py)
    appendix_f(); appendix_g(); appendix_h(); appendix_i(); appendix_j()
    print("pytest:", stats)
