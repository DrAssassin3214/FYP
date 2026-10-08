# Appendix G. Second-coder protocol for the factor-to-risk mapping

> **PROPOSED, NOT YET CARRIED OUT.** Every mapping of a survey factor to a library risk in Appendix A was made by one coder (Source: Expert Judgment). No second coder has been used, no agreement statistic exists, and the audit of 2026-10-08 found mapping decisions that are not consistent (finding F12; examples: M10 "poor site management", M06 "training", A02 "age", M14 "changing jobs"). No `mapping` or `risk` value has been changed since. This appendix is the protocol that the methods review proposed; it is to be executed before any mapping is altered and before the statistics are re-run.

## G.1 What is coded

The {{n_factor_rows}} factor rows of `data/literature_seed.json` ({{n_direct}} direct, {{n_related}} related; the {{n_unmapped}} unmapped rows are group-level or have no matching library risk). The current rows use {{n_mapped_risks}} of the {{n_risks}} library risks; the 8 risks added on 2026-10-08 have no rows yet. Any rows entered later (for example the 34 omitted A14 factors, or the omitted A10 and A21 items) are coded by the same procedure before entry.

## G.2 Procedure

1. **Freeze the coding manual first.** For each of the {{n_risks}} risks: name, scope, a one-sentence definition, two inclusion and two exclusion examples; the decision rule for "direct" (the factor is the same thing as the risk), "related" (the factor is a cause, consequence or part of the risk) and "none"; a rule for factors that are outcomes (for example "low productivity") and for factors that fit two risks.
2. **Choose coder 2.** A person who did not build the mapping: a team member who did not code, or a faculty member with masonry experience.
3. **Blind the sheet.** Export only the factor wording and the study context (country, building type) in random order. Hide coder 1's codes, the RII and the rank columns, so the coding cannot be driven by values.
4. **Calibrate.** Both coders code 15 to 20 rows from a study that is not in the agreement sample, discuss differences, amend the manual once, and freeze it again.
5. **Code all rows independently.**
6. **Compute agreement.** (a) Risk assignment: Cohen's kappa over {{n_risks}} risks plus "none" (a total of {{n_cats}} categories), with percent agreement and a bootstrap 95% interval over rows (Cohen, 1960). (b) Strength (direct / related / none): linearly weighted kappa. (c) The subset that actually feeds the seed (seed studies, direct rows): kappa and percent agreement on their own. Report the prevalence of each category, because kappa depends on it. Landis and Koch (1977) descriptors may be used as labels only.
7. **Apply the pre-committed rule.** If kappa is below 0.60 the manual is revised and a fresh sample is recoded; otherwise disagreements are resolved by discussion and every change is logged (row, old code, new code, reason, date).
8. **Re-run once.** The seed table and the statistics of Chapter 4 are recomputed once on the reconciled mapping, and the original and reconciled results are reported side by side. The choice of mapping is not to be made by which result looks better.

## G.3 Output files (proposed layout)

| File | Content |
|---|---|
| `coding_manual_v1.md` | The frozen manual (step 1), with a version and date. |
| `coder2_sheet.csv` | Blinded sheet: row id, factor wording, study context. |
| `coder_codes.csv` | Row id, coder 1 risk, coder 1 strength, coder 2 risk, coder 2 strength, reconciled risk, reconciled strength. |
| `change_log.csv` | Row id, old, new, reason, date, who. |
| `kappa_report.md` | Statistics of step 6 with n, prevalence and intervals. |

## G.4 What the result can and cannot show

A high kappa would show that a second person applying the same manual reaches the same codes; it would not show that the mapping is correct, because both coders share the manual. A low kappa would show that the manual, not only the coder, is ambiguous. Neither result changes the fact that the surveys are general building-construction surveys and not masonry-specific (Chapter 7).
