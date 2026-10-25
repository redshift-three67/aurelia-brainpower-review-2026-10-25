# Radi144 – Tiefenanalyse des Ist-Zustands

Stand: 2026-06-03
Projektwurzel: `C:\Users\Hubert111\Documents\Radi144`
Analysemodus: Read-only-Analyse mit gezielter Reproduktion von Start-/Import-/Testfehlern

Nachtrag 2026-06-04 (verifiziert):

- Die zuvor geplante Verwaltungsdomäne fuer `Client Registry`, `Session Archive` und `Report Manifest` ist inzwischen produktiv angeschlossen.
- API-Analysen werden jetzt als Sessions gespiegelt; echte Runtime-`client_id`-Aufloesung und PDF-Manifest-Registrierung sind verifiziert.
- Der fruehere CPU-Speicher-/Crash-Blocker im Precision-Pfad der Engine wurde durch einen defensiveren CPU-RAM-Guard vor der Kandidatenerzeugung stabilisiert; der Guard budgetiert jetzt konservativer (inkl. Similarity-Anteil, CPU-Cap 128 MiB, 20% Available-RAM-Obergrenze).
- Zusaetzlich wurde die Testinfrastruktur gegen lokales `tests`-Package-Shadowing abgesichert (`tests/__init__.py`).
- Aktueller verifizierter Teststand: `29 passed, 9 warnings`.
- Verifizierter Git-Befund dieser lokalen Arbeitskopie: Das Projekt liegt unter `C:\Users\Hubert111\Documents\Radi144`, waehrend der aktive Git-Root `C:\Users\Hubert111` ist; projektbezogene Statuspruefungen muessen daher mit Pfadfilter gegen `Documents/Radi144` erfolgen und zeigen aktuell untracked Projektartefakte statt eines isolierten Repo-Status.

Nachtrag 2026-06-08 (lokale Linux-Arbeitskopie verifiziert):

- Radi144 liegt jetzt als isoliertes lokales Git-Repository unter `/home/klaus999/projects/Radi144` vor.
- Die kuratierte lokale Baseline ist committed; der Arbeitsbaum war vor diesem Dokumentationsschritt sauber.
- Phase 4 des Session-/Klienten-/Report-Architekturplans ist adapterartig umgesetzt: `generate_matrix.ps1` liest Template-Historie bevorzugt aus einer generierten Runtime-Leseansicht `data/runtime/powershell_templates.json`.
- Die Leseansicht wird aus `data/runtime/sessions.json` und `data/runtime/clients.json` ueber `export_powershell_templates_from_runtime_dir(...)` erzeugt.
- `data/session_templates.json` bleibt als Legacy-Fallback erhalten.
- Core-Engine, Matrixlogik, Resonanzscore, DB-Ranking, EMF, Audio und Harmonizer-Timing blieben unveraendert.
- Aktueller verifizierter Teststand nach Phase 4: `44 passed`.
- Details: `docs/PHASE4_POWERSHELL_METADATA_STATUS_2026-06-08.md`.

---

## 1. Ziel dieser Analyse

Diese Analyse beschreibt den aktuellen technischen Ist-Zustand des Projekts `Radi144` über die gesamte Struktur hinweg.

Schwerpunkte:

- Gesamtstruktur des Repositories
- tatsächlicher Workflow aus Code, nicht nur aus Dokumentation
- Step-/Substep-Logik des Hauptablaufs
- Echtzeitengine und ihre Funktionalitäten
- Hardwareanbindungen und deren realer Reifegrad
- Session-, Klienten-, Harmonisierungs- und Reporting-Strukturen
- Stabilität, Akkuranz und Startfähigkeit des Gesamtsystems
- reproduzierte Abhängigkeitsprobleme, insbesondere `torch`

Wichtiger Hinweis:
Diese Datei begann als read-only Bestandsaufnahme. Sie wurde danach um einen verifizierten Nachtrag ergänzt, der die inzwischen real umgesetzte Option-A-Runtime-Stabilisierung dokumentiert.

---

## 2. Executive Summary

`Radi144` ist aktuell kein einzelnes konsistentes Laufzeitsystem, sondern ein Verbund aus fünf Ebenen:

1. Windows-Launcher / Bedienfluss über `generate_matrix.ps1`
2. Python-CLI-Orchestrierung über `dev_cli.py`
3. FastAPI-Backend über `main.py` + `app/api/resonance.py`
4. Berechnungskern über `app/algorithms/resonance_engine.py`
5. Sensorik-/EMF-/Amplifier-/Signaturmodule über `app/algorithms/*`

Der Funktionsumfang im Code ist breit:

- Matrixanalyse 12x12 / 24x24 / 36x36
- Klienten-Signaturbildung
- Gruppen-, Geo-, Bild- und DB-bezogene Analysepfade
- EMF-Profiling mit Continuous-Monitoring und WebSocket-Streams
- Amplifier-Matching und Audio-Frequenzlogik
- PDF-/Excel-Export
- Session-Template-Speicherung
- Harmonizer-UI mit Audio und Step-Sequenzen

Gleichzeitig war die reale Betriebsstabilität zum Analysezeitpunkt zunächst eingeschränkt:

- `torch` fehlte im aktiven Python-Environment
- `numpy` fehlte ebenfalls im aktiven Python-Environment
- dadurch scheiterten Engine, API, `main.py`, große Teile der Tests und Teile der CLI sofort beim Import
- der dokumentierte Mock-/Fallback-Gedanke in `dev_cli.py` wurde durch frühe Importabhängigkeiten nur teilweise wirksam
- mehrere Funktionen sind stärker konzeptuell oder placeholderhaft als produktionsreif, insbesondere D-Wave-/Quantum-Refinement und echte Hardware-EMF-Sensorik

Kernaussage:
Das Projekt ist funktional ambitioniert und architektonisch weit entwickelt. Der ursprüngliche Hauptblocker lag nicht im Algorithmus selbst, sondern in der frühen harten Importkette auf `torch` und `numpy`. Dieser Blocker wurde nach der Analyse durch eine harte Option-A-Runtime-Stabilisierung behoben; die strukturellen Architekturthemen bleiben jedoch bestehen.

---

## 3. Verifizierter Projekt-Ist-Zustand

### 3.1 Zentrale Dateien und Rollen

| Pfad | Rolle im System | Befund |
|---|---|---|
| `main.py` | FastAPI-Einstiegspunkt | bindet Router ein und führt jetzt einen harten Runtime-Preflight aus |
| `generate_matrix.ps1` | primärer Windows-Workflow / UI / Launcher | umfangreiche Eingabe-, Template-, History-, Parsing- und Harmonisierungslogik |
| `dev_cli.py` | zentrale Python-CLI / Batch-Workflow / Export / Harmonizer | funktionsreich; jetzt mit hartem Runtime-Preflight vor dem eigentlichen Ablauf |
| `app/api/resonance.py` | HTTP-/WebSocket-Orchestrierung | viele Analyse-, Export-, DB-, EMF- und Monitoring-Endpunkte |
| `app/algorithms/resonance_engine.py` | Kernengine | Hardwareerkennung, Vektorbildung, Matrixsuche, Paletten, EMF-/Amplifier-Integration |
| `app/algorithms/emf_compensator.py` | Echtzeit-EMF-Modul | Baseline, Profiling, Kompensation, Continuous Monitoring, WebSocket-Callbacks, SDR-Plug-in-Schnittstelle |
| `app/algorithms/client_signature.py` | Signaturgenerator | Klienten-, Bild-, Bio- und optionale Kontextsignatur |
| `app/algorithms/amplifier.py` | Amplifier-Matching | Matching, Projektion, Farblogik, Audiofrequenz-Unterstützung |
| `app/schemas/resonance.py` | API-Schemata | Request-/Response-Strukturen für Analyse und EMF |
| `app/schemas/klienten.py` | Klientenmodell | Pydantic-Klientenobjekte, aber keine echte Persistenzschicht |
| `requirements.txt` | deklarierte Kernabhängigkeiten | enthält jetzt zusätzlich `httpx<0.28` zur verifizierten API-TestClient-Kompatibilität |
| `install_dependencies.bat` | Windows-Installer | erstellt jetzt eine lokale `.venv`, installiert Pflichtpakete und verifiziert die Runtime aktiv |
| `run.bat` | API-Start | bevorzugt `.venv\Scripts\python.exe` und führt vor dem Start einen harten Preflight aus |
| `run_test.bat` | CLI-Teststart | bevorzugt `.venv\Scripts\python.exe`, führt Preflight aus und verifiziert den CLI-Pfad |
| `docs/HARDWARE_REQUIREMENTS.md` | Soll-Hardwarebild | beschreibt Dev-PC und Zielserver; teils konzeptionell, nicht gleichbedeutend mit Live-Zustand |
| `docs/SYSTEM_ARCHITECTURE_FLOW.md` | vorhandene Architekturdoku | hilfreich als Referenz, aber nicht ausreichend als alleinige Wahrheit |
| `data/session_templates.json` | Session-Template-Ablage | vorhanden, strukturelle Persistenz bestätigt |
| `last_session.json` | letzte Session | vorhanden |
| `focus_history.txt` | Fokushistorie | vorhanden |
| `Analysen/` | Berichts-/Artefaktordner | Zielordner für Reports und Exporte |

### 3.2 Tatsächliche Modulgruppen

Das Projekt gliedert sich funktional in folgende Cluster:

1. Start-/Bedienebene
   - `generate_matrix.ps1`
   - `run.bat`
   - `run_test.bat`
   - `install_dependencies.bat`

2. Service-/API-Ebene
   - `main.py`
   - `app/api/resonance.py`
   - `app/schemas/*`

3. Rechen- und Signalebene
   - `app/algorithms/resonance_engine.py`
   - `app/algorithms/client_signature.py`
   - `app/algorithms/emf_compensator.py`
   - `app/algorithms/amplifier.py`

4. Persistenz-/Artefakt-Ebene
   - `data/session_templates.json`
   - `last_session.json`
   - `focus_history.txt`
   - `Analysen/`
   - `bio_knowledge.json`
   - `db_import/`

5. Test- und Validierungsebene
   - `tests/test_engine_smoke.py`
   - `tests/test_engine_regressions.py`
   - `tests/test_api_vector_modes.py`
   - `tests/test_audio_checksum.py`

---

## 4. Der reale Gesamtworkflow

## 4.1 Top-Level-Orchestrierung

Es existieren parallel drei primäre Einstiegspfade:

### Pfad A – API-Betrieb
1. `run.bat`
2. bevorzugt `.venv\Scripts\python.exe main.py`
3. `main.py` importiert `app.api.resonance`
4. `app/api/resonance.py` importiert `ResonanceMatrixEngine`
5. vor dem Fachablauf greift ein harter Runtime-Preflight
6. Engine initialisiert sich beim Modulimport
7. API stellt HTTP-/WebSocket-Endpunkte bereit

### Pfad B – Interaktiver Windows-Workflow
1. Benutzer startet `generate_matrix.ps1`
2. PS1 liest letzte Session / Templates / Historie
3. PS1 sammelt Klient-, Fokus- und Konfigurationsdaten
4. PS1 startet `dev_cli.py` mit Parametern
5. PS1 parst Marker-Ausgabe (`###TOP21###`, `###DBRANK###` etc.)
6. PS1 steuert Folgeaktionen wie Harmonisierung, Audio, Maps, Verlauf

### Pfad C – Direkter CLI-/Batch-Betrieb
1. bevorzugt `.venv\Scripts\python.exe dev_cli.py ...`
2. harter Runtime-Preflight validiert Pflicht-Stack
3. Argumentparser normalisiert Modus, Fokus, Presets, Exporte, Harmonisierung
4. Engine/Signatur/Analysepfad laufen direkt in Python
5. Exporte und Session-Artefakte werden im Dateisystem erzeugt

---

## 4.2 Sequenzieller Analyseablauf in fachlichen Steps

Die eigentliche Analyse besteht aus einer wiederkehrenden Pipeline.

### Step 1 – Eingabeaufnahme

Substeps:
1. Klientendaten erfassen
   - Name / Vorname
   - Geburtsdatum
   - Geburtsort
   - optional Planet / Zusatzkontext
2. Fokus erfassen
   - Freitext
   - DB-basierter Fokus
   - Historienauswahl
   - mehrteilige Fokussequenz
3. Modusparameter erfassen
   - `matrix_size`
   - `mode = quantum|precision`
   - `hrv_sim`
   - `quantum_active`
   - `use_planetary`
   - `emf_compensate`
   - `amplifier`
   - `symmetry`
   - `palette`
   - `harmonize`
   - `audio`

Befund:
Die Eingabeschicht ist vor allem in `generate_matrix.ps1` und `dev_cli.py` implementiert. Sie ist breit, aber verteilt.

### Step 2 – Kontextanreicherung / Session-Wiederverwendung

Substeps:
1. `last_session.json` laden
2. `data/session_templates.json` laden
3. `focus_history.txt` laden
4. Presets aus `preset_profiles.json` laden
5. bestehende Template-Konfigurationen in neue Session übernehmen

Befund:
Dieser Teil ist real vorhanden, aber nicht zentral abstrahiert. Sessionlogik lebt teils im PS1-Workflow, teils in der CLI.

### Step 3 – Signaturbildung

Substeps:
1. Standard-Klientensignatur auf Basis von Personendaten bilden
2. optional Gruppenvektor bilden
3. optional Geo-Vektor bilden
4. optional Bildsignatur erzeugen
5. optional planetarische Modulation berücksichtigen
6. optional EMF-Kompensation bereits in die Signaturentstehung einbeziehen

Befund:
Die Signaturbildung ist ein echter Kernbaustein. API-seitig wird sogar zwischen direkter Klientensignatur und vorab berechneter Signatur für Gruppe/Geo/Bild/DB unterschieden.

### Step 4 – Bio-/Fokus-Kontext erkennen

Substeps:
1. Fokustext normalisieren
2. Chakra-/Meridian-Treffer in `bio_knowledge.json` suchen
3. bei Treffer Bio-Frequenz einbetten
4. Bio-Info für Reporting und Ranking anhängen

Befund:
Dieser Pfad ist im Engine-Code real verdrahtet und wird auch durch Regressionstests adressiert.

### Step 5 – EMF-Profiling und Kompensation

Substeps:
1. optional EMF-Kompensation aktivieren
2. EMF-Compensator initialisieren
3. Baseline-Kalibrierung durchführen
4. aktuelles Umfeld profilieren
   - Entropie
   - Timing-Jitter
   - Systemlast
   - GPU-Noise
   - optional SDR-Daten
5. Kompensationsvektor berechnen
6. Client- und Fokusvektor modulieren

Befund:
Das ist keine reine Attrappe. Es gibt eine echte Software-Sensorik. Die echte Hardwaretiefe bleibt jedoch begrenzt, solange kein SDR-Backend und keine externen Sensorbrücken aktiv sind.

### Step 6 – Matrixsuche / Kernberechnung

Substeps:
1. Berechnungsmodus bestimmen
   - `precision` = deterministisch
   - `quantum` = stochastisch
2. Seed ableiten
3. Kandidatenmenge aus Hardwareprofil bestimmen
4. Client- und Fokusvektor in den Suchraum geben
5. Top-K-Matrizen berechnen
6. Score und Intensität ableiten

Befund:
Das Hauptprogramm ist sequentiell logisch sauber aufgebaut. Die Engine entscheidet hardwareabhängig über Kandidatenvolumen und unterstützt mehrere Matrixgrößen. Der eigentliche Kernpfad ist sequenziell orchestriert, obwohl Teiloperationen intern auf Torch-Tensorik beruhen.

Verifizierter Nachtrag 2026-06-04:
Im CPU-Pfad existiert jetzt zusaetzlich ein defensiver RAM-Guard vor der eigentlichen Suche. Er begrenzt die Kandidatenzahl konservativ anhand verfuegbaren Speichers und eines festen Sicherheitsbudgets. Damit wurde der zuvor reproduzierbare Precision-Crash auf diesem Host beseitigt, ohne Scoring-, Seed- oder Ranking-Logik fachlich umzubauen.

### Step 7 – Nachbearbeitung

Substeps:
1. Element-/Bio-Validierung auf Top-Ergebnisse anwenden
2. optional D-Wave-Refinement ausführen
3. optional Symmetrisierung anwenden
   - none
   - horizontal
   - quadrant
4. Amplifier-Modulation einfügen
5. Top-3-Amplifier-Empfehlungen erzeugen
6. Farbmatrix generieren

Befund:
Die Postprocessing-Stufe ist stark ausgebaut. Der D-Wave-Teil ist jedoch aktuell eher vorbereitend als belastbar produktiv.

### Step 8 – Ergebnisbereitstellung

Substeps:
1. Matrixdaten serialisieren
2. Farbraster ableiten
3. Score / Intensität / Hardware-Info zurückgeben
4. `top_10` generieren
5. Bio-Info, Amplifier, EMF-Info einhängen

Befund:
Die Response-Struktur ist relativ reichhaltig und wird für API, CLI und Exporte wiederverwendet.

### Step 9 – Export / Archivierung

Substeps:
1. Ausgabeordner unter `Analysen/` erzeugen
2. PDF generieren
3. Excel generieren
4. Kombinationsberichte erzeugen
5. Session-Template speichern
6. letzte Session aktualisieren

Befund:
Exports sind fachlich integriert, aber paketabhängig. Unter dem neuen Option-A-Verhalten gelten `reportlab` und `openpyxl` explizit als Pflichtpakete; bei Fehlen wird der Start bewusst abgebrochen.

### Step 10 – Harmonisierung / Übertragung

Substeps:
1. aus den Analyseergebnissen eine Übertragungsmenge ableiten
2. typischerweise Top-3-Varianten pro Fokus nutzen
3. Tkinter-Fenster erzeugen
4. Step-/Pause-Zyklen fahren
5. optional Audio synthetisieren
6. Session-Audio als WAV exportieren
7. Abschluss und Status visualisieren

Befund:
Die Harmonisierung ist nicht nur ein Report-Label, sondern ein eigener nachgelagerter Runtime-Abschnitt mit GUI-, Timing- und Audiozustand.

---

## 4.3 Workflow speziell aus `generate_matrix.ps1`

`generate_matrix.ps1` ist derzeit die beste Darstellung des sequentiellen Bedienablaufs.

### Primäre PS1-Steps

1. Initialisierung
   - Sessionpfade setzen
   - Templates/Historie vorbereiten
   - Eingabestand rekonstruieren

2. Interaktive Datenerhebung
   - Klientendaten
   - Fokus
   - Historie / Wiederverwendung
   - Konfigurationsoptionen

3. Python-Aufruf vorbereiten
   - CLI-Parameter zusammensetzen
   - Zielmodus / Palette / Matrixgröße / Flags setzen

4. `dev_cli.py` starten
   - Ausgabe in Textform konsumieren
   - Markerblöcke extrahieren

5. Marker-Parsing
   - `###TOP21### ... ###ENDTOP21###`
   - `###DBRANK### ... ###ENDDBRANK###`
   - Folgeentscheidungen daraus ableiten

6. Folgeaktionen
   - Bericht / Ordner / Persistenz
   - Harmonisierung
   - optionale Nebenschritte

### Bewertung

`generate_matrix.ps1` ist de facto ein Anwendungs-Frontend und kein bloßes Hilfsskript. Es koppelt Bedienung, Persistenz, Parametrisierung und Folgeworkflow stark aneinander. Das macht den Ablauf für einen Einzelplatznutzer praktisch, erzeugt aber strukturelle Redundanz gegenüber API und CLI.

---

## 5. Echtzeitengine und Funktionalitäten

## 5.1 Engine-Initialisierung

Die `ResonanceMatrixEngine` initialisiert beim Start:

1. Gerätetyp (`cpu`, `cuda`, `mps`)
2. RAM-basierte Kandidatenanzahl
3. optional CUDA-/TF32-Optimierungen
4. CPU-Threadoptimierung
5. Signaturgenerator
6. D-Wave-Vorbereitung
7. HRV-State
8. EMF-Subsystem
9. Amplifier-System
10. Bio-Wissensbasis

Wichtig:
`torch` wird auf Zeile 1 von `app/algorithms/resonance_engine.py` importiert. Dadurch bleibt die gesamte Engine bewusst hart importgebunden. Diese Kopplung ist unter Option A jetzt ein absichtliches Betriebsprinzip statt eines unbeabsichtigten Bootstrap-Fehlers.

## 5.2 Unterstützte Matrixgrößen

Verifiziert im Code:

- 12x12: immer verfügbar
- 24x24: ebenfalls freigeschaltet
- 36x36: nur als verfügbar markiert, wenn CUDA mit mindestens 8 GB VRAM erkannt wird

## 5.3 Berechnungsmodi

### Precision-Modus
- deterministischer Seed aus `first_name + birth_date + focus`
- Torch-RNG-State wird gesichert und am Ende wiederhergestellt
- explizit testbar und reproduzierbar angelegt

### Quantum-Modus
- stochastischer Pfad
- stärker heuristisch und nicht im Sinne echter Quantenhardware zu verstehen

## 5.4 EMF-Echtzeitfunktionalitäten

Verifiziert in `app/algorithms/emf_compensator.py`:

- CPU-Timing-Jitter-Messung
- Entropieanalyse über `os.urandom`
- Systemlast-Profiling über `psutil` oder Fallbackschätzung
- GPU-Noise-Messung
  - Basic-Mode
  - Server-Mode mit FFT-/Drift-/Timing-Analyse
- Baseline-Kalibrierung
- Composite-EMF-Index
- Timing-Empfehlung (`OPTIMAL`, `GUT`, `MODERAT`, `KRITISCH`)
- Continuous Monitoring im Hintergrundthread
- WebSocket-Broadcast-Callbacks
- Counter-Frequency-Ableitung
- SDR-Backend-Schnittstelle

Bewertung:
Die EMF-Engine ist softwareseitig vergleichsweise weit ausgebaut. Ihre reale Aussagekraft hängt aber direkt von der realen Verfügbarkeit von `torch`, `numpy`, `psutil` und optionalem Sensor-Backend ab.

## 5.5 WebSocket-Echtzeitpfade

Verifiziert in `app/api/resonance.py`:

- `/emf/ws`
  - liefert Status-/Monitoringdaten zyklisch
  - sendet Fehlerzustände, wenn kein EMF-Compensator initialisiert ist

- `/emf/client-sensor`
  - nimmt Sensordaten von Clientgeräten entgegen
  - vorgesehen für Audio, Standort, HRV, Gerätesensoren

Bewertung:
Die Realtime-Schnittstellen existieren real. Es gibt damit eine tragfähige Grundlage für Live-Monitoring. Vollständig produktionsreif ist das erst mit stabiler Session-/Client-/Persistenzkopplung.

---

## 6. Hardwareanbindungen – realer Reifegrad

## 6.1 Verifizierte aktuelle Host-Hardware

Per WMIC/Runtime geprüft:

- CPU: `AMD Ryzen 9 8945HS with Radeon 780M Graphics`
- RAM: ca. `16 GB`
- GPU: `AMD Radeon(TM) 780M Graphics`
- Betriebssystem: Windows 10

## 6.2 Tatsächlich nutzbare Hardwarepfade im Code

### Direkt real nutzbar
- CPU
- RAM-basierte Skalierung
- Windows-Audio über `winsound`
- Tkinter-UI für Harmonizer
- Systemmetriken über `psutil` sofern installiert

### Bedingt nutzbar
- GPU nur über `torch.cuda` bzw. MPS-Pfade
- auf dem aktuellen Host ist keine CUDA-Nutzung zu erwarten
- GPU-Noise-Logik ist vorhanden, aber für NVIDIA-CUDA-Setups gedacht

### Vorbereitet, aber nicht nativ verdrahtet
- RTL-SDR über Plug-in-Interface
- Clientsensorik via WebSocket-Bridge
- HRV-Wearable via externer Brücke
- Geodaten als semantischer Eingangspfad
- Bildsignaturpfad via Datei/Base64

## 6.3 Kritischer Befund zur Hardwarewahrheit

Die Hardwaredokumentation ist ambitioniert und beschreibt ein Zielsystem, aber der aktuelle Codezustand auf dem analysierten Windows-Host läuft faktisch im CPU-/Software-Proxy-Modus. Echte EMF-Hardwaremessung ist derzeit optional vorbereitet, nicht zentral implementiert oder standardmäßig aktiv.

---

## 7. Zentrale Analyse- und Harmonisierungsverwaltung

Dieser Abschnitt beschreibt den derzeitigen Ist-Zustand und die Architekturfragmentierung.

## 7.1 Aktueller Ist-Zustand

Es gibt keine einzelne zentrale Verwaltungsinstanz für:

- Analysejobs
- laufende Harmonisierungssessions
- Sessionhistorie
- Klientenstammdaten
- Report-Index
- Parallelstatus

Stattdessen ist die Funktionalität verteilt:

- Analyse-Parameter: `generate_matrix.ps1`, `dev_cli.py`, API-Requests
- Session-Templates: `data/session_templates.json`
- letzte Session: `last_session.json`
- Fokusverlauf: `focus_history.txt`
- Berichte/Artefakte: `Analysen/`
- laufende Harmonisierung: Tkinter-Objekt in `dev_cli.py`
- EMF-Livezustände: In-Memory in `EMFCompensator`
- Clientmodelle: nur Schemata, keine echte DB-Persistenz

## 7.2 Architektonische Bewertung

Es existiert funktional bereits eine implizite zentrale Verwaltung, aber nicht als eigener sauberer Domänenkern. Stattdessen lebt die Verwaltung verteilt in:

- Dateisystem
- Prozessspeicher
- PS1-UI-Zustand
- API-Engine-Zustand
- CLI-Zustand

## 7.3 Harmonisierungsempfehlung auf Architekturebene

Aus Analyseperspektive sollte die künftige zentrale Verwaltungsdomäne logisch in fünf Register zerlegt werden:

1. Analysis Registry
   - Analyse-ID
   - Inputkontext
   - Modus
   - Engineparameter
   - Ergebnisstatus
   - Reportpfade

2. Session Registry
   - Session-ID
   - Start-/Endzeit
   - Bezug zu Analyse
   - Harmonizer-State
   - Audio-Artefakte
   - EMF-Kontext

3. Client Registry
   - Client-ID
   - Stammdaten
   - Historie der Analysen
   - aktive / archivierte Sessions

4. Harmonization Runtime Registry
   - laufende Übertragungen
   - parallele Sessions
   - Pulse-/Pause-Zustände
   - Audio-/EMF-Zusatzlayer

5. Report Registry
   - PDF/XLSX/WAV/JSON-Artefakte
   - Dateipfade
   - Generierungszeit
   - Zugehörigkeit zu Session und Analyse

Wichtig:
Dies ist keine Implementierungsanweisung, sondern die zentrale Harmonisierung der aktuellen verteilten Zustände in ein belastbares Architekturmodell.

---

## 8. Session-Archiv

## 8.1 Aktueller Ist-Zustand

Vorhandene Session-nahe Speicherorte:

- `last_session.json`
- `data/session_templates.json`
- `focus_history.txt`
- `Analysen/<timestamp_name>/...`

## 8.2 Stärken

- echte Persistenz existiert bereits
- Templates sind wiedernutzbar
- Analyseordner strukturieren Ergebnisartefakte pro Lauf
- History ist benutzbar für den UI-Workflow

## 8.3 Schwächen

- kein einheitliches Sessionmodell
- keine klare Trennung zwischen Template, Session, Analyse und Report
- keine zentrale Indexdatei für alle Runs
- keine garantierte relationale Verknüpfung zwischen Klient, Session, Fokus, Report und Harmonisierung
- laufende Sessions werden nicht als eigenständige Runtime-Objekte archiviert

## 8.4 Bewertung

Das Session-Archiv ist funktional vorhanden, aber semantisch fragmentiert. Es ist eher eine Sammlung von Hilfsdateien als ein konsistentes Archivsystem.

---

## 9. Klientenverwaltung

## 9.1 Aktueller Ist-Zustand

Vorhanden:

- Pydantic-Klientenmodelle in `app/schemas/klienten.py`
- Klientendaten in Requests
- Klientendaten in Templates
- Klientenbezug in Reports

Nicht vorhanden bzw. nicht verifiziert:

- echte Klientendatenbank
- CRUD-Schicht für Klienten
- dedizierte Client-ID-Lebenszyklen mit Persistenzbackend
- eindeutige Historisierung pro Klient

## 9.2 Fachlicher Befund

Der Begriff „Klientenverwaltung“ ist derzeit eher schema- und reportseitig vorhanden als systemisch. Das Projekt kennt Klientendaten, aber verwaltet Klienten nicht als robuste zentrale Entität.

## 9.3 Risiko

Ohne zentrale Klientenverwaltung drohen:

- redundante Dateneingaben
- inkonsistente Schreibweisen
- fehlende Langzeitzuordnung von Analysen
- erschwerte Archiv- und Verlaufsanalyse

---

## 10. Zentrale Harmonisierungssektion mit parallelen Sessions

## 10.1 Aktueller Ist-Zustand

Reale Harmonisierungsfunktionen existieren in `dev_cli.py`:

- Harmonizer-Start via `--harmonize`
- Auswahl der zu übertragenden Ergebnisse
- UI via Tkinter
- Zeitsteuerung über Pulse-/Pause-Abschnitte
- Audio-Wiedergabe via `winsound`
- WAV-Gesamtexport
- Einbindung von EMF-Counter-Frequencies und Amplifier-Audiofrequenzen

## 10.2 Parallelität

Verifiziert:

- EMF-Monitoring kann in eigenem Hintergrundthread laufen
- Harmonizer nutzt UI-/Audio-/State-Objekte
- API kann WebSocket-Verbindungen parallel bedienen

Nicht verifiziert als robuste zentrale Parallelverwaltung:

- mehrere gleichzeitige Harmonizer-Sessions mit zentralem Scheduler
- Session-Kollisionserkennung
- globale Übersicht über parallele Übertragungen
- saubere Thread-/Worker-/Task-Orchestrierung über mehrere Sessions

## 10.3 Bewertung

Es gibt Parallelität, aber keine zentrale Parallel-Sitzungsverwaltung.

Die aktuelle Situation ist:

- Parallelfähigkeit: partiell vorhanden
- zentrale Parallelkontrolle: nicht vorhanden
- Mehrsitzungsbetrieb: architektonisch angedeutet, aber nicht als beherrschte Kernfunktion umgesetzt

## 10.4 Risiko

Ohne zentrale Runtime-Verwaltung könnten bei späterer Mehrfachnutzung auftreten:

- Audio-/UI-Konflikte
- unklare Besitzverhältnisse von Ressourcen
- fehlende Laufzeittransparenz
- schwer reproduzierbare Zustandsfehler

---

## 11. PDF-Berichte-Sektion

## 11.1 Aktueller Ist-Zustand

Verifiziert:

- PDF-Export in `dev_cli.py`
- kombinierter PDF-Export in `dev_cli.py`
- PDF-Exportpfad auch in API vorhanden
- ReportLab wird genutzt
- Formatierung enthält Klient, Fokus, Matrix, Score, Intensität, Palette, Konfiguration und optional Bio-Info

## 11.2 Stärken

- echte Reportinglogik vorhanden
- PDF ist kein Blindstub
- Konfigurationsdaten werden mitgeführt
- kombinierte Berichte sind vorgesehen

## 11.3 Schwächen

- starke Paketabhängigkeit von `reportlab`
- in der API wird bei fehlendem Paket explizit `HTTP 501` ausgelöst
- keine zentrale Report-Registry
- kein sauberer Report-Index über alle Sessions

## 11.4 Bewertung

Die PDF-Berichtsfunktion ist eine der realsten produktionsnahen Teilfunktionen, aber sie hängt stark an einer fragilen Dependency-Kette und einer noch unharmonisierten Archivstruktur.

---

## 12. Verifizierte Dependency- und Startprobleme

## 12.1 Reproduzierte Fehler

Direkt reproduziert:

- `python -c "import torch"`
  - Fehler: `ModuleNotFoundError: No module named 'torch'`

- Modulimporttest:
  - `app.algorithms.resonance_engine` -> `ModuleNotFoundError: No module named 'torch'`
  - `app.api.resonance` -> `ModuleNotFoundError: No module named 'torch'`
  - `main` -> `ModuleNotFoundError: No module named 'torch'`
  - `dev_cli` -> `ModuleNotFoundError: No module named 'numpy'`

- `python -m pytest tests -q`
  - Exit-Code `2`
  - 4 Sammelfehler bereits in der Test-Collection

## 12.2 Exakte Testfehler

Verifiziert aus `.hermes_pytest_out.txt`:

1. `tests/test_api_vector_modes.py`
   - scheitert, weil `main.py` -> `app/api/resonance.py` -> `app/algorithms/resonance_engine.py` -> `import torch`

2. `tests/test_audio_checksum.py`
   - scheitert direkt an `import numpy as np`

3. `tests/test_engine_regressions.py`
   - scheitert direkt an `import torch`

4. `tests/test_engine_smoke.py`
   - scheitert direkt an Engine-Import wegen `torch`

Zusätzlich sichtbar:

- Pydantic-Deprecation-Warnungen in `app/schemas/klienten.py` und `app/schemas/resonance.py`

## 12.3 Root-Cause-Kette

Die zentrale Fehlerkette lautet:

1. Kernmodule importieren harte numerische Pakete am Modulanfang
2. `torch` fehlt
3. dadurch importiert die Engine nicht
4. dadurch importieren API und `main.py` nicht
5. dadurch scheitern API-Tests bereits beim Sammeln
6. parallel fehlt `numpy`, wodurch selbst `dev_cli.py` und Audio-Tests scheitern

## 12.4 Kritischer Architekturpunkt

Obwohl `dev_cli.py` einen Fallback-/Mock-Gedanken enthält, ist die Startkette nicht robust genug gegen fehlende Kernpakete.

Wesentliche Ursache:

- `dev_cli.py` importiert selbst `numpy` am Dateianfang
- die Engine importiert `torch` am Dateianfang
- dadurch kann der Prozess kippen, bevor spätere degradierte Pfade sinnvoll greifen

Das ist aktuell einer der wichtigsten Stabilitätsmängel des gesamten Projekts.

---

## 13. Workflow-Akkuranz und Stabilität

## 13.1 Stärken

1. Der fachliche Workflow ist tief ausgearbeitet.
2. Die Engine koppelt Signatur, Fokus, EMF, Amplifier, Palette und Export schlüssig.
3. Die API ist breit und unterstützt mehrere Analysearten.
4. Der Harmonizer ist real implementiert.
5. Die Testabsicht ist vorhanden und deckt sinnvolle Punkte ab:
   - Smoke
   - Reproduzierbarkeit
   - API-Vektormodi
   - Audioheader

## 13.2 Schwächen

1. Harte Top-Level-Imports blockieren degradierte Laufmodi.
2. Windows-PS1-, CLI- und API-Logik überlappen sich stark.
3. Zentrale Verwaltungsdomänen fehlen als saubere Kernobjekte.
4. Realtime- und Multi-Session-Aspekte sind nur teilweise verwaltet.
5. Dokumentierte Zielarchitektur und realer Laufzustand driften auseinander.
6. D-Wave-/Quantum-Aspekte sind eher konzeptionell als betriebssicher.

## 13.3 Stabilitätsklassifikation nach Bereich

| Bereich | Status | Bewertung |
|---|---|---|
| API-Boot | blockiert | wegen `torch`-Importkette derzeit nicht startfähig |
| CLI-Boot | blockiert/fragil | `dev_cli.py` scheitert bereits an fehlendem `numpy` |
| Engine-Kern | fachlich stark, runtime-blockiert | Logik breit, aber aktuell nicht lauffähig ohne Kernpakete |
| EMF-Subsystem | funktional interessant | softwareseitig gut angelegt, reale Sensorik aber optional/unvollständig |
| Harmonizer | funktional vorhanden | stark windows-/GUI-orientiert, nicht zentral multi-session-fähig |
| Exporte | gut, aber abhängigkeitskritisch | PDF/XLSX real vorhanden, aber paketgebunden |
| Sessionverwaltung | funktional, fragmentiert | kein einheitliches Archivmodell |
| Klientenverwaltung | schwach | Schemata vorhanden, Verwaltung als System fehlt |
| Testbarkeit | aktuell blockiert | Collection scheitert an Basispaketen |

---

## 14. Kritische Erkenntnisse mit Besprechungsbedarf

Die folgenden Punkte sollten vor späteren kritischen Änderungen mit dir besprochen werden:

### K1 – Die aktuelle Runtime ist nicht bootstrap-robust
`torch` und `numpy` fehlen im aktiven Environment; dadurch scheitern API, Engine, CLI und Tests schon vor dem eigentlichen Fachablauf.

### K2 – Mock-/Fallback-Pfade sind architektonisch nicht früh genug entkoppelt
Der Code enthält degradierte Ideen, aber die Importarchitektur verhindert, dass diese Pfade sauber tragen.

### K3 – Die zentrale Verwaltungsdomäne ist fachlich vorhanden, technisch aber verstreut
Analyse, Session, Klient, Harmonisierung und Reporting leben derzeit in getrennten Dateien, States und Verzeichnissen statt in einem konsistenten Kernmodell.

### K4 – Die Echtzeithardwareanbindung ist überwiegend indirekt
EMF-Realtime existiert softwareseitig, aber echte externe Sensorketten sind optional, pluginbasiert oder nur vorbereitet.

### K5 – Parallelbetrieb ist angedeutet, aber nicht zentral beherrscht
Threads und WebSockets existieren, doch eine zentrale Mehrsitzungssteuerung fehlt.

### K6 – Die Projektdokumentation wirkt weiter als die nachweisbar lauffähige Runtime
Die Hardware- und Architektur-Dokumentation beschreibt ein starkes Zielbild; die aktuelle Umgebung erfüllt dieses Bild zurzeit nicht.

---

## 15. Präzise Schlussbewertung

`Radi144` ist kein frühes Rohprojekt, sondern ein umfangreiches, fachlich vielschichtiges System mit echter Engine-, API-, Harmonizer-, Export- und EMF-Struktur.

Die Hauptprobleme liegen aktuell nicht zuerst in der fachlichen Modellierung, sondern in:

- Runtime-Bootstrap
- Dependency-Management
- zentraler Verwaltungsarchitektur
- konsistenter Mehrsitzungssteuerung
- Entkopplung von GUI-/CLI-/API-Zuständen

Der sequentielle Ablauf ist grundsätzlich klar und aus dem Code rekonstruierbar.
Insbesondere `generate_matrix.ps1` zeigt den operativen Benutzerworkflow sehr deutlich.
Die Engine selbst zeigt ebenfalls einen klaren Analysepfad mit nachvollziehbaren Steps und Substeps.

Die größte unmittelbare technische Wahrheit lautet:

Ohne Behebung der Paket- und Bootstrap-Probleme ist die reale Betriebsstabilität derzeit eingeschränkt, unabhängig davon, wie weit die fachliche Architektur bereits ist.

---

## 16. Ablage dieser Analyse

Diese Analyse wurde erstellt unter:

`C:\Users\Hubert111\Documents\Radi144\docs\RADI144_TIEFENANALYSE_2026-06-03.md`

---

## 17. Verifizierter Nachtrag nach der Runtime-Stabilisierung

Nach Erstellung der ursprünglichen Analyse wurde die Runtime gezielt auf Option A gehärtet und real verifiziert.

### 17.1 Umgesetzte technische Maßnahmen

1. Zentrales Bootstrap-/Preflight-Modul ergänzt
   - `app/bootstrap.py`
2. Harte Runtime-Prüfung in zentrale Einstiegspfade integriert
   - `main.py`
   - `dev_cli.py`
   - `app/algorithms/resonance_engine.py`
3. Windows-Start- und Installationsskripte auf lokale Projekt-Runtime umgestellt
   - `install_dependencies.bat`
   - `run.bat`
   - `run_test.bat`
4. Lokale isolierte Projektumgebung eingeführt
   - `.venv`
5. HTTP-Test-Stack harmonisiert
   - `requirements.txt` enthält jetzt zusätzlich `httpx<0.28`
6. Regressionstests ergänzt
   - `tests/test_runtime_dependencies.py`
   - `tests/test_api_testclient_compat.py`

### 17.2 Reale Verifikationsergebnisse

Verifiziert wurden:

- Modulimporte:
  - `main`: OK
  - `dev_cli`: OK
  - `app.algorithms.resonance_engine`: OK
- API-TestClient-Kompatibilität: OK
- API-Vektorpfade: OK
- komplette Testsuite in lokaler `.venv`: `16 passed`
- Batch-Smoketest über `run_test.bat`: erfolgreich

### 17.3 Real erzeugte Artefakte aus dem verifizierten CLI-Lauf

Im verifizierten Batch-Lauf wurden real erzeugt:

- `C:\Users\Hubert111\Documents\Radi144\Analysen\20260603_214813_Max_Mustermann\Max_Mustermann_20260603_214813.pdf`
- `C:\Users\Hubert111\Documents\Radi144\Analysen\20260603_214813_Max_Mustermann\Max_Mustermann_20260603_214813.xlsx`
- `C:\Users\Hubert111\Documents\Radi144\Analysen\20260603_214813_Max_Mustermann\Max_Mustermann_20260603_214813_KOMPLETT.pdf`

### 17.4 Neue Architekturwahrheit nach Option A

Die harte Importkopplung der Kernengine an `torch` und der CLI an den numerischen Stack bleibt bestehen, ist jetzt aber bewusst abgesichert statt zufällig fragil.

Das bedeutet:

- kein degradiertes Starten mehr als Sollverhalten
- vollständige Pflicht-Runtime als Betriebsgrundlage
- lokale `.venv` als bevorzugter und reproduzierbarer Projektkontext
- klare Fehlermeldung statt impliziter Modulabbrüche

### 17.5 Verbleibende, nicht blockierende Restpunkte

Weiterhin sichtbar, aber nicht blockierend:

1. Pydantic-v2-Deprecation-Warnungen in
   - `app/schemas/klienten.py`
   - `app/schemas/resonance.py`
   - `app/api/resonance.py`
2. TestClient-/httpx-Integration ist nun stabil, verwendet aber noch einen deprecated App-Shortcut im Upstream-Stack
3. Die größeren Architekturthemen bleiben offen:
   - zentrale Verwaltungsdomäne
   - Session-/Klientenmodell
   - Harmonizer-/Parallel-Session-Steuerung
   - klare Trennung von Zielsystem-Doku und realer Hardwarewahrheit

## 18. Empfohlene nächste Besprechungspunkte

Nach der nun erledigten Dependency-/Bootstrap-Stabilisierung ist die sinnvolle nächste Priorisierung:

1. Soll die Installations- und Betriebsdoku weiter vereinheitlicht werden?
2. Soll die zentrale Verwaltungsarchitektur konzeptionell in eigene Domänen zerlegt werden?
3. Soll zuerst die Session-/Klienten-/Report-Struktur vereinheitlicht werden?
4. Soll die Harmonizer-Parallelität als eigener Architekturblock neu gefasst werden?
5. Soll die reale Hardware-/Realtime-Wahrheit von der Zielsystem-Doku klar getrennt werden?
