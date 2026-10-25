# AURELIA G0 Cryptographic Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the offline-verifiable RFC-8785, SHA-256, Ed25519, trust-root, attestation, final-design-approval, and pre-ledger bootstrap contracts without creating live keys or signatures.

**Architecture:** A small cryptographic core wraps the pinned JCS dependency, produces canonical bytes, and verifies externally supplied signatures; closed Draft-2020-12 schemas reject structural drift before semantic validation. The bootstrap validator is pure and dependency-injected only through its internal test surface, while production always uses Node's Ed25519 verifier and externally supplied pins. This plan validates the D→I→offline-artifacts→G order but deliberately stops before every real ceremony and before Genesis.

**Tech Stack:** Node.js 22 ESM, `node:crypto`, the directly pinned `canonicalize@4.0.0` package from Plan 01, JSON Schema Draft 2020-12 through the schema registry from Plan 02, Node test runner, Git plumbing, RFC 8785, RFC 8032.

---

## Scope, prerequisites, and authority boundaries

Plans 01–04 must already provide `scripts/governance-contract.mjs`,
`scripts/governance/schema-registry.mjs` with `validateSchema(schemaName,
value)`, and the offline test runner. This plan creates no private key, signs no
payload, writes no bootstrap artifact, changes no remote, and does not create
Genesis records.

The implementation must enforce this exact chronology:

1. **D** — immutable design commit
   `a6a8e7dca456d14a6748b204b787b235fdedf9be` containing design bytes with
   SHA-256
   `30c7484753972020dec25083e038a2a1a6ab15a0b3f8885579ce4fa6e3727eb1`.
2. **I** — a later, separately reviewed `governanceImplementationCommit`
   containing validator, schemas, directives, and tests, but no live Genesis.
3. **Offline artifacts** — only after I exists, authorized humans/services
   produce `final-design-approval.json`, external pins, and the doubly signed
   `pre-ledger-trust-bundle.json` that binds D and I.
4. **G** — a later Genesis commit applies the exact three-event bootstrap to
   I and includes the already completed offline artifacts.

The validator returns a blocking `AUTHORITY_REQUIRED` result when any external
pin or signed artifact is absent. It must never generate a substitute.

## File map

**Modify (created by Plan 02 and already consumed by Plan 03):**

- `scripts/governance/raw-json.mjs` — verify and extend duplicate-object-name rejection before `JSON.parse` without changing its public contract.
- `scripts/governance/ijson.mjs` — verify and extend fail-closed I-JSON validation without changing its public contract.
- `scripts/governance/rfc8785.mjs` — verify the Plan-02 wrapper around pinned `canonicalize@4.0.0`; never replace it or create a second canonicalizer.

**Create:**
- `scripts/governance/crypto.mjs` — SHA-256, base64url length checks, Ed25519 verification.
- `scripts/governance/bootstrap-validator-internal.mjs` — pure semantic core with injected verification, imported only by wrapper and tests.
- `scripts/governance/bootstrap-validator.mjs` — production wrapper fixed to Node Ed25519 verification.
- `scripts/governance/crypto.test.mjs`
- `scripts/governance/bootstrap-validator.test.mjs`
- `scripts/governance/schema-builders/cryptographic.mjs`
- `scripts/fixtures/governance/rfc8785/core.json`
- `scripts/fixtures/governance/rfc8032/verify-empty-message.json`
- `scripts/fixtures/governance/bootstrap/semantic-valid.json`
- `docs/governance/schemas/trust-roots.schema.json`
- `docs/governance/schemas/event-attestation.schema.json`
- `docs/governance/schemas/pre-ledger-trust-bundle.schema.json`
- `docs/governance/schemas/final-design-approval.schema.json`

**Modify:**

- `scripts/governance/rfc8785.test.mjs` — extend the Plan-02 suite with only the missing RFC/mutation vectors.
- `scripts/governance-contract.mjs` — invoke `validateCryptographicBootstrap` after schema/register validation.
- `scripts/governance-contract.test.mjs` — prove absent external ceremony remains a red preflight, not a false pass.

## Fixed interfaces

```js
// scripts/governance/rfc8785.mjs
export function canonicalize(value) {}       // returns a string
export function canonicalBytes(value) {}     // returns Buffer

// scripts/governance/raw-json.mjs
export function parseUniqueJson(rawBytes) {} // rejects duplicate names before JSON.parse

// scripts/governance/crypto.mjs
export function sha256Hex(bytes) {}
export function fullArtifactSha256(value) {}
export function assertBase64urlBytes(value, expectedLength, field) {}
export function verifyEd25519({ publicKeyBase64url, payloadBytes, signatureBase64url }) {}

// scripts/governance/bootstrap-validator.mjs
export function validateCryptographicBootstrap({
  repositoryRoot,
  designCommit,
  implementationCommit,
  finalApproval,
  preLedgerBundle,
  trustRoots,
  attestations,
  events,
  validatedTransitionReplay,
  externalPins,
}) {} // returns cryptographic validity only; raw pins can never be gate-effective
```

Production callers cannot pass or override `verifySignature`.
`bootstrap-validator.mjs` supplies `verifyEd25519` in its module body. Only
that wrapper and `bootstrap-validator.test.mjs` may import
`bootstrap-validator-internal.mjs`; a source invariant enforces the allowlist.

## Complete closed-schema builder used by Tasks 3 and 4

Create `scripts/governance/schema-builders/cryptographic.mjs` with the
following complete builder. The generated files remain pure JSON; the schema
test rebuilds in memory and requires byte-equivalent parsed JSON.

```js
import { mkdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

const HEX64 = { type: "string", pattern: "^[0-9a-f]{64}$" };
const COMMIT = { type: "string", pattern: "^[0-9a-f]{40}$" };
const KEY_ID = { type: "string", pattern: "^KEY-[A-Z0-9]+(?:-[A-Z0-9]+)*$" };
const KEYREV_ID = { type: "string", pattern: "^KEYREV-[0-9]{6}$" };
const EVT_ID = { type: "string", pattern: "^EVT-[0-9]{6}$" };
const ROLE_ID = { type: "string", pattern: "^ROLE-[A-Z0-9]+(?:-[A-Z0-9]+)*$" };
const TIMESTAMP = { type: "string", pattern: "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\\.[0-9]{3}Z$" };
const B64_32 = { type: "string", pattern: "^[A-Za-z0-9_-]{43}$" };
const B64_64 = { type: "string", pattern: "^[A-Za-z0-9_-]{86}$" };
const IMAGE = { type: "string", pattern: "^sha256:[0-9a-f]{64}$" };
const TEXT = { type: "string", minLength: 1 };
const NIL = { type: "null" };
const nullable = (schema) => ({ anyOf: [schema, NIL] });
const closed = (properties, required = Object.keys(properties)) => ({
  type: "object", additionalProperties: false, required, properties,
});
const arrayOf = (items, minItems = 0) => ({ type: "array", items, minItems, uniqueItems: true });
const base = (id) => ({
  $schema: "https://json-schema.org/draft/2020-12/schema",
  $id: `https://aurelia.invalid/governance/${id}`,
});

const roleKey = closed({
  keyRef: KEY_ID, roleRef: ROLE_ID, assigneeRef: TEXT,
  algorithm: { const: "ed25519" }, publicKeyBase64url: B64_32,
  fingerprintSha256: HEX64,
});
const controllerKey = closed({
  keyRef: KEY_ID, controllerIdentity: TEXT, algorithm: { const: "ed25519" },
  publicKeyBase64url: B64_32, fingerprintSha256: HEX64,
});
const recoveryApp = closed({
  appIdentity: TEXT, keyRef: KEY_ID, algorithm: { const: "ed25519" },
  publicKeyBase64url: B64_32, fingerprintSha256: HEX64, imageDigest: IMAGE,
  policySha256: HEX64, permissionsSha256: HEX64,
  providerInstallationIdentitySha256: HEX64,
});
const servicePin = closed({
  serviceIdentity: TEXT, keyRef: KEY_ID, algorithm: { const: "ed25519" },
  publicKeyBase64url: B64_32, fingerprintSha256: HEX64, imageDigest: IMAGE,
  policySha256: HEX64, permissionsSha256: HEX64,
  providerInstallationIdentitySha256: nullable(HEX64),
  providerCredentialIdentitySha256: nullable(HEX64),
  trustedTimeSourceSha256: HEX64, failureDomain: TEXT,
});
const instanceKey = closed({
  keyRef: KEY_ID, logId: TEXT, keyEpoch: { const: 1 }, algorithm: { const: "ed25519" },
  publicKeyBase64url: B64_32, fingerprintSha256: HEX64,
});
const witnessKey = closed({
  witnessId: TEXT, keyRef: KEY_ID, operatorIdentity: TEXT, failureDomain: TEXT,
  algorithm: { const: "ed25519" }, publicKeyBase64url: B64_32,
  fingerprintSha256: HEX64,
});

export function trustRootsSchema() {
  const key = closed({
    id: KEY_ID, roleRef: ROLE_ID, assigneeRef: TEXT, algorithm: { const: "ed25519" },
    publicKeyBase64url: B64_32, fingerprintSha256: HEX64,
    validFrom: TIMESTAMP, validUntil: nullable(TIMESTAMP), introducedByEventRef: EVT_ID,
  });
  const revocation = closed({
    id: KEYREV_ID, keyRef: KEY_ID, revokedAt: TIMESTAMP, reason: TEXT,
    revokedByEventRef: EVT_ID, supersededByKeyRef: nullable(KEY_ID),
  });
  return { ...base("trust-roots.schema.json"), ...closed({
    schemaVersion: { const: "aurelia-governance-v1" },
    keys: arrayOf(key), revocations: arrayOf(revocation),
  }) };
}

export function eventAttestationSchema() {
  return { ...base("event-attestation.schema.json"), ...closed({
    method: { const: "ed25519" },
    attestationPurpose: { enum: ["actor", "approver", "incoming-operator", "recovery-root", "custodian-a", "custodian-b", "incoming-custodian-a", "incoming-custodian-b"] },
    keyRef: KEY_ID, signerIdentity: TEXT, signerRole: ROLE_ID,
    signedAt: TIMESTAMP, nonce: B64_32, envelopeSha256: HEX64, signature: B64_64,
  }) };
}

export function finalDesignApprovalSchema() {
  return { ...base("final-design-approval.schema.json"), ...closed({
    schemaVersion: { const: "aurelia-governance-v1" },
    repositoryId: { const: "redshift-three67/aurelia" }, approvalText: TEXT,
    designCommit: COMMIT,
    designSpecPath: { const: "docs/superpowers/specs/2026-08-24-aurelia-g0-governance-design.md" },
    designSpecSha256: HEX64, approvalScope: { const: "AURELIA-G0-GOVERNANCE-DESIGN" },
    operatorIdentity: TEXT, operatorRole: { const: "ROLE-OPERATOR" },
    operatorKeyRef: KEY_ID, operatorKeyFingerprint: HEX64,
    method: { const: "ed25519" }, issuedAt: TIMESTAMP, nonce: B64_32, signature: B64_64,
  }) };
}

export function preLedgerTrustBundleSchema() {
  return { ...base("pre-ledger-trust-bundle.schema.json"), ...closed({
    schemaVersion: { const: "aurelia-governance-v1" },
    repositoryId: { const: "redshift-three67/aurelia" },
    designBaselineCommit: COMMIT, designCommit: COMMIT,
    designSpecPath: { const: "docs/superpowers/specs/2026-08-24-aurelia-g0-governance-design.md" },
    designSpecSha256: HEX64, governanceImplementationCommit: COMMIT,
    operatorKey: roleKey, recoveryRootKey: roleKey, orchestratorKey: roleKey,
    validatorControllerKey: controllerKey, recoveryApp,
    recoveryWriteAheadGateway: servicePin, providerRefVerifier: servicePin,
    egressEnforcementMonitor: servicePin, transparencyInstanceKey: instanceKey,
    witnessKeys: arrayOf(witnessKey, 2),
    finalApprovalPath: { const: "docs/governance/bootstrap/final-design-approval.json" },
    finalApprovalSha256: HEX64, bootstrapValidatorImageDigest: IMAGE,
    bootstrapValidatorPolicySha256: HEX64, bootstrapWorkflowSha256: HEX64,
    bootstrapSchemaSetSha256: HEX64, bootstrapTrustProtocolSha256: HEX64,
    genesisEventIds: { const: ["EVT-000001", "EVT-000002", "EVT-000003"] },
    issuedAt: TIMESTAMP, nonce: B64_32,
    operatorSignature: B64_64, recoveryRootSignature: B64_64,
  }) };
}

export const cryptographicSchemas = Object.freeze({
  "trust-roots.schema.json": trustRootsSchema(),
  "event-attestation.schema.json": eventAttestationSchema(),
  "final-design-approval.schema.json": finalDesignApprovalSchema(),
  "pre-ledger-trust-bundle.schema.json": preLedgerTrustBundleSchema(),
});

export async function writeCryptographicSchemas(root) {
  const target = resolve(root, "docs/governance/schemas");
  await mkdir(target, { recursive: true });
  for (const [name, schema] of Object.entries(cryptographicSchemas)) {
    await writeFile(resolve(target, name), `${JSON.stringify(schema, null, 2)}\n`, "utf8");
  }
}
```

### Task 1: Verify and extend the Plan-02 RFC-8785 boundary

**Files:**

- Create: `scripts/fixtures/governance/rfc8785/core.json`
- Modify: `scripts/governance/rfc8785.test.mjs`
- Modify: `scripts/governance/raw-json.mjs`
- Modify: `scripts/governance/ijson.mjs`
- Modify: `scripts/governance/rfc8785.mjs`

- [ ] **Step 1: Add the independent golden fixture**

Create `core.json` with exact UTF-8 content:

```json
{
  "cases": [
    {
      "name": "independently-fixed-property-order-and-unicode",
      "input": { "z": -0.0, "é": "€", "a": [3, 2, 1] },
      "canonical": "{\"a\":[3,2,1],\"z\":0,\"é\":\"€\"}",
      "sha256": "28a0dc367b679d5d565f6a416e0602dcbdb3887a6780e14c2495577110cfa302"
    }
  ]
}
```

The digest above has been independently confirmed with `createHash` over the
literal canonical UTF-8 bytes and must not be regenerated through the
implementation under test. Add the RFC 8785 Appendix B number vectors and
the implementation reference selected from Appendix G beside this project
vector; Appendix G itself is not treated as a source of golden bytes.

- [ ] **Step 2: Write the failing canonicalization test**

```js
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { test } from "node:test";
import { canonicalize, canonicalBytes } from "./rfc8785.mjs";
import { sha256Hex } from "./crypto.mjs";
import { parseUniqueJson } from "./raw-json.mjs";

const fixture = JSON.parse(await readFile(
  new URL("../fixtures/governance/rfc8785/core.json", import.meta.url),
  "utf8",
));

test("RFC 8785 golden bytes and digest are stable", () => {
  for (const vector of fixture.cases) {
    assert.equal(canonicalize(vector.input), vector.canonical, vector.name);
    assert.equal(sha256Hex(canonicalBytes(vector.input)), vector.sha256, vector.name);
  }
});

test("canonicalization rejects non-JSON inputs", () => {
  for (const value of [undefined, 1n, Number.NaN, Infinity, -Infinity]) {
    assert.throws(() => canonicalize(value), /not RFC-8785 JSON/);
  }
});

test("raw JSON rejects duplicate decoded property names before JSON.parse", () => {
  for (const raw of [
    '{"a":1,"a":2}',
    '{"a":1,"\\u0061":2}',
    '{"nested":{"x":1,"x":2}}',
  ]) assert.throws(() => parseUniqueJson(Buffer.from(raw)), /duplicate property/);
});

test("I-JSON rejects lone surrogates in keys and values", () => {
  assert.throws(() => canonicalize({ "\ud800": "x" }), /lone surrogate/);
  assert.throws(() => canonicalize({ key: "\udfff" }), /lone surrogate/);
});
```

- [ ] **Step 3: Run the focused test and confirm RED**

Run:

```powershell
node --test scripts/governance/rfc8785.test.mjs
```

Expected: FAIL only for the newly added RFC/mutation assertions. If an import
is missing, STOP: Plan 02 is incomplete and Plan 05 may not take ownership of
these modules.

- [ ] **Step 4: Compare and extend the existing raw duplicate-key gate**

Implement a single-pass JSON tokenizer that tracks an independent decoded-key
set for every object scope before calling `JSON.parse`. It must recognize the
full JSON string escape grammar, decode each property token with `JSON.parse`,
reject `"a"` plus `"\u0061"` as a duplicate, reject trailing tokens and BOM,
and report the byte offset for malformed strings, numbers, commas, colons, or
nesting. Arrays do not create property-name sets.

```js
import { TextDecoder } from "node:util";

function scanJsonAndRejectDuplicateProperties(raw) {
  let offset = 0;
  const fail = (message) => { throw new SyntaxError(`${message} at byte ${offset}`); };
  const skipWhitespace = () => {
    while (offset < raw.length && /[\u0009\u000a\u000d\u0020]/.test(raw[offset])) offset += 1;
  };
  const parseStringToken = () => {
    if (raw[offset] !== '"') fail("expected JSON string");
    const start = offset++;
    while (offset < raw.length) {
      const code = raw.charCodeAt(offset);
      if (code < 0x20) fail("unescaped control character");
      if (raw[offset] === '"') {
        offset += 1;
        return JSON.parse(raw.slice(start, offset));
      }
      if (raw[offset] === "\\") {
        offset += 1;
        if (offset >= raw.length) fail("truncated escape");
        if (raw[offset] === "u") {
          const hex = raw.slice(offset + 1, offset + 5);
          if (!/^[0-9a-fA-F]{4}$/.test(hex)) fail("invalid unicode escape");
          offset += 5;
          continue;
        }
        if (!'"\\/bfnrt'.includes(raw[offset])) fail("invalid string escape");
      }
      offset += 1;
    }
    fail("unterminated JSON string");
  };
  const parseNumber = () => {
    const match = /^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/.exec(raw.slice(offset));
    if (!match) fail("invalid JSON number");
    offset += match[0].length;
  };
  const parseLiteral = (literal) => {
    if (!raw.startsWith(literal, offset)) fail(`expected ${literal}`);
    offset += literal.length;
  };
  const parseArray = () => {
    offset += 1;
    skipWhitespace();
    if (raw[offset] === "]") { offset += 1; return; }
    for (;;) {
      parseValue();
      skipWhitespace();
      if (raw[offset] === "]") { offset += 1; return; }
      if (raw[offset] !== ",") fail("expected comma or array end");
      offset += 1;
      skipWhitespace();
    }
  };
  const parseObject = () => {
    offset += 1;
    const keys = new Set();
    skipWhitespace();
    if (raw[offset] === "}") { offset += 1; return; }
    for (;;) {
      const key = parseStringToken();
      if (keys.has(key)) fail(`duplicate property ${JSON.stringify(key)}`);
      keys.add(key);
      skipWhitespace();
      if (raw[offset] !== ":") fail("expected colon");
      offset += 1;
      parseValue();
      skipWhitespace();
      if (raw[offset] === "}") { offset += 1; return; }
      if (raw[offset] !== ",") fail("expected comma or object end");
      offset += 1;
      skipWhitespace();
    }
  };
  const parseValue = () => {
    skipWhitespace();
    if (raw[offset] === "{") return parseObject();
    if (raw[offset] === "[") return parseArray();
    if (raw[offset] === '"') { parseStringToken(); return; }
    if (raw[offset] === "t") return parseLiteral("true");
    if (raw[offset] === "f") return parseLiteral("false");
    if (raw[offset] === "n") return parseLiteral("null");
    parseNumber();
  };
  parseValue();
  skipWhitespace();
  if (offset !== raw.length) fail("trailing JSON token");
}

export function parseUniqueJson(rawBytes) {
  const raw = new TextDecoder("utf-8", { fatal: true }).decode(Buffer.from(rawBytes));
  if (raw.charCodeAt(0) === 0xfeff) throw new SyntaxError("BOM is forbidden at byte 0");
  scanJsonAndRejectDuplicateProperties(raw);
  return JSON.parse(raw);
}
```

- [ ] **Step 5: Wrap `canonicalize@4.0.0` with an I-JSON prevalidator**

Do not implement a JCS encoder. `assertIJson` recursively rejects non-finite
numbers, lone UTF-16 surrogates in keys or values, sparse arrays, cycles,
non-plain objects, `undefined`, bigint, functions, and symbols. It performs no
Unicode normalization. Canonical serialization is delegated exclusively to
the dependency pinned in Plan 01:

```js
// ijson.mjs
function assertScalarString(value, path) {
  for (let index = 0; index < value.length; index += 1) {
    const code = value.charCodeAt(index);
    if (code >= 0xd800 && code <= 0xdbff) {
      const next = value.charCodeAt(index + 1);
      if (!(next >= 0xdc00 && next <= 0xdfff)) {
        throw new TypeError(`${path}: lone surrogate`);
      }
      index += 1;
    } else if (code >= 0xdc00 && code <= 0xdfff) {
      throw new TypeError(`${path}: lone surrogate`);
    }
  }
}

function visit(value, path, ancestors) {
  if (value === null || typeof value === "boolean") return;
  if (typeof value === "string") { assertScalarString(value, path); return; }
  if (typeof value === "number") {
    if (!Number.isFinite(value)) throw new TypeError(`${path}: non-finite number`);
    return;
  }
  if (typeof value !== "object") throw new TypeError(`${path}: unsupported I-JSON type`);
  if (ancestors.has(value)) throw new TypeError(`${path}: cyclic value`);
  ancestors.add(value);
  try {
    if (Array.isArray(value)) {
      const keys = Object.keys(value);
      if (keys.length !== value.length || keys.some((key, index) => key !== String(index))) {
        throw new TypeError(`${path}: sparse or extended array`);
      }
      value.forEach((item, index) => visit(item, `${path}/${index}`, ancestors));
      return;
    }
    if (Object.getPrototypeOf(value) !== Object.prototype) {
      throw new TypeError(`${path}: non-plain object`);
    }
    for (const key of Reflect.ownKeys(value)) {
      if (typeof key !== "string") throw new TypeError(`${path}: symbol property`);
      const descriptor = Object.getOwnPropertyDescriptor(value, key);
      if (!descriptor?.enumerable || !("value" in descriptor)) {
        throw new TypeError(`${path}/${key}: accessor or non-enumerable property`);
      }
      assertScalarString(key, `${path}/<key>`);
      visit(value[key], `${path}/${key}`, ancestors);
    }
  } finally {
    ancestors.delete(value);
  }
}

export function assertIJson(value) { visit(value, "$", new Set()); }
```

```js
// rfc8785.mjs
import { Buffer } from "node:buffer";
import canonicalizeJcs from "canonicalize";
import { assertIJson } from "./ijson.mjs";

export function canonicalize(value) {
  assertIJson(value);
  const encoded = canonicalizeJcs(value);
  if (typeof encoded !== "string") {
    throw new TypeError("canonicalize returned no RFC-8785 string");
  }
  return encoded;
}
export function canonicalBytes(value) { return Buffer.from(canonicalize(value), "utf8"); }
```

- [ ] **Step 6: Add RFC-8785 boundary and mutation vectors**

Use literal expected bytes from the RFC 8785 main example and Appendix B for
UTF-16 property order, escaped controls and quotes, exponent formatting, safe-integer boundary,
subnormal numbers, and negative zero. Add rejection mutations for lone
surrogates, duplicate escaped keys, non-finite values, sparse arrays, cycles,
and non-plain values. Appendix G only justifies the pinned implementation
choice; it is not a source of golden vectors. Expected bytes may not be
generated by `canonicalize`.

- [ ] **Step 7: Run the focused test and confirm GREEN**

Run the same command. Expected: all RFC-8785 tests PASS.

- [ ] **Step 8: Commit the canonicalization unit**

```powershell
git add scripts/governance/raw-json.mjs scripts/governance/ijson.mjs scripts/governance/rfc8785.mjs scripts/governance/rfc8785.test.mjs scripts/fixtures/governance/rfc8785/core.json
git commit -m "feat: add RFC 8785 governance canonicalization"
```

### Task 2: Verify RFC-8032 signatures without key synthesis

**Files:**

- Create: `scripts/fixtures/governance/rfc8032/verify-empty-message.json`
- Create: `scripts/governance/crypto.test.mjs`
- Create: `scripts/governance/crypto.mjs`

- [ ] **Step 1: Store RFC-8032 test vector 1 as verification-only data**

```json
{
  "publicKeyBase64url": "11qYAYKxCrfVS_7TyWQHOg7hcvPapiMlrwIaaPcHURo",
  "messageBase64url": "",
  "signatureBase64url": "5VZDAMNgrHKQhuLMgG6CioSHfx645dl02HPgZSJJAVVfuIIVkKM7rMYeOXAc-bRr0lv18FlbviRlUUFDjnoQCw"
}
```

No private key is checked in or generated.

- [ ] **Step 2: Write positive and one-bit mutation tests**

```js
test("RFC 8032 vector verifies and a one-bit signature mutation fails", async () => {
  const vector = JSON.parse(await readFile(FIXTURE_URL, "utf8"));
  const payloadBytes = Buffer.from(vector.messageBase64url, "base64url");
  assert.equal(verifyEd25519({ ...vector, payloadBytes }), true);
  const bytes = Buffer.from(vector.signatureBase64url, "base64url");
  bytes[63] ^= 1;
  assert.equal(verifyEd25519({
    publicKeyBase64url: vector.publicKeyBase64url,
    payloadBytes,
    signatureBase64url: bytes.toString("base64url"),
  }), false);
});

test("base64url contracts reject padding and wrong byte lengths", () => {
  assert.throws(() => assertBase64urlBytes("AA==", 1, "nonce"), /base64url/);
  assert.throws(() => assertBase64urlBytes("AA", 32, "key"), /32 bytes/);
});
```

- [ ] **Step 3: Run the test and confirm RED**

Run `node --test scripts/governance/crypto.test.mjs`.
Expected: FAIL because the crypto exports do not exist.

- [ ] **Step 4: Implement SHA-256 and Ed25519 verification**

Use the DER SPKI prefix `302a300506032b6570032100` before the raw 32-byte
Ed25519 key and `crypto.verify(null, payload, publicKey, signature)`. The
function must return `false` for a cryptographically invalid signature but
throw for malformed encoding or length.

```js
import { createHash, createPublicKey, verify } from "node:crypto";
import { canonicalBytes } from "./rfc8785.mjs";

const ED25519_SPKI_PREFIX = Buffer.from("302a300506032b6570032100", "hex");
export const sha256Hex = (bytes) => createHash("sha256").update(bytes).digest("hex");
export const fullArtifactSha256 = (value) => sha256Hex(canonicalBytes(value));

export function assertBase64urlBytes(value, expectedLength, field) {
  if (typeof value !== "string" || value.includes("=") || !/^[A-Za-z0-9_-]*$/.test(value)) {
    throw new TypeError(`${field}: invalid base64url without padding`);
  }
  const bytes = Buffer.from(value, "base64url");
  if (bytes.length !== expectedLength || bytes.toString("base64url") !== value) {
    throw new TypeError(`${field}: expected ${expectedLength} bytes`);
  }
  return bytes;
}

export function verifyEd25519({ publicKeyBase64url, payloadBytes, signatureBase64url }) {
  const rawKey = assertBase64urlBytes(publicKeyBase64url, 32, "publicKeyBase64url");
  const signature = assertBase64urlBytes(signatureBase64url, 64, "signatureBase64url");
  const publicKey = createPublicKey({
    key: Buffer.concat([ED25519_SPKI_PREFIX, rawKey]), format: "der", type: "spki",
  });
  return verify(null, Buffer.from(payloadBytes), publicKey, signature);
}
```

- [ ] **Step 5: Run the test and confirm GREEN**

Expected: RFC-8032 positive test PASS, mutated signature returns `false`, malformed inputs throw.

- [ ] **Step 6: Commit the verification primitive**

```powershell
git add scripts/governance/crypto.mjs scripts/governance/crypto.test.mjs scripts/fixtures/governance/rfc8032/verify-empty-message.json
git commit -m "feat: verify governance Ed25519 artifacts"
```

### Task 3: Add closed trust-root and detached-attestation schemas

**Files:**

- Create: `docs/governance/schemas/trust-roots.schema.json`
- Create: `docs/governance/schemas/event-attestation.schema.json`
- Modify: `scripts/governance/bootstrap-validator.test.mjs`

- [ ] **Step 1: Write schema RED tests**

Add fixtures inline for one valid public key/revocation document and one valid
detached attestation. Mutate, one at a time: padding, 31-byte key, unknown
property, private-key-like property, duplicate KEY ID, wrong role, and a
signature shorter than 64 bytes. Each mutation must produce one path-specific
schema error.

- [ ] **Step 2: Run the schema tests and confirm RED**

Run:

```powershell
node --test --test-name-pattern="trust-root|detached attestation" scripts/governance/bootstrap-validator.test.mjs
```

Expected: FAIL because both schema files are absent.

- [ ] **Step 3: Generate the closed trust-root schema from the complete builder**

The root has exactly `schemaVersion`, `keys`, and `revocations`. Each key has
exactly `id`, `roleRef`, `assigneeRef`, `algorithm`, `publicKeyBase64url`,
`fingerprintSha256`, `validFrom`, `validUntil`, and
`introducedByEventRef`. Each revocation has exactly `id`, `keyRef`,
`revokedAt`, `reason`, `revokedByEventRef`, and `supersededByKeyRef`.
Use `trustRootsSchema()` from the complete builder above and run
`writeCryptographicSchemas(repositoryRoot)`. Do not hand-maintain a second
field list. The schema test compares parsed generated JSON with the builder
result and separately exercises decoded byte lengths semantically.

- [ ] **Step 4: Generate the detached-attestation schema from the complete builder**

The artifact is the exact EVT `authorizationAttestations` object with fields
`method`, `attestationPurpose`, `keyRef`, `signerIdentity`, `signerRole`,
`signedAt`, `nonce`, `envelopeSha256`, and `signature`. Use
`eventAttestationSchema()`; the builder closes the purpose enum and every
property. Add a test that a generated schema file differs from the in-memory
builder result only in insignificant JSON whitespace.

- [ ] **Step 5: Run the schema tests and confirm GREEN**

Expected: valid fixtures pass; every added, missing, mistyped, padded, or wrong-length field fails.

- [ ] **Step 6: Commit both schema contracts**

```powershell
git add docs/governance/schemas/trust-roots.schema.json docs/governance/schemas/event-attestation.schema.json scripts/governance/schema-builders/cryptographic.mjs scripts/governance/bootstrap-validator.test.mjs
git commit -m "feat: define governance trust-root schemas"
```

### Task 4: Add final-approval and pre-ledger schemas

**Files:**

- Create: `docs/governance/schemas/final-design-approval.schema.json`
- Create: `docs/governance/schemas/pre-ledger-trust-bundle.schema.json`
- Modify: `scripts/governance/bootstrap-validator.test.mjs`

- [ ] **Step 1: Add exact-field schema tests**

Build a semantic fixture whose final approval has exactly these 15 full-
artifact fields: `schemaVersion`, `repositoryId`, `approvalText`,
`designCommit`, `designSpecPath`, `designSpecSha256`, `approvalScope`,
`operatorIdentity`, `operatorRole`, `operatorKeyRef`,
`operatorKeyFingerprint`, `method`, `issuedAt`, `nonce`, and `signature`.
Its pre-ledger bundle has exactly these 29 top-level fields:
`schemaVersion`, `repositoryId`, `designBaselineCommit`, `designCommit`,
`designSpecPath`, `designSpecSha256`, `governanceImplementationCommit`,
`operatorKey`, `recoveryRootKey`, `orchestratorKey`,
`validatorControllerKey`, `recoveryApp`, `recoveryWriteAheadGateway`,
`providerRefVerifier`, `egressEnforcementMonitor`,
`transparencyInstanceKey`, `witnessKeys`, `finalApprovalPath`,
`finalApprovalSha256`, `bootstrapValidatorImageDigest`,
`bootstrapValidatorPolicySha256`, `bootstrapWorkflowSha256`,
`bootstrapSchemaSetSha256`, `bootstrapTrustProtocolSha256`,
`genesisEventIds`, `issuedAt`, `nonce`, `operatorSignature`, and
`recoveryRootSignature`. The nested key/service/witness objects use the exact
closed field sets from §6.4. Add mutations for wrong repository,
seven-character commit, one witness,
same failure domain, nullable gateway credential, non-null verifier credential,
wrong image digest, and an added `privateKey` property.

- [ ] **Step 2: Run and confirm RED**

Expected: both missing schemas make the focused tests fail.

- [ ] **Step 3: Generate `final-design-approval.schema.json`**

Invoke `finalDesignApprovalSchema()` from the complete builder. It requires the
exact repository, scope, method, fixed design path, full commit and hash forms,
timestamp, nonce, and signature. `approvalText` remains structurally nonempty;
semantic validation enforces the exact D/hash sentence.

- [ ] **Step 4: Generate `pre-ledger-trust-bundle.schema.json`**

Invoke `preLedgerTrustBundleSchema()` from the complete builder. Semantic
validation additionally enforces witness sorting and pairwise distinct
identities/domains/keys/fingerprints, Gateway non-null installation/credential,
Verifier same installation with null credential, and Monitor provider fields
null; these cross-object conditions are not weakened into schema annotations.

- [ ] **Step 5: Run and confirm GREEN**

Expected: both canonical structures pass and each field/domain/credential mutation fails.

- [ ] **Step 6: Commit the bootstrap schemas**

```powershell
git add docs/governance/schemas/final-design-approval.schema.json docs/governance/schemas/pre-ledger-trust-bundle.schema.json scripts/governance/bootstrap-validator.test.mjs
git commit -m "feat: define G0 bootstrap artifact schemas"
```

### Task 5: Validate D→I→offline-artifacts→G semantics

**Files:**

- Create: `scripts/fixtures/governance/bootstrap/semantic-valid.json`
- Create: `scripts/governance/bootstrap-validator-internal.mjs`
- Create: `scripts/governance/bootstrap-validator.mjs`
- Modify: `scripts/governance/bootstrap-validator.test.mjs`

- [ ] **Step 1: Write pure semantic tests with an injected verifier**

The fixture contains public-only dummy values of correct length. Pass
`verifySignature: () => true` only in these unit tests. Assert the exact design
commit/hash, `git merge-base --is-ancestor D I`, fixed artifact paths, identical
pins across final approval/bundle/external pins, two distinct witnesses, exact
Genesis IDs, and absence of private-key-shaped field names recursively.

- [ ] **Step 2: Add mutation tests for chronology and cycles**

Test I equal to D, I not descendant of D, final approval naming I instead of D,
bundle missing I, artifact claiming future G, bundle self-hash references,
single signature, key self-introduction, a future event's key authorizing an
earlier event, a key revoked by an earlier event authorizing a later event,
an EVT-000001 key differing by one public-pin field, `signedAt` exactly five
minutes plus 1 ms before and after `occurredAt`, different `logId`, key epoch
other than 1, and changed validator digest. Expected rule codes include
`BOOTSTRAP_ORDER`, `DESIGN_BINDING`, `IMPLEMENTATION_BINDING`,
`FUTURE_GENESIS`, `SELF_HASH`, `SIGNATURE_THRESHOLD`,
`ATTESTATION_KEY_PRESTATE`, `TRUST_ROOT_REVOCATION_PRESTATE`,
`ATTESTATION_KEY_STATE`, `LOG_PIN_MISMATCH`, and `TCB_PIN_MISMATCH`.
The positive sequence proves EVT-000001 only through its two exact external
pins, then applies each event's key additions/revocations after authenticating
that event, so EVT-000002 and every later event use the immediately prior
replayed Trust-Root state.

Mutate the Plan-03-branded record pre/poststate independently: missing ROLE,
unassigned/suspended ROLE, wrong assignee, actor key absent from
`attestationKeyRefs`, key bound to another `roleRef` or `assigneeRef`, future or
revoked key retained by an assigned ROLE, and a plain/copied/error replay
result. Require `ROLE_ATTESTATION_KEY_PRESTATE`, `ROLE_ACTIVE_KEY_BINDING`, or
the missing `validated-transition-replay` authority. The exact EVT-000001
externally pinned bootstrap exception remains the only event allowed to lack an
earlier ROLE/key prestate; its poststate must still establish the matching
assigned ROLE/key bindings.

Also introduce two simultaneously active Reviewer keys with distinct KEY IDs,
roles, and assignees but the same `publicKeyBase64url` and consequently the
same `fingerprintSha256`. Require `ACTIVE_KEY_MATERIAL_SEPARATION` immediately
after the second introduction; repeat once with a fingerprint alias mutation.
Rotation overlap is permitted only when both `roleRef` and `assigneeRef` are
identical.

Exercise the complete Plan-03 authorization matrix for planned Operator
handover, Recovery, initial/rotated Custodian A and B, and the later initial
Recovery-Root assignment. Incoming Operator/Custodian attestations must verify
against the key introduced in that same Event and the resulting assigned ROLE,
but mutation tests prove they never satisfy an old-key/Root/Custodian
authorization threshold. The initial Recovery-Root acceptance uses the
already EVT-000001-pinned/active external Root key and resulting ROLE while a
separate prestate-valid Operator actor authorizes the assignment. Reject a
future key, wrong resulting assignee/role, absent result keyRef, incoming
signature counted as authorization, or self-authorized root assignment with
`INCOMING_KEY_POSSESSION` or `INITIAL_RECOVERY_ROOT_ACCEPTANCE`.

Also mutate `designBaselineCommit`, add any second baseline→D path, change the
D blob, use padded/noncanonical 32-byte keys, mismatch every recomputed
fingerprint, alias/traverse/symlink an attestation path, revoke with neither
the old key nor Recovery-Root, and swap two Witness IDs at the non-ASCII
UTF-16 boundary (`"WITNESS-\uE000"` versus `"WITNESS-\uD800\uDC00"`). Assert
the explicit code-unit comparator, never locale collation. Build the three
Genesis events sequentially in the fixture: finish each offline attestation
set, compute that event's final `eventHash`, and only then place it into the
next event's `previousEventHash`. No implementation in Plans 05–08 may create
or pre-hash multiple unsigned chained events.

- [ ] **Step 3: Run and confirm RED**

Run `node --test scripts/governance/bootstrap-validator.test.mjs`.
Expected: semantic tests fail because `validateCryptographicBootstrap` is missing.

- [ ] **Step 4: Implement the internal validation pipeline**

Implement in this order: schema validation; fixed repository/path/hash checks;
Git ancestry/blob checks; external-pin comparison; key/fingerprint and service
separation; nonce collection; exact approval-text check; canonical core
projection; operator/root signature verification; detached-attestation
filename/object byte equality. Return all deterministic errors and a separate
`authorityRequired` list for missing real pins/artifacts.

The approval text comparison is exact:

```js
const expectedApprovalText =
  `AURELIA G0-Spezifikation ${designCommit} mit Dateihash ${designSpecSha256} final freigegeben`;
```

Use this complete core; `validateSchema` is the fixed Plan 02 export and the
remaining imports are implemented earlier in this plan:

```js
import { execFileSync } from "node:child_process";
import { lstatSync, realpathSync } from "node:fs";
import { posix, relative, resolve, sep } from "node:path";
import { canonicalBytes } from "./rfc8785.mjs";
import { assertBase64urlBytes, fullArtifactSha256, sha256Hex } from "./crypto.mjs";
import { validateSchema } from "./schema-registry.mjs";
import { readValidatedLedgerReplay } from "./transition-ledger.mjs";

const BASELINE = "b20ee873347c5fd767e2089c993f1cf93a625def";
const D = "a6a8e7dca456d14a6748b204b787b235fdedf9be";
const D_PATH = "docs/superpowers/specs/2026-08-24-aurelia-g0-governance-design.md";
const D_SHA = "30c7484753972020dec25083e038a2a1a6ab15a0b3f8885579ce4fa6e3727eb1";
const omit = (object, names) => Object.fromEntries(
  Object.entries(object).filter(([name]) => !names.includes(name)),
);
const equal = (left, right) =>
  canonicalBytes(left).equals(canonicalBytes(right));
const gitBlob = (root, commit, path) => execFileSync(
  "git", ["-C", root, "cat-file", "blob", `${commit}:${path}`], { encoding: null },
);
const isStrictAncestor = (root, ancestor, descendant) => {
  if (ancestor === descendant) return false;
  try {
    execFileSync("git", ["-C", root, "merge-base", "--is-ancestor", ancestor, descendant]);
    return true;
  } catch { return false; }
};
const changedPaths = (root, from, to) => execFileSync("git",
  ["-C", root, "diff", "--name-only", "-z", "--diff-filter=ACDMRTUXB", from, to],
  { encoding: "utf8" }).split("\0").filter(Boolean);
const compareUtf16 = (left, right) => {
  const limit = Math.min(left.length, right.length);
  for (let index = 0; index < limit; index += 1) {
    const delta = left.charCodeAt(index) - right.charCodeAt(index);
    if (delta) return delta;
  }
  return left.length - right.length;
};
function canonicalArtifactPath(root, candidate, expected) {
  try {
    if (candidate !== expected || candidate !== posix.normalize(candidate)
      || candidate.startsWith("/") || candidate.includes("\\") || candidate.split("/").includes("..")) return false;
    const rootReal = realpathSync(root);
    let current = rootReal;
    for (const component of candidate.split("/")) {
      current = resolve(current, component);
      if (lstatSync(current).isSymbolicLink()) return false;
    }
    const rel = relative(rootReal, realpathSync(current));
    return rel !== "" && !rel.startsWith(`..${sep}`) && rel !== "..";
  } catch { return false; }
}
function assertPinnedPublicKey(key, errors, path) {
  try {
    const raw = assertBase64urlBytes(key.publicKeyBase64url, 32, `${path}.publicKeyBase64url`);
    if (sha256Hex(raw) !== key.fingerprintSha256) {
      push(errors, "KEY_FINGERPRINT_MISMATCH", `${path}.fingerprintSha256`, "fingerprint must be recomputed from decoded public key bytes");
    }
  } catch (error) { push(errors, "KEY_ENCODING", path, error.message); }
}
function containsForbiddenKey(value) {
  if (!value || typeof value !== "object") return false;
  return Reflect.ownKeys(value).some((key) =>
    typeof key !== "string" || /private|secret|seed|mnemonic/i.test(key) || containsForbiddenKey(value[key]));
}
function push(errors, rule, path, message) { errors.push({ rule, path, message }); }
function verifyDetached({ artifact, publicKeyBase64url, payload, verifySignature, errors, path }) {
  let valid = false;
  try {
    valid = verifySignature({
      publicKeyBase64url,
      payloadBytes: canonicalBytes(payload),
      signatureBase64url: artifact.signature,
    });
  } catch (error) {
    push(errors, "SIGNATURE_ENCODING", path, error.message);
    return;
  }
  if (!valid) push(errors, "SIGNATURE_INVALID", path, "Ed25519 verification failed");
}

export function validateCryptographicBootstrapCore(args, { verifySignature }) {
  const errors = [];
  const authorityRequired = [];
  const {
    repositoryRoot, designCommit, implementationCommit, finalApproval,
    preLedgerBundle: bundle, trustRoots, attestations, events,
    validatedTransitionReplay, externalPins,
  } = args;
  if (!repositoryRoot) authorityRequired.push("repository-read-input");
  if (!designCommit) authorityRequired.push("design-commit-input");
  if (!implementationCommit) authorityRequired.push("implementation-commit-input");
  if (!finalApproval) authorityRequired.push("final-design-approval");
  if (!bundle) authorityRequired.push("pre-ledger-trust-bundle");
  if (!trustRoots) authorityRequired.push("trust-roots");
  if (!Array.isArray(attestations) || attestations.length === 0) authorityRequired.push("detached-attestation-set");
  if (!Array.isArray(events) || events.length < 3) authorityRequired.push("finished-seed-event-prefix");
  let ledgerReplay;
  try { ledgerReplay = readValidatedLedgerReplay(validatedTransitionReplay); }
  catch { authorityRequired.push("validated-transition-replay"); }
  if (!externalPins) authorityRequired.push("external-control-pins");
  if (authorityRequired.length) return { errors, authorityRequired, cryptographicValid: false, gateEffective: false };

  for (const error of validateSchema("final-design-approval", finalApproval)) errors.push(error);
  for (const error of validateSchema("pre-ledger-trust-bundle", bundle)) errors.push(error);
  for (const error of validateSchema("trust-roots", trustRoots)) errors.push(error);
  for (const item of attestations) {
    for (const error of validateSchema("event-attestation", item.artifact)) errors.push(error);
  }
  if (errors.length) return { errors, authorityRequired, cryptographicValid: false, gateEffective: false };
  if (events.slice(0, 3).map((event) => event.id).join("\u0000")
    !== bundle.genesisEventIds.join("\u0000")) {
    push(errors, "GENESIS_PREFIX", "$.events", "the exact Genesis triple must be the first three events; later seed events remain in the prefix");
  }
  if (containsForbiddenKey({ finalApproval, bundle, trustRoots, attestations })) {
    push(errors, "SECRET_FIELD", "$", "private or secret material is forbidden");
  }
  if (designCommit !== D || bundle.designCommit !== D || finalApproval.designCommit !== D) {
    push(errors, "DESIGN_BINDING", "$.designCommit", "design commit differs from D");
  }
  if (bundle.designBaselineCommit !== BASELINE || !isStrictAncestor(repositoryRoot, BASELINE, D)
    || changedPaths(repositoryRoot, BASELINE, D).join("\n") !== D_PATH) {
    push(errors, "DESIGN_BASELINE", "$.designBaselineCommit",
      "D must strictly descend from the fixed baseline and change only the approved design path");
  }
  if (implementationCommit !== bundle.governanceImplementationCommit ||
      !isStrictAncestor(repositoryRoot, D, implementationCommit)) {
    push(errors, "BOOTSTRAP_ORDER", "$.governanceImplementationCommit", "I must strictly descend from D");
  }
  const actualDesignSha = sha256Hex(gitBlob(repositoryRoot, D, D_PATH));
  if (actualDesignSha !== D_SHA || bundle.designSpecSha256 !== D_SHA ||
      finalApproval.designSpecSha256 !== D_SHA || bundle.designSpecPath !== D_PATH
      || finalApproval.designSpecPath !== D_PATH) {
    push(errors, "DESIGN_BINDING", "$.designSpecSha256", "design bytes differ from approved SHA-256");
  }
  const approvalText = `AURELIA G0-Spezifikation ${D} mit Dateihash ${D_SHA} final freigegeben`;
  if (finalApproval.approvalText !== approvalText) {
    push(errors, "DESIGN_BINDING", "$.approvalText", "approval sentence is not exact");
  }
  if (bundle.finalApprovalSha256 !== fullArtifactSha256(finalApproval)) {
    push(errors, "DESIGN_BINDING", "$.finalApprovalSha256", "approval full-artifact hash differs");
  }
  if (finalApproval.operatorIdentity !== bundle.operatorKey.assigneeRef
    || finalApproval.operatorRole !== bundle.operatorKey.roleRef
    || finalApproval.operatorKeyRef !== bundle.operatorKey.keyRef
    || finalApproval.operatorKeyFingerprint !== bundle.operatorKey.fingerprintSha256
    || !equal(bundle.operatorKey, externalPins.operatorKey)) {
    push(errors, "APPROVAL_OPERATOR_PIN_MISMATCH", "$.finalDesignApproval",
      "approval operator identity, role, key and fingerprint must equal bundle and external pin");
  }
  const pinNames = [
    "operatorKey", "recoveryRootKey", "orchestratorKey", "validatorControllerKey",
    "recoveryApp", "recoveryWriteAheadGateway", "providerRefVerifier",
    "egressEnforcementMonitor", "transparencyInstanceKey", "witnessKeys",
  ];
  for (const name of pinNames) {
    if (!equal(bundle[name], externalPins[name])) {
      push(errors, "EXTERNAL_PIN_MISMATCH", `$.${name}`, "bundle and external pin differ");
    }
  }
  const controlKeys = [bundle.operatorKey, bundle.recoveryRootKey,
    bundle.orchestratorKey, bundle.validatorControllerKey, bundle.recoveryApp,
    bundle.recoveryWriteAheadGateway, bundle.providerRefVerifier,
    bundle.egressEnforcementMonitor, bundle.transparencyInstanceKey,
    ...bundle.witnessKeys];
  controlKeys.forEach((key, index) => assertPinnedPublicKey(key, errors, `$.controlKeys[${index}]`));
  for (const field of ["keyRef", "publicKeyBase64url", "fingerprintSha256"]) {
    if (new Set(controlKeys.map((key) => key[field])).size !== controlKeys.length) {
      push(errors, "KEY_SEPARATION", `$.${field}`, "control keys and fingerprints must be pairwise distinct");
    }
  }
  try {
    assertBase64urlBytes(finalApproval.nonce, 32, "finalApproval.nonce");
    assertBase64urlBytes(finalApproval.signature, 64, "finalApproval.signature");
    assertBase64urlBytes(bundle.nonce, 32, "bundle.nonce");
    assertBase64urlBytes(bundle.operatorSignature, 64, "bundle.operatorSignature");
    assertBase64urlBytes(bundle.recoveryRootSignature, 64, "bundle.recoveryRootSignature");
  } catch (error) { push(errors, "BASE64URL_CANONICALITY", "$", error.message); }

  const eventIndexById = new Map(events.map((event, index) => [event.id, index]));
  const rootsById = new Map();
  for (const [index, key] of trustRoots.keys.entries()) {
    assertPinnedPublicKey({ ...key, keyRef: key.id }, errors, `$.trustRoots.keys[${index}]`);
    if (rootsById.has(key.id) || !eventIndexById.has(key.introducedByEventRef)) {
      push(errors, "TRUST_ROOT_INTRODUCTION", `$.trustRoots.keys[${index}]`, "key ID must be unique and introduced by an existing event");
    }
    rootsById.set(key.id, key);
  }
  const revocationIds = new Set();
  for (const [index, revocation] of trustRoots.revocations.entries()) {
    const key = rootsById.get(revocation.keyRef);
    if (!key || revocationIds.has(revocation.id) || !eventIndexById.has(revocation.revokedByEventRef)
      || revocation.supersededByKeyRef === revocation.keyRef
      || (revocation.supersededByKeyRef !== null && !rootsById.has(revocation.supersededByKeyRef))
      || Date.parse(revocation.revokedAt) < Date.parse(key.validFrom)) {
      push(errors, "TRUST_ROOT_REVOCATION", `$.trustRoots.revocations[${index}]`, "revocation edge is invalid");
    }
    revocationIds.add(revocation.id);
  }
  const gateway = bundle.recoveryWriteAheadGateway;
  const verifier = bundle.providerRefVerifier;
  const monitor = bundle.egressEnforcementMonitor;
  if (!gateway.providerInstallationIdentitySha256 || !gateway.providerCredentialIdentitySha256 ||
      gateway.providerInstallationIdentitySha256 !== verifier.providerInstallationIdentitySha256 ||
      gateway.providerInstallationIdentitySha256 !== bundle.recoveryApp.providerInstallationIdentitySha256 ||
      verifier.providerCredentialIdentitySha256 !== null ||
      monitor.providerInstallationIdentitySha256 !== null || monitor.providerCredentialIdentitySha256 !== null) {
    push(errors, "SERVICE_SEPARATION", "$.recoveryWriteAheadGateway", "provider identities violate closed separation");
  }
  const serviceIdentities = [gateway, verifier, monitor, bundle.recoveryApp]
    .map((value) => value.serviceIdentity ?? value.appIdentity);
  if (new Set(serviceIdentities).size !== serviceIdentities.length) {
    push(errors, "SERVICE_SEPARATION", "$", "service identities must be pairwise distinct");
  }
  const failureDomains = [gateway.failureDomain, verifier.failureDomain,
    monitor.failureDomain, ...bundle.witnessKeys.map((witness) => witness.failureDomain)];
  if (new Set(failureDomains).size !== failureDomains.length) {
    push(errors, "FAILURE_DOMAIN_SEPARATION", "$", "Gateway, Verifier, Monitor and Witness failure domains must be pairwise distinct");
  }
  const witnesses = bundle.witnessKeys;
  const sortedWitnesses = [...witnesses].sort((a, b) => compareUtf16(a.witnessId, b.witnessId));
  if (!equal(witnesses, sortedWitnesses)) push(errors, "WITNESS_ORDER", "$.witnessKeys", "witnesses are not sorted");
  for (const field of ["witnessId", "keyRef", "operatorIdentity", "failureDomain", "fingerprintSha256"]) {
    if (new Set(witnesses.map((value) => value[field])).size !== witnesses.length) {
      push(errors, "WITNESS_SEPARATION", `$.witnessKeys.${field}`, "witness values must be pairwise distinct");
    }
  }
  const nonces = [finalApproval.nonce, bundle.nonce, ...attestations.map((item) => item.artifact.nonce)];
  if (new Set(nonces).size !== nonces.length) push(errors, "NONCE_REUSE", "$", "nonce reused");

  verifyDetached({
    artifact: finalApproval,
    publicKeyBase64url: externalPins.operatorKey.publicKeyBase64url,
    payload: omit(finalApproval, ["signature"]), verifySignature, errors,
    path: "$.finalDesignApproval.signature",
  });
  const bundleCore = omit(bundle, ["operatorSignature", "recoveryRootSignature"]);
  verifyDetached({ artifact: { signature: bundle.operatorSignature },
    publicKeyBase64url: externalPins.operatorKey.publicKeyBase64url,
    payload: bundleCore, verifySignature, errors, path: "$.operatorSignature" });
  verifyDetached({ artifact: { signature: bundle.recoveryRootSignature },
    publicKeyBase64url: externalPins.recoveryRootKey.publicKeyBase64url,
    payload: bundleCore, verifySignature, errors, path: "$.recoveryRootSignature" });

  let previousEventHash = null;
  const activeKeyRefs = new Set();
  const purposeRole = new Map([
    ["approver", "ROLE-OPERATOR"], ["incoming-operator", "ROLE-OPERATOR"],
    ["recovery-root", "ROLE-RECOVERY-ROOT"],
    ["custodian-a", "ROLE-RECOVERY-CUSTODIAN-A"],
    ["custodian-b", "ROLE-RECOVERY-CUSTODIAN-B"],
    ["incoming-custodian-a", "ROLE-RECOVERY-CUSTODIAN-A"],
    ["incoming-custodian-b", "ROLE-RECOVERY-CUSTODIAN-B"],
  ]);
  const incomingPurposes = new Set([
    "incoming-operator", "incoming-custodian-a", "incoming-custodian-b",
  ]);
  for (const [index, event] of events.entries()) {
    const recordPrestate = ledgerReplay.recordPrestateByEventId[event.id];
    const recordPoststate = ledgerReplay.recordPoststateByEventId[event.id];
    if (!recordPrestate || !recordPoststate) {
      push(errors, "ROLE_KEY_REPLAY_STATE", `$.events[${index}]`, "branded record pre/poststate is required for every Event");
      continue;
    }
    if (event.previousEventHash !== previousEventHash) {
      push(errors, "EVENT_CHAIN", `$.events[${index}].previousEventHash`, "event predecessor must bind the prior fully attested event");
    }
    const computed = sha256Hex(canonicalBytes(omit(event, ["eventHash"])));
    if (event.eventHash !== computed) push(errors, "EVENT_HASH", `$.events[${index}].eventHash`, "event hash must include finalized attestations");
    const delta = [
      ...trustRoots.keys.filter((key) => key.introducedByEventRef === event.id),
      ...trustRoots.revocations.filter((revocation) => revocation.revokedByEventRef === event.id),
    ].sort((left, right) => Buffer.compare(canonicalBytes(left), canonicalBytes(right)));
    if (event.trustRootDeltaSha256 !== sha256Hex(canonicalBytes(delta))) {
      push(errors, "TRUST_ROOT_DELTA", `$.events[${index}].trustRootDeltaSha256`, "trust-root additions/revocations do not match event delta");
    }
    for (const attestation of event.authorizationAttestations) {
      const genesisPinnedException = event.id === "EVT-000001"
        && [externalPins.operatorKey.keyRef, externalPins.recoveryRootKey.keyRef].includes(attestation.keyRef)
        && ["actor", "recovery-root"].includes(attestation.attestationPurpose);
      const key = rootsById.get(attestation.keyRef);
      const incomingPossession = incomingPurposes.has(attestation.attestationPurpose);
      const initialRootAcceptance = event.recordRef === "ROLE-RECOVERY-ROOT"
        && event.fromStatus === null && event.toStatus === "assigned"
        && attestation.attestationPurpose === "recovery-root";
      const expectedRole = purposeRole.get(attestation.attestationPurpose);
      const resultRole = expectedRole ? recordPoststate[expectedRole] : null;
      if (incomingPossession) {
        const introducedNow = delta.some((item) => "validFrom" in item && item.id === attestation.keyRef);
        if (!introducedNow || !key || !resultRole || resultRole.status !== "assigned"
          || resultRole.assigneeRef !== attestation.signerIdentity
          || !resultRole.attestationKeyRefs.includes(attestation.keyRef)
          || key.roleRef !== resultRole.id || key.assigneeRef !== resultRole.assigneeRef) {
          push(errors, "INCOMING_KEY_POSSESSION", `$.events[${index}].authorizationAttestations`,
            "incoming signature must prove the same-event candidate key and resulting assigned ROLE only");
        }
      } else if (initialRootAcceptance) {
        const pinned = externalPins.recoveryRootKey;
        if (!activeKeyRefs.has(attestation.keyRef) || !key || !resultRole
          || resultRole.status !== "assigned"
          || resultRole.assigneeRef !== attestation.signerIdentity
          || !resultRole.attestationKeyRefs.includes(attestation.keyRef)
          || key.id !== pinned.keyRef || key.publicKeyBase64url !== pinned.publicKeyBase64url
          || key.fingerprintSha256 !== pinned.fingerprintSha256
          || key.roleRef !== resultRole.id || key.assigneeRef !== resultRole.assigneeRef) {
          push(errors, "INITIAL_RECOVERY_ROOT_ACCEPTANCE", `$.events[${index}].authorizationAttestations`,
            "initial Recovery-Root acceptance must use the earlier external pin and resulting ROLE binding");
        }
      } else if (!activeKeyRefs.has(attestation.keyRef) && !genesisPinnedException) {
        push(errors, "ATTESTATION_KEY_PRESTATE", `$.events[${index}].authorizationAttestations`,
          "every authorizing key must be active before the event; same-event and future keys cannot authorize themselves");
      }
      if (!genesisPinnedException && !incomingPossession && !initialRootAcceptance) {
        const role = recordPrestate[attestation.signerRole];
        if (!role || !role.id?.startsWith("ROLE-") || role.status !== "assigned"
          || role.assigneeRef !== attestation.signerIdentity
          || !role.attestationKeyRefs.includes(attestation.keyRef)
          || !key || key.roleRef !== role.id || key.assigneeRef !== role.assigneeRef) {
          push(errors, "ROLE_ATTESTATION_KEY_PRESTATE", `$.events[${index}].authorizationAttestations`,
            "actor key must be active, listed by the assigned replay-prestate ROLE, and bound to its role and assignee");
        }
      }
    }
    for (const revocation of delta.filter((item) => "revokedAt" in item)) {
      if (!activeKeyRefs.has(revocation.keyRef)) {
        push(errors, "TRUST_ROOT_REVOCATION_PRESTATE", `$.events[${index}]`, "only a key active before this event can be revoked");
      }
      const authorized = event.authorizationAttestations.some((attestation) =>
        attestation.keyRef === revocation.keyRef || attestation.attestationPurpose === "recovery-root");
      if (!authorized) push(errors, "TRUST_ROOT_REVOCATION_AUTHORITY", `$.events[${index}]`, "revocation requires old-key or closed recovery authorization");
    }
    for (const key of delta.filter((item) => "validFrom" in item)) activeKeyRefs.add(key.id);
    for (const revocation of delta.filter((item) => "revokedAt" in item)) activeKeyRefs.delete(revocation.keyRef);
    for (const field of ["publicKeyBase64url", "fingerprintSha256"]) {
      const activeMaterial = new Map();
      for (const keyRef of activeKeyRefs) {
        const key = rootsById.get(keyRef);
        const prior = activeMaterial.get(key[field]);
        if (prior && (prior.roleRef !== key.roleRef || prior.assigneeRef !== key.assigneeRef)) {
          push(errors, "ACTIVE_KEY_MATERIAL_SEPARATION", `$.events[${index}].${field}`,
            "simultaneously active key material/fingerprint cannot cross role or assignee boundaries");
        } else if (!prior) {
          activeMaterial.set(key[field], key);
        }
      }
    }
    for (const role of Object.values(recordPoststate).filter((record) => record?.id?.startsWith("ROLE-") && record.status === "assigned")) {
      if (!Array.isArray(role.attestationKeyRefs) || role.attestationKeyRefs.length === 0) {
        push(errors, "ROLE_ACTIVE_KEY_BINDING", `$.events[${index}].${role.id}`, "assigned ROLE needs at least one active attestation key");
        continue;
      }
      for (const keyRef of role.attestationKeyRefs) {
        const key = rootsById.get(keyRef);
        if (!activeKeyRefs.has(keyRef) || !key || key.roleRef !== role.id || key.assigneeRef !== role.assigneeRef) {
          push(errors, "ROLE_ACTIVE_KEY_BINDING", `$.events[${index}].${role.id}.attestationKeyRefs`,
            "each ROLE key must be active at this replay position and bound to the exact role/assignee");
        }
      }
    }
    previousEventHash = computed;
  }
  for (const [index, item] of attestations.entries()) {
    const artifact = item.artifact;
    const event = events.find((candidate) => candidate.id === item.eventId);
    const expected = `docs/governance/attestations/${item.eventId}--${artifact.attestationPurpose}--${artifact.keyRef}.json`;
    if (!event || !canonicalArtifactPath(repositoryRoot, item.path, expected)
      || !equal(artifact, item.eventAttestation)
      || !Buffer.from(item.fileBytes).equals(canonicalBytes(artifact))) {
      push(errors, "ATTESTATION_DUPLICATE", `$.attestations[${index}]`, "canonical path/file/object duplicate differs");
      continue;
    }
    const key = rootsById.get(artifact.keyRef);
    const envelope = { schemaVersion: "aurelia-governance-v1",
      repositoryId: "redshift-three67/aurelia", method: artifact.method,
      attestationPurpose: artifact.attestationPurpose, keyRef: artifact.keyRef,
      signerIdentity: artifact.signerIdentity, signerRole: artifact.signerRole,
      signedAt: artifact.signedAt,
      eventAuthorizationPayloadSha256: event.eventAuthorizationPayloadSha256,
      nonce: artifact.nonce };
    const revoked = trustRoots.revocations.some((revocation) =>
      revocation.keyRef === artifact.keyRef
      && eventIndexById.get(revocation.revokedByEventRef) < eventIndexById.get(event.id));
    const genesisPinnedException = event.id === "EVT-000001"
      && [externalPins.operatorKey.keyRef, externalPins.recoveryRootKey.keyRef].includes(artifact.keyRef)
      && ["actor", "recovery-root"].includes(artifact.attestationPurpose);
    const incomingPossession = incomingPurposes.has(artifact.attestationPurpose);
    const initialRootAcceptance = event.recordRef === "ROLE-RECOVERY-ROOT"
      && event.fromStatus === null && event.toStatus === "assigned"
      && artifact.attestationPurpose === "recovery-root";
    const introductionIndex = eventIndexById.get(key?.introducedByEventRef);
    const currentEventIndex = eventIndexById.get(event.id);
    const keyPositionValid = incomingPossession
      ? introductionIndex === currentEventIndex
      : genesisPinnedException || introductionIndex < currentEventIndex;
    const expectedRole = purposeRole.get(artifact.attestationPurpose);
    const resultRole = expectedRole
      ? ledgerReplay.recordPoststateByEventId[event.id]?.[expectedRole] : null;
    const possessionBindingValid = !incomingPossession || (resultRole
      && resultRole.status === "assigned"
      && resultRole.assigneeRef === artifact.signerIdentity
      && resultRole.attestationKeyRefs.includes(artifact.keyRef)
      && key?.roleRef === resultRole.id && key?.assigneeRef === resultRole.assigneeRef);
    const initialRootBindingValid = !initialRootAcceptance || (resultRole
      && resultRole.status === "assigned"
      && resultRole.assigneeRef === artifact.signerIdentity
      && resultRole.attestationKeyRefs.includes(artifact.keyRef)
      && key?.id === externalPins.recoveryRootKey.keyRef
      && key?.publicKeyBase64url === externalPins.recoveryRootKey.publicKeyBase64url
      && key?.fingerprintSha256 === externalPins.recoveryRootKey.fingerprintSha256
      && key?.roleRef === resultRole.id && key?.assigneeRef === resultRole.assigneeRef);
    const signingSkewMs = Math.abs(Date.parse(artifact.signedAt) - Date.parse(event.occurredAt));
    const pinnedGenesisKey = artifact.attestationPurpose === "actor"
      ? externalPins.operatorKey : externalPins.recoveryRootKey;
    const genesisPinMatches = !genesisPinnedException || (key
      && key.id === pinnedGenesisKey.keyRef
      && key.roleRef === pinnedGenesisKey.roleRef
      && key.assigneeRef === pinnedGenesisKey.assigneeRef
      && key.publicKeyBase64url === pinnedGenesisKey.publicKeyBase64url
      && key.fingerprintSha256 === pinnedGenesisKey.fingerprintSha256);
    if (!key || !keyPositionValid || !possessionBindingValid || !initialRootBindingValid
      || !genesisPinMatches || key.roleRef !== artifact.signerRole
      || key.assigneeRef !== artifact.signerIdentity
      || Date.parse(artifact.signedAt) < Date.parse(key.validFrom)
      || (key.validUntil !== null && Date.parse(artifact.signedAt) > Date.parse(key.validUntil))
      || !Number.isFinite(signingSkewMs) || signingSkewMs > 300_000 || revoked) {
      push(errors, "ATTESTATION_KEY_STATE", `$.attestations[${index}]`, "signer key is not the immediately prior active trust root");
      continue;
    }
    if ((artifact.attestationPurpose === "actor"
      && (artifact.signerRole !== event.actorRole
        || artifact.signerIdentity !== event.actorAssigneeSnapshot))
      || (artifact.attestationPurpose !== "actor"
        && purposeRole.get(artifact.attestationPurpose) !== artifact.signerRole)) {
      push(errors, "ATTESTATION_PURPOSE_MATRIX", `$.attestations[${index}]`, "purpose, role and event actor matrix differ");
    }
    if (artifact.envelopeSha256 !== sha256Hex(canonicalBytes(envelope))) {
      push(errors, "ATTESTATION_ENVELOPE", `$.attestations[${index}].envelopeSha256`, "envelope fields are not byte-equal");
    }
    if (!event.authorizationAttestations.some((candidate) => equal(candidate, artifact))) {
      push(errors, "ATTESTATION_EVENT_MEMBERSHIP", `$.attestations[${index}]`, "detached artifact is absent from finalized event");
    }
    verifyDetached({ artifact, publicKeyBase64url: key.publicKeyBase64url,
      payload: envelope, verifySignature, errors, path: `$.attestations[${index}].signature` });
  }
  const detachedKeys = attestations.map((item) => `${item.eventId}\u0000${item.artifact.attestationPurpose}\u0000${item.artifact.keyRef}`);
  const embeddedKeys = events.flatMap((event) => event.authorizationAttestations.map((artifact) =>
    `${event.id}\u0000${artifact.attestationPurpose}\u0000${artifact.keyRef}`));
  if (new Set(detachedKeys).size !== detachedKeys.length
    || detachedKeys.slice().sort().join("\u0001") !== embeddedKeys.slice().sort().join("\u0001")) {
    push(errors, "ATTESTATION_BIJECTION", "$.attestations", "every embedded attestation needs exactly one detached canonical file and vice versa");
  }
  return { errors, authorityRequired: [...new Set([...authorityRequired,
    "production-authority-context"])].sort(),
    cryptographicValid: errors.length === 0, gateEffective: false };
}
```

- [ ] **Step 5: Add the production wrapper and enforce its import boundary**

```js
// bootstrap-validator.mjs
import { verifyEd25519 } from "./crypto.mjs";
import { validateCryptographicBootstrapCore } from "./bootstrap-validator-internal.mjs";

export function validateCryptographicBootstrap(args) {
  return validateCryptographicBootstrapCore(args, { verifySignature: verifyEd25519 });
}
```

This wrapper verifies real Ed25519 signatures but its `externalPins` are still
raw caller inputs. Therefore even a clean result is only
`cryptographicValid:true`, always `gateEffective:false`, and carries
`authorityRequired:["production-authority-context"]`. Plan 11 replays the same
raw artifacts while verifying the independently signed pin/inventory/time/
receipt context and is the only layer allowed to compose a gate-effective
aggregate result. No boolean or string hook upgrades this object.

Add a source test that scans all `scripts/**/*.mjs`: only
`bootstrap-validator.mjs` and `bootstrap-validator.test.mjs` may contain the
specifier `bootstrap-validator-internal.mjs`; `governance-contract.mjs` must
import only `bootstrap-validator.mjs`. Passing a `verifySignature` property in
production args must have no effect: a dummy artifact signature still fails.
The same source boundary permits the Plan-03 `readValidatedLedgerReplay`
capability reader only in `bootstrap-validator-internal.mjs` and its tests.
That reader exposes deep-frozen plain record prestates/poststates only for a
successful, module-branded full replay; a caller Map, copied object, partial
range, or boolean never reaches the key-state checks.

- [ ] **Step 6: Run and confirm GREEN**

Expected: semantic fixture passes with the injected verifier; every mutation
returns the named rule code. A test without injected verification and with
dummy signatures must fail cryptographically.

This plan always enforces `signedAt` within `occurredAt ±5 minutes` and the
immediately-prior Trust-Root state. Plan 06 owns the immutable
Acceptance-Receipt first-inclusion replay and enforces the additional
`acceptedAt -24h .. acceptedAt +5m` window. Plan 11 supplies the independently
trusted acceptance/time context for gate evaluation; historical replay uses
the stored receipt time and never current local time.

- [ ] **Step 7: Commit semantic bootstrap validation**

```powershell
git add scripts/governance/bootstrap-validator-internal.mjs scripts/governance/bootstrap-validator.mjs scripts/governance/bootstrap-validator.test.mjs scripts/fixtures/governance/bootstrap/semantic-valid.json
git commit -m "feat: validate G0 bootstrap chronology"
```

### Task 6: Integrate bootstrap preflight without fabricating authority

**Files:**

- Modify: `scripts/governance-contract.mjs`
- Modify: `scripts/governance-contract.test.mjs`

- [ ] **Step 1: Add a failing repository-preflight test**

Assert that the current pre-Genesis repository produces
`authorityRequired` entries for final approval, pre-ledger bundle, and external
pins, while reporting no claim that `GATE-G0` is green.
Add one registry-contract assertion that `validateSchema("trust-roots", value)`
loads the schema and `validateSchema("trust-roots.schema.json", value)` fails
as an invalid logical name; every Plan 05–08 caller uses suffixless names.

- [ ] **Step 2: Run and confirm RED**

Run `node --test scripts/governance-contract.test.mjs`.
Expected: FAIL because the CLI does not yet call the bootstrap validator.

- [ ] **Step 3: Wire the bootstrap validator after structural checks**

The CLI must merge `errors` into its fail-closed result, render
`AUTHORITY_REQUIRED: <artifact>` separately, and exit nonzero for both.
Working-tree preflight may use local UTC only for diagnostics and must print
`preflight-only`; it must never claim live external state.

- [ ] **Step 4: Run and confirm GREEN**

Expected: the focused integration assertion passes; the command itself exits
nonzero with three explicit authority boundaries because no live ceremony has
occurred.

- [ ] **Step 5: Run Plan 05 verification gates**

```powershell
node --test scripts/governance/rfc8785.test.mjs scripts/governance/crypto.test.mjs scripts/governance/bootstrap-validator.test.mjs scripts/governance-contract.test.mjs
npm run check:canon
npm run typecheck:governance
npm run typecheck
npm run lint
git diff --check
```

Expected: targeted tests, canon, typecheck, lint, and diff check pass. The live
governance CLI remains intentionally blocked only by named external authority.

- [ ] **Step 6: Commit the Plan 05 integration**

```powershell
git add scripts/governance-contract.mjs scripts/governance-contract.test.mjs
git commit -m "feat: integrate cryptographic bootstrap preflight"
```

## Plan 05 acceptance evidence

- RFC-8785 golden bytes and digest pass; order, number, and Unicode mutations fail.
- RFC-8032 published verification vector passes; one-bit signature mutation fails.
- All four schemas are closed at every object level.
- D and I are distinct ordered commits; no artifact can refer to future G.
- No production path accepts injected signature verification.
- Raw caller-supplied pins can establish cryptographic validity but never gate
  effectiveness; only Plan 11 closes `production-authority-context`.
- Missing external ceremony is reported as an authority stop, not synthesized.
- No private key, signature generated by the implementation, remote write, or Genesis file is created.
