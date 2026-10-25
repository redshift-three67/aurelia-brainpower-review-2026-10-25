#!/usr/bin/env python3
"""Check migration status"""

import os

# Check files exist
print("FILE CHECKS:")
print("-" * 60)

files = {
    'apps/cli/commands/field.py': 'NEW - field_test() extracted',
    'apps/cli/main.py': 'UPDATED - field_test() removed',
    'apps/cli/main.py.session5c.bak': 'BACKUP - original before migration',
}

for fpath, desc in files.items():
    exists = os.path.exists(fpath)
    if exists:
        size = os.path.getsize(fpath)
        print(f"[OK] {fpath} ({size} bytes) - {desc}")
    else:
        print(f"[FAIL] {fpath} - {desc}")

print()
print("CONTENT CHECKS:")
print("-" * 60)

with open('apps/cli/main.py', 'r', encoding='utf-8') as f:
    main_lines = f.readlines()

with open('apps/cli/commands/field.py', 'r', encoding='utf-8') as f:
    field_lines = f.readlines()

print(f"main.py: {len(main_lines)} lines")
print(f"field.py: {len(field_lines)} lines")
print()

# Check main.py imports
print("main.py imports (first 30 lines):")
for i, line in enumerate(main_lines[:30], 1):
    if line.strip():
        print(f"  {i:3}: {line.rstrip()[:70]}")

print()
print("Check: field_test() removed from main.py?")
has_field_test = any('def field_test(' in line for line in main_lines)
print(f"  Result: {'FAIL - still present' if has_field_test else 'OK - removed'}")

print()
print("Check: multiplex_scan() still at end of main.py?")
has_multiplex = any('def multiplex_scan(' in line for line in main_lines)
print(f"  Result: {'OK - present' if has_multiplex else 'FAIL - missing'}")

print()
print("Check: field.py has field_app?")
has_field_app = any('field_app = typer.Typer()' in line for line in field_lines)
print(f"  Result: {'OK - defined' if has_field_app else 'FAIL - missing'}")

print()
print("NEXT STEPS:")
print("-" * 60)
print("1. Add to main.py imports:")
print("   from apps.cli.commands.field import field_app")
print()
print("2. Add to main.py registrations:")
print("   app.add_typer(field_app, name='field')")
print()
print("3. Test syntax:")
print("   python -m py_compile apps/cli/main.py")
print("   python -m py_compile apps/cli/commands/field.py")
print()
print("4. Test command:")
print("   python -m apps.cli.main field --help")
print()
print("5. Commit:")
print("   git add -A")
print("   git commit -m 'migrate: field_test() to commands/field.py'")
