from __future__ import annotations

import pytest

from core.admin_catalog import normalize_source_records
from core.admin_catalog.contracts import CatalogContext, CatalogEntry, EntryType


def _context() -> CatalogContext:
    return CatalogContext(
        operator_id="operator-f5b",
        workspace_id="workspace-f5b",
        tenant_id="tenant-f5b",
        scope="workspace",
    )


def _known(entry_type: EntryType, entry_id: str) -> CatalogEntry:
    data_by_type: dict[EntryType, dict[str, object]] = {
        EntryType.GROUP: {"label": entry_id, "enabled": True},
        EntryType.REMEDY: {"label": entry_id, "enabled": True},
        EntryType.PATHOGEN: {"label": entry_id, "enabled": True},
    }
    return CatalogEntry(
        entry_type=entry_type,
        entry_id=entry_id,
        context=_context(),
        source_id="known-fixture",
        provenance="f5b-known-fixture",
        data=data_by_type[entry_type],
    )


@pytest.mark.parametrize(
    ("data_type", "record", "expected_type", "known_entries"),
    (
        (
            "profile",
            {"id": "profile-a", "label": "Profile A", "group_ids": ["group-a"]},
            EntryType.PROFILE,
            (_known(EntryType.GROUP, "group-a"),),
        ),
        (
            "group",
            {"id": "group-a", "label": "Group A"},
            EntryType.GROUP,
            (),
        ),
        (
            "remedy",
            {"id": "remedy-a", "label": "Remedy A"},
            EntryType.REMEDY,
            (),
        ),
        (
            "pathogen",
            {"id": "pathogen-a", "label": "Pathogen A"},
            EntryType.PATHOGEN,
            (),
        ),
        (
            "multiplex",
            {
                "id": "multiplex-a",
                "label": "Multiplex A",
                "group_ids": ["group-a"],
                "remedy_ids": ["remedy-a"],
            },
            EntryType.MULTIPLEX,
            (
                _known(EntryType.GROUP, "group-a"),
                _known(EntryType.REMEDY, "remedy-a"),
            ),
        ),
        (
            "terminology",
            {
                "id": "term-a",
                "code": "A-1",
                "label": "Term A",
                "scheme": "fixture",
                "target_entry_id": "group-a",
                "target_entry_type": "group",
            },
            EntryType.TERMINOLOGY,
            (_known(EntryType.GROUP, "group-a"),),
        ),
        (
            "relation",
            {
                "id": "relation-a",
                "pathogen_id": "pathogen-a",
                "priority": 1,
                "relation_type": "remedy_pathogen",
                "remedy_id": "remedy-a",
            },
            EntryType.RELATION,
            (
                _known(EntryType.PATHOGEN, "pathogen-a"),
                _known(EntryType.REMEDY, "remedy-a"),
            ),
        ),
    ),
)
def test_each_source_data_type_uses_its_closed_catalog_schema(
    data_type: str,
    record: dict[str, object],
    expected_type: EntryType,
    known_entries: tuple[CatalogEntry, ...],
) -> None:
    result = normalize_source_records(
        source_id="source-a",
        data_type=data_type,
        records=[record],
        context=_context(),
        known_entries=known_entries,
    )

    assert result.quarantined == ()
    assert len(result.normalized) == 1
    normalized = result.normalized[0]
    assert normalized.entry.entry_type is expected_type
    assert normalized.entry.entry_id == record["id"]
    assert normalized.entry.data.get("label") == record.get("label")


def test_normalized_record_canonically_binds_source_and_source_record_identity() -> None:
    result = normalize_source_records(
        source_id="source-a",
        data_type="group",
        records=[{"id": "group-a", "label": "Group A"}],
        context=_context(),
    )

    assert result.normalized[0].canonical_mapping() == {
        "entry": result.normalized[0].entry.canonical_mapping(),
        "source_id": "source-a",
        "source_record_id": "group-a",
    }


def test_unknown_claim_is_quarantined_without_raw_payload_copy() -> None:
    result = normalize_source_records(
        source_id="source-a",
        data_type="group",
        records=[
            {"id": "group-good", "label": "Good"},
            {
                "id": "group-claim",
                "label": "Claim",
                "unverified_claim": "not a catalog field",
            },
        ],
        context=_context(),
    )

    assert [item.source_record_id for item in result.normalized] == ["group-good"]
    assert len(result.quarantined) == 1
    quarantined = result.quarantined[0]
    assert quarantined.source_id == "source-a"
    assert quarantined.source_record_id == "group-claim"
    assert quarantined.reason_codes == ("invalid_claim",)
    assert len(quarantined.source_record_sha256) == 64
    assert not hasattr(quarantined, "raw_record")


def test_unknown_typed_reference_is_quarantined() -> None:
    result = normalize_source_records(
        source_id="source-a",
        data_type="profile",
        records=[
            {
                "id": "profile-a",
                "label": "Profile A",
                "group_ids": ["missing-group"],
            }
        ],
        context=_context(),
    )

    assert result.normalized == ()
    assert result.quarantined[0].source_record_id == "profile-a"
    assert result.quarantined[0].reason_codes == ("unknown_reference",)


@pytest.mark.parametrize(
    "active_content",
    (
        "<strong>render me</strong>",
        "javascript:alert(1)",
        "download payload.exe",
    ),
)
def test_html_script_and_executable_payloads_are_quarantined(
    active_content: str,
) -> None:
    result = normalize_source_records(
        source_id="source-a",
        data_type="group",
        records=[
            {
                "id": "group-active-content",
                "label": "Unsafe",
                "description": active_content,
            }
        ],
        context=_context(),
    )

    assert result.normalized == ()
    assert result.quarantined[0].reason_codes == ("forbidden_payload",)


def test_normalized_source_record_id_collisions_quarantine_all_claimants() -> None:
    result = normalize_source_records(
        source_id="source-a",
        data_type="group",
        records=[
            {"id": "Group-A", "label": "First"},
            {"id": "group-a", "label": "Second"},
        ],
        context=_context(),
    )

    assert result.normalized == ()
    assert [item.source_record_id for item in result.quarantined] == [
        "Group-A",
        "group-a",
    ]
    assert all(
        item.reason_codes == ("duplicate_record_id",)
        for item in result.quarantined
    )


def test_normalization_result_is_deterministic_across_input_order() -> None:
    records = [
        {"id": "group-z", "label": "Z"},
        {"id": "group-a", "label": "A"},
        {"id": "group-q", "label": "Q", "unknown_claim": True},
    ]

    forward = normalize_source_records(
        source_id="source-a",
        data_type="group",
        records=records,
        context=_context(),
    )
    reverse = normalize_source_records(
        source_id="source-a",
        data_type="group",
        records=reversed(records),
        context=_context(),
    )

    assert [item.source_record_id for item in forward.normalized] == [
        "group-a",
        "group-z",
    ]
    assert forward.canonical_json() == reverse.canonical_json()
    assert forward.sha256 == reverse.sha256
