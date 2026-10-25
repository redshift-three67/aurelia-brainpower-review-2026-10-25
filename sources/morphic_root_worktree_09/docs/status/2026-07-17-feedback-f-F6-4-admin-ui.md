# Feedback f / F6.4 Admin-UI als getrennte Oberflaeche

Stand: 2026-07-17
Arbeitsort: `C:\morphic_v1\.worktrees\operator-workbench-phase1`
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`
Status: **F6.4 technisch geschlossen**

## 1. Kurzfazit

F6.4 ist technisch geschlossen. Es gibt jetzt eine getrennte lokale Admin-Oberflaeche fuer den Admin Catalog:

- `admin.html` ist nicht in die normale Operator Workbench integriert;
- der Bootstrap-Nonce wird nur aus dem URL-Fragment gelesen und danach per `history.replaceState` aus der Adresszeile entfernt;
- der Admin-Token bleibt nur im fluechtigen JS-Speicher und wird nicht in Browser-Storage, Cookies oder URLs persistiert;
- Status und aktive Entries werden ueber die geschuetzten F6.2-Endpunkte geladen;
- Draft, Validierung, Diff, Publish, Aktivierung und Rollback sind visuell getrennt;
- gefaehrliche Aktionen zeigen Scope, Revision, Diff-/Ergebnisflaeche und Auditgrund;
- `/static/admin.html` und `/static/admin-catalog.js` werden mit No-Store-Headern ausgeliefert.

F6.4 baut keinen Onlineadapter und keine Runtime-Catalogwirkung.

## 2. Geaenderter Scope

| Datei | Zweck |
|---|---|
| `apps/web/static/admin.html` | getrennte Admin-Catalog-Oberflaeche |
| `apps/web/static/admin-catalog.js` | Bootstrap-Nonce-Exchange, fluechtiger Token, Admin-Catalog-API-Client |
| `apps/web/static/app.css` | responsive Admin-Catalog-Styles |
| `apps/web/main.py` | No-Store fuer Admin-HTML und Admin-JS |
| `tests/test_admin_catalog_dom.py` | F6.4 DOM-/Security-Contract |
| `docs/status/2026-07-17-feedback-f-F6-4-admin-ui.md` | dieser Gate-Record |

## 3. TDD- und Verifikationsnachweis

| Schritt | Ergebnis |
|---|---|
| RED F6.4 | `4 failed`; `admin.html`/`admin-catalog.js` fehlten, `/static/admin.html` lieferte 404 |
| GREEN F6.4-Fokus | `4 passed in 0.42s` |
| Web/Admin-Regression | `40 passed in 2.04s` fuer `tests/test_admin_catalog_dom.py tests/test_web_admin_catalog.py tests/test_web_admin_security.py tests/test_workbench_sources_dom.py tests/test_web_shell.py tests/test_web_local_security_headers.py tests/test_web_local_security_headers_runtime.py` |
| `py_compile` | Exitcode 0 fuer `apps/web/main.py tests/test_admin_catalog_dom.py` |
| JS-Syntax | `node --check apps/web/static/admin-catalog.js`, Exitcode 0 |
| Konfliktmarker-Scan | keine Treffer |
| Trailing-Whitespace-Scan | keine Treffer |
| `git diff --check` | Exitcode 0; nur bekannte LF/CRLF-Warnungen fuer bestehende Dateien |

Hinweis zur Regression: Ein erster breiter Pytest-Lauf scheiterte vor Testausfuehrung an fehlenden Schreibrechten auf den Benutzer-Temp-Pfad. Die erfolgreiche Wiederholung lief mit frischem Worktree-Basetemp.

## 4. Contract-Grenzen

| Vertrag | Status |
|---|---|
| Admin-UI getrennt von normaler Workbench | testbelegt |
| normale Workbench verlinkt Admin-UI nicht | testbelegt |
| Bootstrap-Nonce nur im Fragment und sofortige URL-Bereinigung | testbelegt |
| Admin-Token nur fluechtig im JS-Speicher | testbelegt |
| keine `localStorage`-/`sessionStorage`-/Cookie-Persistenz | testbelegt |
| geschuetzte Admin-Catalog-API mit `X-Morphic-Admin-Token` | testbelegt |
| Draft, Validierung, Diff, Publish, Aktivierung, Rollback visuell getrennt | testbelegt |
| No-Store-Auslieferung fuer Admin-Oberflaeche | testbelegt |
| Kein Onlineadapter, kein Netzwerkfetch, keine Runtime-Catalogwirkung | bewusst nicht implementiert |

## 5. Fortschritt

| Ebene | Stand nach F6.4 |
|---|---:|
| F6.4 | `100 % technisch geschlossen` |
| F6 gesamt | `4/4 = 100 %` |
| Feedback f gezaehlte Einheiten | `32/39 = 82 %` |
| Feedback f Hauptphasenmodell | `75 %` |
| Nutzerfeedback a-f gesamt | `80 %` |

## 6. Exakt hier weiter

Naechster zulaessiger Block: **F7.1 Adaptervertrag und Netzwerkpolicy**.

Dabei gilt:

- keine Netzwerkfreigabe ohne explizite Admin-Freigabe pro Source-ID, Adapterversion und Tenant;
- keine automatische Publish- oder Runtimewirkung;
- F7.1 muss zuerst die Fail-Closed-Netzwerkpolicy, Host-Allowlist, HTTPS-/Redirect-/DNS-/IP-Schutz und Secret-Injektion testbelegen.
