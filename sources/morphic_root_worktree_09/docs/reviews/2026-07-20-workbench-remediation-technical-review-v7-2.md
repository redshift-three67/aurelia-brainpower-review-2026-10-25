# REQUEST CHANGES

**Konfidenz:** HOCH  
**Befundzählung:** `P0=0, P1=2, P2=2, P3=0`

## Freeze- und Driftprüfung

| Prüfung | Start | Ende |
|---|---|---|
| Branch | `operator-workbench-phase1` | identisch |
| HEAD | `3271ff9366ab3fecb2a158913a0cc19ed6a06726` | identisch |
| Freeze-SHA-256 | `53b8d15a2a0ff79428af39b60757246d3d0e27f9c81f131eafd76bcdc6529693` | identisch |
| Manifestdateien | 66 | 66 |
| Einzelhashes | 66/66 OK | 66/66 OK |
| LF-Aggregat | `bcbd3c90f7a6df0ed99eb23791b6c728b2584aa05386abafeddd0c47ea8fda62` | identisch |
| Dirty-Population | 67 Pfade | 67 Pfade |
| Dirty minus Scope+Freeze | 0 | 0 |
| Scope+Freeze minus Dirty | 0 | 0 |
| Drift | keine | keine |

Alle **66/66 Manifestdateien** wurden read-only geprüft. Freeze v6, der vollständige v6-REQUEST-CHANGES-Bericht und der v7-Closure-Plan wurden einbezogen.

## Findings

### P1 — POSIX-Supervisor verliert den Prozessgruppenbaum nach Ende des produktiven Leaders

**Evidenz:**

- `services/scan_process_gate.py:113-117` bestimmt verbleibende Arbeit über `process.children(recursive=True)`.
- `services/scan_process_gate.py:127-141` beendet den Supervisor, sobald der produktive Leader beendet ist und keine aktuellen Parent/Child-Nachfahren mehr gemeldet werden.
- Nach dem Exit des Leaders werden dessen Kinder unter POSIX üblicherweise reparented. Sie bleiben zwar in der Prozessgruppe, sind aber keine Nachfahren des Supervisors mehr. Der Supervisor kann daher enden, obwohl das produktive Gruppenmitglied weiterläuft.
- `apps/web/scan_jobs.py:443-446` stuft den recovered Job anschließend über die beendete Supervisor-PID als `failed` ein.
- `apps/web/scan_jobs.py:589-635` führt den Gruppen-Kill nur aus, solange `job.process.poll() is None` ist.
- Der Leader-exit-Test `tests/test_web_scan_jobs.py:540-575` wurde auf dem Windows-Host ausgelegt; sogar sein Cleanup verwendet ausschließlich `taskkill`. Er beweist die POSIX-Prozessgruppenautorität nicht.

**Auswirkung:** Auf POSIX kann genau der v6-F-02-Fall weiterbestehen: Leader und Supervisor sind beendet, ein produktiver Nachfahre bleibt aktiv, während Status und Stop keine Kontrolle mehr besitzen.

**Erforderlich:** Der Supervisor muss POSIX-Gruppenlebendigkeit über die gespeicherte PGID prüfen, nicht über Parent/Child-Abstammung. Recovery und Stop müssen die PGID auch bei beendetem Supervisor-Leader PID-reuse-sicher kontrollieren. Ein echter POSIX-Test muss Leader-Exit, lebendes Gruppenmitglied, Restart, Stop und bestätigte Kindprozess-Abwesenheit prüfen.

---

### P1 — Partieller Hardware-Spawnfehler lässt bereits gestartete Kinder ohne Cleanup zurück

**Evidenz:**

- `services/hardware_modulation.py:297-300`: gestartete Hardwarekinder melden `started` und warten anschließend unbegrenzt auf `pulse_event`.
- `services/hardware_modulation.py:316-325`: alle Prozesse werden in einer ungeschützten Schleife gestartet.
- Wirft `process.start()` für ein späteres Hardware-Backend, verlässt die Funktion unmittelbar den Startloop. Es existiert dort kein `try/finally`, das bereits gestartete Prozesse freigibt, terminiert, killt und joint.
- Die Cleanup-Logik beginnt erst ab `services/hardware_modulation.py:327`.
- `tests/test_harmonization_worker_pulse_pause_execution.py:197-266` deckt erfolgreiche Mehrfachstarts und Overrun **nach** erfolgreichem Spawn ab, nicht den Fehler beim zweiten oder dritten `Process.start()`.

**Auswirkung:** Beispielsweise kann CPU bereits gestartet sein und auf `pulse_event` warten, während GPU-Spawn wegen Ressourcen- oder OS-Fehler scheitert. Der API-/Workerpfad propagiert die Exception, aber das CPU-Kind bleibt aktiv; wegen `daemon=False` kann es zusätzlich die Workerbeendigung blockieren.

**Erforderlich:** Prozessaufbau und sämtliche nachfolgenden Kontrollpfade in eine gemeinsame `try/finally`-Convergence-Grenze legen. Jedes gestartete Kind muss bei jedem Fehlerpfad `stop → pulse release → terminate → bounded join → kill → final join` durchlaufen. Adversarialer Test: zweiter Spawn wirft, erster Prozess wartet bereits, Rückkehr erst nach bestätigter PID-Abwesenheit.

---

### P2 — Harmonisierungsautoritäten verwenden weiterhin keinen crash-durablen Replace

**Evidenz:**

- `services/harmonization_worker.py:77-88` flusht zwar die temporäre Datei, verwendet danach aber nur `os.replace()`.
- Ein POSIX-Parent-Directory-Fsync beziehungsweise Windows-Write-through-Replace fehlt.
- Diese Primitive publiziert die restartkritischen Jobsnapshots in `services/harmonization_worker.py:155-163`.
- Auch der Stopmarker verwendet sie in `services/harmonization_worker.py:809-819`.
- Im Gegensatz dazu besitzt `apps/web/durable_io.py:9-68` die neue durable Plattformgrenze und wird von Scan- und Workbench-Stores verwendet.
- `tests/test_web_durable_io.py:38-68` prüft nur Workbench- und Scanregistrierung; Harmonisierungsjob und Stopmarker sind nicht enthalten.

**Auswirkung:** Nach Stromverlust/Systemcrash können Owner-/Tenant-Reservierung, Workeridentität oder Stopautorität trotz vorheriger API-Bestätigung fehlen. Das schwächt Startup-/Pre-Reservation-Recovery und kann einen Worker weiterlaufen lassen oder einen falschen aktiven/terminalen Zustand rekonstruieren.

**Erforderlich:** Jobsnapshot und Stopmarker auf dieselbe durable Plattformprimitive migrieren und Fault-Boundaries für Temp-Flush, Replace und Metadaten-Flush abdecken.

---

### P2 — Erfolgreiches Polling räumt den sichtbaren Degradierungszustand nicht auf; Scan besitzt keinen expliziten Wiederaufnahmeweg

**Evidenz:**

- Scanfehler veröffentlichen den degradierten Zustand in `apps/web/static/app.js:434-453`.
- Ein später erfolgreicher Scanpoll aktualisiert Jobfelder in `apps/web/static/app.js:387-433`, setzt den zuvor über `showInlineState(..., "bad")` veröffentlichten Offlinezustand aber nicht zurück.
- Dasselbe gilt für Harmonisierung: Fehlerpfad `apps/web/static/app.js:690-712`, Erfolgspfad `apps/web/static/app.js:659-689`.
- Nach Scan-Authfehler wird bei `apps/web/static/app.js:437-440` permanent pausiert. Anders als für Harmonisierung existiert im Scanpanel kein expliziter Refresh-/Retry-Button; vgl. `apps/web/static/index.html:460-480` gegenüber `apps/web/static/index.html:604-607`.
- Der Browsertest `tests/browser/workbench.spec.js:510-557` prüft ausschließlich Fehler, Backoff und Pause. Er prüft weder erfolgreiche Recovery noch einen Scan-Reauth-/Retry-Ablauf.

**Auswirkung:** Nach einem transienten Fehler kann der aktuelle Jobstatus wieder korrekt sein, während die zentrale `aria-live`-Anzeige weiterhin „offline/nicht erreichbar“ meldet. Nach Authverlust kann ein Scan trotz erneuter Anmeldung ohne unterstützten Wiederaufnahmeweg unüberwacht bleiben.

**Erforderlich:** Erfolgreiche Polls müssen den zum selben Job gehörenden Degradierungszustand explizit löschen. Für pausierte Scanpolls ist ein generation-/jobgebundener Retry nach Reauth oder ein sichtbarer manueller Refresh erforderlich. Beide Übergänge behavioristisch testen.

## Mapping der acht v6-Befunde

| v6-Befund | v7-Status |
|---|---|
| F-01 Scan vor dauerhafter Registrierung | geschlossen: Supervisor-Gate wartet vor produktivem Start auf durable Registrierung und Release |
| F-02 Leader beendet, Nachfahre lebt | **nur Windows geschlossen; POSIX weiterhin offen**, siehe P1 |
| F-03 Hardwarefuture konvergiert nicht | Haupt-Overrunpfad auf Prozesse migriert; **partieller Spawnfehler bleibt offen**, siehe P1 |
| F-04 Owner/Tenant-Lockout und PID-Reuse | geschlossen: Creation-Time, Startup-Recovery und Recovery unter Registry-Lock vor Reservation vorhanden |
| F-05 Stop versus Error-Event | geschlossen: stop-aware `_commit_error_job()` mit gemeinsamer Lock-/Persistenz-/Evententscheidung |
| F-06 unsichtbare Endlospollfehler | Backoff/Pause implementiert; **Recovery-/Retry-Vertrag nur teilweise geschlossen**, siehe P2 |
| F-07 nicht crash-durable Stores | Scan und Workbench geschlossen; **Harmonisierungsjob und Stopmarker bleiben nicht durable**, siehe P2 |
| F-08 adversariale Evidenzlücken | mehrere Domänen geschlossen; POSIX-Leader-exit, partieller Hardware-Spawn, Harmonization-Durability und Poll-Recovery bleiben unbewiesen |

## Weitere geprüfte Schwerpunkte

Ohne zusätzliche Befunde geprüft:

- Scan-Pre-Registration und Release-Gate;
- PID/Create-Time-Validierung;
- Windows-Job-Object- und Taskkill-Pfad;
- Cross-Process-Locks und atomare Workbench-/Scan-Stores;
- Stop-vs-Cycle-, Stop-vs-Completion- und Stop-vs-Error-Commit;
- Harmonization Startup- und Pre-Reservation-Recovery;
- Owner-/Tenant-Single-Flight;
- Reportkatalog-Tenantbindung, Cachelock, Fehlerfreigabe und TTL-Test;
- Report- und Job-Ownership/Auth;
- exakte Scan-Artefaktbindung;
- Prozess-/Fehler-/Interrupted-Darstellung;
- Reset-, Preview-, Single-Flight-, ARIA- und Prozessgruppentestverträge;
- übrige P0–P3-Klassen im gesamten Manifestscope.

## Abschluss

Freeze v7 ist **hash-, scope- und driftkonsistent**, erfüllt den vorgeschriebenen Nullbefundvertrag aber wegen `P1=2` und `P2=2` nicht.

- Tests, Server, Imports, Netzwerkzugriffe und Installationen: **nicht ausgeführt**
- Dateien erstellt, geändert oder gelöscht: **keine**
- Repository-/Temp-Schreibvorgänge: **keine**
- Beobachtete Besonderheiten: ausschließlich harmlose LF/CRLF-Hinweise bei der initialen Git-Scopeabfrage