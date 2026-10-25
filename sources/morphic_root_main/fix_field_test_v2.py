#!/usr/bin/env python3
"""Fix field_test() - simpler approach"""

with open('apps/cli/main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. Entferne "focus_weighting and" von Zeile 3463
for i, line in enumerate(lines):
    if i == 3462:  # 0-indexed, also Zeile 3463
        if 'if focus_weighting and' in line:
            lines[i] = line.replace('if focus_weighting and ', 'if ')
            print(f"Line {i+1}: focus_weighting removed")

# 2. Entferne focus Parameter aus field_test() falls bereits da
# (Suche nach "focus: str = typer.Option" zwischen Zeilen 3374-3380)
# Nicht nötig wenn nicht da

# 3. Check _resolve_export_paths call (Zeile ~3784)
for i, line in enumerate(lines):
    if '_resolve_export_paths(export, client_info, "field_test", filename_suffix, scan_type, session_id)' in line:
        lines[i] = line.replace(
            '_resolve_export_paths(export, client_info, "field_test", filename_suffix, scan_type, session_id)',
            '_resolve_export_paths(export, client_info, "field_test")'
        )
        print(f"Line {i+1}: _resolve_export_paths fixed")

# Speichern
with open('apps/cli/main.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Done")
