"""Operator-/Workspace-Kontext und Ownership-Pruefung.

Leichte, dateibasierte Vorbereitungsschicht fuer eine spaetere echte
Multitenant-/Auth-Anbindung. Adressiert den in
`docs/deep-audit-2026-07-04/PHASE_3_SICHERHEIT_DSGVO_AUTH_MULTITENANT.md`
dokumentierten P0-Befund ("keine Besitzpruefung fuer Jobs/Reports").

Dies ist ausdruecklich **kein** echtes Auth-/Multitenant-System, sondern
ein stabiler, lokal abgeleiteter Operator-/Workspace-Identifier, an den
spaeter eine echte Benutzer-/Tenant-Verwaltung angebunden werden kann (z. B.
im Sinne von radiquant4s Tenant-Modell, siehe
`docs/deep-audit-2026-07-05/RADIQUANT4_RADIMORPHIC_KONTRAKT_REFERENZ.md`,
Abschnitt 8).
"""

from __future__ import annotations

import getpass
import hashlib
import json
import os
import socket
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from apps.web.durable_io import durable_mkdir_parents
from core.compliance.runtime_manifest import runtime_root


class OwnershipError(PermissionError):
    """Ausgeloest, wenn ein Operator auf eine fremde Ressource zugreifen will."""


@dataclass(frozen=True)
class OperatorContext:
    operator_id: str
    workspace_id: str
    tenant_id: str


def operator_owner_scope(context: OperatorContext) -> str:
    """Bind ownership to the exact tenant/operator tuple without delimiters."""
    components = (context.tenant_id, context.operator_id)
    if any(not isinstance(value, str) or not value.strip() for value in components):
        raise ValueError("tenant_id and operator_id are required for owner scope")
    canonical = json.dumps(
        list(components),
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return "owner-v1-" + hashlib.sha256(canonical).hexdigest()


def _workspace_id_path(root: Path) -> Path:
    return root / "workspace_id.json"


def _load_or_create_workspace_id(root: Path) -> str:
    path = _workspace_id_path(root)
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {}
        workspace_id = str(data.get("workspace_id", "")).strip()
        if workspace_id:
            return workspace_id

    workspace_id = f"ws-{uuid4().hex[:16]}"
    durable_mkdir_parents(path.parent, mode=0o700)
    path.write_text(
        json.dumps({"workspace_id": workspace_id}, indent=2) + "\n",
        encoding="utf-8",
    )
    return workspace_id


def _default_operator_id() -> str:
    override = os.getenv("MORPHIC_OPERATOR_ID", "").strip()
    if override:
        return override
    try:
        user = getpass.getuser()
    except Exception:
        user = "unknown"
    try:
        host = socket.gethostname()
    except Exception:
        host = "unknown-host"
    return f"{user}@{host}"


def _default_tenant_id(workspace_id: str) -> str:
    override = os.getenv("MORPHIC_TENANT_ID", "").strip()
    if override:
        return override
    return workspace_id


def resolve_operator_context(root: Path | None = None) -> OperatorContext:
    """Ermittelt den aktuellen Operator-/Workspace-/Tenant-Kontext.

    `operator_id` kommt standardmaessig aus OS-Benutzername + Hostname
    (ueberschreibbar via `MORPHIC_OPERATOR_ID`), `workspace_id` wird einmalig
    im Runtime-Store persistiert und bleibt danach stabil. `tenant_id` ist
    der kanonische Isolationsschluessel fuer Exportpfade/Berichte (analog
    zu radiquant4s `tenant_id`); er faellt standardmaessig auf `workspace_id`
    zurueck und ist ueberschreibbar via `MORPHIC_TENANT_ID`.
    """

    resolved_root = Path(root) if root is not None else runtime_root()
    workspace_id = _load_or_create_workspace_id(resolved_root)
    tenant_id = _default_tenant_id(workspace_id)
    return OperatorContext(
        operator_id=_default_operator_id(),
        workspace_id=workspace_id,
        tenant_id=tenant_id,
    )


def assert_owner(resource_owner_id: str | None, context: OperatorContext) -> None:
    """Prueft Besitz einer Ressource.

    Verhaelt sich additiv/rueckwaertskompatibel: Ist fuer eine Ressource
    (noch) kein Besitzer erfasst (`resource_owner_id` leer/None), bleibt der
    heutige Ein-Operator-Betrieb unveraendert erlaubt. Nur wenn ein Besitzer
    erfasst ist UND er weder `operator_id` noch `workspace_id` des aktuellen
    Kontexts entspricht, wird `OwnershipError` ausgeloest.
    """

    if not resource_owner_id:
        return
    if resource_owner_id not in (context.operator_id, context.workspace_id):
        raise OwnershipError(
            f"Ressource gehoert nicht zum aktuellen Operator/Workspace ({resource_owner_id!r})."
        )


def assert_strict_owner(resource_owner_id: object, context: OperatorContext) -> None:
    """Accept only the exact tenant/operator owner scope for protected state."""
    if resource_owner_id != operator_owner_scope(context):
        raise OwnershipError("Ressource gehoert nicht zum aktuellen Tenant/Operator.")
