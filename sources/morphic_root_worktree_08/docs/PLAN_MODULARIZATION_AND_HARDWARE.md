# Masterplan: Radialgo2 Modularisierung & Hardware-Evolution

**Ziel:** Transformation der Morphic Engine von einem monolithischen Skript zu einer modularen, hardware-adaptiven Plattform für Analyse und Harmonisierung (Windows Dev -> Linux Root Server).

## Phase 1: Stabilisierung & Modularisierung (Das Fundament)
*Status: Sofort umsetzbar auf Windows-Dev-PC*

### 1.1 Entflechtung des Monolithen (`main.py`)
Das aktuelle `main.py` (>7000 Zeilen) wird in funktionale Module zerlegt.
- **`apps/cli/profiles/`**: Jedes Profil (`gehirn`, `lymph`, `detox`...) bekommt eine eigene Definition (JSON/YAML oder Python-Klasse).
  - *Vorteil*: Neue Profile können per Datei hinzugefügt werden, ohne den Core-Code zu riskieren.
- **`apps/cli/reporting/`**: HTML- und PDF-Generierung wird ausgelagert.
- **`core/engine/`**: Die reine Berechnungslogik (Scoring, Resonanz) wird von der CLI-Eingabe getrennt.

### 1.2 Zentrales "Registry"-System
- Eine `Registry`-Klasse lädt beim Start alle verfügbaren Profile, Gruppen und NLS-Datenbanken.
- **Startup-Check**: Prüft sofort: "Sind alle Gruppen für Profil X vorhanden?". Keine "Silent Failures" mehr.

### 1.3 PowerShell-Brücke
- `Run-MultiplexScan.ps1` bleibt das User-Interface.
- Es ruft nicht mehr das riesige `main.py` auf, sondern gezielt Module (z.B. `python -m apps.cli.scan --profile gehirn`).

## Phase 2: Hardware-Abstraktions-Layer (HAL)
*Status: Vorbereitung für Linux-Portierung & Echtzeit-Hardware*

### 2.1 Hardware-Detection-Modul (`core/hardware/`)
Ein neues Modul, das beim Start die Umgebung scannt:
- **CPU/RAM**: Erkennt verfügbare Kerne (z.B. 12 Threads auf Ryzen 5, wie im Screenshot) und passt `top-k` oder Parallelisierung an.
- **GPU**: Prüft auf CUDA/ROCm (NVIDIA/AMD). Wenn vorhanden (z.B. RTX 4000 Ada), werden Matrix-Berechnungen dorthin ausgelagert (`accel_numpy`).
- **OS**: Unterscheidet Windows (lokal) vs. Linux (Server).

### 2.2 Sensor-Schnittstelle (Unified Sensor API)
Einheitliche Schnittstelle für externe Inputs:
- `USB-Edelstein-Sensor`: Ein Treiber-Modul liest Rohdaten.
- `Kozyrev-Dioden (Raspi)`: Empfängt Daten (z.B. über Netzwerk/Websocket oder Serielle Schnittstelle).
- Die Engine fragt nur: `get_sensor_input("kozyrev")` – egal, ob die Hardware lokal steckt oder simuliert wird (für Dev).

## Phase 3: Erweiterte Analyse & 3D (Innovation)

### 3.1 Integrierter 3D-Workflow
- Der 3D-Export (`nls3d_points`) wird fester Bestandteil der Pipeline.
- **Viewer**: Ein lokaler Webserver (z.B. FastAPI) liefert eine 3D-Ansicht (Three.js) aus, die direkt im Browser aufrufbar ist.

### 3.2 Kontext-Sensitives Scoring (AI-Ansatz)
- Die Engine bewertet nicht mehr nur isoliert ("Leber belastet"), sondern vernetzt:
- "Leber belastet" + "Emotion Wut" + "Schulter-Schmerz rechts" -> Höherer Score für "Leber-Meridian-Blockade".
- Nutzung lokaler LLMs (wie im Screenshot Llama 3.1/Qwen erwähnt), um diese Zusammenhänge textlich zu formulieren.

## Phase 4: Harmonisierungs-Engine (Realtime)
*Status: Planung basierend auf Timer-Screenshot*

### 4.1 Scheduler & Timer
- Implementierung eines Schedulers (ähnlich dem Screenshot), der Harmonisierungen zeitgesteuert ausführt.
- Läuft als Hintergrund-Dienst (Daemon auf Linux, Service auf Windows).

### 4.2 Output-Modulation
- Generierung von Frequenzen/Signalen basierend auf Analyse-Ergebnissen.
- Ausgabe über:
  - Audio (Soundkarte/Spulen)
  - Web-USB (für externe Hardware)
  - Netzwerksignale (für Remote-Harmonisierung)

## Nächste konkrete Schritte (Action Plan)

1.  **JETZT**: Backup erstellen.
2.  **SCHRITT 1**: Erstellen der Ordnerstruktur `apps/cli/profiles` und Auslagern der 3 neuen Profile (`gehirn`, `lymph`, `immun`) als Testballon.
3.  **SCHRITT 2**: Anpassen von `multiplex_scan` in `main.py`, um diese externen Profile zu laden.
4.  **SCHRITT 3**: Implementieren des "Startup-Checks" für Gruppen.

Danach ist das System stabil genug für die Hardware-Layer-Entwicklung.
