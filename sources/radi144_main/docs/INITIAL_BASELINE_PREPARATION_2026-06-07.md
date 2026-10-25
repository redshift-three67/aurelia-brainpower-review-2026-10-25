# Radi144 Initial-Baseline-Vorbereitung

Stand: 2026-06-07
Projektwurzel: `/home/klaus999/projects/Radi144`

## 1. Zweck

Dieses Dokument ist die operative Vorbereitung fuer eine spaetere kuratierte Initial-Baseline. Es ist kein Commit, keine Staging-Aktion und keine Produktivcode-Aenderung.

Wichtig: Es wurde weiterhin kein `git add .` ausgefuehrt. Staging/Commit bleibt freigabepflichtig.

## 2. Sicherheitsgrenze

Nicht veraendert:

- Kernengine
- Resonanzscore
- Matrixlogik
- DB-Ranking-Algorithmus
- Top-30/Top-50-Scanlogik
- EMF-/Audio-/Harmonizer-Algorithmen
- Runtime-JSON-Daten
- `deploy/server.env` Werte
- `db_import/` Inhalte

Vor dieser Phase wurde eine externe ShadowCopy erstellt:

- `/home/klaus999/ShadowCopies/Radi144_20260607_005455_before_initial_baseline_preparation`

## 3. Aktueller Git-Ausgangszustand

Verifiziert am 2026-06-07:

- Branch: `main`
- Getrackte Dateien: keine bekannte Initial-Baseline vorhanden (`git log` zeigt keinen Commit)
- `git status --short`: 38 top-level untracked Kandidaten nach Ausschluss von `generate_analysis_pdf.py`.
- `git status --porcelain=v1 --untracked-files=all`: 154 untracked Einzeldateien nach weiterer Dokumentations-Ergaenzung.
- `git status --ignored --porcelain=v1`: 59 ignorierte Pfade/Artefakte.

## 4. Neue Entscheidung in dieser Phase

`generate_analysis_pdf.py` wurde statisch geprueft und aus der initialen Baseline ausgeschlossen.

Befund:

- harter historischer Windows-Ausgabepfad: `c:\Users\Hubert111\CascadeProjects\12x12\Tiefenanalyse_Codegeau.pdf`
- historische Versions-/Akkuranzclaims im Dokumenttext
- kein aktueller SSOT fuer Radi144 als Standalone- und Referenzmodul
- keine Notwendigkeit fuer aktuelle Tests, API, CLI, DB-Ranking oder Workflow-UI

Entscheidung:

- in `.gitignore` aufgenommen
- in `tests/test_repository_data_hygiene.py` als Guard abgesichert
- spaeterer PDF-Export nur als neue parametrisierte Funktion/Dokumentationspipeline nach separater Freigabe

## 5. Empfohlene Baseline-Gruppen

### Gruppe A: Kontroll-/Hygiene-Basis

Empfehlung: zuerst aufnehmen, sobald Staging/Commit freigegeben wird.

Pfade:

- `.gitignore`
- `pytest.ini`
- `tests/test_repository_data_hygiene.py`

Begruendung:

- schuetzt Runtime-, Secret-, Restore-, Debug- und stale Generator-Artefakte
- verhindert versehentliche Aufnahme lokaler/sensibler Daten
- ist Grundlage fuer alle weiteren Commit-Gruppen

### Gruppe B: Produktiver Standalone-Kern plus Tests

Pfade:

- `app/`
- `dev_cli.py`
- `main.py`
- `tests/` ohne rein lokale Caches

Begruendung:

- aktuelle API-/Service-/Schema-/Algorithmus-Schicht
- Tests decken Engine-Smoke, API, Runtime-Abhaengigkeiten, Archive/Manifest/Client-Registry und UI-Harmonizer ab
- Kernengine bleibt unveraendert; diese Gruppe konserviert den aktuellen Stand

### Gruppe C: Browser-/Workflow-Oberflaeche

Pfade:

- `user_workflow.html`
- `user_workflow.css`
- `user_workflow.js`
- `workflow_stepping.html`
- `workflow_stepping.css`
- `workflow_stepping.js`

Begruendung:

- lokale Standalone-Bedienoberflaeche und Workflow-Stepping
- relevant fuer Radi144 als nutzbares eigenstaendiges Modul

### Gruppe D: Dokumentation

Pfade:

- `docs/`
- ausgewaehlte Root-Markdown-Dokumente, nach finaler Sichtung:
  - `README.md`
  - `SCHNELLSTART-ANLEITUNG.md`
  - `USER_GUIDE_DE.md`
  - `DEVELOPER_MASTER_GUIDE.md`
  - `BIO_RESONANCE_DOCS.md`
  - `FULL_DOCUMENTATION.md`
  - `TIEFENANALYSE_CODEGEAU.md`
  - `TIEFENANALYSE_CODEGEAU_MASTER.md`
  - `WIEDERHERSTELLUNG_2025-02-14.md`

Zurueckstellen/gesondert entscheiden:

- `COMPLETE_SYSTEM_DESCRIPTION.md` wegen moeglich historischer/stale Claims
- `TIEFENANALYSE_CODEGEAU.md.new` wegen unklarer Dubletten-/Zwischenstand-Rolle

### Gruppe E: Produktive Konfiguration und Referenzdaten

Pfade:

- `data/amplifiers.json`
- `data/amplifier_images/.gitkeep`
- `palettes.json`
- `preset_profiles.json`
- `bio_knowledge.json`
- `HA und DE v2.json`
- `Ha und De v1.json`
- `db_import/`

Begruendung:

- produktive Konfigurations-/Referenzdaten fuer Standalone- und Referenzmodulbetrieb
- `db_import/` ist produktiv durch API, PowerShell und Workflow referenziert
- Duplikate in `db_import/` bleiben bewusst erhalten, weil Dateinamen aktuell Teil des Resonanz-/Vorfilter-Signals sein koennen

Einschraenkung:

- vor externer Veroeffentlichung/Remote-Push Herkunft/Lizenz und auffaellige Dateinamen separat freigeben

### Gruppe F: Deployment-/Windows-Betrieb

Pfade:

- `deploy/server.env.example`
- `deploy/resonance-engine.service`
- `deploy/setup_server.sh`
- `generate_matrix.ps1`
- `install_dependencies.bat`
- `run.bat`
- `run_test.bat`
- `setup_new_pc.bat`
- `requirements.txt`

Begruendung:

- notwendige Betriebs-/Setup-Artefakte ohne echte lokale Secrets
- `deploy/server.env` bleibt ignoriert und darf nicht aufgenommen werden
- `generate_matrix.ps1` bleibt aktiver Windows-/PowerShell-Matrixworkflow, aber spaetere Phase-4-Anpassungen nur adapterartig und nach Freigabe

## 6. Explizit nicht aufnehmen

Nicht in die Initial-Baseline:

- `deploy/server.env`
- `data/runtime/`
- `data/session_templates.json`
- `data/.focus_temp.txt`
- `last_session.json`
- `focus_history.txt`
- `Analysen/`
- `RestorePoints/`
- `restore_points/`
- `.hermes*.txt`
- Root-Debug-/Fix-/Verify-Skripte laut `.gitignore`
- `create_restore_point.py`
- `create_restore.ps1`
- `finalize_project.py`
- `generate_analysis_pdf.py`

## 7. Naechste operative Entscheidung

Naechster stabiler Schritt nach erfolgreicher Testverifikation:

1. Nutzerfreigabe einholen: ob Staging/Commit der Gruppe A erfolgen soll.
2. Wenn freigegeben: gezielt nur Gruppe A stagen, `git diff --cached` pruefen, Commit erstellen.
3. Danach Gruppe B separat vorbereiten und verifizieren.
4. Kein `git add .`, kein Remote-Push, keine Kernengine-Aenderung ohne separate Freigabe.
