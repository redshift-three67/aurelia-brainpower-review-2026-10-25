"""
Test: Remedy-Integration in alle Profile
Prüft, ob Heel & Nutramedix Remedies in Standard-Profilen (pathogen, full, etc.) erscheinen.
"""

import sys
from pathlib import Path

# Add parent directory to path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from services.remedy_service import find_remedies_for_group

def test_remedy_integration():
    print("\n" + "="*70)
    print("🔍 REMEDY-INTEGRATION TEST")
    print("Prüft, ob Heel & Nutramedix in Standard-Profilen erscheinen")
    print("="*70)
    
    # Test-Gruppen aus verschiedenen Profilen
    test_groups = [
        # Pathogen-Profil
        ("bakterien", "Bakterien-Gruppe (Pathogen-Profil)"),
        ("viren", "Viren-Gruppe (Pathogen-Profil)"),
        ("parasiten", "Parasiten-Gruppe (Pathogen-Profil)"),
        
        # Regulation-Profil
        ("entgiftung_leber", "Entgiftung-Gruppe (Regulation-Profil)"),
        ("immunsystem_angeboren", "Immunsystem-Gruppe (Regulation-Profil)"),
        
        # Detaillierte Profile
        ("schmerz_kopf", "Kopfschmerz-Gruppe (Detailliert)"),
        ("verdauung_magen", "Verdauung-Gruppe (Detailliert)"),
        
        # B.A.T. Profile
        ("bat_a05_bakterien_abwehr_borreliose", "Borreliose (B.A.T.)"),
    ]
    
    results_summary = []
    
    for group_name, description in test_groups:
        print(f"\n📋 Test: {description}")
        print(f"   Gruppe: {group_name}")
        print("-" * 70)
        
        remedies = find_remedies_for_group(group_name, max_results=5)
        
        if remedies:
            print(f"  ✅ {len(remedies)} Remedies gefunden:")
            
            heel_found = False
            nutra_found = False
            
            for name, indication in remedies:
                # Prüfe, ob es Heel oder Nutramedix ist
                # (Wir prüfen anhand der Datenbank-Kategorie)
                from services.remedy_service import get_remedy_connection
                with get_remedy_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT category FROM remedies WHERE name = ?", (name,))
                    row = cursor.fetchone()
                    category = row[0] if row else ""
                
                marker = ""
                if category == "homotoxikologie_heel":  # Korrigiert: DB hat homotoxikologie_heel
                    marker = "[HEEL]"
                    heel_found = True
                elif category == "phytotherapie_nutramedix":
                    marker = "[NUTRAMEDIX]"
                    nutra_found = True
                
                print(f"     • {name} {marker}")
            
            results_summary.append({
                'group': description,
                'heel': heel_found,
                'nutra': nutra_found,
                'total': len(remedies)
            })
        else:
            print("  ⚠️  Keine Remedies gefunden")
            results_summary.append({
                'group': description,
                'heel': False,
                'nutra': False,
                'total': 0
            })
    
    # Zusammenfassung
    print("\n" + "="*70)
    print("📊 ZUSAMMENFASSUNG")
    print("="*70)
    
    heel_appearances = sum(1 for r in results_summary if r['heel'])
    nutra_appearances = sum(1 for r in results_summary if r['nutra'])
    total_groups = len(results_summary)
    
    print(f"Getestete Gruppen: {total_groups}")
    print(f"Heel erscheint in: {heel_appearances} Gruppen")
    print(f"Nutramedix erscheint in: {nutra_appearances} Gruppen")
    
    print("\nDetaillierte Ergebnisse:")
    for r in results_summary:
        heel_icon = "✅" if r['heel'] else "❌"
        nutra_icon = "✅" if r['nutra'] else "❌"
        print(f"  {r['group']:50s} | Heel: {heel_icon} | Nutra: {nutra_icon} | Total: {r['total']}")
    
    print("="*70)
    
    # Erfolg wenn mindestens in einigen Gruppen Remedies erscheinen
    success = heel_appearances > 0 or nutra_appearances > 0
    
    if success:
        print("\n✅ INTEGRATION FUNKTIONIERT!")
        print("   Heel & Nutramedix Remedies werden in Standard-Profilen gefunden.")
    else:
        print("\n⚠️  WARNUNG: Keine Hersteller-Remedies in Standard-Profilen gefunden!")
        print("   Möglicherweise fehlen Keywords oder die Kategorien sind nicht korrekt.")
    
    return success

if __name__ == "__main__":
    success = test_remedy_integration()
    sys.exit(0 if success else 1)
