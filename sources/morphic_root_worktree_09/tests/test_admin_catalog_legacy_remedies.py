from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import replace
from pathlib import Path

import pytest

import core.admin_catalog.legacy_remedy_adapter as legacy_adapter
from core.admin_catalog.contracts import CatalogContext, EntryType
from core.admin_catalog.legacy_remedy_adapter import (
    LegacyRemedyAdapterError,
    export_legacy_remedies,
)
from core.admin_catalog.validation import validate_entries


PRODUCTION_DB = Path("data/remedies.db")
PRODUCTION_SHA256 = "c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0"
PRODUCTION_EXPORT_SHA256 = "21141427843b112560c333681e4512e24110b5d9701a192d840a192a9304e6a4"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _context() -> CatalogContext:
    return CatalogContext(
        operator_id="operator-f41",
        workspace_id="workspace-f41",
        tenant_id="tenant-f41",
        scope="workspace",
    )


def _create_fixture_database(
    path: Path, *, remedy_potency_type: str = "TEXT"
) -> None:
    if remedy_potency_type not in {"TEXT", "INTEGER"}:
        raise ValueError("unsupported synthetic potency type")
    with sqlite3.connect(path) as connection:
        connection.executescript(
            f"""
            CREATE TABLE remedies (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                potency {remedy_potency_type},
                category TEXT,
                indication TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source TEXT,
                oorep_id INTEGER,
                abbrev TEXT
            );
            CREATE TABLE pathogens (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                pathogen_type TEXT NOT NULL,
                category TEXT,
                indication TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE remedy_pathogen_map (
                id INTEGER PRIMARY KEY,
                pathogen_id INTEGER NOT NULL,
                remedy_id INTEGER NOT NULL,
                priority INTEGER DEFAULT 0
            );
            """
        )
        connection.executemany(
            """
            INSERT INTO remedies (
                id, name, potency, category, indication, created_at,
                source, oorep_id, abbrev
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    2,
                    "Alpha Remedy D6",
                    "D6",
                    "synthetic-a",
                    "Synthetic indication A",
                    "2026-01-01 00:00:00",
                    None,
                    None,
                    "Alpha",
                ),
                (
                    7,
                    "alpha remedy d6",
                    None,
                    "synthetic-b",
                    "Synthetic indication B",
                    None,
                    "Unverified Legacy Source",
                    77,
                    None,
                ),
            ],
        )
        connection.execute(
            """
            INSERT INTO pathogens (
                id, name, pathogen_type, category, indication, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                3,
                "Synthetic Pathogen",
                "synthetic",
                "Synthetic Category",
                "Synthetic pathogen indication",
                "2026-01-02 00:00:00",
            ),
        )
        connection.executemany(
            """
            INSERT INTO remedy_pathogen_map (
                id, pathogen_id, remedy_id, priority
            ) VALUES (?, ?, ?, ?)
            """,
            [(11, 3, 2, 3), (12, 3, 7, 1)],
        )


def test_production_export_has_exact_counts_is_deterministic_and_null_mutating() -> None:
    before_hash = _sha256(PRODUCTION_DB)
    before_stat = PRODUCTION_DB.stat()
    before_siblings = tuple(sorted(path.name for path in PRODUCTION_DB.parent.iterdir()))

    first = export_legacy_remedies(PRODUCTION_DB)
    second = export_legacy_remedies(PRODUCTION_DB)

    assert before_hash == PRODUCTION_SHA256
    assert first.schema_version == 1
    assert first.authority == "legacy_remedy_sqlite"
    assert first.source_status == "legacy_unprovenanced"
    assert first.database_sha256 == PRODUCTION_SHA256
    assert len(first.remedies) == 4079
    assert len(first.pathogens) == 1273
    assert len(first.relations) == 4373
    assert first.canonical_json() == second.canonical_json()
    assert first.sha256 == second.sha256
    assert first.sha256 == hashlib.sha256(
        first.canonical_json().encode("utf-8")
    ).hexdigest()
    assert first.sha256 == PRODUCTION_EXPORT_SHA256
    assert _sha256(PRODUCTION_DB) == before_hash
    assert PRODUCTION_DB.stat().st_size == before_stat.st_size
    assert PRODUCTION_DB.stat().st_mtime_ns == before_stat.st_mtime_ns
    assert tuple(sorted(path.name for path in PRODUCTION_DB.parent.iterdir())) == before_siblings


def test_production_export_is_field_exact_and_uses_integer_namespaced_ids() -> None:
    exported = export_legacy_remedies(PRODUCTION_DB)
    uri = f"{PRODUCTION_DB.resolve().as_uri()}?mode=ro"
    with sqlite3.connect(uri, uri=True) as connection:
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

    assert len(exported.remedies) == len(remedy_rows)
    for normalized, source in zip(exported.remedies, remedy_rows, strict=True):
        assert (
            normalized.legacy_id,
            normalized.name,
            normalized.potency,
            normalized.category,
            normalized.indication,
            normalized.created_at,
            normalized.legacy_source,
            normalized.oorep_id,
            normalized.abbrev,
        ) == source
        assert normalized.catalog_id == f"legacy-remedy-{normalized.legacy_id}"
        assert normalized.source_status == "legacy_unprovenanced"

    assert len(exported.pathogens) == len(pathogen_rows)
    for normalized, source in zip(exported.pathogens, pathogen_rows, strict=True):
        assert (
            normalized.legacy_id,
            normalized.name,
            normalized.pathogen_type,
            normalized.category,
            normalized.indication,
            normalized.created_at,
        ) == source
        assert normalized.catalog_id == f"legacy-pathogen-{normalized.legacy_id}"
        assert normalized.source_status == "legacy_unprovenanced"

    assert len(exported.relations) == len(relation_rows)
    for normalized, source in zip(exported.relations, relation_rows, strict=True):
        legacy_id, pathogen_id, remedy_id, priority = source
        assert normalized.legacy_id == legacy_id
        assert normalized.catalog_id == f"legacy-remedy-pathogen-{legacy_id}"
        assert normalized.pathogen_catalog_id == f"legacy-pathogen-{pathogen_id}"
        assert normalized.remedy_catalog_id == f"legacy-remedy-{remedy_id}"
        assert normalized.priority == priority
        assert normalized.relation_type == "remedy_pathogen"
        assert normalized.source_status == "legacy_unprovenanced"


def test_catalog_projection_is_complete_valid_and_preserves_every_link() -> None:
    exported = export_legacy_remedies(PRODUCTION_DB)
    entries = exported.catalog_entries(_context())

    assert len(entries) == 9725
    assert sum(entry.entry_type is EntryType.REMEDY for entry in entries) == 4079
    assert sum(entry.entry_type is EntryType.PATHOGEN for entry in entries) == 1273
    assert sum(entry.entry_type is EntryType.RELATION for entry in entries) == 4373
    assert all(entry.source_id == "legacy-remedies-db" for entry in entries)
    assert all(entry.provenance == "legacy_unprovenanced" for entry in entries)
    assert validate_entries(entries).is_valid is True

    remedies = {
        entry.entry_id: entry
        for entry in entries
        if entry.entry_type is EntryType.REMEDY
    }
    pathogens = {
        entry.entry_id: entry
        for entry in entries
        if entry.entry_type is EntryType.PATHOGEN
    }
    for source in exported.remedies:
        projected = remedies[source.catalog_id]
        expected_data: dict[str, object] = {
            "label": source.name,
            "enabled": True,
        }
        if source.indication is not None and source.indication.strip():
            expected_data["description"] = source.indication
        assert dict(projected.data) == expected_data
    for source in exported.pathogens:
        projected = pathogens[source.catalog_id]
        expected_data = {"label": source.name, "enabled": True}
        if source.indication is not None and source.indication.strip():
            expected_data["description"] = source.indication
        assert dict(projected.data) == expected_data

    relations = {
        entry.entry_id: entry
        for entry in entries
        if entry.entry_type is EntryType.RELATION
    }
    assert len(relations) == len(exported.relations)
    for source in exported.relations:
        projected = relations[source.catalog_id]
        assert dict(projected.data) == {
            "enabled": True,
            "pathogen_id": source.pathogen_catalog_id,
            "priority": source.priority,
            "relation_type": "remedy_pathogen",
            "remedy_id": source.remedy_catalog_id,
        }


def test_reader_deserializes_exact_hash_bound_bytes_query_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database = tmp_path / "fixture.db"
    _create_fixture_database(database)
    original_hash = _sha256(database)
    real_connect = sqlite3.connect
    calls: list[tuple[object, bool]] = []
    statements: list[str] = []
    deserialized_hashes: list[str] = []

    class TrackingConnection(sqlite3.Connection):
        def deserialize(self, data: bytes, *, name: str = "main") -> None:
            deserialized_hashes.append(hashlib.sha256(data).hexdigest())
            super().deserialize(data, name=name)

    def tracked_connect(database_arg: object, *args: object, **kwargs: object):
        calls.append((database_arg, bool(kwargs.get("uri"))))
        connection = real_connect(
            database_arg, *args, factory=TrackingConnection, **kwargs
        )
        connection.set_trace_callback(statements.append)
        return connection

    monkeypatch.setattr(
        "core.admin_catalog.legacy_remedy_adapter.sqlite3.connect",
        tracked_connect,
    )

    exported = export_legacy_remedies(database)

    assert len(exported.remedies) == 2
    assert len(exported.pathogens) == 1
    assert len(exported.relations) == 2
    assert calls == [(":memory:", False)]
    assert deserialized_hashes == [original_hash]
    normalized_statements = tuple(statement.strip().upper() for statement in statements)
    assert normalized_statements.count("PRAGMA QUERY_ONLY=ON") == 2
    assert normalized_statements.count("PRAGMA TEMP_STORE=MEMORY") == 2
    assert normalized_statements.count("PRAGMA TRUSTED_SCHEMA=OFF") == 2
    assert "BEGIN" in normalized_statements
    assert all(
        statement.startswith(("PRAGMA", "BEGIN", "SELECT"))
        or statement == "ATTACH X AS 'MAIN'"
        for statement in normalized_statements
    )
    assert _sha256(database) == original_hash
    assert not database.with_name(f"{database.name}-journal").exists()
    assert not database.with_name(f"{database.name}-wal").exists()


def test_fixture_casefold_name_collision_does_not_collide_catalog_ids(
    tmp_path: Path,
) -> None:
    database = tmp_path / "fixture.db"
    _create_fixture_database(database)

    exported = export_legacy_remedies(database)

    assert exported.remedies[0].name.casefold() == exported.remedies[1].name.casefold()
    assert exported.remedies[0].catalog_id != exported.remedies[1].catalog_id
    assert len({item.catalog_id for item in exported.remedies}) == 2
    assert exported.remedies[1].legacy_source == "Unverified Legacy Source"
    assert all(
        item.source_status == "legacy_unprovenanced" for item in exported.remedies
    )


def test_orphan_relation_fails_closed(tmp_path: Path) -> None:
    database = tmp_path / "orphan.db"
    _create_fixture_database(database)
    with sqlite3.connect(database) as connection:
        connection.execute(
            "UPDATE remedy_pathogen_map SET remedy_id = 999 WHERE id = 11"
        )

    with pytest.raises(LegacyRemedyAdapterError, match="orphan relation"):
        export_legacy_remedies(database)


def test_duplicate_relation_identity_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database = tmp_path / "duplicate-relation.db"
    _create_fixture_database(database)
    original_relation = legacy_adapter._relation

    def colliding_relation(row: sqlite3.Row):
        return replace(
            original_relation(row),
            catalog_id="legacy-remedy-pathogen-collision",
        )

    monkeypatch.setattr(legacy_adapter, "_relation", colliding_relation)

    with pytest.raises(LegacyRemedyAdapterError, match="duplicate relation"):
        export_legacy_remedies(database)


@pytest.mark.parametrize("suffix", ["-wal", "-shm", "-journal"])
def test_source_sidecars_fail_closed_without_being_consumed(
    tmp_path: Path, suffix: str
) -> None:
    database = tmp_path / "sidecar.db"
    _create_fixture_database(database)
    sidecar = database.with_name(f"{database.name}{suffix}")
    sidecar.write_bytes(b"synthetic-sidecar")
    before_hash = _sha256(database)
    sidecar_hash = _sha256(sidecar)

    with pytest.raises(LegacyRemedyAdapterError, match="sidecar"):
        export_legacy_remedies(database)

    assert _sha256(database) == before_hash
    assert _sha256(sidecar) == sidecar_hash


def test_unicode_and_metacharacter_source_path_is_supported(tmp_path: Path) -> None:
    # '?' is not a legal Windows filename; supported metacharacters remain valid.
    database = tmp_path / "räumlich #1%.db"
    _create_fixture_database(database)

    exported = export_legacy_remedies(database)

    assert len(exported.remedies) == 2
    assert exported.database_sha256 == _sha256(database)


def test_source_path_swap_during_private_connect_cannot_change_bound_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database = tmp_path / "source.db"
    replacement = tmp_path / "replacement.db"
    _create_fixture_database(database)
    _create_fixture_database(replacement)
    with sqlite3.connect(replacement) as connection:
        connection.execute(
            "UPDATE remedies SET name = 'Swapped Remedy' WHERE id = 2"
        )
    original_bytes = database.read_bytes()
    replacement_bytes = replacement.read_bytes()
    original_hash = hashlib.sha256(original_bytes).hexdigest()
    real_connect = sqlite3.connect

    def adversarial_connect(database_arg: object, *args: object, **kwargs: object):
        database.write_bytes(replacement_bytes)
        connection = real_connect(database_arg, *args, **kwargs)
        database.write_bytes(original_bytes)
        return connection

    monkeypatch.setattr(
        "core.admin_catalog.legacy_remedy_adapter.sqlite3.connect",
        adversarial_connect,
    )

    exported = export_legacy_remedies(database)

    assert exported.database_sha256 == original_hash
    assert exported.remedies[0].name == "Alpha Remedy D6"
    assert database.read_bytes() == original_bytes


def test_valid_and_broken_symlink_paths_are_handled_explicitly(tmp_path: Path) -> None:
    target = tmp_path / "target.db"
    link = tmp_path / "linked.db"
    broken = tmp_path / "broken.db"
    _create_fixture_database(target)
    try:
        link.symlink_to(target)
        broken.symlink_to(tmp_path / "absent.db")
    except OSError:
        pytest.skip("symlink creation is not permitted on this Windows host")

    exported = export_legacy_remedies(link)

    assert exported.database_sha256 == _sha256(target)
    with pytest.raises(FileNotFoundError):
        export_legacy_remedies(broken)


def test_missing_or_incompatible_database_is_not_created_or_repaired(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    missing = tmp_path / "missing.db"
    before = tuple(tmp_path.iterdir())
    with pytest.raises(FileNotFoundError):
        export_legacy_remedies(missing)
    assert tuple(tmp_path.iterdir()) == before
    assert missing.exists() is False

    directory = tmp_path / "directory.db"
    directory.mkdir()
    with pytest.raises(FileNotFoundError):
        export_legacy_remedies(directory)

    incompatible = tmp_path / "incompatible.db"
    with sqlite3.connect(incompatible) as connection:
        connection.execute("CREATE TABLE unrelated (id INTEGER PRIMARY KEY)")
    before_hash = _sha256(incompatible)
    with pytest.raises(LegacyRemedyAdapterError, match="required legacy tables"):
        export_legacy_remedies(incompatible)
    assert _sha256(incompatible) == before_hash

    extra_column = tmp_path / "extra-column.db"
    _create_fixture_database(extra_column)
    with sqlite3.connect(extra_column) as connection:
        connection.execute("ALTER TABLE remedies ADD COLUMN unexpected TEXT")
    with pytest.raises(
        LegacyRemedyAdapterError, match="legacy table schema mismatch: remedies"
    ):
        export_legacy_remedies(extra_column)

    wrong_type = tmp_path / "wrong-type.db"
    _create_fixture_database(wrong_type, remedy_potency_type="INTEGER")
    with pytest.raises(
        LegacyRemedyAdapterError, match="legacy table schema mismatch: remedies"
    ):
        export_legacy_remedies(wrong_type)

    missing_columns = tmp_path / "missing-columns.db"
    with sqlite3.connect(missing_columns) as connection:
        connection.executescript(
            """
            CREATE TABLE remedies (id INTEGER PRIMARY KEY);
            CREATE TABLE pathogens (id INTEGER PRIMARY KEY);
            CREATE TABLE remedy_pathogen_map (id INTEGER PRIMARY KEY);
            """
        )
    with pytest.raises(
        LegacyRemedyAdapterError, match="legacy table schema mismatch: remedies"
    ):
        export_legacy_remedies(missing_columns)

    corrupt = tmp_path / "corrupt.db"
    corrupt.write_bytes(b"not-a-sqlite-database")
    real_connect = sqlite3.connect
    opened: list[sqlite3.Connection] = []

    class TrackingConnection(sqlite3.Connection):
        closed = False

        def close(self) -> None:
            self.closed = True
            super().close()

    def tracking_connect(database_arg: object, *args: object, **kwargs: object):
        connection = real_connect(
            database_arg, *args, factory=TrackingConnection, **kwargs
        )
        opened.append(connection)
        return connection

    monkeypatch.setattr(
        "core.admin_catalog.legacy_remedy_adapter.sqlite3.connect",
        tracking_connect,
    )
    with pytest.raises(LegacyRemedyAdapterError) as error:
        export_legacy_remedies(corrupt)
    assert str(error.value) == "legacy remedy database could not be read"
    assert error.value.__cause__ is None
    assert error.value.__suppress_context__ is True
    assert len(opened) == 1
    assert opened[0].closed is True  # type: ignore[attr-defined]


def test_adapter_has_no_productive_runtime_cli_or_engine_wiring() -> None:
    root = Path(__file__).resolve().parents[1]
    consumers = []
    marker = "legacy_remedy_adapter"
    for path in root.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        relative = path.relative_to(root).as_posix()
        if relative in {
            "core/admin_catalog/legacy_multiplex_adapter.py",
            "core/admin_catalog/legacy_remedy_adapter.py",
            "tests/test_admin_catalog_legacy_multiplexes.py",
            "tests/test_admin_catalog_legacy_remedies.py",
        }:
            continue
        if marker in path.read_text(encoding="utf-8", errors="ignore"):
            consumers.append(relative)

    assert consumers == []
