#!/usr/bin/env python3
"""Quick status check"""
with open('apps/cli/main.py', encoding='utf-8') as f:
    main_lines = len(f.readlines())

reduction = 9543 - main_lines
percent = (reduction / 9543) * 100

print("=" * 60)
print("PHASE 3 STATUS CHECK")
print("=" * 60)
print(f"main.py:            {main_lines} lines")
print(f"Total Reduction:    {reduction} lines (-{percent:.1f}%)")
print(f"Progress:           8 of ~50 functions (~48%)")
print(f"Next Migration:     field_test (~541 lines)")
print("=" * 60)
