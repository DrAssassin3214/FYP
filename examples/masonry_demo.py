"""ILLUSTRATIVE brick-masonry run.

EVERY number below marked Source.ASSUMPTION is a placeholder used to exercise the
engine.  None is a literature value or a finding.  Replace with site data, expert
elicitation or sourced values before drawing any conclusion.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.engine.audit import build_record
from app.engine.decision import Constraints, Option, compare_options
from app.engine.emv import cost_summary, event_emv
from app.engine.matrix import classify
from app.engine.models import (Activity, CostModel, DelayDist, Mitigation, Param, Risk, RiskStatus, Source)
from app.engine.simulation import convergence, sensitivity, simulate, summarise

A = Source.ASSUMPTION
ILL = "ILLUSTRATIVE placeholder, not evidence"

# Baseline = quantity / (crews x productivity).  Placeholder inputs; USER INPUT REQUIRED for a real case.
quantity_m2, crews, prod = 1200.0, 3, 26.2          # 26.2 m2/day per 2-mason crew is Palestine data (M03), NOT India
t0 = quantity_m2 / (crews * prod)
activity = Activity("MAS-01", "Brick masonry, ground-floor walls",
                    Param(round(t0, 2), Source.DERIVED, ("M03",), "quantity/(crews*productivity); productivity is a placeholder"),
                    quantity=quantity_m2, unit="m2", deadline_days=Param(round(t0 * 1.15, 1), A, note="placeholder deadline = 115% of baseline"))

def r(rid, name, cat, p, a, m, b, ev, direct=0.0):
    return Risk(rid, name, Param(p, A, note=ILL), DelayDist("pert", a, m, b, source=A), category=cat,
                status=RiskStatus.LITERATURE_SUPPORTED, evidence_ids=ev,
                direct_cost_if_occurs=Param(direct, A, note=ILL))

# The EXISTENCE of these risks is supported by the papers cited (survey rankings, not probabilities);
# probabilities and delay ranges are placeholders.
risks = [
    r("R01", "Brick/material shortage", "Material", 0.30, 1, 3, 8, ("M01", "M06")),
    r("R02", "Labour absenteeism / shortage", "Labour", 0.35, 1, 2, 6, ("M01", "M07", "M15")),
    r("R03", "Rework due to workmanship", "Quality", 0.25, 1, 2, 5, ("M03", "M15"), direct=8000),
    r("R04", "Rain / monsoon stoppage", "Weather", 0.20, 1, 2, 7, ("R08",)),
]
cost = CostModel(Param(15000.0, A, note="cost per delay day, INR: USER INPUT REQUIRED (placeholder)"))

mitigations = [
    Mitigation("M-A", "R01", "Hold a buffer stock of bricks on site", cost=Param(12000, A, note=ILL),
               p_after=Param(0.10, A, note="effect size: EXPERT JUDGMENT REQUIRED"), evidence_ids=("M01",),
               mechanism="Reduces chance of stock-out during the activity"),
    Mitigation("M-B", "R02", "Add one extra crew on standby", cost=Param(25000, A, note=ILL),
               delay_after=DelayDist("pert", 0.5, 1, 3, source=A), evidence_ids=("M02",),
               mechanism="Shortens delay if labour is short by crashing/backfill"),
    Mitigation("M-C", "R03", "Supervisor quality checks each course", cost=Param(9000, A, note=ILL),
               p_after=Param(0.12, A, note="effect size: EXPERT JUDGMENT REQUIRED"), evidence_ids=("M03",),
               mechanism="Fewer rejected panels"),
]
options = [Option("O-A", "Buffer stock", ("M-A",)), Option("O-B", "Standby crew", ("M-B",)),
           Option("O-C", "Quality checks", ("M-C",)), Option("O-ABC", "All three", ("M-A", "M-B", "M-C"))]

N, SEED = 10_000, 20260926
base = simulate(activity, risks, N, SEED)
summary = summarise(base, deadline_days=activity.deadline_days.value, delay_thresholds=(2, 5))
decision = compare_options(activity, risks, options, mitigations, cost, n=N, seed=SEED,
                           constraints=Constraints(max_p_exceed_deadline=None))

print(f"Baseline T0 = {t0:.2f} days")
print("Percentiles:", {k: round(v, 2) for k, v in summary["percentiles"].items()})
print("E[delay] =", round(summary["expected_delay"], 2), "days; P(T > deadline) =", round(summary["p_exceed_deadline"], 3))
print("Event EMV:", [(x["risk_id"], round(x["emv"])) for x in event_emv(risks, cost)])
print("Sensitivity:", [(x["risk_id"], round(x["spearman_with_total_delay"], 2)) for x in sensitivity(base)])
print(decision["rule"])
for o in decision["options"]:
    print(f"  {o['option_id']:7s} TEC={o['total_expected_cost']:9.0f}  P90={o['P90']:6.2f}  Pexceed={o['p_exceed_deadline']:.3f}  admissible={o['admissible']}")
print(decision["statement"])

record = build_record(
    {"activity": activity, "risks": risks, "cost": cost, "mitigations": mitigations},
    {"summary": summary, "cost": cost_summary(base, cost), "matrix": classify(risks, t0, (0.02, 0.05, 0.10, 0.20)),
     "convergence": convergence(base), "decision": decision},
    seed=SEED, n=N, criterion=decision["criterion"])
out = Path(__file__).parent / "output"
out.mkdir(exist_ok=True)
(out / "masonry_demo_audit.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
print("audit record ->", out / "masonry_demo_audit.json")
