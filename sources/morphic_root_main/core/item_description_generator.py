"""
Item Description Generator für Morphic Engine V1

Generiert detaillierte Beschreibungen für Items mittels LLM
und speichert sie in SQLite für permanente Verfügbarkeit.

Features:
- LLM-basierte Beschreibungsgenerierung
- SQLite-Caching für schnellen Zugriff
- Batch-Generierung für alle Items
- Kategorie-spezifische Prompts
"""

import sqlite3
import json
import hashlib
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

# Database
DB_PATH = Path("data/item_descriptions.db")

# LLM-Konfiguration
try:
    from core.llm_pdf_analyzer import call_ollama, check_ollama_available
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False


@dataclass
class ItemDescription:
    """Beschreibung eines Items"""
    item_label: str
    category: str
    short_description: str  # 1-2 Sätze
    detailed_description: str  # Ausführlich
    therapeutic_hints: str  # Therapiehinweise
    related_items: List[str]  # Verwandte Items
    source: str  # 'llm' oder 'manual'
    model_used: str
    created_at: str
    confidence: float


def init_database():
    """Initialisiert die SQLite-Datenbank."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS item_descriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_label TEXT UNIQUE NOT NULL,
            item_hash TEXT NOT NULL,
            category TEXT,
            short_description TEXT,
            detailed_description TEXT,
            therapeutic_hints TEXT,
            related_items TEXT,
            source TEXT DEFAULT 'llm',
            model_used TEXT,
            confidence REAL DEFAULT 0.8,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_item_label ON item_descriptions(item_label)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_category ON item_descriptions(category)
    ''')
    
    conn.commit()
    conn.close()


def get_item_hash(label: str) -> str:
    """Generiert Hash für Item-Label."""
    return hashlib.md5(label.lower().strip().encode()).hexdigest()[:12]


def get_cached_description(label: str) -> Optional[ItemDescription]:
    """Holt gecachte Beschreibung aus DB."""
    init_database()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT item_label, category, short_description, detailed_description,
               therapeutic_hints, related_items, source, model_used, created_at, confidence
        FROM item_descriptions
        WHERE item_label = ? OR item_hash = ?
    ''', (label, get_item_hash(label)))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return ItemDescription(
            item_label=row[0],
            category=row[1] or '',
            short_description=row[2] or '',
            detailed_description=row[3] or '',
            therapeutic_hints=row[4] or '',
            related_items=json.loads(row[5]) if row[5] else [],
            source=row[6] or 'llm',
            model_used=row[7] or '',
            created_at=row[8] or '',
            confidence=row[9] or 0.8
        )
    return None


def save_description(desc: ItemDescription):
    """Speichert Beschreibung in DB."""
    init_database()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    cursor.execute('''
        INSERT OR REPLACE INTO item_descriptions
        (item_label, item_hash, category, short_description, detailed_description,
         therapeutic_hints, related_items, source, model_used, confidence, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        desc.item_label,
        get_item_hash(desc.item_label),
        desc.category,
        desc.short_description,
        desc.detailed_description,
        desc.therapeutic_hints,
        json.dumps(desc.related_items, ensure_ascii=False),
        desc.source,
        desc.model_used,
        desc.confidence,
        desc.created_at or now,
        now
    ))
    
    conn.commit()
    conn.close()


# Kategorie-spezifische System-Prompts
CATEGORY_PROMPTS = {
    'pathogen': """Du bist ein Experte für Mikrobiologie und Infektionskrankheiten.
Beschreibe den Erreger medizinisch korrekt aber verständlich.
Nenne: Typ, Übertragung, Symptome, Behandlungsansätze.""",

    'toxin': """Du bist ein Experte für Toxikologie und Umweltmedizin.
Beschreibe die Substanz, Expositionsquellen, Symptome einer Belastung,
und naturheilkundliche/schulmedizinische Entgiftungsansätze.""",

    'organ': """Du bist ein Experte für Anatomie und Organfunktionen.
Beschreibe das Organ/Körperteil, seine Funktion, typische Störungen,
und unterstützende Maßnahmen für die Organgesundheit.""",

    'nutrient': """Du bist ein Experte für Orthomolekularmedizin und Ernährung.
Beschreibe den Nährstoff, seine Funktionen im Körper, Mangelsymptome,
natürliche Quellen und Dosierungsempfehlungen.""",

    'remedy': """Du bist ein Experte für Naturheilkunde und Komplementärmedizin.
Beschreibe das Mittel, seine Herkunft, traditionelle Anwendung,
Wirkprinzip und Indikationen.""",

    'symptom': """Du bist ein Experte für medizinische Diagnostik.
Beschreibe das Symptom, mögliche Ursachen (differentialdiagnostisch),
und allgemeine Behandlungsansätze.""",

    'frequency': """Du bist ein Experte für Frequenztherapie und Bioelektrizität.
Beschreibe die Frequenz, ihre therapeutische Anwendung,
Wirkprinzip und Anwendungsgebiete.""",
    
    'default': """Du bist ein Experte für ganzheitliche Medizin.
Beschreibe den Begriff medizinisch korrekt und verständlich."""
}


def generate_description_prompt(label: str, category: str, context: str = "") -> str:
    """Erstellt den Prompt für die Beschreibungsgenerierung."""
    
    return f"""Erstelle eine detaillierte Beschreibung für: "{label}"

Antworte im folgenden JSON-Format:
{{
  "short_description": "1-2 Sätze Kurzfassung",
  "detailed_description": "Ausführliche Beschreibung (3-5 Sätze)",
  "therapeutic_hints": "Therapeutische Hinweise und Empfehlungen",
  "related_items": ["verwandtes Item 1", "verwandtes Item 2"],
  "confidence": 0.0-1.0
}}

{f'Zusätzlicher Kontext: {context}' if context else ''}

Antworte NUR mit dem JSON, keine weiteren Erklärungen."""


def generate_single_description(
    label: str,
    category: str = "default",
    model: Optional[str] = None,
    force_regenerate: bool = False
) -> ItemDescription:
    """
    Generiert Beschreibung für ein einzelnes Item.
    
    Args:
        label: Item-Label
        category: Kategorie für spezifischen Prompt
        model: Ollama-Modell
        force_regenerate: Cache ignorieren
    
    Returns:
        ItemDescription
    """
    # Cache prüfen
    if not force_regenerate:
        cached = get_cached_description(label)
        if cached:
            return cached
    
    if not LLM_AVAILABLE:
        raise ImportError("LLM-Modul nicht verfügbar")
    
    ollama = check_ollama_available()
    if not ollama['available']:
        raise RuntimeError(f"Ollama nicht verfügbar: {ollama.get('error')}")
    
    model = model or ollama.get('recommended', 'llama3.2')
    
    # System-Prompt basierend auf Kategorie
    system_prompt = CATEGORY_PROMPTS.get(category, CATEGORY_PROMPTS['default'])
    
    # Generierung
    prompt = generate_description_prompt(label, category)
    
    try:
        response, metadata = call_ollama(
            prompt,
            model=model,
            system_prompt=system_prompt,
            temperature=0.3
        )
        
        # JSON extrahieren
        import re
        json_match = re.search(r'\{[\s\S]*\}', response)
        
        if json_match:
            data = json.loads(json_match.group())
            
            desc = ItemDescription(
                item_label=label,
                category=category,
                short_description=data.get('short_description', ''),
                detailed_description=data.get('detailed_description', ''),
                therapeutic_hints=data.get('therapeutic_hints', ''),
                related_items=data.get('related_items', []),
                source='llm',
                model_used=model,
                created_at=datetime.now().isoformat(),
                confidence=data.get('confidence', 0.8)
            )
            
            # In DB speichern
            save_description(desc)
            
            return desc
    
    except Exception as e:
        # Fallback: Minimale Beschreibung
        return ItemDescription(
            item_label=label,
            category=category,
            short_description=f"{label} - Beschreibung nicht verfügbar",
            detailed_description=f"Fehler bei der Generierung: {e}",
            therapeutic_hints="",
            related_items=[],
            source='error',
            model_used=model or '',
            created_at=datetime.now().isoformat(),
            confidence=0.0
        )


def generate_batch_descriptions(
    items: List[Dict],
    model: Optional[str] = None,
    progress_callback: Optional[callable] = None
) -> Dict:
    """
    Generiert Beschreibungen für mehrere Items.
    
    Args:
        items: Liste von {'label': str, 'category': str}
        model: Ollama-Modell
        progress_callback: Optional callback(current, total, label)
    
    Returns:
        Statistik-Dict
    """
    stats = {
        'total': len(items),
        'generated': 0,
        'cached': 0,
        'errors': 0,
        'items': []
    }
    
    for i, item in enumerate(items):
        label = item.get('label', '')
        category = item.get('category', 'default')
        
        if progress_callback:
            progress_callback(i + 1, len(items), label)
        
        try:
            # Prüfe ob gecacht
            cached = get_cached_description(label)
            if cached:
                stats['cached'] += 1
                stats['items'].append({
                    'label': label,
                    'status': 'cached',
                    'confidence': cached.confidence
                })
                continue
            
            # Generieren
            desc = generate_single_description(label, category, model)
            
            if desc.source == 'error':
                stats['errors'] += 1
                stats['items'].append({
                    'label': label,
                    'status': 'error',
                    'error': desc.detailed_description
                })
            else:
                stats['generated'] += 1
                stats['items'].append({
                    'label': label,
                    'status': 'generated',
                    'confidence': desc.confidence
                })
                
        except Exception as e:
            stats['errors'] += 1
            stats['items'].append({
                'label': label,
                'status': 'error',
                'error': str(e)
            })
    
    return stats


def get_description_for_report(label: str, category: str = "default") -> Dict:
    """
    Holt Beschreibung für Report-Integration.
    Generiert automatisch wenn nicht vorhanden.
    
    Returns:
        Dict mit short_description, detailed_description, therapeutic_hints
    """
    try:
        desc = generate_single_description(label, category)
        return {
            'short': desc.short_description,
            'detailed': desc.detailed_description,
            'therapeutic': desc.therapeutic_hints,
            'related': desc.related_items,
            'confidence': desc.confidence,
            'source': desc.source
        }
    except Exception:
        return {
            'short': '',
            'detailed': '',
            'therapeutic': '',
            'related': [],
            'confidence': 0,
            'source': 'unavailable'
        }


def get_database_stats() -> Dict:
    """Gibt Statistiken zur Beschreibungs-DB zurück."""
    init_database()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Gesamtzahl
    cursor.execute('SELECT COUNT(*) FROM item_descriptions')
    total = cursor.fetchone()[0]
    
    # Nach Kategorie
    cursor.execute('''
        SELECT category, COUNT(*) 
        FROM item_descriptions 
        GROUP BY category
    ''')
    by_category = dict(cursor.fetchall())
    
    # Nach Source
    cursor.execute('''
        SELECT source, COUNT(*) 
        FROM item_descriptions 
        GROUP BY source
    ''')
    by_source = dict(cursor.fetchall())
    
    # Durchschnittliche Konfidenz
    cursor.execute('SELECT AVG(confidence) FROM item_descriptions')
    avg_confidence = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        'database_path': str(DB_PATH.absolute()),
        'total_descriptions': total,
        'by_category': by_category,
        'by_source': by_source,
        'average_confidence': avg_confidence
    }


def export_descriptions_to_json(output_path: Optional[str] = None) -> str:
    """Exportiert alle Beschreibungen als JSON."""
    init_database()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM item_descriptions')
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    
    data = [dict(zip(columns, row)) for row in rows]
    
    conn.close()
    
    output_path = output_path or str(DB_PATH.with_suffix('.export.json'))
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return output_path
