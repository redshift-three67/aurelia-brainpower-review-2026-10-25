# Wiederkehrende Aufbewahrung – Abschlussblock

Ziel: Die genehmigte Regel 7 täglich / 4 wöchentlich / 6 monatlich täglich ausführen. Bestehender Backup-Runner bleibt unverändert. Der bereits geprüfte Retention-Helfer wird hashgebunden wiederverwendet.

Entscheidung: separater Dienst täglich 01:00 UTC, gemeinsame operations.lock, maximal 20 Minuten plus 90 Sekunden Abbruchbereinigung. Backup läuft alle vier Stunden. Aktuelle erfolgreiche Sicherung unter acht Stunden, feste Repository-ID, vollständige Vorprüfung, frischer Plan und identische Snapshotmenge erforderlich. Nur geprüfte IDs löschen. Prune mit maximal 128 MiB Repack und 10 Prozent tolerierten ungenutzten Daten; dies begrenzt nicht die insgesamt freigegebenen Bytes. Danach vollständiger Check, identische verbleibende Snapshotmetadaten und verifizierter Restore des jüngsten Standes in eigenen lokalen Arbeitsbereich. Kein Entpacken ins Live-System.

Eigener Watchdog stündlich und bei Dienstfehler: fehlender/fehlerhafter Bericht oder letzter Erfolg älter als 36 Stunden meldet per vorhandener SMTP-Verbindung. Zustandsdateien getrennt vom Backup, Benachrichtigungen auf eine pro Stunde begrenzt. Ein Server-/Netzausfall selbst ist dadurch nicht extern überwacht.

- [x] Tests zuerst: Fehler vor Löschung, Drift, fremde Profile, Post-Prune-Restore, Fehler-/Altersalarm.
- [x] `artifacts/server-retention-runtime23.py`: Ablauf, Mount-/Sperr-/Cleanup-Prüfung, private Zustände und öffentlicher Ergebnisbericht; synthetischer Linux-Test ohne Produktionszugriff/Mail.
- [x] `artifacts/server-retention-install23.py`: Hashprüfung, exklusive Installation zusätzlicher Dateien/Units, Timer zunächst aus; einmalige reale Abnahme im Dienst vorbereitet, noch nicht gestartet.
- [x] Lokale Tests, Linux-Syntax/Units/Kalender und synthetischer Roundtrip; gezielte Codeprüfung. Nachweis `docs/verification/RETENTION_RUNTIME_2026-09-23.md`.
- [ ] Kurzer Root-Befehl zur manuellen Abnahme anbieten; Ergebnis lesen, erst danach Zeitplan aktivieren. Automatische Löschwirkung ausdrücklich benennen.
- [ ] Kurzen Serverstand und maschinenlesbaren Status aktualisieren. Keine RTO-/Langzeitfreigabe behaupten.

Zurückgestelltes Rescue und zweite Datenkopie bleiben zurückgestellt. Kein neues Ziel/Export. Vor Hermes kurze Abschlussbesprechung einschließlich Erinnerung an zweite Kopie.
