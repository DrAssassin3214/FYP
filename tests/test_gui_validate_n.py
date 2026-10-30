"""/api/validate applies the same simulation n / seed limits as /api/analyze, only when a simulation block exists."""
import pytest

from app import service


@pytest.fixture(scope="module")
def client():
    from gui.api import create_app

    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def _case(sim):
    c = service.example_case()
    if sim is None:
        c.pop("simulation", None)
    else:
        c["simulation"] = sim
    return c


@pytest.mark.parametrize("sim", [
    {"n": 1e9}, {"n": 0}, {"n": "x"}, {"n": 200001}, {"n": 1.5}, {"seed": -1}, {"seed": "x"}, "oops",
])
def test_bad_simulation_settings_are_rejected(client, sim):
    r = client.post("/api/validate", json=_case(sim))
    d = r.get_json()
    assert r.status_code == 200 and d["ok"] is False
    assert any(p.startswith("simulation") for p in d["problems"])


@pytest.mark.parametrize("sim", [{"n": 1}, {"n": 200000, "seed": 0}, {"n": 10000, "seed": 12345}, {}])
def test_valid_simulation_settings_unchanged(client, sim):
    d = client.post("/api/validate", json=_case(sim)).get_json()
    assert d["ok"] is True and "problems" not in d


def test_register_only_case_unchanged(client):
    base = _case(None)
    assert "simulation" not in base
    d = client.post("/api/validate", json=base).get_json()
    assert d["ok"] is True
