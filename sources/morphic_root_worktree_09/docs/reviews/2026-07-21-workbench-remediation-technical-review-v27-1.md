## Freeze-v27 – unabhängiges technisches Review 1

**Verdikt: REQUEST CHANGES**  
**Konfidenz: HOCH**  
**Befunde:** `P0=0 · P1=2 · P2=3 · P3=0`  
**Snapshot-Drift:** `0`

Die verlangte Freigabeschwelle `P0=P1=P2=P3=0` ist nicht erfüllt.

### Befundmatrix

| Prio | Befund | Evidenz |
|---|---|---|
| **P1** | **Die dauerhafte EMF-Autorität ist weiterhin nicht systemweit default-off.** `capture_realtime_context()` prüft die Autorität nur, wenn `_emf_authority_path` vorhanden ist; fehlt das Feld, wird direkt gemessen. Die produktiven CLI- und Workflow-Aufrufer starten Harmonisierungen ohne diesen Pfad. Damit führen diese Jobs beim ersten und danach jedem zehnten Zyklus EMF-Messungen aus, obwohl keine Aktivierung vorliegt. | `services/harmonization_worker.py:357-367,658-660`; `apps/cli/commands/harmonize.py:23-37`; `apps/cli/workflow/step12_harmonize.py:35-46` |
| **P1** | **Ownerlose bzw. nicht eindeutig zuordenbare ambivalente Jobs reservieren die Startautorität nicht global fail-closed.** Aktive und `authority_ambiguous` Jobs werden zwar gesammelt, die Startblockade filtert aber ausschließlich auf exakte Tenant-/Operator-Gleichheit. Ein ambivalenter Legacy-/CLI-Job mit `None` oder leerer Ownership blockiert daher keinen Web-Start mit konkretem Owner; ein zweiter Hardware-Prozessbaum kann neben einer nicht sicher kontrollierbaren Autorität starten. | `services/harmonization_worker.py:131-145,235-248,757-765,918-925` |
| **P2** | **Hardware-Cleanup kann den Primärfehler weiterhin ersetzen und Cleanup vorzeitig abbrechen.** `stop_event.clear()`, `pulse_event.set()` und mehrere `is_alive()`-Abfragen liegen außerhalb geschützter Fehlerakkumulation. Wirft eine dieser Operationen während eines bereits aktiven Primärfehlers, gehen der Primärfehler und bereits gesammelte Cleanup-Fehler verloren; weitere Prozesse werden gegebenenfalls nicht terminiert. | `services/hardware_modulation.py:306-347` |
| **P2** | **Der POSIX-pidfd-Pfad bewahrt mehrere reine Close-Fehler nicht vollständig.** Sind mehrere Descriptor-Close-Operationen fehlerhaft, aber kein anderer Primärfehler aktiv, wird nur der erste Fehler als `RuntimeError` weitergegeben statt aller Fehler in geordneter `BaseExceptionGroup`-Form. | `apps/web/scan_jobs.py:810-820,904-916` |
| **P2** | **Die Logredaktion deckt Pfade mit Leerzeichen und gängige unbeschriftete Credential-Formate nicht vollständig ab.** Beide Pfadregulärausdrücke enden am ersten Whitespace; beispielsweise bleibt von `C:\Users\Klaus Mustermann\report.json` ein identifizierbarer Suffix stehen. `Authorization: Bearer …` wird von der Secret-Regel ebenfalls nicht erfasst. | `apps/web/scan_diagnostics.py:9-14,51-60`; unvollständige Testmatrix: `tests/test_web_scan_diagnostics.py:10-40` |

### Positiv verifiziert

- Scan-Start verwendet den minimierten `Phase1ScanStartResponse`; Command, Klientendaten und Exportpfade werden nicht in der erfolgreichen HTTP-Antwort serialisiert: `apps/web/contracts.py:217-224`, `apps/web/main.py:731-815`.
- HTTP- und Scan-WebSocket-Pfade erzwingen konfigurierte Authentifizierung sowie strikte Job-Ownership vor Datenausgabe: `apps/web/main.py:817-907`, `apps/web/scan_live.py:43-105`.
- Browser-Sitzungen verwenden eine beobachtete monotone Generation; Rollback und Disable/Re-enable werden bei beobachteten Übergängen widerrufen: `apps/web/security.py:45-81,95-108`.
- Harmonisierung wird tatsächlich über `LocalScanJobService` und denselben Gate-Code gestartet: `services/harmonization_worker.py:44-49,796-825`.
- Startfreigabe erfolgt erst nach persistierter Scan-Autorität; POSIX verwendet pidfds und wiederholte Token-Revalidierung, Windows tokenabgeleitete benannte Job Objects mit in den Gate-Prozess dupliziertem Handle: `apps/web/scan_jobs.py:439-528,681-938,1205-1352`.
- Harmonization-Stop publiziert `stopped` erst nach Rückkehr der Baumkonvergenz; Fehler persistieren `authority_ambiguous`: `services/harmonization_worker.py:830-891`.
- Der Frontend-Vertrag konsumiert die neue `diagnostics`-Projektion statt der entfernten Roh-Streams: `apps/web/static/app.js:433-438`.

### Freeze-Bindung

Start und Ende waren identisch:

| Merkmal | Reproduziertes Ergebnis |
|---|---|
| Worktree | `C:/morphic_v1/.worktrees/operator-workbench-phase1` |
| Branch | `operator-workbench-phase1` |
| HEAD | `3271ff9366ab3fecb2a158913a0cc19ed6a06726` |
| Manifest-SHA-256 | `067a54316eee54ee313183192f29a2c7aae548227cc781df4c71e7b94553e47e` |
| Hashzeilen | `160` |
| Einzelhash-Abweichungen | `0` |
| Hashzeilen-Aggregat | `65417cc985d105821ee725998ca503448901232335ad7cbba8a3c51651086511` |
| Dirty Population | `161`, eindeutig `161` |
| Scope/Population-Symmetrie | exakt gleich; fehlend `0`, zusätzlich `0` |
| Status-Fingerprint | `7a6d29285360fa1ddeaf04d9e574cfbc8eabbfd9bf48b840c6cdba5e520e1633` |
| Drift | **0** |

### Testevidenz und Grenzen

- Tests wurden entsprechend dem Auftrag **nicht ausgeführt**; die im Manifest behaupteten `1376 passed, 9 skipped` und Playwright `18 passed` wurden nur als gebundene Metadaten betrachtet.
- Es fehlt statische Testevidenz für:
  - Harmonisierungs-EMF bei vollständig fehlendem Authority-Pfad;
  - ownerlose/blanke ambivalente Jobs gegenüber einem anders gebundenen Start;
  - echtes End-to-End-Restart/Stop eines Harmonisierungs-Workers mit Hardware-Nachfahren über den gemeinsamen Gate;
  - Fehler von `Event.clear/set` und `Process.is_alive()` während eines Primärfehlers;
  - mehrere gleichzeitige pidfd-Close-Fehler ohne Primärfehler;
  - Pfade mit Leerzeichen und `Authorization: Bearer` in der Diagnostikredaktion.

### Review-Hygiene

- Strikt read-only; keine Tests, Imports, Dienste, Netzwerkzugriffe oder Repository-Artefakte.
- **Erstellte oder veränderte Dateien: keine.**
- Werkzeug- oder Scope-Blocker: keine.