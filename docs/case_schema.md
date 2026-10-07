# Case file schema

A case is a JSON object. `python -m app.cli template` prints a blank one and `python -m app.cli example` an
ILLUSTRATIVE one (all numbers are placeholders). Every numeric input that is not a plain count is an object
`{"value": <number>, "source": <Source>, "evidence_ids": [...], "note": "..."}` where `source` is one of
`Literature`, `Historical Data`, `User Input`, `Expert Judgment`, `Derived Calculation`, `Assumption`.
Time units are WORKING DAYS.

| Block | Fields | Notes |
|---|---|---|
| `project` | name, location, construction_type, notes | descriptive |
| `activity` | id, name, planned_duration_days {value, source} | the planned duration is needed for the matrix (impact is a fraction of it) and for rule RL-MAT2; without it the matrix is skipped with a note |
| `facts` | free key/values | inputs to the rule engine, e.g. required_workers, available_workers, material_lead_time_days, material_buffer_days, monsoon_overlap. `planned_duration_days` is added automatically |
| `rules` | optional list | default: `data/rules_masonry.json`. Rules flag relevant risks; they never produce probabilities |
| `risks` | id, name, category, description, status, p {value, source}, delay {kind pert/triangular/uniform/fixed, a, m, b, lam, source}, evidence_ids | p = probability the risk occurs at least once during the activity; delay = EXTRA delay in days if it occurs. A risk whose p or delay is not entered yet stays in the register and is left off the matrix, with a note. A value that is present but wrong (p outside 0 to 1, min > max, a number with no source) is rejected |
| `impact_bin_edges_fraction` | four ascending fractions of the planned duration | user input, no default; needed for the ordinal risk matrix |

`run_case` returns: `project`, `activity`, `risks` (one row per register entry, with `complete`, `p`, `delay`
and any rule `flag`), `matrix` (p class, impact class, score, level and expected delay if it occurs, for every
complete risk), `summary` (counts and level totals), `rules` (fired, not evaluable, flags), `rule_base_issues`,
`warnings`, and `report_markdown`. The command line writes `register.md`, `register.csv` and `result.json`.
