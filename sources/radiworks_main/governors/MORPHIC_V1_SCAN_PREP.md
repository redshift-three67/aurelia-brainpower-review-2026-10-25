# morphic_v1 — Read-Only Scan Preparation

Prepared: 2026-09-11T14:47:42+02:00
Target: `C:/morphic_v1`
Mode: preparation only; no scan or mutation has started.

## Observed starting state

- Branch: `master...origin/master [gone]`
- HEAD: `411ff09`
- Modified tracked files and untracked roots are present.
- The working tree contains potentially sensitive runtime/history/export material and a local virtual environment.

## Scan contract

The eventual scan must be read-only and begin with a new live Git-status, branch, HEAD, and path inventory. It must exclude content inspection of at least `history/`, `Benutzer_Archive/`, `_test_top3scan_tmp/`, logs, virtual environments, secrets, runtime outputs, and external reference copies. It must not launch tests, servers, CLI workflows, hardware paths, or browser flows.

The scan report must distinguish source evidence, historical documentation, ignored/runtime boundaries, and unverified runtime claims. It must not treat the missing remote branch as a reason to reset, clean, or alter local work.

## Entry criterion

Radi144's protected `project_memories/` snapshot now exists outside the source repository and has a verified two-file hash manifest. The next orchestrated action may therefore be a separate, read-only morphic_v1 source/status scan.
