"""Local, per-user settings for the AI layer: the LLM API key and an optional model override.

Stored OUTSIDE the project folder, in the OS's per-user application-data location, deliberately so
the key never ends up inside the project directory -- if this project folder is zipped up and
submitted or shared (a real risk for a student FYP), no secret travels with it. Nothing here is
committed to source control, read by the report generator, or included in an exported case file.
"""
from __future__ import annotations

import json
import os
import stat
from pathlib import Path
from typing import Optional

APP_DIR_NAME = "MasonryDelayRiskGUI"
_KNOWN_KEYS = {"api_key", "model", "provider"}
_KNOWN_PROVIDERS = {"anthropic", "gemini"}
_LEGACY_KEY_FIELD = "anthropic_api_key"  # pre-Gemini field name; still read for settings saved before


def _settings_dir() -> Path:
    if os.name == "nt":
        base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / APP_DIR_NAME


def settings_path() -> Path:
    return _settings_dir() / "settings.json"


def load_settings() -> dict:
    """Never raises: a missing or corrupt file is treated as 'no settings saved'."""
    p = settings_path()
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {}


def save_settings(updates: dict) -> dict:
    """Merge `updates` into the stored settings and write them.  A value of None or "" for a
    recognised key REMOVES it (e.g. save_settings({"api_key": ""}) clears the key).
    Returns the settings actually stored (never the raw values passed in, in case a caller wants
    to log the return value -- log the RESULT of get_status(), not this)."""
    unknown = set(updates) - _KNOWN_KEYS
    if unknown:
        raise ValueError(f"unknown setting(s): {sorted(unknown)}")
    if updates.get("provider") and updates["provider"] not in _KNOWN_PROVIDERS:
        raise ValueError(f"unknown provider {updates['provider']!r}; must be one of {sorted(_KNOWN_PROVIDERS)}")
    cur = load_settings()
    for k, v in updates.items():
        if v in (None, ""):
            cur.pop(k, None)
        else:
            cur[k] = v
    d = _settings_dir()
    d.mkdir(parents=True, exist_ok=True)
    p = settings_path()
    p.write_text(json.dumps(cur, indent=2), encoding="utf-8")
    try:
        if os.name != "nt":
            os.chmod(p, stat.S_IRUSR | stat.S_IWUSR)  # best-effort: owner read/write only
    except OSError:
        pass
    return cur


def get_api_key() -> Optional[str]:
    s = load_settings()
    return s.get("api_key") or s.get(_LEGACY_KEY_FIELD) or None


def get_model_override() -> Optional[str]:
    return load_settings().get("model") or None


def get_provider() -> str:
    """Which provider the saved key/model belong to. Defaults to 'anthropic' -- both for a fresh
    install and for settings saved before Gemini support existed (an unrecognised or missing value
    is never treated as a saved choice)."""
    p = load_settings().get("provider")
    return p if p in _KNOWN_PROVIDERS else "anthropic"


def mask_key(key: Optional[str]) -> Optional[str]:
    """Never return enough of a key to reconstruct it; used for anything the GUI displays back."""
    if not key:
        return None
    if len(key) <= 8:
        return "*" * len(key)
    return f"{key[:5]}...{key[-4:]}"
