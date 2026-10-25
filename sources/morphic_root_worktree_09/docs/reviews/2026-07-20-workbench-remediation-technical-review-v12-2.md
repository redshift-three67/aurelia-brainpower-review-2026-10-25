## Code Review

**Verdikt: REQUEST CHANGES**  
**Konfidenz: HOCH**  
**Befundzählung:** `P0=0, P1=2, P2=1, P3=0`

### Befunde

| Priorität | Befund | Ort |
|---|---|---|
| P1 | Die pidfd-Enumeration öffnet Handles für **jeden Prozess des Systems, bevor dessen PGID geprüft wird**. `EACCES`, `EPERM`, `EMFILE` oder andere Fehler bei einem völlig unbeteiligten Prozess brechen deshalb Stop und Rollback als „authority ambiguous“ ab. | `apps/web/scan_jobs.py:428-449` |
| P1 | Das Beenden des Supervisors zwischen `poll()` und `_open_pidfd()` wird nicht als normale Exit-Race behandelt. Ein `ESRCH`/`ProcessLookupError` bricht die gesamte Signalrunde ab, statt die tokengebundenen Gruppenmitglieder weiter zu enumerieren; andere Erwerbsfehler werden zudem nicht in den persistierten Ambiguitätszustand übersetzt. | `apps/web/scan_jobs.py:492-515`, `apps/web/scan_jobs.py:898-903`; Rollback: `apps/web/scan_jobs.py:561-587` |
| P2 | Die Tests behaupten eine vollständig adversariale Erwerbs-/Enumerationsabdeckung, prüfen aber weder unbeteiligte Prozesse noch Supervisor-Exit beim pidfd-Erwerb, `EMFILE`, konkrete `EACCES`/`EPERM`-Errnos oder beide Enumerationsreihenfolgen. | `tests/test_web_scan_jobs.py:428-519` |

### Details

#### P1 – Fehler unbeteiligter Prozesse blockieren jede Signalrunde

In `_token_process_pidfds()` lautet die Reihenfolge:

1. PID aus `process_iter()` lesen,
2. `_open_pidfd(pid)` aufrufen,
3. erst danach Zombie-Status und `os.getpgid(pid)` prüfen.

Damit wird beispielsweise ein `EPERM` für einen Prozess außerhalb der Ziel-PGID als Ambiguität der Zielgruppe behandelt. Bereits akkumulierte Handles werden korrekt geschlossen und es wird nichts signalisiert, aber produktive Stop-/Rollback-Vorgänge können durch beliebige fremde Systemprozesse dauerhaft blockiert werden. Das ist besonders relevant auf Hosts mit eingeschränkten Namespaces oder heterogenen Prozessberechtigungen.

**Erforderliche Korrektur:** Fremde Prozesse müssen vor einem autoritätsrelevanten Erwerbsfehler sicher ausgesondert werden. Für Kandidaten der Ziel-PGID ist anschließend ein stabiler Handle zu erwerben und Mitgliedschaft, Identität und Token müssen vor Signalversand erneut validiert werden, ohne PID-Reuse wieder zu autorisieren.

#### P1 – Supervisor-Exit-Race kann Stop und Rollback abbrechen

`_signal_posix_authority()` prüft zuerst:

```python
if job.process.poll() is None:
    supervisor_descriptor = _open_pidfd(job.process.pid)
```

Endet der Supervisor unmittelbar nach `poll()`, propagiert `ProcessLookupError`/`ESRCH` aus `_open_pidfd()` ungefangen. Die danach vorgesehene Enumeration tokengebundener Nachfahren wird nicht mehr erreicht. Im Stop-Pfad wird außerdem nur `ProcessAuthorityAmbiguousError` persistiert; ein roher Erwerbsfehler verlässt den Pfad ohne konsistenten Status. Im Start-Rollback kann derselbe Fehler den ursprünglichen Fehler maskieren und die Kontrolle über bereits gestartete Nachfahren gefährden.

**Erforderliche Korrektur:** Supervisor-`ESRCH` muss als „Supervisor verschwunden“ behandelt werden und zur vollständigen Gruppen-Enumeration weiterführen. Nicht-`ESRCH`-Erwerbsfehler müssen fail-closed in den konsistenten Ambiguitätsvertrag eingehen. Dafür sind Tests mit Supervisor-Exit zwischen `poll()` und `_open_pidfd()`, PID-Reuse sowie fortbestehendem legitimem Nachfahren erforderlich.

### Weitere adversariale Ergebnisse

- Vollständige Zielgruppenprüfung in `_process_group_alive()` behandelt später gefundene `AccessDenied`-, fehlende und abweichende Tokens fail-closed.
- Bei Ausnahmen nach akkumulierten pidfds werden aktueller und bereits gesammelte Handles geschlossen.
- `pidfd_send_signal`-`ESRCH` eines stale Handles verhindert die Bearbeitung späterer Handles nicht.
- TERM/KILL-Runden enumerieren erneut und decken Forks zwischen Runden grundsätzlich ab.
- Persistierte Ambiguität kann durch einen expliziten späteren Stop nach eindeutig bestätigter Abwesenheit zu `stopped` übergehen.
- „Neuer Fall“ bleibt während Mutationen sowie bei nicht sicher beendetem Scan blockiert; der verzögerte Start behält seine Generation und Job-ID.
- Keine weiteren P0–P3-Regressionsbefunde in den nachverfolgten Security-, Lifecycle- und Produktpfaden.

### Freeze-/Driftbindung

Start und reservierte Endbindung stimmen exakt überein:

- Branch: `operator-workbench-phase1`
- HEAD: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- Manifest-SHA-256: `1d4931a9e14387ce891b8a27d39235889c671cc66b9375f2e78a78d7eb74d2fc`
- Einzelhashes: **85/85 OK**
- Aggregat: `a51bbec277472ba434a645edd8d2862478938eed0f7529ce7d68628fc3d988ae`
- Exakte Dirty-Population: **86**
- Dirty minus Scope plus Manifest: leer
- Scope minus Dirty: leer
- End-Status-Fingerprint: `6d4499e3b36776a35cdcdadbd8b9f64803c8f9214284eaceeb5646a367608369`
- Drift: **0**

**Dateien erstellt oder verändert:** keine.  
**Tests/Imports/Server/Netzwerk:** gemäß Read-only-/No-execution-Vorgabe nicht ausgeführt.