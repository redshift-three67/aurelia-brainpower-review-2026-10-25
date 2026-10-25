## Urteil: **REQUEST CHANGES**

**Schweregrade:** `P0=0 · P1=1 · P2=2 · P3=1`  
Die Freigabeschwelle `P0=P1=P2=P3=0` ist nicht erfüllt. Der Snapshot blieb jedoch vollständig driftfrei.

### Befunde

- **P1 – API-Key-Rotation widerruft bestehende Browser-Sessions nicht**
  - `SessionAuthority` speichert zeitlich unbegrenzte, nicht an Schlüssel bzw. Schlüsselgeneration gebundene Tokens: `apps/web/security.py:44-67`.
  - HTTP und beide WebSockets akzeptieren diese Sessions auch nach Änderung von `MORPHIC_API_KEY`: `security.py:75-86,89-110`.
  - Damit bleibt eine unter dem alten Schlüssel ausgestellte Session nach Schlüsselrotation weiterhin autorisiert. Einzel-Logout und Prozessneustart widerrufen sie, dynamische Schlüsselrotation jedoch nicht.

- **P2 – Telemetrie-Aktivierung ist nicht autoritativ**
  - `/api/emf/enable` und `/disable` ändern nur `_emf_active`: `apps/web/emf.py:18,26-45`.
  - `/api/emf/profile` misst unabhängig vom deaktivierten Zustand: `emf.py:48-50`.
  - `/api/workbench/hardware` misst ebenfalls immer live: `apps/web/workbench.py:50-66`.
  - Diese Messung wird beim normalen UI-Bootstrap automatisch ausgelöst: `apps/web/static/app.js:1123-1140`.
  - Somit verhindert „disable“ keine Telemetrieerhebung; die Aktivierungsanzeige ist vom produktiven Messpfad getrennt.

- **P2 – Interne Fehlerdetails werden über Hardware-Diagnostik offengelegt**
  - `measure_realtime_calibration()` serialisiert unverändert `str(exc)` in den API-Payload: `apps/web/hardware_truth.py:27-45`.
  - Auch der Driver-Layer-Payload enthält `error: str(exc)`: `apps/web/main.py:125-130`.
  - Beide Datenpfade sind über authentifizierte Hardware-/Workbench-Endpunkte erreichbar. Die Freeze-v25-Behauptung „generic errors“ ist damit nicht vollständig erfüllt.

- **P3 – Harmonization-Polling besitzt keine gemeinsame Single-Flight-Autorität**
  - Scan-Polling hat einen Promise-Identity-Guard: `apps/web/static/app.js:398-406`.
  - Harmonization-Polling führt dagegen jeden manuellen oder geplanten Poll separat aus und plant je Abschluss einen Folgetimer: `app.js:696-768`.
  - Manueller Refresh (`app.js:1230-1234`) kann deshalb mit dem geplanten Poll überlappen und mehrere Pollketten erzeugen. Generation-Prüfungen verhindern zwar Mutation nach Reset, nicht aber Parallelität derselben Generation.

### Verifizierte Oberflächen

- HTTP: öffentliche UI/Status-/Auth-Status-Routen; API-Key-/Session-geschützte Health-, Hardware-, Privacy-, Report-, Scan-, Harmonization-, Workbench-, EMF-, Amplifier-, Profile-, Analyze-, Synergy- und Gruppenrouten; separate Admin-Token-Fläche.
- WebSocket:
  - `/api/scan/jobs/{job_id}/ws`: Authentifizierung vor Store-Zugriff, strikte Owner-Prüfung vor `accept()`, erneute Auth-/Owner-Prüfung vor Frames.
  - `/api/emf/ws`: Authentifizierung vor `accept()` und Messung sowie dynamische Prüfung vor jedem Telemetrie-Frame.
- Scan-Status, Stop, Results, Sync-Trace und Run-Trace prüfen strikte Ownership; fehlende/leere/fremde Owner sind fail-closed.
- Recovery und POSIX-/Windows-Cleanup erhalten geprüfte kombinierte Signal-, Query-, Close- und Wait-Fehler; ambivalente Recovery-Autorität wird persistiert statt still verworfen.
- Persistenz, Reset, Datenschutz-Opt-ins, Hardware-Truth und Accessibility wurden statisch nachvollzogen; keine zusätzlichen freigabeblockierenden Befunde außer den oben genannten.

### Freeze-Bindung – Start und Ende identisch

- Worktree: `C:/morphic_v1/.worktrees/operator-workbench-phase1`
- Branch: `operator-workbench-phase1`
- HEAD: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- Manifest SHA-256: `e69b33ac8f7604686a421342d8e162af92acc54e836903031cc520f0baf18c5a`
- Einträge: `146`; sämtliche Einträge bestanden `sha256sum -c`
- Aggregate as-listed: `680c317658fa0a9e7f4776354bc03ac53ba63e422318a0d3a86af1e6068a29d2`
- Population: `147`; Scope/Dirty `147/147`, fehlend `0`, zusätzlich `0`
- Status-Fingerprint Start/End: `08561dc795c49b16e6a81a662e4f12b36c1cfe8b81d87aff83a10cc06fafefef`
- **Drift: 0**

**Dateien geändert/erstellt:** keine.  
**Ausführung:** strikt read-only; keine Tests, Produktimporte oder Netzwerkzugriffe.