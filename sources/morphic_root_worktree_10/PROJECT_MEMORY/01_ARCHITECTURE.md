# MORPHIC ENGINE V1 - ARCHITEKTUR

**Basiert auf:** MORPHIC_ENGINE_V1_ANALYSE.md  
**Letztes Update:** 2025-12-15 21:15  
**Version:** 1.0 (Pre-Refactoring)

---

## SYSTEM-ÜBERBLICK

Morphic Engine V1 ist ein Analytics-System für homöopathische Mittelanalyse mit:
- **Quantum-Synergy Engine** (Grover-basierte Kombinationsanalyse)
- **Morphic Field Calculation** (Copen-Raten, NLS3D-Punkte)
- **Multi-Profile Support** (16+ Profile: Classical, Kent, Heel, OOREP, etc.)
- **LLM Integration** (Ollama für Beschreibungsgenerierung)
- **Hardware-Entropy Sources** (Quartz, Voltage Dividers, WebSocket)
- **3D Viewer** (Z-Anatomy Bridge)

---

## ORDNERSTRUKTUR (IST-ZUSTAND)

```
Morphic_Engine_V1/
├── apps/
│   ├── cli/
│   │   ├── main.py                    # 9543 Zeilen (MONOLITH!) 🔴
│   │   ├── commands/                  # Neu refactored (Phase 3)
│   │   │   ├── scan.py
│   │   │   ├── trend.py
│   │   │   ├── harmonize.py
│   │   │   ├── synergy.py
│   │   │   └── descriptions.py
│   │   └── profiles/
│   │       └── registry.py
│   ├── server/
│   │   └── websocket_server.py        # WebSocket Streaming
│   └── viewer/
│       └── z_anatomy_bridge.py        # 3D Visualisierung
│
├── config/
│   ├── hardware_profiles.py           # DEV/PROD Profile
│   └── detected_hardware.yaml         # Auto-generiert
│
├── core/
│   ├── quantum_synergy.py             # Grover-Algorithmus
│   ├── morphic_field.py               # Copen-Raten Berechnung
│   ├── levels/
│   │   └── level_resonance.py         # 15 Ebenen (C0-C14)
│   ├── profiles/
│   │   └── profile.py                 # Profil-Logik
│   ├── subgroups/
│   │   └── procedural_groups.py       # Subgruppen-Registry
│   ├── llm/
│   │   └── ollama_client.py           # LLM Integration
│   ├── hardware/
│   │   └── system_info.py             # Hardware-Detektion
│   └── db/
│       ├── descriptions_db.py         # SQLite für Beschreibungen
│       └── trend_db.py                # Trendanalyse-DB
│
├── providers/
│   └── hardware/
│       ├── hardware_entropy.py        # Entropy-Provider
│       └── entropy_sources.py         # Quartz/Voltage/WebSocket
│
├── services/
│   ├── hardware_modulation.py         # Hardware-Steuerung
│   └── subgroup_service.py
│
├── tools/
│   ├── trend_analyzer.py
│   ├── pdf_exporter.py                # PDF-Export (pdfkit)
│   └── batch_descriptions.py
│
├── monitoring/
│   └── health.py                      # Health-Checks
│
├── cli/
│   └── utils/
│       ├── backup.py                  # Backup-Decorator
│       └── logging.py                 # JSON-Logging
│
├── tests/
│   ├── exploratory/                   # Explorative Tests
│   └── test_*.py                      # Unit Tests
│
├── kozyrev-diodes-research/           # Experimentell (separates Projekt)
│   └── src/kozyrev/
│
├── PROJECT_MEMORY/                    # Memory-System (NEU)
│   ├── 00_CURRENT_STATE.md
│   ├── 01_ARCHITECTURE.md             # Diese Datei
│   ├── 02_CHANGES_LOG.md
│   ├── 03_DECISIONS.md
│   ├── 04_FILE_REGISTRY.md
│   └── snapshots/
│
├── requirements.txt                   # Dependencies
├── PROJECT_STATE.md                   # Alt (wird migriert)
└── MORPHIC_ENGINE_V1_ANALYSE.md       # Ursprungsanalyse
```

---

## MODULE & DEPENDENCIES

### Core Module
```python
core.quantum_synergy          # Grover-Suche, Quantum-Synergy
core.morphic_field            # Morphic Field Calculation
core.profiles.profile         # Profil-Management
core.levels.level_resonance   # 15-Ebenen-System
core.nls3d_points_new         # 3D Punkt-Mapping
```

### CLI Module
```python
apps.cli.main                 # Haupt-Entry-Point (MONOLITH)
apps.cli.commands.*           # Separierte Befehle (NEU)
cli.utils.backup              # Backup-Decorator
cli.utils.logging             # JSON-Logging
```

### Hardware Module
```python
providers.hardware.hardware_entropy      # Entropy-Generierung
providers.hardware.entropy_sources       # Quartz/Voltage/WebSocket
config.hardware_profiles                 # DEV/PROD Profile
services.hardware_modulation             # Hardware-Steuerung
```

### LLM Module
```python
core.llm.ollama_client        # Ollama API Integration
core.item_description_generator
tools.batch_descriptions
```

---

## DATENBANKEN

### 1. descriptions.db
```sql
CREATE TABLE descriptions (
    item TEXT PRIMARY KEY,
    description TEXT,
    model TEXT,
    timestamp TEXT
);
```

### 2. trend.db
```sql
CREATE TABLE scans (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    profile TEXT,
    top_items TEXT  -- JSON
);
```

### 3. synergy.db (fragmentiert)
- Synergie-Kombinationen

### 4. harmonize.db (fragmentiert)
- Harmonisierungs-Daten

---

## PROFILE-SYSTEM

### Verfügbare Profile
```python
PROFILES = [
    "homeopathy_classical",      # OOREP (2432 Mittel)
    "kent_repertory",            # Kent (10000+ Rubriken)
    "heel_complex",              # Heel (120+ Komplexmittel)
    "schüssler",                 # Schüssler-Salze (12+15)
    "bach_flowers",              # Bach-Blüten (38)
    "nutramedix",                # Nutramedix-Tropfen
    "dmso_okoubaka",             # DMSO/Okoubaka
    # ... 10+ weitere
]
```

### Profil-Registry
```python
# apps/cli/profiles/registry.py
def get_groups_for_profile(profile: str) -> List[str]
```

---

## HARDWARE-PROFILE

### DEV Profile (Windows, iGPU)
```yaml
max_llm_params_b: 3.0          # Max 3B Parameter
llm_quantization: Q4_K_M       # 4-bit
max_workers: 4
use_gpu_acceleration: false
max_prefilter_items: 200
max_combinations: 5000
```

### PROD Profile (Linux, RTX 4000)
```yaml
max_llm_params_b: 14.0         # Max 14B Parameter
llm_quantization: Q8_0         # 8-bit
max_workers: 12
use_gpu_acceleration: true     # CUDA
max_prefilter_items: 500
max_combinations: 50000
```

---

## KRITISCHE ISSUES (aus Analyse)

### 🔴 KRITISCH
1. **main.py Monolith:** 9543 Zeilen, 378 KB
2. **Backup-Dateien:** 189 gelöscht (Phase 1 ✅)
3. **Dependencies:** Unvollständig (Phase 2 🔄)

### 🟠 HOCH
4. **Duplizierte Module:** core/hardware vs providers/hardware
5. **Inkonsistente Profile:** 3 Speicherorte
6. **Test-Organisation:** tests/ vs Root

### 🟡 MITTEL
7. **Datenbank-Fragmentation:** 4 separate DBs
8. **Keine Migrations:** Keine DB-Versionierung

---

## MIGRATIONS-PLAN (8 Phasen)

1. ✅ **Phase 1: Cleanup** (1 Woche) - ABGESCHLOSSEN
2. 🔄 **Phase 2: Dependencies** (2 Tage) - IN ARBEIT
3. ⏸️ **Phase 3: main.py Refactoring** (2 Wochen)
4. ⏸️ **Phase 4: Test-Abdeckung** (1 Woche)
5. ⏸️ **Phase 5: Datenbank-Konsolidierung** (1 Woche)
6. ⏸️ **Phase 6: Modul-Deduplizierung** (3 Tage)
7. ⏸️ **Phase 7: Monitoring/Logging** (3 Tage)
8. ⏸️ **Phase 8: Server-Deployment** (1 Woche)

**Geschätzte Gesamtdauer:** 7-8 Wochen

---

## TECHNOLOGIE-STACK

### Python Packages
```
numpy>=1.26              # Numerik
scipy>=1.11              # Scientific Computing
pydantic>=2.0            # Validation
typer[all]>=0.9          # CLI Framework
fastapi>=0.110           # Web Server
websockets>=12.0         # WebSocket Support
psutil>=5.9              # System Info
matplotlib>=3.8          # Plotting
pdfkit>=1.0              # PDF Export
pytest>=7.4              # Testing
```

### Externe Services
- **Ollama:** LLM Backend (localhost:11434)
- **wkhtmltopdf:** PDF-Generierung (für pdfkit)

### Hardware-Integration
- **Serial:** USB Voltage Dividers (pyserial)
- **USB-HID:** Quartz Oscillator Sensors
- **WebSocket:** Browser-basierte Entropy-Quellen
- **CUDA:** GPU-Beschleunigung (PROD only)

---

## NOTIZEN

- Architektur wird während Refactoring aktualisiert
- Kozyrev-Diodes: Separates Research-Projekt (optional)
- 3D-Viewer: Integration mit Z-Anatomy (experimentell)

---

**Nächstes Update:** Nach Phase 3 (main.py Refactoring)
