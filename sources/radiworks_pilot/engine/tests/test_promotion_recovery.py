"""Regressions for local draft promotion and volatile broadcast failures."""

import pytest
from fastapi.testclient import TestClient

from radiworks.api.routes import STATE
from radiworks.core.broadcast import BroadcastError, BroadcastManager
from radiworks.core.draft import DraftStore
from radiworks.entropy import EntropyProvider
from radiworks.main import create_app


def test_failed_queue_start_does_not_claim_promoted(tmp_path, monkeypatch):
    catalog = tmp_path / "data" / "radionics"
    catalog.mkdir(parents=True)
    (catalog / "HOMEOPATHY_Test.txt").write_text(
        "Abrotanum\nAbsinthium\nAEsculus\nAconitum\nArnica\n",
        encoding="utf-8",
    )
    app = create_app(base_dir=tmp_path, data_dir=catalog, materia_dir=tmp_path / "empty-materia")
    with TestClient(app) as client:
        run = client.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 42}).json()
        draft_id = run["draft"]["id"]
        assert client.post(
            f"/drafts/{draft_id}/transition", json={"status": "ready"}
        ).status_code == 200
        state = STATE.state
        assert state is not None

        def queue_start_fails():
            raise BroadcastError("synthetic queue start failure")

        monkeypatch.setattr(state.broadcast, "_start_thread", queue_start_fails)
        response = client.post(f"/drafts/{draft_id}/promote", json={})

        assert response.status_code == 422
        assert state.draft_store.get(draft_id)["status"] == "ready"
        assert state.broadcast.queue_state()["queued"] == []
        assert state.broadcast.queue_state()["active"] == []
        assert state.draft_store.get(draft_id)["promotion"]["state"] == "failed"


def test_failed_final_draft_write_cancels_entire_batch(tmp_path, monkeypatch):
    catalog = tmp_path / "data" / "radionics"
    catalog.mkdir(parents=True)
    (catalog / "HOMEOPATHY_Test.txt").write_text(
        "Abrotanum\nAbsinthium\nAEsculus\nAconitum\nArnica\n", encoding="utf-8"
    )
    app = create_app(base_dir=tmp_path, data_dir=catalog, materia_dir=tmp_path / "empty-materia")
    with TestClient(app) as client:
        run = client.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 42}).json()
        draft_id = run["draft"]["id"]
        client.post(f"/drafts/{draft_id}/transition", json={"status": "ready"})
        state = STATE.state
        assert state is not None

        def write_fails(*_args):
            raise OSError("synthetic final write failure")

        monkeypatch.setattr(state.draft_store, "finish_promotion", write_fails)
        response = client.post(f"/drafts/{draft_id}/promote", json={"max_rates": 2})
        assert response.status_code == 503
        assert state.draft_store.get(draft_id)["status"] == "ready"
        assert state.draft_store.get(draft_id)["promotion"]["state"] == "failed"
        assert state.broadcast.queue_state()["queued"] == []
        assert state.broadcast.queue_state()["active"] == []


def test_startup_marks_open_promotion_interrupted_without_requeue(tmp_path):
    catalog = tmp_path / "data" / "radionics"
    catalog.mkdir(parents=True)
    (catalog / "HOMEOPATHY_Test.txt").write_text(
        "Abrotanum\nAbsinthium\nAEsculus\nAconitum\nArnica\n", encoding="utf-8"
    )
    app = create_app(base_dir=tmp_path, data_dir=catalog, materia_dir=tmp_path / "empty-materia")
    with TestClient(app) as client:
        run = client.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 42}).json()
        draft_id = run["draft"]["id"]
        client.post(f"/drafts/{draft_id}/transition", json={"status": "ready"})
        state = STATE.state
        assert state is not None
        promotion_id, _ = state.draft_store.begin_promotion(draft_id)

    restarted = create_app(base_dir=tmp_path, data_dir=catalog, materia_dir=tmp_path / "empty-materia")
    with TestClient(restarted) as client:
        state = STATE.state
        assert state is not None
        draft = client.get(f"/drafts/{draft_id}").json()
        assert draft["status"] == "ready"
        assert draft["promotion"]["id"] == promotion_id
        assert draft["promotion"]["state"] == "interrupted"
        assert not client.get("/broadcast/queue").json()["queued"]
        assert client.post(f"/drafts/{draft_id}/promote", json={}).status_code == 409


def test_failed_attempt_is_preserved_when_a_new_attempt_begins(tmp_path):
    store = DraftStore(tmp_path / "drafts")
    draft = store.create_from_analysis(
        analysis_dict={
            "generalVitality": 100,
            "rateObjects": [{"nameOrRate": "Synthetic", "gv": 200, "energeticValue": 1}],
        },
        passport={"kernel": "test", "kernel_version": "1", "run_id": "test"},
        database="HOMEOPATHY_Test",
    )
    store.transition(draft["id"], "ready")
    first_id, _ = store.begin_promotion(draft["id"])
    store.fail_promotion(draft["id"], first_id)
    second_id, _ = store.begin_promotion(draft["id"])
    current = store.get(draft["id"])
    assert first_id != second_id
    assert current["promotion_history"][-1]["id"] == first_id
    assert current["promotion_history"][-1]["state"] == "failed"


def test_finished_batch_is_confirmed_and_remains_complete_after_restart(tmp_path):
    catalog = tmp_path / "data" / "radionics"
    catalog.mkdir(parents=True)
    (catalog / "HOMEOPATHY_Test.txt").write_text(
        "Abrotanum\nAbsinthium\nAEsculus\nAconitum\nArnica\n", encoding="utf-8"
    )
    app = create_app(base_dir=tmp_path, data_dir=catalog, materia_dir=tmp_path / "empty-materia")
    with TestClient(app) as client:
        run = client.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 42}).json()
        draft_id = run["draft"]["id"]
        client.post(f"/drafts/{draft_id}/transition", json={"status": "ready"})
        promoted = client.post(f"/drafts/{draft_id}/promote", json={"max_rates": 2}).json()
        state = STATE.state
        assert state is not None
        for entry in promoted["broadcastEntries"]:
            state.publish("broadcast.progress", {"broadcastId": entry["broadcastId"], "finished": True})
        assert client.get(f"/drafts/{draft_id}").json()["promotion"]["state"] == "completed"

    restarted = create_app(base_dir=tmp_path, data_dir=catalog, materia_dir=tmp_path / "empty-materia")
    with TestClient(restarted) as client:
        assert client.get(f"/drafts/{draft_id}").json()["promotion"]["state"] == "completed"


def test_late_invalid_batch_entry_does_not_change_existing_queue(monkeypatch):
    events = []
    manager = BroadcastManager(EntropyProvider(seed=1), lambda kind, body: events.append((kind, body)))
    monkeypatch.setattr(manager, "_start_thread", lambda: None)
    foreign = manager.enqueue("FOREIGN", 60)
    accepted = []

    with pytest.raises(BroadcastError):
        manager.enqueue_batch(
            [
                {"signature": "VALID", "seconds": 60},
                {"signature": "INVALID", "seconds": 100_000},
            ],
            on_accepted=lambda ids: accepted.extend(ids),
        )

    assert accepted == []
    assert [item["broadcastId"] for item in manager.queue_state()["queued"]] == [
        foreign["broadcastId"]
    ]
    manager.shutdown()


def test_transition_api_cannot_claim_promoted_without_queue(tmp_path):
    catalog = tmp_path / "data" / "radionics"
    catalog.mkdir(parents=True)
    (catalog / "HOMEOPATHY_Test.txt").write_text(
        "Abrotanum\nAbsinthium\nAEsculus\nAconitum\nArnica\n", encoding="utf-8"
    )
    app = create_app(base_dir=tmp_path, data_dir=catalog, materia_dir=tmp_path / "empty-materia")
    with TestClient(app) as client:
        run = client.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 42}).json()
        draft_id = run["draft"]["id"]
        client.post(f"/drafts/{draft_id}/transition", json={"status": "ready"})

        response = client.post(
            f"/drafts/{draft_id}/transition", json={"status": "promoted"}
        )

        assert response.status_code == 409
        assert client.get(f"/drafts/{draft_id}").json()["status"] == "ready"
        assert client.get("/broadcast/queue").json()["queued"] == []
