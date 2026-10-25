from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from core.compliance.runtime_manifest import (
    DEFAULT_ERASURE_GATE_TOKEN,
    RuntimeManifestService,
)


def test_register_client_safe_view_strips_pii(tmp_path: Path) -> None:
    service = RuntimeManifestService(tmp_path)
    client = service.get_or_create_client(
        {
            "first_name": "Klaus",
            "last_name": "Mustermann",
            "birth_date": "09041966",
            "birth_place": "Augsburg",
        }
    )

    safe = service.list_clients_safe()

    assert client["client_id"].startswith("cli-")
    assert safe == [
        {
            "client_id": client["client_id"],
            "created_at": client["created_at"],
            "updated_at": client["updated_at"],
        }
    ]
    assert "Klaus" not in str(safe)
    assert "Mustermann" not in str(safe)


def test_register_artifact_creates_session_artifact_and_audit(tmp_path: Path) -> None:
    service = RuntimeManifestService(tmp_path)
    artifact_file = tmp_path / "reports" / "bericht.html"
    artifact_file.parent.mkdir()
    artifact_file.write_text("report", encoding="utf-8")

    artifact = service.register_artifact(
        {
            "first_name": "Klaus",
            "last_name": "Mustermann",
            "birth_date": "09041966",
            "birth_place": "Augsburg",
        },
        artifact_type="html",
        path=artifact_file,
        label="Deutung",
        session_id="sess-test",
        focus="Bronchien",
        config={"command": "interpretation"},
    )

    assert artifact["artifact_id"].startswith("art-")
    assert service.load_store("artifacts")["artifacts"][0]["path"] == str(artifact_file)
    assert service.load_store("sessions")["sessions"][0]["session_id"] == "sess-test"
    assert any(e["action"] == "artifact_register" for e in service.load_store("audit_log")["entries"])


def test_erasure_manifest_is_non_destructive_and_execute_is_gated(tmp_path: Path) -> None:
    service = RuntimeManifestService(tmp_path)
    artifact_file = tmp_path / "reports" / "bericht.html"
    artifact_file.parent.mkdir()
    artifact_file.write_text("report", encoding="utf-8")
    artifact = service.register_artifact(
        {
            "first_name": "Klaus",
            "last_name": "Mustermann",
            "birth_date": "09041966",
            "birth_place": "Augsburg",
        },
        artifact_type="html",
        path=artifact_file,
        label="Deutung",
        session_id="sess-test",
    )
    client_id = artifact["client_id"]

    manifest = service.erasure_manifest(client_id)

    assert manifest["client_entry_present"] is True
    assert manifest["gated"] is True
    assert manifest["artifacts"][0]["path"] == str(artifact_file)
    assert artifact_file.exists()

    with pytest.raises(ValueError, match="Gate"):
        service.execute_erasure(client_id, gate_token="WRONG")

    result = service.execute_erasure(client_id, gate_token=DEFAULT_ERASURE_GATE_TOKEN)

    assert result["outcome"] == "ok"
    assert result["removed_clients"] == 1
    assert result["removed_sessions"] == 1
    assert result["removed_artifacts"] == 1
    assert result["removed_files"] == 1
    assert not artifact_file.exists()
    assert service.list_clients_safe() == []


def test_append_audit_defaults_to_system_actor_but_is_overridable(tmp_path: Path) -> None:
    service = RuntimeManifestService(tmp_path)

    default_entry = service.append_audit(
        action="test_action", client_id="cli-x", entity_type="client", entity_id="cli-x"
    )
    custom_entry = service.append_audit(
        action="test_action",
        client_id="cli-x",
        entity_type="client",
        entity_id="cli-x",
        actor="operator-1",
    )

    assert default_entry["actor"] == "system"
    assert custom_entry["actor"] == "operator-1"


def test_find_expired_clients_uses_last_activity_threshold(tmp_path: Path) -> None:
    service = RuntimeManifestService(tmp_path)
    old_client = service.get_or_create_client(
        {
            "first_name": "Alt",
            "last_name": "Klient",
            "birth_date": "01011950",
            "birth_place": "Berlin",
        }
    )
    fresh_client = service.get_or_create_client(
        {
            "first_name": "Neu",
            "last_name": "Klient",
            "birth_date": "01011990",
            "birth_place": "Berlin",
        }
    )

    store = service.load_store("clients")
    for entry in store["clients"]:
        if entry["client_id"] == old_client["client_id"]:
            stale_ts = (datetime.now(UTC) - timedelta(days=400)).isoformat().replace("+00:00", "Z")
            entry["created_at"] = stale_ts
            entry["updated_at"] = stale_ts
    service.save_store("clients", store)

    expired = service.find_expired_clients(retention_days=365)

    assert old_client["client_id"] in expired
    assert fresh_client["client_id"] not in expired


def test_purge_expired_dry_run_does_not_delete(tmp_path: Path) -> None:
    service = RuntimeManifestService(tmp_path)
    client = service.get_or_create_client(
        {
            "first_name": "Alt",
            "last_name": "Klient",
            "birth_date": "01011950",
            "birth_place": "Berlin",
        }
    )
    store = service.load_store("clients")
    stale_ts = (datetime.now(UTC) - timedelta(days=400)).isoformat().replace("+00:00", "Z")
    for entry in store["clients"]:
        entry["created_at"] = stale_ts
        entry["updated_at"] = stale_ts
    service.save_store("clients", store)

    candidates = service.purge_expired(retention_days=365, dry_run=True)

    assert candidates == [client["client_id"]]
    assert service.list_clients_safe() != []
    audit_entries = service.load_store("audit_log")["entries"]
    assert any(e["action"] == "retention_purge_dry_run" for e in audit_entries)


def test_purge_expired_removes_stale_clients_and_keeps_fresh_ones(tmp_path: Path) -> None:
    service = RuntimeManifestService(tmp_path)
    stale = service.get_or_create_client(
        {
            "first_name": "Alt",
            "last_name": "Klient",
            "birth_date": "01011950",
            "birth_place": "Berlin",
        }
    )
    fresh = service.get_or_create_client(
        {
            "first_name": "Neu",
            "last_name": "Klient",
            "birth_date": "01011990",
            "birth_place": "Berlin",
        }
    )
    store = service.load_store("clients")
    stale_ts = (datetime.now(UTC) - timedelta(days=400)).isoformat().replace("+00:00", "Z")
    for entry in store["clients"]:
        if entry["client_id"] == stale["client_id"]:
            entry["created_at"] = stale_ts
            entry["updated_at"] = stale_ts
    service.save_store("clients", store)

    purged = service.purge_expired(retention_days=365, actor="retention-job")

    assert purged == [stale["client_id"]]
    remaining_ids = {c["client_id"] for c in service.list_clients_safe()}
    assert stale["client_id"] not in remaining_ids
    assert fresh["client_id"] in remaining_ids
    audit_entries = service.load_store("audit_log")["entries"]
    purge_entry = next(e for e in audit_entries if e["action"] == "retention_purge")
    assert purge_entry["actor"] == "retention-job"
