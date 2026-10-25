from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from app.models.client_registry import ClientIdentity, ClientRegistryEntry, ClientRegistryStore
from app.services.json_store import JsonStore


class ClientRegistryService:
    def __init__(self, path: str | Path):
        self.store = JsonStore(path)

    def _load(self) -> ClientRegistryStore:
        return self.store.load(ClientRegistryStore)

    def _save(self, model: ClientRegistryStore) -> None:
        self.store.save(model)

    def get_or_create(self, payload: dict[str, Any]) -> ClientRegistryEntry:
        identity = ClientIdentity(
            first_name=str(payload.get("first_name") or "").strip(),
            last_names=[str(v).strip() for v in (payload.get("last_names") or [])],
            birth_date=str(payload.get("birth_date") or "").strip(),
            birth_place=str(payload.get("birth_place") or "").strip(),
            planet=(str(payload.get("planet")).strip() if payload.get("planet") is not None else None),
        )
        store = self._load()
        stable_key = identity.stable_key()
        for entry in store.entries:
            candidate = ClientIdentity(
                first_name=entry.first_name,
                last_names=entry.last_names,
                birth_date=entry.birth_date,
                birth_place=entry.birth_place,
                planet=entry.planet,
            )
            if candidate.stable_key() == stable_key:
                return entry

        digest = hashlib.sha1(stable_key.encode("utf-8")).hexdigest()[:16]
        entry = identity.to_entry(client_id=f"cli-{digest}")
        store.entries.append(entry)
        self._save(store)
        return entry

    def get_by_id(self, client_id: str) -> ClientRegistryEntry | None:
        lookup = str(client_id or "").strip()
        if not lookup:
            return None
        store = self._load()
        for entry in store.entries:
            if entry.client_id == lookup:
                return entry
        return None

    def list_entries(self) -> list[ClientRegistryEntry]:
        """R-8: read-only Liste aller Klienten-Einträge (inkl. PII — nur intern
        fuer die Safe-View-Projektion via safety_service.project_client_safe)."""
        return list(self._load().entries)
