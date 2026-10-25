"""
Vollständige Profil-Analyse: Prüft ALLE Profile auf fehlende/leere Gruppen
"""
import sys
sys.path.insert(0, '.')

from apps.cli.profiles.registry import _PROFILES_DATA
from core.subgroups.procedural_groups import generate_candidates_for_group, list_groups

def analyze_all_profiles():
    """Analysiert ALLE Profile und zeigt Statistiken."""
    
    available_groups = set(list_groups())
    
    print(f"\n{'='*80}")
    print(f"VOLLSTÄNDIGE PROFIL-ANALYSE")
    print(f"{'='*80}")
    print(f"Verfügbare Gruppen im System: {len(available_groups)}")
    print()
    
    all_results = []
    
    for profile_name in sorted(_PROFILES_DATA.keys()):
        defined_groups = _PROFILES_DATA[profile_name]
        
        # Prüfe jede Gruppe
        existing = []
        missing = []
        empty = []
        
        for group in defined_groups:
            if group not in available_groups:
                missing.append(group)
            else:
                # Teste ob Gruppe Daten hat
                try:
                    candidates = generate_candidates_for_group(group, "test", k=1)
                    if candidates and len(candidates) > 0:
                        existing.append(group)
                    else:
                        empty.append(group)
                except Exception:
                    empty.append(group)
        
        effective = len(existing)
        percentage = (effective/len(defined_groups)*100) if len(defined_groups) > 0 else 0
        
        result = {
            'profile': profile_name,
            'defined': len(defined_groups),
            'existing': len(existing),
            'empty': len(empty),
            'missing': len(missing),
            'percentage': percentage
        }
        all_results.append(result)
        
        # Detaillierte Ausgabe
        status = "✅" if percentage == 100 else "⚠️" if percentage >= 50 else "❌"
        print(f"{status} {profile_name:<45} {len(defined_groups):>3} def | {effective:>3} ok | {len(empty):>3} leer | {len(missing):>3} fehlt | {percentage:>5.1f}%")
        
        # Zeige problematische Gruppen
        if empty or missing:
            if empty:
                print(f"   ⚠️  LEERE GRUPPEN ({len(empty)}):")
                for g in empty[:5]:
                    print(f"      - {g}")
                if len(empty) > 5:
                    print(f"      ... und {len(empty) - 5} weitere")
            
            if missing:
                print(f"   ❌ FEHLENDE GRUPPEN ({len(missing)}):")
                for g in missing[:5]:
                    print(f"      - {g}")
                if len(missing) > 5:
                    print(f"      ... und {len(missing) - 5} weitere")
            print()
    
    # Zusammenfassung
    print(f"\n{'='*80}")
    print("ZUSAMMENFASSUNG")
    print(f"{'='*80}")
    
    total_profiles = len(all_results)
    perfect_profiles = sum(1 for r in all_results if r['percentage'] == 100)
    good_profiles = sum(1 for r in all_results if r['percentage'] >= 80)
    problematic_profiles = sum(1 for r in all_results if r['percentage'] < 80)
    
    print(f"Gesamt Profile:        {total_profiles}")
    print(f"Perfekt (100%):        {perfect_profiles}")
    print(f"Gut (>=80%):           {good_profiles}")
    print(f"Problematisch (<80%):  {problematic_profiles}")
    print()
    
    # Top-Probleme
    if problematic_profiles > 0:
        print("PROFILE MIT PROBLEMEN:")
        for r in sorted(all_results, key=lambda x: x['percentage']):
            if r['percentage'] < 80:
                print(f"  {r['profile']:<45} {r['percentage']:>5.1f}% ({r['existing']}/{r['defined']} Gruppen)")
    
    print(f"{'='*80}\n")
    
    return all_results

if __name__ == '__main__':
    analyze_all_profiles()
