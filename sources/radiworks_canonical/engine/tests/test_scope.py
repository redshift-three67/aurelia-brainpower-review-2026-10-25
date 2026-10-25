"""Tests für die strikt lokale Single-Operator-Scope-Grenze."""

from pathlib import Path

import pytest

from radiworks.scope import ScopeContext, ScopeError, ScopeMode, ScopeResolver


def test_local_scope_rejects_untrusted_browser_scope_headers(monkeypatch):
    monkeypatch.delenv("RADIOWORKS_SCOPE_MODE", raising=False)
    resolver = ScopeResolver.from_environment()

    with pytest.raises(ScopeError, match="nicht zulässig"):
        resolver.resolve({"X-Aurelia-Tenant-Id": "spoofed-tenant"})

    assert resolver.mode is ScopeMode.LOCAL
    assert resolver.resolve({}) == ScopeContext("local", "preview", "default")


def test_enforced_scope_mode_is_rejected_until_a_scoped_authority_exists(monkeypatch):
    monkeypatch.setenv("RADIOWORKS_SCOPE_MODE", "enforced")

    with pytest.raises(ScopeError, match="nur local"):
        ScopeResolver.from_environment()


@pytest.mark.parametrize("value", ["", " space", "slash/value", "x" * 129])
def test_scope_context_rejects_unsafe_identifiers(value):
    with pytest.raises(ScopeError):
        ScopeContext(value, "client", "job")


def test_invalid_scope_mode_fails_closed(monkeypatch):
    monkeypatch.setenv("RADIOWORKS_SCOPE_MODE", "passthrough")

    with pytest.raises(ScopeError, match="RADIOWORKS_SCOPE_MODE"):
        ScopeResolver.from_environment()


def test_productive_views_do_not_bypass_the_configured_api_client():
    webapp = Path(__file__).parents[2] / "webapp" / "js"

    assert "fetch(" not in (webapp / "views" / "peggotty.js").read_text(encoding="utf-8")
    assert "fetch(" not in (webapp / "views" / "statusbar.js").read_text(encoding="utf-8")
    client = (webapp / "api.js").read_text(encoding="utf-8")
    assert "script: (name)" in client
    assert "entropyFeed:" in client



def test_local_scope_switch_does_not_expose_other_scope_case_history_or_drafts(
    tmp_path, monkeypatch,
):
    from fastapi.testclient import TestClient

    from radiworks.main import create_app

    data = tmp_path / "data"
    data.mkdir()
    (data / "HOMEOPATHY_Test.txt").write_text("Synthetic A\nSynthetic B\n", encoding="utf-8")
    monkeypatch.setenv("RADIOWORKS_LOCAL_TENANT_ID", "tenant-a")
    first = create_app(base_dir=tmp_path / "runtime", data_dir=data, materia_dir=tmp_path / "empty")
    with TestClient(first) as client:
        assert client.post("/cases", json={"name": "Case A"}).status_code == 200
        assert client.post("/cases/CaseA/activate").status_code == 200
        analysis = client.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 42})
        assert analysis.status_code == 200
        draft_id = analysis.json()["draft"]["id"]
        assert client.get("/cases/recent").json()["recent"] == ["CaseA"]

    monkeypatch.setenv("RADIOWORKS_LOCAL_TENANT_ID", "tenant-b")
    second = create_app(base_dir=tmp_path / "runtime", data_dir=data, materia_dir=tmp_path / "empty")
    with TestClient(second) as client:
        assert client.get("/cases").json()["cases"] == []
        assert client.get("/cases/recent").json()["recent"] == []
        assert client.get("/cases/CaseA").status_code == 404
        assert client.get("/drafts").json()["drafts"] == []
        assert client.get(f"/drafts/{draft_id}").status_code == 404
        assert client.post("/cases/CaseA/activate").status_code == 404
        assert client.post(
            f"/drafts/{draft_id}/transition", json={"status": "ready"},
        ).status_code == 409
        assert client.post(f"/drafts/{draft_id}/promote").status_code == 409
        assert client.get("/analysis/current").json()["result"] is None
        assert client.get("/broadcast/queue").json()["queued"] == []
        spoofed = client.post(
            "/broadcast",
            json={"signature": "Synthetic A"},
            headers={"X-Aurelia-Tenant-Id": "tenant-a"},
        )
        assert spoofed.status_code == 400
        assert client.get("/broadcast/queue").json()["queued"] == []



def test_local_websocket_rejects_untrusted_aurelia_scope_header(tmp_path):
    from fastapi import WebSocketDisconnect
    from fastapi.testclient import TestClient

    from radiworks.main import create_app

    app = create_app(base_dir=tmp_path / "runtime", materia_dir=tmp_path / "empty")
    with TestClient(app) as client:
        with pytest.raises(WebSocketDisconnect) as rejected:
            with client.websocket_connect(
                "/ws", headers={"X-Aurelia-Tenant-Id": "tenant-b"},
            ) as websocket:
                websocket.receive_json()
        assert rejected.value.code == 1008
def test_local_http_rejects_untrusted_host_and_origin(tmp_path):
    from fastapi.testclient import TestClient
    from radiworks.main import create_app

    app = create_app(base_dir=tmp_path / "runtime", materia_dir=tmp_path / "empty")
    with TestClient(app) as client:
        for host in ("attacker.example", "127.0.0.1.attacker.example", "bad@localhost", "localhost:bad"):
            assert client.get("/manifest", headers={"Host": host}).status_code == 400
        for origin in ("https://attacker.example", "null", "http://localhost.attacker.example"):
            assert client.get("/manifest", headers={"Origin": origin}).status_code == 400
        assert client.get(
            "/manifest", headers={"Host": "127.0.0.1:8101", "Origin": "http://localhost:8080"}
        ).status_code == 200


def test_local_websocket_rejects_untrusted_host_and_origin(tmp_path):
    from fastapi import WebSocketDisconnect
    from fastapi.testclient import TestClient
    from radiworks.main import create_app

    app = create_app(base_dir=tmp_path / "runtime", materia_dir=tmp_path / "empty")
    with TestClient(app) as client:
        for headers in (
            {"Host": "attacker.example"},
            {"Origin": "https://attacker.example"},
            {"Origin": "null"},
        ):
            with pytest.raises(WebSocketDisconnect) as rejected:
                with client.websocket_connect("/ws", headers=headers) as websocket:
                    websocket.receive_json()
            assert rejected.value.code == 1008
        with client.websocket_connect(
            "/ws", headers={"Host": "127.0.0.1:8101", "Origin": "http://127.0.0.1:8101"}
        ) as websocket:
            assert websocket.receive_json()["type"] == "server.hello"
