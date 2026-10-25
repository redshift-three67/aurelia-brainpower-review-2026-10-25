#!/usr/bin/env python3
"""Finde mittlere Funktionen (500-1500 Zeilen) fuer manageable Migrationen"""
from pathlib import Path

MAIN_FILE = Path("apps/cli/main.py")

MIGRATED = {
    'groups_overview', 'hw_diagnostics', 'top3_scan', 'analyze_trends',
    'client_trends', 'batch_scan', 'bat_area_scan', 'analyze', 'nls_3d_export',
}

SKIP = {'field_test'}

with open(MAIN_FILE, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Finde alle def-Zeilen (ohne Underscore - sind wahrscheinlich Helfer)
functions = []
for i, line in enumerate(lines, 1):
    stripped = line.lstrip()
    if stripped.startswith('def ') and '(' in line and not stripped.startswith('def _'):
        func_name = line.split('def ')[1].split('(')[0]
        functions.append((func_name, i))

print("=" * 70)
print("MEDIUM-SIZED FUNCTIONS (500-1500 lines)")
print("=" * 70)

candidates = []
for idx, (func_name, start_line) in enumerate(functions):
    if idx + 1 < len(functions):
        end_line = functions[idx + 1][1] - 1
    else:
        end_line = len(lines)
    
    lines_count = end_line - start_line + 1
    
    if func_name in MIGRATED or func_name in SKIP:
        continue
    
    # Medium range: 500-1500 Zeilen
    if 500 <= lines_count <= 1500:
        candidates.append((func_name, start_line, end_line, lines_count))

candidates.sort(key=lambda x: x[3])

print("\nCANDIDATES:\n")
for func_name, start, end, count in candidates:
    print(f"  {func_name:40} {count:4} lines (lines {start}-{end})")

print("\n" + "=" * 70)
if candidates:
    print(f"\nBEST CHOICE: {candidates[0][0]} ({candidates[0][3]} lines)")
    print("  -> Groß genug um wertvoll zu sein")
    print("  -> Klein genug um sicher zu migrieren")
else:
    print("No candidates in 500-1500 line range")
