# PHASE 4 – Frontend UI/UX und Google/web.dev 2026

## 4.1 Frontend-Fläche

| Datei | Zeilen | Rolle | Status |
|---|---:|---|---|
| `apps/web/static/index.html` | 402 | HTML-Struktur der Operator-Web-Shell | Aktiv, deutsch, semantische Bereiche, 8-Step-Wizard. |
| `apps/web/static/app.js` | 963 | State, Navigation, API-Fetches, Polling, Rendering | Aktiv, Vanilla JS, keine Build-Abhängigkeit. |
| `apps/web/static/app.css` | 1.204 | Design Tokens, Layout, Responsive, Reduced Motion | Aktiv, oklch/Radiquant4-Alignment, responsive Breakpoints. |
| `apps/web/main.py` | 558 | Static Serving + API | Aktiv, Uvicorn-Smoke erfolgreich. |

## 4.2 UI/UX-Flow

| Bereich | UX-Stärke | Code-Beleg | Bewertung |
|---|---|---|---|
| Geführter Wizard | Operator wird in 8 Schritten geführt, nicht mit freiem Formular überfordert. | `index.html:22-31`, `app.js:4-13` | Sehr gut für komplexen Workflow. |
| Fortschritt | Top-Stepper + Progress-Bar + `aria-live`. | `index.html:33-38`, `app.js:267-302` | Gut; Fokusmanagement beim Stepwechsel nur Scroll, keine aktive Fokussetzung. |
| Preflight | Health, Quellenstatus, Datenbank-/Profilkennzahlen sichtbar. | `index.html:45-79`, `app.js:316-369` | Gut: Fehler vor Analyse erkennbar. |
| Consent | Lokale Verarbeitung und Wellbeing-Hinweis blockieren Preview/Start. | `index.html:81-103`, `app.js:235-244`, `814-819`, `873-878` | Gut; Persistenz/Audit fehlt. |
| Scan Preview | Zeigt konkreten CLI-Befehl, Profilwahl, Entropie, Bild, Adaptive Limits. | `app.js:97-137` | Sehr gut für Freigabe/Transparenz. |
| Job Status | Status, Returncode, Phase, Substep, Log Tail, Progress. | `index.html:229-261`, `app.js:204-233` | Stark für Operator-Diagnose. |
| Reportkatalog | Klienten-/Session-Gruppierung, Vorschau, Datei öffnen. | `index.html:264-294`, `app.js:528-577` | Produktiv hilfreich; Zugriffsschutz fehlt. |
| HTML Preview | Inline-Iframe mit Sandbox; Backend saniert HTML. | `index.html:289`, `reports.py:531-555` | Positiv für Sicherheit/UX. |
| Harmonisierung | Abschluss-Panel mit Intention, Frequenz, Dauer, Hardware-Toggles, Start/Refresh/Stop. | `index.html:296-397`, `app.js:643-792` | Gute Vollständigkeit; Report-Kontext backendseitig stärker binden. |

## 4.3 Accessibility und Bedienbarkeit

| Kriterium | Status | Beleg | Lücke/Empfehlung |
|---|---|---|---|
| Sprache | `lang="de"` gesetzt. | `index.html:2` | Gut. |
| Viewport | Mobile Viewport gesetzt. | `index.html:5` | Gut. |
| Landmarken | `header`, `nav`, `main`, `section`, `aside` vorhanden. | `index.html` | Gut. |
| ARIA live/status | Statusbereiche mit `role="status"`, `aria-live="polite"`. | `index.html:16`, `33-34`, `226-229`, `277`, `290`, `359` | Gut. |
| Keyboard-Navigation | Buttons, Inputs; ArrowLeft/ArrowRight Navigation. | `app.js:941-955` | Gut, aber Step-Wechsel sollte Fokus auf Panel-Heading setzen. |
| Fokus sichtbarkeit | `:focus-visible` Styles vorhanden. | `app.css:268-273`, `612-621` | Gut. |
| Reduced Motion | `prefers-reduced-motion: reduce` global berücksichtigt. | `app.css:78-89` | Sehr gut. |
| Responsive | Breakpoints bei 980px und 620px. | `app.css:1144-1200` | Gut; reale Touch-Ziel-Messung fehlt. |
| Skip Link | Nicht sichtbar. | `index.html` | Für A11y ergänzen: „Zum Hauptinhalt springen“. |
| Form Labels | Labels mit Text vorhanden. | `index.html:115-132`, `145-167`, `185-206`, `311-330` | Gut. |
| Error Summary | Fehler werden inline angezeigt, aber keine zentrale Fehlerliste. | `app.js` | Für komplexe Forms besser zentrale Fehlermeldung mit Fokus. |
| Touch Targets | Buttons meist `min-height:42px`; WCAG-/mobile Best Practice oft 44x44 CSS px. | `app.css:584-590`; `docs/deep-audit-2026-07-05/GOOGLE_2026_VERIFIKATION.md:37-38` | 42px knapp; auf 44px anheben. |

## 4.4 Performance / Core Web Vitals – Codebasierte Einschätzung

| Metrik | Google/web.dev 2026 Referenz laut repo-interner Verifikation | Aktueller Codezustand | Bewertung |
|---|---:|---|---|
| LCP | gut: ≤ 2,5s | Kleine statische HTML/CSS/JS ohne externe Fonts; keine großen Hero-Bilder | Wahrscheinlich gut lokal, aber nicht gemessen. |
| INP | gut: ≤ 200ms | Vanilla JS, Polling, DOM-Rendering von Reports/Logs; bei 449 Reports potenziell DOM-lastig | Nicht gemessen; Reportliste/Preview kann bei großen Archiven belasten. |
| CLS | gut: ≤ 0,1 | Layout-Grids/Panelwechsel, keine fremden Ads/Fonts; Sticky Header/Stepper | Wahrscheinlich niedrig, aber nicht gemessen. |
| RUM | 75. Perzentil realer Nutzer | Keine RUM-/CWV-Instrumentierung sichtbar | Lücke für produktive Web-Nutzung. |
| Lighthouse | Lab-Prüfung | Kein CI-/Test-Gate sichtbar | Optionales Qualitätstor einführen. |

Quelle im Repo: `docs/deep-audit-2026-07-05/GOOGLE_2026_VERIFIKATION.md:16-27` bestätigt LCP/INP/CLS-Schwellen und RUM-Charakter. Live-Websuche war heute nicht möglich.

## 4.5 Google Search vs. web.dev-Qualität

| Thema | Anwendbarkeit auf Morphic V1 | Begründung |
|---|---|---|
| Google Search Essentials / SEO / Indexierung | Niedrig / aktuell nicht anwendbar | Die App ist eine lokale interne Operator-App ohne öffentliches Hosting, Sitemap, Robots- oder Indexierungsziel. |
| Mobile-First Indexing | Suchmaschinenbezogen nicht relevant; UX-relevant ja | Responsive Design bleibt wichtig, aber nicht für Ranking. |
| Strukturierte Daten / Rich Results | Nicht relevant | Kein öffentlicher Content, der Rich Results erzeugen soll. |
| Core Web Vitals | Als Engineering-Qualität relevant | Auch lokale Chromium-Apps profitieren von schneller Interaktion und stabiler Layoutführung. |
| Accessibility | Rechtlich/qualitativ relevant, nicht als Rankingfaktor | Repo-interne Google-2026-Datei trennt Google Ranking und WCAG/BFSG sauber. |
| Security Headers | Sehr relevant | web.dev/Browser-Baseline, besonders bei sensiblen Daten. |

## 4.6 Google/web.dev-2026-Abgleich nach Code

| Kriterium | Ist-Zustand | Beleg | Status |
|---|---|---|---|
| Keine externen Font-Requests | CSS nutzt Systemstack und kommentiert keine externen Fonts. | `app.css:61-67` | Gut. |
| Responsive Viewport | vorhanden | `index.html:5` | Gut. |
| Mobile Layout | Grid auf 2 Spalten/1 Spalte bei Breakpoints | `app.css:1144-1200` | Gut. |
| Reduced Motion | vorhanden | `app.css:78-89` | Gut. |
| Focus Visible | vorhanden | `app.css:612-621` | Gut. |
| Touch Target >=44px | teilweise knapp (`min-height:42px`) | `app.css:584-590`, Inputs `517-526` | Nachbessern. |
| CSP | nicht sichtbar | keine Header-Middleware | Lücke. |
| X-Content-Type-Options | nicht sichtbar | keine Header-Middleware | Lücke. |
| X-Frame-Options / frame-ancestors | nicht sichtbar | keine Header-Middleware | Lücke. |
| HSTS | nicht sichtbar | lokale HTTP-App | Für HTTPS Deployment relevant. |
| RUM/CWV | nicht sichtbar | keine web-vitals JS / keine Metrics API | Lücke, wenn öffentlich/mehrbenutzerfähig. |
| PWA/Offline | nicht sichtbar | kein manifest/service worker | Optional, nicht zwingend. |
| SEO-Meta | minimal (`title`, viewport) | `index.html:4-7` | Für lokale App ausreichend. |
| robots/sitemap | nicht vorhanden | Code-/Dateisuche | Für lokale App irrelevant. |

## 4.7 UI/UX-Befunde

| Nr | Kategorie | Schwere | Befund | Beleg | Empfehlung |
|---:|---|---|---|---|---|
| U1 | Operator UX | niedrig | 8-Step-Wizard ist klar, deutsch, phasenorientiert. | `index.html:22-31` | Beibehalten und an 12-Step-Backend visuell stärker koppeln. |
| U2 | A11y Fokus | mittel | Bei Stepwechsel wird gescrollt, aber kein Fokus auf aktiven Panel-Heading gesetzt. | `app.js:304-310` | `panel.querySelector('h2').focus()` mit `tabindex=-1` ergänzen. |
| U3 | Skip Link | mittel | Kein Skip-Link sichtbar. | `index.html` | Direkt nach `<body>` hinzufügen. |
| U4 | Touch Target | mittel | Buttons/Inputs min-height 42px, Empfehlung 44px. | `app.css:517-526`, `584-590` | Min-height auf 44px anheben. |
| U5 | CWV Messung | mittel | Keine INP/LCP/CLS-RUM-Messung. | Code-Suche | Optionales `web-vitals`-freies Mini-Metrics-Logging oder Playwright/Lighthouse-Gate. |
| U6 | Large Report DOM | mittel | Reportliste rendert alle Clients/Sessions/Files direkt. | `app.js:528-577`; Smoke `count=449` | Pagination/Virtualisierung oder Limit/Filter. |
| U7 | Error Summary | niedrig-mittel | Fehlermeldungen sind lokal, keine zentrale Fehlerzusammenfassung. | `app.js:814-925` | Für Forms und API-Fehler ein Summary-Panel. |
| U8 | Report Preview Context | niedrig-mittel | Harmonisierung hängt vom aktiven Report im Frontend ab, Backend bekommt keine Report-ID. | `app.js:718-747` | Backend-Payload um `report_id`/`artifact_id` erweitern. |

## 4.8 Innovationsvorschläge UI/UX

| Innovation | Nutzen | Aufwand | Risiko | Stabiler Gate-Ansatz |
|---|---|---:|---|---|
| Operator Workbench v2 mit 12-Step-Timeline | UI und Backend-Steps werden 1:1 sichtbar | mittel | gering-mittel | Erst read-only Timeline aus `SUBSTEP_MANIFEST`, dann Live-Events. |
| Manifest-first Report Explorer | Reports an Client/Session/Artifact sicher binden | mittel | mittel | Erst nur Anzeige mit Rückfall auf ReportCatalog, danach Enforcement. |
| A11y Quality Gate | Verhindert Regressionen | niedrig-mittel | gering | Playwright/HTML-Audit: Labels, focus, headings, touch size. |
| CWV/INP Local Metrics | UI-Performance messbar machen | niedrig | gering | Kleine PerformanceObserver-Messung optional im Dev-Modus. |
| Reportlisten-Filter | Bessere Bedienung bei 449+ Reports | niedrig-mittel | gering | Suchfeld + Limit + client/session filter. |
| Security Banner | Klarer Modus: Local/Open/Auth Enabled | niedrig | gering | `/api/status` um security_mode erweitern; UI Pill anzeigen. |

## 4.9 Reifegrad Phase 4

| Dimension | Score | Begründung |
|---|---:|---|
| Lokale Operator-Usability | 4.0/5 | Geführter Wizard, klare Zustände, Preview/Reports/Harmonisierung. |
| Accessibility | 3.5/5 | Gute Basis; Skip/Fokus/Touch/Error Summary fehlen. |
| Performance-Codequalität | 3.6/5 | Kleine statische App; keine Messung, große Reportlisten möglich. |
| Google/web.dev-Konformität | 3.3/5 | Viele Best Practices vorhanden, aber Headers/RUM/CWV fehlen. |
| SEO/Search-Relevanz | n/a | Nicht öffentlich indexierte lokale App. |

Phase-4-Urteil: Das Frontend ist als lokale Operator-Workbench brauchbar und deutlich strukturiert. Für professionelle Web-Qualität fehlen messbare Performance-/Accessibility-Gates und Security-Header; SEO ist aktuell kein sinnvolles Ziel.
