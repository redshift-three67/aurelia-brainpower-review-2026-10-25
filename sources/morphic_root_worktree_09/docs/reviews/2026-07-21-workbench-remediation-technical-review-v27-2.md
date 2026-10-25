## Freeze-v27 – Technisches Review 2

**Entscheidung: REQUEST CHANGES**  
**Konfidenz: HOCH**

### Befundzahlen

| Schweregrad | Anzahl |
|---|---:|
| P0 | 0 |
| P1 | 3 |
| P2 | 2 |
| P3 | 0 |
| **Gesamt** | **5** |

### Freeze- und Drift-Verifikation

| Eigenschaft | Start | Ende |
|---|---|---|
| Branch | `operator-workbench-phase1` | identisch |
| HEAD | `3271ff9366ab3fecb2a158913a0cc19ed6a06726` | identisch |
| Manifest-SHA-256 | `067a54316eee54ee313183192f29a2c7aae548227cc781df4c71e7b94553e47e` | identisch |
| Manifest-Einträge | 160 | 160 |
| Hash-Aggregat | `65417cc985d105821ee725998ca503448901232335ad7cbba8a3c51651086511` | identisch |
| Abweichende Eintrags-Hashes | 0 | 0 |
| Dirty Population | 161 | 161 |
| Fehlende/zusätzliche Pfade | 0 / 0 | 0 / 0 |
| Status-Fingerprint | `7a6d29285360fa1ddeaf04d9e574cfbc8eabbfd9bf48b840c6cdba5e520e1633` | identisch |

**Drift: keiner.** Die Prüfung ist vollständig an die verlangten Freeze-v27-Bytes gebunden.

## Findings

### P1 – WebSockets können nach Auth-Widerruf oder Owner-Wechsel noch Daten senden

Die beiden WebSocket-Schleifen prüfen Authentifizierung bzw. Ownership vor dem produktiven Lesen, revalidieren aber nicht nochmals unmittelbar nach dem Read und vor `send_json()`:

- `apps/web/scan_live.py:67-105`
- `apps/web/emf.py:113-121`

Damit bleibt ein belastbares Zeitfenster:

1. Auth/Owner wird validiert.
2. Jobstatus oder EMF-Profil wird gelesen beziehungsweise gemessen.
3. API-Key, Session oder Ownership wird widerrufen/geändert.
4. Der bereits gelesene geschützte Payload wird trotzdem gesendet.

Die Tests widerrufen jeweils deterministisch bei der Prüfung vor dem Read und decken keinen Widerruf während des Reads bzw. der Messung ab:

- `tests/test_web_scan_live_security.py:111-137`
- `tests/test_web_emf_security.py:60-91`

**Erforderlich:** Generation und Ownership nach dem produktiven Read beziehungsweise der Messung und vor jedem Frame erneut validieren; idealerweise den gelesenen Payload an die validierte Generation binden.

---

### P1 – EMF-Autorität ist bei fehlender Authority-Bindung fail-open und nicht atomar zur Messung

`capture_realtime_context()` blockiert Messungen nur, wenn `_emf_authority_path` vorhanden und deaktiviert ist. Fehlt der interne Pfad, wird ohne Autoritätsprüfung gemessen:

- `services/harmonization_worker.py:357-367`

Der bestehende Test schreibt dieses fail-open-Verhalten ausdrücklich fest:

- `tests/test_harmonization_worker_stop.py:289-315`

Zusätzlich liegt zwischen `is_enabled()` und den Messungen ein ungeschütztes Zeitfenster:

- Prüfung: `services/harmonization_worker.py:360-365`
- Messung/Fallback: `services/harmonization_worker.py:366-391`

Ein paralleles Disable kann daher nach erfolgreicher Prüfung eintreten, während anschließend noch eine EMF- oder Hardware-Snapshot-Messung startet bzw. publiziert wird. Dasselbe Muster besteht im EMF-WebSocket bei `apps/web/emf.py:117-121`.

**Erforderlich:** Fehlende Autoritätsbindung muss für produktive Messpfade fail-closed sein. Disable und Messungsbeginn benötigen eine generation-/lease-basierte Autorität; vor Publikation ist erneut zu prüfen.

---

### P1 – Windows-Job-Stop bestätigt nur den Supervisor, nicht den vollständigen Prozessbaum

`_terminate_windows_job()` terminiert den Job und kann den Job-Handle unmittelbar schließen:

- `apps/web/scan_jobs.py:562-603`

Der aufrufende Stop-Pfad wartet danach ausschließlich auf `job.process`, also den Gate-/Supervisor-Prozess:

- `apps/web/scan_jobs.py:1403-1413`

Danach wird ohne erneute Job-Abfrage `stopped` publiziert:

- `apps/web/scan_jobs.py:1429-1432`

Damit fehlt eine handle-basierte Bestätigung, dass `ActiveProcesses == 0` für den vollständigen Windows Job Object gilt. Ein beendeter Supervisor beweist nicht, dass alle produktiven Nachfahren bereits konvergiert sind. Dieser gemeinsame Authority-Pfad betrifft sowohl Scan- als auch Harmonization-Jobs.

**Erforderlich:** Den Job-Handle bis zur bestätigten Baum-Abwesenheit halten, `QueryInformationJobObject` bis `ActiveProcesses == 0` mit begrenzter Deadline ausführen und erst danach schließen und `stopped` publizieren. Query-, Close- und Wait-Fehler müssen gruppiert erhalten bleiben.

---

### P2 – Service-eigene Windows-Job-Handles lecken bei normalem Abschluss

Der beim Start erzeugte Job-Handle wird als Integer am kurzlebigen `_LocalScanJob` gehalten:

- Erzeugung/Rückgabe: `apps/web/scan_jobs.py:454-528`
- Zuweisung: `apps/web/scan_jobs.py:1310-1322`

Beim Harmonization-Start wird der dafür erzeugte `LocalScanJobService` nicht dauerhaft gehalten:

- `services/harmonization_worker.py:803-817`

Die automatische Schließung bei inaktivem Job greift nur, wenn derselbe Job mit seinem lokalen Handle später erneut abgefragt wird:

- `apps/web/scan_jobs.py:675-677`

Nach Verwerfen des Service-Objekts existiert kein Besitzer mehr, der diesen rohen Handle bei normalem Abschluss zuverlässig schließt. Neu erzeugte Recovery-Services öffnen lediglich einen weiteren Handle anhand des Namens.

**Erforderlich:** Explizites Service-/Handle-Lifecycle-Management oder Übergabe der alleinigen Lebensdauer an den Supervisor und anschließendes Schließen des lokalen Handles nach sicherer Registrierung und Freigabe.

---

### P2 – Hardware-Cleanup schließt Process- und Queue-Ressourcen nicht und kann Close-Fehler nicht erhalten

Die Cleanup-Routine führt `join()`, `terminate()`, `kill()` und erneutes `join()` aus:

- `services/hardware_modulation.py:306-347`

Sie ruft jedoch für keinen `multiprocessing.Process` `close()` auf. Auch die bei `services/hardware_modulation.py:360` erzeugte Queue wird weder geschlossen noch über `join_thread()` konvergiert. Der `finally`-Pfad endet unmittelbar nach `_converge_started_processes()`:

- `services/hardware_modulation.py:430-431`

Damit werden OS-/IPC-Ressourcen der wiederholten Pulse nicht deterministisch freigegeben, und mögliche Close-Fehler können entgegen dem geforderten Fehlererhalt überhaupt nicht gemeldet oder mit Primary/Join/Terminate/Kill-Fehlern gruppiert werden.

**Erforderlich:** Nach jeder Prozesskonvergenz alle Process-Handles und Queue-Endpunkte schließen; Close- und `join_thread()`-Fehler in kausaler Reihenfolge an bestehende Cleanup-Fehler anhängen.

## Abschluss

- **Zero-finding-Gate nicht erfüllt:** `P0=0, P1=3, P2=2, P3=0`.
- **Freeze vollständig gültig, keine Drift.**
- **Keine Tests oder Server gestartet; ausschließlich Source und Tests statisch geprüft.**
- **Keine Dateien erstellt oder verändert.**
- **Keine Ausführungsprobleme aufgetreten.**