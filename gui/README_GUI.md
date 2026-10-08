# GUI: brick-masonry risk identification, register and matrix

A local, offline web application for one brick or block masonry activity. It helps you identify risks
(curated library, site-fact rules, guarded AI suggestions over a cited evidence corpus), keep the risk
register, and place the register on a probability x impact matrix. **The GUI computes nothing of its
own.** Every figure on screen comes from `app.service.run_case`, which runs on every edit, so there is no
Run button.

## Start

```
python -m gui                  # opens the default browser at http://127.0.0.1:8765/
python -m gui --port 9000      # another preferred port (the next free port is used if busy)
python -m gui --no-browser     # do not open a browser
python -m gui --verbose        # log every HTTP request
```

or double-click `gui\run_gui.bat`. Stop with **Ctrl+C** in the terminal. It serves on `127.0.0.1` only.

AI: with no key the tool runs in **offline mode** (evidence retrieval and matching library risks). Add an
Anthropic (Claude) or Google (Gemini) key in **Settings** (left rail, bottom) to get guarded candidate risks.
The key is stored outside the project folder. The AI proposes risks and cites evidence; it never supplies a
probability, delay or matrix placement.

## Steps (left rail)

| # | Screen | What you do / what you see |
|---|---|---|
| 1 | Case & Activity | Project details, activity name and the **planned duration** in working days (with its Source). Impact on the matrix is measured as a fraction of this duration. |
| 2 | Site facts & Rules | Declare site facts (Yes / No / Unknown, or a number) for the 22 site-fact rules. Rules flag risks as relevant or elevated; rules that lack a fact are shown as not evaluable, never guessed. Changing a fact adds any flagged risk that is missing from the register, with probability and delay left empty (Open / Load never adds anything: a saved case is restored exactly). |
| 3 | Risk register | Risk cards: probability and a delay range (PERT, triangular, uniform or fixed), each with a Source, plus status and evidence chips. Side panel: the library of 46 risks (16 of them have no survey value) and **AI suggestions**. Each card also has text-only owner, early-warning sign, response type (avoid / reduce / transfer / accept), action and review date. A risk with numbers missing stays in the register, off the matrix, with a note. |
| 4 | Risk matrix | Enter four impact bin edges (fractions of the planned duration) with their Source. A 5x5 grid places every complete risk; a table lists p class, expected delay if it occurs, impact class, score and level. Ordinal prioritisation only. |
| 5 | Evidence | Curated evidence records; search reaches the whole corpus, including the bulk literature harvest. |
| 6 | Export | Download `register.md`, `register.csv` and the case JSON. |

Top bar: case name, unsaved-changes indicator, input-problem counter, **New**, **Open** / **Save** case JSON,
**Load example** (ILLUSTRATIVE placeholders), light/dark theme. A strip under the bar summarises the register
(risks, complete, on the matrix, levels, rule-flagged and not yet in the register). Shortcuts: Ctrl+S save,
Ctrl+O open, Esc closes pop-ups.

Values that are present but wrong (probability outside 0 to 1, delay with min > max, a number with no
Source) are shown as problems and the register keeps its last valid state until they are fixed.

## API

`GET /api/health, /api/meta, /api/template, /api/example, /api/risk-library, /api/rules, /api/evidence`
(`?ids=`, `?q=`, or the curated records); `GET/POST /api/settings`, `POST /api/settings/test`;
`POST /api/validate` (always HTTP 200: `{"ok": true, "result": ...}` or `{"ok": false, "problems": [...]}`),
`POST /api/run` (422 on problems), `POST /api/suggest-risks`, `POST /api/report` (register.md),
`POST /api/register-csv` (register.csv).

### Charts on the Cost, options & decision screen
After a run the screen draws six inline-SVG charts (no library, no network; colours from the `--chart-*` tokens so light and dark themes work): (1) simulated duration histogram with P50, P90 and the deadline marked (`histogram`, `summary`); (2) two tornado charts of risks ranked by mean delay contributed (`sensitivity`) and by value at stake (`value_at_stake`); (3) event EMV per risk (`event_emv`); (4) expected total cost per option, stacked mitigation + residual, at most 10 options (Accept, the preferred option and the lowest total expected cost), the preferred one outlined and worded "preferred under the stated criterion"; (5) preferred option against cost per delay day (`decision_sensitivity`; absent when only Accept was evaluated). Each chart has an aria-label, a caption with its Derived Calculation label (and the Source of the cost per day), an ILLUSTRATIVE badge for an illustrative case, and a "Data table for this chart" disclosure. Only returned values are drawn; code in `gui/static/js/analysis_charts.js`, tests in `tests/test_analysis_charts.py`, screenshots in `report/figures/fig5_analysis_charts_{1280,800}_{light,dark}.png`.

`POST /api/analysis-charts-html` (button "charts (HTML)") returns a self-contained HTML export: matplotlib PNG charts embedded as base64, a data table under each chart, and the report text.

## Literature seed (what the matrix shows for risks without numbers)

The seed is an **importance ranking** from general building-construction surveys (RII). It is **not a probability and not a delay**. Two Assumptions turn it into a matrix cell: (1) the same RII class is used for BOTH the probability and impact axes; (2) a rule flag raises the probability class by 1 (capped at 5). Such risks are shown as a grey dashed **literature tier (Assumption)** chip, are not counted in the level totals, and the cell colour under them is not an assessed level. The seed dataset has 182 rows from 11 studies; 30 of the 46 library risks have a seed value. Agreement with the held-out surveys is weak and not statistically significant (only held-out surveys with enough overlap can be compared). Matrix colours are the same in both themes (Low #4fcf6f, Moderate #ffd93d, High #ff9626, Extreme #ff4b4b, dark ink, contrast 5.6:1 or better).

If the server cannot check the case (HTTP 500, unreadable reply) the summary strip shows the server's problem text instead of "Checking the case".

## Known limitations

- Local single-user tool on a development-grade server (werkzeug, threaded). Do not expose it on a network.
- The matrix's probability classes and level thresholds are the engine's equal-width Assumptions; impact edges
  are your input and have no default.
- Retrieval is lexical (token overlap), not semantic; many harvested records have an abstract only.
- The Gemini path has been checked against the live API; the Anthropic path has not (no key was available).
