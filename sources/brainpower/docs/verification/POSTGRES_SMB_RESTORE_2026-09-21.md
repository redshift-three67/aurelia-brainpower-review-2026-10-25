# PostgreSQL16: physische SMB-Sicherung und Offline-Restore bestätigt

Betreiber führte bpdbsave21 aus. Bericht mit Zeitstempel21.09.2026 10:50:02UTC anschließend vollständig gelesen, lokal unter artifacts/db-cold21-report.json gesichert und maschinell validiert. SHA256 lokal/servergleich d33b60f7e9bb066d881c60254876e6db65eaf25a238f79f0a7de1614b24cfa58.

| Nachweis | Ergebnis |
|---|---|
| Status | cold_database_restore_verified |
| SMB-Repository | //fra1-nas-backup1.ip-projects.de/213487/aurelia-db-cold-20260921 |
| Snapshot | 87cca8b60a1e08cd717a01c11177cff769d40035af4b773ba9fb1f76abc6c05b |
| Archiv | 41963520Bytes; drei Bereiche: Cluster16/main, /etc/postgresql, /etc/postgresql-common |
| Archiv-SHA256 | df981b579ab26a28873ffa14e0f5725008ad9e87107867cefae15a24e001658b |
| Vollprüfung und Archivrestore | erfolgreich |
| Extrahierter Cluster | 995 Archiveinträge; Dateiinhalte, Modi und Eigentümer stimmen mit Quelle überein |
| Offline-Prüfsummen im Restore | 948Dateien/2820Blöcke,0fehlerhafteChecksums,Version1 |
| Quelle | unverändert laut Vor-/Nachmanifesten und Stillstandsprüfungen |
| Mounts/Dienste | eigener SMB-Mount entfernt, Originalzustand unverändert; frischeSSH: keinCIFS, PostgreSQL16/main down, keinefailedUnits |

Schlüsselreferenz449ada54bc1e4de0aefb58dd8d90f5d4; vorhandener Schlüssel öffnet erwarteten alten Snapshot, kein neuer Schlüssel. Externe Kopie nicht erneut geprüft. Keine Sicherungen gelöscht, keine Timer aktiviert, keine Datenbank gestartet, kein Live-Restore. Nicht wiederholen.

Grenzen: physischer Offline-Restore für passende PostgreSQL16-Umgebung. Kein logischer SQL-Dump-/Restoretest, keine gestartete Testinstanz, keine Prüfung des Nutzdatenbestands oder aller Datenbankrechte. Gesamt-G0 bleibt offen. Als nächster DB-Schritt logische Bestands-/Restoreprüfung an einer getrennten Kopie planen; Originalcluster bleibt geschützt. Unabhängiger Recovery-/Providerzugang weiterhin offen.
