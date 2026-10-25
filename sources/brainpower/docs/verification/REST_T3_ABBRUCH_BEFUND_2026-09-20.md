# T3-Abbruchtest: Teilnachweise und blockierter Abschluss

Lauf `fcc704a500994914980489fbb99afda6`, 20.09.2026. Einmal ausgeführt, nicht wiederholt.

| Prüfung | Befund |
| --- | --- |
| Laufende Prozesse | Zwei eigene Prozesse beobachtet |
| Laufende cgroup-Limits | RAM 134217728 Byte, Swap 0, Tasks 16, CPU 25000/100000 |
| Abbruch | Journal: Stop 12:38:32 CEST; SIGTERM-Timeout und SIGKILL für beide Prozesse 12:38:34 |
| Endzustand | MainPID=0, failed/failed, Result=timeout, ExecMainCode=2, ExecMainStatus=9; Test-cgroup abwesend |
| Identität | InvocationID 76e88634e2544dd98d4f0f79d4370eff, Boot 2d811cdff7704fa0bb3cf6ec54666fed |
| Fremddienste | SSH, wg-admin und GDM bei unabhängiger Nachprüfung active |
| Controller | blocked / abort_unverified; Journal abort_requested, active=1 |
| Rücknahme | Test-Staging und fehlgeschlagene Test-Unit noch vorhanden; keine Bereinigung ausgeführt |

Der systemd-Journaltext belegt den Stop-Timeout nach zwei Sekunden, nicht das Erreichen des 20-Sekunden-Laufzeitlimits. Die Abschlussprüfung verlangte dagegen ausschließlich inactive. Ein fehlgeschlagener Unit-Zustand bedeutet hier nicht, dass Testprozesse weiterlaufen. Der ursprüngliche Bericht enthält keinen Rückgabecode des inneren systemctl-Aufrufs; dessen damaliger Erfolg ist daher nicht separat nachgewiesen.

`services_unchanged=false` im abgebrochenen Bericht ist ein nicht abgeschlossener Prüfschritt, kein Nachweis veränderter Fremddienste. Kein OOM- oder CPU-Drosselungsnachweis aus den beobachteten Grenzwerten ableiten. T3 bleibt offen.

## Lokale Verifikation

`python -B -m unittest discover -s tests -p 'test_contract*.py' -q`: **177 Tests bestanden**, 0 Fehler/Skips, 40,957 Sekunden. Die lokale Suite ersetzt keinen Ubuntu-Ausführungsbeleg der Korrektur.

## Gesicherte Belege

- `artifacts/t3abort20-report.json`: exportierter Rootbericht; SHA256 `ee357c8d70cfb03f224386f99ec1db8752c318876e22be65c561f568381f27ca`.
- Ursprünglicher Rootbericht SHA256 `867aa45ea502d94410c3584677d24938a2da62e21efe4590eb9cc02ea0ddec36` laut Export.
- `artifacts/t3abort20-journal.txt`: lesend abgerufenes systemd-Journal, lokal als UTF-8 gespeichert.
- Ursprünglicher Runner und Bericht bleiben unverändert erhalten.

## Lokale Korrektur

`linux_backend.py` trennt Endebeleg und Unit-Rücknahme. Ein frischer unabhängiger Beobachter darf den gebundenen Prozessabschluss mit entfernter cgroup und timeout/SIGKILL bestätigen. Boot, Invocation und doppelte Zustands-/Abwesenheitsprüfung bleiben erforderlich. Erst bei Rücknahme wird genau diese Test-Unit per reset-failed zurückgesetzt; danach gilt weiterhin die strikte Prüfung inactive und abwesende cgroup, bevor Paketdateien entfernt werden.

Nicht erfolgreiche Stop-Befehle bleiben konservativ blockiert; die Änderung verschluckt keine Befehlsfehler. Kein automatischer Retry. Vier zusätzliche lokale Regressionstests prüfen erwartetes Timeout-Ende, abweichende Endbelege, begrenzte Unit-Rücknahme und den aufgezeichneten systemd-Zustand einschließlich Identitätsabweichungen.

Noch keine neue Runnerinstallation oder Linux-Ausführung der Korrektur. Nächster Schritt: identitätsgebundene Recovery des bereits beendeten Laufs mit gesondertem Bericht und gezielter Rücknahme vorbereiten. Der historische blockierte Abschluss darf dabei nicht nachträglich als vollständig erfolgreicher Abbruchlauf umetikettiert werden.
