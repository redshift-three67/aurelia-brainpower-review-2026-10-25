from __future__ import annotations

from pathlib import Path

from core.admin_catalog import AdminCatalogService
from core.admin_catalog.contracts import CatalogContext, CatalogEntry, EntryType
from core.admin_catalog.runtime_acceptance import (
    run_synthetic_runtime_acceptance,
)
from core.admin_catalog.store import CatalogStore
from core.admin_catalog.validation_attestation import HmacValidationKeyProvider


def _context(suffix: str = "accept") -> CatalogContext:
    return CatalogContext(
        operator_id=f"operator-{suffix}",
        workspace_id=f"workspace-{suffix}",
        tenant_id=f"tenant-{suffix}",
        scope="workspace",
    )


def _entry(
    context: CatalogContext,
    entry_type: EntryType,
    entry_id: str,
    data: dict[str, object],
) -> CatalogEntry:
    return CatalogEntry(
        entry_type=entry_type,
        entry_id=entry_id,
        context=context,
        source_id="synthetic-f8-4",
        provenance="f8-4-runtime-acceptance-test",
        data=data,
    )


def _revision_entries(
    context: CatalogContext,
    suffix: str,
    *,
    stable_managed_ids: bool = False,
) -> tuple[CatalogEntry, ...]:
    group_id = f"group-{suffix}"
    profile_id = "profile-a" if stable_managed_ids else f"profile-{suffix}"
    remedy_id = "remedy-a" if stable_managed_ids else f"remedy-{suffix}"
    pathogen_id = "pathogen-a" if stable_managed_ids else f"pathogen-{suffix}"
    relation_id = "relation-a" if stable_managed_ids else f"relation-{suffix}"
    multiplex_id = "multiplex-a" if stable_managed_ids else f"multiplex-{suffix}"
    return (
        _entry(
            context,
            EntryType.GROUP,
            group_id,
            {
                "description": f"Group {suffix} runtime description",
                "enabled": True,
                "label": f"Group {suffix.upper()}",
            },
        ),
        _entry(
            context,
            EntryType.PROFILE,
            profile_id,
            {
                "aliases": [f"profile-{suffix}-alias"],
                "category": "acceptance",
                "enabled": True,
                "group_ids": [group_id],
                "label": f"Profile {suffix.upper()}",
                "level": 2,
            },
        ),
        _entry(
            context,
            EntryType.REMEDY,
            remedy_id,
            {
                "description": f"Remedy {suffix} indication",
                "enabled": True,
                "label": f"Remedy {suffix.upper()}",
            },
        ),
        _entry(
            context,
            EntryType.PATHOGEN,
            pathogen_id,
            {
                "description": f"Pathogen {suffix} indication",
                "enabled": True,
                "label": f"Pathogen {suffix.upper()}",
            },
        ),
        _entry(
            context,
            EntryType.RELATION,
            relation_id,
            {
                "enabled": True,
                "pathogen_id": pathogen_id,
                "priority": 7,
                "relation_type": "remedy_pathogen",
                "remedy_id": remedy_id,
            },
        ),
        _entry(
            context,
            EntryType.MULTIPLEX,
            multiplex_id,
            {
                "description": f"Multiplex {suffix} runtime description",
                "enabled": True,
                "group_ids": [group_id],
                "label": f"Multiplex {suffix.upper()}",
                "remedy_ids": [remedy_id],
            },
        ),
    )


def _service(tmp_path: Path) -> AdminCatalogService:
    return AdminCatalogService(
        CatalogStore(
            tmp_path / "catalog.sqlite3",
            validation_key_provider=HmacValidationKeyProvider(
                authority_id="f8-4-runtime-acceptance-tests",
                active_key_id="test-v1",
                keys={"test-v1": b"K" * 32},
            ),
        )
    )


def test_f8_4_acceptance_lifecycle_survives_reload_and_rollback(
    tmp_path: Path,
) -> None:
    context = _context()
    service = _service(tmp_path)

    evidence = run_synthetic_runtime_acceptance(
        service,
        context,
        _revision_entries(context, "a"),
        _revision_entries(context, "b", stable_managed_ids=True),
    )

    assert evidence.status == "passed"
    assert evidence.activation_versions == (1, 2, 3)
    assert evidence.revision_after_reload == "revision-a"
    assert evidence.revision_after_second_activation == "revision-b"
    assert evidence.revision_after_rollback == "revision-a"
    assert evidence.group_ids_after_reload == ("group-a",)
    assert evidence.group_ids_after_second_activation == ("group-b",)
    assert evidence.group_ids_after_rollback == ("group-a",)
    assert evidence.foreign_context_error_code == "active_revision_missing"
    assert evidence.kill_switch_disabled_selected_source == "legacy"
    assert evidence.audit_chain_valid is True
    assert evidence.redacted is True
