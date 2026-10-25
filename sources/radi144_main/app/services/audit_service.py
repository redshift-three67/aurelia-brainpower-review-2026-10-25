"""R-9: Append-only Audit-Service (forensischer Art.17-Beleg).

Append-only JSON-Store via JsonStore (load→append→save, atomic). Best-effort
NIE-raising: ein Audit-Fehler darf den Erasure-Flow nicht abbrechen (forensischer
Beleg wird immer versucht, ein Schreibfehler wird geloggt und verworfen).

Pfad default ``data/runtime/audit_log.json`` (env ``R144_AUDIT_LOG_PATH``).
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from uuid import uuid4
from datetime import datetime
from typing import Any

from ..models.audit_log import AuditLogEntry, AuditLogStore
from .json_store import JsonStore

logger = logging.getLogger(__name__)


def default_audit_log_path() -> Path:
    """``data/runtime/audit_log.json`` unter PROJECT_ROOT (env-override)."""
    override = os.getenv("R144_AUDIT_LOG_PATH", "").strip()
    if override:
        return Path(override)
    return Path(__file__).resolve().parents[2] / "data" / "runtime" / "audit_log.json"


class AuditService:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else default_audit_log_path()
        self.store = JsonStore(self.path)

    def _load(self) -> AuditLogStore:
        return self.store.load(AuditLogStore)

    def append(
        self,
        *,
        action: str,
        entity_type: str,
        entity_id: str,
        client_id: str,
        outcome: str = "ok",
        detail: dict[str, Any] | None = None,
        actor: str = "system",
    ) -> AuditLogEntry:
        """Append-only Eintrag. Best-effort NIE-raising."""
        entry = AuditLogEntry(
            event_id=f"aud-{uuid4().hex[:12]}",
            actor=actor,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            client_id=client_id,
            outcome=outcome,
            detail=detail or {},
            created_at=datetime.utcnow().isoformat(),
        )
        try:
            store = self._load()
            store.entries.append(entry)
            self.store.save(store)
        except Exception as exc:  # best-effort: forensischer Beleg darf Flow nicht brechen
            logger.warning(f"Audit-Log-Schreibfehler ({action} {client_id}): {exc}")
        return entry

    def list_for_client(self, client_id: str) -> list[AuditLogEntry]:
        lookup = str(client_id or "").strip()
        if not lookup:
            return []
        try:
            return [e for e in self._load().entries if e.client_id == lookup]
        except Exception:
            return []