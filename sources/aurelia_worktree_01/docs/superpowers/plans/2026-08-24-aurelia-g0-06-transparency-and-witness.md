# AURELIA G0 Transparency and Witness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement deterministic offline replay of AURELIA's append-only transparency log, RFC-6962 Merkle checkpoints, witness floors, policy epochs, key transitions, equivocation reports, and custodian-pin transitions.

**Architecture:** Every external control entry is first validated against its closed payload schema, then against one common log-entry envelope, hash chain, active instance-key epoch, and checkpoint chain. A full-prefix verifier recomputes every leaf, Merkle root, floor, and active-state transition; it never trusts supplied inclusion or consistency proofs. Live freshness and signatures require external pins and are explicit authority stops when absent.

**Tech Stack:** Node.js 22 ESM, `node:crypto`, Draft-2020-12 schema registry, RFC 8785 core from Plan 05, RFC 6962 Merkle hashing, Ed25519 verification, Node test runner.

---

## Prerequisites and non-goals

Plan 05 must be green. This plan does not deploy a log, contact a witness,
create an external pin, sign a checkpoint, rotate a key, or update a remote.
It only implements schemas, pure state derivation, golden vectors, and
fail-closed offline validation.

## File map

**Create:**

- `scripts/governance/rfc6962.mjs`
- `scripts/governance/rfc6962.test.mjs`
- `scripts/governance/transparency-verifier-internal.mjs`
- `scripts/governance/transparency-verifier.mjs`
- `scripts/governance/transparency-verifier.test.mjs`
- `scripts/governance/nonce-replay.mjs`
- `scripts/governance/nonce-replay.test.mjs`
- `scripts/governance/production-authority-context.mjs`
- `scripts/governance/production-authority-context.test.mjs`
- `scripts/governance/schema-builders/transparency.mjs`
- `scripts/fixtures/governance/rfc6962/golden.json`
- `scripts/fixtures/governance/transparency/valid-prefix.json`
- `scripts/fixtures/governance/transparency/mutations.json`
- `docs/governance/schemas/acceptance-receipt.schema.json`
- `docs/governance/schemas/branch-policy-transition.schema.json`
- `docs/governance/schemas/transparency-checkpoint.schema.json`
- `docs/governance/schemas/transparency-bundle.schema.json`
- `docs/governance/schemas/transparency-key-transition.schema.json`
- `docs/governance/schemas/transparency-equivocation-report.schema.json`
- `docs/governance/schemas/transparency-witness-floor.schema.json`
- `docs/governance/schemas/custodian-pin-transition.schema.json`

**Modify:**

- `scripts/governance-contract.mjs`
- `scripts/governance-contract.test.mjs`

## Stable exports

```js
// Interface contracts only; Tasks 1–3 contain the complete implementations.
// scripts/governance/rfc6962.mjs
export function leafHash(canonicalEntryBytes) {}
export function nodeHash(left, right) {}
export function merkleRootFromEntries(entries) {}

// scripts/governance/transparency-verifier.mjs
export function verifyTransparencyBundle({ bundle, externalPins, verificationTime }) {}
export function deriveCryptographicallyVerifiedTransparencyState(verifiedReplay) {}
export function verifyFreshWitnessFloors({ bundle, externalPins, now, challenge }) {}
export function verifyGovernanceNoncePrefix({ artifacts }) {}
export function readProductionAuthorityContext(value) {}
```

`verifyTransparencyBundle` returns `{ errors, state, authorityRequired }`.
`state` contains `lastLogIndex`, `lastEntrySha256`, `latestCheckpointSha256`,
`activeInstanceKeyRef`, `instanceKeyEpoch`, `branchPolicyByBranch`,
`activeTcbState`, `custodianPins`, `consumedPromotionRequests`, and
`equivocationDetected`.

The public production module always supplies Plan 05's `verifyEd25519` to the
internal core. Only `transparency-verifier.test.mjs` may import the internal
module with a semantic signature test double. Every internal/test-double result
is marked `testOnly: true` and `gateEffective: false`; the CLI rejects such a
result even if every semantic check passes. A source allowlist test forbids any
other import of `transparency-verifier-internal.mjs`.

The Plan-06 production wrapper proves only cryptographic/internal consistency
against the supplied public material. Because raw `externalPins` and
`verificationTime` are caller inputs, its output is module-branded as
`cryptographicValid` but always has `gateEffective:false` and
`authorityRequired:["production-authority-context"]` until Plan 11 verifies
the independently signed pin set, Trusted-Time attestation, live challenge,
branch controls, and Acceptance-Receipt chain together. Only Plan 11 may mint
the separate module-private `ProductionAuthorityContext`; no Plan-06 export
accepts a caller-created boolean or string hook as a substitute.

`deriveCryptographicallyVerifiedTransparencyState` accepts only the branded,
cryptographically valid Plan-06 result, not an arbitrary bundle. This state is
safe as an input to further verification but is not independently gate-effective.

### Task 1: Lock RFC-6962 leaf and node hashing

**Files:**

- Create: `scripts/fixtures/governance/rfc6962/golden.json`
- Create: `scripts/governance/rfc6962.test.mjs`
- Create: `scripts/governance/rfc6962.mjs`

- [ ] **Step 1: Add independent RFC-6962 golden hashes**

```json
{
  "emptyTreeSha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "emptyLeafSha256": "6e340b9cffb37a989ca544e6bb780a2c78901d3fb33738768511a30617afa01d",
  "twoEmptyLeavesSha256": "fe43d66afa4a9a5c4f9c9da89f4ffb52635c8f342e7ffb731d68e36c5982072a"
}
```

- [ ] **Step 2: Write RED tests for domain separation**

```js
test("RFC 6962 domain separation matches golden vectors", () => {
  assert.equal(sha256Hex(Buffer.alloc(0)), fixture.emptyTreeSha256);
  const leaf = leafHash(Buffer.alloc(0));
  assert.equal(leaf.toString("hex"), fixture.emptyLeafSha256);
  assert.equal(nodeHash(leaf, leaf).toString("hex"), fixture.twoEmptyLeavesSha256);
});

test("leaf and node domains are not interchangeable", () => {
  const leaf = leafHash(Buffer.from("x"));
  assert.notEqual(leaf.toString("hex"), nodeHash(leaf, leaf).toString("hex"));
});
```

- [ ] **Step 3: Run and confirm RED**

Run `node --test scripts/governance/rfc6962.test.mjs`.
Expected: FAIL with missing `rfc6962.mjs`.

- [ ] **Step 4: Implement RFC-6962 hashing and odd-node recursion**

```js
import { createHash } from "node:crypto";
import { canonicalBytes } from "./rfc8785.mjs";

const digest = (bytes) => createHash("sha256").update(bytes).digest();
export const leafHash = (bytes) => digest(Buffer.concat([Buffer.from([0]), Buffer.from(bytes)]));
export const nodeHash = (left, right) => digest(Buffer.concat([Buffer.from([1]), left, right]));

function largestPowerOfTwoBelow(n) {
  if (!Number.isSafeInteger(n) || n < 2) throw new RangeError("invalid RFC-6962 tree size");
  let k = 1;
  while (k * 2 < n) k *= 2;
  return k;
}

function root(leaves) {
  if (leaves.length === 0) return digest(Buffer.alloc(0));
  if (leaves.length === 1) return leaves[0];
  const k = largestPowerOfTwoBelow(leaves.length);
  return nodeHash(root(leaves.slice(0, k)), root(leaves.slice(k)));
}

export function merkleRootFromEntries(entries) {
  if (!Array.isArray(entries) || !Number.isSafeInteger(entries.length)) {
    throw new RangeError("invalid RFC-6962 entry count");
  }
  return root(entries.map((entry) => leafHash(canonicalBytes(entry))));
}
```

- [ ] **Step 5: Add size-boundary and 1-, 2-, 3-, and 5-leaf mutation tests**

For each size, reorder one entry, omit the last entry, duplicate index 0, and
change one payload byte. Every root must differ from the golden root for the
unaltered ordered array. Test the arithmetic helper without allocating arrays:
`largestPowerOfTwoBelow(2_147_483_649) == 2_147_483_648`,
`largestPowerOfTwoBelow(Number.MAX_SAFE_INTEGER) == 4_503_599_627_370_496`,
and unsafe, fractional, zero, or negative sizes throw. No bitwise operator is
permitted in the implementation.

- [ ] **Step 6: Run and confirm GREEN**

Expected: all RFC-6962 tests pass.

- [ ] **Step 7: Commit the Merkle primitive**

```powershell
git add scripts/governance/rfc6962.mjs scripts/governance/rfc6962.test.mjs scripts/fixtures/governance/rfc6962/golden.json
git commit -m "feat: add RFC 6962 transparency hashing"
```

### Task 2: Define common log entries, acceptance receipts, and branch-policy epochs

**Files:**

- Create: `docs/governance/schemas/acceptance-receipt.schema.json`
- Create: `docs/governance/schemas/branch-policy-transition.schema.json`
- Create: `scripts/governance/schema-builders/transparency.mjs`
- Create: `scripts/governance/transparency-verifier.test.mjs`
- Create: `scripts/governance/transparency-verifier-internal.mjs`
- Create: `scripts/governance/transparency-verifier.mjs`

- [ ] **Step 1: Write common-entry and payload schema tests**

The common envelope has exactly `schemaVersion`, `entryKind`, `repositoryId`,
`logId`, `transparencyLogIndex`, `previousLogEntrySha256`, `loggedAt`,
`instanceKeyRef`, `instanceKeyEpoch`, `method`, `entryCoreSha256`, and
`instanceSignature`, plus the exact entry-kind payload fields at top level.
Test index 0/null predecessor, index 1/full predecessor hash, wrong repository,
unknown entry kind, payload-only hash used as entry hash, and an extra property.
Mutate `instanceSignature.keyRef` independently of `instanceKeyRef`, replace
its nonce with a padded/noncanonical or 31-byte value, reuse that nonce in a
later entry/checkpoint/witness/recovery signature, and set `signedAt` one
millisecond after `loggedAt`; require the dedicated fail-closed rules. The
positive fixture proves `signature.keyRef === instanceKeyRef ===` the active
externally supplied instance pin and signs the exact `entryCoreSha256`.

- [ ] **Step 2: Run and confirm RED**

Expected: missing schemas and verifier fail.

- [ ] **Step 3: Implement the complete closed schema builder**

Create `scripts/governance/schema-builders/transparency.mjs` with this complete
core. These are payload-plus-common-envelope schemas for log entries and
standalone schemas for checkpoints, bundles, floors, and reports; no field is
implicitly admitted.

```js
import { mkdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

const DRAFT = "https://json-schema.org/draft/2020-12/schema";
const V = { const: "aurelia-governance-v1" };
const REPO = { const: "redshift-three67/aurelia" };
const TEXT = { type: "string", minLength: 1 };
const HEX = { type: "string", pattern: "^[0-9a-f]{64}$" };
const COMMIT = { type: "string", pattern: "^[0-9a-f]{40}$" };
const TIME = { type: "string", pattern: "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\\.[0-9]{3}Z$" };
const NONCE = { type: "string", pattern: "^[A-Za-z0-9_-]{43}$" };
const SIG = { type: "string", pattern: "^[A-Za-z0-9_-]{86}$" };
const UINT = { type: "integer", minimum: 0, maximum: 9007199254740991 };
const POS = { type: "integer", minimum: 1, maximum: 9007199254740991 };
const nullable = (schema) => ({ anyOf: [schema, { type: "null" }] });
const list = (items, minItems = 0) => ({ type: "array", items, minItems });
const closed = (properties) => ({
  type: "object", additionalProperties: false,
  required: Object.keys(properties), properties,
});
const top = (id, body) => ({ $schema: DRAFT, $id: id, ...body });

const instanceSignature = closed({
  keyRef: TEXT, signedAt: TIME, nonce: NONCE, entryCoreSha256: HEX, signature: SIG,
});
const checkpointInstanceSignature = closed({
  keyRef: TEXT, signedAt: TIME, nonce: NONCE,
  checkpointCoreSha256: HEX, signature: SIG,
});
const witnessSignature = closed({
  witnessId: TEXT, keyRef: TEXT, signedAt: TIME, nonce: NONCE,
  checkpointCoreSha256: HEX, signature: SIG,
});
const recoveryCheckpointSignature = closed({
  purpose: { enum: ["operator", "recovery-root", "validator-controller", "custodian-a", "custodian-b"] },
  signerRole: TEXT, signerIdentity: TEXT, keyRef: TEXT, signedAt: TIME,
  nonce: NONCE, checkpointCoreSha256: HEX, signature: SIG,
});
const commonEntry = (entryKind) => ({
  schemaVersion: V, entryKind: { const: entryKind }, repositoryId: REPO,
  logId: TEXT, transparencyLogIndex: UINT, previousLogEntrySha256: nullable(HEX),
  loggedAt: TIME, instanceKeyRef: TEXT, instanceKeyEpoch: POS,
  method: { const: "ed25519" }, entryCoreSha256: HEX,
  instanceSignature: nullable(instanceSignature),
});
const entry = (id, kind, payload) => top(id, closed({ ...commonEntry(kind), ...payload }));

const eventAttestation = closed({
  attestationPurpose: TEXT, keyRef: TEXT, envelopeSha256: HEX, nonceSha256: HEX,
});
const acceptedEvent = closed({
  eventId: { type: "string", pattern: "^EVT-[0-9]{6}$" },
  eventSha256: HEX, attestations: list(eventAttestation, 1),
});
const acceptanceReceipt = entry(
  "https://aurelia.invalid/schemas/acceptance-receipt.schema.json",
  "acceptance-receipt", {
    receiptId: { type: "string", pattern: "^RECEIPT-[0-9]{12}$" },
    branch: TEXT, headCommit: COMMIT, headTreeOid: COMMIT,
    events: list(acceptedEvent, 1), validatorImageDigest: { type: "string", pattern: "^sha256:[0-9a-f]{64}$" },
    validatorPolicySha256: HEX, workflowSha256: HEX, schemaSetSha256: HEX,
    trustProtocolSha256: HEX, tcbStateEpoch: POS,
    tcbStateEntryId: nullable(TEXT), tcbStateEntrySha256: nullable(HEX),
    branchRulesSha256: HEX, branchPolicyEpoch: POS, acceptedAt: TIME,
    oidcIssuer: TEXT, oidcAudience: TEXT, oidcSubject: TEXT, runId: TEXT,
  },
);
const branchPolicyTransition = entry(
  "https://aurelia.invalid/schemas/branch-policy-transition.schema.json",
  "branch-policy-transition", {
    policyTransitionId: { type: "string", pattern: "^POLICYTRANS-[0-9]{12}$" },
    branch: TEXT, observedHeadCommit: COMMIT, previousBranchRulesSha256: HEX,
    observedBranchRulesSha256: HEX, previousBranchPolicyEpoch: POS,
    branchPolicyEpoch: POS, invalidatesThroughLogIndex: UINT,
    reason: TEXT, observedAt: TIME,
  },
);

const checkpointCoreProperties = {
  schemaVersion: V, repositoryId: REPO, logId: TEXT,
  checkpointKind: { enum: ["regular", "key-recovery-floor"] },
  treeSize: POS, rootSha256: HEX, issuedAt: TIME,
  previousCheckpointSha256: nullable(HEX), instanceKeyRef: TEXT,
  instanceKeyEpoch: POS, keyTransitionSha256: nullable(HEX),
  method: { const: "ed25519" },
};
const transparencyCheckpoint = top(
  "https://aurelia.invalid/schemas/transparency-checkpoint.schema.json",
  closed({ ...checkpointCoreProperties, checkpointCoreSha256: HEX,
    instanceSignature: nullable(checkpointInstanceSignature),
    recoveryAuthorizationSignatures: list(recoveryCheckpointSignature),
    witnessSignatures: list(witnessSignature, 1),
  }),
);
const transparencyWitnessFloor = top(
  "https://aurelia.invalid/schemas/transparency-witness-floor.schema.json",
  closed({ schemaVersion: V, repositoryId: REPO,
    floorId: { type: "string", pattern: "^WFLOOR-[0-9]{12}$" }, logId: TEXT,
    witnessId: TEXT, keyRef: TEXT, minimumTreeSize: POS,
    minimumCheckpointSha256: HEX, instanceKeyEpoch: POS, observedAt: TIME,
    previousFloorSha256: nullable(HEX), nonce: NONCE, signature: SIG,
  }),
);
const transparencyBundle = top(
  "https://aurelia.invalid/schemas/transparency-bundle.schema.json",
  closed({ schemaVersion: V, repositoryId: REPO,
    entries: list({ oneOf: [
      "acceptance-receipt", "branch-policy-transition", "validator-activation",
      "validator-rollback-record", "emergency-tcb-recovery",
      "recovery-operation-lease", "recovery-write-ahead-receipt",
      "recovery-idempotency-tombstone", "recovery-egress-intent",
      "transparency-key-transition", "external-model-request-receipt",
      "custodian-pin-transition",
    ].map((name) => ({ $ref: `${name}.schema.json` })) }),
    checkpoints: list({ $ref: "transparency-checkpoint.schema.json" }, 1),
    witnessFloors: list({ $ref: "transparency-witness-floor.schema.json" }, 1),
  }),
);

const transitionRoleSignature = closed({
  purpose: { enum: ["operator", "recovery-root", "validator-controller", "custodian-a", "custodian-b"] },
  signerRole: TEXT, signerIdentity: TEXT, keyRef: TEXT, signedAt: TIME,
  nonce: NONCE, transitionCoreSha256: HEX, signature: SIG,
});
const transitionWitnessSignature = closed({
  purpose: { const: "witness" }, witnessId: TEXT, keyRef: TEXT, signedAt: TIME,
  nonce: NONCE, transitionCoreSha256: HEX, signature: SIG,
});
const transparencyKeyTransition = entry(
  "https://aurelia.invalid/schemas/transparency-key-transition.schema.json",
  "transparency-key-transition", {
    transitionId: { type: "string", pattern: "^KEYTRANS-[0-9]{12}$" },
    transitionReason: { enum: ["rotation", "compromise", "loss"] },
    fromKeyRef: TEXT, fromKeyEpoch: POS, fromKeyFingerprint: HEX,
    toKey: closed({ keyRef: TEXT, keyEpoch: POS, algorithm: { const: "ed25519" },
      publicKeyBase64url: { type: "string", pattern: "^[A-Za-z0-9_-]{43}$" }, fingerprintSha256: HEX }),
    lastCheckpointSha256: HEX, lastTreeSize: POS, lastRootSha256: HEX,
    activationMode: { const: "after-witness-floor" }, transitionCoreSha256: HEX,
    authorizationSignatures: list({ oneOf: [transitionRoleSignature, transitionWitnessSignature] }, 2),
  },
);

const proposal = closed({
  checkpointCore: closed(checkpointCoreProperties), checkpointCoreSha256: HEX,
  instanceSignature: checkpointInstanceSignature,
  witnessSignatures: list(witnessSignature),
});
const transparencyEquivocationReport = top(
  "https://aurelia.invalid/schemas/transparency-equivocation-report.schema.json",
  closed({ schemaVersion: V, repositoryId: REPO,
    reportId: { type: "string", pattern: "^EQUIV-[0-9]{12}$" }, logId: TEXT,
    witnessId: TEXT, witnessKeyRef: TEXT,
    reason: { enum: ["same-size-different-root", "decreasing-tree-size", "inconsistent-successor"] },
    firstProposal: proposal, secondProposal: proposal,
    previousWitnessObservationSha256: nullable(HEX), observedAt: TIME,
    nonce: NONCE, reportCoreSha256: HEX, signature: SIG,
  }),
);

const pinSignature = closed({
  purpose: { enum: ["operator", "recovery-root", "custodian-a", "custodian-b", "incoming-custodian-a", "incoming-custodian-b"] },
  signerRole: TEXT, signerIdentity: TEXT, keyRef: TEXT, signedAt: TIME,
  nonce: NONCE, pinTransitionCoreSha256: HEX, signature: SIG,
});
const custodianPinTransition = entry(
  "https://aurelia.invalid/schemas/custodian-pin-transition.schema.json",
  "custodian-pin-transition", {
    pinTransitionId: { type: "string", pattern: "^PINTRANS-[0-9]{12}$" },
    custodianRole: { enum: ["ROLE-RECOVERY-CUSTODIAN-A", "ROLE-RECOVERY-CUSTODIAN-B"] },
    transitionKind: { enum: ["initial-assignment", "rotation"] },
    previousPinEpoch: UINT, pinEpoch: POS, previousAssigneeRef: nullable(TEXT),
    previousKeyRef: nullable(TEXT), previousKeyFingerprint: nullable(HEX),
    nextAssigneeRef: TEXT, nextKeyRef: TEXT, nextKeyFingerprint: HEX,
    roleEventId: { type: "string", pattern: "^EVT-[0-9]{6}$" }, roleEventSha256: HEX,
    acceptanceReceiptId: { type: "string", pattern: "^RECEIPT-[0-9]{12}$" },
    headCommit: COMMIT, headTreeOid: COMMIT, effectiveAfterCheckpoint: { const: true },
    pinTransitionCoreSha256: HEX, transitionSignatures: list(pinSignature, 3),
  },
);

export const transparencySchemas = {
  "acceptance-receipt.schema.json": acceptanceReceipt,
  "branch-policy-transition.schema.json": branchPolicyTransition,
  "transparency-checkpoint.schema.json": transparencyCheckpoint,
  "transparency-bundle.schema.json": transparencyBundle,
  "transparency-key-transition.schema.json": transparencyKeyTransition,
  "transparency-equivocation-report.schema.json": transparencyEquivocationReport,
  "transparency-witness-floor.schema.json": transparencyWitnessFloor,
  "custodian-pin-transition.schema.json": custodianPinTransition,
};
export async function writeTransparencySchemas(target = "docs/governance/schemas") {
  await mkdir(target, { recursive: true });
  for (const [name, schema] of Object.entries(transparencySchemas)) {
    await writeFile(resolve(target, name), `${JSON.stringify(schema, null, 2)}\n`, "utf8");
  }
}
```

Schema generation must be deterministic and followed by registration in the
Plan-02 registry. Semantic checks additionally enforce array sort/uniqueness,
bootstrap-nullability, exact threshold sets, core projections, epoch arithmetic,
and cross-artifact equality; JSON Schema cannot safely express those replay
invariants.

- [ ] **Step 4: Generate and test acceptance/policy schemas**

Run the builder, register all eight files, and assert that each exact valid
fixture passes while deleting every required field, adding one unknown field
at every nested level, changing each constant, or using the wrong primitive
type fails. For acceptance receipts also test sorted unique events and
attestations, and require null TCB state ID/hash iff epoch is 1. For policy
transitions enforce `branchPolicyEpoch == previousBranchPolicyEpoch + 1` and
`invalidatesThroughLogIndex == transparencyLogIndex - 1`.

- [ ] **Step 5: Implement common entry verification**

For each entry: validate the kind-specific schema; require its index to equal
the array position; compare predecessor hash to the full canonical signed
previous entry; recompute `entryCoreSha256` over all fields except itself and
`instanceSignature`; verify method/key/epoch; then verify the instance
signature. Allow `instanceSignature: null` only for the two recovery forms
explicitly authorized by §6.4.

Use this complete core shape in `transparency-verifier-internal.mjs`; later
tasks extend `applyEntry` without weakening these checks:

```js
import { canonicalBytes } from "./rfc8785.mjs";
import { assertBase64urlBytes, sha256Hex } from "./crypto.mjs";
import { validateSchema } from "./schema-registry.mjs";

const KIND_SCHEMA = new Map([
  ["acceptance-receipt", "acceptance-receipt"],
  ["branch-policy-transition", "branch-policy-transition"],
  ["tcb-activation", "validator-activation"],
  ["tcb-rollback", "validator-rollback-record"],
  ["tcb-emergency-recovery", "emergency-tcb-recovery"],
  ["recovery-operation-lease", "recovery-operation-lease"],
  ["recovery-write-ahead-receipt", "recovery-write-ahead-receipt"],
  ["recovery-idempotency-tombstone", "recovery-idempotency-tombstone"],
  ["recovery-egress-intent", "recovery-egress-intent"],
  ["transparency-key-transition", "transparency-key-transition"],
  ["external-model-request-receipt", "external-model-request-receipt"],
  ["custodian-pin-transition", "custodian-pin-transition"],
]);
const without = (value, names) => Object.fromEntries(
  Object.entries(value).filter(([name]) => !names.includes(name)),
);
const fullHash = (value) => sha256Hex(canonicalBytes(value));
const push = (errors, rule, path, message) => errors.push({ rule, path, message });
const sortedUnique = (items, key) => items.every((item, index) => (
  index === 0 || key(items[index - 1]) < key(item)
));

function verifyInstanceSignature(entry, active, nonceSet, verifySignature, errors, path) {
  const sig = entry.instanceSignature;
  const recoveryTransition = entry.entryKind === "transparency-key-transition"
    && ["compromise", "loss"].includes(entry.transitionReason);
  if (sig === null) {
    if (!recoveryTransition) push(errors, "LOG_INSTANCE_SIGNATURE_REQUIRED", path, "null signature is not authorized");
    return;
  }
  if (recoveryTransition) push(errors, "LOG_RECOVERY_SIGNATURE_MUST_BE_NULL", path, "recovery transition cannot use instance trust");
  let nonceValid = true;
  try { assertBase64urlBytes(sig.nonce, 32, `${path}.instanceSignature.nonce`); }
  catch (error) {
    nonceValid = false;
    push(errors, "LOG_INSTANCE_NONCE_INVALID", `${path}.instanceSignature.nonce`, error.message);
  }
  const signedAt = Date.parse(sig.signedAt);
  const loggedAt = Date.parse(entry.loggedAt);
  if (entry.instanceKeyRef !== active.keyRef || entry.instanceKeyEpoch !== active.keyEpoch
    || sig.keyRef !== active.keyRef || sig.entryCoreSha256 !== entry.entryCoreSha256) {
    push(errors, "LOG_INSTANCE_EPOCH_MISMATCH", path, "entry does not use active instance key epoch");
    return;
  }
  if (!Number.isFinite(signedAt) || !Number.isFinite(loggedAt) || signedAt > loggedAt) {
    push(errors, "LOG_INSTANCE_SIGNATURE_TIME_INVALID", `${path}.instanceSignature.signedAt`, "instance signature must not postdate loggedAt");
  }
  if (nonceValid && nonceSet.has(sig.nonce)) {
    push(errors, "LOG_SIGNATURE_NONCE_REUSE", `${path}.instanceSignature.nonce`, "signature nonce is globally reused");
  } else if (nonceValid) nonceSet.add(sig.nonce);
  const ok = verifySignature({
    publicKeyBase64url: active.publicKeyBase64url,
    payloadBytes: canonicalBytes(without(entry, ["entryCoreSha256", "instanceSignature"])),
    signatureBase64url: sig.signature,
  });
  if (!ok) push(errors, "LOG_INSTANCE_SIGNATURE_INVALID", `${path}.instanceSignature.signature`, "Ed25519 verification failed");
}

function applyEntry(state, entry, fullEntrySha256, errors, path) {
  if (entry.entryKind === "branch-policy-transition") {
    const previous = state.branchPolicyByBranch.get(entry.branch);
    if (!previous || entry.previousBranchPolicyEpoch !== previous.epoch
      || entry.previousBranchRulesSha256 !== previous.rulesSha256
      || entry.branchPolicyEpoch !== previous.epoch + 1
      || entry.invalidatesThroughLogIndex !== entry.transparencyLogIndex - 1) {
      push(errors, "POLICY_TRANSITION_CHAIN_INVALID", path, "policy epoch/rules/invalidation edge is invalid");
    } else state.branchPolicyByBranch.set(entry.branch, {
      epoch: entry.branchPolicyEpoch, rulesSha256: entry.observedBranchRulesSha256,
      effectiveAt: entry.transparencyLogIndex,
    });
  }
  if (entry.entryKind === "acceptance-receipt") {
    const policy = state.branchPolicyByBranch.get(entry.branch);
    if (!policy || entry.branchPolicyEpoch !== policy.epoch
      || entry.branchRulesSha256 !== policy.rulesSha256) {
      push(errors, "RECEIPT_POLICY_EPOCH_INVALID", path, "receipt is not in the active branch-policy epoch");
    }
    if (!sortedUnique(entry.events, (event) => event.eventId)
      || entry.events.some((event) => !sortedUnique(event.attestations,
        (att) => `${att.attestationPurpose}\u0000${att.keyRef}`))) {
      push(errors, "RECEIPT_COLLECTION_ORDER_INVALID", `${path}.events`, "events/attestations must be sorted and unique");
    }
    const acceptedAt = Date.parse(entry.acceptedAt);
    const loggedAt = Date.parse(entry.loggedAt);
    if (!Number.isFinite(acceptedAt) || !Number.isFinite(loggedAt) || acceptedAt > loggedAt) {
      push(errors, "RECEIPT_ACCEPTANCE_TIME_INVALID", `${path}.acceptedAt`, "acceptedAt must be valid and no later than loggedAt");
    }
    for (const accepted of entry.events) {
      const event = state.eventById.get(accepted.eventId);
      if (!event || state.acceptedEventIds.has(accepted.eventId)
        || event.eventHash !== accepted.eventSha256) {
        push(errors, "RECEIPT_EVENT_FIRST_INCLUSION_INVALID", `${path}.events`,
          "receipt must bind each existing event exactly at its first acceptance");
        continue;
      }
      const expectedAttestations = event.authorizationAttestations.map((attestation) => ({
        attestationPurpose: attestation.attestationPurpose,
        keyRef: attestation.keyRef,
        envelopeSha256: attestation.envelopeSha256,
        nonceSha256: sha256Hex(Buffer.from(attestation.nonce, "base64url")),
      })).sort((left, right) => {
        const a = `${left.attestationPurpose}\u0000${left.keyRef}`;
        const b = `${right.attestationPurpose}\u0000${right.keyRef}`;
        return a < b ? -1 : a > b ? 1 : 0;
      });
      if (canonicalBytes(expectedAttestations).compare(canonicalBytes(accepted.attestations)) !== 0) {
        push(errors, "RECEIPT_ATTESTATION_SET_MISMATCH", `${path}.events`, "receipt attestation summaries are not byte-equal");
      }
      for (const attestation of event.authorizationAttestations) {
        const signedAt = Date.parse(attestation.signedAt);
        if (!Number.isFinite(signedAt) || signedAt < acceptedAt - 86_400_000
          || signedAt > acceptedAt + 300_000) {
          push(errors, "RECEIPT_NEW_EVENT_SIGNING_WINDOW", `${path}.events`,
            "first-included event signatures must be within acceptedAt -24h/+5m");
        }
      }
      state.acceptedEventIds.add(accepted.eventId);
    }
    state.receipts.push({ id: entry.receiptId, index: entry.transparencyLogIndex,
      policyEpoch: entry.branchPolicyEpoch, fullEntrySha256 });
  }
  state.lastLogIndex = entry.transparencyLogIndex;
  state.lastEntrySha256 = fullEntrySha256;
}

export function verifyLogPrefixCore({ entries, initialState, signatureNonces }, { verifySignature }) {
  const errors = [];
  const state = {
    ...initialState,
    branchPolicyByBranch: new Map(initialState.branchPolicyByBranch),
    eventById: new Map(initialState.eventById),
    acceptedEventIds: new Set(initialState.acceptedEventIds ?? []),
    receipts: [], lastLogIndex: -1, lastEntrySha256: null,
  };
  let predecessor = null;
  for (const [index, entry] of entries.entries()) {
    const path = `$.entries[${index}]`;
    const entryErrors = [];
    const schema = KIND_SCHEMA.get(entry?.entryKind);
    if (!schema) push(entryErrors, "LOG_ENTRY_KIND_UNKNOWN", `${path}.entryKind`, "entry kind is not closed");
    else for (const error of validateSchema(schema, entry)) entryErrors.push({ ...error, path: `${path}${error.path.slice(1)}` });
    if (schema && entry.transparencyLogIndex !== index) push(entryErrors, "LOG_INDEX_NOT_CONTIGUOUS", `${path}.transparencyLogIndex`, "index must equal array position");
    if (schema && entry.previousLogEntrySha256 !== predecessor) push(entryErrors, "LOG_PREDECESSOR_MISMATCH", `${path}.previousLogEntrySha256`, "wrong full-entry predecessor hash");
    let expectedCore = null;
    let entrySha256 = null;
    if (entryErrors.length === 0) {
      expectedCore = fullHash(without(entry, ["entryCoreSha256", "instanceSignature"]));
      if (entry.entryCoreSha256 !== expectedCore) push(entryErrors, "LOG_ENTRY_CORE_MISMATCH", `${path}.entryCoreSha256`, "wrong canonical entry core hash");
      if (entry.instanceSignature && entry.instanceSignature.entryCoreSha256 !== expectedCore) push(entryErrors, "LOG_SIGNATURE_CORE_MISMATCH", `${path}.instanceSignature.entryCoreSha256`, "signature binds another core");
      verifyInstanceSignature(entry, state.activeInstanceKey, signatureNonces, verifySignature, entryErrors, path);
      entrySha256 = fullHash(entry);
    }
    if (entryErrors.length === 0) {
      const candidate = { ...state,
        branchPolicyByBranch: new Map(state.branchPolicyByBranch),
        eventById: new Map(state.eventById),
        acceptedEventIds: new Set(state.acceptedEventIds),
        receipts: [...state.receipts] };
      applyEntry(candidate, entry, entrySha256, entryErrors, path);
      if (entryErrors.length === 0) Object.assign(state, candidate);
    }
    errors.push(...entryErrors);
    if (entrySha256 !== null) predecessor = entrySha256;
  }
  return { errors, state };
}
```

Plan 07 adds its four recovery entry cases and Plan 08 adds the three TCB cases
inside `applyEntry`; they reuse this one envelope/hash/signature loop. No later
plan may create another log verifier.

- [ ] **Step 6: Add policy invalidation replay tests**

Create three old-epoch receipts, one policy transition, and one new receipt.
Assert all three old receipts become non-gate-effective and never reactivate
after a byte-identical policy returns at a later epoch.

- [ ] **Step 7: Run and confirm GREEN**

Expected: ordered entries pass; all predecessor/index/core/policy mutations fail.

- [ ] **Step 8: Commit log and policy validation**

```powershell
git add docs/governance/schemas/acceptance-receipt.schema.json docs/governance/schemas/branch-policy-transition.schema.json scripts/governance/schema-builders/transparency.mjs scripts/governance/transparency-verifier-internal.mjs scripts/governance/transparency-verifier.mjs scripts/governance/transparency-verifier.test.mjs
git commit -m "feat: validate transparency log entries"
```

### Task 3: Validate checkpoints, full-prefix bundles, and witness floors

**Files:**

- Create: `docs/governance/schemas/transparency-checkpoint.schema.json`
- Create: `docs/governance/schemas/transparency-bundle.schema.json`
- Create: `docs/governance/schemas/transparency-witness-floor.schema.json`
- Create: `scripts/fixtures/governance/transparency/valid-prefix.json`
- Modify: `scripts/governance/transparency-verifier.mjs`
- Modify: `scripts/governance/transparency-verifier.test.mjs`

- [ ] **Step 1: Write RED tests for a three-entry full prefix**

Use fixed fixture times and injected `verifySignature: () => true`. Assert
indices exactly `0..treeSize-1`, recomputed Merkle roots for every checkpoint,
checkpoint predecessor hashes, all configured witness signatures, and each
witness's monotone floor chain.

Import the injected core only from the test. Assert its return value has
`testOnly: true` and `gateEffective: false`. Separately invoke the public
production wrapper with the unsigned fixture and assert real Ed25519
verification rejects it; passing an extra `verifySignature` property must not
change that result.

- [ ] **Step 2: Add stale/split-view mutations**

Delete entry 1, duplicate entry 2, alter a root, omit one witness, decrease a
floor size, change a floor's same-size checkpoint hash, make a live floor
larger than the bundle, and make the latest checkpoint 60 minutes plus 1 ms
old. Each must return a distinct deterministic rule code.

- [ ] **Step 3: Run and confirm RED**

Expected: missing checkpoint/bundle/floor schemas fail.

- [ ] **Step 4: Generate and exhaustively test all three closed schemas**

Checkpoint fields, signature arrays, `regular|key-recovery-floor`
discrimination, bundle top-level arrays, and witness-floor fields must exactly
match §6.4. `key-recovery-floor` alone permits null instance signature and
requires the full recovery threshold; `regular` requires the active instance
signature and empty recovery signatures.

- [ ] **Step 5: Implement full-prefix verification**

Recompute each checkpoint root from `entries.slice(0, treeSize)`, require
nondecreasing sizes, permit same size/root only across the first checkpoint of
a new key epoch, verify the complete checkpoint predecessor chain, and reject
any inclusion/consistency proof field as an unknown property.

Add this complete checkpoint/floor chain core beside the log-prefix core (the
helpers `fullHash`, `without`, `push`, and `sortedUnique` are the definitions
from Task 2):

```js
import { merkleRootFromEntries } from "./rfc6962.mjs";

function verifyDetached(publicKey, message, signature, verifySignature, errors, rule, path) {
  if (!publicKey || !verifySignature({ publicKeyBase64url: publicKey,
    payloadBytes: canonicalBytes(message), signatureBase64url: signature })) {
    push(errors, rule, path, "Ed25519 verification failed or public pin is absent");
  }
}
function verifyCheckpointSignatureRecord({ record, pin, core, coreSha256,
  issuedAt, nonceSet, verifySignature, errors, rule, path }) {
  let nonceValid = true;
  try { assertBase64urlBytes(record?.nonce, 32, `${path}.nonce`); }
  catch { nonceValid = false; }
  if (!record || !pin || record.keyRef !== pin.keyRef
    || record.checkpointCoreSha256 !== coreSha256
    || !nonceValid
    || nonceSet.has(record.nonce)
    || Date.parse(record.signedAt) > Date.parse(issuedAt)) {
    push(errors, `${rule}_RECORD_INVALID`, path,
      "keyRef, core digest, canonical unique nonce, and signature time must match");
    return;
  }
  nonceSet.add(record.nonce);
  verifyDetached(pin.publicKeyBase64url, core, record.signature, verifySignature,
    errors, rule, `${path}.signature`);
}

export function verifyCheckpointChainCore({ entries, checkpoints, witnessFloors, externalPins, now, signatureNonces }, { verifySignature }) {
  const errors = [];
  const authorityRequired = [];
  if (!externalPins?.instanceKeys || !externalPins?.witnessKeys) {
    authorityRequired.push("transparency-public-pins");
    return { errors, authorityRequired, latestCheckpointSha256: null };
  }
  let previous = null;
  let priorCheckpoint = null;
  for (const [index, checkpoint] of checkpoints.entries()) {
    const path = `$.checkpoints[${index}]`;
    for (const error of validateSchema("transparency-checkpoint", checkpoint)) {
      errors.push({ ...error, path: `${path}${error.path.slice(1)}` });
    }
    if (checkpoint.previousCheckpointSha256 !== previous) push(errors, "CHECKPOINT_PREDECESSOR_MISMATCH", `${path}.previousCheckpointSha256`, "checkpoint chain is broken");
    if (checkpoint.treeSize > entries.length) push(errors, "CHECKPOINT_TREE_SIZE_OUT_OF_RANGE", `${path}.treeSize`, "tree exceeds full prefix");
    else {
      const root = merkleRootFromEntries(entries.slice(0, checkpoint.treeSize)).toString("hex");
      if (root !== checkpoint.rootSha256) push(errors, "CHECKPOINT_ROOT_MISMATCH", `${path}.rootSha256`, "root does not match full prefix");
    }
    const core = without(checkpoint, ["checkpointCoreSha256", "instanceSignature", "recoveryAuthorizationSignatures", "witnessSignatures"]);
    const coreSha256 = fullHash(core);
    if (checkpoint.checkpointCoreSha256 !== coreSha256) push(errors, "CHECKPOINT_CORE_MISMATCH", `${path}.checkpointCoreSha256`, "wrong checkpoint core hash");
    if (priorCheckpoint) {
      if (checkpoint.treeSize < priorCheckpoint.treeSize) push(errors, "CHECKPOINT_SIZE_DECREASED", `${path}.treeSize`, "checkpoint size decreased");
      if (checkpoint.treeSize === priorCheckpoint.treeSize) {
        const legalEpochBridge = checkpoint.rootSha256 === priorCheckpoint.rootSha256
          && checkpoint.instanceKeyEpoch === priorCheckpoint.instanceKeyEpoch + 1
          && checkpoint.keyTransitionSha256 !== null;
        if (!legalEpochBridge) push(errors, "CHECKPOINT_SAME_SIZE_ILLEGAL", path, "same size is only legal at a key-epoch bridge");
      }
    }
    if (!sortedUnique(checkpoint.witnessSignatures, (sig) => `${sig.witnessId}\u0000${sig.keyRef}`)) push(errors, "CHECKPOINT_WITNESSES_NOT_SORTED", `${path}.witnessSignatures`, "witness signatures must be sorted and unique");
    const requiredWitnesses = Object.keys(externalPins.witnessKeys).sort();
    if (checkpoint.witnessSignatures.map((sig) => sig.witnessId).join("\u0000") !== requiredWitnesses.join("\u0000")) push(errors, "CHECKPOINT_WITNESS_SET_INCOMPLETE", `${path}.witnessSignatures`, "exact witness set required");
    for (const [sigIndex, sig] of checkpoint.witnessSignatures.entries()) {
      const pin = externalPins.witnessKeys[sig.witnessId];
      verifyCheckpointSignatureRecord({ record: sig, pin, core, coreSha256,
        issuedAt: checkpoint.issuedAt, nonceSet: signatureNonces, verifySignature,
        errors, rule: "CHECKPOINT_WITNESS_SIGNATURE_INVALID",
        path: `${path}.witnessSignatures[${sigIndex}]` });
    }
    if (checkpoint.checkpointKind === "regular") {
      if (checkpoint.instanceSignature === null || checkpoint.recoveryAuthorizationSignatures.length !== 0) push(errors, "CHECKPOINT_REGULAR_SIGNATURE_FORM_INVALID", path, "regular checkpoint signature form is invalid");
      else verifyCheckpointSignatureRecord({ record: checkpoint.instanceSignature,
        pin: externalPins.instanceKeys[checkpoint.instanceKeyEpoch], core, coreSha256,
        issuedAt: checkpoint.issuedAt, nonceSet: signatureNonces, verifySignature,
        errors, rule: "CHECKPOINT_INSTANCE_SIGNATURE_INVALID", path: `${path}.instanceSignature` });
    } else {
      if (checkpoint.instanceSignature !== null) push(errors, "CHECKPOINT_RECOVERY_INSTANCE_SIGNATURE_FORBIDDEN", `${path}.instanceSignature`, "recovery floor must not trust instance key");
      const requiredPurposes = [...(externalPins.pilotWasGreen ? ["custodian-a", "custodian-b"] : []),
        "operator", "recovery-root", "validator-controller"];
      const actualPurposes = checkpoint.recoveryAuthorizationSignatures.map((sig) => sig.purpose);
      if (!sortedUnique(checkpoint.recoveryAuthorizationSignatures,
        (sig) => `${sig.purpose}\u0000${sig.keyRef}`)
        || actualPurposes.join("\u0000") !== requiredPurposes.join("\u0000")) {
        push(errors, "CHECKPOINT_RECOVERY_THRESHOLD_INVALID", `${path}.recoveryAuthorizationSignatures`, "exact current recovery threshold required");
      }
      for (const sig of checkpoint.recoveryAuthorizationSignatures) {
        const pin = externalPins.recoveryRoles?.[sig.purpose];
        if (!pin || pin.keyRef !== sig.keyRef || pin.signerRole !== sig.signerRole
          || pin.signerIdentity !== sig.signerIdentity) push(errors, "CHECKPOINT_RECOVERY_PIN_MISMATCH", path, "recovery signer does not match active pin");
        else verifyCheckpointSignatureRecord({ record: sig, pin, core, coreSha256,
          issuedAt: checkpoint.issuedAt, nonceSet: signatureNonces, verifySignature,
          errors, rule: "CHECKPOINT_RECOVERY_SIGNATURE_INVALID",
          path: `${path}.recoveryAuthorizationSignatures` });
      }
    }
    previous = fullHash(checkpoint);
    priorCheckpoint = checkpoint;
  }
  if (checkpoints.length === 0 || checkpoints.at(-1).treeSize !== entries.length) push(errors, "BUNDLE_NOT_COMPLETE_PREFIX", "$.entries", "entries must end at latest checkpoint treeSize");

  const floorByWitness = new Map();
  for (const [index, floor] of witnessFloors.entries()) {
    const path = `$.witnessFloors[${index}]`;
    for (const error of validateSchema("transparency-witness-floor", floor)) errors.push({ ...error, path: `${path}${error.path.slice(1)}` });
    const prior = floorByWitness.get(floor.witnessId);
    if ((prior && floor.previousFloorSha256 !== fullHash(prior)) || (!prior && floor.previousFloorSha256 !== null)) push(errors, "WITNESS_FLOOR_PREDECESSOR_MISMATCH", `${path}.previousFloorSha256`, "witness floor chain is broken");
    if (prior && (floor.minimumTreeSize < prior.minimumTreeSize || floor.instanceKeyEpoch < prior.instanceKeyEpoch)) push(errors, "WITNESS_FLOOR_DECREASED", path, "witness floor is not monotone");
    if (prior && floor.minimumTreeSize === prior.minimumTreeSize
      && floor.minimumCheckpointSha256 !== prior.minimumCheckpointSha256) {
      push(errors, "WITNESS_FLOOR_EQUIVOCATION", path, "same-size floor changed checkpoint hash");
    }
    let floorNonceValid = true;
    try { assertBase64urlBytes(floor.nonce, 32, `${path}.nonce`); }
    catch { floorNonceValid = false; }
    if (!floorNonceValid || signatureNonces.has(floor.nonce)) {
      push(errors, "WITNESS_FLOOR_NONCE_INVALID", `${path}.nonce`, "floor nonce must be canonical and globally unique");
    } else signatureNonces.add(floor.nonce);
    verifyDetached(externalPins.witnessKeys[floor.witnessId]?.publicKeyBase64url,
      without(floor, ["signature"]), floor.signature, verifySignature,
      errors, "WITNESS_FLOOR_SIGNATURE_INVALID", `${path}.signature`);
    floorByWitness.set(floor.witnessId, floor);
  }
  const latest = checkpoints.at(-1);
  const evaluatedAt = Date.parse(now);
  const checkpointAt = latest ? Date.parse(latest.issuedAt) : Number.NaN;
  if (!Number.isFinite(evaluatedAt) || !Number.isFinite(checkpointAt)
    || checkpointAt > evaluatedAt || evaluatedAt - checkpointAt > 60 * 60 * 1000) {
    push(errors, "CHECKPOINT_NOT_FRESH", "$.checkpoints", "latest checkpoint must be no older than one hour and not future-dated");
  }
  for (const witnessId of Object.keys(externalPins.witnessKeys)) {
    const floor = floorByWitness.get(witnessId);
    if (!floor) push(errors, "WITNESS_FLOOR_MISSING", "$.witnessFloors", `missing ${witnessId}`);
    else if (floor.minimumTreeSize > latest.treeSize
      || (floor.minimumTreeSize === latest.treeSize && floor.minimumCheckpointSha256 !== fullHash(latest))) {
      push(errors, "WITNESS_FLOOR_SPLIT_OR_STALE", "$.witnessFloors", `floor mismatch for ${witnessId}`);
    }
  }
  return { errors, authorityRequired, latestCheckpointSha256: latest ? fullHash(latest) : null };
}
```

The threshold-purpose equality for `key-recovery-floor` is implemented in
Task 4 after Pilot-Green history is available; this function already forbids
an instance signature and verifies every witness.

- [ ] **Step 6: Implement floor freshness as an external-input boundary**

`verifyFreshWitnessFloors` must require one challenge-fresh response per
externally pinned witness for live gate evaluation. An exported historical
floor can prove history but cannot prove live freshness. Missing live responses
return `authorityRequired: ["live-witness-floors"]`.

Keep injection out of the production export. The internal file exports the
two explicitly separated entry points below; its allowlist permits imports
only from `transparency-verifier.mjs` and
`transparency-verifier.test.mjs`:

```js
export function verifyTransparencyBundleCore(args, { verifySignature }) {
  const signatureNonces = new Set();
  const log = verifyLogPrefixCore({ entries: args.bundle.entries,
    initialState: args.externalPins.initialState, signatureNonces }, { verifySignature });
  const chain = verifyCheckpointChainCore({ ...args.bundle,
    externalPins: args.externalPins, now: args.now, signatureNonces }, { verifySignature });
  return { errors: [...log.errors, ...chain.errors], state: log.state,
    authorityRequired: chain.authorityRequired };
}
export function verifyTransparencyBundleForSemanticTest(args, { verifySignature }) {
  const result = verifyTransparencyBundleCore(args, { verifySignature });
  return { ...result, testOnly: true, gateEffective: false };
}
```

The production facade is exactly:

```js
import { sha256Hex, verifyEd25519 } from "./crypto.mjs";
import { canonicalBytes } from "./rfc8785.mjs";
import { verifyTransparencyBundleCore } from "./transparency-verifier-internal.mjs";

const cryptographicallyVerifiedResults = new WeakSet();
const without = (value, names) => Object.fromEntries(
  Object.entries(value).filter(([name]) => !names.includes(name)),
);
export function verifyTransparencyBundle({ bundle, externalPins, verificationTime }) {
  const result = verifyTransparencyBundleCore({ bundle, externalPins, now: verificationTime },
    { verifySignature: verifyEd25519 });
  const cryptographicValid = result.errors.length === 0
    && result.authorityRequired.filter((item) => item !== "production-authority-context").length === 0;
  const output = { ...result, cryptographicValid, testOnly: false,
    gateEffective: false,
    authorityRequired: [...new Set([...result.authorityRequired, "production-authority-context"])].sort() };
  if (cryptographicValid) cryptographicallyVerifiedResults.add(output);
  return output;
}
export function deriveCryptographicallyVerifiedTransparencyState(verifiedReplay) {
  if (!cryptographicallyVerifiedResults.has(verifiedReplay) || !verifiedReplay.cryptographicValid) {
    throw new TypeError("state requires a cryptographically verified Plan-06 replay");
  }
  return verifiedReplay.state;
}
export function verifyFreshWitnessFloors({ bundle, externalPins, now, challenge }) {
  if (!challenge || !Array.isArray(challenge.responses)
    || !/^[A-Za-z0-9_-]{43}$/.test(challenge.nonce)) {
    return { errors: [], authorityRequired: ["live-witness-floors"], gateEffective: false };
  }
  const required = Object.keys(externalPins.witnessKeys).sort();
  const received = challenge.responses.map((item) => item.witnessId).sort();
  if (required.join("\u0000") !== received.join("\u0000")) {
    return { errors: [{ rule: "LIVE_WITNESS_SET_INCOMPLETE", path: "$.challenge.responses",
      message: "one response per externally pinned witness is required" }],
      authorityRequired: [], gateEffective: false };
  }
  const historical = verifyTransparencyBundle({ bundle, externalPins, verificationTime: now });
  if (!historical.cryptographicValid) return { errors: historical.errors,
    authorityRequired: historical.authorityRequired, challengeFresh: false, gateEffective: false };
  const requestedAt = Date.parse(challenge.requestedAt);
  const evaluatedAt = Date.parse(now);
  const errors = [];
  if (!Number.isFinite(requestedAt) || !Number.isFinite(evaluatedAt)
    || requestedAt > evaluatedAt || evaluatedAt - requestedAt > 60 * 60 * 1000) {
    errors.push({ rule: "LIVE_WITNESS_CHALLENGE_STALE", path: "$.challenge.requestedAt",
      message: "challenge must be no older than one hour" });
  }
  const latestCheckpoint = bundle.checkpoints.at(-1);
  const latestCheckpointSha256 = sha256Hex(canonicalBytes(latestCheckpoint));
  const historicalByWitness = new Map();
  for (const floor of bundle.witnessFloors) historicalByWitness.set(floor.witnessId, floor);
  for (const [index, response] of challenge.responses.entries()) {
    const observed = Date.parse(response.floor.observedAt);
    const respondedAt = Date.parse(response.respondedAt);
    if (response.challengeNonce !== challenge.nonce || !Number.isFinite(observed)
      || !Number.isFinite(respondedAt) || observed < requestedAt
      || respondedAt < observed || respondedAt > evaluatedAt) {
      errors.push({ rule: "LIVE_WITNESS_RESPONSE_NOT_CHALLENGE_FRESH",
        path: `$.challenge.responses[${index}]`,
        message: "signed floor must be observed within the challenge window" });
    }
    const pin = externalPins.witnessKeys[response.witnessId];
    const prior = historicalByWitness.get(response.witnessId);
    const floorSha256 = sha256Hex(canonicalBytes(response.floor));
    const responsePayload = { repositoryId: "redshift-three67/aurelia",
      logId: latestCheckpoint.logId, witnessId: response.witnessId,
      challengeNonce: response.challengeNonce, floorSha256,
      latestCheckpointSha256, respondedAt: response.respondedAt };
    if (response.floor.witnessId !== response.witnessId || !pin || !prior
      || response.floor.keyRef !== pin.keyRef
      || response.floor.previousFloorSha256 !== sha256Hex(canonicalBytes(prior))
      || response.floor.instanceKeyEpoch < prior.instanceKeyEpoch
      || response.floor.minimumTreeSize < prior.minimumTreeSize
      || (response.floor.minimumTreeSize === prior.minimumTreeSize
        && response.floor.minimumCheckpointSha256 !== prior.minimumCheckpointSha256)
      || response.floor.minimumTreeSize > latestCheckpoint.treeSize
      || (response.floor.minimumTreeSize === latestCheckpoint.treeSize
        && response.floor.minimumCheckpointSha256 !== latestCheckpointSha256)
      || response.floor.nonce === prior.nonce
      || !verifyEd25519({ publicKeyBase64url: pin.publicKeyBase64url,
        payloadBytes: canonicalBytes(without(response.floor, ["signature"])),
        signatureBase64url: response.floor.signature })
      || !verifyEd25519({ publicKeyBase64url: pin.publicKeyBase64url,
        payloadBytes: canonicalBytes(responsePayload),
        signatureBase64url: response.responseSignature })) {
      errors.push({ rule: "LIVE_WITNESS_RESPONSE_SIGNATURE_INVALID",
        path: `$.challenge.responses[${index}]`, message: "unlinked, stale, split, replayed, or invalid witness response" });
    }
  }
  return { errors, authorityRequired: ["production-authority-context"],
    challengeFresh: errors.length === 0, gateEffective: false };
}
```

Factor the historical/live floor comparison above into one shared helper in
implementation, preserving every condition. Mutations independently break
previous-floor hash, key epoch, nonce, size, same-size checkpoint hash, latest
checkpoint bound, challenge nonce, both timestamps, floor signature, and
challenge-response signature.

- [ ] **Step 7: Run and confirm GREEN**

Expected: valid prefix passes offline replay; stale/split/missing mutations fail;
live evaluation without challenge responses reports an authority stop.
Even a valid challenge against caller-supplied pins remains
`challengeFresh:true, gateEffective:false`; Plan 11 alone consumes it while
constructing the independently authority-bound aggregate context.

- [ ] **Step 8: Commit full-prefix verification**

```powershell
git add docs/governance/schemas/transparency-checkpoint.schema.json docs/governance/schemas/transparency-bundle.schema.json docs/governance/schemas/transparency-witness-floor.schema.json scripts/governance/transparency-verifier.mjs scripts/governance/transparency-verifier.test.mjs scripts/fixtures/governance/transparency/valid-prefix.json
git commit -m "feat: verify transparency checkpoints and floors"
```

### Task 4: Validate instance-key transition and equivocation reports

**Files:**

- Create: `docs/governance/schemas/transparency-key-transition.schema.json`
- Create: `docs/governance/schemas/transparency-equivocation-report.schema.json`
- Modify: `scripts/governance/transparency-verifier.mjs`
- Modify: `scripts/governance/transparency-verifier.test.mjs`

- [ ] **Step 1: Add RED tests for normal rotation**

Assert old instance signature plus Operator/Root signatures, and after first
Pilot-Green both Custodian signatures; next epoch exactly current+1; transition
binds the latest old checkpoint; old instance creates the final old checkpoint;
new instance becomes active only after witness floor plus first new checkpoint.

- [ ] **Step 2: Add RED tests for compromise/loss recovery**

Require Operator, Root, Controller, all Witnesses, and post-Pilot both
Custodians. Instance signature is null, the key-recovery floor is complete,
and pin caches cannot advance before the new regular checkpoint.

- [ ] **Step 3: Add RED equivocation tests**

Use two individually instance-signed checkpoint proposals of equal size and
different root with disjoint partial witness signatures. Assert a valid report
sets `equivocationDetected: true` and all derived gates red without requiring
a full witness quorum on either proposal.

- [ ] **Step 4: Run and confirm RED**

Expected: key-transition and equivocation tests fail on absent schemas/logic.

- [ ] **Step 5: Generate both schemas and implement transition replay**

Use the exact closed role-signature and witness-signature `oneOf` forms from
§6.4. Enforce sorted unique purposes/keys, exact `lastCheckpointSha256`, tree
size/root, transition entry full hash, floor/new-checkpoint linkage, and
permanent red derivation after either recovery floor or equivocation.

- [ ] **Step 6: Run and confirm GREEN**

Expected: valid normal/recovery transitions and equivocation report pass;
threshold, order, epoch, premature pin, and fork mutations fail.

- [ ] **Step 7: Commit key-transition and fork detection**

```powershell
git add docs/governance/schemas/transparency-key-transition.schema.json docs/governance/schemas/transparency-equivocation-report.schema.json scripts/governance/transparency-verifier.mjs scripts/governance/transparency-verifier.test.mjs
git commit -m "feat: verify transparency key transitions"
```

### Task 5: Validate custodian-pin transitions

**Files:**

- Create: `docs/governance/schemas/custodian-pin-transition.schema.json`
- Modify: `scripts/governance/transparency-verifier.mjs`
- Modify: `scripts/governance/transparency-verifier.test.mjs`

- [ ] **Step 1: Write assignment and rotation RED tests**

Initial assignment uses pin epoch 0→1, null previous identity/key/fingerprint,
and Operator+Root+candidate signatures. Rotation uses old epoch→old+1 and
Root+remaining Custodian+candidate. Event hash, acceptance receipt, head/tree,
role, key, assignee, and fingerprint must match repository replay exactly.

- [ ] **Step 2: Add pending-pin and split-view mutations**

Before the first full-quorum checkpoint, derive the repository ROLE as
externally pending and gate-red. Test candidate authorizing pre-transition
gate resets, one-sided pin cache update, same person/key as another Custodian,
wrong receipt head, and missing witness.

- [ ] **Step 3: Run and confirm RED**

Expected: missing schema and pin-state derivation fail.

- [ ] **Step 4: Generate the closed schema and implement replay**

Use exact fields and signature purposes from §12.5. Update
`state.custodianPins` only at the first checkpoint whose tree includes the
transition; never infer external effectiveness from the ROLE record alone.

- [ ] **Step 5: Run and confirm GREEN**

Expected: initial assignment and rotation pass; pending, split, identity,
receipt, and threshold mutations fail.

- [ ] **Step 6: Commit custodian-pin verification**

```powershell
git add docs/governance/schemas/custodian-pin-transition.schema.json scripts/governance/transparency-verifier.mjs scripts/governance/transparency-verifier.test.mjs
git commit -m "feat: verify custodian pin transitions"
```

### Task 6: Enforce one repository-wide nonce prefix

**Files:**

- Create: `scripts/governance/nonce-replay.mjs`
- Create: `scripts/governance/nonce-replay.test.mjs`
- Create: `scripts/governance/production-authority-context.mjs`
- Create: `scripts/governance/production-authority-context.test.mjs`
- Create: `docs/governance/schemas/signed-artifact-inventory.schema.json`
- Modify: `scripts/governance/schema-builders/transparency.mjs`
- Modify: `scripts/governance/schema-registry.test.mjs`
- Modify: `scripts/governance-contract.mjs`
- Modify: `scripts/governance-contract.test.mjs`

- [ ] **Step 1: Write RED tests across artifact families**

Build one ordered artifact stream containing final approval, Pre-Ledger,
detached EVT attestations, log-entry instance signatures, checkpoints,
recovery-threshold signatures, Witness signatures/floors, key transitions and
live challenge responses plus exactly one signed artifact-inventory envelope.
Reuse one canonical nonce across every pair of
families and require `GOVERNANCE_NONCE_REUSE`; also reject padded, wrong-length,
missing, multiply addressed, and unregistered nonce-bearing schema paths.
The same bytes in a non-nonce digest field are not a collision.
Also prove that no arbitrary object, copied object, proxy, serialized value,
or synthetically correct raw pin/time bundle is accepted by
`readProductionAuthorityContext`; before Plan 11 no issuer exists at all.

Create `signed-artifact-inventory.schema.json` as a closed Draft-2020-12
schema with exactly
`purpose/inventoryId/repositoryId/headCommit/headTreeOid/artifactCount/artifactSetSha256/governanceDomainState/issuedAt/expiresAt/nonce/signature`.
`signature` is closed to `algorithm/keyRef/value`; algorithm is exactly
`Ed25519`. Commit/Tree and SHA-256 fields use lower-case full-length patterns,
the nonce is canonical unpadded 32-byte Base64url, count is a nonnegative safe
integer, and all timestamps are UTC RFC-3339 instants. `governanceDomainState`
is closed to `phase/domains`; `phase` is exactly
`before-final-approval`, `before-pre-ledger`, `before-genesis`, or
`gate-evaluation`. `domains` contains exactly one code-unit-sorted entry for
each frozen G0 domain in this exact order:
`acceptance-receipts`, `attestations`, `authority-controls`, `bootstrap`,
`collector`, `design-approval`, `events`, `evidence`, `external-model`,
`gates`, `manifests`, `operator-acceptance`, `recovery`, `register-records`,
`reviews`, `tcb`, `transparency-checkpoints`, and `trust-roots`; each closed entry has exactly
`domainId/artifactCount/headSha256`, with a null head allowed only at count
zero. Plan 11 performs signature, purpose, time, pin, Head/Tree, and signed
inventory/replay binding; the schema alone conveys no authority.
Extend `schema-builders/transparency.mjs` as the single writer of those exact
schema bytes, and add registry tests proving the canonical
`signed-artifact-inventory` name resolves, compiles, rejects extra properties,
rejects a missing/reordered/duplicate domain, and accepts the one valid closed
fixture used by `nonce-replay.test.mjs`.

- [ ] **Step 2: Implement the closed nonce-path registry and full-prefix replay**

```js
import { assertBase64urlBytes, sha256Hex } from "./crypto.mjs";
import { canonicalBytes } from "./rfc8785.mjs";

const GOVERNANCE_NONCE_PATHS = Object.freeze({
  "final-design-approval": Object.freeze({ owned: Object.freeze(["nonce"]), references: Object.freeze([]) }),
  "pre-ledger-trust-bundle": Object.freeze({ owned: Object.freeze(["nonce"]), references: Object.freeze([]) }),
  "signed-artifact-inventory": Object.freeze({ owned: Object.freeze(["nonce"]), references: Object.freeze([]) }),
  "trust-roots": Object.freeze({ owned: Object.freeze([]), references: Object.freeze([]) }),
  "event-attestation": Object.freeze({ owned: Object.freeze(["nonce"]), references: Object.freeze([]) }),
  "governance-event": Object.freeze({ owned: Object.freeze([]), references: Object.freeze(["authorizationAttestations[].nonce"]) }),
  "governance-register-record": Object.freeze({ owned: Object.freeze([]), references: Object.freeze([]) }),
  "evidence-record": Object.freeze({ owned: Object.freeze([]), references: Object.freeze([]) }),
  "evidence-artifact": Object.freeze({ owned: Object.freeze([]), references: Object.freeze([]) }),
  "review-record": Object.freeze({ owned: Object.freeze([]), references: Object.freeze([]) }),
  "gate-record": Object.freeze({ owned: Object.freeze([]), references: Object.freeze([]) }),
  "governance-manifest": Object.freeze({ owned: Object.freeze([]), references: Object.freeze([]) }),
  "acceptance-receipt": Object.freeze({ owned: Object.freeze(["instanceSignature.nonce"]), references: Object.freeze([]) }),
  "branch-policy-transition": Object.freeze({ owned: Object.freeze(["instanceSignature.nonce"]), references: Object.freeze([]) }),
  "transparency-checkpoint": Object.freeze({
    owned: Object.freeze(["instanceSignature.nonce", "recoveryAuthorizationSignatures[].nonce", "witnessSignatures[].nonce"]),
    references: Object.freeze([]),
  }),
  "transparency-witness-floor": Object.freeze({ owned: Object.freeze(["nonce"]), references: Object.freeze([]) }),
  "transparency-key-transition": Object.freeze({
    owned: Object.freeze(["instanceSignature.nonce", "authorizationSignatures[].nonce"]), references: Object.freeze([]),
  }),
  "transparency-equivocation-report": Object.freeze({
    owned: Object.freeze(["nonce", "firstProposal.instanceSignature.nonce", "firstProposal.witnessSignatures[].nonce", "secondProposal.instanceSignature.nonce", "secondProposal.witnessSignatures[].nonce"]),
    references: Object.freeze([]),
  }),
  "custodian-pin-transition": Object.freeze({
    owned: Object.freeze(["instanceSignature.nonce", "transitionSignatures[].nonce"]), references: Object.freeze([]),
  }),
});
const noncePathsBySchema = new Map(Object.entries(GOVERNANCE_NONCE_PATHS));
function valuesAt(value, path) {
  const segments = path.split(".");
  function visit(node, index) {
    if (index === segments.length) return [node];
    const many = segments[index].endsWith("[]");
    const name = many ? segments[index].slice(0, -2) : segments[index];
    const next = node?.[name];
    if (many) return Array.isArray(next)
      ? next.flatMap((item) => visit(item, index + 1)) : [];
    return next === undefined || next === null ? [] : visit(next, index + 1);
  }
  return visit(value, 0);
}
export function verifyGovernanceNoncePrefix({ artifacts }) {
  const errors = [];
  const seen = new Map();
  const claims = [];
  const artifactClaims = [];
  const artifactIds = new Set();
  let inventoryEnvelopeCount = 0;
  for (const artifact of artifacts) {
    if (!artifact || typeof artifact !== "object" || Array.isArray(artifact)
      || ![null, Object.prototype].includes(Object.getPrototypeOf(artifact))) {
      errors.push({ rule: "NONCE_ARTIFACT_DESCRIPTOR_INVALID", path: "$",
        message: "artifact descriptor must be a closed plain object" });
      continue;
    }
    const descriptorKeys = Object.keys(artifact).sort();
    const expectedKeys = (artifact.inventoryMember === false
      ? ["artifactId", "inventoryMember", "schemaName", "value"]
      : ["artifactId", "schemaName", "value"]).sort();
    if (JSON.stringify(descriptorKeys) !== JSON.stringify(expectedKeys)) {
      errors.push({ rule: "NONCE_ARTIFACT_DESCRIPTOR_INVALID", path: String(artifact.artifactId),
        message: "artifact descriptor has missing or extra fields" });
      continue;
    }
    if (typeof artifact.artifactId !== "string" || artifact.artifactId.length === 0
      || artifactIds.has(artifact.artifactId)) {
      errors.push({ rule: "NONCE_ARTIFACT_ID_INVALID", path: String(artifact.artifactId),
        message: "artifact IDs must be non-empty and globally unique" });
      continue;
    }
    artifactIds.add(artifact.artifactId);
    if (artifact.inventoryMember === false) {
      inventoryEnvelopeCount += 1;
      if (artifact.schemaName !== "signed-artifact-inventory") {
        errors.push({ rule: "NONCE_INVENTORY_ENVELOPE_INVALID", path: artifact.artifactId,
          message: "only the signed inventory envelope may be excluded from its subject set" });
      }
    } else {
      artifactClaims.push([artifact.schemaName, artifact.artifactId,
        sha256Hex(canonicalBytes(artifact.value))]);
    }
    const pathContract = noncePathsBySchema.get(artifact.schemaName);
    if (!pathContract) {
      errors.push({ rule: "NONCE_SCHEMA_UNREGISTERED", path: artifact.artifactId,
        message: `no closed nonce map for ${artifact.schemaName}` });
      continue;
    }
    for (const path of pathContract.owned) for (const nonce of valuesAt(artifact.value, path)) {
      try { assertBase64urlBytes(nonce, 32, `${artifact.artifactId}.${path}`); }
      catch (error) {
        errors.push({ rule: "GOVERNANCE_NONCE_INVALID", path: `${artifact.artifactId}.${path}`, message: error.message });
        continue;
      }
      const claim = `${artifact.schemaName}\u0000${artifact.artifactId}\u0000${path}`;
      if (seen.has(nonce)) errors.push({ rule: "GOVERNANCE_NONCE_REUSE",
        path: claim, message: `nonce already claimed by ${seen.get(nonce)}` });
      else { seen.set(nonce, claim); claims.push([claim, nonce]); }
    }
    for (const path of pathContract.references) for (const nonce of valuesAt(artifact.value, path)) {
      try { assertBase64urlBytes(nonce, 32, `${artifact.artifactId}.${path}`); }
      catch (error) {
        errors.push({ rule: "GOVERNANCE_NONCE_REFERENCE_INVALID", path: `${artifact.artifactId}.${path}`, message: error.message });
        continue;
      }
      if (!seen.has(nonce)) errors.push({ rule: "GOVERNANCE_NONCE_REFERENCE_UNRESOLVED",
        path: `${artifact.schemaName}\u0000${artifact.artifactId}\u0000${path}`,
        message: "nonce reference must resolve to exactly one earlier owner" });
    }
  }
  if (inventoryEnvelopeCount !== 1) {
    errors.push({ rule: "NONCE_INVENTORY_ENVELOPE_INVALID", path: "$",
      message: "exactly one signed inventory envelope is required" });
  }
  claims.sort((left, right) => {
    const a = `${left[0]}\u0000${left[1]}`;
    const b = `${right[0]}\u0000${right[1]}`;
    return a < b ? -1 : a > b ? 1 : 0;
  });
  artifactClaims.sort((left, right) => {
    const a = `${left[0]}\u0000${left[1]}`;
    const b = `${right[0]}\u0000${right[1]}`;
    return a < b ? -1 : a > b ? 1 : 0;
  });
  return Object.freeze({ errors, noncePrefixSha256: errors.length ? null
    : sha256Hex(canonicalBytes(claims)), claimCount: claims.length,
    artifactSetSha256: errors.length ? null : sha256Hex(canonicalBytes(artifactClaims)),
    artifactCount: artifactClaims.length,
    occupiedNonces: Object.freeze([...seen.keys()].sort()),
    cryptographicValid: errors.length === 0,
    inventoryBindingVerified: false,
    testOnly: false, gateEffective: false });
}
```

Create the non-issuing capability shell exactly as follows. Plan 11 modifies
this same module to add the only validating issuer; no other plan may export a
constructor or expose the private map.

```js
const PRODUCTION_AUTHORITY_CLAIMS = new WeakMap();

export function readProductionAuthorityContext(value) {
  const claims = value && typeof value === "object" ? PRODUCTION_AUTHORITY_CLAIMS.get(value) : undefined;
  if (!claims) throw new TypeError("unverified production authority context");
  return claims;
}

// Plan 11 adds verifyProductionAuthorityContext in this module and only after
// its complete verification stores Object.freeze(claims) in PRODUCTION_AUTHORITY_CLAIMS.
```

The single versioned source literal registers every Plan-05/06 inventory
subject schema, including explicit empty `owned/references` contracts for
non-Nonce trust-root/register/evidence/review/gate/manifest subjects. A
`governance-event` references, but does not re-own, the Nonces of its exact
detached `event-attestation` subjects, which must precede it in append order.
It also registers every Plan-05/06 owned/reference nonce location
with exactly the closed shape `{owned:[string],references:[string]}`, including
nested signature arrays and nullable instance signatures. Both arrays use the
same dot/`[]` path grammar and never a JSONPath `$` prefix. `owned` creates a
globally unique nonce claim; `references` must resolve to exactly one owner in
an earlier artifact and never creates a second claim. Each later schema-builder
in Plans 07–10 edits this same source literal in its sequential commit, after
which module initialization recursively freezes the completed table; no
`Object.assign`, exported mutator, runtime API, or alternate registry name may
add or replace a registration. A source
contract walks every registered closed schema property tree and fails when a
field named `nonce`, ending in `Nonce`, or a signature object's nonce is not
classified exactly once as owner or reference. Tests reject a reference before
its owner, a reference to no owner, two owners, owner/reference double
classification, alternative path grammar, and post-initialization mutation.
The replay consumes the complete immutable artifact
prefix, never only newly added files. Its result is integrity evidence, not a
gate: Plan 11 must bind it into `ProductionAuthorityContext`.
The standalone result deliberately reports `inventoryBindingVerified:false`:
Plan 06 cannot know that the caller supplied every artifact. In issuer Phase A,
Plan 11 recomputes and verifies the independently signed counts, IDs, heads and
inventory digests, then binds the exact `noncePrefixSha256` and occupied set in
the context claims; no caller can flip this flag.

Each logical signed artifact appears exactly once in `artifacts`. In
particular, Plan 05 first proves detached/embedded EVT-attestation byte
equality and then supplies only the canonical detached artifact to this nonce
stream; the embedded duplicate and Acceptance-Receipt `nonceSha256` summary
are consistency witnesses, not second nonce claims. Missing either duplicate
binding still fails in its owning verifier.

Exactly the externally signed inventory envelope is passed with
`inventoryMember:false`: its nonce is still checked and claimed globally, but
its own full hash is excluded from the subject `artifactSetSha256` that it
signs, preventing a self-hash cycle. Zero or more than one excluded artifact,
or exclusion of any other schema, is `NONCE_INVENTORY_ENVELOPE_INVALID`.
The descriptor is otherwise closed: normal descriptors contain exactly
`artifactId/schemaName/value`; only the inventory descriptor additionally
contains `inventoryMember:false`. Tests cover missing, duplicate, wrongly
typed, differently identified, and multiply excluded inventory envelopes,
extra descriptor fields, and code-unit-order permutations. Plan 11 then proves
that this excluded descriptor contains byte-for-byte the same signed envelope
whose `artifactCount/artifactSetSha256` equals the included subject set.

- [ ] **Step 3: Integrate and commit the nonce replay**

```powershell
node --test scripts/governance/nonce-replay.test.mjs scripts/governance/production-authority-context.test.mjs scripts/governance-contract.test.mjs
git add docs/governance/schemas/signed-artifact-inventory.schema.json scripts/governance/nonce-replay.mjs scripts/governance/nonce-replay.test.mjs scripts/governance/production-authority-context.mjs scripts/governance/production-authority-context.test.mjs scripts/governance/schema-builders/transparency.mjs scripts/governance/schema-registry.test.mjs scripts/governance-contract.mjs scripts/governance-contract.test.mjs
git commit -m "feat: replay the global governance nonce prefix"
```

Expected: all pairwise family-reuse mutations fail deterministically; a full
unique prefix produces a stable `noncePrefixSha256` but remains
non-gate-effective and inventory-unproven until Plan 11.

### Task 7: Integrate offline transparency replay

**Files:**

- Modify: `scripts/governance-contract.mjs`
- Modify: `scripts/governance-contract.test.mjs`
- Create: `scripts/fixtures/governance/transparency/mutations.json`

- [ ] **Step 1: Add an integration RED test**

Pass a valid exported fixture bundle and external public pins to the CLI and
assert offline history verifies, but current-gate evaluation remains blocked
without live challenge floors.

- [ ] **Step 2: Run and confirm RED**

Expected: CLI ignores the bundle or falsely claims current state.

- [ ] **Step 3: Wire `verifyTransparencyBundle` after bootstrap validation**

The CLI accepts only an explicit local bundle path and explicit external-pin
input supplied by the protected caller. It must label history replay
`offline-verified` and current state `authority-required` unless live inputs
are separately present. It performs no network call.
It also rejects every result carrying `testOnly: true` or
`gateEffective: false` as evidence for a green gate.

- [ ] **Step 4: Run and confirm GREEN**

Expected: offline fixture verifies; missing live floors remain a precise
authority stop; every mutation in `mutations.json` produces its expected rule.

- [ ] **Step 5: Run Plan 06 gates**

```powershell
node --test scripts/governance/rfc6962.test.mjs scripts/governance/transparency-verifier.test.mjs scripts/governance-contract.test.mjs
npm run check:canon
npm run typecheck:governance
npm run typecheck
npm run lint
git diff --check
```

Expected: all local tests and static gates pass; no live transparency claim is made.

- [ ] **Step 6: Commit transparency integration**

```powershell
git add scripts/governance-contract.mjs scripts/governance-contract.test.mjs scripts/fixtures/governance/transparency/mutations.json
git commit -m "feat: integrate offline transparency replay"
```

## Plan 06 acceptance evidence

- RFC-6962 leaf/node/full-tree golden vectors pass, including odd tree sizes.
- Bundle contains exactly the complete indexed prefix; all roots are recomputed.
- Checkpoint, floor, key-epoch, policy-epoch, TCB-state, and pin chains are monotone and closed.
- Old policy receipts never reactivate after A→B→A policy bytes.
- Partial split proposals suffice for an equivocation report and permanent red derivation.
- Historical replay is offline-verifiable; freshness is never inferred without live witness authority.
- No production API accepts a caller-supplied signature verifier; test-only replay is never gate-effective.
- No log append, witness contact, pin update, signature generation, or remote action occurs.
