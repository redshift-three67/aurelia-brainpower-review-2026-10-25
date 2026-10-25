# Phase 0 – Prüfgrundlage, Projektgröße und echte Laufzeit

## 0.1 Prüfgegenstand

| Attribut | Verifizierter Wert |
|---|---|
| Projektwurzel | `C:/morphic_v1/.worktrees/operator-workbench-phase1` (`git rev-parse --show-toplevel`) |
| Branch / HEAD | `operator-workbench-phase1` / `619a1f5` |
| Arbeitsbaum | ein ungetrackter Exportordner `Benutzer_Archive__ws-8fa0e23e88354d08/`; nicht verändert |
| Python-Runtime | `C:/morphic_v1/.venv/Scripts/python.exe`, im Health-Endpunkt Python 3.12.10 |
| deklarierte Mindestversion | Python >=3.10 (`pyproject.toml:5-23`) |
| Git Remote | keiner; Backup-/CI-/Release-Nachweis ist lokal nicht gegeben |

## 0.2 Umfang

Die Zählung schließt `.git`, `.venv`, Caches, `codex_tmp` und Exportordner aus. Das Inventarskript ergab **290 Python-Dateien / 66.420 Zeilen**, 87 HTML-Dateien / 30.721 Zeilen, 6 JavaScript-Dateien / 2.224 Zeilen, 4 CSS-Dateien / 2.639 Zeilen und 79 getrackte Testmodule. Große SQL-Dumps (`data/oorep*.sql`, je 1.513.559 Zeilen) sind Daten, nicht Anwendungslogik.

Die breite Struktur entspricht README: `apps/` als Interfaces, `core/` als Domänenlogik, `services/` als Orchestrierung, `providers/` als Hardware/Entropieadapter, `tools/` als Berichts-/Postprocessing, `data/` als Daten und `tests/` als Prüfschicht. Die aktuelle README ist jedoch sachlich veraltet: sie behauptet Python 3.13, Platzhalter-Dependencies und „repository scaffolding“ (`README.md:23-28`), obwohl aktuelle Venv, CLI, FastAPI und Tests funktionieren.

## 0.3 Reproduzierte Prüfungen

| Prüfung | Resultat | Interpretation |
|---|---|---|
| Volltest | 282 passed, 2 skipped in 124.05s | Regressionstestnetz ist aktiv; kein Coverage-Prozentwert erhoben |
| CLI help | Root-, Scan- und Privacy-Help erfolgreich | modularer Typer-Einstieg ist real verfügbar (`apps/cli/main.py:39-95`) |
| Syntax | 10 zentrale Python-Module via `ast.parse`; 4 Workbench-JS-Dateien via `node --check` | fehlerfrei |
| Web HTTP smoke | HTTP 200 für Startseite, Status, Health, Static JS | kontrollierter lokaler Read-only-Smoke; Server danach beendet |
| Portpreflight | 8000 und 8090 bereits belegt; daher Audit-Shell auf 8001 | keine fremden Prozesse beendet |

## 0.4 Reifegrad (Ist, kein Zielbild)

| Dimension | Wert / 5 | Begründung |
|---|---:|---|
| Funktionalität | 4.0 | CLI, Web-Shell, Reports und Harmonization sind real verdrahtet und getestet. |
| Codequalität | 3.2 | gute modulare Zielstruktur; zugleich große Legacy-/Backup-Dateien und viele catch-all-Fallbacks. |
| Testabdeckung | 3.8 | 282 Tests decken zentrale Verträge, Exporte, Web und Hardware-Fallbacks ab; kein gemessener Coverage-Wert, kein Browser-E2E-Test. |
| Dokumentation | 3.1 | zahlreiche Detaildocs, aber README und alte Auditberichte driften. |
| DevOps/Betrieb | 2.0 | kein Remote, kein CI-Konfigurationsnachweis, keine production-grade Secret-/Deployment-Policy. |
| Security/Privacy | 2.2 | nützliche lokale Schutzbausteine, aber kein echtes AuthN/AuthZ und Klartextpersistenz. |
| UI/UX | 3.8 | erklärter 11-Phasen-Operatorflow, Tastatur-/A11y-Bausteine; Validierungs- und Fehlerführung lückenhaft. |
| Gesamt (gewichtete Einschätzung) | **3.2 / 5** | lokal stabiler, gut testbarer Operator-Prototyp; noch nicht internet- oder mandantenproduktionsreif. |

## 0.5 Historische Einordnung

Die Git-Historie zeigt eine echte Konsolidierung vom 2026-07-01 bis 2026-07-10: Modularisierung, Web-Shell, API-Key/Rate-Limit, Runtime-Privacy, Hardware-/Realtime-Layer, Operator Workbench, Reporting-PDFs und Tenant-Suffixierung. Der alte Bericht `docs/PROJEKT_TIEFENANALYSE_20260628.md` ist als Historie nützlich, aber kein Ist-Nachweis mehr; seine damaligen P0-Import-/Venv-Probleme sind durch die heutigen Prüfergebnisse überholt.
