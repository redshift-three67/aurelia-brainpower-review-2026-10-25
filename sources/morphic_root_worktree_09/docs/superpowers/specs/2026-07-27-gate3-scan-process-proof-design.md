# Gate 3 Scan Process Proof Design

**Date:** 2026-07-27
**Status:** Approved design, pending implementation
**Scope:** Private Web-to-process-gate-to-CLI fingerprint binding

## 1. Goal

Prove that a scan started by the Workbench carries the operator-confirmed scan
profile pool fingerprint through the real local process gate into the real
`scan top3-scan` CLI entry point. A gate-bound CLI process must reject a missing,
changed, or incompletely bound fingerprint before profile activation or the
first subscan.

The proof must remain private. The fingerprint, proof nonce, proof digest, and
their environment variable names must not appear in command arguments, HTTP
responses, persisted public job state, start-operation records, run traces,
stdout, or stderr.

## 2. Threat Boundary

This design protects the application-internal process boundary and accidental
or stale environment propagation. It does not attempt to defend against a
malicious process running as the same operating-system user, because such a
process can construct arbitrary environment values and control the local Python
runtime.

`MORPHIC_SCAN_GROUP_TOKEN` remains process-tree recovery authority only. It is
persisted as part of the existing recovery contract and therefore must not be
used to identify a gate-bound CLI invocation.

## 3. Selected Design

The process gate creates a one-shot proof only after the release authority is
visible and immediately before spawning the productive CLI child.

The proof consists of:

- a cryptographically random 256-bit nonce;
- a SHA-256 digest over a versioned domain separator, the nonce, and the private
  scan profile pool fingerprint.

Shared private constants define the nonce and digest environment variable
names. The proof values are never added to the job model and are never passed
to persistence code.

The existing fingerprint environment value reaches the process gate through
the already private `env_overrides` path. The gate reads it only to construct
the one-shot binding and passes the fingerprint, nonce, and digest to its single
productive child through that child's environment.

## 4. CLI Contract

`scan top3-scan` removes the fingerprint, nonce, and digest environment values
as its first productive action. Validation occurs before pool resolution,
profile activation, export-root creation, or any subscan.

The accepted states are:

1. No nonce and no digest: direct CLI mode. A fingerprint may remain optional
   under the existing direct-CLI contract.
2. Nonce and digest both present: gate-bound mode. The fingerprint is required,
   all three values must be syntactically valid, and the digest must match the
   versioned nonce/fingerprint binding using constant-time comparison.

All partial proof combinations, malformed values, a missing fingerprint in
gate-bound mode, or a mismatched digest fail with the existing generic profile
authority error and a nonzero exit code. They must not expose the rejected
values, internal environment names, or a traceback.

The presence of `MORPHIC_SCAN_GROUP_TOKEN` alone has no effect on this decision.

## 5. Process And Data Flow

1. The Workbench confirms the current pool fingerprint before reserving a start
   operation or creating a scan job.
2. `LocalScanJobService` supplies the fingerprint only through private child
   environment overrides when it creates `scan_process_gate.py`.
3. The gate waits without spawning the productive CLI until the release file is
   published.
4. After release, the gate generates the nonce and digest in memory and starts
   exactly one productive child with the private proof triplet.
5. The CLI removes and validates the triplet before all scan side effects.
6. The CLI removes the fingerprint from every environment passed to later
   subscans.

No proof recovery is required. If the gate process terminates before spawning
the CLI, the one-shot proof disappears with that process. Existing process-tree
recovery continues to use its separate token and authority files.

## 6. Error And Cleanup Contract

- Gate proof generation failure exits the gate nonzero without starting the CLI.
- CLI proof validation failure exits generically before activation and subscan.
- Timeout handling must terminate or stop the real process authority. A test
  timeout must not rely on a non-cancellable executor thread whose context
  manager can wait forever.
- Tests use condition-based waits with finite deadlines and `finally` cleanup.
- Temporary release, started, result, log, state, trace, and probe files are
  scanned for private-value leaks before cleanup.

## 7. Required Tests

### Positive integration

Use the real in-process Web endpoint, real `LocalScanJobService`, real
`scan_process_gate.py`, and actual `apps.cli.main scan top3-scan` entry point.
Only the expensive downstream `field multiplex-scan` execution may be replaced
after the actual CLI subscan command is observed.

Prove that:

- the productive CLI does not start before gate release;
- matching authority reaches the CLI and is removed before activation;
- the first real subscan command is attempted without the proof triplet;
- no private value or variable name leaks through public or persisted surfaces.

### Negative integration

Prove separately that missing fingerprint, mismatched fingerprint, malformed
nonce, malformed digest, partial proof, and tampered binding fail for the exact
generic authority reason before activation, export creation, or subscan.
An exit-time probe must confirm that all proof values were removed from the CLI
environment on these paths.

### Compatibility

Prove that:

- direct CLI without proof remains valid under its existing contract;
- an artificial `MORPHIC_SCAN_GROUP_TOKEN` without the one-shot proof does not
  activate gate-bound validation;
- proof values and names never enter the persisted job payload.

## 8. Non-Goals

- No defense against an adversarial process running as the same OS user.
- No new public API or CLI option.
- No proof persistence or replay support.
- No change to process-tree recovery authority.
- No execution of the expensive real multiplex analysis in the integration
  suite.
