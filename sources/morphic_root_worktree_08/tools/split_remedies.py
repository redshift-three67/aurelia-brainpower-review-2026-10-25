"""
Heel Remedy Splitter & Cleaner
Trennt Mehrfachnennungen in einer Zeile und bereinigt Namen.
"""

import re
from pathlib import Path

def clean_and_split(input_file, output_file):
    print(f"\n✂️  Splitte und Reinige {input_file}...")
    print("=" * 70)
    
    clean_remedies = set()
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        # 1. Splitte an Kommas (aber nicht in Klammern!)
        # Einfacher Ansatz: Splitte an Komma, wenn danach ein Großbuchstabe kommt oder "Acidum" etc.
        parts = re.split(r',\s*(?=[A-Z])', line)
        
        for part in parts:
            part = part.strip()
            
            # Entferne Punkte am Ende
            if part.endswith('.'):
                part = part[:-1]
                
            # Entferne Synonyme in Klammern am Ende, wenn der Name lang genug ist
            # "Acidum arsenicosum (Arsenicum album)" -> "Acidum arsenicosum"
            # Aber behalte "Vitamin C"
            if '(' in part:
                # Prüfe ob es wie ein Synonym aussieht (am Ende)
                match = re.match(r'^(.*?)\s*\([A-Za-z\s-]+\)$', part)
                if match:
                    clean_part = match.group(1)
                    if len(clean_part) > 3:
                        part = clean_part

            # Filter: Zu kurz?
            if len(part) < 4:
                continue
                
            clean_remedies.add(part)

    # Sortieren
    sorted_remedies = sorted(list(clean_remedies))
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Bereinigte Heel Deep Scan Liste\n")
        f.write(f"# Anzahl: {len(sorted_remedies)}\n\n")
        for r in sorted_remedies:
            f.write(f"{r}\n")
            
    print(f"✅ Fertig. {len(sorted_remedies)} saubere Einzelmittel.")
    print(f"💾 Gespeichert in: {output_file}")

if __name__ == "__main__":
    clean_and_split("heel_deep_scan.txt", "heel_deep_scan_clean.txt")
