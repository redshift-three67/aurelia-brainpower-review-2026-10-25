"""Read-only F8.1 shadow comparison between Legacy and Admin Catalog.

The comparison is an evidence/reporting layer only. It reads one active Catalog
snapshot, compares it with an explicit legacy snapshot, classifies every
difference, and always leaves the selected runtime source as legacy.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Sequence

from .contracts import CatalogContext, CatalogEntry, EntryType, normalize_catalog_id
from .validation import validate_entries


_DOMAINS = (
    "groups",
    "multiplexes",
    "pathogens",
    "profiles",
    "remedies",
    "remedy_relations",
)
_CLASSIFICATIONS = frozenset({"blocker", "expected", "warning"})


class ShadowComparisonError(ValueError):
    """The F8.1 comparison request violates the closed shadow contract."""


@dataclass(frozen=True, slots=True)
class ShadowRecord:
    record_id: str
    payload: Mapping[str, Any]

    def __post_init__(self) -> None:
        normalize_catalog_id(self.record_id)
        object.__setattr__(self, "payload", MappingProxyType(_canonical_payload(self.payload)))

    def canonical_mapping(self) -> dict[str, Any]:
        return {
            "payload": _plain_json(self.payload),
            "record_id": self.record_id,
        }


@dataclass(frozen=True, slots=True)
class ShadowLegacySnapshot:
    profiles: tuple[ShadowRecord, ...] = ()
    groups: tuple[ShadowRecord, ...] = ()
    remedies: tuple[ShadowRecord, ...] = ()
    pathogens: tuple[ShadowRecord, ...] = ()
    remedy_relations: tuple[ShadowRecord, ...] = ()
    multiplexes: tuple[ShadowRecord, ...] = ()
    records_by_domain: Mapping[str, Mapping[str, ShadowRecord]] = field(init=False)
    domain_counts: Mapping[str, int] = field(init=False)
    sha256: str = field(init=False)

    def __post_init__(self) -> None:
        indexed = {
            "groups": _index_records(self.groups, "groups"),
            "multiplexes": _index_records(self.multiplexes, "multiplexes"),
            "pathogens": _index_records(self.pathogens, "pathogens"),
            "profiles": _index_records(self.profiles, "profiles"),
            "remedies": _index_records(self.remedies, "remedies"),
            "remedy_relations": _index_records(
                self.remedy_relations,
                "remedy_relations",
            ),
        }
        object.__setattr__(
            self,
            "records_by_domain",
            MappingProxyType(
                {
                    domain: MappingProxyType(records)
                    for domain, records in indexed.items()
                }
            ),
        )
        object.__setattr__(
            self,
            "domain_counts",
            MappingProxyType(
                {domain: len(indexed[domain]) for domain in _DOMAINS}
            ),
        )
        object.__setattr__(self, "sha256", _canonical_sha256(self.canonical_mapping()))

    @classmethod
    def from_records(
        cls,
        *,
        profiles: Iterable[ShadowRecord] = (),
        groups: Iterable[ShadowRecord] = (),
        remedies: Iterable[ShadowRecord] = (),
        pathogens: Iterable[ShadowRecord] = (),
        remedy_relations: Iterable[ShadowRecord] = (),
        multiplexes: Iterable[ShadowRecord] = (),
    ) -> "ShadowLegacySnapshot":
        return cls(
            profiles=tuple(profiles),
            groups=tuple(groups),
            remedies=tuple(remedies),
            pathogens=tuple(pathogens),
            remedy_relations=tuple(remedy_relations),
            multiplexes=tuple(multiplexes),
        )

    def canonical_mapping(self) -> dict[str, Any]:
        return {
            domain: [
                record.canonical_mapping()
                for record in sorted(
                    self.records_by_domain[domain].values(),
                    key=lambda item: item.record_id,
                )
            ]
            for domain in _DOMAINS
        }


@dataclass(frozen=True, slots=True)
class ShadowDiffExpectation:
    domain: str
    record_id: str
    kind: str
    fields: tuple[str, ...] = ()
    classification: str = "expected"
    reason: str = ""

    def __post_init__(self) -> None:
        if self.domain not in _DOMAINS:
            raise ShadowComparisonError(f"unknown shadow domain: {self.domain!r}")
        normalize_catalog_id(self.record_id)
        if self.kind not in {"catalog_only", "changed", "legacy_only"}:
            raise ShadowComparisonError(f"unknown shadow diff kind: {self.kind!r}")
        if self.classification not in _CLASSIFICATIONS:
            raise ShadowComparisonError(
                f"unknown shadow classification: {self.classification!r}"
            )
        if any(not isinstance(field, str) or not field for field in self.fields):
            raise ShadowComparisonError("shadow expectation fields must be text")
        if not self.reason.strip():
            raise ShadowComparisonError("shadow expectation reason must be non-empty")
        object.__setattr__(self, "fields", tuple(sorted(set(self.fields))))

    @property
    def key(self) -> tuple[str, str, str, tuple[str, ...]]:
        return (self.domain, self.record_id, self.kind, self.fields)


@dataclass(frozen=True, slots=True)
class ShadowDifference:
    domain: str
    record_id: str
    kind: str
    fields: tuple[str, ...]
    classification: str
    reason: str
    legacy_sha256: str | None = None
    catalog_sha256: str | None = None


@dataclass(frozen=True, slots=True)
class ShadowComparisonIssue:
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class ShadowComparisonReport:
    mode: str
    selected_source: str
    legacy_snapshot_sha256: str
    active_revision_id: str | None
    differences: tuple[ShadowDifference, ...]
    errors: tuple[ShadowComparisonIssue, ...]
    expectations: tuple[ShadowDiffExpectation, ...]
    summary: Mapping[str, int]
    used_legacy_fallback: bool
    no_publish: bool = True
    no_activate: bool = True
    productive_runtime_effect: bool = False


def compare_catalog_shadow_to_legacy(
    store: Any,
    context: CatalogContext,
    legacy_snapshot: ShadowLegacySnapshot,
    *,
    expectations: Sequence[ShadowDiffExpectation] = (),
) -> ShadowComparisonReport:
    if not isinstance(context, CatalogContext):
        raise ShadowComparisonError("context must be CatalogContext")
    if not isinstance(legacy_snapshot, ShadowLegacySnapshot):
        raise ShadowComparisonError("legacy_snapshot must be ShadowLegacySnapshot")
    normalized_expectations = tuple(expectations)
    expectation_index = _expectation_index(normalized_expectations)

    try:
        snapshot = store.current_revision_snapshot(context)
    except Exception:
        return _error_report(
            legacy_snapshot,
            normalized_expectations,
            active_revision_id=None,
            code="catalog_read_failed",
            message="active catalog snapshot could not be read",
        )
    if snapshot is None:
        return _error_report(
            legacy_snapshot,
            normalized_expectations,
            active_revision_id=None,
            code="active_revision_missing",
            message="no active catalog revision exists in the requested context",
        )
    active_revision_id, entries = snapshot
    try:
        if any(entry.context != context for entry in entries):
            raise ShadowComparisonError("active catalog revision has a foreign context")
        validation = validate_entries(entries)
        if not validation.is_valid:
            raise ShadowComparisonError("active catalog revision has invalid references")
        catalog_records = _catalog_shadow_records(entries)
    except Exception:
        return _error_report(
            legacy_snapshot,
            normalized_expectations,
            active_revision_id=str(active_revision_id),
            code="active_revision_invalid",
            message="active catalog revision failed validation",
        )

    differences = _diff_snapshots(
        legacy_snapshot.records_by_domain,
        catalog_records.records_by_domain,
        expectation_index,
    )
    return ShadowComparisonReport(
        mode="shadow_compare",
        selected_source="legacy",
        legacy_snapshot_sha256=legacy_snapshot.sha256,
        active_revision_id=str(active_revision_id),
        differences=differences,
        errors=(),
        expectations=normalized_expectations,
        summary=MappingProxyType(_summary(differences)),
        used_legacy_fallback=False,
    )


def legacy_shadow_snapshot_from_exports(
    *,
    profiles: Any,
    remedies: Any,
    multiplexes: Any,
) -> ShadowLegacySnapshot:
    profile_records = [
        ShadowRecord(
            profile.name,
            {
                "aliases": tuple(profile.aliases),
                "category": profile.category,
                "enabled": profile.enabled,
                "group_ids": tuple(profile.groups),
                "label": profile.display_name,
                "level": profile.level,
            },
        )
        for profile in profiles.profiles
    ]
    group_records = [
        ShadowRecord(group_id, {"label": group_id})
        for group_id in profiles.referenced_groups
    ]
    remedy_records = [
        ShadowRecord(remedy.catalog_id, {"label": remedy.name})
        for remedy in remedies.remedies
    ]
    pathogen_records = [
        ShadowRecord(pathogen.catalog_id, {"label": pathogen.name})
        for pathogen in remedies.pathogens
    ]
    relation_records = [
        ShadowRecord(
            relation.catalog_id,
            {
                "enabled": True,
                "pathogen_id": relation.pathogen_catalog_id,
                "priority": relation.priority,
                "relation_type": relation.relation_type,
                "remedy_id": relation.remedy_catalog_id,
            },
        )
        for relation in remedies.relations
    ]
    multiplex_records = [
        ShadowRecord(
            multiplex.name,
            {
                "explicit_remedy_group": multiplex.explicit_remedy_group,
                "heuristic_remedy_group": multiplex.heuristic_remedy_group,
                "labels": tuple(multiplex.labels),
                "label_source": multiplex.label_source,
            },
        )
        for multiplex in multiplexes.runtime_multiplexes
    ]
    return ShadowLegacySnapshot.from_records(
        profiles=profile_records,
        groups=group_records,
        remedies=remedy_records,
        pathogens=pathogen_records,
        remedy_relations=relation_records,
        multiplexes=multiplex_records,
    )


def _catalog_shadow_records(entries: Sequence[CatalogEntry]) -> ShadowLegacySnapshot:
    records: dict[str, list[ShadowRecord]] = {domain: [] for domain in _DOMAINS}
    for entry in entries:
        if entry.entry_type is EntryType.PROFILE:
            if entry.data.get("enabled", True) is not True:
                continue
            if entry.data.get("tombstoned", False) is True:
                continue
            records["profiles"].append(
                ShadowRecord(
                    entry.entry_id,
                    {
                        "aliases": tuple(entry.data.get("aliases", ())),
                        "category": entry.data.get("category", ""),
                        "enabled": entry.data.get("enabled", True),
                        "group_ids": tuple(entry.data["group_ids"]),
                        "label": entry.data["label"],
                        "level": entry.data.get("level", 2),
                    },
                )
            )
        elif entry.entry_type is EntryType.GROUP:
            if entry.data.get("enabled", True) is True:
                records["groups"].append(
                    ShadowRecord(entry.entry_id, {"label": entry.data["label"]})
                )
        elif entry.entry_type is EntryType.REMEDY:
            if entry.data.get("enabled", True) is True:
                records["remedies"].append(
                    ShadowRecord(entry.entry_id, {"label": entry.data["label"]})
                )
        elif entry.entry_type is EntryType.PATHOGEN:
            if entry.data.get("enabled", True) is True:
                records["pathogens"].append(
                    ShadowRecord(entry.entry_id, {"label": entry.data["label"]})
                )
        elif entry.entry_type is EntryType.RELATION:
            if entry.data.get("enabled", True) is True:
                records["remedy_relations"].append(
                    ShadowRecord(
                        entry.entry_id,
                        {
                            "enabled": entry.data.get("enabled", True),
                            "pathogen_id": entry.data["pathogen_id"],
                            "priority": entry.data["priority"],
                            "relation_type": entry.data["relation_type"],
                            "remedy_id": entry.data["remedy_id"],
                        },
                    )
                )
        elif entry.entry_type is EntryType.MULTIPLEX:
            if entry.data.get("enabled", True) is True:
                records["multiplexes"].append(
                    ShadowRecord(
                        entry.entry_id,
                        {
                            "enabled": entry.data.get("enabled", True),
                            "group_ids": tuple(entry.data["group_ids"]),
                            "label": entry.data["label"],
                            "remedy_ids": tuple(entry.data["remedy_ids"]),
                        },
                    )
                )
    return ShadowLegacySnapshot.from_records(
        profiles=records["profiles"],
        groups=records["groups"],
        remedies=records["remedies"],
        pathogens=records["pathogens"],
        remedy_relations=records["remedy_relations"],
        multiplexes=records["multiplexes"],
    )


def _diff_snapshots(
    legacy: Mapping[str, Mapping[str, ShadowRecord]],
    catalog: Mapping[str, Mapping[str, ShadowRecord]],
    expectations: Mapping[tuple[str, str, str, tuple[str, ...]], ShadowDiffExpectation],
) -> tuple[ShadowDifference, ...]:
    differences: list[ShadowDifference] = []
    for domain in _DOMAINS:
        legacy_records = legacy[domain]
        catalog_records = catalog[domain]
        for record_id in sorted(legacy_records.keys() | catalog_records.keys()):
            if record_id not in legacy_records:
                differences.append(
                    _classified_difference(
                        domain=domain,
                        record_id=record_id,
                        kind="catalog_only",
                        fields=(),
                        legacy_record=None,
                        catalog_record=catalog_records[record_id],
                        expectations=expectations,
                    )
                )
                continue
            if record_id not in catalog_records:
                differences.append(
                    _classified_difference(
                        domain=domain,
                        record_id=record_id,
                        kind="legacy_only",
                        fields=(),
                        legacy_record=legacy_records[record_id],
                        catalog_record=None,
                        expectations=expectations,
                    )
                )
                continue
            legacy_payload = legacy_records[record_id].payload
            catalog_payload = catalog_records[record_id].payload
            changed_fields = tuple(
                field
                for field in sorted(set(legacy_payload) | set(catalog_payload))
                if legacy_payload.get(field) != catalog_payload.get(field)
            )
            if changed_fields:
                differences.append(
                    _classified_difference(
                        domain=domain,
                        record_id=record_id,
                        kind="changed",
                        fields=changed_fields,
                        legacy_record=legacy_records[record_id],
                        catalog_record=catalog_records[record_id],
                        expectations=expectations,
                    )
                )
    return tuple(differences)


def _classified_difference(
    *,
    domain: str,
    record_id: str,
    kind: str,
    fields: tuple[str, ...],
    legacy_record: ShadowRecord | None,
    catalog_record: ShadowRecord | None,
    expectations: Mapping[tuple[str, str, str, tuple[str, ...]], ShadowDiffExpectation],
) -> ShadowDifference:
    key = (domain, record_id, kind, fields)
    expectation = expectations.get(key)
    classification = "blocker"
    reason = "unclassified F8.1 shadow difference"
    if expectation is not None:
        classification = expectation.classification
        reason = expectation.reason
    return ShadowDifference(
        domain=domain,
        record_id=record_id,
        kind=kind,
        fields=fields,
        classification=classification,
        reason=reason,
        legacy_sha256=(
            None
            if legacy_record is None
            else _canonical_sha256(legacy_record.canonical_mapping())
        ),
        catalog_sha256=(
            None
            if catalog_record is None
            else _canonical_sha256(catalog_record.canonical_mapping())
        ),
    )


def _expectation_index(
    expectations: Sequence[ShadowDiffExpectation],
) -> dict[tuple[str, str, str, tuple[str, ...]], ShadowDiffExpectation]:
    indexed: dict[tuple[str, str, str, tuple[str, ...]], ShadowDiffExpectation] = {}
    for expectation in expectations:
        if expectation.key in indexed:
            raise ShadowComparisonError("duplicate shadow diff expectation")
        indexed[expectation.key] = expectation
    return indexed


def _error_report(
    legacy_snapshot: ShadowLegacySnapshot,
    expectations: tuple[ShadowDiffExpectation, ...],
    *,
    active_revision_id: str | None,
    code: str,
    message: str,
) -> ShadowComparisonReport:
    return ShadowComparisonReport(
        mode="shadow_compare",
        selected_source="legacy",
        legacy_snapshot_sha256=legacy_snapshot.sha256,
        active_revision_id=active_revision_id,
        differences=(),
        errors=(ShadowComparisonIssue(code, message),),
        expectations=expectations,
        summary=MappingProxyType({"blocker": 1, "expected": 0, "warning": 0}),
        used_legacy_fallback=True,
    )


def _summary(differences: Sequence[ShadowDifference]) -> dict[str, int]:
    counts = {"blocker": 0, "expected": 0, "warning": 0}
    for difference in differences:
        counts[difference.classification] += 1
    return counts


def _index_records(records: Iterable[ShadowRecord], domain: str) -> dict[str, ShadowRecord]:
    indexed: dict[str, ShadowRecord] = {}
    for record in records:
        if not isinstance(record, ShadowRecord):
            raise ShadowComparisonError(f"{domain} records must be ShadowRecord")
        normalized_id = normalize_catalog_id(record.record_id)
        if normalized_id in indexed:
            raise ShadowComparisonError(f"{domain} contains duplicate normalized ids")
        indexed[normalized_id] = record
    return indexed


def _canonical_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise ShadowComparisonError("shadow payload must be a mapping")
    return {str(key): _freeze_value(value) for key, value in sorted(payload.items())}


def _freeze_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {str(key): _freeze_value(nested) for key, nested in sorted(value.items())}
        )
    if isinstance(value, list):
        return tuple(_freeze_value(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze_value(item) for item in value)
    if value is None or isinstance(value, (str, int, bool)):
        return value
    raise ShadowComparisonError("shadow payload contains non-canonical data")


def _plain_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _plain_json(nested) for key, nested in value.items()}
    if isinstance(value, tuple):
        return [_plain_json(item) for item in value]
    return value


def _canonical_sha256(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        _plain_json(payload),
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


__all__ = [
    "ShadowComparisonError",
    "ShadowComparisonIssue",
    "ShadowComparisonReport",
    "ShadowDiffExpectation",
    "ShadowDifference",
    "ShadowLegacySnapshot",
    "ShadowRecord",
    "compare_catalog_shadow_to_legacy",
    "legacy_shadow_snapshot_from_exports",
]
