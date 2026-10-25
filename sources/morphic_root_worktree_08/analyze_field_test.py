#!/usr/bin/env python3
"""Analysiere field_test() Funktion und ihre Abhängigkeiten"""
from pathlib import Path

MAIN_FILE = Path("apps/cli/main.py")

with open(MAIN_FILE, 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

print("=" * 70)
print("FIELD_TEST ANALYSIS")
print("=" * 70)

# Finde field_test()
for i, line in enumerate(lines, 1):
    if 'def field_test(' in line:
        print(f"\n[FOUND] field_test() at line {i}")
        
        # Zeige Funktion-Signatur
        sig_start = i
        sig_end = i
        for j in range(i, min(i + 30, len(lines))):
            if ') -> None:' in lines[j-1] or ') -> Dict' in lines[j-1] or ') ->' in lines[j-1]:
                sig_end = j
                break
        
        print(f"[SIGNATURE] Lines {sig_start}-{sig_end}:")
        for j in range(sig_start - 1, sig_end):
            print(f"  {j+1}: {lines[j][:80]}")
        
        # Finde End-Zeile
        for j in range(i, len(lines)):
            if j > i and lines[j].strip() and not lines[j].startswith(' ') and not lines[j].startswith('\t'):
                print(f"\n[RANGE] field_test: Lines {i}-{j-1} ({j-i} Zeilen)")
                break
        
        break
else:
    print("[ERROR] field_test() nicht gefunden!")

# Suche nach Helfer-Funktionen die nur von field_test verwendet werden
helpers_pattern = [
    '_nls_session_from_profiles',
    '_nls_calculate_morphic_field',
    '_nls_calculate_potential',
    'test_with_profile',
    'calculate_score',
]

print("\n" + "=" * 70)
print("POTENTIAL HELPER FUNCTIONS")
print("=" * 70)

for helper in helpers_pattern:
    found = False
    for i, line in enumerate(lines, 1):
        if f'def {helper}(' in line:
            print(f"\n[FOUND] {helper} at line {i}")
            # Finde End
            for j in range(i, len(lines)):
                if j > i and lines[j].strip() and not lines[j].startswith(' ') and not lines[j].startswith('\t'):
                    end = j - 1
                    break
            else:
                end = len(lines) - 1
            print(f"  Range: {i}-{end} ({end-i+1} Zeilen)")
            found = True
            break
    
    if not found:
        # Suche nach Verwendung
        usage_count = 0
        for line in lines:
            if helper in line and 'def ' + helper not in line:
                usage_count += 1
        
        if usage_count > 0:
            print(f"[USAGE] {helper}: verwendet in {usage_count} Zeilen (keine Definition)")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("[TIP] field_test is likely a large command - check for:")
print("  - Helper functions with internal scope")
print("  - Imports at function start")
print("  - Related utility functions in main.py")
print("=" * 70)
