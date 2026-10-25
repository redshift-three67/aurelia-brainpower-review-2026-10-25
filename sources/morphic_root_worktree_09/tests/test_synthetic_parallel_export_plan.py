from __future__ import annotations

from apps.web.reports import ReportCatalog
from core.compliance.artifact_repository import TenantClientArtifactRepository
from core.compliance.runtime_manifest import RuntimeManifestService


def test_synthetic_parallel_export_plan_registers_pseudonymous_manifest_reference_without_writing(tmp_path) -> None:
    runtime = RuntimeManifestService(tmp_path / "runtime")
    client = {
        "first_name": "Synthetic",
        "last_name": "OperatorTest",
        "birth_date": "01012000",
        "birth_place": "Testort",
    }
    client_id = runtime.get_or_create_client(client)["client_id"]
    repository = TenantClientArtifactRepository(
        tmp_path / "parallel-exports", tenant_id="ws-synthetic", client_id=client_id
    )
    planned = repository.plan_path(
        category="resonance", session_id="sess-synthetic", filename="result.json"
    )

    artifact = runtime.register_artifact(
        client,
        artifact_type="parallel_export_plan",
        path=planned,
        session_id="sess-synthetic",
        config={"mode": "plan_only", "tenant_id": "ws-synthetic"},
    )
    manifest = runtime.erasure_manifest(client_id)

    assert artifact["path"] == str(planned)
    assert not planned.exists()
    assert manifest["artifacts"] == [
        {
            "id": artifact["artifact_id"],
            "path": str(planned),
            "artifact_type": "parallel_export_plan",
            "path_state": "missing",
        }
    ]
    assert "Synthetic" not in str(planned)
    assert "OperatorTest" not in str(planned)


def test_synthetic_parallel_export_plan_is_read_only_for_manifest_and_report_catalog(tmp_path) -> None:
    runtime = RuntimeManifestService(tmp_path / "runtime")
    client = {
        "first_name": "Synthetic",
        "last_name": "CatalogTest",
        "birth_date": "02022000",
        "birth_place": "Testort",
    }
    client_id = runtime.get_or_create_client(client)["client_id"]
    parallel_root = tmp_path / "parallel-exports"
    planned = TenantClientArtifactRepository(
        parallel_root, tenant_id="ws-synthetic", client_id=client_id
    ).plan_path(
        category="resonance", session_id="sess-catalog", filename="planned_result.json"
    )
    artifact = runtime.register_artifact(
        client,
        artifact_type="parallel_export_plan",
        path=planned,
        session_id="sess-catalog",
        config={"mode": "plan_only", "tenant_id": "ws-synthetic"},
    )

    manifest = runtime.erasure_manifest(client_id)
    catalog = ReportCatalog([parallel_root]).list(include_all_formats=True)

    assert planned == (
        parallel_root
        / "ws-synthetic"
        / client_id
        / "resonance"
        / "sess-catalog"
        / "planned_result.json"
    )
    assert manifest["artifacts"] == [
        {
            "id": artifact["artifact_id"],
            "path": str(planned),
            "artifact_type": "parallel_export_plan",
            "path_state": "missing",
        }
    ]
    assert catalog == {
        "count": 0,
        "root_count": 1,
        "client_count": 0,
        "clients": [],
        "reports": [],
    }
    assert not parallel_root.exists()
