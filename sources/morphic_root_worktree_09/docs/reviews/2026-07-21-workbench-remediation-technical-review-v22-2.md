## Verdict: **REQUEST CHANGES / NICHT GENEHMIGT**

**Befunde:** `P0=0, P1=2, P2=2, P3=0`  
Die Freigabeschwelle `P0=P1=P2=P3=0` ist nicht erfüllt.

### P1

- **Unauthentifizierter, eigentümerübergreifender Scan-WebSocket:**  
  `apps/web/scan_live.py:22-82` akzeptiert `/api/scan/jobs/{job_id}/ws` vor jeder Authentifizierung und ruft `scan_jobs.get(job_id)` ohne Owner-Prüfung auf. Damit sind Jobstatus, Fortschritt und potenziell Logs auch bei konfiguriertem `MORPHIC_API_KEY` sowie für fremde Operatoren abrufbar. Der Fallback `scan_live.py:45-50` öffnet zusätzlich selbständig den persistenten Job-Store.
- **Run-Trace-IDOR innerhalb authentifizierter Kontexte:**  
  `apps/web/workbench.py:119-128` schützt den Run-Trace zwar mit API-Key, prüft aber keine Scan-Job-/Operator-Ownership. Der Trace enthält job- und klientenbezogene Review-/Profilinformationen aus `main.py:175-213`.

### P2

- **POSIX-Fehlergruppierung weiterhin unvollständig:**  
  In `_token_process_pidfds()` werden Close-Fehler bei gleichzeitig aktiver Provenienz-/Acquisition-Ausnahme unterdrückt (`scan_jobs.py:755-759`). Auch der äußere Cleanup verwirft seine Close-Fehler (`scan_jobs.py:761-763`). Freeze v22 behebt nur den späteren Signal+Close-Pfad in `_signal_posix_authority()`, nicht alle Descriptor-Acquisition/Validation/Close-Kombinationen.
- **Windows-Termination/Query kann Primärfehler durch Close-Fehler maskieren:**  
  `_terminate_windows_job()` verliert bei gleichzeitig fehlgeschlagenem `TerminateJobObject` und `CloseHandle` den Termination-Primärfehler (`scan_jobs.py:549-557`). Dasselbe Muster besteht bei Query+Close in `_windows_job_active()` (`scan_jobs.py:603-618`). Während Recovery kann ein solcher `OSError` durch `_recover_jobs()` abgefangen und der persistierte Job vollständig übersprungen werden (`scan_jobs.py:1073-1083`).

## Freeze-Bindung

- Worktree: `C:/morphic_v1/.worktrees/operator-workbench-phase1`
- Branch/HEAD Start und Ende: `operator-workbench-phase1` / `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- Manifest-SHA-256: `221ae14e85dd615c4482d29fcf0f5d99c89d82bc355fe6700e784cab7de74f58`
- Einzelhashes: `125/125 OK`
- Aggregat: `0442c28997476ebdbb30832a4b9e41503a23297655cbb14fbfad33b8b74c41d7`
- Exakte Population: `126/126`; `EXTRA=[]`, `MISSING=[]`
- Vollständiger Status-Fingerprint (`--porcelain=v1 -z --untracked-files=all`): `70a46c44aff73ba1084312926580178188a1ea8e54c38cbb4a1cfacbf056b228`
- **Drift: 0**

Keine Tests, Imports, Server oder Netzwerkzugriffe ausgeführt. Keine Dateien erstellt oder verändert.