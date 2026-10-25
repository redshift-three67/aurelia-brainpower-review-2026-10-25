from __future__ import annotations

import sqlite3
import warnings
from pathlib import Path

from services import description_service


def _prepare_description_db(path: Path, monkeypatch) -> None:
    monkeypatch.setattr(description_service, "DB_PATH", path)
    description_service.init_database()
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS descriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT NOT NULL,
                group_name TEXT NOT NULL,
                description TEXT NOT NULL,
                indications TEXT,
                contraindications TEXT,
                rate_min REAL,
                rate_max REAL,
                source TEXT DEFAULT 'manual',
                quality_score REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(label, group_name)
            )
            """
        )
        conn.commit()


def test_get_description_falls_back_to_enriched_descriptions_table(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "descriptions.db"
    _prepare_description_db(db_path, monkeypatch)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO descriptions (label, group_name, description, quality_score) VALUES (?, ?, ?, ?)",
            ("Aorta", "kreislauf", "Enriched Aorta text", 0.9),
        )
        conn.commit()

    assert description_service.get_description("Aorta") == "Enriched Aorta text"
    assert description_service.get_description("Aorta", "kreislauf") == "Enriched Aorta text"


def test_batch_descriptions_merge_items_and_enriched_descriptions(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "descriptions.db"
    _prepare_description_db(db_path, monkeypatch)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        description_service.save_description("Streptokokken", "Items table text", group_name="bakterien")
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO descriptions (label, group_name, description, quality_score) VALUES (?, ?, ?, ?)",
            ("Aorta", "kreislauf", "Enriched Aorta text", 0.9),
        )
        conn.commit()

    descriptions = description_service.get_descriptions_batch(["Streptokokken", "Aorta"])

    assert descriptions == {
        "Streptokokken": "Items table text",
        "Aorta": "Enriched Aorta text",
    }


def test_sync_status_counts_enriched_description_table(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "descriptions.db"
    _prepare_description_db(db_path, monkeypatch)
    description_service.save_description("Streptokokken", "Items table text", group_name="bakterien")
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO descriptions (label, group_name, description, quality_score) VALUES (?, ?, ?, ?)",
            ("Aorta", "kreislauf", "Enriched Aorta text", 0.9),
        )
        conn.commit()

    status = description_service.get_sync_status()

    assert status["items_with_desc"] == 1
    assert status["enriched_descriptions"] == 1
    assert status["available_descriptions"] == 2


def test_get_description_falls_back_to_item_description_cache(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "descriptions.db"
    item_cache_path = tmp_path / "item_descriptions.db"
    _prepare_description_db(db_path, monkeypatch)
    monkeypatch.setattr(description_service, "ITEM_DESCRIPTION_DB_PATH", item_cache_path)
    with sqlite3.connect(item_cache_path) as conn:
        conn.execute(
            """
            CREATE TABLE item_descriptions (
                item_label TEXT UNIQUE NOT NULL,
                short_description TEXT,
                detailed_description TEXT
            )
            """
        )
        conn.execute(
            """
            INSERT INTO item_descriptions (item_label, short_description, detailed_description)
            VALUES (?, ?, ?)
            """,
            ("Coenzym Q10", "Short Q10 text", "Detailed Q10 text"),
        )
        conn.commit()

    assert description_service.get_description("Coenzym Q10") == "Short Q10 text"
    assert description_service.get_descriptions_batch(["Coenzym Q10"]) == {
        "Coenzym Q10": "Short Q10 text"
    }
