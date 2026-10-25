# Feedback f Option B Live Runtime Acceptance Design

## Status

Stand: 2026-07-18
Arbeitsort: `C:\morphic_v1\.worktrees\operator-workbench-phase1`
Branch: `operator-workbench-phase1`

Diese Spec setzt die vom Nutzer bestaetigte Fortsetzung nach F8.4 Option A um:
zuerst ein stabiles API/ASGI-Transport-Gate, danach bei Bedarf ein echter
Browser-Smoke. Sie nimmt keine produktive Catalog-Freigabe vor.

## Ziel

Option B soll beweisen, dass der fachliche F8.4-Lifecycle nicht nur direkt ueber
Service-/Store-Objekte funktioniert, sondern ueber den geschuetzten Webtransport
bis zur expliziten Runtime-Auswahl sichtbar wird. Der Nachweis umfasst
Bootstrap-Adminauth, Draft, Validate, Diff, Publish, Activate, App-/Store-Reload,
Runtime-Read, zweite Aktivierung, Rollback, Kontextisolation, Kill-Switch-Grenze
und redigierte Evidence.

## Scope

Der erste Option-B-Schritt nutzt ASGI-Requests gegen `create_app()` und einen
testlokalen SQLite-Catalog unter `tmp_path`. Damit laufen echte FastAPI-Router,
Admin-Security-Pruefungen, Pydantic-Validation und Catalog-Service-Factories,
ohne einen externen Browser oder Produktivdaten zu benoetigen.

Neu ergaenzt wird ein geschuetzter Runtime-Read-Endpunkt:

`GET /api/admin/catalog/runtime`

Der Endpunkt gibt die vom Runtime-Adapter ausgewaehlte Quelle und, bei
aktiviertem Catalog, die ausgewerteten Runtime-IDs der aktiven Revision zurueck.
Er mutiert nichts und nutzt denselben `MORPHIC_ADMIN_CATALOG_ENABLED`-Kill-Switch
wie F8.3.

## Architektur

`apps/web/admin_catalog.py` bleibt die Web-Fassade fuer den Admin Catalog. Der
neue Runtime-Endpunkt haengt dort am bestehenden Router und nutzt
`_service_and_context(request)`, damit er dieselbe Adminauth, denselben
Context-Resolver und dieselbe Service-Factory wie Status, Entries, Draft,
Publish, Activate und Rollback verwendet.

Der Endpunkt ruft `load_configured_runtime(service.store, context)` aus
`core.admin_catalog.runtime_adapter` auf. Bei deaktiviertem Kill-Switch antwortet
er mit `selected_source="legacy"` und ohne Catalog-IDs. Bei aktiviertem
Kill-Switch antwortet er mit `selected_source="catalog"`, `active_revision_id`
und sortierten IDs fuer Profile, Groups, Remedies, Pathogens, Relations und
Multiplexes. Runtime-Fehler bleiben fail-closed: keine aktive Revision ergibt
HTTP 409 mit stabilem Fehlercode, ungueltige Kill-Switch-Werte HTTP 422.

Der Acceptance-Test erzeugt zwei synthetische Revisionen ueber echte Admin-API-
Requests. Nach jeder Aktivierung wird eine neue `create_app()`-Instanz mit
derselben testlokalen Catalog-DB gestartet, um App-/Store-Reload abzubilden.
Der Runtime-Nachweis erfolgt ausschliesslich ueber
`GET /api/admin/catalog/runtime`.

## Contracts

- Runtime-Read ist admin-geschuetzt und fail-closed, wenn Admin-Security fehlt.
- Deaktivierter Kill-Switch liefert Legacy und liest keine Catalog-IDs aus.
- Ungueltiger Kill-Switch-Wert liefert einen strukturierten 422-Fehler.
- Aktivierter Kill-Switch verlangt eine aktive Revision; sonst HTTP 409.
- Draft -> Validate -> Diff -> Publish -> Activate laeuft ueber Admin-HTTP-
  Requests.
- App-/Store-Reload sieht dieselbe aktive Revision.
- Revision 2 aendert die Runtime-IDs sichtbar.
- Rollback stellt Revision 1 wieder her.
- Fremder Catalog-Kontext kann die aktive Revision nicht sehen und scheitert
  fail-closed.
- Response-Evidence enthaelt keine Tokens, Nonces, Patientendaten oder Roh-PII.

## Nichtziele

- Kein produktiver Catalog-Default.
- Keine produktive Registry- oder Remedy-DB-Mutation.
- Keine Source-Aktivierung und kein Online-Fetch.
- Kein echter Browserlauf in diesem ersten Option-B-Schritt.
- Kein Commit, Staging, Push, Reset oder Cleanup ohne explizite Nutzerfreigabe.

## Verifikation

Minimaler Abschluss fuer diesen Option-B-Schritt:

```powershell
$env:PYTHONUTF8="1"
$env:OPENBLAS_NUM_THREADS="1"
$env:TMP=(Resolve-Path -LiteralPath 'codex_tmp').Path
$env:TEMP=(Resolve-Path -LiteralPath 'codex_tmp').Path
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests\test_web_admin_catalog_runtime_acceptance.py -q -p no:cacheprovider --basetemp codex_tmp\pytest-option-b-green
& C:\morphic_v1\.venv\Scripts\python.exe -m py_compile apps\web\admin_catalog.py tests\test_web_admin_catalog_runtime_acceptance.py
git diff --check
```

Erweiterte Regression:

```powershell
$env:PYTHONUTF8="1"
$env:OPENBLAS_NUM_THREADS="1"
$env:TMP=(Resolve-Path -LiteralPath 'codex_tmp').Path
$env:TEMP=(Resolve-Path -LiteralPath 'codex_tmp').Path
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests\test_web_admin_catalog_runtime_acceptance.py tests\test_web_admin_catalog.py tests\test_admin_catalog_runtime_acceptance.py tests\test_admin_catalog_runtime_consumption.py tests\test_admin_catalog_shadow_comparison.py -q -p no:cacheprovider --basetemp codex_tmp\pytest-option-b-final
```
