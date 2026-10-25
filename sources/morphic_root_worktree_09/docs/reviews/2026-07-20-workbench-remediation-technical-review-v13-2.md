## Code Review

**Verdikt: REQUEST CHANGES**  
**Konfidenz: HOCH**  
**Befundzählung:** `P0=0, P1=2, P2=1, P3=0`  
**Scope-Drift:** `0`

### Befunde

| Priorität | Befund | Ort |
|---|---|---|
| P1 | `_open_pidfd()` kann für den Supervisor ausdrücklich `RuntimeError` melden, wenn stabile POSIX-Handles nicht verfügbar sind. `_signal_posix_authority()` übersetzt aber nur `OSError` in `ProcessAuthorityAmbiguousError`. Der rohe Fehler umgeht damit den persistierten Ambiguitätsvertrag in `stop()`. | `apps/web/scan_jobs.py:411-416`, `apps/web/scan_jobs.py:513-523`, `apps/web/scan_jobs.py:927-931` |
| P1 | Ein Fehler des Post-Release-Rollbacks maskiert weiterhin die ursprüngliche Ausnahme aus `_snapshot()`/Publikation – einschließlich `KeyboardInterrupt` oder `SystemExit`. Zudem werden `forced_status="failed"` und die abschließende Persistierung übersprungen, wenn `_rollback_scan_authority()` selbst scheitert. | `apps/web/scan_jobs.py:858-877`, insbesondere `870-877` |
| P2 | Die Testmatrix belegt die umfassenden v13-Verträge nicht vollständig: kein Supervisor-`RuntimeError`, kein explizites `EMFILE`, keine Kandidaten-Exit/PID-Reuse-Sequenz zwischen Prefilter/Open/Revalidierung, keine Close-Fehler auf middle/current/transferred Handles unter `KeyboardInterrupt`/`SystemExit` und kein Test gegen Maskierung der ursprünglichen Startausnahme. | `tests/test_web_scan_jobs.py:497-597`, `1119-1156` |

### Details

#### P1 – Supervisor-Fehler außerhalb von `OSError` bleiben unklassifiziert

Der produktive Helper besitzt diesen Vertrag:

```python
if opener is None or sender is None:
    raise RuntimeError("stable POSIX process handles are unavailable")
```

Der Supervisor-Pfad behandelt dagegen lediglich `ProcessLookupError` und `OSError`. Folglich wird der dokumentierte v13-Satz „Other supervisor acquisition failures become `ProcessAuthorityAmbiguousError`“ nicht erfüllt. Im Stop-Pfad wird dann weder `authority_ambiguous` gesetzt noch persistiert.

**Erforderlich:** Sämtliche Nicht-Exit-Fehler des Supervisor-Handle-Erwerbs – einschließlich des eigenen `RuntimeError`-Vertrags – vor jeder Signalisierung in `ProcessAuthorityAmbiguousError` übersetzen und adversarial testen.

#### P1 – Rollback maskiert die auslösende Ausnahme

Der Startpfad enthält weiterhin:

```python
except BaseException:
    _rollback_scan_authority(job)
    job.forced_status = "failed"
    ...
    raise
```

Wirft `_rollback_scan_authority()` etwa wegen Ambiguität, fehlender stabiler Handles oder eines Close-Fehlers, ersetzt dieser Fehler die ursprünglich aktive Ausnahme. Die danach stehende Status-/Persistenzlogik wird ebenfalls nicht erreicht. Die ausnahmetotale Behandlung innerhalb der pidfd-Cleanup-Funktionen schließt diesen übergeordneten Lifecycle-Pfad nicht.

**Erforderlich:** Original- und Rollbackfehler getrennt erfassen, den fehlgeschlagenen Rollback dauerhaft sichtbar machen und die Primärausnahme nicht stillschweigend ersetzen, beispielsweise durch geeignete Verkettung bzw. `ExceptionGroup`.

### Adversariale Bewertung

- Fremde PGIDs werden vor `_open_pidfd()` gefiltert; ein Open-Fehler eines sicher fremden Prozesses blockiert die Runde nicht.
- `EACCES`/`EPERM` beziehungsweise andere Open-Fehler bei einem Zielkandidaten führen vor dem ersten Signal fail-closed zu Ambiguität.
- Supervisor-`ProcessLookupError`/`ESRCH` setzt die Enumeration valider Nachkommen fort.
- Token-Mismatch und unlesbare Zielgruppen-Provenienz verhindern die gesamte Signalrunde.
- Aktuelle und übertragene Handles werden bei normalen `Exception`- und `BaseException`-Pfaden konzeptionell vollständig abgearbeitet; die Tests beweisen jedoch nur einen isolierten Fehler am ersten Handle.
- TERM/KILL-Runden enumerieren erneut und können zwischen den Runden auftretende Forks erfassen; bestätigte Abwesenheit kann einen persistierten Ambiguitätszustand in `stopped` überführen.
- Keine weiteren P0–P3-Befunde in den nachverfolgten Security-, Ownership-, Recovery-, Hardware-, Polling- und Produkt-Lifecycle-Pfaden.

### Freeze-v13-Bindung

Start und reservierte Endbindung waren identisch:

- Branch: `operator-workbench-phase1`
- HEAD: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- Manifest-SHA-256: `34ffd894bc392c6edfa83660ae2652eafb64d1b7fec85b520c60e380a832e9fa`
- Einzelhashes: **89/89 OK**
- Aggregat: `eeae5c32adeccca03a58e5eb5f8bfa2fe994b89d629f9adfb87269ad1d333c77`
- Exakte Population: **90**
- Scope minus Population: leer
- Population minus Scope: leer
- Status-Fingerprint Start/End: `74f86bd5aaa9e036c6865a480eb03742c042474f23f697606790ec585ebe8989`
- Drift: **0**

**Dateien erstellt oder verändert:** keine.  
**Tests/Produktcode ausgeführt:** nein, entsprechend der strikten Read-only-/No-execution-Vorgabe.