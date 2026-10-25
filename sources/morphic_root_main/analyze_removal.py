#!/usr/bin/env python3
"""
Sichere Entfernung der analyze() Funktion aus main.py
mit Validierung der Helfer-Abhängigkeiten
"""
import re
from pathlib import Path

MAIN_FILE = Path("apps/cli/main.py")
SCAN_FILE = Path("apps/cli/commands/scan.py")

def find_function_range(lines, decorator_pattern, func_name):
    """Findet Start- und Endzeilennummer einer Funktion"""
    start_line = None
    
    # Finde Dekorator + Funktionsdefinition
    for i, line in enumerate(lines):
        if decorator_pattern in line:
            # Prüfe nächste Zeilen für Funktionsdefinition
            for j in range(i, min(i+5, len(lines))):
                if f"def {func_name}" in lines[j]:
                    start_line = i
                    break
            if start_line is not None:
                break
    
    if start_line is None:
        return None, None
    
    # Finde Endzeilennummer (nächste Funktion oder EOF)
    indent_of_func = len(lines[start_line + 1]) - len(lines[start_line + 1].lstrip())
    
    for i in range(start_line + 2, len(lines)):
        line = lines[i]
        # Leere Zeilen überspringen
        if not line.strip():
            continue
        # Nächste Top-Level-Definition (def oder @)
        curr_indent = len(line) - len(line.lstrip())
        if curr_indent == 0 and (line.strip().startswith("@") or line.strip().startswith("def ")):
            return start_line, i - 1
    
    return start_line, len(lines) - 1

def check_helper_dependencies(lines):
    """Prüfe welche Helfer noch von anderen Funktionen verwendet werden"""
    helpers = {
        '_build_rate_db_from_subgroups': False,
        '_client_folder_name': False,
        '_resolve_export_paths': False,
        '_clamp': False,
    }
    
    # Finde analyze() Bereich
    analyze_start, analyze_end = find_function_range(lines, "@app.command()", "analyze")
    
    # Zähle Verwendungen außerhalb von analyze()
    for helper in helpers:
        usage_in_main = 0
        usage_outside_analyze = 0
        
        for i, line in enumerate(lines):
            if helper in line and f"def {helper}" not in line:
                usage_in_main += 1
                if not (analyze_start <= i <= analyze_end):
                    usage_outside_analyze += 1
        
        helpers[helper] = usage_outside_analyze > 0
        print(f"  {helper}: {usage_outside_analyze} uses außerhalb analyze() (total: {usage_in_main})")
    
    return helpers

def remove_analyze_function(main_file):
    """Entfernt analyze() Funktion aus main.py"""
    
    with open(main_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    original_count = len(lines)
    
    print(f"Analysiere {main_file}...")
    print(f"  Zeilen: {original_count}")
    
    # Finde analyze() Funktion
    start, end = find_function_range(lines, "@app.command()", "analyze")
    
    if start is None:
        print("  [ERROR] analyze() Funktion nicht gefunden!")
        return False
    
    print(f"  [OK] analyze() gefunden: Zeilen {start+1}-{end+1}")
    
    # Prüfe Helfer-Abhängigkeiten
    print("\nPruefen Helfer-Abhaengigkeiten:")
    needed_helpers = check_helper_dependencies(lines)
    
    # Bestimme was entfernt werden soll
    helpers_to_remove = [h for h, needed in needed_helpers.items() if not needed]
    
    print(f"\nEnfernbare Helfer: {helpers_to_remove}")
    print(f"Behalte Helfer: {[h for h, needed in needed_helpers.items() if needed]}")
    
    # Entferne analyze()
    removed_lines = lines[start:end+1]
    lines = lines[:start] + lines[end+1:]
    
    # Versuche Helfer zu entfernen (nur wenn nicht mehr benötigt)
    for helper in helpers_to_remove:
        h_start, h_end = find_function_range(lines, "", helper)
        if h_start is not None:
            print(f"  Entferne {helper}...")
            lines = lines[:h_start] + lines[h_end+1:]
    
    new_content = '\n'.join(lines)
    
    # Validierung
    print("\nValidierung:")
    print(f"  Zeilen entfernt: {original_count - len(lines)}")
    print(f"  Neue Dateigrösse: {len(lines)} Zeilen")
    
    # Prüfe ob analyze noch vorhanden ist
    if "def analyze(" in new_content and "@app.command()" in content.split("def analyze(")[0].split('@app.command()')[-1]:
        print("  [ERROR] analyze() ist noch in der Datei!")
        return False
    
    print("  [OK] analyze() erfolgreich entfernt")
    
    # Schreibe Backup
    backup_path = main_file.with_suffix('.py.backup')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  [OK] Backup erstellt: {backup_path}")
    
    # Schreibe neue Datei
    with open(main_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"  [OK] {main_file} aktualisiert")
    
    return True

if __name__ == "__main__":
    import os
    os.chdir(Path(__file__).parent)
    
    success = remove_analyze_function(MAIN_FILE)
    if success:
        print("\n[SUCCESS] Erfolgreich abgeschlossen!")
    else:
        print("\n[FAILED] Fehler bei der Entfernung!")
