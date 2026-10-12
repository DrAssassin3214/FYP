# Lead D findings, round 1 (audit only) - FINAL

Method: I ran pytest and counted library/rules myself; D1 (numbers), D2 (wording), D3 (stale docs), D4 (decisions) reports are merged. "V" = I reproduced it this round; "W" = worker finding, spot-check only; items not reproduced are marked UNVERIFIED. Nothing was edited except this file.

Important context: `data/literature.db` and `data/openalex_corpus.jsonl` were rewritten during the audit (12-10 23:26 by another process): 3,975 works at the start, 4,736 now (screening table 17,788 -> 21,023 rows; new works unreviewed). Every corpus figure below is correct only for the 3,975 snapshot; re-audit corpus figures after Lead C's rebuild settles.

## Findings

| ID | Sev | Location | What is wrong | Evidence | Proposed fix | Conf | User decision |
|---|---|---|---|---|---|---|---|
| D-01 | high | Handoff s.4 line 94 (README line 56 command) | Test count "133 passing / 137 passed, 3 skipped" stale | V: `python -m pytest tests -q` = 555 passed 1 failed (my run) and 556 passed 0 failed (D1 run); 556 collected | Write "556 collected, run `python -m pytest tests -q`, date it". report/ chapters 03/06/07/08/App.E and the report .docx say 513 passed, 3 skipped, 516 collected (W) | high | no |
| D-02 | high | `python -m pytest` / `pytest -q` from root; README line 56 | Bare pytest gives 20 collection errors: extracted copies `Bricks-ly_latest/` and `Bricks-ly_latest_v3/` (each with tests/) in the repo root | V: "import file mismatch ... Bricks-ly_latest_v3\tests\test_ai_guard.py"; no pytest.ini/testpaths | Add `testpaths = tests` (Lead A) or retire the folders; README should say `pytest tests` | high | yes (folder removal) |
| D-03 | med | tests/test_relevance_guard.py::test_g6 | Failed once in my full run, passed in D1's full run and alone (`-k g6`: 2 passed). Order- or timing-dependent (the corpus DB was being rewritten at that time) | V both outcomes; cause UNVERIFIED | Lead A to investigate | med | no |
| D-04 | high | Review_Preparation_Pack.docx (defence pack) | Says 38 risks, 11 rules, 5,214 records, 21,902 harvested, 45 curated PDFs in 5 folders, "Monte Carlo removed", "out-of-sample ranking check", "every cause of delay in 11 studies", "182 values each with table and page", M01/A02 "masonry" | W (D1+D2+D3); counts V: library 46, rules 22 | Regenerate first, before any defence | high | yes (scope wording) |
| D-05 | high | Statistical_Analysis.docx, Statistical_Analysis_Standardised.docx | Live withdrawn claims, no banner: "rain/monsoon rated lower (p 0.049)" listed as Supported; "rho 0.73" and "0.40/0.53" as support (circular); "modest" agreement (W 0.40 p 0.156); "Validation"; "predict a held-out study"; LOSO stable with no caveat; M01 "masonry site"; "38 library risks" | W (D2 exact paragraph/table locations in its report: Stat P8,P12,P22-24,T6R1-3; Std P18-P30,T5-T7) | Banner now "OUTDATED: 38-risk era, Handoff 8.11 withdrawals apply"; regenerate after library freeze | high | no |
| D-06 | high | Handoff line 136; Audit_Corrections line 7 | "All 182 rii/rank values match the printed papers" overstates depth: 161 rows / 8 studies were compared (agent-reported, text layer, figures not viewed); A02 (14), A15 (5), HAS25 (2) = 21 rows were not | V: Research_Notes/fulltext_review/README.md lines 12-22 say A02, A15, HAS25 rest on earlier notes; D1 confirms 161 | Reword to "161 of 182 rows (8 studies) matched; 21 rows not compared" | high | no |
| D-07 | high | README lines 3-5, 16, 22, 43-45; Handoff 8.14 vs s.9 vs s.6; Project_Charter items 3-4 | Scope stated inconsistently: lean only / decision layer (Monte Carlo/EMV) re-connected and run by README / "stay out of scope". Layout calls simulation/EMV "legacy, unused" while app/analysis.py uses them. Project_Overview_Report.html note says they are "no longer part of the app" | V (read) | One scope sentence after the user's decision, then fix README, Handoff s.9, Overview HTML | high | yes |
| D-08 | med | Handoff lines 23, 41, 44, 81, 8.2 closing note | Not marked superseded: 38 risks / 8 unseeded, 11 rules, category split. Correct: 46 risks (Labour 13, Material 6, Management 6, Design 4, Equipment 3, Financial 3, External 3, Safety 2, Weather 2, Quality 2, Site 2), 16 unseeded (8 old + R-FEST, R-FRONT, R-GPAY, R-HEAT, R-MORT, R-OPEN, R-SCAF, R-VT), 22 rules (18 elevated, 4 normal) | V counts 46/30/16/22; split from D1 | Tag superseded or update | high | no |
| D-09 | med | Handoff line 86, 98, 8.9, README; Review pack; root Literature_Database docx | Corpus size: 5,214 appears in no repo file (DB and jsonl: 3,975 at start, 4,736 now; screening_report.json 11,599/3,550 is a stale run; Literature_Database_Report 17,788/3,975 matched the DB at start). Both root Literature_Database docx still carry the pre-fix F19/F20 text ("N = 3,550", "about 8%" vs table 10.4%, FPC-less margin) | W (D1) | Pick one figure after rebuild; use corrected wording from Literature_Database_Report.md s.2 | high | yes |
| D-10 | med | Handoff line 99 | "45 hand-picked PDFs (Research_Papers/1-5)": 27 PDFs in folders 1, 2, 5, 6 | W (D1) | Correct | med | no |
| D-11 | med | Audit_Corrections lines 20, 102; Handoff line 129; Agent_Workflow line 57 | Say Project_Overview_Report.html is missing; it exists (docs/, 28-09-2026 22:37), old six-step Monte Carlo/EMV app, "130 passing", no OUTDATED banner, "6,194 PDFs" vs 6,237 elsewhere | V file exists and date; content W | Correct the three docs; insert the banner text from Audit s.1 | high | no |
| D-12 | med | Handoff 8.5 and Audit F11 | Holm values (0.117/0.485/0.553) come from t-approximation p; with the recommended permutation p (0.04465/0.24035/0.55305) Holm is about 0.134/0.481/0.553. Conclusion unchanged (none survives) | W, from docs/tool_statistics.json p_t, p_perm | State which p; fix numbers | med | no |
| D-13 | med | Review pack P44/T4R5; Worked_Calculations P48 | "one of three tests would not survive correction" / "your validation is not significant ... moderate agreement": none of three survives | W | "none survives Holm" | high | no |
| D-14 | med | Worked_Calculations.docx | "8. Validation" heading; "Steps 1 to 8 real published values" but steps 6,7,9 ILLUSTRATIVE; seeded cells shown as "Extreme" (contradicts tier labelling); RL-MAT uses retired material_buffer_days | W | Regenerate/banner | med | no |
| D-15 | med | Expert_Survey_Form.docx P13, T0R2, P21 | "same rating as published surveys so answers can be compared" (scales differ); delay-day anchors and sample-size targets without Source | W | "rank-order comparison only"; label Assumption | high | no |
| D-16 | med | Handoff line 118 | "tool is checked against published survey data and an expert survey": survey not administered | V (read) | "expert survey is planned" | high | no |
| D-17 | med | Research_Framework_Stages_5-16.docx P60 | "about 60-65% confidence ... 85%" unsourced, conflicts with own P31; "48 tests" stale | W | Delete or label Expert Judgment | high | no |
| D-18 | low | Tool_Statistical_Analysis.docx/.md l.16-21, 94, 102, 106 | Role "validation" still in generated output; LOSO 0.78 with no caveat; "where studies agree it is defensible" | W | Regenerate after script wording fix (F23 UNVERIFIED regenerated) | med | no |
| D-19 | low | Handoff 8.2 etc. | "Validation", "real-site validation is phase 2", "Monte Carlo prediction step" roadmap uses (judgement) | W | "site comparison (phase 2)" | med | no |
| D-20 | low | Project_Charter l.7 | "a verified risk library": single coder, kappa pending | W | Reword | med | no |
| D-21 | low | Handoff l.249, 260, 276; Audit l.114 | "committee review": human or agent reviewers UNVERIFIED | W | Say "agent review panel" if so | low | yes (what it was) |
| D-22 | low | Literature_Database_and_Statistical_Analysis_new.docx P1 vs P9-12 | Says precision "not yet measured" then describes the review; "every screened work read" at title+snippet depth | W | State model reviewers, snippet depth | high | no |
| D-23 | low | Review pack, root, report/ | report/Bricks-ly_Project_Report.docx/.pdf (129 pages) not audited; stray root files (2 zips, scenarios.zip, empty matrix.js/risks.js, gui_stdout.log, *_new.xlsx duplicates, test1_manual_calc_simulation.xlsx) | V listing | Separate audit of report/; retire list for user | high | yes |
| D-24 | low | Handoff 8.3/8.4/8.6, Audit F03 | Held-out-only rho 0.08/0.09/0.76, cross-prediction values, study-level KW p 0.25, "14 of 35 classes" | UNVERIFIED (no stored output; not re-derived) | Lead C to recompute | - | no |
| D-25 | low | Statistical_Analysis P17; case_schema.md l.15, 39 | A15 weight 90 = firms; missing full stop; defaults n 10,000/seed 12345 without Source | W | Minor fixes | med | no |
| D-26 | low | Research_Proposal.docx | 20+ uses of "predict/validate", unsourced "gap" claim | W | Do not edit approved proposal; add a note of scope narrowing | med | yes |

## Verified OK (D1, plus mine)
46 risks (30 seeded, 16 unseeded, 38 activity + 8 project scope); 22 rules; 182 rows, 11 studies (5 seed), 178 mapped + 4 unmapped (135 direct, 43 related); Handoff 8.2 table identical to seed_table() for all 30 rows; class split 12 Extreme / 6 Moderate / 12 Low / 0 High; rank 12 vs 13 gap 0.0008; 14 of 30 single-study; top-6 span 0.019, ranks 1-24 span 0.096; seed checksum guard passes; Tool_Statistical_Analysis, Literature_Database_Report and Corpus_Statistical_Analysis figures match their JSON/DB at the 3,975 snapshot; 129 report pages.

## Stale documents (D3, dates V from listing)
Regenerate first: Review_Preparation_Pack.docx. Banner now: Project_Overview_Report.html (28-09), Statistical_Analysis.docx, Statistical_Analysis_Standardised.docx, Worked_Calculations.docx, Tool_Statistical_Analysis.docx (38-risk era). Keep ten-risk by design but label: Expert_Survey_Form.docx, Site_Data_Collection_Form.docx (regenerate Site form before any site data). Historical banner: Research_Proposal.docx, Research_Framework_Stages_5-16.docx. Retire candidates (user): older Literature_Database_and_Statistical_Analysis.docx, zips, extracted folders. README: one-line fix for "legacy unused" wording. Project_Charter.md, case_schema.md: current.

## Open decisions for the user (D4, deduplicated)
1. Scope vs official title (retitle or justify the 2026-09-28 cut): registration decision.
2. Decision layer (Monte Carlo/EMV/costs) in or out of scope: docs contradict (D-07).
3. Legacy code deletion (simulation, EMV, decision, productivity, old screens/tests): deleting is a user gate; depends on 2.
4. Legacy data files (productivity_models.json, india_labour_norms.json, stale rows in Literature_Evidence_Package.xlsx).
5. Seeded-cell colours (option B) and dropping the unsourced +1 rule-flag step.
6. Corpus size figure and rebuild (D-09); Lead C is changing the DB now.
7. Entering omitted A14 (34 of 39), A10, A21, A15 rows: changes the seed.
8. Second-coder check of factor-to-risk mappings (kappa).
9. M01 truncation (only RII >= 0.700 printed).
10. M14 recompute on W/(4N).
11. Risk-library evidence updates (R-LAB, R-WX citations).
12. Merges/removals R-TRN, R-OVT/R-FAT, R-PRD (change seed bands).
13. Event/condition tag on library risks.
14. Site-language renames; R-SUP recategorisation.
15. Standardised pooled ranking vs current seed (loses held-out check).
16. Expert survey (length, respondents); 17. usability session; 18. site pilot or leave as phase 2.
19. Threshold sensitivity table scope.
20. Git/branch policy (not a repo; QUALITY_BAR item 8 cannot be met).
21. HAS25 real title; 22. A15 details and firms-vs-respondents weighting.
23. 357-paper download batch (names, sources, sizes first).
24. Deleting/moving stray root files, extracted copies, zips (D-02, D-23).
25. Retire vs regenerate stale documents (D-04, D-05, D-11).
26. Keep the "Find options online" feature (network use in an offline tool).
27. p-value standard (permutation/exact + Holm; D-12).
28. Supervisor name, team names, charter sign-off.
29. Wording of the note to the professor.
30. Identify the "mentor explanation document" (QUALITY_BAR item 10): none found.
31. Who/what the "committee review" was (D-21).
