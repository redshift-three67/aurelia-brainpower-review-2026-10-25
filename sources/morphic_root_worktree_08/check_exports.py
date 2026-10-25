#!/usr/bin/env python3

with open('apps/cli/main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Finde _resolve_export_paths definition
for i, line in enumerate(lines, 1):
    if 'def _resolve_export_paths' in line:
        print(f'FOUND: Line {i}')
        for j in range(max(0, i-2), min(len(lines), i+8)):
            print(f'{j+1}: {lines[j].rstrip()}')
        break
else:
    print('_resolve_export_paths NOT FOUND')

# Suche nach Calls
print('\n--- Calls to _resolve_export_paths ---')
for i, line in enumerate(lines, 1):
    if '_resolve_export_paths(' in line and 'def ' not in line:
        print(f'{i}: {line.rstrip()}')
