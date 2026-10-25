"""Prepare a separate legacy rate catalog without changing the active release."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

from .catalog_release import CatalogRelease, CatalogSnapshotError


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_files(root: Path) -> list[Path]:
    if not root.is_dir() or root.is_symlink():
        raise CatalogSnapshotError("Katalogquelle ist kein reguläres Verzeichnis")
    files = []
    for directory, dirs, names in os.walk(root, followlinks=False):
        folder = Path(directory)
        dirs[:] = [name for name in dirs if name != ".git"]
        for name in dirs:
            path = folder / name
            if path.is_symlink() or bool(getattr(path.lstat(), "st_file_attributes", 0) & 0x400):
                raise CatalogSnapshotError("Katalogquelle enthält einen Verzeichnisverweis")
        for name in names:
            path = folder / name
            if path.is_symlink() or bool(getattr(path.lstat(), "st_file_attributes", 0) & 0x400) or not path.is_file():
                raise CatalogSnapshotError("Katalogquelle enthält einen Dateiverweis")
            files.append(path)
    return files


def merge_catalog(base_data: Path, legacy_data: Path, target_data: Path) -> dict:
    """Copy base bytes, add safe legacy TXT files, and report every collision."""
    base = Path(base_data).resolve(strict=True)
    legacy = Path(legacy_data).resolve(strict=True)
    # Resolve existing parent links/junctions before proving source separation.
    target = Path(target_data).resolve(strict=False)
    if target.exists() or target.is_relative_to(base) or target.is_relative_to(legacy):
        raise CatalogSnapshotError("Ziel muss neu und von beiden Quellen getrennt sein")
    release = CatalogRelease.load_for_data_dir(base)
    if release:
        release.verify_tree()
    base_files = _safe_files(base)
    legacy_files = _safe_files(legacy)
    target.mkdir(parents=True)
    names: dict[str, Path] = {}
    base_names: set[str] = set()
    for path in base_files:
        relative = path.relative_to(base)
        key = path.name.casefold()
        if key in names:
            raise CatalogSnapshotError("Basiskatalog enthält doppelte Dateinamen")
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(path.read_bytes())
        names[key] = destination
        base_names.add(key)
    report: dict = {"added": 0, "same": 0, "conflicts": 0, "transcoded": 0,
                    "addedFiles": [], "sameFiles": [], "conflictFiles": []}
    candidates = [path for path in legacy_files if path.suffix.lower() == ".txt"
                  and not path.name.startswith("FUNCTION_")]
    for path in sorted(candidates, key=lambda item: (len(item.relative_to(legacy).parts), str(item).casefold())):
        relative = path.relative_to(legacy)
        raw = path.read_bytes()
        if len(raw) > 8 * 1024 * 1024:
            raise CatalogSnapshotError("Raten-Datei überschreitet 8 MiB")
        try:
            content = raw.decode("utf-8")
            encoding = "utf-8"
        except UnicodeDecodeError:
            content = raw.decode("cp1252")
            encoding = "cp1252"
        normalized = content.encode("utf-8")
        key = path.name.casefold()
        if key in names and names[key].read_bytes() == normalized:
            report["same"] += 1
            report["sameFiles"].append({"source": relative.as_posix(), "sha256": _digest(raw)})
            continue
        if key in base_names:
            report["conflicts"] += 1
            report["conflictFiles"].append({"source": relative.as_posix(), "sha256": _digest(raw),
                                             "existingSha256": _digest(names[key].read_bytes())})
            continue
        destination = target / relative
        if key in names:
            prefix = relative.parent.name if len(relative.parts) > 1 else "LEGACY"
            destination = target / relative.parent / f"{prefix}_{path.name}"
            key = destination.name.casefold()
            if key in names:
                raise CatalogSnapshotError("Namensraum für doppelte Raten-Datei ist belegt")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(normalized)
        names[key] = destination
        report["added"] += 1
        report["transcoded"] += encoding != "utf-8"
        report["addedFiles"].append({"source": relative.as_posix(),
                                     "target": destination.relative_to(target).as_posix(),
                                     "sourceSha256": _digest(raw), "targetSha256": _digest(normalized),
                                     "sourceEncoding": encoding})
    return report
