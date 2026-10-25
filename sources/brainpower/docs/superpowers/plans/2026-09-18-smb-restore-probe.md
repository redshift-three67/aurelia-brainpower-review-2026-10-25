# Isolierter SMB-Backup-/Restoretest

**Freigabe:** Bestandteil der bereits bestätigten sechs Schritte und des vereinbarten synthetischen Backup-/Restoretests. Kein produktiver Restore oder Timerstart. Umsetzung im vorhandenen Arbeitsbereich.

**Ziel:** Restic auf dem tatsächlich erreichbaren G2-SMB-Ziel mit neu erzeugten synthetischen Dateien, vollständigem Repositorycheck und unabhängigem Wiederherstellungsvergleich prüfen.

**Aufbau:** Neues eindeutiges Testrepository unter der Freigabe; separater temporärer verschlüsselter Schreibmount, bestehender Lesemount bleibt bestehen. Neuer nur lokal rootlesbarer Test-Repositoryschlüssel. Originaldateien, NAS-Testrepository und Restore getrennt. Exakte Snapshot-ID statt latest; kein Cache beim Lesen, check --read-data, restore --verify plus eigener Datei-/Hash-/Modusvergleich. Temporären Mount am Ende aushängen. Keine Löschung bestehender Daten, kein Prune, keine Timeraktivierung. Sanitisierten Bericht für SSH bereitstellen, Rohlogs und Schlüssel rootgeschützt lassen.

- [x] Negative Tests für falsche Mountquelle, fehlende Schutzflags sowie fehlende/zusätzliche/veränderte Restoredateien (drei Unit-Tests bestanden).
- [x] Begrenztes Prüfskript und lokaler echter Restic-Rundlauf auf dem Zielserver: vier synthetische Dateien, Repositorycheck und Hash-/Modusvergleich bestanden.
- [x] Geprüftes Skript unter `/home/klaus999/bprestore18` bereitgestellt; SHA256 lokal/remote identisch, siehe WIEDERAUFNAHME.md.
- [x] Root-Ausführung und NAS-Bericht per SSH verifiziert: synthetischer Test bestanden, temporärer Mount entfernt, Hauptmount RO und Timer aus. Nachweis: `docs/verification/SMB_RESTORE_2026-09-18.md`.

Grenzen: kein vollständiges Serverbackup, keine PostgreSQL-Wiederherstellung, keine RPO/RTO-/Aufbewahrungs-/Offsite-Abnahme und keine Produktfreigabe. CIFS-Workaround GODEBUG=asyncpreemptoff=1 gemäß offizieller Restic-Dokumentation. Installierte Restic-Version 0.16.4 unterstützt die genannten Optionen laut lokalem --help.
