"""
Test: Multiplex-Scanner mit Nutramedix-Mitteln
Simuliert verschiedene Pathogen-/Symptom-Szenarien und prüft, ob passende Nutramedix-Mittel gefunden werden.
"""

import sys
from pathlib import Path

# Add parent directory to path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from services.remedy_service import find_remedies_for_group, get_remedy_stats

def test_nutramedix_intelligence():
    print("\n" + "="*70)
    print("🧪 NUTRAMEDIX INTELLIGENCE TEST")
    print("="*70)
    
    # Test-Szenarien
    test_cases = [
        ("Borreliose", ["Samento", "Banderol", "Cumanda", "Takuna"]),
        ("Entgiftung", ["Burbur", "Pinella", "Parsley", "Sealantro"]),
        ("Entzündung", ["Quercetin", "Serra Peptase", "Bromelain"]),
        ("Immunsystem", ["Samento", "Elderberry", "Zinc"]),
        ("Parasiten", ["Artemisia", "Cumanda", "Quina"]),
        ("Stress", ["Relaxmedix", "Moodmedix", "Adrenal"]),
        ("Herz-Kreislauf", ["Nattokinase", "Magnesium"]),
        ("Verdauung", ["Chanca Piedra", "Dandelion", "Stevia"])
    ]
    
    total_tests = len(test_cases)
    passed_tests = 0
    
    for i, (search_term, expected_keywords) in enumerate(test_cases, 1):
        print(f"\n[{i}/{total_tests}] Test: '{search_term}'")
        print("-" * 70)
        
        # Suche Remedies
        results = find_remedies_for_group(search_term, max_results=5)
        
        if results:
            print(f"  ✅ {len(results)} Mittel gefunden:")
            for name, category in results:
                print(f"     • {name} ({category})")
                
            # Prüfe, ob mindestens ein erwartetes Keyword im Ergebnis ist
            found_names = [name.lower() for name, _ in results]
            matches = [kw for kw in expected_keywords if any(kw.lower() in fn for fn in found_names)]
            
            if matches:
                print(f"  🎯 Erwartete Treffer: {', '.join(matches)}")
                passed_tests += 1
            else:
                print(f"  ⚠️  Keine erwarteten Treffer (erwartet: {', '.join(expected_keywords)})")
        else:
            print(f"  ❌ Keine Mittel gefunden!")
            print(f"  ⚠️  Erwartet wurden: {', '.join(expected_keywords)}")
    
    # Statistik
    print("\n" + "="*70)
    print(f"📊 TEST-ERGEBNIS: {passed_tests}/{total_tests} Tests bestanden")
    
    # DB-Statistik
    stats = get_remedy_stats()
    print(f"📊 Remedy-DB: {stats['total']} Einträge")
    print("="*70)
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = test_nutramedix_intelligence()
    sys.exit(0 if success else 1)
