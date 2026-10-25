# RadiWorks: Layoutabgleich und Verfahrensgrenzen

Stand: 2026-10-06T20:25:22+02:00. Kandidat8112 gegen bestehende C23-Liveversion8103; Dauerinstanzen8103–8109 unverändert.

## Befund und Korrektur

Kein bisheriger fester HTML-Bedienelement-Identifier entfernt: 99 alt, 115 im Kandidaten, keine doppelten HTML-IDs. Alle zehn Ansichten lesend verglichen; im geprüften Original-Anzeigestand keine fehlenden sichtbaren bisherigen IDs. Diese Inventur ist kein vollständiger fachlicher Funktionstest aller dynamischen Zustände. Einstellungen ohne implementierte Funktion bleiben entsprechend der Nutzerfreigabe ausgeblendet. Die synthetische Kandidatendatenbank ist bewusst vom realen Livekatalog getrennt.

Ursache des vermissten GV-/Auto-/Freigabebereichs: Das persönliche Verfahren blendete die gesamte gemeinsame Original-Zeile aus. Jetzt bleiben Original-GV, Original-Auto-Zustand und Original-Prüfdraft sichtbar. Eine Erklärung und ein ausdrücklicher Rückwechselknopf ordnen sie zu. Persönliche Matrixscores bleiben eigene Werte und werden nicht als GV/EW dargestellt.

| Bereich | Originalverfahren | Persönliche Heuristik |
| --- | --- | --- |
| Original-Fall-GV / Auto-Status | Sichtbar und wie bisher bedienbar | Sichtbar und ausdrücklich als Original gekennzeichnet |
| Auto AUS | Verfügbar | Verfügbar, um einen bereits laufenden Original-Auto-Modus zu beenden |
| Neue GV-Runde / Original-21er-Prüfung / Auto AN | Bisheriger Ablauf bleibt | Gesperrt; Originalverfahren bewusst wählen |
| Original-Prüfdraft / Fragen / Zwischenablage | Bisherige Freigabe- und Sperrzustände bleiben | Sichtbarer Originalbereich, Aktionen gesperrt |
| Originalergebnisse / EXP1-Vergleich / Original-Watchlist | Bisherige Bereiche erreichbar | Über ausdrücklich gewähltes Originalverfahren erreichbar |
| Persönliche Ergebnisse / persönliche Broadcast-Auswahl | Getrennte Aufträge bleiben gespeichert | Eigener persönlicher Bereich unverändert |
| Stick-Pad-Treffer erneut analysieren | Nur bei geeignetem gespeicherten Stick-Pad-Ursprung | Versteckt und auch im Handler gesperrt; kein stiller Originalauftrag |
| Broadcast-Dock und übrige Modulansichten | Erhalten | Erhalten |

Das Wechseln startet keinen Auftrag und ändert keine laufenden Aufträge. Ein bereits laufender Original-Auto-Modus wird durch den Wechsel nicht beendet. Sein Statusabgleich überschreibt im persönlichen Verfahren nicht mehr die gewählte Datenbank. Disabled-Fieldsets erhalten untergeordnete Busy-/CopyGuard-Sperren, statt diese beim Rückwechsel pauschal aufzuheben. Zusätzlich verhindern Handlerprüfungen Original-Aktionen über Tastatur oder programmatische Klicks im persönlichen Verfahren. Original-Session-Pfeile bleiben im persönlichen Verfahren inaktiv.

## Nachweise

- Vor Änderung: Wiederherstellungspunkt `checkpoints/RadiWorks-Layout-20261006-201519`, fünf Dateien samt Hashnachweisen; Backup erneut verifiziert. Keine Fall-/Schlüsseldateien kopiert oder geändert.
- Browserregression reproduzierte vor dem Fix den fehlenden sichtbaren Original-GV-Bereich; danach zehn Prüfpunkte bestanden. Sämtliche HTTP-Aufrufe dieser Regression synthetisch abgefangen, keine echten API-Aufträge. Enthält AutoAUS, Rückwechsel ohne Auftrag, Draftsperre, Tastatur/programmatische Verfahrensgrenzen, Stick-Pad und390px-Ansicht. Desktop1440px und dunkles Template visuell kontrolliert.
- Alle zehn Tabs auf8103 und8112 in neuen Browserkontexten lesend geprüft; sämtliche nicht-GET-Anfragen blockiert, keine JavaScript-Laufzeitfehler und kein Seitenüberlauf im geprüften Desktopzustand.
- 21 bestehende JS-Vertragstests bestanden; Syntax aller28JS-Dateien geprüft.
- 41 gezielte Python-Tests bestanden, keine Fehler/Skips: Auto-Modus, Draft, GV-Beobachtungs-API und Broadcast-Ziel-API. Der zuerst versuchte unittest-Runner fand in diesen Pytest-Dateien keine Tests und zählt ausdrücklich nicht als Nachweis; korrekter Pytest-Lauf ist in `evidence/layout-api-regression.xml` belegt. Bekannte Node-ESM-/Starlette-Testadapterwarnungen ändern die bestandenen Testergebnisse nicht.
- Luna6/max: statischer Bedienelement-/API-Abgleich. Astra6/medium: unabhängiger Review des Korrekturdeltas ohne wesentlichen Restbefund; begrenzter Quellenreview, kein eigener vollständiger Livefunktionstest.

Nur drei Produktdateien geändert: index.html, analyze.js, app.css. Backend-/Analyseformeln unverändert. 172Produktdateien über den Service-Verifikator geprüft; Manifest `615ffb32b98951f60ee206449b755071c2414abb82269b941ae0ee80543c22aa`. 8112 antwortet mitHTTP200, bestehenderPID69156 bleibt ohneRestart. Service-Startdigest ist historischer Startupnachweis; aktueller Dateistand und Konfiguration für nächsten Start sind separat verifiziert. Aktuelle Benutzerfälle und Broadcasts wurden nicht zu Testzwecken verändert.

## Phasenstand / nächste Grenze

| Paket | Stand | Noch offen |
| --- | --- | --- |
| Layoutabgleich und Nachkorrektur | 100% technisch im beschriebenen Umfang | Persönliche Nutzerprobe8112 |
| O1–O5 Optionsfunktionen | Technisch geprüft | Gesamte persönliche Funktionsabnahme weiterhin offen |
| O6 reale Kamera | Hardwareabnahme offen | Geeignete reale Kamera/Feednachweis |
| O7 bestehendes Start5 | Bestandsprobe bestanden | Keine neue Version verteilt |
| O8 Übernahme | 0% Live-/Quelle-/Template-/Paketübernahme | Nutzerabnahme, Windows-Stoppauffälligkeit erneut prüfen, Checkpoint, Rollout, Quellen/Templates, neues Start5, Gesamtsicherung |
| S4.8 Aurelia-Integration | 0%, keine Freigabe | Plattform-/Host-/Betreiber-Gates |

Prozente betreffen begrenzte Arbeitspakete; keine Garantie vollständiger Gleichheit, Gesamtqualität oder Aurelia-Freigabe. Keine neue persönliche GV-Formel und keine ungetestete parallele Engineausführung ergänzt. Kanonischer RadiWorks-Quellordner, Modul_Templates und Portable5 bleiben bis zum vereinbarten Übernahmegate unverändert.

Evidenz: `runtime/rw-options-20261006/evidence/layout-regression.json`, `layout-all-tabs.json`, `layout-final-verification.json`, `layout-api-regression.xml`, reproduzierbare Playwright-Scripts und Screenshots.
