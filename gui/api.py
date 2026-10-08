"""Thin HTTP layer over app.service for the local GUI.

Everything the GUI shows comes from app.service.run_case.  This module only moves JSON in and out,
maps service errors to HTTP 422 with the service's own problem list, and serves the static
single-page front end.  It contains no risk, matrix or rule logic of its own.

Routes
    GET  /api/health          status, AI mode, evidence counts
    GET  /api/meta            vocabularies the forms need (sources, statuses, fact schema, matrix legend)
    GET  /api/template        service.template_case()
    GET  /api/example         service.example_case()   (ILLUSTRATIVE placeholders)
    GET  /api/risk-library    service.risk_library()
    GET  /api/rules           service.rule_library()
    GET  /api/evidence        ?ids=M01,R08  |  ?q=search words  |  (curated records; the bulk harvest is searched with q)
    POST /api/validate        service.run_case(case) -> {"ok": false, "problems"} or {"ok": true, "result": ...} (always HTTP 200)
    POST /api/run             service.run_case(case) -> result, or 422 {"problems": [...]}
    POST /api/suggest-risks   service.suggest_risks(...) (offline retrieval or guarded LLM)
    POST /api/report          register.md download
    POST /api/register-csv    register.csv download
    POST /api/matrix-svg      colour-coded matrix graphic (SVG)
    POST /api/report-html     printable report with the graphical matrix
"""
from __future__ import annotations

import json
import logging
import math
import mimetypes
import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from flask import Flask, Response, request, send_from_directory  # noqa: E402
from werkzeug.exceptions import HTTPException  # noqa: E402

from app import service  # noqa: E402
from app.ai_layer.clients import describe_config, get_client  # noqa: E402
from app.ai_layer import settings_store  # noqa: E402
from app.engine.matrix import DEFAULT_LABELS, DEFAULT_P_EDGES, matrix_level  # noqa: E402
from app.engine.models import RiskStatus  # noqa: E402
from app.reporting.matrix_graphic import register_html  # noqa: E402
from app.reporting.register_report import register_csv as register_csv_text  # noqa: E402

from . import __version__  # noqa: E402

STATIC = Path(__file__).resolve().parent / "static"
WORKBOOK = ROOT / "Literature_Evidence_Package.xlsx"
log =logging.getLogger("gui.api")

# Windows can map .js to text/plain in the registry, which breaks ES modules.
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("text/javascript", ".mjs")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("image/svg+xml", ".svg")


# ----------------------------------------------------------------------------------- helpers
def _clean(o: Any) -> Any:
    """Replace NaN/inf with None so the browser always receives valid JSON."""
    if isinstance(o, float):
        return o if math.isfinite(o) else None
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if hasattr(o, "item") and not isinstance(o, (str, bytes)):
        try:
            return _clean(o.item())
        except (TypeError, ValueError):
            return str(o)
    return o


def _json(obj: Any, status: int = 200, headers: dict | None = None) -> Response:
    body = json.dumps(_clean(obj), allow_nan=False, ensure_ascii=False, default=str)
    return Response(body, status=status, mimetype="application/json", headers=headers)


def _problems(problems: list[str], status: int = 422, **extra) -> Response:
    return _json({"ok": False, "problems": list(problems), **extra}, status)


def _describe(e: Exception) -> str:
    if isinstance(e, KeyError):
        return f"a required field is missing: {e}"
    if isinstance(e, TypeError):
        return f"a value has the wrong type or is empty ({e})"
    return str(e)


class BadRequest(Exception):
    """A malformed request body; becomes a clean JSON error (never HTML, never a traceback)."""

    def __init__(self, problems: list[str], status: int = 422):
        super().__init__("; ".join(problems))
        self.problems, self.status = problems, status


# Anything the service or a renderer can raise on a malformed-but-parseable case is the caller's input problem.
_INPUT_ERRORS = (ValueError, TypeError, KeyError, AttributeError, IndexError, ArithmeticError, RecursionError)
MAX_JSON_DEPTH = 40
_ALLOWED_HOSTS = {"127.0.0.1", "localhost", "::1", "[::1]"}


def _reject_constant(name: str):
    raise ValueError(f"{name} is not valid JSON")


def _too_deep(o: Any, limit: int = MAX_JSON_DEPTH) -> bool:
    stack = [(o, 1)]
    while stack:
        cur, d = stack.pop()
        if isinstance(cur, (dict, list)):
            if d > limit:
                return True
            stack.extend((v, d + 1) for v in (cur.values() if isinstance(cur, dict) else cur))
    return False


def _json_body() -> Any:
    """Parse the request body as JSON. Invalid JSON, NaN/Infinity and absurd nesting raise BadRequest."""
    raw = request.get_data(cache=True)
    try:
        data = json.loads(raw.decode("utf-8-sig"), parse_constant=_reject_constant)
    except (ValueError, RecursionError, UnicodeDecodeError):
        raise BadRequest(["request body is not valid JSON"])
    if _too_deep(data):
        raise BadRequest([f"request body is nested more than {MAX_JSON_DEPTH} levels deep"])
    return data


def _json_object() -> dict:
    data = _json_body()
    if not isinstance(data, dict):
        raise BadRequest([f"request body must be a JSON object, not {type(data).__name__ if data is not None else 'null'}"])
    return data


def _opt_str(body: dict, name: str) -> Any:
    """body[name] if it is text or null; anything else (number, list, bool, object) is a 422."""
    v = body.get(name)
    if v is not None and not isinstance(v, str):
        raise BadRequest([f"{name} must be a string"])
    return v


def _case_from_request() -> dict:
    data = _json_object()
    if "case" in data and isinstance(data["case"], dict):
        data = data["case"]
    return data


def _gui_checks(case: dict) -> list[str]:
    """Input-shape checks the service does not perform itself (reported, never corrected)."""
    out: list[str] = []
    edges = case.get("impact_bin_edges_fraction")
    if edges is not None:
        ok = isinstance(edges, list) and len(edges) == 4 and all(
            isinstance(x, (int, float)) and not isinstance(x, bool) for x in edges)
        if not ok:
            out.append("impact_bin_edges_fraction: enter four numbers (fractions of the baseline duration) or leave all four blank")
        elif any(b <= a for a, b in zip(edges, edges[1:])) or edges[0] <= 0:
            out.append("impact_bin_edges_fraction: the four edges must be positive and strictly ascending")
    return out


@lru_cache(maxsize=1)
def evidence_store():
    store = service._store()           # the service's own loader for the full evidence corpus
    store.build_index()                # pay the indexing cost once at start-up, not on the first search
    return store


@lru_cache(maxsize=1)
def evidence_index() -> dict:
    return service.evidence_index_from_workbook()


def _record(r) -> dict:
    return {"id": r.evidence_id, "citation": r.citation, "doi": r.doi, "context": r.context,
            "evidence_depth": r.evidence_depth, "text": r.text}


def ai_status() -> dict:
    client = get_client()
    if client is None:
        return {"mode": "offline", "label": "AI: offline mode (evidence retrieval only)",
                "model_id": None}
    return {"mode": "llm", "label": f"AI: guarded LLM mode ({client.model_id})", "model_id": client.model_id}


def _fact_schema() -> list[dict]:
    """Facts referenced by the bundled rule base, with the type the rules compare them as."""
    facts: dict[str, dict] = {}
    for r in service.rule_library():
        for c in (r.get("all_of") or []) + (r.get("any_of") or []):
            pairs = [(c.get("fact"), isinstance(c.get("value"), bool))]
            if c.get("other_fact"):
                pairs.append((c["other_fact"], False))
            for name, is_bool in pairs:
                if not name or name == "planned_duration_days":
                    continue
                ent = facts.setdefault(name, {"name": name, "type": "boolean" if is_bool else "number", "rules": []})
                if r["id"] not in ent["rules"]:
                    ent["rules"].append(r["id"])
    return list(facts.values())


# ----------------------------------------------------------------------------------- app
def create_app() -> Flask:
    app = Flask(__name__, static_folder=str(STATIC), static_url_path="/static")
    app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    app.json.sort_keys = False

    @app.get("/")
    def index():
        resp = send_from_directory(STATIC, "index.html")
        resp.headers["Cache-Control"] = "no-store"
        return resp

    @app.get("/favicon.ico")
    def favicon():
        return send_from_directory(STATIC, "favicon.svg", mimetype="image/svg+xml")

    # ---------------------------------------------------------------- reference data
    @app.get("/api/health")
    def health():
        store = evidence_store()
        return _json({"ok": True, "version": __version__, "ai": ai_status(), "evidence_records": len(store),
                      "evidence_workbook_found": WORKBOOK.exists(), "sources": service.SOURCES})

    @app.get("/api/meta")
    def meta():
        return _json({
            "sources": service.SOURCES,
            "statuses": [s.value for s in RiskStatus],
            "dist_kinds": ["pert", "triangular", "uniform", "fixed"],
            "facts": _fact_schema(),
            "matrix": {"p_edges": list(DEFAULT_P_EDGES), "labels": list(DEFAULT_LABELS),
                       "levels": {str(p): {str(i): matrix_level(p, i) for i in range(1, 6)} for p in range(1, 6)},
                       "note": "Probability-class edges and level thresholds are the engine's equal-width ASSUMPTIONS."},
        })

    @app.get("/api/template")
    def template():
        return _json(service.template_case())

    @app.get("/api/example")
    def example():
        return _json(service.example_case())

    @app.get("/api/risk-library")
    def risk_library():
        return _json(service.risk_library())

    @app.get("/api/rules")
    def rules():
        return _json(service.rule_library())

    @app.get("/api/evidence")
    def evidence():
        store = evidence_store()
        ids = request.args.get("ids")
        q = request.args.get("q")
        missing: list[str] = []
        if ids:
            wanted = [x.strip() for x in ids.split(",") if x.strip()]
            recs = [store.get(x) for x in wanted]
            missing = [x for x, r in zip(wanted, recs) if r is None]
            recs = [r for r in recs if r is not None]
        elif q:
            try:
                k = max(1, min(100, int(request.args.get("k", 20))))
            except ValueError:
                k = 20
            recs = store.retrieve(q, k)
        else:
            # the bulk literature harvest (OA-... ids, tens of thousands of records) is reached with q= or ids=
            recs = [r for r in store.all() if not r.evidence_id.startswith("OA-")]
        return _json({"records": [_record(r) for r in recs], "missing": missing, "count": len(store),
                      "workbook": WORKBOOK.name})

    # ---------------------------------------------------------------- settings (AI provider)
    @app.get("/api/settings")
    def get_settings():
        """Never returns the key itself -- only whether one is configured, where it came from
        (settings file saved via this screen, or an ANTHROPIC_API_KEY environment variable), and a
        masked preview. The key is stored outside the project folder (settings_store.settings_path())."""
        return _json({**describe_config(), "settings_path": str(settings_store.settings_path())})

    @app.post("/api/settings")
    def post_settings():
        body = _json_object()
        updates = {}
        for name in ("api_key", "model", "provider"):
            if name in body:
                updates[name] = (_opt_str(body, name) or "").strip()
        try:
            settings_store.save_settings(updates)
        except ValueError as e:
            return _problems([str(e)])
        return _json({**describe_config(), "settings_path": str(settings_store.settings_path()),
                      "saved": True, "ai": ai_status()})

    @app.post("/api/settings/test")
    def test_settings():
        """Makes ONE small, real request to the provider to confirm the key works, so the person
        knows before relying on it. Costs a trivial amount of their API usage; never happens on
        every keystroke or on save alone -- only when this route is explicitly called."""
        body = _json_object()
        key = (_opt_str(body, "api_key") or "").strip() or None
        model = (_opt_str(body, "model") or "").strip() or None
        provider = (_opt_str(body, "provider") or "").strip() or None
        client = get_client(api_key=key, model=model, provider=provider)
        if client is None:
            return _json({"ok": False, "message": "No API key configured (enter one above, or set ANTHROPIC_API_KEY / GEMINI_API_KEY)."})
        try:
            reply = client.complete("Reply with exactly one word: OK")
        except Exception as e:  # noqa: BLE001 -- any network/auth/provider failure is a normal, expected outcome here
            msg = str(e)
            if key and key in msg:
                msg = msg.replace(key, "<key>")
            return _json({"ok": False, "message": f"Request failed: {msg}", "model_id": client.model_id})
        return _json({"ok": True, "message": f"Connected. Model replied: {reply.strip()[:80]!r}", "model_id": client.model_id})

    # ---------------------------------------------------------------- analysis
    @app.post("/api/validate")
    def validate():
        # Live validation: problems are an expected outcome, so they come back with HTTP 200 and ok=false
        # (the browser would otherwise log every keystroke's 422 as a console error). /api/run keeps 422.
        case = _case_from_request()          # a malformed body is a 400/422 JSON error (BadRequest handler)
        extra = _gui_checks(case)
        try:
            res = service.run_case(case, evidence_index())
        except service.CaseError as e:
            return _problems(list(e.problems) + extra, 200)
        except _INPUT_ERRORS as e:
            return _problems([_describe(e)] + extra, 200)
        if extra:
            return _problems(extra, 200)
        return _json({"ok": True, "warnings": res["warnings"], "result": res})

    @app.post("/api/run")
    def run():
        try:
            case = _case_from_request()
            extra = _gui_checks(case)
            if extra:
                raise service.CaseError(extra)
            res = service.run_case(case, evidence_index())
        except service.CaseError as e:
            return _problems(e.problems)
        except _INPUT_ERRORS as e:
            return _problems([_describe(e)])
        return _json(res)

    # ---------------------------------------------------------------- cost / EMV, options and the decision
    @app.post("/api/analyze")
    def analyze():
        """Monte Carlo schedule, cost and event EMV, option comparison and the AUTHORIZE / ACCEPT command for a case
        that carries a cost model and (optionally) mitigations.  Wraps service.run_analysis; nothing is added here."""
        try:
            res = service.run_analysis(_case_from_request(), evidence_index())
        except service.CaseError as e:
            return _problems(e.problems)
        except _INPUT_ERRORS as e:
            return _problems([_describe(e)])
        return _json(res)

    @app.post("/api/analysis-report")
    def analysis_report():
        try:
            res = service.run_analysis(_case_from_request(), evidence_index())
        except service.CaseError as e:
            return _problems(e.problems)
        except _INPUT_ERRORS as e:
            return _problems([_describe(e)])
        return Response(res["report_markdown"], mimetype="text/markdown",
                        headers={"Content-Disposition": 'attachment; filename="analysis.md"'})

    @app.get("/api/mitigation-catalogue")
    def mitigation_catalogue():
        return _json({"entries": service.mitigation_catalogue()})

    @app.get("/api/example-analysis")
    def example_analysis():
        return _json(service.example_analysis_case())

    @app.post("/api/suggest-risks")
    def suggest_risks():
        d = _json_object()
        for f in ("query", "activity_name"):
            if d.get(f) is not None and not isinstance(d.get(f), str):
                raise BadRequest([f"{f} must be a string"])
        query = (d.get("query") or "").strip()
        if not query:
            return _problems(["enter a few words describing the conditions or risks to search for"])
        try:
            k = max(1, min(20, int(d.get("k") or 6)))
        except (TypeError, ValueError):
            k = 6
        client = get_client()
        try:
            out = service.suggest_risks(d.get("activity_name") or "Brick masonry", query, client=client, k=k)
        except Exception as e:
            log.exception("suggest failed")
            return _problems([f"suggestion request failed: {e}"], 502 if client else 500)
        out["ok"] = True
        out["ai"] = ai_status()
        return _json(out)

    def _run_for_download():
        case = _case_from_request()
        extra = _gui_checks(case)
        if extra:
            raise service.CaseError(extra)
        return service.run_case(case, evidence_index())

    @app.post("/api/report")
    def report():
        try:
            res = _run_for_download()
        except service.CaseError as e:
            return _problems(e.problems)
        except _INPUT_ERRORS as e:
            return _problems([_describe(e)])
        return Response(res["report_markdown"], mimetype="text/markdown",
                        headers={"Content-Disposition": 'attachment; filename="register.md"'})

    @app.post("/api/register-csv")
    def register_csv():
        try:
            res = _run_for_download()
        except service.CaseError as e:
            return _problems(e.problems)
        except _INPUT_ERRORS as e:
            return _problems([_describe(e)])
        # utf-8-sig (BOM) so Excel on Windows decodes non-ASCII text correctly
        return Response(register_csv_text(res).encode("utf-8-sig"), content_type="text/csv; charset=utf-8",
                        headers={"Content-Disposition": 'attachment; filename="register.csv"'})

    @app.post("/api/matrix-svg")
    def matrix_svg_download():
        try:
            res = _run_for_download()
        except service.CaseError as e:
            return _problems(e.problems)
        except _INPUT_ERRORS as e:
            return _problems([_describe(e)])
        return Response(res["matrix_svg"], mimetype="image/svg+xml",
                        headers={"Content-Disposition": 'attachment; filename="risk_matrix.svg"'})

    @app.post("/api/report-html")
    def report_html_download():
        try:
            res = _run_for_download()
        except service.CaseError as e:
            return _problems(e.problems)
        except _INPUT_ERRORS as e:
            return _problems([_describe(e)])
        return Response(register_html(res, evidence_index()), mimetype="text/html",
                        headers={"Content-Disposition": 'attachment; filename="risk_report.html"'})

    @app.before_request
    def _host_check():
        """DNS-rebinding hardening: only answer requests addressed to the loopback host names."""
        host = (request.host or "").strip().lower()
        name = host[: host.index("]") + 1] if host.startswith("[") and "]" in host else host.rsplit(":", 1)[0] if host.count(":") == 1 else host
        if name not in _ALLOWED_HOSTS:
            return _json({"ok": False, "problems": ["this tool only answers requests addressed to 127.0.0.1 or localhost"]}, 403)
        return None

    @app.errorhandler(BadRequest)
    def bad_request(e):
        return _problems(e.problems, e.status)

    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith("/api/"):
            return _problems([f"no such endpoint: {request.path}"], 404)
        return e

    @app.errorhandler(405)
    def bad_method(e):
        if request.path.startswith("/api/"):
            return _problems([f"method {request.method} not allowed on {request.path}"], 405)
        return e

    @app.errorhandler(413)
    def too_large(e):
        return _problems(["request too large"], 413)

    @app.errorhandler(HTTPException)
    def http_error(e):
        if request.path.startswith("/api/"):
            return _problems([e.description or e.name], e.code or 400)
        return e

    @app.errorhandler(Exception)
    def internal_error(e):
        if isinstance(e, HTTPException):          # not reached (handled above); defensive
            return e
        log.exception("unhandled error on %s", request.path)
        return _json({"ok": False, "error": "internal error"}, 500)

    return app
