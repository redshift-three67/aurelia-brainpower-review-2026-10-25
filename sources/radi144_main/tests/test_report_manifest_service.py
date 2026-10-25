from app.models.report_manifest import ReportArtifact
from app.services.report_manifest_service import ReportManifestService


def test_report_manifest_registers_artifacts_per_session(tmp_path):
    service = ReportManifestService(tmp_path / "artifacts.json")

    artifact = service.register_artifact(
        session_id="sess-123",
        artifact_type="pdf",
        path="Analysen/20260603_Max/report.pdf",
        label="Einzelbericht",
    )

    assert isinstance(artifact, ReportArtifact)
    assert artifact.session_id == "sess-123"
    assert artifact.artifact_type == "pdf"
    assert artifact.path.endswith("report.pdf")

    items = service.list_for_session("sess-123")
    assert len(items) == 1
    assert items[0].artifact_id == artifact.artifact_id


def test_report_manifest_store_contains_metadata(tmp_path):
    store_path = tmp_path / "artifacts.json"
    service = ReportManifestService(store_path)

    service.register_artifact(
        session_id="sess-234",
        artifact_type="xlsx",
        path="Analysen/20260603_Max/report.xlsx",
        label="Excelbericht",
    )

    persisted = store_path.read_text(encoding="utf-8")
    assert '"artifacts"' in persisted
    assert '"artifact_type": "xlsx"' in persisted
