"""R-7/R-8/R-9: Clients-Router — Safety-Posture, PII-Safe-View, Art.17-Kaskade.

Additiv, non-breaking. Wird in main.py unter prefix=/api/v1 registriert.
Beruehrt NICHT user_workflow.* (aktive Nutzer-Vorarbeit).

- GET  /clients/safety/posture           — R-7: kanonische Safety-Posture abrufbar.
- GET  /clients                          — R-8: Pseudonym-Safe-View (keine Roh-PII).
- GET  /clients/{id}/erasure-manifest    — R-9: nicht-destruktives Art.17-Manifest.
- DELETE /clients/{id}                   — R-9: gegegte Kaskade (JSON×3 + Dateisystem).
- GET  /clients/{id}/audit               — R-9: forensische Audit-Eintraege pro Klient.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from ..services.safety_service import safety_block, DISCLAIMER_DE, project_client_safe
from ..services.client_registry_service import ClientRegistryService
from ..services.session_archive_service import SessionArchiveService
from ..services.report_manifest_service import ReportManifestService
from ..services.erasure_service import ErasureService, R144_ERASURE_ACKNOWLEDGED
from ..services.audit_service import AuditService

router = APIRouter()


def _runtime_archive_root():
    from pathlib import Path
    return Path(__file__).resolve().parents[2] / "data" / "runtime"


def _archive_services():
    root = _runtime_archive_root()
    return (
        ClientRegistryService(root / "clients.json"),
        SessionArchiveService(root / "sessions.json"),
        ReportManifestService(root / "artifacts.json"),
    )


def _erasure_service():
    root = _runtime_archive_root()
    from pathlib import Path
    project_root = Path(__file__).resolve().parents[2]
    return ErasureService(
        registry_path=root / "clients.json",
        session_path=root / "sessions.json",
        artifact_path=root / "artifacts.json",
        audit_log_path=root / "audit_log.json",
        analysen_dir=project_root / "Analysen",
    )


# ------------------------------------------------------------------ R-7
@router.get("/clients/safety/posture")
async def safety_posture():
    """Kanonische Nicht-Medizin-Safety-Posture (Disclaimer + Marker)."""
    return safety_block()


# ------------------------------------------------------------------ R-8
@router.get("/clients")
async def list_clients_safe():
    """PII-Safe-View: liefert NUR Pseudonym-Projektionen, KEINE Roh-PII.

    Die autarkische Safe-View fuer Audit/Bus-Andock (R-10 nutzt sie als
    PII-stripped Quelle). Roh-PII (first_name/last_names/birth_date/birth_place)
    wird via project_client_safe entfernt — siehe services/safety_service.py.
    """
    registry, _, _ = _archive_services()
    return [project_client_safe(entry) for entry in registry.list_entries()]


# Re-Export fuer Konsumenten, die den Disclaimer-Text direkt brauchen.
__all__ = [
    "router", "safety_posture", "list_clients_safe", "DISCLAIMER_DE",
    "R144_ERASURE_ACKNOWLEDGED",
]


# ------------------------------------------------------------------ R-9: Art.17-Kaskade
@router.get("/clients/{client_id}/erasure-manifest")
async def erasure_manifest(client_id: str):
    """Nicht-destruktives Art.17-Manifest: listet, WAS geloescht wuerde.

    Mutiert keine Stores. Schreibt einen ``erasure_manifest``-Audit-Eintrag
    (forensischer Beleg der Auskunft). Echte Kaskade nur via DELETE + Gate-Token.
    """
    service = _erasure_service()
    manifest = service.request_manifest(client_id)
    return manifest


@router.delete("/clients/{client_id}")
async def erase_client(client_id: str, gate_token: str = Query(default="")):
    """Gegegte Art.17-Kaskade (JSON×3-Stores + Dateisystem + Audit).

    Ohne/falsches ``gate_token`` -> 401. Korrekter Token -> Kaskade + forensischer
    ``erasure.execute``-Audit-Eintrag IMMER (auch bei not_found/leer). Idempotent.
    """
    service = _erasure_service()
    try:
        result = service.execute(client_id, gate_token=gate_token)
    except ValueError:
        return JSONResponse(
            status_code=401,
            content={"detail": "Ungueltiges oder fehlendes Gate-Token (R144_ERASURE_ACKNOWLEDGED)."},
        )
    if result.get("outcome") == "not_found":
        return JSONResponse(status_code=404, content=result)
    return result


@router.get("/clients/{client_id}/audit")
async def client_audit(client_id: str):
    """Forensische Audit-Eintraege fuer einen Klienten (Transparenz)."""
    service = _erasure_service()
    entries = service.audit.list_for_client(client_id)
    return [e.model_dump(mode="json") for e in entries]