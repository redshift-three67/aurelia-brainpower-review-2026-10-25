# Schlüsselverwahrung und Ausfallüberwachung – 23.09.2026

## Nachweise

- Betreiber bestätigt heute: Archivpasswort, LUKS-Passphrase und SMB-Zugang außerhalb des Servers verfügbar. Keine Geheimnisse angefordert oder ausgegeben.
- Historischer Export19.09.: Restic-Schlüssel extern/servergleich geprüft; SHA25670f076532265546d1283105d0efb371e1d30d4cc94df4abe8132c88d9d4a2ad9, Quelle WIEDERAUFNAHME.md Abschnitt Externe Schluesselkopie verifiziert. Der geprüfte Vorbereitungshelfer23.09. verwendet denselben alten Schlüssel für das aktuelle Operations-Repository; keine Neuerzeugung. Aktueller Backup-/Restorebetrieb funktioniert mit der Serverkopie.
- E:/Aurelia-Recovery/Aurelia-Recovery.zip vorhanden. SHA2561ae0bc8d0777ee2623e0a7b4dc2920e1a4af6a61b3b19e2418cb5c8968ef7301. Nur ZIP-Verzeichnis gelesen: verschlüsselter Eintrag aurelia-config-449ada54bc1e4de0aefb58dd8d90f5d4.key (65Bytes), verschlüsselte README. Kein Entschlüsseln/Extrahieren; heutige Bytegleichheit des enthaltenen Schlüssels und unabhängiger Restore noch nicht erneut bewiesen.
- LUKS-Header auf E: SHA2564d3509f1b549773ddf24c953853875522478c465d7ec9bb0b1802313a2ea5756 stimmt mit historischem Servernachweis überein. Kein Headerrestore-/Entsperrtest.
- F:/Aurelia-Recovery aktuell nicht erreichbar. Keine zweite Datenkopie erstellt; weiterhin ausdrücklich zurückgestellt.
- Aurelia-Healthtimer active/enabled. Bericht23.09.21:09:01UTC healthy=true, errors/failed_units leer, RAID nicht degradiert, NVMe ohne kritische Warnungen/Medienfehler. Dienst prüft lokal und hat keinen externen Alarmversand. Ein späterer systemctl-Aufruf traf den Dienst während eines regulären Laufs (activating, vorheriges Result=success).
- Betreiber bestätigt: noch keine unabhängige Ausfallüberwachung vorhanden. Bestehende Backup-/Retention-E-Mailalarme laufen auf Aurelia und ersetzen keine externe Ausfallmeldung.

## Nächste Entscheidung

Vorgeschlagen: unabhängiger Empfänger für ausgehende Lebenszeichen alle5Minuten, E-Mailalarm bei Ausbleiben; keine zusätzliche eingehende Portfreigabe. Ausführungsort beim Betreiber angefragt: externer Dienst, vorhandener separater Webserver oder vorerst zurückstellen. Anbieter, Zugang, konkrete Alarmfrist und Umsetzung noch nicht festgelegt; nichts eingerichtet, keine Testmail versandt. Bei Wahl des vorhandenen Mail-/Webservers gemeinsame Provider-/Netzabhängigkeiten berücksichtigen. Keine Zugangsdaten in Chat/Projekt.

Schlüsselverwahrung ist dokumentiert und vom Betreiber bestätigt; kein neuer vollständiger Recovery-/RTO-Nachweis. Rescue und zweite Datenkopie bleiben nach Betreiberentscheidung zurückgestellt. Medium.

## Betreiberentscheidung

Externe Ausfallüberwachung wird später über einen externen Dienst eingerichtet. Jetzt zurückgestellt; keine Anbieter-/Zugangsfrage erneut stellen und keinen Monitor einrichten. Keine vollständige Ausfallalarmierung als vorhanden behaupten.
