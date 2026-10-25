# RadiWorks Personal Runtime Implementation Plan

> For agentic workers: apply the existing TDD and verification workflow task by task; no recursive delegation.

**Goal:** One isolated CPU child per personal job instead of per21-rate block; unchanged complete rates, formulas,80000 candidates/rate,1CPU thread and job-local RNG. Preserve incrementally reported progress and strict cancellation/recovery.
**Architecture:** Keep the existing oneshot worker as a compatibility/reference path. New stream mode reads one frozen job input, emits bounded sequential21-rate result frames and a final completion frame, then exits. A separate owner handles bounded binary pipes, exactly one stdout reader, writer and stderr drain with confirmed cleanup. Controller commits each validated prefix block; final block only after the completion frame, EOF and zero process exit. No child reuse between jobs.
**Stack:** Existing Python standard library IPC, pinned Torch/NumPy CPU dependencies, SQLite ledger and pytest. Isolated runtime copy; no Git mutation because the discovered Git root is the user profile.

## Ownership and preserved baseline
Candidate runtime/rw-performance-v2-20261007 only. Baseline178file manifest bae4872ad61ac533b19cf596e3a8c670bec1ce0efa6ff038b2e96a9eda1973f4; prior rollback checkpoint checkpoints/RadiWorks-Clear-Abschluss-20261007-212228. Current8112 and8103-8109 remain unchanged during implementation.

## P1 – Tests before implementation
- [x] Add tests under engine/tests/test_personal_stream.py and update affected behavioral controller tests. Confirm the current implementation fails the one-process/multiblock or stream requirement.
- [x] Test real Python child fixtures for partial/missing newline, malformed UTF8/JSON, oversized/duplicate/extra frames, early EOF, nonzero exit, timeout while input cannot be written, cancel and cleanup. Fake numerical replies only in protocol tests; numerical parity must use real80000-candidate calculations.
- [x] Verify cancellation before delayed reply never stores it; source drift before final commit fails; final completion must await clean process exit.

## P2 – Owned bounded stream transport
Files: engine/src/radiworks/core/personal_stream.py (new), personal_controller.py (modify), personal_worker.py (modify), tests named above.
- [x] Define MAX_INPUT_BYTES12MiB including UTF8/newline, MAX_OUTPUT_FRAME_BYTES256KiB and at most2 buffered frames. Serialize once per job. Never inherit keys; preserve hidden child creation and1-thread environment.
- [x] Writer uses a deadline covering input delivery. One stdout reader uses bounded byte line reads and a bounded queue; stderr drains with bounded retained data and no payload logging. Reader, writer, drains must stop and join after confirmed child exit. Do not call communicate() concurrently with readers.
- [x] Controller owns the child until confirmed exit; kill/wait on timeout or cancellation, close pipes, join readers. Cleanup failures do not report success or release unknown ownership.

## P3 – Job stream and commit rules
- [x] Worker mode reads one frozen input and computes existing rank_personal_block(input, range(start,min(start+21,total))) without altered numerical operations. Emit rows in input order and final {done: total}; stop on source hash drift/errors.
- [x] Root checks implementation hash before launch, every block and immediately before ledger append; preserve generation checks. Own block timeout remains120s, including first input write/start. No transparent retries/restarts/replay.
- [x] Buffer the last rows frame; accept only expected completion count, EOF, zero exit and confirmed thread cleanup before final append/completed. Prefix rows remain incomplete and not exposed as completed tables on failure.

## P4 – Verification
- [x] Run personal_store/lifetime/controller/analysis/stream tests with PYTHONPATH=<candidate>/engine/src;<pinnedDeps>, RADIOWORKS_EXP1_TEST_DEPS=<pinnedDeps>, OMP_NUM_THREADS=1,MKL_NUM_THREADS=1 and existing venv python -m pytest.
- [x] Independently compare >=24 real rates across two blocks for seeded0, another seed and frozen stochastic input. Require exact row values against oneshot baseline; retain80000 candidates/rate. Track elapsed time, child count and owned child/thread cleanup.
- [x] Verify numerical implementation files remain byteequal; current user records/homes unchanged; review consequential IPC/lifetime decisions with Astra6/medium. Expand tests for concrete review findings only.

## P5 – Candidate acceptance boundary
- [x] Build manifest and controlled isolated development service only after tests/review. Existing8112 can be promoted only at explicit idle gate with same home/key/scope, preserved receipt bytes, checkpoint and graceful exit. Do not terminate new user jobs silently.
- [ ] Operator verification before R6. Technical live-browser verification passed. Audio and5 image layers are separate approved work packages following CPU stability; no early persistent/Start5 rollout. S4.8 remains0%.

## Consolidated follow-on requests
Server random default is configuration, not a third random algorithm. Keep persisted/default compatibility; prefer two explicit UI choices and display adopted effective mode. Audio profiles: independent versioned optional adapter, original event audio preserved, fixed432/528/429.62Hz and user-confirmed Solfeggio sequence, pink noise/Phi/Fibonacci parameters documented; own noise RNG and safe master stop/level, no automatic GV frequency mapping. Up to5 fall-owned image layers, separate from analytical focus image, sanitized stored image refs and immutable profile binding for each new broadcast. Verify both before R6/source/Modul_Templates/Start5 update and consistent backup.

Verified outcome: docs/verification/RADIWORKS_PERSONAL_RUNTIME_2026-10-07.md. Live candidate184files ad3c06f9f4a42d1864b10ca0665a7598d8e70e5ae0908f2cf3c51fad6bba4c20. Full1382probe186.220s;3exact24-rate parityprofiles;78Personal/API+88OriginalAPItestsPASS. NoR6/Start5rollout.
