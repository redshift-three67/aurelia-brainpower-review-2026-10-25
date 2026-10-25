# RadiWorks Journal-Writer Performance Implementation Plan

> For agentic workers: test-first, bounded worker implementation with independent Astra review. No recursive delegation.

**Goal:** Reduce measured fall-bound Stochastic latency while keeping exact original analysis/draw semantics and existing recovery format.
**Architecture:** A scoped append writer reuses one file handle only during one API analysis computation. Flush each fully written encrypted record before cursor advancement. Close on success or exception, poison a failed writer, no blind retry. fsync remains at the existing commit call. Other entry points retain bounded open/close behavior; no new global handle ownership or app shutdown dependency.
**Tech Stack:** Existing Python, FastAPI, cryptography/Fernet, pytest; original Windows venv. Candidate runtime/rw-journal-20261004 only.

Operator approved the previous report's isolated optimization and failure/restart tests. The scoped writer is a narrower realization of the recommended reusable writer. Alternate whole-provider lifetime requires many ownership/shutdown changes; RAM buffering would weaken per-record visibility. Both are excluded. No settings, scope/case contracts, algorithms, keys, live processes, original source or template changes.


Acceptance: same results/seeds/order/schema, append visibility, unchanged commit barrier, deterministic resource cleanup and fault rejection, exact HTTP restart, no original/live mutation. Prior approved report docs/verification/ROUTEN_KONSOLEN_KAMERA_2026-10-04.md governs this isolated block.
