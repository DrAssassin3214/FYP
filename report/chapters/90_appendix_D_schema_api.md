# Appendix D. Case file schema and interface endpoints

## D.1 Case JSON schema, summary

A case is one JSON object that describes one masonry activity. `python -m app.cli template` prints a blank case and `python -m app.cli example` prints the ILLUSTRATIVE one. Every numeric input that is not a plain count is an object `{"value": ..., "source": ..., "evidence_ids": [...], "note": "..."}`. The `source` must be one of `Literature`, `Historical Data`, `User Input`, `Expert Judgment`, `Derived Calculation` or `Assumption`; a number without a source is rejected. Time is in working days. The full definition is `docs/case_schema.md`; this appendix summarises it.

**Table D.1.** Top-level blocks of the case file. Source: `docs/case_schema.md` (summarised).

| Block | Fields | Notes |
|---|---|---|
| `project` | name, location, construction_type, notes | Descriptive text. |
| `activity` | id, name, `planned_duration_days` {value, source} | The planned duration is the denominator of the impact fraction for risks with entered numbers and an input to rule RL-MAT2. Risks placed from the literature seed do not need it. |
| `facts` | free key / value pairs | Inputs to the rules, for example `required_workers`, `available_workers`, `material_stock_days`, `material_lead_time_days`, `scaffolding_ready`, `monsoon_overlap`. Every fact used by the 22 rules is listed in `data/rules_masonry.json`. A missing fact makes a rule "not evaluable". |
| `rules` | optional list | Default is `data/rules_masonry.json`. A rule flags a library risk as relevant or elevated; a flag never produces a probability or a delay for a risk with entered numbers. |
| `risks` | id, name, category, description, status, `p` {value, source, note}, `delay` {kind, a, m, b, lam, source, note}, evidence_ids; optional text fields `owner`, `trigger`, `response_type` (avoid, reduce, transfer, accept), `response_action`, `review_date` (YYYY-MM-DD) | `p` is the probability that the risk occurs at least once during the activity. `delay` is the extra delay in days if it occurs, as PERT, triangular, uniform or fixed. A risk with p or delay missing stays in the register; if the literature seed has a value for it, it is placed at a labelled literature tier, otherwise it is left off the matrix with a note. The register text fields carry no numbers. |
| `use_literature_seed`, `seed_basis` | optional | `use_literature_seed` is true by default. `seed_basis` is `seed` by default (the 5 seed studies, direct mappings); `all` also uses held-out studies and related mappings, so the held-out agreement check no longer applies to it. |
| `impact_bin_edges_fraction` | four ascending fractions of the planned duration | User input, no default. A value exactly on an edge goes to the higher class (relative tolerance 1e-9, both axes). |
| `impact_bin_edges_source` | optional {source, note} | Source of the four edges. If missing, a warning is issued and the exports print "Source: not given". |

Results returned by `run_case` (Appendix I shows an example) are: `project`, `activity`, `risks` (one row per register entry with a completeness flag and any rule flag), `matrix` (probability class, impact class, score, level and expected delay if it occurs, for every placed risk; literature-tier rows carry `basis: literature-seed` and no expected delay), `summary` (counts and level totals; literature-tier rows are not counted in the level totals), `rules` (fired, not evaluable, flags), `matrix_settings` (impact edges with Source; probability edges and level thresholds, both Assumption), `high_consequence` (entered-number risks in impact class 5; a filter, not a score), `warnings` and `report_markdown`. The command line writes `register.md`, `register.csv` and `result.json`. The register CSV appends `delay_note`, `expected_delay_source`, `tier`, `owner`, `trigger`, `response_type`, `response_action` and `review_date`; its `level` column is empty for literature-tier rows.

**Table D.2.** Optional analysis blocks of the decision layer (`app/analysis.py`, `python -m app.cli analyze`). Every number is a `{"value", "source"}` object and nothing has a default value except the simulation settings. Source: `docs/case_schema.md` (summarised).

| Block | Content |
|---|---|
| `activity.deadline_days` | Optional deadline, needed for liquidated damages and the probability of exceeding the deadline. |
| `risks[].direct_cost_if_occurs` | Optional money lost if the risk occurs, on top of the cost of its delay days. |
| `cost` | `cost_per_delay_day` (required), `ld_per_day_after_deadline` (optional), `currency` (default INR). |
| `mitigations[]` | id, risk_id, action, strategy, `cost` (required), `p_after` and / or `delay_after` (entered, with a source, normally Expert Judgment), secondary risks, feasibility. A response with no modelled effect is reported and left out. |
| `options[]`, `constraints` | Optional option sets (blank = generated: each response alone, combinations that target different risks, and Accept); optional maximum probability of exceeding the deadline and maximum budget. |
| `simulation` | `n` (default 10,000, at most 200,000), `seed` (default 12345), `criterion`, correlations. |

The command is one of `AUTHORIZE MITIGATION`, `ACCEPT RISK`, `NO ADMISSIBLE OPTION` or `NO RESPONSE EVALUATED`. It is worded as "preferred under the stated criterion among the options evaluated", never as optimal, and it is not produced from literature-tier placements.

## D.2 Interface endpoints

The local interface (`python -m gui`) is a Flask application that serves a single page on `127.0.0.1` only. `gui/api.py` registers 23 routes, 21 of them under `/api/`. The table below is parsed from the source file by `report/scripts/gen_appendices.py`; the purposes are summarised from `gui/README_GUI.md` and `docs/case_schema.md`. The interface computes nothing itself: every figure on screen comes from `app.service.run_case` (or `run_analysis`), which runs on every edit.

**Table D.3.** Routes registered in `gui/api.py`. Source: `gui/api.py` (route paths); purposes summarised from the repository documents.

| Method | Path | Purpose |
|---|---|---|
| GET | / | Serves the single-page interface |
| GET | /favicon.ico | Icon |
| GET | /api/health | Liveness check; reports whether AI is offline and the number of curated evidence records |
| GET | /api/meta | Version, counts and run settings for the interface |
| GET | /api/template | Blank case JSON |
| GET | /api/example | The ILLUSTRATIVE example case (placeholders, labelled Assumption) |
| GET | /api/risk-library | The risk library (Appendix B) with seed placement |
| GET | /api/rules | The site-fact rules (Appendix C) |
| GET | /api/evidence | Evidence records (curated list, by ids, or search with ?q=) |
| GET | /api/settings | Whether an AI key is configured (never returns the key) |
| POST | /api/settings | Store the AI provider and key outside the project folder |
| POST | /api/settings/test | One small real request to the provider to check the key |
| POST | /api/validate | Check a case; always HTTP 200 with ok true/false and a problem list |
| POST | /api/run | Run the register, rules and matrix on a case (HTTP 422 on problems) |
| POST | /api/analyze | Optional decision layer: Monte Carlo schedule, delay cost / EMV, response comparison on user-entered numbers |
| POST | /api/analysis-report | Markdown report of the optional decision layer |
| GET | /api/mitigation-catalogue | Catalogue of candidate responses (text only, no effect sizes) |
| GET | /api/example-analysis | ILLUSTRATIVE case with cost model, deadline and responses |
| POST | /api/suggest-risks | Guarded AI suggestions: risk names, mechanisms and evidence IDs only |
| POST | /api/report | register.md |
| POST | /api/register-csv | register.csv |
| POST | /api/matrix-svg | matrix.svg download |
| POST | /api/report-html | report.html download |

Errors on `/api/` paths return JSON. `POST /api/validate` always answers HTTP 200 with `{"ok": true, "result": ...}` or `{"ok": false, "problems": [...]}`; `POST /api/run` answers 422 when the case has problems. The desktop version (`python -m gui.qt_app`) hosts the same interface in a Qt WebEngine window; it is a wrapper, not a separate implementation.
