#!/usr/bin/env python3
"""Findet _build_rate_db_from_subgroups in main.py"""

with open('apps/cli/main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if 'def _build_rate_db_from_subgroups' in line:
        print(f"[FOUND] def _build_rate_db_from_subgroups at line {i}")
        print(f"Context (lines {max(1, i-2)}-{min(len(lines), i+10)}):")
        for j in range(max(0, i-3), min(len(lines), i+10)):
            print(f"  {j+1}: {lines[j].rstrip()[:100]}")
        break
else:
    print("[OK] _build_rate_db_from_subgroups Definition nicht in main.py gefunden")

# Suche Verwendung
usages = []
for i, line in enumerate(lines, 1):
    if '_build_rate_db_from_subgroups' in line and 'def _build' not in line:
        usages.append((i, line.rstrip()))

if usages:
    print(f"\n[FOUND] {len(usages)} Usage(s) von _build_rate_db_from_subgroups:")
    for line_num, content in usages[:5]:
        print(f"  Line {line_num}: {content[:100]}")
else:
    print("\n[OK] Keine Verwendungen von _build_rate_db_from_subgroups gefunden")
