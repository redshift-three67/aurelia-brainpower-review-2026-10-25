# RadiWorks: Fallbezug, Fokusbild und paralleler 21-Minuten-Versuch

Versuch am 03.10.2026; Abschlussdokumentation am 04.10.2026. Ausschließlich synthetische Fälle, eigene Testprozesse und Ports 8111–8113. Keine Übernahme in die Dauerinstanzen 8103–8109.

## Ergebnis und Bedeutung

**Die technische Fallzuordnung ist geprüft, eine numerische Wirkung des persönlichen Vektors ist derzeit nicht implementiert.** Name, Fokus und Absicht werden nach der Berechnung dem Draft zugeordnet. Die normale Analyse verarbeitet Ratenkatalog und Entropie; sie liest weder Namen noch Geburtsdatum, Ort oder Bild als Berechnungseingang. Der Fokus kann nach bewusstem Nutzerklick die Datenbanksuche unterstützen.

Die bestehende Oberfläche besitzt keine getrennten validierten Felder für Vorname, Nachname, Geburtsdatum und Ort. Im Versuch enthielten die drei unterschiedlichen erfundenen Fallnamen diese Angaben; zusätzlich war jeweils ein anderer Fokus gespeichert. Das prüft den vorhandenen Vertrag, keinen noch nicht vorhandenen strukturierten Personenvektor.

Bei **jedem der drei Seeds** waren die numerischen Ergebnisse aller drei Fälle identisch. Die neun Kontrollanalysen zeigen damit, dass unterschiedliche Fallkontexte im aktuellen seeded-Verfahren keine andere Rangfolge, EW, Potenz, Level oder Analyse-GV bewirken. Bei unterschiedlichen Seeds änderten sich diese Werte. Diese Variation belegt keine bessere oder angemessene persönliche Fallpassung. Der kleine kontrollierte Versuch ersetzt keine allgemeine wissenschaftliche Validierung.

Quellenbezug im Kandidaten: `api/routes.py:367` beschreibt den Request; `routes.py:667` berechnet vor der Kontextzuordnung ab Zeile 683. `main.py:146–147` erstellt den Broadcast mit eigener Entropie, aber stets Seed 0.

## Durchführung

Katalog: dieselbe unveränderte Datei `ESSENCES_BACHFLOWERS_RATES.txt`, SHA-256 `3ae6634e3d821d3a9e421db0e77b5675a0224a48a7b1c010c2a6889388ba6720`. Alle Analysen lieferten die vorhandenen 39 Raten. Drei getrennte Prozesse mit getrennten Homes, Client-/Job-Scopes, Fallreferenzen, Sitzungen und Drafts. Jeder Fall wurde mit Seeds 20261003, 20261004 und 20261005 analysiert. Anschließend erfolgte je eine vollständige 21-Raten-GV-Runde und eine ausdrückliche Draft-Freigabe.

Die gemeinsame Beobachtung lief von **21:33:19 bis 21:54:20 UTC** am 03.10.2026, entsprechend **23:33:19 bis 23:54:20 MESZ**. Letzter Messpunkt: **1260,067 Sekunden**, 249 externe Queue-Abfragen. Die gesamte gemeinsame Laufzeit bis zur Abschlussprüfung betrug 1260,925 Sekunden. Der vorherige Drei-Sekunden-Funktionstest zählt ausdrücklich nicht als Langlauf.

| Synthetischer Fall | Testport | Gewählter Seed | Fall-GV nach 21er-Runde | Raten mit GV | Aktive Broadcasts | Simulierte Resonanzereignisse |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 8111 | 20261003 | 802 | 21 | 8 | 75 |
| B | 8112 | 20261004 | 960 | 21 | 4 | 37 |
| C | 8113 | 20261005 | 1019 | 21 | 1 | 10 |

Die unterschiedlichen Broadcast-Anzahlen folgen der bestehenden Auswahl/Freigabe; es wurde keine gleiche Auftragszahl erzwungen. Die ersten 21 Plätze überlappten zwischen den gewählten unterschiedlichen Seeds in 11, 12 bzw. 11 Raten; alle vollständigen Ratenmengen waren gleich, ihre Reihenfolge unterschiedlich.

Alle gewählten Broadcasts blieben bis zum letzten Messpunkt aktiv. Fallreferenz, Scope, Sitzung, ursprünglicher Ratenindex und Analysehash blieben passend; die kumulierten Resonanzzähler fielen nicht zurück. Die Analysewerte und Fallkontexte blieben während der Beobachtung unverändert. Danach wurden ausschließlich die Testqueues geleert und die eigenen Testprozesse beendet; 8111–8113 sind geschlossen.

**Resonanzgrenze:** Dies sind virtuelle Zufallsereignisse. Alle Broadcast-Prozesse starten mit Seed 0, also nicht mit unabhängigen stochastischen Strömen. Unterschiedliche Queuegrößen und Zeitabläufe beeinflussen die Zuordnung der Zufallsziehungen. 75/37/10 ist daher kein vergleichbarer Nachweis von Fallpassung oder Harmonisierung. Es gab keine zusätzlichen periodischen GV-Ziehungen und keine Kamera-/Hotbits-Probe.

## Optionales Fokusbild

**Als separat zugeordnetes Kontextbild machbar; noch nicht implementiert.** Die normale Analyse nimmt kein Bildfeld an. Ein entsprechender Zusatzparameter wurde in allen drei Testscopes mit HTTP 422 abgewiesen. Die künstlichen Bilder B/C blieben ausschließlich mit Referenz und Hash im Versuchsmanifest; ein Bild-/Kein-Bild-Analysevergleich war daher nicht möglich. Die Funktionen „Bild & Area“ sind eigenständige Abläufe und ersetzen diesen Vertrag nicht.

Empfohlen ist ein optionales fallgebundenes Bild mit unveränderlichem Kontext-Snapshot pro neuem Draft. Gleicher Seed/Katalog soll mit und ohne Kontextbild die bisherigen Zahlen liefern. Keine heimliche Verwendung von Namen oder Bildhash als Seed. Eine neue fallbezogene Auswahlberechnung müsste als eigener Modus separat beschlossen, spezifiziert und geprüft werden.

Der [konkrete Bildvorschlag](../superpowers/specs/2026-10-03-radiworks-fokusbild-pruefung.md) beschreibt Format-/Größenlimits, Scope, Fallwechsel, Speicherung, Wiederanlauf und Modul_Templates-/Aurelia-Abstimmung. Animierte/mehrseitige Bilder, Decoderbudget sowie Entfernen/Löschung historisch referenzierter Bilder müssen vor Umsetzung ausdrücklich festgelegt werden. Kein gemeinsamer Hostvertrag wurde geändert.

## Zusätzlich erkannter Broadcast-Taktfehler

Der Fortschrittszeitpunkt wurde bisher in jedem 50-ms-Tick zurückgesetzt und erreichte nach dem ersten Ereignis meist nicht mehr den vorgesehenen 200-ms-Abstand. Im **isolierten Kandidaten** wird die Fälligkeit jetzt einmal je Tick geprüft und die Zeitbasis nur bei Fälligkeit weitergesetzt; alle aktiven Einträge erhalten dabei ihre Fortschrittsmeldungen. Keine neue GV-Berechnung und keine Änderung an Seed/Formeln oder Zuordnungsfeldern. Mehr Ereignisarbeit kann bei begrenzter Laufzeit die erreichbare Tickzahl beeinflussen; identische Resonanz-Endzählungen werden nicht garantiert.

- Zwei Fake-Clock-Regressionsfälle für einen und drei aktive Einträge waren vor dem Fix rot, danach grün.
- Vollständige Kandidaten-Engine: **362 bestanden, 2 bekannte Windows-Symlink-Skips**, eine bestehende Starlette/httpx-Warnung.
- JavaScript-Syntaxchecks für Analyse, Broadcast und Browser-Smoke bestanden. Ein erster Check verwendete einen nicht vorhandenen `webapp/main.js`-Pfad; die tatsächlichen Dateien wurden danach geprüft.
- Die neue vollständige Browserregression ist **nicht bestanden/abgeschlossen**: ein Start scheiterte bei Prozessinitialisierung, ein Wiederholungsversuch brach nach zwei PASS-Abschnitten mit `Fatal process out of memory: Zone` ab. Windows meldete anschließend ca. 723 MiB freie Commit-Reserve bei ca. 3,4 GiB freiem RAM. Keine fremden Programme, Auslagerungsdatei oder Dauerinstanzen wurden verändert. Kein verbliebener Test-Python-Prozess festgestellt; der synthetische Browser-Testordner bleibt als Diagnose erhalten.
- Der frühere 22/22-Browsernachweis gilt für GV-1 **vor** diesem Takt-Fix. Auch der 21-Minuten-Langlauf verwendete eine eingefrorene Quelle vor dem Takt-Fix. Diese Nachweise werden nicht auf den neuen Stand umgedeutet.
- Gemischte Zeilenenden in `broadcast.py` wurden abschließend zu CRLF normalisiert; der Python-AST blieb identisch zur erfolgreich getesteten Fassung.

Luna/max prüfte den Datenfluss und implementierte ausschließlich den kleinen Takt-Fix samt Fake-Clock-Test. Astra/medium prüfte unabhängig die Interpretation, den Fix und den Bildvertrag statisch; keine eigenen Laufzeittests. Sol 6.1/high führte Versuch, Kontrollmatrix, Vollsuite, Auswertung und Dokumentation aus. Keine gemessene Kosteneinsparung und keine Änderung der Hermes-/Governors-Routen.

## Erhaltener Stand und Fortsetzung

**134/134 Originalquelldateien unverändert; alle sieben Dauerinstanzen `/ping=pong` und dieselben Prozess-IDs wie vor dem Versuch.** Ihre Fälle und Broadcasts wurden nicht angefasst. Der Kandidat ist nicht live übernommen.

| Arbeitspaket | Stand | Nächster notwendiger Schritt |
| --- | ---: | --- |
| Kontrollmatrix und 21-Minuten-Versuch | 100 % | Ergebnis dokumentiert; Vektorwirkung nicht vorhanden |
| Fokusbild-Machbarkeitsprüfung | 100 % | Bildspeicher-/Löschvertrag vor Umsetzung konkretisieren |
| Fokusbild-Funktion | 0 % umgesetzt | getrennte additive Erweiterung, keine heimliche Algorithmusänderung |
| Broadcast-Takt-Fix | Engine geprüft | vollständige Browserregression nach Entlastung erneut durchführen; vor Live-Übernahme offen |
| GV-1 Fall-/Sitzungsbindung | 100 % isoliert geprüft | dauerhafte Identität/Wiederanlauf für Historie vorbereiten |
| GV-2 periodische 21-Minuten-GV und Historie | 0 % umgesetzt | getrennte Entropie, Fake-Clock-/Stop-/Wiederanlauftests, additive Historie |
| Reale Kamera/Stochastic und Warmstart | offen | echte Umgebungsproben |
| S4.8 Aurelia-Integration | 0 % | Host-/Templatevertrag und Betreiberfreigabe |

Die Prozente beziehen sich auf die benannten Teilpakete, nicht auf Gesamtproduktreife. Als Nächstes bleibt GV-2 ein eigener isolierter Block. Die aktuelle Probe war ein 21-minütiger Broadcast-Beobachtungslauf, keine bereits implementierte periodische GV-Aktualisierung.

## Reproduzierbare Belege

Laufverzeichnis: `runtime/rw-vector-probe-20261003-233302`. `RESULT.json` enthält Dauer/Abschluss, `SUMMARY.json` die Gegenüberstellung, `CONTROLS.json` alle neun Analysen, `samples.jsonl` die Messpunkte und `CONTRACT_CHECKS.json` die Bild-/Kontextchecks. `analysis-comparison.csv` und `resonance-comparison.csv` erlauben Einzelprüfung. `SOURCE.json` bindet Quell-/Katalogbytes; `EVIDENCE_MANIFEST.json` bindet alle Versuchdateien mit SHA-256. `LIVE_BEFORE.json`, `LIVE_AFTER.json` und `RESOURCE_DIAGNOSTIC.json` dokumentieren Erhalt und Browsergrenze.

Werkzeuge: `tools/radiworks_vector_21m_probe.py` und `tools/summarize_radiworks_vector_probe.py`. Ein erneuter Langlauf startet wieder ausschließlich eigene Testprozesse; er ist kein normaler Wiederaufnahmeschritt und ersetzt keine Freigabe. Kandidatenbelege: `runtime/rw-gv-binding-20261003/progress-fix-tests.xml`, `progress-fix-browser.log` und `VECTOR_VERIFY.json`.
