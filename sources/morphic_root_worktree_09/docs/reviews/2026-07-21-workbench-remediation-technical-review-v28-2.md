## Technisches Review Freeze v28

**Verdikt:** **REQUEST CHANGES**  
**Konfidenz:** **HOCH**

### Schweregrad

| P0 | P1 | P2 | P3 |
|---:|---:|---:|---:|
| 0 | 5 | 1 | 0 |

Die Freigabebedingung `P0=P1=P2=P3=0` ist damit nicht erfüllt.

### Befunde

| Prio | Befund | Evidenz |
|---|---|---|
| **P1** | **Die EMF-Generation-Lease ist nicht über alle produktiven Oberflächen durchgesetzt.** Der CLI-Workflow misst direkt ohne Authority/Generation. Der Web-Hardware-Endpunkt verwendet nur ein anfälliges `is_enabled()`-Check-then-measure und validiert die Generation vor der Antwort nicht erneut. Ein paralleles Disable kann daher nach dem Check noch eine Messung starten bzw. deren Ergebnis veröffentlichen. | `apps/cli/workflow/step05_emf.py:18-24`; `apps/web/workbench.py:51-70`; direkte Messfunktion: `apps/web/hardware_truth.py:44-46` |
| **P1** | **Die EMF-Generation ist nach Verlust oder Beschädigung der Authority nicht monoton.** `set_enabled()` setzt bei fehlender, unlesbarer oder ungültiger Datei die Generation auf `1`. Eine ältere Messung mit Generation 1 kann nach Löschen/Beschädigen und Reaktivieren wieder als aktuell gelten – ein ABA-/Revival-Fenster. | `apps/web/emf_authority.py:48-60`; `apps/web/emf_authority.py:62-74` |
| **P1** | **Windows-Start-Rollback bestätigt keine vollständige Prozessbaum-Konvergenz und schließt den gehaltenen Job-Handle nicht.** Der Rollback ruft lediglich `TerminateJobObject` und optional `wait()` auf den Supervisor auf. Anders als der normale Stop prüft er nicht bis `ActiveProcesses == 0`, sammelt Query/Wait/Close-Fehler nicht vollständig und lässt `windows_job_handle` auf diesem Pfad offen. | unvollständiger Rollback: `apps/web/scan_jobs.py:950-957`; vollständigerer Stop-Konvergenzpfad: `apps/web/scan_jobs.py:567-597`; produktiver Aufruf: `apps/web/scan_jobs.py:1084-1103`; schwacher Rollback-Test: `tests/test_web_scan_jobs.py:250-296` |
| **P1** | **POSIX-Konvergenz bricht beim ersten TERM-/Authority-Fehler ab.** `_signal_posix_authority()` gruppiert zwar interne Send/Close-Fehler, aber `_converge_posix_authority()` akkumuliert Fehler nicht und versucht nach einem TERM-Fehler weder KILL-Runden noch abschließende Konvergenz. Auch Fehler in den wiederholten Aktivitätsabfragen überspringen die restliche Bereinigung. | `apps/web/scan_jobs.py:835-925`; `apps/web/scan_jobs.py:935-947`; für dieses Fortsetzungs-/Gruppierungsszenario keine statische Testdeckung gefunden |
| **P1** | **Terminalstatus kann durch ein Poll/Authority-TOCTOU dauerhaft falsch als `failed` gespeichert werden.** `returncode` wird einmalig gelesen. Endet der Prozess danach erfolgreich, während die Authority-Abfrage bereits „nicht aktiv“ liefert, bleibt der gecachte Wert `None`; der Code wählt `failed` statt `completed` und persistiert diesen Status anschließend als `forced_status`. Das betrifft insbesondere Windows zwischen `poll()` und `ActiveProcesses == 0`. | `apps/web/scan_jobs.py:1444-1473`; dauerhafte Festschreibung: `apps/web/scan_jobs.py:1534-1537` |
| **P2** | **Diagnostik-Redaktion deckt Cookies und mehrere Credential-Formen nicht ab; der Test enthält eine vakuose Assertion.** Beispielsweise bleiben `Cookie: morphic_session=...` und Bezeichner wie `access_token=...` unredigiert. Der Authorization-Test speist bereits `***` ein und prüft anschließend, dass ein nie eingegebener Wert nicht vorkommt. | `apps/web/scan_diagnostics.py:9-15`; `apps/web/scan_diagnostics.py:40-70`; `tests/test_web_scan_diagnostics.py:50-64` |

### Positiv statisch bestätigt

- Scan-WebSocket authentifiziert vor dem ersten Store-Zugriff und prüft Auth sowie Ownership erneut unmittelbar vor dem Senden: `apps/web/scan_live.py:43-60`, `65-120`.
- EMF-WebSocket prüft Auth und EMF-Generation nach der Messung erneut: `apps/web/emf.py:102-138`.
- Unbekannte bzw. unvollständige Harmonization-Owner reservieren die Ressource global: `services/harmonization_worker.py:762-781`.
- Hardware-Helfer versucht `Process.close()`, `Queue.close()` und `Queue.join_thread()` und bewahrt aktive Primärfehler in einer Gruppe: `services/hardware_modulation.py:306-368`.
- Der reguläre Windows-Stop fragt `ActiveProcesses` bis zur Konvergenz ab und sammelt Terminate/Wait/Query/Close-Fehler: `apps/web/scan_jobs.py:567-678`.

## Freeze-Bindung und Drift

Start- und Endprüfung waren identisch:

- Branch: `operator-workbench-phase1`
- HEAD: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- Manifest-SHA-256: `ecb804e4533b6344c9c2d2db742ba5dd9d1493c68526b223b348cfddc5bc3152`
- Manifest-Einträge: **164**, Abweichungen: **0**
- Hash-Line-Aggregat: `91eeb53e10ff29029690fedb61f169f227e223b376b6c6434228ca5c4e3b4c37`
- Population: **165**, fehlend: **0**, zusätzlich: **0**
- Status-Fingerprint, Rezept `git status --porcelain=v1 --untracked-files=all` mit LF: `7750511c75fe716534ba83789fe9b03082bf748bc74e1ce6e0eaaa63a661514b`
- **Drift: 0**

### Coverage-Grenzen

- Strikt statische, read-only Prüfung.
- Keine Tests, App-Imports, Netzwerkzugriffe oder produktiven Prozesse ausgeführt.
- Windows-API- und POSIX-pidfd-Verhalten wurde konzeptionell anhand der Plattformzweige und statischen Tests geprüft, nicht auf beiden Betriebssystemen ausgeführt.
- Keine Dateien erstellt oder verändert; keine Repo-Artefakte erzeugt.