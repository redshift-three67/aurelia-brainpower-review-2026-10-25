# CURRENT SESSION CHRONICLE – Rekonstruktion 2026-07-13

**Projekt:** Morphic Engine V1 / Operator Workbench
**Worktree:** `C:\morphic_v1\.worktrees\operator-workbench-phase1`
**Sessionende/Pause:** 2026-07-13 00:28

> Diese Datei ist eine detaillierte technische Rekonstruktion der Session aus Chatverlauf, Toolausgaben, Änderungen und Verifikation. Sie ist kein bytegenauer Export einer internen Chatdatenbank. Der verbindliche Fortsetzungswortlaut steht in `NEXT_SESSION_PROMPT.md`.

## 1. Ausgangslage

Die Session begann nach einem Absturz der vorherigen Sitzung. Der reale Zustand wurde aus Git, `PROJECT_MEMORY`, Status-/Handoff-Dateien und der gespeicherten letzten Hermes-Session rekonstruiert. Dabei wurde festgestellt:

- `PROJECT_MEMORY/00_CURRENT_STATE.md` war veraltet und endete noch vor Feedbackpunkt e;
- das Handoff `2026-07-12_153244` endete vor E5.10A;
- der tatsächlich neueste Stand war E5.10D vollständig abgeschlossen;
- Feedback e lag bei ca. 85 %;
- E5.10 insgesamt blieb NO-GO;
- nächster sicherer Block war E5.10E.

## 2. E5.10E-Discovery

Kartiert wurde der reale produktive Pfad:

```text
POST /api/scan/jobs
→ apps/web/main.py::scan_job_start
→ build_phase1_scan_launcher
→ LocalScanJobService.start
→ python -m apps.cli.main scan top3-scan
→ N Screening-Subprozesse field multiplex-scan
→ N Detail-Subprozesse field multiplex-scan
→ AnalysisService.encode_profile(profile_obj)
```

Der zentrale Architekturbruch war, dass `AnalysisService` zwar `group_opt_in` unterstützte, der produktive Field-Aufruf aber keines übergab. Gleichzeitig durfte der E5.10D-One-Time-Handle nicht einfach an sämtliche Subprozesse weitergereicht werden, weil nur der erste Consumer erfolgreich wäre.

## 3. Gewählte Architektur

Die minimal sichere Lösung wurde als Root-/Child-Handle-Fan-out festgelegt:

1. Webprozess prüft Kill-Switch und explizite Stärke.
2. Nur ein explizites `group_draft_id` kann Aktivierung anfordern.
3. Subject-ID wird serverseitig aus den aktuellen Scanidentitätsdaten abgeleitet.
4. Draft, Mitglieder, Einzelconsents, Owner, Workspace und Tenant werden vor Prozessstart geprüft.
5. Ein autorisierter In-Memory-Kandidat wird als DPAPI-Root-Handle gespeichert.
6. `LocalScanJobService` erhält den Handle ausschließlich als nicht persistiertes `env_overrides`.
7. Top-N konsumiert den Root-Handle einmal unmittelbar beim Start.
8. Top-N hält den Kandidaten nur in-memory und erzeugt für jeden Screening-/Detailprozess einen neuen Child-Handle.
9. Jeder Field-Worker konsumiert genau seinen Child-Handle.
10. Erst danach wird das Opt-in an `AnalysisService.encode_profile()` übergeben.

Ein unabhängig gestarteter Read-only-Subagent kam zeitversetzt zur exakt gleichen Architekturentscheidung. Sein ursprüngliches NO-GO bezog sich auf den Vor-E5.10E-Stand; seine empfohlene Root-/Child-Handle-Lösung war zu diesem Zeitpunkt bereits umgesetzt.

## 4. TDD-Arbeitsblöcke

| Block | RED | GREEN/Ergebnis |
|---|---|---|
| Runtime-Environment | neues Modul fehlte; 4 Fehler | `core/compliance/group_activation_runtime.py`; 5 Tests grün |
| Field-Worker | Helper und Übergabe fehlten; 3 Fehler | One-Time-Consume unmittelbar vor `encode_profile()` |
| Top-N-Fan-out | Root-Consume/Child-Ausgabe fehlten; 3 Fehler | eigener Handle pro Subprozess |
| ScanJob-Environment | `env_overrides` unbekannt | Prozess-only Environment, Snapshot bleibt redigiert |
| Web-Vorbereitung | Modul und `group_draft_id` fehlten; 4 Fehler | serverseitige Draft→Resolver→Handle-Kette |
| Webroute | Fake-Job erhielt kein Environment | privates Environment nur bei gültiger Aktivierung |
| Release-Gate | alte Nichtverdrahtungsassertion | positiver handle-only Boundary-Vertrag |

## 5. Implementierte Dateien

Neu:

- `core/compliance/group_activation_runtime.py`
- `apps/web/group_analysis_runtime.py`
- `tests/test_group_activation_runtime.py`
- `tests/test_field_group_activation_runtime.py`
- `tests/test_topn_group_activation_fanout.py`
- `tests/test_scan_job_private_environment.py`
- `tests/test_web_group_productive_activation.py`
- `.hermes/plans/2026-07-13-e510e-local-productive-group-integration.md`
- `docs/status/2026-07-13-e510e-local-productive-group-integration-gate.md`

Geändert:

- `apps/web/contracts.py`
- `apps/web/main.py`
- `apps/web/scan_jobs.py`
- `apps/cli/commands/scan.py`
- `apps/cli/commands/field.py`
- `tests/test_group_e510_release_gate.py`
- `tests/test_group_vector.py`
- `docs/status/2026-07-12-gesamtstruktur-fortschritt.md`

## 6. Sicherheitsgrenzen

- `Phase1ScanRequest` enthält nur optionales kanonisches `group_draft_id`.
- Keine Rohgruppenwerte, Member-Rate-Mappings, Zentroide, Subjects oder Handles im Request.
- Kein Handle in CLI-Kommandos.
- Job-Snapshot speichert weder Environment noch Handle/Storepfad.
- Workbench-Run-Trace bleibt redigiert.
- Reports und Manifeste erhalten keine Gruppenwerte.
- Fehlendes Flag, fehlende Stärke oder Stärke 0 führen ohne Storezugriff zur Baseline.
- Handlefehler sind fail-closed.
- `MORPHIC_RUNTIME_DIR` wird nur im privaten Environment gesetzt, damit Web-, Top-N- und Field-Prozesse denselben Workspace-/Tenant-Kontext auflösen.
- Geo blieb vollständig unverdrahtet.

## 7. Verifikation

- 59 fokussierte E5.10E-/Web-/Release-Tests bestanden.
- 13 neue Integrationsfokustests bestanden.
- Rest-Suite: 470 bestanden, 2 übersprungen, acht bekannte gemeinsame 429-Ausreißer; alle separat grün.
- Ein alter Boundary-Test wurde gategerecht evolviert und isoliert grün nachgewiesen.
- Top-5-Smoke: `1 passed in 152.25s`.
- Python-Compile, JavaScript-Syntax und `git diff --check`: bestanden.

## 8. Endposition

```text
Feedback e: ca. 90 %
E5.10A–E: technisch GO
E5.10 insgesamt: NO-GO
Nächster Block: E5.10F
Geo: separat NO-GO
```

E5.10F muss die explizite Browsersteuerung, positive reale synthetische Wirkung, Rollback-Matrix, Redaction realer Laufartefakte und die finale Browser-/Privacy-/Audit-Gesamtfreigabe erbringen.

Es wurden keine Commits, Pushes, Stagings, Resets oder Cleans durchgeführt. Port 8090 und bestehende Prozesse blieben unberührt.
