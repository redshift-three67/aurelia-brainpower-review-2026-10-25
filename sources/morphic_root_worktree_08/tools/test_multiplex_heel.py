"""
Multiplex Heel Test
Testet, ob der Scanner (Resonance Pipeline) die neuen Heel-Mittel für Pathogene vorschlägt.
"""

import sys
import os
from pathlib import Path

# Sicherstellen, dass wir das Root-Verzeichnis finden
current_dir = Path(__file__).resolve().parent
root_dir = current_dir.parent
sys.path.insert(0, str(root_dir))

# Arbeitsverzeichnis wechseln
os.chdir(root_dir)

from services.remedy_service import get_remedy_connection, find_remedies_for_group

def test_multiplex():
    print("\n🔬 MULTIPLEX SCAN TEST (HEEL FOKUS - DIREKT)")
    print("=" * 70)
    
    # Wir simulieren, was die Pipeline tun würde:
    # Sie nimmt den Pathogen-Namen und fragt find_remedies_for_group()
    
    mock_scan_results = [
        {"name": "Streptococcus pyogenes", "probability": 0.95},
        {"name": "Entzündung akut", "probability": 0.88},
        {"name": "Leber Belastung", "probability": 0.75}
    ]
    
    print("Szenario: Klient hat folgende Resonanzen:")
    for item in mock_scan_results:
        print(f"  🦠 {item['name']} ({int(item['probability']*100)}%)")
        
    print("\n🚀 Starte Analyse (Datenbank-Abfrage)...")
    
    for item in mock_scan_results:
        name = item["name"]
        print(f"\n🔍 Suche Mittel für '{name}'...")
        
        # Hier passiert die Magie: Die DB sucht nach Keywords
        matches = find_remedies_for_group(name, max_results=5)
        
        if matches:
            for remedy, ind in matches:
                # Prüfe Kategorie
                is_heel = False
                desc = ""
                with get_remedy_connection() as conn:
                    c = conn.cursor()
                    c.execute("SELECT category FROM remedies WHERE name = ?", (remedy,))
                    row = c.fetchone()
                    if row and "heel" in row[0].lower():
                        is_heel = True
                        
                marker = "✅ HEEL" if is_heel else "⚪ Andere"
                print(f"   💊 {remedy} [{marker}]")
        else:
            print("   ❌ Keine Treffer")

if __name__ == "__main__":
    test_multiplex()
