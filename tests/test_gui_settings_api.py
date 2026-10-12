"""Tests for the /api/settings routes.  Isolated from the real machine: APPDATA/XDG_CONFIG_HOME are
redirected to a temp directory for every test here, so running the suite never touches the
developer's actual saved API key."""
import json

import pytest

from app.ai_layer import settings_store


@pytest.fixture(autouse=True)
def isolated_settings(tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("FYP_LLM_MODEL", raising=False)
    yield


@pytest.fixture
def client():
    from gui.api import create_app

    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_get_settings_reports_offline_when_nothing_saved(client):
    d = client.get("/api/settings").get_json()
    assert d["configured"] is False and d["source"] == "none" and d["masked_key"] is None
    assert d["provider"] == "anthropic"
    assert str(settings_store.settings_path()) == d["settings_path"]


def test_post_settings_saves_key_and_never_echoes_it_back(client):
    r = client.post("/api/settings", json={"api_key": "sk-ant-abcdefghijklmnop", "model": "claude-opus-5-5"})
    d = r.get_json()
    assert r.status_code == 200 and d["saved"] is True
    assert d["configured"] is True and d["source"] == "settings" and d["model"] == "claude-opus-5-5"
    assert d["masked_key"] == "sk-an...mnop"
    assert "abcdefghijkl" not in json.dumps(d)
    assert d["ai"]["mode"] == "llm"
    # the key really was persisted, outside the request/response cycle
    assert settings_store.get_api_key() == "sk-ant-abcdefghijklmnop"


def test_post_settings_saves_provider(client):
    r = client.post("/api/settings", json={"api_key": "AIza-fake", "provider": "gemini"})
    d = r.get_json()
    assert d["provider"] == "gemini"
    assert settings_store.get_provider() == "gemini"


def test_post_settings_rejects_unknown_provider(client):
    r = client.post("/api/settings", json={"provider": "openai"})
    assert r.status_code == 422


def test_post_settings_clears_key_with_empty_string(client):
    client.post("/api/settings", json={"api_key": "sk-ant-abcdefghijklmnop"})
    r = client.post("/api/settings", json={"api_key": ""})
    d = r.get_json()
    assert d["configured"] is False and d["ai"]["mode"] == "offline"
    assert settings_store.get_api_key() is None


def test_post_settings_rejects_non_string(client):
    r = client.post("/api/settings", json={"api_key": 12345})
    assert r.status_code == 422
    assert "must be a string" in " ".join(r.get_json()["problems"])


def test_post_settings_rejects_non_object_body(client):
    r = client.post("/api/settings", data="not json", content_type="application/json")
    assert r.status_code == 422


def test_test_route_with_no_key_reports_not_configured(client):
    d = client.post("/api/settings/test", json={}).get_json()
    assert d["ok"] is False and "No API key configured" in d["message"]


def test_test_route_never_leaks_the_key_on_failure(client, monkeypatch):
    def boom(self, prompt):
        raise RuntimeError(f"HTTP 401: bad key sk-ant-shouldnotleak was rejected")

    monkeypatch.setattr("app.ai_layer.clients.AnthropicClient.complete", boom)
    d = client.post("/api/settings/test", json={"api_key": "sk-ant-shouldnotleak"}).get_json()
    assert d["ok"] is False
    assert "sk-ant-shouldnotleak" not in d["message"] and "<key>" in d["message"]


def test_test_route_uses_the_unsaved_key_without_saving_it(client, monkeypatch):
    calls = []

    def ok(self, prompt):
        calls.append((self.api_key, self.model_id, prompt))
        return "OK"

    monkeypatch.setattr("app.ai_layer.clients.AnthropicClient.complete", ok)
    d = client.post("/api/settings/test", json={"api_key": "sk-ant-tryme", "model": "claude-opus-5-5"}).get_json()
    assert d["ok"] is True and "OK" in d["message"] and d["model_id"] == "claude-opus-5-5"
    assert calls == [("sk-ant-tryme", "claude-opus-5-5", "Reply with exactly one word: OK")]
    assert settings_store.get_api_key() is None          # testing must not silently save


def test_test_route_uses_gemini_client_when_provider_is_gemini(client, monkeypatch):
    calls = []

    def ok(self, prompt):
        calls.append((self.api_key, self.model_id, prompt))
        return "OK"

    monkeypatch.setattr("app.ai_layer.clients.GeminiClient.complete", ok)
    d = client.post("/api/settings/test", json={"api_key": "AIza-tryme", "provider": "gemini"}).get_json()
    assert d["ok"] is True
    from app.ai_layer.clients import DEFAULT_MODEL

    assert calls == [("AIza-tryme", DEFAULT_MODEL["gemini"], "Reply with exactly one word: OK")]


def test_health_reflects_saved_settings(client):
    client.post("/api/settings", json={"api_key": "sk-ant-abcdefghijklmnop"})
    h = client.get("/api/health").get_json()
    assert h["ai"]["mode"] == "llm" and "guarded LLM" in h["ai"]["label"] or "sk-ant" not in json.dumps(h)
    assert "sk-ant-abcdefghijklmnop" not in json.dumps(h)
