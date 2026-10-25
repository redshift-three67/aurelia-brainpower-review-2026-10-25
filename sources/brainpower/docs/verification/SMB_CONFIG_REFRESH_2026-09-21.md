# Aktuelle SMB-Konfiguration: Sicherung und Archivrestore bestätigt

Betreiber führte `python3 /home/klaus999/bpconfig20` aus. Vollständiger Bericht anschließend per SSH gelesen, lokal gesichert und maschinell validiert. Prüfung am21.09.2026 um00:39CEST (Serverzeit20.09.22:39UTC). Die Lauf-ID enthält das Vorbereitungsdatum; daraus wird kein genauer Ausführungszeitpunkt abgeleitet.

| Nachweis | Ergebnis |
|---|---|
| Status | configuration_archive_restore_verified |
| Lauf | config-refresh-20260920 |
| SMB-Repository | //fra1-nas-backup1.ip-projects.de/213487/aurelia-config-config-refresh-20260920 |
| Snapshot | d2cadcb983700c5082ea487e5043fbedf79bda2d505b34fa295c8aa7f3e5a1ff |
| Konfigurationsarchiv | 38 ausgewählte Pfade,1679360Bytes |
| Archiv SHA256 | 07604b7fc9cca254ee3fc999e5502adcb83dda014bb9ece172dcc17c1a855043 |
| Vollständige Repositoryprüfung | erfolgreich laut geprüftem Bericht |
| Getrennter Archivrestore | erfolgreich, ursprüngliches/restauriertes Payload per Hash und Modus verglichen |
| Bestehender Schlüssel | öffnet erwarteten alten Snapshot; Referenzlauf449ada54bc1e4de0aefb58dd8d90f5d4 |
| Mount-Rücknahme | eigener Mount entfernt; ursprünglicher Mount vorher/nachher unmounted |
| Unabhängige Nachprüfung | kein CIFS-Mount (findmnt Exit1 ohne Ausgabe), Timer disabled, keine failed Units |

Bericht: `/var/tmp/aurelia-config-result-config-refresh-20260920.json`, lokal `artifacts/config-refresh20-report.json`. SHA256 auf Server und lokal gleich: `4dbea4bcafc2da1149dd4662b6f6780dba1e1de37af7d7cdb8c6a601a14f5e55`.

Die aktuelle Konfiguration einschließlich Healthskript und Systemd-Pfaden ist durch den definierten Sicherungsumfang erfasst. Keine Wiederholung nötig. Nicht vorhandene optionale Pfade etc/iptables, etc/lightdm, etc/xrdp sind keine Fehler.

Grenzen: Wiederherstellung des Archivs in getrennten Arbeitsbereich, kein Live-Restore auf /etc, kein vollständig neu aufgebauter Server, keine PostgreSQL-Daten-/Produktrepository-Sicherung. Keine neue externe Schlüsselkopie geprüft: off_server_key_copy_verified=false ist hier korrekt; historische externe Schlüsselsicherung bleibt davon getrennt. Der Schlüssel wurde wiederverwendet, kein neuer erzeugt. Timer nicht aktiviert, keine alten Backups gelöscht. Gesamt-G0 und Provider-/Recoveryklärung weiterhin offen.
