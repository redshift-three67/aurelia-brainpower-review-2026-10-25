# Morphic Engine V1 – Code-echte Tiefenanalyse 2026-07-07

## Zweck

Diese Dokumentation ist eine aktuelle, codebasierte 1:1-Tiefenanalyse des lokalen Projekts `C:\morphic_v1`. Sie trennt verifizierte Implementierung von Dokumentationsanspruch, Platzhalter, Vorbereitungsnaht und sinnvoller Roadmap.

## Executive Summary

| Dimension | Code-echter Status | Reife | Kurzurteil |
|---|---:|---:|---|
| Projektstruktur / Modularisierung | `apps/cli/main.py` ist auf 95 Zeilen reduziert; CLI-Logik in `apps/cli/commands/*`; Web-Shell in `apps/web/*`; Kern in `core/*`. | 4.2/5 | Solide modularisiert, aber `apps/cli/main_backup_20251203.py` und `web_app.py` bleiben als große Legacy-/Parallelflächen bestehen. |
| Workflow / Steppings | 12-Step-Orchestrator real vorhanden (`apps/cli/workflow/orchestrator.py:28-107`) und Web-UI bildet einen 8-Step-Operator-Wizard ab (`apps/web/static/index.html:22-31`). | 4.1/5 | Gute Ablauftransparenz; nicht alle RadiMorphic-Substeps sind 1:1 implementiert. |
| Runtime / Tests | `.venv/Scripts/python.exe -m pytest tests` = `230 passed, 2 skipped in 118.39s`. Uvicorn Smoke auf `127.0.0.1:8000` erfolgreich. | 4.4/5 | Aktueller Testzustand deutlich besser als ältere Projektmemory-Angaben. |
| Sicherheit | Optionaler API-Key, Pydantic-Validation, Rate-Limit, HTML-Preview-Sanitizer vorhanden. | 2.7/5 | Lokal brauchbar, produktiv/multitenant nicht ausreichend: Auth optional, CORS `*`, keine Rollen/Tenants, keine Security-Header-Baseline. |
| DSGVO / Privacy | Runtime-Manifest, pseudonymisierte Safe-Client-Liste, Löschmanifest, Gate-Token-Löschung, Retention-Purge, Auditlog vorhanden. | 3.4/5 | Gute Grundlage, aber keine echte Verschlüsselung, Zugriffskontrolle, Mandantentrennung oder formales DSAR-/DPIA-Konzept. |
| Authentifizierung / Multitenant | OperatorContext/Ownership/Entitlement-Stubs vorhanden, aber bewusst kein echtes System. | 2.0/5 | Erweiterungsnaht ja; echtes Auth-/Tenant-System nein. |
| Frontend UI/UX | Single-Page Web-Shell mit 8-Step-Wizard, Statuspills, Reportkatalog, Inline-Vorschau, Harmonisierungskontrollen. | 3.6/5 | Stark für lokalen Operator; PWA/RUM/ARIA-Feinschliff/Security-Header fehlen. |
| Google/web.dev 2026 | Als interne lokale App nicht SEO-/Search-Essentials-relevant; web.dev-Qualität weiterhin sinnvoll. | 3.3/5 | Viewport, Responsive, Reduced-Motion vorhanden; CWV/RUM/Touch-Target/Headers fehlen oder nicht gemessen. |

Gesamturteil: Lokale Operator-/Research-Plattform mit hoher funktionaler Dichte und guter Testbasis. Für lokalen Betrieb stabil; für echte Mehrbenutzer-, Mandanten-, produktive Web- oder DSGVO-sensitive Nutzung fehlen harte Auth-, Tenant-, Header-, Verschlüsselungs- und Audit-Governance-Schichten.

## Verifikationsbasis

| Beleg | Ergebnis |
|---|---|
| `git rev-parse --show-toplevel` | `C:/morphic_v1` |
| `git branch --show-current` | `master` |
| `git status --short` vor Analyse-Dokumentation | `M apps/web/static/app.js`, `M apps/web/static/index.html`, `?? .commit_msg_docs.txt`, `?? .commit_msg_feat.txt`, `?? .quantum_check.py` |
| `find`/AST-Analyse via Python | ohne `.git`, `.venv`, `.worktrees`, `PROJECT_MEMORY`, `_backups`, `data`, `Mustermann`: 506 auditierte Dateien; 208 Source-Python-Dateien / 56.970 Zeilen; 73 Testdateien / 7.562 Zeilen; 81 Markdown-Dokumente / 22.082 Zeilen; 3 Web-Static-Dateien / 2.569 Zeilen; 12 PowerShell-Skripte / 2.676 Zeilen |
| `apps/cli/workflow` | 16 Python-Dateien / 1.399 Zeilen; 12 Step-Dateien |
| `apps/cli/commands` | 18 Python-Dateien / 9.724 Zeilen |
| `core` | 84 Python-Dateien / 21.465 Zeilen |
| `apps/web` | 15 Python-Dateien / 2.532 Zeilen |
| `pytest` | `.venv/Scripts/python.exe -m pytest tests` = 230 passed, 2 skipped |
| Port-Preflight | `127.0.0.1:8000` geschlossen vor Smoke; `127.0.0.1:8090` offen; `127.0.0.1:443` geschlossen |
| Web-Smoke | Uvicorn `apps.web.main:app` auf `127.0.0.1:8000`; `/api/status`, `/api/health`, `/api/sources`, `/api/hardware/status`, `/api/privacy/clients`, `/api/reports`, `/api/scan/preview` alle HTTP 200 |
| Google-Live-Websuche | Heute nicht möglich: Hermes-Webtool nicht konfiguriert (`FIRECRAWL_API_KEY`/`FIRECRAWL_API_URL` fehlt). Deshalb: Abgleich auf Basis vorhandener repo-interner Verifikation `docs/deep-audit-2026-07-05/GOOGLE_2026_VERIFIKATION.md` plus statische Codeprüfung. |

## Dokumente dieser Analyse

| Datei | Inhalt |
|---|---|
| `PHASE_0_METHODIK_LIVE_BASELINE.md` | Live-Baseline, Git-/Runtime-/Test-/Smoke-Status, Grenzen der Analyse |
| `PHASE_1_ARCHITEKTUR_STRUKTUR_CODEBASE.md` | Projektstruktur, Schichtenmodell, Module, Datenmodell, technische Schulden |
| `PHASE_2_WORKFLOW_STEPPINGS_SUBSTEPPINGS.md` | CLI-/Web-/12-Step-Workflow, Substep-Mapping, Artefakte, Lücken |
| `PHASE_3_SICHERHEIT_DSGVO_AUTH_MULTITENANT.md` | Security, DSGVO, Privacy, Auth, Multitenant, Findings |
| `PHASE_4_FRONTEND_UIUX_GOOGLE_2026.md` | Frontend UI/UX, Accessibility, Google/web.dev 2026, mobile/responsive/SEO-Einordnung |
| `PHASE_5_LUECKEN_INNOVATIONEN_ROADMAP.md` | Befundmatrix, priorisierte Innovationen, stabile Gate-Roadmap |
| `SITUATION_KONSOLIDIERT_BRANCHES_UI_ANALYSELAUF.md` | **Konsolidierte Situationsanalyse (2026-07-07): Branch-Topologie, korrupter Worktree-Root-Cause, "12 vs 10 Steppings"-Klärung, OpenBLAS-Umgebung, schritt-für-Schritt-Wiederherstellung für Entwickler** |

## Wichtigste Lücken, die vor Umsetzung besprochen werden sollten

| Nr | Bereich | Schwere | Befund | Empfehlung |
|---:|---|---|---|---|
| 1 | Auth/Multitenant | hoch | Kein echtes Login, keine Rollen, kein Tenant-Modell; API-Key optional (`apps/web/security.py:37-52`). | Vor produktiver Web-Nutzung zwingend echtes AuthN/AuthZ/Tenant-Schema. |
| 2 | CORS / Web-Hardening | hoch | CORS erlaubt `*` + Credentials (`apps/web/main.py:181-188`), keine CSP/HSTS/X-Content-Type-Options/Frame-Guard-Middleware sichtbar. | Loopback-only oder allowlist; Security-Headers einführen. |
| 3 | DSGVO-Datenschutz | hoch | Clientdaten liegen dateibasiert/berichtsbasiert lokal; kein Verschlüsselungs-/Key-Management sichtbar. | At-rest encryption, Zugriffskontrolle, Export-/Löschprotokoll härten. |
| 4 | Legacy-Flächen | mittel | `apps/cli/main_backup_20251203.py` 9.436 Zeilen und `web_app.py` 907 Zeilen bleiben im Codebaum. | Als Archiv verschieben oder explizit aus Runtime-/Package-Flächen ausschließen. |
| 5 | Google/CWV | mittel | Keine RUM-/CWV-Instrumentierung, kein Lighthouse-/Playwright-A11y-Gate. | Web-Quality-Gate additiv in Tests/CI aufnehmen. |
| 6 | Operator Ownership | mittel | Ownership-Stubs existieren, aber Web-Endpoints nutzen sie nicht durchgängig sichtbar. | Job-/Report-/Manifestzugriffe an OperatorContext binden. |

## Nächste sinnvolle Besprechungsagenda

1. Entscheiden, ob Ziel weiter `lokaler Ein-Operator-Betrieb` oder `produktive Mehrbenutzer-/Tenant-Plattform` ist.
2. Wenn produktiv: Phase A `Security Baseline` vor UI-Innovationen.
3. Wenn lokal: Phase A `Legacy-/Dokumentationsbereinigung + Workflow-UX-Feinschliff` genügt.
4. DSGVO: Datenklassifizierung, Retention-Policy, Löschprozess und Verschlüsselung explizit definieren.
5. Frontend: entscheiden, ob Web-Shell nur Operator-Workbench bleibt oder patienten-/kundennahe Oberfläche werden soll.
