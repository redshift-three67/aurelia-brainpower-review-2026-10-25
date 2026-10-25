## Freeze-v18-Abschlussreview

**Verdikt: REQUEST CHANGES**  
**Konfidenz: HOCH**  
**Befunde:** `P0=0, P1=1, P2=1, P3=0`  
**Scope-Drift:** **keine**

### Befunde

| Priorität | Befund | Ort |
|---|---|---|
| **P1** | **Windows-Recovery verwendet die neue Job-Object-Aktivitätsprüfung nicht.** `_recover_jobs()` entscheidet weiterhin mit `process.poll() is None or _process_group_alive(...)`. `_process_group_alive()` liefert unter Windows grundsätzlich `False`. Ist der Supervisor beendet oder seine PID wiederverwendet, während ein Job-Nachfahre noch lebt, wird der wiederhergestellte Job daher als `failed` fixiert. `_snapshot()` überspringt anschließend wegen `forced_status == "failed"` die `QueryInformationJobObject`-Prüfung. Der Nachfahre kann zwar über einen späteren expliziten `stop()` noch gefunden werden, Recovery- und Snapshot-Status sind aber falsch und die behauptete Windows-Lifecycle-Closure ist nicht erfüllt. | `apps/web/scan_jobs.py:303-305`, `apps/web/scan_jobs.py:946-975`, `apps/web/scan_jobs.py:1188-1205` |
| **P2** | **Die behauptete adversariale Windows-Recovery-Abdeckung fehlt.** Der native Restart-Test erzeugt nur eine zweite Serviceinstanz, während erster Service, Supervisor und ursprünglicher Handle-Eigentümer weiterleben. Es gibt keinen Windows-Test „Supervisor beendet, Nachfahre aktiv, Recovery meldet running“. Das Remediation-Dokument behauptet diesen Vertrag dennoch als geschlossen. `test_scan_restart_fails_closed_when_pid_identity_changed` erwartet zwar indirekt Job-basierte Recovery, widerspricht auf Windows aber dem aktuellen `_recover_jobs()`-Pfad. | `tests/test_web_scan_jobs.py:1250-1283`, `tests/test_web_scan_jobs.py:1286-1317`, `docs/superpowers/plans/2026-07-21-workbench-freeze-v17-review-remediation-v18.md:11,17` |

### Bestätigte Teilbereiche

- Windows Stop und Rollback fragen Job-Aktivität unabhängig vom Supervisor ab.
- `QueryInformationJobObject` verwendet `ActiveProcesses`; fehlende/unlesbare Autorität bleibt mehrdeutig.
- Gehaltene sowie recovery-geöffnete Windows-Handles besitzen nachvollziehbare Close-Pfade; natürlicher Abschluss schließt den gehaltenen Handle.
- POSIX enumeriert tokenweit über Same-Owner-Prozesse und erfasst damit geerbte Token auch nach `setsid()`/neuer Session.
- Kandidaten werden vor und nach `pidfd_open()` tokenvalidiert; fremde Mitglieder der ursprünglichen PGID führen fail-closed zur Mehrdeutigkeit.
- pidfd-Cleanup versucht alle übertragenen Handles; Signalisierung erfolgt nicht per numerischem `killpg`.
- Im produktiven und ausführenden Testcode existiert kein `taskkill`; die einzigen Vorkommen sind negative Assertions.
- Der übrige Produkt-/Security-Scope ist gegenüber v17 byte-identisch; außerhalb der genannten Windows-Recovery-/Evidenzlücke ergab die erneute Prüfung keinen zusätzlichen P0–P3-Befund.

### Freeze-v18-Bindung

Start und reservierte Endbindung stimmen exakt überein:

- Branch: `operator-workbench-phase1`
- HEAD: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- Manifest-SHA-256: `f949f7feffd8a810e0a712816610ddd03a2b47817f3ca4875348a6b811c5e0e2`
- Einzelhashes: `109/109 OK`
- Hashzeilen-Aggregat: `5e4883d95c5d75ab744f81d5fcce88b4c418d1a133a3be6beac966e5bd1b322e`
- Population/Scope: `110/110`
- Scope minus Dirty: leer
- Dirty minus Scope: leer
- Status-Fingerprint: `0f0d8e49eec1fa0a0f611aeb9164508588a1d28c26459da668b73449926a1d7f`
- Drift: **keine**

### Ausführung

- Keine Dateien erstellt, verändert oder gelöscht.
- Keine Tests, Projektimporte oder Produktprozesse ausgeführt.
- Keine technischen Probleme bei der read-only Prüfung.

**Endgültiges Verdikt: `REQUEST CHANGES — P0=0, P1=1, P2=1, P3=0; null Scope-Drift`.**