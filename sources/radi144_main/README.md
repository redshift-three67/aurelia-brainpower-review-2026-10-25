# 12x12 Resonance Matrix Engine (Standalone)

High-Performance Radionics Matrix Engine with CUDA Acceleration and Coherent Color Generation.

## Features

*   **12x12 Matrix Analysis**: Computes resonance patterns across $10^{144}$ possibilities.
*   **CUDA Acceleration**: Uses NVIDIA RTX GPU Tensor Cores for massive parallel processing.
*   **Coherent Color Mapping**: Generates symmetrical color palettes based on spectral resonance logic (0-9).
*   **FastAPI Backend**: Modern, asynchronous API for easy integration.

## Setup

Radi144 verwendet jetzt einen harten Runtime-Preflight (Option A).
Das bedeutet:

- ohne vollständigen Pflicht-Stack startet das System bewusst nicht
- die bevorzugte Projekt-Runtime ist eine lokale virtuelle Umgebung unter `.venv`
- die Batch-Skripte (`install_dependencies.bat`, `run.bat`, `run_test.bat`) nutzen diese `.venv` automatisch, falls sie vorhanden ist

Empfohlener Setup-Pfad unter Windows:

1.  Ensure **Python 3.10+** is installed.
2.  Starte `install_dependencies.bat`
3.  Das Skript erstellt automatisch eine lokale Projektumgebung unter `.venv`
4.  Danach werden alle Pflichtabhängigkeiten installiert und die Runtime direkt verifiziert

Manueller Alternativpfad:

```bash
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Wichtige Pflichtpakete:

- `torch`
- `numpy`
- `fastapi`
- `reportlab`
- `openpyxl`

Für den verifizierten API-Test-Stack ist zusätzlich relevant:

- `httpx<0.28`

Hinweis:
Für CUDA-Support muss weiterhin eine zur GPU-/Treiberlage passende PyTorch-Runtime verfügbar sein.

## Running

Bevorzugt:

- Doppelklick auf `run.bat`

oder manuell mit der lokalen Projektumgebung:

```bash
.venv\Scripts\python.exe main.py
```

`run.bat` führt vor dem Start einen harten Runtime-Preflight aus.
Wenn Pflichtabhängigkeiten fehlen, wird der Start bewusst abgebrochen.

The server will start at `http://localhost:8000`.

## API Usage

**Endpoint**: `POST /api/v1/analyze-matrix`

**Request**:
```json
{
  "focus": "Harmonische Regulation",
  "client_data": {
    "first_name": "Max",
    "last_names": ["Mustermann"],
    "birth_date": "1990-01-01",
    "birth_place": "Berlin"
  },
  "matrix_size": 12
}
```

**Response**:
Returns the 12x12 integer matrix, the corresponding color matrix (hex codes), and resonance score.

Verifizierter aktueller API-/Runtime-Stand:

- `client_id` ist API-seitig jetzt eine echte Runtime-Registry-ID (`cli-...`) statt eines rein semantischen Platzhalters
- API-Analysen werden in die gemeinsame Runtime-Verwaltungsdomäne unter `data/runtime/` gespiegelt
- `POST /api/v1/analyze-matrix` liefert Header `X-Client-ID` und `X-Session-ID`
- `POST /api/v1/export/pdf` kann bei mitgeliefertem `session_id` + `output_path` ein PDF schreiben, im Report-Manifest registrieren und `X-Artifact-ID` zurückgeben
- `generate_matrix.ps1` liest Template-Historie bevorzugt ueber eine generierte Runtime-Leseansicht `data/runtime/powershell_templates.json`
- `data/session_templates.json` bleibt als Legacy-Fallback erhalten

## Developer Tools (CLI)

Für schnelle Tests auf einem Development-PC steht ein PowerShell-Skript zur Verfügung.

**Features:**
*   Interaktive Eingabe (Name, Vorname, Geburtsort)
*   Datumseingabe im Format DDMMYYYY (z.B. 20031967)
*   **Fokus-Historie:** Zeigt die letzten 10 Eingaben zur schnellen Auswahl
*   **Gewichtung:** Sanft, Normal oder Stark für die Fokus-Priorisierung
*   Sofortige Berechnung der 12x12 Matrix
*   **NEU:** Hochauflösender PDF & Excel Export im Ordner `Analysen`
*   Ausgabe des **144-stelligen Raten-Strings** (für Radionik-Geräte)
*   Automatische Speicherung in `dev_results.txt` (Log)

**Nutzung:**
Rechtsklick auf `generate_matrix.ps1` -> *Mit PowerShell ausführen*

Oder im Terminal:
```powershell
.\generate_matrix.ps1
```

Für einen direkten CLI-Smoketest steht zusätzlich `run_test.bat` zur Verfügung.
Dieses Skript nutzt ebenfalls den harten Runtime-Preflight und bevorzugt die lokale `.venv`.

## Troubleshooting Audio

Falls es Probleme mit der Audio-Ausgabe (Knacken, Pulsieren oder kein Ton) gibt:

1.  **Treiber-Updates**: Stellen Sie sicher, dass Ihre Audio-Treiber (Realtek, ASIO, etc.) auf dem neuesten Stand sind.
2.  **Lautstärke**: Überprüfen Sie den Windows-Mixer. Die Engine nutzt die Standard-Audioausgabe.
3.  **Berechtigungen**: Unter Windows kann `winsound` blockiert werden, wenn eine andere Anwendung exklusiven Zugriff auf das Audio-Gerät hat.
4.  **Dateizugriff**: Die Engine erstellt temporäre `.wav` Dateien im System-Temp-Ordner. Stellen Sie sicher, dass keine Antiviren-Software den Zugriff blockiert.
5.  **CPU-Last**: Bei extrem hoher CPU-Last kann es zu Aussetzern kommen, obwohl der Buffer auf 30 Sekunden ausgelegt ist.

---

## Entwickler-Informationen (Neu)

### Presets
Presets können in `preset_profiles.json` definiert werden. Sie erlauben den schnellen Start mit vorkonfigurierten Fokus-Texten und Gewichtungen.
Nutzung: `python dev_cli.py --preset chakra:muladhara`

### Tests
Die Systemstabilität sollte bevorzugt in der lokalen Projektumgebung geprüft werden:

```bash
.venv\Scripts\python.exe -m pytest tests -q
```

Verifizierter Stand dieser Codebasis:

- komplette Testsuite: `44 passed`
- API-TestClient-Kompatibilität abgesichert
- Engine-CPU-Speicherschutz für Precision-Mode verifiziert
- Runtime-Verwaltungsdomäne fuer Client Registry, Session Archive und Report Manifest verifiziert
- PowerShell-Runtime-Metadatenadapter fuer Template-Historie verifiziert
- CLI-Smoketest über `run_test.bat` erfolgreich

Dabei werden u. a. validiert:

- Runtime-Dependency-Preflight
- API-Vektorpfade
- Audio-Header-Integrität
- Engine-Grundfunktion (Smoke Test)
