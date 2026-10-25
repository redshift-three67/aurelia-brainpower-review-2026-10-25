import os
import shutil
import datetime
import time

VERSION = "1.5.0"
VERSION_NAME = "EMF Compensation & Environmental Intelligence Edition"
LAST_UPDATE = "09. Februar 2026"

# Der Inhalt für die COMPLETE_SYSTEM_DESCRIPTION.md
SYSTEM_DESCRIPTION_CONTENT = """# 12x12 Resonance Matrix Engine – Vollständige Systembeschreibung (Developer Edition)

**Version:** 1.4.9 (Adaptive Hardware & Client Synergy Edition)  
**Stand:** 01. Februar 2026  
**Status:** Finalized & Validated  
**Zielgruppe:** Entwickler:innen, DevOps, technische Reviewer  

---

## 0. Kurzüberblick (Executive Snapshot)
Die **12x12 Resonance Matrix Engine** ist ein hybrides, hardware-adaptives System zur Berechnung radionischer Resonanzfelder. In der Version 1.4.9 wurde das System auf maximale Flexibilität und Benutzerfreundlichkeit optimiert. Es erkennt nun dynamisch die vorhandene Hardware (RAM, VRAM, CPU) und skaliert die Rechenlast automatisch für optimale Stabilität und Performance auf jedem Endgerät.

- **Adaptive Hardware-Skalierung:** Automatische Anpassung an High-End GPUs (RTX 4000 Ada), Standard-Laptops (Ryzen 9) und Office-PCs.
- **Erweiterte Gruppen-Analyse:** Einbindung des Geburtsorts für jedes Gruppenmitglied zur präziseren Signatur-Generierung.
- **Robustheit:** Fix des UTF-8 BOM Fehlers bei JSON-Importen und vollständige ASCII-Transition im UI.
- **Klienten-Dokumentation:** Neuer `USER_GUIDE_DE.md` für eine einfache Handhabung durch Endnutzer.

---

## 1. Architektur – Gesamtübersicht

### 1.1 Schichtenmodell (v1.4.9)
```
┌─────────────────────────────────────────────────────────────┐
│                     USER / ADMIN UI                         │
│     PowerShell CLI (ASCII) + Adaptive Group Entry           │
└─────────────────────────────────────────────────────────────┘
                         │ (Einzel / Gruppe / Geo)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION BRIDGE                       │
│        dev_cli.py (BOM-Fix, Adaptive HW Detection)          │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    CORE COMPUTATION LAYER                   │
│      ResonanceMatrixEngine (Dynamic Scaling: 80k - 1M)      │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              EXPORT + AUDIO + REPORTING LAYER               │
│      PDF / XLSX / Logs / Harmonizer / User Guide (DE)       │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Hardware-Adaption (Dynamisch)
Die Engine nutzt `psutil` und `torch.cuda`, um die Umgebung zu analysieren:
- **Extreme Mode (1M Kandidaten):** Aktiviert bei VRAM >= 20GB (z.B. RTX 4000 SFF Ada).
- **High Mode (500k Kandidaten):** Aktiviert bei VRAM >= 8GB.
- **Standard Mode (200k Kandidaten):** Standard für CUDA-Systeme.
- **CPU Optimized:** Skalierung basierend auf verfügbarem System-RAM (80k - 250k) und Thread-Optimierung für AMD Ryzen.

---

## 2. Funktionale Hauptmodule (v1.4.9 Updates)

### 2.1 Erweiterte Gruppen-Synergie
Der Gruppen-Flow erfasst nun Nachname, Vorname, Geburtsdatum **und Geburtsort**. Dies erhöht die Spezifität des kollektiven Resonanzfeldes signifikant. JSON-Importe unterstützen nun das `utf-8-sig` Format zur Vermeidung von BOM-Fehlern.

### 2.2 Klienten-Dokumentation
Mit dem `USER_GUIDE_DE.md` steht eine kompakte, verständliche Anleitung zur Verfügung, die Klienten hilft, die Bedeutung des Resonanz-Scores, der Farbmatrix und des HRV-Feedbacks zu verstehen.

---

## 3. Roadmap
- [x] v1.4.5: DB-Scan Edition (Auto-Resonanz Ranking)
- [x] v1.4.8: ASCII & Robust Encoding (Windows Stability Fixes)
- [x] v1.4.9: Adaptive Hardware & Client Synergy (Multi-PC Support)
- [ ] v1.5.0: Physische HRV-Hardware Integration & D-Wave Live API

**Ende der Systembeschreibung v1.4.9.**
"""

def create_restore_point():
    # 2. Write File
    target_file = os.path.join(os.getcwd(), "COMPLETE_SYSTEM_DESCRIPTION.md")
    try:
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(SYSTEM_DESCRIPTION_CONTENT)
        print(f"SUCCESS: System Description updated at {target_file}", flush=True)
    except Exception as e:
        print(f"ERROR: Could not write file: {e}", flush=True)

    # 3. Create Backup
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    project_root = os.getcwd()
    restore_points_dir = os.path.join(project_root, "RestorePoints")
    backup_dir = os.path.join(restore_points_dir, f"RestorePoint_v1491_PreBugfix_{ts}")
    
    # Ensure base RestorePoints dir exists
    if not os.path.exists(restore_points_dir):
        try:
            os.makedirs(restore_points_dir)
        except Exception as e:
            print(f"WARNING: Could not create base RestorePoints dir: {e}", flush=True)

    def ignore_func(directory, files):
        # Always ignore these to save space and avoid recursion
        base_ignores = [
            '__pycache__', '.git', 'venv', 'env', 'build_env', 
            'RestorePoints', 'Analysen', 'Radi144/Analysen',
            '*.pyc', '*.tmp', '*.wav', 'temp_group.json', 'smoke_test_v140.py'
        ]
        return set(shutil.ignore_patterns(*base_ignores)(directory, files))

    print(f"Starting backup from {project_root} to {backup_dir}...", flush=True)
    
    try:
        shutil.copytree(project_root, backup_dir, ignore=ignore_func)
        print(f"SUCCESS: Restore Point created at {backup_dir}", flush=True)
        
        # Create a README in the restore point
        readme_path = os.path.join(backup_dir, "RESTORE_INFO.txt")
        with open(readme_path, "w") as f:
            f.write(f"Restore Point created on {datetime.datetime.now()}\n")
            f.write(f"Label: Pre-Bugfix Snapshot v{VERSION}\n")
            f.write(f"Version: {VERSION} ({VERSION_NAME})\n")
            f.write(f"Date: {LAST_UPDATE}\n")
            f.write("\n")
            f.write("=== FEATURES ===\n")
            f.write("- Adaptive HW Scaling (psutil, 80k-1M Kandidaten)\n")
            f.write("- UTF-8 BOM Fix fuer JSON Gruppen-Import\n")
            f.write("- Group Birth Place Integration (Geburtsort in Signatur)\n")
            f.write("- User Guide (DE) fuer Klienten\n")
            f.write("- Rekursiver DB-Scan mit Top-21 Ranking\n")
            f.write("- Audio-Harmonisierung mit Solfeggio-Layering\n")
            f.write("\n")
            f.write("=== RECOVERY ANLEITUNG ===\n")
            f.write("1. Diesen Ordner komplett nach C:\\Users\\<User>\\CascadeProjects\\12x12 kopieren\n")
            f.write("2. Bestehende Dateien ueberschreiben (ACHTUNG: Analysen-Ordner bleibt erhalten)\n")
            f.write("3. setup_new_pc.bat ausfuehren (installiert Abhaengigkeiten)\n")
            f.write("4. generate_matrix.ps1 starten zum Testen\n")
            f.write("\n")
            f.write("=== BEKANNTE ISSUES (werden nach diesem Snapshot behoben) ===\n")
            f.write("- B1: PkADDING Tippfehler in dev_cli.py Zeile 282 (PDF Padding fehlt)\n")
            f.write("- B2: $u_ae/$u_ue Variablen nicht definiert in generate_matrix.ps1\n")
            f.write("- M1: REST API nicht auf v1.4.9 Features aktualisiert\n")
            f.write("- M2: main.py Version noch auf 1.0.0\n")
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"ERROR: Backup failed: {e}", flush=True)

if __name__ == "__main__":
    create_restore_point()
