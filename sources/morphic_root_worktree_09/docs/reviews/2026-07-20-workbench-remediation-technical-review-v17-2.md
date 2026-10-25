## Zweites adversariales Freeze-v17-Review

**Verdikt: REQUEST CHANGES**  
**Konfidenz: HOCH**  
**Befunde:** `P0=0, P1=2, P2=2, P3=0`  
**Scope-Drift:** `0`

### Befunde

| Priorität | Befund | Ort |
|---|---|---|
| **P1** | Die POSIX-Autorität umfasst lediglich die persistierte Prozessgruppe, nicht den vollständigen Nachfahrenbaum. Ein produktiver Nachfahre kann durch `setsid()`, `setpgid()` oder `start_new_session=True` die Gruppe verlassen. Danach wird er weder von `_process_group_alive()` gefunden noch per pidfd signalisiert; der Supervisor kann den Baum trotzdem als beendet melden. Der Realtest erzeugt nur ein Kind, das die Gruppe erbt, und falsifiziert diesen Escape nicht. | `services/scan_process_gate.py:121-136,160-173`; `apps/web/scan_jobs.py:303-344,510-591`; `tests/test_web_scan_jobs.py:1550-1586` |
| **P1** | Im Testscope verbleiben drei numerische `taskkill /PID`-Grenzen. Zwischen `pid_exists()`/`tasklist` und `taskkill` kann die PID wiederverwendet werden, sodass die Tests einen fremden Prozessbaum beenden können – genau die TOCTOU-Klasse, die v17 produktiv beseitigen soll. Der plattformübergreifende Test bei Zeile 1444 verwendet im Cleanup sogar auf POSIX `taskkill`, wodurch ein ursprünglicher Fehler maskiert und ein Survivor zurückgelassen werden kann. | `tests/test_web_scan_jobs.py:1193-1200,1234-1241,1473-1479` |
| **P2** | Windows-Job-Handles werden nur nach erfolgreichem explizitem `TerminateJobObject` geschlossen. Bei natürlichem Abschluss verbleibt `windows_job_handle` unbegrenzt im Jobobjekt; es gibt weder terminales Close in `_snapshot()` noch Service-Shutdown-/Eviction-Cleanup. Zusätzlich werden `CloseHandle`-Fehler ignoriert und der gespeicherte Handle dennoch auf `None` gesetzt. Wiederholte Scans können daher Kernel-Handles leaken. | `apps/web/scan_jobs.py:438-489,1075-1161` |
| **P2** | Der Windows-„Restart“-Test erzeugt lediglich eine zweite Serviceinstanz im selben Python-Prozess. Die erste Instanz und ihr ursprünglicher Job-Handle bleiben aktiv. Damit wird zwar `OpenJobObjectW` indirekt verwendet, aber nicht der entscheidende Neustartfall nach Ende des ursprünglichen Handle-Eigentümerprozesses bzw. Schließen dessen letzten Service-Handles geprüft. | `tests/test_web_scan_jobs.py:1203-1241` |

### Windows-Revalidierung

Ohne zusätzlichen Befund bestätigt:

- `CreateJobObjectW`, `AssignProcessToJobObject`, `OpenJobObjectW`, `TerminateJobObject`, `QueryInformationJobObject` und die verwendeten Strukturen/Pointerbreiten sind für den Zielpfad plausibel deklariert.
- `JOB_OBJECT_TERMINATE` (`0x0008`) ist für `OpenJobObjectW` ausreichend.
- Der Jobname wird einwegig aus einem zufälligen 128-Bit-Token abgeleitet und nicht über API-Snapshots veröffentlicht.
- Der Gate-Supervisor wird vor Veröffentlichung der Release-Datei dem benannten Job zugeordnet; vor erfolgreicher Zuordnung kann kein produktiver Nachfahre starten.
- Windows-Jobvererbung verhindert gewöhnlichen Child-Breakaway, da keine Breakaway-Limits gesetzt werden.
- Assignment-Fehler beenden vor Freigabe nur den bereits geöffneten Supervisor-Handle; Termination-Fehler werden nicht als erfolgreicher Stop ausgegeben.
- Produktiv existiert kein `taskkill`, `killpg` oder anderer numerischer finaler Windows-Signalpfad mehr.
- Die PID-/Creation-Time-Matrix und die POSIX-pidfd-Cleanup-/Ambiguitätszweige sind ansonsten schlüssig abgedeckt.

### Freeze-v17-Bindung

Start- und reservierte Endbindung stimmen überein:

- Branch: `operator-workbench-phase1`
- HEAD: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- Manifest-SHA-256: `ccb996eb4c167b525581d384f44c6dcfe3e97a94043504903a5731fe092948ce`
- Einzelhashes: **105/105 OK**
- Hashzeilen-Aggregat: `92309bc9a7b86d16774f861ad5cb680505b7fc092e7c4b4d4d930905f45746aa`
- Exakte Population: **106**
- Scope-Differenz: leer
- End-Status-Fingerprint: `64e8ca6a0038bc269cb429e528dc633db66fb851ba3b1b27ad41a5be8c7bd7ac`
- Drift: **keine**

### Ausführung

- Keine Dateien erstellt, verändert oder gelöscht.
- Keine Tests, Projektimporte oder Produktprozesse ausgeführt.
- Drei anfängliche Inline-Python-Quotingfehler hatten keine Seiteneffekte; die korrigierte Startprüfung und die vollständige Endbindung waren erfolgreich.

**Endgültiges Verdikt: `REQUEST CHANGES — P1=2, P2=2, null Scope-Drift`.**