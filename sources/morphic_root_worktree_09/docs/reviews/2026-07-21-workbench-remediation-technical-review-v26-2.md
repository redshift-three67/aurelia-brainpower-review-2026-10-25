## Freeze-v26 – Zweites unabhängiges adversariales Review

**Verdikt: REQUEST CHANGES — NICHT APPROVE**  
**Konfidenz: hoch**  
**Befunde:** `P0=0 · P1=4 · P2=3 · P3=0`  
**Snapshot-Drift:** `0`

Die Freigabeschwelle `P0=P1=P2=P3=0` ist trotz vollständig driftfreier Freeze-Bindung nicht erfüllt.

### Befundmatrix

| Prio | Befund | Evidenz |
|---|---|---|
| **P1** | **Browser-Sitzungen sind an den Schlüsselwert, nicht an eine monotone Auth-Generation gebunden.** Das Token speichert lediglich `SHA256(API-Key)`. Nach `A → B → A` oder `A → unset → A` wird eine zuvor widerrufene Sitzung wieder gültig. HTTP und beide WebSockets übernehmen diese wiedererlangte Autorität. | `apps/web/security.py:45-69,83-92,95-117`; `apps/web/main.py:510-535`; `apps/web/emf.py:102-118`; `apps/web/scan_live.py:42-70`; unvollständiger Rotationstest: `tests/test_web_shell.py:1128-1154` |
| **P1** | **EMF-Disable ist weiterhin keine systemweite Messautorität.** Profil, EMF-WebSocket und Workbench-Kalibrierung respektieren `_emf_active`; der produktive Harmonization-Worker misst dagegen bei Zyklus 1 und danach jedem zehnten Zyklus immer ein EMF-Profil. Dieser Prozess besitzt auch keine Verbindung zur prozesslokalen `_emf_active`-Autorität. | `apps/web/emf.py:18-27,30-56,94-120`; `apps/web/workbench.py:52-72`; `services/harmonization_worker.py:321-328,343-348,634-640` |
| **P1** | **Harmonization-Stop besitzt weder POSIX-pidfd- noch Windows-Job-Object-Autorität und kann Ambiguität als Erfolg behandeln.** Persistiert werden nur numerische PID und Creation-Time. Lokal werden `multiprocessing.Process.terminate()/kill()`, nach Neustart `psutil.Process(pid).terminate()/kill()` verwendet. `PermissionError`/`AccessDenied` wird bei der Identitätsprüfung zu `False`; `_pid_is_alive()` kollabiert jedes `OSError` ebenfalls zu „nicht lebend“. Der Stop kann anschließend `stopped` publizieren, obwohl die physische Worker-Existenz nicht sicher ausgeschlossen wurde. | `services/harmonization_worker.py:124-134,782-817,819-842,845-873,876-893` |
| **P1** | **Keine physische Descendant-Konvergenz und keine sichere Restart-/Reservierungsautorität.** Der Worker erzeugt weitere Hardware-Prozesse, aber der API-Stop kontrolliert nur den unmittelbaren Worker. Stirbt dieser, können Nachfahren ohne persistenten Handle/Job/pidfd weiterlaufen. Recovery prüft ausschließlich die Worker-PID, markiert den Job `interrupted`, und die Owner-Reservierung betrachtet ihn danach nicht mehr als aktiv; ein neuer Job kann neben Überlebenden starten. | `services/hardware_modulation.py:289-305,342-365,397-423`; `services/harmonization_worker.py:226-234,738-746,801-842,896-917` |
| **P2** | **Prozess-Cleanup bewahrt kombinierte Fehler nicht und erfüllt den verlangten Failure-Grouping-Vertrag nicht.** Join-, Terminate-, Kill- und zweite Join-Fehler der Hardware-Nachfahren werden einzeln mit `except BaseException: pass` verworfen. Der direkte Worker-Stop gruppiert ebenfalls weder Primär- noch Cleanup-/Wait-Fehler und bricht bei der ersten Exception ab. Dadurch fehlen kausal geordnete Fehler und eine belastbare Diagnose der Konvergenz. | `services/hardware_modulation.py:305-339`; `services/harmonization_worker.py:801-842` |
| **P2** | **Der Scan-Start veröffentlicht weiterhin sensible Prozess-, Pfad- und Klientendaten in einem erfolgreichen HTTP-Payload.** `Phase1ScanJobResponse` erbt `command`, `focus`, `image_path` und `notes`; der Befehl enthält Namen, Geburtsdaten/-ort, Fokus, Interpreter- und Exportpfad. Zusätzlich können `parallel_export_plan` und `parallel_export_client_id` zurückgegeben werden. Damit ist der v26-Anspruch, sensible Prozess-/Ressourcenfelder aus erfolgreichen HTTP-Payloads zu entfernen, nicht vollständig erfüllt. | `apps/web/contracts.py:190-214`; `apps/web/launcher.py:24-55,61-95`; `apps/web/main.py:711-795` |
| **P2** | **Die sichtbare Scan-Logdiagnostik ist nach der Redaktion funktionslos.** Der Store liest weiterhin `stdout_tail` und `stderr_tail`, aber `_scan_job_safe_view()` entfernt beide. Das Frontend bezieht seine Loganzeige ausschließlich aus genau diesen nun fehlenden Feldern und setzt sie deshalb auf leer. Auch der WebSocket erwartet ein nicht mehr geliefertes `logs`-Feld. | `apps/web/scan_jobs.py:1426-1439,1489-1506`; `apps/web/main.py:241-247,802-814`; `apps/web/static/app.js:410-435`; `apps/web/scan_live.py:83-99` |

## Zusätzlich statisch verifiziert

- `/api/status` verwendet jetzt konfigurierte Authentifizierung: `apps/web/main.py:504-508`.
- `A → B` invalidiert Sitzungen unmittelbar; nur Rollback/Reaktivierung desselben Schlüsselwerts bleibt fehlerhaft.
- No-Key → konfigurierte Authentifizierung wird in den WebSocket-Schleifen vor weiterer Messung bzw. Store-Ausgabe erneut geprüft.
- EMF-Profil, EMF-WebSocket und Workbench-Kalibrierung respektieren den lokalen Enable/Disable-Zustand.
- Scan-Status, Stop, Results, Sync-Trace und Run-Trace erzwingen Authentifizierung und strikte Ownership; Status-/Stop-Envelopes sind redigiert: `apps/web/main.py:797-889`.
- Harmonization-Status und -Stop prüfen Tenant und Operator fail-closed, einschließlich `None`, leer, Whitespace und Fremdwerten: `apps/web/main.py:663-698`; `tests/test_web_shell.py:867-933`.
- Harmonization-Polling besitzt nun einen Promise-Identity-Single-Flight-Guard: `apps/web/static/app.js:697-705`.
- Reset blockiert parallele Mutationen und führt serverseitige Stops vor der Generationserhöhung aus: `apps/web/static/app.js:868-920`.
- Hardware-Exceptions werden in den geprüften öffentlichen Hardware-Payloads generisch behandelt: `apps/web/hardware_truth.py:44-62`; `apps/web/main.py:112-130,556-565`.
- Beim statischen Produkt-, Datenschutz-, Security- und Accessibility-Pass wurden keine zusätzlichen P0/P1-Befunde außerhalb der Matrix festgestellt.

## Exakte Freeze-Bindung

Start und Ende waren identisch:

| Merkmal | Start | Ende |
|---|---|---|
| Worktree | `C:/morphic_v1/.worktrees/operator-workbench-phase1` | identisch |
| Branch | `operator-workbench-phase1` | identisch |
| HEAD | `3271ff9366ab3fecb2a158913a0cc19ed6a06726` | identisch |
| Manifest-SHA | `b978a8a028c4e7da65d276cbe350a8d0b2d30b5a00c213afab6fdb0dc632100c` | identisch |
| Hash-Einträge | `151`, alle `sha256sum -c` erfolgreich | identisch |
| Aggregate, as-listed | `3c9f0835e7644394a1c4a3d10d470ffce16d7fe7d391586777c29d0d3122140c` | identisch |
| Dirty-Population | `152` eindeutig | `152` eindeutig |
| Erwartete Population | `151 + Manifest = 152` | identisch |
| Bidirektionale Scope-Gleichheit | wahr; fehlend `0`, zusätzlich `0` | identisch |
| NUL-Status-Fingerprint | `4ee27890788a1d8f96cb857f528a7b2710198ff87b1edc42381afde1daa0cd19` | identisch |

**Drift: 0.**

## Hygiene und Einschränkungen

- Strikt read-only: keine Tests, Imports, Server, Netzwerkzugriffe oder Produktprozesse.
- Die im Manifest genannten Gates `1368/9 skipped`, `121` und Playwright `18` wurden wegen des Ausführungsverbots nicht erneut ausgeführt; geprüft wurde ihre Manifestbindung, nicht ihre Laufzeitwiederholung.
- **Erstellte oder geänderte Dateien:** keine.
- **Probleme während des Reviews:** keine Werkzeug- oder Scope-Blocker.