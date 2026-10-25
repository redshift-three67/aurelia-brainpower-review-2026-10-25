# Copy-Paste Resume Prompt

```text
Continue the F5-B/v10 work exactly from the verified pause point after Gate M3.

Workspace:
- Worktree: C:\morphic_v1\.worktrees\operator-workbench-phase1
- Branch: operator-workbench-phase1
- Expected HEAD: 619a1f5485a151816e32732929a6a823839ccb57
- Base branch: master
- F5-B is still NO-GO.

Read these files in exactly this order before changing anything:
1. CLAUDE.md, if present.
2. docs/developer-current-state-2026-07-16/README.md
3. docs/developer-current-state-2026-07-16/01_TIEFENANALYSE_AKTUELLER_STAND.md
4. docs/developer-current-state-2026-07-16/02_AKTUELLE_PLANUNG_UND_PAUSEPUNKT.md
5. docs/developer-current-state-2026-07-16/03_VERIFIKATION.md
6. .hermes/plans/2026-07-13-feedback-f-admin-catalog-repositories.md
7. docs/session-handoffs/2026-07-16-m3-b1-pause/README.md
8. docs/status/2026-07-16-feedback-f-F5-B-v10-M3-v7-backup-migration.md

Before planning or editing, independently verify:
- current working directory, branch, HEAD and concise Git status;
- the live hashes of config/source_repositories.json and data/remedies.db;
- MORPHIC_ADMIN_STAGE_KEY is unset and no productive stage key exists;
- port 8000 is free and Radi144 remains on 127.0.0.1:8090;
- no product authority, production backup, ShadowCopy, registry or remedy DB
  was mutated.

Important completed state:
- A0, M1, M2 and M3 are technically closed; F5-B remains NO-GO.
- M3 added migrate_catalog_backup_v7_to_v8() in core/admin_catalog/backup.py.
- M3 accepts only exact verified v7 bundles, creates a fresh v8 bundle and
  leaves the source byte-identical.
- The M3 temp name is exclusively preclaimed with open("xb"). This is not the
  final durable publication solution.
- Gate B1 is next. It must use or extract the existing SourceRegistry durable
  filesystem authority; it needs handle-bound SQLite temp output, a completion
  record, safe bundle publication, restore through the same boundary, and
  parent/temp-swap plus flush fault contracts.
- Do not make normal restore accept v7.
- The post-M3 full suite is green: 1061 passed, 8 skipped in 207.23s.
- Baseline test repairs added a dynamic consent test clock and a test-only
  reset of the global web rate-limit store. Production rate limiting is not
  changed.

Non-negotiable constraints:
- Do not modify Radi144 at 127.0.0.1:8090.
- Treat config/source_repositories.json and data/remedies.db as read-only.
- Do not create/use a production stage key, backup or ShadowCopy.
- Do not commit, stage, merge, push, create a PR, delete worktree files, or
  change Git configuration without explicit user permission.
- The worktree is intentionally dirty with extensive unrelated WIP. Never
  revert or clean it.
- Use the required skill workflow before any task. For B1, begin with
  brainstorming/design approval, then a written implementation plan, TDD and
  root-cause debugging. Keep changes minimal and fail-closed.

After verification, report any drift or blocker. If there is no drift, begin
the B1 design discussion. Do not implement B1 until the design is approved.
```
