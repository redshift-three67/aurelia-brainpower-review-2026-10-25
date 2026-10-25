"""Tests der Sprint-Fixes: fortlaufender GV-Strom, Live-Provider, CLARKE."""

from fastapi.testclient import TestClient


def test_gv_round_advances_without_seed(home: TestClient):
    """Fix b): GV-Züge ohne Seed müssen variieren (Strom wird fortgesetzt)."""
    home.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 77})
    values = [home.post("/analysis/gv-round", json={}).json()["gv"] for _ in range(6)]
    assert len(set(values)) > 1, "GV-Züge wiederholen sich — Strom wird neu gestartet"


def test_gv_round_with_explicit_seed_is_stable(home: TestClient):
    home.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 77})
    a = home.post("/analysis/gv-round", json={"seed": 5}).json()["gv"]
    home.post("/analysis/gv-round/reset")
    b = home.post("/analysis/gv-round", json={"seed": 5}).json()["gv"]
    assert a == b


def test_gv_standalone_advances_without_seed(home: TestClient):
    values = [home.post("/gv", json={}).json()["gv"] for _ in range(6)]
    assert len(set(values)) > 1, "Ad-hoc-GV wiederholt sich — Live-Provider fehlt"


def test_clarke_compare(home: TestClient):
    home.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 3})
    data = home.post("/materia/clarke-compare", json={"rate": "Abrotanum"}).json()
    assert data["rate"] == "Abrotanum"
    assert isinstance(data["clinical"], list)
    # Abrotanum ist im Testkorpus als Remedie geladen — klinische Symptome
    # kommen aus dem echten Clarke-Korpus oder dem Testbestand
    assert "sharedCounts" in data and "others" in data


def test_promote_uses_multiplier_from_client(home: TestClient):
    run = home.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 42}).json()
    draft_id = run["draft"]["id"]
    home.post(f"/drafts/{draft_id}/transition", json={"status": "ready"})
    promoted = home.post(f"/drafts/{draft_id}/promote", json={"multiplier": 9, "max_rates": 2}).json()
    for entry in promoted["broadcastEntries"]:
        assert entry["multiplier"] == 9
    home.delete("/broadcast/all")


def test_training_flow(home: TestClient):
    started = home.post("/training/start", json={"database": "HOMEOPATHY_Test", "seed": 8}).json()
    assert started == {"active": True, "covered": True}
    uncovered = home.post("/training/uncover").json()
    assert uncovered["covered"] is False and uncovered["signature"]
    assert home.get("/training").json()["active"] is True
    assert home.delete("/training").json() == {"active": False}
