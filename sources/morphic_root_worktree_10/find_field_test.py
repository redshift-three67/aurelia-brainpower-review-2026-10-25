#!/usr/bin/env python3
"""Finde field_test() Funktion in main.py"""

with open('apps/cli/main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if 'def field_test' in line:
        print(f'field_test() gefunden bei Zeile {i}')
        print(f'Umgebung (±10 Zeilen):')
        start = max(0, i - 3)
        end = min(len(lines), i + 50)
        for j in range(start, end):
            marker = '>>> ' if j == i - 1 else '    '
            print(f'{marker}{j+1:5d}: {lines[j].rstrip()}')
        break
