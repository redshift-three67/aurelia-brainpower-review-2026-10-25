# Systemarchitektur Und Entry-Points

## 1. Reale Projektstruktur

Zentrale Verzeichnisse:

- `apps/`
- `core/`
- `providers/`
- `services/`
- `tools/`
- `data/`
- `tests/`

Wichtige Neben- und Legacy-Bereiche:

- `PROJECT_MEMORY/`
- `docs/`
- `web_ui/`
- `web_app.py`
- `analysis_reports/`
- `logs/`
- `codex_tmp/`

## 2. Zentrale Entry-Points

### CLI

- Root-CLI: `python -m apps.cli.main`
- Hauptmodul: `apps/cli/main.py`

Wichtige Kommandofamilien:

- `scan top3-scan`
- `field multiplex-scan`
- `field workflow-scan`
- `sources`
- `trend`
- `privacy`
- `harmonize`
- `health`

### Web

- offizieller FastAPI-Entry-Point: `apps.web.main:app`
- Bootstrap: `web_server.py`
- Weblauncher: `Run-WebUI.ps1`

Wichtige Web-Routen:

- `/` -> aktuelle Web-Shell
- `/workflow-stepping` -> erklaerende 12-Step-Oberflaeche
- `/api/health`
- `/api/sources`
- `/api/privacy/clients`
- `/api/reports`
- `/api/scan/preview`
- `/api/scan/jobs`
- `/api/scan/jobs/{job_id}`
- `/api/scan/jobs/{job_id}/results`
- `/api/harmonization/jobs`

### Worktree-spezifische neue API-Flaechen

Bereits im aktiven Worktree angelegt:

- `/api/workbench/registry`
- `/api/workbench/hardware`
- `/api/workbench/draft`
- `/api/workbench/templates`
- `/api/workbench/run-trace/{run_id}`

## 3. Architekturelle Realitaet

### Produktivpfad

Der derzeit produktivste Pfad ist weiterhin der Top-N-CLI-Scan ueber:

- `apps/cli/commands/scan.py`
- `apps/cli/commands/field.py`

Die aktuelle Web-Shell baut darauf auf.

### 12-Step-Pfad

Parallel dazu existiert weiterhin ein eigener 12-Step-Orchestrator:

- `apps/cli/workflow/orchestrator.py`
- `apps/web/analyze.py`

Dieser ist technisch real, aber nicht identisch mit dem produktiven Web-Hauptpfad.

### Ergebnis

Die Architektur hat noch keinen einzigen kanonischen Workflow ueber alle Ebenen hinweg, sondern mehrere parallel lebende Modelle.

## 4. Persistenz- und Laufzeitmodelle

### Datenbanken

Unter `data/`:

- `descriptions.db`
- `item_descriptions.db`
- `remedies.db`
- `resonance.db`

### Runtime-Manifest

Unter `data/runtime/`:

- Clients
- Sessions
- Artifacts
- Audit-Log

Zentrales Modul:

- `core/compliance/runtime_manifest.py`

### Harmonisierung

Unter `data/harmonization_jobs/`:

- JSON-Jobdateien
- Event-Logs (`events/*.jsonl`)

Zentrales Modul:

- `services/harmonization_worker.py`

### Web-Joblogs

- Standardmaessig `codex_tmp/web-jobs`
- alternativ runtime-gebundene Ablage

## 5. Entwicklerisch wichtigste Strukturpunkte

1. `apps/web/main.py` ist der aktuelle kanonische Web-Hub.
2. `apps/cli/main.py` ist duenn, aber `scan.py` und `field.py` bleiben gross und fachlich schwergewichtig.
3. `core/compliance/runtime_manifest.py` ist bereits eine reale zentrale Metadatenachse.
4. Der aktive Worktree fuehrt eine neue `workbench_*`-Schicht im Web ein, die langfristig die neue kanonische Operatoroberflaeche tragen soll.
