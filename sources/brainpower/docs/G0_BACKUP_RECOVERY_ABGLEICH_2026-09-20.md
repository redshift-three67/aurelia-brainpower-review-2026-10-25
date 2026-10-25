# G0: Sicherungsumfang und Recovery-Abgleich

Aktualisierung 21.09.2026: Die folgende Tabelle beschreibt den historischen Stand vom20.09. Aktuelle Konfigurationssicherung sowie physischer und logischer PostgreSQL-Restore sind inzwischen bestanden. Der Snapshot vom21.09. ersetzt den19.09.-Snapshot als jüngeren Arbeitsstand, umfasst aber ebenfalls keinen Server. Maßgeblicher aktueller Betriebsabgleich: [Backup-Betrieb und Restabnahme](G0_BACKUP_BETRIEB_2026-09-21.md). Automatisierung und unabhängiger Recoveryweg bleiben offen.

Stand20.09.2026. Keine Produktfreigabe, kein automatischer Restore auf Originalpfade. Geltende Grundlage: Aurelia Ground-Zero-Design §§9–12. §9 verlangt zwei verifizierte externe Kopien vor Löschungen; aktuell ist keine Löschung vorgesehen. Der vollständige externe Restore aus §12 bleibt dennoch ein G0-Kriterium.

## Vorhandene Sicherungen und konkret fehlender Nachweis

| Bestand | Beleg | Noch erforderlich |
|---|---|---|
| Lokaler Hermes-Snapshot19.09.23:46 | Manifest plus alle3147 Dateien/151314633Bytes am20.09. geprüft; isoliert wiederhergestellt, alleZielhashes korrekt, SQLite integrity_check=ok | Snapshot enthält nicht die Änderungen vom20.09., keine vollständigen externen Repositories/Git-Historien, keinen Server. Kein Anwendungslauf aus Restore |
| Server-Konfiguration18.09. | Verschlüsseltes Restic-Archiv und Archivrestore bereits geprüft; inkl. SSH/WG/LUKS-Mountkonfiguration, Systemd und weitere definierte Konfiguration | Aktuellen Deltaumfang abgleichen, insbesondere Healthänderung20.09.; alter Snapshot ist kein aktuelles Vollbackup. Nicht blind /etc zurückspielen |
| Graphischer Boot und Firewall19.09. | Gesonderte Ergänzungen laut vorhandenen Recovery-README-Dateien | Mit zugehöriger Konfigurationsversion in Recoveryindex verbinden; keine zusätzliche Vollsicherung daraus ableiten |
| LUKS-Header und Schlüssel | Historisch E:/F:-Kopien geprüft; E:/Aurelia-Recovery aktuell vorhanden, F: aktuell nicht eingebunden | Verfügbarkeit bei Totalausfall, Entsperr-/Recoverytest über unabhängigen Weg. Header ist kein Datenbackup. Kein Schlüsselinhalt gelesen |
| Synthetischer SMB-Restore | Erfolgreicher begrenzter Test18.09. | Kein vollständiger Produkt-/DB-/Serverrestore, kein Ersatz für Datenklassifikation und Konsistenz |
| Fünf externe Produktrepositories | Nicht Bestandteil des geprüften Hermes-Snapshots | Versionierte Quell-/Branch-/Tag-/WIP-Sicherungen und isolierter Repositoryrestore, soweit für G0/Übernahme erforderlich; keine Produktimplementierung oder Altserviceaktivierung |
| PostgreSQL16 | Gestoppt, Kontrollmetadaten sauber, Checksums1 | Tatsächlichen relevanten DB-Datenbestand bestimmen. Konfigurationsarchiv umfasst /etc/postgresql, nicht /var/lib/postgresql. Gestoppt bedeutet nicht leer; keine pauschale Nichtanwendbarkeit |
| Automatisches Serverbackup | aurelia-backup-files.timer disabled | Sicherungsumfang, Konsistenz, RPO/RTO, Retention und Alarmierung vor Aktivierung konkretisieren |

## Neuer isolierter lokaler Restorebeleg

- Quelle: `D:/Aurelia/_Snapshots/Hermes_Aurelia_2026-09-19_23-46-38`.
- Manifest-SHA256: `0ac1253cca0d882b518217f7b601baefe65c464f523cd0fdf7299d30c858cb04`.
- Integritätsbericht: `artifacts/snapshot19-integrity20.json`; sämtliche Manifestdateien bestätigt.
- Restoreziel: `artifacts/isolated-restore19-20260920-201620`; neu angelegt, kein Original überschrieben.
- Restorebericht: `artifacts/snapshot19-restore20.json`;3147 Dateien hashgeprüft; SQLite PRAGMA integrity_check=ok.
- Kopier-/Hash-/SQLite-Prüfung dauerte6,813s. Das ist keine vertragliche RTO und umfasst weder Serverwiederaufbau noch Dienststart.
- Anwendung nicht gestartet, kein Modellaufruf, keine Freigaben aus altem Journal wieder aktiviert. Restorekopie ist vertraulicher lokaler Prüfbestand, kein Releasepaket.

## Weitere Arbeit in Abhängigkeiten

1. Serverdaten-Unterbäume und relevante DB-Nutzung gezielt erfassen, ohne Inhalte/Secrets zu exportieren; daraus tatsächlichen Sicherungsumfang bestimmen.
2. Fehlende aktuelle Sicherungsstände und getrennte Restoreproben vorbereiten. Keine erfolgreiche Bestandsprobe grundlos wiederholen.
3. Provider klärt unabhängiges Rescue/VirtualMedia, BMC-Trennung, Stromausfallpfad und ECC. Betreiber am20.09.: Verfügbarkeit muss erst abgeklärt werden. Anfrageentwurf in G0_PROVIDER_ANFRAGE_2026-09-20.md, nicht versendet.
4. Mit bestätigtem Rettungsweg einen konkreten Recoveryablauf samt Rückkehrpfad vorbereiten. Keine RAID-Mitglieder entfernen oder Header live überschreiben, um einen Test zu erzwingen.
5. Soak-/RPO-/RTO-Kriterien konkret vereinbaren und praktisch nachweisen; danach Gesamt-G0 entscheiden. Keine willkürlichen Prozentwerte oder stillschweigende Gateänderung.
