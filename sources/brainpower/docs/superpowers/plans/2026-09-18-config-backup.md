# Einmalige Konfigurationssicherung

Betreiber hat nach dem synthetischen SMB-Test die gezielte Sicherung bestehender Serverkonfigurationen vor weiteren Änderungen bestätigt. Keine Vorziehung einer vollständigen produktiven Backupplattform.

Umsetzung: feste Pfadauswahl in `artifacts/server-config-backup-20260918.py`; erforderliche Quellen müssen vorhanden sein, fehlende optionale Quellen werden berichtet. GNU-tar-Archiv mit numerischen Eigentümern, ACLs und erweiterten Attributen; keine Dereferenzierung von Symlinks. Vergleich gegen Quellen nach Aufnahme. Neues exklusives Restic-Repository auf verschlüsseltem temporären SMB-Schreibmount; zufälliger lokaler rootgeschützter Schlüssel. Vollprüfung und isolierte Wiederherstellung des Archivs, unabhängiger Hash-/Modusvergleich. Keine Extraktion in aktive Systempfade, keine Dienst-/Firewall-/Timeränderungen, kein Prune.

- [x] Vorhandenen Backupdienst lesend prüfen: deaktivierte Vorlage; SSH hat kein passwortloses sudo.
- [x] Pfadauswahltests zunächst wegen fehlender Implementierung fehlgeschlagen; danach sechs gezielte Tests einschließlich Mount-/Restore-Negativtests bestanden.
- [x] Skript auf neuen Pfad `/home/klaus999/bpconfig18` übertragen; SHA256 lokal/remote `cc444df5f4108ffedacba92d6529903e4a761a4afb735734bcefb602965e16ff`.
- [x] Echter lokaler Server-Selbsttest mit synthetischem Konfigurationsbaum einschließlich Symlink, tar-Vergleich, Restic-Vollprüfung und Archiv-Restore bestanden.
- [x] Betreiber hat `python3 /home/klaus999/bpconfig18` in Root-KVM ausgeführt.
- [x] Bericht `aurelia-config-result-449ada54bc1e4de0aefb58dd8d90f5d4.json` per SSH verifiziert: 38 Pfade, 1679360 Bytes, Repositorycheck und Archiv-Restore erfolgreich. Frischer Mount-/Timercheck: Hauptmount RO, Schreibmount entfernt, Timer disabled. Snapshot und Hash in WIEDERAUFNAHME.md.
- [x] Externe Kopie am 19.09.2026 direkt auf Betreiberziel `F:\Aurelia-Recovery` uebertragen, SHA256 mit privater Serverzwischenkopie identisch; Zuordnung/Recovery-Hinweise daneben verifiziert. Serverzwischenkopie entfernt, Root-Original erhalten. Laufwerksverschluesselung laut Betreiber, nicht unabhaengig technisch bestaetigt; kein separater Off-Server-Restic-Restore. Schluesselinhalt nicht ausgegeben oder im Projekt gespeichert.

Grenzen: kein Systemabbild, keine LUKS-Header-/Partitionstabellensicherung, keine Datenbank-/Projektdatensicherung. Wiederhergestellt wird das Konfigurationsarchiv in einem isolierten Verzeichnis; kein Boot-/Dienst-Restoretest. Geheimnisse sind im Archiv enthalten, daher lokal ausschließlich unter rootgeschütztem `/var/lib/aurelia-config-backups/<run_id>` und auf NAS nur im verschlüsselten Restic-Repository. Bis zur separaten Schlüsselsicherung kein Schutz vor vollständigem Serververlust behaupten. Kein neuer ZIP-Checkpoint. Produktgates bleiben getrennt.
