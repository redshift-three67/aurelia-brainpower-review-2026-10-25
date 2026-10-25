# PostgreSQL: logischer Wiederherstellungstest bestätigt

Betreiber führte `bpmaint21v2` aus. Vollständiger Bericht anschließend per SSH gelesen und lokal unter `artifacts/maintenance21-v2-report.json` gesichert. Berichtzeitpunkt: 21.09.2026 20:54:45 UTC. SHA256 lokal/servergleich: `9ead56ca690092541f927f3096b85825fbe3fa10df7fb0d2e3e2f04b2921254e`.

| Prüfung | Ergebnis |
|---|---|
| Status | `logical_restore_verified` |
| Getrennte Kopie des zuvor aus SMB restaurierten Clusters | Logischer Dump, Restore in neuen Testcluster und Dumpvergleich bestanden |
| Umfang | 1 Nichttemplate-Datenbank, 15 Rollen; Globals-Vergleich bestanden |
| Laufzeitisolation | Vor Datenbankstart geprüft; keine TCP-Listener |
| Testcluster und Testunit | Beendet; unabhängig per SSH Unit inactive/MainPID=0 bestätigt, keine postgres-Prozesse gefunden |
| Original PostgreSQL16/main | Nie gestartet, Manifest unverändert; unabhängig per SSH down/inactive/MainPID=0 |
| Automatische Gesamtfreigabe | Keine |

Vorheriger Lauf stoppte vor dem Worker mit 226/NAMESPACE. Separate inerte Vergleichsprobe zeigte Exit226 mit InaccessiblePaths=/run und Exit0 mit TemporaryFileSystem=/run:ro. V2 ersetzt ausschließlich diese Einstellung und verwendet neue Lauf-/Unit-IDs. Alte Fehlerberichte bleiben erhalten. Payload-SHA256: `555a926716dc9502e16c8eea401b761e01aa3a9a4e6b315b2ed7c715a6860c0f`. Sechs gezielte lokale Tests bestanden vor Bereitstellung.

Grenzen: Template-Datenbanken ausgeschlossen. Ausschließlich drei unveränderte Standardmitgliedschaften von pg_monitor normalisieren den abweichenden initdb-Bootstrap-Grantor; sonstiger Vergleich bleibt streng. Kein vollständiges Tenant-/Anwendungsrechteaudit, kein Live-Restore des Originals und kein unabhängiger Server-Recoverytest. Private Testkopien verbleiben geschützt zur Nachprüfung; kein erneuter Lauf erforderlich. Kein Timer aktiviert. G0 bleibt wegen weiterer Recovery-/Betriebsanforderungen offen.
