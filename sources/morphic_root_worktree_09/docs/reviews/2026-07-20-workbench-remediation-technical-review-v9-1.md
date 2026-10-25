# REQUEST CHANGES

**Konfidenz:** HOCH  
**Befundzählung:** `P0=0, P1=0, P2=1, P3=2`

## Befunde

### P2 — POSIX-Provenienz-Token ist nicht vertraulich gespeichert oder übergeben

- Der kryptographisch zufällige Token wird direkt in die Supervisor-Kommandozeile aufgenommen: `apps/web/scan_jobs.py:584-595`.
- Er wird zusätzlich im Job-State im Klartext persistiert: `apps/web/scan_jobs.py:471-504`.
- `durable_write_bytes()` erstellt Verzeichnis und Temporärdatei ohne explizite POSIX-Rechte `0700`/`0600`: `apps/web/durable_io.py:51-63`. Die effektiven Rechte hängen damit vom Prozess-`umask` ab.
- Der Gate-Prozess übernimmt den Token aus `argv` und stellt ihn anschließend in die produktive Umgebung: `services/scan_process_gate.py:143-156,177-190`.
- Positiv: Der Token fehlt vollständig in der öffentlichen Job-Snapshot/API-Antwort (`apps/web/scan_jobs.py:818-836`); dies wird durch `tests/test_web_scan_jobs.py:459-465` geprüft.
- Auswirkung: Die Zufälligkeit verhindert zufällige PGID-Kollisionen, bildet aber keine belastbare geheime Provenienz, solange der Wert über Prozesskommandozeile beziehungsweise potenziell breit lesbaren State offengelegt wird. Das widerspricht der Freeze-v9-Aussage, der Token werde „nur“ in die produktive Umgebung injiziert.

**Erforderlich:** Token nicht über `argv` transportieren; State-Verzeichnis und tokenhaltige Dateien auf POSIX explizit owner-only absichern und dies adversarial testen. Den lokalen Trust-Boundary ausdrücklich dokumentieren, falls gleichberechtigte Prozesse desselben OS-Accounts außerhalb des Schutzmodells liegen.

### P3 — Kein adversarialer `process.environ()`-AccessDenied-Vertrag

`_process_group_alive()` behandelt `PermissionError`, `psutil.AccessDenied` über `psutil.Error` und weitere Lesefehler fail-closed (`apps/web/scan_jobs.py:279-297`). Es fehlt jedoch ein Test, der:

1. eine numerisch passende PGID liefert,
2. bei `process.environ()` `psutil.AccessDenied` auslöst,
3. `running` ausschließt und
4. beweist, dass `stop()` kein `killpg()` ausführt.

Die vorhandenen Fremdgruppen-Tests ersetzen die Provenienzprüfung vollständig durch einen gemockten `False`-Rückgabewert (`tests/test_web_scan_jobs.py:333-357`) und üben die reale Fehlergrenze daher nicht aus.

### P3 — Poll-Single-Flight nicht vollständig adversarial bewiesen

Die Implementierung besitzt einen identitätsgeschützten In-flight-Guard und einen sicheren Reset (`apps/web/static/app.js:398-406,409-498,900-908`). Der Browsertest `tests/browser/workbench.spec.js:625-641` beweist jedoch nur, dass zwei schnelle manuelle Klicks insgesamt einen zusätzlichen Fetch erzeugen. Nicht bewiesen werden die Freeze-v9-Verträge:

- manueller und bereits terminierter/scheduled Poll teilen dieselbe Autorität,
- genau ein Nachfolgetimer wird angelegt,
- ein Generation-/Job-Wechsel während eines alten Requests wird nicht blockiert,
- die alte Promise darf die neue In-flight-Autorität nicht löschen.

## Mapping sämtlicher v8-Befunde

| v8-Befund | v9-Bewertung |
|---|---|
| Review 1 / Review 2: fremde oder wiederverwendete POSIX-PGID wird übernommen | **Teilweise geschlossen:** PGID plus zufälliger Environment-Token verhindert zufällige Wiederverwendung und `AccessDenied` schließt statisch sicher. Token-Vertraulichkeit und adversarialer AccessDenied-Nachweis bleiben offen. |
| Post-Release-Snapshotfehler lässt Prozessgruppe weiterlaufen | **Geschlossen:** gemeinsamer Rollback ab `apps/web/scan_jobs.py:645-664`; POSIX-Gruppenkonvergenz und Windows-Tree-Abbruch in `:357-404`; produktiver Nachkommentest in `tests/test_web_scan_jobs.py:693-730`. |
| Hardware-Cleanup bestätigt Survivor-Abwesenheit nicht | **Geschlossen:** Cleanup-Operationen werden pro Kind isoliert, Survivor werden erneut geprüft und eskaliert (`services/hardware_modulation.py:305-339,397-423`); adversarialer Test `tests/test_harmonization_worker_pulse_pause_execution.py:281-318`. |
| Manueller Scan-Retry ist nicht single-flight | **Implementierung geschlossen, Nachweis teilweise:** Guard und generationssicheres Freigeben sind vorhanden; die geforderten Scheduled-/Timer-/Generation-Adversarialfälle fehlen. |

## Freeze-/Driftbindung

| Prüfung | Start | Ende |
|---|---:|---:|
| Branch | `operator-workbench-phase1` | identisch |
| HEAD | `3271ff9366ab3fecb2a158913a0cc19ed6a06726` | identisch |
| Freeze-v9 SHA-256 | `3c30e1b4927e91aeffbc23067fa0bfc490e549d4e52695d08faaf8035e292969` | identisch |
| Manifest-Einträge | 73 | 73 |
| Einzelhashes | 73/73 OK | 73/73 OK |
| LF-Aggregat | `886ff1f9513234799619592ee1cbdb464d34d9a9c200dae074df9c418d80859a` | identisch |
| Dirty-Population | 74 | 74 |
| Dirty minus Scope+Manifest | 0 | 0 |
| Scope+Manifest minus Dirty | 0 | 0 |
| Status-SHA-256 | `9fa222442813522d297e1efd7f5d534453d8ea3bed5a916ca4fe4b811b1bd702` | identisch |
| Drift | keine | keine |

- Alle v8→v9 geänderten Produkt-, Test- und Planartefakte sowie die relevanten Prozess-, Persistenz-, API- und Frontend-Grenzen wurden statisch geprüft.
- Tests, Imports, Server, Netzwerk und Installationen wurden entsprechend der Vorgabe **nicht ausgeführt**.
- Dateien erstellt, geändert oder gelöscht: **keine**.
- Technisches Problem: Ein erster Abschlussbindungs-Parserlauf hatte einen reinen Python-Quotingfehler; der unmittelbar wiederholte vollständige Bindungslauf war erfolgreich und zeigte null Drift.