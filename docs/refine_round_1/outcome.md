# Round 1 outcome (cloud session, 2026-10-12): report for the owner's review

Branch `session/2026-10-12-literature-refinement-c2v60n`, pull request #1 into `session/2026-10-12-literature-refinement`. Nothing touched `main` or any other branch; no force-push. Commit author is the GitHub no-reply address; a search of the tree finds no personal e-mail address (scripts read `OPENALEX_MAILTO` from the environment).

## Numbers (all run in the cloud copy on the final commit)
| Check | Result |
|---|---|
| `python -m pytest tests -q` | **629 passed, 3 skipped** (632 collected) on the round-1 commit; after the 2026-10-13 clean-up 600 passed, 3 skipped (603 collected). Baseline before my changes: 553 passed, 3 skipped, 556 collected. The 3 skips need git-ignored local data. Your local count of 556 plus 76 new tests = 632 |
| `flake8 --select=F,E9 app gui tests` | clean except one unused import in `tests/test_india_norms.py` (a file `conftest.py` excludes from collection) |
| Golden hashes (`python scripts/golden_hash.py`) | identical before and after all engine changes; identical for `PYTHONHASHSEED` 1, 2, 3 |
| GUI layout (`scripts/gui_layout_check.py`, Chromium) | 7 screens x 1280/800/375 px: no horizontal scroll, no unnamed rail links, no console errors. Before: 509 px of scroll at 375 px, 8 unnamed rail links at 800 px |
| `compileall` | ok |

## What changed, by finding (see `triage.md` for every ID)
* **A / A2 (engine, API, CLI):** A-01, A-02, A-04, A-06, A-08, A-10, A-11, A2-01 to A2-14, A2-16 to A2-18 fixed with tests in `tests/test_round1_hardening.py`. New finding by the root: the order of "facts used" depended on Python hash randomisation (a `set`), so output differed between processes; fixed in `app/engine/rules.py` (an ordered tuple). The PR description wrongly blames a `field()` default; the cause was the set.
* **B (GUI):** B-01, B-02, B-03, B-06, B-08, B-09, B-10, B-07, B-17, B-19 to B-21, B-22 (scroll), B-23, B-24, B-25, B-26, B-27, B-28, B-29, B-30, B-32, B-33, B-36 to B-43 (wording) done. A boot race (hash change before the case loaded) found and fixed on the way.
* **C:** C-08 (empty / uncited quote in guard G3), C-09 (number check no longer accepts a bare number scaled by 100), C-10 and C-30 (`docs/rii_statistics.json` and `rii_standardised_statistics.json` regenerated from the seed: 46 risks instead of 38, other values unchanged), build script `sys` NameError (found by flake8). C-31 not done (file in `Research_Notes/` not edited).
* **D:** README, Handoff (new section 10), Audit_Corrections, Agent_Workflow corrected for: test counts, "161 of 182 rows compared", PDF count, expert-survey sentence, legacy-module wording, Overview HTML now has an OUTDATED banner.

## Not done, and why
* **Needs local data (left for the local session):** P1 (review of the 761 pending works, then regenerate every corpus figure: C-27, C-28, C-29), P6 (full-text reading), C-01/C-02/C-04/C-05/C-13 to C-19 scripts that need the database, B-16 (AI badge model name).
* **Open GUI items:** B-18 (confirm dialog replaces the Settings dialog), B-31, B-34, B-35, B-37, B-44 to B-48, B-14 (toast position). Not verified in a screen reader or by a keyboard-only walk-through; I verified with Chromium only.
* **Word documents** (`Review_Preparation_Pack`, `Statistical_Analysis*`, `Worked_Calculations`, `Expert_Survey_Form`, `Research_*`, both root `Literature_Database*` files) still carry withdrawn wording. Not edited blind; regenerate or banner them (`lead_D.md` D-04, D-05, D-14, D-15, D-17).
* **A2-15, A2-19:** not fixed (exports of not-evaluable rules; escaped pipes in the Markdown preview).

## Decisions only you can make (gates)
The full list is `lead_D.md` "Open decisions" (31 items). The ones that block the most work: scope versus the official title and whether the decision layer (Monte Carlo/EMV) stays (D-07, B-05); which corpus size to quote (D-09); deleting legacy code and stray root copies (A-12, A-13, D-23); Tags default on or off (B-04); entering the omitted A14/A15/A02 rows; regenerate or retire the old Word documents.

## Confidence
[Certain] test, flake8, golden-hash and layout results above (commands in `docs/run_state.md`). [Likely] the GUI accessibility fixes are right but were checked by DOM/layout probes, not by assistive technology. [Guessing] none in this report.
