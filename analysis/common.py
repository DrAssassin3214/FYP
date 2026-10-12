"""Shared helpers for the analysis scripts. Every table/figure/JSON written through these helpers is labelled
'Derived Calculation' and carries its n. Nothing here edits the repo; it only reads app.* and data/*.json."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from statistics import mean

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

LABEL = "Derived Calculation"
SEED = 20261008            # the single fixed random seed used by every script (see README)
OKABE = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#F0E442", "#000000"]
PALETTE11 = OKABE[:6] + ["#882255", "#44AA99", "#999933", "#AA4499", "#117733"]
plt.rcParams.update({"figure.dpi": 110, "savefig.dpi": 140, "font.size": 9, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.titlesize": 10, "figure.facecolor": "white"})


def rnd(v, k=6):
    if isinstance(v, (float, np.floating)):
        return None if not np.isfinite(v) else round(float(v), k)
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.bool_,)):
        return bool(v)
    return v


def write_csv(name: str, rows: list[dict], fields: list[str]) -> Path:
    """Write out/<name>.csv. `label` is always the first column; callers must include an `n...` column."""
    assert any(f == "n" or f.startswith("n_") for f in fields), f"{name}: table must state n"
    p = OUT / f"{name}.csv"
    with p.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["label"] + fields, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({"label": LABEL, **{k: rnd(r.get(k)) for k in fields}})
    return p


def _clean(o):
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    return rnd(o) if isinstance(o, (float, np.floating, np.integer, np.bool_)) else o


def write_json(name: str, obj: dict, n: dict | int) -> Path:
    p = OUT / f"{name}.json"
    payload = _clean({"label": LABEL, "n": n, **obj})       # NaN -> null so the file is valid JSON
    p.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return p


def save_fig(fig, name: str, n_text: str, title: str | None = None) -> Path:
    if title:
        fig.suptitle(f"{title}\n[{LABEL}]  {n_text}", x=0.01, y=1.0, ha="left", va="bottom", fontsize=10)
    fig.text(0.01, -0.035, f"{LABEL} | {n_text} | fixed seed {SEED} | ordinal / rank quantities only; RII is not a probability or a number of days",
             fontsize=6.5, color="#555555", va="top")
    p = OUT / f"{name}.png"
    fig.savefig(p, bbox_inches="tight", metadata={"Software": "matplotlib", "Description": LABEL})
    plt.close(fig)
    return p


# ----------------------------------------------------------------------------------------- literature data
def load_data() -> dict:
    from app.literature_seed import load_dataset
    return load_dataset()


def roles(data: dict) -> dict[str, str]:
    """'seed' or 'held-out' (the dataset's non-seed role is renamed here on purpose)."""
    return {s["id"]: ("seed" if s["role"] == "seed" else "held-out") for s in data["studies"]}


def per_study_risk_means(data: dict, mappings=("direct",), studies=None, rescale=None) -> dict[str, dict[str, float]]:
    """study -> {risk -> mean of that study's items mapped to the risk}. One value per (study, risk), exactly as the repo
    averages (items inside a study first). rescale: optional {study: k} to map RII -> (RII-1/k)/(1-1/k)."""
    out: dict[str, dict[str, list[float]]] = {}
    for r in data["rows"]:
        if not r.get("risk") or r.get("mapping") not in mappings:
            continue
        if studies is not None and r["study"] not in studies:
            continue
        v = r["rii"]
        if rescale and rescale.get(r["study"]):
            k = rescale[r["study"]]
            v = (v - 1 / k) / (1 - 1 / k)
        out.setdefault(r["study"], {}).setdefault(r["risk"], []).append(v)
    return {s: {k: mean(v) for k, v in d.items()} for s, d in out.items()}


def risk_means(by_study: dict[str, dict[str, float]], weights: dict[str, float] | None = None, min_studies=1) -> dict[str, float]:
    acc: dict[str, list[tuple[float, float]]] = {}
    for s, d in by_study.items():
        w = 1.0 if weights is None else weights.get(s, 0.0)
        if w <= 0:
            continue
        for rid, v in d.items():
            acc.setdefault(rid, []).append((w, v))
    return {rid: sum(w * v for w, v in x) / sum(w for w, _ in x) for rid, x in acc.items() if len(x) >= min_studies}


def order(means: dict[str, float]) -> list[str]:
    """Same tie-break as app.literature_seed: descending mean, then risk id."""
    return sorted(means, key=lambda r: (-means[r], r))


def bands_equal_count(means: dict[str, float], n_bands=5) -> dict[str, int]:
    """Repo rule: class = n_bands - ((rank-1)*n_bands)//n (rank 1 = highest mean -> top class)."""
    o = order(means)
    n = len(o)
    return {rid: n_bands - (i * n_bands) // n for i, rid in enumerate(o)}


def spearman(x, y):
    from scipy import stats
    x = np.asarray(x, float); y = np.asarray(y, float)
    if len(x) < 3 or np.ptp(x) == 0 or np.ptp(y) == 0:
        return float("nan")
    return float(stats.spearmanr(x, y)[0])


def kendall(x, y):
    from scipy import stats
    x = np.asarray(x, float); y = np.asarray(y, float)
    if len(x) < 3 or np.ptp(x) == 0 or np.ptp(y) == 0:
        return float("nan")
    return float(stats.kendalltau(x, y)[0])


def holm(pvals) -> np.ndarray:
    """Holm step-down adjusted p-values, implemented by hand (no statsmodels)."""
    p = np.asarray(pvals, float)
    m = len(p)
    idx = np.argsort(p, kind="mergesort")
    adj = np.empty(m)
    run = 0.0
    for k, i in enumerate(idx):
        run = max(run, (m - k) * p[i])
        adj[i] = min(1.0, run)
    return adj


def _selftest_holm():
    got = holm([0.01, 0.04, 0.03, 0.005])
    assert np.allclose(got, [0.03, 0.06, 0.06, 0.02]), got
    assert holm([]).size == 0


_selftest_holm()
