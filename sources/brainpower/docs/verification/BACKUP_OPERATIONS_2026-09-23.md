# Gemeinsame Backup-Abnahme vom 23.09.2026

Status: **manueller Lauf mit echten Serverdaten auf SMB erfolgreich**, vollständiger Bericht per SSH geprüft. Automatik bleibt aus.

## Tatsächlicher Lauf

Start laut Bericht 23.09.2026 18:55:22 UTC. Status `cold_operations_restore_verified`. Unveränderter Originalbericht lokal `artifacts/operations23-report.json`, SHA256 lokal/servergleich `b249d058f2b6511450ebe35caf20dd7b9909752a6c7197e93b984d40afe7997b`.

Snapshot `84bb5f8cff3057f8b918da618701fb05c22e2bb830d0f38c3ce11ea513d5f65e` im erwarteten Betriebsrepository. Repositoryprüfung und Archiv-Restore erfolgreich; Dateiabgleich sowie Datenbankinhalte und Metadaten stimmen überein. Quell- und Restoreprüfung: jeweils 948 Dateien, 2820 Blöcke, null schlechte Prüfsummen, Version1. Archivdaten insgesamt 48.722.386 Bytes.

Retention-Vorschau behält den einzigen Snapshot dieses Profils; keine Löschkandidaten (`remove=null`). Das bestätigt die Vorschau für den aktuellen Bestand, noch keine Langzeitverteilung über Wochen/Monate. Temporärer Mount entfernt und Originalzustand unverändert. Frische separate SSH-Abfrage: PostgreSQL inactive/MainPID0; Backuptimer inactive/disabled. Keine Fehler-E-Mail erforderlich oder versendet. `bpops23.py` nicht erneut ausführen.

## Vorbereitungsnachweis

- Datei: `artifacts/server-operations23.py`, Server: `/home/klaus999/bpops23.py`.
- Finale SHA256 lokal/servergleich: `774761ee0df458216ac8432fea1de29592320f68a2da973b8a340e40c156845d`; Linux-AST geprüft.
- Kurzer Rootstart: `python3 /home/klaus999/bpops23.py`.
- Bericht: `/var/tmp/aurelia-operations23-result.json`; exklusives Arbeitsverzeichnis verhindert versehentliche Wiederholung.

## Umfang und Grenzen

Quellen: `/etc`, `/home/aurelia-dev`, `/srv/build`, `/srv/aurelia`, `/usr/local/sbin`, `/home/klaus999/.ssh/authorized_keys`. Ausgeschlossen: Backup-Staging, lost+found in den beiden srv-Quellen, node_modules, .venv, __pycache__, persönliche venvs. Konfiguration einschließlich Zugangsdaten gelangt nur in private lokale Archive und das verschlüsselte Repository; keine Inhalte werden im öffentlichen Bericht ausgegeben.

PostgreSQL16 wird ausschließlich gestoppt und sauber heruntergefahren akzeptiert. Kein Start/Stopp, keine Live-Rücksicherung. Separate DB-Datei im gemeinsamen Snapshot; Quelle und extrahierte Testkopie werden nach Inhalt/Modus/Eigentümer sowie PostgreSQL-Prüfsummen verglichen. Konfigurations-/Dateiarchiv wird aus dem Repository zurückgelesen, gehasht und mit GNU tar gegen die Quellen verglichen, nicht über das laufende System extrahiert.

Verwendet das bestehende Repository `aurelia-operations-v1`, ID `8dd73248e24a470cb30e72fe7a0d15e8caf0278d654e08a03ff7a41d92b10c98`; keine Neuinitialisierung. Vor Zugriff: bekannter CIFS-Mount mit SMB3.1.1/seal und erwartete Repository-ID. Eigener Mount wird anschließend entfernt; ursprünglicher Mount sowie DB-/Timerstatus kontrolliert. Exklusive Sperre und zeitlich begrenzte Kindprozesse. SIGTERM leitet geordnetes Aufräumen ein; harter Prozess-/Stromausfall bleibt separat zu behandeln.

Retention ausschließlich Vorschau: `forget --dry-run`, Tag `operations-cold`, Host `aureliaserver`, Gruppierung `host,tags`, 7 täglich/4 wöchentlich/6 monatlich. Keine Löschungen, kein Prune, kein Timer. Fehler werden nach Aufräumen einmal per bestehendem SMTP-Konto gemeldet; SMTP-Ausgang bei Fehler separat im Bericht, keine automatische Wiederholung. Vollständiger Serverausfall oder fehlender Start wird von diesem einzelnen Paket nicht überwacht.

## Nachweise

`python -m unittest tests.test_operations23`: acht Tests bestanden. Prüfen eindeutigen Backupbeleg, Retention ohne Löschung, Datenbankzustand, Repository-ID, TLS-Abbruch vor Anmeldung/Versand, festen Empfänger ohne Geheimnisse, Abbruch vor Quellzugriff bei falschem Repository und Aufräumen/Fehlerbericht bei fehlgeschlagener Sicherung. Mailtests verwenden Mocks, versenden nichts.

Unprivilegierter Linux-Selftest am 23.09. ca.18:51 UTC erfolgreich: `/tmp/aurelia-operations23-selftest-y9brpudy`. Künstliche Konfiguration einschließlich Symlink und separat initialisierte Offline-PostgreSQL16-Datenbank; lokales Testrepository, kein SMB und kein Mailversand. Snapshot `1724e6a26aa901d2f2c07b51f249e50628643e86ed55a46b890769cc80447786`; Repositorycheck, Rücklesen und Vergleich erfolgreich. Quelle und Kopie jeweils 948 Dateien, 2820 Blöcke, 0 Prüfsummenfehler, Prüfsummenversion1. Archivdaten 41.574.742 Bytes. Retention-Vorschau behält den einzigen Snapshot, remove=null. Nachfolgende Änderung betraf nur SIGTERM-Behandlung im privilegierten Einstieg; finale Datei separat per Hash/Syntax und erneut acht Unit-Tests geprüft.

Der tatsächliche SMB-Restore mit Serverdaten ist inzwischen oben belegt. Dies ist kein vollständiger Maschinenrestore und kein RPO12h-/RTO12h-Nachweis. Frühere physische/logische Restorebelege bleiben separate Evidenz. Automatik, Altersüberwachung, externes Recovery und Gesamtfreigabe bleiben offen. Fehlerbenachrichtigung ist im manuellen Paket implementiert und mit Mocks geprüft; ein realer Backup-Fehler wurde nicht künstlich ausgelöst.
