# PostgreSQL Offline-Sicherung und getrennter Restore

Freigegebener nächster Schritt: gestoppten Cluster verschlüsselt auf SMB sichern und isoliert prüfen. Keine Originalstarts, Dumps laufender Dienste, Produktintegration oder Backup-Timer.

Architektur: vorhandene gehashte Backup-Helfer wiederverwenden; exklusiver Lauf und neues NAS-Repository, vorhandener extern gesicherter Schlüssel wird gegen alten Snapshot geprüft. PostgreSQL16-Daten und /etc/postgresql sowie /etc/postgresql-common sichern. Symlinks, externe Mounts/Tablespaces, Sonderdateien und zu große Bestände sperren statt unbemerkt auszulassen. Zustand/PID/pg_control und vollständige lokale Dateimanifeste vor/nach Sicherung abgleichen. Diese Beobachtungen sperren keinen parallelen fremden Administrator; Änderungen führen zum Abbruch.

Restore: vollständige Restic-Datenprüfung, Archivhashprüfung; nur vorher validierte reguläre Clusterdateien und Verzeichnisse in eigenes Ziel extrahieren, Inhalte/Eigentümer/Modi vergleichen und pg_checksums dort prüfen. Konfiguration im Archiv erhalten, nicht live anwenden. Keine Quellinhalte, Schlüssel oder Datenbanknamen in öffentlichen Bericht schreiben.

- [x] Negative Guard-/Archivtests zuerst (fehlendes Modul); dann sechs neue und vier bestehende Tests bestanden.
- [x] Synthetischen PostgreSQL16-Cluster ohne Netzwerkstart initialisiert und vollständigen lokalen Backup/Restorepfad getestet.
- [x] Root-Helfer übertragen und Hash verifiziert.
- [x] Kurzer KVM-Aufruf für echte Daten.
- [x] Echten Bericht/Mountcleanup unabhängig ausgewertet. Physischer Offline-Teilabschluss: docs/verification/POSTGRES_SMB_RESTORE_2026-09-21.md. Keine Gesamt-G0-Freigabe.

Grenzen: physische Sicherung für passende PostgreSQL16-Umgebung, kein logischer SQL-Dump/-Restore, keine gestartete Recoveryinstanz oder vollständige Serverabnahme. Externe Schlüsselkopie in diesem Lauf nicht erneut prüfen; keine alten Sicherungen löschen.

## Bereit für Root-Ausführung

- Lokale Quelle artifacts/server-db-backup21.py, Server /home/klaus999/bpdbsave21; SHA256 beide ded1fdbea473cb7552af39e4dfc858f0bc6f8fce506fed692ad5ec429dd940e1.
- Kurzer einmaliger Aufruf `python3 ~klaus999/bpdbsave21`. Noch nicht ausgeführt.
- Fester exklusiver Arbeitslauf /var/lib/aurelia-config-backups/db-cold-20260921; NAS-Repository aurelia-db-cold-20260921. Vorhandener Schlüssel449ada54bc1e4de0aefb58dd8d90f5d4; kein neues Schlüsselmaterial.
- Bericht /var/tmp/aurelia-db-cold-20260921-result.json. Bei Fehler nicht wiederholen; private Logs am Server behalten, nur bereinigten Bericht auswerten.
- Linux-Selftest unprivilegiert bestanden: neues synthetisches initdb16 mit Datenchecksums, kein Netzwerkstart/NASzugriff/Originaldatenzugriff. 41574400Byte Archiv, vollständiger Restic-Check,994Cluster-Archiveinträge; Dateiinhalte/Modi/Eigentümer identisch, Source unverändert,948Dateien/2820Blöcke im Restore geprüft,0fehlerhafteChecksums. Konfiguration im Archiv wiederhergestellt, nicht angewendet.
- Nachprüfung Originalcluster16/main weiterdown, keinefailedUnits. Physische Echt-Sicherung weiterhin offen.
