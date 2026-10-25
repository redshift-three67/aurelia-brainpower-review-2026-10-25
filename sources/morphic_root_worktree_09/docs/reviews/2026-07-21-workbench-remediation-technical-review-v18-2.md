## Zweites adversariales Freeze-v18-Review

**Verdikt: REQUEST CHANGES**  
**Konfidenz: HOCH**  
**Befunde:** `P0=0, P1=2, P2=2, P3=0`  
**Scope-Drift:** `0`

### Befunde

| Priorität | Befund | Ort |
|---|---|---|
| **P1** | **Windows-Recovery verwirft weiterhin gültige Job-Object-Autorität bei beendetem oder wiederverwendetem Supervisor-PID.** `_recover_jobs()` bestimmt Aktivität über `process.poll() is None or _process_group_alive(...)`; letzteres liefert unter Windows immer `False`. Ist der Supervisor beendet, wird der Job daher auf `failed` festgelegt, ohne das benannte Job Object über `_windows_job_active()` zu öffnen und abzufragen. Auch `stop()` kehrt bei Creation-Time-Mismatch vor der Job-Abfrage als `failed` zurück. Ein aktiver Job-Nachfahre kann dadurch nach echtem Serviceprozess-Neustart nicht mehr gestoppt werden. | `apps/web/scan_jobs.py:303-305,946-975,1129-1136` |
| **P1** | **Im Test-Cleanup verbleibt eine numerische PID-Signalisierung.** Der `finally`-Block prüft `pid_exists(child_pid)` und ruft danach `os.kill(child_pid, SIGKILL)` auf. Zwischen Prüfung und Signal kann die PID wiederverwendet werden; dann kann der Test einen fremden Prozess beenden. Das widerspricht ausdrücklich dem Freeze-v18-Vertrag „no numeric test cleanup“. | `tests/test_web_scan_jobs.py:1622-1624` |
| **P2** | Der Windows-„Restart“-Realtest erzeugt nur eine zweite Serviceinstanz im selben Python-Prozess. Die erste Instanz und ihr eigener Job-Handle bleiben erhalten. Damit falsifiziert der Test weder das Ende des ursprünglichen Handle-Eigentümerprozesses noch Recovery nach geschlossenem letztem Service-Handle; außerdem bleibt der oben genannte Supervisor-Endfall ungedeckt. | `tests/test_web_scan_jobs.py:1250-1283` |
| **P2** | Beim Fehlschlag von `AssignProcessToJobObject()` wird das Ergebnis von `CloseHandle()` verworfen. Ein Close-Fehler wird weder propagiert noch mit dem Assignment-Fehler gruppiert, obwohl Freeze v18 fehlertransparentes Handle-Cleanup behauptet. | `apps/web/scan_jobs.py:458-464` |

### Erforderliche Korrekturen

1. In der Windows-Recovery zuerst das rekonstruierte Jobobjekt erstellen und `_windows_job_active()` unabhängig vom Supervisorzustand ausführen. PID/Creation-Time darf Windows-Job-Autorität nicht vorzeitig verwerfen.
2. Im Windows-Stop-Pfad einen PID-Mismatch nicht vor der Job-Object-Abfrage als terminal behandeln.
3. Numerisches `os.kill(child_pid, ...)` aus dem Cleanup entfernen; ausschließlich die stabile Service-/Jobautorität erneut verwenden.
4. Einen echten separaten Windows-Serviceprozess-Test ergänzen, bei dem der ursprüngliche Handle-Eigentümer endet.
5. `CloseHandle`-Fehler im Assignment-Fehlerpfad erhalten und gemeinsam mit dem Primärfehler melden.

### Bestätigte Aspekte

- POSIX-Discovery ist tokenweit und nicht auf den PGID beschränkt; `setsid()`/`setpgid()`-Nachfahren bleiben grundsätzlich auffindbar.
- Fremde Benutzernamen werden vor `environ()` ausgeschlossen; unbekannte beziehungsweise gleichnamige unlesbare Provenienz schlägt fail-closed fehl.
- Token wird nach `pidfd_open()` erneut validiert.
- Übertragene und aktuelle Deskriptoren werden bei Fehlern bestmöglich geschlossen; Signalrunden werden zur Konvergenz neu enumeriert.
- Produktiv existiert kein numerischer `taskkill`-/`killpg`-Signalpfad.
- Der unveränderte frühere Produktscope wurde über die v17-Reviews und identischen Scope-Hashes gegen Auth-, Ownership-, Persistenz-, Hardware-, Polling-, Reset-, Telemetrie- und Accessibility-Befundklassen abgeglichen; kein zusätzlicher P0–P3-Befund.

### Freeze-v18-Bindung

Start und Ende waren identisch:

- Branch: `operator-workbench-phase1`
- HEAD: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- Manifest-SHA-256: `f949f7feffd8a810e0a712816610ddd03a2b47817f3ca4875348a6b811c5e0e2`
- Einzelhashes: **109/109 OK**
- Aggregat: `5e4883d95c5d75ab744f81d5fcce88b4c418d1a133a3be6beac966e5bd1b322e`
- Population: **110**
- Scope minus Dirty: leer
- Dirty minus Scope: leer
- Status-Fingerprint: `85411056fd56f11b56b44c61abde6d4c5841fc998b2866b05aa6135468b5523f`
- Drift: **keine**

### Ausführung

- Keine Dateien erstellt, verändert oder gelöscht.
- Keine Tests, Projektimporte, Netzwerkzugriffe oder Produktprozesse ausgeführt.

**Endgültiges Verdikt: `REQUEST CHANGES — P0=0, P1=2, P2=2, P3=0; null Scope-Drift`.**