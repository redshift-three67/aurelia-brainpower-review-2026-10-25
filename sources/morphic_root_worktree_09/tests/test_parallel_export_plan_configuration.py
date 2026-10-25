from __future__ import annotations

from core.compliance.artifact_repository import parallel_export_plan_from_environment


def test_parallel_export_plan_is_disabled_by_default(monkeypatch) -> None:
    monkeypatch.delenv("MORPHIC_PARALLEL_EXPORT_ROOT", raising=False)

    assert parallel_export_plan_from_environment(
        tenant_id="ws-123", client_id="cli-abc", session_id="scan-001"
    ) is None


def test_parallel_export_plan_uses_server_configured_root(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("MORPHIC_PARALLEL_EXPORT_ROOT", str(tmp_path / "parallel"))

    plan = parallel_export_plan_from_environment(
        tenant_id="ws-123", client_id="cli-abc", session_id="scan-001"
    )

    assert plan == tmp_path / "parallel" / "ws-123" / "cli-abc" / "resonance" / "scan-001" / "planned_result.json"
    assert not plan.exists()
