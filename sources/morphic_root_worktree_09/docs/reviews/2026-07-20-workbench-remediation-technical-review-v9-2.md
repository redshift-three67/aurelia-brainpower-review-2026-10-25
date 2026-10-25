# REQUEST CHANGES

**Konfidenz:** HOCH  
**Befundzählung:** `P0=0, P1=1, P2=1, P3=0`

## Findings

| Priorität | Befund | Ort |
|---|---|---|
| P1 | Zwischen tokengebundener Provenienzprüfung und `killpg()` besteht weiterhin ein TOCTOU-Fenster. Eine nach der Prüfung beendete legitime Gruppe kann numerisch wiederverwendet werden; die anschließend signalisierte Gruppe wird an der finalen Signalgrenze nicht erneut auf Token-Provenienz geprüft. | `apps/web/scan_jobs.py:371-385`, `apps/web/scan_jobs.py:676-711` |
| P2 | Der neue Provenienz-Token wird entgegen dem dokumentierten Vertrag „nur im produktiven Environment“ als `--token` in der Gate-Kommandozeile veröffentlicht. Die Tests prüfen lediglich, dass er nicht im API-Snapshot erscheint, nicht seine Abwesenheit aus `argv`. | `apps/web/scan_jobs.py:584-598`, `services/scan_process_gate.py:177-190`, `tests/test_web_scan_jobs.py:458-465` |

### P1 — Keine Provenienzprüfung an der finalen `killpg()`-Grenze

`stop()` ermittelt `group_active` einmal in `apps/web/scan_jobs.py:676-677`. Danach erfolgen weitere Prüfungen und Verzweigungen, bevor Zeile 711 die numerische PGID signalisiert. Endet die tokenführende Gruppe dazwischen und wird die PGID wiederverwendet, kann `killpg()` die neue fremde Gruppe treffen. Derselbe Abstand besteht im Rollback zwischen `apps/web/scan_jobs.py:371-374` und `:385`.

Der neue Fremdgruppen-Test modelliert dieses Rennen nicht: `tests/test_web_scan_jobs.py:333-357` ersetzt `_process_group_alive()` lediglich konstant durch `False`; er beweist weder Tokenprüfung mit einer realen/falschen Umgebung noch einen Wechsel von „legitim“ zu „fremd“ unmittelbar vor `killpg()`.

**Erforderlich:** Provenienz an der letzten Signalgrenze erneut und fail-closed validieren beziehungsweise eine Signalautorität verwenden, die nicht allein auf einer wiederverwendbaren numerischen PGID beruht. Ein adversarialer Test muss die Gruppe nach der ersten positiven Prüfung durch eine fremde Gruppe ersetzen und beweisen, dass `killpg()` nicht aufgerufen wird.

### P2 — Token in Prozess-`argv`

Der zufällige Token wird in `apps/web/scan_jobs.py:594-595` als Kommandozeilenargument übergeben und in `services/scan_process_gate.py:182` eingelesen. Damit kann er in Prozesslisten, Diagnoseaufnahmen oder Command-Line-Telemetrie erscheinen. Das widerspricht dem Freeze-v9-Vertrag, nach dem er ausschließlich in die produktive Prozessumgebung injiziert wird.

**Erforderlich:** Token über einen nicht in `argv` sichtbaren, restriktiven Kanal an das Gate übergeben und mit einem Test sowohl API-/Persistenzgrenzen als auch Gate-Kommandozeile prüfen.

## Prüfung der vier v8-Befunde

- **POSIX-Provenienz:** Tokenbindung schließt die einfache numerische Übernahme, aber wegen des finalen TOCTOU-Fensters nicht vollständig geschlossen.
- **Post-Release-Rollback:** Vollständige Gruppen-/Windows-Baum-Konvergenz und Abwesenheitsprüfung sind grundsätzlich vorhanden; keine weitere Regression außer derselben finalen Signalrace gefunden.
- **Hardware-Convergence:** Cleanup läuft über einzelne Join-/Terminate-/Kill-Ausnahmen hinweg und eskaliert verbleibende Prozesse mit `HardwareModulationOverrunError`; geschlossen.
- **Scan-Polling:** Job-/Generation-keyed Single-Flight, stale-authority-Vergleich und Timerkontrolle schließen den v8-Reentrancy-Befund.

Ohne weitere Befunde geprüft: Auth/Authz, Session-Cookie und Secrets, Owner-/Tenant-/Reportbindung, Rate-Limit-Buckets, New Case und Generation-/Stale-Guards, in-flight Promises/Timer, dauerhafte Stores, tokenlose Legacy-State-Recovery (fail-closed ohne Supervisor), Windows-Job-Pfad, ARIA-Verträge und Browserverhalten.

## Freeze-/Driftbindung

| Prüfung | Start | Ende |
|---|---:|---:|
| Branch | `operator-workbench-phase1` | identisch |
| HEAD | `3271ff9366ab3fecb2a158913a0cc19ed6a06726` | identisch |
| Manifest-SHA-256 | `3c30e1b4927e91aeffbc23067fa0bfc490e549d4e52695d08faaf8035e292969` | identisch |
| Einzelhashes | `73/73 OK` | `73/73 OK` |
| LF-Aggregat | `886ff1f9513234799619592ee1cbdb464d34d9a9c200dae074df9c418d80859a` | identisch |
| Dirty-Population | 74 | 74 |
| Scope + Freeze | 74 | 74 |
| Dirty minus Scope | 0 | 0 |
| Scope minus Dirty | 0 | 0 |
| Drift | keine | keine |

- Tests, Imports, Server, Netzwerk und Installationen: **nicht ausgeführt**
- Dateien erstellt, verändert oder gelöscht: **keine**
- Probleme: nur harmlose Git-Hinweise zu zukünftiger LF/CRLF-Konvertierung