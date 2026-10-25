"""
Heel Reality Check
Testet, ob die Heel-Mittel gefunden werden - sowohl über Namen als auch über Kontext.
"""

import sys
from pathlib import Path

# Add parent directory to path to find 'services'
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.remedy_service import find_remedies_for_group, get_remedy_stats, get_remedy_connection

def test_search(query, comment):
    print(f"\n🔎 TEST: '{query}' ({comment})")
    print("-" * 60)
    
    # Wir nutzen die Service-Funktion, die auch Keywords prüft
    # Da find_remedies_for_group normalerweise Gruppen-Namen erwartet,
    # simulieren wir hier eine Gruppe, die so heißt wie unser Suchbegriff.
    
    results = find_remedies_for_group(query, max_results=10)
    
    if not results:
        print("   ❌ Keine Treffer.")
    else:
        for name, indication in results:
            print(f"   💊 {name}")
            # Hole Beschreibung für Details
            with get_remedy_connection() as conn:
                c = conn.cursor()
                c.execute("SELECT description FROM remedy_descriptions WHERE remedy_id = (SELECT id FROM remedies WHERE name = ?)", (name,))
                row = c.fetchone()
                desc = row[0] if row else "Keine Beschreibung"
                print(f"      📝 {desc[:80]}...")

def main():
    print("🏥 HEEL SYSTEM DIAGNOSE")
    print("=" * 60)
    
    # 1. Statistik
    stats = get_remedy_stats()
    print(f"📊 Bestand: {stats['total_remedies']} Mittel in der Datenbank.")
    
    # 2. Test: Direkte Namenssuche (Muss funktionieren)
    test_search("Traumeel", "Suche nach Name")
    test_search("Acidum", "Suche nach Inhaltsstoff (Deep Scan)")
    
    # 3. Test: Logik-Suche (Der Härtetest)
    # Funktioniert nur, wenn 'Indikationen' als Keywords gespeichert wurden
    test_search("Entzündung", "Suche nach Indikation (Hidden Logic)")
    test_search("Leber", "Suche nach Organbezug")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
