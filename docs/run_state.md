# Run state (checkpoint for the automatic loop)

The loop reads this file at every wake-up, does the first unfinished step that the usage rules allow, then updates this file. Nothing depends on chat memory, so a pause (usage window, restart) loses nothing. Spec: `docs/Agent_Workflow.md`. Pass list: `docs/QUALITY_BAR.md`. Local run only, no git (user decision 2026-10-12).

## Usage-window rules (Pro plan: 5-hour window + weekly window)
Before starting any wave, call `get_usage`:
* 5-hour used **>= 90%**: start nothing. Schedule the next wake-up at the window reset time plus 3 minutes (wake-ups are capped at 1 hour each, so chain them with a cheap "still waiting" tick).
* **>= 70%**: only light work (scripts, my own reads, at most 2 agents).
* **< 55%**: heavy waves allowed (up to the 20-agent cap), then re-check usage before the next wave.
* Weekly used >= 85%: only light work until it resets.
* Every wave writes its output to a file before it ends; every step is resumable (idempotent scripts, "what is already done" check first).
* Ask an agent to save partial results early (write the file first, refine after).

## Standing rules
Agents: model `sonnet` or `haiku` only, set explicitly. Evidence integrity rules apply. Gates that stay with the user: deleting or moving files, editing `data/literature_seed.json` values, scope decisions, publishing/sending, git. Everything else runs automatically. Downloads: only the batch the user approved in principle (open-access PDFs from `data/fulltext_manifest.json`, top 40 by citations, one plain request each, no workaround of a refusal), logged to `docs/fulltext_download_log.md` before fetching.

## Steps (status: todo / doing / done)

| # | Step | Status | Notes |
|---|---|---|---|
| P0a | Round-1 audit: Lead B (GUI) | done | `docs/refine_round_1/lead_B.md`, 48 findings |
| P0b | Round-1 audit: Leads A, C, D | **done** (all four leads reported; A2 report saved separately) | A: 15 findings, 0 high, 3 med; A2 (error-path tests) never returned, so re-run it in P3. Root re-ran A-01: `probability_class(True)` = 5, negative delay gives impact class 1, `matrix_level(6,6)` = Extreme confirmed; NaN probability raises (the report said it is accepted: not reproduced). |
| P1 | Literature cycle 2: 761 pending works in `data/review_batches/cycle2/n00..n02.txt` -> 3 haiku reviewers + second reviewer (sonnet, 10%, `scripts/review_agreement.py --draw/--score`) -> append decisions to `data/review_decisions.tsv` -> `scripts/apply_review.py` -> regenerate statistics (`corpus_statistics.py`, `stats_corpus.py`, `stats_tool.py`, `build_stats_docx.py`, `build_ranking_workbook.py`) -> pytest | todo | cycle 1 harvest added 3,235 screened / 761 included. Stop growing when a cycle adds < 50 included works. |
| P2 | Triage round-1 findings (root): do now / needs user / reject; write `docs/refine_round_1/triage.md` | **done** | `triage.md` written 2026-10-12 (cloud) |
| P3 | Fix wave by owners (A engine/tests, B GUI, C data, D docs), each fix with a test or command; golden-hash check before/after engine changes | **done (remaining items listed in outcome.md)** | A done (commit b4cc2d8). B partly done: layout, rail names, skip link, wording (B-01/02/03/06/09/19/21/24/36-43), CSV (B-10). Still open: B-17/18/20/22/23/25-35/37/44-48, C-08/C-09 (guard), C-10/C-30 (regenerate rii_statistics.json), C-31 |
| P4 | Verification: pytest, compile check, numbers audit (Lead D), coverage matrix (Lead C) | **done for the cloud side** | 629 passed 3 skipped, flake8 clean, golden identical; numbers audit of corpus figures and coverage matrix need the local DB |
| P5 | Refresh stale documents and the handoff (section 10) with verified numbers | **partly done** | Markdown/HTML docs corrected; Word documents and corpus figures wait for owner / P1 |
| P6 | Full-text reading: top 40 by citations (log first, then fetch, then sonnet readers, then load into the evidence store) | todo | user said "in the end" |
| P7 | Final report to the user: what changed, numbers, list of open decisions; stop the loop | **written** | `docs/refine_round_1/outcome.md`; hourly routine keeps checking PR until 2026-10-13 16:00 UTC |

## Open decisions collected for the user (agents do not decide these)
See `docs/refine_round_1/lead_D.md` (section "Open decisions") and Lead B's list: step 5 "Cost, options & decision" in the navigation; Source tags on or off by default; deleting legacy screens/modules; which corpus size to quote; entering the omitted A14/A15/A02 factor rows; git tomorrow.

## Verified facts for later steps (checked by the root, 2026-10-12)
* Always run tests as `python -m pytest tests -q`: 556 passed in about 100 s. A bare `pytest -q` fails at collection (20 errors) because copies of the project sit in the root (`Bricks-ly_latest`, `Bricks-ly_latest_v3`); other new root folders: `analysis`, `loop_setup`, `output`, `report`, `scenarios`, `.github`. The root did not create them; do not move or delete them (gate). Earlier "133/137/140 tests" figures in docs are stale.
* Lead D (done, `lead_D.md`: 26 findings, 31 open decisions) says the handoff's "all 182 seed rows match the papers" is too strong: 161 rows (8 studies) were compared; A02, A15, HAS25 (21 rows) were not. Withdrawn wording remains in the older Word documents (Statistical_Analysis*, Worked_Calculations, Review_Preparation_Pack).

* Lead A (`lead_A.md`): a test in `tests/test_relevance_guard.py` (about lines 156-173) reached the live Gemini API and failed on a 503 (worker report, not re-run); add `testpaths = tests` for bare pytest; `simulation`, `emv`, `decision`, `options`, `explain` ARE imported by `app/analysis.py`, `options.py`, `report.py` (the "unused legacy" list was partly wrong; only `productivity/predictor.py` and `productivity/india_norms.py` have no non-test importer). Do not delete anything without the user.

* Lead C (`lead_C.md`: 31 findings, 4 high). Root actions already done: `build_literature_db.py` now refuses to run on a database that holds review decisions (it would erase them; `--force-rebuild` overrides); `apply_review.py` keeps the per-tier reviewed counts incrementally; `corpus_statistics.py` no longer crashes with works pending review; `harvest_supplement.py` no longer tells the user to run the rebuild. Still open from Lead C: ~190 stale figures in docs/workbooks until P1 finishes and everything is regenerated, `rii_study` metadata (M01/A02 masonry "Yes") and `docs/rii_statistics.json` missing the 8 later risks, user's e-mail address in `data/fulltext_manifest.json` and three scripts (scrub before sharing), guard/explain letting empty quotes and some invented numbers through (worker demos, not re-run).
* A2 error-path worker (late report) saved as `docs/refine_round_1/A2_error_path.md`: 20 findings (8 med): analysis path crashes for `simulation.n` < 10, CLI `analyze` has no error handling, wrong-type blocks, bare-string `evidence_ids`, non-finite numbers, overflow values. Not yet re-run by the root.
* `tests/test_relevance_guard.py::test_g6_legacy_modules_are_not_imported_by_the_live_app` passes alone but fails in a full run (order-dependent, confirmed by the root 2026-10-12): fix in P3 by checking in a fresh subprocess. A live-API test in the same file is also reported.
* Full test run now: `python -m pytest tests -q` (556 tests; about 100 s).

## Cloud session (2026-10-12 evening onwards)
Work now runs in a claude.ai cloud container (not the owner's PC). Branch `session/2026-10-12-literature-refinement-c2v60n`, PR #1 into `session/2026-10-12-literature-refinement` (never main). Test command: `python -m pytest tests -q` (baseline 553 passed, 3 skipped without local data; now 627+). Golden hashes: `python scripts/golden_hash.py` (stable across PYTHONHASHSEED). GUI check: `python -m gui --no-browser --port 8791` then `CHROMIUM_PATH=/opt/pw-browsers/chromium-1194/chrome-linux/chrome python scripts/gui_layout_check.py 8791`. Routine `trig_01C9ArEMbxVvkN8TRZu2kTzw` wakes this session every 2 h until 2026-10-13 16:00 UTC. P1 and P6 stay local (need data not in the repository). Commit author must stay the GitHub no-reply address.

## Git
Git 2.56 is installed (this shell needs its PATH refreshed from the registry). The project is now a local repository on branch `master`, first commit `f943e65` (363 files, author Omkar, local only, no remote; `Bricks-ly_latest*/`, `data/*.db`, `data/*.jsonl` and `Research_Papers/` are ignored). From now on a round ends with a commit of the changed files (message lists what changed); a branch per round and a pull request need a remote, which the user has not provided. The user's e-mail address is still inside `data/fulltext_manifest.json` and three scripts (MAILTO), so scrub it before any push to a shared remote. Moving the session to the cloud needs a pushed branch on github.com.

## Log
* 2026-10-12 ~18:05 UTC: 5-hour usage 89% (resets 20:30 UTC), weekly 13%. Round-1 audit complete (A, B, C, D, A2). PAUSED for new agent waves until the reset; wake-ups chain hourly with noop ticks, then at reset + 3 min the loop resumes with P1 (review the 761 pending works in `data/review_batches/cycle2/`, 3 haiku reviewers + sonnet second reviewer).
* 2026-10-12 17:56 UTC: usage 73% of the 5-hour window (resets 20:30 UTC), weekly 11%. Harvest cycle 1 done (1,923 + earlier new raw records; 3,235 screened; 761 included, pending review). Leads A, C, D told to save partials.
* 2026-10-12 ~18:50 UTC (cloud): P2 done; fix wave A (engine, analysis, CLI, tests; found and fixed a hash-order nondeterminism in rules.py) and part of wave B pushed, PR #1 open. Next: finish wave B, guard fixes, regenerate rii_statistics.json, P5 documents, P4 checks, P7 outcome.md.
* 2026-10-12 ~20:10 UTC (cloud): first scheduled wake-up worked. Accessibility batch (focus restore, tooltip names, th scope, live KPI) and boot-race fix done; P4 verification re-run (629 passed, 3 skipped); outcome.md written. Next wake-ups: check PR #1 for review comments, fix anything red; remaining GUI items are listed in outcome.md.
