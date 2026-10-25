# REQUEST CHANGES

**Konfidenz:** hoch  
**Befundzählung:** `P0=0, P1=0, P2=1, P3=0`  
**Scope-Drift:** `0`

## Befund

| Priorität | Befund | Ort |
|---|---|---|
| P2 | Der behauptete Vertrag „**jeder Nicht-Exit-Fehler** beim pidfd-Erwerb wird vor einer Signalisierung in persistierte Ambiguität übersetzt“ ist nicht vollständig umgesetzt. Supervisor- und Kandidatenpfad behandeln ausschließlich `OSError` und `RuntimeError`. Andere normale `Exception`-Typen – konkret etwa ein `ValueError` aus `int(opener(pid, 0))` – verlassen `_signal_posix_authority()` unverändert. `stop()` fängt nur `ProcessAuthorityAmbiguousError`; daher bleiben `forced_status` und die persistierte Autorität unverändert. Es wird zwar fail-closed **kein Signal** gesendet, aber die geforderte dauerhafte Ambiguitätsabbildung fehlt. Die Tests decken nur `EACCES`/`EPERM`/`EMFILE`, `ProcessLookupError` und den speziellen Supervisor-`RuntimeError` ab; ein sonstiger Nicht-Exit-Fehler durch den vollständigen `stop()`-/Persistenzpfad fehlt. | `apps/web/scan_jobs.py:411-416`, `apps/web/scan_jobs.py:449-461`, `apps/web/scan_jobs.py:516-527`, `apps/web/scan_jobs.py:946-951`; Testlücke: `tests/test_web_scan_jobs.py:498-524`, `tests/test_web_scan_jobs.py:642-661` |

**Erforderliche Korrektur:** Nach den bestätigten Exit-Fällen (`ProcessLookupError`/`ESRCH`) alle übrigen normalen Erwerbsausnahmen – semantisch `Exception`, nicht `BaseException` – als `ProcessAuthorityAmbiguousError` klassifizieren. Ein adversarialer Test muss über `LocalScanJobService.stop()` belegen: kein Signal, `forced_status == "authority_ambiguous"` und derselbe Zustand in der langlebigen State-Datei.

## Weitere Prüfergebnisse

- Supervisor-`RuntimeError` wird jetzt korrekt in `ProcessAuthorityAmbiguousError` übersetzt.
- `EACCES`, `EPERM` und `EMFILE` sind fail-closed und explizit getestet.
- PID-/PGID-Wechsel nach dem Öffnen wird vor Provenienzprüfung erneut kontrolliert; das pidfd bleibt an die geöffnete Prozessidentität gebunden.
- `_raise_start_failure()` führt Rollback und Persistenz unabhängig aus, setzt bei Rollbackfehler `rollback_failed`, versucht dessen dauerhafte Speicherung und behält Primär-, Rollback- und Persistenzfehler in dieser Reihenfolge.
- Bei ausschließlich normalen `Exception`-Elementen wird der konstruierte `BaseExceptionGroup` von Python automatisch als `ExceptionGroup` zurückgegeben. Enthält die Gruppe `KeyboardInterrupt`, `SystemExit` oder eine andere direkte `BaseException`, bleibt sie ein `BaseExceptionGroup`. In beiden Fällen steht die ursprüngliche Startausnahme an Position 1.
- Aktuelle und bereits übertragene Deskriptoren werden auch unter `SystemExit` vollständig zur Schließung versucht; ein Close-Fehler überspringt keine späteren Handles und maskiert den aktiven `SystemExit` nicht.
- Die v9–v13-Befunde sowie Auth/Authz, Session/Secrets, Ownership/Tenant-Bindung, Rate Limits, Durable Stores, „Neuer Fall“, Windows-Prozessbaum, Hardware-Konvergenz, Poll-Single-Flight und Accessibility wurden erneut statisch verfolgt. Außer dem oben genannten Restvertrag ergaben sich keine weiteren P0–P3-Befunde. Die produktiven Dateien dieser Bereiche sind gegenüber Freeze v13 unverändert; v14 änderte produktiv nur `apps/web/scan_jobs.py`.

## Freeze-v14-Bindung

Start und Ende stimmen überein:

- Branch: `operator-workbench-phase1`
- HEAD: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- Manifest-SHA-256: `ff06cb2902f5a43cefee09afc3bda9971d5a558efc1576b6f508269b85513f68`
- Einzelhashes: `93/93 OK`
- Aggregat: `3e7dd5ca5c85ba1cc87a26d79f909125da7448f2e284a8590af13c0bca1bb601`
- Exakte Population: `94`
- Scope minus Dirty: leer
- Dirty minus Scope: leer
- Status-Fingerprint Start/End: `f2cccb3eb949492f2ccffe133fc49758fdceb428b0d5fbb1c3edd94530eb0db3`
- Drift: **keine**

**Dateien erstellt oder verändert:** keine.  
**Ausführung:** keine Tests, Projekt-Imports, Server, Netzwerkzugriffe oder Installationen.  
**Hinweis:** Ein erster End-Populationsprobe enthielt einen Shell-Subshell-Auswertungsfehler und meldete fälschlich alle Scope-Dateien als nicht dirty. Der korrigierte vollständige Wiederholungslauf ergab `Scope minus Dirty=0`, `Dirty minus Scope=0` und Population `94`; Hash- und Statusbindung blieben unverändert.