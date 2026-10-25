# AURELIA G0 Governance Implementation Master Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement and independently verify AURELIA's G0 governance foundation without granting production, server, repository-mutation, or cryptographic signing authority.

**Architecture:** G0 is delivered as thirteen dependency-ordered plans with separately testable boundaries for local validation, append-only governance, cryptographic bootstrap, transparency, recovery, TCB lifecycle, controlled egress, the future M-G1 collector, remote policy evidence, genesis, and acceptance. The frozen design commit remains immutable; local simulators prove contracts but can never substitute for external keys, pins, witnesses, GitHub state, or operator approval.

**Tech Stack:** Node.js 22, ECMAScript modules, TypeScript, `node:test`, Ajv 8.20.0 with JSON Schema Draft 2020-12, ajv-formats 3.0.1, canonicalize 4.0.0/RFC 8785, Node `crypto` Ed25519/SHA-256, Git first-parent replay, GitHub REST API, Markdown governance registers.

---

## Frozen design authority

- Design commit `D`: `a6a8e7dca456d14a6748b204b787b235fdedf9be`
- Design path: `docs/superpowers/specs/2026-08-24-aurelia-g0-governance-design.md`
- SHA-256 of the exact design bytes at `D`: `30c7484753972020dec25083e038a2a1a6ab15a0b3f8885579ce4fa6e3727eb1`
- The operator's chat statement `G0-Design a6a8e7d final freigegeben` authorizes implementation planning. It is not an Ed25519 signature and must never be serialized as `final-design-approval.json`.
- Any change to the frozen design requires a new design commit, a new byte hash, fresh independent reviews, and explicit operator approval before implementation resumes.

## Non-negotiable authority boundary

The implementation agents may create local commits, tests, schemas, fixtures, validators, and documentation in an isolated worktree. They may not push, open or merge a pull request, change GitHub settings, install a GitHub App, mint credentials, generate or use production keys, sign for the operator or recovery root, provision external infrastructure, contact an external LLM with project material, access M-G1, install server software, change services, delete files, migrate a database, or process production/client data without a later explicit authorization for that exact action.

Every unavailable external fact is represented as `unknown/red`. Synthetic fixtures, published public signature vectors, mock GitHub payloads, simulated witnesses, and test repositories must be marked `testOnly: true` and must be structurally unable to produce real gate evidence. No private key is generated, stored in, or read from the repository, fixtures, chat, test output, or logs.

G0 changes governance documents and offline validators, not the application UI. A Chrome live preview therefore adds no acceptance evidence in these plans. If a later authorized task changes portal copy or UI, add a local browser test with a synthetic profile and no production/client data to that task's plan.

## Plan map and dependencies

| Order | Plan | Produces | Depends on |
|---:|---|---|---|
| 01 | [Toolchain, directives, and quality gates](2026-08-24-aurelia-g0-01-toolchain-directives-and-quality-gates.md) | Cross-platform test runner, pinned validation dependencies, G0 directives, deterministic local gates | `D` |
| 02 | [Register and schema core](2026-08-24-aurelia-g0-02-register-and-schema-core.md) | Closed schemas, raw JSON/I-JSON/RFC-8785 core, register parser, product-decision index, reference graph | 01 |
| 03 | [Transition ledger](2026-08-24-aurelia-g0-03-transition-ledger.md) | First-parent replay, append-only transitions, hashes, nonces, status state machine | 02 |
| 04 | [Reviews, evidence, gates, and no-waiver](2026-08-24-aurelia-g0-04-reviews-evidence-gates-no-waiver.md) | Review/evidence lifecycle, taint propagation, gate engine, complete local validator CLI | 03 |
| 05 | [Cryptographic bootstrap](2026-08-24-aurelia-g0-05-cryptographic-bootstrap.md) | RFC-8032 verification and offline ceremony contracts over Plan-02 canonical bytes | 04 |
| 06 | [Transparency and witness protocol](2026-08-24-aurelia-g0-06-transparency-and-witness.md) | RFC 6962 replay, global nonce prefix, non-issuing authority-capability shell, checkpoints, floors, equivocation | 05 |
| 07 | [Recovery write path](2026-08-24-aurelia-g0-07-recovery-write-path.md) | CAS, leases, write-ahead receipts, tombstones, uncertain-outcome closure | 06 |
| 08 | [TCB lifecycle](2026-08-24-aurelia-g0-08-tcb-lifecycle.md) | Promotion, activation, rollback, emergency recovery, immutable identity checks | 07 |
| 09 | [External LLM and egress](2026-08-24-aurelia-g0-09-external-llm-and-egress.md) | Due diligence, sanitization, sealed dispatch, H1/H2 transport evidence | 04, 05, 06 |
| 10 | [M-G1 collector contract](2026-08-24-aurelia-g0-10-mg1-collector-contract.md) | Offline collector, confinement, protected-state comparison, redaction | 02, 04, 05, 09 |
| 11 | [Remote governance](2026-08-24-aurelia-g0-11-remote-governance.md) | Read-only capability probe, branch/ruleset evidence, provider receipt verification | 08, 10 |
| 12 | [Genesis and initial manifest](2026-08-24-aurelia-g0-12-genesis-initial-manifest.md) | Reviewed implementation freeze `I`, closed ceremony CLI/transaction writer, offline signed bundle intake, separate genesis `G` | 10, 11 |
| 13 | [G0 acceptance](2026-08-24-aurelia-g0-13-g0-acceptance.md) | Sequential evidence run, independent final review, operator acceptance request | 12 |

Plans 09 and 10 are implemented sequentially in that order because both extend
the one closed `GOVERNANCE_NONCE_PATHS` literal and its coverage test. Their
read-only research/review may overlap, but implementation and commits may not.
Shared scripts, package metadata, the Governance CLI aggregator, register
files, and Genesis artifacts are always integrated sequentially by the
orchestrator; concurrent agents must not edit those shared paths.

Plan 02 exclusively owns `raw-json.mjs`, `ijson.mjs`, `rfc8785.mjs`, and their direct tests. Later plans import and extend those contracts but do not create a competing canonicalizer. Plan 03 exclusively owns the complete EVT authorization matrix and the stable `buildGovernanceTransaction` API. Event signing is necessarily sequential: only one null-attestation change may produce the singular next `signingRequest`; only its non-empty verified attestations finalize that event and therefore fix the `previousEventHash` for the following request.

Plan 06 exclusively owns the complete repository-wide nonce-prefix replay and
creates `production-authority-context.mjs` as a deliberately non-issuing,
module-private capability shell. Plan 11 modifies that same module and is the
only owner of `verifyProductionAuthorityContext(rawArtifacts)`. Its closed
`pre-genesis-ceremony` profile binds local `I`, signed inventory, independent
pins, Trusted-Time and the global nonce prefix but is always non-gate-effective;
this avoids an I→remote-Receipt→G cycle. Its separate `gate-evaluation` profile
also requires full-prefix receipts/checkpoints/floors, branch controls and all
TCB/recovery/egress/collector results before any Gate can become effective. Plans
05–10 may report cryptographic or semantic validity from raw inputs but can
never make it gate-effective; Plans 04, 12 and 13 accept no caller boolean,
string hook, raw pin/time object, or serialized/copyable substitute.

## Commit and ceremony sequence

The history must preserve these distinct states:

1. `D` is the immutable approved design commit above.
2. Plans 01–11 plus the unsigned constructors, closed ceremony CLI,
   transaction/recovery writer, and seed-generator tasks at the start of plan
   12 produce reviewed local implementation commits without Governance
   Genesis.
3. `I` is the exact reviewed implementation freeze after those plan-12 pre-ceremony tasks, local gates, both technical reviews, and the independent final review pass. Record the full 40-character commit ID; never use a moving branch name or local convenience ref as its trust identity.
4. Outside the repository, the operator and the separate offline recovery root create real keys in approved stores and externally pin their public identities.
5. The operator signs the final design approval over the exact design-defined canonical fields binding `D`, the design byte hash, `issuedAt`, `nonce`, approval scope, and public-key reference. The final-approval schema does not contain `I`.
6. The operator and recovery root sign the identical pre-ledger trust-bundle bytes, which bind `I` and the full bootstrap/control pin set. Neither private key nor an unsigned approximation enters Git, chat, logs, fixtures, or CI.
7. `G` is a new commit based on `I` containing the verified public bootstrap artifacts, the closed initial manifest, and the exact three-part genesis beginning. `G` must not contain validator implementation changes.
8. After `G`, every governance change is a new governance-only transition commit. Existing events and register history remain a byte-identical prefix; corrections use supersession and new events, never deletion or history rewriting.

Every normal non-EVID transition consumes authorization evidence already in the exact lifecycle state permitted by the design (`captured` or, where required, `verified`), whose single `governance-change:<recordRef>:<eventKind>:<previousRecordSha256>:<resultingRecordSha256>` scope and change digest match exactly. EVID lifecycle transitions use only the normalized self-lifecycle rule; no event, evidence record, report, manifest, commit, or signature may depend on its own future hash. Plan 13 therefore captures each dedicated Review/Gate authorization record before it finalizes the corresponding REV/GATE event, with the independent Final Review performed before its own authorization evidence is constructed.

If `I` changes by one byte or commit, discard all dependent unsigned or signed bootstrap candidates and restart steps 3–7 with a new `I`.

## Review protocol for every implementation task

- The orchestrator declares the intended model/reasoning level before each complex step and does not escalate beyond that declaration without a fresh operator acknowledgement.
- Default orchestration uses a balanced reasoning level for status, bookkeeping, prompt drafting, and mechanical consistency checks. `high` is reserved for plan corrections with security or governance impact. `xHigh` is reserved for frozen-design interpretation, cryptographic authority boundaries, recovery/egress/TCB conflicts, and final acceptance decisions.
- Review work is external-review-first unless the operator explicitly authorizes an in-chat internal reviewer for that exact review. The orchestrator supplies the exact review prompt and the smallest sufficient excerpt bundle; the operator returns the review output in chat.
- Review prompts must request only concrete P0-P2 findings with file/section/line, impact, and required fix. Style advice, broad redesigns, and speculative findings are out of scope.
- External Kimi/Gemini or comparable models may review only public, sanitized, or synthetic excerpts. They must not receive the complete G0 design, recovery architecture, server state, secrets, credentials, private or production keys, client/product data, or security-sensitive implementation.
- Internal low-cost OpenAI-family models may be used for narrow mechanical verification, table reconciliation, duplicate-flag scans, and markdown/static consistency checks when the input is non-sensitive and the result is rechecked by the orchestrator.
- Implement with a fresh task agent only when the operator has approved subagent execution for that concrete task; otherwise execute sequentially in this chat.
- After implementation tests pass, obtain a specification review through the external-review-first protocol above.
- Correct every valid finding, then repeat the specification review until approved.
- Obtain a different quality/security review only after specification approval.
- Correct every valid finding, then rerun both review stages because corrections can invalidate earlier approval.
- The orchestrator runs the task's exact gates and inspects the diff before committing or accepting the task commit.
- Reviewers must not accept unresolved P0, P1, or P2 findings. A disagreement is resolved from the frozen design, executable evidence, and authoritative primary documentation; it is never waived for schedule reasons.
- The orchestrator records for each review: model/provider family, reasoning level when known, exact prompt hash, excerpt/source scope, reviewer output hash, accepted findings, rejected findings with rationale, and follow-up verification. A review never becomes governance evidence until the relevant plan's formal evidence lifecycle creates and verifies the record.

## Task 1: Verify the frozen start state

**Files:**
- Read: `docs/superpowers/specs/2026-08-24-aurelia-g0-governance-design.md`
- Read: `docs/superpowers/plans/2026-08-24-aurelia-g0-implementation-master.md`

- [ ] **Step 1: Verify the branch and exact design object**

Run:

```powershell
git branch --show-current
git rev-parse --verify 'a6a8e7d^{commit}'
git show --format= --name-status a6a8e7d
```

Expected: branch `codex/aurelia-g0-governance`; full commit `a6a8e7dca456d14a6748b204b787b235fdedf9be`; the commit adds only the frozen design specification.

- [ ] **Step 2: Recompute the design byte hash from Git, not the working tree**

Run:

```powershell
git rev-parse a6a8e7d:docs/superpowers/specs/2026-08-24-aurelia-g0-governance-design.md
node --input-type=module -e "import {spawnSync} from 'node:child_process'; import {createHash} from 'node:crypto'; const r=spawnSync('git',['show','a6a8e7d:docs/superpowers/specs/2026-08-24-aurelia-g0-governance-design.md'],{encoding:null}); if(r.status!==0) process.exit(r.status ?? 1); console.log(createHash('sha256').update(r.stdout).digest('hex'))"
```

Expected: the SHA-256 line ends in `30c7484753972020dec25083e038a2a1a6ab15a0b3f8885579ce4fa6e3727eb1`. The Git blob ID is recorded separately and must not be mistaken for SHA-256.

- [ ] **Step 3: Verify the worktree is clean before implementation**

Run: `git status --short --branch`

Expected: only the branch header and no modified or untracked paths after the plan suite itself has been committed.

## Task 2: Execute local foundation plans 01–04 sequentially

**Files:**
- Read and execute: plan files 01, 02, 03, and 04 from the table above
- Modify: only the exact files enumerated by the active child plan

- [ ] **Step 1: Execute plan 01 task-by-task with its two-stage reviews**

Expected: complete MJS discovery is cross-platform; zero discovered tests is red; pinned Ajv/RFC 8785 dependencies and deterministic local gate commands are committed.

- [ ] **Step 2: Execute plan 02 task-by-task with its two-stage reviews**

Expected: every schema is Draft 2020-12 strict and closed recursively; registers and all product decision families are parsed from authoritative Git blobs.

- [ ] **Step 3: Execute plan 03 task-by-task with its two-stage reviews**

Expected: first-parent replay, prefix immutability, hash chains, nonce uniqueness, transition rules, and base/head equivalence pass positive and adversarial tests.

- [ ] **Step 4: Execute plan 04 task-by-task with its two-stage reviews**

Expected: taint cannot be laundered through indirect evidence; all nine no-waiver gates fail closed; unassigned mandatory roles keep dependent gates red.

- [ ] **Step 5: Run the local foundation gate in strict sequence**

Run:

```powershell
npm run check:canon
$governanceOutput = & npm run check:governance -- --pre-genesis 2>&1
$governanceExit = $LASTEXITCODE
$governanceText = $governanceOutput -join "`n"
if (
  $governanceExit -eq 0 -or
  $governanceText -notmatch 'AUTHORITY-RED/PRE-GENESIS' -or
  $governanceText -notmatch '"gateEffective"\s*:\s*false' -or
  $governanceText -notmatch '"GENESIS"'
) {
  throw 'pre-Genesis governance authority boundary was not enforced'
}
npm run typecheck
npm run typecheck:governance
npm run lint
npm test
npm run build:dev
git diff --check a6a8e7dca456d14a6748b204b787b235fdedf9be...HEAD
```

The exclusive `--pre-genesis` mode must also report
`gateEffective:false` and `authorityRequired:["GENESIS"]`; parser errors,
empty argv, mixed flags, or a generic test failure do not satisfy this check.

Expected: every ordinary local command exits `0`; the captured production governance invocation exits nonzero with `AUTHORITY-RED/PRE-GENESIS`, after which the explicit assertion itself passes. No other governance diagnostic is accepted. The test runner reports a nonzero discovered test count; `build:dev` performs no database migration. Do not run `npm run build` while it invokes `db:migrate`.

## Task 3: Execute cryptographic and control-plane plans 05–11

**Files:**
- Read and execute: plan files 05 through 11 from the table above
- Modify: only the exact files enumerated by the active child plan

- [ ] **Step 1: Execute plans 05–08 sequentially with two-stage reviews**

Expected: all local cryptographic, transparency, recovery, and TCB fixtures are unmistakably test-only; no private key or external identity is created; no local fixture can satisfy a production gate.

- [ ] **Step 2: Execute plans 09 and 10 in isolated worktrees after their dependencies pass**

Expected: plan 09 reaches only synthetic dummy endpoints; plan 10 proves the offline collector contract in a local fixture or isolated Debian test VM and never connects to M-G1.

- [ ] **Step 3: Integrate plans 09 and 10 sequentially and rerun both review stages**

Expected: shared aggregator and package changes contain no conflict residue; the complete local suite remains green.

- [ ] **Step 4: Execute the read-only capability portion of plan 11 only after explicit authorization to use the GitHub connector**

Expected: the probe has Metadata, Contents, Administration, Checks, Commit statuses, and when needed Pull requests read access only. It performs no mutation. If `bypass_actors`, private-repository branch protection, required-check state, marker controls, force-push/delete controls, or signed-commit evidence cannot be observed completely, record `unknown/red` and stop remote acceptance work.

- [ ] **Step 5: Stop instead of escalating hidden GitHub visibility**

Expected: no write permission is silently added. The orchestrator presents the exact missing observation and requests either a formally reviewed design amendment or a separately constrained privileged-observer architecture before any claim that `GATE-G0` can become green.

## Task 4: Complete unsigned plan-12 builders and freeze implementation commit `I`

**Files:**
- Read: all implementation, schema, fixture, test, directive, and plan paths changed since `D`
- Read and execute before freezing: the unsigned constructors, closed ceremony
  CLI/transaction writer, and initial-manifest builder tasks at the start of
  `docs/superpowers/plans/2026-08-24-aurelia-g0-12-genesis-initial-manifest.md`
- Record outside the repository: the protected, externally authenticated execution record that fixes the full 40-character implementation commit `I`

- [ ] **Step 1: Implement and review the unsigned plan-12 constructors, closed ceremony runner/transaction writer, and deterministic seed generator**

Expected: their unit, fault-injection, and recovery tests pass without
generating a key, signature, Nonce, current time, identity, pin, bootstrap
artifact, register, or Genesis commit. They are normal implementation and
therefore part of `I`.

- [ ] **Step 2: Run all local gates sequentially from a clean checkout of the candidate**

Run the exact command sequence from Task 2, Step 5 with `HEAD` as the candidate.

Expected: every ordinary local command exits `0`; the real production governance invocation remains the explicitly asserted `AUTHORITY-RED/PRE-GENESIS` result until Genesis. No gate is parallelized or reused from an earlier commit.

- [ ] **Step 3: Obtain fresh specification and quality/security approvals for the complete `D..HEAD` range**

Expected: two different reviewers approve the exact full commit ID with no open P0–P2 finding.

- [ ] **Step 4: Obtain the independent final review and record the immutable implementation candidate**

Run: `git rev-parse HEAD`

Expected: the independent final reviewer is separate from implementers, orchestrator, specification reviewer, and quality/security reviewer. One 40-character commit ID is designated `I`. The working tree is clean and `I` does not yet contain register genesis or real bootstrap signatures.

- [ ] **Step 5: Freeze changes pending the offline ceremony**

Expected: any requested implementation correction invalidates `I` and restarts Task 4 from Step 1. Documentation that changes the signed scope is an implementation change for this purpose.

## Task 5: Execute plan 12 ceremony intake and separate genesis

**Files:**
- Read and execute: `docs/superpowers/plans/2026-08-24-aurelia-g0-12-genesis-initial-manifest.md`
- Create: only the exact public artifacts and register files listed in plan 12

- [ ] **Step 1: Stop for explicit operator authorization and approved key-ceremony runbook**

Expected: the operator confirms secure storage, separated operator and recovery-root custodians, external public-key pin destinations, backup/recovery handling, nonce source, time source, and the exact signing bytes. Chat approval alone is rejected.

- [ ] **Step 2: Verify supplied public artifacts offline**

Expected: canonical bytes, purpose separation, public-key fingerprints, both signatures, `D`, design SHA-256, and `I` all verify. The repository never receives private-key material.

- [ ] **Step 3: Build and review genesis commit `G` separately from `I`**

Expected: `G` has parent `I`; it contains no validator or application implementation change; the initial manifest is closed; the prescribed three-event empty-evidence Genesis prefix is exact; every later seed change is preceded by its exact captured change-authorization EVID (or uses the normalized EVID self-lifecycle) with no fourth exemption.

- [ ] **Step 4: Stop before any push or protected-branch integration**

Expected: local `G` is not remote state. Push, PR, provider write credentials, and merge each require the later explicit authority and verified remote controls specified in plans 11 and 12.

## Task 6: Execute plan 13 G0 acceptance

**Files:**
- Read and execute: `docs/superpowers/plans/2026-08-24-aurelia-g0-13-g0-acceptance.md`
- Create: only the exact acceptance evidence listed by plan 13

- [ ] **Step 1: Reconstruct the complete external transparency prefix and remote-control evidence**

Expected: checkpoints are at most one hour old, both witness floors are fresh, external pins agree, no equivocation exists, and branch-control evidence binds the exact G0 head.

- [ ] **Step 2: Run final gates sequentially against the exact candidate head**

Expected: local gates, external receipt verification, and full-prefix replay all pass on the same commit. A stale or partial observation is red.

- [ ] **Step 3: Dispatch an independent final reviewer**

Expected: the final reviewer was not the implementer and did not supply either earlier technical approval; no P0–P2 finding remains open.

- [ ] **Step 4: Request cryptographic operator acceptance for the exact head and scope**

Expected: only a valid operator artifact over the exact full candidate Commit/Tree and pre-acceptance Nonce prefix can make the already proposed `GATE-G0` transition effective. `GATE-DATAFLOW`, `GATE-PROFILE`, `GATE-ART9`, `GATE-MODULE`, `GATE-CUDA`, `GATE-HARDWARE`, `GATE-PILOT`, and `GATE-24X7` remain red.

- [ ] **Step 5: Record the G0 boundary**

Expected: no client/production data, M-G1 access, CUDA, USB, hardware activation, server cleanup, service change, migration, or production deployment occurred as part of G0.

## Stop conditions

Stop the active wave and keep the affected gate red when any of the following occurs:

- the frozen design commit or byte hash differs;
- a command reports zero discovered governance/MJS tests;
- a schema is not strict Draft 2020-12 or permits unknown nested fields;
- an event prefix changes, a nonce repeats, or base/head replay disagrees;
- a signature, pin, checkpoint, witness floor, receipt, provider state, or role assignment is missing, stale, ambiguous, test-only, or unverifiable;
- GitHub hides `bypass_actors`, omits another required protection field, or the read-only probe cannot prove that the required controls are effectively enforced on the private repository; subscription or billing capability is accepted only from a separate authoritative record, never inferred from the public user response;
- a proposed fix would grant broader write permission instead of improving independent observation;
- the recovery result is uncertain; it remains `executing` until closure evidence proves the outcome;
- a requested external-model payload includes the complete G0 design, recovery/security architecture, server state, credentials, secrets, or client data;
- any implementation step requires M-G1, production data, database migration, remote mutation, external provisioning, or key use without its exact later authorization;
- any P0, P1, or P2 review finding remains open.

## Rollback policy

- Before genesis, undo local implementation only with a new revert/fix commit or by abandoning the isolated unpushed worktree; never rewrite an already reviewed or shared history.
- After genesis, never delete or edit historical register entries or events. Redden affected gates first, then append corrective and supersession events.
- Returning a branch policy or external reference to earlier bytes does not reactivate an old receipt; it is a new transition requiring new evidence.
- TCB rollback uses only the pre-activation rollback authorization and the preserved isolated prior TCB.
- A later M-G1 bootstrap gets its own on-site change plan with pre-hashes, backup, exact write set, atomic rollback, and post-hashes. A collector finding never authorizes cleanup automatically.

## Completion record

The orchestrator records, for each child plan: exact start and end commit, changed paths, test count, sequential gate outputs, specification reviewer identity/result, quality/security reviewer identity/result, unresolved findings, external authority used, and whether any stop condition fired. G0 is complete only when plan 13 has verified the complete record and the real operator acceptance artifact transitions only `GATE-G0` to green.
