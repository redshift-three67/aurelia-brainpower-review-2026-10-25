"""R-8: PII-Stripping Safe-View-Regression-Guard.

Pinnt, dass die Pseudonym-Safe-View KEINE Roh-PII ausgibt:
- project_client_safe wirft first_name/last_names/birth_date/birth_place, behaelt client_id.
- project_session_safe redigiert client_name, behaelt client_id.
- GET /api/v1/clients liefert nur Pseudonyme (kein first_name in der Response).

Nutzt tmp JsonStore-Pfade — KEIN Schreibzugriff auf echte data/runtime/.
user_workflow.* wird NICHT beruehrt.
"""
from pathlib import Path

from fastapi.testclient import TestClient

from app.api import clients as clients_api
from app.api import resonance as resonance_api
from app.services.safety_service import project_client_safe, project_session_safe
from app.services.client_registry_service import ClientRegistryService
from app.services.session_archive_service import SessionArchiveService


def _make_entry():
    service = ClientRegistryService.__new__(ClientRegistryService)
    from app.models.client_registry import ClientRegistryEntry
    return ClientRegistryEntry(
        client_id="cli-abcdef0123456789",
        first_name="Max",
        last_names=["Mustermann"],
        birth_date="1980-05-20",
        birth_place="Berlin",
        planet="Venus",
        metadata={"k": "v"},
        created_at="2026-01-01T00:00:00",
        updated_at="2026-01-01T00:00:00",
    )


def test_project_client_safe_strips_pii_keeps_pseudonym():
    entry = _make_entry()
    safe = project_client_safe(entry)
    # Pseudonym + Nicht-PII bleibt
    assert safe["client_id"] == "cli-abcdef0123456789"
    assert safe["planet"] == "Venus"
    assert safe["metadata"] == {"k": "v"}
    # Roh-PII entfernt
    for field in ("first_name", "last_names", "birth_date", "birth_place"):
        assert field not in safe, f"PII-Feld {field} nicht gestrippt"


def test_project_session_safe_redacts_name():
    from app.models.session_archive import SessionArchiveEntry, SessionClientRef
    entry = SessionArchiveEntry(
        session_id="sess-test",
        created_at="2026-01-01T00:00:00",
        client_ref=SessionClientRef(client_id="cli-abcdef0123456789", client_name="Max Mustermann"),
        focus="Test-Fokus",
    )
    safe = project_session_safe(entry)
    assert safe["client_ref"]["client_id"] == "cli-abcdef0123456789"
    assert safe["client_ref"]["client_name"] == "[redacted]"
    assert "Mustermann" not in str(safe)


def _seed_clients(runtime_root: Path):
    service = ClientRegistryService(runtime_root / "clients.json")
    service.get_or_create(
        {"first_name": "Max", "last_names": ["Mustermann"], "birth_date": "1980-05-20", "birth_place": "Berlin", "planet": None}
    )
    service.get_or_create(
        {"first_name": "Anna", "last_names": ["Schmidt"], "birth_date": "1990-01-01", "birth_place": "Hamburg", "planet": None}
    )
    return service


def test_clients_endpoint_returns_pseudonyms_only(monkeypatch, tmp_path):
    monkeypatch.setattr(resonance_api, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(clients_api, "_runtime_archive_root", lambda: tmp_path / "data" / "runtime")

    runtime_root = tmp_path / "data" / "runtime"
    _seed_clients(runtime_root)

    client = TestClient(__import__("main").app)
    response = client.get("/api/v1/clients")

    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert len(items) == 2
    for item in items:
        assert "client_id" in item
        # KEINE Roh-PII in der Safe-View
        for field in ("first_name", "last_names", "birth_date", "birth_place"):
            assert field not in item, f"PII-Feld {field} in /clients-Response ausgeliefert"
    ids = {item["client_id"] for item in items}
    assert all(cid.startswith("cli-") for cid in ids)


def test_list_entries_and_list_for_client_methods(tmp_path):
    runtime_root = tmp_path / "data" / "runtime"
    registry = _seed_clients(runtime_root)
    entries = registry.list_entries()
    assert len(entries) == 2
    assert all(e.client_id.startswith("cli-") for e in entries)

    sess_service = SessionArchiveService(runtime_root / "sessions.json")
    cid = entries[0].client_id
    sess_service.create_session(
        client_ref={"client_id": cid, "client_name": "Max Mustermann"},
        focus="F1", focus_sequence=["F1"], config={}, result_summary={}, harmonization_status="not_requested",
    )
    sess_service.create_session(
        client_ref={"client_id": "cli-other", "client_name": "Other"},
        focus="F2", focus_sequence=["F2"], config={}, result_summary={}, harmonization_status="not_requested",
    )
    for_client = sess_service.list_for_client(cid)
    assert len(for_client) == 1
    assert for_client[0].client_ref.client_id == cid