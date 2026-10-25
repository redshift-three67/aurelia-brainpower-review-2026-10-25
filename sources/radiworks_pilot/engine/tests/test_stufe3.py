"""Tests Stufe-3-Vollendung: Statistik, Bilder, Skript, Webcam-Feed."""

from fastapi.testclient import TestClient

from radiworks.api.routes import STATE


def test_case_statistics(home: TestClient):
    # Zwei Analysen in denselben Fall schreiben (attach_analysis nutzt current)
    home.post("/cases", json={"name": "StatFall", "description": "synthetisch"})
    home.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 1})
    home.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 2})
    stats = home.get("/cases/StatFall/statistics").json()
    assert stats["sessions"] >= 1
    assert stats["topList"], "Top-Liste muss Einträge haben"
    first = stats["topList"][0]
    for field in ("name", "occurrence", "overallGV", "overallEnergeticValue"):
        assert field in first
    # Sortierung: occurrence absteigend
    occurrences = [entry["occurrence"] for entry in stats["topList"]]
    assert occurrences == sorted(occurrences, reverse=True)
    # GET-Statistik bleibt beobachtungsrein und persistiert keine abgeleitete Top-Liste.
    saved = home.get("/cases/StatFall").json()
    assert saved.get("topTenList") == []


def test_images_analyze_deterministic(home: TestClient):
    body = {"count": 3, "seed": 9}
    a = home.post("/images/analyze", json=body).json()
    b = home.post("/images/analyze", json=body).json()
    assert a == b
    assert len(a["layers"]) == 3
    assert a["max"] >= 162  # Abbruchschwelle des Originals
    for layer in a["layers"]:
        assert 0 <= layer["gv"] <= 768  # 256 Züge × max 3 Punkte


def test_images_analyze_validates_count(home: TestClient):
    assert home.post("/images/analyze", json={"count": 0}).status_code == 422
    assert home.post("/images/analyze", json={"count": 99}).status_code == 422


def test_images_broadcast(home: TestClient):
    queued = home.post(
        "/images/broadcast", json={"md5": "d41d8cd98f00b204e9800998ecf8427e", "seconds": 30}
    ).json()
    assert queued["signature"].startswith("IMAGE:")
    home.delete("/broadcast/all")


def test_script_execute_inline(home: TestClient):
    script = "## Test\nx = ANALYZE HOMEOPATHY_Test\nPRINT x\nPRINT Ende."
    result = home.post("/script/execute", json={"script": script, "seed": 4}).json()
    assert any("Analyzing HOMEOPATHY_Test" in line for line in result["output"])
    assert any(line.startswith("AnalysisResult") for line in result["output"])
    assert "Ende." in result["output"]
    assert result["errors"] == []


def test_script_execute_unknown_line(home: TestClient):
    result = home.post("/script/execute", json={"script": "BLAFASEL\n"}).json()
    assert any(line.startswith("NON INTERPRETED LINE") for line in result["errors"])


def test_script_execute_named(home: TestClient):
    result = home.post("/script/execute", json={"name": "beispiel", "seed": 5}).json()
    assert any("Analyzing HOMEOPATHY" in line for line in result["output"])


def test_script_duplicate_label_rejected_before_execution(home: TestClient):
    response = home.post("/script/execute", json={
        "script": "start:\nPRINT first\n start :\nPRINT second",
        "seed": 5,
    })
    assert response.status_code == 422
    assert "start" in response.json()["error"]["message"]


def test_script_distinct_labels_keep_existing_execution(home: TestClient):
    response = home.post("/script/execute", json={
        "script": "first:\nPRINT one\nsecond:\nPRINT two",
        "seed": 5,
    })
    assert response.status_code == 200
    assert response.json()["output"] == ["one", "two"]


def test_entropy_feed_prioritized(home: TestClient):
    state = STATE.state
    assert state is not None
    state.random_org._http_get = None  # Tests duerfen keinen externen Egress ausloesen.
    status_before = home.get("/entropy/feed").json()
    accepted = home.post(
        "/entropy/acquire", json={"integerList": [123456, 234567, 42, 999999]}
    ).json()
    # 42 wird verworfen (Original: seed < 100)
    assert accepted["acquired"] == 3
    assert accepted["feedSize"] == status_before["feedSize"] + 3

    # Stochastischer Lauf konsumiert den Feed zuerst
    run = home.post(
        "/analysis", json={"database": "HOMEOPATHY_Test", "mode": "stochastic", "seed": None}
    ).json()
    assert run["passport"]["entropy_mode"] == "stochastic"
    assert home.get("/entropy/feed").json()["feedSize"] < accepted["feedSize"]
