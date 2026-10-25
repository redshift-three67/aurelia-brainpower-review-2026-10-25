# S3a verification — 2026-09-17

Approved design: `../superpowers/specs/2026-09-17-dependent-change-design.md` (operator: “Bestätigt!”).

- Initial 10 preview tests failed because the new module did not exist; implemented after this red check.
- Initial protected HTTP test failed 404 versus expected 400 before adding the endpoint; both endpoint tests then passed, including a real temporary pilot/journal.
- Final scoped regression: **72 tests, 71 passed, one skipped, zero failures**, 22.457 seconds. Full log: `S3a_2026-09-17_unittest.log`. Modules: test_change_chain_preview, test_execution_policy, test_plans, test_change_chain, test_test_chains and three targeted ServerTests preview cases. This is not a rerun of the entire application suite.
- New preview tests cover canonical A→B binding, unchanged DB/files and zero dispatch, unchanged dependency execution denial, invalid selection/shape, same/case/prefix path overlap, absent new files, external receipt withdrawal, source/selection/adapter/root drift, active independent allowlist, empty journal, prior transition exclusion, oversized/nonregular sources and sanitized errors.
- `node --check governor_workbench/static/app.js` passed.
- Chromium component check used the actual `showChangeChainPreview` source with synthetic API responses: exact two selections, conditional order, text escaping, no start control, pending-response invalidation, blocked reasons and close during request. Four requests, all preview-only; zero page errors. Script: local temporary `playwright-test-s3a.cjs`. No live source or job mutation.

Scope limitation: preview only, no automatic source rebase or test inheritance. No S3b transition journal or S3c dependent apply. Observations are not an OS/filesystem snapshot. Ubuntu/SMB/restore and first-module production acceptance remain separate.

Local activation: checked zero active jobs/test chains/sequences and auto_review=false, stopped/restarted Governor with existing scripts. The new protected endpoint returned `missing_plan` and execution_authorized=false for a deliberately nonexistent candidate using the real session/CSRF flow. Active jobs remained zero; automatic reviews remained disabled. The skipped regression is the host's unavailable directory-symlink creation. JSON operating contract syntax also passed.
