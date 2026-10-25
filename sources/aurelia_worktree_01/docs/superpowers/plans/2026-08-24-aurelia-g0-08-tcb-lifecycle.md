# AURELIA G0 TCB Lifecycle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement deterministic TCB promotion, activation, pre-authorized rollback, and emergency-recovery replay on top of the verified transparency and recovery protocols.

**Architecture:** TCB changes form one externally checkpointed linear state machine whose state identity is epoch plus full transition-entry hash, never merely a repeated digest set. A promotion request first binds an atomic reset of every green gate, then an inert activation and rollback authorization, and becomes effective only at the unique first full-witness checkpoint that contains it. Rollback and Emergency Recovery compose Plan 07's independently verified provider write path, bind the actual authorization checkpoint by full hash/tree size/issued time, and consume the complete versioned Nonce-prefix plus Plan-11-minted `ProductionAuthorityContext`; no active validator may approve its own replacement or recovery.

**Tech Stack:** Node.js 22 ESM, Draft-2020-12 schema registry, Plans 05–07 cryptographic/transparency/recovery verifiers, RFC-8785 golden vectors, Node test runner.

---

## Prerequisites and authority stops

Plans 05–07 must be green. Plan 06 owns the central versioned
`scripts/governance/nonce-replay.mjs` and
`scripts/governance/production-authority-context.mjs`. The latter exposes only
`readProductionAuthorityContext(value)` over a module-private `WeakMap`; there
is no issuer until Plan 11 later adds the sole
`verifyProductionAuthorityContext(rawArtifacts)`. Before that issuer exists,
every public TCB result necessarily carries
`authorityRequired:["production-authority-context"]` and
`gateEffective:false`. This plan validates only fixture bytes and exported
bundles. It does not build or sign a validator image, activate a controller,
append a transition, reset a live gate, call GitHub, restore a branch, or
contact any witness. Live Operator/Root/Controller/Custodian signatures,
external TCB pins, old-validator receipts, and remote checkpoints remain
explicit `AUTHORITY_REQUIRED` boundaries.

## File map

**Create:**

- `scripts/governance/tcb-verifier-internal.mjs`
- `scripts/governance/tcb-verifier.mjs`
- `scripts/governance/tcb-verifier.test.mjs`
- `scripts/governance/schema-builders/tcb.mjs`
- `scripts/fixtures/governance/tcb/valid-promotion.json`
- `scripts/fixtures/governance/tcb/valid-normal-rollback.json`
- `scripts/fixtures/governance/tcb/valid-emergency-recovery.json`
- `scripts/fixtures/governance/tcb/rfc8785-cores.json`
- `scripts/fixtures/governance/tcb/mutations.json`
- `docs/governance/schemas/validator-promotion-request.schema.json`
- `docs/governance/schemas/validator-activation.schema.json`
- `docs/governance/schemas/validator-activation-bundle.schema.json`
- `docs/governance/schemas/validator-rollback-authorization.schema.json`
- `docs/governance/schemas/validator-rollback-record.schema.json`
- `docs/governance/schemas/emergency-tcb-recovery.schema.json`

**Modify:**

- `scripts/governance/transparency-verifier.mjs`
- `scripts/governance/nonce-replay.mjs`
- `scripts/governance/nonce-replay.test.mjs`
- `scripts/governance-contract.mjs`
- `scripts/governance-contract.test.mjs`

## Stable production exports

```js
// tcb-verifier.mjs; production Ed25519/transparency/recovery are fixed internally;
// raw verification inputs can prove validity but never authorize a gate.
// Interface contracts; complete algorithms appear in Task 7.
export function verifyTcbLifecycle({ bundle, artifacts, nonceArtifacts,
  repositoryState, verificationInputs, authorityContext = null }) {}
export function isProductionTcbResult(value) {}
export function deriveActiveTcbState({ verifiedReplay }) {}
```

The public wrapper first uses raw `verificationInputs.externalPins` and
`verificationInputs.verificationTime` to create its real-signature,
module-privately branded `cryptographicValid/semanticValid` base result. Raw
inputs can never make that result gate-effective. `isProductionTcbResult`
allows Plan 11 to consume this brand in Issuer Phase A without an already
minted Gate Context. Optional gate derivation accepts only the branded claims
`profile:"gate-evaluation"` and `gateEffective:true`, and obtains their exact
`externalPinsSha256`, `trustedTime.now`, `transparency.bundleSha256`, and
`noncePrefixSha256` only from `readProductionAuthorityContext`; Plan 11 must
mint these names from verified evidence. The separately branded
`profile:"pre-genesis-ceremony"` is always non-gate and is rejected here as
Gate authority. The separate `nonceArtifacts` argument is the complete
ordered, versioned raw artifact prefix: the base always replays it but cannot
prove completeness and must preserve `inventoryBindingVerified:false`; Plan 08
never changes that field, and only Plan 11's separately signed inventory
composition may establish completeness. The
optional gate pass additionally compares its
`artifactSetSha256` and `noncePrefixSha256` with the independently
inventory-bound branded claims. The wrapper never
accepts raw pins/time, a boolean/string authority hook, a deserialized
lookalike, or a caller verifier as Gate authority. The internal core remains
semantic-testable and always non-gate-effective without the Plan-11
capability. Plan 11 must never require a gate-effective Plan-08 result to mint
the context that later enables it.

Return state:

```js-fragment
{
  tcbStateEpoch,
  tcbStateEntryId,
  tcbStateEntrySha256,
  activeTcb,
  reservedRecovery: null | { recoveryId, reservedTcbStateEpoch },
  consumedPromotionRequests,
  discardedEpochs,
  gatesForcedRed,
}
```

## Complete schema-builder contract

Create `scripts/governance/schema-builders/tcb.mjs` in Task 1 and extend only
this builder in Tasks 2–5. The following executable core defines all nested
shapes and every exact field list; generated files are registered through the
Plan-02 registry.

```js
import { mkdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
const DRAFT = "https://json-schema.org/draft/2020-12/schema";
const V = { const: "aurelia-governance-v1" }, REPO = { const: "redshift-three67/aurelia" };
const TEXT = { type: "string", minLength: 1 }, HEX = { type: "string", pattern: "^[0-9a-f]{64}$" };
const OID = { type: "string", pattern: "^[0-9a-f]{40}$" };
const TIME = { type: "string", pattern: "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\\.[0-9]{3}Z$" };
const NONCE = { type: "string", pattern: "^[A-Za-z0-9_-]{43}$" }, SIG = { type: "string", pattern: "^[A-Za-z0-9_-]{86}$" };
const UINT = { type: "integer", minimum: 0, maximum: 9007199254740991 }, POS = { type: "integer", minimum: 1, maximum: 9007199254740991 };
const nullable = (schema) => ({ anyOf: [schema, { type: "null" }] });
const closed = (properties) => ({ type: "object", additionalProperties: false, required: Object.keys(properties), properties });
const top = (name, body) => ({ $schema: DRAFT, $id: `https://aurelia.invalid/schemas/${name}`, ...body });
const fields = (names, overrides = {}) => Object.fromEntries(names.map((name) => {
  if (overrides[name]) return [name, overrides[name]];
  if (/(?:Sha256)$/.test(name)) return [name, HEX];
  if (/(?:Commit|TreeOid)$/.test(name)) return [name, OID];
  if (/(?:At|ValidUntil|ExpiresAt|NotBefore)$/.test(name)) return [name, TIME];
  if (/(?:Epoch|TreeSize)$/.test(name)) return [name, POS];
  return [name, TEXT];
}));
const tcb = closed({ validatorImageDigest: { type: "string", pattern: "^sha256:[0-9a-f]{64}$" },
  policySha256: HEX, workflowSha256: HEX, schemaSetSha256: HEX, trustProtocolSha256: HEX });
const roleSignature = (coreField, purposes) => closed({ purpose: { enum: purposes },
  signerRole: TEXT, signerIdentity: TEXT, keyRef: TEXT, signedAt: TIME, nonce: NONCE,
  [coreField]: HEX, signature: SIG });
const controllerSignature = (coreField) => closed({ keyRef: TEXT, signedAt: TIME,
  nonce: NONCE, [coreField]: HEX, signature: SIG });
const commonLog = (entryKind) => ({ schemaVersion: V, entryKind: { const: entryKind }, repositoryId: REPO,
  logId: TEXT, transparencyLogIndex: UINT, previousLogEntrySha256: nullable(HEX), loggedAt: TIME,
  instanceKeyRef: TEXT, instanceKeyEpoch: POS, method: { const: "ed25519" }, entryCoreSha256: HEX,
  instanceSignature: closed({ keyRef: TEXT, signedAt: TIME, nonce: NONCE, entryCoreSha256: HEX, signature: SIG }) });
const logEntry = (kind, payload) => closed({ ...commonLog(kind), ...payload });

const gatePlan = closed({ gateRef: TEXT, previousRecordSha256: HEX,
  resultingRedRecordSha256: HEX, changeDigest: HEX });
const promotionFields = ["schemaVersion", "promotionEvidenceRef", "repositoryId",
  "previousTcbStateEpoch", "previousTcbStateEntryId", "previousTcbStateEntrySha256",
  "previousValidatorImageDigest", "nextValidatorImageDigest", "previousPolicySha256",
  "nextPolicySha256", "previousWorkflowSha256", "nextWorkflowSha256",
  "previousSchemaSetSha256", "nextSchemaSetSha256", "previousTrustProtocolSha256",
  "nextTrustProtocolSha256", "reviewRefs", "gateResetPlan", "gateResetTransactionSha256",
  "activationNotBefore", "expiresAt", "rollbackValidUntil", "nonce", "authorizationSignatures"];
const validatorPromotionRequest = top("validator-promotion-request.schema.json", closed(fields(promotionFields, {
  schemaVersion: V, repositoryId: REPO, previousTcbStateEntryId: nullable(TEXT),
  previousTcbStateEntrySha256: nullable(HEX),
  previousValidatorImageDigest: { type: "string", pattern: "^sha256:[0-9a-f]{64}$" },
  nextValidatorImageDigest: { type: "string", pattern: "^sha256:[0-9a-f]{64}$" },
  reviewRefs: { type: "array", minItems: 1, items: TEXT }, gateResetPlan: { type: "array", items: gatePlan },
  nonce: NONCE, authorizationSignatures: { type: "array", minItems: 2,
    items: roleSignature("promotionCoreSha256", ["operator", "recovery-root", "custodian-a", "custodian-b"]) },
})));

const activationFields = ["schemaVersion", "repositoryId", "activationId", "requestEvidenceRef",
  "requestSha256", "resetReceiptId", "resetHeadCommit", "resetHeadTreeOid",
  "previousTcbStateEpoch", "previousTcbStateEntryId", "previousTcbStateEntrySha256",
  "previousTcb", "nextTcb", "preparedAt", "activationNonce", "controllerSignature"];
const validatorActivation = top("validator-activation.schema.json", closed(fields(activationFields, {
  schemaVersion: V, repositoryId: REPO,
  activationId: { type: "string", pattern: "^TCBACT-[0-9]{12}$" },
  previousTcbStateEntryId: nullable(TEXT), previousTcbStateEntrySha256: nullable(HEX),
  previousTcb: tcb, nextTcb: tcb, activationNonce: NONCE,
  controllerSignature: controllerSignature("activationCoreSha256"),
})));

const rollbackAuthFields = ["schemaVersion", "repositoryId", "activationId", "activationSha256",
  "requestEvidenceRef", "requestSha256", "rollbackHeadReceiptId", "rollbackHeadCommit",
  "rollbackHeadTreeOid", "previousTcb", "nextTcb", "rollbackValidUntil", "allowedReasons",
  "rollbackCoreSha256", "authorizationSignatures"];
const rollbackPurposes = ["controller", "operator", "recovery-root", "custodian-a", "custodian-b"];
const validatorRollbackAuthorization = top("validator-rollback-authorization.schema.json",
  closed(fields(rollbackAuthFields, { schemaVersion: V, repositoryId: REPO,
    previousTcb: tcb, nextTcb: tcb, allowedReasons: { const: ["health-check-failed", "policy-regression", "validator-unusable"] },
    authorizationSignatures: { type: "array", minItems: 3,
      items: roleSignature("rollbackCoreSha256", rollbackPurposes) } })));

const bundleFields = ["activationId", "activationSha256", "rollbackAuthorizationSha256",
  "requestEvidenceRef", "requestSha256", "requestConsumed", "previousTcbStateEpoch",
  "tcbStateEpoch", "previousTcbStateEntryId", "previousTcbStateEntrySha256", "nextTcb",
  "rollbackValidUntil", "effectiveAfterCheckpoint", "controllerBundleCoreSha256", "controllerSignature"];
const validatorActivationBundle = top("validator-activation-bundle.schema.json",
  logEntry("tcb-activation", fields(bundleFields, {
    activationId: { type: "string", pattern: "^TCBACT-[0-9]{12}$" }, requestConsumed: { const: true },
    previousTcbStateEntryId: nullable(TEXT), previousTcbStateEntrySha256: nullable(HEX),
    nextTcb: tcb, effectiveAfterCheckpoint: { const: true },
    controllerSignature: controllerSignature("controllerBundleCoreSha256"),
  })));

const rollbackRecordFields = ["rollbackId", "activationId", "activationEntrySha256",
  "rollbackAuthorizationSha256", "reason", "attemptedHeadCommit", "attemptedHeadTreeOid",
  "restoreReceiptId", "restoreHeadCommit", "restoreHeadTreeOid", "restoredTcb",
  "authorizationCheckpointSha256", "authorizationCheckpointTreeSize",
  "authorizationCheckpointIssuedAt", "recoveryOperationLeaseId", "recoveryOperationLeaseSha256",
  "recoveryAppAttestationRef", "recoveryAppAttestationSha256", "gatewayAcceptedReceiptRef",
  "gatewayAcceptedReceiptSha256", "recoveryIdempotencyTombstoneRef",
  "recoveryIdempotencyTombstoneSha256", "recoveryEgressIntentRef", "recoveryEgressIntentSha256",
  "gatewayDispatchStartedReceiptRef", "gatewayDispatchStartedReceiptSha256",
  "gatewaySettledReceiptRef", "gatewaySettledReceiptSha256", "providerReceiptRef",
  "providerReceiptSha256", "compareAndSwapOperationIdSha256", "previousTcbStateEpoch",
  "tcbStateEpoch", "previousTcbStateEntryId", "previousTcbStateEntrySha256", "rolledBackAt",
  "rollbackRecordCoreSha256", "controllerSignature"];
const validatorRollbackRecord = top("validator-rollback-record.schema.json",
  logEntry("tcb-rollback", fields(rollbackRecordFields, {
    rollbackId: { type: "string", pattern: "^TCBRB-[0-9]{12}$" },
    reason: { enum: ["health-check-failed", "policy-regression", "validator-unusable"] },
    restoredTcb: tcb, authorizationCheckpointTreeSize: POS,
    previousTcbStateEntryId: nullable(TEXT), previousTcbStateEntrySha256: nullable(HEX),
    controllerSignature: controllerSignature("rollbackRecordCoreSha256"),
  })));
```

Append the discriminated Emergency schema and writer to that same file:

```js
const recoveryPurposes = ["controller", "operator", "recovery-root", "custodian-a", "custodian-b"];
const authorizedFields = ["recoveryId", "phase", "incidentArtifactUri", "incidentArtifactSha256",
  "branch", "expectedCompromisedHeadCommit", "recoveryTargetReceiptId",
  "recoveryTargetHeadCommit", "recoveryTargetHeadTreeOid", "recoveryTargetTcb",
  "previousTcbStateEpoch", "reservedTcbStateEpoch", "previousTcbStateEntryId",
  "previousTcbStateEntrySha256", "authorizedAt", "authorizationExpiresAt",
  "recoveryAuthorizationCoreSha256", "authorizationSignatures"];
const authorized = logEntry("tcb-emergency-recovery", fields(authorizedFields, {
  recoveryId: { type: "string", pattern: "^TCBREC-[0-9]{12}$" }, phase: { const: "authorized" },
  expectedCompromisedHeadCommit: OID, recoveryTargetHeadCommit: OID, recoveryTargetHeadTreeOid: OID,
  recoveryTargetTcb: tcb, previousTcbStateEntryId: nullable(TEXT),
  previousTcbStateEntrySha256: nullable(HEX), authorizationSignatures: { type: "array", minItems: 3,
    items: roleSignature("recoveryAuthorizationCoreSha256", recoveryPurposes) },
}));
const completedFields = ["recoveryId", "phase", "authorizationEntrySha256",
  "authorizationCheckpointSha256", "authorizationCheckpointTreeSize",
  "authorizationCheckpointIssuedAt", "recoveryOperationLeaseId", "recoveryOperationLeaseSha256",
  "branch", "observedRestoredHeadCommit", "observedRestoredHeadTreeOid", "restoredTcb",
  "recoveryAppAttestationRef", "recoveryAppAttestationSha256", "gatewayAcceptedReceiptRef",
  "gatewayAcceptedReceiptSha256", "recoveryIdempotencyTombstoneRef",
  "recoveryIdempotencyTombstoneSha256", "recoveryEgressIntentRef", "recoveryEgressIntentSha256",
  "gatewayDispatchStartedReceiptRef", "gatewayDispatchStartedReceiptSha256",
  "gatewaySettledReceiptRef", "gatewaySettledReceiptSha256", "providerReceiptRef",
  "providerReceiptSha256", "compareAndSwapOperationIdSha256", "previousTcbStateEpoch",
  "tcbStateEpoch", "previousTcbStateEntryId", "previousTcbStateEntrySha256", "completedAt",
  "recoveryCompletionCoreSha256", "controllerSignature"];
const completed = logEntry("tcb-emergency-recovery", fields(completedFields, {
  recoveryId: { type: "string", pattern: "^TCBREC-[0-9]{12}$" }, phase: { const: "completed" },
  authorizationCheckpointTreeSize: POS, observedRestoredHeadCommit: OID,
  observedRestoredHeadTreeOid: OID, restoredTcb: tcb,
  previousTcbStateEntryId: nullable(TEXT), previousTcbStateEntrySha256: nullable(HEX),
  controllerSignature: controllerSignature("recoveryCompletionCoreSha256"),
}));
const abortedFields = ["recoveryId", "phase", "authorizationEntrySha256",
  "authorizationCheckpointSha256", "authorizationCheckpointTreeSize",
  "authorizationCheckpointIssuedAt", "recoveryOperationLeaseId", "recoveryOperationLeaseSha256",
  "abortReason", "observedBranchHeadCommit", "failureProofType", "failureProofRef",
  "failureProofSha256", "failureProofCheckpointSha256", "failureProofCheckpointTreeSize",
  "previousTcbStateEpoch", "reservedTcbStateEpoch", "previousTcbStateEntryId",
  "previousTcbStateEntrySha256", "abortedAt", "recoveryAbortCoreSha256",
  "authorizationSignatures"];
const abortedProperties = fields(abortedFields, {
  recoveryId: { type: "string", pattern: "^TCBREC-[0-9]{12}$" }, phase: { const: "aborted" },
  authorizationCheckpointTreeSize: POS, recoveryOperationLeaseId: nullable(TEXT),
  recoveryOperationLeaseSha256: nullable(HEX),
  abortReason: { enum: ["lease-unavailable", "gateway-not-dispatched", "cas-precondition-failed",
    "provider-error", "authorization-expired", "operator-abort"] },
  observedBranchHeadCommit: OID,
  failureProofType: nullable({ enum: ["gateway-cancelled", "gateway-settled-failure"] }),
  failureProofRef: nullable(TEXT), failureProofSha256: nullable(HEX),
  failureProofCheckpointSha256: nullable(HEX), failureProofCheckpointTreeSize: nullable(POS),
  previousTcbStateEntryId: nullable(TEXT), previousTcbStateEntrySha256: nullable(HEX),
  authorizationSignatures: { type: "array", minItems: 3,
    items: roleSignature("recoveryAbortCoreSha256", recoveryPurposes) },
});
const noProof = ["failureProofType", "failureProofRef", "failureProofSha256",
  "failureProofCheckpointSha256", "failureProofCheckpointTreeSize"];
const aborted = { ...logEntry("tcb-emergency-recovery", abortedProperties), allOf: [{ oneOf: [
  { properties: Object.fromEntries(["recoveryOperationLeaseId", "recoveryOperationLeaseSha256", ...noProof]
    .map((name) => [name, { type: "null" }])) },
  { properties: { recoveryOperationLeaseId: { not: { type: "null" } },
    recoveryOperationLeaseSha256: { not: { type: "null" } },
    failureProofType: { const: "gateway-cancelled" }, failureProofRef: { not: { type: "null" } },
    failureProofSha256: { not: { type: "null" } },
    failureProofCheckpointSha256: { not: { type: "null" } },
    failureProofCheckpointTreeSize: { not: { type: "null" } } } },
  { properties: { recoveryOperationLeaseId: { not: { type: "null" } },
    recoveryOperationLeaseSha256: { not: { type: "null" } },
    failureProofType: { const: "gateway-settled-failure" }, failureProofRef: { not: { type: "null" } },
    failureProofSha256: { not: { type: "null" } },
    failureProofCheckpointSha256: { not: { type: "null" } },
    failureProofCheckpointTreeSize: { not: { type: "null" } } } },
] }] };
const emergencyTcbRecovery = top("emergency-tcb-recovery.schema.json",
  { oneOf: [authorized, completed, aborted] });

export const tcbSchemas = {
  "validator-promotion-request.schema.json": validatorPromotionRequest,
  "validator-activation.schema.json": validatorActivation,
  "validator-activation-bundle.schema.json": validatorActivationBundle,
  "validator-rollback-authorization.schema.json": validatorRollbackAuthorization,
  "validator-rollback-record.schema.json": validatorRollbackRecord,
  "emergency-tcb-recovery.schema.json": emergencyTcbRecovery,
};
export async function writeTcbSchemas(target = "docs/governance/schemas") {
  await mkdir(target, { recursive: true });
  for (const [name, schema] of Object.entries(tcbSchemas)) {
    await writeFile(resolve(target, name), `${JSON.stringify(schema, null, 2)}\n`, "utf8");
  }
}
```

The schema test deletes/adds/mistypes every field at every level and tests each
Emergency `oneOf` nullability branch. Semantic replay separately constrains
the no-Lease abort branch to its three allowed reasons and all proof branches
to their matching Gateway state.

The internal core may be imported only by `tcb-verifier.mjs` and its test.
Semantic-test results are permanently `testOnly: true, gateEffective: false`.
The public wrapper supplies real Plan 05 signature verification, Plan 06
transparency replay, and Plan 07 recovery verification without caller override.

## Shared TCB value

Every `previousTcb`, `nextTcb`, `restoredTcb`, or `recoveryTargetTcb` has
exactly these five 64-hex fields, with validator image using the image form:

```js-fragment
{
  validatorImageDigest: "sha256:<64 lowercase hex>",
  policySha256: "<64 lowercase hex>",
  workflowSha256: "<64 lowercase hex>",
  schemaSetSha256: "<64 lowercase hex>",
  trustProtocolSha256: "<64 lowercase hex>",
}
```

### Task 1: Validate immutable promotion request and atomic gate-reset plan

**Files:**

- Create: `docs/governance/schemas/validator-promotion-request.schema.json`
- Create: `scripts/governance/schema-builders/tcb.mjs`
- Create: `scripts/governance/tcb-verifier.test.mjs`
- Create: `scripts/governance/tcb-verifier-internal.mjs`
- Create: `scripts/governance/tcb-verifier.mjs`
- Create: `scripts/fixtures/governance/tcb/valid-promotion.json`

- [ ] **Step 1: Write the promotion schema RED test**

The fixture contains exactly the §6.3 request fields, no future commit/tree/
receipt, sorted review refs, sorted complete gate-reset plan, timing, nonce,
and sorted authorization signatures. Each signature binds the same promotion
core but has its own purpose/key/identity/time/nonce/signature.

- [ ] **Step 2: Add exact gate-reset digest RED tests**

For every currently green gate, recompute its `changeDigest` and require one
plan entry with previous/resulting record hashes. Recompute
`gateResetTransactionSha256` from repository ID, evidence ref, and complete
plan. Reject missing/extra/duplicate/not-currently-green gates and an EVID
scope other than
`governance-transaction:tcb-promotion:<gateResetTransactionSha256>`.

- [ ] **Step 3: Add threshold, time, and A→B→A mutations**

Reject missing Operator/Root, missing post-Pilot Custodian, wrong role/key,
same assignee, changed review, request reuse, previous epoch/ID/hash mismatch,
`activationNotBefore >= expiresAt`, rollback window outside 1–24 hours, and a
request made before a later A→B→A state sequence even when TCB digests repeat.

- [ ] **Step 4: Run and confirm RED**

```powershell
node --test --test-name-pattern="promotion request" scripts/governance/tcb-verifier.test.mjs
```

Expected: missing schema and verifier fail.

- [ ] **Step 5: Generate and exhaustively test the closed request schema**

Use exact top-level, gate-plan, and signature field sets from §6.3 with
`additionalProperties: false` at all levels. Close purposes to `operator`,
`recovery-root`, `custodian-a`, `custodian-b`. The core excludes only
`authorizationSignatures`; each signature object contains its own
`promotionCoreSha256`.

- [ ] **Step 6: Implement request validation**

Recompute core and transaction hashes, compare the replayed predecessor state
tuple three times (request creation, reset head, activation), require all
reviews/current roles, and insert the request hash into a never-reuse set only
when the later activation becomes checkpoint-effective.

- [ ] **Step 7: Run and confirm GREEN**

Expected: valid request passes; every scope, gate, signature, time, state-epoch,
A→B→A, and reuse mutation fails.

- [ ] **Step 8: Commit promotion validation**

```powershell
git add docs/governance/schemas/validator-promotion-request.schema.json scripts/governance/schema-builders/tcb.mjs scripts/governance/tcb-verifier-internal.mjs scripts/governance/tcb-verifier.mjs scripts/governance/tcb-verifier.test.mjs scripts/fixtures/governance/tcb/valid-promotion.json
git commit -m "feat: validate TCB promotion requests"
```

### Task 2: Validate inert activation and prior rollback authorization

**Files:**

- Create: `docs/governance/schemas/validator-activation.schema.json`
- Create: `docs/governance/schemas/validator-rollback-authorization.schema.json`
- Modify: `scripts/governance/schema-builders/tcb.mjs`
- Modify: `scripts/governance/tcb-verifier-internal.mjs`
- Modify: `scripts/governance/tcb-verifier.test.mjs`

- [ ] **Step 1: Write activation RED tests**

Assert exact request hash/EVID, reset receipt/head/tree, predecessor state tuple,
previous/next TCB, prepared time, activation nonce, and closed Controller
signature. `activationSha256` is the full canonical signed artifact hash and is
not stored inside the activation object.

- [ ] **Step 2: Write rollback-authorization RED tests**

Assert activation/request hashes, rollback head/receipt exactly equal the old-
TCB accepted reset head, previous/next TCB, rollback deadline, exact sorted
reasons `health-check-failed`, `policy-regression`, `validator-unusable`, core,
and Controller+Operator+Root(+post-Pilot Custodians) signatures.

- [ ] **Step 3: Add cycle/order mutations**

Reject Activation that includes future bundle hash, rollback authorization
that includes future rollback record, different reset receipt, wrong head/tree,
changed TCB, missing reason, wrong core projection, or signature time outside
the authorized interval.

- [ ] **Step 4: Run and confirm RED**

Expected: both missing schemas fail.

- [ ] **Step 5: Generate both closed schemas and implement validators**

Use the exact §6.3 field sets. Recompute Activation core excluding only its
Controller signature; recompute rollback core excluding itself and signatures.
Require rollback authorization to exist and validate completely before any
activation bundle can be accepted.

- [ ] **Step 6: Run and confirm GREEN**

Expected: valid inert pair passes; every cycle, reset, TCB, reason, threshold,
core, and time mutation fails.

- [ ] **Step 7: Commit activation preparation**

```powershell
git add docs/governance/schemas/validator-activation.schema.json docs/governance/schemas/validator-rollback-authorization.schema.json scripts/governance/schema-builders/tcb.mjs scripts/governance/tcb-verifier-internal.mjs scripts/governance/tcb-verifier.test.mjs
git commit -m "feat: validate TCB activation preparation"
```

### Task 3: Activate only at the full-witness checkpoint

**Files:**

- Create: `docs/governance/schemas/validator-activation-bundle.schema.json`
- Modify: `scripts/governance/schema-builders/tcb.mjs`
- Modify: `scripts/governance/tcb-verifier-internal.mjs`
- Modify: `scripts/governance/tcb-verifier.test.mjs`

- [ ] **Step 1: Write activation-bundle RED tests**

Assert exact Activation/Rollback-Authorization/Request hashes, consumed flag,
predecessor state tuple, epoch increment, next TCB, rollback deadline,
`effectiveAfterCheckpoint: true`, Controller bundle core, and signature.

- [ ] **Step 2: Add inert/effective boundary tests**

Derive old TCB before the first full-quorum checkpoint that includes the
bundle, then next TCB at that checkpoint. Reject partial witness signatures,
checkpoint before logged entry, too-late checkpoint, second activation from
the request, different next TCB, and branch state fork.

- [ ] **Step 3: Run and confirm RED**

Expected: schema/state activation absent.

- [ ] **Step 4: Generate the schema and implement activation replay**

Use exact fields from §6.3. Increase state epoch exactly once; state entry ID
is `activationId`; state entry hash is the full signed log-entry hash. Mark the
request consumed only at the effective checkpoint. All later Acceptance
Receipts must bind epoch, ID, hash, and full TCB exactly.

- [ ] **Step 5: Run and confirm GREEN**

Expected: inert/effective transition passes; all fork, threshold, time,
consumption, state, and receipt mutations fail.

- [ ] **Step 6: Commit checkpoint activation**

```powershell
git add docs/governance/schemas/validator-activation-bundle.schema.json scripts/governance/schema-builders/tcb.mjs scripts/governance/tcb-verifier-internal.mjs scripts/governance/tcb-verifier.test.mjs
git commit -m "feat: activate TCB at witness checkpoint"
```

### Task 4: Validate normal rollback through the recovery write path

**Files:**

- Create: `docs/governance/schemas/validator-rollback-record.schema.json`
- Create: `scripts/fixtures/governance/tcb/valid-normal-rollback.json`
- Modify: `scripts/governance/schema-builders/tcb.mjs`
- Modify: `scripts/governance/tcb-verifier-internal.mjs`
- Modify: `scripts/governance/tcb-verifier.test.mjs`

- [ ] **Step 1: Write rollback-record RED tests**

Assert every §6.3 field: activation/auth hashes, allowed reason, attempted and
restored head/tree/TCB, original authorization checkpoint, all Lease/App/
Gateway/Tombstone/Intent/Provider references and full hashes, CAS operation
digest, predecessor/new state tuple, rollback time, Controller core/signature.
Resolve the unique first full-quorum checkpoint containing the referenced
Activation entry and require the record's `authorizationCheckpointSha256`,
`authorizationCheckpointTreeSize`, and `authorizationCheckpointIssuedAt` to
equal that actual checkpoint. Mutate each of the three independently, add a
later otherwise valid checkpoint, and prove neither the later checkpoint nor a
caller-selected same-tree checkpoint is accepted.

- [ ] **Step 2: Compose Plan 07 success evidence**

Call production `verifyRecoveryFullPrefix` and require one successful exact
CAS from attempted head to reset head with target TCB equal `previousTcb`.
Reject test-only recovery results, App-only success, wrong marker, unknown
provider outcome, different restore receipt, or completion after rollback
deadline.

- [ ] **Step 3: Add discarded-epoch mutations**

After rollback checkpoint, assert all Acceptance Receipts from the discarded
epoch remain historical but cannot support a gate. Reject state reactivation,
second rollback, missing all-gates-red derivation, and a receipt that binds the
old epoch with the restored TCB bytes.

- [ ] **Step 4: Run and confirm RED**

Expected: rollback schema/composition missing.

- [ ] **Step 5: Generate the rollback schema and implement replay**

Use the exact closed payload. Require
`activationCheckpoint.issuedAt < rolledBackAt <= rollbackEntry.loggedAt <=
rollbackCheckpoint.issuedAt <= rollbackValidUntil`. Activate restored TCB only
at the rollback checkpoint, increment epoch exactly once, set state ID to
`rollbackId`, and permanently record the discarded epoch. The
`activationCheckpoint` variable is obtained only by exact resolution against
the already verified full checkpoint chain; no field carried by the Rollback
record selects or synthesizes it.

- [ ] **Step 6: Run and confirm GREEN**

Expected: valid rollback passes; every recovery, marker, receipt, time, state,
and discarded-epoch mutation fails.

- [ ] **Step 7: Commit normal rollback**

```powershell
git add docs/governance/schemas/validator-rollback-record.schema.json scripts/fixtures/governance/tcb/valid-normal-rollback.json scripts/governance/schema-builders/tcb.mjs scripts/governance/tcb-verifier-internal.mjs scripts/governance/tcb-verifier.test.mjs
git commit -m "feat: verify TCB rollback records"
```

### Task 5: Validate emergency recovery authorization, completion, and abort

**Files:**

- Create: `docs/governance/schemas/emergency-tcb-recovery.schema.json`
- Create: `scripts/fixtures/governance/tcb/valid-emergency-recovery.json`
- Modify: `scripts/governance/schema-builders/tcb.mjs`
- Modify: `scripts/governance/tcb-verifier-internal.mjs`
- Modify: `scripts/governance/tcb-verifier.test.mjs`

- [ ] **Step 1: Write Authorized-phase RED tests**

Require exact incident artifact, branch, compromised expected head, target
receipt/head/tree/TCB, predecessor state, reserved epoch=current+1, authorization
times/core, and Controller+Operator+Root(+post-Pilot Custodians) signatures.
Expiry is at most 15 minutes; expiration alone never unlocks.
The Authorized entry becomes a reservation only at the unique first
full-quorum checkpoint that contains it. Store that checkpoint's full hash,
tree size, and issued time in the reservation state; a second same-size bridge
or later checkpoint must not replace it.

- [ ] **Step 2: Write Completed-phase RED tests**

Require exact Authorization entry/checkpoint, Lease, observed restored head/tree,
restored TCB, all Plan 07 evidence, predecessor/reserved state, completion time,
Controller core/signature, and checkpoint no later than authorization expiry.
Only a successful independently verified CAS may complete.
Resolve the checkpoint again from the referenced Authorization entry and require
all three signed checkpoint fields to equal both the actual checkpoint and the
stored reservation tuple.

- [ ] **Step 3: Write Aborted-phase RED tests**

Cover all six abort reasons and the exact three proof modes: no Lease/no proof,
checkpointed `gateway-cancelled`, or checkpointed
`gateway-settled-failure`. Test every nullable combination. Unknown provider
outcome, uncheckpointed proof, or post-dispatch cancel without Zero-Byte
Closure cannot abort.
The Abort record binds the same actual Authorization checkpoint tuple as the
reservation. A null Lease is legal only when the production Recovery replay has
no operation whose `authorizationEntrySha256` equals this Authorization entry;
it may not hide an issued/running/unknown/failed/succeeded operation. An
existing operation may release the reservation only with checkpointed final
`gateway-cancelled` plus required Closure or final
`gateway-settled-failure`. Running, unknown, or succeeded state throws and the
reservation remains byte-identical.

- [ ] **Step 4: Add reservation/fork/retry mutations**

While authorized, reject any Receipt, release, second TCB transition, or second
recovery reservation. Completion activates reserved epoch; Abort releases it
only at its checkpoint without changing active state. Retry requires new
Recovery ID, Lease, correlation, Tombstone, and full authorization threshold.

- [ ] **Step 5: Run and confirm RED**

Expected: three-phase schema/replay missing.

- [ ] **Step 6: Generate the discriminated schema and implement total replay**

Use `oneOf` branches for `authorized`, `completed`, and `aborted`, each with
the exact field set in §6.3. The replay state machine has no default success
branch. Completed state ID/hash use the full Completion log entry; Abort does
not create a TCB state or reactivate gates. Checkpoint resolution uses only the
ordered, production-verified complete Checkpoint prefix. Failure to resolve one
unique first containing checkpoint, any checkpoint-field mismatch, a hidden
operation behind null Lease, or any nonfinal Recovery state is a throwing
transition and therefore restores the prior reservation snapshot.

- [ ] **Step 7: Run and confirm GREEN**

Expected: valid Authorization→Completion and Authorization→Abort pass; every
nullability, proof, reservation, retry, time, threshold, and fork mutation fails.

- [ ] **Step 8: Commit emergency recovery**

```powershell
git add docs/governance/schemas/emergency-tcb-recovery.schema.json scripts/fixtures/governance/tcb/valid-emergency-recovery.json scripts/governance/schema-builders/tcb.mjs scripts/governance/tcb-verifier-internal.mjs scripts/governance/tcb-verifier.test.mjs
git commit -m "feat: verify emergency TCB recovery"
```

### Task 6: Lock RFC-8785 TCB artifact cores

**Files:**

- Create: `scripts/fixtures/governance/tcb/rfc8785-cores.json`
- Modify: `scripts/governance/tcb-verifier.test.mjs`

- [ ] **Step 1: Add literal independent vectors**

For Promotion Request signatures, Activation, Rollback Authorization,
Activation Bundle, Rollback Record, and each Emergency phase, store the full
fixture, exact exclusion list, literal canonical core bytes as base64url, and
independently fixed SHA-256. Store full signed-artifact and full log-entry
hashes separately; do not derive expected values with production canonicalization.

- [ ] **Step 2: Add every-field mutation loops**

Mutate each bound field independently and require the relevant core hash to
change. Mutate excluded core/signature fields and require only the surrounding
full-artifact or entry hash to change. Explicitly test previous state epoch,
ID, and hash independently so repeating the five TCB digests cannot hide stale state.

- [ ] **Step 3: Run and confirm GREEN**

Expected: all literal core/full-artifact/full-entry bytes and mutations pass.

- [ ] **Step 4: Commit TCB golden vectors**

```powershell
git add scripts/fixtures/governance/tcb/rfc8785-cores.json scripts/governance/tcb-verifier.test.mjs
git commit -m "test: lock TCB RFC 8785 cores"
```

### Task 7: Integrate the complete TCB state machine

**Files:**

- Create: `scripts/fixtures/governance/tcb/mutations.json`
- Modify: `scripts/governance/tcb-verifier-internal.mjs`
- Modify: `scripts/governance/tcb-verifier.mjs`
- Modify: `scripts/governance/transparency-verifier.mjs`
- Modify: `scripts/governance/nonce-replay.mjs`
- Modify: `scripts/governance/nonce-replay.test.mjs`
- Modify: `scripts/governance-contract.mjs`
- Modify: `scripts/governance-contract.test.mjs`

- [ ] **Step 1: Write full-chain RED integration tests**

Replay Bootstrap epoch 1, Promotion Reset, Activation, new Receipt, Normal
Rollback, second Promotion, Emergency Authorization+Abort, and new Emergency
Authorization+Completion. Assert one linear active state at every log index.

- [ ] **Step 2: Add import and test-only boundary tests**

Only `tcb-verifier.mjs` and its test may import the internal core. Production
must reject invalid signatures even when an extra caller property requests a
test verifier, and reject every `testOnly` recovery/transparency result.
Raw pins/time may produce only the branded cryptographic/semantic base result.
A plain/fabricated or `pre-genesis-ceremony` AuthorityContext cannot elevate
it; a stale/partial Governance-Nonce prefix or context bound to another
Transparency bundle fails. Before Plan 11, a valid public replay must expose
`cryptographicValid:true`, `semanticValid:true`, the named authority
requirement, and `gateEffective:false`. Prove Plan 11 can consume the base brand
without calling the optional gate pass, eliminating an issuer cycle.

In the same RED wave, modify only Plan 06's `GOVERNANCE_NONCE_PATHS` source
literal. Every entry has exactly `owned/references`, both frozen arrays of
strings in the same dot/`[]` path grammar without a leading `$.`. Do not rename
the literal, call `Object.assign`, export a mutation API, or mutate it at
runtime. Insert these properties before the enclosing `Object.freeze` executes:

```js-fragment
"validator-promotion-request": Object.freeze({
  owned: Object.freeze(["nonce", "authorizationSignatures[].nonce"]), references: Object.freeze([]),
}),
"validator-activation": Object.freeze({
  owned: Object.freeze(["activationNonce", "controllerSignature.nonce"]), references: Object.freeze([]),
}),
"validator-rollback-authorization": Object.freeze({
  owned: Object.freeze(["authorizationSignatures[].nonce"]), references: Object.freeze([]),
}),
"validator-activation-bundle": Object.freeze({
  owned: Object.freeze(["instanceSignature.nonce", "controllerSignature.nonce"]), references: Object.freeze([]),
}),
"validator-rollback-record": Object.freeze({
  owned: Object.freeze(["instanceSignature.nonce", "controllerSignature.nonce"]), references: Object.freeze([]),
}),
"emergency-tcb-recovery#authorized": Object.freeze({
  owned: Object.freeze(["instanceSignature.nonce", "authorizationSignatures[].nonce"]), references: Object.freeze([]),
}),
"emergency-tcb-recovery#completed": Object.freeze({
  owned: Object.freeze(["instanceSignature.nonce", "controllerSignature.nonce"]), references: Object.freeze([]),
}),
"emergency-tcb-recovery#aborted": Object.freeze({
  owned: Object.freeze(["instanceSignature.nonce", "authorizationSignatures[].nonce"]), references: Object.freeze([]),
}),
```

The three `#phase` names are internal artifact-dispatch keys, not three file
schemas and not caller fields. Only after `emergency-tcb-recovery.schema.json`
validates the closed discriminated object does the fixed collector derive the
matching key from `entry.phase`; unknown/missing phase fails before Nonce or
inventory dispatch. Plan 11 maps those same three virtual keys to the TCB
domain and registry tests require exact equality.

An unlisted nonce-like path, duplicate owner within a signature array or across
Bootstrap/EVT/Transparency/Recovery/TCB domains, omitted artifact, wrong phase
branch, or changed prefix hash fails the complete production replay. Any later
reference must resolve byte-for-byte to exactly one strictly earlier owner;
references neither enter the owner uniqueness set nor increase `claimCount`.
Add a source-contract test in `scripts/governance-contract.test.mjs` that
requires the TCB gate consumer to read exactly
`authorityClaims.transparency.bundleSha256`, rejects any legacy top-level
bundle-hash claim, and proves the standalone replay
still exposes `inventoryBindingVerified:false` before Plan 11 composition.

- [ ] **Step 3: Run and confirm RED**

Expected: central transparency/contract replay does not yet derive all TCB states.

- [ ] **Step 4: Register TCB log-entry semantics**

Add `tcb-activation`, `tcb-rollback`, and
`tcb-emergency-recovery` to production transparency delegation. Preserve the
single common log envelope; do not introduce a parallel TCB log. Derive current
gate effectiveness only from the active epoch/ID/full-entry-hash tuple.

- [ ] **Step 5: Wire the immutable production wrapper**

`tcb-verifier.mjs` fixes real Ed25519, production transparency, production
recovery, and the complete Plan-06 Nonce replay in its module body. It first
uses bundle, typed lifecycle artifacts, the complete ordered `nonceArtifacts`
prefix, repository state, and raw `verificationInputs` to create a real,
branded, non-gate base replay. Plan 11 consumes that base only through
`isProductionTcbResult` in Issuer Phase A. The optional later gate pass consumes
claims only through `readProductionAuthorityContext`; those claims are
byte-bound to the same pins, Trusted Time, Transparency bundle, and
Governance-Nonce prefix. No caller verifier is accepted, and raw pins/time
alone never authorize a gate.

Implement this total replay core. It receives only already production-verified
transparency/recovery results; invalid entries are never partially applied.

```js
// tcb-verifier-internal.mjs
import { canonicalBytes } from "./rfc8785.mjs";
import { sha256Hex } from "./crypto.mjs";
import { validateSchema } from "./schema-registry.mjs";

const without = (value, names) => Object.fromEntries(Object.entries(value)
  .filter(([name]) => !names.includes(name)));
const hash = (value) => sha256Hex(canonicalBytes(value));
const time = (value) => { const result = Date.parse(value); if (!Number.isFinite(result)) throw new TypeError(`invalid time ${value}`); return result; };
const sameTcb = (left, right) => canonicalBytes(left).equals(canonicalBytes(right));
const stateTupleMatches = (entry, state, epochName = "previousTcbStateEpoch") =>
  entry[epochName] === state.tcbStateEpoch
  && entry.previousTcbStateEntryId === state.tcbStateEntryId
  && entry.previousTcbStateEntrySha256 === state.tcbStateEntrySha256;
const fullQuorumCheckpointFor = (entry, checkpoints) => {
  const index = checkpoints.findIndex((checkpoint) =>
    checkpoint.treeSize > entry.transparencyLogIndex);
  if (index < 0) throw new Error("TCB_FULL_QUORUM_CHECKPOINT_MISSING");
  const checkpoint = checkpoints[index];
  if (checkpoints.slice(0, index).some((candidate) =>
    candidate.treeSize > entry.transparencyLogIndex)) {
    throw new Error("TCB_FIRST_CONTAINING_CHECKPOINT_AMBIGUOUS");
  }
  return Object.freeze({ checkpoint, checkpointSha256: hash(checkpoint), index });
};
const requireAuthorizationCheckpointBinding = (carrier, authorizedEntry, checkpoints) => {
  const actual = fullQuorumCheckpointFor(authorizedEntry, checkpoints);
  if (carrier.authorizationCheckpointSha256 !== actual.checkpointSha256
    || carrier.authorizationCheckpointTreeSize !== actual.checkpoint.treeSize
    || carrier.authorizationCheckpointIssuedAt !== actual.checkpoint.issuedAt) {
    throw new Error("TCB_AUTHORIZATION_CHECKPOINT_BINDING_INVALID");
  }
  return actual;
};
const requireSchema = (name, value) => {
  const errors = validateSchema(name, value);
  if (errors.length) throw new Error(`TCB_SCHEMA_INVALID:${name}`);
};
const verifyCoreSignature = ({ value, coreExclusions, coreField, signature,
  publicKeyBase64url, verifySignature }) => {
  const core = without(value, coreExclusions);
  const coreSha256 = hash(core);
  if (signature[coreField] !== coreSha256
    || !verifySignature({ publicKeyBase64url, payloadBytes: canonicalBytes(core),
      signatureBase64url: signature.signature })) throw new Error(`TCB_SIGNATURE_INVALID:${coreField}`);
  return coreSha256;
};
const sortedUnique = (items, key) => items.every((item, index) =>
  index === 0 || key(items[index - 1]) < key(item));
const COMMON_LOG_FIELDS = ["schemaVersion", "entryKind", "repositoryId", "logId",
  "transparencyLogIndex", "previousLogEntrySha256", "loggedAt", "instanceKeyRef",
  "instanceKeyEpoch", "method", "entryCoreSha256", "instanceSignature"];
const payloadOf = (entry) => without(entry, COMMON_LOG_FIELDS);
function verifyControllerPayload({ payload, coreField, signatureField,
  externalPins, verifySignature }) {
  const signature = payload[signatureField];
  if (!signature || signature.keyRef !== externalPins.validatorController.keyRef) {
    throw new Error("TCB_CONTROLLER_PIN_MISMATCH");
  }
  verifyCoreSignature({ value: payload, coreExclusions: [coreField, signatureField],
    coreField, signature, publicKeyBase64url: externalPins.validatorController.publicKeyBase64url,
    verifySignature });
}
function verifyRecoveryBindings(entry, operation, recoveryArtifacts) {
  const refs = [
    ["recoveryAppAttestationRef", "recoveryAppAttestationSha256", recoveryArtifacts.appAttestations],
    ["gatewayAcceptedReceiptRef", "gatewayAcceptedReceiptSha256", recoveryArtifacts.gatewayReceipts],
    ["recoveryIdempotencyTombstoneRef", "recoveryIdempotencyTombstoneSha256", recoveryArtifacts.tombstones],
    ["recoveryEgressIntentRef", "recoveryEgressIntentSha256", recoveryArtifacts.intents],
    ["gatewayDispatchStartedReceiptRef", "gatewayDispatchStartedReceiptSha256", recoveryArtifacts.gatewayReceipts],
    ["gatewaySettledReceiptRef", "gatewaySettledReceiptSha256", recoveryArtifacts.gatewayReceipts],
    ["providerReceiptRef", "providerReceiptSha256", recoveryArtifacts.providerReceipts],
  ];
  for (const [refField, hashField, collection] of refs) {
    const artifact = collection.find((item) => item.ref === entry[refField]);
    if (!artifact || hash(artifact.value ?? artifact) !== entry[hashField]) {
      throw new Error(`TCB_RECOVERY_ARTIFACT_BINDING:${refField}`);
    }
  }
  const provider = recoveryArtifacts.providerReceipts.find((item) =>
    hash(item.value ?? item) === entry.providerReceiptSha256)?.value
    ?? recoveryArtifacts.providerReceipts.find((item) => hash(item) === entry.providerReceiptSha256);
  if (!provider || provider.result !== "succeeded"
    || provider.observedRefOidBefore !== entry.attemptedHeadCommit
    || provider.observedRefOidAfter !== (entry.restoreHeadCommit ?? entry.observedRestoredHeadCommit)
    || provider.observedProviderMarkerOid !== provider.targetRefOid
    || sha256Hex(Buffer.from(provider.operationCorrelationId, "utf8")) !== entry.compareAndSwapOperationIdSha256
    || operation.gatewayPhase !== "settled" || operation.providerResult !== "succeeded") {
    throw new Error("TCB_RECOVERY_CAS_BINDING_INVALID");
  }
}

function verifyRoleThreshold({ value, coreExclusions, coreField, signatures,
  purposes, externalPins, verifySignature, pilotWasGreen }) {
  const required = (pilotWasGreen
    ? [...purposes] : purposes.filter((purpose) => !["custodian-a", "custodian-b"].includes(purpose)))
    .sort((left, right) => left < right ? -1 : left > right ? 1 : 0);
  if (!sortedUnique(signatures, (item) => `${item.purpose}\u0000${item.keyRef}`)
    || signatures.map((item) => item.purpose).join("\u0000") !== required.join("\u0000")) {
    throw new Error("TCB_SIGNATURE_THRESHOLD_INVALID");
  }
  for (const signature of signatures) {
    const pin = externalPins.roles[signature.purpose];
    if (!pin || pin.keyRef !== signature.keyRef || pin.signerRole !== signature.signerRole
      || pin.signerIdentity !== signature.signerIdentity) throw new Error("TCB_SIGNER_PIN_MISMATCH");
    verifyCoreSignature({ value, coreExclusions, coreField, signature,
      publicKeyBase64url: pin.publicKeyBase64url, verifySignature });
  }
}

function validatePromotion({ request, repositoryState, state, externalPins,
  verifySignature, pilotWasGreen }) {
  requireSchema("validator-promotion-request", request);
  if (!stateTupleMatches(request, state)) throw new Error("TCB_PROMOTION_STALE_STATE");
  const green = repositoryState.gates.filter((gate) => gate.status === "green")
    .sort((a, b) => a.id < b.id ? -1 : a.id > b.id ? 1 : 0);
  if (request.gateResetPlan.length !== green.length) throw new Error("TCB_GATE_RESET_NOT_COMPLETE");
  for (let index = 0; index < green.length; index += 1) {
    const plan = request.gateResetPlan[index], gate = green[index];
    if (plan.gateRef !== gate.id || plan.previousRecordSha256 !== hash(gate.record)
      || plan.resultingRedRecordSha256 !== hash({ ...gate.record, status: "red" })) {
      throw new Error("TCB_GATE_RESET_PLAN_MISMATCH");
    }
  }
  const resetDigest = hash({ repositoryId: request.repositoryId,
    promotionEvidenceRef: request.promotionEvidenceRef, gateResetPlan: request.gateResetPlan });
  if (request.gateResetTransactionSha256 !== resetDigest
    || repositoryState.promotionEvidence.scope !== `governance-transaction:tcb-promotion:${resetDigest}`) {
    throw new Error("TCB_GATE_RESET_DIGEST_MISMATCH");
  }
  if (!(time(request.activationNotBefore) < time(request.expiresAt)
    && time(request.expiresAt) < time(request.rollbackValidUntil))
    || time(request.rollbackValidUntil) - time(request.expiresAt) < 3_600_000
    || time(request.rollbackValidUntil) - time(request.expiresAt) > 86_400_000) {
    throw new Error("TCB_PROMOTION_TIME_WINDOW_INVALID");
  }
  verifyRoleThreshold({ value: request, coreExclusions: ["authorizationSignatures"],
    coreField: "promotionCoreSha256", signatures: request.authorizationSignatures,
    purposes: ["operator", "recovery-root", "custodian-a", "custodian-b"],
    externalPins, verifySignature, pilotWasGreen });
}

export function verifyTcbLifecycleCore({ bundle, artifacts, repositoryState,
  externalPins, verificationTime, transparencyReplay, recoveryReplay }, { verifySignature }) {
  if (!transparencyReplay?.cryptographicValid || transparencyReplay.testOnly
    || !recoveryReplay?.cryptographicValid || !recoveryReplay?.semanticValid
    || recoveryReplay.testOnly) {
    throw new Error("TCB_REQUIRES_CRYPTOGRAPHIC_DEPENDENCY_REPLAYS");
  }
  const state = { tcbStateEpoch: 1, tcbStateEntryId: null, tcbStateEntrySha256: null,
    activeTcb: structuredClone(externalPins.bootstrapTcb), reservedRecovery: null,
    consumedPromotionRequests: new Set(), discardedEpochs: new Set(), gatesForcedRed: false };
  const effective = bundle.entries.flatMap((entry) => {
    const index = bundle.checkpoints.findIndex((checkpoint) =>
      checkpoint.treeSize > entry.transparencyLogIndex);
    return index < 0 ? [] : [{ entry, checkpoint: bundle.checkpoints[index] }];
  });
  for (const { entry, checkpoint } of effective) {
    const snapshot = structuredClone({ ...state,
      consumedPromotionRequests: [...state.consumedPromotionRequests],
      discardedEpochs: [...state.discardedEpochs] });
    try {
      if (entry.entryKind === "acceptance-receipt") {
        if (state.reservedRecovery) throw new Error("TCB_RECEIPT_DURING_RECOVERY_RESERVATION");
        if (entry.tcbStateEpoch !== state.tcbStateEpoch
          || entry.tcbStateEntryId !== state.tcbStateEntryId
          || entry.tcbStateEntrySha256 !== state.tcbStateEntrySha256
          || !sameTcb({ validatorImageDigest: entry.validatorImageDigest,
            policySha256: entry.validatorPolicySha256, workflowSha256: entry.workflowSha256,
            schemaSetSha256: entry.schemaSetSha256, trustProtocolSha256: entry.trustProtocolSha256 }, state.activeTcb)) {
          throw new Error("TCB_RECEIPT_STATE_MISMATCH");
        }
      } else if (entry.entryKind === "tcb-activation") {
        requireSchema("validator-activation-bundle", entry);
        if (state.reservedRecovery || !stateTupleMatches(entry, state)
          || entry.tcbStateEpoch !== state.tcbStateEpoch + 1) throw new Error("TCB_ACTIVATION_PREDECESSOR_INVALID");
        const activation = artifacts.activations.find((item) => hash(item) === entry.activationSha256);
        const rollback = artifacts.rollbackAuthorizations.find((item) => hash(item) === entry.rollbackAuthorizationSha256);
        const request = artifacts.promotionRequests.find((item) => hash(item) === entry.requestSha256);
        if (!activation || !rollback || !request) throw new Error("TCB_ACTIVATION_ARTIFACT_MISSING");
        validatePromotion({ request, repositoryState, state, externalPins,
          verifySignature, pilotWasGreen: repositoryState.pilotWasGreen });
        requireSchema("validator-activation", activation);
        requireSchema("validator-rollback-authorization", rollback);
        verifyControllerPayload({ payload: activation, coreField: "activationCoreSha256",
          signatureField: "controllerSignature", externalPins, verifySignature });
        verifyRoleThreshold({ value: rollback,
          coreExclusions: ["rollbackCoreSha256", "authorizationSignatures"],
          coreField: "rollbackCoreSha256", signatures: rollback.authorizationSignatures,
          purposes: ["controller", "operator", "recovery-root", "custodian-a", "custodian-b"],
          externalPins, verifySignature, pilotWasGreen: repositoryState.pilotWasGreen });
        verifyControllerPayload({ payload: payloadOf(entry), coreField: "controllerBundleCoreSha256",
          signatureField: "controllerSignature", externalPins, verifySignature });
        if (state.consumedPromotionRequests.has(entry.requestSha256)
          || !sameTcb(activation.nextTcb, entry.nextTcb)
          || !sameTcb(activation.previousTcb, state.activeTcb)
          || rollback.activationSha256 !== entry.activationSha256
          || rollback.requestSha256 !== entry.requestSha256
          || !sameTcb(rollback.previousTcb, state.activeTcb)
          || !sameTcb(rollback.nextTcb, entry.nextTcb)
          || rollback.rollbackValidUntil !== entry.rollbackValidUntil
          || activation.requestSha256 !== entry.requestSha256
          || activation.activationId !== entry.activationId
          || activation.resetReceiptId !== rollback.rollbackHeadReceiptId
          || activation.resetHeadCommit !== rollback.rollbackHeadCommit
          || activation.resetHeadTreeOid !== rollback.rollbackHeadTreeOid
          || repositoryState.resetHeadCommit !== activation.resetHeadCommit
          || repositoryState.resetHeadTreeOid !== activation.resetHeadTreeOid
          || repositoryState.gatesAtResetHead.some((gate) => gate.status !== "red")
          || time(request.activationNotBefore) > time(checkpoint.issuedAt)
          || time(checkpoint.issuedAt) > time(request.expiresAt)) throw new Error("TCB_ACTIVATION_BINDING_INVALID");
        state.consumedPromotionRequests.add(entry.requestSha256);
        state.tcbStateEpoch = entry.tcbStateEpoch; state.tcbStateEntryId = entry.activationId;
        state.tcbStateEntrySha256 = hash(entry); state.activeTcb = structuredClone(entry.nextTcb);
        state.gatesForcedRed = true;
      } else if (entry.entryKind === "tcb-rollback") {
        requireSchema("validator-rollback-record", entry);
        if (state.reservedRecovery || !stateTupleMatches(entry, state)
          || entry.tcbStateEpoch !== state.tcbStateEpoch + 1) throw new Error("TCB_ROLLBACK_PREDECESSOR_INVALID");
        verifyControllerPayload({ payload: payloadOf(entry), coreField: "rollbackRecordCoreSha256",
          signatureField: "controllerSignature", externalPins, verifySignature });
        const operation = recoveryReplay.operations.find((item) =>
          item.leaseId === entry.recoveryOperationLeaseId);
        const activationEntry = bundle.entries.find((item) => item.entryKind === "tcb-activation"
          && item.activationId === entry.activationId);
        const rollbackAuthorization = artifacts.rollbackAuthorizations
          .find((item) => hash(item) === entry.rollbackAuthorizationSha256);
        if (!activationEntry || hash(activationEntry) !== entry.activationEntrySha256) {
          throw new Error("TCB_ROLLBACK_ACTIVATION_MISSING");
        }
        const activationCheckpoint = requireAuthorizationCheckpointBinding(
          entry, activationEntry, bundle.checkpoints).checkpoint;
        if (!operation || operation.gatewayPhase !== "settled" || operation.providerResult !== "succeeded"
          || operation.authorizationEntrySha256 !== entry.activationEntrySha256
          || operation.leaseEntrySha256 !== entry.recoveryOperationLeaseSha256
          || !rollbackAuthorization
          || !rollbackAuthorization.allowedReasons.includes(entry.reason)
          || !sameTcb(entry.restoredTcb, rollbackAuthorization.previousTcb)
          || entry.restoreReceiptId !== rollbackAuthorization.rollbackHeadReceiptId
          || entry.restoreHeadCommit !== rollbackAuthorization.rollbackHeadCommit
          || entry.restoreHeadTreeOid !== rollbackAuthorization.rollbackHeadTreeOid
          || time(activationCheckpoint.issuedAt) >= time(entry.rolledBackAt)
          || time(entry.rolledBackAt) > time(entry.loggedAt)
          || time(entry.loggedAt) > time(checkpoint.issuedAt)
          || time(checkpoint.issuedAt) > time(rollbackAuthorization.rollbackValidUntil)) {
          throw new Error("TCB_ROLLBACK_RECOVERY_EVIDENCE_INVALID");
        }
        verifyRecoveryBindings(entry, operation, artifacts.recovery);
        state.discardedEpochs.add(state.tcbStateEpoch); state.tcbStateEpoch = entry.tcbStateEpoch;
        state.tcbStateEntryId = entry.rollbackId; state.tcbStateEntrySha256 = hash(entry);
        state.activeTcb = structuredClone(entry.restoredTcb); state.gatesForcedRed = true;
      } else if (entry.entryKind === "tcb-emergency-recovery") {
        requireSchema("emergency-tcb-recovery", entry);
        if (entry.phase === "authorized") {
          if (state.reservedRecovery || !stateTupleMatches(entry, state)
            || entry.reservedTcbStateEpoch !== state.tcbStateEpoch + 1
            || time(entry.authorizedAt) >= time(entry.authorizationExpiresAt)
            || time(entry.authorizationExpiresAt) - time(entry.authorizedAt) > 900_000
            || time(entry.authorizedAt) > time(entry.loggedAt)
            || time(entry.loggedAt) > time(checkpoint.issuedAt)
            || time(checkpoint.issuedAt) > time(entry.authorizationExpiresAt)) {
            throw new Error("TCB_RECOVERY_AUTHORIZATION_INVALID");
          }
          verifyRoleThreshold({ value: payloadOf(entry),
            coreExclusions: ["recoveryAuthorizationCoreSha256", "authorizationSignatures"],
            coreField: "recoveryAuthorizationCoreSha256", signatures: entry.authorizationSignatures,
            purposes: ["controller", "operator", "recovery-root", "custodian-a", "custodian-b"],
            externalPins, verifySignature, pilotWasGreen: repositoryState.pilotWasGreen });
          const authorizationCheckpoint = fullQuorumCheckpointFor(entry, bundle.checkpoints);
          if (authorizationCheckpoint.checkpoint !== checkpoint) {
            throw new Error("TCB_RECOVERY_AUTHORIZATION_CHECKPOINT_NOT_FIRST");
          }
          state.reservedRecovery = { recoveryId: entry.recoveryId,
            reservedTcbStateEpoch: entry.reservedTcbStateEpoch,
            authorizationEntrySha256: hash(entry), authorizationExpiresAt: entry.authorizationExpiresAt,
            authorizationCheckpointSha256: authorizationCheckpoint.checkpointSha256,
            authorizationCheckpointTreeSize: checkpoint.treeSize,
            authorizationCheckpointIssuedAt: checkpoint.issuedAt };
          state.gatesForcedRed = true;
        } else {
          const reservation = state.reservedRecovery;
          if (!reservation || reservation.recoveryId !== entry.recoveryId
            || reservation.authorizationEntrySha256 !== entry.authorizationEntrySha256) {
            throw new Error("TCB_RECOVERY_RESERVATION_MISMATCH");
          }
          const authorization = bundle.entries.find((item) => hash(item) === entry.authorizationEntrySha256
            && item.entryKind === "tcb-emergency-recovery" && item.phase === "authorized");
          if (!authorization) throw new Error("TCB_RECOVERY_AUTHORIZATION_MISSING");
          const authorizationCheckpoint = requireAuthorizationCheckpointBinding(
            entry, authorization, bundle.checkpoints);
          if (reservation.authorizationCheckpointSha256 !== authorizationCheckpoint.checkpointSha256
            || reservation.authorizationCheckpointTreeSize !== authorizationCheckpoint.checkpoint.treeSize
            || reservation.authorizationCheckpointIssuedAt !== authorizationCheckpoint.checkpoint.issuedAt) {
            throw new Error("TCB_RECOVERY_RESERVATION_CHECKPOINT_MISMATCH");
          }
          if (entry.phase === "completed") {
            const operation = recoveryReplay.operations.find((item) => item.leaseId === entry.recoveryOperationLeaseId);
            verifyControllerPayload({ payload: payloadOf(entry), coreField: "recoveryCompletionCoreSha256",
              signatureField: "controllerSignature", externalPins, verifySignature });
            if (!operation || operation.gatewayPhase !== "settled" || operation.providerResult !== "succeeded"
              || operation.authorizationEntrySha256 !== entry.authorizationEntrySha256
              || operation.leaseEntrySha256 !== entry.recoveryOperationLeaseSha256
              || authorization.recoveryId !== entry.recoveryId
              || entry.branch !== authorization.branch
              || entry.observedRestoredHeadCommit !== authorization.recoveryTargetHeadCommit
              || entry.observedRestoredHeadTreeOid !== authorization.recoveryTargetHeadTreeOid
              || !sameTcb(entry.restoredTcb, authorization.recoveryTargetTcb)
              || entry.previousTcbStateEpoch !== authorization.previousTcbStateEpoch
              || entry.previousTcbStateEntryId !== authorization.previousTcbStateEntryId
              || entry.previousTcbStateEntrySha256 !== authorization.previousTcbStateEntrySha256
              || entry.tcbStateEpoch !== reservation.reservedTcbStateEpoch
              || time(entry.completedAt) > time(entry.loggedAt)
              || time(entry.loggedAt) > time(checkpoint.issuedAt)
              || time(checkpoint.issuedAt) > time(reservation.authorizationExpiresAt)) {
              throw new Error("TCB_RECOVERY_COMPLETION_INVALID");
            }
            verifyRecoveryBindings({ ...entry,
              attemptedHeadCommit: authorization.expectedCompromisedHeadCommit,
              restoreHeadCommit: entry.observedRestoredHeadCommit }, operation, artifacts.recovery);
            state.discardedEpochs.add(state.tcbStateEpoch); state.tcbStateEpoch = entry.tcbStateEpoch;
            state.tcbStateEntryId = entry.recoveryId; state.tcbStateEntrySha256 = hash(entry);
            state.activeTcb = structuredClone(entry.restoredTcb);
          } else if (entry.phase === "aborted") {
            const authorizationOperations = recoveryReplay.operations.filter((item) =>
              item.authorizationEntrySha256 === entry.authorizationEntrySha256);
            const operation = entry.recoveryOperationLeaseId === null ? null
              : recoveryReplay.operations.find((item) => item.leaseId === entry.recoveryOperationLeaseId);
            verifyRoleThreshold({ value: payloadOf(entry),
              coreExclusions: ["recoveryAbortCoreSha256", "authorizationSignatures"],
              coreField: "recoveryAbortCoreSha256", signatures: entry.authorizationSignatures,
              purposes: ["controller", "operator", "recovery-root", "custodian-a", "custodian-b"],
              externalPins, verifySignature, pilotWasGreen: repositoryState.pilotWasGreen });
            if ((entry.recoveryOperationLeaseId === null && authorizationOperations.length !== 0)
              || (entry.recoveryOperationLeaseId !== null
                && (!operation
                  || operation.authorizationEntrySha256 !== entry.authorizationEntrySha256
                  || operation.leaseEntrySha256 !== entry.recoveryOperationLeaseSha256))) {
              throw new Error("TCB_RECOVERY_ABORT_LEASE_OMISSION_OR_MISMATCH");
            }
            const proofValid = entry.failureProofType === null
              ? operation === null && authorizationOperations.length === 0
                && ["lease-unavailable", "authorization-expired", "operator-abort"].includes(entry.abortReason)
              : entry.failureProofType === "gateway-cancelled"
                ? operation?.gatewayPhase === "cancelled" && operation?.closureReason !== null
                : entry.failureProofType === "gateway-settled-failure"
                  && operation?.gatewayPhase === "settled" && operation?.providerResult === "failed";
            if (!proofValid || operation?.providerResult === "unknown" || operation?.providerResult === "succeeded"
              || time(entry.abortedAt) > time(entry.loggedAt)
              || time(entry.loggedAt) > time(checkpoint.issuedAt)) {
              throw new Error("TCB_RECOVERY_ABORT_UNCERTAIN_OR_SUCCESSFUL");
            }
          } else throw new Error("TCB_RECOVERY_PHASE_UNKNOWN");
          state.reservedRecovery = null;
        }
      }
    } catch (error) {
      Object.assign(state, snapshot, { consumedPromotionRequests: new Set(snapshot.consumedPromotionRequests),
        discardedEpochs: new Set(snapshot.discardedEpochs) });
      throw error;
    }
  }
  return { errors: [], state: { ...state,
    consumedPromotionRequests: [...state.consumedPromotionRequests].sort(),
    discardedEpochs: [...state.discardedEpochs].sort((a, b) => a - b) },
    verifiedAt: verificationTime };
}
```

Production wrapping and branding are exact:

```js
// tcb-verifier.mjs
import { fullArtifactSha256, verifyEd25519 } from "./crypto.mjs";
import { verifyGovernanceNoncePrefix } from "./nonce-replay.mjs";
import { readProductionAuthorityContext } from "./production-authority-context.mjs";
import { verifyTransparencyBundle } from "./transparency-verifier.mjs";
import { verifyRecoveryFullPrefix } from "./recovery-verifier.mjs";
import { verifyTcbLifecycleCore } from "./tcb-verifier-internal.mjs";
const productionResults = new WeakSet();
const readAuthorityOrNull = (value) => {
  try { return readProductionAuthorityContext(value); }
  catch (error) { if (error instanceof TypeError) return null; throw error; }
};
const gateAuthorityMatches = ({ authorityContext, bundle, externalPins,
  verificationTime, noncePrefixSha256, artifactSetSha256 }) => {
  const authorityClaims = readAuthorityOrNull(authorityContext);
  if (authorityClaims === null || authorityClaims.profile !== "gate-evaluation"
    || authorityClaims.gateEffective !== true) return false;
  if (fullArtifactSha256(bundle) !== authorityClaims.transparency.bundleSha256) {
    throw new Error("TCB_AUTHORITY_BUNDLE_MISMATCH");
  }
  if (fullArtifactSha256(externalPins) !== authorityClaims.externalPinsSha256
    || verificationTime !== authorityClaims.trustedTime.now
    || noncePrefixSha256 !== authorityClaims.noncePrefixSha256
    || artifactSetSha256 !== authorityClaims.artifactSetSha256) {
    throw new Error("TCB_AUTHORITY_INPUT_MISMATCH");
  }
  return true;
};
export function verifyTcbLifecycle({ bundle, artifacts, nonceArtifacts,
  repositoryState, verificationInputs, authorityContext = null }) {
  const externalPins = verificationInputs?.externalPins;
  const verificationTime = verificationInputs?.verificationTime;
  const transparencyReplay = verifyTransparencyBundle({ bundle,
    externalPins, verificationTime });
  const recoveryReplay = verifyRecoveryFullPrefix({ bundle, artifacts: artifacts.recovery,
    nonceArtifacts, verificationInputs, authorityContext: null });
  const nonceReplay = verifyGovernanceNoncePrefix({ artifacts: nonceArtifacts });
  if (!nonceReplay.cryptographicValid || nonceReplay.testOnly) {
    throw new Error("TCB_NONCE_PREFIX_INVALID");
  }
  const core = verifyTcbLifecycleCore({ bundle, artifacts, repositoryState,
    externalPins, verificationTime,
    transparencyReplay, recoveryReplay }, { verifySignature: verifyEd25519 });
  const gateAuthorized = gateAuthorityMatches({ authorityContext, bundle, externalPins,
    verificationTime, noncePrefixSha256: nonceReplay.noncePrefixSha256,
    artifactSetSha256: nonceReplay.artifactSetSha256 });
  const result = Object.freeze({ ...core, testOnly: false, cryptographicValid: true,
    semanticValid: core.errors.length === 0,
    authorityRequired: gateAuthorized ? [] : ["production-authority-context"],
    gateEffective: gateAuthorized && core.errors.length === 0
      && !core.state.reservedRecovery });
  productionResults.add(result);
  return result;
}
export function isProductionTcbResult(value) {
  return productionResults.has(value) && value.cryptographicValid === true
    && value.semanticValid === true && value.testOnly === false;
}
export function deriveActiveTcbState({ verifiedReplay }) {
  if (!productionResults.has(verifiedReplay) || !verifiedReplay.gateEffective) {
    throw new TypeError("active TCB requires a gate-effective production replay");
  }
  return verifiedReplay.state;
}
```

The test suite exercises each adjacent timeline inequality with ±1 ms,
including activation, rollback, Authorized→Completed, and Authorized→Abort;
every thrown transition leaves the state byte-identical to its snapshot.

- [ ] **Step 6: Run Plan 08 gates**

```powershell
node --test scripts/governance/tcb-verifier.test.mjs scripts/governance/recovery-verifier.test.mjs scripts/governance/transparency-verifier.test.mjs scripts/governance-contract.test.mjs
npm run check:canon
npm run typecheck:governance
npm run typecheck
npm run lint
git diff --check
```

Expected: all local TCB/recovery/transparency tests and static gates pass;
live activation/recovery remain named authority stops.

- [ ] **Step 7: Commit TCB integration**

```powershell
git add scripts/fixtures/governance/tcb/mutations.json scripts/governance/tcb-verifier-internal.mjs scripts/governance/tcb-verifier.mjs scripts/governance/transparency-verifier.mjs scripts/governance/nonce-replay.mjs scripts/governance/nonce-replay.test.mjs scripts/governance-contract.mjs scripts/governance-contract.test.mjs
git commit -m "feat: integrate TCB lifecycle replay"
```

## Plan 08 acceptance evidence

- All six schemas are closed and state-discriminated.
- Promotion request binds complete green-gate reset, current state epoch/ID/hash, reviews, thresholds, and time windows.
- Activation is inert until rollback authorization exists and a full-witness checkpoint covers the bundle.
- Normal Rollback and Emergency Completion/Abort bind the exact first full-quorum Authorization checkpoint by full hash, tree size, and issued time; a later or caller-selected checkpoint never substitutes.
- Request and state epochs prevent replay even after A→B→A digest equality.
- Normal Rollback composes only production-valid Plan 07 evidence and permanently discards the replaced epoch.
- Emergency reservation blocks all receipts/transitions until checkpointed Completion or Abort.
- Abort with a null Lease is legal only when no operation exists for that Authorization; running, unknown, or succeeded operations fail atomically and retain the reservation.
- Unknown provider outcome never becomes Abort or Completion.
- Golden core/full-artifact/full-entry vectors and one-field mutations pass.
- Production exports accept no verification callback and no test-only evidence.
- Production base verification uses real signatures and the supplied Plan-06 Nonce-prefix but remains authority-red; only Plan 11 independently proves its complete signed inventory and mints matching `gate-evaluation` claims, without an issuer cycle.
- No key, signature, remote controller action, gate reset, branch write, witness call, or server change is produced.
