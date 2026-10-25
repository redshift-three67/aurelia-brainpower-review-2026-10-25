# T3 – Controllerablauf lokal geprüft

20.09.2026: **136 Tests bestanden, 0 Fehler, 0 Skips, 38,072 Sekunden**. 15 neue Controllertests. Die Betriebssystemaktionen des Backends sind synthetisch; die SQLite-Transaktionen und Windows-Dateisperren werden tatsächlich ausgeführt, einschließlich konkurrierendem separatem Python-Prozess.

```powershell
& 'C:/Users/Hubert111/AppData/Local/Programs/Python/Python312/python.exe' -B -m unittest discover -s tests -p 'test_contract*.py' -q
```

| Bereich | Geprüftes Verhalten |
|---|---|
| Exklusivität | OS-Dateisperre vor Journalöffnung. Zweiter Controller kann weder übernehmen noch den aktiven Journalzustand auf unknown umstellen. Separater Prozess kann gehaltene Sperre ebenfalls nicht übernehmen. Sperrdatei bleibt bestehen; kein Unlink mit nachfolgend zwei unterschiedlichen Sperrinodes. |
| Start | Paketprüfung → Backend-Vorprüfung → erneute Paketprüfung → dauerhafte Reservierung → externer Start → Identitätsprüfung → gestarteter Beleg. Eine aktive Reservierung sperrt einen zweiten Start. |
| Startunsicherheit | Startfehler oder Fehler beim Speichern des Startbelegs lassen die Reservierung bestehen; kein Retry, Stop oder Dateilöschen aus diesem Fehlerpfad. |
| Drift | Paketänderung vor oder während Vorprüfung verhindert den Start. Der zusätzliche Drift-Test war zunächst rot und führte zur zweiten Paketprüfung. |
| Stop | Gespeicherte Identität und frische laufende Beobachtung müssen übereinstimmen. Abbruchanforderung vor Stop speichern, nach Stop unabhängig ended verlangen. Ohne Endebeleg bleibt Slot belegt. |
| Wiederaufnahme | Kein automatischer Start. Bei zuvor unknown bleibt auch nach technischem Stop-Ende der fachliche Ausgang released_unknown. |
| Schließen | Controllerclose schließt Journal und gibt Sperre frei. Spätere Aktionsaufrufe derselben Instanz gesperrt. |

## Noch nicht umgesetzt / nicht behauptet

`contract_lab/linux_controller.py` verbindet die Ablaufregeln, hat aber absichtlich **keinen voreingestellten privilegierten Backend-Executor**. Ein vollständiger serverseitiger Runner fehlt weiterhin. Die Test-Backendantworten sind keine echten Linux-Befunde und kein Schutz gegen ein böswilliges Backend.

Als nächster konkreter Baustein ist das Linux-Backend erforderlich: root-eigene, gegen fremde Schreibzugriffe geschützte Ablage, echte Runtime-/Unit-Prüfung, Paketübertragung zum festen Ausführungspfad, tatsächliche systemd-Aufrufe, Identitätserfassung und begrenzte Beobachtung bis Ende. Danach folgt die gezielte Dateirücknahme und ein vollständiger Paket-/Root-Aufruf. Diese Sicherheitsprüfungen dürfen nicht nur aus der Existenz der preflight-Methode abgeleitet werden.

Die verbleibende Start-/Speicherlücke wird konservativ gesperrt, noch nicht automatisch aufgelöst. Unterschiedliche Sperrpfade oder ein direkt am Controller vorbei geöffnetes Journal sind nicht durch diese lokale Vereinbarung verhindert; das Backend muss die Pfade fest binden. Der POSIX-flock-Zweig ist vorhanden, aber hier nicht ausgeführt. Elternpfad-/Symlink-Races, privilegierte Fremdaktionen und atomare Prüfung-plus-Stop sind nicht abgenommen. Eine bereits beendete oder nicht mehr beobachtbare Unit wird von stop nicht als bestätigter Abbruch behandelt; dafür bleibt ein gesonderter Recoverypfad erforderlich.

Keine Serverdatei/Dienstkonfiguration verändert. Workerpaket unverändert; kein neues Backup, kein UI-/Governorcode geändert und keine Produktfreigabe. Vor Serverausführung bleibt das komplette konkrete Paket erforderlich.

| Datei | SHA256 |
|---|---|
| contract_lab/linux_controller.py | 6254b834a8f40f16a5a231332bc2bffd2490cd1a2ae9f3f4968cd7e5babba478 |
| tests/test_contract_linux_controller.py | 1294cc1dfe9c66c2ef67de9182289633fe50eb6decfc6e424232b2a53d3da7ab |
