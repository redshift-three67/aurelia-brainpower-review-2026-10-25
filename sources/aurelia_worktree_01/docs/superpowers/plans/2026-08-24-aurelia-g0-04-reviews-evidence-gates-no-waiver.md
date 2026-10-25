# AURELIA G0 Reviews, Evidence, Gates, and No-Waiver Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enforce closed REV/EVID/EXC/GATE contracts, independent review and finding resolution, two-stage evidence capture/verification, epoch-bound gate eligibility, and transitive no-waiver provenance for all nine initial gates.

**Architecture:** Schema rejects malformed states; pure semantic validators operate on the replay state produced by Plan 03. `reviews-evidence-gates.mjs` verifies role matrices, historical snapshots, baselines, lifecycles, findings, byte-identical evidence artifacts, and gate prerequisites. `exception-provenance.mjs` computes the least fixed point over the closed reference graph and makes provenance monotone. No validator writes records, changes status, or converts unknown external proof to green.

**Tech Stack:** Node.js 22 ESM, `node:test`, Draft 2020-12/Ajv, Git ancestry through `repository-view.mjs`, RFC-8785 helpers from Plan 02, deterministic UTC inputs.

---

## Scope and file map

- Modify `docs/governance/governance.schema.json`: complete `$defs.gate`, `review`, `finding`, `findingResolution`, `subjectActorSnapshot`, `evidence`, `exception`.
- Create `docs/governance/schemas/reasoning-approval.schema.json`, `input-manifest.schema.json`, and `subject-manifest.schema.json`: the three mandatory standalone Draft-2020-12 artifact contracts owned exclusively by Plan 04.
- Create `scripts/governance/evidence-artifact-schemas.mjs` and `.test.mjs`: single schema-builder/write owner for those three files; Plan-02 `schema-registry.mjs` remains the sole generic load/compile registry.
- Modify `scripts/governance/schema-registry.test.mjs`: prove all three canonical names resolve and compile through the stable registry API.
- Create `scripts/governance/reviews-evidence-gates.mjs` and `.test.mjs`.
- Create `scripts/governance/exception-provenance.mjs` and `.test.mjs`.
- Modify `scripts/governance/reference-graph.mjs`: export direct record-to-record edges used by provenance.
- Modify `scripts/governance-contract.mjs` and `.test.mjs`: compose semantic errors after schema/reference/replay checks.

The files remain absent from the real pre-Genesis register paths until Plan 12. All Plan-04 tests use temporary registers and explicit baseline, epoch, role, ancestry and module-branded test authority-context fixtures; no raw `now` can reach Gate evaluation. Do not create reviews, evidence, exceptions, gates, events, signatures, remote proof, UI changes, or server state.

### Task 1: Define closed GATE, EXC, Finding, and snapshot schemas

**Files:**

- Modify: `docs/governance/governance.schema.json`
- Modify: `scripts/governance/schema-validator.test.mjs`

- [ ] **Step 1: Write one valid object and mutation tests for each definition**

For each definition, mutate every required field, enum, nullable coupling, `uniqueItems`, timestamp/date/commit/hash format, ID family, and additional property. Use explicit full objects; do not test fragments detached from their containing register.

- [ ] **Step 2: Add the complete `finding` definition**

The closed object has exactly these required properties and rules:

```json
{
  "findingId": { "type": "string", "pattern": "^F-[A-Z0-9]+(?:-[A-Z0-9]+)*$" },
  "priority": { "enum": ["P0", "P1", "P2", "P3"] },
  "assertion": { "$ref": "#/$defs/nonEmptyString" },
  "evidencePath": { "$ref": "#/$defs/repositoryPath" },
  "lineStart": { "type": ["integer", "null"], "minimum": 1 },
  "lineEnd": { "type": ["integer", "null"], "minimum": 1 },
  "scenario": { "$ref": "#/$defs/nonEmptyString" },
  "invariantRefs": { "type": "array", "uniqueItems": true, "items": { "$ref": "#/$defs/nonEmptyString" } },
  "correction": { "$ref": "#/$defs/nonEmptyString" },
  "verificationTest": { "$ref": "#/$defs/nonEmptyString" },
  "confidence": { "enum": ["low", "medium", "high"] }
}
```

Require all eleven names, set `additionalProperties: false`, and add `allOf` rules so both line fields are null together or integers with `lineEnd >= lineStart` (the latter comparison is also enforced semantically because standard JSON Schema has no `$data` comparison).

- [ ] **Step 3: Add complete `findingResolution` and `subjectActorSnapshot` definitions**

`findingResolution` requires exactly `findingRef`, `disposition`, `resolution`, `resolutionEvidenceRefs`, `dismissedByRole`, `dismissedByAssigneeSnapshot`; ref pattern is `^REV-[A-Z0-9]+(?:-[A-Z0-9]+)*#F-[A-Z0-9]+(?:-[A-Z0-9]+)*$`; disposition is `resolved|dismissed`; evidence is unique/non-empty; both dismissal fields are null for resolved and non-empty for dismissed. `subjectActorSnapshot` requires exactly non-empty `subjectRef`, ROLE `roleRef`, non-empty `assigneeRef`, EVID `assignmentEvidenceRef`; close both objects.

- [ ] **Step 4: Add complete GATE and EXC definitions**

Build both with Plan-02 `common` and `successor`, `unevaluatedProperties: false`, and exact required lists:

```json-fragment
"gateRequired": ["id","title","status","ownerRole","sourceRefs","reviewOn","exceptionProvenanceRefs","supersedesRecordRef","supersededByRecordRef","entryCriteria","exitCriteria","requiredEvidenceRefs","noWaiver","verifierRoleRefs","approverRoleRefs","baselineCommit","reviewRefs","exceptionRefs","expiresOn"],
"exceptionRequired": ["id","title","status","ownerRole","sourceRefs","reviewOn","exceptionProvenanceRefs","supersedesRecordRef","supersededByRecordRef","scopeIds","justification","compensatingControlRefs","requestedByRole","approvedByRole","requestedAt","expiresAt","revokedAt","evidenceRefs","blockedGateRefs"]
```

GATE status is `red|amber|green|expired`; its three criteria/evidence arrays are non-empty, role arrays are non-empty/unique, commits are null or 40 lowercase hex, and `expiresOn` is a nullable date. `green` requires a non-null baseline, non-empty reviews, and no exceptions when `noWaiver` is true. A null expiry is valid; if a date is set, trusted time must show it is not expired. EXC status is `requested|approved|revoked|expired`; its three scope/control/gate arrays are non-empty/unique; requested has null approval/revocation; approved requires `ROLE-OPERATOR`, non-empty evidence, null revocation; revoked requires RFC3339 `revokedAt`.

- [ ] **Step 5: Run schema tests and commit the first schema slice**

```powershell
node --test scripts/governance/schema-validator.test.mjs
git add docs/governance/governance.schema.json scripts/governance/schema-validator.test.mjs
git commit -m "feat: define gate exception and finding schemas"
```

Expected: every valid fixture passes; every extra property and invalid state coupling fails.

### Task 2: Define closed REV and EVID schemas

**Files:** Same schema and test files.

- [ ] **Step 1: Add status-complete REV test vectors**

Create one fixture for `requested`, `changes-required`, `approved`, and `superseded`, then mutate every status-specific invariant from Design §12.4. Include human/internal-agent preflight coupling, snapshot lengths, empty subjects, expired date, supersession nullability, P0 finding, and duplicate Finding ID.

- [ ] **Step 2: Add the complete REV property contract**

Require every field listed here and no others:

```json
["id","title","status","ownerRole","sourceRefs","reviewOn","exceptionProvenanceRefs","reviewType","subjectIds","subjectPaths","scope","evidenceSubjectRefs","reviewerRole","independentFrom","reviewerAssigneeSnapshot","independentAssigneeSnapshots","subjectActorSnapshots","reviewerExecution","modelName","reasoningLevel","promptDigest","reasoningApprovalEvidenceRef","externalReviewEvidenceRefs","baselineCommit","createdEpoch","decisionEpoch","verdict","findings","evidenceRefs","approvedByRole","performedAt","approvedByAssigneeSnapshot","expiresOn","supersedesReviewRef","supersededByReviewRef","supersededFromStatus","findingResolutions"]
```

Use exact design enums, ID patterns, non-empty scope, full commit, positive `createdEpoch`, nullable positive `decisionEpoch`, unique arrays, `$defs.finding`, `$defs.findingResolution`, `$defs.subjectActorSnapshot`, and `additionalProperties: false`. Encode human fields all null; internal-agent model/reasoning/prompt/reasoning-evidence all non-null. Encode the four state payloads exactly; semantic checks handle ancestry, role snapshots, prior-state preservation and open findings.

- [ ] **Step 3: Add status-complete EVID test vectors**

Create exact `expected`, `captured`, `verified`, `invalidated`, and `superseded` fixtures. Mutate artifact/hash/time/baseline/capture-base/manifests/result/producer/verifier/review/state reason/epoch/supersession couplings and all specialized payload exclusivity cases.

- [ ] **Step 4: Add the complete EVID property contract**

Require exactly every field in Design §12.4, including the seven specialized objects. Use these base enums:

```json-fragment
"evidenceType": ["command-output","test-report","design-commit","review-report","approval-record","audit-artifact","qualification","reasoning-approval","collector-contract","network-enforcement-verification","egress-dispatcher-contract","validator-promotion-request","external-model-output","provider-due-diligence","sanitization-report"],
"status": ["expected","captured","verified","invalidated","superseded"]
```

Close the record. Require non-empty producer/scope/command/retention, at least one subject ID or path, unique derivation/digest/review arrays, full commit/hash patterns, positive epochs, and the exact status couplings from the design. For each specialized type, use `if evidenceType then` exactly its matching object non-null and the other six null; every ordinary type requires all seven null.

- [ ] **Step 5: Run and commit the second schema slice**

```powershell
node --test scripts/governance/schema-validator.test.mjs
git add docs/governance/governance.schema.json scripts/governance/schema-validator.test.mjs
git commit -m "feat: define review and evidence lifecycle schemas"
```

Expected: all lifecycle vectors pass and every direct `expected→verified` representation is impossible.

### Task 2A: Publish reasoning-approval and manifest artifact schemas

**Files:**

- Create: `scripts/governance/evidence-artifact-schemas.mjs`
- Create: `scripts/governance/evidence-artifact-schemas.test.mjs`
- Create: `scripts/governance/test-fixtures/evidence-artifacts.mjs`
- Create: `docs/governance/schemas/reasoning-approval.schema.json`
- Create: `docs/governance/schemas/input-manifest.schema.json`
- Create: `docs/governance/schemas/subject-manifest.schema.json`
- Modify: `scripts/governance/schema-registry.test.mjs`

Plan 04 is the sole writer/owner of these three schema files. Later plans may
only consume them through Plan-02's `validateSchema(name, value, { root })`;
they must not copy or redefine their field lists.

- [ ] **Step 1: Write failing builder, registry, and closed-object mutation tests**

Use complete valid fixtures for all three artifacts. For every schema delete
each required field and add an extra root property. For manifests also add an
extra nested property, duplicate each unique array, mix fields from two Subject
entry kinds, use an empty combined Subject set, use a glob/non-revision-fixed
input URI, mismatch the EVID ID/path convention, and break entry order. Schema
tests reject shape errors; semantic manifest tests in Task 5 reject coverage,
path convention, sorting, glob, Git-mode and provenance errors.

The registry regression is exact:

```js
const SHA = "a".repeat(64);
const COMMIT = "b".repeat(40);
const VALID_ARTIFACTS = Object.freeze({
  "reasoning-approval": Object.freeze({
    taskScope: "AURELIA-G0-GOVERNANCE-IMPLEMENTATION",
    modelName: "gpt-5.6-sol",
    previousReasoningLevel: "high",
    approvedReasoningLevel: "xhigh",
    approvedAt: "2026-08-24T10:00:00.000Z",
    expiresAt: "2026-08-24T12:00:00.000Z",
    operatorAttestationRef: "docs/governance/attestations/EVT-000100--approver--KEY-OPERATOR.json",
  }),
  "subject-manifest": Object.freeze({
    schemaVersion: "aurelia-governance-v1", manifestId: "MANIFEST-EVID-TEST-SUBJECT",
    evidenceRef: "EVID-TEST", baselineCommit: COMMIT,
    subjectIds: ["REQ-GOV-001"], subjectPaths: [],
    entries: [{ kind: "record", recordRef: "REQ-GOV-001",
      registerPath: "docs/governance/traceability-register.md", recordSha256: SHA }],
  }),
  "input-manifest": Object.freeze({
    schemaVersion: "aurelia-governance-v1", manifestId: "MANIFEST-EVID-TEST-INPUTS",
    evidenceRef: "EVID-TEST", subjectBaselineCommit: COMMIT,
    generatedAt: "2026-08-24T10:00:00.000Z",
    entries: [{ pathOrUri: "docs/governance/traceability-register.md",
      fileMode: "100644", sha256: SHA, dataClassification: "internal-control",
      derivationRefs: ["REQ-GOV-001"], exceptionProvenanceRefs: [] }],
  }),
});
for (const name of ["reasoning-approval", "input-manifest", "subject-manifest"]) {
  assert.equal(schemaPath(name), `docs/governance/schemas/${name}.schema.json`);
  assert.deepEqual(validateSchema(name, VALID_ARTIFACTS[name], { root: fixture.root }), []);
}
assert.equal(validateSchema("reasoning-approval", {
  ...VALID_ARTIFACTS["reasoning-approval"], injected: true,
}, { root: fixture.root })[0].rule, "SCHEMA-ADDITIONALPROPERTIES");
```

Create `scripts/governance/evidence-artifact-schemas.test.mjs` with this
complete mutation harness (import the `VALID_ARTIFACTS` fixture above from the
test fixture module rather than copying it):

```js
import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import { evidenceArtifactSchemas, writeEvidenceArtifactSchemas }
  from "./evidence-artifact-schemas.mjs";
import { validateSchema } from "./schema-registry.mjs";
import { VALID_ARTIFACTS } from "./test-fixtures/evidence-artifacts.mjs";

const clone = (value) => structuredClone(value);

function fixtureRoot(t) {
  const root = mkdtempSync(join(tmpdir(), "aurelia-artifact-schemas-"));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  writeEvidenceArtifactSchemas(root);
  return root;
}

function assertInvalid(root, name, value, pattern) {
  const diagnostics = validateSchema(name, value, { root });
  assert.ok(diagnostics.length > 0, `${name} mutation was accepted`);
  assert.match(diagnostics.map((item) => `${item.rule}:${item.message}`).join("\n"), pattern);
}

test("materialized artifact schemas equal their deterministic builders", (t) => {
  const root = fixtureRoot(t);
  for (const [name, schema] of Object.entries(evidenceArtifactSchemas)) {
    const bytes = readFileSync(join(root,
      `docs/governance/schemas/${name}.schema.json`), "utf8");
    assert.equal(bytes, `${JSON.stringify(schema, null, 2)}\n`);
    assert.deepEqual(validateSchema(name, VALID_ARTIFACTS[name], { root }), []);
  }
});

test("all artifact roots are required and closed", (t) => {
  const root = fixtureRoot(t);
  for (const [name, valid] of Object.entries(VALID_ARTIFACTS)) {
    for (const field of Object.keys(valid)) {
      const mutated = clone(valid);
      delete mutated[field];
      assertInvalid(root, name, mutated, /required/i);
    }
    assertInvalid(root, name, { ...clone(valid), injected: true },
      /additionalProperties/i);
  }
});

test("manifest nested objects, unions, and unique arrays are closed", (t) => {
  const root = fixtureRoot(t);
  for (const name of ["subject-manifest", "input-manifest"]) {
    const nestedExtra = clone(VALID_ARTIFACTS[name]);
    nestedExtra.entries[0].injected = true;
    assertInvalid(root, name, nestedExtra, /additionalProperties|oneOf/i);
    const duplicateEntry = clone(VALID_ARTIFACTS[name]);
    duplicateEntry.entries.push(clone(duplicateEntry.entries[0]));
    assertInvalid(root, name, duplicateEntry, /uniqueItems/i);
  }
  const mixedKind = clone(VALID_ARTIFACTS["subject-manifest"]);
  Object.assign(mixedKind.entries[0], { kind: "file", path: "README.md",
    fileMode: "100644", sha256: "a".repeat(64) });
  assertInvalid(root, "subject-manifest", mixedKind, /oneOf|additionalProperties/i);

  const duplicateSubject = clone(VALID_ARTIFACTS["subject-manifest"]);
  duplicateSubject.subjectIds.push(duplicateSubject.subjectIds[0]);
  assertInvalid(root, "subject-manifest", duplicateSubject, /uniqueItems/i);
  const duplicateDerivation = clone(VALID_ARTIFACTS["input-manifest"]);
  duplicateDerivation.entries[0].derivationRefs.push(
    duplicateDerivation.entries[0].derivationRefs[0]);
  assertInvalid(root, "input-manifest", duplicateDerivation, /uniqueItems/i);
  const duplicateProvenance = clone(VALID_ARTIFACTS["input-manifest"]);
  duplicateProvenance.entries[0].exceptionProvenanceRefs = ["EXC-TEST", "EXC-TEST"];
  assertInvalid(root, "input-manifest", duplicateProvenance, /uniqueItems/i);
});
```

Move `VALID_ARTIFACTS` into the created
`scripts/governance/test-fixtures/evidence-artifacts.mjs` file and list that
path in this task's **Files** section. Both tests import this single frozen
fixture; there is no second drifting schema example.

- [ ] **Step 2: Implement the complete deterministic schema builders**

Create `scripts/governance/evidence-artifact-schemas.mjs`:

```js
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";

const DRAFT = "https://json-schema.org/draft/2020-12/schema";
const ID_BASE = "https://aurelia.invalid/governance/schemas/";
const TEXT = Object.freeze({ type: "string", minLength: 1 });
const HEX64 = Object.freeze({ type: "string", pattern: "^[0-9a-f]{64}$" });
const FULL_COMMIT = Object.freeze({ type: "string", pattern: "^[0-9a-f]{40}$" });
const TIMESTAMP = Object.freeze({ type: "string", format: "date-time", pattern: "Z$" });
const EVID_ID = Object.freeze({ type: "string", pattern: "^EVID-[A-Z0-9]+(?:-[A-Z0-9]+)*$" });
const MODE = Object.freeze({ enum: ["100644", "100755"] });
const STRING_ARRAY = Object.freeze({ type: "array", uniqueItems: true, items: TEXT });
const GOVERNANCE_ID_ARRAY = Object.freeze({
  type: "array", uniqueItems: true,
  items: { type: "string", pattern: "^(?:REQ|CTRL|PROFILE|ROLE|COMP|RISK|DATA|FLOW|GATE|REV|EVID|EXC)-[A-Z0-9]+(?:-[A-Z0-9]+)*$" },
});

const closed = (properties, required = Object.keys(properties)) => Object.freeze({
  type: "object", additionalProperties: false, required, properties,
});
const root = (name, body) => Object.freeze({
  $schema: DRAFT, $id: `${ID_BASE}${name}.schema.json`, ...body,
});

export function reasoningApprovalSchema() {
  return root("reasoning-approval", closed({
    taskScope: TEXT,
    modelName: TEXT,
    previousReasoningLevel: { enum: ["medium", "high", "xhigh", "max", "ultra"] },
    approvedReasoningLevel: { enum: ["medium", "high", "xhigh", "max", "ultra"] },
    approvedAt: TIMESTAMP,
    expiresAt: TIMESTAMP,
    operatorAttestationRef: TEXT,
  }));
}

const fileEntry = closed({
  kind: { const: "file" }, path: TEXT, fileMode: MODE, sha256: HEX64,
});
const recordEntry = closed({
  kind: { const: "record" }, recordRef: TEXT, registerPath: TEXT,
  recordSha256: HEX64,
});
const productDecisionEntry = closed({
  kind: { const: "product-decision" }, productDecisionRef: TEXT,
  sourcePath: TEXT, exportName: TEXT, sourceBlobSha256: HEX64,
  derivedStatusSha256: HEX64,
});

export function subjectManifestSchema() {
  return root("subject-manifest", closed({
    schemaVersion: { const: "aurelia-governance-v1" },
    manifestId: TEXT,
    evidenceRef: EVID_ID,
    baselineCommit: FULL_COMMIT,
    subjectIds: STRING_ARRAY,
    subjectPaths: STRING_ARRAY,
    entries: { type: "array", minItems: 1, uniqueItems: true,
      items: { oneOf: [fileEntry, recordEntry, productDecisionEntry] } },
  }));
}

const inputEntry = closed({
  pathOrUri: TEXT,
  fileMode: { anyOf: [MODE, { type: "null" }] },
  sha256: HEX64,
  dataClassification: { enum: ["public", "synthetic", "sanitized-non-production", "internal-control", "art9", "secret"] },
  derivationRefs: GOVERNANCE_ID_ARRAY,
  exceptionProvenanceRefs: { type: "array", uniqueItems: true,
    items: { type: "string", pattern: "^EXC-[A-Z0-9]+(?:-[A-Z0-9]+)*$" } },
});

export function inputManifestSchema() {
  return root("input-manifest", closed({
    schemaVersion: { const: "aurelia-governance-v1" },
    manifestId: TEXT,
    evidenceRef: EVID_ID,
    subjectBaselineCommit: FULL_COMMIT,
    generatedAt: TIMESTAMP,
    entries: { type: "array", minItems: 1, uniqueItems: true, items: inputEntry },
  }));
}

export const evidenceArtifactSchemas = Object.freeze({
  "reasoning-approval": reasoningApprovalSchema(),
  "input-manifest": inputManifestSchema(),
  "subject-manifest": subjectManifestSchema(),
});

export function writeEvidenceArtifactSchemas(rootDirectory = process.cwd()) {
  for (const [name, schema] of Object.entries(evidenceArtifactSchemas)) {
    const path = resolve(rootDirectory, `docs/governance/schemas/${name}.schema.json`);
    mkdirSync(dirname(path), { recursive: true });
    writeFileSync(path, `${JSON.stringify(schema, null, 2)}\n`, { encoding: "utf8", flag: "w" });
  }
}
```

- [ ] **Step 3: Materialize, validate, and commit the three schemas**

```powershell
node --input-type=module -e "import('./scripts/governance/evidence-artifact-schemas.mjs').then(({writeEvidenceArtifactSchemas}) => writeEvidenceArtifactSchemas())"
node --test scripts/governance/evidence-artifact-schemas.test.mjs scripts/governance/schema-registry.test.mjs
git add docs/governance/schemas/reasoning-approval.schema.json docs/governance/schemas/input-manifest.schema.json docs/governance/schemas/subject-manifest.schema.json scripts/governance/evidence-artifact-schemas.mjs scripts/governance/evidence-artifact-schemas.test.mjs scripts/governance/test-fixtures/evidence-artifacts.mjs scripts/governance/schema-registry.test.mjs
git commit -m "feat: define evidence manifest artifact schemas"
```

Expected: generated files equal their in-memory builders, all three registry
names validate, every root/nested extra property fails, and no later plan owns
or rewrites these contracts.

### Task 3: Enforce the closed review matrix and historical separation

**Files:**

- Create: `scripts/governance/reviews-evidence-gates.mjs`
- Create: `scripts/governance/reviews-evidence-gates.test.mjs`

- [ ] **Step 1: Write the full review-type cross-product test**

For all nine types, test the exact reviewer role, operator approver, minimum `independentFrom`, symmetric ROLE separation, assigned/qualified roles, distinct reviewer/approver/independent/subject-actor assignees, and historical snapshot stability after role reassignment. Add the operator exception only for reviewer=approver, never subject author.

- [ ] **Step 2: Implement the complete matrix and snapshot verifier**

Create `scripts/governance/reviews-evidence-gates.mjs` beginning with:

```js
import { canonicalBytes } from "./rfc8785.mjs";

export const REVIEW_MATRIX = Object.freeze({
  spec: ["ROLE-SPEC-REVIEWER", ["ROLE-IMPLEMENTER", "ROLE-ORCHESTRATOR"]],
  "quality-security": ["ROLE-QUALITY-SECURITY-REVIEWER", ["ROLE-IMPLEMENTER", "ROLE-ORCHESTRATOR", "ROLE-SPEC-REVIEWER"]],
  final: ["ROLE-FINAL-REVIEWER", ["ROLE-IMPLEMENTER", "ROLE-ORCHESTRATOR", "ROLE-SPEC-REVIEWER", "ROLE-QUALITY-SECURITY-REVIEWER"]],
  operator: ["ROLE-OPERATOR", ["ROLE-IMPLEMENTER", "ROLE-ORCHESTRATOR"]],
  privacy: ["ROLE-PRIVACY-REVIEWER", ["ROLE-IMPLEMENTER", "ROLE-ORCHESTRATOR", "ROLE-LEGAL-REVIEWER"]],
  legal: ["ROLE-LEGAL-REVIEWER", ["ROLE-IMPLEMENTER", "ROLE-ORCHESTRATOR", "ROLE-PRIVACY-REVIEWER"]],
  pentest: ["ROLE-PENTESTER", ["ROLE-IMPLEMENTER", "ROLE-ORCHESTRATOR", "ROLE-QUALITY-SECURITY-REVIEWER"]],
  hardware: ["ROLE-HARDWARE-REVIEWER", ["ROLE-IMPLEMENTER", "ROLE-ORCHESTRATOR"]],
  "a11y-claims": ["ROLE-A11Y-CLAIMS-REVIEWER", ["ROLE-IMPLEMENTER", "ROLE-ORCHESTRATOR"]],
});

const cmp = (a, b) => a < b ? -1 : a > b ? 1 : 0;
const issue = (record, rule, message) => ({ file: "docs/governance/gate-register.md", record, rule, message });
function reviewDecisionEvent(review, lifecycleContext) {
  if (["requested", "superseded"].includes(review.status)) return null;
  return lifecycleContext.transitionFor(review.id, review.status);
}

function roleAtDecisionErrors(review, decisionEvent, roleId, expectedSnapshot,
  lifecycleContext, rulePrefix) {
  const errors = [];
  const role = lifecycleContext.roleBeforeEvent(decisionEvent.id, roleId);
  if (!role || role.status !== "assigned" || !role.assigneeRef) {
    return [issue(review.id, `${rulePrefix}-UNASSIGNED`, `${roleId} was not assigned immediately before ${decisionEvent.id}`)];
  }
  if (role.assigneeRef !== expectedSnapshot) {
    errors.push(issue(review.id, `${rulePrefix}-SNAPSHOT`, `${roleId} snapshot differs at ${decisionEvent.id}`));
  }
  if (role.qualificationRequirements.length > 0 && role.qualificationEvidenceRefs.length === 0) {
    errors.push(issue(review.id, `${rulePrefix}-QUALIFICATION-MISSING`, `${roleId} has requirements but no qualification EVID`));
  }
  for (const evidenceId of role.qualificationEvidenceRefs) {
    const evidence = lifecycleContext.recordBeforeEvent(decisionEvent.id, evidenceId);
    if (!evidence || evidence.status !== "verified" || evidence.evidenceType !== "qualification"
      || !evidence.subjectIds.includes(roleId)) {
      errors.push(issue(review.id, `${rulePrefix}-QUALIFICATION`, `${evidenceId} did not qualify ${roleId} before ${decisionEvent.id}`));
    }
  }
  return errors;
}

export function reviewSeparationErrors(review, { lifecycleContext }) {
  const errors = [];
  const [expectedReviewer, requiredIndependent] = REVIEW_MATRIX[review.reviewType] ?? [];
  if (!expectedReviewer || review.reviewerRole !== expectedReviewer) errors.push(issue(review.id, "REV-ROLE-MATRIX", "reviewer role does not match reviewType"));
  if (review.status === "approved" && review.approvedByRole !== "ROLE-OPERATOR") errors.push(issue(review.id, "REV-APPROVER-MATRIX", "approved review requires ROLE-OPERATOR"));
  for (const id of requiredIndependent ?? []) if (!review.independentFrom.includes(id)) errors.push(issue(review.id, "REV-INDEPENDENCE-MISSING", `missing ${id}`));
  if (["requested", "superseded"].includes(review.status)) return errors;
  const decisionEvent = reviewDecisionEvent(review, lifecycleContext);
  if (!decisionEvent) return [...errors, issue(review.id, "REV-DECISION-EVT",
    "decided review has no replayed lifecycle Event")];
  const reviewer = lifecycleContext.roleBeforeEvent(decisionEvent.id, review.reviewerRole);
  errors.push(...roleAtDecisionErrors(review, decisionEvent, review.reviewerRole,
    review.reviewerAssigneeSnapshot, lifecycleContext, "REV-REVIEWER"));
  if (review.status === "approved") {
    errors.push(...roleAtDecisionErrors(review, decisionEvent, "ROLE-OPERATOR",
      review.approvedByAssigneeSnapshot, lifecycleContext, "REV-APPROVER"));
  }
  const snapshots = [review.reviewerAssigneeSnapshot,
    ...review.independentAssigneeSnapshots,
    ...review.subjectActorSnapshots.map((x) => x.assigneeRef),
    ...(review.reviewType === "operator" ? [] : [review.approvedByAssigneeSnapshot]),
  ].filter(Boolean);
  if (new Set(snapshots).size !== snapshots.length) errors.push(issue(review.id, "REV-SNAPSHOT-COLLISION", "review identities are not independent"));
  if (review.independentFrom.length !== review.independentAssigneeSnapshots.length) errors.push(issue(review.id, "REV-SNAPSHOT-POSITION", "independent snapshots are not positional"));
  review.independentFrom.forEach((id, index) => {
    errors.push(...roleAtDecisionErrors(review, decisionEvent, id,
      review.independentAssigneeSnapshots[index], lifecycleContext, "REV-INDEPENDENT"));
    const independent = lifecycleContext.roleBeforeEvent(decisionEvent.id, id);
    const left = reviewer?.separationFromRoleRefs.includes(id) ?? false;
    const right = independent?.separationFromRoleRefs.includes(review.reviewerRole) ?? false;
    if (!left || !right) errors.push(issue(review.id, "REV-SEPARATION-SYMMETRY",
      `${review.reviewerRole} and ${id} require symmetric separation`));
  });
  if (review.reviewType === "operator" && review.subjectActorSnapshots.some((x) => x.assigneeRef === reviewer?.assigneeRef)) errors.push(issue(review.id, "REV-OPERATOR-SELF-REVIEW", "operator is a subject actor"));
  return errors;
}
```

`lifecycleContext` is produced by Plan 03 for the concrete adjacent commit.
`transitionFor(recordRef, toStatus)` returns the actual lifecycle EVT,
`roleBeforeEvent(eventId, roleId)` returns its immutable immediate role
pre-state, and `recordBeforeEvent(eventId, recordId)` resolves historical
qualification EVID from the same pre-state. Subject baseline and operator epoch
are not role-state locators: multiple reassignments may occur inside one epoch.
The aggregate calls this verifier only for a Review changed in the adjacent
commit. An unchanged historical Review is not re-resolved against current
roles; its original accepted step remains bound by the receipt/transparency
chain. Current-role qualification is separately evaluated when a Gate uses it.

- [ ] **Step 3: Add reasoning and subject-coverage validation**

Add the complete helpers below. `repositoryReader.pathExistsAtCommit` is the
non-writing fatal Git-object reader constructed from Plan 03; it returns false
for a missing object, symlink, submodule, malformed path or ambiguous/shallow
history and never falls back to the Working Tree.

```js
export function reviewExecutionErrors(review, lifecycleContext) {
  const errors = [];
  if (["requested", "superseded"].includes(review.status)) return errors;
  const modelFields = [review.modelName, review.reasoningLevel,
    review.promptDigest, review.reasoningApprovalEvidenceRef];
  if (review.reviewerExecution === "human") {
    if (modelFields.some((value) => value !== null)) errors.push(issue(review.id,
      "REV-HUMAN-PREFLIGHT", "human review must not claim model/reasoning fields"));
    return errors;
  }
  if (review.reviewerExecution !== "internal-agent" || modelFields.some((value) => value === null)) {
    return [issue(review.id, "REV-AGENT-PREFLIGHT", "internal-agent requires model, level, prompt digest and reasoning approval")];
  }
  const decisionEvent = reviewDecisionEvent(review, lifecycleContext);
  if (!decisionEvent) return [issue(review.id, "REV-DECISION-EVT",
    "agent review has no replayed lifecycle Event")];
  const approval = lifecycleContext.recordBeforeEvent(decisionEvent.id,
    review.reasoningApprovalEvidenceRef);
  if (!approval || approval.evidenceType !== "reasoning-approval"
    || !["captured", "verified"].includes(approval.status)
    || !review.evidenceRefs.includes(approval.id)) {
    return [issue(review.id, "REV-REASONING-EVIDENCE", "reasoning approval is absent or ineligible")];
  }
  const payload = approval.reasoningApproval;
  if (!payload || payload.taskScope !== review.scope || payload.modelName !== review.modelName
    || payload.approvedReasoningLevel !== review.reasoningLevel) {
    errors.push(issue(review.id, "REV-REASONING-BINDING", "reasoning approval scope/model/level differs"));
  }
  const approvedAt = Date.parse(payload?.approvedAt);
  const expiresAt = Date.parse(payload?.expiresAt);
  const performedAt = Date.parse(review.performedAt);
  const assignmentTimes = review.subjectActorSnapshots.map((snapshot) =>
    Date.parse(lifecycleContext.recordBeforeEvent(decisionEvent.id,
      snapshot.assignmentEvidenceRef)?.producedAt));
  if (![approvedAt, expiresAt, performedAt, ...assignmentTimes].every(Number.isFinite)
    || approvedAt >= Math.min(...assignmentTimes, performedAt)
    || performedAt >= expiresAt) {
    errors.push(issue(review.id, "REV-REASONING-TIME",
      "reasoning approval was not prior to assignment/review or had expired at performance"));
  }
  return errors;
}

export function reviewSubjectErrors(review, repositoryReader, lifecycleContext) {
  const errors = [];
  if (["requested", "superseded"].includes(review.status)) return errors;
  const decisionEvent = reviewDecisionEvent(review, lifecycleContext);
  if (!decisionEvent) return [issue(review.id, "REV-DECISION-EVT",
    "subject snapshots have no replayed lifecycle Event")];
  const expected = [...review.subjectIds,
    ...review.subjectPaths.map((path) => `path:${path}`)].sort(cmp);
  const actual = review.subjectActorSnapshots.map((item) => item.subjectRef).sort(cmp);
  if (new Set(actual).size !== actual.length
    || !canonicalBytes(actual).equals(canonicalBytes(expected))) {
    errors.push(issue(review.id, "REV-SUBJECT-SNAPSHOT-COVERAGE", "subjects require exactly one primary actor snapshot"));
  }
  for (const snapshot of review.subjectActorSnapshots) {
    const assignment = lifecycleContext.recordBeforeEvent(decisionEvent.id,
      snapshot.assignmentEvidenceRef);
    const assignmentBindsSubject = snapshot.subjectRef.startsWith("path:")
      ? assignment?.subjectPaths.includes(snapshot.subjectRef.slice(5))
      : assignment?.subjectIds.includes(snapshot.subjectRef);
    if (!assignment || !["captured", "verified"].includes(assignment.status)
      || !review.evidenceRefs.includes(snapshot.assignmentEvidenceRef)
      || !assignmentBindsSubject) {
      errors.push(issue(review.id, "REV-ASSIGNMENT-EVIDENCE",
        `assignment EVID does not bind ${snapshot.subjectRef}`));
    }
  }
  for (const path of review.subjectPaths) {
    if (!repositoryReader.pathExistsAtCommit(review.baselineCommit, path)) {
      errors.push(issue(review.id, "REV-SUBJECT-PATH", `${path} absent from review baseline`));
    }
  }
  for (const evidenceId of review.evidenceSubjectRefs) {
    if (!review.evidenceRefs.includes(evidenceId)) errors.push(issue(review.id,
      "REV-EVIDENCE-SUBSET", `${evidenceId} is not in evidenceRefs`));
  }
  return errors;
}
```

Tests reassign reviewer, approver and an independent role twice inside one
epoch between baseline and Decision-EVT; only the actual event-prestate passes.
Suspend a role while retaining its old `assigneeRef`, revoke its qualification
EVID, make separation one-sided, or alter the operator snapshot; each mutation
must fail with its exact `REV-*` rule.

- [ ] **Step 4: Run focused tests and commit**

```powershell
node --test --test-name-pattern="review|separation|snapshot" scripts/governance/reviews-evidence-gates.test.mjs
git add scripts/governance/reviews-evidence-gates.mjs scripts/governance/reviews-evidence-gates.test.mjs
git commit -m "feat: enforce independent governance reviews"
```

### Task 4: Enforce Findings, supersession, and resolution

**Files:** Modify the two Task-3 files.

- [ ] **Step 1: Write mutation tests for every finding rule**

Cover globally duplicate IDs, invalid line pair/order, changed old finding, self-resolution, unrelated review, broken supersede chain, subject/scope/type mismatch, non-descendant/equal baseline, duplicate resolution, resolved without captured evidence, dismissed without reviewer identity, P0/P1 dismissal without approved operator-attested successor, approved review with new P0–P2, and open ancestor P0–P2.

- [ ] **Step 2: Implement immutable finding indexing and chain traversal**

```js
export function indexFindings(reviews) {
  const index = new Map();
  const errors = [];
  for (const review of reviews) for (const finding of review.findings) {
    const ref = `${review.id}#${finding.findingId}`;
    if ([...index.values()].some((entry) => entry.finding.findingId === finding.findingId)) errors.push(issue(review.id, "REV-FINDING-DUPLICATE", `duplicate ${finding.findingId}`));
    else index.set(ref, { review, finding });
  }
  return { index, errors };
}

export function supersedeChain(review, reviewsById) {
  const chain = [];
  const seen = new Set([review.id]);
  let cursor = review;
  while (cursor.supersedesReviewRef) {
    if (seen.has(cursor.supersedesReviewRef)) throw new Error(`review supersession cycle at ${cursor.id}`);
    seen.add(cursor.supersedesReviewRef);
    cursor = reviewsById.get(cursor.supersedesReviewRef);
    if (!cursor) throw new Error(`missing superseded review from ${review.id}`);
    chain.push(cursor);
  }
  return chain;
}
```

- [ ] **Step 3: Implement `findingResolutionErrors`**

Add this complete implementation. It inspects only the concrete decision EVT
returned by Plan 03; Plan 05 subsequently authenticates every embedded
attestation and the aggregate cannot become gate-effective before that layer.

```js
export function findingResolutionErrors(review, reviewsById, records,
  repositoryReader, lifecycleContext) {
  const errors = [];
  const ancestors = supersedeChain(review, reviewsById);
  const ancestorByRef = new Map(ancestors.flatMap((ancestor) =>
    ancestor.findings.map((finding) => [`${ancestor.id}#${finding.findingId}`,
      { ancestor, finding }])));
  const allResolutions = [review, ...ancestors].flatMap((item) =>
    item.findingResolutions.map((resolution) => ({ review: item, resolution })));
  const resolutionCounts = new Map();
  for (const { resolution } of allResolutions) resolutionCounts.set(
    resolution.findingRef, (resolutionCounts.get(resolution.findingRef) ?? 0) + 1);
  for (const [ref, count] of resolutionCounts) if (count !== 1) errors.push(
    issue(review.id, "REV-RESOLUTION-DUPLICATE", `${ref} resolved ${count} times`));

  for (const resolution of review.findingResolutions) {
    const original = ancestorByRef.get(resolution.findingRef);
    if (!original || original.ancestor.id === review.id) {
      errors.push(issue(review.id, "REV-RESOLUTION-SUBJECT", `${resolution.findingRef} is not in the supersede chain`));
      continue;
    }
    if (review.reviewType !== original.ancestor.reviewType
      || review.scope !== original.ancestor.scope
      || !canonicalBytes(review.subjectIds).equals(canonicalBytes(original.ancestor.subjectIds))
      || !canonicalBytes(review.subjectPaths).equals(canonicalBytes(original.ancestor.subjectPaths))
      || review.baselineCommit === original.ancestor.baselineCommit
      || !repositoryReader.isAncestor(original.ancestor.baselineCommit, review.baselineCommit)) {
      errors.push(issue(review.id, "REV-RESOLUTION-CHAIN", "resolution review is not a strict matching successor"));
    }
    for (const evidenceId of resolution.resolutionEvidenceRefs) {
      const evidence = records.get(evidenceId)?.record;
      if (!evidence || !["captured", "verified"].includes(evidence.status)
        || evidence.scope !== review.scope || evidence.baselineCommit !== review.baselineCommit) {
        errors.push(issue(review.id, "REV-RESOLUTION-EVIDENCE", `${evidenceId} is not bound to the re-review`));
      }
    }
    if (resolution.disposition === "resolved"
      && (resolution.dismissedByRole !== null || resolution.dismissedByAssigneeSnapshot !== null)) {
      errors.push(issue(review.id, "REV-RESOLUTION-DISMISSAL-FIELDS", "resolved finding has dismissal identity"));
    }
    if (resolution.disposition === "dismissed") {
      if (resolution.dismissedByRole !== review.reviewerRole
        || resolution.dismissedByAssigneeSnapshot !== review.reviewerAssigneeSnapshot
        || original.ancestor.subjectActorSnapshots.some((item) =>
          item.assigneeRef === resolution.dismissedByAssigneeSnapshot)) {
        errors.push(issue(review.id, "REV-DISMISSAL-IDENTITY", "dismissal identity is not the independent successor reviewer"));
      }
      if (["P0", "P1"].includes(original.finding.priority)
        && (() => {
          const event = lifecycleContext.transitionFor(review.id, "approved");
          const operatorAttested = event?.authorizationAttestations.some((item) =>
            item.attestationPurpose === "approver" && item.signerRole === "ROLE-OPERATOR");
          return review.status !== "approved" || review.approvedByRole !== "ROLE-OPERATOR"
            || !operatorAttested;
        })()) {
        errors.push(issue(review.id, "REV-DISMISSAL-P0P1-AUTHORITY", "P0/P1 dismissal lacks approved operator-attested successor"));
      }
    }
  }

  if (review.status === "approved") {
    for (const finding of review.findings.filter((item) => item.priority !== "P3")) {
      errors.push(issue(review.id, "REV-APPROVED-NEW-FINDING", `${finding.findingId} is P0-P2`));
    }
    for (const [ref, entry] of ancestorByRef) if (entry.finding.priority !== "P3"
      && (resolutionCounts.get(ref) ?? 0) !== 1) errors.push(issue(review.id,
        "REV-OPEN-ANCESTOR-FINDING", `${ref} remains open`));
  }
  return errors;
}
```

- [ ] **Step 4: Run tests and commit**

```powershell
node --test --test-name-pattern="finding|resolution|supersed" scripts/governance/reviews-evidence-gates.test.mjs
git add scripts/governance/reviews-evidence-gates.mjs scripts/governance/reviews-evidence-gates.test.mjs
git commit -m "feat: preserve and resolve review findings"
```

### Task 5: Enforce the two-stage EVID lifecycle and baseline binding

**Files:** Modify Task-3 module/tests.

- [ ] **Step 1: Write lifecycle/epoch/manifest mutation tests**

Cover `expected→verified`, stale creation epoch, mismatched capture/decision epoch, producer/verifier collision, unassigned role, snapshot drift, unapproved/expired/wrong-scope review, missing subject/input manifest, wrong manifest hash/coverage/baseline, mutable captured scope/digest, wrong self-evidence rule, specialized payload mismatch, and invalidated/superseded history rewrite.

- [ ] **Step 2: Implement state and epoch validation**

```js
function evidenceRoleAtEventErrors(evidence, event, roleId, expectedSnapshot,
  lifecycleContext, rulePrefix) {
  if (!event) return [issue(evidence.id, `${rulePrefix}-EVT`,
    `missing lifecycle Event for ${roleId}`)];
  const role = lifecycleContext.roleBeforeEvent(event.id, roleId);
  const errors = [];
  if (!role || role.status !== "assigned" || !role.assigneeRef) {
    return [issue(evidence.id, `${rulePrefix}-UNASSIGNED`,
      `${roleId} was not assigned immediately before ${event.id}`)];
  }
  if (role.assigneeRef !== expectedSnapshot) errors.push(issue(evidence.id,
    `${rulePrefix}-SNAPSHOT`, `${roleId} snapshot differs at ${event.id}`));
  if (role.qualificationRequirements.length > 0
    && role.qualificationEvidenceRefs.length === 0) errors.push(issue(evidence.id,
      `${rulePrefix}-QUALIFICATION-MISSING`, `${roleId} has no qualification EVID`));
  for (const evidenceId of role.qualificationEvidenceRefs) {
    const qualification = lifecycleContext.recordBeforeEvent(event.id, evidenceId);
    if (!qualification || qualification.status !== "verified"
      || qualification.evidenceType !== "qualification"
      || !qualification.subjectIds.includes(roleId)) errors.push(issue(evidence.id,
        `${rulePrefix}-QUALIFICATION`, `${evidenceId} did not qualify ${roleId} at ${event.id}`));
  }
  return errors;
}

export function evidenceStateErrors(evidence, { lifecycleContext }) {
  const errors = [];
  const currentEvent = lifecycleContext.transitionFor(evidence.id, evidence.status);
  if (evidence.status === "expected") return errors;
  if (!currentEvent) return [issue(evidence.id, "EVID-DECISION-EVT",
    "non-expected EVID has no replayed lifecycle Event")];
  if (evidence.status === "captured") errors.push(...evidenceRoleAtEventErrors(
    evidence, currentEvent, evidence.producerRole,
    evidence.producerAssigneeSnapshot, lifecycleContext, "EVID-PRODUCER"));
  if (["captured", "verified", "invalidated"].includes(evidence.status) && evidence.captureEpoch !== evidence.createdEpoch) errors.push(issue(evidence.id, "EVID-CAPTURE-EPOCH", "capture epoch mismatch"));
  if (["verified", "invalidated"].includes(evidence.status) && evidence.decisionEpoch !== evidence.captureEpoch) errors.push(issue(evidence.id, "EVID-DECISION-EPOCH", "decision epoch mismatch"));
  if (evidence.status === "verified") {
    errors.push(...evidenceRoleAtEventErrors(evidence, currentEvent,
      evidence.verifiedByRole, evidence.verifiedByAssigneeSnapshot,
      lifecycleContext, "EVID-VERIFIER"));
    const verifier = lifecycleContext.roleBeforeEvent(currentEvent.id,
      evidence.verifiedByRole);
    if (verifier?.assigneeRef === evidence.producerAssigneeSnapshot) errors.push(issue(evidence.id, "EVID-SELF-VERIFICATION", "producer and verifier are identical"));
  }
  return errors;
}
```

An epoch rotation never makes the historical EVID record invalid. It only prevents current gate eligibility; capture/decision equality and qualification above are checked against immediate pre-state records of the concrete capture/decision EVTs. Add a regression where a role is reassigned twice inside the same epoch between subject baseline, capture and decision; only the assignee and verified qualification directly before each actual EVT match. Later suspension, qualification revocation or reassignment does not retroactively invalidate an already accepted historical EVID, but it prevents a current Gate from using that role.

- [ ] **Step 3: Implement manifest/review/supersession checks**

Extend the module imports exactly with:

```js
import { createHash } from "node:crypto";
import { parseUniqueJson } from "./raw-json.mjs";
import { validateSchema } from "./schema-registry.mjs";
```

Then add the complete orchestration below. `manifestReader` is
constructed by the CLI from the fatal Plan-03 repository view and the Plan-02
Product Decision Index. Its closed methods are:

```js
// root -> absolute repository root used only by schema-registry file loading
// readTargetBytes(path) -> Buffer|null; target commit/Working Tree only
// deriveSubjectEntries({ baselineCommit, subjectIds, subjectPaths }) -> sorted entries
// deriveInputEntries({ evidence, inputManifest }) -> complete sorted derivation inputs
// readEvidenceArtifactBytes({ artifactPathOrUri, captureBaseCommit })
//   -> frozen { source, bytes, immutableLocator, byteLength } | null
// assertExternalEvidenceInventoryBijection(consumedUris) -> diagnostic[]
```

`deriveSubjectEntries` recursively expands Git tree paths, rejects modes other
than 100644/100755, derives record hashes from baseline registers, and derives
Product-Decision entries from the baseline blob reader. `deriveInputEntries`
uses the immutable capture execution inventory, never the manifest itself as
the source of completeness. Neither method accepts a callback or current-tree
fallback in production.

For a repository `artifactPathOrUri`, `readEvidenceArtifactBytes` reads the
exact target Commit/Working-Tree blob through the fatal Plan-03 repository view
and rejects a symlink, submodule, directory, traversal, missing blob, or mode
other than `100644|100755`. For an external URI it performs no network call: the
CLI conditionally requires `--evidence-artifact-inventory <absolute-file>` and
loads a protected duplicate-key-free canonical JSON object with exactly
`schemaVersion/repositoryId/artifacts`. Each code-unit-sorted artifact entry has
exactly `artifactPathOrUri/contentFilePath/sha256/byteLength`; the content path
is absolute, outside the repository, non-symlink, and read-only for this run.
The reader rereads and hashes those bytes. The flag is absent iff the target
EVID set contains no external URI. Every inventory entry must be consumed by
exactly one non-`expected` EVID and every such external EVID must consume one
entry; missing, duplicate, extra, alias, redirect, mutable locator, or hash/
length drift is fatal. Repository paths and external URIs cannot alias.

Add this closed byte-binding layer before manifest/review decisions:

```js
const VERIFIED_EVIDENCE_ARTIFACT_SETS = new WeakMap();

export function verifyEvidenceArtifactSet(evidences, artifactReader) {
  const errors = [];
  const descriptors = [];
  const consumedExternalUris = [];
  for (const evidence of evidences) {
    if (evidence.status === "expected") continue;
    const loaded = artifactReader.readEvidenceArtifactBytes({
      artifactPathOrUri: evidence.artifactPathOrUri,
      captureBaseCommit: evidence.captureBaseCommit,
    });
    if (!loaded || !Buffer.isBuffer(loaded.bytes)) {
      errors.push(issue(evidence.id, "EVID-ARTIFACT-MISSING",
        `${evidence.artifactPathOrUri ?? "null"} is not immutable/readable`));
      continue;
    }
    const actualSha256 = sha256(loaded.bytes);
    if (actualSha256 !== evidence.sha256 || loaded.byteLength !== loaded.bytes.length) {
      errors.push(issue(evidence.id, "EVID-ARTIFACT-BYTE-HASH",
        "artifact bytes/length do not match captured EVID"));
      continue;
    }
    if (loaded.source === "external-inventory") consumedExternalUris.push(evidence.artifactPathOrUri);
    descriptors.push(Object.freeze({ schemaName: "evidence-artifact",
      artifactId: evidence.id, value: Object.freeze({
        schemaVersion: "aurelia-evidence-artifact-binding-v1",
        evidenceRef: evidence.id, artifactPathOrUri: evidence.artifactPathOrUri,
        sha256: actualSha256, byteLength: loaded.bytes.length,
        immutableLocator: loaded.immutableLocator,
      }) }));
  }
  errors.push(...artifactReader.assertExternalEvidenceInventoryBijection(
    Object.freeze([...consumedExternalUris].sort(cmp))));
  descriptors.sort((a, b) => cmp(a.artifactId, b.artifactId));
  const result = Object.freeze({ errors, cryptographicValid: errors.length === 0,
    gateEffective: false });
  if (errors.length === 0) VERIFIED_EVIDENCE_ARTIFACT_SETS.set(result,
    Object.freeze(descriptors));
  return result;
}

export function readVerifiedEvidenceArtifactDescriptors(result) {
  const descriptors = VERIFIED_EVIDENCE_ARTIFACT_SETS.get(result);
  if (!descriptors) throw new Error("unverified evidence artifact set");
  return descriptors;
}
```

Only `production-authority-context.mjs` and the Plan-04 contract test may import
`readVerifiedEvidenceArtifactDescriptors`; source allowlist tests enforce that
boundary. The production semantic composition runs
`verifyEvidenceArtifactSet` over every target EVID before any Review or Gate
check, carries the branded result in its module-private validated semantic
state, and requires the same brand for `captured`, `verified`, `invalidated`,
or `superseded` EVID. `evidenceReviewErrors` rejects a decision if the matching
descriptor is absent. `gateEligibilityErrors` rejects any required EVID unless
its exact artifact descriptor comes from that current branded set. Plan 11
reads only those branded descriptors and requires an exact one-to-one match in
the signed artifact inventory; an EVID record, raw inventory descriptor, or
claimed 64-hex digest alone can never satisfy the byte gate.

```js
const sha256 = (bytes) => createHash("sha256").update(bytes).digest("hex");
const hasGlob = (value) => /[*?\[\]{}]/.test(value);

export function manifestShapeErrors(evidence, subjectManifest, inputManifest) {
  const errors = [];
  const subjectPath = `docs/governance/manifests/${evidence.id}--subject.json`;
  const inputPath = `docs/governance/manifests/${evidence.id}--inputs.json`;
  if (evidence.subjectManifestPath !== subjectPath) errors.push(issue(evidence.id,
    "EVID-SUBJECT-MANIFEST-PATH", subjectPath));
  if (evidence.inputManifestPath !== inputPath) errors.push(issue(evidence.id,
    "EVID-INPUT-MANIFEST-PATH", inputPath));
  if (subjectManifest.evidenceRef !== evidence.id
    || inputManifest.evidenceRef !== evidence.id) errors.push(issue(evidence.id,
      "EVID-MANIFEST-REF", "manifest evidenceRef mismatch"));
  if (subjectManifest.manifestId !== `MANIFEST-${evidence.id}-SUBJECT`
    || inputManifest.manifestId !== `MANIFEST-${evidence.id}-INPUTS`) {
    errors.push(issue(evidence.id, "EVID-MANIFEST-ID",
      "manifestId does not follow the EVID naming contract"));
  }
  if (subjectManifest.baselineCommit !== evidence.baselineCommit
    || inputManifest.subjectBaselineCommit !== evidence.baselineCommit) {
    errors.push(issue(evidence.id, "EVID-MANIFEST-BASELINE",
      "manifest baseline mismatch"));
  }
  if (evidence.subjectIds.length + evidence.subjectPaths.length === 0) {
    errors.push(issue(evidence.id, "EVID-SUBJECT-EMPTY",
      "at least one subject is required"));
  }
  if (!canonicalBytes(subjectManifest.subjectIds).equals(canonicalBytes(evidence.subjectIds))
    || !canonicalBytes(subjectManifest.subjectPaths).equals(canonicalBytes(evidence.subjectPaths))) {
    errors.push(issue(evidence.id, "EVID-SUBJECT-COVERAGE",
      "manifest subjects differ from EVID"));
  }
  const subjectKeys = subjectManifest.entries.map((entry) => entry.kind === "file"
    ? `file\0${entry.path}` : entry.kind === "record"
      ? `record\0${entry.recordRef}`
      : `product-decision\0${entry.productDecisionRef}`);
  if (!canonicalBytes(subjectKeys).equals(canonicalBytes([...subjectKeys].sort(cmp)))) {
    errors.push(issue(evidence.id, "EVID-SUBJECT-ORDER",
      "subject entries are not code-unit sorted"));
  }
  const inputKeys = inputManifest.entries.map((entry) => entry.pathOrUri);
  if (inputKeys.some(hasGlob)
    || !canonicalBytes(inputKeys).equals(canonicalBytes([...inputKeys].sort(cmp)))) {
    errors.push(issue(evidence.id, "EVID-INPUT-ORDER",
      "input entries contain glob or are not code-unit sorted"));
  }
  if (new Set(inputKeys).size !== inputKeys.length) errors.push(issue(evidence.id,
    "EVID-INPUT-DUPLICATE", "duplicate input pathOrUri"));
  return errors;
}

const CAPTURE_FIELDS = Object.freeze([
  "artifactPathOrUri", "sha256", "producerAssigneeSnapshot", "producedAt",
  "baselineCommit", "captureBaseCommit", "subjectIds", "subjectPaths",
  "subjectManifestPath", "subjectManifestSha256", "scope", "command", "result",
  "derivationRefs", "inputManifestPath", "inputManifestSha256",
  "governanceChangeDigests", "reasoningApproval", "collectorContract",
  "networkEnforcementVerification", "egressDispatcherContract",
  "externalModelOutput", "providerDueDiligence", "sanitizationReport",
  "producerRole", "retentionRule", "createdEpoch", "captureEpoch",
]);

function loadManifest(evidence, kind, manifestReader) {
  const pathField = kind === "subject" ? "subjectManifestPath" : "inputManifestPath";
  const hashField = kind === "subject" ? "subjectManifestSha256" : "inputManifestSha256";
  const path = evidence[pathField];
  const bytes = path && manifestReader.readTargetBytes(path);
  if (!Buffer.isBuffer(bytes)) return { value: null, errors: [issue(evidence.id,
    `EVID-${kind.toUpperCase()}-MANIFEST-MISSING`, `${path ?? "null"} is absent`)] };
  let value;
  try { value = parseUniqueJson(bytes); }
  catch (error) { return { value: null, errors: [issue(evidence.id,
    `EVID-${kind.toUpperCase()}-MANIFEST-JSON`, error.message)] }; }
  const errors = validateSchema(`${kind}-manifest`, value,
    { root: manifestReader.root })
    .map((error) => issue(evidence.id, error.rule, `${path}: ${error.message}`));
  if (sha256(bytes) !== evidence[hashField]) errors.push(issue(evidence.id,
    `EVID-${kind.toUpperCase()}-MANIFEST-HASH`, `${path} byte hash mismatch`));
  return { value, errors };
}

export function evidenceManifestErrors(evidence, manifestReader,
  derivedProvenanceByRecord) {
  if (evidence.status === "expected") return [];
  const subject = loadManifest(evidence, "subject", manifestReader);
  const input = loadManifest(evidence, "input", manifestReader);
  const errors = [...subject.errors, ...input.errors];
  if (!subject.value || !input.value) return errors;
  errors.push(...manifestShapeErrors(evidence, subject.value, input.value));
  const expectedSubjects = manifestReader.deriveSubjectEntries({
    baselineCommit: evidence.baselineCommit,
    subjectIds: evidence.subjectIds,
    subjectPaths: evidence.subjectPaths,
  });
  if (!canonicalBytes(subject.value.entries).equals(canonicalBytes(expectedSubjects))) {
    errors.push(issue(evidence.id, "EVID-SUBJECT-MANIFEST-COVERAGE",
      "subject entries differ from independently derived baseline coverage"));
  }
  const expectedInputs = manifestReader.deriveInputEntries({ evidence,
    inputManifest: input.value });
  if (!canonicalBytes(input.value.entries).equals(canonicalBytes(expectedInputs))) {
    errors.push(issue(evidence.id, "EVID-INPUT-MANIFEST-COVERAGE",
      "input entries differ from immutable capture inventory"));
  }
  const taint = new Set();
  for (const entry of expectedInputs) for (const ref of entry.derivationRefs) {
    for (const exc of derivedProvenanceByRecord.get(ref) ?? []) taint.add(exc);
  }
  const expectedTaint = [...taint].sort(cmp);
  if (!canonicalBytes(evidence.exceptionProvenanceRefs).equals(canonicalBytes(expectedTaint))) {
    errors.push(issue(evidence.id, "EVID-INPUT-PROVENANCE",
      "EVID does not carry complete transitive input provenance"));
  }
  return errors;
}

export function evidenceReviewErrors(evidence, lifecycleContext,
  evidenceArtifactSet) {
  if (evidence.status !== "verified") return [];
  if (!VERIFIED_EVIDENCE_ARTIFACT_SETS.has(evidenceArtifactSet)
    || !VERIFIED_EVIDENCE_ARTIFACT_SETS.get(evidenceArtifactSet)
      .some((descriptor) => descriptor.artifactId === evidence.id)) {
    return [issue(evidence.id, "EVID-ARTIFACT-UNVERIFIED",
      "verified decision lacks the current byte-bound artifact descriptor")];
  }
  const errors = [];
  const decisionEvent = lifecycleContext.transitionFor(evidence.id, "verified");
  if (!decisionEvent || !Number.isFinite(Date.parse(decisionEvent.occurredAt))) {
    return [issue(evidence.id, "EVID-DECISION-EVT",
      "decision EVID has no replayed Event with trusted occurrence time")];
  }
  const decisionDate = decisionEvent.occurredAt.slice(0, 10);
  if (evidence.reviewRefs.length === 0) errors.push(issue(evidence.id,
    "EVID-REVIEW-MISSING", "decision state requires an approved review"));
  for (const id of evidence.reviewRefs) {
    const review = lifecycleContext.recordBeforeEvent(decisionEvent.id, id);
    if (!review || review.status !== "approved" || review.verdict !== "approved"
      || review.scope !== evidence.scope || review.baselineCommit !== evidence.baselineCommit
      || !review.evidenceSubjectRefs.includes(evidence.id)
      || !review.evidenceRefs.includes(evidence.id)
      || (review.expiresOn !== null && review.expiresOn < decisionDate)) {
      errors.push(issue(evidence.id, "EVID-REVIEW-INELIGIBLE", `${id} cannot decide ${evidence.id}`));
    }
  }
  return errors;
}

export function evidenceSupersessionErrors(evidence, priorEvidence, records,
  repositoryReader) {
  const errors = [];
  if (priorEvidence && ["captured", "verified", "invalidated", "superseded"].includes(priorEvidence.status)) {
    for (const field of CAPTURE_FIELDS) if (!canonicalBytes(evidence[field])
      .equals(canonicalBytes(priorEvidence[field]))) errors.push(issue(evidence.id,
        "EVID-CAPTURE-MUTATED", `${field} changed after capture`));
  }
  if (evidence.status !== "superseded") return errors;
  const successor = records.get(evidence.supersededByEvidenceRef)?.record;
  if (!successor || successor.supersedesEvidenceRef !== evidence.id
    || successor.id === evidence.id || successor.scope !== evidence.scope
    || !canonicalBytes(successor.subjectIds).equals(canonicalBytes(evidence.subjectIds))
    || !canonicalBytes(successor.subjectPaths).equals(canonicalBytes(evidence.subjectPaths))
    || !repositoryReader.isAncestor(evidence.baselineCommit, successor.baselineCommit)
    || evidence.baselineCommit === successor.baselineCommit) {
    errors.push(issue(evidence.id, "EVID-SUPERSESSION", "successor is absent, cyclic, mismatched, or not a strict baseline descendant"));
  }
  return errors;
}
```

Direct `expected→verified` remains rejected by Plan-03 transition policy.
Tests corrupt raw manifest bytes, add duplicate JSON keys, remove one recursive
file, replace a Product-Decision entry with a File entry, omit one immutable
capture input, remove historical EXC provenance, mutate each `CAPTURE_FIELDS`
member, and break each side of supersession. Additional mutations create a
captured EVID with a syntactically valid but false 64-hex digest, omit its
repository artifact, change one artifact byte after capture, change mode/path,
substitute an external inventory entry, add an orphan external descriptor,
alias one external URI to two EVIDs, forge the branded result, and remove a
required EVID descriptor before Review/Gate evaluation. Every case fails before
the EVID can be verified or a Gate can become eligible.

- [ ] **Step 4: Run tests and commit**

```powershell
node --test --test-name-pattern="EVID|evidence|manifest" scripts/governance/reviews-evidence-gates.test.mjs
git add scripts/governance/reviews-evidence-gates.mjs scripts/governance/reviews-evidence-gates.test.mjs
git commit -m "feat: bind captured and verified governance evidence"
```

### Task 6: Compute exception provenance to a least fixed point

**Files:**

- Create: `scripts/governance/exception-provenance.mjs`
- Create: `scripts/governance/exception-provenance.test.mjs`
- Modify: `scripts/governance/reference-graph.mjs`

- [ ] **Step 1: Write direct, two-level, three-level, cycle, revocation, and laundering tests**

For each of the nine no-waiver gates, test: direct EXC; helper CTRL with EXC; REQ→CTRL→EVID with EXC; cyclic records; revoked/expired EXC remains historical provenance; stored provenance removal; manual extra provenance; new EVID derived from tainted input; and atomic approval missing one dependent record.

- [ ] **Step 2: Export the exact direct edge extractor**

From `reference-graph.mjs` export `directGovernanceReferenceIds(record)`. It iterates only the closed reference fields from Design §12, includes `exceptionRefs`, excludes product IDs, paths, EVT IDs, inline Finding refs and assignment metadata that is not a governance record, returns a code-unit-sorted unique array, and never discovers refs by regexing arbitrary strings.

- [ ] **Step 3: Implement fixed-point derivation and stored-value comparison**

Create `scripts/governance/exception-provenance.mjs`:

```js
import { directGovernanceReferenceIds } from "./reference-graph.mjs";
import { canonicalBytes } from "./rfc8785.mjs";

export const INITIAL_NO_WAIVER_GATES = Object.freeze([
  "GATE-G0", "GATE-DATAFLOW", "GATE-PROFILE", "GATE-ART9", "GATE-MODULE",
  "GATE-CUDA", "GATE-HARDWARE", "GATE-PILOT", "GATE-24X7",
]);
const cmp = (a, b) => a < b ? -1 : a > b ? 1 : 0;
const issue = (record, rule, message) => ({ file: "docs/governance/gate-register.md", record, rule, message });

export function deriveExceptionProvenance(records, approvedExceptionHistory,
  priorDerivedHistory = new Map()) {
  const derived = new Map([...records.keys()].map((id) =>
    [id, new Set(priorDerivedHistory.get(id) ?? [])]));
  let changed = true;
  while (changed) {
    changed = false;
    for (const [id, entry] of records) {
      const target = derived.get(id);
      for (const ref of directGovernanceReferenceIds(entry.record)) {
        const referenced = records.get(ref);
        if (!referenced) continue;
        if (referenced.family === "EXC" && ref !== id && approvedExceptionHistory.has(ref) && !target.has(ref)) { target.add(ref); changed = true; }
        for (const exc of derived.get(ref) ?? []) if (!target.has(exc)) { target.add(exc); changed = true; }
      }
    }
  }
  return new Map([...derived].map(([id, set]) => [id, [...set].sort(cmp)]));
}

export function advanceExceptionProvenanceHistory(records,
  approvedExceptionHistory, priorDerivedHistory = new Map()) {
  return deriveExceptionProvenance(records, approvedExceptionHistory,
    priorDerivedHistory);
}

export function exceptionProvenanceErrors(records, expectedDerivedHistory) {
  const errors = [];
  for (const [id, entry] of records) {
    const stored = [...(entry.record.exceptionProvenanceRefs ?? [])].sort(cmp);
    const expected = expectedDerivedHistory.get(id) ?? [];
    if (!canonicalBytes(stored).equals(canonicalBytes(expected))) errors.push(issue(id, "EXC-PROVENANCE-MISMATCH", `stored ${stored.join(",")} expected ${expected.join(",")}`));
  }
  return errors;
}
```

`approvedExceptionHistory` is derived exclusively by replaying valid EXC
`requested→approved` events. `priorDerivedHistory` is likewise validator-owned:
the explicit base/head CLI starts with an empty Map at Genesis, advances it once
for every accepted First-Parent state, and carries the returned Map into the
next adjacent validation. Neither the current nor previous stored
`exceptionProvenanceRefs` ever seed either value. Revocation, expiry, amendment,
edge removal and supersession never remove an ID already in derived history.
The current fixed point begins with that history, so newly derived records also
inherit old taint through current typed edges.

Add this exact replay regression:

```js
const atTaintedEdge = advanceExceptionProvenanceHistory(recordsWithReqToApprovedExc,
  new Set(["EXC-001"]));
assert.deepEqual(atTaintedEdge.get("REQ-001"), ["EXC-001"]);
const afterEdgeRemoval = advanceExceptionProvenanceHistory(recordsWithoutThatEdge,
  new Set(["EXC-001"]), atTaintedEdge);
assert.deepEqual(afterEdgeRemoval.get("REQ-001"), ["EXC-001"]);
assert.deepEqual(exceptionProvenanceErrors(recordsWithoutThatEdge,
  afterEdgeRemoval), []);
const laundered = structuredClone(recordsWithoutThatEdge);
laundered.get("REQ-001").record.exceptionProvenanceRefs = [];
assert.equal(exceptionProvenanceErrors(laundered,
  afterEdgeRemoval)[0].rule, "EXC-PROVENANCE-MISMATCH");
```

- [ ] **Step 4: Implement transitive no-waiver traversal**

```js
export function noWaiverErrors(records, derivedHistory) {
  const errors = [];
  for (const gateId of INITIAL_NO_WAIVER_GATES) {
    const gate = records.get(gateId)?.record;
    if (!gate) { errors.push(issue(gateId, "GATE-NO-WAIVER-MISSING", "initial gate is missing")); continue; }
    if (gate.noWaiver !== true) errors.push(issue(gateId, "GATE-NO-WAIVER-FLAG", "initial gate must be noWaiver"));
    const seen = new Set();
    const queue = [gateId];
    while (queue.length) {
      const id = queue.shift();
      if (seen.has(id)) continue;
      seen.add(id);
      const provenance = derivedHistory.get(id) ?? [];
      if (provenance.length) errors.push(issue(gateId, "GATE-NO-WAIVER-PROVENANCE", `${id} carries ${provenance.join(",")}`));
      const entry = records.get(id);
      if (entry) queue.push(...directGovernanceReferenceIds(entry.record).filter((ref) => records.has(ref)).sort(cmp));
    }
  }
  return errors;
}
```

The per-range composition is deterministic and advances history only after all
schema/reference/ledger/provenance diagnostics for that adjacent commit are
empty:

```js
export function validateAndAdvanceProvenance({ records,
  approvedExceptionHistory, priorDerivedHistory }) {
  const nextDerivedHistory = advanceExceptionProvenanceHistory(records,
    approvedExceptionHistory, priorDerivedHistory);
  const errors = [
    ...exceptionProvenanceErrors(records, nextDerivedHistory),
    ...noWaiverErrors(records, nextDerivedHistory),
  ];
  return Object.freeze({ errors, nextDerivedHistory: errors.length === 0
    ? nextDerivedHistory : priorDerivedHistory });
}
```

- [ ] **Step 5: Run provenance tests and commit**

```powershell
node --test scripts/governance/exception-provenance.test.mjs
git add scripts/governance/exception-provenance.mjs scripts/governance/exception-provenance.test.mjs scripts/governance/reference-graph.mjs
git commit -m "feat: enforce transitive no-waiver provenance"
```

### Task 7: Derive gate eligibility without waivers or stale epochs

**Files:** Modify review/evidence/gate module and tests.

- [ ] **Step 1: Write one mutation per green prerequisite**

For each initial gate start from a valid green fixture and remove/expire/mismatch: baseline, required EVID, verified state, approved REV, reviewer/approver assignment/qualification/separation, finding resolution, current creation/capture/decision epoch, and gate authorization epoch. Pass only the branded Plan-11 `ProductionAuthorityContext` whose claims have `profile:"gate-evaluation"` and `gateEffective:true`. Mutate it to a plain object, serialized copy, raw pins, raw `now`, string hooks, `pre-genesis-ceremony` profile, or false gate-effective claim; every variant fails before Gate field evaluation. For `GATE-G0`, additionally require non-null `authority.operatorAcceptance`; mutate its Head, Tree, scope, final Gate-vector hash, current register Gate vector, full-artifact hash, or the signed `operator-acceptance` inventory-domain count/head independently and assert fail-closed. The same claim may be null for every non-G0/intermediate Gate. For `GATE-G0`, test the exact closed support policy: the two Design EVIDs plus Design Review use D/design scope; the three implementation/final EVIDs plus Spec/Quality/Final Reviews use I/implementation scope; Gate baseline is I; and D is a strict ancestor of I. Mutate every ID into the wrong D/I bucket, use a third older ancestor, swap either scope, set Gate baseline D, or make D unrelated/future; all fail. An unknown green Gate without a separately specified closed policy also fails. Add positive red/amber fixtures that remain valid without claiming eligibility.

- [ ] **Step 2: Implement gate eligibility as errors, never status mutation**

Import only `readProductionAuthorityContext` from
`./production-authority-context.mjs`; do not import a raw pin/time verifier or
the Plan-11 issuer into this module.

```js
import { readProductionAuthorityContext }
  from "./production-authority-context.mjs";

export const GATE_SUPPORT_POLICY = Object.freeze({
  "GATE-G0": Object.freeze({
    gateBaselineAnchor: "implementationCommit",
    evidence: Object.freeze({
      "EVID-G0-DESIGN-COMMIT": ["designCommit", "AURELIA-G0-GOVERNANCE-DESIGN"],
      "EVID-G0-FINAL-DESIGN-APPROVAL": ["designCommit", "AURELIA-G0-GOVERNANCE-DESIGN"],
      "EVID-G0-BASELINE-GATES": ["implementationCommit", "AURELIA-G0-GOVERNANCE-IMPLEMENTATION"],
      "EVID-G0-CONTRACT-TESTS": ["implementationCommit", "AURELIA-G0-GOVERNANCE-IMPLEMENTATION"],
      "EVID-G0-FINAL-GATES": ["implementationCommit", "AURELIA-G0-GOVERNANCE-IMPLEMENTATION"],
    }),
    reviews: Object.freeze({
      "REV-G0-DESIGN-APPROVAL": ["designCommit", "AURELIA-G0-GOVERNANCE-DESIGN"],
      "REV-G0-SPEC-REVIEW": ["implementationCommit", "AURELIA-G0-GOVERNANCE-IMPLEMENTATION"],
      "REV-G0-QUALITY-REVIEW": ["implementationCommit", "AURELIA-G0-GOVERNANCE-IMPLEMENTATION"],
      "REV-G0-FINAL-REVIEW": ["implementationCommit", "AURELIA-G0-GOVERNANCE-IMPLEMENTATION"],
    }),
  }),
});

export const FINAL_G0_GATE_VECTOR = Object.freeze({
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

function g0OperatorAcceptanceErrors(gate, records, authority) {
  if (gate.id !== "GATE-G0") return [];
  const acceptance = authority.operatorAcceptance;
  if (acceptance === null || typeof acceptance !== "object") {
    return [issue(gate.id, "GATE-G0-OPERATOR-ACCEPTANCE",
      "GATE-G0 requires the verified operator-acceptance claim")];
  }
  const currentVector = Object.freeze(Object.fromEntries(
    Object.keys(FINAL_G0_GATE_VECTOR).map((gateId) =>
      [gateId, records.get(gateId)?.record?.status ?? null]),
  ));
  if (!canonicalBytes(currentVector).equals(canonicalBytes(FINAL_G0_GATE_VECTOR))) {
    return [issue(gate.id, "GATE-G0-FINAL-VECTOR",
      "current Gate vector differs from the closed G0 final vector")];
  }
  const expectedVectorSha256 = sha256(canonicalBytes(FINAL_G0_GATE_VECTOR));
  const acceptanceDomain = authority.governanceDomainState?.domains
    ?.find((domain) => domain.domainId === "operator-acceptance");
  const exact = acceptance.headCommit === authority.headCommit
    && acceptance.headTreeOid === authority.headTreeOid
    && acceptance.scope === "AURELIA-G0-GOVERNANCE-ACCEPTANCE"
    && acceptance.finalGateVectorSha256 === expectedVectorSha256
    && /^[0-9a-f]{64}$/.test(authority.operatorAcceptanceSha256 ?? "")
    && acceptanceDomain?.artifactCount === 1
    && acceptanceDomain?.headSha256 === authority.operatorAcceptanceSha256;
  return exact ? [] : [issue(gate.id, "GATE-G0-OPERATOR-ACCEPTANCE-BINDING",
    "operator acceptance does not bind the authority Head/Tree/scope/final Gate vector")];
}

function exactPolicySetErrors(gate, actual, expectedObject, rule) {
  const expected = Object.keys(expectedObject).sort(cmp);
  const received = [...actual].sort(cmp);
  return canonicalBytes(received).equals(canonicalBytes(expected)) ? []
    : [issue(gate.id, rule, `expected ${expected.join(",")}; received ${received.join(",")}`)];
}

function gateSupportPrerequisiteErrors(gate, records, {
  currentEpoch, authorizationEpoch, derivedProvenance,
  isAncestor, baselineAnchors, now,
}) {
  const errors = [];
  if (!Number.isFinite(Date.parse(now))) return [issue(gate.id,
    "GATE-AUTHORITY-TIME", "authority context has no verified RFC3339 time")];
  const policy = GATE_SUPPORT_POLICY[gate.id];
  if (!policy) return [issue(gate.id, "GATE-SUPPORT-POLICY-UNKNOWN",
    "green Gate has no closed support policy")];
  if (!gate.baselineCommit) errors.push(issue(gate.id, "GATE-BASELINE", "green gate has no baseline"));
  const designCommit = baselineAnchors?.designCommit;
  const implementationCommit = baselineAnchors?.implementationCommit;
  if (!/^[0-9a-f]{40}$/.test(designCommit ?? "")
    || !/^[0-9a-f]{40}$/.test(implementationCommit ?? "")
    || designCommit === implementationCommit
    || !isAncestor(designCommit, implementationCommit)) {
    errors.push(issue(gate.id, "GATE-BASELINE-ANCHORS",
      "closed D/I anchors are absent or D is not a strict ancestor of I"));
  }
  if (gate.baselineCommit !== baselineAnchors?.[policy.gateBaselineAnchor]) {
    errors.push(issue(gate.id, "GATE-BASELINE-POLICY",
      `Gate baseline must equal ${policy.gateBaselineAnchor}`));
  }
  if (gate.expiresOn && gate.expiresOn < now.slice(0, 10)) errors.push(issue(gate.id, "GATE-EXPIRED", "green gate is expired"));
  if (authorizationEpoch !== currentEpoch) errors.push(issue(gate.id, "GATE-EPOCH", "gate authorization is stale"));
  if (gate.noWaiver && (derivedProvenance.get(gate.id) ?? []).length) errors.push(issue(gate.id, "GATE-NO-WAIVER", "gate carries exception provenance"));
  errors.push(...exactPolicySetErrors(gate, gate.requiredEvidenceRefs,
    policy.evidence, "GATE-EVIDENCE-SET"));
  for (const id of gate.requiredEvidenceRefs) {
    const evidence = records.get(id)?.record;
    const expected = policy.evidence[id];
    const expectedBaseline = expected && baselineAnchors?.[expected[0]];
    if (!evidence || !expected || evidence.status !== "verified"
      || evidence.baselineCommit !== expectedBaseline || evidence.scope !== expected[1]
      || evidence.decisionEpoch !== currentEpoch) errors.push(issue(gate.id,
        "GATE-EVIDENCE", `ineligible or policy-mismatched evidence ${id}`));
  }
  errors.push(...exactPolicySetErrors(gate, gate.reviewRefs,
    policy.reviews, "GATE-REVIEW-SET"));
  for (const id of gate.reviewRefs) {
    const review = records.get(id)?.record;
    const expected = policy.reviews[id];
    const expectedBaseline = expected && baselineAnchors?.[expected[0]];
    if (!review || !expected || review.status !== "approved"
      || review.verdict !== "approved" || review.baselineCommit !== expectedBaseline
      || review.scope !== expected[1] || review.decisionEpoch !== currentEpoch) {
      errors.push(issue(gate.id, "GATE-REVIEW",
        `ineligible or policy-mismatched review ${id}`));
    }
  }
  for (const roleId of [...gate.verifierRoleRefs, ...gate.approverRoleRefs]) {
    const assigned = records.get(roleId)?.record;
    if (!assigned || assigned.status !== "assigned" || !assigned.assigneeRef) errors.push(issue(gate.id, "GATE-ROLE", `unassigned role ${roleId}`));
    if (assigned?.qualificationRequirements.length
      && (assigned.qualificationEvidenceRefs.length === 0
        || !assigned.qualificationEvidenceRefs.every((id) => {
          const evidence = records.get(id)?.record;
          return evidence?.status === "verified"
            && evidence.evidenceType === "qualification"
            && evidence.subjectIds.includes(roleId);
        }))) errors.push(issue(gate.id, "GATE-QUALIFICATION",
          `unverified qualification ${roleId}`));
  }
  const gateRoles = [...new Set([...gate.verifierRoleRefs, ...gate.approverRoleRefs])];
  for (let left = 0; left < gateRoles.length; left += 1) for (let right = left + 1; right < gateRoles.length; right += 1) {
    const a = records.get(gateRoles[left])?.record;
    const b = records.get(gateRoles[right])?.record;
    const separated = a?.separationFromRoleRefs.includes(gateRoles[right]) || b?.separationFromRoleRefs.includes(gateRoles[left]);
    if (separated && a?.assigneeRef === b?.assigneeRef) errors.push(issue(gate.id, "GATE-ROLE-SEPARATION", `${gateRoles[left]} and ${gateRoles[right]} share an assignee`));
  }
  return errors;
}

export function gateEligibilityErrors(gate, records, {
  currentEpoch, authorizationEpoch, derivedProvenance,
  productionAuthorityContext, targetHeadCommit, targetHeadTreeOid,
  isAncestor, baselineAnchors, evidenceArtifactSet,
}) {
  if (gate.status !== "green") return [];
  const errors = [];
  const artifactDescriptors = VERIFIED_EVIDENCE_ARTIFACT_SETS.get(evidenceArtifactSet);
  if (!artifactDescriptors) return [issue(gate.id, "GATE-EVIDENCE-ARTIFACT-SET",
    "gate evaluation lacks a current verified evidence artifact set")];
  const boundEvidence = new Set(artifactDescriptors.map((item) => item.artifactId));
  for (const evidenceId of gate.requiredEvidenceRefs) if (!boundEvidence.has(evidenceId)) {
    errors.push(issue(gate.id, "GATE-EVIDENCE-ARTIFACT-BINDING",
      `${evidenceId} has no byte-bound artifact descriptor`));
  }
  let authority;
  try { authority = readProductionAuthorityContext(productionAuthorityContext); }
  catch (error) { return [issue(gate.id, "GATE-AUTHORITY-CONTEXT",
    `unverified production authority context: ${error.message}`)]; }
  if (authority.profile !== "gate-evaluation" || authority.gateEffective !== true) {
    return [issue(gate.id, "GATE-AUTHORITY-PROFILE",
      "gate evaluation requires a gate-effective gate-evaluation capability")];
  }
  if (authority.headCommit !== targetHeadCommit
    || authority.headTreeOid !== targetHeadTreeOid) {
    return [issue(gate.id, "GATE-AUTHORITY-TARGET",
      "production authority must bind the exact evaluated target Head and Tree")];
  }
  const now = authority.trustedTime?.now;
  errors.push(...gateSupportPrerequisiteErrors(gate, records, {
    currentEpoch, authorizationEpoch, derivedProvenance,
    isAncestor, baselineAnchors, now,
  }));
  errors.push(...g0OperatorAcceptanceErrors(gate, records, authority));
  return errors;
}
```

- [ ] **Step 2a: Add a permanently non-effective local G0 proposal path**

The complete code above owns the non-authority portion of
`gateEligibilityErrors` (closed policy sets, D/I baselines and scopes, expiry,
epoch, no-waiver, EVID/REV state, qualifications and separation) in the
module-private `gateSupportPrerequisiteErrors`. The production wrapper calls it
and then requires `g0OperatorAcceptanceErrors`; the proposal path calls the same
support helper but is not permitted to call `validateGateTransition`,
`g0OperatorAcceptanceErrors`, `verifyProductionAuthorityContext`, or any
WeakMap issuer.

Add this exact proposal API to the same module:

```js
const ALL_RED_G0_GATE_VECTOR = Object.freeze(Object.fromEntries(
  Object.keys(FINAL_G0_GATE_VECTOR).map((gateId) => [gateId, "red"]),
));

function gateVector(records) {
  return Object.freeze(Object.fromEntries(Object.keys(FINAL_G0_GATE_VECTOR)
    .map((gateId) => [gateId, records.get(gateId)?.record?.status ?? null])));
}

function soleG0RecordProjectionErrors(baseRecords, targetRecords) {
  const errors = [];
  const ids = [...new Set([...baseRecords.keys(), ...targetRecords.keys()])].sort(cmp);
  for (const id of ids) {
    if (id === "GATE-G0") continue;
    const before = baseRecords.get(id)?.record ?? null;
    const after = targetRecords.get(id)?.record ?? null;
    if (!canonicalBytes(before).equals(canonicalBytes(after))) {
      errors.push(issue("GATE-G0", "GATE-PROPOSAL-EXTRA-CHANGE",
        `proposal changes non-GATE-G0 record ${id}`));
    }
  }
  const before = baseRecords.get("GATE-G0")?.record;
  const after = targetRecords.get("GATE-G0")?.record;
  if (!before || !after || before.status !== "red" || after.status !== "green") {
    errors.push(issue("GATE-G0", "GATE-PROPOSAL-TRANSITION",
      "proposal must project exactly GATE-G0 red→green"));
  }
  return errors;
}

export function validateG0GateProposal({
  baseRecords, targetRecords, productionAuthorityContext,
  baseHeadCommit, baseHeadTreeOid, currentEpoch, authorizationEpoch,
  derivedProvenance, isAncestor, baselineAnchors,
}) {
  const errors = [];
  let authority;
  try { authority = readProductionAuthorityContext(productionAuthorityContext); }
  catch (error) { errors.push(issue("GATE-G0", "GATE-PROPOSAL-AUTHORITY",
    `unverified accepted-base authority: ${error.message}`)); }
  if (authority && (authority.profile !== "gate-evaluation"
    || authority.gateEffective !== true
    || authority.headCommit !== baseHeadCommit
    || authority.headTreeOid !== baseHeadTreeOid)) {
    errors.push(issue("GATE-G0", "GATE-PROPOSAL-BASE-BINDING",
      "authority must bind the accepted all-red base Head and Tree"));
  }
  if (!canonicalBytes(gateVector(baseRecords))
    .equals(canonicalBytes(ALL_RED_G0_GATE_VECTOR))) {
    errors.push(issue("GATE-G0", "GATE-PROPOSAL-BASE-VECTOR",
      "accepted proposal base must contain the exact all-red Gate vector"));
  }
  if (!canonicalBytes(gateVector(targetRecords))
    .equals(canonicalBytes(FINAL_G0_GATE_VECTOR))) {
    errors.push(issue("GATE-G0", "GATE-PROPOSAL-TARGET-VECTOR",
      "proposal target must contain the exact sole-green G0 Gate vector"));
  }
  errors.push(...soleG0RecordProjectionErrors(baseRecords, targetRecords));
  const targetGate = targetRecords.get("GATE-G0")?.record;
  if (targetGate && authority) errors.push(...gateSupportPrerequisiteErrors(
    targetGate, targetRecords, {
      currentEpoch, authorizationEpoch, derivedProvenance,
      isAncestor, baselineAnchors, now: authority.trustedTime?.now,
    }));
  return Object.freeze({ errors: Object.freeze(errors.sort((left, right) => cmp(
    `${left.record}\0${left.rule}\0${left.message}`,
    `${right.record}\0${right.rule}\0${right.message}`,
  ))), status: "LOCAL-GATE-PROPOSAL-ONLY", gateEffective: false,
  authorityRequired: Object.freeze(["g0-operator-acceptance", "remote-acceptance"]) });
}
```

`baseHeadCommit` and `baseHeadTreeOid` come only from the concrete Plan-03
read-only repository view at the accepted base; the CLI does not expose a
caller hook for them. Add source tests proving the proposal function contains
no import/call of the production issuer or effective transition validator.
Pass a clean proposal result and its structured clone to
`readProductionAuthorityContext`, `gateEligibilityErrors` as
`productionAuthorityContext`, and every Plan-11 authority-result guard; all
must reject. Even a zero-error proposal result remains exactly
`LOCAL-GATE-PROPOSAL-ONLY`, `gateEffective:false`, with both required external
authorities and no capability brand.

- [ ] **Step 3: Compose all semantic checks**

Export the exact array-returning composition below. `derivedProvenanceHistory` is
the validator-derived result from Task 6 for this adjacent state; it is not
accepted from a register or CLI flag.

```js
const changed = (id, records, previousRecords) => {
  const before = previousRecords.get(id)?.record ?? null;
  const after = records.get(id)?.record ?? null;
  return !before || !after || !canonicalBytes(before).equals(canonicalBytes(after));
};

function findingHistoryErrors(review, priorReview) {
  const errors = [];
  for (const finding of review.findings) {
    const bothNull = finding.lineStart === null && finding.lineEnd === null;
    const validRange = Number.isInteger(finding.lineStart)
      && Number.isInteger(finding.lineEnd) && finding.lineEnd >= finding.lineStart;
    if (!bothNull && !validRange) errors.push(issue(review.id,
      "REV-FINDING-LINES", `${finding.findingId} has invalid line bounds`));
  }
  if (priorReview && priorReview.status !== "requested"
    && !canonicalBytes(priorReview.findings).equals(canonicalBytes(review.findings))) {
    errors.push(issue(review.id, "REV-FINDING-MUTATED", "decided findings changed"));
  }
  return errors;
}

export function reviewsEvidenceGateErrors({
  records, previousRecords, repositoryReader, manifestReader, lifecycleContext,
  derivedProvenanceHistory, currentEpoch, authorizationEpochs,
  productionAuthorityContext, targetHeadCommit, targetHeadTreeOid,
  isAncestor, baselineAnchors,
}) {
  const errors = [];
  const reviews = [...records.values()].filter((entry) => entry.family === "REV")
    .map((entry) => entry.record);
  const evidenceRecords = [...records.values()].filter((entry) => entry.family === "EVID")
    .map((entry) => entry.record);
  const evidenceArtifactSet = verifyEvidenceArtifactSet(evidenceRecords,
    manifestReader);
  errors.push(...evidenceArtifactSet.errors);
  const reviewsById = new Map(reviews.map((review) => [review.id, review]));
  errors.push(...indexFindings(reviews).errors);

  for (const review of reviews) {
    if (!changed(review.id, records, previousRecords)) continue;
    const prior = previousRecords.get(review.id)?.record ?? null;
    errors.push(...reviewSeparationErrors(review, { lifecycleContext }));
    errors.push(...reviewExecutionErrors(review, lifecycleContext));
    errors.push(...reviewSubjectErrors(review, repositoryReader, lifecycleContext));
    errors.push(...findingHistoryErrors(review, prior));
    errors.push(...findingResolutionErrors(review, reviewsById, records,
      repositoryReader, lifecycleContext));
  }

  for (const evidence of evidenceRecords) {
    if (!changed(evidence.id, records, previousRecords)) continue;
    errors.push(...evidenceStateErrors(evidence, { lifecycleContext }));
    errors.push(...evidenceManifestErrors(evidence, manifestReader,
      derivedProvenanceHistory));
    errors.push(...evidenceReviewErrors(evidence, lifecycleContext,
      evidenceArtifactSet));
    errors.push(...evidenceSupersessionErrors(evidence,
      previousRecords.get(evidence.id)?.record ?? null, records,
      repositoryReader));
  }

  errors.push(...exceptionProvenanceErrors(records,
    derivedProvenanceHistory));
  errors.push(...noWaiverErrors(records, derivedProvenanceHistory));
  for (const entry of records.values()) if (entry.family === "GATE") {
    errors.push(...gateEligibilityErrors(entry.record, records, {
      currentEpoch,
      authorizationEpoch: authorizationEpochs.get(entry.record.id) ?? null,
      derivedProvenance: derivedProvenanceHistory,
      productionAuthorityContext, targetHeadCommit, targetHeadTreeOid,
      isAncestor, baselineAnchors, evidenceArtifactSet,
    }));
  }
  return errors.sort((a, b) => cmp(
    `${a.file}\0${a.record}\0${a.rule}\0${a.message}`,
    `${b.file}\0${b.record}\0${b.rule}\0${b.message}`,
  ));
}
```

`productionAuthorityContext` is the opaque module-branded capability minted by
Plan 11. The only field access is through
`readProductionAuthorityContext(context)`; the resulting frozen claims must be
exactly `profile:"gate-evaluation", gateEffective:true`. Raw pins, caller time,
string/boolean hooks, plain objects, serialized copies and the distinct
`pre-genesis-ceremony` profile are rejected before they can influence a Gate.
For `GATE-G0` those same branded claims must contain the Plan-11-verified
non-null `operatorAcceptance` claim bound to the identical authority Head,
Tree, exact scope `AURELIA-G0-GOVERNANCE-ACCEPTANCE`, and
`SHA256(RFC8785(FINAL_G0_GATE_VECTOR))`. A null claim is permitted for every
other/intermediate Gate and never upgrades it.

`baselineAnchors` comes from the protected D/I execution record and is compared
to exact full SHAs already present in the records. `isAncestor(older, newer)`
is the fail-closed Git-object resolver from Plan 03 and is used only to prove
the additional strict D→I relationship. It never authorizes an arbitrary older
baseline: the closed policy requires each named EVID/REV to equal its exact D
or I anchor and exact scope. Missing objects, shallow-history ambiguity or
resolver failure emits `GATE-BASELINE-ANCHORS`. Plans 05/06/11 supply the
cryptographic/acceptance/transparency authority result; missing or unknown
authority keeps attempted green Gates red.

- [ ] **Step 4: Run tests and commit**

```powershell
node --test scripts/governance/reviews-evidence-gates.test.mjs scripts/governance/exception-provenance.test.mjs
git add scripts/governance/reviews-evidence-gates.mjs scripts/governance/reviews-evidence-gates.test.mjs
git commit -m "feat: derive fail-closed governance gate eligibility"
```

### Task 8: Compose Plan-04 semantics and run sequential verification

**Files:**

- Modify: `scripts/governance-contract.mjs`
- Modify: `scripts/governance-contract.test.mjs`

- [ ] **Step 1: Add aggregate order/no-write tests**

Use a temporary replay with one error from schema, reference, ledger, review, evidence, provenance and gate layers. Assert deterministic layer/rule order and byte-identical repository before/after. Test the real pre-Genesis repository returns nonzero `AUTHORITY-RED/PRE-GENESIS`, not a local-pass claim.

- [ ] **Step 2: Add semantic composition only after replay succeeds**

For every adjacent First-Parent step, call schema/reference/ledger first. Only a
structurally replayable state advances the validator-owned provenance history:

```js
let derivedProvenanceHistory = new Map();
for (const adjacent of acceptedFirstParentSteps) {
  const structuralErrors = validateAdjacentStructure(adjacent);
  if (structuralErrors.length) {
    diagnostics.push(...structuralErrors);
    continue;
  }
  const candidateHistory = advanceExceptionProvenanceHistory(adjacent.records,
    adjacent.approvedExceptionHistory, derivedProvenanceHistory);
  const semanticErrors = reviewsEvidenceGateErrors({
    records: adjacent.records,
    previousRecords: adjacent.previousRecords,
    repositoryReader: adjacent.repositoryReader,
    manifestReader: adjacent.manifestReader,
    lifecycleContext: adjacent.lifecycleContext,
    derivedProvenanceHistory: candidateHistory,
    currentEpoch: adjacent.currentEpoch,
    authorizationEpochs: adjacent.authorizationEpochs,
    productionAuthorityContext: adjacent.productionAuthorityContext,
    targetHeadCommit: adjacent.targetHeadCommit,
    targetHeadTreeOid: adjacent.targetHeadTreeOid,
    isAncestor: adjacent.repositoryReader.isAncestor,
    baselineAnchors: adjacent.baselineAnchors,
  });
  diagnostics.push(...semanticErrors);
  if (semanticErrors.length === 0) derivedProvenanceHistory = candidateHistory;
}
```

`acceptedFirstParentSteps` and every `adjacent.*` member are constructed inside
the CLI from Plan-03 replay plus later branded authority layers; they are not
deserialized caller objects. `targetHeadCommit` is the adjacent target's full
Git SHA and `targetHeadTreeOid` is read from that same immutable commit object;
neither may come from a record or CLI value. Malformed schema never reaches semantics.
Structural or semantic failure never advances history and never throws away
diagnostics. The CLI remains non-writing.

- [ ] **Step 3: Run every gate in order**

```powershell
node --experimental-strip-types --test scripts/governance-contract.test.mjs
node --test scripts/governance/reviews-evidence-gates.test.mjs
node --test scripts/governance/exception-provenance.test.mjs
npm test
npm run typecheck:governance
npm run check:canon
npm run typecheck
npm run lint
git diff --check
git status --short
```

Expected: all test/static commands exit 0; the explicit real-repository pre-Genesis test expects the validator's nonzero red-authority result. No real register, UI, server, remote, Chrome, or M-G1 path changes.

- [ ] **Step 4: Commit a gate-only correction if required, then stop**

```powershell
git add docs/governance/governance.schema.json scripts/governance scripts/governance-contract.mjs scripts/governance-contract.test.mjs
git commit -m "test: close reviews evidence and no-waiver gates"
```

Do not create the authoritative registers or claim `GATE-G0 green`; Plan 12 performs the atomic first import after Plans 05–11 provide cryptographic and external proof layers.
