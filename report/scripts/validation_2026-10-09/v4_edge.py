"""Targeted edge-case probes, hypotheses from code reading, and report-vs-code drift.  Never edits the repo."""
import copy, json, math, re, sys, time, zlib, itertools, collections
from pathlib import Path
import numpy as np
from scipy import special, signal

REPO = Path("/home/claude/drassassin3214/fyp"); SP = Path(sys.argv[1]); sys.path.insert(0, str(REPO))
from app import service, analysis
from app.engine.models import Activity, DelayDist, Param, Risk, Source, CostModel
from app.engine.simulation import simulate, summarise

A = "Assumption"
E = []


def rec(area, test, ok, detail=""):
    E.append({"area": area, "test": test, "pass": bool(ok), "detail": str(detail)[:500]})
    print(("PASS " if ok else "FAIL ") + f"[{area}] {test}" + (f" -> {detail}" if detail and not ok else (f"  ({detail})" if detail else "")), flush=True)


def mk(risks, T0=16, deadline=None, cd=8000, ld=None, mits=None, n=3000, seed=1, **extra):
    risks_json = []
    for i, r in enumerate(risks):
        p, d = r[0], r[1]
        risks_json.append({"id": r[2] if len(r) > 2 else f"R{i}", "name": f"r{i}", "p": {"value": p, "source": A}, "delay": {**d, "source": A}})
    c = {"project": {"name": "t"}, "activity": {"id": "A", "name": "a", "planned_duration_days": {"value": T0, "source": A}}, "facts": {}, "risks": risks_json,
         "use_literature_seed": False, "impact_bin_edges_fraction": [0.02, 0.05, 0.1, 0.2], "impact_bin_edges_source": {"source": A, "note": ""},
         "cost": {"cost_per_delay_day": {"value": cd, "source": A}, "currency": "INR"}, "simulation": {"n": n, "seed": seed}, "mitigations": mits or []}
    if deadline is not None: c["activity"]["deadline_days"] = {"value": deadline, "source": A}
    if ld is not None: c["cost"]["ld_per_day_after_deadline"] = {"value": ld, "source": A}
    c.update(extra); return c


PERT = lambda a, m, b, lam=None: {"kind": "pert", "a": a, "m": m, "b": b, **({"lam": lam} if lam else {})}
FIX = lambda m: {"kind": "fixed", "m": m}


def run(c):
    try:
        return analysis.run_analysis(c), None
    except service.CaseError as e:
        return None, ("CaseError", e.problems)
    except Exception as e:
        return None, (type(e).__name__, str(e)[:200])


def strict(o):
    try: json.dumps(o, allow_nan=False); return True
    except Exception: return False


# ---------------------------------------------------------------- E1-E7 boundaries with hand answers
r, e = run(mk([(0.0, PERT(1, 3, 8)), (0.0, PERT(1, 2, 6))]))
rec("EDGE", "all p = 0: delay 0, P(any)=0, P90 = planned, cost 0, no NaN",
    r and r["summary"]["expected_delay"] == 0 and r["summary"]["p_any_delay"] == 0 and r["summary"]["percentiles"]["P90"] == 16 and r["cost"]["expected_cost"] == 0 and strict(r), e or "")
rec("EDGE", "all p = 0 and no mitigations -> 'NO RESPONSE EVALUATED' (not a false 'ACCEPT')", r and r["command"]["command"] == "NO RESPONSE EVALUATED", r and r["command"]["command"])
r, e = run(mk([(1.0, FIX(2), "A1"), (1.0, FIX(3), "A2")], deadline=20, ld=1000))
rec("EDGE", "p = 1, fixed delays 2+3: duration exactly 21, cost = 8000*5 + 1000*1 = 41000",
    r and abs(r["summary"]["mean"] - 21) < 1e-12 and r["summary"]["std"] == 0 and abs(r["cost"]["expected_cost"] - 41000) < 1e-6 and r["summary"]["p_exceed_deadline"] == 1.0, e or (r and (r["summary"]["mean"], r["cost"]["expected_cost"])))
r, e = run(mk([(0.5, PERT(1, 2, 3))], n=1)); rec("EDGE", "n = 1 runs without error (std/CI degenerate cases)", r is not None and strict(r), e)
r, e = run(mk([(0.5, PERT(1, 2, 3))], n=200_000)); rec("EDGE", "n = 200000 (upper limit) accepted", r is not None, e)
r, e = run(mk([(0.5, PERT(1, 2, 3))], n=200_001)); rec("EDGE", "n = 200001 rejected with a message", e and e[0] == "CaseError", e)
for bad in (0, -5, 2.5, "x", True):
    c = mk([(0.5, PERT(1, 2, 3))]); c["simulation"]["n"] = bad; r, e = run(c); rec("EDGE", f"n = {bad!r} rejected cleanly", e and e[0] == "CaseError", e)
for bad in (-1, 2 ** 31, 1.5):
    c = mk([(0.5, PERT(1, 2, 3))]); c["simulation"]["seed"] = bad; r, e = run(c); rec("EDGE", f"seed = {bad!r} rejected cleanly", e and e[0] == "CaseError", e)
c = mk([(0.5, PERT(1, 2, 3))]); c["simulation"]["seed"] = 2 ** 31 - 1; r, e = run(c); rec("EDGE", "seed = 2^31-1 accepted", r is not None, e)
r, e = run(mk([(0.4, PERT(2, 2, 2))])); rec("EDGE", "degenerate PERT a=m=b=2 -> every occurrence delays exactly 2 d", r and abs(r["summary"]["expected_delay"] - 0.8) < 0.06, e or "")
r, e = run(mk([(0.5, PERT(0, 0, 0))])); rec("EDGE", "zero-delay risk: delay 0, P(any delay)=0", r and r["summary"]["p_any_delay"] == 0 and r["summary"]["expected_delay"] == 0, e or "")
r, e = run(mk([(0.5, PERT(1e9, 2e9, 3e9))], cd=1e12)); rec("EDGE", "huge values (1e9 d, 1e12 INR/d): finite, strict JSON", r is not None and strict(r), e)
r, e = run(mk([(1e-12, PERT(1, 2, 3))])); rec("EDGE", "p = 1e-12 runs; matrix class 1", r is not None and strict(r), e)
r, e = run(mk([(0.5, PERT(1, 2, 3, lam=1e6)), (0.5, PERT(1, 2, 3, lam=1e-9))])); rec("EDGE", "PERT lambda extremes 1e6 and 1e-9 give finite results", r is not None and strict(r) and np.isfinite(r["summary"]["mean"]), e)
r, e = run(mk([(0.5, PERT(1, 2, 3, lam=0))])); rec("EDGE", "PERT lambda = 0 rejected", e and e[0] == "CaseError", e)
r, e = run(mk([(0.5, PERT(3, 2, 1))])); rec("EDGE", "a > m > b rejected", e and e[0] == "CaseError", e)

# deadline semantics, hand answer
risks = [(0.5, PERT(1, 3, 8), "X1"), (0.3, PERT(1, 2, 6), "X2")]
mu = lambda a, m, b: (a + 4 * m + b) / 6
Ed = 0.5 * mu(1, 3, 8) + 0.3 * mu(1, 2, 6)
r, e = run(mk(risks, T0=16, deadline=10, cd=0, ld=1000, n=200_000))   # deadline below planned: 6 d overrun always + delay
hand = 1000 * (6 + Ed)
rec("EDGE", "deadline < planned duration: LD charged on (baseline overrun + delay); E[cost] = LD*(6+E[D])", r and abs(r["cost"]["expected_cost"] - hand) < 4 * r["cost"]["std"] / math.sqrt(200_000) + 1, (r and r["cost"]["expected_cost"], hand))
r, e = run(mk(risks, T0=16, deadline=16, cd=0, ld=1000, n=100_000))
pany = 1 - 0.5 * 0.7
rec("EDGE", "deadline == planned: P(exceed) equals P(any delay) = 1-(0.5)(0.7) = 0.65", r and abs(r["summary"]["p_exceed_deadline"] - pany) < 0.01, r and r["summary"]["p_exceed_deadline"])
c = mk(risks, ld=1000); r, e = run(c); rec("EDGE", "LD > 0 with no deadline rejected with a message", e and e[0] == "CaseError", e)
c = mk(risks, deadline=0); r, e = run(c); rec("EDGE", "deadline = 0 rejected", e and e[0] == "CaseError", e)
c = mk(risks, T0=0); r, e = run(c); rec("EDGE", "planned duration = 0 rejected", e and e[0] == "CaseError", e)
c = mk([]); r, e = run(c); rec("EDGE", "empty risk register rejected with a message", e and e[0] == "CaseError", e)
c = mk(risks, cd=-1); r, e = run(c); rec("EDGE", "negative cost per day rejected", e and e[0] == "CaseError", e)
c = mk(risks, cd=0); r, e = run(c); rec("EDGE", "cost per day = 0 accepted (all costs 0, no divide-by-zero)", r is not None and strict(r), e)

# ---------------------------------------------------------------- mitigation / option / constraint semantics
M = lambda mid, rid, cost, **kw: {"id": mid, "risk_id": rid, "action": mid, "cost": {"value": cost, "source": A}, **kw}
base = [(0.5, PERT(1, 3, 8), "X1"), (0.3, PERT(1, 2, 6), "X2")]
c = mk(base, mits=[M("M1", "X1", 100, p_after={"value": 0.1, "source": A}), M("M2", "NOPE", 100, p_after={"value": 0.1, "source": A})]); r, e = run(c)
rec("MITIG", "mitigation targeting an unknown risk rejected", e and e[0] == "CaseError", e)
c = mk(base, mits=[M("M1", "X1", 100, p_after={"value": 1.5, "source": A})]); r, e = run(c); rec("MITIG", "p_after = 1.5 rejected", e and e[0] == "CaseError", e)
c = mk(base, mits=[M("M1", "X1", -5, p_after={"value": 0.1, "source": A})]); r, e = run(c); rec("MITIG", "negative mitigation cost rejected", e and e[0] == "CaseError", e)
c = mk(base, mits=[M("M1", "X1", 100, p_after={"value": 0.1, "source": A}), M("M1", "X2", 100, p_after={"value": 0.1, "source": A})]); r, e = run(c); rec("MITIG", "duplicate mitigation id rejected", e and e[0] == "CaseError", e)
c = mk(base, mits=[M("M1", "X1", 100)]); r, e = run(c)
rec("MITIG", "mitigation with no modelled effect is left out and reported (not silently simulated)", r and r["command"]["command"] == "NO RESPONSE EVALUATED" and any("no modelled effect" in w for w in r["warnings"]), e or (r and r["warnings"]))
c = mk(base, mits=[M("M1", "X1", 100, p_after={"value": 0.1, "source": A}), M("M2", "X1", 50, p_after={"value": 0.2, "source": A})],
       options=[{"id": "BOTH", "label": "both", "mitigation_ids": ["M1", "M2"]}]); r, e = run(c)
rec("MITIG", "explicit option with two responses to the same risk rejected", e and e[0] == "CaseError", e)
c = mk(base, mits=[M("M1", "X1", 0, p_after={"value": 0.0, "source": A})]); r, e = run(c)
rec("MITIG", "zero-cost mitigation that removes the risk -> AUTHORIZE MITIGATION, cost/day-avoided is null not inf", r and r["command"]["command"] == "AUTHORIZE MITIGATION" and strict(r), e or "")
c = mk(base, mits=[M("M1", "X1", 10 ** 9, p_after={"value": 0.0, "source": A})]); r, e = run(c)
rec("MITIG", "absurdly expensive mitigation -> ACCEPT RISK", r and r["command"]["command"] == "ACCEPT RISK", e or (r and r["command"]["command"]))
c = mk(base, mits=[M("M1", "X1", 100, p_after={"value": 0.1, "source": A})], constraints={"max_mitigation_budget": 0}); r, e = run(c)
rec("MITIG", "budget = 0 removes every paid response; ACCEPT remains selected", r and r["command"]["command"] == "ACCEPT RISK", e or "")
c = mk(base, deadline=17, ld=1000, mits=[M("M1", "X1", 100, p_after={"value": 0.1, "source": A})], constraints={"max_p_exceed_deadline": 0.0}); r, e = run(c)
rec("MITIG", "impossible deadline-probability limit (0.0) -> NO ADMISSIBLE OPTION", r and r["command"]["command"] == "NO ADMISSIBLE OPTION" and r["command"]["selected_option_id"] is None, e or (r and r["command"]["command"]))
for crit in ("min_p90_duration", "min_deadline_exceedance"):
    c = mk(base, deadline=20, ld=1000, mits=[M("M1", "X1", 100, p_after={"value": 0.1, "source": A})]); c["simulation"]["criterion"] = crit
    r, e = run(c); rec("MITIG", f"criterion {crit} selects the response that lowers it", r and r["command"]["selected_option_id"] == "O-M1", e or (r and r["command"]["selected_option_id"]))
c = mk(base, mits=[M("M1", "X1", 100, p_after={"value": 0.1, "source": A})]); c["simulation"]["criterion"] = "min_deadline_exceedance"; r, e = run(c)
rec("MITIG", "min_deadline_exceedance without a deadline rejected", e and e[0] == "CaseError", e)

# ---------------------------------------------------------------- correlation input
for rho, label in ((1.0, "rho = 1 (singular)"), (-1.0, "rho = -1 (singular)"), (1.5, "rho = 1.5"), ("x", "rho = 'x'")):
    c = mk(base); c["simulation"]["correlation"] = [{"a": "X1", "b": "X2", "rho": rho}]; r, e = run(c)
    rec("CORR", f"{label} rejected with a message", e and e[0] == "CaseError", e)
c = mk(base); c["simulation"]["correlation"] = [{"a": "X1", "b": "X2", "rho": 0.999}]; r, e = run(c); rec("CORR", "rho = 0.999 accepted (strict positive definite)", r is not None and strict(r), e)
c = mk(base); c["simulation"]["correlation"] = [{"a": "X1", "b": "X1", "rho": 0.5}]; r, e = run(c); rec("CORR", "self-correlation rejected", e and e[0] == "CaseError", e)
c = mk(base); c["simulation"]["correlation"] = [{"a": "X1", "b": "X2", "rho": 0.3}, {"a": "X2", "b": "X1", "rho": 0.6}]; r, e = run(c); rec("CORR", "conflicting duplicate pair (0.3 vs 0.6) rejected", e and e[0] == "CaseError", e)
# positive correlation must widen the spread of total delay (variance of sum of positively correlated Bernoullis)
a0 = mk(base, n=100_000); a1 = copy.deepcopy(a0); a1["simulation"]["correlation"] = [{"a": "X1", "b": "X2", "rho": 0.8}]
r0, _ = run(a0); r1, _ = run(a1)
rec("CORR", "positive occurrence correlation (0.8) raises the std of duration and leaves the mean unchanged", r1["summary"]["std"] > r0["summary"]["std"] and abs(r1["summary"]["expected_delay"] - r0["summary"]["expected_delay"]) < 0.05,
    (r0["summary"]["std"], r1["summary"]["std"], r0["summary"]["expected_delay"], r1["summary"]["expected_delay"]))

# ---------------------------------------------------------------- hypothesis 1: CRC32-keyed random streams
rec("RNG", "sanity: crc32('plumless') == crc32('buckeroo') (known collision pair)", zlib.crc32(b"plumless") == zlib.crc32(b"buckeroo"))
mkr = lambda rid, p: Risk(rid, rid, Param(p, Source.ASSUMPTION), DelayDist("fixed", 0, 1, 1))
act = Activity("X", "X", Param(10, Source.ASSUMPTION))
try:
    simulate(act, [mkr("plumless", 0.5), mkr("buckeroo", 0.5)], 1000, 5); refused = False
except ValueError as e:
    refused = "same CRC32" in str(e)
rec("RNG", "FIXED F5: colliding CRC32 ids are refused with a message instead of silently correlating", refused)
print("   (collision probability for a 46-risk register ~ 46*45/2/2^32 =", f"{46*45/2/2**32:.1e})")
# how many ids does the shipped risk library use, and do any collide?
lib = [x["id"] for x in service.risk_library()]; crcs = collections.Counter(zlib.crc32(i.encode()) for i in lib)
rec("RNG", f"no CRC32 collision among the {len(lib)} shipped library risk ids", all(v == 1 for v in crcs.values()))

# ---------------------------------------------------------------- ids with odd content
odd = [(0.3, FIX(1), "R é ü 💥"), (0.3, FIX(2), " lead space"), (0.3, FIX(3), "R,comma;semi\"quote")]
r, e = run(mk(odd)); rec("IDS", "unicode / spaces / CSV-hostile characters in risk ids work in analysis", r is not None and strict(r), e)
c = mk([(0.3, FIX(1), 5), (0.3, FIX(2), "6")]); r, e = run(c); rec("IDS", "numeric risk id (5) and text id ('6') both accepted", r is not None, e)
c = mk([(0.3, FIX(1), "X"), (0.3, FIX(2), "x")]); r, e = run(c); rec("IDS", "ids differing only by case ('X' vs 'x') treated as distinct", r is not None, e)
c = mk([(0.3, FIX(1), "X"), (0.3, FIX(2), "X")]); r, e = run(c); rec("IDS", "duplicate risk id rejected", e and e[0] == "CaseError", e)

# ---------------------------------------------------------------- hypothesis 2: option truncation at 40 / combos capped at 3
seven = [(0.5, PERT(1, 3, 8), f"Q{i}") for i in range(7)]
mits7 = [M(f"M{i}", f"Q{i}", 100, p_after={"value": 0.05, "source": A}) for i in range(7)]
r, e = run(mk(seven, mits=mits7, n=2000))
notes = r["option_build_notes"]
rec("OPTIONS", "7 independent cheap responses: options are truncated (7 + 21 + 35 = 63 -> 40)", notes["truncated"] and notes["n_generated"] == 40, notes)
surfaced = any("truncat" in w.lower() or "options were" in w.lower() for w in r["warnings"]) or "truncat" in r["report_markdown"].lower()
rec("OPTIONS", "truncation is surfaced to the user in warnings or the exported report", surfaced, f"warnings={r['warnings']}")
chosen = r["command"]["selected_option_id"]; sel = [o for o in r["decision"]["options"] if o["option_id"] == chosen][0]
print(f"   with 7 near-free responses, the tool's preferred option has {len(sel['mitigations'])} responses (max combination size 3, cap 40 options)")
ops7 = {o["option_id"]: o for o in r["decision"]["options"]}
all7_cost = None
c7 = mk(seven, mits=mits7, n=2000, options=[{"id": "ALL7", "label": "all seven", "mitigation_ids": [f"M{i}" for i in range(7)]}])
r7, e7 = run(c7)
if r7:
    all7 = [o for o in r7["decision"]["options"] if o["option_id"] == "ALL7"][0]
    rec("OPTIONS", "an explicit 7-response option beats the tool's auto-generated best (auto search is limited to <= 3 responses)", all7["total_expected_cost"] < sel["total_expected_cost"] - 1,
        f"ALL7 total {all7['total_expected_cost']:.0f} vs auto-best {sel['total_expected_cost']:.0f}")
five = [(0.5, PERT(1, 3, 8), f"Q{i}") for i in range(6)]; mits6 = [M(f"M{i}", f"Q{i}", 100, p_after={"value": 0.05, "source": A}) for i in range(6)]
r, e = run(mk(five, mits=mits6, n=2000)); print("   6 responses -> options generated:", r["option_build_notes"]["n_generated"], "truncated:", r["option_build_notes"]["truncated"], "(6+15+20 = 41 > 40)")

# ---------------------------------------------------------------- shapes that crashed the fuzz (targeted)
shape_cases = {
    "mitigations = true": lambda c: c.__setitem__("mitigations", True),
    "mitigations = 5": lambda c: c.__setitem__("mitigations", 5),
    "mitigations = 'x'": lambda c: c.__setitem__("mitigations", "x"),
    "options = true": lambda c: c.__setitem__("options", True),
    "options = 5": lambda c: c.__setitem__("options", 5),
    "constraints = 5": lambda c: c.__setitem__("constraints", 5),
    "constraints = [1]": lambda c: c.__setitem__("constraints", [1]),
    "simulation = 5": lambda c: c.__setitem__("simulation", 5),
    "simulation = [1]": lambda c: c.__setitem__("simulation", [1]),
    "simulation.correlation = 5": lambda c: c["simulation"].__setitem__("correlation", 5),
    "cost = 5": lambda c: c.__setitem__("cost", 5),
    "mitigation.secondary_risks = 5": lambda c: c["mitigations"][0].__setitem__("secondary_risks", 5),
    "mitigation.secondary_risks = true": lambda c: c["mitigations"][0].__setitem__("secondary_risks", True),
    "mitigation.evidence_ids = 5": lambda c: c["mitigations"][0].__setitem__("evidence_ids", 5),
    "mitigation.evidence_ids = [1, 'a']": lambda c: c["mitigations"][0].__setitem__("evidence_ids", [1, "a"]),
    "mitigation.evidence_ids = [[1]]": lambda c: c["mitigations"][0].__setitem__("evidence_ids", [[1]]),
    "mitigation.evidence_ids = 'M01' (bare string)": lambda c: c["mitigations"][0].__setitem__("evidence_ids", "M01"),
    "mitigation.time_to_implement_days = 'x'": lambda c: c["mitigations"][0].__setitem__("time_to_implement_days", "x"),
    "risk.direct_cost_if_occurs = 5": lambda c: c["risks"][0].__setitem__("direct_cost_if_occurs", 5),
}
unhandled = []
for label, f in shape_cases.items():
    c = mk(base, mits=[M("M1", "X1", 100, p_after={"value": 0.1, "source": A})], n=300)
    f(c); r, e = run(c)
    clean = (r is not None) or (e and e[0] == "CaseError")
    rec("SHAPES", f"run_analysis: {label} -> clean result or CaseError", clean, e)
    if not clean: unhandled.append((label, e))
print(f"   unhandled shapes: {len(unhandled)} of {len(shape_cases)}")

# ---------------------------------------------------------------- performance at scale
big_r = [(round(0.05 + 0.4 * ((i * 37) % 10) / 10, 3), PERT(1, 2 + (i % 4), 6 + (i % 5)), f"B{i}") for i in range(40)]
big_m = [M(f"BM{i}", f"B{i}", 500 + 100 * i, p_after={"value": 0.02, "source": A}) for i in range(12)]
t = time.time(); r, e = run(mk(big_r, T0=120, deadline=140, ld=3000, mits=big_m, n=10_000)); el = time.time() - t
rec("PERF", f"40 risks + 12 responses at n=10,000 finishes in a usable time", r is not None and el < 60, f"{el:.1f}s; options evaluated {len(r['decision']['options']) if r else '-'}")
rec("PERF", "40-risk analysis result is strict JSON and its size is reasonable", r is not None and strict(r), f"{len(json.dumps(r))/1e6:.2f} MB" if r else e)
t = time.time(); r, e = run(mk(big_r[:7], T0=16, mits=big_m[:5], n=200_000)); el2 = time.time() - t
print(f"   7 risks + 5 responses at n=200,000: {el2:.1f}s")
rec("PERF", "n=200,000 with 5 responses finishes within 60 s", r is not None and el2 < 60, f"{el2:.1f}s")

# ---------------------------------------------------------------- decision_sensitivity vs exact hand answer
exa = json.loads(json.dumps(service.example_analysis_case())); H = 0.005
Rk = {x["id"]: dict(p=x["p"]["value"], d=dict(kind=x["delay"]["kind"], a=x["delay"]["a"], m=x["delay"]["m"], b=x["delay"]["b"])) for x in exa["risks"]}
def cdf(d, x):
    a, m, b = d["a"], d["m"], d["b"]; al = 1 + 4 * (m - a) / (b - a); be = 1 + 4 * (b - m) / (b - a)
    return special.betainc(al, be, np.clip((x - a) / (b - a), 0, 1))
def pmf(p, d):
    L = int(math.ceil(d["b"] / H)) + 3; edges = (np.arange(L) - .5) * H; edges[0] = -1.0
    hi = cdf(d, edges + H); hi[-1] = 1; lo = np.concatenate([[0], hi[:-1]]); mass = np.clip(hi - lo, 0, None); mass /= mass.sum(); q = p * mass; q[0] += 1 - p; return q
def tot(rl):
    t_ = np.array([1.0])
    for p, d in rl: t_ = np.clip(signal.fftconvolve(t_, pmf(p, d)), 0, None); t_ /= t_.sum()
    return t_
def tec(ids, cd_):
    rl = {k: dict(v) for k, v in Rk.items()}; extra = []; mc = 0
    for mid in ids:
        m = [x for x in exa["mitigations"] if x["id"] == mid][0]; mc += m["cost"]["value"]; t_ = m["risk_id"]
        if m.get("p_after"): rl[t_]["p"] = m["p_after"]["value"]
        if m.get("delay_after"): da = m["delay_after"]; rl[t_]["d"] = dict(kind="pert", a=da["a"], m=da["m"], b=da["b"])
        for s in m.get("secondary_risks") or []: sd = s["delay"]; extra.append((s["p"]["value"], dict(kind="pert", a=sd["a"], m=sd["m"], b=sd["b"])))
    pm = tot([(v["p"], v["d"]) for v in rl.values()] + extra); k = np.arange(len(pm)) * H
    return mc + cd_ * float((pm * k).sum()) + 5000 * float((pm * np.maximum(k - 4, 0)).sum())
feasible = [m["id"] for m in exa["mitigations"] if m.get("feasible", True)]
opts = [()] + [(m,) for m in feasible]
for sz in (2, 3):
    for combo in itertools.combinations(feasible, sz):
        if len({[x for x in exa["mitigations"] if x["id"] == m][0]["risk_id"] for m in combo}) == sz: opts.append(combo)
exa["simulation"]["n"] = 10_000
rr, _ = run(exa)
rows = rr["decision_sensitivity"]["rows"]; mism = []
for row in rows:
    cd_ = row["cost_per_delay_day"]; best = min(opts, key=lambda ids: tec(ids, cd_)); bid = "ACCEPT" if not best else "O-" + "+".join(best)
    ts = sorted(tec(ids, cd_) for ids in opts); gap = ts[1] - ts[0]
    ok = (row["selected_option_id"] == bid)
    print(f"   Cd x{row['multiplier']:<5} tool picks {row['selected_option_id']:<22} hand-exact picks {bid:<22} gap to runner-up {gap:8.1f} INR  {'ok' if ok else 'DIFFERENT'}")
    if not ok: mism.append((row["multiplier"], row["selected_option_id"], bid, gap))
rec("DECISION", "decision_sensitivity (Cd x0.25 .. x4): tool's preferred option equals the exact hand-computed optimum at every multiplier", not mism, mism)
print("   flips reported by tool between multipliers:", rr["decision_sensitivity"]["flip_between_multipliers"], "| stability flag:", rr["decision_stability"]["stable"], rr["decision_stability"]["selected_option_ids"])

# ---------------------------------------------------------------- report vs code drift
txt = (REPO / "report/tables/hand_check_output.txt").read_text()
m = re.search(r"TOOL: expected_delay ([\d.]+) SE ([\d.]+) p_any_delay ([\d.]+) P90 duration ([\d.]+) P\(T>20\) ([\d.]+) E\[cost\] ([\d.]+)", txt)
exb = json.loads(json.dumps(service.example_analysis_case())); rb, _ = run(exb)
if m and rb:
    quoted = dict(expected_delay=float(m[1]), se=float(m[2]), p_any=float(m[3]), P90=float(m[4]), p_exceed=float(m[5]), E_cost=float(m[6]))
    s = rb["summary"]; cur = dict(expected_delay=s["expected_delay"], se=s["mean_se"], p_any=s["p_any_delay"], P90=s["percentiles"]["P90"], p_exceed=s["p_exceed_deadline"], E_cost=rb["cost"]["expected_cost"])
    same = all(abs(quoted[k] - cur[k]) < (0.5 if k == "E_cost" else 0.0006) for k in quoted)
    print("   report table says:", quoted); print("   code at HEAD gives:", {k: round(v, 4) for k, v in cur.items()})
    rec("DRIFT", "numbers quoted in report/tables/hand_check_output.txt (TOOL line, n=10000 seed 12345) are reproduced by the current code", same, f"quoted {quoted} vs now {cur}")

json.dump(E, open(SP / "v4_results.json", "w"), indent=1, default=str)
nf = sum(not x["pass"] for x in E)
print(f"\nEDGE/SHAPE/PERF CHECKS: {len(E)}   passed {len(E) - nf}   failed {nf}")
for x in E:
    if not x["pass"]: print("  FAIL", x["area"], "|", x["test"], "|", x["detail"][:200])
