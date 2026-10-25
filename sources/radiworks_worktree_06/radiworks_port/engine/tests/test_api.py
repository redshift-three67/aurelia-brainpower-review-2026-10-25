"""Tests: API_CONTRACT v1 (REST + WebSocket)."""

from fastapi.testclient import TestClient


def test_ping(home: TestClient):
    data = home.get("/ping").json()
    assert data["result"] == "pong"
    assert data["module"] == "radiworks.engine"
    assert data["version"]


def test_manifest_is_kernel_abi_v1(home: TestClient):
    m = home.get("/manifest").json()
    for field in ("id", "version", "hash", "input_schema", "output_schema", "class", "repro", "budget", "entry", "copy"):
        assert field in m, field
    assert m["class"] == "cpu"
    assert m["repro"] == "seeded"
    assert m["hash"].startswith("sha256:")
    assert m["isHardwareActivatable"] is False


def test_entropy_status(home: TestClient):
    data = home.get("/entropy/status").json()
    assert data["defaultMode"] == "seeded"
    assert "stochastic" in data["modes"]


def test_databases_and_alias(home: TestClient):
    assert "HOMEOPATHY_Test" in home.get("/databases").json()["databases"]
    assert home.get("/rates").json() == home.get("/databases").json()


def test_analysis_seeded_is_replayable(home: TestClient):
    body = {"database": "HOMEOPATHY_Test", "seed": 1234}
    first = home.post("/analysis", json=body).json()
    second = home.post("/analysis", json=body).json()
    assert first["result"] == second["result"]
    assert first["passport"]["seed"] == second["passport"]["seed"]
    # Passport-Pflichtfelder (docs/04-compute.md)
    for field in ("run_id", "kernel", "kernel_hash", "input_hash", "seed", "dauer_ms"):
        assert field in first["passport"]
    # Draft wurde erzeugt (D18)
    assert first["draft"]["status"] == "draft"
    # Ergebnislimit 105 und GV vorhanden
    assert len(first["result"]["rateObjects"]) <= 105
    assert first["result"]["generalVitality"] is not None


def test_analysis_unknown_database_404(home: TestClient):
    assert home.post("/analysis", json={"database": "NIX"}).status_code == 404


def test_gv_and_anomaly(home: TestClient):
    gv = home.post("/gv", json={"seed": 5}).json()
    assert 0 <= gv["gv"] < 1500
    anomaly = home.post("/search-anomaly", json={"width": 4, "height": 3, "seed": 5}).json()
    assert len(anomaly["values"]) == 12


def test_case_flow(home: TestClient):
    saved = home.post(
        "/cases", json={"name": "Test Fall", "description": "synthetisch"}
    ).json()
    assert saved["name"] == "Test Fall"
    names = home.get("/cases").json()["cases"]
    assert "TestFall" in names
    loaded = home.get("/cases/TestFall").json()
    assert loaded["description"] == "synthetisch"
    current = home.get("/cases/current").json()
    assert current["name"] == "Test Fall"


def test_draft_promote_queues_broadcast(home: TestClient):
    run = home.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 42}).json()
    draft_id = run["draft"]["id"]
    # Draft -> ready -> promote (D18-Pflichtweg)
    home.post(f"/drafts/{draft_id}/transition", json={"status": "ready"})
    promoted = home.post(f"/drafts/{draft_id}/promote", json={}).json()
    assert promoted["status"] == "promoted"
    queue = home.get("/broadcast/queue").json()
    assert queue["queued"] or queue["active"]
    # Direkt-Promote aus draft waere abgelehnt worden:
    run2 = home.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 43}).json()
    direct = home.post(f"/drafts/{run2['draft']['id']}/promote", json={})
    assert direct.status_code == 409


def test_broadcast_direct_and_stop(home: TestClient):
    queued = home.post(
        "/broadcast", json={"signature": "MANUELL 55 C 30", "seconds": 2, "multiplier": 3}
    ).json()
    assert queued["signature"] == "MANUELL 55 C 30"
    assert home.delete("/broadcast/all").json() == {"stopped": "all"}


def test_materia_search(home: TestClient):
    result = home.get("/materiaMedicaSearch", params={"query": "Haarausfall"}).json()
    assert result["searchResults"], "Abrotanum sollte 'Haarausfall' treffen"
    top = result["searchResults"][0]
    assert "Abrotanum" in top["remedyName"]
    assert "<b>" in top["clinical"][0] or top["clinical"]


def test_materia_search_short_query_empty(home: TestClient):
    assert home.get("/materiaMedicaSearch", params={"query": "Ha"}).json()["searchResults"] == []


def test_websocket_channel(home: TestClient):
    with home.websocket_connect("/ws") as ws:
        home.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 8})
        message = ws.receive_json()
    assert message["v"] == 1
    assert message["type"] in {"analysis.update", "analysis.progress"}
    assert "id" in message and "ts" in message


def test_static_webapp_mounted(home: TestClient):
    response = home.get("/index.html")
    assert response.status_code == 200
    assert "RadiWorks" in response.text
