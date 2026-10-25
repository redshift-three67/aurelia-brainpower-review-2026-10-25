# E5.10B – lokales Consent Enrollment und Widerruf

**Stand:** 2026-07-12
**Branch:** `operator-workbench-phase1`
**Entscheidung:** **E5.10B technisch GO; E5.10 insgesamt weiterhin NO-GO**

## Ergebnis

E5.10B stellt einen dedizierten lokalen Enrollment-/Widerrufspfad für individuelle Gruppenanalyse-Einwilligungen bereit. Registrierung und Consent-Verwaltung sind vollständig vom Scanformular, Launcher, Worker und der Analyseaktivierung getrennt.

| Vertrag | Ergebnis |
|---|---:|
| explizite DPAPI-Registrierung mit separater Speicherfreigabe | ✅ |
| Registrierung standardmäßig ohne Analyse-Einwilligung | ✅ |
| serverseitig festgeschriebene Consent-Version `group-analysis-v1` | ✅ |
| aktivierte Einwilligung benötigt timezone-aware Ablaufzeit | ✅ |
| exakte pseudonyme Client-ID als Aktivierungs-/Widerrufsbestätigung | ✅ |
| Owner-/Workspace-/Tenant-Prüfung fail-closed | ✅ |
| sofortiger Widerruf | ✅ |
| Safe-Liste ohne Namen, Geburtsdaten, Tenant oder Pfade | ✅ |
| dedizierte UI außerhalb von `scan-form` | ✅ |
| Reload lädt nur redigierten Status und verlangt erneut Bestätigung | ✅ |
| keine Gruppenstärke, kein Kill-Switch und keine Scanaktivierung | absichtlich noch nicht vorhanden |
| keine Gruppenidentitäten oder Raten in Jobs, CLI, Reports oder Traces | ✅ |

## Zentrale Dateien

- `apps/web/group_consents.py`
- `apps/web/main.py`
- `apps/web/static/index.html`
- `apps/web/static/app.js`
- `apps/web/static/workbench-api.js`
- `tests/test_web_group_consents.py`
- `tests/test_workbench_group_consent_dom.py`
- `tests/test_group_e510_release_gate.py`

## Reale Browserabnahme

Die Abnahme lief auf dem vorab als frei geprüften Loopback-Port `8001`. Port `8090` blieb unberührt.

Beobachtete Verträge:

- Registrierung initial deaktiviert;
- Aktivierung und Widerruf initial deaktiviert;
- Registrierung erst nach expliziter DPAPI-Speicherfreigabe möglich;
- zurückgegebene Client-ID kanonisch `cli-<20 hex>`;
- Consent-Schaltflächen erst nach exakter Client-ID-Bestätigung aktiv;
- Aktivierung mit Ablaufzeit erfolgreich;
- Reload rekonstruiert nur pseudonyme ID und Safe-Status;
- nach Reload ist eine erneute exakte Bestätigung erforderlich;
- Widerruf sofort erfolgreich;
- Safe-Liste nach Widerruf: `consent_enabled=false` und ohne Testidentität;
- 320-px-Viewport: `scrollWidth == innerWidth == 320`;
- Testidentität anschließend gezielt gelöscht;
- temporärer Server beendet und Port 8001 als geschlossen bestätigt;
- ausschließlich eigens erzeugte temporäre Browserartefakte entfernt.

## Verifikation

| Prüfung | Ergebnis |
|---|---:|
| E5.10B Backend/DOM/Release-Fokus | `11 passed` |
| erweiterter Privacy-/Nichtwirkungsfokus | `38 passed` |
| Rest-Suite ohne Top-5 | `436 passed, 2 skipped`; fünf Rate-Limit-429-Ausreißer |
| alle fünf Ausreißer separat/frisch | jeweils `1 passed` |
| Top-5-Smoke | `1 passed in 102.24s` |
| Python-Compile | bestanden |
| JavaScript-Syntax | bestanden |
| `git diff --check` | bestanden; nur bestehende LF→CRLF-Hinweise |

## Freigabegrenze

E5.10B ist technisch abgeschlossen. Eine registrierte oder eingewilligte Identität startet keinen Scan und erzeugt keine Gruppenwirkung.

Weiterhin offen:

1. E5.10C – default-false Kill-Switch und explizite Gruppenstärke `[0,1]`;
2. E5.10D – kurzlebiger serverseitiger Activation Handle ohne Rohidentitäten/Raten in Payloads;
3. E5.10E/F – produktive lokale Integration, Rollback-, Privacy- und Browserabnahme.

**Finale Entscheidung:** `E5.10A GO`, `E5.10B GO`, `E5.10 weiterhin NO-GO`, `Geo separat NO-GO`.
