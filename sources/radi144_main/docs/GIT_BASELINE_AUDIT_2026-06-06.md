# Radi144 Git-Baseline-Audit

Stand: 2026-06-06
Projektwurzel: `/home/klaus999/projects/Radi144`

Projektzielbild: Radi144 ist sowohl eigenstaendig lauffaehiges Standalone-System als auch Referenz-/Informationsmodul fuer das uebergeordnete Radionik-Wellbeing-/Radiquant-Projekt. Siehe `docs/RADI144_PROJECT_INTENT_2026-06-06.md`.

## 1. Zweck dieses Dokuments

Dieses Dokument ist die kuratierte Entscheidungsgrundlage fuer eine spaetere Initial-/Baseline-Aufnahme in Git.

Es ist bewusst **kein Commit** und **keine Produktivcode-Aenderung**. Es dokumentiert, welche Dateigruppen in eine stabile Baseline gehoeren, welche vorerst ausgeschlossen bleiben muessen und welche vor einer Aufnahme noch manuell geprueft werden sollten.

Wichtig: Kernengine, Kernalgorithmen, Resonanz-Scoring, EMF-Kompensation, Top-3-/Top-10-Selektion, Matrixberechnung und Audio-Harmonizer-Timing wurden in dieser Audit-Phase nicht veraendert.

## 2. Verifizierter Git-Ausgangszustand

Werkzeugausgabe waehrend dieser Phase:

- `git ls-files | wc -l` -> `0`
- `git status --porcelain | wc -l` -> `64`

Bewertung:

- Das Repository besitzt aktuell noch keine getrackte Git-Baseline.
- Ein breites `git add .` waere riskant, weil die Projektwurzel produktive Dateien, lokale Runtime-Daten, Wiederherstellungsarchive, Debug-Skripte und Dokumentationsartefakte gemischt enthaelt.
- Vor jedem Commit muss weiter kuratiert statt pauschal hinzugefuegt werden.

## 3. Verifizierte Groessen-/Kategorienuebersicht

Die folgenden Zahlen wurden aus dem aktuellen Dateisystem mit Ausschluss von `.git`, `.venv`, `build_env`, `__pycache__` und `.pytest_cache` erzeugt.

| Kategorie | Dateien | Bytes | Baseline-Empfehlung |
|---|---:|---:|---|
| `productive_python_package` | 21 | 202083 | aufnehmen |
| `tests` | 16 | 31952 | aufnehmen |
| `project_control_files` | 2 | 592 | aufnehmen |
| `browser_workflow_static` | 6 | 184460 | aufnehmen |
| `windows_powershell_entrypoints` | 6 | 54777 | aufnehmen, weil PowerShell-Workflow Teil des Zielsystems ist |
| `deploy` | 3 | 5263 | pruefen, dann aufnehmen oder neutralisieren |
| `docs` | 15 | 161198 | aufnehmen, aber Session-/Handoff-Dokumente bewusst als Dokumentation klassifizieren |
| `product_config_or_reference_json` | 7 | 16224 | aufnehmen nach Inhaltscheck |
| `reference_database_import` | 59 | 3857602 | aufnehmen nur nach Duplikat-/Lizenz-/Sensibilitaetscheck |
| `root_entry_or_utility_python` | 2 | 85226 | aufnehmen (`dev_cli.py`, `main.py`) |
| `root_utility_debug_scripts` | 26 | 51228 | nicht pauschal aufnehmen; Legacy-/Generator-Sonderfaelle ignorieren |
| `root_docs_or_text` | 25 | 107423 | selektiv aufnehmen; Hermes-Testlogs ignorieren/loeschen |
| `ignored_sensitive_runtime` | 17 | 889720 | nicht aufnehmen |
| `ignored_restore_archive` | 132 | 4010182 | nicht aufnehmen |
| `other` | 1 | 5445 | pruefen |

## 4. Pygount-Codebasis-Summary

Pygount wurde mit Skip-Folders fuer `.git`, `.venv`, `build_env`, `__pycache__`, `.pytest_cache`, `RestorePoints`, `restore_points` und `Analysen` ausgefuehrt.

Auszug:

| Sprache | Dateien | Code | Kommentar |
|---|---:|---:|---:|
| JSON | 11 | 18211 | 0 |
| Python | 60 | 5780 | 1060 |
| JavaScript+Genshi Text | 2 | 1843 | 76 |
| HTML | 2 | 763 | 27 |
| PowerShell | 2 | 715 | 95 |
| CSS+Lasso | 2 | 521 | 64 |
| Batchfile | 4 | 123 | 17 |
| Bash | 1 | 55 | 15 |
| Systemd | 1 | 24 | 3 |
| INI | 1 | 4 | 0 |
| Text only | 55 | 0 | 81627 |
| Markdown | 24 | 0 | 2404 |
| Sum | 180 | 28039 | 85388 |

Bewertung:

- Die produktive Codebasis ist ueberschaubar, aber von grossen Text-/Referenzdatenbloecken begleitet.
- JSON und Textdaten dominieren die Zeilenzahl; deshalb ist eine inhaltliche Baseline-Kuratierung zwingend.

## 5. Dateien/Gruppen, die in die erste kuratierte Baseline gehoeren

### 5.1 Produktiver Python-Code

Empfehlung: aufnehmen.

Pfade:

- `app/`
- `dev_cli.py`
- `main.py`

Begruendung:

- Enthalten aktive Kern-/API-/Service-/Schema-/Modellschicht.
- Phase 1-3 des Umsetzungsplans sind hier implementiert.
- Diese Dateien sind fuer Tests und spaetere Phase-4-Arbeit erforderlich.

Nicht veraendern ohne separate Freigabe:

- `app/algorithms/resonance_engine.py`
- `app/algorithms/emf_compensator.py`
- `app/algorithms/amplifier.py`
- `app/algorithms/client_signature.py`

### 5.2 Tests

Empfehlung: aufnehmen.

Pfade:

- `tests/`
- `pytest.ini`

Begruendung:

- Aktueller verifizierter Stand nach Baseline-Kuratierung: 41 Tests gruen.
- Datenhygiene ist jetzt ueber `tests/test_repository_data_hygiene.py` abgesichert.
- Tests sind die stabilste Grundlage fuer weitere Umsetzung.

### 5.3 Browser-/Workflow-Dateien

Empfehlung: aufnehmen.

Pfade:

- `user_workflow.html`
- `user_workflow.css`
- `user_workflow.js`
- `workflow_stepping.html`
- `workflow_stepping.css`
- `workflow_stepping.js`

Begruendung:

- Diese Dateien enthalten die lokale Workflow-/Stepping-/Harmonizer-Oberflaeche.
- Vorherige UI-Erweiterungen wurden genau hier bewusst lokal und ohne Backend-Persistenz umgesetzt.

### 5.4 PowerShell-/Windows-Entrypoints

Empfehlung: aufnehmen, aber spaeter separat testen.

Pfade:

- `generate_matrix.ps1`
- `install_dependencies.bat`
- `run.bat`
- `run_test.bat`
- `setup_new_pc.bat`

Begruendung:

- `generate_matrix.ps1` ist im Umsetzungsplan fuer Phase 4 relevant.
- Die Batch-Dateien gehoeren zum historischen Windows-Betriebsmodell. Das stale `create_restore.ps1` wurde nach Sonderfall-Audit explizit ausgeschlossen; aktuelle Backups erfolgen ueber externe ShadowCopies.

Risiko:

- Phase-4-Aenderungen duerfen `generate_matrix.ps1` nur adapterartig an gemeinsame Metadaten anbinden; keine Komplettmigration ohne Freigabe.

### 5.5 Produktive Konfiguration / Referenz-JSON

Empfehlung: nach Inhaltscheck aufnehmen.

Pfade:

- `data/amplifiers.json`
- `data/amplifier_images/.gitkeep`
- `palettes.json`
- `preset_profiles.json`
- `bio_knowledge.json`
- `HA und DE v2.json`
- `Ha und De v1.json`

Begruendung:

- Wirken wie produktive Fach-/Konfigurationsdaten und nicht wie lokale Runtime-Historie.

Offener Check:

- Vor Commit kurz auf personenbezogene Daten, Lizenz-/Herkunftsrisiken und Duplikate pruefen.

### 5.6 Dokumentation

Empfehlung: aufnehmen, aber Root-Dokumente ggf. spaeter unter `docs/` konsolidieren.

Wichtige Pfade:

- `README.md`
- `SCHNELLSTART-ANLEITUNG.md`
- `docs/RADI144_TIEFENANALYSE_2026-06-03.md`
- `docs/SESSION_CLIENT_REPORT_ARCHITEKTURPLAN_2026-06-03.md`
- `docs/SYSTEM_ARCHITECTURE_FLOW.md`
- `docs/HARDWARE_REQUIREMENTS.md`
- `docs/AMPLIFIER_KONZEPT.md`

Bewertung:

- Dokumente sind fuer Projektverstaendnis wichtig.
- Statusdokumente bleiben aber Claims und muessen gegen Code/Tests verifiziert werden.

## 6. Dateien/Gruppen, die nicht in die Baseline gehoeren

### 6.1 Sensible/lokale Runtime- und Sessiondaten

Nicht aufnehmen.

Pfade:

- `data/runtime/clients.json`
- `data/runtime/sessions.json`
- `data/runtime/artifacts.json`
- `data/session_templates.json`
- `data/.focus_temp.txt`
- `last_session.json`
- `focus_history.txt`
- `Analysen/`

Begruendung:

- Enthalten lokale Klienten-, Session-, Fokus- oder Reportdaten.
- DSGVO-/Datenschutzrisiko.
- Werden durch `.gitignore` geschuetzt und durch `tests/test_repository_data_hygiene.py` abgesichert.

### 6.2 Restore-/Snapshot-Artefakte

Nicht aufnehmen.

Pfade:

- `RestorePoints/`
- `restore_points/`

Begruendung:

- Enthalten historische Komplett- oder Teilkopien.
- Erhoehen Repository-Groesse und koennen veraltete oder sensible Daten enthalten.
- Backup-/ShadowCopy-Mechanismus liegt ausserhalb der Git-Baseline.

### 6.3 Hermes-/temporäre Testlogs

Nicht aufnehmen; spaeter loeschen oder dauerhaft ignorieren.

Beispiele:

- `.hermes_engine_regression_check.txt`
- `.hermes_phase3_full.txt`
- `.hermes_phase3_green1.txt`
- `.hermes_phase3_green2.txt`
- `.hermes_phase3_green_headers.txt`
- `.hermes_phase3_green_headers2.txt`
- `.hermes_phase3_red.txt`
- `.hermes_phase3_red_headers.txt`
- `.hermes_phase3_subset.txt`
- `.hermes_phase3_subset2.txt`
- `.hermes_pytest_ist_pruefung.txt`
- `.hermes_pytest_out.txt`

Begruendung:

- Lokale Ausfuehrungsartefakte, keine dauerhafte Projektquelle.

## 7. Gruppen mit manueller Vorentscheidung vor Commit

### 7.1 `db_import/`

Umgesetzter Audit-Stand 2026-06-06:

- Detailaudit erstellt: `docs/DATA_REFERENCE_AUDIT_2026-06-06.md`
- 59 Dateien, 3,857,602 Bytes, alle `.txt`
- 83,751 nicht-leere Textzeilen
- 45 Dateien UTF-8, 14 Dateien Latin-1 beim ersten erfolgreichen Dekodierungsversuch
- 0 JSON-Dateien, 0 leere Dateien, 0 Dekodierungsfehler
- Produktive Verbraucher bestaetigt: `app/api/resonance.py`, `generate_matrix.ps1`, `user_workflow.html`
- 9 exakte SHA256-Duplikatgruppen dokumentiert
- keine E-Mail- oder IBAN-Heuristiktreffer; telefonnummernaehnliche Treffer wurden als wahrscheinliche Frequenz-/Rate-/Codefolgen klassifiziert

Baseline-Entscheidung:

- `db_import/` bleibt Git-kandidatenfaehig und wird nicht ignoriert.
- Keine Inhalte wurden geaendert oder entfernt.
- Duplikate bleiben vorerst erhalten, weil Dateinamen selbst im aktuellen Ranking als Resonanz-/Vorfilter-Signal verwendet werden.
- Vor externer Veroeffentlichung/Remote-Push bleibt Herkunft/Lizenz separat freigabepflichtig.
- Auffaellige Dateinamen wie `Klaus_Test_Raten_V1.txt`, `HA_24_01_26_09_00.txt` und `Raphael_WS_Physis.txt` sind fuer eine externe/veroeffentlichte Baseline manuell zu bewerten.

### 7.2 Root-Debug-/Utility-Skripte

Umgesetzter Sicherungsstand 2026-06-06:

- Detailklassifizierung erstellt: `docs/ROOT_SCRIPT_BASELINE_AUDIT_2026-06-06.md`
- 22 offensichtliche Legacy-/Einmal-Diagnose- und Reparaturskripte in `.gitignore` aufgenommen.
- Aktive Root-Entrypoints bleiben Git-kandidatenfaehig.
- Schutz ist in `tests/test_repository_data_hygiene.py` abgedeckt.

Ignoriert / ausserhalb Initial-Baseline:

- `check_bom.py`, `check_bom_v2.py`, `check_output.py`, `check_palettes_bom.py`
- `debug_export.py`, `debug_gui.py`, `debug_imports.py`, `debug_test.py`
- `diag_check.py`, `fix_encoding.py`, `fix_encoding_bom.py`, `inspect_history.py`
- `reproduce_issue.py`
- `test_audio.py`, `test_date.py`, `test_engine.py`, `test_pdf.py`
- `verify_config.py`, `verify_execution.py`, `verify_fix.py`, `verify_fix_v2.py`, `verify_umlaut_flow.py`

Weiterhin Baseline-Kandidaten:

- `main.py`, `dev_cli.py`, `generate_matrix.ps1`
- `run.bat`, `run_test.bat`, `setup_new_pc.bat`, `install_dependencies.bat`
- `user_workflow.html`, `user_workflow.js`, `workflow_stepping.html`, `workflow_stepping.js`

Aus initialer Baseline ausgeschlossen nach Sonderfall-Audit:

- `create_restore_point.py`
- `create_restore.ps1`
- `finalize_project.py`
- `generate_analysis_pdf.py` nach Inhaltspruefung am 2026-06-07: stale harter Windows-Ausgabepfad `c:\\Users\\Hubert111\\CascadeProjects\\12x12\\Tiefenanalyse_Codegeau.pdf`, historische Versions-/Akkuranzclaims und kein aktueller Standalone-/Referenzmodul-SSOT. Falls spaeter PDF-Export gebraucht wird, separat als parametrisierte Dokumentationsfunktion neu aufbauen.

Detailaudit: `docs/RESTORE_PACKAGING_AUDIT_2026-06-06.md`

### 7.3 `deploy/server.env`

Verifizierter Heuristik-Befund ohne Werteausgabe:

- erkannte Env-Keys: 15
- nicht-leere Werte: 14
- Platzhalter-aehnliche Werte: 0
- auffaelliger Key-Name: `API_KEY`

Umgesetzter Sicherungsstand 2026-06-06:

- `deploy/server.env` ist jetzt in `.gitignore` als lokale Deploy-Secret-/Runtime-Override-Datei geschuetzt.
- `deploy/server.env.example` wurde mit neutralen Platzhaltern und ohne echte Werte erstellt.
- Der Zustand ist durch `tests/test_repository_data_hygiene.py` als Git-Ignore-/Example-Guard abgesichert.

Baseline-Empfehlung:

- `deploy/server.env` nicht aufnehmen.
- `deploy/server.env.example` aufnehmen.
- Werte aus `deploy/server.env` niemals in Logs, Chat, Dokumentation oder Commits ausgeben.

## 8. Empfohlene Commit-Gruppen spaeter

Kein Commit in dieser Audit-Phase. Wenn der Nutzer die Baseline-Freigabe gibt, dann in kleinen Gruppen:

1. Kontroll-/Datenhygiene-Basis
   - `.gitignore`
   - `pytest.ini`
   - `tests/test_repository_data_hygiene.py`

2. Produktiver Kern + Tests
   - `app/`
   - `dev_cli.py`
   - `main.py`
   - `tests/`

3. Browser-/Workflow-Oberflaeche
   - `user_workflow.*`
   - `workflow_stepping.*`

4. Dokumentation
   - `docs/`
   - ausgewaehlte Root-Markdown-Dateien

5. Konfiguration/Referenzdaten nach separatem Check
   - `data/amplifiers.json`
   - `palettes.json`
   - `preset_profiles.json`
   - `db_import/` als lokaler Referenzdaten-Baseline-Kandidat gemaess `docs/DATA_REFERENCE_AUDIT_2026-06-06.md`

6. Windows-/PowerShell-Betrieb
   - `generate_matrix.ps1`
   - `.bat`-/`.ps1`-Entrypoints

## 9. Naechste empfohlene operative Phase

Die Baseline-Kuratierungsrisiken fuer lokale Runtime-Daten, Deploy-Secrets, Root-Debug-Skripte, `db_import/` und Restore-/Packaging-Sonderfaelle sind dokumentiert und durch `tests/test_repository_data_hygiene.py` abgesichert.

Als naechstes sollte die Initial-Baseline vorbereitet werden, aber erst nach ausdruecklicher Nutzerfreigabe gestaged/committed werden:

1. Vollstaendigen Gitstatus aufnehmen und Commit-Gruppen final abgleichen.
2. Kontroll-/Datenhygiene-Gruppe vorbereiten.
3. Produktiven Standalone-Kern + Tests vorbereiten.
4. Browser-/Workflow-Oberflaeche vorbereiten.
5. Dokumentation und Referenzdaten vorbereiten.
6. Vor externer Veroeffentlichung: Herkunft/Lizenz von `db_import/` separat freigeben.

Erst danach sollte Phase 4 beginnen:

- `generate_matrix.ps1` nur lesend/adapterartig an gemeinsame Metadaten anbinden.
- Bestehende Altdateien weiter unterstuetzen.
- Keine PowerShell-Komplettmigration.
- Keine Kernengine-/Scoring-/Harmonizer-Timing-Aenderung ohne explizite Freigabe.

## 10. Aktueller Verifikationsanker

Vor Erstellung dieses Dokuments war der bekannte gruene Stand:

- Datenhygiene-Test: `9 passed`
- Gesamttest: `41 passed`

Nach Erstellung dieses Dokuments muessen die Tests erneut ausgefuehrt werden, um die Audit-Phase sauber abzuschliessen.
