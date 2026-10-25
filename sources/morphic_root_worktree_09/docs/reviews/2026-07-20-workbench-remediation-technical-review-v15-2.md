## Zweites adversariales Freeze-v15-Review

**Verdikt: REQUEST CHANGES**  
**Konfidenz: HOCH**  
**Befunde:** `P0=0, P1=1, P2=0, P3=0`  
**Scope-Drift:** `0`

### Befund

| Priorität | Befund | Ort |
|---|---|---|
| **P1** | Ein nicht-exitbedingter Fehler bei der Creation-Time-Revalidierung des Supervisors **nach erfolgreichem `pidfd_open()`** wird als bloßer Identitäts-Mismatch verschluckt. Dadurch können tokengebundene Nachfahren signalisiert werden, obwohl die Supervisor-Autorität nicht positiv revalidiert wurde; `authority_ambiguous` wird weder gesetzt noch persistiert. | `apps/web/scan_jobs.py:266-277`, `apps/web/scan_jobs.py:533-565` |

#### Reproduzierbare statische Falsifikation

1. `job.process.poll()` meldet einen aktiven Supervisor.
2. `_open_pidfd(job.process.pid)` liefert erfolgreich ein stabiles Handle.
3. `psutil.Process(pid).create_time()` wirft beispielsweise `OSError(EACCES)` oder `psutil.AccessDenied`.
4. `_process_create_time()` fängt pauschal `OSError`/`psutil.Error` und liefert `None`.
5. `_process_identity_matches()` liefert dadurch lediglich `False`; der Nicht-Exit-Fehler wird nicht als Ambiguität klassifiziert.
6. `_token_process_pidfds()` erwirbt anschließend gültige Nachfahren-pidfds.
7. `_signal_posix_authority()` signalisiert diese Nachfahren.

Damit erfolgt ein Signal **nach einer unaufgelösten Supervisor-Revalidierung**, statt vor jeder Signalisierung fail-closed abzubrechen. Der vorhandene EACCES-Test injiziert den Fehler nur in `os.getpgid()` und ersetzt `_process_identity_matches()` durch `True`; dieser Pfad bleibt daher ungetestet (`tests/test_web_scan_jobs.py:742-773`).

**Erforderliche Korrektur:** Die post-open Creation-Time-Prüfung muss bestätigte Exit-Races (`NoSuchProcess`, `ProcessLookupError`, `ESRCH`) von allen anderen Fehlern unterscheiden. Nicht-Exit-Fehler müssen vor der Nachfahrenenumeration zu `ProcessAuthorityAmbiguousError` werden. Ein vollständiger `stop()`-Test muss **kein Signal**, exakt einmaliges Schließen des Supervisor-pidfd sowie dauerhaftes `forced_status == "authority_ambiguous"` belegen.

### Weitere Prüfergebnisse

Ohne zusätzlichen P0–P3-Befund statisch nachvollzogen:

- `ValueError`/generische Erwerbsfehler bei Supervisor- und Kandidaten-pidfd werden grundsätzlich in Ambiguität übersetzt.
- Kandidaten-`OSError`: nur bestätigtes `ESRCH` wird als Exit behandelt; `EACCES`, `EPERM` und `EMFILE` sind fail-closed.
- PGID-Revalidierung nach pidfd-Erwerb verhindert die Übernahme einer wiederverwendeten numerischen PID.
- Gemischte oder unlesbare Tokenpopulation wird vollständig vor der ersten Signalisierung abgelehnt.
- Supervisor-Exit nach erfolgreichem Open lässt legitime Nachfahrenkontrolle zu.
- TERM/KILL-Runden re-enumerieren fortgesetzte oder neu entstandene Nachfahren.
- Aktuelle, übertragene und Supervisor-Handles werden ohne doppelte Schließung abgearbeitet; Close-Fehler überspringen keine späteren Handles.
- `BaseExceptionGroup` bewahrt Primärfehler, Traceback, Rollback- und Persistenzfehler in stabiler Reihenfolge.
- Rollback- und Persistenzfehler werden unabhängig gesammelt; `rollback_failed` wird vor dem Persistenzversuch gesetzt.
- Stop-/Ambiguitätszustände werden auf den untersuchten definierten Pfaden dauerhaft publiziert.
- Produkt-/Security-Scope sowie unveränderte Authentifizierung, Ownership, langlebige Stores, Windows-Prozessbaum-, Hardware-, Frontend- und Polling-Verträge wurden mit den Tests und vorherigen Freeze-Befunden abgeglichen.

### Freeze-v15-Bindung

Start und Ende stimmen überein:

- Branch: `operator-workbench-phase1`
- HEAD: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- Manifest-SHA-256: `de20792835dd7e68a7ef18e4aaf0cd3e76815f29dc950ab947bef751f6a009a6`
- Einzelhashes: **97/97 OK**
- Exaktes Hashzeilen-Aggregat: `f39ec0f9c5522b194160c4b2ead5aacf20a5601d23fdc9231c9f9ccaf176d853`
- Exakte Population: **98**
- Scope minus Dirty: leer
- Dirty minus Population: leer
- Population minus Dirty: leer
- End-Status-Fingerprint (`git status --porcelain=v1 -z`): `931549e5bc024d2bb470481ec4c295db6019fd9f01dbffe578e530d21b3d3aa1`
- Drift: **keine**

**Dateien erstellt oder verändert:** keine.  
**Ausführung:** keine Tests, Projektimporte oder Produktprozesse. Ein erster Hash-Verifikationsversuch hatte ausschließlich einen Inline-Python-Quotingfehler; die vollständige Wiederholung sowie die reservierte Endbindung waren erfolgreich.