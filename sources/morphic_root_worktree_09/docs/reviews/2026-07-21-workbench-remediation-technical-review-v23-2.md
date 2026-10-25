## Freeze-v23 Review

**Verdikt: REQUEST CHANGES — NICHT APPROVE**  
**Befunde:** P0=0, **P1=2**, P2=0, P3=0

### P1-Befunde

1. **WebSocket-Berechtigung wird nach `accept()` nicht erneut geprüft**  
   **Ort:** `apps/web/scan_live.py:42-65,72-99`  
   API-Key beziehungsweise Browser-Session und Ownership werden nur vor dem Accept geprüft. Danach streamt die Verbindung bis zu zehn Minuten weiter, selbst wenn:
   - die Session über Logout widerrufen wird,
   - der API-Key rotiert oder deaktiviert wird,
   - die aktuelle Snapshot-Ownership nicht mehr passt.

   Dadurch können private Statusdaten und Logs nach Entzug der Berechtigung weiter offengelegt werden. Vor jedem Snapshot-Versand müssen aktuelle Authentifizierung und Ownership erneut fail-closed geprüft werden; bei Widerruf mit `4401`, bei Ownership-Verlust mit `4403` schließen. Die vorhandenen Tests prüfen nur die Prä-Accept-Fälle.

2. **Konfigurierte HTTP-Authentifizierung schützt detaillierte Systemdiagnose nicht**  
   **Ort:** `apps/web/main.py:531-552`, `apps/web/workbench.py:48-60`; Datenumfang in `core/db/health.py:240-253`  
   `/api/health`, `/api/hardware/status`, `/api/sources` und `/api/workbench/hardware` bleiben auch bei gesetztem `MORPHIC_API_KEY` unauthentifiziert. Insbesondere `/api/health` veröffentlicht absolute Projekt-/Datenbank-/Python-/Modulpfade, Konfigurationspfade, Versionen, Tabellenbestände und Fehlerdetails. Das umgeht die ansonsten eingerichtete HTTP-Datenschutzgrenze.  
   Diese Endpunkte müssen `verify_api_key` verwenden oder in einen minimalen öffentlichen Liveness-Endpunkt und authentifizierte Detaildiagnose getrennt werden.

### Freeze-Bindung

Start und Ende identisch, kein Drift:

- Branch: `operator-workbench-phase1`
- HEAD: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- Manifest SHA-256: `116682a5ea20eda60dcc10d3629b659baffda0574a7d453e981b8bdc89a69f61`
- Hash-Einträge: `132`, alle verifiziert
- Exakter Hashzeilen-Aggregat: `64558ac9a280dbaa66e82af6036dc99ca208d4cb5684d903a1751e7b70b25e50`
- Status-Population: `133`
- Manifest-/Population-Abdeckung: exakt, keine fehlenden oder zusätzlichen Scope-Pfade

### Durchführung

- Read-only Prüfung von HTTP/WS/Session-/Ownership-/Run-Trace-Pfaden, Prozessautorität und Cleanup-Logik, Persistenz, Polling, Hardware, Reset, Datenschutz und Accessibility.
- Keine Tests, Imports oder Netzwerkzugriffe ausgeführt.
- **Keine Dateien erstellt oder verändert.**