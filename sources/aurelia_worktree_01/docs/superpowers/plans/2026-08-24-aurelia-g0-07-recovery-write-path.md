# AURELIA G0 Recovery Write Path Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement an offline-verifiable, replay-safe recovery write protocol from authorization checkpoint through lease, gateway, immutable tombstone, sealed egress, GitHub compare-and-swap evidence, and terminal recovery state.

**Architecture:** Recovery is derived only from the complete witness-confirmed transparency prefix; no application or gateway statement is trusted in isolation. Seven closed artifact schemas and one pure state machine enforce a single linear send attempt, externally durable idempotency, zero-byte closure, independent provider verification, and exact GitHub `updateRefs` request bytes. Production verification is fixed to Ed25519 and consumes both the complete versioned Nonce-prefix replay and the opaque `ProductionAuthorityContext` that only Plan 11 may mint; raw pins, a caller clock, or semantic test injection can never become gate-effective.

**Tech Stack:** Node.js 22 ESM, Draft-2020-12 schema registry, Plan 05 RFC-8785/Ed25519 primitives, Plan 06 transparency replay, Node test runner, GitHub GraphQL request fixtures only.

---

## Prerequisites and authority stops

Plans 05 and 06 must be green. Plan 06 provides the central versioned
`scripts/governance/nonce-replay.mjs` path. Plan 11 later supplies the opaque
production authority capability; until then every public Recovery result is
cryptographically/semantically useful but carries
`authorityRequired:["production-authority-context"]` and
`gateEffective:false`. This plan creates no GitHub token, GitHub App,
provider credential, key, signature, log append, marker ref, network namespace,
or remote request. Live recovery remains blocked until separately authorized
external App/Gateway/Verifier/Monitor pins and an isolated non-production
provider target exist. No test may call DNS, HTTPS, GitHub, a proxy, a Unix
socket, or a server.

## File map

**Create:**

- `scripts/governance/recovery-verifier-internal.mjs`
- `scripts/governance/recovery-verifier.mjs`
- `scripts/governance/recovery-verifier.test.mjs`
- `scripts/governance/recovery-provider-request.mjs`
- `scripts/governance/recovery-provider-request.test.mjs`
- `scripts/governance/schema-builders/recovery.mjs`
- `scripts/fixtures/governance/recovery/valid-success.json`
- `scripts/fixtures/governance/recovery/valid-pre-dispatch-cancel.json`
- `scripts/fixtures/governance/recovery/valid-post-dispatch-zero-byte.json`
- `scripts/fixtures/governance/recovery/state-cross-product.json`
- `scripts/fixtures/governance/recovery/rfc8785-cores.json`
- `docs/governance/schemas/recovery-operation-lease.schema.json`
- `docs/governance/schemas/recovery-write-ahead-receipt.schema.json`
- `docs/governance/schemas/recovery-idempotency-tombstone.schema.json`
- `docs/governance/schemas/recovery-egress-intent.schema.json`
- `docs/governance/schemas/recovery-egress-closure.schema.json`
- `docs/governance/schemas/recovery-app-attestation.schema.json`
- `docs/governance/schemas/provider-ref-update-receipt.schema.json`

**Modify:**

- `scripts/governance/transparency-verifier.mjs` — register the four recovery log-entry kinds and delegate their semantic replay.
- `scripts/governance/nonce-replay.mjs` — extend the closed schema-to-Nonce-path table with every Recovery-owned signature/artifact nonce and every challenge reference.
- `scripts/governance/nonce-replay.test.mjs`
- `scripts/governance-contract.mjs`
- `scripts/governance-contract.test.mjs`

## Stable production exports

```js
// recovery-verifier.mjs; no caller-supplied verifier; raw pins/time can prove
// cryptographic/semantic validity but can never authorize a gate.
// Interface contracts; complete algorithms appear in Task 8.
export function verifyRecoveryFullPrefix({ bundle, artifacts, nonceArtifacts,
  verificationInputs, authorityContext = null }) {}
export function isProductionRecoveryResult(value) {}
export function deriveRecoveryOperationState({ verifiedReplay, leaseId }) {}

// recovery-provider-request.mjs; pure byte validation
export function validateGitHubUpdateRefsRequest({
  requestBytes,
  branch,
  pinnedBranch,
  repositoryNodeId,
  expectedRefOid,
  targetRefOid,
  operationCorrelationId,
  expectedRequestSha256,
}) {}
```

`verificationInputs` contains raw `externalPins` and `verificationTime` only
for real Ed25519, freshness, and semantic replay. A successful replay is
module-privately branded `cryptographicValid:true, semanticValid:true` but
remains `gateEffective:false`; Plan 11 consumes that brand in its independent
Issuer Phase A. `authorityContext` is an opaque, module-branded capability
minted only by the
Plan-11 production composition after external pin, Trusted-Time, live Witness,
branch-control, and Acceptance-Receipt verification. A plain object, raw
`externalPins`, `now`, `verificationTime`, boolean, or caller callback is not an
authority context and can never make the base result gate-effective. Plan 06 creates
`scripts/governance/production-authority-context.mjs` with only
`readProductionAuthorityContext(value)` backed by a module-private `WeakMap`;
there is deliberately no issuer before Plan 11. Plan 11 later modifies that
same file and adds the sole issuer
`verifyProductionAuthorityContext(rawArtifacts)`. Plan 07 may consume claims
only through `readProductionAuthorityContext`. Gate use additionally requires
the exact branded claims `profile:"gate-evaluation"` and
`gateEffective:true`, plus `externalPinsSha256`, `trustedTime.now`,
`transparency.bundleSha256`, and `noncePrefixSha256`; Plan 11 must mint these
exact paths from verified evidence. The separately branded
`profile:"pre-genesis-ceremony"` is always non-gate and is rejected here as
Gate authority. Before Plan 11 every value is unreadable, so the public wrapper
returns the real branded base replay with
`authorityRequired:["production-authority-context"]` and `gateEffective:false`;
it may not mint, clone, deserialize, or structurally recognize a capability
itself. Gate derivation is optional and strictly downstream: Plan 11 must never
need a gate-effective Plan-07 result to mint the context that enables it.

`nonceArtifacts` is the complete ordered, versioned raw Governance artifact
prefix in Plan-06 descriptor form, not a Recovery-only subset. The wrapper
always replays it through `verifyGovernanceNoncePrefix`; the base cannot prove
inventory completeness, must preserve `inventoryBindingVerified:false`, and
stays non-gate. Plan 07 never changes that field; only Plan 11's separately
signed inventory composition may establish completeness. The optional gate pass requires its
`artifactSetSha256` and `noncePrefixSha256` to equal the independently
inventory-bound branded AuthorityContext claims.

The internal core accepts semantic test doubles only from
`recovery-verifier.test.mjs`. Its result is always `testOnly: true` and
`gateEffective: false`. The production wrapper supplies Plan 05's real
Ed25519 verifier and Plan 06's production transparency verifier. A source
allowlist forbids other internal imports.

## Normative state and field invariants

- Lease phases: `issued → claimed → failed` or a TCB terminal entry; at most
  one lease per `authorizationEntrySha256`, one claim, and one successor.
- `gatewaySequence` is one global zero-based, contiguous sequence over the
  complete Gateway prefix. `previousGatewayReceiptSha256` is `null` only at
  sequence 0 and otherwise equals the full canonical signed predecessor,
  including when the predecessor belongs to another operation.
- Gateway phases: `registered → accepted → dispatch-started → settled`, or
  `registered|accepted → cancelled`; post-dispatch cancellation additionally
  requires `post-dispatch-zero-byte` closure.
- Before dispatch: Accepted checkpoint → Tombstone checkpoint → Egress-Intent
  checkpoint → Dispatch-Started checkpoint → fresh witness floors → token
  consumption → first provider byte.
- Tombstones are unique independently by correlation ID, idempotency digest,
  marker ref, and provider-request digest; they never expire or disappear.
- No automatic retransmission exists after `dispatch-started`.
- Unknown provider outcome remains `executing`; only independent final provider
  evidence permits `settled`.
- A closure is valid only after atomic credential/namespace lock, sealed
  write-once counter exactly zero, and destroyed namespace.
- `providerInstallationIdentitySha256` appears once in the App schema despite
  its duplicate textual occurrence in the design field list.

## Complete schema-builder contract

Task 1 creates `scripts/governance/schema-builders/recovery.mjs`; Tasks 2–6
extend the same file with the definitions below. This executable builder is the
single owner of all seven closed schemas. It uses explicit field lists—never
name discovery from a fixture—and then semantic tests exercise every nullable
branch.

```js
import { mkdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

const DRAFT = "https://json-schema.org/draft/2020-12/schema";
const V = { const: "aurelia-governance-v1" };
const REPO = { const: "redshift-three67/aurelia" };
const TEXT = { type: "string", minLength: 1 };
const HEX = { type: "string", pattern: "^[0-9a-f]{64}$" };
const OID = { type: "string", pattern: "^[0-9a-f]{40}$" };
const TIME = { type: "string", pattern: "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\\.[0-9]{3}Z$" };
const NONCE = { type: "string", pattern: "^[A-Za-z0-9_-]{43}$" };
const SIG = { type: "string", pattern: "^[A-Za-z0-9_-]{86}$" };
const UINT = { type: "integer", minimum: 0, maximum: 9007199254740991 };
const POS = { type: "integer", minimum: 1, maximum: 9007199254740991 };
const nullable = (schema) => ({ anyOf: [schema, { type: "null" }] });
const closed = (properties) => ({ type: "object", additionalProperties: false,
  required: Object.keys(properties), properties });
const top = (id, body) => ({ $schema: DRAFT, $id: `https://aurelia.invalid/schemas/${id}`, ...body });
const asProperties = (names, overrides = {}) => Object.fromEntries(names.map((name) => {
  if (overrides[name]) return [name, overrides[name]];
  if (/(?:Sha256|Fingerprint)$/.test(name)) return [name, HEX];
  if (/(?:Commit|TreeOid|RefOid|TargetOid|OidBefore|OidAfter|MarkerOid)$/.test(name)) return [name, OID];
  if (/(?:At|IssuedAt|ExpiresAt|ValidUntil)$/.test(name)) return [name, TIME];
  if (/(?:TreeSize|Sequence|BytesSent)$/.test(name)) return [name, UINT];
  return [name, TEXT];
}));
const nullOnly = (...names) => ({ properties: Object.fromEntries(names.map((name) => [name, { type: "null" }])) });
const requiredValue = (...names) => ({ properties: Object.fromEntries(names.map((name) => [name, { not: { type: "null" } }])) });
const branch = (constants, nonNull = [], nulls = []) => ({ properties: {
  ...Object.fromEntries(Object.entries(constants).map(([name, value]) => [name, { const: value }])),
  ...requiredValue(...nonNull).properties, ...nullOnly(...nulls).properties,
} });
const commonLog = (entryKind) => ({
  schemaVersion: V, entryKind: { const: entryKind }, repositoryId: REPO,
  logId: TEXT, transparencyLogIndex: UINT, previousLogEntrySha256: nullable(HEX),
  loggedAt: TIME, instanceKeyRef: TEXT, instanceKeyEpoch: POS,
  method: { const: "ed25519" }, entryCoreSha256: HEX,
  instanceSignature: nullable(closed({ keyRef: TEXT, signedAt: TIME, nonce: NONCE,
    entryCoreSha256: HEX, signature: SIG })),
});
const logEntry = (id, kind, payload, constraints = []) => top(id,
  { ...closed({ ...commonLog(kind), ...payload }), ...(constraints.length ? { allOf: constraints } : {}) });
const serviceSignature = (coreName) => closed({ keyRef: TEXT, signedAt: TIME,
  nonce: NONCE, [coreName]: HEX, signature: SIG });

const leaseFields = [
  "leaseId", "phase", "operationType", "operationSubjectId",
  "authorizationEntrySha256", "authorizationCheckpointSha256",
  "authorizationCheckpointTreeSize", "previousLeaseEntrySha256", "branch",
  "expectedRefOid", "targetRefOid", "operationCorrelationId",
  "providerIdempotencyKeySha256", "gatewayRegistrationReceiptRef",
  "gatewayRegistrationReceiptSha256", "gatewayRegistrationCheckpointSha256",
  "gatewayRegistrationCheckpointTreeSize", "issuedAt", "expiresAt",
  "failureProofType", "failureProofRef", "failureProofSha256",
  "failureProofCheckpointSha256", "failureProofCheckpointTreeSize",
  "effectiveAfterCheckpoint",
];
const leaseNullable = {
  previousLeaseEntrySha256: nullable(HEX), gatewayRegistrationReceiptRef: nullable(TEXT),
  gatewayRegistrationReceiptSha256: nullable(HEX), gatewayRegistrationCheckpointSha256: nullable(HEX),
  gatewayRegistrationCheckpointTreeSize: nullable(UINT), failureProofType: nullable({ enum: ["gateway-cancelled", "gateway-settled-failure"] }),
  failureProofRef: nullable(TEXT), failureProofSha256: nullable(HEX),
  failureProofCheckpointSha256: nullable(HEX), failureProofCheckpointTreeSize: nullable(UINT),
};
const leasePayload = asProperties(leaseFields, {
  ...leaseNullable, leaseId: { type: "string", pattern: "^RECLEASE-[0-9]{12}$" },
  phase: { enum: ["issued", "claimed", "failed"] },
  operationType: { enum: ["tcb-rollback", "tcb-emergency-recovery"] },
  authorizationCheckpointTreeSize: POS, gatewayRegistrationCheckpointTreeSize: nullable(POS),
  failureProofCheckpointTreeSize: nullable(POS), effectiveAfterCheckpoint: { const: true },
});
const registrationGroup = ["gatewayRegistrationReceiptRef", "gatewayRegistrationReceiptSha256",
  "gatewayRegistrationCheckpointSha256", "gatewayRegistrationCheckpointTreeSize"];
const failureGroup = ["failureProofType", "failureProofRef", "failureProofSha256",
  "failureProofCheckpointSha256", "failureProofCheckpointTreeSize"];
const recoveryOperationLease = logEntry("recovery-operation-lease.schema.json",
  "recovery-operation-lease", leasePayload, [{ oneOf: [
    branch({ phase: "issued" }, [], ["previousLeaseEntrySha256", ...registrationGroup, ...failureGroup]),
    branch({ phase: "claimed" }, ["previousLeaseEntrySha256", ...registrationGroup], failureGroup),
    branch({ phase: "failed" }, ["previousLeaseEntrySha256", ...registrationGroup, ...failureGroup]),
  ] }]);

const gatewayFields = [
  "gatewayReceiptId", "gatewaySequence", "previousGatewayReceiptSha256",
  "previousOperationReceiptSha256", "phase", "gatewayServiceIdentity", "gatewayKeyRef",
  "gatewayImageDigest", "gatewayPolicySha256", "gatewayPermissionsSha256",
  "providerInstallationIdentitySha256", "providerCredentialIdentitySha256",
  "trustedTimeSourceSha256", "authorizationEntrySha256", "authorizationCheckpointSha256",
  "leaseId", "issuedLeaseEntrySha256", "claimedLeaseEntrySha256", "leaseCheckpointSha256",
  "operationCorrelationId", "providerIdempotencyKeySha256", "providerApiOrigin",
  "providerEndpointSha256", "branch", "expectedRefOid", "targetRefOid", "providerMarkerRef",
  "providerMarkerTargetOid", "providerRequestSha256", "recoveryIdempotencyTombstoneRef",
  "recoveryIdempotencyTombstoneSha256", "recoveryIdempotencyTombstoneCheckpointSha256",
  "recoveryIdempotencyTombstoneCheckpointTreeSize", "recoveryEgressIntentRef",
  "recoveryEgressIntentSha256", "recoveryEgressIntentCheckpointSha256",
  "recoveryEgressIntentCheckpointTreeSize", "controlPlaneHandleSha256",
  "networkNamespaceSha256", "networkPolicySha256", "providerByteCounterIdSha256",
  "oneShotEgressTokenSha256", "floorChallengeNonce", "witnessFloorResponsesSha256",
  "registeredAt", "acceptedAt", "dispatchStartedAt", "cancelledAt", "settledAt",
  "recoveryEgressClosureRef", "recoveryEgressClosureSha256", "providerReceiptRef",
  "providerReceiptSha256", "receiptCoreSha256", "signature",
];
const gatewayNullableNames = ["previousGatewayReceiptSha256", "previousOperationReceiptSha256",
  "claimedLeaseEntrySha256", "leaseCheckpointSha256", "recoveryIdempotencyTombstoneRef",
  "recoveryIdempotencyTombstoneSha256", "recoveryIdempotencyTombstoneCheckpointSha256",
  "recoveryIdempotencyTombstoneCheckpointTreeSize", "recoveryEgressIntentRef",
  "recoveryEgressIntentSha256", "recoveryEgressIntentCheckpointSha256",
  "recoveryEgressIntentCheckpointTreeSize", "controlPlaneHandleSha256", "networkNamespaceSha256",
  "networkPolicySha256", "providerByteCounterIdSha256", "oneShotEgressTokenSha256",
  "floorChallengeNonce", "witnessFloorResponsesSha256", "acceptedAt", "dispatchStartedAt",
  "cancelledAt", "settledAt", "recoveryEgressClosureRef", "recoveryEgressClosureSha256",
  "providerReceiptRef", "providerReceiptSha256"];
const gatewayOverrides = Object.fromEntries(gatewayNullableNames.map((name) => [name,
  nullable(/TreeSize$/.test(name) ? POS : /(?:Sha256)$/.test(name) ? HEX : /At$/.test(name) ? TIME : TEXT)]));
Object.assign(gatewayOverrides, {
  gatewayReceiptId: TEXT, gatewaySequence: UINT,
  phase: { enum: ["registered", "accepted", "dispatch-started", "cancelled", "settled"] },
  gatewayImageDigest: { type: "string", pattern: "^sha256:[0-9a-f]{64}$" },
  providerMarkerTargetOid: OID, signature: serviceSignature("receiptCoreSha256"),
});
const claimGroup = ["claimedLeaseEntrySha256", "leaseCheckpointSha256",
  "floorChallengeNonce", "witnessFloorResponsesSha256", "acceptedAt"];
const tombstoneGroup = ["recoveryIdempotencyTombstoneRef",
  "recoveryIdempotencyTombstoneSha256", "recoveryIdempotencyTombstoneCheckpointSha256",
  "recoveryIdempotencyTombstoneCheckpointTreeSize"];
const intentGroup = ["recoveryEgressIntentRef", "recoveryEgressIntentSha256",
  "recoveryEgressIntentCheckpointSha256", "recoveryEgressIntentCheckpointTreeSize",
  "controlPlaneHandleSha256", "networkNamespaceSha256", "networkPolicySha256",
  "providerByteCounterIdSha256", "oneShotEgressTokenSha256"];
const closureGroup = ["recoveryEgressClosureRef", "recoveryEgressClosureSha256"];
const providerGroup = ["providerReceiptRef", "providerReceiptSha256"];
const terminalTimes = ["dispatchStartedAt", "cancelledAt", "settledAt"];
const afterRegistered = ["previousOperationReceiptSha256"];
const gatewayConstraints = [{ oneOf: [
  branch({ phase: "registered" }, [], [...afterRegistered, ...claimGroup, ...tombstoneGroup,
    ...intentGroup, ...terminalTimes, ...closureGroup, ...providerGroup]),
  branch({ phase: "accepted" }, [...afterRegistered, ...claimGroup], [...tombstoneGroup,
    ...intentGroup, ...terminalTimes, ...closureGroup, ...providerGroup]),
  branch({ phase: "dispatch-started" }, [...afterRegistered, ...claimGroup, ...tombstoneGroup,
    ...intentGroup, "dispatchStartedAt"], ["cancelledAt", "settledAt", ...closureGroup, ...providerGroup]),
  branch({ phase: "cancelled" }, [...afterRegistered, "cancelledAt"], [...claimGroup,
    ...tombstoneGroup, ...intentGroup, "dispatchStartedAt", "settledAt", ...closureGroup, ...providerGroup]),
  branch({ phase: "cancelled" }, [...afterRegistered, ...claimGroup, "cancelledAt"], [
    ...tombstoneGroup, ...intentGroup, "dispatchStartedAt", "settledAt", ...closureGroup, ...providerGroup]),
  branch({ phase: "cancelled" }, [...afterRegistered, ...claimGroup, ...tombstoneGroup,
    "cancelledAt"], [...intentGroup, "dispatchStartedAt", "settledAt", ...closureGroup, ...providerGroup]),
  branch({ phase: "cancelled" }, [...afterRegistered, ...claimGroup, ...tombstoneGroup,
    ...intentGroup, "cancelledAt", ...closureGroup], ["dispatchStartedAt", "settledAt", ...providerGroup]),
  branch({ phase: "cancelled" }, [...afterRegistered, ...claimGroup, ...tombstoneGroup,
    ...intentGroup, "dispatchStartedAt", "cancelledAt", ...closureGroup], ["settledAt", ...providerGroup]),
  branch({ phase: "settled" }, [...afterRegistered, ...claimGroup, ...tombstoneGroup,
    ...intentGroup, "dispatchStartedAt", "settledAt", ...providerGroup], ["cancelledAt", ...closureGroup]),
] }];
const recoveryWriteAheadReceipt = logEntry("recovery-write-ahead-receipt.schema.json",
  "recovery-write-ahead-receipt", asProperties(gatewayFields, gatewayOverrides), gatewayConstraints);

const tombstoneFields = ["tombstoneId", "tombstoneNamespace", "leaseId",
  "operationCorrelationId", "providerIdempotencyKeySha256", "authorizationEntrySha256",
  "claimedLeaseEntrySha256", "gatewayAcceptedReceiptRef", "gatewayAcceptedReceiptSha256",
  "gatewayAcceptedCheckpointSha256", "gatewayAcceptedCheckpointTreeSize",
  "gatewayServiceIdentity", "gatewayKeyRef", "gatewayImageDigest", "gatewayPolicySha256",
  "gatewayPermissionsSha256", "trustedTimeSourceSha256",
  "providerInstallationIdentitySha256", "providerCredentialIdentitySha256", "branch",
  "expectedRefOid", "targetRefOid", "providerMarkerRef", "providerMarkerTargetOid",
  "providerRequestSha256", "createdAt", "tombstoneCoreSha256", "gatewaySignature"];
const recoveryIdempotencyTombstone = logEntry("recovery-idempotency-tombstone.schema.json",
  "recovery-idempotency-tombstone", asProperties(tombstoneFields, {
    tombstoneId: { type: "string", pattern: "^RECTOMB-[0-9]{12}$" },
    tombstoneNamespace: { const: "aurelia-recovery-provider-operations" },
    gatewayImageDigest: { type: "string", pattern: "^sha256:[0-9a-f]{64}$" },
    gatewayAcceptedCheckpointTreeSize: POS, gatewaySignature: serviceSignature("tombstoneCoreSha256"),
  }));

const intentFields = ["egressIntentId", "leaseId", "operationCorrelationId",
  "recoveryIdempotencyTombstoneRef", "recoveryIdempotencyTombstoneSha256",
  "recoveryIdempotencyTombstoneCheckpointSha256", "recoveryIdempotencyTombstoneCheckpointTreeSize",
  "gatewayAcceptedReceiptRef", "gatewayAcceptedReceiptSha256", "gatewayAcceptedCheckpointSha256",
  "gatewayAcceptedCheckpointTreeSize", "authorizationEntrySha256", "claimedLeaseEntrySha256",
  "providerIdempotencyKeySha256", "branch", "expectedRefOid", "targetRefOid",
  "providerInstallationIdentitySha256", "providerCredentialIdentitySha256", "providerApiOrigin",
  "providerEndpointSha256", "providerRequestSha256", "providerMarkerRef", "providerMarkerTargetOid",
  "controlPlaneHandleSha256", "networkNamespaceSha256", "networkPolicySha256",
  "providerByteCounterIdSha256", "initialProviderBytesSent", "providerSocketOpened",
  "oneShotEgressTokenSha256", "provisionedAt", "expiresAt", "monitorServiceIdentity",
  "monitorKeyRef", "monitorImageDigest", "monitorPolicySha256", "monitorPermissionsSha256",
  "monitorTrustedTimeSourceSha256", "intentCoreSha256", "monitorSignature"];
const recoveryEgressIntent = logEntry("recovery-egress-intent.schema.json",
  "recovery-egress-intent", asProperties(intentFields, {
    egressIntentId: { type: "string", pattern: "^RECEGRESS-[0-9]{12}$" },
    recoveryIdempotencyTombstoneCheckpointTreeSize: POS,
    gatewayAcceptedCheckpointTreeSize: POS, initialProviderBytesSent: { const: 0 },
    providerSocketOpened: { const: false }, monitorImageDigest: { type: "string", pattern: "^sha256:[0-9a-f]{64}$" },
    monitorSignature: serviceSignature("intentCoreSha256"),
  }));

const closureFields = ["schemaVersion", "repositoryId", "closureId", "closureReason",
  "leaseId", "operationCorrelationId", "recoveryIdempotencyTombstoneRef",
  "recoveryIdempotencyTombstoneSha256", "recoveryEgressIntentRef", "recoveryEgressIntentSha256",
  "recoveryEgressIntentCheckpointSha256", "recoveryEgressIntentCheckpointTreeSize",
  "gatewayDispatchStartedEntrySha256", "gatewayDispatchStartedCheckpointSha256",
  "gatewayDispatchStartedCheckpointTreeSize", "providerApiOrigin", "providerEndpointSha256",
  "providerRequestSha256", "providerInstallationIdentitySha256", "providerCredentialIdentitySha256",
  "providerMarkerRef", "controlPlaneHandleSha256", "networkNamespaceSha256", "networkPolicySha256",
  "providerByteCounterIdSha256", "oneShotEgressTokenSha256", "oneShotEgressTokenConsumed",
  "providerSocketOpened", "initialProviderBytesSent", "finalProviderBytesSent",
  "firstProviderByteAt", "counterSealedAt", "namespaceDestroyedAt", "closedAt",
  "monitorServiceIdentity", "monitorKeyRef", "monitorImageDigest", "monitorPolicySha256",
  "monitorPermissionsSha256", "monitorTrustedTimeSourceSha256", "closureCoreSha256", "monitorSignature"];
const dispatchClosureFields = ["gatewayDispatchStartedEntrySha256",
  "gatewayDispatchStartedCheckpointSha256", "gatewayDispatchStartedCheckpointTreeSize"];
const closureProps = asProperties(closureFields, {
  schemaVersion: V, repositoryId: REPO, closureId: { type: "string", pattern: "^RECCLOSE-[0-9]{12}$" },
  closureReason: { enum: ["pre-dispatch-expiry", "post-dispatch-zero-byte"] },
  recoveryEgressIntentCheckpointTreeSize: POS,
  gatewayDispatchStartedEntrySha256: nullable(HEX), gatewayDispatchStartedCheckpointSha256: nullable(HEX),
  gatewayDispatchStartedCheckpointTreeSize: nullable(POS), oneShotEgressTokenConsumed: { type: "boolean" },
  providerSocketOpened: { const: false }, initialProviderBytesSent: { const: 0 },
  finalProviderBytesSent: { const: 0 }, firstProviderByteAt: { type: "null" },
  monitorImageDigest: { type: "string", pattern: "^sha256:[0-9a-f]{64}$" },
  monitorSignature: serviceSignature("closureCoreSha256"),
});
const recoveryEgressClosure = top("recovery-egress-closure.schema.json", {
  ...closed(closureProps), allOf: [{ oneOf: [
    branch({ closureReason: "pre-dispatch-expiry", oneShotEgressTokenConsumed: false }, [], dispatchClosureFields),
    branch({ closureReason: "post-dispatch-zero-byte", oneShotEgressTokenConsumed: true }, dispatchClosureFields),
  ] }],
});

const witnessFloorResponse = closed({
  witnessId: TEXT, keyRef: TEXT,
  floorId: { type: "string", pattern: "^WFLOOR-[0-9]{12}$" }, floorSha256: HEX,
  minimumTreeSize: POS, minimumCheckpointSha256: HEX,
  floorChallengeNonce: NONCE, respondedAt: TIME, responseSignature: SIG,
});
const appFields = [
  "schemaVersion", "repositoryId", "attestationId", "operationType", "appIdentity",
  "appKeyRef", "appImageDigest", "appPolicySha256", "appPermissionsSha256",
  "providerInstallationIdentitySha256", "authorizationEntrySha256",
  "authorizationCheckpointSha256", "authorizationCheckpointTreeSize",
  "authorizationCheckpointIssuedAt", "authorizationExpiresAt", "recoveryOperationLeaseId",
  "recoveryOperationLeaseSha256", "leaseCheckpointSha256", "leaseCheckpointTreeSize",
  "leaseCheckpointIssuedAt", "leaseExpiresAt", "floorChallengeNonce", "witnessFloorResponses",
  "branch", "expectedRefOid", "targetRefOid", "operationCorrelationId",
  "providerIdempotencyKeySha256", "providerCredentialIdentitySha256", "providerApiOrigin",
  "providerEndpointSha256", "providerMarkerRef", "providerMarkerTargetOid",
  "gatewayAcceptedReceiptRef", "gatewayAcceptedReceiptSha256", "gatewayAcceptedCheckpointSha256",
  "gatewayAcceptedCheckpointTreeSize", "recoveryIdempotencyTombstoneRef",
  "recoveryIdempotencyTombstoneSha256", "recoveryIdempotencyTombstoneCheckpointSha256",
  "recoveryIdempotencyTombstoneCheckpointTreeSize", "recoveryEgressIntentRef",
  "recoveryEgressIntentSha256", "recoveryEgressIntentCheckpointSha256",
  "recoveryEgressIntentCheckpointTreeSize", "controlPlaneHandleSha256",
  "networkNamespaceSha256", "networkPolicySha256", "providerByteCounterIdSha256",
  "oneShotEgressTokenSha256", "gatewayDispatchStartedReceiptRef",
  "gatewayDispatchStartedReceiptSha256", "gatewayDispatchStartedCheckpointSha256",
  "gatewayDispatchStartedCheckpointTreeSize", "gatewaySettledReceiptRef",
  "gatewaySettledReceiptSha256", "gatewaySettledCheckpointSha256",
  "gatewaySettledCheckpointTreeSize", "observedRefOidBefore", "observedRefOidAfter",
  "observedProviderMarkerOid", "providerReceiptRef", "providerReceiptSha256",
  "operationStartedAt", "operationCompletedAt", "result", "attestedAt", "nonce",
  "attestationCoreSha256", "signature",
];
const recoveryAppAttestation = top("recovery-app-attestation.schema.json", closed(
  asProperties(appFields, {
    schemaVersion: V, repositoryId: REPO,
    attestationId: { type: "string", pattern: "^RECAPP-[0-9]{12}$" },
    operationType: { enum: ["tcb-rollback", "tcb-emergency-recovery"] },
    appImageDigest: { type: "string", pattern: "^sha256:[0-9a-f]{64}$" },
    authorizationCheckpointTreeSize: POS, leaseCheckpointTreeSize: POS,
    gatewayAcceptedCheckpointTreeSize: POS,
    recoveryIdempotencyTombstoneCheckpointTreeSize: POS,
    recoveryEgressIntentCheckpointTreeSize: POS,
    gatewayDispatchStartedCheckpointTreeSize: POS, gatewaySettledCheckpointTreeSize: POS,
    observedRefOidBefore: OID, observedRefOidAfter: OID,
    observedProviderMarkerOid: nullable(OID), result: { enum: ["succeeded", "failed"] },
    nonce: NONCE, signature: SIG, witnessFloorResponses: { type: "array", minItems: 2, items: witnessFloorResponse },
  }),
));

const providerFields = [
  "schemaVersion", "repositoryId", "providerReceiptId", "providerName", "providerApiOrigin",
  "providerEndpointSha256", "providerInstallationIdentitySha256",
  "providerCredentialIdentitySha256", "providerIdempotencyKeySha256",
  "operationCorrelationId", "authorizationEntrySha256", "authorizationCheckpointSha256",
  "leaseId", "claimedLeaseEntrySha256", "leaseCheckpointSha256",
  "gatewayAcceptedReceiptRef", "gatewayAcceptedReceiptSha256",
  "recoveryIdempotencyTombstoneRef", "recoveryIdempotencyTombstoneSha256",
  "recoveryIdempotencyTombstoneCheckpointSha256", "recoveryIdempotencyTombstoneCheckpointTreeSize",
  "recoveryEgressIntentRef", "recoveryEgressIntentSha256",
  "recoveryEgressIntentCheckpointSha256", "recoveryEgressIntentCheckpointTreeSize",
  "controlPlaneHandleSha256", "networkNamespaceSha256", "networkPolicySha256",
  "providerByteCounterIdSha256", "oneShotEgressTokenSha256", "oneShotEgressTokenConsumedAt",
  "finalProviderBytesSent", "gatewayDispatchStartedReceiptRef",
  "gatewayDispatchStartedReceiptSha256", "gatewayDispatchStartedCheckpointSha256",
  "gatewayDispatchStartedCheckpointTreeSize", "dispatchFloorChallengeNonce",
  "dispatchWitnessFloorResponses", "providerMarkerRef", "providerMarkerTargetOid",
  "providerPrimitive", "providerRequestId", "providerRequestRef", "providerRequestSha256",
  "providerResponseRef", "providerResponseSha256", "tlsTranscriptRef", "tlsTranscriptSha256",
  "providerCertificateChainSha256", "operationType", "branch", "expectedRefOid", "targetRefOid",
  "observedRefOidBefore", "observedRefOidAfter", "observedProviderMarkerOid", "result",
  "providerRequestStartedAt", "providerAcceptedAt", "providerCompletedAt", "providerObservedAt",
  "verificationStartedAt", "verificationCompletedAt", "verifierServiceIdentity", "verifierKeyRef",
  "verifierImageDigest", "verifierPolicySha256", "trustedTimeSourceSha256", "nonce",
  "receiptCoreSha256", "signature",
];
const providerRefUpdateReceipt = top("provider-ref-update-receipt.schema.json", closed(
  asProperties(providerFields, {
    schemaVersion: V, repositoryId: REPO,
    providerReceiptId: { type: "string", pattern: "^PROVREC-[0-9]{12}$" },
    providerName: { const: "github" }, providerPrimitive: { const: "github-graphql-updateRefs-beforeOid" },
    operationType: { const: "compare-and-swap-ref" }, result: { enum: ["succeeded", "failed"] },
    recoveryIdempotencyTombstoneCheckpointTreeSize: POS,
    recoveryEgressIntentCheckpointTreeSize: POS, gatewayDispatchStartedCheckpointTreeSize: POS,
    finalProviderBytesSent: POS, observedRefOidBefore: OID, observedRefOidAfter: OID,
    observedProviderMarkerOid: nullable(OID), providerMarkerTargetOid: OID,
    dispatchFloorChallengeNonce: NONCE,
    dispatchWitnessFloorResponses: { type: "array", minItems: 2, items: witnessFloorResponse },
    verifierImageDigest: { type: "string", pattern: "^sha256:[0-9a-f]{64}$" },
    nonce: NONCE, signature: SIG,
  }),
));

export const recoverySchemas = {
  "recovery-operation-lease.schema.json": recoveryOperationLease,
  "recovery-write-ahead-receipt.schema.json": recoveryWriteAheadReceipt,
  "recovery-idempotency-tombstone.schema.json": recoveryIdempotencyTombstone,
  "recovery-egress-intent.schema.json": recoveryEgressIntent,
  "recovery-egress-closure.schema.json": recoveryEgressClosure,
  "recovery-app-attestation.schema.json": recoveryAppAttestation,
  "provider-ref-update-receipt.schema.json": providerRefUpdateReceipt,
};
export async function writeRecoverySchemas(target = "docs/governance/schemas") {
  await mkdir(target, { recursive: true });
  for (const [name, schema] of Object.entries(recoverySchemas)) {
    await writeFile(resolve(target, name), `${JSON.stringify(schema, null, 2)}\n`, "utf8");
  }
}
```

The gateway `oneOf` is the permitted matrix: `registered`, `accepted`,
`dispatch-started`, each reachable pre-/post-dispatch `cancelled` form, and
`settled`. No fixture may infer or modify it. The builder test serializes every
branch, asserts it passes, and flips each member of each group independently to
prove partial groups fail.

### Task 1: Define and validate the recovery lease chain

**Files:**

- Create: `docs/governance/schemas/recovery-operation-lease.schema.json`
- Create: `scripts/governance/schema-builders/recovery.mjs`
- Create: `scripts/governance/recovery-verifier.test.mjs`
- Create: `scripts/governance/recovery-verifier-internal.mjs`
- Create: `scripts/governance/recovery-verifier.mjs`

- [ ] **Step 1: Write issued/claimed/failed RED schema tests**

Create one inline fixture for each phase. Assert exact common operation fields,
phase-dependent predecessor, registration and failure-proof fields, fixed
operation types, full hashes, UTC times, and `effectiveAfterCheckpoint: true`.
Mutate every nullable group one field at a time so partial groups fail.

- [ ] **Step 2: Add semantic uniqueness RED tests**

Reject second issue under the same authorization even with a different
subject ID, global correlation reuse across epochs, duplicate claim,
sibling failed/terminal successors, mismatched subject derivation, expiry over
15 minutes, and a checkpoint outside authorization/rollback expiry.

- [ ] **Step 3: Run and confirm RED**

```powershell
node --test --test-name-pattern="recovery lease" scripts/governance/recovery-verifier.test.mjs
```

Expected: FAIL because schema and replay exports do not exist.

- [ ] **Step 4: Generate and exhaustively test the closed lease schema**

Use exactly the payload fields in §6.3. Express issued, claimed, and failed as
three disjoint `oneOf` branches. `issued` has null predecessor, registration,
and failure fields; `claimed` binds issued plus all four registration fields;
`failed` binds claim plus exactly one complete cancellation or failed-settlement
proof group.

- [ ] **Step 5: Implement lease replay**

Index the full prefix by lease, authorization, subject, and raw correlation
ID. Enforce one linear successor and these exact time relations:

```text
authorizationCheckpoint.issuedAt < issuedAt
issuedAt <= issuedEntry.loggedAt <= issuedCheckpoint.issuedAt
issuedCheckpoint.issuedAt <= claimedEntry.loggedAt
claimedEntry.loggedAt <= claimedCheckpoint.issuedAt < expiresAt
expiresAt <= authorizationExpiresAt|rollbackValidUntil
```

- [ ] **Step 6: Run and confirm GREEN**

Expected: all three valid phase fixtures pass; every uniqueness, nullability,
subject, predecessor, and timing mutation fails.

- [ ] **Step 7: Commit the lease unit**

```powershell
git add docs/governance/schemas/recovery-operation-lease.schema.json scripts/governance/schema-builders/recovery.mjs scripts/governance/recovery-verifier-internal.mjs scripts/governance/recovery-verifier.mjs scripts/governance/recovery-verifier.test.mjs
git commit -m "feat: validate recovery operation leases"
```

### Task 2: Define the write-ahead gateway journal

**Files:**

- Create: `docs/governance/schemas/recovery-write-ahead-receipt.schema.json`
- Modify: `scripts/governance/schema-builders/recovery.mjs`
- Modify: `scripts/governance/recovery-verifier-internal.mjs`
- Modify: `scripts/governance/recovery-verifier.test.mjs`

- [ ] **Step 1: Write one RED test per gateway phase**

Use exact phase branches for `registered`, `accepted`, `dispatch-started`,
`cancelled`, and `settled`. Verify the global sequence, full previous-gateway
hash, per-operation previous hash, all service/image/policy/permission/time
pins, request/marker fields, timestamps, and phase-specific nullable groups.
Every phase fixture carries a real RFC-8032 test-vector signature in the
Gateway signature slot. Mutate `gatewayServiceIdentity`, `gatewayKeyRef`, the
nested signature `keyRef`, `receiptCoreSha256`, and one signature bit
independently and require rejection by the public non-injectable production
wrapper; a valid Transparency instance signature never substitutes for the
Gateway service signature.

- [ ] **Step 2: Add fork and crash mutations**

Reject sequence gaps, wrong previous full hash, two accepted siblings,
accept/cancel race, dispatch without checkpointed Tombstone and Intent,
settlement without provider receipt, cancel after dispatch without closure,
and two internally signed gateway heads under different transparency forks.
Interleave two Lease IDs and prove that global `gatewaySequence` and
`previousGatewayReceiptSha256` still form one zero-based contiguous chain,
while `previousOperationReceiptSha256` independently follows only that Lease.
Reject duplicate receipt IDs/sequences, a first phase other than `registered`,
duplicate/skipped phases, a phase after `settled|cancelled`, and every sequence
outside the closed prefixes of the normative success/cancel branches.

- [ ] **Step 3: Run and confirm RED**

Expected: missing schema and gateway replay fail.

- [ ] **Step 4: Generate and exhaustively test the closed gateway schema**

Define the complete field set once in `$defs`, then five phase `oneOf`
branches with exact const/null requirements from §6.3. Gateway `receiptCoreSha256`
excludes itself, gateway signature, and every common transparency field.
The surrounding log `entryCoreSha256` includes the entire specific payload,
gateway signature, and common log context.

- [ ] **Step 5: Implement gateway replay and dual-core validation**

Recompute `receiptCoreSha256` from payload-only fields and
`entryCoreSha256` from the full log entry. Require each phase's own full-quorum
checkpoint before it is effective. Derive a single reachable operation state;
never choose a branch by latest timestamp. Verify `signature.keyRef` byte-equal
to `gatewayKeyRef` and to the externally authenticated
`recoveryWriteAheadGateway.keyRef`, verify all repeated Gateway identity/image/
policy/permission/time-source pins, and verify Ed25519 over the exact payload
core. Apply global sequence/predecessor validation before per-operation replay.

- [ ] **Step 6: Run and confirm GREEN**

Expected: phase fixtures pass; sequence, fork, checkpoint, core-projection,
nullability, and crash mutations fail.

- [ ] **Step 7: Commit the gateway journal**

```powershell
git add docs/governance/schemas/recovery-write-ahead-receipt.schema.json scripts/governance/schema-builders/recovery.mjs scripts/governance/recovery-verifier-internal.mjs scripts/governance/recovery-verifier.test.mjs
git commit -m "feat: validate recovery gateway journal"
```

### Task 3: Enforce immutable Tombstone and sealed Egress Intent

**Files:**

- Create: `docs/governance/schemas/recovery-idempotency-tombstone.schema.json`
- Create: `docs/governance/schemas/recovery-egress-intent.schema.json`
- Modify: `scripts/governance/schema-builders/recovery.mjs`
- Modify: `scripts/governance/recovery-verifier-internal.mjs`
- Modify: `scripts/governance/recovery-verifier.test.mjs`

- [ ] **Step 1: Write Tombstone RED tests**

Assert the exact accepted-receipt/checkpoint, authorization, claim,
installation/credential, branch/OID, marker, provider-request, creation time,
payload core, and Gateway signature fields. Reject a second Tombstone for each
of the four uniqueness keys independently and any creation before Accepted
checkpoint.

- [ ] **Step 2: Write Egress-Intent RED tests**

Assert Tombstone/Accepted checkpoint binding, exact provider/branch/request
identity, Handle/Namespace/Policy/Counter/Token hashes, initial bytes 0,
socket false, monitor pins, provisioning/expiry, core, and signature. Reject a
second Intent per Tombstone, Handle, Namespace, Counter, or Token.

For both tests, mutate the nested signature `keyRef`, repeated service identity,
each pinned image/policy/permission/time-source field, core digest, and one
signature bit. A Tombstone is valid only under the exact externally
authenticated `recoveryWriteAheadGateway` pin; an Intent is valid only under
the exact externally authenticated `egressEnforcementMonitor` pin.

- [ ] **Step 3: Add direct-egress and stale-intent mutations**

Reject a different Credential/Namespace/Policy/Token between artifacts,
Intent after lease expiry, pre-opened socket, nonzero counter, missing
full-quorum checkpoint, and any declared DNS/proxy/IPv4/IPv6/Unix/foreign-
namespace bypass.

- [ ] **Step 4: Run and confirm RED**

Expected: both schemas and uniqueness replay are missing.

- [ ] **Step 5: Generate both schemas and implement monotone indexes**

Use exact field sets from §6.3 and `additionalProperties: false` everywhere.
Maintain independent never-delete maps for correlation, idempotency hash,
marker, request, Tombstone, Handle, Namespace, Counter, and Token. A collision
returns a hard error and sets all recovery gates red in derived state.
Recompute the payload-only `tombstoneCoreSha256`/`intentCoreSha256`, require the
same digest inside the corresponding signature record, require signature
`keyRef` and all repeated service-pin fields byte-equal to the AuthorityContext
claims, and verify Ed25519 before inserting either artifact into an index.

- [ ] **Step 6: Run and confirm GREEN**

Expected: the linear Tombstone→Intent path passes; every collision, stale,
bypass, socket, counter, checkpoint, or identity mutation fails.

- [ ] **Step 7: Commit idempotency and egress intent**

```powershell
git add docs/governance/schemas/recovery-idempotency-tombstone.schema.json docs/governance/schemas/recovery-egress-intent.schema.json scripts/governance/schema-builders/recovery.mjs scripts/governance/recovery-verifier-internal.mjs scripts/governance/recovery-verifier.test.mjs
git commit -m "feat: enforce recovery idempotency and egress intent"
```

### Task 4: Prove zero provider bytes before cancellation

**Files:**

- Create: `docs/governance/schemas/recovery-egress-closure.schema.json`
- Create: `scripts/fixtures/governance/recovery/valid-pre-dispatch-cancel.json`
- Create: `scripts/fixtures/governance/recovery/valid-post-dispatch-zero-byte.json`
- Modify: `scripts/governance/schema-builders/recovery.mjs`
- Modify: `scripts/governance/recovery-verifier-internal.mjs`
- Modify: `scripts/governance/recovery-verifier.test.mjs`

- [ ] **Step 1: Write both closure-branch RED tests**

`pre-dispatch-expiry` requires all dispatch fields null and token not consumed.
`post-dispatch-zero-byte` requires dispatch entry/hash/checkpoint non-null and
token consumed. Both require socket false, initial/final byte counters zero,
first-byte time null, sealed counter, destroyed namespace, closed time, and
the exact Monitor pins.

- [ ] **Step 2: Add closure identity mutations**

Change Handle, Namespace, Policy, Counter, Token, Credential, Endpoint,
Request, Marker, or Tombstone one at a time. Also test an open socket, unknown
counter, one byte, missing namespace destruction, gateway self-signature, and
closure created only from later process inspection.

- [ ] **Step 3: Run and confirm RED**

Expected: missing schema and closure semantics fail.

- [ ] **Step 4: Generate the schema and implement closure validation**

Use two disjoint schema branches and compare all shared identities byte-for-
byte with Intent and Dispatch-Started. Require counter seal before namespace
destruction and destruction no later than closure signature time. Verify only
the externally pinned Monitor signature; Gateway statements cannot substitute.

- [ ] **Step 5: Run and confirm GREEN**

Expected: both closure forms pass and every identity/counter/socket/order mutation fails.

- [ ] **Step 6: Commit zero-byte closure**

```powershell
git add docs/governance/schemas/recovery-egress-closure.schema.json scripts/fixtures/governance/recovery/valid-pre-dispatch-cancel.json scripts/fixtures/governance/recovery/valid-post-dispatch-zero-byte.json scripts/governance/schema-builders/recovery.mjs scripts/governance/recovery-verifier-internal.mjs scripts/governance/recovery-verifier.test.mjs
git commit -m "feat: verify recovery zero-byte closure"
```

### Task 5: Validate the exact GitHub CAS and immutable marker request

**Files:**

- Create: `scripts/governance/recovery-provider-request.mjs`
- Create: `scripts/governance/recovery-provider-request.test.mjs`

- [ ] **Step 1: Add a literal valid GraphQL request fixture in the test**

The parsed `UpdateRefsInput` must contain exactly two ordered updates:

```js
[
  {
    name: `refs/heads/${branch}`,
    beforeOid: expectedRefOid,
    afterOid: targetRefOid,
    force: true,
  },
  {
    name: `refs/heads/aurelia-recovery-markers/${sha256Hex(Buffer.from(operationCorrelationId, "utf8"))}`,
    beforeOid: "0000000000000000000000000000000000000000",
    afterOid: targetRefOid,
    force: false,
  },
]
```

`clientMutationId` is exactly the raw correlation ID and is described only as
correlation, never idempotency. `repositoryNodeId` is the externally pinned
GitHub node ID for `redshift-three67/aurelia` and is included in
`UpdateRefsInput`; aliases or caller-selected repositories are rejected.

- [ ] **Step 2: Add request mutation tests**

Reject swapped updates, a third update, branch `force:false`, marker
`force:true`, marker update without zero `beforeOid`, different marker digest,
different target, missing `beforeOid`, wildcard ref, delete, variable not used
by the operation, and request bytes whose recorded digest differs.

- [ ] **Step 3: Run and confirm RED**

Run `node --test scripts/governance/recovery-provider-request.test.mjs`.
Expected: missing pure request validator fails; there must be no network output.

- [ ] **Step 4: Implement closed parsing and validation**

Accept UTF-8 request bytes, parse with Plan 05's duplicate-key rejecting JSON
parser, validate the fixed GraphQL operation/document digest and exact variables,
and recompute the full request SHA-256. Do not accept semantically equivalent
but byte-different requests because the Gateway artifacts bind exact bytes.

Use this complete implementation; the operation text and its independently
fixed digest are constants, not produced from caller input:

```js
import { createHash } from "node:crypto";
import { parseUniqueJson } from "./raw-json.mjs";

const OPERATION = "mutation AureliaRecoveryUpdateRefs($input: UpdateRefsInput!) {\n  updateRefs(input: $input) {\n    clientMutationId\n  }\n}";
const OPERATION_SHA256 = "d384baf8574b811ec5e898f5afe32e90e72e145da5d40b9dc202170cac2e3084";
const sha256Hex = (bytes) => createHash("sha256").update(bytes).digest("hex");
const markerFor = (correlation) => `refs/heads/aurelia-recovery-markers/${sha256Hex(Buffer.from(correlation, "utf8"))}`;
const validBranch = (name) => typeof name === "string" && name.length > 0
  && !name.startsWith(".") && !name.endsWith(".") && !name.endsWith("/")
  && !name.endsWith(".lock") && !name.includes("..") && !name.includes("//")
  && !name.includes("@{") && !/[\u0000-\u0020~^:?*\[\\]/u.test(name);

export function validateGitHubUpdateRefsRequest({ requestBytes, branch,
  pinnedBranch, repositoryNodeId, expectedRefOid, targetRefOid,
  operationCorrelationId, expectedRequestSha256 }) {
  const errors = [];
  const fail = (rule, path, message) => errors.push({ rule, path, message });
  let request;
  const bytes = Buffer.from(requestBytes);
  try { request = parseUniqueJson(bytes); }
  catch (error) { fail("PROVIDER_REQUEST_JSON", "$", error.message); return { ok: false, errors }; }
  if (sha256Hex(Buffer.from(OPERATION, "utf8")) !== OPERATION_SHA256) fail("PROVIDER_OPERATION_PIN", "$.query", "pinned operation digest is corrupt");
  if (branch !== pinnedBranch || !validBranch(branch)) fail("PROVIDER_BRANCH_PIN", "$.variables.input.refUpdates[0].name", "branch must equal the verified pin and satisfy git-check-ref-format");
  if (!/^[A-Za-z0-9_-]+$/.test(repositoryNodeId)
    || !/^[0-9a-f]{40}$/.test(expectedRefOid) || !/^[0-9a-f]{40}$/.test(targetRefOid)
    || typeof operationCorrelationId !== "string" || operationCorrelationId.length === 0) {
    fail("PROVIDER_REQUEST_INPUT", "$", "invalid pinned request input");
  }
  const expected = {
    query: OPERATION,
    variables: { input: {
      repositoryId: repositoryNodeId,
      refUpdates: [
        { name: `refs/heads/${branch}`, beforeOid: expectedRefOid,
          afterOid: targetRefOid, force: true },
        { name: markerFor(operationCorrelationId),
          beforeOid: "0000000000000000000000000000000000000000",
          afterOid: targetRefOid, force: false },
      ],
      clientMutationId: operationCorrelationId,
    } },
  };
  const expectedBytes = Buffer.from(JSON.stringify(expected), "utf8");
  if (!bytes.equals(expectedBytes)) fail("PROVIDER_REQUEST_BYTES", "$", "wire bytes must equal the one canonical JSON serialization");
  const requestSha256 = sha256Hex(bytes);
  if (requestSha256 !== expectedRequestSha256) fail("PROVIDER_REQUEST_DIGEST", "$", "wire bytes differ from pre-checkpointed request digest");
  return { ok: errors.length === 0, errors, providerRequestSha256: requestSha256,
    operationSha256: OPERATION_SHA256, repositoryNodeId, branch, expectedRefOid,
    targetRefOid, clientMutationId: operationCorrelationId,
    markerRef: markerFor(operationCorrelationId), parsed: request };
}
```

The test supplies a literal `expectedRequestSha256`; semantically identical
bytes with whitespace or property-order drift fail. It also runs
`git check-ref-format --branch` over the accepted/rejected corpus to keep the
pure predicate byte-equivalent to Git's grammar, and verifies the authenticated
provider response proves both updates occurred in the one mutation call with
the returned branch/marker OIDs.

- [ ] **Step 5: Run and confirm GREEN**

Expected: exact request passes; all shape, ref, force, OID, marker, correlation,
duplicate-key, and byte-digest mutations fail. Assert no socket API is imported.

- [ ] **Step 6: Commit the provider request contract**

```powershell
git add scripts/governance/recovery-provider-request.mjs scripts/governance/recovery-provider-request.test.mjs
git commit -m "feat: validate GitHub recovery CAS request"
```

### Task 6: Validate independent provider receipt and App attestation

**Files:**

- Create: `docs/governance/schemas/provider-ref-update-receipt.schema.json`
- Create: `docs/governance/schemas/recovery-app-attestation.schema.json`
- Create: `scripts/fixtures/governance/recovery/valid-success.json`
- Modify: `scripts/governance/schema-builders/recovery.mjs`
- Modify: `scripts/governance/recovery-verifier-internal.mjs`
- Modify: `scripts/governance/recovery-verifier.test.mjs`

- [ ] **Step 1: Write provider-receipt RED tests**

Assert all exact §6.3 fields: provider/endpoint/install/credential, operation,
authorization/lease/gateway/Tombstone/Intent/Dispatch checkpoints, Egress
identities, token-consumption/counter, marker, exact request and authenticated
response/TLS references, before/after OIDs, provider times, independent
Verifier pins, dispatch challenge floors, core, and signature.

- [ ] **Step 2: Add success/failure/unknown mutations**

Success requires before=expected, after=target, marker=target, and bytes >0.
Failure requires after=before, marker null, authenticated final rejection, and
bytes >0. Timeout, disconnect, lost response, zero bytes, wrong Request ID,
Verifier holding write credential, or successful CAS labelled failed remains
`executing` and cannot create a terminal receipt.

- [ ] **Step 3: Write App-attestation RED tests**

Require exactly one installation identity field, no App provider credential,
all checkpoint/floor/request/Egress/Provider identities, observed OIDs/marker,
operation times/result, nonce/core/signature, and pinned App image/policy/
permissions. Reject App success without the independent provider receipt.

- [ ] **Step 4: Run and confirm RED**

Expected: both schemas and semantic correlation are missing.

- [ ] **Step 5: Generate both schemas and implement cross-artifact verification**

Use exact closed fields from §6.3. Recompute raw request/response/TLS hashes,
challenge responses, and all full-artifact hashes. Enforce the complete fixed
ordering and every five-second skew window exactly; do not make skew
configurable. Provider Receipt, Settled Gateway Receipt, and App Attestation
must be byte-identical on all shared IDs, hashes, pins, OIDs, marker, and times.

Replace ad-hoc shared-field loops with the following single closed edge
contract in `recovery-verifier-internal.mjs`. For every Lease,
`artifacts.evidenceByLeaseId[leaseId]` must expose the exact raw
`providerRequestBytes`, `providerResponseBytes`, `tlsTranscriptBytes`, and
Monitor-signed `providerCounterEvidenceBytes`
consumed by the Provider Receipt; no digest-only substitute is accepted and a
single shared byte tuple cannot stand in for multiple operations. The internal
context builder alone derives `providerRequestContract`, the provider-
authenticated `providerResponseContract`, the transcript-verified
`tlsTranscriptContract`, the pinned-Monitor-verified `egressCounterContract`,
and the revision-fixed, content-addressed
`evidenceBindings` from those bytes. Callers cannot submit any of these
derived aliases or an `...Verified:true` boolean.
`checkpoint:<artifact>` resolves only through the already cryptographically
verified Transparency replay to the unique full-quorum checkpoint that covers
the canonical full hash of that artifact. `full-hash` is exactly
`fullArtifactSha256(value) = SHA256(RFC8785(value))`, never a payload-core hash.
`rfc8785-sha256` hashes the exact named value rather than the surrounding
artifact. All flat `...CheckpointSha256/...CheckpointTreeSize` schema pairs
resolve through one virtual `...Checkpoint` target; no partial pair is an
endpoint.
Every expanded edge has exactly
`id/kind/source/target/appliesTo/maxSkewMs`; no caller may add, remove, replace,
or override an edge:

```js
const edgeGroup = (group, kind, source, targets, {
  appliesTo = "when-present", maxSkewMs = null,
} = {}) => Object.freeze(targets.map((target, index) => Object.freeze({
  id: `${group}-${String(index + 1).padStart(2, "0")}`,
  kind, source, target, appliesTo, maxSkewMs,
})));

export const RECOVERY_CROSS_ARTIFACT_EDGES = Object.freeze([
  // Stable IDs and direct references.
  ...edgeGroup("ID-REPOSITORY", "equal", "repositoryAnchor.repositoryId", [
    "issuedLease.repositoryId", "claimedLease.repositoryId", "failedLease.repositoryId",
    "gatewayRegistered.repositoryId", "gatewayAccepted.repositoryId",
    "gatewayDispatchStarted.repositoryId", "gatewaySettled.repositoryId",
    "gatewayCancelled.repositoryId", "tombstone.repositoryId", "intent.repositoryId",
    "closure.repositoryId", "providerReceipt.repositoryId", "appAttestation.repositoryId",
  ]),
  ...edgeGroup("ID-LEASE", "equal", "issuedLease.leaseId", [
    "claimedLease.leaseId", "failedLease.leaseId", "gatewayRegistered.leaseId", "gatewayAccepted.leaseId",
    "tombstone.leaseId", "intent.leaseId", "gatewayDispatchStarted.leaseId",
    "closure.leaseId", "providerReceipt.leaseId", "gatewaySettled.leaseId", "gatewayCancelled.leaseId",
    "appAttestation.recoveryOperationLeaseId",
  ]),
  ...edgeGroup("ID-REGISTERED", "equal", "gatewayRegistered.gatewayReceiptId", [
    "claimedLease.gatewayRegistrationReceiptRef",
  ]),
  ...edgeGroup("ID-ACCEPTED", "equal", "gatewayAccepted.gatewayReceiptId", [
    "tombstone.gatewayAcceptedReceiptRef", "intent.gatewayAcceptedReceiptRef",
    "providerReceipt.gatewayAcceptedReceiptRef", "appAttestation.gatewayAcceptedReceiptRef",
  ]),
  ...edgeGroup("ID-TOMBSTONE", "equal", "tombstone.tombstoneId", [
    "intent.recoveryIdempotencyTombstoneRef", "gatewayDispatchStarted.recoveryIdempotencyTombstoneRef",
    "closure.recoveryIdempotencyTombstoneRef", "providerReceipt.recoveryIdempotencyTombstoneRef",
    "gatewaySettled.recoveryIdempotencyTombstoneRef", "gatewayCancelled.recoveryIdempotencyTombstoneRef",
    "appAttestation.recoveryIdempotencyTombstoneRef",
  ]),
  ...edgeGroup("ID-INTENT", "equal", "intent.egressIntentId", [
    "gatewayDispatchStarted.recoveryEgressIntentRef", "closure.recoveryEgressIntentRef",
    "providerReceipt.recoveryEgressIntentRef", "gatewaySettled.recoveryEgressIntentRef",
    "gatewayCancelled.recoveryEgressIntentRef", "appAttestation.recoveryEgressIntentRef",
  ]),
  ...edgeGroup("ID-DISPATCH", "equal", "gatewayDispatchStarted.gatewayReceiptId", [
    "providerReceipt.gatewayDispatchStartedReceiptRef", "appAttestation.gatewayDispatchStartedReceiptRef",
  ]),
  ...edgeGroup("ID-PROVIDER", "equal", "providerReceipt.providerReceiptId", [
    "gatewaySettled.providerReceiptRef", "appAttestation.providerReceiptRef",
  ], { appliesTo: "terminal-provider" }),
  ...edgeGroup("ID-SETTLED", "equal", "gatewaySettled.gatewayReceiptId", [
    "appAttestation.gatewaySettledReceiptRef",
  ], { appliesTo: "terminal-provider" }),
  ...edgeGroup("ID-CLOSURE", "equal", "closure.closureId", [
    "gatewayCancelled.recoveryEgressClosureRef",
  ], { appliesTo: "zero-byte-cancel" }),

  // Canonical full-artifact hashes and predecessor edges.
  ...edgeGroup("HASH-AUTHORIZATION", "full-hash", "authorizationEntry", [
    "issuedLease.authorizationEntrySha256",
  ]),
  ...edgeGroup("HASH-ISSUED-LEASE", "full-hash", "issuedLease", [
    "gatewayRegistered.issuedLeaseEntrySha256", "gatewayAccepted.issuedLeaseEntrySha256",
    "gatewayDispatchStarted.issuedLeaseEntrySha256", "gatewaySettled.issuedLeaseEntrySha256",
    "gatewayCancelled.issuedLeaseEntrySha256",
  ]),
  ...edgeGroup("HASH-CLAIMED-LEASE", "full-hash", "claimedLease", [
    "gatewayAccepted.claimedLeaseEntrySha256", "tombstone.claimedLeaseEntrySha256",
    "intent.claimedLeaseEntrySha256", "gatewayDispatchStarted.claimedLeaseEntrySha256",
    "providerReceipt.claimedLeaseEntrySha256", "gatewaySettled.claimedLeaseEntrySha256",
    "gatewayCancelled.claimedLeaseEntrySha256", "appAttestation.recoveryOperationLeaseSha256",
  ]),
  ...edgeGroup("HASH-REGISTERED", "full-hash", "gatewayRegistered", [
    "claimedLease.gatewayRegistrationReceiptSha256",
  ]),
  ...edgeGroup("HASH-ACCEPTED", "full-hash", "gatewayAccepted", [
    "gatewayDispatchStarted.previousOperationReceiptSha256", "tombstone.gatewayAcceptedReceiptSha256",
    "intent.gatewayAcceptedReceiptSha256", "providerReceipt.gatewayAcceptedReceiptSha256",
    "appAttestation.gatewayAcceptedReceiptSha256",
  ]),
  ...edgeGroup("HASH-TOMBSTONE", "full-hash", "tombstone", [
    "intent.recoveryIdempotencyTombstoneSha256", "gatewayDispatchStarted.recoveryIdempotencyTombstoneSha256",
    "closure.recoveryIdempotencyTombstoneSha256", "providerReceipt.recoveryIdempotencyTombstoneSha256",
    "gatewaySettled.recoveryIdempotencyTombstoneSha256", "gatewayCancelled.recoveryIdempotencyTombstoneSha256",
    "appAttestation.recoveryIdempotencyTombstoneSha256",
  ]),
  ...edgeGroup("HASH-INTENT", "full-hash", "intent", [
    "gatewayDispatchStarted.recoveryEgressIntentSha256", "closure.recoveryEgressIntentSha256",
    "providerReceipt.recoveryEgressIntentSha256", "gatewaySettled.recoveryEgressIntentSha256",
    "gatewayCancelled.recoveryEgressIntentSha256", "appAttestation.recoveryEgressIntentSha256",
  ]),
  ...edgeGroup("HASH-DISPATCH", "full-hash", "gatewayDispatchStarted", [
    "gatewaySettled.previousOperationReceiptSha256", "closure.gatewayDispatchStartedEntrySha256",
    "providerReceipt.gatewayDispatchStartedReceiptSha256", "appAttestation.gatewayDispatchStartedReceiptSha256",
  ], { appliesTo: "post-dispatch" }),
  ...edgeGroup("HASH-PROVIDER", "full-hash", "providerReceipt", [
    "gatewaySettled.providerReceiptSha256", "appAttestation.providerReceiptSha256",
  ], { appliesTo: "terminal-provider" }),
  ...edgeGroup("HASH-SETTLED", "full-hash", "gatewaySettled", [
    "appAttestation.gatewaySettledReceiptSha256",
  ], { appliesTo: "terminal-provider" }),
  ...edgeGroup("HASH-CLOSURE", "full-hash", "closure", [
    "gatewayCancelled.recoveryEgressClosureSha256",
  ], { appliesTo: "zero-byte-cancel" }),
  ...edgeGroup("HASH-FAILURE-PROOF", "full-hash", "gatewayTerminalFailure", [
    "failedLease.failureProofSha256",
  ], { appliesTo: "failed-lease" }),
  ...edgeGroup("ID-FAILURE-PROOF", "equal", "gatewayTerminalFailure.gatewayReceiptId", [
    "failedLease.failureProofRef",
  ], { appliesTo: "failed-lease" }),

  // Operation, provider, request, marker, installation and credential identity.
  ...edgeGroup("OP-CORRELATION", "equal", "issuedLease.operationCorrelationId", [
    "claimedLease.operationCorrelationId", "failedLease.operationCorrelationId", "gatewayRegistered.operationCorrelationId",
    "gatewayAccepted.operationCorrelationId", "tombstone.operationCorrelationId",
    "intent.operationCorrelationId", "gatewayDispatchStarted.operationCorrelationId",
    "closure.operationCorrelationId", "providerReceipt.operationCorrelationId",
    "gatewaySettled.operationCorrelationId", "gatewayCancelled.operationCorrelationId", "appAttestation.operationCorrelationId",
    "providerRequestContract.clientMutationId",
  ]),
  ...edgeGroup("OP-IDEMPOTENCY", "equal", "issuedLease.providerIdempotencyKeySha256", [
    "claimedLease.providerIdempotencyKeySha256", "failedLease.providerIdempotencyKeySha256",
    "gatewayRegistered.providerIdempotencyKeySha256",
    "gatewayAccepted.providerIdempotencyKeySha256", "tombstone.providerIdempotencyKeySha256",
    "intent.providerIdempotencyKeySha256", "gatewayDispatchStarted.providerIdempotencyKeySha256",
    "providerReceipt.providerIdempotencyKeySha256", "gatewaySettled.providerIdempotencyKeySha256",
    "gatewayCancelled.providerIdempotencyKeySha256", "appAttestation.providerIdempotencyKeySha256",
  ]),
  ...edgeGroup("OP-AUTHORIZATION", "equal", "issuedLease.authorizationEntrySha256", [
    "claimedLease.authorizationEntrySha256", "failedLease.authorizationEntrySha256",
    "gatewayRegistered.authorizationEntrySha256",
    "gatewayAccepted.authorizationEntrySha256", "tombstone.authorizationEntrySha256",
    "intent.authorizationEntrySha256", "gatewayDispatchStarted.authorizationEntrySha256",
    "providerReceipt.authorizationEntrySha256", "gatewaySettled.authorizationEntrySha256",
    "gatewayCancelled.authorizationEntrySha256", "appAttestation.authorizationEntrySha256",
  ]),
  ...edgeGroup("OP-BRANCH", "equal", "issuedLease.branch", [
    "claimedLease.branch", "failedLease.branch", "gatewayRegistered.branch", "gatewayAccepted.branch", "tombstone.branch",
    "intent.branch", "gatewayDispatchStarted.branch", "providerReceipt.branch",
    "gatewaySettled.branch", "gatewayCancelled.branch", "appAttestation.branch", "providerRequestContract.branch",
  ]),
  ...edgeGroup("OP-EXPECTED-OID", "equal", "issuedLease.expectedRefOid", [
    "claimedLease.expectedRefOid", "failedLease.expectedRefOid", "gatewayRegistered.expectedRefOid", "gatewayAccepted.expectedRefOid",
    "tombstone.expectedRefOid", "intent.expectedRefOid", "gatewayDispatchStarted.expectedRefOid",
    "providerReceipt.expectedRefOid", "gatewaySettled.expectedRefOid", "gatewayCancelled.expectedRefOid", "appAttestation.expectedRefOid",
    "providerRequestContract.expectedRefOid",
  ]),
  ...edgeGroup("OP-TARGET-OID", "equal", "issuedLease.targetRefOid", [
    "claimedLease.targetRefOid", "failedLease.targetRefOid", "gatewayRegistered.targetRefOid", "gatewayAccepted.targetRefOid",
    "tombstone.targetRefOid", "intent.targetRefOid", "gatewayDispatchStarted.targetRefOid",
    "providerReceipt.targetRefOid", "gatewaySettled.targetRefOid", "gatewayCancelled.targetRefOid", "appAttestation.targetRefOid",
    "providerRequestContract.targetRefOid", "tombstone.providerMarkerTargetOid",
    "intent.providerMarkerTargetOid", "gatewayRegistered.providerMarkerTargetOid",
    "gatewayAccepted.providerMarkerTargetOid", "gatewayDispatchStarted.providerMarkerTargetOid",
    "gatewaySettled.providerMarkerTargetOid", "gatewayCancelled.providerMarkerTargetOid",
    "providerReceipt.providerMarkerTargetOid", "appAttestation.providerMarkerTargetOid",
  ]),
  ...edgeGroup("OP-TYPE", "equal", "issuedLease.operationType", [
    "claimedLease.operationType", "failedLease.operationType", "appAttestation.operationType",
  ]),
  ...edgeGroup("OP-SUBJECT", "equal", "issuedLease.operationSubjectId", [
    "claimedLease.operationSubjectId", "failedLease.operationSubjectId",
  ]),
  ...edgeGroup("LEASE-ISSUED-AT", "equal", "issuedLease.issuedAt", [
    "claimedLease.issuedAt", "failedLease.issuedAt",
  ]),
  ...edgeGroup("LEASE-EXPIRES-AT", "equal", "issuedLease.expiresAt", [
    "claimedLease.expiresAt", "failedLease.expiresAt", "appAttestation.leaseExpiresAt",
  ]),
  ...edgeGroup("LEASE-REGISTRATION-REF", "equal", "claimedLease.gatewayRegistrationReceiptRef", [
    "failedLease.gatewayRegistrationReceiptRef",
  ]),
  ...edgeGroup("LEASE-REGISTRATION-HASH", "equal", "claimedLease.gatewayRegistrationReceiptSha256", [
    "failedLease.gatewayRegistrationReceiptSha256",
  ]),
  ...edgeGroup("LEASE-REGISTRATION-CHECKPOINT", "equal", "claimedLease.gatewayRegistrationCheckpointSha256", [
    "failedLease.gatewayRegistrationCheckpointSha256",
  ]),
  ...edgeGroup("LEASE-REGISTRATION-TREE-SIZE", "equal", "claimedLease.gatewayRegistrationCheckpointTreeSize", [
    "failedLease.gatewayRegistrationCheckpointTreeSize",
  ]),
  ...edgeGroup("PROVIDER-ORIGIN", "equal", "gatewayRegistered.providerApiOrigin", [
    "gatewayAccepted.providerApiOrigin", "intent.providerApiOrigin",
    "gatewayDispatchStarted.providerApiOrigin", "closure.providerApiOrigin",
    "providerReceipt.providerApiOrigin", "gatewaySettled.providerApiOrigin",
    "gatewayCancelled.providerApiOrigin", "appAttestation.providerApiOrigin",
  ]),
  ...edgeGroup("PROVIDER-ENDPOINT", "equal", "gatewayRegistered.providerEndpointSha256", [
    "gatewayAccepted.providerEndpointSha256", "intent.providerEndpointSha256",
    "gatewayDispatchStarted.providerEndpointSha256", "closure.providerEndpointSha256",
    "providerReceipt.providerEndpointSha256", "gatewaySettled.providerEndpointSha256",
    "gatewayCancelled.providerEndpointSha256",
    "appAttestation.providerEndpointSha256",
  ]),
  ...edgeGroup("PROVIDER-INSTALLATION", "equal", "externalPins.recoveryWriteAheadGateway.providerInstallationIdentitySha256", [
    "gatewayRegistered.providerInstallationIdentitySha256", "gatewayAccepted.providerInstallationIdentitySha256",
    "tombstone.providerInstallationIdentitySha256", "intent.providerInstallationIdentitySha256",
    "gatewayDispatchStarted.providerInstallationIdentitySha256", "closure.providerInstallationIdentitySha256",
    "providerReceipt.providerInstallationIdentitySha256", "gatewaySettled.providerInstallationIdentitySha256",
    "gatewayCancelled.providerInstallationIdentitySha256",
    "appAttestation.providerInstallationIdentitySha256",
  ]),
  ...edgeGroup("PROVIDER-CREDENTIAL", "equal", "externalPins.recoveryWriteAheadGateway.providerCredentialIdentitySha256", [
    "gatewayRegistered.providerCredentialIdentitySha256", "gatewayAccepted.providerCredentialIdentitySha256",
    "tombstone.providerCredentialIdentitySha256", "intent.providerCredentialIdentitySha256",
    "gatewayDispatchStarted.providerCredentialIdentitySha256", "closure.providerCredentialIdentitySha256",
    "providerReceipt.providerCredentialIdentitySha256", "gatewaySettled.providerCredentialIdentitySha256",
    "gatewayCancelled.providerCredentialIdentitySha256",
    "appAttestation.providerCredentialIdentitySha256",
  ]),
  ...edgeGroup("REQUEST-BYTES", "bytes-sha256", "artifacts.providerRequestBytes", [
    "gatewayRegistered.providerRequestSha256", "gatewayAccepted.providerRequestSha256",
    "tombstone.providerRequestSha256", "intent.providerRequestSha256",
    "gatewayDispatchStarted.providerRequestSha256", "closure.providerRequestSha256",
    "providerReceipt.providerRequestSha256", "gatewaySettled.providerRequestSha256",
    "gatewayCancelled.providerRequestSha256",
  ]),
  ...edgeGroup("RESPONSE-BYTES", "bytes-sha256", "artifacts.providerResponseBytes", [
    "providerReceipt.providerResponseSha256",
  ], { appliesTo: "terminal-provider" }),
  ...edgeGroup("TLS-BYTES", "bytes-sha256", "artifacts.tlsTranscriptBytes", [
    "providerReceipt.tlsTranscriptSha256",
  ], { appliesTo: "terminal-provider" }),
  ...edgeGroup("MARKER-REF", "equal", "providerRequestContract.markerRef", [
    "gatewayRegistered.providerMarkerRef", "gatewayAccepted.providerMarkerRef",
    "tombstone.providerMarkerRef", "intent.providerMarkerRef", "gatewayDispatchStarted.providerMarkerRef",
    "closure.providerMarkerRef", "providerReceipt.providerMarkerRef", "gatewaySettled.providerMarkerRef",
    "gatewayCancelled.providerMarkerRef", "appAttestation.providerMarkerRef",
  ]),
  ...edgeGroup("REQUEST-REPOSITORY", "equal", "externalPins.recoveryWriteAheadGateway.repositoryNodeId", [
    "providerRequestContract.repositoryNodeId",
  ]),
  ...edgeGroup("REQUEST-ID", "equal", "providerResponseContract.providerRequestId", [
    "providerReceipt.providerRequestId",
  ], { appliesTo: "terminal-provider" }),
  ...edgeGroup("REQUEST-REF", "equal", "evidenceBindings.providerRequestRef", [
    "providerReceipt.providerRequestRef",
  ], { appliesTo: "terminal-provider" }),
  ...edgeGroup("RESPONSE-REF", "equal", "evidenceBindings.providerResponseRef", [
    "providerReceipt.providerResponseRef",
  ], { appliesTo: "terminal-provider" }),
  ...edgeGroup("TLS-REF", "equal", "evidenceBindings.tlsTranscriptRef", [
    "providerReceipt.tlsTranscriptRef",
  ], { appliesTo: "terminal-provider" }),
  ...edgeGroup("TLS-CERTIFICATE-CHAIN", "equal", "tlsTranscriptContract.providerCertificateChainSha256", [
    "providerReceipt.providerCertificateChainSha256",
  ], { appliesTo: "terminal-provider" }),
  ...edgeGroup("COUNTER-FINAL-BYTES", "equal", "egressCounterContract.finalProviderBytesSent", [
    "providerReceipt.finalProviderBytesSent",
  ], { appliesTo: "terminal-provider" }),
  ...edgeGroup("TOKEN-CONSUMED-AT", "equal", "egressCounterContract.oneShotEgressTokenConsumedAt", [
    "providerReceipt.oneShotEgressTokenConsumedAt",
  ], { appliesTo: "terminal-provider" }),

  // Fields carried unchanged through later Gateway receipts and App evidence.
  ...edgeGroup("PROP-REGISTERED-AT", "equal", "gatewayRegistered.registeredAt", [
    "gatewayAccepted.registeredAt", "gatewayDispatchStarted.registeredAt",
    "gatewaySettled.registeredAt", "gatewayCancelled.registeredAt",
  ]),
  ...edgeGroup("PROP-ACCEPTED-AT", "equal", "gatewayAccepted.acceptedAt", [
    "gatewayDispatchStarted.acceptedAt", "gatewaySettled.acceptedAt",
    "gatewayCancelled.acceptedAt",
  ]),
  ...edgeGroup("PROP-DISPATCH-AT", "equal", "gatewayDispatchStarted.dispatchStartedAt", [
    "gatewaySettled.dispatchStartedAt", "gatewayCancelled.dispatchStartedAt",
  ], { appliesTo: "post-dispatch" }),
  ...edgeGroup("PROP-FLOOR-CHALLENGE", "equal", "gatewayAccepted.floorChallengeNonce", [
    "gatewayDispatchStarted.floorChallengeNonce", "gatewaySettled.floorChallengeNonce",
    "gatewayCancelled.floorChallengeNonce", "appAttestation.floorChallengeNonce",
  ]),
  ...edgeGroup("PROP-WITNESS-FLOOR-HASH", "equal", "gatewayAccepted.witnessFloorResponsesSha256", [
    "gatewayDispatchStarted.witnessFloorResponsesSha256", "gatewaySettled.witnessFloorResponsesSha256",
    "gatewayCancelled.witnessFloorResponsesSha256",
  ]),
  ...edgeGroup("APP-WITNESS-FLOOR-HASH", "rfc8785-sha256", "appAttestation.witnessFloorResponses", [
    "gatewayAccepted.witnessFloorResponsesSha256",
  ], { appliesTo: "terminal-provider" }),
  ...edgeGroup("PROVIDER-RESULT", "equal", "providerReceipt.result", [
    "appAttestation.result",
  ], { appliesTo: "terminal-provider" }),
  ...edgeGroup("PROVIDER-OBSERVED-BEFORE", "equal", "providerReceipt.observedRefOidBefore", [
    "appAttestation.observedRefOidBefore",
  ], { appliesTo: "terminal-provider" }),
  ...edgeGroup("PROVIDER-OBSERVED-AFTER", "equal", "providerReceipt.observedRefOidAfter", [
    "appAttestation.observedRefOidAfter",
  ], { appliesTo: "terminal-provider" }),
  ...edgeGroup("PROVIDER-OBSERVED-MARKER", "equal", "providerReceipt.observedProviderMarkerOid", [
    "appAttestation.observedProviderMarkerOid",
  ], { appliesTo: "terminal-provider" }),

  // Gateway, Monitor, Verifier and App service pins.
  ...edgeGroup("PIN-GATEWAY-SERVICE", "equal", "externalPins.recoveryWriteAheadGateway.serviceIdentity", [
    "gatewayRegistered.gatewayServiceIdentity", "gatewayAccepted.gatewayServiceIdentity",
    "gatewayDispatchStarted.gatewayServiceIdentity", "gatewaySettled.gatewayServiceIdentity",
    "gatewayCancelled.gatewayServiceIdentity", "tombstone.gatewayServiceIdentity",
  ]),
  ...edgeGroup("PIN-GATEWAY-KEY", "equal", "externalPins.recoveryWriteAheadGateway.keyRef", [
    "gatewayRegistered.gatewayKeyRef", "gatewayAccepted.gatewayKeyRef", "gatewayDispatchStarted.gatewayKeyRef",
    "gatewaySettled.gatewayKeyRef", "gatewayCancelled.gatewayKeyRef", "tombstone.gatewayKeyRef",
  ]),
  ...edgeGroup("PIN-GATEWAY-IMAGE", "equal", "externalPins.recoveryWriteAheadGateway.imageDigest", [
    "gatewayRegistered.gatewayImageDigest", "gatewayAccepted.gatewayImageDigest", "gatewayDispatchStarted.gatewayImageDigest",
    "gatewaySettled.gatewayImageDigest", "gatewayCancelled.gatewayImageDigest", "tombstone.gatewayImageDigest",
  ]),
  ...edgeGroup("PIN-GATEWAY-POLICY", "equal", "externalPins.recoveryWriteAheadGateway.policySha256", [
    "gatewayRegistered.gatewayPolicySha256", "gatewayAccepted.gatewayPolicySha256", "gatewayDispatchStarted.gatewayPolicySha256",
    "gatewaySettled.gatewayPolicySha256", "gatewayCancelled.gatewayPolicySha256", "tombstone.gatewayPolicySha256",
  ]),
  ...edgeGroup("PIN-GATEWAY-PERMISSIONS", "equal", "externalPins.recoveryWriteAheadGateway.permissionsSha256", [
    "gatewayRegistered.gatewayPermissionsSha256", "gatewayAccepted.gatewayPermissionsSha256",
    "gatewayDispatchStarted.gatewayPermissionsSha256", "gatewaySettled.gatewayPermissionsSha256",
    "gatewayCancelled.gatewayPermissionsSha256", "tombstone.gatewayPermissionsSha256",
  ]),
  ...edgeGroup("PIN-GATEWAY-TIME", "equal", "externalPins.recoveryWriteAheadGateway.trustedTimeSourceSha256", [
    "gatewayRegistered.trustedTimeSourceSha256", "gatewayAccepted.trustedTimeSourceSha256",
    "gatewayDispatchStarted.trustedTimeSourceSha256", "gatewaySettled.trustedTimeSourceSha256",
    "gatewayCancelled.trustedTimeSourceSha256", "tombstone.trustedTimeSourceSha256",
  ]),
  ...edgeGroup("PIN-MONITOR-SERVICE", "equal", "externalPins.egressEnforcementMonitor.serviceIdentity", [
    "intent.monitorServiceIdentity", "closure.monitorServiceIdentity",
  ]),
  ...edgeGroup("PIN-MONITOR-KEY", "equal", "externalPins.egressEnforcementMonitor.keyRef", [
    "intent.monitorKeyRef", "closure.monitorKeyRef",
  ]),
  ...edgeGroup("PIN-MONITOR-IMAGE", "equal", "externalPins.egressEnforcementMonitor.imageDigest", [
    "intent.monitorImageDigest", "closure.monitorImageDigest",
  ]),
  ...edgeGroup("PIN-MONITOR-POLICY", "equal", "externalPins.egressEnforcementMonitor.policySha256", [
    "intent.monitorPolicySha256", "closure.monitorPolicySha256",
  ]),
  ...edgeGroup("PIN-MONITOR-PERMISSIONS", "equal", "externalPins.egressEnforcementMonitor.permissionsSha256", [
    "intent.monitorPermissionsSha256", "closure.monitorPermissionsSha256",
  ]),
  ...edgeGroup("PIN-MONITOR-TIME", "equal", "externalPins.egressEnforcementMonitor.trustedTimeSourceSha256", [
    "intent.monitorTrustedTimeSourceSha256", "closure.monitorTrustedTimeSourceSha256",
  ]),
  ...edgeGroup("PIN-VERIFIER", "equal", "externalPins.providerRefVerifier.serviceIdentity", ["providerReceipt.verifierServiceIdentity"]),
  ...edgeGroup("PIN-VERIFIER-KEY", "equal", "externalPins.providerRefVerifier.keyRef", ["providerReceipt.verifierKeyRef"]),
  ...edgeGroup("PIN-VERIFIER-IMAGE", "equal", "externalPins.providerRefVerifier.imageDigest", ["providerReceipt.verifierImageDigest"]),
  ...edgeGroup("PIN-VERIFIER-POLICY", "equal", "externalPins.providerRefVerifier.policySha256", ["providerReceipt.verifierPolicySha256"]),
  ...edgeGroup("PIN-VERIFIER-TIME", "equal", "externalPins.providerRefVerifier.trustedTimeSourceSha256", ["providerReceipt.trustedTimeSourceSha256"]),
  ...edgeGroup("PIN-APP", "equal", "externalPins.recoveryApp.appIdentity", ["appAttestation.appIdentity"]),
  ...edgeGroup("PIN-APP-KEY", "equal", "externalPins.recoveryApp.keyRef", ["appAttestation.appKeyRef"]),
  ...edgeGroup("PIN-APP-IMAGE", "equal", "externalPins.recoveryApp.imageDigest", ["appAttestation.appImageDigest"]),
  ...edgeGroup("PIN-APP-POLICY", "equal", "externalPins.recoveryApp.policySha256", ["appAttestation.appPolicySha256"]),
  ...edgeGroup("PIN-APP-PERMISSIONS", "equal", "externalPins.recoveryApp.permissionsSha256", ["appAttestation.appPermissionsSha256"]),

  // Sealed Egress Handle/Namespace/Policy/Counter/Token.
  ...edgeGroup("EGRESS-HANDLE", "equal", "intent.controlPlaneHandleSha256", [
    "gatewayDispatchStarted.controlPlaneHandleSha256", "closure.controlPlaneHandleSha256",
    "providerReceipt.controlPlaneHandleSha256", "gatewaySettled.controlPlaneHandleSha256",
    "gatewayCancelled.controlPlaneHandleSha256",
    "appAttestation.controlPlaneHandleSha256",
  ]),
  ...edgeGroup("EGRESS-NAMESPACE", "equal", "intent.networkNamespaceSha256", [
    "gatewayDispatchStarted.networkNamespaceSha256", "closure.networkNamespaceSha256",
    "providerReceipt.networkNamespaceSha256", "gatewaySettled.networkNamespaceSha256",
    "gatewayCancelled.networkNamespaceSha256",
    "appAttestation.networkNamespaceSha256",
  ]),
  ...edgeGroup("EGRESS-POLICY", "equal", "intent.networkPolicySha256", [
    "gatewayDispatchStarted.networkPolicySha256", "closure.networkPolicySha256",
    "providerReceipt.networkPolicySha256", "gatewaySettled.networkPolicySha256",
    "gatewayCancelled.networkPolicySha256",
    "appAttestation.networkPolicySha256",
  ]),
  ...edgeGroup("EGRESS-COUNTER", "equal", "intent.providerByteCounterIdSha256", [
    "gatewayDispatchStarted.providerByteCounterIdSha256", "closure.providerByteCounterIdSha256",
    "providerReceipt.providerByteCounterIdSha256", "gatewaySettled.providerByteCounterIdSha256",
    "gatewayCancelled.providerByteCounterIdSha256",
    "appAttestation.providerByteCounterIdSha256", "egressCounterContract.providerByteCounterIdSha256",
  ]),
  ...edgeGroup("EGRESS-TOKEN", "equal", "intent.oneShotEgressTokenSha256", [
    "gatewayDispatchStarted.oneShotEgressTokenSha256", "closure.oneShotEgressTokenSha256",
    "providerReceipt.oneShotEgressTokenSha256", "gatewaySettled.oneShotEgressTokenSha256",
    "gatewayCancelled.oneShotEgressTokenSha256", "appAttestation.oneShotEgressTokenSha256",
    "egressCounterContract.oneShotEgressTokenSha256",
  ]),

  // Exact checkpoint bindings. `checkpoint` targets name a Sha256/TreeSize pair;
  // `checkpoint-sha` targets name the exact checkpoint digest field when that
  // closed schema deliberately does not repeat TreeSize.
  ...edgeGroup("CHECKPOINT-AUTH", "checkpoint", "authorizationEntry", [
    "issuedLease.authorizationCheckpoint", "claimedLease.authorizationCheckpoint",
    "failedLease.authorizationCheckpoint", "appAttestation.authorizationCheckpoint",
  ]),
  ...edgeGroup("CHECKPOINT-AUTH-SHA", "checkpoint-sha", "authorizationEntry", [
    "gatewayRegistered.authorizationCheckpointSha256", "gatewayAccepted.authorizationCheckpointSha256",
    "gatewayDispatchStarted.authorizationCheckpointSha256", "providerReceipt.authorizationCheckpointSha256",
    "gatewaySettled.authorizationCheckpointSha256", "gatewayCancelled.authorizationCheckpointSha256",
  ]),
  ...edgeGroup("CHECKPOINT-REGISTERED", "checkpoint", "gatewayRegistered", [
    "claimedLease.gatewayRegistrationCheckpoint",
  ]),
  ...edgeGroup("CHECKPOINT-CLAIM", "checkpoint", "claimedLease", [
    "appAttestation.leaseCheckpoint",
  ]),
  ...edgeGroup("CHECKPOINT-CLAIM-SHA", "checkpoint-sha", "claimedLease", [
    "gatewayAccepted.leaseCheckpointSha256", "gatewayDispatchStarted.leaseCheckpointSha256",
    "providerReceipt.leaseCheckpointSha256", "gatewaySettled.leaseCheckpointSha256",
    "gatewayCancelled.leaseCheckpointSha256",
  ]),
  ...edgeGroup("CHECKPOINT-ACCEPTED", "checkpoint", "gatewayAccepted", [
    "tombstone.gatewayAcceptedCheckpoint", "intent.gatewayAcceptedCheckpoint",
    "appAttestation.gatewayAcceptedCheckpoint",
  ]),
  ...edgeGroup("CHECKPOINT-TOMBSTONE", "checkpoint", "tombstone", [
    "intent.recoveryIdempotencyTombstoneCheckpoint",
    "gatewayDispatchStarted.recoveryIdempotencyTombstoneCheckpoint",
    "providerReceipt.recoveryIdempotencyTombstoneCheckpoint",
    "gatewaySettled.recoveryIdempotencyTombstoneCheckpoint",
    "gatewayCancelled.recoveryIdempotencyTombstoneCheckpoint",
    "appAttestation.recoveryIdempotencyTombstoneCheckpoint",
  ]),
  ...edgeGroup("CHECKPOINT-INTENT", "checkpoint", "intent", [
    "gatewayDispatchStarted.recoveryEgressIntentCheckpoint", "closure.recoveryEgressIntentCheckpoint",
    "providerReceipt.recoveryEgressIntentCheckpoint", "gatewaySettled.recoveryEgressIntentCheckpoint",
    "gatewayCancelled.recoveryEgressIntentCheckpoint", "appAttestation.recoveryEgressIntentCheckpoint",
  ]),
  ...edgeGroup("CHECKPOINT-DISPATCH", "checkpoint", "gatewayDispatchStarted", [
    "closure.gatewayDispatchStartedCheckpoint", "providerReceipt.gatewayDispatchStartedCheckpoint",
    "appAttestation.gatewayDispatchStartedCheckpoint",
  ], { appliesTo: "post-dispatch" }),
  ...edgeGroup("CHECKPOINT-SETTLED", "checkpoint", "gatewaySettled", [
    "appAttestation.gatewaySettledCheckpoint",
  ], { appliesTo: "terminal-provider" }),
  ...edgeGroup("CHECKPOINT-FAILURE", "checkpoint", "gatewayTerminalFailure", [
    "failedLease.failureProofCheckpoint",
  ], { appliesTo: "failed-lease" }),
  ...edgeGroup("CHECKPOINT-AUTH-ISSUED-AT", "equal", "checkpoint:authorizationEntry.issuedAt", [
    "appAttestation.authorizationCheckpointIssuedAt",
  ], { appliesTo: "terminal-provider" }),
  ...edgeGroup("CHECKPOINT-CLAIM-ISSUED-AT", "equal", "checkpoint:claimedLease.issuedAt", [
    "appAttestation.leaseCheckpointIssuedAt",
  ], { appliesTo: "terminal-provider" }),

  // Normative time order and the five fixed five-second skew edges.
  ...edgeGroup("TIME-00", "time-lt", "checkpoint:authorizationEntry.issuedAt", ["checkpoint:claimedLease.issuedAt"]),
  ...edgeGroup("TIME-01", "time-lt", "checkpoint:claimedLease.issuedAt", ["appAttestation.operationStartedAt"]),
  ...edgeGroup("TIME-02", "time-lte", "appAttestation.operationStartedAt", ["gatewayAccepted.acceptedAt"], { maxSkewMs: 5000 }),
  ...edgeGroup("TIME-03", "time-lte", "gatewayAccepted.acceptedAt", ["gatewayAccepted.loggedAt"]),
  ...edgeGroup("TIME-04", "time-lt", "gatewayAccepted.loggedAt", ["checkpoint:gatewayAccepted.issuedAt"]),
  ...edgeGroup("TIME-05", "time-lte", "checkpoint:gatewayAccepted.issuedAt", ["tombstone.createdAt"]),
  ...edgeGroup("TIME-06", "time-lte", "tombstone.createdAt", ["tombstone.loggedAt"]),
  ...edgeGroup("TIME-07", "time-lte", "tombstone.loggedAt", ["checkpoint:tombstone.issuedAt"]),
  ...edgeGroup("TIME-08", "time-lt", "checkpoint:tombstone.issuedAt", ["intent.provisionedAt"]),
  ...edgeGroup("TIME-09", "time-lte", "intent.provisionedAt", ["intent.loggedAt"]),
  ...edgeGroup("TIME-10", "time-lte", "intent.loggedAt", ["checkpoint:intent.issuedAt"]),
  ...edgeGroup("TIME-11", "time-lt", "checkpoint:intent.issuedAt", ["gatewayDispatchStarted.dispatchStartedAt"]),
  ...edgeGroup("TIME-12", "time-lte", "gatewayDispatchStarted.dispatchStartedAt", ["gatewayDispatchStarted.loggedAt"]),
  ...edgeGroup("TIME-13", "time-lte", "gatewayDispatchStarted.loggedAt", ["checkpoint:gatewayDispatchStarted.issuedAt"]),
  ...edgeGroup("TIME-14", "time-lte", "checkpoint:gatewayDispatchStarted.issuedAt", ["providerReceipt.oneShotEgressTokenConsumedAt"]),
  ...edgeGroup("TIME-15", "time-lte", "providerReceipt.oneShotEgressTokenConsumedAt", ["providerReceipt.providerRequestStartedAt"]),
  ...edgeGroup("TIME-16", "time-lte", "checkpoint:gatewayDispatchStarted.issuedAt", ["providerReceipt.providerRequestStartedAt"], { maxSkewMs: 5000 }),
  ...edgeGroup("TIME-17", "time-lte", "providerReceipt.providerRequestStartedAt", ["providerReceipt.providerAcceptedAt"]),
  ...edgeGroup("TIME-18", "time-lte", "providerReceipt.providerAcceptedAt", ["providerReceipt.providerCompletedAt"]),
  ...edgeGroup("TIME-19", "time-lte", "providerReceipt.providerCompletedAt", ["appAttestation.operationCompletedAt"], { maxSkewMs: 5000 }),
  ...edgeGroup("TIME-20", "time-lte", "appAttestation.operationCompletedAt", ["providerReceipt.providerObservedAt"]),
  ...edgeGroup("TIME-21", "time-lte", "providerReceipt.providerObservedAt", ["providerReceipt.verificationStartedAt"]),
  ...edgeGroup("TIME-22", "time-lte", "providerReceipt.verificationStartedAt", ["providerReceipt.verificationCompletedAt"]),
  ...edgeGroup("TIME-23", "time-lte", "providerReceipt.verificationCompletedAt", ["gatewaySettled.settledAt"]),
  ...edgeGroup("TIME-24", "time-lte", "gatewaySettled.settledAt", ["gatewaySettled.loggedAt"]),
  ...edgeGroup("TIME-25", "time-lte", "gatewaySettled.loggedAt", ["checkpoint:gatewaySettled.issuedAt"]),
  ...edgeGroup("TIME-26", "time-lte", "checkpoint:gatewaySettled.issuedAt", ["appAttestation.attestedAt"]),
  ...edgeGroup("TIME-27", "time-lte", "appAttestation.attestedAt", ["issuedLease.expiresAt", "appAttestation.authorizationExpiresAt"]),
  ...edgeGroup("TIME-28", "time-lte", "max:appAttestation.witnessFloorResponses[].respondedAt", ["gatewayAccepted.acceptedAt"], { maxSkewMs: 5000 }),
  ...edgeGroup("TIME-29", "time-lte", "max:providerReceipt.dispatchWitnessFloorResponses[].respondedAt", ["providerReceipt.providerRequestStartedAt"], { maxSkewMs: 5000 }),
  ...edgeGroup("TIME-30", "time-lte", "intent.expiresAt", ["issuedLease.expiresAt"]),
  ...edgeGroup("TIME-CLOSURE-01", "time-lte", "closure.counterSealedAt", ["closure.namespaceDestroyedAt"], { appliesTo: "zero-byte-cancel" }),
  ...edgeGroup("TIME-CLOSURE-02", "time-lte", "closure.namespaceDestroyedAt", ["closure.closedAt"], { appliesTo: "zero-byte-cancel" }),
  ...edgeGroup("TIME-CLOSURE-03", "time-lte", "closure.closedAt", ["closure.monitorSignature.signedAt"], { appliesTo: "zero-byte-cancel" }),
]);
```

`when-present` means that the state cross-product, not this equality helper,
decides whether an optional branch artifact must exist; once both endpoint
aliases exist the edge is mandatory. The resolver rejects an unknown alias,
an absent endpoint required by the active cross-product branch, duplicate
edge ID, unsupported `kind`, a target that is also accepted from an unlisted
source, or any edge whose source/target is not schema-declared. Conditional
success, authenticated-final-failure, pre-dispatch closure, post-dispatch
zero-byte closure, and failed-Lease fixtures together must exercise every edge
at least once. For success, `providerReceipt.observedRefOidBefore` and
`appAttestation.observedRefOidBefore` equal `issuedLease.expectedRefOid`, while
both `observedRefOidAfter` and non-null marker observations equal
`issuedLease.targetRefOid`; authenticated failure instead requires after=before
and both marker observations null. The request validator's returned
`providerRequestSha256`, `markerRef`, branch/OIDs, `clientMutationId`, and pinned
repository node ID are part of the table input, not independently trusted
booleans.

For each Issued Lease, `buildRecoveryEdgeContext` selects at most one artifact
for every named phase, rejects duplicate phase aliases, selects exactly that
Lease's `evidenceByLeaseId` record, parses and authenticates its raw evidence,
derives `repositoryAnchor` from the branded Transparency replay, and resolves
every virtual checkpoint from that same replay.
It derives the active applicability set exactly as `terminal-provider`,
`post-dispatch`, `zero-byte-cancel`, and/or `failed-lease`; no caller passes
those labels. `verifyRecoveryCrossArtifactEdges` must then execute the frozen
table exactly once before state derivation. `assertSame`, a second allowlist,
or a fallback equality loop is forbidden because it would create an
unreviewed parallel contract.

Add one generated negative test per expanded edge. The test clones the valid
fixture for `edge.appliesTo`, mutates only `edge.target` (one digest bit, one ID
byte, one pin/identity byte, one OID nibble, one integer unit, a null/non-null
flip, or one millisecond past the exact time/skew boundary), and requires the unique diagnostic
`RECOVERY-EDGE-BINDING:<edge.id>`. It also asserts that all edge IDs are unique,
every source and target resolves, every applicable edge was executed, the
valid fixtures execute the entire table with zero diagnostics, and removing any
table row makes its corresponding mutation fail the coverage test rather than
silently pass.

- [ ] **Step 6: Run and confirm GREEN**

Expected: valid success passes; failure passes only with authenticated final
rejection; unknown and every shared-field/time mutation fail closed.

- [ ] **Step 7: Commit provider and App evidence**

```powershell
git add docs/governance/schemas/provider-ref-update-receipt.schema.json docs/governance/schemas/recovery-app-attestation.schema.json scripts/fixtures/governance/recovery/valid-success.json scripts/governance/schema-builders/recovery.mjs scripts/governance/recovery-verifier-internal.mjs scripts/governance/recovery-verifier.test.mjs
git commit -m "feat: verify recovery provider evidence"
```

### Task 7: Lock RFC-8785 payload-core and entry-core vectors

**Files:**

- Create: `scripts/fixtures/governance/recovery/rfc8785-cores.json`
- Modify: `scripts/governance/recovery-verifier.test.mjs`

- [ ] **Step 1: Add literal golden core bytes for all seven artifacts**

For Lease, Gateway, Tombstone, Intent, Closure, Provider Receipt, and App
Attestation store: the complete fixture object, the exact ordered exclusion
list, literal canonical core UTF-8 as base64url, and independently fixed SHA-256.
Gateway stores two vectors: payload-only `receiptCoreSha256` and complete log
`entryCoreSha256`. The expected bytes must be reviewed literals, not output
from `canonicalBytes` during the test.

- [ ] **Step 2: Add one-field mutation loops**

Mutate every bound scalar and each nested signature/floor item independently;
assert its core digest changes. Mutate only excluded core/signature/common-log
fields and assert the appropriate payload-core remains unchanged while the
full entry core changes where required.

- [ ] **Step 3: Run and confirm GREEN**

Run the focused `rfc8785 recovery core` tests. Expected: every literal byte/
digest vector and projection mutation passes.

- [ ] **Step 4: Commit the golden vectors**

```powershell
git add scripts/fixtures/governance/recovery/rfc8785-cores.json scripts/governance/recovery-verifier.test.mjs
git commit -m "test: lock recovery RFC 8785 cores"
```

### Task 8: Exhaust the recovery state cross-product and integrate

**Files:**

- Create: `scripts/fixtures/governance/recovery/state-cross-product.json`
- Modify: `scripts/governance/recovery-verifier-internal.mjs`
- Modify: `scripts/governance/recovery-verifier.mjs`
- Modify: `scripts/governance/transparency-verifier.mjs`
- Modify: `scripts/governance/nonce-replay.mjs`
- Modify: `scripts/governance/nonce-replay.test.mjs`
- Modify: `scripts/governance-contract.mjs`
- Modify: `scripts/governance-contract.test.mjs`

- [ ] **Step 1: Encode the full cross-product table**

Each row explicitly names Lease phase, Gateway phase, Tombstone present,
Intent present, closure reason/null, abort reason/null, failure-proof type/null,
expected derived state, and valid/invalid. Cover every cartesian combination;
do not sample. Valid rows must include issued/pending, claimed/executing,
pre-dispatch cancel/failed, post-dispatch zero-byte cancel/failed, settled
success/terminal-capable, settled final failure/failed, and unknown/executing.

- [ ] **Step 2: Write the table-driven RED test**

Assert `deriveRecoveryOperationState` returns exactly
`pending|executing|failed|completed|aborted` and rejects every invalid
nullability combination before terminal TCB composition.

In the same RED wave, modify only Plan 06's `GOVERNANCE_NONCE_PATHS` source
literal. Every entry has exactly `owned/references`, both frozen arrays of
strings in Plan-06 dot/`[]` path grammar without a leading `$.`. Do not rename
the literal, call `Object.assign`, export a mutation API, or mutate it at
runtime. Mark new Nonce owners separately from references so a repeated
authenticated challenge reference is equality-checked but not misreported as
a second issue. Insert these properties into that literal before its enclosing
`Object.freeze` executes:

```js-fragment
"recovery-operation-lease": Object.freeze({
  owned: Object.freeze(["instanceSignature.nonce"]), references: Object.freeze([]),
}),
"recovery-write-ahead-receipt": Object.freeze({
  owned: Object.freeze(["instanceSignature.nonce", "signature.nonce"]),
  references: Object.freeze(["floorChallengeNonce"]),
}),
"recovery-idempotency-tombstone": Object.freeze({
  owned: Object.freeze(["instanceSignature.nonce", "gatewaySignature.nonce"]),
  references: Object.freeze([]),
}),
"recovery-egress-intent": Object.freeze({
  owned: Object.freeze(["instanceSignature.nonce", "monitorSignature.nonce"]),
  references: Object.freeze([]),
}),
"recovery-egress-closure": Object.freeze({
  owned: Object.freeze(["monitorSignature.nonce"]), references: Object.freeze([]),
}),
"recovery-app-attestation": Object.freeze({
  owned: Object.freeze(["nonce"]),
  references: Object.freeze(["floorChallengeNonce", "witnessFloorResponses[].floorChallengeNonce"]),
}),
"provider-ref-update-receipt": Object.freeze({
  owned: Object.freeze(["nonce"]),
  references: Object.freeze(["dispatchFloorChallengeNonce", "dispatchWitnessFloorResponses[].floorChallengeNonce"]),
}),
```

The table is exact: an unlisted nonce-like schema path, missing owner,
owner duplication anywhere in the full Governance prefix, dangling challenge
reference, a reference that does not resolve to exactly one strictly earlier
owner, or reference unequal to that owner fails. References never enter the
owner uniqueness set and never increase `claimCount`. Tests concatenate
Bootstrap, EVT/attestation, Transparency and all Recovery domains and prove a
reuse across any two domains is rejected by the production Nonce replay.
Add a source-contract test in `scripts/governance-contract.test.mjs` that
requires the Recovery gate consumer to read exactly
`authorityClaims.transparency.bundleSha256`, rejects any legacy top-level
bundle-hash claim, and proves the standalone replay
still exposes `inventoryBindingVerified:false` before Plan 11 composition.

- [ ] **Step 3: Run and confirm RED**

Expected: incomplete state derivation fails at least one table row.

- [ ] **Step 4: Implement total deterministic state derivation**

Use exhaustive `switch` branches with an unreachable-state error; never use a
truthy fallback. Once dispatch exists, absent final provider evidence derives
only `executing`. After failure/abort/completion, old leases and authorization
are permanently consumed.

Implement the pure total reducer exactly as follows. `terminalPhase` is `null`,
`completed`, or `aborted` after Plan 08 validates the terminal TCB entry; a
Gateway success alone never invents completion.

```js
export function deriveRecoveryOperationStateCore({ leasePhase, gatewayPhase,
  closureReason = null, providerResult = null, terminalPhase = null }) {
  const fail = (message) => { throw new Error(`RECOVERY_STATE_INVALID: ${message}`); };
  if (!["issued", "claimed", "failed"].includes(leasePhase)) fail("unknown lease phase");
  if (![null, "registered", "accepted", "dispatch-started", "cancelled", "settled"].includes(gatewayPhase)) fail("unknown gateway phase");
  if (![null, "pre-dispatch-expiry", "post-dispatch-zero-byte"].includes(closureReason)) fail("unknown closure reason");
  if (![null, "succeeded", "failed", "unknown"].includes(providerResult)) fail("unknown provider result");
  if (![null, "completed", "aborted"].includes(terminalPhase)) fail("unknown terminal phase");

  if (terminalPhase === "completed") {
    if (leasePhase !== "claimed" || gatewayPhase !== "settled"
      || providerResult !== "succeeded" || closureReason !== null) fail("completion lacks settled success");
    return "completed";
  }
  if (terminalPhase === "aborted") {
    const abortable = gatewayPhase === null || gatewayPhase === "registered"
      || gatewayPhase === "accepted" || gatewayPhase === "cancelled"
      || (gatewayPhase === "settled" && providerResult === "failed");
    if (!abortable || providerResult === "succeeded") fail("abort follows successful or unresolved send");
    return "aborted";
  }
  if (leasePhase === "failed") {
    if (gatewayPhase === "cancelled") {
      if (providerResult !== null) fail("cancelled operation cannot have provider receipt");
      if (![null, "pre-dispatch-expiry", "post-dispatch-zero-byte"].includes(closureReason)) fail("invalid cancellation closure");
      return "failed";
    }
    if (gatewayPhase === "settled" && providerResult === "failed" && closureReason === null) return "failed";
    fail("failed lease lacks final failure proof");
  }
  if (leasePhase === "issued") {
    if (![null, "registered"].includes(gatewayPhase) || providerResult !== null || closureReason !== null) fail("issued lease advanced without claim");
    return "pending";
  }
  switch (gatewayPhase) {
    case "registered":
    case "accepted":
      if (providerResult !== null || closureReason !== null) fail("pre-dispatch state has provider/closure result");
      return "executing";
    case "dispatch-started":
      if (providerResult !== null || closureReason !== null) fail("dispatch-started cannot be terminal");
      return "executing";
    case "settled":
      if (closureReason !== null || providerResult === null || providerResult === "unknown") fail("settled requires final provider evidence");
      return "executing"; // awaits a Plan-08 terminal entry or failed Lease
    case "cancelled":
      fail("cancelled gateway requires failed Lease successor");
    case null:
      return "executing"; // claimed but gateway state not yet checkpoint-effective
    default:
      return fail("unreachable gateway phase");
  }
}
```

The exhaustive fixture enumerates all 3×6×3×4×3 combinations (with `null`
included as stated), so every branch and every rejection above is exercised.

- [ ] **Step 5: Add the immutable production wrapper**

`recovery-verifier.mjs` supplies real Ed25519 and first verifies raw
`verificationInputs`, Transparency, Recovery semantics, and the complete
versioned `nonceArtifacts` Plan-06 replay. That base result receives a
module-private production brand but always remains non-gate without the
optional Gate AuthorityContext. `isProductionRecoveryResult` exposes only
brand membership plus fixed validity bits so Plan 11 can consume the base in
Issuer Phase A without a cycle. Only afterwards may the same wrapper use
`readProductionAuthorityContext(authorityContext)` to derive gate status. Add
an import allowlist test and assert an injected property cannot bypass a
one-bit invalid signature. A plain/pre-Genesis/pre-Plan-11 context leaves the
otherwise valid base at
`authorityRequired:["production-authority-context"]`, `gateEffective:false`.
A changed Nonce-prefix head, omitted Recovery artifact, test-only dependency,
or invalid signature throws before branding. The internal semantic core
remains directly testable but can never mint the production brand.

Use one shared core and a production-only `WeakSet` brand:

```js
// recovery-verifier-internal.mjs
import { canonicalBytes } from "./rfc8785.mjs";
import { sha256Hex } from "./crypto.mjs";
import { validateSchema } from "./schema-registry.mjs";
import { deriveRecoveryOperationStateCore } from "./recovery-state.mjs";

const without = (value, names) => Object.fromEntries(Object.entries(value)
  .filter(([name]) => !names.includes(name)));
const fullHash = (value) => sha256Hex(canonicalBytes(value));
const at = (value) => { const n = Date.parse(value); if (!Number.isFinite(n)) throw new TypeError(`invalid time ${value}`); return n; };
const COMMON_LOG_FIELDS = ["schemaVersion", "entryKind", "repositoryId", "logId",
  "transparencyLogIndex", "previousLogEntrySha256", "loggedAt", "instanceKeyRef",
  "instanceKeyEpoch", "method", "entryCoreSha256", "instanceSignature"];
const payloadOf = (entry) => without(entry, COMMON_LOG_FIELDS);
const verifyServiceArtifact = (artifact, { schema, coreField, signatureField,
  pin, keyRefField = null, pinBindings = [], logEntry = false, verifySignature }) => {
  const errors = validateSchema(schema, artifact);
  if (errors.length) throw new Error(`RECOVERY_SCHEMA_INVALID: ${schema}`);
  const signedValue = logEntry ? payloadOf(artifact) : artifact;
  const core = without(signedValue, [coreField, signatureField]);
  if (artifact[coreField] !== fullHash(core)) throw new Error(`RECOVERY_CORE_INVALID: ${coreField}`);
  const signature = artifact[signatureField];
  const encoded = typeof signature === "string" ? signature : signature.signature;
  const keyRef = typeof signature === "string" ? artifact[keyRefField] : signature.keyRef;
  if (!pin || keyRef !== pin.keyRef
    || (typeof signature !== "string" && signature[coreField] !== artifact[coreField])) {
    throw new Error(`RECOVERY_SERVICE_PIN_INVALID: ${signatureField}`);
  }
  for (const [artifactField, pinField] of pinBindings) {
    if (artifact[artifactField] !== pin[pinField]) {
      throw new Error(`RECOVERY_SERVICE_PIN_INVALID: ${artifactField}`);
    }
  }
  if (!verifySignature({ publicKeyBase64url: pin.publicKeyBase64url,
    payloadBytes: canonicalBytes(core), signatureBase64url: encoded })) {
    throw new Error(`RECOVERY_SIGNATURE_INVALID: ${signatureField}`);
  }
};
const checkpointFor = (entry, checkpoints) => checkpoints.find((checkpoint) =>
  checkpoint.treeSize > entry.transparencyLogIndex);
const sameSequence = (actual, expected) => canonicalBytes(actual).equals(canonicalBytes(expected));
const ALLOWED_LEASE_CHAINS = [["issued"], ["issued", "claimed"],
  ["issued", "claimed", "failed"]];
const ALLOWED_GATEWAY_CHAINS = [
  ["registered"], ["registered", "accepted"],
  ["registered", "accepted", "dispatch-started"],
  ["registered", "accepted", "dispatch-started", "settled"],
  ["registered", "cancelled"], ["registered", "accepted", "cancelled"],
  ["registered", "accepted", "dispatch-started", "cancelled"],
];
const requireClosedPhaseChain = (chain, allowed, rule) => {
  const phases = chain.map((entry) => entry.phase);
  if (!allowed.some((candidate) => sameSequence(phases, candidate))) throw new Error(rule);
};
const GATEWAY_PIN_BINDINGS = [
  ["gatewayServiceIdentity", "serviceIdentity"], ["gatewayKeyRef", "keyRef"],
  ["gatewayImageDigest", "imageDigest"], ["gatewayPolicySha256", "policySha256"],
  ["gatewayPermissionsSha256", "permissionsSha256"],
  ["trustedTimeSourceSha256", "trustedTimeSourceSha256"],
  ["providerInstallationIdentitySha256", "providerInstallationIdentitySha256"],
  ["providerCredentialIdentitySha256", "providerCredentialIdentitySha256"],
];
const MONITOR_PIN_BINDINGS = [
  ["monitorServiceIdentity", "serviceIdentity"], ["monitorKeyRef", "keyRef"],
  ["monitorImageDigest", "imageDigest"], ["monitorPolicySha256", "policySha256"],
  ["monitorPermissionsSha256", "permissionsSha256"],
  ["monitorTrustedTimeSourceSha256", "trustedTimeSourceSha256"],
];

export function verifyRecoveryFullPrefixCore({ bundle, artifacts, externalPins,
  verificationTime, transparencyReplay }, { verifySignature }) {
  if (!transparencyReplay?.cryptographicValid || transparencyReplay.testOnly) {
    throw new Error("RECOVERY_REQUIRES_CRYPTOGRAPHIC_TRANSPARENCY_REPLAY");
  }
  const leases = bundle.entries.filter((entry) => entry.entryKind === "recovery-operation-lease");
  const gateways = bundle.entries.filter((entry) => entry.entryKind === "recovery-write-ahead-receipt");
  const tombstones = bundle.entries.filter((entry) => entry.entryKind === "recovery-idempotency-tombstone");
  const intents = bundle.entries.filter((entry) => entry.entryKind === "recovery-egress-intent");
  for (const entry of [...leases, ...gateways, ...tombstones, ...intents]) {
    if (!checkpointFor(entry, bundle.checkpoints)) throw new Error(`RECOVERY_ENTRY_NOT_CHECKPOINTED: ${entry.transparencyLogIndex}`);
  }
  const unique = (items, field) => {
    const seen = new Set();
    for (const item of items) { if (seen.has(item[field])) throw new Error(`RECOVERY_UNIQUENESS: ${field}`); seen.add(item[field]); }
  };
  unique(leases.filter((entry) => entry.phase === "issued"), "leaseId");
  unique(leases.filter((entry) => entry.phase === "issued"), "authorizationEntrySha256");
  unique(leases.filter((entry) => entry.phase === "issued"), "operationCorrelationId");
  unique(gateways, "gatewayReceiptId");
  unique(gateways, "gatewaySequence");
  unique(tombstones, "leaseId");
  unique(intents, "leaseId");
  for (const collection of [artifacts.closures, artifacts.providerReceipts,
    artifacts.appAttestations]) unique(collection, collection === artifacts.appAttestations
      ? "recoveryOperationLeaseId" : "leaseId");
  for (const field of ["operationCorrelationId", "providerIdempotencyKeySha256",
    "providerMarkerRef", "providerRequestSha256"]) unique(tombstones, field);
  for (const field of ["recoveryIdempotencyTombstoneSha256", "controlPlaneHandleSha256",
    "networkNamespaceSha256", "providerByteCounterIdSha256", "oneShotEgressTokenSha256"]) unique(intents, field);

  const issuedLeaseIds = new Set(leases.filter((entry) => entry.phase === "issued")
    .map((entry) => entry.leaseId));
  for (const item of [...leases, ...gateways, ...tombstones, ...intents,
    ...artifacts.closures, ...artifacts.providerReceipts]) {
    if (!issuedLeaseIds.has(item.leaseId)) throw new Error("RECOVERY_ORPHAN_ARTIFACT");
  }
  for (const item of artifacts.appAttestations) {
    if (!issuedLeaseIds.has(item.recoveryOperationLeaseId)) throw new Error("RECOVERY_ORPHAN_ARTIFACT");
  }

  const globallyOrderedGateways = [...gateways]
    .sort((left, right) => left.gatewaySequence - right.gatewaySequence);
  for (let index = 0; index < globallyOrderedGateways.length; index += 1) {
    const gateway = globallyOrderedGateways[index];
    const previous = index === 0 ? null : globallyOrderedGateways[index - 1];
    if (gateway.gatewaySequence !== index
      || gateway.previousGatewayReceiptSha256 !== (previous ? fullHash(previous) : null)) {
      throw new Error("RECOVERY_GLOBAL_GATEWAY_CHAIN_INVALID");
    }
    verifyServiceArtifact(gateway, { schema: "recovery-write-ahead-receipt",
      coreField: "receiptCoreSha256", signatureField: "signature", logEntry: true,
      pin: externalPins.recoveryWriteAheadGateway,
      pinBindings: GATEWAY_PIN_BINDINGS, verifySignature });
  }
  for (const tombstone of tombstones) {
    verifyServiceArtifact(tombstone, { schema: "recovery-idempotency-tombstone",
      coreField: "tombstoneCoreSha256", signatureField: "gatewaySignature", logEntry: true,
      pin: externalPins.recoveryWriteAheadGateway,
      pinBindings: GATEWAY_PIN_BINDINGS, verifySignature });
  }
  for (const intent of intents) {
    verifyServiceArtifact(intent, { schema: "recovery-egress-intent",
      coreField: "intentCoreSha256", signatureField: "monitorSignature", logEntry: true,
      pin: externalPins.egressEnforcementMonitor,
      pinBindings: MONITOR_PIN_BINDINGS, verifySignature });
  }

  const operations = [];
  for (const issued of leases.filter((entry) => entry.phase === "issued")) {
    const chain = leases.filter((entry) => entry.leaseId === issued.leaseId)
      .sort((a, b) => a.transparencyLogIndex - b.transparencyLogIndex);
    if (chain.length > 3 || chain[0] !== issued) throw new Error("RECOVERY_LEASE_FORK");
    requireClosedPhaseChain(chain, ALLOWED_LEASE_CHAINS, "RECOVERY_LEASE_PHASE_CHAIN");
    for (let index = 1; index < chain.length; index += 1) {
      if (chain[index].previousLeaseEntrySha256 !== fullHash(chain[index - 1])) throw new Error("RECOVERY_LEASE_PREDECESSOR");
    }
    const gatewayChain = gateways.filter((entry) => entry.leaseId === issued.leaseId)
      .sort((a, b) => a.gatewaySequence - b.gatewaySequence);
    if (gatewayChain.length) {
      requireClosedPhaseChain(gatewayChain, ALLOWED_GATEWAY_CHAINS,
        "RECOVERY_GATEWAY_PHASE_CHAIN");
    }
    for (let index = 0; index < gatewayChain.length; index += 1) {
      const prior = index === 0 ? null : gatewayChain[index - 1];
      if (gatewayChain[index].previousOperationReceiptSha256 !== (prior && fullHash(prior))) throw new Error("RECOVERY_GATEWAY_PREDECESSOR");
    }
    const tombstone = tombstones.find((item) => item.leaseId === issued.leaseId) ?? null;
    const intent = intents.find((item) => item.leaseId === issued.leaseId) ?? null;
    const closure = artifacts.closures.find((item) => item.leaseId === issued.leaseId) ?? null;
    const provider = artifacts.providerReceipts.find((item) => item.leaseId === issued.leaseId) ?? null;
    const app = artifacts.appAttestations.find((item) => item.recoveryOperationLeaseId === issued.leaseId) ?? null;
    if (closure) verifyServiceArtifact(closure, { schema: "recovery-egress-closure",
      coreField: "closureCoreSha256", signatureField: "monitorSignature",
      pin: externalPins.egressEnforcementMonitor,
      pinBindings: MONITOR_PIN_BINDINGS, verifySignature });
    if (provider) verifyServiceArtifact(provider, { schema: "provider-ref-update-receipt",
      coreField: "receiptCoreSha256", signatureField: "signature", keyRefField: "verifierKeyRef",
      pin: externalPins.providerRefVerifier,
      pinBindings: [["verifierServiceIdentity", "serviceIdentity"], ["verifierKeyRef", "keyRef"],
        ["verifierImageDigest", "imageDigest"], ["verifierPolicySha256", "policySha256"],
        ["trustedTimeSourceSha256", "trustedTimeSourceSha256"]], verifySignature });
    if (app) verifyServiceArtifact(app, { schema: "recovery-app-attestation",
      coreField: "attestationCoreSha256", signatureField: "signature", keyRefField: "appKeyRef",
      pin: externalPins.recoveryApp,
      pinBindings: [["appIdentity", "appIdentity"], ["appKeyRef", "keyRef"],
        ["appImageDigest", "imageDigest"], ["appPolicySha256", "policySha256"],
        ["appPermissionsSha256", "permissionsSha256"]], verifySignature });
    const phase = (name) => gatewayChain.find((entry) => entry.phase === name) ?? null;
    const evidence = artifacts.evidenceByLeaseId?.[issued.leaseId] ?? null;
    verifyRecoveryCrossArtifactEdges(buildRecoveryEdgeContext({
      bundle, transparencyReplay, externalPins, evidence,
      issuedLease: issued,
      claimedLease: chain.find((entry) => entry.phase === "claimed") ?? null,
      failedLease: chain.find((entry) => entry.phase === "failed") ?? null,
      gatewayRegistered: phase("registered"), gatewayAccepted: phase("accepted"),
      gatewayDispatchStarted: phase("dispatch-started"),
      gatewaySettled: phase("settled"), gatewayCancelled: phase("cancelled"),
      tombstone, intent, closure, providerReceipt: provider, appAttestation: app,
    }));
    if (intent && at(intent.expiresAt) > at(issued.expiresAt)) throw new Error("RECOVERY_INTENT_OUTLIVES_LEASE");
    if (provider && provider.finalProviderBytesSent <= 0) throw new Error("RECOVERY_PROVIDER_ZERO_BYTES");
    const timeline = gatewayChain.flatMap((entry) => [entry.registeredAt, entry.acceptedAt,
      entry.dispatchStartedAt, entry.cancelledAt, entry.settledAt]).filter(Boolean).map(at);
    if (timeline.some((time, index) => index > 0 && time < timeline[index - 1])) throw new Error("RECOVERY_TIME_ORDER");
    const latestLease = chain.at(-1);
    const latestGateway = gatewayChain.at(-1) ?? null;
    operations.push({ leaseId: issued.leaseId,
      authorizationEntrySha256: issued.authorizationEntrySha256,
      operationSubjectId: issued.operationSubjectId,
      operationType: issued.operationType,
      leaseEntrySha256: fullHash(latestLease), leasePhase: latestLease.phase,
      gatewayPhase: latestGateway?.phase ?? null, closureReason: closure?.closureReason ?? null,
      providerResult: provider?.result ?? null, terminalPhase: null,
      state: deriveRecoveryOperationStateCore({ leasePhase: latestLease.phase,
        gatewayPhase: latestGateway?.phase ?? null, closureReason: closure?.closureReason ?? null,
        providerResult: provider?.result ?? null, terminalPhase: null }) });
  }
  return { errors: [], operations, verifiedAt: verificationTime };
}
```

The chronological tests then assert every fixed five-second edge and the full
ordering string in §6.3, one adjacent pair at a time; changing either endpoint
by 1 ms must fail. This keeps the code above readable without making any
ordering edge optional.

```js
// recovery-verifier.mjs
import { fullArtifactSha256, verifyEd25519 } from "./crypto.mjs";
import { readProductionAuthorityContext } from "./production-authority-context.mjs";
import { verifyGovernanceNoncePrefix } from "./nonce-replay.mjs";
import { verifyTransparencyBundle } from "./transparency-verifier.mjs";
import { verifyRecoveryFullPrefixCore } from "./recovery-verifier-internal.mjs";
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
    throw new Error("RECOVERY_AUTHORITY_BUNDLE_MISMATCH");
  }
  if (fullArtifactSha256(externalPins) !== authorityClaims.externalPinsSha256
    || verificationTime !== authorityClaims.trustedTime.now
    || noncePrefixSha256 !== authorityClaims.noncePrefixSha256
    || artifactSetSha256 !== authorityClaims.artifactSetSha256) {
    throw new Error("RECOVERY_AUTHORITY_INPUT_MISMATCH");
  }
  return true;
};
export function verifyRecoveryFullPrefix({ bundle, artifacts, nonceArtifacts,
  verificationInputs, authorityContext = null }) {
  const externalPins = verificationInputs?.externalPins;
  const verificationTime = verificationInputs?.verificationTime;
  const transparencyReplay = verifyTransparencyBundle({ bundle,
    externalPins, verificationTime });
  const nonceReplay = verifyGovernanceNoncePrefix({ artifacts: nonceArtifacts });
  if (!nonceReplay.cryptographicValid || nonceReplay.testOnly) {
    throw new Error("RECOVERY_NONCE_PREFIX_INVALID");
  }
  const core = verifyRecoveryFullPrefixCore({ bundle, artifacts, externalPins,
    verificationTime, transparencyReplay },
    { verifySignature: verifyEd25519 });
  const gateAuthorized = gateAuthorityMatches({ authorityContext, bundle, externalPins,
    verificationTime, noncePrefixSha256: nonceReplay.noncePrefixSha256,
    artifactSetSha256: nonceReplay.artifactSetSha256 });
  const result = Object.freeze({ ...core, testOnly: false, cryptographicValid: true,
    semanticValid: core.errors.length === 0,
    authorityRequired: gateAuthorized ? [] : ["production-authority-context"],
    gateEffective: gateAuthorized && core.errors.length === 0 });
  productionResults.add(result);
  return result;
}
export function isProductionRecoveryResult(value) {
  return productionResults.has(value) && value.cryptographicValid === true
    && value.semanticValid === true && value.testOnly === false;
}
export function deriveRecoveryOperationState({ verifiedReplay, leaseId }) {
  if (!productionResults.has(verifiedReplay) || !verifiedReplay.gateEffective) {
    throw new TypeError("unverified recovery replay");
  }
  const operation = verifiedReplay.operations.find((item) => item.leaseId === leaseId);
  if (!operation) throw new RangeError(`unknown lease ${leaseId}`);
  return operation.state;
}
```

- [ ] **Step 6: Integrate the four recovery-control log entry kinds**

Register `recovery-operation-lease`, `recovery-write-ahead-receipt`,
`recovery-idempotency-tombstone`, and `recovery-egress-intent` as log entries;
Closure, Provider Receipt, and App Attestation remain separately signed
artifacts referenced by full hash. The terminal TCB entry is a distinct,
already-listed kind delegated to Plan 08; no fifth recovery kind and no new
unlisted `entryKind` is invented.

- [ ] **Step 7: Run Plan 07 gates**

```powershell
node --test scripts/governance/recovery-provider-request.test.mjs scripts/governance/recovery-verifier.test.mjs scripts/governance/transparency-verifier.test.mjs scripts/governance-contract.test.mjs
npm run check:canon
npm run typecheck:governance
npm run typecheck
npm run lint
git diff --check
```

Expected: all local recovery/transparency tests and static gates pass; no remote
request occurs; live recovery remains an authority stop.

- [ ] **Step 8: Commit Plan 07 integration**

```powershell
git add scripts/fixtures/governance/recovery/state-cross-product.json scripts/governance/recovery-verifier-internal.mjs scripts/governance/recovery-verifier.mjs scripts/governance/transparency-verifier.mjs scripts/governance/nonce-replay.mjs scripts/governance/nonce-replay.test.mjs scripts/governance-contract.mjs scripts/governance-contract.test.mjs
git commit -m "feat: integrate recovery write-path replay"
```

## Plan 07 acceptance evidence

- All seven closed schemas reject added, missing, partial, or mistyped fields.
- Every Lease/Gateway/Tombstone/Intent/Closure/Provider/App transition is full-prefix and checkpoint bound.
- Gateway payload core and common log entry core are independently golden-tested.
- Tombstone prevents replay after failure, completion, marker loss, or A→B→A OID history.
- Exact two-update GitHub CAS request is validated from bytes without network access.
- Direct App/Gateway/host Egress, retransmission, fork, and zero-byte substitution fail closed.
- Unknown provider outcome remains executing; no manual or automatic unlock exists.
- Production verification cannot accept injected signature or transparency verification.
- Production base verification uses real signatures and the exact complete Plan-06 Nonce-prefix but remains authority-red; only Plan-11-minted `gate-evaluation` claims can derive a gate-effective result, without an issuer cycle.
- No credential, key, signature, marker, network namespace, remote request, or server change is created.
