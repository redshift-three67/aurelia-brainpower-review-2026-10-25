# RadiWorks Journal-Writer Performance Implementation Plan

> For agentic workers: test-first, bounded worker implementation with independent Astra review. No recursive delegation.

**Goal:** Reduce measured fall-bound Stochastic latency while keeping exact original analysis/draw semantics and existing recovery format.
**Architecture:** A scoped append writer reuses one file handle only during one API analysis computation. Flush each fully written encrypted record before cursor advancement. Close on success or exception, poison a failed writer, no blind retry. fsync remains at the existing commit call. Other entry points retain bounded open/close behavior; no new global handle ownership or app shutdown dependency.
**Tech Stack:** Existing Python, FastAPI, cryptography/Fernet, pytest; original Windows venv. Candidate runtime/rw-journal-20261004 only.

Operator approved the previous report's isolated optimization and failure/restart tests. The scoped writer is a narrower realization of the recommended reusable writer. Alternate whole-provider lifetime requires many ownership/shutdown changes; RAM buffering would weaken per-record visibility. Both are excluded. No settings, scope/case contracts, algorithms, keys, live processes, original source or template changes.

- [x] Root benchmark frozen old writer: identical synthetic records, encryption, append, commit and digest separately; save machine-local proof.
- [x] Luna owns only candidate entropy_journal.py, entropy.py, api/routes.py and new test_journal_writer.py. Tests first: reader visibility, cursor/digests/old format, one file open in scope, reopen after close, nonnested ownership, abort, short write, flush/fsync/close faults, Windows rename/delete. Observe RED before implementation.
- [x] Implement scope forwarding through EntropyProvider and wrap ONLY analyse_rate_list + check_general_vitality in /analysis. Keep existing commit location after successful computation. Seeded paths remain no-op. Scope must close before return and every error; no persistent handle/GC cleanup dependency. No new raw seed export.
- [x] Root run comparable candidate benchmark and frozen-baseline seeded/result comparison. No algorithm changes; Fernet ciphertext differs naturally between encryptions.
- [x] Astra reviews actual diff independently for persistence, lifecycle and concurrency boundaries; repair material findings with targeted checks.
- [x] Full candidate engine suite and browser regression. Real HTTP Stochastic + restart, using prior camera-derived encrypted synthetic seeds and replayed OS seeds for exact result equivalence; no new camera activation or real key.
- [x] Verify 134 original files and seven live PIDs/pings unchanged; save bounded checkpoint/manifest and update report/resume. Candidate only, no live activation or Aurelia gate.

Bench script and integration proof belong to root; worker must not touch these or any live resources. Explicit scope use is serialized by existing case mutation lock; unsafe nested/concurrent use of one writer is rejected. Multiple independent API journal objects remain separate; no claim of multiwriter locking on the same path.

Diagnostic result before implementation: 12000 records, Fernet-only0.108s, old append6.513s. Strict same-ciphertext I/O control: open/close2.558s vs retained-handle/flush0.065s, byte-identical output. Both one-trial machine-local observations.
