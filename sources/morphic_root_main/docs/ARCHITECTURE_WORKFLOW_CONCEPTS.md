# Architektur: Workflow-Konzepte

## Überblick

Morphic Engine V1 verwendet **zwei parallele Workflow-Konzepte**, die sich
ergänzen aber unterschiedliche Einsatzbereiche haben.

---

## 1. CLI Commands (`apps/cli/commands/`)

**Einsatzbereich:** Interaktive CLI-Nutzung, Einzelfunktionen, Production-Scans.

Die CLI-Commands sind über Typer-Subapps organisiert und werden aufgerufen via:
```
python -m apps.cli.main <command> <subcommand> [args]
```

### Verfügbare Commands

| Command | Subcommands | Zweck |
|---------|-------------|-------|
| `scan` | `top3-scan`, `groups-overview`, `hw-diagnostics`, `analyze`, `batch-scan` | Scan- & Analyse-Befehle |
| `trend` | `analyze-trends`, `client-trends` | Trend- & Verlaufsanalyse |
| `harmonize` | (various) | Harmonisierung |
| `descriptions` | (various) | Beschreibungs-Datenbank |
| `synergy` | (various) | Quantum-Synergy |
| `field` | `field-test`, `multiplex-scan` | Feld-Tests & Multiplex |
| `sources` | (various) | Quellen-Repositories |
| `privacy` | (various) | DSGVO/Runtime-Manifeste |
| `health` | - | System-Gesundheit |

### Eigenschaften
- **Status:** Produktiv, voll getestet (153 Tests)
- **Architektur:** Modular, jede Funktion in eigenem Command-File
- **Entry-Point:** `apps/cli/main.py` (72 Zeilen, reine Delegation)

---

## 2. Workflow Orchestrator (`apps/cli/workflow/`)

**Einsatzbereich:** Automatisierte 12-Step-Pipeline, API-Aufrufe, Web-UI.

Der Orchestrator implementiert den **Radi144-Blueprint** als sequenzielle
12-Step-Pipeline. Jeder Step verarbeitet einen `WorkflowState` und reicht
ihn an den nächsten weiter.

### Die 12 Steps

| Step | Modul | Zweck |
|------|-------|-------|
| 01 | `step01_init.py` | System-Initialisierung, Hardware-Erkennung |
| 02 | `step02_input.py` | Benutzer-Eingabe validieren |
| 03 | `step03_signature.py` | Klienten-Signatur (Frequenz) berechnen |
| 04 | `step04_focus.py` | Fokus-Vektorisierung & Bio-Knowledge |
| 05 | `step05_emf.py` | EMF-Kompensation (Sensing → Profiling → Compensate) |
| 06 | `step06_amplifier.py` | Amplifier-System (Heilsteine, Kristalle) |
| 07 | `step07_palette.py` | Farbpaletten-Generierung (6 Strategien) |
| 08 | `step08_matrix.py` | Matrix-Suche (Monte-Carlo im 10^144 Raum) |
| 09 | `step09_quantum.py` | Quantum-Synergy (Grover-Algorithmus) |
| 10 | `step10_post.py` | Post-Processing & Harmonisierung |
| 11 | `step11_export.py` | Export (PDF, HTML, JSON, Audio) |
| 12 | `step12_harmonize.py` | Harmonisierung (optional) |

### Aufruf
```python
from apps.cli.workflow.orchestrator import run_workflow

state = run_workflow(
    name="Mustermann",
    first_name="Klaus",
    birth_date="09041966",
    birth_place="Augsburg",
    focus="Bronchien",
    top_n=5,
)
```

### Eigenschaften
- **Status:** Funktional, aber nicht über CLI-Commands integriert
- **Architektur:** Pipeline-Pattern mit `WorkflowState` als Datenträger
- **Entry-Point:** `run_workflow()` in `orchestrator.py`
- **Web-UI:** Verfügbar via `POST /api/analyze` (apps/web/analyze.py)

---

## Wann was verwenden?

| Szenario | Empfohlen |
|----------|-----------|
| Einzelfunktion ausführen (z.B. nur Trend-Analyse) | CLI Commands |
| Vollständigen Scan mit allen Schritten | CLI `scan top3-scan` |
| Automatisierte Pipeline aus API/Web-UI | Workflow Orchestrator |
| Batch-Processing mehrerer Klienten | CLI `scan batch-scan` |
| Entwicklung/Debugging einzelner Steps | Workflow Orchestrator (mit verbose=True) |

---

## Beziehung zwischen beiden Konzepten

Die CLI-Commands nutzen **dieselben Core-Module** wie der Orchestrator:
- `core/nls/nls_db.py` - NLS-Datenbank
- `core/quantum_synergy/` - Quantum-Synergy
- `core/trend_analysis.py` - Trend-Analyse
- `tools/` - Report-Tools (synergy, remedy, trend, interpretation)
- `services/harmonization_worker.py` - Harmonisierung

Der Orchestrator ist eine ** thin Orchestration-Layer** über denselben
Core-Modulen, während die CLI-Commands direkteren Zugriff bieten.

---

**Zuletzt aktualisiert:** 2026-07-02
