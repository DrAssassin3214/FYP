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
| 2 | Site facts & Rules | Declare site facts (Yes / No / Unknown, or a number). Rules flag risks as relevant or elevated; rules that lack a fact are shown as not evaluable, never guessed. Changing a fact adds any flagged risk that is missing from the register, with probability and delay left empty. |
| 3 | Risk register | Risk cards: probability and a delay range (PERT, triangular, uniform or fixed), each with a Source, plus status and evidence chips. Side panel: the curated library and **AI suggestions**. A risk with numbers missing stays in the register, off the matrix, with a note. |
| 4 | Risk matrix | Enter four impact bin edges (fractions of the planned duration). A 5x5 grid places every complete risk; a table lists p class, expected delay if it occurs, impact class, score and level. Ordinal prioritisation only. |
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

## Known limitations

- Local single-user tool on a development-grade server (werkzeug, threaded). Do not expose it on a network.
- The matrix's probability classes and level thresholds are the engine's equal-width Assumptions; impact edges
  are your input and have no default.
- Retrieval is lexical (token overlap), not semantic; many harvested records have an abstract only.
- The Gemini path has been checked against the live API; the Anthropic path has not (no key was available).
