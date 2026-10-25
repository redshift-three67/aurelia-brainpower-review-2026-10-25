# RadiWorks: Einstellungen, Area und Peggotty — 02.10.2026

**Nachtrag 03.10.2026:** Peggotty-Fix ist inzwischen in Quelle und laufender Engine nachgewiesen: Bytevergleich mit der Testkopie und HTTP-422-Duplikatprobe auf 8103/8106. Die nachstehenden Übernahmegrenzen beschreiben den historischen Stand vom 02.10. [Aktueller Nachweis und Restplan](RADIWORKS_SIEBEN_INSTANZEN_CHAT_NETZWERK_2026-10-03.md).

**Status:** Die vom Betreiber bestätigte Fallfokus-/Datenbanksuche-Probe ist lokal abgenommen. Die neuen Einstellungs- und Area-Ansichten sind in der RadiWorks-Webquelle und werden auf Port 8103 ausgeliefert. Die Peggotty-Engine-Korrektur ist vollständig isoliert getestet, aber wegen laufendem Auto-Modus **noch nicht** in den 8103-Prozess übernommen. Keine Aurelia-Integrationsfreigabe.

## Geprüfte Änderungen

- Die Einstellungsseite erklärt alle elf derzeit gelieferten Boolean-Werte und `entropy.defaultMode` in Alltagssprache. Sie unterscheidet aktive Wirkung von derzeit nur gespeicherten Original-Schaltern. API-Schlüssel, Werte und GET/PUT-Speichervertrag bleiben erhalten. Nach erfolgreichem Speichern wird der Binaural-Schalter in der Broadcast-Ansicht synchronisiert.
- Area hat zusätzlich zum bestehenden numerischen Scan ein getrenntes 31 × 12-Farb-Overlay über einem lokal gewählten Bild. Erzeugen, Verstärken und Zurücksetzen wurden mit einem künstlichen SVG im isolierten Browser geprüft. Die Zufallsquelle ist `crypto.getRandomValues` im Browser, **nicht** der Hotbits-Handler des Originals. Die Ansicht beeinflusst weder GV noch Fall noch Broadcast. Der numerische 16 × 10-Scan funktionierte nach dem Overlay-Test weiterhin.
- Das Original verwirft doppelte Peggotty-Skriptmarken. Der bisherige Python-Port überschreibt die erste Marke stillschweigend. Die isolierte Korrektur verwirft den Auftrag vor Ausführung mit HTTP 422 und lesbarer Zeilenangabe; gültige Skripte bleiben lauffähig. Die Änderung liegt unter `runtime/rw-peggotty-20261002` und ist nicht in der produktiven RadiWorks-Quelle.

## Nachweise und Übernahme

- Isolierte Browserprobe auf Port 8107: Einstellungen geladen, Binaural-Wert gespeichert und in Broadcast synchronisiert; Area-Bild geladen, Overlay erzeugt/verstärkt/zurückgesetzt und numerischer Scan erneut erfolgreich. Die 390-px-Ansicht wurde visuell geprüft. JavaScript-Syntaxprüfungen bestanden.
- Vollständige Engine-Suite mit Peggotty-Korrektur in kompletter Testkopie: **292 bestanden, 2 umgebungsabhängig übersprungen**. Zuerst meldete die unvollständige Testkopie vier fehlende Dateien; nach Ergänzung von `run.py` und `webapp` bestand die komplette Suite. Keine Testdaten aus dem laufenden 8103-Fall wurden verwendet.
- [Webapp-Manifest](../../runtime/rw-settings-help-20261002/promotion-manifest.json): fünf geprüfte Dateien, Vorher-/Nachher-SHA-256 und [Wiederherstellungspunkt](../../checkpoints/radiworks-settings-area-20261002-before). Die fünf von 8103 HTTP-ausgelieferten Bytesätze stimmten nach der Übernahme mit der Testkopie überein. Der 8103-Prozess wurde nicht neu gestartet.
- Lesende 8103-Nachprobe: Dienst erreichbar, Einstellungen mit elf Schaltern, drei gespeicherte Fälle, 123 Datenbanken; Auto-Modus und vier virtuelle Broadcasts waren aktiv. Der Draft-Zähler stieg während Auto-Betrieb von 51 auf 56. Die Live-Einstellungen, Fallakten und Queue wurden nicht verändert.
- Die drei RadiWorks-bezogenen `Modul_Templates`-Referenzen wurden aus einer hashgeprüften Vorlage aktualisiert; [Manifest](../../runtime/rw-settings-help-20261002/templates-manifest.json) und [Vorher-Bytes](../../checkpoints/radiworks-settings-template-20261002-before) sind gesichert. Gemeinsamer API-Vertrag und Reifegrad-Regeln blieben unverändert.

## Offene Grenzen

1. Peggotty-Engine-Korrektur erst nach Auto AUS und leerer Queue hashgesichert in Quelle übernehmen und 8103 kontrolliert neu starten. Bis dahin gilt im laufenden Prozess das bisherige Peggotty-Verhalten.
2. Reale Kamera, Entropiequalität und persistenter Stochastic-Wiederherstellungsschlüssel auf der Zielumgebung bleiben separat zu prüfen. Die lokale Browser-Farbansicht ersetzt diese Nachweise nicht.
3. Mehrere unabhängige Aufträge pro Fall, Host-/Mandantenisolation, Rechte, WCAG-Gesamtabnahme und Aurelia-S4.8-Entscheidung sind offen. Der gemeinsame `API_CONTRACT.md` v1 wurde nicht verändert.

| Phase | Planungsstand | Nächster Nachweis |
| --- | ---: | --- |
| S4.6 Analyse, GV, Bedienung | ca. 98 % | verbleibende Betreiber- und Grenzproben |
| S4.7 Originalnähe und Restfunktionen | ca. 93 % | Peggotty-Übernahme, reale Kamera und Recovery-Umgebung |
| Fokus und Datenbanksuche | 100 % lokal | Betreiber bestätigte durchgängige Funktion; Host-Gate getrennt |
| Einstellungen und Area-Overlay | 100 % technisch lokal | Betreiberansicht nach bewusstem Neuladen von 8103 |
| Peggotty-Duplikatgrenze | 90 % | 292/2 Tests; Quelle/Prozess noch alt |
| Modul_Templates-Referenzen | 100 % lokal synchronisiert | Host-/ABI-Entscheidung weiterhin offen |
| S4.8 Aurelia-Integration | 0 % | Host-, Scope-, Rechte- und Betreiberentscheidung |

Prozentwerte sind Arbeitsplan-Näherungen, keine Testabdeckung oder Freigabe.
