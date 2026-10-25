## Code Review

**Verdikt: REQUEST CHANGES**  
**Konfidenz: HOCH**  
**Befunde:** `P0=0, P1=1, P2=1, P3=0`  
**Scope-Drift:** `0`

### Befunde

| Priorität | Befund | Ort |
|---|---|---|
| P1 | Ein Supervisor-Exit bzw. `OSError` **nach erfolgreichem `pidfd_open()`**, aber während der anschließenden Identitäts-/PGID-Revalidierung, wird nicht behandelt. Ein roher `ProcessLookupError`/`OSError` beendet die Signalisierungsrunde, statt den verschwundenen Supervisor zu ignorieren und tokengebundene Nachfahren zu enumerieren. | `apps/web/scan_jobs.py:528-539`, `apps/web/scan_jobs.py:946-951` |
| P2 | Die Tests behaupten Primärfehler-/Traceback-Erhaltung, prüfen aber nur Objektidentität und Gruppenreihenfolge. Der tatsächliche Traceback wird nicht untersucht. Auch die post-open Supervisor-ESRCH/OSError-Sequenz ist nicht abgedeckt. | `tests/test_web_scan_jobs.py:642-690` |

### P1 – Supervisor-Race nach Handle-Erwerb

Nach erfolgreichem `_open_pidfd()` läuft folgende ungeschützte Revalidierung:

```python
if (
    supervisor_descriptor is not None
    and _process_identity_matches(job.process.pid, job.process_create_time)
    and os.getpgid(job.process.pid) == job.process_group_id
):
```

Der Supervisor kann zwischen `_process_identity_matches()` und `os.getpgid()` verschwinden. Dann kann `os.getpgid()` `ProcessLookupError` beziehungsweise `OSError(errno.ESRCH)` auslösen. Der `finally`-Block schließt zwar das Handle, aber:

- `_token_process_pidfds()` wird nicht mehr aufgerufen;
- legitime Nachfahren werden in dieser Runde nicht signalisiert;
- `_converge_posix_authority()` bricht mit dem rohen Fehler ab;
- `stop()` übersetzt nur `ProcessAuthorityAmbiguousError`, sodass kein definierter/persistierter öffentlicher Lifecycle-Zustand entsteht.

Dasselbe gilt für sonstige `OSError` aus der post-open Revalidierung: Sie umgehen den Ambiguitätsvertrag.

**Erforderliche Korrektur:** Die Supervisor-Revalidierung nach `pidfd_open()` separat kapseln:

- `ProcessLookupError` und `OSError(ESRCH)` als normalen Supervisor-Exit behandeln und anschließend die Gruppenmitglieder enumerieren;
- andere `OSError` in `ProcessAuthorityAmbiguousError` übersetzen;
- vor jeder Ausnahme das erworbene Supervisor-Handle weiterhin exakt einmal schließen.

Dazu adversariale Tests für Exit/`ESRCH` und Nicht-`ESRCH` **nach** erfolgreichem Open und erfolgreicher Creation-Time-Prüfung ergänzen. Sie müssen Signale, Handle-Schließung, Nachfahren-Enumeration sowie den öffentlichen/persistierten Status konkret behaupten.

### Weitere Prüfung

Statisch nachvollzogen und ohne zusätzlichen Befund:

- `BaseExceptionGroup` erhält Primär-, Rollback- und Persistenzfehler in stabiler Reihenfolge.
- Rollback-Fehlschlag setzt vor dem Persistenzversuch `rollback_failed`.
- Persistenz wird auch nach Rollback-Fehler versucht.
- Aktuelle, übertragene und Supervisor-pidfds werden auf den untersuchten `BaseException`-Pfaden vollständig abgearbeitet.
- Fremdgruppen/Token-Mismatch und unlesbare Provenienz verhindern Signalisierung.
- TERM/KILL-Runden enumerieren erneut und unterstützen wiederholte Konvergenz.
- `RuntimeError` beim Supervisor-Open sowie Open-Fehler `EACCES`, `EPERM`, `EMFILE` werden fail-closed behandelt.
- PID-/PGID-Wiederverwendung verleiht ohne passende Token-Provenienz keine Signalautorität.

### Freeze-v14-Bindung

Start- und reservierte Endbindung stimmen überein:

- Branch: `operator-workbench-phase1`
- HEAD: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- Manifest-SHA-256: `ff06cb2902f5a43cefee09afc3bda9971d5a558efc1576b6f508269b85513f68`
- Einzelhashes: **93/93 OK**
- Aggregat: `3e7dd5ca5c85ba1cc87a26d79f909125da7448f2e284a8590af13c0bca1bb601`
- Exakte Population: **94**
- Scope minus Dirty: `0`
- Dirty minus Scope plus Manifest: `0`
- End-Status-SHA-256 (`git status --porcelain=v1 -z`): `55253e45f5dc83c1b1b06f06e87f1e4846041a76ea59efc183c215e0bce7410e`
- Drift: **0**

**Dateien erstellt oder verändert:** keine.  
**Tests/Produktcode ausgeführt:** nein, gemäß strikt read-only/no-execution Reviewvertrag.