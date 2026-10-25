# Feedback f / Option B - Live Runtime Acceptance API/ASGI

Stand: 2026-07-18
Arbeitsort: `C:\morphic_v1\.worktrees\operator-workbench-phase1`
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`

## 1. Status

**Option B API/ASGI-Transport-Gate ist technisch geschlossen.**

Hinweis: Der nachgelagerte Browser-Smoke ist inzwischen in
`docs/status/2026-07-18-feedback-f-option-b-browser-smoke.md` ebenfalls
technisch geschlossen.

Der Admin-Catalog-Lifecycle wird jetzt ueber echte geschuetzte Web/API-Grenzen
bis zur expliziten Runtime-Auswahl nachgewiesen. Der neue Admin-Endpunkt
`GET /api/admin/catalog/runtime` liest das konfigurierte Runtime-Read-Model,
bleibt admin-geschuetzt, mutiert nichts und respektiert den F8.3-Kill-Switch
`MORPHIC_ADMIN_CATALOG_ENABLED`.

Dies ist weiterhin kein Produktiv-GO. Der ehemals nachgelagerte Browser-Smoke
ist inzwischen in
`docs/status/2026-07-18-feedback-f-option-b-browser-smoke.md` technisch
geschlossen; dieses Dokument bleibt der Gate-Record fuer den API/ASGI-Transport.

## 2. Umgesetzter Scope

| Artefakt | Status | Befund |
|---|---|---|
| `apps/web/admin_catalog.py` | erweitert | `GET /api/admin/catalog/runtime` als geschuetztes Runtime-Read-Model ueber bestehenden Admin-Catalog-Router |
| `tests/test_web_admin_catalog_runtime_acceptance.py` | neu | ASGI-Transport-Acceptance mit Bootstrap-Exchange, Draft, Validate, Diff, Publish, Activate, Reload, zweite Aktivierung, Rollback, Kontextisolation, Kill-Switch und Redaction |
| `docs/superpowers/specs/2026-07-18-feedback-f-option-b-live-runtime-acceptance-design.md` | neu | Option-B-Design fuer API/ASGI-Transport zuerst, Browser-Smoke danach |
| `docs/superpowers/plans/2026-07-18-feedback-f-option-b-live-runtime-acceptance.md` | neu/aktualisiert | TDD-/Verifikationsplan mit erledigten Task-1/2-Schritten |
| `docs/status/2026-07-18-feedback-f-option-b-live-runtime-acceptance.md` | neu | Gate-Record fuer Option B API/ASGI |
| `docs/2026-07-17-aktueller-umsetzungsplan-fortschritt.md` | aktualisiert | Rollup auf Option B API/ASGI und Browser-Smoke technisch geschlossen |
| `docs/status/2026-07-17-umsetzungsplan-status-tiefenanalyse.md` | aktualisiert | Tiefenanalyse auf Option-B-API/ASGI- und Browser-Smoke-Fortschritt gehoben |

## 3. Geschlossene Option-B-API/ASGI-Vertraege

| Vertrag | Status | Nachweis |
|---|---|---|
| Runtime-Read ist admin-geschuetzt | geschlossen | fehlende Admin-Security liefert HTTP 503 |
| Bootstrap laeuft ueber geschuetzten Webtransport | geschlossen | Test nutzt `/api/admin/bootstrap/exchange` |
| Draft -> Validate -> Diff -> Publish -> Activate laeuft ueber Admin-HTTP | geschlossen | Test nutzt nur `/api/admin/catalog/*`-Requests |
| App-/Store-Reload sieht aktive Revision | geschlossen | neue `create_app()`-Instanz liest `revision-a` |
| Aktivierte Revision 2 aendert Runtime sichtbar | geschlossen | Gruppenwechsel `["group-a"]` -> `["group-b"]` |
| Runtime zeigt Profile/Remedies/Pathogens/Relations/Multiplexes | geschlossen | `profile_ids`, `remedy_ids`, `pathogen_ids`, `relation_ids`, `multiplex_ids` belegt |
| Rollback stellt Revision 1 wieder her | geschlossen | Aktivierungszaehler `3`, Runtime wieder `revision-a` |
| Fremder Kontext scheitert fail-closed | geschlossen | HTTP 409 mit `active_revision_missing` |
| Deaktivierter Kill-Switch bleibt Legacy | geschlossen | `selected_source == "legacy"`, keine Catalog-IDs |
| Ungueltiger Kill-Switch ist Konfigurationsfehler | geschlossen | HTTP 422 mit `invalid_catalog_enabled_value` |
| Runtime-Response ist redigiert | geschlossen | `redacted is True`, keine Token-/Nonce-/PII-Fragmente |

## 4. Implementierungsentscheidung

Der neue Endpunkt lebt in `apps/web/admin_catalog.py`, nicht in einem separaten
Router. Damit nutzt er dieselbe Adminauth, dieselbe Contextableitung und
dieselbe Service-Factory wie die bereits abgenommenen Admin-Catalog-Mutationen.

Die Response gibt bei aktiviertem Catalog nur strukturierte Runtime-IDs zurueck:
Profile, Gruppen, Remedies, Pathogens, Relations und Multiplexes. Bei
deaktiviertem Kill-Switch werden keine Catalog-IDs ausgegeben. Runtimefehler
werden nicht auf Legacy zurueckgebogen, sondern als HTTP 409 beziehungsweise
HTTP 422 sichtbar.

## 5. Verifikation

| Pruefung | Ergebnis |
|---|---:|
| RED Runtime-Endpunkt | `1 failed`; `/api/admin/catalog/runtime` lieferte erwartungsgemaess HTTP 404 |
| GREEN Runtime-Endpunkt | `1 passed in 0.80s` |
| RED Redaction-Evidence | `2 failed, 2 passed`; fehlend war `redacted` in der Runtime-Response |
| Boundary-/Redaction-GREEN | `4 passed in 1.06s` |
| Fokussierte Option-B-/Admin-/Runtime-/Shadow-Regression | `39 passed in 4.76s` |
| `py_compile` fuer Admin-Catalog-Router und Option-B-Test | Exitcode 0 |
| `git diff --check` | Exitcode 0; nur bekannte LF/CRLF-Warnungen in bereits dirty tracked Dateien |
| Konfliktmarker-Scan fuer Option-B-Dateien | keine Treffer |
| Trailing-Whitespace-Scan `[ \t]+$` fuer Option-B-Dateien | keine Treffer |

Hinweis zur Testumgebung: Die Pytest-Laeufe wurden mit `PYTHONUTF8=1`,
`OPENBLAS_NUM_THREADS=1`, `TMP`/`TEMP` im Worktree, `-p no:cacheprovider` und
explizitem `--basetemp` unter `codex_tmp` ausgefuehrt, weil die Sandbox keine
Schreibrechte unter `C:\Users\Hubert111\AppData\Local\Temp` und `.pytest_cache`
bereitstellt.

## 6. Fortschritt nach Option B API/ASGI und Browser-Smoke-Nachtrag

| Modell | Stand |
|---|---:|
| F8.4 Option A | **100 % technisch geschlossen** |
| Option B API/ASGI-Transport | **100 % technisch geschlossen** |
| Option B Browser-Smoke | **100 % technisch geschlossen** |
| Produktivfreigabe | **nicht erteilt** |

## 7. Offener Zielschritt

| Reihenfolge | Gate | Status | Exakter naechster Inhalt |
|---:|---|---|---|
| 1 | Abschlussentscheidung | offen | Review/Commit, lokales Behalten oder naechsten Nutzerfeedbackpunkt ausdruecklich waehlen |

## 8. Harte Schranken

- Kein produktiver Catalog-Default.
- Deaktivierter Kill-Switch bleibt Legacy.
- Aktivierter Kill-Switch verlangt eine gueltige aktive Catalog-Revision.
- Bei aktiviertem Catalog gibt es keinen stillen Legacy-Fallback.
- Keine produktive Registry-, Remedy-DB- oder Source-Mutation durch Option B API/ASGI.
- Kein Commit, Staging, Push, Reset oder Cleanup ohne explizite Nutzerfreigabe.

## 9. Naechster verbindlicher Block

**Abschlussentscheidung fuer den uncommitted Worktree.**

Der fachliche Transportvertrag ist durch API/ASGI geschlossen, und der
Browser-Smoke ist im nachgelagerten Gate-Record ebenfalls technisch geschlossen.
Exakt weiter geht es mit der Integrationsentscheidung oder mit dem separaten
Nutzerfeedbackpunkt a.
