"""Entitlement-Stub.

Minimale, austauschbare Schnittstelle fuer Modul-/Feature-Freischaltung.
Im heutigen Standalone-Betrieb gibt es kein Abo-/Tenant-System in
`morphic_v1` - per Default sind daher alle Module verfuegbar.

Dies ist ausschliesslich eine Erweiterungsnaht: Eine spaetere, echte
Entitlement-Quelle (angelehnt an radiquant4s `EntitlementService`, siehe
`docs/deep-audit-2026-07-05/RADIQUANT4_RADIMORPHIC_KONTRAKT_REFERENZ.md`,
Abschnitt 8) kann per `set_entitlement_provider` injiziert werden, ohne dass
sich Aufrufstellen aendern muessen.

Bewusst NICHT in bestehende CLI-Befehle eingehaengt (siehe Umsetzungsplan,
Task 3, Schritt 3) - es soll kein Gating vorgetaeuscht werden, das es heute
nicht gibt.
"""

from __future__ import annotations

from typing import Callable

from core.compliance.operator_context import OperatorContext

EntitlementProvider = Callable[[str, OperatorContext], bool]


def _default_provider(module: str, context: OperatorContext) -> bool:
    """Standalone-Default: alle Module sind verfuegbar."""

    return True


_provider: EntitlementProvider = _default_provider


def set_entitlement_provider(provider: EntitlementProvider | None) -> None:
    """Setzt die aktive Entitlement-Quelle (oder setzt mit `None` zurueck)."""

    global _provider
    _provider = provider or _default_provider


def is_module_available(module: str, context: OperatorContext) -> bool:
    """Prueft, ob ein Modul fuer den aktuellen Operator-/Workspace-Kontext
    verfuegbar ist. Standalone: immer `True`."""

    return _provider(module, context)
