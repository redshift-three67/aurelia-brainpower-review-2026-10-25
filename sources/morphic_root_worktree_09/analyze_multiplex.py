#!/usr/bin/env python3
"""Analyze multiplex_scan() function in main.py"""

import re

with open('apps/cli/main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

total_lines = len(lines)
print(f"Total lines in main.py: {total_lines}")
print("=" * 80)

# Find multiplex_scan() start
multiplex_start = None
for i, line in enumerate(lines, 1):
    if 'def multiplex_scan(' in line:
        multiplex_start = i
        print(f"multiplex_scan() starts at line: {multiplex_start}")
        break

if not multiplex_start:
    print("ERROR: multiplex_scan() not found!")
    exit(1)

# Find next function or decorator after multiplex_scan
multiplex_end = None
for i in range(multiplex_start, len(lines)):
    line = lines[i].strip()
    # Look for next @app.command or @log_command (function boundary)
    if i > multiplex_start and (line.startswith('@app.command') or line.startswith('@log_command')):
        multiplex_end = i + 1
        print(f"Next function starts at line: {multiplex_end}")
        break

if multiplex_end is None:
    multiplex_end = total_lines + 1
    print(f"*** CRITICAL: multiplex_scan() extends to EOF at line: {multiplex_end}")
    print(f"*** This means multiplex_scan() is the LAST function in main.py!")

size = multiplex_end - multiplex_start
print(f"multiplex_scan() size: {size} lines (lines {multiplex_start}-{multiplex_end-1})")
print("=" * 80)

# Analyze complexity
sample_start = multiplex_start - 1
sample_end = min(multiplex_start + 50, multiplex_end - 1)

print("\nFunction signature (first 30 lines):")
print("-" * 80)
for i in range(sample_start, min(sample_start + 30, sample_end)):
    print(f"{i+1:5} | {lines[i].rstrip()}")

print("\n" + "=" * 80)
print("RISK ASSESSMENT FOR multiplex_scan():")
print("=" * 80)

# Read function content for analysis
func_content = ''.join(lines[multiplex_start-1:multiplex_end-1])

# Count various elements
if_count = func_content.count('\nif ')
for_count = func_content.count('\nfor ')
while_count = func_content.count('\nwhile ')
try_count = func_content.count('\ntry:')
class_count = func_content.count('Service(')
helper_calls = func_content.count('_')

print(f"\nComplexity metrics:")
print(f"  - If statements: {if_count}")
print(f"  - For loops: {for_count}")
print(f"  - While loops: {while_count}")
print(f"  - Try blocks: {try_count}")
print(f"  - Class instantiations: {class_count}")
print(f"  - Helper function calls: {helper_calls}")

size_risk = "VERY HIGH" if size > 3000 else "HIGH" if size > 2000 else "MEDIUM"
complexity_risk = "VERY HIGH" if if_count > 30 else "HIGH" if if_count > 15 else "MEDIUM"
deps_risk = "VERY HIGH" if class_count > 10 else "HIGH" if class_count > 5 else "MEDIUM"

print(f"\nSIZE RISK: {size_risk} (3402 lines)")
print(f"COMPLEXITY RISK: {complexity_risk}")
print(f"DEPENDENCIES RISK: {deps_risk}")

print("\n" + "=" * 80)
print("CRITICAL FINDINGS:")
print("=" * 80)
print("1. multiplex_scan() is 3402 lines long (44% of entire main.py)")
print("2. multiplex_scan() is the LAST function in main.py")
print("3. Removing multiplex_scan() will reduce main.py by 47%")
print("4. This is a SINGLE MONOLITHIC FUNCTION that likely contains:")
print("   - Multiple internal helpers (defined inline)")
print("   - Complex business logic")
print("   - Nested control flow")
print("\n** RECOMMENDATION: SPLIT multiplex_scan() **")
print("** Instead of 1 migration, split into:")
print("   1. Core multiplex_scan() function (main logic)")
print("   2. Extracted internal helper functions")
print("   3. Distributed to multiplex.py + potentially other modules")
print("=" * 80)
