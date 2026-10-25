"""
Analyse-Skript: Prüft welche Gruppen in Profilen definiert sind vs. tatsächlich existieren
"""
import sys
sys.path.insert(0, '.')

from apps.cli.profiles.registry import _PROFILES_DATA
from core.subgroups.procedural_groups import generate_candidates_for_group, list_groups

def analyze_profile(profile_name: str):
    """Analysiert ein Profil und zeigt fehlende Gruppen."""
    if profile_name not in _PROFILES_DATA:
        print(f"❌ Profil '{profile_name}' nicht gefunden!")
        return
    
    defined_groups = _PROFILES_DATA[profile_name]
    available_groups = set(list_groups())
    
    print(f"\n{'='*70}")
    print(f"PROFIL: {profile_name}")
    print(f"{'='*70}")
    print(f"Definierte Gruppen: {len(defined_groups)}")
    print(f"Verfügbare Gruppen: {len(available_groups)}")
    print()
    
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
            except Exception as e:
                empty.append(group)
    
    print(f"✅ EXISTIEREND: {len(existing)} Gruppen")
    print(f"⚠️  LEER:        {len(empty)} Gruppen")
    print(f"❌ FEHLEND:     {len(missing)} Gruppen")
    print()
    
    if missing:
        print("❌ FEHLENDE GRUPPEN:")
        for g in missing[:20]:  # Zeige max 20
            print(f"   - {g}")
        if len(missing) > 20:
            print(f"   ... und {len(missing) - 20} weitere")
        print()
    
    if empty:
        print("⚠️  LEERE GRUPPEN:")
        for g in empty[:20]:
            print(f"   - {g}")
        if len(empty) > 20:
            print(f"   ... und {len(empty) - 20} weitere")
        print()
    
    # Effektive Gruppen
    effective = len(existing)
    print(f"📊 EFFEKTIVE GRUPPEN: {effective} von {len(defined_groups)} ({effective/len(defined_groups)*100:.1f}%)")
    print()
    
    return {
        'profile': profile_name,
        'defined': len(defined_groups),
        'existing': len(existing),
        'empty': len(empty),
        'missing': len(missing),
        'percentage': effective/len(defined_groups)*100
    }

if __name__ == '__main__':
    # Analysiere alle Profile
    profiles_to_check = [
        'gehirn_detailliert',
        'lymphsystem_detailliert',
        'immunsystem_detailliert',
        'zaehne_kiefer_detailliert',
        'meridiane_tcm_detailliert',
        'emf_stoerfelder_detailliert',
        'hormone_stoffwechsel_detailliert',
        'psyche_emotion_detailliert',
    ]
    
    results = []
    for profile in profiles_to_check:
        result = analyze_profile(profile)
        if result:
            results.append(result)
    
    # Zusammenfassung
    print(f"\n{'='*70}")
    print("ZUSAMMENFASSUNG ALLER PROFILE")
    print(f"{'='*70}")
    print(f"{'Profil':<40} {'Definiert':>10} {'Effektiv':>10} {'%':>8}")
    print(f"{'-'*70}")
    for r in results:
        print(f"{r['profile']:<40} {r['defined']:>10} {r['existing']:>10} {r['percentage']:>7.1f}%")
    print(f"{'='*70}")
