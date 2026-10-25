# Feedback f / F6.1 Fail-closed Adminauthentisierung

Stand: 2026-07-17
Arbeitsort: `C:\morphic_v1\.worktrees\operator-workbench-phase1`
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`
Status: **F6.1 technisch geschlossen**

## 1. Kurzfazit

F6.1 ist technisch geschlossen. Die Web-App besitzt jetzt einen separaten,
fail-closed Admin-Security-Kern fuer spaetere Adminmutationen:

- ohne explizit konfigurierte Admin-Security schlagen Adminrequests mit `503`
  fehl;
- normaler `X-API-Key`, `OperatorContext` und Entitlement-Stubs gelten nicht
  als Adminnachweis;
- Adminrequests verwenden ausschliesslich den separaten Header
  `X-Morphic-Admin-Token`;
- Bootstrap-Nonces sind kryptographisch zufaellig, maximal 30 Sekunden gueltig,
  single-use, an Origin, Host und Serverinstanz gebunden;
- der Nonce-Austausch liefert den Admin-Token nur ueber die same-origin
  Bootstrap-POST-Route, nicht in Cookie, Query oder URL;
- Token werden serverseitig nur als HMAC-SHA-256-Digests gehalten, laufen nach
  kurzer TTL ab, sind widerrufbar und werden mit `secrets.compare_digest`
  geprueft;
- der Launcher kann optional einen Adminstart vorbereiten und uebergibt nur den
  Bootstrap-Nonce im URL-Fragment, nie den Admin-Token.

F6.1 exponiert noch keine Admin-Catalog-API und keine Admin-UI. F6.2 bis F6.4
bleiben offen. Onlineadapter und Runtime-Catalogwirkung bleiben weiterhin
gesperrt.

## 2. Geaenderter Scope

| Datei | Zweck |
|---|---|
| `apps/web/admin_security.py` | neuer fail-closed Admin-Security-State, Bootstrap-Exchange-Route, Token-Dependency |
| `apps/web/main.py` | Admin-Security-State aus Launcher-Umgebung initialisiert und Bootstrap-Router eingebunden |
| `Run-WebUI.ps1` | kryptographischen Bootstrap-Nonce erzeugt, erwartete Origin/Host setzt, optionalen Fragment-Adminstart vorbereitet |
| `tests/test_web_admin_security.py` | F6.1-Contract-Tests fuer Fail-Closed, Headertrennung, Nonce-/Tokenvertrag und Launchergrenzen |

## 3. TDD-Nachweis

| Schritt | Ergebnis |
|---|---|
| RED `tests/test_web_admin_security.py` | erwarteter Importfehler: `ModuleNotFoundError: No module named 'apps.web.admin_security'` |
| GREEN F6.1-Fokus | `8 passed in 0.56s` |
| Security-/Launcher-Smoke | `11 passed in 0.64s` fuer `tests/test_web_admin_security.py tests/test_run_webui_launcher.py tests/test_web_local_security_headers.py tests/test_web_local_security_headers_runtime.py` |
| Web-App-Regression | `48 passed in 1.20s` fuer `tests/test_web_shell.py tests/test_web_contracts.py tests/test_run_webui_launcher.py tests/test_web_admin_security.py` |
| `py_compile` | Exitcode 0 fuer `apps/web/admin_security.py apps/web/main.py` |

## 4. Contract-Grenzen

| Vertrag | Status |
|---|---|
| Keine konfigurierte Admin-Security sperrt Adminzugriffe | testbelegt |
| API-Key, OperatorContext und Entitlement-Stub reichen nicht | testbelegt |
| Separater Header `X-Morphic-Admin-Token` erforderlich | testbelegt |
| Bootstrap-Nonce single-use, Origin-/Host-gebunden und zeitlich begrenzt | testbelegt |
| Admin-Token nicht in Cookie, Query oder URL-Fragment | testbelegt |
| Constant-time Digest-Vergleich | testbelegt |
| Launcher gibt keinen Admin-Token aus und nutzt nur Fragment-Nonce | testbelegt |
| Admin-Catalog-Mutationen bleiben bis F6.2/F6.4 ausstehend | bewusst nicht implementiert |

## 5. Fortschritt

| Ebene | Stand nach F6.1 |
|---|---:|
| F6.1 | `100 % technisch geschlossen` |
| F6 gesamt | `1/4 = 25 %` |
| Feedback f gezaehlte Einheiten | `29/39 = 74 %` |
| Feedback f Hauptphasenmodell | `66 %` |
| Nutzerfeedback a-f gesamt | `79 %` |

## 6. Exakt hier weiter

Naechster zulaessiger Block: **F6.2 Admin-Catalog-API**.

Dabei gilt:

- alle Admin-Catalog-Mutationen muessen `require_admin_request` nutzen;
- jede Mutation braucht Kontext, erwartete Version/CAS und Auditgrund;
- F6.3 Quellenanzeige und F6.4 Admin-UI nicht in F6.2 vermischen;
- keine Onlineadapter-, Netzwerk- oder Runtime-Catalogfreigabe vor F7/F8.
