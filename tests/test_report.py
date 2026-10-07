from pathlib import Path

from app.engine.decision import Option, compare_options
from app.engine.models import Activity, CostModel, DelayDist, Mitigation, Param, Risk, RiskStatus, Source
from app.engine.simulation import simulate
from app.reporting.report import generate_report, plot_distributions

A = Source.ASSUMPTION


def test_report_contains_required_sections_and_assumptions(tmp_path: Path):
    act = Activity("A", "Test activity", Param(10, A), deadline_days=Param(12, A))
    risks = [Risk("R1", "Shortage", Param(0.4, A), DelayDist("pert", 1, 2, 5), status=RiskStatus.LITERATURE_SUPPORTED, evidence_ids=("M01",))]
    cost = CostModel(Param(1000, Source.USER))
    mits = [Mitigation("M1", "R1", "Buffer", cost=Param(500, Source.USER), p_after=Param(0.1, Source.EXPERT), evidence_ids=("M01",))]
    dec = compare_options(act, risks, [Option("O1", "Buffer", ("M1",))], mits, cost, n=2000, seed=1)
    base = simulate(act, risks, 2000, 1)
    fig = plot_distributions(base, simulate(act, risks, 2000, 1), tmp_path / "f.png", 12)
    assert fig.exists()
    md = generate_report(act, risks, cost, mits, base, dec, (0.05, 0.1, 0.2, 0.4), {"M01": "Karthik & Rao 2019"}, "f.png")
    for heading in ("## 1. Executive summary", "## 7. Risk matrix", "## 10. Simulation results", "## 17. Decision analysis",
                    "## 18. Assumptions", "## 19. Limitations", "## 20. Evidence references"):
        assert heading in md
    assert "Karthik & Rao 2019" in md
    assert "Assumption" in md and "Expert Judgment" in md
    assert "not a prediction validated" in md
    low = md.lower()
    assert "is optimal" not in low and "the optimal" not in low and "optimal option" not in low
