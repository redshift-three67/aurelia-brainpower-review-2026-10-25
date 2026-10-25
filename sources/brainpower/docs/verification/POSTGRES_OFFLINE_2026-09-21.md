# PostgreSQL16: Offline-Seitenprüfung bestanden

Betreiber führte bpdb21 aus. Bericht09:37:05UTC am21.09.2026 perSSH vollständig gelesen und lokal unter artifacts/db-check21-report.json gesichert. SHA256 lokal/servergleich:0758e719f604f83411fd2b1856c07547f9a7b25f69a374ac409c47e9c8e1b8ea.

- Status offline_checksums_verified; pg_checksums --check Exit0, stderr leer.
- 948 Dateien und2820 Blöcke geprüft;0 fehlerhafte Prüfsummen, Prüfsummenversion1.
- Keine Datenbank gestartet oder Konfiguration geändert; frisches pg_lsclusters bestätigt16/main down.
- Vorherige Betreiber-du-Ausgabe: Cluster ca.39MiB, davon base22MiB und WAL17MiB. Kleine Größe beweist keine Nutzdatenfreiheit.

Nachweis abgeschlossen, nicht wiederholen. Dies ist kein logischer Konsistenztest, kein DB-Backup-/Restoretest und keine Gesamt-G0-Freigabe. Nächster Schritt: konsistente Sicherung des gestoppten Clusters auf SMB und isolierte Wiederherstellung vorbereiten; dabei PostgreSQL-Version, Konfiguration, etwaige externe Tablespaces/WAL-Verweise, unveränderten Stillstand und vorhandenen Sicherungsschlüssel berücksichtigen. Originalcluster nicht zur Bestandsaufnahme starten; Nutzdatenumfang anschließend gegebenenfalls ausschließlich an isolierter Kopie prüfen.
