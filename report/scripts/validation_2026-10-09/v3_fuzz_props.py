"""Randomised robustness (fuzz) and invariant testing of run_case / run_analysis.  Never edits the repo."""
import copy, json, math, random, signal, sys, time, traceback, collections
from pathlib import Path
import numpy as np

REPO = Path("/home/claude/drassassin3214/fyp")
OUT = Path(sys.argv[1]); sys.path.insert(0, str(REPO))
from app import service, analysis

ex_reg = json.load(open(REPO / "examples/example_case.json", encoding="utf-8-sig"))
ex_ana = json.loads(json.dumps(service.example_analysis_case()))      # current generator (what the GUI loads)


class Timeout(Exception): pass


def _alarm(sig, frm): raise Timeout()


signal.signal(signal.SIGALRM, _alarm)

JUNK = [None, "", " ", "abc", "0.5", "1e999", "NaN", "\u0000", "💥", -1, 0, 1, 2, 10 ** 30, 1e308, -1e308, 1e-320, float("nan"), float("inf"),
        float("-inf"), True, False, [], {}, [1, 2], {"value": None}, {"value": "x", "source": "Assumption"}, {"value": 0.5}, {"source": "Assumption"}, [[]],
        {"a": 1}, "Assumption", "Expert Judgment", 0.5, 1.5, -0.5, 3.0]


def paths(obj, prefix=()):
    yield prefix
    if isinstance(obj, dict):
        for k, v in obj.items(): yield from paths(v, prefix + (k,))
    elif isinstance(obj, list):
        for i, v in enumerate(obj): yield from paths(v, prefix + (i,))


def get(obj, path):
    for k in path: obj = obj[k]
    return obj


def mutate(case, rng):
    c = copy.deepcopy(case)
    for _ in range(rng.choice([1, 1, 1, 2, 3])):
        ps = [p for p in paths(c) if p]
        p = rng.choice(ps)
        parent = get(c, p[:-1]); k = p[-1]
        op = rng.choice(["junk", "junk", "junk", "delete", "dup", "swap", "type"])
        try:
            if op == "junk": parent[k] = rng.choice(JUNK)
            elif op == "delete":
                if isinstance(parent, dict): del parent[k]
                else: parent.pop(k)
            elif op == "dup" and isinstance(parent, list): parent.append(copy.deepcopy(parent[k]))
            elif op == "swap" and isinstance(parent, list) and len(parent) > 1: j = rng.randrange(len(parent)); parent[k], parent[j] = parent[j], parent[k]
            elif op == "type":
                v = parent[k]
                parent[k] = [v] if rng.random() < .5 else {"value": v}
        except Exception:
            pass
    return c


def strict_json_ok(res):
    try:
        json.dumps(res, allow_nan=False); return True
    except Exception as e:
        return str(e)


def run_fuzz(name, fn, base, n_mut, seed, per_call_s):
    rng = random.Random(seed)
    cnt = collections.Counter(); bugs = []
    for i in range(n_mut):
        c = mutate(base, rng)
        before = json.dumps(c, default=str, sort_keys=True)
        signal.alarm(per_call_s)
        try:
            res = fn(c)
            signal.alarm(0)
            cnt["ok"] += 1
            sj = strict_json_ok(res)
            if sj is not True:
                bugs.append({"kind": "non-strict-JSON output (NaN/Inf)", "detail": sj, "case": c}); cnt["nonjson"] += 1
        except service.CaseError:
            signal.alarm(0); cnt["CaseError"] += 1
        except Timeout:
            cnt["timeout"] += 1; bugs.append({"kind": "timeout >%ds" % per_call_s, "case": c})
        except Exception as e:
            signal.alarm(0)
            cnt["UNHANDLED " + type(e).__name__] += 1
            bugs.append({"kind": "unhandled " + type(e).__name__, "detail": str(e)[:300], "tb": traceback.format_exc()[-700:], "case": c})
        finally:
            signal.alarm(0)
        after = json.dumps(c, default=str, sort_keys=True)
        if before != after:
            bugs.append({"kind": "input mutated by the call", "case": c}); cnt["input_mutated"] += 1
    print(f"[{name}] {n_mut} mutations: {dict(cnt)}", flush=True)
    return cnt, bugs


def small(case):
    c = copy.deepcopy(case)
    sim = c.get("simulation")
    if isinstance(sim, dict): sim["n"] = 300
    return c


all_bugs = {}
t0 = time.time()
cnt1, b1 = run_fuzz("run_case(example register)", lambda c: service.run_case(c), ex_reg, 4000, 1, 20)
cnt2, b2 = run_fuzz("run_case(example analysis case)", lambda c: service.run_case(c), ex_ana, 3000, 2, 20)
cnt3, b3 = run_fuzz("run_analysis(n=300)", lambda c: analysis.run_analysis(small(c)), ex_ana, 700, 3, 60)
print(f"fuzz time {time.time() - t0:.0f}s", flush=True)

# de-duplicate bugs by (kind, detail-ish)
def dedupe(bugs):
    seen = {}
    for b in bugs:
        key = (b["kind"], (b.get("detail") or "")[:80], (b.get("tb") or "").splitlines()[-3:-1].__str__() if b.get("tb") else "")
        seen.setdefault(key, b)
    return list(seen.values())


unique = {"run_case_register": dedupe(b1), "run_case_analysis": dedupe(b2), "run_analysis": dedupe(b3)}
for k, v in unique.items():
    print(f"\n== unique unhandled/odd outcomes in {k}: {len(v)}")
    for b in v[:8]:
        print("  -", b["kind"], "|", b.get("detail", "")[:160])
        if b.get("tb"): print("    tb:", b["tb"].replace("\n", " | ")[-260:])

# ================================================================== invariants on random VALID cases
print("\n== Invariants on random valid cases", flush=True)
A = "Assumption"


def rand_case(rng, i):
    k = rng.randint(1, 10)
    T0 = rng.choice([1, 5, 12, 16, 30, 90, 200])
    risks = []
    for j in range(k):
        kind = rng.choice(["pert", "pert", "triangular", "uniform", "fixed"])
        a = round(rng.uniform(0, 5), 2); m = round(a + rng.uniform(0, 6), 2); b = round(m + rng.uniform(0, 12), 2)
        p = rng.choice([0.0, 1.0, round(rng.random(), 3), round(rng.random(), 3), round(rng.random(), 3)])
        d = {"kind": kind, "source": A}
        if kind == "fixed": d["m"] = m
        elif kind == "uniform": d.update(a=a, b=b)
        else: d.update(a=a, m=m, b=b)
        risks.append({"id": f"R{j}", "name": f"risk {j}", "p": {"value": p, "source": A}, "delay": d,
                      **({"direct_cost_if_occurs": {"value": rng.choice([0, 500, 12000]), "source": A}} if rng.random() < .4 else {})})
    case = {"project": {"name": "rnd"}, "activity": {"id": "A", "name": "a", "planned_duration_days": {"value": T0, "source": A}},
            "facts": {}, "risks": risks, "use_literature_seed": False,
            "impact_bin_edges_fraction": [0.02, 0.05, 0.10, 0.20], "impact_bin_edges_source": {"source": A, "note": ""},
            "cost": {"cost_per_delay_day": {"value": rng.choice([0, 1000, 8000, 50000]), "source": A}, "currency": "INR"},
            "simulation": {"n": rng.choice([2000, 4000]), "seed": rng.randint(0, 10 ** 6), "criterion": rng.choice(["min_expected_total_cost", "min_p90_duration"])}}
    has_dl = rng.random() < .6
    if has_dl:
        case["activity"]["deadline_days"] = {"value": round(T0 + rng.uniform(-0.2 * T0, 6), 2) if T0 > 1 else 3.0, "source": A}
        if case["activity"]["deadline_days"]["value"] <= 0: case["activity"]["deadline_days"]["value"] = 1.0
        if rng.random() < .6: case["cost"]["ld_per_day_after_deadline"] = {"value": rng.choice([0, 2000, 20000]), "source": A}
        if rng.random() < .3: case["simulation"]["criterion"] = "min_deadline_exceedance"
    mits = []
    for j in range(rng.randint(0, 5)):
        t = rng.choice(risks)
        m = {"id": f"M{j}", "risk_id": t["id"], "action": f"act {j}", "cost": {"value": rng.choice([0, 300, 5000, 40000]), "source": A}}
        if rng.random() < .7: m["p_after"] = {"value": round(rng.random() * float(t["p"]["value"]), 3), "source": A}
        if rng.random() < .3 or "p_after" not in m:
            m["delay_after"] = {"kind": "pert", "a": 0, "m": 1, "b": 3, "source": A}
        if rng.random() < .15: m["feasible"] = False; m["infeasible_reason"] = "n/a"
        mits.append(m)
    case["mitigations"] = mits
    if k >= 2 and rng.random() < .3:
        case["simulation"]["correlation"] = [{"a": "R0", "b": "R1", "rho": round(rng.uniform(-0.8, 0.9), 2)}]
    if rng.random() < .3: case["constraints"] = {"max_mitigation_budget": rng.choice([0, 1000, 10000])}
    return case


from app.engine.models import Source
fails = collections.defaultdict(list); n_ok = 0; n_case_err = 0; n_unhandled = 0
rng = random.Random(2026)
NCASES = 140
t0 = time.time()
for i in range(NCASES):
    case = rand_case(rng, i); frozen = json.dumps(case, sort_keys=True)
    signal.alarm(120)
    try:
        res = analysis.run_analysis(case); signal.alarm(0)
    except service.CaseError as e:
        n_case_err += 1; fails["valid-looking case rejected"].append((i, str(e)[:200])); continue
    except Exception as e:
        n_unhandled += 1; fails["unhandled " + type(e).__name__].append((i, str(e)[:200], traceback.format_exc()[-500:])); continue
    finally:
        signal.alarm(0)
    n_ok += 1
    if json.dumps(case, sort_keys=True) != frozen: fails["input mutated"].append(i)
    s = res["summary"]; n = res["n_used"]
    pct = [s["min"]] + [s["percentiles"][k] for k in ("P10", "P50", "P80", "P85", "P90", "P95")] + [s["max"]]
    if any(b < a - 1e-9 for a, b in zip(pct, pct[1:])): fails["percentiles not monotone"].append(i)
    if not (s["min"] - 1e-9 <= s["mean"] <= s["max"] + 1e-9): fails["mean outside [min,max]"].append(i)
    if not (0 <= s["p_any_delay"] <= 1): fails["p_any outside [0,1]"].append(i)
    if s.get("p_exceed_deadline") is not None and not (0 <= s["p_exceed_deadline"] <= 1): fails["p_exceed outside [0,1]"].append(i)
    c = res["cost"]
    if c["expected_cost"] < -1e-9 or any(c[k] < -1e-9 for k in ("P50", "P80", "P90", "P95")): fails["negative cost"].append(i)
    if not (c["P50"] <= c["P80"] + 1e-9 <= c["P90"] + 2e-9 <= c["P95"] + 3e-9): fails["cost percentiles not monotone"].append(i)
    if sum(res["histogram"]["counts"]) != n: fails["histogram counts != n"].append(i)
    if strict_json_ok(res) is not True: fails["non-strict JSON output"].append((i, strict_json_ok(res)))
    # analytic mean of delay
    pa = analysis.parse_analysis(case)
    from app.engine.simulation import analytic_moments
    am = analytic_moments(pa["risks"])
    se = (am["std"] / math.sqrt(n)) if am["std"] > 0 else 1e-9
    if abs(s["expected_delay"] - am["expected_delay"]) > 4.5 * se + 1e-9: fails["simulated mean delay != analytic (4.5 SE)"].append((i, s["expected_delay"], am["expected_delay"], se))
    # EMV sum vs expected cost when linear (no LD)
    ld = case["cost"].get("ld_per_day_after_deadline", {}).get("value", 0)
    if not ld:
        emv_sum = sum(r["emv"] for r in res["event_emv"])
        cse = c["std"] / math.sqrt(n) if c["std"] > 0 else 1e-9
        if abs(c["expected_cost"] - emv_sum) > 4.5 * cse + 1e-6: fails["sum event EMV != expected cost (4.5 SE, no LD)"].append((i, c["expected_cost"], emv_sum, cse))
    # decision: ACCEPT row == base run
    dec = res["decision"]; rows = {o["option_id"]: o for o in dec["options"]}
    acc = rows["ACCEPT"]
    if abs(acc["expected_delay"] - s["expected_delay"]) > 1e-9: fails["ACCEPT row != base summary"].append(i)
    if abs(acc["residual_expected_cost"] - c["expected_cost"]) > 1e-6 * max(1, abs(c["expected_cost"])): fails["ACCEPT row cost != base cost"].append(i)
    # selected option is argmin among admissible
    key = {"min_expected_total_cost": "total_expected_cost", "min_deadline_exceedance": "p_exceed_deadline", "min_p90_duration": "P90"}[res["criterion"]]
    adm = [o for o in dec["options"] if o["admissible"]]
    if adm:
        best = min(o[key] for o in adm)
        sel = rows[dec["selected_option_id"]]
        if sel[key] > best + 1e-9: fails["selected option is not the argmin of the criterion"].append(i)
        if not sel["admissible"]: fails["selected option not admissible"].append(i)
    else:
        if dec["selected_option_id"] is not None: fails["selected an option when none admissible"].append(i)
    cmd = res["command"]["command"]
    sid = dec["selected_option_id"]
    exp = "NO ADMISSIBLE OPTION" if sid is None else ("ACCEPT RISK" if sid == "ACCEPT" else "AUTHORIZE MITIGATION")
    if len(dec["options"]) <= 1: exp = "NO RESPONSE EVALUATED" if sid is not None else "NO ADMISSIBLE OPTION"
    if cmd != exp: fails["command text inconsistent with selected option"].append((i, cmd, exp))
    # infeasible never selected
    if sid and not rows[sid]["feasible"]: fails["infeasible option selected"].append(i)
    # mitigation_checks identity
    for ch in res["mitigation_checks"]:
        if abs(ch["net_benefit"] - (ch["emv_before"] - ch["emv_after"] - ch["secondary_risk_emv"] - ch["mitigation_cost"])) > 1e-6: fails["net benefit identity"].append((i, ch["mitigation_id"]))
    # budget constraint respected
    bud = (case.get("constraints") or {}).get("max_mitigation_budget")
    if bud is not None and sid and rows[sid]["mitigation_cost"] > bud + 1e-9: fails["budget constraint violated by selected option"].append(i)
    # determinism: same input twice -> identical decision numbers
    if i % 10 == 0:
        res2 = analysis.run_analysis(case)
        if res2["summary"] != res["summary"] or res2["command"] != res["command"]: fails["not deterministic for same seed"].append(i)
        case2 = copy.deepcopy(case); case2["simulation"]["seed"] = case["simulation"]["seed"] + 1
        res3 = analysis.run_analysis(case2)
        if res3["summary"]["mean"] == res["summary"]["mean"] and res["summary"]["std"] > 0: fails["different seed gives identical results"].append(i)
    # value at stake non-negative
    if any(v["value_at_stake"] < -1e-9 for v in res["value_at_stake"]): fails["negative value at stake"].append(i)
    # register-side invariants
    rc = service.run_case(case)
    for m in rc["matrix"]:
        if not (1 <= m["p_class"] <= 5 and 1 <= m["impact_class"] <= 5 and m["score"] == m["p_class"] * m["impact_class"]): fails["matrix class out of range / score != product"].append(i)
        sc = m["score"]; lv = "Low" if sc <= 5 else "Moderate" if sc <= 10 else "High" if sc <= 15 else "Extreme"
        if m["level"] != lv: fails["matrix level != hand level"].append((i, m["risk_id"], sc, m["level"]))
    if rc["summary"]["n_on_matrix"] != len(rc["matrix"]): fails["summary.n_on_matrix != len(matrix)"].append(i)
print(f"random valid cases: {NCASES}; ran ok {n_ok}; rejected by CaseError {n_case_err}; unhandled {n_unhandled}; time {time.time() - t0:.0f}s")
if not fails: print("  all invariants held on every case")
for k, v in fails.items(): print(f"  FAIL [{k}] x{len(v)}: first -> {v[0]}")

json.dump({"fuzz": {"run_case_register": dict(cnt1), "run_case_analysis": dict(cnt2), "run_analysis": dict(cnt3)},
           "unique_bugs": {k: [{kk: vv for kk, vv in b.items() if kk != "case"} for b in v] for k, v in unique.items()},
           "bug_cases": {k: [b["case"] for b in v[:3]] for k, v in unique.items()},
           "invariants": {"cases": NCASES, "ok": n_ok, "caseerr": n_case_err, "unhandled": n_unhandled, "fails": {k: [str(x) for x in v[:3]] + [f"count={len(v)}"] for k, v in fails.items()}}},
          open(OUT / "v3_results.json", "w"), indent=1, default=str)
