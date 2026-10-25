# Feedback f / F6.2 Admin-Catalog-API

Stand: 2026-07-17
Arbeitsort: `C:\morphic_v1\.worktrees\operator-workbench-phase1`
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`
Status: **F6.2 technisch geschlossen**

## 1. Kurzfazit

F6.2 ist technisch geschlossen. Die Web-App besitzt jetzt eine geschuetzte
Admin-Catalog-API hinter dem F6.1-Adminauth-Gate:

- `/api/admin/catalog/status` und `/api/admin/catalog/entries` sind nur mit
  gueltigem Admin-Token erreichbar;
- Draft-Create, Draft-Update, Validate, Diff, Publish, Activate und Rollback
  sind als FastAPI-Routen vorhanden;
- alle Mutationen verlangen Adminauth, contextgebundene Service-Ausfuehrung,
  erwartete Version/CAS und einen nicht-leeren Auditgrund;
- `X-API-Key`, OperatorContext und Entitlement-Stubs bleiben kein Adminnachweis;
- die Web-Schicht nutzt `AdminCatalogService` und erzeugt keine eigene
  Catalog-Logik;
- die Catalog-Service-Factory ist injizierbar, der Default nutzt die bestehende
  Validation-Key-Composition und bleibt ohne Validation-Key fail-closed.

F6.2 exponiert noch keine Admin-UI und korrigiert nicht die normale
Quellenanzeige. F6.3 und F6.4 bleiben offen. Onlineadapter und
Runtime-Catalogwirkung bleiben weiterhin gesperrt.

## 2. Geaenderter Scope

| Datei | Zweck |
|---|---|
| `apps/web/admin_catalog.py` | neuer geschuetzter Admin-Catalog-Router fuer Status, Entries, Drafts, Publish, Activate und Rollback |
| `apps/web/main.py` | Admin-Catalog-Router eingebunden; injizierbare Context-/Service-Factories ergaenzt |
| `tests/test_web_admin_catalog.py` | F6.2-Contract-Tests fuer Adminauth, CAS/Auditgrund und komplette Web-Lifecycle-Kette |
| `docs/status/2026-07-17-feedback-f-F6-2-admin-catalog-api.md` | dieser Gate-Record |

## 3. TDD-Nachweis

| Schritt | Ergebnis |
|---|---|
| RED F6.2-Service-Injektion | `4 failed`; erwarteter Fehlschlag wegen fehlender `admin_catalog_service_factory` |
| GREEN F6.2-Fokus | `4 passed in 1.03s` |
| RED PATCH-Route | erwarteter Fehlschlag `404` fuer `PATCH /api/admin/catalog/drafts/draft-1` |
| GREEN F6.2-Fokus nach PATCH | `4 passed in 0.95s` |
| Web-/Admin-Regression | `52 passed in 2.03s` fuer `tests/test_web_admin_catalog.py tests/test_web_admin_security.py tests/test_run_webui_launcher.py tests/test_web_shell.py tests/test_web_contracts.py` |
| Abschlussmatrix Web/Admin/Core | `68 passed in 3.20s` inklusive `tests/test_admin_catalog_service.py` |
| `py_compile` | Exitcode 0 fuer `apps/web/admin_catalog.py apps/web/main.py tests/test_web_admin_catalog.py` |

## 4. Contract-Grenzen

| Vertrag | Status |
|---|---|
| `/api/admin/catalog/*` ist adminauthgeschuetzt | testbelegt |
| normaler API-Key reicht nicht | testbelegt ueber F6.1/F6.2 |
| Mutationen verlangen erwartete Version/CAS | testbelegt |
| Mutationen verlangen Auditgrund | testbelegt |
| Draft-Create/Update/Validate/Publish/Activate laufen ueber `AdminCatalogService` | testbelegt |
| Rollback gegen fruehere aktive Revision | testbelegt |
| Default-Service bleibt ohne Validation-Key fail-closed | implementiert ueber bestehende Composition-Root |
| Keine Admin-UI, kein Onlineadapter, keine Runtime-Catalogwirkung | bewusst nicht implementiert |

## 5. Fortschritt

| Ebene | Stand nach F6.2 |
|---|---:|
| F6.2 | `100 % technisch geschlossen` |
| F6 gesamt | `2/4 = 50 %` |
| Feedback f gezaehlte Einheiten | `30/39 = 77 %` |
| Feedback f Hauptphasenmodell | `69 %` |
| Nutzerfeedback a-f gesamt | `80 %` |

## 6. Exakt hier weiter

Naechster zulaessiger Block: **F6.3 Quellenanzeigefehler separat korrigieren**.

Dabei gilt:

- normale Quellenansicht darf keine geschuetzten Admin-Details leaken;
- vollstaendige Source-Details bleiben der geschuetzten Adminansicht
  vorbehalten;
- F6.4 Admin-UI nicht in F6.3 vermischen;
- keine Onlineadapter-, Netzwerk- oder Runtime-Catalogfreigabe vor F7/F8.
