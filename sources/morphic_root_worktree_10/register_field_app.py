#!/usr/bin/env python3
"""Register field_app in main.py"""

with open('apps/cli/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add import
old_import = "from apps.cli.commands.synergy import synergy_app"
new_import = "from apps.cli.commands.synergy import synergy_app\nfrom apps.cli.commands.field import field_app"

if new_import not in content:
    content = content.replace(old_import, new_import)
    print("[OK] Added import for field_app")
else:
    print("[SKIP] field_app import already exists")

# Add registration
old_reg = 'app.add_typer(synergy_app, name="synergy")'
new_reg = 'app.add_typer(synergy_app, name="synergy")\napp.add_typer(field_app, name="field")'

if new_reg not in content:
    content = content.replace(old_reg, new_reg)
    print("[OK] Added registration for field_app")
else:
    print("[SKIP] field_app registration already exists")

with open('apps/cli/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] main.py updated with field_app registration")
