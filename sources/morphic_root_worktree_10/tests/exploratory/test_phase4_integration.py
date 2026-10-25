"""Test ob Phase 4 Gruppen korrekt integriert wurden"""
import sys
from pathlib import Path

# Füge Projektverzeichnis zum Path hinzu
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from core.subgroups.procedural_groups import _GROUP_LABELS
    
    print("=" * 70)
    print("PHASE 4 INTEGRATION TEST")
    print("=" * 70)
    
    # Zähle alle Gruppen
    total_groups = len(_GROUP_LABELS)
    print(f"\n✓ Gesamt-Gruppen: {total_groups}")
    
    # Suche Phase 4 Gruppen
    phase4_keywords = [
        'zahn_symptome', 'zahn_pathologien', 'zahn_materialien', 'zahn_remedies',
        'wirbelsaeule_symptome', 'wirbelsaeule_pathologien', 'wirbelsaeule_remedies',
        'strahlung_symptome', 'strahlung_quellen', 'geopathie_fein', 'strahlung_schutz',
        'entgiftung_symptome', 'entgiftung_organe', 'entgiftung_remedies',
        'verdauung_symptome', 'verdauung_pathologien', 'verdauung_remedies',
        'nerven_symptome', 'nerven_pathologien', 'nerven_remedies',
        'herz_symptome', 'kreislauf_symptome', 'herz_pathologien', 'herz_remedies',
        'knochen_symptome', 'knochen_pathologien', 'knochen_remedies',
        'toxine_symptome', 'schwermetalle_detailliert', 'chemikalien_detailliert', 'toxine_remedies',
        'atmung_symptome', 'atmung_pathologien', 'atmung_remedies',
        'hormone_symptome', 'hormone_schilddruese', 'hormone_geschlecht', 'hormone_remedies',
        'luft_symptome', 'wohnraumgifte_fein', 'luft_remedies',
        'nahrung_symptome', 'nahrung_unvertraeglichkeiten', 'nahrung_remedies',
    ]
    
    found_groups = []
    for keyword in phase4_keywords:
        if keyword in _GROUP_LABELS:
            found_groups.append(keyword)
    
    print(f"✓ Phase 4 Gruppen gefunden: {len(found_groups)}/44")
    
    if len(found_groups) == 44:
        print("\n" + "=" * 70)
        print("✅ ALLE 44 PHASE 4 GRUPPEN ERFOLGREICH INTEGRIERT!")
        print("=" * 70)
        
        # Zeige Beispiele
        print("\n📋 BEISPIELE:")
        for i, group_name in enumerate(found_groups[:10], 1):
            items = _GROUP_LABELS[group_name]
            item_count = len(items) if isinstance(items, list) else "?"
            print(f"  {i}. {group_name}: {item_count} Items")
        
        if len(found_groups) > 10:
            print(f"  ... und {len(found_groups) - 10} weitere Gruppen")
            
    else:
        print("\n⚠️ WARNUNG: Nicht alle Gruppen gefunden!")
        missing = set(phase4_keywords) - set(found_groups)
        print(f"\nFehlende Gruppen ({len(missing)}):")
        for m in sorted(missing):
            print(f"  - {m}")
    
    print("\n" + "=" * 70)
    
except Exception as e:
    print(f"❌ FEHLER: {e}")
    import traceback
    traceback.print_exc()
