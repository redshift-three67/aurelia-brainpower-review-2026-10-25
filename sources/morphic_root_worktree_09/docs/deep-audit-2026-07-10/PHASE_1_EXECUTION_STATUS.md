# Phase 1 – P0 Workbench-Vertrag: Ausführungsstatus

**Stand:** 2026-07-10T09:25:00+02:00
**Status:** in Ausführung – nicht abgeschlossen

## Abgeschlossene TDD-Tasks

| Task | RED-Nachweis | GREEN-Änderung | Verifikation |
|---|---|---|---|
| Hardware-Review akzeptiert Dictionary-Komponenten | Node-Regressionstest reproduzierte `TypeError: comps.map is not a function` | `apps/web/static/workbench-render.js` normalisiert `components` mit `Object.values()` | gezielter Node-/pytest-Test grün |
| Scan-Preview lehnt HTTP 422 ab | Node-Regressionstest zeigte: `loadScanPreview resolved despite HTTP 422` | `apps/web/static/workbench-api.js` enthält `requestJson()` und verwirft nicht erfolgreiche Preview-/Scanstart-Antworten mit Status/Detail | gezielter Node-/pytest-Test grün |
| Review-Karten interpretieren Client-/Hardwarewerte nicht als HTML | statischer Regressionstest fand `innerHTML` im Review-Renderer; DOM-Stub zeigte keine strukturiert gerenderte Hardwarekarte | Review-Karten verwenden nun erzeugte DOM-Knoten und `textContent`; keine `innerHTML`-Interpolation innerhalb von `renderReviewCards()` | gezielter Node-/pytest-Test grün |
| Alle Workbench-API-Helper lehnen nicht erfolgreiche Antworten ab | Node-Test ließ jeden API-Helper mit HTTP 503 laufen und schlug beim ersten still aufgelösten Helper fehl | alle API-Helper verwenden zentral `requestJson()` | 17 Helper werden gegen HTTP 503 geprüft |
| Fallbacknavigation nutzt alle statischen Phasen | Test fand keinen gemeinsamen Fallback-Stepbestand | `FALLBACK_STEPS` ist die eine 11-Step-Quelle für Bootstrap und `navigate()` | 11-Step-Regressionstest grün |
| Scan-Formular- und Consent-Gate | Frontend leitete unvollständige Daten/fehlende Einwilligungen erst an die API weiter | `validateScanPayload()` prüft fünf Pflichtfelder, DDMMYYYY und beide bereits serverseitig geforderten Einwilligungen vor Preview und Start | zwei RED/Green-Regressionstests |
| Job-ID-Gate | Ein erfolgreicher, aber unvollständiger Start-Response führte zur Laufphase ohne pollbaren Job | Start setzt UI-/State-/Navigation/Polling erst nach nichtleerer `job_id` fort | Regressionstest für fehlende Job-ID grün |
| Startfortschritt / 11-Step-Vertrag | Statisches HTML zeigte zunächst `1 / 10`, während Bootstrap und Fallback 11 Phasen definieren | Initialwert, Fortschrittsberechnung und Next-Gate leiten die Gesamtzahl jetzt aus den gerenderten Stepper-Buttons ab | 11-Step-Regressionstest grün |

## Aktuelle Prüfungen

```text
PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 C:/morphic_v1/.venv/Scripts/python.exe -m pytest tests -q
291 passed, 2 skipped in 131.47s

node --check apps/web/static/workbench-render.js
node --check apps/web/static/workbench-api.js
```

## Noch offene Phase-1-Tasks

1. Die UI-Fehlerdarstellung/Retry-Führung an den zentralen Fehlervertrag anbinden.
2. Startfortschritt `1 / 11` aus der Registryquelle rendern.
3. Report-Katalog und übrige dynamische Renderpfade auf sichere DOM-Ausgabe prüfen und schrittweise umstellen.
4. Browser-/DOM-Gates für 401/422, Tastatur/Fokus und XSS-Payloads ausbauen; danach Phase 1 vollständig prüfen.

## Unveränderte Grenzen

Keine Änderung an Kernengine, Scoring, Profilen, Multiplexen, Berichtsinhalten oder Produktionsdaten. Kein Commit/Push/Exportlöschen.
