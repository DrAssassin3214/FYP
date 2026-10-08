"""Markdown tables for Chapter 4 built only from analysis/out/*.csv|json (Derived Calculation). Output: report/scripts/out/t_*.md"""
import csv, json
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]; AO = REPO / "analysis" / "out"; OUT = REPO / "report" / "scripts" / "out"
def rd(n): return list(csv.DictReader((AO / n).open(encoding="utf-8")))
def js(n): return json.loads((AO / n).read_text(encoding="utf-8"))
def md(rows, header, align=None):
    a = align or ["---"] * len(header)
    return "| " + " | ".join(header) + " |\n|" + "|".join(a) + "|\n" + "".join("| " + " | ".join(str(x) for x in r) + " |\n" for r in rows)
def f(x, k=3):
    return "" if x in ("", None) else f"{float(x):.{k}f}"
def w(n, t): (OUT / n).write_text(t, encoding="utf-8")

# S3 band variants
v = rd("s3_band_variants.csv")
w("t_band_variants.md", md([[r["variant"], r["n_risks_in_variant"], r["n_class_changed"], f"{float(r['pct_class_changed']):.1f}", f(r["spearman_means"], 2), f(r["kendall_tau_classes"], 2), r["class_counts_1_to_5"],
                             r["risks_dropped"] or "-", r["risks_added"] or "-"] for r in v],
    ["Variant", "Risks", "Changed class", "% changed", "Spearman of mean RII vs base", "Kendall tau of classes", "Class counts (class:risks)", "Dropped", "Added"],
    ["---", "--:", "--:", "--:", "--:", "--:", "---", "---", "---"]))
# gaps
w("t_gaps.md", md([[r["boundary_between_ranks"], r["upper_risk"], r["lower_risk"], f(r["mean_rii_gap"], 5)] for r in rd("s3_band_boundary_gaps.csv")],
                  ["Band boundary (ranks)", "Upper risk", "Lower risk", "Gap in seed mean RII"], ["---", "---", "---", "--:"]))
# bootstrap per risk
w("t_boot.md", md([[r["base_rank"], r["risk_id"], r["base_class"], r["n_seed_studies_with_risk"], f(r["boot_present_share"], 2), f(r["p_same_class_as_base"], 2), f(r["p_top_tier_repo_class5"], 2),
                    f(r["p_top_tertile"], 2), f"{float(r['rank_p2.5']):.0f}-{float(r['rank_median']):.0f}-{float(r['rank_p97.5']):.0f}"] for r in rd("s3_bootstrap_tier_membership.csv")],
    ["Rank", "Risk", "Base class", "Seed studies", "Present", "P(same class)", "P(class 5)", "P(top 10)", "Rank in resamples (2.5%-median-97.5%)"],
    ["--:", "---", "--:", "--:", "--:", "--:", "--:", "--:", "---"]))
w("t_loso_rank.md", md([[r["dropped_seed_study"], r["n_common_risks"], f(r["spearman_rho"], 2), f(r["kendall_tau"], 2), r["n_repo_class_changed"]] for r in rd("s3_leave_one_study_out_rank_stability.csv")],
    ["Seed study dropped", "Risks still seeded", "Spearman vs full seed order", "Kendall tau", "Risks changing class (of 30)"], ["---", "--:", "--:", "--:", "--:"]))
# S1
w("t_base_example.md", md([[k, v_[0], v_[1], v_[2], v_[3]] for k, v_ in js("s1_summary.json")["base_matrix"].items()], ["Risk", "p class", "Impact class", "Score", "Level"], ["---", "--:", "--:", "--:", "---"]))
s1 = js("s1_summary.json")["oat_level_changes_out_of_7_by_input_and_factor"]
w("t_oat.md", md([[inp] + [s1[inp][k] for k in ("0.5", "0.8", "1.2", "1.5")] for inp in ("p", "delay", "p+delay")], ["Input changed", "x0.5", "x0.8", "x1.2", "x1.5"], ["---", "--:", "--:", "--:", "--:"]))
be = rd("s1_breakeven.csv")
def g(x): return x if x else "none in 0.30-2.00"
w("t_breakeven.md", md([[r["risk_id"], r["input"], g(r["up_class"]), g(r["down_class"]), g(r["up_level"]), g(r["down_level"])] for r in be],
    ["Risk", "Input", "Up: first multiplier changing class", "Down: first multiplier changing class", "Up: first multiplier changing level", "Down: first multiplier changing level"], ["---", "---", "--:", "--:", "--:", "--:"]))
j = rd("s1_joint_grid_summary.csv")
fps = ["0.5", "0.8", "1.0", "1.2", "1.5"]
d = {(r["factor_p"], r["factor_delay"]): r for r in j}
w("t_joint.md", md([[f"p x{fp}"] + [d[(fp, fd)]["n_level_changed"] for fd in fps] for fp in fps], ["Delay days ->", "x0.5", "x0.8", "x1.0", "x1.2", "x1.5"], ["---", "--:", "--:", "--:", "--:", "--:"]))
w("t_joint_random.md", md([[r["risk_id"], r["base_p"], r["base_level"], f(r["share_level_changed"], 3), f(r["share_level_up"], 3), f(r["share_level_down"], 3), f(r["share_p_class_changed"], 3), f(r["share_impact_class_changed"], 3)] for r in rd("s1_joint_random_by_risk.csv")],
    ["Risk", "Base p (Assumption)", "Base level", "Share of draws: level changed", "up", "down", "p class changed", "impact class changed"], ["---", "--:", "---", "--:", "--:", "--:", "--:", "--:"]))
# S2
s2 = js("s2_summary.json")
names = {"p_edge_single_shift": "One p edge shifted by -0.10, -0.05, +0.05 or +0.10", "p_edges_all_shift": "All four p edges shifted together by the same amounts",
         "p_edge_alternative_set": "Alternative p-edge sets (4)", "impact_edge_single_scale": "One impact edge scaled (x0.5 to x2)",
         "impact_edges_all_scale": "All four impact edges scaled (x0.5 to x2)", "impact_edge_alternative_set": "Alternative impact-edge sets (3)", "level_cutoff_alternative": "Alternative level cut-offs (7 named triples)"}
sc = rd("s2_threshold_scenarios.csv")
def impmax(grp):
    return max(int(r["n_impact_class_changed"]) for r in sc if r["group"] == grp)
def pmax(grp):
    return max(int(r["n_p_class_changed"]) for r in sc if r["group"] == grp)
rows = []
for grp, st in s2["level_changes_out_of_7_by_group"].items():
    rows.append([names[grp], st["scenarios"], f"{st['min']}-{st['median']:g}-{st['max']}", pmax(grp), impmax(grp)])
w("t_thresh_groups.md", md(rows, ["Scenario group (ILLUSTRATIVE example, 7 risks)", "Scenarios", "Levels changed: min-median-max (of 7)", "Max p classes changed", "Max impact classes changed"], ["---", "--:", "---", "--:", "--:"]))
sel = [r for r in sc if r["group"] in ("p_edge_alternative_set", "impact_edge_alternative_set", "level_cutoff_alternative", "p_edges_all_shift")]
w("t_thresh_selected.md", md([[r["scenario"], r["n_p_class_changed"], r["n_impact_class_changed"], r["n_level_changed"], r["risks_level_changed"] or "-"] for r in sel],
    ["Scenario", "p classes changed", "Impact classes changed", "Levels changed", "Risks whose level changed"], ["---", "--:", "--:", "--:", "---"]))
w("t_margins.md", md([[r["risk_id"], r["p"], r["nearest_p_edge_distance_abs"], r["delay_over_baseline"] and f(r["delay_over_baseline"], 4), f(r["nearest_impact_edge_distance_rel"], 4), r["p_class"], r["impact_class"], r["level"]] for r in rd("s2_edge_margins.csv")],
    ["Risk", "p (Assumption)", "Distance of p to nearest p edge", "Expected delay / planned duration", "Distance of ratio to nearest impact edge", "p class", "Impact class", "Level"], ["---", "--:", "--:", "--:", "--:", "--:", "--:", "---"]))
# S4
pw = [r for r in rd("s4_pairwise_spearman.csv") if int(r["n_shared_risks"]) >= 5]
w("t_pairs.md", md([[f"{r['study_a']} - {r['study_b']}", f"{r['role_a']} / {r['role_b']}", r["n_shared_risks"], f(r["spearman_rho"], 2), f(r["perm_p_two_sided"], 3), r["p_method"], f(r["holm_p"], 3)] for r in pw],
    ["Pair", "Roles", "n shared risks", "Spearman rho", "Two-sided p", "p method", "Holm p (13 tests)"], ["---", "---", "--:", "--:", "--:", "---", "--:"]))
w("t_cov.md", md([[r["study"], r["role"], r["n_risks_direct"], r["n_items_direct"], r["scale"]] for r in rd("s4_study_coverage.csv")], ["Study", "Role", "Risks with a direct item", "Direct items", "Scale"], ["---", "---", "--:", "--:", "---"]))
w("t_loso.md", md([[r["study"], r["role"], r["n_shared_risks"], f(r["spearman_rho"], 2), f(r["perm_p_two_sided"], 3) or "not tested", f(r["holm_p"], 3) or "-", r["circular_n_shared"], f(r["circular_spearman_x_inside_own_seed"], 2) or "-"] for r in rd("s4_leave_one_study_out.csv")],
    ["Study X", "Role", "n shared risks (X vs seed built from the other 4)", "Spearman rho", "Two-sided p", "Holm p", "n (circular)", "rho if X is inside its own seed (circular, shown only as a warning)"], ["---", "---", "--:", "--:", "--:", "--:", "--:", "--:"]))
kw = rd("s4_kendall_w.csv")
w("t_w.md", md([[r["studies"], r["n_risks"], f(r["kendall_W"], 3), f(r["perm_p_one_sided"], 3), f(r["holm_p"], 3)] for r in kw], ["Studies (m)", "Complete risks (n)", "Kendall W", "Permutation p", "Holm p (14 blocks)"], ["---", "--:", "--:", "--:", "--:"]))
# S5
sp = rd("s5_rii_spread_by_risk.csv")
rows = [[r["seed_rank"], r["risk_id"], r["n_seed_studies"], f(r["seed_mean_rii"], 4), f(r["seed_range_rii"], 4), r["n_studies_all"], f(r["min_rii"], 3), f(r["max_rii"], 3), f(r["range_rii"], 3)] for r in sp if r["seed_rank"] and int(r["n_seed_studies"]) >= 2]
w("t_spread.md", md(rows, ["Seed rank", "Risk", "Seed studies", "Seed mean RII", "Range of seed study means", "All studies reporting", "Min RII (all)", "Max RII (all)", "Range (all)"], ["--:", "---", "--:", "--:", "--:", "--:", "--:", "--:", "--:"]))
print("ok")
