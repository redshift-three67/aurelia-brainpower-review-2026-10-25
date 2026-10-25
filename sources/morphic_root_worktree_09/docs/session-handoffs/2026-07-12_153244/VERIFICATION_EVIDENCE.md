# VERIFICATION EVIDENCE – Übergabe 2026-07-12 15:32 CEST

## 1. Repositoryidentität

```text
Worktree: C:\morphic_v1\.worktrees\operator-workbench-phase1
Git top-level: C:/morphic_v1/.worktrees/operator-workbench-phase1
Branch: operator-workbench-phase1
HEAD: 619a1f5 docs: mark feedback point d) Phase 5 complete, next up is point e)
```

Der Arbeitsbaum ist umfangreich modified/untracked. Der Status war bereits vor und während Phase E absichtlich nicht bereinigt. Die vollständige Live-Liste muss in der nächsten Session mit `git status --short` erneut erhoben werden.

Besonders zu schützen:

- zahlreiche `Benutzer_Archive__ws-*`-Verzeichnisse;
- `.hermes/` mit aktiven Plänen;
- neue Phase-E-Module und Tests;
- bestehende Modified-Dateien aus früheren Arbeitsblöcken.

Keine Bereinigung ist Teil der Übergabe.

---

## 2. Letzte vollständige Verifikation nach E5.9.5

### Fokussiertes Release-/Privacy-/Baseline-Gate

Befehl:

```bash
PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 /c/morphic_v1/.venv/Scripts/python.exe -m pytest \
  tests/test_group_e510_release_gate.py \
  tests/test_group_member_consent_revocation.py \
  tests/test_group_member_resolution_activation.py \
  tests/test_group_geo_default_equivalence.py -q
```

Ergebnis:

```text
12 passed in 0.55s
```

### Rest-Suite ohne Top-5-Smoke

Befehl:

```bash
PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 /c/morphic_v1/.venv/Scripts/python.exe \
  -m pytest tests -q --ignore=tests/test_top5_workflow_smoke.py
```

Ergebnis:

```text
1 failed, 418 passed, 2 skipped in 24.90s
```

Einziger Fehler:

```text
tests/test_workbench_client_context_persistence.py::
test_workbench_draft_rejects_optional_client_context_without_explicit_consent

expected 422, received 429
```

Ursache: gemeinsamer Test-IP-Rate-Limiter im großen Prozess, wiederholt reproduziert.

### Isolierter Retry des einzigen Ausreißers

```bash
PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 /c/morphic_v1/.venv/Scripts/python.exe -m pytest \
  tests/test_workbench_client_context_persistence.py::test_workbench_draft_rejects_optional_client_context_without_explicit_consent -q
```

Ergebnis:

```text
1 passed in 0.66s
```

### Separater Top-5-Workflow-Smoke

```bash
PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 /c/morphic_v1/.venv/Scripts/python.exe -m pytest \
  tests/test_top5_workflow_smoke.py::test_top5_scan_writes_multiplex_exports -q
```

Ergebnis:

```text
1 passed in 162.75s
```

### Syntax-/Compile-/Whitespace-Gate

```bash
PYTHONUTF8=1 /c/morphic_v1/.venv/Scripts/python.exe -m py_compile \
  core/compliance/runtime_manifest.py \
  core/compliance/group_member_identity_source.py \
  core/profiles/group_member_rate_resolver.py \
  apps/web/group_analysis_activation.py

node --check apps/web/static/app.js
node --check apps/web/static/workbench-api.js
git diff --check
```

Ergebnis:

```text
Exit 0
```

Git meldete bestehende LF→CRLF-Hinweise für mehrere Dateien, aber keine `git diff --check`-Fehler.

---

## 3. Gateweise Testentwicklung

| Gate | Letzter fokussierter Nachweis |
|---|---:|
| E5.8 UI/Router/Boundary | `8 passed` |
| E5.8 Browserabnahme | realer Playwright-Flow erfolgreich |
| E5.9.0 Namespace | `14 passed` im Gruppen-/Operatorblock |
| E5.9.1 Resolver | `19 passed` im Resolver-/Opt-in-/Authblock |
| E5.9.2 Identity Source | `24 passed` im Source-/Resolver-/Runtimeblock |
| E5.9.3 Draft-Resolver-Brücke | `23 passed` |
| E5.9.4 Consent/Erasure | `14 passed` |
| E5.9.5 Release-Gate | `12 passed` |

Die Rest-Suite wuchs im Verlauf bis auf 418 bestandene Tests plus 2 Skips und den bekannten isoliert grünen Rate-Limit-Ausreißer.

---

## 4. Verifizierte Nichtwirkungsgrenzen

| Pfad | Gruppenwirkung/-daten |
|---|---:|
| `Phase1ScanRequest` | keine Gruppenfelder |
| Webscan-Payload | keine Gruppenfelder |
| CLI | keine Gruppenflags oder Raten |
| Launcher | keine Gruppenaktivierung |
| Jobs | keine Mitgliedslisten/Raten |
| Reports | keine Mitgliedslisten/Raten |
| Run-Traces | keine Mitgliedslisten/Raten |
| Run-Manifeste | keine Mitgliedslisten/Raten |
| Gruppen-Draft-Router | nur lokale DPAPI-Draftverwaltung |
| `group_analysis_activation.py` | direkte Python-API, keine Route |
| `AnalysisService` | optionaler in-memory Opt-in; Default unverändert |

Projektweite Suche nach `build_resolved_group_draft_opt_in` und `RuntimeManifestGroupMemberIdentitySource` ergab nur:

- Definitionen;
- Tests;
- keine produktive Router-/Scan-/CLI-Verwendung.

---

## 5. E5.9.5 Release-Siegel

`tests/test_group_e510_release_gate.py` beweist absichtlich den NO-GO-Zustand:

- kein `group_opt_in`, `group_member_rates` oder `group_strength` in `Phase1ScanRequest`;
- keine Aktivierungsbrücke in `main.py` oder `group_drafts.py`;
- keine produktive Consent-Route;
- kein UI-Feld `group-strength`;
- kein `MORPHIC_GROUP_ANALYSIS_ENABLED`;
- aktive Runtime-Sessionregistrierung ruft weiterhin `get_or_create_client(client)` ohne Kontext auf;
- `group_opt_in=None` ist exakt baseline-äquivalent.

Dieser Test darf bei E5.10 nicht ersatzlos entfernt werden. Jede Blockerbehebung muss ihn in einen positiven, weiterhin default-sicheren Releasevertrag überführen.

---

## 6. Aktuelle Releaseentscheidung

```text
E5.9: GO / abgeschlossen
E5.10: NO-GO
Geo: NO-GO / separat
```

E5.10A–D müssen vor jeder produktiven Scanwirkung abgeschlossen sein:

1. gehärtete/verschlüsselte Client-Identity-Quelle;
2. Consent Enrollment und Widerruf;
3. default-false Kill-Switch und explizite Stärke;
4. sicherer kurzlebiger Worker-Transport ohne Rohvektoren in Payload/CLI/Logs.

---

## 7. Reproduktionsbefehle für die nächste Session

```bash
cd /c/morphic_v1/.worktrees/operator-workbench-phase1

git branch --show-current
git status --short
git log -1 --oneline

PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 /c/morphic_v1/.venv/Scripts/python.exe -m pytest \
  tests/test_group_e510_release_gate.py \
  tests/test_group_member_consent_revocation.py \
  tests/test_group_member_resolution_activation.py \
  tests/test_group_geo_default_equivalence.py -q

PYTHONUTF8=1 /c/morphic_v1/.venv/Scripts/python.exe -m py_compile \
  core/compliance/runtime_manifest.py \
  core/compliance/group_member_identity_source.py \
  core/profiles/group_member_rate_resolver.py \
  apps/web/group_analysis_activation.py

node --check apps/web/static/app.js
node --check apps/web/static/workbench-api.js
git diff --check
```

Vor einem Serverstart:

```bash
/c/morphic_v1/.venv/Scripts/python.exe -c "import socket; out={}; [(lambda s,p:(out.__setitem__(p,s.connect_ex(('127.0.0.1',p))==0),s.close()))(socket.socket(),p) for p in (8000,8001,8002,8090)]; print(out)"
```

Port 8090 nicht verändern.
