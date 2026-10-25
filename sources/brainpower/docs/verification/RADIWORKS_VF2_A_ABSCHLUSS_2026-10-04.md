# RadiWorks VF2-A: Backend-Kontext und Auftragsbindung

Stand: 2026-10-04T22:09:30+02:00. **100 % des abgegrenzten Backend-Pakets**, keine vollständige VF-2-/Modul-/Integrationsfreigabe.

## Ergebnis und Nutzerwirkung
- Getrennte persönliche Angaben im Backend: Vorname, Nachname, Geburtsdatum, Ort; bestehende Fallbezeichnung, Beschreibung und Fokus bleiben erhalten. Strenge Typ-, Längen-, Unicode- und Datumsprüfung; persönliche Angaben werden nicht aus alten Dateinamen abgeleitet.
- Feste serverseitige Fall-ID und steigende Kontextversion. Explizites Umbenennen hält Datei, ID und bestehenden Fallverweis; eine vollständige Fallkopie erhält eine neue ID und unveränderte historische Herkunft.
- Neue fallgebundene Analysen speichern den damaligen Kontext getrennt in Sitzung und Draft. Spätere Falländerungen ändern diesen Stand nicht. GV-Folgesitzungen erben den exakten Elternstand, auch bei Fallkopien.
- Beim ausdrücklichen Promote erhält die virtuelle Queue ausschließlich eine unveränderliche Kontextreferenz, keine vollständigen persönlichen Daten. Bestehende Signatur-/Zeit-/Zahlenberechnung unverändert.
- Alte Sitzungen bleiben historisch ungebunden. Schreibversuche, ihren Kontext nachträglich zu ergänzen, zu ersetzen oder zu entfernen, werden abgewiesen.
- Der bereits vorhandene direkte GV-Helfer wurde angeglichen. Die ältere falsche Argumentposition im geplanten GV-Fork ist durch einen Gegenbeispieltest korrigiert: Entropiecheckpoint statt unbeabsichtigter Draft-ID.

## Verifikation
| Prüfung | Nachweis |
|---|---|
| Ganze Engine, endgültiger Stand |468 bestanden,3 bekannte Windows-Symlink-Skips,0 Fehler/Fehlschläge;471 erfasst|
| Neues Kontext-Testmodul |37 bestandene synthetische Fälle einschließlich Negativ-, Legacy-, Kopie-, Versions-, GV- und Promote-Prüfungen|
| Abschließende Playwright-Browserregression |22/22 Abschnitte auf zugewiesenem temporären Loopback-Port; keine JS-Seitenfehler|
| Gepinnter GV-2-Elternkandidat |103/103 Hashes unverändert|
| VF2-Kandidat |105 Dateien gepinnt;5 bestehende Engine-Dateien geändert,2 neue Dateien|
| Webapp und Rechenkerne |23/23 Webapp-Dateien und5 explizit geprüfte Zahlen-/Entropiekerne unverändert; gleicher Original-Seed trotz geändertem persönlichen Kontext getestet|
| Dauerinstanzen und Pilot |8103–8109 sowie8110 weiterhin Loopback, gleicher PID und pong; keine Starts/Stops/Taskänderungen|
| Referenzquellen |Gepinnte Aurelia-/Template-/Radi144-Referenzen erneut bytegleich; keine kanonische Übernahme|
| Unabhängiger Review |Astra: aufgeführte Befunde geschlossen, keine weiteren konkretenP1/P2 im abgegrenzten Umfang; Gesamtsuite vom Root ausgeführt|

Belege unter `runtime/rw-vf2-20261004/`: `vf2-engine-verified.xml/log`, `vf2-browser-verified.log`, `vf2-clone-fork-green.xml/log`, ursprüngliche RED/GREEN-Gegenbeispiele, `FINAL_VERIFY.json`, `REVIEW.json`, `PRODUCT_MANIFEST.json` und `PRODUCT_DIFF.patch`.
Die Starlette/httpx-Deprecation-Warnung bleibt. Kein neuer Linux-/Windows10-/Hardware-/Kamera-/bezahlter Hermes-Modelllauf.

## Grenzen
- Kein Originalalgorithmus nutzt diese persönlichen Metadaten als zusätzliche numerische Gewichtung. Eine solche Wirkung wird nicht behauptet; EXP-1 ist separat.
- Bild unterstützt hier nur validierte Referenzmetadaten (SHA256, Typ, Byteanzahl). Noch kein Bild-Upload, sichere Bilddecodierung oder Browserfeld. Dateiendung/Hash beweist keinen Bildinhalt.
- Auto-, direkte und Bild-Broadcasts sind ohne separat implementierte Herkunft weiterhin ungebunden; kein stillschweigendes Zuordnen zum aktuellen Fall.
- Die lokale SHA256-Prüfung dient Integrität/Provenienz, nicht als Signatur gegen einen Angreifer mit Vollzugriff auf Dateien. Validierte API-Schreibpfade erhalten die Historie.
- Legacy-Verweise verwenden weiterhin den pro Prozess erzeugten HMAC-Schlüssel. Die neue Fall-ID ist dauerhaft; der alte HMAC-Link wird dadurch nicht restartfest.
- Neue Felder sind **noch nicht in8110 oder8103–8109 sichtbar**. Browserstand unverändert; keine Migration realer Falldaten, Keys oder laufender Jobs.
- Originalbefunde, Testalgorithmen und GV-Verläufe belegen keine medizinische Wirkung.

## Phasenstand und nächste Schritte
| Paket | Stand |
|---|---|
| VF2-A Kontext-/Identitäts-/Auftragsvertrag Backend |100 % des geprüften Pakets|
| VF2-B persönliche Browserfelder und sicheres optionales Fokusbild |0 % Umsetzung; nächster Block|
| VF3 erklärbare heuristische Datenbankvorschläge |0 % Umsetzung, genehmigt|
| EXP1 separat wählbare Radi144-Heuristik |0 % Umsetzung, genehmigt|
| Weitere Echtzeit-Trend-, Kamera-/Recovery-, Area-/Peggotty- und Bedienabnahme |offen; frühere Einzelbelege gelten nur für ihren Quellstand|
| Kanonische RadiWorks-/Modul_Templates-Abstimmung |Delta vorbereitet, Übernahme offen|
| Windows10 Standalone mit bis5 isolierten Instanzen |noch nicht gebaut; nach integrierbarem Prototyp und Abnahme|
| Vollständige Governors/Aurelia/Module/Konfigurationen/Sessionhistorien-Sicherung aufF: |noch nicht aktualisiert; nach Paketprüfung und konsistentem Export|
| AureliaS4.8 |0 % Freigabe|

Die Prozentwerte gelten für die genannten begrenzten Pakete, nicht für eine Gesamtproduktionsreife.
Nächster Block VF2-B: explizite zugängliche Felder, originaler Falltext erhalten, sicheres optionales lokales Bild, verständliche Validierung und Neustart-/Browserprüfungen. Orientierung etwa1–2Stunden, bei Befunden länger; kein Zeitlimit.
Danach VF3 → EXP1 → Restprüfungen/Betreiberabnahme → Quellen/Templates → versioniertes Win10-Testpaket → vollständige zeitgestempelte Sicherung mit Wiederherstellungsprobe → Radi144. S4.8 separat.

## Modelle
Gewählte Chatleitung Sol6.1/high; Root implementierte und führte Prüfungen aus. Tatsächlich verwendet: Luna6/max für begrenzten lesenden Vertragsabgleich, Astra6/medium für unabhängige kritische Grenzprüfung. Keine gemessene Token-/Kosteneinsparung. Dies ändert keine Governors/Hermes-Anwendungsroute.

## Begrenzter Wiederherstellungspunkt
`checkpoints/RadiWorks-VF2-A-20261004-220930`:105 Kandidatendateien, Nachweise, Bericht/Plan/aktueller Einstieg und Hilfswerkzeuge mitSHA256-Manifest. Keine realen/synthetischen Homes, Keys, Tokens, venv, Caches oder temporären Testdaten. Kein Ersatz für die noch geplante vollständigeF:-Sicherung. Wiederherstellung zunächst ausschließlich in neues isoliertes Verzeichnis; keine automatische Übernahme in Dauerinstanzen.

## Nachtrag 04.10.2026 — Browser-Quellbindung korrigiert
Der folgende VF2-B-Block zeigte: Der alte Browserhelfer importierte die installierte Engine statt des VF2-A-Kandidaten. Die oben berichteten 22 grünen Abschnitte sind kein Backendnachweis. Korrekt gebundene 468 Engine-PASS bleiben gültig. Der frische VF2-B-Gegenlauf mit 494 Engine-PASS/3 Windows-Skips und 28 Browserabschnitten mit ausdrücklicher sys.path-/__file__-Prüfung ersetzt den unzureichenden Beleg. [Aktueller Bericht](RADIWORKS_VF2_B_ABSCHLUSS_2026-10-04.md). Früherer Checkpoint unverändert historisch.
