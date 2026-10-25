# Morphic V1 – Präziser Session-Handoff

**Erstellt:** 2026-07-11T00:12:13 (lokale Sitzung)
**Arbeitsverzeichnis:** `C:\morphic_v1\.worktrees\operator-workbench-phase1`
**Branch:** `operator-workbench-phase1`
**HEAD bei Pause:** `619a1f5485a151816e32732929a6a823839ccb57`
**Betriebsprofil:** Variante A – lokaler Einoperator, ausschließlich Loopback.
**Kein Commit oder Push wurde in dieser Session ausgeführt.**

---

## 1. Exakter Startauftrag für die nächste Session

> Arbeite ausschließlich im Worktree `C:\morphic_v1\.worktrees\operator-workbench-phase1` auf Branch `operator-workbench-phase1`. Lies zuerst `CLAUDE.md`, diese Handoff-Datei, `PROJECT_MEMORY/00_CURRENT_STATE.md` falls vorhanden und `docs/plans/2026-07-10-morphic-v1-stabilisierung-security-ui-umsetzungsplan.md`. Prüfe danach Branch, `git status --short`, `git diff --check`, die Portbelegung 8000/8001/8090 sowie die konkreten Quell- und Testdateien des nächsten Gates. Lies niemals `.env`-Dateien, Secrets, reale Klientenexporte, Runtime-Inhalte oder ungetrackte `Benutzer_Archive__ws-*`-Ordner. Kein Commit, Push, Löschen, Verschieben vorhandener Export-/Archivdaten oder Start auf Port 8090 ohne explizite Nutzerfreigabe.
>
> Halte TDD ein: zuerst RED-Test schreiben und Fehlschlag ausführen, dann minimale GREEN-Implementierung, gezielte Tests, `py_compile` für geänderte Python-Dateien, `node --check` für geänderte JS-Dateien, `git diff --check` und schließlich die Vollsuite:
> ```bash
> PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 /c/morphic_v1/.venv/Scripts/python.exe -m pytest tests -q
> ```
> Vor jedem mutierenden Block eine zeitgestempelte ShadowCopy unter `E:\mprphic_v1_Backups\` mit `SOURCE_MANIFEST.sha256` erzeugen und prüfen. Ausschließlich additive, getrennt testbare Gates; keine Änderung von Scoring, Resonanzformeln, Profil-/Gruppenlogik, Multiplexlogik oder Legacy-Exportinhalten ohne eigenes Äquivalenzgate.

## 2. Letzter verifizierter Stand

```text
Vollsuite: 335 passed, 2 skipped in 112.35s
Git diff --check: Exit 0
Bekannte Ausgabe: ausschließlich CRLF-Hinweise in bereits bestehenden geänderten Dateien.
Gezieltes JSONL-/Scanjob-Gate: 6 passed in 0.20s
Port 8090: Listener vorhanden, gehört Radi144; nicht anfassen.
Port 8000: Listener vorhanden.
Port 8001: nicht durch diese Session belegt.
```

Die aktuelle Session wurde zusätzlich in diesem Projektordner gesichert:

```text
docs/session-handoffs/2026-07-11_001213/
  SESSION_HANDOFF.md      # dieser vollständige Weiterarbeitsauftrag
  GIT_STATUS.txt          # Statussnapshot vor Handoff-Erstellung
  VERIFICATION.md         # reale letzte Test-/Gate-Ergebnisse
```

## 3. Phasenstatus und Fortschritt

Die Prozentwerte sind Planfortschritt, **keine Produktionsfreigabe**.

| Bereich | Status | Fortschritt |
|---|---|---:|
| Phase 0 – Basis/Verifikation | abgeschlossen | 100 % |
| Phase 1 – Workbench-Grundlagen | abgeschlossen; manuelles Browsergate offen | 100 % |
| Phase 2 – lokaler Einoperator/Loopback | abgeschlossen | 100 % |
| Phase 3 – Privacy-/Export-/Erasure-/Backup-Grenzen | abgeschlossen, additiv/synthetisch | 100 % |
| Phase 4 – Nachvollziehbarkeit/Jobsicherheit | sichere Vorstufen fertig, keine Runtime-Anbindung | 100 % der fünf Planvorstufen |
| Phase 5 – Modifier/Radi144-Klientendaten | offen | 0 % |
| Phase 6 – Harmonization Truthfulness | offen | 0 % |
| Phase 7 – UX/Browser/Accessibility/Performance | formelle Abnahme offen | 0 % |
| Phase 8 – Betriebsreife/CI/Runbook | offen | 0 % |

**Produktionsreife bleibt 0 %**, solange die Abschlusskriterien der Phasen 4–8, insbesondere Browser-/Security-/Privacy-Nachweise, Recovery, CI und Restorepunkt, nicht erfüllt sind.

## 4. In dieser Session abgeschlossene Phase-4-Gates

### Gate 1 – reiner Run-Manifest-Builder
- `core/compliance/run_manifest.py`
- `tests/test_run_manifest.py`
- Deterministisches, pseudonymes Objekt: Schema, Run-ID, Zeitstempel, Commit, Tenant-/Client-ID, Profil-/Daten-/Artefakthashes, Seed-Modus, Parameter-Version, Manifesthash.
- Nicht an Scans, Reports, Runtime oder Writer verdrahtet.

### Gate 2 – explizite Hashquellen
- `core/compliance/run_manifest_sources.py`
- `tests/test_run_manifest_sources.py`
- Read-only Git-Commit und explizit übergebene reguläre Quellpfade; keine Pfadrateversuche, symbolische oder fehlende Quellen fail-closed.

### Gate 3 – Top-N-Quellenkarte und synthetischer Post-Success-Writer
- `docs/deep-audit-2026-07-10/PHASE_4_TOPN_RUN_MANIFEST_SOURCE_MAP.md`
- `core/compliance/run_manifest_persistence.py`
- `tests/test_run_manifest_persistence.py`
- Nachgewiesene spätere Quellen: `core/profile_sync/__init__.py`, `apps/cli/commands/scan.py`, `core/subgroups/procedural_groups.py`, `services/subgroup_service.py`.
- Klarnamen, Geburtsdaten, Fokus, Bilder, Seedmaterial, Entropieproben und Laufzeitdaten ausdrücklich ausgeschlossen.
- Manifest wird nur bei `status == "completed"` und `returncode == 0` atomar geschrieben; Tests benutzen nur `tmp_path`.

### Gate 4 – synthetisches Web-Jobmanifest
- `core/compliance/web_job_manifest.py`
- `tests/test_web_job_manifest.py`
- `docs/deep-audit-2026-07-10/PHASE_4_WEB_JOB_MANIFEST_GATE.md`
- Atomare, redigierte Jobmetadaten (Job-ID, Status, Exitcode, Owner/Tenant, Zeitstempel, Logpfade). Für `top3-scan` werden sämtliche Argumente nach dem Kommando redigiert. `recover_read_only()` verändert die Datei nicht.
- Nicht in `LocalScanJobService` oder FastAPI verdrahtet.

### Gate 5 – strukturierte JSONL-Progress-Events
- `core/compliance/progress_events.py`
- `tests/test_progress_events.py`
- `docs/deep-audit-2026-07-10/PHASE_4_JSONL_PROGRESS_GATE.md`
- JSONL-Allow-list enthält nur Schema, Zeitstempel, Job-ID, Status, Exitcode, Fortschritt, Phase, Substep und abgeschlossene Substeps. Command sowie stdout/stderr werden nie serialisiert.
- Nicht an `LocalScanJobService` oder UI verdrahtet; stdout bleibt unveränderter Fallback.

## 5. Exakte nächste Arbeit

Der nächste sichere Arbeitsblock ist **Phase 4: Mehrprozess-/Store-Grenzen dokumentieren und eine Runtime-Anbindung noch nicht implementieren**.

1. `apps/web/scan_jobs.py`, `apps/web/main.py`, `apps/web/workbench_runtime.py`, die neuen `core/compliance/*manifest*.py` sowie zugehörige Tests vollständig lesen.
2. Eine schriftliche Mehrprozessentscheidung erstellen: aktueller `LocalScanJobService` hält Jobs nur in-memory; `threading.Lock` schützt nicht mehrere Prozesse; der neue JSONL-/Manifest-Store ist derzeit nur synthetische Vorstufe.
3. Festlegen, dass echte App-Start-Recovery, Runtime-Jobmanifest-Integration und JSONL-UI-Präferenz **erst nach separaten RED-Tests** erfolgen dürfen. Dazu gehören PII-Redaction, Owner-/Tenant-Policy, abgestürzter Prozess, fehlende/beschädigte Dateien und unveränderte stdout-UI-Fallbacks.
4. Danach Phase-4-Abschluss nur dann behaupten, wenn Restart-Smoke, Event-/Fallback-Test, Reporthashvergleich und Vollsuite tatsächlich grün sind.

Nicht als nächstes ohne neue explizite Freigabe starten:
- reale Manifest-/Web-Job-/JSONL-Runtime-Anbindung,
- Phase 5 Modifier-/Radi144-Daten,
- Phase 6 Harmonization-Semantik,
- Multiuser-/OIDC-/TLS-Betrieb,
- reale Exportmigration, Löschung oder Restore echter Daten.

## 6. Noch offene manuelle Abnahme

`phase1-accessibility-manual` bleibt offen: M1–M6 für Tastatur, Zoom/320px, Kontrast und Firefox/NVDA. In dieser Agentensitzung waren Firefox, NVDA, Playwright, Selenium und ein steuerbarer Browser nicht verfügbar. Nicht als bestanden behaupten. Die formelle Checkliste ist `docs/deep-audit-2026-07-10/PHASE_1_ACCESSIBILITY_CHECKLISTE.md`.

## 7. Unverhandelbare Invarianten

1. Keine Resonanz-, NLS-, Profil-, Gruppen-, Multiplex- oder Scoringänderung ohne Äquivalenzgate.
2. Keine Secrets, `.env`, Klientenexporte, echte Runtime-/Archiv-/Backupdaten öffnen oder ausgeben.
3. `Benutzer_Archive__ws-*` sind Testartefakte: nicht lesen, verschieben, löschen oder committen.
4. Erasure bleibt read-only Dry-run; keine automatische Löschung.
5. Kein Commit oder Push ohne explizite Nutzerfreigabe.
6. Loopback-only bleibt aktiv; keine Mehrbenutzer-, LAN- oder SaaS-Zusage.
7. Vor Serverstart Ports prüfen; temporäre Server nur auf `127.0.0.1` und danach beenden.
8. Radi144 auf `127.0.0.1:8090` nicht stören.

## 8. Einstiegskommandos

```bash
cd /c/morphic_v1/.worktrees/operator-workbench-phase1
git branch --show-current
git status --short
git diff --check
python -c "import subprocess; text=subprocess.run(['netstat','-ano'], capture_output=True).stdout.decode('utf-8', errors='replace'); print(''.join(line+'\n' for line in text.splitlines() if any(':'+port in line for port in ('8000','8001','8090'))) or 'ports 8000/8001/8090: none')"

PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 \
  /c/morphic_v1/.venv/Scripts/python.exe -m pytest tests -q
```
