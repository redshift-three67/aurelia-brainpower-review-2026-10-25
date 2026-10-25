from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from core.db.health import (
    assert_core_databases_ready,
    collect_core_database_health,
    table_count,
)


def test_table_count_counts_rows(tmp_path: Path) -> None:
    db_path = tmp_path / "sample.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute("create table sample (id integer primary key, label text)")
        conn.executemany("insert into sample (label) values (?)", [("a",), ("b",)])

    assert table_count(db_path, "sample") == 2


def test_table_count_rejects_unsafe_table_names(tmp_path: Path) -> None:
    db_path = tmp_path / "sample.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute("create table sample (id integer primary key)")

    with pytest.raises(ValueError):
        table_count(db_path, "sample; drop table sample")


def test_collect_core_database_health_reports_real_project_databases() -> None:
    report = collect_core_database_health(Path("data"))

    assert report["ok"] is True, report
    assert report["databases"]["remedies"]["tables"]["remedies"] >= 1000
    assert report["databases"]["remedies"]["tables"]["remedy_keywords"] >= 1000
    assert report["databases"]["descriptions"]["tables"]["items"] >= 1000
    assert "resonance" in report["databases"]


def test_allowed_empty_optional_database_does_not_warn() -> None:
    report = collect_core_database_health(Path("data"))
    resonance = report["databases"]["resonance"]

    assert resonance["ok"] is True
    assert resonance["warnings"] == []
    assert not any("resonance.db" in warning for warning in report["warnings"])


def test_assert_core_databases_ready_rejects_missing_data_dir(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError):
        assert_core_databases_ready(tmp_path / "missing")
