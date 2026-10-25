"""Tests für scope-partitionierte Workflow-Speicherprimitive."""

from radiworks.scope import ScopeContext
from radiworks.workflow import WorkflowRegistry


def test_workflow_registry_partitions_case_and_draft_storage(tmp_path):
    registry = WorkflowRegistry(tmp_path, tmp_path / "cases", tmp_path / "drafts")
    first_scope = ScopeContext("tenant-a", "client-a", "case-a")
    second_scope = ScopeContext("tenant-b", "client-b", "case-b")
    first = registry.workspace(first_scope)
    second = registry.workspace(second_scope)

    first.case_store.save({"name": "Shared Name"})
    second.case_store.save({"name": "Shared Name"})
    first_draft = first.draft_store.create_from_analysis(
        analysis_dict={"rateObjects": []},
        passport={"kernel": "radiworks.engine", "kernel_version": "0.2.0", "run_id": "run-a"},
        database="HOMEOPATHY_Test",
    )

    assert first.case_store.list_names() == ["SharedName"]
    assert second.case_store.list_names() == ["SharedName"]
    assert first.case_store.current["scope"] == first_scope.to_dict()
    assert second.case_store.current["scope"] == second_scope.to_dict()
    assert first.draft_store.get(first_draft["id"])["scope"] == first_scope.to_dict()
    assert second.draft_store.get(first_draft["id"]) is None
    assert first.case_store.cases_dir != second.case_store.cases_dir
    assert first.draft_store.drafts_dir != second.draft_store.drafts_dir
    assert first.journal_dir != second.journal_dir
