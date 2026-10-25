"""Validated source repository registry for optional external data sources."""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

from apps.web.durable_io import durable_mkdir_parents
from core.admin_catalog.source_policy import (
    SourcePolicyError,
    resolve_local_import_path,
    validate_source_policy_fields,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_REGISTRY_PATH = PROJECT_ROOT / "config" / "source_repositories.json"
SUPPORTED_SCHEMA_VERSION = 1

ALLOWED_SOURCE_TYPES = {"online_api", "online_download", "web_reference", "local_import"}
ALLOWED_STATUSES = {"active", "disabled", "quarantined", "deprecated"}
ONLINE_URL_FIELDS = ("homepage", "endpoint", "documentation_url", "download_url")
SOURCE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_.-]*$")
BATCH_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")


class SourceRegistryError(ValueError):
    """Raised when a source registry or manifest is invalid."""


@dataclass(frozen=True)
class SourceManifest:
    id: str
    label: str
    description: str
    source_type: str
    scopes: tuple[str, ...]
    enabled: bool
    status: str
    homepage: str = ""
    endpoint: str = ""
    documentation_url: str = ""
    download_url: str = ""
    local_path: str = ""
    license: str = ""
    trust_level: str = ""
    import_policy: str = "manual"
    warnings: tuple[str, ...] = ()
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def active(self) -> bool:
        return self.enabled and self.status == "active"

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "SourceManifest":
        if not isinstance(data, Mapping):
            raise SourceRegistryError("Source manifest must be an object.")
        _validate_source_mapping(data)
        try:
            _sha256_json(data)
        except (TypeError, ValueError) as exc:
            raise SourceRegistryError("Source manifest must be strict canonical JSON data.") from exc
        try:
            validate_source_policy_fields(data)
        except SourcePolicyError as exc:
            raise SourceRegistryError(str(exc)) from exc

        known = {
            "id",
            "label",
            "description",
            "source_type",
            "scopes",
            "enabled",
            "status",
            "homepage",
            "endpoint",
            "documentation_url",
            "download_url",
            "local_path",
            "license",
            "trust_level",
            "import_policy",
            "warnings",
        }
        extra = {key: value for key, value in data.items() if key not in known}
        return cls(
            id=data["id"],
            label=data["label"],
            description=data.get("description", ""),
            source_type=data["source_type"],
            scopes=tuple(data["scopes"]),
            enabled=data.get("enabled", False),
            status=data["status"],
            homepage=data.get("homepage", ""),
            endpoint=data.get("endpoint", ""),
            documentation_url=data.get("documentation_url", ""),
            download_url=data.get("download_url", ""),
            local_path=data.get("local_path", ""),
            license=data.get("license", ""),
            trust_level=data.get("trust_level", ""),
            import_policy=data.get("import_policy", "manual"),
            warnings=tuple(data.get("warnings", [])),
            extra=extra,
        )

    def to_mapping(self) -> dict[str, Any]:
        data = dict(self.extra)
        data.update(
            {
                "id": self.id,
                "label": self.label,
                "description": self.description,
                "source_type": self.source_type,
                "homepage": self.homepage,
                "endpoint": self.endpoint,
                "documentation_url": self.documentation_url,
                "download_url": self.download_url,
                "local_path": self.local_path,
                "license": self.license,
                "trust_level": self.trust_level,
                "import_policy": self.import_policy,
                "scopes": list(self.scopes),
                "enabled": self.enabled,
                "status": self.status,
                "warnings": list(self.warnings),
            }
        )
        return {key: value for key, value in data.items() if value not in ("", [], {})}

    def with_state(
        self,
        *,
        enabled: bool,
        status: str,
        extra_updates: Mapping[str, Any] | None = None,
    ) -> "SourceManifest":
        data = self.to_mapping()
        data["enabled"] = enabled
        data["status"] = status
        if extra_updates:
            data.update(extra_updates)
        return SourceManifest.from_mapping(data)


@dataclass(frozen=True)
class SourceImportPlan:
    source: SourceManifest
    action: str
    changed_fields: dict[str, dict[str, Any]]


class SourceRegistry:
    def __init__(
        self,
        path: Path,
        sources: Iterable[SourceManifest],
        schema_version: int = 1,
        revision: int = 0,
        rollback_history: Iterable[Mapping[str, Any]] = (),
        legacy_read_only: bool = False,
    ):
        self.path = _canonical_registry_path(Path(path))
        self.schema_version = schema_version
        if not isinstance(revision, int) or isinstance(revision, bool) or revision < 0:
            raise SourceRegistryError("Source registry revision must be a non-negative integer.")
        self.revision = revision
        self.rollback_history = _validate_rollback_history(list(rollback_history))
        self.legacy_read_only = legacy_read_only
        self._baseline_registry_sha256: str | None = None
        self._baseline_parent_identity: tuple[int, int] | None = None
        source_list = list(sources)
        self._sources = {source.id: source for source in source_list}
        if len(self._sources) != len(source_list):
            raise SourceRegistryError("Duplicate source ids are not allowed.")

    @classmethod
    def load_default(cls) -> "SourceRegistry":
        return cls.load(DEFAULT_SOURCE_REGISTRY_PATH)

    @classmethod
    def load(cls, path: Path | str) -> "SourceRegistry":
        registry_path = Path(path)
        if not registry_path.exists():
            raise SourceRegistryError(f"Source registry not found: {registry_path}")
        parent_identity_before = _directory_stat_identity(
            os.lstat(registry_path.parent)
        )
        payload = _strict_json_load(registry_path)
        parent_identity_after = _directory_stat_identity(
            os.lstat(registry_path.parent)
        )
        if parent_identity_before != parent_identity_after:
            raise SourceRegistryError(
                "Source registry parent identity changed during trusted read."
            )
        if isinstance(payload, dict):
            current_registry_fields = {
                "schema_version",
                "revision",
                "rollback_history",
                "sources",
            }
            legacy_registry_fields = {"schema_version", "sources"}
            if set(payload) == legacy_registry_fields:
                legacy_read_only = True
                revision = 0
                rollback_history = []
            elif set(payload) == current_registry_fields:
                legacy_read_only = False
                revision = payload["revision"]
                raw_rollback_history = payload["rollback_history"]
                if not isinstance(raw_rollback_history, list):
                    raise SourceRegistryError("Source registry rollback_history must be a list.")
                rollback_history = raw_rollback_history
            else:
                raise SourceRegistryError("Source registry wrapper fields are invalid.")
            raw_schema_version = payload.get("schema_version", 1)
            if not isinstance(raw_schema_version, int) or isinstance(raw_schema_version, bool):
                raise SourceRegistryError("Source registry schema_version must be an integer.")
            schema_version = raw_schema_version
            if schema_version != SUPPORTED_SCHEMA_VERSION:
                raise SourceRegistryError(
                    f"Unsupported source registry schema_version: {schema_version}"
                )
            raw_sources = payload.get("sources", [])
        else:
            raise SourceRegistryError("Source registry must use the versioned JSON object wrapper.")
        if not isinstance(raw_sources, list):
            raise SourceRegistryError("Source registry field 'sources' must be a list.")

        sources = [SourceManifest.from_mapping(item) for item in raw_sources]
        ids = [source.id for source in sources]
        if len(ids) != len(set(ids)):
            raise SourceRegistryError("Duplicate source ids are not allowed.")
        registry = cls(
            registry_path,
            sources,
            schema_version=schema_version,
            revision=revision,
            rollback_history=rollback_history,
            legacy_read_only=legacy_read_only,
        )
        registry._baseline_registry_sha256 = _sha256_json(registry._to_payload())
        registry._baseline_parent_identity = parent_identity_after
        return registry

    def list_sources(self, *, scope: str | None = None, active_only: bool = False) -> list[SourceManifest]:
        sources = sorted(self._sources.values(), key=lambda source: source.id)
        if scope:
            sources = [source for source in sources if scope in source.scopes]
        if active_only:
            sources = [source for source in sources if source.active]
        return sources

    def get(self, source_id: str) -> SourceManifest:
        try:
            return self._sources[source_id]
        except KeyError as exc:
            raise SourceRegistryError(f"Unknown source id: {source_id}") from exc

    def enable_source(self, source_id: str, *, allow_quarantined: bool = False) -> SourceManifest:
        source = self.get(source_id)
        if source.status == "deprecated":
            raise SourceRegistryError(f"Source '{source_id}' is deprecated and cannot be enabled.")
        if source.status == "quarantined" and not allow_quarantined:
            raise SourceRegistryError(f"Source '{source_id}' is quarantined; use explicit override to enable it.")
        extra_updates = {}
        if source.status == "quarantined":
            extra_updates["return_status_on_disable"] = "quarantined"
        updated = source.with_state(enabled=True, status="active", extra_updates=extra_updates)
        self._sources[source_id] = updated
        try:
            self.save()
        except BaseException:
            self._sources[source_id] = source
            raise
        return updated

    def disable_source(self, source_id: str) -> SourceManifest:
        source = self.get(source_id)
        if source.status == "deprecated":
            raise SourceRegistryError(f"Source '{source_id}' is deprecated and terminal.")
        status = (
            "quarantined"
            if source.status == "quarantined" or source.extra.get("return_status_on_disable") == "quarantined"
            else "disabled"
        )
        updated = source.with_state(enabled=False, status=status)
        self._sources[source_id] = updated
        try:
            self.save()
        except BaseException:
            self._sources[source_id] = source
            raise
        return updated

    def plan_import_manifest(
        self,
        manifest_path: Path | str,
        *,
        replace: bool = False,
        import_root: Path | str | None = None,
    ) -> SourceImportPlan:
        source = _load_source_manifest(manifest_path, import_root=import_root)
        current = self._sources.get(source.id)
        if current is not None and not replace:
            raise SourceRegistryError(f"Source '{source.id}' already exists. Use replace=True to overwrite.")
        if current is not None:
            _validate_replacement_lifecycle(current, source)
        _validate_server_owned_policy(current, source)

        changed_fields: dict[str, dict[str, Any]] = {}
        if current is not None:
            current_map = current.to_mapping()
            incoming_map = source.to_mapping()
            for key in sorted(set(current_map) | set(incoming_map)):
                if current_map.get(key) != incoming_map.get(key):
                    changed_fields[key] = {
                        "current": current_map.get(key),
                        "incoming": incoming_map.get(key),
                    }

        return SourceImportPlan(
            source=source,
            action="replace" if current is not None else "add",
            changed_fields=changed_fields,
        )

    def stage_manifest(
        self,
        manifest_path: Path | str,
        staging_dir: Path | str,
        *,
        replace: bool = False,
        import_root: Path | str | None = None,
        approval_id: str,
    ) -> Path:
        if not BATCH_ID_RE.fullmatch(approval_id):
            raise SourceRegistryError(f"Invalid approval id '{approval_id}'.")
        if self.legacy_read_only:
            raise SourceRegistryError(
                "Legacy source registry shape is read-only; migrate it before staging imports."
            )
        with _registry_lock(self.path):
            current_registry = SourceRegistry.load(self.path)
            if current_registry.legacy_read_only:
                raise SourceRegistryError(
                    "Legacy source registry shape is read-only; migrate it before staging imports."
                )
            return current_registry._stage_manifest_current(
                manifest_path,
                staging_dir,
                replace=replace,
                import_root=import_root,
                approval_id=approval_id,
            )

    def _stage_manifest_current(
        self,
        manifest_path: Path | str,
        staging_dir: Path | str,
        *,
        replace: bool,
        import_root: Path | str | None,
        approval_id: str,
    ) -> Path:
        plan = self.plan_import_manifest(
            manifest_path,
            replace=replace,
            import_root=import_root,
        )
        source_mapping = plan.source.to_mapping()
        manifest_sha256 = _sha256_json(source_mapping)
        registry_sha256 = _sha256_json(self._to_payload())
        approval_receipt = {
            "schema": "morphic_source_manifest_approval_receipt",
            "schema_version": 1,
            "approval_id": approval_id,
            "source_id": plan.source.id,
            "action": plan.action,
            "registry_revision": self.revision,
            "registry_sha256": registry_sha256,
            "manifest_sha256": manifest_sha256,
        }
        artifact = {
            "schema": "morphic_source_manifest_stage",
            "schema_version": 1,
            "registry_revision": self.revision,
            "registry_sha256": registry_sha256,
            "action": plan.action,
            "import_root": (
                str(Path(import_root).expanduser().resolve(strict=True))
                if plan.source.source_type == "local_import" and import_root is not None
                else ""
            ),
            "manifest_sha256": manifest_sha256,
            "source": source_mapping,
            "approval_receipt": approval_receipt,
        }
        artifact_sha256 = _sha256_json(artifact)
        artifact["artifact_sha256"] = artifact_sha256
        approval_receipt["artifact_sha256"] = artifact_sha256
        target_dir = Path(staging_dir)
        durable_mkdir_parents(target_dir, mode=0o700)
        target_parent_identity = _directory_stat_identity(os.lstat(target_dir))
        staged_path = target_dir / f"{plan.source.id}.{artifact_sha256}.source-stage.json"
        _atomic_publish_json(
            staged_path,
            artifact,
            expected_parent_identity=target_parent_identity,
        )
        return staged_path

    def import_manifest(
        self,
        staged_path: Path | str,
        *,
        rollback_dir: Path | str | None = None,
        batch_id: str | None = None,
    ) -> SourceManifest:
        if self.legacy_read_only:
            raise SourceRegistryError(
                "Legacy source registry shape is read-only; migrate it before import."
            )
        artifact = _load_staged_manifest(staged_path)
        artifact_revision = artifact["registry_revision"]
        if artifact_revision != self.revision:
            raise SourceRegistryError(
                "Staged source manifest registry revision is stale or concurrent."
            )
        if artifact["registry_sha256"] != _sha256_json(self._to_payload()):
            raise SourceRegistryError(
                "Staged source manifest registry baseline is stale or concurrent."
            )
        source = SourceManifest.from_mapping(artifact["source"])
        current = self._sources.get(source.id)
        if current is not None:
            _validate_replacement_lifecycle(current, source)
        _validate_server_owned_policy(current, source)
        expected_action = "replace" if current is not None else "add"
        if artifact["action"] != expected_action:
            raise SourceRegistryError("Staged source manifest action no longer matches registry state.")
        changed_fields = _changed_fields(current, source)
        plan = SourceImportPlan(source=source, action=expected_action, changed_fields=changed_fields)
        previous = current
        previous_registry = self._to_payload()
        previous_registry_sha256 = _sha256_json(previous_registry)
        self._sources[source.id] = source
        expected_revision = self.revision + 1
        expected_registry_sha256 = _sha256_json(
            self._to_payload(revision=expected_revision)
        )
        rollback_root = Path(rollback_dir) if rollback_dir is not None else None
        try:
            if rollback_root is not None:
                self._write_rollback_snapshot(
                    rollback_root,
                    batch_id or _default_batch_id(plan.source.id),
                    plan,
                    expected_current_revision=expected_revision,
                    expected_current_registry_sha256=expected_registry_sha256,
                    previous_registry=previous_registry,
                )
            self.save()
        except BaseException as exc:
            disk_state = "ambiguous"
            try:
                with _registry_lock(self.path):
                    disk_registry = SourceRegistry.load(self.path)
                    disk_sha256 = _sha256_json(disk_registry._to_payload())
                if (
                    disk_registry.revision == expected_revision
                    and disk_sha256 == expected_registry_sha256
                ):
                    disk_state = "committed"
                elif (
                    disk_registry.revision == previous_registry["revision"]
                    and disk_sha256 == previous_registry_sha256
                ):
                    disk_state = "not_committed"
            except (OSError, SourceRegistryError):
                disk_state = "ambiguous"

            if disk_state == "committed":
                self.revision = expected_revision
                self._baseline_registry_sha256 = expected_registry_sha256
                raise SourceRegistryError(
                    "Source import committed but completion was interrupted; "
                    "rollback evidence was retained."
                ) from exc

            if previous is None:
                self._sources.pop(source.id, None)
            else:
                self._sources[source.id] = previous
            if disk_state == "not_committed":
                raise
            raise SourceRegistryError(
                "Source import commit state is ambiguous; rollback evidence was retained."
            ) from exc
        return source

    def rollback_import(
        self,
        batch_id: str,
        *,
        rollback_dir: Path | str,
        expected_revision: int,
    ) -> None:
        if any(item["batch_id"] == batch_id for item in self.rollback_history):
            raise SourceRegistryError(f"Rollback batch already reverted or consumed: {batch_id}")
        snapshot_path = _rollback_snapshot_path(Path(rollback_dir), batch_id)
        rollback_parent_identity = _directory_stat_identity(
            os.lstat(snapshot_path.parent)
        )
        if not snapshot_path.exists():
            raise SourceRegistryError(f"Rollback batch not found: {batch_id}")
        consumed_path = _rollback_consumed_path(Path(rollback_dir), batch_id)
        snapshot = _strict_json_load(snapshot_path)
        expected_snapshot_fields = {
            "schema",
            "schema_version",
            "batch_id",
            "registry_path",
            "source_id",
            "action",
            "changed_fields",
            "expected_current_revision",
            "expected_current_registry_sha256",
            "previous_registry",
            "snapshot_sha256",
        }
        if not isinstance(snapshot, dict) or set(snapshot) != expected_snapshot_fields:
            raise SourceRegistryError("Rollback snapshot fields are invalid.")
        if Path(str(snapshot["registry_path"])).resolve() != self.path.resolve():
            raise SourceRegistryError("Rollback snapshot registry path mismatch.")
        if snapshot.get("batch_id") != batch_id:
            raise SourceRegistryError(f"Rollback batch id mismatch in {snapshot_path}")
        snapshot_schema_version = snapshot.get("schema_version")
        if (
            snapshot.get("schema") != "morphic_source_registry_rollback"
            or not isinstance(snapshot_schema_version, int)
            or isinstance(snapshot_schema_version, bool)
            or snapshot_schema_version != 2
        ):
            raise SourceRegistryError("Rollback snapshot schema is unsupported.")
        snapshot_sha256 = snapshot.get("snapshot_sha256")
        unsigned_snapshot = dict(snapshot)
        unsigned_snapshot.pop("snapshot_sha256", None)
        if snapshot_sha256 != _sha256_json(unsigned_snapshot):
            raise SourceRegistryError("Rollback snapshot integrity hash mismatch.")
        if (
            not isinstance(expected_revision, int)
            or isinstance(expected_revision, bool)
            or expected_revision != self.revision
            or snapshot.get("expected_current_revision") != expected_revision
        ):
            raise SourceRegistryError("Rollback registry revision conflict.")
        if snapshot.get("expected_current_registry_sha256") != _sha256_json(
            self._to_payload()
        ):
            raise SourceRegistryError("Rollback current registry state hash conflict.")
        previous = snapshot.get("previous_registry")
        if not isinstance(previous, dict):
            raise SourceRegistryError("Rollback snapshot is missing previous_registry.")
        if set(previous) != {"schema_version", "revision", "rollback_history", "sources"}:
            raise SourceRegistryError("Rollback previous_registry fields are invalid.")
        previous_schema = previous.get("schema_version")
        previous_revision = previous.get("revision")
        if previous_schema != SUPPORTED_SCHEMA_VERSION:
            raise SourceRegistryError("Rollback previous_registry schema is unsupported.")
        if (
            not isinstance(previous_revision, int)
            or isinstance(previous_revision, bool)
            or previous_revision < 0
        ):
            raise SourceRegistryError("Rollback previous_registry revision is invalid.")
        raw_history = previous.get("rollback_history")
        if not isinstance(raw_history, list):
            raise SourceRegistryError("Rollback previous_registry history is invalid.")
        _validate_rollback_history(raw_history)
        raw_sources = previous.get("sources", [])
        if not isinstance(raw_sources, list):
            raise SourceRegistryError("Rollback snapshot field 'sources' must be a list.")

        restored = [SourceManifest.from_mapping(item) for item in raw_sources]
        old_sources = self._sources
        old_rollback_history = list(self.rollback_history)
        previous_registry_sha256 = _sha256_json(self._to_payload())
        reverted_at = _utc_now()
        self._sources = {source.id: source for source in restored}
        self.rollback_history.append(
            {
                "batch_id": batch_id,
                "snapshot_sha256": snapshot_sha256,
                "reverted_at": reverted_at,
            }
        )
        expected_revision_after_rollback = self.revision + 1
        expected_registry_sha256 = _sha256_json(
            self._to_payload(revision=expected_revision_after_rollback)
        )
        try:
            self.save()
        except Exception as exc:
            disk_state = "ambiguous"
            try:
                with _registry_lock(self.path):
                    disk_registry = SourceRegistry.load(self.path)
                    disk_sha256 = _sha256_json(disk_registry._to_payload())
                if (
                    disk_registry.revision == expected_revision_after_rollback
                    and disk_sha256 == expected_registry_sha256
                ):
                    disk_state = "committed"
                elif (
                    disk_registry.revision == expected_revision
                    and disk_sha256 == previous_registry_sha256
                ):
                    disk_state = "not_committed"
            except (OSError, SourceRegistryError):
                disk_state = "ambiguous"
            if disk_state == "committed":
                self.revision = expected_revision_after_rollback
                self._baseline_registry_sha256 = expected_registry_sha256
            elif disk_state == "not_committed":
                self._sources = old_sources
                self.rollback_history = old_rollback_history
                raise
            else:
                raise SourceRegistryError(
                    "Rollback commit state is ambiguous; authoritative state must be inspected."
                ) from exc
        marker = {
            "schema": "morphic_source_registry_rollback_consumed",
            "schema_version": 1,
            "batch_id": batch_id,
            "snapshot_sha256": snapshot_sha256,
            "reverted_registry_revision": self.revision,
            "consumed_at": reverted_at,
        }
        try:
            _atomic_publish_json(
                consumed_path,
                marker,
                expected_parent_identity=rollback_parent_identity,
            )
        except (OSError, SourceRegistryError):
            # rollback_history is the atomic authoritative consumed state;
            # this sidecar is supplementary evidence only.
            pass

    def save(self) -> None:
        if self.legacy_read_only:
            raise SourceRegistryError(
                "Legacy source registry shape is read-only; explicit migration is required."
            )
        if self._baseline_parent_identity is None:
            raise SourceRegistryError("Source registry parent identity is not bound.")
        current_parent_identity = _directory_stat_identity(os.lstat(self.path.parent))
        if current_parent_identity != self._baseline_parent_identity:
            raise SourceRegistryError(
                "Source registry parent identity changed before commit."
            )
        with _directory_commit_guard(
            self.path.parent,
            expected_identity=self._baseline_parent_identity,
        ):
            with _registry_lock(self.path):
                if self.path.exists():
                    current = SourceRegistry.load(self.path)
                    if current.legacy_read_only:
                        raise SourceRegistryError(
                            "Legacy source registry shape is read-only; explicit migration is required."
                        )
                    current_sha256 = _sha256_json(current._to_payload())
                else:
                    current = None
                    current_sha256 = None
                if current is not None and (
                    current.revision != self.revision
                    or self._baseline_registry_sha256 is None
                    or current_sha256 != self._baseline_registry_sha256
                ):
                    raise SourceRegistryError(
                        "Source registry state conflict; stale or concurrent writer rejected."
                    )
                if current is None and (
                    self.revision != 0 or self._baseline_registry_sha256 is not None
                ):
                    raise SourceRegistryError("Source registry disappeared before save.")
                next_revision = self.revision + 1
                next_payload = self._to_payload(revision=next_revision)
                _atomic_replace_json(
                    self.path,
                    next_payload,
                    authority_validator=_canonical_registry_path,
                    expected_parent_identity=self._baseline_parent_identity,
                )
                self.revision = next_revision
                self._baseline_registry_sha256 = _sha256_json(next_payload)

    def _to_payload(self, *, revision: int | None = None) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "revision": self.revision if revision is None else revision,
            "rollback_history": [dict(item) for item in self.rollback_history],
            "sources": [source.to_mapping() for source in self.list_sources()],
        }

    def _write_rollback_snapshot(
        self,
        rollback_dir: Path,
        batch_id: str,
        plan: SourceImportPlan,
        *,
        expected_current_revision: int,
        expected_current_registry_sha256: str,
        previous_registry: Mapping[str, Any],
    ) -> Path:
        if not BATCH_ID_RE.fullmatch(batch_id):
            raise SourceRegistryError(f"Invalid rollback batch id '{batch_id}'.")
        durable_mkdir_parents(rollback_dir, mode=0o700)
        rollback_parent_identity = _directory_stat_identity(os.lstat(rollback_dir))
        snapshot_path = _rollback_snapshot_path(rollback_dir, batch_id)
        if snapshot_path.exists():
            raise SourceRegistryError(f"Rollback batch already exists: {batch_id}")
        snapshot = {
            "schema": "morphic_source_registry_rollback",
            "schema_version": 2,
            "batch_id": batch_id,
            "registry_path": str(self.path),
            "source_id": plan.source.id,
            "action": plan.action,
            "changed_fields": plan.changed_fields,
            "expected_current_revision": expected_current_revision,
            "expected_current_registry_sha256": expected_current_registry_sha256,
            "previous_registry": dict(previous_registry),
        }
        snapshot["snapshot_sha256"] = _sha256_json(snapshot)
        _atomic_publish_json(
            snapshot_path,
            snapshot,
            expected_parent_identity=rollback_parent_identity,
        )
        return snapshot_path


def validate_manifest(
    data: Mapping[str, Any],
    *,
    import_root: Path | str | None = None,
) -> SourceManifest:
    payload: Mapping[str, Any] = data
    if "source" in data:
        if set(data) != {"schema_version", "source"}:
            raise SourceRegistryError("Source manifest wrapper fields are invalid.")
        raw_schema_version = data.get("schema_version", SUPPORTED_SCHEMA_VERSION)
        if not isinstance(raw_schema_version, int) or isinstance(raw_schema_version, bool):
            raise SourceRegistryError("Source manifest schema_version must be an integer.")
        schema_version = raw_schema_version
        if schema_version != SUPPORTED_SCHEMA_VERSION:
            raise SourceRegistryError(
                f"Unsupported source manifest schema_version: {schema_version}"
            )
        raw_source = data["source"]
        if not isinstance(raw_source, Mapping):
            raise SourceRegistryError("Import manifest must contain one source object.")
        payload = raw_source
    elif "schema_version" in data:
        raise SourceRegistryError("Source manifest wrapper requires a source object.")

    normalized = dict(payload)
    if str(normalized.get("source_type", "")) == "local_import":
        if import_root is None:
            raise SourceRegistryError("local_import manifests require an explicit import_root.")
        try:
            normalized["local_path"] = str(
                resolve_local_import_path(
                    str(normalized.get("local_path", "")),
                    import_root=import_root,
                )
            )
        except SourcePolicyError as exc:
            raise SourceRegistryError(str(exc)) from exc
    return SourceManifest.from_mapping(normalized)


def validate_manifest_file(
    manifest_path: Path | str,
    *,
    import_root: Path | str | None = None,
) -> SourceManifest:
    """Strictly parse and validate one source manifest file."""
    return _load_source_manifest(manifest_path, import_root=import_root)


def _load_source_manifest(
    manifest_path: Path | str,
    *,
    import_root: Path | str | None,
) -> SourceManifest:
    path = Path(manifest_path)
    payload = _strict_json_load(path)
    if not isinstance(payload, dict):
        raise SourceRegistryError("Import manifest must contain one source object.")
    return validate_manifest(payload, import_root=import_root)


def _load_staged_manifest(staged_path: Path | str) -> dict[str, Any]:
    path = Path(staged_path)
    payload = _strict_json_load(path)
    if not isinstance(payload, dict) or payload.get("schema") != "morphic_source_manifest_stage":
        raise SourceRegistryError("Source import requires a staged manifest artifact with approval receipt.")
    staged_schema_version = payload.get("schema_version")
    if (
        not isinstance(staged_schema_version, int)
        or isinstance(staged_schema_version, bool)
        or staged_schema_version != 1
    ):
        raise SourceRegistryError("Staged source manifest has an unsupported schema_version.")
    expected_artifact_fields = {
        "schema",
        "schema_version",
        "registry_revision",
        "registry_sha256",
        "action",
        "import_root",
        "manifest_sha256",
        "source",
        "approval_receipt",
        "artifact_sha256",
    }
    if set(payload) != expected_artifact_fields:
        raise SourceRegistryError("Staged source manifest artifact fields are invalid.")
    source = payload.get("source")
    receipt = payload.get("approval_receipt")
    if not isinstance(source, dict) or not isinstance(receipt, dict):
        raise SourceRegistryError("Staged source manifest is missing source or approval receipt.")
    if receipt.get("schema") != "morphic_source_manifest_approval_receipt":
        raise SourceRegistryError("Staged source manifest approval receipt is invalid.")
    receipt_schema_version = receipt.get("schema_version")
    if (
        not isinstance(receipt_schema_version, int)
        or isinstance(receipt_schema_version, bool)
        or receipt_schema_version != 1
    ):
        raise SourceRegistryError("Staged source manifest approval receipt schema_version is invalid.")
    expected_receipt_fields = {
        "schema",
        "schema_version",
        "approval_id",
        "source_id",
        "action",
        "registry_revision",
        "registry_sha256",
        "manifest_sha256",
        "artifact_sha256",
    }
    if set(receipt) != expected_receipt_fields:
        raise SourceRegistryError("Staged source manifest approval receipt fields are invalid.")
    approval_id = receipt.get("approval_id")
    if not isinstance(approval_id, str) or not BATCH_ID_RE.fullmatch(approval_id):
        raise SourceRegistryError("Staged source manifest approval id is invalid.")
    manifest_sha256 = _sha256_json(source)
    if payload.get("manifest_sha256") != manifest_sha256:
        raise SourceRegistryError("Staged source manifest hash mismatch.")
    expected_receipt = {
        "source_id": source.get("id"),
        "action": payload.get("action"),
        "registry_revision": payload.get("registry_revision"),
        "registry_sha256": payload.get("registry_sha256"),
        "manifest_sha256": manifest_sha256,
    }
    if any(receipt.get(field) != value for field, value in expected_receipt.items()):
        raise SourceRegistryError("Staged source manifest approval receipt mismatch.")
    if payload.get("action") not in {"add", "replace"}:
        raise SourceRegistryError("Staged source manifest action is invalid.")
    revision = payload.get("registry_revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 0:
        raise SourceRegistryError("Staged source manifest registry revision is invalid.")
    registry_sha256 = payload.get("registry_sha256")
    if not isinstance(registry_sha256, str) or not re.fullmatch(
        r"[0-9a-f]{64}", registry_sha256
    ):
        raise SourceRegistryError("Staged source manifest registry hash is invalid.")

    claimed_artifact_hash = payload.get("artifact_sha256")
    unsigned_artifact = dict(payload)
    unsigned_artifact.pop("artifact_sha256", None)
    unsigned_artifact["approval_receipt"] = dict(payload["approval_receipt"])
    unsigned_artifact["approval_receipt"].pop("artifact_sha256", None)
    if claimed_artifact_hash != _sha256_json(unsigned_artifact):
        raise SourceRegistryError("Staged source manifest artifact hash mismatch.")
    if receipt.get("artifact_sha256") != claimed_artifact_hash:
        raise SourceRegistryError("Staged source manifest approval artifact hash mismatch.")

    source_manifest = SourceManifest.from_mapping(source)
    if source_manifest.source_type == "local_import":
        import_root = payload.get("import_root")
        if not isinstance(import_root, str) or not import_root:
            raise SourceRegistryError("Staged local source manifest is missing its import root.")
        try:
            canonical = resolve_local_import_path(
                source_manifest.local_path,
                import_root=import_root,
            )
        except SourcePolicyError as exc:
            raise SourceRegistryError(str(exc)) from exc
        if str(canonical) != source_manifest.local_path:
            raise SourceRegistryError("Staged local source path changed after policy validation.")
    return payload


def _changed_fields(
    current: SourceManifest | None,
    incoming: SourceManifest,
) -> dict[str, dict[str, Any]]:
    if current is None:
        return {}
    current_map = current.to_mapping()
    incoming_map = incoming.to_mapping()
    return {
        key: {"current": current_map.get(key), "incoming": incoming_map.get(key)}
        for key in sorted(set(current_map) | set(incoming_map))
        if current_map.get(key) != incoming_map.get(key)
    }


def _sha256_json(value: Any) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _json_bytes(payload: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(payload, allow_nan=False, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def _temporary_path(target: Path) -> Path:
    return target.with_name(f".{target.name}.tmp-{uuid.uuid4().hex}")


_BOUND_TEMP_DESCRIPTORS: dict[str, int] = {}
_BOUND_TEMP_DESCRIPTORS_LOCK = threading.Lock()


def _write_temporary_bytes(target: Path, payload: bytes) -> Path:
    temporary = _temporary_path(target)
    try:
        with temporary.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return temporary


def _require_no_reparse_components(path: Path) -> None:
    for component in list(reversed(path.parents)) + [path]:
        try:
            attributes = os.lstat(component)
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(attributes.st_mode) or bool(
            getattr(attributes, "st_file_attributes", 0) & 0x400
        ):
            raise SourceRegistryError(
                f"Authority path contains a symlink or reparse point: {path}"
            )


@contextmanager
def _directory_commit_guard(
    parent: Path,
    *,
    expected_identity: tuple[int, int] | None = None,
):
    parent = Path(os.path.abspath(parent.expanduser()))
    _require_no_reparse_components(parent)
    initial = os.lstat(parent)
    if not stat.S_ISDIR(initial.st_mode):
        raise SourceRegistryError(f"Authority parent is not a directory: {parent}")
    initial_identity = _directory_stat_identity(initial)
    if expected_identity is not None and initial_identity != expected_identity:
        raise SourceRegistryError(
            f"Authority parent identity changed before binding: {parent}"
        )
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        create_file = kernel32.CreateFileW
        create_file.argtypes = [
            wintypes.LPCWSTR,
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.LPVOID,
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.HANDLE,
        ]
        create_file.restype = wintypes.HANDLE
        handle = create_file(
            str(parent),
            0x80000000 | 0x40000000,
            0x00000001 | 0x00000002,
            None,
            3,
            0x02000000 | 0x00200000,
            None,
        )
        invalid = wintypes.HANDLE(-1).value
        if handle in (None, invalid):
            raise SourceRegistryError(
                f"Authority parent handle cannot be opened safely: {parent}"
            )
        opened = os.lstat(parent)
        if _directory_stat_identity(opened) != initial_identity:
            kernel32.CloseHandle(handle)
            raise SourceRegistryError(
                f"Authority parent identity changed at handle open: {parent}"
            )

        def flush_directory() -> None:
            if not kernel32.FlushFileBuffers(handle):
                raise SourceRegistryError(
                    f"Authority parent metadata could not be flushed: {parent}"
                )

        guard = {"parent": parent, "handle": handle, "fd": None}
        try:
            yield guard, flush_directory
        finally:
            kernel32.CloseHandle(handle)
    else:
        descriptor = os.open(
            parent,
            os.O_RDONLY
            | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_NOFOLLOW", 0),
        )

        def flush_directory() -> None:
            os.fsync(descriptor)

        guard = {"parent": parent, "handle": None, "fd": descriptor}
        try:
            if (initial.st_dev, initial.st_ino) != (
                os.fstat(descriptor).st_dev,
                os.fstat(descriptor).st_ino,
            ):
                raise SourceRegistryError(
                    f"Authority parent identity changed at open: {parent}"
                )
            yield guard, flush_directory
        finally:
            os.close(descriptor)
    final = os.lstat(parent)
    if (initial.st_dev, initial.st_ino) != (final.st_dev, final.st_ino):
        raise SourceRegistryError(
            f"Authority parent identity changed during commit: {parent}"
        )


@contextmanager
def _held_file_identity(path: Path):
    if os.name == "nt":
        import ctypes
        import msvcrt
        from ctypes import wintypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        create_file = kernel32.CreateFileW
        create_file.argtypes = [
            wintypes.LPCWSTR,
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.LPVOID,
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.HANDLE,
        ]
        create_file.restype = wintypes.HANDLE
        handle = create_file(
            str(path),
            0x80000000 | 0x00010000,
            0x00000001 | 0x00000002 | 0x00000004,
            None,
            3,
            0x00200000,
            None,
        )
        invalid = wintypes.HANDLE(-1).value
        if handle in (None, invalid):
            raise SourceRegistryError(f"Temporary authority handle failed: {path}")
        descriptor = msvcrt.open_osfhandle(
            int(handle), os.O_RDONLY | getattr(os, "O_BINARY", 0)
        )
    else:
        descriptor = os.open(
            path,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
        )
    registered = False
    try:
        attributes = os.fstat(descriptor)
        if not stat.S_ISREG(attributes.st_mode) or attributes.st_nlink != 1:
            raise SourceRegistryError(
                f"Temporary authority must be a regular single-link file: {path}"
            )
        descriptor_key = str(Path(os.path.abspath(path)))
        with _BOUND_TEMP_DESCRIPTORS_LOCK:
            if descriptor_key in _BOUND_TEMP_DESCRIPTORS:
                raise SourceRegistryError(
                    f"Temporary authority is already bound: {path}"
                )
            _BOUND_TEMP_DESCRIPTORS[descriptor_key] = descriptor
        registered = True
        yield _authority_stat_identity(attributes)
    finally:
        if registered:
            with _BOUND_TEMP_DESCRIPTORS_LOCK:
                remaining_descriptor = _BOUND_TEMP_DESCRIPTORS.pop(
                    descriptor_key, None
                )
            if remaining_descriptor is not None:
                os.close(remaining_descriptor)
        else:
            os.close(descriptor)


def _windows_rename_bound_temp(source: Path, target: Path, *, replace: bool) -> None:
    import ctypes
    import msvcrt
    import struct
    from ctypes import wintypes

    descriptor_key = str(Path(os.path.abspath(source)))
    with _BOUND_TEMP_DESCRIPTORS_LOCK:
        descriptor = _BOUND_TEMP_DESCRIPTORS.get(descriptor_key)
    if descriptor is None:
        raise SourceRegistryError(f"Temporary authority is not handle-bound: {source}")
    held_attributes = os.fstat(descriptor)
    try:
        named_attributes = os.lstat(source)
    except FileNotFoundError as exc:
        raise SourceRegistryError(
            f"Temporary authority name changed before commit: {source}"
        ) from exc
    if (
        _authority_stat_identity(named_attributes)
        != _authority_stat_identity(held_attributes)
        or held_attributes.st_nlink != 1
    ):
        raise SourceRegistryError(
            f"Temporary authority name changed before commit: {source}"
        )

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    set_information = kernel32.SetFileInformationByHandle
    set_information.argtypes = [
        wintypes.HANDLE,
        ctypes.c_int,
        wintypes.LPVOID,
        wintypes.DWORD,
    ]
    set_information.restype = wintypes.BOOL
    target_name = str(target).encode("utf-16le")
    buffer_size = 20 + len(target_name) + 2
    information = ctypes.create_string_buffer(buffer_size)
    struct.pack_into("<I", information, 0, int(replace))
    struct.pack_into("<Q", information, 8, 0)
    struct.pack_into("<I", information, 16, len(target_name))
    ctypes.memmove(ctypes.addressof(information) + 20, target_name, len(target_name))
    native_handle = msvcrt.get_osfhandle(descriptor)
    if not set_information(native_handle, 3, information, buffer_size):
        error = ctypes.get_last_error()
        if not replace and error in {80, 183}:
            raise FileExistsError(error, "immutable authority already exists", target)
        raise OSError(error, "handle-bound durable authority publish failed", target)
    with _BOUND_TEMP_DESCRIPTORS_LOCK:
        published_descriptor = _BOUND_TEMP_DESCRIPTORS.pop(descriptor_key, None)
    if published_descriptor is not None:
        os.close(published_descriptor)


def _guard_authority_parent(guard: Mapping[str, object]) -> Path:
    parent = guard.get("parent")
    if not isinstance(parent, Path):
        raise SourceRegistryError("Guarded publish authority parent is invalid.")
    return Path(os.path.abspath(parent.expanduser()))


def _same_authority_path(left: Path, right: Path) -> bool:
    return os.path.normcase(str(left)) == os.path.normcase(str(right))


def _require_guarded_publish_paths(
    guard: Mapping[str, object],
    source: Path,
    target: Path,
) -> None:
    parent = _guard_authority_parent(guard)
    source_parent = Path(os.path.abspath(source.expanduser())).parent
    target_parent = Path(os.path.abspath(target.expanduser())).parent
    if not _same_authority_path(source_parent, parent) or not _same_authority_path(
        target_parent, parent
    ):
        raise SourceRegistryError(
            "Guarded publish source and target must stay under the bound authority parent."
        )


def _require_posix_dir_fd_support(
    operation: Callable[..., object],
    operation_label: str,
) -> None:
    if os.name == "nt":
        return
    if operation not in getattr(os, "supports_dir_fd", set()):
        raise SourceRegistryError(
            f"POSIX guarded publish requires dir_fd support for {operation_label}."
        )


def _require_posix_source_inode_bound_publish(operation_label: str) -> None:
    if os.name == "nt":
        return
    raise SourceRegistryError(
        "POSIX source-inode-bound guarded publish is not supported for "
        f"{operation_label}; refusing to mutate authority target."
    )


def _replace_in_guard(guard: Mapping[str, object], source: Path, target: Path) -> None:
    _require_posix_dir_fd_support(os.replace, "replace")
    _require_guarded_publish_paths(guard, source, target)
    _require_posix_source_inode_bound_publish("replace")
    if os.name == "nt":
        _windows_rename_bound_temp(source, target, replace=True)
    else:
        descriptor = int(guard["fd"])
        os.replace(
            source.name,
            target.name,
            src_dir_fd=descriptor,
            dst_dir_fd=descriptor,
        )


def _link_in_guard(guard: Mapping[str, object], source: Path, target: Path) -> None:
    _require_posix_dir_fd_support(os.link, "link")
    _require_guarded_publish_paths(guard, source, target)
    _require_posix_source_inode_bound_publish("link")
    if os.name == "nt":
        _windows_rename_bound_temp(source, target, replace=False)
    else:
        descriptor = int(guard["fd"])
        os.link(
            source.name,
            target.name,
            src_dir_fd=descriptor,
            dst_dir_fd=descriptor,
            follow_symlinks=False,
        )


def _attest_published_bytes(
    target: Path, expected_bytes: bytes, expected_identity: tuple[int, int, int]
) -> None:
    final = os.lstat(target)
    if _authority_stat_identity(final) != expected_identity:
        raise SourceRegistryError(
            f"Published authority identity is ambiguous: {target}"
        )
    if _read_registry_authority_bytes(target) != expected_bytes:
        raise SourceRegistryError(f"Published authority bytes are ambiguous: {target}")


def _atomic_replace_json(
    target: Path,
    payload: Mapping[str, Any],
    *,
    authority_validator: Callable[[Path], object] | None = None,
    expected_parent_identity: tuple[int, int],
) -> None:
    expected_bytes = _json_bytes(payload)
    with _directory_commit_guard(
        target.parent,
        expected_identity=expected_parent_identity,
    ) as (guard, flush_directory):
        temporary = _write_temporary_bytes(target, expected_bytes)
        try:
            with _held_file_identity(temporary) as temporary_identity:
                if authority_validator is not None:
                    authority_validator(target)
                _replace_in_guard(guard, temporary, target)
                flush_directory()
                _attest_published_bytes(target, expected_bytes, temporary_identity)
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise


def _atomic_publish_bytes(
    target: Path,
    expected_bytes: bytes,
    *,
    expected_parent_identity: tuple[int, int],
) -> None:
    with _directory_commit_guard(
        target.parent,
        expected_identity=expected_parent_identity,
    ) as (guard, flush_directory):
        temporary = _write_temporary_bytes(target, expected_bytes)
        try:
            with _held_file_identity(temporary) as temporary_identity:
                try:
                    _link_in_guard(guard, temporary, target)
                except FileExistsError as exc:
                    raise SourceRegistryError(
                        f"Immutable artifact already exists: {target}"
                    ) from exc
                temporary.unlink(missing_ok=True)
                flush_directory()
                _attest_published_bytes(target, expected_bytes, temporary_identity)
        finally:
            temporary.unlink(missing_ok=True)


def _atomic_publish_json(
    target: Path,
    payload: Mapping[str, Any],
    *,
    expected_parent_identity: tuple[int, int],
) -> None:
    _atomic_publish_bytes(
        target,
        _json_bytes(payload),
        expected_parent_identity=expected_parent_identity,
    )


def _strict_json_load(path: Path) -> Any:
    def reject_constant(value: str) -> None:
        raise SourceRegistryError(f"Non-finite JSON value is forbidden: {value}")

    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise SourceRegistryError(f"Duplicate JSON key is forbidden: {key}")
            result[key] = value
        return result

    requested = Path(os.path.abspath(path.expanduser()))
    try:
        raw, before, after, final = _read_authority_bytes(requested)
        payload = json.loads(
            raw.decode("utf-8"),
            parse_constant=reject_constant,
            object_pairs_hook=reject_duplicate_keys,
        )
        final = os.lstat(requested)
        if _read_registry_authority_bytes(requested) != raw:
            raise SourceRegistryError(
                f"Source registry authority bytes changed during parse: {requested}"
            )
    except (OSError, UnicodeError) as exc:
        raise SourceRegistryError(
            f"Source registry authority read failed safely: {requested}"
        ) from exc
    _require_stable_authority_read(requested, before, after, final)
    return payload


def _read_registry_authority_bytes(path: Path) -> bytes:
    requested = Path(os.path.abspath(path.expanduser()))
    try:
        payload, before, after, final = _read_authority_bytes(requested)
    except OSError as exc:
        raise SourceRegistryError(
            f"Source registry authority read failed safely: {requested}"
        ) from exc
    _require_stable_authority_read(requested, before, after, final)
    return payload


def _read_authority_bytes(
    requested: Path,
) -> tuple[bytes, os.stat_result, os.stat_result, os.stat_result]:
    expected = os.lstat(requested)
    canonical = _canonical_registry_path(requested)
    current = os.lstat(canonical)
    if _authority_stat_identity(expected) != _authority_stat_identity(current):
        raise SourceRegistryError(
            f"Source registry authority identity changed before open: {requested}"
        )
    descriptor = os.open(canonical, _authority_read_flags())
    with os.fdopen(descriptor, "rb") as handle:
        before = os.fstat(handle.fileno())
        if not stat.S_ISREG(before.st_mode):
            raise SourceRegistryError(
                f"Source registry authority is not a regular file: {requested}"
            )
        if _authority_stat_identity(expected) != _authority_stat_identity(before):
            raise SourceRegistryError(
                f"Source registry authority identity changed at open: {requested}"
            )
        payload = handle.read()
        after = os.fstat(handle.fileno())
    final = os.lstat(requested)
    if (expected.st_mtime_ns, expected.st_ctime_ns) != (
        final.st_mtime_ns,
        final.st_ctime_ns,
    ):
        raise SourceRegistryError(
            f"Source registry authority metadata changed during read: {requested}"
        )
    return payload, before, after, final


def _require_stable_authority_read(
    requested: Path,
    before: os.stat_result,
    after: os.stat_result,
    final: os.stat_result,
) -> None:
    identities = {
        _authority_stat_identity(item) for item in (before, after, final)
    }
    if (
        len(identities) != 1
        or any(item.st_nlink != 1 for item in (before, after, final))
        or (before.st_mtime_ns, before.st_ctime_ns)
        != (after.st_mtime_ns, after.st_ctime_ns)
    ):
        raise SourceRegistryError(
            f"Source registry authority identity changed during read: {requested}"
        )


def _authority_read_flags() -> int:
    return (
        os.O_RDONLY
        | getattr(os, "O_BINARY", 0)
        | getattr(os, "O_NOINHERIT", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )


def _authority_stat_identity(attributes: os.stat_result) -> tuple[int, int, int]:
    return attributes.st_dev, attributes.st_ino, attributes.st_size


def _directory_stat_identity(attributes: os.stat_result) -> tuple[int, int]:
    return attributes.st_dev, attributes.st_ino


def _read_registry_revision(path: Path) -> int:
    if not path.exists():
        return 0
    return SourceRegistry.load(path).revision


@contextmanager
def _registry_lock(path: Path, *, timeout_seconds: float = 5.0):
    lock_path = path.with_name(f".{path.name}.lock")
    durable_mkdir_parents(lock_path.parent, mode=0o700)
    with lock_path.open("a+b") as handle:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        deadline = time.monotonic() + timeout_seconds
        while True:
            try:
                _lock_file(handle)
                break
            except OSError as exc:
                if time.monotonic() >= deadline:
                    raise SourceRegistryError("Timed out acquiring source registry process lock.") from exc
                time.sleep(0.01)
        try:
            yield
        finally:
            _unlock_file(handle)


def _lock_file(handle: Any) -> None:
    handle.seek(0)
    if os.name == "nt":
        import msvcrt

        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        return
    import fcntl

    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)


def _unlock_file(handle: Any) -> None:
    handle.seek(0)
    if os.name == "nt":
        import msvcrt

        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        return
    import fcntl

    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _default_batch_id(source_id: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{timestamp}-{source_id}"


def _rollback_snapshot_path(rollback_dir: Path, batch_id: str) -> Path:
    if not BATCH_ID_RE.fullmatch(batch_id):
        raise SourceRegistryError(f"Invalid rollback batch id '{batch_id}'.")
    return rollback_dir / f"{batch_id}.source-registry-rollback.json"


def _rollback_consumed_path(rollback_dir: Path, batch_id: str) -> Path:
    if not BATCH_ID_RE.fullmatch(batch_id):
        raise SourceRegistryError(f"Invalid rollback batch id '{batch_id}'.")
    return rollback_dir / f"{batch_id}.source-registry-rollback.consumed.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _validate_replacement_lifecycle(
    current: SourceManifest,
    incoming: SourceManifest,
) -> None:
    if current.status == "deprecated":
        raise SourceRegistryError(
            f"Source '{current.id}' is deprecated and cannot be replaced."
        )
    if incoming.enabled != current.enabled or incoming.status != current.status:
        raise SourceRegistryError(
            "Manifest replacement cannot change enabled/status; use explicit lifecycle commands."
        )
    current_return_status = current.extra.get("return_status_on_disable")
    incoming_return_status = incoming.extra.get("return_status_on_disable")
    if incoming_return_status != current_return_status:
        raise SourceRegistryError(
            "Manifest replacement cannot change the quarantine lifecycle marker."
        )


def _validate_server_owned_policy(
    current: SourceManifest | None,
    incoming: SourceManifest,
) -> None:
    policy_fields = ("source_type", "license", "trust_level", "import_policy")
    if current is not None:
        changed = [
            field_name
            for field_name in policy_fields
            if getattr(current, field_name) != getattr(incoming, field_name)
        ]
        if changed:
            raise SourceRegistryError(
                "Source manifest cannot change server-owned policy fields: "
                + ", ".join(changed)
            )
        return

    expected_license = (
        "admin-provided" if incoming.source_type == "local_import" else "source-specific"
    )
    expected = {
        "license": expected_license,
        "trust_level": "experimental_unverified",
        "import_policy": "reference_only",
    }
    mismatched = [
        field_name
        for field_name, expected_value in expected.items()
        if getattr(incoming, field_name) != expected_value
    ]
    if mismatched or incoming.enabled or incoming.status != "disabled":
        raise SourceRegistryError(
            "New source manifests must use the server-owned least-privilege onboarding policy "
            f"{expected!r}, enabled=False, status='disabled'."
        )


def _canonical_registry_path(path: Path) -> Path:
    absolute = Path(os.path.abspath(path.expanduser()))
    try:
        initial = os.lstat(absolute)
    except FileNotFoundError:
        initial = None
    except OSError as exc:
        raise SourceRegistryError(
            f"Source registry path cannot be inspected safely: {absolute}"
        ) from exc
    components = list(reversed(absolute.parents)) + [absolute]
    for component in components:
        try:
            attributes = os.lstat(component)
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise SourceRegistryError(
                f"Source registry path cannot be inspected safely: {absolute}"
            ) from exc
        if component.is_symlink() or bool(
            getattr(attributes, "st_file_attributes", 0) & 0x400
        ):
            raise SourceRegistryError(
                f"Source registry path must not contain symlinks or reparse points: {absolute}"
            )
    try:
        resolved = absolute.resolve(strict=absolute.exists())
    except OSError as exc:
        raise SourceRegistryError(
            f"Source registry path cannot be resolved safely: {absolute}"
        ) from exc
    if os.path.normcase(str(resolved)) != os.path.normcase(str(absolute)):
        raise SourceRegistryError(
            f"Source registry authority resolved away from its expected path: {absolute}"
        )
    if absolute.exists():
        try:
            final = os.lstat(absolute)
            if initial is None or _authority_stat_identity(initial) != _authority_stat_identity(final):
                raise SourceRegistryError(
                    f"Source registry authority identity changed during path validation: {absolute}"
                )
            if final.st_nlink != 1 or not stat.S_ISREG(final.st_mode):
                raise SourceRegistryError(
                    f"Source registry file must be regular with exactly one hard link: {absolute}"
                )
        except OSError as exc:
            raise SourceRegistryError(
                f"Source registry path cannot be inspected safely: {absolute}"
            ) from exc
    return absolute


def _validate_rollback_history(
    entries: list[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise SourceRegistryError("Source registry rollback_history entries must be objects.")
        if set(entry) != {"batch_id", "snapshot_sha256", "reverted_at"}:
            raise SourceRegistryError("Source registry rollback_history entry fields are invalid.")
        batch_id = entry.get("batch_id")
        snapshot_sha256 = entry.get("snapshot_sha256")
        reverted_at = entry.get("reverted_at")
        if not isinstance(batch_id, str) or not BATCH_ID_RE.fullmatch(batch_id):
            raise SourceRegistryError("Source registry rollback_history batch_id is invalid.")
        if batch_id in seen:
            raise SourceRegistryError("Source registry rollback_history batch_id is duplicated.")
        if not isinstance(snapshot_sha256, str) or not re.fullmatch(
            r"[0-9a-f]{64}", snapshot_sha256
        ):
            raise SourceRegistryError("Source registry rollback_history snapshot hash is invalid.")
        if not isinstance(reverted_at, str) or not reverted_at:
            raise SourceRegistryError("Source registry rollback_history reverted_at is invalid.")
        seen.add(batch_id)
        normalized.append(
            {
                "batch_id": batch_id,
                "snapshot_sha256": snapshot_sha256,
                "reverted_at": reverted_at,
            }
        )
    return normalized


def _validate_source_mapping(data: Mapping[str, Any]) -> None:
    required = ("id", "label", "source_type", "scopes", "enabled", "status")
    missing = [field_name for field_name in required if field_name not in data]
    if missing:
        raise SourceRegistryError(f"Missing required source fields: {', '.join(missing)}")

    for field_name in ("id", "label", "source_type", "status"):
        if not isinstance(data[field_name], str) or not data[field_name].strip():
            raise SourceRegistryError(
                f"Source field '{field_name}' must be a non-empty string."
            )

    optional_string_fields = (
        "description",
        "homepage",
        "endpoint",
        "documentation_url",
        "download_url",
        "local_path",
        "license",
        "trust_level",
        "import_policy",
    )
    for field_name in optional_string_fields:
        if field_name in data and not isinstance(data[field_name], str):
            raise SourceRegistryError(f"Source field '{field_name}' must be a string.")

    source_id = data["id"]
    if not SOURCE_ID_RE.fullmatch(source_id):
        raise SourceRegistryError(f"Invalid source id '{source_id}'.")

    source_type = data["source_type"]
    if source_type not in ALLOWED_SOURCE_TYPES:
        raise SourceRegistryError(f"Invalid source_type '{source_type}'.")

    status = data["status"]
    if status not in ALLOWED_STATUSES:
        raise SourceRegistryError(f"Invalid status '{status}'.")

    scopes = data["scopes"]
    if (
        not isinstance(scopes, list)
        or not scopes
        or not all(isinstance(scope, str) and scope.strip() for scope in scopes)
    ):
        raise SourceRegistryError(
            "Source field 'scopes' must be a non-empty list of non-empty strings."
        )

    warnings = data.get("warnings", [])
    if not isinstance(warnings, list) or not all(
        isinstance(item, str) and item.strip() for item in warnings
    ):
        raise SourceRegistryError("Source field 'warnings' must be a list of strings.")

    enabled = data.get("enabled")
    if not isinstance(enabled, bool):
        raise SourceRegistryError("Source field 'enabled' must be a boolean.")
    if enabled != (status == "active"):
        raise SourceRegistryError(
            "Source enabled/status must be exactly true/active or false/non-active."
        )

    if source_type == "local_import" and not data.get("local_path", "").strip():
        raise SourceRegistryError("local_import sources require local_path.")

    for field_name in ONLINE_URL_FIELDS:
        value = data.get(field_name, "").strip()
        if value and not value.startswith("https://"):
            raise SourceRegistryError(f"Online source URL '{field_name}' must use https.")
