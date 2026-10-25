# Developer Reproduction Guide – 12x12 Resonance Matrix Engine v1.5.0

**Ziel:** Exakte 1:1 Reproduktion der Applikation auf einem neuen System  
**Stand:** 09. Februar 2026  
**Zielgruppe:** Entwickler mit Python-Erfahrung

---

## 1. Voraussetzungen

### 1.1 Software

| Software | Version | Zweck |
|----------|---------|-------|
| Python | 3.10 – 3.12 | Runtime |
| Git | 2.x+ | Versionskontrolle |
| pip | 23.x+ | Paketmanagement |
| PowerShell | 5.1+ (Windows) / 7+ (Cross-Platform) | Interaktives UI |

### 1.2 Optionale Software

| Software | Version | Zweck |
|----------|---------|-------|
| NVIDIA CUDA Toolkit | 12.x | GPU-Beschleunigung |
| NVIDIA Driver | 535+ | GPU-Zugriff |

---

## 2. Projekt-Struktur (Vollständig)

```
12x12/
├── main.py                          # FastAPI Hauptanwendung (v1.5.0)
├── dev_cli.py                       # CLI Haupteinstiegspunkt (1127 Zeilen)
├── generate_matrix.ps1              # PowerShell Interaktives UI (611 Zeilen)
├── finalize_project.py              # Versions- und Restore-Point Management
├── requirements.txt                 # Python Dependencies
├── bio_knowledge.json               # Bio-energetische Wissensbasis
├── palettes.json                    # Farbpaletten-Definitionen
├── preset_profiles.json             # Analyse-Presets
│
├── app/
│   ├── __init__.py
│   ├── algorithms/
│   │   ├── __init__.py
│   │   ├── resonance_engine.py      # Kern-Engine (711 Zeilen)
│   │   ├── client_signature.py      # Klienten-Signatur Generator (316 Zeilen)
│   │   ├── emf_compensator.py       # EMF-Kompensation (793 Zeilen)
│   │   └── amplifier.py             # Amplifier-System (520 Zeilen)
│   ├── api/
│   │   ├── __init__.py
│   │   └── resonance.py             # REST/WebSocket API (558 Zeilen)
│   └── schemas/
│       ├── __init__.py
│       └── resonance.py             # Pydantic Schemas
│
├── data/
│   ├── amplifiers.json              # Amplifier-Registry (12 Einträge)
│   └── amplifier_images/            # Referenzbilder der Amplifier
│       └── .gitkeep
│
├── deploy/
│   ├── server.env                   # Linux Server Umgebungsvariablen
│   ├── resonance-engine.service     # systemd Service-Definition
│   └── setup_server.sh              # Automatisches Server-Setup
│
├── docs/
│   ├── AMPLIFIER_KONZEPT.md         # Amplifier Konzept & Architektur
│   ├── HARDWARE_REQUIREMENTS.md     # Hardware-Spezifikationen
│   ├── DEVELOPER_REPRODUCTION_GUIDE.md  # Dieses Dokument
│   └── SYSTEM_ARCHITECTURE_FLOW.md  # Flow-Diagramme
│
├── tests/
│   └── test_smoke.py                # Smoke Tests
│
└── RestorePoints/                   # Automatische Sicherungen
```

---

## 3. Installation (Schritt-für-Schritt)

### 3.1 Windows Development

```powershell
# 1. Repository klonen
git clone <repository-url> 12x12
cd 12x12

# 2. Virtual Environment erstellen
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Dependencies installieren
pip install --upgrade pip
pip install -r requirements.txt

# 4. PyTorch installieren (CPU-Version für Dev ohne NVIDIA)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
# ODER mit CUDA (wenn NVIDIA GPU vorhanden):
# pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# 5. Verifikation
python -c "import torch; print(f'PyTorch {torch.__version__}, CUDA: {torch.cuda.is_available()}')"
python -c "from app.algorithms.resonance_engine import ResonanceMatrixEngine; e = ResonanceMatrixEngine(); print(f'Engine OK: {e.hw_info}')"
python -c "from app.algorithms.amplifier import AmplifierVectorGenerator; a = AmplifierVectorGenerator(); print(f'Amplifier OK: {len(a.amplifiers)} registriert')"
```

### 3.2 Linux Debian Server

```bash
# 1. Als root auf dem Server
chmod +x deploy/setup_server.sh
./deploy/setup_server.sh

# Alternativ manuell:
# 1. System-Pakete
apt-get update && apt-get install -y python3.11 python3.11-venv python3.11-dev \
    git curl nvidia-driver-535 nvidia-cuda-toolkit

# 2. Benutzer & Verzeichnisse
useradd -r -s /bin/false resonance
mkdir -p /opt/resonance-engine /var/log/resonance-engine
chown -R resonance:resonance /opt/resonance-engine /var/log/resonance-engine

# 3. Deployment
rsync -av --exclude='RestorePoints' --exclude='__pycache__' ./ /opt/resonance-engine/
cd /opt/resonance-engine
python3.11 -m venv venv && source venv/bin/activate
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt

# 4. systemd Service
cp deploy/resonance-engine.service /etc/systemd/system/
systemctl daemon-reload && systemctl enable resonance-engine
systemctl start resonance-engine
```

---

## 4. Kern-Algorithmen (Detailliert)

### 4.1 Matrix-Berechnung (`resonance_engine.py`)

```
Eingabe: client_data, focus, focus_weight, palette, mode, amplifier
    │
    ├─ 1. Client-Signatur generieren (6 Komponenten + EMF-Korrektur)
    │     → client_vector = embed_signature(signature) → 256D Tensor
    │
    ├─ 2. Fokus-Vektor generieren (semantische Einbettung)
    │     → focus_vector = embed_focus(focus) → 256D Tensor
    │     → Optional: + bio_vector (Meridian/Chakra Frequenz)
    │
    ├─ 3. EMF-Kompensation (wenn aktiv)
    │     → client_vector = apply_compensation(client_vector)
    │     → focus_vector = apply_compensation(focus_vector)
    │
    ├─ 4. Hybrid-Suche (CUDA/CPU)
    │     → Generiere N Kandidaten-Matrizen (12x12, Werte 0-9)
    │     → Berechne Resonanz-Score = cosine_sim(flatten(matrix), combined_vector)
    │     → Gewichtung nach focus_weight (Sanft/Normal/Stark)
    │     → Top-10 nach Score sortiert
    │
    ├─ 5. Amplifier-Modulation (wenn aktiv)
    │     → Palette modulieren (Hue-Shift Richtung Amplifier-Farbe)
    │     → Amplifier-Empfehlung berechnen (Top-3)
    │
    └─ 6. Ausgabe: Matrix, Score, Palette, Amplifier-Info, EMF-Daten
```

### 4.2 Client-Signatur (`client_signature.py`)

```
Eingabe: first_name, last_names[], dob, place, planet?, image_path?
    │
    ├─ Komponente 1: Name-Frequenz
    │   → SHA-256(name) → Modulo 1000 → Normalisierung → Hz
    │
    ├─ Komponente 2: Geburtsdaten
    │   → Numerologische Quersumme → Frequenz-Mapping
    │   → Jahreszeit → Element-Modulation
    │
    ├─ Komponente 3: Bild-Hash (optional)
    │   → SHA-256(image_bytes) → Frequenz-Derivat
    │
    ├─ Komponente 4: Organuhr
    │   → Aktuelle Uhrzeit → Meridian-Zuordnung → Frequenz
    │
    ├─ Komponente 5: Planetarisch (optional)
    │   → Planet → Bekannte Resonanzfrequenz
    │
    ├─ Komponente 6: EMF-Korrektur (optional)
    │   → EMF-Index × Schumann-Harmonische → Korrekturfaktor
    │
    └─ Finale Signatur:
        frequency = Σ(component × weight) / Σ(weights)
```

### 4.3 EMF Compensator (`emf_compensator.py`)

```
Layer 1: SENSING (4 Software-Sensoren)
    ├─ CPU Timing Jitter (perf_counter_ns, 50 Zyklen)
    ├─ RNG Entropy Quality (os.urandom, Shannon + Chi² + Autokorrelation)
    ├─ GPU Thermal Noise (Basic: 256² / Server: 1024² + FFT + Drift + Memory)
    └─ System Load (psutil CPU + RAM)

Layer 2: PROFILING
    ├─ Kalibrierung (5× Baseline-Messungen)
    ├─ Composite EMF Index (gewichtet: 35% Entropy + 30% Jitter + 20% GPU + 15% Load)
    └─ Low-Noise Window Detection (Index < 0.3)

Layer 3: COMPENSATION
    ├─ Kompensationsvektor (12D, Schumann-basiert)
    ├─ Counter-Frequencies (Solfeggio, gewichtet nach EMF-Profil)
    └─ Timing-Empfehlung (proceed/wait/delay)

Layer 4: MONITORING (optional)
    └─ Hintergrund-Thread (alle 30 Sek Profiling, History)
```

### 4.4 Amplifier (`amplifier.py`)

```
Registry (amplifiers.json) → 12D Vektor pro Amplifier
    │
    ├─ Matching: Cosinus-Ähnlichkeit (Client 12D ↔ Amplifier 12D)
    │   + Element-Synergie (5-Elemente-Nährungs-Zyklus)
    │   + Property-Match (Fokus-Keywords ↔ Amplifier-Eigenschaften)
    │   → Score = 0.55×Cosinus + 0.20×Element + 0.25×Property
    │
    ├─ Audio-Modulation: Amplifier-Frequenzen als Sinuswellen-Layer
    │   → Basis + 3 Harmonische, abnehmende Amplitude (×0.8^n)
    │   → 8% der Hauptamplitude
    │
    ├─ Palette-Modulation: Hue/Sat/Val Shift Richtung Amplifier-Farbe
    │   → 15% Hue, 7.5% Saturation, 4.5% Value
    │
    └─ Umfeld-Sensor: Bild-Vergleich (Referenz ↔ Aktuell)
        → Delta: Helligkeit, Variation, Entropie → Change Score (0-1)
```

---

## 5. Daten-Dateien (Exakte Formate)

### 5.1 `bio_knowledge.json` (Struktur)

```json
{
  "chakras": {
    "muladhara": {"name": "Wurzelchakra", "frequency_hz": 256, "element": "Erde", "color": "#FF0000"},
    ...
  },
  "meridians": {
    "lunge": {"name": "Lunge", "frequency_hz": 220, "peak_time": "03:00-05:00", "element": "Metall"},
    ...
  },
  "elements": {
    "holz": {"name": "Holz", "frequency_hz": 294, ...},
    ...
  }
}
```

### 5.2 `palettes.json` (Struktur)

```json
{
  "Radionik (Standard)": {"0": "#FFFFFF", "1": "#FF0000", ..., "9": "#000000"},
  "Sanft (Pastell)": {"0": "#F5F5F5", ...},
  ...
}
```

### 5.3 `amplifiers.json` (Struktur)

```json
{
  "_meta": {"version": "1.5.0", ...},
  "amplifiers": {
    "rosenquarz": {
      "name": "Rosenquarz",
      "category": "heilstein",
      "base_frequency_hz": 350.0,
      "harmonics_hz": [350.0, 700.0, 1050.0, 175.0],
      "solfeggio_affinity": 639,
      "element": "Wasser",
      "chakra": "Herz",
      "chakra_index": 4,
      "color_hex": "#F7CAC9",
      "amplification_factor": 0.75,
      "properties": ["liebe", "heilung", "harmonie", "emotionale_balance"],
      "image_path": "data/amplifier_images/rosenquarz.jpg",
      "mohs_hardness": 7.0,
      "crystal_system": "trigonal"
    },
    ...
  }
}
```

---

## 6. API Referenz (Vollständig)

### 6.1 REST Endpoints

| Method | Pfad | Beschreibung | Body |
|--------|------|-------------|------|
| POST | `/api/v1/analyze-matrix` | Matrix-Analyse | `ResonanceAnalysisRequest` |
| GET | `/api/v1/emf/status` | EMF-Status | – |
| POST | `/api/v1/emf/enable` | EMF aktivieren | – |
| POST | `/api/v1/emf/disable` | EMF deaktivieren | – |
| GET | `/api/v1/emf/profile` | EMF-Profil | – |
| GET | `/api/v1/emf/monitor` | HTML Dashboard | – |
| GET | `/api/v1/amplifier/list` | Amplifier-Liste | – |
| POST | `/api/v1/amplifier/set/{name}` | Amplifier setzen | – |
| POST | `/api/v1/amplifier/clear` | Amplifier deaktivieren | – |
| POST | `/api/v1/amplifier/match` | Klienten-Matching | `{client_data, focus, top_n}` |
| POST | `/api/v1/amplifier/add` | Neuen Amplifier | `{id, data}` |

### 6.2 WebSocket Endpoints

| Pfad | Richtung | Beschreibung |
|------|----------|-------------|
| `/api/v1/emf/ws` | Server→Client | EMF Live-Daten (alle 5 Sek) |
| `/api/v1/emf/client-sensor` | Client→Server | Sensor-Daten (Audio, GPS, HRV) |

---

## 7. CLI Referenz (Vollständig)

```bash
python dev_cli.py \
  --surname "Mustermann" \           # Nachname (Pflicht)
  --firstname "Max" \                # Vorname (Pflicht)
  --dob "1990-01-15" \               # Geburtsdatum ISO (Pflicht)
  --place "Berlin" \                 # Geburtsort
  --planet "Venus" \                 # Planet (optional)
  --focus "Heilung;Schutz" \         # Fokus (Semicolon = Sequenz)
  --weight "Normal" \                # Deaktiviert|Sanft|Normal|Stark
  --palette "Focus+EMF Coherent" \   # Palette-Wahl
  --mode "quantum" \                 # quantum|precision
  --amplifier "rosenquarz" \         # Amplifier ID/Name
  --emf-compensate \                 # EMF-Kompensation
  --hrv-sim \                        # HRV-Simulation
  --quantum-active \                 # D-Wave Toggle
  --use-planetary \                  # Planetarische Signatur
  --harmonize \                      # Harmonisierung starten
  --audio \                          # Audio aktivieren
  --solfeggio "528" \                # 528|432|429.62
  --pulse 21 \                       # Impuls (Sek)
  --pause 14 \                       # Pause (Sek)
  --duration 1.0 \                   # Dauer (×21 Min)
  --group "gruppe.json" \            # Gruppen-Analyse
  --coords "52.52,13.405" \          # Geo-Koordinaten
  --db-path "remedies.txt" \         # Datenbank-Scan
  --db-scan                          # DB-Scan Modus
```

---

## 8. Tests

### 8.1 Smoke Test

```bash
python -c "
from app.algorithms.resonance_engine import ResonanceMatrixEngine
e = ResonanceMatrixEngine(use_cuda=False)
r = e.calculate_resonance(
    {'first_name': 'Test', 'last_names': ['User'], 'dob': '2000-01-01', 'birth_place': 'Berlin'},
    'Heilung', focus_weight='Sanft'
)
assert r['resonance_score'] > 0
assert len(r['matrix_12x12']) == 12
assert len(r['amplifier_recommendations']) > 0
print(f'Score: {r[\"resonance_score\"]:.4f}')
print(f'Amplifier Empfehlung: {r[\"amplifier_recommendations\"][0][\"name\"]}')
print('SMOKE TEST: PASSED')
"
```

### 8.2 Amplifier Test

```bash
python -c "
from app.algorithms.amplifier import AmplifierVectorGenerator
a = AmplifierVectorGenerator()
assert len(a.amplifiers) >= 12
matches = a.match_client({'frequency': 440, 'components': {}}, ['Heilung'])
assert len(matches) == 3
print(f'Top Match: {matches[0][\"name\"]} ({matches[0][\"score\"]*100:.1f}%)')
print('AMPLIFIER TEST: PASSED')
"
```

### 8.3 EMF Test

```bash
python -c "
from app.algorithms.emf_compensator import EMFCompensator
import torch
c = EMFCompensator(device=torch.device('cpu'))
p = c.profile_environment()
assert 0 <= p['composite_emf_index'] <= 1
assert 0 <= p['entropy_score'] <= 1
print(f'EMF Index: {p[\"composite_emf_index\"]:.4f}')
print('EMF TEST: PASSED')
"
```

---

## 9. Deployment Checkliste

### Windows

- [ ] Python 3.10+ installiert
- [ ] Virtual Environment erstellt & aktiviert
- [ ] `pip install -r requirements.txt` erfolgreich
- [ ] PyTorch installiert (CPU oder CUDA)
- [ ] `bio_knowledge.json` vorhanden
- [ ] `palettes.json` vorhanden
- [ ] `data/amplifiers.json` vorhanden
- [ ] Smoke Test bestanden
- [ ] `generate_matrix.ps1` ausführbar

### Linux Server

- [ ] NVIDIA Driver 535+ installiert
- [ ] CUDA Toolkit 12.x installiert
- [ ] Python 3.11 installiert
- [ ] PyTorch + cu121 installiert
- [ ] `torch.cuda.is_available()` = True
- [ ] systemd Service installiert & aktiv
- [ ] Port 8000 offen (Firewall)
- [ ] `/var/log/resonance-engine/` beschreibbar
- [ ] API erreichbar: `curl http://localhost:8000/docs`
- [ ] EMF Monitor: `http://SERVER:8000/api/v1/emf/monitor`
