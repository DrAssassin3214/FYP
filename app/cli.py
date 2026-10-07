"""Command line: build the risk register and matrix from a case file, or write a template.

    python -m app.cli template > my_case.json     # blank case
    python -m app.cli example  > example.json     # ILLUSTRATIVE placeholder case
    python -m app.cli run my_case.json --out out/ # register.md, register.csv, result.json
"""
from __future__ import annotations

import argparse
import json
import sys

from app import service


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
            res = service.run_case_file(a.case, a.out, service.evidence_index_from_workbook())
        except service.CaseError as e:
            print("Case has problems:", file=sys.stderr)
            for p in e.problems:
                print(f"  - {p}", file=sys.stderr)
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
