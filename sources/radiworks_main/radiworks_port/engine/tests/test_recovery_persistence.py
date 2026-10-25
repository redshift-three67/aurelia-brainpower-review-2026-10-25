"""Ausfallgrenzen fuer atomare Case-/Draft-Recovery."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from radiworks.api.routes import STATE
from radiworks.main import create_app
from radiworks.persistence import (
    RecoveryCoordinator,
    RecoveryError,
    RecoveryTarget,
    atomic_json_replace,
)


def _coordinator(root: Path, failure_hook=None) -> RecoveryCoordinator:
    cases = root / "cases"
    drafts = root / "drafts"
    cases.mkdir(parents=True)
    drafts.mkdir()
    return RecoveryCoordinator(
        root / "recovery",
        stores={"case": cases, "draft": drafts},
        failure_hook=failure_hook,
    )


@pytest.mark.parametrize(
    ("phase", "index"),
    [
        ("prepared", 0),
        ("target-replaced", 0),
        ("target-replaced", 1),
        ("completed", 2),
    ],
)
def test_recovery_completes_every_interrupted_target_boundary(tmp_path, phase, index):
    interrupted = {"raised": False}

    def fail_once(actual_phase, actual_index):
        if not interrupted["raised"] and (actual_phase, actual_index) == (phase, index):
            interrupted["raised"] = True
            raise RuntimeError("simulated interruption")

    coordinator = _coordinator(tmp_path, fail_once)
    case_path = tmp_path / "cases" / "atomic.json"
    draft_path = tmp_path / "drafts" / "draft-1.json"
    before_case = {"name": "atomic", "sessionList": []}
    before_draft = {"id": "draft-1", "sessionId": None}
    after_case = {"name": "atomic", "sessionList": [{"sessionId": "session-1"}]}
    after_draft = {"id": "draft-1", "sessionId": "session-1"}
    atomic_json_replace(case_path, before_case)
    atomic_json_replace(draft_path, before_draft)

    with pytest.raises(RecoveryError):
        coordinator.apply(
            "analysis-session-link",
            [
                RecoveryTarget("case", "atomic.json", before_case, after_case),
                RecoveryTarget("draft", "draft-1.json", before_draft, after_draft),
            ],
        )

    RecoveryCoordinator(
        tmp_path / "recovery",
        stores={"case": tmp_path / "cases", "draft": tmp_path / "drafts"},
    ).recover()

    assert json.loads(case_path.read_text(encoding="utf-8")) == after_case
    assert json.loads(draft_path.read_text(encoding="utf-8")) == after_draft
    assert list((tmp_path / "recovery").glob("*.json")) == []


def test_recovery_fails_closed_on_operator_digest_conflict(tmp_path):
    def interrupt_after_marker(phase, _index):
        if phase == "prepared":
            raise RuntimeError("simulated interruption")

    coordinator = _coordinator(tmp_path, interrupt_after_marker)
    case_path = tmp_path / "cases" / "atomic.json"
    before = {"name": "atomic", "sessionList": []}
    after = {"name": "atomic", "sessionList": [{"sessionId": "session-1"}]}
    operator_edit = {"name": "atomic", "sessionList": [{"sessionId": "operator"}]}
    atomic_json_replace(case_path, before)

    with pytest.raises(RecoveryError):
        coordinator.apply(
            "analysis-session-link",
            [RecoveryTarget("case", "atomic.json", before, after)],
        )
    atomic_json_replace(case_path, operator_edit)

    with pytest.raises(RecoveryError):
        RecoveryCoordinator(
            tmp_path / "recovery",
            stores={"case": tmp_path / "cases", "draft": tmp_path / "drafts"},
        ).recover()

    assert json.loads(case_path.read_text(encoding="utf-8")) == operator_edit
    marker = next((tmp_path / "recovery").glob("*.json"))
    assert json.loads(marker.read_text(encoding="utf-8"))["state"] == "failed"


def test_interrupted_analysis_recovers_linked_case_and_draft_after_restart(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    (data / "HOMEOPATHY_Test.txt").write_text("Synthetic rate\n", encoding="utf-8")
    app = create_app(base_dir=tmp_path, data_dir=data)

    with TestClient(app) as client:
        assert client.post("/cases", json={"name": "Atomic Synthetic"}).status_code == 200
        state = STATE.state
        assert state is not None
        failed = {"value": False}

        def interrupt_after_draft(phase, index):
            if not failed["value"] and (phase, index) == ("target-replaced", 0):
                failed["value"] = True
                raise RuntimeError("simulated interruption")

        state.recovery._failure_hook = interrupt_after_draft
        response = client.post(
            "/analysis",
            json={"database": "HOMEOPATHY_Test", "seed": 44},
        )
        assert response.status_code == 409
        assert list((tmp_path / "recovery").glob("*.json"))

    restarted = create_app(base_dir=tmp_path, data_dir=data)
    with TestClient(restarted) as client:
        case = client.get("/cases/AtomicSynthetic").json()
        drafts = client.get("/drafts").json()["drafts"]

    assert len(case["sessionList"]) == 1
    session = case["sessionList"][0]
    assert len(drafts) == 1
    assert drafts[0]["sessionId"] == session["sessionId"]
    assert drafts[0]["sessionRevision"] == session["revision"]
    assert list((tmp_path / "recovery").glob("*.json")) == []


def test_interrupted_gv_projection_recovers_one_event_and_draft_revision(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    (data / "HOMEOPATHY_Test.txt").write_text("Synthetic rate\n", encoding="utf-8")
    app = create_app(base_dir=tmp_path, data_dir=data)

    with TestClient(app) as client:
        assert client.post("/cases", json={"name": "GV Atomic"}).status_code == 200
        analysis = client.post(
            "/analysis",
            json={"database": "HOMEOPATHY_Test", "seed": 44},
        ).json()
        draft_id = analysis["draft"]["id"]
        state = STATE.state
        assert state is not None
        failed = {"value": False}

        def interrupt_after_case(phase, index):
            if not failed["value"] and (phase, index) == ("target-replaced", 0):
                failed["value"] = True
                raise RuntimeError("simulated interruption")

        state.recovery._failure_hook = interrupt_after_case
        response = client.post("/analysis/gv-round", json={})
        assert response.status_code == 409
        assert list((tmp_path / "recovery").glob("*.json"))

    restarted = create_app(base_dir=tmp_path, data_dir=data)
    with TestClient(restarted) as client:
        case = client.get("/cases/GVAtomic").json()
        draft = client.get(f"/drafts/{draft_id}").json()

    session = case["sessionList"][0]
    assert len(session["gvHistory"]) == 1
    assert session["revision"] == 1
    assert draft["sessionId"] == session["sessionId"]
    assert draft["sessionRevision"] == 1
    assert list((tmp_path / "recovery").glob("*.json")) == []


def test_interrupted_stickpad_gv_recovers_receipt_and_case_once(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    (data / "HOMEOPATHY_Test.txt").write_text("Synthetic rate\n", encoding="utf-8")

    with TestClient(create_app(base_dir=tmp_path, data_dir=data)) as client:
        assert client.post("/cases", json={"name": "Stick Recovery"}).status_code == 200
        analysis = client.post(
            "/analysis", json={"database": "HOMEOPATHY_Test", "seed": 44},
        ).json()
        assert client.post("/stickpad/position", json={"x": 640, "y": 400}).status_code == 200
        state = STATE.state
        assert state is not None
        interrupted = False

        def fail_after_case(phase, index):
            nonlocal interrupted
            if not interrupted and (phase, index) == ("target-replaced", 0):
                interrupted = True
                raise RuntimeError("synthetic interruption")

        state.recovery._failure_hook = fail_after_case
        assert client.post("/stickpad/gv").status_code == 409
        assert client.post("/stickpad/position", json={"x": 20, "y": 40}).status_code == 409
        assert list((tmp_path / "recovery").glob("*.json"))

    with TestClient(create_app(base_dir=tmp_path, data_dir=data)) as restarted:
        case = restarted.get("/cases/StickRecovery").json()
        session = case["sessionList"][0]
        pad = restarted.get("/stickpad").json()
        draft = restarted.get(f"/drafts/{analysis['draft']['id']}").json()
        assert len(session["gvHistory"]) == 1
        assert session["revision"] == 1
        assert session["gvHistory"][0]["kind"] == "stickpad-step"
        assert session["gvHistory"][0]["stickPadReceiptId"] == pad["lastReceipt"]["id"]
        assert pad["positions"] == []
        assert draft["sessionRevision"] == 1
        assert list((tmp_path / "recovery").glob("*.json")) == []


def test_interrupted_stickpad_analysis_recovers_draft_session_and_capture_once(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    (data / "HOMEOPATHY_Test.txt").write_text("Synthetic rate\n", encoding="utf-8")

    with TestClient(create_app(base_dir=tmp_path, data_dir=data)) as client:
        assert client.post("/cases", json={"name": "Stick Analysis Recovery"}).status_code == 200
        assert client.post("/stickpad/position", json={"x": 640, "y": 400}).status_code == 200
        state = STATE.state
        assert state is not None
        interrupted = False

        def fail_after_draft(phase, index):
            nonlocal interrupted
            if not interrupted and (phase, index) == ("target-replaced", 0):
                interrupted = True
                raise RuntimeError("synthetic interruption")

        state.recovery._failure_hook = fail_after_draft
        assert client.post(
            "/stickpad/analyze", json={"database": "HOMEOPATHY_Test"},
        ).status_code == 409
        assert client.post("/stickpad/position", json={"x": 20, "y": 40}).status_code == 409
        assert list((tmp_path / "recovery").glob("*.json"))

    with TestClient(create_app(base_dir=tmp_path, data_dir=data)) as restarted:
        case = restarted.get("/cases/StickAnalysisRecovery").json()
        assert len(case["sessionList"]) == 1
        session = case["sessionList"][0]
        pad = restarted.get("/stickpad").json()
        draft = restarted.get(f"/drafts/{session['draftId']}").json()
        assert pad["positions"] == []
        assert session["stickPadReceiptId"] == pad["lastReceipt"]["id"]
        assert session["stickPadCapture"] == pad["lastReceipt"]
        assert draft["sessionId"] == session["sessionId"]
        assert draft["source_run_id"] == pad["lastReceipt"]["runId"]
        assert list((tmp_path / "recovery").glob("*.json")) == []


def test_interrupted_gv_fork_recovers_child_session_and_successor_draft(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    (data / "HOMEOPATHY_Test.txt").write_text("Synthetic rate\n", encoding="utf-8")
    app = create_app(base_dir=tmp_path, data_dir=data)

    with TestClient(app) as client:
        assert client.post("/cases", json={"name": "Fork Atomic"}).status_code == 200
        analysis = client.post(
            "/analysis",
            json={"database": "HOMEOPATHY_Test", "seed": 44},
        ).json()
        parent_draft_id = analysis["draft"]["id"]
        state = STATE.state
        assert state is not None and state.gv_round is not None
        while not state.gv_round.at_round_boundary:
            assert client.post("/analysis/gv-round", json={}).status_code == 200
        failed = {"value": False}

        def interrupt_after_child_case(phase, index):
            if not failed["value"] and (phase, index) == ("target-replaced", 0):
                failed["value"] = True
                raise RuntimeError("simulated interruption")

        state.recovery._failure_hook = interrupt_after_child_case
        response = client.post("/analysis/gv-round", json={})
        assert response.status_code == 409
        assert list((tmp_path / "recovery").glob("*.json"))

    restarted = create_app(base_dir=tmp_path, data_dir=data)
    with TestClient(restarted) as client:
        case = client.get("/cases/ForkAtomic").json()
        drafts = client.get("/drafts").json()["drafts"]

    assert len(case["sessionList"]) == 2
    parent, child = case["sessionList"]
    assert child["parentSessionId"] == parent["sessionId"]
    assert child["draftId"] != parent_draft_id
    successor = next(draft for draft in drafts if draft["id"] == child["draftId"])
    assert successor["parentDraftId"] == parent_draft_id
    assert successor["sessionId"] == child["sessionId"]
    assert list((tmp_path / "recovery").glob("*.json")) == []


def test_startup_fails_closed_for_an_unknown_recovery_marker(tmp_path):
    recovery_dir = tmp_path / "recovery"
    recovery_dir.mkdir()
    (recovery_dir / "unknown.json").write_text('{"schema":"unknown"}', encoding="utf-8")
    app = create_app(base_dir=tmp_path)

    with pytest.raises(RecoveryError):
        with TestClient(app):
            pass


def test_seeded_session_restores_and_continues_gv_after_clean_restart(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    (data / "HOMEOPATHY_Test.txt").write_text(
        "Abrotanum\nAbsinthium\nAEsculus\nAconitum\nArnica\n",
        encoding="utf-8",
    )

    app = create_app(base_dir=tmp_path, data_dir=data)
    with TestClient(app) as client:
        assert client.post("/cases", json={"name": "Seeded Restart"}).status_code == 200
        assert client.post(
            "/analysis", json={"database": "HOMEOPATHY_Test", "seed": 44}
        ).status_code == 200

    restarted = create_app(base_dir=tmp_path, data_dir=data)
    with TestClient(restarted) as client:
        assert client.post("/cases/SeededRestart/activate").status_code == 200
        assert client.post("/analysis/sessions/0/view").status_code == 200
        assert client.post("/analysis/gv-round", json={}).status_code == 200


def test_seeded_gv_sequence_matches_uninterrupted_run_across_restart(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    (data / "HOMEOPATHY_Test.txt").write_text(
        "Abrotanum\nAbsinthium\nAEsculus\nAconitum\nArnica\n",
        encoding="utf-8",
    )

    def start(client):
        assert client.post("/cases", json={"name": "Seeded Differential"}).status_code == 200
        assert client.post(
            "/analysis", json={"database": "HOMEOPATHY_Test", "seed": 44}
        ).status_code == 200

    def step(client):
        response = client.post("/analysis/gv-round", json={})
        assert response.status_code == 200
        body = response.json()
        return {
            "gv": body["gv"],
            "generalVitality": body["generalVitality"],
            "counter": body["counter"],
            "totalRuns": body["totalRuns"],
            "rateIndex": body["rateIndex"],
            "roundBoundary": body["roundBoundary"],
            "rates": [
                (rate["gv"], rate["recurringGeneralVitality"])
                for rate in body["result"]["rateObjects"]
            ],
        }

    baseline = create_app(base_dir=tmp_path / "baseline", data_dir=data)
    with TestClient(baseline) as client:
        start(client)
        baseline_steps = [step(client) for _ in range(8)]
        baseline_case = client.get("/cases/SeededDifferential").json()

    interrupted = create_app(base_dir=tmp_path / "interrupted", data_dir=data)
    with TestClient(interrupted) as client:
        start(client)
        restarted_steps = [step(client) for _ in range(5)]

    resumed = create_app(base_dir=tmp_path / "interrupted", data_dir=data)
    with TestClient(resumed) as client:
        assert client.post("/cases/SeededDifferential/activate").status_code == 200
        assert client.post("/analysis/sessions/0/view").status_code == 200
        restarted_steps.extend(step(client) for _ in range(3))
        restarted_case = client.get("/cases/SeededDifferential").json()

    assert restarted_steps == baseline_steps
    assert [item["roundBoundary"] for item in restarted_steps] == [False] * 6 + [True, False]
    for case in (baseline_case, restarted_case):
        assert len(case["sessionList"]) == 2
        parent, child = case["sessionList"]
        assert child["parentSessionId"] == parent["sessionId"]
