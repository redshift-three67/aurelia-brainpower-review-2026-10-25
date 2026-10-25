#!/usr/bin/env python3
"""Identifiziere alle großen Funktionen in main.py zur Migration"""
from pathlib import Path

MAIN_FILE = Path("apps/cli/main.py")

# Bereits migrierte Funktionen
MIGRATED = {
    'groups_overview',
    'hw_diagnostics', 
    'top3_scan',
    'analyze_trends',
    'client_trends',
    'batch_scan',
    'bat_area_scan',
    'analyze',
    'nls_3d_export',  # bereits in scan.py
}

# Bekannte Probleme
SKIP = {
    'field_test',  # Hat undefinierte Parameter
}

with open(MAIN_FILE, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Finde alle def-Zeilen
functions = []
for i, line in enumerate(lines, 1):
    if line.startswith('def ') and '(' in line:
        func_name = line.split('def ')[1].split('(')[0]
        functions.append((func_name, i))

print("=" * 70)
print("CANDIDATE FUNCTIONS FOR MIGRATION")
print("=" * 70)

# Berechne Zeilenzahlen fuer jede Funktion
candidates = []
for idx, (func_name, start_line) in enumerate(functions):
    # Finde Endzeilennummer (naechste Funktion oder EOF)
    if idx + 1 < len(functions):
        end_line = functions[idx + 1][1] - 1
    else:
        end_line = len(lines)
    
    lines_count = end_line - start_line + 1
    
    # Pruefen ob bereits migriert oder zu skipping
    if func_name in MIGRATED or func_name in SKIP:
        continue
    
    # Nur Funktionen mit 300+ Zeilen
    if lines_count < 300:
        continue
    
    candidates.append((func_name, start_line, end_line, lines_count))

# Sortiere nach Zeilenzahl (absteigend)
candidates.sort(key=lambda x: x[3], reverse=True)

print("\nGROSSE FUNKTIONEN (>=300 Zeilen):\n")
for func_name, start, end, count in candidates[:10]:
    status = "[SKIP]" if func_name in SKIP else "[OK]"
    print(f"{status} {func_name:40} {count:4} lines (lines {start}-{end})")

print("\n" + "=" * 70)
print("RECOMMENDED NEXT TARGETS:\n")

# Top 3 empfehlungen
for i, (func_name, start, end, count) in enumerate(candidates[:3], 1):
    if func_name not in SKIP:
        print(f"{i}. {func_name:40} ({count} lines)")

print("=" * 70)
