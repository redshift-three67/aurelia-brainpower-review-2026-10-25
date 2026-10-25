# Wiederherstellungspunkt: Pause vor Quellenabgleich und aktuellen Produkttests

Stand: 12.09.2026. Arbeitsverzeichnis: C:/Users/Hubert111/Documents/Brainpower.
Checkpoint: checkpoints/2026-09-12_PAUSE_QUELLENABGLEICH.

## Verbindliche neue Betreiberangaben

1. Auf dem Server sind laut Betreiber täglich Backups vorhanden. Das ist eine Betreiberangabe; Umfang, getrennte/offline Kopien und erfolgreiche Wiederherstellung sind noch nicht technisch nachgewiesen.
2. Neue Tests auf dem aktuellen Projektstand sind zwingend. Historische Testzahlen ersetzen keine aktuellen Nachweise.
3. Maßgeblich für die Produktfunktionalität ist der Ubuntu-Server, der die Webanwendung liefert. Windows bleibt separat die Umgebung für Governor/Hermes/Installer; dessen Prüfungen ersetzen keine Ubuntu-Produktabnahme.
4. Bei mehreren Lösungen prüft das System deren Akkuranz und empfiehlt eine begründete Variante. Der Betreiber entscheidet final, welche Lösung ausgeführt wird.
5. Der Betreiber folgt dem vorgeschlagenen Vorgehen: zuerst Quellen-/Gateabgleich und Prüfung; anschließend nur verbleibende Entscheidungen tabellarisch vorlegen. Keine erneute Grundsatzfreigabe für den Abgleich erforderlich.

## Exakter Pausenstand

Governor 0.5.0 wurde vor Sicherung über die lokale API erreicht. Supervisor Sol; lokale Beobachtung an; automatische Modellreviews aus; keine laufenden, wartenden oder eingereihten Aufträge beim Kontrollabruf. Diese Einstellungen nicht durch die Wiederaufnahme automatisch ändern.

Die vier Aufnahmefelder je Projekt wurden in verständliche Markdown-Tabellen überführt. Maßgebliche Lesefassung: artifacts/AUFNAHMEFELDER_ZUSAMMENFASSUNGEN.md. Vollständiger Originalwortlaut und Quellenbindung: artifacts/AUFNAHMEFELDER_ZUR_PRUEFUNG_2026-09-12.md und artifacts/aufnahmefelder-tabellen-basis.json.

Die fünf Aufnahmen waren beim letzten Aufnahmeabgleich aktuell, bleiben aber unbestätigte Entwürfe. Die jüngsten Betreiberangaben sind hier dokumentiert, noch nicht als bestätigte Aufnahme oder Gateabnahme im Governor-Journal eingetragen. Keine Matrixstrategie oder Produktumsetzung wurde durch die Tabellen freigegeben. Seit deren Erstellung wurden keine neuen Produktprüfungen, Modellreviews oder Servereingriffe ausgeführt.

Der frühere technische Implementierungsstand bleibt in project_memories/IMPLEMENTATION_0_5_2026-09-12.md dokumentiert. Allgemeine Produktausführung, automatische Schrittfolgen und vollständige Windows-Nullinstallation bleiben offen. Der bisherige begrenzte Hybridnachweis ist kein Beweis vollständiger Produktprüfung oder genereller Modelloptimalität.

## Fortsetzung in vereinbarter Reihenfolge

| Priorität | Prüfung | Empfehlung / Entscheidungsgrenze |
|---|---|---|
| 1 | Aurelia: vorhandene Sicherungs-/Restore-Nachweise erfassen. | Isolierten Restore-Test konkret vorbereiten. Keine Wiederherstellung über produktive Daten. Betreiber nimmt Nachweis und nötige Konzeptänderungen ab. |
| 2 | Ubuntu-Zielumgebung: Zugriff, Dienste, Datenbank, Rechte, Startwege und Projektversionen feststellen. | Bestehende Zugänge prüfen, keine Anmeldedaten ausgeben. Fehlenden Zugriff konkret benennen. Serveränderungen separat vorlegen. |
| 3 | Alle fünf Projekte: Code-/Gedächtnis-/Git-Stände und Gate-/Betreiberentscheidungen abgleichen. | Aktuelle Bytes, Index und HEAD trennen; WIP erhalten. Quellen exakt binden. Widersprüche nicht durch Vermutungen auflösen. |
| 4 | Aktuelle Testpläne je Projekt und neue Tests. | Zuerst festhalten, welche Tests lokal und welche unter Ubuntu nötig sind. Isolierte sichere Prüfungen im genehmigten Umfang; produktiv wirksame Tests vorher konkret vorlegen. |
| 5 | Modul_Templates: gemeinsame Schnittstellen und Vertragsvarianten prüfen. | Korrektheit, Kompatibilität, Prüfbarkeit und Folgekosten vergleichen; Betreiber wählt bei echten Alternativen. |
| 6 | RadiWorks: lesenden Integrations-/Vertragsabgleich und unabhängige Prüfung erstellen. | Priorisierter Modulschritt; nicht auf Morphic warten. Technische Integration benötigt eigene Voraussetzungen und Freigabe. |
| 7 | Radi144-Checkpoint/Gates und Morphic-Autoritäten prüfen. | Eindeutige Baselines und passende aktuelle Tests; Stilllegungen, Funktionsgrenzen und fachliche Varianten zur Entscheidung vorlegen. |
| 8 | Geprüfte aktuelle Befunde hybrid bewerten und Matrixvorschlag erstellen. | Erst bestätigte aktuelle Aufnahmen und passende Voraussetzungen. Terra/Sol bzw. Terra/Astra, nachvollziehbare Prioritäten/Abhängigkeiten. Betreiber nimmt Plan und konkrete Umsetzungsschritte an. |

Die Reihenfolge ist ein Prüfplan. Unabhängige lesende Prüfungen können parallel bearbeitet werden; fehlende Restore-Evidenz blockiert nicht pauschal einen erlaubten lesenden Vertragsabgleich. Produktgates gelten schrittbezogen.

## Wortlaut für die Wiederaufnahme

> Wir setzen genau am Pausenstand vor dem Quellenabgleich und den neuen Produkttests fort. Lies project_memories/PAUSE_QUELLENABGLEICH_2026-09-12.md, WIEDERAUFNAHME.md, docs/GOVERNOR_0_5.md und docs/LLM_OPERATING_CONTRACT.json vollständig. Prüfe den aktuellen Zustand gegen checkpoints/2026-09-12_PAUSE_QUELLENABGLEICH, ohne Dateien zurückzuspielen oder Änderungen zu überschreiben. Tägliche Serverbackups sind von mir bestätigt, ein Restore ist noch nachzuweisen. Neue Tests sind Pflicht; die Produktabnahme richtet sich nach Ubuntu. Prüfe Lösungsvarianten und empfehle eine begründet; ich entscheide die Umsetzung. Beginne mit dem Quellen-/Gateabgleich und der Erfassung der lokal beziehungsweise unter Ubuntu erforderlichen Tests. Lege mir danach nur verbleibende Entscheidungen mit Befund, Empfehlung und Auswirkungen vor. Aufnahmen und Produktgates nicht stillschweigend bestätigen. Automatische Reviews nicht allein durch die Wiederaufnahme aktivieren.

## Umfang und Wiederherstellung

Dies ist ein lokaler Workbench-Checkpoint mit Programm, Konfiguration, Dokumentation, konsistenter SQLite-Journalsicherung und ausgewählten Gesprächsartefakten. Kein vollständiges Backup der fünf externen Produkte, des Ubuntu-Servers, von Hermes/CC Switch oder Zugangsdaten. Der ältere D:-Backupstand wird hierdurch nicht aktualisiert.

Zur normalen Fortsetzung nichts zurückkopieren. Bei tatsächlichem Verlust zunächst Dienst stoppen, aktuellen Restbestand separat sichern und das gesicherte Programm/Journalsystem gemeinsam in ein frisches Verzeichnis übernehmen. Pfade und externe Installationen prüfen. Keine alten WAL-/SHM-Dateien mit dem gesicherten journal.db kombinieren. Das Manifest dient der Integritätsprüfung. Die Daten sind lokal und enthalten Projektinformationen; kein öffentliches Installationspaket.
