#!/usr/bin/env python3
"""
Import-Script für OOREP (Open Online Repertory) homöopathische Mittel.

Liest die oorep.sql Datei und importiert die Remedy-Daten in die remedies.db.
Erstellt eine neue Gruppe 'oorep_homeopathy_multiplex' für den Multiplex-Scan.

Quelle: https://github.com/nondeterministic/oorep
Lizenz: GPL v3
"""

import sqlite3
import re
from pathlib import Path
from datetime import datetime

# Pfade
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
OOREP_SQL = DATA_DIR / "oorep.sql"
REMEDIES_DB = DATA_DIR / "remedies.db"

# Gruppe für die importierten Mittel
GROUP_NAME = "oorep_homeopathy_multiplex"
GROUP_DESCRIPTION = "Homöopathische Einzelmittel aus OOREP (Open Online Repertory) - Kent, Boericke, Hahnemann"


def parse_oorep_remedies(sql_path: Path) -> list[dict]:
    """Parst die oorep.sql und extrahiert Remedy-Daten."""
    
    print(f"Lese {sql_path}...")
    
    with open(sql_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Finde den COPY-Block für remedy
    pattern = r"COPY public\.remedy \(id, nameabbrev, namelong, namealt\) FROM stdin;\n(.*?)\n\\."
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        raise ValueError("Konnte COPY public.remedy Block nicht finden!")
    
    remedy_data = match.group(1)
    lines = remedy_data.strip().split("\n")
    
    remedies = []
    for line in lines:
        if not line.strip():
            continue
        
        # Tab-separierte Felder
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        
        remedy_id = parts[0]
        abbrev = parts[1]
        name_long = parts[2]
        name_alt = parts[3] if len(parts) > 3 and parts[3] != "\\N" else None
        
        # Alternative Namen parsen (PostgreSQL Array Format)
        alt_names = []
        if name_alt and name_alt.startswith("{") and name_alt.endswith("}"):
            # Format: {"Name1","Name2"}
            alt_content = name_alt[1:-1]
            if alt_content:
                # Einfaches Parsing für quoted strings
                alt_names = [n.strip('"') for n in alt_content.split('","')]
        
        remedies.append({
            "oorep_id": int(remedy_id),
            "abbrev": abbrev,
            "name": name_long,
            "alt_names": alt_names,
        })
    
    print(f"  → {len(remedies)} Mittel gefunden")
    return remedies


def import_to_remedies_db(remedies: list[dict], db_path: Path) -> int:
    """Importiert die Remedies in die SQLite-Datenbank.
    
    Tabellenstruktur remedies:
    - id, name, potency, category, indication, created_at, source, oorep_id, abbrev
    """
    
    print(f"\nImportiere in {db_path}...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Prüfe existierende Spalten
    cursor.execute("PRAGMA table_info(remedies)")
    columns = {row[1] for row in cursor.fetchall()}
    print(f"  Vorhandene Spalten: {columns}")
    
    # Füge fehlende Spalten hinzu falls nötig
    if "source" not in columns:
        cursor.execute("ALTER TABLE remedies ADD COLUMN source TEXT")
        print("  → Spalte 'source' hinzugefügt")
    if "oorep_id" not in columns:
        cursor.execute("ALTER TABLE remedies ADD COLUMN oorep_id INTEGER")
        print("  → Spalte 'oorep_id' hinzugefügt")
    if "abbrev" not in columns:
        cursor.execute("ALTER TABLE remedies ADD COLUMN abbrev TEXT")
        print("  → Spalte 'abbrev' hinzugefügt")
    
    # Zähle existierende Einträge für diese Kategorie
    cursor.execute(
        "SELECT COUNT(*) FROM remedies WHERE category = ?",
        (GROUP_NAME,)
    )
    existing_count = cursor.fetchone()[0]
    
    if existing_count > 0:
        print(f"  ⚠️  Kategorie '{GROUP_NAME}' existiert bereits mit {existing_count} Einträgen")
        print("  → Überspringe Import (keine Duplikate)")
        conn.close()
        return 0
    
    # Importiere neue Mittel
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    imported = 0
    skipped = 0
    
    for remedy in remedies:
        # Name = Vollständiger Name
        name = remedy["name"]
        
        # Indication mit Kurzform und Alternativen
        indication_parts = [f"Kurzform: {remedy['abbrev']}"]
        if remedy["alt_names"]:
            indication_parts.append(f"Auch bekannt als: {', '.join(remedy['alt_names'])}")
        indication = " | ".join(indication_parts)
        
        # Prüfe ob Name bereits existiert
        cursor.execute("SELECT id FROM remedies WHERE name = ?", (name,))
        if cursor.fetchone():
            skipped += 1
            continue
        
        cursor.execute("""
            INSERT INTO remedies (name, potency, category, indication, created_at, source, oorep_id, abbrev)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            None,  # potency - nicht relevant für homöopathische Grundmittel
            GROUP_NAME,
            indication,
            timestamp,
            "OOREP - Open Online Repertory (GPL v3)",
            remedy["oorep_id"],
            remedy["abbrev"],
        ))
        imported += 1
    
    conn.commit()
    conn.close()
    
    print(f"  ✅ {imported} Mittel importiert")
    if skipped > 0:
        print(f"  ⚠️  {skipped} Mittel übersprungen (bereits vorhanden)")
    
    return imported


def verify_import(db_path: Path):
    """Verifiziert den Import."""
    
    print(f"\nVerifiziere Import...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Zähle Einträge
    cursor.execute(
        "SELECT COUNT(*) FROM remedies WHERE category = ?",
        (GROUP_NAME,)
    )
    count = cursor.fetchone()[0]
    print(f"  → {count} Einträge in Kategorie '{GROUP_NAME}'")
    
    # Zeige Beispiele
    cursor.execute("""
        SELECT name, abbrev, indication 
        FROM remedies 
        WHERE category = ?
        ORDER BY name
        LIMIT 10
    """, (GROUP_NAME,))
    
    print("\n  Beispiele:")
    for row in cursor.fetchall():
        print(f"    - {row[0]} ({row[1]})")
    
    # Statistik nach Anfangsbuchstaben
    cursor.execute("""
        SELECT SUBSTR(name, 1, 1) as letter, COUNT(*) as cnt
        FROM remedies
        WHERE category = ?
        GROUP BY letter
        ORDER BY letter
    """, (GROUP_NAME,))
    
    print("\n  Verteilung nach Anfangsbuchstaben:")
    letters = cursor.fetchall()
    line = "    "
    for letter, cnt in letters:
        line += f"{letter}:{cnt} "
        if len(line) > 80:
            print(line)
            line = "    "
    if line.strip():
        print(line)
    
    conn.close()


def main():
    """Hauptfunktion."""
    
    print("=" * 60)
    print("OOREP Homöopathie-Mittel Import")
    print("=" * 60)
    print(f"Quelle: {OOREP_SQL}")
    print(f"Ziel: {REMEDIES_DB}")
    print(f"Gruppe: {GROUP_NAME}")
    print("=" * 60)
    
    # Prüfe Dateien
    if not OOREP_SQL.exists():
        print(f"❌ Fehler: {OOREP_SQL} nicht gefunden!")
        print("   Bitte laden Sie oorep.sql.gz von GitHub herunter und entpacken Sie es.")
        return 1
    
    if not REMEDIES_DB.exists():
        print(f"⚠️  {REMEDIES_DB} existiert nicht, wird erstellt...")
    
    # Parse und importiere
    try:
        remedies = parse_oorep_remedies(OOREP_SQL)
        imported = import_to_remedies_db(remedies, REMEDIES_DB)
        
        if imported > 0:
            verify_import(REMEDIES_DB)
            print("\n" + "=" * 60)
            print("✅ Import erfolgreich abgeschlossen!")
            print("=" * 60)
            print(f"\nNächster Schritt: Registrieren Sie die Gruppe in procedural_groups.py:")
            print(f'  _DYNAMIC_GROUPS.append("{GROUP_NAME}")')
        else:
            print("\n⚠️  Keine neuen Mittel importiert.")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Fehler beim Import: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
