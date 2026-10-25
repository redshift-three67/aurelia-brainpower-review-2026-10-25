# REQUEST CHANGES

**Konfidenz:** HOCH  
**Befundzählung:** `P0=0, P1=2, P2=0, P3=0`

## Befunde

| Priorität | Befund | Ort |
|---|---|---|
| P1 | `AccessDenied` ist nicht global fail-closed: unlesbare Mitglieder werden wie nicht vorhandene Mitglieder behandelt. Dadurch kann der Supervisor bzw. können andere Mitglieder signalisiert und ein unlesbarer produktiver Nachkomme anschließend fälschlich als abwesend betrachtet werden. | `apps/web/scan_jobs.py:287-297`, `apps/web/scan_jobs.py:398-415`, `apps/web/scan_jobs.py:419-444`, `apps/web/scan_jobs.py:750-804` |
| P1 | Ein normaler Prozess-Exit zwischen pidfd-Erfassung und Signalisierung kann die gesamte Signalrunde abbrechen. Ein `ProcessLookupError`/`ESRCH` bei einem Deskriptor verhindert, dass nachfolgende gültige pidfds signalisiert werden; Stop und Post-Release-Rollback konvergieren dann nicht zuverlässig. | `apps/web/scan_jobs.py:431-444`, `apps/web/scan_jobs.py:474-489`, `apps/web/scan_jobs.py:782-804` |

## Details

### P1 — `AccessDenied` kann überlebende Prozesse als abwesend klassifizieren

Sowohl `_process_group_alive()` als auch `_token_process_pidfds()` verschlucken `psutil.AccessDenied` zusammen mit transientem Prozessverschwinden:

- `_process_group_alive()` liefert danach gegebenenfalls `False`.
- `_token_process_pidfds()` überspringt den unlesbaren Prozess, kann aber andere Handles zurückgeben.
- `_signal_posix_authority()` signalisiert diese Handles trotzdem.
- Die nachfolgenden Abwesenheitsprüfungen verwenden erneut `_process_group_alive()` und können denselben unlesbaren Nachkommen übersehen.

Konkreter Gegenfall: Supervisor ist gültig und aktiv, ein produktiver Nachkomme derselben PGID verweigert `environ()`. Der Supervisor-pidfd wird trotzdem signalisiert; der Nachkomme wird aus Enumeration und Abwesenheitsprüfung ausgeschlossen. `stop()` kann anschließend `stopped` setzen, obwohl der Nachkomme weiterlebt. Das widerspricht dem expliziten v10-Vertrag „AccessDenied … failed/not-running und kein Signal“.

Der neue Test `tests/test_web_scan_jobs.py:367-383` prüft nur isoliert leere Helper-Ergebnisse und Deskriptorschließung. Er führt weder `stop()` noch Rollback aus und beweist nicht, dass bei einer gemischten Population überhaupt kein Signal gesendet wird.

**Erforderlich:** Enumeration als Tri-State/Ergebnisobjekt modellieren. Sobald bei einem zur Ziel-PGID gehörenden Kandidaten die Provenienz nicht gelesen werden kann, muss die gesamte Signalautorität vor dem ersten Signal fail-closed abbrechen. Stop und Rollback müssen diesen Zustand als fehlgeschlagen behandeln und dürfen keine erfolgreiche Abwesenheit ableiten. Adversarialen Stop-/Rollback-Test mit gültigem Supervisor, zugänglichem Mitglied und `AccessDenied`-Mitglied ergänzen.

### P1 — Ein veralteter pidfd bricht die Signalisierung verbleibender Autorität ab

`_signal_posix_authority()` erfasst zunächst alle Handles und sendet anschließend sequenziell:

```python
for descriptor in handles:
    sender(descriptor, sent_signal, None, 0)
```

Beendet sich der erste Prozess nach der Enumeration, liefert `pidfd_send_signal()` typischerweise `ESRCH`/`ProcessLookupError`. Die Schleife bricht ab; spätere, weiterhin lebende und tokenvalidierte Mitglieder erhalten kein Signal. `finally` schließt zwar alle Deskriptoren korrekt, stellt aber keine Signalkonvergenz her.

Im Rollback kann dies den ursprünglichen Startfehler maskieren und produktive Nachkommen zurücklassen. Im Stop führt es zu einem ungefangenen Fehler, ohne die verbleibenden Handles oder eine neue Enumeration abzuarbeiten. Der v10-Plan verlangt dagegen wiederholte, begrenzte Enumeration bis zur bestätigten Abwesenheit.

**Erforderlich:** Pro pidfd `ESRCH`/`ProcessLookupError` als bereits konvergiert behandeln und mit den übrigen Handles fortfahren. Andere Signalfehler müssen fail-closed aggregiert werden. Danach bounded re-enumerieren und erneut signalisieren, bis keine vollständig validierten Mitglieder mehr vorhanden sind oder ein expliziter Fehler/Timeout erreicht ist. Test ergänzen, bei dem das erste Handle vor dem Signal verschwindet und ein späteres weiterhin signalisiert wird.

## Mapping sämtlicher v9-Befunde

| v9-Befund | v10-Bewertung |
|---|---|
| Review 1 P2 / Review 2 P2: Token in Supervisor-`argv` | **Geschlossen:** `_build_gate_launch()` legt den Token ausschließlich in `MORPHIC_SCAN_GATE_TOKEN`; Gate-Command und produktiver Command enthalten ihn nicht (`apps/web/scan_jobs.py:307-330`). |
| Review 1 P2: gate-only Token gelangt in produktive Umgebung | **Geschlossen:** `os.environ.pop()` entfernt ihn vor `supervise()`; nur `MORPHIC_SCAN_GROUP_TOKEN` wird dem produktiven Kind injiziert (`services/scan_process_gate.py:153-157,189-192`). |
| Review 1 P2: tokenhaltiger State ohne owner-only Modi | **Geschlossen:** Parent `0700`, temporäre und veröffentlichte Datei `0600`; Tempdatei wird mit `O_EXCL` erstellt und atomar publiziert (`apps/web/durable_io.py:51-72`). |
| Review 1 P2: Trust Boundary und API-Ausschluss | **Geschlossen:** Same-account-Angreifer werden im v10-Plan ausdrücklich ausgeschlossen; der öffentliche Snapshot enthält weiterhin keinen Token (`apps/web/scan_jobs.py:896-914`). |
| Review 1 P3: fehlender `AccessDenied`-Vertrag | **Nicht geschlossen; zu P1 eskaliert:** Helper-Test vorhanden, produktiver Stop-/Rollback-Vertrag und globale „kein Signal“-Semantik fehlen. |
| Review 1 P3: unvollständiger Poll-Single-Flight-Nachweis | **Geschlossen:** gleicher Job-/Generationsschlüssel koalesziert; Timer wird vor Fetch entfernt und genau einmal ersetzt; alte Completion kann neue Authority nicht löschen (`apps/web/static/app.js:398-406,409-498`; `tests/browser/workbench.spec.js:645-702`). |
| Review 2 P1: TOCTOU vor numerischem `killpg()` | **Safety-Aspekt geschlossen:** pidfds werden vor Token-/PGID-Prüfung geöffnet; `killpg()` kommt im produktiven Modul nicht mehr vor. Fremde/recycelte PIDs können dadurch nicht auf eine neue Prozessidentität umgebunden signalisiert werden. Die oben beschriebenen Konvergenzfehler bleiben jedoch offen. |

## Weitere geprüfte Verträge

- pidfd wird vor PGID-/Tokenvalidierung geöffnet.
- Fremdtoken und wiederverwendete PID werden nicht über den stabilen Handle auf eine fremde Identität umgebunden.
- Supervisor erhält eine separate create-time-/PGID-Identitätsprüfung.
- Alle erfassten pidfds werden auch bei Ausnahmen geschlossen.
- Es existiert kein produktiver `killpg()`-Aufruf mehr.
- Browser-Polling verwendet eine gemeinsame Job-/Generationsautorität für manuelle und geplante Aufrufe.
- Alte Generationen dürfen weder UI noch neue In-flight-Autorität oder deren Timer löschen.
- Token ist nicht Bestandteil des öffentlichen Job-Snapshots/API-Responses.

## Freeze-/Driftbindung

**Startbindung erfolgreich:**

- Branch: `operator-workbench-phase1`
- HEAD: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- Manifest-SHA-256: `713857a5a092984539febefe81688402b57b24cd96a5bf89806cb337061bf1e9`
- Einzelhashes: `77/77 OK`
- Aggregat: `3dc9980ec125b21fc3a604d747735e59364108eded5c913b55e51f3cc1e1370e`
- Dirty-Population: `78`
- Scope plus Freeze-Manifest: exakt `78`

Die reservierte vollständige Endbindung wurde vom Toolzugriff blockiert und durfte laut Toolanweisung nicht wiederholt werden. Daher kann **keine abschließende Zero-Drift-Bestätigung** behauptet werden. Das ändert den Sachverhalt der beiden snapshotgebundenen P1-Befunde nicht; eine Genehmigung wäre bereits deshalb ausgeschlossen.

- Tests, Imports, Server, Netzwerk und Installationen: **nicht ausgeführt**
- Dateien erstellt oder verändert: **keine**