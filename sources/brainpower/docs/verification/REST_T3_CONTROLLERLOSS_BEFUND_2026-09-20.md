# Controllerverlust: Teilnachweise, blockierter Abschluss und Nachbereitung

## Aktualisierung: Nachbereitung abgeschlossen

Vollständiger Serverexport bestätigt cleanup_verified um 2026-09-20T15:00:23.463716+00:00. journal_active=null, journal_released/package_removed/unit_retired/staging_absent/original_report_unchanged/services_unchanged jeweils true. SSH/wg-admin/GDM vorher/nachher active. Frische unabhängige SSH-Abfrage: Unit not-found/inactive/MainPID0.

Export lokal `artifacts/t3loss-cleanup20-report.json`, SHA256 `a7c4bbc0a8a2ecfd31d98ab6b0b5812c86ce074b4455e9d59628c3373da86894`, identisch mit Server; Status, Identität und Abschlussflags maschinell geprüft. Der später gezeigte generische BLOCKIERT-Hinweis passt zur Wiederholungssperre nach bereits erfolgter Bereinigung; ohne spezifischen Fehlercode lässt sich die genaue Abbruchstelle jenes Aufrufs nicht beweisen. Keine erneute Ausführung oder Reparatur erforderlich.

Der ursprüngliche Controllerverlust-Test bleibt historisch blocked, fachlicher Ausgang released_unknown. Erfolgreiche Nachbereitung ersetzt keinen vollständigen erfolgreichen Lauf der korrigierten Controllerverlust-Prüfung. Nachfolgende Beschreibung des offenen Zustands ist historisch.

Lauf `0ea5c17104524676939cf6b86926481b` einmalig ausgeführt. Testcontrollerexit73 vom Helfer bestätigt; Nachfolger beobachtete unknown bei zwei weiterlaufenden Prozessen mit korrekten Ressourcenlimits. Abschluss blocked/controller_loss_unverified; Journal unknown/active=1, Test-Staging erhalten.

## Unabhängige Serverbefunde

- systemd-Journal: Start 16:50:57 CEST, Runtime-Limit erreicht 16:51:17, SIGKILL beider Prozesse 16:51:20. MainPID0, Resulttimeout, ExitCode2/Status9; cgroup abwesend.
- Berichtexport-Mtime 16:51:18.128712044 CEST liegt während Stopphase, vor SIGKILL. Die spezifische innere Fehlerursache wurde im alten Runner nicht gespeichert.
- SSH/wg-admin/GDM weiterhin active. services_unchanged=false im abgebrochenen Bericht ist kein Nachweis einer Dienstabweichung.
- Export lokal `artifacts/t3loss20-report.json`, SHA256 `3538566223b9a5f537237522a921ba2400bd1d4fb73baafa49e80b6bfa497975`; systemd-Journal `artifacts/t3loss20-journal.txt`.

## Reproduzierte lokale Lücke und Korrektur

Ein stabiler identitätsgeprüfter Zustand deactivating/stop-sigterm wurde bislang unknown; recover_loss blockierte sofort. Dies passt zeitlich zum Serverbefund, ist wegen fehlender innerer Diagnose aber nicht als einzig mögliche Ursache belegt. Ein Wechsel zwischen zwei Beobachtungen bleibt ebenfalls konservativ blockierend.

Beobachter kennzeichnet jetzt nur stabil geprüfte deactivating/stop-sigterm oder stop-sigkill mit befüllter eigener cgroup als stopping. Recovery wartet darauf innerhalb des unveränderten 30-Sekunden-Budgets; unklare Zustände/Identitätsdrift bleiben blockierend. Vor Freigabe weiterhin vollständiger unabhängiger Endebeleg. Letzte erfolgreiche Beobachtung wird künftig im Report bewahrt.

Drei neue Regressionstests; gesamte lokale Suite **206 Tests bestanden**, 0 Fehler/Skips, 40,062 s. Keine Linux-Wiederholung und keine vollständige Controllerverlust-Abnahme behauptet.

## Vorbereitete Nachbereitung des vorhandenen Laufs

Helfer `artifacts/server-t3-loss-cleanup-20260920.py`, SHA256 `7481d4d277053f2311ca7bad31b26248210360bd17efd634a26423541fc6f74f`, übertragen nach `/home/klaus999/bpt3lossclean20`; Serverhash bestätigt. Verwendet unveränderte zuvor geprüfte Cleanup-Bibliothek `/home/klaus999/t3cleanup20.pyz`, SHA256 `3f0add3baa237e3bc0e430a963c5190c6143bc4fe32ce827209efbf1bdcff4e5`, erneut auf Server geprüft.

Fest gebunden an Originalbericht, Run/Boot/Invocation, Journal unknown und Paketmanifest. Frisches Ende prüfen, eigene Zwischenberichte dauerhaft schreiben, released_unknown buchen, ausschließlich eigene Unit/Staging zurücknehmen. Ursprünglicher blocked-Bericht bleibt unverändert. Neue Rootinstallation unter cleanup-loss20.pyz verhindert versehentliche Wiederholung. Kein Workerstart.

Root-KVM-Aktion `python3 /home/klaus999/bpt3lossclean20` erledigt; Export ausgewertet und gesichert. Nicht wiederholen; keine weitere KVM-Aktion für diesen Lauf.
