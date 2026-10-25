"""
Validierungsscript für das 3D-Mapping.
Prüft, wie viele typische Items erfolgreich auf 3D-Koordinaten gemappt werden.
"""
import sys
import os
from pathlib import Path

# Pfad erweitern, damit wir core importieren können
sys.path.append(str(Path(__file__).parent.parent))

from core.nls3d_points_new import map_item_to_point, NLS3D_POINTS

# Typische Items aus verschiedenen Kategorien simulieren
TEST_ITEMS = [
    {"label": "Halswirbelsaeule (C0-C7)", "group": "wirbelsaeule_hws"},
    {"label": "Brustwirbelsaeule (Th1-Th12)", "group": "wirbelsaeule_bws"},
    {"label": "Leber", "group": "entgiftung_leber"},
    {"label": "Magen", "group": "verdauung_magen"},
    {"label": "Herz", "group": "kreislauf"},
    {"label": "Niere Links", "group": "entgiftung_niere"},
    {"label": "Stirnchakra", "group": "chakren"},
    {"label": "Borrelia burgdorferi", "group": "bakterien"}, # Sollte generisch gemappt werden?
    {"label": "Influenza A", "group": "viren"},
    {"label": "Quecksilber", "group": "schwermetalle"},
]

def run_check():
    print(f"--- Validierung 3D-Mapping ---")
    print(f"Vorhandene 3D-Punkt-Definitionen: {len(NLS3D_POINTS)}")
    
    mapped_count = 0
    for item in TEST_ITEMS:
        pt = map_item_to_point(item)
        status = "✅ OK" if pt else "❌ FEHLT"
        if pt:
            mapped_count += 1
            coords = f"[{pt.coords[0]:.2f}, {pt.coords[1]:.2f}, {pt.coords[2]:.2f}]"
            print(f"{item['label']:<30} -> {status} ({pt.id} @ {coords})")
        else:
            print(f"{item['label']:<30} -> {status}")

    success_rate = (mapped_count / len(TEST_ITEMS)) * 100
    print(f"\nErfolgsrate für Test-Set: {success_rate:.1f}%")
    
    if success_rate < 50:
        print("\n⚠ WARNUNG: Das 3D-Mapping ist lückenhaft. Der Viewer wird viele Items nicht anzeigen.")
    else:
        print("\n✓ Mapping scheint für Basis-Strukturen zu funktionieren.")

if __name__ == "__main__":
    run_check()
