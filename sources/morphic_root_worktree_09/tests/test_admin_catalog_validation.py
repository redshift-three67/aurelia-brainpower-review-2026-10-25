from __future__ import annotations

from core.admin_catalog.contracts import CatalogContext, CatalogEntry, EntryType
from core.admin_catalog.validation import ValidationIssue, validate_entries


def _context(suffix: str = "a") -> CatalogContext:
    return CatalogContext(
        operator_id=f"operator-{suffix}",
        workspace_id=f"workspace-{suffix}",
        tenant_id=f"tenant-{suffix}",
        scope="workspace",
    )


def _entry(
    entry_type: EntryType,
    entry_id: str,
    data: dict[str, object],
    *,
    context: CatalogContext | None = None,
) -> CatalogEntry:
    return CatalogEntry(
        entry_type=entry_type,
        entry_id=entry_id,
        context=context or _context(),
        source_id="fixture",
        provenance="synthetic-test",
        data=data,
    )


def _group(entry_id: str, *, enabled: bool = True, context: CatalogContext | None = None) -> CatalogEntry:
    return _entry(
        EntryType.GROUP,
        entry_id,
        {"label": entry_id, "enabled": enabled},
        context=context,
    )


def _remedy(entry_id: str, *, enabled: bool = True) -> CatalogEntry:
    return _entry(EntryType.REMEDY, entry_id, {"label": entry_id, "enabled": enabled})


def _pathogen(
    entry_id: str,
    *,
    enabled: bool = True,
    context: CatalogContext | None = None,
) -> CatalogEntry:
    return _entry(
        EntryType.PATHOGEN,
        entry_id,
        {"label": entry_id, "enabled": enabled},
        context=context,
    )


def _terminology(
    entry_id: str,
    *,
    enabled: bool = True,
    context: CatalogContext | None = None,
) -> CatalogEntry:
    return _entry(
        EntryType.TERMINOLOGY,
        entry_id,
        {
            "label": entry_id,
            "scheme": "synthetic",
            "code": entry_id.upper(),
            "target_entry_id": "pathogen-a",
            "target_entry_type": "pathogen",
            "enabled": enabled,
        },
        context=context,
    )


def _codes(issues: tuple[ValidationIssue, ...]) -> list[str]:
    return [issue.code for issue in issues]


def test_valid_cross_referenced_catalog_has_no_issues() -> None:
    entries = [
        _group("group-a"),
        _remedy("remedy-a"),
        _pathogen("pathogen-a"),
        _entry(
            EntryType.PROFILE,
            "profile-a",
            {"label": "Profile A", "group_ids": ["group-a"], "enabled": True},
        ),
        _entry(
            EntryType.MULTIPLEX,
            "multiplex-a",
            {
                "label": "Multiplex A",
                "group_ids": ["group-a"],
                "remedy_ids": ["remedy-a"],
                "enabled": True,
            },
        ),
        _entry(
            EntryType.RELATION,
            "relation-a",
            {
                "relation_type": "remedy_pathogen",
                "remedy_id": "remedy-a",
                "pathogen_id": "pathogen-a",
                "priority": 7,
                "enabled": True,
            },
        ),
        _entry(
            EntryType.TERMINOLOGY,
            "mesh-a",
            {
                "label": "Mesh A",
                "scheme": "mesh",
                "code": "D000001",
                "target_entry_id": "pathogen-a",
                "target_entry_type": "pathogen",
                "enabled": True,
            },
        ),
    ]

    result = validate_entries(entries)

    assert result.is_valid is True
    assert result.errors == ()
    assert result.warnings == ()


def test_terminology_ids_are_typed_enabled_context_bound_references() -> None:
    context = _context()
    foreign = _context("foreign")
    valid = validate_entries(
        [
            _pathogen("pathogen-a", context=context),
            _terminology("term-a", context=context),
            _entry(
                EntryType.REMEDY,
                "remedy-a",
                {"label": "Remedy A", "terminology_ids": ["term-a"]},
                context=context,
            ),
        ]
    )
    unknown = validate_entries(
        [
            _entry(
                EntryType.REMEDY,
                "remedy-a",
                {"label": "Remedy A", "terminology_ids": ["missing-term"]},
                context=context,
            )
        ]
    )
    wrong_type = validate_entries(
        [
            _group("group-a", context=context),
            _entry(
                EntryType.REMEDY,
                "remedy-a",
                {"label": "Remedy A", "terminology_ids": ["group-a"]},
                context=context,
            ),
        ]
    )
    disabled = validate_entries(
        [
            _pathogen("pathogen-a", context=context),
            _terminology("term-a", enabled=False, context=context),
            _entry(
                EntryType.REMEDY,
                "remedy-a",
                {"label": "Remedy A", "terminology_ids": ["term-a"]},
                context=context,
            ),
        ]
    )
    cross_context = validate_entries(
        [
            _pathogen("pathogen-a", context=foreign),
            _terminology("term-a", context=foreign),
            _entry(
                EntryType.REMEDY,
                "remedy-a",
                {"label": "Remedy A", "terminology_ids": ["term-a"]},
                context=context,
            ),
        ]
    )

    assert valid.errors == ()
    assert _codes(unknown.errors) == ["unknown_reference"]
    assert _codes(wrong_type.errors) == ["wrong_reference_type"]
    assert _codes(disabled.errors) == ["disabled_reference"]
    assert "cross_context_reference" in _codes(cross_context.errors)


def test_managed_tombstone_keeps_historical_terminology_ids_without_revalidation() -> None:
    tombstone = _entry(
        EntryType.REMEDY,
        "remedy-a",
        {
            "label": "Remedy A",
            "enabled": False,
            "terminology_ids": ["historical-term"],
            "tombstoned": True,
        },
    )

    assert validate_entries([tombstone]).errors == ()


def test_profile_rejects_an_unknown_group() -> None:
    profile = _entry(
        EntryType.PROFILE,
        "profile-a",
        {"label": "Profile A", "group_ids": ["missing-group"]},
    )

    result = validate_entries([profile])

    assert _codes(result.errors) == ["unknown_reference"]
    assert result.errors[0].field == "group_ids"
    assert result.errors[0].target_id == "missing-group"


def test_multiplex_rejects_unknown_group_and_remedy_in_deterministic_order() -> None:
    multiplex = _entry(
        EntryType.MULTIPLEX,
        "multiplex-a",
        {
            "label": "Multiplex A",
            "group_ids": ["missing-z"],
            "remedy_ids": ["missing-a"],
        },
    )

    result = validate_entries([multiplex])

    assert [(issue.field, issue.target_id) for issue in result.errors] == [
        ("group_ids", "missing-z"),
        ("remedy_ids", "missing-a"),
    ]


def test_tombstoned_multiplex_retains_historical_references_without_reactivating_them() -> None:
    tombstone = _entry(
        EntryType.MULTIPLEX,
        "multiplex-a",
        {
            "label": "Retained multiplex",
            "group_ids": ["missing-historical-group"],
            "remedy_ids": ["missing-historical-remedy"],
            "enabled": False,
            "tombstoned": True,
        },
    )

    result = validate_entries([tombstone])

    assert result.is_valid
    assert result.errors == ()
    assert result.warnings == ()


def test_relation_rejects_unknown_or_wrongly_typed_targets() -> None:
    relation = _entry(
        EntryType.RELATION,
        "relation-a",
        {
            "relation_type": "remedy_pathogen",
            "remedy_id": "group-a",
            "pathogen_id": "missing-pathogen",
            "priority": 1,
        },
    )

    result = validate_entries([_group("group-a"), relation])

    assert _codes(result.errors) == ["unknown_reference", "wrong_reference_type"]
    assert {issue.field for issue in result.errors} == {"pathogen_id", "remedy_id"}


def test_terminology_reference_is_type_and_context_bound() -> None:
    terminology = _entry(
        EntryType.TERMINOLOGY,
        "term-a",
        {
            "label": "Term A",
            "scheme": "test",
            "code": "A",
            "target_entry_id": "target-a",
            "target_entry_type": "pathogen",
        },
    )

    wrong_type = validate_entries([_group("target-a"), terminology])
    foreign_context = validate_entries(
        [_pathogen("target-a", context=_context("foreign")), terminology]
    )

    assert "wrong_reference_type" in _codes(wrong_type.errors)
    assert "mixed_context" in _codes(foreign_context.errors)
    assert "cross_context_reference" in _codes(foreign_context.errors)


def test_alias_cycles_and_duplicate_aliases_are_rejected() -> None:
    first = _entry(
        EntryType.GROUP,
        "group-a",
        {"label": "A", "aliases": ["group-b", "shared-alias"]},
    )
    second = _entry(
        EntryType.GROUP,
        "group-b",
        {"label": "B", "aliases": ["group-a", "shared-alias"]},
    )

    result = validate_entries([second, first])

    assert "alias_cycle" in _codes(result.errors)
    assert "duplicate_alias" in _codes(result.errors)


def test_disabled_reference_targets_fail_closed_by_default() -> None:
    profile = _entry(
        EntryType.PROFILE,
        "profile-a",
        {"label": "P", "group_ids": ["group-a"]},
    )

    blocked = validate_entries([_group("group-a", enabled=False), profile])
    allowed = validate_entries(
        [_group("group-a", enabled=False), profile], allow_disabled_targets=True
    )

    assert _codes(blocked.errors) == ["disabled_reference"]
    assert allowed.errors == ()
    assert _codes(allowed.warnings) == ["disabled_reference_allowed"]


def test_empty_reference_sets_fail_closed_but_can_be_explicitly_allowed() -> None:
    profile = _entry(
        EntryType.PROFILE,
        "profile-a",
        {"label": "P", "group_ids": []},
    )
    multiplex = _entry(
        EntryType.MULTIPLEX,
        "multiplex-a",
        {"label": "M", "group_ids": [], "remedy_ids": []},
    )

    blocked = validate_entries([multiplex, profile])
    allowed = validate_entries([multiplex, profile], allow_empty_targets=True)

    assert _codes(blocked.errors) == ["empty_references", "empty_references"]
    assert allowed.errors == ()
    assert _codes(allowed.warnings) == [
        "empty_references_allowed",
        "empty_references_allowed",
    ]


def test_normalized_identifier_collisions_are_rejected() -> None:
    result = validate_entries([_group("Group-A"), _group("group-a")])

    assert _codes(result.errors) == ["normalized_id_collision"]


def test_issues_are_deterministic_for_reversed_input() -> None:
    entries = [
        _entry(
            EntryType.PROFILE,
            "profile-z",
            {"label": "Z", "group_ids": ["missing-z"]},
        ),
        _entry(
            EntryType.PROFILE,
            "profile-a",
            {"label": "A", "group_ids": ["missing-a"]},
        ),
    ]

    first = validate_entries(entries)
    second = validate_entries(list(reversed(entries)))

    assert first == second
    assert [issue.entry_id for issue in first.errors] == ["profile-a", "profile-z"]


def test_alias_cannot_shadow_another_canonical_id_case_insensitively() -> None:
    owner = _entry(
        EntryType.GROUP,
        "group-a",
        {"label": "A", "aliases": ["GROUP-B"]},
    )
    canonical_target = _group("group-b")

    result = validate_entries([owner, canonical_target])

    assert _codes(result.errors) == ["alias_canonical_collision"]
    assert result.errors[0].entry_id == "group-a"
    assert result.errors[0].target_id == "group-b"


def test_exact_duplicate_resolution_is_independent_of_input_order() -> None:
    enabled = _group("group-a")
    disabled = _entry(
        EntryType.GROUP,
        "group-a",
        {"label": "Disabled A", "enabled": False},
    )
    profile = _entry(
        EntryType.PROFILE,
        "profile-a",
        {"label": "Profile A", "group_ids": ["group-a"]},
    )

    first = validate_entries([enabled, disabled, profile])
    second = validate_entries([disabled, enabled, profile])

    assert first == second
    assert "normalized_id_collision" in _codes(first.errors)
