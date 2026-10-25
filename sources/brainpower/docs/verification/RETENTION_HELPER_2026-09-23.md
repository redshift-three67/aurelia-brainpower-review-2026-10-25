# Aufbewahrungshelfer – lokaler Vorbereitungsstand

## Aktuell: begrenzte reale Entfernung erfolgreich

Betreiber hat `--apply` ausgeführt. Bericht23.09.20:36:07UTC mit Status `reviewed_snapshot_removal_verified` per SSH geprüft und getrennt als `artifacts/retention-apply23-report.json` gesichert. SHA256 lokal/servergleich `744830c99407f9df5eee3ca08b792068d1d5e1445b872c7562573815796aad09`. Genau der freigegebene Snapshot0c879b55 wurde entfernt; erwartete übrige Snapshotmenge danach exakt verglichen und `restic check --read-data` erfolgreich abgeschlossen (Voraussetzungen dieses Erfolgsstatus im geprüften Helfer). Geschützter8591d898 sowie84bb5f8c/8590a841 erhalten. Temporärer Mount entfernt. Prune nicht durchgeführt, keine automatische Bereinigung aktiviert. Apply nicht wiederholen: rootgeschützter Vorschauplan wurde nach Erfolg verbraucht.

Beide Timer separat20:36:48UTC active/enabled bestätigt; nächste Sicherung24.09.02:00CEST, Watchdog23.09.22:45CEST. Alte Vorschau unten historische Evidenz; Einzelschritt ist kein Nachweis einer aktivierten automatischen Retention oder Speicherfreigabe durch Prune.

## Aktuell: reale Vorschau geprüft

Betreiber hat Standardaufruf ausgeführt. Bericht23.09.20:32:09UTC per SSH geprüft und lokal als `artifacts/retention-preview23-report.json` unverändert gesichert; SHA256 lokal/servergleich `5729a81f40cde2aba65321a5c21db473da87abcff5bf702945813f80c9691761`. Status retention_preview_verified, apply_requested=false, prune_performed=false, temporary_mount_detached=true.

Einziger Kandidat: `0c879b553cc803b9e79337d303cba3f7d02a802ff9f63d7bd35e410fdb607aec` (23.09.21:18CEST). Erhalten bleiben ursprünglicher Profilstand84bb5f8c, synthetischer Vorbereitungsstand8590a841 und geschützter jüngster geprüfter Profilstand8591d898 (22:00CEST). Snapshotmengenhash `fade9fa02ed7622b53ac8e4061585619872081aa632430b180b6b1448351896e`. Beide neuen Timer frisch active; nächste Sicherung24.09.02:00CEST.

Konkreter nächster Rootaufruf zur bewussten Entfernung ausschließlich dieses unverändert geprüften Kandidaten: `python3 /home/klaus999/bpret23.py --apply`. **Noch nicht ausgeführt.** Bei verändertem Bestand/Erfolgsstand bricht er ab; keine pauschale Policy-Neuberechnung mit ungeprüfter Löschung. Kein produktivesPrune/keine automatischeBereinigung. Danach neuen Ergebnisbericht getrennt sichern, Vorschau-Evidenz erhalten. Nachfolgende Vorbereitungsangaben historisch.

Datei `artifacts/server-retention23.py`, SHA256 `0bf12a0f1f05f593264ccc7921cb8b711473dbbdab1115767ec5320e1263c119`. Acht lokale Tests `tests.test_retention23` bestanden. **Nach ausdrücklicher Datei-/Zielfreigabe übertragen; Linux-Selftest bestanden. Reale Root-Vorschau und Apply stehen aus.**

Standardaufruf als root erstellt ausschließlich neue Vorschau; `--apply` ist separater noch nicht angeforderter Löschschritt. Frischer erfolgreicher Backupnachweis unter8h, bekannter Host/Tag, festes Repository, gemeinsamer Backup-Lock, vollständiger Repositorycheck, geschützter jüngster verifizierter Snapshot, exakte disjunkte Mengen und Snapshotdriftkontrolle. Apply verwendet ausschließlich explizite IDs aus unveränderter rootgeschützter Vorschau. Danach Mengen-/Repositoryprüfung; keine produktive prune-Operation und keine Timerinstallation.

Linux-Selftest erfolgreich: unprivilegiertes lokales Testrepository mit3synthetischen Profilständen plus fremdem Testprofil; genau1Zwischenstand entfernt, ausschließlich Testrepository geprunt, check und erhaltenen Inhalt erfolgreich wiederhergestellt. Fremdes Profil erhalten. Ausgabe synthetic=true, production_access=false, candidates_removed=1, foreign_profile_preserved=true, check_after_prune=true, retained_restore_verified=true. Kein SMB oder produktiver Datenzugriff. Serverhash oben stimmt mit lokalem Hash überein; temporäres synthetisches Repository automatisch entfernt.

Erster Upload nach `/home/klaus999/bpret23.py` auf185.242.115.210 durch automatische Freigabeprüfung abgelehnt: konkrete Payload-/Zielfreigabe verlangt. Betreiber hat anschließend ausdrücklich „Übertragung und synthetischen Test freigeben“ bestätigt. Erneuter gleicher Upload und synthetischer Test danach genehmigt und erfolgreich; keine Umgehung. Diese Freigabe umfasst keine echte Löschung.

Nächster kurzer Rootaufruf: `python3 /home/klaus999/bpret23.py` (ohne Argumente, nur Vorschau). Er prüft aktuelles Erfolgsalter, vollständiges Repository, Snapshotpartition und geschützten Stand unter gemeinsamer Backup-Sperre; speichert Plan rootgeschützt in `/var/lib/aurelia-backup-runtime/retention-preview.json` und bereinigten Bericht `/var/tmp/aurelia-retention23-result.json`. Anschließend Bericht per SSH prüfen. `--apply` noch nicht veranlasst; keine automatische Bereinigung eingerichtet.

Erinnerung an zweite Sicherungslocation angelegt: Heartbeat `zweite-serversicherung-vormerken`, täglich stille Anlassprüfung, Erinnerung erst zur Server-Abschlussbesprechung/Hermes-Übergang oder spätestens vor nicht reproduzierbaren Produktivdaten; doppelte Meldungen unterdrücken, nach Erfüllung pausieren.
