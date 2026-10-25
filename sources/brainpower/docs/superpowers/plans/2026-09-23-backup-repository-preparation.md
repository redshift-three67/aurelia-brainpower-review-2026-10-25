# Betriebsrepository vorbereiten – ohne Aktivierung

Betreiber beauftragt Fortsetzung des beschriebenen Einrichtungspakets. RTO vorläufig maximal12h; noch kein gemessener Gesamtrestore. RPO wird vor Aktivierung besprochen. Bestehende Konfigurations-/DB-Backups bleiben unangetastet.

## Abgegrenztes Paket

1. Neuen gehashten Starter und Payload vorbereiten; ausschließlich rootgeschützter exklusiver Arbeitsbereich. Vor Ausführung PGstillstand und disabled/inactive-Backuptimer prüfen.
2. Bestehenden Schlüssel449ada54bc1e4de0aefb58dd8d90f5d4 gegen bekannten alten SMB-Snapshot verifizieren. Kein neuer produktiver Schlüssel, keine Ausgabe seines Inhalts. Geschützte Kopie nur im neuen Vorbereitungsbereich.
3. Eigenen temporären CIFS-Mount mit SMB3.1.1/seal/nosuid/nodev/noexec nutzen. Vor jedem Restic-Aufruf Identität/Schutz prüfen. Nur neues Repository aurelia-operations-v1 exklusiv anlegen; vorhandenes Ziel sperrt. Kein init auf vorhandenem Verzeichnis.
4. Kleine eindeutig synthetische Testdatei sichern, Repository vollständig prüfen, getrennt zurücklesen und Bytes/Modus vergleichen. Repository-ID und Snapshot-ID dokumentieren. Keine neue Sicherung echter Daten in diesem Paket.
5. Kandidatenkonfiguration root0600 mit Repo-ID, Schlüsselreferenz, explizit deaktivierter Automatik und RTO12h ablegen. Keine bestehenden /etc-Dateien oder Dienste ändern. Eigenen Mount entfernen; Timer/PG/Originalmount nachprüfen.
6. Lokale negative Tests und unprivilegierter Linux-Selftest vor Rootausführung. Dann kurzen Start über überprüfte Chrome-KVM, Bericht per SSH und Hashvergleich auswerten.

Das abschließende Laufprogramm für Dateibackup und getrennte konsistente DB-Sicherung ist ein nachfolgender Paketbestandteil. Dieses Vorbereitungspaket aktiviert weder tägliche Sicherungen noch eine Live-DB. RPO, Aufbewahrung und Alarmierung bleiben Entscheidungs-/Abnahmepunkte vor Aktivierung. Kein Prune, keine Wiederherstellung auf Originalpfade, keine Behauptung, G0 oder12h-RTO sei erreicht.
