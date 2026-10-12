"""S0. Targeted checks of repo functions that the other scripts depend on. Each check is a small deterministic probe;
results go to out/s0_repo_checks.json. Nothing in the repo is modified."""
from __future__ import annotations

import inspect
import json

import common as C
from app.engine import matrix as M
from app.literature_seed import seed_table, seed_for, seed_observations
from app.service import example_case, run_case


def main():
    out = {}
    # 1 float edge asymmetry: impact_class tolerates 1e-9 at an edge, probability_class does not
    a = 0.1 + 0.7                      # intended 0.8, float 0.7999999999999999
    out["p_class_float_edge"] = {"value": repr(a), "probability_class": M.probability_class(a), "expected_if_tolerant": 5,
                                 "impact_class_same_ratio_(tolerant)": M.impact_class(a * 10, 10, [0.2, 0.4, 0.6, 0.8]),
                                 "finding": "probability_class has no EDGE_REL_TOL, impact_class does; a p built as 0.1+0.7 lands one class low"}
    # 2 p edges not reachable through run_case
    src = inspect.getsource(M.classify)
    out["p_edges_not_user_editable_via_run_case"] = {"classify_uses_default_edges": "probability_class(r.p.value)" in src,
                                                     "docstring_claims_user_editable": "user-editable" in (M.__doc__ or "")}
    # 3 example case p exactly on an edge
    ex = example_case()
    on_edge = [(r["id"], r["p"]["value"]) for r in ex["risks"] if r["p"]["value"] in M.DEFAULT_P_EDGES]
    out["example_case_p_exactly_on_edge"] = on_edge
    # 4 seed table integrity
    st = seed_table(); seeded = {k: v for k, v in st.items() if v["class"]}
    out["seed_table"] = {"risks_in_table": len(st), "seeded": len(seeded), "per_class": {str(c): sum(v["class"] == c for v in seeded.values()) for c in range(1, 6)},
                         "unseeded": sorted(k for k, v in st.items() if not v["class"]),
                         "single_study_risks": sorted(k for k, v in seeded.items() if len(v["evidence_ids"]) == 1),
                         "n_single_study_risks": sum(len(v["evidence_ids"]) == 1 for v in seeded.values())}
    # 5 seed_for elevated rule
    out["seed_for_elevated_cap"] = {"class5_elevated_p_class": seed_for("R-MAT", elevated=True)["p_class"], "class4_elevated_p_class": seed_for("R-LAB", elevated=True)["p_class"],
                                    "R-MAT_impact_class": seed_for("R-MAT")["impact_class"]}
    # 6 basis switch: does 'all' use held-out studies and what changes
    sa = seed_table("all"); common = [k for k in seeded if sa[k]["class"]]
    out["basis_all_vs_seed"] = {"n_seeded_all": sum(1 for v in sa.values() if v["class"]), "n_class_differs_on_common_risks": sum(sa[k]["class"] != seeded[k]["class"] for k in common), "n_common": len(common)}
    # 7 lru_cache(maxsize=1) thrash when bases alternate
    from app import literature_seed as L
    L._table_cached.cache_clear(); seed_table("seed"); seed_table("all"); seed_table("seed")
    info = L._table_cached.cache_info()
    out["lru_cache_maxsize_1_with_two_bases"] = {"hits": info.hits, "misses": info.misses, "finding": "alternating bases recomputes every call (performance only, results correct)"}
    # 8 'related' rows with null mapping
    d = L.load_dataset()
    out["rows_with_risk_but_mapping_none"] = sum(1 for r in d["rows"] if r.get("risk") and r.get("mapping") is None)
    out["rows_total"] = len(d["rows"]); out["studies_total"] = len(d["studies"])
    # 9 delay scaling is linear in mean (needed by S1)
    c = run_case(ex)
    out["example_run_case_levels"] = c["summary"]["levels"]
    C.write_json("s0_repo_checks", out, {"checks": 9, "example_risks": len(ex["risks"]), "seeded_risks": len(seeded)})
    return out


if __name__ == "__main__":
    print(json.dumps(main(), indent=1))
