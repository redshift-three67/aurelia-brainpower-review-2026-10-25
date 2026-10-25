# REQUEST CHANGES

**Konfidenz:** HOCH  
**Befundzählung:** `P0=0, P1=1, P2=0, P3=0`

## Freeze-, Scope- und Driftbindung

| Prüfung | Start | Ende |
|---|---:|---:|
| Branch | `operator-workbench-phase1` | identisch |
| HEAD | `3271ff9366ab3fecb2a158913a0cc19ed6a06726` | identisch |
| Freeze-SHA-256 | `ddca521250a8b3f558a71ccc42617499e04a2ed770b8b6aaa3b6887c00c9a3ef` | identisch |
| Manifestdateien | 69 | 69 |
| Einzelhashes | 69/69 OK | 69/69 OK |
| LF-Aggregat | `a0554a01566728c34a3a00810bd25576b7eaf22c876ae1c3607d12ebb3536530` | identisch |
| Dirty-Population | 70 | 70 |
| Scope + Freeze | 70 | 70 |
| Dirty minus Scope | 0 | 0 |
| Scope minus Dirty | 0 | 0 |
| Drift | keine | keine |

## Finding

### P1 — Recovery/Stop kann nach Supervisor-PID-/PGID-Reuse eine fremde POSIX-Prozessgruppe übernehmen und töten

**Evidenz:**

- `apps/web/scan_jobs.py:272-276` validiert die gespeicherte Supervisor-PID mittels Creation-Time.
- `apps/web/scan_jobs.py:279-291` erklärt eine Gruppe jedoch allein aufgrund der numerischen PGID und irgendeines nicht-zombierten Mitglieds für aktiv; Herkunft oder Creation-Time der Gruppenmitglieder werden nicht geprüft.
- `apps/web/scan_jobs.py:462-467` akzeptiert bei Recovery eine lebende numerische PGID ausdrücklich auch dann, wenn `_RecoveredProcess.poll()` wegen nicht passender Supervisor-Identität bereits fehlgeschlagen ist.
- `apps/web/scan_jobs.py:610-617` führt die PID-Identitätsprüfung beim Stop nur aus, wenn der gespeicherte Supervisor noch als aktiv gilt.
- Ist dessen PID inzwischen wiederverwendet und die neue fremde Gruppe trägt dieselbe PGID, läuft der Pfad über `group_active=True`, `supervisor_active=False`; anschließend sendet `apps/web/scan_jobs.py:633-660` `SIGTERM` beziehungsweise `SIGKILL` an diese fremde Gruppe.
- Der angebliche Reuse-Test `tests/test_web_scan_jobs.py:410-439` deckt das nicht plattformneutral ab: Auf POSIX bleibt die echte gespeicherte Gruppe während des Tests aktiv. Daher würde `_process_group_alive()` trotz injizierter Creation-Time-Abweichung `True` liefern und die erwartete Einstufung als `failed` verhindern.
- Die neuen Tests `tests/test_web_scan_jobs.py:275-320` beweisen nur numerische Gruppenlebendigkeit und Gruppen-Kill. Der echte POSIX-Test `tests/test_web_scan_jobs.py:654-690` beweist Crash/Restart/Stop, simuliert aber keine PID-/PGID-Wiederverwendung oder fremde Gruppenprovenienz.

**Auswirkung:** Nach PID-/PGID-Wiederverwendung kann ein alter Scan als laufend rekonstruiert werden und `stop()` Prozesse eines unabhängigen Workloads terminieren. Damit ist der explizite v8-Vertrag „fail closed bei PID/PGID reuse oder fremder Gruppe“ nicht erfüllt.

**Erforderliche Korrektur:** Die Gruppenautorität muss an dauerhaft überprüfbare Provenienz gebunden werden, nicht nur an die numerische PGID. Bei fehlender positiver Provenienz muss Recovery/Stop fehlschließen und darf kein `killpg()` ausführen. Zusätzlich ist ein POSIX-Test erforderlich, der eine abweichende Supervisor-Identität bei numerisch lebender/fremder PGID simuliert und sowohl `running` als auch `killpg()` ausschließt.

## Übrige v8-Prüfung

Ohne weitere P0–P3-Befunde geprüft:

- **POSIX-Leader-Exit:** Der Supervisor prüft nun nicht-zombierte PGID-Mitglieder in `services/scan_process_gate.py:121-136,139-164`; die reine Parent/Child-Lücke aus v7 ist geschlossen.
- **Windows-Pfad:** Gate-Skript und produktiver Prozess werden mit explizitem Interpreter, `shell=False`, Windows-Creation-Flags und unveränderter Job-Object-Grenze gestartet (`apps/web/scan_jobs.py:81-84,517-555`); keine neue Windows-Pfadregression gefunden.
- **Partieller Hardware-Spawn:** Jeder erfolgreiche Start wird sofort registriert und durch das gemeinsame `finally` konvergiert (`services/hardware_modulation.py:305-318,340-344,401-402`); adversarialer Zweitspawn-Test in `tests/test_harmonization_worker_pulse_pause_execution.py:229-278`.
- **Durable Harmonisierung:** Snapshot und Stopmarker delegieren an `durable_write_bytes` (`services/harmonization_worker.py:28,79-80,147-155,801-812`); Delegations-/Fehlerverträge in `tests/test_web_durable_io.py:73-128`.
- **Polling:** Job-/Generation-/Revision-Ownership und success-clear sind vorhanden (`apps/web/static/app.js:25-35,61-76,397-404,684-696`). Manueller Scan-Retry ist sichtbar und an die aktuelle Job-/Generation-Autorität gebunden (`apps/web/static/index.html:478-480`; `apps/web/static/app.js:455-464,1206-1210`), mit Browserabdeckung in `tests/browser/workbench.spec.js:559-638`.
- Gesamter produktiver v7→v8-Änderungsumfang und transitive Tests wurden auf neu eingeführte P0–P3-Regressionsklassen geprüft.

## Abschluss

Freeze v8 ist **hash-, scope- und driftkonsistent**, erfüllt wegen des offenen POSIX-Reuse-Befunds aber nicht den vorgeschriebenen Nullbefundvertrag.

- Tests, Imports, Server, Netzwerk und Installationen: **nicht ausgeführt**
- Dateien erstellt, geändert oder gelöscht: **keine**
- Probleme bei der Prüfung: **keine**, abgesehen von harmlosen LF/CRLF-Git-Hinweisen