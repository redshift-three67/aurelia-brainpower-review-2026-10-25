"""API-Tests P3-Teil 3 (GV-Runde, Essential, Settings, Stick-Pad)."""

from fastapi.testclient import TestClient


def _run_analysis(home: TestClient, seed: int = 5):
    return home.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": seed}).json()


def test_gv_round_flow(home: TestClient):
    _run_analysis(home)
    first = home.post("/analysis/gv-round", json={"seed": 1}).json()
    assert first["counter"] == 1 and first["rateIndex"] is None
    second = home.post("/analysis/gv-round", json={"seed": 2}).json()
    assert second["counter"] == 2 and second["rateIndex"] == 0
    assert second["result"]["rateObjects"][0]["gv"] == second["gv"]

    state = home.get("/analysis/gv-round").json()
    assert state["active"] and state["totalRuns"] == 2

    reset = home.post("/analysis/gv-round/reset").json()
    assert reset["state"]["counter"] == 0  # Reset meldet den Zustand nach dem Zurücksetzen
    assert all(r["gv"] == 0 for r in reset["result"]["rateObjects"])


def test_gv_round_without_analysis_409(home: TestClient):
    assert home.post("/analysis/gv-round", json={"seed": 1}).status_code == 409


def test_gv_round_deterministic(home: TestClient):
    _run_analysis(home, seed=9)
    a = home.post("/analysis/gv-round", json={"seed": 21}).json()
    _run_analysis(home, seed=9)
    b = home.post("/analysis/gv-round", json={"seed": 21}).json()
    assert a["gv"] == b["gv"] and a["generalVitality"] == b["generalVitality"]


def test_essential_questions_endpoint(home: TestClient):
    data = home.post("/essential-questions", json={"seed": 3}).json()
    assert "ESSENZIELLE FRAGEN" in data["report"]


def test_settings_roundtrip(home: TestClient):
    original = home.get("/settings").json()
    updated = home.put(
        "/settings",
        json={"booleans": {"broadcast.legacyMixMode": True}, "strings": {"entropy.defaultMode": "stochastic"}},
    ).json()
    assert updated["booleans"]["broadcast.legacyMixMode"] is True
    assert updated["strings"]["entropy.defaultMode"] == "stochastic"
    # Wirkung sichtbar
    assert home.get("/entropy/status").json()["defaultMode"] == "stochastic"
    # Typfehler abgelehnt
    assert home.put("/settings", json={"booleans": {"x": "ja"}}).status_code == 422
    # Original-Zustand wiederherstellen für weitere Tests
    home.put(
        "/settings",
        json={
            "booleans": {"broadcast.legacyMixMode": original["booleans"].get("broadcast.legacyMixMode", False)},
            "strings": {"entropy.defaultMode": original["strings"].get("entropy.defaultMode", "seeded")},
        },
    )


def test_stickpad_flow(home: TestClient):
    for index, (x, y) in enumerate(((640, 400), (120, 80), (300, 250)), start=1):
        assert home.post("/stickpad/position", json={"x": x, "y": y}).json()["positions"] == index
    result = home.post("/stickpad/analyze", json={"database": "HOMEOPATHY_Test"}).json()
    assert result["rateObjects"], "Stick-Pad-Analyse muss Raten liefern"
    # Positionen verbraucht -> erneute Analyse lehnt ab
    assert home.post("/stickpad/analyze", json={"database": "HOMEOPATHY_Test"}).status_code == 409
