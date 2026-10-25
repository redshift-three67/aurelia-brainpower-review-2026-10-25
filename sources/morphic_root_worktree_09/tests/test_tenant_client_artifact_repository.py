from __future__ import annotations

import pytest

from core.compliance.artifact_repository import TenantClientArtifactRepository


def test_artifact_repository_builds_pseudonymous_tenant_client_paths(tmp_path) -> None:
    repository = TenantClientArtifactRepository(tmp_path / "exports", tenant_id="ws-123", client_id="cli-abc")

    path = repository.plan_path(category="resonance", session_id="sess-001", filename="report.json")

    assert path == tmp_path / "exports" / "ws-123" / "cli-abc" / "resonance" / "sess-001" / "report.json"
    assert "Klaus" not in str(path)


@pytest.mark.parametrize("value", ["../escape", "tenant/name", "", "with space"])
def test_artifact_repository_rejects_noncanonical_path_segments(tmp_path, value) -> None:
    with pytest.raises(ValueError):
        TenantClientArtifactRepository(tmp_path, tenant_id=value, client_id="cli-abc")
