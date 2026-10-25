# AURELIA G0 13 Acceptance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the reviewed G0 evidence/review lifecycle, obtain cryptographic operator acceptance and fresh remote authority for one exact candidate, and transition only `GATE-G0` from `red` to `green` while all eight later gates remain `red`.

**Architecture:** No implementation code changes after the frozen implementation commit `I`. Every acceptance change is executed only through Plan 12's frozen `scripts/governance-wave.mjs` runner, which internally owns Plan 03's deterministic `buildGovernanceTransaction(...)` use, protected execution records, resumable transaction journals, raw command capture, and remote-acceptance recording. Evidence follows `captured -> approved review -> verified`; the candidate Gate transition follows only after all required evidence and reviews are verified. Local green output never substitutes for an Acceptance-Receipt, fresh checkpoint, fresh challenge-bound floors, protected trusted time, or the operator's signed full-commit approval.

The generated Genesis change-authorization EVIDs from Plan 12 remain immutable historical provenance throughout this plan. They are additional captured records, not members of GATE-G0's closed five mandatory outcome-evidence set and not substitutes for the five new Review/Gate change-authorization EVIDs below. Every inventory and No-Waiver traversal still includes them.

**Tech Stack:** Frozen Node.js 22 ESM governance validator at `I`, `node:test`, Git first-parent object verification, RFC 8785, SHA-256, Ed25519, RFC 6962, Plan-03 transaction builder, Plan-11 remote verifier.

---

## Immutable inputs and authority boundary

The execution record must supply full 40-character values for `designCommit`, `implementationCommit`, `genesisCommit`, `acceptedGenesisHead`, and later every accepted wave head. It also supplies hashes/IDs for the final design approval, Pre-Ledger bundle, active TCB, branch-policy epoch/rules, external pin set, latest receipt, checkpoint, challenge, challenge responses, and trusted-time attestation. Environment variables are session copies, never trust anchors.

This plan does not create code, schemas, tests, workflows, private keys, credentials, external signatures, trusted times, nonces, GitHub settings, remote refs, or transparency entries. It does not access M-G1, a Debian host, Chrome, an external LLM, client/product data, a database, CUDA, USB, an emitter, or a sensor. Pushing, opening/merging a PR, requesting a validator append, requesting Witness responses, and requesting an operator signature are external-state or human-authority steps and each has an explicit STOP below.

The only allowed final Gate vector is:

```js
const FINAL_GATE_VECTOR = Object.freeze({
  "GATE-G0": "green",
  "GATE-DATAFLOW": "red",
  "GATE-PROFILE": "red",
  "GATE-ART9": "red",
  "GATE-MODULE": "red",
  "GATE-CUDA": "red",
  "GATE-HARDWARE": "red",
  "GATE-PILOT": "red",
  "GATE-24X7": "red",
});
```

No exception may exist: all nine are No-Waiver Gates.

Every EVT carries a non-null trust-root delta. With no trust-root change the exact value is:

```js
const EMPTY_TRUST_ROOT_DELTA_SHA256 = "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"; // SHA256(RFC8785([]))
```

Every non-EVID change has a dedicated authorization EVID captured before that change. Its scope is exactly `governance-change:<recordRef>:transition:<previousRecordSha256>:<resultingRecordSha256>` and its `governanceChangeDigests` is exactly `[changeDigest]`. The closed IDs are:

```js
const CHANGE_AUTH_EVIDENCE = Object.freeze({
  "REV-G0-DESIGN-APPROVAL": "EVID-G0-DESIGN-REVIEW-AUTH",
  "REV-G0-SPEC-REVIEW": "EVID-G0-SPEC-REVIEW-AUTH",
  "REV-G0-QUALITY-REVIEW": "EVID-G0-QUALITY-REVIEW-AUTH",
  "REV-G0-FINAL-REVIEW": "EVID-G0-FINAL-REVIEW-AUTH",
  "GATE-G0": "EVID-G0-GATE-AUTH",
});
```

The first four use `evidenceType:"review-report"`; the Gate authorization uses `evidenceType:"approval-record"`. The latter is only a conditional authorization of the exact future red→green change digest; capture makes no claim that the Gate predicates are already satisfied and cannot itself make a Gate eligible. Their capture EVT is the normalized EVID self-lifecycle exemption: it references only its own EVID ID and needs no self-digest. The later REV/GATE EVT references only its matching change-authorization EVID, which is already captured and immutable and contains its exact scope/change digest; Gate eligibility is evaluated afresh from the later Plan-11 authority context immediately before transition. General test/design evidence stays in the resulting REV/GATE records; it is not decoratively copied into an EVT with the wrong governance-change scope.

## Frozen wave runner and transaction API

Plan 13 consumes, but never changes, Plan 12's frozen governance wave runner.
Direct ad hoc calls to Plan 03 from Plan 13 are prohibited. The snippets below
define the declarative transaction shape that the runner validates and executes;
they are not a second executable path.

Plan 13 therefore supplies only the following declarative transaction contract
to `scripts/governance-wave.mjs` from `I`; it never imports or invokes a
Plan-03 module itself:

```text
runner input  = { baseCommit, changes, protected input file/hash references }
change        = { recordRef, eventKind, resultingRecord, actorRole,
                  actorAssigneeSnapshot, operatorEpoch, occurredAt,
                  evidenceRefs, trustRootDeltaSha256,
                  authorizationAttestations, genesisAnchor }
runner output = { newEvents, resultingRecords, signingRequest }
```

Inside the frozen runner only, `authorizationAttestations` is null for the next
request or a non-empty verified array to finalize that exact next Event; an
empty array is rejected. The runner loads the current schema-valid registers
and byte-identical full EVT prefix from the exact base Git object and invokes
the frozen Plan-03 builder/ledger validator. Signing is strictly sequential
because a finalized attestation changes the Event hash and therefore the next
Event core. The runner exports only the single next `signingRequest` digest and
closed purpose/scope, verifies the returned detached public attestation, and
rebuilds that one change with a non-empty array. Only then may it append the
finalized Event and expose the next request. Multiple unsigned changes or a
later request before the predecessor is finalized are rejected. Only the fully
finalized `resultingRecords`/`newEvents` are rendered. The four Markdown
registers retain exactly one delimited JSON block; historical EVT and records
are byte-identical except the records named in the current transaction.

Every Plan-13 wave uses the same closed runner sequence:

```powershell
npm run check:governance-wave -- --mode next-signing-request --request $env:AURELIA_WAVE_NEXT_REQUEST_FILE --out $env:AURELIA_WAVE_NEXT_SIGNING_REQUEST_FILE
npm run check:governance-wave -- --mode final-render --request $env:AURELIA_WAVE_FINAL_REQUEST_FILE
git add docs/governance
git commit -m "<exact wave commit message>"
npm run check:governance-wave -- --mode record-head --request $env:AURELIA_WAVE_RECORD_HEAD_REQUEST_FILE
npm run check:governance-wave -- --mode record-remote-acceptance --request $env:AURELIA_WAVE_REMOTE_ACCEPTANCE_REQUEST_FILE
```

Environment variables are only session pointers to protected request/record
files. On resume, the execution record and transaction journal are
authoritative; a shell variable, local branch name, or chat summary is never a
trust anchor. Raw command output used by evidence reports is captured through
`command-capture` request profiles and consumed from the protected receipt, not
from terminal scrollback.

### Task 1: Lock G, verify Genesis external acceptance, and capture the acceptance base

**Files:** No repository file changes.

- [ ] **Step 1: Load full anchors from the protected execution record**

```powershell
foreach ($name in 'AURELIA_IMPLEMENTATION_COMMIT','AURELIA_GENESIS_COMMIT','AURELIA_ACCEPTED_GENESIS_HEAD') {
  $value = [Environment]::GetEnvironmentVariable($name)
  if ($value -notmatch '^[0-9a-f]{40}$') { throw "AUTHORITY-RED: $name absent or not a full SHA" }
}
$requiredAuthorityFiles = @(
  'AURELIA_REMOTE_BUNDLE_FILE','AURELIA_PRODUCTION_AUTHORITY_BUNDLE_FILE',
  'AURELIA_EXTERNAL_PINS_FILE','AURELIA_BRANCH_CONTROL_HISTORY_FILE',
  'AURELIA_FLOOR_CHALLENGE_HISTORY_FILE','AURELIA_FLOOR_RESPONSE_HISTORY_FILE',
  'AURELIA_TRUSTED_TIME_HISTORY_FILE','AURELIA_ACCEPTANCE_RECEIPTS_FILE',
  'AURELIA_INITIAL_BRANCH_POLICY_PIN_FILE','AURELIA_SIGNED_ARTIFACT_INVENTORY_FILE',
  'AURELIA_NONCE_ARTIFACTS_FILE','AURELIA_PRODUCTION_ARTIFACTS_FILE'
)
foreach ($name in $requiredAuthorityFiles) {
  $path = [Environment]::GetEnvironmentVariable($name)
  if (-not $path -or -not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "AUTHORITY-RED: $name absent or not a file" }
}
if ($env:AURELIA_GENESIS_COMMIT -ne $env:AURELIA_ACCEPTED_GENESIS_HEAD) { throw 'AUTHORITY-RED: accepted Genesis Head is not G' }
if ((git rev-parse "$env:AURELIA_GENESIS_COMMIT^") -ne $env:AURELIA_IMPLEMENTATION_COMMIT) { throw 'G parent is not I' }
$plan13BaseSha = git rev-parse HEAD
if ($plan13BaseSha -ne $env:AURELIA_GENESIS_COMMIT) { throw 'Plan 13 does not start at exact G' }
$env:AURELIA_PLAN13_BASE_SHA = $plan13BaseSha
```

Expected: no output and exact topology `D -> reviewed implementation commits -> I -> G`. Record `plan13BaseSha` in the protected execution record; create no local branch/ref.

- [ ] **Step 2: Verify G locally and remotely against the same Head/Tree**

```powershell
$tree = git show -s --format=%T $env:AURELIA_GENESIS_COMMIT
npm run check:governance -- --base $env:AURELIA_IMPLEMENTATION_COMMIT --head $env:AURELIA_GENESIS_COMMIT --external-pins $env:AURELIA_EXTERNAL_PINS_FILE --local-preflight
npm run check:governance-remote -- --profile gate-evaluation `
  --bundle $env:AURELIA_REMOTE_BUNDLE_FILE --pins $env:AURELIA_EXTERNAL_PINS_FILE `
  --branch-control-history $env:AURELIA_BRANCH_CONTROL_HISTORY_FILE --floor-challenge-history $env:AURELIA_FLOOR_CHALLENGE_HISTORY_FILE `
  --floor-response-history $env:AURELIA_FLOOR_RESPONSE_HISTORY_FILE --trusted-time-history $env:AURELIA_TRUSTED_TIME_HISTORY_FILE `
  --acceptance-receipts $env:AURELIA_ACCEPTANCE_RECEIPTS_FILE --initial-branch-policy-pin $env:AURELIA_INITIAL_BRANCH_POLICY_PIN_FILE `
  --signed-artifact-inventory $env:AURELIA_SIGNED_ARTIFACT_INVENTORY_FILE --nonce-artifacts $env:AURELIA_NONCE_ARTIFACTS_FILE `
  --production-artifacts $env:AURELIA_PRODUCTION_ARTIFACTS_FILE --head $env:AURELIA_GENESIS_COMMIT --tree $tree
```

Expected: both exit 0; the closed production aggregate contains `operatorAcceptance:null`; remote output binds exact Head/Tree, active TCB/branch-policy epochs, full prefix, a checkpoint no older than one hour under protected trusted time, and at least two challenge-fresh Witness floors from distinct pinned identities/failure domains. All nine Gates remain red. A non-null G0 operator artifact at this all-red stage, test-only `--test-now`, stale challenge, hidden bypass state, missing private-repository capability, repository-derived pin, partial prefix, or equivocation is `AUTHORITY-RED` and stops the plan.

- [ ] **Step 3: Prove the clean Governance-only starting state**

```powershell
git status --short
git diff --check "$env:AURELIA_IMPLEMENTATION_COMMIT..$env:AURELIA_GENESIS_COMMIT"
```

Expected: empty status and diff-check exit 0. Any product/code change after `I` restarts Plan 12 with a new `I` and `G`.

### Task 1A: Commission Plan-13 role assignments before evidence capture

**Files:**
- Modify only through `scripts/governance-wave.mjs`: governance role,
  assignment, trust-root, and EVT records under `docs/governance/**`
- Create: protected external execution records for public-key introduction,
  qualification evidence, and remote acceptance

- [ ] **Step 1: Prepare the closed role-commissioning wave**

Create a protected wave request that assigns distinct, qualified assignees and
externally pinned public keys for `ROLE-IMPLEMENTER`,
`ROLE-SPEC-REVIEWER`, `ROLE-QUALITY-SECURITY-REVIEWER`, and
`ROLE-FINAL-REVIEWER`. The wave contains non-empty trust-root deltas for every
new public-key introduction, exact qualification evidence, operator
authorization attestations, and identity/key separation evidence. A reviewer
may not be the orchestrator, the implementer, or another reviewer when the role
matrix requires separation.

- [ ] **Step 2: Execute the wave only through the frozen runner**

Run the mandatory `next-signing-request -> final-render -> commit ->
record-head -> record-remote-acceptance` sequence from the Frozen wave runner
section. Do not call Plan 03 directly and do not trust a shell variable as the
committed boundary.

- [ ] **Step 3: Store the accepted reviewer-ready head**

Record the accepted Head/Tree, Receipt, checkpoint, floor-set, trusted-time
history tail, and role-assignment hashes in the protected execution record and
expose only the session pointer `AURELIA_G0_REVIEWER_READY_HEAD`.

Expected: all four role families are assigned, qualified, externally pinned,
distinct where required, and remotely accepted before Task 2 starts. Missing
qualification evidence, empty trust-root deltas, duplicate reviewer identity,
unassigned `ROLE-FINAL-REVIEWER`, copied assignee objects, or unrecorded remote
acceptance is `AUTHORITY-RED`.

### Task 2: Capture the three pre-review G0 evidences

**Files:**
- Create: `docs/governance/evidence/EVID-G0-BASELINE-GATES--report.json`
- Create: `docs/governance/evidence/EVID-G0-CONTRACT-TESTS--report.json`
- Create: `docs/governance/manifests/EVID-G0-BASELINE-GATES--subject.json`
- Create: `docs/governance/manifests/EVID-G0-BASELINE-GATES--inputs.json`
- Create: `docs/governance/manifests/EVID-G0-FINAL-DESIGN-APPROVAL--subject.json`
- Create: `docs/governance/manifests/EVID-G0-FINAL-DESIGN-APPROVAL--inputs.json`
- Create: `docs/governance/manifests/EVID-G0-CONTRACT-TESTS--subject.json`
- Create: `docs/governance/manifests/EVID-G0-CONTRACT-TESTS--inputs.json`
- Create: verified detached EVT attestations under `docs/governance/attestations/`
- Modify: `docs/governance/gate-register.md`

- [ ] **Step 1: Run and bind the baseline/contract reports at exact G**

```powershell
if ($env:AURELIA_G0_REVIEWER_READY_HEAD -notmatch '^[0-9a-f]{40}$') { throw 'AUTHORITY-RED: reviewer-ready head absent' }
if ((git rev-parse HEAD) -ne $env:AURELIA_G0_REVIEWER_READY_HEAD) { throw 'AUTHORITY-RED: worktree is not at reviewer-ready head' }
npm run check:canon
npm run typecheck:governance
npm run typecheck
npm run lint
npm test
npm run build:dev
```

Expected: all exit 0 in this order. The reports record command, exit code, discovered test count greater than zero, exact toolchain versions, G Head/Tree, subject/input manifest hashes, start/end trusted times, and SHA-256 of the complete raw outputs. Do not run `npm run build`, because it invokes database migrations.

- [ ] **Step 2: Define the exact capture changes in the protected wave request**

The frozen runner constructs the transaction internally. Populate its external
`waveDefinition` with `baseCommit = reviewerReadyHead` and these three
declarative `changes`, in this order. The
full `reviewerReadyHead` is reread from the protected execution record; the
session pointer `AURELIA_G0_REVIEWER_READY_HEAD` must match it exactly and is
never the trust source:

```js
const captureChanges = [
  ["EVID-G0-BASELINE-GATES", "docs/governance/evidence/EVID-G0-BASELINE-GATES--report.json", baselineReportSha256, implementationCommit, reviewerReadyHead, "AURELIA-G0-GOVERNANCE-IMPLEMENTATION", baselineSubjectManifest, baselineInputManifest],
  ["EVID-G0-FINAL-DESIGN-APPROVAL", "docs/governance/bootstrap/final-design-approval.json", finalApprovalSha256, designCommit, reviewerReadyHead, "AURELIA-G0-GOVERNANCE-DESIGN", finalApprovalSubjectManifest, finalApprovalInputManifest],
  ["EVID-G0-CONTRACT-TESTS", "docs/governance/evidence/EVID-G0-CONTRACT-TESTS--report.json", contractReportSha256, implementationCommit, reviewerReadyHead, "AURELIA-G0-GOVERNANCE-IMPLEMENTATION", contractSubjectManifest, contractInputManifest],
].map(([recordRef, artifactPathOrUri, sha256, baselineCommit, captureBaseCommit, scope, subjectManifest, inputManifest]) => {
  const current = priorRecords.get(recordRef);
  const resultingRecord = Object.freeze({
    ...current,
    status: "captured",
    artifactPathOrUri,
    sha256,
    producerAssigneeSnapshot: "codex-orchestrator",
    producedAt: trustedProducedAt,
    baselineCommit,
    captureBaseCommit,
    subjectManifestPath: subjectManifest.path,
    subjectManifestSha256: subjectManifest.sha256,
    inputManifestPath: inputManifest.path,
    inputManifestSha256: inputManifest.sha256,
    result: "pass",
    verifiedByRole: null,
    verifiedByAssigneeSnapshot: null,
    reviewRefs: [],
    stateReason: null,
    supersedesEvidenceRef: null,
    supersededByEvidenceRef: null,
    supersededFromStatus: null,
    captureEpoch: 1,
    decisionEpoch: null,
    scope,
  });
  return Object.freeze({
    recordRef,
    eventKind: "transition",
    resultingRecord,
    actorRole: current.producerRole,
    actorAssigneeSnapshot: "codex-orchestrator",
    operatorEpoch: 1,
    occurredAt: trustedOccurredAt,
    evidenceRefs: [recordRef],
    trustRootDeltaSha256: EMPTY_TRUST_ROOT_DELTA_SHA256,
    authorizationAttestations: verifiedCaptureAttestations[recordRef],
    genesisAnchor: null,
  });
});
```

The design-approval subject manifest contains only the fixed design path/blob at D; its input manifest (also `subjectBaselineCommit:D`) binds the separately captured bootstrap artifact while `captureBaseCommit` is the reviewer-ready Head. The Baseline/Contract subject manifests expand the frozen implementation surface at I (`GOVERNANCE.md`, `AGENTS.project.md`, canonical corrections, `docs/governance/schemas/**`, `scripts/governance/**`, governance CLIs/tests, and package scripts); their input manifests declare `subjectBaselineCommit:I` while revisionsfest hashing the accepted G and reviewer-role-wave registers/receipt inputs used by the reports. No manifest hashes a path from a future/self commit. `subjectIds`, `subjectPaths`, `command`, `derivationRefs`, `governanceChangeDigests`, `retentionRule`, and specialized payloads otherwise follow the seeded schema. Negative tests swap D/I/G/reviewer-ready Head among baseline/capture fields, mismatch scope, hash current working-tree subjects, omit a recursive I path, or put a G/reviewer-role-wave record into the I subject manifest; all must fail.

- [ ] **Step 3: Record RED before applying, then GREEN after rendering**

Before rendering, validate the proposed target with one removed capture EVT; expected: `LEDGER-TARGET-MISMATCH`. For each of the three changes in order, request and finalize exactly one signature before moving to the next; rebuild the full prefix to prove determinism, render only the fully finalized records/events, then run:

```powershell
npm run check:governance -- --base $env:AURELIA_G0_REVIEWER_READY_HEAD --working-tree --external-pins $env:AURELIA_EXTERNAL_PINS_FILE --local-preflight
git diff --check $env:AURELIA_G0_REVIEWER_READY_HEAD
```

Expected: exit 0 and `LOCAL-PREFLIGHT-ONLY`; three evidences are `captured`, all reviews remain non-approved, and all nine Gates remain red.

- [ ] **Step 4: Commit the Governance-only capture wave**

```powershell
$changed = @(git diff --name-only $env:AURELIA_G0_REVIEWER_READY_HEAD)
if (@($changed | Where-Object { $_ -notlike 'docs/governance/*' }).Count) { throw 'capture wave is not Governance-only' }
git add docs/governance
git commit -m "docs: capture G0 baseline evidence"
$env:AURELIA_G0_CAPTURE_HEAD = git rev-parse HEAD
```

Expected: one first-parent successor of the exact reviewer-ready Head. STOP before push/PR/merge/validator append. Those require explicit operator authorization; after authorization, record a fresh remote Acceptance-Receipt/checkpoint/floors for this exact Head/Tree before Task 3.

### Task 3: Approve Design, Spec, and Quality reviews, then verify their evidences

**Files:**
- Modify: `docs/governance/gate-register.md`
- Create: `docs/governance/evidence/EVID-G0-DESIGN-REVIEW-AUTH--report.json`
- Create: `docs/governance/evidence/EVID-G0-SPEC-REVIEW-AUTH--report.json`
- Create: `docs/governance/evidence/EVID-G0-QUALITY-REVIEW-AUTH--report.json`
- Create: subject/input manifests for those three exact EVID IDs under `docs/governance/manifests/`
- Create: verified detached review/event attestations under `docs/governance/attestations/`

- [ ] **Step 1: Verify remote acceptance of the capture head**

Run the exact remote command from Task 1 with Head/Tree equal to `AURELIA_G0_CAPTURE_HEAD`. Expected: current full-prefix acceptance, no equivocation, fresh trusted time/floors. Otherwise STOP.

- [ ] **Step 2: Complete three independent reviews against identical evidence scope**

`REV-G0-DESIGN-APPROVAL` (baseline D, design scope) reviews `EVID-G0-DESIGN-COMMIT` and `EVID-G0-FINAL-DESIGN-APPROVAL`, both baseline D and identical scope. `REV-G0-SPEC-REVIEW` and `REV-G0-QUALITY-REVIEW` (baseline I, implementation scope) review `EVID-G0-BASELINE-GATES` and `EVID-G0-CONTRACT-TESTS`, both baseline I and identical scope. Reviewer identities are distinct from implementers/orchestrator and from each other where the role contract requires it. Each `resultingRecord` is `{...current, status:"approved", verdict:"approved", reviewerAssigneeSnapshot, independentAssigneeSnapshots, subjectActorSnapshots, decisionEpoch:1, performedAt, approvedByRole:"ROLE-OPERATOR", approvedByAssigneeSnapshot:"redshift-three67", findings:[], findingResolutions:[], evidenceSubjectRefs, evidenceRefs}` with all human/model/reasoning fields set exactly for its execution kind. Negative tests cross-feed a D evidence into an I review, change one scope, or use capture-base as review baseline; all fail. No open P0-P2 and no expired review is accepted.

- [ ] **Step 2a: Capture the exact authorization evidence for those three proposed review changes**

Before any REV changes, compute each requested Review's `previousRecordSha256 = recordSha256(current)`, `resultingRecordSha256 = recordSha256(approvedResult)`, and `changeDigest({recordRef:reviewId,eventKind:"transition",previousRecordSha256,resultingRecordSha256})`. This digest is independent of future EVT ID, previous Event hash, commit, authorization envelope, and signature, so capturing it does not create a cycle. Create `EVID-G0-DESIGN-REVIEW-AUTH`, `EVID-G0-SPEC-REVIEW-AUTH`, and `EVID-G0-QUALITY-REVIEW-AUTH` as new `review-report` records with `status:"captured"`, `subjectIds:[reviewId]`, the exact governance-change scope, `governanceChangeDigests:[changeDigest]`, baseline/capture base equal to the already accepted capture head, complete subject/input manifests containing the previous Review record, proposed result/report inputs, producer snapshot, hashes/times, and no specialized payload. Their own EVID capture EVTs reference only themselves and use `EMPTY_TRUST_ROOT_DELTA_SHA256`; no self-digest is inserted. Capture/finalize them sequentially, run mismatch RED tests for swapped Review IDs, old result hash, extra digest, and scope drift, then commit and obtain fresh remote acceptance:

```powershell
npm run check:governance -- --base $env:AURELIA_G0_CAPTURE_HEAD --working-tree --external-pins $env:AURELIA_EXTERNAL_PINS_FILE --local-preflight
git add docs/governance
git commit -m "docs: capture G0 review authorizations"
$env:AURELIA_G0_REVIEW_AUTH_HEAD = git rev-parse HEAD
```

Expected: the three authorization evidences are captured; Reviews remain requested and all Gates red. STOP until that exact head is remotely accepted.

- [ ] **Step 3: Build, authorize, render, and commit the review transaction**

Create the three Plan-03 changes in Design -> Spec -> Quality order, each with `eventKind:"transition"`, exact approved review record, `actorRole` equal to its reviewer role, its immutable assignee snapshot, epoch `1`, trusted `occurredAt`, EVT `evidenceRefs` containing only its matching captured `CHANGE_AUTH_EVIDENCE`, `trustRootDeltaSha256:EMPTY_TRUST_ROOT_DELTA_SHA256`, verified reviewer plus operator authorization attestations, and `genesisAnchor:null`. For each one, run the null-attestation request and missing-attestation RED mutation, finalize that single Event with a non-empty verified array, then advance the prefix before requesting the next. Render only after all three sequential Event hashes reproduce.

```powershell
npm run check:governance -- --base $env:AURELIA_G0_REVIEW_AUTH_HEAD --working-tree --external-pins $env:AURELIA_EXTERNAL_PINS_FILE --local-preflight
git diff --check $env:AURELIA_G0_REVIEW_AUTH_HEAD
git add docs/governance
git commit -m "docs: approve G0 technical reviews"
$env:AURELIA_G0_REVIEW_HEAD = git rev-parse HEAD
```

Expected: local preflight 0, three approved reviews, evidences still only captured, nine red Gates. STOP for separately authorized remote integration/acceptance of this exact head.

- [ ] **Step 4: Verify the four reviewed evidences in a successor transaction**

After fresh remote acceptance of `AURELIA_G0_REVIEW_HEAD`, transition `EVID-G0-DESIGN-COMMIT`, `EVID-G0-FINAL-DESIGN-APPROVAL`, `EVID-G0-BASELINE-GATES`, and `EVID-G0-CONTRACT-TESTS` from `captured` to `verified`, strictly one signed/finalized Event at a time. Each result is `{...current,status:"verified",verifiedByRole,verifiedByAssigneeSnapshot,reviewRefs:[matchingApprovedReviewIds],decisionEpoch:1}`; all capture fields remain byte-identical. Each change is authorized by its stored verifier role/assignee, references exactly itself in EVT `evidenceRefs`, uses `EMPTY_TRUST_ROOT_DELTA_SHA256`, has no Genesis anchor, and carries a fresh verified attestation. The three change-authorization EVIDs remain immutable `captured` authorization inputs; they are not Review subjects and are not given mismatched Review refs. The second signing request is not generated until the first finalized Event hash is in the prefix, and so on.

```powershell
npm run check:governance -- --base $env:AURELIA_G0_REVIEW_HEAD --working-tree --external-pins $env:AURELIA_EXTERNAL_PINS_FILE --local-preflight
git diff --check $env:AURELIA_G0_REVIEW_HEAD
git add docs/governance
git commit -m "docs: verify reviewed G0 evidence"
$env:AURELIA_G0_VERIFIED_EVIDENCE_HEAD = git rev-parse HEAD
```

Expected: four verified evidences, `EVID-G0-FINAL-GATES` still expected, final review requested, and nine red Gates. STOP for separately authorized remote integration/acceptance.

### Task 4: Capture final gates, approve Final Review, and verify final evidence

**Files:**
- Create: `docs/governance/evidence/EVID-G0-FINAL-GATES--report.json`
- Create: `docs/governance/manifests/EVID-G0-FINAL-GATES--subject.json`
- Create: `docs/governance/manifests/EVID-G0-FINAL-GATES--inputs.json`
- Create: `docs/governance/evidence/EVID-G0-GATE-AUTH--report.json`
- Create: `docs/governance/evidence/EVID-G0-FINAL-REVIEW-AUTH--report.json`
- Create: subject/input manifests for those two exact EVID IDs under `docs/governance/manifests/`
- Modify: `docs/governance/gate-register.md`
- Create: verified detached EVT/review attestations under `docs/governance/attestations/`

- [ ] **Step 1: Run final gates sequentially at the exact accepted evidence head**

After fresh remote acceptance of `AURELIA_G0_VERIFIED_EVIDENCE_HEAD`, run:

```powershell
npm run check:canon
npm run check:governance -- --base $env:AURELIA_GENESIS_COMMIT --head $env:AURELIA_G0_VERIFIED_EVIDENCE_HEAD --external-pins $env:AURELIA_EXTERNAL_PINS_FILE --local-preflight
npm run typecheck:governance
npm run typecheck
npm run lint
npm test
npm run build:dev
git diff --check "$env:AURELIA_PLAN13_BASE_SHA..$env:AURELIA_G0_VERIFIED_EVIDENCE_HEAD"
```

Expected: all exit 0; governance output says local-only and nine red Gates. Capture complete raw outputs, versions, test count, exact Head/Tree, manifests, trusted start/end, and hashes in the final-gates report.

- [ ] **Step 2: Capture final-gates evidence**

Build one change for `EVID-G0-FINAL-GATES` using the exact capture projection from Task 2 with `baselineCommit:I`, scope `AURELIA-G0-GOVERNANCE-IMPLEMENTATION`, artifact/report bound to the already-existing `AURELIA_G0_VERIFIED_EVIDENCE_HEAD`, and `captureBaseCommit` equal to that head. Its subject manifest expands the I implementation tree; its input manifest has `subjectBaselineCommit:I` and revisionsfest binds every accepted Governance head/receipt/register input consumed by the final run. Use the producer role/snapshot from the seed and fresh authorization. Apply RED mutations for baseline=current-head, captureBase=I, scope drift, future/self path, and missing manifest; render, validate, commit, then STOP for remote acceptance:

```powershell
npm run check:governance -- --base $env:AURELIA_G0_VERIFIED_EVIDENCE_HEAD --working-tree --external-pins $env:AURELIA_EXTERNAL_PINS_FILE --local-preflight
git add docs/governance
git commit -m "docs: capture final G0 gates"
$env:AURELIA_G0_FINAL_GATES_CAPTURE_HEAD = git rev-parse HEAD
```

- [ ] **Step 2a: Precompute and capture only the Gate change authorization without a hash cycle**

At the accepted Final-Gates capture head, construct the complete future `GATE-G0 green` record (baseline I, the five required EVIDs, four Review IDs, no exceptions) and hash its current red predecessor/result/change. Create captured `EVID-G0-GATE-AUTH` with `evidenceType:"approval-record"`, subject `GATE-G0`, exact governance-change scope, and exactly that change digest. This is explicitly conditional change authorization, not a contemporaneous statement that Final Review, final Evidence, remote authority, or Green eligibility already exists. Its subject manifest binds the current red Gate record and the complete proposed green record as canonical bytes; its input manifest ends at `AURELIA_G0_FINAL_GATES_CAPTURE_HEAD` and binds the five required EVIDs, four requested/approved Review records available at that point, the pinned role assignments, and the then-known Gate predicate inputs. It never names its own report, manifest, capture Event, or future commit.

The EVID capture EVT references only itself, uses `EMPTY_TRUST_ROOT_DELTA_SHA256`, and is finalized sequentially. The fixed EVID ID makes the proposed Gate result hashable; the authorization record contains neither the future Gate Event hash, future commit SHA, its own record hash, nor its own capture change digest. Run RED tests for replacing the proposed-result hash after capture, using a Review scope, adding a second digest, and attempting to use a future candidate commit as baseline.

```powershell
npm run check:governance -- --base $env:AURELIA_G0_FINAL_GATES_CAPTURE_HEAD --working-tree --external-pins $env:AURELIA_EXTERNAL_PINS_FILE --local-preflight
git add docs/governance
git commit -m "docs: capture G0 Gate authorization"
$env:AURELIA_G0_GATE_AUTH_HEAD = git rev-parse HEAD
```

Expected: Gate authorization evidence captured, Final Review still requested, Gate red, and no Final-Review authorization evidence yet. STOP until exact remote acceptance.

- [ ] **Step 3: Perform the independent Final Review, then capture its exact authorization evidence**

After fresh remote acceptance of `AURELIA_G0_GATE_AUTH_HEAD`, the Final Reviewer—distinct from implementers, orchestrator, Spec Reviewer, and Quality/Security Reviewer—reviews the I implementation subjects plus the complete captured input chain ending exactly at that accepted Gate-authorization head, all mandatory EVIDs, all prior REV results, remote controls, crypto/bootstrap/TCB/transparency/recovery/egress/collector boundaries, and the eight intentional red Gates. The Review inputs do not include `EVID-G0-FINAL-REVIEW-AUTH`, its manifests, its capture Event, or any later commit. The existing requested `REV-G0-FINAL-REVIEW` keeps baseline I and implementation scope, exactly matching `EVID-G0-FINAL-GATES`; later Governance heads are revisionsfest input/derivation records, never a changed Review baseline.

The human reviewer now produces the actual immutable report values `performedAt`, `reviewerAssigneeSnapshot`, `independentAssigneeSnapshots`, `subjectActorSnapshots`, `findings`, `findingResolutions`, and `verdict`. STOP if the verdict is not `approved`, if a P0-P2 finding is open, or if identity/separation evidence is absent. Only from that completed report construct the exact proposed Review result:

```js
const finalReviewResult = Object.freeze({
  ...priorRecords.get("REV-G0-FINAL-REVIEW"),
  status: "approved",
  verdict: "approved",
  decisionEpoch: 1,
  performedAt,
  reviewerAssigneeSnapshot,
  independentAssigneeSnapshots,
  subjectActorSnapshots,
  evidenceSubjectRefs: Object.freeze(["EVID-G0-FINAL-GATES"]),
  evidenceRefs: Object.freeze([
    "EVID-G0-FINAL-GATES",
    ...requiredAssignmentAndReasoningPreflightEvidenceIds,
  ]),
  approvedByRole: "ROLE-OPERATOR",
  approvedByAssigneeSnapshot: "redshift-three67",
  findings,
  findingResolutions,
});
const previousRecordSha256 = recordSha256(priorRecords.get("REV-G0-FINAL-REVIEW"));
const resultingRecordSha256 = recordSha256(finalReviewResult);
const finalReviewChangeDigest = changeDigest({
  recordRef: "REV-G0-FINAL-REVIEW",
  eventKind: "transition",
  previousRecordSha256,
  resultingRecordSha256,
});
const finalReviewAuthorizationScope =
  `governance-change:REV-G0-FINAL-REVIEW:transition:${previousRecordSha256}:${resultingRecordSha256}`;
```

Create and self-capture `EVID-G0-FINAL-REVIEW-AUTH` only now. Its immutable report is the just-completed independent Review report; its closed record has `evidenceType:"review-report"`, `subjectIds:["REV-G0-FINAL-REVIEW"]`, `scope:finalReviewAuthorizationScope`, and `governanceChangeDigests:[finalReviewChangeDigest]`. Its subject manifest binds the requested predecessor plus `finalReviewResult`; its input manifest ends exactly at `AURELIA_G0_GATE_AUTH_HEAD` and binds everything actually reviewed. Neither manifest includes the new authorization EVID or its capture commit. Its own capture EVT references only itself and uses `EMPTY_TRUST_ROOT_DELTA_SHA256`. Run RED mutations for a report/result mismatch, input head after `AURELIA_G0_GATE_AUTH_HEAD`, absent reviewer separation, non-approved verdict, changed finding resolution, wrong scope/hash, or a second digest. Render, validate, commit, and STOP for exact remote acceptance:

```powershell
git add docs/governance
git commit -m "docs: capture final G0 review authorization"
$env:AURELIA_G0_FINAL_REVIEW_AUTH_HEAD = git rev-parse HEAD
```

- [ ] **Step 4: Approve the independently performed Final Review**

After fresh remote acceptance of `AURELIA_G0_FINAL_REVIEW_AUTH_HEAD`, reconstruct `finalReviewResult` and `finalReviewChangeDigest` from the captured report and manifests and require byte-identical equality. Build exactly one sequential Plan-03 change for `REV-G0-FINAL-REVIEW`; its EVT `evidenceRefs` contains only `EVID-G0-FINAL-REVIEW-AUTH`, and it uses `EMPTY_TRUST_ROOT_DELTA_SHA256`. First pass `authorizationAttestations:null` and require the singular signing request. Then pass a non-empty independently verified authorization array; reject an empty array, a request for two changes, a changed result/report, a changed digest, or any evidence reference other than the matching authorization EVID. Render the independently signed transaction, validate, commit, and STOP for remote acceptance:

```powershell
git add docs/governance
git commit -m "docs: approve final G0 review"
$env:AURELIA_G0_FINAL_REVIEW_HEAD = git rev-parse HEAD
```

- [ ] **Step 5: Verify final-gates evidence**

After remote acceptance of the Final Review head, transition only `EVID-G0-FINAL-GATES` to `{...current,status:"verified",verifiedByRole:"ROLE-FINAL-REVIEWER",verifiedByAssigneeSnapshot:finalReviewerAssignee,reviewRefs:["REV-G0-FINAL-REVIEW"],decisionEpoch:1}`. All capture fields remain byte-identical; its EVID EVT references only itself and uses `EMPTY_TRUST_ROOT_DELTA_SHA256`. `EVID-G0-GATE-AUTH` and `EVID-G0-FINAL-REVIEW-AUTH` remain captured and immutable. Render the fresh attested event, validate, commit, and STOP for remote acceptance.

```powershell
git add docs/governance
git commit -m "docs: verify final G0 evidence"
$env:AURELIA_G0_FINAL_EVIDENCE_HEAD = git rev-parse HEAD
```

Expected after fresh remote acceptance: the five mandatory G0 EVIDs are verified, all five change-authorization EVIDs are captured with exact change scopes/digests, required REV records are approved/current, no P0-P2 is open, no exception exists, and all nine Gates remain red.

### Task 5: Build the sole GATE-G0 green candidate

**Files:**
- Modify: `docs/governance/gate-register.md`
- Create: the verified detached GATE EVT authorization under `docs/governance/attestations/`

- [ ] **Step 1: Re-run complete local and remote preconditions on one exact base**

Run Task-4 Step-1 local gates with Head `AURELIA_G0_FINAL_EVIDENCE_HEAD`, then, inside the same Gate-builder process, call Plan 11's sole `verifyProductionAuthorityContext` issuer over that exact accepted all-red Head/Tree and the complete fresh raw input set with `operatorAcceptance:null`. Pass only its in-process `profile:"gate-evaluation",gateEffective:true` capability as the accepted-base authority to Plan 04's dedicated `validateG0GateProposal`. That proposal validator binds the exact working-tree candidate, proves all G0 prerequisites and the target vector, but always returns `status:"LOCAL-GATE-PROPOSAL-ONLY",gateEffective:false,authorityRequired:["g0-operator-acceptance","remote-acceptance"]`; it is never a `ProductionAuthorityContext` and cannot enter the effective Gate engine. Expected: the accepted base vector is nine red and the sole proposed target difference is `GATE-G0:red->green`. A `pre-genesis-ceremony` context, target-head context, cached earlier receipt, raw pin/time object, independently supplied hook map, prior-process result, serialized context, or proposal result presented as authority is rejected.

Use only Plan 11's dedicated proposal runner for that composition. Before the
Working-Tree run, require an operator-provided external report path in
`AURELIA_G0_WORKING_PROPOSAL_REPORT_FILE`; the runner rejects a path inside the
repository:

```powershell
npm run check:governance-g0-proposal -- --base $env:AURELIA_G0_FINAL_EVIDENCE_HEAD --working-tree `
  --external-pins $env:AURELIA_EXTERNAL_PINS_FILE `
  --accepted-base-remote-bundle $env:AURELIA_PRODUCTION_AUTHORITY_BUNDLE_FILE `
  --report-out $env:AURELIA_G0_WORKING_PROPOSAL_REPORT_FILE
```

Expected: exit 0 only for the non-effective proposal status above. This report
is preliminary and cannot be signed because target Commit/Tree are null.

- [ ] **Step 2: Build the one-record Gate transaction and negative mutations**

Use this exact resulting projection:

```js
const current = priorRecords.get("GATE-G0");
const resultingRecord = Object.freeze({
  ...current,
  status: "green",
  baselineCommit: implementationCommit,
  requiredEvidenceRefs: Object.freeze([
    "EVID-G0-BASELINE-GATES",
    "EVID-G0-DESIGN-COMMIT",
    "EVID-G0-FINAL-DESIGN-APPROVAL",
    "EVID-G0-CONTRACT-TESTS",
    "EVID-G0-FINAL-GATES",
  ]),
  reviewRefs: Object.freeze([
    "REV-G0-DESIGN-APPROVAL",
    "REV-G0-SPEC-REVIEW",
    "REV-G0-QUALITY-REVIEW",
    "REV-G0-FINAL-REVIEW",
  ]),
  exceptionRefs: Object.freeze([]),
  expiresOn: null,
});
const gateChange = Object.freeze({
  recordRef: "GATE-G0",
  eventKind: "transition",
  resultingRecord,
  actorRole: "ROLE-OPERATOR",
  actorAssigneeSnapshot: "redshift-three67",
  operatorEpoch: 1,
  occurredAt: trustedOccurredAt,
  evidenceRefs: Object.freeze(["EVID-G0-GATE-AUTH"]),
  trustRootDeltaSha256: EMPTY_TRUST_ROOT_DELTA_SHA256,
  authorizationAttestations: verifiedOperatorGateAttestations,
  genesisAnchor: null,
});
```

The projection uses the exact section-12.4 Gate fields: pre-existing `entryCriteria`, `exitCriteria`, `noWaiver:true`, `verifierRoleRefs`, and `approverRoleRefs` remain byte-identical; `baselineCommit`, `requiredEvidenceRefs`, `reviewRefs`, `exceptionRefs`, and `expiresOn` are the only Gate-specific acceptance bindings. Run negative builds for one missing/extra/stale EVID, non-approved/expired REV, old operator epoch, exception, unassigned Recovery Root, missing active TCB/service/Witness pin, stale checkpoint/floor/time, changed branch-policy epoch, and each additional Gate changed to non-red. Every mutation must be rejected before the real candidate is rendered.

- [ ] **Step 3: Render, validate, and commit the local candidate**

```powershell
npm run check:governance-g0-proposal -- --base $env:AURELIA_G0_FINAL_EVIDENCE_HEAD --working-tree `
  --external-pins $env:AURELIA_EXTERNAL_PINS_FILE `
  --accepted-base-remote-bundle $env:AURELIA_PRODUCTION_AUTHORITY_BUNDLE_FILE `
  --report-out $env:AURELIA_G0_WORKING_PROPOSAL_REPORT_FILE
$changed = @(git diff --name-only $env:AURELIA_G0_FINAL_EVIDENCE_HEAD)
if (@($changed | Where-Object { $_ -notlike 'docs/governance/*' }).Count) { throw 'G0 Gate candidate is not Governance-only' }
git diff --check $env:AURELIA_G0_FINAL_EVIDENCE_HEAD
git add docs/governance
git commit -m "docs: propose G0 governance acceptance"
$env:AURELIA_G0_CANDIDATE_HEAD = git rev-parse HEAD
if (-not $env:AURELIA_G0_COMMITTED_PROPOSAL_REPORT_FILE) { throw 'AUTHORITY-RED: external committed-proposal report path absent' }
npm run check:governance-g0-proposal -- --base $env:AURELIA_G0_FINAL_EVIDENCE_HEAD --head $env:AURELIA_G0_CANDIDATE_HEAD `
  --external-pins $env:AURELIA_EXTERNAL_PINS_FILE `
  --accepted-base-remote-bundle $env:AURELIA_PRODUCTION_AUTHORITY_BUNDLE_FILE `
  --report-out $env:AURELIA_G0_COMMITTED_PROPOSAL_REPORT_FILE
```

Expected: both proposal runs report `LOCAL-GATE-PROPOSAL-ONLY`; the second report binds the actual candidate Commit/Tree and is the sole source of `finalLocalGateReportSha256`. Repository records show only `GATE-G0` green, but G0 is **not accepted yet** and no effective Gate API has returned true for the candidate. The candidate commit cannot contain its own later full-commit operator approval, proposal report, or external Acceptance-Receipt.

### Task 6: Obtain operator full-commit approval and external acceptance

**Files:** No repository changes. Operator approval, Receipt, checkpoint, floors, and trusted-time artifacts live in their protected external systems/bundle.

- [ ] **Step 1: Pause for cryptographic operator approval of the exact candidate**

Present the operator with repository ID, full candidate commit SHA, Tree SHA, complete `I..candidate` path/hash manifest, design commit/spec SHA, scope `AURELIA-G0-GOVERNANCE-ACCEPTANCE`, current operator epoch/key fingerprint, final Gate vector, final local gate report hash, active TCB/branch-policy/pin-set digests, protected trusted time, and fresh nonce. The exact target bindings come only from the Plan-11 wrapper around Plan 04's always non-effective proposal diagnostic; its authority snapshot comes only from the in-process accepted-base Plan-11 `ProductionAuthorityContext`. Before releasing bytes, that wrapper extends the verified base descriptor prefix with every actual committed candidate record/Event, detached attestation, evidence/manifest artifact, and proposal report, then brands the zero-error pre-Operator replay. The signing request fixes `priorNoncePrefixSha256` to that complete candidate pre-acceptance prefix, and the candidate nonce must be absent from its canonical occupied set, including the GATE-G0 Event-attestation Nonce. The operator signs the RFC-8785 bytes with the externally pinned key. Chat text, a Git commit signature alone, a fixture key, a generated key, an orchestrator signature, raw pins/time, a copied context/proposal object, or a signature for another Head/Tree/scope is rejected.

The signing-request handoff also contains the complete canonical accepted-base
Trusted-Time artifact and its full hash. Store that immutable public artifact
at the protected external path
`AURELIA_G0_OPERATOR_TRUSTED_TIME_ATTESTATION_FILE`; it must be byte-identical
to the value from `AURELIA_PRODUCTION_AUTHORITY_BUNDLE_FILE` used by the
proposal runner. It is the historical signing time and is never overwritten
when the external validator later refreshes
the current tail of `AURELIA_TRUSTED_TIME_HISTORY_FILE` with protected time.

Concretely, the Plan-11 proposal wrapper—not Plan 04's plain diagnostic
result—brands the verified committed report and calls the sole unsigned-core
builder. The operator supplies an external closed input file containing only a
new acceptance ID and Nonce; the runner generates neither. Require external
paths in `AURELIA_G0_OPERATOR_INPUT_FILE` and
`AURELIA_G0_OPERATOR_SIGNING_REQUEST_FILE`, then run:

```powershell
npm run check:governance-g0-proposal -- --base $env:AURELIA_G0_FINAL_EVIDENCE_HEAD --head $env:AURELIA_G0_CANDIDATE_HEAD `
  --external-pins $env:AURELIA_EXTERNAL_PINS_FILE `
  --accepted-base-remote-bundle $env:AURELIA_PRODUCTION_AUTHORITY_BUNDLE_FILE `
  --report-out $env:AURELIA_G0_COMMITTED_PROPOSAL_REPORT_FILE `
  --operator-input $env:AURELIA_G0_OPERATOR_INPUT_FILE `
  --operator-signing-request-out $env:AURELIA_G0_OPERATOR_SIGNING_REQUEST_FILE
```

Expected: `OPERATOR-SIGNATURE-PENDING`, `gateEffective:false`; the canonical
core and digest reproduce exactly on a second run. Present only those canonical
bytes/digest and the verified public context to the external operator signer.

- [ ] **Step 2: Verify the operator artifact offline**

Store the returned artifact in the protected external execution record, expose only its file path as `AURELIA_G0_OPERATOR_ACCEPTANCE_FILE`, and require both that file and `AURELIA_G0_OPERATOR_TRUSTED_TIME_ATTESTATION_FILE` to be leaves; otherwise stop `AUTHORITY-RED`. Before any integration request, run the frozen offline return verifier:

```powershell
npm run check:governance-wave -- --mode operator-return-verify --request $env:AURELIA_G0_OPERATOR_RETURN_VERIFY_REQUEST_FILE
```

Expected: strict schema, canonical bytes, Ed25519 signature, external key/fingerprint, role/identity/epoch, global nonce uniqueness against the exact signed pre-acceptance Plan-06 prefix, the byte-identical historical protected-time artifact/hash, exact Head/Tree/path hashes/scope, and exact final Gate vector all verify. The mode writes only protected external public verification artifacts and returns `OPERATOR-RETURN-VERIFIED`; otherwise stop `AUTHORITY-RED`. After integration, refresh the descriptor prefix and signed inventory without changing the historical artifact: the operator artifact contributes exactly one new owned Nonce, the newly issued current Trusted-Time, later Receipt/checkpoint/floor artifacts follow it, the current inventory is last, and the `operator-acceptance` domain has exactly `artifactCount:1` plus its full hash as `headSha256`. A mismatch is `AUTHORITY-RED`; never edit signed fields or replace the key from repository data.

- [ ] **Step 3: Pause for separately authorized remote integration**

Push/PR/merge is not authorized by this plan text. The operator must authorize exact target repository/branch/candidate SHA and the constrained integration mechanism. After integration, the external validator must observe the exact integrated Head/Tree and operator artifact, append one Acceptance-Receipt, co-sign a fresh checkpoint, collect challenge-fresh floors, and obtain a new current Trusted-Time attestation. It then refreshes every component file plus `AURELIA_PRODUCTION_AUTHORITY_BUNDLE_FILE`; the closed aggregate contains `operatorAcceptance` as the parsed exact artifact and `productionArtifacts.operatorTrustedTimeAttestation` as the byte-identical accepted-base historical artifact, not paths or verifier results. The separate current attestation remains in `remoteAuthorityInputs`. If any provider write is partial, the protected branch changed, the historical bytes drift, or the Head differs, G0 remains red externally and recovery follows Plans 07/11; do not rewrite history.

- [ ] **Step 4: Verify final external authority**

```powershell
$tree = git show -s --format=%T $env:AURELIA_G0_CANDIDATE_HEAD
npm run check:governance-remote -- --profile gate-evaluation `
  --bundle $env:AURELIA_REMOTE_BUNDLE_FILE --pins $env:AURELIA_EXTERNAL_PINS_FILE `
  --branch-control-history $env:AURELIA_BRANCH_CONTROL_HISTORY_FILE --floor-challenge-history $env:AURELIA_FLOOR_CHALLENGE_HISTORY_FILE `
  --floor-response-history $env:AURELIA_FLOOR_RESPONSE_HISTORY_FILE --trusted-time-history $env:AURELIA_TRUSTED_TIME_HISTORY_FILE `
  --acceptance-receipts $env:AURELIA_ACCEPTANCE_RECEIPTS_FILE --initial-branch-policy-pin $env:AURELIA_INITIAL_BRANCH_POLICY_PIN_FILE `
  --signed-artifact-inventory $env:AURELIA_SIGNED_ARTIFACT_INVENTORY_FILE --nonce-artifacts $env:AURELIA_NONCE_ARTIFACTS_FILE `
  --production-artifacts $env:AURELIA_PRODUCTION_ARTIFACTS_FILE --operator-trusted-time $env:AURELIA_G0_OPERATOR_TRUSTED_TIME_ATTESTATION_FILE `
  --operator-acceptance $env:AURELIA_G0_OPERATOR_ACCEPTANCE_FILE `
  --head $env:AURELIA_G0_CANDIDATE_HEAD --tree $tree
```

Expected: exit 0. The Receipt directly binds the accepted Head/Tree, Event attestations, active TCB, branch-policy epoch/rules, external log prefix, checkpoint, and pin set. Independently, the refreshed signed inventory/domain state and full Nonce replay bind the operator full-commit artifact; fresh challenge-bound floors bind the resulting checkpoint. All three chains meet in the one Plan-11 authority context. Only now may `GATE-G0` be called effectively green.

### Task 7: Prove final state and close G0

**Files:** No intended changes.

- [ ] **Step 1: Run sequential final gates against the accepted candidate**

```powershell
npm run check:canon
npm run check:governance -- --base $env:AURELIA_GENESIS_COMMIT --head $env:AURELIA_G0_CANDIDATE_HEAD --external-pins $env:AURELIA_EXTERNAL_PINS_FILE --remote-bundle $env:AURELIA_PRODUCTION_AUTHORITY_BUNDLE_FILE
$candidateTree = git show -s --format=%T $env:AURELIA_G0_CANDIDATE_HEAD
npm run check:governance-remote -- --profile gate-evaluation `
  --bundle $env:AURELIA_REMOTE_BUNDLE_FILE --pins $env:AURELIA_EXTERNAL_PINS_FILE `
  --branch-control-history $env:AURELIA_BRANCH_CONTROL_HISTORY_FILE --floor-challenge-history $env:AURELIA_FLOOR_CHALLENGE_HISTORY_FILE `
  --floor-response-history $env:AURELIA_FLOOR_RESPONSE_HISTORY_FILE --trusted-time-history $env:AURELIA_TRUSTED_TIME_HISTORY_FILE `
  --acceptance-receipts $env:AURELIA_ACCEPTANCE_RECEIPTS_FILE --initial-branch-policy-pin $env:AURELIA_INITIAL_BRANCH_POLICY_PIN_FILE `
  --signed-artifact-inventory $env:AURELIA_SIGNED_ARTIFACT_INVENTORY_FILE --nonce-artifacts $env:AURELIA_NONCE_ARTIFACTS_FILE `
  --production-artifacts $env:AURELIA_PRODUCTION_ARTIFACTS_FILE --operator-trusted-time $env:AURELIA_G0_OPERATOR_TRUSTED_TIME_ATTESTATION_FILE `
  --operator-acceptance $env:AURELIA_G0_OPERATOR_ACCEPTANCE_FILE `
  --head $env:AURELIA_G0_CANDIDATE_HEAD --tree $candidateTree
npm run typecheck:governance
npm run typecheck
npm run lint
npm test
npm run build:dev
git diff --check "$env:AURELIA_PLAN13_BASE_SHA..$env:AURELIA_G0_CANDIDATE_HEAD"
git status --short
```

Expected: all commands exit 0; status empty; discovered tests are nonzero; exact final vector equals `FINAL_GATE_VECTOR`; exceptions remain empty; all event/control prefixes are immutable; no P0-P2 finding is open.

- [ ] **Step 2: Run explicit later-Gate regression**

Read the resulting Gate records and assert exact key/value equality with `FINAL_GATE_VECTOR`. Then mutation-test each of the eight later Gates as `amber`, `green`, `expired`, missing, duplicated, or exception-derived. Expected: every mutation fails and the unmodified accepted state passes.

- [ ] **Step 3: Perform independent acceptance Spec Review**

Reviewer checks design sections 6.2-6.4, 7, 9, 12.4-12.6, 13, and 16, D/I/G topology, every wave head/receipt, evidence/review order, full-commit operator approval, and exact Gate vector. Expected: approved, no open P0-P2.

- [ ] **Step 4: Perform independent acceptance Quality/Security Review**

Attack stale/forked prefixes, self-approval, wrong epoch, signature substitution, nonce reuse, repository-derived pins/time, hidden bypass actors, partial `updateRefs`, receipt/head mismatch, old-TCB reactivation, Witness collusion/failure-domain duplication, review/evidence cycles, exception provenance, and an extra green Gate. Expected: approved, no open P0-P2. A finding invalidates acceptance and follows append-only correction; never edit signed artifacts or rewrite accepted history.

- [ ] **Step 5: Record the completed boundary**

The protected handoff records D, I, G, every Plan-13 commit and Tree, artifact/file hashes, operator approval ID/hash, active TCB and branch-policy epochs, external Receipt/checkpoint/floor IDs, trusted-time attestation hash, reviewer identities/verdicts, exact green/red vector, and the following scope statement:

```text
GATE-G0 green authorizes only joint specification of the Debian pilot profile, Threat Model, and privacy dataflow. It authorizes no client or production data, M-G1 access/change, server cleanup/service change, deployment, migration, CUDA, USB, emitter, sensor, hardware activation, external-model disclosure, pilot release, or 24/7 commitment.
```

No live preview is required for this Governance-only boundary. A browser screenshot cannot prove Git object identity, signatures, remote controls, transparency freshness, or Gate effectiveness.
