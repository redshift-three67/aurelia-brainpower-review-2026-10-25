"""S4.3: öffentliche Projektion ohne Verlust der internen Analysebelege."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from radiworks.api.routes import BOOT_ID, STATE


BLOCKED = "Heilt garantiert"
PLACEHOLDER = "[CopyGuard: Text zurückgehalten]"


def _blocked_analysis(home: TestClient, tmp_path: Path) -> dict:
    catalog = tmp_path / "data" / "radionics" / "HOMEOPATHY_S4Blocked.txt"
    catalog.write_text(BLOCKED + "\n", encoding="utf-8")
    state = home.app.state.radiworks_state
    state.rate_repository.refresh()
    response = home.post(
        "/analysis", json={"database": "HOMEOPATHY_S4Blocked", "seed": 7}
    )
    assert response.status_code == 200
    return response.json()


def _assert_public(value: dict) -> None:
    serialized = json.dumps(value, ensure_ascii=False)
    assert BLOCKED not in serialized
    assert PLACEHOLDER in serialized


def test_blocked_analysis_is_projected_across_http_and_live_but_raw_is_kept(
    home: TestClient, tmp_path: Path,
) -> None:
    created = home.post("/cases", json={"name": "S4 Fall"})
    assert created.status_code == 200
    analysis = _blocked_analysis(home, tmp_path)
    _assert_public(analysis)
    draft_id = analysis["draft"]["id"]
    assert analysis["draft"]["copyguard_verdict"] == "block"

    state = home.app.state.radiworks_state
    raw_draft = state.draft_store.get(draft_id)
    assert raw_draft is not None
    assert raw_draft["payload"]["rateObjects"][0]["nameOrRate"] == BLOCKED
    assert state.case_store.current["sessionList"][-1]["analysisResult"]["rateObjects"][0]["nameOrRate"] == BLOCKED

    for path in (
        "/analysis/current",
        f"/drafts/{draft_id}",
        "/cases/current",
        "/cases/S4Fall",
        "/cases/S4Fall/statistics",
    ):
        response = home.get(path)
        assert response.status_code == 200, path
        assert BLOCKED not in json.dumps(response.json(), ensure_ascii=False), path
    viewed = home.post("/analysis/sessions/0/view")
    assert viewed.status_code == 200
    _assert_public(viewed.json())

    analysis_events = [
        event for event in state.event_history if event["type"] == "analysis.update"
    ]
    assert analysis_events
    _assert_public(analysis_events[-1])
    event_id = analysis_events[-1]["id"]
    with home.websocket_connect(
        f"/ws?last_event_id={event_id - 1}&last_boot={BOOT_ID}"
    ) as ws:
        assert ws.receive_json()["type"] == "server.hello"
        replay = ws.receive_json()
    assert replay["type"] == "analysis.update"
    _assert_public(replay)

    ready = home.post(f"/drafts/{draft_id}/transition", json={"status": "ready"})
    assert ready.status_code == 200
    assert home.post(f"/drafts/{draft_id}/promote").status_code == 409
    queue = home.get("/broadcast/queue").json()
    assert not queue["queued"] and not queue["active"]


def test_case_metadata_edit_preserves_raw_analysis_and_rejects_redacted_document(
    home: TestClient, tmp_path: Path,
) -> None:
    assert home.post(
        "/cases", json={"name": "S4 Edit", "description": BLOCKED}
    ).status_code == 200
    _blocked_analysis(home, tmp_path)
    public_case = home.get("/cases/current").json()
    assert BLOCKED not in json.dumps(public_case, ensure_ascii=False)
    assert public_case["description"] == PLACEHOLDER

    unsafe_roundtrip = home.post("/cases", json=public_case)
    assert unsafe_roundtrip.status_code == 409

    unchanged = home.post(
        "/cases/current/metadata",
        json={"name": "S4 Edit", "description": PLACEHOLDER},
    )
    assert unchanged.status_code == 200
    assert home.app.state.radiworks_state.case_store.current["description"] == BLOCKED
    rejected = home.post(
        "/cases/current/metadata",
        json={"description": BLOCKED},
    )
    assert rejected.status_code == 409
    assert home.app.state.radiworks_state.case_store.current["description"] == BLOCKED

    saved = home.post(
        "/cases/current/metadata",
        json={"name": "S4 Edit", "description": "sicherer Text", "intention": "Notiz"},
    )
    assert saved.status_code == 200
    assert saved.json()["description"] == "sicherer Text"
    raw = home.app.state.radiworks_state.case_store.current
    assert raw["sessionList"][-1]["analysisResult"]["rateObjects"][0]["nameOrRate"] == BLOCKED
    assert raw["sessionList"][-1]["intention"] == "Notiz"


def test_current_case_metadata_requires_an_active_case(home: TestClient) -> None:
    response = home.post("/cases/current/metadata", json={"description": "Text"})
    assert response.status_code == 409


def test_error_response_does_not_echo_blocked_case_name(home: TestClient) -> None:
    response = home.get("/cases/Heilt%20garantiert")
    assert response.status_code == 404
    assert BLOCKED not in json.dumps(response.json(), ensure_ascii=False)
    assert PLACEHOLDER in response.json()["error"]["message"]


def test_opaque_case_reference_loads_distinct_redacted_cases_without_exposing_names(
    home: TestClient,
) -> None:
    for name in ("Heilt garantiert", "Diagnose sicher"):
        assert home.post("/cases", json={"name": name, "description": "Synthetisch"}).status_code == 200
    listed = home.get("/cases").json()
    entries = listed["entries"]
    assert len(entries) == 2
    assert [entry["name"] for entry in entries] == [PLACEHOLDER, PLACEHOLDER]
    assert len({entry["ref"] for entry in entries}) == 2
    assert "Heilt garantiert" not in json.dumps(listed, ensure_ascii=False)
    for entry in entries:
        activated = home.post(f"/cases/ref/{entry['ref']}/activate")
        assert activated.status_code == 200
        assert activated.json()["name"] == PLACEHOLDER
        stats = home.get(f"/cases/ref/{entry['ref']}/statistics")
        assert stats.status_code == 200
        assert stats.json()["case"] == PLACEHOLDER
        assert home.app.state.radiworks_state.case_store.current["name"] in (
            "Heilt garantiert", "Diagnose sicher"
        )
    current_ref = home.get("/cases/current/ref").json()["ref"]
    assert current_ref in {entry["ref"] for entry in entries}
    recent = home.get("/cases/recent").json()
    assert recent["entries"][0]["ref"] == current_ref
    assert recent["entries"][0]["name"] == PLACEHOLDER
    assert "Heilt garantiert" not in json.dumps(recent, ensure_ascii=False)
    assert home.post("/cases/ref/invalid/activate").status_code == 404
    assert home.get("/cases/ref/invalid/statistics").status_code == 404


def test_safe_analysis_payload_stays_unchanged(home: TestClient) -> None:
    response = home.post(
        "/analysis", json={"database": "HOMEOPATHY_Test", "seed": 7}
    )
    assert response.status_code == 200
    assert all(rate["nameOrRate"] != PLACEHOLDER for rate in response.json()["result"]["rateObjects"])
    state = home.app.state.radiworks_state
    raw = state.draft_store.get(response.json()["draft"]["id"])
    assert response.json()["result"] == raw["payload"]


def test_clarke_corpus_is_projected_without_changing_loaded_source(
    home: TestClient, tmp_path: Path,
) -> None:
    corpus = tmp_path / "materiaMedica" / "Clarke" / "Synthetic.json"
    corpus.write_text(json.dumps({
        "remedyName": "Heilt garantiert",
        "remedyAlternativeNames": "Miracle",
        "categories": {"Clinical": ["Diagnose sicher"]},
    }), encoding="utf-8")
    state = home.app.state.radiworks_state
    state.materia_medica.load()

    search = home.get("/materiaMedicaSearch", params={"query": "Heilt"})
    assert search.status_code == 200
    _assert_public(search.json())
    assert "Miracle" not in json.dumps(search.json(), ensure_ascii=False)
    comparison = home.post("/materia/clarke-compare", json={"rate": BLOCKED})
    assert comparison.status_code == 200
    _assert_public(comparison.json())
    assert state.materia_medica.remedies[-1].remedy_name == BLOCKED


def test_script_names_source_output_errors_and_variables_are_projected(
    home: TestClient, tmp_path: Path,
) -> None:
    script = tmp_path / "data" / "radionics" / "Heilt garantiert.rscript"
    script.write_text("PRINT Heilt garantiert\n", encoding="utf-8")
    home.app.state.radiworks_state.rate_repository.refresh()
    listed = home.get("/scripts")
    assert listed.status_code == 200
    _assert_public(listed.json())
    loaded = home.get("/scripts/Heilt%20garantiert")
    assert loaded.status_code == 200
    _assert_public(loaded.json())

    executed = home.post("/script/execute", json={
        "script": "Heilt garantiert = sicher\nPRINT Heilt garantiert\n"
                  "NON INTERPRETED Heilt garantiert", "seed": 7,
    })
    assert executed.status_code == 200
    _assert_public(executed.json())
    assert home.app.state.radiworks_state.rate_repository.read_script(BLOCKED) == "PRINT Heilt garantiert\n"


def test_image_analysis_api_carries_no_local_filename(home: TestClient) -> None:
    response = home.post("/images/analyze", json={"count": 1, "seed": 7})
    assert response.status_code == 200
    assert set(response.json()) == {"layers", "min", "max", "rounds", "relativeGVratio"}


def test_stickpad_analysis_and_error_are_projected_without_queueing_blocked_rate(
    home: TestClient, tmp_path: Path,
) -> None:
    catalog = tmp_path / "data" / "radionics" / "HOMEOPATHY_StickBlocked.txt"
    catalog.write_text(BLOCKED + "\n", encoding="utf-8")
    state = home.app.state.radiworks_state
    state.rate_repository.refresh()
    assert home.post("/cases", json={"name": "Stick-Fall"}).status_code == 200
    assert home.post("/stickpad/position", json={"x": 640, "y": 400}).status_code == 200

    response = home.post("/stickpad/analyze", json={"database": "HOMEOPATHY_StickBlocked"})
    assert response.status_code == 200
    public = response.json()
    _assert_public(public)
    assert public["draft"]["copyguard_verdict"] == "block"
    draft_id = public["draft"]["id"]
    assert state.draft_store.get(draft_id)["payload"]["rateObjects"][0]["nameOrRate"] == BLOCKED
    assert state.case_store.current["sessionList"][-1]["analysisResult"]["rateObjects"][0]["nameOrRate"] == BLOCKED
    _assert_public([event for event in state.event_history if event["type"] == "analysis.update"][-1])
    for path in ("/stickpad", "/analysis/current", f"/drafts/{draft_id}", "/cases/current"):
        result = home.get(path)
        assert result.status_code == 200, path
        assert BLOCKED not in json.dumps(result.json(), ensure_ascii=False), path
    assert home.post(f"/drafts/{draft_id}/transition", json={"status": "ready"}).status_code == 200
    assert home.post(f"/drafts/{draft_id}/promote").status_code == 409
    assert not home.get("/broadcast/queue").json()["queued"]

    error = home.post("/stickpad/analyze", json={"database": BLOCKED})
    assert error.status_code == 404
    _assert_public(error.json())


def test_interrupted_promotion_after_restart_keeps_blocked_text_out_of_public_state(
    tmp_path: Path,
) -> None:
    from radiworks.main import create_app

    catalog = tmp_path / "data" / "radionics"
    catalog.mkdir(parents=True)
    (catalog / "HOMEOPATHY_RecoverySafe.txt").write_text("Arnica\n", encoding="utf-8")
    app = create_app(base_dir=tmp_path, data_dir=catalog, materia_dir=tmp_path / "empty-materia")
    with TestClient(app) as client:
        assert client.post("/cases", json={"name": BLOCKED}).status_code == 200
        run = client.post("/analysis", json={"database": "HOMEOPATHY_RecoverySafe", "seed": 7})
        assert run.status_code == 200
        draft_id = run.json()["draft"]["id"]
        assert app.state.radiworks_state.draft_store.get(draft_id)["focus"]["case"] == BLOCKED
        assert client.post(f"/drafts/{draft_id}/transition", json={"status": "ready"}).status_code == 200
        app.state.radiworks_state.draft_store.begin_promotion(draft_id)

    restarted = create_app(base_dir=tmp_path, data_dir=catalog, materia_dir=tmp_path / "empty-materia")
    with TestClient(restarted) as client:
        draft = client.get(f"/drafts/{draft_id}")
        assert draft.status_code == 200
        _assert_public(draft.json())
        assert draft.json()["promotion"]["state"] == "interrupted"
        listed = client.get("/drafts")
        assert listed.status_code == 200
        assert BLOCKED not in json.dumps(listed.json(), ensure_ascii=False)
        assert client.post(f"/drafts/{draft_id}/promote").status_code == 409
        assert not client.get("/broadcast/queue").json()["queued"]


def test_public_view_keeps_distinct_values_when_redacted_keys_collide() -> None:
    from radiworks.copyguard import PUBLIC_REDACTION, public_view

    original = {
        "Heilt garantiert": {"id": "first"},
        "Diagnose sicher": {"id": "second"},
        f"{PUBLIC_REDACTION} [2]": {"id": "third"},
    }
    projected = public_view(original)

    assert len(projected) == 3
    assert projected[f"{PUBLIC_REDACTION} [2]"]["id"] == "third"
    assert sorted(value["id"] for value in projected.values()) == [
        "first", "second", "third",
    ]
    assert "Heilt garantiert" not in projected
    assert "Diagnose sicher" not in projected