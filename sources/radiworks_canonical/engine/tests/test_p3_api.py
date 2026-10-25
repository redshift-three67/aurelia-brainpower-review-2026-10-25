"""API-Tests P3-Teil 3 (GV-Runde, Essential, Settings, Stick-Pad)."""

import time
from concurrent.futures import ThreadPoolExecutor
from threading import Event

from fastapi.testclient import TestClient

from radiworks.main import create_app


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


def test_bound_gv_steps_reject_stale_draft_and_counter(home: TestClient):
    run = _run_analysis(home)
    draft_id = run["draft"]["id"]
    state = home.get("/analysis/gv-round").json()
    assert state["draftId"] == draft_id
    assert state["counter"] == 0
    assert home.post("/analysis/gv-round", json={
        "expected_draft_id": "stale", "expected_counter": 0,
    }).status_code == 409
    assert home.get("/analysis/gv-round").json()["counter"] == 0
    first = home.post("/analysis/gv-round", json={
        "expected_draft_id": draft_id, "expected_counter": 0,
    })
    assert first.status_code == 200 and first.json()["counter"] == 1
    assert home.post("/analysis/gv-round", json={
        "expected_draft_id": draft_id, "expected_counter": 0,
    }).status_code == 409
    assert home.get("/analysis/gv-round").json()["counter"] == 1
    _run_analysis(home, seed=6)
    assert home.post("/analysis/gv-round", json={
        "expected_draft_id": draft_id, "expected_counter": 0,
    }).status_code == 409


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


def test_stickpad_analysis_links_own_passport_draft_session_and_gv(home: TestClient):
    assert home.post("/cases", json={"name": "Stick Analysis Synthetic", "focus": "Pflanzen"}).status_code == 200
    assert home.post("/stickpad/position", json={"x": 640, "y": 400}).status_code == 200
    response = home.post("/stickpad/analyze", json={"database": "HOMEOPATHY_Test"})
    assert response.status_code == 200
    data = response.json()
    assert data["sessionLinked"] is True
    assert data["passport"]["input_hash_scheme"] == "stickpad-position-catalog-v1"
    assert data["passport"]["modus"] == "stickpad-analyse"
    assert data["passport"]["replayable"] is False
    assert data["passport"]["seed_scheme"] == "stickpad-gv-continuation-v1"
    assert data["passport"]["sources"]["analysis"] == "stickpad-positions"
    receipt = data["stickPadCapture"]
    assert receipt["runId"] == data["passport"]["run_id"]
    case = home.get("/cases/current").json()
    session = case["sessionList"][-1]
    assert session["stickPadReceiptId"] == receipt["id"]
    assert session["stickPadCapture"] == receipt
    assert session["passport"]["run_id"] == data["passport"]["run_id"]
    assert session["analysisResult"] == data["result"]
    assert data["draft"]["sessionId"] == session["sessionId"]
    draft = home.get(f"/drafts/{data['draft']['id']}").json()
    assert draft["sessionId"] == session["sessionId"]
    assert draft["source_run_id"] == data["passport"]["run_id"]
    assert draft["focus"]["case_focus"] == "Pflanzen"
    assert home.get("/stickpad").json()["positions"] == []

    assert home.post("/stickpad/position", json={"x": 120, "y": 80}).status_code == 200
    gv = home.post("/stickpad/gv")
    assert gv.status_code == 200
    assert gv.json()["coupled"] is True
    assert gv.json()["sessionId"] == session["sessionId"]
    assert gv.json()["counter"] == 1
    restored = home.post("/analysis/sessions/0/view")
    assert restored.status_code == 200
    assert restored.json()["state"]["counter"] == 1


def test_stickpad_hits_can_be_reanalysed_as_separate_bound_session(home: TestClient):
    assert home.get("/ping").json()["supportsStickPadFollowup"] is True
    assert home.post("/cases", json={"name": "Synthetic Followup", "focus": "Pflanzen"}).status_code == 200
    for x, y in ((640, 400), (120, 80), (300, 250)):
        assert home.post("/stickpad/position", json={"x": x, "y": y}).status_code == 200
    first = home.post("/stickpad/analyze", json={"database": "HOMEOPATHY_Test"}).json()
    source = home.get("/cases/current").json()["sessionList"][-1]
    source_id = source["sessionId"]
    source_baseline = source["analysisBaseline"]
    assert source_baseline["rateObjects"]
    assert first["draft"]["focus"]["case_focus"] == "Pflanzen"

    # A later ordinary database analysis must not become the follow-up input.
    assert home.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 4}).status_code == 200
    reference = home.get("/cases/current/ref").json()["ref"]
    assert home.post("/cases/current/metadata", json={
        "focus": "Mineralien", "expected_case_ref": reference,
    }).status_code == 200
    second = home.post("/analysis/stickpad-followup", json={
        "source_session_id": source_id, "seed": 17, "mode": "seeded",
    })
    assert second.status_code == 200
    data = second.json()
    assert data["passport"]["modus"] == "stickpad-folgeanalyse"
    assert data["passport"]["input_hash_scheme"] == "stickpad-followup-v1"
    assert data["draft"]["focus"]["case_focus"] == "Mineralien"
    assert home.get(f"/drafts/{first['draft']['id']}").json()["focus"]["case_focus"] == "Pflanzen"
    assert data["sourceSessionId"] == source_id
    assert {r["nameOrRate"] for r in data["result"]["rateObjects"]} <= {
        r["nameOrRate"] for r in source_baseline["rateObjects"]
    }
    current = home.get("/cases/current").json()
    assert current["sessionList"][0] == source
    assert current["sessionList"][-1]["parentSessionId"] == source_id
    assert current["sessionList"][-1]["draftId"] == data["draft"]["id"]
    assert current["sessionList"][-1]["analysisResult"] == data["result"]
    assert home.get("/analysis/gv-round").json()["draftId"] == data["draft"]["id"]


def test_stickpad_followup_rejects_missing_source_without_new_draft(home: TestClient):
    assert home.post("/cases", json={"name": "Synthetic Followup Missing"}).status_code == 200
    before = home.get("/drafts").json()
    response = home.post("/analysis/stickpad-followup", json={
        "source_session_id": "absent", "seed": 17, "mode": "seeded",
    })
    assert response.status_code == 409
    assert home.get("/drafts").json() == before


def test_stickpad_followup_rejects_changed_source_hits(home: TestClient):
    from radiworks.api.routes import STATE

    assert home.post("/cases", json={"name": "Synthetic Followup Integrity"}).status_code == 200
    assert home.post("/stickpad/position", json={"x": 640, "y": 400}).status_code == 200
    source = home.post("/stickpad/analyze", json={"database": "HOMEOPATHY_Test"}).json()
    assert source["sessionId"]
    state = STATE.state
    assert state is not None and state.case_store.current is not None
    state.case_store.current["sessionList"][0]["analysisBaseline"]["rateObjects"][0]["nameOrRate"] = "changed"
    before = home.get("/drafts").json()
    response = home.post("/analysis/stickpad-followup", json={
        "source_session_id": source["sessionId"], "seed": 17, "mode": "seeded",
    })
    assert response.status_code == 409
    assert home.get("/drafts").json() == before


def test_stickpad_analysis_without_case_has_passport_and_draft_but_no_session(home: TestClient):
    assert home.post("/stickpad/position", json={"x": 640, "y": 400}).status_code == 200
    response = home.post("/stickpad/analyze", json={"database": "HOMEOPATHY_Test"})
    assert response.status_code == 200
    data = response.json()
    assert data["sessionLinked"] is False
    assert data["passport"]["input_hash_scheme"] == "stickpad-position-catalog-v1"
    assert data["draft"]["sessionId"] is None
    assert home.get("/analysis/current").json()["draft"]["id"] == data["draft"]["id"]
    assert home.get("/stickpad").json()["lastReceipt"]["runId"] == data["passport"]["run_id"]


def test_failed_stickpad_analysis_keeps_previous_gv_round(home: TestClient, monkeypatch):
    from radiworks.api.routes import STATE
    from radiworks.persistence import RecoveryError

    assert home.post("/cases", json={"name": "Stick Failure Boundary"}).status_code == 200
    assert home.post(
        "/analysis", json={"database": "HOMEOPATHY_Test", "seed": 44},
    ).status_code == 200
    previous = home.get("/cases/current").json()["sessionList"][-1]["sessionId"]
    assert home.post("/stickpad/position", json={"x": 640, "y": 400}).status_code == 200
    state = STATE.state
    assert state is not None

    def reject_before_marker(*args, **kwargs):
        raise RecoveryError("synthetic pre-marker failure")

    with monkeypatch.context() as context:
        context.setattr(state.recovery, "apply", reject_before_marker)
        failed = home.post("/stickpad/analyze", json={"database": "HOMEOPATHY_Test"})
    assert failed.status_code == 409
    assert len(home.get("/stickpad").json()["positions"]) == 1
    assert len(home.get("/cases/current").json()["sessionList"]) == 1

    measured = home.post("/stickpad/gv")
    assert measured.status_code == 200
    assert measured.json()["sessionId"] == previous


def test_stickpad_analysis_serializes_concurrent_gv(home: TestClient, monkeypatch):
    from radiworks.api.routes import STATE

    assert home.post("/cases", json={"name": "Stick Concurrent"}).status_code == 200
    assert home.post("/stickpad/position", json={"x": 640, "y": 400}).status_code == 200
    state = STATE.state
    assert state is not None
    entered = Event()
    release = Event()
    original = state.stick_pad.plan_analysis_with_capture

    def pause_analysis(*args, **kwargs):
        entered.set()
        assert release.wait(5), "synthetic concurrent request timed out"
        return original(*args, **kwargs)

    with monkeypatch.context() as context:
        context.setattr(state.stick_pad, "plan_analysis_with_capture", pause_analysis)
        with ThreadPoolExecutor(max_workers=2) as pool:
            analysis_future = pool.submit(
                home.post, "/stickpad/analyze", json={"database": "HOMEOPATHY_Test"},
            )
            assert entered.wait(3)
            gv_future = pool.submit(home.post, "/analysis/gv-round", json={})
            time.sleep(0.1)
            release.set()
            analysis = analysis_future.result(timeout=5)
            gv = gv_future.result(timeout=5)
    assert analysis.status_code == 200
    assert gv.status_code == 200
    assert gv.json()["sessionId"] == home.get("/cases/current").json()["sessionList"][-1]["sessionId"]


def test_stickpad_gv_updates_active_case_and_rate_round(home: TestClient):
    assert home.post("/cases", json={"name": "Stick GV Synthetic"}).status_code == 200
    analysis = home.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 44})
    assert analysis.status_code == 200
    draft_id = analysis.json()["draft"]["id"]

    assert home.post("/stickpad/position", json={"x": 640, "y": 400}).status_code == 200
    first = home.post("/stickpad/gv")
    assert first.status_code == 200
    first_data = first.json()
    assert first_data["coupled"] is True
    assert first_data["counter"] == 1
    assert first_data["generalVitality"] == first_data["gv"]
    assert first_data["rateIndex"] is None
    assert first_data["positions"] == 0
    assert first_data["stickPadCapture"]["kind"] == "gv"

    assert home.post("/stickpad/position", json={"x": 120, "y": 80}).status_code == 200
    second = home.post("/stickpad/gv")
    assert second.status_code == 200
    second_data = second.json()
    assert second_data["coupled"] is True
    assert second_data["counter"] == 2
    assert second_data["rateIndex"] == 0
    assert second_data["result"]["rateObjects"][0]["gv"] == second_data["gv"]

    case = home.get("/cases/current").json()
    session = case["sessionList"][-1]
    assert [event["kind"] for event in session["gvHistory"]] == ["stickpad-step"] * 2
    assert [event["stickPadReceiptId"] for event in session["gvHistory"]] == [
        first_data["stickPadCapture"]["id"], second_data["stickPadCapture"]["id"],
    ]
    assert session["gvState"]["counter"] == 2
    assert session["revision"] == 2
    assert session["analysisResult"]["rateObjects"][0]["gv"] == second_data["gv"]
    assert home.get(f"/drafts/{draft_id}").status_code == 200


def test_stickpad_analysis_couples_later_gv_only_to_its_new_session(home: TestClient):
    assert home.post("/cases", json={"name": "Stick Analysis Boundary"}).status_code == 200
    previous = home.post(
        "/analysis", json={"database": "HOMEOPATHY_Test", "seed": 44},
    )
    assert previous.status_code == 200
    assert home.post("/stickpad/position", json={"x": 640, "y": 400}).status_code == 200
    new_analysis = home.post(
        "/stickpad/analyze", json={"database": "HOMEOPATHY_Test"},
    )
    assert new_analysis.status_code == 200
    assert new_analysis.json()["sessionLinked"] is True
    assert home.post("/stickpad/position", json={"x": 120, "y": 80}).status_code == 200
    measured = home.post("/stickpad/gv")
    assert measured.status_code == 200
    case = home.get("/cases/current").json()
    previous_session, new_session = case["sessionList"]
    assert previous_session["gvHistory"] == []
    assert previous_session["revision"] == 0
    assert new_session["passport"]["run_id"] == new_analysis.json()["passport"]["run_id"]
    assert new_session["gvHistory"][0]["stickPadReceiptId"] == measured.json()["stickPadCapture"]["id"]
    assert len(home.get("/stickpad").json()["positions"]) == 0


def test_stickpad_gv_requires_loaded_analysis_for_active_case(home: TestClient):
    assert home.post("/cases", json={"name": "GV Needs Analysis"}).status_code == 200
    assert home.post("/stickpad/position", json={"x": 640, "y": 400}).status_code == 200
    assert home.post("/stickpad/gv").status_code == 409
    assert len(home.get("/stickpad").json()["positions"]) == 1
    assert home.get("/cases/current").json()["sessionList"] == []


def test_stickpad_gv_round_boundary_preserves_collected_positions(home: TestClient):
    assert home.post("/cases", json={"name": "Stick Boundary"}).status_code == 200
    assert home.post(
        "/analysis", json={"database": "HOMEOPATHY_Test", "seed": 44},
    ).status_code == 200
    rates = home.get("/cases/current").json()["sessionList"][-1]["analysisResult"]["rateObjects"]
    for _ in range(len(rates) + 1):
        assert home.post("/analysis/gv-round", json={}).status_code == 200
    assert home.post("/stickpad/position", json={"x": 640, "y": 400}).status_code == 200
    boundary = home.post("/stickpad/gv")
    assert boundary.status_code == 200
    assert boundary.json()["roundBoundary"] is True
    assert boundary.json()["gv"] is None
    assert boundary.json()["positions"] == 1
    measured = home.post("/stickpad/gv")
    assert measured.status_code == 200
    assert measured.json()["roundBoundary"] is False
    assert measured.json()["rateIndex"] is None
    assert measured.json()["positions"] == 0


def test_stickpad_original_mode_is_explicit_and_batch_mode_cannot_change(home: TestClient):
    first = home.post("/stickpad/position", json={"x": 640, "y": 400, "mode": "original"})
    assert first.status_code == 200
    position = first.json()["capture"]
    assert position["mode"] == "original"
    assert position["seedX"] == 640 + position["capturedAtMs"]
    assert position["seedY"] == 400 + position["capturedAtMs"]
    assert home.post("/stickpad/position", json={"x": 120, "y": 80}).status_code == 409
    assert home.get("/stickpad").json()["mode"] == "original"
    assert len(home.get("/stickpad").json()["positions"]) == 1
    result = home.post("/stickpad/analyze", json={"database": "HOMEOPATHY_Test"})
    assert result.status_code == 200
    assert result.json()["stickPadCapture"]["positions"][0]["capturedAtMs"] == position["capturedAtMs"]
    assert home.get("/stickpad").json()["positions"] == []
    assert home.post("/stickpad/position", json={"x": 120, "y": 80}).json()["capture"]["mode"] == "reproducible"


def test_stickpad_receipt_tracks_used_catalog_and_detects_drift_after_restart(tmp_path):
    catalog = tmp_path / "data" / "radionics" / "HOMEOPATHY_Synthetic.txt"
    catalog.parent.mkdir(parents=True)
    original = "Synthetic Alpha\nSynthetic Beta\nSynthetic Gamma\n"
    catalog.write_text(original, encoding="utf-8")
    app_args = {"base_dir": tmp_path, "data_dir": catalog.parent, "materia_dir": tmp_path / "empty"}

    with TestClient(create_app(**app_args)) as client:
        assert client.post("/stickpad/position", json={"x": 640, "y": 400}).status_code == 200
        result = client.post("/stickpad/analyze", json={"database": "HOMEOPATHY_Synthetic"})
        assert result.status_code == 200
        binding = result.json()["stickPadCapture"]["catalog"]
        assert binding["scheme"] == "ordered-rates-sha256-v1"
        assert binding["selector"] == "HOMEOPATHY_Synthetic"
        assert binding["rateCount"] == 3
        assert len(binding["digest"]) == 64
        assert client.get("/stickpad").json()["catalogCheck"]["state"] == "current"
        catalog.write_text("Synthetic Alpha\nSynthetic Delta\nSynthetic Gamma\n", encoding="utf-8")
        changed = client.get("/stickpad").json()
        assert changed["catalogCheck"]["state"] == "changed"
        assert changed["lastReceipt"]["catalog"] == binding

    with TestClient(create_app(**app_args)) as restarted:
        restored = restarted.get("/stickpad").json()
        assert restored["catalogCheck"]["state"] == "changed"
        assert restored["lastReceipt"]["catalog"] == binding
        catalog.write_text(original, encoding="utf-8")
        assert restarted.get("/stickpad").json()["catalogCheck"]["state"] == "current"
        catalog.unlink()
        assert restarted.get("/stickpad").json()["catalogCheck"]["state"] == "unavailable"


def test_stickpad_legacy_receipt_is_not_mistaken_for_current_catalog(tmp_path):
    from radiworks.core.analysis import Rate
    from radiworks.core.stickpad import StickPad

    catalog = tmp_path / "data" / "radionics" / "HOMEOPATHY_Synthetic.txt"
    catalog.parent.mkdir(parents=True)
    catalog.write_text("Synthetic Alpha\n", encoding="utf-8")
    pad = StickPad(tmp_path / "stickpad" / "state.json")
    pad.add_position(10, 20)
    pad.analyze([Rate(name="Synthetic Alpha")])
    with TestClient(create_app(
        base_dir=tmp_path, data_dir=catalog.parent, materia_dir=tmp_path / "empty",
    )) as client:
        status = client.get("/stickpad").json()
        assert status["lastReceipt"]["kind"] == "analysis"
        assert status["catalogCheck"]["state"] == "unverified_legacy"


def test_stickpad_freshly_discovers_matching_catalog_files_without_restart(tmp_path):
    data = tmp_path / "data" / "radionics"
    data.mkdir(parents=True)
    (data / "HOMEOPATHY_A.txt").write_text("Synthetic Alpha\n", encoding="utf-8")
    with TestClient(create_app(
        base_dir=tmp_path, data_dir=data, materia_dir=tmp_path / "empty",
    )) as client:
        (data / "HOMEOPATHY_B.txt").write_text("Synthetic Beta\n", encoding="utf-8")
        assert client.post("/stickpad/position", json={"x": 20, "y": 40}).status_code == 200
        analysis = client.post("/stickpad/analyze", json={"database": "HOMEOPATHY_"})
        assert analysis.status_code == 200
        assert analysis.json()["stickPadCapture"]["catalog"]["rateCount"] == 2
        assert client.get("/stickpad").json()["catalogCheck"]["state"] == "current"
        (data / "HOMEOPATHY_C.txt").write_text("Synthetic Gamma\n", encoding="utf-8")
        assert client.get("/stickpad").json()["catalogCheck"]["state"] == "changed"


def test_stickpad_rejects_catalog_changed_during_read_without_consuming_positions(tmp_path, monkeypatch):
    from pathlib import Path

    catalog = tmp_path / "data" / "HOMEOPATHY_Synthetic.txt"
    catalog.parent.mkdir()
    catalog.write_text("Synthetic Alpha\n", encoding="utf-8")
    read_bytes = Path.read_bytes
    reads = 0

    def change_on_second_read(path):
        nonlocal reads
        if path == catalog:
            reads += 1
            if reads == 2:
                catalog.write_text("Synthetic Beta\n", encoding="utf-8")
        return read_bytes(path)

    with TestClient(create_app(
        base_dir=tmp_path, data_dir=catalog.parent, materia_dir=tmp_path / "empty",
    )) as client:
        assert client.post("/stickpad/position", json={"x": 20, "y": 40}).status_code == 200
        with monkeypatch.context() as patcher:
            patcher.setattr(Path, "read_bytes", change_on_second_read)
            failed = client.post("/stickpad/analyze", json={"database": "HOMEOPATHY_Synthetic"})
        assert failed.status_code == 409
        assert "Katalog" in failed.text
        status = client.get("/stickpad").json()
        assert len(status["positions"]) == 1
        assert status["lastReceipt"] is None
        passed = client.post("/stickpad/analyze", json={"database": "HOMEOPATHY_Synthetic"})
        assert passed.status_code == 200
        assert passed.json()["stickPadCapture"]["catalog"]["rateCount"] == 1


def test_stickpad_rejects_new_matching_file_during_catalog_read(tmp_path, monkeypatch):
    from pathlib import Path

    data = tmp_path / "data"
    data.mkdir()
    first = data / "HOMEOPATHY_A.txt"
    first.write_text("Synthetic Alpha\n", encoding="utf-8")
    second = data / "HOMEOPATHY_B.txt"
    read_bytes = Path.read_bytes
    added = False

    def add_matching_file(path):
        nonlocal added
        if path == first and not added:
            second.write_text("Synthetic Beta\n", encoding="utf-8")
            added = True
        return read_bytes(path)

    with TestClient(create_app(
        base_dir=tmp_path, data_dir=data, materia_dir=tmp_path / "empty",
    )) as client:
        assert client.post("/stickpad/position", json={"x": 20, "y": 40}).status_code == 200
        with monkeypatch.context() as patcher:
            patcher.setattr(Path, "read_bytes", add_matching_file)
            failed = client.post("/stickpad/analyze", json={"database": "HOMEOPATHY_"})
        assert failed.status_code == 409
        assert len(client.get("/stickpad").json()["positions"]) == 1
        passed = client.post("/stickpad/analyze", json={"database": "HOMEOPATHY_"})
        assert passed.status_code == 200
        assert passed.json()["stickPadCapture"]["catalog"]["rateCount"] == 2
