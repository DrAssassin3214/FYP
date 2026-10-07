# FYP

Framework for brickwork labour-productivity and delay-risk prediction using managerial factors in
selected Indian building projects (NICMAR final year project).

An offline decision-support tool: a deterministic rules engine and risk register, Monte Carlo schedule
simulation, and an expected-monetary-value (EMV) decision layer, with a local web GUI.

## Layout

| Folder | Contents |
|---|---|
| `app/` | Engine (rules, simulation, EMV, decision), productivity models, AI evidence layer, reporting, service API |
| `gui/` | Local offline GUI, as a web page (`python -m gui`) or a PySide6 desktop window (`python -m gui.qt_app`); see `gui/README_GUI.md` |
| `data/` | Rules, risk library, productivity models, India labour norms, literature seed |
| `scripts/` | Literature harvesting, screening and statistics scripts |
| `tests/` | pytest suite |
| `Research_Notes/`, `Literature_Evidence_Package.xlsx` | Evidence corpus the app loads (M##/R## records, research notes, full-text reviews) |
| `docs/` | Handoff summary, case schema, statistical analysis reports |
| `examples/` | Example case and demo script |

## Run

Windows: double-click `setup_windows.bat` (creates `.venv`, installs the requirements, starts the GUI).
Next time use `gui\run_gui.bat`.

Any platform:

```
pip install -r requirements.txt
python -m gui                      # opens http://127.0.0.1:8765/
python -m app.cli example > case.json
python -m app.cli run case.json --out out    # writes register.md, register.csv, result.json
python examples/masonry_demo.py    # Monte Carlo + EMV option comparison
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
