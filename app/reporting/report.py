"""Generate the research-oriented report (master prompt section 67) from engine outputs.

The report only restates engine results and the input register; it performs no
new modelling.  Every parameter is printed with its Source, and everything that
is not Literature/Historical is repeated in the assumptions section.
"""
from __future__ import annotations

from pathlib import Path
from typing import Mapping, Optional, Sequence

import numpy as np

from app.engine.audit import assumption_register
from app.engine.emv import cost_summary, event_emv
from app.engine.matrix import classify
from app.engine.models import Activity, CostModel, Mitigation, Risk
from app.engine.simulation import SimResult, sensitivity, summarise


def _fmt(x, nd=2):
    return "NR" if x is None else (f"{x:,.{nd}f}" if isinstance(x, (int, float)) else str(x))


def plot_distributions(base: SimResult, residual: Optional[SimResult], path: Path, deadline: Optional[float] = None) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    bins = np.linspace(base.duration.min(), max(base.duration.max(), residual.duration.max() if residual else 0), 40)
    ax[0].hist(base.duration, bins=bins, alpha=0.6, label="Without mitigation", density=True)
    if residual is not None:
        ax[0].hist(residual.duration, bins=bins, alpha=0.6, label="With selected option", density=True)
    ax[0].set_xlabel("Activity duration (days)")
    ax[0].set_ylabel("Density")
    ax[0].set_title("Simulated duration")
    for arr, lab in [(base.duration, "base")] + ([(residual.duration, "resid")] if residual else []):
        xs = np.sort(arr)
        ax[1].plot(xs, np.arange(1, len(xs) + 1) / len(xs), label=f"CDF {lab}")
    for q, ls in ((0.5, ":"), (0.8, "--"), (0.9, "-."), (0.95, "-")):
        ax[1].axhline(q, color="grey", lw=0.5, ls=ls)
    if deadline:
        ax[1].axvline(deadline, color="red", lw=1, label="Deadline")
    ax[1].set_xlabel("Activity duration (days)")
    ax[1].set_ylabel("Cumulative probability")
    ax[1].set_title("CDF with P50/P80/P90/P95 guides")
    ax[0].legend(fontsize=8)
    ax[1].legend(fontsize=8)
    fig.text(0.5, 0.005, "Inputs are user/expert/literature-derived assumptions; the spread reflects those assumptions, not measured certainty.",
             ha="center", fontsize=7)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def generate_report(
    activity: Activity,
    risks: Sequence[Risk],
    cost: CostModel,
    mitigations: Sequence[Mitigation],
    base: SimResult,
    decision: Mapping,
    impact_edges_fraction: Sequence[float],
    evidence_index: Mapping[str, str],
    figure_path: Optional[str] = None,
    limitations: Sequence[str] = (),
) -> str:
    t0 = activity.baseline_duration_days.value
    deadline = activity.deadline_days.value if activity.deadline_days else None
    s = summarise(base, deadline_days=deadline, delay_thresholds=(2, 5))
    cs = cost_summary(base, cost, deadline)
    emv = event_emv(risks, cost)
    mat = {m["risk_id"]: m for m in classify(risks, t0, impact_edges_fraction)}
    sens = sensitivity(base)
    inputs = {"activity": activity, "risks": list(risks), "cost": cost, "mitigations": list(mitigations)}
    assumptions = assumption_register(inputs)
    used_ids = sorted({e for r in risks for e in r.evidence_ids} | {e for m in mitigations for e in m.evidence_ids}
                      | set(activity.baseline_duration_days.evidence_ids))

    L: list[str] = []
    a = L.append
    a(f"# Risk assessment report: {activity.name}\n")
    a("## 1. Executive summary\n")
    sel = decision.get("selected_option_id")
    a(f"- Baseline duration T0 = {t0:.2f} days ({activity.baseline_duration_days.source.value}).")
    a(f"- Simulated expected duration {s['mean']:.2f} days; expected delay {s['expected_delay']:.2f} days; "
      f"P80 {s['percentiles']['P80']:.2f}, P90 {s['percentiles']['P90']:.2f}, P95 {s['percentiles']['P95']:.2f} days.")
    if deadline:
        a(f"- Probability of exceeding the {deadline:.1f}-day deadline under the stated assumptions: {s['p_exceed_deadline']:.1%}.")
    a(f"- Expected delay cost {cs['expected_cost']:,.0f} {cost.currency} (P90 {cs['P90']:,.0f}).")
    a(f"- Decision-support statement: {decision['statement']}")
    a("- This is a probabilistic simulation under stated assumptions, not a prediction validated against project outcomes.\n")

    a("## 2. Activity description\n")
    a(f"| Field | Value | Source |\n|---|---|---|\n| ID | {activity.activity_id} | |\n| Name | {activity.name} | |")
    a(f"| Baseline duration (days) | {t0:.2f} | {activity.baseline_duration_days.source.value} {', '.join(activity.baseline_duration_days.evidence_ids)} |")
    a(f"| Quantity | {_fmt(activity.quantity)} {activity.unit} | |")
    a(f"| Deadline (days) | {_fmt(deadline)} | {activity.deadline_days.source.value if activity.deadline_days else ''} |\n")

    a("## 3. Risk register\n")
    a("| ID | Risk | Status | p | p source | Delay distribution (a, m, b) days | Dist. source | Direct cost | Evidence |\n|---|---|---|---|---|---|---|---|---|")
    for r in risks:
        d = r.delay
        a(f"| {r.risk_id} | {r.name} | {r.status.value} | {r.p.value:.2f} | {r.p.source.value} | {d.kind}({d.a}, {d.m}, {d.b}) | {d.source.value} | "
          f"{r.direct_cost_if_occurs.value:,.0f} ({r.direct_cost_if_occurs.source.value}) | {', '.join(r.evidence_ids) or 'none'} |")
    a("")
    a("## 4. Literature evidence\n")
    for e in used_ids:
        a(f"- **{e}**: {evidence_index.get(e, 'reference not found in evidence index')}")
    a("")
    a("## 5-6. Probability and impact assessment\n")
    a("Probability p is an event probability during execution of this activity, not an expert score. Impact is the conditional delay distribution in days. "
      "Survey rankings (RII) in the cited papers rank importance; they are not probabilities and were not converted to p.\n")
    a("## 7. Risk matrix (prioritisation only)\n")
    a("| Risk | p | p class | Impact class | Score | Level |\n|---|---|---|---|---|---|")
    for r in risks:
        m = mat[r.risk_id]
        a(f"| {r.risk_id} | {m['p']:.2f} | {m['p_class']} | {m['impact_class']} | {m['score']} | {m['level']} |")
    a("\nMatrix bins and thresholds are editable assumptions. The level is not used in the simulation or in EMV.\n")
    a("## 8. Delay distribution assumptions\n")
    a("Delay given occurrence follows the listed distribution; Beta-PERT shape weight lambda = 4 unless stated. Occurrence is Bernoulli(p) per risk.\n")
    a("## 9. Monte Carlo methodology\n")
    a(f"T = T0 + sum(I_i D_i); I_i ~ Bernoulli(p_i); independent by default. n = {base.n:,} iterations; seed = {base.seed}; "
      "common random numbers across scenarios; percentiles by empirical quantile with distribution-free 95% intervals.\n")
    a("## 10. Simulation results\n")
    a("| Statistic | Value (days) |\n|---|---|")
    for k in ("min", "mean", "median", "std", "max"):
        a(f"| {k} | {s[k]:.2f} |")
    for k, v in s["percentiles"].items():
        lo, hi = s["percentile_ci95"][k]
        a(f"| {k} | {v:.2f} (95% CI {lo:.2f}-{hi:.2f}) |")
    a(f"| Standard error of mean | {s['mean_se']:.3f} |")
    if deadline:
        a(f"| P(T > deadline) | {s['p_exceed_deadline']:.3f} |")
    for x, pr in s["p_delay_exceeds"].items():
        a(f"| P(delay > {x:g} d) | {pr:.3f} |")
    if figure_path:
        a(f"\n![Duration distribution]({figure_path})\n")
    a("\n## 11. Sensitivity analysis\n")
    a("Spearman rank correlation of each risk's delay with total delay (descriptive, not causal):\n")
    a("| Risk | Spearman rho | Mean contribution (days) | Share of expected delay |\n|---|---|---|---|")
    for x in sens:
        a(f"| {x['risk_id']} | {x['spearman_with_total_delay']:.2f} | {x['mean_contribution_days']:.2f} | {x['share_of_expected_delay']:.1%} |")
    a("\n## 12-13. Monetary impact and EMV\n")
    a(f"Cost per delay day = {cost.cost_per_delay_day.value:,.0f} {cost.currency} ({cost.cost_per_delay_day.source.value}).\n")
    a("| Risk | p | E[delay if occurs] | Conditional cost | Event EMV |\n|---|---|---|---|---|")
    for e in emv:
        a(f"| {e['risk_id']} | {e['p']:.2f} | {e['expected_delay_if_occurs_days']:.2f} | {e['conditional_cost']:,.0f} | {e['emv']:,.0f} |")
    a(f"\nSum of event EMV = {sum(e['emv'] for e in emv):,.0f}; simulated expected cost = {cs['expected_cost']:,.0f} {cost.currency}. "
      "They agree in expectation only for independent, additive risks with a linear cost model.\n")
    a("## 14-16. Mitigation alternatives, residual risk and post-mitigation simulation\n")
    a("| Option | Mitigations | Cost | Residual E[cost] | TEC | E[duration] | P90 | P(T>deadline) | Admissible | Note |\n|---|---|---|---|---|---|---|---|---|---|")
    for o in decision["options"]:
        pe = "NR" if o["p_exceed_deadline"] is None else f"{o['p_exceed_deadline']:.3f}"
        note = "; ".join(o["rejected_because"]) if o["rejected_because"] else ""
        a(f"| {o['label']} | {', '.join(o['mitigations']) or '-'} | {o['mitigation_cost']:,.0f} | {o['residual_expected_cost']:,.0f} | "
          f"{o['total_expected_cost']:,.0f} | {o['expected_duration']:.2f} | {o['P90']:.2f} | {pe} | {o['admissible']} | {note} |")
    a("")
    for m in mitigations:
        a(f"- **{m.mitigation_id}** ({m.strategy}) targets {m.risk_id}: {m.action}. Mechanism: {m.mechanism or 'NR'}. "
          f"Effect source: p_after = {m.p_after.source.value if m.p_after else 'unchanged'}; "
          f"delay_after = {m.delay_after.source.value if m.delay_after else 'unchanged'}. Evidence: {', '.join(m.evidence_ids) or 'none'}.")
    a("\n## 17. Decision analysis\n")
    a(f"**Rule used.** {decision['rule']}\n")
    a(f"**Result.** {decision['statement']}\n")
    a(f"*{decision['caveat']}*\n")
    a("## 18. Assumptions and non-literature inputs\n")
    a("| Input | Value | Source | Note |\n|---|---|---|---|")
    for x in assumptions:
        a(f"| {x['input']} | {x['value']} | {x['source']} | {x['note']} |")
    a("\n## 19. Limitations\n")
    base_lim = [
        "Probabilities, delay ranges and mitigation effects are subjective unless a source is shown; results inherit that uncertainty.",
        "Risks are treated as independent and delays as additive unless a correlation is specified; interacting risks can widen the tail.",
        "Cost per delay day is treated as constant.",
        "No back-testing against actual project outcomes has been performed, so outputs are simulation results, not validated predictions.",
    ]
    for x in list(base_lim) + list(limitations):
        a(f"- {x}")
    a("\n## 20. Evidence references\n")
    for e in used_ids:
        a(f"- {e}: {evidence_index.get(e, 'not found')}")
    return "\n".join(L) + "\n"
