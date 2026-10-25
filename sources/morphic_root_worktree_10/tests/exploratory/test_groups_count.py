"""Test: Wie viele Gruppen sind tatsächlich verfügbar?"""

from core.subgroups.procedural_groups import list_groups, _GROUP_LABELS

# Alle verfügbaren Gruppen
all_groups = list_groups()

print("=" * 70)
print("GRUPPEN-ANALYSE")
print("=" * 70)
print(f"\nTOTAL VERFÜGBARE GRUPPEN: {len(all_groups)}")
print(f"GRUPPEN IN _GROUP_LABELS: {len(_GROUP_LABELS)}")

print("\n" + "=" * 70)
print("ALLE GRUPPEN (alphabetisch sortiert):")
print("=" * 70)

for i, group in enumerate(sorted(all_groups), 1):
    print(f"{i:3d}. {group}")

print("\n" + "=" * 70)
print(f"GESAMT: {len(all_groups)} Gruppen")
print("=" * 70)
