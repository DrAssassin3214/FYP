# Appendix H. Assumption register

Every value or rule in the tool that is chosen by the project team without supporting data is an Assumption (Source label "Assumption") and is listed here, with where it is used, why it was made and which analysis, if any, shows how much the outputs depend on it. The register has {{n_assump}} entries. It is deliberately longer than a typical assumptions list because the integrity rule of the project is that no placeholder may look like evidence. Sensitivity figures are Derived Calculations from `analysis/out/` (scripts `analysis/s1` to `s5`, one fixed random seed, all variants reported); they describe how the scoring rule and the seed bands respond to their inputs, not how any real site behaves. Where the figure comes from the ILLUSTRATIVE example it is itself ILLUSTRATIVE.

The factor-to-risk mapping is not listed as an Assumption because it is Expert Judgment (single coder, kappa pending; Appendix G). The Source labels used in this report are Literature, Historical Data, User Input, Expert Judgment, Derived Calculation and Assumption.

**Table H.1.** Assumption register. Source: tool code and data files named in the "Where used" column; sensitivity: `analysis/out/s1_summary.json`, `s2_summary.json`, `s3_summary.json` (Derived Calculation).

{{register_table}}

## H.1 How to read the sensitivity column

The seed-band sensitivity shows that the class of a seeded risk depends on the banding rule and on which studies are included, which is why the tool shows seeded risks only as a labelled, uncounted literature tier. The example sensitivity shows that, in the example, the level responds to the probability class and to the thresholds far more than to the entered delay range, because the probability class caps the score. Neither result says that a real risk behaves in this way.

## H.2 Items that are decisions, not assumptions

Some open points are decisions for the supervisor rather than assumptions: whether to drop the "+1 class for a rule flag" step and to show seeded risks without any level colour (finding F02 / F18), whether to enter the omitted A14, A10 and A21 factors and re-run the statistics (F03), whether to treat the M01 truncated list differently (F13), which corpus count to report (F08), and whether the registered title or the scope is to be changed (F07). They are recorded in `docs/Audit_Corrections_2026-10-08.md`.
