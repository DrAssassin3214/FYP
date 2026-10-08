# Appendix E. Software test log

The automated test suite was run for this appendix on {{stamp}} with `pytest -v` (Python {{py}}, pytest {{pt}}) from the repository root, using `report/scripts/gen_appendices.py`. The raw output is saved as `report/scripts/out/pytest_log.txt`. Result line: **{{final_line}}**. That is {{tot}} tests in {{n_files}} files: {{passed}} passed, {{skipped}} skipped, {{failed}} failed or errored.

The tests verify software behaviour (that the code does what the documents say it does). They do not validate the tool against real sites and say nothing about the accuracy of any risk level (Chapter 6). The counts are a Derived Calculation from the log; the module docstring column is the first line of each test module's own docstring, where one exists.

Two further files, `tests/test_explain.py` and `tests/test_india_norms.py`, are excluded from collection by `tests/conftest.py` (they exercise legacy modules); they are not part of the counts below.

**Table E.1.** Test results by file. Source: `pytest -v` run of {{stamp}}; docstrings from the test modules.

{{files_table}}

**Table E.2.** Skipped tests and the reason printed by pytest. Source: `pytest -rs` section of the same run.

{{skip_table}}

## E.1 Relevance and consistency guards

`tests/test_relevance_guard.py` pins the counts and the wording rules used in this report. It reads the numbers from the data files and compares them with the documents, so a change to the library, the rules or the seed that is not reflected in the documents fails the suite. Its {{n_guard}} tests in this run are listed below; the guard numbering G-1 to G-10 follows `docs/Project_Handoff_Summary.md` section 9.

{{guard_list}}

## E.2 Known defects not covered by the suite

The engine audit of 2026-10-08 (`docs/Audit_Corrections_2026-10-08.md`, section 4) lists defects that were reported and, for the items marked FIXED in section 6 of that file, repaired and tested after the committee review. Items still marked "needs code change" there (for example H1, the CLI JSON writer accepting NaN; M1, booleans accepted as numbers; M2, M3, M5, M6, M8, M9 and L1 to L14 except those listed as fixed) are not guaranteed by this test log. Several of the test files named above (for example `test_validation_hardening.py`) were written after the audit and pin the repaired behaviour. This list is the one to re-check before any release of the tool.
