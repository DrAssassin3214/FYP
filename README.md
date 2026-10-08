# FYP

Framework for brickwork labour-productivity and delay-risk prediction using managerial factors in
selected Indian building projects (NICMAR final year project). The official title describes the earlier,
larger scope; the current scope is below.

**Current scope (since 2026-09-28):** an offline decision-support tool for delay risk in one activity,
brick/blockwork masonry: risk **identification** (risk library of 46 risks, 22 site-fact rules, evidence-cited AI
suggestions) -> risk **register** -> **5x5 probability-impact matrix** -> exports (report.html, matrix.png/svg,
register.md/csv, case JSON), with a local web GUI. Risks without entered numbers are placed on the matrix
at a **labelled literature tier (Assumption)** from the **literature seed**: relative importance index (RII) values from published surveys (182 rows from 11 studies, 5 of them seed studies), turned
into an ordinal band for 30 of the 46 library risks; the other 16 have no survey value and stay off the matrix until you enter numbers. An RII measures importance, not probability or days of delay, so the seed is an
ordinal starting position and an Assumption of this tool, not a validated prediction; replace it with
expert-survey and site data. See `docs/Project_Handoff_Summary.md` sections 8 and 9 for the limits and the 2026-10-08 committee upgrades.

**Out of scope and not in the UI:** the earlier Monte Carlo schedule simulation, the expected-monetary-value
(EMV) decision layer, mitigation decisions and the labour-productivity models. That code is still in
`app/` and `examples/` (unused by the interface) and is not part of the current deliverable.

## Layout

| Folder | Contents |
|---|---|
| `app/` | Rules, risk matrix, literature seed, AI evidence layer, reporting, service API (also legacy, unused code: simulation, EMV, decision, productivity models) |
| `gui/` | Local offline GUI, as a web page (`python -m gui`) or a PySide6 desktop window (`python -m gui.qt_app`); see `gui/README_GUI.md` |
| `data/` | Rules, risk library, productivity models, India labour norms, literature seed |
| `scripts/` | Literature harvesting, screening and statistics scripts |
| `tests/` | pytest suite |
| `Research_Notes/`, `Literature_Evidence_Package.xlsx` | Evidence corpus the app loads (M##/R## records, research notes, full-text reviews) |
| `docs/` | Handoff summary, case schema, statistical analysis reports |
| `examples/` | ILLUSTRATIVE example case and a legacy demo script |

## Run

Windows: double-click `setup_windows.bat` (creates `.venv`, installs the requirements, starts the GUI).
Next time use `gui\run_gui.bat`.

Any platform:

```
pip install -r requirements.txt
python -m gui                      # opens http://127.0.0.1:8765/
python -m app.cli example > case.json
python -m app.cli run case.json --out out    # writes register.md, register.csv, result.json
python examples/masonry_demo.py    # legacy demo (Monte Carlo + EMV option comparison); out of the current scope
```

Desktop app (PySide6 window, no browser): `run_desktop.bat` runs it from source; `build_desktop_exe.bat`
(or the GitHub workflow below) builds `FYP-Risk-Tool-Desktop.exe`. It hosts the same offline interface in Qt
WebEngine; exports open a normal Save dialog.

Browser-version program (.exe): run `build_exe.bat` to produce `dist\FYP-Risk-Tool\FYP-Risk-Tool.exe`, or use the
**Build Windows exe** workflow in the GitHub Actions tab (Run workflow) and download the zip it produces.
Copy the whole `FYP-Risk-Tool` folder to move it; no Python is needed on the target computer.

Tests and research scripts: `pip install -r requirements-dev.txt`, then `python -m pytest`.

## Not in the repository

Large or third-party files stay out of git (see `.gitignore`): `data/literature.db`, the `.jsonl`
corpus files and the downloaded `Research_Papers/` PDFs. The scripts in `scripts/` rebuild the database
and corpus.
