# Project audit and clean-up, 2026-10-13 (cloud session)

Purpose: read the whole project, record its shortcomings, remove code that nothing uses, and close the routes by which an
outlier or inconsistent data file could make the tool print a wrong number. Every figure below was produced by a command
run in this session on branch `session/2026-10-12-literature-refinement-c2v60n` (pull request #1). Corpus figures are not
re-derived: the local database is not in the repository.

## 1. What was read
`app/` (64 files), `gui/` (48), `scripts/` (38), `tests/` (70), `data/` (13), `docs/` (28), `analysis/`, `examples/`,
`Research_Notes/` (40), `loop_setup/`, root files. Tools: `vulture`, `flake8 --select=F,E9`, import-graph greps, a new
data-consistency script, the full test suite, a Chromium layout check.

## 2. Removed (all unused by the live app; reverted by `git revert` of the clean-up commit)
| Item | Evidence it was dead |
|---|---|
| `gui/static/js/screens/{cost,decision,mitigation,productivity,simulation,explain}.js` | imported by nothing except each other; test G-6 already asserts the front end does not load them |
| `app/productivity/` (predictor, india_norms, model) | imported only by tests; no GUI, CLI or service route |
| `tests/test_productivity.py`, `tests/test_india_norms.py`, 3 tests in `test_legacy_hardening.py` | tested only the removed package (`test_india_norms.py` could not even be imported) |
| `app/ai_layer/explain.py: build_explain_prompt, explain_with_llm` | unused LLM-narrative path; an open channel for invented numbers with no caller |
| `scenarios/` (duplicate of `examples/scenarios/`) | `diff -r` shows identical |
| `output/` (generated demo output), `matrix.js`, `risks.js` (0 bytes) | generated or empty |
| `conftest.py` exclusion of two test files | `test_explain.py` repaired and now runs |

Kept on purpose (scope decision still open, `lead_D.md` D-07): the Monte Carlo / EMV / decision modules and
`app/reporting/report.py`, which the optional Cost, options & decision screen, `app/analysis.py`, the demo and 30+ tests use.
Kept: `data/productivity_models.json` and `data/india_labour_norms.json` (read as evidence records by the AI layer),
`gui/screenshots/` (4.3 MB, some show removed screens; yours to delete), `report/`, Word documents, `analysis/`, `loop_setup/`.

## 3. Outlier and variation controls added
* Numbers: plain ASCII decimals only; NaN, infinity, booleans and anything above 1e12 rejected with the field name.
* Matrix: out-of-range probability, negative delay, unsorted or NaN class edges now raise instead of giving a class.
* Unit slips: a delay maximum above 5x the planned duration produces a warning (computed, not blocked).
* Determinism: output no longer changes between Python processes (set ordering fixed); `scripts/golden_hash.py`.
* Data: `scripts/check_data.py` (and `tests/test_data_integrity.py`) checks 46 risks, 22 rules, 182 seed rows in 11 studies,
  13 catalogue entries and 472 evidence ids: no duplicate or dangling ids, no RII outside (0, 1], no rank that contradicts the
  RII order inside a study. Result on this commit: OK.
* AI layer: empty or uncited quotes are flagged (G3); a bare number scaled by 100 no longer passes the number check.
* No edit to any value in `data/literature_seed.json`.

## 4. Shortcomings that remain (ranked)
1. **No site comparison yet (high).** Everything the tool outputs is ordinal and rests on literature rankings and entered
   assumptions. The planned test against real project data (MSP or Primavera schedule of one site) has not started.
2. Scope is stated inconsistently across README, Handoff and Charter (D-07); the official title describes the earlier scope.
3. Corpus figures in the reports (3,975 / 4,736 / 5,214 works) disagree; 761 works await review; needs the local database.
4. Seed covers 30 of 46 risks; 14 of those 30 rest on a single study; ranks 12 and 13 differ by 0.0008 RII.
5. Old Word documents still contain withdrawn wording (validated, predicts, weather "rated lower").
6. Expert survey not administered; mapping of survey factors to risks has one coder only.
7. Accessibility checked with Chromium only, not with a screen reader; a few low-priority GUI items open (`outcome.md`).
8. `gui/screenshots/` and `report/` contain images of removed screens.
