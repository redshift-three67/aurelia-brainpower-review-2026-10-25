"""
Test: Heel & Nutramedix Profile
Testet, ob die neuen Hersteller-Profile korrekt funktionieren.
"""

import sys
from pathlib import Path

# Add parent directory to path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from services.remedy_service import find_remedies_for_group, get_remedy_stats

def test_remedy_profiles():
    print("\n" + "="*70)
    print("🧪 REMEDY-PROFILE TEST")
    print("="*70)
    
    # Test 1: Heel-Profile
    print("\n[1/2] Test: Heel-Remedies Profil")
    print("-" * 70)
    
    heel_results = find_remedies_for_group('__remedy_category_heel_remedies__', max_results=10)
    
    if heel_results:
        print(f"  ✅ {len(heel_results)} Heel-Mittel gefunden:")
        for i, (name, indication) in enumerate(heel_results[:10], 1):
            print(f"     {i:2d}. {name}")
    else:
        print("  ❌ Keine Heel-Mittel gefunden!")
    
    # Test 2: Nutramedix-Profile
    print("\n[2/2] Test: Nutramedix-Remedies Profil")
    print("-" * 70)
    
    nutra_results = find_remedies_for_group('__remedy_category_nutramedix_remedies__', max_results=10)
    
    if nutra_results:
        print(f"  ✅ {len(nutra_results)} Nutramedix-Mittel gefunden:")
        for i, (name, indication) in enumerate(nutra_results[:10], 1):
            print(f"     {i:2d}. {name}")
    else:
        print("  ❌ Keine Nutramedix-Mittel gefunden!")
    
    # Statistik
    print("\n" + "="*70)
    stats = get_remedy_stats()
    print(f"📊 Remedy-DB: {stats['total']} Einträge")
    
    # Prüfe Kategorien
    from services.remedy_service import get_remedy_connection
    with get_remedy_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM remedies WHERE category = 'phytotherapie_heel'")
        heel_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM remedies WHERE category = 'phytotherapie_nutramedix'")
        nutra_count = cursor.fetchone()[0]
        
        print(f"   • Heel: {heel_count} Mittel")
        print(f"   • Nutramedix: {nutra_count} Mittel")
    
    print("="*70)
    
    # Erfolg wenn beide Profile Ergebnisse liefern
    success = len(heel_results) > 0 and len(nutra_results) > 0
    
    if success:
        print("\n✅ ALLE TESTS BESTANDEN!")
    else:
        print("\n❌ TESTS FEHLGESCHLAGEN!")
    
    return success

if __name__ == "__main__":
    success = test_remedy_profiles()
    sys.exit(0 if success else 1)
