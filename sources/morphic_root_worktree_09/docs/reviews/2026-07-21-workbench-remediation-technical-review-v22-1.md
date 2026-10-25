## Freeze-v22-Review

**Verdikt: REQUEST CHANGES**  
**Konfidenz: HOCH**  
**Befunde: P0=0 · P1=0 · P2=2 · P3=1**

### Befunde

| Prio | Befund | Evidenz |
|---|---|---|
| **P2** | Im POSIX-Signalpfad bleibt eine weitere konkurrierende Authority-/Close-Fehlerkombination unvollständig erhalten. Wenn `_token_process_pidfds()` nach bereits geöffneten Handles scheitert, ruft der äußere Fehlerpfad `_close_process_handles(handles)` auf, verwirft aber dessen Rückgabefehler. `_signal_posix_authority()` erhält somit nur den Primärfehler; Close-Fehler und mögliche Descriptor-Leaks werden nicht gruppiert. | `apps/web/scan_jobs.py:755-763`; Aufrufer `apps/web/scan_jobs.py:815-820` |
| **P2** | Der Windows-Startup-Zweig für `process_create_time is None` verwendet weiterhin sequenziell `process.kill()` und `process.wait()`. Ein Killfehler verhindert Wait vollständig und ersetzt den primären Identity-Fehler; ein Waitfehler ersetzt ihn ebenfalls. Die neue Gruppierung deckt nur Exceptions aus `_process_create_time()` und Windows-Job-Setupfehler ab. | `apps/web/scan_jobs.py:1177-1185`; korrekt gruppierter Vergleichspfad `apps/web/scan_jobs.py:1222-1237` |
| **P3** | Die Ownership-Regressionstests binden nicht die deklarierte vollständige Matrix. Es fehlen explizite Tests für blank/Whitespace-Owner sowie missing/blank/foreign/matching Owner am `/sync-trace`-Endpoint; matching Owner wird außerdem nicht für Status und Stop gebunden. Der gemeinsame Helper macht das aktuelle Verhalten plausibel korrekt, lässt aber Freeze-v22-spezifische Regressionen ungesichert. | `tests/test_web_scan_job_ownership.py:75-127`; keine entsprechenden Treffer für `sync-trace` oder blank Owner |

### Bestätigt

- Status, Stop, Sync und Results verwenden denselben scan-spezifischen Ownership-Helper.
- Fehlender, nicht-stringförmiger oder blanker `owner_id` wird mit 403 fail-closed behandelt.
- Explizit fremde Owner werden abgewiesen; passende Operator-/Workspace-Owner bleiben erlaubt.
- Recovery übernimmt fehlende/blanke Legacy-Owner unverändert; dadurch bleiben sie bis zu einer belegten Migration gesperrt.
- Der direkte POSIX Send-/Close-Doppelfehler wird jetzt geordnet als `BaseExceptionGroup` erhalten.
- Windows-Job-Setupfehler plus Kill- und Waitfehler werden im neuen Setup-Fehlerpfad geordnet gruppiert.
- Auth-Grenzen der sensiblen Scan-, Harmonisierung-, Report- und Privacy-Endpunkte sowie die übrigen v21 Produkt-/Security-Bereiche zeigten bei der statischen Nachprüfung keinen weiteren neuen Befund.

### Start-/Endbindung

- Branch/HEAD an beiden Grenzen: `operator-workbench-phase1` / `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- Status-Fingerprint an beiden Grenzen: `076ecdd63d2e12c036b790b82ed123e447671a0f568464e9bf0ae51003fa91a3`
- Status-Population an beiden Grenzen: **126**
- Kein beobachteter Branch-/HEAD-/Status-Drift.
- Manifest-SHA `221ae14e…`, 125 Einzelhashes und Aggregat `0442c289…` waren vorgegeben, konnten aber nicht nochmals unabhängig berechnet werden: Der kombinierte Verifikationsbefehl wurde wegen seiner temporären Dateien vom Tool-Gate abgewiesen. Daher keine Behauptung einer vollständigen unabhängigen Exact-Byte-Endprüfung.

### Ausführung

- Keine Tests, Projektimporte oder Produktprozesse ausgeführt.
- **Keine Dateien erstellt oder verändert.**
- APPROVE ist wegen **P2=2, P3=1** ausgeschlossen.