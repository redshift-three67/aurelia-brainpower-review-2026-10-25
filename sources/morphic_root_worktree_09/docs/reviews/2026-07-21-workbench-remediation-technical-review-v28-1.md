## Freeze-v28 – unabhängiges technisches Review 1

**Verdikt: REQUEST CHANGES**  
**Konfidenz: HOCH**  
**Befunde:** `P0=0 · P1=3 · P2=2 · P3=0`  
**Snapshot-Drift:** `0`

Die Freigabeschwelle `P0=P1=P2=P3=0` ist nicht erfüllt.

### Befundmatrix

| Prio | Befund | Evidenz |
|---|---|---|
| **P1** | **Der produktive Workbench-Hardware-Endpunkt umgeht weiterhin die EMF-Generation-Lease.** Er prüft nur `is_enabled()`, misst anschließend ohne gebundene Generation und publiziert ohne erneute Generation- oder Auth-Revalidierung. Ein Disable bzw. Credential-Widerruf während der Messung kann daher den bereits erzeugten Kalibrierungspayload nicht verwerfen. Zusätzlich misst `build_hardware_truth_snapshot()` bei fehlender expliziter Kalibrierung standardmäßig ohne Autorität. | `apps/web/workbench.py:51-71`; `apps/web/hardware_truth.py:44-46,65-76`; fehlende entsprechende Abdeckung in `tests/test_web_emf_security.py:39-151` |
| **P1** | **Whitespace-Ownership reserviert die globale Harmonisierungsautorität nicht fail-closed.** `bool("   ")` gilt als vollständig gebundener Owner; ebenso bestehen bestehende Whitespace-Werte die Owner-Vollständigkeitsprüfung. Ein aktiver Legacy-Job mit Whitespace-Tenant oder -Operator blockiert deshalb einen anders gebundenen Web-Start nicht. Der Test deckt nur `None` bei einem ohnehin global blockierenden `authority_ambiguous`-Status ab. | `services/harmonization_worker.py:762-777`; `tests/test_harmonization_worker_recovery.py:120-152` |
| **P1** | **Der Windows-Rollbackpfad bestätigt weiterhin nicht die Konvergenz des vollständigen Job Objects.** Nach `TerminateJobObject` wird höchstens auf den Supervisor gewartet; eine abschließende Abfrage von `ActiveProcesses == 0` fehlt. Der gehaltene Parent-Handle wird dabei ebenfalls nicht geschlossen. `_raise_start_failure()` behandelt diesen unvollständigen Rollback dennoch als erfolgreich. Das betrifft insbesondere Fehler nach der produktiven Freigabe. | `apps/web/scan_jobs.py:950-957,1084-1104,1348-1364`; die Rollback-Prüfung bestätigt nur einen Terminate-Aufruf: `tests/test_web_scan_jobs.py:250-296` |
| **P2** | **Die dauerhafte EMF-Generation ist bei fehlender oder beschädigter Authority-Datei nicht monoton.** `set_enabled()` setzt nach jedem Read-/Parse-Fehler die Generation erneut auf `1`. Nach Löschung oder Korruption kann ein erneutes Enable damit eine alte Generation wiederbeleben; eine zuvor mit Generation `1` begonnene Messung kann anschließend wieder als aktuell gelten. | `apps/web/emf_authority.py:48-70`; der Fail-closed-Test prüft nur das Lesen beschädigter Bytes, nicht Re-Enable/Generation-Reuse: `tests/test_emf_enable_authority.py:9-30` |
| **P2** | **Nicht alle Scan-WebSocket-Frames werden unmittelbar vor dem Senden erneut autorisiert.** Der „job not found“-Frame wird nach einem produktiven Store-Read ohne Post-read-Auth-/Ownerprüfung gesendet; der Timeout-Frame folgt nach dem letzten Sleep ebenfalls ohne erneute Prüfung. Ein zwischenzeitlicher Auth-Widerruf kann daher noch einen Frame mit der geschützten Job-ID erhalten. | `apps/web/scan_live.py:67-76,127-134`; die neuen Tests erfassen nur den regulären Update-Pfad: `tests/test_web_scan_live_security.py:111-167` |

### Positiv verifiziert

- Fehlende EMF-Authority-Bindung im Harmonisierungs-Worker ist nun fail-closed: `services/harmonization_worker.py:357-367`.
- Harmonisierungs-Messungen und die EMF-Profil-/WebSocket-Pfade prüfen ihre Generation vor und nach der Messung: `services/harmonization_worker.py:365-407`; `apps/web/emf.py:51-64,119-138`.
- Reguläre Scan-WebSocket-Updates revalidieren Authentifizierung und lesen die Ownership vor `send_json()` erneut: `apps/web/scan_live.py:95-120`.
- `None` und leere Owner sowie alle `authority_ambiguous`-Jobs blockieren Starts global; nur Whitespace bleibt offen: `services/harmonization_worker.py:765-777`.
- Der reguläre Windows-Stop fragt die Baumautorität bis `ActiveProcesses == 0` ab und gruppiert Terminate-, Wait-, Query- und Close-Fehler: `apps/web/scan_jobs.py:567-597,600-678,1396-1439`.
- Regulärer Windows-Start schließt den Parent-Handle nach Gate-Registrierung: `apps/web/scan_jobs.py:1348-1362`.
- POSIX-Signal- und sämtliche Descriptor-Close-Fehler werden gruppiert: `apps/web/scan_jobs.py:810-832,835-925`.
- Hardware-Cleanup schützt Event-, Join-, `is_alive`-, Terminate-, Kill-, Process-Close-, Queue-Close- und `join_thread`-Operationen: `services/hardware_modulation.py:306-368`.
- Whitespace-Pfade und Authorization-Header werden redigiert: `apps/web/scan_diagnostics.py:9-15,40-70`; `tests/test_web_scan_diagnostics.py:50-64`.

### Byte-Bindung und Drift

Start und Ende lieferten identische Ergebnisse:

| Merkmal | Ergebnis |
|---|---|
| Worktree | `C:/morphic_v1/.worktrees/operator-workbench-phase1` |
| Branch | `operator-workbench-phase1` |
| HEAD | `3271ff9366ab3fecb2a158913a0cc19ed6a06726` |
| Manifest-SHA-256 | `ecb804e4533b6344c9c2d2db742ba5dd9d1493c68526b223b348cfddc5bc3152` |
| Manifest-Einträge | `164` |
| Einzelhash-Abweichungen | `0` |
| Hashzeilen-Aggregat | `91eeb53e10ff29029690fedb61f169f227e223b376b6c6434228ca5c4e3b4c37` |
| Dirty Population | `165`, eindeutig `165` |
| Scope inklusive Manifest | `165` |
| Scope minus Dirty Population | `0` |
| Dirty Population minus Scope | `0` |
| Status-Fingerprint, kanonisches Newline-Porcelain | `7750511c75fe716534ba83789fe9b03082bf748bc74e1ce6e0eaaa63a661514b` |
| NUL-Porcelain-Fingerprint | `4e8419ba27e1f829c65a473becb68298588a38de4bb478d0f436445d3f9e8241` |
| Drift | **0** |

### Review-Hygiene

- Ausschließlich statische, read-only Quellcode-, Test- und Byteprüfung.
- Keine Tests, App-Imports, Dienste oder Netzwerkzugriffe ausgeführt.
- Die im Manifest genannten `1379 passed, 9 skipped` und `18 passed` wurden nur als gebundene Metadaten betrachtet.
- **Erstellte oder veränderte Dateien: keine.**
- Werkzeug- oder Scope-Probleme: keine.