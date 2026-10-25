# T3 – integrierter Normal-/Recovery-Runner

20.09.2026: **159 Tests bestanden, 0 Fehler, 0 Skips, 38,836 Sekunden**. Zehn neue Integrationstests verbinden echtes lokales SQLite-Journal, Controller und Runner mit ausdrücklich synthetischen OS-Backendantworten. Keine Ubuntu-Ausführung.

```powershell
& 'C:/Users/Hubert111/AppData/Local/Programs/Python/Python312/python.exe' -B -m unittest discover -s tests -p 'test_contract*.py' -q
```

## Implementiert

| Baustein | Verhalten / Nachweis |
|---|---|
| Fester Einstieg | Ausschließlich normal/recover, 32-stellige Laufkennung und Manifestanker. Linux/root-Gate vor privilegierter Aktion. Feste Pfade für Paket, Journal, Sperre und Berichte. |
| Normalende | Passende Identität, ended, erfolgreicher Unit-Ausgang und Exitcode 0 erforderlich. running/fehlender Beleg/Exitfehler ergeben blocked ohne Paketlöschung. Prozessabschluss ist kein Nachweis eines kompletten fachlichen Analysevertrags. |
| Fremddienstvergleich | SSH, wg-admin und GDM werden über feste ActiveState-Abfragen vor/nach beobachtet. Vorher active erforderlich, Änderungen verhindern Paketentfernung. Das ist kein vollständiges Serverinventar oder Verfügbarkeitsbeweis. |
| Recovery | Nur bereits unknown mit gespeicherter Identität; kein Start/Replay. Passender Endebeleg erlaubt ausschließlich released_unknown. Keine Löschung durch Recovery. |
| Bericht | UTC, Laufkennung, Manifestanker, begrenzte Beobachtungen und Status. Exklusive neue Datei mit fsync; bestehender Beleg wird nicht überschrieben. Bereinigte Fehler ohne Rohfehlertext. |
| Cleanupfehler | Selbst nach terminalem Journalbeleg kein erfolgreicher Gesamtbericht bei fehlgeschlagener Paketentfernung. Teilstände bleiben unterscheidbar. |

RED/GREEN: fehlender Runner zuerst nachgewiesen. Einstiegspunkttest war vor Ergänzung rot; danach gemeinsamer Lauf erfolgreich. Windows-Gate separat über gebautes Zipapp geprüft: blocked/entry_unverified, keine Serveraktion.

## Gebautes Paket

`artifacts/rest-t3-runner-20260920.pyz` enthält ausschließlich acht contract_lab-Module und den festen Einstiegspunkt. ZIP-Integrität geprüft, jeder enthaltene Modulinhalt bytegleich zum lokalen Quellstand.

- Runner-SHA256: `d29aed5d9e3519aaa3df181608b8c09341025b0f6e463db15eb15b580e95f82a`
- Zugehöriges Workerpaket: `artifacts/rest-t3b-20260920/`
- Worker-Manifestanker: `5379aa7b6d45a25a93ba5a6b1a507e8281c3c99b0f4b555c562b7fffcd7b42f1`

Vorgesehene spätere Root-Aufrufform (noch NICHT ausgeführt/freigegeben): `/usr/bin/python3 -I /opt/aurelia-t3/runner.pyz normal <neue-32-stellige-laufkennung> <worker-manifestanker>`. Zielpaket ist fest `/opt/aurelia-t3/package`, Journal/Sperre/Berichte unter `/var/tmp/aurelia-t3-control`. Bereitstellung muss zuvor Rootbesitz, Pfadschutz und beide externen Hashanker prüfen.

## Konkrete Hindernisse vor Ubuntu-Freigabe

1. Der Beobachter verlangt bisher eine vorhandene identisch gebundene cgroup. Wenn systemd diese beim Normalende entfernt, blockiert er korrekt, kann aber keinen Abschluss bestätigen. Ein gesonderter belastbarer Endebeleg für diesen Linux-Lebenszyklus muss spezifiziert und getestet werden; nicht einfach fehlende cgroup als Erfolg werten.
2. Paketdateien können gezielt entfernt werden, die mit RemainAfterExit erhaltene Testeinheit wird jedoch noch nicht ausdrücklich zurückgenommen. Unit-Abschluss und anschließender Zustandsnachweis müssen ergänzt werden.
3. Der Runner beobachtet den Normalfall aktuell einmal. Ein noch laufender Prozess ergibt blocked; keine versteckte Wiederholung. Beobachtungsbudget und persistente Nachbeobachtung benötigen einen begrenzten gemeinsamen Ablauf.

Deshalb: **ausführbares lokales Artefakt vorhanden, vollständige Server-Abnahmebereitschaft noch nicht erreicht**. Nächste Arbeit gezielt an diesen Lebenszykluspunkten; keine weitere allgemeine Konzeptausweitung. Stress-/Abbruch-/OOM-Ausführungen sind nicht über diesen Einstieg freigegeben. Recoverybericht ist keine Backupwiederherstellung.

Keine Serveränderung, kein neues Backup, keine Produktfreigabe.

| Quelle | SHA256 |
|---|---|
| contract_lab/linux_runner.py | 6d8d368bb69974d23a09eebb910aae74a86252ffc09242f474a558f2119bd6ed |
| contract_lab/linux_backend.py | 041157b7507517a3021587a10ee61b100a35694cd2cb6c30cd147601e9dfdadf |
| tests/test_contract_linux_runner.py | 10e52345be16f0166afc551dd19814a65b0e6b62804fa92885585a6a9548e6f1 |
