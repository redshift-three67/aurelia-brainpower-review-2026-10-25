# REQUEST CHANGES

**Konfidenz:** HOCH  
**Befundzählung:** `P0=0, P1=3, P2=1, P3=0`

## Freeze-/Scope-Bindung

| Prüfung | Start | Ende |
|---|---:|---:|
| Branch | `operator-workbench-phase1` | identisch |
| HEAD | `3271ff9366ab3fecb2a158913a0cc19ed6a06726` | identisch |
| Freeze-SHA-256 | `ddca521250a8b3f558a71ccc42617499e04a2ed770b8b6aaa3b6887c00c9a3ef` | identisch |
| Einzelhashes | `69/69 OK` | `69/69 OK` |
| LF-Aggregat | `a0554a01566728c34a3a00810bd25576b7eaf22c876ae1c3607d12ebb3536530` | identisch |
| Dirty-Population | 70 | 70 |
| Dirty minus Scope+Freeze | 0 | 0 |
| Scope+Freeze minus Dirty | 0 | 0 |
| Drift | keine | keine |

Geprüft wurden die zehn byteveränderten v7→v8-Dateien, die drei neuen Review-/Planartefakte, ihre produktiven Prozess-/Store-/Frontend-Grenzen und Tests. Für die 56 byteidentischen v7-Dateien wurde der vollständige v7-Bericht berücksichtigt.

## Findings

| Priorität | Befund | Ort |
|---|---|---|
| P1 | Recovery und Stop akzeptieren nach Supervisor-Ende jede aktuell lebende Gruppe mit der gespeicherten PGID. Die persistierte Supervisor-Creation-Time wird in diesem Pfad nicht mehr als Provenienz verwendet. Eine alte Jobdatei kann nach PGID-Wiederverwendung daher einen fremden Lauf als `running` einstufen und `killpg()` gegen ihn ausführen. | `apps/web/scan_jobs.py:445-466`, `apps/web/scan_jobs.py:606-645` |
| P1 | Nach Freigabe des Start-Gates kann der abschließende `_snapshot()`/durable Write fehlschlagen. Der Exception-Pfad beendet dann nur den Supervisor-Prozess; auf POSIX können bereits gestartete produktive Gruppenmitglieder weiterlaufen. | `apps/web/scan_jobs.py:577-598`, insbesondere `581-592`; Persistenzgrenze `apps/web/scan_jobs.py:749-750` |
| P1 | Die Hardware-Convergence endet nach `kill()` und einem begrenzten Join ohne abschließende `is_alive()`-Prüfung oder Fehlereskalation. Bei unwirksamem/verzögertem Kill kann der Aufrufer zurückkehren, obwohl das Kind noch lebt; damit ist die geforderte bestätigte PID-Abwesenheit nicht garantiert. | `services/hardware_modulation.py:305-318`, aufgerufen aus `services/hardware_modulation.py:401-402` |
| P2 | Der neue manuelle Scan-Retry ist nicht single-flight. Mehrfachklicks starten parallele Fetches; jeder erfolgreiche Fetch kann einen eigenen Timer planen, während nur der zuletzt gespeicherte Handle löschbar ist. Das kann Pollschleifen vervielfachen, das Poll-Rate-Limit belasten und terminale Trace-Synchronisierung mehrfach anstoßen. | `apps/web/static/app.js:397-485`, `apps/web/static/app.js:1206-1210` |

### Erforderliche Korrekturen

1. **POSIX-Provenienz:** Eine restartfeste, nicht nur numerische Gruppenidentität speichern und vor Status/Stop fail-closed validieren. Ein Test muss explizit eine alte Jobdatei plus wiederverwendete/fremde PGID modellieren und beweisen, dass weder `running` gemeldet noch `killpg()` ausgeführt wird.
2. **Start-Rollback:** Ab dem Gate-Release bei jedem Fehler den gesamten Windows-Job beziehungsweise die POSIX-Prozessgruppe terminieren und deren Abwesenheit bestätigen, nicht nur den Supervisor.
3. **Hardware-Convergence:** Nach finalem Join alle Prozesse erneut prüfen; verbleibende Prozesse müssen eine explizite Convergence-Exception auslösen. Cleanup-Exceptions dürfen außerdem nicht die Bereinigung weiterer Kinder verhindern.
4. **Polling:** Pro Domain/Job/Generation einen In-flight-Guard oder AbortController verwenden; Retry während eines laufenden Polls deaktivieren/zusammenführen und nur eine nächste Timerautorität zulassen.

## Mapping der vier v7-Befunde

| v7-Befund | v8-Entscheidung |
|---|---|
| P1 POSIX-Supervisor verliert Gruppenbaum | **Nicht vollständig geschlossen:** Gruppenlebendigkeit nach Leader-Exit ist verbessert, aber restartfeste PGID-Provenienz/PID-Reuse-Sicherheit fehlt; zusätzlich ist der Post-Release-Fehlerpfad nicht gruppenkonvergent. |
| P1 partieller Hardware-Spawnfehler | **Nicht vollständig geschlossen:** Der `finally`-Pfad erfasst gestartete Kinder, bestätigt nach finalem Kill aber nicht zwingend deren Abwesenheit. |
| P2 Harmonisierungsautoritäten nicht crash-durable | **Geschlossen:** Job-Snapshots und Stopmarker delegieren an `durable_write_bytes`; die beiden Autoritäten und Failure-Preservation sind abgedeckt. |
| P2 Poll-Degradierung/Scan-Reauth-Retry | **Funktional im Einzelablauf geschlossen:** owner-/job-/generationgebundenes Clear und sichtbarer Retry sind vorhanden. Der neue Retry erzeugt jedoch den separaten P2-Reentrancy-/Rate-Limit-Befund. |

## Übrige geprüfte Klassen

Ohne weitere Befunde: Authentifizierung, Autorisierung und Session-Cookie-Nutzung; Secrets/API-Key-Behandlung; Owner-/Tenant-Bindung von Jobs und Reports; Reportpfade und Rate-Limit-Bucket-Zuordnung; New-Case-Generation und stale Job-/Generation-Guards; ARIA-Live-/Progressbar-Verträge; Harmonization-Durability und Stopmarker-Locking. Die byteidentischen v7-P0/P3- und übrigen P1/P2-Klassen bleiben ohne zusätzlichen Befund.

- Tests, Imports, Server, Netzwerk und Installationen: **nicht ausgeführt**.
- Dateien erstellt, verändert oder gelöscht: **keine**.
- Abschlussbindung: **null Drift**, aber Nullbefundvertrag wegen `P1=3, P2=1` nicht erfüllt.