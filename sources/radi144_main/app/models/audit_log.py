"""R-9: Append-only Audit-Log-Modell (forensischer Art.17-Beleg).

Spiegelt ME2s access_audit_log-Pattern (G9.1), adaptiert auf Radi144s
JSON-File-Persistenz. Append-only im Service-Layer (load→append→save,
atomic via JsonStore) — siehe services/audit_service.py.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AuditLogEntry(BaseModel):
    event_id: str
    actor: str = "system"
    action: str  # erasure_manifest | erasure_execute | access | purge
    entity_type: str  # client | session | artifact | file | dir
    entity_id: str
    client_id: str
    outcome: str  # ok | gated | not_found | error
    detail: dict[str, Any] = Field(default_factory=dict)
    created_at: str


class AuditLogStore(BaseModel):
    version: str = "1.0"
    entries: list[AuditLogEntry] = Field(default_factory=list)