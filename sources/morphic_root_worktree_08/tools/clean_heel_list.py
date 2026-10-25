"""
Heel-Listen-Reiniger
Bereinigt die automatisch extrahierte Produktliste von Müll und Artefakten.
"""

import sys
from pathlib import Path
import re

def clean_list(input_file, output_file):
    print(f"\n🧹 Reinige {input_file}...")
    print("=" * 70)
    
    clean_entries = set()
    removed_count = 0
    
    # Muster, die entfernt werden sollen
    blacklist_patterns = [
        r"KOMBINATIONSPRÄPARATE", 
        r"EINZELMITTEL",
        r"REG\.-NR", 
        r"ZUL\.-NR",
        r"^SIEHE\s", 
        r"^INJEEL\s",
        r"ZITRONENSÄUREZYKLUS",
        r"HEUSCHNUPFENSPRAY", # Eher Gattungsbegriff
        r"EINZELPOTENZEN",
        r"^JHOMÖOPATHISCHE",
        r"^KHOMÖOPATHISCHE",
        r"^EHOMÖOPATHISCHE",
        r"^SUIS-INJEEL FORTE", # Eher Einzelmittel-Rest
        r"^HAHNEMANNI-INJEEL",
        r"^PHOSPHORICUM-INJEEL",
        r"^CORROSIVUS-INJEEL",
    ]
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        
        # 1. Leere Zeilen und Kommentare behalten/ignorieren
        if not line or line.startswith('#'):
            continue
            
        # 2. Prüfe Blacklist
        is_bad = False
        for pattern in blacklist_patterns:
            if re.search(pattern, line.upper()):
                is_bad = True
                print(f"❌ Entfernt (Muster): {line}")
                break
        
        if is_bad:
            removed_count += 1
            continue
            
        # 3. Prüfe Länge
        if len(line) < 4:
            is_bad = True
            print(f"❌ Entfernt (zu kurz): {line}")
            removed_count += 1
            continue
            
        # 4. Prüfe auf "nur Großbuchstaben" bei längeren Worten (Kapitelüberschriften oft ALLCAPS)
        # Aber Achtung: Manche Produkte sind ALLCAPS? Eher nicht bei Heel.
        # Wir lassen es erstmal zu, außer es sind offensichtliche Überschriften.
        
        # 5. Spezieller Filter für OCR-Fehler am Anfang (z.B. "SKombinationspräparate")
        if re.match(r'^[A-Z]Kombinationspräparate', line):
            is_bad = True
            print(f"❌ Entfernt (OCR-Fehler): {line}")
            removed_count += 1
            continue

        clean_entries.add(line)
        
    # Sortieren
    sorted_entries = sorted(list(clean_entries))
    
    # Speichern
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Bereinigte Heel-Produktliste\n")
        f.write(f"# Anzahl: {len(sorted_entries)}\n\n")
        for entry in sorted_entries:
            f.write(f"{entry}\n")
            
    print("=" * 70)
    print(f"✅ Fertig! {len(sorted_entries)} Produkte behalten.")
    print(f"🗑️  {removed_count} Einträge entfernt.")
    print(f"💾 Gespeichert in: {output_file}")

if __name__ == "__main__":
    input_path = Path("heel_products.txt")
    output_path = Path("heel_products_clean.txt")
    
    if not input_path.exists():
        print(f"❌ Eingabedatei fehlt: {input_path}")
        sys.exit(1)
        
    clean_list(input_path, output_path)
