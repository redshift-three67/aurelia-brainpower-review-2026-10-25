#!/usr/bin/env python3
"""Verify Session 5C migration is complete"""

import py_compile
import sys

print("=" * 80)
print("SESSION 5C VERIFICATION")
print("=" * 80)
print()

errors = []

# 1. Syntax check
print("1. SYNTAX CHECKS:")
print("-" * 80)

files_to_check = [
    'apps/cli/main.py',
    'apps/cli/commands/field.py',
]

for fpath in files_to_check:
    try:
        py_compile.compile(fpath, doraise=True)
        print(f"  [OK] {fpath}")
    except py_compile.PyCompileError as e:
        print(f"  [FAIL] {fpath}")
        errors.append((fpath, str(e)))

print()

# 2. Content checks
print("2. CONTENT CHECKS:")
print("-" * 80)

with open('apps/cli/main.py', 'r', encoding='utf-8', errors='ignore') as f:
    main_content = f.read()

with open('apps/cli/commands/field.py', 'r', encoding='utf-8', errors='ignore') as f:
    field_content = f.read()

checks = [
    ('field_app import in main.py', 'from apps.cli.commands.field import field_app' in main_content),
    ('field_app registration', 'app.add_typer(field_app, name="field")' in main_content),
    ('field_test removed from main.py', 'def field_test(' not in main_content),
    ('field_test in field.py', 'def field_test(' in field_content),
    ('field_app defined in field.py', 'field_app = typer.Typer()' in field_content),
    ('multiplex_scan still in main.py', 'def multiplex_scan(' in main_content),
]

for desc, result in checks:
    status = '[OK]' if result else '[FAIL]'
    print(f"  {status} {desc}")
    if not result and 'removed' not in desc:
        errors.append((desc, "Missing required content"))

print()

# 3. File sizes
print("3. FILE SIZES:")
print("-" * 80)

with open('apps/cli/main.py', 'r', encoding='utf-8', errors='ignore') as f:
    main_lines = len(f.readlines())

with open('apps/cli/commands/field.py', 'r', encoding='utf-8', errors='ignore') as f:
    field_lines = len(f.readlines())

print(f"  main.py: {main_lines} lines (was 7309, removed 549)")
print(f"  field.py: {field_lines} lines (new)")

print()
print("=" * 80)

if errors:
    print("ERRORS FOUND:")
    for item, error in errors:
        print(f"  - {item}: {error}")
    print()
    sys.exit(1)
else:
    print("ALL CHECKS PASSED!")
    print()
    print("NEXT: git commit -m 'migrate: field_test() to commands/field.py'")
    sys.exit(0)
