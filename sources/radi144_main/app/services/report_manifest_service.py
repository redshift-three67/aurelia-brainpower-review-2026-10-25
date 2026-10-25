from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from app.models.report_manifest import ReportArtifact, ReportManifestStore
from app.services.json_store import JsonStore


class ReportManifestService:
    def __init__(self, path: str | Path):
        self.store = JsonStore(path)

    def _load(self) -> ReportManifestStore:
        return self.store.load(ReportManifestStore)

    def _save(self, model: ReportManifestStore) -> None:
        self.store.save(model)

    def register_artifact(self, session_id: str, artifact_type: str, path: str, label: str = "") -> ReportArtifact:
        store = self._load()
        artifact = ReportArtifact(
            artifact_id=f"art-{uuid4().hex[:12]}",
            session_id=session_id,
            artifact_type=artifact_type,
            path=path,
            label=label,
            created_at=datetime.utcnow().isoformat(),
        )
        store.artifacts.append(artifact)
        self._save(store)
        return artifact

    def list_for_session(self, session_id: str) -> list[ReportArtifact]:
        store = self._load()
        return [artifact for artifact in store.artifacts if artifact.session_id == session_id]
