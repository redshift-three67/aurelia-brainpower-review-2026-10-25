#!/usr/bin/env python3
"""
Description Service - SQLite-basierte Verwaltung von Item-Beschreibungen
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from contextlib import contextmanager

# Datenbank-Pfad
DB_PATH = Path(__file__).parent.parent / "data" / "descriptions.db"
ITEM_DESCRIPTION_DB_PATH = Path(__file__).parent.parent / "data" / "item_descriptions.db"


def get_db_path() -> Path:
    """Gibt den Pfad zur Datenbank zurück."""
    return DB_PATH


@contextmanager
def get_connection():
    """Context Manager für Datenbankverbindung."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def _table_exists(cursor: sqlite3.Cursor, table_name: str) -> bool:
    cursor.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    )
    return cursor.fetchone() is not None


def _get_cached_item_description(label: str) -> Optional[str]:
    if not ITEM_DESCRIPTION_DB_PATH.exists():
        return None

    with sqlite3.connect(str(ITEM_DESCRIPTION_DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if not _table_exists(cursor, "item_descriptions"):
            return None
        cursor.execute(
            """
            SELECT short_description, detailed_description
            FROM item_descriptions
            WHERE item_label = ?
              AND (
                (short_description IS NOT NULL AND short_description != '')
                OR (detailed_description IS NOT NULL AND detailed_description != '')
              )
            LIMIT 1
            """,
            (label,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return row["short_description"] or row["detailed_description"]


def _get_cached_item_descriptions(labels: List[str]) -> Dict[str, str]:
    if not labels or not ITEM_DESCRIPTION_DB_PATH.exists():
        return {}

    with sqlite3.connect(str(ITEM_DESCRIPTION_DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if not _table_exists(cursor, "item_descriptions"):
            return {}
        placeholders = ",".join("?" * len(labels))
        cursor.execute(
            f"""
            SELECT item_label, short_description, detailed_description
            FROM item_descriptions
            WHERE item_label IN ({placeholders})
              AND (
                (short_description IS NOT NULL AND short_description != '')
                OR (detailed_description IS NOT NULL AND detailed_description != '')
              )
            """,
            labels,
        )
        result: Dict[str, str] = {}
        for row in cursor.fetchall():
            text = row["short_description"] or row["detailed_description"]
            if text:
                result[row["item_label"]] = text
        return result


def init_database():
    """Initialisiert die Datenbank mit dem Schema."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Items-Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT NOT NULL,
                description TEXT,
                group_name TEXT,
                category TEXT,
                model_used TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(label, group_name)
            )
        """)
        
        # Gruppen-Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                display_name TEXT,
                description TEXT,
                item_count INTEGER DEFAULT 0,
                model_used TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Sync-Status-Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_status (
                id INTEGER PRIMARY KEY,
                last_sync TIMESTAMP,
                items_total INTEGER DEFAULT 0,
                items_with_desc INTEGER DEFAULT 0,
                groups_total INTEGER DEFAULT 0,
                groups_with_desc INTEGER DEFAULT 0
            )
        """)
        
        # Initial sync status
        cursor.execute("""
            INSERT OR IGNORE INTO sync_status (id, last_sync) VALUES (1, NULL)
        """)
        
        # Index für schnelle Lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_items_label ON items(label)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_items_group ON items(group_name)
        """)
        
        conn.commit()
        
    print(f"✅ Datenbank initialisiert: {DB_PATH}")


def get_description(label: str, group_name: Optional[str] = None) -> Optional[str]:
    """
    Holt die Beschreibung für ein Item.
    
    Args:
        label: Item-Label
        group_name: Optional - Gruppenname für genauere Suche
    
    Returns:
        Beschreibung oder None
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        
        row = None
        if group_name:
            cursor.execute(
                """
                SELECT description FROM items
                WHERE label = ? AND group_name = ? AND description IS NOT NULL AND description != ''
                LIMIT 1
                """,
                (label, group_name)
            )
            row = cursor.fetchone()
        else:
            cursor.execute(
                """
                SELECT description FROM items
                WHERE label = ? AND description IS NOT NULL AND description != ''
                LIMIT 1
                """,
                (label,)
            )
            row = cursor.fetchone()
        
        if row:
            return row["description"]

        if _table_exists(cursor, "descriptions"):
            if group_name:
                cursor.execute(
                    """
                    SELECT description FROM descriptions
                    WHERE label = ? AND group_name = ? AND description IS NOT NULL AND description != ''
                    ORDER BY quality_score DESC
                    LIMIT 1
                    """,
                    (label, group_name),
                )
            else:
                cursor.execute(
                    """
                    SELECT description FROM descriptions
                    WHERE label = ? AND description IS NOT NULL AND description != ''
                    ORDER BY quality_score DESC
                    LIMIT 1
                    """,
                    (label,),
                )

            row = cursor.fetchone()
            if row:
                return row["description"]

        return _get_cached_item_description(label)


def get_descriptions_batch(labels: List[str]) -> Dict[str, str]:
    """
    Holt Beschreibungen für mehrere Items auf einmal.
    
    Args:
        labels: Liste von Item-Labels
    
    Returns:
        Dictionary {label: description}
    """
    if not labels:
        return {}
    
    with get_connection() as conn:
        cursor = conn.cursor()
        placeholders = ",".join("?" * len(labels))
        cursor.execute(
            f"SELECT label, description FROM items WHERE label IN ({placeholders})",
            labels
        )
        
        result = {row["label"]: row["description"] for row in cursor.fetchall() if row["description"]}

        missing_labels = [label for label in labels if label not in result]
        if missing_labels and _table_exists(cursor, "descriptions"):
            placeholders = ",".join("?" * len(missing_labels))
            cursor.execute(
                f"""
                SELECT label, description FROM descriptions
                WHERE label IN ({placeholders})
                  AND description IS NOT NULL
                  AND description != ''
                ORDER BY label, quality_score DESC
                """,
                missing_labels,
            )
            for row in cursor.fetchall():
                result.setdefault(row["label"], row["description"])

        missing_labels = [label for label in labels if label not in result]
        result.update(_get_cached_item_descriptions(missing_labels))

        return result


def save_description(
    label: str,
    description: str,
    group_name: Optional[str] = None,
    category: Optional[str] = None,
    model_used: str = "llama3.2:3b"
) -> bool:
    """
    Speichert eine Beschreibung für ein Item.
    
    Returns:
        True bei Erfolg
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO items (label, description, group_name, category, model_used, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(label, group_name) DO UPDATE SET
                description = excluded.description,
                model_used = excluded.model_used,
                updated_at = excluded.updated_at
        """, (label, description, group_name, category, model_used, datetime.now().isoformat(timespec="seconds")))
        
        conn.commit()
        return True


def save_descriptions_batch(
    descriptions: Dict[str, str],
    group_name: Optional[str] = None,
    category: Optional[str] = None,
    model_used: str = "llama3.2:3b"
) -> int:
    """
    Speichert mehrere Beschreibungen auf einmal.
    
    Returns:
        Anzahl gespeicherter Beschreibungen
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        now = datetime.now().isoformat(timespec="seconds")
        
        data = [
            (label, desc, group_name, category, model_used, now)
            for label, desc in descriptions.items()
        ]
        
        cursor.executemany("""
            INSERT INTO items (label, description, group_name, category, model_used, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(label, group_name) DO UPDATE SET
                description = excluded.description,
                model_used = excluded.model_used,
                updated_at = excluded.updated_at
        """, data)
        
        conn.commit()
        return len(data)


def get_items_without_description(group_name: Optional[str] = None) -> List[str]:
    """
    Gibt alle Items ohne Beschreibung zurück.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        
        if group_name:
            cursor.execute(
                "SELECT label FROM items WHERE (description IS NULL OR description = '') AND group_name = ?",
                (group_name,)
            )
        else:
            cursor.execute(
                "SELECT label FROM items WHERE description IS NULL OR description = ''"
            )
        
        return [row["label"] for row in cursor.fetchall()]


def register_items(items: List[str], group_name: str, category: Optional[str] = None) -> int:
    """
    Registriert Items in der DB (ohne Beschreibung).
    Nützlich um zu tracken welche Items noch Beschreibungen brauchen.
    
    Returns:
        Anzahl neu registrierter Items
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        now = datetime.now()
        
        new_count = 0
        for label in items:
            cursor.execute("""
                INSERT OR IGNORE INTO items (label, group_name, category, created_at)
                VALUES (?, ?, ?, ?)
            """, (label, group_name, category, now))
            if cursor.rowcount > 0:
                new_count += 1
        
        conn.commit()
        return new_count


def get_sync_status() -> Dict:
    """Gibt den aktuellen Sync-Status zurück."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Gesamtzahlen
        cursor.execute("SELECT COUNT(*) as total FROM items")
        items_total = cursor.fetchone()["total"]
        
        cursor.execute("SELECT COUNT(*) as with_desc FROM items WHERE description IS NOT NULL AND description != ''")
        items_with_desc = cursor.fetchone()["with_desc"]
        
        cursor.execute("SELECT COUNT(DISTINCT group_name) as groups FROM items")
        groups_total = cursor.fetchone()["groups"]
        
        cursor.execute("SELECT last_sync FROM sync_status WHERE id = 1")
        row = cursor.fetchone()
        last_sync = row["last_sync"] if row else None

        enriched_descriptions = 0
        available_descriptions = items_with_desc
        if _table_exists(cursor, "descriptions"):
            cursor.execute(
                """
                SELECT COUNT(*) as total
                FROM descriptions
                WHERE description IS NOT NULL AND description != ''
                """
            )
            enriched_descriptions = cursor.fetchone()["total"]

            cursor.execute(
                """
                SELECT COUNT(*) as total FROM (
                    SELECT label, COALESCE(group_name, '') as group_name
                    FROM items
                    WHERE description IS NOT NULL AND description != ''
                    UNION
                    SELECT label, COALESCE(group_name, '') as group_name
                    FROM descriptions
                    WHERE description IS NOT NULL AND description != ''
                )
                """
            )
            available_descriptions = cursor.fetchone()["total"]
        
        return {
            "items_total": items_total,
            "items_with_desc": items_with_desc,
            "enriched_descriptions": enriched_descriptions,
            "available_descriptions": available_descriptions,
            "items_missing_desc": items_total - items_with_desc,
            "groups_total": groups_total,
            "last_sync": last_sync,
            "coverage_percent": round(available_descriptions / items_total * 100, 1) if items_total > 0 else 0
        }


def update_sync_timestamp():
    """Aktualisiert den Sync-Zeitstempel."""
    with get_connection() as conn:
        cursor = conn.cursor()
        status = get_sync_status()
        
        cursor.execute("""
            UPDATE sync_status SET
                last_sync = ?,
                items_total = ?,
                items_with_desc = ?,
                groups_total = ?
            WHERE id = 1
        """, (datetime.now().isoformat(timespec="seconds"), status["items_total"], status["items_with_desc"], status["groups_total"]))
        
        conn.commit()


def get_group_stats() -> List[Dict]:
    """Gibt Statistiken pro Gruppe zurück."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                group_name,
                COUNT(*) as total,
                SUM(CASE WHEN description IS NOT NULL AND description != '' THEN 1 ELSE 0 END) as with_desc
            FROM items
            GROUP BY group_name
            ORDER BY group_name
        """)
        
        return [
            {
                "group": row["group_name"] or "(ohne Gruppe)",
                "total": row["total"],
                "with_desc": row["with_desc"],
                "missing": row["total"] - row["with_desc"],
                "coverage": round(row["with_desc"] / row["total"] * 100, 1) if row["total"] > 0 else 0
            }
            for row in cursor.fetchall()
        ]


# Initialisierung beim Import
if not DB_PATH.exists():
    init_database()
