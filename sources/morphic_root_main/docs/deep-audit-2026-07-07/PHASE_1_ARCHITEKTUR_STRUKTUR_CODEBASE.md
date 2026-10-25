# PHASE 1 – Architektur, Projektstruktur und Codebase-Status

## 1.1 Schichtenmodell

```text
Operator / CLI / Web
├─ apps/cli/main.py                    Typer-Entry-Point, Delegation an commands/*
├─ apps/cli/commands/*                 produktive CLI-Kommandos
├─ apps/cli/workflow/*                 12-Step-Workflow-Orchestrator
├─ apps/web/main.py                    aktive FastAPI Web-Shell
├─ apps/web/static/*                   lokale Operator-UI
│
Application Services
├─ services/*                          Analyse-, Harmonization-, Remedy-/Report-Services
├─ tools/*                             Reporting/PDF/Interpretation/Export-Helfer
│
Domain Core
├─ core/nls/*                          NLS DB / Scoring
├─ core/quantum_synergy/*              Grover/Hybrid Quantum Synergy mit Fallback
├─ core/hardware/*                     Entropie/Sensor/Driver/Snapshot Layer
├─ core/compliance/*                   Runtime Manifest, Safety, OperatorContext, Platform Export
├─ core/subgroups/*                    Fachliche Gruppen-/Taxonomie-Registries
├─ core/profile_sync/*                 Profilkatalog/-Sync
│
Data / Runtime / Reports
├─ data/runtime/*.json                 Clients/Sessions/Artifacts/Auditlog/Workspace-ID
├─ C:/Benutzer_*_Start                 produktive Report-Wurzeln laut Code
├─ docs/*                              Audit-/Plan-/Referenzdokumentation
```

## 1.2 Top-Level-Struktur – code-echter Status

| Pfad | Status | Beleg | Bewertung |
|---|---|---|---|
| `apps/cli/main.py` | aktiver Typer-Entry-Point | `app = typer.Typer(...)` in `apps/cli/main.py:39`; Typer-Registrierung `scan/trend/harmonize/...` in `apps/cli/main.py:41-50` | Gut: schlanker Delegationspunkt. |
| `apps/cli/commands/` | aktive CLI-Kommandos | 18 Python-Dateien / 9.724 Zeilen; u. a. `field.py`, `scan.py`, `privacy.py`, `sources.py` | Funktional stark, aber `field.py`/`scan.py` noch sehr groß. |
| `apps/cli/workflow/` | 12-Step-Orchestrator | `run_workflow(...)` sequenziert Step 1-12 in `apps/cli/workflow/orchestrator.py:73-89` | Gut isoliert, state-getrieben. |
| `apps/web/main.py` | aktive Web-Shell | `app = create_app()` in `apps/web/main.py:558`; Endpunkte `/api/*` | Aktiv, Smoke erfolgreich. |
| `apps/web/static/` | lokale UI | `index.html` 402 Zeilen, `app.js` 963 Zeilen, `app.css` 1.204 Zeilen | Gute Single-Page-Workbench, aber noch ohne Build-System/RUM. |
| `core/compliance/` | Compliance-Grundlagen | `runtime_manifest.py`, `safety.py`, `operator_context.py`, `entitlement_stub.py`, `platform_export.py` | Gute Erweiterungsnaht; produktive Security/DSGVO noch unvollständig. |
| `core/hardware/` | Hardware-/Realtime-Schicht | Driver, Sensors, Entropy, Snapshots; Tests vorhanden | Additiv und defensiv; echte externe Hardware opt-in. |
| `docs/` | umfangreiche Architektur-/Audit-Historie | 81 Markdown-Dateien / 22.082 Zeilen vor dieser Analyse | Sehr gute Nachvollziehbarkeit; Gefahr von Drift, da ältere Golden Records nicht mehr aktuell. |
| `web_app.py` | Legacy-/Parallel-Web-App | 907 Zeilen; eigener alter `/api/v1/*`-Pfadbestand | Muss klar archiviert oder deaktiviert bleiben, um Doppelwahrheit zu vermeiden. |
| `apps/cli/main_backup_20251203.py` | große Backup-Datei im Source-Baum | 9.436 Zeilen | Technische Schuld: kann Packaging/Analyse/Imports verwirren. |

## 1.3 CLI-Kommandofläche

| Modul | Zeilen | Registrierte Commands | Bemerkung |
|---|---:|---|---|
| `apps/cli/commands/scan.py` | 2.593 | `groups-overview`, `hw-diagnostics`, `multiplex-scan`, `top3-scan`, `batch-scan`, `bat-area-scan`, `nls-3d-export`, `analyze` | Zentrale Scan-/Diagnosefläche. |
| `apps/cli/commands/field.py` | 4.454 | `field_test`, `multiplex-scan`, `workflow-scan` | Größte aktive Datei; enthält Field-/Workflow-Logik. |
| `apps/cli/commands/harmonize.py` | 90 | `harmonize`, `harmonize-status`, `harmonize-stop` | Job-orientierte Harmonisierung. |
| `apps/cli/commands/privacy.py` | 92 | `clients`, `erasure-manifest`, `erase`, `purge-expired`, `audit` | DSGVO/Privacy-CLI real vorhanden. |
| `apps/cli/commands/sources.py` | 246 | `list`, `enable`, `disable`, `validate`, `stage`, `import`, `rollback`, `data-stage`, `data-promote` | Source Registry und Import-/Promotion-Gates. |
| `apps/cli/commands/synergy.py` | 200 | `optimize`, `analyze`, `stats` | Synergy-Analyse und Optimierung. |
| `apps/cli/commands/trend.py` | 260 | `analyze-trends`, `client-trends` | Trendhistorie. |
| `apps/cli/commands/descriptions.py` | 72 | `descriptions-sync`, `descriptions-status`, `descriptions-generate` | Beschreibungsdatenbank. |

## 1.4 Web-API-Fläche

Aktive App: `apps/web/main.py:create_app`.

| Bereich | Endpunkte | Beleg | Status |
|---|---|---|---|
| Status/Health | `/api/status`, `/api/health`, `/api/hardware/status` | `apps/web/main.py:235-293` | Smoke 200. |
| Quellen | `/api/sources` | `apps/web/main.py:295-303` | Smoke 200, 18 Quellen. |
| Privacy | `/api/privacy/clients` | `apps/web/main.py:305-309` | Smoke 200, Safe-Client-Liste ohne Namen. |
| Reports | `/api/reports`, `/api/reports/{id}/preview`, `/api/reports/{id}/file` | `apps/web/main.py:311-335`, `apps/web/reports.py` | Smoke 200; HTML-Sanitizer vorhanden. |
| Harmonisierung | POST `/api/harmonization/jobs`, GET status, POST stop | `apps/web/main.py:337-378` | API-Key-Dependency vorhanden, aber optional. |
| Scan | POST `/api/scan/preview`, POST `/api/scan/jobs`, GET job/status/results | `apps/web/main.py:380-553` | Preview-Smoke 200, Job-Service dateiloggesteuert. |
| Live | WebSocket `/api/scan/jobs/{job_id}/ws` | `apps/web/scan_live.py:23` | Vorhanden, nicht im Smoke getestet. |

## 1.5 Datenmodell und Persistenz

| Datenbereich | Implementierung | Beleg | Datenschutz-/Architekturstatus |
|---|---|---|---|
| Runtime Clients | JSON Store `clients.json`; ID `cli-<sha256[:20]>` aus Vorname/Nachname/Geburtsdatum/Geburtsort | `core/compliance/runtime_manifest.py:38-50`, `108-144` | Pseudonymisierte ID; Rohdaten weiterhin im Store. |
| Sessions | JSON Store `sessions.json`; IDs `sess-<uuid>` oder übergeben | `core/compliance/runtime_manifest.py:146-178` | Einfach, dateibasiert, keine DB-Transaktionen. |
| Artifacts | JSON Store `artifacts.json`; Pfad/Typ/Label | `core/compliance/runtime_manifest.py:180-221` | Nachvollziehbar, aber Pfade enthalten potenziell sensitive Struktur. |
| Auditlog | JSON Store `audit_log.json` | `core/compliance/runtime_manifest.py:81-106` | Gute Grundlage; keine Tamper-Evidence/Kryptosignatur. |
| Reports | Dateisystem unter `C:/Benutzer_Archive_Start`, `C:/Benutzer_Synergy_Start`, `C:/Benutzer_Remedies_Start`, `C:/Benutzer_Trends_Start`, `C:/Benutzer_Deutung_Start` | `apps/web/main.py:54-60`; ReportCatalog | Real aktiv; Smoke zeigt 449 Reports. |
| Source Registry | `SourceRegistry.load_default()` | `apps/web/main.py:295-303`, `apps/cli/commands/sources.py` | Gate-/Stage-/Promote-Struktur vorhanden. |

## 1.6 Architektur-Befunde

| Nr | Kategorie | Schwere | Befund | Beleg | Empfehlung |
|---:|---|---|---|---|---|
| A1 | Modularisierung | niedrig | `main.py` ist erfolgreich schlank und delegiert sauber. | `apps/cli/main.py:39-50`, `86-95` | Beibehalten; keine Rückmigration in Monolith. |
| A2 | Legacy | mittel | `apps/cli/main_backup_20251203.py` liegt als 9.436-Zeilen-Backup im Source-Baum. | LOC-Analyse | In `archive/` verschieben oder Packaging-/Test-Ausschluss dokumentieren. |
| A3 | Legacy Web | mittel | `web_app.py` enthält eigene `/api/v1/*`-Routen und überlappt mit `apps/web/main.py`. | AST-Routenanalyse; `web_app.py` 907 Zeilen | Offiziell als deprecated markieren, Importpfade prüfen, mittelfristig archivieren. |
| A4 | Große Module | mittel | `field.py` 4.454 Zeilen, `scan.py` 2.593 Zeilen. | LOC-Analyse | Spätere Gate-Extraktion nach Verantwortung: Export, NLS, Client, Reporting, CLI-Adapter. |
| A5 | Dokumentationsdrift | mittel | Golden Record nennt 153 Tests; live sind 230 passed/2 skipped. | `PROJECT_MEMORY/00_CURRENT_STATE.md`, Pytest-Live | `PROJECT_MEMORY`/`CLAUDE.md` nach Audit synchronisieren. |
| A6 | Daten-/Code-Mischung | niedrig-mittel | Projekt enthält sehr große `data`/Backup/Report-Bereiche; Analyse muss stark ausschließen. | LOC-Analyse mit massiven `data`-Zeilen | Repo-Hygiene prüfen: produktive Daten nicht mit Source/Docs vermischen, sofern Git-tracked. |

## 1.7 Reifegrad Phase 1

| Dimension | Score | Begründung |
|---|---:|---|
| Schichtenklarheit | 4.0/5 | `apps`, `core`, `services`, `tools`, `docs` gut getrennt. |
| Entry-Point-Klarheit | 4.2/5 | `apps/cli/main.py` und `apps/web/main.py` klar; `web_app.py` stört. |
| Testbarkeit | 4.4/5 | 230 Tests grün, viele Kontrakt-/Smoke-/Equivalence-Tests. |
| Wartbarkeit | 3.5/5 | Große Module und Legacy-Dateien bleiben. |
| Dokumentierbarkeit | 4.3/5 | Viele Docs, aber Drift-Risiko. |

Phase-1-Urteil: Architektur ist lokal stabil und deutlich gereift. Hauptlücke ist nicht fehlende Funktion, sondern Konsolidierung/Archivierung und Vermeidung doppelter Wahrheiten.
