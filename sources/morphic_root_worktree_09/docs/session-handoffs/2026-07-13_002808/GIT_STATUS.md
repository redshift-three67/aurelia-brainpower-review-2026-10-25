# Git-/Arbeitsbaumstatus bei Übergabe

**Erhoben:** 2026-07-13 00:28
**Worktree:** `C:\morphic_v1\.worktrees\operator-workbench-phase1`
**Branch:** `operator-workbench-phase1`
**HEAD:** `619a1f5 docs: mark feedback point d) Phase 5 complete, next up is point e)`

## Schutzvermerk

Der Arbeitsbaum ist absichtlich sehr umfangreich modified/untracked. Der Status umfasst frühere Operator-Workbench-/Phase-E-Arbeit sowie zahlreiche `Benutzer_Archive__ws-*`-Verzeichnisse. Diese Übergabe ist keine Aufforderung zur Bereinigung.

Verboten ohne ausdrückliche Nutzerfreigabe:

- `git reset`, `git clean`, pauschales Restore oder Checkout;
- Staging, Commit oder Push;
- Löschen oder Durchsuchen der zahlreichen Archive als vermeintliche Testbereinigung;
- Veränderung bestehender Ports/Prozesse, insbesondere Port 8090.

E5.10E-relevante neue/geänderte Pfade:

- `core/compliance/group_activation_runtime.py`
- `apps/web/group_analysis_runtime.py`
- `apps/web/contracts.py`
- `apps/web/main.py`
- `apps/web/scan_jobs.py`
- `apps/cli/commands/scan.py`
- `apps/cli/commands/field.py`
- `tests/test_group_activation_runtime.py`
- `tests/test_field_group_activation_runtime.py`
- `tests/test_topn_group_activation_fanout.py`
- `tests/test_scan_job_private_environment.py`
- `tests/test_web_group_productive_activation.py`
- `tests/test_group_e510_release_gate.py`
- `tests/test_group_vector.py`
- `.hermes/plans/2026-07-13-e510e-local-productive-group-integration.md`
- `docs/status/2026-07-13-e510e-local-productive-group-integration-gate.md`

`git diff --check` war bei Übergabe Exit 0; es bestanden nur bekannte LF→CRLF-Hinweise. Den vollständigen Live-Status in der nächsten Session erneut mit `git status --short` erheben.
