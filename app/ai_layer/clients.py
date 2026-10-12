"""Provider-agnostic LLM clients.  The default is 'no LLM': the tool then runs fully offline with
retrieval-only suggestions and deterministic explanations.

Both clients expose the same tiny interface the rest of the AI layer relies on: `.complete(prompt) ->
str` and a `.model_id` attribute. Which provider is used is a per-user setting (see settings_store),
never hardcoded, so a wrong key/provider pairing (e.g. a Gemini key saved while provider is Anthropic)
fails loudly through /api/settings/test rather than silently.

AnthropicClient uses the public Messages API over HTTPS and needs an Anthropic API key (from
console.anthropic.com, starts with "sk-ant-"), via the ANTHROPIC_API_KEY environment variable or the
Settings screen.

GeminiClient uses the public Generative Language API over HTTPS and needs a Gemini API key (from
aistudio.google.com, GEMINI_API_KEY environment variable or the Settings screen).

Neither is exercised by the automated tests (no key or network in CI); the guard logic they feed is.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from typing import Optional

_FENCE = re.compile(r"```[A-Za-z0-9_+-]*[ \t]*\r?\n?(.*?)```", re.S)


def extract_json(raw):
    """Parse JSON out of an LLM reply: strips markdown code fences and tolerates prose before/after a
    JSON object or array. Returns the parsed value; raises ValueError if no JSON value is found."""
    if not isinstance(raw, str):
        raise ValueError("reply is not text")
    text = raw.strip().lstrip("\ufeff")
    candidates = [text]
    candidates += [m.group(1).strip() for m in _FENCE.finditer(text)]
    dec = json.JSONDecoder()
    for c in candidates:
        try:
            return json.loads(c)
        except (ValueError, RecursionError):
            pass
    for c in candidates:
        for i, ch in enumerate(c):
            if ch in "{[":
                try:
                    obj, _ = dec.raw_decode(c[i:])
                except (ValueError, RecursionError):
                    continue
                if isinstance(obj, (dict, list)):
                    return obj
    raise ValueError("no JSON object or array found in the reply")


PROVIDERS = ("anthropic", "gemini")
DEFAULT_MODEL = {"anthropic": "claude-sonnet-5", "gemini": "gemini-3.8-flash"}
_RETRY_CODES = (429, 500, 502, 503, 529)      # rate limit / provider overloaded: usually gone within seconds


def _post_json(req: urllib.request.Request, timeout: float, provider: str, attempts: int = 3) -> dict:
    """POST and decode JSON, retrying briefly on the provider's temporary-overload responses."""
    delay = 2.0
    for i in range(attempts):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in _RETRY_CODES and i < attempts - 1:
                time.sleep(delay)
                delay *= 2
                continue
            raise RuntimeError(f"{provider} API error {e.code}: {e.read().decode('utf-8', 'replace')[:300]}") from e
    raise RuntimeError(f"{provider} API did not respond")       # unreachable; keeps the type checker honest


class AnthropicClient:
    provider = "anthropic"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, max_tokens: int = 1500,
                 temperature: float = 0.0, timeout: float = 60.0):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.model_id = model or os.environ.get("FYP_LLM_MODEL", DEFAULT_MODEL["anthropic"])
        self.max_tokens, self.temperature, self.timeout = max_tokens, temperature, timeout
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")

    def complete(self, prompt: str) -> str:
        body = json.dumps({"model": self.model_id, "max_tokens": self.max_tokens, "temperature": self.temperature,
                           "messages": [{"role": "user", "content": prompt}]}).encode("utf-8")
        req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body, method="POST", headers={
            "content-type": "application/json", "x-api-key": self.api_key, "anthropic-version": "2023-06-01"})
        data = _post_json(req, self.timeout, "Anthropic")
        return "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")


class GeminiClient:
    provider = "gemini"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, max_tokens: int = 1500,
                 temperature: float = 0.0, timeout: float = 60.0):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.model_id = model or os.environ.get("FYP_LLM_MODEL", DEFAULT_MODEL["gemini"])
        self.max_tokens, self.temperature, self.timeout = max_tokens, temperature, timeout
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is not set")

    def complete(self, prompt: str) -> str:
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_id}:generateContent"
               f"?key={self.api_key}")
        body = json.dumps({"contents": [{"parts": [{"text": prompt}]}],
                           "generationConfig": {"maxOutputTokens": self.max_tokens,
                                                 "temperature": self.temperature}}).encode("utf-8")
        req = urllib.request.Request(url, data=body, method="POST", headers={"content-type": "application/json"})
        data = _post_json(req, self.timeout, "Gemini")
        cands =data.get("candidates") or []
        if not cands:
            return ""
        parts = (cands[0].get("content") or {}).get("parts") or []
        return "".join(p.get("text", "") for p in parts)


_CLIENT_CLS = {"anthropic": AnthropicClient, "gemini": GeminiClient}
_KEY_ENV_VAR = {"anthropic": "ANTHROPIC_API_KEY", "gemini": "GEMINI_API_KEY"}


def resolve_config(api_key: Optional[str] = None, model: Optional[str] = None,
                    provider: Optional[str] = None) -> tuple[Optional[str], Optional[str], str, str]:
    """(key, model, provider, source) with priority: explicit args > saved settings > environment
    variable. `source` is 'explicit', 'settings', 'environment' or 'none' (no key found anywhere).
    `provider` defaults to 'anthropic' when nothing else specifies one, for backward compatibility
    with settings saved before Gemini support existed."""
    from . import settings_store

    if api_key:
        prov = provider or settings_store.get_provider()
        return api_key, model, prov, "explicit"

    prov = provider or settings_store.get_provider()
    saved_key = settings_store.get_api_key()
    if saved_key:
        return saved_key, model or settings_store.get_model_override(), prov, "settings"
    env_key = os.environ.get(_KEY_ENV_VAR.get(prov, "ANTHROPIC_API_KEY"))
    if env_key:
        return env_key, model or os.environ.get("FYP_LLM_MODEL"), prov, "environment"
    return None, model or settings_store.get_model_override(), prov, "none"


def get_client(api_key: Optional[str] = None, model: Optional[str] = None,
               provider: Optional[str] = None):
    """Return a live client (AnthropicClient or GeminiClient, chosen by `provider`) using
    resolve_config's priority order, or None (offline mode) if no key is configured anywhere."""
    key, mdl, prov, _source = resolve_config(api_key, model, provider)
    if not key:
        return None
    cls = _CLIENT_CLS.get(prov, AnthropicClient)
    try:
        return cls(api_key=key, model=mdl)
    except RuntimeError:
        return None


def _mask(key: Optional[str]) -> Optional[str]:
    """Display-safe preview of a key: a short key is never shown (only that one is set); a long key shows
    the provider prefix and the last 4 characters, which can never reconstruct it."""
    if not key:
        return None
    if len(key) < 12:
        return "(key set)"
    return f"{key[:5]}...{key[-4:]}"


def describe_config() -> dict:
    """What get_client() would use right now, WITHOUT exposing the key -- for a settings/health
    screen. 'configured' is false only when source == 'none'."""
    from . import settings_store

    key, mdl, prov, source = resolve_config()
    return {"configured": source != "none", "source": source, "provider": prov,
            "masked_key": _mask(key), "model": mdl or DEFAULT_MODEL.get(prov, "claude-sonnet-5")}
