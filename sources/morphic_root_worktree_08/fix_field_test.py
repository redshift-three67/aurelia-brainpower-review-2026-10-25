#!/usr/bin/env python3
"""Fix field_test() undefined variables - Option A"""
import re

with open('apps/cli/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Entferne focus_weighting Check (Zeile ~3458)
# Ersetze: if focus_weighting and (focus or "").strip():
# Mit: if (focus or "").strip():
content = re.sub(
    r'if focus_weighting and \(\(focus or ""\)\.strip\(\)\):',
    r'if (focus or "").strip():',
    content
)

# 2. Ändere export_data["command"] von "multiplex_scan" zu "field_test"
content = re.sub(
    r'"command": "multiplex_scan",\n\s+"hardware_profile": _profile,\n\s+"hardware_source": src\.name\(\),\n\s+"h_level": float\(h_level\),\n\s+"client": client_info,\n\s+"focus": focus,',
    r'"command": "field_test",\n        "hardware_profile": _profile,\n        "hardware_source": src.name(),\n        "h_level": float(h_level),\n        "client": client_info,\n        "focus": focus,',
    content
)

# 3. Ändere _resolve_export_paths Call - entferne filename_suffix, scan_type, session_id
# Von: json_path, html_path = _resolve_export_paths(export, client_info, "multiplex_scan", filename_suffix, scan_type, session_id)
# Zu:  json_path, html_path = _resolve_export_paths(export, client_info, "field_test")
old_export_call = r'json_path, html_path = _resolve_export_paths\(export, client_info, "multiplex_scan", filename_suffix, scan_type, session_id\)'
new_export_call = r'json_path, html_path = _resolve_export_paths(export, client_info, "field_test")'
content = re.sub(old_export_call, new_export_call, content)

# 4. Füge focus Parameter zu field_test() hinzu (nach hardware_profile)
# Finde die Funktion und füge hinzu nach top_k Parameter
old_params = r'(top_k: int = typer\.Option\(8, "--top-k", min=1, help="Anzahl der Top-Resonanzen im Bericht"\),)'
new_params = r'''\1
    focus: str = typer.Option(
        "",
        "--focus",
        help="Optionaler Fokus / Symptom zur Gewichtung der Ergebnisse",
    ),'''
content = re.sub(old_params, new_params, content)

with open('apps/cli/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ field_test() fixes applied:")
print("  - Removed focus_weighting condition")
print("  - Changed 'multiplex_scan' to 'field_test' in command")
print("  - Fixed _resolve_export_paths() call")
print("  - Added focus parameter")
