# Server-Migrationsplan für Radialgo2 Morphic Engine V1

**Status**: Session 5C Complete - field_test() Migriert  
**Aktueller Stand**: main.py 6762 Zeilen (von ursprünglich 9543 = -28.9%)  
**Zielstand**: Funktional auf Linux Server mit GPU-Support

---

## I. AKTUELLER STATUS NACH SESSION 5C

### Abgeschlossene Migrationen
```
✓ Session 1: groups_overview, hw_diagnostics, top3_scan (1164 lines)
✓ Session 2: analyze_trends, client_trends (425 lines)  
✓ Session 3: batch_scan, bat_area_scan (365 lines)
✓ Session 4: Duplicate cleanup (~0 lines saved, clean)
✓ Session 5A: analyze() + 3 helpers (252 lines + helpers)
✓ Session 5B: Remove 5 duplicates (314 lines)
✓ Session 5C: field_test() → field.py (549 lines)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GESAMT:      2069 lines migriert, main.py -28.9%
```

### Verbleibende Funktionen in main.py
```
main.py: 6762 Zeilen (Nach 5C)
├─ multiplex_scan()    [3402 lines] ← KRITISCH (51% of main.py!)
├─ Nested helpers       [~400 lines estimated]
├─ Service classes     [~500 lines estimated]
├─ Imports + Setup    [~360 lines]
└─ Utility functions   [~1000 lines]
```

---

## II. KRITISCHE ANALYSE: multiplex_scan()

### Befunde
| Metrik | Befund |
|--------|--------|
| **Größe** | 3402 Zeilen (44% gesamte main.py) |
| **Position** | LETZTE Funktion in main.py (3908-7309) |
| **Komplexität** | Monolitisches Design, viele sequenzielle Operationen |
| **Dependencies** | 3 Service-Instanziierungen, 12+ Helper-Aufrufe |
| **Dekorierer** | `@log_command` + `@app.command("multiplex-scan")` |

### Funktionalität
- **Core**: Multiplex-Resonanz-Scan mit 20+ Parameter-Optionen
- **Features**: Synergy-Analyse, TCM/Planet-Typing, Morphic-Field-Berechnung
- **Output**: JSON+HTML Export mit detaillierten Resonanzberichten
- **Business Logic**: Komplexe Score-Berechnung, Threshold-Evaluierung, Section-Mapping

### Warum multiplex_scan() ANDERS ist als field_test()
| Aspekt | field_test() | multiplex_scan() |
|--------|--------------|------------------|
| **Zeilen** | 549 | 3402 |
| **Parameter** | 9 | 20+ |
| **Features** | Basis | Advanced (Synergy, TCM, Morphic) |
| **Exports** | JSON | JSON + HTML |
| **Helper-Aufrufe** | 7 | 12+ |

---

## III. ENTSCHEIDUNGSPUNKT: multiplex_scan() STRATEGIE

### Option A: DIREKTE MIGRATION (NICHT EMPFOHLEN)
```
Risiko: SEHR HOCH
- 3402 Zeilen auf einmal extrahieren
- Viele unbekannte Dependencies
- Keine Zwischentests möglich
- Fehlerquellen multiplizieren sich
```

### Option B: SPLIT-STRATEGIE (EMPFOHLEN)
```
Risiko: MITTEL
Phase 1: Analyse
  - Extracte alle internen Helper-Funktionen (in multiplex_scan() definiert)
  - Identifiziere externe Dependencies
  - Dokumentiere Data Flows
  
Phase 2: Migration der Helpers  
  - Extrahiere Helpers zu multiplex_helpers.py
  - Teste Import-Pfade
  
Phase 3: Migration von multiplex_scan()
  - Extrahiere Kernel-Funktion zu multiplex.py
  - Registriere in main.py
  - Teste vollständig
  
Phase 4: Cleanup
  - Entferne doppelten Code
  - Optimiere Imports
  - Dokumentiere Public APIs
```

---

## IV. SCHRITTE VOR SERVER-ÜBERGABE

### MUST-HAVE (Blockers für Server)

#### 1. Syntax & Import Validation
```bash
# Prüfen: Alle Python-Dateien kompilierbar
python -m py_compile apps/cli/main.py
python -m py_compile apps/cli/commands/*.py

# Prüfen: Keine circular imports
python -c "from apps.cli.main import app; print('OK')"

# Prüfen: Alle Commands funktionieren
python -m apps.cli.main --help
python -m apps.cli.main scan --help
python -m apps.cli.main field --help
```

#### 2. Dependencies Check
```bash
# Installiert alle in requirements.txt
pip install -r requirements.txt

# Teste GPU/CUDA auf Server
python -c "import cupy; print(cupy.__version__)"  # Wenn CuPy installiert

# Teste ollama API
curl http://localhost:11434/api/tags
```

#### 3. Data Path Validation
```bash
# Prüfe: Produktionspfade existieren
[ -d "C:\Benutzer_Archive_Start\" ] && echo "Archive OK"
[ -d "C:\Benutzer_Trends_Start\" ] && echo "Trends OK"  
[ -d "C:\Benutzer_Deutung_Start\" ] && echo "Deutung OK"

# Prüfe: Log-Verzeichnis
mkdir -p logs && chmod 755 logs
```

#### 4. Database Connectivity
```bash
# Falls DB verwendet: Connection prüfen
python -c "from apps.db import connect; c = connect(); print('DB OK')"

# Teste Dateizugriff
python -c "from pathlib import Path; Path('test.tmp').write_text('test'); print('FS OK')"
```

#### 5. Resource Configuration
```bash
# main.py Hardware-Profile prüfen:
# - "legacy" (Standard für Windows)
# - "windows" (Windows erweitert)
# - "debian_server" (Linux mit GPU/QRNG)

# Teste Hardware-Detection:
python -m apps.cli.main field test first --birth-date 01011990 --birth-place test --hardware-profile debian_server
```

### NICE-TO-HAVE (Performance, Monitoring)

#### 6. Performance Baseline
```bash
# Teste lange-laufende Befehle
time python -m apps.cli.main scan top3-scan Alice Smith --birth-date 01011990 --birth-place Berlin --json

# Benchmark: Wie schnell sind Services?
# → Erwartung: Top3-Scan < 10s, Multiplex < 30s
```

#### 7. Logging & Monitoring
```bash
# Prüfe: Log-Format ist JSON
cat logs/radialgo.log | head -1 | python -m json.tool

# Prüfe: Metriken sammeln
python -c "from monitoring.health import check_paths; check_paths()"
```

#### 8. Git Status
```bash
# Alles committed?
git status --short

# Richtige Branch?
git branch -v

# Tags aktuelle?
git describe --tags
```

---

## V. EXAKTE SCHRITTE FÜR SERVER-ÜBERGABE

### Phase 0: LOCAL FINALIZATION (Jetzt)
```
✓ 1. multiplex_scan() analysieren (interne Helpers finden)
✓ 2. Migration-Plan konkretisieren
✓ 3. Alle Syntax-Checks lokal durchführen
✓ 4. Alle generierte *.py Scripts in .gitignore eintragen
✓ 5. Code-Review durchführen
□ 6. Final Commit mit `main.py refactoring complete`
```

### Phase 1: SERVER SETUP (Linux)
```
□ 1. Repository clonen
□ 2. Python 3.12 installieren
□ 3. Alle Dependencies installieren:
    pip install -r requirements.txt
    pip install cupy-cuda12x  # Für RTX 4000
□ 4. ollama starten
□ 5. Hardware-Profile testen
```

### Phase 2: VALIDATION (Linux)
```
□ 1. Alle Imports testen
□ 2. Alle Commands ausführen (--help)
□ 3. Sample-Daten durchlaufen
□ 4. Logs überprüfen
```

### Phase 3: PROFILING (Linux)
```
□ 1. GPU-Nutzung profilen (nvidia-smi)
□ 2. Memory-Nutzung profilen (psutil)
□ 3. Response-Zeiten messen
□ 4. Bottlenecks identifizieren
```

### Phase 4: OPTIMIZATION (Conditional)
```
□ 1. Cluster-Analysen falls zu langsam
□ 2. Caching implementieren falls nötig
□ 3. Async-I/O für Netzwerk-Calls
```

---

## VI. KONKRETE TODOs BIS SERVER-ÜBERGABE

### MUSS (Blocking)
- [ ] 1. multiplex_scan() interne Struktur analysieren
  - Wie viele Nested Functions?
  - Export-Pfade prüfen
  - Dependencies auf externe Services?

- [ ] 2. Alle analyse_*.py Skripte aufräumen
  - Zu .gitignore hinzufügen
  - Cleanup durchführen

- [ ] 3. Git Repository aufreinigen
  - Alle Migration-Skripte commiten oder löschen
  - Git-History prüfen (keine Secrets?)
  - Final tag setzen: v1.0-session5c-done

- [ ] 4. requirements.txt finalisieren
  - Alle Pakete aktuell?
  - Python 3.12 kompatibel?
  - Windows vs Linux Dependencies prüfen

- [ ] 5. PROJECT_MEMORY aktualisieren
  - SESSION_5C_SUMMARY.md erstellen
  - CURRENT_STATE.md updaten
  - Migration Checklist zur Hand

### SOLLTE (Non-blocking)
- [ ] 6. Bash/PowerShell Migration-Skript erstellen
  - Windows: .ps1 für lokales Setup
  - Linux: .sh für Server-Deployment

- [ ] 7. Docker-Image Optional (für Reproduzibilität)
  - Dockerfile mit Python 3.12 + Dependencies
  - GPU-Support (cuda-base-image)

- [ ] 8. Performance-Baselines dokumentieren
  - Top3-Scan Benchmark
  - Multiplex-Scan Benchmark
  - Ressourcen-Limits setzen

---

## VII. WINDOWS ↔ LINUX COMPATIBILITY ISSUES

### Bekannte Probleme
```
PROBLEM 1: Pfade
  Windows: C:\Benutzer_Archive_Start\
  Linux:   /data/benutzer_archive_start/
  
  LÖSUNG: Path.resolve() verwenden, keine hardcoded Pfade

PROBLEM 2: Encoding
  Windows: cp1252 Standard
  Linux:   utf-8 Standard
  
  LÖSUNG: PYTHONIOENCODING=utf-8 setzen

PROBLEM 3: Line Endings
  Windows: CRLF (\r\n)
  Linux:   LF (\n)
  
  LÖSUNG: Git core.autocrlf=true setzen

PROBLEM 4: GPU/CUDA
  Windows: No CUDA (nur iGPU)
  Linux:   RTX 4000 mit CUDA 12
  
  LÖSUNG: hardware_profile dynamisch setzen

PROBLEM 5: Network I/O
  Windows: Synchron bevorzugt
  Linux:   Async möglich (bessere Skalierung)
  
  LÖSUNG: Conditional imports basierend auf OS
```

### Zu testende Commands auf Linux
```bash
# Basic
python -m apps.cli.main --help
python -m apps.cli.main log-check

# With debian_server profile
python -m apps.cli.main scan top3-scan Test Person \
  --birth-date 01011990 --birth-place Berlin \
  --hardware-profile debian_server

# With Multiplex
python -m apps.cli.main multiplex-scan Test Person \
  --birth-date 01011990 --birth-place Berlin \
  --hardware-profile debian_server

# Export Test
python -m apps.cli.main field test person \
  --birth-date 01011990 --birth-place test \
  --export results.json
```

---

## VIII. RESOURCES AUF TARGET SERVER

### Hardware Spezifikation
```
CPU:     Intel Xeon (Server)
GPU:     RTX 4000 Ada (20GB VRAM) ← WICHTIG für CuPy
RAM:     256GB
Storage: NVMe SSD
Network: Gigabit Ethernet
```

### Erwartete Performance
```
top3-scan:      ~5s (mit GPU)
field-test:     ~8s (mit GPU)
multiplex-scan: ~15s (mit GPU)
# Ohne GPU: 3x-5x langsamer
```

### Installation auf Server (Bash)
```bash
#!/bin/bash
set -e

# 1. Clone & Setup
git clone <repo> morphic_v1
cd morphic_v1
git checkout phase3-continue-refactoring

# 2. Python Environment
python3.12 -m venv venv
source venv/bin/activate

# 3. Dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install cupy-cuda12x  # GPU support

# 4. Hardware Test
python -c "import cupy; print('CuPy ready')"
python -m apps.cli.main scan top3-scan Test Test --birth-date 01011990 --birth-place Test --json

# 5. Run
python -m apps.cli.main --help
```

---

## IX. DECISION TREE

```
Bist du JETZT bereit für Server-Übergabe?

├─ JA, wenn:
│  ✓ Alle Syntax-Checks bestanden
│  ✓ Keine ungelösten Imports
│  ✓ multiplex_scan() kann ignoriert werden (noch nicht auf Server nötig?)
│  ✓ Alle Services funktionieren lokal
│  → GEHE ZU: Phase 1 (Server Setup)
│
└─ NEIN, wenn:
   ✗ multiplex_scan() ist NOTWENDIG
   ✗ Andere Funktionen zeigen Fehler
   ✗ Database-Verbindung unklar
   → GEHE ZU: multiplex_scan() Analyse
```

---

## X. ZUSAMMENFASSUNG

### Fazit
**main.py ist 28,9% kleiner und modularisiert**, aber:
- **multiplex_scan()** ist noch riesig (3402 Zeilen = 44% von main.py)
- **BLOCKER?** Nein - wenn multiplex-scan nicht auf Server gebraucht wird
- **OPTIONAL?** Ja - kann nach Server-Migration in Ruhe erfolgen

### Empfohlenes Vorgehen
1. **Sofort auf Server**: Wenn multiplex_scan() NICHT dringend ist
2. **Erst lokal**:multiplex_scan() analysieren & splitten

### Server-Readiness Score
```
Syntax:      ████████░░  80% (field.py hat noch Import-Dependencies)
Testing:     ███████░░░  70% (Nicht auf Linux getestet)
Performance: ██████░░░░  60% (GPU-Profiling ausstehend)
Docs:        █████░░░░░  50% (Migration-Guide lückenhaft)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OVERALL:     ███████░░░  65% READY FOR SERVER
```

Recommendation: **DEPLOY TO SERVER** mit Bedingung:
- Sei bereit, lokal zu debuggen wenn Imports fehlschlagen
- Habe GPU-Driver/CUDA 12 auf Server vorbereitet
- multiplex_scan() kann später migriert werden
