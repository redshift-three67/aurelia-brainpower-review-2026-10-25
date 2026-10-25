#!/usr/bin/env python3
"""
Erstellt einen Wiederherstellungspunkt für Codegeau v1.4.9.1
Direkter, vereinfachter Ansatz ohne komplexe Ausgabe-Pufferung
"""
import os
import shutil
import datetime
import sys

def main():
    print("=" * 70, flush=True)
    print("RESTORE POINT CREATOR - Codegeau v1.4.9.1", flush=True)
    print("=" * 70, flush=True)
    
    project_root = os.getcwd()
    print(f"\n[1] Project Root: {project_root}", flush=True)
    
    # Erstelle RestorePoints Verzeichnis falls nicht vorhanden
    restore_points_dir = os.path.join(project_root, "RestorePoints")
    if not os.path.exists(restore_points_dir):
        os.makedirs(restore_points_dir)
        print(f"[2] Created RestorePoints directory", flush=True)
    else:
        print(f"[2] RestorePoints directory exists", flush=True)
    
    # Zeitstempel für eindeutigen Namen
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(restore_points_dir, f"RestorePoint_v1491_PreBugfix_{ts}")
    
    print(f"[3] Backup destination: {backup_dir}", flush=True)
    
    # Definiere Ignore-Patterns
    ignore_patterns = [
        '__pycache__', '.git', 'venv', 'env', 'build_env',
        'RestorePoints', 'Analysen', 'Radi144',
        '*.pyc', '*.tmp', '*.wav', 'temp_group.json',
        'smoke_test_v140.py', '.pytest_cache', '.vscode',
        'restore_output.txt', 'create_restore_point.py'
    ]
    
    def ignore_func(directory, files):
        ignored = set()
        for pattern in ignore_patterns:
            for file in files:
                if pattern.replace('*', '') in file or file == pattern:
                    ignored.add(file)
        return ignored
    
    print(f"[4] Starting backup (ignoring {len(ignore_patterns)} patterns)...", flush=True)
    
    try:
        shutil.copytree(project_root, backup_dir, ignore=ignore_func)
        print(f"[5] SUCCESS: Backup completed", flush=True)
    except Exception as e:
        print(f"[ERROR] Backup failed: {e}", flush=True)
        return False
    
    # Erstelle RESTORE_INFO.txt
    print(f"[6] Creating RESTORE_INFO.txt...", flush=True)
    
    restore_info_path = os.path.join(backup_dir, "RESTORE_INFO.txt")
    try:
        with open(restore_info_path, "w", encoding="utf-8") as f:
            f.write("=" * 70 + "\n")
            f.write("RESTORE POINT INFORMATION\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Created: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Label: Pre-Bugfix Snapshot v1.4.9.1\n")
            f.write(f"Version: 1.4.9.1 (Adaptive Hardware & Client Synergy Edition)\n")
            f.write(f"Date: 05. Februar 2026\n\n")
            
            f.write("=" * 70 + "\n")
            f.write("FEATURES IN THIS SNAPSHOT\n")
            f.write("=" * 70 + "\n")
            f.write("- Adaptive HW Scaling (psutil, 80k-1M Kandidaten)\n")
            f.write("- UTF-8 BOM Fix fuer JSON Gruppen-Import\n")
            f.write("- Group Birth Place Integration (Geburtsort in Signatur)\n")
            f.write("- User Guide (DE) fuer Klienten\n")
            f.write("- Rekursiver DB-Scan mit Top-21 Ranking\n")
            f.write("- Audio-Harmonisierung mit Solfeggio-Layering\n")
            f.write("- Harmonizer mit Puls/Pause-Zyklen\n\n")
            
            f.write("=" * 70 + "\n")
            f.write("RECOVERY INSTRUCTIONS\n")
            f.write("=" * 70 + "\n")
            f.write("1. Copy entire folder to: C:\\Users\\<Username>\\CascadeProjects\\12x12\n")
            f.write("2. Overwrite existing files (Analysen folder will be preserved)\n")
            f.write("3. Run: setup_new_pc.bat (installs dependencies)\n")
            f.write("4. Test: generate_matrix.ps1\n\n")
            
            f.write("=" * 70 + "\n")
            f.write("KNOWN ISSUES (Fixed after this snapshot)\n")
            f.write("=" * 70 + "\n")
            f.write("B1: PkADDING typo in dev_cli.py line 282 (PDF padding missing)\n")
            f.write("B2: $u_ae/$u_ue variables undefined in generate_matrix.ps1\n")
            f.write("M1: REST API not updated to v1.4.9 features\n")
            f.write("M2: main.py version still 1.0.0\n\n")
            
            f.write("=" * 70 + "\n")
            f.write("DIRECTORY SIZE\n")
            f.write("=" * 70 + "\n")
        
        print(f"[7] RESTORE_INFO.txt created successfully", flush=True)
    except Exception as e:
        print(f"[WARNING] Could not create RESTORE_INFO.txt: {e}", flush=True)
    
    # Berechne Größe
    try:
        total_size = sum(
            os.path.getsize(os.path.join(dirpath, filename))
            for dirpath, dirnames, filenames in os.walk(backup_dir)
            for filename in filenames
        )
        size_mb = total_size / (1024 * 1024)
        print(f"[8] Backup size: {size_mb:.2f} MB", flush=True)
    except Exception as e:
        print(f"[WARNING] Could not calculate size: {e}", flush=True)
    
    print(f"\n[SUCCESS] Restore point created successfully!", flush=True)
    print(f"Location: {backup_dir}", flush=True)
    print("=" * 70, flush=True)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
