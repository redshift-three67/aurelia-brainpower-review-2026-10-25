from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from core.admin_catalog import (
    AdminCatalogService,
    CatalogServiceError,
    CatalogContext,
    CatalogEntry,
    ContractError,
    DraftConflictError,
    EntryType,
    ProfileConflictError,
    ProfileNotFoundError,
    ProfileStateError,
    ProfileTypeError,
    ProfileValidationError,
)
from core.admin_catalog.store import (
    CatalogStore,
    CatalogStoreError,
    ProfileRemovalError,
    TombstoneMutationError,
)
from core.admin_catalog.validation_attestation import HmacValidationKeyProvider
from core.profile_sync import MASTER_PROFILES


def _catalog_store(path: Path) -> CatalogStore:
    return CatalogStore(
        path,
        validation_key_provider=HmacValidationKeyProvider(
            authority_id="admin-profile-tests",
            active_key_id="test-v1",
            keys={"test-v1": b"K" * 32},
        ),
    )


def _context(suffix: str = "a") -> CatalogContext:
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
        source_id="synthetic-fixture",
        provenance="f3-profile-management-test",
        data=data,
    )


def _group(context: CatalogContext, entry_id: str) -> CatalogEntry:
    return _entry(
        context,
        EntryType.GROUP,
        entry_id,
        {"label": entry_id, "enabled": True},
    )


def _profile(
    context: CatalogContext,
    entry_id: str = "profile-a",
    *,
    group_ids: list[str] | None = None,
    aliases: list[str] | None = None,
    enabled: bool = True,
    label: str | None = None,
    tombstoned: bool = False,
) -> CatalogEntry:
    data: dict[str, object] = {
        "label": label or entry_id,
        "group_ids": group_ids if group_ids is not None else ["group-a"],
        "enabled": enabled,
        "category": "synthetic-category",
        "level": 2,
    }
    if tombstoned:
        data["tombstoned"] = True
    if aliases is not None:
        data["aliases"] = aliases
    return _entry(context, EntryType.PROFILE, entry_id, data)


def _service(tmp_path: Path) -> AdminCatalogService:
    return AdminCatalogService(_catalog_store(tmp_path / "catalog.db"))


def _draft_entries(
    service: AdminCatalogService, context: CatalogContext, draft_id: str = "draft-1"
) -> tuple[CatalogEntry, ...]:
    entries = service.store.get_draft_entries(context, draft_id)
    assert entries is not None
    return entries


def _draft_profile(
    service: AdminCatalogService,
    context: CatalogContext,
    profile_id: str = "profile-a",
) -> CatalogEntry:
    matches = [
        entry
        for entry in _draft_entries(service, context)
        if entry.entry_type is EntryType.PROFILE and entry.entry_id == profile_id
    ]
    assert len(matches) == 1
    return matches[0]


def test_create_profile_adds_only_to_existing_draft(tmp_path: Path) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(context, "draft-1", [_group(context, "group-a")])

    state = service.create_profile(
        context,
        "draft-1",
        _profile(context),
        expected_version=1,
    )

    assert state.version == 2
    assert state.entry_ids == ("group-a", "profile-a")
    assert _draft_profile(service, context).data["enabled"] is True
    assert service.store.list_revision_ids(context) == []
    assert service.store.current_revision_id(context) is None


def test_profile_create_rejects_duplicate_id_wrong_type_and_foreign_context(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    foreign = _context("foreign")
    service.create_draft(
        context,
        "draft-1",
        [_group(context, "group-a"), _profile(context)],
    )

    with pytest.raises(ProfileConflictError):
        service.create_profile(
            context, "draft-1", _profile(context), expected_version=1
        )
    with pytest.raises(ProfileTypeError, match="profile"):
        service.create_profile(
            context,
            "draft-1",
            _group(context, "group-b"),
            expected_version=1,
        )
    with pytest.raises(ProfileTypeError, match="not a profile"):
        service.create_profile(
            context,
            "draft-1",
            _profile(context, "group-a"),
            expected_version=1,
        )
    with pytest.raises(ProfileValidationError):
        service.create_profile(
            context,
            "draft-1",
            _profile(foreign, "profile-foreign"),
            expected_version=1,
        )
    with pytest.raises(ProfileStateError, match="new profile"):
        service.create_profile(
            context,
            "draft-1",
            _profile(
                context,
                "profile-tombstone",
                enabled=False,
                tombstoned=True,
            ),
            expected_version=1,
        )

    assert service.get_draft(context, "draft-1").version == 1


def test_update_profile_requires_exact_positive_integer_cas_and_preserves_others(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(
        context,
        "draft-1",
        [
            _group(context, "group-a"),
            _group(context, "group-b"),
            _profile(context),
        ],
    )

    with pytest.raises(DraftConflictError):
        service.update_profile(
            context,
            "draft-1",
            "profile-a",
            _profile(context, group_ids=["group-b"]),
            expected_version=True,
        )
    with pytest.raises(DraftConflictError):
        service.update_profile(
            context,
            "draft-1",
            "profile-a",
            _profile(context, group_ids=["group-b"]),
            expected_version=2,
        )
    with pytest.raises(ProfileConflictError, match="identity"):
        service.update_profile(
            context,
            "draft-1",
            "profile-a",
            _profile(context, "profile-renamed", group_ids=["group-b"]),
            expected_version=1,
        )
    with pytest.raises(ProfileStateError, match="delete_profile"):
        service.update_profile(
            context,
            "draft-1",
            "profile-a",
            _profile(context, enabled=False, tombstoned=True),
            expected_version=1,
        )

    state = service.update_profile(
        context,
        "draft-1",
        "profile-a",
        _profile(context, group_ids=["group-b"], label="Updated"),
        expected_version=1,
    )

    assert state.version == 2
    assert _draft_profile(service, context).data["group_ids"] == ("group-b",)
    assert _draft_profile(service, context).data["label"] == "Updated"
    assert {entry.entry_id for entry in _draft_entries(service, context)} == {
        "group-a",
        "group-b",
        "profile-a",
    }


def test_enable_and_disable_profile_preserve_profile_payload(tmp_path: Path) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(
        context,
        "draft-1",
        [
            _group(context, "group-a"),
            _profile(context, enabled=False, aliases=["profile-alias"]),
        ],
    )

    enabled = service.enable_profile(
        context, "draft-1", "profile-a", expected_version=1
    )
    disabled = service.disable_profile(
        context, "draft-1", "profile-a", expected_version=2
    )

    profile = _draft_profile(service, context)
    assert enabled.version == 2
    assert disabled.version == 3
    assert profile.data["enabled"] is False
    assert profile.data["group_ids"] == ("group-a",)
    assert profile.data["aliases"] == ("profile-alias",)


def test_delete_profile_is_a_retained_disabled_tombstone(tmp_path: Path) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(
        context,
        "draft-1",
        [_group(context, "group-a"), _profile(context)],
    )

    state = service.delete_profile(
        context, "draft-1", "profile-a", expected_version=1
    )

    profile = _draft_profile(service, context)
    assert state.version == 2
    assert profile.entry_id == "profile-a"
    assert profile.data["enabled"] is False
    assert profile.data["tombstoned"] is True
    assert profile.data["group_ids"] == ("group-a",)


def test_generic_draft_update_cannot_hard_delete_an_unpublished_profile(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(
        context,
        "draft-1",
        [_group(context, "group-a"), _profile(context)],
    )

    with pytest.raises(ProfileConflictError, match="tombstone"):
        service.update_draft(
            context,
            "draft-1",
            [_group(context, "group-a")],
            expected_version=1,
        )

    assert service.get_draft(context, "draft-1").version == 1
    assert _draft_profile(service, context).data["enabled"] is True


def test_atomic_store_policy_blocks_profile_added_and_published_during_update(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service = _service(tmp_path)
    context = _context()
    group = _group(context, "group-a")
    service.create_draft(context, "draft-1", [group])
    original_update = service.store.update_draft
    injected = False

    def interleaved_update(
        update_context: CatalogContext,
        draft_id: str,
        entries: tuple[CatalogEntry, ...],
        *,
        expected_version: int,
    ) -> tuple[int, str]:
        nonlocal injected
        if not injected:
            injected = True
            competing = AdminCatalogService(_catalog_store(service.store.db_path))
            competing.create_profile(
                context,
                "draft-1",
                _profile(context),
                expected_version=1,
            )
            assert competing.validate_draft(context, "draft-1").is_valid
            competing.publish_draft(
                context,
                "draft-1",
                "revision-1",
                expected_draft_version=2,
            )
        return original_update(
            update_context,
            draft_id,
            entries,
            expected_version=expected_version,
        )

    monkeypatch.setattr(service.store, "update_draft", interleaved_update)

    with pytest.raises(ProfileConflictError, match="tombstone"):
        service.update_draft(context, "draft-1", [group], expected_version=2)

    assert service.get_draft(context, "draft-1").version == 2
    assert service.get_profile(context, "draft-1", "profile-a").entry_id == "profile-a"
    revision_entries = service.store.get_revision_entries(context, "revision-1")
    assert revision_entries is not None
    assert any(entry.entry_type is EntryType.PROFILE for entry in revision_entries)


def test_published_profile_can_only_be_deleted_as_tombstone(tmp_path: Path) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(
        context,
        "draft-1",
        [_group(context, "group-a"), _profile(context)],
    )
    assert service.validate_draft(context, "draft-1").is_valid
    service.publish_draft(
        context,
        "draft-1",
        "revision-1",
        expected_draft_version=1,
    )

    with pytest.raises(ProfileConflictError, match="tombstone"):
        service.update_draft(
            context,
            "draft-1",
            [_group(context, "group-a")],
            expected_version=1,
        )

    state = service.delete_profile(
        context, "draft-1", "profile-a", expected_version=1
    )
    revision_entries = service.store.get_revision_entries(context, "revision-1")
    assert revision_entries is not None
    revision_profile = next(
        entry for entry in revision_entries if entry.entry_type is EntryType.PROFILE
    )

    assert state.version == 2
    assert _draft_profile(service, context).data["enabled"] is False
    assert _draft_profile(service, context).data["tombstoned"] is True
    assert revision_profile.data["enabled"] is True


def test_publish_rejects_cross_draft_omission_of_a_published_profile(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    group = _group(context, "group-a")
    service.create_draft(context, "draft-source", [group, _profile(context)])
    assert service.validate_draft(context, "draft-source").is_valid
    service.publish_draft(
        context,
        "draft-source",
        "revision-source",
        expected_draft_version=1,
    )
    service.create_draft(context, "draft-bypass", [group])
    assert service.validate_draft(context, "draft-bypass").is_valid

    with pytest.raises(ProfileConflictError, match="tombstone"):
        service.publish_draft(
            context,
            "draft-bypass",
            "revision-bypass",
            expected_draft_version=1,
        )

    assert service.store.list_revision_ids(context) == ["revision-source"]
    assert service.get_draft(context, "draft-bypass").version == 1


def test_new_draft_cannot_forge_an_unpublished_tombstone(tmp_path: Path) -> None:
    service = _service(tmp_path)
    context = _context()
    group = _group(context, "group-a")
    service.create_draft(context, "draft-source", [group, _profile(context)])
    assert service.validate_draft(context, "draft-source").is_valid
    service.publish_draft(
        context,
        "draft-source",
        "revision-source",
        expected_draft_version=1,
    )

    with pytest.raises(ProfileStateError, match="delete_profile"):
        service.create_draft(
            context,
            "draft-forged",
            [group, _profile(context, enabled=False, tombstoned=True)],
        )

    assert service.store.get_draft(context, "draft-forged") is None


def test_low_level_revision_write_cannot_bypass_profile_retention(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    group = _group(context, "group-a")
    service.create_draft(context, "draft-source", [group, _profile(context)])
    assert service.validate_draft(context, "draft-source").is_valid
    service.publish_draft(
        context,
        "draft-source",
        "revision-source",
        expected_draft_version=1,
    )

    with pytest.raises(ProfileRemovalError, match="tombstone"):
        service.store.create_revision(context, "revision-omission", [group])
    with pytest.raises(TombstoneMutationError, match="delete_profile"):
        service.store.create_revision(
            context,
            "revision-forged-tombstone",
            [
                group,
                _profile(context),
                _profile(context, "profile-b", enabled=False, tombstoned=True),
            ],
        )

    assert service.store.list_revision_ids(context) == ["revision-source"]


def test_published_tombstone_is_terminal_across_every_revision_path(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    group = _group(context, "group-a")
    live = _profile(context, aliases=["reserved-alias"])
    service.create_draft(context, "draft-source", [group, live])
    service.create_draft(context, "draft-stale-live", [group, live])
    assert service.validate_draft(context, "draft-source").is_valid
    service.publish_draft(
        context,
        "draft-source",
        "revision-live",
        expected_draft_version=1,
    )
    service.delete_profile(
        context,
        "draft-source",
        "profile-a",
        expected_version=1,
    )
    assert service.validate_draft(context, "draft-source").is_valid
    service.publish_draft(
        context,
        "draft-source",
        "revision-tombstone",
        expected_draft_version=2,
    )

    resurrected = _profile(context, aliases=["replacement-alias"])
    with pytest.raises(ProfileStateError, match="terminal"):
        service.create_draft(
            context,
            "draft-resurrection",
            [group, resurrected],
        )
    assert service.validate_draft(context, "draft-stale-live").is_valid
    with pytest.raises(ProfileStateError, match="terminal"):
        service.publish_draft(
            context,
            "draft-stale-live",
            "revision-resurrection",
            expected_draft_version=1,
        )
    with pytest.raises(TombstoneMutationError, match="terminal"):
        service.store.create_revision(
            context,
            "revision-direct-resurrection",
            [group, resurrected],
        )

    assert service.store.list_revision_ids(context) == [
        "revision-live",
        "revision-tombstone",
    ]


def test_direct_revision_preserves_tombstone_alias_and_allows_identical_carry(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    group = _group(context, "group-a")
    live = _profile(context, aliases=["reserved-alias"])
    service.create_draft(context, "draft-source", [group, live])
    assert service.validate_draft(context, "draft-source").is_valid
    service.publish_draft(
        context,
        "draft-source",
        "revision-live",
        expected_draft_version=1,
    )
    service.delete_profile(
        context,
        "draft-source",
        "profile-a",
        expected_version=1,
    )
    assert service.validate_draft(context, "draft-source").is_valid
    service.publish_draft(
        context,
        "draft-source",
        "revision-tombstone",
        expected_draft_version=2,
    )
    tombstone = service.get_profile(context, "draft-source", "profile-a")

    with pytest.raises(CatalogStoreError, match="duplicate_alias"):
        service.store.create_revision(
            context,
            "revision-alias-theft",
            [
                group,
                tombstone,
                _profile(context, "profile-b", aliases=["reserved-alias"]),
            ],
        )
    with pytest.raises(CatalogStoreError, match="normalized_id_collision"):
        service.store.create_revision(
            context,
            "revision-id-theft",
            [group, tombstone, _group(context, "Profile-A")],
        )
    with pytest.raises(CatalogStoreError, match="alias_canonical_collision"):
        service.store.create_revision(
            context,
            "revision-id-as-alias-theft",
            [
                group,
                tombstone,
                _profile(context, "profile-b", aliases=["Profile-A"]),
            ],
        )
    with pytest.raises(CatalogStoreError, match="alias_canonical_collision"):
        service.store.create_revision(
            context,
            "revision-alias-as-id-theft",
            [group, tombstone, _group(context, "Reserved-Alias")],
        )

    class SwitchingEntries:
        def __init__(self) -> None:
            self.iterations = 0

        def __iter__(self):
            self.iterations += 1
            if self.iterations <= 2:
                return iter((group, tombstone))
            return iter((group, live))

    switching_entries = SwitchingEntries()
    service.store.create_revision(
        context,
        "revision-sequence-snapshot",
        switching_entries,  # type: ignore[arg-type]
    )
    frozen_entries = service.store.get_revision_entries(
        context, "revision-sequence-snapshot"
    )
    assert frozen_entries is not None
    frozen_profile = next(
        entry for entry in frozen_entries if entry.entry_type is EntryType.PROFILE
    )
    assert frozen_profile.payload_hash == tombstone.payload_hash

    service.store.create_revision(
        context,
        "revision-carry",
        [group, tombstone],
    )
    carried = service.store.get_revision_entries(context, "revision-carry")
    assert carried is not None
    carried_tombstone = next(
        entry for entry in carried if entry.entry_type is EntryType.PROFILE
    )
    assert carried_tombstone.payload_hash == tombstone.payload_hash
    assert service.store.list_revision_ids(context) == [
        "revision-carry",
        "revision-live",
        "revision-sequence-snapshot",
        "revision-tombstone",
    ]


def test_generic_draft_context_errors_do_not_leak_or_masquerade_as_missing(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    foreign = _context("foreign")
    local_group = _group(context, "group-a")
    foreign_group = _group(foreign, "group-a")

    with pytest.raises(CatalogServiceError, match="different catalog context"):
        service.create_draft(context, "draft-foreign", [foreign_group])
    assert service.store.get_draft(context, "draft-foreign") is None

    service.create_draft(context, "draft-local", [local_group])
    before = service.get_draft(context, "draft-local")
    with pytest.raises(CatalogServiceError, match="different catalog context"):
        service.update_draft(
            context,
            "draft-local",
            [foreign_group],
            expected_version=1,
        )

    assert service.get_draft(context, "draft-local") == before


def test_store_has_no_public_generic_tombstone_authorization_flag() -> None:
    parameters = inspect.signature(CatalogStore.update_draft).parameters

    assert "allow_profile_tombstone" not in parameters


def test_profile_group_and_alias_validation_fail_closed_without_draft_mutation(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(
        context,
        "draft-1",
        [
            _group(context, "group-a"),
            _profile(context, "profile-a", aliases=["shared-alias"]),
        ],
    )
    before = service.get_draft(context, "draft-1")

    with pytest.raises(ProfileValidationError) as unknown_group:
        service.create_profile(
            context,
            "draft-1",
            _profile(context, "profile-b", group_ids=["missing-group"]),
            expected_version=1,
        )
    assert "unknown_reference" in str(unknown_group.value)

    with pytest.raises(ProfileValidationError) as duplicate_alias:
        service.create_profile(
            context,
            "draft-1",
            _profile(context, "profile-b", aliases=["shared-alias"]),
            expected_version=1,
        )
    assert "duplicate_alias" in str(duplicate_alias.value)

    after = service.get_draft(context, "draft-1")
    assert after == before
    assert tuple(entry.entry_id for entry in _draft_entries(service, context)) == (
        "group-a",
        "profile-a",
    )


def test_generic_draft_update_rejects_invalid_profile_snapshot(tmp_path: Path) -> None:
    service = _service(tmp_path)
    context = _context()
    group = _group(context, "group-a")
    service.create_draft(context, "draft-1", [group, _profile(context)])
    before = service.get_draft(context, "draft-1")

    with pytest.raises(ProfileValidationError) as captured:
        service.update_draft(
            context,
            "draft-1",
            [group, _profile(context, group_ids=["missing-group"])],
            expected_version=1,
        )

    assert tuple(issue.code for issue in captured.value.result.errors) == (
        "unknown_reference",
    )
    assert service.get_draft(context, "draft-1") == before


def test_generic_draft_update_cannot_create_or_transition_to_tombstone(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    group = _group(context, "group-a")
    service.create_draft(context, "draft-live", [group, _profile(context)])
    service.create_draft(context, "draft-new", [group])
    tombstone = _profile(context, enabled=False, tombstoned=True)

    with pytest.raises(ProfileStateError, match="delete_profile"):
        service.update_draft(
            context,
            "draft-live",
            [group, tombstone],
            expected_version=1,
        )
    with pytest.raises(ProfileStateError, match="delete_profile"):
        service.update_draft(
            context,
            "draft-new",
            [group, tombstone],
            expected_version=1,
        )

    assert service.get_draft(context, "draft-live").version == 1
    assert service.get_draft(context, "draft-new").version == 1


def test_successful_draft_update_returns_its_atomic_write_without_reread(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(context, "draft-1", [_group(context, "group-a")])
    updated_group = _entry(
        context,
        EntryType.GROUP,
        "group-a",
        {"label": "Updated", "enabled": True},
    )

    def fail_followup_read(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("successful write result must not be reread")

    monkeypatch.setattr(service, "_state", fail_followup_read)
    state = service.update_draft(
        context,
        "draft-1",
        [updated_group],
        expected_version=1,
    )

    assert state.version == 2
    assert state.entry_ids == ("group-a",)
    assert len(state.payload_hash) == 64


def test_empty_draft_rejects_foreign_profile_context_as_validation_error(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    foreign = _context("foreign")
    service.create_draft(context, "draft-1", [])

    with pytest.raises(ProfileValidationError) as captured:
        service.create_profile(
            context,
            "draft-1",
            _profile(foreign, "profile-foreign"),
            expected_version=1,
        )

    assert tuple(issue.code for issue in captured.value.result.errors) == (
        "cross_context_profile",
    )
    assert service.get_draft(context, "draft-1").version == 1
    assert _draft_entries(service, context) == ()


def test_profile_operations_reject_missing_or_non_profile_targets(tmp_path: Path) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(context, "draft-1", [_group(context, "group-a")])

    with pytest.raises(ProfileNotFoundError):
        service.disable_profile(
            context, "draft-1", "missing-profile", expected_version=1
        )
    with pytest.raises(ProfileNotFoundError):
        service.update_profile(
            context,
            "draft-1",
            "missing-profile",
            _profile(context, "missing-profile"),
            expected_version=1,
        )
    with pytest.raises(ProfileTypeError):
        service.disable_profile(
            context, "draft-1", "group-a", expected_version=1
        )

    assert service.get_draft(context, "draft-1").version == 1


def test_profile_contract_preserves_category_level_and_explicit_tombstone() -> None:
    context = _context()
    profile = _profile(
        context,
        enabled=False,
        tombstoned=True,
    )

    assert profile.data["category"] == "synthetic-category"
    assert profile.data["level"] == 2
    assert profile.data["tombstoned"] is True

    with pytest.raises(ContractError, match="tombstoned profile must be disabled"):
        _profile(context, enabled=True, tombstoned=True)


def test_disable_and_tombstone_are_distinct_persisted_states(tmp_path: Path) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(
        context,
        "draft-1",
        [_group(context, "group-a"), _profile(context)],
    )

    service.disable_profile(context, "draft-1", "profile-a", expected_version=1)
    disabled = service.get_profile(context, "draft-1", "profile-a")
    assert disabled.data["enabled"] is False
    assert disabled.data.get("tombstoned", False) is False

    service.delete_profile(context, "draft-1", "profile-a", expected_version=2)
    tombstone = service.get_profile(context, "draft-1", "profile-a")
    assert tombstone.data["enabled"] is False
    assert tombstone.data["tombstoned"] is True


def test_tombstone_is_terminal_and_reserves_identity_and_alias(tmp_path: Path) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(
        context,
        "draft-1",
        [
            _group(context, "group-a"),
            _profile(context, aliases=["reserved-alias"]),
        ],
    )
    service.delete_profile(context, "draft-1", "profile-a", expected_version=1)

    with pytest.raises(ProfileStateError):
        service.enable_profile(context, "draft-1", "profile-a", expected_version=2)
    with pytest.raises(ProfileStateError):
        service.update_profile(
            context,
            "draft-1",
            "profile-a",
            _profile(context, label="replacement"),
            expected_version=2,
        )
    with pytest.raises(ProfileStateError):
        service.delete_profile(context, "draft-1", "profile-a", expected_version=2)
    with pytest.raises(ProfileConflictError):
        service.create_profile(
            context,
            "draft-1",
            _profile(context, "profile-a"),
            expected_version=2,
        )
    with pytest.raises(ProfileValidationError):
        service.create_profile(
            context,
            "draft-1",
            _profile(context, "profile-b", aliases=["reserved-alias"]),
            expected_version=2,
        )

    assert service.get_draft(context, "draft-1").version == 2


def test_generic_draft_update_cannot_restore_or_modify_a_tombstone(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    group = _group(context, "group-a")
    service.create_draft(context, "draft-1", [group, _profile(context)])
    service.delete_profile(context, "draft-1", "profile-a", expected_version=1)

    with pytest.raises(ProfileStateError):
        service.update_draft(
            context,
            "draft-1",
            [group, _profile(context, label="restored")],
            expected_version=2,
        )

    persisted = service.get_profile(context, "draft-1", "profile-a")
    assert persisted.data["tombstoned"] is True
    assert persisted.data["enabled"] is False
    assert service.get_draft(context, "draft-1").version == 2


def test_tombstone_historical_group_references_do_not_block_validation(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(
        context,
        "draft-1",
        [_group(context, "group-a"), _profile(context)],
    )
    service.delete_profile(context, "draft-1", "profile-a", expected_version=1)
    tombstone = service.get_profile(context, "draft-1", "profile-a")

    service.update_draft(context, "draft-1", [tombstone], expected_version=2)

    assert service.validate_draft(context, "draft-1").is_valid


def test_profile_publication_state_is_finalized_revision_and_context_bound(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    foreign = _context("foreign")
    service.create_draft(
        context,
        "draft-1",
        [_group(context, "group-a"), _profile(context, "Profile-A")],
    )

    before = service.profile_publication_state(context, "profile-a")
    assert before.published is False
    assert before.entry_type is None
    assert before.revision_ids == ()

    assert service.validate_draft(context, "draft-1").is_valid
    service.publish_draft(
        context, "draft-1", "revision-1", expected_draft_version=1
    )

    published = service.profile_publication_state(context, "profile-a")
    assert published.published is True
    assert published.entry_type is EntryType.PROFILE
    assert published.revision_ids == ("revision-1",)
    assert service.profile_publication_state(foreign, "profile-a").published is False


def test_profile_publication_state_rejects_published_non_profile_id(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(context, "draft-1", [_group(context, "group-a")])
    assert service.validate_draft(context, "draft-1").is_valid
    service.publish_draft(
        context, "draft-1", "revision-1", expected_draft_version=1
    )

    with pytest.raises(ProfileTypeError):
        service.profile_publication_state(context, "group-a")


@pytest.mark.parametrize("invalid_version", [True, 0, -1, "1"])
def test_every_profile_mutation_rejects_invalid_cas_without_mutation(
    tmp_path: Path, invalid_version: object
) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(
        context,
        "draft-1",
        [_group(context, "group-a"), _profile(context)],
    )
    before = service.get_draft(context, "draft-1")

    operations = (
        lambda: service.create_profile(
            context,
            "draft-1",
            _profile(context, "profile-b"),
            expected_version=invalid_version,  # type: ignore[arg-type]
        ),
        lambda: service.update_profile(
            context,
            "draft-1",
            "profile-a",
            _profile(context, label="updated"),
            expected_version=invalid_version,  # type: ignore[arg-type]
        ),
        lambda: service.disable_profile(
            context,
            "draft-1",
            "profile-a",
            expected_version=invalid_version,  # type: ignore[arg-type]
        ),
        lambda: service.delete_profile(
            context,
            "draft-1",
            "profile-a",
            expected_version=invalid_version,  # type: ignore[arg-type]
        ),
    )
    for operation in operations:
        with pytest.raises(DraftConflictError):
            operation()
        assert service.get_draft(context, "draft-1") == before


def test_profile_validation_error_exposes_deterministic_result(tmp_path: Path) -> None:
    service = _service(tmp_path)
    context = _context()
    service.create_draft(context, "draft-1", [_group(context, "group-a")])

    with pytest.raises(ProfileValidationError) as captured:
        service.create_profile(
            context,
            "draft-1",
            _profile(context, group_ids=["missing-group"]),
            expected_version=1,
        )

    assert captured.value.result.is_valid is False
    assert tuple(issue.code for issue in captured.value.result.errors) == (
        "unknown_reference",
    )


def test_profile_management_and_catalog_activation_have_no_legacy_engine_effect(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    context = _context()
    before = tuple(sorted((key, id(value)) for key, value in MASTER_PROFILES.items()))
    service.create_draft(
        context,
        "draft-1",
        [_group(context, "group-a"), _profile(context, "catalog-only-profile")],
    )
    assert service.validate_draft(context, "draft-1").is_valid
    service.publish_draft(
        context,
        "draft-1",
        "revision-1",
        expected_draft_version=1,
    )
    service.activate_revision(
        context,
        "revision-1",
        expected_previous_revision_id=None,
        expected_activation_version=0,
        actor_id="operator-a",
        reason="synthetic F3.2 isolation proof",
    )

    assert "catalog-only-profile" not in MASTER_PROFILES
    assert tuple(sorted((key, id(value)) for key, value in MASTER_PROFILES.items())) == before
