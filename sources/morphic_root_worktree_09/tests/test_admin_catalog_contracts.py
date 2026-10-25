from __future__ import annotations

from dataclasses import replace

import pytest

from core.admin_catalog.contracts import (
    CatalogContext,
    CatalogEntry,
    ContractError,
    EntryType,
    RelationType,
    _freeze_json,
)


def _context(**overrides: str) -> CatalogContext:
    values = {
        "operator_id": "operator@example-host",
        "workspace_id": "ws-1234",
        "tenant_id": "tenant-1234",
        "scope": "workspace",
    }
    values.update(overrides)
    return CatalogContext(**values)


def _entry(entry_type: EntryType, entry_id: str, data: dict[str, object]) -> CatalogEntry:
    return CatalogEntry(
        entry_type=entry_type,
        entry_id=entry_id,
        context=_context(),
        source_id="legacy-fixture",
        provenance="synthetic-test",
        data=data,
    )


def test_entry_types_and_relation_types_are_closed() -> None:
    assert {item.value for item in EntryType} == {
        "profile",
        "group",
        "remedy",
        "pathogen",
        "multiplex",
        "terminology",
        "relation",
    }
    assert {item.value for item in RelationType} == {"remedy_pathogen"}


def test_context_binds_operator_workspace_tenant_and_scope() -> None:
    context = _context()

    assert context.canonical_mapping() == {
        "operator_id": "operator@example-host",
        "scope": "workspace",
        "tenant_id": "tenant-1234",
        "workspace_id": "ws-1234",
    }


@pytest.mark.parametrize(
    "value",
    ["", " leading", "contains space", "../escape", "slash/value", "umlaut-ä", "x" * 129],
)
def test_context_rejects_unstable_identifiers(value: str) -> None:
    with pytest.raises(ContractError):
        _context(tenant_id=value)


def test_profile_and_multiplex_references_are_typed_lists() -> None:
    profile = _entry(
        EntryType.PROFILE,
        "profile-a",
        {"label": "Profile A", "group_ids": ["group-a"], "enabled": True},
    )
    multiplex = _entry(
        EntryType.MULTIPLEX,
        "multiplex-a",
        {
            "label": "Multiplex A",
            "group_ids": ["group-a"],
            "remedy_ids": ["remedy-a"],
            "enabled": True,
        },
    )

    assert profile.data["group_ids"] == ("group-a",)
    assert multiplex.data["remedy_ids"] == ("remedy-a",)


@pytest.mark.parametrize(
    ("entry_type", "data"),
    [
        (EntryType.PROFILE, {"label": "P", "group_ids": "group-a"}),
        (EntryType.MULTIPLEX, {"label": "M", "group_ids": [], "remedy_ids": "remedy-a"}),
    ],
)
def test_reference_fields_reject_strings_instead_of_lists(
    entry_type: EntryType, data: dict[str, object]
) -> None:
    with pytest.raises(ContractError):
        _entry(entry_type, "entry-a", data)


def test_remedy_pathogen_relation_preserves_typed_targets_and_priority() -> None:
    relation = _entry(
        EntryType.RELATION,
        "relation-a",
        {
            "relation_type": RelationType.REMEDY_PATHOGEN.value,
            "remedy_id": "remedy-a",
            "pathogen_id": "pathogen-a",
            "priority": 17,
            "enabled": True,
        },
    )

    assert relation.data == {
        "enabled": True,
        "pathogen_id": "pathogen-a",
        "priority": 17,
        "relation_type": "remedy_pathogen",
        "remedy_id": "remedy-a",
    }


@pytest.mark.parametrize("entry_type", [EntryType.REMEDY, EntryType.MULTIPLEX])
def test_managed_entry_tombstone_is_explicit_and_disabled(
    entry_type: EntryType,
) -> None:
    data: dict[str, object] = {
        "label": "Retained identity",
        "enabled": False,
        "tombstoned": True,
    }
    if entry_type is EntryType.MULTIPLEX:
        data.update(
            {
                "group_ids": ["historical-group"],
                "remedy_ids": ["historical-remedy"],
            }
        )

    entry = _entry(entry_type, "managed-a", data)

    assert entry.data["enabled"] is False
    assert entry.data["tombstoned"] is True


@pytest.mark.parametrize("entry_type", [EntryType.REMEDY, EntryType.MULTIPLEX])
def test_managed_entry_tombstone_cannot_remain_enabled(entry_type: EntryType) -> None:
    data: dict[str, object] = {
        "label": "Invalid tombstone",
        "enabled": True,
        "tombstoned": True,
    }
    if entry_type is EntryType.MULTIPLEX:
        data.update({"group_ids": [], "remedy_ids": []})

    with pytest.raises(ContractError, match="tombstoned .* must be disabled"):
        _entry(entry_type, "managed-a", data)


def test_relation_requires_non_empty_record_provenance() -> None:
    with pytest.raises(ContractError, match="provenance"):
        CatalogEntry(
            entry_type=EntryType.RELATION,
            entry_id="relation-a",
            context=_context(),
            source_id="fixture",
            provenance=" ",
            data={
                "relation_type": RelationType.REMEDY_PATHOGEN.value,
                "remedy_id": "remedy-a",
                "pathogen_id": "pathogen-a",
                "priority": 0,
            },
        )


@pytest.mark.parametrize("priority", [-1, 1.5, "1", True])
def test_relation_priority_must_be_a_non_negative_integer(priority: object) -> None:
    with pytest.raises(ContractError):
        _entry(
            EntryType.RELATION,
            "relation-a",
            {
                "relation_type": "remedy_pathogen",
                "remedy_id": "remedy-a",
                "pathogen_id": "pathogen-a",
                "priority": priority,
            },
        )


def test_terminology_requires_explicit_target_mapping() -> None:
    terminology = _entry(
        EntryType.TERMINOLOGY,
        "mesh-d012345",
        {
            "label": "Synthetic term",
            "scheme": "mesh",
            "code": "D012345",
            "target_entry_id": "pathogen-a",
            "target_entry_type": "pathogen",
            "enabled": True,
        },
    )

    assert terminology.data["target_entry_id"] == "pathogen-a"
    assert terminology.data["target_entry_type"] == "pathogen"
    assert "scan_group_id" not in terminology.data


def test_terminology_rejects_an_unknown_target_type() -> None:
    with pytest.raises(ContractError, match="target_entry_type"):
        _entry(
            EntryType.TERMINOLOGY,
            "mesh-d012345",
            {
                "label": "Synthetic term",
                "scheme": "mesh",
                "code": "D012345",
                "target_entry_id": "pathogen-a",
                "target_entry_type": "unknown",
            },
        )


@pytest.mark.parametrize(
    "pii_field",
    ["patient_id", "patient_name", "email", "phone", "address", "birth_date", "dob"],
)
def test_domain_records_reject_pii_fields(pii_field: str) -> None:
    with pytest.raises(ContractError, match="PII"):
        _entry(EntryType.GROUP, "group-a", {"label": "Group A", pii_field: "secret"})


def test_unknown_fields_are_rejected() -> None:
    with pytest.raises(ContractError, match="unknown"):
        _entry(EntryType.REMEDY, "remedy-a", {"label": "R", "surprise": 1})


@pytest.mark.parametrize("payload", [b"bytes", object(), lambda: None])
def test_executable_or_non_json_payloads_are_rejected(payload: object) -> None:
    with pytest.raises(ContractError):
        _entry(EntryType.GROUP, "group-a", {"label": "Group A", "description": payload})


def test_contract_is_immutable_and_canonical_payload_is_deterministic() -> None:
    first = _entry(
        EntryType.GROUP,
        "Group-A",
        {"enabled": True, "label": "Group A", "aliases": ["Alias-B", "alias-a"]},
    )
    second = _entry(
        EntryType.GROUP,
        "Group-A",
        {"aliases": ["Alias-B", "alias-a"], "label": "Group A", "enabled": True},
    )

    assert first.canonical_json() == second.canonical_json()
    assert first.payload_hash == second.payload_hash
    with pytest.raises((TypeError, AttributeError)):
        first.data["label"] = "Changed"  # type: ignore[index]
    with pytest.raises(ContractError):
        replace(first, entry_id="../escape")


def test_constructor_rejects_unknown_top_level_fields() -> None:
    with pytest.raises(TypeError):
        CatalogEntry(  # type: ignore[call-arg]
            entry_type=EntryType.GROUP,
            entry_id="group-a",
            context=_context(),
            source_id="fixture",
            provenance="synthetic",
            data={"label": "Group A"},
            executable="no",
        )


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_json_boundary_rejects_non_finite_floats(value: float) -> None:
    with pytest.raises(ContractError, match="finite"):
        _freeze_json(value, "synthetic_json_field")
