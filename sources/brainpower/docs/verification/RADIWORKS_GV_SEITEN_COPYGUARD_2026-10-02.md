# RadiWorks: GV-Seiten, Ergebnisanzeige und Prüffreigabe (02.10.2026)

**Stand:** Lokaler Kandidat auf Port 8103; keine Aurelia-Integrationsfreigabe. Die vorhandene `/analysis`-Antwort und das registrierte Manifest-Schema bleiben unverändert. Bestehende Fall- und Broadcast-Daten wurden für diese Änderung nicht als Testdaten verwendet.

## Umgesetztes Verhalten

- Die rote Flächenfarbe für wiederkehrende Wörter ist entfernt. Der sichtbare **W**-Marker und seine Erklärung bleiben. Nur die GV-Zelle erhält bei vorhandenem Messwert eine Vergleichsfarbe und `↑`, `=` oder `↓` gegenüber dem zuletzt angezeigten Fall-GV. Das Zeichen ist **kein zeitlicher Trend**; Broadcast-Fortschritt berechnet keinen Raten-GV neu.
- Die bestätigte 21er-Prüfung für die erste Seite bleibt bestehen. Für Seite 2 und folgende gibt es einen ausdrücklich gestarteten Knopf. Der Start legt eine neue vollständige Fallsitzung und einen neuen Draft an, behält die vorherige Sitzung und die GV-Werte anderer Seiten im Kind bei und setzt nur die gewählte Seite für neue Raten-GV zurück. Jeder Zug prüft Draft-ID und Schrittzähler. Seitenindex und -länge werden mit dem GV-Zustand gespeichert, so dass ein abgebrochener Lauf nach Laden der Sitzung an derselben Seite fortgesetzt werden kann. Eine erneute vollständige Prüfung derselben Seite erzeugt erneut eine getrennte Sitzung.
- Der Bereich „Analyse prüfen und freigeben“ erklärt den zweistufigen Draft-Weg, die getrennten Direkt-/Auto-Broadcastwege und die rein lokale KI-Zwischenablage.
- Beim Wechsel zwischen gespeicherten Sitzungen wird auch der zugehörige Prüfdraft nachgeladen. So kann die Freigabeanzeige nicht den Draft der vorherigen Sitzung behalten; ein nicht abrufbarer Draft wird sichtbar als solcher gemeldet.
- CopyGuard im RadiWorks-Prototyp ist eine **lexikalische** DE/EN-Prüfung sichtbarer Ratentexte. Treffer werden in öffentlichen Antworten zurückgehalten und vor einer Draft-Freigabe gesperrt; der Digest bindet den geprüften Textstand. Das ist keine fachliche oder medizinische Validierung. Die zusätzliche lokale KI-Stufe ist erst für Aurelia vorgesehen.

## Dynamic Adjustments und Originalabgleich

Der geprüfte AetherOnePi-2.9.0-Ablauf behandelt `dynamic.adjustments` am Ende eines Broadcasts: Er vergleicht dann einen neu gezogenen Fall-GV und kann unter seinen Bedingungen einen weiteren, verkürzten Broadcast einreihen. Er schreibt **keine** periodisch neu berechneten Raten-GV in die Analyseliste. RadiWorks speichert derzeit nur den gleichnamigen Schalter; ein solcher Adjustment-Ablauf ist nicht implementiert. Auf 8103 ist der gespeicherte Wert momentan `true`, hat dort aber **keine Wirkung**. Die Oberfläche benennt diese Grenze; für den aktuellen Arbeitsschritt wurde kein weiterer Broadcast-Automat aktiviert und kein gespeicherter Betreiberwert geändert. Eine spätere Implementierung benötigt einen eigenen, zunächst rein virtuellen Zustands- und Abbruchtest.

## Nachweise und Grenzen

- Vollständige Engine-Suite auf dem Kandidaten: Exit 0, zwei umgebungsabhängige Skips. Die neuen API-Tests decken vollständige Kind-Sitzung, unveränderte Elternsitzung, GV-Zuordnung von Seite 2, kurze Seite 3, Wiederaufnahme, veraltete Bindung und nicht existierende Seite ab. Der bisherige Erste-Seite-/Auto-Test blieb grün.
- Isolierter synthetischer Chrome-Smoke: alle bestehenden Abschnitte plus Seite-2-Probe grün; Browser-JavaScript-Fehler 0. Die Seite-2-Probe belegt den vollständigen Nachfolger mit erhaltenem gemessenen Seite-1-Wert sowie die passende Draft-Anzeige nach Vor-/Zurücknavigation. W-Marker ohne roten Zellhintergrund, GV-Hinweis und Dynamic-Adjustments-Kennzeichnung wurden im Browser geprüft. JavaScript-Syntaxprüfungen bestanden.
- Zehn geänderte RadiWorks-Code-/Testdateien wurden nach Sicherung nach `Documents/Radiworks/radiworks_port` kopiert und sind SHA-256-gleich mit dem Kandidaten. Sicherung: `Brainpower/checkpoints/radiworks-source-sync-20261002`.
- 8103 wurde mit demselben Vorschau-Home, Katalog und Scope kontrolliert neu gestartet. Lesender Nachweis: `/ping=pong`, neuer Seiten-Endpunkt im OpenAPI-Schema, drei erhaltene Fälle, Auto AUS, null aktive und null wartende virtuelle Broadcasts. Der Betreiber-Bedienlauf der neuen Seite auf 8103 steht noch aus.
- Der neue Endpunkt `/analysis/gv-page/start` ist ein **lokaler RadiWorks-Zusatzweg**, keine Aurelia-Manifest-Operation und keine allgemeine Mehrmandanten-/Parallelitätsfreigabe. Das bisherige `/analysis`-Schema blieb bewusst unverändert.

| Phase | Geschätzter Stand | Offene Abnahme |
| --- | ---: | --- |
| S4.6 Ergebnis/Bedienung/GV | ca. 98 % | Betreiberprobe der neuen Seitenprüfung auf 8103; weitere Accessibility-Zustände |
| S4.7 Originalnähe/Restfunktionen | ca. 90 % | ergänzende Area-Darstellung, Peggotty-Randfälle, Kamera-/Hotbits-Langlauf und Wiederherstellung bei aktivem Fall |
| S4.8 Aurelia-Integration | 0 % | Host-, Scope-, Rechte-, Einwilligungs- und Betreiberentscheidung |

Die Prozentwerte sind Planungsnäherungen, keine Testabdeckung oder Freigabequote. Die späteren Area-, Peggotty- und Kamera-/Recovery-Punkte waren ausdrücklich als nächster Block vorgesehen und wurden hier nicht als erledigt markiert.
