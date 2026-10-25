# RadiWorks: persoenlicher Statusabgleich – abgeschlossen 2026-10-07

Phase R5, gezielte Nachkorrektur der Betreiberprobe. Technische Korrektur in 8112 bereit; erneute Betreiberabnahme offen. Keine Integrationsfreigabe.

## Nachgewiesene Ursache

Der gezeigte Auftrag c98806e9 war serverseitig vollstaendig abgeschlossen: 1382 Ergebniszeilen, erstellt 2026-10-06T20:50:47.431652+00:00, abgeschlossen/aktualisiert 2026-10-06T21:00:09.656008+00:00. Laufzeit etwa 9 Minuten 22 Sekunden. Persoenliche Fallinhalte wurden nicht in den Bericht uebernommen.

Nach einem Fehler der Einzelstatusabfrage stellte das alte Frontend Polling ein. Die manuelle Aktualisierung ersetzte nur die Verlaufsliste, nicht den schon angezeigten Auftrag. Dessen alter running-Stand blockierte weitere Starts und verbarg die fertige Ergebnisliste. Ein Verlaufsklick konnte umgekehrt die Startsperre zu frueh loesen. Die Original-Recovery-Bedingung konnte zudem den gemeinsamen Analyseknopf auch im persoenlichen Verfahren sperren; ihre Beteiligung im konkreten Nutzertab ist nicht nachgewiesen.

## Eng begrenzte Korrektur

- Manuelle Aktualisierung gleicht den angezeigten Auftrag anhand seiner ID ab und nimmt Fortschrittsabfragen wieder auf.
- Auswahl im Verlauf und aktive Startsperre sind getrennt. Spaete Antworten koennen weder eine neu gewaehlte Ergebnissitzung noch einen anderen Fall ersetzen; terminale Auftraege werden nicht wieder als aktiv angezeigt.
- Ein bestaetigter Start plant Statusabfragen sofort, unabhaengig von einer ausstehenden Verlaufsantwort. Astra fand diese zusaetzliche P1-Luecke im ersten Korrekturstand; sie wurde vor Uebernahme mit eigener RED/GREEN-Regression geschlossen.
- Persoenliche Starts verwenden ihre eigenen Bedingungen; die Original-Recoverysperre bleibt fuer Original erhalten. Fehlender Katalog beziehungsweise unbestaetigter Start bleiben gesperrt. Kein automatischer POST-Replay.
- Die Statuszeile erklaert: Die Auswahl oben gilt fuer den naechsten Auftrag. Die vollstaendige sortierte persoenliche Liste erscheint erst nach Abschluss; grosse Datenbanken benoetigen mehrere Minuten.
- Ein zusaetzlich reproduzierter unbehandelter Entropiestatusfehler in Ueber/Quellen zeigt jetzt eine sichtbare Fehlermeldung.

Drei Produktdateien geaendert: webapp/js/views/personal_analysis.js, analyze.js und info.js; zwei neue Regressionstestdateien. Alle 133 Engine-Produktdateien bytegleich zur vorher gesicherten Version. Formeln, 80000 CPU-Kandidaten pro Rate, Fall-/Journalgrenzen, Zufallsfolgen und Backend unveraendert. Persoenliche Matrixscores bleiben getrennt von Original-EW/GV. Bestehende Auftraege behalten Datenbank, Modus und unveraenderlichen Kontext.

## Sicherung und verifizierte Uebernahme

Vorhersicherung: checkpoints/RadiWorks-Personal-Status-20261006-230252. 178 Dateien mit Hash-/Bytepruefung: 174 Produktdateien, Metadaten und konsistente Online-SQLite-Kopie der persoenlichen Auftraege (integrity_check ok). Kein neuer kompletter F:-Sicherungspunkt; Schluessel nicht ausgegeben.

Reparaturkopie runtime/rw-personal-status-20261006; synthetische Pruefung auf 8114. Finales Produktmanifest: 176 Dateien, SHA-256 00f646cfac80eefffdbb23ed06f49807e807a75ed782a95232e1ccaf5180bd00.

8112 verwendet weiterhin runtime/rw-ux-20261006, gleiches Home, KeyFile, Scope und Vollkatalog mit 123 Datenbanken. Verifizierte statische Hotfixuebernahme ohne zusaetzlichen Dienstrestart; PID 27556 waehrend dieser Uebernahme gleich. Alle drei ausgelieferten JS-Dateien stimmen bytegenau mit der geprueften Kopie ueberein. Der fertige Nutzerauftrag besitzt unveraendert 1382 Zeilen und denselben Datensatzhash 5240d2ee1a40d734253d601708940482ff17a992eaa06a84eb5cb5745b705a31. Service-state.manifestDigest bleibt der historische Startdigest; aktive Konfiguration und aktuelles Produktmanifest enthalten den neuen Digest.

## Pruefnachweise

| Pruefung | Ergebnis / Beleg in runtime/rw-personal-status-20261006 |
| --- | --- |
| Alte Statusanzeige im echten CPU-Browserlauf | RED: status-recovery-red.json, trotz 39 serverseitig fertiger Raten keine Tabelle nach Refresh |
| Fokussierte Frontendtests gegen Altstand | RED: 9 von 10 scheiterten, dokumentiert in evidence/personal-controller-red.log |
| Neuer hängender Verlaufsabruf | RED/GREEN, Bestandteil der finalen Regressionen |
| Entropiestatusausfall Ueber/Quellen | RED: unhandledRejection; GREEN: sichtbarer Hinweis |
| Gesamter JS-Regressionssatz | 41/41 PASS, inklusive 14 persoenlicher Tests und spaeter POST-/Poll-/Cancel-Antworten nach Fallwechsel; evidence/all-js-tests-final.log |
| JS-Syntax | 28 Produkt-JS-Dateien ohne Syntaxfehler |
| Backend/API/Journal/CPU-Controller/Budget | 32/32 PASS mit realem CPU-Bundle, evidence/personal-backend-final.xml; bestehende Starlette-Testclient-Deprecationwarnung |
| Statusfehler und Wiederaufnahme im Browser | 10/10 PASS: zwei kuenstlich unterbrochene GETs, echte seeded/stochastic 39-Raten-Auftraege, Refresh, sichtbare 21+18 Zeilen; evidence/status-recovery-green.json |
| Original-/Personal-Startsperren | 4/4 PASS bei kuenstlich fehlender Original-Recovery und Status-503, keine POSTs; evidence/personal-readiness-green.json |
| Realer vollstaendiger Grosskatalog | 1382/1382 Raten, 596.878 Sekunden, keine Kuerzung; evidence/large-job-completed.json |
| Jede Grosskatalog-Ergebniszeile im Browser | 4/4 PASS, alle 1382 Werte auf 66 Seiten mit API abgeglichen, letzte Seite 17 Zeilen, Refresh erhaelt Seite, kein neuer Auftrag; evidence/large-results-green.json |
| Vier Kombinationen / erhaltener Originalablauf | Final 15/15 PASS, 123 Kataloge, Original seeded/stochastic mit GV-21-Runde, Personal seeded/stochastic mit vollstaendiger Matrixscoreliste, zehn schmale Ansichten, keine JS-Fehler; evidence/ux-fourmode-visible-review-browser.json |
| Ausgelieferte 8112-Version | 5/5 schreibfreie Browserchecks, Vollkatalog/persoenliches Panel/GV-Controls/Startsperren, keine Mutation oder JS-Fehler; evidence/8112-readonly-browser.json |
| Eigener finaler Pruefdienststopp | 8114 exitClean=true, Port frei; evidence/8114-final-clean-stop.json |
| Nutzerinstanzen | Abschliessend 8103–8109 und 8112 jeweils ping200; Dauerinstanzen nicht aktualisiert |

## Zusaetzliche Beobachtung / Grenzen

Ein frueher Vier-Modi-Lauf endete mit worker_failed fuer einen synthetischen 39-Raten-Auftrag, 0 fertige Raten. Der exakt gleiche erste 21-Raten-Block lief danach mit identischen Eingaben erfolgreich: returncode0, 21 Zeilen, leerer stderr (evidence/worker-diagnostic.json). Ursache dieses Einzelereignisses nicht belegt; kein Formel-/CPU-Fix behauptet. Fehlerbeleg evidence/fourmode-worker-failure.json/.png bleibt erhalten.

Anschliessend verschwanden unerwartet die Entwicklungsprozesse fuer 8112 und 8114, ohne geordneten Stoppeintrag. Kein Windows-Neustart und kein Stopmarker festgestellt; Ursache unbekannt. Laufende Dauerinstanzen 8103–8109 waren weiterhin separat erreichbar. Beide Entwicklungsdienste wurden kontrolliert mit gleichen Homes/Scopes/Schluesselpfaden wiederhergestellt. Original-PID47940 ist deshalb nicht erhalten; PID27556 bezieht sich auf den wiederhergestellten 8112-Dienst. Bestehende gespeicherte Nutzerergebnisse blieben erhalten. Der letzte Vier-Modi-Lauf nach Wiederherstellung und alle gezielten Backendtests bestanden. Kein neuer Windows-Warmstart-/Codex-Schliessnachweis und kein garantierter Dauerbetrieb des Entwicklungskandidaten.

Eigene Browserkontexte und synthetische Faelle sind kein Nachweis fuer den Zustand des bereits offenen Nutzertabs. Es wurden keine Nutzerfaelle per API aktiviert oder neue Auftraege fuer reale Nutzerinhalte gestartet. Nach dem Wiederanlauf gegebenenfalls den gespeicherten Fall erneut laden.

Tatsaechliche Helfer: GPT-6 Luna/max fuer Frontendkorrektur/Regressionen; GPT-6 Astra/medium fuer unabhaengigen Grenzreview, final ohne verbleibenden wesentlichen Diffbefund. Leitung gemaess Betreiberwahl GPT-6.1 Sol/high; die gespeicherte Einstellung ist kein eigenstaendiger Laufzeitnachweis. Keine gemessene Tokenersparnis. Hermes-App-Routing nicht geaendert.

## Naechste Betreiberprobe und Gates

8112 mit Strg+F5 laden, unter Faelle den gespeicherten Fall laden, Persoenliche Heuristik waehlen, Auftraege/Status aktualisieren und den fertigen Zeeden-Auftrag auswaehlen. Erwartung: abgeschlossen 1382/1382 und blaetterbare eigene Matrixscoreliste. Danach bewusst einen neuen Auftrag mit einer kleinen Einzel-Datenbank starten; grosse Datenbanken koennen etwa zehn Minuten benoetigen. Neue Auswahl aendert keine alten Auftraege.

| Phase | Stand |
| --- | --- |
| R5 Status-/Startsperren-Nachkorrektur, begrenztes Paket | Technisch 100%, in 8112 geprueft bereit |
| R5 erneute Betreiberprobe dieses Fixes | Offen, keine neue Nutzerbestaetigung |
| R6 Dauerinstanzen / Quellmodul / Modul_Templates / neues Start5 | 0% dieser Uebernahme, erst nach Betreiberabnahme |
| S4.8 Aurelia-Integrationsfreigabe | 0%, keine Freigabe |

Audio-/Bildlayerplanung bleibt getrennt: docs/verification/RADIWORKS_BROADCAST_BILD_AUDIO_PLAN_2026-10-06.md. Phi-Fibonacci-Generator wartet auf Quellcode. Keine allgemeine Datenbankstrukturplanung oder Integrationsentscheidung in diesem Fix.
## Pause und nächste Prioritäten – 2026-10-07

Betreiberbeobachtung: Die persönliche Ratenberechnung läuft, dauert jedoch für die Bedienung zu lange. Das ist noch keine vollständige Betreiberabnahme. Für morgen zuerst die reale Laufzeit und den Rechenaufwand untersuchen; gemessene Grundlage: 1382 Raten mit 80000 Kandidaten je Rate in etwa zehn Minuten. Berechnung, Prozessstart, Datenübertragung und Darstellung getrennt messen. Beschleunigungen nur mit unveränderten bestätigten Formeln/Ergebnisregeln und belastbaren Vergleichstests; keine stille Kürzung der Datenbank oder Kandidatenanzahl. Den früheren einzelnen Workerfehler und Entwicklungsprozessverlust bei der Untersuchung berücksichtigen; Ursachen bisher nicht belegt.

Danach Bedienhinweise prüfen und vereinfachen:
- Analyseverfahren: Original AetherOne berechnet die bisherigen EW/GV-Werte; Persönliche Heuristik berücksichtigt ausgewählte persönliche Angaben und zeigt getrennte Matrixscores.
- Zufallsmodus: Reproduzierbar/seeded liefert bei gleichem Seed und unveränderten Eingaben wiederholbare Ergebnisse; stochastisch verwendet eine neu gezogene Zufallsfolge mit protokollierter Quelle. Beide Modi sind mit beiden Verfahren kombinierbar.
- „Einstellung (Server)“ ist kein dritter Zufallsmodus, sondern übernimmt die Servervorgabe. Für die ausdrückliche Wahl zwischen den beiden Modi ist diese Option nicht erforderlich. Empfehlung zur späteren Vereinfachung: in erweiterte Einstellungen verlagern oder die übernommene Vorgabe eindeutig anzeigen; keine Änderung während der Pause. Vor einer Ausblendung bestehende Konfigurationen und gespeicherte Aufträge berücksichtigen.

Die beiden Auswahlachsen werden schon in procedure-help und random-mode-help erklärt. Trotzdem als offener UX-Punkt vorgemerkt: einfachere Formulierungen, klare Unterscheidung der Ergebniswerte und gut sichtbare tatsächlich verwendete Auswahl je Auftrag. Der aktuelle Stand wird dadurch nicht als bereits optimal verständlich abgenommen.

Erst wenn Grundfunktion, Laufzeit und Bedienung stimmen: neuen Phi-Fibonacci-Frequenzmodulator/Binauralweg anhand des bereitgestellten Quellcodes prüfen; danach getrennte optionale Broadcast-Bildlayer umsetzen und abnehmen. Fallbezogene Definition/Speicherung der Darstellungsprofile ist vorgesehen; ein neuer Broadcast bindet einen unveränderlichen Profilstand. Analytisches Fokusbild bleibt getrennt. Audio-Eingaben, Layerdetails und technische Grenzen vor Umsetzung konkret prüfen. Aktueller Audio-/Bildlayerplan bleibt maßgeblich.

Pause: keine neuen Berechnungen, Instanzstarts/-stopps, Produktänderungen oder Liveübernahmen in diesem Arbeitsschritt. Kein unbeaufsichtigter Test für morgen eingeplant. R5 Betreiberabnahme offen; R6 und S4.8 unverändert gesperrt. Dieser Nachtrag ist Planung, kein Nachweis für zukünftige Laufzeiten oder den aktuellen Weiterlauf nach Codex-Schließen.