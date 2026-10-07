# FYP

Framework for brickwork labour-productivity and delay-risk prediction using managerial factors in
selected Indian building projects (NICMAR final year project).

An offline decision-support tool: a deterministic rules engine and risk register, Monte Carlo schedule
simulation, and an expected-monetary-value (EMV) decision layer, with a local web GUI.

## Layout

| Folder | Contents |
|---|---|
| `app/` | Engine (rules, simulation, EMV, decision), productivity models, AI evidence layer, reporting, service API |
| `gui/` | Local offline web GUI (see `gui/README_GUI.md`) |
| `data/` | Rules, risk library, productivity models, India labour norms, literature seed |
| `scripts/` | Literature harvesting, screening and statistics scripts |
| `tests/` | pytest suite |
| `docs/` | Handoff summary, case schema, statistical analysis reports |
| `examples/` | Example case and demo script |

## Run

```
pip install -r requirements.txt
python -m gui          # opens http://127.0.0.1:8765/
python -m pytest
```

## Not in the repository

Large or third-party files stay out of git (see `.gitignore`): `data/literature.db`, the `.jsonl`
corpus files and the downloaded `Research_Papers/` PDFs. The scripts in `scripts/` rebuild the database
and corpus.
