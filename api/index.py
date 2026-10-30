"""Vercel entry point: exposes the Flask app of the FYP Risk Tool as `app`.
Serverless storage is read-only except /tmp, so user settings are redirected there."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("XDG_CONFIG_HOME", "/tmp")
os.environ.setdefault("HOME", "/tmp")

from gui.api import create_app  # noqa: E402

app = create_app()
