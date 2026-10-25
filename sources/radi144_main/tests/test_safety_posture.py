"""R-7: Safety-Posture-Regression-Guard.

Pinnt die kanonische Nicht-Medizin-Disclaimer- und Safety-Marker-Posture:
- DISCLAIMER_DE enthaelt die Kern-Substrings (Arzt/Heilpraktiker/Diagnose).
- safety_block() Marker medical_claims=0 / inference_only / non_medical / disclaimer.
- Jede /analyze-*-Response traegt ``safety`` (additiv, byte-kompatibel).
- /export/pdf injiziert den Disclaimer in die PDF-Bytes.
- /api/v1/clients/safety/posture ist erreichbar.

user_workflow.* (aktive Nutzer-Vorarbeit) wird hier NICHT beruehrt.
"""
from pathlib import Path

from fastapi.testclient import TestClient

from main import app
from app.api import resonance as resonance_api
from app.services import safety_service
from app.services.client_registry_service import ClientRegistryService
from tests.test_api_vector_modes import _DummyEngine


def test_disclaimer_de_contains_core_terms():
    assert safety_service.DISCLAIMER_DE
    for term in ("Arzt", "Heilpraktiker", "Diagnose", "Heilung"):
        assert term in safety_service.DISCLAIMER_DE


def test_safety_block_markers():
    block = safety_service.safety_block()
    assert block["medical_claims"] == 0
    assert block["inference_only"] is True
    assert block["non_medical"] is True
    assert block["disclaimer"] == safety_service.DISCLAIMER_DE
    # Frische Kopie: Mutation aendert nicht die kanonische Quelle
    block["medical_claims"] = 999
    again = safety_service.safety_block()
    assert again["medical_claims"] == 0


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


def test_analyze_matrix_response_carries_safety(monkeypatch, tmp_path):
    monkeypatch.setattr(resonance_api, "engine", _DummyEngine())
    monkeypatch.setattr(resonance_api, "PROJECT_ROOT", tmp_path)

    runtime_root = tmp_path / "data" / "runtime"
    client_id = _seed_client(runtime_root)

    client = TestClient(app)
    response = client.post(
        "/api/v1/analyze-matrix",
        json={
            "client_id": client_id,
            "focus": "Safety-Posture-Test",
            "matrix_size": 12,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert "safety" in body
    assert body["safety"]["medical_claims"] == 0
    assert body["safety"]["inference_only"] is True
    assert body["safety"]["non_medical"] is True
    assert body["safety"]["disclaimer"] == safety_service.DISCLAIMER_DE


def test_export_pdf_contains_disclaimer(monkeypatch, tmp_path):
    from app.services.session_archive_service import SessionArchiveService

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
    response = client.post(
        "/api/v1/export/pdf",
        json={
            "session_id": session.session_id,
            "output_path": str(tmp_path / "Analysen" / "safety.pdf"),
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
    # reportlab komprimiert den Content-Stream per /ASCII85Decode + /FlateDecode.
    # Plaintext-Suche in rohen Bytes schlaegt fehl; erst ASCII85-, dann zlib-dekodieren.
    import zlib
    import base64

    def _pdf_text(raw: bytes) -> str:
        out = []
        cursor = 0
        while True:
            start = raw.find(b"stream", cursor)
            if start == -1:
                break
            j = start + len(b"stream")
            body_start = j + (2 if raw[j:j + 2] == b"\r\n" else 1)
            end = raw.find(b"endstream", body_start)
            if end == -1:
                break
            region = raw[body_start:end]
            eod = region.rfind(b"~>")
            chunk = region[:eod + 2] if eod != -1 else region.strip()
            try:
                decoded = base64.a85decode(chunk, adobe=True)
                out.append(zlib.decompress(decoded))
            except Exception:
                out.append(chunk)  # unfilterter Stream → direkt
            cursor = end + len(b"endstream")
        return b"\n".join(out).decode("latin-1", errors="ignore")

    decompressed = _pdf_text(response.content)
    assert "Diagnose" in decompressed or "Heilpraktiker" in decompressed, (
        "Disclaimer nicht im PDF-Content-Stream gefunden"
    )


def test_safety_posture_endpoint_reachable():
    client = TestClient(app)
    response = client.get("/api/v1/clients/safety/posture")
    assert response.status_code == 200
    body = response.json()
    assert body["medical_claims"] == 0
    assert body["inference_only"] is True
    assert body["non_medical"] is True
    assert body["disclaimer"] == safety_service.DISCLAIMER_DE