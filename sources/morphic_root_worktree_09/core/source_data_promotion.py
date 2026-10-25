"""Offline immutable staging and consistency ledger for source data batches."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import stat
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, cast
from uuid import uuid4

from core.admin_catalog import (
    AdminCatalogService,
    CatalogContext,
    CatalogEntry,

    DraftState,
    PublishedRevision,
    SourceNormalizationResult,
    normalize_source_records,
)
from core.admin_catalog.store import CatalogStoreError, DraftSourceImportReceipt
from core.admin_catalog.validation import validate_entries
from core.source_registry import (
    SourceRegistry,
    SourceRegistryError,
    _atomic_publish_bytes,
    _atomic_publish_json,
    _atomic_replace_json,
    _canonical_registry_path,
    _directory_commit_guard,
    _directory_stat_identity,
    _read_registry_authority_bytes,
    _registry_lock,
)


ALLOWED_DATA_TYPES = {
    "group",
    "multiplex",
    "pathogen",
    "profile",
    "reference",
    "relation",
    "remedy",
    "terminology",
}
_BATCH_SCHEMA = "morphic_source_data_batch"
_BATCH_SCHEMA_VERSION = 1
_STAGE_INDEX_SCHEMA = "morphic_source_stage_index"
_STAGE_INDEX_SCHEMA_VERSION = 4
_STAGE_INDEX_FILENAME = ".morphic-stage-index.json"
_LEDGER_SCHEMA = "morphic_source_data_consistency_ledger"
_LEDGER_SCHEMA_VERSION = 3


class SourceDataPromotionError(ValueError):
    """Raised when a source data batch cannot be staged or promoted."""


@dataclass(frozen=True, slots=True)
class SourceDraftImportResult:
    draft: DraftState
    receipt: DraftSourceImportReceipt
    normalization: SourceNormalizationResult


@dataclass(frozen=True, slots=True)
class _PreparedSourceDraftImport:
    entries: tuple[CatalogEntry, ...]
    receipt: DraftSourceImportReceipt
    normalization: SourceNormalizationResult
    stage_parent_identity: tuple[int, int]
    registry_parent_identity: tuple[int, int]


def _required_registry_parent_identity(registry: SourceRegistry) -> tuple[int, int]:
    identity = registry._baseline_parent_identity
    if identity is None:
        raise SourceDataPromotionError("Source registry parent identity is not bound.")
    return identity


def stage_source_data_batch(
    batch_path: Path | str,
    staging_dir: Path | str,
    registry: SourceRegistry,
    *,
    quarantine_dir: Path | str | None = None,
) -> Path:
    path = Path(batch_path)
    batch = _validate_batch(_load_json(path))
    if registry.legacy_read_only:
        raise SourceDataPromotionError(
            "Legacy source registry shape is read-only; migrate it before data staging."
        )
    with _registry_lock(registry.path):
        current_registry = SourceRegistry.load(registry.path)
        if current_registry.legacy_read_only:
            raise SourceDataPromotionError(
                "Legacy source registry shape is read-only; migrate it before data staging."
            )
        return _stage_source_data_batch_locked(
            batch,
            staging_dir,
            current_registry,
            quarantine_dir=quarantine_dir,
        )


def _stage_source_data_batch_locked(
    batch: Mapping[str, Any],
    staging_dir: Path | str,
    registry: SourceRegistry,
    *,
    quarantine_dir: Path | str | None,
) -> Path:
    source_id = str(batch["source_id"])
    try:
        source = registry.get(source_id)
    except SourceRegistryError as exc:
        raise SourceDataPromotionError(f"Unknown source: {source_id}") from exc

    quarantined = (
        source.status == "quarantined"
        or source.extra.get("return_status_on_disable") == "quarantined"
    )
    if quarantined:
        if quarantine_dir is None:
            raise SourceDataPromotionError(
                "Quarantined sources require an explicit separate analysis quarantine root."
            )
        normal_root = Path(staging_dir).resolve()
        target_dir = Path(quarantine_dir).resolve()
        if (
            target_dir == normal_root
            or target_dir.is_relative_to(normal_root)
            or normal_root.is_relative_to(target_dir)
        ):
            raise SourceDataPromotionError(
                "Quarantine root must be separate and disjoint from normal staging."
            )
        analysis_only = True
    else:
        if not source.active:
            raise SourceDataPromotionError(
                f"Source '{source_id}' is disabled or not active and cannot be staged."
            )
        target_dir = Path(staging_dir)
        analysis_only = False

    if source.import_policy == "reference_only":
        raise SourceDataPromotionError(
            f"Source '{source_id}' has reference_only policy and cannot stage import data."
        )
    if batch["license"] != source.license:
        raise SourceDataPromotionError("Source data batch license does not match registry policy.")
    _require_source_scope(source.scopes, str(batch["data_type"]))

    source_manifest_sha256 = _canonical_sha256(source.to_mapping())
    source_registry_sha256 = _canonical_sha256(registry._to_payload())
    batch_identity_sha256 = _canonical_sha256(
        {
            "source_id": source_id,
            "source_version": batch["source_version"],
            "data_type": batch["data_type"],
            "license": batch["license"],
            "retrieval_metadata": batch["retrieval_metadata"],
            "records": batch["records"],
        }
    )
    rights = {"draft": False, "publish": False, "activate": False}
    artifact_id = uuid4().hex
    staged_at = _utc_now()
    contract = {
        "schema": _BATCH_SCHEMA,
        "schema_version": _BATCH_SCHEMA_VERSION,
        "artifact_id": artifact_id,
        "source_id": source_id,
        "source_version": batch["source_version"],
        "data_type": batch["data_type"],
        "license": batch["license"],
        "retrieval_metadata": batch["retrieval_metadata"],
        "batch_identity_sha256": batch_identity_sha256,
        "source_manifest_sha256": source_manifest_sha256,
        "source_registry_revision": registry.revision,
        "source_registry_sha256": source_registry_sha256,
        "analysis_only": analysis_only,
        "rights": rights,
        "records": batch["records"],
        "record_count": len(batch["records"]),
        "staged_at": staged_at,
    }
    batch_sha256 = _canonical_sha256(contract)
    staged = {
        **contract,
        "sha256": batch_sha256,
    }
    registry_parent_identity = _required_registry_parent_identity(registry)
    target_dir.mkdir(parents=True, exist_ok=True)
    target_parent_identity = _directory_stat_identity(os.lstat(target_dir))
    staged_path = (
        target_dir
        / f"{source_id}.{batch['data_type']}.{batch_identity_sha256}.batch.json"
    )
    try:
        _atomic_publish_json(
            staged_path,
            staged,
            expected_parent_identity=target_parent_identity,
        )
    except SourceRegistryError as exc:
        if "Immutable artifact already exists" not in str(exc):
            raise SourceDataPromotionError(
                "Source data stage authority publication failed."
            ) from exc
        existing = _load_stage_authority_json(staged_path)
        _validate_staged_batch(existing)
        expected_existing_fields = {
            "analysis_only": analysis_only,
            "batch_identity_sha256": batch_identity_sha256,
            "source_manifest_sha256": source_manifest_sha256,
            "source_registry_revision": registry.revision,
            "source_registry_sha256": source_registry_sha256,
        }
        if any(
            existing.get(name) != value
            for name, value in expected_existing_fields.items()
        ):
            raise SourceDataPromotionError(
                f"Duplicate or replay source data batch already exists: {batch_identity_sha256}"
            ) from exc
        try:
            _register_staged_artifact(
                target_dir,
                staged_path,
                existing,
                registry.path,
                expected_parent_identity=target_parent_identity,
                registry_parent_identity=registry_parent_identity,
            )
        except SourceDataPromotionError as registration_exc:
            raise SourceDataPromotionError(
                f"Duplicate or replay source data batch already exists: {batch_identity_sha256}"
            ) from registration_exc
        return staged_path
    _register_staged_artifact(
        target_dir,
        staged_path,
        staged,
        registry.path,
        expected_parent_identity=target_parent_identity,
        registry_parent_identity=registry_parent_identity,
    )
    return staged_path


@contextmanager
def _prepare_source_data_draft_import(
    staged_path: Path | str,
    *,
    staging_root: Path | str,
    registry: SourceRegistry,
    service: AdminCatalogService,
    context: CatalogContext,
    draft_id: str,
    actor_id: str,
    reason: str,
    catalog_authority_path: Path | str,
    base_entries: tuple[CatalogEntry, ...] = (),
    base_revision_id: str = "",
) -> SourceDraftImportResult:
    """Create one new Catalog draft plus immutable approval receipt."""

    if not isinstance(service, AdminCatalogService):
        raise SourceDataPromotionError("service must be AdminCatalogService")
    if not isinstance(context, CatalogContext):
        raise SourceDataPromotionError("context must be CatalogContext")
    _required_text(draft_id, "draft_id")
    _required_text(actor_id, "actor_id")
    _required_text(reason, "reason")
    if bool(base_entries) != bool(base_revision_id):
        raise SourceDataPromotionError(
            "base_entries and base_revision_id must be supplied together."
        )
    path = Path(staged_path)
    staged = _load_stage_authority_json(path)
    _validate_staged_batch(staged)
    _validate_registered_stage(
        path,
        staging_root,
        staged,
        registry.path,
        expected_registry_parent_identity=_required_registry_parent_identity(registry),
        catalog_authority_path=Path(catalog_authority_path),
        context=context,
        draft_id=draft_id,
    )
    if staged["analysis_only"]:
        raise SourceDataPromotionError(
            "analysis_only quarantined batches cannot create a Catalog draft."
        )
    if staged["data_type"] == "reference":
        raise SourceDataPromotionError(
            "generic reference batches have no closed Catalog normalization schema."
        )
    if registry.legacy_read_only:
        raise SourceDataPromotionError(
            "Legacy source registry shape is read-only; migrate it before draft import."
        )

    with _locked_stage_and_registry(
        path,
        staging_root,
        staged,
        registry,
        catalog_authority_path=Path(catalog_authority_path),
        context=context,
        draft_id=draft_id,
    ) as (
        current_registry,
        staged,
        stage_parent_identity,
        registry_parent_identity,
    ):
        _revalidate_staged_source(staged, current_registry)
        normalization = normalize_source_records(
            source_id=str(staged["source_id"]),
            data_type=str(staged["data_type"]),
            records=staged["records"],
            context=context,
            known_entries=base_entries,
        )
        if normalization.quarantined:
            record_ids = ", ".join(
                item.source_record_id for item in normalization.quarantined
            )
            raise SourceDataPromotionError(
                f"Source records require quarantine before draft import: {record_ids}"
            )
        entries = (*base_entries, *(item.entry for item in normalization.normalized))
        validation = validate_entries(entries)
        if not validation.is_valid:
            codes = ", ".join(sorted({issue.code for issue in validation.errors}))
            raise SourceDataPromotionError(
                f"Normalized Catalog draft snapshot is invalid: {codes}"
            )
        draft_payload_hash = service.store.preview_draft_payload_hash(context, entries)
        if base_entries:
            stored_base = service.store.get_revision_entries(context, base_revision_id)
            base_revision_payload_hash = service.store.revision_payload_hash(
                context, base_revision_id
            )
            if stored_base != base_entries or base_revision_payload_hash is None:
                raise SourceDataPromotionError(
                    "Explicit base revision identity or entries changed."
                )
        else:
            base_revision_payload_hash = "0" * 64
        # Stable per artifact so a retry can present the exact same approval receipt.
        imported_at = str(staged["staged_at"])
        unsigned_receipt = {
            "actor_id": actor_id,
            "artifact_id": staged["artifact_id"],
            "base_revision_id": base_revision_id,
            "base_revision_payload_hash": base_revision_payload_hash,
            "batch_identity_sha256": staged["batch_identity_sha256"],
            "draft_id": draft_id,
            "draft_payload_hash": draft_payload_hash,
            "draft_version": 1,
            "imported_at": imported_at,
            "normalization_sha256": normalization.sha256,
            "operator_id": context.operator_id,
            "reason": reason,
            "scope": context.scope,
            "source_id": staged["source_id"],
            "source_manifest_sha256": staged["source_manifest_sha256"],
            "source_registry_revision": staged["source_registry_revision"],
            "source_registry_path": str(_canonical_registry_path(registry.path)),
            "source_registry_sha256": staged["source_registry_sha256"],
            "staged_batch_sha256": staged["sha256"],
            "tenant_id": context.tenant_id,
            "workspace_id": context.workspace_id,
        }
        receipt = DraftSourceImportReceipt(
            draft_id=draft_id,
            draft_version=1,
            draft_payload_hash=draft_payload_hash,
            source_id=str(staged["source_id"]),
            artifact_id=str(staged["artifact_id"]),
            batch_identity_sha256=str(staged["batch_identity_sha256"]),
            staged_batch_sha256=str(staged["sha256"]),
            source_manifest_sha256=str(staged["source_manifest_sha256"]),
            source_registry_revision=int(staged["source_registry_revision"]),
            source_registry_path=str(_canonical_registry_path(registry.path)),
            source_registry_sha256=str(staged["source_registry_sha256"]),
            normalization_sha256=normalization.sha256,
            base_revision_id=base_revision_id,
            base_revision_payload_hash=base_revision_payload_hash,
            operator_id=context.operator_id,
            workspace_id=context.workspace_id,
            tenant_id=context.tenant_id,
            scope=context.scope,
            actor_id=actor_id,
            reason=reason,
            imported_at=imported_at,
            receipt_sha256=_canonical_sha256(unsigned_receipt),
        )
        yield _PreparedSourceDraftImport(
            entries=tuple(entries),
            receipt=receipt,
            normalization=normalization,
            stage_parent_identity=stage_parent_identity,
            registry_parent_identity=registry_parent_identity,
        )


def import_staged_source_data_to_draft(
    staged_path: Path | str,
    *,
    staging_root: Path | str,
    registry: SourceRegistry,
    service: AdminCatalogService,
    context: CatalogContext,
    draft_id: str,
    actor_id: str,
    reason: str,
    base_revision_id: str = "",
) -> SourceDraftImportResult:
    """Create a source draft only through the Store-owned authority boundary."""

    try:
        payload_hash, raw_prepared = service.store.import_staged_source_draft(
            staged_path,
            staging_root=staging_root,
            registry=registry,
            context=context,
            draft_id=draft_id,
            actor_id=actor_id,
            reason=reason,
            base_revision_id=base_revision_id,
        )
    except sqlite3.IntegrityError as exc:
        raise SourceDataPromotionError(
            "Catalog source draft import failed: source batch replay or draft conflict"
        ) from exc
    except CatalogStoreError as exc:
        raise SourceDataPromotionError(
            f"Catalog source draft import failed: {exc}"
        ) from exc
    prepared = cast(_PreparedSourceDraftImport, raw_prepared)
    draft = DraftState(
        draft_id=draft_id,
        version=1,
        payload_hash=payload_hash,
        entry_ids=tuple(sorted(entry.entry_id for entry in prepared.entries)),
    )
    return SourceDraftImportResult(
        draft=draft,
        receipt=prepared.receipt,
        normalization=prepared.normalization,
    )


def validate_staged_source_artifact(
    staged_path: Path | str,
    *,
    staging_root: Path | str,
    registry: SourceRegistry,
) -> None:
    """Validate Stage authority and live source policy without Catalog mutation."""

    path = Path(staged_path)
    staged = _load_stage_authority_json(path)
    _validate_staged_batch(staged)
    _validate_registered_stage(
        path,
        staging_root,
        staged,
        registry.path,
        expected_registry_parent_identity=_required_registry_parent_identity(registry),
    )
    if staged["analysis_only"]:
        raise SourceDataPromotionError(
            "analysis_only quarantined batches cannot create a Catalog draft."
        )
    with _registry_lock(registry.path):
        _revalidate_staged_source(staged, SourceRegistry.load(registry.path))


def preflight_staged_source_data_to_draft(
    staged_path: Path | str,
    *,
    staging_root: Path | str,
    registry: SourceRegistry,
    context: CatalogContext,
    base_entries: tuple[CatalogEntry, ...] = (),
) -> None:
    """Validate normalization and snapshot semantics without Catalog mutation."""

    path = Path(staged_path)
    staged = _load_stage_authority_json(path)
    _validate_staged_batch(staged)
    _validate_registered_stage(
        path,
        staging_root,
        staged,
        registry.path,
        expected_registry_parent_identity=_required_registry_parent_identity(registry),
    )
    if staged["analysis_only"] or staged["data_type"] == "reference":
        raise SourceDataPromotionError(
            "Staged batch has no importable closed Catalog schema."
        )
    with _registry_lock(registry.path):
        current_registry = SourceRegistry.load(registry.path)
        _revalidate_staged_source(staged, current_registry)
        normalization = normalize_source_records(
            source_id=str(staged["source_id"]),
            data_type=str(staged["data_type"]),
            records=staged["records"],
            context=context,
            known_entries=base_entries,
        )
        if normalization.quarantined:
            raise SourceDataPromotionError(
                "Source records require quarantine before draft import."
            )
        entries = (*base_entries, *(item.entry for item in normalization.normalized))
        validation = validate_entries(entries)
        if not validation.is_valid:
            codes = ", ".join(sorted({issue.code for issue in validation.errors}))
            raise SourceDataPromotionError(
                f"Normalized Catalog draft snapshot is invalid: {codes}"
            )


def revalidate_source_import_receipt(
    receipt: DraftSourceImportReceipt,
    *,
    registry: SourceRegistry,
) -> None:
    """Fail closed unless an immutable receipt still matches the live registry."""

    with _registry_lock(registry.path):
        _revalidate_source_import_receipt_against_registry(
            receipt, SourceRegistry.load(registry.path)
        )


def publish_source_imported_draft(
    *,
    registry: SourceRegistry,
    service: AdminCatalogService,
    context: CatalogContext,
    draft_id: str,
    revision_id: str,
    expected_draft_version: int,
) -> PublishedRevision:
    """Revalidate and publish while holding the registry lock across both steps."""

    try:
        payload_hash = service.store.publish_validated_draft(
            context,
            draft_id,
            revision_id,
            expected_draft_version=expected_draft_version,
            source_registry_path=registry.path,
        )
    except (CatalogStoreError, SourceRegistryError) as exc:
        raise SourceDataPromotionError(
            f"Catalog source draft publication failed: {exc}"
        ) from exc
    return PublishedRevision(
        revision_id=revision_id,
        payload_hash=payload_hash,
        draft_id=draft_id,
        draft_version=expected_draft_version,
    )


def _revalidate_source_import_receipt_against_registry(
    receipt: DraftSourceImportReceipt,
    registry: SourceRegistry,
) -> None:
    if not isinstance(receipt, DraftSourceImportReceipt) or not receipt.has_valid_hash():
        raise SourceDataPromotionError("Source approval receipt hash is invalid.")
    if registry.legacy_read_only:
        raise SourceDataPromotionError(
            "Legacy source registry shape cannot revalidate a source approval receipt."
        )
    try:
        source = registry.get(receipt.source_id)
    except SourceRegistryError as exc:
        raise SourceDataPromotionError(
            "Source approval receipt source no longer exists."
        ) from exc
    quarantined = (
        source.status == "quarantined"
        or source.extra.get("return_status_on_disable") == "quarantined"
    )
    if quarantined or not source.active:
        raise SourceDataPromotionError(
            "Source approval receipt source is disabled or quarantined."
        )
    if source.import_policy == "reference_only":
        raise SourceDataPromotionError(
            "Source approval receipt source is now reference_only."
        )
    if receipt.source_manifest_sha256 != _canonical_sha256(source.to_mapping()):
        raise SourceDataPromotionError(
            "Source approval receipt manifest no longer matches."
        )
    if receipt.source_registry_revision != registry.revision:
        raise SourceDataPromotionError(
            "Source approval receipt registry revision is stale."
        )
    if receipt.source_registry_sha256 != _canonical_sha256(registry._to_payload()):
        raise SourceDataPromotionError(
            "Source approval receipt registry hash no longer matches."
        )


def promote_staged_source_data(
    staged_path: Path | str,
    ledger_path: Path | str,
    *,
    registry: SourceRegistry,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Record a staged batch in the local consistency ledger.

    The legacy Python function name is retained for compatibility only. This
    operation does not publish, activate, or import data into the Catalog.
    """
    path = Path(staged_path)
    ledger_file = _canonical_consistency_ledger_path(Path(ledger_path))
    if ledger_file.resolve() == registry.path.resolve():
        raise SourceDataPromotionError("Consistency ledger and source registry must be different files.")
    staged = _load_stage_authority_json(path)
    _validate_staged_batch(staged)
    if staged["analysis_only"]:
        raise SourceDataPromotionError(
            "analysis_only quarantined batches have no consistency-recording, draft, publish, or activation rights."
        )
    if registry.legacy_read_only:
        raise SourceDataPromotionError(
            "Legacy source registry shape is read-only; migrate it before ledger planning."
        )
    registry_guard = nullcontext() if dry_run else _registry_lock(registry.path)
    with registry_guard:
        current_registry = SourceRegistry.load(registry.path)
        registry_baseline_sha256 = _canonical_sha256(current_registry._to_payload())
        _revalidate_staged_source(staged, current_registry)
        if current_registry.legacy_read_only:
            raise SourceDataPromotionError(
                "Legacy source registry shape is read-only; migrate it before ledger mutation."
            )
        entry = {
            "recorded_at": _utc_now(),
            "source_id": staged["source_id"],
            "source_version": staged["source_version"],
            "data_type": staged["data_type"],
            "record_count": staged["record_count"],
            "sha256": staged["sha256"],
            "batch_identity_sha256": staged["batch_identity_sha256"],
            "manifest_sha256": staged["source_manifest_sha256"],
            "registry_revision": staged["source_registry_revision"],
            "staged_path": str(path),
        }
        entry["entry_sha256"] = _canonical_sha256(entry)
        result = dict(entry)
        result["dry_run"] = dry_run
        if dry_run:
            if ledger_file.exists():
                entries = _validate_consistency_ledger(_load_json(ledger_file))
            else:
                entries = []
            _reject_replay(entries, staged["batch_identity_sha256"])
            final_registry = SourceRegistry.load(registry.path)
            if _canonical_sha256(final_registry._to_payload()) != registry_baseline_sha256:
                raise SourceDataPromotionError(
                    "Source registry changed during dry-run revalidation."
                )
            return result

        ledger_file.parent.mkdir(parents=True, exist_ok=True)
        ledger_parent_identity = _directory_stat_identity(
            os.lstat(ledger_file.parent)
        )
        with _registry_lock(ledger_file):
            _canonical_consistency_ledger_path(ledger_file)
            if ledger_file.exists():
                ledger = _load_json(ledger_file)
                entries = _validate_consistency_ledger(ledger)
            else:
                ledger = {
                    "schema": _LEDGER_SCHEMA,
                    "schema_version": _LEDGER_SCHEMA_VERSION,
                    "entries": [],
                }
                entries = ledger["entries"]

            _reject_replay(entries, staged["batch_identity_sha256"])
            entries.append(entry)
            _atomic_replace_json(
                ledger_file,
                ledger,
                authority_validator=_canonical_consistency_ledger_path,
                expected_parent_identity=ledger_parent_identity,
            )
        return result


def _canonical_consistency_ledger_path(path: Path) -> Path:
    try:
        return _canonical_registry_path(path)
    except SourceRegistryError as exc:
        raise SourceDataPromotionError(
            f"Consistency ledger authority path is invalid: {exc}"
        ) from exc


def _reject_replay(entries: list[Any], batch_identity_sha256: str) -> None:
    if any(
        isinstance(existing, Mapping)
        and existing.get("batch_identity_sha256") == batch_identity_sha256
        for existing in entries
    ):
        raise SourceDataPromotionError(
            "Duplicate or replay source data consistency record rejected: "
            f"{batch_identity_sha256}"
        )


def _validate_consistency_ledger(ledger: Mapping[str, Any]) -> list[Any]:
    if ledger.get("schema") != _LEDGER_SCHEMA:
        raise SourceDataPromotionError("Consistency ledger has an unsupported schema.")
    if set(ledger) != {"schema", "schema_version", "entries"}:
        raise SourceDataPromotionError("Consistency ledger fields are invalid.")
    ledger_schema_version = ledger.get("schema_version")
    if (
        not isinstance(ledger_schema_version, int)
        or isinstance(ledger_schema_version, bool)
        or ledger_schema_version != _LEDGER_SCHEMA_VERSION
    ):
        raise SourceDataPromotionError("Consistency ledger has an unsupported schema_version.")
    entries = ledger.get("entries")
    if not isinstance(entries, list):
        raise SourceDataPromotionError("Consistency ledger field 'entries' must be a list.")
    expected_fields = {
        "recorded_at",
        "source_id",
        "source_version",
        "data_type",
        "record_count",
        "sha256",
        "batch_identity_sha256",
        "manifest_sha256",
        "registry_revision",
        "staged_path",
        "entry_sha256",
    }
    identities: set[str] = set()
    for entry in entries:
        if not isinstance(entry, Mapping) or set(entry) != expected_fields:
            raise SourceDataPromotionError("Consistency ledger entry fields are invalid.")
        _validate_timestamp(entry["recorded_at"], "consistency.recorded_at")
        for field in ("source_id", "source_version", "data_type", "staged_path"):
            _required_text(entry[field], f"consistency.{field}")
        if entry["data_type"] not in ALLOWED_DATA_TYPES:
            raise SourceDataPromotionError("Consistency ledger data_type is invalid.")
        for field in ("sha256", "batch_identity_sha256", "manifest_sha256"):
            if not _is_sha256(entry[field]):
                raise SourceDataPromotionError(f"Consistency ledger {field} is invalid.")
        record_count = entry["record_count"]
        revision = entry["registry_revision"]
        if not isinstance(record_count, int) or isinstance(record_count, bool) or record_count < 1:
            raise SourceDataPromotionError("Consistency ledger record_count is invalid.")
        if not isinstance(revision, int) or isinstance(revision, bool) or revision < 0:
            raise SourceDataPromotionError("Consistency ledger registry_revision is invalid.")
        identity = str(entry["batch_identity_sha256"])
        if identity in identities:
            raise SourceDataPromotionError("Consistency ledger contains duplicate replay identities.")
        identities.add(identity)
        unsigned_entry = dict(entry)
        claimed_entry_hash = unsigned_entry.pop("entry_sha256")
        if claimed_entry_hash != _canonical_sha256(unsigned_entry):
            raise SourceDataPromotionError("Consistency ledger entry hash mismatch.")
    return entries


def _revalidate_staged_source(
    staged: Mapping[str, Any],
    registry: SourceRegistry,
) -> None:
    try:
        source = registry.get(str(staged["source_id"]))
    except SourceRegistryError as exc:
        raise SourceDataPromotionError("Staged batch source no longer exists.") from exc
    quarantined = (
        source.status == "quarantined"
        or source.extra.get("return_status_on_disable") == "quarantined"
    )
    if quarantined or not source.active:
        raise SourceDataPromotionError("Staged batch source is disabled or quarantined.")
    if source.import_policy == "reference_only":
        raise SourceDataPromotionError("Staged batch source policy is reference_only.")
    if staged["license"] != source.license:
        raise SourceDataPromotionError("Staged batch source license changed.")
    _require_source_scope(source.scopes, str(staged["data_type"]))
    if staged["source_registry_revision"] != registry.revision:
        raise SourceDataPromotionError("Staged batch registry revision is stale.")
    if staged["source_registry_sha256"] != _canonical_sha256(registry._to_payload()):
        raise SourceDataPromotionError("Staged batch registry baseline changed.")
    if staged["source_manifest_sha256"] != _canonical_sha256(source.to_mapping()):
        raise SourceDataPromotionError("Staged batch source manifest hash changed.")


def _require_source_scope(scopes: tuple[str, ...], data_type: str) -> None:
    if data_type not in scopes:
        raise SourceDataPromotionError(
            f"Source scope does not authorize data_type: {data_type}"
        )


def _validate_batch(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    required = (
        "schema_version",
        "source_id",
        "source_version",
        "data_type",
        "license",
        "retrieval_metadata",
        "records",
    )
    missing = [field for field in required if field not in payload]
    if missing:
        raise SourceDataPromotionError(
            f"Missing source data batch fields: {', '.join(missing)}"
        )
    if set(payload) != set(required):
        raise SourceDataPromotionError("Source data batch fields are invalid.")
    batch_schema_version = payload["schema_version"]
    if (
        not isinstance(batch_schema_version, int)
        or isinstance(batch_schema_version, bool)
        or batch_schema_version != _BATCH_SCHEMA_VERSION
    ):
        raise SourceDataPromotionError(
            f"Unsupported source data batch schema_version: {payload['schema_version']}"
        )
    source_id = _required_text(payload["source_id"], "source_id")
    _required_text(payload["source_version"], "source_version")
    data_type = _required_text(payload["data_type"], "data_type")
    if data_type not in ALLOWED_DATA_TYPES:
        raise SourceDataPromotionError(f"Unsupported source data_type: {data_type}")
    _required_text(payload["license"], "license")
    retrieval_metadata = payload["retrieval_metadata"]
    if not isinstance(retrieval_metadata, Mapping) or not retrieval_metadata:
        raise SourceDataPromotionError("retrieval_metadata must be a non-empty object.")
    records = payload["records"]
    if not isinstance(records, list) or not records:
        raise SourceDataPromotionError("records must be a non-empty list.")
    for index, record in enumerate(records, 1):
        if not isinstance(record, Mapping):
            raise SourceDataPromotionError(f"record {index} must be an object.")
        _required_text(record.get("id"), f"record {index} id")
        if data_type != "relation":
            _required_text(record.get("label"), f"record {index} label")
    try:
        _canonical_sha256(
            {
                "source_id": source_id,
                "source_version": payload["source_version"],
                "data_type": data_type,
                "license": payload["license"],
                "retrieval_metadata": retrieval_metadata,
                "records": records,
            }
        )
    except (TypeError, ValueError) as exc:
        raise SourceDataPromotionError("Source data batch must be canonical JSON data.") from exc
    return payload


def _validate_staged_batch(payload: Mapping[str, Any]) -> None:
    expected_fields = {
        "schema",
        "schema_version",
        "artifact_id",
        "source_id",
        "source_version",
        "data_type",
        "license",
        "retrieval_metadata",
        "batch_identity_sha256",
        "source_manifest_sha256",
        "source_registry_revision",
        "source_registry_sha256",
        "analysis_only",
        "rights",
        "records",
        "record_count",
        "staged_at",
        "sha256",
    }
    if set(payload) != expected_fields:
        raise SourceDataPromotionError("Staged batch fields are invalid.")
    if payload.get("schema") != _BATCH_SCHEMA:
        raise SourceDataPromotionError("Staged batch has an unsupported schema.")
    _required_text(payload.get("artifact_id"), "artifact_id")
    raw_batch_fields = {
        field: payload[field]
        for field in (
            "schema_version",
            "source_id",
            "source_version",
            "data_type",
            "license",
            "retrieval_metadata",
            "records",
        )
    }
    _validate_batch(raw_batch_fields)
    records = payload["records"]
    record_count = payload.get("record_count")
    if (
        not isinstance(record_count, int)
        or isinstance(record_count, bool)
        or record_count != len(records)
    ):
        raise SourceDataPromotionError("Staged batch record_count mismatch.")
    _validate_timestamp(payload.get("staged_at"), "staged_at")
    identity_contract = {
        "source_id": payload["source_id"],
        "source_version": payload["source_version"],
        "data_type": payload["data_type"],
        "license": payload["license"],
        "retrieval_metadata": payload["retrieval_metadata"],
        "records": records,
    }
    if payload.get("batch_identity_sha256") != _canonical_sha256(identity_contract):
        raise SourceDataPromotionError("Staged batch identity hash mismatch.")
    if not _is_sha256(payload.get("source_manifest_sha256")):
        raise SourceDataPromotionError("Staged batch source manifest hash is invalid.")
    revision = payload.get("source_registry_revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 0:
        raise SourceDataPromotionError("Staged batch source registry revision is invalid.")
    if not _is_sha256(payload.get("source_registry_sha256")):
        raise SourceDataPromotionError("Staged batch source registry hash is invalid.")
    if not isinstance(payload.get("analysis_only"), bool):
        raise SourceDataPromotionError("Staged batch analysis_only flag is invalid.")
    if payload.get("rights") != {"draft": False, "publish": False, "activate": False}:
        raise SourceDataPromotionError("Staged batch rights are invalid.")
    contract = {
        field: payload[field]
        for field in (
            "schema",
            "schema_version",
            "artifact_id",
            "source_id",
            "source_version",
            "data_type",
            "license",
            "retrieval_metadata",
            "batch_identity_sha256",
            "source_manifest_sha256",
            "source_registry_revision",
            "source_registry_sha256",
            "analysis_only",
            "rights",
            "records",
            "record_count",
            "staged_at",
        )
    }
    if payload.get("sha256") != _canonical_sha256(contract):
        raise SourceDataPromotionError("Staged batch hash mismatch.")


def _canonical_stage_root(path: Path) -> Path:
    absolute = Path(os.path.abspath(path.expanduser()))
    for component in [*reversed(absolute.parents), absolute]:
        try:
            attributes = os.lstat(component)
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise SourceDataPromotionError(
                f"Stage authority path cannot be inspected safely: {absolute}"
            ) from exc
        if component.is_symlink() or bool(
            getattr(attributes, "st_file_attributes", 0) & 0x400
        ):
            raise SourceDataPromotionError(
                f"Stage authority path must not contain symlinks or reparse points: {absolute}"
            )
    try:
        resolved = absolute.resolve(strict=absolute.exists())
    except OSError as exc:
        raise SourceDataPromotionError(
            f"Stage authority path cannot be resolved safely: {absolute}"
        ) from exc
    if resolved.exists() and not resolved.is_dir():
        raise SourceDataPromotionError("Stage authority root is not a directory.")
    return resolved


def _canonical_stage_file(path: Path) -> Path:
    absolute = Path(os.path.abspath(path.expanduser()))
    _canonical_stage_root(absolute.parent)
    try:
        attributes = os.lstat(absolute)
    except OSError as exc:
        raise SourceDataPromotionError(
            f"Stage authority file cannot be inspected safely: {absolute}"
        ) from exc
    if absolute.is_symlink() or bool(
        getattr(attributes, "st_file_attributes", 0) & 0x400
    ):
        raise SourceDataPromotionError(
            f"Stage authority file must not be a symlink or reparse point: {absolute}"
        )
    if not absolute.is_file() or attributes.st_nlink != 1:
        raise SourceDataPromotionError(
            f"Stage authority file must be a regular single-link file: {absolute}"
        )
    resolved = absolute.resolve(strict=True)
    if os.path.normcase(str(resolved)) != os.path.normcase(str(absolute)):
        raise SourceDataPromotionError(
            f"Stage authority file resolved away from its expected path: {absolute}"
        )
    final = os.lstat(absolute)
    if (
        (attributes.st_dev, attributes.st_ino, attributes.st_size)
        != (final.st_dev, final.st_ino, final.st_size)
        or final.st_nlink != 1
    ):
        raise SourceDataPromotionError(
            f"Stage authority file identity changed during path validation: {absolute}"
        )
    return absolute


def _load_stage_authority_json(path: Path) -> Mapping[str, Any]:
    requested = Path(os.path.abspath(path.expanduser()))
    expected = os.lstat(requested)
    canonical = _canonical_stage_file(requested)
    try:
        descriptor = os.open(
            canonical,
            os.O_RDONLY
            | getattr(os, "O_BINARY", 0)
            | getattr(os, "O_NOINHERIT", 0)
            | getattr(os, "O_NOFOLLOW", 0),
        )
    except OSError as exc:
        raise SourceDataPromotionError(
            "Stage authority file could not be opened without identity drift."
        ) from exc
    with os.fdopen(descriptor, "rb") as handle:
        before = os.fstat(handle.fileno())
        if not stat.S_ISREG(before.st_mode):
            raise SourceDataPromotionError("Stage authority is not a regular file.")
        if (
            expected.st_dev,
            expected.st_ino,
            expected.st_size,
        ) != (before.st_dev, before.st_ino, before.st_size):
            raise SourceDataPromotionError(
                "Stage authority file identity changed at open."
            )
        raw = handle.read()
        payload = _load_json_bytes(raw)
        after = os.fstat(handle.fileno())
    final = os.lstat(requested)
    identities = {
        (item.st_dev, item.st_ino, item.st_size)
        for item in (before, after, final)
    }
    if (
        len(identities) != 1
        or any(item.st_nlink != 1 for item in (before, after, final))
        or (before.st_mtime_ns, before.st_ctime_ns)
        != (after.st_mtime_ns, after.st_ctime_ns)
        or (expected.st_mtime_ns, expected.st_ctime_ns)
        != (final.st_mtime_ns, final.st_ctime_ns)
    ):
        raise SourceDataPromotionError(
            "Stage authority file identity changed during read."
        )
    return payload


def _register_staged_artifact(
    staging_root: Path,
    staged_path: Path,
    staged: Mapping[str, Any],
    registry_path: Path,
    *,
    expected_parent_identity: tuple[int, int],
    registry_parent_identity: tuple[int, int],
) -> None:
    root = _canonical_stage_root(staging_root)
    if _directory_stat_identity(os.lstat(root)) != expected_parent_identity:
        raise SourceDataPromotionError(
            "Stage authority parent identity changed before index registration."
        )
    canonical_staged = _canonical_stage_file(staged_path)
    if canonical_staged.parent != root:
        raise SourceDataPromotionError("Staged artifact must be directly under staging root.")
    index_path = root / _STAGE_INDEX_FILENAME
    key = _stage_hmac_key(
        registry_path,
        staging_root=root,
        create=True,
        expected_parent_identity=registry_parent_identity,
    )
    with _registry_lock(index_path):
        if index_path.exists():
            index = dict(_load_stage_authority_json(index_path))
            entries = _validate_stage_index(index, key)
        else:
            index = {
                "schema": _STAGE_INDEX_SCHEMA,
                "schema_version": _STAGE_INDEX_SCHEMA_VERSION,
                "entries": [],
                "hmac_sha256": "",
            }
            entries = index["entries"]
        artifact_id = str(staged["artifact_id"])
        if any(
            entry["artifact_id"] == artifact_id
            or entry["relative_path"] == staged_path.name
            or entry["batch_identity_sha256"] == staged["batch_identity_sha256"]
            for entry in entries
        ):
            raise SourceDataPromotionError("Staged artifact is already registered.")
        entries.append(
            {
                "artifact_id": artifact_id,
                "batch_identity_sha256": staged["batch_identity_sha256"],
                "consumer_catalog_path": "",
                "consumer_context_sha256": "",
                "consumer_draft_id": "",
                "consumption_state": "",
                "consumed_receipt_sha256": "",
                "relative_path": staged_path.name,
                "staged_batch_sha256": staged["sha256"],
            }
        )
        entries.sort(key=lambda entry: entry["artifact_id"])
        index["hmac_sha256"] = _stage_index_hmac(index, key)
        _atomic_replace_json(
            index_path,
            index,
            expected_parent_identity=expected_parent_identity,
        )


@contextmanager
def _locked_stage_and_registry(
    staged_path: Path,
    staging_root: Path | str,
    staged: Mapping[str, Any],
    registry: SourceRegistry,
    *,
    catalog_authority_path: Path,
    context: CatalogContext,
    draft_id: str,
):
    registry_parent_identity = _required_registry_parent_identity(registry)
    root = _canonical_stage_root(Path(staging_root))
    parent_identity = _directory_stat_identity(os.lstat(root))
    path = _canonical_stage_file(staged_path)
    if path.parent != root:
        raise SourceDataPromotionError(
            "Staged artifact path is outside the explicit staging root."
        )
    index_path = root / _STAGE_INDEX_FILENAME
    key = _stage_hmac_key(
        registry.path,
        staging_root=root,
        create=False,
        expected_parent_identity=registry_parent_identity,
    )
    with _registry_lock(index_path):
        current_staged = _load_stage_authority_json(path)
        _validate_staged_batch(current_staged)
        entries = _validate_stage_index(
            _load_stage_authority_json(index_path), key
        )
        expected = {
            "artifact_id": current_staged["artifact_id"],
            "batch_identity_sha256": current_staged["batch_identity_sha256"],
            "relative_path": staged_path.name,
            "staged_batch_sha256": current_staged["sha256"],
        }
        matched = next(
            (
                entry
                for entry in entries
                if all(entry[name] == value for name, value in expected.items())
            ),
            None,
        )
        if matched is None or current_staged != staged:
            raise SourceDataPromotionError(
                "Staged artifact changed before the Catalog write boundary."
            )
        if _directory_stat_identity(os.lstat(root)) != parent_identity:
            raise SourceDataPromotionError(
                "Stage authority parent identity changed during trusted read."
            )
        state = matched["consumption_state"]
        catalog_path = str(_canonical_stage_file(catalog_authority_path))
        if state == "committed":
            raise SourceDataPromotionError(
                "Staged artifact is already consumed and cannot be replayed."
            )
        if state == "pending" and (
            matched["consumer_catalog_path"] != catalog_path
            or matched["consumer_context_sha256"]
            != _catalog_context_sha256(context)
            or matched["consumer_draft_id"] != draft_id
        ):
            raise SourceDataPromotionError(
                "Staged artifact is reserved by another Catalog authority."
            )
        with _registry_lock(registry.path):
            current_registry = SourceRegistry.load(registry.path)
            if current_registry._baseline_parent_identity != registry_parent_identity:
                raise SourceDataPromotionError(
                    "Source registry parent identity changed before draft import."
                )
            yield (
                current_registry,
                current_staged,
                parent_identity,
                registry_parent_identity,
            )


def _validate_registered_stage(
    staged_path: Path,
    staging_root: Path | str,
    staged: Mapping[str, Any],
    registry_path: Path,
    *,
    expected_registry_parent_identity: tuple[int, int],
    catalog_authority_path: Path | None = None,
    context: CatalogContext | None = None,
    draft_id: str = "",
) -> None:
    root = _canonical_stage_root(Path(staging_root))
    path = _canonical_stage_file(staged_path)
    if path.parent != root:
        raise SourceDataPromotionError(
            "Staged artifact path is outside the explicit staging root."
        )
    index_path = root / _STAGE_INDEX_FILENAME
    key = _stage_hmac_key(
        registry_path,
        staging_root=root,
        create=False,
        expected_parent_identity=expected_registry_parent_identity,
    )
    with _registry_lock(index_path):
        if not index_path.is_file():
            raise SourceDataPromotionError("Staged artifact is not registered.")
        entries = _validate_stage_index(
            _load_stage_authority_json(index_path), key
        )
        expected = {
            "artifact_id": staged["artifact_id"],
            "batch_identity_sha256": staged["batch_identity_sha256"],
            "relative_path": staged_path.name,
            "staged_batch_sha256": staged["sha256"],
        }
        matched = next(
            (
                entry
                for entry in entries
                if all(entry[name] == value for name, value in expected.items())
            ),
            None,
        )
        if matched is None:
            raise SourceDataPromotionError(
                "Staged artifact identity is not registered for this path."
            )
        if matched["consumption_state"] == "pending" and catalog_authority_path is not None:
            catalog_path = str(_canonical_stage_file(catalog_authority_path))
            if (
                matched["consumer_catalog_path"] == catalog_path
                and context is not None
                and matched["consumer_context_sha256"]
                == _catalog_context_sha256(context)
                and matched["consumer_draft_id"] == draft_id
            ):
                return
            raise SourceDataPromotionError(
                "Staged artifact is reserved by another Catalog context or authority."
            )
        if matched["consumed_receipt_sha256"]:
            raise SourceDataPromotionError(
                "Staged artifact is already consumed and cannot be replayed."
            )


def _validate_stage_index(
    payload: Mapping[str, Any], key: bytes
) -> list[dict[str, Any]]:
    if set(payload) != {"schema", "schema_version", "entries", "hmac_sha256"}:
        raise SourceDataPromotionError("Stage index fields are invalid.")
    if (
        payload.get("schema") != _STAGE_INDEX_SCHEMA
        or payload.get("schema_version") != _STAGE_INDEX_SCHEMA_VERSION
    ):
        raise SourceDataPromotionError("Stage index schema is invalid.")
    supplied_hmac = payload.get("hmac_sha256")
    if not isinstance(supplied_hmac, str) or not hmac.compare_digest(
        supplied_hmac, _stage_index_hmac(payload, key)
    ):
        raise SourceDataPromotionError("Stage index HMAC is invalid.")
    entries = payload.get("entries")
    if not isinstance(entries, list):
        raise SourceDataPromotionError("Stage index entries must be a list.")
    expected_fields = {
        "artifact_id",
        "batch_identity_sha256",
        "consumer_catalog_path",
        "consumer_context_sha256",
        "consumer_draft_id",
        "consumption_state",
        "consumed_receipt_sha256",
        "relative_path",
        "staged_batch_sha256",
    }
    artifact_ids: set[str] = set()
    relative_paths: set[str] = set()
    identities: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != expected_fields:
            raise SourceDataPromotionError("Stage index entry fields are invalid.")
        artifact_id = _required_text(entry["artifact_id"], "stage artifact_id")
        relative_path = _required_text(entry["relative_path"], "stage relative_path")
        identity = _required_text(
            entry["batch_identity_sha256"], "stage batch_identity_sha256"
        )
        consumed = entry["consumed_receipt_sha256"]
        if not isinstance(consumed, str) or (consumed and not _is_sha256(consumed)):
            raise SourceDataPromotionError("Stage index consumption marker is invalid.")
        state = entry["consumption_state"]
        consumer_path = entry["consumer_catalog_path"]
        consumer_context_sha256 = entry["consumer_context_sha256"]
        consumer_draft_id = entry["consumer_draft_id"]
        if state not in {"", "pending", "committed"}:
            raise SourceDataPromotionError("Stage index consumption state is invalid.")
        if not all(
            isinstance(item, str)
            for item in (consumer_path, consumer_context_sha256, consumer_draft_id)
        ):
            raise SourceDataPromotionError("Stage index consumer identity is invalid.")
        if state == "":
            if consumer_path or consumer_context_sha256 or consumer_draft_id or consumed:
                raise SourceDataPromotionError("Unused stage entry has consumer identity.")
        elif (
            not Path(consumer_path).is_absolute()
            or not _is_sha256(consumer_context_sha256)
            or not consumer_draft_id
            or not consumed
        ):
            raise SourceDataPromotionError("Consumed stage entry lacks consumer identity.")
        if Path(relative_path).name != relative_path:
            raise SourceDataPromotionError("Stage index relative_path is invalid.")
        if not _is_sha256(identity) or not _is_sha256(entry["staged_batch_sha256"]):
            raise SourceDataPromotionError("Stage index hash is invalid.")
        if (
            artifact_id in artifact_ids
            or relative_path in relative_paths
            or identity in identities
        ):
            raise SourceDataPromotionError("Stage index contains duplicate identity.")
        artifact_ids.add(artifact_id)
        relative_paths.add(relative_path)
        identities.add(identity)
    return entries


def _transition_registered_stage(
    staged_path: Path,
    staging_root: Path | str,
    receipt: DraftSourceImportReceipt,
    registry_path: Path,
    catalog_authority_path: Path,
    expected_parent_identity: tuple[int, int],
    expected_registry_parent_identity: tuple[int, int],
    *,
    target_state: str,
) -> str:
    """Transition one stage entry while its caller holds both authority locks."""

    if target_state not in {"pending", "pending_replace", "committed"} or not receipt.has_valid_hash():
        raise SourceDataPromotionError("Stage consumption transition is invalid.")
    root = _canonical_stage_root(Path(staging_root))
    path = _canonical_stage_file(staged_path)
    catalog_path = str(_canonical_stage_file(catalog_authority_path))
    if path.parent != root:
        raise SourceDataPromotionError(
            "Staged artifact path is outside the explicit staging root."
        )
    index_path = root / _STAGE_INDEX_FILENAME
    key = _stage_hmac_key(
        registry_path,
        staging_root=root,
        create=False,
        expected_parent_identity=expected_registry_parent_identity,
    )
    index = dict(_load_stage_authority_json(index_path))
    entries = _validate_stage_index(index, key)
    matched = [
        entry
        for entry in entries
        if entry["artifact_id"] == receipt.artifact_id
        and entry["batch_identity_sha256"] == receipt.batch_identity_sha256
        and entry["relative_path"] == path.name
        and entry["staged_batch_sha256"] == receipt.staged_batch_sha256
    ]
    if len(matched) != 1:
        raise SourceDataPromotionError(
            "Stage consumption identity is not uniquely registered."
        )
    entry = matched[0]
    previous_receipt_hash = str(entry["consumed_receipt_sha256"])
    previous_state = str(entry["consumption_state"])
    if previous_state == "committed":
        raise SourceDataPromotionError(
            "Staged artifact is already consumed and cannot be replayed."
        )
    if previous_state == "pending" and (
        entry["consumer_catalog_path"] != catalog_path
        or entry["consumer_context_sha256"]
        != _receipt_context_sha256(receipt)
        or entry["consumer_draft_id"] != receipt.draft_id
    ):
        raise SourceDataPromotionError(
            "Staged artifact is reserved by another Catalog authority."
        )
    if target_state == "pending" and previous_state == "pending":
        if previous_receipt_hash != receipt.receipt_sha256:
            raise SourceDataPromotionError(
                "Staged artifact is reserved by another approval receipt identity."
            )
        return previous_receipt_hash
    if target_state == "committed" and (
        previous_state != "pending"
        or previous_receipt_hash != receipt.receipt_sha256
    ):
        raise SourceDataPromotionError("Stage commitment does not match its reservation.")
    entry["consumer_catalog_path"] = catalog_path
    entry["consumer_context_sha256"] = _receipt_context_sha256(receipt)
    entry["consumer_draft_id"] = receipt.draft_id
    entry["consumption_state"] = (
        "pending" if target_state == "pending_replace" else target_state
    )
    entry["consumed_receipt_sha256"] = receipt.receipt_sha256
    index["hmac_sha256"] = _stage_index_hmac(index, key)
    _atomic_replace_json(
        index_path,
        index,
        expected_parent_identity=expected_parent_identity,
    )
    return previous_receipt_hash


def _reserve_registered_stage(
    staged_path: Path,
    staging_root: Path | str,
    receipt: DraftSourceImportReceipt,
    registry_path: Path,
    catalog_authority_path: Path,
    expected_parent_identity: tuple[int, int],
    expected_registry_parent_identity: tuple[int, int],
) -> str:
    return _transition_registered_stage(
        staged_path,
        staging_root,
        receipt,
        registry_path,
        catalog_authority_path,
        expected_parent_identity,
        expected_registry_parent_identity,
        target_state="pending",
    )


def _commit_registered_stage(
    staged_path: Path,
    staging_root: Path | str,
    receipt: DraftSourceImportReceipt,
    registry_path: Path,
    catalog_authority_path: Path,
    expected_parent_identity: tuple[int, int],
    expected_registry_parent_identity: tuple[int, int],
) -> None:
    _transition_registered_stage(
        staged_path,
        staging_root,
        receipt,
        registry_path,
        catalog_authority_path,
        expected_parent_identity,
        expected_registry_parent_identity,
        target_state="committed",
    )


def _replace_pending_registered_stage(
    staged_path: Path,
    staging_root: Path | str,
    receipt: DraftSourceImportReceipt,
    registry_path: Path,
    catalog_authority_path: Path,
    expected_parent_identity: tuple[int, int],
    expected_registry_parent_identity: tuple[int, int],
) -> None:
    _transition_registered_stage(
        staged_path,
        staging_root,
        receipt,
        registry_path,
        catalog_authority_path,
        expected_parent_identity,
        expected_registry_parent_identity,
        target_state="pending_replace",
    )


def _stage_index_hmac(payload: Mapping[str, Any], key: bytes) -> str:
    unsigned = {
        "schema": payload["schema"],
        "schema_version": payload["schema_version"],
        "entries": payload["entries"],
    }
    return hmac.new(
        key,
        json.dumps(
            unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _catalog_context_sha256(context: CatalogContext) -> str:
    return _canonical_sha256(context.canonical_mapping())


def _receipt_context_sha256(receipt: DraftSourceImportReceipt) -> str:
    return _canonical_sha256(
        {
            "operator_id": receipt.operator_id,
            "workspace_id": receipt.workspace_id,
            "tenant_id": receipt.tenant_id,
            "scope": receipt.scope,
        }
    )


def _stage_hmac_key(
    registry_path: Path,
    *,
    staging_root: Path,
    create: bool,
    expected_parent_identity: tuple[int, int] | None,
) -> bytes:
    try:
        key_path = _canonical_registry_path(
            registry_path.with_name(f"{registry_path.name}.stage-key")
        )
    except SourceRegistryError as exc:
        raise SourceDataPromotionError("Stage authority key path is invalid.") from exc
    if expected_parent_identity is not None and _directory_stat_identity(
        os.lstat(key_path.parent)
    ) != expected_parent_identity:
        raise SourceDataPromotionError(
            "Stage authority key parent identity changed before access."
        )
    root = staging_root.resolve()
    if key_path == root or root in key_path.parents:
        raise SourceDataPromotionError(
            "Stage authority key must be outside the staging root."
        )
    if create and not key_path.exists():
        if expected_parent_identity is None:
            raise SourceDataPromotionError(
                "Stage authority key parent identity is not bound."
            )
        try:
            _atomic_publish_bytes(
                key_path,
                secrets.token_bytes(32),
                expected_parent_identity=expected_parent_identity,
            )
        except SourceRegistryError as exc:
            if (
                "Immutable artifact already exists" not in str(exc)
                or not key_path.exists()
                ):
                raise
    try:
        if expected_parent_identity is None:
            key = _read_registry_authority_bytes(key_path)
        else:
            with _directory_commit_guard(
                key_path.parent,
                expected_identity=expected_parent_identity,
            ):
                key = _read_registry_authority_bytes(key_path)
    except (OSError, SourceRegistryError) as exc:
        raise SourceDataPromotionError("Stage authority key is unavailable.") from exc
    if len(key) != 32:
        raise SourceDataPromotionError("Stage authority key is invalid.")
    return key


def _load_json_bytes(raw: bytes) -> Mapping[str, Any]:
    def reject_constant(value: str) -> None:
        raise SourceDataPromotionError(f"Non-finite JSON value is forbidden: {value}")

    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise SourceDataPromotionError(f"Duplicate JSON key is forbidden: {key}")
            result[key] = value
        return result

    payload = json.loads(
        raw.decode("utf-8"),
        parse_constant=reject_constant,
        object_pairs_hook=reject_duplicate_keys,
    )
    if not isinstance(payload, Mapping):
        raise SourceDataPromotionError("JSON payload must be an object.")
    return payload


def _load_json(path: Path) -> Mapping[str, Any]:
    return _load_json_bytes(path.read_bytes())


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _is_sha256(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return True


def _validate_timestamp(value: Any, field: str) -> str:
    text = _required_text(value, field)
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise SourceDataPromotionError(f"{field} must be an ISO-8601 timestamp.") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise SourceDataPromotionError(f"{field} must include a timezone offset.")
    return text


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SourceDataPromotionError(f"{field} must be a non-empty string.")
    return value.strip()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
