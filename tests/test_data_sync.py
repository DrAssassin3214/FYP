"""Online-first data with a local fallback (app.data_sync).  No real network: a fake fetcher stands in for it."""
import hashlib
import json

import pytest

from app import data_sync as ds
from app import service


def _pack(version="2026-10-12.1", rules_extra=None):
    lib = json.loads((ds.BUNDLED_DIR / "risk_library_masonry.json").read_text(encoding="utf-8-sig"))
    lib = [dict(r) for r in lib]
    lib.append({"id": "R-TESTONLINE", "name": "Online-only test risk", "category": "Test", "description": "x"})
    files = {"risk_library_masonry.json": json.dumps(lib).encode()}
    man = {"schema": 1, "version": version,
           "files": {n: {"sha256": hashlib.sha256(b).hexdigest(), "bytes": len(b)} for n, b in files.items()}}
    store = {"https://x.test/p/manifest.json": json.dumps(man).encode()}
    store.update({"https://x.test/p/" + n: b for n, b in files.items()})
    return store, man


def fetcher(store):
    def get(url):
        if url not in store:
            raise ds.FetchError("HTTP 404")
        return store[url]
    return get


def offline(url):
    raise ds.FetchError("Network is unreachable")


URL = "https://x.test/p/manifest.json"


def test_offline_uses_bundled_data():
    res = ds.refresh(URL, fetch=offline)
    assert res["ok"] is False and res["online"] is False and "using the data on this computer" in res["message"]
    assert ds.status()["mode"] == "bundled"
    assert all(r["id"] != "R-TESTONLINE" for r in service.risk_library())
    assert len(service.risk_library()) == 46


def test_online_pack_is_installed_and_used():
    store, _ = _pack()
    res = ds.refresh(URL, fetch=fetcher(store))
    assert res["ok"] and res["updated"] and res["version"] == "2026-10-12.1"
    assert any(r["id"] == "R-TESTONLINE" for r in service.risk_library())
    st = ds.status()
    assert st["mode"] == "online pack" and st["files"]["risk_library_masonry.json"] == "online pack"
    assert st["files"]["rules_masonry.json"] == "bundled"          # not in this pack: still local
    assert ds.provenance()["data_version"] == "2026-10-12.1"


def test_goes_offline_after_install_keeps_last_online_pack():
    store, _ = _pack()
    ds.refresh(URL, fetch=fetcher(store))
    res = ds.refresh(URL, fetch=offline)
    assert res["ok"] is False
    assert any(r["id"] == "R-TESTONLINE" for r in service.risk_library())      # still the downloaded copy


def test_reset_returns_to_bundled():
    store, _ = _pack()
    ds.refresh(URL, fetch=fetcher(store))
    assert ds.reset()["mode"] == "bundled"
    assert len(service.risk_library()) == 46


def test_same_or_older_version_is_not_reinstalled():
    store, _ = _pack("2026-10-12.2")
    assert ds.refresh(URL, fetch=fetcher(store))["updated"] is True
    store2, _ = _pack("2026-10-12.1")
    r = ds.refresh(URL, fetch=fetcher(store2))
    assert r["updated"] is False and ds.status()["version"] == "2026-10-12.2"


def test_bad_checksum_is_rejected():
    store, man = _pack()
    store["https://x.test/p/risk_library_masonry.json"] += b" "
    r = ds.refresh(URL, fetch=fetcher(store))
    assert r["ok"] is False and "checksum" in r["message"] and ds.status()["mode"] == "bundled"


@pytest.mark.parametrize("bad", [b"[]", b'[{"id":"A"}]', b"not json"])
def test_bad_structure_is_rejected(bad):
    man = {"schema": 1, "version": "9", "files": {"risk_library_masonry.json": {"sha256": hashlib.sha256(bad).hexdigest()}}}
    store = {URL: json.dumps(man).encode(), "https://x.test/p/risk_library_masonry.json": bad}
    r = ds.refresh(URL, fetch=fetcher(store))
    assert r["ok"] is False and ds.status()["mode"] == "bundled"


def test_catalogue_with_numbers_is_rejected():
    bad = json.dumps({"entries": [{"catalogue_id": "C1", "cost": 5}]}).encode()
    man = {"schema": 1, "version": "9", "files": {"mitigation_catalogue.json": {"sha256": hashlib.sha256(bad).hexdigest()}}}
    store = {URL: json.dumps(man).encode(), "https://x.test/p/mitigation_catalogue.json": bad}
    assert "must not carry" in ds.refresh(URL, fetch=fetcher(store))["message"]


def test_unknown_file_and_http_are_refused():
    assert ds.validate_file("evil.json", {}) is not None
    with pytest.raises(ds.FetchError):
        ds._http_get("http://x.test/manifest.json")


def test_tampered_installed_file_falls_back_to_bundled():
    store, _ = _pack()
    ds.refresh(URL, fetch=fetcher(store))
    (ds.pack_dir() / "risk_library_masonry.json").write_text("[]", encoding="utf-8")
    assert len(service.risk_library()) == 46 and ds.status()["mode"] == "bundled"


def test_empty_url_turns_updates_off():
    assert ds.refresh("", fetch=offline)["updated"] is False


def test_bundled_files_pass_their_own_checks():
    for n in ds.PACK_FILES:
        assert ds.validate_file(n, json.loads((ds.BUNDLED_DIR / n).read_text(encoding="utf-8-sig"))) is None


def test_search_results_are_saved_and_used_offline(monkeypatch):
    from app import online_search as osr
    monkeypatch.setattr(osr, "_get_json", lambda url: {"results": [{"title": "Paper A", "doi": "10.1/a", "publication_year": 2020}]
                                                      if "openalex" in url else {"message": {"items": []}}})
    first = osr.search_literature("brick wall delay")
    assert first["ok"] and not first["from_cache"]

    def down(url):
        raise osr.OfflineError("no network")
    monkeypatch.setattr(osr, "_get_json", down)
    again = osr.search_literature("brick wall delay")
    assert again["ok"] and again["from_cache"] and again["results"][0]["title"] == "Paper A"
    assert osr.search_literature("never searched")["ok"] is False


def test_offline_option_search_still_lists_local_catalogue(monkeypatch):
    from app import online_search as osr
    monkeypatch.setattr(osr, "_get_json", lambda url: (_ for _ in ()).throw(osr.OfflineError("down")))
    out = osr.find_options_online([{"id": "R-MAT", "name": "Material shortage"}], service.mitigation_catalogue())
    assert out["ok"] is False and out["offline"] is True and out["risks"][0]["catalogue_options"]


def test_gui_routes(monkeypatch):
    from gui.api import create_app
    c = create_app().test_client()
    assert c.get("/api/data-status").get_json()["mode"] == "bundled"
    assert c.get("/api/health").get_json()["data"]["mode"] == "bundled"
    r = c.post("/api/data-update", json={}).get_json()          # URL is "" in tests: no network, no change
    assert r["updated"] is False and r["status"]["mode"] == "bundled"
    assert c.post("/api/data-reset", json={}).get_json()["ok"] is True
