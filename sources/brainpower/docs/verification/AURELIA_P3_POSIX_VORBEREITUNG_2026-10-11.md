# P3 – POSIX-Prüfvorbereitung und aktueller Anlaufblocker

Stand: 11.10.2026. **Statische Aufnahme abgeschlossen; null Produktmodule und null POSIX-Tests ausgeführt.** Die tatsächliche Linux-Ablehnungs-/Cleanup-Prüfung bleibt offen.

| Teil | Ergebnis und Grenze |
|---|---|
| Quellenvertrag | Zehn notwendige Module des bestehenden Windows-Loadervertrags frisch aus zwei Byte-Reads gebunden; HEAD/tracked-only und Basishashes geprüft. Migration bleibt außerhalb dieses Blocks |
| POSIX-Guard | Originaler Link-/Replace-Pfad verweigert unter POSIX die Publikation; statisch verfolgt, nicht auf Linux ausgeführt |
| Öffentliche Wege | Vorbereiteter Vertrag für Backup/Restore und Bereinigung eigener temporärer Dateien/FDs. Erreichen des Guards setzt erfolgreiche Vorprüfungen/Snapshotgates voraus; tatsächliches Cleanup nicht bestätigt |
| WSL-Anlauf | Inventur erfolgreich: `Ubuntu-24.04` und `Aurelia-Referenz-24.04`, beide WSL2/Stopped. Start der Referenzprobe scheitert vor Python mit `Wsl/Service/CreateInstance/CreateVm/HCS/0x800705aa` |
| Hostdiagnose | Zusätzlich scheitert eine erhöhte CIM-Abfrage an CoreCLR-/GC-Initialisierung `0x80004005`; daraus keine CIM-Speicherwerte gewonnen |
| Direkte Zähler | Rein lesendes `GlobalMemoryStatusEx` funktioniert. Beim beobachteten ersten Snapshot rund 3,52 GiB verfügbarer physischer RAM und 1,32 GiB verfügbarer systemweiter Commitrahmen. Point-in-time; kein identifizierter Kausalprozess |

Die `pagefile`-Feldnamen stammen aus der WinAPI-Struktur und bezeichnen Commit-bezogene Grenzen/Verfügbarkeit, keine Größe oder freien Datenträgerplatz einer einzelnen Auslagerungsdatei. Die Ressourcenknappheit ist mit den Startfehlern vereinbar; genaue Ursache und erforderliches WSL-Budget sind nicht bewiesen. Der Sicherungspunkt enthält einen zweiten automatisch erfassten Speicherschnappschuss als `MEMORY-readback.json`; beide Zeitpunkte getrennt betrachten.

`OBSERVED_ENVIRONMENT.json` ist ausdrücklich eine Root-Transkription der Toolausgaben, kein automatisch gespeichertes Prozessrohprotokoll. Die Angaben zu unterlassenen Eingriffen dokumentieren den Arbeitsablauf; sie sind keine unabhängige OS-Attestierung. Die direkte Speicherprobe liest nur Zähler. Keine Prozessbeendigung, Änderung von Auslagerungsdatei/RAM/WSL, globales Shutdown, ursprüngliche Ubuntuänderung oder Liveinstanzänderung durch diesen Block.

## Geplanter tatsächlicher Nachweis

Nach tragfähigem Anlauf: Python und ext4-Scratch prüfen, begrenzten bytegebundenen Loader ohne Produktinitialisierer/Defaults vorbereiten und vor Ausführung unabhängig prüfen lassen. Fünf negative Proben: direkter Link, direkter Replace, Publish ohne Überschreiben, öffentliche Backuperstellung und öffentliche Wiederherstellung. Vorhandene Ziele, unveränderte synthetische Eingaben, Dateideskriptoren, temporäre Datenbank-/Journal-/WAL-/SHM-Dateien getrennt kontrollieren. Zwei frische Läufe mit exakten Namen und unabhängiger Artefaktnachrechnung. Keine Umgehung des Originalguards, keine positive Linux-Publishabnahme aus erwarteter Ablehnung.

Der statische Plattformbefund ist für P4 relevant: dieser originale Publikationspfad ist unter POSIX absichtlich gesperrt. Ein späterer produktiver Linux-Publishadapter braucht eigene Planung, Freigabe und Tests; er wird jetzt nicht implementiert. Zentraler Datenbankentscheid P5 und normative Aurelia-/Modul_Template-Anpassungen bleiben getrennt.

## Review und Sicherung

GPT-6 Luna/max: begrenzte statische Quellen-/Guardaufnahme. GPT-6 Astra/medium: unabhängiger SPEC→QUALITY-Review von Vertrag, Diagnose, Abschlusswerkzeug und Aussagegrenzen; keine Produkt-/Linuxausführung. Leitung prüft aktuelle Quellenbytes und frühere 133 Manifestdateien, erstellt Vorher-/Nachherdokumentstand und erhält die vollständige historische Wiederaufnahme als Bytesuffix. Historische Manifestbytes werden zusätzlich zwischen prepare und final gebunden. Hashkonsistenz ist keine externe Authentizitätsgarantie oder kontinuierliche Überwachung.

Lokaler Prüfpunkt `checkpoints/Aurelia-P3-POSIX-Status-20261011-195451Z`. Das Abschlussmanifest und `ROOT-after.json` werden erst vom tatsächlich erfolgreichen final-Lauf samt Readback bestätigt; dieser Bericht allein bestätigt keine Versiegelung. Keine komplette Projekt-/Server-/F:-Sicherung, kein Kamera-, Cloud-, Access- oder Applikationsfunktionstest.

P0/P1/P2, RF-E1 und übrige P3-Verträge bleiben offen. Weiter tatsächlichen POSIX-Nachweis unter tragfähiger Umgebung und unabhängige Registry-/Writer-/Job-/RMF-Prüfungen; danach P4 vollständige siebenmodulige Matrix mit Aurelia/Modul_Templates, erst P5 zentrale Datenstrukturentscheidung. Quellenvertrag: `checkpoints/Aurelia-P3-POSIX-Sources-20261011/CONTRACT.md`; Beobachtungen: `checkpoints/Aurelia-P3-POSIX-Tests-20261011/OBSERVED_ENVIRONMENT.json`.
