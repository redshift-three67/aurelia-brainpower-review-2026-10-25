# REQUEST CHANGES

**Konfidenz:** HOCH  
**Befundzählung:** `P0=0, P1=2, P2=0, P3=0`

## Befunde

### P1 — Ein normaler pidfd-Exit-Race bricht Stop/Rollback vor dem Signalisieren weiterer Prozesse ab

**Ort:** `apps/web/scan_jobs.py:419-444`, insbesondere `:437-439`  
**Unzureichender Test:** `tests/test_web_scan_jobs.py:386-423`

`_signal_posix_authority()` sammelt mehrere stabile Handles, signalisiert sie anschließend aber in einer Schleife ohne Behandlung von `ProcessLookupError`/`OSError`:

```python
for descriptor in handles:
    sender(descriptor, sent_signal, None, 0)
```

Ein token-validierter Prozess darf zwischen Enumeration und `pidfd_send_signal()` regulär enden. Liefert sein pidfd dann `ESRCH`/`ProcessLookupError`, bricht die Funktion sofort ab. Alle späteren, weiterhin laufenden und bereits validierten Prozesse werden nicht signalisiert.

Auswirkungen:

- `stop()` propagiert die Ausnahme aus `apps/web/scan_jobs.py:782` beziehungsweise `:794`, bevor Abwesenheitsbestätigung und `forced_status="stopped"` erreicht werden.
- Der Start-Rollback bricht entsprechend an `apps/web/scan_jobs.py:474` oder `:483` ab und kann produktive Nachkommen zurücklassen.
- Forks während einer Enumerationsrunde verschärfen das Problem: Die Implementierung wiederholt keine Signal-/Enumerationsrunde bis zu einem leeren, bestätigten Snapshot; nach einem stale pidfd kann sie sogar vor der ersten vollständigen Runde abbrechen.
- Der neue Test lässt `pidfd_send_signal()` ausschließlich erfolgreich sein und modelliert den unvermeidbaren Exit-Race nicht.

**Erforderlich:** `ESRCH` pro Handle als bereits konvergiert behandeln, andere Fehler fail-closed sammeln, alle übrigen Handles trotzdem bearbeiten und Signal/Enumeration begrenzt wiederholen, bis kein token-validierter Prozess mehr vorhanden ist. Adversarial testen: erstes Handle wird vor dem Send stale, zweites bleibt aktiv und muss dennoch signalisiert werden; zusätzlich Fork zwischen zwei Runden.

---

### P1 — „New Case“ kann einen gleichzeitig gestarteten Scan orphanen

**Ort:** `apps/web/static/app.js:350-395`, `:856-868`, `:900-908`

`startScanJob()` wartet an Zeile 367 auf die serverseitige Erstellung. Bis zur Antwort existiert lokal noch keine `activeJobId`:

```javascript
const result = await ...startScanJob(body);
if (generation !== caseGeneration) return;
state.activeJobId = jobId;
```

`resetWorkbenchForNewCase()` blockiert jedoch nur auf `pendingMutations`/`resetInProgress` und stoppt ausschließlich eine bereits gesetzte `activeJobId`. `scanStartPending` wird nicht geprüft:

```javascript
if (state.pendingMutations > 0 || state.resetInProgress) return false;
...
if (state.activeJobId) await ...stopScanJob(...)
```

Damit ist folgende Race möglich:

1. Scan-POST wurde serverseitig angenommen, Antwort ist noch ausstehend.
2. „New Case“ sieht keine `activeJobId` und beginnt den Reset.
3. Die Startantwort trifft während oder nach dem Stop-Abschnitt ein.
4. Vor dem Generation-Inkrement kann sie eine Job-ID setzen, die der Reset anschließend verwirft; danach wird sie wegen des Generation-Guards unmittelbar verworfen.
5. Der Serverjob läuft weiter, ohne dass der neue Fall seine ID behält oder ihn stoppen kann.

Der Generation-Guard schützt nur die UI, nicht die bereits erfolgte Servermutation.

**Erforderlich:** Fallwechsel mindestens während `scanStartPending` sperren oder Starts in `pendingMutations` einbeziehen. Robuster ist, die Startantwort auch nach einem Generationwechsel auszuwerten und die erhaltene Job-ID kompensierend zu stoppen. Ein verzögerter Start-vs.-Reset-Browsertest muss beweisen, dass kein Serverjob ohne lokale Stop-Autorität verbleibt.

## Weitere Prüfung

Ohne zusätzliche P0–P3-Befunde statisch nachverfolgt:

- Token fehlt in Gate-`argv`; Übergabe erfolgt über `MORPHIC_SCAN_GATE_TOKEN`, das vor dem produktiven Spawn aus der Gate-Umgebung entfernt wird.
- Tokenhaltiger State wird über temporäre Dateien mit `0600` und Runtime-Verzeichnis mit `0700` publiziert.
- Fremdtoken-, `AccessDenied`- und supervisorlose Pfade signalisieren keine numerische PGID.
- Auth/Authz, Session/Secrets, Owner-/Tenant-/Reportbindung, Rate-Limit-Klassen, durable Stores, Windows-Job-Pfad, Hardware-Konvergenz, Poll-Promise-/Timer-Autorität, Generation-Cleanup und Accessibility wurden auf Regressionen geprüft.
- Keine Tests, Imports, Server, Netzwerkzugriffe oder Installationen ausgeführt.

## Freeze-/Driftbindung

| Prüfung | Start | Ende |
|---|---|---|
| Branch | `operator-workbench-phase1` | identisch |
| HEAD | `3271ff9366ab3fecb2a158913a0cc19ed6a06726` | identisch |
| Manifest-SHA-256 | `713857a5a092984539febefe81688402b57b24cd96a5bf89806cb337061bf1e9` | identisch |
| Manifest-Einträge | 77 | 77 |
| Einzelhashes | 77/77 OK | 77/77 OK |
| LF-Aggregat | `3dc9980ec125b21fc3a604d747735e59364108eded5c913b55e51f3cc1e1370e` | identisch |
| Dirty-Population | 78 | 78 |
| Scope + Freeze | exakt 78 | exakt 78 |
| Bidirektionale Scope-Differenz | leer | leer |
| Drift | keine | keine |

**Dateien erstellt oder verändert:** keine.