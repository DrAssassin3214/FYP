# Analysis scripts and outputs (all outputs are "Derived Calculation")

Reproducible sensitivity and rank-agreement calculations for the brickwork risk-register tool. Nothing here edits the repo;
scripts only read `app.service.run_case`, `app.engine.matrix`, `app.literature_seed` and `data/literature_seed.json`.

## Rerun

    cd /home/claude/fyp
    PYTHONPATH=/usr/local/lib/python3.13/dist-packages python analysis/run_all.py

Needs numpy, scipy, matplotlib (no statsmodels; Holm is implemented in `common.py` and self-tested on import).
Runtime about 27 s (S4 permutation tests dominate). One fixed seed (`common.SEED = 20261008`, `numpy.random.default_rng`) is
used for every random draw. `run_all.py` clears `out/`, reruns everything, asserts every CSV/JSON carries the label and an `n`
column, and writes `out/manifest.json` (sha256 of each file). Two runs with different `PYTHONHASHSEED` gave an identical manifest.
`out/run_timing.json` holds wall-clock times and is excluded from the manifest.

Labelling: every CSV has a first column `label = Derived Calculation` and an `n` column (plus `n_boot`/`n_draws` where relevant);
every JSON has `label` and `n`; every PNG states the label, n and seed in its title and footer.

## Scripts

| Script | What it does | Main outputs in `out/` |
|---|---|---|
| `common.py` | Helpers: labelled writers, seed re-implementation helpers, hand-written Holm, Kendall/Spearman wrappers | - |
| `s0_repo_function_checks.py` | Small probes of repo functions (float edges, which edges are user-editable, seed table integrity, basis switch, cache) | `s0_repo_checks.json` |
| `s1_example_sensitivity.py` | ILLUSTRATIVE example case (`python -m app.cli example`): p and delay days (a, m, b) scaled by x0.5, 0.8, 1.2, 1.5, one risk at a time (p, delay, both), jointly on a 5x5 grid, and 5000 random joint draws (each input x U(0.5,1.5)); break-even multipliers. Uses `run_case`; a faster path using the matrix functions is asserted equal to `run_case` on all 84 one-at-a-time runs and 100 random draws | `s1_oat_example.csv`, `s1_joint_grid_*.csv`, `s1_joint_random_by_risk.csv`, `s1_breakeven.csv`, `s1_summary.json`, `s1_oat_scores.png`, `s1_joint.png` |
| `s2_threshold_sensitivity.py` | Same case: each of the four probability edges shifted, all four shifted, alternative edge sets; impact edges scaled singly/jointly; level cut-offs (extra); 5000 random edge jitters; margin of each risk to its nearest edge. Baseline and all impact-edge variants are asserted equal to `run_case` | `s2_threshold_scenarios.csv`, `s2_threshold_random_jitter*.csv`, `s2_edge_margins.csv`, `s2_summary.json`, `s2_threshold_*.png` |
| `s3_seed_band_sensitivity.py` | Re-implements the RII-to-class rule (asserted identical to `seed_table()` for all 30 seeded risks), then: alternative bands (tertiles, 4 bands, equal-width, fixed RII cut-offs), data variants (direct+related, scale rescaling, percentile rank, drop-one seed study), a 2000-resample bootstrap over the 5 seed studies (rank stability by Kendall tau and Spearman, class and top-tier membership frequency), exact leave-one-study-out, gaps at band boundaries | `s3_band_variants.csv`, `s3_bootstrap_tier_membership.csv`, `s3_bootstrap_rank_stability.csv`, `s3_leave_one_study_out_rank_stability.csv`, `s3_band_boundary_gaps.csv`, `s3_summary.json`, `s3_*.png` |
| `s4_interstudy_agreement.py` | 11 studies. (a) pairwise Spearman on shared risks with n for every pair, permutation p (exact for n <= 8, else 20000 permutations), Holm over pairs with n >= 5; (b) each study against a seed built from the OTHER seed studies only, with the circular comparison shown beside it; (c) Kendall W (tie-corrected) on every complete study x risk block with >= 3 studies and >= 5 risks, permutation p, Holm | `s4_pairwise_spearman.csv`, `s4_leave_one_study_out.csv`, `s4_kendall_w.csv`, `s4_study_coverage.csv`, `s4_summary.json`, `s4_*.png` |
| `s5_rii_uncertainty.py` | Per-risk spread of RII across the studies reporting it (min, max, range, SD, scale-free percentile-rank range) and its comparison with the RII gaps between adjacent seed ranks | `s5_rii_spread_by_risk.csv`, `s5_spread_vs_band_gaps.csv`, `s5_summary.json`, `s5_rii_spread.png` |

Unit for all literature work: one value per (study, risk) = mean of that study's items mapped `direct` to the risk (the repo's own
averaging). The dataset's non-seed studies are called "held-out" in outputs.

## Interpretation limits (read before quoting any number)

* RII is a survey importance index. It is not a probability and not a number of days; nothing here converts it into either. The
  classes from the seed are ranking bands that the repo applies to both matrix axes; S3 only tests how stable those bands are.
* S1 and S2 use the ILLUSTRATIVE example, whose inputs are placeholders (Assumption). They show how the ordinal classification
  reacts to changes in inputs and thresholds, not how any real site behaves. One case, 7 risks: counts are small and not a sample.
* The matrix is per-risk and independent: changing one risk never changes another risk's class (checked, S1 summary).
* The example risk R-WX has p = 0.20, exactly on the first probability edge (lower-edge-inclusive, class 2); any downward shift of
  that edge or p flips it. This drives many S1/S2 counts.
* S3 bootstrap resamples only 5 seed studies, of which 14 of 30 seeded risks are backed by a single study. Resamples that omit a
  study drop its risks, so class shares are conditional on the risk being present. Studies differ in scale (1-4, 1-5, pooled, unrecorded),
  sample and country; M01 is a truncated list (RII >= 0.70 only), A14/A15 contribute 4 items each. Tied means are broken by risk id.
* S4 agreement is rank agreement between importance indices on overlapping risks only. Overlaps are small (13 of 55 pairs have
  n >= 5; most have n <= 2), so power is low: a non-significant result is not evidence of disagreement or of agreement. Studies are
  not independent (M10 pools 10 surveys; related contexts). Kendall W blocks overlap, so their Holm-adjusted p-values are descriptive.
  The leave-one-study-out comparison removes the study from its seed, which is the point; the circular column shows how much
  including it would inflate agreement.
* S5 spread is between-study spread on unequal scales, not the sampling error of any survey.
* Holm families are separate (pairs / leave-one-study-out / W blocks); permutation p-values for n > 8 carry Monte-Carlo error of roughly +-0.003.
