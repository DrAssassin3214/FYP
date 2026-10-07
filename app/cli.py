"""Command line: build the risk register and matrix from a case file, or write a template.

    python -m app.cli template > my_case.json     # blank case
    python -m app.cli example  > example.json     # ILLUSTRATIVE placeholder case
    python -m app.cli run my_case.json --out out/ # register.md, register.csv, result.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app import service
from app.reporting.register_report import register_csv


class CliError(Exception):
    """A user-facing problem: printed as one line on stderr, exit code 2, no traceback."""


def _load_case(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise CliError(f"case file not found: {path}")
    if p.is_dir():
        raise CliError(f"{path} is a folder, not a case file")
    try:
        raw = p.read_bytes()
    except OSError as e:
        raise CliError(f"cannot read {path}: {e.strerror or e}")
    if not raw.strip():
        raise CliError(f"{path} is empty")
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        raise CliError(f"{path} is saved as UTF-16; re-save it as UTF-8 (in Notepad: Save As > Encoding > UTF-8)")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise CliError(f"{path} is not valid UTF-8 text; re-save it as UTF-8")
    try:
        case = json.loads(text)
    except (ValueError, RecursionError) as e:
        raise CliError(f"{path} is not valid JSON: {e}")
    if not isinstance(case, dict):
        raise CliError(f"{path} must contain a JSON object (a case), not a {type(case).__name__}")
    return case


def _write_outputs(res: dict, out_dir: str) -> None:
    out = Path(out_dir)
    if out.exists() and not out.is_dir():
        raise CliError(f"--out {out_dir} is a file; give a folder")
    try:
        out.mkdir(parents=True, exist_ok=True)
        (out / "register.md").write_text(res["report_markdown"], encoding="utf-8")
        # utf-8-sig: Excel on Windows needs the BOM to decode non-ASCII text
        (out / "register.csv").write_text(register_csv(res), encoding="utf-8-sig", newline="")
        (out / "result.json").write_text(
            json.dumps({k: v for k, v in res.items() if k != "report_markdown"}, indent=2, default=str), encoding="utf-8")
    except OSError as e:
        raise CliError(f"cannot write to --out {out_dir}: {e.strerror or e}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="fyp-risk")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("template")
    sub.add_parser("example")
    r = sub.add_parser("run")
    r.add_argument("case")
    r.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    if a.cmd == "template":
        print(json.dumps(service.template_case(), indent=2))
    elif a.cmd == "example":
        print(json.dumps(service.example_case(), indent=2))
    else:
        try:
            case = _load_case(a.case)
            res = service.run_case(case, service.evidence_index_from_workbook())
            if a.out:
                _write_outputs(res, a.out)
        except CliError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
        except service.CaseError as e:
            print("Case has problems:", file=sys.stderr)
            for p in e.problems:
                print(f"  - {p}", file=sys.stderr)
            return 2
        except (ValueError, TypeError, KeyError, AttributeError, RecursionError) as e:
            print(f"error: the case could not be processed ({type(e).__name__}: {e})", file=sys.stderr)
            return 2
        s = res["summary"]
        print(f"{s['n_risks']} risks in the register ({s['n_complete']} complete); {s['n_on_matrix']} on the matrix: "
              + ", ".join(f"{s['levels'][k]} {k}" for k in service.LEVELS if s["levels"][k]) if s["n_on_matrix"]
              else f"{s['n_risks']} risks in the register ({s['n_complete']} complete); none on the matrix")
        for w in res["warnings"]:
            print("note:", w)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
