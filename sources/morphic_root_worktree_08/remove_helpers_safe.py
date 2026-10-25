#!/usr/bin/env python3
"""
Sichere Entfernung von Helfer-Funktionen ohne Dekorator
"""
from pathlib import Path

MAIN_FILE = Path("apps/cli/main.py")

def find_function_lines(lines, func_name):
    """Findet Start und End-Zeile einer Funktion (mit oder ohne Dekorator)"""
    start_idx = None
    
    # Suche die Funktion
    for i, line in enumerate(lines):
        if f"def {func_name}(" in line:
            start_idx = i
            break
    
    if start_idx is None:
        return None, None
    
    # Gehe rückwärts um evtl. Dekorator zu finden
    actual_start = start_idx
    for i in range(start_idx - 1, -1, -1):
        if lines[i].strip().startswith("@"):
            actual_start = i
        else:
            break
    
    # Finde die End-Zeile (nächste Funktion oder EOF)
    func_indent = len(lines[start_idx]) - len(lines[start_idx].lstrip())
    
    end_idx = len(lines) - 1
    for i in range(start_idx + 1, len(lines)):
        line = lines[i]
        if line.strip():
            curr_indent = len(line) - len(line.lstrip())
            if curr_indent == 0 and line.strip().startswith(("def ", "@")):
                end_idx = i - 1
                break
    
    return actual_start, end_idx

def remove_function(file_path, func_name):
    """Entfernt eine Funktion aus der Datei"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    start, end = find_function_lines(lines, func_name)
    
    if start is None:
        print(f"[SKIP] {func_name} nicht gefunden")
        return False
    
    print(f"[REMOVE] {func_name}: Zeilen {start+1}-{end+1} ({end-start+1} Zeilen)")
    
    # Entferne die Zeilen und den nachfolgenden Leerzeilen
    new_lines = lines[:start] + lines[end+1:]
    
    # Entferne überschüssige Leerzeilen am Anfang
    while new_lines and new_lines[start].strip() == "":
        new_lines.pop(start)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    return True

if __name__ == "__main__":
    print("ENTFERNEN VON HELPER-FUNKTIONEN")
    print("=" * 60)
    
    # Entferne _build_rate_db_from_subgroups
    with open(MAIN_FILE, 'r', encoding='utf-8') as f:
        original = f.read()
    
    if remove_function(MAIN_FILE, "_build_rate_db_from_subgroups"):
        with open(MAIN_FILE, 'r', encoding='utf-8') as f:
            updated = f.read()
        
        lines_removed = len(original.split('\n')) - len(updated.split('\n'))
        print(f"[OK] {lines_removed} Zeilen entfernt")
        print(f"[OK] main.py: {len(original.split(chr(10)))} -> {len(updated.split(chr(10)))} Zeilen")
    
    print("=" * 60)
    print("[SUCCESS] Abgeschlossen")
