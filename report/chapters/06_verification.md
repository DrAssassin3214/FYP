# Chapter 6. Verification and Testing

This chapter reports what was checked, how, and with what result, and then states what was not checked. The checks establish that the software does what Chapter 5 says it does: that it computes the matrix cells it claims to, rejects the input it claims to reject, keeps its wording within limits, and gives the same output for the same input. They do not establish that the tool is useful to a site manager, that its probabilities or thresholds are right, or that it improves any decision. No expert evaluation, no usability study and no site trial were carried out, and Section 6.9 lists what that leaves open.

All counts in this chapter were produced by commands run on 8 October 2026 against commit 9f265f9 of the repository (working tree with the report files untracked), on Linux with Python 3.13.16. Commands and scripts are named so that the reader can repeat them.

## 6.1 Verification approach

Four kinds of evidence are used, in order of strength for the claim they support.

1. **Automated tests** (Section 6.2 to 6.3) show that specified behaviour holds for the inputs the tests choose. They are only as good as those inputs.
2. **Independent recomputation** (Sections 6.4 to 6.6) shows that the numbers the tool prints for the ILLUSTRATIVE example equal numbers obtained by a separate calculation, by hand in the text and by a second implementation of the arithmetic in `report/scripts/hand_check.py`.
3. **Robustness probing** (Section 6.7) shows how the tool behaves on malformed and hostile input. It was done by an independent QA pass and repeated for a sample of its findings in this session.
4. **Audit and review** (Section 6.8) shows what independent reviewers found wrong, and what was changed.

The ILLUSTRATIVE example is used for the worked checks because it is the only case with complete numbers. Its probabilities, delays, costs and planned duration are placeholders labelled Assumption. A match between hand calculation and tool therefore shows that the arithmetic is right. It says nothing about whether the placeholders resemble any site.

## 6.2 The automated test suite

### 6.2.1 How it was run

pytest is not installed in the system Python of the environment used for this report. It was run from the isolated environment of the `pytest` tool that was already present, with the project's dependencies on the path:

```
PYTHONPATH=/usr/local/lib/python3.13/dist-packages \
  /root/.local/share/uv/tools/pytest/bin/python -m pytest -q -rA
PYTHONPATH=... python -m pytest --collect-only -q
```

The run took 29 seconds. The result was **513 passed, 3 skipped, 0 failed** from **516 collected tests** in 17 files. The earlier project documents quote 137 passed and 3 skipped on 8 October before the committee changes (Handoff section 8), and 133 before that; the larger number now is mostly parametrised cases of the hardening tests (one test function can generate many cases) and the tests added with the committee upgrades, not 380 new behaviours.

Two further test files, `tests/test_explain.py` (7 test functions) and `tests/test_india_norms.py` (6 test functions), are not collected. `tests/conftest.py` excludes them with `collect_ignore` because they import service functions (`explain_result`, `india_norms`) of the earlier simulation, cost and decision features that the lean application no longer exposes. They are kept on disk until their removal is confirmed. These 13 test functions did not run and are not counted as passed.

The three skipped tests are in `tests/test_corpus.py` and skip on a missing optional resource: the bulk literature harvest (`data/openalex_corpus.jsonl`, not in git) and the SQLite database `data/literature.db` (not in git, built by `scripts/build_literature_db.py`). The tests that check the database against its screening log and the 3,000-record work target therefore did not run in this environment, and the corpus-size discrepancy noted in the audit (finding F08) is not tested.

### 6.2.2 Tests per file

**Table 6.1.** Tests per file: collected, passed, skipped (all failed counts are zero). Collected counts from `pytest --collect-only -q`; passed and skipped from `pytest -rA`, both run for this report. A parametrised test counts once per case. Source: command output saved under the session scratch directory; commands as in Section 6.2.1.

| File | Collected | Passed | Skipped | What it covers |
|---|---|---|---|---|
| `test_validation_hardening.py` | 140 | 140 | 0 | Input validation: non-finite numbers, booleans as numbers, bad shapes, missing Source, probability and impact edge rules, string facts |
| `test_export_api_hardening.py` | 129 | 129 | 0 | Exports and HTTP layer: CSV injection, Markdown escaping, BOM, odd bodies on every POST route, host check, guard rules G7 to G9, settings masking |
| `test_service.py` | 42 | 42 | 0 | `run_case`: example reproducibility, matrix rows, literature tier, rules in the service, register fields, exports |
| `test_engine.py` | 32 | 32 | 0 | Distribution means and variances, Monte Carlo against analytic moments, reproducibility, EMV, residual risk, constraints, audit hash |
| `test_analysis.py` | 29 | 29 | 0 | Decision layer: sections of the result, wording, input errors, deadline criterion, API routes |
| `test_legacy_hardening.py` | 26 | 26 | 0 | Earlier simulation, EMV and productivity code: bad values rejected, EMV against hand calculation, Monte Carlo mean within 3 standard errors |
| `test_options.py` | 17 | 17 | 0 | Response options: break-even targets, option generation, net benefit, command wording, seed stability, catalogue has no numbers |
| `test_settings.py` | 16 | 16 | 0 | AI key storage: outside the project, masked, never echoed, retry behaviour |
| `test_relevance_guard.py` | 14 | 14 | 0 | Guards that tie documents, data and wording to the facts (Section 6.3) |
| `test_gui_api.py` | 14 | 14 | 0 | HTTP routes of the interface |
| `test_corpus.py` | 13 | 10 | 3 | Evidence store and corpus loading; the 3 skips need data not in git |
| `test_productivity.py` | 13 | 13 | 0 | Earlier productivity models (out of scope) |
| `test_gui_settings_api.py` | 12 | 12 | 0 | Settings routes |
| `test_ai_guard.py` | 10 | 10 | 0 | Guard rules G1 to G4, audit log, promotion rules |
| `test_rules.py` | 5 | 5 | 0 | Rule firing, missing facts, priority and conflicts, consistency checker |
| `test_gui_static.py` | 3 | 3 | 0 | Static files are UTF-8 without garbled characters; opening a case does not auto-add risks; honest wording |
| `test_report.py` | 1 | 1 | 0 | Earlier Monte Carlo report |
| **Total** | **516** | **513** | **3** | |

Two things stand out. First, the two largest files are hardening tests added after audit and QA findings, so more than half of the suite is a regression guard for defects that were found and fixed (Section 6.8). Second, 40 tests (`test_legacy_hardening`, `test_productivity` and `test_report`) cover earlier code that is out of scope and not used by the interface; they pass but support no claim about the current tool. The same holds in part for `test_engine.py` and `test_options.py`, which test the simulation and decision modules; those modules are live only in the optional decision layer.

### 6.2.3 Test categories

The suite can be read as six kinds of test.

**Unit tests of the logic** (`test_engine`, `test_rules`, parts of `test_validation_hardening`). Examples: the closed-form mean of each delay distribution equals the mean from a simulation within sampling error; a value exactly on a class edge goes to the higher class; a brute-force check over a one-decimal grid of ratios agrees with exact arithmetic for the impact class (`test_m4_brute_force_one_decimal_grid_matches_exact_arithmetic`); a rule with a missing fact is not evaluable and never fires; two rules of equal priority and different levels give `conflict`.

**Integration tests of the service** (`test_service`, `test_analysis`). They run whole cases through `run_case` or `run_analysis` and check the result: that the example is reproducible, that every matrix row equals the engine's classification of the register risk, that an entered number replaces the literature tier, that a rule flag raises the probability class by one for a seeded risk only, that a risk with partial numbers stays in the register, and that every evidence ID cited by the example exists in the corpus.

**API and export tests** (`test_gui_api`, `test_export_api_hardening`, `test_gui_settings_api`). They call the Flask routes with valid, malformed and hostile bodies, and parse the exports (CSV with the `csv` module, HTML for unescaped markup, SVG as XML).

**Guard tests** (`test_ai_guard`, `test_relevance_guard`, parts of `test_export_api_hardening`). They check the AI guard rules and the document and wording guards of Section 6.3.

**Regression tests for named defects.** The hardening files name the audit item they guard: `test_h1_*` (non-finite numbers), `test_h2_*` (delay without Source), `test_m1_*` to `test_m9_*`, `test_l1_*` to `test_l5_*` and `test_qa14_*`. Each test was written after the defect was reproduced, so each one is a record that the defect existed.

**What the suite does not include.** There are no automated tests of the JavaScript interface code: `test_gui_static.py` checks encoding, wording and one behaviour of the load function by reading the source, but no browser test drives the screens. The browser behaviour was checked manually and with a Playwright pass (Section 6.7), whose scripts are not in the repository. The Qt desktop wrapper has no test in the suite; it has a self-test in the build workflow that was not run here (Section 5.11.2). There is no test of a real LLM reply for the Anthropic path (no key was available), and no coverage measurement was made, so the proportion of lines exercised is not known.

## 6.3 The relevance guard tests

`tests/test_relevance_guard.py` holds ten guards added on 8 October 2026 after the committee review. They protect the report and the interface from drifting away from the data. In this report they are cited as RG-1 to RG-10, matching the function names `test_g1_*` to `test_g10_*` in the file; they are distinct from the AI guard rules G1 to G9 of Chapter 5.

**Table 6.2.** The relevance guard tests. Source: `tests/test_relevance_guard.py`; all 14 test cases (RG-5 has two parametrised cases; RG-4, RG-6 and RG-9 have two functions each) passed in the run of 8 October 2026.

| Guard | What it asserts | Why it matters |
|---|---|---|
| RG-1 | Counts read from the data are consistent with each other: seeded plus unseeded equals the number of library risks (46), seed plus held-out studies equals the number of studies (11), the unseeded risks are exactly those with a `seed_status` note, IDs are unique | These counts are quoted throughout the report; they are not typed into the test |
| RG-2 | `README.md`, `docs/case_schema.md` and `gui/README_GUI.md` state the rule, row, study and risk counts found in the data | Documents cannot silently go stale |
| RG-3 | The 182 seed rows are frozen: a checksum of the study, factor, rii and rank fields equals the stored value | A change to a transcribed survey value fails the suite |
| RG-4 | Withdrawn wording ("validated", "predicts", "built from every factor" and others listed in Handoff section 8) does not occur in live text; the handoff mentions withdrawn wording only on lines that say it is withdrawn | Keeps the claims within what the work supports |
| RG-5 | Every number in the exports has its Source printed next to it, for the example and for a case with the whole library added | Integrity rule 2 |
| RG-6 | Legacy modules are not imported by the live application, and the interface does not load the legacy screens | Out-of-scope code cannot influence outputs |
| RG-7 | The example case stays labelled ILLUSTRATIVE in every export | Placeholders cannot be mistaken for data |
| RG-8 | Rule-base sanity: every rule is Assumption-sourced or carries evidence IDs; no pair of rules on one risk has different levels at equal priority; every fact used by a rule has a label on the facts screen; every rule targets a library risk | Rule base stays consistent with the interface |
| RG-9 | Unseeded library risks carry the `seed_status` note and have no seed rows; evidence IDs of the eight added risks exist in the corpus | The 16 unseeded risks cannot acquire a literature tier by accident |
| RG-10 | `promote` refuses a derived (AI) value as the source of p or delay; the response of `/api/suggest-risks` contains no numeric-looking key | NFR3 |

These guards test consistency, not truth. RG-3 shows that the seed rows are unchanged since the row-level check against the printed papers; it does not re-check them. RG-4 shows that listed phrases are absent; a new over-claim in different words would pass.

## 6.4 Hand calculation against the tool: the matrix

### 6.4.1 The example

The ILLUSTRATIVE example (`app.service.example_case`, also `examples/example_case.json`) has a planned duration T₀ = 16 working days, impact edges (0.02, 0.05, 0.10, 0.20), and seven risks with PERT delays. All values are Assumptions. The calculation uses the formulas of Section 5.6: E[D] = (a + 4m + b)/6, r = E[D]/T₀, c_p from the edges 0.2, 0.4, 0.6, 0.8, c_i from the impact edges, s = c_p c_i, and the level thresholds 5, 10, 15.

### 6.4.2 By hand, for R-MAT

R-MAT has p = 0.50 and a delay range a = 1, m = 3, b = 8 days.

- E[D] = (1 + 4 × 3 + 8)/6 = 21/6 = 3.5 days.
- r = 3.5/16 = 0.21875, which is at least the fourth edge 0.20, so the impact class is c_i = 5.
- p = 0.50 is at least 0.4 and below 0.6, so the probability class is c_p = 3.
- s = 3 × 5 = 15, and 11 ≤ 15 ≤ 15 gives the level High.

For R-LAB (p = 0.35, a/m/b = 1/2/6): E[D] = (1 + 8 + 6)/6 = 2.5; r = 0.15625 lies in [0.10, 0.20), so c_i = 4; p = 0.35 lies in [0.2, 0.4), so c_p = 2; s = 8, Moderate. R-PLAN (p = 0.10, a/m/b = 1/1/3): E[D] = (1 + 4 + 3)/6 = 1.3333; r = 0.08333 lies in [0.05, 0.10), so c_i = 3; p = 0.10 is below 0.2, so c_p = 1; s = 3, Low. The remaining four risks are computed in the same way in Table 6.3.

### 6.4.3 All seven risks

**Table 6.3.** Hand calculation and tool output for the seven risks of the ILLUSTRATIVE example. All inputs are placeholders labelled Assumption. "Hand" columns come from the formulas of Section 5.6 applied with a separate script (`report/scripts/hand_check.py`, which does not call `app.engine`); "Tool" columns come from `app.service.run_case`. Source: `report/tables/hand_check_output.txt`, produced by running the script.

| Risk | p | a / m / b (d) | E[D] hand (d) | r = E[D]/16 | c_p | c_i | s | Level (hand) | Tool: E[D], c_p, c_i, s, level |
|---|---|---|---|---|---|---|---|---|---|
| R-MAT | 0.50 | 1 / 3 / 8 | 3.5000 | 0.2188 | 3 | 5 | 15 | High | 3.5000, 3, 5, 15, High |
| R-LAB | 0.35 | 1 / 2 / 6 | 2.5000 | 0.1562 | 2 | 4 | 8 | Moderate | 2.5000, 2, 4, 8, Moderate |
| R-RWK | 0.25 | 1 / 2 / 5 | 2.3333 | 0.1458 | 2 | 4 | 8 | Moderate | 2.3333, 2, 4, 8, Moderate |
| R-WX | 0.20 | 1 / 2 / 7 | 2.6667 | 0.1667 | 2 | 4 | 8 | Moderate | 2.6667, 2, 4, 8, Moderate |
| R-PLAN | 0.10 | 1 / 1 / 3 | 1.3333 | 0.0833 | 1 | 3 | 3 | Low | 1.3333, 1, 3, 3, Low |
| R-SAFE | 0.30 | 1 / 2 / 6 | 2.5000 | 0.1562 | 2 | 4 | 8 | Moderate | 2.5000, 2, 4, 8, Moderate |
| R-SKILL | 0.22 | 1 / 2 / 5 | 2.3333 | 0.1458 | 2 | 4 | 8 | Moderate | 2.3333, 2, 4, 8, Moderate |

All seven rows agree: expected delay to within 10⁻⁹ days, and class, score and level exactly. The tool's summary reports one High, five Moderate and one Low. The p = 0.20 of R-WX is exactly on the edge 0.2 and goes to class 2, which is the lower-edge-inclusive convention of Section 5.6.3; this case is a deliberate check of the convention. The test `test_m4_exact_edge_goes_to_the_higher_class` guards the same behaviour.

What this check shows is limited. It confirms the arithmetic and the edge convention. The classes and levels depend on the impact edges (0.02 to 0.20), the probability edges and the score thresholds, which are Assumptions; with other edges the same seven risks would be classed differently. The sensitivity of the levels to those choices was examined in Chapter 4 and is not repeated here.

### 6.4.4 Rules for the example, by hand

The example's 28 facts (Chapter 5, Figure 5.6) fire nine rules. By hand, with the facts of the example (required workers 6, available 5, material stock 2 days, lead time 6 days, planned duration 16, monsoon overlap Yes, external walls Yes, schedule compressed Yes, planned daily output 10, achieved 8, prior rework Yes, skilled masons short Yes):

- RL-LAB fires (6 > 5), RL-MAT fires (2 ≤ 6) at priority 1, RL-MAT2 fires (2 < 16) as `normal`, RL-WX fires as `normal`, RL-RWK fires, RL-PLAN fires, RL-SKILL fires, RL-WX2 fires (monsoon and external walls) at priority 1, RL-PACE fires (10 > 8).
- Thirteen rules do not fire: RL-TOOL (no tools shortage), RL-HGT (work at height but scaffolding is ready), RL-PAY, RL-DES, RL-FRONT (work front ready), RL-VT (floor 0 is below 1), RL-SCAF (scaffolding ready), RL-MORT (8 > 5 days), RL-GPAY, RL-OPEN (all three items ready), RL-FEST, RL-FEST2, RL-HEAT.

On R-MAT, RL-MAT (elevated, priority 1) and RL-MAT2 (normal, priority 0) both fire, and the higher priority wins, so R-MAT is `elevated`, not `conflict`. On R-WX, RL-WX (normal, 0) and RL-WX2 (elevated, 1) give `elevated`. The tool reports the same nine fired rules, no rule not evaluable, and six elevated risks (R-LAB, R-MAT, R-WX, R-RWK, R-PLAN, R-SKILL), matching the "rule-flagged 6" in the key-figure strip of Figure 5.8. R-SAFE has no flag, as its scaffolding is ready.

### 6.4.5 Literature tier, by hand

The tier is not used by the example, whose risks all have entered numbers. To check the tier arithmetic, a case with R-MAT entered and R-TOOL and R-WX left without numbers was run, with `tools_shortage` set to true and the other facts as in the example. The seed table (`app.literature_seed.seed_table()`) gives R-TOOL a mean RII of 0.7528 (study means M01 0.7455 and A02 0.760, the mean of the two study means) at rank 12 of 30, and R-WX a mean RII of 0.6934 (A14 0.6528, M01 0.764, A02 0.700, M06 0.6567) at rank 24.

- R-TOOL: tier = 5 − ⌊5 × 11/30⌋ = 5 − 1 = 4. It is flagged elevated by RL-TOOL, so c_p = min(5, 4 + 1) = 5 and c_i = 4, giving score 20.
- R-WX: tier = 5 − ⌊5 × 23/30⌋ = 5 − 3 = 2. RL-WX2 (elevated, priority 1) beats RL-WX (normal), so c_p = 3 and c_i = 2, giving score 6.

The tool reports exactly these cells and marks both as "literature tier (Assumption)" with `raised_by_rule` true. Its level totals count only R-MAT (High), as the specification requires: the seeded risks do not enter the High, Moderate or Low counts even though their cells carry a colour. Band membership also holds in the data: the 30 seeded risks fall six into each tier (Counter of tiers 1 to 5: 6, 6, 6, 6, 6). Both the 20 and the 6 are cell positions produced by two Assumptions (one RII band on both axes, +1 for a flag), and not assessments of those risks.

## 6.5 Independent check of the decision layer

The decision layer is checked on the ILLUSTRATIVE analysis example, again with placeholders. Two kinds of check are possible: closed-form quantities that can be computed by hand, and simulated quantities that need an independent simulation.

**Closed-form: expected delay and event EMV.** The expected total delay of independent additive risks is the sum of p_i E[D_i]:

0.50 × 3.5 + 0.35 × 2.5 + 0.25 × 2.3333 + 0.20 × 2.6667 + 0.10 × 1.3333 + 0.30 × 2.5 + 0.22 × 2.3333 = 1.75 + 0.875 + 0.5833 + 0.5333 + 0.1333 + 0.75 + 0.5133 = **5.1383 days**.

At INR 8,000 per delay day the sum of event EMVs is 5.1383 × 8,000 = **INR 41,106.67**. The tool's event EMV rows sum to INR 41,106.67, equal to the cent.

**Simulated: expected delay.** The tool's 10,000-run simulation with the default seed gives an expected delay of 5.1323 days with a standard error of 0.0334, which is 0.18 standard errors below the hand value. A second implementation written for this check (`hand_check.py`, own beta sampler, own random generator) with 4,000,000 runs gives 5.1401 days (standard error 0.0016), 1.1 standard errors above the hand value and consistent with it. The tool with 200,000 runs gives 5.1521.

**Simulated: probability of any delay.** Every risk, if it occurs, adds at least one day, so the probability that the activity finishes late is 1 − ∏(1 − p_i) = 1 − 0.5 × 0.65 × 0.75 × 0.8 × 0.9 × 0.7 × 0.78 = **0.9042**. The tool's default run reports 0.8975, 0.0067 below, which is 2.3 standard errors of a proportion at 10,000 runs and therefore looks like a sampling fluctuation but needs a check. Six other seeds give 0.9084, 0.9037, 0.9039, 0.9028, 0.9037 and 0.9092, and 200,000 runs give 0.9036, all in agreement with 0.9042. The seed 12345 simply happens to be a low draw for this quantity. This is the reason the tool shows the number of runs, the seed and standard errors, and why a result should not be read to more digits than the sampling error allows.

**Deadline and cost.** The probability of exceeding the 20-day deadline and the expected cost (which includes the liquidated-damages term) have no closed form here, because they depend on the distribution of the sum. The tool reports P(T > 20) = 0.598 and an expected cost of INR 50,821 at 10,000 runs. The independent 200,000-run simulation gives 0.6025 and INR 50,929. The 200,000-run tool run gives 0.6041. The two simulators agree to within about 0.5 % on the cost and 0.5 percentage points on the probability, which is within the sampling error of the 10,000-run result. As a consistency check on the liquidated-damages term, the expected cost minus 8,000 × 5.1323 = INR 41,058 leaves about INR 9,763, which is the expected liquidated damages 5,000 × E[max(T − 20, 0)], so E[max(T − 20, 0)] is about 1.95 days; this is a derived consistency figure and was not computed independently.

**Decision command.** The command (AUTHORIZE MITIGATION with "buffer stock plus inspection hold point") rests on the simulated cost of 22 admissible options and was not recomputed by hand. What was verified is that the preferred option does not change with the seed (three seeds), that the repository's tests compare the net benefit of a response with the simulated comparison when the cost is linear (`test_net_benefit_agrees_with_simulated_comparison_when_cost_is_linear`), and that the break-even targets agree with hand checks (`test_break_even_targets_hand_checked`). The gap between the first and second option is 0.3 % of total expected cost, smaller than a difference that the sampling error of a 10,000-run simulation would make dependable by itself; the tool reports the gap for that reason. The result is a demonstration of the arithmetic on placeholders and not a recommendation about any activity.

## 6.6 Reproducibility and determinism

Repeating the same case gives the same output. In the QA run, six cases were each sent 96 times concurrently, in forward and reversed order, and the hashes of `/api/run` and of all four exports were identical across repetitions; no server state carried between requests. The test `test_example_case_builds_the_register_and_matrix_and_is_reproducible` and `test_result_is_reproducible_and_input_is_not_modified` give the same check in the suite. The Monte Carlo layer is reproducible for a given seed and number of runs, as the hand check above shows by the stable 12345-seed values, and the result of a change of seed is shown, not hidden.

## 6.7 Robustness and fuzz testing (QA report)

### 6.7.1 What the QA pass did

An independent QA pass on 8 October 2026 tested the interface and service with scripted fuzzing and a real Chromium run. The report is at `/tmp/claude-0/-home-claude-fyp/b6e485db-2d31-5ab7-a4a5-10d8b255e54b/scratchpad/qa/qa_report.md`, and the scripts it names (`fuzz.py`, `fuzz2.py`, `probe*.py`, `det.py`, `b1.py` to `b4.py`) are in the same session directory, not in the repository. The pass covered API fuzzing of every route with empty, malformed, wrongly typed and oversized bodies; export checks; determinism; the settings store; the command line; a Chromium run through all screens, themes and widths with XSS payloads in every text field; and a static review. The suite at that time had 137 passed and 3 skipped.

What it found to be sound is recorded in the report: all POST routes returned 422 or `ok:false` for empty bodies, bad JSON, wrong content type and list or null bodies (except two routes, defect 6 below); a 30 MB body returned 413; 5,000 risks validated in 0.4 seconds and 1.2 MB names were handled by all five exports; probabilities outside [0, 1] in object form, reversed delay ranges, negative delays, bad planned durations, duplicate IDs and bad impact edges were all rejected with clear messages; CSV parsed with 17 columns on every row at that time; the SVG was well-formed; the HTML report contained no raw script or image tags; path-traversal strings returned 404; the register was identical after save and reopen of the unmodified example; and none of the XSS payloads executed on any screen or in the problem list.

### 6.7.2 Defects found, and their status

The QA report listed 17 defects. They were reported at a commit before the committee upgrades; the table gives the status found when selected items were re-probed in this session on the current code, with the test that now guards each.

**Table 6.4.** QA defects and their status. "Re-probed" means the reproduction of the QA report was repeated in this session against the current code (command output not saved to a file); "test" names the guard in the suite. Source: QA report, section "Defects"; probes run on 8 October 2026.

| # | Severity | Defect (QA report) | Status on current code |
|---|---|---|---|
| 1 | medium | Opening a saved case re-added a rule-flagged risk the user had deleted | Fixed: `test_load_case_does_not_auto_add_risks` in `test_gui_static.py` (checks the source of the load function) |
| 2 | medium | Non-string names and non-object `activity` gave HTTP 500 | Re-probed: now `ok:false` with "activity.name must be text, not int" and "activity: expected an object"; `test_m6_non_string_names`, `test_validate_never_returns_html_for_odd_case_shapes` |
| 3 | medium | CSV formula injection | Re-probed: cell now written as text with a leading apostrophe; `test_csv_cells_starting_with_formula_chars_are_neutralised` |
| 4 | medium | Invalid bare `p` (-1, 1.5, "abc") silently treated as not entered | Re-probed: `p = -1` gives "expected an object with value and source"; `test_m2_bare_probability_value_rejected` |
| 5 | low-med | `register.md` table broken by `\|` or newline in names | Re-probed: pipe escaped, newline replaced; `test_markdown_table_escapes_pipes_and_newlines` |
| 6 | low-med | `/api/suggest-risks` and `/api/settings/test` returned HTML 500 for non-object bodies | Re-probed: HTTP 422; `test_settings_test_and_suggest_reject_wrong_types` |
| 7 | low | Garbled characters ("Â·", "â€¦") in `app.js` | Fixed: `test_static_files_are_utf8_without_mojibake` |
| 8 | low | NaN, Infinity and booleans accepted as numbers | Re-probed: "must be a finite number"; boolean gives "must be a number, not true"; `test_h1_*`, `test_m1_booleans_are_not_numbers` |
| 9 | low | Case with bad types left the screen at "Checking the case..." with the cause hidden | Same validation as 2; screen behaviour not re-probed in a browser |
| 10 | low | Export screen overflowed at 800 px | Handoff section 9 records a screenshot check at 800 px with no overflow; not re-probed here |
| 11 | low | Deeply nested JSON gave HTML 500 | Re-probed: HTTP 422 with a JSON body; `test_unhandled_exception_becomes_json_500`, `test_every_post_route_returns_clean_json_error_for_odd_bodies` |
| 12 | low | CLI printed tracebacks for bad files | Re-probed for a missing file: one-line message; `test_cli_friendly_errors` |
| 13 | low | CSV had no BOM | Fixed: the HTTP route and the CLI encode as `utf-8-sig`; `test_register_csv_endpoint_has_bom_and_is_parseable`, `test_cli_writes_csv_with_bom` |
| 14 | low | Unknown evidence IDs accepted without warning | Re-probed: a warning is given; `test_qa14_unknown_evidence_ids_are_warnings_not_errors` |
| 15 | info | Masked key revealed short keys; any Host header accepted | Fixed: `test_masked_key_never_reveals_a_short_key`, `test_host_header_is_checked` |
| 16 | info | Dead JavaScript screens shipped; dark-theme level colours differ from the specified values | Dead-code part guarded by RG-6; dark-theme colours not re-checked here |
| 17 | low | Label `for` attributes missing; one select text clipped; toast uses `innerHTML` for a few server strings | Not re-checked; treat as open |

Fourteen of the seventeen were re-probed or have a named guard test that passed; items 9, 10, 16 (dark-theme part) and 17 were not re-checked in this session. A new display defect was found while capturing the screenshots for Chapter 5 and is not in the QA report.

### 6.7.3 A defect found in this verification

On the "Cost, options & decision" screen at a viewport width of 1280 px, the number fields for the response costs and the deadline are too narrow for their values. A measurement in the page shows the deadline field (value 20) with a client width of 20 px and a content width of 41 px, and the cost fields (value 6000) 37 px wide against 56 px of content, so the digits are cut off (Figure 5.11 shows "60" for 6,000 and an empty-looking deadline). The stored values are correct and are the ones used in the analysis; the display misleads the user about what is entered. This is a usability defect in a part of the tool that decides on money. It is not fixed, and it is listed with the known defects below.

### 6.7.4 Independent validation and bug testing, 9 October 2026

A further check was made on 9 October 2026 against the repository head. Its references were built without reading the tool's output: closed-form formulas; an exact distribution of the project duration by grid convolution (step 0.005 days, fast Fourier transform); a 20-million-draw simulation in plain numpy; and a bivariate-normal probability for the occurrence correlation. The inputs were the ILLUSTRATIVE example (planned duration 16 days, deadline 20 days, delay cost 8,000 INR per day, liquidated damages 5,000 INR per day, seven risks, six candidate responses); these are placeholders, so the checks show that the arithmetic is right, not that the numbers describe a site. The scripts, their first-run outputs and their post-fix re-runs are in `report/scripts/validation_2026-10-09/`.

**Test count.** The 513 passed quoted in Section 6.2 and Appendix E is the run of 8 October. At the repository head on 9 October, before any fix, the suite gave 522 passed and 3 skipped, because a file of nine chart tests (`test_analysis_charts.py`) had been added. After the fixes below it gives 554 passed and 3 skipped (557 collected, 0 failed), including 32 new regression tests in `tests/test_validation_fixes.py`. Table 6.1 and Appendix E Table E.1 keep the 8 October run; Table E.3 gives the later one.

**Table 6.5.** Results of the 9 October validation, before and after the fixes. Source: `report/scripts/validation_2026-10-09/` (Derived Calculation from the script outputs).

| Test set | Checks | Passed before | Passed after | Cause of the failures before |
|---|---|---|---|---|
| Hand and exact calculation (`v1`) | 242 | 239 | 240 | Two P90 differences of 0.049 and 0.051 days at n = 200,000 (sampling noise, below); one example file out of date (F6, fixed) |
| Command-line, API, front-end and packaging flows (`v2`) | 86 | 79 | 85 | Six failures of `analyze` on a bad file (F1, fixed); one wrong expectation of the test script |
| Edge cases, wrong-shape inputs, performance (`v4`) | 85 | 68 | 83 | n = 1 (F4) and 14 wrong-shape inputs (F2, F3), all fixed; two wrong expectations of the test script |
| Fuzzing (`v3`) | 7,700 mutated inputs | 12 unhandled errors | 0 | Wrong-type containers and mixed-type evidence ids in the analysis (F2, F3) |
| Invariants on random valid cases (`v3`) | 140 | 140 | 140 | None |

**What agreed.** For all ten distribution shapes tried (PERT with the mode at either end and with lambda = 6, triangular, uniform, fixed), the tool's mean and variance equalled the closed form to six decimals and a numerical integral. The event expected monetary value, p x E[D] x 8,000, equalled the hand value for all seven risks; the total expected delay was 5.13833 days (variance 10.79384) and the probability of any delay 0.90418 by hand and by tool. The classification into the 5 x 5 matrix matched on the seven example risks and on an exhaustive grid (0 of 20,010 probability-class and 0 of 20,004 impact-class mismatches, 0 of 25 level mismatches); the independent rule evaluator fired the same 7 of 22 rules; and the literature seed re-ranked into five classes of six with no mismatch. The Gaussian-copula joint probability agreed with the bivariate-normal value to within 0.0003 at correlations of -0.5, 0, 0.6 and 0.95. The six per-response net benefits agreed to the rupee.

The exact distribution gives, for accepting the risk, a P90 duration of 25.568 days, a probability of finishing after day 20 of 0.6019 and an expected cost of 50,792.7 INR. At n = 10,000 and seed 12345 the tool gave 25.638 days, 0.5981 and 50,821 INR, which are the figures already printed in `report/tables/hand_check_output.txt` and reproduced by the current code.

**Table 6.6.** The five lowest total expected costs among the 23 options, from the exact distribution (INR). The tool chose the same first option at n = 10,000 and n = 200,000. Source: `v1_output.txt` (Derived Calculation).

| Option | Total expected cost (INR) |
|---|---|
| O-M-BUF+M-QC | 43,992 |
| O-M-BUF+M-COV+M-QC | 44,180 |
| O-M-BUF | 45,008 |
| O-M-BUF+M-COV | 45,163 |
| O-M-SUP+M-QC | 46,808 |

The gap between the first and second option is 187.7 INR, which is small against the cost scale: the choice between them is not firm, and the tool's seed-stability check exists for this reason. When the delay cost was scaled from 0.25 to 4 times, the tool's preferred option equalled the exact optimum at every scale (accept at 0.25; O-M-BUF+M-QC from 0.5 to 1; O-M-BUF+M-COV+M-QC from 1.5 to 4).

**The two P90 differences.** At n = 200,000 the exact P90 duration lay 0.049 and 0.051 days outside the tool's 95% interval for two options. A 20-million-draw reference and a test over 100 independent seeds found no bias in the P90; over 200 seeds of 10,000 draws the mean z-score was -0.037 (expected 0, standard error 0.07) and the interval covered the exact mean in 93.5% of runs. One miss in 23 options at 95% is expected by chance, and the largest option-cost z-score at n = 200,000 was 2.97 for one option (1.04 with a second seed). These are treated as sampling noise, not defects.

**Defects found and fixed.** Six defects were found. None changed a number for a valid case; all concerned the handling of invalid or extreme input. They are fixed on branch `fix/validation-f1-f6`.

**Table 6.7.** Defects of the 9 October validation. Source: `report/scripts/validation_2026-10-09/`; regression tests in `tests/test_validation_fixes.py`.

| ID | Where | Problem found | Fix | Status |
|---|---|---|---|---|
| F1 | `app/cli.py`, `analyze` | A missing, empty, invalid, UTF-16, binary or folder case file ended in a Python traceback (6 of 6 cases); `run` handled the same files cleanly | `analyze` uses the same loader and error handling as `run` | Implemented and tested |
| F2 | `app/analysis.py` | A wrong-type container (a number or true for `mitigations`, `options`, `secondary_risks`; a number or list for `constraints`, `simulation`; a number for `simulation.correlation`) raised an unhandled error; 14 of 19 shapes | Each container is type-checked and reported as a case problem | Implemented and tested |
| F3 | `app/analysis.py`, `app/engine/decision.py` | Mixed-type or nested evidence ids failed when sorted; a bare string was split into characters | Ids are converted to text; a bare string is one id | Implemented and tested |
| F4 | `app/engine/simulation.py`, `convergence()` | For n below 10 the checkpoints were empty; n = 1 raised an error | At least one draw per checkpoint | Implemented and tested |
| F5 | `app/engine/simulation.py`, `simulate()` | Two risk ids with the same CRC32 would share one random stream and become perfectly correlated (probability about 2 x 10^-7 for 46 risks; none in the library) | The simulation refuses such ids and asks for a rename. The hash was not changed, because that would change every seeded result in this report | Implemented and tested |
| F6 | `examples/example_analysis_case.json` | The file differed from the function that generates the example | Regenerated; a test compares the two | Implemented and tested |

One limit was documented and not changed (F7): automatic option generation stops at combinations of three responses and 40 options, and the report prints this when it applies. In a stress case an explicitly entered seven-response option cost 11,226 INR against 60,068 INR for the best automatic option.

**What this did not cover.** The Qt window and the Windows executables were not run, because PySide6 could not be installed in the environment; the browser front end was checked for syntax and references, not operated by a person; the legacy productivity and India-norm modules had a light check only; and no coverage tool was available. This is verification of the software. It is not validation against a site, and it does not change the findings of Section 6.10.

## 6.8 Audit findings and what was corrected

### 6.8.1 The audit

Before the committee upgrades, a research-methods audit of the repository (30 findings, F01 to F30), a row-level check of the literature seed against the printed papers (17 findings, V-prefixed), and an engine audit (3 high, 10 medium and 14 low findings, H, M and L) were carried out. `docs/Audit_Corrections_2026-10-08.md` lists each with its status. The status tags in the file (a finding can carry two) show that, of the 30 research findings, 19 were fixed in documents, 5 in data, 12 needed a code change when the file was written, and 10 were left as decisions for the supervisor.

### 6.8.2 The main result: the data were right, the claims were not

The row-level check compared all 182 RII values and ranks in `data/literature_seed.json` with the printed papers and found them all to match. No row transcribed from M01 (28 of 28 table rows), M06 (40 of 40), A14 (as entered) or M10 (33 of 33 Table 7 rows) was missing. What was wrong was metadata, notes and wording. This finding supports the reliability of the transcription; it does not extend to the mapping of survey items to library risks, which is a judgement (finding F12), and for which no second coder or agreement statistic exists. Two further entries, A11 and P1-23 (listed under "other indices" in the seed file, not used in the seed), were not verified against PDFs because the files were not on disk.

### 6.8.3 Statistical findings that were corrected

The audit found the following problems in what had been said about the literature seed. Each was corrected in the documents; the scripts that generate some of the old figures were not all changed (Audit_Corrections section 5).

- **Circular agreement figures** (F01). The agreement of the pooled ranking with the seed (rho 0.73) included the seed studies themselves. The held-out-only values are rho 0.08 (n = 22, p = 0.73) for the pooled rank against the seed and 0.09 (p = 0.70) for the standardised pooled score. The circular values are withdrawn.
- **Over-claim of validation** (F05). "Validation", "out-of-sample test" and "predicts the order of study X" were withdrawn. The leave-one-study-out comparisons against the seed give rho 0.09 (M01, p 0.76), 0.37 (A02, p 0.29), 0.64 (M06, permutation p 0.066) and 0.60 (A14, n 4); these are seed studies, not held-out ones. For the three held-out studies M15, M10 and M14 the Holm-adjusted p are 0.13, 0.48 and 0.55. The proper description is an agreement check that is weak, low-powered and inconclusive.
- **Same band on both axes** (F02). Using one class on both axes squares the rank: 12 of the 30 seeded risks fall in the Extreme level and none in High. The use was kept as a labelled Assumption and the seeded cells were demoted to a "literature tier" display (Section 5.7).
- **Subset claims** (F03). Only 5 of the 39 factors of A14 were entered, so "built from every factor" was withdrawn and the subset stated.
- **Post-hoc finding** (F09). "Weather is rated lower than the rest" (p = 0.049) was item-level and post hoc; the study-level Kruskal-Wallis p was 0.25. It was withdrawn.
- **Kendall W** (F10). W = 0.400, permutation p = 0.153 (chi-square approximation 0.156; four studies, six risks) is no evidence of agreement and was reworded.

These are findings about the evidence behind the tier, discussed in Chapter 4. They are included here because the tier is a feature of the tool and its description in the interface changed as a result.

### 6.8.4 Engine and QA findings fixed in code

After the committee review the code changes in Audit_Corrections section 6 were made and tests added. Re-probing on the current code in this session (Section 6.7 and the checks below) shows that most items listed as "needs code change" in sections 4 and 5 of the audit file are now rejected or handled, although those sections of the file were not updated. The statuses found were:

- H1 non-finite numbers: a NaN planned duration is rejected with "must be a finite number". The audit's remaining point, the command line writing invalid JSON for NaN, was not re-probed.
- H2 delay without Source: rejected ("source is required"). Previously it was silently labelled Expert Judgment.
- M1 booleans, M2 out-of-range probability without a delay, M5 string facts, M6 malformed shapes, M9 edge count (six edges now rejected, "exactly four numbers"), L1 (a conflicting planned-duration fact is rejected), L4 (a string `use_literature_seed` is rejected): re-probed, all handled.
- M3, partly entered numbers: a risk with only p entered stays in the register with the entered p kept, is placed from the literature seed if it has a seed value, and carries a note that the p is not used for placement until the delay is entered. This is a documented design choice and not a defect.
- L5, a uniform distribution without `m`, is accepted, as intended: uniform uses only a and b.
- M4, rounding of values exactly on an edge: fixed with the 10⁻⁹ relative tolerance on both axes, with the brute-force grid test.
- M7, the unenforced sentence "No number here was produced by AI": replaced (Section 5.8.3).

The deferred items, which remain open, are in Section 6.9.

## 6.9 Known defects and deferred items

This section lists what is known to be wrong or unfinished, so that nothing in the earlier sections is read as completeness.

**Known defects**

1. The number fields of the "Cost, options & decision" screen clip their values at 1280 px (Section 6.7.3).
2. QA items 9, 10, 16 (dark-theme colours) and 17 (label associations, one clipped select, `innerHTML` in a few toasts) were not re-checked, and item 17 is treated as open.
3. The stale sections 4 and 5 of `docs/Audit_Corrections_2026-10-08.md` still list items as needing code changes that the code now handles. The document describes a state before the committee changes and was only extended in its section 6. The report does not rely on those sections for status.
4. The scripts that generate corpus statistics (`scripts/corpus_statistics.py`, `scripts/stats_corpus.py`) still print the old margin-of-error and N sentences, so re-running them overwrites the corrected documents (F19, F20). The statistics scripts still compute the circular agreement figures (F01, F21), and still use the t-based p-value for two studies where a permutation p is recommended (F11).
5. The three corpus sizes (21,902 / 5,214; 17,788 / 3,975; 11,599 / 3,550) have not been reconciled (F08), and the test that would compare the database with its screening log is skipped in this environment.
6. The Windows executables and the Qt desktop window were not built or run in this verification (Section 5.11.2).
7. Retrieval is lexical; no test measures how good the retrieved records are, and the guard is pattern-based (Section 5.8.4).
8. The `explain` module with guard rule G6, and 13 test functions of the earlier decision features, are not exposed or run.
9. Automatic option generation stops at three responses and 40 options (F7, Section 6.7.4); the user can enter larger options by hand.

**Deferred decisions** (Audit_Corrections section 6 and Handoff section 9): an event-or-condition tag on library risks; merging and removing risks (R-TRN into R-SKILL, R-OVT with R-FAT, removal of R-PRD), which would change the seed mapping and every band; renaming risks into site language; the uncoloured-tier display and dropping the +1 step; entering the 34 omitted A14 factors; a second-coder check of the mappings (F12); handling of the truncated M01 table (F13); updating the stale `existence_evidence` of core risks (F16); recomputing M14 on its stated scale (V-M14); the sensitivity table of thresholds in the interface; the title-versus-scope decision (F07); the real title of HAS25 and the details of A15 (V-A15, V-HAS25).

## 6.10 What was not done

The verification stops where the evidence stops. The following were not done, and no statement in this report depends on them.

- **No expert evaluation.** No expert survey was run and no expert reviewed the library, the rules, the thresholds or the response catalogue. The statements that a rule or risk is "relevant" rest on literature records and on the team's judgement, not on practitioner confirmation. The rules are labelled Assumption with Low or Moderate confidence for this reason.
- **No usability study.** No site manager or engineer used the tool. The claims about the interface (no free-text fact fields, plain error messages, Source badges) describe its design; whether they work for users is untested. The defect in Section 6.7.3 would probably have been found by even a short session.
- **No site data and no calibration.** No project data were collected, so nothing in this chapter shows that the tool's classes or its decision layer agree with what happened on any project. No accuracy figure for any real site exists or is claimed.
- **No validation of the thresholds or the tier.** The probability edges, score thresholds and tier construction are Assumptions. Their effect was explored by sensitivity analysis (Chapter 4), which shows how much the output depends on them and not that any setting is correct.
- **No inter-rater check of the risk mapping,** no second coder, no kappa.
- **No test of AI usefulness or of the Anthropic path.** The guard blocks numbers; whether suggestions improve identification was not tested, and the Anthropic client was not run against the live service.
- **No code coverage measurement and no browser test suite in the repository.**
- **No penetration test or security review beyond the QA probes.** The tool is for a single user on one machine and should not be exposed on a network.

## 6.11 Summary

The automated suite passes (513 passed on 8 October and 554 passed on 9 October, after the fixes of Section 6.7.4; 3 skipped for missing optional data, 0 failed), but more than half of it guards defects that were found and fixed, and under a tenth covers out-of-scope code. For the ILLUSTRATIVE example, an independent calculation reproduces every matrix cell, the nine fired rules, the tier arithmetic and the closed-form delay and EMV, and a second simulator agrees with the Monte Carlo layer within sampling error. A further independent validation on 9 October (Section 6.7.4) reproduced the closed-form figures and the exact option costs, and found six input-handling defects, now fixed. Fuzz and QA probing found 17 defects, most of which are now fixed and guarded by tests, and this verification found one more, a display defect in the decision screen. The audit confirmed that the transcribed survey values match the papers and corrected a set of over-claims about what the seed shows. The tool has not been evaluated by experts or users, has not been run on any real project, and its Windows builds were not exercised here; those gaps limit what can be concluded about its worth, and they are the main limitations carried into Chapter 7.
