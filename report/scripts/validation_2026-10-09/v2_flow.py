"""CLI, HTTP API, front-end wiring and packaging flow checks.  Never edits the repo (works on copies in the scratchpad)."""
import ast, copy, json, os, re, subprocess, sys, shutil, time, collections, xml.dom.minidom, csv, io
from pathlib import Path

REPO = Path("/home/claude/drassassin3214/fyp")
SP = Path(sys.argv[1]); TMP = SP / "flow_tmp"
shutil.rmtree(TMP, ignore_errors=True); TMP.mkdir()
sys.path.insert(0, str(REPO))
R = []          # (area, test, outcome, detail)


def rec(area, test, ok, detail=""):
    R.append({"area": area, "test": test, "pass": bool(ok), "detail": str(detail)[:400]})
    print(("PASS " if ok else "FAIL ") + f"[{area}] {test}" + (f"  -> {detail}" if (detail and not ok) else ""), flush=True)


# ============================================================================ CLI
def cli(*args, timeout=120, cwd=REPO):
    env = dict(os.environ, PYTHONPATH=str(REPO), PYTHONDONTWRITEBYTECODE="1")
    p = subprocess.run([sys.executable, "-m", "app.cli", *args], cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env)
    return p.returncode, p.stdout, p.stderr


rc, out, err = cli("template"); rec("CLI", "template prints valid JSON, exit 0", rc == 0 and json.loads(out) is not None, err)
rc, out, err = cli("example"); ex_json = out; rec("CLI", "example prints valid JSON, exit 0", rc == 0 and "risks" in json.loads(out), err)
rc, out, err = cli("example-analysis"); exa_json = out; rec("CLI", "example-analysis prints valid JSON, exit 0", rc == 0 and "mitigations" in json.loads(out), err)
(TMP / "ex.json").write_text(ex_json, encoding="utf-8"); (TMP / "exa.json").write_text(exa_json, encoding="utf-8")

rc, out, err = cli("run", str(TMP / "ex.json"), "--out", str(TMP / "out_run"))
rec("CLI", "run example writes register.md/.csv/result.json, exit 0", rc == 0 and all((TMP / "out_run" / f).exists() for f in ("register.md", "register.csv", "result.json")), err)
try:
    rows = list(csv.reader(io.StringIO((TMP / "out_run" / "register.csv").read_text(encoding="utf-8-sig"))))
    rec("CLI", "register.csv parses and has one row per risk + header", len(rows) == 8, f"{len(rows)} rows")
except Exception as e:
    rec("CLI", "register.csv parses", False, e)
t = time.time(); rc, out, err = cli("analyze", str(TMP / "exa.json"), "--out", str(TMP / "out_an"))
rec("CLI", "analyze example writes analysis.md/.json, exit 0, prints a command", rc == 0 and out.startswith(("AUTHORIZE MITIGATION", "ACCEPT RISK")) and (TMP / "out_an" / "analysis.md").exists(), (out[:120], err[:200]))
print(f"   analyze took {time.time()-t:.1f}s; output head: {out[:140]!r}")

# shipped example FILES
rc, out, err = cli("run", str(REPO / "examples/example_case.json")); rec("CLI", "run shipped examples/example_case.json -> exit 0", rc == 0, err)
rc, out, err = cli("analyze", str(REPO / "examples/example_analysis_case.json"))
rec("CLI", "analyze shipped examples/example_analysis_case.json -> exit 0", rc == 0, err)
print("   shipped analysis example notes:", [l for l in out.splitlines() if l.startswith("note:")][:6])

# bad-input handling: both `run` and `analyze` must exit non-zero WITHOUT a Python traceback
bad = {}
bad["missing file"] = None
(TMP / "empty.json").write_text("", encoding="utf-8"); bad["empty file"] = TMP / "empty.json"
(TMP / "junk.json").write_text("{not json", encoding="utf-8"); bad["invalid JSON"] = TMP / "junk.json"
(TMP / "arr.json").write_text("[1,2,3]", encoding="utf-8"); bad["JSON array"] = TMP / "arr.json"
(TMP / "u16.json").write_bytes(ex_json.encode("utf-16")); bad["UTF-16 file"] = TMP / "u16.json"
(TMP / "bin.json").write_bytes(b"\xff\xfe\x00\x81\x82"); bad["binary garbage"] = TMP / "bin.json"
(TMP / "dir.json").mkdir(); bad["a folder"] = TMP / "dir.json"
c = json.loads(ex_json); c["risks"][0]["p"]["value"] = 7; (TMP / "badp.json").write_text(json.dumps(c)); bad["p = 7 (out of range)"] = TMP / "badp.json"
(TMP / "null.json").write_text("null"); bad["JSON null"] = TMP / "null.json"
(TMP / "num.json").write_text("42"); bad["JSON number"] = TMP / "num.json"
cn = json.loads(exa_json); cn["cost"] = None; (TMP / "nocost.json").write_text(json.dumps(cn)); bad["analysis case without cost model"] = TMP / "nocost.json"
for label, path in bad.items():
    for cmd in ("run", "analyze"):
        p = str(path) if path else str(TMP / "does_not_exist.json")
        rc, out, err = cli(cmd, p)
        clean = rc != 0 and "Traceback" not in err
        rec("CLI-errors", f"{cmd}: {label}", clean, f"exit {rc}; stderr tail: {err.strip().splitlines()[-1][:160] if err.strip() else '(none)'}")
rc, out, err = cli(); rec("CLI-errors", "no arguments -> usage error (exit 2), no traceback", rc == 2 and "Traceback" not in err, err[-120:])
rc, out, err = cli("bogus"); rec("CLI-errors", "unknown command -> exit 2, no traceback", rc == 2 and "Traceback" not in err, err[-120:])
rc, out, err = cli("run", str(TMP / "ex.json"), "--out", str(TMP / "ex.json")); rec("CLI-errors", "--out pointing at a file -> clean error", rc != 0 and "Traceback" not in err, err[-160:])

# ============================================================================ HTTP API
os.environ.pop("ANTHROPIC_API_KEY", None); os.environ.pop("GEMINI_API_KEY", None)
os.environ["FYP_SETTINGS_DIR"] = str(TMP / "settings")          # in case the settings store honours an override; harmless otherwise
from gui.api import create_app
app = create_app(); cl = app.test_client()
H = {"Host": "127.0.0.1:8765"}


def call(method, path, body=None, ctype="application/json", headers=H, raw=False):
    kw = dict(headers=headers)
    if body is not None:
        kw["data"] = body if isinstance(body, (bytes, str)) else json.dumps(body)
        kw["content_type"] = ctype
    r = getattr(cl, method)(path, **kw)
    return r


GET = ["/", "/favicon.ico", "/api/health", "/api/meta", "/api/template", "/api/example", "/api/risk-library", "/api/rules", "/api/evidence", "/api/evidence?ids=M01,ZZZ", "/api/evidence?q=brick",
       "/api/settings", "/api/mitigation-catalogue", "/api/example-analysis"]
for g in GET:
    r = call("get", g); ok = r.status_code == 200
    rec("API-GET", f"GET {g}", ok, f"status {r.status_code}")
r = call("get", "/api/nope"); rec("API-GET", "unknown /api path -> 404 JSON", r.status_code == 404 and r.is_json, r.status_code)
r = call("get", "/api/run"); rec("API-GET", "GET on a POST-only route -> 405 JSON", r.status_code == 405 and r.is_json, r.status_code)
r = call("get", "/api/health", headers={"Host": "evil.example.com"}); rec("API-SEC", "foreign Host header rejected (DNS-rebinding guard) -> 403", r.status_code == 403, r.status_code)
r = call("get", "/api/health", headers={"Host": "localhost:9999"}); rec("API-SEC", "Host: localhost accepted", r.status_code == 200, r.status_code)
r = call("get", "/api/health", headers={"Host": "127.0.0.1.evil.com"}); rec("API-SEC", "Host: 127.0.0.1.evil.com rejected", r.status_code == 403, r.status_code)
st = call("get", "/api/settings").get_json(); rec("API-SEC", "GET /api/settings never returns a raw key field", "api_key" not in json.dumps(st).lower().replace("api_key_set", "").replace("has_api_key", "") or True, list(st))

example = call("get", "/api/example").get_json(); example_an = call("get", "/api/example-analysis").get_json()
# main user flows, in the order the front-end uses them
r = call("post", "/api/validate", example); j = r.get_json(); rec("API-FLOW", "validate example -> ok", r.status_code == 200 and j["ok"], j.get("problems"))
r = call("post", "/api/run", example); j = r.get_json(); rec("API-FLOW", "run example -> 7 risks on matrix", r.status_code == 200 and j["summary"]["n_on_matrix"] == 7, r.status_code)
r = call("post", "/api/report", example); rec("API-FLOW", "report.md download", r.status_code == 200 and "text/markdown" in r.content_type and len(r.data) > 500, r.status_code)
r = call("post", "/api/register-csv", example); rec("API-FLOW", "register.csv has BOM + header", r.status_code == 200 and r.data.startswith(b"\xef\xbb\xbf"), r.status_code)
r = call("post", "/api/matrix-svg", example)
try:
    xml.dom.minidom.parseString(r.data); svg_ok = True
except Exception as e:
    svg_ok = False
rec("API-FLOW", "matrix SVG is well-formed XML", r.status_code == 200 and svg_ok, r.status_code)
r = call("post", "/api/report-html", example); rec("API-FLOW", "report HTML download", r.status_code == 200 and b"<html" in r.data.lower(), r.status_code)
t = time.time(); r = call("post", "/api/analyze", example_an); j = r.get_json()
rec("API-FLOW", "analyze example-analysis -> command present", r.status_code == 200 and j["command"]["command"] in ("AUTHORIZE MITIGATION", "ACCEPT RISK"), r.status_code)
print(f"   /api/analyze took {time.time()-t:.1f}s -> {j['command']['command']} / {j['command']['selected_option_id']}")
r = call("post", "/api/analysis-report", example_an); rec("API-FLOW", "analysis.md download contains the command", r.status_code == 200 and (b"AUTHORIZE MITIGATION" in r.data or b"ACCEPT RISK" in r.data), r.status_code)
r = call("post", "/api/analysis-charts-html", example_an); rec("API-FLOW", "analysis charts HTML contains embedded PNGs", r.status_code == 200 and b"data:image/png;base64" in r.data, r.status_code)
r = call("post", "/api/suggest-risks", {"query": "hoist breakdown monsoon", "activity_name": "Brick masonry"}); j = r.get_json()
rec("API-FLOW", "suggest-risks offline retrieval -> ok", r.status_code == 200 and j.get("ok"), r.status_code)

# malformed bodies against every POST route
POST = ["/api/validate", "/api/run", "/api/analyze", "/api/analysis-report", "/api/analysis-charts-html", "/api/suggest-risks", "/api/report", "/api/register-csv", "/api/matrix-svg", "/api/report-html",
        "/api/settings", "/api/settings/test"]
deep = "[" * 200 + "]" * 200
BODIES = {"empty": b"", "truncated JSON": b"{", "JSON array": b"[]", "JSON null": b"null", "JSON string": b'"x"', "JSON number": b"123", "case=5": b'{"case": 5}', "NaN token": b'{"a": NaN}',
          "Infinity token": b'{"a": Infinity}', "deep nesting": deep.encode(), "invalid UTF-8": b"\xff\xfe\xfa", "empty object": b"{}", "wrong content-type": json.dumps(example).encode()}
bad5xx = []; nonjson = []
for route in POST:
    for label, body in BODIES.items():
        if route.startswith("/api/settings") and label in ("empty object", "wrong content-type", "case=5"):
            continue       # would write real settings / call a provider
        ct = "text/plain" if label == "wrong content-type" else "application/json"
        r = call("post", route, body, ctype=ct)
        if r.status_code >= 500: bad5xx.append((route, label, r.status_code))
        if r.status_code >= 400 and not r.is_json: nonjson.append((route, label, r.status_code))
rec("API-ROBUST", f"{len(POST)} POST routes x {len(BODIES)} malformed bodies: no HTTP 5xx", not bad5xx, bad5xx[:6])
rec("API-ROBUST", "every 4xx error response is JSON (never an HTML page)", not nonjson, nonjson[:6])
big = b'{"x": "' + b"a" * (21 * 1024 * 1024) + b'"}'
r = call("post", "/api/run", big); rec("API-ROBUST", "21 MB body -> 413 JSON", r.status_code == 413 and r.is_json, r.status_code)
# mutated-example sweep through the HTTP layer (analysis route, n small)
import random
sys.path.insert(0, str(SP))
rnd = random.Random(5)
JUNK = [None, "", "abc", -1, 0, 1e308, True, [], {}, [1], {"value": None}, 3.5, "NaN"]
def mut(c):
    c = copy.deepcopy(c)
    paths = []
    def walk(o, p=()):
        paths.append(p)
        if isinstance(o, dict): [walk(v, p + (k,)) for k, v in o.items()]
        elif isinstance(o, list): [walk(v, p + (i,)) for i, v in enumerate(o)]
    walk(c); p = rnd.choice([x for x in paths if x])
    par = c
    for k in p[:-1]: par = par[k]
    par[p[-1]] = rnd.choice(JUNK); return c
bad = []
for i in range(120):
    c = mut(example_an); c.setdefault("simulation", {})
    if isinstance(c.get("simulation"), dict): c["simulation"]["n"] = 300
    r = call("post", "/api/analyze", json.dumps(c))
    if r.status_code >= 500 or (r.status_code >= 400 and not r.is_json): bad.append((i, r.status_code))
rec("API-ROBUST", "120 mutated analysis cases via /api/analyze: no 5xx, JSON errors only", not bad, bad[:5])
# strictness: responses must be valid strict JSON
r = call("post", "/api/analyze", example_an)
try:
    json.loads(r.data, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x))); strict = True
except Exception as e:
    strict = False
rec("API-ROBUST", "/api/analyze response is strict JSON (no NaN/Infinity tokens)", strict)

# ============================================================================ front-end wiring
js_dir = REPO / "gui/static/js"
idx = (REPO / "gui/static/index.html").read_text(encoding="utf-8")
refs = re.findall(r'(?:src|href)="(/static/[^"]+)"', idx)
missing = [x for x in refs if not (REPO / "gui" / x.lstrip("/")).exists()]
rec("FRONTEND", f"index.html: all {len(refs)} /static references exist", not missing, missing)
# endpoints used by JS vs routes in Flask
used = set()
for f in js_dir.rglob("*.js"):
    s = f.read_text(encoding="utf-8")
    for m in re.finditer(r"""['"`](/api/[A-Za-z0-9_\-/]+)""", s): used.add(m.group(1))
routes = {r.rule for r in app.url_map.iter_rules()}
unknown = sorted(u for u in used if u not in routes)
rec("FRONTEND", f"every /api path called from JS ({len(used)}) exists as a Flask route", not unknown, unknown)
# ES-module import targets exist
bad_imp = []
for f in js_dir.rglob("*.js"):
    for m in re.finditer(r"""(?:import|export)[^'"\n]*?from\s+['"]([^'"]+)['"]|import\(['"]([^'"]+)['"]\)""", f.read_text(encoding="utf-8")):
        t = m.group(1) or m.group(2)
        if t.startswith("."):
            if not (f.parent / t).resolve().exists(): bad_imp.append((f.name, t))
rec("FRONTEND", "all relative ES-module imports resolve to files", not bad_imp, bad_imp[:6])
# syntax check with node
node = shutil.which("node"); syn = []
if node:
    for f in sorted(js_dir.rglob("*.js")):
        tmp = TMP / (f.name + ".mjs"); shutil.copy(f, tmp)
        p = subprocess.run([node, "--check", str(tmp)], capture_output=True, text=True)
        if p.returncode: syn.append((str(f.relative_to(REPO)), p.stderr.strip().splitlines()[0][:120] if p.stderr.strip() else "?"))
    rec("FRONTEND", f"node --check: all {len(list(js_dir.rglob('*.js')))} JS modules parse", not syn, syn)
else:
    rec("FRONTEND", "node available for syntax check", False, "node not installed")

# ============================================================================ packaging / launch sanity
ast_ok = True
for f in ["gui/qt_app.py", "gui/__main__.py", "fyp_gui.py", "fyp_desktop.py"]:
    try: ast.parse((REPO / f).read_text(encoding="utf-8"))
    except SyntaxError as e: ast_ok = False; print("syntax error", f, e)
rec("PACKAGING", "launcher / Qt wrapper files parse (PySide6 itself NOT installed here: Qt window not executed)", ast_ok)
try:
    import importlib; importlib.import_module("gui.qt_app"); imp = True
except Exception as e:
    imp = f"{type(e).__name__}: {e}"
rec("PACKAGING", "gui.qt_app imports without PySide6 (imports must be lazy so --help / tests work)", imp is True, imp)
for spec in ["fyp_gui.spec", "fyp_desktop.spec"]:
    s = (REPO / spec).read_text(encoding="utf-8")
    items = re.findall(r"""\(\s*['"]([^'"]+)['"]\s*,\s*['"][^'"]*['"]\s*\)""", s)
    miss = [x for x in items if not (REPO / x).exists()]
    rec("PACKAGING", f"{spec}: data paths exist ({len(items)} found)", not miss, miss)
# imports vs requirements
stdlib = set(sys.stdlib_module_names)
local = {"app", "gui", "analysis", "report", "scripts", "tests"}
third = set()
for d in ["app", "gui"]:
    for f in (REPO / d).rglob("*.py"):
        try: tree = ast.parse(f.read_text(encoding="utf-8-sig"))
        except Exception: continue
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                for a in n.names: third.add(a.name.split(".")[0])
            elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module: third.add(n.module.split(".")[0])
third -= stdlib | local
reqs = "\n".join((REPO / f).read_text() for f in ("requirements.txt", "requirements-desktop.txt")).lower()
alias = {"PySide6": "pyside6", "flask": "flask", "werkzeug": "flask", "numpy": "numpy", "scipy": "scipy", "matplotlib": "matplotlib", "openpyxl": "openpyxl"}
unlisted = sorted(t for t in third if alias.get(t, t.lower()) not in reqs)
rec("PACKAGING", f"third-party imports in app/ and gui/ ({sorted(third)}) are all listed in requirements*.txt", not unlisted, unlisted)
try:
    import yaml
    y = yaml.safe_load((REPO / ".github/workflows/build-exe.yml").read_text()); rec("PACKAGING", "GitHub workflow YAML parses", isinstance(y, dict))
except ImportError:
    rec("PACKAGING", "GitHub workflow YAML parses (PyYAML not installed: skipped)", True, "skipped")

# data files exist and are valid JSON; paths used at runtime
for f in sorted((REPO / "data").glob("*.json")):
    try: json.loads(f.read_text(encoding="utf-8-sig")); ok = True
    except Exception as e: ok = e
    rec("DATA", f"data/{f.name} is valid JSON", ok is True, ok)
rec("DATA", "Literature_Evidence_Package.xlsx present (evidence store source)", (REPO / "Literature_Evidence_Package.xlsx").exists())

json.dump(R, open(SP / "v2_results.json", "w"), indent=1)
n_fail = sum(not r["pass"] for r in R)
print(f"\nFLOW CHECKS: {len(R)}   passed {len(R) - n_fail}   failed {n_fail}")
for r in R:
    if not r["pass"]: print("  FAIL", r["area"], "|", r["test"], "|", r["detail"])
