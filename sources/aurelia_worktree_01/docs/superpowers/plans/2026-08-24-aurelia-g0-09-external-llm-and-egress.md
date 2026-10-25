# AURELIA G0 09 External LLM and Egress Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the fail-closed, offline-verifiable contracts for sanitized external-model evidence and its non-bypassable, receipt-first network egress without sending any request to an external model.

**Architecture:** This plan adds closed Draft-2020-12 schemas and pure validators around the existing RFC-8785, crypto, schema-registry, transparency, and evidence-lifecycle modules. Cryptographic tests use public RFC-8032 vectors; semantic tests use a strictly test-only verifier that can never affect a gate, while production verification is non-injectable. Provider access, network dispatch, credentials, production context, and the complete private repository remain out of scope. The request chain is accepted only in the order verified due diligence and sanitization -> verified dispatcher contract -> checkpointed request receipt -> sealed enforcement lease -> dispatch attestation -> transport receipt -> byte-identical response capture.

**Tech Stack:** Node.js 22 ESM, `node:test`, JSON Schema Draft 2020-12, RFC 8785, SHA-256, Ed25519, existing `scripts/governance/*` helpers.

---

## Scope and fixed dependencies

Use these exports exactly as established by the preceding G0 plans:

```js
import { canonicalBytes } from "./rfc8785.mjs";
import { fullArtifactSha256, sha256Hex, verifyEd25519 } from "./crypto.mjs";
import { validateSchema } from "./schema-registry.mjs";
import { readProductionAuthorityContext } from "./production-authority-context.mjs";
```

This plan never invokes Kimi, Gemini, another external model, a provider API, Chrome, GitHub, or M-G1. The G0 design itself must not be exported to an external model because it contains current security, recovery, deployment, and server architecture. All fixture authorities use `example.invalid`; all identities begin with `synthetic-g0-`. No private key exists in the repository, fixtures, chat, logs, or test output. Cryptographic unit tests use public RFC-8032 vectors only. Semantic fixture tests may use a `testOnlySemanticVerifier` exported exclusively from `scripts/governance/test-helpers.mjs`; the production `validateGovernance` and `governanceErrors` paths always call the real `verifyEd25519`, reject a `testOnlySemanticVerifier` option, and never allow semantic fixtures to support a gate.

Before the first implementation commit, capture the exact review base in the protected execution record:

```powershell
$plan09BaseSha = git rev-parse HEAD
if ($plan09BaseSha -notmatch '^[0-9a-f]{40}$') { throw 'Plan 09 base is not a full commit SHA' }
$env:AURELIA_PLAN09_BASE_SHA = $plan09BaseSha
$plan09BaseSha
```

Expected: the final command prints the captured 40-character pre-Plan-09 SHA. The operator records that exact value as `plan09BaseSha` in the separately protected execution record; the environment variable is only a session copy and no branch/ref is created as an identity anchor.

### Task 1: Close the due-diligence, sanitization, and request-envelope schemas

**Files:**
- Create: `docs/governance/schemas/provider-due-diligence.schema.json`
- Create: `docs/governance/schemas/sanitization-report.schema.json`
- Create: `docs/governance/schemas/external-model-request-envelope.schema.json`
- Create: `docs/governance/schemas/external-model-request-receipt.schema.json`
- Create: `scripts/governance/external-model-contract.mjs`
- Create: `scripts/governance/external-model-contract.test.mjs`
- Create: `scripts/fixtures/governance/external-model/valid-request-chain.json`
- Modify: `scripts/governance/nonce-replay.mjs`
- Modify: `scripts/governance/nonce-replay.test.mjs`

- [ ] **Step 1: Write the failing schema-closure test**

Add a test that loads the synthetic chain, validates each named schema, then mutates every top-level object with `unexpected: true` and expects a schema diagnostic. The valid due-diligence payload is exactly:

```js
const VALID_DUE_DILIGENCE = Object.freeze({
  providerName: "synthetic-provider",
  endpointClass: "local-runtime",
  endpointIdentifierSha256: "1".repeat(64),
  modelVersion: "synthetic-model-1",
  processingRegion: "EU-test",
  retentionPolicy: "zero-retention-test-contract",
  trainingUse: "disabled",
  termsVersionSha256: "2".repeat(64),
  assessedAt: "2026-08-24T10:00:00.000Z",
  expiresAt: "2026-08-24T11:00:00.000Z",
  assessorRole: "ROLE-QUALITY-SECURITY-REVIEWER",
  assessorAssigneeSnapshot: "synthetic-g0-dd-reviewer",
});
```

Also assert that `trainingUse: "enabled"`, an expired assessment, a non-EU production identifier, and a nonzero sanitization finding are rejected.

The fixture has two different immutable EVID record versions with the same ID: `expectedOutputEvidence` is externally accepted, has `status:"expected"` and `externalModelOutput:null`; `capturedOutputEvidence` does not exist yet at preflight. The Request Envelope's `expectedEvidenceRecordSha256` is exactly `fullArtifactSha256(expectedOutputEvidence)`. A test that substitutes a captured/future record, a guessed response hash, or a self-hash must fail.

- [ ] **Step 2: Run the test and record RED**

Run:

```powershell
node --test scripts/governance/external-model-contract.test.mjs
```

Expected: FAIL with `ERR_MODULE_NOT_FOUND` for `external-model-contract.mjs` or a missing-schema diagnostic naming all four schema paths.

- [ ] **Step 3: Implement the closed schemas and pure preflight validator**

Export this interface from `external-model-contract.mjs`:

```js
export function validateExternalModelPreflight({
  expectedOutputEvidence,
  dueDiligenceEvidence,
  sanitizationEvidence,
  dispatcherEvidence,
  requestEnvelope,
  requestReceipt,
  authorityContext,
}) {
  const authority = readProductionAuthorityContext(authorityContext);
  if (authority.profile !== "gate-evaluation" || authority.gateEffective !== true) throw new TypeError("gate-effective gate-evaluation ProductionAuthorityContext required");
  const errors = [];
  errors.push(...validateSchema("provider-due-diligence", dueDiligenceEvidence.providerDueDiligence));
  errors.push(...validateSchema("sanitization-report", sanitizationEvidence.sanitizationReport));
  errors.push(...validateSchema("external-model-request-envelope", requestEnvelope));
  errors.push(...validateSchema("external-model-request-receipt", requestReceipt));
  errors.push(...validateEvidenceOrder({
    expectedOutputEvidence,
    dueDiligenceEvidence,
    sanitizationEvidence,
    dispatcherEvidence,
    requestEnvelope,
    requestReceipt,
    authority,
  }));
  return errors;
}
```

Implement `validateEvidenceOrder` in the same module with no delegated/undefined comparison helper:

```js
function mismatch(errors, path, values) {
  if (values.some((value) => value !== values[0])) errors.push(diagnostic(path, "bound values differ"));
}

function verifiedEvent(authority, evidence, expectedHash, path, errors) {
  const event = authority.transparency.eventsByHash[expectedHash];
  if (!event || event.recordRef !== evidence.id || event.resultingStatus !== "verified") {
    errors.push(diagnostic(path, "does not identify the verified transition of the referenced EVID"));
    return null;
  }
  if (!authority.acceptanceReceipts.acceptedEventHashes.includes(expectedHash)) {
    errors.push(diagnostic(path, "verified transition lacks prior external acceptance"));
  }
  return event;
}

function validateEvidenceOrder({
  expectedOutputEvidence, dueDiligenceEvidence, sanitizationEvidence, dispatcherEvidence,
  requestEnvelope, requestReceipt, authority,
}) {
  const errors = [];
  const dd = dueDiligenceEvidence.providerDueDiligence;
  const sanitization = sanitizationEvidence.sanitizationReport;
  const dispatcher = dispatcherEvidence.egressDispatcherContract;
  for (const name of ["providerName", "endpointClass", "endpointIdentifierSha256", "modelVersion", "processingRegion", "retentionPolicy", "trainingUse"]) {
    mismatch(errors, name, [dd[name], requestEnvelope[name]]);
  }
  mismatch(errors, "inputArtifactSha256", [sanitization.sanitizedArtifactSha256, requestEnvelope.inputArtifactSha256]);
  for (const name of ["inputClassification", "sanitizerRole", "sanitizerAssigneeSnapshot"]) {
    mismatch(errors, name, [sanitization[name], requestEnvelope[name]]);
  }
  if (!["public", "synthetic", "sanitized-non-production"].includes(requestEnvelope.inputClassification)) errors.push(diagnostic("inputClassification", "classification is not dispatchable"));
  if (sanitization.secretFindings !== 0 || sanitization.personalDataFindings !== 0 || sanitization.disposition !== "passed") errors.push(diagnostic("sanitizationReport", "sanitization is not clean"));
  if (requestEnvelope.dueDiligenceEvidenceRef !== dueDiligenceEvidence.id) errors.push(diagnostic("dueDiligenceEvidenceRef", "wrong EVID"));
  if (requestEnvelope.sanitizationEvidenceRef !== sanitizationEvidence.id) errors.push(diagnostic("sanitizationEvidenceRef", "wrong EVID"));
  if (requestEnvelope.egressDispatcherContractEvidenceRef !== dispatcherEvidence.id) errors.push(diagnostic("egressDispatcherContractEvidenceRef", "wrong EVID"));
  verifiedEvent(authority, dueDiligenceEvidence, requestEnvelope.dueDiligenceVerificationEventHash, "dueDiligenceVerificationEventHash", errors);
  verifiedEvent(authority, sanitizationEvidence, requestEnvelope.sanitizationVerificationEventHash, "sanitizationVerificationEventHash", errors);
  verifiedEvent(authority, dispatcherEvidence, requestEnvelope.egressDispatcherContractVerificationEventHash, "egressDispatcherContractVerificationEventHash", errors);
  for (const name of [
    "externalOutputEvidenceRef", "expectedEvidenceRecordSha256", "requestDescriptorSha256",
    "providerApplicationRequestSha256", "providerRequestBodySha256", "providerApplicationHeadersSha256",
    "transportProfileRef", "transportProfileSha256", "authorizationCredentialSha256",
  ]) mismatch(errors, name, [requestEnvelope[name], requestReceipt[name]]);
  mismatch(errors, "allowedHeaderNames", [
    JSON.stringify(requestEnvelope.allowedHeaderNames), JSON.stringify(requestReceipt.allowedHeaderNames),
  ]);
  for (const name of ["subjectIds", "subjectPaths"]) mismatch(errors, name, [JSON.stringify(requestEnvelope[name]), JSON.stringify(expectedOutputEvidence[name])]);
  mismatch(errors, "scope", [requestEnvelope.scope, expectedOutputEvidence.scope]);
  const expectedRecordSha256 = fullArtifactSha256(expectedOutputEvidence);
  if (expectedOutputEvidence.status !== "expected" || expectedOutputEvidence.externalModelOutput !== null) errors.push(diagnostic("expectedOutputEvidence", "pre-dispatch predecessor must remain expected with no captured output object"));
  if (requestEnvelope.externalOutputEvidenceRef !== expectedOutputEvidence.id || requestReceipt.externalOutputEvidenceRef !== expectedOutputEvidence.id) errors.push(diagnostic("externalOutputEvidenceRef", "does not identify the expected predecessor"));
  if (expectedRecordSha256 !== requestEnvelope.expectedEvidenceRecordSha256 || expectedRecordSha256 !== requestReceipt.expectedEvidenceRecordSha256) errors.push(diagnostic("expectedEvidenceRecordSha256", "expected predecessor bytes differ"));
  if (!authority.acceptanceReceipts.acceptedRecordHashes.includes(expectedRecordSha256)) errors.push(diagnostic("expectedEvidenceRecordSha256", "expected predecessor lacks earlier external acceptance"));
  if (fullArtifactSha256(requestEnvelope) !== requestReceipt.requestEnvelopeSha256) errors.push(diagnostic("requestEnvelopeSha256", "Envelope bytes differ"));
  const receiptLogEntry = authority.transparency.entriesByReceiptId[requestReceipt.requestReceiptId];
  if (!receiptLogEntry || receiptLogEntry.entryKind !== "external-model-request-receipt") errors.push(diagnostic("requestReceiptId", "signed receipt log entry is absent"));
  for (const [kind, idField, indexField] of [
    ["dueDiligence", "dueDiligenceAcceptanceReceiptId", "dueDiligenceAcceptanceReceiptLogIndex"],
    ["sanitization", "sanitizationAcceptanceReceiptId", "sanitizationAcceptanceReceiptLogIndex"],
    ["dispatcher", "egressDispatcherContractAcceptanceReceiptId", "egressDispatcherContractAcceptanceReceiptLogIndex"],
  ]) {
    const accepted = authority.acceptanceReceipts.byId[requestReceipt[idField]];
    if (!accepted || accepted.logIndex !== requestReceipt[indexField] || accepted.logIndex >= receiptLogEntry.logIndex) errors.push(diagnostic(indexField, `${kind} acceptance receipt is absent or not prior`));
  }
  const instant = Date.parse(authority.trustedTime.now);
  if (![instant, Date.parse(requestReceipt.preflightAcceptedAt), Date.parse(requestReceipt.expiresAt), Date.parse(dd.expiresAt), Date.parse(dispatcher.expiresAt)].every(Number.isFinite)) errors.push(diagnostic("trustedTime", "invalid timestamp"));
  if (Date.parse(requestReceipt.preflightAcceptedAt) >= Date.parse(requestReceipt.expiresAt) || instant >= Date.parse(requestReceipt.expiresAt) || instant >= Date.parse(dd.expiresAt) || instant >= Date.parse(dispatcher.expiresAt)) errors.push(diagnostic("expiresAt", "preflight authority is expired"));
  return errors;
}
```

Plan 11's sole issuer stores code-unit-sorted, deeply frozen `eventsByHash`, `entriesByReceiptId`, Acceptance-Receipt hash arrays, pins, and Trusted-Time claims in the module-private context; callers cannot supply or mutate these views. Import `diagnostic` from `diagnostics.mjs`. The schema additionally closes `command` as the exact runner invocation and the tests recompute `requestDescriptorSha256` from the full section-12.4 projection, so command or descriptor drift is rejected before this relational pass.

Modify only Plan 06's `GOVERNANCE_NONCE_PATHS` source literal in
`nonce-replay.mjs`; never discover nonces by recursively accepting arbitrary
key names. Every entry has exactly `owned/references`, both frozen arrays of
strings in the same dot/`[]` path grammar without a leading `$.`. Do not rename
the literal, call `Object.assign`, export a mutation API, or mutate it at
runtime. Insert these properties before the enclosing `Object.freeze` executes:

```js-fragment
"provider-due-diligence": Object.freeze({ owned: Object.freeze([]), references: Object.freeze([]) }),
"sanitization-report": Object.freeze({ owned: Object.freeze([]), references: Object.freeze([]) }),
"external-model-request-envelope": Object.freeze({
  owned: Object.freeze(["nonce"]), references: Object.freeze([]),
}),
"external-model-request-receipt": Object.freeze({ owned: Object.freeze([]), references: Object.freeze([]) }),
"egress-transport-profile": Object.freeze({ owned: Object.freeze([]), references: Object.freeze([]) }),
"network-enforcement-verification": Object.freeze({ owned: Object.freeze([]), references: Object.freeze([]) }),
"egress-dispatcher-contract": Object.freeze({ owned: Object.freeze([]), references: Object.freeze([]) }),
"egress-enforcement-lease": Object.freeze({
  owned: Object.freeze(["monitorSignature.nonce"]),
  references: Object.freeze(["floorChallengeNonce"]),
}),
"egress-dispatch-attestation": Object.freeze({
  owned: Object.freeze(["monitorSignature.nonce"]),
  references: Object.freeze(["floorChallengeNonce"]),
}),
"egress-transport-receipt": Object.freeze({
  owned: Object.freeze(["monitorSignature.nonce"]), references: Object.freeze([]),
}),
"external-model-response-envelope": Object.freeze({
  owned: Object.freeze(["nonce"]), references: Object.freeze([]),
}),
```

Plan-06's Witness-challenge schema owns the one occurrence for
`floorChallengeNonce`; lease/attestation occurrences above are references and
must equal exactly one strictly earlier owner without entering the owner
uniqueness set or increasing `claimCount`. Add schema-source coverage tests:
every registered path exists in its schema, every schema property whose name
contains `nonce` is registered exactly once as owner/reference, unknown
nonce-like properties fail, every owner is canonical 32-byte Base64url and
globally unique, and every reference resolves to exactly one earlier owner in
the full prefix. The Request and Response Envelope nonces must be different.
The standalone replay retains `inventoryBindingVerified:false`; Plan 09 never
changes that field, and only Plan 11's separately signed inventory composition
may establish completeness.

- [ ] **Step 4: Run the focused test and record GREEN**

Run:

```powershell
node --test scripts/governance/external-model-contract.test.mjs
```

Expected: PASS; the TAP summary reports zero failures and at least eight subtests.

- [ ] **Step 5: Commit the preflight contract**

```powershell
git add docs/governance/schemas/provider-due-diligence.schema.json docs/governance/schemas/sanitization-report.schema.json docs/governance/schemas/external-model-request-envelope.schema.json docs/governance/schemas/external-model-request-receipt.schema.json scripts/governance/external-model-contract.mjs scripts/governance/external-model-contract.test.mjs scripts/governance/nonce-replay.mjs scripts/governance/nonce-replay.test.mjs scripts/fixtures/governance/external-model/valid-request-chain.json
git commit -m "feat: validate external model preflight evidence"
```

### Task 2: Bind application request bytes and the discriminated transport profile

**Files:**
- Create: `docs/governance/schemas/egress-transport-profile.schema.json`
- Create: `scripts/governance/egress-transport-profile.mjs`
- Create: `scripts/governance/egress-transport-profile.test.mjs`
- Create: `scripts/fixtures/governance/external-model/http1-profile.json`
- Create: `scripts/fixtures/governance/external-model/http2-profile.json`

- [ ] **Step 1: Write the failing H1/H2 profile tests**

Test the exact discriminant:

```js
assert.deepEqual(validateTransportProfile(http1Profile), []);
assert.deepEqual(validateTransportProfile(http2Profile), []);
assert.match(validateTransportProfile({ ...http2Profile, connectionReuse: true })[0].message, /connectionReuse/);
assert.match(validateTransportProfile({ ...http2Profile, http2: { ...http2Profile.http2, streamId: 3 } })[0].message, /streamId/);
assert.match(validateTransportProfile({ ...http1Profile, trailers: ["digest"] })[0].message, /trailers/);
```

The H2 fixture must contain Stream 1, dynamic table size 0, Huffman false, the pseudoheader order `:method,:scheme,:authority,:path`, client settings 1=0, 2=0, 3=1 in numeric order, ACK required, and a fresh exclusive connection. The H1 fixture must contain origin form, HTTP/1.1, one Host, Content-Length, `connection: close`, no transfer encoding, and no reuse.

- [ ] **Step 2: Run the test and record RED**

```powershell
node --test scripts/governance/egress-transport-profile.test.mjs
```

Expected: FAIL because `validateTransportProfile` is not exported.

- [ ] **Step 3: Implement exact application-request and profile comparison**

Export:

```js
export function validateTransportProfile(profile) {
  const errors = validateSchema("egress-transport-profile", profile);
  if (errors.length) return errors;
  return profile.kind === "http/1.1"
    ? validateHttp1Profile(profile)
    : validateHttp2Profile(profile);
}

export function applicationRequestDigests(request) {
  const names = request.applicationHeaders.map(({ name }) => name);
  if (names.some((name) => name !== name.toLowerCase())) throw new TypeError("application header names must be lowercase");
  if (new Set(names).size !== names.length) throw new TypeError("application header names must be unique");
  if (JSON.stringify(names) !== JSON.stringify(names.toSorted())) throw new TypeError("application headers must be name sorted");
  if (names.some((name) => ["host", "connection", "transfer-encoding", "content-length"].includes(name) || name.startsWith(":"))) throw new TypeError("transport header in applicationHeaders");
  const headerBytes = canonicalBytes(request.applicationHeaders);
  const bodyBytes = Buffer.from(request.bodyBase64url, "base64url");
  if (bodyBytes.toString("base64url") !== request.bodyBase64url) throw new TypeError("bodyBase64url is not canonical");
  if (sha256Hex(bodyBytes) !== request.bodySha256) throw new TypeError("bodySha256 differs");
  return Object.freeze({
    requestSha256: fullArtifactSha256(request),
    bodySha256: sha256Hex(bodyBytes),
    headersSha256: sha256Hex(headerBytes),
  });
}
```

Implement the two profile helpers in full:

```js
function validateHttp1Profile(profile) {
  const errors = [];
  const requiredOrder = ["host", "content-length", "connection"];
  const h1 = profile.http1;
  if (profile.http2 !== null) errors.push(diagnostic("http2", "must be null for HTTP/1.1"));
  for (const [path, actual, expected] of [
    ["tlsAlpn", profile.tlsAlpn, "http/1.1"], ["connectionReuse", profile.connectionReuse, false],
    ["singleRequest", profile.singleRequest, true], ["streaming", profile.streaming, false],
    ["framingMode", profile.framingMode, "content-length"], ["http1.protocolVersion", h1.protocolVersion, "HTTP/1.1"],
    ["http1.requestTargetForm", h1.requestTargetForm, "origin"], ["http1.hostHeaderSource", h1.hostHeaderSource, "authority"],
    ["http1.contentLengthRequired", h1.contentLengthRequired, true], ["http1.connectionHeader", h1.connectionHeader, "close"],
    ["http1.transferEncoding", h1.transferEncoding, null],
  ]) if (actual !== expected) errors.push(diagnostic(path, `must equal ${String(expected)}`));
  if (profile.trailers.length !== 0 || profile.duplicateHeaderNamesAllowed.length !== 0) errors.push(diagnostic("trailers", "trailers/duplicate headers forbidden"));
  if (JSON.stringify(h1.mandatoryHeaderOrder) !== JSON.stringify(requiredOrder)) errors.push(diagnostic("http1.mandatoryHeaderOrder", "closed order mismatch"));
  if (!requiredOrder.every((name) => profile.orderedWireHeaderNames.includes(name))) errors.push(diagnostic("orderedWireHeaderNames", "mandatory header absent"));
  return errors;
}

function validateHttp2Profile(profile) {
  const errors = [];
  const h2 = profile.http2;
  const expectedPseudo = [":method", ":scheme", ":authority", ":path"];
  const expectedSettings = [
    { identifier: 1, value: 0 },
    { identifier: 2, value: 0 },
    { identifier: 3, value: 1 },
  ];
  if (profile.http1 !== null) errors.push(diagnostic("http1", "must be null for h2"));
  for (const [path, actual, expected] of [
    ["tlsAlpn", profile.tlsAlpn, "h2"], ["connectionReuse", profile.connectionReuse, false],
    ["singleRequest", profile.singleRequest, true], ["streaming", profile.streaming, false],
    ["http2.connectionMode", h2.connectionMode, "fresh-exclusive"],
    ["http2.connectionPreface", h2.connectionPreface, "PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"],
    ["http2.streamId", h2.streamId, 1], ["http2.maxConcurrentStreams", h2.maxConcurrentStreams, 1],
    ["http2.hpackDynamicTableSize", h2.hpackDynamicTableSize, 0], ["http2.hpackHuffman", h2.hpackHuffman, false],
    ["http2.settingsAckRequired", h2.settingsAckRequired, true], ["http2.goawayAfterResponse", h2.goawayAfterResponse, true],
  ]) if (actual !== expected) errors.push(diagnostic(path, `must equal ${String(expected)}`));
  if (JSON.stringify(h2.pseudoHeaderOrder) !== JSON.stringify(expectedPseudo)) errors.push(diagnostic("http2.pseudoHeaderOrder", "closed pseudoheader order mismatch"));
  if (JSON.stringify(h2.clientSettings) !== JSON.stringify(expectedSettings)) errors.push(diagnostic("http2.clientSettings", "closed SETTINGS mismatch"));
  if (profile.trailers.length !== 0 || profile.duplicateHeaderNamesAllowed.length !== 0) errors.push(diagnostic("trailers", "trailers/duplicate headers forbidden"));
  if (profile.orderedWireHeaderNames.some((name) => ["host", "connection", "transfer-encoding"].includes(name))) errors.push(diagnostic("orderedWireHeaderNames", "HTTP/2-forbidden header"));
  return errors;
}
```

The schema restricts `applicationHeaders[].name` to the closed provider-profile `allowedHeaderNames`; the code above rejects duplicate/non-lowercase/transport headers and proves the body digest. It must never expose or log the authorization value; only `authorizationCredentialSha256` is compared outside the encrypted request artifact.

- [ ] **Step 4: Run the focused tests and record GREEN**

```powershell
node --test scripts/governance/egress-transport-profile.test.mjs
```

Expected: PASS with zero failures.

- [ ] **Step 5: Commit the transport profile**

```powershell
git add docs/governance/schemas/egress-transport-profile.schema.json scripts/governance/egress-transport-profile.mjs scripts/governance/egress-transport-profile.test.mjs scripts/fixtures/governance/external-model/http1-profile.json scripts/fixtures/governance/external-model/http2-profile.json
git commit -m "feat: bind external model transport profiles"
```

### Task 3: Verify dispatcher, enforcement lease, and dispatch attestation

**Files:**
- Create: `docs/governance/schemas/network-enforcement-verification.schema.json`
- Create: `docs/governance/schemas/egress-dispatcher-contract.schema.json`
- Create: `docs/governance/schemas/egress-enforcement-lease.schema.json`
- Create: `docs/governance/schemas/egress-dispatch-attestation.schema.json`
- Create: `scripts/governance/egress-enforcement.mjs`
- Create: `scripts/governance/egress-enforcement.test.mjs`
- Create: `scripts/fixtures/governance/external-model/valid-enforcement-chain.json`

- [ ] **Step 1: Write the failing lease-intent projection and mutation tests**

Use this exact projection rule from design section 12.4:

```js
const LEASE_INTENT_EXCLUDED_FIELDS = new Set([
  "witnessFloorResponsesSha256",
  "activatedAt",
  "leaseIntentSha256",
  "leaseCoreSha256",
  "monitorSignature",
]);
```

Assert that mutating every other lease field changes `leaseIntentSha256`, while mutating each excluded field does not. Separately assert that the full lease core and monitor signature bind `witnessFloorResponsesSha256` and `activatedAt`. Reject stale floors, reused challenge nonce, nonempty `bypassPaths`, a contract profile absent from the verified profile list, token reuse, mismatched service/image/policy/endpoint hashes, and any expiry ordering violation.

- [ ] **Step 2: Run the test and record RED**

```powershell
node --test scripts/governance/egress-enforcement.test.mjs
```

Expected: FAIL because `leaseIntentBytes` and `validateEgressEnforcement` do not exist.

- [ ] **Step 3: Implement the pure enforcement-chain verifier**

Export:

```js
export function leaseIntentBytes(lease) {
  return canonicalBytes(Object.fromEntries(
    Object.entries(lease).filter(([name]) => !LEASE_INTENT_EXCLUDED_FIELDS.has(name)),
  ));
}

export function validateEgressEnforcement({
  networkEvidence,
  dispatcherEvidence,
  requestEnvelope,
  requestReceipt,
  requestCheckpoint,
  enforcementLease,
  dispatchAttestation,
  authorityContext,
}) {
  const authority = readProductionAuthorityContext(authorityContext);
  if (authority.profile !== "gate-evaluation" || authority.gateEffective !== true) throw new TypeError("gate-effective gate-evaluation ProductionAuthorityContext required");
  const errors = [
    ...validateSchema("network-enforcement-verification", networkEvidence.networkEnforcementVerification),
    ...validateSchema("egress-dispatcher-contract", dispatcherEvidence.egressDispatcherContract),
    ...validateSchema("egress-enforcement-lease", enforcementLease),
    ...validateSchema("egress-dispatch-attestation", dispatchAttestation),
    ...verifyEnforcementBindings({ networkEvidence, dispatcherEvidence, requestEnvelope, requestReceipt, enforcementLease, dispatchAttestation }),
  ];
  const lease = verifyLeaseIntentAndCore({ enforcementLease, dispatchAttestation, authority });
  const floors = verifyDispatchFloors({ enforcementLease, dispatchAttestation, requestCheckpoint, authority });
  errors.push(...lease.errors, ...floors.errors);
  const authorityRequired = [...new Set([...lease.authorityRequired, ...floors.authorityRequired])];
  return Object.freeze({ errors, authorityRequired, gateEffective: errors.length === 0 && authorityRequired.length === 0 });
}
```

Implement every called helper as executable core logic:

```js
const without = (value, excluded) => Object.fromEntries(
  Object.entries(value).filter(([name]) => !excluded.includes(name)),
);

function verifyLeaseIntentAndCore({ enforcementLease: lease, dispatchAttestation: attestation, authority }) {
  const errors = [];
  const authorityRequired = [];
  const intentSha256 = sha256Hex(leaseIntentBytes(lease));
  const coreSha256 = sha256Hex(canonicalBytes(without(lease, ["leaseCoreSha256", "monitorSignature"])));
  const attestationCoreSha256 = sha256Hex(canonicalBytes(without(attestation, ["attestationCoreSha256", "monitorSignature"])));
  if (intentSha256 !== lease.leaseIntentSha256) errors.push(diagnostic("leaseIntentSha256", "intent projection differs"));
  if (coreSha256 !== lease.leaseCoreSha256) errors.push(diagnostic("leaseCoreSha256", "lease core differs"));
  if (attestationCoreSha256 !== attestation.attestationCoreSha256) errors.push(diagnostic("attestationCoreSha256", "attestation core differs"));
  const pin = authority.pins.egressEnforcementMonitor;
  if (!pin || pin.keyRef !== lease.monitorKeyRef) authorityRequired.push("egress-monitor-public-pin");
  else {
    if (pin.serviceIdentity !== lease.monitorServiceIdentity || pin.imageDigest !== lease.monitorImageDigest || pin.policySha256 !== lease.monitorPolicySha256 || pin.permissionsSha256 !== lease.monitorPermissionsSha256 || pin.trustedTimeSourceSha256 !== lease.monitorTrustedTimeSourceSha256) errors.push(diagnostic("monitorKeyRef", "monitor pin metadata differs"));
    const leaseSignature = lease.monitorSignature;
    const attestationSignature = attestation.monitorSignature;
    if (leaseSignature.keyRef !== lease.monitorKeyRef || leaseSignature.leaseCoreSha256 !== lease.leaseCoreSha256 || !verifyEd25519({ publicKeyBase64url: pin.publicKeyBase64url, payloadBytes: canonicalBytes(without(leaseSignature, ["signature"])), signatureBase64url: leaseSignature.signature })) errors.push(diagnostic("monitorSignature", "invalid lease monitor signature"));
    if (attestationSignature.keyRef !== attestation.monitorKeyRef || attestationSignature.attestationCoreSha256 !== attestation.attestationCoreSha256 || !verifyEd25519({ publicKeyBase64url: pin.publicKeyBase64url, payloadBytes: canonicalBytes(without(attestationSignature, ["signature"])), signatureBase64url: attestationSignature.signature })) errors.push(diagnostic("monitorSignature", "invalid dispatch monitor signature"));
  }
  return { errors, authorityRequired };
}

function verifyDispatchFloors({ enforcementLease: lease, dispatchAttestation: attestation, requestCheckpoint, authority }) {
  const verifiedFloors = authority.freshFloors;
  const errors = [];
  if (verifiedFloors.challengeNonce !== lease.floorChallengeNonce) errors.push(diagnostic("floorChallengeNonce", "verified challenge nonce differs"));
  if (fullArtifactSha256(requestCheckpoint) !== lease.requestCheckpointSha256 || verifiedFloors.minimumTreeSize < requestCheckpoint.treeSize) errors.push(diagnostic("requestCheckpointSha256", "checkpoint is not covered by verified fresh floors"));
  if (sha256Hex(canonicalBytes(attestation.witnessFloorResponses)) !== lease.witnessFloorResponsesSha256) errors.push(diagnostic("witnessFloorResponsesSha256", "response array differs"));
  if (sha256Hex(canonicalBytes(attestation.witnessFloorResponses)) !== verifiedFloors.responsesSha256) errors.push(diagnostic("witnessFloorResponsesSha256", "responses differ from ProductionAuthorityContext"));
  for (const [index, response] of attestation.witnessFloorResponses.entries()) {
    if (response.floor.minimumTreeSize < requestCheckpoint.treeSize || (response.floor.minimumTreeSize === requestCheckpoint.treeSize && response.floor.minimumCheckpointSha256 !== requestCheckpoint.sha256)) errors.push(diagnostic(`witnessFloorResponses[${index}]`, "floor is below request checkpoint"));
    const respondedAt = Date.parse(response.respondedAt);
    const activatedAt = Date.parse(lease.activatedAt);
    if (!Number.isFinite(respondedAt) || respondedAt > activatedAt || activatedAt - respondedAt > 10_000) errors.push(diagnostic(`witnessFloorResponses[${index}].respondedAt`, "not within ten seconds before activation"));
  }
  return { errors, authorityRequired: [] };
}

function verifyEnforcementBindings({ networkEvidence, dispatcherEvidence, requestEnvelope, requestReceipt, enforcementLease: lease, dispatchAttestation: attestation }) {
  const errors = [];
  const network = networkEvidence.networkEnforcementVerification;
  const dispatcher = dispatcherEvidence.egressDispatcherContract;
  for (const name of ["dispatcherServiceIdentity", "dispatcherImageDigest", "dispatcherBinarySha256", "networkPolicySha256", "tokenStorePolicySha256"]) mismatch(errors, name, [network[name], dispatcher[name], lease[name], attestation[name]]);
  mismatch(errors, "endpointIdentifierSha256", [network.allowedEndpointIdentifierSha256, dispatcher.allowedEndpointIdentifierSha256, requestEnvelope.endpointIdentifierSha256, lease.endpointIdentifierSha256, attestation.endpointIdentifierSha256]);
  mismatch(errors, "requestReceiptId", [requestReceipt.requestReceiptId, lease.requestReceiptId, attestation.requestReceiptId]);
  mismatch(errors, "requestReceiptSha256", [fullArtifactSha256(requestReceipt), lease.requestReceiptSha256, attestation.requestReceiptSha256]);
  for (const name of ["dispatchTokenSha256", "providerApplicationRequestSha256", "providerRequestBodySha256", "providerApplicationHeadersSha256", "transportProfileRef", "transportProfileSha256", "authorizationCredentialSha256"]) mismatch(errors, name, [requestReceipt[name], lease[name], attestation[name]]);
  mismatch(errors, "allowedHeaderNames", [JSON.stringify(requestReceipt.allowedHeaderNames), JSON.stringify(lease.allowedHeaderNames), JSON.stringify(attestation.allowedHeaderNames)]);
  mismatch(errors, "requestCheckpointSha256", [lease.requestCheckpointSha256, attestation.requestCheckpointSha256]);
  mismatch(errors, "requestCheckpointTreeSize", [lease.requestCheckpointTreeSize, attestation.requestCheckpointTreeSize]);
  mismatch(errors, "requestCheckpointIssuedAt", [lease.requestCheckpointIssuedAt, attestation.requestCheckpointIssuedAt]);
  mismatch(errors, "enforcementLeaseSha256", [fullArtifactSha256(lease), attestation.enforcementLeaseSha256]);
  if (!network.allowedTransportProfileSha256s.includes(lease.transportProfileSha256) || JSON.stringify(network.allowedTransportProfileSha256s) !== JSON.stringify(dispatcher.allowedTransportProfileSha256s)) errors.push(diagnostic("allowedTransportProfileSha256s", "profile is absent or lists differ"));
  if (dispatcher.bypassPaths.length !== 0 || dispatcher.tokenConsumptionMode !== "atomic-single-use-before-egress" || JSON.stringify(dispatcher.allowedMethods) !== JSON.stringify(["POST"])) errors.push(diagnostic("egressDispatcherContract", "dispatcher is bypassable or method/token policy differs"));
  const times = Object.fromEntries(Object.entries({
    preflight: requestReceipt.preflightAcceptedAt, checkpoint: lease.requestCheckpointIssuedAt,
    activated: lease.activatedAt, observed: attestation.observedAt, leaseExpires: lease.expiresAt,
    attestationExpires: attestation.expiresAt, receiptExpires: requestReceipt.expiresAt,
    dispatcherExpires: dispatcher.expiresAt, networkExpires: network.expiresAt,
  }).map(([name, value]) => [name, Date.parse(value)]));
  if (Object.values(times).some((value) => !Number.isFinite(value))) errors.push(diagnostic("timestamps", "invalid timestamp"));
  else {
    if (!(times.preflight <= times.checkpoint && times.checkpoint <= times.activated && times.activated <= times.observed && times.observed < times.attestationExpires && times.attestationExpires <= times.receiptExpires)) errors.push(diagnostic("timestamps", "dispatch time order differs"));
    if (!(times.activated < times.leaseExpires && times.leaseExpires <= Math.min(times.receiptExpires, times.dispatcherExpires, times.networkExpires))) errors.push(diagnostic("expiresAt", "lease exceeds authority"));
    if (times.leaseExpires - times.activated > 900_000 || times.attestationExpires - times.observed > 30_000 || times.observed - times.checkpoint > dispatcher.maxReceiptAgeSeconds * 1000) errors.push(diagnostic("expiresAt", "maximum duration exceeded"));
  }
  return errors;
}
```

The validator accepts only Plan 11's opaque `authorityContext` and obtains pins, Trusted-Time, full transparency replay, complete Nonce prefix, and challenge-fresh Witness floors exclusively through `readProductionAuthorityContext`. Raw pins, raw replay/transparency maps, a caller time, challenge object, response array, boolean, or status string are not production parameters. The verifier is read-only and receives all chain bytes explicitly. It must never inspect host firewall state itself or claim that a fixture proves real enforcement. The semantic test facade returns `testOnly:true,gateEffective:false`; only a branded context may support a production result.

- [ ] **Step 4: Run enforcement tests and record GREEN**

```powershell
node --test scripts/governance/egress-enforcement.test.mjs
```

Expected: PASS, including one positive chain and every named mutation.

- [ ] **Step 5: Commit the enforcement verifier**

```powershell
git add docs/governance/schemas/network-enforcement-verification.schema.json docs/governance/schemas/egress-dispatcher-contract.schema.json docs/governance/schemas/egress-enforcement-lease.schema.json docs/governance/schemas/egress-dispatch-attestation.schema.json scripts/governance/egress-enforcement.mjs scripts/governance/egress-enforcement.test.mjs scripts/fixtures/governance/external-model/valid-enforcement-chain.json
git commit -m "feat: verify sealed external model egress"
```

### Task 4: Verify wire receipts and byte-identical response capture

**Files:**
- Create: `docs/governance/schemas/egress-transport-receipt.schema.json`
- Create: `docs/governance/schemas/external-model-response-envelope.schema.json`
- Create: `scripts/governance/egress-transport-receipt.mjs`
- Create: `scripts/governance/egress-transport-receipt.test.mjs`
- Create: `scripts/fixtures/governance/external-model/http1-completed-receipt.json`
- Create: `scripts/fixtures/governance/external-model/http2-completed-receipt.json`
- Create: `scripts/fixtures/governance/external-model/aborted-prefix-receipt.json`

- [ ] **Step 1: Write failing transport-evidence tests**

For H1 reject an extra header, duplicate Host, trailer, transfer encoding, and reuse. For H2 reject a foreign stream, missing SETTINGS/ACK prefix, nonempty HPACK state, Huffman use, reordered pseudoheaders, trailer, and identical header-block bytes paired with a different initial HPACK-state hash. For both kinds reject policy-epoch drift, any digest drift, a completed receipt without all timestamps, and an aborted receipt used as output evidence.

- [ ] **Step 2: Run the test and record RED**

```powershell
node --test scripts/governance/egress-transport-receipt.test.mjs
```

Expected: FAIL because `validateTransportReceipt` is missing.

- [ ] **Step 3: Implement discriminated receipt verification**

Export:

```js
export function validateTransportReceipt({ receipt, profile, chain, responseEnvelope, responseBytes, artifactReader, authorityContext }) {
  const authority = readProductionAuthorityContext(authorityContext);
  if (authority.profile !== "gate-evaluation" || authority.gateEffective !== true) throw new TypeError("gate-effective gate-evaluation ProductionAuthorityContext required");
  const errors = validateSchema("egress-transport-receipt", receipt);
  errors.push(...validateSchema("external-model-response-envelope", responseEnvelope));
  if (errors.length) return errors;
  errors.push(...validateTransportProfile(profile));
  errors.push(...validateCommonTransportBindings({ receipt, profile, chain, responseEnvelope, artifactReader, authority }));
  errors.push(...(profile.kind === "http/1.1"
    ? validateHttp1Evidence(receipt.http1Evidence, profile)
    : validateHttp2Evidence(receipt.http2Evidence, profile, artifactReader)));
  const discriminatedEvidence = receipt.http1Evidence ?? receipt.http2Evidence;
  if (sha256Hex(canonicalBytes(discriminatedEvidence)) !== receipt.mandatoryTransportFieldsSha256) errors.push(diagnostic("mandatoryTransportFieldsSha256", "transport evidence projection differs"));
  if (receipt.transportResult !== "completed") errors.push(diagnostic("transportResult", "aborted receipt cannot support output evidence"));
  if (sha256Hex(responseBytes) !== receipt.providerResponseSha256) errors.push(diagnostic("providerResponseSha256", "captured bytes differ"));
  return errors;
}
```

Implement all three called helpers in the same module:

```js
function validateCommonTransportBindings({ receipt, profile, chain, responseEnvelope, artifactReader, authority }) {
  const errors = [];
  const { requestReceipt, dispatchAttestation, enforcementLease, outputEvidence } = chain;
  for (const name of ["requestReceiptId", "dispatchTokenSha256", "providerApplicationRequestSha256", "providerRequestBodySha256", "providerApplicationHeadersSha256", "transportProfileRef", "transportProfileSha256"]) mismatch(errors, name, [receipt[name], requestReceipt[name], dispatchAttestation[name] ?? requestReceipt[name], enforcementLease[name] ?? requestReceipt[name], responseEnvelope[name] ?? requestReceipt[name]]);
  mismatch(errors, "requestReceiptSha256", [receipt.requestReceiptSha256, dispatchAttestation.requestReceiptSha256, enforcementLease.requestReceiptSha256, responseEnvelope.requestReceiptSha256, fullArtifactSha256(requestReceipt)]);
  mismatch(errors, "dispatchAttestationSha256", [receipt.dispatchAttestationSha256, responseEnvelope.dispatchAttestationSha256, fullArtifactSha256(dispatchAttestation)]);
  mismatch(errors, "enforcementLeaseSha256", [receipt.enforcementLeaseSha256, responseEnvelope.egressEnforcementLeaseSha256, fullArtifactSha256(enforcementLease)]);
  if (fullArtifactSha256(profile) !== receipt.transportProfileSha256) errors.push(diagnostic("transportProfileSha256", "profile bytes differ"));
  if (receipt.controlPlaneHandleSha256 !== enforcementLease.controlPlaneHandleSha256) errors.push(diagnostic("controlPlaneHandleSha256", "sealed handle differs"));
  for (const [start, end, expected, path] of [
    [receipt.policyEpochAtStart, receipt.policyEpochAtEnd, enforcementLease.policyEpoch, "policyEpoch"],
    [receipt.networkPolicySha256AtStart, receipt.networkPolicySha256AtEnd, enforcementLease.networkPolicySha256, "networkPolicySha256"],
    [receipt.tokenStorePolicySha256AtStart, receipt.tokenStorePolicySha256AtEnd, enforcementLease.tokenStorePolicySha256, "tokenStorePolicySha256"],
  ]) if (start !== end || start !== expected) errors.push(diagnostic(path, "start/end/lease binding differs"));
  const receiptCoreSha256 = sha256Hex(canonicalBytes(without(receipt, ["receiptCoreSha256", "monitorSignature"])));
  if (receiptCoreSha256 !== receipt.receiptCoreSha256) errors.push(diagnostic("receiptCoreSha256", "receipt core differs"));
  const monitorPin = authority.pins.egressEnforcementMonitor;
  if (!monitorPin || monitorPin.keyRef !== receipt.monitorKeyRef) errors.push(diagnostic("monitorKeyRef", "externally pinned monitor key is absent or differs"));
  else if (!verifyEd25519({ publicKeyBase64url: monitorPin.publicKeyBase64url, payloadBytes: canonicalBytes(without(receipt.monitorSignature, ["signature"])), signatureBase64url: receipt.monitorSignature.signature })) errors.push(diagnostic("monitorSignature", "invalid receipt signature"));
  const runnerPin = authority.transparency.activeKeysByRef[responseEnvelope.runnerKeyRef];
  if (!runnerPin || runnerPin.role !== "ROLE-EXTERNAL-REVIEW-RUNNER" || runnerPin.assigneeSnapshot !== responseEnvelope.runnerAssigneeSnapshot || !verifyEd25519({ publicKeyBase64url: runnerPin.publicKeyBase64url, payloadBytes: canonicalBytes(without(responseEnvelope, ["signature"])), signatureBase64url: responseEnvelope.signature })) errors.push(diagnostic("responseEnvelope.signature", "invalid or unpinned runner signature"));
  if (responseEnvelope.nonce === chain.requestEnvelope.nonce) errors.push(diagnostic("responseEnvelope.nonce", "request/response nonce reuse"));
  if (receipt.wireRequestTranscriptRef && sha256Hex(artifactReader.readBytes(receipt.wireRequestTranscriptRef)) !== receipt.wireRequestTranscriptSha256) errors.push(diagnostic("wireRequestTranscriptSha256", "wire bytes differ"));
  if (receipt.tlsTranscriptRef && sha256Hex(artifactReader.readBytes(receipt.tlsTranscriptRef)) !== receipt.tlsTranscriptSha256) errors.push(diagnostic("tlsTranscriptSha256", "TLS transcript differs"));
  if (fullArtifactSha256(receipt) !== responseEnvelope.egressTransportReceiptSha256) errors.push(diagnostic("egressTransportReceiptSha256", "response Envelope receipt hash differs"));
  if (fullArtifactSha256(responseEnvelope) !== outputEvidence.externalModelOutput.responseEnvelopeSha256) errors.push(diagnostic("responseEnvelopeSha256", "output EVID response Envelope hash differs"));
  if (fullArtifactSha256(chain.requestEnvelope) !== responseEnvelope.requestEnvelopeSha256 || responseEnvelope.requestEnvelopeSha256 !== outputEvidence.externalModelOutput.requestEnvelopeSha256) errors.push(diagnostic("requestEnvelopeSha256", "request Envelope binding differs"));
  mismatch(errors, "providerResponseSha256", [receipt.providerResponseSha256, responseEnvelope.providerResponseSha256, outputEvidence.sha256, outputEvidence.externalModelOutput.providerResponseSha256]);
  if (responseEnvelope.requestSentAt !== receipt.firstRequestByteAt || responseEnvelope.responseReceivedAt !== receipt.lastResponseByteAt) errors.push(diagnostic("responseEnvelope", "response times differ from wire receipt"));
  return errors;
}

function validateHeaderMultimap(entries, expectedNames, path) {
  const errors = [];
  if (JSON.stringify(entries.map(({ name }) => name)) !== JSON.stringify(expectedNames)) errors.push(diagnostic(path, "header name/order differs"));
  entries.forEach((entry, index) => {
    if (entry.ordinal !== index || !Number.isInteger(entry.valueLength) || entry.valueLength < 0 || !/^[0-9a-f]{64}$/.test(entry.valueSha256)) errors.push(diagnostic(`${path}[${index}]`, "invalid closed header evidence"));
  });
  return errors;
}

function validateHttp1Evidence(evidence, profile) {
  const errors = validateHeaderMultimap(evidence.orderedHeaderMultimap, profile.orderedWireHeaderNames, "http1Evidence.orderedHeaderMultimap");
  if (evidence.orderedHeaderMultimap.filter(({ name }) => name === "host").length !== 1) errors.push(diagnostic("http1Evidence", "exactly one Host required"));
  if (evidence.transferEncoding !== null || evidence.connection !== "close" || evidence.trailers.length !== 0 || evidence.connectionReuse !== false) errors.push(diagnostic("http1Evidence", "framing/trailer/reuse mismatch"));
  if (evidence.contentLength < 0 || !Number.isInteger(evidence.contentLength)) errors.push(diagnostic("http1Evidence.contentLength", "invalid Content-Length"));
  return errors;
}

function validateHttp2Evidence(evidence, profile, artifactReader) {
  const errors = [];
  const emptyHpackStateSha256 = sha256Hex(canonicalBytes({ dynamicTable: [], dynamicTableSize: 0 }));
  for (const [path, actual, expected] of [
    ["streamId", evidence.streamId, 1], ["exclusiveSingleStream", evidence.exclusiveSingleStream, true],
    ["hpackDynamicTableSizeAtStart", evidence.hpackDynamicTableSizeAtStart, 0], ["hpackDynamicTableSizeAtEnd", evidence.hpackDynamicTableSizeAtEnd, 0],
    ["hpackInitialStateSha256", evidence.hpackInitialStateSha256, emptyHpackStateSha256], ["hpackFinalStateSha256", evidence.hpackFinalStateSha256, emptyHpackStateSha256],
    ["connectionReuse", evidence.connectionReuse, false],
  ]) if (actual !== expected) errors.push(diagnostic(`http2Evidence.${path}`, `must equal ${String(expected)}`));
  if (JSON.stringify(evidence.orderedPseudoHeaders.map(({ name }) => name)) !== JSON.stringify(profile.http2.pseudoHeaderOrder)) errors.push(diagnostic("http2Evidence.orderedPseudoHeaders", "pseudoheader order differs"));
  errors.push(...validateHeaderMultimap(evidence.orderedHeaderMultimap, profile.orderedWireHeaderNames, "http2Evidence.orderedHeaderMultimap"));
  if (evidence.orderedPseudoHeaders.filter(({ name }) => name === ":authority").length !== 1 || evidence.trailers.length !== 0) errors.push(diagnostic("http2Evidence", "authority/trailer mismatch"));
  for (const [refName, hashName] of [["connectionPrefaceRef", "connectionPrefaceSha256"], ["clientSettingsRef", "clientSettingsSha256"], ["serverSettingsRef", "serverSettingsSha256"], ["settingsAckRef", "settingsAckSha256"]]) {
    if (sha256Hex(artifactReader.readBytes(evidence[refName])) !== evidence[hashName]) errors.push(diagnostic(`http2Evidence.${hashName}`, "referenced bytes differ"));
  }
  return errors;
}
```

Always check `receipt.mandatoryTransportFieldsSha256 === sha256Hex(canonicalBytes(receipt.http1Evidence ?? receipt.http2Evidence))`; add that assertion immediately after the discriminated helper call. Use the shared structured diagnostic constructor from `diagnostics.mjs`; do not throw for contract failures. The response EVID `sha256`, receipt `providerResponseSha256`, and response-envelope digest must be byte-identical. The schemas require every nullable transport/timestamp/hash field to be non-null for `completed`; an aborted receipt can bind only a captured prefix and cannot support output evidence.

- [ ] **Step 4: Run the tests and record GREEN**

```powershell
node --test scripts/governance/egress-transport-receipt.test.mjs
```

Expected: PASS with zero failures.

- [ ] **Step 5: Commit wire-receipt verification**

```powershell
git add docs/governance/schemas/egress-transport-receipt.schema.json docs/governance/schemas/external-model-response-envelope.schema.json scripts/governance/egress-transport-receipt.mjs scripts/governance/egress-transport-receipt.test.mjs scripts/fixtures/governance/external-model/http1-completed-receipt.json scripts/fixtures/governance/external-model/http2-completed-receipt.json scripts/fixtures/governance/external-model/aborted-prefix-receipt.json
git commit -m "feat: verify external model wire receipts"
```

### Task 5: Integrate the chain into governance evidence replay

**Files:**
- Modify: `docs/governance/governance.schema.json`
- Modify: `scripts/governance/schema-validator.test.mjs`
- Modify: `scripts/governance/reviews-evidence-gates.mjs`
- Modify: `scripts/governance-contract.mjs`
- Modify: `scripts/governance-contract.test.mjs`
- Modify: `package.json`

- [ ] **Step 1: Add a failing full-chain contract test**

Build a repository fixture with an externally accepted Expected predecessor and a distinct Captured successor created only after the full valid chain. Its Capture EVT binds the two exact record hashes. Clone it into one mutation per binding: provider, endpoint, model, region, retention, training, sanitizer, input, dispatcher, receipt, token, lease, transport, raw response, runner key, scope, subject, baseline, Expected acceptance, Capture acceptance, previous record hash, resulting record hash, and future/self-hash injection. Assert the valid fixture yields `[]` and every mutation yields an error containing its field path.

- [ ] **Step 2: Run the integration test and record RED**

```powershell
node --test --test-name-pattern="external model" scripts/governance-contract.test.mjs
```

Expected: FAIL because `governanceErrors` does not yet call the external-model validators. The fixture run is semantic only and must carry `gateEffective: false`; the production entry point rejects test-only verification injection.

- [ ] **Step 3: Wire the validators into the evidence lifecycle**

Export the complete production composition from `external-model-contract.mjs`. The adapter resolves every reference from the immutable artifact reader/replay prefix and never accepts a verifier callback:

```js
const productionExternalModelResults = new WeakSet();

function finishProductionExternalModelResult(errors, authorityRequired = []) {
  const authority = [...new Set(authorityRequired)];
  const result = Object.freeze({ errors, authorityRequired: authority, testOnly: false,
    gateEffective: errors.length === 0 && authority.length === 0 });
  productionExternalModelResults.add(result);
  return result;
}

function containsScalar(value, needle) {
  if (value === needle) return true;
  if (Array.isArray(value)) return value.some((item) => containsScalar(item, needle));
  if (value && typeof value === "object") return Object.values(value).some((item) => containsScalar(item, needle));
  return false;
}

function validateCapturedOutputBindings({ capturedOutputEvidence, requestEnvelope, requestReceipt, enforcementLease, dispatchAttestation, receipt, responseEnvelope }) {
  const errors = [];
  const output = capturedOutputEvidence.externalModelOutput;
  for (const name of ["providerName", "endpointClass", "endpointIdentifierSha256", "modelVersion", "processingRegion", "retentionPolicy", "trainingUse", "inputArtifactSha256", "inputClassification", "sanitizerRole", "sanitizerAssigneeSnapshot", "sanitizationEvidenceRef", "dueDiligenceEvidenceRef", "egressDispatcherContractEvidenceRef", "expectedEvidenceRecordSha256", "requestDescriptorSha256", "providerApplicationRequestRef", "providerApplicationRequestSha256", "providerRequestBodySha256", "providerApplicationHeadersSha256", "transportProfileRef", "transportProfileSha256", "runnerRole", "runnerAssigneeSnapshot"]) {
    mismatch(errors, name, [output[name], requestEnvelope[name]]);
  }
  mismatch(errors, "requestReceiptId", [output.requestReceiptId, requestReceipt.requestReceiptId, enforcementLease.requestReceiptId, dispatchAttestation.requestReceiptId, receipt.requestReceiptId, responseEnvelope.requestReceiptId]);
  mismatch(errors, "requestReceiptSha256", [output.requestReceiptSha256, fullArtifactSha256(requestReceipt), enforcementLease.requestReceiptSha256, dispatchAttestation.requestReceiptSha256, receipt.requestReceiptSha256, responseEnvelope.requestReceiptSha256]);
  mismatch(errors, "dispatchAttestationSha256", [output.dispatchAttestationSha256, fullArtifactSha256(dispatchAttestation), receipt.dispatchAttestationSha256, responseEnvelope.dispatchAttestationSha256]);
  mismatch(errors, "egressEnforcementLeaseSha256", [output.egressEnforcementLeaseSha256, fullArtifactSha256(enforcementLease), dispatchAttestation.enforcementLeaseSha256, receipt.enforcementLeaseSha256, responseEnvelope.egressEnforcementLeaseSha256]);
  mismatch(errors, "egressTransportReceiptSha256", [output.egressTransportReceiptSha256, fullArtifactSha256(receipt), responseEnvelope.egressTransportReceiptSha256]);
  mismatch(errors, "requestEnvelopeSha256", [output.requestEnvelopeSha256, fullArtifactSha256(requestEnvelope), responseEnvelope.requestEnvelopeSha256]);
  mismatch(errors, "responseEnvelopeSha256", [output.responseEnvelopeSha256, fullArtifactSha256(responseEnvelope)]);
  mismatch(errors, "providerResponseSha256", [output.providerResponseSha256, receipt.providerResponseSha256, responseEnvelope.providerResponseSha256, capturedOutputEvidence.sha256]);
  mismatch(errors, "providerRequestIdSha256", [output.providerRequestIdSha256, responseEnvelope.providerRequestIdSha256]);
  mismatch(errors, "wireRequestTranscriptSha256", [output.wireRequestTranscriptSha256, receipt.wireRequestTranscriptSha256, responseEnvelope.wireRequestTranscriptSha256]);
  mismatch(errors, "tlsTranscriptSha256", [output.tlsTranscriptSha256, receipt.tlsTranscriptSha256, responseEnvelope.tlsTranscriptSha256]);
  mismatch(errors, "requestSentAt", [output.requestSentAt, responseEnvelope.requestSentAt, receipt.firstRequestByteAt]);
  mismatch(errors, "responseReceivedAt", [output.responseReceivedAt, responseEnvelope.responseReceivedAt, receipt.lastResponseByteAt]);
  if (output.dispatchAttestationRef !== responseEnvelope.dispatchAttestationRef || output.egressEnforcementLeaseRef !== responseEnvelope.egressEnforcementLeaseRef || output.egressTransportReceiptRef !== responseEnvelope.egressTransportReceiptRef || output.responseEnvelopeRef === output.requestEnvelopeRef) errors.push(diagnostic("artifactRefs", "closed chain references differ or alias"));
  return errors;
}

export function validateExternalModelEvidenceChain({
  expectedOutputEvidence,
  capturedOutputEvidence,
  captureEvent,
  authorityContext,
  artifactReader,
}) {
  const authority = readProductionAuthorityContext(authorityContext);
  if (authority.profile !== "gate-evaluation" || authority.gateEffective !== true) throw new TypeError("gate-effective gate-evaluation ProductionAuthorityContext required");
  const errors = [];
  const output = capturedOutputEvidence.externalModelOutput;
  const evidenceById = authority.transparency.evidenceById;
  const dueDiligenceEvidence = evidenceById[output.dueDiligenceEvidenceRef];
  const sanitizationEvidence = evidenceById[output.sanitizationEvidenceRef];
  const dispatcherEvidence = evidenceById[output.egressDispatcherContractEvidenceRef];
  for (const [path, value] of [["dueDiligenceEvidenceRef", dueDiligenceEvidence], ["sanitizationEvidenceRef", sanitizationEvidence], ["egressDispatcherContractEvidenceRef", dispatcherEvidence]]) {
    if (!value) errors.push(diagnostic(path, "referenced EVID is absent"));
  }
  if (errors.length) return finishProductionExternalModelResult(errors);
  const read = (kind, ref, path) => {
    try { return kind === "json" ? artifactReader.readJson(ref) : artifactReader.readBytes(ref); }
    catch { errors.push(diagnostic(path, "referenced immutable artifact is absent or unreadable")); return null; }
  };
  const requestEnvelope = read("json", output.requestEnvelopeRef, "requestEnvelopeRef");
  const requestReceipt = authority.transparency.entriesByReceiptId[output.requestReceiptId];
  const enforcementLease = read("json", output.egressEnforcementLeaseRef, "egressEnforcementLeaseRef");
  const requestCheckpoint = authority.transparency.checkpointsBySha256[enforcementLease?.requestCheckpointSha256];
  const dispatchAttestation = read("json", output.dispatchAttestationRef, "dispatchAttestationRef");
  const receipt = read("json", output.egressTransportReceiptRef, "egressTransportReceiptRef");
  const responseEnvelope = read("json", output.responseEnvelopeRef, "responseEnvelopeRef");
  const profile = read("json", output.transportProfileRef, "transportProfileRef");
  const responseBytes = read("bytes", capturedOutputEvidence.artifactPathOrUri, "artifactPathOrUri");
  if (!requestReceipt) errors.push(diagnostic("requestReceiptId", "receipt is absent from verified log prefix"));
  if (!requestCheckpoint) errors.push(diagnostic("requestCheckpointSha256", "full-quorum request checkpoint is absent"));
  if (errors.length) return finishProductionExternalModelResult(errors);
  const expectedRecordSha256 = fullArtifactSha256(expectedOutputEvidence);
  const capturedRecordSha256 = fullArtifactSha256(capturedOutputEvidence);
  if (expectedOutputEvidence.id !== capturedOutputEvidence.id || expectedOutputEvidence.status !== "expected" || capturedOutputEvidence.status !== "captured") errors.push(diagnostic("capturedOutputEvidence", "expected→captured identity/status transition differs"));
  if (expectedOutputEvidence.externalModelOutput !== null) errors.push(diagnostic("expectedOutputEvidence.externalModelOutput", "future output data exists before dispatch"));
  if (captureEvent.recordRef !== capturedOutputEvidence.id || captureEvent.eventKind !== "transition" || captureEvent.previousRecordSha256 !== expectedRecordSha256 || captureEvent.resultingRecordSha256 !== capturedRecordSha256) errors.push(diagnostic("captureEvent", "Capture EVT predecessor/result hash binding differs"));
  if (output.expectedEvidenceRecordSha256 !== expectedRecordSha256 || requestEnvelope.expectedEvidenceRecordSha256 !== expectedRecordSha256 || requestReceipt.expectedEvidenceRecordSha256 !== expectedRecordSha256) errors.push(diagnostic("expectedEvidenceRecordSha256", "chain does not bind the accepted expected predecessor"));
  if (requestEnvelope.externalOutputEvidenceRef !== expectedOutputEvidence.id || requestReceipt.externalOutputEvidenceRef !== expectedOutputEvidence.id) errors.push(diagnostic("externalOutputEvidenceRef", "request chain does not identify expected predecessor"));
  const preCaptureArtifacts = [requestEnvelope, requestReceipt, enforcementLease, dispatchAttestation, receipt, responseEnvelope];
  if (preCaptureArtifacts.some((artifact) => containsScalar(artifact, capturedRecordSha256) || containsScalar(artifact, captureEvent.eventHash))) errors.push(diagnostic("captureCycle", "chain artifact binds a future Capture record/Event hash"));
  if (!authority.acceptanceReceipts.acceptedRecordHashes.includes(expectedRecordSha256) || !authority.acceptanceReceipts.acceptedEventHashes.includes(captureEvent.eventHash)) errors.push(diagnostic("acceptanceReceipts", "expected predecessor or Capture EVT lacks external acceptance"));
  errors.push(...validateExternalModelPreflight({
    expectedOutputEvidence, dueDiligenceEvidence, sanitizationEvidence, dispatcherEvidence,
    requestEnvelope, requestReceipt, authorityContext,
  }));
  errors.push(...validateCapturedOutputBindings({ capturedOutputEvidence, requestEnvelope, requestReceipt, enforcementLease, dispatchAttestation, receipt, responseEnvelope }));
  const enforcement = validateEgressEnforcement({
    networkEvidence: evidenceById[dispatcherEvidence.egressDispatcherContract.networkEnforcementEvidenceRef],
    dispatcherEvidence, requestEnvelope, requestReceipt, requestCheckpoint, enforcementLease,
    dispatchAttestation, authorityContext,
  });
  errors.push(...enforcement.errors);
  errors.push(...validateTransportReceipt({
    receipt, profile,
    chain: { requestReceipt, requestEnvelope, dispatchAttestation, enforcementLease, outputEvidence: capturedOutputEvidence },
    responseEnvelope, responseBytes, artifactReader, authorityContext,
  }));
  return finishProductionExternalModelResult(errors, enforcement.authorityRequired);
}

export function assertGateEffectiveExternalModelResult(result) {
  if (!productionExternalModelResults.has(result) || result.testOnly || !result.gateEffective) {
    throw new TypeError("external-model result is not production gate-effective");
  }
  return result;
}
```

Add one RED mutation per lookup and for expected/captured aliasing, wrong predecessor hash, wrong resulting hash, absent Expected acceptance, absent Capture-EVT acceptance, an Envelope containing the captured-record hash, and any artifact containing a future Capture-Event hash. `expectedOutputEvidence` is immutable and externally accepted before Envelope creation; `capturedOutputEvidence` is constructed only after the completed response/transport chain. The Envelope binds only the Expected predecessor's full hash. The Capture EVT alone binds `previousRecordSha256=fullArtifactSha256(expectedOutputEvidence)` and `resultingRecordSha256=fullArtifactSha256(capturedOutputEvidence)`. Nothing before capture contains the captured record hash, Capture Event hash, future commit, or its own hash.

In `reviews-evidence-gates.mjs`, dispatch by evidence type and preserve the authority result rather than spreading an object as an array:

```js
if (evidence.evidenceType === "external-model-output") {
  const result = validateExternalModelEvidenceChain({
    expectedOutputEvidence: transition.previousRecord,
    capturedOutputEvidence: evidence,
    captureEvent: transition.event,
    authorityContext: options.authorityContext,
    artifactReader: options.artifactReader,
  });
  errors.push(...result.errors);
  authorityRequired.push(...result.authorityRequired);
  if (!result.gateEffective) gateEffective = false;
}
```

`transition.previousRecord` and `transition.event` come from Plan 03's already validated adjacent replay, not from caller-supplied hooks. Require `external-model-request-receipt` in the verified full log prefix and reject its use before a full-quorum checkpoint. Production integration accepts only the opaque Plan-11 context and calls `readProductionAuthorityContext`; raw `replayState`, `transparencyState`, pins, Trusted-Time strings/results, booleans, or callbacks are absent from its signature. Add no network code and no provider SDK dependency.

For Plan 11 issuer Phase A, this module also exposes one import-allowlisted non-injectable candidate wrapper that runs the same closed chain over artifact bytes and the issuer-provided module-branded pin/time/transparency/floor/branch/Nonce/Receipt subresults. It returns a module-private branded `semanticValid:true,gateEffective:false,authorityRequired:["production-authority-context"]` result and never accepts raw state or a test facade. Only `production-authority-context.mjs` and this module's tests may import its brand guard. Normal production/Gate integration still requires `readProductionAuthorityContext` and the `gate-evaluation` profile above.

In the EVID status validator, close the only allowed field-shape change for this type: `expected→captured` changes `externalModelOutput` from `null` to the closed captured object and populates capture-only producer/artifact fields; every other immutable EVID field stays byte-identical. No expected record may contain provider-response, transport-receipt, Capture-Event, resulting-record, or future-commit data. No captured record may change the `expectedEvidenceRecordSha256` that was bound by the Envelope/Receipt.

- [ ] **Step 4: Run targeted and full local gates**

```powershell
node --test --test-name-pattern="external model" scripts/governance-contract.test.mjs
npm test
```

Expected: targeted tests and `npm test` exit 0; the external-model tests execute rather than being skipped. Then run the real pre-Genesis check separately:

```powershell
$preGenesisOutput = & npm run check:governance -- --pre-genesis 2>&1
$preGenesisExit = $LASTEXITCODE
$preGenesisText = $preGenesisOutput -join "`n"
$preGenesisResult = $null
try {
  $jsonStart = $preGenesisText.IndexOf('{')
  $jsonEnd = $preGenesisText.LastIndexOf('}')
  if ($jsonStart -lt 0 -or $jsonEnd -lt $jsonStart) { throw 'missing JSON result' }
  $preGenesisResult = $preGenesisText.Substring($jsonStart, $jsonEnd - $jsonStart + 1) | ConvertFrom-Json -ErrorAction Stop
} catch {}
$preGenesisAuthority = @($preGenesisResult.authorityRequired)
$preGenesisMismatch = $preGenesisExit -isnot [int] -or $preGenesisExit -eq 0 -or $null -eq $preGenesisResult
$preGenesisMismatch = $preGenesisMismatch -or $preGenesisResult.status -cne 'AUTHORITY-RED/PRE-GENESIS'
$preGenesisMismatch = $preGenesisMismatch -or $preGenesisResult.gateEffective -isnot [bool] -or $preGenesisResult.gateEffective
$preGenesisMismatch = $preGenesisMismatch -or $preGenesisAuthority.Count -ne 1 -or $preGenesisAuthority[0] -cne 'GENESIS'
if ($preGenesisMismatch) {
  throw 'pre-Genesis governance result was not exact AUTHORITY-RED/PRE-GENESIS with gateEffective=false and authorityRequired=[GENESIS]'
}
```

Expected before Plan 12: the npm command itself is nonzero, while the enclosing
PowerShell assertion succeeds only for the exact structured
`AUTHORITY-RED/PRE-GENESIS`, `gateEffective:false`,
`authorityRequired:["GENESIS"]` result. The real Genesis registers and external
authority do not yet exist. No other contract diagnostic is accepted. Do not
turn this authority-red state into a synthetic success mode, and do not record
the semantic fixtures as gate evidence.

- [ ] **Step 5: Commit integration**

```powershell
git add docs/governance/governance.schema.json scripts/governance/schema-validator.test.mjs scripts/governance/reviews-evidence-gates.mjs scripts/governance-contract.mjs scripts/governance-contract.test.mjs package.json
git commit -m "feat: enforce external model evidence chain"
```

### Task 6: Review and close Plan 09

**Files:** No intended source changes; review corrections use the exact files listed by the finding.

- [ ] **Step 1: Run the sequential evidence gates**

```powershell
npm run check:canon
npm run typecheck:governance
npm run typecheck
npm run lint
npm test
if ($env:AURELIA_PLAN09_BASE_SHA -notmatch '^[0-9a-f]{40}$') { throw 'AUTHORITY-RED: Plan 09 base SHA absent' }
git diff --check "$env:AURELIA_PLAN09_BASE_SHA..HEAD"
```

Expected: each listed command exits 0 in this order. Run `npm run check:governance` immediately afterward; before Genesis it must exit nonzero with only `AUTHORITY-RED`. A zero exit before the real authority inputs exist is a P0 failure.

- [ ] **Step 2: Perform independent Spec Review**

Review every Plan-09 commit against design sections 6.3, 6.4, 10, and 12.4. The reviewer must be distinct from the implementer and orchestrator. Expected verdict: `approved` with no open P0-P2.

- [ ] **Step 3: Perform independent Quality/Security Review**

Require explicit attacks for direct host/runner egress, token reuse, stale floors, policy drift, credential logging, H1/H2 ambiguity, HPACK-state confusion, response substitution, and an external model impersonating a reviewer. Expected verdict: `approved` with no open P0-P2.

- [ ] **Step 4: Re-run both reviews after any correction**

For every correction, run its focused RED/GREEN test, commit it with `fix: close external model review finding`, then repeat both reviews for the affected scope. Do not dismiss a P0-P2 without a successor review and verified correction evidence.

- [ ] **Step 5: Record the Plan-09 boundary**

The handoff must say: contracts and synthetic tests are complete; no external provider, model, credential, remote repository, or production context was contacted; no output EVID is gate-effective without later external receipts and pins.
