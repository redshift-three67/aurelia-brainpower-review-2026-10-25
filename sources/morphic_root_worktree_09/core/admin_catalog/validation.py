"""Deterministische Cross-Reference-Validierung fuer Admin-Catalog F1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from .contracts import CatalogEntry, EntryType, normalize_catalog_id


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    entry_id: str
    field: str
    target_id: str | None
    message: str

    def sort_key(self) -> tuple[str, str, str, str, str]:
        return (
            normalize_catalog_id(self.entry_id),
            self.field,
            "" if self.target_id is None else normalize_catalog_id(self.target_id),
            self.code,
            self.message,
        )


@dataclass(frozen=True)
class ValidationResult:
    errors: tuple[ValidationIssue, ...]
    warnings: tuple[ValidationIssue, ...]

    @property
    def is_valid(self) -> bool:
        return not self.errors


def _issue(
    code: str,
    entry: CatalogEntry,
    field: str,
    target_id: str | None,
    message: str,
) -> ValidationIssue:
    return ValidationIssue(
        code=code,
        entry_id=entry.entry_id,
        field=field,
        target_id=target_id,
        message=message,
    )


def _enabled(entry: CatalogEntry) -> bool:
    return bool(entry.data.get("enabled", True))


def _alias_cycle_nodes(graph: dict[str, set[str]]) -> set[str]:
    cycle_nodes: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []
    in_stack: set[str] = set()

    def visit(node: str) -> None:
        if node in visited:
            return
        visited.add(node)
        stack.append(node)
        in_stack.add(node)
        for target in sorted(graph.get(node, ())):
            if target not in visited:
                visit(target)
            elif target in in_stack:
                start = stack.index(target)
                cycle_nodes.update(stack[start:])
        stack.pop()
        in_stack.remove(node)

    for node in sorted(graph):
        visit(node)
    return cycle_nodes


def _entry_sort_key(entry: CatalogEntry) -> tuple[str, str, str]:
    return (
        normalize_catalog_id(entry.entry_id),
        entry.entry_type.value,
        entry.canonical_json(),
    )


def validate_entries(
    entries: Sequence[CatalogEntry] | Iterable[CatalogEntry],
    *,
    allow_disabled_targets: bool = False,
    allow_empty_targets: bool = False,
) -> ValidationResult:
    """Validate one context-bound candidate snapshot without mutating it."""

    ordered = sorted(tuple(entries), key=_entry_sort_key)
    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []
    if not ordered:
        return ValidationResult(errors=(), warnings=())

    expected_context = ordered[0].context
    for entry in ordered:
        if entry.context != expected_context:
            errors.append(
                _issue(
                    "mixed_context",
                    entry,
                    "context",
                    None,
                    "entry belongs to a different operator/workspace/tenant/scope",
                )
            )

    by_normalized_id: dict[str, list[CatalogEntry]] = {}
    for entry in ordered:
        by_normalized_id.setdefault(normalize_catalog_id(entry.entry_id), []).append(entry)
    for collision_key, colliding in sorted(by_normalized_id.items()):
        if len(colliding) > 1:
            owner = sorted(colliding, key=_entry_sort_key)[0]
            errors.append(
                _issue(
                    "normalized_id_collision",
                    owner,
                    "entry_id",
                    collision_key,
                    "multiple entry IDs normalize to the same identifier",
                )
            )

    canonical: dict[str, CatalogEntry] = {
        key: sorted(values, key=_entry_sort_key)[0]
        for key, values in by_normalized_id.items()
    }

    aliases: dict[str, list[CatalogEntry]] = {}
    alias_graph: dict[str, set[str]] = {}
    for entry in ordered:
        owner_id = normalize_catalog_id(entry.entry_id)
        for alias in entry.data.get("aliases", ()):
            alias_id = normalize_catalog_id(str(alias))
            aliases.setdefault(alias_id, []).append(entry)
            if alias_id in canonical:
                canonical_target = canonical[alias_id]
                if canonical_target is not entry:
                    errors.append(
                        _issue(
                            "alias_canonical_collision",
                            entry,
                            "aliases",
                            canonical_target.entry_id,
                            "alias shadows another canonical entry ID",
                        )
                    )
                alias_graph.setdefault(owner_id, set()).add(alias_id)
    for alias_id, owners in sorted(aliases.items()):
        if len(owners) > 1:
            owner = sorted(owners, key=_entry_sort_key)[0]
            errors.append(
                _issue(
                    "duplicate_alias",
                    owner,
                    "aliases",
                    alias_id,
                    "alias is declared more than once",
                )
            )
    cycle_nodes = _alias_cycle_nodes(alias_graph)
    if cycle_nodes:
        owner_id = sorted(cycle_nodes)[0]
        owner = canonical[owner_id]
        errors.append(
            _issue(
                "alias_cycle",
                owner,
                "aliases",
                owner_id,
                "aliases form a cycle through canonical entry IDs",
            )
        )

    def check_reference(
        entry: CatalogEntry,
        field: str,
        target_id: str,
        expected_type: EntryType,
    ) -> None:
        target = canonical.get(normalize_catalog_id(target_id))
        if target is None:
            errors.append(
                _issue(
                    "unknown_reference",
                    entry,
                    field,
                    target_id,
                    f"reference target does not exist as {expected_type.value}",
                )
            )
            return
        if target.context != entry.context:
            errors.append(
                _issue(
                    "cross_context_reference",
                    entry,
                    field,
                    target_id,
                    "reference target belongs to another catalog context",
                )
            )
            return
        if target.entry_type is not expected_type:
            errors.append(
                _issue(
                    "wrong_reference_type",
                    entry,
                    field,
                    target_id,
                    f"expected {expected_type.value}, found {target.entry_type.value}",
                )
            )
            return
        if not _enabled(target):
            if allow_disabled_targets:
                warnings.append(
                    _issue(
                        "disabled_reference_allowed",
                        entry,
                        field,
                        target_id,
                        "disabled reference target explicitly allowed",
                    )
                )
            else:
                errors.append(
                    _issue(
                        "disabled_reference",
                        entry,
                        field,
                        target_id,
                        "reference target is disabled",
                    )
                )

    for entry in ordered:
        if entry.data.get("tombstoned", False) is True:
            continue
        for target_id in entry.data.get("terminology_ids", ()):
            check_reference(
                entry,
                "terminology_ids",
                str(target_id),
                EntryType.TERMINOLOGY,
            )
        if entry.entry_type is EntryType.PROFILE:
            group_ids = tuple(entry.data["group_ids"])
            if not group_ids:
                destination = warnings if allow_empty_targets else errors
                destination.append(
                    _issue(
                        (
                            "empty_references_allowed"
                            if allow_empty_targets
                            else "empty_references"
                        ),
                        entry,
                        "group_ids",
                        None,
                        "profile has no group references",
                    )
                )
            for target_id in group_ids:
                check_reference(entry, "group_ids", str(target_id), EntryType.GROUP)
        elif entry.entry_type is EntryType.MULTIPLEX:
            group_ids = tuple(entry.data["group_ids"])
            remedy_ids = tuple(entry.data["remedy_ids"])
            if not group_ids and not remedy_ids:
                destination = warnings if allow_empty_targets else errors
                destination.append(
                    _issue(
                        (
                            "empty_references_allowed"
                            if allow_empty_targets
                            else "empty_references"
                        ),
                        entry,
                        "group_ids/remedy_ids",
                        None,
                        "multiplex has no group or remedy references",
                    )
                )
            for target_id in group_ids:
                check_reference(entry, "group_ids", str(target_id), EntryType.GROUP)
            for target_id in remedy_ids:
                check_reference(entry, "remedy_ids", str(target_id), EntryType.REMEDY)
        elif entry.entry_type is EntryType.RELATION:
            check_reference(
                entry,
                "remedy_id",
                str(entry.data["remedy_id"]),
                EntryType.REMEDY,
            )
            check_reference(
                entry,
                "pathogen_id",
                str(entry.data["pathogen_id"]),
                EntryType.PATHOGEN,
            )
        elif entry.entry_type is EntryType.TERMINOLOGY:
            check_reference(
                entry,
                "target_entry_id",
                str(entry.data["target_entry_id"]),
                EntryType(str(entry.data["target_entry_type"])),
            )

    return ValidationResult(
        errors=tuple(sorted(errors, key=ValidationIssue.sort_key)),
        warnings=tuple(sorted(warnings, key=ValidationIssue.sort_key)),
    )


__all__ = ["ValidationIssue", "ValidationResult", "validate_entries"]
