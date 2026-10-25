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
import json
import os
import socket
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from core.compliance.runtime_manifest import runtime_root


class OwnershipError(PermissionError):
    """Ausgeloest, wenn ein Operator auf eine fremde Ressource zugreifen will."""


@dataclass(frozen=True)
class OperatorContext:
    operator_id: str
    workspace_id: str


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
    path.parent.mkdir(parents=True, exist_ok=True)
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


def resolve_operator_context(root: Path | None = None) -> OperatorContext:
    """Ermittelt den aktuellen Operator-/Workspace-Kontext.

    `operator_id` kommt standardmaessig aus OS-Benutzername + Hostname
    (ueberschreibbar via `MORPHIC_OPERATOR_ID`), `workspace_id` wird einmalig
    im Runtime-Store persistiert und bleibt danach stabil.
    """

    resolved_root = Path(root) if root is not None else runtime_root()
    workspace_id = _load_or_create_workspace_id(resolved_root)
    return OperatorContext(operator_id=_default_operator_id(), workspace_id=workspace_id)


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
