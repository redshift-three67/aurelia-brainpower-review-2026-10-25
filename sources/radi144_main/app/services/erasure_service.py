"""R-9: Art.17-Lösch-Kaskade (manifest → gated execute).

Spiegelt ME2s Art.17-Pattern (G9.1/G9.2): default nicht-destruktives Manifest,
echte Kaskade nur per Gate-Token ``R144_ERASURE_ACKNOWLEDGED`` (env
``R144_ERASURE_GATE_TOKEN``), forensischer Audit-Eintrag IMMER (auch bei
not_found/leer). Idempotent (Re-Execute = 0-Counts + not_found-Audit).

Kaskaden-Scope (Nutzer-Entscheidung 2026-06-27): JSON×3-Stores (clients.json,
sessions.json, artifacts.json) **+** physische Dateien (ReportArtifact.path)
und best-effort ``Analysen/*_<sanitized_name>``-Verzeichnisse.

Verknuepfung: Client → Sessions (``client_ref.client_id``) → Artifacts
(``ReportArtifact.session_id`` ∈ betroffenen Session-IDs) → Dateien.
"""
from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path
from typing import Any

from .client_registry_service import ClientRegistryService
from .session_archive_service import SessionArchiveService
from .report_manifest_service import ReportManifestService
from .audit_service import AuditService

logger = logging.getLogger(__name__)

R144_ERASURE_ACKNOWLEDGED = "R144_ERASURE_ACKNOWLEDGED"


def _gate_token() -> str:
    return (os.getenv("R144_ERASURE_GATE_TOKEN", "").strip() or R144_ERASURE_ACKNOWLEDGED)


def _sanitized_full_name(entry) -> str:
    """Reproduziert dev_cli.py:122 ``client_name.replace(' ', '_')``.

    full_name = f"{first_name} {' '.join(last_names)}".strip()  (dev_cli.py:1059).
    """
    last_names = entry.last_names or []
    if isinstance(last_names, list):
        suffix = " ".join(str(n).strip() for n in last_names if str(n).strip())
    else:
        suffix = str(last_names).strip()
    full = f"{entry.first_name} {suffix}".strip() or "Unbekannt"
    return full.replace(" ", "_")


class ErasureService:
    def __init__(
        self,
        registry_path: str | Path,
        session_path: str | Path,
        artifact_path: str | Path,
        audit_log_path: str | Path | None = None,
        analysen_dir: str | Path | None = None,
    ):
        self.registry_path = Path(registry_path)
        self.session_path = Path(session_path)
        self.artifact_path = Path(artifact_path)
        self.audit = AuditService(audit_log_path)
        self.analysen_dir = Path(analysen_dir) if analysen_dir else None

    # ------------------------------------------------------------------ interne Helfer
    def _services(self):
        return (
            ClientRegistryService(self.registry_path),
            SessionArchiveService(self.session_path),
            ReportManifestService(self.artifact_path),
        )

    def _collect(self, client_id: str) -> dict[str, Any]:
        """Sammelt alle betroffenen Entitaeten OHNE zu mutieren (Manifest-Grundlage)."""
        registry, session_service, report_service = self._services()
        client_entry = registry.get_by_id(client_id)
        sessions = session_service.list_for_client(client_id) if client_entry else []
        affected_session_ids = {s.session_id for s in sessions}
        artifacts_store = report_service._load()
        artifacts = [a for a in artifacts_store.artifacts if a.session_id in affected_session_ids]
        fs_files = [a.path for a in artifacts if a.path]

        fs_dirs: list[str] = []
        if client_entry and self.analysen_dir and self.analysen_dir.exists():
            suffix = "_" + _sanitized_full_name(client_entry)
            try:
                for p in self.analysen_dir.iterdir():
                    if p.is_dir() and p.name.endswith(suffix):
                        fs_dirs.append(str(p))
            except Exception as exc:
                logger.warning(f"Analysen-Dir-Scan fehlgeschlagen ({client_id}): {exc}")

        return {
            "client_entry": client_entry,
            "sessions": sessions,
            "affected_session_ids": affected_session_ids,
            "artifacts": artifacts,
            "fs_files": fs_files,
            "fs_dirs": fs_dirs,
        }

    # ------------------------------------------------------------------ Manifest (nicht-destruktiv)
    def request_manifest(self, client_id: str) -> dict[str, Any]:
        client_id = str(client_id or "").strip()
        collected = self._collect(client_id)
        client_entry = collected["client_entry"]
        manifest = {
            "client_id": client_id,
            "client_entry_present": client_entry is not None,
            "sessions": [s.session_id for s in collected["sessions"]],
            "artifacts": [{"id": a.artifact_id, "path": a.path} for a in collected["artifacts"]],
            "fs_files": collected["fs_files"],
            "fs_dirs": collected["fs_dirs"],
            "gated": True,
            "gate_token_required": True,
        }
        self.audit.append(
            action="erasure_manifest",
            entity_type="client",
            entity_id=client_id,
            client_id=client_id,
            outcome="ok" if client_entry is not None else "not_found",
            detail={
                "sessions": len(manifest["sessions"]),
                "artifacts": len(manifest["artifacts"]),
                "fs_files": len(manifest["fs_files"]),
                "fs_dirs": len(manifest["fs_dirs"]),
            },
        )
        return manifest

    # ------------------------------------------------------------------ Execute (gated)
    def execute(self, client_id: str, *, gate_token: str) -> dict[str, Any]:
        client_id = str(client_id or "").strip()
        if gate_token != _gate_token():
            # forensischer Beleg auch fuer den abgewiesenen Versuch
            self.audit.append(
                action="erasure_execute",
                entity_type="client",
                entity_id=client_id,
                client_id=client_id,
                outcome="gated",
                detail={"reason": "invalid or missing gate_token"},
            )
            raise ValueError("Ungueltiges oder fehlendes Gate-Token (R144_ERASURE_ACKNOWLEDGED).")

        collected = self._collect(client_id)
        client_entry = collected["client_entry"]
        registry, session_service, report_service = self._services()

        removed_clients = 0
        removed_sessions = 0
        removed_artifacts = 0
        removed_files = 0
        removed_dirs = 0

        if client_entry is None:
            # idempotent: nicht-destruktiv, aber forensischer Beleg IMMER
            self.audit.append(
                action="erasure_execute",
                entity_type="client",
                entity_id=client_id,
                client_id=client_id,
                outcome="not_found",
                detail={"reason": "client_id nicht in clients.json"},
            )
            return {
                "client_id": client_id,
                "removed_clients": 0,
                "removed_sessions": 0,
                "removed_artifacts": 0,
                "removed_files": 0,
                "removed_dirs": 0,
                "outcome": "not_found",
            }

        # (1) clients.json — entferne Entry
        clients_store = registry._load()
        before_c = len(clients_store.entries)
        clients_store.entries = [e for e in clients_store.entries if e.client_id != client_id]
        removed_clients = before_c - len(clients_store.entries)
        registry._save(clients_store)

        # (2) sessions.json — entferne Sessions des Klienten
        sessions_store = session_service._load()
        before_s = len(sessions_store.sessions)
        sessions_store.sessions = [
            s for s in sessions_store.sessions if (s.client_ref.client_id or "") != client_id
        ]
        removed_sessions = before_s - len(sessions_store.sessions)
        session_service._save(sessions_store)

        # (3) artifacts.json — entferne Artifacts betroffener Sessions
        affected = collected["affected_session_ids"]
        artifacts_store = report_service._load()
        before_a = len(artifacts_store.artifacts)
        artifacts_store.artifacts = [
            a for a in artifacts_store.artifacts if a.session_id not in affected
        ]
        removed_artifacts = before_a - len(artifacts_store.artifacts)
        report_service._save(artifacts_store)

        # (4) Dateisystem — loesche registrierte Artefakt-Dateien (best-effort)
        for path_str in collected["fs_files"]:
            try:
                Path(path_str).unlink(missing_ok=True)
                removed_files += 1
            except Exception as exc:
                logger.warning(f"Datei-Loeschung fehlgeschlagen ({path_str}): {exc}")

        # (5) Dateisystem — best-effort Analysen/<name>-Verzeichnisse
        for dir_str in collected["fs_dirs"]:
            try:
                shutil.rmtree(dir_str, ignore_errors=False)
                removed_dirs += 1
            except Exception as exc:
                logger.warning(f"Verzeichnis-Loeschung fehlgeschlagen ({dir_str}): {exc}")

        audit_entry = self.audit.append(
            action="erasure_execute",
            entity_type="client",
            entity_id=client_id,
            client_id=client_id,
            outcome="ok",
            detail={
                "removed_clients": removed_clients,
                "removed_sessions": removed_sessions,
                "removed_artifacts": removed_artifacts,
                "removed_files": removed_files,
                "removed_dirs": removed_dirs,
            },
        )
        return {
            "client_id": client_id,
            "removed_clients": removed_clients,
            "removed_sessions": removed_sessions,
            "removed_artifacts": removed_artifacts,
            "removed_files": removed_files,
            "removed_dirs": removed_dirs,
            "outcome": "ok",
            "audit_event_id": audit_entry.event_id,
        }