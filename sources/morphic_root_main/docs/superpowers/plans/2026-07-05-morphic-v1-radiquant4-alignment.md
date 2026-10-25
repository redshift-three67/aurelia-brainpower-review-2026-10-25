# Morphic V1 → radiquant4 Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> **Approved 2026-07-06** with one sequencing amendment: Task 8 (Design-Token-Übernahme) runs strictly **after** Task 4 of `2026-07-05-morphic-operator-workbench-phase1.md` is complete, not in parallel/during. Tasks 1-3, 5-7, 9 are independent of that dependency and may proceed now.
> **Update 2026-07-06 (evening):** Tasks 1-7, 9 umgesetzt im Haupt-Checkout. Task 8 und Task 2 Schritt 4 nachträglich am 2026-07-06 im Worktree `operator-workbench-phase1` umgesetzt (Operator-Workbench-Task 4 hatte noch nicht begonnen, daher Design-Tokens additiv auf die bestehenden statischen Dateien angewendet - sie werden vom Task-4-Rebuild dann genutzt). Alle 9 Tasks damit erledigt.

**Goal:** Finish `morphic_v1` functionally so it can later be handed to a `radiquant4`-side instance for either standalone release or synergetic integration as/alongside the existing `radimorphic` service — without migrating any code into `radiquant4` itself, and without regressing the in-flight Operator Workbench work.

**Depends on:**
- `docs/superpowers/plans/2026-07-04-apps-web-radi144-workflow-ux.md` / `2026-07-04-apps-web-workflow-stepper-phase2.md` (prior UX work)
- `docs/superpowers/plans/2026-07-05-morphic-operator-workbench-phase1.md` (Tasks 1-3 done in worktree `operator-workbench-phase1`, Tasks 4-6 open)
- `docs/superpowers/specs/2026-07-05-morphic-v1-radiquant4-alignment-design.md` (design rationale for this plan)
- `docs/deep-audit-2026-07-05/RADIQUANT4_RADIMORPHIC_KONTRAKT_REFERENZ.md` (source contract facts)

**Tech Stack:** Python 3.12, FastAPI, Pydantic, Typer, pytest, plain HTML/CSS/JS (no new build tooling introduced by this plan)

---

## Scope Boundary

Included:
- Standard output contract adapter compatible with `StandardAnalysisBlock`
- Substep vocabulary mapping table + event emission for the 12-step workflow
- Deterministic, tenant-/workspace-scoped seed + honest entropy fallback chain
- Quantum path hardening (installable + verifiable `qiskit` path, documented fallback chain)
- Lightweight `operator_id`/`workspace_id` context + ownership checks (P0 from `PHASE_3`)
- Design-token adoption into `apps/web/static/app.css` (values only, no framework change)
- DSGVO hardening: audit actor context, retention purge job
- Test coverage for all of the above

Excluded (see design doc "Nicht-Ziele"):
- Any change to the `radiquant4` server
- Astro/React/Tailwind framework migration
- Real Postgres/Redis/Celery infrastructure in `morphic_v1`
- Actual migration/handover of `morphic_v1` code into `radiquant4`
- Renaming `morphic_v1`'s domain factor tables to match `radiquant4`'s

## File Map

### Create

- `core/compliance/platform_export.py` — builds a `StandardAnalysisBlock`-shaped JSON (module=`"radimorphic"` compatible payload) from an existing scan/multiplex result, additive/non-breaking.
- `core/compliance/operator_context.py` — `operator_id`/`workspace_id` resolution + ownership check helpers (file-based, single-process-safe).
- `core/compliance/entitlement_stub.py` — minimal, swappable interface (`is_module_available(module: str) -> bool`) defaulting to "all available" for standalone use, documented as a future integration seam.
- `core/realtime/seed_generator.py` — deterministic tenant/workspace-scoped seed (SHA-256 of `workspace_id:last_name:first_name:birth_date:birth_place`) + entropy fallback chain wrapper around existing `providers/hardware/entropy_sources.py`.
- `apps/cli/workflow/substep_manifest.py` — mapping table between `morphic_v1`'s 12 steps and `radiquant4`'s 12 substep vocabulary (`profile_resolution` … `export`), used only for documentation/event labeling, not behavior change.
- `tests/test_platform_export.py`
- `tests/test_operator_context.py`
- `tests/test_seed_generator.py`
- `tests/test_substep_manifest.py`
- `tests/test_quantum_real_path.py` (optional-extra gated, see Task 4)
- `docs/deep-audit-2026-07-05/QISKIT_VERIFICATION_LOG.md` — dated record of the one-time real-circuit verification run (Task 4)

### Modify

- `apps/cli/workflow/step11_export.py` — call `platform_export.build_standard_output_block(...)` in addition to existing export, write alongside existing artifacts (new file, e.g. `*_standard_block.json`), never replacing existing output.
- `apps/cli/workflow/step09_quantum.py` — surface `engine.use_quantum` truth (real vs. fallback) into `state`, not just synergy results.
- `core/compliance/runtime_manifest.py` — add `actor` parameter (default `"system"`, overridable) to audit log calls; add a `purge_expired(...)` retention function (no automatic scheduling yet, callable via CLI).
- `apps/cli/commands/privacy.py` — expose new `privacy purge-expired` CLI command wrapping the new retention function.
- `apps/web/static/app.css` — add CSS custom properties block adopting `radiquant4` design tokens (colors, type scale, radius, shadow, motion incl. `prefers-reduced-motion`), applied additively to existing Operator Workbench styles from the in-flight worktree.
- `pyproject.toml` — keep `qiskit` as optional extra, add a documented `make`/`tox`-free command (README snippet) for the one-time verification run.
- `PROJECT_MEMORY/00_CURRENT_STATE.md`, `Entwicklung/03_ROADMAP_STATUS_ERLEDIGT_OFFEN.md` — append this initiative once tasks land (documentation hygiene, per existing drift findings).

### Read During Implementation

- `docs/deep-audit-2026-07-05/RADIQUANT4_RADIMORPHIC_KONTRAKT_REFERENZ.md`
- `docs/deep-audit-2026-07-04/PHASE_3_SICHERHEIT_DSGVO_AUTH_MULTITENANT.md`
- `docs/deep-audit-2026-07-05/PHASE_8_QUANTUM_FRAMEWORK_TIEFENANALYSE.md`
- `docs/deep-audit-2026-07-05/PHASE_9_INNOVATIONEN_ECHTZEIT_UND_QUANTUM.md`
- `docs/superpowers/plans/2026-07-05-morphic-operator-workbench-phase1.md` (for the worktree file layout you must not collide with)

---

### Task 1: Standard Output Contract Adapter

**Files:** Create `core/compliance/platform_export.py`, `tests/test_platform_export.py`; Modify `apps/cli/workflow/step11_export.py`

- [ ] **Step 1: Write failing tests** asserting `build_standard_output_block(scan_result, workspace_id, session_id)` returns a dict with exactly the shape from the contract reference: `{"inputs": {...}, "outputs": {"quality_score", "morphic_field", "holographic_entropy", "remedy_matches": [(name, score), ...]}, "meta": {"timestamp", "source_system": "MORPHIC_V1"}}`, using a representative fixture built from an existing multiplex-scan JSON shape.
- [ ] **Step 2: Run tests, confirm failure** (`ModuleNotFoundError`).
- [ ] **Step 3: Implement** `platform_export.py` as a pure function module (no I/O side effects beyond what callers provide), mapping existing scan/remedy fields onto the target shape. Do not invent fields that have no real source; use `None`/omit rather than fabricate.
- [ ] **Step 4: Wire into `step11_export.py`** as an additional artifact (e.g. `<slug>_standard_block.json`), written after existing exports succeed, wrapped so a failure here never breaks the existing export path (log + continue).
- [ ] **Step 5: Run full test suite**, confirm no regression in existing export tests (`tests/test_report_manifest_registration.py` etc.).

### Task 2: Operator/Workspace Context + Ownership

**Files:** Create `core/compliance/operator_context.py`, `tests/test_operator_context.py`; Modify `apps/web/main.py` (read-only wiring, see step 4)

- [ ] **Step 1: Write failing tests** for `resolve_operator_context(request_or_env) -> OperatorContext(operator_id, workspace_id)` (defaults to a stable local machine/user-derived id when unset) and `assert_owner(resource_owner_id, context) -> None | raises OwnershipError`.
- [ ] **Step 2: Run tests, confirm failure.**
- [ ] **Step 3: Implement** as a small dataclass + two functions, file-based default (e.g. derived from OS username + a generated `workspace_id` persisted once in `data/runtime/workspace_id.json`).
- [ ] **Step 4 (DEFERRED, same gate as Task 8):** Wire into the two highest-risk unauthenticated endpoints identified in `PHASE_3` (`GET /api/reports/{report_id}/file`, `GET /api/scan/jobs/{job_id}/results`) as a **non-breaking, additive** check. **Reason for deferral:** `apps/web/main.py` is actively modified in the `operator-workbench-phase1` worktree (per `Entwicklung/04_AKTIVE_UMSETZUNG_OPERATOR_WORKBENCH.md`); editing it on the main checkout now would create a near-certain merge collision. Do this only after that worktree's Task 4 lands, in the same pass as Task 8.
- [ ] **Step 5: Add regression tests** confirming existing single-operator flows still pass unauthenticated as before (to be added together with Step 4).

### Task 3: Entitlement Stub

**Files:** Create `core/compliance/entitlement_stub.py`, extend `tests/test_operator_context.py` or new test file

- [ ] **Step 1: Write failing test** for `is_module_available(module: str, context: OperatorContext) -> bool` always returning `True` in standalone mode, plus a documented extension point (`set_entitlement_provider(callable)`).
- [ ] **Step 2: Implement** minimal stub; document in module docstring that a future `radiquant4`-aware provider can be injected without changing call sites.
- [ ] **Step 3: Do not wire this into any CLI command gating yet** — this task only establishes the seam, per design doc "Nicht-Ziele" (no fake gating in standalone mode).

### Task 4: Quantum Path Hardening

**Files:** Modify `pyproject.toml`, `apps/cli/workflow/step09_quantum.py`; Create `tests/test_quantum_real_path.py`, `docs/deep-audit-2026-07-05/QISKIT_VERIFICATION_LOG.md`

- [ ] **Step 1:** In an isolated environment (not the shared dev `.venv`, to avoid destabilizing existing OpenBLAS-sensitive tests), install `.[quantum]` and run `core/quantum_synergy/grover_search.py`'s real circuit path against a small synthetic item set (8-16 items).
- [ ] **Step 2:** Write `tests/test_quantum_real_path.py`, marked with `pytest.mark.skipif(not QISKIT_AVAILABLE, ...)` so it stays inert in the default environment and only runs when the optional extra is present.
- [ ] **Step 3:** Record the verification run's result (date, qiskit version, item count, pass/fail) in `QISKIT_VERIFICATION_LOG.md`.
- [ ] **Step 4:** In `step09_quantum.py`, surface `engine.use_quantum` (real vs. classical-fallback truth) into `state.quantum_mode` so it is visible to callers/exports, not just log output.
- [ ] **Step 5:** Update `PHASE_8_QUANTUM_FRAMEWORK_TIEFENANALYSE.md` with a short "Update 2026-XX-XX: real path now verified" addendum once done (do not rewrite the original findings).

### Task 5: Deterministic Seed + Entropy Fallback Chain

**Files:** Create `core/realtime/seed_generator.py`, `tests/test_seed_generator.py`

- [ ] **Step 1: Write failing tests** for `generate_deterministic_seed(workspace_id, last_name, first_name, birth_date, birth_place) -> int` (same inputs → same output, different `workspace_id` → different output) and `generate_seed_with_entropy(..., use_hardware: bool) -> (deterministic_seed, hardware_seed_or_none, samples_or_none, source_label)`.
- [ ] **Step 2: Implement**, reusing `providers/hardware/entropy_sources.py` as the hardware tier, `os.urandom` as final fallback, mirroring the `radiquant4` cascade shape (documented tiers, not identical device set — no Kozyrev/ESP32 hardware present here).
- [ ] **Step 3:** Document the exact cascade order in the module docstring, matching the honesty requirement from `PHASE_9` (no tier claimed if not actually implemented).
- [ ] **Step 4:** Do not replace existing `core/profiles/profile.py` rate-encoding yet — this is an additive, parallel utility for the platform-export path only, to avoid regressing the production scan path.

### Task 6: Substep Vocabulary Mapping

**Files:** Create `apps/cli/workflow/substep_manifest.py`, `tests/test_substep_manifest.py`

- [ ] **Step 1: Write failing test** asserting a mapping table exists from `morphic_v1` step names (`step01_init` … `step12_harmonize`) to the `radiquant4` substep vocabulary (`profile_resolution` … `export`), with an explicit `null`/`"no_equivalent"` entry where no honest mapping exists (do not force-fit).
- [ ] **Step 2: Implement** as a plain data structure (list of dicts), consumed only for documentation/labeling — no behavior change to the orchestrator.
- [ ] **Step 3:** Reference this mapping from `RADIQUANT4_RADIMORPHIC_KONTRAKT_REFERENZ.md` (append a short cross-reference section) so both audiences (this repo and any future `radiquant4`-side reader) share one source.

### Task 7: DSGVO Hardening (Audit Actor + Retention Purge)

**Files:** Modify `core/compliance/runtime_manifest.py`, `apps/cli/commands/privacy.py`; extend `tests/test_runtime_privacy_manifest.py`

- [ ] **Step 1: Write failing tests** for `record_audit_event(..., actor="system")` accepting and persisting a real actor string, and `purge_expired(retention_days: int) -> list[str]` (returns purged client ids), operating only on artifacts older than the threshold.
- [ ] **Step 2: Implement**, keeping `actor="system"` as default so existing call sites keep working unchanged.
- [ ] **Step 3:** Add `privacy purge-expired --retention-days N [--dry-run]` CLI command.
- [ ] **Step 4:** Add tests covering dry-run vs. real purge, and that non-expired artifacts are untouched.

### Task 8: Design-Token Adoption (strictly after Operator Workbench Task 4 is complete)

**Files:** Modify `apps/web/static/app.css` (inside the `operator-workbench-phase1` worktree, not a second parallel branch)

**Gate:** Do not start this task until `2026-07-05-morphic-operator-workbench-phase1.md` Task 4 ("Rebuild The Frontend As A 10-Phase Operator Workbench") is checked off complete. Verify via `Entwicklung/04_AKTIVE_UMSETZUNG_OPERATOR_WORKBENCH.md` or the worktree's current task state before beginning.

- [ ] **Step 1:** Confirm Task 4 of the Operator Workbench plan is complete (10-phase frontend shell in place) before touching `app.css`, to avoid a merge collision or rework.
- [ ] **Step 2:** Add a token block at the top of `app.css` mirroring `radiquant4`'s semantic tokens (`--background`, `--foreground`, `--primary`, phase tokens), self-hosted `Fraunces`/`Inter` font-faces (no external Google Fonts request, per `PHASE_4` finding on `workflow_stepping.html`), and a `prefers-reduced-motion` block.
- [ ] **Step 3:** Re-point existing hardcoded color values in `app.css` to the new custom properties incrementally (do not do a full rewrite in one pass; keep diff reviewable).
- [ ] **Step 4:** Visual regression check: manual before/after screenshot comparison of the 10-phase workbench (no Playwright infra exists yet in this repo — do not introduce it as a side effect of this task).

### Task 9: Documentation Closure

**Files:** Modify `PROJECT_MEMORY/00_CURRENT_STATE.md`, `Entwicklung/03_ROADMAP_STATUS_ERLEDIGT_OFFEN.md`, `docs/deep-audit-2026-07-05/README.md`

- [ ] **Step 1:** Append a short, dated status entry once Tasks 1-8 land, listing what is now "platform-ready" per the Definition of Done in the design doc.
- [ ] **Step 2:** Do not mark anything "migrated" or "integrated with radiquant4" — only "prepared for future integration", to avoid repeating the documentation-drift pattern already found in `PHASE_0`.

---

## Verification Gate (before declaring this plan done)

1. `pytest tests -q` green (excluding the optional Qiskit-gated test when the extra is not installed).
2. `python -m apps.cli.main health --strict` still `OK`.
3. A full `scan top3-scan` smoke run produces the additional `*_standard_block.json` artifact with the exact contracted field names.
4. `privacy purge-expired --dry-run` runs without error against real archive data.
5. Manual visual check confirms the Operator Workbench still functions with the new design tokens applied.
