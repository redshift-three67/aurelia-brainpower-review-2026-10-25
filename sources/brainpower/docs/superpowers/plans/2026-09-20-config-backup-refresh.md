# Aktuelle SMB-Konfigurationssicherung

Freigegeben durch Betreiber: aktuellen Konfigurationsstand verschlüsselt auf vorhandenes SMB sichern, vollständig prüfen und getrennt wiederherstellen. Bestehende Freigabe wird fortgeführt; keine neue Plattformfunktion.

Ziel: vorhandenen Ablauf18.09. für den aktuellen nicht eingebundenen Hauptmount und Wiederverwendung des extern gesicherten Schlüssels anpassen. Neues exklusives Repository, keine Retention/Löschung, kein Live-Restore/Timer. Schlüssel vor Verwendung anhand des bekannten alten Snapshots prüfen; keine neue Schlüsselausgabe. Quelle bleibt definierte Konfiguration, keine DB-/Produktdaten.

- [x] Negative Tests für Hauptmountzustand und alten Snapshot schreiben/ausführen (zunächst fehlende Implementierung; danach vier Tests erfolgreich).
- [x] Separaten Helfer aus bewährtem Ablauf erstellen; fixierte einmalige Lauf-ID, bestehender Schlüssel, unveränderter Hauptmountzustand, private Arbeitsablage/Logs.
- [x] Lokale Tests und isolierten synthetischen Linux-Roundtrip ausführen (Exit0, vollständige Repositoryprüfung und Archivrestore).
- [x] Helfer übertragen/Hash prüfen.
- [x] Ein Root-KVM-Aufruf für echte Sicherung.
- [x] Tatsächlichen Bericht, Hashes und Mount-Rücknahme geprüft. Ergebnis docs/verification/SMB_CONFIG_REFRESH_2026-09-21.md; begrenzte Konfigurationssicherung abgeschlossen, keine Gesamt-G0-Freigabe.

Grenzen: Wiederherstellung des vollständigen Konfigurationsarchivs in getrenntes Verzeichnis, kein Entpacken nach /etc, kein Neuaufbau des Servers. Die Anwendung des externen Schlüssels nach Totalausfall bleibt eigener Recovery-Nachweis. Historische Prüfungen werden nicht auf neue Ausführung übertragen.

## Bereitstellung

Quelle `artifacts/server-config-backup-20260920.py`, Server `/home/klaus999/bpconfig20`, SHA256 lokal/servergleich `388e23473404e0c9d3cd374f3dc474cfd4ef032969fe6249b9e3b7215fb98cd2`. Gehashter bestehender Helfer bprestore18 unverändert. Linux-Selftest am20.09. ohneRoot/NAS/echteDaten: configuration archive10240Bytes, repository_check=true, archive_restore_verified=true. Nur dieser synthetische Test ist bisher ausgeführt.

Einmaliger Root-Aufruf: `python3 /home/klaus999/bpconfig20`. Fixierte Lauf-ID `config-refresh-20260920` blockiert Wiederholung über exklusive Arbeitsablage. NAS-Ziel neu: `aurelia-config-config-refresh-20260920`; alter Snapshot `fcdef1aebc7cf2447c549cb793e2cafe093271406c4e835a73ce9cc6a7e8a648` wird vorab mit bestehendem Schlüssel geprüft. Schlüsselreferenz bleibt Lauf449ada54bc1e4de0aefb58dd8d90f5d4; keine neue Schlüsseldatei. Feld off_server_key_copy_verified bleibt für die neue Ausführung ausdrücklich false (keine neue externe Schlüsselprüfung), trotz historischer externer Sicherung.

Erwarteter Ergebnisbericht `/var/tmp/aurelia-config-result-config-refresh-20260920.json`. Vollständigen Bericht nach Betreiberaufruf lesen, Originalmount vorher/nachher und eigenen Mount-Abbau prüfen. Sicherung umfasst aktuelle usr/local/sbin/Health- und Systemd-Konfiguration mit definierten übrigen Konfigurationspfaden, keine PostgreSQL-Daten oder Produktrepositories. Keine Timer-/Retentionänderung oder Löschung alter Sicherungen.
