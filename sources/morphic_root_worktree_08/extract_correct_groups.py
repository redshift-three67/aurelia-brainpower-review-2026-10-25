"""Extrahiert die KORREKTE Liste aller verfügbaren Gruppen für CLI."""

from core.subgroups.procedural_groups import list_groups

# Alle verfügbaren Gruppen
all_groups = sorted(list_groups())

print("# KORREKTE GRUPPENLISTE FÜR CLI (266 Gruppen)")
print("# Generiert aus: core.subgroups.procedural_groups.list_groups()")
print()
print("groups = [")

for group in all_groups:
    print(f'    "{group}",')

print("]")
print()
print(f"# TOTAL: {len(all_groups)} Gruppen")
