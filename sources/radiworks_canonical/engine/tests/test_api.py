"""Tests: API_CONTRACT v1 (REST + WebSocket)."""

import asyncio
from copy import deepcopy
import hashlib
import threading
from datetime import datetime
from pathlib import Path
from uuid import UUID

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError

from fastapi import WebSocketDisconnect
from fastapi.testclient import TestClient

from radiworks.api import routes as routes_module
from radiworks.api.routes import BOOT_ID, STATE, WS_EVENT_HISTORY, websocket_endpoint
from radiworks.main import create_app


class DisconnectingWebSocket:
    """Minimaler WS-Doppelgänger für deterministische Handshake-Races."""

    def __init__(self, on_send=None):
        self.sent = []
        self.closed = []
        self.on_send = on_send

    async def accept(self):
        return None

    async def send_json(self, envelope):
        self.sent.append(envelope)
        if self.on_send is not None:
            self.on_send(envelope)

    async def close(self, *, code):
        self.closed.append(code)

    async def receive_text(self):
        raise WebSocketDisconnect()


def _websocket_endpoint(
    websocket,
    last_event_id=None,
    last_boot=None,
):
    state = STATE.state
    assert state is not None
    return websocket_endpoint(
        websocket,
        last_event_id,
        last_boot,
        state=state,
    )


def _assert_error(response, status_code: int, code: str) -> None:
    assert response.status_code == status_code
    assert set(response.json()) == {"error"}
    assert response.json()["error"] == {
        "code": code,
        "message": response.json()["error"]["message"],
    }
    assert isinstance(response.json()["error"]["message"], str)


def test_ping(home: TestClient):
    data = home.get("/ping").json()
    assert data["result"] == "pong"
    assert data["module"] == "radiworks.engine"
    assert data["version"]


def test_local_operator_boundary_rejects_browser_scope_headers(home: TestClient):
    response = home.get("/ping", headers={"X-Aurelia-Tenant-Id": "other-operator"})

    _assert_error(response, 400, "bad_request")


def test_analysis_uses_the_fixed_local_scope_and_rejects_payload_scope(home: TestClient):
    accepted = home.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 7})
    rejected = home.post(
        "/analysis",
        json={"database": "HOMEOPATHY_Test", "tenant_id": "other-operator"},
    )

    assert accepted.status_code == 200
    assert accepted.json()["passport"]["tenant_id"] == "local"
    assert accepted.json()["passport"]["client_id"] == "preview"
    _assert_error(rejected, 422, "validation_error")


def test_settings_get_is_observational_and_does_not_create_defaults(tmp_path: Path):
    app = create_app(base_dir=tmp_path)

    with TestClient(app) as client:
        response = client.get("/settings")

    assert response.status_code == 200
    assert response.json()["strings"]["entropy.defaultMode"] == "seeded"
    assert not (tmp_path / "config" / "Settings.json").exists()


def test_entropy_status_get_is_observational_and_does_not_create_defaults(tmp_path: Path):
    app = create_app(base_dir=tmp_path)

    with TestClient(app) as client:
        response = client.get("/entropy/status")

    assert response.status_code == 200
    assert not (tmp_path / "config" / "Settings.json").exists()


def test_case_get_routes_do_not_mutate_case_or_recent_metadata(home: TestClient):
    created = home.post("/cases", json={"name": "ReadOnlyCase"})
    assert created.status_code == 200
    assert home.post("/cases", json={"name": "CurrentCase"}).status_code == 200
    state = STATE.state
    assert state is not None
    assert state.case_store.current["name"] == "CurrentCase"
    case_path = state.case_store.cases_dir / "ReadOnlyCase.json"
    before = hashlib.sha256(case_path.read_bytes()).hexdigest()
    recent_path = state.case_store.cases_dir / "dashboardInformations.json"
    assert not recent_path.exists()

    assert home.get("/cases/ReadOnlyCase").status_code == 200
    assert home.get("/cases/ReadOnlyCase/statistics").status_code == 200

    assert hashlib.sha256(case_path.read_bytes()).hexdigest() == before
    assert not recent_path.exists()
    assert state.case_store.current["name"] == "CurrentCase"


def test_http_errors_follow_aurelia_envelope(home: TestClient):
    unknown_database = home.post("/analysis", json={"database": "NIX"})
    _assert_error(unknown_database, 404, "not_found")

    invalid_request = home.post("/analysis", json={"database": "HOMEOPATHY_Test", "max_hits": 101})
    _assert_error(invalid_request, 422, "validation_error")

    wrong_method = home.post("/ping")
    _assert_error(wrong_method, 405, "method_not_allowed")

    missing_static = home.get("/missing.txt")
    _assert_error(missing_static, 404, "not_found")

    cors_error = home.post(
        "/analysis",
        json={"database": "NIX"},
        headers={"Origin": "http://localhost:8080"},
    )
    _assert_error(cors_error, 404, "not_found")
    assert cors_error.headers["access-control-allow-origin"] == "http://localhost:8080"


def test_unexpected_http_error_does_not_leak_exception_text(tmp_path: Path):
    app = create_app(base_dir=tmp_path)

    @app.get("/test-only-boom")
    def boom():
        raise RuntimeError("secret implementation detail")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/test-only-boom")

    _assert_error(response, 500, "internal_error")
    assert "secret implementation detail" not in response.json()["error"]["message"]


def test_default_runtime_home_uses_external_override(monkeypatch, tmp_path: Path):
    runtime_home = tmp_path / "external-runtime-home"
    monkeypatch.setenv("RADIOWORKS_HOME", str(runtime_home))

    app = create_app()
    state = app.state.radiworks_state

    assert state.case_store.cases_dir == runtime_home / "cases"
    assert state.draft_store.drafts_dir == runtime_home / "drafts"
    assert state.case_store.cases_dir.exists()
    assert state.draft_store.drafts_dir.exists()


def test_external_rate_catalog_is_independent_of_runtime_home(monkeypatch, tmp_path: Path):
    runtime_home = tmp_path / "runtime"
    catalog = tmp_path / "readonly-catalog"
    catalog.mkdir()
    (catalog / "SYMBOLISM_rates.txt").write_text("Synthetic symbol rate\n", encoding="utf-8")
    monkeypatch.setenv("RADIOWORKS_HOME", str(runtime_home))
    monkeypatch.setenv("RADIOWORKS_DATA_DIR", str(catalog))

    app = create_app()
    state = app.state.radiworks_state
    with TestClient(app) as client:
        assert "SYMBOLISM_rates" in client.get("/databases").json()["databases"]

    assert state.case_store.cases_dir == runtime_home / "cases"
    assert state.rate_repository.data_dir == catalog


def test_external_catalog_supports_expected_group_prefixes(monkeypatch, tmp_path: Path):
    runtime_home = tmp_path / "runtime"
    catalog = tmp_path / "readonly-catalog"
    catalog.mkdir()
    prefixes = [
        "HOMEOPATHY",
        "BIOLOGICAL",
        "SYMBOLISM",
        "ESSENCES",
        "CHEMICAL",
        "ENERGY",
        "AGRICULTURE",
        "ANALYSIS",
    ]
    for prefix in prefixes:
        (catalog / f"{prefix}_preview.txt").write_text(
            f"Synthetic {prefix} rate\n", encoding="utf-8"
        )
    monkeypatch.setenv("RADIOWORKS_HOME", str(runtime_home))
    monkeypatch.setenv("RADIOWORKS_DATA_DIR", str(catalog))

    with TestClient(create_app()) as client:
        databases = client.get("/databases").json()["databases"]
        assert set(databases) == {f"{prefix}_preview" for prefix in prefixes}
        assert client.post(
            "/analysis", json={"database": "SYMBOLISM_preview", "seed": 44}
        ).status_code == 200
        assert client.post(
            "/analysis", json={"database": "SYMBOLISM", "seed": 44}
        ).status_code == 200


def test_overlapping_apps_keep_their_bound_state(home: TestClient, tmp_path: Path):
    state_a = STATE.state
    assert state_a is not None
    app_b = create_app(base_dir=tmp_path / "second-app")

    with TestClient(app_b) as second:
        assert second.get("/ping").status_code == 200
        assert home.get("/broadcast/queue").status_code == 200

    assert STATE.state is state_a
    response = home.post(
        "/broadcast",
        json={"signature": "APP A", "seconds": 1, "multiplier": 1},
    )
    assert response.status_code == 200
    state_a.broadcast.stop_all()


def test_non_lifo_lifespans_do_not_restore_shutdown_state(tmp_path: Path):
    app_a = create_app(base_dir=tmp_path / "app-a")
    app_b = create_app(base_dir=tmp_path / "app-b")
    state_a = app_a.state.radiworks_state
    state_b = app_b.state.radiworks_state
    client_a = TestClient(app_a)
    client_b = TestClient(app_b)
    a_open = b_open = False

    try:
        client_a.__enter__()
        a_open = True
        client_b.__enter__()
        b_open = True
        assert STATE.state is state_b

        client_a.__exit__(None, None, None)
        a_open = False
        assert state_a.broadcast._shutdown is True
        assert STATE.state is state_b
        assert client_b.get("/broadcast/queue").status_code == 200

        client_b.__exit__(None, None, None)
        b_open = False
        assert state_b.broadcast._shutdown is True
        assert STATE.state is None
    finally:
        if b_open:
            client_b.__exit__(None, None, None)
        if a_open:
            client_a.__exit__(None, None, None)


def test_manifest_is_kernel_abi_v1(home: TestClient):
    m = home.get("/manifest").json()
    for field in ("id", "version", "hash", "input_schema", "output_schema", "class", "repro", "budget", "entry", "copy"):
        assert field in m, field
    assert m["class"] == "cpu"
    assert m["repro"] == "seeded"
    assert m["hash"].startswith("sha256:")
    assert m["isHardwareActivatable"] is False


def test_manifest_matches_local_analysis_scope_and_passport(home: TestClient):
    manifest = home.get("/manifest").json()
    input_schema = manifest["input_schema"]
    assert input_schema["additionalProperties"] is False
    assert "tenant_id" not in input_schema["properties"]
    assert "client_id" not in input_schema["properties"]
    assert "null" in input_schema["properties"]["mode"]["type"]

    response = home.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 7, "mode": None})
    assert response.status_code == 200
    passport = response.json()["passport"]
    passport_schema = manifest["output_schema"]["properties"]["passport"]
    assert set(passport).issubset(passport_schema["properties"])
    assert set(passport_schema["required"]).issubset(passport)
    assert {"tenant_id", "client_id"}.issubset(passport_schema["required"])
    assert passport["tenant_id"] == "local"
    assert passport["client_id"] == "preview"

def test_manifest_describes_complete_analysis_result_and_draft(home: TestClient):
    output = home.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 17})
    assert output.status_code == 200
    body = output.json()
    schemas = home.get("/manifest").json()["output_schema"]
    assert set(body) == set(schemas["properties"]) == set(schemas["required"])
    assert schemas["additionalProperties"] is False

    passport = body["passport"]
    passport_schema = schemas["properties"]["passport"]
    assert set(passport) == set(passport_schema["properties"]) == set(passport_schema["required"])
    assert passport_schema["additionalProperties"] is False

    result = body["result"]
    result_schema = schemas["properties"]["result"]
    assert set(result) == set(result_schema["properties"]) == set(result_schema["required"])
    assert result_schema["additionalProperties"] is False
    assert result["rateObjects"]
    rate_schema = result_schema["properties"]["rateObjects"]["items"]
    assert set(result["rateObjects"][0]) == set(rate_schema["properties"]) == set(rate_schema["required"])
    assert rate_schema["additionalProperties"] is False

    draft = body["draft"]
    draft_schema = schemas["properties"]["draft"]
    assert set(draft) == set(draft_schema["properties"]) == set(draft_schema["required"])
    assert draft_schema["additionalProperties"] is False
    assert "payload" not in draft
    assert draft["scope"] == {"tenant_id": "local", "client_id": "preview", "job_id": "default"}
    assert set(draft["scope"]) == set(draft_schema["properties"]["scope"]["properties"])
    assert draft["job_id"] == "default"

    assert home.post("/cases", json={"name": "SchemaCase"}).status_code == 200
    linked = home.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 18})
    assert linked.status_code == 200
    linked_draft = linked.json()["draft"]
    assert set(linked_draft) == set(draft_schema["required"])
    assert isinstance(linked_draft["sessionId"], str)
    assert linked_draft["focus"]["case"] == "SchemaCase"


def _assert_manifest_schema_subset(value, schema: dict, path: str = "$") -> None:
    """Fail closed for the JSON Schema keywords used by this local ABI."""
    supported = {
        "type", "required", "properties", "additionalProperties", "items",
        "enum", "const", "description", "format",
    }
    assert not set(schema) - supported, (path, set(schema) - supported)
    kinds = {
        "object": lambda item: isinstance(item, dict),
        "array": lambda item: isinstance(item, list),
        "string": lambda item: isinstance(item, str),
        "integer": lambda item: type(item) is int,
        "boolean": lambda item: type(item) is bool,
        "null": lambda item: item is None,
    }
    declared = schema.get("type", [])
    if isinstance(declared, str):
        declared = [declared]
    assert all(kind in kinds for kind in declared), (path, declared)
    if declared:
        assert any(kinds[kind](value) for kind in declared), (path, value, declared)
    if "enum" in schema:
        assert value in schema["enum"], (path, value)
    if "const" in schema:
        assert value == schema["const"], (path, value)
    if "format" in schema:
        assert isinstance(value, str), (path, value)
        if schema["format"] == "uuid":
            assert str(UUID(value)) == value, (path, value)
        elif schema["format"] == "date-time":
            assert datetime.fromisoformat(value).utcoffset() is not None, (path, value)
        else:
            raise AssertionError((path, schema["format"]))
    if isinstance(value, dict):
        assert set(schema.get("required", [])).issubset(value), path
        properties = schema.get("properties", {})
        for key, item in value.items():
            child = properties.get(key, schema.get("additionalProperties", True))
            assert child is not False, (path, key)
            if isinstance(child, dict):
                _assert_manifest_schema_subset(item, child, f"{path}.{key}")
    elif isinstance(value, list) and "items" in schema:
        for index, item in enumerate(value):
            _assert_manifest_schema_subset(item, schema["items"], f"{path}[{index}]")


def test_manifest_analysis_output_types_and_formats(home: TestClient, tmp_path: Path):
    manifest = home.get("/manifest").json()
    schema = manifest["output_schema"]
    Draft202012Validator.check_schema(manifest["input_schema"])
    Draft202012Validator.check_schema(schema)
    checker = FormatChecker()
    assert {"uuid", "date-time"}.issubset(checker.checkers)
    validator = Draft202012Validator(schema, format_checker=checker)
    input_validator = Draft202012Validator(manifest["input_schema"], format_checker=checker)
    input_validator.validate({"database": "HOMEOPATHY_Test", "seed": 21, "mode": None})
    with pytest.raises(ValidationError):
        input_validator.validate({"database": "HOMEOPATHY_Test", "tenant_id": "foreign"})
    with pytest.raises(ValidationError):
        input_validator.validate({"database": "HOMEOPATHY_Test", "mode": "invalid"})
    passport_schema = schema["properties"]["passport"]
    draft_schema = schema["properties"]["draft"]
    assert passport_schema["properties"]["run_id"]["format"] == "uuid"
    assert draft_schema["properties"]["id"]["format"] == "uuid"
    assert draft_schema["properties"]["source_run_id"]["format"] == "uuid"
    for name in ("created", "updated", "ttl_hint"):
        assert draft_schema["properties"][name]["format"] == "date-time"

    safe = home.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 21})
    assert safe.status_code == 200
    _assert_manifest_schema_subset(safe.json(), schema)
    validator.validate(safe.json())
    bad_uuid = deepcopy(safe.json())
    bad_uuid["passport"]["run_id"] = "not-a-uuid"
    with pytest.raises(ValidationError):
        validator.validate(bad_uuid)
    bad_time = deepcopy(safe.json())
    bad_time["draft"]["created"] = "2026-09-29T12:00:00"
    with pytest.raises(ValidationError):
        validator.validate(bad_time)

    assert home.post("/cases", json={"name": "SchemaTypesCase"}).status_code == 200
    linked = home.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 22})
    assert linked.status_code == 200
    _assert_manifest_schema_subset(linked.json(), schema)
    validator.validate(linked.json())
    assert linked.json()["draft"]["sessionId"] is not None

    blocked_file = tmp_path / "data" / "radionics" / "HOMEOPATHY_SchemaBlocked.txt"
    blocked_file.write_text("Heilt garantiert\n", encoding="utf-8")
    home.app.state.radiworks_state.rate_repository.refresh()
    blocked = home.post("/analysis", json={"database": "HOMEOPATHY_SchemaBlocked", "seed": 23})
    assert blocked.status_code == 200
    assert blocked.json()["draft"]["copyguard_verdict"] == "block"
    _assert_manifest_schema_subset(blocked.json(), schema)
    validator.validate(blocked.json())


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


def test_case_name_rejects_path_traversal(home: TestClient):
    state = STATE.state
    assert state is not None

    response = home.post("/cases", json={"name": "../drafts/poc"})

    assert response.status_code == 422
    assert not (state.draft_store.drafts_dir / "poc.json").exists()


def test_analysis_max_hits_contract(home: TestClient):
    for max_hits in (100, 1000):
        response = home.post(
            "/analysis", json={"database": "HOMEOPATHY_Test", "seed": 7, "max_hits": max_hits}
        )
        assert response.status_code == 200

    invalid = home.post(
        "/analysis", json={"database": "HOMEOPATHY_Test", "seed": 7, "max_hits": 101}
    )
    assert invalid.status_code == 422


def test_image_broadcast_rejects_unsafe_multiplier(home: TestClient):
    state = STATE.state
    assert state is not None

    response = home.post("/images/broadcast", json={"md5": "synthetic", "multiplier": -6765})

    assert response.status_code == 422
    assert state.broadcast.queue_state()["queued"] == []
    assert state.broadcast.queue_state()["active"] == []


def test_image_broadcast_rejects_non_hash_text_without_queueing(home: TestClient):
    state = STATE.state
    assert state is not None

    response = home.post("/images/broadcast", json={"md5": "not-a-hash"})

    _assert_error(response, 422, "validation_error")
    assert state.broadcast.queue_state()["queued"] == []
    assert state.broadcast.queue_state()["active"] == []


def test_image_broadcast_accepts_webapp_sha256_hash(home: TestClient):
    response = home.post(
        "/images/broadcast",
        json={"md5": "a" * 64, "seconds": 1},
    )

    assert response.status_code == 200
    assert response.json()["signature"] == f"IMAGE:{'a' * 64}"


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


def test_broadcast_direct_and_stop(home: TestClient, monkeypatch):
    state = STATE.state
    assert state is not None
    monkeypatch.setattr(state.broadcast, "_start_thread", lambda: None)
    sequence_before = state._event_seq

    queued = home.post(
        "/broadcast", json={"signature": "MANUELL 55 C 30", "seconds": 2, "multiplier": 3}
    ).json()
    assert queued["signature"] == "MANUELL 55 C 30"
    assert queued["broadcastId"]

    state.broadcast._promote_from_queue()
    starts = [
        envelope
        for envelope in state.event_history
        if envelope["id"] > sequence_before
        and envelope["type"] == "broadcast.progress"
        and envelope["payload"].get("started")
    ]
    assert len(starts) == 1
    assert starts[0]["payload"]["broadcastId"] == queued["broadcastId"]

    assert home.delete("/broadcast/all").json() == {"stopped": "all"}
    assert state.broadcast.queue_state()["active"] == []


def test_auto_mode_rest_contract(home: TestClient, monkeypatch):
    state = STATE.state
    assert state is not None and state.auto is not None
    ensure_calls = []

    def ensure_running():
        ensure_calls.append(state.auto.snapshot()["enabled"])

    monkeypatch.setattr(state.broadcast, "ensure_running", ensure_running)

    initial = home.get("/auto-mode").json()
    assert initial["enabled"] is False

    enabled = home.post(
        "/auto-mode/on",
        json={"database": "HOMEOPATHY_Test", "multiplier": 7},
    ).json()
    assert enabled == {
        "enabled": True,
        "database": "HOMEOPATHY_Test",
        "multiplier": 7,
        "caseGv": 0,
        "runs": 0,
        "seriesLength": 0,
        "average": None,
    }
    assert ensure_calls == [True]
    assert home.get("/auto-mode").json() == enabled
    assert state.event_history[-1]["type"] == "auto.mode"
    assert state.event_history[-1]["payload"] == enabled

    disabled = home.post("/auto-mode/off").json()
    assert disabled["enabled"] is False
    assert state.event_history[-1]["type"] == "auto.mode"
    assert state.event_history[-1]["payload"] == disabled


def test_auto_mode_real_manager_stays_running_when_enabled(home: TestClient):
    state = STATE.state
    assert state is not None and state.auto is not None
    tick_seen = threading.Event()
    original_tick = state.broadcast._on_tick

    def observe_tick():
        assert original_tick is not None
        original_tick()
        tick_seen.set()

    state.broadcast._on_tick = observe_tick
    enabled = home.post(
        "/auto-mode/on",
        json={"database": "HOMEOPATHY_Test", "multiplier": 1},
    )
    assert enabled.status_code == 200
    thread = state.broadcast._thread
    assert thread is not None
    assert tick_seen.wait(2), "Auto-Modus-Uhr hat aus dem Leerlauf nicht getaktet"
    assert thread.is_alive()
    assert state.auto.snapshot()["runs"] >= 1

    home.post("/auto-mode/off")
    state.broadcast.stop_all()
    thread.join(1)
    assert not thread.is_alive()


def test_auto_mode_request_validation(home: TestClient):
    assert home.post("/auto-mode/on", json={}).status_code == 422
    assert home.post(
        "/auto-mode/on",
        json={"database": "NIX", "multiplier": 1},
    ).status_code == 404
    for multiplier in (0, 1001):
        response = home.post(
            "/auto-mode/on",
            json={"database": "HOMEOPATHY_Test", "multiplier": multiplier},
        )
        assert response.status_code == 422
    assert home.get("/auto-mode").json()["enabled"] is False


def test_materia_search(home: TestClient):
    result = home.get("/materiaMedicaSearch", params={"query": "Haarausfall"}).json()
    assert result["searchResults"], "Abrotanum sollte 'Haarausfall' treffen"
    top = result["searchResults"][0]
    assert "Abrotanum" in top["remedyName"]
    assert "<b>" in top["clinical"][0] or top["clinical"]


def test_materia_search_short_query_empty(home: TestClient):
    assert home.get("/materiaMedicaSearch", params={"query": "Ha"}).json()["searchResults"] == []


def test_websocket_channel_starts_with_hello_then_business_event(home: TestClient):
    with home.websocket_connect("/ws") as ws:
        hello = ws.receive_json()
        home.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 8})
        message = ws.receive_json()

    assert hello["v"] == 1
    assert hello["id"] == 0
    assert hello["boot"] == BOOT_ID
    assert hello["type"] == "server.hello"
    assert hello["payload"] == {"cursor": 0, "latestEventId": 0}
    assert hello["ts"] > 0
    assert message["v"] == 1
    assert message["type"] in {"analysis.update", "analysis.progress"}
    assert message["id"] > 0
    assert message["boot"] == BOOT_ID
    assert message["ts"] > 0


def test_websocket_control_events_do_not_advance_history(home: TestClient):
    state = STATE.state
    assert state is not None
    sequence_before = state._event_seq
    history_before = list(state.event_history)

    with home.websocket_connect("/ws?last_event_id=999999") as ws:
        hello = ws.receive_json()
        gap = ws.receive_json()
        ws.send_text("ping")
        pong = ws.receive_json()

    assert hello["type"] == "server.hello"
    assert gap["type"] == "server.replay_gap"
    assert gap["id"] == 0
    assert pong == {
        "v": 1,
        "id": 0,
        "boot": BOOT_ID,
        "type": "pong",
        "payload": {},
        "ts": pong["ts"],
    }
    assert pong["ts"] > 0
    assert state._event_seq == sequence_before
    assert list(state.event_history) == history_before


def test_websocket_replay_uses_event_id_and_boot(home: TestClient):
    state = STATE.state
    assert state is not None
    state.publish("test.one", {"value": 1})
    state.publish("test.two", {"value": 2})

    with home.websocket_connect(f"/ws?last_event_id=1&last_boot={BOOT_ID}") as ws:
        assert ws.receive_json()["type"] == "server.hello"
        replayed = ws.receive_json()
    assert replayed["type"] == "test.two"
    assert replayed["id"] == 2

    with home.websocket_connect("/ws?last_event_id=999999&last_boot=old-boot") as ws:
        assert ws.receive_json()["type"] == "server.hello"
        first = ws.receive_json()
        second = ws.receive_json()
    assert [first["type"], second["type"]] == ["test.one", "test.two"]
    assert [first["id"], second["id"]] == [1, 2]


def test_websocket_reports_retained_history_gap(home: TestClient):
    state = STATE.state
    assert state is not None
    for index in range(WS_EVENT_HISTORY + 3):
        state.publish("test.history", {"index": index})

    websocket = DisconnectingWebSocket()
    asyncio.run(
        _websocket_endpoint(
            websocket,
            last_event_id=0,
            last_boot=BOOT_ID,
        )
    )

    assert websocket.sent[0]["type"] == "server.hello"
    gap = websocket.sent[1]
    assert gap["type"] == "server.replay_gap"
    assert gap["id"] == 0
    assert gap["payload"] == {
        "reason": "history-truncated",
        "requestedLastEventId": 0,
        "oldestAvailableEventId": 4,
        "latestEventId": WS_EVENT_HISTORY + 3,
    }
    business = [envelope for envelope in websocket.sent if envelope["id"] > 0]
    assert len(business) == WS_EVENT_HISTORY
    assert business[0]["id"] == 4
    assert business[-1]["id"] == WS_EVENT_HISTORY + 3


def test_websocket_reports_future_cursor_and_replays_available_history(home: TestClient):
    state = STATE.state
    assert state is not None
    state.publish("test.current", {"value": 1})

    websocket = DisconnectingWebSocket()
    asyncio.run(
        _websocket_endpoint(
            websocket,
            last_event_id=999,
            last_boot=BOOT_ID,
        )
    )

    assert [envelope["type"] for envelope in websocket.sent] == [
        "server.hello",
        "server.replay_gap",
        "test.current",
    ]
    assert websocket.sent[1]["payload"]["reason"] == "cursor-ahead"
    assert websocket.sent[1]["payload"]["latestEventId"] == 1


def test_websocket_handshake_pending_is_bounded(home: TestClient):
    state = STATE.state
    assert state is not None

    def flood_during_hello(envelope):
        if envelope["type"] != "server.hello":
            return
        for index in range(routes_module.WS_HANDSHAKE_QUEUE + 1):
            state.publish("test.flood", {"index": index})

    websocket = DisconnectingWebSocket(flood_during_hello)
    asyncio.run(_websocket_endpoint(websocket))

    assert websocket.closed == [1013]
    assert [envelope["type"] for envelope in websocket.sent] == ["server.hello"]
    assert websocket not in state._ws_pending
    assert websocket not in state._ws_clients


def test_websocket_handshake_drain_has_cumulative_bound(home: TestClient):
    state = STATE.state
    assert state is not None
    published = 0

    def publish_after_every_send(_envelope):
        nonlocal published
        published += 1
        state.publish("test.continuous", {"index": published})

    websocket = DisconnectingWebSocket(publish_after_every_send)
    asyncio.run(_websocket_endpoint(websocket))

    assert websocket.closed == [1013]
    business = [envelope for envelope in websocket.sent if envelope["id"] > 0]
    assert len(business) == routes_module.WS_HANDSHAKE_QUEUE
    assert websocket not in state._ws_pending
    assert websocket not in state._ws_clients


def test_websocket_accept_timeout_cleans_unregistered_client(home: TestClient, monkeypatch):
    state = STATE.state
    assert state is not None
    monkeypatch.setattr(routes_module, "WS_HANDSHAKE_TIMEOUT_S", 0.01)

    class StalledAcceptWebSocket:
        def __init__(self):
            self.release = asyncio.Event()
            self.closed = []

        async def accept(self):
            await self.release.wait()

        async def send_json(self, _envelope):
            raise AssertionError("Handshake must not send before accept completes")

        async def close(self, *, code):
            self.closed.append(code)
            self.release.set()

        async def receive_text(self):
            raise AssertionError("Handshake must not receive before accept completes")

    websocket = StalledAcceptWebSocket()
    asyncio.run(_websocket_endpoint(websocket))

    assert websocket.closed == [1013]
    assert websocket not in state._ws_pending
    assert websocket not in state._ws_clients


def test_websocket_handshake_send_timeout_cleans_client(home: TestClient, monkeypatch):
    state = STATE.state
    assert state is not None
    monkeypatch.setattr(routes_module, "WS_SEND_TIMEOUT_S", 0.01)

    class StalledWebSocket:
        def __init__(self):
            self.release = asyncio.Event()
            self.closed = []

        async def accept(self):
            return None

        async def send_json(self, _envelope):
            await self.release.wait()

        async def close(self, *, code):
            self.closed.append(code)
            self.release.set()

        async def receive_text(self):
            raise WebSocketDisconnect()

    websocket = StalledWebSocket()
    asyncio.run(_websocket_endpoint(websocket))

    assert websocket.closed == [1011]
    assert websocket not in state._ws_pending
    assert websocket not in state._ws_clients


def test_websocket_live_sender_timeout_cleans_client(home: TestClient, monkeypatch):
    state = STATE.state
    assert state is not None
    monkeypatch.setattr(routes_module, "WS_SEND_TIMEOUT_S", 0.01)

    class StalledWebSocket:
        def __init__(self):
            self.closed = []
            self.closed_event = asyncio.Event()

        async def send_json(self, _envelope):
            await asyncio.Event().wait()

        async def close(self, *, code):
            self.closed.append(code)
            self.closed_event.set()

    websocket = StalledWebSocket()

    async def scenario():
        with state._event_lock:
            state._ws_clients.add(websocket)
        state._schedule_send({"v": 1, "id": 1, "type": "test.live", "payload": {}}, (websocket,))
        await asyncio.wait_for(websocket.closed_event.wait(), timeout=0.5)
        await asyncio.sleep(0)

    asyncio.run(scenario())

    assert websocket.closed == [1011]
    assert websocket not in state._ws_clients
    assert websocket not in state._ws_queues
    assert websocket not in state._ws_senders


def test_websocket_hello_cursor_prevents_replaying_skipped_history(home: TestClient):
    state = STATE.state
    assert state is not None
    state.publish("test.before-connect", {"value": 1})

    first = DisconnectingWebSocket()
    asyncio.run(_websocket_endpoint(first))
    assert [envelope["type"] for envelope in first.sent] == ["server.hello"]
    cursor = first.sent[0]["payload"]["cursor"]
    assert cursor == 1

    reconnected = DisconnectingWebSocket()
    asyncio.run(
        _websocket_endpoint(
            reconnected,
            last_event_id=cursor,
            last_boot=BOOT_ID,
        )
    )
    assert [envelope["type"] for envelope in reconnected.sent] == ["server.hello"]


def test_websocket_handshake_buffers_event_published_during_hello(home: TestClient):
    state = STATE.state
    assert state is not None

    def on_send(envelope):
        if envelope["type"] == "server.hello":
            state.publish("test.during-hello", {"value": 1})

    websocket = DisconnectingWebSocket(on_send)
    asyncio.run(_websocket_endpoint(websocket))

    assert [envelope["type"] for envelope in websocket.sent] == [
        "server.hello",
        "test.during-hello",
    ]
    assert websocket.sent[1]["id"] == 1


def test_websocket_replay_finishes_before_buffered_live_event(home: TestClient):
    state = STATE.state
    assert state is not None
    state.publish("test.one", {"value": 1})
    state.publish("test.two", {"value": 2})
    published_live = False

    def on_send(envelope):
        nonlocal published_live
        if envelope.get("id") == 1 and not published_live:
            published_live = True
            state.publish("test.three", {"value": 3})

    websocket = DisconnectingWebSocket(on_send)
    asyncio.run(
        _websocket_endpoint(
            websocket,
            last_event_id=999999,
            last_boot="old-boot",
        )
    )

    business = [envelope for envelope in websocket.sent if envelope["id"] > 0]
    assert [envelope["id"] for envelope in business] == [1, 2, 3]
    assert [envelope["type"] for envelope in business] == [
        "test.one",
        "test.two",
        "test.three",
    ]


def test_slow_websocket_client_does_not_block_fast_client(home: TestClient):
    state = STATE.state
    assert state is not None

    async def scenario():
        slow_release = asyncio.Event()
        fast_received = asyncio.Event()

        class SlowClient:
            async def send_json(self, _envelope):
                await slow_release.wait()

            async def close(self, **_kwargs):
                slow_release.set()

        class FastClient:
            def __init__(self):
                self.sent = []

            async def send_json(self, envelope):
                self.sent.append(envelope)
                if len(self.sent) == 2:
                    fast_received.set()

            async def close(self, **_kwargs):
                return None

        slow = SlowClient()
        fast = FastClient()
        with state._event_lock:
            state._ws_clients.update((slow, fast))
        first = {"v": 1, "id": 1, "boot": BOOT_ID, "type": "one", "payload": {}, "ts": 1}
        second = {"v": 1, "id": 2, "boot": BOOT_ID, "type": "two", "payload": {}, "ts": 2}

        try:
            state._schedule_send(first, (slow, fast))
            state._schedule_send(second, (slow, fast))
            await asyncio.wait_for(fast_received.wait(), timeout=1)
            assert [envelope["id"] for envelope in fast.sent] == [1, 2]
            assert len(state._ws_senders) == 2
        finally:
            state._remove_ws_client(slow)
            state._remove_ws_client(fast)
            await asyncio.sleep(0)

    asyncio.run(scenario())


def test_websocket_shutdown_waits_for_overflow_tasks(home: TestClient):
    state = STATE.state
    assert state is not None

    async def scenario():
        class OverflowClient:
            def __init__(self):
                self.closed = []

            async def send_json(self, _envelope):
                return None

            async def close(self, *, code):
                self.closed.append(code)

        client = OverflowClient()
        with state._event_lock:
            state._ws_clients.add(client)
        for event_id in range(routes_module.WS_CLIENT_QUEUE + 1):
            state._schedule_send(
                {
                    "v": 1,
                    "id": event_id + 1,
                    "boot": BOOT_ID,
                    "type": "overflow",
                    "payload": {},
                    "ts": 1,
                },
                (client,),
            )
        tracked = tuple(state._ws_tasks)
        assert tracked

        await state.shutdown_websockets()

        assert all(task.done() for task in tracked)
        assert state._ws_tasks == set()
        assert state._ws_clients == set()
        assert state._ws_senders == {}

    asyncio.run(scenario())


def test_websocket_shutdown_does_not_wait_for_non_cooperative_close(
    home: TestClient,
    monkeypatch,
):
    state = STATE.state
    assert state is not None
    monkeypatch.setattr(routes_module, "WS_SHUTDOWN_TIMEOUT_S", 0.05)

    async def scenario():
        close_started = asyncio.Event()
        release_close = asyncio.Event()

        class NonCooperativeClient:
            async def close(self, **_kwargs):
                close_started.set()
                while not release_close.is_set():
                    try:
                        await release_close.wait()
                    except asyncio.CancelledError:
                        pass

        client = NonCooperativeClient()
        with state._event_lock:
            state._ws_clients.add(client)
        shutdown = asyncio.create_task(state.shutdown_websockets())

        try:
            await asyncio.wait_for(close_started.wait(), timeout=1)
            await asyncio.wait_for(asyncio.shield(shutdown), timeout=0.2)
        finally:
            release_close.set()
            await asyncio.wait_for(shutdown, timeout=1)

    asyncio.run(scenario())


def test_static_webapp_mounted(home: TestClient):
    response = home.get("/index.html")
    assert response.status_code == 200
    assert "RadiWorks" in response.text


def test_passport_replay_and_copyguard_match_draft(home: TestClient):
    first = home.post(
        "/analysis", json={"database": "HOMEOPATHY_Test", "seed": 991}
    ).json()
    passport = first["passport"]
    draft = home.get(f"/drafts/{first['draft']['id']}").json()

    assert passport["seed"] == 991
    assert passport["replayable"] is True
    assert passport["seed_scheme"] == "effective-v2"
    assert passport["copyguard_digest"] == draft["copyguard_digest"]

    replay = home.post(
        "/analysis",
        json={"database": "HOMEOPATHY_Test", "seed": passport["seed"]},
    ).json()
    assert replay["result"] == first["result"]


def test_omitted_seed_uses_effective_zero_and_stochastic_is_not_replayable(home: TestClient):
    omitted = home.post("/analysis", json={"database": "HOMEOPATHY_Test"}).json()
    assert omitted["passport"]["seed"] == 0
    assert omitted["passport"]["replayable"] is True

    state = STATE.state
    assert state is not None
    state.random_org._http_get = None
    state.entropy_feed.feed([123])
    stochastic = home.post(
        "/analysis",
        json={"database": "HOMEOPATHY_Test", "mode": "stochastic"},
    ).json()
    assert stochastic["passport"]["seed"] is None
    assert stochastic["passport"]["replayable"] is False


def test_entropy_default_mode_rejects_invalid_values(home: TestClient):
    assert home.put(
        "/settings", json={"strings": {"entropy.defaultMode": "invalid"}}
    ).status_code == 422
    assert home.get("/settings").json()["strings"]["entropy.defaultMode"] == "seeded"


def test_corrupt_entropy_setting_fails_consistently(home: TestClient):
    state = STATE.state
    assert state is not None
    settings = state.settings_store.load("Settings")
    settings.set_string("entropy.defaultMode", "invalid")

    assert home.get("/entropy/status").status_code == 422
    assert home.post("/gv", json={}).status_code == 422
    assert home.post("/analysis", json={"database": "HOMEOPATHY_Test"}).status_code == 422
    assert home.post(
        "/analysis", json={"database": "HOMEOPATHY_Test", "mode": "seeded"}
    ).status_code == 200
