# REQUEST CHANGES

**Konfidenz:** HOCH  
**Befundzählung:** `P0=0, P1=2, P2=0, P3=0`  
**Scope-Drift:** `0`

## Befunde

| Priorität | Befund | Ort |
|---|---|---|
| P1 | Ein bestätigtes `ProcessLookupError`/`ESRCH` beim Erwerb des Supervisor-pidfd wird nicht als Exit-Race übersprungen. `_signal_posix_authority()` bricht ab, bevor die weiterhin gültigen tokengebundenen Gruppenmitglieder erfasst und signalisiert werden. Stop und Post-Release-Rollback können dadurch trotz vorhandener Prozessautorität nicht konvergieren. | `apps/web/scan_jobs.py:497-515`; Testlücke `tests/test_web_scan_jobs.py:497-519` |
| P1 | Die behauptete Schließung aller aktuellen und akkumulierten Deskriptoren auf **jedem** Ausnahmeweg ist nicht gewährleistet. Der äußere Cleanup erfasst nur `Exception`, nicht `BaseException`; außerdem beendet ein Fehler eines einzelnen `os.close()` die Cleanup-Schleife und lässt spätere akkumulierte Handles offen. | `apps/web/scan_jobs.py:482-489`, zusätzlich konsumierender Cleanup `apps/web/scan_jobs.py:532-536` |

## Details

### P1 – Supervisor-pidfd-Exit-Race blockiert die gesamte Signalrunde

Für Gruppenmitglieder behandelt `_token_process_pidfds()` `ProcessLookupError` und `errno.ESRCH` korrekt als verschwunden. Der separat erworbene Supervisor-Handle besitzt diesen Vertrag jedoch nicht:

```python
if job.process.poll() is None:
    supervisor_descriptor = _open_pidfd(job.process.pid)
```

Endet der Supervisor zwischen `poll()` und `_open_pidfd()`, propagiert der bestätigte Exit-Race unmittelbar. `_token_process_pidfds()` wird nicht mehr aufgerufen. Ein noch lebender, tokenvalider Nachkomme bleibt deshalb unbehandelt. Das betrifft sowohl `_converge_posix_authority()` im produktiven Stop als auch `_rollback_scan_authority()`.

Der vorhandene Akquisitionsvertrag testet ausschließlich `_token_process_pidfds()`, nicht diesen Supervisor-Pfad.

**Erforderlich:** `ProcessLookupError` bzw. `OSError(errno.ESRCH)` beim Supervisor-pidfd überspringen und anschließend die vollständige Ziel-PGID enumerieren. Alle anderen Akquisitionsfehler müssen weiterhin vor dem ersten Signal abbrechen. Adversarialer Test: Supervisor verschwindet genau beim pidfd-Open, tokenvalider Nachkomme bleibt und wird kontrolliert konvergiert.

### P1 – Deskriptor-Cleanup ist nicht ausnahmetotal

Der normale Fehlerpfad schließt aktuellen und zuvor akkumulierten Deskriptor jeweils einmal. Die stärkere Freeze-v12-Zusage „auf jedem Ausnahmeweg“ ist jedoch nicht erfüllt:

- `except Exception` erfasst beispielsweise `KeyboardInterrupt`/`SystemExit` nicht.
- Wirft `os.close()` für einen akkumulierten Handle, stoppt die Schleife; spätere Handles werden nicht geschlossen.
- Dasselbe nicht isolierte Schleifenmuster besteht beim konsumierenden Cleanup in `_signal_posix_authority()`.

**Erforderlich:** Cleanup über alle übertragenen Handles ausnahmesicher ausführen, Close-Fehler pro Handle isolieren/aggregieren und die ursprüngliche Ausnahme anschließend weiterreichen. Tests müssen einen Fehler beim ersten von mehreren Close-Vorgängen injizieren und exakt einen Close-Versuch für jeden aktuellen und akkumulierten Deskriptor nachweisen.

## Weitere Audit-Ergebnisse

- Vollständige Ziel-PGID-Entscheidung scannt jetzt ohne frühen positiven Return; gültig→AccessDenied/fehlend/abweichend und die umgekehrte Reihenfolge sind im Code fail-closed.
- Fehlende bzw. abweichende Provenienz wird als `authority_ambiguous` behandelt, nicht als Abwesenheit.
- Supervisor-Ausschluss verlangt pidfd-Erwerb plus Create-Time-Identität; ein Create-Time-Mismatch wird nicht als vertrauenswürdiger Supervisor übersprungen.
- Nicht-`ESRCH`-Akquisitionsfehler in `_token_process_pidfds()` brechen vor dem Signalisieren ab.
- Ambiguität wird in Recovery/Snapshot publiziert; Stop und Rollback verweigern Signale. Ein späterer Stop unter Service-/Job-Lock überführt bestätigte Abwesenheit in persistiertes `stopped`.
- Frühere v9–v11-Befunde sowie Auth/Authz, Sessions/Secrets, Ownership/Tenant/Report-Bindung, Rate-Limit-Buckets, Durable Stores, New Case, Windows, Hardware-Konvergenz, Poll-Single-Flight und Accessibility wurden erneut statisch verfolgt; keine weiteren P0–P3-Befunde.

## Freeze-v12-Bindung

Start- und reservierte Endbindung stimmen überein:

- Branch: `operator-workbench-phase1`
- HEAD: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- Manifest-SHA-256: `1d4931a9e14387ce891b8a27d39235889c671cc66b9375f2e78a78d7eb74d2fc`
- Einträge: `85`
- Einzelhashes: `85/85 OK`
- Aggregat: `a51bbec277472ba434a645edd8d2862478938eed0f7529ce7d68628fc3d988ae`
- Population: `86/86`
- Dirty minus Scope: leer
- Scope minus Dirty: leer
- End-Status-Fingerprint (`git status --porcelain=v1 -z`): `18600cbab0614dc2a7de166ef58f8814f6e7548f06c068e78446f99a4144c44f`
- Drift: **keine**

**Dateien erstellt oder verändert:** keine.  
**Tests/Imports/Server/Netzwerk/Installationen:** nicht ausgeführt.  
**Problem:** Ein erster Population-Abgleich wurde wegen der Verwendung temporärer Dateien vom Read-only-Guard blockiert; die reservierte Endprüfung wurde anschließend vollständig speicherintern und erfolgreich ausgeführt.