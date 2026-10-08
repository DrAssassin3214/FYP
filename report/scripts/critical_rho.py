#!/usr/bin/env python3
"""Smallest |Spearman rho| that would be two-sided significant at 5% for n paired risks (no ties), and Holm adjustment
for the three held-out comparisons of analysis S4. Derived Calculation; writes report/scripts/out/critical_rho.csv.

For n <= 8 the exact permutation distribution is enumerated; for larger n 200,000 random permutations with a fixed seed
(20261008) are used. The critical value is the smallest observed |rho| on the achievable grid whose two-sided
permutation p is <= 0.05.
"""
import csv
import itertools
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(20261008)


def rho_from_perm(ranks_y, n):
    d = ranks_y - np.arange(1, n + 1)
    return 1 - 6 * (d ** 2).sum(axis=-1) / (n * (n ** 2 - 1))


def dist(n):
    if n <= 8:
        perms = np.array(list(itertools.permutations(range(1, n + 1))))
    else:
        perms = np.array([rng.permutation(n) + 1 for _ in range(200000)])
    return rho_from_perm(perms, n)


rows = []
for n in (5, 6, 7, 8, 9, 10, 11, 13, 15, 19):
    r = np.round(dist(n), 10)
    vals = np.unique(np.abs(r))
    crit = None
    for v in sorted(vals):
        p = (np.abs(r) >= v - 1e-12).mean()
        if p <= 0.05:
            crit = (v, p)
            break
    rows.append(["Derived Calculation", n, "exact" if n <= 8 else "200000 permutations", round(crit[0], 3) if crit else "none", round(crit[1], 4) if crit else ""])
with open(OUT / "critical_rho.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["label", "n_shared_risks", "method", "critical_abs_rho_two_sided_5pct", "attained_p"])
    w.writerows(rows)
for r in rows:
    print(r)

# Holm over the three held-out comparisons (M10, M15, M14) using the raw permutation p from analysis/out
src = ROOT / "analysis/out/s4_leave_one_study_out.csv"
raw = {}
for r in csv.DictReader(open(src, encoding="utf-8")):
    if r["study"] in ("M10", "M15", "M14"):
        raw[r["study"]] = (int(r["n_shared_risks"]), float(r["spearman_rho"]), float(r["perm_p_two_sided"]))
order = sorted(raw, key=lambda k: raw[k][2])
adj, prev = {}, 0.0
for i, k in enumerate(order):
    a = min(1.0, raw[k][2] * (len(order) - i))
    prev = max(prev, a)
    adj[k] = prev
res = {k: dict(n=raw[k][0], rho=round(raw[k][1], 3), p_raw=round(raw[k][2], 3), p_holm_family_of_3=round(adj[k], 3)) for k in raw}
(OUT / "holm_heldout3.json").write_text(json.dumps({"label": "Derived Calculation", "source": "analysis/out/s4_leave_one_study_out.csv", "results": res}, indent=1))
print(res)
