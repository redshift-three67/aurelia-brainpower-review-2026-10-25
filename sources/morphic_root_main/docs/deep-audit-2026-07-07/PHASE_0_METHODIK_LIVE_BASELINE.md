# PHASE 0 – Methodik, Live-Baseline und verifizierter Ist-Zustand

## 0.1 Analysemodus

| Punkt | Status |
|---|---|
| Modus | Codebasierte Tiefenanalyse mit statischer AST-/Dateianalyse, gezielten Datei-Reads, Git-/Port-/Pytest-/Web-Smoke-Verifikation |
| Projektroot | `C:\morphic_v1` |
| Schreibzugriff | Nur Dokumentation unter `docs/deep-audit-2026-07-07/`; keine Produktivcode-Änderung |
| Sprache | Deutsch, Entwickler-orientiert, phasen-/gatefähig |
| Google-/Web-Recherche | Live-Webtool nicht konfiguriert; heutige Websuche blockiert. Repo-interne Google-2026-Verifikation vom 2026-07-05 wurde gelesen und mit aktuellem UI-Code abgeglichen. |

## 0.2 Git-Baseline

| Befehl | Ergebnis |
|---|---|
| `git rev-parse --show-toplevel` | `C:/morphic_v1` |
| `git branch --show-current` | `master` |
| `git log --oneline -10` | HEAD `225beac feat: add radiquant4 alignment layer for platform readiness`; danach mehrere Docs-/UX-/Hardware-Commits |
| `git status --short` vor neuen Docs | `M apps/web/static/app.js`; `M apps/web/static/index.html`; `?? .commit_msg_docs.txt`; `?? .commit_msg_feat.txt`; `?? .quantum_check.py` |

Wichtig: Die Analyse hat vorhandene geänderte UI-Dateien nicht berührt. Neu hinzugekommen sind nur Markdown-Dateien in `docs/deep-audit-2026-07-07/`.

## 0.3 Host-/Port-Baseline

| Prüfung | Ergebnis | Bedeutung |
|---|---|---|
| `127.0.0.1:8000` | geschlossen vor Smoke | Für kurzzeitigen Uvicorn-Smoke frei. |
| `127.0.0.1:8090` | offen | Benutzerpräferenz beachten: Port 8090 ist belegt, nicht für Tests/Webserver verwenden. |
| `127.0.0.1:443` | geschlossen | Kein lokaler HTTPS-Dienst erkannt. |

## 0.4 Python-/Test-Baseline

| Prüfung | Ergebnis | Bewertung |
|---|---|---|
| `command -v python` | Hermes-Agent-Venv: `C:/Users/Hubert111/AppData/Local/hermes/hermes-agent/venv/Scripts/python` | Falscher Interpreter für Projekt-Tests; kein `pytest`. |
| `python --version` | `Python 3.11.12` | Nicht das Projektvenv. |
| `.venv/Scripts/python.exe --version` | `Python 3.12.10` | Projektinterpreter. |
| `.venv/Scripts/python.exe -m pytest tests` | `230 passed, 2 skipped in 118.39s` | Aktueller Live-Teststand; neuer als `PROJECT_MEMORY/00_CURRENT_STATE.md` mit 153 Tests. |
| Direkter `fastapi.testclient.TestClient` | blockiert: `starlette.testclient` verlangt `httpx2` | Kein Produktivblocker, da Test-Suite grün; aber manueller TestClient-Smoke benötigt Zusatzdependency oder Server-Smoke. |

## 0.5 Web-Smoke über echten Server

Uvicorn wurde temporär gestartet mit:

`C:\morphic_v1\.venv\Scripts\python.exe -m uvicorn apps.web.main:app --host 127.0.0.1 --port 8000`

Danach wurden per HTTP folgende Endpunkte geprüft:

| Endpunkt | HTTP | Ergebnis-Auszug |
|---|---:|---|
| `/api/status` | 200 | `{"status":"ok","version":"1.0.0","server":"Morphic Engine V1"}` |
| `/api/health` | 200 | `ok=true`, Projektroot `C:\morphic_v1`, Python `.venv\Scripts\python.exe`, Version `3.12.10` |
| `/api/sources` | 200 | `count=18`, `active=16`, `quarantined=2` |
| `/api/hardware/status` | 200 | Windows 10, AMD64, CPU/GPU/Sensor-Status wird ausgegeben |
| `/api/privacy/clients` | 200 | `count=5`, nur sichere Client-IDs/Zeitstempel, keine Namen im Safe-Endpoint |
| `/api/reports` | 200 | `count=449`, `root_count=5`, `client_count=4` |
| `/api/scan/preview` | 200 | CLI-Preview erzeugt; `unsupported_request_fields=[]`; produktiver CLI-Pfad `.venv\Scripts\python.exe -m apps.cli.main scan top3-scan` |

Uvicorn-Prozess wurde danach beendet.

## 0.6 Codeumfang – bereinigte Zählung

Ausschlüsse: `.git`, `.venv`, `venv`, `__pycache__`, `.pytest_cache`, `.worktrees`, `PROJECT_MEMORY`, `Benutzer_Archive`, `codex_tmp`, `_backups`, `data`, `Mustermann`, `_test_top3scan_tmp`.

| Kategorie | Dateien | Zeilen |
|---|---:|---:|
| Source Python | 208 | 56.970 |
| Tests Python | 73 | 7.562 |
| Docs Markdown | 81 | 22.082 |
| Web Static (`apps/web/*.html/js/css`) | 3 | 2.569 |
| PowerShell-Skripte | 12 | 2.676 |
| Auditierte Dateien gesamt | 506 | n/a |

Top Source-Dateien:

| Rang | Datei | Zeilen | Einordnung |
|---:|---|---:|---|
| 1 | `apps/cli/main_backup_20251203.py` | 9.436 | Legacy-/Backup-Datei im Source-Baum; nicht Entry-Point, aber Risiko für Verwirrung/Packaging. |
| 2 | `apps/cli/commands/field.py` | 4.454 | Größte aktive CLI-Kommandofläche: Field-/Multiplex-/Workflow-Scan. |
| 3 | `apps/cli/commands/scan.py` | 2.593 | Scan-/Overview-/Diagnostics-/Batch-Logik. |
| 4 | `core/profile_sync/__init__.py` | 1.878 | Profil-/Registry-Synchronisierung. |
| 5 | `core/subgroups/procedural_groups.py` | 1.638 | große Gruppe-/Taxonomiefläche. |
| 6 | `apps/cli/commands_extended.py` | 1.140 | optionaler Extended-Typer; möglicher zweiter CLI-Pfad. |
| 7 | `web_app.py` | 907 | alte Web-App/Parallelfläche; Kommentar verweist auf `apps.web.main:create_app`. |

## 0.7 Abweichung zu älteren Projektmemory-Daten

| Quelle | Alter Stand | Live-Stand 2026-07-07 | Bewertung |
|---|---:|---:|---|
| `PROJECT_MEMORY/00_CURRENT_STATE.md` | 153 Tests | 230 passed, 2 skipped | Projekt ist seit Golden Record fortgeschritten. Golden Record ist nützlich, aber nicht mehr vollständig aktuell. |
| `CLAUDE.md` | main.py 72 Zeilen | `apps/cli/main.py` 95 Zeilen | Zusätzliche Delegation/Kompatibilität seitdem. |
| `PROJECT_MEMORY/00_CURRENT_STATE.md` | Zwei Web-Apps überlappen | Live bestätigt: `web_app.py` noch vorhanden, `apps/web/main.py` aktiv | Offener Architekturpunkt bleibt gültig. |

## 0.8 Grenzen dieser Analyse

| Grenze | Konsequenz |
|---|---|
| Keine externe Google-Websuche möglich | Google-2026-Bewertung basiert auf vorhandener repo-interner Verifikation und allgemein bekannten web.dev-Prinzipien; keine neue Live-Quelle wurde geladen. |
| Keine Browser-Pixel-/Lighthouse-Messung | UI/UX-Bewertung ist Code-/Struktur-/Smoke-basiert, nicht visuell mit Screenshot oder CWV-Labwerten gemessen. |
| Keine produktive Security-Pentest-Ausführung | Security-Bewertung ist statisch plus Endpoint-Smoke, kein Fuzzing/DAST. |
| Keine personenbezogenen Rohdaten geöffnet | Datenschutzbewertung nutzt Codepfade/Manifest-Endpunkte, nicht Inhalte realer Berichte. |
