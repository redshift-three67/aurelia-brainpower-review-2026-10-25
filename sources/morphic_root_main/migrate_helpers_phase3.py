#!/usr/bin/env python3
"""
Phase 3 Helper Migration Script
Migriert 28 Helper-Funktionen aus main.py in 6 neue Module
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple

# Konfiguration: Welche Funktionen in welche Module
HELPER_MODULES = {
    "database_helpers": [
        "_compute_db_client_rate_value",
        "_build_db_client_rate_block",
        "_compute_db_resonance_score",
        "_build_db_items_from_sub_results",
        "_build_db_analysis_summary",
        "_summarize_axis_items",
        "_build_morphic_axes_from_sub_results"
    ],
    "potency_helpers": [
        "_extract_potency_from_label",
        "_weighted_pick_potency_type",
        "_generate_potency_for_type",
        "_interpret_potency_from_score",
        "_interpret_potency"
    ],
    "interpretation_helpers": [
        "_interpret_level",
        "_rates_to_level_info"
    ],
    "utility_helpers": [
        "_is_remedy_group",
        "_client_folder_name",
        "_resolve_export_paths",
        "_atomic_write_text",
        "_normalize_tcm_type",
        "_normalize_planet_type",
        "_build_organ_clock_block",
        "_build_image_block"
    ],
    "influence_helpers": [
        "_build_influence_factors",
        "_compute_influence_multiplier_for_item",
        "_compute_focus_multiplier_for_item"
    ],
    "harmonization_helpers": [
        "_generate_harmonization_steps",
        "_render_basic_html",
        "_render_multiplex_txt"
    ]
}

MAIN_PY = Path("/opt/morphic_v1/apps/cli/main.py")
HELPERS_DIR = Path("/opt/morphic_v1/apps/cli/commands/helpers")

def extract_function_code(content: str, func_name: str) -> str:
    """Extrahiert eine Funktion aus dem Code"""
    # Pattern: def func_name(...):
    pattern = f"^def {re.escape(func_name)}\\(.*?\\):\\n"
    match = re.search(pattern, content, re.MULTILINE)
    
    if not match:
        return None
    
    start = match.start()
    lines = content[start:].split('\n')
    
    # Sammle Zeilen bis zur nächsten def auf gleicher Indent-Ebene
    func_lines = [lines[0]]
    for i, line in enumerate(lines[1:], 1):
        if line.startswith('def ') and not line.startswith('    '):
            # Nächste Funktion auf Hauptebene gefunden
            break
        func_lines.append(line)
    
    # Entferne trailing leere Zeilen
    while func_lines and not func_lines[-1].strip():
        func_lines.pop()
    
    return '\n'.join(func_lines)

def get_imports(content: str) -> str:
    """Extrahiert alle Import-Statements aus main.py"""
    lines = content.split('\n')
    imports = []
    
    for line in lines:
        if line.startswith('import ') or line.startswith('from '):
            imports.append(line)
        elif line and not line.startswith(' ') and imports:
            # Erste nicht-Import-Zeile, stop
            break
    
    return '\n'.join(imports)

def create_helper_module(module_name: str, functions: List[str], main_content: str, imports: str) -> str:
    """Erstellt den Code für ein Helper-Modul"""
    
    # Sammle Funktionen
    func_codes = []
    for func_name in functions:
        code = extract_function_code(main_content, func_name)
        if code:
            func_codes.append(code)
        else:
            print(f"⚠️ WARNING: Could not extract {func_name}")
    
    # Baue Modul
    module_code = f'''"""{module_name.replace('_', ' ').title()} - Helper Functions for morphic_v1"""

{imports}

# ─────────────────────────────────────────────────────────────────────────
# {module_name.upper()}
# ─────────────────────────────────────────────────────────────────────────

'''
    
    module_code += '\n\n'.join(func_codes)
    module_code += '\n'
    
    return module_code

def main():
    print("=" * 80)
    print("🚀 PHASE 3 HELPER MIGRATION - AUTOMATED")
    print("=" * 80)
    
    # Lese main.py
    print("\n1️⃣ Reading main.py...")
    main_content = MAIN_PY.read_text(encoding='utf-8')
    print(f"   Total lines: {len(main_content.split(chr(10)))}")
    
    # Extrahiere Imports
    print("\n2️⃣ Extracting imports...")
    imports = get_imports(main_content)
    print(f"   Found {len(imports.split(chr(10)))} import lines")
    
    # Erstelle Helper-Module
    print("\n3️⃣ Creating helper modules...")
    
    helpers_dir = HELPERS_DIR
    helpers_dir.mkdir(parents=True, exist_ok=True)
    
    total_functions = 0
    total_lines = 0
    
    for module_name, functions in HELPER_MODULES.items():
        print(f"\n   📄 {module_name}.py ({len(functions)} functions)...")
        
        # Erstelle Modul
        module_code = create_helper_module(module_name, functions, main_content, imports)
        module_file = helpers_dir / f"{module_name}.py"
        
        # Schreibe Datei
        module_file.write_text(module_code, encoding='utf-8')
        
        lines = len(module_code.split('\n'))
        print(f"      ✓ Written {lines} lines")
        
        total_functions += len(functions)
        total_lines += lines
    
    # Erstelle __init__.py
    print(f"\n   📄 __init__.py...")
    init_code = '''"""Helper modules for morphic_v1 commands"""

from .database_helpers import (
    _compute_db_client_rate_value,
    _build_db_client_rate_block,
    _compute_db_resonance_score,
    _build_db_items_from_sub_results,
    _build_db_analysis_summary,
    _summarize_axis_items,
    _build_morphic_axes_from_sub_results,
)

from .potency_helpers import (
    _extract_potency_from_label,
    _weighted_pick_potency_type,
    _generate_potency_for_type,
    _interpret_potency_from_score,
    _interpret_potency,
)

from .interpretation_helpers import (
    _interpret_level,
    _rates_to_level_info,
)

from .utility_helpers import (
    _is_remedy_group,
    _client_folder_name,
    _resolve_export_paths,
    _atomic_write_text,
    _normalize_tcm_type,
    _normalize_planet_type,
    _build_organ_clock_block,
    _build_image_block,
)

from .influence_helpers import (
    _build_influence_factors,
    _compute_influence_multiplier_for_item,
    _compute_focus_multiplier_for_item,
)

from .harmonization_helpers import (
    _generate_harmonization_steps,
    _render_basic_html,
    _render_multiplex_txt,
)

__all__ = [
    # Database
    "_compute_db_client_rate_value",
    "_build_db_client_rate_block",
    "_compute_db_resonance_score",
    "_build_db_items_from_sub_results",
    "_build_db_analysis_summary",
    "_summarize_axis_items",
    "_build_morphic_axes_from_sub_results",
    # Potency
    "_extract_potency_from_label",
    "_weighted_pick_potency_type",
    "_generate_potency_for_type",
    "_interpret_potency_from_score",
    "_interpret_potency",
    # Interpretation
    "_interpret_level",
    "_rates_to_level_info",
    # Utility
    "_is_remedy_group",
    "_client_folder_name",
    "_resolve_export_paths",
    "_atomic_write_text",
    "_normalize_tcm_type",
    "_normalize_planet_type",
    "_build_organ_clock_block",
    "_build_image_block",
    # Influence
    "_build_influence_factors",
    "_compute_influence_multiplier_for_item",
    "_compute_focus_multiplier_for_item",
    # Harmonization
    "_generate_harmonization_steps",
    "_render_basic_html",
    "_render_multiplex_txt",
]
'''
    
    init_file = helpers_dir / "__init__.py"
    init_file.write_text(init_code, encoding='utf-8')
    print(f"      ✓ Written __init__.py")
    
    print("\n" + "=" * 80)
    print(f"✅ MIGRATION COMPLETE")
    print("=" * 80)
    print(f"\nSummary:")
    print(f"  • Total modules: {len(HELPER_MODULES)}")
    print(f"  • Total functions: {total_functions}")
    print(f"  • Total lines: {total_lines}")
    print(f"  • Location: {helpers_dir}")
    print(f"\n🎯 NEXT STEPS:")
    print(f"  1. Verify imports work: python -c 'from apps.cli.commands.helpers import *'")
    print(f"  2. Update main.py to remove these functions")
    print(f"  3. Update commands (scan.py, harmonize.py, etc.) to import from helpers")

if __name__ == "__main__":
    main()
