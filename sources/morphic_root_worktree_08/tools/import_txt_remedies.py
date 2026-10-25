"""
TXT-Remedy-Import Tool

Importiert Remedies aus TXT-Files in die Remedy-Datenbank.
Unterstützt verschiedene Formate und Kategorien.
"""

import sys
from pathlib import Path
import re

# Füge Parent-Verzeichnis zum Path hinzu
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.remedy_service import add_remedy, get_remedy_stats, init_remedy_database


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


def parse_remedy_line(line, file_category):
    """
    Parst eine Zeile aus einer Remedy-Datei.
    
    Format-Varianten:
    1. "Kategorie: Name: Beschreibung" → "Kohärente Harmonisierung mit Name"
    2. "Name: Beschreibung" → "Kohärente Harmonisierung mit Name"
    3. "Name - Beschreibung" → "Kohärente Harmonisierung mit Name"
    
    Returns:
        (name, indication, keywords, category) oder None
    """
    line = line.strip()
    
    if not line or line.startswith('#'):
        return None
    
    # Entferne führende Marker
    line = re.sub(r'^[-•*]\s*', '', line)
    
    # Variante 1: "Kategorie: Name: Beschreibung"
    if line.count(':') >= 2:
        parts = line.split(':', 2)
        category_prefix = parts[0].strip()  # z.B. "Emotionale Homöopathie"
        remedy_name = parts[1].strip()      # z.B. "Abrotanum"
        indication = parts[2].strip() if len(parts) > 2 else ''
        
        # Erstelle "Kohärente Harmonisierung mit" Name
        full_name = f'Kohärente Harmonisierung mit {remedy_name}'
        
        # Extrahiere Keywords
        keywords = extract_keywords(remedy_name, indication, file_category)
        
        return (full_name, indication, keywords, file_category)
    
    # Variante 2: "Name: Beschreibung"
    elif ':' in line:
        parts = line.split(':', 1)
        remedy_name = parts[0].strip()
        indication = parts[1].strip() if len(parts) > 1 else ''
        
        full_name = f'Kohärente Harmonisierung mit {remedy_name}'
        keywords = extract_keywords(remedy_name, indication, file_category)
        
        return (full_name, indication, keywords, file_category)
    
    # Variante 3: "Name - Beschreibung"
    elif ' - ' in line:
        parts = line.split(' - ', 1)
        remedy_name = parts[0].strip()
        indication = parts[1].strip() if len(parts) > 1 else ''
        
        full_name = f'Kohärente Harmonisierung mit {remedy_name}'
        keywords = extract_keywords(remedy_name, indication, file_category)
        
        return (full_name, indication, keywords, file_category)
    
    # Fallback: Ganze Zeile als Name
    else:
        full_name = f'Kohärente Harmonisierung mit {line}'
        keywords = extract_keywords(line, '', file_category)
        return (full_name, '', keywords, file_category)


def extract_keywords(name, indication, category):
    """
    Extrahiert Keywords aus Name, Indikation und Kategorie.
    
    Returns:
        Liste von Keywords
    """
    keywords = []
    
    # Name-basierte Keywords
    name_lower = name.lower()
    
    # Entferne Potenzen (C200, D6, etc.)
    name_clean = re.sub(r'\s+[cd]\d+', '', name_lower)
    name_clean = re.sub(r'\s+\d+[xc]', '', name_clean)
    
    # Splitte in Wörter
    words = re.split(r'[\s\-_,()]+', name_clean)
    keywords.extend([w for w in words if len(w) > 2])
    
    # Kategorie-basierte Keywords
    if category:
        cat_lower = category.lower()
        cat_words = re.split(r'[\s\-_,()]+', cat_lower)
        keywords.extend([w for w in cat_words if len(w) > 2])
    
    # Indikations-basierte Keywords (wichtigste Wörter)
    if indication:
        ind_lower = indication.lower()
        
        # Erkenne wichtige Begriffe
        important_terms = [
            'bakterien', 'viren', 'pilz', 'parasit',
            'borreliose', 'herpes', 'candida', 'streptokokken',
            'schmerz', 'entzündung', 'verletzung', 'trauma',
            'angst', 'depression', 'stress', 'schlaf',
            'leber', 'niere', 'herz', 'darm',
            'immun', 'entgiftung', 'hormone'
        ]
        
        for term in important_terms:
            if term in ind_lower:
                keywords.append(term)
    
    # Dedupliziere und filtere
    keywords = list(set(keywords))
    keywords = [k for k in keywords if len(k) > 2 and k not in ['und', 'der', 'die', 'das', 'für', 'mit', 'bei']]
    
    return keywords


def categorize_file(filename):
    """
    Bestimmt die beschreibende Kategorie basierend auf Dateinamen.
    Format: "Kohärente Harmonisierung mit [Kategorie]"
    
    Returns:
        Kategorie-String
    """
    name_lower = filename.lower()
    
    # Entferne Präfix #M
    clean_name = filename.replace('#M ', '').replace('.txt', '')
    
    # Homöopathie
    if 'homöop' in name_lower:
        if 'nosode' in name_lower:
            return f'Kohärente Harmonisierung mit Nosoden'
        elif 'seelen' in name_lower:
            return f'Kohärente Harmonisierung mit Homöopathischer Seelenregeneration'
        else:
            return f'Kohärente Harmonisierung mit Homöopathischen Mitteln'
    
    # Bachblüten
    elif 'bach' in name_lower:
        return f'Kohärente Harmonisierung mit Bachblüten'
    
    # Schüssler
    elif 'schüssler' in name_lower:
        return f'Kohärente Harmonisierung mit Schüssler-Salzen'
    
    # Spezifische Essenzen
    elif 'alaska' in name_lower:
        return f'Kohärente Harmonisierung mit Alaska Flower Essenzen'
    elif 'california' in name_lower:
        return f'Kohärente Harmonisierung mit California Flower Essenzen'
    elif 'australisch' in name_lower or 'busch' in name_lower:
        return f'Kohärente Harmonisierung mit Australischen Buschblüten'
    elif 'himalaya' in name_lower:
        return f'Kohärente Harmonisierung mit Himalaya Essenzen'
    elif 'arizona' in name_lower or 'wüste' in name_lower:
        return f'Kohärente Harmonisierung mit Arizona Wüstenessenzen'
    elif 'hawaii' in name_lower or 'aloha' in name_lower:
        return f'Kohärente Harmonisierung mit Aloha Hawaii Essenzen'
    elif 'buddhafield' in name_lower:
        return f'Kohärente Harmonisierung mit Buddhafield Flower Essenzen'
    elif 'living' in name_lower:
        return f'Kohärente Harmonisierung mit Living Essenzen'
    elif 'orchidee' in name_lower:
        return f'Kohärente Harmonisierung mit Orchideen-Essenzen'
    elif 'pilz' in name_lower and 'essenz' in name_lower:
        return f'Kohärente Harmonisierung mit Pilz-Essenzen'
    elif 'meer' in name_lower:
        return f'Kohärente Harmonisierung mit Meeresessenzen'
    elif 'baum' in name_lower:
        return f'Kohärente Harmonisierung mit Baumblüten-Essenzen'
    elif 'rose' in name_lower:
        return f'Kohärente Harmonisierung mit Rosenessenzen'
    elif 'wildpflanze' in name_lower:
        return f'Kohärente Harmonisierung mit Wildpflanzen Essenzen'
    elif 'garten' in name_lower:
        return f'Kohärente Harmonisierung mit Gartenessenzen'
    elif 'essenz' in name_lower or 'flower' in name_lower:
        return f'Kohärente Harmonisierung mit Blütenessenzen'
    
    # Kräuter
    elif 'kräuter' in name_lower or 'kraeuter' in name_lower:
        if 'chinesisch' in name_lower:
            return f'Kohärente Harmonisierung mit Chinesischen Kräutern'
        else:
            return f'Kohärente Harmonisierung mit Kräutern'
    
    # Edelsteine
    elif 'edelstein' in name_lower or 'heilstein' in name_lower:
        return f'Kohärente Harmonisierung mit Edelsteinen'
    
    # Spagyrik
    elif 'spagyr' in name_lower:
        return f'Kohärente Harmonisierung mit Spagyrischen Essenzen'
    
    # Aromatherapie
    elif 'aroma' in name_lower or 'öl' in name_lower:
        return f'Kohärente Harmonisierung mit Aromatherapie'
    
    # Emotionale Mittel
    elif 'emotion' in name_lower:
        return f'Kohärente Harmonisierung mit Emotionaler Homöopathie'
    
    # Mistel
    elif 'mistel' in name_lower:
        return f'Kohärente Harmonisierung mit Misteltherapie'
    
    # Spinnengifte
    elif 'spinne' in name_lower:
        return f'Kohärente Harmonisierung mit Spinnengiften'
    
    # Zähne
    elif 'zähn' in name_lower or 'zahn' in name_lower:
        return f'Kohärente Harmonisierung mit Zähne-Mitteln'
    
    # Wetter
    elif 'wetter' in name_lower:
        return f'Kohärente Harmonisierung mit Wetter-Emotionen'
    
    # Phyto
    elif 'phyto' in name_lower:
        return f'Kohärente Harmonisierung mit Phytomitteln'
    
    # Tinkturen
    elif 'tinktur' in name_lower:
        return f'Kohärente Harmonisierung mit Pflanzen-Tinkturen'
    
    # Schutz
    elif 'schutz' in name_lower:
        return f'Kohärente Harmonisierung mit Schutzmitteln'
    
    # Heilmittel (allgemein)
    elif 'heilmittel' in name_lower:
        return f'Kohärente Harmonisierung mit Heilmitteln'
    
    # Default: Verwende Dateinamen
    else:
        return f'Kohärente Harmonisierung mit {clean_name}'


def import_remedy_file(file_path, dry_run=False, seen_names=None):
    """
    Importiert Remedies aus einer TXT-Datei mit Duplikate-Filter.
    
    Args:
        file_path: Pfad zur Datei
        dry_run: Wenn True, nur analysieren ohne Import
        seen_names: Set von bereits gesehenen Namen (Duplikate-Filter)
    
    Returns:
        (success_count, error_count, skipped_count, duplicate_count)
    """
    if seen_names is None:
        seen_names = set()
    
    encoding = detect_encoding(file_path)
    category = categorize_file(file_path.name)
    
    success_count = 0
    error_count = 0
    skipped_count = 0
    duplicate_count = 0
    
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            lines = f.readlines()
        
        for line in lines:
            parsed = parse_remedy_line(line, category)
            
            if not parsed:
                skipped_count += 1
                continue
            
            name, indication, keywords, cat = parsed
            
            # Duplikate-Filter: Prüfe ob Name bereits existiert
            if name in seen_names:
                duplicate_count += 1
                continue
            
            seen_names.add(name)
            
            # Extrahiere Potenz aus Name
            potency = ''
            potency_match = re.search(r'([CD]\d+|N|\d+[XC])', name)
            if potency_match:
                potency = potency_match.group(1)
            
            if dry_run:
                success_count += 1
            else:
                try:
                    add_remedy(
                        name=name,
                        potency=potency,
                        category=cat,
                        indication=indication[:500] if indication else '',  # Limit
                        keywords=keywords
                    )
                    success_count += 1
                
                except Exception as e:
                    # UNIQUE constraint = Duplikat in DB (nicht in seen_names)
                    if 'UNIQUE constraint' in str(e):
                        duplicate_count += 1
                    else:
                        error_count += 1
                        print(f"      ⚠️  Fehler bei '{name}': {e}")
    
    except Exception as e:
        print(f"    ❌ Datei-Fehler: {e}")
        return (0, 1, 0, 0)
    
    return (success_count, error_count, skipped_count, duplicate_count)


def import_all_remedy_files(dry_run=False):
    """
    Importiert alle Remedy-Dateien.
    
    Args:
        dry_run: Wenn True, nur analysieren ohne Import
    """
    print("=" * 70)
    print("REMEDY-IMPORT AUS TXT-FILES")
    print("=" * 70)
    print()
    
    if dry_run:
        print("🔍 DRY-RUN-MODUS (kein Import)")
        print()
    
    # Statistiken vor Import
    stats_before = get_remedy_stats()
    print(f"Vor Import: {stats_before['total']} Remedies in DB")
    print()
    
    # Finde alle #M Dateien (Mittel/Remedies)
    remedy_files = sorted(DB_PATH.glob("#M *.txt"))
    
    if not remedy_files:
        print("❌ Keine Remedy-Dateien gefunden!")
        return
    
    print(f"Gefunden: {len(remedy_files)} Remedy-Dateien")
    print()
    
    total_success = 0
    total_errors = 0
    total_skipped = 0
    total_duplicates = 0
    seen_names = set()  # Globaler Duplikate-Filter
    
    for file_path in remedy_files:
        print(f"📄 {file_path.name}")
        
        success, errors, skipped, duplicates = import_remedy_file(file_path, dry_run, seen_names)
        
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
        print(f"Nach Import: {stats_after['total']} Remedies in DB")
        print(f"Neu hinzugefügt: {stats_after['total'] - stats_before['total']}")
        print()
        
        if stats_after['by_category']:
            print("Nach Kategorie:")
            for cat, count in sorted(stats_after['by_category'].items(), key=lambda x: -x[1]):
                print(f"  {cat}: {count}")
    
    print("=" * 70)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Importiert Remedies aus TXT-Files')
    parser.add_argument('--dry-run', action='store_true', help='Nur analysieren, nicht importieren')
    
    args = parser.parse_args()
    
    # Initialisiere DB
    init_remedy_database()
    
    # Importiere
    import_all_remedy_files(dry_run=args.dry_run)
