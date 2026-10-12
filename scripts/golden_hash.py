"""Golden hash of engine output (QUALITY_BAR item 3): same input and seed give identical output.

    python scripts/golden_hash.py            # prints one SHA-256 per built-in case
Compare the lines before and after an engine change; a difference must be explained.
The audit timestamp is excluded.
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import service  # noqa: E402


def _strip(o):
    if isinstance(o, dict):
        return {k: _strip(v) for k, v in o.items() if k not in ("timestamp", "created", "generated_at", "run_at", "timestamp_utc")}
    if isinstance(o, list):
        return [_strip(v) for v in o]
    return o


def digest(obj) -> str:
    return hashlib.sha256(json.dumps(_strip(obj), sort_keys=True, default=str).encode("utf-8")).hexdigest()


def main() -> None:
    print("run_case(example)      ", digest(service.run_case(service.example_case())))
    print("run_case(template)     ", digest(service.run_case(service.template_case())))
    print("run_analysis(example)  ", digest(service.run_analysis(service.example_analysis_case())))
    for basis in ("seed", "all"):
        c = service.template_case()
        c["risks"] = [{"id": r["id"], "name": r["name"], "category": r.get("category", "")} for r in service.risk_library()]
        c["seed_basis"] = basis
        print(f"run_case(seed {basis:4s})   ", digest(service.run_case(c)))


if __name__ == "__main__":
    main()
