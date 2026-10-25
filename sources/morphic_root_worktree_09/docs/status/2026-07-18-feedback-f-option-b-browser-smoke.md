# Feedback f / Option B - Browser Smoke

Stand: 2026-07-18
Arbeitsort: `C:\morphic_v1\.worktrees\operator-workbench-phase1`
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`

## 1. Status

**Option B Browser-Smoke ist technisch geschlossen.**

Die geschuetzte Admin-UI zeigt jetzt die explizite Runtime-Auswahl an und kann
sie ueber `GET /api/admin/catalog/runtime` aus dem Browser ausloesen. Der
Browser-Smoke hat den kompletten UI-Pfad mit Bootstrap-Nonce im Fragment,
Draft, Validate, Diff, Publish, Activate, Runtime-Pruefung, zweiter Aktivierung,
Rollback und finaler Runtime-Pruefung gegen einen isolierten lokalen Testserver
erfolgreich ausgefuehrt.

Dies ist weiterhin kein Produktiv-GO: Der Smoke nutzt eine testlokale SQLite-DB
unter `codex_tmp`, einen testlokalen Admin-Nonce und einen temporaren Server.
Der produktive Default bleibt unveraendert.

## 2. Umgesetzter Scope

| Artefakt | Status | Befund |
|---|---|---|
| `apps/web/static/admin.html` | erweitert | Runtime-Metriken und Runtime-Smoke-Sektion mit Button `admin-load-runtime` |
| `apps/web/static/admin-catalog.js` | erweitert | `RUNTIME_ENDPOINT`, `loadRuntime()` und redigierte Runtime-Anzeige ohne Token-Persistenz |
| `apps/web/admin_security.py` | erweitert | Same-Origin-Requests ohne `Origin`-Header werden aus Scheme und Host abgeleitet, Token- und Hostbindung bleiben bestehen |
| `tests/test_admin_catalog_dom.py` | erweitert | DOM-/JS-Contract fuer Runtime-Smoke-UI und Endpoint-Anker |
| `tests/test_web_admin_security.py` | erweitert | Same-Origin-GET ohne `Origin` mit gueltigem Admin-Token testbelegt |
| `tests/test_admin_catalog_runtime_adapter.py` | aktualisiert | Consumer-Guard erlaubt nur Option-A-Acceptance-Harness, geschuetzten Admin-Runtime-Endpunkt und Option-B-Acceptance-Test |
| `codex_tmp/option_b_browser_smoke_server.py` | temporaer | Isolierter Smoke-Server mit testlokalem Catalog-Store und festem Test-Nonce |
| `codex_tmp/option_b_browser_smoke.js` | temporaer | Headless-Playwright-Smoke gegen `admin.html` |
| `docs/status/2026-07-18-feedback-f-option-b-browser-smoke.md` | neu | Gate-Record fuer Option B Browser-Smoke |
| Rollups | aktualisiert | Feedback f / Option B Browser-Smoke technisch geschlossen; Produktivfreigabe nicht erteilt |

## 3. Geschlossene Browser-Smoke-Vertraege

| Vertrag | Status | Nachweis |
|---|---|---|
| Admin-UI besitzt sichtbare Runtime-Metriken | geschlossen | `admin-runtime-source`, `admin-runtime-revision`, `admin-runtime-redacted` |
| Admin-UI besitzt Runtime-Smoke-Sektion | geschlossen | `admin-runtime-section`, `admin-load-runtime`, `admin-runtime` |
| JS nutzt den geschuetzten Runtime-Endpoint | geschlossen | `RUNTIME_ENDPOINT = "/api/admin/catalog/runtime"` |
| Admin-Token bleibt fluechtig | geschlossen | keine `localStorage`, `sessionStorage`, `document.cookie`, `innerHTML` |
| Same-Origin-GET ohne `Origin` ist browserkompatibel | geschlossen | Security-Test akzeptiert Host/Scheme-Ableitung mit gueltigem Token |
| Browser-Bootstrap nutzt Fragment-Nonce | geschlossen | Playwright oeffnet `admin.html#admin_nonce=...` |
| Browser-UI erstellt, validiert und publiziert Revision A | geschlossen | Operation-Result und Diff im Browser sichtbar |
| Browser-UI aktiviert Revision A und liest Catalog-Runtime | geschlossen | Runtime-Quelle `catalog`, Gruppen `group-a` |
| Browser-UI aktiviert Revision B und liest geaenderte Runtime | geschlossen | Runtime-Revision `browser-revision-b`, Gruppen `group-b` |
| Browser-UI rollt auf Revision A zurueck | geschlossen | finale Runtime-Revision `browser-revision-a`, Gruppen `group-a` |
| Runtime-Ausgabe bleibt redigiert | geschlossen | `redacted`, keine Token-/Nonce-/PII-Fragmente |
| Browser-Konsole bleibt sauber | geschlossen | `consoleMessages: []` |

## 4. Verifikation

| Pruefung | Ergebnis |
|---|---:|
| UI RED | `2 failed, 2 passed`; fehlend waren Runtime-Endpoint-Anker und Runtime-UI-IDs |
| UI GREEN | `4 passed in 0.57s` |
| Same-Origin-Origin-RED | `1 failed`; fehlender `Origin` ergab HTTP 403 |
| Admin-Security-GREEN | `9 passed in 0.61s` |
| Browser-Prereq-Matrix | `52 passed in 5.29s` |
| Headless-Playwright-Browser-Smoke | `passed`; Quelle `catalog`, finale Revision `browser-revision-a`, Evidence `redigiert`, `consoleMessages: []` |
| Finaler Headless-Playwright-Browser-Smoke | `passed`; Quelle `catalog`, finale Revision `browser-revision-a`, Evidence `redigiert`, `consoleMessages: []` |
| Adapter-/Pfad-Nachpruefung mit externem Basetemp | `37 passed, 1 skipped in 2.04s` |
| Finale Vollsuite mit externem Basetemp | `1161 passed, 8 skipped in 160.96s` |

Screenshot-Evidence:

`C:\morphic_v1\.worktrees\operator-workbench-phase1\codex_tmp\option-b-browser-smoke\admin-runtime-smoke.png`

Hinweis zur Testumgebung: Der Browser-Smoke lief gegen einen temporaren
`uvicorn`-Server auf `127.0.0.1:8765`, gestartet aus
`codex_tmp/option_b_browser_smoke_server.py` und im selben PowerShell-Lauf per
`finally` beendet. Der Playwright-Lauf nutzte vorhandene lokale Node-Module aus
`C:\Users\Hubert111\.agents\skills\playwright\node_modules`, ohne Netzwerk- oder
Installationsschritt.

## 5. Fortschritt nach Option B Browser-Smoke

| Modell | Stand |
|---|---:|
| F8.4 Option A | **100 % technisch geschlossen** |
| Option B API/ASGI-Transport | **100 % technisch geschlossen** |
| Option B Browser-Smoke | **100 % technisch geschlossen** |
| Produktivfreigabe | **nicht erteilt** |

## 6. Harte Schranken

- Kein produktiver Catalog-Default.
- Deaktivierter Kill-Switch bleibt Legacy.
- Aktivierter Kill-Switch verlangt eine gueltige aktive Catalog-Revision.
- Bei aktiviertem Catalog gibt es keinen stillen Legacy-Fallback.
- Keine produktive Registry-, Remedy-DB- oder Source-Mutation durch Option B.
- Kein Commit, Staging, Push, Reset oder Cleanup ohne explizite Nutzerfreigabe.

## 7. Naechster verbindlicher Schritt

**Abschlussentscheidung fuer den uncommitted Worktree.**

Technisch ist Feedback f fuer Option A und Option B geschlossen. Offen bleiben
die organisatorischen Schritte: Code-Review/Commit-Freigabe, Umgang mit den
grossen untracked Worktree-Artefakten und danach gegebenenfalls der separate
Nutzerfeedbackpunkt a zum einheitlichen Reportdesign.
