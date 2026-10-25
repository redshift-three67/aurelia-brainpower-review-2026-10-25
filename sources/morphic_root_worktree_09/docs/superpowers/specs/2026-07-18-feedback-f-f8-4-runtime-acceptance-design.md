# Feedback f F8.4 Runtime Acceptance Design

## Status

Stand: 2026-07-18
Arbeitsort: `C:\morphic_v1\.worktrees\operator-workbench-phase1`
Branch: `operator-workbench-phase1`

Diese Spec setzt die vom Nutzer freigegebene Option A um und haelt die
Struktur fuer Option B offen.

## Ziel

F8.4 soll nachweisen, dass die Admin-Catalog-Umschaltung nicht nur aus
Einzelbausteinen besteht, sondern als zusammenhaengender, isolierter
Acceptance-Lauf funktioniert: Draft, Validierung, Diff, Publish, Aktivierung,
Runtime-Load, Reload/Neustartsimulation, Rollback, Kontextisolation,
Kill-Switch-Grenze und Auditkette.

## Scope

Option A verwendet ausschliesslich synthetische Daten in einem explizit
uebergebenen `tmp_path`-Catalog-Store. Es gibt keine produktive
Registry-Mutation, keine Remedy-DB-Mutation, keine Source-Aktivierung, keinen
Online-Fetch und keine Bereinigung bestehender Worktree-Artefakte.

Die Acceptance-Harness wird als kleines Python-Modul unter
`core/admin_catalog/runtime_acceptance.py` gebaut. Sie ruft die bereits
abgenommenen Admin-Service-, Store- und Runtime-Adapter-Grenzen auf und gibt
eine redigierte, testbare Evidence-Struktur zurueck.

## Architektur

Die Harness besitzt keine eigenen Schreibprimitive. Alle Schreiboperationen
laufen ueber `AdminCatalogService`; alle Runtime-Leseoperationen laufen ueber
`load_configured_runtime()` mit `MORPHIC_ADMIN_CATALOG_ENABLED=on`. Ein
simulierter Prozessneustart wird durch eine neue `CatalogStore`-Instanz auf
derselben SQLite-Datei abgebildet.

Die Funktion akzeptiert zwei vollstaendige synthetische Revisions-Payloads.
Revision 1 wird aktiviert und nach Reload geladen. Revision 2 wird danach
aktiviert, als geaenderte Runtime sichtbar und anschliessend per Rollback
wieder auf Revision 1 zurueckgestellt.

## Contracts

- Draft -> Validate -> Diff -> Publish -> Activate laeuft in der richtigen
  Reihenfolge.
- Runtime bei aktiviertem Catalog liest genau die aktive Revision.
- Eine neue Store-Instanz sieht dieselbe aktive Revision.
- Revision 2 aendert die Runtime sichtbar.
- Rollback stellt Revision 1 wieder her.
- Fremder Kontext sieht keine aktive Revision und scheitert fail-closed.
- Deaktivierter Kill-Switch liest keinen Catalog.
- Auditkette bleibt konsistent.
- Evidence enthaelt keine Tokens, Nonces, Patientendaten oder Roh-PII.

## Option-B-Vorbereitung

Option B kann spaeter dieselben synthetischen Payloads und dieselbe Evidence
verwenden, aber den Lifecycle ueber den laufenden FastAPI-Server und die
geschuetzte Admin-UI anstossen. Der Kern der fachlichen Abnahme bleibt damit
identisch; nur Transport und Browserinteraktion kommen hinzu.

## Nichtziele

- Kein produktiver Catalog-Default.
- Kein Commit, Staging oder Push.
- Keine echten Quellenimporte.
- Keine externe Netzwerkabnahme.
- Keine Veraenderung an `data/remedies.db`, `config/source_repositories.json`
  oder Radi144 auf `127.0.0.1:8090`.

## Verifikation

Minimaler Abschluss fuer Option A:

```powershell
$env:PYTHONUTF8="1"
$env:OPENBLAS_NUM_THREADS="1"
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests\test_admin_catalog_runtime_acceptance.py -q -p no:cacheprovider
& C:\morphic_v1\.venv\Scripts\python.exe -m py_compile core\admin_catalog\runtime_acceptance.py tests\test_admin_catalog_runtime_acceptance.py
git diff --check
```

Erweiterte Regression, falls Zeit/RAM stabil:

```powershell
$env:PYTHONUTF8="1"
$env:OPENBLAS_NUM_THREADS="1"
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests\test_admin_catalog_runtime_acceptance.py tests\test_admin_catalog_runtime_consumption.py tests\test_web_admin_catalog.py -q -p no:cacheprovider
```
