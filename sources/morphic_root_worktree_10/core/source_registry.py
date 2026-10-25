"""Validated source repository registry for optional external data sources."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_REGISTRY_PATH = PROJECT_ROOT / "config" / "source_repositories.json"

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
        _validate_source_mapping(data)

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
            id=str(data["id"]),
            label=str(data["label"]),
            description=str(data.get("description", "")),
            source_type=str(data["source_type"]),
            scopes=tuple(str(scope) for scope in data["scopes"]),
            enabled=bool(data.get("enabled", False)),
            status=str(data["status"]),
            homepage=str(data.get("homepage", "")),
            endpoint=str(data.get("endpoint", "")),
            documentation_url=str(data.get("documentation_url", "")),
            download_url=str(data.get("download_url", "")),
            local_path=str(data.get("local_path", "")),
            license=str(data.get("license", "")),
            trust_level=str(data.get("trust_level", "")),
            import_policy=str(data.get("import_policy", "manual")),
            warnings=tuple(str(item) for item in data.get("warnings", []) or []),
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
    def __init__(self, path: Path, sources: Iterable[SourceManifest], schema_version: int = 1):
        self.path = Path(path)
        self.schema_version = schema_version
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
        payload = json.loads(registry_path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            schema_version = 1
            raw_sources = payload
        elif isinstance(payload, dict):
            schema_version = int(payload.get("schema_version", 1))
            raw_sources = payload.get("sources", [])
        else:
            raise SourceRegistryError("Source registry must be a JSON object or list.")
        if not isinstance(raw_sources, list):
            raise SourceRegistryError("Source registry field 'sources' must be a list.")

        sources = [SourceManifest.from_mapping(item) for item in raw_sources]
        ids = [source.id for source in sources]
        if len(ids) != len(set(ids)):
            raise SourceRegistryError("Duplicate source ids are not allowed.")
        return cls(registry_path, sources, schema_version=schema_version)

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
        self.save()
        return updated

    def disable_source(self, source_id: str) -> SourceManifest:
        source = self.get(source_id)
        status = (
            "quarantined"
            if source.status == "quarantined" or source.extra.get("return_status_on_disable") == "quarantined"
            else "disabled"
        )
        updated = source.with_state(enabled=False, status=status)
        self._sources[source_id] = updated
        self.save()
        return updated

    def plan_import_manifest(self, manifest_path: Path | str, *, replace: bool = False) -> SourceImportPlan:
        source = _load_source_manifest(manifest_path)
        current = self._sources.get(source.id)
        if current is not None and not replace:
            raise SourceRegistryError(f"Source '{source.id}' already exists. Use replace=True to overwrite.")

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
    ) -> Path:
        plan = self.plan_import_manifest(manifest_path, replace=replace)
        target_dir = Path(staging_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        staged_path = target_dir / f"{plan.source.id}.source.json"
        payload = {"schema_version": 1, "source": plan.source.to_mapping()}
        staged_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return staged_path

    def import_manifest(
        self,
        manifest_path: Path | str,
        *,
        replace: bool = False,
        rollback_dir: Path | str | None = None,
        batch_id: str | None = None,
    ) -> SourceManifest:
        plan = self.plan_import_manifest(manifest_path, replace=replace)
        if rollback_dir is not None:
            self._write_rollback_snapshot(Path(rollback_dir), batch_id or _default_batch_id(plan.source.id), plan)

        source = plan.source
        self._sources[source.id] = source
        self.save()
        return source

    def rollback_import(self, batch_id: str, *, rollback_dir: Path | str) -> None:
        snapshot_path = _rollback_snapshot_path(Path(rollback_dir), batch_id)
        if not snapshot_path.exists():
            raise SourceRegistryError(f"Rollback batch not found: {batch_id}")
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        if snapshot.get("batch_id") != batch_id:
            raise SourceRegistryError(f"Rollback batch id mismatch in {snapshot_path}")
        previous = snapshot.get("previous_registry")
        if not isinstance(previous, dict):
            raise SourceRegistryError("Rollback snapshot is missing previous_registry.")
        raw_sources = previous.get("sources", [])
        if not isinstance(raw_sources, list):
            raise SourceRegistryError("Rollback snapshot field 'sources' must be a list.")

        restored = [SourceManifest.from_mapping(item) for item in raw_sources]
        self.schema_version = int(previous.get("schema_version", 1))
        self._sources = {source.id: source for source in restored}
        self.save()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = self._to_payload()
        self.path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def _to_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "sources": [source.to_mapping() for source in self.list_sources()],
        }

    def _write_rollback_snapshot(
        self,
        rollback_dir: Path,
        batch_id: str,
        plan: SourceImportPlan,
    ) -> Path:
        if not BATCH_ID_RE.fullmatch(batch_id):
            raise SourceRegistryError(f"Invalid rollback batch id '{batch_id}'.")
        rollback_dir.mkdir(parents=True, exist_ok=True)
        snapshot_path = _rollback_snapshot_path(rollback_dir, batch_id)
        if snapshot_path.exists():
            raise SourceRegistryError(f"Rollback batch already exists: {batch_id}")
        snapshot = {
            "schema_version": 1,
            "batch_id": batch_id,
            "registry_path": str(self.path),
            "source_id": plan.source.id,
            "action": plan.action,
            "changed_fields": plan.changed_fields,
            "previous_registry": self._to_payload(),
        }
        snapshot_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return snapshot_path


def validate_manifest(data: Mapping[str, Any]) -> SourceManifest:
    return SourceManifest.from_mapping(data)


def _load_source_manifest(manifest_path: Path | str) -> SourceManifest:
    path = Path(manifest_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and "source" in payload:
        payload = payload["source"]
    if not isinstance(payload, dict):
        raise SourceRegistryError("Import manifest must contain one source object.")
    return SourceManifest.from_mapping(payload)


def _default_batch_id(source_id: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{timestamp}-{source_id}"


def _rollback_snapshot_path(rollback_dir: Path, batch_id: str) -> Path:
    if not BATCH_ID_RE.fullmatch(batch_id):
        raise SourceRegistryError(f"Invalid rollback batch id '{batch_id}'.")
    return rollback_dir / f"{batch_id}.source-registry-rollback.json"


def _validate_source_mapping(data: Mapping[str, Any]) -> None:
    required = ("id", "label", "source_type", "scopes", "enabled", "status")
    missing = [field_name for field_name in required if field_name not in data]
    if missing:
        raise SourceRegistryError(f"Missing required source fields: {', '.join(missing)}")

    source_id = str(data["id"])
    if not SOURCE_ID_RE.fullmatch(source_id):
        raise SourceRegistryError(f"Invalid source id '{source_id}'.")

    source_type = str(data["source_type"])
    if source_type not in ALLOWED_SOURCE_TYPES:
        raise SourceRegistryError(f"Invalid source_type '{source_type}'.")

    status = str(data["status"])
    if status not in ALLOWED_STATUSES:
        raise SourceRegistryError(f"Invalid status '{status}'.")

    scopes = data["scopes"]
    if not isinstance(scopes, list) or not scopes or not all(str(scope).strip() for scope in scopes):
        raise SourceRegistryError("Source field 'scopes' must be a non-empty list.")

    if bool(data.get("enabled", False)) and status != "active":
        raise SourceRegistryError("Enabled sources must have status 'active'.")

    if source_type == "local_import" and not str(data.get("local_path", "")).strip():
        raise SourceRegistryError("local_import sources require local_path.")

    for field_name in ONLINE_URL_FIELDS:
        value = str(data.get(field_name, "") or "").strip()
        if value and not value.startswith("https://"):
            raise SourceRegistryError(f"Online source URL '{field_name}' must use https.")
