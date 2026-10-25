# Feedback f / F6.3 Quellenanzeige-Safe-View

Stand: 2026-07-17
Arbeitsort: `C:\morphic_v1\.worktrees\operator-workbench-phase1`
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`
Status: **F6.3 technisch geschlossen**

## 1. Kurzfazit

F6.3 ist technisch geschlossen. Die normale Workbench-Quellenanzeige nutzt
jetzt den realen Source-Contract und bekommt nur noch eine reduzierte
Safe-View:

- `label` wird als Anzeigename verwendet;
- es wird kein erfundenes `name`-Feld mehr erwartet;
- `/api/sources` liefert fuer die normale Workbench keine `local_path`,
  Approval-/Importdaten, Trust-/Policy-Felder oder Repository-URLs;
- Statuszaehlung, `id`, `label`, `description`, `enabled`, `active`, `status`,
  `scopes` und `warnings` bleiben fuer die normale Workbench sichtbar;
- vollstaendige Source-Details bleiben geschuetzten Admin-Pfaden vorbehalten.

F6.3 baut keine Admin-UI, keinen Onlineadapter und keine Runtime-Catalogwirkung.

## 2. Geaenderter Scope

| Datei | Zweck |
|---|---|
| `apps/web/main.py` | `/api/sources` auf Workbench-Safe-View reduziert |
| `apps/web/static/app.js` | Quellenliste rendert `label` statt `name` |
| `tests/test_workbench_sources_dom.py` | F6.3-Contract-Tests fuer API-Safe-View und DOM-Feldvertrag |
| `docs/status/2026-07-17-feedback-f-F6-3-source-display-safe-view.md` | dieser Gate-Record |

## 3. TDD-Nachweis

| Schritt | Ergebnis |
|---|---|
| RED F6.3 | `2 failed`; API lieferte zu breite Source-Mappings und DOM nutzte `s.name` |
| GREEN F6.3-Fokus | `2 passed in 0.44s` |
| Web/Admin-Regression | `34 passed in 1.85s` fuer `tests/test_workbench_sources_dom.py tests/test_web_shell.py tests/test_web_admin_catalog.py tests/test_web_admin_security.py` |
| `py_compile` | Exitcode 0 fuer `apps/web/main.py tests/test_workbench_sources_dom.py` |

## 4. Contract-Grenzen

| Vertrag | Status |
|---|---|
| `label` wird angezeigt | testbelegt |
| `name` wird nicht als Source-Contract erfunden | testbelegt |
| normale Workbench erhaelt reduzierte Safe-View | testbelegt |
| `local_path`, Import-/Approval-/Trust-/Policyfelder nicht in `/api/sources` | testbelegt |
| Vollstaendige Source-Details nicht in normaler Workbench | testbelegt |
| Keine Admin-UI, kein Onlineadapter, keine Runtime-Catalogwirkung | bewusst nicht implementiert |

## 5. Fortschritt

| Ebene | Stand nach F6.3 |
|---|---:|
| F6.3 | `100 % technisch geschlossen` |
| F6 gesamt | `3/4 = 75 %` |
| Feedback f gezaehlte Einheiten | `31/39 = 79 %` |
| Feedback f Hauptphasenmodell | `72 %` |
| Nutzerfeedback a-f gesamt | `80 %` |

## 6. Exakt hier weiter

Naechster zulaessiger Block: **F6.4 Admin-UI als getrennte Oberflaeche**.

Dabei gilt:

- Admin-UI muss getrennt von der normalen Operator Workbench bleiben;
- Admin-UI nutzt den F6.1 Bootstrap-/Tokenpfad und die F6.2 Admin-Catalog-API;
- keine Onlineadapter-, Netzwerk- oder Runtime-Catalogfreigabe vor F7/F8.
