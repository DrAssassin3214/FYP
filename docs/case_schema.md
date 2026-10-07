# Case file schema

A case is a JSON object. `python -m app.cli template` prints a blank one and `python -m app.cli example` an
ILLUSTRATIVE one (all numbers are placeholders). Every numeric input that is not a plain count is an object
`{"value": <number>, "source": <Source>, "evidence_ids": [...], "note": "..."}` where `source` is one of
`Literature`, `Historical Data`, `User Input`, `Expert Judgment`, `Derived Calculation`, `Assumption`.
Time units are WORKING DAYS.

| Block | Fields | Notes |
|---|---|---|
| `project` | name, location, construction_type, notes | descriptive |
| `activity` | id, name, planned_duration_days {value, source} | the planned duration is needed for the impact class of risks with entered numbers (impact is a fraction of it) and for rule RL-MAT2; without it those risks are not placed (a note says so), while risks placed from the literature seed need no planned duration |
| `facts` | free key/values | inputs to the rule engine, e.g. required_workers, available_workers, material_lead_time_days, material_buffer_days, monsoon_overlap. `planned_duration_days` is added automatically |
| `rules` | optional list | default: `data/rules_masonry.json`. A rule flags a relevant risk as elevated. A flag never produces a probability or a delay for an entered risk. For a risk that is placed from the literature seed, a flag raises its seed probability class by one (capped at 5); that step is an Assumption of this tool with no literature source |
| `risks` | id, name, category, description, status, p {value, source}, delay {kind pert/triangular/uniform/fixed, a, m, b, lam, source}, evidence_ids | p = probability the risk occurs at least once during the activity; delay = EXTRA delay in days if it occurs. A risk whose p or delay is not entered stays in the register. If the literature seed has a value for it (30 of the 38 library risks), it is placed on the matrix from the seed (marked "literature seed", ordinal only, no probability or delay is shown or computed from it); otherwise it is left off the matrix with a note. The seed is a survey importance rank (RII) turned into a band that is used as BOTH the probability class and the impact class, which is an Assumption; an RII is not a probability and not a number of days. Entering both p and delay replaces the seed placement A value that is present but wrong (p outside 0 to 1, min > max, a number with no source) is rejected |
| `use_literature_seed`, `seed_basis` | optional top-level keys | `use_literature_seed` (true by default; set false to leave un-numbered risks off the matrix) and `seed_basis` (`seed` by default: the five seed studies; `all`: also uses the held-out studies and "related" mappings, so the held-out agreement check no longer applies to it) |
| `impact_bin_edges_fraction` | four ascending fractions of the planned duration | user input, no default; needed for the ordinal risk matrix |

`run_case` returns: `project`, `activity`, `risks` (one row per register entry, with `complete`, `p`, `delay`
and any rule `flag`), `matrix` (p class, impact class, score, level and expected delay if it occurs, for every
complete risk; literature-seed placements carry no expected delay and are marked `basis: literature-seed`), `summary` (counts and level totals), `rules` (fired, not evaluable, flags), `rule_base_issues`,
`warnings`, and `report_markdown`. The command line writes `register.md`, `register.csv` and `result.json`.
