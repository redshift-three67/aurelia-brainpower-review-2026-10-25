# Google/web.dev 2026 – Live-Verifikation der Referenzkriterien

## Ziel dieses Abschnitts

`docs/deep-audit-2026-07-04/PHASE_4` hat das Frontend gegen web.dev-Leitplanken abgeglichen. Diese Datei prüft per aktueller Websuche (Stand `2026-07-05`), ob diese Referenzwerte noch korrekt sind, und ergänzt eine wichtige Einordnung, die im 07-04-Audit fehlte: **Ist Morphic V1 überhaupt ein Ziel von "Google-Richtlinien" im Suchmaschinensinn?**

## 1. Wichtigste Einordnung zuerst

Morphic V1 ist eine **interne, nicht öffentlich indexierte Operator-Anwendung** (lokaler FastAPI-Server, kein öffentliches Hosting, kein Robots-/Sitemap-Konzept, keine Suchmaschinen-Sichtbarkeit erkennbar). Damit gilt technisch:

- **Google Search Essentials** (Crawlbarkeit, Indexierung, Mobile-First-Indexierung, strukturierte Daten für Rich Results, Spam-Richtlinien) sind **nicht anwendbar**, weil es nichts zu crawlen/indexieren gibt.
- **web.dev-Qualitätsstandards** (Core Web Vitals, Formular-Best-Practices, Fokus-/Tastatur-Zugänglichkeit, `prefers-reduced-motion`, Security-Header) sind trotzdem **weiterhin sinnvoll**, weil sie generelle Chromium-/Browser-Engineering-Qualitätsmaßstäbe sind, unabhängig davon, ob Google die Seite indexiert. Sie sind der richtige Maßstab für "ist das ein professionell gebautes Web-Frontend", nicht weil Google ranken würde, sondern weil es die von Google/Chrome selbst definierte technische Exzellenzlinie ist.

Der 07-04-Audit hat diese Unterscheidung nicht explizit gemacht; sie ist aber wichtig, um Prioritäten richtig zu setzen (z. B. hat "Rich Results"/"strukturierte Daten" für dieses Projekt keine Relevanz, während Core Web Vitals/Accessibility sehr wohl relevant bleiben).

## 2. Core Web Vitals – Prüfergebnis: unverändert korrekt

Aktuelle Quellen (u. a. `web.dev/articles/vitals`, `web.dev/articles/defining-core-web-vitals-thresholds`, mehrere 2026-datierte Fachartikel) bestätigen für 2026 unverändert:

| Metrik | Schwelle "gut" | Status ggü. `PHASE_4` (07-04) |
| --- | --- | --- |
| LCP (Largest Contentful Paint) | `≤ 2,5 s` | unverändert korrekt zitiert |
| INP (Interaction to Next Paint) | `≤ 200 ms` | unverändert korrekt zitiert (INP ersetzte FID bereits seit März 2024, weiterhin aktueller Standard 2026) |
| CLS (Cumulative Layout Shift) | `≤ 0,1` | unverändert korrekt zitiert |

Messbasis bleibt das 75. Perzentil realer Nutzer-Sessions (Feld-/RUM-Daten), nicht Laborwerte. Der 07-04-Befund "keine RUM-/CWV-Instrumentierung vorhanden" bleibt damit unverändert gültig und relevant, falls Morphic V1 künftig auch außerhalb einer einzelnen lokalen Maschine betrieben wird.

## 3. Mobile-First-Indexierung – Prüfergebnis: bestätigt, aber nicht anwendbar

Aktuelle Quellen bestätigen: Mobile-First-Indexierung ist seit 2023 für alle Google-Properties abgeschlossen und 2026 laufender Normalbetrieb (Inhaltsparität Mobile/Desktop, serverseitig gerendertes strukturiertes JSON-LD, Viewport-Meta-Tag, responsive Single-URL-Design). Für Morphic V1 ist das mangels Suchmaschinen-Indexierung **nicht direkt relevant** – responsives Verhalten bleibt aber unabhängig davon aus reiner Usability-Sicht sinnvoll, wie in `PHASE_4` (07-04) bereits unter "Responsive/Mobile" bewertet.

## 4. Accessibility/WCAG – wichtige Aktualisierung ggü. 07-04

Neue, für diese Analyse relevante Erkenntnis aus der Websuche: Google hat im März 2026 den Abschnitt "Design for Accessibility" aus seiner JavaScript-SEO-Dokumentation entfernt, mit der Begründung, dass Google JavaScript seit Jahren zuverlässig rendert und das alte "im Zweifel Text-Browser/JS-aus testen"-Argument veraltet sei. Wichtig für die Einordnung:

- **Das ändert nichts an Accessibility als Qualitäts- oder Rechtsthema.** Google stellt explizit klar, dass WCAG-Konformität **kein direkter Google-Rankingfaktor** ist und war – die Dokumentationsänderung betrifft nur eine veraltete SEO-Testempfehlung, nicht die Gültigkeit von Accessibility-Standards selbst.
- Für ein Tool, das mit gesundheitsnahen, personenbezogenen Daten arbeitet (siehe `PHASE_3`, 07-04) und potenziell von unterschiedlichen Operator:innen bedient wird, bleibt Accessibility ein **eigenständiges, von Google unabhängiges Qualitäts- und Sorgfaltsthema** – in Deutschland zusätzlich mit einer klaren gesetzlichen Dimension über das **Barrierefreiheitsstärkungsgesetz (BFSG)**, das seit `28. Juni 2025` für bestimmte digitale Produkte/Dienstleistungen gilt. Das ist ein stärkerer, unabhängig von Google bestehender Grund für die in `PHASE_4` (07-04) empfohlenen Maßnahmen (Skip-Link, Fokusmanagement, `prefers-reduced-motion`) als "Google-Konformität" – sollte Morphic V1 je gegenüber Endkund:innen statt nur internen Operator:innen exponiert werden, wäre eine BFSG-Prüfung fachlich naheliegend.
- Konkreter, in `PHASE_4` (07-04) nicht genannter Zusatzpunkt: WCAG/gängige mobile Usability-Leitlinien fordern Touch-Ziele von mindestens `44×44 CSS-Pixel`. Das wurde im bisherigen Audit nicht geprüft und wäre ein sinnvoller Ergänzungspunkt für eine spätere UI-Detailprüfung der Web-Shell/Operator-Workbench.

## 5. Security-Header-Baseline – Prüfergebnis: unverändert relevant

Die in `PHASE_4`/`PHASE_3` (07-04) genannte fehlende Header-Baseline (`Content-Security-Policy`, `X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security`, `Cross-Origin-Opener-Policy`, `Cross-Origin-Resource-Policy`) bleibt unverändert eine anerkannte, von Google/web.dev empfohlene Grundhärtung für jede Webanwendung, die sensible Daten verarbeitet – unabhängig von Suchmaschinen-Sichtbarkeit. Kein Korrekturbedarf.

## 6. Zusammenfassende Bewertung

| Bereich | 07-04-Zitat | Heutige Prüfung |
| --- | --- | --- |
| Core Web Vitals Schwellen | korrekt | bestätigt, unverändert |
| Form-/Fokus-/Motion-Best-Practices | korrekt | bestätigt, unverändert |
| Security-Header-Baseline | korrekt | bestätigt, unverändert |
| Einordnung "Google-Suchrelevanz" | implizit vermischt mit "Web-Qualität" | jetzt explizit getrennt: Search Essentials nicht anwendbar, web.dev-Qualitätsmaßstäbe weiterhin sinnvoll |
| Accessibility-Treiber | nur an Google/web.dev festgemacht | ergänzt um BFSG/EU-rechtliche Perspektive als eigentlich stärkeren Treiber |
| Touch-Target-Größe | nicht geprüft | als offener Zusatzprüfpunkt ergänzt |

**Ergebnis:** Die technischen Referenzwerte aus `PHASE_4` (07-04) sind für 2026 weiterhin korrekt und müssen nicht revidiert werden. Die sinnvollste Ergänzung ist nicht eine Zahlenkorrektur, sondern die Klarstellung, *warum* diese Standards für Morphic V1 gelten sollten (Engineering-Qualität und ggf. BFSG), nicht *weil* Google sonst schlechter rankt.
