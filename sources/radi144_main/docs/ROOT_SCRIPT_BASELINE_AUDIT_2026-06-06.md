# Radi144 Root-Skript-Baseline-Audit

Stand: 2026-06-06
Projektwurzel: `/home/klaus999/projects/Radi144`

## 1. Zweck

Dieses Dokument klassifiziert Root-nahe Skripte vor einer kuratierten initialen Git-Baseline. Ziel ist, aktive Produkt-/Workflow-Einstiegspunkte von einmaligen Diagnose-, Reparatur- und Legacy-Debug-Artefakten zu trennen.

Wichtig: Die Skripte wurden fuer diese Klassifizierung **nicht ausgefuehrt**. Die Bewertung erfolgte durch Dateiname, Groesse, erste Zeilen, statische Heuristik und Git-/Baseline-Risiko.

## 2. Sicherheitsgrenze

Nicht veraendert:

- Kernengine
- Resonanzscore
- Matrixlogik
- Top-10/Top-3-Auswertung
- EMF-/Audio-/Harmonizer-Algorithmen
- Runtime JSON-Daten
- `deploy/server.env` Werte

## 3. Aktive Baseline-Kandidaten

Diese Root-Dateien bleiben aktuell Git-kandidatenfaehig und sollten vor einem Initial-Commit in die produktive Baseline-Gruppe aufgenommen werden, sofern die naechste Gesamtpruefung gruen bleibt:

| Datei | Bewertung | Begruendung |
|---|---|---|
| `main.py` | aufnehmen | FastAPI/Uvicorn-Einstiegspunkt, produktiver API-Start |
| `dev_cli.py` | aufnehmen | zentrale CLI, Client/Session/Report-Mirroring, produktiver Workflow |
| `generate_matrix.ps1` | aufnehmen, aber spaeter Phase-4-adapterartig pruefen | zentraler Windows/PowerShell-Matrixworkflow laut Umsetzungsplan |
| `run.bat` | aufnehmen | Windows-Operator-Einstiegspunkt |
| `run_test.bat` | aufnehmen | Windows-Preflight/Test-Entrypoint, aktuell bewusst Kandidat |
| `setup_new_pc.bat` | aufnehmen nach manueller Installationspruefung | reproduzierbarer Setup-Hinweis fuer Windows-Zielumgebung |
| `install_dependencies.bat` | aufnehmen nach manueller Installationspruefung | Abhaengigkeits-/Setup-Dokumentation fuer Windows |
| `user_workflow.html` | aufnehmen | Browser-Workflow UI |
| `user_workflow.js` | aufnehmen | Browser-Workflow Logik |
| `workflow_stepping.html` | aufnehmen | Workflow-Stepping UI |
| `workflow_stepping.js` | aufnehmen | Workflow-Stepping Logik |

## 4. Aus initialer Baseline ausgeschlossene Root-Diagnose-/Reparaturartefakte

Diese Dateien wurden als einmalige oder legacy-nahe Diagnose-/Fix-/Verifikationsartefakte klassifiziert und sind jetzt explizit in `.gitignore` aufgefuehrt:

| Datei | Grund |
|---|---|
| `check_bom.py` | BOM-/Encoding-Einmaldiagnose fuer `generate_matrix.ps1`/`focus_history.txt` |
| `check_bom_v2.py` | Windows-Pfad-gebundene BOM-Diagnose (`c:\\Users\\...`) |
| `check_output.py` | lokale `Analysen/`-Ausgabepruefung |
| `check_palettes_bom.py` | Windows-Pfad-gebundene Palette-BOM-Diagnose |
| `debug_export.py` | schreibt lokale Analyse-/Debug-Ausgaben |
| `debug_gui.py` | isolierter Tkinter-GUI-Debug |
| `debug_imports.py` | schreibt `import_debug.log`, Importdiagnose |
| `debug_test.py` | schreibt `debug_output.txt`, Einmaldiagnose |
| `diag_check.py` | lokale Torch/Systemdiagnose |
| `fix_encoding.py` | schreibt/veraendert `focus_history.txt` |
| `fix_encoding_bom.py` | BOM-/Encoding-Reparatur fuer Root-Dateien |
| `inspect_history.py` | lokale `focus_history.txt`-Inspektion |
| `reproduce_issue.py` | isolierte Reproduktion mit Tkinter/Winsound, kein produktiver SSOT |
| `test_audio.py` | manuelles Windows-Audioexperiment, nicht Teil der Pytest-Suite |
| `test_date.py` | manuelle Datumsparse-Probe |
| `test_engine.py` | manuelle Engine-Import-/Smoke-Probe |
| `test_pdf.py` | manuelle PDF-Ausgabeprobe in `Analysen/` |
| `verify_config.py` | manuelle Config-/Umgebungsprobe |
| `verify_execution.py` | fuehrt `dev_cli.py` mit Testdaten aus; nicht als Root-Artefakt committen |
| `verify_fix.py` | manuelle Client-Signature-Pruefung |
| `verify_fix_v2.py` | manuelle Import-/Client-Signature-Pruefung |
| `verify_umlaut_flow.py` | manuelle Umlaut-/Encoding-Probe |
| `generate_analysis_pdf.py` | am 2026-06-07 geprueft: harter historischer Windows-Ausgabepfad, stale Version-/Akkuranzclaims, kein aktueller Standalone-/Referenzmodul-SSOT; fuer PDF-Export spaeter neu/parametrisiert aufbauen |

## 5. Erledigte Sonderfall-Entscheidungen

Diese Dateien wurden nach separater statischer Pruefung explizit aus der initialen Baseline ausgeschlossen und durch `.gitignore` plus Repository-Hygiene-Tests abgesichert:

| Datei | Grund |
|---|---|
| `create_restore_point.py` | stale in-repo RestorePoint-Erzeugung; externe ShadowCopies sind aktueller Sicherungsstandard |
| `create_restore.ps1` | stale Windows-RestorePoint-Erzeugung; nicht aktueller PowerShell-Baseline-Entrypoint |
| `finalize_project.py` | vermischt Release, Dokumenterzeugung und Backup; stale Versions-/Dokumentationsstand |
| `generate_analysis_pdf.py` | stale historischer PDF-Generator mit hartem Benutzerpfad und nicht verifizierten Altclaims |

Details: `docs/RESTORE_PACKAGING_AUDIT_2026-06-06.md` und `docs/GIT_BASELINE_AUDIT_2026-06-06.md`.

## 6. Automatisierter Guard

Erweitert wurde:

- `tests/test_repository_data_hygiene.py`

Neue Schutzregeln:

1. Legacy Root-Diagnose-/Einmal-Reparaturskripte muessen ignoriert bleiben.
2. Aktive Root-Einstiegspunkte muessen Git-kandidatenfaehig bleiben.

Damit wird verhindert, dass ein spaeterer `.gitignore`-Umbau versehentlich Debug-/Fix-Artefakte in die Baseline zieht oder aktive Entrypoints ausblendet.

## 7. Baseline-Entscheidung fuer den naechsten Schritt

Naechste notwendige Prioritaet:

1. Kuratierte Initial-Baseline-Gruppen bilden.
2. Keine Sammelaufnahme via `git add .`.
3. Vor Staging/Commit ausdrueckliche Nutzerfreigabe einholen.

Noch kein `git add .` verwenden.
