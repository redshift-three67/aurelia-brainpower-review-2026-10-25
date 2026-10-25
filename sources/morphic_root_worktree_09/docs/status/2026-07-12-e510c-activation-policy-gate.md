# E5.10C – default-false Kill-Switch und explizite Gruppenstärke

**Stand:** 2026-07-12
**Branch:** `operator-workbench-phase1`
**Entscheidung:** **E5.10C technisch GO; E5.10 insgesamt weiterhin NO-GO**

## Ergebnis

E5.10C führt eine serverseitige, standardmäßig deaktivierte Aktivierungspolicy und eine ausdrücklich festzulegende Gruppenstärke `[0,1]` ein. Die Policy bleibt ein lokaler Kandidat ohne Verbindung zum Scan-, Resolver- oder Workerpfad.

| Vertrag | Ergebnis |
|---|---:|
| `MORPHIC_GROUP_ANALYSIS_ENABLED` fehlt → `feature_enabled=false` | ✅ |
| nur explizite True-Werte (`1/true/yes/on`) aktivieren das Policy-Flag | ✅ |
| keine versteckte Default-Stärke | ✅ |
| Stärke muss explizit in `[0,1]` liegen | ✅ |
| Stärke `0` ist gültig und bleibt wirkungslos | ✅ |
| Policy-Safe-Summary ist identitätsfrei | ✅ |
| `analysis_ready=false` trotz Flag und Stärke | ✅ |
| `productive_effect=false` trotz Flag und Stärke | ✅ |
| UI außerhalb von `scan-form` | ✅ |
| Stärke wird nicht in Scanpayload, CLI, Job, Report oder Trace übernommen | ✅ |
| kein Resolver-/Identity-Import in der Policy | ✅ |

## Zentrale Dateien

- `apps/web/group_analysis_policy.py`
- `apps/web/main.py`
- `apps/web/static/index.html`
- `apps/web/static/app.js`
- `apps/web/static/workbench-api.js`
- `tests/test_web_group_analysis_policy.py`
- `tests/test_workbench_group_analysis_policy_dom.py`
- `tests/test_group_e510_release_gate.py`

## Reale Browserabnahme

Die Abnahme lief auf dem vorab als frei geprüften Loopback-Port `8001`; Port `8090` blieb unberührt.

Beobachtete Verträge:

- Kill-Switch initial als serverseitig deaktiviert angezeigt;
- Stärke initial leer, Speichern deaktiviert;
- keine versteckte Stärke;
- explizite Stärke `0` aktiviert die Vormerk-Schaltfläche;
- API-Antwort bei Stärke `0`: `feature_enabled=false`, `analysis_ready=false`, `productive_effect=false`;
- explizite Stärke `0.25` erfolgreich vorgemerkt;
- Browser-Reload stellt `0.25` innerhalb derselben lokalen Serverlaufzeit wieder dar;
- Kill-Switch bleibt nach Reload deaktiviert;
- `scan-form` enthält keine Gruppenfelder;
- 320-px-Viewport ohne horizontalen Overflow;
- temporärer Server beendet, Port 8001 geschlossen und ausschließlich Testartefakte entfernt.

## Verifikation

| Prüfung | Ergebnis |
|---|---:|
| erweiterter Policy-/Consent-/Nichtwirkungsfokus | `22 passed` |
| Rest-Suite ohne Top-5 | `441 passed, 2 skipped`; sieben Rate-Limit-429-Ausreißer |
| alle sieben Ausreißer separat/frisch | jeweils `1 passed` |
| Top-5-Smoke | `1 passed in 96.32s` |
| Python-Compile | bestanden |
| JavaScript-Syntax | bestanden |
| `git diff --check` | bestanden; nur bestehende LF→CRLF-Hinweise |

## Freigabegrenze

E5.10C ist technisch abgeschlossen. Weder Feature-Flag noch vorgemerkte Stärke erzeugen einen Activation Handle oder eine Scanwirkung.

Weiterhin offen:

1. E5.10D – kurzlebiger, owner-/tenantgebundener serverseitiger Activation Handle ohne Rohidentitäten oder Raten in Payloads;
2. E5.10E/F – produktive lokale Integration, Rollback-, Privacy- und Browserabnahme.

**Finale Entscheidung:** `E5.10A/B/C GO`, `E5.10 weiterhin NO-GO`, `Geo separat NO-GO`.
