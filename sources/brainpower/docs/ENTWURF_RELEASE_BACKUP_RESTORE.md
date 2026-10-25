# Planungsvorschlag: Releases, Backup und Restore im Governor

Status: Diskussionsentwurf aus dem Betreiberwunsch, keine Deployment-/Restore-Freigabe und keine neue laufende Integration. Reihenfolge bleibt: bestehende Hermes-Restfunktionen abschließen/testen/stabilisieren, dann SMB und Backup-/Restore-Abnahme, dann Produktverifikation und Integration.

## Empfohlenes Modell

Pro Projekt/Modul eine stabile Kennung und pro freigegebenem Schritt ein unveränderliches Release-Manifest: Schritt, exakte Quellen-/Artefakthashes, Testbelege, Zielplattform, Abhängigkeiten, Datenbankschema-/Migrationsversion, Freigabe, lokaler und serverseitiger Backupbezug. Ein Gruppenmanifest bindet kompatible Modulstände. Git-Commit, aktueller Arbeitsstand und tatsächlich erzeugtes Linux-Artefakt sind getrennte Nachweise.

Governor zeigt getrennt: lokal vorhanden/getestet; übertragen; serverseitig geprüft; aktiv; gesichert; Restore getestet. Jeder Serverstatus benötigt einen zeitlich datierten Beobachtungsbeleg. Bei fehlender Erreichbarkeit unbekannt/veraltet statt stillschweigend erfolgreich. Freigaben hängen an exakten Manifesten; Drift stoppt weitere Schritte.

Transportvorschlag: SSH/SFTP durch vorhandenes WireGuard mit geprüftem Hostschlüssel und begrenztem Deploymentkonto. Upload in einen neuen Zwischenbereich, vollständige Hashprüfung, Linux-Stagingtests, erst danach ausdrücklich freigegebene Aktivierung. Keine bidirektionale Arbeitsverzeichnisspiegelung. Windows-Umgebungen werden nicht als Linux-Laufzeit ausgeliefert; Zielartefakte werden in passender, reproduzierbarer Linux-Umgebung gebaut.

## Gekoppelter Wiederherstellungssatz

Gemeinsame Release-/Recovery-ID verbindet lokale Quellensicherung, serverseitigen Vorzustand und gesicherten Nachzustand. Unterschiedliche Systeme werden dabei nicht als zeitgleich atomar gesichert behauptet. Erst wenn alle erforderlichen Einzelbelege vorhanden und geprüft sind, ist der Wiederherstellungssatz vollständig. Fehlende Sicherung blockiert die Aktivierung. Für zusammengehörige Datenbanken und Dateien braucht es eine anwendungsspezifische Konsistenzgrenze.

Vorschlag: getrennte verschlüsselte Backup-Repositories für Arbeitsplatz und Server auf dem G2-Ziel, verknüpft durch das Manifest; zusätzlich eine unabhängige geschützte Kopie. Lokale Zwischenkopie und NAS unter denselben löschberechtigten Zugangsdaten sind keine unabhängige Schutzgrenze. Datenbankbackups separat konsistent erzeugen und Rollen/Berechtigungen berücksichtigen. Produktionsdaten werden nicht automatisch auf den Entwickler-PC zurückkopiert.

Restic ist ein Kandidat aufgrund vorhandener Vorbereitung; die konkrete SMB/CIFS-Nutzung bleibt bis zum Integritäts-/Restoretest unbestätigt. NAS-Erreichbarkeit allein ist kein Sicherungsnachweis; bei fehlendem Mount darf kein Ersatzbackup unbemerkt auf die lokale Rootpartition gehen. Provider-Snapshots/Unveränderbarkeit, Aufbewahrung, Kapazität, RPO/RTO und separate Wiederherstellungsschlüssel sind noch zu klären.

## Zweites Sicherungsziel (Betreiberergänzung)

Ein zweiter SMB-Share ist als unabhängiges Sicherungsziel sinnvoll: bevorzugt anderer Anbieter/Standort und getrennte Konten, Schlüssel und Aufbewahrungsregeln. Zwei Shares auf demselben NAS sind keine unabhängigen Ausfalldomänen. Mindestens eine Kopie sollte gegen Löschung durch die produktiven Zugangsdaten geschützt sein (nachgewiesene Unveränderbarkeit oder offline). Verschlüsselung allein verhindert keine Löschung. Kein ungeprüftes Spiegeln eines laufend veränderten Backup-Repositories: separate abgeschlossene Sicherungen beziehungsweise ein vom Backupwerkzeug unterstützter Kopiervorgang mit eigener Prüfung.

Der Governor soll je Ziel Backup-ID, Zeitpunkt, Vollständigkeit, Integritätsprüfung und letzten Restoretest zeigen. Eine gemeinsame Recovery-ID verknüpft passende Stände. Bei Ausfall eines erforderlichen Ziels bleibt der Gesamtsatz unvollständig; eine reduzierte Schutzstufe darf nicht stillschweigend als vollständig gelten. Ob beide Ziele vor jeder Aktivierung erforderlich sind, wird in der späteren Schutzrichtlinie festgelegt. Beschaffung und Einrichtung sind hiermit nicht ausgeführt.

Grundlage: [CISA StopRansomware Guide](https://www.cisa.gov/stopransomware/ransomware-guide) empfiehlt offline verschlüsselte Backups und regelmäßige Wiederherstellungsprüfungen.

## Rücknahme und Wiederherstellung (Ablauf)

Anwendungscode-Rollback ist nur bei passender Datenbank-/Datenkompatibilität zulässig. Nach Migrationen oder neuen produktiven Schreibvorgängen ist eine alte Datenbanksicherung kein verlustfreier Undo. Vor Restore: Ziel-/Auswirkungsplan, Abhängigkeiten, neuer Sicherungspunkt des aktuellen Zustands und ausdrückliche Freigabe. Zuerst isolierte Wiederherstellung testen, anschließend Hashes, Datenbank, Start, Rechte und Modulverträge prüfen. Ein erfolgreicher Backup-/Integritätsbefehl ersetzt diesen Restoretest nicht.

Governor koordiniert feste überprüfbare Adapter und schreibt Belege; Modellantworten treffen keine eigenständigen Backup-Lösch-, Aktivierungs- oder Restoreentscheidungen. Medium bleibt Standard, keine automatische Hochstufung.

## Quellen für spätere Detailplanung

- PostgreSQL16: https://www.postgresql.org/docs/16/backup-dump.html (konsistente Dumps; Rollen separat; Datenbankübergreifende Dumps nicht automatisch synchron).
- Restic: https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html (Repositories, Schlüssel, CIFS-Hinweise).
- Restic: https://restic.readthedocs.io/en/stable/045_working_with_repos.html (Repository-Prüfung).
