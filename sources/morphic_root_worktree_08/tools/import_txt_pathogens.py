"""
Pathogen-Import Tool

Importiert Pathogene aus #K TXT-Files in die Pathogen-Datenbank.
Format: "Kohärente Harmonisierung von [Pathogen]"
"""

import sys
from pathlib import Path
import re

# Füge Parent-Verzeichnis zum Path hinzu
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.remedy_service import add_pathogen, get_remedy_stats, init_remedy_database


# Pfad zu den Datenbanken
DB_PATH = Path(__file__).parent.parent / "imports" / "Datenbanken"


def detect_encoding(file_path):
    """Erkennt das Encoding einer Datei."""
    encodings = ['utf-8', 'windows-1252', 'iso-8859-1', 'cp1252', 'latin1']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                f.read()
                return encoding
        except:
            continue
    
    return 'iso-8859-1'  # Fallback


def parse_pathogen_line(line, file_type):
    """
    Parst eine Zeile aus einer Pathogen-Datei.
    
    Format-Varianten:
    1. "Kategorie: Name (Details)"
    2. "Kategorie: Name: Details"
    
    Returns:
        (name, pathogen_type, indication, keywords) oder None
    """
    line = line.strip()
    
    if not line or line.startswith('#'):
        return None
    
    # Entferne führende Marker
    line = re.sub(r'^[-•*]\s*', '', line)
    
    # Erkenne Pathogen-Typ aus Zeile
    pathogen_type = file_type
    
    # Variante 1: "Kategorie: Name (Details)"
    if ':' in line:
        parts = line.split(':', 1)
        category_prefix = parts[0].strip()
        rest = parts[1].strip() if len(parts) > 1 else ''
        
        # Extrahiere Name und Details
        if '(' in rest:
            name_part = rest.split('(')[0].strip()
            details_part = rest.split('(')[1].split(')')[0].strip() if ')' in rest else ''
        else:
            name_part = rest
            details_part = ''
        
        # Erstelle "Kohärente Harmonisierung von" Name
        full_name = f'Kohärente Harmonisierung von {name_part}'
        
        # Extrahiere Keywords
        keywords = extract_pathogen_keywords(name_part, details_part, pathogen_type)
        
        return (full_name, pathogen_type, details_part, keywords)
    
    # Fallback: Ganze Zeile als Name
    else:
        full_name = f'Kohärente Harmonisierung von {line}'
        keywords = extract_pathogen_keywords(line, '', pathogen_type)
        return (full_name, pathogen_type, '', keywords)


def extract_pathogen_keywords(name, indication, pathogen_type):
    """
    Extrahiert Keywords aus Pathogen-Name und Indikation.
    
    Returns:
        Liste von Keywords
    """
    keywords = []
    
    # Name-basierte Keywords
    name_lower = name.lower()
    
    # Splitte in Wörter
    words = re.split(r'[\s\-_,()]+', name_lower)
    keywords.extend([w for w in words if len(w) > 2])
    
    # Pathogen-Typ
    keywords.append(pathogen_type)
    
    # Indikations-basierte Keywords
    if indication:
        ind_lower = indication.lower()
        ind_words = re.split(r'[\s\-_,()]+', ind_lower)
        keywords.extend([w for w in ind_words if len(w) > 3])
    
    # Dedupliziere und filtere
    keywords = list(set(keywords))
    keywords = [k for k in keywords if len(k) > 2 and k not in ['und', 'der', 'die', 'das', 'für', 'mit', 'bei', 'von', 'typ']]
    
    return keywords


def categorize_pathogen_file(filename):
    """
    Bestimmt Pathogen-Typ und Kategorie basierend auf Dateinamen.
    
    Returns:
        (pathogen_type, category)
    """
    name_lower = filename.lower()
    
    if 'bakterien' in name_lower:
        return ('bakterien', 'Kohärente Harmonisierung von Bakterien')
    elif 'viren' in name_lower or 'virus' in name_lower:
        return ('viren', 'Kohärente Harmonisierung von Viren')
    elif 'pilz' in name_lower:
        return ('pilze', 'Kohärente Harmonisierung von Pilzen')
    elif 'parasit' in name_lower:
        return ('parasiten', 'Kohärente Harmonisierung von Parasiten')
    elif 'infekt' in name_lower:
        # Gemischte Infektionen - erkenne aus Zeile
        return ('infektionen', 'Kohärente Harmonisierung von Infektionen')
    else:
        return ('sonstige', 'Kohärente Harmonisierung von Pathogenen')


def import_pathogen_file(file_path, dry_run=False, seen_names=None):
    """
    Importiert Pathogene aus einer TXT-Datei mit Duplikate-Filter.
    
    Args:
        file_path: Pfad zur Datei
        dry_run: Wenn True, nur analysieren ohne Import
        seen_names: Set von bereits gesehenen Namen
    
    Returns:
        (success_count, error_count, skipped_count, duplicate_count)
    """
    if seen_names is None:
        seen_names = set()
    
    encoding = detect_encoding(file_path)
    pathogen_type, category = categorize_pathogen_file(file_path.name)
    
    success_count = 0
    error_count = 0
    skipped_count = 0
    duplicate_count = 0
    
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            lines = f.readlines()
        
        for line in lines:
            parsed = parse_pathogen_line(line, pathogen_type)
            
            if not parsed:
                skipped_count += 1
                continue
            
            name, ptype, indication, keywords = parsed
            
            # Duplikate-Filter
            if name in seen_names:
                duplicate_count += 1
                continue
            
            seen_names.add(name)
            
            # Für gemischte Infektionen: Erkenne Typ aus Zeile
            if ptype == 'infektionen':
                if '(pilz)' in line.lower() or 'pilz:' in line.lower():
                    ptype = 'pilze'
                    category = 'Kohärente Harmonisierung von Pilzen'
                elif '(parasit)' in line.lower() or 'parasit:' in line.lower():
                    ptype = 'parasiten'
                    category = 'Kohärente Harmonisierung von Parasiten'
                elif '(bakterien)' in line.lower() or 'bakterium' in line.lower():
                    ptype = 'bakterien'
                    category = 'Kohärente Harmonisierung von Bakterien'
                elif '(viren)' in line.lower() or 'virus' in line.lower():
                    ptype = 'viren'
                    category = 'Kohärente Harmonisierung von Viren'
            
            if dry_run:
                success_count += 1
            else:
                try:
                    add_pathogen(
                        name=name,
                        pathogen_type=ptype,
                        category=category,
                        indication=indication[:500] if indication else '',
                        keywords=keywords
                    )
                    success_count += 1
                
                except Exception as e:
                    if 'UNIQUE constraint' in str(e):
                        duplicate_count += 1
                    else:
                        error_count += 1
                        print(f"      ⚠️  Fehler bei '{name}': {e}")
    
    except Exception as e:
        print(f"    ❌ Datei-Fehler: {e}")
        return (0, 1, 0, 0)
    
    return (success_count, error_count, skipped_count, duplicate_count)


def import_all_pathogen_files(dry_run=False):
    """
    Importiert alle Pathogen-Dateien (#K).
    
    Args:
        dry_run: Wenn True, nur analysieren ohne Import
    """
    print("=" * 70)
    print("PATHOGEN-IMPORT AUS TXT-FILES")
    print("=" * 70)
    print()
    
    if dry_run:
        print("🔍 DRY-RUN-MODUS (kein Import)")
        print()
    
    # Statistiken vor Import
    stats_before = get_remedy_stats()
    print(f"Vor Import: {stats_before.get('total_pathogens', 0)} Pathogene in DB")
    print()
    
    # Finde alle #K Dateien (Körper/Infektionen)
    pathogen_files = [
        DB_PATH / "#K Bakterien T.txt",
        DB_PATH / "#K Viren.txt",
        DB_PATH / "#K Pilze T.txt",
        DB_PATH / "#K Parasiten T.txt",
        DB_PATH / "#K Infektionen T.txt"
    ]
    
    # Filtere existierende Dateien
    pathogen_files = [f for f in pathogen_files if f.exists()]
    
    if not pathogen_files:
        print("❌ Keine Pathogen-Dateien gefunden!")
        return
    
    print(f"Gefunden: {len(pathogen_files)} Pathogen-Dateien")
    print()
    
    total_success = 0
    total_errors = 0
    total_skipped = 0
    total_duplicates = 0
    seen_names = set()
    
    for file_path in pathogen_files:
        print(f"📄 {file_path.name}")
        
        success, errors, skipped, duplicates = import_pathogen_file(file_path, dry_run, seen_names)
        
        total_success += success
        total_errors += errors
        total_skipped += skipped
        total_duplicates += duplicates
        
        print(f"   ✅ {success} importiert, ⚠️ {errors} Fehler, ⏭️ {skipped} übersprungen, 🔄 {duplicates} Duplikate")
    
    print()
    print("=" * 70)
    print("IMPORT ABGESCHLOSSEN")
    print("=" * 70)
    print(f"Gesamt importiert: {total_success}")
    print(f"Gesamt Fehler: {total_errors}")
    print(f"Gesamt übersprungen: {total_skipped}")
    print(f"Gesamt Duplikate: {total_duplicates}")
    print()
    
    if not dry_run:
        # Statistiken nach Import
        stats_after = get_remedy_stats()
        print(f"Nach Import: {stats_after.get('total_pathogens', 0)} Pathogene in DB")
        print(f"Neu hinzugefügt: {stats_after.get('total_pathogens', 0) - stats_before.get('total_pathogens', 0)}")
        print()
        
        if stats_after.get('pathogens_by_type'):
            print("Nach Typ:")
            for ptype, count in sorted(stats_after['pathogens_by_type'].items(), key=lambda x: -x[1]):
                print(f"  {ptype}: {count}")
    
    print("=" * 70)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Importiert Pathogene aus TXT-Files')
    parser.add_argument('--dry-run', action='store_true', help='Nur analysieren, nicht importieren')
    
    args = parser.parse_args()
    
    # Initialisiere DB
    init_remedy_database()
    
    # Importiere
    import_all_pathogen_files(dry_run=args.dry_run)
