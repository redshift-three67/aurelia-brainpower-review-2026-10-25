## Freeze-v20-Review

**Verdikt:** **REQUEST CHANGES**  
**Konfidenz:** Hoch  
**Befunde:** **P0=0, P1=0, P2=1, P3=0**  
**Scope-Drift:** **0**

### Befund

| Priorität | Befund | Ort |
|---|---|---|
| **P2** | Der neue POSIX-Startup-pidfd-Pfad ist nicht vollständig exception-safe. Schlägt `pidfd_send_signal()` bei fehlender Creation-Time fehl, wird der vorab geöffnete pidfd nicht in einem `finally` geschlossen und der Gate-Prozess nicht abgewartet. Schlägt anschließend das Schließen des pidfd fehl, wird vor `process.wait()` geworfen, sodass der terminierte Supervisor unreaped bleiben kann. Der Crash-Injection-Test schließt seinen pidfd ebenfalls nicht per `finally` und deckt diese Fehlerpfade nicht ab. | `apps/web/scan_jobs.py:1119-1132`, `tests/test_web_scan_jobs.py:1702-1707` |

### Bestätigte Closures

- POSIX öffnet den Startup-pidfd unmittelbar nach `Popen` und vor der Creation-Time-Ermittlung.
- Der POSIX-Identity-Failure-Normalpfad signalisiert über `pidfd_send_signal`; kein erreichbarer POSIX-`Popen.kill()`-Pfad festgestellt. Die verbleibenden `process.kill()`-Aufrufe sind Windows-Zweige.
- Die POSIX-Crash-Injection verwendet pidfd statt numerischer PID-Signalisierung.
- Windows weist den Gate-Supervisor über dessen vorhandenen `Popen._handle` dem äußeren benannten Job zu und dupliziert dessen Job-Handle mit `DuplicateHandle` in den Gate-Prozess, bevor die Release-Datei veröffentlicht wird.
- Der separate Windows-Eigentümerprozess startet den Job und endet mit `os._exit(0)`; anschließend erfolgen Recovery, handlebasierte Query und `TerminateJobObject` aus einem anderen Prozesskontext.
- Windows Open/Query/Terminate-Handles werden auf den geprüften normalen und wesentlichen Fehlerpfaden geschlossen; Assignment-/Retention- plus Close-Fehler bleiben geordnet erhalten.
- Keine Regression im zuvor geprüften Produkt-/Security-Scope zu Auth, Ownership, Persistenz, Hardware-Cleanup, Polling, Reset, Telemetrie und Accessibility festgestellt.

### Start-/Endbindung

- Branch/HEAD: `operator-workbench-phase1` / `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- Manifest-SHA: `c3fd537a0671861a4fc3378a8baed8f3ab9003cefc10321608f60091272d333d`
- Einzelhashes: **117/117 OK**
- Exaktes Aggregat: `10a5374277197a7f9c5b7e2b4ac6e9c419e7d29c62145a2a70540bfcbebd3087`
- Population: **118**
- Status-Fingerprint Start/End: `6802b63ee53ae9a1befd91d9128510ac11c3fe9103a42656ec21d9a3d6440521`
- Drift: **keine**
- Der abschließende zusätzliche `comm`-Populationvergleich hatte einen Shell-Syntaxfehler; die vollständigen Einzelhash-, Manifest-, Population- und Statusbindungen davor und danach waren erfolgreich und unverändert.

### Ausführung

- Keine Dateien erstellt oder verändert.
- Keine Tests, Projektimporte oder Produktprozesse ausgeführt.