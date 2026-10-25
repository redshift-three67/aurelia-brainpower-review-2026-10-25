# Phase 1 - Codebase Architektur Und Struktur

## Kurzfazit

Die Codebasis ist funktionsreich, aber nicht streng konsolidiert.
Sie folgt grob dem Muster `apps -> services/core/providers/tools`, haelt aber mehrere Legacy- und Parallelpfade gleichzeitig aktiv.
Die wichtigste strukturelle Eigenschaft ist nicht Modularitaet, sondern Koexistenz mehrerer Entwicklungsstufen.

## Reale Top-Level-Struktur

| Pfad | Rolle | Statusbewertung |
| --- | --- | --- |
| `apps/cli/` | primaere CLI-Einstiegspunkte und Produktionskommandos | zentral |
| `apps/web/` | aktuelle FastAPI-Web-App plus statische Web-Shell | zentral |
| `apps/server/` | separater WebSocket-Server | Nebenpfad |
| `apps/viewer/` | Viewer/Anatomie-Frontend | Spezialpfad |
| `core/` | Fachlogik, Resonanz, Hardware, Compliance, Profile, Quantum | zentral |
| `providers/` | Hardware-/Entropie-Adapter | zentral |
| `services/` | Service-Fassaden und Worker | zentral |
| `tools/` | Reporting- und Export-Postprocessing | zentral |
| `data/` | DBs, Runtime-Manifeste, Job-Dateien, generierte Daten | zentral |
| `tests/` | pytest-Regressionssuite | stark ausgebaut |
| `PROJECT_MEMORY/` | Memory- und Hand-off-Dokumente | historisch nuetzlich, teils veraltet |
| `web_ui/` | aeltere UI-Linie | Legacy |
| `web_app.py` | aeltere FastAPI-App | Legacy |
| `logs/`, `codex_tmp/`, `analysis_reports/`, `Benutzer_Archive/` | Laufzeit- und Artefaktablage im Repo-Baum | hygiene-kritisch |

## Entry-Points

### CLI

| Entry-Point | Datei | Zweck |
| --- | --- | --- |
| `python -m apps.cli.main` | `apps/cli/main.py` | Root-Typer-App |
| `scan top3-scan` | `apps/cli/commands/scan.py` | produktiver Top-N Auto-Scan |
| `field multiplex-scan` | `apps/cli/commands/field.py` | tiefer Produktionsscan pro Profil |
| `field workflow-scan` | `apps/cli/commands/field.py` | separater 12-Step-Orchestrator |
| `health` | `apps/cli/commands/health.py` | Runtime-/DB-/Pfad-Pruefung |
| `privacy *` | `apps/cli/commands/privacy.py` | DSGVO-nahe CLI-Funktionen |

### Web

| Entry-Point | Datei | Zweck |
| --- | --- | --- |
| `apps.web.main:app` | `apps/web/main.py` | aktuelle Web-App |
| `web_server.py` | `web_server.py` | Bootstrap fuer aktuelle Web-App |
| `/` | `apps/web/static/index.html` | 8-Step Web-Shell |
| `/workflow-stepping` | `apps/cli/workflow/workflow_stepping.html` | separate 12-Step-Dokumentationsseite |
| `/api/analyze` | `apps/web/analyze.py` | synchroner 12-Step-Webpfad |
| `web_app.py` | `web_app.py` | deprecated Legacy-App |

## Layering im Ist-Zustand

### 1. UI und Orchestrierung

- `apps/web/main.py:154-558`
- `apps/web/static/index.html`
- `apps/web/static/app.js`
- `apps/cli/main.py`
- `Run-MultiplexScan.ps1`

Diese Ebene nimmt Nutzereingaben entgegen, baut CLI-Kommandos, startet Jobs und visualisiert Report- und Jobstatus.

### 2. Produktionskommandos

- `apps/cli/commands/scan.py`
- `apps/cli/commands/field.py`
- `apps/cli/commands/trend.py`
- `apps/cli/commands/synergy.py`
- `apps/cli/commands/descriptions.py`

Hier liegt der groesste Teil der effektiven Produktlogik, nicht nur ein schmaler Adapter.
Insbesondere `field.py` und `scan.py` tragen einen grossen Teil der orchestralischen und fachlichen Last.

### 3. Fachlogik

- Profile und Encoding: `core/profiles/profile.py`
- Profilkatalog: `core/profile_sync/*`
- Kandidatengenerierung/Gruppen: `core/subgroups/*`
- NLS/Scoring: `core/nls/*`, `services/nls_service.py`
- Resonanz: `core/resonance/*`
- Quantum-Synergy: `core/quantum_synergy/*`
- Hardware/Realtime: `core/hardware/*`, `core/realtime/*`
- Compliance: `core/compliance/*`

### 4. Provider- und Adapterebene

- `providers/hardware/entropy_sources.py`
- `providers/hardware/hardware_entropy.py`

Hier sitzt die Auswahl bzw. Kapselung unterschiedlicher Entropie- und Hardwarequellen.

### 5. Reporting- und Nachverarbeitungsebene

- `tools/reporting_common.py`
- `tools/synergy_consolidator.py`
- `tools/remedy_reporter.py`
- `tools/interpretation_generator.py`
- `tools/trend_analyzer.py`
- `tools/simple_pdf.py`

Diese Ebene verarbeitet Exportartefakte nachtraeglich weiter und formt die historisierte Report-Landschaft.

## Persistenz- und Artefaktstruktur

| Typ | Pfad/Familie | Beobachtung |
| --- | --- | --- |
| Runtime-Manifest | `data/runtime/*.json` | Clients, Sessions, Artefakte, Audit |
| Harmonisierungsjobs | `data/harmonization_jobs/*.json` | persistente Background-Jobs |
| Event-Logs | `data/harmonization_jobs/events/*.jsonl` | Realtime-/Worker-Ereignisse |
| Report-Archive | `C:/Benutzer_Archive_Start`, `C:/Benutzer_*_Start` | produktive Exportziele ausserhalb des Repo-Roots |
| lokale Web-Joblogs | `codex_tmp/web-jobs` oder `<runtime>/web_jobs` | Statusquellen fuer Scan-Polling |
| Datenbanken | `data/*.db` | lokal eingebettet |
| last client state | `last_client.json` | tracked, PII-nah |

## Wichtige Strukturbrueche

### README-Architektur stimmt nicht mit der Ist-Struktur ueberein

`README.md:11-20` beschreibt ein `infra/`-basiertes Layout, das im aktuellen Projekt nicht die reale operative Mitte ist.
Das Repo lebt praktisch aus `apps/`, `core/`, `services/`, `providers/`, `tools/`, `data/`.

### Zwei Web-Apps existieren parallel

- aktuelle App: `apps/web/main.py`
- Legacy-App: `web_app.py`

Die Legacy-App ist zwar als deprecated markiert, existiert aber weiterhin mit eigenem Routing, eigenen Fortschrittsparsern und eigener CORS-Konfiguration.

### Zwei UI-Linien existieren parallel

- neue Web-Shell: `apps/web/static/*`
- aeltere UI-Ablage: `web_ui/*`
- separate Workflow-Doku: `apps/cli/workflow/workflow_stepping.html`

### Code und Runtime-Artefakte sind vermischt

Im Repo-Baum liegen Quellcode, Laufzeitdaten, Backups, Logs, tmp-Dateien, Viewer-Artefakte und personennahes Testmaterial nebeneinander.
Das erschwert Reproduzierbarkeit, Hygiene und Security Review.

## Architekturelle Staerken

1. Die funktionale Abdeckung ist real und breit: CLI, Web, Reporting, Privacy, Hardware, Realtime, Tests.
2. Die aktuelle Web-App ist modularer als die Legacy-App; Router sind sauberer getrennt.
3. Der Runtime-Health- und Source-Registry-Check ist praktisch brauchbar.
4. Die Compliance-Komponenten sind nicht nur Dokumentation, sondern echter Code mit Tests.

## Architekturelle Schwaechen

1. Produktionslogik ist zu stark in grossen CLI-Modulen konzentriert.
2. Mehrere Schichten importieren ueber ihre Grenzen hinweg.
   - Beispiel: Workflow- und Toolcode greifen auf CLI-Helfer zu.
3. Web, CLI und Report-Tools teilen sich keine einzige kanonische Workflow- oder Event-Sprache.
4. Packaging und Imports sind nicht deckungsgleich.

## Konkrete Altlasten mit Entwicklerwirkung

| Befund | Evidenz |
| --- | --- |
| Backups werden neben Source-Dateien erzeugt | `cli/utils/backup.py:10-35` |
| `scan.py.bak_*`-Dateien liegen real im Tree | gezaehlt: `17` |
| Runtime-Temp-Dateien akkumulieren | `data/runtime`, gezaehlt: `120` |
| `last_client.json` und clientnahe Artefakte sind tracked | Repo-Root |
| Health-Konfiguration ist Windows-zentriert | `monitoring/health.py:5-37`, `config.yaml` |

## Entwicklerische Schlussfolgerung

Die Codebasis ist nicht primaer an einem Mangel an Funktionen krank, sondern an fehlender Konsolidierung.
Die strategische Hauptaufgabe lautet daher nicht "mehr Features", sondern "einen einzigen belastbaren Betriebs- und Datenpfad pro Fachfunktion herstellen".
