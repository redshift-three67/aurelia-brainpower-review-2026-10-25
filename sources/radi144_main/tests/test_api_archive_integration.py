from pathlib import Path

from fastapi.testclient import TestClient

from main import app
from app.api import resonance as resonance_api
from app.services.client_registry_service import ClientRegistryService
from app.services.report_manifest_service import ReportManifestService
from app.services.session_archive_service import SessionArchiveService
from tests.test_api_vector_modes import _DummyEngine



def _seed_client(runtime_root: Path) -> str:
    service = ClientRegistryService(runtime_root / "clients.json")
    entry = service.get_or_create(
        {
            "first_name": "Max",
            "last_names": ["Mustermann"],
            "birth_date": "1980-05-20",
            "birth_place": "Berlin",
            "planet": None,
        }
    )
    return entry.client_id



def test_analyze_matrix_resolves_string_client_id_and_archives_session(monkeypatch, tmp_path):
    monkeypatch.setattr(resonance_api, "engine", _DummyEngine())
    monkeypatch.setattr(resonance_api, "PROJECT_ROOT", tmp_path)

    runtime_root = tmp_path / "data" / "runtime"
    client_id = _seed_client(runtime_root)

    client = TestClient(app)
    response = client.post(
        "/api/v1/analyze-matrix",
        json={
            "client_id": client_id,
            "focus": "Archivierter API-Test",
            "matrix_size": 12,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["client_name"] == "Max Mustermann"
    assert response.headers["x-client-id"] == client_id
    assert response.headers["x-session-id"].startswith("sess-")

    session_service = SessionArchiveService(runtime_root / "sessions.json")
    sessions = session_service._load().sessions
    assert len(sessions) == 1
    assert sessions[0].session_id == response.headers["x-session-id"]
    assert sessions[0].client_ref.client_id == client_id
    assert sessions[0].client_ref.client_name == "Max Mustermann"
    assert sessions[0].focus == "Archivierter API-Test"
    assert sessions[0].artifact_ids == []



def test_export_pdf_can_write_artifact_and_register_manifest(monkeypatch, tmp_path):
    monkeypatch.setattr(resonance_api, "PROJECT_ROOT", tmp_path)

    runtime_root = tmp_path / "data" / "runtime"
    session_service = SessionArchiveService(runtime_root / "sessions.json")
    session = session_service.create_session(
        client_ref={"client_id": "cli-test", "client_name": "Max Mustermann"},
        focus="PDF Fokus",
        focus_sequence=["PDF Fokus"],
        config={"mode": "quantum", "matrix_size": 12},
        result_summary={"result_count": 1, "resonance_score": 0.42, "hardware": "TEST"},
        harmonization_status="not_requested",
    )

    client = TestClient(app)
    output_path = tmp_path / "Analysen" / "api_export.pdf"
    response = client.post(
        "/api/v1/export/pdf",
        json={
            "session_id": session.session_id,
            "output_path": str(output_path),
            "result": {
                "client_name": "Max Mustermann",
                "focus": "PDF Fokus",
                "resonance_score": 0.42,
                "processing_time_ms": 5.0,
                "hardware_acceleration": "TEST",
                "matrix_size": 12,
                "matrix_data": [[1 for _ in range(12)] for _ in range(12)],
                "matrix_colors": [["#FFFFFF" for _ in range(12)] for _ in range(12)],
            },
            "context": {
                "vector_mode": "client",
                "focus_weight": "Normal",
                "calculation_mode": "quantum",
                "symmetry": "none",
                "palette": "Standard",
                "amplifier": None,
                "planetary_enabled": False,
                "emf_enabled": False,
                "hrv_enabled": False,
            },
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["x-artifact-id"].startswith("art-")
    assert output_path.exists()
    assert output_path.stat().st_size > 0

    report_service = ReportManifestService(runtime_root / "artifacts.json")
    artifacts = report_service.list_for_session(session.session_id)
    assert len(artifacts) == 1
    assert artifacts[0].artifact_type == "pdf"
    assert artifacts[0].path == str(output_path)

    updated_session = session_service.get_session(session.session_id)
    assert updated_session is not None
    assert updated_session.artifact_ids == [artifacts[0].artifact_id]
