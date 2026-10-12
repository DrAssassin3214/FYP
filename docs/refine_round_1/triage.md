# Round-1 triage (root, 2026-10-12, cloud session)

Every finding from `lead_A.md`, `A2_error_path.md`, `lead_B.md`, `lead_C.md`, `lead_D.md` is put in one of four bins.
**Do now** = fixed in this branch with a test or a command (P3). **Needs user** = a gate (delete/move files, seed values,
scope, publishing) or a design choice. **Local** = needs data that is not in the repository (`data/literature.db`, JSONL, PDFs,
API key); left for the local session. **Reject / not a defect** = reproduced and found fine, or too far-fetched for the code it costs.

Evidence depth: the cloud copy has no `literature.db`, so no corpus number is re-derived here. Items marked (V) were reproduced in
this session; the rest are worker findings that I read and accepted or deferred as stated. The status column is updated when P3/P4 finish
(see "Outcome" at the end).

## Lead A and A2 (engine, API, tests)

| ID | Bin | Note |
|---|---|---|
| A-01 | do now | bool / NaN edges / negative delay / score range in `matrix.py` |
| A-02 | do now | isolate the live-API test (and the order-dependent g6 check, via fresh subprocess with a clean environment) |
| A-03 | do now (testpaths) / needs user (backup copies) | the copies are not in this checkout; `testpaths = tests` is added anyway |
| A-04, A-05, A-07, A-08 | do now | test-quality fixes; no test weakened (assertions made stricter) |
| A-06 | do now | add boundary tests for matrix_level, probability_class edges, +1 cap |
| A-09 | reject | display rounding of a mean; rank/class unchanged; documented instead |
| A-10, A-11 | do now | unused imports / variables (flake8 F401, F841) |
| A-12, A-13 | needs user | dead-code removal is a gate |
| A-14 | do now (narrow) | silent `except: pass` gets a narrower exception where trivial |
| A-15 | local | scripts in Lead C's area with a hard-coded Windows path: made configurable by environment variable |
| A2-01..A2-10, A2-13, A2-14, A2-17, A2-18 | do now | input validation / CLI `analyze` error handling |
| A2-11, A2-12, A2-15, A2-16 | do now where cheap (warnings), else needs user | silently ignored input becomes a warning |
| A2-19, A2-20 | do now (19) / reject (20) | markdown cell pipes; 4,301-digit JSON is not a real input |
| NEW (found by root) | do now | "facts used" order depended on Python hash randomisation: output differed between processes (QUALITY_BAR 3). Fixed in `rules.py`; `scripts/golden_hash.py` added and is stable across `PYTHONHASHSEED` |

## Lead B (GUI)

| ID | Bin | Note |
|---|---|---|
| B-01, B-21, B-22 | do now | mobile layout: remove `min-width`, wrapping, grid minmax, matrix scroll |
| B-02, B-23, B-29 | do now | accessible names (aria-label) |
| B-03, B-06, B-40, B-43 | do now | wording fixes |
| B-04 | needs user | Tags default is a design choice made earlier by the owner |
| B-05, B-36 | needs user | scope: keep or hide step 5; the step number wording is fixed either way |
| B-07 | do now | inline prompt for duration / edges |
| B-08 | do now | removes a withdrawn sentence from the library data (data owner is Lead C; trivial text edit, not a seed value) |
| B-09 | do now | tag renamed |
| B-10 | do now | CSV: blank class/score for tier rows, round to 2 dp |
| B-12, B-45 | needs user | corpus-size figure (F08) |
| B-14 | do now | toast position |
| B-15 | do now | README_GUI step table brought in line with the navigation |
| B-16 | local | needs the settings of the owner's machine |
| B-17, B-18, B-19, B-20, B-24..B-28, B-30..B-35 | do now where small and testable by static test; rest listed under "not done" | |
| B-37..B-39, B-41, B-42, B-44, B-46..B-48 | do now (wording) / B-44 needs user (citation check needs the corpus) | |

## Lead C (data, scripts)

| ID | Bin | Note |
|---|---|---|
| C-01, C-04..C-06, C-13..C-19, C-21, C-26 | local / partly do now | scripts that cannot be run without the local database; only code-only guards are added |
| C-02, C-24, C-27..C-29 | local | need `literature.db` (P1 review of the 761 pending works, regeneration) |
| C-03 | done in the snapshot (scrubbed before upload); do now: confirm no e-mail or IP string is left | |
| C-07 | needs user | duplicate tree, not in this checkout |
| C-08, C-09 | do now | guard: empty quote, x100 allowance (with tests) |
| C-10, C-30 | do now | `docs/rii_statistics.json` regenerated from the seed (does not need the DB) |
| C-11, C-22, C-23, C-25 | needs user | evidence-list and workbook edits (F16, F29) |
| C-12, C-20 | do now (small) / local | |
| C-31 | do now | README header |

## Lead D (documents)

| ID | Bin | Note |
|---|---|---|
| D-01, D-02, D-03 | do now | test-count wording, pytest command |
| D-04, D-05, D-14, D-18 | do now (banner in the Markdown/HTML; Word files get a clearly marked superseded note) / needs user (regenerate vs retire) | |
| D-06, D-08, D-10, D-11, D-13, D-16, D-19, D-20 | do now | wording in README, Handoff, Audit_Corrections, Charter |
| D-07, D-09, D-21, D-23, D-26 | needs user | scope, corpus size, who the "committee" was, stray files, proposal |
| D-12 | do now | state which p the Holm values use |
| D-15, D-17 | do now | Word forms: listed for owner (binary edit risk), not edited blind |
| D-24 | local | needs recomputation from data |
| D-25 | do now | |

## Not a defect / rejected

* A-09 (display rounding), A2-20 (4,301-digit JSON), C-12 pinned versions (requirements pinning is an owner choice).
* The "Â±" in `Literature_Database_Report.md` is a Windows display artefact (Lead C's note).

## Outcome

Filled in at the end of P3/P4: see `docs/run_state.md` log and `docs/refine_round_1/outcome.md`.
