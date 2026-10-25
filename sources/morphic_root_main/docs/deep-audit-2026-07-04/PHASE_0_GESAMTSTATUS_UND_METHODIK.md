# Phase 0 - Gesamtstatus Und Methodik

## Ziel dieses Abschnitts

Diese Phase dokumentiert den belastbaren Projekt-Snapshot, die verwendete Methodik und die wichtigsten Abweichungen zwischen Projekt-Selbstdarstellung und tatsaechlicher Repository-Realitaet.

## Untersuchungsbasis

Direkt gelesen oder validiert wurden unter anderem:

- `README.md`
- `CLAUDE.md`
- `PROJECT_MEMORY/00_CURRENT_STATE.md`
- `pyproject.toml`
- `requirements.txt`
- `apps/web/*.py`
- `apps/web/static/*`
- `apps/cli/main.py`
- `apps/cli/commands/*.py`
- `apps/cli/workflow/*`
- `core/compliance/runtime_manifest.py`
- `services/harmonization_worker.py`
- `tests/*.py`

Zusaetzlich lokal verifiziert:

- `apps.cli.main health --strict`
- `apps.cli.main sources validate`
- `pytest tests`

## Aktueller Snapshot

### Repo-Realitaet

- Git-Repository: ja
- Branch: `master`
- Letzte sichtbare Commits:
  - `e87cee3 docs: plan radi144 workflow ux implementation`
  - `68c71c0 docs: expand radi144 workflow ux scope`
  - `d89957f docs: design radi144 workflow ux alignment`
  - `e944280 docs: design workflow stepper phase 2`
- Worktree ist nicht sauber:
  - modifiziert: `apps/web/static/app.css`
  - modifiziert: `apps/web/static/app.js`
  - modifiziert: `apps/web/static/index.html`
  - modifiziert: `tests/test_web_shell.py`
  - untracked: `docs/superpowers/plans/2026-07-04-apps-web-workflow-stepper-phase2.md`

### Laufzeitstatus

- Python: `3.12.10`
- `apps.cli.main health --strict`: `OK`
- `apps.cli.main sources validate`: `18` Quellen, Registry gueltig
- `pytest tests` zeigte in dieser Analyse-Session zwei unterschiedliche frische Resultate:
  - zuerst `202 passed in 144.84s`
  - spaeter `21 failed, 181 passed in 27.86s`
  - dominantes Fehlermuster: `OpenBLAS error: Memory allocation still failed after 10 retries, giving up.`

### Gezogene Zaehlsignale

- Testdateien unter `tests/`: `56`
- Exploratory-Testdateien unter `tests/exploratory/`: `10`
- gefundene `def test_...` in `tests/`: `208`
- Markdown-Dateien unter `docs/`: `61`
- `@log_command`-Verwendungen: `23`
- `scan.py.bak_*` in `apps/cli/commands/`: `17`
- `*.tmp.*` unter `data/runtime/`: `120`

## Projekt-Selbstdarstellung vs. Ist-Zustand

### Dokumentationsdrift

| Quelle | Behauptung | Ist-Zustand |
| --- | --- | --- |
| `README.md:23-28` | Repository sei noch "scaffolding in progress" | Das Repo enthaelt reale CLI-, Web-, Reporting-, Compliance- und Testpfade |
| `CLAUDE.md:4-17` | `153/153 Tests gruen`, `main.py` 72 Zeilen | Tatsaechlich `202` gruene Tests; `apps/cli/main.py` ist groesser als 72 Zeilen |
| `PROJECT_MEMORY/00_CURRENT_STATE.md:6-16` | "Repository bereinigt" und `153 passed` | Der Worktree ist aktuell dirty; die Testsuite ist groesser |
| `PROJECT_MEMORY/00_CURRENT_STATE.md:86-90` | `pyserial` sei entfernt/ungenutzt | Serial-Hardware wird real importiert, z.B. in `providers/hardware/entropy_sources.py` |

### Fazit zur Dokumentationslage

Die Memory- und Meta-Dokumente sind als historischer Kontext nuetzlich, aber nicht mehr als verlaesslicher Single Source of Truth geeignet.
Fuer Entwicklungsentscheidungen muss der aktuelle Code als primaere Wahrheit betrachtet werden.

## Methodische Bewertung

### Was als belastbar gilt

- Direkte Imports, Routen, Pydantic-Modelle, Datei- und Prozesspfade
- lokale Test- und Health-Outputs
- konkrete Persistenzpfade und Dateiformate
- Routing-, Header-, CORS- und Exportlogik

### Was als abgeleitet gilt

- reale UX-Qualitaet ohne Browser-Messung
- Multitenant-Faehigkeit aus vorhandenen Identifikatoren und fehlenden Ownership-Checks
- DSGVO-Reife aus technischen Kontrollpunkten

### Was bewusst nicht behauptet wird

- keine rechtliche Vollkonformitaet
- keine produktive Last- oder Sicherheitsfreigabe
- keine CWV-Zielerreichung ohne Field-Daten

## Gesamtbewertung in einem Satz

`C:/morphic_V1` ist kein leeres oder unfertiges Scaffold, sondern ein funktionsreiches, lokal lauffaehiges System mit guter Testbasis, aber mit deutlicher Architekturdrift, Sicherheitsluecken, Privacy-Widerspruechen, Packaging-Unordnung und mehreren parallel lebenden Workflow-Modellen.

## Zusatzbefund zur Reproduzierbarkeit

Die Testbasis ist stark, aber der frische Re-Run zeigt, dass die lokale Reproduzierbarkeit aktuell nicht voll monoton stabil ist.
Das beobachtete OpenBLAS-Speicherfehlermuster betrifft vor allem subprocess-lastige CLI-/Report-Pfade und ist selbst schon ein relevanter Reifegradbefund.

## P0-Querschnittsrisiken

1. Kein echtes Auth-/Mandantenmodell bei gleichzeitigem Umgang mit klientenbezogenen Daten.
2. Historisierte Report- und Archivstruktur exponiert Klartext-Slugs.
3. Optionaler API-Key plus offene CORS-Defaults in der aktuellen Web-App.
4. Drei konkurrierende Workflow-Erzaehlungen mit unterschiedlichen Datenfluesen.
5. Meta-Dokumentation und Packaging-Konfiguration spiegeln den Ist-Zustand nicht mehr korrekt.

## Was fuer Folgephasen wichtig ist

- Architekturfragen muessen immer zwischen produktivem Top-N-CLI-Pfad und 12-Step-Workflow unterscheiden.
- Privacy-/Security-Befunde muessen die Report-Katalog-Realitaet und das Runtime-Manifest gemeinsam betrachten.
- UI/UX-Bewertungen duerfen nicht nur `apps/web/static/*`, sondern auch `/workflow-stepping` und das alte `web_ui/` beruecksichtigen.
