"""Offline Admin-Catalog-Service fuer Feedback-f-Gate F2.1.

Keine Runtime-, Web-, CLI- oder Netzwerkverdrahtung. Alle Mutationen bleiben im
explizit injizierten :class:`CatalogStore`.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Sequence

from .contracts import CatalogContext, CatalogEntry, EntryType, normalize_catalog_id
from .store import (
    CatalogStore,
    CatalogStoreError,
    ConcurrencyError,

    EntryPublicationState,
    ManagedEntryReferenceError,
    ManagedEntryRemovalError,
    ManagedEntryTombstoneError,
    ProfileRemovalError,
    StoreAccessError,
    TombstoneMutationError,
)
from .validation import ValidationIssue, ValidationResult, validate_entries


class CatalogServiceError(RuntimeError):
    """Basisklasse fuer F2.1-Servicevertragsverletzungen."""


class DraftNotFoundError(CatalogServiceError):
    """Der Draft ist im angefragten Kontext nicht sichtbar."""


class DraftConflictError(CatalogServiceError):
    """Die erwartete Draft-Version ist veraltet."""


class DraftValidationError(CatalogServiceError):
    """Der Draft besitzt keine aktuelle erfolgreiche Validierung."""


class PublishedDraftError(CatalogServiceError):
    """Die Draft-ID ist als Revisionsprovenienz referenziell gebunden."""


class RevisionConflictError(CatalogServiceError):
    """Die angeforderte Revisions-ID ist im Kontext bereits vergeben."""


class ProfileConflictError(CatalogServiceError):
    """Eine Profilmutation kollidiert mit dem aktuellen Draftzustand."""


class ProfileNotFoundError(CatalogServiceError):
    """Das Profil ist im angefragten Draft nicht vorhanden."""


class ProfileTypeError(CatalogServiceError):
    """Eine Catalog-ID ist vorhanden, bezeichnet aber kein Profil."""


class ProfileStateError(CatalogServiceError):
    """Der persistierte Profil-Lifecycle erlaubt die Mutation nicht."""


class ProfileValidationError(CatalogServiceError):
    """Eine Profilmutation verletzt Catalog- oder Referenzvertraege."""

    def __init__(self, result: ValidationResult) -> None:
        self.result = result
        codes = ", ".join(issue.code for issue in result.errors)
        super().__init__(f"profile mutation is invalid: {codes}")


class ManagedEntryConflictError(CatalogServiceError):
    """Eine Remedy-/Multiplex-Mutation kollidiert mit dem Draftzustand."""


class ManagedEntryNotFoundError(CatalogServiceError):
    """Das angeforderte Remedy oder Multiplex ist im Draft nicht vorhanden."""


class ManagedEntryTypeError(CatalogServiceError):
    """Catalog-ID oder Payload besitzt nicht den erwarteten F4.3-Typ."""


class ManagedEntryStateError(CatalogServiceError):
    """Der persistierte Remedy-/Multiplex-Lifecycle erlaubt die Mutation nicht."""


class ManagedEntryValidationError(CatalogServiceError):
    """Eine F4.3-Mutation verletzt Catalog- oder Referenzvertraege."""

    def __init__(self, result: ValidationResult) -> None:
        self.result = result
        codes = ", ".join(issue.code for issue in result.errors)
        super().__init__(f"managed entry mutation is invalid: {codes}")


class ReferencedRemedyError(ManagedEntryConflictError):
    """Ein Remedy ist noch durch explizit ausgewiesene Referenzen gebunden."""

    def __init__(self, references: Sequence[str]) -> None:
        self.references = tuple(sorted(references))
        super().__init__("remedy is still referenced: " + ", ".join(self.references))


@dataclass(frozen=True)
class DraftState:
    draft_id: str
    version: int
    payload_hash: str
    entry_ids: tuple[str, ...]


@dataclass(frozen=True)
class CatalogDiff:
    added: tuple[str, ...]
    removed: tuple[str, ...]
    changed: tuple[str, ...]


@dataclass(frozen=True)
class PublishedRevision:
    revision_id: str
    payload_hash: str
    draft_id: str
    draft_version: int


def _entry_key(entry: CatalogEntry) -> tuple[str, str]:
    return entry.entry_type.value, normalize_catalog_id(entry.entry_id)


def _entry_label(entry: CatalogEntry) -> str:
    return f"{entry.entry_type.value}:{entry.entry_id}"


def _profile_entry(entry: CatalogEntry) -> CatalogEntry:
    if not isinstance(entry, CatalogEntry) or entry.entry_type is not EntryType.PROFILE:
        raise ProfileTypeError(
            "profile must be a CatalogEntry with entry_type profile"
        )
    return entry


def _with_profile_lifecycle(
    entry: CatalogEntry, *, enabled: bool, tombstoned: bool | None = None
) -> CatalogEntry:
    mapping = entry.canonical_mapping()
    data = dict(mapping["data"])
    data["enabled"] = enabled
    if tombstoned is not None:
        data["tombstoned"] = tombstoned
    return CatalogEntry(
        entry_type=entry.entry_type,
        entry_id=entry.entry_id,
        context=entry.context,
        source_id=entry.source_id,
        provenance=entry.provenance,
        data=data,
    )


def _require_profile_version(expected_version: int) -> None:
    if (
        isinstance(expected_version, bool)
        or not isinstance(expected_version, int)
        or expected_version < 1
    ):
        raise DraftConflictError(
            "expected profile draft version must be a positive integer"
        )


def _require_profile_context(
    context: CatalogContext, profile: CatalogEntry
) -> None:
    if profile.context != context:
        raise ProfileValidationError(
            ValidationResult(
                errors=(
                    ValidationIssue(
                        code="cross_context_profile",
                        entry_id=profile.entry_id,
                        field="context",
                        target_id=None,
                        message=(
                            "profile belongs to a different "
                            "operator/workspace/tenant/scope"
                        ),
                    ),
                ),
                warnings=(),
            )
        )


def _require_entries_context(
    context: CatalogContext, entries: Sequence[CatalogEntry]
) -> None:
    for entry in entries:
        if entry.context == context:
            continue
        if entry.entry_type is EntryType.PROFILE:
            _require_profile_context(context, entry)
        raise CatalogServiceError(
            f"catalog entry {entry.entry_id!r} belongs to a different catalog context"
        )


def _draft_state_from_write(
    draft_id: str,
    entries: Sequence[CatalogEntry],
    *,
    version: int,
    payload_hash: str,
) -> DraftState:
    ordered = sorted(
        entries,
        key=lambda entry: (
            entry.entry_type.value,
            normalize_catalog_id(entry.entry_id),
            entry.canonical_json(),
        ),
    )
    return DraftState(
        draft_id=draft_id,
        version=version,
        payload_hash=payload_hash,
        entry_ids=tuple(entry.entry_id for entry in ordered),
    )


class AdminCatalogService:
    """Kontextgebundene Offline-Fassade auf einem explizit injizierten Store."""

    def __init__(self, store: CatalogStore) -> None:
        if not isinstance(store, CatalogStore):
            raise TypeError("store must be CatalogStore")
        self.store = store

    def _state(self, context: CatalogContext, draft_id: str) -> DraftState:
        value = self.store.get_draft(context, draft_id)
        if value is None:
            raise DraftNotFoundError("draft does not exist in the requested context")
        return DraftState(
            draft_id=str(value["draft_id"]),
            version=int(value["version"]),
            payload_hash=str(value["payload_hash"]),
            entry_ids=tuple(str(item) for item in value["entry_ids"]),
        )

    def get_draft(self, context: CatalogContext, draft_id: str) -> DraftState:
        return self._state(context, draft_id)

    def create_draft(
        self,
        context: CatalogContext,
        draft_id: str,
        entries: Sequence[CatalogEntry],
    ) -> DraftState:
        candidate_entries = tuple(entries)
        _require_entries_context(context, candidate_entries)
        try:
            payload_hash = self.store.create_draft(context, draft_id, candidate_entries)
        except ManagedEntryTombstoneError as exc:
            raise ManagedEntryStateError(str(exc)) from exc
        except TombstoneMutationError as exc:
            raise ProfileStateError(str(exc)) from exc
        except sqlite3.IntegrityError as exc:
            raise DraftConflictError("draft already exists") from exc
        return _draft_state_from_write(
            draft_id, candidate_entries, version=1, payload_hash=payload_hash
        )

    def update_draft(
        self,
        context: CatalogContext,
        draft_id: str,
        entries: Sequence[CatalogEntry],
        *,
        expected_version: int,
    ) -> DraftState:
        return self._update_draft(
            context,
            draft_id,
            entries,
            expected_version=expected_version,
            tombstone_profile_id=None,
        )

    def _update_draft(
        self,
        context: CatalogContext,
        draft_id: str,
        entries: Sequence[CatalogEntry],
        *,
        expected_version: int,
        tombstone_profile_id: str | None,
    ) -> DraftState:
        candidate_entries = tuple(entries)
        _require_entries_context(context, candidate_entries)
        current_entries = self.store.get_draft_entries(context, draft_id)
        if current_entries is None:
            raise DraftNotFoundError("draft does not exist in the requested context")
        candidate_profile_ids = {
            normalize_catalog_id(entry.entry_id)
            for entry in candidate_entries
            if entry.entry_type is EntryType.PROFILE
        }
        removed_profile_ids = {
            normalize_catalog_id(entry.entry_id)
            for entry in current_entries
            if entry.entry_type is EntryType.PROFILE
            and normalize_catalog_id(entry.entry_id) not in candidate_profile_ids
        }
        if removed_profile_ids:
            raise ProfileConflictError(
                "profiles must be retained as disabled tombstones"
            )
        candidate_profiles = {
            normalize_catalog_id(entry.entry_id): entry
            for entry in candidate_entries
            if entry.entry_type is EntryType.PROFILE
        }
        current_profiles = {
            normalize_catalog_id(entry.entry_id): entry
            for entry in current_entries
            if entry.entry_type is EntryType.PROFILE
        }
        if tombstone_profile_id is None:
            for profile_id, candidate in candidate_profiles.items():
                current = current_profiles.get(profile_id)
                if (
                    candidate.data.get("tombstoned", False) is True
                    and (
                        current is None
                        or current.data.get("tombstoned", False) is not True
                    )
                ):
                    raise ProfileStateError(
                        "use delete_profile to create a tombstone"
                    )
        for current in current_entries:
            if (
                current.entry_type is EntryType.PROFILE
                and current.data.get("tombstoned", False) is True
                and candidate_profiles[normalize_catalog_id(current.entry_id)].payload_hash
                != current.payload_hash
            ):
                raise ProfileStateError("tombstoned profile is immutable")
        if any(
            entry.entry_type
            in {EntryType.PROFILE, EntryType.REMEDY, EntryType.MULTIPLEX}
            for entry in (*current_entries, *candidate_entries)
        ):
            validation = validate_entries(candidate_entries)
            if not validation.is_valid:
                if any(
                    entry.entry_type is EntryType.PROFILE
                    for entry in (*current_entries, *candidate_entries)
                ):
                    raise ProfileValidationError(validation)
                raise ManagedEntryValidationError(validation)
        try:
            if tombstone_profile_id is None:
                new_version, payload_hash = self.store.update_draft(
                    context,
                    draft_id,
                    candidate_entries,
                    expected_version=expected_version,
                )
            else:
                new_version, payload_hash = self.store._tombstone_profile(
                    context,
                    draft_id,
                    profile_id=tombstone_profile_id,
                    expected_version=expected_version,
                )
        except StoreAccessError as exc:
            raise DraftNotFoundError(str(exc)) from exc
        except ConcurrencyError as exc:
            raise DraftConflictError(str(exc)) from exc
        except ManagedEntryRemovalError as exc:
            raise ManagedEntryConflictError(str(exc)) from exc
        except ManagedEntryReferenceError as exc:
            raise ReferencedRemedyError(exc.references) from exc
        except ManagedEntryTombstoneError as exc:
            raise ManagedEntryStateError(str(exc)) from exc
        except ProfileRemovalError as exc:
            raise ProfileConflictError(str(exc)) from exc
        except TombstoneMutationError as exc:
            raise ProfileStateError(str(exc)) from exc
        except CatalogStoreError as exc:
            raise DraftConflictError(str(exc)) from exc
        return _draft_state_from_write(
            draft_id,
            candidate_entries,
            version=new_version,
            payload_hash=payload_hash,
        )

    def _profile_target(
        self, context: CatalogContext, draft_id: str, profile_id: str
    ) -> tuple[tuple[CatalogEntry, ...], int, CatalogEntry]:
        entries = self.store.get_draft_entries(context, draft_id)
        if entries is None:
            raise DraftNotFoundError("draft does not exist in the requested context")
        target_key = normalize_catalog_id(profile_id)
        matches = [
            (index, entry)
            for index, entry in enumerate(entries)
            if normalize_catalog_id(entry.entry_id) == target_key
        ]
        if not matches:
            raise ProfileNotFoundError(
                f"profile {profile_id!r} does not exist in the draft"
            )
        if len(matches) != 1 or matches[0][1].entry_type is not EntryType.PROFILE:
            raise ProfileTypeError(
                f"catalog entry {profile_id!r} is not a profile"
            )
        index, profile = matches[0]
        return entries, index, profile

    def get_profile(
        self, context: CatalogContext, draft_id: str, profile_id: str
    ) -> CatalogEntry:
        return self._profile_target(context, draft_id, profile_id)[2]

    @staticmethod
    def _validated_profile_snapshot(
        entries: Sequence[CatalogEntry],
    ) -> tuple[CatalogEntry, ...]:
        candidate = tuple(entries)
        validation = validate_entries(candidate)
        if not validation.is_valid:
            raise ProfileValidationError(validation)
        return candidate

    def create_profile(
        self,
        context: CatalogContext,
        draft_id: str,
        profile: CatalogEntry,
        *,
        expected_version: int,
    ) -> DraftState:
        _require_profile_version(expected_version)
        profile = _profile_entry(profile)
        _require_profile_context(context, profile)
        if profile.data.get("tombstoned", False) is True:
            raise ProfileStateError("new profile cannot start as a tombstone")
        entries = self.store.get_draft_entries(context, draft_id)
        if entries is None:
            raise DraftNotFoundError("draft does not exist in the requested context")
        target_key = normalize_catalog_id(profile.entry_id)
        existing = next(
            (
                entry
                for entry in entries
                if normalize_catalog_id(entry.entry_id) == target_key
            ),
            None,
        )
        if existing is not None and existing.entry_type is not EntryType.PROFILE:
            raise ProfileTypeError(
                f"catalog entry {profile.entry_id!r} is not a profile"
            )
        if existing is not None:
            raise ProfileConflictError(
                f"catalog entry {profile.entry_id!r} already exists"
            )
        candidate = self._validated_profile_snapshot((*entries, profile))
        return self.update_draft(
            context, draft_id, candidate, expected_version=expected_version
        )

    def update_profile(
        self,
        context: CatalogContext,
        draft_id: str,
        profile_id: str,
        replacement: CatalogEntry,
        *,
        expected_version: int,
    ) -> DraftState:
        _require_profile_version(expected_version)
        replacement = _profile_entry(replacement)
        _require_profile_context(context, replacement)
        entries, index, current = self._profile_target(context, draft_id, profile_id)
        if current.data.get("tombstoned", False) is True:
            raise ProfileStateError("tombstoned profile cannot be updated")
        if replacement.data.get("tombstoned", False) is True:
            raise ProfileStateError("use delete_profile to create a tombstone")
        if normalize_catalog_id(replacement.entry_id) != normalize_catalog_id(profile_id):
            raise ProfileConflictError("profile update cannot change profile identity")
        candidate = list(entries)
        candidate[index] = replacement
        validated = self._validated_profile_snapshot(candidate)
        return self.update_draft(
            context, draft_id, validated, expected_version=expected_version
        )

    def _set_profile_enabled(
        self,
        context: CatalogContext,
        draft_id: str,
        profile_id: str,
        *,
        enabled: bool,
        expected_version: int,
    ) -> DraftState:
        _require_profile_version(expected_version)
        profile = self.get_profile(context, draft_id, profile_id)
        if profile.data.get("tombstoned", False) is True:
            raise ProfileStateError("tombstoned profile cannot be enabled or disabled")
        return self.update_profile(
            context,
            draft_id,
            profile_id,
            _with_profile_lifecycle(profile, enabled=enabled),
            expected_version=expected_version,
        )

    def enable_profile(
        self,
        context: CatalogContext,
        draft_id: str,
        profile_id: str,
        *,
        expected_version: int,
    ) -> DraftState:
        return self._set_profile_enabled(
            context, draft_id, profile_id, enabled=True, expected_version=expected_version
        )

    def disable_profile(
        self,
        context: CatalogContext,
        draft_id: str,
        profile_id: str,
        *,
        expected_version: int,
    ) -> DraftState:
        return self._set_profile_enabled(
            context, draft_id, profile_id, enabled=False, expected_version=expected_version
        )

    def delete_profile(
        self,
        context: CatalogContext,
        draft_id: str,
        profile_id: str,
        *,
        expected_version: int,
    ) -> DraftState:
        _require_profile_version(expected_version)
        entries, index, profile = self._profile_target(context, draft_id, profile_id)
        if profile.data.get("tombstoned", False) is True:
            raise ProfileStateError("profile is already tombstoned")
        candidate = list(entries)
        candidate[index] = _with_profile_lifecycle(
            profile, enabled=False, tombstoned=True
        )
        validated = self._validated_profile_snapshot(candidate)
        return self._update_draft(
            context,
            draft_id,
            validated,
            expected_version=expected_version,
            tombstone_profile_id=normalize_catalog_id(profile_id),
        )

    def tombstone_profile(
        self,
        context: CatalogContext,
        draft_id: str,
        profile_id: str,
        *,
        expected_version: int,
    ) -> DraftState:
        return self.delete_profile(
            context, draft_id, profile_id, expected_version=expected_version
        )

    def profile_publication_state(
        self, context: CatalogContext, profile_id: str
    ) -> EntryPublicationState:
        state = self.store.entry_publication_state(context, profile_id)
        if state.published and state.entry_type is not EntryType.PROFILE:
            raise ProfileTypeError(
                f"published catalog entry {profile_id!r} is not a profile"
            )
        return state

    @staticmethod
    def _require_managed_version(expected_version: int) -> None:
        if (
            isinstance(expected_version, bool)
            or not isinstance(expected_version, int)
            or expected_version < 1
        ):
            raise DraftConflictError(
                "expected managed-entry draft version must be a positive integer"
            )

    @staticmethod
    def _require_managed_entry(
        entry: CatalogEntry, expected_type: EntryType
    ) -> CatalogEntry:
        if not isinstance(entry, CatalogEntry) or entry.entry_type is not expected_type:
            raise ManagedEntryTypeError(
                f"entry must be a CatalogEntry with entry_type {expected_type.value}"
            )
        return entry

    @staticmethod
    def _require_managed_context(
        context: CatalogContext, entry: CatalogEntry
    ) -> None:
        if entry.context == context:
            return
        raise ManagedEntryValidationError(
            ValidationResult(
                errors=(
                    ValidationIssue(
                        code="cross_context_managed_entry",
                        entry_id=entry.entry_id,
                        field="context",
                        target_id=None,
                        message="managed entry belongs to a different catalog context",
                    ),
                ),
                warnings=(),
            )
        )

    @staticmethod
    def _validated_managed_snapshot(
        entries: Sequence[CatalogEntry],
    ) -> tuple[CatalogEntry, ...]:
        candidate = tuple(entries)
        validation = validate_entries(candidate)
        if not validation.is_valid:
            raise ManagedEntryValidationError(validation)
        return candidate

    def _managed_target(
        self,
        context: CatalogContext,
        draft_id: str,
        entry_id: str,
        expected_type: EntryType,
    ) -> tuple[tuple[CatalogEntry, ...], int, CatalogEntry]:
        entries = self.store.get_draft_entries(context, draft_id)
        if entries is None:
            raise DraftNotFoundError("draft does not exist in the requested context")
        target_key = normalize_catalog_id(entry_id)
        matches = [
            (index, entry)
            for index, entry in enumerate(entries)
            if normalize_catalog_id(entry.entry_id) == target_key
        ]
        if not matches:
            raise ManagedEntryNotFoundError(
                f"{expected_type.value} {entry_id!r} does not exist in the draft"
            )
        if len(matches) != 1 or matches[0][1].entry_type is not expected_type:
            raise ManagedEntryTypeError(
                f"catalog entry {entry_id!r} is not a {expected_type.value}"
            )
        index, target = matches[0]
        return entries, index, target

    def _create_managed_entry(
        self,
        context: CatalogContext,
        draft_id: str,
        entry: CatalogEntry,
        expected_type: EntryType,
        *,
        expected_version: int,
    ) -> DraftState:
        self._require_managed_version(expected_version)
        entry = self._require_managed_entry(entry, expected_type)
        self._require_managed_context(context, entry)
        if entry.data.get("tombstoned", False) is True:
            raise ManagedEntryStateError(
                f"new {expected_type.value} cannot start as a tombstone"
            )
        entries = self.store.get_draft_entries(context, draft_id)
        if entries is None:
            raise DraftNotFoundError("draft does not exist in the requested context")
        target_key = normalize_catalog_id(entry.entry_id)
        existing = next(
            (
                candidate
                for candidate in entries
                if normalize_catalog_id(candidate.entry_id) == target_key
            ),
            None,
        )
        if existing is not None and existing.entry_type is not expected_type:
            raise ManagedEntryTypeError(
                f"catalog entry {entry.entry_id!r} is not a {expected_type.value}"
            )
        if existing is not None:
            raise ManagedEntryConflictError(
                f"catalog entry {entry.entry_id!r} already exists"
            )
        candidate = self._validated_managed_snapshot((*entries, entry))
        return self.update_draft(
            context, draft_id, candidate, expected_version=expected_version
        )

    def _update_managed_entry(
        self,
        context: CatalogContext,
        draft_id: str,
        entry_id: str,
        replacement: CatalogEntry,
        expected_type: EntryType,
        *,
        expected_version: int,
    ) -> DraftState:
        self._require_managed_version(expected_version)
        replacement = self._require_managed_entry(replacement, expected_type)
        self._require_managed_context(context, replacement)
        entries, index, current = self._managed_target(
            context, draft_id, entry_id, expected_type
        )
        if current.data.get("tombstoned", False) is True:
            raise ManagedEntryStateError(
                f"tombstoned {expected_type.value} cannot be updated"
            )
        if replacement.data.get("tombstoned", False) is True:
            raise ManagedEntryStateError(
                f"use delete_{expected_type.value} to create a tombstone"
            )
        if normalize_catalog_id(replacement.entry_id) != normalize_catalog_id(entry_id):
            raise ManagedEntryConflictError(
                f"{expected_type.value} update cannot change identity"
            )
        candidate = list(entries)
        candidate[index] = replacement
        validated = self._validated_managed_snapshot(candidate)
        return self.update_draft(
            context, draft_id, validated, expected_version=expected_version
        )

    def _set_managed_enabled(
        self,
        context: CatalogContext,
        draft_id: str,
        entry_id: str,
        expected_type: EntryType,
        *,
        enabled: bool,
        expected_version: int,
    ) -> DraftState:
        self._require_managed_version(expected_version)
        entry = self._managed_target(context, draft_id, entry_id, expected_type)[2]
        if entry.data.get("tombstoned", False) is True:
            raise ManagedEntryStateError(
                f"tombstoned {expected_type.value} cannot be enabled or disabled"
            )
        mapping = entry.canonical_mapping()
        data = dict(mapping["data"])
        data["enabled"] = enabled
        replacement = CatalogEntry(
            entry_type=entry.entry_type,
            entry_id=entry.entry_id,
            context=entry.context,
            source_id=entry.source_id,
            provenance=entry.provenance,
            data=data,
        )
        return self._update_managed_entry(
            context,
            draft_id,
            entry_id,
            replacement,
            expected_type,
            expected_version=expected_version,
        )

    def _delete_managed_entry(
        self,
        context: CatalogContext,
        draft_id: str,
        entry_id: str,
        expected_type: EntryType,
        *,
        expected_version: int,
    ) -> DraftState:
        self._require_managed_version(expected_version)
        entries, index, current = self._managed_target(
            context, draft_id, entry_id, expected_type
        )
        if current.data.get("tombstoned", False) is True:
            raise ManagedEntryStateError(
                f"{expected_type.value} is already tombstoned"
            )
        candidate = list(entries)
        candidate[index] = _with_profile_lifecycle(
            current, enabled=False, tombstoned=True
        )
        try:
            new_version, payload_hash = self.store._tombstone_managed_entry(
                context,
                draft_id,
                entry_type=expected_type,
                entry_id=entry_id,
                expected_version=expected_version,
            )
        except StoreAccessError as exc:
            raise DraftNotFoundError(str(exc)) from exc
        except ConcurrencyError as exc:
            raise DraftConflictError(str(exc)) from exc
        except ManagedEntryReferenceError as exc:
            raise ReferencedRemedyError(exc.references) from exc
        except ManagedEntryTombstoneError as exc:
            raise ManagedEntryStateError(str(exc)) from exc
        except CatalogStoreError as exc:
            raise ManagedEntryConflictError(str(exc)) from exc
        return _draft_state_from_write(
            draft_id,
            candidate,
            version=new_version,
            payload_hash=payload_hash,
        )

    def create_remedy(
        self, context: CatalogContext, draft_id: str, remedy: CatalogEntry, *, expected_version: int
    ) -> DraftState:
        return self._create_managed_entry(
            context, draft_id, remedy, EntryType.REMEDY, expected_version=expected_version
        )

    def get_remedy(
        self, context: CatalogContext, draft_id: str, remedy_id: str
    ) -> CatalogEntry:
        return self._managed_target(context, draft_id, remedy_id, EntryType.REMEDY)[2]

    def update_remedy(
        self,
        context: CatalogContext,
        draft_id: str,
        remedy_id: str,
        replacement: CatalogEntry,
        *,
        expected_version: int,
    ) -> DraftState:
        return self._update_managed_entry(
            context,
            draft_id,
            remedy_id,
            replacement,
            EntryType.REMEDY,
            expected_version=expected_version,
        )

    def enable_remedy(
        self, context: CatalogContext, draft_id: str, remedy_id: str, *, expected_version: int
    ) -> DraftState:
        return self._set_managed_enabled(
            context,
            draft_id,
            remedy_id,
            EntryType.REMEDY,
            enabled=True,
            expected_version=expected_version,
        )

    def disable_remedy(
        self, context: CatalogContext, draft_id: str, remedy_id: str, *, expected_version: int
    ) -> DraftState:
        return self._set_managed_enabled(
            context,
            draft_id,
            remedy_id,
            EntryType.REMEDY,
            enabled=False,
            expected_version=expected_version,
        )

    def delete_remedy(
        self, context: CatalogContext, draft_id: str, remedy_id: str, *, expected_version: int
    ) -> DraftState:
        return self._delete_managed_entry(
            context,
            draft_id,
            remedy_id,
            EntryType.REMEDY,
            expected_version=expected_version,
        )

    def tombstone_remedy(
        self, context: CatalogContext, draft_id: str, remedy_id: str, *, expected_version: int
    ) -> DraftState:
        return self.delete_remedy(
            context, draft_id, remedy_id, expected_version=expected_version
        )

    def create_multiplex(
        self,
        context: CatalogContext,
        draft_id: str,
        multiplex: CatalogEntry,
        *,
        expected_version: int,
    ) -> DraftState:
        return self._create_managed_entry(
            context,
            draft_id,
            multiplex,
            EntryType.MULTIPLEX,
            expected_version=expected_version,
        )

    def get_multiplex(
        self, context: CatalogContext, draft_id: str, multiplex_id: str
    ) -> CatalogEntry:
        return self._managed_target(
            context, draft_id, multiplex_id, EntryType.MULTIPLEX
        )[2]

    def update_multiplex(
        self,
        context: CatalogContext,
        draft_id: str,
        multiplex_id: str,
        replacement: CatalogEntry,
        *,
        expected_version: int,
    ) -> DraftState:
        return self._update_managed_entry(
            context,
            draft_id,
            multiplex_id,
            replacement,
            EntryType.MULTIPLEX,
            expected_version=expected_version,
        )

    def enable_multiplex(
        self,
        context: CatalogContext,
        draft_id: str,
        multiplex_id: str,
        *,
        expected_version: int,
    ) -> DraftState:
        return self._set_managed_enabled(
            context,
            draft_id,
            multiplex_id,
            EntryType.MULTIPLEX,
            enabled=True,
            expected_version=expected_version,
        )

    def disable_multiplex(
        self,
        context: CatalogContext,
        draft_id: str,
        multiplex_id: str,
        *,
        expected_version: int,
    ) -> DraftState:
        return self._set_managed_enabled(
            context,
            draft_id,
            multiplex_id,
            EntryType.MULTIPLEX,
            enabled=False,
            expected_version=expected_version,
        )

    def delete_multiplex(
        self,
        context: CatalogContext,
        draft_id: str,
        multiplex_id: str,
        *,
        expected_version: int,
    ) -> DraftState:
        return self._delete_managed_entry(
            context,
            draft_id,
            multiplex_id,
            EntryType.MULTIPLEX,
            expected_version=expected_version,
        )

    def tombstone_multiplex(
        self,
        context: CatalogContext,
        draft_id: str,
        multiplex_id: str,
        *,
        expected_version: int,
    ) -> DraftState:
        return self.delete_multiplex(
            context, draft_id, multiplex_id, expected_version=expected_version
        )

    def delete_draft(
        self,
        context: CatalogContext,
        draft_id: str,
        *,
        expected_version: int,
    ) -> None:
        try:
            self.store.delete_draft(
                context,
                draft_id,
                expected_version=expected_version,
            )
        except StoreAccessError as exc:
            raise DraftNotFoundError(str(exc)) from exc
        except ConcurrencyError as exc:
            raise DraftConflictError(str(exc)) from exc
        except CatalogStoreError as exc:
            raise DraftConflictError(str(exc)) from exc
        except sqlite3.IntegrityError as exc:
            if (
                getattr(exc, "sqlite_errorcode", None)
                != sqlite3.SQLITE_CONSTRAINT_FOREIGNKEY
            ):
                raise
            raise PublishedDraftError(
                "published draft cannot be deleted because revision provenance references it"
            ) from exc

    def validate_draft(
        self, context: CatalogContext, draft_id: str
    ) -> ValidationResult:
        state = self._state(context, draft_id)
        entries = self.store.get_draft_entries(context, draft_id)
        if entries is None:
            raise DraftNotFoundError("draft does not exist in the requested context")
        result = validate_entries(entries)
        if result.is_valid:
            try:
                self.store.mark_draft_validated(
                    context,
                    draft_id,
                    expected_version=state.version,
                    expected_payload_hash=state.payload_hash,
                )
            except ConcurrencyError as exc:
                raise DraftConflictError(str(exc)) from exc
        return result

    def publish_draft(
        self,
        context: CatalogContext,
        draft_id: str,
        revision_id: str,
        *,
        expected_draft_version: int,
    ) -> PublishedRevision:
        receipts = self.store.source_import_receipts(context, draft_id)
        if receipts:
            raise DraftValidationError(
                "source-imported draft requires dedicated source receipt revalidation"
            )
        try:
            payload_hash = self.store.publish_validated_draft(
                context,
                draft_id,
                revision_id,
                expected_draft_version=expected_draft_version,
            )
        except StoreAccessError as exc:
            raise DraftNotFoundError(str(exc)) from exc
        except ConcurrencyError as exc:
            raise DraftConflictError(str(exc)) from exc
        except ManagedEntryRemovalError as exc:
            raise ManagedEntryConflictError(str(exc)) from exc
        except ManagedEntryTombstoneError as exc:
            raise ManagedEntryStateError(str(exc)) from exc
        except ProfileRemovalError as exc:
            raise ProfileConflictError(str(exc)) from exc
        except TombstoneMutationError as exc:
            raise ProfileStateError(str(exc)) from exc
        except sqlite3.IntegrityError as exc:
            if getattr(exc, "sqlite_errorcode", None) not in {
                sqlite3.SQLITE_CONSTRAINT_PRIMARYKEY,
                sqlite3.SQLITE_CONSTRAINT_UNIQUE,
            }:
                raise
            raise RevisionConflictError(
                f"revision {revision_id!r} already exists in the requested context"
            ) from exc
        except CatalogStoreError as exc:
            raise DraftValidationError(str(exc)) from exc
        return PublishedRevision(
            revision_id=revision_id,
            payload_hash=payload_hash,
            draft_id=draft_id,
            draft_version=expected_draft_version,
        )

    def diff_draft(self, context: CatalogContext, draft_id: str) -> CatalogDiff:
        draft_entries = self.store.get_draft_entries(context, draft_id)
        if draft_entries is None:
            raise DraftNotFoundError("draft does not exist in the requested context")
        active_revision_id = self.store.current_revision_id(context)
        active_entries = (
            ()
            if active_revision_id is None
            else self.store.get_revision_entries(context, active_revision_id)
        )
        if active_entries is None:
            raise CatalogServiceError("active revision is unavailable in this context")
        draft_by_key = {_entry_key(entry): entry for entry in draft_entries}
        active_by_key = {_entry_key(entry): entry for entry in active_entries}
        added = tuple(
            _entry_label(draft_by_key[key])
            for key in sorted(draft_by_key.keys() - active_by_key.keys())
        )
        removed = tuple(
            _entry_label(active_by_key[key])
            for key in sorted(active_by_key.keys() - draft_by_key.keys())
        )
        changed = tuple(
            _entry_label(draft_by_key[key])
            for key in sorted(draft_by_key.keys() & active_by_key.keys())
            if draft_by_key[key].payload_hash != active_by_key[key].payload_hash
        )
        return CatalogDiff(added=added, removed=removed, changed=changed)

    def activate_revision(
        self,
        context: CatalogContext,
        revision_id: str,
        *,
        expected_previous_revision_id: str | None,
        expected_activation_version: int,
        actor_id: str,
        reason: str,
    ) -> int:
        return self.store.activate_revision(
            context,
            revision_id,
            expected_previous_revision_id=expected_previous_revision_id,
            expected_activation_version=expected_activation_version,
            actor_id=actor_id,
            reason=reason,
        )

    def deactivate(
        self,
        context: CatalogContext,
        *,
        expected_previous_revision_id: str,
        expected_activation_version: int,
        actor_id: str,
        reason: str,
    ) -> int:
        return self.store.deactivate_revision(
            context,
            expected_previous_revision_id=expected_previous_revision_id,
            expected_activation_version=expected_activation_version,
            actor_id=actor_id,
            reason=reason,
        )

    def rollback(
        self,
        context: CatalogContext,
        *,
        target_revision_id: str,
        expected_previous_revision_id: str,
        expected_activation_version: int,
        actor_id: str,
        reason: str,
    ) -> int:
        return self.store.rollback(
            context,
            target_revision_id=target_revision_id,
            expected_previous_revision_id=expected_previous_revision_id,
            expected_activation_version=expected_activation_version,
            actor_id=actor_id,
            reason=reason,
        )


__all__ = [
    "AdminCatalogService",
    "CatalogDiff",
    "CatalogServiceError",
    "DraftConflictError",
    "DraftNotFoundError",
    "DraftState",
    "DraftValidationError",
    "PublishedDraftError",
    "PublishedRevision",
    "ProfileConflictError",
    "ProfileNotFoundError",
    "ProfileStateError",
    "ProfileTypeError",
    "ProfileValidationError",
    "RevisionConflictError",
]
