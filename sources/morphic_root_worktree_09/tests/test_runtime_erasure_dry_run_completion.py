from __future__ import annotations

from core.compliance.runtime_manifest import RuntimeManifestService


def test_erasure_manifest_reports_existing_and_missing_artifact_paths_without_mutation(tmp_path) -> None:
    service = RuntimeManifestService(tmp_path / "runtime")
    client = {
        "first_name": "Test",
        "last_name": "Client",
        "birth_date": "01012000",
        "birth_place": "Ort",
    }
    existing = tmp_path / "existing-report.json"
    existing.write_text("test", encoding="utf-8")
    missing = tmp_path / "missing-report.json"
    service.register_artifact(client, artifact_type="report", path=existing)
    service.register_artifact(client, artifact_type="report", path=missing)

    client_id = service.list_clients_safe()[0]["client_id"]
    manifest = service.erasure_manifest(client_id)

    statuses = {item["path"]: item["path_state"] for item in manifest["artifacts"]}
    assert statuses[str(existing)] == "exists_file"
    assert statuses[str(missing)] == "missing"
    assert manifest["dry_run"] is True
    assert "web_job_logs" in manifest["uncovered_storage_classes"]
    assert existing.exists()
