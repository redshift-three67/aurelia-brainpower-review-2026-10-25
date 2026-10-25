"""
Advanced PDF Import für Morphic Engine V1

Erweiterte Funktionen:
- Strukturierte Listen-Erkennung
- Automatische Gruppen-Erstellung
- NLS-Datenbank-Integration
- Multi-Level Pattern-Matching
- Tabellen-Extraktion
"""

import json
import re
import os
from typing import List, Dict, Optional, Tuple, Set
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from collections import defaultdict

# Import-Ordner Definition
IMPORT_FOLDER = Path("imports")
GENERATED_GROUPS_FOLDER = Path("data/generated_groups")
NLS_DATABASE_FOLDER = Path("data/nls_databases")

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

# OCR-Unterstützung
try:
    import pytesseract
    from PIL import Image
    import io
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


@dataclass
class ExtractedItem:
    """Einzelnes extrahiertes Item"""
    label: str
    value: Optional[float] = None
    unit: str = ""
    category: str = "unknown"
    confidence: float = 0.5
    source_page: int = 0
    raw_text: str = ""


@dataclass
class ExtractedGroup:
    """Erkannte Gruppe aus PDF"""
    name: str
    items: List[ExtractedItem] = field(default_factory=list)
    category: str = "unknown"
    source_section: str = ""
    confidence: float = 0.5


@dataclass
class ImportResult:
    """Vollständiges Import-Ergebnis"""
    source_file: str
    extracted_at: str
    total_pages: int
    groups: List[ExtractedGroup] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    quality_score: float = 0.0
    suggestions: List[Dict] = field(default_factory=list)


# Erweiterte Pattern-Definitionen
SECTION_PATTERNS = {
    # Überschriften-Patterns
    'heading': [
        r'^#{1,3}\s+(.+)$',  # Markdown
        r'^([A-ZÄÖÜ][A-ZÄÖÜa-zäöüß\s\-]+):?\s*$',  # GROSSBUCHSTABEN Überschrift
        r'^\d+\.\s+([A-ZÄÖÜ][^\n]+)',  # Nummerierte Überschrift
        r'^([A-Za-zäöüÄÖÜß\s\-]+)\s*[-–—]\s*Analyse',  # "X - Analyse"
        r'^([A-Z]\d+)\s*[-–]\s*(.+)$',  # B.A.T. Format: "A01 - Gruppenname"
    ],
    # Listen-Patterns
    'list_item': [
        r'^\s*[-•●○▪]\s+(.+)',  # Bullet Points
        r'^\s*\d+[.)]\s+(.+)',  # Nummerierte Liste
        r'^\s*[a-z][.)]\s+(.+)',  # Alphabetische Liste
        r'^(\d+[,\.]\d*)\s*[-–]\s*(.+)$',  # B.A.T. Format: "20,1 - Itemname"
        r'^(\d+)\s*[-–]\s*(.+)$',  # Einfaches Format: "20 - Itemname"
    ],
    # Wert-Patterns
    'value': [
        r'(\d+[.,]\d+)\s*%',  # Prozent
        r'(\d+[.,]\d+)\s*(mg|µg|ng|ml|µl)',  # Einheiten
        r'score[:\s]*(\d+[.,]\d+)',  # Score
        r'(\d+[.,]\d+)\s*/\s*10',  # X/10 Format
        r':\s*(\d+[.,]\d+)',  # Nach Doppelpunkt
    ],
}

# Kategorie-Keywords für automatische Zuordnung
CATEGORY_KEYWORDS = {
    'pathogen': {
        'keywords': ['bakterien', 'viren', 'parasiten', 'pilze', 'candida', 'borrelia', 
                     'streptococcus', 'staphylococcus', 'escherichia', 'helicobacter',
                     'herpes', 'epstein-barr', 'ebv', 'cmv', 'hpv'],
        'group_suffix': '_pathogen_multiplex'
    },
    'toxin': {
        'keywords': ['schwermetall', 'quecksilber', 'blei', 'cadmium', 'aluminium',
                     'arsen', 'toxin', 'pestizid', 'herbizid', 'glyphosat', 'belastung'],
        'group_suffix': '_toxin_multiplex'
    },
    'organ': {
        'keywords': ['leber', 'niere', 'herz', 'lunge', 'darm', 'magen', 'gehirn',
                     'milz', 'pankreas', 'schilddrüse', 'nebenniere', 'prostata'],
        'group_suffix': '_organ_multiplex'
    },
    'nutrient': {
        'keywords': ['vitamin', 'mineral', 'zink', 'magnesium', 'eisen', 'selen',
                     'kalzium', 'kalium', 'jod', 'b12', 'folsäure', 'omega'],
        'group_suffix': '_nutrient_multiplex'
    },
    'remedy': {
        'keywords': ['homöopath', 'bach', 'spagyri', 'nosode', 'potenz', 'globuli',
                     'tinktur', 'essenz', 'arnica', 'belladonna', 'phosphorus'],
        'group_suffix': '_remedies_multiplex'
    },
    'symptom': {
        'keywords': ['schmerz', 'müdigkeit', 'kopfschmerz', 'übelkeit', 'durchfall',
                     'verstopfung', 'schlafstörung', 'entzündung', 'allergie'],
        'group_suffix': '_symptom_multiplex'
    },
    'frequency': {
        'keywords': ['frequenz', 'hz', 'khz', 'rife', 'clark', 'solfeggio'],
        'group_suffix': '_frequency_multiplex'
    }
}


def ensure_import_folders():
    """Erstellt Import-Ordner wenn nicht vorhanden."""
    IMPORT_FOLDER.mkdir(parents=True, exist_ok=True)
    GENERATED_GROUPS_FOLDER.mkdir(parents=True, exist_ok=True)
    NLS_DATABASE_FOLDER.mkdir(parents=True, exist_ok=True)
    return {
        'import': str(IMPORT_FOLDER.absolute()),
        'groups': str(GENERATED_GROUPS_FOLDER.absolute()),
        'nls': str(NLS_DATABASE_FOLDER.absolute())
    }


def extract_text_with_ocr(pdf_path: str, language: str = "deu+eng") -> str:
    """
    Extrahiert Text aus PDF mittels OCR (für Bild-basierte PDFs).
    
    Args:
        pdf_path: Pfad zur PDF-Datei
        language: Tesseract-Sprache (deu+eng für Deutsch+Englisch)
    
    Returns:
        Extrahierter Text
    """
    if not PYMUPDF_AVAILABLE:
        raise ImportError("PyMuPDF nicht installiert")
    if not OCR_AVAILABLE:
        raise ImportError("pytesseract/Pillow nicht installiert. Run: pip install pytesseract Pillow")
    
    doc = fitz.open(pdf_path)
    full_text = ""
    
    for page_num, page in enumerate(doc):
        # Erst normalen Text versuchen
        text = page.get_text().strip()
        
        if len(text) < 50:  # Wenig Text = wahrscheinlich Bild-PDF
            # OCR auf Seite anwenden
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x Zoom für bessere OCR
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            try:
                text = pytesseract.image_to_string(img, lang=language)
            except Exception as e:
                text = f"[OCR-Fehler Seite {page_num + 1}: {e}]"
        
        full_text += f"\n--- Seite {page_num + 1} ---\n{text}\n"
    
    doc.close()
    return full_text


def is_image_pdf(pdf_path: str) -> bool:
    """Prüft ob PDF hauptsächlich aus Bildern besteht."""
    if not PYMUPDF_AVAILABLE:
        return False
    
    doc = fitz.open(pdf_path)
    total_text_length = 0
    
    for page in doc:
        total_text_length += len(page.get_text().strip())
    
    doc.close()
    
    # Weniger als 100 Zeichen pro Seite = wahrscheinlich Bild-PDF
    avg_text = total_text_length / max(len(doc), 1) if doc else 0
    return avg_text < 100


def extract_tables_from_pdf(pdf_path: str) -> List[Dict]:
    """
    Extrahiert Tabellen aus PDF mit verbesserter Erkennung.
    """
    if not PYMUPDF_AVAILABLE:
        raise ImportError("PyMuPDF nicht installiert")
    
    doc = fitz.open(pdf_path)
    tables = []
    
    for page_num, page in enumerate(doc):
        # Text mit Positionsinformationen extrahieren
        blocks = page.get_text("dict")["blocks"]
        
        # Suche nach tabellenartigen Strukturen
        lines_with_pos = []
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    text = " ".join([span["text"] for span in line["spans"]])
                    bbox = line["bbox"]
                    lines_with_pos.append({
                        'text': text.strip(),
                        'x': bbox[0],
                        'y': bbox[1],
                        'page': page_num
                    })
        
        # Gruppiere Zeilen nach Y-Position (gleiche Zeile)
        y_groups = defaultdict(list)
        for line in lines_with_pos:
            y_key = round(line['y'] / 10) * 10  # 10px Toleranz
            y_groups[y_key].append(line)
        
        # Erkenne Tabellen (mehrere Spalten in gleicher Zeile)
        for y_key, group in y_groups.items():
            if len(group) >= 2:  # Mindestens 2 Spalten
                sorted_cols = sorted(group, key=lambda x: x['x'])
                row_data = [col['text'] for col in sorted_cols]
                if any(row_data):
                    tables.append({
                        'page': page_num,
                        'y_pos': y_key,
                        'columns': row_data
                    })
    
    doc.close()
    return tables


def extract_bat_format(text: str) -> List[ExtractedGroup]:
    """
    Spezialisierte Extraktion für B.A.T.-Akutprogramm Format.
    Format: "A01 - Gruppenname" für Gruppen, "20,1 - Itemname" für Items.
    """
    groups = []
    current_group = None
    current_group_code = None
    current_items = []
    
    # B.A.T. spezifische Patterns
    group_pattern = re.compile(r'^([A-Z]\d+)\s*[-–]\s*(.+)$')
    item_pattern = re.compile(r'^(\d+[,\.]?\d*)\s*[-–]\s*(.+)$')
    
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('Stand:') or line.startswith('Seite'):
            continue
        
        # Prüfe auf Gruppenüberschrift (A01 - Name)
        group_match = group_pattern.match(line)
        if group_match:
            # Speichere vorherige Gruppe
            if current_group and current_items:
                groups.append(ExtractedGroup(
                    name=current_group,
                    items=current_items,
                    category=categorize_group(current_group, current_items),
                    source_section=f"{current_group_code} - {current_group}"
                ))
            
            current_group_code = group_match.group(1)
            current_group = group_match.group(2).strip()
            current_items = []
            continue
        
        # Prüfe auf Item (20,1 - Name)
        item_match = item_pattern.match(line)
        if item_match and current_group:
            item_code = item_match.group(1)
            item_name = item_match.group(2).strip()
            
            item = ExtractedItem(
                label=item_name,
                value=float(item_code.replace(',', '.')) if item_code else None,
                category=categorize_item(item_name),
                raw_text=line
            )
            current_items.append(item)
    
    # Letzte Gruppe speichern
    if current_group and current_items:
        groups.append(ExtractedGroup(
            name=current_group,
            items=current_items,
            category=categorize_group(current_group, current_items),
            source_section=f"{current_group_code} - {current_group}"
        ))
    
    return groups


def extract_structured_lists(text: str) -> List[ExtractedGroup]:
    """
    Extrahiert strukturierte Listen und erkennt Gruppen.
    Erkennt automatisch B.A.T.-Format.
    """
    # Prüfe auf B.A.T.-Format
    if re.search(r'^[A-Z]\d+\s*[-–]', text, re.MULTILINE):
        bat_groups = extract_bat_format(text)
        if bat_groups:
            return bat_groups
    
    groups = []
    current_group = None
    current_items = []
    
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Prüfe auf Überschrift/Gruppenname
        is_heading = False
        for pattern in SECTION_PATTERNS['heading']:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                # Speichere vorherige Gruppe
                if current_group and current_items:
                    groups.append(ExtractedGroup(
                        name=current_group,
                        items=current_items,
                        category=categorize_group(current_group, current_items),
                        source_section=current_group
                    ))
                
                current_group = match.group(1).strip()
                current_items = []
                is_heading = True
                break
        
        if is_heading:
            continue
        
        # Prüfe auf Listen-Item
        for pattern in SECTION_PATTERNS['list_item']:
            match = re.match(pattern, line)
            if match:
                item_text = match.group(1).strip()
                value = extract_value(item_text)
                
                item = ExtractedItem(
                    label=clean_label(item_text),
                    value=value,
                    category=categorize_item(item_text),
                    raw_text=line
                )
                current_items.append(item)
                break
        else:
            # Kein Listen-Pattern, aber könnte ein Item sein
            if current_group and len(line) > 3 and len(line) < 100:
                value = extract_value(line)
                if value is not None or contains_category_keyword(line):
                    item = ExtractedItem(
                        label=clean_label(line),
                        value=value,
                        category=categorize_item(line),
                        raw_text=line
                    )
                    current_items.append(item)
    
    # Letzte Gruppe speichern
    if current_group and current_items:
        groups.append(ExtractedGroup(
            name=current_group,
            items=current_items,
            category=categorize_group(current_group, current_items),
            source_section=current_group
        ))
    
    return groups


def extract_value(text: str) -> Optional[float]:
    """Extrahiert numerischen Wert aus Text."""
    for pattern in SECTION_PATTERNS['value']:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                value_str = match.group(1).replace(',', '.')
                return float(value_str)
            except ValueError:
                continue
    return None


def clean_label(text: str) -> str:
    """Bereinigt Label-Text."""
    # Entferne Werte und Einheiten am Ende
    text = re.sub(r'\s*[:=]\s*[\d.,]+\s*%?\s*$', '', text)
    text = re.sub(r'\s*\([\d.,]+\s*%?\)\s*$', '', text)
    text = re.sub(r'\s*–\s*[\d.,]+\s*$', '', text)
    # Entferne Bullet-Zeichen
    text = re.sub(r'^[-•●○▪\d.)\s]+', '', text)
    return text.strip()


def categorize_item(text: str) -> str:
    """Kategorisiert ein Item basierend auf Keywords."""
    text_lower = text.lower()
    for category, data in CATEGORY_KEYWORDS.items():
        for keyword in data['keywords']:
            if keyword in text_lower:
                return category
    return 'unknown'


def categorize_group(name: str, items: List[ExtractedItem]) -> str:
    """Kategorisiert eine Gruppe basierend auf Name und Items."""
    name_lower = name.lower()
    
    # Erst nach Gruppenname
    for category, data in CATEGORY_KEYWORDS.items():
        for keyword in data['keywords']:
            if keyword in name_lower:
                return category
    
    # Dann nach Item-Kategorien (Mehrheit)
    if items:
        category_counts = defaultdict(int)
        for item in items:
            category_counts[item.category] += 1
        
        if category_counts:
            most_common = max(category_counts.items(), key=lambda x: x[1])
            if most_common[1] >= len(items) * 0.3:  # Mind. 30% gleiche Kategorie
                return most_common[0]
    
    return 'unknown'


def contains_category_keyword(text: str) -> bool:
    """Prüft ob Text ein Kategorie-Keyword enthält."""
    text_lower = text.lower()
    for data in CATEGORY_KEYWORDS.values():
        for keyword in data['keywords']:
            if keyword in text_lower:
                return True
    return False


def advanced_pdf_import(pdf_path: str, use_ocr: bool = True) -> ImportResult:
    """
    Führt erweiterten PDF-Import mit struktureller Analyse durch.
    Nutzt automatisch OCR für Bild-basierte PDFs.
    
    Args:
        pdf_path: Pfad zur PDF-Datei
        use_ocr: OCR für Bild-PDFs nutzen (Standard: True)
    """
    if not PYMUPDF_AVAILABLE:
        raise ImportError("PyMuPDF nicht installiert")
    
    doc = fitz.open(pdf_path)
    
    result = ImportResult(
        source_file=pdf_path,
        extracted_at=datetime.now().isoformat(),
        total_pages=len(doc)
    )
    
    # Volltext extrahieren
    full_text = ""
    for page in doc:
        full_text += page.get_text() + "\n"
    
    # Prüfen ob OCR benötigt wird
    ocr_used = False
    if use_ocr and len(full_text.strip()) < 100 * len(doc):
        # Wenig Text pro Seite = wahrscheinlich Bild-PDF
        if OCR_AVAILABLE:
            doc.close()
            full_text = extract_text_with_ocr(pdf_path)
            ocr_used = True
            doc = fitz.open(pdf_path)  # Wieder öffnen für Metadaten
    
    # Metadaten extrahieren
    result.metadata = {
        'title': doc.metadata.get('title', ''),
        'author': doc.metadata.get('author', ''),
        'subject': doc.metadata.get('subject', ''),
        'creator': doc.metadata.get('creator', ''),
        'text_length': len(full_text),
        'ocr_used': ocr_used,
        'ocr_available': OCR_AVAILABLE
    }
    
    doc.close()
    
    # Strukturierte Listen extrahieren
    result.groups = extract_structured_lists(full_text)
    
    # Tabellen extrahieren und zu Gruppen konvertieren
    try:
        tables = extract_tables_from_pdf(pdf_path)
        table_groups = convert_tables_to_groups(tables)
        result.groups.extend(table_groups)
    except Exception:
        pass  # Tabellen-Extraktion ist optional
    
    # Duplikate entfernen und zusammenführen
    result.groups = merge_similar_groups(result.groups)
    
    # Konfidenz berechnen
    for group in result.groups:
        group.confidence = calculate_group_confidence(group)
    
    # Qualitäts-Score berechnen
    total_items = sum(len(g.items) for g in result.groups)
    categorized_items = sum(
        len([i for i in g.items if i.category != 'unknown'])
        for g in result.groups
    )
    
    if total_items > 0:
        result.quality_score = categorized_items / total_items
    
    # Vorschläge generieren
    result.suggestions = generate_import_suggestions(result)
    
    return result


def convert_tables_to_groups(tables: List[Dict]) -> List[ExtractedGroup]:
    """Konvertiert extrahierte Tabellen zu Gruppen."""
    groups = []
    current_header = None
    current_items = []
    
    for table in tables:
        cols = table['columns']
        
        # Prüfe ob Überschrift
        if len(cols) == 1 or (len(cols) >= 1 and cols[0] and not cols[0][0].isdigit()):
            if current_header and current_items:
                groups.append(ExtractedGroup(
                    name=current_header,
                    items=current_items,
                    category=categorize_group(current_header, current_items)
                ))
            current_header = cols[0]
            current_items = []
        elif len(cols) >= 2:
            # Datenzeile
            label = cols[0]
            value = None
            if len(cols) > 1:
                try:
                    value = float(cols[1].replace(',', '.').replace('%', ''))
                except ValueError:
                    pass
            
            if label:
                item = ExtractedItem(
                    label=clean_label(label),
                    value=value,
                    category=categorize_item(label)
                )
                current_items.append(item)
    
    # Letzte Gruppe
    if current_header and current_items:
        groups.append(ExtractedGroup(
            name=current_header,
            items=current_items,
            category=categorize_group(current_header, current_items)
        ))
    
    return groups


def merge_similar_groups(groups: List[ExtractedGroup]) -> List[ExtractedGroup]:
    """Führt ähnliche Gruppen zusammen."""
    merged = {}
    
    for group in groups:
        # Normalisiere Gruppennamen
        key = re.sub(r'[^a-zäöüß]', '', group.name.lower())
        
        if key in merged:
            # Füge Items hinzu
            existing_labels = {i.label.lower() for i in merged[key].items}
            for item in group.items:
                if item.label.lower() not in existing_labels:
                    merged[key].items.append(item)
                    existing_labels.add(item.label.lower())
        else:
            merged[key] = group
    
    return list(merged.values())


def calculate_group_confidence(group: ExtractedGroup) -> float:
    """Berechnet Konfidenz-Score für eine Gruppe."""
    if not group.items:
        return 0.0
    
    score = 0.5  # Basis
    
    # Mehr Items = höhere Konfidenz
    score += min(0.2, len(group.items) * 0.02)
    
    # Kategorisierte Items erhöhen Konfidenz
    categorized = sum(1 for i in group.items if i.category != 'unknown')
    score += (categorized / len(group.items)) * 0.2
    
    # Werte vorhanden erhöht Konfidenz
    with_values = sum(1 for i in group.items if i.value is not None)
    score += (with_values / len(group.items)) * 0.1
    
    return min(1.0, score)


def generate_import_suggestions(result: ImportResult) -> List[Dict]:
    """Generiert Vorschläge basierend auf Import-Ergebnis."""
    suggestions = []
    
    for group in result.groups:
        if len(group.items) >= 3 and group.confidence >= 0.5:
            # Generiere Gruppen-Namen
            suffix = CATEGORY_KEYWORDS.get(group.category, {}).get(
                'group_suffix', '_imported_multiplex'
            )
            
            safe_name = re.sub(r'[^a-z0-9_]', '_', group.name.lower())
            group_name = f"{safe_name}{suffix}"
            
            suggestions.append({
                'type': 'create_group',
                'group_name': group_name,
                'category': group.category,
                'item_count': len(group.items),
                'confidence': group.confidence,
                'items': [{'label': i.label, 'value': i.value} for i in group.items],
                'action': f"Erstelle Gruppe '{group_name}' mit {len(group.items)} Items"
            })
    
    # NLS-Database Vorschlag wenn genug Daten
    total_items = sum(len(g.items) for g in result.groups)
    if total_items >= 10:
        suggestions.append({
            'type': 'create_nls_database',
            'name': f"imported_{datetime.now().strftime('%Y%m%d')}",
            'total_items': total_items,
            'groups': len(result.groups),
            'action': f"Erstelle NLS-Datenbank mit {total_items} Items aus {len(result.groups)} Gruppen"
        })
    
    return suggestions


def create_group_from_import(
    group: ExtractedGroup,
    output_folder: Optional[Path] = None
) -> Path:
    """
    Erstellt eine Gruppen-Datei aus importierter Gruppe.
    """
    output_folder = output_folder or GENERATED_GROUPS_FOLDER
    output_folder.mkdir(parents=True, exist_ok=True)
    
    suffix = CATEGORY_KEYWORDS.get(group.category, {}).get(
        'group_suffix', '_imported_multiplex'
    )
    safe_name = re.sub(r'[^a-z0-9_]', '_', group.name.lower())
    filename = f"{safe_name}{suffix}.json"
    
    group_data = {
        'name': group.name,
        'type': 'imported',
        'category': group.category,
        'created_at': datetime.now().isoformat(),
        'source': group.source_section,
        'items': [
            {
                'label': item.label,
                'value': item.value,
                'category': item.category
            }
            for item in group.items
        ]
    }
    
    output_path = output_folder / filename
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(group_data, f, indent=2, ensure_ascii=False)
    
    return output_path


def create_nls_database_from_import(
    result: ImportResult,
    db_name: Optional[str] = None,
    output_folder: Optional[Path] = None
) -> Path:
    """
    Erstellt eine NLS-Datenbank aus Import-Ergebnis.
    """
    output_folder = output_folder or NLS_DATABASE_FOLDER
    output_folder.mkdir(parents=True, exist_ok=True)
    
    db_name = db_name or f"imported_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    filename = f"{db_name}.json"
    
    # NLS-Format erstellen
    nls_data = {
        'database_name': db_name,
        'version': '1.0',
        'created_at': datetime.now().isoformat(),
        'source_file': result.source_file,
        'quality_score': result.quality_score,
        'groups': {},
        'items': []
    }
    
    item_id = 1
    for group in result.groups:
        group_key = re.sub(r'[^a-z0-9_]', '_', group.name.lower())
        nls_data['groups'][group_key] = {
            'name': group.name,
            'category': group.category,
            'item_count': len(group.items)
        }
        
        for item in group.items:
            nls_data['items'].append({
                'id': item_id,
                'label': item.label,
                'group': group_key,
                'category': item.category,
                'value': item.value,
                'rates': generate_rates_for_item(item)
            })
            item_id += 1
    
    output_path = output_folder / filename
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(nls_data, f, indent=2, ensure_ascii=False)
    
    return output_path


def generate_rates_for_item(item: ExtractedItem) -> List[float]:
    """
    Generiert Rate-Werte für ein Item basierend auf Kategorie.
    """
    import hashlib
    
    # Deterministischer Hash für konsistente Werte
    hash_input = f"{item.label}_{item.category}".encode()
    hash_bytes = hashlib.sha256(hash_input).digest()
    
    # Generiere 8 Rate-Werte zwischen 0 und 100
    rates = []
    for i in range(8):
        byte_val = hash_bytes[i]
        rate = (byte_val / 255) * 100
        rates.append(round(rate, 2))
    
    return rates


def get_import_status() -> Dict:
    """Gibt Status der Import-Funktionen zurück."""
    folders = ensure_import_folders()
    
    # Zähle vorhandene Dateien
    import_files = list(IMPORT_FOLDER.glob('*.pdf')) if IMPORT_FOLDER.exists() else []
    generated_groups = list(GENERATED_GROUPS_FOLDER.glob('*.json')) if GENERATED_GROUPS_FOLDER.exists() else []
    nls_databases = list(NLS_DATABASE_FOLDER.glob('*.json')) if NLS_DATABASE_FOLDER.exists() else []
    
    return {
        'pymupdf_available': PYMUPDF_AVAILABLE,
        'ocr_available': OCR_AVAILABLE,
        'folders': folders,
        'pending_imports': len(import_files),
        'generated_groups': len(generated_groups),
        'nls_databases': len(nls_databases),
        'import_files': [f.name for f in import_files[:10]],  # Max 10 anzeigen
        'install_hints': {
            'ocr': 'pip install pytesseract Pillow' if not OCR_AVAILABLE else None,
            'tesseract': 'Tesseract OCR installieren: https://github.com/tesseract-ocr/tesseract'
        }
    }
