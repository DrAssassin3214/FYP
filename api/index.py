"""Vercel entry point: exposes the Flask app of the FYP Risk Tool as `app`.

Serverless storage is read-only except /tmp, so user settings are redirected there.
The whole site is protected by HTTP Basic authentication. The user name and password are read from the
FYP_USER and FYP_PASSWORD environment variables (set them in the Vercel project settings, never in git);
if either is missing every request is refused.
"""
import hmac
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("XDG_CONFIG_HOME", "/tmp")
os.environ.setdefault("HOME", "/tmp")

from flask import Response, request  # noqa: E402

from gui.api import create_app  # noqa: E402

app = create_app()


def _deny() -> Response:
    return Response("Sign in required.", 401, {"WWW-Authenticate": 'Basic realm="FYP Risk Tool", charset="UTF-8"'})


@app.before_request
def _require_login():
    user = os.environ.get("FYP_USER", "")
    password = os.environ.get("FYP_PASSWORD", "")
    if not user or not password:
        return Response("Server login is not configured.", 503)
    auth = request.authorization
    if not auth or auth.type != "basic":
        return _deny()
    ok_user = hmac.compare_digest((auth.username or "").encode(), user.encode())
    ok_pass = hmac.compare_digest((auth.password or "").encode(), password.encode())
    return None if (ok_user and ok_pass) else _deny()
