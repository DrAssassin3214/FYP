"""Independent manual-calculation validation of the FYP engine.

The 'manual' side below never imports app.*.  It reads only the INPUT numbers from the repo's shipped example case
(examples/example_analysis_case.json) and recomputes everything from closed-form formulas or from an exact
grid-convolution of the risk mixture distributions.  The tool side is then run and compared.
"""
import json, math, sys, time, itertools
from pathlib import Path
import numpy as np
from scipy import special, signal, stats

REPO = Path("/home/claude/drassassin3214/fyp")
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
sys.path.insert(0, str(REPO))

results = {}          # everything the report needs
checks = []           # (id, description, hand, tool, abs_diff, tol, passed)


def check(cid, desc, hand, tool, tol, note=""):
    d = abs(hand - tool)
    ok = d <= tol
    checks.append({"id": cid, "desc": desc, "hand": hand, "tool": tool, "abs_diff": d, "tol": tol, "pass": bool(ok), "note": note})
    return ok


# ------------------------------------------------------------------ inputs (read only)
case = json.load(open(REPO / "examples/example_analysis_case.json", encoding="utf-8-sig"))
T0 = case["activity"]["planned_duration_days"]["value"]
DL = case["activity"]["deadline_days"]["value"]
CD = case["cost"]["cost_per_delay_day"]["value"]
LD = case["cost"]["ld_per_day_after_deadline"]["value"]
R = {}
for r in case["risks"]:
    d = r["delay"]
    R[r["id"]] = dict(p=r["p"]["value"], kind=d["kind"], a=d["a"], m=d["m"], b=d["b"], lam=d.get("lam", 4.0))
MITS = {}
for m in case["mitigations"]:
    MITS[m["id"]] = m
print(f"inputs: T0={T0} deadline={DL} Cd={CD} LD={LD} risks={list(R)}")


# ------------------------------------------------------------------ hand formulas
def h_mean(d):
    k, a, m, b, lam = d["kind"], d["a"], d["m"], d["b"], d.get("lam", 4.0)
    if k == "pert": return (a + lam * m + b) / (lam + 2)
    if k == "triangular": return (a + m + b) / 3
    if k == "uniform": return (a + b) / 2
    return m


def h_var(d):
    k, a, m, b, lam = d["kind"], d["a"], d["m"], d["b"], d.get("lam", 4.0)
    if k == "pert":
        mu = (a + lam * m + b) / (lam + 2)
        return (mu - a) * (b - mu) / (lam + 3)          # identity for Beta-PERT, derived by hand
    if k == "triangular": return (a * a + m * m + b * b - a * m - a * b - m * b) / 18
    if k == "uniform": return (b - a) ** 2 / 12
    return 0.0


def h_cdf(d, x):
    """CDF of the conditional delay at x (vectorised) by an independent route (regularised incomplete beta / closed forms)."""
    k, a, m, b, lam = d["kind"], d["a"], d["m"], d["b"], d.get("lam", 4.0)
    x = np.asarray(x, float)
    if k == "fixed": return (x >= m).astype(float)
    if b == a: return (x >= a).astype(float)
    if k == "uniform": return np.clip((x - a) / (b - a), 0, 1)
    if k == "triangular":
        lo = (x - a) ** 2 / ((b - a) * (m - a)) if m > a else np.zeros_like(x)
        hi = 1 - (b - x) ** 2 / ((b - a) * (b - m)) if b > m else np.ones_like(x)
        return np.where(x <= a, 0.0, np.where(x < m, lo, np.where(x < b, hi, 1.0)))
    al = 1 + lam * (m - a) / (b - a); be = 1 + lam * (b - m) / (b - a)
    return special.betainc(al, be, np.clip((x - a) / (b - a), 0, 1))


# ======================================================================================== V1 distribution moments
print("\n== V1: distribution moments (hand closed form vs tool vs independent numerical integration)")
from app.engine.models import DelayDist
from app.engine.simulation import delay_ppf

dist_cases = {
    "PERT(1,3,8)": dict(kind="pert", a=1, m=3, b=8, lam=4.0),
    "PERT(1,2,6)": dict(kind="pert", a=1, m=2, b=6, lam=4.0),
    "PERT(0,1,3)": dict(kind="pert", a=0, m=1, b=3, lam=4.0),
    "PERT(1,3,8) lam=6": dict(kind="pert", a=1, m=3, b=8, lam=6.0),
    "PERT(2,2,9) m=a": dict(kind="pert", a=2, m=2, b=9, lam=4.0),
    "PERT(2,9,9) m=b": dict(kind="pert", a=2, m=9, b=9, lam=4.0),
    "Triangular(1,3,8)": dict(kind="triangular", a=1, m=3, b=8),
    "Triangular(0,0,4)": dict(kind="triangular", a=0, m=0, b=4),
    "Uniform(2,10)": dict(kind="uniform", a=2, m=6, b=10),
    "Fixed(4)": dict(kind="fixed", a=4, m=4, b=4),
}
N = 2_000_000
u = (np.arange(N) + 0.5) / N          # midpoint rule on the quantile function: mean = int_0^1 Q(u) du
v1 = []
for name, d in dist_cases.items():
    dd = DelayDist(d["kind"], d["a"], d["m"], d["b"], d.get("lam", 4.0))
    x = delay_ppf(dd, u)
    hm, hv = h_mean(d), h_var(d)
    row = {"case": name, "hand_mean": hm, "tool_mean": dd.mean(), "quad_mean": float(x.mean()),
           "hand_var": hv, "tool_var": dd.variance(), "quad_var": float(x.var())}
    # CDF round trip: F_hand(Q_tool(u)) should equal u  (independent CDF route)
    err = float(np.max(np.abs(h_cdf(d, x) - u))) if d["kind"] != "fixed" and d["b"] != d["a"] else 0.0
    row["max_cdf_roundtrip_err"] = err
    v1.append(row)
    check(f"V1-mean-{name}", f"mean {name}: hand vs tool formula", hm, dd.mean(), 1e-12)
    check(f"V1-var-{name}", f"variance {name}: hand vs tool formula", hv, dd.variance(), 1e-12)
    check(f"V1-qmean-{name}", f"mean {name}: hand vs integral of tool inverse-CDF", hm, float(x.mean()), 2e-4)
    check(f"V1-qvar-{name}", f"variance {name}: hand vs variance of tool inverse-CDF", hv, float(x.var()), 2e-3 * max(1, hv))
    check(f"V1-cdf-{name}", f"inverse-CDF round trip via independent CDF {name}", 0.0, err, 1e-5)
    print(f"  {name:20s} mean hand {hm:.6f} tool {dd.mean():.6f} quad {x.mean():.6f} | var hand {hv:.6f} tool {dd.variance():.6f} quad {x.var():.6f} | cdf-roundtrip {err:.2e}")
results["V1"] = v1

# ======================================================================================== V2 per-risk table, EMV
print("\n== V2: per-risk mean, EMV, expected delay, variance (hand vs tool)")
from app import analysis, service
pa = analysis.parse_analysis(case)
risks = pa["risks"]
from app.engine.emv import event_emv
from app.engine.simulation import analytic_moments
tool_emv = {r["risk_id"]: r for r in event_emv(risks, pa["cost"])}
v2 = []
for rid, d in R.items():
    mu = h_mean(d); emv_h = d["p"] * mu * CD
    t = tool_emv[rid]
    v2.append({"risk": rid, "p": d["p"], "abc": f"{d['a']}/{d['m']}/{d['b']}", "hand_mean": mu, "tool_mean": t["expected_delay_if_occurs_days"],
               "hand_emv": emv_h, "tool_emv": t["emv"]})
    check(f"V2-mean-{rid}", f"E[D|occurs] {rid}", mu, t["expected_delay_if_occurs_days"], 1e-12)
    check(f"V2-emv-{rid}", f"event EMV {rid} (INR)", emv_h, t["emv"], 1e-6)
    print(f"  {rid:8s} p={d['p']:<5} a/m/b={d['a']}/{d['m']}/{d['b']:<2} mean hand {mu:.4f} tool {t['expected_delay_if_occurs_days']:.4f} | EMV hand {emv_h:10.2f} tool {t['emv']:10.2f}")
results["V2"] = v2
E_delay_h = sum(d["p"] * h_mean(d) for d in R.values())
Var_h = sum(d["p"] * (h_var(d) + h_mean(d) ** 2) - d["p"] ** 2 * h_mean(d) ** 2 for d in R.values())
P_any_h = 1 - np.prod([1 - d["p"] for d in R.values()])
EMV_sum_h = sum(d["p"] * h_mean(d) * CD for d in R.values())
am = analytic_moments(risks)
check("V2-Edelay", "expected total delay (days)", E_delay_h, am["expected_delay"], 1e-12)
check("V2-Var", "variance of total delay", Var_h, am["variance"], 1e-12)
check("V2-EMVsum", "sum of event EMV (INR)", EMV_sum_h, sum(r["emv"] for r in tool_emv.values()), 1e-6)
print(f"  total: E[delay] hand {E_delay_h:.5f} tool {am['expected_delay']:.5f}; Var hand {Var_h:.5f} tool {am['variance']:.5f}; sum EMV hand {EMV_sum_h:.2f}; P(any) hand {P_any_h:.5f}")
results["V2_totals"] = {"E_delay": E_delay_h, "Var": Var_h, "sd": Var_h ** .5, "EMV_sum": EMV_sum_h, "P_any": float(P_any_h)}


# ======================================================================================== V3 exact distribution by convolution
H = 0.005


def risk_pmf(p, d, L):
    edges = (np.arange(L) - 0.5) * H
    edges[0] = -1.0                                   # absorb everything below 0.5H in cell 0
    cdf_hi = h_cdf(d, edges + H)                      # F at upper cell edge
    cdf_hi[-1] = 1.0
    cdf_lo = np.concatenate([[0.0], cdf_hi[:-1]])
    mass = np.clip(cdf_hi - cdf_lo, 0, None)
    mass /= mass.sum()
    pmf = p * mass
    pmf[0] += 1 - p
    return pmf


def total_pmf(risk_list):
    """risk_list: [(p, dist_dict)]; returns pmf of the SUM of delays on the grid H."""
    tot = np.array([1.0])
    for p, d in risk_list:
        L = int(math.ceil(d["b"] / H)) + 3
        tot = signal.fftconvolve(tot, risk_pmf(p, d, L))
        tot = np.clip(tot, 0, None); tot /= tot.sum()
    return tot


def metrics(pmf, t0, deadline, cd, ld):
    k = np.arange(len(pmf)); dvals = k * H
    ed = float((pmf * dvals).sum())
    cdf_edge = np.cumsum(pmf)                          # CDF at upper edge of cell k = (k+.5)H
    edges_up = (k + 0.5) * H
    def q(qq):
        i = int(np.searchsorted(cdf_edge, qq))
        lo = cdf_edge[i - 1] if i > 0 else 0.0
        frac = (qq - lo) / max(cdf_edge[i] - lo, 1e-300)
        return float(t0 + edges_up[i] - H + frac * H)
    over = max(deadline - t0, 0.0)
    p_exceed = float(pmf[dvals > over + 1e-9].sum() + 0.5 * pmf[np.abs(dvals - over) <= 1e-9].sum())
    e_ld_days = float((pmf * np.maximum(dvals - over, 0)).sum())
    e_cost = cd * ed + ld * e_ld_days
    return {"E_delay": ed, "P50": q(0.5), "P80": q(0.8), "P90": q(0.9), "P95": q(0.95), "p_exceed": p_exceed,
            "E_LD_days": e_ld_days, "E_cost": e_cost}


print("\n== V3: exact distribution by grid convolution (H = 0.005 d), all options")
base_list = [(d["p"], d) for d in R.values()]
pm = total_pmf(base_list)
mb = metrics(pm, T0, DL, CD, LD)
print(f"  ACCEPT exact: E[delay] {mb['E_delay']:.5f} (closed form {E_delay_h:.5f})  P90 {mb['P90']:.3f}  P(T>{DL}) {mb['p_exceed']:.4f}  E[LD days] {mb['E_LD_days']:.4f}  E[cost] {mb['E_cost']:.1f}")
check("V3-grid-mean", "grid-convolution mean vs closed-form sum p*mu (validates the exact reference itself)", E_delay_h, mb["E_delay"], 2e-3)
var_grid = float(((np.arange(len(pm)) * H) ** 2 * pm).sum() - mb["E_delay"] ** 2)
check("V3-grid-var", "grid-convolution variance vs closed form (validates the exact reference itself)", Var_h, var_grid, 2e-2)
p_none_grid = float(pm[0]); check("V3-grid-p0", "P(no risk occurs) grid vs product(1-p)", float(np.prod([1 - d["p"] for d in R.values()])), p_none_grid, 5e-4,
                                  "mass at zero also contains tiny mass of delays < H/2, so tolerance 5e-4")


def option_hand(mids):
    """Residual risk list for an option, built by hand from the case JSON (mitigation semantics: replace p and/or delay of the
    targeted risk; add secondary risks)."""
    rl = {rid: dict(p=d["p"], d=d) for rid, d in R.items()}
    extra = []
    cost = 0.0
    for mid in mids:
        m = MITS[mid]; cost += m["cost"]["value"]
        t = m["risk_id"]
        if m.get("p_after"): rl[t]["p"] = m["p_after"]["value"]
        if m.get("delay_after"):
            da = m["delay_after"]; rl[t]["d"] = dict(kind=da["kind"], a=da["a"], m=da["m"], b=da["b"], lam=da.get("lam", 4.0))
        for s in m.get("secondary_risks") or []:
            sd = s["delay"]; extra.append((s["p"]["value"], dict(kind=sd["kind"], a=sd["a"], m=sd["m"], b=sd["b"], lam=sd.get("lam", 4.0))))
    return [(v["p"], v["d"]) for v in rl.values()] + extra, cost


feasible = [mid for mid, m in MITS.items() if m.get("feasible", True) and (m.get("p_after") or m.get("delay_after"))]
infeasible = [mid for mid, m in MITS.items() if not m.get("feasible", True)]
opt_ids = [()]                                                   # ACCEPT
opt_ids += [(m,) for m in feasible]
for size in (2, 3):
    for combo in itertools.combinations(feasible, size):
        if len({MITS[m]["risk_id"] for m in combo}) == size:
            opt_ids.append(combo)
opt_ids += [(m,) for m in infeasible]
hand_opts = {}
for ids in opt_ids:
    rl, mc = option_hand(ids)
    mt = metrics(total_pmf(rl), T0, DL, CD, LD)
    mt["mit_cost"] = mc; mt["TEC"] = mc + mt["E_cost"]
    hand_opts["O-" + "+".join(ids) if ids else "ACCEPT"] = mt
best_hand = min((k for k, v in hand_opts.items() if k == "ACCEPT" or not any(i in k for i in infeasible)), key=lambda k: hand_opts[k]["TEC"])
print(f"  options hand-computed: {len(hand_opts)}; best by hand (feasible only): {best_hand}  TEC {hand_opts[best_hand]['TEC']:.1f}")
results["V3_hand_options"] = hand_opts

# tool side
import copy
from app.engine.decision import compare_options
from app.engine.emv import simulated_cost
from app.engine.simulation import simulate, summarise
from app.engine.decision import apply_mitigations


def tool_run(n, seed=12345):
    c = copy.deepcopy(case); c["simulation"] = {"n": n, "seed": seed, "criterion": "min_expected_total_cost"}
    t = time.time(); res = analysis.run_analysis(c); el = time.time() - t
    return res, el


tool10, el10 = tool_run(10_000)
tool200, el200 = tool_run(200_000)
print(f"  tool run time: n=10k {el10:.1f}s  n=200k {el200:.1f}s")
results["timing"] = {"n10000_s": el10, "n200000_s": el200}


def se_of_option(opt_row, n):
    ids = tuple(opt_row["mitigations"])
    mits = [pa["mitigations"][[m.mitigation_id for m in pa["mitigations"]].index(i)] for i in ids]
    resid = apply_mitigations(risks, mits)
    from app.engine.models import Activity
    act = Activity("A", "A", pa["planned"], deadline_days=pa["deadline"])
    res = simulate(act, resid, n, 12345)
    c = simulated_cost(res, pa["cost"], DL)
    return float(c.std(ddof=1) / math.sqrt(n)), summarise(res, deadline_days=DL)


from app.engine.models import Activity as _A
act_v3 = _A('A','A',pa['planned'],deadline_days=pa['deadline'])
rows3 = []
maxz10 = 0.0; maxz200 = 0.0
for o10, o200 in zip(tool10["decision"]["options"], tool200["decision"]["options"]):
    oid = o10["option_id"]
    h = hand_opts[oid]
    se10, s10 = se_of_option(o10, 10_000)
    se200, s200 = se_of_option(o200, 200_000)
    z10 = (o10["total_expected_cost"] - h["TEC"]) / se10 if se10 > 0 else 0.0
    z200 = (o200["total_expected_cost"] - h["TEC"]) / se200 if se200 > 0 else 0.0
    maxz10 = max(maxz10, abs(z10)); maxz200 = max(maxz200, abs(z200))
    ci = s200["percentile_ci95"]["P90"]
    rows3.append({"option": oid, "mit_cost": h["mit_cost"], "hand_TEC": h["TEC"], "tool_TEC_10k": o10["total_expected_cost"], "z10": z10,
                  "tool_TEC_200k": o200["total_expected_cost"], "z200": z200, "se200": se200,
                  "hand_P90": h["P90"], "tool_P90_200k": o200["P90"], "tool_P90_CI": ci,
                  "hand_pexc": h["p_exceed"], "tool_pexc_200k": o200["p_exceed_deadline"], "feasible": o10["feasible"],
                  "hand_Edelay": h["E_delay"], "tool_Edelay_200k": o200["expected_delay"]})
    check(f"V3-TEC10-{oid}", f"total expected cost {oid} (n=10k), |diff| <= 4 SE", h["TEC"], o10["total_expected_cost"], 4 * se10)
    check(f"V3-TEC200-{oid}", f"total expected cost {oid} (n=200k), |diff| <= 4 SE", h["TEC"], o200["total_expected_cost"], 4 * se200)
    check(f"V3-P90-{oid}", f"P90 duration {oid} (n=200k): hand inside tool 95% CI (+0.02 d grid slack)", h["P90"], o200["P90"],
          max(abs(ci[1] - ci[0]) / 2, 0.0) + 0.02)
    pe_se = math.sqrt(max(o200["p_exceed_deadline"] * (1 - o200["p_exceed_deadline"]), 1e-9) / 200_000)
    check(f"V3-pexc-{oid}", f"P(duration > deadline) {oid} (n=200k), |diff| <= 4 SE", h["p_exceed"], o200["p_exceed_deadline"], 4 * pe_se + 2e-3)
    check(f"V3-Edel-{oid}", f"expected delay {oid} (n=200k)", h["E_delay"], o200["expected_delay"], 0.06)
results["V3_rows"] = rows3
# second, independent seed at n=200k: is the largest z a fluke or a bias?
tool200b, _ = tool_run(200_000, seed=2024)
zb = []
for o in tool200b["decision"]["options"]:
    oid = o["option_id"]; h = hand_opts[oid]
    ids = tuple(o["mitigations"])
    mits_ = [pa["mitigations"][[m.mitigation_id for m in pa["mitigations"]].index(i)] for i in ids]
    resid = apply_mitigations(risks, mits_)
    res_ = simulate(act_v3, resid, 200_000, 2024)
    c_ = simulated_cost(res_, pa["cost"], DL); se_ = float(c_.std(ddof=1) / math.sqrt(200_000))
    zb.append((oid, (o["total_expected_cost"] - h["TEC"]) / se_))
results["V3_seed2024"] = {"max_abs_z": max(abs(z) for _, z in zb), "mean_z": float(np.mean([z for _, z in zb])), "worst": max(zb, key=lambda t: abs(t[1]))}
print("  second seed (2024, n=200k): max |z| %.2f, mean z %+.2f, worst %s" % (results["V3_seed2024"]["max_abs_z"], results["V3_seed2024"]["mean_z"], results["V3_seed2024"]["worst"]))
check("V3-seed2024", "second seed n=200k: all |z| of TEC vs exact <= 4", 0.0, results["V3_seed2024"]["max_abs_z"], 4.0)
print("  option z-scores seed 12345 (n=200k):", sorted([(round(r["z200"],2), r["option"]) for r in rows3], key=lambda t: -abs(t[0]))[:4])
results["V3_maxz"] = {"n10k": maxz10, "n200k": maxz200}
print(f"  max |z| of TEC vs exact: n=10k {maxz10:.2f}   n=200k {maxz200:.2f}")
sel_tool10, sel_tool200 = tool10["command"]["selected_option_id"], tool200["command"]["selected_option_id"]
print(f"  decision: hand-best {best_hand}; tool(n=10k) {sel_tool10} [{tool10['command']['command']}]; tool(n=200k) {sel_tool200} [{tool200['command']['command']}]")
srt = sorted((v["TEC"], k) for k, v in hand_opts.items() if k == "ACCEPT" or not any(i in k for i in infeasible))
print("  top-5 by hand:", [(k, round(t)) for t, k in srt[:5]], " gap 1st-2nd:", round(srt[1][0] - srt[0][0], 1))
results["V3_decision"] = {"hand_best": best_hand, "tool10k": sel_tool10, "tool200k": sel_tool200, "top5": [(k, t) for t, k in srt[:5]],
                          "command10k": tool10["command"]["command"], "stable_flag": tool10["decision_stability"]["stable"] if tool10["decision_stability"] else None}
check("V3-decision", "preferred option by hand == tool (n=200k)", 0.0 if best_hand == sel_tool200 else 1.0, 0.0, 0.0,
      f"hand {best_hand} / tool {sel_tool200}")

# ======================================================================================== V4 mitigation net benefit / break-even by hand
print("\n== V4: per-mitigation net benefit and break-even (hand vs tool)")
v4 = []
tool_checks = {c["mitigation_id"]: c for c in tool10["mitigation_checks"]}
for mid, m in MITS.items():
    t = m["risk_id"]; d = R[t]
    before = d["p"] * h_mean(d) * CD
    p2 = m["p_after"]["value"] if m.get("p_after") else d["p"]
    d2 = m["delay_after"] if m.get("delay_after") else d
    d2m = h_mean(dict(kind=d2["kind"], a=d2["a"], m=d2["m"], b=d2["b"], lam=d2.get("lam", 4.0)))
    after = p2 * d2m * CD
    sec = sum(s["p"]["value"] * h_mean(dict(kind=s["delay"]["kind"], a=s["delay"]["a"], m=s["delay"]["m"], b=s["delay"]["b"], lam=s["delay"].get("lam", 4.0))) * CD
              for s in m.get("secondary_risks") or [])
    net = before - after - sec - m["cost"]["value"]
    tc = tool_checks[mid]
    frac = m["cost"]["value"] / before
    v4.append({"mit": mid, "risk": t, "before": before, "after": after, "secondary": sec, "cost": m["cost"]["value"], "hand_net": net, "tool_net": tc["net_benefit"],
               "hand_required_reduction": frac, "tool_required_reduction": tc["break_even"]["required_reduction_fraction"]})
    check(f"V4-net-{mid}", f"net benefit {mid} (INR)", net, tc["net_benefit"], 1e-6)
    check(f"V4-be-{mid}", f"break-even required reduction {mid}", frac, tc["break_even"]["required_reduction_fraction"], 1e-12)
    pmax = d["p"] - m["cost"]["value"] / (h_mean(d) * CD)
    tmax = tc["break_even"]["max_p_after_if_only_p_changes"]
    if tmax is not None: check(f"V4-pmax-{mid}", f"max p-after that still pays {mid}", pmax, tmax, 1e-12)
    print(f"  {mid:7s} on {t:7s}: EMV before {before:9.1f} after {after:9.1f} secondary {sec:8.1f} cost {m['cost']['value']:7.0f} -> net hand {net:9.1f} tool {tc['net_benefit']:9.1f}  pays(tool)={tc['pays_for_itself']}")
results["V4"] = v4

# ======================================================================================== V5 matrix classification
print("\n== V5: matrix classification (hand function vs tool): example risks + exhaustive grid + edge hits")
from app.engine.matrix import probability_class, impact_class, matrix_level, classify
P_EDGES = (0.2, 0.4, 0.6, 0.8); I_EDGES = case["impact_bin_edges_fraction"]; LV = (5, 10, 15)


def h_pclass(p):  # lower-edge-inclusive
    return 1 + sum(p >= e - 1e-12 for e in P_EDGES)


def h_iclass(delay, base):
    r = delay / base
    return 1 + sum(r >= e - 1e-12 for e in I_EDGES)


def h_level(score):
    if score <= 5: return "Low"
    if score <= 10: return "Moderate"
    if score <= 15: return "High"
    return "Extreme"


rows5 = []
for rid, d in R.items():
    mu = h_mean(d); pc = h_pclass(d["p"]); ic = h_iclass(mu, T0); sc = pc * ic
    rows5.append({"risk": rid, "p": d["p"], "mean": mu, "ratio": mu / T0, "pc": pc, "ic": ic, "score": sc, "level": h_level(sc)})
tool_mx = {m["risk_id"]: m for m in service.run_case(case)["matrix"]}
mism = 0
for r in rows5:
    t = tool_mx[r["risk"]]
    ok = (t["p_class"], t["impact_class"], t["score"], t["level"]) == (r["pc"], r["ic"], r["score"], r["level"])
    mism += (not ok)
    print(f"  {r['risk']:8s} p={r['p']:<5} mean={r['mean']:.4f} ratio={r['ratio']:.4f} -> pc {r['pc']} ic {r['ic']} score {r['score']:2d} {r['level']:8s} | tool {t['p_class']} {t['impact_class']} {t['score']:2d} {t['level']}  {'OK' if ok else 'MISMATCH'}")
check("V5-example", "example risks: hand class/score/level == tool (count of mismatches)", 0, mism, 0)
results["V5_rows"] = rows5
# exhaustive: all 25 class pairs and level
lv_mis = sum(matrix_level(pc, ic) != h_level(pc * ic) for pc in range(1, 6) for ic in range(1, 6))
check("V5-level25", "all 25 (p-class x impact-class) cells: level hand == tool (mismatches)", 0, lv_mis, 0)
# random + exact-edge values
rng = np.random.default_rng(7)
ps = np.concatenate([rng.random(20000), np.array(P_EDGES), np.array([0.0, 1.0, 0.19999999, 0.2000001, 0.39999999999999997, 0.6000000000000001])])
pmis = sum(probability_class(float(p)) != h_pclass(float(p)) for p in ps)
check("V5-pclass", f"p-class on {len(ps)} values incl. exact edges: mismatches", 0, pmis, 0)
rs = np.concatenate([rng.random(20000) * 0.5, np.array(I_EDGES)])
imis = sum(impact_class(float(x) * 16, 16.0, I_EDGES) != h_iclass(float(x) * 16, 16.0) for x in rs)
check("V5-iclass", f"impact-class on {len(rs)} values incl. exact edges: mismatches", 0, imis, 0)
# float-trap: 1.6 days on 16 days (ratio 0.1 exactly?) ; 0.32/16 = 0.02
trap = impact_class(0.32, 16.0, I_EDGES), impact_class(0.8, 16.0, I_EDGES), impact_class(1.6, 16.0, I_EDGES), impact_class(3.2, 16.0, I_EDGES)
check("V5-trap", "ratios exactly on the 4 impact edges (0.32,0.8,1.6,3.2 d on 16 d) -> classes 2,3,4,5", 0, int(trap != (2, 3, 4, 5)), 0, f"got {trap}")
print(f"  exact-edge impact classes (expect 2,3,4,5): {trap};  p-class mismatches {pmis}/{len(ps)}; impact mismatches {imis}/{len(rs)}; level mismatches {lv_mis}/25")

# ======================================================================================== V6 rules engine, independent evaluator
print("\n== V6: rule engine (independent evaluator over data/rules_masonry.json vs tool)")
rules = json.load(open(REPO / "data/rules_masonry.json", encoding="utf-8-sig"))
facts = dict(case["facts"]); facts["planned_duration_days"] = T0
OPS = {"lt": lambda a, b: a < b, "le": lambda a, b: a <= b, "gt": lambda a, b: a > b, "ge": lambda a, b: a >= b, "eq": lambda a, b: a == b, "ne": lambda a, b: a != b}


def ev(c):
    if c["fact"] not in facts or facts[c["fact"]] is None: return None
    lhs = facts[c["fact"]]
    if c.get("other_fact"):
        if c["other_fact"] not in facts or facts[c["other_fact"]] is None: return None
        rhs = facts[c["other_fact"]]
    else:
        rhs = c["value"]
    return OPS[c["op"]](lhs, rhs)


hand_fired = {}
for r in rules:
    allr = [ev(c) for c in r.get("all_of") or []]; anyr = [ev(c) for c in r.get("any_of") or []]
    if all(x is True for x in allr) and ((not anyr) or any(x is True for x in anyr)):
        hand_fired[r["id"]] = (r["risk_id"], r["level"], r.get("priority", 0))
hand_flags = {}
for rid, (risk, level, pr) in hand_fired.items():
    hand_flags.setdefault(risk, []).append((pr, level, rid))
hand_level = {}
for risk, lst in hand_flags.items():
    top = max(x[0] for x in lst); levs = {x[1] for x in lst if x[0] == top}
    hand_level[risk] = levs.pop() if len(levs) == 1 else "conflict"
tr = service.run_case(case)["rules"]
tool_fired = {f["rule_id"] for f in tr["fired"]}
tool_level = {k: v["level"] for k, v in tr["flags"].items()}
check("V6-fired", "set of fired rules identical (symmetric difference size)", 0, len(set(hand_fired) ^ tool_fired), 0)
check("V6-levels", "per-risk resolved level identical (mismatches)", 0, sum(hand_level.get(k) != tool_level.get(k) for k in set(hand_level) | set(tool_level)), 0)
print(f"  rules {len(rules)}; fired by hand {len(hand_fired)} / tool {len(tool_fired)}; per-risk levels hand {hand_level}")
results["V6"] = {"n_rules": len(rules), "hand_fired": sorted(hand_fired), "tool_fired": sorted(tool_fired), "hand_level": hand_level, "tool_level": tool_level}
# plain-English spot checks, verified by reading the facts
spot = [("RL-LAB", "required_workers 6 > available_workers 5 -> fires"), ("RL-MAT", "stock 2 d <= lead 6 d -> fires")]
for rid, why in spot:
    check(f"V6-spot-{rid}", why, 1, int(rid in tool_fired), 0)

# ======================================================================================== V7 literature seed banding
print("\n== V7: literature-seed ranking and equal-count banding (independent recomputation from data/literature_seed.json)")
ls = json.load(open(REPO / "data/literature_seed.json", encoding="utf-8-sig"))
roles = {s["id"]: s["role"] for s in ls["studies"]}
obs = [r for r in ls["rows"] if roles.get(r["study"]) == "seed" and r.get("mapping") == "direct" and r.get("risk")]
byrs = {}
for o in obs: byrs.setdefault(o["risk"], {}).setdefault(o["study"], []).append(o["rii"])
mrii = {rk: float(np.mean([np.mean(v) for v in st.values()])) for rk, st in byrs.items()}
order = sorted(mrii, key=lambda k: (-mrii[k], k)); n = len(order)
cls = {k: 5 - ((order.index(k)) * 5) // n for k in order}
from app.literature_seed import seed_table
st = seed_table()
mis = [k for k in order if st[k]["class"] != cls[k] or abs(st[k]["mean_rii"] - round(mrii[k], 4)) > 1e-9 or st[k]["rank"] != order.index(k) + 1]
check("V7-seed", f"seed rank / mean RII / class for {n} seeded risks: mismatches", 0, len(mis), 0, f"{mis[:5]}")
counts = {c: sum(1 for v in cls.values() if v == c) for c in range(1, 6)}
print(f"  seeded risks {n}; class sizes {counts}; mismatches {len(mis)}")
results["V7"] = {"n_seeded": n, "class_sizes": counts}
# +1 step for an elevated rule flag
from app.literature_seed import seed_for
some = order[0]; low = order[-1]
a1 = seed_for(some, elevated=True); a2 = seed_for(low, elevated=True); a3 = seed_for(low, elevated=False)
check("V7-cap", "elevated flag raises probability class by 1, capped at 5 (top-ranked stays 5)", 5, a1["p_class"], 0)
check("V7-raise", "elevated flag on lowest class raises p-class 1->2, impact class unchanged", 2, a2["p_class"], 0)
check("V7-noflag", "no flag: p-class == impact-class == tier", a3["impact_class"], a3["p_class"], 0)

# ======================================================================================== V8 legacy productivity & norms
print("\n== V8: legacy productivity / India norms (hand vs tool)  [out of current scope, light check]")
from app.productivity.model import load_models
from app.productivity.india_norms import load_norms, crew_output_per_day
from app.productivity.predictor import build_baseline, CrewConversion, to_m2_per_day_per_crew
models = load_models(); norms = load_norms()
m3 = models["M03-brick-rework"]; pred = m3.predict({"rework_cost_pct": 5.0})
check("V8-lin", "linear model M03: 34.36 - 1.71*5 = 25.81 m2/day (crew of 2)", 34.36 - 1.71 * 5.0, pred.value, 1e-12)
mp = models["P1-01-ouga-kampala"]
pr2 = mp.predict({"work_height_m": 3.0, "porters_per_layer": 2.0, "exed": 4.0})
check("V8-lin3", "linear model P1-01: 0.53 - 0.08*3 + 0.4*2 + 0.36*4 = 2.53 m2/hour/worker", 0.53 - 0.08 * 3 + 0.4 * 2 + 0.36 * 4, pr2.value, 1e-12)
y, w = to_m2_per_day_per_crew(pred, m3, CrewConversion(workers_per_crew=4))
check("V8-crew", "M03 scaled to a crew of 4 (linear): 25.81/2*4 = 51.62 m2/day", 25.81 / 2 * 4, y, 1e-9)
y2, _ = to_m2_per_day_per_crew(pr2, mp, CrewConversion(workers_per_crew=3, hours_per_day=8.0))
check("V8-hours", "P1-01: m2/hour/worker * 8 h * 3 workers", 2.53 * 8 * 3, y2, 1e-9)
bl = build_baseline(1000.0, 2, manual={"min": 20.0, "most_likely": 25.0, "max": 30.0, "source": "User Input"})
check("V8-t0", "baseline mode = 1000/(2*25) = 20 d", 20.0, bl.planned_days, 1e-12)
check("V8-tmin", "baseline min = 1000/(2*30)", 1000 / 60, bl.dist.a, 1e-12)
check("V8-tmax", "baseline max = 1000/(2*20)", 1000 / 40, bl.dist.b, 1e-12)
n1 = norms["IS7272-1brick"]; co = crew_output_per_day(n1, 6)
check("V8-is7272", "IS 7272 1-brick: 6 masons / 0.94 mason-days per m3 = 6.383 m3/day", 6 / 0.94, co.output_per_day, 1e-12)
n2 = norms["CPWD-FPS-superstructure-1brick"]; co2 = crew_output_per_day(n2, 6)
check("V8-cpwd", "CPWD superstructure: 6 masons / (0.47+0.47) = 6.383 m3/day", 6 / 0.94, co2.output_per_day, 1e-12)
req_maz = 6 * 1.8 / 0.94; check("V8-support", "required mazdoor for 6 masons = 6*1.8/0.94 = 11.489", req_maz, co.required_support["mazdoor"], 1e-12)

# ======================================================================================== V9 sampling consistency over many seeds
print("\n== V9: statistical consistency over 200 independent seeds (n = 10,000 each)")
from app.engine.models import Activity
act = Activity("A", "A", pa["planned"], deadline_days=pa["deadline"])
z_mean, z_pany, z_p90 = [], [], []
p90_hand = mb["P90"]; cover_mean = cover_p90 = 0
sd_hand = Var_h ** .5
for sd in range(1000, 1200):
    res = simulate(act, risks, 10_000, sd)
    s = summarise(res, deadline_days=DL)
    se = s["std"] / math.sqrt(10_000)
    z_mean.append((s["expected_delay"] - E_delay_h) / se)
    pa_hat = s["p_any_delay"]; z_pany.append((pa_hat - P_any_h) / math.sqrt(P_any_h * (1 - P_any_h) / 10_000))
    lo, hi = s["percentile_ci95"]["P90"]; cover_p90 += (lo <= p90_hand <= hi)
    cover_mean += (abs(s["expected_delay"] - E_delay_h) <= 1.96 * se)
zm = np.array(z_mean); zp = np.array(z_pany)
print(f"  mean: avg z {zm.mean():+.3f} (expect ~0, SE 0.07), sd z {zm.std():.3f} (expect ~1), 95% CI coverage {cover_mean/200:.1%}")
print(f"  P(any delay): avg z {zp.mean():+.3f}, sd z {zp.std():.3f};  P90: hand value inside tool 95% CI in {cover_p90/200:.1%} of runs")
check("V9-zmean", "mean of z-scores of E[delay] over 200 seeds is ~0 (|avg| <= 0.30 ~ 4 SE)", 0.0, float(zm.mean()), 0.30)
check("V9-zsd", "sd of z-scores of E[delay] ~ 1 (reported standard error is honest)", 1.0, float(zm.std()), 0.2)
check("V9-cov", "95% CI coverage of the analytic mean over 200 seeds (92%..98%)", 0.95, cover_mean / 200, 0.035)
check("V9-covp90", "P90 CI coverage of the exact P90 over 200 seeds (>= 90%)", 0.95, cover_p90 / 200, 0.05)
check("V9-pany", "mean z of P(any delay) ~ 0", 0.0, float(zp.mean()), 0.30)
results["V9"] = {"avg_z_mean": float(zm.mean()), "sd_z_mean": float(zm.std()), "cov_mean": cover_mean / 200, "cov_p90": cover_p90 / 200, "avg_z_pany": float(zp.mean())}

# ======================================================================================== V10 correlation (Gaussian copula) check
print("\n== V10: occurrence correlation (Gaussian copula) vs bivariate-normal probability")
from app.engine.models import Risk, Param, Source
mk = lambda rid, p: Risk(rid, rid, Param(p, Source.ASSUMPTION), DelayDist("fixed", 0, 1, 1))
rA, rB = mk("A", 0.40), mk("B", 0.30)
v10 = []
for rho in (-0.5, 0.0, 0.6, 0.95):
    res = simulate(Activity("X", "X", Param(10, Source.ASSUMPTION)), [rA, rB], 600_000, 99, {("A", "B"): rho})
    pa_, pb_ = res.occurrence[:, 0].mean(), res.occurrence[:, 1].mean()
    joint = (res.occurrence[:, 0] & res.occurrence[:, 1]).mean()
    mv = stats.multivariate_normal(mean=[0, 0], cov=[[1, rho], [rho, 1]])
    hand_joint = float(mv.cdf([stats.norm.ppf(0.40), stats.norm.ppf(0.30)]))
    se = math.sqrt(hand_joint * (1 - hand_joint) / 600_000)
    v10.append({"rho": rho, "hand_joint": hand_joint, "tool_joint": float(joint), "marg_A": float(pa_), "marg_B": float(pb_)})
    check(f"V10-joint-{rho}", f"P(A and B) at rho={rho}: bivariate-normal CDF vs tool, 4 SE", hand_joint, float(joint), 4 * se + 1e-4)
    check(f"V10-margA-{rho}", f"marginal P(A)=0.40 preserved at rho={rho}", 0.40, float(pa_), 4 * math.sqrt(.24 / 600_000))
    print(f"  rho={rho:+.2f}: P(A&B) hand {hand_joint:.4f} tool {joint:.4f}; marginals {pa_:.4f}, {pb_:.4f}")
results["V10"] = v10

# ======================================================================================== V11 repo's shipped example files = generators
print("\n== V11: shipped example JSON files equal the generator functions")
ex1 = json.load(open(REPO / "examples/example_case.json", encoding="utf-8-sig")); ex2 = json.load(open(REPO / "examples/example_analysis_case.json", encoding="utf-8-sig"))
same1 = ex1 == json.loads(json.dumps(service.example_case())); same2 = ex2 == json.loads(json.dumps(service.example_analysis_case()))
print(f"  example_case.json == service.example_case(): {same1};  example_analysis_case.json == example_analysis_case(): {same2}")
check("V11-ex1", "examples/example_case.json equals service.example_case()", 1, int(same1), 0)
check("V11-ex2", "examples/example_analysis_case.json equals example_analysis_case()", 1, int(same2), 0)
results["V11"] = {"ex1": same1, "ex2": same2}

# ======================================================================================== summary
npass = sum(c["pass"] for c in checks)
print(f"\nTOTAL manual-validation checks: {len(checks)}   passed: {npass}   failed: {len(checks) - npass}")
for c in checks:
    if not c["pass"]:
        print("  FAIL", c["id"], c["desc"], "hand", c["hand"], "tool", c["tool"], "diff", c["abs_diff"], "tol", c["tol"], c["note"])
json.dump({"checks": checks, "results": results}, open(OUT / "v1_results.json", "w"), indent=1, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o))
