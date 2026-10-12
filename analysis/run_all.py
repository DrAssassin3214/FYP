"""Run every analysis script in order and write out/manifest.json (sha256 of every output file).
    python analysis/run_all.py            # from the repo root; needs numpy, scipy, matplotlib
Deterministic: every random draw uses numpy.random.default_rng(common.SEED); two runs give identical file hashes
(out/run_timing.json, which holds wall-clock times, is deliberately excluded from the manifest)."""
from __future__ import annotations

import hashlib
import importlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import common as C  # noqa: E402

MODULES = ["s0_repo_function_checks", "s1_example_sensitivity", "s2_threshold_sensitivity", "s3_seed_band_sensitivity",
           "s4_interstudy_agreement", "s5_rii_uncertainty"]


def main():
    # clear stale outputs so the manifest lists exactly what this run produced
    for p in C.OUT.glob("*"):
        if p.is_file():
            p.unlink()
    timing = {}
    t_all = time.time()
    for name in MODULES:
        t = time.time()
        importlib.import_module(name).main()
        timing[name] = round(time.time() - t, 2)
        print(f"{name:32s} {timing[name]:6.2f} s")
    files = sorted(p for p in C.OUT.iterdir() if p.is_file())
    for p in files:                                                  # every output must be labelled and carry n
        if p.suffix == ".csv":
            head = p.read_text(encoding="utf-8").splitlines()[0].split(",")
            assert head[0] == "label" and any(h == "n" or h.startswith("n_") for h in head), p.name
            assert p.read_text(encoding="utf-8").splitlines()[1].startswith(C.LABEL), p.name
        elif p.suffix == ".json":
            j = json.loads(p.read_text(encoding="utf-8"))
            assert j["label"] == C.LABEL and "n" in j, p.name
    manifest = {"label": C.LABEL, "seed": C.SEED, "n_files": len(files),
                "sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
    (C.OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    timing["total"] = round(time.time() - t_all, 2)
    (C.OUT / "run_timing.json").write_text(json.dumps({"label": C.LABEL, "n": len(MODULES), "seconds": timing}, indent=2) + "\n", encoding="utf-8")
    print(f"total {timing['total']} s; {len(files)} files in {C.OUT}")


if __name__ == "__main__":
    main()
