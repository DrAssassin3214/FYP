# Appendix E. Software test log

The automated test suite was run for this appendix on 2026-10-08 13:10 UTC with `pytest -v` (Python 3.13.16, pytest 9.1.1) from the repository root, using `report/scripts/gen_appendices.py`. The raw output is saved as `report/scripts/out/pytest_log.txt`. Result line: **513 passed, 3 skipped in 30.21 s**. That is 516 tests in 17 files: 513 passed, 3 skipped, 0 failed or errored.

The tests verify software behaviour (that the code does what the documents say it does). They do not validate the tool against real sites and say nothing about the accuracy of any risk level (Chapter 6). The counts are a Derived Calculation from the log; the module docstring column is the first line of each test module's own docstring, where one exists.

Two further files, `tests/test_explain.py` and `tests/test_india_norms.py`, are excluded from collection by `tests/conftest.py` (they exercise legacy modules); they are not part of the counts below.

**Table E.1.** Test results by file. Source: `pytest -v` run of 2026-10-08 13:10 UTC; docstrings from the test modules.

| Test file | Tests | Passed | Skipped | Failed | Module docstring (first line) |
|---|---|---|---|---|---|
| test_ai_guard.py | 10 | 10 | 0 | 0 |  |
| test_analysis.py | 29 | 29 | 0 | 0 | Tests for the quantitative analysis flow (app/analysis.py), its service wrappers, report and HTTP routes. |
| test_corpus.py | 13 | 10 | 3 | 0 |  |
| test_engine.py | 32 | 32 | 0 | 0 |  |
| test_export_api_hardening.py | 129 | 129 | 0 | 0 | Regression tests for export / HTTP API / CLI / AI-guard hardening. |
| test_gui_api.py | 14 | 14 | 0 | 0 | Tests for the GUI's HTTP layer (gui/api.py) using Flask's built-in test client. |
| test_gui_settings_api.py | 12 | 12 | 0 | 0 | Tests for the /api/settings routes.  Isolated from the real machine: APPDATA/XDG_CONFIG_HOME are |
| test_gui_static.py | 3 | 3 | 0 | 0 | Static-content checks for the GUI front end (no browser needed). |
| test_legacy_hardening.py | 26 | 26 | 0 | 0 | Regression tests for the legacy quantitative modules (simulation, EMV, productivity, India norms). |
| test_options.py | 17 | 17 | 0 | 0 | Tests for option generation and the decision command (app/engine/options.py) and the memoised Beta quantile. |
| test_productivity.py | 13 | 13 | 0 | 0 |  |
| test_relevance_guard.py | 14 | 14 | 0 | 0 | Relevance / consistency guards G-1 .. G-10 (committee 2026-10-08). |
| test_report.py | 1 | 1 | 0 | 0 |  |
| test_rules.py | 5 | 5 | 0 | 0 |  |
| test_service.py | 42 | 42 | 0 | 0 |  |
| test_settings.py | 16 | 16 | 0 | 0 |  |
| test_validation_hardening.py | 140 | 140 | 0 | 0 | Regression tests for the validation hardening of app.service / app.engine (audit 2026-10-08). |
| **Total** | **516** | **513** | **3** | **0** |  |

**Table E.2.** Skipped tests and the reason printed by pytest. Source: `pytest -rs` section of the same run.

| Reason location | Count | Reason |
|---|---|---|
| tests/test_corpus.py:118 | 1 | bulk harvest not run yet |
| tests/test_corpus.py:128 | 1 | literature.db not built |
| tests/test_corpus.py:134 | 1 | literature.db not built (scripts/build_literature_db.py) |

## E.1 Relevance and consistency guards

`tests/test_relevance_guard.py` pins the counts and the wording rules used in this report. It reads the numbers from the data files and compares them with the documents, so a change to the library, the rules or the seed that is not reflected in the documents fails the suite. Its 14 tests in this run are listed below; the guard numbering G-1 to G-10 follows `docs/Project_Handoff_Summary.md` section 9.

- `test_g1_counts_are_consistent_with_each_other`
- `test_g2_current_docs_state_the_counts_in_the_data`
- `test_g3_seed_rows_are_frozen`
- `test_g4_withdrawn_wording_does_not_occur`
- `test_g4_handoff_only_mentions_withdrawn_wording_on_lines_that_say_so`
- `test_g5_every_exported_number_has_a_source[example_case]`
- `test_g5_every_exported_number_has_a_source[_full_library_case]`
- `test_g6_legacy_modules_are_not_imported_by_the_live_app`
- `test_g6_front_end_does_not_load_legacy_screens`
- `test_g7_the_example_stays_illustrative_everywhere`
- `test_g8_rule_base_sanity`
- `test_g9_unseeded_library_risks_are_labelled_and_have_no_seed_rows`
- `test_g9_new_risk_evidence_ids_exist_in_the_corpus`
- `test_g10_ai_path_cannot_carry_numbers`

## E.2 Known defects not covered by the suite

The engine audit of 2026-10-08 (`docs/Audit_Corrections_2026-10-08.md`, section 4) lists defects that were reported and, for the items marked FIXED in section 6 of that file, repaired and tested after the committee review. Items still marked "needs code change" there (for example H1, the CLI JSON writer accepting NaN; M1, booleans accepted as numbers; M2, M3, M5, M6, M8, M9 and L1 to L14 except those listed as fixed) are not guaranteed by this test log. Several of the test files named above (for example `test_validation_hardening.py`) were written after the audit and pin the repaired behaviour. This list is the one to re-check before any release of the tool.

## E.3 Update of 9 October 2026

The run above is that of 8 October. On 9 October, after the defect fixes of Section 6.7.4, the suite was run again with `python -m pytest tests -v` (Python 3.13, pytest 9.1.1) from the repository root. The result was **554 passed, 3 skipped in 44.9 s**: 557 tests in 19 files, 0 failed. The full log is `report/scripts/validation_2026-10-09/pytest_v_final.txt`. Two files are new since the table above: `test_analysis_charts.py` (9 tests, present at the repository head before the fixes) and `test_validation_fixes.py` (32 tests, one group per fix F1 to F6). The three skipped tests and their reasons are unchanged (Table E.2).

**Table E.3.** Test results by file, 9 October 2026. Source: `pytest -v` run after the fixes (Derived Calculation from the log).

| Test file | Tests | Passed | Skipped | Failed |
|---|---|---|---|---|
| test_ai_guard.py | 10 | 10 | 0 | 0 |
| test_analysis.py | 29 | 29 | 0 | 0 |
| test_analysis_charts.py | 9 | 9 | 0 | 0 |
| test_corpus.py | 13 | 10 | 3 | 0 |
| test_engine.py | 32 | 32 | 0 | 0 |
| test_export_api_hardening.py | 129 | 129 | 0 | 0 |
| test_gui_api.py | 14 | 14 | 0 | 0 |
| test_gui_settings_api.py | 12 | 12 | 0 | 0 |
| test_gui_static.py | 3 | 3 | 0 | 0 |
| test_legacy_hardening.py | 26 | 26 | 0 | 0 |
| test_options.py | 17 | 17 | 0 | 0 |
| test_productivity.py | 13 | 13 | 0 | 0 |
| test_relevance_guard.py | 14 | 14 | 0 | 0 |
| test_report.py | 1 | 1 | 0 | 0 |
| test_rules.py | 5 | 5 | 0 | 0 |
| test_service.py | 42 | 42 | 0 | 0 |
| test_settings.py | 16 | 16 | 0 | 0 |
| test_validation_fixes.py | 32 | 32 | 0 | 0 |
| test_validation_hardening.py | 140 | 140 | 0 | 0 |
| **Total** | **557** | **554** | **3** | **0** |

On 10 October 2026, after the manual-check export was added (`app/reporting/manual_check.py`, command `manual-check`, route `/api/manual-check-xlsx`), `python -m pytest tests -q` gave 561 passed and 3 skipped. The 7 added tests are in `tests/test_manual_check.py`. The totals in Table E.3 are those of 9 October and are not changed.
