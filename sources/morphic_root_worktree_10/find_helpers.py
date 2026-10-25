#!/usr/bin/env python3
"""Finde große Helfer-Funktionen (mit _ prefix)"""
from pathlib import Path

MAIN_FILE = Path("apps/cli/main.py")

KEEP_IN_MAIN = {
    '_clamp', '_resolve_export_paths', '_client_folder_name',
    '_render_basic_html', '_render_multiplex_html', '_render_multiplex_txt',
    '_atomic_write_text', '_priority', '_category_for_group', '_is_remedy_group',
    '_rates_to_level_info', '_compute_focus_multiplier_for_item',
}

with open(MAIN_FILE, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("=" * 70)
print("LARGE HELPER FUNCTIONS (>= 50 lines)")
print("=" * 70)

helpers = []
i = 0
while i < len(lines):
    line = lines[i].lstrip()
    if line.startswith('def _'):
        func_name = line.split('def ')[1].split('(')[0].strip()
        start_line = i + 1
        
        # Finde Endzeilennummer
        for j in range(i + 1, len(lines)):
            check_line = lines[j].lstrip()
            if check_line.startswith('def ') or (check_line.startswith('@') and lines[j][0] not in (' ', '\t')):
                end_line = j - 1
                break
        else:
            end_line = len(lines) - 1
        
        lines_count = end_line - start_line + 1
        
        if lines_count >= 50:
            status = "KEEP" if func_name in KEEP_IN_MAIN else "MIGRATE"
            helpers.append((func_name, start_line, end_line, lines_count, status))
        
        i = j if 'j' in locals() else i + 1
    else:
        i += 1

# Sort by Zeilenzahl (aufsteigend)
helpers.sort(key=lambda x: x[3])

print("\n{:<40} {:>6}  STATUS\n".format("FUNCTION", "LINES"))
print("-" * 70)

total_migratable = 0
for func_name, start, end, count, status in helpers:
    marker = "[*]" if status == "KEEP" else "[ ]"
    print(f"{marker} {func_name:<35} {count:>6}  {status}")
    if status == "MIGRATE":
        total_migratable += count

print("\n" + "=" * 70)
print(f"\nTOTAL LINES TO MIGRATE (helpers): {total_migratable}")
print("\nCANDIDATES:\n")

migratables = [(f, s, e, c) for f, s, e, c, st in helpers if st == "MIGRATE"]
for func_name, start, end, count in migratables:
    print(f"  {func_name:<40} {count:>5} lines")
