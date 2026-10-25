## Code Review

**Verdikt: REQUEST CHANGES**  
**Konfidenz: HOCH**

### Findings

| Priorität | Befund | Ort |
|---|---|---|
| P1 | Fehler beim Erwerb eines `pidfd` – einschließlich `EACCES`/`EPERM` – werden pauschal übersprungen. Dadurch kann ein nicht vollständig autorisierter Signal-Durchlauf trotzdem andere Prozesse terminieren. | `apps/web/scan_jobs.py:415-433` |
| P1 | Mitglieder der Ziel-PGID mit fehlendem oder abweichendem Provenienz-Token werden als nicht existent behandelt, obwohl ihre Existenz feststeht. Das kann verwaiste Prozesse und einen falsch terminalen Jobstatus erzeugen. | `apps/web/scan_jobs.py:292-311`, `apps/web/scan_jobs.py:419-429` |
| P1 | Ein persistiertes `authority_ambiguous` kann nach später eindeutig bestätigter Abwesenheit nicht in einen erfolgreichen terminalen Zustand überführt werden und kann dadurch Teardown bzw. „Neuer Fall“ dauerhaft blockieren. | `apps/web/scan_jobs.py:800-841`, `apps/web/scan_jobs.py:843-865` |

**Severity-Zählung:** P0=0, P1=3, P2=0, P3=0.

### Details

#### P1 – `pidfd_open`-Fehler werden vor der PGID-Prüfung verschluckt

`_token_process_pidfds()` ruft zuerst `_open_pidfd(pid)` auf. Jeder dabei entstehende `OSError` landet anschließend in:

```python
except (ProcessLookupError, psutil.Error, OSError):
    pass
```

Damit werden nicht nur `ESRCH`-Exit-Races, sondern auch `EACCES`, `EPERM`, Ressourcenfehler und andere nicht-`ESRCH`-Fehler ignoriert. Da die Enumeration danach weitere Deskriptoren sammeln und `_signal_posix_authority()` diese signalisieren kann, ist ein partieller Signal-Durchlauf möglich.

Insbesondere kann ein Ziel-PGID-Mitglied, dessen `pidfd_open` mit AccessDenied scheitert, übersprungen werden, weil seine PGID erst **nach** dem fehlgeschlagenen Öffnen geprüft würde. Die v11-Zusage „abort the complete signal round before any pidfd is signalled“ ist damit nicht vollständig erfüllt.

**Erforderliche Korrektur:** Nur einen eindeutig belegten `ESRCH`/`ProcessLookupError` als Prozess-Exit behandeln. Alle anderen Descriptor-Erwerbsfehler müssen fail-closed in die Rundenauswertung eingehen; vor dem ersten Signal muss feststehen, dass die gesamte relevante Ziel-PGID autoritativ enumeriert wurde.

#### P1 – Ziel-PGID-Mitglieder ohne passenden Token werden als abwesend klassifiziert

Sowohl `_process_group_alive()` als auch `_token_process_pidfds()` ignorieren ein bereits eindeutig als Mitglied der Ziel-PGID erkanntes Verfahren, wenn:

```python
token != process_group_token
```

Ein Prozess kann seine Umgebung selbst bereinigen oder einen Nachfahren mit bereinigter Umgebung starten. Ebenso kann ein abweichender Token auf PGID-Wiederverwendung hindeuten. In beiden Fällen ist der Prozess aber nicht „abwesend“: Die Autorität ist **mehrdeutig**.

Aktuell können nach dem Ende des tokenführenden Supervisors nur solche tokenlosen bzw. tokenabweichenden Nachfahren verbleiben. `_process_group_alive()` liefert dann `False`; `stop()` überspringt die Konvergenz, und `_snapshot()` kann den Job als `completed` oder `failed` festschreiben, obwohl die Zielgruppe noch lebt.

**Erforderliche Korrektur:** Jedes nicht-zombie Ziel-PGID-Mitglied ohne exakt passenden lesbaren Token muss `ProcessAuthorityAmbiguousError` auslösen. Es darf weder signalisiert noch als Abwesenheit gewertet werden.

#### P1 – `authority_ambiguous` bleibt nach bestätigter Abwesenheit kleben

Nach einem AccessDenied speichert `stop()`:

```python
job.forced_status = "authority_ambiguous"
```

Bei einem späteren Stop-Versuch, nachdem Supervisor und Gruppe nachweislich nicht mehr aktiv sind, wird `forced_status` nicht aktualisiert. `_snapshot()` priorisiert anschließend weiterhin den alten erzwungenen Status. Somit gibt es keinen erfolgreichen terminalen Übergang, obwohl die Abwesenheit jetzt autoritativ bestätigt wurde.

Das kann den Scan dauerhaft als nicht abgeschlossen darstellen und den Fallwechsel blockieren. Ein erneuter Stop hilft nur, wenn zu diesem Zeitpunkt noch aktive Autorität existiert und die Konvergenz tatsächlich ausgeführt wird.

**Erforderliche Korrektur:** Nach einer vollständig autoritativen, nicht mehr mehrdeutigen Abwesenheitsprüfung muss `authority_ambiguous` atomar in einen definierten terminalen Zustand überführt werden, beispielsweise `stopped`, und persistiert werden. Der Übergang muss unter demselben Prozess-/Job-Lock erfolgen.

### Weitere Fokusprüfungen

- `pendingMutations` wird in `workbench-api.js:16-22` synchron **vor dem ersten `await fetch(...)`** erhöht. Der verzögerte Scan-Start liegt damit grundsätzlich innerhalb des Mutation-Fence.
- Die pidfd-Signal-Schleife behandelt `ProcessLookupError` und `errno.ESRCH` pro Handle und fährt mit späteren Handles fort.
- Die TERM/KILL-Konvergenz enumeriert wiederholt und ist zeitlich begrenzt.
- Supervisor-, Deskriptor-, Stop/Completion-, Hardware-Child- und Reset-/Generationspfade wurden in die transitive Prüfung einbezogen. Die drei obigen Fehler verhindern dennoch eine Freigabe.

### Freeze-v11-Bindung

Start und Ende waren konsistent:

- Branch: `operator-workbench-phase1`
- HEAD: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- Manifest SHA-256: `2a089645bcc6e6265e013b48f13f31181e65c7cc09191184a5a81d8320e9427a`
- Einträge: **81/81**, keine fehlerhaften Datei-Hashes
- Aggregat: `802b19686a013a37e4e51e9a535579cd7d9e4b0253353a6947edec3c1d2c4f9d`
- Exakte Population: **82**
- Fehlende/zusätzliche Scope-Pfade: keine
- Drift: **0**
- Tests wurden gemäß Read-only-/No-tests-Vorgabe nicht erneut ausgeführt.

### Arbeitsbereich

- Keine Dateien erstellt oder verändert.
- Keine Tests, Imports, Server, Installationen oder Netzwerkzugriffe ausgeführt.