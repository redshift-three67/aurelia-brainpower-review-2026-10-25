# Phase 2 - Workflows, Steps Und Substeps

## Kurzfazit

Das Projekt besitzt aktuell drei unterschiedliche Workflow-Realitaeten.
Sie sind teilweise verwandt, aber nicht identisch.
Jede tiefere Weiterentwicklung muss deshalb zuerst entscheiden, welcher dieser drei Pfade der kanonische Produktpfad sein soll.

## Die drei Workflow-Modelle

| Modell | Einstieg | Technischer Kern | Aktueller Status |
| --- | --- | --- | --- |
| Produktiver Top-N-Scan | `scan top3-scan` | `apps/cli/commands/scan.py` + `field multiplex-scan` | faktisch produktiv |
| 12-Step Workflow | `field workflow-scan` oder `/api/analyze` | `apps/cli/workflow/*` | separater Orchestrator, nicht produktionsgleich |
| 8-Step Web-Wizard | `/` | `apps/web/static/*` + `apps/web/main.py` | aktuelle Operator-UI |

## A. Produktiver Top-N-Scan

### Einstieg

- PowerShell-Launcher: `Run-MultiplexScan.ps1`
- Web-Launcher: `apps/web/launcher.py`
- CLI: `python -m apps.cli.main scan top3-scan ...`

### Technische Kernidee

Der Name `top3-scan` ist historisch irrefuehrend.
Tatsaechlich baut der Pfad einen konfigurierbaren Top-N-Auto-Scan fuer `3/5/7/9` Profile.

### Ablauf in sachlicher Reihenfolge

1. Environment- und Source-Preflight
   - `Run-MultiplexScan.ps1:17-42`
2. Erfassung von Klientendaten, Analyse-Level und optionalem Fokus
   - `Run-MultiplexScan.ps1:137-260`
3. Web oder PowerShell bauen dasselbe CLI-Kommando
   - `apps/web/launcher.py:21-94`
4. `scan.py` fuehrt Phase-1-Screening ueber Hauptprofile aus
5. Fokusgewichtung beeinflusst Priorisierung
6. Top-N Profile werden ermittelt
7. Fuer jedes Top-Profil wird ein tieferer Produktionsscan gestartet
   - via `field multiplex-scan`
8. Exportartefakte werden in historisierter Archivstruktur geschrieben
9. Nachgelagerte Tools bauen Synergy-, Remedy-, Deutungs- und Trendberichte

### Wichtigste technische Beobachtungen

- Der Web-Launcher uebergibt denselben produktiven CLI-Pfad wie der PowerShell-Launcher.
  - `apps/web/launcher.py:79-94`
- Der Launcher setzt feste Defaults wie:
  - Export `C:\Benutzer_Archive_Start`
  - Hardware-Profil `windows`
  - `--synergy`
  - `--k-total 2048`
  - `--top-k 192`
- Fokus und `main_symptom` werden in einem einzigen `--focus` zusammengefuehrt.
  - `apps/web/launcher.py:59-70`

## B. 12-Step-Workflow

### Einstieg

- `apps/cli/workflow/orchestrator.py:28-107`
- Webseitig zusaetzlich: `apps/web/analyze.py:16-73`

### Step-Liste

| Step | Datei | Zweck | Hauptoutputs |
| --- | --- | --- | --- |
| 1 | `step01_init.py` | Hardware-/Entropy-Init | `hardware_report`, `h_level` |
| 2 | `step02_input.py` | Eingabepruefung | `errors` |
| 3 | `step03_signature.py` | Klienten-Signatur | `client_rates`, `client_frequency` |
| 4 | `step04_focus.py` | Fokus-Vektor | `focus_vector`, `focus_multiplier` |
| 5 | `step05_emf.py` | EMF-Kompensation | `composite_emf_index`, `counter_frequencies` |
| 6 | `step06_amplifier.py` | Amplifier-Match | `amplifier_recommendations` |
| 7 | `step07_palette.py` | Farbpalette | `palette`, `palette_strategy` |
| 8 | `step08_matrix.py` | Kandidaten-/Matrix-Suche | `matrix_results`, `candidate_count` |
| 9 | `step09_quantum.py` | Quantum-Synergy | `quantum_synergies` |
| 10 | `step10_post.py` | Post-Processing | `level_info`, finalisierte Matrixdaten |
| 11 | `step11_export.py` | Export | `export_paths` |
| 12 | `step12_harmonize.py` | Harmonisierung | `harmonization_active`, `harmonization_job_id` |

### Zustandsmodell

Der 12-Step-Pfad verwendet einen expliziten `WorkflowState` als Transportobjekt.

- `apps/cli/workflow/state.py:14-97`

Das ist strukturell klarer als der produktive Top-N-Pfad, aber fachlich nicht identisch mit ihm.

### Konkrete Inkonsistenzen des 12-Step-Pfads

1. Er ist nicht der Web-Hauptpfad.
   - Der Web-Hauptpfad startet `top3-scan`, nicht `run_workflow()`.
2. Export-Shape und Folgetools sind nicht identisch zum produktiven Archivpfad.
3. Die Harmonisierung in Step 12 hat einen Typbruch.
   - `step12_harmonize.py:41-53` behandelt den Rueckgabewert wie ein Job-Objekt.
   - `services/harmonization_worker.py:489-539` gibt aber nur `job_id: str` zurueck.
   - Folge: `harmonization_job_id` faellt effektiv auf `unknown` zurueck.

## C. 8-Step Web-Wizard

### Sichtbarer Ablauf

Der aktuelle Web-Wizard besteht aus acht Operator-Schritten:

1. Preflight
2. Hinweise
3. Klientenaufnahme
4. Fokus
5. Scan-Profil
6. Analysefreigabe
7. Berichte
8. Harmonisierung

Evidenz:

- `apps/web/static/index.html:22-31`
- `apps/web/static/app.js:4-13`

### Funktionaler Ablauf

1. Preflight: `GET /api/health`, `GET /api/sources`
2. Consent: Checkbox-basierte Freigaben
3. Erfassung von Name, Geburtsdatum, Geburtsort
4. Auswahl von Fokus, Level und Top-N
5. Auswahl von Profiltemplate, Entropiemodus, Bildpfad, Adaptive Limits
6. Vorschau und Start des produktiven CLI-Kommandos
7. Anzeige eines historisierten Berichtskatalogs
8. Start/Stopp/Refresh eines Harmonisierungsjobs

## Substeps und Fortschrittslogik

### Wichtiger Punkt

Die Web-Substeps sind keine echten Workflow-Domaenenobjekte.
Sie werden aus Prozessausgabe geparst.

### Mechanismus

- Job-Start: `apps/web/scan_jobs.py:225-263`
- Snapshot/Polling: `apps/web/scan_jobs.py:270-322`
- Parser fuer Phase/Substep-Labels: `apps/web/scan_jobs.py:29-151`

Die Erkennung basiert auf String-Markern wie:

- `screening aller haupt-profile`
- `top-profile`
- `phase 2`
- `export`
- `harmonisierung`
- `trendbericht`
- `remedy`
- `synergy`

### Folge

Der sichtbare Fortschritt der Web-Oberflaeche ist fragil gegen:

- Textaenderungen in CLI-Ausgabe
- Uebersetzungen
- Schreibfehler oder Encoding-Unterschiede
- neue Zwischenschritte ohne Parser-Anpassung

## Report- und Sessionfluss

### Scan-Ergebnisse

`apps/web/main.py:413-553` versucht Top-Profile und Top-Resonanzen aus erzeugten Scan-JSONs zu rekonstruieren.

Dabei werden:

- Name, Vorname, Geburtsdatum, Geburtsort aus CLI-Argumenten rekonstruiert
- daraus Client-Slugs gebaut
- Session-Ordner gesucht
- `*_multiplex_scan.json` gelesen

### Relevante Konsequenzen

1. Der Ergebnispfad ist stark an Dateinamen- und Archivkonventionen gekoppelt.
2. Report- und Resultatdarstellung basiert nicht auf einer stabilen DB oder API-Projection, sondern auf Dateiablage.
3. Session-Isolation ist teilweise vorhanden, aber nicht eigentuemergebunden.

## Historisierte Session-Scope-Logik

Positives Signal:

- `tests/test_topn_session_scope.py:13-48` zeigt, dass zumindest ein client-lokaler Session-Filter gegen historische JSONs getestet wird.

Einschraenkung:

- Das gesamte System ist weiterhin timestamp- und pfadkonventionslastig.
- Eine belastbare Mandanten- oder Benutzerbindung entsteht daraus nicht.

## Die wichtigste Workflow-Divergenz

### Produktiver Fakt

Die aktuelle Web-App verkauft nach aussen einen "Phase-1 Klienten-Workflow", startet technisch aber den produktiven Top-N-CLI-Pfad.

### Nicht dasselbe

- `/api/analyze` startet den 12-Step-Orchestrator synchron.
- `/api/scan/jobs` startet den produktiven Top-N-CLI-Workflow asynchron.
- `/workflow-stepping` dokumentiert einen 12-Step-Blueprint, der weder die 8-Step-UI noch den produktiven CLI-Pfad 1:1 abbildet.

## Entwicklerische Hauptfolgerung

Vor jeder groesseren Weiterentwicklung muss zuerst eine kanonische Antwort auf drei Fragen festgelegt werden:

1. Welcher Workflow ist produktiv verbindlich?
2. Welche Fortschritts-/Statussprache ist die einzige Wahrheit?
3. Aus welcher Quelle werden Ergebnisse gelesen: Events, DB, Runtime-Manifest oder Dateisystem?

Ohne diese Konsolidierung bleibt jede weitere UI-, Security- oder Compliance-Arbeit nur teilweise stabil.

## Ergaenzender Referenzhinweis

Fuer die Frage, wie ein professionellerer Operator-Workflow aussehen koennte, siehe auch:

- `PHASE_6_RADI144_TRANSFER_WORKFLOW_UIUX.md`

Dort ist `Radi144` gezielt als Workflow- und UX-Referenz fuer Morphic V1 ausgewertet.
