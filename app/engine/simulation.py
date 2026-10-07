"""Vectorised Monte Carlo engine.

Model (candidate formulation, to be justified against the literature):
    I_i ~ Bernoulli(p_i)            occurrence of risk i during the activity
    D_i ~ F_i(a_i, m_i, b_i)        delay in days given occurrence
    T   = T0 + sum_i I_i * D_i      additive, independent by default

Common random numbers: the uniforms for risk i are generated from a stream keyed
on (seed, risk_id), so a mitigation scenario that changes p_i or F_i re-uses the
same underlying draws.  Differences between scenarios are then driven by the
parameter changes, not by sampling noise.
"""
from __future__ import annotations

import zlib
from dataclasses import dataclass
from typing import Mapping, Optional, Sequence

import numpy as np
from scipy import stats

from .models import Activity, DelayDist, Risk

DEFAULT_QUANTILES = (0.10, 0.50, 0.80, 0.85, 0.90, 0.95)


def _stream(seed: int, risk_id: str) -> np.random.Generator:
    return np.random.default_rng([int(seed), zlib.crc32(risk_id.encode("utf-8"))])


def delay_ppf(dist: DelayDist, u: np.ndarray) -> np.ndarray:
    """Inverse CDF of the conditional delay distribution (vectorised)."""
    dist.validate()
    if dist.kind == "fixed":
        return np.full_like(u, dist.m, dtype=float)
    a, m, b = dist.a, dist.m, dist.b
    if b == a:
        return np.full_like(u, a, dtype=float)
    if dist.kind == "uniform":
        return a + u * (b - a)
    if dist.kind == "triangular":
        c = (m - a) / (b - a)
        low = a + np.sqrt(u * (b - a) * (m - a))
        high = b - np.sqrt((1.0 - u) * (b - a) * (b - m))
        return np.where(u < c, low, high)
    alpha = 1.0 + dist.lam * (m - a) / (b - a)
    beta = 1.0 + dist.lam * (b - m) / (b - a)
    return a + (b - a) * stats.beta.ppf(u, alpha, beta)


@dataclass
class SimResult:
    t0: float
    n: int
    seed: int
    risk_ids: list[str]
    occurrence: np.ndarray          # (n, k) bool
    risk_delay: np.ndarray          # (n, k) days contributed (0 if not occurred)
    delay: np.ndarray               # (n,)  total delay
    duration: np.ndarray            # (n,)  T0 + delay
    direct_cost: np.ndarray         # (n,)  sum of direct costs of occurred risks
    latent_delay: Optional[np.ndarray] = None   # (n,) T0*(L-1) from routine productivity variability, if modelled


def _correlation_matrix(ids: Sequence[str], corr: Optional[Mapping[tuple[str, str], float]]) -> Optional[np.ndarray]:
    if not corr:
        return None
    k = len(ids)
    idx = {r: i for i, r in enumerate(ids)}
    mat = np.eye(k)
    for (r1, r2), rho in corr.items():
        if r1 in idx and r2 in idx:
            if not (-1.0 <= rho <= 1.0):
                raise ValueError("correlation must be in [-1, 1]")
            mat[idx[r1], idx[r2]] = mat[idx[r2], idx[r1]] = rho
    if np.min(np.linalg.eigvalsh(mat)) < -1e-10:
        raise ValueError("correlation matrix is not positive semi-definite")
    return mat


def simulate(
    activity: Activity,
    risks: Sequence[Risk],
    n: int = 10_000,
    seed: int = 12345,
    occurrence_correlation: Optional[Mapping[tuple[str, str], float]] = None,
) -> SimResult:
    """Run the Monte Carlo model.

    occurrence_correlation: optional Gaussian-copula correlation between occurrence
    indicators, keyed by (risk_id, risk_id).  Default None = independent (baseline
    assumption A01, to be tested by sensitivity analysis).
    """
    activity.validate()
    if n < 1:
        raise ValueError("n must be >= 1")
    ids = [r.risk_id for r in risks]
    if len(set(ids)) != len(ids):
        raise ValueError("risk ids must be unique")
    for r in risks:
        r.validate()

    k = len(risks)
    t0 = activity.baseline_duration_days.value
    u_occ = np.empty((n, k))
    u_del = np.empty((n, k))
    for j, r in enumerate(risks):
        g = _stream(seed, r.risk_id)
        u_occ[:, j] = g.random(n)
        u_del[:, j] = g.random(n)

    cmat = _correlation_matrix(ids, occurrence_correlation)
    if cmat is not None and k > 0:
        z = stats.norm.ppf(np.clip(u_occ, 1e-12, 1 - 1e-12))
        z = z @ np.linalg.cholesky(cmat).T
        u_occ = stats.norm.cdf(z)

    occurrence = np.zeros((n, k), dtype=bool)
    risk_delay = np.zeros((n, k))
    direct = np.zeros(n)
    for j, r in enumerate(risks):
        occ = u_occ[:, j] < r.p.value
        occurrence[:, j] = occ
        risk_delay[:, j] = np.where(occ, delay_ppf(r.delay, u_del[:, j]), 0.0)
        direct += occ * r.direct_cost_if_occurs.value

    latent = None
    if activity.productivity_cv is not None and activity.productivity_cv.value > 0:
        # mean-1 lognormal multiplier L on the baseline: T = T0 * L + sum I_i D_i
        s2 = np.log(1.0 + activity.productivity_cv.value ** 2)
        z = stats.norm.ppf(np.clip(_stream(seed, "__latent__").random(n), 1e-12, 1 - 1e-12))
        latent = t0 * (np.exp(-s2 / 2 + np.sqrt(s2) * z) - 1.0)

    if activity.baseline_dist is not None:
        u_b = np.clip(_stream(seed, "__baseline__").random(n), 1e-12, 1 - 1e-12)
        latent = delay_ppf(activity.baseline_dist, u_b) - t0      # realised baseline minus planned baseline

    delay = risk_delay.sum(axis=1) + (latent if latent is not None else 0.0)
    return SimResult(t0, n, seed, ids, occurrence, risk_delay, delay, t0 + delay, direct, latent)


def analytic_moments(risks: Sequence[Risk]) -> dict:
    """Exact mean and variance of sum I_i D_i for INDEPENDENT risks (validation check).

    E[I D] = p mu ;  Var[I D] = p (sigma^2 + mu^2) - p^2 mu^2
    """
    mean = var = 0.0
    for r in risks:
        p, mu, s2 = r.p.value, r.delay.mean(), r.delay.variance()
        mean += p * mu
        var += p * (s2 + mu * mu) - p * p * mu * mu
    return {"expected_delay": mean, "variance": var, "std": var ** 0.5}


def simulate_until_precise(
    activity: Activity,
    risks: Sequence[Risk],
    tolerance_days: float,
    quantile: float = 0.90,
    start_n: int = 10_000,
    max_n: int = 400_000,
    seed: int = 12345,
    occurrence_correlation=None,
) -> SimResult:
    """Double n until the 95% CI half-width of the chosen quantile is <= tolerance_days
    (or max_n is reached).  Tail quantiles need more runs than the mean."""
    n = start_n
    while True:
        res = simulate(activity, risks, n, seed, occurrence_correlation)
        lo, hi = quantile_ci(np.sort(res.duration), quantile)
        if (hi - lo) / 2 <= tolerance_days or n >= max_n:
            return res
        n *= 2


def quantile_ci(sorted_x: np.ndarray, q: float, conf: float = 0.95) -> tuple[float, float]:
    """Distribution-free CI for a quantile from order statistics (normal approx. of ranks)."""
    n = len(sorted_x)
    z = stats.norm.ppf(0.5 + conf / 2)
    half = z * np.sqrt(n * q * (1 - q))
    lo = int(max(np.floor(n * q - half), 0))
    hi = int(min(np.ceil(n * q + half), n - 1))
    return float(sorted_x[lo]), float(sorted_x[hi])


def summarise(
    res: SimResult,
    deadline_days: Optional[float] = None,
    delay_thresholds: Sequence[float] = (),
    quantiles: Sequence[float] = DEFAULT_QUANTILES,
) -> dict:
    t = np.sort(res.duration)
    d = res.duration - res.t0
    out: dict = {
        "n": res.n,
        "seed": res.seed,
        "baseline_days": res.t0,
        "min": float(t[0]),
        "max": float(t[-1]),
        "mean": float(t.mean()),
        "median": float(np.median(t)),
        "std": float(t.std(ddof=1)) if res.n > 1 else 0.0,
        "variance": float(t.var(ddof=1)) if res.n > 1 else 0.0,
        "mean_se": float(t.std(ddof=1) / np.sqrt(res.n)) if res.n > 1 else 0.0,
        "expected_delay": float(d.mean()),
        "p_any_delay": float((d > 0).mean()),
        "percentiles": {},
        "percentile_ci95": {},
        "delay_percentiles": {},
    }
    for q in quantiles:
        key = f"P{int(round(q * 100))}"
        out["percentiles"][key] = float(np.quantile(t, q))
        out["percentile_ci95"][key] = quantile_ci(t, q)
        out["delay_percentiles"][key] = float(np.quantile(d, q))
    for q in (0.90, 0.95):
        cut = np.quantile(t, q)
        out[f"cvar_{int(q * 100)}"] = float(t[t >= cut].mean())     # mean duration in the worst (1-q) tail
    if deadline_days is not None:
        out["p_exceed_deadline"] = float((res.duration > deadline_days).mean())
    out["p_delay_exceeds"] = {float(x): float((d > x).mean()) for x in delay_thresholds}
    return out


def convergence(res: SimResult, quantiles: Sequence[float] = (0.5, 0.8, 0.9), checkpoints: int = 10) -> list[dict]:
    """Running mean and percentiles at increasing sample sizes.

    Use to judge whether the reported statistics have stabilised; sampling error
    shrinks roughly as 1/sqrt(n) for the mean and depends on density for tails.
    """
    rows = []
    for c in np.linspace(res.n / checkpoints, res.n, checkpoints).astype(int):
        x = res.duration[:c]
        row = {"n": int(c), "mean": float(x.mean())}
        for q in quantiles:
            row[f"P{int(round(q * 100))}"] = float(np.quantile(x, q))
        rows.append(row)
    return rows


def sensitivity(res: SimResult) -> list[dict]:
    """Rank-correlation and mean-contribution of each risk to total delay.

    Spearman correlation is descriptive; it is not evidence of causation and can
    understate risks that matter only when they co-occur.
    """
    out = []
    total_rank = stats.rankdata(res.delay)
    for j, rid in enumerate(res.risk_ids):
        x = res.risk_delay[:, j]
        if np.ptp(x) == 0 or np.ptp(res.delay) == 0:
            rho = 0.0
        else:
            rho = float(np.corrcoef(stats.rankdata(x), total_rank)[0, 1])
        out.append(
            {
                "risk_id": rid,
                "spearman_with_total_delay": rho,
                "mean_contribution_days": float(x.mean()),
                "share_of_expected_delay": float(x.mean() / res.delay.mean()) if res.delay.mean() > 0 else 0.0,
            }
        )
    if res.latent_delay is not None:
        x = res.latent_delay
        rho = float(np.corrcoef(stats.rankdata(x), total_rank)[0, 1]) if np.ptp(x) > 0 and np.ptp(res.delay) > 0 else 0.0
        out.append({"risk_id": "LATENT_PRODUCTIVITY", "spearman_with_total_delay": rho,
                    "mean_contribution_days": float(x.mean()),
                    "share_of_expected_delay": float(x.mean() / res.delay.mean()) if res.delay.mean() > 0 else 0.0})
    return sorted(out, key=lambda r: -abs(r["spearman_with_total_delay"]))
