"""Read-only inventory of the distinct legacy multiplex authorities for F4.2."""

from __future__ import annotations

import ast
import hashlib
import json
import os
import stat
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import BinaryIO, Iterator, Mapping

from core.remedy_group_registry import EXPLICIT_REMEDY_GROUPS, is_remedy_group
from core.subgroups import procedural_groups

from .legacy_remedy_adapter import LegacyRemedyExport, export_legacy_remedies


_EXPORT_SCHEMA_VERSION = 1
_SOURCE_STATUS = "legacy_unprovenanced"
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_CUSTOM_CONFIG = _PROJECT_ROOT / "config" / "groups_config.json"
_DEFAULT_BAT_SOURCE = _PROJECT_ROOT / "core" / "bat_report_aggregator.py"
_MAX_BOUND_SOURCE_BYTES = 1_048_576
_EXPECTED_BAT_SOURCE_SHA256 = "6b6b9f2536bd838dfe26455460082fae3b1f513e077f7b015623b545e558b6a5"
_EXPECTED_BAT_MATCHER_SHA256 = "a41964d281421cb9f39416220691b0cfed288dd83c5c4ad01ca3bfd28f602c25"

_CUSTOM_CONFIG_FIELDS = frozenset(
    {
        "custom_groups",
        "custom_multiplexes",
        "group_descriptions",
        "last_modified",
        "version",
    }
)
_CUSTOM_GROUP_FIELDS = frozenset({"labels", "description", "created", "type"})
_CUSTOM_MULTIPLEX_FIELDS = frozenset(
    {"groups", "description", "k_total", "focus_areas", "created", "type"}
)
_DYNAMIC_MULTIPLEX_CATEGORIES = {
    "heel_remedies_multiplex": "homotoxikologie_heel",
    "nutramedix_remedies_multiplex": "phytotherapie_nutramedix",
    "oorep_homeopathy_multiplex": "oorep_homeopathy_multiplex",
    "schuessler_remedies_multiplex": "Kohärente Harmonisierung mit Schüssler-Salzen",
}


class LegacyMultiplexAdapterError(ValueError):
    """A legacy multiplex authority violates the closed F4.2 inventory contract."""


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _required_text(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("expected non-empty text")
    return value


def _text_sequence(value: object, *, non_empty: bool = False) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise ValueError("expected a text list")
    if non_empty and not value:
        raise ValueError("expected a non-empty text list")
    return tuple(value)


def _reject_duplicate_json_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


class _SourceReparsePointError(OSError):
    pass


@contextmanager
def _open_binary_nofollow(path: Path) -> Iterator[BinaryIO]:
    """Open one regular file without following its final symlink/reparse point."""

    if os.name != "nt":
        flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags)
        try:
            opened = os.fstat(fd)
            if stat.S_ISLNK(opened.st_mode) or not stat.S_ISREG(opened.st_mode):
                raise _SourceReparsePointError("source is not a regular file")
            with os.fdopen(fd, "rb") as handle:
                fd = -1
                yield handle
        finally:
            if fd >= 0:
                os.close(fd)
        return

    import ctypes
    import msvcrt
    from ctypes import wintypes

    class _ByHandleFileInformation(ctypes.Structure):
        _fields_ = [
            ("dwFileAttributes", wintypes.DWORD),
            ("ftCreationTime", wintypes.FILETIME),
            ("ftLastAccessTime", wintypes.FILETIME),
            ("ftLastWriteTime", wintypes.FILETIME),
            ("dwVolumeSerialNumber", wintypes.DWORD),
            ("nFileSizeHigh", wintypes.DWORD),
            ("nFileSizeLow", wintypes.DWORD),
            ("nNumberOfLinks", wintypes.DWORD),
            ("nFileIndexHigh", wintypes.DWORD),
            ("nFileIndexLow", wintypes.DWORD),
        ]

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
    get_information = kernel32.GetFileInformationByHandle
    get_information.argtypes = [wintypes.HANDLE, ctypes.POINTER(_ByHandleFileInformation)]
    get_information.restype = wintypes.BOOL
    close_handle = kernel32.CloseHandle
    close_handle.argtypes = [wintypes.HANDLE]
    close_handle.restype = wintypes.BOOL

    handle = create_file(
        str(path),
        0x80000000,
        0x00000001,
        None,
        3,
        0x00200000 | 0x08000000,
        None,
    )
    invalid_handle = ctypes.c_void_p(-1).value
    if handle == invalid_handle:
        raise ctypes.WinError(ctypes.get_last_error())
    fd = -1
    try:
        information = _ByHandleFileInformation()
        if not get_information(handle, ctypes.byref(information)):
            raise ctypes.WinError(ctypes.get_last_error())
        if information.dwFileAttributes & 0x00000400:
            raise _SourceReparsePointError("source is a reparse point")
        fd = msvcrt.open_osfhandle(
            int(handle),
            os.O_RDONLY | getattr(os, "O_BINARY", 0),
        )
        handle = invalid_handle
        with os.fdopen(fd, "rb") as file_handle:
            fd = -1
            yield file_handle
    finally:
        if fd >= 0:
            os.close(fd)
        elif handle != invalid_handle:
            close_handle(handle)


def _read_bound_bytes(
    path: Path,
    *,
    missing_allowed: bool,
    symlink_error: str,
    max_bytes: int = _MAX_BOUND_SOURCE_BYTES,
) -> tuple[bytes, str] | None:
    opened_once = False
    try:
        with _open_binary_nofollow(path) as handle:
            opened_once = True
            opened = os.fstat(handle.fileno())
            if opened.st_size > max_bytes:
                raise ValueError("source exceeds size limit")
            payload = handle.read(max_bytes + 1)
            handle.seek(0)
            verification_payload = handle.read(max_bytes + 1)
            after_read = os.fstat(handle.fileno())
            with _open_binary_nofollow(path) as current_handle:
                current = os.fstat(current_handle.fileno())
            if not os.path.samestat(opened, after_read) or not os.path.samestat(
                opened, current
            ):
                raise ValueError("source identity changed")
            if (
                len(payload) != opened.st_size
                or verification_payload != payload
                or after_read.st_size != opened.st_size
                or after_read.st_mtime_ns != opened.st_mtime_ns
            ):
                raise ValueError("source content changed")
            return payload, _sha256_bytes(payload)
    except _SourceReparsePointError:
        raise LegacyMultiplexAdapterError(symlink_error) from None
    except FileNotFoundError:
        if missing_allowed and not opened_once and not os.path.lexists(path):
            return None
        raise


@dataclass(frozen=True, slots=True)
class LegacyRuntimeMultiplex:
    name: str
    labels: tuple[str, ...]
    label_source: str
    explicit_remedy_group: bool
    heuristic_remedy_group: bool
    scan_effect: str = "active_runtime"
    source_status: str = _SOURCE_STATUS


@dataclass(frozen=True, slots=True)
class LegacyExplicitRemedyGroup:
    name: str
    runtime_available: bool
    runtime_multiplex: bool
    source_status: str = _SOURCE_STATUS


@dataclass(frozen=True, slots=True)
class LegacyRelationModel:
    model_type: str
    relation_count: int
    relation_catalog_ids: tuple[str, ...]
    remedy_export_sha256: str
    scan_effect: str = "not_consumed_by_scan"
    source_status: str = _SOURCE_STATUS


@dataclass(frozen=True, slots=True)
class LegacyCustomMultiplex:
    name: str
    groups: tuple[str, ...]
    description: str
    k_total: int
    focus_areas: tuple[str, ...]
    created: str
    type: str
    listed_in_groups_overview: bool = True
    scan_effect: str = "no_runtime_effect"
    source_status: str = _SOURCE_STATUS


@dataclass(frozen=True, slots=True)
class LegacyCustomGroup:
    name: str
    labels: tuple[str, ...]
    description: str
    created: str
    type: str
    source_status: str = _SOURCE_STATUS


@dataclass(frozen=True, slots=True)
class LegacyCustomConfig:
    configured: bool
    source_sha256: str | None
    version: str | None
    last_modified: str | None
    custom_groups: tuple[LegacyCustomGroup, ...]
    group_descriptions: tuple[tuple[str, str], ...]
    multiplexes: tuple[LegacyCustomMultiplex, ...]
    scan_effect: str = "no_runtime_effect"
    source_status: str = _SOURCE_STATUS

    @property
    def custom_group_names(self) -> tuple[str, ...]:
        return tuple(group.name for group in self.custom_groups)


@dataclass(frozen=True, slots=True)
class LegacyBatKeywordFallback:
    keyword: str
    remedies: tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class LegacyBatFallback:
    keyword_entries: tuple[LegacyBatKeywordFallback, ...]
    default_remedies: tuple[tuple[str, str], ...]
    source_sha256: str
    matcher_sha256: str
    authoritative: bool = False
    scan_effect: str = "fallback_only"
    source_status: str = _SOURCE_STATUS


@dataclass(frozen=True, slots=True)
class LegacyMultiplexConflict:
    conflict_type: str
    subject: str
    reference: str


@dataclass(frozen=True, slots=True)
class LegacyMultiplexExport:
    schema_version: int
    authority: str
    source_status: str
    runtime_snapshot_sha256: str
    remedy_registry_snapshot_sha256: str
    runtime_multiplexes: tuple[LegacyRuntimeMultiplex, ...]
    explicit_remedy_groups: tuple[LegacyExplicitRemedyGroup, ...]
    relation_model: LegacyRelationModel
    custom_config: LegacyCustomConfig
    bat_fallback: LegacyBatFallback
    conflicts: tuple[LegacyMultiplexConflict, ...]

    def canonical_json(self) -> str:
        return _canonical_json(asdict(self))

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


def _runtime_authority_snapshot(
) -> tuple[tuple[str, ...], dict[str, tuple[str, ...]], dict[str, bool], str]:
    runtime_names = tuple(procedural_groups.list_groups())
    normalized: dict[str, str] = {}
    for name in runtime_names:
        if not isinstance(name, str) or not name.strip():
            raise LegacyMultiplexAdapterError("legacy runtime group authority is invalid")
        key = name.casefold()
        if key in normalized:
            raise LegacyMultiplexAdapterError("legacy runtime group identity collision")
        normalized[key] = name
    static_labels: dict[str, tuple[str, ...]] = {}
    heuristic_remedy: dict[str, bool] = {}
    for name in sorted(item for item in runtime_names if "multiplex" in item.casefold()):
        heuristic_remedy[name] = is_remedy_group(name)
        if name in _DYNAMIC_MULTIPLEX_CATEGORIES:
            continue
        raw_labels = procedural_groups._GROUP_LABELS.get(name)
        if not isinstance(raw_labels, list) or not all(
            isinstance(label, str) and label.strip() for label in raw_labels
        ):
            raise LegacyMultiplexAdapterError(
                "legacy runtime multiplex labels are invalid"
            )
        static_labels[name] = tuple(raw_labels)
    snapshot_sha256 = hashlib.sha256(
        _canonical_json(
            {
                "runtime_names": runtime_names,
                "static_labels": static_labels,
                "heuristic_remedy": heuristic_remedy,
            }
        ).encode("utf-8")
    ).hexdigest()
    return runtime_names, static_labels, heuristic_remedy, snapshot_sha256


def _runtime_multiplexes(
    remedy_export: LegacyRemedyExport,
    runtime_names: tuple[str, ...],
    static_labels: Mapping[str, tuple[str, ...]],
    heuristic_remedy: Mapping[str, bool],
    explicit_names: frozenset[str],
) -> tuple[tuple[LegacyRuntimeMultiplex, ...], set[str]]:
    runtime_name_set = set(runtime_names)
    remedies_by_category: dict[str, list[str]] = {}
    for remedy in remedy_export.remedies:
        if remedy.category is not None:
            remedies_by_category.setdefault(remedy.category, []).append(remedy.name)

    result: list[LegacyRuntimeMultiplex] = []
    for name in sorted(item for item in runtime_names if "multiplex" in item.casefold()):
        if name in _DYNAMIC_MULTIPLEX_CATEGORIES:
            labels = tuple(
                sorted(remedies_by_category.get(_DYNAMIC_MULTIPLEX_CATEGORIES[name], []))
            )
            label_source = "legacy_remedy_database_category"
        else:
            labels = static_labels[name]
            label_source = "procedural_group_labels"
        if not labels:
            raise LegacyMultiplexAdapterError(
                "legacy runtime multiplex labels are unavailable"
            )
        result.append(
            LegacyRuntimeMultiplex(
                name=name,
                labels=labels,
                label_source=label_source,
                explicit_remedy_group=name in explicit_names,
                heuristic_remedy_group=heuristic_remedy[name],
            )
        )
    return tuple(result), runtime_name_set


def _explicit_remedy_groups(
    runtime_names: set[str],
    explicit_names: tuple[str, ...],
) -> tuple[LegacyExplicitRemedyGroup, ...]:
    normalized: set[str] = set()
    result: list[LegacyExplicitRemedyGroup] = []
    for name in explicit_names:
        if not isinstance(name, str) or not name.strip() or name.casefold() in normalized:
            raise LegacyMultiplexAdapterError("legacy explicit remedy authority is invalid")
        normalized.add(name.casefold())
        result.append(
            LegacyExplicitRemedyGroup(
                name=name,
                runtime_available=name in runtime_names,
                runtime_multiplex="multiplex" in name.casefold(),
            )
        )
    return tuple(result)


def _relation_model(remedy_export: LegacyRemedyExport) -> LegacyRelationModel:
    relation_ids = tuple(relation.catalog_id for relation in remedy_export.relations)
    if len(set(item.casefold() for item in relation_ids)) != len(relation_ids):
        raise LegacyMultiplexAdapterError("legacy relation identity collision")
    return LegacyRelationModel(
        model_type="remedy_pathogen_relation",
        relation_count=len(relation_ids),
        relation_catalog_ids=relation_ids,
        remedy_export_sha256=remedy_export.sha256,
    )


def _custom_config(
    path: Path,
    runtime_names: set[str],
) -> tuple[LegacyCustomConfig, tuple[LegacyMultiplexConflict, ...]]:
    try:
        bound = _read_bound_bytes(
            path,
            missing_allowed=True,
            symlink_error="legacy custom multiplex config must not be a symlink",
        )
        if bound is None:
            return (
                LegacyCustomConfig(
                    configured=False,
                    source_sha256=None,
                    version=None,
                    last_modified=None,
                    custom_groups=(),
                    group_descriptions=(),
                    multiplexes=(),
                ),
                (),
            )
        payload, source_sha256 = bound
        parsed = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_json_keys,
        )
        if not isinstance(parsed, dict) or frozenset(parsed) != _CUSTOM_CONFIG_FIELDS:
            raise ValueError("invalid top-level config")
        if parsed["version"] != "1.0":
            raise ValueError("unsupported config version")
        version = _required_text(parsed["version"])
        last_modified = _required_text(parsed["last_modified"])
        groups = parsed["custom_groups"]
        multiplexes = parsed["custom_multiplexes"]
        descriptions = parsed["group_descriptions"]
        if not isinstance(groups, dict) or not isinstance(multiplexes, dict):
            raise ValueError("invalid custom mappings")
        if not isinstance(descriptions, dict) or not all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in descriptions.items()
        ):
            raise ValueError("invalid group descriptions")

        custom_groups: list[LegacyCustomGroup] = []
        custom_group_norms: dict[str, str] = {}
        conflicts: list[LegacyMultiplexConflict] = []
        runtime_by_norm = {name.casefold(): name for name in runtime_names}
        for name, value in sorted(groups.items()):
            name = _required_text(name)
            if not isinstance(value, dict) or frozenset(value) != _CUSTOM_GROUP_FIELDS:
                raise ValueError("invalid custom group")
            labels = _text_sequence(value["labels"], non_empty=True)
            if not isinstance(value["description"], str):
                raise ValueError("invalid custom group description")
            created = _required_text(value["created"])
            if value["type"] != "custom":
                raise ValueError("invalid custom group type")
            norm = name.casefold()
            if norm in custom_group_norms:
                conflicts.append(
                    LegacyMultiplexConflict(
                        conflict_type="custom_group_casefold_collision",
                        subject=name,
                        reference=custom_group_norms[norm],
                    )
                )
            else:
                custom_group_norms[norm] = name
            if norm in runtime_by_norm:
                conflicts.append(
                    LegacyMultiplexConflict(
                        conflict_type="custom_group_name_collision",
                        subject=name,
                        reference=runtime_by_norm[norm],
                    )
                )
            custom_groups.append(
                LegacyCustomGroup(
                    name=name,
                    labels=labels,
                    description=value["description"],
                    created=created,
                    type=value["type"],
                )
            )

        result: list[LegacyCustomMultiplex] = []
        custom_multiplex_norms: dict[str, str] = {}
        custom_group_names = {group.name for group in custom_groups}
        available_references = runtime_names.union(custom_group_names)
        known_by_norm: dict[str, list[str]] = {}
        for known_name in sorted(runtime_names) + sorted(custom_group_names):
            known_by_norm.setdefault(known_name.casefold(), []).append(known_name)
        description_norms: dict[str, str] = {}
        for description_name in sorted(descriptions):
            norm = description_name.casefold()
            candidates = tuple(known_by_norm.get(norm, ()))
            if norm in description_norms:
                conflicts.append(
                    LegacyMultiplexConflict(
                        conflict_type="group_description_casefold_collision",
                        subject=description_name,
                        reference=description_norms[norm],
                    )
                )
            else:
                description_norms[norm] = description_name
            if description_name not in available_references:
                conflicts.append(
                    LegacyMultiplexConflict(
                        conflict_type=(
                            "group_description_case_mismatch"
                            if candidates
                            else "unknown_group_description_reference"
                        ),
                        subject=description_name,
                        reference=candidates[0] if candidates else description_name,
                    )
                )
            if len(candidates) > 1:
                conflicts.append(
                    LegacyMultiplexConflict(
                        conflict_type="ambiguous_group_description_reference",
                        subject=description_name,
                        reference="|".join(candidates),
                    )
                )
        for name, value in sorted(multiplexes.items()):
            name = _required_text(name)
            if not isinstance(value, dict) or frozenset(value) != _CUSTOM_MULTIPLEX_FIELDS:
                raise ValueError("invalid custom multiplex")
            groups_value = _text_sequence(value["groups"], non_empty=True)
            if not isinstance(value["description"], str):
                raise ValueError("invalid custom multiplex description")
            k_total = value["k_total"]
            if isinstance(k_total, bool) or not isinstance(k_total, int) or k_total < 1:
                raise ValueError("invalid k_total")
            focus_areas = _text_sequence(value["focus_areas"])
            created = _required_text(value["created"])
            if value["type"] != "custom":
                raise ValueError("invalid custom multiplex type")

            norm = name.casefold()
            runtime_collision = runtime_by_norm.get(norm)
            if runtime_collision is not None:
                conflicts.append(
                    LegacyMultiplexConflict(
                        conflict_type="custom_name_collision",
                        subject=name,
                        reference=runtime_collision,
                    )
                )
            if norm in custom_multiplex_norms:
                conflicts.append(
                    LegacyMultiplexConflict(
                        conflict_type="custom_casefold_collision",
                        subject=name,
                        reference=custom_multiplex_norms[norm],
                    )
                )
            if norm not in custom_multiplex_norms:
                custom_multiplex_norms[norm] = name
            custom_group_collision = custom_group_norms.get(norm)
            if custom_group_collision is not None:
                conflicts.append(
                    LegacyMultiplexConflict(
                        conflict_type="custom_group_multiplex_collision",
                        subject=name,
                        reference=custom_group_collision,
                    )
                )
            if len(set(groups_value)) != len(groups_value):
                conflicts.append(
                    LegacyMultiplexConflict(
                        conflict_type="duplicate_group_reference",
                        subject=name,
                        reference=name,
                    )
                )
            for reference in groups_value:
                if reference not in available_references:
                    conflicts.append(
                        LegacyMultiplexConflict(
                            conflict_type="unknown_group_reference",
                            subject=name,
                            reference=reference,
                        )
                    )
            result.append(
                LegacyCustomMultiplex(
                    name=name,
                    groups=groups_value,
                    description=value["description"],
                    k_total=k_total,
                    focus_areas=focus_areas,
                    created=created,
                    type=value["type"],
                )
            )
        return (
            LegacyCustomConfig(
                configured=True,
                source_sha256=source_sha256,
                version=version,
                last_modified=last_modified,
                custom_groups=tuple(custom_groups),
                group_descriptions=tuple(sorted(descriptions.items())),
                multiplexes=tuple(result),
            ),
            tuple(
                sorted(
                    conflicts,
                    key=lambda item: (
                        item.conflict_type,
                        item.subject,
                        item.reference,
                    ),
                )
            ),
        )
    except LegacyMultiplexAdapterError:
        raise
    except (
        MemoryError,
        OSError,
        RecursionError,
        TypeError,
        UnicodeError,
        ValueError,
        json.JSONDecodeError,
    ):
        raise LegacyMultiplexAdapterError(
            "legacy custom multiplex config is invalid"
        ) from None


def _validated_remedy_pairs(value: object) -> tuple[tuple[str, str], ...]:
    if not isinstance(value, (list, tuple)) or not value:
        raise ValueError("invalid remedy pairs")
    result: list[tuple[str, str]] = []
    for pair in value:
        if (
            not isinstance(pair, (list, tuple))
            or len(pair) != 2
            or not all(isinstance(item, str) and item.strip() for item in pair)
        ):
            raise ValueError("invalid remedy pair")
        result.append((pair[0], pair[1]))
    return tuple(result)


def _validate_bat_authority_shape(
    tree: ast.Module,
    mapping_node: ast.expr,
    matcher_node: ast.FunctionDef,
) -> None:
    allowed_top_level = (ast.Expr, ast.Import, ast.ImportFrom, ast.FunctionDef, ast.Assign)
    if any(not isinstance(node, allowed_top_level) for node in tree.body):
        raise ValueError("ambiguous BAT top-level source shape")
    for node in tree.body:
        if isinstance(node, ast.Expr) and not (
            isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)
        ):
            raise ValueError("executable BAT top-level expression")
        if isinstance(node, ast.Assign) and node.value is not mapping_node:
            raise ValueError("additional BAT top-level assignment")
        if isinstance(node, ast.FunctionDef):
            defaults = [*node.args.defaults, *[item for item in node.args.kw_defaults if item]]
            if node.decorator_list or any(
                not isinstance(default, ast.Constant) for default in defaults
            ):
                raise ValueError("executable BAT function declaration")

    mapping_stores = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
        and node.id == "BAT_REMEDY_MAP"
        and isinstance(node.ctx, (ast.Store, ast.Del))
    ]
    if len(mapping_stores) != 1:
        raise ValueError("ambiguous BAT map writes")
    nested_mapping_mutations = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.Subscript, ast.Attribute))
        and isinstance(node.ctx, (ast.Store, ast.Del))
        and isinstance(node.value, ast.Name)
        and node.value.id == "BAT_REMEDY_MAP"
    ]
    mutating_mapping_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "BAT_REMEDY_MAP"
        and node.func.attr not in {"get", "items", "keys", "values", "copy"}
    ]
    dangerous_dynamic_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id
        in {"__import__", "compile", "delattr", "eval", "exec", "globals", "locals", "setattr"}
    ]
    if nested_mapping_mutations or mutating_mapping_calls or dangerous_dynamic_calls:
        raise ValueError("dynamic BAT authority mutation")

    matcher_definitions = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        and node.name == "find_remedies_for_group"
    ]
    if matcher_definitions != [matcher_node]:
        raise ValueError("ambiguous BAT matcher definitions")
    matcher_name_writes = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
        and node.id == "find_remedies_for_group"
        and isinstance(node.ctx, (ast.Store, ast.Del))
    ]
    imported_names = [
        alias
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
        if (alias.asname or alias.name.rsplit(".", 1)[-1])
        in {"BAT_REMEDY_MAP", "find_remedies_for_group"}
    ]
    if matcher_name_writes or imported_names:
        raise ValueError("ambiguous BAT authority rebinding")


def _bat_fallback(path: Path) -> LegacyBatFallback:
    try:
        bound = _read_bound_bytes(
            path,
            missing_allowed=False,
            symlink_error="legacy BAT fallback source must not be a symlink",
        )
        assert bound is not None
        payload, source_sha256 = bound
        if source_sha256 != _EXPECTED_BAT_SOURCE_SHA256:
            raise ValueError("unexpected BAT authority snapshot")
        text = payload.decode("utf-8")
        tree = ast.parse(text, filename="legacy_bat_fallback.py")
        mapping_nodes: list[ast.expr] = []
        matcher_nodes: list[ast.FunctionDef] = []
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "BAT_REMEDY_MAP"
                for target in node.targets
            ):
                mapping_nodes.append(node.value)
            elif isinstance(node, ast.FunctionDef) and node.name == "find_remedies_for_group":
                matcher_nodes.append(node)
        if len(mapping_nodes) != 1 or len(matcher_nodes) != 1:
            raise ValueError("required BAT declarations missing")
        mapping_node = mapping_nodes[0]
        matcher_node = matcher_nodes[0]
        _validate_bat_authority_shape(tree, mapping_node, matcher_node)
        if not isinstance(mapping_node, ast.Dict):
            raise ValueError("BAT map must be a literal mapping")
        literal_keywords = [ast.literal_eval(key) for key in mapping_node.keys]
        if len(literal_keywords) != len(set(literal_keywords)):
            raise ValueError("duplicate BAT keyword")
        mapping = ast.literal_eval(mapping_node)
        if not isinstance(mapping, dict) or not mapping:
            raise ValueError("invalid BAT map")
        entries: list[LegacyBatKeywordFallback] = []
        for keyword, remedies in sorted(mapping.items()):
            entries.append(
                LegacyBatKeywordFallback(
                    keyword=_required_text(keyword),
                    remedies=_validated_remedy_pairs(remedies),
                )
            )
        if not matcher_node.body or not isinstance(matcher_node.body[-1], ast.Return):
            raise ValueError("BAT default fallback missing")
        final_value = matcher_node.body[-1].value
        if (
            not isinstance(final_value, ast.Subscript)
            or not isinstance(final_value.value, ast.List)
            or not isinstance(final_value.slice, ast.Slice)
            or final_value.slice.lower is not None
            or final_value.slice.step is not None
            or not isinstance(final_value.slice.upper, ast.Name)
            or final_value.slice.upper.id != "max_remedies"
        ):
            raise ValueError("BAT default fallback invalid")
        default_remedies = _validated_remedy_pairs(ast.literal_eval(final_value.value))
        matcher_source = ast.get_source_segment(text, matcher_node)
        if matcher_source is None:
            raise ValueError("BAT matcher source missing")
        matcher_sha256 = hashlib.sha256(matcher_source.encode("utf-8")).hexdigest()
        if matcher_sha256 != _EXPECTED_BAT_MATCHER_SHA256:
            raise ValueError("unexpected BAT matcher snapshot")
        return LegacyBatFallback(
            keyword_entries=tuple(entries),
            default_remedies=default_remedies,
            source_sha256=source_sha256,
            matcher_sha256=matcher_sha256,
        )
    except (
        MemoryError,
        OSError,
        RecursionError,
        SyntaxError,
        TypeError,
        UnicodeError,
        ValueError,
    ):
        raise LegacyMultiplexAdapterError(
            "legacy BAT fallback source is invalid"
        ) from None


def export_legacy_multiplexes(
    remedy_database_path: Path,
    *,
    custom_config_path: Path | None = None,
    bat_source_path: Path | None = None,
) -> LegacyMultiplexExport:
    """Return a deterministic null-mutating inventory of all legacy multiplex models."""

    remedy_export = export_legacy_remedies(Path(remedy_database_path))
    explicit_names_snapshot = tuple(sorted(EXPLICIT_REMEDY_GROUPS))
    explicit_name_set = frozenset(explicit_names_snapshot)
    remedy_registry_snapshot_sha256 = hashlib.sha256(
        _canonical_json(explicit_names_snapshot).encode("utf-8")
    ).hexdigest()
    (
        runtime_names_snapshot,
        static_labels_snapshot,
        heuristic_snapshot,
        runtime_snapshot_sha256,
    ) = _runtime_authority_snapshot()
    runtime_multiplexes, runtime_names = _runtime_multiplexes(
        remedy_export,
        runtime_names_snapshot,
        static_labels_snapshot,
        heuristic_snapshot,
        explicit_name_set,
    )
    explicit_groups = _explicit_remedy_groups(runtime_names, explicit_names_snapshot)
    custom_config, conflicts = _custom_config(
        Path(custom_config_path) if custom_config_path is not None else _DEFAULT_CUSTOM_CONFIG,
        runtime_names,
    )
    bat_fallback = _bat_fallback(
        Path(bat_source_path) if bat_source_path is not None else _DEFAULT_BAT_SOURCE
    )
    if _runtime_authority_snapshot()[3] != runtime_snapshot_sha256:
        raise LegacyMultiplexAdapterError(
            "legacy runtime group authority changed during export"
        )
    if tuple(sorted(EXPLICIT_REMEDY_GROUPS)) != explicit_names_snapshot:
        raise LegacyMultiplexAdapterError(
            "legacy explicit remedy authority changed during export"
        )
    return LegacyMultiplexExport(
        schema_version=_EXPORT_SCHEMA_VERSION,
        authority="legacy_multiplex_authorities",
        source_status=_SOURCE_STATUS,
        runtime_snapshot_sha256=runtime_snapshot_sha256,
        remedy_registry_snapshot_sha256=remedy_registry_snapshot_sha256,
        runtime_multiplexes=runtime_multiplexes,
        explicit_remedy_groups=explicit_groups,
        relation_model=_relation_model(remedy_export),
        custom_config=custom_config,
        bat_fallback=bat_fallback,
        conflicts=conflicts,
    )


__all__ = [
    "LegacyBatFallback",
    "LegacyBatKeywordFallback",
    "LegacyCustomConfig",
    "LegacyCustomGroup",
    "LegacyCustomMultiplex",
    "LegacyExplicitRemedyGroup",
    "LegacyMultiplexAdapterError",
    "LegacyMultiplexConflict",
    "LegacyMultiplexExport",
    "LegacyRelationModel",
    "LegacyRuntimeMultiplex",
    "export_legacy_multiplexes",
]
