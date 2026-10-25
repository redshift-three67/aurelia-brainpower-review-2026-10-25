"""Pure, deterministic normalization of staged source records into Catalog contracts."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

from .contracts import (
    CatalogContext,
    CatalogEntry,
    ContractError,
    EntryType,
    normalize_catalog_id,
)


_HTML_PATTERN = re.compile(r"<\s*/?\s*[A-Za-z][^>]*>")
_SCRIPT_SCHEME_PATTERN = re.compile(
    r"(?:javascript\s*:|data\s*:\s*text/html)", re.IGNORECASE
)
_EXECUTABLE_PATTERN = re.compile(
    r"(?:^|[\s\"'=:/\\])[^\s\"'<>]*\.(?:bat|cmd|com|dll|exe|jar|js|msi|ps1|scr|sh|vbs)(?:$|[\s\"'?&#])",
    re.IGNORECASE,
)


class SourceNormalizationError(ValueError):
    """The normalization request itself violates the closed F5.2 contract."""


@dataclass(frozen=True, slots=True)
class NormalizedSourceRecord:
    source_id: str
    source_record_id: str
    entry: CatalogEntry

    def canonical_mapping(self) -> dict[str, object]:
        return {
            "entry": self.entry.canonical_mapping(),
            "source_id": self.source_id,
            "source_record_id": self.source_record_id,
        }


@dataclass(frozen=True, slots=True)
class QuarantinedSourceRecord:
    source_id: str
    source_record_id: str
    reason_codes: tuple[str, ...]
    source_record_sha256: str

    def canonical_mapping(self) -> dict[str, object]:
        return {
            "reason_codes": list(self.reason_codes),
            "source_id": self.source_id,
            "source_record_id": self.source_record_id,
            "source_record_sha256": self.source_record_sha256,
        }


@dataclass(frozen=True, slots=True)
class SourceNormalizationResult:
    normalized: tuple[NormalizedSourceRecord, ...]
    quarantined: tuple[QuarantinedSourceRecord, ...]

    def canonical_mapping(self) -> dict[str, object]:
        return {
            "normalized": [item.canonical_mapping() for item in self.normalized],
            "quarantined": [item.canonical_mapping() for item in self.quarantined],
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
    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


def _record_sha256(record: Mapping[str, object]) -> str:
    encoded = json.dumps(
        record,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _quarantined(
    source_id: str,
    source_record_id: str,
    record: Mapping[str, object],
    *reason_codes: str,
) -> QuarantinedSourceRecord:
    return QuarantinedSourceRecord(
        source_id=source_id,
        source_record_id=source_record_id,
        reason_codes=tuple(sorted(set(reason_codes))),
        source_record_sha256=_record_sha256(record),
    )


def _contains_forbidden_payload(value: object) -> bool:
    if isinstance(value, str):
        return bool(
            _HTML_PATTERN.search(value)
            or _SCRIPT_SCHEME_PATTERN.search(value)
            or _EXECUTABLE_PATTERN.search(value)
        )
    if isinstance(value, Mapping):
        return any(
            _contains_forbidden_payload(key) or _contains_forbidden_payload(nested)
            for key, nested in value.items()
        )
    if isinstance(value, (list, tuple)):
        return any(_contains_forbidden_payload(nested) for nested in value)
    return False


def _references(entry: CatalogEntry) -> tuple[tuple[EntryType, str], ...]:
    references: list[tuple[EntryType, str]] = [
        (EntryType.TERMINOLOGY, str(target_id))
        for target_id in entry.data.get("terminology_ids", ())
    ]
    if entry.entry_type is EntryType.PROFILE:
        references.extend(
            (EntryType.GROUP, str(target_id)) for target_id in entry.data["group_ids"]
        )
    elif entry.entry_type is EntryType.MULTIPLEX:
        references.extend(
            (EntryType.GROUP, str(target_id)) for target_id in entry.data["group_ids"]
        )
        references.extend(
            (EntryType.REMEDY, str(target_id)) for target_id in entry.data["remedy_ids"]
        )
    elif entry.entry_type is EntryType.RELATION:
        references.extend(
            (
                (EntryType.PATHOGEN, str(entry.data["pathogen_id"])),
                (EntryType.REMEDY, str(entry.data["remedy_id"])),
            )
        )
    elif entry.entry_type is EntryType.TERMINOLOGY:
        references.append(
            (
                EntryType(str(entry.data["target_entry_type"])),
                str(entry.data["target_entry_id"]),
            )
        )
    return tuple(references)


def normalize_source_records(
    *,
    source_id: str,
    data_type: str,
    records: Sequence[Mapping[str, object]] | Iterable[Mapping[str, object]],
    context: CatalogContext,
    known_entries: Sequence[CatalogEntry] | Iterable[CatalogEntry] = (),
) -> SourceNormalizationResult:
    """Project one source record type onto its existing closed Catalog schema."""

    if not isinstance(source_id, str) or not source_id.strip():
        raise SourceNormalizationError("source_id must be non-empty text")
    if not isinstance(context, CatalogContext):
        raise SourceNormalizationError("context must be CatalogContext")
    try:
        entry_type = EntryType(data_type)
    except (TypeError, ValueError) as exc:
        raise SourceNormalizationError(f"unsupported source data_type: {data_type!r}") from exc
    known = tuple(known_entries)

    candidates: list[tuple[Mapping[str, object], NormalizedSourceRecord]] = []
    quarantined: list[QuarantinedSourceRecord] = []
    for record in records:
        if not isinstance(record, Mapping):
            raise SourceNormalizationError("source record must be an object")
        source_record_id = record.get("id")
        if not isinstance(source_record_id, str) or not source_record_id.strip():
            raise SourceNormalizationError("source record id must be non-empty text")
        try:
            normalize_catalog_id(source_record_id)
        except ContractError:
            record_hash = _record_sha256(record)
            quarantined.append(
                _quarantined(
                    source_id,
                    f"invalid-record-{record_hash[:16]}",
                    record,
                    "invalid_record_id",
                )
            )
            continue
        if _contains_forbidden_payload(record):
            quarantined.append(
                _quarantined(source_id, source_record_id, record, "forbidden_payload")
            )
            continue
        data = {key: value for key, value in record.items() if key != "id"}
        try:
            entry = CatalogEntry(
                entry_type=entry_type,
                entry_id=source_record_id,
                context=context,
                source_id=source_id,
                provenance=f"source-record:{source_record_id}",
                data=data,
            )
        except ContractError:
            quarantined.append(
                _quarantined(source_id, source_record_id, record, "invalid_claim")
            )
            continue
        candidates.append(
            (
                record,
                NormalizedSourceRecord(
                    source_id=source_id,
                    source_record_id=source_record_id,
                    entry=entry,
                ),
            )
        )

    candidates_by_id: dict[
        str, list[tuple[Mapping[str, object], NormalizedSourceRecord]]
    ] = {}
    for record, candidate in candidates:
        candidates_by_id.setdefault(
            normalize_catalog_id(candidate.entry.entry_id), []
        ).append((record, candidate))
    retained_candidates: list[
        tuple[Mapping[str, object], NormalizedSourceRecord]
    ] = []
    for claimants in candidates_by_id.values():
        if len(claimants) == 1:
            retained_candidates.extend(claimants)
            continue
        quarantined.extend(
            _quarantined(
                source_id,
                candidate.source_record_id,
                record,
                "duplicate_record_id",
            )
            for record, candidate in claimants
        )

    fixed_available = {
        (entry.entry_type, normalize_catalog_id(entry.entry_id))
        for entry in known
        if entry.context == context
    }
    pending = list(retained_candidates)
    while pending:
        available = fixed_available | {
            (candidate.entry.entry_type, normalize_catalog_id(candidate.entry.entry_id))
            for _, candidate in pending
        }
        invalid = [
            (record, candidate)
            for record, candidate in pending
            if any(
                (target_type, normalize_catalog_id(target_id)) not in available
                for target_type, target_id in _references(candidate.entry)
            )
        ]
        if not invalid:
            break
        invalid_ids = {id(candidate) for _, candidate in invalid}
        quarantined.extend(
            _quarantined(
                source_id,
                candidate.source_record_id,
                record,
                "unknown_reference",
            )
            for record, candidate in invalid
        )
        pending = [
            (record, candidate)
            for record, candidate in pending
            if id(candidate) not in invalid_ids
        ]
    normalized = [candidate for _, candidate in pending]

    return SourceNormalizationResult(
        normalized=tuple(
            sorted(
                normalized,
                key=lambda item: (
                    item.entry.entry_type.value,
                    normalize_catalog_id(item.entry.entry_id),
                    item.entry.canonical_json(),
                    item.source_record_id,
                ),
            )
        ),
        quarantined=tuple(
            sorted(
                quarantined,
                key=lambda item: (
                    normalize_catalog_id(item.source_record_id),
                    item.source_record_id,
                    item.reason_codes,
                    item.source_record_sha256,
                ),
            )
        ),
    )


__all__ = [
    "NormalizedSourceRecord",
    "QuarantinedSourceRecord",
    "SourceNormalizationError",
    "SourceNormalizationResult",
    "normalize_source_records",
]
