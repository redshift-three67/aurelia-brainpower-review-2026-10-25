# S3a – Read-only dependent change preview

**Goal:** Diagnose exactly two selected dependent change steps without opening any execution gate.
**Architecture:** A separate read-only observer uses the existing PlanBook dependency report and safe path reader. No synthetic execution permissions, no schema initialization, no worker or model requests. Two fresh observations bind sources, root, selection, predecessor receipts and adapter implementation. UI exposes preview only.
**Tech stack:** Python stdlib, SQLite read queries, vanilla JavaScript.

Approved scope: `docs/superpowers/specs/2026-09-17-dependent-change-design.md`. Inline execution in the existing authorized workspace; preserve unrelated WIP and the parent repository. No commit or worktree migration of the home-directory repository. Medium remains appropriate for safety-sensitive binding semantics.

- [x] Add `tests/test_change_chain_preview.py`: real temporary pilot and journal; A→B canonical preview, no DB/source/job/model effects, missing/withdrawn external receipts, invalid selections, branches, overlaps and path aliases, root/group/archive restrictions, source/adapter drift, missing files, malformed input, sanitized failures and empty journal. Run new tests and observe missing implementation failure.
- [x] Add `governor_workbench/change_chain_preview.py`: `preview(app,candidate_id,step_ids)` returns explicit reason code, structural eligibility, binding hash and conditional B; always execution_authorized=false. Existing transitions require S3b and block. Max 20 paths per step, 1MiB combined source bytes; absent new files bound as null. Case-folded same/prefix scope aliases block. Read-only PlanBook facade, compare two observations. Existing execution_policy unchanged.
- [x] Add protected POST `/api/change-chains/preview`, exactly candidate_id/step_ids; test Origin/cookie/CSRF, extra fields, no dispatch, valid preview with real fixture. No start endpoint.
- [x] Add UI selector under dependency report: exactly two change steps, pending-response revision guard, conditional labels, reason and no start/approval control. Run JS syntax and synthetic browser check against actual app assets.
- [x] Run relevant unittest modules for new preview/API and existing dependency/test/change policies; inspect complete test summary. Document exact tested scope, no full S3 acceptance or live server claim.
- [x] Update developer contract, README and WIEDERAUFNAHME with approved design, S3a evidence and S3b next.

Representative checks: `python -m unittest tests.test_change_chain_preview -v`; `python -m unittest tests.test_server.ServerTests.test_change_chain_preview_is_strict_guarded_and_read_only -v`; existing S1/S2/dependency modules selected by filename. Source state and historical transition validation remain separate; no hidden adapter privilege reuse.

