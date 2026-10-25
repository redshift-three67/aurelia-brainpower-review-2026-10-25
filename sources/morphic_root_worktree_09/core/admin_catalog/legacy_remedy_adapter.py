"""Read-only inventory of the legacy remedy SQLite authority for Admin Catalog F4.1."""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path

from .contracts import CatalogContext, CatalogEntry, EntryType, RelationType


_EXPORT_SCHEMA_VERSION = 1
_AUTHORITY = "legacy_remedy_sqlite"
_SOURCE_ID = "legacy-remedies-db"
_SOURCE_STATUS = "legacy_unprovenanced"
_REQUIRED_TABLES = frozenset({"remedies", "pathogens", "remedy_pathogen_map"})
_EXPECTED_TABLE_SCHEMAS: dict[str, tuple[tuple[object, ...], ...]] = {
    "remedies": (
        (0, "id", "INTEGER", 0, None, 1, 0),
        (1, "name", "TEXT", 1, None, 0, 0),
        (2, "potency", "TEXT", 0, None, 0, 0),
        (3, "category", "TEXT", 0, None, 0, 0),
        (4, "indication", "TEXT", 0, None, 0, 0),
        (5, "created_at", "TIMESTAMP", 0, "CURRENT_TIMESTAMP", 0, 0),
        (6, "source", "TEXT", 0, None, 0, 0),
        (7, "oorep_id", "INTEGER", 0, None, 0, 0),
        (8, "abbrev", "TEXT", 0, None, 0, 0),
    ),
    "pathogens": (
        (0, "id", "INTEGER", 0, None, 1, 0),
        (1, "name", "TEXT", 1, None, 0, 0),
        (2, "pathogen_type", "TEXT", 1, None, 0, 0),
        (3, "category", "TEXT", 0, None, 0, 0),
        (4, "indication", "TEXT", 0, None, 0, 0),
        (5, "created_at", "TIMESTAMP", 0, "CURRENT_TIMESTAMP", 0, 0),
    ),
    "remedy_pathogen_map": (
        (0, "id", "INTEGER", 0, None, 1, 0),
        (1, "pathogen_id", "INTEGER", 1, None, 0, 0),
        (2, "remedy_id", "INTEGER", 1, None, 0, 0),
        (3, "priority", "INTEGER", 0, "0", 0, 0),
    ),
}


class LegacyRemedyAdapterError(ValueError):
    """The legacy database cannot be represented by the closed F4.1 contract."""


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _positive_integer(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise LegacyRemedyAdapterError(f"{field} must be a positive integer")
    return value


def _non_negative_integer(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise LegacyRemedyAdapterError(f"{field} must be a non-negative integer")
    return value


def _required_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise LegacyRemedyAdapterError(f"{field} must be non-empty text")
    return value


def _optional_text(value: object, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise LegacyRemedyAdapterError(f"{field} must be text or null")
    return value


def _optional_integer(value: object, field: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise LegacyRemedyAdapterError(f"{field} must be an integer or null")
    return value


def _description(value: str | None) -> dict[str, object]:
    if value is None or not value.strip():
        return {}
    return {"description": value}


@dataclass(frozen=True, slots=True)
class LegacyRemedy:
    legacy_id: int
    catalog_id: str
    name: str
    potency: str | None
    category: str | None
    indication: str | None
    created_at: str | None
    legacy_source: str | None
    oorep_id: int | None
    abbrev: str | None
    source_status: str = _SOURCE_STATUS


@dataclass(frozen=True, slots=True)
class LegacyPathogen:
    legacy_id: int
    catalog_id: str
    name: str
    pathogen_type: str
    category: str | None
    indication: str | None
    created_at: str | None
    source_status: str = _SOURCE_STATUS


@dataclass(frozen=True, slots=True)
class LegacyRemedyPathogenRelation:
    legacy_id: int
    catalog_id: str
    pathogen_catalog_id: str
    remedy_catalog_id: str
    priority: int
    relation_type: str = RelationType.REMEDY_PATHOGEN.value
    source_status: str = _SOURCE_STATUS


@dataclass(frozen=True, slots=True)
class LegacyRemedyExport:
    schema_version: int
    authority: str
    source_status: str
    database_sha256: str
    remedies: tuple[LegacyRemedy, ...]
    pathogens: tuple[LegacyPathogen, ...]
    relations: tuple[LegacyRemedyPathogenRelation, ...]

    def canonical_json(self) -> str:
        return _canonical_json(asdict(self))

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()

    def catalog_entries(self, context: CatalogContext) -> tuple[CatalogEntry, ...]:
        """Project the lossless inventory onto the fields supported by F1 contracts."""

        entries: list[CatalogEntry] = []
        for remedy in self.remedies:
            entries.append(
                CatalogEntry(
                    entry_type=EntryType.REMEDY,
                    entry_id=remedy.catalog_id,
                    context=context,
                    source_id=_SOURCE_ID,
                    provenance=remedy.source_status,
                    data={
                        "label": remedy.name,
                        "enabled": True,
                        **_description(remedy.indication),
                    },
                )
            )
        for pathogen in self.pathogens:
            entries.append(
                CatalogEntry(
                    entry_type=EntryType.PATHOGEN,
                    entry_id=pathogen.catalog_id,
                    context=context,
                    source_id=_SOURCE_ID,
                    provenance=pathogen.source_status,
                    data={
                        "label": pathogen.name,
                        "enabled": True,
                        **_description(pathogen.indication),
                    },
                )
            )
        for relation in self.relations:
            entries.append(
                CatalogEntry(
                    entry_type=EntryType.RELATION,
                    entry_id=relation.catalog_id,
                    context=context,
                    source_id=_SOURCE_ID,
                    provenance=relation.source_status,
                    data={
                        "enabled": True,
                        "pathogen_id": relation.pathogen_catalog_id,
                        "priority": relation.priority,
                        "relation_type": relation.relation_type,
                        "remedy_id": relation.remedy_catalog_id,
                    },
                )
            )
        return tuple(entries)


def _remedy(row: sqlite3.Row) -> LegacyRemedy:
    legacy_id = _positive_integer(row["id"], "remedy id")
    return LegacyRemedy(
        legacy_id=legacy_id,
        catalog_id=f"legacy-remedy-{legacy_id}",
        name=_required_text(row["name"], "remedy name"),
        potency=_optional_text(row["potency"], "remedy potency"),
        category=_optional_text(row["category"], "remedy category"),
        indication=_optional_text(row["indication"], "remedy indication"),
        created_at=_optional_text(row["created_at"], "remedy created_at"),
        legacy_source=_optional_text(row["source"], "remedy source"),
        oorep_id=_optional_integer(row["oorep_id"], "remedy oorep_id"),
        abbrev=_optional_text(row["abbrev"], "remedy abbrev"),
    )


def _pathogen(row: sqlite3.Row) -> LegacyPathogen:
    legacy_id = _positive_integer(row["id"], "pathogen id")
    return LegacyPathogen(
        legacy_id=legacy_id,
        catalog_id=f"legacy-pathogen-{legacy_id}",
        name=_required_text(row["name"], "pathogen name"),
        pathogen_type=_required_text(row["pathogen_type"], "pathogen type"),
        category=_optional_text(row["category"], "pathogen category"),
        indication=_optional_text(row["indication"], "pathogen indication"),
        created_at=_optional_text(row["created_at"], "pathogen created_at"),
    )


def _relation(row: sqlite3.Row) -> LegacyRemedyPathogenRelation:
    legacy_id = _positive_integer(row["id"], "relation id")
    pathogen_id = _positive_integer(row["pathogen_id"], "relation pathogen_id")
    remedy_id = _positive_integer(row["remedy_id"], "relation remedy_id")
    return LegacyRemedyPathogenRelation(
        legacy_id=legacy_id,
        catalog_id=f"legacy-remedy-pathogen-{legacy_id}",
        pathogen_catalog_id=f"legacy-pathogen-{pathogen_id}",
        remedy_catalog_id=f"legacy-remedy-{remedy_id}",
        priority=_non_negative_integer(row["priority"], "relation priority"),
    )


def _source_sidecars(path: Path) -> tuple[Path, ...]:
    return tuple(
        sidecar
        for suffix in ("-wal", "-shm", "-journal")
        if (sidecar := path.with_name(f"{path.name}{suffix}")).exists()
    )


def _verify_source_unchanged(path: Path, expected_hash: str) -> None:
    try:
        if _source_sidecars(path) or _sha256(path) != expected_hash:
            raise LegacyRemedyAdapterError(
                "legacy remedy database changed during read"
            )
    except LegacyRemedyAdapterError:
        raise
    except OSError:
        raise LegacyRemedyAdapterError(
            "legacy remedy database changed during read"
        ) from None


def _bound_source_bytes(path: Path) -> tuple[bytes, str]:
    """Read one file handle and bind its bytes, identity and source path."""

    if _source_sidecars(path):
        raise LegacyRemedyAdapterError("legacy remedy database has a sidecar")
    try:
        path_stat = path.stat()
        with path.open("rb") as source:
            opened_stat = os.fstat(source.fileno())
            if not os.path.samestat(path_stat, opened_stat):
                raise LegacyRemedyAdapterError(
                    "legacy remedy database identity changed during read"
                )
            snapshot_bytes = source.read()
            finished_stat = os.fstat(source.fileno())
        if (
            not os.path.samestat(opened_stat, finished_stat)
            or opened_stat.st_size != finished_stat.st_size
            or opened_stat.st_mtime_ns != finished_stat.st_mtime_ns
            or len(snapshot_bytes) != finished_stat.st_size
            or not os.path.samestat(finished_stat, path.stat())
        ):
            raise LegacyRemedyAdapterError(
                "legacy remedy database identity changed during read"
            )
    except LegacyRemedyAdapterError:
        raise
    except OSError:
        raise LegacyRemedyAdapterError(
            "legacy remedy database could not be snapshotted"
        ) from None
    if _source_sidecars(path):
        raise LegacyRemedyAdapterError("legacy remedy database has a sidecar")
    database_hash = hashlib.sha256(snapshot_bytes).hexdigest()
    _verify_source_unchanged(path, database_hash)
    return snapshot_bytes, database_hash


def export_legacy_remedies(database_path: Path) -> LegacyRemedyExport:
    """Deserialize the exact hash-bound source bytes into a private query-only DB."""

    if not isinstance(database_path, Path):
        raise TypeError("database_path must be pathlib.Path")
    resolved = database_path.resolve(strict=False)
    if not resolved.is_file():
        raise FileNotFoundError(resolved)
    snapshot_bytes, database_hash = _bound_source_bytes(resolved)
    connection: sqlite3.Connection | None = None
    try:
        connection = sqlite3.connect(":memory:")
        connection.execute("PRAGMA query_only=ON")
        connection.execute("PRAGMA temp_store=MEMORY")
        connection.execute("PRAGMA trusted_schema=OFF")
        connection.deserialize(snapshot_bytes)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only=ON")
        connection.execute("PRAGMA temp_store=MEMORY")
        connection.execute("PRAGMA trusted_schema=OFF")
        connection.execute("BEGIN")
        integrity = connection.execute("PRAGMA integrity_check").fetchall()
        if tuple(tuple(row) for row in integrity) != (("ok",),):
            raise LegacyRemedyAdapterError("legacy remedy database integrity failed")
        tables = {
            str(row["name"])
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        if not _REQUIRED_TABLES <= tables:
            raise LegacyRemedyAdapterError("required legacy tables are missing")
        for table_name, expected_schema in _EXPECTED_TABLE_SCHEMAS.items():
            observed_schema = tuple(
                tuple(row)
                for row in connection.execute(
                    f"PRAGMA table_xinfo({table_name})"
                ).fetchall()
            )
            if observed_schema != expected_schema:
                raise LegacyRemedyAdapterError(
                    f"legacy table schema mismatch: {table_name}"
                )
        remedy_rows = connection.execute(
            """
            SELECT id, name, potency, category, indication, created_at,
                   source, oorep_id, abbrev
            FROM remedies ORDER BY id
            """
        ).fetchall()
        pathogen_rows = connection.execute(
            """
            SELECT id, name, pathogen_type, category, indication, created_at
            FROM pathogens ORDER BY id
            """
        ).fetchall()
        relation_rows = connection.execute(
            """
            SELECT id, pathogen_id, remedy_id, priority
            FROM remedy_pathogen_map ORDER BY id
            """
        ).fetchall()
    except LegacyRemedyAdapterError:
        raise
    except (MemoryError, sqlite3.Error):
        raise LegacyRemedyAdapterError(
            "legacy remedy database could not be read"
        ) from None
    finally:
        close_error = False
        try:
            if connection is not None:
                connection.close()
        except sqlite3.Error:
            close_error = True
        if close_error:
            raise LegacyRemedyAdapterError(
                "private remedy database could not be closed"
            ) from None

    remedies = tuple(_remedy(row) for row in remedy_rows)
    pathogens = tuple(_pathogen(row) for row in pathogen_rows)
    relations = tuple(_relation(row) for row in relation_rows)
    remedy_ids = {item.catalog_id for item in remedies}
    pathogen_ids = {item.catalog_id for item in pathogens}
    relation_ids = {item.catalog_id for item in relations}
    if any(
        relation.remedy_catalog_id not in remedy_ids
        or relation.pathogen_catalog_id not in pathogen_ids
        for relation in relations
    ):
        raise LegacyRemedyAdapterError("orphan relation in legacy remedy database")
    if len(remedy_ids) != len(remedies) or len(pathogen_ids) != len(pathogens):
        raise LegacyRemedyAdapterError("duplicate legacy integer identity")
    if len(relation_ids) != len(relations):
        raise LegacyRemedyAdapterError("duplicate relation identity")
    _verify_source_unchanged(resolved, database_hash)
    return LegacyRemedyExport(
        schema_version=_EXPORT_SCHEMA_VERSION,
        authority=_AUTHORITY,
        source_status=_SOURCE_STATUS,
        database_sha256=database_hash,
        remedies=remedies,
        pathogens=pathogens,
        relations=relations,
    )


__all__ = [
    "LegacyPathogen",
    "LegacyRemedy",
    "LegacyRemedyAdapterError",
    "LegacyRemedyExport",
    "LegacyRemedyPathogenRelation",
    "export_legacy_remedies",
]
