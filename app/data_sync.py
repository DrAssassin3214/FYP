"""Online-first data with a local fallback.

Rule (set by the project owner): when the device is online the tool uses the newest data pack published on the
internet; when it is offline it uses the local data that is bundled in ``data/`` (the database created earlier).

Order of use for each data file, first one that works:
    1. the last good ONLINE data pack stored in the per-user cache folder (downloaded and verified earlier),
    2. the bundled file in ``data/``.
``refresh()`` tries to download a newer pack; any failure (no network, timeout, 404, bad hash, bad JSON, wrong
structure) leaves what is already in use untouched.  Nothing here raises to the caller and importing this module never
touches the network.

Integrity: a pack is accepted only if every file matches the SHA-256 in its manifest and passes a structure check.
The hash protects against corruption, NOT against a malicious host: only publish the pack from a repository you
control.  The pack version and hashes are shown in the GUI and written into every analysis audit record, so a result
always says which data it was produced with.  Online data never changes the code, only the four data files below.

Manifest (``manifest.json`` next to the files):
    {"schema": 1, "version": "2026-10-12.1",
     "files": {"rules_masonry.json": {"sha256": "...", "bytes": 12111}, ...}}
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import socket
import tempfile
import threading
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Optional

ROOT = Path(__file__).resolve().parents[1]
BUNDLED_DIR = ROOT / "data"
APP_DIR_NAME = "MasonryDelayRiskGUI"          # same per-user folder as the settings file

PACK_FILES = ("risk_library_masonry.json", "rules_masonry.json", "literature_seed.json", "mitigation_catalogue.json")
DEFAULT_MANIFEST_URL = "https://raw.githubusercontent.com/DrAssassin3214/bricksly-datapack/main/manifest.json"
TIMEOUT_S = 6
MAX_FILE_BYTES = 5_000_000
USER_AGENT = "FYP-BrickworkRiskTool/1.0 (data pack check)"

_lock = threading.Lock()
_clear_callbacks: list[Callable[[], None]] = []


# ------------------------------------------------------------------------------------------------ locations
def base_dir() -> Path:
    """Per-user folder; BRICKSLY_DATA_DIR overrides it (used by the tests)."""
    env = os.environ.get("BRICKSLY_DATA_DIR")
    if env:
        return Path(env)
    if os.name == "nt":
        root = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
    else:
        root = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(root) / APP_DIR_NAME


def pack_dir() -> Path:
    return base_dir() / "data_pack"


def cache_dir() -> Path:
    return base_dir() / "online_cache"


def manifest_url() -> str:
    """BRICKSLY_PACK_URL, then the url saved in pack_config.json, then the default.  An empty value turns online
    updates off (the tool then uses only the bundled data)."""
    if "BRICKSLY_PACK_URL" in os.environ:
        return os.environ["BRICKSLY_PACK_URL"].strip()
    try:
        cfg = json.loads((base_dir() / "pack_config.json").read_text(encoding="utf-8"))
        if isinstance(cfg, dict) and isinstance(cfg.get("manifest_url"), str):
            return cfg["manifest_url"].strip()
    except (OSError, ValueError):
        pass
    return DEFAULT_MANIFEST_URL


def register_cache_clear(fn: Callable[[], None]) -> None:
    """Modules that cache parsed data register a clear function, called after a new pack is installed."""
    if fn not in _clear_callbacks:
        _clear_callbacks.append(fn)


# ------------------------------------------------------------------------------------------------ small helpers
def _sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _version_key(v: Any) -> tuple:
    parts = []
    for p in str(v).replace("-", ".").split("."):
        parts.append((0, int(p)) if p.isdigit() else (1, p))
    return tuple(parts)


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _installed() -> Optional[dict]:
    """pack.json of the installed online pack, or None."""
    try:
        meta = _read_json(pack_dir() / "pack.json")
    except (OSError, ValueError):
        return None
    return meta if isinstance(meta, dict) and isinstance(meta.get("files"), dict) else None


@lru_cache(maxsize=32)
def _verified(path_str: str, mtime_ns: int, size: int, sha: str) -> bool:
    try:
        return _sha256(Path(path_str).read_bytes()) == sha
    except OSError:
        return False


# ------------------------------------------------------------------------------------------------ structure checks
def _is_obj_list(x: Any, keys: tuple) -> bool:
    return isinstance(x, list) and bool(x) and all(isinstance(r, dict) and all(k in r for k in keys) for r in x)


def validate_file(name: str, data: Any) -> Optional[str]:
    """None if the structure is acceptable, otherwise a short reason."""
    if name == "risk_library_masonry.json":
        if not _is_obj_list(data, ("id", "name", "category")):
            return "risk library must be a non-empty list of risks with id, name and category"
        ids = [r["id"] for r in data]
        if len(set(ids)) != len(ids):
            return "risk library has duplicate ids"
    elif name == "rules_masonry.json":
        if not _is_obj_list(data, ("id", "risk_id", "level", "source")):
            return "rules must be a non-empty list with id, risk_id, level and source"
        if any(r["level"] not in ("elevated", "normal") for r in data):
            return "a rule has a level other than elevated or normal"
    elif name == "literature_seed.json":
        if not (isinstance(data, dict) and isinstance(data.get("studies"), list) and isinstance(data.get("rows"), list)
                and data["rows"]):
            return "seed must have studies and rows"
        for r in data["rows"]:
            if not isinstance(r, dict) or "study" not in r:
                return "a seed row has no study"
    elif name == "mitigation_catalogue.json":
        if not (isinstance(data, dict) and isinstance(data.get("entries"), list)):
            return "catalogue must have an entries list"
        blob = json.dumps(data).lower()
        if '"effect_size"' in blob or '"p_after"' in blob or '"delay_after"' in blob or '"cost"' in blob:
            return "catalogue must not carry costs or effect sizes (the user enters them with a Source)"
    else:
        return f"{name} is not a data-pack file"
    return None


# ------------------------------------------------------------------------------------------------ resolve
def resolve(name: str) -> Path:
    """Path of the file to read now: the verified online copy if one is installed, otherwise the bundled file."""
    bundled = BUNDLED_DIR / name
    if name not in PACK_FILES:
        return bundled
    meta = _installed()
    if not meta:
        return bundled
    want = (meta["files"].get(name) or {}).get("sha256")
    p = pack_dir() / name
    try:
        st = p.stat()
    except OSError:
        return bundled
    if want and _verified(str(p), st.st_mtime_ns, st.st_size, want):
        return p
    return bundled


def load(name: str) -> Any:
    p = resolve(name)
    try:
        return _read_json(p)
    except (OSError, ValueError):
        if p != BUNDLED_DIR / name:               # the installed copy went bad: fall back to the bundled file
            return _read_json(BUNDLED_DIR / name)
        raise


def status() -> dict:
    meta = _installed()
    files = {}
    for n in PACK_FILES:
        files[n] = "online pack" if resolve(n) != BUNDLED_DIR / n else "bundled"
    online_in_use = any(v == "online pack" for v in files.values())
    return {"mode": "online pack" if online_in_use else "bundled",
            "version": meta.get("version") if (meta and online_in_use) else "bundled",
            "installed_utc": meta.get("installed_utc") if meta else None,
            "last_check_utc": (meta or {}).get("last_check_utc") or _last_check(),
            "manifest_url": manifest_url(), "files": files,
            "sha256": {n: (meta["files"].get(n) or {}).get("sha256") for n in PACK_FILES} if (meta and online_in_use)
            else {n: _sha256((BUNDLED_DIR / n).read_bytes()) for n in PACK_FILES if (BUNDLED_DIR / n).exists()}}


def provenance() -> dict:
    """Short record for audit trails: which data produced a result."""
    s = status()
    return {"data_source": s["mode"], "data_version": s["version"], "data_sha256": s["sha256"]}


def _last_check() -> Optional[str]:
    try:
        return _read_json(base_dir() / "last_check.json").get("utc")
    except (OSError, ValueError, AttributeError):
        return None


def _note_check(ok: bool, message: str) -> None:
    try:
        base_dir().mkdir(parents=True, exist_ok=True)
        (base_dir() / "last_check.json").write_text(json.dumps({"utc": _now(), "ok": ok, "message": message}), encoding="utf-8")
    except OSError:
        pass


# ------------------------------------------------------------------------------------------------ network
class FetchError(Exception):
    pass


def _http_get(url: str) -> bytes:
    if urllib.parse.urlparse(url).scheme != "https":
        raise FetchError("only https addresses are accepted")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            raw = resp.read(MAX_FILE_BYTES + 1)
    except urllib.error.HTTPError as e:
        raise FetchError(f"HTTP {e.code}") from e
    except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError, OSError) as e:
        raise FetchError(str(getattr(e, "reason", None) or e)) from e
    if len(raw) > MAX_FILE_BYTES:
        raise FetchError("file too large")
    return raw


def refresh(url: Optional[str] = None, fetch: Optional[Callable[[str], bytes]] = None) -> dict:
    """Try to install a newer online data pack.  Returns
    {"ok", "online", "updated", "version", "message"}.  Never raises; on any failure the data in use is unchanged."""
    get = fetch or _http_get
    url = (url if url is not None else manifest_url()).strip()
    if not url:
        return {"ok": True, "online": False, "updated": False, "message": "Online updates are switched off; using the data on this computer."}
    with _lock:
        try:
            manifest = json.loads(get(url).decode("utf-8-sig"))
        except FetchError as e:
            _note_check(False, str(e))
            return {"ok": False, "online": False, "updated": False,
                    "message": f"Offline or the data pack is unreachable ({e}); using the data on this computer."}
        except (ValueError, UnicodeDecodeError):
            _note_check(False, "manifest unreadable")
            return {"ok": False, "online": True, "updated": False, "message": "The online manifest could not be read; data in use is unchanged."}
        files = manifest.get("files") if isinstance(manifest, dict) else None
        version = str(manifest.get("version", "")) if isinstance(manifest, dict) else ""
        if manifest.get("schema") != 1 or not version or not isinstance(files, dict) or not files:
            _note_check(False, "bad manifest")
            return {"ok": False, "online": True, "updated": False, "message": "The online manifest is not in the expected format; data in use is unchanged."}
        meta = _installed()
        if meta and _version_key(version) <= _version_key(meta.get("version", "")):
            _note_check(True, "up to date")
            return {"ok": True, "online": True, "updated": False, "version": meta.get("version"),
                    "message": f"Online data pack {meta.get('version')} is already installed."}
        names = [n for n in files if n in PACK_FILES]
        if not names:
            return {"ok": False, "online": True, "updated": False, "message": "The manifest lists no known data files."}
        base = url.rsplit("/", 1)[0] + "/"
        tmp = Path(tempfile.mkdtemp(prefix="pack_", dir=str(_ensure(base_dir()))))
        try:
            got: dict[str, dict] = {}
            for n in names:
                want = str((files[n] or {}).get("sha256", "")).lower()
                try:
                    raw = get(base + n)
                except FetchError as e:
                    return {"ok": False, "online": False, "updated": False, "message": f"Download of {n} failed ({e}); data in use is unchanged."}
                if _sha256(raw) != want:
                    return {"ok": False, "online": True, "updated": False, "message": f"{n} does not match its checksum; rejected."}
                try:
                    data = json.loads(raw.decode("utf-8-sig"))
                except (ValueError, UnicodeDecodeError):
                    return {"ok": False, "online": True, "updated": False, "message": f"{n} is not valid JSON; rejected."}
                bad = validate_file(n, data)
                if bad:
                    return {"ok": False, "online": True, "updated": False, "message": f"{n} rejected: {bad}."}
                (tmp / n).write_bytes(raw)
                got[n] = {"sha256": want, "bytes": len(raw)}
            # files absent from this pack keep coming from the previous pack or the bundle
            prev = (meta or {}).get("files", {})
            pd = _ensure(pack_dir())
            for n, info in got.items():
                os.replace(tmp / n, pd / n)
            merged = {n: i for n, i in prev.items() if n not in got and (pd / n).exists()}
            merged.update(got)
            (pd / "pack.json").write_text(json.dumps({"version": version, "installed_utc": _now(), "source_url": url,
                                                       "files": merged}, indent=2), encoding="utf-8")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        _verified.cache_clear()
        for fn in _clear_callbacks:
            try:
                fn()
            except Exception:                      # noqa: BLE001 - a cache clear must never break an update
                pass
        _note_check(True, f"installed {version}")
        return {"ok": True, "online": True, "updated": True, "version": version,
                "message": f"Installed online data pack {version}."}


def _ensure(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def refresh_in_background(on_done: Optional[Callable[[dict], None]] = None) -> threading.Thread:
    """Check for a newer pack without blocking start-up."""
    def run() -> None:
        res = refresh()
        if on_done:
            on_done(res)
    t = threading.Thread(target=run, name="data-pack-refresh", daemon=True)
    t.start()
    return t


def reset() -> dict:
    """Remove the installed online pack and go back to the bundled data."""
    shutil.rmtree(pack_dir(), ignore_errors=True)
    _verified.cache_clear()
    for fn in _clear_callbacks:
        try:
            fn()
        except Exception:                          # noqa: BLE001
            pass
    return status()


# ------------------------------------------------------------------------------------------------ search cache
def _ckey(kind: str, query: str) -> Path:
    return cache_dir() / f"{kind}_{_sha256(query.encode('utf-8'))[:24]}.json"


def cache_put(kind: str, query: str, payload: Any) -> None:
    try:
        _ensure(cache_dir())
        _ckey(kind, query).write_text(json.dumps({"utc": _now(), "query": query, "payload": payload}), encoding="utf-8")
    except (OSError, TypeError, ValueError):
        pass


def cache_get(kind: str, query: str) -> Optional[dict]:
    try:
        d = _read_json(_ckey(kind, query))
        return d if isinstance(d, dict) and "payload" in d else None
    except (OSError, ValueError):
        return None
