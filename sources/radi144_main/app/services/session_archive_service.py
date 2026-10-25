from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from uuid import uuid4
from typing import Any

from app.models.session_archive import SessionArchiveEntry, SessionArchiveStore, SessionClientRef
from app.services.client_registry_service import ClientRegistryService
from app.services.json_store import JsonStore


class SessionArchiveService:
    def __init__(self, path: str | Path):
        self.store = JsonStore(path)

    def _load(self) -> SessionArchiveStore:
        return self.store.load(SessionArchiveStore)

    def _save(self, model: SessionArchiveStore) -> None:
        self.store.save(model)

    def create_session(
        self,
        client_ref: dict[str, Any],
        focus: str,
        focus_sequence: list[str],
        config: dict[str, Any],
        result_summary: dict[str, Any],
        harmonization_status: str = "not_started",
    ) -> SessionArchiveEntry:
        store = self._load()
        entry = SessionArchiveEntry(
            session_id=f"sess-{uuid4().hex[:12]}",
            created_at=datetime.utcnow().isoformat(),
            client_ref=SessionClientRef(
                client_id=client_ref.get("client_id"),
                client_name=str(client_ref.get("client_name") or "Unbekannt"),
            ),
            focus=focus,
            focus_sequence=focus_sequence,
            config=config,
            result_summary=result_summary,
            harmonization_status=harmonization_status,
        )
        store.sessions.append(entry)
        self._save(store)
        return entry

    def get_session(self, session_id: str) -> SessionArchiveEntry | None:
        store = self._load()
        for entry in store.sessions:
            if entry.session_id == session_id:
                return entry
        return None

    def list_for_client(self, client_id: str) -> list[SessionArchiveEntry]:
        """R-8/R-9: alle Sessions eines Klienten (Filter ueber client_ref.client_id).
        Grundlage fuer die PII-Safe-View (R-8) und die Art.17-Kaskade (R-9)."""
        lookup = str(client_id or "").strip()
        if not lookup:
            return []
        return [e for e in self._load().sessions if (e.client_ref.client_id or "") == lookup]

    def attach_artifact(self, session_id: str, artifact_id: str) -> SessionArchiveEntry:
        store = self._load()
        for index, entry in enumerate(store.sessions):
            if entry.session_id == session_id:
                if artifact_id not in entry.artifact_ids:
                    entry.artifact_ids.append(artifact_id)
                store.sessions[index] = entry
                self._save(store)
                return entry
        raise KeyError(f"Session nicht gefunden: {session_id}")


def _birth_date_for_powershell(value: str) -> str:
    """Return DDMMYYYY for the legacy PowerShell template view when possible."""
    raw = str(value or "").strip()
    if not raw:
        return ""
    try:
        if "-" in raw:
            return datetime.strptime(raw, "%Y-%m-%d").strftime("%d%m%Y")
        if len(raw) == 8 and raw.isdigit():
            return raw
    except ValueError:
        pass
    return raw


def _powershell_template_from_session(entry: SessionArchiveEntry, runtime_dir: Path) -> dict[str, Any]:
    client = None
    if entry.client_ref.client_id:
        client = ClientRegistryService(runtime_dir / "clients.json").get_by_id(entry.client_ref.client_id)

    config = dict(entry.config or {})
    focus_sequence = entry.focus_sequence or ([entry.focus] if entry.focus else [])
    client_name = entry.client_ref.client_name
    first_name = client.first_name if client else ""
    surname = " ".join(client.last_names) if client and client.last_names else ""

    if not first_name and client_name:
        name_parts = client_name.split()
        first_name = name_parts[0]
        surname = " ".join(name_parts[1:])

    return {
        "timestamp": entry.created_at,
        "template_name": config.get("template_name", ""),
        "client_name": client_name,
        "surname": surname,
        "firstname": first_name,
        "dob": _birth_date_for_powershell(client.birth_date if client else ""),
        "place": client.birth_place if client else "",
        "planet": client.planet if client and client.planet else "",
        "focus": ";".join(focus_sequence),
        "weight": config.get("weight", "Sanft"),
        "palette": config.get("palette", "Client Coherent (Auto)"),
        "mode": config.get("mode", "quantum"),
        "hrv_sim": bool(config.get("hrv_sim", False)),
        "quantum_active": bool(config.get("quantum_active", False)),
        "use_planetary": bool(config.get("use_planetary", False)),
        "emf_compensate": bool(config.get("emf_compensate", False)),
        "amplifier": config.get("amplifier", ""),
        "symmetry": config.get("symmetry", "none"),
        "matrix_size": int(config.get("matrix_size", 12) or 12),
    }


def export_powershell_templates_from_runtime_dir(
    runtime_dir: str | Path,
    output_path: str | Path | None = None,
    max_templates: int = 21,
) -> Path:
    """Export a legacy-compatible PowerShell template view from runtime metadata.

    This keeps `generate_matrix.ps1` consuming the stable `data/runtime/*.json`
    metadata while preserving its existing `session_templates.json` object shape.
    The exported file is generated runtime state and must remain ignored by Git.
    """
    runtime = Path(runtime_dir)
    session_service = SessionArchiveService(runtime / "sessions.json")
    store = session_service._load()
    templates = [
        _powershell_template_from_session(entry, runtime)
        for entry in reversed(store.sessions[-max_templates:])
    ]
    payload = {
        "_meta": {
            "version": "1.0",
            "source": "data/runtime/sessions.json",
            "max_templates": max_templates,
        },
        "templates": templates,
    }
    destination = Path(output_path) if output_path else runtime / "powershell_templates.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return destination
