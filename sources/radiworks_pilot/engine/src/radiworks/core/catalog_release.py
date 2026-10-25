"""Opt-in, immutable rate-catalog releases for a single pinned engine lifetime."""

from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

SCHEMA = "radiworks.catalog-release.v1"
_RELEASE_ID = re.compile(r"[0-9a-f]{32}\Z")
_HEX_DIGEST = re.compile(r"[0-9a-f]{64}\Z")


class CatalogSnapshotError(ValueError):
    """A published catalog is missing, modified, or unsafe to consume."""


def _redirected(path: Path) -> bool:
    info = path.lstat()
    return path.is_symlink() or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def _regular_files(root: Path) -> list[Path]:
    if _redirected(root) or not root.is_dir():
        raise CatalogSnapshotError("Katalogverzeichnis ist nicht sicher lesbar")
    result: list[Path] = []

    def failed(exc: OSError) -> None:
        raise CatalogSnapshotError("Katalogverzeichnis ist nicht vollständig lesbar") from exc

    for base, dirs, files in os.walk(root, followlinks=False, onerror=failed):
        directory = Path(base)
        for name in dirs:
            if _redirected(directory / name):
                raise CatalogSnapshotError("Katalog enthält einen Verzeichnisverweis")
        for name in files:
            path = directory / name
            if _redirected(path) or not path.is_file():
                raise CatalogSnapshotError("Katalog enthält einen Dateiverweis")
            result.append(path)
    return result


def _relative_path(raw: object) -> Path:
    if not isinstance(raw, str) or not raw or "\\" in raw or ":" in raw:
        raise CatalogSnapshotError("Ungültiger Katalogpfad")
    posix = PurePosixPath(raw)
    if posix.is_absolute() or posix.as_posix() != raw or any(
        part in {".", ".."} for part in posix.parts
    ):
        raise CatalogSnapshotError("Ungültiger Katalogpfad")
    return Path(*posix.parts)


def publish_catalog_release(source_dir: Path, releases_dir: Path) -> Path:
    """Copy an operator-frozen source into a new release, then atomically publish it.

    The source must remain unchanged during publication. This function detects
    ordinary drift but cannot certify an externally mutable source against ABA.
    Failed staging directories are deliberately left unpublished for inspection.
    """
    source = Path(source_dir).expanduser().resolve(strict=True)
    releases = Path(releases_dir).expanduser().resolve()
    if source == releases or source.is_relative_to(releases) or releases.is_relative_to(source):
        raise CatalogSnapshotError("Quelle und Release-Ziel müssen getrennt sein")
    files = _regular_files(source)
    if not files:
        raise CatalogSnapshotError("Leerer Katalog wird nicht veröffentlicht")
    releases.mkdir(parents=True, exist_ok=True)
    release_id = uuid.uuid4().hex
    staging = releases / f".staging-{release_id}"
    final = releases / release_id
    staging.mkdir()
    data_target = staging / "data"
    data_target.mkdir()
    entries: list[dict] = []
    for path in files:
        relative = path.relative_to(source)
        content = path.read_bytes()
        target = data_target / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        entries.append({
            "path": relative.as_posix(),
            "bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
        })
    current = _regular_files(source)
    if {path.relative_to(source).as_posix() for path in current} != {
        entry["path"] for entry in entries
    }:
        raise CatalogSnapshotError("Quelle hat sich während der Veröffentlichung verändert")
    for entry in entries:
        path = source / _relative_path(entry["path"])
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            raise CatalogSnapshotError("Quelle hat sich während der Veröffentlichung verändert")
    manifest = {"schema": SCHEMA, "releaseId": release_id, "files": entries}
    with (staging / "manifest.json").open("x", encoding="utf-8") as output:
        json.dump(manifest, output, ensure_ascii=False, separators=(",", ":"))
        output.flush()
        os.fsync(output.fileno())
    os.replace(staging, final)
    return final


@dataclass(frozen=True)
class CatalogRelease:
    data_dir: Path
    release_id: str
    entries: tuple[dict, ...]

    @classmethod
    def load_for_data_dir(cls, data_dir: Path) -> CatalogRelease | None:
        raw_data = Path(data_dir).expanduser().absolute()

        def reject_release_alias() -> None:
            try:
                target = raw_data.resolve()
            except (OSError, RuntimeError) as exc:
                raise CatalogSnapshotError("Katalogpfad ist nicht auflösbar") from exc
            if target.name == "data" and _RELEASE_ID.fullmatch(target.parent.name):
                raise CatalogSnapshotError("Katalog-Release muss direkt adressiert werden")

        if raw_data.name != "data":
            reject_release_alias()
            return None
        raw_release = raw_data.parent
        raw_manifest = raw_release / "manifest.json"
        is_release_path = (
            raw_release.name.startswith(".staging-")
            or bool(_RELEASE_ID.fullmatch(raw_release.name))
            or raw_manifest.exists()
        )
        if not is_release_path:
            reject_release_alias()
            return None
        try:
            if _redirected(raw_data) or _redirected(raw_release):
                raise CatalogSnapshotError("Veröffentlichter Katalogpfad wurde umgeleitet")
            if raw_manifest.exists() and _redirected(raw_manifest):
                raise CatalogSnapshotError("Katalogmanifest wurde umgeleitet")
            data = raw_data.resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise CatalogSnapshotError("Veröffentlichter Katalogpfad ist nicht verfügbar") from exc
        release_dir = data.parent
        if release_dir.name.startswith(".staging-"):
            raise CatalogSnapshotError("Unveröffentlichter Katalogstand")
        if not _RELEASE_ID.fullmatch(release_dir.name):
            raise CatalogSnapshotError("Ungültiger Katalog-Release-Name")
        try:
            manifest = json.loads((release_dir / "manifest.json").read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise CatalogSnapshotError("Katalogmanifest fehlt oder ist ungültig") from exc
        if (
            not isinstance(manifest, dict)
            or manifest.get("schema") != SCHEMA
            or manifest.get("releaseId") != release_dir.name
            or not isinstance(manifest.get("files"), list)
            or not manifest["files"]
        ):
            raise CatalogSnapshotError("Katalogmanifest hat ein ungültiges Schema")
        seen: set[str] = set()
        for entry in manifest["files"]:
            if not isinstance(entry, dict):
                raise CatalogSnapshotError("Ungültiger Katalogeintrag")
            relative = _relative_path(entry.get("path"))
            name = relative.as_posix()
            if name in seen or type(entry.get("bytes")) is not int or entry["bytes"] < 0:
                raise CatalogSnapshotError("Ungültiger Katalogeintrag")
            if not isinstance(entry.get("sha256"), str) or not _HEX_DIGEST.fullmatch(entry["sha256"]):
                raise CatalogSnapshotError("Ungültiger Katalogdigest")
            seen.add(name)
        release = cls(data, release_dir.name, tuple(manifest["files"]))
        release.verify_tree()
        return release

    def verify_tree(self) -> None:
        actual = _regular_files(self.data_dir)
        expected = {entry["path"] for entry in self.entries}
        if {path.relative_to(self.data_dir).as_posix() for path in actual} != expected:
            raise CatalogSnapshotError("Veröffentlichter Katalog enthält abweichende Dateien")
        for entry in self.entries:
            self.read_verified(self.data_dir / _relative_path(entry["path"]))

    def read_verified(self, path: Path) -> bytes:
        try:
            name = path.relative_to(self.data_dir).as_posix()
            entry = next(item for item in self.entries if item["path"] == name)
            if _redirected(path):
                raise CatalogSnapshotError("Veröffentlichter Katalog enthält einen Dateiverweis")
            content = path.read_bytes()
        except (OSError, ValueError, StopIteration) as exc:
            raise CatalogSnapshotError("Veröffentlichter Katalog ist nicht vollständig verfügbar") from exc
        if len(content) != entry["bytes"] or hashlib.sha256(content).hexdigest() != entry["sha256"]:
            raise CatalogSnapshotError("Veröffentlichter Katalog wurde verändert")
        return content
