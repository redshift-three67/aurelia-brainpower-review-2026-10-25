"""
SQLite-Datenbank für Item-Beschreibungen.

Speichert therapeutische Beschreibungen für alle Items (Remedies, Meridiane, etc.)
zur schnellen Verwendung in Berichten ohne LLM-Wartezeit.
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class DescriptionsDB:
    """Datenbank für Item-Beschreibungen."""
    
    def __init__(self, db_path: str = "data/descriptions.db"):
        """
        Initialisiert Beschreibungs-Datenbank.
        
        Args:
            db_path: Pfad zur SQLite-Datenbank
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Erstellt Datenbank-Schema falls nicht vorhanden."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Haupttabelle: Beschreibungen
            cursor.execute("""
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
            """)
            
            # Index für schnelle Suche
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_label_group 
                ON descriptions(label, group_name)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_group 
                ON descriptions(group_name)
            """)
            
            # Metadaten-Tabelle
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            logger.info(f"Datenbank initialisiert: {self.db_path}")
    
    def add_description(
        self,
        label: str,
        group_name: str,
        description: str,
        indications: Optional[str] = None,
        contraindications: Optional[str] = None,
        rate_min: Optional[float] = None,
        rate_max: Optional[float] = None,
        source: str = "manual",
        quality_score: float = 0.0
    ) -> bool:
        """
        Fügt Beschreibung hinzu oder aktualisiert sie.
        
        Args:
            label: Item-Label (z.B. "An Shen Wan", "Chrom")
            group_name: Gruppen-Name (z.B. "tcm_rezepturen")
            description: Therapeutische Beschreibung (max 200 Zeichen)
            indications: Indikationen (optional)
            contraindications: Kontraindikationen (optional)
            rate_min: Minimale Rate (optional)
            rate_max: Maximale Rate (optional)
            source: Quelle (manual, ollama, expert)
            quality_score: Qualitätsscore 0.0-1.0
        
        Returns:
            True bei Erfolg
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO descriptions 
                    (label, group_name, description, indications, contraindications, 
                     rate_min, rate_max, source, quality_score, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(label, group_name) DO UPDATE SET
                        description = excluded.description,
                        indications = excluded.indications,
                        contraindications = excluded.contraindications,
                        rate_min = excluded.rate_min,
                        rate_max = excluded.rate_max,
                        source = excluded.source,
                        quality_score = excluded.quality_score,
                        updated_at = CURRENT_TIMESTAMP
                """, (label, group_name, description, indications, contraindications,
                      rate_min, rate_max, source, quality_score))
                
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Fehler beim Hinzufügen von Beschreibung: {e}")
            return False
    
    def get_description(self, label: str, group_name: str = "") -> Optional[str]:
        """
        Holt Beschreibung für Item.
        
        Args:
            label: Item-Label
            group_name: Gruppen-Name (optional, für eindeutige Zuordnung)
        
        Returns:
            Beschreibung oder None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if group_name:
                    cursor.execute("""
                        SELECT description FROM descriptions
                        WHERE label = ? AND group_name = ?
                        LIMIT 1
                    """, (label, group_name))
                else:
                    # Fallback: Suche nur nach Label
                    cursor.execute("""
                        SELECT description FROM descriptions
                        WHERE label = ?
                        ORDER BY quality_score DESC
                        LIMIT 1
                    """, (label,))
                
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Fehler beim Abrufen von Beschreibung: {e}")
            return None
    
    def get_full_info(self, label: str, group_name: str = "") -> Optional[Dict]:
        """
        Holt vollständige Info für Item.
        
        Args:
            label: Item-Label
            group_name: Gruppen-Name (optional)
        
        Returns:
            Dictionary mit allen Feldern oder None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if group_name:
                    cursor.execute("""
                        SELECT * FROM descriptions
                        WHERE label = ? AND group_name = ?
                        LIMIT 1
                    """, (label, group_name))
                else:
                    cursor.execute("""
                        SELECT * FROM descriptions
                        WHERE label = ?
                        ORDER BY quality_score DESC
                        LIMIT 1
                    """, (label,))
                
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"Fehler beim Abrufen von Info: {e}")
            return None
    
    def get_all_by_group(self, group_name: str) -> List[Dict]:
        """
        Holt alle Beschreibungen einer Gruppe.
        
        Args:
            group_name: Gruppen-Name
        
        Returns:
            Liste von Dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM descriptions
                    WHERE group_name = ?
                    ORDER BY label
                """, (group_name,))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Fehler beim Abrufen von Gruppen-Beschreibungen: {e}")
            return []
    
    def get_missing_items(self, items: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """
        Findet Items ohne Beschreibung.
        
        Args:
            items: Liste von (label, group_name) Tupeln
        
        Returns:
            Liste von (label, group_name) Tupeln ohne Beschreibung
        """
        missing = []
        for label, group_name in items:
            if not self.get_description(label, group_name):
                missing.append((label, group_name))
        return missing
    
    def get_stats(self) -> Dict:
        """
        Holt Statistiken über Datenbank.
        
        Returns:
            Dictionary mit Statistiken
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Gesamtanzahl
                cursor.execute("SELECT COUNT(*) FROM descriptions")
                total = cursor.fetchone()[0]
                
                # Nach Quelle
                cursor.execute("""
                    SELECT source, COUNT(*) FROM descriptions
                    GROUP BY source
                """)
                by_source = dict(cursor.fetchall())
                
                # Nach Gruppe (Top 10)
                cursor.execute("""
                    SELECT group_name, COUNT(*) FROM descriptions
                    GROUP BY group_name
                    ORDER BY COUNT(*) DESC
                    LIMIT 10
                """)
                by_group = dict(cursor.fetchall())
                
                # Durchschnittliche Qualität
                cursor.execute("SELECT AVG(quality_score) FROM descriptions")
                avg_quality = cursor.fetchone()[0] or 0.0
                
                return {
                    "total": total,
                    "by_source": by_source,
                    "by_group": by_group,
                    "avg_quality": avg_quality
                }
        except Exception as e:
            logger.error(f"Fehler beim Abrufen von Statistiken: {e}")
            return {}
    
    def export_to_json(self, output_path: str):
        """
        Exportiert alle Beschreibungen als JSON.
        
        Args:
            output_path: Pfad zur JSON-Datei
        """
        import json
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM descriptions ORDER BY group_name, label")
                rows = [dict(row) for row in cursor.fetchall()]
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(rows, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Exportiert: {len(rows)} Beschreibungen → {output_path}")
        except Exception as e:
            logger.error(f"Fehler beim Export: {e}")
    
    def import_from_json(self, input_path: str) -> int:
        """
        Importiert Beschreibungen aus JSON.
        
        Args:
            input_path: Pfad zur JSON-Datei
        
        Returns:
            Anzahl importierter Einträge
        """
        import json
        
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                rows = json.load(f)
            
            count = 0
            for row in rows:
                if self.add_description(
                    label=row.get('label', ''),
                    group_name=row.get('group_name', ''),
                    description=row.get('description', ''),
                    indications=row.get('indications'),
                    contraindications=row.get('contraindications'),
                    rate_min=row.get('rate_min'),
                    rate_max=row.get('rate_max'),
                    source=row.get('source', 'import'),
                    quality_score=row.get('quality_score', 0.0)
                ):
                    count += 1
            
            logger.info(f"Importiert: {count} Beschreibungen aus {input_path}")
            return count
        except Exception as e:
            logger.error(f"Fehler beim Import: {e}")
            return 0


# Globale Instanz (Singleton)
_descriptions_db: Optional[DescriptionsDB] = None


def get_descriptions_db(db_path: str = "data/descriptions.db") -> DescriptionsDB:
    """
    Gibt Beschreibungs-Datenbank Singleton zurück.
    
    Args:
        db_path: Pfad zur Datenbank
    
    Returns:
        DescriptionsDB Instanz
    """
    global _descriptions_db
    
    if _descriptions_db is None:
        _descriptions_db = DescriptionsDB(db_path=db_path)
    
    return _descriptions_db
