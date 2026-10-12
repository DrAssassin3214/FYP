# Round 1 plan (lead's merge of the four workstream reports)

Baseline: 610 passed, 3 skipped (25 test files) at start of round; branch refine/round-1.

## Phase A (code and data; workers do not commit, the lead commits)
- A1 numeric guard (app/engine/emv.py, simulation.py, app/analysis.py; new tests/test_numeric_guard.py): cap on delay/cost/LD magnitude, finite-output check; plus unknown-evidence-id WARNING parity between run_analysis and run_case (warning only, not an error).
- A2 rule source strictness and Optional narrowing (app/service.py; new tests/test_rule_source.py).
- A3 types (app/reporting/report.py, app/engine/options.py, app/engine/rules.py line ~108, app/ai_layer/evidence.py line ~104); output byte-identical.
- A4 test lint (8 test files).
- A5 /api/validate parity with /api/analyze simulation limits (gui/api.py; new tests/test_gui_validate_n.py).
- A6 import guards for scripts/build_rii_workbook.py and scripts/stats_rii.py.

## Phase B (docs and report; run after Phase A so numbers come from the final test run)
- B1 README.md + docs/Project_Handoff_Summary.md; B2 gui/README_GUI.md; B3 .gitignore + update_and_run.bat guard.
- B4 report 05_system_design.md; B5 06_verification.md + 03_methodology.md (+ template); B6 Appendix E + generator + template; B7 Appendices D and I; B8 07, 08, 00_front.

## Needs human decision (not touched by agents)
- Report title (registered vs working vs stated).
- Canonical corpus figure (21,902/5,214 vs 17,788/3,975 vs 11,599/3,550).
- Rule `source` label: all 22 rules say Assumption but 7 rationales say Expert Judgment; docs disagree.
- Evidence ids used by risks/rules but missing from the evidence workbook (8 ids), RL-HEAT P2-06 vs P2-08.
- Whether unknown evidence ids should be an error instead of a warning.
- Author initials, incomplete references (Hassoon, Manoharan, ISO 31000 / IEC 31010 editions).
- Whether the online data pack is in thesis scope (changes the 'fully offline' claim) and who hosts it.
- Normalising CRLF/LF in data files (changes pack hashes).
