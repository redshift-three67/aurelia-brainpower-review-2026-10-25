# Phase 1 – Accessibility-Checkliste und Loopback-Nachweis

**Status:** Statischer und HTTP-Loopback-Baseline-Nachweis grün; manuelle
Browser-/Assistive-Technology-Abnahme noch offen.
**Betriebsprofil:** Variante A, lokaler Einoperator, ausschließlich Loopback.

## 1. Durchgeführter kontrollierter Loopback-Smoke

Ein temporärer Uvicorn-Prozess wurde mit dem Projektvenv auf `127.0.0.1:8001`
und einem temporär gesetzten `MORPHIC_RUNTIME_DIR` gestartet. Es wurden nur
`GET /api/health` und `GET /` angefragt.

| Prüfung | Ergebnis |
|---|---|
| Listenerbindung | ausschließlich `127.0.0.1:8001` |
| `/api/health` | HTTP 200 |
| Workbench-Shell `/` | HTTP 200 |
| Skip-Link in der Shell | vorhanden, Ziel `#main-content` |
| polite Live-Region | vorhanden |
| Prozessabschluss | Testserver kontrolliert beendet |
| Port 8090 / Radi144 | nicht angesprochen oder verändert |

Es wurden keine Scanstarts, Formulareingaben, Klientenexporte, Runtime-Inhalte,
Secrets oder Browser-LocalStorage-Daten verwendet.

## 2. Statisch nachgewiesene A11y-Baseline

| Bereich | Quellnachweis | Status |
|---|---|---|
| Skip-Link | `index.html:10`, Ziel `main-content` in `index.html:39` | statisch vorhanden |
| Navigationsbezeichnung | `index.html:25`, `role="navigation"`, `aria-label="Workbench-Navigation"` | statisch vorhanden |
| Fortschrittsansage | `index.html:40-43`, `role="status"`, `aria-live="polite"` | statisch vorhanden |
| Status-/Ergebnisregionen | mehrere gezielte `aria-live="polite"`-Regionen | statisch vorhanden |
| Sichtbarer Tastaturfokus | `app.css:268-274`, `:focus-visible` für Stepper; `app.css:612-621` für Controls | statisch vorhanden |
| Reduzierte Bewegung | `app.css:80-88`, `prefers-reduced-motion` | statisch vorhanden |
| JS-Shellregression | `tests/test_web_shell.py::test_web_shell_accessibility_and_report_readability_baseline` | automatisiert abgedeckt |

Ein statischer Nachweis ersetzt keine Interaktionsprüfung im Browser.

## 3. Manuelle Abnahme-Checkliste – noch auszuführen

Diese Schritte müssen auf einem kontrollierten lokalen Browserfenster erfolgen.
Nur synthetische, nicht sensible Eingaben verwenden und keinen Scan starten.

| ID | Durchführung | Erwartung | Status dieser Sitzung |
|---|---|---|---|
| M1 | `Tab` ab Seitenbeginn drücken. | Der Skip-Link wird sichtbar und springt mit Enter zum Hauptinhalt. | nicht manuell ausgeführt |
| M2 | Mit `Tab` durch Stepper, Zurück/Weiter, Formfelder und Statusregionen navigieren. | Sichtbarer Fokus, logische Reihenfolge, keine Tastaturfalle. | nicht manuell ausgeführt |
| M3 | Einen Step per Stepperbutton und per Zurück/Weiter wechseln. | Aktueller Step, Fortschritt und Live-Status werden korrekt aktualisiert. | nicht manuell ausgeführt |
| M4 | Bei 200 % Browserzoom und 320 CSS-Pixel Breite prüfen. | Bedienfelder bleiben erreichbar; keine unlesbare Überlappung oder horizontale Bedienfalle. | nicht manuell ausgeführt |
| M5 | Mit Firefox + NVDA durch Überschriften, Navigation, Status und Fehlermeldungen lesen. | Labels, Statusänderungen und Fokusreihenfolge sind verständlich. | nicht manuell ausgeführt |
| M6 | Sichtbaren Kontrast von Fokus, Buttons, Status und Fehlermeldungen prüfen. | Zustand/Fokus nicht allein über Farbe erkennbar; Text bleibt lesbar. | nicht manuell ausgeführt |

## 4. Korrigierter Tastaturbefund

Die Pfeiltastennavigation ist auf `#wizard-stepper` begrenzt
(`apps/web/static/app.js`). Außerhalb des Steppers bleiben `ArrowLeft` und
`ArrowRight` für native Controls und Scrollbereiche verfügbar. Der Regressionstest
`tests/test_workbench_navigation_js.py::test_arrow_navigation_is_scoped_to_the_workbench_stepper`
prüft die Begrenzung und das Verhindern des Standardverhaltens nur im Stepper.

Dieser automatisierte Nachweis ersetzt weiterhin nicht die manuelle M1–M6-Abnahme.

## 5. Begrenzung dieser Sitzung

Für eine echte M1–M6-Abnahme standen in dieser Agentensitzung kein steuerbarer
Browser, kein Firefox/NVDA-Lauf und keine Playwright-/Selenium-Toolchain zur
Verfügung. Es wird deshalb kein manueller Accessibility-Pass behauptet.

Vor der formellen Phase-1-Abnahme muss M1–M6 auf dem lokalen Windows-Desktop
nachgeholt und hier mit Browser-, Zoom-, NVDA/Firefox-Versionen sowie Ergebnis pro
Punkt dokumentiert werden. Erst danach kann der verbleibende Phase-1-
Accessibility-Restpunkt geschlossen werden.
