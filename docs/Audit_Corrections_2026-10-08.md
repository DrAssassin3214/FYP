# Audit corrections, 2026-10-08

Source of the findings: the research-methods audit (F01 to F30, with independent recomputation), the row-level check of the literature seed against the PDFs (M01, M06, A14, M10, M15, M14, A10, A21), and the engine audit. Scope of this file: what was and was not changed in **documents and data files**. Code, GUI, examples and tests were not touched by this work.

Status values: **FIXED in docs**, **FIXED in data**, **needs code change** (a `.py`, GUI, example or test file must change; nothing was changed there by this work), **decision for supervisor**, **not an error**. A row can carry two statuses.

Result of the row-level check: all 182 `rii` and `rank` values in `data/literature_seed.json` match the printed papers (no seed row is absent from the papers; no table row of M01, M06, A14-as-entered, M10 is missing). Only metadata and notes were wrong. After the edit the 182 rows are identical to the committed version (no `rii`, `rank`, `risk` or `mapping` value changed).

## 1. Files changed by this work

| File | Change |
|---|---|
| `data/literature_seed.json` | metadata and notes only (study fields `authors`, `venue`, `context`, `masonry`, `location`, appended `note`; `why_not_used` text of A11 and P1-23). Same keys, valid JSON, 182 rows unchanged. |
| `docs/Project_Handoff_Summary.md` | new section 8 (dated), superseded paragraphs marked "(superseded, see section 8)", withdrawn wording marked; no history deleted |
| `docs/Literature_Database_Report.md`, `docs/Corpus_Statistical_Analysis.md` | margin-of-error text, stale N and percentage, validation wording |
| `docs/case_schema.md` | incomplete risks are placed from the literature seed; rule flags and the +1 step; `use_literature_seed` and `seed_basis` documented |
| `README.md` | current scope; legacy Monte Carlo/EMV marked out of scope; run instructions kept |
| `docs/Audit_Corrections_2026-10-08.md` | this file |

Not changed, with reason: `docs/Project_Overview_Report.html` (the file does not exist in this checkout, so no banner could be added; the banner text to insert is "OUTDATED: describes the earlier, larger scope (Monte Carlo/EMV). See README.md for the current scope."), `gui/README_GUI.md` (owned by another agent), `data/risk_library_masonry.json` (not in the list of files to edit), `data/productivity_models.json`, `data/india_labour_norms.json`, `Literature_Evidence_Package.xlsx` (not text, not in scope).

## 2. Research-audit findings F01 to F30

| ID | Finding | Evidence | Status | What was changed |
|---|---|---|---|---|
| F01 | Agreement figures are circular (pooled rank vs seed 0.73; seed vs pooled z 0.40 / 0.53 include the seed studies) | Held-out-only: pooled rank vs seed rho 0.08 (n 22, p 0.73); z pooled vs seed rho 0.09 (n 22, p 0.70); M01+M06 alone 0.76 | FIXED in docs; needs code change | Handoff section 8.3 states the held-out-only values and withdraws the circular ones; marked in the old paragraph. The scripts `stats_rii.py` (s.7) and `stats_standardised.py` (vs_seed) still compute and print the circular versions. |
| F02 | Same band used for both axes squares the rank: 12 of 30 seeded risks Extreme, none High; R-TOOL Extreme vs R-INC Moderate on a 0.0008 gap | Run of matrix_level on seed_table | FIXED in docs (labelled Assumption); needs code change; decision for supervisor | Handoff 8.7, README, `case_schema.md` label it an Assumption. Not changed: UI/Source taxonomy, level colours for seeded cells (code), whether seeded cells keep level colours (supervisor). |
| F03 | Only 5 of A14's 39 factors entered; claim "built from every factor" untrue | Verification: 34 of 39 not in seed; top omitted: Q11 0.8233 rank 3, Q39 0.7902 rank 5, Q9 0.7890 rank 6, Q28 0.7485 rank 11; adding rows moves 14 of 35 classes | FIXED in docs and in data (claim withdrawn, subset stated); decision for supervisor | A14 note lists the omitted top factors and 26.4% road-project respondents; A10/A21/A15/A02 subset notes; handoff 8.10 withdraws "every factor". The 34 rows were NOT entered (new rows would change the seed; needs a decision and a re-run). |
| F04 | Stale 10-risk ranks and classes shown as current | Current seed: R-SKILL class 5, R-LAB rank 7 class 4, R-DES 10/4, R-WX 24/2 | FIXED in docs | Handoff 8.2 has the 30-risk table recomputed with `app.literature_seed.seed_table()`; the old table is marked superseded. |
| F05 | "Validation", "out-of-sample test", "predicts study X's order" over-claim; LOSO reported is robustness vs the full ranking | Cross-prediction M01 0.09 (p 0.76), A02 0.37 (p 0.29), M06 0.64 (p 0.061), A14 0.60 (n 4), A15 untestable; held-out Holm p 0.12 to 0.55 | FIXED in docs | Handoff 8.4, 8.5, 8.11; old paragraphs marked; wording withdrawn. Plan item in section 6 marked superseded. |
| F06 | RII surveys of M01 and A02 are general building-construction surveys; masonry only in the field case (M01: AAC blocks) | Full-text notes P23, A_masonry_india.md | FIXED in data; FIXED in docs | Seed: M01 and A02 `context`, `masonry` ("No (...)" instead of "Yes"), `note`. The `masonry` field is only displayed (workbook column "Masonry-specific?", DB column), not read by logic (grep of app/ and scripts/). Handoff key-studies line reworded. |
| F07 | README describes Monte Carlo, EMV, prediction and productivity models no longer in the product | README lines 3-7, layout row, run line | FIXED in docs; decision for supervisor | README rewritten to the current scope (identification, register, 5x5 matrix, labelled literature seed, exports); legacy code marked out of scope; all run instructions kept. The official title (and project description) still describe the old scope: decision whether to justify the cut or retitle. |
| F08 | Three corpus sizes: 21,902 / 5,214; 17,788 / 3,975; 11,599 / 3,550 | Handoff s.5 (`data/openalex_corpus.jsonl`); `Literature_Database_Report.md` (`data/literature.db`); `data/screening_report.json` (all rules 2026-10-07.1) | decision for supervisor | Not reconciled and no figure chosen. Listed with sources in handoff 8.9; a note added at the top of `Literature_Database_Report.md`. Needs a re-run of `corpus_statistics.py` against the database. |
| F09 | "R-WX lower than the rest" (p = 0.049) is post-hoc, item-level; R-WX is rank 24 of 30 | Study-level KW p 0.25; z interval includes 0 | FIXED in docs | Handoff 8.6, 8.11; marked WITHDRAWN in the old paragraphs. Script keys: see F21. |
| F10 | "Studies agree modestly" with Kendall W 0.40, p 0.16 (4 studies, 6 risks) | W = 0.400, chi2 8.0, df 5, p 0.156 | FIXED in docs | Handoff 8.5, 8.11 (wording: weak, not distinguishable from chance). |
| F11 | Multiple testing and p-value method switch: M15 p 0.039 (t) vs 0.045 (permutation); M14 10-risk p 0.09 vs 0.11 | Holm-adjusted 0.117 (M15), 0.485 (M10), 0.553 (M14) | FIXED in docs; needs code change | Handoff 8.5 gives Holm values and recommends permutation/exact p throughout; stats scripts and workbook not changed. |
| F12 | Inconsistent direct/related mapping decisions (e.g. M10 poor site management, M06 training, A02 age, M14 changing jobs) | Audit B13, judgement | decision for supervisor | No `mapping` or `risk` value was changed. A second-coder check with an agreement statistic (kappa) is recommended before changing any of them. |
| F13 | M01 prints only RII >= 0.700 (28 of 38): truncation bias | P23 | FIXED in data (stated in M01 note); decision for supervisor | Whether to exclude M01 for risks whose M01 items were cut is not decided. |
| F14 | Example case described as 5 risks; it has 7 | R-SAFE 0.30, R-SKILL 0.22 | FIXED in docs | Handoff 8.8 (and the old paragraph pointer). |
| F15 | Example case: impact bin edges have no Source label; delay ranges lack ILLUSTRATIVE note | `examples/example_case.json`, `app/service.py` `example_case()` | needs code change | Not done (examples/ and .py are not mine). Recorded in handoff 8.8. |
| F16 | Risk-library `existence_evidence` of the core 10 stale; R-LAB cites M15 skills item; R-WX cites cold-region R08 | libcheck | decision for supervisor | NOT changed: `data/risk_library_masonry.json` was not in the list of files to edit. Suggested: R-LAB cite A14 Q25 0.8245 and A02 absenteeism 0.751; R-WX cite A09 (Kolkata monsoon). |
| F17 | `case_schema.md` and `gui/README_GUI.md` say incomplete risks stay off the matrix and rules never produce probabilities | `app/service.py` lines 324-344 / 532-558 | FIXED in docs (`case_schema.md`); needs doc change by the owner of `gui/README_GUI.md` | `case_schema.md` updated. `gui/README_GUI.md` step 3 and 4 not touched (another agent). |
| F18 | Rule-flag +1 class is an unsourced Assumption, not labelled as one in the output | docstring and tooltip only | FIXED in docs; needs code change | Labelled Assumption in `case_schema.md` and handoff 8.7. Register/report output label not changed (code). |
| F19 | "FPC-corrected" margin not applied to whole-database and tier-1 figures; a census has no sampling error | 1.96 x 0.5 / sqrt(3975) = 0.0155; subgroup 0.0467 (FPC) | FIXED in docs; needs code change | `Literature_Database_Report.md` s.2 and `Corpus_Statistical_Analysis.md` s.7 corrected. The generator text in `scripts/corpus_statistics.py` (lines about 5, 34, 144-145) still produces the old sentence; a re-run overwrites the doc fix. |
| F20 | Corpus analysis s.6 text: "With N = 3,550", ML share "about 8%" vs table 10.4% | table in the same file | FIXED in docs; needs code change | `Corpus_Statistical_Analysis.md` now says N = 3,975 and 10.4%. The generator `scripts/stats_corpus.py` (lines 231-232) still has the old text. |
| F21 | `stats_rii.py` JSON keys `kruskal_all10`, `range_all10` hold 30-risk results | audit B10 | needs code change | Not done. |
| F22 | `literature_seed.py` docstring (basis "all") says it "removes the held-out validation studies" | docstring | FIXED in docs (`case_schema.md` states the correct meaning); needs code change | Docstring not edited. |
| F23 | UI selector says "6 studies held out for validation"; only 3 testable (A10, A21, HAS25 overlap with 2, 1, 1 risks as first stated; the A10/A21 overlap is larger, see V-A10/V-A21) | audit E | needs code change | Not done. |
| F24 | A11 "overlaps only about 2 of our 10 risks"; real reason for exclusion is the different index | A11 covers rework, skilled labour, design, climate | FIXED in docs; FIXED in data | Handoff 8.10 and old line marked superseded; `other_indices` A11 `why_not_used` appended. A11 values themselves were NOT verified (PDF not available). |
| F25 | "182 RII values ... every value with its table/page" | locations are per study; 4 rows unmapped/group-level | FIXED in docs | Reworded in handoff (178 factor values + 4 rows) and in `Literature_Database_Report.md`. |
| F26 | `stats_rii.py` NSAMP: A15 weight 90 = firms, not respondents | audit | FIXED in data (note); needs code change | A15 note says `n` counts firms. The script weight is not changed. |
| F27 | `productivity_models.json` M03: journal "to be confirmed"; F(1,39) with n = 40 | notes give Revista de la Construccion 19(1):30-41 | decision for supervisor | Not changed (file not in the list; legacy, out of scope). |
| F28 | `india_labour_norms.json`: FPS gloss and "class-75" likely wrong; bhisti/bhishti key mismatch; URLs NR | judgement, PDF not re-checked | decision for supervisor; needs code change | Not changed (legacy, out of scope). See also engine H3. |
| F29 | Citation inconsistencies: M15 authors, M10/M06 workbook stale, HAS25 placeholder title, A10 volume/pages, P1-23 year | audit D | FIXED in data (partly); decision for supervisor | M15 full author list, A10 volume/pages, M01 pages 55-70, HAS25 placeholder-title note, P1-23 overlap/year note. Not done: the stale rows in `Literature_Evidence_Package.xlsx` (M06 year NC, M10 first author, M15 authors NC); HAS25's real title still unknown. |
| F30 | "nine of the ten risks within 0.036" is a 10-risk statement | 30 risks: top 24 within 0.096, top 6 within 0.019; SE of one M01 RII about 0.03 | FIXED in docs | Handoff 8.2 and the old line marked superseded. |

## 3. Issues found by the row-level verification against the PDFs

| ID | Finding | Evidence | Status | What was changed |
|---|---|---|---|---|
| V-M15a | Author list incomplete (5 names plus "et al."; Aidar omitted) | Printed: six authors | FIXED in data | `authors` = Eduardo Lavocat Galvão de Almeida, Vitor Amadeu da Silva Feitoza, Michele Tereza Marques Carvalho, Ana Beatriz Souza Piña, Lissa Gomes Araújo & Luiz Augusto Gimenez Aidar. |
| V-M15b | DOI inconsistent inside the PDF | footers/header e5194; how-to-cite box on p.1 e5120 | FIXED in data (note); the DOI field keeps e5194 | note appended. Which DOI Crossref resolves was not checked (egress blocked). |
| V-M10 | Seed note wrong: Man. 20 and Tec. 5 are not Table 7 rows | They appear only in the text below the table, p.211 | FIXED in data | note appended; the original sentence is kept with the correction after it. Table 7: 33 rows printed, 33 in seed. |
| V-M10b | Paper lists Malaysia and Vietnam under "Middle East" | paper's own inconsistency | FIXED in data (note); not an error of the seed | note appended. |
| V-M14 | Printed RII = W/(5N) although the text states A = 4 (e.g. 305/(4 x 83) = 0.919, printed 0.735) | all 23 rows | FIXED in data (note); decision for supervisor | Values kept as printed. Not on the paper's own 1-4 basis; absolute level not comparable with other studies; ranks unaffected. Whether to recompute on W/(4N) for the agreement check is not decided. |
| V-M06 | n = 201 (abstract, Table 3) vs 206 in Section 3.1 text; scale not stated in the text | RII = total / (5 x 201) is consistent with max weight 5 | FIXED in data (note) | `n` and `scale` fields unchanged. |
| V-M01 | Row "Bad leadership skill": printed sum/RII 165 / 0.750 vs counts [1,5,5,27,6] giving 164 / 0.745 | PDF | FIXED in data (note); not a transcription error | Value kept as printed (0.750). |
| V-A10a | Location "RII table" is vague | Table 2 pp.766-767, Table 3 p.767, text p.767; weather 0.616 only in the text (Table 2 has 6 of 8 groups) | FIXED in data | `location` and `venue` (106(3): 763-771) updated. |
| V-A10b | Note "only 2 tool risks overlap" too pessimistic: about 10 tool risks overlap | Table 2 rows listed in the verification | FIXED in data (note) | Rows NOT entered; the file is a deliberate subset. The group row rank 1 is correct (Table 3). Ranks of site (2) and contractor (3) groups are printed in the paper but null in the seed; not changed (rank values are frozen). |
| V-A10c | Paper-internal oddities (text 0.602 and 0.544 attributed to wrong items; counts column unreliable) | verification | not an error of the seed | Printed RII values used. Not added to the note beyond the subset statement. |
| V-A21a | Location "Results section" vague; labour 0.733 vs 0.773 | Table 6 p.16; 0.773 only in the abstract | FIXED in data | `location` and note updated; the 0.733 value is kept. |
| V-A21b | More than the stated risks overlap (e.g. materials/procurement 0.719, planning 0.706, subcontractors 0.700, communication 0.712, weather 0.641, change orders 0.723) | Table 6 | FIXED in data (note) | Rows NOT entered; deliberate subset. Paper's Table 8 duplicates a row and gives 70.00% vs 70.56% in Table 6 (paper's own inconsistency, not recorded in the seed). |
| V-A14 | Context: 26.4% of respondents on road projects; 34 of 39 factors not entered | verification | FIXED in data (note) | see F03. |
| V-A15 | Full author list, volume/pages, scale not recorded; values are two-decimal summary figures | audit D | FIXED in data (note: recorded as unknown); decision for supervisor | Details not invented; need the paper. |
| V-HAS25 | Title field is a placeholder | seed title "(brickwork / housing skeleton tasks, Iraq)" | FIXED in data (note); decision for supervisor | Real title still needs reading from the paper; cannot be cited in APA as is. |
| V-A11 | A11 and P1-23 values not verified (PDFs not on disk) | verification | FIXED in data (notes say not re-checked / possible overlap with M01) | Nothing verified. |
| V-M01M06 | M01 28 of 28 and M06 40 of 40 table rows present; no seed row absent from its paper | verification | not an error | none |

## 4. Engine and QA findings (engine_audit.md)

None of these was fixed by this work (code is not mine). Items that touch documents or data are marked.

| ID | Finding | Status | Note |
|---|---|---|---|
| H1 | NaN / inf accepted by validation, giving wrong matrix classes; CLI writes invalid JSON | needs code change | |
| H2 | Delay distribution without a source silently labelled "Expert Judgment" (integrity rule 2) | needs code change | `case_schema.md` says every number needs a source; the code does not enforce it for delay |
| H3 | CPWD norms: second-class mason labour dropped, output doubled (legacy productivity) | needs code change; decision for supervisor | touches `india_labour_norms.json` (F28); legacy, out of scope |
| M1 | Booleans accepted as numbers | needs code change | |
| M2 | Out-of-range p not rejected when delay is missing; seed then used | needs code change | `case_schema.md` still says "a value that is present but wrong is rejected", which is only true when both numbers are present |
| M3 | Partly entered numbers discarded in output; seed used instead | needs code change | |
| M4 | Float rounding moves on-edge ratios into the lower impact class | needs code change | edge convention (lower-edge inclusive) is not documented; add to the report once decided |
| M5 | String/non-boolean facts evaluate False instead of "not evaluable" | needs code change | |
| M6 | Malformed shapes give tracebacks / HTTP 500 | needs code change | |
| M7 | AI text can carry probabilities/delays/costs; report says "No number here was produced by AI" (integrity rule 3) | needs code change | the sentence in the report is not accurate until fixed |
| M8 | Guard crashes on malformed item shapes | needs code change | |
| M9 | CLI accepts any number of impact edges; classes above 5 not drawn | needs code change | `case_schema.md` says four edges; enforced only in the GUI API |
| M10 | CSV export does not mark literature-seed rows | needs code change | |
| L1 to L14 (L1 planned-duration override of activity duration; L2 unknown-fact check can never fire; L3 contradictory "matrix not computed" warning while seeded cells are placed; L4 string `use_literature_seed` truthy; L5 uniform needs unused `m`; L6 ILLUSTRATIVE missing in register.csv; L7 Markdown/CSV escaping; L8 to L11 legacy simulation/EMV/predictor/explain defects; L12 BOM encoding in `model.py`; L13 thread-safety suspected) | needs code change | L4: the new `case_schema.md` row says `use_literature_seed` is true or false; the code now reports non-boolean values as a problem (service.py lines 453-458), which is not what the audit run saw, so recheck |

## 5. Items waiting for a decision or a code change (summary)

**needs code change:** F01 (scripts print circular figures), F02 (seeded-cell colours and labels), F11 (p-value method), F15 (example labels), F18 (output label for +1), F19 and F20 (generator text in `scripts/corpus_statistics.py`, `scripts/stats_corpus.py`), F21, F22, F23, F26, H1 to M10 and L1 to L14 above, `gui/README_GUI.md` (F17), `Project_Overview_Report.html` banner (file absent).

**decision for supervisor:** title versus scope (F07); corpus size (F08, three versions, none chosen); entering all 39 A14 rows and the omitted A10/A21 rows, then re-running the statistics (F03); second-coder check of mappings (F12); M01 truncation handling (F13); risk-library evidence updates (F16); M14 recompute on W/(4N) (V-M14); standardised pooled ranking versus the current seed (and the loss of the held-out check if the pooled ranking is adopted); HAS25 real title, A15 details (V-A15); legacy data files (F27, F28).
