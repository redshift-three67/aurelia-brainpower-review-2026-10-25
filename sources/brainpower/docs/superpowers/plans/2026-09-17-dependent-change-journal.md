# S3b – Append-only dependent-change evidence journal

**Goal:** Preserve and reconstruct two disjoint changes and last-in-first-out rollback without granting execution.
**Architecture:** New internal journal, separate from legacy plan_scope_transitions. Immutable chain baseline and hash-linked events, SQLite BEGIN IMMEDIATE plus expected-head comparison. Pure reconstruction validates immutable manifest/transaction/technical-receipt snapshots; a separate read-only observation compares only the reconstructed tip to actual files. No HTTP writer, worker dispatch or implicit migration of old receipts.
**Execution:** Inline, approved S3 design; Medium. Existing workspace and unrelated WIP preserved. No external products, server changes or live models.

- [x] Tests first in `tests/test_change_journal.py`: actual temporary files, H0→H1→H2 reconstruction, B-before-A rollback, no revival, immutable rows, malformed/replaced evidence, stale head/concurrent writers, identical retry/conflicting retry, startup/legacy data, adapter/root/file drift and incomplete transaction denial.
- [x] `governor_workbench/change_journal_evidence.py`: validate bounded baseline and evidence snapshots. Bind exact candidate/selection/step/root, before/after scope hashes, sealed manifest, completed transaction and recorded technical receipt; distinguish integrity from authorization. Reject nonterminal evidence and mismatching file maps. No old-current validator reuse for historical state.
- [x] `governor_workbench/change_journal.py`: lazily initialize separate immutable tables. Create baseline, append confirmed transition/rollback snapshots with expected-head CAS and deterministic retry identity. Reconstruct full explicit file map from baseline; reject overlap/third transition/rollback of non-tip/reapply after rollback. No writes to pilot files.
- [x] Read-only `inspect`: history_valid separately from current tip; freshly validate canonical root/identity, explicit files and supplied current context/adapter. Never restore old approvals when bytes return. Hash observations are not a filesystem snapshot or protection from a hostile local DB owner.
- [x] Relevant existing pilot/technical completion/legacy change/S3a regressions; documentation and resumption update with exact results. This journal is an internal integrity layer: S3c must obtain fresh authenticated operator decisions, verify trusted evidence at execution time, reserve the worker and enforce rollback order before physical writes. S3b must not claim those controller obligations implemented.

Checks: `python -m unittest tests.test_change_journal -v`; then scoped legacy pilot, technical completion, change-chain and preview modules. No UI behavior changes, so no new browser test is required for S3b.

