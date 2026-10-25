"""Vergleicht alte und neue Scan-Ergebnisse detailliert."""

import json
from pathlib import Path

# Pfade zu den Scans
old_scan = Path("Benutzer_Archive/Von_Rützen-Kositzkau_Claudia_02031970_Berlin/20251116_170638_multiplex_scan.json")
new_scan = Path("Benutzer_Archive/Von_Rützen-Kositzkau_Claudia_02031970_Berlin/20251116_212735_multiplex_scan.json")

print("=" * 80)
print("SCAN-VERGLEICH: ALT vs. NEU")
print("=" * 80)

# Lade alte Scan-Daten
with open(old_scan, 'r', encoding='utf-8') as f:
    old_data = json.load(f)

# Lade neue Scan-Daten
with open(new_scan, 'r', encoding='utf-8') as f:
    new_data = json.load(f)

# Extrahiere Gruppen
old_groups = old_data.get('sub_results', {}).get('groups', [])
new_groups = new_data.get('sub_results', {}).get('groups', [])

# Extrahiere Top-Items
old_top = old_data.get('sub_results', {}).get('top', [])
new_top = new_data.get('sub_results', {}).get('top', [])

# Extrahiere ALLE Items aus sub_results
old_all_items = []
new_all_items = []

# Sammle Items aus allen Gruppen
for group_name, group_data in old_data.get('sub_results', {}).items():
    if isinstance(group_data, dict) and 'items' in group_data:
        old_all_items.extend(group_data['items'])

for group_name, group_data in new_data.get('sub_results', {}).items():
    if isinstance(group_data, dict) and 'items' in group_data:
        new_all_items.extend(group_data['items'])

print("\n" + "=" * 80)
print("GRUPPEN-VERGLEICH")
print("=" * 80)
print(f"ALT (170638): {len(old_groups)} Gruppen")
print(f"NEU (212735): {len(new_groups)} Gruppen")
print(f"DIFFERENZ: {len(new_groups) - len(old_groups)} Gruppen")

# Fehlende Gruppen
missing_in_new = set(old_groups) - set(new_groups)
new_in_new = set(new_groups) - set(old_groups)

if missing_in_new:
    print(f"\n❌ FEHLEN IM NEUEN SCAN ({len(missing_in_new)} Gruppen):")
    for g in sorted(missing_in_new)[:10]:
        print(f"  - {g}")
    if len(missing_in_new) > 10:
        print(f"  ... und {len(missing_in_new) - 10} weitere")

if new_in_new:
    print(f"\n✅ NEU IM NEUEN SCAN ({len(new_in_new)} Gruppen):")
    for g in sorted(new_in_new)[:10]:
        print(f"  - {g}")
    if len(new_in_new) > 10:
        print(f"  ... und {len(new_in_new) - 10} weitere")

print("\n" + "=" * 80)
print("ITEMS-VERGLEICH")
print("=" * 80)
print(f"ALT (170638) - Top Items: {len(old_top)}")
print(f"NEU (212735) - Top Items: {len(new_top)}")
print(f"ALT (170638) - ALLE Items: {len(old_all_items)}")
print(f"NEU (212735) - ALLE Items: {len(new_all_items)}")

print("\n" + "=" * 80)
print("TOP 10 ITEMS - ALT (170638)")
print("=" * 80)
for i, item in enumerate(old_top[:10], 1):
    label = item.get('label', 'N/A')
    score = item.get('score', 0)
    group = item.get('group', 'N/A')
    print(f"{i:2d}. {label:40s} | Score: {score:6.2f} | Gruppe: {group}")

print("\n" + "=" * 80)
print("TOP 10 ITEMS - NEU (212735)")
print("=" * 80)
for i, item in enumerate(new_top[:10], 1):
    label = item.get('label', 'N/A')
    score = item.get('score', 0)
    group = item.get('group', 'N/A')
    print(f"{i:2d}. {label:40s} | Score: {score:6.2f} | Gruppe: {group}")

# Prüfe Synergy-Daten
print("\n" + "=" * 80)
print("SYNERGY-ANALYSE")
print("=" * 80)

old_synergy = old_data.get('quantum_synergy', {})
new_synergy = new_data.get('quantum_synergy', {})

print(f"ALT (170638) - Synergy vorhanden: {bool(old_synergy)}")
print(f"NEU (212735) - Synergy vorhanden: {bool(new_synergy)}")

if new_synergy:
    synergy_combos = new_synergy.get('top_combinations', [])
    print(f"NEU - Synergy Kombinationen: {len(synergy_combos)}")
    
    if synergy_combos:
        print("\nTOP 5 SYNERGY-KOMBINATIONEN:")
        for i, combo in enumerate(synergy_combos[:5], 1):
            score = combo.get('synergy_score', 0)
            items = combo.get('items', [])
            labels = [it.get('label', 'N/A') for it in items]
            print(f"{i}. Score: {score:.4f} | Items: {', '.join(labels[:3])}")

print("\n" + "=" * 80)
print("ZUSAMMENFASSUNG")
print("=" * 80)
print(f"✅ Gruppen ALT: {len(old_groups)}")
print(f"✅ Gruppen NEU: {len(new_groups)}")
print(f"✅ Top Items ALT: {len(old_top)}")
print(f"✅ Top Items NEU: {len(new_top)}")
print(f"✅ ALLE Items ALT: {len(old_all_items)}")
print(f"✅ ALLE Items NEU: {len(new_all_items)}")
print("=" * 80)
