# Zweites unabhängiges Freeze-v6-Review

## Urteil: **REQUEST CHANGES / NO-GO**

**Konfidenz:** HOCH  
**Reviewbindung:** Branch `operator-workbench-phase1`, HEAD `3271ff9366ab3fecb2a158913a0cc19ed6a06726`

## 1. Start-Evidenz

| Prüfung | Ergebnis |
|---|---|
| Git-Toplevel | `C:/morphic_v1/.worktrees/operator-workbench-phase1` |
| Branch | `operator-workbench-phase1` |
| HEAD | `3271ff9366ab3fecb2a158913a0cc19ed6a06726` |
| Freeze-Manifest | `docs/reviews/2026-07-20-workbench-remediation-technical-freeze-v6.sha256` |
| Manifest-SHA-256 | `279a2d365636a9989eb1a9e6cfae74d7eaa9f248ec3e3c8b3c1cb2bae3147e39` |
| Manifest-Einträge | 58 |
| Einzelhashes | **58/58 OK** |
| Pfadsortiertes LF-Aggregat | `d1758106368f9449f4e2b93873f3a1bbedfdd07229dda70a4dd735caf9027b45` |
| Dirty-Population ohne v6-Manifest | 58 |
| Scope-Differenz | leer |
| Population einschließlich Manifest | 59 |
| `git status --short --untracked-files=all` | 59 Pfade |

Der v6-Plan und beide vollständigen v5-Reviews wurden gelesen. Alle **58/58 manifestierten Produktions-, Test- und Evidenzdateien** wurden vollständig geprüft.

## 2. Findings

### F-01 — P1: Scanprozess kann vor seiner dauerhaften Registrierung verwaisen

**Datei:** `apps/web/scan_jobs.py:500-535`

**Adversarialer Ablauf:**

1. `subprocess.Popen()` startet den produktiven Prozess.
2. PID und Erstellungszeit werden ermittelt.
3. Der Webprozess stirbt zwischen `Popen()` und `_snapshot()` beziehungsweise `_persist_job()`.
4. Es existiert kein `*.state.json`.
5. Eine neue `LocalScanJobService`-Instanz kann den laufenden Prozess nicht rekonstruieren, anzeigen oder stoppen.

**Auswirkung:** Unkontrollierte Scanarbeit und mögliche Berichtserzeugung trotz Controller-Restart; der behauptete atomare Start-/Registrierungsvertrag ist nicht erfüllt.

**Minimale Korrektur:** Vor produktiver Arbeit eine dauerhafte `starting`-Reservierung schreiben und den Kindprozess erst nach einem PID-/Creation-Time-Handshake freigeben. Alternativ Prozesslebenszeit zwingend an eine restartfeste Controller-/Job-Object-Autorität binden.

---

### F-02 — P1: Restart-Stop verliert den Prozessbaum, sobald der Gruppenführer endet

**Datei:** `apps/web/scan_jobs.py:276-291,441-472,543-593`

**Adversarialer Ablauf:**

1. Der registrierte Scanprozess startet einen langlebigen Nachfahren.
2. Der registrierte Elternprozess endet, während der Nachfahre weiterarbeitet.
3. `_RecoveredProcess.poll()` liefert terminal, weil nur PID und Creation-Time des Elternprozesses geprüft werden.
4. `stop()` führt den Prozessbaum-Kill nur aus, wenn `poll() is None`.
5. Der bekannte Prozessgruppenbezug wird nicht mehr verwendet; der Nachfahre bleibt aktiv.

**Auswirkung:** Nach Restart kann Status `failed` erscheinen, obwohl produktive Nachfahren weiterlaufen. New Case kann diese Arbeit nicht beenden.

**Minimale Korrektur:** Gruppen-/Job-Object-Lebendigkeit unabhängig vom Führungsprozess prüfen und stoppen. Unter Windows sollte ein dauerhaftes Job Object verwendet werden; unter POSIX muss die gespeicherte PGID auch nach Ende des Leaders geprüft und mit `killpg` beendet werden.

---

### F-03 — P1: Hardware-Overrun bricht nur das Warten ab, nicht die Futures

**Dateien:**  
`services/hardware_modulation.py:336-353`  
`tests/test_harmonization_worker_pulse_pause_execution.py:211-228`

**Adversarialer Ablauf:**

1. Ein Hardwarepfad ignoriert `should_continue()` und blockiert dauerhaft.
2. `wait()` läuft nach Pulsdauer plus 0,1 Sekunden ab.
3. `future.cancel()` kann einen bereits laufenden Thread nicht abbrechen.
4. `executor.shutdown(wait=False)` kehrt zurück und `HardwareModulationOverrunError` wird gemeldet.
5. Der Thread läuft weiter; beim Prozessende wartet Python auf die nicht-daemonisierten Executor-Threads.

**Auswirkung:** Der API-/Workerpfad scheint begrenzt fehlzuschlagen, der Workerprozess und seine Ressourcen können aber unbegrenzt weiterleben. Stop und Owner-Single-Flight bleiben dadurch blockiert.

**Minimale Korrektur:** Nicht vertrauenswürdige Hardwarepfade in killbaren Unterprozessen isolieren und nach der Grace-Periode terminieren oder ausschließlich kooperative Implementierungen zulassen und deren tatsächliche Beendigung vor Rückkehr bestätigen.

Der Test misst nur die Rückkehrzeit des aufrufenden Threads. Er beweist nicht, dass Future, Thread oder Workerprozess beendet wurden.

---

### F-04 — P1: Owner-/Tenant-Single-Flight kann nach Workercrash dauerhaft sperren und ist PID-Reuse-anfällig

**Datei:** `services/harmonization_worker.py:128-130,718-725,800-828`  
**Composition Root:** `apps/web/main.py:305-307`

**Adversarialer Ablauf:**

1. Ein Owner startet einen Job; der Snapshot bleibt `pending` oder `running`.
2. Der Worker stirbt abrupt.
3. `recover_interrupted_harmonization_jobs()` wird beim App-/Service-Start und vor der nächsten Reservierung nicht aufgerufen.
4. `get_active_jobs()` betrachtet den Snapshot weiterhin als aktiv.
5. Jeder weitere Start desselben Owner-/Tenant-Paars wird dauerhaft abgewiesen.
6. Selbst bei manuellem Recovery wird nur `os.kill(pid, 0)` geprüft. Wird die PID wiederverwendet, gilt der fremde Prozess als lebender Worker.

**Auswirkung:** Dauerhafter 409-Lockout eines Operators/Tenants; PID-Reuse kann die Sperre unbegrenzt konservieren.

**Minimale Korrektur:** Worker-PID zusammen mit Creation-Time/Nonce persistieren, Recovery beim Composition-Root-Start und atomar unmittelbar vor der Single-Flight-Reservierung ausführen und verwaiste Jobs unter derselben Registry-/Job-Lockgrenze auf `interrupted` setzen.

---

### F-05 — P2: Stop kann mit einem falschen `error`-Event enden

**Datei:** `services/harmonization_worker.py:677-683`  
**Vergleich:** `services/harmonization_worker.py:147-155`

**Adversarialer Ablauf:**

1. Hardwaremodulation wirft eine Ausnahme.
2. Parallel veröffentlicht die API den Stopmarker und persistiert `stopped`.
3. Der Exception-Pfad setzt sein älteres Jobobjekt auf `error`.
4. `_save_locked()` erkennt den Stopmarker und persistiert tatsächlich `stopped`.
5. Danach wird trotzdem bedingungslos das Event `error` emittiert.

**Auswirkung:** Persistente Autorität und Event-/Auditspur widersprechen sich; UI und Nachvollziehbarkeit können einen Fehler für einen gestoppten Job melden.

**Minimale Korrektur:** Auch Fehlerentscheidung, finale Speicherung und Fehlerereignis unter einer gemeinsamen Stop-aware Lock-/CAS-Grenze durchführen. `error` nur emittieren, wenn der bestätigte gespeicherte Terminalstatus tatsächlich `error` ist.

---

### F-06 — P2: Pollfehler bleiben unsichtbar und werden unbegrenzt wiederholt

**Datei:** `apps/web/static/app.js:429-432,668-674`

**Adversarialer Ablauf:**

1. Ein Scan- oder Harmonisierungsjob läuft.
2. Auth-Session, Server oder Netzwerkzugriff fällt dauerhaft aus.
3. Der Catch-Zweig aktualisiert weder Status noch `aria-live`-Fehleranzeige.
4. Alle fünf Sekunden wird unbegrenzt weitergepollt.
5. Die UI zeigt weiterhin den letzten erfolgreichen Laufzustand.

**Auswirkung:** Operatoren sehen einen veralteten, scheinbar aktuellen Prozesszustand und erhalten keinen sichtbaren Offline-/Auth-/Abbruchhinweis. Das war bereits Bestandteil des v5-F-08-Vertrags.

**Minimale Korrektur:** Pollfehler sichtbar und barrierefrei als degradierter/offline Zustand veröffentlichen, Authfehler terminal behandeln und Retries mit begrenztem Backoff beziehungsweise expliziter Wiederaufnahme versehen.

---

### F-07 — P2: Atomare Store-Replaces sind nicht vollständig crash-durable

**Dateien:**  
`apps/web/workbench_runtime.py:85-106`  
`apps/web/scan_jobs.py:416-423`

**Adversarialer Ablauf:**

1. Temporärdatei wird geschrieben und ersetzt die Autoritätsdatei.
2. Unmittelbar nach `os.replace()`/`Path.replace()` tritt Stromverlust oder Systemcrash ein.
3. Beim Workbench-Store wurde nur der Dateiinhalt, nicht die Verzeichnis-Metadatenänderung geflusht.
4. Beim Scan-State fehlt bereits der explizite Flush/Fsync der Temporärdatei.
5. Nach Restart kann der letzte Stand fehlen oder veraltet sein.

**Auswirkung:** Verlust von Draft-/Templatezustand beziehungsweise Scan-Cursor, Owner-/PID- oder Terminalzustand; im Scanfall kann dies die Restart-Kontrollautorität schwächen.

**Minimale Korrektur:** Scan-Temporärdateien explizit flushen/fsyncen; nach jedem Replace die Verzeichnis-/Metadatenänderung dauerhaft flushen, soweit die Plattform dies unterstützt, oder eine dokumentierte Windows-Durable-Replace-Primitive verwenden.

---

### F-08 — P2: Die adversariale Testevidenz schließt zentrale v6-Domänen nicht

**Dateien:**  
`tests/test_harmonization_worker_pulse_pause_execution.py:211-228`  
`tests/test_web_scan_jobs.py:310-340,424-447`  
`tests/test_harmonization_worker_pulse_pause.py:62-83`  
`tests/test_web_shell.py:301-321`

Fehlende behavioristische Nachweise:

- Nichtkooperativer Hardwarefuture: Test prüft die schnelle Exception, aber nicht, ob Thread und Workerprozess konvergieren.
- Prozessbaum nach Leader-Ende: Restart-Test hält den Elternprozess bis zum Stop am Leben.
- Crash zwischen `Popen()` und dauerhafter Scanregistrierung wird nicht injiziert.
- Cross-Instance-Scanpolling wird mit Threads in einem Prozess geprüft, nicht mit unabhängigen App-Prozessen.
- Harmonization-Recovery vor Owner-/Tenant-Reservierung und PID-Reuse werden nicht geprüft.
- Reportkatalogtest beweist nur, dass dieselbe Instanz und eine positive TTL existieren; keine parallele Single-Flight-Traversierung, Cachefehler-Freigabe oder TTL-Invalidierung wird behavioristisch geprüft.
- Stop-vs-Exception-Terminalpublikation wird nicht getestet.

**Auswirkung:** Die Freeze-v6-Aussagen zu bounded convergence, restartfester Prozessautorität, Owner-Single-Flight und Katalog-Single-Flight können grün bleiben, obwohl die obigen Defekte bestehen.

**Minimale Korrektur:** Deterministische Tests in den realen Domains ergänzen: unabhängige Prozesse, realer Leader-exit/lebender Child, blockierter Start-Registrierungs-Handshake, PID-Reuse, nach Testende bestätigte Future-/Prozessbeendigung und instrumentierte parallele Katalogtraversierung.

## 3. Counts

| Severity | Anzahl |
|---|---:|
| P0 | 0 |
| P1 | 4 |
| P2 | 4 |
| P3 | 0 |
| **Gesamt** | **8** |

## 4. Evidenzqualität

- Alle **58/58 Scope-Dateien** wurden vollständig gelesen und gegen den v6-Plan sowie beide vollständigen v5-Reviews abgeglichen.
- Produktionscode, Tests und Evidenz wurden getrennt bewertet; Testnamen und Freeze-Header wurden nicht als Ersatz für Verhaltensprüfung akzeptiert.
- Wegen des ausdrücklichen Verbots wurden keine Tests, Imports, Server, Netzwerkzugriffe oder Installationen ausgeführt. Die im Manifest genannten Laufresultate wurden daher nur als historische Claims behandelt.
- Keine Repositorydatei wurde erstellt, geändert oder gelöscht.
- Methodische Abweichung: Bei der ersten Scopeprüfung wurden zwei kurzlebige Betriebssystem-Temporärdateien außerhalb des Repositories durch `mktemp` erzeugt und per Trap wieder entfernt. Sie beeinflussten weder Worktree noch Freeze-Hashes. Die Endprüfung verwendete ausschließlich Process Substitution ohne solche Dateien.

## 5. End-Evidenz

| Prüfung | Ergebnis |
|---|---|
| Branch | `operator-workbench-phase1` |
| HEAD | `3271ff9366ab3fecb2a158913a0cc19ed6a06726` |
| Manifest-SHA-256 | `279a2d365636a9989eb1a9e6cfae74d7eaa9f248ec3e3c8b3c1cb2bae3147e39` |
| Manifest-Einträge | 58 |
| Einzelhashes | **58/58 OK** |
| Pfadsortiertes LF-Aggregat | `d1758106368f9449f4e2b93873f3a1bbedfdd07229dda70a4dd735caf9027b45` |
| Dirty-Population ohne Manifest | 58 |
| Scope-Differenz | leer |
| Population einschließlich Manifest | 59 |
| Statuspopulation | 59 |

Die Git-Ausgaben enthielten ausschließlich bekannte LF/CRLF-Hinweise.

## 6. Drift

**Keine Drift.** Branch, HEAD, Manifesthash, 58 Einzelhashes, Aggregat, Scopemenge und 59er Population waren an Start und Ende identisch.

## 7. Schlussurteil

# **REQUEST CHANGES / NO-GO**

Freeze v6 ist hash-, scope- und driftkonsistent, erfüllt aber wegen **P1=4 und P2=4** den vorgeschriebenen Nullbefundvertrag nicht. Besonders blockierend sind:

1. das Scan-Registrierungs-Crashfenster,
2. verlorene Prozessnachfahren nach Ende des Leaders,
3. nicht tatsächlich konvergierende Hardwarefutures,
4. dauerhaft blockierbare und PID-Reuse-anfällige Owner-/Tenant-Single-Flight-Autorität.

**Dateien erstellt oder geändert:** keine Repositorydateien.