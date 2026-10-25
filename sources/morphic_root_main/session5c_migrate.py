#!/usr/bin/env python3
import shutil

print("SESSION 5C: FIELD_TEST() MIGRATION")
print("=" * 80)

with open('apps/cli/main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

total = len(lines)
start = end = None

for i in range(len(lines)):
    if '@app.command()' in lines[i] and 3300 < i < 3360:
        for j in range(i+1, min(i+5, len(lines))):
            if 'def field_test(' in lines[j]:
                start = i
                break
    if start is not None and end is None:
        if '@app.command("multiplex-scan")' in lines[i]:
            end = i
            break

print(f'Start: line {start+1}, End: line {end+1}')
print(f'Extract {end-start} lines')

code = ''.join(lines[start:end])
header = '''"""Field Test Command"""
from pathlib import Path
from typing import Dict, List
import numpy as np
import typer

from apps.cli.main import (
    SubgroupService, ClientProfile, AnalysisService, RateEncoder, NlsService,
    _clamp, _compute_focus_multiplier_for_item, _rates_to_level_info,
    _is_remedy_group, _resolve_export_paths, _atomic_write_text,
    _render_multiplex_html, _render_multiplex_txt, select_entropy_source,
)

field_app = typer.Typer()

'''

code_clean = code.replace('@app.command()', '@field_app.command()')

with open('apps/cli/commands/field.py', 'w', encoding='utf-8') as f:
    f.write(header + code_clean)

shutil.copy('apps/cli/main.py', 'apps/cli/main.py.session5c.bak')
new = lines[:start] + lines[end:]

with open('apps/cli/main.py', 'w', encoding='utf-8') as f:
    f.writelines(new)

print('[OK] field.py created')
print(f'[OK] main.py updated: {total} -> {len(new)} lines (-{total-len(new)})')
print('[OK] backup saved')
