# RadiWorks C23 — Dauerübernahme vom 05.10.2026

Die ausdrücklich genehmigte Übernahme ist abgeschlossen. Alle sieben Dauerinstanzen **8103–8109** starten den geprüften C23-Release (`runtime/rw-c23-release-20261005`, 131 unveränderte Produktdateien). Original bleibt Standard; der optional wählbare Experimentalvergleich läuft getrennt mit dem bestehenden Radi144-CPU-Profil (80.000 Kandidaten, höchstens 21 ausgewählte Raten). Kein Originalzahlen-/Broadcast-Algorithmuswechsel durch den Startadapter.

## Daten und Betrieb

- **13 API-Fälle und 19 Fall-Dateien erhalten**, bytegleich zur geschlossenen Vorher-Sicherung. Pro Port: 3/2/2/1/3/2/0 Fälle. Keine Fallinhalte wurden ausgegeben oder in das portable Paket übernommen.
- Die vom Betreiber zur Beendigung freigegebenen Broadcasts sind beendet; Queue und Auto-Modus waren beim Wechsel ruhig. Kein Wiederanlauf alter Broadcast-Aufträge.
- Home, Scope, aktueller Katalog und Clarke-Bestand bleiben unverändert. Der vorhandene externe E:-Fernet-Schlüssel wird auf 8103 weiterverwendet. Die übrigen sechs Instanzen behalten ihre vorherige Seed-Konfiguration ohne Stochastic-Recoveryschlüssel; für sie wurde keine neue Stochastic-Freigabe behauptet.
- Alle acht bestehenden Windows-Aufgaben sind wieder aktiviert. Actions, Triggers, Principals und Settings wurden vor/nach dem Wechsel exakt verglichen. Der angemeldete Benutzer bleibt zuständig; ein Windows-Neustart wurde heute nicht durchgeführt. Der Start über Aufgabenplanung ist unabhängig vom Codex-Chat.
- 8104 wurde über den eigenen Stopflag geordnet beendet (`exitClean=true`) und aus derselben Aufgabe neu gestartet. Fallbytes und Scope bleiben gleich. Auf allen sieben Ports stimmen Listener-PID, Prozessstart, konkrete Startargumente, Prozessbilder und Scheduler-Abstammung mit der neuen Serviceidentität überein.
- 8110 bleibt der **ältere synthetische Pilot**, unverändert; für den aktuellen Live-Stand 8103–8109 verwenden. Radi144/8090 wurde nicht berührt.

## Sicherungspunkt und Grenzen

Die geschlossene private Vorher-Sicherung liegt im Pfad aus [BACKUP_TARGET.json](../../runtime/rw-c23-rollout-20261005/BACKUP_TARGET.json): 272 Dateien, 246.870.167 Bytes, SHA-256-Rückleseprüfung; keine SQLite-Dateien im Altbestand erkannt. Vererbungsfreie ACL für Eigentümer und SYSTEM, externe Schlüssel nicht kopiert. Die private Sicherung enthält Fall-/Laufzeitdaten und gehört nicht in ein Testpaket. Wiederherstellungsanleitung liegt dort als `RESTORE.md`; Code-Rollback berücksichtigt auch die alten `instance.json`-Hostmarker. Bei normaler Fortsetzung keine älteren Falldaten zurückspielen.

Dies ersetzt **keine neue vollständige F:-Gesamtprojektsicherung**. Kanonischer RadiWorks-Quellordner, Modul_Templates und Aurelia bleiben separate Synchronisations-/Freigabepakete. S4.8 ist weiterhin nicht freigegeben.

## Nachweise

[Alle sieben APIs/Fall-/Produktbytes](../../runtime/rw-c23-rollout-20261005/ALL_TRANSFER_RESULT.json) · [Prozess-/Portautorität](../../runtime/rw-c23-rollout-20261005/LISTENER_AUTHORITY_VERIFIED.json) · [Taskdefinitionen](../../runtime/rw-c23-rollout-20261005/TASKS_AFTER_VERIFIED.json) · [Neustart](../../runtime/rw-c23-rollout-20261005/LIVE_RESTART_PROBE.json) · [Fallprüfung nach Neustart](../../runtime/rw-c23-rollout-20261005/RESTART_VERIFIED.json) · [Live-Browser](../../runtime/rw-c23-rollout-20261005/LIVE_BROWSER_VERIFIED.json).

19 Wrapper-/Lifecycle-Tests bestanden, inklusive realer TCP-Prozesse, Portkollision vor App-/Recoveryöffnung, doppelter Homebelegung, sauberem Stop/Restart und sichtbarem Shutdownfehler. Sieben zusätzliche Browserprüfungen auf 8104 bestanden ohne Fall-/Auftragsmutation. Astra-Reviewbefunde zu Portreservierung, ExitClean und separat belegter Prozessautorität sind behoben; Review ist keine Betreiber-/Aureliafreigabe. Der C23-Produktcode selbst blieb unverändert; dessen vorherige 674 CPU-PASS/3 Windows-Skips gelten ergänzend, keine unnötige Wiederholung der gesamten Suite.

| Phase | Stand dieses begrenzten Pakets |
|---|---|
| C23-Dauerübernahme + Fallbewahrung | **100% geprüft** |
| Portable5 Offline-Windows-Testpaket | in Umsetzung und anschließender praktischer Prüfung |
| Test auf weiterem PC / persönliche C23-Abnahme | offen |
| Kanonischer Quell-/Modul_Templates-/Aurelia-Abgleich | separat offen |
| Neue vollständige F:-Gesamtsicherung / S4.8 | offen / keine Freigabe |

Tatsächlich eingesetzte Helfer: Luna6/max für den begrenzten Paketbau; Astra6/medium für die unabhängige kritische Service-/Übernahmeprüfung. Root integriert, prüft und hält die Daten-/Betriebsgrenzen. Keine gemessene Tokenersparnis.
