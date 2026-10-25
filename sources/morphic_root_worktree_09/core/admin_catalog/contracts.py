"""Strikte, runtime-unabhaengige Vertraege fuer den Admin-Catalog."""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping


class ContractError(ValueError):
    """Ein Catalog-Datensatz verletzt den geschlossenen F1-Vertrag."""


class EntryType(str, Enum):
    PROFILE = "profile"
    GROUP = "group"
    REMEDY = "remedy"
    PATHOGEN = "pathogen"
    MULTIPLEX = "multiplex"
    TERMINOLOGY = "terminology"
    RELATION = "relation"


class RelationType(str, Enum):
    REMEDY_PATHOGEN = "remedy_pathogen"


_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._@-]{0,127}$")
_ALLOWED_SCOPES = frozenset({"operator", "workspace", "tenant", "system"})
_PII_FIELDS = frozenset(
    {
        "address",
        "birth_date",
        "dob",
        "email",
        "patient_id",
        "patient_name",
        "person_name",
        "phone",
    }
)
_COMMON_FIELDS = frozenset({"aliases", "description", "enabled", "label", "terminology_ids"})
_ALLOWED_FIELDS: dict[EntryType, frozenset[str]] = {
    EntryType.PROFILE: _COMMON_FIELDS
    | {"category", "group_ids", "level", "tombstoned"},
    EntryType.GROUP: _COMMON_FIELDS,
    EntryType.REMEDY: _COMMON_FIELDS | {"tombstoned"},
    EntryType.PATHOGEN: _COMMON_FIELDS,
    EntryType.MULTIPLEX: _COMMON_FIELDS
    | {"group_ids", "remedy_ids", "tombstoned"},
    EntryType.TERMINOLOGY: frozenset(
        {
            "aliases",
            "code",
            "enabled",
            "label",
            "scheme",
            "target_entry_id",
            "target_entry_type",
        }
    ),
    EntryType.RELATION: frozenset(
        {"enabled", "pathogen_id", "priority", "relation_type", "remedy_id"}
    ),
}
_REQUIRED_FIELDS: dict[EntryType, frozenset[str]] = {
    EntryType.PROFILE: frozenset({"group_ids", "label"}),
    EntryType.GROUP: frozenset({"label"}),
    EntryType.REMEDY: frozenset({"label"}),
    EntryType.PATHOGEN: frozenset({"label"}),
    EntryType.MULTIPLEX: frozenset({"group_ids", "label", "remedy_ids"}),
    EntryType.TERMINOLOGY: frozenset(
        {"code", "label", "scheme", "target_entry_id", "target_entry_type"}
    ),
    EntryType.RELATION: frozenset(
        {"pathogen_id", "priority", "relation_type", "remedy_id"}
    ),
}
_LIST_ID_FIELDS = frozenset({"aliases", "group_ids", "remedy_ids", "terminology_ids"})
_SINGLE_ID_FIELDS = frozenset({"pathogen_id", "remedy_id", "target_entry_id"})
_TEXT_FIELDS = frozenset({"category", "code", "description", "label", "scheme"})


def _require_identifier(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not _ID_PATTERN.fullmatch(value):
        raise ContractError(f"{field_name} is not a stable identifier")
    return value


def normalize_catalog_id(value: str) -> str:
    """Return the deterministic collision key for an already valid identifier."""

    return _require_identifier(value, "identifier").casefold()


def _assert_no_pii(value: object) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if isinstance(key, str) and key.casefold() in _PII_FIELDS:
                raise ContractError(f"PII field is forbidden: {key}")
            _assert_no_pii(nested)
    elif isinstance(value, (list, tuple)):
        for nested in value:
            _assert_no_pii(nested)


def _freeze_json(value: object, field_name: str) -> object:
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ContractError(f"{field_name} contains a non-finite float")
        return value
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, list):
        return tuple(_freeze_json(item, field_name) for item in value)
    if isinstance(value, Mapping):
        frozen: dict[str, object] = {}
        for key, nested in value.items():
            if not isinstance(key, str):
                raise ContractError(f"{field_name} contains a non-string key")
            frozen[key] = _freeze_json(nested, field_name)
        return MappingProxyType(frozen)
    raise ContractError(f"{field_name} contains a non-JSON or executable payload")


def _plain_json(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _plain_json(nested) for key, nested in value.items()}
    if isinstance(value, tuple):
        return [_plain_json(nested) for nested in value]
    return value


@dataclass(frozen=True)
class CatalogContext:
    operator_id: str
    workspace_id: str
    tenant_id: str
    scope: str

    def __post_init__(self) -> None:
        _require_identifier(self.operator_id, "operator_id")
        _require_identifier(self.workspace_id, "workspace_id")
        _require_identifier(self.tenant_id, "tenant_id")
        if self.scope not in _ALLOWED_SCOPES:
            raise ContractError(f"unknown scope: {self.scope!r}")

    def canonical_mapping(self) -> dict[str, str]:
        return {
            "operator_id": self.operator_id,
            "scope": self.scope,
            "tenant_id": self.tenant_id,
            "workspace_id": self.workspace_id,
        }


@dataclass(frozen=True)
class CatalogEntry:
    entry_type: EntryType
    entry_id: str
    context: CatalogContext
    source_id: str
    provenance: str
    data: Mapping[str, object]

    def __post_init__(self) -> None:
        try:
            entry_type = EntryType(self.entry_type)
        except (TypeError, ValueError) as exc:
            raise ContractError(f"unknown entry type: {self.entry_type!r}") from exc
        object.__setattr__(self, "entry_type", entry_type)
        _require_identifier(self.entry_id, "entry_id")
        _require_identifier(self.source_id, "source_id")
        if not isinstance(self.provenance, str) or not self.provenance.strip():
            raise ContractError("provenance must be non-empty text")
        if not isinstance(self.context, CatalogContext):
            raise ContractError("context must be CatalogContext")
        if not isinstance(self.data, Mapping):
            raise ContractError("data must be a mapping")

        raw_data = dict(self.data)
        _assert_no_pii(raw_data)
        unknown = sorted(set(raw_data) - _ALLOWED_FIELDS[entry_type])
        if unknown:
            raise ContractError(f"unknown fields for {entry_type.value}: {unknown}")
        missing = sorted(_REQUIRED_FIELDS[entry_type] - set(raw_data))
        if missing:
            raise ContractError(f"missing fields for {entry_type.value}: {missing}")

        normalized: dict[str, object] = {}
        for field_name, value in raw_data.items():
            if field_name in _LIST_ID_FIELDS:
                if not isinstance(value, list):
                    raise ContractError(f"{field_name} must be a list")
                normalized[field_name] = tuple(
                    _require_identifier(item, field_name) for item in value
                )
            elif field_name in _SINGLE_ID_FIELDS:
                normalized[field_name] = _require_identifier(value, field_name)
            elif field_name in _TEXT_FIELDS:
                if not isinstance(value, str) or not value.strip():
                    raise ContractError(f"{field_name} must be non-empty text")
                normalized[field_name] = value
            elif field_name == "enabled":
                if not isinstance(value, bool):
                    raise ContractError("enabled must be boolean")
                normalized[field_name] = value
            elif field_name == "tombstoned":
                if not isinstance(value, bool):
                    raise ContractError("tombstoned must be boolean")
                normalized[field_name] = value
            elif field_name == "level":
                if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                    raise ContractError("level must be a positive integer")
                normalized[field_name] = value
            elif field_name == "priority":
                if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                    raise ContractError("priority must be a non-negative integer")
                normalized[field_name] = value
            elif field_name == "relation_type":
                try:
                    normalized[field_name] = RelationType(value).value
                except (TypeError, ValueError) as exc:
                    raise ContractError(f"unknown relation_type: {value!r}") from exc
            elif field_name == "target_entry_type":
                try:
                    normalized[field_name] = EntryType(value).value
                except (TypeError, ValueError) as exc:
                    raise ContractError(f"unknown target_entry_type: {value!r}") from exc
            else:
                normalized[field_name] = _freeze_json(value, field_name)

        if (
            entry_type in {EntryType.PROFILE, EntryType.REMEDY, EntryType.MULTIPLEX}
            and normalized.get("tombstoned", False) is True
            and normalized.get("enabled", True) is not False
        ):
            raise ContractError(f"tombstoned {entry_type.value} must be disabled")

        object.__setattr__(self, "data", MappingProxyType(normalized))

    def canonical_mapping(self) -> dict[str, object]:
        return {
            "context": self.context.canonical_mapping(),
            "data": _plain_json(self.data),
            "entry_id": self.entry_id,
            "entry_type": self.entry_type.value,
            "provenance": self.provenance,
            "source_id": self.source_id,
        }

    def canonical_json(self) -> str:
        return json.dumps(
            self.canonical_mapping(),
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )

    @property
    def payload_hash(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


__all__ = [
    "CatalogContext",
    "CatalogEntry",
    "ContractError",
    "EntryType",
    "RelationType",
    "normalize_catalog_id",
]
