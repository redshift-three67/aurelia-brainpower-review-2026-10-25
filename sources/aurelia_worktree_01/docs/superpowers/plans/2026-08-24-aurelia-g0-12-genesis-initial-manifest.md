# AURELIA G0 12 Genesis and Initial Manifest Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Freeze the reviewed governance implementation, obtain the required offline signatures and external pins, and create the one valid initial Governance Genesis while keeping all nine gates red.

**Architecture:** The sequence is immutable: final design commit `D` -> separately reviewed implementation commit `I` -> offline final-design and dual pre-ledger signatures -> one Genesis commit `G`. Constructors, the closed ceremony CLI, its transactional writer, and seed generation are tested before `I`; the signed bootstrap artifacts, four registers, trust roots, detached attestations, and all initial records enter only in `G`, whose `baseCommit` is exactly `I`. No synthetic key, test fixture, chat approval, repository-controlled pin, ad-hoc Node expression, or later commit may substitute for the offline ceremony.

**Tech Stack:** Node.js 22 ESM, `node:test`, Git object inspection, JSON Schema Draft 2020-12, RFC 8785, SHA-256, Ed25519, existing bootstrap/transparency/ledger validators.

---

## Fixed design anchors

```text
designBaselineCommit = b20ee873347c5fd767e2089c993f1cf93a625def
designCommit = a6a8e7dca456d14a6748b204b787b235fdedf9be
designSpecPath = docs/superpowers/specs/2026-08-24-aurelia-g0-governance-design.md
designSpecSha256 = 30c7484753972020dec25083e038a2a1a6ab15a0b3f8885579ce4fa6e3727eb1
repositoryId = redshift-three67/aurelia
```

The implementation freeze is the full 40-character `I` SHA recorded in the separately protected external execution record. This plan deliberately creates no repository-local `implementation-freeze.json`: such a file would be a movable, repository-controlled assertion and is not a design-defined authority. Session environment variables are convenience copies only.

The required approval text is exactly:

```text
AURELIA G0-Spezifikation a6a8e7dca456d14a6748b204b787b235fdedf9be mit Dateihash 30c7484753972020dec25083e038a2a1a6ab15a0b3f8885579ce4fa6e3727eb1 final freigegeben
```

The user's chat phrase authorizes planning but is not this Ed25519 artifact.

### Task 1: Prove the design anchors and build unsigned bootstrap constructors

**Files:**
- Create: `scripts/governance/bootstrap-artifacts.mjs`
- Create: `scripts/governance/bootstrap-artifacts.test.mjs`
- Modify: `scripts/governance/bootstrap-validator-internal.mjs`
- Modify: `scripts/governance/bootstrap-validator.mjs`
- Modify: `scripts/governance/bootstrap-validator.test.mjs`
- Create: `scripts/fixtures/governance/bootstrap/final-design-approval-core.json`
- Create: `scripts/fixtures/governance/bootstrap/pre-ledger-core.json`

- [ ] **Step 1: Capture the pre-Plan-12 review base**

```powershell
$plan12BaseSha = git rev-parse HEAD
if ($plan12BaseSha -notmatch '^[0-9a-f]{40}$') { throw 'Plan 12 base is not a full commit SHA' }
if (-not $env:AURELIA_EXECUTION_RECORD_PATH) { throw 'AUTHORITY-RED: protected execution-record path absent' }
if (Test-Path -LiteralPath $env:AURELIA_EXECUTION_RECORD_PATH) {
  $record = Get-Content -Raw -LiteralPath $env:AURELIA_EXECUTION_RECORD_PATH | ConvertFrom-Json
  if ($record.plan12BaseSha -and $record.plan12BaseSha -ne $plan12BaseSha) { throw 'AUTHORITY-RED: Plan 12 base conflicts with protected record' }
}
$env:AURELIA_PLAN12_BASE_SHA = $plan12BaseSha
$plan12BaseSha
```

Expected: the full SHA is printed and the separately protected execution record either agrees or has an externally authorized empty `plan12BaseSha` field for the operator to fill. Do not create a movable branch or treat the environment variable as the protected record.

- [ ] **Step 2: Write failing anchor and projection tests**

Assert that `git diff --name-only b20ee873347c5fd767e2089c993f1cf93a625def..a6a8e7dca456d14a6748b204b787b235fdedf9be` returns only the design path, `git show` returns the exact spec bytes, and their SHA-256 is the fixed digest above. Require these exports:

```js
export function buildFinalDesignApprovalCore(input) {}
export function assembleFinalDesignApproval({ core, signatureBase64url, externalPins, repositoryRoot, implementationCommit, productionAuthorityContext }) {}
export function buildPreLedgerCore(input) {}
export function assemblePreLedgerBundle({ core, operatorSigningRecord, recoveryRootSigningRecord, externalPins, productionAuthorityContext, bootstrapValidationContext }) {}
export function assertFreshCandidateNonces(productionAuthorityContext, implementationCommit, externalPins, expectedPhase, expectedDomainState, occurredAt, candidateNonces) {}
export function assertValidationResult(result, label) {}
```

The constructors consume the single `ProductionAuthorityContext` brand defined
in Plans 06/11, specifically its closed `profile:"pre-genesis-ceremony"` form.
Plan 11 creates that non-gate-effective profile only after the complete raw
artifact prefix, externally signed count/head inventory, independently signed
pins and Trusted-Time have verified. Its claims include exact local `I`, the
Plan-06 `noncePrefixSha256` and canonical occupied nonce set. Remote Receipt,
Branch-control and fresh-floor requirements belong to the distinct
`profile:"gate-evaluation"`; requiring them here would create an I→Receipt→G
cycle. Plan 12 must reject that Gate profile as well as an unbranded object.
Each ceremony assembly command invokes the issuer and constructor in the same
Node process; a prior CLI's JSON output cannot carry the WeakMap brand. On a
later signing step all raw inputs are reloaded and reverified to mint a fresh
context.
At the D-to-I pre-Genesis boundary, zero repository Events/attestations are
authoritative only when the externally signed inventory binds those zero
counts and exact I. Its signed phase advances from `before-final-approval` to
`before-pre-ledger` and `before-genesis` as those two external public ceremony
artifacts are verified; this never changes the zero repository state of I.
Tests cover omitted domains, false-empty inventories, invalid heads/time/
signatures, unknown nonce-like fields, reuse, copied/plain-object context
forgery and stale context head. Unit fixtures contain no private key.

- [ ] **Step 3: Run and record RED**

```powershell
node --test scripts/governance/bootstrap-artifacts.test.mjs
```

Expected: FAIL because the constructor exports do not exist.

- [ ] **Step 4: Implement exact closed projections**

First add these complete internal helpers; `canonicalBytes`, `sha256Hex`, `verifyEd25519`, and `validateSchema` are stable exports from Plans 02 and 05:

```js
import { canonicalBytes } from "./rfc8785.mjs";
import { sha256Hex, verifyEd25519 } from "./crypto.mjs";
import { validateSchema } from "./schema-registry.mjs";
import { validatePreLedgerCandidate } from "./bootstrap-validator.mjs";
import { readProductionAuthorityContext } from "./production-authority-context.mjs";
import { execFileSync } from "node:child_process";

function assertClosedObject(value, fields, label) {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new TypeError(`${label} must be an object`);
  const actual = Object.keys(value).sort();
  const expected = [...fields].sort();
  if (JSON.stringify(actual) !== JSON.stringify(expected)) throw new Error(`${label} has non-contract fields`);
}

function assertBase64urlBytes(value, bytes, label) {
  if (typeof value !== "string" || !/^[A-Za-z0-9_-]+$/.test(value) || value.includes("=")) throw new Error(`${label} is not unpadded Base64url`);
  const decoded = Buffer.from(value, "base64url");
  if (decoded.length !== bytes || decoded.toString("base64url") !== value) throw new Error(`${label} is not canonical ${bytes}-byte Base64url`);
}

export function assertValidationResult(result, label) {
  const diagnostics = Array.isArray(result) ? result : (result?.diagnostics ?? result?.errors ?? []);
  const authorityRequired = Array.isArray(result?.authorityRequired) ? result.authorityRequired : [];
  const resultObjectNeedsAuthority = result && !Array.isArray(result) && Object.prototype.hasOwnProperty.call(result, "gateEffective");
  if (result === false || result?.ok === false || diagnostics.length || authorityRequired.length || (resultObjectNeedsAuthority && result.gateEffective !== true) || result?.testOnly === true) throw new Error(`${label} failed: ${JSON.stringify({ diagnostics, authorityRequired, gateEffective: result?.gateEffective, testOnly: result?.testOnly })}`);
}

function assertImplementationTreePreGenesis(repositoryRoot, implementationCommit) {
  const paths = execFileSync("git", ["ls-tree", "-r", "--name-only", implementationCommit], { cwd: repositoryRoot, encoding: "utf8" }).trim().split(/\r?\n/).filter(Boolean);
  const forbiddenFiles = new Set([
    "docs/governance/traceability-register.md",
    "docs/governance/risk-register.md",
    "docs/governance/data-processing-inventory.md",
    "docs/governance/gate-register.md",
    "docs/governance/trust-roots.json",
  ]);
  const forbiddenPrefixes = [
    "docs/governance/bootstrap/",
    "docs/governance/attestations/",
    "docs/governance/evidence/",
    "docs/governance/manifests/",
  ];
  for (const path of paths) {
    if (forbiddenFiles.has(path) || forbiddenPrefixes.some((prefix) => path.startsWith(prefix))) {
      throw new Error(`I contains pre-Genesis authority artifact ${path}`);
    }
  }
}

export function assertFreshCandidateNonces(productionAuthorityContext, implementationCommit, externalPins,
  expectedPhase, expectedDomainHeads, candidateTime, candidateNonces) {
  const claims = readProductionAuthorityContext(productionAuthorityContext);
  const domainById = Object.fromEntries(claims.governanceDomainState?.domains?.map((domain) => [domain.domainId, domain]) ?? []);
  if (claims.profile !== "pre-genesis-ceremony" || claims.gateEffective !== false
    || claims.repositoryId !== "redshift-three67/aurelia"
    || claims.implementationCommit !== implementationCommit
    || claims.externalPinsSha256 !== sha256Hex(canonicalBytes(externalPins))
    || claims.governanceDomainState?.phase !== expectedPhase
    || claims.trustedTime?.now !== candidateTime
    || !/^[0-9a-f]{64}$/.test(claims.noncePrefixSha256)
    || !Array.isArray(claims.occupiedNonces)) {
    throw new Error("production authority context does not bind exact I, phase, trusted time, and nonce prefix");
  }
  for (const [domainId, expected] of Object.entries(expectedDomainHeads)) {
    const actual = domainById[domainId];
    if (!actual || actual.artifactCount !== expected.artifactCount || actual.headSha256 !== expected.headSha256) {
      throw new Error(`production authority context has wrong ${domainId} phase head`);
    }
  }
  candidateNonces.forEach((nonce, index) => assertBase64urlBytes(nonce, 32, `candidateNonce[${index}]`));
  if (candidateNonces.some((nonce) => claims.occupiedNonces.includes(nonce))) throw new Error("candidate nonce was already used");
  if (new Set(candidateNonces).size !== candidateNonces.length) throw new Error("ceremony candidates reuse a nonce");
}
```

`buildFinalDesignApprovalCore` must call `assertClosedObject(input, ["schemaVersion","operatorKeyRef","operatorKeyFingerprint","issuedAt","nonce"], "finalDesignApprovalInput")` and return exactly these fields and no signature:

```js-fragment
return Object.freeze({
  schemaVersion: input.schemaVersion,
  repositoryId: "redshift-three67/aurelia",
  approvalText: "AURELIA G0-Spezifikation a6a8e7dca456d14a6748b204b787b235fdedf9be mit Dateihash 30c7484753972020dec25083e038a2a1a6ab15a0b3f8885579ce4fa6e3727eb1 final freigegeben",
  designCommit: "a6a8e7dca456d14a6748b204b787b235fdedf9be",
  designSpecPath: "docs/superpowers/specs/2026-08-24-aurelia-g0-governance-design.md",
  designSpecSha256: "30c7484753972020dec25083e038a2a1a6ab15a0b3f8885579ce4fa6e3727eb1",
  approvalScope: "AURELIA-G0-GOVERNANCE-DESIGN",
  operatorIdentity: "redshift-three67",
  operatorRole: "ROLE-OPERATOR",
  operatorKeyRef: input.operatorKeyRef,
  operatorKeyFingerprint: input.operatorKeyFingerprint,
  method: "ed25519",
  issuedAt: input.issuedAt,
  nonce: input.nonce,
});
```

Implement the production assemblies and Pre-Ledger projection exactly as follows:

```js
export function assembleFinalDesignApproval({ core, signatureBase64url, externalPins, repositoryRoot, implementationCommit, productionAuthorityContext }) {
  assertImplementationTreePreGenesis(repositoryRoot, implementationCommit);
  assertFreshCandidateNonces(productionAuthorityContext, implementationCommit, externalPins,
    "before-final-approval", {
      "design-approval": { artifactCount: 0, headSha256: null },
      bootstrap: { artifactCount: 0, headSha256: null },
    }, core.issuedAt, [core.nonce]);
  if (core.operatorIdentity !== "redshift-three67" || core.operatorRole !== "ROLE-OPERATOR" || core.operatorKeyRef !== externalPins.operatorKey.keyRef || core.operatorKeyFingerprint !== externalPins.operatorKey.fingerprintSha256) throw new Error("final approval operator pin mismatch");
  const payloadBytes = canonicalBytes(core);
  if (!verifyEd25519({ publicKeyBase64url: externalPins.operatorKey.publicKeyBase64url, payloadBytes, signatureBase64url })) throw new Error("final design approval signature invalid");
  const artifact = Object.freeze({ ...core, signature: signatureBase64url });
  assertValidationResult(validateSchema("final-design-approval", artifact), "final-design-approval schema");
  return artifact;
}

const PRE_LEDGER_FIELDS = Object.freeze([
  "schemaVersion", "repositoryId", "designBaselineCommit", "designCommit", "designSpecPath", "designSpecSha256",
  "governanceImplementationCommit", "operatorKey", "recoveryRootKey", "orchestratorKey", "validatorControllerKey",
  "recoveryApp", "recoveryWriteAheadGateway", "providerRefVerifier", "egressEnforcementMonitor", "transparencyInstanceKey",
  "witnessKeys", "finalApprovalPath", "finalApprovalSha256", "bootstrapValidatorImageDigest", "bootstrapValidatorPolicySha256",
  "bootstrapWorkflowSha256", "bootstrapSchemaSetSha256", "bootstrapTrustProtocolSha256", "genesisEventIds", "issuedAt", "nonce",
]);

export function buildPreLedgerCore(input) {
  assertClosedObject(input, PRE_LEDGER_FIELDS, "preLedgerCoreInput");
  const witnessKeys = [...input.witnessKeys].sort((a, b) => (a.witnessId < b.witnessId ? -1 : a.witnessId > b.witnessId ? 1 : 0));
  if (witnessKeys.length < 2) throw new Error("at least two witnesses required");
  for (const field of ["witnessId", "keyRef", "operatorIdentity", "failureDomain", "fingerprintSha256"]) {
    if (new Set(witnessKeys.map((item) => item[field])).size !== witnessKeys.length) throw new Error(`witness ${field} values must be pairwise distinct`);
  }
  const core = Object.freeze({ ...input, witnessKeys: Object.freeze(witnessKeys) });
  if (core.repositoryId !== "redshift-three67/aurelia") throw new Error("repositoryId mismatch");
  if (JSON.stringify(core.genesisEventIds) !== JSON.stringify(["EVT-000001", "EVT-000002", "EVT-000003"])) throw new Error("genesisEventIds mismatch");
  if (core.finalApprovalPath !== "docs/governance/bootstrap/final-design-approval.json") throw new Error("final approval path mismatch");
  return core;
}

const PRE_LEDGER_PENDING_AUTHORITIES = Object.freeze([
  "genesis-register-set",
  "genesis-trust-roots",
  "genesis-detached-attestation-set",
  "genesis-event-prefix",
]);

function assertPreLedgerCandidateResult(result) {
  if (result?.testOnly === true || result?.phase !== "pre-ledger-candidate" || result?.candidateValid !== true || result?.gateEffective !== false || result.errors.length !== 0 || JSON.stringify(result.authorityRequired) !== JSON.stringify(PRE_LEDGER_PENDING_AUTHORITIES)) {
    throw new Error(`pre-ledger candidate validation failed: ${JSON.stringify(result)}`);
  }
}

export function assemblePreLedgerBundle({ core, operatorSigningRecord, recoveryRootSigningRecord, externalPins, productionAuthorityContext, bootstrapValidationContext }) {
  assertImplementationTreePreGenesis(bootstrapValidationContext.repositoryRoot, core.governanceImplementationCommit);
  assertFreshCandidateNonces(productionAuthorityContext, core.governanceImplementationCommit, externalPins,
    "before-pre-ledger", {
      "design-approval": { artifactCount: 1, headSha256: core.finalApprovalSha256 },
      bootstrap: { artifactCount: 0, headSha256: null },
    }, core.issuedAt, [core.nonce]);
  const payloadBytes = canonicalBytes(core);
  const payloadSha256 = sha256Hex(payloadBytes);
  for (const [label, record, key] of [
    ["operator", operatorSigningRecord, externalPins.operatorKey],
    ["recovery-root", recoveryRootSigningRecord, externalPins.recoveryRootKey],
  ]) {
    assertClosedObject(record, ["payloadSha256", "observedNonce", "signatureBase64url"], `${label}SigningRecord`);
    if (record.payloadSha256 !== payloadSha256 || record.observedNonce !== core.nonce) throw new Error(`${label} signed a different core or nonce`);
    if (!verifyEd25519({ publicKeyBase64url: key.publicKeyBase64url, payloadBytes, signatureBase64url: record.signatureBase64url })) throw new Error(`${label} signature invalid`);
  }
  if (externalPins.operatorKey.fingerprintSha256 !== core.operatorKey.fingerprintSha256 || externalPins.recoveryRootKey.fingerprintSha256 !== core.recoveryRootKey.fingerprintSha256) throw new Error("external signer pin mismatch");
  const artifact = Object.freeze({ ...core, operatorSignature: operatorSigningRecord.signatureBase64url, recoveryRootSignature: recoveryRootSigningRecord.signatureBase64url });
  assertValidationResult(validateSchema("pre-ledger-trust-bundle", artifact), "pre-ledger-trust-bundle schema");
  const candidateResult = validatePreLedgerCandidate({
    repositoryRoot: bootstrapValidationContext.repositoryRoot,
    designCommit: core.designCommit,
    implementationCommit: core.governanceImplementationCommit,
    finalApproval: bootstrapValidationContext.finalApproval,
    preLedgerBundle: artifact,
    externalPins,
  });
  assertPreLedgerCandidateResult(candidateResult);
  return artifact;
}
```

Refactor the Plan-05 internal validator before `I` into a shared signed-bootstrap-pair phase and the existing full-Genesis phase. The production wrapper is exactly:

```js
import { verifyEd25519 } from "./crypto.mjs";
import {
  validateCryptographicBootstrapCore,
  validatePreLedgerCandidateCore,
} from "./bootstrap-validator-internal.mjs";

export function validatePreLedgerCandidate(args) {
  return validatePreLedgerCandidateCore(args, { verifySignature: verifyEd25519 });
}

export function validateCryptographicBootstrap(args) {
  return validateCryptographicBootstrapCore(args, { verifySignature: verifyEd25519 });
}
```

`validatePreLedgerCandidateCore` requires only `repositoryRoot`, D, I, final approval, signed Pre-Ledger bundle, and external pins. It performs the same closed-schema checks, forbidden-secret scan, fixed D/spec/hash/approval-text checks, strict D→I topology, final-approval artifact hash/path check, all nested external key/service/image/policy/provider/failure-domain/log/witness equalities, pairwise key/service/failure-domain separation, canonical Base64url/nonces, code-unit Witness order, and all three Ed25519 checks (final approval, operator Pre-Ledger, recovery-root Pre-Ledger) used by the full validator. It returns exactly:

```js
Object.freeze({
  phase: "pre-ledger-candidate",
  candidateValid: errors.length === 0,
  errors,
  authorityRequired: [...PRE_LEDGER_PENDING_AUTHORITIES],
  testOnly: false,
  gateEffective: false,
});
```

It does not accept or inspect caller-supplied empty `trustRoots`, `attestations`, `events`, or registers and can never be used as a green Gate result. `validateCryptographicBootstrapCore` then calls the same signed-pair phase and additionally requires/validates the complete G trust roots, detached-attestation bijection, finalized seed Event prefix, trust-root deltas, immediately-prior signer state, and register/ledger consistency; that full G result may become `cryptographicValid:true` but remains `gateEffective:false` until composed by Plan 11. Add source-boundary tests proving that only `bootstrap-validator.mjs` and its test import the internal module, injected/dummy signatures fail through both production exports, the candidate phase has the exact four pending authorities, and passing empty Genesis arrays cannot change `gateEffective:false`.

Before Pre-Ledger assembly, refresh `ProductionAuthorityContext` through Plan 11 with the signed final approval included in the complete artifact inventory; omission changes its signed count/head/hash binding and its nonce-prefix claims. A locally supplied nonce array, boolean, self-hash, raw pin set, or copied context object never proves completeness or authority.

- [ ] **Step 5: Run tests and commit constructors**

```powershell
node --test scripts/governance/bootstrap-artifacts.test.mjs scripts/governance/bootstrap-validator.test.mjs
git add scripts/governance/bootstrap-artifacts.mjs scripts/governance/bootstrap-artifacts.test.mjs scripts/governance/bootstrap-validator-internal.mjs scripts/governance/bootstrap-validator.mjs scripts/governance/bootstrap-validator.test.mjs scripts/fixtures/governance/bootstrap/final-design-approval-core.json scripts/fixtures/governance/bootstrap/pre-ledger-core.json
git commit -m "feat: construct G0 bootstrap artifacts"
```

Expected: PASS and a focused commit.

### Task 2: Generate and validate the complete unsigned initial manifest

**Files:**
- Create: `scripts/governance/initial-manifest.mjs`
- Create: `scripts/governance/initial-manifest.test.mjs`
- Create: `scripts/governance/initial-manifest-seed.mjs`
- Create: `scripts/governance-genesis-ceremony.mjs`
- Create: `scripts/governance-genesis-ceremony.test.mjs`
- Create: `scripts/governance-wave.mjs`
- Create: `scripts/governance-wave.test.mjs`
- Create: `scripts/fixtures/governance/genesis/valid-unsigned-seed.json`
- Create: `scripts/fixtures/governance/genesis/invalid-seed-mutations.json`
- Modify: `package.json`

- [ ] **Step 1: Write the failing closed-seed coverage test**

Require exact sets for 22 `REQ-HR-*`, 12 `REQ-GOV-*`, 13 initial Controls, two Profiles, every role from design section 7, nine components, eleven risks, six data objects, eight flows, nine red gates, five reviews, the five core G0 evidences, the exact generated Genesis change-authorization EVID set described below, and zero exceptions. Require complete product coverage for D01-24, C01-12, X01-20, U01-12, K1-8, L01-09, H1-8, O01-10, and WV01-06.

Assert the first three events are exactly operator assignment, orchestrator assignment, and design-commit capture. For every later non-self-authorizing seed subject, require one immediately preceding, already captured, exact-change-bound authorization EVID; captured EVID lifecycle records authorize only themselves. Every seed and authorization record has exactly one `fromStatus:null` event. Mutate every family by missing, duplicate, extra, reordered-first-three, subject-before-EVID, wrong EVID ID/scope/change digest/baseline/status, wrong role, wrong status, wrong base, and product-ID omission.

- [ ] **Step 2: Run and record RED**

```powershell
node --test scripts/governance/initial-manifest.test.mjs
```

Expected: FAIL because `buildInitialManifest` and `validateInitialManifestCoverage` are missing.

- [ ] **Step 3: Implement deterministic seed builders**

`scripts/governance/initial-manifest-seed.mjs` exports the complete closed,
schema-valid subject definitions as `INITIAL_G0_SUBJECTS`; it contains public
governance data only, no Nonce, signature, private key, credential, pin,
current time, or generated identity. `scripts/governance/initial-manifest.mjs`
imports the stable pure builder from Plan 03 and implements this closed
coverage and assembly core:

```js
import { buildGovernanceTransaction } from "./transition-ledger.mjs";
import { canonicalBytes } from "./rfc8785.mjs";
import { sha256Hex } from "./crypto.mjs";
import { validateSchema } from "./schema-registry.mjs";
import {
  assertFreshCandidateNonces,
  assertValidationResult,
} from "./bootstrap-artifacts.mjs";
import {
  CORE_G0_EVIDENCE_IDS,
  GENESIS_CHANGE_AUTH_EVIDENCE_IDS,
  INITIAL_G0_SUBJECTS,
  PREVIEW_ALLOWED_CAPABILITIES,
  PREVIEW_FORBIDDEN_CAPABILITIES,
  materializeGenesisSeed,
} from "./initial-manifest-seed.mjs";

const range = (prefix, from, to, width) => Object.freeze(Array.from({ length: to - from + 1 }, (_, index) => `${prefix}${String(from + index).padStart(width, "0")}`));
const REQUIRED = Object.freeze({
  requirement: Object.freeze([...range("REQ-HR-", 1, 22, 2), ...range("REQ-GOV-", 1, 12, 3)]),
  control: Object.freeze([
    "CTRL-GOV-SOURCE-PRECEDENCE", "CTRL-GOV-TRACEABILITY", "CTRL-GOV-INDEPENDENT-REVIEW", "CTRL-GOV-REASONING-CONFIRMATION",
    "CTRL-GOV-EXTERNAL-LLM-SANITIZATION", "CTRL-GOV-SERVER-ACCESS", "CTRL-GOV-NO-WAIVER", "CTRL-GOV-VALIDATOR",
    "CTRL-GOV-ACTOR-ATTESTATION", "CTRL-GOV-BRANCH-PROTECTION", "CTRL-GOV-EXCEPTION-PROVENANCE", "CTRL-GOV-OPERATOR-RECOVERY",
    "CTRL-GOV-INVENTORY-COLLECTOR",
  ]),
  profile: Object.freeze(["PROFILE-PREVIEW", "PROFILE-DEBIAN-PILOT"]),
  role: Object.freeze([
    "ROLE-OPERATOR", "ROLE-ORCHESTRATOR", "ROLE-EXTERNAL-REVIEW-RUNNER", "ROLE-IMPLEMENTER", "ROLE-SPEC-REVIEWER",
    "ROLE-QUALITY-SECURITY-REVIEWER", "ROLE-FINAL-REVIEWER", "ROLE-PRIVACY-REVIEWER", "ROLE-LEGAL-REVIEWER", "ROLE-PENTESTER",
    "ROLE-HARDWARE-REVIEWER", "ROLE-A11Y-CLAIMS-REVIEWER", "ROLE-RECOVERY-ROOT", "ROLE-RECOVERY-CUSTODIAN-A", "ROLE-RECOVERY-CUSTODIAN-B",
  ]),
  component: Object.freeze(["COMP-BROWSER", "COMP-EDGE", "COMP-CONTROL", "COMP-DATA", "COMP-COMPUTE", "COMP-BACKUP", "COMP-IDENTITY", "COMP-EXPORT", "COMP-DELETE"]),
  risk: Object.freeze(["RISK-GOV-DRIFT", "RISK-GOV-SELF-APPROVAL", "RISK-GOV-EXTERNAL-DISCLOSURE", "RISK-GOV-UNTRACEABLE-EXCEPTION", "RISK-MG1-SINGLE-ORIGIN", "RISK-MG1-INPLACE-CHANGE", "RISK-REASONING-MISMATCH", "RISK-GOV-FORGED-ACTOR", "RISK-GOV-STALE-EVIDENCE", "RISK-GOV-OPERATOR-LOCKOUT", "RISK-GOV-TIME-POISONING"]),
  data: Object.freeze(["DATA-PUBLIC", "DATA-CONTROL", "DATA-ART9", "DATA-SECRETS", "DATA-AUDIT", "DATA-BACKUP"]),
  flow: Object.freeze(["FLOW-BROWSER-EDGE", "FLOW-EDGE-CONTROL", "FLOW-CONTROL-DATA", "FLOW-DATA-COMPUTE", "FLOW-DATA-BACKUP", "FLOW-IDENTITY", "FLOW-EXPORT", "FLOW-DELETE"]),
  gate: Object.freeze(["GATE-G0", "GATE-DATAFLOW", "GATE-PROFILE", "GATE-ART9", "GATE-MODULE", "GATE-CUDA", "GATE-HARDWARE", "GATE-PILOT", "GATE-24X7"]),
  review: Object.freeze(["REV-G0-ELABORATION-AUTHORIZATION", "REV-G0-DESIGN-APPROVAL", "REV-G0-SPEC-REVIEW", "REV-G0-QUALITY-REVIEW", "REV-G0-FINAL-REVIEW"]),
  evidence: Object.freeze([...CORE_G0_EVIDENCE_IDS, ...GENESIS_CHANGE_AUTH_EVIDENCE_IDS]),
  exception: Object.freeze([]),
});

const PRODUCT_IDS = Object.freeze([
  ...range("D", 1, 24, 2), ...range("C", 1, 12, 2), ...range("X", 1, 20, 2), ...range("U", 1, 12, 2),
  ...range("K", 1, 8, 1), ...range("L", 1, 9, 2), ...range("H", 1, 8, 1), ...range("O", 1, 10, 2), ...range("WV", 1, 6, 2),
]);

function assertClosedObject(value, fields, label) {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new TypeError(`${label} must be an object`);
  if (JSON.stringify(Object.keys(value).sort()) !== JSON.stringify([...fields].sort())) throw new Error(`${label} has non-contract fields`);
}

function assertExactIds(records) {
  for (const [recordType, requiredIds] of Object.entries(REQUIRED)) {
    const actual = records.filter((entry) => entry.recordType === recordType).map((entry) => entry.record.id).sort();
    const expected = [...requiredIds].sort();
    if (JSON.stringify(actual) !== JSON.stringify(expected)) throw new Error(`closed seed mismatch for ${recordType}`);
  }
  const referenced = new Set(records.flatMap((entry) =>
    Array.isArray(entry.record.productDecisionRefs) ? entry.record.productDecisionRefs : []));
  const missing = PRODUCT_IDS.filter((id) => !referenced.has(id));
  const extra = [...referenced].filter((id) => !PRODUCT_IDS.includes(id));
  if (missing.length || extra.length) throw new Error(`product coverage mismatch: missing=${missing.join(",")};extra=${extra.join(",")}`);
  const preview = records.find((entry) => entry.record.id === "PROFILE-PREVIEW")?.record;
  if (!preview
    || preview.maximumDataClass !== "synthetic"
    || preview.identityAuthority !== "preview-gate"
    || preview.serverAccessLevel !== "none"
    || preview.secretDataRefs.length !== 0
    || !Buffer.from(canonicalBytes(preview.allowedCapabilities))
      .equals(canonicalBytes(PREVIEW_ALLOWED_CAPABILITIES))
    || !Buffer.from(canonicalBytes(preview.forbiddenCapabilities))
      .equals(canonicalBytes(PREVIEW_FORBIDDEN_CAPABILITIES))) {
    throw new Error("PROFILE-PREVIEW synthetic/access/capability boundary mismatch");
  }
  if (records.filter((entry) => entry.recordType === "gate").some((entry) => entry.record.status !== "red" || entry.record.noWaiver !== true)) throw new Error("all initial gates must be red and no-waiver");
  if (records.some((entry) => entry.recordType === "exception")) throw new Error("Genesis exceptions must be empty");
}

export function buildInitialManifest({
  implementationCommit,
  genesisAnchor,
  publicTrustRoots,
  eventAuthorizations,
  occurredAt,
  productDecisionIndex,
  finalApprovalSha256,
  preLedgerBundleSha256,
  externalPins,
  productionAuthorityContext,
  genesisChangeAuthorizationEvidence,
  detachedAttestationFiles,
}) {
  if (!/^[0-9a-f]{40}$/.test(implementationCommit)) throw new Error("implementationCommit must be a full SHA");
  const { records: initialRecords, evidenceFiles } = materializeGenesisSeed({
    subjects: INITIAL_G0_SUBJECTS,
    genesisChangeAuthorizationEvidence,
    implementationCommit,
    occurredAt,
  });
  const candidateNonces = Object.values(eventAuthorizations)
    .flatMap((authorization) => authorization.authorizationAttestations ?? [])
    .map((attestation) => attestation.nonce);
  assertFreshCandidateNonces(productionAuthorityContext, implementationCommit, externalPins,
    "before-genesis", {
      "design-approval": { artifactCount: 1, headSha256: finalApprovalSha256 },
      bootstrap: { artifactCount: 1, headSha256: preLedgerBundleSha256 },
    }, occurredAt, candidateNonces);
  assertExactIds(initialRecords);
  for (const id of PRODUCT_IDS) if (!productDecisionIndex.has(id)) throw new Error(`unresolved product decision ${id}`);
  let priorEvents = Object.freeze([]);
  let priorRecords = new Map();
  for (const { record, authorizationDefaults } of initialRecords) {
    const authorization = eventAuthorizations[record.id];
    assertClosedObject(authorization, ["actorRole", "actorAssigneeSnapshot", "operatorEpoch", "evidenceRefs", "trustRootDeltaSha256", "eventAuthorizationPayloadSha256", "authorizationAttestations"], `${record.id} authorization`);
    if (!Array.isArray(authorization.authorizationAttestations) || authorization.authorizationAttestations.length === 0) throw new Error(`${record.id} needs non-empty attestations`);
    if (!Buffer.from(canonicalBytes(authorization.evidenceRefs))
      .equals(canonicalBytes(authorizationDefaults.requiredEvidenceRefs))) {
      throw new Error(`${record.id} has non-topological or non-exact evidenceRefs`);
    }
    const changeCore = Object.freeze({
      recordRef: record.id,
      eventKind: "transition",
      resultingRecord: record,
      actorRole: authorization.actorRole,
      actorAssigneeSnapshot: authorization.actorAssigneeSnapshot,
      operatorEpoch: authorization.operatorEpoch,
      occurredAt,
      evidenceRefs: authorization.evidenceRefs,
      trustRootDeltaSha256: authorization.trustRootDeltaSha256,
      genesisAnchor: authorizationDefaults.requiresGenesisAnchor ? genesisAnchor : null,
    });
    const unsigned = buildGovernanceTransaction({ baseCommit: implementationCommit, priorEvents, priorRecords, changes: [{ ...changeCore, authorizationAttestations: null }] });
    if (unsigned.newEvents.length !== 0 || !unsigned.signingRequest || unsigned.signingRequest.eventAuthorizationPayloadSha256 !== authorization.eventAuthorizationPayloadSha256) throw new Error(`${record.id} signing request mismatch`);
    const finalized = buildGovernanceTransaction({ baseCommit: implementationCommit, priorEvents, priorRecords, changes: [{ ...changeCore, authorizationAttestations: authorization.authorizationAttestations }] });
    if (finalized.signingRequest !== null || finalized.newEvents.length !== 1) throw new Error(`${record.id} did not finalize exactly one event`);
    priorEvents = Object.freeze([...priorEvents, ...finalized.newEvents]);
    priorRecords = finalized.resultingRecords;
  }
  const firstThree = priorEvents.slice(0, 3).map(({ id, recordRef, fromStatus, toStatus }) => ({ id, recordRef, fromStatus, toStatus }));
  const expectedFirstThree = [
    { id: "EVT-000001", recordRef: "ROLE-OPERATOR", fromStatus: null, toStatus: "assigned" },
    { id: "EVT-000002", recordRef: "ROLE-ORCHESTRATOR", fromStatus: null, toStatus: "assigned" },
    { id: "EVT-000003", recordRef: "EVID-G0-DESIGN-COMMIT", fromStatus: null, toStatus: "captured" },
  ];
  if (JSON.stringify(firstThree) !== JSON.stringify(expectedFirstThree)) throw new Error("Genesis prefix mismatch");
  assertValidationResult(validateSchema("trust-roots", publicTrustRoots), "trust-roots schema");
  const trustRootsFileBytes = canonicalBytes(publicTrustRoots);
  const suppliedDetached = new Map(detachedAttestationFiles.map((file, index) => {
    assertClosedObject(file, ["path", "sha256", "fileBytes"], `detachedAttestationFiles[${index}]`);
    if (!Buffer.isBuffer(file.fileBytes) || sha256Hex(file.fileBytes) !== file.sha256)
      throw new Error(`detached attestation byte hash mismatch: ${file.path}`);
    if (file.path.includes("\\") || file.path.startsWith("/") || file.path.split("/").includes(".."))
      throw new Error(`non-canonical detached attestation path: ${file.path}`);
    return [file.path, file];
  }));
  if (suppliedDetached.size !== detachedAttestationFiles.length)
    throw new Error("duplicate detached attestation path");
  const expectedDetached = new Map(priorEvents.flatMap((event) =>
    event.authorizationAttestations.map((attestation) => {
      assertValidationResult(validateSchema("event-attestation", attestation), "event-attestation schema");
      const path = `docs/governance/attestations/${event.id}--${attestation.attestationPurpose}--${attestation.keyRef}.json`;
      if (!/^docs\/governance\/attestations\/EVT-[0-9]{6}--[a-z0-9-]+--KEY-[A-Z0-9]+(?:-[A-Z0-9]+)*\.json$/.test(path))
        throw new Error(`detached attestation filename contract mismatch: ${path}`);
      return [path, canonicalBytes(attestation)];
    })));
  if (expectedDetached.size !== priorEvents.reduce((count, event) =>
    count + event.authorizationAttestations.length, 0)
    || canonicalBytes([...suppliedDetached.keys()].sort())
      .compare(canonicalBytes([...expectedDetached.keys()].sort())) !== 0)
    throw new Error("detached/embedded attestation path bijection mismatch");
  for (const [path, expectedBytes] of expectedDetached) {
    if (!suppliedDetached.get(path).fileBytes.equals(expectedBytes))
      throw new Error(`detached/embedded attestation byte mismatch: ${path}`);
  }
  const reservedPaths = new Set([
    ...expectedDetached.keys(),
    "docs/governance/trust-roots.json",
    "docs/governance/traceability-register.md", "docs/governance/risk-register.md",
    "docs/governance/data-processing-inventory.md", "docs/governance/gate-register.md",
  ]);
  if (Object.keys(evidenceFiles).some((path) => reservedPaths.has(path)))
    throw new Error("Genesis output path collision");
  return Object.freeze({
    records: priorRecords,
    events: priorEvents,
    trustRootsFileBytes,
    attestationFiles: Object.freeze(Object.fromEntries([...expectedDetached.entries()])),
    evidenceFiles,
  });
}

export function renderInitialManifest(manifest) {
  const records = [...manifest.records.values()];
  const select = (prefix) => records.filter((record) => record.id.startsWith(prefix));
  const markdownBytes = (register) => Buffer.from(
    `<!-- governance-data:start -->\n\`\`\`json\n${canonicalBytes(register).toString("utf8")}\n\`\`\`\n<!-- governance-data:end -->\n`,
    "utf8",
  );
  return Object.freeze({
    ...manifest.evidenceFiles,
    ...manifest.attestationFiles,
    "docs/governance/trust-roots.json": manifest.trustRootsFileBytes,
    "docs/governance/traceability-register.md": markdownBytes(Object.freeze({
      schemaVersion: "aurelia-governance-v1", registerType: "traceability",
      requirements: select("REQ-"), controls: select("CTRL-"), profiles: select("PROFILE-"), roles: select("ROLE-"), components: select("COMP-"),
    })),
    "docs/governance/risk-register.md": markdownBytes(Object.freeze({
      schemaVersion: "aurelia-governance-v1", registerType: "risk", risks: select("RISK-"),
    })),
    "docs/governance/data-processing-inventory.md": markdownBytes(Object.freeze({
      schemaVersion: "aurelia-governance-v1", registerType: "data-processing", dataObjects: select("DATA-"), flows: select("FLOW-"),
    })),
    "docs/governance/gate-register.md": markdownBytes(Object.freeze({
      schemaVersion: "aurelia-governance-v1", registerType: "gate",
      gates: select("GATE-"), reviews: select("REV-"), evidence: select("EVID-"), exceptions: select("EXC-"), transitions: manifest.events,
    })),
  });
}
```

The builder is deterministic for explicit inputs, writes nothing, and never creates a signature, time, nonce, key, identity, or external pin. Ceremony execution is strictly sequential: pass `authorizationAttestations:null` for exactly the next change, sign that one returned `signingRequest`, rebuild that same one change with a non-empty verified attestation array, then use its finalized event hash as the prefix for the next request. An empty array is rejected. No later request is exposed before its predecessor is finalized. Only the fully replayed final result may be rendered.

`initial-manifest-seed.mjs` first defines the closed static core subjects, then deterministically describes their expansion before `I`; it does not invent captured evidence bytes, paths, timestamps, hashes, manifests, Nonces, or signatures. It exports `PREVIEW_ALLOWED_CAPABILITIES` as exactly `['synthetic-catalogue-read','synthetic-workflow-preview']` and `PREVIEW_FORBIDDEN_CAPABILITIES` as exactly `['art9-data','debian-local-identity','hardware-access','production-secret-read','privileged-server-access','runtime-server-access']`, both code-unit-sorted and deeply frozen. The `PROFILE-PREVIEW` seed uses those exact arrays, `maximumDataClass:'synthetic'`, `identityAuthority:'preview-gate'`, empty `secretDataRefs`, and `serverAccessLevel:'none'`; no nonexistent profile discriminator is used. The only empty-evidence records are exactly `EVT-000001..EVT-000003`. For every later subject that is not itself a `null->captured` EVID lifecycle, `genesisAuthorizationEvidenceId(subject)` returns exactly `EVID-G0-RECOVERY-ROOT-ASSIGNMENT-AUTH` for `ROLE-RECOVERY-ROOT` and otherwise `EVID-G0-GENESIS-${subject.id}-AUTH`. At ceremony time, `materializeGenesisSeed` accepts the closed `genesisChangeAuthorizationEvidence` map of already produced canonical report/subject-manifest/input-manifest bytes plus the complete captured EVID record for each exact ID. It verifies all Plan-04 manifest/path/hash/provenance rules, `producedAt === occurredAt`, `captureBaseCommit === baselineCommit === I`, and exact key bijection before expanding anything; missing/extra or generated substitute bytes fail.

The expansion inserts that verified schema-valid `null->captured` EVID immediately before its subject. Its scope is exactly `governance-change:${subject.id}:transition:null:${resultingRecordSha256}`, `governanceChangeDigests` contains only the subject's exact pending `changeDigest`, `producerRole` is an already assigned allowed actor, and its own Event references exactly itself. The consuming subject references exactly that EVID. A later core EVID whose target status is `captured` instead uses its own normalized self-lifecycle and is not given a second authorization EVID; a core EVID in any other initial status receives one like every other subject. `GENESIS_CHANGE_AUTH_EVIDENCE_IDS` is the frozen code-unit-ordered result of that explicit subject expansion, and tests independently recompute the expected subject-to-EVID bijection rather than trusting the export. The returned `evidenceFiles` map contains only the already supplied canonical `docs/governance/evidence/**` and `docs/governance/manifests/**` bytes and is rendered atomically with the registers; no report is synthesized from its own record.

`INITIAL_G0_SUBJECTS` orders the three required Genesis subjects first, then each authorization-EVID/subject pair in dependency order: remaining roles needed as actors, Requirements/Controls/Profiles/Components/Risks/Data/Flows/Gates/Reviews/core Evidence. In particular, the Recovery-Root authorization EVID is finalized before the Recovery Root assignment and is mutated in tests for wrong ID, expected instead of captured, wrong scope, wrong digest, wrong baseline, and reversed order. The seed defines `REV-G0-DESIGN-APPROVAL` as requested with baseline `D` and scope `AURELIA-G0-GOVERNANCE-DESIGN`; `REV-G0-SPEC-REVIEW`, `REV-G0-QUALITY-REVIEW`, and `REV-G0-FINAL-REVIEW` are requested with baseline `I` and scope `AURELIA-G0-GOVERNANCE-IMPLEMENTATION`. Expected core EVID records retain the schema-required null baseline until capture. `EVID-G0-DESIGN-COMMIT` alone is captured with baseline `D` and capture base `I`. `validateTransitionLedger({ baseRecords: new Map(), targetRecords: result.records, baseEvents: [], targetEvents: result.events, baseCommit: implementationCommit })` must return no diagnostics. Every later human specialist and both Custodians are explicitly `unassigned`.

`renderInitialManifest` returns concrete byte buffers for every path, never JS
objects for file writers to reinterpret. Tests parse each Markdown file back
through the production fatal-I-JSON register parser, require exactly one start
marker, one `json` fence, one end marker, byte-identical records/Events, and a
single final LF. They also parse every canonical JSON output and require
`fileBytes === canonicalBytes(parsed)`. Mutations cover missing/extra/duplicate
detached files, wrong file hash/path/purpose/key, embedded/detached drift,
noncanonical trust-root bytes, evidence/output path collision, extra fence or
marker, CRLF/BOM, and renderer key loss.

#### Closed executable ceremony and transaction contract

Create `scripts/governance-genesis-ceremony.mjs` as the only production
ceremony runner. It imports the Plan-11 issuer and the constructors above, so
every invocation recreates and consumes the module-private
`pre-genesis-ceremony` capability in the same Node process. It never accepts a
serialized result/context, never imports a private-key API, never calls the
network, never chooses a time/Nonce/identity, and never evaluates code from an
input file. The parser rejects duplicate, missing, or unknown flags and has
exactly these modes and flag matrices:

| Mode | Required flags | Permitted write |
|---|---|---|
| `final-design-core` | `--request`, `--out` | one new protected external signing-request file |
| `final-design-assemble` | `--request`, `--signature`, `--artifact-out` | exact repository path `docs/governance/bootstrap/final-design-approval.json` |
| `pre-ledger-core` | `--request`, `--out` | one new protected external dual-signature request |
| `pre-ledger-assemble` | `--request`, `--operator-signature`, `--recovery-root-signature`, `--artifact-out` | exact repository path `docs/governance/bootstrap/pre-ledger-trust-bundle.json` |
| `genesis-next-signing-request` | `--request`, `--out` | one new protected external request for exactly the next seed Event |
| `genesis-final-render` | `--request` | the exact new Genesis public paths returned by `renderInitialManifest` |

Every path flag is absolute. `--request`, signatures, and ordinary `--out`
paths resolve outside the repository; artifact outputs resolve to their exact
fixed path, are absent before exclusive creation, and cannot be symlinks. Each
request is fatal-I-JSON/canonical JSON with exactly
`schemaVersion/mode/repositoryId/implementationCommit/authorityComponents/inputs`.
It fixes `schemaVersion:"aurelia-ceremony-request-v1"`, repository ID, full
`I`, its Tree, and the mode. `authorityComponents` has exactly externally
protected absolute path plus expected raw SHA-256 for `externalPins`, the
complete append-only `trustedTimeHistory`, `signedArtifactInventory`, `nonceArtifacts`, and
`ceremonyArtifacts`. The runner rereads, hashes, strictly parses, and passes
those actual objects to Plan 11; no digest-only substitute is accepted.
Every `inputs` member except `transactionJournal` is exactly
`{path,sha256}`; both fields are mandatory and closed. The field sets are:

| Request `mode` | Exact `inputs` keys |
|---|---|
| `final-design-core` | `operatorInput` |
| `final-design-assemble` | `coreRequest`, `signingRequest`, `transactionJournal` |
| `pre-ledger-core` | `finalDesignApproval`, `preLedgerInput` |
| `pre-ledger-assemble` | `coreRequest`, `signingRequest`, `finalDesignApproval`, `transactionJournal` |
| `genesis-next-signing-request` | `finalDesignApproval`, `preLedgerBundle`, `publicTrustRoots`, `genesisChangeAuthorizationEvidence`, `eventAuthorizationsPrefix`, `detachedAttestationFilesPrefix` |
| `genesis-final-render` | `finalDesignApproval`, `preLedgerBundle`, `publicTrustRoots`, `genesisChangeAuthorizationEvidence`, `eventAuthorizationsComplete`, `detachedAttestationFilesComplete`, `transactionJournal` |

`transactionJournal` is exactly `{path,expectedState}` with external absolute
path and `expectedState:"absent-or-recoverable"`; because it is created and
updated by the runner it has no caller-supplied hash. The product-decision
index is always recomputed from immutable `I`, never loaded through `inputs`.
Signature files remain only in their exact assembly CLI flags and are bound by
their signed payload hash; duplicating one under `inputs` is rejected. Tests
freeze the exact key set for all six modes and mutate every
missing/extra/path/hash/value/mode combination.

Core and assembly invocations never reuse one Request object under another
mode. `final-design-assemble` and `pre-ledger-assemble` each have their own
canonical Request file with the matching `mode`; their closed `inputs` bind
the corresponding earlier core Request and emitted signing request by absolute
path, raw SHA-256, and expected core mode. The runner reloads both, requires
their exact canonical bytes, and recomputes the unsigned core from the
assembly Request's independently repeated authority components. Mismatched
core/assembly components, a changed core Request, or use of a core-mode Request
for assembly fails before signature verification.

Core modes emit canonical JSON containing exactly the unsigned `core`, its
canonical payload as Base64url, `payloadSha256`, public authority bindings, and
`status:"SIGNATURE-PENDING"`; they use exclusive create plus file and parent
directory sync and never write the repository. Assembly modes independently
reissue the capability, recompute the core rather than trusting the output
file, verify each external public signature record and exact payload hash, and
write only already verified canonical public bytes by exclusive temporary
file, `fsync`, byte/hash read-back, and same-directory rename. Each assembly
uses its own external `transactionJournal`; there is no unjournaled repository
write. Without a matching recoverable journal, an existing target is
`AUTHORITY-RED` and is never overwritten. With a matching journal from an
interrupted invocation, the runner first verifies the transaction ID, target,
expected hash/length, temp name, and every recorded byte. A matching completed
rename is either finished idempotently after full read-back or rolled back;
partial matching temp/final state is removed and restored to target-absent
before a single retry. Unknown, drifted, or unjournaled target bytes, a
symlink/reparse point, wrong signer purpose, or any mismatch stop
`AUTHORITY-RED` without deleting the unknown object.

`genesis-next-signing-request` treats the complete seed order as a state
machine. Its request contains the immutable Genesis inputs and only the
already finalized authorization map. It recomputes the complete preceding
record/Event prefix, rejects a gap/reorder/future entry, and emits exactly the
next `recordRef`, authorization core, canonical bytes, hash, and prior Event
hash. It cannot render and exposes no later request. A repeated invocation with
the same bytes is byte-identical. `genesis-final-render` requires the exact
complete authorization map, recomputes every request/final Event, invokes
`buildInitialManifest`, `renderInitialManifest`, the production schema,
reference, ledger, cryptographic-bootstrap and local-preflight validators,
then uses a fail-closed all-or-rollback transaction.

The CLI response ABI is also closed and schema-tested; prose-only output is
forbidden. Every response is canonical JSON followed by one LF and no other
stdout. Stderr contains diagnostics only. The exact top-level keys are:

| Mode | Exact canonical response keys | Fixed status |
|---|---|---|
| `final-design-core` / `pre-ledger-core` | `schemaVersion,mode,repositoryId,implementationCommit,core,payloadSha256,payloadBase64url,authorityBindings,status,gateEffective` | `SIGNATURE-PENDING` |
| `final-design-assemble` / `pre-ledger-assemble` | `schemaVersion,mode,repositoryId,implementationCommit,artifactPath,artifactSha256,signerKeyRefs,status,gateEffective` | `ARTIFACT-ASSEMBLED` |
| `genesis-next-signing-request` | `schemaVersion,mode,repositoryId,implementationCommit,eventId,recordRef,priorEventHash,core,payloadSha256,payloadBase64url,authorityBindings,status,gateEffective` | `SIGNATURE-PENDING` |
| `genesis-final-render` | `schemaVersion,mode,repositoryId,implementationCommit,implementationTreeOid,pathCount,paths,outputSetSha256,status,gateEffective` | `GENESIS-RENDER-COMPLETE` |

`schemaVersion` is exactly `aurelia-ceremony-response-v1` and
`gateEffective:false` in all modes. `authorityBindings` has exactly
`externalPinsSha256/trustedTimeAttestationSha256/signedArtifactInventorySha256/noncePrefixSha256/implementationTreeOid`.
`signerKeyRefs` and `paths` are nonempty, unique, code-unit-sorted arrays;
`paths` contains exact `{path,sha256,byteLength}` objects. Core responses use
the closed unsigned core schema for that mode; payload digest/Base64url are
recomputed from its RFC-8785 bytes. Assembly/final responses are emitted only
after journal completion and disk read-back. The test suite validates closed
response schemas for all six modes, rejects every added/removed/retyped nested
field and wrong status, and compares one complete golden byte fixture per mode.

#### Closed post-Genesis Governance Wave and resume runner

Also create `scripts/governance-wave.mjs` before `I`. Plan 13 is forbidden to
call `buildGovernanceTransaction` from an ad-hoc expression or render a file
itself; it uses only this runner. The runner imports the fixed Plan-03 builder,
repository view, Plan-02/04 validators, Plan-05 signature verifier, and Plan-11
offline authority wrapper. It contains no private key, network client, raw
clock, Nonce generator, or dynamic module/eval path. Its parser accepts exactly
`--mode <closed-mode> --request <absolute-external-file>` and additionally
`--out <new-absolute-external-file>` only for
`next-signing-request`. Duplicate/unknown flags or repository-contained request,
journal, execution-record, signing, output, or protected-input paths fail.

Every request is canonical duplicate-key-free JSON with exactly
`schemaVersion/mode/repositoryId/repositoryRoot/implementationCommit/executionRecord/inputs`.
`schemaVersion` is `aurelia-governance-wave-request-v1`; the repository and
frozen `I` are exact. `executionRecord` has exactly absolute external
`path/priorSha256/transactionJournalPath`. It is a canonical append-only state
machine, not a session environment variable. Each entry binds
`sequence/waveId/baseCommit/baseTreeOid/renderedPathSetSha256/committedHead/committedTreeOid/parentCommit/remoteAcceptanceStatus/remoteAuthorityBundleSha256/receiptId/checkpointSha256/floorSetSha256/trustedTimeAttestationSha256`;
nullable fields follow the stage. The runner rereads the record, requires its
raw `priorSha256`, validates every earlier Git object and external artifact,
then journals each replacement. A resume never trusts `$env:` and stops on a
moved HEAD, wrong parent, rewritten prior entry, missing artifact, or changed
remote status.

The exact mode/input table is:

| Mode | Exact `inputs` keys | Effect |
|---|---|---|
| `command-capture` | `captureDefinition,protectedTrustedTimeBefore,protectedTrustedTimeAfter,transactionJournal` | runs one closed allowlisted command profile; exclusively stores raw stdout, raw stderr and canonical receipt outside the repository |
| `next-signing-request` | `waveDefinition,eventAuthorizationsPrefix,detachedAttestationFilesPrefix` | emits exactly one new external signing request |
| `final-render` | `waveDefinition,eventAuthorizationsComplete,detachedAttestationFilesComplete,transactionJournal` | atomically renders the complete validated Governance-only wave |
| `record-head` | `waveId,expectedBaseCommit,expectedCommittedHead,expectedCommittedTreeOid,transactionJournal` | verifies HEAD/Tree/one-parent topology and records the committed boundary |
| `record-remote-acceptance` | `waveId,remoteAuthorityAggregate,transactionJournal` | re-verifies the exact committed Head through Plan 11 and records accepted Receipt/checkpoint/floor/time bindings |
| `operator-return-verify` | `operatorSigningRequest,operatorAcceptance,operatorTrustedTimeAttestation,externalPins,acceptedBaseAuthorityAggregate,preAcceptanceNonceArtifacts,verificationRecordOut,operatorTrustedTimeOut,transactionJournal` | verifies the returned full-commit signature and writes only protected external public verification artifacts |

Every path/hash input except a journal is exactly `{path,sha256}`; journals use
`{path,expectedState:"absent-or-recoverable"}`. `waveDefinition` is a closed
external JSON object with exactly
`schemaVersion/waveId/baseCommit/baseTreeOid/changes/publicArtifacts`.
`changes` uses the exact Plan-03 change ABI with externally supplied time,
Nonce and authorization fields; `publicArtifacts` contains code-unit-sorted
`{path,sha256,byteLength,contentFile}` entries limited to
`docs/governance/**`. The runner loads prior registers/Events only from the
exact base Git object, validates every actual public artifact byte through the
Plan-03/04 bijection gates, builds signing requests strictly one Event at a
time, verifies each returned detached attestation against prestate role/key/
epoch/purpose, rebuilds the full prefix after every signature, and exposes no
later request early. Final render requires a complete prefix and uses the same
all-or-rollback writer/recovery state machine as Genesis. It writes neither a
commit nor a remote ref.

`command-capture` has a fixed source allowlist for the Plan-13 command IDs and
their exact argv/cwd; no shell string is accepted. It writes byte-exact stdout
and stderr files, then a canonical receipt with exact
`schemaVersion/captureId/commandId/argv/cwd/headCommit/headTreeOid/startedTrustedTimeAttestationSha256/finishedTrustedTimeAttestationSha256/exitCode/stdoutPath/stdoutSha256/stdoutByteLength/stderrPath/stderrSha256/stderrByteLength/toolVersions/status`.
All three outputs are exclusive, journaled, immutable, and later required by
the report's input manifest. Thus no Terminal-only output or unreproducible hash
can become EVID.

`operator-return-verify` is deliberately non-gate-effective and must succeed
before any push/integration request. In one process it recreates the accepted
base context, recomputes the branded pre-Operator prefix and unsigned core,
requires the returned artifact's canonical core byte equality, verifies its
Ed25519 signature against the pinned active Operator key/epoch/fingerprint,
checks the preserved accepted-base Trusted-Time raw bytes/hash, approval time,
scope, candidate Head/Tree, and globally fresh Nonce, then exclusively writes
the byte-identical historical Trusted-Time artifact plus a canonical
`OPERATOR-RETURN-VERIFIED` record. It never writes the repository or returns
`gateEffective:true`; later Receipt/current-time/floors remain mandatory.

All six modes have closed response schemas and golden-byte tests. Fault tests
interrupt before/after every external/repository write, sync, rename, execution
record update, and recovery step. They prove idempotent resume or complete
rollback, never a partial successful status. Add the package script:

```json-fragment
"check:governance-wave": "node scripts/governance-wave.mjs"
```

That transaction accepts only new target paths under the repository, requires
every target and transaction-temp name absent and non-symlink, and stores an
external, canonical, `fsync`ed journal containing transaction ID, repository
root, `I`, exact path/hash/length list, the exact missing parent directories it
created, state, and completed-renames list. Before staging, every existing
ancestor is resolved inside the repository and rejected if it is a symlink or
reparse point; each required absent fixed parent is created one component at a
time, recorded, mode-restricted, and directory-synced. It
writes every sibling temp with exclusive create, mode `0600`, `fsync`, and
byte-identical read-back before the first rename. The commit phase renames only
same-directory temps, syncing the journal and affected directory after each
step. On an exception or next invocation after interruption, recovery removes
only journal-listed temp/final paths whose bytes still match the journal,
then removes only journal-listed created directories that are still empty;
it refuses unknown/drifted files and restores the all-targets-absent state before
retry. The two assembly modes use the same journal state machine,
parent-resolution, recovery rules, and exclusive single-artifact subset; they
may not implement a shorter ad-hoc writer. After all renames it rereads the complete candidate from disk, reruns
the full validation and exact output bijection, marks the journal complete,
syncs, and removes it. Fault-injection tests stop before/after every write,
sync, and rename and prove either zero final targets or the one complete,
validated output set; a partial tree can never pass the subsequent commit
gate. Signal handlers never claim success and recovery is mandatory before
any other mode. Add:

```json-fragment
"check:governance-genesis": "node scripts/governance-genesis-ceremony.mjs"
```

- [ ] **Step 4: Run tests and commit seed generation**

```powershell
node --test scripts/governance/initial-manifest.test.mjs scripts/governance-genesis-ceremony.test.mjs scripts/governance-wave.test.mjs
git add scripts/governance/initial-manifest.mjs scripts/governance/initial-manifest.test.mjs scripts/governance/initial-manifest-seed.mjs scripts/governance-genesis-ceremony.mjs scripts/governance-genesis-ceremony.test.mjs scripts/governance-wave.mjs scripts/governance-wave.test.mjs scripts/fixtures/governance/genesis/valid-unsigned-seed.json scripts/fixtures/governance/genesis/invalid-seed-mutations.json package.json
git commit -m "feat: generate closed G0 initial manifest"
```

Expected: PASS with every mutation rejected.

### Task 3: Freeze and independently approve implementation commit I

**Files:** No real Genesis/bootstrap/register artifact is allowed in this task. `I` includes every reviewed implementation file from Plans 01-11 **and** the constructors, complete public seed definition, Genesis/Wave ceremony runners, and tests from Tasks 1-2 of this plan. It also includes every canonical documentation correction required by Plan 01. No Plan-13 code may appear after `I`; Plan 13 consumes only the already frozen `scripts/governance-wave.mjs` CLI, which internally owns Plan 03's `buildGovernanceTransaction(...)` use.

- [ ] **Step 1: Prove that real governance remains authority-red before Genesis**

```powershell
npm run check:governance -- --pre-genesis
```

Expected: nonzero with only `AUTHORITY-RED` for absent real Genesis/external authority. Any structural or contract error must be fixed before continuing; a zero exit is a P0 false-green.

- [ ] **Step 2: Run all implementation-candidate gates**

```powershell
npm run check:canon
npm run typecheck:governance
npm run typecheck
npm run lint
npm test
npm run build:dev
if ($env:AURELIA_PLAN12_BASE_SHA -notmatch '^[0-9a-f]{40}$') { throw 'AUTHORITY-RED: Plan 12 base SHA absent' }
git diff --check "$env:AURELIA_PLAN12_BASE_SHA..HEAD"
```

Expected: each exits 0. Do not run `npm run build`, because it invokes database migrations.

- [ ] **Step 3: Complete independent Spec and Quality/Security Reviews**

The Spec Reviewer checks complete design coverage; the Quality/Security Reviewer attacks fail-open paths, projections, signatures, time, replay, remote inputs, egress, recovery, and collector boundaries. They must be distinct from implementers and orchestrator. Correct every P0-P2 and repeat both reviews after every correction.

- [ ] **Step 4: Complete independent Final Review of the implementation candidate**

The Final Reviewer is distinct from implementers, orchestrator, Spec Reviewer, and Quality/Security Reviewer. Expected: approved, no open P0-P2, exact commit/file scope recorded.

- [ ] **Step 5: Capture I and prohibit further implementation changes**

```powershell
$implementationCommit = git rev-parse HEAD
if ($implementationCommit -notmatch '^[0-9a-f]{40}$') { throw 'I is not a full commit SHA' }
if (-not $env:AURELIA_EXECUTION_RECORD_PATH) { throw 'AUTHORITY-RED: protected execution-record path absent' }
$record = Get-Content -Raw -LiteralPath $env:AURELIA_EXECUTION_RECORD_PATH | ConvertFrom-Json
if ($record.implementationCommit -and $record.implementationCommit -ne $implementationCommit) { throw 'AUTHORITY-RED: I conflicts with protected record' }
$env:AURELIA_IMPLEMENTATION_COMMIT = $implementationCommit
$implementationCommit
git status --short
```

Expected: full SHA printed and empty status. The operator records that exact SHA in the protected execution record; the environment variable is only a session copy and never a trust anchor. From now until `G`, no commit is allowed. Any implementation correction invalidates `I`, all derived unsigned cores, all signatures, and the pending Genesis; restart Task 3 after correction.

### Task 4: Perform the offline final-design approval ceremony

**Files:**
- Create only after external signing: `docs/governance/bootstrap/final-design-approval.json`

- [ ] **Step 1: Build and independently display the exact unsigned core**

Prepare the closed protected request described in Task 2, including an
externally generated CSPRNG 32-byte Base64url Nonce, then run:

```powershell
npm run check:governance-genesis -- --mode final-design-core --request $env:AURELIA_FINAL_DESIGN_CORE_REQUEST_FILE --out $env:AURELIA_FINAL_DESIGN_SIGNING_REQUEST_FILE
```

The runner uses `buildFinalDesignApprovalCore` with operator key
ref/fingerprint from the protected external pin source and the Trusted-Time
claim read from the freshly Plan-11-verified in-process context. The Nonce must
be absent from that context's complete occupied-nonce set. The context binds
the full raw event/control prefix, all detached attestations, exact externally
signed bootstrap inventory, independent pins, exact I and nonce-prefix hash.
Present only the emitted canonical bytes, digest, and verified public heads to
`ROLE-OPERATOR` outside the repository signer. Do not display private-key
material.

- [ ] **Step 2: Pause for the real operator signature**

`ROLE-OPERATOR` signs the displayed canonical bytes with the externally pinned Ed25519 key using the approved offline signer. This is a human authority step. Chat text, a fixture signature, a generated test key, an orchestrator signature, and an unsigned approval are rejected.

- [ ] **Step 3: Assemble and verify the signed artifact before adding it**

Run the sole production assembly mode against its mode-specific assembly
Request, which byte-binds the immutable core Request/signing output, and the
external public signature record:

```powershell
$finalApprovalPath = Join-Path (Get-Location) 'docs/governance/bootstrap/final-design-approval.json'
npm run check:governance-genesis -- --mode final-design-assemble --request $env:AURELIA_FINAL_DESIGN_ASSEMBLY_REQUEST_FILE --signature $env:AURELIA_FINAL_DESIGN_SIGNATURE_FILE --artifact-out $finalApprovalPath
```

It recreates the in-process capability and recomputes the core before calling
`assembleFinalDesignApproval`. Expected: schema passes, signature verifies,
candidate Nonce is absent from every production-verified domain,
identity/role/key/fingerprint match, exclusive transactional write succeeds,
and the full artifact hash is printed. A missing prefix, changed prefix head,
unknown trusted time, forged capability, reuse, or signature mismatch is
`AUTHORITY-RED`; do not edit signed fields.

- [ ] **Step 4: Place only the verified public artifact at its fixed path**

Do not write, copy, or normalize the artifact a second time. The assembly mode
above already performed the sole exclusive transactional write to
`docs/governance/bootstrap/final-design-approval.json`. Re-read that file from
disk and require byte-identical hash equality with the verified artifact hash
printed by the assembly runner.

- [ ] **Step 5: Confirm no secret material entered the tree**

```powershell
git diff -- docs/governance/bootstrap/final-design-approval.json
rg -n --hidden --glob '!node_modules/**' --glob '!.git/**' 'BEGIN .*PRIVATE KEY|github_pat_|ghp_|Authorization: Bearer|DATABASE_URL=' docs/governance scripts/fixtures/governance
```

Expected: diff contains only public fields and signature; `rg` finds no secret material.

### Task 5: Perform the dual-signature Pre-Ledger ceremony

**Files:**
- Create only after external signing: `docs/governance/bootstrap/pre-ledger-trust-bundle.json`

- [ ] **Step 1: Build the exact Pre-Ledger core bound to I**

Load `I` into the closed request by comparing
`$env:AURELIA_IMPLEMENTATION_COMMIT` with the full `implementationCommit` in
the protected execution record. Bind the verified final-approval full hash,
all public key/service/image/policy/permission/time/failure-domain pins from
the protected external source, immutable validator digests, and sorted Witness
set, then run:

```powershell
npm run check:governance-genesis -- --mode pre-ledger-core --request $env:AURELIA_PRE_LEDGER_CORE_REQUEST_FILE --out $env:AURELIA_PRE_LEDGER_SIGNING_REQUEST_FILE
```

The runner reissues Plan 11's sole context over current complete raw prefixes
and the externally signed artifact inventory containing the signed final
approval, then consumes its refreshed Nonce claims in-process. External pin
values must be independent of repository bytes.

- [ ] **Step 2: Verify closed pin and separation invariants before signing**

Require exactly one non-null provider credential identity on the Gateway pin; Recovery App, Verifier, and Monitor have no credential value. Require App, Gateway, Verifier, Monitor, Controller, Transparency Instance, and every Witness to have the specified distinct identities/failure domains. Require at least two distinct Witnesses. Any missing, duplicated, repository-derived, stale, or differently hashed pin stops the ceremony.

- [ ] **Step 3: Pause for two signatures over identical canonical bytes**

Operator and separately stored Offline Recovery Root each sign the same RFC-8785 Pre-Ledger core via their approved offline signers. The one core nonce was freshly generated before display and is therefore necessarily identical in both displayed signature cores; no signer is allowed to substitute its own nonce or any byte. The separate `operatorSigningRecord` and `recoveryRootSigningRecord` each repeat the same `payloadSha256` and `observedNonce` and carry only their own signature. Neither signer receives the other's private key. The Pre-Ledger core nonce must differ from the final-approval nonce and every value in the complete external replay snapshot.

- [ ] **Step 4: Assemble and reverify the full bundle**

Run:

```powershell
$preLedgerPath = Join-Path (Get-Location) 'docs/governance/bootstrap/pre-ledger-trust-bundle.json'
npm run check:governance-genesis -- --mode pre-ledger-assemble --request $env:AURELIA_PRE_LEDGER_ASSEMBLY_REQUEST_FILE `
  --operator-signature $env:AURELIA_PRE_LEDGER_OPERATOR_SIGNATURE_FILE `
  --recovery-root-signature $env:AURELIA_PRE_LEDGER_RECOVERY_ROOT_SIGNATURE_FILE `
  --artifact-out $preLedgerPath
```

`assemblePreLedgerBundle` receives both exact external signing records, the
freshly recreated production replay capability, and the full external pin
object. It verifies both signatures over byte-identical cores, their repeated
core digest/Nonce, exact `I`, final-approval hash/path, design anchors, Genesis
IDs, validator/TCB digests, keys, services, log ID/epoch, Witness code-unit
order, trusted issued time, and global Nonce uniqueness. It writes only the
verified canonical public artifact to its fixed path through the exclusive
transactional assembly writer. Do not commit yet.

- [ ] **Step 5: Hash and inspect both bootstrap artifacts**

```powershell
Get-FileHash -Algorithm SHA256 docs/governance/bootstrap/final-design-approval.json
Get-FileHash -Algorithm SHA256 docs/governance/bootstrap/pre-ledger-trust-bundle.json
git status --short
```

Expected: two hashes and only uncommitted Genesis-related paths. No commit exists between `I` and the pending `G`.

### Task 6: Materialize and validate Genesis G in the working tree

**Files:**
- Create: `docs/governance/traceability-register.md`
- Create: `docs/governance/risk-register.md`
- Create: `docs/governance/data-processing-inventory.md`
- Create: `docs/governance/gate-register.md`
- Create: `docs/governance/trust-roots.json`
- Create: canonical public JSON files under `docs/governance/attestations/`, with each exact filename supplied by the verified Genesis authorization map and validated as `EVT-[0-9]{6}--[a-z0-9-]+--KEY-[A-Z0-9]+(?:-[A-Z0-9]+)*.json`
- Create: exact canonical Genesis change-authorization reports under `docs/governance/evidence/` for every `GENESIS_CHANGE_AUTH_EVIDENCE_IDS` member
- Create: matching subject/input manifests under `docs/governance/manifests/` for every Genesis change-authorization EVID

The four canonical documentation corrections (`docs/00-index.md`, `docs/23-id-schema.md`, `docs/07-identity.md`, and any design-proven source correction) already belong to `I`. They must not change in `I..G`; `docs/26-wiedervorlage.md` has no separate Genesis obligation and is not touched here.

- [ ] **Step 1: Generate all unsigned seed records/events from fixed inputs**

Before calling `buildInitialManifest`, reissue Plan 11's sole in-process context
from an externally signed `before-genesis` inventory containing exact full
hashes of both the final approval and Pre-Ledger bundle. Pass that context,
those two full hashes, the byte-identical external pin set, and
`occurredAt = claims.trustedTime.now`. Use `implementationCommit` read from the
protected execution record and equality-checked against
`$env:AURELIA_IMPLEMENTATION_COMMIT`, exact Genesis anchor hashes, public trust
roots, already externally produced `eventAuthorizations`, and the product
decision index derived from `I`. Also pass the protected
`genesisChangeAuthorizationEvidence` map containing the exact canonical report
and both manifest bytes for every generated authorization EVID; the builder
materializes no report itself. Pass `detachedAttestationFiles` with exact path,
full-file SHA-256, and byte buffer for every embedded authorization attestation;
the builder proves the complete embedded/detached bijection before returning
any output bytes. The builder checks every candidate attestation
nonce against this refreshed complete prefix before constructing the first
Event. The authorization-map file is external input whose digest is protected;
it maps every subject ID to exact attestation path, full-file SHA-256, purpose,
keyRef, nonce, and event-envelope digest. No builder may sign, name, time, or
invent a missing attestation.

Execute the sequence only through the state-machine mode. Initially and after
each externally returned Event Attestation, update the protected canonical
request with exactly the finalized prefix. Before each invocation, protected
ceremony tooling sets `AURELIA_GENESIS_NEXT_SIGNING_REQUEST_FILE` to a new,
absent absolute external path whose canonical basename is
`<next-EVT-ID>--<recordRef>--signing-request.json`; a path used by a prior
round is immutable and may not be reused, truncated, or overwritten. Run:

```powershell
npm run check:governance-genesis -- --mode genesis-next-signing-request --request $env:AURELIA_GENESIS_NEXT_REQUEST_FILE --out $env:AURELIA_GENESIS_NEXT_SIGNING_REQUEST_FILE
```

The output names exactly one next subject and remains
`SIGNATURE-PENDING`; present it to the pinned external signer, verify and add
that one public attestation plus the exact prior output path/hash to the next
protected request, advance both the expected EVT ID and the `--out` path, then
repeat. A
second request cannot be emitted until the first is finalized. When no subject
remains, the runner emits `GENESIS-AUTHORIZATIONS-COMPLETE` and the full prefix
hash, never a signing request.

- [ ] **Step 2: Render exactly one canonical JSON block per Markdown register**

Each register contains one fenced JSON block between `governance-data:start` and `governance-data:end`, schema version `aurelia-governance-v1`, and only its assigned arrays. `trust-roots.json`, bootstrap artifacts, Genesis authorization reports/manifests, and detached attestations are pure canonical JSON without Markdown. The rendered EVID paths/hashes must match their records byte-for-byte, and the complete generated-ID/file bijection is checked before any file write.

After the protected final request contains the complete verified
authorization map, invoke the only final writer:

```powershell
npm run check:governance-genesis -- --mode genesis-final-render --request $env:AURELIA_GENESIS_FINAL_REQUEST_FILE
```

Expected: `GENESIS-RENDER-COMPLETE`, the exact output-set hash, and no pending
transaction journal. Any interrupted prior transaction is recovered first;
any drift stops without claiming completion.

- [ ] **Step 3: Assert Genesis safety properties before validation**

Run a focused test that asserts `baseCommit === I` on every seed EVT, first three events and Genesis anchors are byte-identical where required, every seed has one event, events are globally contiguous, exceptions are empty, and all nine gates are `red`. Assert `PROFILE-PREVIEW` is synthetic-only and all later specialist/Custodian roles remain unassigned.

- [ ] **Step 4: Run the real local Genesis preflight with external public pins**

At this phase—and not during the Pre-Ledger ceremony—the working-tree adapter loads the four generated registers, `trust-roots.json`, all finalized seed Events, and the exact detached-attestation file inventory and calls production `validateCryptographicBootstrap`. Add a focused integration test that removes each one in turn and expects the corresponding authority/error; with the complete G candidate it requires `errors:[]`, `cryptographicValid:true`, `gateEffective:false`, `authorityRequired:["production-authority-context"]`, and the detached/embedded attestation bijection. The overall CLI remains local-only; only a later Plan-11 aggregate context over the accepted G Head, independently signed pins/time/inventory, receipts and fresh floors can close that authority requirement.

```powershell
if (-not $env:AURELIA_EXTERNAL_PINS_FILE) { throw 'AUTHORITY-RED: external public pin file absent' }
$implementationCommit = $env:AURELIA_IMPLEMENTATION_COMMIT
if ($implementationCommit -notmatch '^[0-9a-f]{40}$') { throw 'AUTHORITY-RED: I absent' }
npm run check:governance -- --base $implementationCommit --working-tree --external-pins $env:AURELIA_EXTERNAL_PINS_FILE --local-preflight
```

Expected: exit 0, `CRYPTOGRAPHIC-BOOTSTRAP=PASS`, and explicit overall status `LOCAL-PREFLIGHT-ONLY`; every Gate is red. The command must not claim a Remote Acceptance-Receipt or current Witness floors.

- [ ] **Step 5: Run all non-remote repository gates**

```powershell
npm run check:canon
npm run typecheck:governance
npm run typecheck
npm run lint
npm test
git diff --check $env:AURELIA_IMPLEMENTATION_COMMIT
```

Expected: every command exits 0.

### Task 7: Commit G and obtain the first external Acceptance-Receipt

**Files:** Only `docs/governance/**` Genesis artifacts from Tasks 4–6. No implementation, schema, test, workflow, top-level directive, index, canonical product document, or unrelated product file may differ from `I`.

- [ ] **Step 1: Verify the exact D-to-I-to-G topology before commit**

```powershell
$implementationCommit = $env:AURELIA_IMPLEMENTATION_COMMIT
git merge-base --is-ancestor a6a8e7dca456d14a6748b204b787b235fdedf9be $implementationCommit
$changed = @(git diff --name-only $implementationCommit)
if ($changed.Count -eq 0) { throw 'Genesis candidate is empty' }
if (@($changed | Where-Object { $_ -notlike 'docs/governance/*' }).Count -ne 0) { throw 'I..G candidate is not Governance-only' }
git diff --name-status $implementationCommit
if (@(git log --format=%H "$implementationCommit..HEAD").Count -ne 0) { throw 'A commit exists between I and pending G' }
```

Expected: ancestor check exit 0; diff contains only Genesis paths; log range is empty.

- [ ] **Step 2: Commit the indivisible Genesis**

```powershell
git add docs/governance
git commit -m "feat: establish Aurelia G0 governance genesis"
$genesisCommit = git rev-parse HEAD
if ((git rev-parse "$genesisCommit^") -ne $env:AURELIA_IMPLEMENTATION_COMMIT) { throw 'G parent is not I' }
if (-not $env:AURELIA_EXECUTION_RECORD_PATH) { throw 'AUTHORITY-RED: protected execution-record path absent' }
$record = Get-Content -Raw -LiteralPath $env:AURELIA_EXECUTION_RECORD_PATH | ConvertFrom-Json
if ($record.genesisCommit -and $record.genesisCommit -ne $genesisCommit) { throw 'AUTHORITY-RED: G conflicts with protected record' }
$env:AURELIA_GENESIS_COMMIT = $genesisCommit
$genesisCommit
```

Expected: one commit directly after `I`; full SHA captured as `G`.

- [ ] **Step 3: Revalidate G as a commit transition**

```powershell
$implementationCommit = $env:AURELIA_IMPLEMENTATION_COMMIT
$genesisCommit = $env:AURELIA_GENESIS_COMMIT
npm run check:governance -- --base $implementationCommit --head $genesisCommit --external-pins $env:AURELIA_EXTERNAL_PINS_FILE --local-preflight
```

Expected: exit 0 and `LOCAL-PREFLIGHT-ONLY`; all nine gates remain red.

- [ ] **Step 4: Pause for explicit remote-write authorization**

Pushing `G`, opening a PR, configuring controls, or asking the external validator to append an Acceptance-Receipt changes external state and requires a separate operator instruction. If absent, stop with the local candidate and do not claim Genesis acceptance.

- [ ] **Step 5: Verify the externally returned Receipt and Checkpoint offline**

After authorized external integration, obtain the signed full-prefix bundle and external public pins through the protected channel. Run `check:governance-remote` with exact `G` Head/Tree and trusted time. Expected: Receipt covers every Genesis attestation exactly once, active TCB bootstrap digests match Pre-Ledger, full prefix/Merkle/checkpoint/floors verify, and all gates still remain red.

### Task 8: Review and close Plan 12

**Files:** No intended source changes after `G`; any implementation correction invalidates the ceremony and requires a new `I` and `G`, never an in-place edit of signed bytes.

- [ ] **Step 1: Run the sequential post-Genesis local gates**

```powershell
npm run check:canon
npm run check:governance -- --base $env:AURELIA_IMPLEMENTATION_COMMIT --head $env:AURELIA_GENESIS_COMMIT --external-pins $env:AURELIA_EXTERNAL_PINS_FILE --local-preflight
npm run typecheck:governance
npm run typecheck
npm run lint
npm test
git diff --check "$env:AURELIA_IMPLEMENTATION_COMMIT..$env:AURELIA_GENESIS_COMMIT"
git status --short
```

Expected: all exit 0; status empty; output says local preflight and nine red gates.

- [ ] **Step 2: Perform independent Genesis Spec Review**

Check design sections 6.2, 6.4, 12.5, 12.6, and 13, including D/I/G topology and every seed ID. Expected: approved with no open P0-P2.

- [ ] **Step 3: Perform independent Genesis Quality/Security Review**

Attack commit/self-hash cycles, repository-derived pins, single signature, key self-introduction, nonce reuse, wrong Core projection, altered signed bytes, hidden private key, missing Witness, wrong failure domain, topological seed error, and any non-red gate. Expected: approved with no open P0-P2.

- [ ] **Step 4: Apply the immutable-correction rule**

A finding in constructors/tests before `I` is fixed with a new implementation commit and complete ceremony restart. A finding in unsigned seed rendering before `G` restarts generation/signature verification. A finding after `G` is never fixed by rewriting history; create a formally reviewed successor sequence under the ledger rules.

- [ ] **Step 5: Record the Genesis boundary**

The handoff records D, I, G, both bootstrap artifact hashes, external Receipt/checkpoint IDs when available, and the fact that all nine Gates are red. No product data, database migration, server access, CUDA, USB, or external-model call occurred.
