# Agent workflow for refining the whole project

Shape (as described by the project owner): one agent at the top, four below it, and more workers below each of those.
It covers the **entire project, code and research together**, not one pipeline. Nested spawning was tested on 2026-10-12 and works.
Pass criteria for every round are `docs/QUALITY_BAR.md`.

```
                                 ROOT (the main chat)
                                          |
   +---------------------+----------------+----------------+---------------------+
   |                     |                                 |                     |
 LEAD A                LEAD B                            LEAD C                LEAD D
 Engine, API,          GUI and                           Research data,        Documents,
 tests, code           usability                         literature and        integrity and
 correctness                                             statistics            release readiness
   |                     |                                 |                     |
 workers               workers                           workers               workers
 (A1..A4)              (B1..B4)                          (C1..C6+)             (D1..D4)
```

## Who owns which files (one owner per file, so edits never collide)

| Lead | Owns | Does not touch |
|---|---|---|
| A. Engine, API, tests | `app/engine/`, `app/service.py`, `app/cli.py`, `app/analysis.py`, `app/reporting/`, `app/online_search.py`, `gui/api.py`, `tests/` | GUI static files, data files, docs |
| B. GUI and usability | `gui/static/` (js, css, html), `gui/README_GUI.md`, screenshots | Python under `app/`, data, docs other than the GUI README |
| C. Research data and statistics | `data/`, `scripts/`, `app/literature_seed.py`, `app/ai_layer/`, `Research_Papers/`, `Research_Notes/`, the statistics reports and workbooks | engine, GUI, general docs |
| D. Documents and integrity | `docs/` (except generated statistics reports), `README.md`, Word documents, handoff summary, `docs/Agent_Workflow.md` | code, data |

A lead that needs a change in another lead's file writes a request to the root; it does not edit the file.

## Roles

### Root (the main chat, one)
Owns the plan, the loop and every question to the user. Per round: brief the leads, read their one-page reports, spot-check a random sample of claims (a number against its file, a "fixed" item against the diff or test), triage findings into **do now / needs the user's decision / reject**, and decide continue or stop.

### Lead A: Engine, API, tests, code correctness
* A1 independent recomputation: re-derive the matrix classes, scores and seed placement by hand/script from the data and compare with the engine (uses the `independent-code-validation` approach).
* A2 error-path and input tests: NaN, bool, negative, missing source, empty register, wrong types through the service and the API; reports each defect with a failing example.
* A3 static and dead-code review: `flake8 --select=F,E9`, unused modules (legacy simulation, EMV, decision, productivity), what imports what. It only reports; deleting needs the user.
* A4 test-suite quality: weak or tautological tests, missing cases; adds tests, never weakens or deletes one.

### Lead B: GUI and usability
* B1 flow walk-through in the running app (case, rules, risks, matrix, evidence, report): every control, every empty state, every error message.
* B2 responsive and accessibility: 1280, 800 and 375 px, keyboard use, focus, contrast, console and network errors.
* B3 wording and labels: Source labels, ILLUSTRATIVE banner, "ordinal prioritisation only", no withdrawn wording ("validated", "predicts", "optimal"), plain language for a site engineer.
* B4 exports: report.html, register.csv/md, matrix png/svg are readable and match the screen.

### Lead C: Research data, literature and statistics
The existing literature pipeline, now one team among four:
* C1 harvest and screen QA, C2..C5 relevance reviewers (batches) plus a second reviewer on 10% for Cohen's kappa (`scripts/review_agreement.py`), C6 full-text readers (only after the user confirms a download batch), C7 seed-checker against the papers, C8 statistics and tool-statistics regeneration.
* Phase 1 (grow and review) stops when a cycle adds fewer than 50 new included works.

### Lead D: Documents, integrity and release readiness
* D1 numbers audit: every count, percentage and test number in `README.md`, the handoff summary and the reports is re-derived from a repo file or a command run this round (QUALITY_BAR item 4).
* D2 wording and evidence audit: withdrawn wording, unsourced numbers, depth labels that overstate what was read.
* D3 stale documents: `Project_Overview_Report.html` (present in `docs/`, dated 2026-09-28, describes the older six-step app), old Word documents that describe the ten-risk core or the earlier scope; reports what to regenerate.
* D4 supervisor list: collects every open decision (scope versus the official title, deleting legacy code, seeded-cell colours, A14 row entry, ...) into one list for the user. Agents do not decide these.

## Model policy (project owner, 2026-10-12): Sonnet and Haiku only, never Opus
Every Agent call sets `model` explicitly.

| Role | Model |
|---|---|
| Root, Leads A-D | sonnet |
| Batch relevance reviewers, harvest/screen QA, statistics and test runners, GUI walk-through readers (B1, B4), A3 static review | haiku |
| Second reviewer, PDF readers, A1 recomputation, A2 error-path, A4 tests, B3 wording, D1/D2 audits, C7 seed-checker | sonnet |

If a Haiku worker fails a spot-check (missing ids, wrong format, a figure that does not match its source), that unit is re-run on Sonnet and the failure rate is reported.

## Coverage rule (project owner, 2026-10-12): almost nothing may sit outside the tool

Every document, paper, data file and record in the project must either be **used by the tool's working process** (read by the app, the ranking, the evidence store, the AI layer, the statistics or an export) or be on a short **exclusion list with a stated reason**. The aim is that the exclusion list stays small.

* **Coverage matrix (Lead C builds it, Lead D checks it):** one row per source: the 5,214-record legacy corpus decisions, the 3,975 database works, the 27 full-text notes, `Research_Notes/*.md|json`, each of the 11 RII studies and every one of their factor rows, the workbooks, each data file. Columns: where it is read in code (file:line), what the tool does with it, status `used` / `used partly` / `not used`, and the reason for any `partly` or `not used`.
* **Known gaps to close or justify first** (from the audits and handoff): factor rows deliberately omitted from the seed (A14 has 5 of 39 entered, A15 5 of 32, A02 14 of 35; more of A10's and A21's items overlap with library risks than were entered); the 4 unmapped rows; the `related` mappings and the 6 held-out studies, which the default basis does not use; method papers P01-P12 that feed no number; research notes for dropped topics; records judged D by the reviewers (excluded on relevance, kept as screening rows).
* **How a gap is closed:** by adding the data to the tool (for seed rows: transcribed from the paper with its table/page and double-checked against the PDF), by making an optional basis that uses it (as `seed_basis = all` does), or by writing the reason it cannot be used. Entering new seed rows changes `data/literature_seed.json` values, so it needs the user's approval for the specific rows; agents prepare the rows and the check, they do not apply them.
* **Round check:** a round passes only if the exclusion list did not grow without a reason, and each lead reports how many sources in its area moved from `not used` to `used`.

## Rules that keep it safe

* **At most 20 agents at once** (leads and workers). Root 1 + 4 leads leaves 15 workers; split roughly A 3, B 3, C up to 6, D 3.
* **Round shape:** (1) audit, read-only, each lead writes `docs/refine_round_N/<lead>.md` with ranked findings, evidence (file:line, command output) and a confidence tag; (2) root triage; (3) fixes by the owning lead, with a test or a command that shows it; (4) verification round: Lead D re-derives numbers, Lead A runs the suite and flake8; (5) summary to the user.
* **Gates that need the user:** downloads (names, sources, sizes first, one plain request, no workaround of a refusal); deleting or moving any file; editing `data/literature_seed.json` values; scope decisions; publishing or sending anything; creating a git repository or branches. **Decision 2026-10-12: this run is local only; Git is updated tomorrow if needed.** Git is not installed here and the project is not a repository, so QUALITY_BAR item 8 (refine/round-N branch and pull request) is marked "deferred by the user" for this run, not failed; every round still writes its reports and changed-file lists so the work can be committed later in one step.
* **Evidence integrity:** no invented papers, numbers or site data; depth stated (title+snippet / abstract / full text, figures viewed or not); NR / NC instead of guessing; agent output is a claim until spot-checked.
* **No test weakened, deleted or skipped to pass.** Golden-hash check of engine output (QUALITY_BAR item 3) before and after any engine change.
* **Idempotent and resumable;** a lead starts by checking what exists. Deterministic work (harvest, screening, builds, statistics) stays in scripts.
