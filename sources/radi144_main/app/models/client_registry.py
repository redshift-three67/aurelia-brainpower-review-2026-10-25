from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ClientRegistryEntry(BaseModel):
    client_id: str
    first_name: str
    last_names: list[str] = Field(default_factory=list)
    birth_date: str
    birth_place: str
    planet: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str
    updated_at: str


class ClientRegistryStore(BaseModel):
    version: str = "1.0"
    entries: list[ClientRegistryEntry] = Field(default_factory=list)


class ClientIdentity(BaseModel):
    first_name: str
    last_names: list[str] = Field(default_factory=list)
    birth_date: str
    birth_place: str
    planet: str | None = None

    def stable_key(self) -> str:
        last = "|".join(name.strip().lower() for name in self.last_names)
        planet = (self.planet or "").strip().lower()
        return "::".join([
            self.first_name.strip().lower(),
            last,
            self.birth_date.strip(),
            self.birth_place.strip().lower(),
            planet,
        ])

    def to_entry(self, client_id: str, metadata: dict[str, Any] | None = None) -> ClientRegistryEntry:
        now = datetime.utcnow().isoformat()
        return ClientRegistryEntry(
            client_id=client_id,
            first_name=self.first_name,
            last_names=self.last_names,
            birth_date=self.birth_date,
            birth_place=self.birth_place,
            planet=self.planet,
            metadata=metadata or {},
            created_at=now,
            updated_at=now,
        )
