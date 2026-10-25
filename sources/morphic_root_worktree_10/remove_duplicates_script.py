#!/usr/bin/env python3
"""Entfernt Duplikate aus main.py (Zeilen 7300-7612)"""

with open('apps/cli/main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"VORHER: {len(lines)} Zeilen")

# Entferne Zeilen 7300-7612 (0-indiziert: 7299-7612)
new_lines = lines[:7299] + lines[7613:]

print(f"NACHHER: {len(new_lines)} Zeilen")
print(f"ENTFERNT: {len(lines) - len(new_lines)} Zeilen")

with open('apps/cli/main.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ Duplikate erfolgreich entfernt!")
