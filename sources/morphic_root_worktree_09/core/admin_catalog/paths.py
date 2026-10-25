"""Fail-closed external path policy for the offline Admin Catalog.

The helpers in this module only resolve and validate paths.  They do not create
folders, open a database, or wire the catalog into runtime, web, CLI, or network
paths.
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
from pathlib import Path
from typing import Iterable

from .contracts import CatalogContext


ADMIN_CATALOG_ENV = "MORPHIC_ADMIN_CATALOG_DIR"
CATALOG_DATABASE_FILENAME = "catalog.sqlite3"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
_WINDOWS_REPARSE_ATTRIBUTE = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
_ARCHIVE_ROOT_NAMES = (
    "Benutzer_Archive",
    "Benutzer_Archive_Start",
    "Benutzer_Deutung_Start",
    "Benutzer_Remedies_Start",
    "Benutzer_Synergy_Start",
    "Benutzer_Trends_Start",
)


def _default_blocked_roots(project_root: Path) -> tuple[Path, ...]:
    roots = [project_root / name for name in _ARCHIVE_ROOT_NAMES]
    if os.name == "nt" and project_root.anchor:
        drive_root = Path(project_root.anchor)
        roots.extend(drive_root / name for name in _ARCHIVE_ROOT_NAMES)
    parallel_export = os.getenv("MORPHIC_PARALLEL_EXPORT_ROOT", "").strip()
    if parallel_export:
        configured = Path(parallel_export).expanduser()
        if not configured.is_absolute():
            raise ValueError("configured export/archive root must be absolute")
        if _contains_parent_traversal(configured):
            raise ValueError("configured export/archive root must not contain path traversal")
        if _has_reparse_component(configured):
            raise ValueError("configured export/archive root must not use a reparse point")
        roots.append(configured)
    return tuple(roots)


def _contains_parent_traversal(path: Path) -> bool:
    return any(part == ".." for part in path.parts)


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _overlaps(first: Path, second: Path) -> bool:
    return _is_within(first, second) or _is_within(second, first)


def _uses_archive_namespace(path: Path) -> bool:
    names = tuple(name.casefold() for name in _ARCHIVE_ROOT_NAMES)
    return any(
        part.casefold() == name or part.casefold().startswith(f"{name}__")
        for part in path.parts
        for name in names
    )


def _existing_components(path: Path) -> list[tuple[Path, os.stat_result]]:
    components: list[tuple[Path, os.stat_result]] = []
    current = path
    while True:
        try:
            components.append((current, current.lstat()))
        except FileNotFoundError:
            pass
        except OSError as exc:
            raise ValueError("admin catalog path cannot be inspected safely") from exc
        if current == current.parent:
            break
        current = current.parent
    return components


def _has_reparse_component(path: Path) -> bool:
    for _component, metadata in _existing_components(path):
        attributes = getattr(metadata, "st_file_attributes", 0)
        if stat.S_ISLNK(metadata.st_mode) or attributes & _WINDOWS_REPARSE_ATTRIBUTE:
            return True
    return False


def _configured_root() -> Path:
    override = os.getenv(ADMIN_CATALOG_ENV, "").strip()
    if override:
        return Path(override).expanduser()
    local_app_data = os.getenv("LOCALAPPDATA", "").strip()
    if not local_app_data:
        raise RuntimeError(
            "LOCALAPPDATA is required when MORPHIC_ADMIN_CATALOG_DIR is not configured"
        )
    return Path(local_app_data).expanduser() / "MorphicEngine" / "admin_catalog"


def _validate_root(
    root: str | Path,
    *,
    project_root: str | Path,
    blocked_roots: Iterable[str | Path] | None,
) -> Path:
    raw_root = Path(root).expanduser()
    if not raw_root.is_absolute():
        raise ValueError("admin catalog root must be an absolute path")
    if _contains_parent_traversal(raw_root):
        raise ValueError("admin catalog root must not contain path traversal")
    if _has_reparse_component(raw_root):
        raise ValueError("admin catalog root must not use a symlink or Windows reparse point")

    resolved_root = raw_root.resolve(strict=False)
    resolved_project = Path(project_root).expanduser().resolve(strict=False)
    if _overlaps(resolved_root, resolved_project):
        raise ValueError("admin catalog root must be outside and separate from the project root")
    if _uses_archive_namespace(resolved_root):
        raise ValueError("admin catalog root must be separate from export/archive namespaces")

    additional_roots = (
        () if blocked_roots is None else tuple(Path(item) for item in blocked_roots)
    )
    roots = (*_default_blocked_roots(resolved_project), *additional_roots)
    for blocked in roots:
        raw_blocked = blocked.expanduser()
        if not raw_blocked.is_absolute():
            raise ValueError("blocked export/archive root must be absolute")
        resolved_blocked = raw_blocked.resolve(strict=False)
        if _overlaps(resolved_root, resolved_blocked):
            raise ValueError("admin catalog root must be separate from export/archive roots")
    return resolved_root


def admin_catalog_root(
    *,
    project_root: str | Path = PROJECT_ROOT,
    blocked_roots: Iterable[str | Path] | None = None,
) -> Path:
    """Resolve the dedicated external root without creating it.

    An explicit ``MORPHIC_ADMIN_CATALOG_DIR`` wins.  Otherwise the root is
    derived solely from ``LOCALAPPDATA``; the worktree-backed ``runtime_root``
    is intentionally not consulted.
    """

    return _validate_root(
        _configured_root(),
        project_root=project_root,
        blocked_roots=blocked_roots,
    )


def context_namespace(context: CatalogContext) -> str:
    """Return a stable namespace bound to every exact context component."""

    if not isinstance(context, CatalogContext):
        raise TypeError("context must be CatalogContext")
    canonical = json.dumps(
        context.canonical_mapping(),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return f"ctx-v1-{hashlib.sha256(canonical).hexdigest()}"


def catalog_database_path(
    context: CatalogContext,
    *,
    root: str | Path | None = None,
    writable: bool = True,
    project_root: str | Path = PROJECT_ROOT,
    blocked_roots: Iterable[str | Path] | None = None,
) -> Path:
    """Return a sandboxed path after a non-mutating point-in-time validation.

    A later integration must revalidate immediately before directory creation or
    SQLite open; returning a ``Path`` cannot prevent another process from
    replacing a not-yet-existing component after this planning check.
    """

    if not isinstance(context, CatalogContext):
        raise TypeError("context must be CatalogContext")
    if writable and context.scope == "system":
        raise PermissionError("system-scope Admin Catalog paths are read-only by default")

    resolved_root = (
        admin_catalog_root(project_root=project_root, blocked_roots=blocked_roots)
        if root is None
        else _validate_root(
            root,
            project_root=project_root,
            blocked_roots=blocked_roots,
        )
    )
    unresolved_target = resolved_root / context_namespace(context) / CATALOG_DATABASE_FILENAME
    if _has_reparse_component(unresolved_target):
        raise ValueError("admin catalog path crosses a symlink or Windows reparse point")
    resolved_target = unresolved_target.resolve(strict=False)
    if not _is_within(resolved_target, resolved_root):
        raise ValueError("admin catalog path escapes its sandbox")
    return resolved_target
