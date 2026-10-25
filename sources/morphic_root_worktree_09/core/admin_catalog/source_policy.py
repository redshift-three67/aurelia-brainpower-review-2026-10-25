"""Fail-closed policy boundaries for administrative source manifests.

This module validates server-defined policy values and canonical local-import
paths.  It performs no registry, catalog, network, or directory mutation.
"""

from __future__ import annotations

import stat
from pathlib import Path
from typing import Any, Mapping


ALLOWED_LICENSE_POLICIES = frozenset({"admin-provided", "source-specific"})
ALLOWED_TRUST_LEVELS = frozenset(
    {
        "admin_curated",
        "experimental_unverified",
        "legacy_unverified",
        "official",
        "official_guideline",
    }
)
ALLOWED_IMPORT_POLICIES = frozenset({"api_manual", "manual_review", "reference_only"})
_WINDOWS_REPARSE_ATTRIBUTE = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)


class SourcePolicyError(ValueError):
    """Raised when a source manifest violates server-side source policy."""


def validate_source_policy_fields(data: Mapping[str, Any]) -> None:
    """Reject manifest-provided policy values outside server-owned enums."""

    _validate_enum(data, "license", ALLOWED_LICENSE_POLICIES)
    _validate_enum(data, "trust_level", ALLOWED_TRUST_LEVELS)
    _validate_enum(data, "import_policy", ALLOWED_IMPORT_POLICIES)


def resolve_local_import_path(
    local_path: str | Path,
    *,
    import_root: str | Path,
) -> Path:
    """Resolve a point-in-time plan path below an explicit safe import root.

    F5-A performs no source-data I/O. A future consumer must repeat containment
    through a non-delete-shareable OS handle at its actual read boundary and
    copy the source into a private immutable snapshot.
    """

    raw_root = Path(import_root).expanduser()
    if not raw_root.is_absolute():
        raise SourcePolicyError("admin import root must be absolute")
    if _contains_parent_traversal(raw_root):
        raise SourcePolicyError("admin import root must not contain parent traversal")
    _reject_reparse_components(raw_root, label="admin import root")
    if not raw_root.exists() or not raw_root.is_dir():
        raise SourcePolicyError("admin import root must exist and be a directory")
    try:
        resolved_root = raw_root.resolve(strict=True)
    except OSError as exc:
        raise SourcePolicyError("admin import root cannot be resolved safely") from exc

    raw_source = Path(local_path).expanduser()
    if not str(raw_source).strip():
        raise SourcePolicyError("local_path must not be empty")
    if _contains_parent_traversal(raw_source):
        raise SourcePolicyError("local_path must not contain parent traversal")
    candidate = raw_source if raw_source.is_absolute() else resolved_root / raw_source
    _reject_reparse_components(candidate, label="local_path")
    if not candidate.exists():
        raise SourcePolicyError("local_path must exist")
    try:
        resolved_source = candidate.resolve(strict=True)
    except OSError as exc:
        raise SourcePolicyError("local_path cannot be resolved safely") from exc
    if not _is_within(resolved_source, resolved_root):
        raise SourcePolicyError("local_path escapes or is outside the configured admin import root")
    return resolved_source


def _validate_enum(data: Mapping[str, Any], field: str, allowed: frozenset[str]) -> None:
    value = data.get(field)
    if not isinstance(value, str) or value not in allowed:
        raise SourcePolicyError(f"source field '{field}' is not allowed by server policy")


def _contains_parent_traversal(path: Path) -> bool:
    return any(part == ".." for part in path.parts)


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _reject_reparse_components(path: Path, *, label: str) -> None:
    current = path
    while True:
        try:
            metadata = current.lstat()
        except FileNotFoundError:
            pass
        except OSError as exc:
            raise SourcePolicyError(f"{label} cannot be inspected safely") from exc
        else:
            attributes = getattr(metadata, "st_file_attributes", 0)
            if stat.S_ISLNK(metadata.st_mode) or attributes & _WINDOWS_REPARSE_ATTRIBUTE:
                raise SourcePolicyError(f"{label} must not use a symlink or Windows reparse point")
        if current == current.parent:
            break
        current = current.parent


__all__ = [
    "ALLOWED_IMPORT_POLICIES",
    "ALLOWED_LICENSE_POLICIES",
    "ALLOWED_TRUST_LEVELS",
    "SourcePolicyError",
    "resolve_local_import_path",
    "validate_source_policy_fields",
]
