# Technical Production GO Recovery Design

**Date:** 2026-07-21
**Worktree:** `C:\morphic_v1\.worktrees\operator-workbench-phase1`
**Branch:** `operator-workbench-phase1`
**Status:** User-approved design

## Goal

Restore the interrupted Operator Workbench work to a technically defensible production GO before discussing or implementing Gates 1-16 of the broader correction plan. The GO must be based on the exact current worktree bytes, complete verification, independent review, and live acceptance on port 8765.

## Scope

This recovery closes the remaining Gate-0 durability and idempotency gaps without adding product features or changing scoring, profile, EMF, report, or harmonization semantics.

In scope:

- Mandatory idempotency for scan and harmonization starts.
- Cross-process atomic start-operation claims.
- Replay before mutable preconditions or mutations.
- Recovery when a job exists but claim completion was interrupted.
- Safe operation-ID retention across uncertain failures.
- Durable publication through `apps/web/durable_io.py`.
- Scan and harmonization parity tests.
- Full Python, JavaScript, and browser verification.
- Exact-byte freeze, two independent zero-finding reviews, and live acceptance on port 8765.

Out of scope:

- Gates 1-16 and their new functionality.
- Score or ranking formula changes.
- Catalog promotion, online adapters, or automatic source activation.
- Destructive worktree cleanup, reset, broad staging, or implicit commit.
- Real client data.

## Architecture

- `apps/web/start_operations.py` is the authority for durable idempotency claims.
- `apps/web/durable_io.py` is the shared atomic publication primitive.
- `apps/web/scan_jobs.py` must adopt or reload a persisted deterministic job before any new process can be spawned.
- Scan and harmonization endpoints use the same required idempotency contract.
- The browser retains operation authority whenever the server may have committed the operation.
- Existing persisted formats remain compatible unless a failing test proves a format change is necessary.

## Start And Replay Flow

1. The client creates and persists an operation ID.
2. The server acquires the cross-process lock for that operation.
3. A completed claim replays before mutable validation or mutation.
4. A pending claim resolves its deterministic job ID from memory and then durable storage.
5. A found durable job is adopted, the claim is completed, and the existing job is returned.
6. A new job may be created only when no claim or durable job proves an earlier commit.
7. Payload mismatch, record corruption, timeout, and response loss preserve retry authority.
8. Unrecoverable corruption fails closed with an explicit conflict and never silently creates a second job.

The recovery contract must hold after a restart and between independently running service instances.

## Error Handling

- Persistence and lock failures fail closed.
- Corrupt or mismatched operation records return a conflict response.
- Client-side operation IDs are cleared only when the response proves that no server-side commit occurred.
- Unknown or ambiguous failures retain the operation ID for replay.
- Recovery must not duplicate productive group activation, scan workers, or harmonization workers.

## Verification

Implementation follows TDD:

1. Add failing regression tests for a durable job with a pending claim, independent services/processes, response loss, corruption, and scan/harmonization parity.
2. Apply the smallest production changes that make the focused tests pass.
3. Run focused Python tests.
4. Run the complete Python suite.
5. Run JavaScript syntax checks and the complete browser matrix.
6. Re-run the affected ladder after every later product patch.
7. Create a complete SHA-256 freeze for the exact current technical scope.
8. Obtain two independent reviews with start/end drift zero and `P0=P1=P2=P3=0`.

Historical freezes and test results are evidence only. They do not validate the current bytes.

## Live Acceptance

Only after tests and reviews pass:

1. Re-check hashes, ports, interpreter, runtime roots, and rollback command.
2. Start the worktree server on port 8765.
3. Verify health and runtime identity.
4. Verify the dynamic profile catalog returns HTTP 200 and authoritative profiles.
5. Verify scan start and replay with synthetic data.
6. Verify the Workbench and report flow through API and browser smoke tests.
7. Record post-state evidence and the exact recovery point.

Any failed live check returns the project to NO-GO.

## GO Criteria

Technical production GO requires all of the following:

- Remaining Gate-0 findings are closed in current code and tests.
- Focused, full Python, JavaScript, and browser verification passes.
- The current exact-byte freeze is complete and drift-free.
- Two independent reviews report no P0-P3 findings.
- Port 8765 serves the reviewed worktree and passes live acceptance.
- Rollback and recovery evidence is current.

No Git commit is part of this design unless the user explicitly requests one.
