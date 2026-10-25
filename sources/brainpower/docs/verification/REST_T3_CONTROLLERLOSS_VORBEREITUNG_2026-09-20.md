# T3c: Controllerverlust, konkrete Vorbereitung

Betreiberfreigabe erteilt; Paket und Helfer übertragen, beide Serverhashes identisch mit lokalen Artefakten. Noch kein Linux-Lauf. Einmaliger neuer Testlauf `0ea5c17104524676939cf6b86926481b`. Keine Verbindung mit Governor-/Produktjournalen.

## Festgelegter Ablauf

1. Geschützte vorhandene Pakete und neue Archivhashes prüfen; exklusiver neuer Runnername verhindert versehentliche Wiederholung. Mindestens 2 GiB MemAvailable erforderlich.
2. Eigenen begrenzten systemd-Worker im bestehenden Modus ignore_term starten. Identität dauerhaft im Testjournal speichern, zwei laufende Prozesse beobachten und eigenen Startbeleg fsyncen.
3. Nur dieser Testcontroller beendet sich abrupt mit `os._exit(73)`, ohne Python-Aufräumen oder Journalabschluss. Das ist Prozessverlust, kein Serverabsturz/Neustart und kein Test eines Stromausfalls.
4. Helfer verlangt exakt Rückgabecode 73; danach eigener neuer Recoveryprozess. Er übernimmt die OS-Dateisperre und erkennt den alten Journalzustand als unknown. Identität und Manifest müssen zum vorherigen Startbeleg passen.
5. Worker muss zu Beginn noch nachweislich laufen. Dieser ungeklärte laufende Zustand wird dokumentiert und nicht freigegeben. Kein erneuter Start und kein Stop-/Kill-Befehl gegen den Worker.
6. Bis zu 30 Sekunden Beobachtungsbudget auf unabhängig belegtes Ende warten; systemd RuntimeMaxSec20s plus Stopfrist2s begrenzen den Worker. Die 30 Sekunden ersetzen nicht die bestehende 5-Sekunden-Abbruchprüfung. Einzelne begrenzte Abfragen können über die Budgetgrenze hinaus zurückkehren; ein verspäteter Endebeleg wird abgelehnt, keine harte Gesamtlaufzeitgarantie.
7. Bestehende geprüfte Cleanup-Verbindung verlangt passenden timeout/SIGKILL-Endebeleg und entfernte cgroup. Bericht sichern, Journal released_unknown, eigene Unit und Staging zurücknehmen, Fremddienste vergleichen. Erst dann controller_loss_verified.

Fehlender/falscher Beleg, zu frühes Ende (kein Beleg für weiterlaufenden Worker nach Verlust), noch laufender Worker nach Budget oder Dienstabweichung: blocked, keine Wiederholung. Kein automatisches fachliches Erfolgsergebnis. Der Helfer begrenzt jeden seiner zwei Controller-Unterprozesse auf 45 Sekunden; bei Timeout ist der Zustand gesondert zu prüfen.

## Lokale Prüfungen und Artefakte

Gesamte lokale Suite: **203 Tests bestanden**, 0 Fehler/Skips, 39,459 Sekunden (`python -B -m unittest discover -s tests -p 'test_contract*.py' -q`). Kein bereits erfolgter Linux-Nachweis.

Acht gezielte Tests bestehen: durabler Beleg vor abruptem Exit, Schreibfehler verhindert absichtlichen Exit, keine Freigabe bei weiterlaufendem Worker, Bindungsabweichung, zu frühes Ende, Übergabe an geprüfte Rücknahme, Identitätswechsel sowie echter lokaler Python-Prozessabbruch. Letzterer zeigt Journalpersistenz, Freigabe der OS-Dateisperre und unknown beim Nachfolger. Mock-Backend dieses lokalen Prozesses startet keinen Linux-Worker.

- `artifacts/rest-t3-loss-20260920.pyz`, elf Module bytegeprüft: SHA256 `d9db9d134c20acba8a4e857914f4ce9e1d848444378eab308c817f402e05bda7`.
- `artifacts/server-t3-loss-20260920.py`, Syntax geprüft: SHA256 `cca2750440f522fc37f6994beceed0bf60a993edaa68ca75893fd855d3d7a6af`.
- Nach konkreter Freigabe und Abwesenheitsprüfung nach `/home/klaus999/t3loss20.pyz` und `/home/klaus999/bpt3loss20` übertragen; beide Hashes auf Ubuntu bestätigt. Nächster einmaliger Root-KVM-Befehl: `python3 /home/klaus999/bpt3loss20`. Nicht wiederholen.
- Geplanter Export `/home/klaus999/t3loss20-report.json`. Keine Produktfreigabe und kein Ersatz für den noch offenen vollständigen korrigierten Abbruchlauf.
