# Appendix I. User guide

This guide is for a site engineer or student who wants to install the tool and work through a case. It is summarised from `README.md` and `gui/README_GUI.md` and uses the ILLUSTRATIVE example case shipped with the tool. Every number in the example is a placeholder labelled Assumption; do not read it as site data or as evidence. The step results shown here were produced by running `app.service.run_case` on the example on 2026-10-08 and agree with `python -m app.cli run`; the screen layout is described from the GUI documentation and was not re-photographed for this guide.

## I.1 What the tool does and does not do

The tool helps one engineer identify, register and rank delay risks for one brick or block masonry activity. It offers a library of 46 risks, 22 rules that read site facts you declare, a risk register in which each number carries a Source, and a 5 x 5 probability-impact matrix. It runs offline on your computer. It does not predict delays or productivity, it does not know anything about your site until you enter it, and it never turns a survey rank into a probability or a number of days. Risks you have not given numbers appear at a labelled "literature tier", which is an ordinal starting position, not an assessment. An optional cost and decision screen works only from numbers you enter.

## I.2 Install and start

**Windows.** Double-click `setup_windows.bat`. It creates a `.venv` folder, installs the requirements and starts the interface. Next time use `gui\run_gui.bat`. A built desktop program can be produced with `build_desktop_exe.bat` (a Windows executable that needs no Python on the target computer); building it was not part of this report's verification.

**Any platform.**

```
pip install -r requirements.txt
python -m gui                       # opens http://127.0.0.1:8765/
python -m gui --port 9000           # another preferred port
python -m gui --no-browser          # do not open a browser
python -m gui.qt_app                # PySide6 window instead of the browser
```

Stop the browser version with Ctrl+C in the terminal. The server listens on `127.0.0.1` only; do not expose it on a network. Command-line use without the interface:

```
python -m app.cli example > case.json
python -m app.cli run case.json --out out      # writes register.md, register.csv, result.json
python -m app.cli example-analysis > a.json    # optional decision layer, ILLUSTRATIVE
python -m app.cli analyze a.json --out out     # writes analysis.md
```

To run the tests: `pip install -r requirements-dev.txt`, then `python -m pytest` (Appendix E).

AI suggestions work offline (evidence retrieval and matching library risks). If you add an Anthropic or Google key in Settings, the tool returns guarded candidate risks with evidence IDs; the key is stored outside the project folder. The AI may propose risk names and cite evidence. It never supplies a probability, a delay, a cost or a matrix placement, and numeric fields in its answers are rejected.

## I.3 Step by step on the ILLUSTRATIVE example

Click **Load example** in the top bar (or open a case file with **Open**). A banner on every screen says ILLUSTRATIVE. The left rail has six screens.

1. **Case & Activity.** Project details, the activity name and the planned duration in working days with its Source. The example uses a planned duration of 16 working days (Assumption, ILLUSTRATIVE). Impact on the matrix is measured as a fraction of this duration, so enter your own value with its Source.
2. **Site facts & Rules.** Declare each fact as Yes, No, Unknown or a number. The 22 rules flag risks as relevant or elevated; a rule that lacks a fact is shown as not evaluable and is never guessed. Changing a fact adds any flagged risk that is missing from the register, with probability and delay left empty. Opening or loading a case adds nothing: a saved case is restored exactly. In the example, six risks are flagged elevated or relevant by the rules that fired (table below).
3. **Risk register.** One card per risk, with probability, delay range (PERT, triangular, uniform or fixed), a Source for each, status, evidence chips, and the text fields owner, early-warning sign, response type (avoid / reduce / transfer / accept), action and review date. The side panel lists the library and the AI suggestions. A risk with a missing number stays in the register, off the matrix, with a note, unless the literature seed can place it, in which case it appears as a grey dashed chip labelled "literature tier (Assumption)".
4. **Risk matrix.** Enter the four impact bin edges (fractions of the planned duration) and their Source. The 5 x 5 grid places every complete risk and a table lists probability class, expected delay if it occurs, impact class, score and level. This is ordinal prioritisation only. The example has 7 risks.
5. **Evidence.** The curated evidence records; the search reaches the whole corpus including the bulk literature harvest.
6. **Export.** Download `register.md`, `register.csv`, the case JSON, the matrix (`matrix.svg`) and `report.html`.

Top bar: case name, unsaved-changes indicator, input-problem counter, **New**, **Open**, **Save**, **Load example**, light / dark theme. Shortcuts: Ctrl+S save, Ctrl+O open, Esc closes pop-ups. A value that is present but wrong (probability outside 0 to 1, a delay with minimum above maximum, a number with no Source) is shown as a problem and the register keeps its last valid state until it is fixed.

### Result of the example (as produced by the tool)

**Table I.1.** Matrix rows for the ILLUSTRATIVE example: planned duration 16 days (Assumption), impact edges 0.02 / 0.05 / 0.10 / 0.20 of the planned duration (Assumption, ILLUSTRATIVE), probability edges 0.2 / 0.4 / 0.6 / 0.8 (Assumption, tool default), thresholds 5 / 10 / 15 (Assumption, tool default). Expected delay is the mean of the entered PERT range, (a + 4m + b) / 6. Level counts: 1 High, 5 Moderate, 1 Low. Source: `app.service.run_case` on the example case (Derived Calculation from Assumption inputs, ILLUSTRATIVE).

| Risk | p (as entered) | p class | Expected delay if it occurs (days) | Impact class | Score | Level |
|---|---|---|---|---|---|---|
| R-MAT | 0.5 | 3 | 3.50 | 5 | 15 | High |
| R-LAB | 0.35 | 2 | 2.50 | 4 | 8 | Moderate |
| R-RWK | 0.25 | 2 | 2.33 | 4 | 8 | Moderate |
| R-WX | 0.2 | 2 | 2.67 | 4 | 8 | Moderate |
| R-PLAN | 0.1 | 1 | 1.33 | 3 | 3 | Low |
| R-SAFE | 0.3 | 2 | 2.50 | 4 | 8 | Moderate |
| R-SKILL | 0.22 | 2 | 2.33 | 4 | 8 | Moderate |

**Table I.2.** Rules that fired on the example's declared facts. Source: `app.service.run_case` (rules from `data/rules_masonry.json`, Assumption).

| Rule | Flags risk | Level |
|---|---|---|
| RL-LAB | R-LAB | elevated |
| RL-MAT | R-MAT | elevated |
| RL-MAT2 | R-MAT | normal |
| RL-WX | R-WX | normal |
| RL-RWK | R-RWK | elevated |
| RL-PLAN | R-PLAN | elevated |
| RL-SKILL | R-SKILL | elevated |
| RL-WX2 | R-WX | elevated |
| RL-PACE | R-PLAN | elevated |

Reading the table: R-MAT has the highest level (High, p class 3 x impact class 5 = 15) because its entered probability and its expected delay of 3.5 days (a fifth of the planned duration or more) are the largest; the five Moderate risks all share the cell p class 2 x impact class 4. Several of those classes depend on a value sitting exactly on a class edge (R-WX has p = 0.20, which is on the first probability edge and so falls in class 2); a tiny change would move it. This is one reason the level is a prioritisation aid and not a measurement (Chapter 6).

## I.4 Working with a real activity

1. Enter your own planned duration, impact edges and Sources before anything else; replace every ILLUSTRATIVE value, and delete the example's banner text from the notes.
2. Declare the facts you know; leave "Unknown" where you do not. Rules never guess.
3. Review each flagged risk. Add risks from the library or from the AI suggestions that fit the activity; remove any that do not.
4. For every risk you care about, enter probability and delay with a Source. Use "Expert Judgment" for your own estimate, "Historical Data" for numbers from your own past activities, "User Input" for a measured or contractual value. The tool does not check that a number is sensible.
5. Fill in owner, early-warning sign, response type, action and review date. These are text and are part of the register.
6. Export the register and keep the case JSON. The exports print each number with its Source, and print the matrix settings as Assumptions.

## I.5 Optional cost, options and decision analysis

The command `python -m app.cli analyze` (and `POST /api/analyze`) runs a Monte Carlo schedule simulation, delay-cost and EMV analysis and a comparison of the responses you enter, with a command of `AUTHORIZE MITIGATION`, `ACCEPT RISK`, `NO ADMISSIBLE OPTION` or `NO RESPONSE EVALUATED`. It needs the cost of one delay day, a cost for each response and the effect of each response, all entered by you with a Source; it has no default costs or effect sizes, never uses literature-tier placements as probabilities, and words its output as "preferred under the stated criterion", never as optimal. It was added on 2026-10-08, is not in the navigation of the interface, and has been verified only as software, not against real projects. The earlier labour-productivity models are not used by the interface.

## I.6 Known limits to keep in mind

- The tool is a single-user, local program on a development-grade server.
- The probability-class edges and level thresholds are fixed assumptions; the impact edges are yours and have no default.
- The literature seed comes from general building-construction surveys; it is a starting position only. Replace it with your own numbers or with expert-survey results.
- Retrieval of evidence is lexical (word overlap), not semantic; many harvested records have only an abstract.
- The Google (Gemini) AI path was checked against the live service; the Anthropic path was not (no key was available).
- Defects listed as "needs code change" in `docs/Audit_Corrections_2026-10-08.md` section 4 may still be present.
