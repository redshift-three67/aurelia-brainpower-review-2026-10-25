# RadiFarben RF-E1 – synthetische Access-Import-/Exportprobe

> Ausführung des bereits freigegebenen RF-E1-Kandidaten mit `superpowers:subagent-driven-development`: begrenzter Worker, SPEC→QUALITY-Vorprüfung, danach eigene reale Probe der Leitung. Keine Originalöffnung. Betreiberfortsetzung und RMF-Versionspflege am 11.10.2026 bestätigt.

**Ziel:** In der vorhandenen Access-Version nachweisen, welche selbst erzeugten Formular-/Berichts-/Modul-/Makro-/Querydefinitionen importiert und exportiert werden können, ohne deren Ereignisse im Import-/Exportweg auszuführen.

**Architektur:** Neues exklusives Scratchverzeichnis und eindeutig eigene, verborgene Access-Automationsinstanz. Selbst erzeugte Quelle und frisches Ziel; gespeicherte ursprüngliche RadiFarben-Dateien werden niemals als Access-Eingabe verwendet. Nur synthetische lokale Marker. Keine Office-/Trustcenter-/Windows-/Netzwerkänderung, keine Tabellen-/Link-/Menüübernahme, keine systemweite Ausführungssperre behaupten. Kein Gast und keine OS-Sandbox.

**Technik:** PowerShell, vorhandenes Access-COM-Objektmodell; Standardbibliothek für Quellen-/Dateihashes und Ergebnisprüfung. Kein neues Produktionspaket, keine Installation und kein Governor-Auftrag.

## Dateien und Verantwortung

- Worker exklusiv: `checkpoints/RadiFarben-Access-Synthetic-20261011/` (Probe, Hilfsfunktionen, gezielte Host-freie Prüfungen, Arbeitsnotiz).
- Leitung: Versionsaufnahme/Sicherung, konsolidierter Phasenplan, RF-Referenzdokument, Wiederaufnahme und tatsächliche Ausführung.
- Reviewer: ausschließlich lesender SPEC→QUALITY-Befund auf synthetischem Harness, Ergebnissen und bereinigtem Bericht. Kein Roh-ACCDB-/Definitions-/Klientendatenversand.

## Ausführungsschritte

- [x] 1. Original-/Dokumentstände vor Änderung sichern. Aktuelle und alte ACCDB mit Dateihash getrennt binden; unveränderte Live-Port-/Prozessidentitäten vor/nach prüfen. Keine Ableitung einer Formeländerung allein aus Dateidrift.
- [ ] 2. Exklusive Scratchpfade und Eigentumsprüfung der Automationsinstanz vorbereiten. Vorhandene Access-PIDs erfassen; hWnd der neuen Instanz einer neuen PID/Startzeit zuordnen. Bei Wiederverwendung/unklarem Eigentum ohne Datenbankänderung stoppen, keine fremde Instanz schließen. Neue Instanz muss vor Datenbankaktionen leer sein.
- [x] 3. Host-freie Prüfungen für erlaubte Pfade, vorhandene Ziele, Reparse-/Traversalgrenzen, Fremd-PID/Startzeit und Ergebnisbewertung ausführen. Erst mit roten Proben, dann minimalen Funktionen; Syntax und Quellenhash dokumentieren. Keine Access-Ausführung durch den Worker vor ausdrücklichem GO der Leitung. Endfassung:59 Assertions bei Worker und Leitung, keine Skips/Fehler; statischer Review abgeschlossen, reale COM-/Objektpfade ungetestet.
- [ ] 4. Selbst erzeugte ACCDB: leeres Formular/Report in Designansicht, Modul und feste lokale Marker für Form-/Report-/Timer-/Makro-/Querypfade. Keine Quelle von Hostvorlagen/externen Bibliotheken akzeptieren. AutoExec-Definition nur geschlossen erzeugen/importieren, keine Wiederöffnung einer mit AutoExec versehenen Datei. Alle Markerpfade bleiben im Scratchverzeichnis.
- [ ] 5. Definitionen aus der selbst erzeugten Quelle in ein frisches Ziel importieren; nur Form, Report, Modul, Makro und Query als Query. Keine Datensatz-/Tabellenimporte. Vor/nach jedem Import und SaveAsText auf Marker prüfen. Objektinventar, exportierte Definitionen und Hashes erfassen; Importnormalisierung ausdrücklich zulassen und ausweisen statt Byteparität zu behaupten.
- [ ] 6. Positive Kontrollproben bewusst nur an synthetischen Objekten ausführen: Markermechanismus und tatsächlich ausführbare Event-/Timer-/Querypfade nachweisen. Keine fehlende Markerspur als Erfolg werten, wenn die Kontrollprobe nicht funktioniert oder Code gesperrt ist. Falls ein Objekttyp/Mechanismus nicht verfügbar ist, als offen/fehlgeschlagen erfassen; kein stiller Erfolg.
- [ ] 7. Nur eindeutig eigene Instanz schließen; Kinder-COM-Referenzen lösen, eigene PID/Startzeit und Prozessende nachprüfen. Bei Fehler/Timeout keinen fremden Prozess beenden. Art und Grenze eines gezielten eigenen Prozessabbruchs vor Anwendung prüfen. Alle Erfolgs-/Fehler-/Teilbelege erhalten; kein automatischer Neustart oder unbegrenzter Retry.
- [ ] 8. SPEC→QUALITY-Endreview, eigener Ergebnisvergleich und SHA-Rückleseprüfung. RF-E1 besteht nur im tatsächlich geprobten Umfang mit aktiven Positivkontrollen; Originalimport/-öffnung, ActiveX-/Link-/P-Code-/volle Laufzeitparität bleiben eigene spätere Nachweise.

## Prüfkriterien und Grenzen

**Tatsächlicher Stand11.10.:** Zwei Readiness-Aktivierungsversuche scheitern vor COM-Objekt/DBaktionen (`80080005`). Schritte4–6 nicht ausgeführt; Schritt2/7 als Werkzeuge vorbereitet, aber eigene Instanz-/Datenbank-/Cleanupabnahme nicht erfolgt. Host-freie Prüfungen und statischer Review werden separat abgeschlossen; daraus keine vollständige RF-E1-Abnahme ableiten. Quelle/Masterhashes und acht Listeneridentitäten nachkontrolliert. [Aktueller Bericht](../../verification/AURELIA_P3_RADIFARBEN_SYNTHETISCHE_ACCESSPROBE_2026-10-11.md).

**Vorbereitungsabschluss:**59 Host-freie Assertions und begrenzter statischer Review abgeschlossen. Unbekannte Gesamt-Vorlagenabdeckung blockiert ausdrücklich jede Datenbankanlage. Äußerer Vollharnesscontroller, tatsächlicher COM-Start/Owned-Cleanup, Import/Export und aktive Positivkontrollen bleiben Voraussetzungen/offene Prüfungen. Auch Schritt8 ist damit nur teilweise erfüllt; RF-E1 insgesamt nicht bestanden.

Jeder unterstützte Typ erhält `constructed`, `imported`, `exported`, `definitionMarkerBound`, `unexpectedExecutionAbsent`, `positiveControlObserved` separat. Gesamtstatus besteht nur für explizit ausgeführte und kontrollierte Fälle; ungetestete Typen werden nicht verschluckt. Während reiner Übernahme dürfen keine synthetischen Ausführungsmarker entstehen. Positive Kontrollen erzeugen die erwarteten Marker erst in der ausgewiesenen Kontrollphase.

Access kann lokale Normalisierungs-/Kompilierungseffekte haben. Markerabwesenheit ist ein begrenzter empirischer Befund und keine garantierte Nebenwirkungsfreiheit gegenüber unbekanntem Originalcode. Unterbundene synthetische Codeausführung ist kein Nachweis, dass Originalcode sicher importierbar ist. Die aktuelle Originaldatei bleibt geschlossen.

## RMF-Versionen

Menüpunkt1 ist laut Betreiber die aktuell höchste RMF-Version und weiterhin in Entwicklung. Aktuellen Stand als unveränderliche Ausgangsreferenz sichern; spätere Versionen bis zur Aurelia-Modulintegration als getrennte Kandidaten aufnehmen, technische Unterschiede/Referenzfolgen prüfen und erst nach dokumentierter Übernahme die Arbeitsbaseline wechseln. Alte Aufträge/Belege behalten ihre ursprünglichen Quell- und Algorithmusbindungen. Keinen unbestätigten semantischen Versionswert erfinden.
