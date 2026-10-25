# T3: zwei getrennte korrigierte Nachweise, ein KVM-Aufruf

## Aktualisierung: Nachbereitung des zweiten Laufs bestätigt

Cleanupbericht 2026-09-20T15:36:41.208159+00:00: cleanup_verified, journal_active=null; journal_released/package_removed/unit_retired/staging_absent/original_report_unchanged/services_unchanged jeweils true. Unabhängige SSH-Abfrage bestätigt Unit not-found/inactive/MainPID0, SSH/wg-admin/GDM active.

Export `artifacts/t3lossv2-cleanup20-report.json` lokal gesichert und maschinell geprüft. SHA256 `b202b7789c5187982645c738c466376ce0a9cdacbe525f00242f343b52bb0a90` identisch mit Server. Keine weiteren Testreste dieses Laufs offen; alte Berichte und Bibliotheksartefakte bleiben erhalten. Keine erneute KVM-Eingabe nötig.

Der ursprüngliche Controllerverlustlauf bleibt blocked, fachlicher Ausgang released_unknown. Abbruchnachweis ist bestanden. Noch offen: genaue Ursache des verbleibenden Beobachtungsfehlers und vollständiger Controllerverlust-Nachweis. Keine Testwiederholung ohne vorherige gezielte Diagnose und konkrete Freigabe.

## Tatsächlicher Lauf: Abbruch bestanden, Controllerverlust blockiert

Paket einmalig ausgeführt. Abbruchlauf 78252bac63a64892899c4751b5a722ab: abort_verified, zwei laufende Prozesse und Limits belegt, Ende SIGKILL, Journal aborted/active0, Unit/Staging entfernt, Fremddienste unverändert active. Unabhängige SSH-Abfrage bestätigt Unit not-found/MainPID0. Export `artifacts/t3abortv220-report.json`, SHA256 `9f3caa0c65380255fdd660752ea94402a5fb616b65fe9ac6935a2d7ef1cce439`, maschinell geprüft.

Controllerverlust d429c7470b7c4428b5a6c3f80040e5db: blocked, failed_phase=watchdog_observation. Letzte erfolgreiche Beobachtung stopping, beide Prozesse noch vorhanden; Journal unknown/active1. Der frühere stabile Stopübergang wurde somit behandelt. Der genaue nachfolgende Ausnahmegrund fehlt weiterhin; mögliche Messänderung/cgroup-Rücknahme ist eine Hypothese, keine bewiesene Ursache. Kein weiterer Codefix oder Testwiederholung auf dieser Grundlage.

Systemd-Journal bestätigt Runtime-Limit 17:28:39 CEST und SIGKILL beider Prozesse 17:28:41. Frisch per SSH: MainPID0, failed/timeout, Invocation f987b532ea2b41e89d2b9cbc371455a3; cgroup abwesend. SSH/wg-admin/GDM active. Export `artifacts/t3lossv220-report.json`, SHA256 `d6c66196cb25fccf8dd587abcac0caf843612733e8713d11e802cdbee97ddad4`. services_unchanged=false ist hier unvollständige Prüfung, keine nachgewiesene Dienstabweichung.

## Nachbereitung ausschließlich des zweiten Laufs bereit

`artifacts/server-t3-lossv2-cleanup-20260920.py` übertragen nach `/home/klaus999/bpt3lossv2clean20`, SHA256 `409fd1e75b7c21b30451d227145bce4edd3ea2bb450d777d9047e28b68566e5c` auf Server bestätigt, Syntax lokal geprüft. Bewährte unveränderte Bibliothek t3cleanup20.pyz mit Hash 3f0add3baa237e3bc0e430a963c5190c6143bc4fe32ce827209efbf1bdcff4e5 erneut verifiziert. Rootbeleg über exakten Pfad/Hash gebunden, Journal unknown, identitätsgebundener frischer Endebeleg vor Recovery und gezielter Rücknahme. Kein Workerstart. Exportziel `/home/klaus999/t3lossv2-cleanup20-report.json`.

Root-KVM-Aktion `python3 /home/klaus999/bpt3lossv2clean20` inzwischen erledigt; Ergebnis oben bestätigt. Nicht wiederholen. Korrigierter Abbruchnachweis abgeschlossen; vollständige Controllerverlust-Abnahme weiterhin offen. Folgende Planung ist historisch.

Status: beide neuen Läufe ausdrücklich freigegeben; vier Dateien nach Abwesenheitsprüfung übertragen, alle Server-SHA256 identisch mit unten. Noch nicht ausgeführt. Keine Wiederholung alter Laufkennungen. Nächste einmalige Root-KVM-Aktion: `python3 /home/klaus999/bpt3pair20`.

## Umfang und Reihenfolge

1. Abbruchlauf `78252bac63a64892899c4751b5a722ab`: zwei eigene Prozesse, identitätsgebundener Stop, SIGKILL-Ende/Rücknahme; Ziel abort_verified, Journal aborted/active0.
2. Nur nach geprüftem Abschluss von 1: Controllerverlust `d429c7470b7c4428b5a6c3f80040e5db`. Eigener Controllerexit73, neuer Recoveryprozess beobachtet unknown/running, wartet auf Ende und nimmt eigene Reste zurück; Ziel controller_loss_verified, Journal released_unknown/active0.

Unveränderte Worker-/Manifestdateien und Limits: 128 MiB RAM, Swap0, Tasks16, CPU25%, Runtime20s, Stop2s. Keine Produktdaten, keine Governor-/Dienständerungen, kein Reboot. Alte Fehlerberichte bleiben erhalten.

Gemeinsamer Helfer stoppt bei jedem nicht bestätigten Ergebnis. Zwischen beiden Läufen prüft er rootgeschützten Ergebnisbericht, Rücknahmeflags und tatsächlichen Journalabschluss; kein automatisches Retry. Eigene exklusive Ablage unter /opt/aurelia-t3/pair20 verhindert versehentliche Wiederholung. Zwei getrennte Exporte t3abortv220-report.json und t3lossv220-report.json.

## Lokale Korrektur und Grenzen

Zusätzlich zum stabilen stopping-Zustand wird ein enger Übergang zwischen zwei Messungen erkannt: gleiche Boot-/Invocation-/cgroup-/PID-/Konfigurationswerte, nur active/running/success nach deactivating/stop-sigterm/timeout. Nur dieser StopTransition darf im bestehenden 30s-Budget erneut gelesen werden. Identitätsänderungen, andere inkonsistente Messungen und unklare Zustände bleiben Fehler. Kein Start-/Stop-Aufruf wird dadurch wiederholt.

Controllerverlustberichte speichern die zuletzt beobachteten Werte und bei eigener Ausnahme eine feste fehlgeschlagene Phase, ohne rohe Fehlermeldungen. Helfer nennen zumindest den Fehlertyp. Vorherige generische Fehler werden nicht nachträglich umgedeutet.

Gesamte lokale Suite: **209 Tests bestanden**, 0 Fehler/Skips, 39,882 s. Drei neue Regressionstests für engen Stopübergang, erneute reine Beobachtung und vertrauliche Fehlerdiagnose. Gemeinsamer KVM-Helfer syntaktisch geprüft; seine echte Linux-Orchestrierung ist noch nicht ausgeführt.

## Prüfsummen

| Artefakt | SHA256 |
| --- | --- |
| artifacts/rest-t3-pair-20260920.pyz | b3cd9cc982aa3f4c432524272e6b4d54002d6beadb92444ca1e0b8ff04efda06 |
| artifacts/server-t3-abortv2-20260920.py | 318a0dd0d7326bb5c1f8fcb56e15d1fe78a7687deefdde089b9bede0c16a4bee |
| artifacts/server-t3-lossv2-20260920.py | 404dd4fd12726a19e5a56d1e5b6578de41ed6fafbc13ac274b85f8f44772de6b |
| artifacts/server-t3-pair-20260920.py | 39cbe88658fa7c3d67b063f2900ae0b36356b777357e00dbb764e54c264aa2b7 |

Elf Moduldateien im Archiv byteweise gegen Quellen geprüft. Freigegebene Uploadziele /home/klaus999/t3pair20.pyz, bpt3abortv220, bpt3lossv220 und bpt3pair20 übertragen und Hashvergleich abgeschlossen. Anschließend beide tatsächlichen Ergebnisbelege getrennt auswerten; T3-Gesamtstatus erst anhand aller Kriterien fortschreiben.
