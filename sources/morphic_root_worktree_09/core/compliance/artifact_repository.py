"""Additiver Planer fuer tenant- und clientgebundene Exportpfade.

Er erzeugt nur kanonische Pfade und schreibt keine Daten. Bestehende Legacy-
Exportpfade bleiben unveraendert, bis ein eigener Integrationsgate sie bewusst
auf diesen Adapter umstellt.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path


_CANONICAL_SEGMENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")
_CANONICAL_FILENAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")


def _segment(value: str, label: str) -> str:
    cleaned = str(value or "").strip()
    if not _CANONICAL_SEGMENT.fullmatch(cleaned):
        raise ValueError(f"{label} must be a canonical path segment")
    return cleaned


def _filename(value: str) -> str:
    cleaned = str(value or "").strip()
    if not _CANONICAL_FILENAME.fullmatch(cleaned) or ".." in cleaned:
        raise ValueError("filename must be a canonical filename")
    return cleaned


@dataclass(frozen=True)
class TenantClientArtifactRepository:
    root: Path
    tenant_id: str
    client_id: str

    def __init__(self, root: str | Path, *, tenant_id: str, client_id: str) -> None:
        object.__setattr__(self, "root", Path(root))
        object.__setattr__(self, "tenant_id", _segment(tenant_id, "tenant_id"))
        object.__setattr__(self, "client_id", _segment(client_id, "client_id"))

    def plan_path(self, *, category: str, session_id: str, filename: str) -> Path:
        return (
            self.root
            / self.tenant_id
            / self.client_id
            / _segment(category, "category")
            / _segment(session_id, "session_id")
            / _filename(filename)
        )


def parallel_export_plan_from_environment(
    *, tenant_id: str, client_id: str, session_id: str
) -> Path | None:
    """Plant nur bei explizit gesetztem serverseitigem Root einen Parallelpfad."""
    root = os.getenv("MORPHIC_PARALLEL_EXPORT_ROOT", "").strip()
    if not root:
        return None
    return TenantClientArtifactRepository(
        root, tenant_id=tenant_id, client_id=client_id
    ).plan_path(
        category="resonance", session_id=session_id, filename="planned_result.json"
    )
