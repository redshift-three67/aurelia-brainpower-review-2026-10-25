#!/usr/bin/env python3
"""Zeige ALLE @app.command() Funktionen"""
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
print("ALL @app.command() FUNCTIONS")
print("=" * 70)

commands = []
i = 0
while i < len(lines):
    line = lines[i]
    if '@app.command()' in line or '@app.command(' in line:
        # Suche naechste def Zeile
        for j in range(i, min(i + 10, len(lines))):
            if 'def ' in lines[j]:
                func_name = lines[j].split('def ')[1].split('(')[0].strip()
                start_line = i + 1
                
                # Finde Endzeilennummer
                for k in range(j + 1, len(lines)):
                    if (lines[k].startswith('def ') or 
                        (lines[k].startswith('@') and 'app.command' in lines[k])):
                        end_line = k - 1
                        break
                else:
                    end_line = len(lines) - 1
                
                lines_count = end_line - start_line + 1
                
                status = "MIGRATED" if func_name in MIGRATED else "SKIP" if func_name in SKIP else "AVAILABLE"
                
                commands.append((func_name, start_line, end_line, lines_count, status))
                i = k
                break
        else:
            i += 1
    else:
        i += 1

# Sort by Zeilenzahl
commands.sort(key=lambda x: x[3])

print("\n{:<40} {:>6}  STATUS\n".format("FUNCTION", "LINES"))
print("-" * 70)

for func_name, start, end, count, status in commands:
    marker = "[X]" if status == "MIGRATED" else "[-]" if status == "SKIP" else "[ ]"
    print(f"{marker} {func_name:<35} {count:>6}  {status}")

print("\n" + "=" * 70)
print("\nAVAILABLE FOR MIGRATION:\n")
available = [(f, s, e, c) for f, s, e, c, st in commands if st == "AVAILABLE"]
for func_name, start, end, count in available:
    print(f"  {func_name:<40} {count:>5} lines")
