#!/usr/bin/env python3
"""Finde alle @app.command() Funktionen in main.py"""
from pathlib import Path

MAIN_FILE = Path("apps/cli/main.py")

MIGRATED = {
    'groups_overview', 'hw_diagnostics', 'top3_scan', 'analyze_trends',
    'client_trends', 'batch_scan', 'bat_area_scan', 'analyze', 'nls_3d_export',
}

SKIP = {'field_test'}

with open(MAIN_FILE, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("=" * 70)
print("COMMANDS (@app.command) IN MAIN.PY")
print("=" * 70)

# Finde @app.command() Zeilen und die nachfolgende def Zeile
commands = []
for i, line in enumerate(lines):
    if '@app.command()' in line or '@app.command(' in line:
        # Suche naechste def Zeile
        for j in range(i, min(i + 10, len(lines))):
            if 'def ' in lines[j]:
                func_name = lines[j].split('def ')[1].split('(')[0]
                start_line = i + 1  # Start from decorator
                
                # Finde Endzeilennummer
                for k in range(j + 1, len(lines)):
                    if lines[k].startswith('def ') or (lines[k].startswith('@') and 'app.command' in lines[k]):
                        end_line = k - 1
                        break
                else:
                    end_line = len(lines)
                
                lines_count = end_line - start_line + 1
                
                if func_name not in MIGRATED and func_name not in SKIP:
                    commands.append((func_name, start_line, end_line, lines_count))
                
                break

# Sort by Zeilenzahl (aufsteigend) - kleinere zuerst aber > 300
commands = [c for c in commands if c[3] >= 300]
commands.sort(key=lambda x: x[3])

print("\nAVAILABLE COMMANDS (>= 300 lines):\n")
for func_name, start, end, count in commands:
    print(f"  {func_name:40} {count:5} lines (lines {start}-{end})")

print("\n" + "=" * 70)
if commands:
    print(f"\nBEST NEXT CHOICE:")
    print(f"  -> {commands[0][0]} ({commands[0][3]} lines)")
    print(f"     Start: line {commands[0][1]}")
    print(f"     End:   line {commands[0][2]}")
