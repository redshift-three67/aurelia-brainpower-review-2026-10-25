# Backup-Betrieb: Voraussetzungen vollständig erhoben

Betreiber führte bpbp22 aus. Berichtzeitpunkt 22.09.2026 16:22:21 UTC. Per SSH gelesen und artifacts/backup-preflight22-report.json gesichert. SHA256 lokal/servergleich `ce826b9b30f942d053585a30d022be26503b5f182521a638d7c60c52f092128d`. Status observations_only bedeutet Erhebung, keine Betriebsfreigabe.

| Voraussetzung | Beobachtung | Bedeutung |
|---|---|---|
| /etc/aurelia-backup/repository | Fehlt | Automatischer Dienst hat noch kein konfiguriertes Repository |
| /etc/aurelia-backup/password | Fehlt | Für diesen Dienst erwartete Passwortdatei fehlt; keine Aussage über die Schlüssel früherer Einzelsicherungen |
| SMB-Credentials | Regulär, root:root0600 | Datei vorhanden; Inhalt und aktuelle Anmeldung nicht geprüft |
| /mnt/aurelia-g2 | Kein eigener Mount, darunterliegendes ext4 | NAS aktuell nicht eingehängt; kein Beweis eines NAS-Ausfalls. Ein Repository darf hier nicht ersatzweise lokal angelegt werden |
| /home, /srv/build, /srv/aurelia | Jeweils eigene ext4-Mounts, beschreibbar | Im Backup-Programm erkennbare Quellmountbedingungen derzeit erfüllt |
| Backup-Cache | root:root0700-Verzeichnis vorhanden | Lokaler Cache vorbereitet |
| backup-staging | Verzeichnis uid/gid995,0700 | Vorhanden, nicht als rootgeschütztes Restore-/Backup-Arbeitsverzeichnis behandeln |
| PostgreSQL16 | inactive/MainPID0, kein postmaster.pid, sauber heruntergefahren, Checksums1 | Original bleibt gestoppt; kein Anzeichen einer gestarteten Testinstanz aus dieser Prüfung |
| PG-Werkzeuge | pg_dump, pg_dumpall, pg_restore, pg_basebackup, pg_verifybackup vorhanden | Verfügbarkeit, noch kein Nachweis eines automatischen laufenden DB-Backups |
| Credentialreferenzen im Backup-Programm | CREDENTIALS_DIRECTORY und restic-password erwähnt | Marker passen zum LoadCredential-Ansatz, ersetzen keine vollständige Semantikprüfung |
| Backup-Timer | disabled/inactive | Keine automatische Sicherung aktiv |

Frische zusätzliche systemctl-Abfrage bestätigt Backup-Timer und PostgreSQL inaktiv; PostgreSQL-Unit ebenfalls disabled. Keine Dienste/Mounts/Backups gestartet, keine Schlüsseldateien gelesen oder verändert.

## Nächste konkrete Umsetzungsvorbereitung

Die Diagnosephase für fehlende Basiskonfiguration ist abgeschlossen. Nicht weitere identische Leseprüfungen anfordern. Nächstes Paket soll die tatsächliche Einrichtung vorbereiten: bestehenden geprüften Schlüssel sicher zuordnen (kein neues Schlüsselmaterial ohne Bedarf), getrenntes Betriebsrepository festlegen, erwarteten SMB-Mount mit Versions-/Verschlüsselungs-/Schreibschutzprüfung absichern und bei fehlendem NAS zwingend stoppen. Keine lokale Ersatzablage und kein init/prune auf bestehenden Testrepositories.

Dateien und Datenbank bleiben getrennte Konsistenzbereiche. Aktuell gestoppte DB nicht allein für eine Automatik starten; für späteren Livebetrieb konsistenten DB-Backupweg und getrennten Restoretest vorsehen. Installationspaket und Tests vor Serveränderung vorbereiten. Automatik bleibt bis technischer Abnahme sowie Betreiberentscheidung über RPO/RTO, Aufbewahrung und Fehlerbenachrichtigung deaktiviert. Aufgeschobene RPO/RTO-Fragen gezielt vor Aktivierung erneut stellen. Unabhängiger Provider-Recoveryweg und Gesamt-G0 bleiben offen.
