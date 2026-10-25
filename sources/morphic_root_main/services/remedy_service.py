"""
Remedy-Service für Morphic Engine V1

Intelligente Remedy-Verwaltung mit automatischer Integration:
- Namenskonventions-basierte Zuordnung
- Automatische Erkennung neuer Gruppen
- SQLite-basierte Persistenz
- Ollama-Integration für Beschreibungen
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from contextlib import contextmanager
import re


# Pfade
REMEDY_DB_PATH = Path(__file__).parent.parent / "data" / "remedies.db"
REMEDY_DB_PATH.parent.mkdir(parents=True, exist_ok=True)


# ============================================================================
# DATENBANK-SETUP
# ============================================================================

def init_remedy_database():
    """
    Initialisiert die Remedy-Datenbank.
    
    Schema:
    - remedies: Remedy-Stammdaten (Kohärente Harmonisierung mit...)
    - remedy_keywords: Keywords für automatische Zuordnung
    - remedy_descriptions: AI-generierte Beschreibungen
    - pathogens: Pathogen-Stammdaten (Kohärente Harmonisierung von...)
    - pathogen_keywords: Keywords für Pathogene
    - remedy_pathogen_map: Multiplex-Zuordnung (Pathogen + Remedies)
    """
    conn = sqlite3.connect(REMEDY_DB_PATH)
    cursor = conn.cursor()
    
    # Remedies-Tabelle
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS remedies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            potency TEXT,
            category TEXT,
            indication TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Keywords-Tabelle (für automatische Zuordnung)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS remedy_keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            remedy_id INTEGER NOT NULL,
            keyword TEXT NOT NULL,
            priority INTEGER DEFAULT 0,
            FOREIGN KEY (remedy_id) REFERENCES remedies(id),
            UNIQUE(remedy_id, keyword)
        )
    """)
    
    # Beschreibungen-Tabelle
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS remedy_descriptions (
            remedy_id INTEGER PRIMARY KEY,
            description TEXT,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (remedy_id) REFERENCES remedies(id)
        )
    """)
    
    # Pathogene-Tabelle (NEU)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pathogens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            pathogen_type TEXT NOT NULL,
            category TEXT,
            indication TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Pathogen-Keywords-Tabelle (NEU)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pathogen_keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pathogen_id INTEGER NOT NULL,
            keyword TEXT NOT NULL,
            priority INTEGER DEFAULT 0,
            FOREIGN KEY (pathogen_id) REFERENCES pathogens(id),
            UNIQUE(pathogen_id, keyword)
        )
    """)
    
    # Remedy-Pathogen-Mapping (NEU - Multiplex B)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS remedy_pathogen_map (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pathogen_id INTEGER NOT NULL,
            remedy_id INTEGER NOT NULL,
            priority INTEGER DEFAULT 0,
            FOREIGN KEY (pathogen_id) REFERENCES pathogens(id),
            FOREIGN KEY (remedy_id) REFERENCES remedies(id),
            UNIQUE(pathogen_id, remedy_id)
        )
    """)
    
    # Indizes für Performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_keywords ON remedy_keywords(keyword)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON remedies(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pathogen_keywords ON pathogen_keywords(keyword)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pathogen_type ON pathogens(pathogen_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pathogen_map ON remedy_pathogen_map(pathogen_id)")
    
    conn.commit()
    conn.close()


@contextmanager
def get_remedy_connection():
    """Context Manager für Remedy-DB-Verbindungen."""
    conn = sqlite3.connect(REMEDY_DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# ============================================================================
# REMEDY-VERWALTUNG
# ============================================================================

def add_remedy(
    name: str,
    potency: str,
    category: str,
    indication: str,
    keywords: List[str]
) -> int:
    """
    Fügt ein Remedy zur Datenbank hinzu.
    
    Args:
        name: Remedy-Name (z.B. "Arnica C200")
        potency: Potenz (z.B. "C200", "D6")
        category: Kategorie (z.B. "trauma", "bakterien", "viren")
        indication: Kurze Indikation
        keywords: Keywords für automatische Zuordnung
    
    Returns:
        Remedy-ID
    """
    with get_remedy_connection() as conn:
        cursor = conn.cursor()
        
        # Füge Remedy hinzu (oder ignoriere wenn existiert)
        cursor.execute("""
            INSERT OR IGNORE INTO remedies (name, potency, category, indication)
            VALUES (?, ?, ?, ?)
        """, (name, potency, category, indication))
        
        # Hole Remedy-ID
        cursor.execute("SELECT id FROM remedies WHERE name = ?", (name,))
        remedy_id = cursor.fetchone()[0]
        
        # Füge Keywords hinzu
        for keyword in keywords:
            cursor.execute("""
                INSERT OR IGNORE INTO remedy_keywords (remedy_id, keyword)
                VALUES (?, ?)
            """, (remedy_id, keyword.lower()))
        
        conn.commit()
        return remedy_id


def find_remedies_for_group(
    group_name: str,
    max_results: int = 3
) -> List[Tuple[str, str]]:
    """
    Findet passende Remedies für eine Gruppe basierend auf Keywords.
    
    AUTOMATISCHE ZUORDNUNG via Namenskonventionen:
    - "bakterien" → Bakterien-Remedies
    - "viren" → Viren-Remedies
    - "bat_a05_bakterien_abwehr_borreliose" → Borreliose-Remedies
    - "__remedy_category_heel_remedies__" → Alle Heel-Mittel
    - "__remedy_category_nutramedix_remedies__" → Alle Nutramedix-Mittel
    
    Args:
        group_name: Gruppenname (z.B. "bakterien_fein", "bat_a05_bakterien_abwehr_borreliose")
        max_results: Maximale Anzahl Remedies
    
    Returns:
        Liste von (Remedy-Name, Indikation) Tupeln
    """
    # Prüfe auf Kategorie-Filter-Marker oder Multiplex-Gruppen
    category_map = {
        '__remedy_category_heel_remedies__': 'homotoxikologie_heel',
        '__remedy_category_nutramedix_remedies__': 'phytotherapie_nutramedix',
        # NEU: Multiplex-Gruppen für Profile
        'heel_remedies_multiplex': 'homotoxikologie_heel',
        'nutramedix_remedies_multiplex': 'phytotherapie_nutramedix',
        'schuessler_remedies_multiplex': 'Kohärente Harmonisierung mit Schüssler-Salzen',
    }
    
    if group_name.startswith('__remedy_category_') or group_name in category_map:
        if group_name in category_map:
            target_category = category_map[group_name]
            
            with get_remedy_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name, indication
                    FROM remedies
                    WHERE category = ?
                    ORDER BY name
                    LIMIT ?
                """, (target_category, max_results * 10))  # Mehr Ergebnisse für Hersteller-Profile
                
                return [(row[0], row[1]) for row in cursor.fetchall()]
    
    # Normalisiere Gruppennamen
    group_lower = group_name.lower()
    
    # Extrahiere Keywords aus Gruppennamen
    # Entferne Präfixe wie "bat_a05_"
    clean_name = re.sub(r'^bat_[a-z]\d+_', '', group_lower)
    
    # Splitte in Wörter
    words = re.split(r'[_\s-]+', clean_name)
    
    with get_remedy_connection() as conn:
        cursor = conn.cursor()
        
        # Suche nach Remedies mit passenden Keywords
        # Priorisierung: Exakte Matches > Teilmatches
        results = []
        
        for word in words:
            if len(word) < 3:  # Ignoriere sehr kurze Wörter
                continue
            
            cursor.execute("""
                SELECT DISTINCT r.name, r.indication, rk.priority
                FROM remedies r
                JOIN remedy_keywords rk ON r.id = rk.remedy_id
                WHERE rk.keyword LIKE ?
                ORDER BY rk.priority DESC, r.name
                LIMIT ?
            """, (f"%{word}%", max_results))
            
            for row in cursor.fetchall():
                remedy_tuple = (row[0], row[1])
                if remedy_tuple not in results:
                    results.append(remedy_tuple)
                
                if len(results) >= max_results:
                    break
            
            if len(results) >= max_results:
                break
        
        # Fallback: Allgemeine Remedies basierend auf Hauptkategorie
        if not results:
            # Erkenne Hauptkategorie
            main_category = None
            
            if any(word in group_lower for word in ['bakterien', 'borreliose', 'streptokokken']):
                main_category = 'bakterien'
            elif any(word in group_lower for word in ['viren', 'virus', 'influenza', 'herpes']):
                main_category = 'viren'
            elif any(word in group_lower for word in ['pilz', 'candida', 'dermatophyt']):
                main_category = 'pilze'
            elif any(word in group_lower for word in ['parasit', 'protozoen', 'wurm']):
                main_category = 'parasiten'
            elif any(word in group_lower for word in ['schmerz', 'migräne', 'kopfschmerz']):
                main_category = 'schmerz'
            elif any(word in group_lower for word in ['verletzung', 'trauma', 'bruch', 'prellung']):
                main_category = 'verletzung'
            
            if main_category:
                cursor.execute("""
                    SELECT r.name, r.indication
                    FROM remedies r
                    WHERE r.category = ?
                    ORDER BY r.name
                    LIMIT ?
                """, (main_category, max_results))
                
                results = [(row[0], row[1]) for row in cursor.fetchall()]
        
        return results


def get_remedy_description(remedy_name: str) -> Optional[str]:
    """
    Holt die Beschreibung eines Remedies aus der DB.
    
    Args:
        remedy_name: Name des Remedies
    
    Returns:
        Beschreibung oder None
    """
    with get_remedy_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT rd.description
            FROM remedy_descriptions rd
            JOIN remedies r ON rd.remedy_id = r.id
            WHERE r.name = ?
        """, (remedy_name,))
        
        row = cursor.fetchone()
        return row[0] if row else None


def get_remedies_batch(remedy_names: List[str]) -> Dict[str, str]:
    """
    Holt Beschreibungen für mehrere Remedies.
    
    Args:
        remedy_names: Liste von Remedy-Namen
    
    Returns:
        Dictionary {remedy_name: description}
    """
    if not remedy_names:
        return {}
    
    with get_remedy_connection() as conn:
        cursor = conn.cursor()
        
        placeholders = ','.join('?' * len(remedy_names))
        cursor.execute(f"""
            SELECT r.name, rd.description
            FROM remedies r
            LEFT JOIN remedy_descriptions rd ON r.id = rd.remedy_id
            WHERE r.name IN ({placeholders})
        """, remedy_names)
        
        return {row[0]: row[1] for row in cursor.fetchall() if row[1]}


def list_all_remedies(category: Optional[str] = None) -> List[Dict]:
    """
    Listet alle Remedies auf.
    
    Args:
        category: Optional, filtere nach Kategorie
    
    Returns:
        Liste von Remedy-Dictionaries
    """
    with get_remedy_connection() as conn:
        cursor = conn.cursor()
        
        if category:
            cursor.execute("""
                SELECT r.id, r.name, r.potency, r.category, r.indication,
                       rd.description
                FROM remedies r
                LEFT JOIN remedy_descriptions rd ON r.id = rd.remedy_id
                WHERE r.category = ?
                ORDER BY r.name
            """, (category,))
        else:
            cursor.execute("""
                SELECT r.id, r.name, r.potency, r.category, r.indication,
                       rd.description
                FROM remedies r
                LEFT JOIN remedy_descriptions rd ON r.id = rd.remedy_id
                ORDER BY r.category, r.name
            """)
        
        remedies = []
        for row in cursor.fetchall():
            remedies.append({
                'id': row[0],
                'name': row[1],
                'potency': row[2],
                'category': row[3],
                'indication': row[4],
                'description': row[5]
            })
        
        return remedies


def get_remedy_categories() -> List[str]:
    """
    Gibt alle verfügbaren Remedy-Kategorien zurück.
    
    Returns:
        Liste von Kategorien
    """
    with get_remedy_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT category
            FROM remedies
            WHERE category IS NOT NULL
            ORDER BY category
        """)
        
        return [row[0] for row in cursor.fetchall()]


# ============================================================================
# PATHOGEN-VERWALTUNG (NEU)
# ============================================================================

def add_pathogen(
    name: str,
    pathogen_type: str,
    category: str,
    indication: str,
    keywords: List[str]
) -> int:
    """
    Fügt ein Pathogen zur Datenbank hinzu.
    
    Args:
        name: Pathogen-Name (z.B. "Kohärente Harmonisierung von Staphylococcus aureus")
        pathogen_type: Typ (bakterien, viren, pilze, parasiten)
        category: Kategorie (z.B. "Kohärente Harmonisierung von Bakterien")
        indication: Kurze Indikation
        keywords: Keywords für automatische Zuordnung
    
    Returns:
        Pathogen-ID
    """
    with get_remedy_connection() as conn:
        cursor = conn.cursor()
        
        # Füge Pathogen hinzu (oder ignoriere wenn existiert)
        cursor.execute("""
            INSERT OR IGNORE INTO pathogens (name, pathogen_type, category, indication)
            VALUES (?, ?, ?, ?)
        """, (name, pathogen_type, category, indication))
        
        # Hole Pathogen-ID
        cursor.execute("SELECT id FROM pathogens WHERE name = ?", (name,))
        row = cursor.fetchone()
        pathogen_id = row[0] if row else None
        
        if not pathogen_id:
            conn.rollback()
            return None
        
        # Füge Keywords hinzu
        for keyword in keywords:
            cursor.execute("""
                INSERT OR IGNORE INTO pathogen_keywords (pathogen_id, keyword)
                VALUES (?, ?)
            """, (pathogen_id, keyword.lower()))
        
        conn.commit()
        return pathogen_id


def link_remedy_to_pathogen(pathogen_id: int, remedy_id: int, priority: int = 0):
    """
    Verknüpft ein Remedy mit einem Pathogen (Multiplex B).
    
    Args:
        pathogen_id: ID des Pathogens
        remedy_id: ID des Remedies
        priority: Priorität (höher = wichtiger)
    """
    with get_remedy_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR IGNORE INTO remedy_pathogen_map (pathogen_id, remedy_id, priority)
            VALUES (?, ?, ?)
        """, (pathogen_id, remedy_id, priority))
        
        conn.commit()


def get_remedies_for_pathogen(pathogen_id: int, max_results: int = 5) -> List[Tuple[str, str]]:
    """
    Findet passende Remedies für ein Pathogen (Multiplex B).
    
    Args:
        pathogen_id: ID des Pathogens
        max_results: Maximale Anzahl Remedies
    
    Returns:
        Liste von (Remedy-Name, Indikation) Tupeln
    """
    with get_remedy_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT r.name, r.indication
            FROM remedies r
            JOIN remedy_pathogen_map rpm ON r.id = rpm.remedy_id
            WHERE rpm.pathogen_id = ?
            ORDER BY rpm.priority DESC, r.name
            LIMIT ?
        """, (pathogen_id, max_results))
        
        return [(row[0], row[1]) for row in cursor.fetchall()]


def find_pathogens_by_keyword(keyword: str, max_results: int = 10) -> List[Dict]:
    """
    Findet Pathogene basierend auf Keyword.
    
    Args:
        keyword: Suchbegriff
        max_results: Maximale Anzahl Ergebnisse
    
    Returns:
        Liste von Pathogen-Dictionaries
    """
    with get_remedy_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT p.id, p.name, p.pathogen_type, p.category, p.indication
            FROM pathogens p
            JOIN pathogen_keywords pk ON p.id = pk.pathogen_id
            WHERE pk.keyword LIKE ?
            ORDER BY pk.priority DESC, p.name
            LIMIT ?
        """, (f"%{keyword.lower()}%", max_results))
        
        pathogens = []
        for row in cursor.fetchall():
            pathogens.append({
                'id': row[0],
                'name': row[1],
                'pathogen_type': row[2],
                'category': row[3],
                'indication': row[4]
            })
        
        return pathogens


# ============================================================================
# STATISTIKEN
# ============================================================================

def get_remedy_stats() -> Dict:
    """
    Gibt Statistiken über Remedies und Pathogene zurück.
    
    Returns:
        Dictionary mit Statistiken
    """
    with get_remedy_connection() as conn:
        cursor = conn.cursor()
        
        # Remedies: Gesamt-Anzahl
        cursor.execute("SELECT COUNT(*) FROM remedies")
        total_remedies = cursor.fetchone()[0]
        
        # Remedies: Mit Beschreibung
        cursor.execute("""
            SELECT COUNT(*)
            FROM remedies r
            JOIN remedy_descriptions rd ON r.id = rd.remedy_id
            WHERE rd.description IS NOT NULL AND rd.description != ''
        """)
        remedies_with_description = cursor.fetchone()[0]
        
        # Remedies: Nach Kategorie
        cursor.execute("""
            SELECT category, COUNT(*)
            FROM remedies
            WHERE category IS NOT NULL
            GROUP BY category
            ORDER BY COUNT(*) DESC
        """)
        remedies_by_category = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Pathogene: Gesamt-Anzahl
        cursor.execute("SELECT COUNT(*) FROM pathogens")
        total_pathogens = cursor.fetchone()[0]
        
        # Pathogene: Nach Typ
        cursor.execute("""
            SELECT pathogen_type, COUNT(*)
            FROM pathogens
            GROUP BY pathogen_type
            ORDER BY COUNT(*) DESC
        """)
        pathogens_by_type = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Multiplex: Anzahl Verknüpfungen
        cursor.execute("SELECT COUNT(*) FROM remedy_pathogen_map")
        multiplex_links = cursor.fetchone()[0]
        
        return {
            'total_remedies': total_remedies,
            'remedies_with_description': remedies_with_description,
            'remedies_without_description': total_remedies - remedies_with_description,
            'remedies_by_category': remedies_by_category,
            'total_pathogens': total_pathogens,
            'pathogens_by_type': pathogens_by_type,
            'multiplex_links': multiplex_links,
            # Legacy-Kompatibilität
            'total': total_remedies,
            'with_description': remedies_with_description,
            'without_description': total_remedies - remedies_with_description,
            'by_category': remedies_by_category
        }


# ============================================================================
# INITIALISIERUNG
# ============================================================================

# Initialisiere DB beim Import
init_remedy_database()


if __name__ == "__main__":
    # Test
    print("=" * 70)
    print("REMEDY-SERVICE - VOLLSTÄNDIGE STATISTIK")
    print("=" * 70)
    
    # Teste DB-Initialisierung
    print("\n✅ Datenbank initialisiert")
    print(f"   Pfad: {REMEDY_DB_PATH}")
    
    # Zeige Statistiken
    stats = get_remedy_stats()
    
    print("\n" + "=" * 70)
    print("📊 DATENBANK-ÜBERSICHT")
    print("=" * 70)
    print(f"\n✅ REMEDIES: {stats['total_remedies']}")
    print(f"   Mit Beschreibung: {stats['remedies_with_description']}")
    print(f"   Ohne Beschreibung: {stats['remedies_without_description']}")
    
    print(f"\n✅ PATHOGENE: {stats['total_pathogens']}")
    
    if stats.get('pathogens_by_type'):
        print(f"\n   Nach Typ:")
        for ptype, count in sorted(stats['pathogens_by_type'].items(), key=lambda x: -x[1]):
            print(f"     {ptype}: {count}")
    
    print(f"\n✅ MULTIPLEX-LINKS: {stats['multiplex_links']}")
    print(f"   (Pathogen → Remedy Verknüpfungen)")
    
    print("\n" + "=" * 70)
    print(f"GESAMT: {stats['total_remedies'] + stats['total_pathogens'] + stats['multiplex_links']} DATENSÄTZE")
    print("=" * 70)
    
    if stats['by_category']:
        print(f"\nTop-10 Remedy-Kategorien:")
        sorted_cats = sorted(stats['by_category'].items(), key=lambda x: -x[1])
        for cat, count in sorted_cats[:10]:
            print(f"  {cat}: {count}")
    
    print("\n" + "=" * 70)
