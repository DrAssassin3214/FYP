"""Build the online data pack from the bundled data/ files.

    python scripts/make_data_pack.py [--out datapack] [--version 2026-10-12.1]

Writes the four data files plus manifest.json (SHA-256 of each) into --out.  Publish that folder at the address in
app/data_sync.py DEFAULT_MANIFEST_URL (a public GitHub repository, branch main, files at the top level), or set
BRICKSLY_PACK_URL on the laptop.  Raise the version every time the files change; the tool installs a pack only when
its version is newer than the one it has.  Publish only data you are willing to make public.
"""
import argparse
import hashlib
import json
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = ("risk_library_masonry.json", "rules_masonry.json", "literature_seed.json", "mitigation_catalogue.json")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="datapack")
    ap.add_argument("--version", default=f"{date.today().isoformat()}.1")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    files = {}
    for n in FILES:
        raw = (ROOT / "data" / n).read_bytes()
        (out / n).write_bytes(raw)
        files[n] = {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
    (out / "manifest.json").write_text(json.dumps({"schema": 1, "version": a.version, "files": files}, indent=2), encoding="utf-8")
    print(f"wrote {len(files)} files and manifest.json (version {a.version}) to {out}")


if __name__ == "__main__":
    main()
