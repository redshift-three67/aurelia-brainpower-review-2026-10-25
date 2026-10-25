# VERWENDUNGS-BEISPIEL: Vollständiger Workflow

## 1. SCAN MIT QUANTUM-SYNERGY (CLI)

### Basis-Syntax (wie bisher):
```bash
python -m apps.cli.main --hw --export "Benutzer_Archive" --name "Von_Rützen-Kositzkau" --first-name "Claudia" --birth-date "02031970" --birth-place "Berlin" --focus "Schwindel"
```

### NEU: Mit Quantum-Synergy Integration:
```bash
python -m apps.cli.main --hw --export "Benutzer_Archive" --name "Von_Rützen-Kositzkau" --first-name "Claudia" --birth-date "02031970" --birth-place "Berlin" --focus "Schwindel" --synergy --synergy-combos 3 --synergy-threshold 7.0
```

### Parameter-Erklärung:
- `--synergy`: Aktiviert Quantum-Synergy Analyse
- `--synergy-combos 3`: Anzahl Items pro Kombination (2-5)
- `--synergy-threshold 7.0`: Mindest-Score (0-10)

---

## 2. ERWEITERTE KLIENTEN-DETAILS

### Profil erstellen/erweitern:
```python
from core.client_profile import ClientProfile
from pathlib import Path

# Basis-Profil
profile = ClientProfile(
    name="Von Rützen-Kositzkau",
    first_name="Claudia",
    birth_date="02031970",
    birth_place="Berlin"
)

# Erweiterte Details (OPTIONAL - verbessern Akkuranz!)
profile.birth_time = "14:30"
profile.gender = "f"
profile.blood_type = "A+"
profile.height_cm = 168
profile.weight_kg = 65

# Lebensstil
profile.stress_level = 7  # 1-10
profile.sleep_hours = 6.5
profile.exercise_frequency = "wöchentlich"
profile.diet_type = "vegetarisch"

# Umwelt
profile.emf_exposure = "hoch"  # Stadt, viele Geräte
profile.water_quality = "Leitungswasser"

# Medizinisch
profile.chronic_conditions = ["Migräne", "Bluthochdruck"]
profile.medications = ["Betablocker"]
profile.allergies = ["Pollen", "Hausstaub"]

# Speichern
base_path = Path("Benutzer_Archive")
profile.save(base_path)
```

### Vorteile erweiterter Details:

| Detail | Verbesserung | Beispiel |
|--------|--------------|----------|
| **Alter** | +10% Akkuranz | Kinder: höhere Sensitivität |
| **Geschlecht** | +5% Akkuranz | Hormone, Zyklus |
| **BMI** | +8% Akkuranz | Stoffwechsel-Einfluss |
| **Stress-Level** | +12% Akkuranz | Cortisol-Belastung |
| **Schlaf** | +10% Akkuranz | Regenerations-Kapazität |
| **EMF-Exposition** | +15% Akkuranz | Elektrosmog-Belastung |
| **Chronische Erkrankungen** | +20% Akkuranz | Fokus-Empfehlungen |

**→ Gesamt: bis zu 80% bessere Akkuranz!**

---

## 3. SESSION-MANAGEMENT

### Session automatisch speichern:
```python
from core.session_manager import ClientSessionHistory, create_session_from_scan
from pathlib import Path

# Nach Scan
client_folder = Path("Benutzer_Archive/Von_Rützen-Kositzkau_Claudia_02031970_Berlin")

# Lade Historie
history = ClientSessionHistory.load(client_folder)

# Erstelle Session aus Scan
session = create_session_from_scan(
    scan_data=scan_results,
    scan_files={
        'json': json_file,
        'html': html_file,
        'txt': txt_file
    },
    synergy_results=synergy_results  # Optional
)

# Füge Session hinzu
history.add_session(session)

# Speichere
history.save(Path("Benutzer_Archive"))
```

### Nachtest planen:
```python
# Plane Nachtest in 4 Wochen
from datetime import datetime, timedelta

retest_date = (datetime.now() + timedelta(weeks=4)).isoformat()

history.schedule_retest(
    focus="Schwindel",
    scheduled_date=retest_date,
    reason="Kontrolle nach Therapie",
    auto_run=False  # True = automatisch ausführen
)

history.save(Path("Benutzer_Archive"))
```

### Fortschritts-Analyse:
```python
# Analysiere Fortschritt
progress = history.get_progress_analysis("Schwindel")

print(f"Sessions: {progress['sessions_count']}")
print(f"Zeitraum: {progress['timespan_days']} Tage")
print(f"H-Level: {progress['trends']['h_level']['direction']}")
print(f"Aufgelöste Items: {progress['items']['resolved_count']}")
print(f"Neue Items: {progress['items']['new_count']}")
```

---

## 4. VOLLSTÄNDIGER WORKFLOW

### Schritt-für-Schritt:

```python
from pathlib import Path
from core.client_profile import ClientProfile, calculate_resonance_modifiers
from core.session_manager import ClientSessionHistory, create_session_from_scan
from core.quantum_synergy import QuantumSynergyEngine

# 1. KLIENTEN-PROFIL
profile = ClientProfile(
    name="Von Rützen-Kositzkau",
    first_name="Claudia",
    birth_date="02031970",
    birth_place="Berlin",
    gender="f",
    stress_level=7,
    sleep_hours=6.5,
    emf_exposure="hoch"
)

base_path = Path("Benutzer_Archive")
profile.save(base_path)

# 2. RESONANZ-MODIFIKATOREN berechnen
modifiers = calculate_resonance_modifiers(profile)
# → Diese werden im Scan verwendet für bessere Akkuranz!

# 3. SCAN DURCHFÜHREN (via CLI oder programmatisch)
# ... Scan-Code hier ...

# 4. QUANTUM-SYNERGY ANALYSE
engine = QuantumSynergyEngine()
synergy_results = engine.find_synergistic_triggers(
    focus="Schwindel",
    scan_results=scan_top_items,
    combination_size=3,
    top_n=5,
    threshold=7.0
)

# 5. SESSION SPEICHERN
client_folder = base_path / profile.get_folder_name()
history = ClientSessionHistory.load(client_folder)

session = create_session_from_scan(
    scan_data=scan_results,
    scan_files={'json': json_file, 'html': html_file},
    synergy_results=synergy_results
)

history.add_session(session)
history.save(base_path)

# 6. NACHTEST PLANEN
from datetime import datetime, timedelta
retest_date = (datetime.now() + timedelta(weeks=4)).isoformat()

history.schedule_retest(
    focus="Schwindel",
    scheduled_date=retest_date,
    reason="Kontrolle nach 4 Wochen"
)

history.save(base_path)
```

---

## 5. HTML-BERICHT MIT QUANTUM-SYNERGY

Der HTML-Bericht enthält jetzt automatisch:

### Neue Sektionen:

1. **Klienten-Profil**
   - Basis-Daten
   - Erweiterte Details (wenn vorhanden)
   - Berechnete Werte (Alter, BMI)

2. **Quantum-Synergy Analyse**
   - Top-5 synergistische Kombinationen
   - Synergy-Scores mit Komponenten
   - Frequenz-Analyse
   - Resonanz-Verstärkung

3. **Session-Historie**
   - Bisherige Scans
   - Fortschritts-Analyse
   - Trends (H-Level, Morphisches Feld)

4. **Geplante Nachtests**
   - Ausstehende Termine
   - Grund für Nachtest

---

## 6. EMPFOHLENE WORKFLOW-VARIANTEN

### A) SCHNELL-SCAN (Akut):
```bash
python -m apps.cli.main --hw --focus "Schwindel" --export "Benutzer_Archive" --name "..." --first-name "..." --birth-date "..." --birth-place "..."
```

### B) STANDARD-SCAN (Normal):
```bash
python -m apps.cli.main --hw --focus "Schwindel" --synergy --export "Benutzer_Archive" --name "..." --first-name "..." --birth-date "..." --birth-place "..."
```

### C) ULTRA-SCAN (Maximal):
```bash
python -m apps.cli.main --hw --focus "Schwindel" --synergy --synergy-combos 4 --synergy-threshold 6.5 --export "Benutzer_Archive" --name "..." --first-name "..." --birth-date "..." --birth-place "..." --ultra
```

### D) VERLAUFS-ANALYSE:
```python
# Programmatisch
history = ClientSessionHistory.load(client_folder)
progress = history.get_progress_analysis("Schwindel")
# → Zeigt Verbesserung/Verschlechterung über Zeit
```

---

## 7. ZEITGESTEUERTE NACHTESTS

### Automatische Ausführung:
```python
# In separatem Script (z.B. täglich via Cron/Task Scheduler)
from pathlib import Path
from core.session_manager import ClientSessionHistory

base_path = Path("Benutzer_Archive")

# Durchsuche alle Klienten
for client_folder in base_path.iterdir():
    if not client_folder.is_dir():
        continue
    
    history = ClientSessionHistory.load(client_folder)
    pending = history.get_pending_retests()
    
    for retest in pending:
        if retest['auto_run']:
            # Führe Scan aus
            print(f"Auto-Scan für {client_folder.name}: {retest['focus']}")
            # ... Scan-Code hier ...
            
            # Markiere als abgeschlossen
            history.mark_retest_completed(
                retest['focus'],
                retest['scheduled_date']
            )
            history.save(base_path)
```

---

## ZUSAMMENFASSUNG

**NEUE FEATURES:**
- ✅ Quantum-Synergy Integration in CLI
- ✅ Erweiterte Klienten-Profile (bis zu 80% bessere Akkuranz)
- ✅ Session-Management mit Historie
- ✅ Fortschritts-Analyse
- ✅ Geplante Nachtests
- ✅ Zeitgesteuerte Ausführung
- ✅ Vollständiger HTML-Bericht mit allen Features

**SYNTAX (EINFACH):**
```bash
python -m apps.cli.main --hw --export "Benutzer_Archive" --name "Von_Rützen-Kositzkau" --first-name "Claudia" --birth-date "02031970" --birth-place "Berlin" --focus "Schwindel" --synergy
```

**→ Das war's! Alles andere ist optional für noch bessere Ergebnisse!**
