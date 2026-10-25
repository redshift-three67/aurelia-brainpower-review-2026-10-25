"""S3: append-only Sessions und durable GV-Ereignisse."""

from fastapi.testclient import TestClient

from radiworks.api.routes import STATE
from radiworks.entropy_journal import EntropyJournalStore


def _create_case_and_analysis(home: TestClient, name: str = "S3 Synthetic") -> dict:
    assert home.post("/cases", json={"name": name, "description": "synthetisch"}).status_code == 200
    response = home.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 44})
    assert response.status_code == 200, response.text
    return response.json()


def test_analyses_append_distinct_persisted_sessions(home: TestClient):
    _create_case_and_analysis(home)
    second = home.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 45})
    assert second.status_code == 200, second.text

    case = home.get("/cases/S3Synthetic").json()
    sessions = case["sessionList"]
    assert len(sessions) == 2
    assert sessions[0]["sessionId"] != sessions[1]["sessionId"]
    assert sessions[0]["analysisResult"] != sessions[1]["analysisResult"]
    assert sessions[0]["draftId"] != sessions[1]["draftId"]


def test_gv_step_and_reset_are_persisted_as_events(home: TestClient):
    _create_case_and_analysis(home)
    step = home.post("/analysis/gv-round", json={})
    assert step.status_code == 200
    reset = home.post("/analysis/gv-round/reset")
    assert reset.status_code == 200

    case = home.get("/cases/S3Synthetic").json()
    session = case["sessionList"][0]
    assert [event["kind"] for event in session["gvHistory"]] == ["step", "reset"]
    assert session["revision"] == 2
    assert session["analysisResult"] == reset.json()["result"]
    assert session["gvState"]["counter"] == 0


def test_terminal_gv_boundary_forks_without_entropy_draw(home: TestClient):
    _create_case_and_analysis(home)
    ordinary = [home.post("/analysis/gv-round", json={}).json() for _ in range(6)]
    assert all(response["roundBoundary"] is False for response in ordinary)

    boundary = home.post("/analysis/gv-round", json={})
    assert boundary.status_code == 200
    boundary_data = boundary.json()
    assert boundary_data["roundBoundary"] is True
    assert boundary_data["gv"] is None
    assert boundary_data["rateIndex"] is None
    assert boundary_data["counter"] == 0
    assert boundary_data["totalRuns"] == 0

    case = home.get("/cases/S3Synthetic").json()
    assert len(case["sessionList"]) == 2
    parent, child = case["sessionList"]
    assert child["parentSessionId"] == parent["sessionId"]
    assert [event["kind"] for event in parent["gvHistory"]] == ["step"] * 6
    assert [event["kind"] for event in child["gvHistory"]] == ["round-boundary"]
    assert child["entropyCheckpoint"]["drawCount"] == parent["entropyCheckpoint"]["drawCount"]
    assert all(rate["gv"] == 0 for rate in child["analysisResult"]["rateObjects"])

    first_child_draw = home.post("/analysis/gv-round", json={}).json()
    assert first_child_draw["roundBoundary"] is False
    assert first_child_draw["counter"] == 1
    assert first_child_draw["rateIndex"] is None


def test_repeated_page_round_forks_with_auto_enabled_without_changing_auto_state(home: TestClient):
    analysis = _create_case_and_analysis(home)
    state = STATE.state
    assert state is not None and state.auto is not None
    # The test isolates the manual round from the background clock; the live
    # Auto tick has its own controller and is covered by test_automode.py.
    state.auto.tick = lambda: None
    enabled = home.post(
        "/auto-mode/on", json={"database": "HOMEOPATHY_Test", "multiplier": 1}
    )
    assert enabled.status_code == 200
    assert home.get("/analysis/gv-round").json()["supportsBoundSuccessor"] is True

    draft_id = analysis["draft"]["id"]
    for counter in range(6):
        step = home.post(
            "/analysis/gv-round",
            json={"expected_draft_id": draft_id, "expected_counter": counter},
        )
        assert step.status_code == 200, (counter, step.text)
        assert step.json()["draftId"] == draft_id
        assert step.json()["counter"] == counter + 1
        if counter == 0:
            duplicate = home.post(
                "/analysis/gv-round",
                json={"expected_draft_id": draft_id, "expected_counter": 0},
            )
            assert duplicate.status_code == 409

    boundary = home.post(
        "/analysis/gv-round",
        json={"expected_draft_id": draft_id, "expected_counter": 6},
    )
    assert boundary.status_code == 200
    child = boundary.json()
    assert child["roundBoundary"] is True
    assert child["counter"] == 0
    assert child["draftId"] != draft_id

    first_repeat = home.post(
        "/analysis/gv-round",
        json={"expected_draft_id": child["draftId"], "expected_counter": 0},
    )
    assert first_repeat.status_code == 200
    assert first_repeat.json()["counter"] == 1
    assert home.get("/auto-mode").json()["enabled"] is True
    assert home.get("/broadcast/queue").json()["queued"] == []


def test_ready_draft_gets_successor_when_gv_changes(home: TestClient):
    analysis = _create_case_and_analysis(home)
    original_id = analysis["draft"]["id"]
    assert home.post(f"/drafts/{original_id}/transition", json={"status": "ready"}).status_code == 200

    assert home.post("/analysis/gv-round", json={}).status_code == 200
    case = home.get("/cases/S3Synthetic").json()
    successor_id = case["sessionList"][0]["draftId"]

    assert successor_id != original_id
    assert home.get(f"/drafts/{original_id}").json()["status"] == "ready"
    successor = home.get(f"/drafts/{successor_id}").json()
    assert successor["status"] == "draft"
    assert successor["parentDraftId"] == original_id


def test_later_gv_page_forks_complete_result_and_resumes_by_page(home: TestClient, tmp_path):
    catalog = tmp_path / "data" / "radionics" / "HOMEOPATHY_Test.txt"
    catalog.write_text("\n".join(f"Synthetic rate {i:02d}" for i in range(47)) + "\n", encoding="utf-8")
    run = _create_case_and_analysis(home, "Page Synthetic")
    assert len(run["result"]["rateObjects"]) > 42
    parent_session_id = home.get("/analysis/gv-round").json()["sessionId"]
    parent_draft_id = run["draft"]["id"]
    for _ in range(3):
        assert home.post("/analysis/gv-round", json={}).status_code == 200
    parent = home.get("/cases/PageSynthetic").json()["sessionList"][0]
    original_gv = [rate["gv"] for rate in parent["analysisResult"]["rateObjects"]]
    assert any(original_gv[:2])

    start = home.post("/analysis/gv-page/start", json={
        "page": 2, "expected_draft_id": parent_draft_id,
        "expected_session_id": parent_session_id,
    })
    assert start.status_code == 200, start.text
    child = start.json()
    assert child["sessionId"] != parent_session_id
    assert child["draftId"] != parent_draft_id
    assert child["pageStart"] == 21 and child["pageLength"] == 21
    assert len(child["result"]["rateObjects"]) == len(original_gv)
    assert [rate["gv"] for rate in child["result"]["rateObjects"][:21]] == original_gv[:21]
    assert all(rate["gv"] == 0 for rate in child["result"]["rateObjects"][21:42])
    assert home.post("/analysis/gv-page/start", json={
        "page": 2, "expected_draft_id": parent_draft_id,
        "expected_session_id": parent_session_id,
    }).status_code == 409

    for counter in range(3):
        step = home.post("/analysis/gv-round", json={
            "expected_draft_id": child["draftId"], "expected_counter": counter,
        })
        assert step.status_code == 200, step.text
    assert step.json()["rateIndex"] == 22
    case = home.get("/cases/PageSynthetic").json()
    assert case["sessionList"][0] == parent
    assert case["sessionList"][1]["gvState"]["pageStart"] == 21
    assert case["sessionList"][1]["analysisResult"]["rateObjects"][22]["gv"] > 0

    viewed = home.post("/analysis/sessions/1/view")
    assert viewed.status_code == 200, viewed.text
    state = home.get("/analysis/gv-round").json()
    assert state["pageStart"] == 21 and state["counter"] == 3
    assert state["sessionId"] == child["sessionId"]
    assert home.post("/analysis/gv-round", json={
        "expected_draft_id": state["draftId"], "expected_counter": 3,
    }).json()["rateIndex"] == 23
    third = home.post("/analysis/gv-page/start", json={
        "page": 3, "expected_draft_id": state["draftId"],
        "expected_session_id": state["sessionId"],
    })
    assert third.status_code == 200, third.text
    assert third.json()["pageStart"] == 42
    assert third.json()["pageLength"] == 5
    assert len(third.json()["result"]["rateObjects"]) == 47
    assert third.json()["result"]["rateObjects"][22]["gv"] > 0


def test_later_gv_page_rejects_missing_or_stale_session(home: TestClient, tmp_path):
    catalog = tmp_path / "data" / "radionics" / "HOMEOPATHY_Test.txt"
    catalog.write_text("\n".join(f"Synthetic rate {i:02d}" for i in range(24)) + "\n", encoding="utf-8")
    run = _create_case_and_analysis(home, "Page Guard")
    request = {"page": 2, "expected_draft_id": run["draft"]["id"],
               "expected_session_id": home.get("/analysis/gv-round").json()["sessionId"]}
    assert home.post("/analysis/gv-page/start", json={**request, "page": 3}).status_code == 422
    assert home.post("/analysis/gv-page/start", json={**request, "expected_session_id": "stale"}).status_code == 409
    assert len(home.get("/cases/PageGuard").json()["sessionList"]) == 1


def test_entropy_journal_encrypts_raw_seed_material(tmp_path):
    from cryptography.fernet import Fernet

    journal = EntropyJournalStore(tmp_path, key=Fernet.generate_key()).create()
    assert journal.append(123456, "webcam", 0) == 1
    assert journal.records() == [{"seed": 123456, "source": "webcam", "segment": 0}]
    assert b"123456" not in journal.path.read_bytes()


def test_legacy_session_is_not_mutated_until_gv_write(home: TestClient):
    assert home.post("/cases", json={"name": "Legacy Synthetic"}).status_code == 200
    state = STATE.state
    assert state is not None
    state.case_store.current["sessionList"] = [
        {
            "created": "2026-01-01T00:00:00+00:00",
            "analysisResult": {"generalVitality": 1, "numberOfTrials": 1, "rateObjects": []},
            "passport": {"seed": 1},
        }
    ]
    state.case_store.save(state.case_store.current)

    viewed = home.post("/analysis/sessions/0/view")
    assert viewed.status_code == 200
    before = home.get("/cases/LegacySynthetic").json()["sessionList"][0]
    assert "sessionId" not in before

    assert home.post("/analysis/gv-round", json={}).status_code == 200
    after = home.get("/cases/LegacySynthetic").json()["sessionList"][0]
    assert after["sessionId"]
    assert after["gvHistory"]


def test_stochastic_case_requires_deployment_journal_key(home: TestClient, monkeypatch):
    monkeypatch.delenv("RADIOWORKS_JOURNAL_KEY", raising=False)
    assert home.post("/cases", json={"name": "S3 Stochastic"}).status_code == 200

    response = home.post(
        "/analysis", json={"database": "HOMEOPATHY_Test", "mode": "stochastic"}
    )

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "stochastic_recovery_unavailable"
    assert "RADIOWORKS_JOURNAL_KEY" not in response.json()["error"]["message"]
    assert home.get("/cases/S3Stochastic").json()["sessionList"] == []
    assert home.get("/drafts").json()["drafts"] == []


def test_stochastic_without_case_remains_nonrecoverable(home: TestClient, monkeypatch):
    monkeypatch.delenv("RADIOWORKS_JOURNAL_KEY", raising=False)
    state = STATE.state
    assert state is not None
    state.random_org._http_get = None
    state.entropy_feed.feed([123456])

    status = home.get("/entropy/status").json()["stochasticRecovery"]
    assert status == {
        "activeCase": False,
        "requiredForActiveCase": False,
        "available": False,
    }
    response = home.post(
        "/analysis", json={"database": "HOMEOPATHY_Test", "mode": "stochastic"}
    )

    assert response.status_code == 200
    assert home.get("/drafts").json()["drafts"]
    assert not state.journal_dir.exists()


def test_stochastic_case_keeps_raw_seeds_out_of_public_artifacts(home: TestClient, monkeypatch):
    from cryptography.fernet import Fernet

    monkeypatch.setenv("RADIOWORKS_JOURNAL_KEY", Fernet.generate_key().decode("ascii"))
    assert home.post("/cases", json={"name": "S3 Stochastic"}).status_code == 200
    state = STATE.state
    assert state is not None
    state.random_org._http_get = None
    state.entropy_feed.feed([123456])
    assert home.get("/entropy/status").json()["stochasticRecovery"] == {
        "activeCase": True,
        "requiredForActiveCase": True,
        "available": True,
    }

    analysis = home.post(
        "/analysis", json={"database": "HOMEOPATHY_Test", "mode": "stochastic"}
    )
    assert analysis.status_code == 200
    case = home.get("/cases/S3Stochastic").json()
    checkpoint = case["sessionList"][0]["entropyCheckpoint"]
    assert checkpoint["journalId"]
    assert "123456" not in str(case)
    journal = state.open_entropy_journal(checkpoint["journalId"])
    assert journal.records()[0]["seed"] == 123456
    assert b"123456" not in journal.path.read_bytes()


def test_stochastic_parent_session_survives_child_journal_suffix(home: TestClient, monkeypatch):
    from cryptography.fernet import Fernet

    monkeypatch.setenv("RADIOWORKS_JOURNAL_KEY", Fernet.generate_key().decode("ascii"))
    assert home.post("/cases", json={"name": "S3 Stochastic Fork"}).status_code == 200
    state = STATE.state
    assert state is not None
    state.random_org._http_get = None
    state.entropy_feed.feed([123456] * 256)

    assert home.post(
        "/analysis", json={"database": "HOMEOPATHY_Test", "mode": "stochastic"}
    ).status_code == 200
    for _ in range(6):
        assert home.post("/analysis/gv-round", json={}).status_code == 200
    assert home.post("/analysis/gv-round", json={}).status_code == 200
    assert home.post("/analysis/gv-round", json={}).status_code == 200

    sessions = home.get("/cases/S3StochasticFork").json()["sessionList"]
    parent, child = sessions
    assert child["entropyCheckpoint"]["journalCursor"] > parent["entropyCheckpoint"]["journalCursor"]
    assert home.post("/analysis/sessions/0/view").status_code == 200


def test_stochastic_session_rejects_tampered_checkpoint_prefix(home: TestClient, monkeypatch):
    from cryptography.fernet import Fernet

    monkeypatch.setenv("RADIOWORKS_JOURNAL_KEY", Fernet.generate_key().decode("ascii"))
    assert home.post("/cases", json={"name": "S3 Stochastic Tamper"}).status_code == 200
    state = STATE.state
    assert state is not None
    state.random_org._http_get = None
    state.entropy_feed.feed([123456] * 256)
    assert home.post(
        "/analysis", json={"database": "HOMEOPATHY_Test", "mode": "stochastic"}
    ).status_code == 200

    session = home.get("/cases/S3StochasticTamper").json()["sessionList"][0]
    journal = state.open_entropy_journal(session["entropyCheckpoint"]["journalId"])
    journal.path.write_bytes(b"tampered\\n" + journal.path.read_bytes())

    response = home.post("/analysis/sessions/0/view")
    assert response.status_code == 422
    assert "Session-Checkpoint" in response.json()["error"]["message"]


def test_legacy_stochastic_checkpoint_keeps_whole_journal_integrity(home: TestClient, monkeypatch):
    from cryptography.fernet import Fernet

    monkeypatch.setenv("RADIOWORKS_JOURNAL_KEY", Fernet.generate_key().decode("ascii"))
    assert home.post("/cases", json={"name": "S3 Stochastic Legacy"}).status_code == 200
    state = STATE.state
    assert state is not None
    state.random_org._http_get = None
    state.entropy_feed.feed([123456] * 256)
    assert home.post(
        "/analysis", json={"database": "HOMEOPATHY_Test", "mode": "stochastic"}
    ).status_code == 200

    session = state.case_store.current["sessionList"][0]
    checkpoint = session["entropyCheckpoint"]
    checkpoint.pop("journalPrefixDigest")
    journal = state.open_entropy_journal(checkpoint["journalId"])
    journal.append(654321, "os", 1)
    journal.commit()
    state.case_store.save(state.case_store.current)

    assert home.post("/analysis/sessions/0/view").status_code == 422
