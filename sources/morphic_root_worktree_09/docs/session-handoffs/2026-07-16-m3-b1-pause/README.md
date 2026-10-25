# Session Handoff: F5-B/v10 After M3

## Read This First

This file records the exact verified pause point after Gate M3. It is an
operational handoff, not a release approval.

- Date: 2026-07-16
- Worktree: `C:\morphic_v1\.worktrees\operator-workbench-phase1`
- Branch: `operator-workbench-phase1`
- HEAD: `619a1f5485a151816e32732929a6a823839ccb57`
- Local base branch: `master`
- Merge-base with `master`: `e87cee3e509b0855cfa1249bc63c3bfca45b84c8`
- Overall F5-B status: **NO-GO**
- Closed technical gates: A0, M1, M2, M3
- Next binding implementation gate: B1, shared durable backup publication
- Git integration: no commit, staging, merge, push, PR, backup, ShadowCopy, or
  production authority mutation was performed in this session.

The worktree is intentionally dirty and contains extensive pre-existing WIP.
Do not revert, clean, stage, delete, or otherwise modify unrelated changes.

## Exact Current State

### Gate M3 Is Technically Closed

M3 now provides:

```python
migrate_catalog_backup_v7_to_v8(
    source_backup_root: str | Path,
    target_backup_root: str | Path,
) -> Path
```

The API is implemented in `core/admin_catalog/backup.py` and accepts only an
exact historical v7 backup bundle. It creates a new complete v8 backup bundle
and never mutates the v7 source bundle.

The accepted v7 bundle is constrained to:

- exactly `catalog.sqlite3` and `manifest.json`;
- backup manifest version 1;
- `catalog_schema_version == 7`;
- the documented database filename, byte count and SHA-256;
- `no_productive_activation == true`;
- no reparse components or SQLite WAL, SHM, or journal sidecars;
- a valid SQLite integrity check;
- historical v7 schema fingerprint
  `e8bcf21ff2317c82e8fd142abf46b6ca9ac1169c7738767c2553ede06e6e0d21`.

The normal `restore_catalog_backup()` path still accepts v8 only. M3 does not
silently teach regular restore to accept v7.

### M3 Flow

1. Validate source and target absolute-path, no-reparse and no-overwrite
   boundaries.
2. Validate the v7 bundle manifest, exact files, sidecar state, hash, size,
   SQLite integrity and exact v7 schema fingerprint.
3. Generate a UUID snapshot path in the target parent and reserve it
   exclusively with `open("xb")`.
4. If that generated path is already occupied, raise `FileExistsError` before
   SQLite opens it and do not delete the foreign artifact.
5. Use the existing SQLite backup API to create an owned temporary snapshot.
6. Verify the snapshot has the source manifest hash and byte count.
7. Invoke M2 `migrate_catalog_v7_to_v8()` on the snapshot.
8. Verify no sidecars, SQLite integrity and exact current v8 schema.
9. Invoke existing `create_catalog_backup()` to create the fresh target v8
   bundle and manifest.
10. Remove only the exclusively reserved temporary snapshot and its sidecars.

### M3 Source Files

- `core/admin_catalog/backup.py`
  - `_V7_CATALOG_SCHEMA_FINGERPRINT`
  - version-aware `_load_manifest(..., expected_catalog_schema_version=...)`
  - `_assert_v7_catalog_schema()`
  - `migrate_catalog_backup_v7_to_v8()`
- `core/admin_catalog/migration.py`
  - imports the single v7 fingerprint authority from `backup.py`; the local
    duplicate literal was removed.
- `tests/admin_catalog_v7_fixture.py`
  - deterministic historical v7 database and backup-bundle fixture.
  - explicit SQLite connection cleanup plus `gc.collect()` before seed deletion
    is required on Windows because the sqlite extension may retain native
    handles in cycles.
- `tests/test_admin_catalog_v7_backup_migration_contract.py`
  - 14 M3 contracts.

### M3 Review History

The initial focused M3 review found P1: a UUID name alone did not prove that
the temporary snapshot was owned. A foreign process could preclaim the guessed
name before SQLite opened it.

Fix implemented and tested:

- the snapshot is exclusively reserved with `open("xb")`;
- cleanup is conditional on successful reservation;
- a contract preclaims a deterministic generated temp name and proves that it
  remains byte-identical while M3 fails closed;
- re-review result: `APPROVED`, no P0-P3 findings.

Residual boundary, intentionally not claimed as solved by M3:

- Gate B1 must implement the stronger shared durable filesystem authority:
  handle-bound SQLite temporary output and publication, completion record,
  parent/temp-swap and directory-flush fault contracts.
- A path replacement after successful M3 reservation remains a B1 concern.

## Baseline Repairs Performed After M3

The first whole-project test run found 14 unrelated failures. Both causes were
reproduced, diagnosed and repaired without changing production behavior.

### Stale Consent Test Time

`tests/test_group_member_consent_revocation.py` had fixed
`NOW = 2026-07-12T12:00:00+00:00`. On 2026-07-16, its setup expiry was already
past and the production fail-closed check correctly rejected it.

Repair:

```python
NOW = datetime.now(UTC)
```

The test still controls its later expiry check through its injected clock.

### Global Web Rate-Limit State Between Tests

`apps/web/security.py` intentionally has a process-global in-memory
`_rate_limit_store` keyed by IP. The production process has one web app, but
the test suite creates many apps in one process, all using loopback. After 60
requests, later unrelated tests received HTTP 429. Affected test isolated in a
fresh process passed.

Repair:

`tests/conftest.py` contains an autouse fixture that clears
`_rate_limit_store` before and after every pytest test. The production
middleware and rate limit are unchanged.

## Verification Evidence

All commands below used:

```powershell
& "C:\morphic_v1\.venv\Scripts\python.exe" -X utf8 -m pytest ... -q -p no:cacheprovider
```

### Targeted M3 Evidence

```text
tests/test_admin_catalog_v7_backup_migration_contract.py
14 passed in 1.91s

M3 + M2 + v8 backup focus matrix
59 passed, 1 skipped in 7.54s

Admin Catalog matrix
288 passed, 5 skipped in 28.07s
```

### Baseline Repair Evidence

```text
tests/test_group_member_consent_revocation.py
7 passed in 0.56s

tests/test_web_shell.py
tests/test_web_workbench_runtime.py
tests/test_workbench_client_context_persistence.py
32 passed in 3.11s
```

### Fresh Whole-Project Evidence

```text
1061 passed, 8 skipped in 207.23s (0:03:27)
```

### Static Checks

- `py_compile` passed for M3 source and test files.
- Ruff passed for M3 files and for baseline repair files.
- `git diff --check` exited 0. It emitted only pre-existing LF-to-CRLF warnings
  in unrelated WIP files.
- Ruff is not installed in the project venv. Use:

```powershell
& "C:\Users\Hubert111\AppData\Local\Programs\Python\Python312\Scripts\ruff.exe" check <paths>
```

## Authority And Safety Constraints

Do not weaken or bypass these constraints in the next session:

- F5-B is still **NO-GO**.
- Do not modify Radi144 on `127.0.0.1:8090`.
- Treat `config/source_repositories.json` and `data/remedies.db` as read-only.
- Do not create or use a productive stage key.
- Do not create production backups or ShadowCopies.
- Do not commit, stage, merge, push, create a PR, or change Git configuration
  without explicit user approval.
- Do not revert or clean the dirty worktree. It contains user and other-agent
  changes outside the M3 scope.
- Prefer minimal, fail-closed changes. Use TDD and root-cause debugging for
  every failure.
- Keep M3 source output immutable. Do not alter normal v8 restore semantics.

Last previously recorded live authority values were:

```text
Source registry SHA-256:
6c93c5a1aab9b022bf22e3a8c8097b07bde2738efec3678645ffadf849e4a0b3

Remedy database SHA-256:
c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0
```

Recompute, do not merely trust, those values before starting B1.

## Required Reading Order At Resume

1. `CLAUDE.md`, if present in the active worktree.
2. `docs/developer-current-state-2026-07-16/README.md`.
3. `docs/developer-current-state-2026-07-16/01_TIEFENANALYSE_AKTUELLER_STAND.md`.
4. `docs/developer-current-state-2026-07-16/02_AKTUELLE_PLANUNG_UND_PAUSEPUNKT.md`.
5. `docs/developer-current-state-2026-07-16/03_VERIFIKATION.md`.
6. `.hermes/plans/2026-07-13-feedback-f-admin-catalog-repositories.md`.
7. This handoff and `RESUME_PROMPT.md` in the same directory.
8. M3 completion evidence:
   `docs/status/2026-07-16-feedback-f-F5-B-v10-M3-v7-backup-migration.md`.

The original developer planning package has historical M3 wording and a stale
copy-paste resume paragraph. Use it for the authoritative gate definitions;
use this handoff and the current status documents for what has been completed.

## Next Work: Gate B1

Do not implement B1 immediately after reading this document. First verify the
worktree and all authorities, then use the required brainstorming/design and
planning workflow.

Gate B1 from the binding planning document requires:

1. Reuse or deliberately extract a common durable filesystem authority from
   `core/source_registry.py`; do not create a second independent security
   implementation.
2. Write and verify temporary SQLite snapshots through a held handle.
3. Publish database, manifest and a final completion record as one bundle
   protocol.
4. Treat only that completion record as authority for a consumable backup.
5. Publish restore output through the same boundary.
6. Never path-delete a potentially foreign target after a post-publish error.
7. Add parent-swap, temp-swap, concurrent-exists and directory-flush fault
   contracts.

The M3 exclusive `xb` reservation is only a preclaim defense. B1 must resolve
the stronger post-reservation path-identity and durable publication boundary.

## Current Integration Decision

The user has not selected an integration option. The last offered choices were
merge to `master`, push a PR, keep the branch, or discard. Preserve the branch
and worktree until the user explicitly chooses one.
