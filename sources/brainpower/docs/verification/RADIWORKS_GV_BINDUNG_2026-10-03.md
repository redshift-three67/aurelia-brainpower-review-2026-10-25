# RadiWorks: erster Pilot für eine eindeutige GV-Verlaufszuordnung

Stand: 03.10.2026, 23:00 Uhr Europe/Berlin. Ausschließlich isolierter Kandidat; keine Übernahme oder Integrationsfreigabe.

## Ergebnis

Der Kandidat `runtime/rw-gv-binding-20261003` ergänzt freigegebene Draft-Broadcasts um einen geprüften Fall-, Sitzungs-, Draft-, Revisions-, Analysehash- und ursprünglichen Ratenindex-Bezug. Die Metadaten gelangen unverändert in Queue-, Fortschritts- und Resonanzereignisse. Sortierung oder identische Ratenbezeichnungen ändern die Zuordnung nicht. Es werden keine zusätzlichen GV-Werte gezogen und keine Originalwerte verändert.

Eine fehlende, kopierte, mehrdeutige oder veraltete Herkunft verhindert ausschließlich die neue Bindung; der vorhandene Freigabe-/Broadcast-Weg bleibt erhalten. Direkte und Auto-Broadcasts erhalten keine erfundene Fallzuordnung. Die Bindung ist noch kein periodischer Beobachtungsauftrag.

Die API prüft die gespeicherte Sitzung unter der bestehenden Stick-Pad-Transaktions- und Promotionssperre. Die unabhängig aus dem serverseitig gespeicherten ursprünglichen `draft.focus.case` abgeleitete Fallreferenz muss zum aktuellen gespeicherten Fall passen. Ein gefrorener Validator und eine gegen Neuzuweisung/Löschung geschützte Entry-Eigenschaft halten die Bindung fest. Öffentliche Payloads sind Kopien. Der zusätzliche Batch-Vertrag lehnt ungültige Metadaten vor Teilannahme ab.

## Prüfung und Review

- Neue Verhaltensprüfungen wurden vor den jeweiligen Korrekturen rot ausgeführt. Die finale vollständige Suite enthält **68 Bindungsprüfungen**.
- Finale Engine-Suite: **360 bestanden, 2 übersprungen, 0 Fehler**. Die zwei Windows-Symlink-Prüfungen benötigen ein hier nicht vorhandenes Recht. Eine vorhandene Starlette/httpx-Deprecation-Warnung bleibt.
- Isolierter sichtbarer Chrome-/Playwright-Lauf: **22/22 PASS-Abschnitte**, Exit 0 und Cleanup. Geprüft wurden unter anderem Analyse, Draft-Freigabe, virtuelle Queue, geschützte Fälle, Stick-Pad, spätere GV-Seiten, schmale Ansichten und WebSocket-Wiederverbindung. Ein separat vergebener Loopback-Port und ausschließlich synthetische Daten wurden verwendet; keine Kamera aktiviert.
- Der erste Browserlauf scheiterte an einer veralteten Text-Erwartung zu `dynamic.adjustments`. Nur der Kandidaten-Test wurde auf die vorhandene Erklärung und den Status „Derzeit nur gespeichert“ angepasst; die Oberfläche blieb unverändert. Der zweite Lauf bestand vollständig.
- Astra fand zunächst eine falsche Zuordnung bei einer nach Fall B kopierten Sitzung sowie einen optionalen Bindungsfehler bei ungültigem Fall-JSON. Beide wurden mit Regressionstests behoben. Die Nachprüfung fand zusätzlich die mögliche Löschung der Entry-Bindung; auch diese ist getestet und korrigiert. Astra bestätigte die Korrekturen statisch, führte selbst keine Tests aus.

Nachweise: Kandidaten-Dateien `BASELINE.json`, `VERIFY.json`, `test-results.xml`, `browser-smoke.log`. `targeted-results.xml` dokumentiert den früheren Zwischenstand mit 67 Zieltests; der finale XML-Vollnachweis enthält zusätzlich die Löschprüfung.

## Erhaltene Live-Funktionen

**134/134 geprüfte Originalquelldateien** sind weiterhin bytegleich zur Ausgangsbasis. Im Kandidaten änderten sich drei vorhandene Python-Dateien und der Browser-Test; hinzu kamen der Validator und zwei Testdateien. Die Webapp wurde nicht verändert. Live-Prüfung: alle sieben `/ping`-Antworten `pong`, Listener-PIDs weiterhin 64344, 22064, 69908, 24552, 69960, 50748 und 23764 für 8103–8109. Kein Neustart, Stop oder neuer Live-Auftrag.

## Nächster Block und Grenzen

Als Nächstes erst im Kandidaten: getrennte Entropie für Beobachtungen, ausdrücklich aktiviertes 1260-Sekunden-Intervall, Fake-Clock-Tests für Stop/Ende/Fallwechsel, additive Sitzungshistorie und nachvollziehbare numerische Trendklassen. Historie und Anzeige dürfen bestätigte 21er-Werte nicht überschreiben. Für dauerhafte Historien muss die bestehende **prozessgebundene** HMAC-Fallreferenz noch um einen geprüften Wiederanlaufvertrag ergänzt werden; sie ist allein keine dauerhafte Fallidentität.

Die Dauerinstanzen, ihre derzeitigen Broadcasts und Originalwerte bleiben im jetzigen Funktionsstand. Kamera-/Stochastic-Langlauf, echte Windows-Neustart-/Anmeldeprobe, Aurelia-Host-/Mandantenvertrag und S4.8 bleiben offen. Entropiebasierte GV-Verläufe belegen keine gesundheitliche Verbesserung oder Verschlechterung.

| Teilpaket | Fortschritt | Aussage |
| --- | ---: | --- |
| GV-1: eindeutige Zuordnung | 100 % | begrenzter Pilot isoliert geprüft; nicht live übernommen |
| GV-2: 21-Minuten-Abfrage und Historie | 0 % umgesetzt | nächster Kandidatenblock |
| Sieben Dauerinstanzen | eingerichtet | alle erreichbar; praktische Warmstartprobe offen |
| Reale Kamera/Stochastic | offen | separate Probe mit geeigneter Kamera |
| S4.8: Aurelia-Integration | 0 % | keine Freigabe |

Prozentangaben beschreiben die genannten Arbeitspakete, keine Testabdeckung oder Gesamtreife. Tatsächlich beteiligt: **GPT-6.1 Sol/high** für Integration und Prüfung, **GPT-6 Luna/max** für den begrenzten Validator samt Tests, **GPT-6 Astra/medium** für die unabhängige Grenzprüfung. Keine gemessene Kostenersparnis; keine Änderung der Hermes-Anwendungsrouten.

Begrenzter Wiederherstellungspunkt: `checkpoints/radiworks-gv-binding-20261003-230335`; vor einer Rückkopie `RESTORE.md`, `MANIFEST.json` und `VERIFY.json` prüfen. Keine Sicherung aktiver Laufzeitdaten.
