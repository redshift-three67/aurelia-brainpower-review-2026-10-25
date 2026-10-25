# Phase 4 - Frontend, UI, UX Und Google 2026

## Kurzfazit

Die aktuelle Web-Shell ist funktional brauchbar, in Teilen angenehm strukturiert und fuer einen internen Operatorfluss schon relativ weit.
Sie verfehlt jedoch mehrere aktuelle web.dev-/Google-Leitplanken, vor allem bei Privacy-UX, Fokusfuehrung, Bewegungsreduktion, Messbarkeit und konsistenter Informationsarchitektur.

## 1. Referenzrahmen fuer den 2026-Abgleich

Waehrend dieser Analyse wurden als Google-/web.dev-nahe Leitplanken insbesondere diese Quellen herangezogen:

- `web.dev/articles/vitals`
  - Core Web Vitals: `LCP <= 2.5s`, `INP <= 200ms`, `CLS <= 0.1`, gemessen am 75. Perzentil und idealerweise mit eigener RUM-Instrumentierung
- `web.dev/articles/payment-and-address-form-best-practices`
  - sinnvolle Formelemente, echte Labels, Autocomplete, Inline-Validation, nur notwendige Daten, stabile Felder, Test in Field und Lab
- `web.dev/learn/accessibility/focus`
  - logische Fokusreihenfolge, sichtbare Fokusindikatoren, Skip-Links, sinnvolle Keyboard-Unterstuetzung
- `web.dev/articles/prefers-reduced-motion`
  - Bewegung/Animation an Nutzervorlieben koppeln
- `web.dev/articles/security-headers`
  - Security Header fuer sensible Webanwendungen als Basislinie

Wichtig:

- Der folgende Abgleich trennt beobachteten Codezustand und normative Zielbilder.
- Es wurden keine Lighthouse- oder CrUX-Livewerte erhoben.

## 2. Reale UI-Architektur

### Primaere UI

- `apps/web/static/index.html`
- `apps/web/static/app.js`
- `apps/web/static/app.css`

Diese Shell bildet einen 8-Step-Operator-Wizard fuer:

1. Preflight
2. Hinweise
3. Klientenaufnahme
4. Fokus
5. Scan-Profil
6. Analysefreigabe
7. Berichte
8. Harmonisierung

### Sekundaere UIs

- `/workflow-stepping` -> `apps/cli/workflow/workflow_stepping.html`
- optionales altes `/ui` aus `web_ui/`

Diese Koexistenz fuehrt zu einer fragmentierten UX-Realitaet.

## 3. Nachweisbare Staerken

1. Der Wizard ist funktional gut gegliedert.
   - `index.html:22-31`, `33-43`
2. Preflight und Quellenstatus werden sichtbar gemacht.
   - `app.js:316-368`
3. Der Scan-Launcher ist transparent.
   - `app.js:97-137`
4. Jobstatus, Phase, Substep, CLI-Logtail und Fortschrittsbalken sind vorhanden.
   - `index.html:223-261`, `app.js:204-233`
5. Es gibt sichtbare Focus-Styles und semantische Labels.
   - `app.css:174-180`, `511-520`
6. Report-Preview ist technisch sanitisiert.
   - `apps/web/reports.py:238-249`, `531-555`

## 4. Codebasierte UI/UX-Probleme

### Informationsarchitektur

| Problem | Evidenz | Auswirkung |
| --- | --- | --- |
| 8-Step-Produkt-UI und 12-Step-Doku sprechen nicht dieselbe Sprache | `index.html:22-31`, `workflow_stepping.html:27-245` | Verwirrung fuer Entwickler und Operatoren |
| Reports werden bereits beim Start geladen | `app.js:960-963` | unnoetige Vorablast, Privacy- und Kontextproblem |
| Report-Katalog zeigt historisierte Klientenlabels | `apps/web/reports.py:430-515` | PII-nahe Sichtbarkeit |
| Formular ist mit realistisch wirkenden Defaults vorbefuellt | `index.html:118-148` | Risiko fuer Demo/Privacy/Fehleingaben |

### Form-UX

| Problem | Evidenz | Bewertung gegen web.dev |
| --- | --- | --- |
| Geburtsdatum als freies Textfeld `DDMMYYYY` | `index.html:125-127`, `contracts.py:59-65` | formal validiert, aber schwach gefuehrt |
| Bildpfad als lokaler Dateipfadstring statt Browser-Upload | `index.html:203-206` | fuer Web/mobile unnatuerlich |
| Consent wird im Formular erfragt, aber nicht weiter erklaert oder nachweisbar gespeichert | `index.html:95-102`, `contracts.py:97-102` | UX ok, Governance schwach |
| Autocomplete ist nur teilweise genutzt | `index.html:116-131` | ausbaufaehig |

### Accessibility

| Problem | Evidenz | Bewertung |
| --- | --- | --- |
| Kein Skip-Link vor Header/Navigation | `index.html:10-33` | Abweichung von web.dev-Focus-Leitlinie |
| Schrittwechsel setzt keinen Fokus auf neuen Inhalt | `app.js:304-310`, `267-302` | Screenreader-/Keyboard-Fluss schwach |
| globale Arrow-Key-Navigation kann unerwartet wirken | `app.js:941-955` | teilweise konflikttraechtig |
| kein `prefers-reduced-motion` | kein Treffer im Frontend; `app.css:25-27`, `272-289` | Abweichung von Bewegungsreduktion |
| `workflow-stepping` nutzt Inline-`onclick` und klickbare `div`s | `workflow_stepping.html:250-273` | schwache A11y-Semantik |

### Responsive/Mobile

| Problem | Evidenz | Wirkung |
| --- | --- | --- |
| harte Sticky-Offets | `app.css:132`, `1061`, `1087` | fragil bei Zoom und kleinen Screens |
| Report-Iframe ist hoch und schwergewichtig | `app.css:935-937` | mobile Last und Scroll-Komplexitaet |
| Bildpfad-Input ist fuer mobile Endgeraete unpassend | `index.html:203-206` | schlechte Eingabe-UX |

## 5. Google/web.dev 2026 Abgleichsmatrix

| Bereich | Erwartung | Aktueller Codezustand | Urteil |
| --- | --- | --- | --- |
| Core Web Vitals | Messen in Field, idealerweise eigene RUM | kein `web-vitals`, keine RUM-Pipeline, kein Lighthouse-Artefakt | nicht erfuellt |
| LCP/INP/CLS-Bewertung | belastbare Metriken statt Vermutung | keine Messpunkte gefunden | nicht erfuellt |
| Form-Best-Practices | starke Labels, passende Input-Typen, nur noetige Daten, Inline-Hilfe | Labels vorhanden, aber Geburtsdatum/Bildpfad/Defaults problematisch | teilweise |
| Accessibility Focus | logische Fokusreihenfolge, Skip-Link, klare Fokusindikatoren | Fokusindikatoren ja, Skip-Link/Fokusmanagement nein | teilweise |
| Reduced Motion | `prefers-reduced-motion` respektieren | nicht implementiert | nicht erfuellt |
| Privacy-/Security-UX | sensible Daten zurueckhaltend zeigen | Report-Katalog zeigt historische Klientenlabels | nicht erfuellt |
| Mobile-First Flows | niedrige Reibung, keine fragilen Layout-Hacks | Wizard ok, aber harte Sticky-Werte und schwerer Report-Block | teilweise |
| Field Testing | echte Browser-/RUM-/Interaction-Daten | nicht vorhanden | nicht erfuellt |

## 6. Besondere Befunde zu `/workflow-stepping`

Diese Seite ist fachlich interessant, aber im aktuellen Produktkontext problematisch.

### Konkrete Probleme

1. Sie laedt externe Google Fonts.
   - `workflow_stepping.html:7`
2. Sie referenziert `workflow_stepping.css` relativ, aber `apps/web/main.py:224-233` liefert nur das HTML als Inline-Antwort aus.
   - Der CSS-Pfad ist damit im aktuellen Webrouting nicht sauber abgesichert.
3. Sie verwendet Inline-`onclick` und eigene Tastatursteuerung.
   - `workflow_stepping.html:250-273`
4. Sie beschreibt nicht exakt die gleiche Produktrealitaet wie die 8-Step Web-Shell.

### UX-Bedeutung

Fuer Entwickler ist die Seite als interne Systemgrafik nuetzlich.
Fuer Operatoren ist sie derzeit eher ein konkurrierendes mentales Modell als eine Hilfeseite.

## 7. Testabdeckung des Frontends

### Vorhanden

- `tests/test_web_shell.py`
- `tests/test_web_contracts.py`
- `tests/test_web_reports.py`
- `tests/test_web_scan_jobs.py`
- `tests/test_web_catalog_client_view.py`
- `tests/test_web_hardware_status.py`

### Abgedeckt

- API- und HTML-Struktur
- Contracts
- Reports/Sanitizing
- Jobparser
- Basis-A11y-Markup-Pruefungen auf Stringebene

### Nicht abgedeckt

- echte Browser-E2E-Tests
- visuelle Regression
- Touch-/Mobile-Interaktion
- Keyboard-Flows im Browser
- WebSocket-Livepfad im Frontend
- CWV/Lighthouse/RUM

## 8. Priorisierte UI/UX-Massnahmen

### P0

1. Report-Katalog privacy-by-design umstellen.
2. Einen einzigen offiziellen Workflow narrativ und visuell festlegen.
3. `/workflow-stepping` entweder intern kapseln oder mit der Produktrealitaet synchronisieren.

### P1

1. Fokusmanagement nach Schrittwechsel einbauen.
2. Skip-Link und klarere Tastaturpfade einfuehren.
3. `prefers-reduced-motion` unterstuetzen.
4. Geburtsdatum und Bildreferenz als echte Web-Form-Inputs neu modellieren.

### P2

1. WebSocket-Liveupdates statt reinem Polling nutzen.
2. Report-Laden lazy statt eager ausfuehren.
3. RUM/CWV-Messpunkte einfuehren.

## 9. Gesamturteil fuer das Frontend

Das Frontend ist kein Totalschaden und auch kein blosses Mockup.
Es ist ein arbeitsfaehiger interner Wizard mit echter Systemkopplung.
Der groesste UX-Schaden entsteht nicht durch fehlende Komponenten, sondern durch inkonsistente Produktgeschichte, Privacy-Widersprueche und fehlende moderne Qualitaetsmetriken.

## Ergaenzender Referenzhinweis

Fuer konkrete uebertragbare Workflow- und Usability-Muster aus `Radi144` siehe:

- `PHASE_6_RADI144_TRANSFER_WORKFLOW_UIUX.md`
