# Chapter 5. System Design and Implementation

This chapter describes the tool as it exists in the repository on 8 October 2026. Everything stated here can be checked against a file in the repository; where a statement rests on a test, the test is named. Section 5.1 sets out the requirements the design answers, Sections 5.2 to 5.4 the architecture, data model and risk library, Sections 5.5 to 5.7 the rule engine, the register and matrix logic and the literature-tier display, Sections 5.8 and 5.9 the AI evidence layer and the exports, Section 5.10 the interface, Section 5.11 the desktop wrapper and the build, and Section 5.12 the optional decision layer. Chapter 6 reports how the tool was verified.

Two points frame the chapter. First, the tool does not predict delay. It organises delay risks for one activity (brick or block masonry), places them on a probability-impact matrix as an ordinal aid, and keeps every number it shows tied to a Source label. Second, no site data and no expert survey were collected for this project, so every probability, delay, cost and planned duration shown in the screenshots below is an ILLUSTRATIVE placeholder labelled Assumption. The scope change from the original project title is explained in Chapter 1.

## 5.1 Requirements

### 5.1.1 How the requirements were obtained

The requirements below were reconstructed from the project's own design documents (`README.md`, `docs/Project_Handoff_Summary.md`, `docs/case_schema.md`), from the integrity rules the team adopted (Handoff section 3), and from four review passes carried out on 8 October 2026 (engineering and usability, domain, research methods, examiner). They were not elicited from site managers. No requirements interview, site visit or usability session was held, and the requirements therefore express what the team decided the tool should do, not what practitioners asked for. This is a limitation of the work and is repeated in Chapter 6.

### 5.1.2 Functional requirements

**Table 5.1.** Functional requirements and where each is implemented. Source: repository files named in the last column.

| ID | Requirement | Implemented in |
|---|---|---|
| FR1 | Describe one masonry activity: project details, activity name, planned duration in working days with a Source | `gui/static/js/screens/case.js`; `app/service.py` (`parse_case`) |
| FR2 | Accept site facts (Yes / No / Unknown, or a number) and evaluate rules on them; a missing fact must never be guessed | `app/engine/rules.py`; `gui/static/js/screens/rules.js` |
| FR3 | Offer a curated library of masonry delay risks, each with the evidence record IDs that show the risk exists | `data/risk_library_masonry.json`; register screen side panel |
| FR4 | Keep a risk register: probability and a delay range per risk, each with a Source, plus status and text-only owner, early-warning sign, response type, action and review date | `app/service.py`; `gui/static/js/screens/risks.js` |
| FR5 | Place risks that have entered numbers on a 5 x 5 probability-impact matrix and state the level | `app/engine/matrix.py`; `gui/static/js/screens/matrix.js` |
| FR6 | Place risks without entered numbers at a labelled literature tier, never as a probability | `app/literature_seed.py`; `app/service.py` (`run_case`) |
| FR7 | Search a cited evidence corpus and show the record behind each citation | `app/ai_layer/evidence.py`, `corpus.py`; evidence screen |
| FR8 | Propose candidate risks from the corpus (offline retrieval, optionally an LLM) without any number coming from the model | `app/ai_layer/guard.py`; `gui/api.py` (`/api/suggest-risks`) |
| FR9 | Export the register and matrix as `register.md`, `register.csv`, `report.html`, `matrix.svg`, `matrix.png`, and save and reopen the case as JSON | `app/reporting/*`; `gui/api.py` |
| FR10 | Reject wrong input with a plain message and keep the last valid result on screen | `app/service.py`; `gui/static/js/problems.js` |
| FR11 | Optional: compare responses by simulated schedule and cost using only user-entered numbers | `app/analysis.py`, `app/engine/*` |
| FR12 | Run offline on a site laptop, as a browser page or a desktop window, with a Windows build | `gui/__main__.py`, `gui/qt_app.py`, `.github/workflows/build-exe.yml` |

### 5.1.3 Non-functional requirements and integrity constraints

**Table 5.2.** Non-functional requirements and constraints. Source: `docs/Project_Handoff_Summary.md` sections 3 and 9; `gui/README_GUI.md`. RG-n refers to the relevance guard test `test_gn_*` in `tests/test_relevance_guard.py` (Section 6.3).

| ID | Requirement | How it is met |
|---|---|---|
| NFR1 | Every number carries a Source label (Literature, Historical Data, User Input, Expert Judgment, Derived Calculation, Assumption) | `Source` enumeration in `app/engine/models.py`; a number without a Source is a problem; guard test RG-5 checks that every number in the exports has its Source |
| NFR2 | A survey importance index (RII) is never presented as a probability or as days | literature tier labelled Assumption; excluded from level totals; no p or delay shown for it |
| NFR3 | AI never supplies a probability, delay, cost or effect size | guard rules G2, G7, G9 (Section 5.8); guard test RG-10 |
| NFR4 | Deterministic and reproducible: same case, same output | determinism checked in the QA run (Section 6.7); Monte Carlo uses a fixed seed |
| NFR5 | Offline for the core path; nothing leaves the machine unless the user adds an AI key | server binds `127.0.0.1` only; host-header check; key stored outside the project folder |
| NFR6 | Calm failure: no stack trace to the user, no silent defaults | `CaseError` problems list; JSON error handlers in `gui/api.py` |
| NFR7 | Readable at 1280 px and 800 px, light and dark theme, no horizontal page scroll | checked by screenshots on 8 October 2026 (Handoff section 9, item 7) |
| NFR8 | Wording stays within what the work supports (no "validated", "predicts", "optimal") | guard tests RG-4 and the analysis test on optimality wording |

## 5.2 Architecture

### 5.2.1 Layers

The tool is a single Python package with a small local web interface. Figure 5.1 shows the layers. The interface (HTML, CSS and JavaScript in `gui/static`) is served by a Flask application (`gui/api.py`) bound to `127.0.0.1`. The interface holds the case in the browser, and on every edit it posts the case to the server, which returns the register and the matrix. The interface computes nothing of its own: the service function `app.service.run_case` produces every figure on screen (`gui/README_GUI.md`).

![Figure 5.1. Layers of the tool. Dashed box: optional decision layer. Drawn by report/scripts/make_ch5_diagrams.py from the module structure of the repository.](figures/ch5_architecture_layers.png)

This arrangement was chosen so that the same code is exercised by the command-line tool (`python -m app.cli`), the browser version, the desktop window and the tests. It keeps the engine testable without a browser and the interface free of numeric logic that could disagree with the engine.

**Table 5.3.** Size of the code base, counted with `wc -l` on 8 October 2026 over `.py`, `.js`, `.css` and `.html` files (pycache excluded). Source: command run for this report.

| Part | Lines |
|---|---|
| `app/` (engine, service, AI layer, reporting, decision layer, legacy productivity models) | 5,060 |
| of which `app/productivity/` (legacy, not used by the interface) | 420 |
| `gui/` Python (server, entry point, Qt wrapper) | 761 |
| `gui/static/` (interface: HTML, CSS, JavaScript) | 3,928 |
| `tests/` | 3,297 |

Line counts say nothing about quality; they are given so the reader can judge the size of what was verified.

### 5.2.2 Data flow of one edit

Figure 5.2 follows one edit through the service. `parse_case` checks types and the presence of a Source on every number and builds a list of problems. If there are problems, the run stops and the interface keeps the last valid result on screen, marked as stale. Otherwise the rule engine evaluates the site facts, the matrix classifies every risk that has entered numbers, and the literature seed places the remaining library risks that have a seed value. The result object carries the register rows, the matrix rows, the summary counts, the matrix settings with their Source, the rule outcomes, the warnings, and the rendered Markdown and SVG.

![Figure 5.2. Data flow of `run_case` (`app/service.py`). Dashed box: the optional decision layer takes the same case plus cost inputs.](figures/ch5_dataflow_run_case.png)

### 5.2.3 Module map

**Table 5.4.** Main modules. Source: repository tree.

| Module | Role |
|---|---|
| `app/service.py` | Parsing and validation of the case, `run_case`, example and template cases, evidence lookup, suggestion entry point |
| `app/engine/models.py` | `Source`, `Param`, `DelayDist` (PERT, triangular, uniform, fixed), `Risk`, `Mitigation`, `CostModel` |
| `app/engine/rules.py` | Rule objects, typed evaluation, rule-base consistency check, priority and conflict resolution |
| `app/engine/matrix.py` | Probability class, impact class, score and level |
| `app/literature_seed.py` | Literature tier from the seed file |
| `app/ai_layer/` | Evidence store, retrieval, guard, LLM clients, settings store |
| `app/reporting/` | `register.md`, `register.csv`, `report.html`, `matrix.svg` writers |
| `app/analysis.py`, `app/engine/{simulation,emv,decision,options}.py` | Optional decision layer |
| `gui/api.py`, `gui/__main__.py`, `gui/qt_app.py` | Local server, entry points, desktop wrapper |
| `data/*.json` | Risk library, rules, literature seed, mitigation catalogue |
| `app/productivity/`, `data/productivity_models.json`, `data/india_labour_norms.json` | Earlier labour-productivity models; out of scope, not used by the interface (guard test RG-6) |

The productivity models belong to the original project scope. They remain in the repository because their removal needs a supervisor decision (Handoff section 9), and a guard test confirms that neither the live application nor the interface loads them.

## 5.3 Data model: the case file

A case is one JSON object (`docs/case_schema.md`). It is the only input to the engine, and it is what the interface saves and opens. Every numeric input other than a plain count is an object `{"value", "source", "evidence_ids", "note"}`, and time is in working days.

**Table 5.5.** Blocks of the case file. Source: `docs/case_schema.md`; `app/service.py` (`template_case`).

| Block | Content | Notes |
|---|---|---|
| `project` | name, location, construction type, notes | descriptive only |
| `activity` | id, name, `planned_duration_days` {value, source}; optional `deadline_days` | impact class is measured against the planned duration |
| `facts` | key-value pairs: numbers, true/false | inputs to the 22 rules; `planned_duration_days` is added automatically |
| `risks[]` | id, name, category, status, `p` {value, source}, `delay` {kind, a, m, b, source}, evidence IDs; text-only owner, trigger, response type, action, review date | p is the probability that the risk occurs at least once during the activity; delay is the extra delay in days if it occurs |
| `impact_bin_edges_fraction`, `impact_bin_edges_source` | four ascending fractions of the planned duration, with a Source | user input, no default |
| `use_literature_seed`, `seed_basis` | switch for the literature tier; `seed` (default) or `all` | `all` also uses held-out studies, so no held-out comparison applies to it |
| `cost`, `mitigations[]`, `options[]`, `constraints`, `simulation` | optional decision layer | Section 5.12 |

Three design choices in the data model are worth stating.

1. **Source is part of the number.** A probability without a Source is rejected as a problem rather than defaulted, and a delay distribution carries its own Source. The six values of `Source` are those listed in the project's integrity rules.
2. **Delay is conditional.** The delay is the extra delay in working days given that the risk occurs, and p is the probability of occurrence during the activity. This is the same Bernoulli-times-delay structure used for risk events in the schedule-risk literature recorded in the research notes (for example the Beta-PERT times Bernoulli construction of Prins et al., 2022, a preprint that was not peer reviewed). The structure is a modelling choice of this tool, stated as such.
3. **Wrong is not the same as missing.** A value that is present but invalid (p outside 0 to 1, minimum above maximum, a number with no Source, a boolean or non-finite value where a number is needed) is a problem and the register keeps its last valid state. A value that is simply not entered leaves the risk in the register without a placement or with a literature tier.

A blank template is produced by `python -m app.cli template` and the ILLUSTRATIVE example by `python -m app.cli example`. The example has seven risks; Section 5.10 shows it in the interface and Chapter 6 recomputes it by hand.

## 5.4 The risk library

The library (`data/risk_library_masonry.json`) holds 46 risks. Thirty-eight were built on 7 October 2026 from the factors transcribed from the eleven studies of the literature seed, and eight were added on 8 October 2026 after the domain review (R-FRONT, R-VT, R-MORT, R-GPAY, R-OPEN, R-SCAF, R-FEST, R-HEAT). Each entry has an identifier, a name, a category, a description, the evidence IDs that show the risk exists, an evidence note, and a scope (`activity` for 38, `project` for 8). Entries without a survey value carry a `seed_status` note.

**Table 5.6.** Library risks by category and by whether the literature seed has a value for them. Generated from the data by `report/scripts/gen_ch5_tables.py`. Source: `data/risk_library_masonry.json`, `data/literature_seed.json` (seed studies, direct mappings).

| Category | Risks | With seed value | Without |
|---|---|---|---|
| Labour | 13 | 9 | 4 |
| Management | 6 | 4 | 2 |
| Material | 6 | 4 | 2 |
| Design | 4 | 3 | 1 |
| Equipment | 3 | 1 | 2 |
| External | 3 | 2 | 1 |
| Financial | 3 | 2 | 1 |
| Quality | 2 | 1 | 1 |
| Safety | 2 | 2 | 0 |
| Site | 2 | 1 | 1 |
| Weather | 2 | 1 | 1 |
| **Total** | **46** | **30** | **16** |


The evidence IDs on a library entry support only the statement that the risk exists in published studies. They do not support a probability. The evidence note of R-MAT, for instance, records that M01 reports material shortage at RII 0.777 and that survey rankings show importance, not probability.

Sixteen library risks have no survey value in the seed studies. They are listed in Table 5.7. Eight were in the original 38 and have no matching survey item; eight were added later and are written in site language from the domain review. For the eight added risks the masonry-specific form of the risk is labelled Expert Judgment in the library and is to be confirmed by the expert survey, which has not been run.

**Table 5.7.** The 16 library risks without a seed value, with the rules that flag them. Generated by `report/scripts/gen_ch5_tables.py`. Source: `data/risk_library_masonry.json`, `data/rules_masonry.json`.

| Risk | Name | Category | Scope | Added 2026-10-08 | Rules that flag it |
|---|---|---|---|---|---|
| R-TRN | Inadequate training of workers | Labour | activity | no | none |
| R-PRD | Low labour productivity | Labour | activity | no | none |
| R-SUB | Subcontracting and contract-type problems | Management | activity | no | none |
| R-CLI | Client decision delay or pressure | Management | project | no | none |
| R-QLT | Inspection and quality-approval delays | Quality | activity | no | none |
| R-DEF | Defective or poor-quality material | Material | activity | no | none |
| R-GOV | Government policies or approvals | External | project | no | none |
| R-FIN | Contractor financial difficulties | Financial | project | no | none |
| R-FRONT | Work front not released (slab not de-shuttered, props or debris in place, frame not handed over) | Site | activity | yes | RL-FRONT |
| R-VT | Hoist or material lift unavailable or broken (bricks and mortar to upper floors) | Equipment | activity | yes | RL-VT |
| R-MORT | Mortar materials short or poor (cement, sand, or mixer down) | Material | activity | yes | RL-MORT |
| R-GPAY | Gang wages or labour-contractor running bill overdue | Labour | activity | yes | RL-GPAY |
| R-OPEN | Openings, lintels, door/window frames and MEP sleeves not coordinated | Design | activity | yes | RL-OPEN |
| R-SCAF | Scaffolding not available, not erected or not passed safe | Equipment | activity | yes | RL-SCAF |
| R-FEST | Festival, harvest or election season exodus of the migrant gang | Labour | activity | yes | RL-FEST, RL-FEST2 |
| R-HEAT | Peak-summer heat cuts effective working hours | Weather | activity | yes | RL-HEAT |


Two limits follow from the table. Only 18 of the 46 library risks have any rule: the 10 original rule targets plus the 8 added risks. The other 28 enter the register by choice from the library, from an AI suggestion, or as custom risks. And the library is built from general building-construction surveys, with masonry-specific evidence mainly from M01 and A02, so it should not be read as a census of masonry delay causes on Indian sites. The risk of over-reading it is discussed in Chapter 7.

## 5.5 The rule engine

### 5.5.1 Purpose and constraints

The rule engine turns declared site facts into qualitative flags. A rule states a logical condition over facts, for example required workers exceed available workers. A rule flags one library risk as `elevated` or `normal` (relevant only). The module's design constraints (`app/engine/rules.py`) are the following.

- A rule carries no probability and no numeric threshold invented by the software. Where a number appears, it is a fact the user enters (stock days, lead time) or the planned duration.
- A flag never produces a probability or a delay for a risk with entered numbers.
- A fact that is missing, or that has the wrong type for the rule, makes the rule "not evaluable". It is reported as such and never guessed.
- Every rule has an identifier, a Source, evidence IDs, a rationale and a confidence, and the rule base is checked for consistency before use.

### 5.5.2 Evaluation

A rule has a list of `all_of` conditions and an optional list of `any_of` conditions. Each condition compares a fact with a literal or with another fact, using one of `lt, le, gt, ge, eq, ne, in`. The rule fires when every `all_of` condition is true and, if `any_of` is present, at least one `any_of` condition is true.

Typing is strict. Numeric comparisons need finite real numbers, and equality tests need the fact to have the same type as the value it is compared with. A string such as "10" or "yes" is not coerced. A rule is "not evaluable" if a needed fact is missing or has the wrong type and no other condition of the rule is already false.

When several rules fire on the same risk, the highest priority wins. If rules of equal priority disagree on the level, the outcome is reported as `conflict`. The rule base itself is checked for duplicate IDs, unknown facts, unknown levels, missing conditions, literature-sourced rules without evidence IDs, and identical conditions with contradictory levels (`check_rule_base`). Guard test RG-8 asserts that no pair of rules on one risk can give an equal-priority conflict.

### 5.5.3 The 22 rules

**Table 5.8.** The 22 site-fact rules. Generated from `data/rules_masonry.json` by `report/scripts/gen_ch5_tables.py`; the "condition in words" is the rule's own description field. Level `elevated` marks the risk as elevated; `normal` marks it as relevant only. Pri. is the priority used when several rules fire on one risk. Source: `data/rules_masonry.json`.

| Rule | Condition (in words) | Formal condition | Risk flagged | Level | Pri. | Source | Conf. |
|---|---|---|---|---|---|---|---|
| RL-LAB | Required workers exceed workers available | `required_workers` > `available_workers` | R-LAB | elevated | 0 | Assumption | Moderate |
| RL-MAT | Stock on site runs out before a new delivery can arrive (for the material with the longest lead time) | `material_stock_days` <= `material_lead_time_days` | R-MAT | elevated | 1 | Assumption | Moderate |
| RL-MAT2 | Stock on site covers fewer days than the planned duration | `material_stock_days` < `planned_duration_days` | R-MAT | normal | 0 | Assumption | Low |
| RL-TOOL | Tools or equipment shortage expected | `tools_shortage` = true | R-TOOL | elevated | 0 | Assumption | Low |
| RL-WX | Activity period overlaps the monsoon / rainy season | `monsoon_overlap` = true | R-WX | normal | 0 | Assumption | Moderate |
| RL-HGT | Masonry is done at height and scaffolding is not ready | `work_at_height` = true AND `scaffolding_ready` = false | R-SAFE | elevated | 0 | Assumption | Low |
| RL-PAY | Payment delays occurred previously or are expected | `payment_delay_expected` = true | R-PAY | elevated | 0 | Assumption | Low |
| RL-DES | Drawings or details are incomplete | `design_incomplete` = true | R-DES | elevated | 0 | Assumption | Low |
| RL-RWK | Rework was frequent in earlier work on this site or crew | `prior_rework_history` = true | R-RWK | elevated | 0 | Assumption | Low |
| RL-PLAN | Planner or site engineer judges the programme faster than the gang can achieve | `schedule_compressed` = true | R-PLAN | elevated | 0 | Assumption | Low |
| RL-SKILL | Skilled masons are fewer than needed | `skilled_masons_short` = true | R-SKILL | elevated | 0 | Assumption | Low |
| RL-WX2 | Monsoon overlaps the activity and external walls are in scope | `monsoon_overlap` = true AND `external_walls_in_scope` = true | R-WX | elevated | 1 | Assumption | Low |
| RL-PACE | Planned daily output is higher than the output achieved last week | `planned_daily_output` > `achieved_daily_output_last_week` | R-PLAN | elevated | 0 | Assumption | Low |
| RL-FRONT | Floors or walls planned for the next 7 days are not de-propped, cleared and handed over | `work_front_ready` = false | R-FRONT | elevated | 0 | Assumption | Low |
| RL-VT | Masonry is above the ground floor and no hoist or material lift is available | `masonry_floor_level` >= 1 AND `hoist_available` = false | R-VT | elevated | 0 | Assumption | Low |
| RL-SCAF | Scaffolding is not ready | `scaffolding_ready` = false | R-SCAF | elevated | 0 | Assumption | Low |
| RL-MORT | Sand or cement stock runs out before a new delivery can arrive | `sand_cement_stock_days` <= `sand_cement_lead_time_days` | R-MORT | elevated | 0 | Assumption | Low |
| RL-GPAY | The gang's weekly payment or the labour contractor's bill is overdue | `gang_payment_overdue` = true | R-GPAY | elevated | 0 | Assumption | Low |
| RL-OPEN | Door/window frames, MEP sleeve layout or lintel-level plan is not ready | `frames_on_site` = false OR `mep_sleeve_layout_marked` = false OR `lintel_level_plan_issued` = false | R-OPEN | elevated | 0 | Assumption | Low |
| RL-FEST | A major festival, harvest or election falls inside the activity window | `festival_or_harvest_in_window` = true | R-FEST | normal | 0 | Assumption | Low |
| RL-FEST2 | A festival, harvest or election falls inside the window and the gang is mostly migrant | `festival_or_harvest_in_window` = true AND `gang_mostly_migrant` = true | R-FEST | elevated | 1 | Assumption | Low |
| RL-HEAT | The activity overlaps peak summer | `summer_overlap` = true | R-HEAT | normal | 0 | Assumption | Low |


All 22 rules carry the Source label Assumption, 19 have confidence Low and 3 Moderate (RL-LAB, RL-MAT, RL-WX). The reason is that each rule states a logical condition that the team judged relevant, with evidence IDs showing that the risk exists. None of the rules is an empirical finding about how much a condition raises delay. The rationale text of each rule says this, and the interface shows the Source and the confidence beside each rule. Twenty-nine distinct fact names are used by the rules, one of which (the planned duration) is supplied automatically.

Several rules were changed after the review of 8 October 2026 (Audit_Corrections section 6). RL-MAT now compares stock days with lead time with a tie counted as a stock-out; RL-MAT2, RL-WX, RL-FEST and RL-HEAT are `normal` only, so that merely overlapping the monsoon does not mark weather as elevated; RL-HGT needs scaffolding not ready as well as work at height; and RL-WX2, RL-PACE and nine other rules were added. Priorities were set so that no pair of rules on one risk conflicts.

## 5.6 Register and matrix logic

### 5.6.1 The register

The register holds one card per risk. A card shows the name, category, status, the probability and the delay range with their Source badges, evidence chips, the rule flag if any, the matrix cell if any, and the expected delay if the risk occurs. The status is one of `literature-supported`, `expert/user-provided` and `AI-suggested-unverified`. The text-only fields (owner, early-warning trigger, response type, action, review date) follow the register practice described in the risk-response literature in the research notes (avoid, reduce, transfer, accept; Baker et al., 1999; Dey, 2011). They carry no numbers and take no part in any calculation.

### 5.6.2 Expected delay

For a risk with entered numbers the matrix uses the conditional expected delay E[D], computed in closed form from the entered range (`DelayDist.mean`):

$$E[D]_{\mathrm{PERT}} = \frac{a + \lambda m + b}{\lambda + 2},\ \lambda = 4 \qquad E[D]_{\mathrm{tri}} = \frac{a + m + b}{3} \qquad E[D]_{\mathrm{uni}} = \frac{a + b}{2} \qquad E[D]_{\mathrm{fixed}} = m$$

where a, m and b are the minimum, most likely and maximum delay in working days. With the default shape weight λ = 4 the PERT mean is (a + 4m + b)/6, the classical three-point mean (Herrerias-Velasco et al., 2011; Trietsch et al., 2012). The choice of λ = 4 is the conventional default and carries no site calibration. The notes record that no source supplies a masonry-specific value of λ.

### 5.6.3 Probability class, impact class, score and level

Let T₀ be the planned duration in working days, p the entered probability, and f₁ < f₂ < f₃ < f₄ the four impact bin edges entered by the user as fractions of T₀. The probability class is

$$c_p = 1 + \sum_{k=1}^{4} \mathbf{1}[\,p \ge e_k\,],\qquad (e_1,\dots,e_4) = (0.2,\ 0.4,\ 0.6,\ 0.8)$$

and the impact class is

$$r = \frac{E[D]}{T_0},\qquad c_i = 1 + \sum_{k=1}^{4} \mathbf{1}[\,r \ge f_k\,].$$

Both classes run from 1 to 5. The indicator uses lower-edge-inclusive bins: a value exactly on an edge goes to the higher class. "Exactly on an edge" is judged with a relative tolerance of 10⁻⁹, so that 1.2 days on a 12-day activity, which is 0.09999999999999999 in binary floating point, is still the 0.10 edge. The same tolerance applies on both axes (`EDGE_REL_TOL` in `app/engine/matrix.py`); it was added to the probability axis after the audit finding M4. The score and the level are

$$s = c_p \times c_i,\qquad \text{level} = \begin{cases}\text{Low} & s \le 5\\ \text{Moderate} & 6 \le s \le 10\\ \text{High} & 11 \le s \le 15\\ \text{Extreme} & s \ge 16\end{cases}$$

The probability edges and the score thresholds are equal-width choices of the tool. They are not taken from the literature, and every export prints them labelled Assumption. The impact edges have no default: they are the user's input with a Source, and without them the matrix is not computed for entered numbers. Because the highest score in probability class 1 is 1 × 5 = 5, a risk in probability class 1 is always Low whatever its impact. This is a consequence of the product rule, and the matrix legend states it and marks the two affected cells. Risks in impact class 5 are also listed separately as a high-consequence filter, so that a severe but unlikely risk is not lost in a "Low" cell. The filter is not a score.

The matrix is an ordinal prioritisation aid. The literature on risk matrices (Cox, 2008; Duijm, 2015) warns that matrices have poor resolution, can rank a quantitatively smaller risk above a larger one, and depend on how the bins are drawn. The tool therefore keeps the continuous p and delay in the register next to the class, labels the thresholds as Assumptions, and calls the output "ordinal prioritisation only" on screen and in every export. The sensitivity of the levels to the thresholds and edges was analysed separately (Chapter 4); the matrix does not remove the limits the literature describes.

![Figure 5.3. Placement of a register risk on the matrix. Drawn by report/scripts/make_ch5_diagrams.py from `run_case` in `app/service.py`.](figures/ch5_matrix_placement.png)

## 5.7 Literature tier and source labels

### 5.7.1 What the tier is

A library risk whose probability and delay are not both entered still appears on the matrix if the literature seed has a value for it (30 of the 46 library risks). The placement is computed in `app/literature_seed.py`. For each risk, the direct-mapped RII values of each seed study are averaged first, so that one study counts once, and the study means are then averaged. The 30 risks are ranked by this mean, rank 1 being the highest, and cut into five equal-count bands of six. For rank ρ among n = 30 seeded risks,

$$\text{tier} = 5 - \left\lfloor \frac{5\,(\rho - 1)}{n} \right\rfloor .$$

The tier is used as both the probability class and the impact class. If a rule flags the risk as elevated, the probability class is raised by one, capped at 5: c_p = min(5, tier + 1). Entering both p and delay replaces the placement.

Both uses of the tier are Assumptions of this tool, and neither is a finding. An RII measures how important respondents rated a factor; it is not a probability and not a number of days. Using one rank on both axes squares it in the score, and the +1 step for a rule flag has no literature source. The seed values themselves match the printed papers (Audit_Corrections, row-level check of all 182 values), but the agreement of the seed with held-out surveys is weak and not statistically significant (Handoff section 8.4, reported in Chapter 4). The seed is therefore an ordinal starting position, to be replaced by expert-survey and site data.

### 5.7.2 How the tier is displayed

After the committee review of 8 October 2026, a seeded risk is shown differently from a risk with entered numbers, in all outputs.

- The chip on the grid is grey with a dashed outline and the label "literature tier (Assumption)". The cell colour beneath it is the colour of the cell, not an assessed level for that risk.
- Seeded risks are left out of the level totals (`summary.levels`, the key-figure strip, and the High, Moderate, Low counts). The strip counts "on matrix (entered numbers)" separately from the seeded count.
- No probability, expected delay or monetary value is displayed or computed for a seeded risk.
- In `register.csv` the `level` cell is empty for a seeded row and the `tier` column holds the text "literature tier (Assumption): tier n".
- The +1 step is labelled Assumption wherever it applies.

A fuller alternative, showing seeded risks in neutral colour with no level at all and dropping the +1 step, was considered in the review and left to a supervisor decision (Audit_Corrections section 6). The present display is the smaller fallback.

### 5.7.3 Source labels in the interface

Every numeric field has a Source picker, and the badge (for example ASM for Assumption) is shown beside the value on register cards, in the matrix table and in the exports. Typing a number into an empty field sets the Source to User Input; it never sets Literature automatically. The matrix legend prints the impact edges with their Source and the default probability edges and score thresholds as Assumption. If the impact edges have no Source, the tool gives a warning and the exports print "Source: not given". A banner on every screen states "ILLUSTRATIVE case: every number is a placeholder, not evidence and not site data" whenever the example is loaded (guard test RG-7 keeps the example labelled in every export).

## 5.8 AI evidence layer and guard rules

### 5.8.1 Purpose

The AI layer helps identify candidate risks. It does not estimate anything. The user types an activity and a query; the tool retrieves the best-matching records from the evidence store, sends only those records to a language model, and accepts back candidate risks that name a mechanism and cite record IDs. The layer works without a key in an offline mode that returns matching library risks and evidence records. With a key stored in Settings, either an Anthropic or a Google model can be called; default model identifiers are set in `app/ai_layer/clients.py` and can be overridden. The Gemini path was checked against the live service during development, and the Anthropic path was not checked because no key was available (`gui/README_GUI.md`). The key is stored in the user's application-data folder, outside the project folder, with restricted file permissions, so that zipping the project for submission does not carry it.

### 5.8.2 Evidence store and retrieval

The store holds the curated records of `Literature_Evidence_Package.xlsx` and the structured records parsed from `Research_Notes/` (`app/ai_layer/corpus.py`). The running application reports 472 evidence records. Retrieval is lexical, by token overlap, and runs offline. The code comments and the GUI notes state that lexical retrieval is simple and that many harvested records have an abstract only. Retrieval grounding does not by itself prevent unsupported output, which is why the guard follows it.

![Figure 5.4. Path of an AI suggestion from query to register. Dashed boxes: optional or rejected paths. Drawn from `app/ai_layer/guard.py`.](figures/ch5_ai_guard_flow.png)

### 5.8.3 Guard rules

The guard (`app/ai_layer/guard.py`) validates every reply before anything reaches the interface. Table 5.9 lists the rules. Each is enforced in code and exercised in `tests/test_ai_guard.py` or the relevance guard tests.

**Table 5.9.** Guard rules G1 to G9 of the AI layer. Source: `app/ai_layer/guard.py` header and code.

| Rule | What it enforces |
|---|---|
| G1 | Every cited ID must be in the retrieved set and in the store; otherwise it is dropped and the item flagged |
| G2 | Any numeric field the model returns (probability, delay, cost, effect size and similar listed keys) is stripped and logged as rejected |
| G3 | A quoted passage must appear in the cited record's stored text; otherwise the quote is flagged |
| G4 | Output is always `AI-suggested-unverified`; only an explicit user confirmation changes the status |
| G5 | The prompt, model identifier, retrieved IDs and raw output are kept verbatim in an audit log |
| G6 | Belongs to the explanation module (`app/ai_layer/explain.py`), which checks numbers in a narrative against the result trace; that module is not exposed by the current interface |
| G7 | A suggestion whose name, category or mechanism contains a probability, percentage, duration, day count or currency figure is rejected and logged |
| G8 | Every field is type-checked; one malformed item is dropped and logged and the others survive |
| G9 | Unknown numeric keys (likelihood, days, impact and similar) are dropped and logged as under G2 |

The consequence is that the AI path cannot place a number in the register. A candidate carries a name, a category, a mechanism and valid evidence IDs. `promote` turns a candidate into a risk only when the caller supplies the probability and delay with a Source, refuses a derived value as the source of either, and leaves the status at AI-unverified unless the user confirms. Guard test RG-10 checks that no path from the AI layer to the service can carry a number, and guard test RG-4 checks that the wording of the exports no longer claims "No number here was produced by AI", a sentence that the audit (finding M7) showed was not enforced at the time. It was replaced by a statement of what the tool does: it does not generate probabilities, delays or costs, each number shown was entered with the Source printed next to it, and the AI feature can propose names, mechanisms and evidence IDs only.

### 5.8.4 Limits of the guard

The guard is pattern-based. G7 detects figures with regular expressions for percentages, probability phrases, durations and currency; a figure written in a form that none of the patterns matches could pass, and a suggestion with a harmless number in a name could be rejected without need. G3 compares text after whitespace and case normalisation, so a paraphrase is flagged but a quotation of the wrong sense is not. The guard does not judge whether a suggested risk is good: it judges whether it is traceable and number-free. Whether AI suggestions improve identification has not been tested; this would need a comparison with an expert-built list, which was not done.

## 5.9 Exports

All exports are produced from the result object, so they cannot disagree with the screen.

**Table 5.10.** Exports. Source: `app/reporting/*`, `gui/api.py`.

| File | Content |
|---|---|
| `register.md` | Settings block (impact edges with Source; probability edges and thresholds as Assumption), the matrix grid, the register table, rule flags, warnings, and the statement of what the tool does and does not do |
| `register.csv` | One row per risk, 28 columns including basis (entered or literature tier), p and its Source, delay kind and range, class and level, `tier`, ILLUSTRATIVE note, and the text-only register fields |
| `report.html` | Printable page with the coloured matrix and the register (print to PDF from the browser) |
| `matrix.svg`, `matrix.png` | The 5 x 5 grid as a graphic |
| case JSON | The input case, for saving and reopening |
| `analysis.md` | Optional decision layer report (Section 5.12) |

Several output-safety measures were added after the QA run (Chapter 6). The CSV neutralises cells that begin with `=`, `+`, `-`, `@`, tab or carriage return, so a risk named with a spreadsheet formula is written as text. The Markdown writer escapes the pipe character and replaces newlines. The HTML report escapes all text. The SVG writer escapes its inputs. The CSV is served with a byte-order mark so that Excel on Windows decodes non-ASCII names.

## 5.10 The interface

The interface has seven screens in the left rail (Table 5.11). A top bar holds the case name, an unsaved-changes indicator, an input-problem counter and the New, Open, Save and Load example buttons, and a theme switch. A strip under the bar summarises the register: risks, complete, on the matrix (entered numbers), levels, and rule-flagged. Shortcuts are Ctrl+S, Ctrl+O and Esc.

**Table 5.11.** Screens. Source: `gui/README_GUI.md`; `gui/static/js/app.js`.

| # | Screen | Purpose |
|---|---|---|
| 1 | Case & Activity | project details, activity, planned duration with Source |
| 2 | Site facts & Rules | declare facts; see which rules fired, which are not evaluable |
| 3 | Risk register | cards with p, delay, Source, status, evidence; library and AI suggestions in a side panel |
| 4 | Risk matrix | impact edges with Source; the grid; the table of classes and levels; the high-consequence list |
| 5 | Cost, options & decision | optional decision layer (Section 5.12) |
| 6 | Evidence | curated records; search across the corpus |
| 7 | Export | downloads |

The following figures show each screen with the ILLUSTRATIVE example loaded, at a viewport width of 1280 px in the light theme, captured with Playwright and Chromium on 8 October 2026 by `report/scripts/take_screenshots.py`. Long pages are cropped at the bottom; no other editing was done. Every number in these figures is an ILLUSTRATIVE placeholder labelled Assumption.

![Figure 5.5. Case & Activity screen with the ILLUSTRATIVE example. Planned duration (16 working days) and its Source are on this screen. The values are placeholders, not site data.](figures/fig5_screen_case.png)

![Figure 5.6. Site facts & Rules screen (top part), with the ILLUSTRATIVE example. Each fact is a Yes / No / Unknown control or a number field with its unit, and names the rules that use it. The rule table below the facts is listed in Table 5.8. Cropped.](figures/fig5_screen_rules.png)

The facts screen avoids free text on purpose. Every input is a number with a unit, or a three-way Yes / No / Unknown control, so the user cannot type a value the rules cannot read. Unknown is the default and means "not evaluable", which is different from No.

![Figure 5.7. Risk register screen with the ILLUSTRATIVE example: seven cards, each with p and delay and their Source badges, evidence chips, rule flag and matrix cell. The side panel offers the 46-risk library and AI suggestions.](figures/fig5_screen_risks.png)

![Figure 5.8. Risk matrix screen with the ILLUSTRATIVE example. The grey notice states what the literature seed is and is not. The grid shows the seven risks; the legend states the impact edges and their Source, the probability edges and score thresholds as Assumption, and marks the two probability-class-1 cells where a risk is Low whatever its impact. Below the grid: the table of classes and levels and the high-consequence list.](figures/fig5_screen_matrix.png)

In the example, R-MAT falls in probability class 3 and impact class 5 (score 15, High) and is the only entry in the high-consequence list; five risks are Moderate and R-PLAN is Low. The hand calculation in Chapter 6 reproduces these cells. The example has no risk placed from the literature tier, so no grey dashed chip appears in this figure; the dashed style is exercised in tests (Chapter 6) and in the legend.

![Figure 5.9. Evidence screen (top part, cropped). The search reaches the whole corpus; curated records are listed first.](figures/fig5_screen_evidence.png)

![Figure 5.10. Export screen (top part, cropped).](figures/fig5_screen_report.png)

Errors are handled in the same way on every screen. A value that is present but wrong is shown beside the field and in a problem counter in the top bar, with a button that jumps to the screen that holds it. The register and matrix keep their last valid state and are marked stale until the problem is fixed. Opening a saved case restores it exactly: a risk the user deleted is not re-added on open. This was defect 1 of the QA report and is now covered by a test (Chapter 6).

## 5.11 Desktop wrapper, build and continuous integration

### 5.11.1 Two ways to run

`python -m gui` starts the server and opens a browser tab at `http://127.0.0.1:8765/`; the next free port is used if the preferred one is busy. `python -m gui.qt_app` opens a PySide6 window that hosts the same interface in Qt WebEngine. The window starts the same Flask server on a free loopback port in a background thread, loads it, opens any external link in the normal browser, and replaces browser downloads with a Save dialog. The desktop window therefore adds no new logic: it is a different container for the same files, and a defect in the engine is the same defect in both.

The project description speaks of a PySide6 desktop application. The implementation is accurate to that description only in this sense: the window is a PySide6 application, but the interface inside it is web content. This is stated so that the wrapper is not mistaken for a native Qt interface.

### 5.11.2 Build and checks

`build_desktop_exe.bat` and `build_exe.bat` build Windows executables with PyInstaller from `fyp_desktop.spec` and `fyp_gui.spec`. A GitHub Actions workflow (`.github/workflows/build-exe.yml`, run on demand or on a version tag) performs the following on a Windows runner: install the requirements, run the test suite, build the browser-version executable, start it and call `/api/health`, `/api/example` and `/api/run`, run the desktop window from source in a headless self-test (`--smoke`), build the desktop executable, run its self-test, and upload the zipped folders as artifacts. The self-test loads the page, checks that the page has buttons and text and that the server reports loaded evidence records, and writes a JSON result.

**What was and was not checked.** The workflow is in the repository. In the working session for this report it was not run, because the session is a Linux machine without Windows, PyInstaller or Qt WebEngine, and the QA report states that the Qt wrapper and `fyp_desktop.py` were not tested in its run. This report therefore makes no claim that the Windows executables were built or run successfully; the workflow is the means by which that is to be checked, and its log is the evidence. Python 3.12 is the version used on the build runner, and the development environment of this report used Python 3.13.

### 5.11.3 Dependencies and offline use

The runtime requirements are Flask, NumPy, SciPy, Matplotlib and openpyxl; the desktop window adds PySide6. No component of the core path needs a network. The only network use is an AI request, which happens only when the user has stored a key and presses the suggestion button, and the test route for the key. The server answers only requests addressed to `127.0.0.1`, `localhost` or the loopback IPv6 name, which blocks DNS-rebinding access to the settings routes (`gui/api.py`). The server is the Flask development server, which is adequate for one user on one machine and is not meant to be exposed on a network; the interface README says so.

## 5.12 Optional decision layer

### 5.12.1 Scope and status

On 8 October 2026 the team asked for a cost, options and decision screen to be added. It is implemented in `app/analysis.py` with the engine modules `simulation`, `emv`, `decision` and `options`, exposed on screen 5 and by `python -m app.cli analyze`. It is optional. The register and the matrix do not depend on it, and its result never feeds back into the register or the matrix level.

It is not the four-phase pipeline described in the original project description. In particular, it does not use a 27-state matrix to produce a delay probability, it does not produce a mitigation cost, and it does not compute the product of a P90 delay, a daily penalty and a delay probability. It computes the expected total cost of each response option from a simulated schedule, as set out below.

### 5.12.2 What goes in, and what does not

The layer uses only numbers the user enters, each with a Source: the cost of one delay day (no default), optional liquidated damages per day after a deadline, an optional deadline, per-response costs, and the effect of each response on a risk as a new probability and/or a new delay range. A response with no entered effect is reported and left out; the tool does not supply one. The mitigation catalogue (`data/mitigation_catalogue.json`, 13 entries) lists candidate actions and what must be elicited for each, and contains no effect sizes and no costs, because the evidence review found no transferable risk-reduction factor for a masonry-specific response (Research_Notes/D_mitigation.md, section 7, as recorded in the catalogue header). The layer never uses a literature-tier (RII) placement as a probability. If a risk has no entered p and delay, it is left out of the simulation with a note.

### 5.12.3 Method

For each risk i with entered probability p_i and delay distribution F_i, a simulated run draws an occurrence I_i ~ Bernoulli(p_i) and, if the risk occurs, a delay D_i ~ F_i. The duration is

$$T = T_0 + \sum_i I_i D_i ,$$

with independent, additive risks unless correlations are entered. The delay distributions are Beta-PERT with shape weight λ = 4, triangular, uniform or fixed. The draws for each risk come from a random stream keyed on the seed and the risk ID, so a response option that changes p_i or F_i reuses the same underlying draws as the baseline (common random numbers). Differences between options are then driven by the entered changes and not by sampling noise. The default is 10,000 runs and seed 12345, both user-editable (up to 200,000 runs).

The cost of a run is

$$C = C_d \max(0, T - T_0) + \ell \max(0, T - T_{dl}) + \sum_i I_i\, d_i ,$$

where C_d is the cost of a delay day, ℓ the liquidated damages per day after the deadline T_dl, and d_i an optional direct cost if risk i occurs. Early finishes earn no credit: negative delay is clipped at zero in the cost. The event expected monetary value of one risk is analytic,

$$\mathrm{EMV}_i = p_i\,(E[D_i]\,C_d + d_i),$$

and its sum equals the simulated expected delay cost in expectation for independent additive risks. It does not include liquidated damages, whose term is non-linear in T and cannot be recovered from event EMVs.

For response options, each option is a set of at most one response per risk. The tool evaluates each response alone and combinations of responses that target different risks (at most 40 options), plus the option "accept". For option j with mitigation cost M_j the total expected cost is

$$\mathrm{TEC}_j = M_j + E[C_j^{\mathrm{res}}],$$

where the residual cost is simulated with the changed p and F. The default criterion is the minimum TEC; minimum probability of exceeding the deadline and minimum P90 duration are also available, with optional constraints on the deadline probability and the mitigation budget. Infeasible responses and options that violate a constraint are removed before ranking. The result is one of the commands AUTHORIZE MITIGATION or ACCEPT RISK, with the figures behind it. The command text says the option is "preferred under the stated criterion among the options evaluated", never "optimal", and a test enforces that wording. Two further checks accompany every command: the preferred option under three different seeds, and the preferred option as the cost of a delay day is scaled from 0.25 to 4 times.

### 5.12.4 Illustrative output

The ILLUSTRATIVE analysis example (`python -m app.cli example-analysis`) adds to the register example a deadline of 20 working days, a delay-day cost of INR 8,000, liquidated damages of INR 5,000 per day, and six responses with placeholder costs and effects, one of them marked infeasible. All of these numbers are Assumptions of the example and are not evidence, site data or an expert's estimate. Figure 5.11 shows the entry fields and Figure 5.12 the decision part of the screen after the analysis was run.

![Figure 5.11. Cost, options & decision screen, inputs (cost model and candidate responses), ILLUSTRATIVE analysis example. Cropped. In this capture the narrow number fields clip the entered values: the cost of M-BUF is stored as 6000 but the field shows "60", and the deadline field (20 days) shows no digits. The data are intact; the display is a defect recorded in Chapter 6.](figures/fig5_screen_analysis_inputs.png)

![Figure 5.12. Decision part of the same screen after "Run analysis": the command, the criterion, and the first rows of the table of options compared. Cropped. Every number is derived from ILLUSTRATIVE placeholders.](figures/fig5_screen_analysis_decision.png)

With those placeholders the tool reports an expected delay of 5.13 days, a probability of 59.8 % of finishing after the deadline, and the command AUTHORIZE MITIGATION for the option "buffer stock plus inspection hold point" (mitigation cost INR 7,500; change in total expected cost INR -7,047 against accepting). The closest alternative is INR 130 more expensive, a gap of 0.3 %, which the tool itself describes as close. The preferred option is the same under three seeds and changes to "accept" when the delay-day cost is scaled to a quarter. This shows how sensitive the command is to its inputs, which are invented. It is not a result about any real project. Section 6.5 compares the first of these figures with an independent calculation.

### 5.12.5 Limits

The layer is a calculator over user inputs. It is only as good as the probabilities, delay ranges, costs and response effects entered, none of which this project has measured. Independence between risks is the default, though correlations can be entered. A pre-implementation review noted that the evidence base offers no masonry-specific effect sizes for any response, and the layer was therefore built so that it refuses to invent them. The distribution shape (PERT with λ = 4) has no site calibration. Whether a site manager would use the screen, or would trust its command, has not been tested.

## 5.13 Summary

The tool is a deterministic, offline register-and-matrix aid with a transparent rule base, a labelled literature tier, a guarded AI suggestion path that cannot supply numbers, and an optional cost layer that uses only the user's own numbers. Its main design decisions are to keep the engine separate from the interface, to attach a Source to every number, to prefer "not evaluable" or "not placed" over a guess, and to word outputs as ordinal or conditional. Its main design weaknesses, carried forward to Chapter 6 and Chapter 7, are the Assumption-laden class edges and thresholds, the use of one RII band on two axes, the thin evidential basis of the rules, and the absence of any evaluation with practitioners.
