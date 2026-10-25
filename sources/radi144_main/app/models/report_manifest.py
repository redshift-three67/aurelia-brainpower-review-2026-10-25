from __future__ import annotations

from pydantic import BaseModel, Field


class ReportArtifact(BaseModel):
    artifact_id: str
    session_id: str
    artifact_type: str
    path: str
    label: str = ""
    created_at: str


class ReportManifestStore(BaseModel):
    version: str = "1.0"
    artifacts: list[ReportArtifact] = Field(default_factory=list)
