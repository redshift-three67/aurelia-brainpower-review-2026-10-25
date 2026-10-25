"""R-9: Art.17-Lösch-Kaskaden-Regression-Guard.

Pinnt die 2-stufig gegegte Kaskade (Nutzer-Entscheidung 2026-06-27):
- Manifest ist nicht-destruktiv (Stores nach Manifest unveraendert).
- Execute ohne/falsches Gate-Token -> 401 + gated-Audit.
- Execute mit korrektem Token -> JSON×3-Stores bereinigt + FS-Dateien/Dirs
  geloescht + forensischer erasure.execute-Audit-Eintrag.
- Idempotent (Re-Execute = 0-Counts + not_found-Audit).
- not-found-Client -> 404 + not_found-Audit.

Nutzt tmp-Pfade — KEIN Schreibzugriff auf echte data/runtime/.
user_workflow.* wird NICHT beruehrt.
"""
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.api import clients as clients_api
from app.api import resonance as resonance_api
from app.services.client_registry_service import ClientRegistryService
from app.services.session_archive_service import SessionArchiveService
from app.services.report_manifest_service import ReportManifestService
from app.services.audit_service import AuditService
from app.services.erasure_service import ErasureService, R144_ERASURE_ACKNOWLEDGED


def _seed_world(runtime_root: Path, analysen_dir: Path):
    """Baut einen Klienten + Session + Artefakt-Datei + Analysen-Dir + einen zweiten Klienten."""
    registry = ClientRegistryService(runtime_root / "clients.json")
    target = registry.get_or_create(
        {"first_name": "Max", "last_names": ["Mustermann"], "birth_date": "1980-05-20", "birth_place": "Berlin", "planet": None}
    )
    other = registry.get_or_create(
        {"first_name": "Anna", "last_names": ["Schmidt"], "birth_date": "1990-01-01", "birth_place": "Hamburg", "planet": None}
    )

    sess_service = SessionArchiveService(runtime_root / "sessions.json")
    target_session = sess_service.create_session(
        client_ref={"client_id": target.client_id, "client_name": "Max Mustermann"},
        focus="F1", focus_sequence=["F1"], config={}, result_summary={}, harmonization_status="not_requested",
    )
    sess_service.create_session(
        client_ref={"client_id": other.client_id, "client_name": "Anna Schmidt"},
        focus="F2", focus_sequence=["F2"], config={}, result_summary={}, harmonization_status="not_requested",
    )

    # Artefakt-Datei (physisch) fuer den Target-Klienten
    report_service = ReportManifestService(runtime_root / "artifacts.json")
    artifact_file = analysen_dir / "20260603_223103_Max_Mustermann" / "Max_Mustermann_report.pdf"
    artifact_file.parent.mkdir(parents=True, exist_ok=True)
    artifact_file.write_bytes(b"%PDF-1.4 target")
    artifact = report_service.register_artifact(
        session_id=target_session.session_id, artifact_type="pdf", path=str(artifact_file), label="report"
    )
    sess_service.attach_artifact(target_session.session_id, artifact.artifact_id)

    return target, other, target_session, artifact_file


def _patch(monkeypatch, tmp_path):
    runtime_root = tmp_path / "data" / "runtime"
    analysen_dir = tmp_path / "Analysen"
    monkeypatch.setattr(resonance_api, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(clients_api, "_runtime_archive_root", lambda: runtime_root)
    # _erasure_service() leitet analysen_dir aus __file__ ab — patche es auf tmp
    monkeypatch.setattr(
        clients_api, "_erasure_service",
        lambda: ErasureService(
            registry_path=runtime_root / "clients.json",
            session_path=runtime_root / "sessions.json",
            artifact_path=runtime_root / "artifacts.json",
            audit_log_path=runtime_root / "audit_log.json",
            analysen_dir=analysen_dir,
        ),
    )
    return runtime_root, analysen_dir


def test_manifest_is_non_destructive(monkeypatch, tmp_path):
    runtime_root, analysen_dir = _patch(monkeypatch, tmp_path)
    target, other, _, _ = _seed_world(runtime_root, analysen_dir)

    client = TestClient(__import__("main").app)
    res = client.get(f"/api/v1/clients/{target.client_id}/erasure-manifest")
    assert res.status_code == 200
    manifest = res.json()
    assert manifest["client_entry_present"] is True
    assert manifest["gated"] is True
    assert len(manifest["sessions"]) == 1
    assert len(manifest["artifacts"]) == 1
    assert any("Max_Mustermann" in p for p in manifest["fs_files"])
    assert any(d.endswith("Max_Mustermann") for d in manifest["fs_dirs"])

    # Stores UNVERAENDERT nach Manifest
    assert len(ClientRegistryService(runtime_root / "clients.json").list_entries()) == 2
    assert len(SessionArchiveService(runtime_root / "sessions.json")._load().sessions) == 2
    assert len(ReportManifestService(runtime_root / "artifacts.json")._load().artifacts) == 1


def test_execute_without_gate_token_is_401(monkeypatch, tmp_path):
    runtime_root, analysen_dir = _patch(monkeypatch, tmp_path)
    target, _, _, _ = _seed_world(runtime_root, analysen_dir)

    client = TestClient(__import__("main").app)
    res = client.delete(f"/api/v1/clients/{target.client_id}")
    assert res.status_code == 401
    # Klient noch vorhanden (Kaskade nicht ausgefuehrt)
    assert len(ClientRegistryService(runtime_root / "clients.json").list_entries()) == 2
    # gated-Audit-Eintrag geschrieben
    audit = AuditService(runtime_root / "audit_log.json").list_for_client(target.client_id)
    assert any(e.action == "erasure_execute" and e.outcome == "gated" for e in audit)


def test_execute_with_correct_token_cascades(monkeypatch, tmp_path):
    runtime_root, analysen_dir = _patch(monkeypatch, tmp_path)
    target, other, target_session, artifact_file = _seed_world(runtime_root, analysen_dir)
    assert artifact_file.exists()

    client = TestClient(__import__("main").app)
    res = client.delete(
        f"/api/v1/clients/{target.client_id}?gate_token={R144_ERASURE_ACKNOWLEDGED}"
    )
    assert res.status_code == 200
    body = res.json()
    assert body["removed_clients"] == 1
    assert body["removed_sessions"] == 1
    assert body["removed_artifacts"] == 1
    assert body["removed_files"] == 1
    assert body["removed_dirs"] == 1
    assert body["outcome"] == "ok"

    # (1) clients.json — Target weg, Other bleibt
    entries = ClientRegistryService(runtime_root / "clients.json").list_entries()
    assert len(entries) == 1
    assert entries[0].client_id == other.client_id

    # (2) sessions.json — Target-Session weg, Other-Session bleibt
    sessions = SessionArchiveService(runtime_root / "sessions.json")._load().sessions
    assert len(sessions) == 1
    assert sessions[0].client_ref.client_id == other.client_id

    # (3) artifacts.json — leer
    assert len(ReportManifestService(runtime_root / "artifacts.json")._load().artifacts) == 0

    # (4) FS-Datei geloescht + (5) Analysen-Dir geloescht
    assert not artifact_file.exists()
    assert not artifact_file.parent.exists()

    # forensischer erasure.execute-Audit-Eintrag (ok)
    audit = AuditService(runtime_root / "audit_log.json").list_for_client(target.client_id)
    assert any(e.action == "erasure_execute" and e.outcome == "ok" for e in audit)


def test_execute_is_idempotent_and_not_found_audited(monkeypatch, tmp_path):
    runtime_root, analysen_dir = _patch(monkeypatch, tmp_path)
    target, _, _, _ = _seed_world(runtime_root, analysen_dir)

    client = TestClient(__import__("main").app)
    # Erste Kaskade loescht den Klienten
    r1 = client.delete(f"/api/v1/clients/{target.client_id}?gate_token={R144_ERASURE_ACKNOWLEDGED}")
    assert r1.status_code == 200 and r1.json()["removed_clients"] == 1
    # Re-Execute: Klient existiert nicht mehr -> 404 + 0-Counts + not_found-Audit
    r2 = client.delete(f"/api/v1/clients/{target.client_id}?gate_token={R144_ERASURE_ACKNOWLEDGED}")
    assert r2.status_code == 404
    assert r2.json()["outcome"] == "not_found"
    assert r2.json()["removed_clients"] == 0

    audit = AuditService(runtime_root / "audit_log.json").list_for_client(target.client_id)
    not_found = [e for e in audit if e.action == "erasure_execute" and e.outcome == "not_found"]
    assert len(not_found) >= 1


def test_execute_wrong_token_is_401(monkeypatch, tmp_path):
    runtime_root, analysen_dir = _patch(monkeypatch, tmp_path)
    target, _, _, _ = _seed_world(runtime_root, analysen_dir)

    client = TestClient(__import__("main").app)
    res = client.delete(f"/api/v1/clients/{target.client_id}?gate_token=WRONG")
    assert res.status_code == 401
    assert len(ClientRegistryService(runtime_root / "clients.json").list_entries()) == 2