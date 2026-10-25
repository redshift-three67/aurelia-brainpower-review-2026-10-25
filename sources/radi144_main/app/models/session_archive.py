from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SessionClientRef(BaseModel):
    client_id: str | None = None
    client_name: str


class SessionArchiveEntry(BaseModel):
    session_id: str
    created_at: str
    client_ref: SessionClientRef
    focus: str
    focus_sequence: list[str] = Field(default_factory=list)
    config: dict[str, Any] = Field(default_factory=dict)
    result_summary: dict[str, Any] = Field(default_factory=dict)
    artifact_ids: list[str] = Field(default_factory=list)
    harmonization_status: str = "not_started"


class SessionArchiveStore(BaseModel):
    version: str = "1.0"
    sessions: list[SessionArchiveEntry] = Field(default_factory=list)
