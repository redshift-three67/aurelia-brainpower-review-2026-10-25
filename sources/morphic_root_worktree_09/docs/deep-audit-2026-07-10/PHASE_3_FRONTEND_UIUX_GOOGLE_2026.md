# Phase 3 – Frontend, Usability, Accessibility und Google-/web.dev-Abgleich

## 3.1 Verifizierter UI-Zustand

Die Startseite ist eine deutschsprachige, responsive Operator Workbench mit Skip-Link, Landmarken, Live-Regions, sichtbaren Fokusstilen, Scrollregionen mit `tabindex=0`, Systemfont-Stack und `prefers-reduced-motion` (`index.html:10-49`, `app.css:61-89,612-620`). Der Flow bietet Kontext-/Einwilligung, Review, Scanstatus, Ergebnis, Trace, Katalog und Harmonisierung. HTTP-Smoke lieferte für `/` und statische JS jeweils HTTP 200.

| UX-Stärke | Beleg |
|---|---|
| klare sequenzielle Führung | 11 Navigationsschritte `index.html:25-37` |
| Review vor Jobstart | `index.html:238-265`, `app.js:169-201` |
| Transparente Hardwarekommunikation | Software-Fallback wird im Backend ausdrücklich ausgewiesen (`main.py:205-240`) |
| Fortschritt ohne Browserfreeze | Subprozess mit niedriger Windows-Priorität (`scan_jobs.py:14-18`) und 2s Polling (`app.js:207-243`) |
| sichere HTML-Vorschau-Isolation | iframe `sandbox`, Link `rel=noopener noreferrer` (`index.html:454-458`) |

## 3.2 UX-/Accessibility-Befunde

| Nr. | Befund | Schwere | Beleg / Wirkung |
|---:|---|---|---|
| U-01 | Der globale „Weiter“-Button erlaubt Phasenwechsel ohne clientseitige Gate-/Validity-Prüfung. | mittel | `app.js:441-449,533-536`; Pflichtfelder/Consent werden erst beim Preview/Start API-seitig sichtbar. Phase 2 kann unvollständig verlassen werden. |
| U-02 | API-/Start-/Harmonization-Fehler werden oft nur generisch dargestellt oder vollständig verworfen. | mittel | `app.js:179-181,202-204,350,367,389-402`; keine Fehlerdetails, Retry-/Korrekturführung oder ARIA-Fehlerreferenz. |
| U-03 | Erfolgreich abgeschlossene Jobs führen nicht automatisch zu Ergebnisphase 8. | mittel | `app.js:235-239` lädt Resultate, navigiert aber nicht. |
| U-04 | Statusklassen werden per `className="inline-state ${state}"` gesetzt, CSS prüft teils `[data-state=...]`. | niedrig | `app.js:41-46`; `app.css:644-653`. Erfolgs-/Fehlerfarben für Inline-State können ausbleiben. |
| U-05 | Reportliste baut servergelieferte Labels/Dateinamen mit `innerHTML` ein. | mittel | `app.js:284-306`. Reportdaten sollten als untrusted behandelt werden; DOM via `textContent` bauen oder serverseitig strikt escapen. |
| U-06 | Geburtsdatum hat nur `inputmode=numeric`, keine clientseitige Muster-/Format-Hilfe; Contract akzeptiert nur DDMMYYYY. | niedrig | `index.html:102`; `contracts.py:67-73`. |
| U-07 | Dateiauswahl übernimmt nur Dateinamen, keinen Upload; der angezeigte Wert kann kein serverlesbarer Pfad sein. | mittel | `index.html:194-200`; `app.js:524-530`. Funktional transparent beschrieben, aber für Nutzer leicht missverständlich. |
| U-08 | Keine automatisierte Browser-, Screenreader-, Kontrast- oder mobile Viewport-Prüfung im Projekt gefunden. | mittel | pytest deckt Backend/Strings, nicht DOM-Interaktion/CWV. |
| U-09 | Statische Assets haben im lokalen Smoke nur ETag/Last-Modified, keine explizite Cache-Control-Strategie; Root `/` erhält nicht die für `/ui` gesetzten no-cache Header. | niedrig | `main.py:317-330`, Smoke-Headers. |
| U-10 | Die Hardware-Review-Karte behandelt `components` als Array, obwohl der Backendvertrag ein Dictionary liefert; die Hardwarephase konvertiert korrekt, die Review-Karte ruft dagegen `comps.map(...)` auf. | hoch | `apps/web/hardware_truth.py:67-136`; `apps/web/static/workbench-render.js:74-79,145-146`. Reale Review-Renderung kann mit `TypeError` abbrechen. |
| U-11 | `fetch`-Wrapper prüft bei Scan-Preview/-Start keinen `response.ok`; zusammen mit leeren Catch-Pfaden kann ein 401/422 als erfolgreicher Start behandelt werden. | hoch | `apps/web/static/workbench-api.js:60-75`; `apps/web/static/app.js:169-204`. |
| U-12 | Die Fallback-Navigation erzeugt 11 Schritte, `navigate()` begrenzt ohne Registry aber auf 10; Phase 11 ist dann per Vor/Zurück nicht erreichbar. | mittel | `apps/web/static/app.js:441-449,501-510`. |
| U-13 | Die Pseudo-Radio-Karten bilden keine vollständige ARIA-Radiogroup: keine `role=radio`, kein `aria-checked`, keine Pfeiltastensemantik; die Selects sind zugleich aria-hidden. | mittel | `index.html:176,186,506`; `workbench-render.js:202-220`. |
| U-14 | Nach erfolgreichem Scan lädt die UI Ergebnisse, navigiert aber nicht automatisch in Phase 8; es gibt außerdem keinen Scan-Abbruch und keine Sperre gegen parallele Starts. | mittel | `app.js:235-255,184-201`; `index.html:516-518`. |

## 3.3 Google-/web.dev-2026-Abgleich

Am 2026-07-10 wurden die offiziellen Seiten über TLS mit `curl -k` erreicht: Google Search Central „Creating helpful, reliable, people-first content“, Google Search Central „Core Web Vitals“ und web.dev „Web Vitals“. Externe Firecrawl-Suche war in dieser Umgebung nicht konfiguriert. Der Abgleich betrifft deshalb technische Vorbedingungen, **keine** reale Google-Indexierung und keine gemessenen Feldwerte.

| Google/web.dev-Thema | Codebefund | Status |
|---|---|---|
| hilfreicher, personenorientierter Content | Dies ist eine authentifizierungsbedürftige lokale Operator-App, keine öffentliche Content-Site; SEO ist sekundär. | nicht anwendbar, bis öffentliche Seiten entstehen |
| Crawl/Indexierung | Keine robots.txt, sitemap, Canonical/Description/OG-Metadaten gefunden; Startseite hat Titel und Sprache. | für lokale App nicht erforderlich; für Marketing-/Docs-Site nachrüsten |
| Core Web Vitals (LCP/INP/CLS) | Keine Lighthouse-, CrUX-, RUM- oder Performance-Messung. DOM/CSS/JS sind lokal, aber Größe/Interaktion nicht gemessen. | **unverifiziert** |
| Accessibility als Qualitätsvoraussetzung | lang=de, viewport, skip-link, landmark, Live-Regions, keyboard controls, motion preference vorhanden. | gute Basis; manuelle/automatisierte Prüfung fehlt |
| sichere Browsereinbettung | iframe sandbox, keine externen Font-Requests in Workbench-CSS. | positiv |
| Performance/Resilienz | mehrere API-Loads beim Bootstrap; 2s polling; keine Asset-Bundling-/Cache-/Error-observability-Strategie. | mittel |

## 3.4 Empfohlenes Frontend-Gate

1. Playwright oder vergleichbares Browser-E2E: Pflichtfelder, Consent, Fehler, Keyboard, Report-XSS-Sample, Jobstatus und mobile 320px.
2. Lighthouse CI auf lokaler Testinstanz; LCP/INP/CLS als Budget erfassen, nicht schätzen.
3. axe-core/pa11y plus manuelle NVDA/Chrome- und Kontrastprüfung.
4. Vor jeder UX-Politur: U-10 und U-11 per Browser-Regressionstest schließen; danach Report-Rendering auf reine DOM-APIs umstellen sowie Preview-CSP/sandbox tests ergänzen.
5. Für spätere öffentliche Website: getrennte Marketing/Docs-Oberfläche mit Search Essentials, Datenschutz-/Impressumsseiten, robots/sitemap/canonical und strukturierten Daten nur für tatsächlich sichtbaren Content.
