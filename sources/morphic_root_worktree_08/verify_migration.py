#!/usr/bin/env python3
"""Verifiziert dass analyze() Funktion korrekt migriert wurde"""

with open('apps/cli/main.py', 'r', encoding='utf-8') as f:
    main_content = f.read()

with open('apps/cli/commands/scan.py', 'r', encoding='utf-8') as f:
    scan_content = f.read()

print("MIGRATION VERIFICATION")
print("=" * 60)

# Check main.py
if 'def analyze(' in main_content:
    print("[ERROR] analyze() ist noch in main.py!")
    exit(1)
else:
    print("[OK] analyze() wurde aus main.py entfernt")

# Check scan.py
if 'def analyze(' in scan_content and '@scan_app.command()' in scan_content:
    print("[OK] analyze() ist in scan.py vorhanden (mit Dekorator)")
else:
    print("[ERROR] analyze() in scan.py fehlt oder ist malformed!")
    exit(1)

# Check helpers
scan_helpers = ['_build_rate_db_from_subgroups', '_client_folder_name', '_resolve_export_paths']
for helper in scan_helpers:
    if f'def {helper}' in scan_content:
        print(f"[OK] {helper} ist in scan.py vorhanden")
    else:
        print(f"[ERROR] {helper} fehlt in scan.py!")
        exit(1)

# Check that _build_rate_db_from_subgroups is NOT in main.py
if 'def _build_rate_db_from_subgroups' in main_content:
    print("[ERROR] _build_rate_db_from_subgroups sollte aus main.py entfernt sein!")
    exit(1)
else:
    print("[OK] _build_rate_db_from_subgroups wurde aus main.py entfernt")

print("\n" + "=" * 60)
print("[SUCCESS] Migration erfolgreich abgeschlossen!")
