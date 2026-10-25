#!/usr/bin/env python3
"""Prüft die Struktur der remedies.db"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "remedies.db"

print(f"Prüfe: {DB_PATH}")
print("=" * 60)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Tabellen auflisten
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"\nTabellen: {[t[0] for t in tables]}")

# Für jede Tabelle die Struktur anzeigen
for (table_name,) in tables:
    print(f"\n--- Tabelle: {table_name} ---")
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]:20} {col[2]:15} {'NOT NULL' if col[3] else ''}")
    
    # Beispieldaten
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 2")
    rows = cursor.fetchall()
    if rows:
        print(f"  Beispiele:")
        for row in rows:
            print(f"    {row}")

conn.close()
print("\n" + "=" * 60)
