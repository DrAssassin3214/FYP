"""Independent re-computation of the ILLUSTRATIVE example (no use of app.engine code for the arithmetic).
Compares with app.service.run_case / run_analysis. All inputs are the ILLUSTRATIVE placeholders of
app.service.example_case (Source: Assumption)."""
import json, math, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from app import service

case = service.example_case()
planned = case["activity"]["planned_duration_days"]["value"]
edges = case["impact_bin_edges_fraction"]
pe = [0.2, 0.4, 0.6, 0.8]
def cls(x, e): return 1 + sum(1 for t in e if x >= t - 1e-12)
rows = []
for r in case["risks"]:
    p = r["p"]["value"]; d = r["delay"]; a, m, b = d["a"], d["m"], d["b"]
    mean = (a + 4*m + b) / 6
    pc, ic = cls(p, pe), cls(mean/planned, edges)
    sc = pc*ic
    lvl = "Low" if sc <= 5 else "Moderate" if sc <= 10 else "High" if sc <= 15 else "Extreme"
    rows.append(dict(id=r["id"], p=p, a=a, m=m, b=b, mean=mean, ratio=mean/planned, pc=pc, ic=ic, score=sc, level=lvl, emv=p*mean*8000))
tool = {x["risk_id"]: x for x in service.run_case(case)["matrix"]}
print("risk  p     a/m/b   mean   ratio   pc ic score level | tool: mean pc ic score level  match")
allmatch = True
for h in rows:
    t = tool[h["id"]]
    ok = (abs(t["expected_delay_if_occurs_days"]-h["mean"])<1e-9 and t["p_class"]==h["pc"] and t["impact_class"]==h["ic"] and t["score"]==h["score"] and t["level"]==h["level"])
    allmatch &= ok
    print(f'{h["id"]:7}{h["p"]:<5}{h["a"]}/{h["m"]}/{h["b"]:<3}{h["mean"]:7.4f}{h["ratio"]:8.4f}{h["pc"]:4}{h["ic"]:3}{h["score"]:5} {h["level"]:9}| {t["expected_delay_if_occurs_days"]:.4f} {t["p_class"]} {t["impact_class"]} {t["score"]} {t["level"]} {ok}')
print("ALL MATCH:", allmatch)
ed = sum(h["p"]*h["mean"] for h in rows)
print("sum p*mean (expected delay, days) =", round(ed, 5))
print("sum event EMV at 8000/day =", round(ed*8000, 2))
pnone = math.prod(1-h["p"] for h in rows)
print("P(at least one risk occurs) analytic =", round(1-pnone, 5))
an = service.run_analysis(service.example_analysis_case())
s = an["summary"]
print("TOOL: expected_delay", round(s["expected_delay"], 4), "SE", round(s["mean_se"], 4), "p_any_delay", s["p_any_delay"], "P90 duration", round(s["percentiles"]["P90"], 3), "P(T>20)", s["p_exceed_deadline"], "E[cost]", round(an["cost"]["expected_cost"], 1))
print("TOOL event EMV sum", round(sum(x["emv"] for x in an["event_emv"]), 2))
# independent Monte Carlo (own sampler, different seed, 200000 runs)
rng = np.random.default_rng(2026)
N = 200_000
T = np.full(N, float(planned))
for h in rows:
    occ = rng.random(N) < h["p"]
    al = 1 + 4*(h["m"]-h["a"])/(h["b"]-h["a"]); be = 1 + 4*(h["b"]-h["m"])/(h["b"]-h["a"])
    D = h["a"] + (h["b"]-h["a"])*rng.beta(al, be, N)
    T += occ*D
dl = 20
cost = 8000*(T-planned) + 5000*np.maximum(T-dl, 0)
print(f"INDEPENDENT MC (N={N}): E[delay]={np.mean(T-planned):.4f} (SE {np.std(T)/math.sqrt(N):.4f}), P(T>dl)={np.mean(T>dl):.4f}, P90={np.quantile(T,.9):.3f}, E[cost]={cost.mean():.0f}, P(any)={np.mean(T>planned):.4f}")
print("TOOL repeated with other seeds (n=10000): seed, p_any_delay, expected_delay")
for sd in (1, 2, 3, 4, 5, 6):
    c = service.example_analysis_case(); c["simulation"]["seed"] = sd
    s2 = service.run_analysis(c)["summary"]; print(sd, s2["p_any_delay"], round(s2["expected_delay"], 3))
c = service.example_analysis_case(); c["simulation"]["n"] = 200000
s3 = service.run_analysis(c)["summary"]; print("TOOL n=200000:", s3["p_any_delay"], round(s3["expected_delay"], 4), s3["p_exceed_deadline"], round(s3["percentiles"]["P90"], 3))
rng = np.random.default_rng(7); N2 = 4_000_000
tot = np.zeros(N2)
for h in rows:
    al = 1 + 4*(h["m"]-h["a"])/(h["b"]-h["a"]); be = 1 + 4*(h["b"]-h["m"])/(h["b"]-h["a"])
    tot += (rng.random(N2) < h["p"]) * (h["a"] + (h["b"]-h["a"])*rng.beta(al, be, N2))
print(f"INDEPENDENT MC (N={N2}): E[delay]={tot.mean():.4f} (SE {tot.std()/N2**.5:.4f}) vs analytic {ed:.4f}")
# ---- literature tier worked example (R-TOOL rank 12 of 30, R-WX rank 24 of 30), rule flags as in the text
from app import literature_seed as ls
tb = ls.seed_table()
for rid, flagged in (("R-TOOL", True), ("R-WX", True)):
    rank = tb[rid]["rank"]; tier = 5 - (5*(rank-1))//30
    pc = min(5, tier+1) if flagged else tier
    print(f"TIER {rid}: mean RII {tb[rid]['mean_rii']} rank {rank} -> hand tier {tier} (tool {tb[rid]['class']}); flagged elevated -> p class {pc}, impact class {tier}, score {pc*tier}")
