"""
Analyse-Skript für Remedy TXT-Files

Analysiert die TXT-Files im imports/Datenbanken Ordner und gibt eine Übersicht.
"""

import os
from pathlib import Path
from collections import defaultdict
import chardet


# Pfad zu den Datenbanken
DB_PATH = Path(__file__).parent.parent / "imports" / "Datenbanken"


def detect_encoding(file_path):
    """Erkennt das Encoding einer Datei."""
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            return result['encoding']
    except:
        return None


def read_file_with_encoding(file_path):
    """Liest eine Datei mit automatischer Encoding-Erkennung."""
    encodings = ['utf-8', 'windows-1252', 'iso-8859-1', 'cp1252', 'latin1']
    
    # Versuche chardet
    detected = detect_encoding(file_path)
    if detected:
        encodings.insert(0, detected)
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                return content, encoding
        except:
            continue
    
    return None, None


def analyze_file_structure(content):
    """Analysiert die Struktur einer Datei."""
    lines = content.strip().split('\n')
    
    # Zähle nicht-leere Zeilen
    non_empty = [l.strip() for l in lines if l.strip()]
    
    # Erkenne Struktur
    has_tabs = any('\t' in l for l in non_empty)
    has_semicolons = any(';' in l for l in non_empty)
    has_pipes = any('|' in l for l in non_empty)
    
    # Sample-Zeilen
    sample = non_empty[:5] if len(non_empty) >= 5 else non_empty
    
    return {
        'total_lines': len(lines),
        'non_empty_lines': len(non_empty),
        'has_tabs': has_tabs,
        'has_semicolons': has_semicolons,
        'has_pipes': has_pipes,
        'sample': sample
    }


def main():
    print("=" * 70)
    print("REMEDY-FILES ANALYSE")
    print("=" * 70)
    print()
    
    if not DB_PATH.exists():
        print(f"❌ Pfad nicht gefunden: {DB_PATH}")
        return
    
    # Kategorisiere nach Präfix
    categories = defaultdict(list)
    
    for file_path in DB_PATH.glob("*.txt"):
        name = file_path.name
        
        # Erkenne Präfix
        if name.startswith('#M '):
            category = 'Mittel/Remedies'
        elif name.startswith('#K '):
            category = 'Körper/Anatomie'
        elif name.startswith('#P '):
            category = 'Psyche/Emotion'
        elif name.startswith('#E '):
            category = 'Energie'
        elif name.startswith('#U '):
            category = 'Umwelt/Toxine'
        elif name.startswith('#F '):
            category = 'Firma/Business'
        elif name.startswith('#T '):
            category = 'Tiere'
        elif name.startswith('#+ '):
            category = 'Essenzen'
        elif name.startswith('#A '):
            category = 'Ursachen'
        elif name.startswith('#Z '):
            category = 'Sonstiges'
        else:
            category = 'Andere'
        
        categories[category].append(file_path)
    
    # Zeige Übersicht
    print("KATEGORIEN:")
    print()
    for cat, files in sorted(categories.items()):
        print(f"{cat}: {len(files)} Dateien")
    
    print()
    print("=" * 70)
    print("DETAILANALYSE: MITTEL/REMEDIES")
    print("=" * 70)
    print()
    
    # Analysiere Mittel-Dateien im Detail
    remedy_files = categories.get('Mittel/Remedies', [])
    
    for file_path in sorted(remedy_files)[:10]:  # Erste 10
        print(f"\n📄 {file_path.name}")
        print(f"   Größe: {file_path.stat().st_size} bytes")
        
        content, encoding = read_file_with_encoding(file_path)
        
        if content:
            print(f"   Encoding: {encoding}")
            
            structure = analyze_file_structure(content)
            print(f"   Zeilen: {structure['non_empty_lines']}")
            print(f"   Format: ", end="")
            
            if structure['has_tabs']:
                print("Tab-separiert", end="")
            if structure['has_semicolons']:
                print("Semikolon-separiert", end="")
            if structure['has_pipes']:
                print("Pipe-separiert", end="")
            
            print()
            print(f"   Sample:")
            for i, line in enumerate(structure['sample'][:3], 1):
                preview = line[:80] + "..." if len(line) > 80 else line
                print(f"     {i}. {preview}")
        else:
            print(f"   ❌ Konnte nicht gelesen werden")
    
    print()
    print("=" * 70)
    print("DETAILANALYSE: KÖRPER/ANATOMIE (Infektionen)")
    print("=" * 70)
    print()
    
    # Analysiere Infektions-Dateien
    body_files = categories.get('Körper/Anatomie', [])
    infection_files = [f for f in body_files if 'Infekt' in f.name or 'Bakterien' in f.name or 'Viren' in f.name or 'Pilz' in f.name or 'Parasit' in f.name]
    
    for file_path in sorted(infection_files)[:5]:
        print(f"\n📄 {file_path.name}")
        print(f"   Größe: {file_path.stat().st_size} bytes")
        
        content, encoding = read_file_with_encoding(file_path)
        
        if content:
            print(f"   Encoding: {encoding}")
            
            structure = analyze_file_structure(content)
            print(f"   Zeilen: {structure['non_empty_lines']}")
            print(f"   Sample:")
            for i, line in enumerate(structure['sample'][:3], 1):
                preview = line[:80] + "..." if len(line) > 80 else line
                print(f"     {i}. {preview}")
    
    print()
    print("=" * 70)
    print("EMPFEHLUNG")
    print("=" * 70)
    print()
    print("Basierend auf der Analyse:")
    print("1. Mittel/Remedies-Dateien enthalten homöopathische Mittel")
    print("2. Körper/Anatomie-Dateien enthalten Infektionen/Pathogene")
    print("3. Format ist vermutlich Tab- oder Semikolon-separiert")
    print()
    print("Nächster Schritt:")
    print("- Detaillierte Struktur-Analyse einer Beispiel-Datei")
    print("- Migrations-Strategie entwickeln")
    print()


if __name__ == "__main__":
    main()
