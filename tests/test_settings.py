import json
import os

import pytest

from app.ai_layer import clients, settings_store


@pytest.fixture(autouse=True)
def isolated_settings_dir(tmp_path, monkeypatch):
    """Every test gets its own fake app-data directory so nothing touches the real user's machine
    and tests never interfere with each other."""
    monkeypatch.setenv("APPDATA", str(tmp_path))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("FYP_LLM_MODEL", raising=False)
    yield tmp_path


def test_settings_path_is_outside_the_project_folder(isolated_settings_dir):
    p = settings_store.settings_path()
    assert str(isolated_settings_dir) in str(p)
    project_root = settings_store.__file__
    assert str(p).lower() != project_root.lower()
    assert "MasonryDelayRiskGUI" in str(p)


def test_missing_or_corrupt_file_is_empty_not_an_error(isolated_settings_dir):
    assert settings_store.load_settings() == {}
    settings_store.settings_path().parent.mkdir(parents=True, exist_ok=True)
    settings_store.settings_path().write_text("{not json", encoding="utf-8")
    assert settings_store.load_settings() == {}


def test_save_get_and_clear_round_trip():
    settings_store.save_settings({"api_key": "sk-ant-abcdefghijklmnop", "model": "claude-opus-5-5"})
    assert settings_store.get_api_key() == "sk-ant-abcdefghijklmnop"
    assert settings_store.get_model_override() == "claude-opus-5-5"
    settings_store.save_settings({"api_key": ""})       # clear only the key
    assert settings_store.get_api_key() is None
    assert settings_store.get_model_override() == "claude-opus-5-5"   # model untouched


def test_unknown_setting_rejected():
    with pytest.raises(ValueError):
        settings_store.save_settings({"totally_unrelated": "x"})


def test_unknown_provider_rejected():
    with pytest.raises(ValueError):
        settings_store.save_settings({"provider": "openai"})


def test_provider_defaults_to_anthropic_and_round_trips():
    assert settings_store.get_provider() == "anthropic"
    settings_store.save_settings({"provider": "gemini"})
    assert settings_store.get_provider() == "gemini"
    settings_store.save_settings({"provider": ""})   # clears back to the default
    assert settings_store.get_provider() == "anthropic"


def test_legacy_key_field_still_read(isolated_settings_dir):
    """Settings files saved before Gemini support existed used 'anthropic_api_key'; those keys must
    still be picked up rather than silently going offline after an upgrade."""
    settings_store.settings_path().parent.mkdir(parents=True, exist_ok=True)
    settings_store.settings_path().write_text(json.dumps({"anthropic_api_key": "sk-ant-legacy"}), encoding="utf-8")
    assert settings_store.get_api_key() == "sk-ant-legacy"


def test_masking_never_exposes_the_full_key():
    assert settings_store.mask_key(None) is None
    assert settings_store.mask_key("short") == "*****"
    m = settings_store.mask_key("sk-ant-abcdefghijklmnop")
    assert m == "sk-an...mnop" and "abcdefghijkl" not in m


def test_saved_file_is_not_json_readable_as_something_else(isolated_settings_dir):
    settings_store.save_settings({"api_key": "sk-ant-xxxxxxxxxxxx"})
    raw = json.loads(settings_store.settings_path().read_text(encoding="utf-8"))
    assert raw == {"api_key": "sk-ant-xxxxxxxxxxxx"}


# ---------------------------------------------------------------- clients.resolve_config priority
def test_priority_explicit_over_settings_over_environment():
    os.environ["ANTHROPIC_API_KEY"] = "env-key"
    settings_store.save_settings({"api_key": "settings-key"})
    assert clients.resolve_config()[0:1] == ("settings-key",)
    assert clients.resolve_config()[3] == "settings"
    assert clients.resolve_config(api_key="explicit-key")[3] == "explicit"
    settings_store.save_settings({"api_key": ""})
    assert clients.resolve_config() == ("env-key", None, "anthropic", "environment")
    del os.environ["ANTHROPIC_API_KEY"]
    assert clients.resolve_config() == (None, None, "anthropic", "none")


def test_get_client_offline_when_nothing_configured():
    assert clients.get_client() is None


def test_get_client_uses_saved_settings():
    settings_store.save_settings({"api_key": "sk-ant-realistic-looking-key", "model": "claude-opus-5-5"})
    c = clients.get_client()
    assert c is not None and c.api_key == "sk-ant-realistic-looking-key" and c.model_id == "claude-opus-5-5"


def test_get_client_uses_gemini_when_provider_is_gemini():
    settings_store.save_settings({"api_key": "AIza-fake-gemini-key", "provider": "gemini"})
    c = clients.get_client()
    assert isinstance(c, clients.GeminiClient)
    assert c.api_key == "AIza-fake-gemini-key" and c.model_id == clients.DEFAULT_MODEL["gemini"]


def _http_error(code):
    import io
    import urllib.error

    return urllib.error.HTTPError("http://x", code, "err", {}, io.BytesIO(b'{"error": "boom"}'))


class _Resp:
    def __init__(self, body):
        self._b = body

    def read(self):
        return self._b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_temporary_provider_overload_is_retried_then_succeeds(monkeypatch):
    calls = []

    def fake_urlopen(req, timeout=None):
        calls.append(1)
        if len(calls) < 3:
            raise _http_error(503)
        return _Resp(b'{"candidates": [{"content": {"parts": [{"text": "OK"}]}}]}')

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    monkeypatch.setattr("time.sleep", lambda s: None)
    assert clients.GeminiClient(api_key="k").complete("hi") == "OK" and len(calls) == 3


def test_auth_errors_are_not_retried_and_name_the_provider(monkeypatch):
    calls = []

    def fake_urlopen(req, timeout=None):
        calls.append(1)
        raise _http_error(401)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    monkeypatch.setattr("time.sleep", lambda s: None)
    with pytest.raises(RuntimeError, match="Gemini API error 401"):
        clients.GeminiClient(api_key="k").complete("hi")
    assert len(calls) == 1


def test_describe_config_never_exposes_the_key():
    assert clients.describe_config() == {"configured": False, "source": "none", "provider": "anthropic",
                                          "masked_key": None, "model": "claude-sonnet-5"}
    settings_store.save_settings({"api_key": "sk-ant-abcdefghijklmnop"})
    d = clients.describe_config()
    assert d["configured"] is True and d["source"] == "settings" and d["provider"] == "anthropic"
    assert d["masked_key"] == "sk-an...mnop"
    assert "abcdefghijkl" not in json.dumps(d)
