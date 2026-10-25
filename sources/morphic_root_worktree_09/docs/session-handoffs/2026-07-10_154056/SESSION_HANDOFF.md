# Morphic V1 – Präziser Session-Handoff

**Erstellt:** 2026-07-10T15:40:56+02:00
**Arbeitsverzeichnis:** `C:\morphic_v1\.worktrees\operator-workbench-phase1`
**Branch:** `operator-workbench-phase1`
**HEAD bei Pause:** `619a1f5485a151816e32732929a6a823839ccb57`
**Betriebsprofil:** Variante A – lokaler Einoperator, ausschließlich Loopback.
**Kein Commit/Push ausgeführt.**

---

## 1. Exakter Startauftrag für eine neue Session

> Arbeite im Worktree `C:\morphic_v1\.worktrees\operator-workbench-phase1` auf Branch `operator-workbench-phase1` weiter. Lies zuerst `CLAUDE.md`, diese Datei und `docs/plans/2026-07-10-morphic-v1-stabilisierung-security-ui-umsetzungsplan.md`. Lies keine `.env`-Dateien, Secrets, Klientenexporte oder ungetrackte `Benutzer_Archive__...`-Ordner. Prüfe vor jeder Änderung Branch, Git-Status, Ports und relevante Quell-/Testdateien. Kein Commit, Push, Löschen oder Verschieben vorhandener Klientenexporte ohne ausdrückliche Freigabe. Nutze TDD: zuerst RED, danach minimale GREEN-Änderung, gezielte Tests, `node --check` für geänderte JS-Dateien, `git diff --check` und anschließend die Vollsuite mit `PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 C:/morphic_v1/.venv/Scripts/python.exe -m pytest tests -q`.
>
> Aktueller Fokus ist **Phase 3 – Privacy Data Lifecycle und sichere Exportgrenze**. Der zuletzt implementierte Stand ist ein serverseitig aktivierbarer, ausschließlich planender Parallel-Exportmodus. Bei gesetztem `MORPHIC_PARALLEL_EXPORT_ROOT` ergänzt `POST /api/scan/jobs` einen pseudonymen `parallel_export_plan` und eine `parallel_export_client_id` zur Response und registriert den Plan als `parallel_export_plan` im Runtime-Manifest. Der produktive Legacy-CLI-Befehl einschließlich `--export C:\Benutzer_Archive_Start` bleibt unverändert. Es wird keine Datei im Parallelpfad geschrieben. Ohne gesetzte Environment-Variable bleibt der Parallelmodus deaktiviert.
>
> Nächster optimaler Schritt: Einen **synthetischen, rein lesenden Manifest-/Reportkatalog-Lesetest** für den Parallelplan hinzufügen. Er darf keine bestehenden Exportverzeichnisse öffnen, verschieben oder verändern. Er soll mit einem temporären Root nachweisen, dass (a) der Parallelplan über pseudonyme Tenant-/Client-/Sessionsegmente referenziert wird, (b) der Runtime-Erasure-Dry-run ihn als registriertes, noch fehlendes Artefakt erkennt und (c) der Legacy-Reportkatalog ohne tatsächliche Parallel-Exportdatei keine neue Datei als Bericht anbietet. Danach erst entscheiden, ob ein separater, expliziter synthetischer Schreibtest mit temporärem Root sinnvoll ist. Keine Umstellung des Legacy-Schreibpfads ohne eigenes Äquivalenzgate.

---

## 2. Letzter verifizierter Stand

```text
pytest tests -q
320 passed, 2 skipped in 120.78s

git diff --check
OK (nur CRLF-Hinweise in bestehenden geänderten Dateien)

py_compile OK:
- apps/web/main.py
- apps/web/contracts.py
- core/compliance/artifact_repository.py
```

Vor dem letzten Integrationsschritt waren zusätzlich geprüft:

```text
node --check apps/web/static/app.js
node --check apps/web/static/workbench-api.js
```

**Wichtig:** Nach dem letzten Codechange (`apps/web/main.py`, `apps/web/contracts.py`) lief die vollständige Suite grün. Kein Server ist aus dieser Sitzung aktiv; der frühere temporäre Auditserver auf Port 8001 wurde beendet.

---

## 3. Umgesetzte Phasen und Entscheidungen

### Phase 0 – abgeschlossen

- Zeitgestempelte ShowCopy existiert unter `E:\mprphic_v1_Backups\morphic_v1_showcopy_20260710_091815`.
- Keine Klientenexporte, Runtime-Daten oder Secrets in die ShowCopy aufgenommen.

### Phase 1 – Workbench-Vertrag weitgehend abgeschlossen

- Hardware-Dictionary-Normalisierung in Review-Karten.
- Zentraler HTTP-Fehlervertrag für alle Workbench-API-Helper.
- Job-ID-Gate, Consent-/Pflichtfeld-/Datumsvalidierung, 11-Step-Fallback und Fortschrittsvertrag.
- Dynamische DOM-Ausgaben in Workbench-Review, Hardware, Reportkatalog, Choice-Cards und Ergebnissen auf DOM-Knoten/Textknoten umgestellt.
- `innerHTML`-Sinks in `app.js` und `workbench-render.js` entfernt.
- Browser-/Loopback-Smoke auf isoliertem Port 8001 durchgeführt; HTTP 422 für ungültige Preview bestätigt.

Rest Phase 1: formelle manuelle Accessibility-Checkliste (Tastatur, Zoom, NVDA/Firefox) und Statusdokumentation konsolidieren; automatisierte Gates sind grün.

### Phase 2A – lokaler Einoperator umgesetzt

- `web_server.py` verweigert nicht-loopback `APP_HOST` fail-closed.
- `Run-WebUI.ps1` bindet fest an `127.0.0.1` und beendet keinen belegenden Prozess mehr automatisch.
- CORS ohne Wildcard, restriktive Security-Header, CSP, Referrer- und Permissions-Policy implementiert.
- API-Key ist als optionaler Maschinen-Key eingeordnet, nicht als Browser-Login oder Multiuser-Sicherheit.
- Dokumentiert in `README.md`, `docs/LOCAL_OPERATOR_RUNBOOK.md` und `docs/deep-audit-2026-07-10/PHASE_2_*.md`.

Variante B (OIDC/TLS/echte Principals/Rollen/Tenant-AuthZ) ist bewusst **nicht** implementiert.

### Phase 3 – laufend, zentrale Ergebnisse

1. Artefaktkarte: `docs/deep-audit-2026-07-10/PHASE_3_ARTEFAKTKARTE.md`.
2. `RuntimeManifestService.erasure_manifest()` ist ein read-only Completion-Report:
   - registrierte Artefakte mit `path_state`,
   - abgedeckte/nicht abgedeckte Speicherklassen,
   - Workbench-Dry-run über `draft.json`, `templates.json`, `run_traces.json`,
   - Web-Joblog-Dry-run mit `attributable_via_run_trace` oder `unattributable_global`,
   - Harmonization JSON/JSONL als `unattributable_global`.
3. CLI unterstützt:
   ```text
   privacy erasure-manifest <cli-id>
     --runtime <runtime-dir>
     --workbench-runtime <workbench-dir>
     --web-job-root <web-job-root>
     --harmonization-root <harmonization-root>
   ```
4. Fokus-Historie im Browser: nur nach Opt-in; Deaktivieren löscht Consent plus Historie; expliziter Löschbutton vorhanden.
5. Run-Traces enthalten für neue Läufe keine Klarnamen, Geburtsdaten, Geburtsorte oder Fokuswerte mehr; nur `review.client_id` plus technische Profilparameter.
6. Sensible Workbench-Drafts/Templates benötigen serverseitig `persist_sensitive_data: true`. Browser-Template-UI hat sichtbare Operatorfreigabe; ohne Freigabe HTTP 422.
7. Neuer additiver `TenantClientArtifactRepository` plant nur kanonische Pfade:
   ```text
   <root>/<tenant_id>/<client_id>/<category>/<session_id>/<filename>
   ```
8. Der serverseitige Parallelplan wird nur aktiviert, wenn `MORPHIC_PARALLEL_EXPORT_ROOT` gesetzt ist. Er erzeugt keine Datei und ändert den Legacy-Export nicht.

---

## 4. Letzter Codezustand – relevante Dateien

### Neu, ungetrackt

```text
core/compliance/artifact_repository.py
tests/test_tenant_client_artifact_repository.py
tests/test_synthetic_parallel_export_plan.py
tests/test_parallel_export_plan_configuration.py
tests/test_runtime_erasure_dry_run_completion.py
tests/test_runtime_erasure_workbench_dry_run.py
tests/test_runtime_erasure_web_job_dry_run.py
tests/test_runtime_erasure_harmonization_dry_run.py
docs/session-handoffs/2026-07-10_154056/SESSION_HANDOFF.md
```

Zusätzlich sind die früheren Audit-/Plan-/Frontend-/Launcher-/Security-Regressionen als ungetrackte Dateien vorhanden. Nicht pauschal löschen oder neu erzeugen.

### Geändert, nicht committet

```text
README.md
Run-WebUI.ps1
apps/cli/commands/privacy.py
apps/web/contracts.py
apps/web/main.py
apps/web/static/app.js
apps/web/static/index.html
apps/web/static/workbench-api.js
apps/web/static/workbench-render.js
apps/web/static/workbench-state.js
apps/web/workbench.py
core/compliance/runtime_manifest.py
tests/test_web_shell.py
tests/test_web_workbench_runtime.py
web_server.py
```

### Kritische aktuelle Implementierungsdetails

- `apps/web/main.py:506+` ergänzt beim Scanstart bei gesetztem `MORPHIC_PARALLEL_EXPORT_ROOT` die Responsefelder `parallel_export_plan` und `parallel_export_client_id`; registriert den Plan im `RuntimeManifestService`.
- `apps/web/contracts.py:189+` kennt die beiden optionalen Responsefelder.
- `core/compliance/artifact_repository.py` validiert alle Pfadsegmente und plant nur Pfade; Funktion `parallel_export_plan_from_environment()` ist bei fehlendem Root `None`.
- `apps/web/workbench.py` erzwingt bei sensiblen Draft-/Templatefeldern eine explizite Persistenzfreigabe.
- `core/compliance/runtime_manifest.py` darf nicht in einen Löschmodus erweitert werden, ohne eigenes Gate. Der bestehende Dry-run bleibt read-only.

---

## 5. Offene Prioritäten

| Priorität | Nächster Block | Sicherheitsregel |
|---|---|---|
| P0 | Parallelplan synthetisch gegen Manifest und Reportkatalog lesen testen | Keine reale Datei, keine Legacy-Pfadänderung |
| P0 | Phase-3-Exportäquivalenzgate definieren | Keine Produktionsexporte/Scoringformeln ändern |
| P1 | Windows ACL/DPAPI-Entscheidung mit temporären Testdaten | Keine echten Klientendaten/Secrets verwenden |
| P1 | Backup-/Restore-Policy und Testprobe | Keine vorhandenen Archive manipulieren |
| P1 | Phase-1-Manualliste: Tastatur/Zoom/NVDA/Firefox | Nur Loopback-Testserver, danach beenden |
| Danach | Phase 4 Run-Manifest/Job-Recovery | Keine Algorithmus-/Scoreänderung |

Nicht als nächstes starten: Phase 5 (Modifierdaten), Phase 6 (Harmonization-Semantik), Variante-B-Multiuserbetrieb oder eine reale Exportmigration. Sie benötigen eigene fachliche bzw. Architektur-Gates.

---

## 6. Unverhandelbare Invarianten

1. Keine Änderung an Resonanzformeln, NLS-Gewichten, Profil-/Gruppenregeln, Multiplex-/Scoringlogik oder bestehenden Exportinhalten ohne separates Äquivalenzgate.
2. Keine Secrets, `.env`-Inhalte, Klientenexporte oder Runtime-Inhalte lesen oder ausgeben.
3. Ungetrackte `Benutzer_Archive__ws-...`-Ordner stammen aus Tests; nicht lesen, verschieben, löschen oder committen.
4. Keine automatische Löschung: Erasure bleibt Dry-run, bis ein vollständiger Artefaktindex und ein explizites Freigabegate existieren.
5. Kein Commit/Push ohne Nutzerfreigabe.
6. Lokaler Betrieb bleibt Loopback-only; keine Multiuser-/SaaS-/LAN-Zusage.
7. Vor Serverstart Portbelegung prüfen; eigene temporäre Server ausschließlich auf `127.0.0.1` starten und danach beenden.

---

## 7. Empfohlene Einstiegsbefehle für die neue Session

```bash
cd /c/morphic_v1/.worktrees/operator-workbench-phase1
git branch --show-current
git status --short
git diff --check

PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 \
  /c/morphic_v1/.venv/Scripts/python.exe -m pytest tests -q
```

Dann zuerst die genannten Handoff-/Plan-Dokumente lesen, danach ausschließlich den P0-Parallelplan-Lesetest umsetzen.
