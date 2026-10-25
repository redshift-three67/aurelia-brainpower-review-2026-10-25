# AURELIA G0 Append-Only Transition Ledger Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every governance state change replayable from a Git-pinned, globally ordered, append-only EVT ledger and reject deletion, rewriting, illegal transitions, illegal amendments, non-governance commits, and operator-lockout paths.

**Architecture:** `repository-view.mjs` provides a read-only working-tree or explicit `--base/--head` view, rejects non-fatal UTF-8 decoding, and proves that every ranged base is on the actual First-Parent chain. `record-hashes.mjs` owns the exact RFC-8785 projections. `status-transitions.mjs` is the closed lifecycle/amendment/actor policy. `transition-ledger.mjs` validates the immutable prefix, global chain, one-event-per-record transaction rule, record replay, source-only commit boundary, epoch rotations, and special ROLE bundles. The CLI exposes closed pre-Genesis, local-preflight, and production-replay modes; only production replay consumes a verified remote bundle, while local success is explicitly non-gate-effective.

**Tech Stack:** Node.js 22 ESM, `node:test`, Git via `execFileSync` argument arrays, canonicalize 4.0.0, SHA-256, JSON Schema Draft 2020-12.

---

## Scope and file map

- Create `scripts/governance/repository-view.mjs` and `.test.mjs`.
- Create `scripts/governance/record-hashes.mjs` and `.test.mjs`.
- Create `scripts/governance/status-transitions.mjs` and `.test.mjs`.
- Create `scripts/governance/transition-ledger.mjs` and `.test.mjs`.
- Modify `docs/governance/governance.schema.json`: replace only `$defs.transition` with the closed EVT contract.
- Modify `scripts/governance-contract.mjs` and `.test.mjs`: implement the closed pre-Genesis, explicit Working-Tree preflight, explicit commit preflight, and remote production-replay argument modes used by Plans 12/13.

Do not create attestations, keys, receipts, remote pins, register seed records, or server state. Plan 05 verifies `authorizationAttestations`, Genesis and trust roots; Plan 06 verifies external acceptance and transparency. Until those plans pass, ledger success is structural preflight only and no gate can be declared green.

### Task 1: Read exact repository states without a shell

**Files:**

- Create: `scripts/governance/repository-view.mjs`
- Create: `scripts/governance/repository-view.test.mjs`

- [ ] **Step 1: Write failing committed-tree and working-tree tests**

Use `makeTempRepository(t)` and `commitAll`. Verify: full SHA normalization; `readText(path, "base")`; `readText(path, "head")`; absent base path returns `null`; working-tree text is read from disk; UTF-8 BOM and malformed UTF-8 fail in committed and working blobs; symlink/submodule modes are rejected; `changedEntries()` returns code-unit-sorted `{ path, oldMode, newMode, oldSha256, newSha256 }` values. Create a merge whose second parent is the requested base and assert `firstParentRange(secondParent, merge)` throws; a base on the real First-Parent chain returns every adjacent commit oldest-first.

Add these exact regressions after the positive repository-view test:

```js
import { execFileSync } from "node:child_process";
import { writeFileSync } from "node:fs";
import { resolve } from "node:path";

function writeBytes(root, path, bytes) {
  writeFileSync(resolve(root, path), bytes, { flag: "w" });
}

function testGit(root, args) {
  return execFileSync("git", args, { cwd: root, encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"] }).trim();
}

function makeMergeFixture(t) {
  const fixture = makeTempRepository(t);
  writeBytes(fixture.root, "base.txt", Buffer.from("base\n", "utf8"));
  const base = commitAll(fixture.root, "base");
  testGit(fixture.root, ["switch", "-c", "side"]);
  writeBytes(fixture.root, "side.txt", Buffer.from("side\n", "utf8"));
  const side = commitAll(fixture.root, "side");
  testGit(fixture.root, ["switch", "--detach", base]);
  writeBytes(fixture.root, "main.txt", Buffer.from("main\n", "utf8"));
  const main = commitAll(fixture.root, "main");
  testGit(fixture.root, ["merge", "--no-ff", "--no-edit", side]);
  const merge = testGit(fixture.root, ["rev-parse", "HEAD"]);
  return { root: fixture.root, base, main, side, merge };
}

test("readText rejects BOM and malformed UTF-8 on both repository sides", (t) => {
  const fixture = makeTempRepository(t);
  writeBytes(fixture.root, "bad.txt", Buffer.from([0xef, 0xbb, 0xbf, 0x61]));
  const bomCommit = commitAll(fixture.root, "add BOM");
  assert.throws(() => createRepositoryView({ root: fixture.root, base: bomCommit }).readText("bad.txt", "base"), /UTF-8 BOM is forbidden: bad\.txt/);
  writeBytes(fixture.root, "bad.txt", Buffer.from([0xc3, 0x28]));
  assert.throws(() => createRepositoryView({ root: fixture.root, base: bomCommit }).readText("bad.txt", "head"), /invalid UTF-8: bad\.txt/);
  const malformedCommit = commitAll(fixture.root, "replace with malformed UTF-8");
  assert.throws(() => createRepositoryView({ root: fixture.root,
    base: malformedCommit }).readText("bad.txt", "base"), /invalid UTF-8: bad\.txt/);
  writeBytes(fixture.root, "bad.txt", Buffer.from([0xef, 0xbb, 0xbf, 0x61]));
  assert.throws(() => createRepositoryView({ root: fixture.root,
    base: malformedCommit }).readText("bad.txt", "head"), /UTF-8 BOM is forbidden: bad\.txt/);
});

test("range base must be on the actual First-Parent chain", (t) => {
  const fixture = makeMergeFixture(t);
  const view = createRepositoryView({ root: fixture.root, base: fixture.main, head: fixture.merge });
  assert.deepEqual(view.firstParentRange(fixture.main, fixture.merge), [fixture.merge]);
  assert.throws(
    () => view.firstParentRange(fixture.side, fixture.merge),
    /base is not on first-parent chain/,
  );
});
```

- [ ] **Step 2: Run and observe the missing module**

Run `node --test scripts/governance/repository-view.test.mjs`.

Expected: FAIL with `ERR_MODULE_NOT_FOUND`.

- [ ] **Step 3: Implement the complete Git adapter**

Create `scripts/governance/repository-view.mjs`:

```js
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, lstatSync, readFileSync } from "node:fs";
import { isAbsolute, relative, resolve } from "node:path";

const FULL_SHA = /^[0-9a-f]{40}$/;
const sortCodeUnit = (a, b) => a < b ? -1 : a > b ? 1 : 0;
const digest = (bytes) => createHash("sha256").update(bytes).digest("hex");
const fatalUtf8 = new TextDecoder("utf-8", { fatal: true });

function decodeUtf8(bytes, label, { allowBom = false } = {}) {
  if (!allowBom && bytes.length >= 3
    && bytes[0] === 0xef && bytes[1] === 0xbb && bytes[2] === 0xbf) {
    throw new Error(`UTF-8 BOM is forbidden: ${label}`);
  }
  try { return fatalUtf8.decode(bytes); }
  catch { throw new Error(`invalid UTF-8: ${label}`); }
}

function git(root, args, encoding = null) {
  return execFileSync("git", args, { cwd: root, encoding, stdio: ["ignore", "pipe", "pipe"] });
}

const splitNul = (buffer) => decodeUtf8(buffer, "Git NUL output", { allowBom: true }).split("\0").filter(Boolean);
function safePath(root, path) {
  const target = resolve(root, path);
  const rel = relative(root, target);
  if (isAbsolute(rel) || rel === ".." || rel.startsWith(`..${process.platform === "win32" ? "\\" : "/"}`)) throw new Error(`path escapes repository: ${path}`);
  return target;
}

export function resolveCommit(root, ref) {
  const sha = git(root, ["rev-parse", "--verify", `${ref}^{commit}`], "utf8").trim();
  if (!FULL_SHA.test(sha)) throw new Error(`not a full commit SHA: ${ref}`);
  return sha;
}

export function createRepositoryView({ root = process.cwd(), base = "HEAD", head = null } = {}) {
  const resolvedRoot = resolve(root);
  const baseSha = resolveCommit(resolvedRoot, base);
  const headSha = head === null ? null : resolveCommit(resolvedRoot, head);

  function commitEntry(path, commit) {
    const rows = splitNul(git(resolvedRoot, ["ls-tree", "-z", commit, "--", path]));
    if (rows.length === 0) return null;
    if (rows.length !== 1) throw new Error(`ambiguous tree entry: ${path}`);
    const match = rows[0].match(/^(\d{6}) (blob|commit) ([0-9a-f]{40})\t([\s\S]+)$/);
    if (!match || match[4] !== path) throw new Error(`unparseable tree entry: ${path}`);
    const [, mode, type, oid] = match;
    if (type !== "blob" || !["100644", "100755"].includes(mode)) throw new Error(`unsupported tree mode ${mode}: ${path}`);
    return { mode, oid };
  }

  function readCommit(path, commit) {
    const entry = commitEntry(path, commit);
    return entry === null ? null : git(resolvedRoot, ["cat-file", "blob", entry.oid]);
  }

  function readWorking(path) {
    const target = safePath(resolvedRoot, path);
    if (!existsSync(target)) return null;
    const stat = lstatSync(target);
    if (stat.isSymbolicLink() || !stat.isFile()) throw new Error(`unsupported working-tree entry: ${path}`);
    return readFileSync(target);
  }

  function readBytes(path, side) {
    if (side === "base") return readCommit(path, baseSha);
    if (side === "head") return headSha === null ? readWorking(path) : readCommit(path, headSha);
    throw new Error(`unknown repository side: ${side}`);
  }

  function readText(path, side) {
    const bytes = readBytes(path, side);
    return bytes === null ? null : decodeUtf8(bytes, path);
  }

  function parentsOf(commit) {
    return git(resolvedRoot, ["rev-list", "--parents", "-n", "1", commit], "utf8")
      .trim().split(" ").slice(1);
  }

  function changedEntries() {
    const tokens = splitNul(git(resolvedRoot, headSha === null
      ? ["diff", "--name-status", "-z", "-M", baseSha, "--"]
      : ["diff", "--name-status", "-z", "-M", baseSha, headSha, "--"]));
    const changes = new Map();
    for (let index = 0; index < tokens.length;) {
      const status = tokens[index++];
      if (/^[RC][0-9]+$/.test(status)) {
        const sourcePath = tokens[index++];
        const path = tokens[index++];
        changes.set(path, { changeKind: status[0], sourcePath });
      } else {
        const path = tokens[index++];
        changes.set(path, { changeKind: status[0], sourcePath: null });
      }
    }
    if (headSha === null) for (const path of splitNul(git(resolvedRoot, ["ls-files", "-z", "--others", "--exclude-standard"]))) changes.set(path, { changeKind: "A", sourcePath: null });
    return [...changes.keys()].sort(sortCodeUnit).map((path) => {
      const oldEntry = commitEntry(path, baseSha);
      const oldBytes = oldEntry && readCommit(path, baseSha);
      const newEntry = headSha === null ? null : commitEntry(path, headSha);
      const newBytes = headSha === null ? readWorking(path) : newEntry && readCommit(path, headSha);
      let newMode = newEntry?.mode ?? "000000";
      if (headSha === null && newBytes) {
        const index = splitNul(git(resolvedRoot, ["ls-files", "-s", "-z", "--", path]));
        newMode = index.length ? index[0].slice(0, 6) : "100644";
        if (process.platform !== "win32") newMode = (lstatSync(safePath(resolvedRoot, path)).mode & 0o111) === 0 ? "100644" : "100755";
        if (!["100644", "100755"].includes(newMode)) throw new Error(`unsupported working-tree mode ${newMode}: ${path}`);
      }
      return { path, ...changes.get(path), oldMode: oldEntry?.mode ?? "000000", newMode, oldSha256: oldBytes && digest(oldBytes), newSha256: newBytes && digest(newBytes) };
    });
  }

  return {
    root: resolvedRoot, baseSha, headSha,
    readBytes,
    readText,
    changedEntries,
    parentsOf,
    firstParentRange: (older = baseSha, newer = headSha) => {
      if (newer === null) return [];
      const commits = git(resolvedRoot,
        ["rev-list", "--first-parent", "--reverse", `${older}..${newer}`], "utf8")
        .trim().split("\n").filter(Boolean);
      let expectedParent = older;
      for (const commit of commits) {
        if (parentsOf(commit)[0] !== expectedParent) {
          throw new Error(`base is not on first-parent chain: ${older}..${newer}`);
        }
        expectedParent = commit;
      }
      if (expectedParent !== newer) {
        throw new Error(`base is not on first-parent chain: ${older}..${newer}`);
      }
      return commits;
    },
    isAncestor: (older, newer) => {
      try { git(resolvedRoot, ["merge-base", "--is-ancestor", older, newer]); return true; }
      catch { return false; }
    },
  };

}
```

- [ ] **Step 4: Run repository-view tests**

Run `node --test scripts/governance/repository-view.test.mjs`.

Expected: every case passes, including staged-only, unstaged-only, untracked,
delete, Unix chmod/mode drift, fatal UTF-8/BOM rejection, and rejection of a
base reachable only through a merge's non-first parent. NUL-delimited paths
containing tabs/newlines are not split incorrectly. Commands use argument
arrays, `shell` is never enabled, and returned SHAs are 40 lowercase hex
characters.

- [ ] **Step 5: Commit the read-only repository view**

```powershell
git add scripts/governance/repository-view.mjs scripts/governance/repository-view.test.mjs
git commit -m "feat: add Git-pinned governance repository views"
```

### Task 2: Define exact canonical EVT hash projections

**Files:**

- Create: `scripts/governance/record-hashes.mjs`
- Create: `scripts/governance/record-hashes.test.mjs`

- [ ] **Step 1: Write fixed vectors before implementation**

Create tests for Unicode keys, reordered object properties, `-0`, nested arrays, and these projections: record hash; `changeDigest`; authorization core excluding exactly three fields; event hash excluding exactly `eventHash`. Assert 64 lowercase hex and that changing any included byte changes the digest.

- [ ] **Step 2: Confirm the module is absent**

Run `node --test scripts/governance/record-hashes.test.mjs`.

Expected: FAIL with `ERR_MODULE_NOT_FOUND`.

- [ ] **Step 3: Implement every projection explicitly**

Create `scripts/governance/record-hashes.mjs`:

```js
import { createHash } from "node:crypto";
import { canonicalBytes } from "./rfc8785.mjs";

export function sha256Hex(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

export const recordSha256 = (record) => sha256Hex(canonicalBytes(record));

export function changeDigest(event) {
  return sha256Hex(canonicalBytes({
    recordRef: event.recordRef,
    eventKind: event.eventKind,
    previousRecordSha256: event.previousRecordSha256,
    resultingRecordSha256: event.resultingRecordSha256,
  }));
}

export function eventAuthorizationPayloadSha256(event) {
  const {
    eventAuthorizationPayloadSha256: ignoredPayload,
    authorizationAttestations: ignoredAttestations,
    eventHash: ignoredHash,
    ...core
  } = event;
  return sha256Hex(canonicalBytes(core));
}

export function eventHash(event) {
  const { eventHash: ignoredHash, ...envelope } = event;
  return sha256Hex(canonicalBytes(envelope));
}

export const emptyTrustRootDeltaSha256 = () => sha256Hex(canonicalBytes([]));
```

- [ ] **Step 4: Run fixed-vector tests twice**

Run the same focused command twice.

Expected: identical results, all tests pass, no locale-sensitive ordering.

- [ ] **Step 5: Commit the projection helpers**

```powershell
git add scripts/governance/record-hashes.mjs scripts/governance/record-hashes.test.mjs
git commit -m "feat: bind canonical governance event hashes"
```

### Task 3: Encode the EVT schema as a closed record

**Files:**

- Modify: `docs/governance/governance.schema.json`
- Modify: `scripts/governance/schema-validator.test.mjs`

- [ ] **Step 1: Add a failing exact-event schema test**

Construct a valid EVT with all 20 required properties from Design §12.5, one actor attestation, and `genesisAnchor: null`. Mutate each of: extra property, short commit, uppercase hash, missing attestation field, unknown purpose, negative epoch, invalid RFC3339. Every mutation must fail.

- [ ] **Step 2: Replace `$defs.transition: false` with the complete schema**

Use a closed object with required fields exactly:

```json
["id","eventKind","recordRef","fromStatus","toStatus","previousRecordSha256","resultingRecordSha256","changeDigest","trustRootDeltaSha256","actorRole","actorAssigneeSnapshot","operatorEpoch","occurredAt","baseCommit","evidenceRefs","previousEventHash","eventAuthorizationPayloadSha256","eventHash","authorizationAttestations","genesisAnchor"]
```

Properties are exact: EVT ID `^EVT-[0-9]{6}$`; five `eventKind` values; nullable `fromStatus`, previous record/event hashes; full SHA-1 commit; nonnegative integer epoch; RFC3339 time; unique EVID refs; hash definitions from Plan 02; `authorizationAttestations` items reference a closed `$defs.authorizationAttestation`; `genesisAnchor` is `null` or the closed `$defs/genesisAnchor` containing every field in Design §12.5. The attestation definition requires exactly `method`, `attestationPurpose`, `keyRef`, `signerIdentity`, `signerRole`, `signedAt`, `nonce`, `envelopeSha256`, `signature`; method is `ed25519`, purpose is the exact eight-value enum (`actor`, `approver`, `incoming-operator`, `recovery-root`, `custodian-a`, `custodian-b`, `incoming-custodian-a`, `incoming-custodian-b`), and no additional property is allowed.

- [ ] **Step 3: Run schema tests**

Run `node --test scripts/governance/schema-validator.test.mjs`.

Expected: the valid EVT passes; every mutation fails at the exact property.

- [ ] **Step 4: Commit the event schema**

```powershell
git add docs/governance/governance.schema.json scripts/governance/schema-validator.test.mjs
git commit -m "feat: define the closed governance event schema"
```

### Task 4: Encode closed lifecycle, amendment, and actor policy

**Files:**

- Create: `scripts/governance/status-transitions.mjs`
- Create: `scripts/governance/status-transitions.test.mjs`

- [ ] **Step 1: Write a table-driven full transition cross-product test**

Import `RECORD_STATUSES` from the Plan-02-owned
`scripts/governance/lifecycle-contract.mjs`. For every family, generate every
`(from,to)` pair across that shared status enum plus `null`; assert the
following exported policy is the complete allowlist. Also assert that the set
of every non-null endpoint occurring in `TRANSITIONS[family]` equals
`RECORD_STATUSES[family]` exactly. Exercise valid IDs for `REQ-HR-*`,
`REQ-GOV-*`, numeric REQ, and every other family, plus malformed/unknown IDs.
Add explicit regressions proving `ROLE suspended` participates in the shared
cross-product and that `COMP verified` is neither a status nor a transition
endpoint. Add negative tests for generic ROLE `assigned→assigned`, transition
with equal states, amend with unequal states, finalized-record amend,
immutable field changes, and manual exception-provenance insertion/removal.

Use this shared-contract assertion in
`scripts/governance/status-transitions.test.mjs` (in addition to the full
allowed/denied pair loop):

```js
const compareCodeUnit = (left, right) => left < right ? -1 : left > right ? 1 : 0;
for (const [family, statuses] of Object.entries(RECORD_STATUSES)) {
  test(`${family} transition endpoints equal the Plan-02 lifecycle contract`, () => {
    const endpoints = new Set();
    for (const pair of TRANSITIONS[family]) {
      const [from, to] = pair.split(">");
      if (from !== "null") endpoints.add(from);
      endpoints.add(to);
    }
    assert.deepEqual([...endpoints].sort(compareCodeUnit),
      [...statuses].sort(compareCodeUnit));
  });
}
assert(RECORD_STATUSES.ROLE.includes("suspended"));
assert(!RECORD_STATUSES.COMP.includes("verified"));
```

- [ ] **Step 2: Implement the closed tables and pure checks**

Create `scripts/governance/status-transitions.mjs`:

```js
import { canonicalBytes } from "./rfc8785.mjs";
import { RECORD_STATUSES } from "./lifecycle-contract.mjs";

const pairs = (text) => new Set(text.split(" "));
export const TRANSITIONS = Object.freeze({
  REQ: pairs("null>proposed proposed>approved proposed>retired approved>implemented approved>retired implemented>verified implemented>retired verified>retired"),
  CTRL: pairs("null>proposed proposed>implemented proposed>retired implemented>verified implemented>retired verified>retired"),
  COMP: pairs("null>proposed proposed>approved proposed>retired approved>implemented approved>retired implemented>retired"),
  PROFILE: pairs("null>proposed proposed>approved proposed>retired approved>active approved>retired active>retired"),
  ROLE: pairs("null>unassigned null>assigned unassigned>assigned unassigned>retired assigned>unassigned assigned>suspended assigned>retired suspended>assigned suspended>retired"),
  RISK: pairs("null>open open>treated open>accepted open>closed treated>open treated>accepted treated>closed accepted>open accepted>closed closed>open"),
  DATA: pairs("null>catalogued catalogued>planned catalogued>retired planned>active planned>retired active>retired"),
  FLOW: pairs("null>catalogued catalogued>planned catalogued>retired planned>active planned>retired active>retired"),
  GATE: pairs("null>red red>amber red>green red>expired amber>red amber>green amber>expired green>red green>expired expired>red"),
  REV: pairs("null>requested requested>changes-required requested>approved changes-required>superseded approved>superseded"),
  EVID: pairs("null>expected null>captured expected>captured captured>verified captured>invalidated captured>superseded verified>invalidated verified>superseded invalidated>superseded"),
  EXC: pairs("null>requested requested>approved requested>revoked requested>expired approved>revoked approved>expired"),
});

const compareCodeUnit = (left, right) => left < right ? -1 : left > right ? 1 : 0;
for (const [family, statuses] of Object.entries(RECORD_STATUSES)) {
  const endpoints = new Set();
  for (const pair of TRANSITIONS[family] ?? []) {
    const [from, to] = pair.split(">");
    if (from !== "null") endpoints.add(from);
    endpoints.add(to);
  }
  if (!canonicalBytes([...endpoints].sort(compareCodeUnit))
    .equals(canonicalBytes([...statuses].sort(compareCodeUnit)))) {
    throw new Error(`${family} transition endpoints drift from lifecycle contract`);
  }
}

const COMMON_AMEND = ["title", "sourceRefs", "reviewOn", "ownerRole"];
export const AMEND = Object.freeze({
  REQ: { statuses: ["proposed"], fields: [...COMMON_AMEND, "sourceQuote", "sourceQuoteSourceRef", "sourceQuoteSha256", "normalizedRequirement", "productDecisionRefs", "profileRefs", "dataRefs", "componentRefs", "roleRefs", "controlRefs", "riskRefs", "gateRefs", "verificationMethod", "evidenceRefs", "acceptanceCriteria"] },
  CTRL: { statuses: ["proposed"], fields: [...COMMON_AMEND, "controlType", "objective", "requirementRefs", "riskRefs", "profileRefs", "implementationPaths", "verificationMethod", "evidenceRefs", "failureBehavior", "gateRefs"] },
  COMP: { statuses: ["proposed"], fields: [...COMMON_AMEND, "componentKind", "trustZone", "profileRefs", "requirementRefs", "controlRefs", "implementationPaths", "gateRefs"] },
  PROFILE: { statuses: ["proposed"], fields: [...COMMON_AMEND, "purpose", "maximumDataClass", "identityAuthority", "allowedCapabilities", "forbiddenCapabilities", "secretDataRefs", "serverAccessLevel", "requirementRefs", "gateRefs"] },
  ROLE: { statuses: ["unassigned"], fields: ["qualificationRequirements", "separationFromRoleRefs"] },
  RISK: { statuses: ["open", "treated"], fields: [...COMMON_AMEND, "scenario", "dataRefs", "profileRefs", "componentRefs", "cause", "threatOrFailure", "likelihood", "impactSecurity", "impactPrivacy", "impactOperations", "impactProduct", "inherentRating", "residualRating", "controlRefs", "treatment", "dueOn", "requirementRefs", "gateRefs"] },
  DATA: { statuses: ["catalogued", "planned"], fields: [...COMMON_AMEND, "dataSubjectGroups", "fields", "classification", "purpose", "plannedLegalBasis", "controllerRole", "processorNames", "storageLocations", "regions", "encryptionAtRest", "keyOwnerRole", "accessRoleRefs", "retentionRule", "backupRule", "exportRule", "deletionRule", "prohibitedDestinations", "gateRefs"] },
  FLOW: { statuses: ["catalogued", "planned"], fields: [...COMMON_AMEND, "dataRefs", "purpose", "sourceComponentRef", "targetComponentRef", "trustBoundary", "profileRefs", "transportProtection", "authentication", "authorization", "loggingRule", "processorNames", "regionPath", "controlRefs", "riskRefs", "gateRefs"] },
  GATE: { statuses: ["red", "amber"], fields: ["title", "sourceRefs", "reviewOn", "entryCriteria", "exitCriteria", "requiredEvidenceRefs", "verifierRoleRefs", "approverRoleRefs", "expiresOn"] },
  REV: { statuses: ["requested"], fields: ["subjectIds", "subjectPaths", "scope", "evidenceSubjectRefs", "reviewerRole", "independentFrom", "reviewerExecution", "modelName", "reasoningLevel", "promptDigest", "reasoningApprovalEvidenceRef", "externalReviewEvidenceRefs", "evidenceRefs", "expiresOn"] },
  EVID: { statuses: ["expected"], fields: ["evidenceType", "producerRole", "subjectIds", "subjectPaths", "scope", "command", "derivationRefs", "governanceChangeDigests", "retentionRule"] },
  EXC: { statuses: ["requested"], fields: ["scopeIds", "justification", "compensatingControlRefs", "requestedByRole", "expiresAt", "evidenceRefs", "blockedGateRefs"] },
});

export function recordFamily(id) {
  const match = /^(REQ|CTRL|PROFILE|ROLE|COMP|RISK|DATA|FLOW|GATE|REV|EVID|EXC)-/.exec(id);
  if (!match) throw new Error(`unknown governance record family: ${id}`);
  return match[1];
}
export const transitionAllowed = (family, from, to) => TRANSITIONS[family]?.has(`${from ?? "null"}>${to}`) ?? false;

export function changedTopLevelFields(before, after) {
  return [...new Set([...Object.keys(before), ...Object.keys(after)])]
    .filter((key) => Object.hasOwn(before, key) !== Object.hasOwn(after, key)
      || !canonicalBytes(before[key]).equals(canonicalBytes(after[key])))
    .sort((a, b) => a < b ? -1 : a > b ? 1 : 0);
}

export function amendmentAllowed(family, before, after, expectedExceptionProvenance = before.exceptionProvenanceRefs) {
  const policy = AMEND[family];
  if (!policy || before.status !== after.status || !policy.statuses.includes(before.status)) return false;
  const allowed = new Set([...policy.fields, "exceptionProvenanceRefs"]);
  const changed = changedTopLevelFields(before, after);
  if (changed.some((field) => !allowed.has(field))) return false;
  return canonicalBytes(after.exceptionProvenanceRefs).equals(canonicalBytes(expectedExceptionProvenance));
}
```

- [ ] **Step 3: Run the complete matrix tests**

Run `node --test scripts/governance/status-transitions.test.mjs`.

Expected: all allowlisted pairs pass, every other cross-product pair fails, and no locale or current date affects the result.

- [ ] **Step 4: Commit lifecycle policy**

```powershell
git add scripts/governance/status-transitions.mjs scripts/governance/status-transitions.test.mjs
git commit -m "feat: close governance lifecycle transitions"
```

### Task 5: Replay the append-only ledger against base and target records

**Files:**

- Create: `scripts/governance/transition-ledger.mjs`
- Create: `scripts/governance/transition-ledger.test.mjs`

- [ ] **Step 0: Define and test the pure transaction builder before replay implementation**

The stable API is exact: `buildGovernanceTransaction({ baseCommit, priorEvents, priorRecords, changes })`. `priorRecords` is a `Map<string, record>`. Every ordered `changes` item contains exactly `recordRef`, `eventKind`, `resultingRecord`, `actorRole`, `actorAssigneeSnapshot`, `operatorEpoch`, `occurredAt`, `evidenceRefs`, `trustRootDeltaSha256`, `authorizationAttestations`, and `genesisAnchor`. Time, nonces and detached signatures are externally supplied. `authorizationAttestations: null` requests the next signing payload; a non-empty array supplies completed detached attestations. Because each event hash binds its attestations and is the next event's `previousEventHash`, signing is intentionally sequential. The builder never signs, reads/writes files, invokes Git, or mutates an input.

Add this complete implementation before the validator:

```js
export function buildGovernanceTransaction({ baseCommit, priorEvents, priorRecords, changes }) {
  if (!/^[0-9a-f]{40}$/.test(baseCommit)) throw new Error("baseCommit must be a full SHA");
  if (chainErrors(priorEvents).length) throw new Error("prior event chain is invalid");
  if (changes.length === 0) throw new Error("governance transaction requires at least one change");
  if (changes.some((change) => change.authorizationAttestations === null) && changes.length !== 1) throw new Error("a signing-request build accepts exactly one change");
  const changeKeys = ["actorAssigneeSnapshot", "actorRole", "authorizationAttestations", "eventKind", "evidenceRefs", "genesisAnchor", "occurredAt", "operatorEpoch", "recordRef", "resultingRecord", "trustRootDeltaSha256"];
  const recordRefs = new Set();
  for (const change of changes) {
    const actual = Object.keys(change).sort((a, b) => a < b ? -1 : a > b ? 1 : 0);
    if (canonicalBytes(actual).compare(canonicalBytes(changeKeys)) !== 0) throw new Error("change has an invalid key set");
    if (recordRefs.has(change.recordRef)) throw new Error(`duplicate change for ${change.recordRef}`);
    recordRefs.add(change.recordRef);
  }
  const resultingRecords = new Map([...priorRecords].map(([id, value]) => [id, structuredClone(value)]));
  const newEvents = [];
  let previousEventHash = priorEvents.at(-1)?.eventHash ?? null;
  let signingRequest = null;
  for (let index = 0; index < changes.length; index += 1) {
    const change = structuredClone(changes[index]);
    const before = resultingRecords.get(change.recordRef) ?? null;
    const after = change.resultingRecord;
    const draft = {
      id: `EVT-${String(priorEvents.length + index + 1).padStart(6, "0")}`,
      eventKind: change.eventKind, recordRef: change.recordRef,
      fromStatus: before?.status ?? null, toStatus: after.status,
      previousRecordSha256: before ? recordSha256(before) : null,
      resultingRecordSha256: recordSha256(after), changeDigest: null,
      trustRootDeltaSha256: change.trustRootDeltaSha256,
      actorRole: change.actorRole, actorAssigneeSnapshot: change.actorAssigneeSnapshot,
      operatorEpoch: change.operatorEpoch, occurredAt: change.occurredAt,
      baseCommit, evidenceRefs: [...change.evidenceRefs], previousEventHash,
      eventAuthorizationPayloadSha256: null,
      authorizationAttestations: change.authorizationAttestations === null ? [] : [...change.authorizationAttestations],
      eventHash: null, genesisAnchor: change.genesisAnchor,
    };
    draft.changeDigest = changeDigest(draft);
    draft.eventAuthorizationPayloadSha256 = eventAuthorizationPayloadSha256(draft);
    if (change.authorizationAttestations === null) {
      signingRequest = Object.freeze({
        eventId: draft.id,
        eventAuthorizationPayloadSha256: draft.eventAuthorizationPayloadSha256,
      });
      break;
    }
    if (change.authorizationAttestations.length === 0) throw new Error(`${draft.id}: finalized event requires attestations`);
    draft.eventHash = eventHash(draft);
    newEvents.push(Object.freeze(draft));
    resultingRecords.set(change.recordRef, structuredClone(after));
    previousEventHash = draft.eventHash;
  }
  return {
    newEvents,
    resultingRecords,
    signingRequest,
  };
}
```

Test deterministic output, unchanged inputs, exact Change keyset, duplicate-record rejection, invalid-prior-chain rejection, and an empty `changes` array rejection. A single null-attestation change returns a request without finalizing an event; null plus any later change throws instead of returning a partial transaction; a non-empty attestation array produces exactly one final event; an empty attestation array fails. For two events, prove the second signing request is unavailable until the first signed event fixes `previousEventHash`, then binds that final hash exactly. Changing time, actor, baseline, record or evidence changes the core digest; adding nonce/signature-bearing attestations changes the final event hash. `newEvents` contains only fully attested appended events.

- [ ] **Step 1: Write failing append-only and replay tests**

Cover: first ID not `EVT-000001`; gap; duplicate; order change; old-event byte change; bad previous hash; decreasing global time; non-increasing per-record time; wrong prior record hash/status; wrong resulting hash; wrong change/core/event digest; two events for one record in a commit; illegal lifecycle pair; illegal amendment field; target record not equal to replay result; decorative/missing evidence; and positive multi-record commit.

- [ ] **Step 2: Implement the deterministic ledger core**

Create `scripts/governance/transition-ledger.mjs` with these complete public functions; use diagnostics from Plan 01:

```js
import { changeDigest, eventAuthorizationPayloadSha256, eventHash, recordSha256 } from "./record-hashes.mjs";
import { canonicalBytes } from "./rfc8785.mjs";
import { amendmentAllowed, recordFamily, transitionAllowed } from "./status-transitions.mjs";

const compare = (a, b) => a < b ? -1 : a > b ? 1 : 0;
const diag = (record, rule, message) => ({ file: "docs/governance/gate-register.md", record, rule, message });
const validatedReplayStates = new WeakMap();

function deepFreezeJson(value) {
  if (value === null || typeof value !== "object") return value;
  for (const child of Object.values(value)) deepFreezeJson(child);
  return Object.freeze(value);
}

function immutableRecordTable(records) {
  return deepFreezeJson(Object.fromEntries([...records.entries()]
    .sort(([left], [right]) => compare(left, right))
    .map(([id, record]) => [id, structuredClone(record)])));
}

function immutableEventStateTable(statesByEventId) {
  return deepFreezeJson(Object.fromEntries([...statesByEventId.entries()]
    .sort(([left], [right]) => compare(left, right))
    .map(([eventId, records]) => [eventId, immutableRecordTable(records)])));
}

export function readValidatedLedgerReplay(result) {
  const state = validatedReplayStates.get(result);
  if (!state) throw new TypeError("validated, module-branded ledger replay required");
  return state;
}

export function immutablePrefixErrors(baseEvents, targetEvents) {
  const errors = [];
  if (targetEvents.length < baseEvents.length) errors.push(diag("LEDGER", "EVT-PREFIX-TRUNCATED", "event prefix was truncated"));
  for (let i = 0; i < Math.min(baseEvents.length, targetEvents.length); i += 1) {
    if (!canonicalBytes(baseEvents[i]).equals(canonicalBytes(targetEvents[i]))) errors.push(diag(targetEvents[i]?.id ?? `INDEX-${i}`, "EVT-PREFIX-MUTATED", "historical event changed"));
  }
  return errors;
}

export function chainErrors(events) {
  const errors = [];
  for (let i = 0; i < events.length; i += 1) {
    const event = events[i];
    const expectedId = `EVT-${String(i + 1).padStart(6, "0")}`;
    if (event.id !== expectedId) errors.push(diag(event.id, "EVT-ID-SEQUENCE", `expected ${expectedId}`));
    const previous = events[i - 1] ?? null;
    if (event.previousEventHash !== (previous?.eventHash ?? null)) errors.push(diag(event.id, "EVT-HASH-LINK", "previousEventHash mismatch"));
    if (previous && event.occurredAt < previous.occurredAt) errors.push(diag(event.id, "EVT-TIME-GLOBAL", "occurredAt decreased"));
    if (event.changeDigest !== changeDigest(event)) errors.push(diag(event.id, "EVT-CHANGE-DIGEST", "changeDigest mismatch"));
    if (event.eventAuthorizationPayloadSha256 !== eventAuthorizationPayloadSha256(event)) errors.push(diag(event.id, "EVT-AUTH-PAYLOAD", "authorization payload digest mismatch"));
    if (event.eventHash !== eventHash(event)) errors.push(diag(event.id, "EVT-EVENT-HASH", "eventHash mismatch"));
  }
  return errors;
}

export function validateTransitionLedger({ baseRecords, targetRecords, baseEvents, targetEvents, baseCommit, expectedProvenanceByRecord = new Map(), isAncestor = () => false, pilotWasEverGreen = false }) {
  const isGenesisImport = baseRecords.size === 0 && baseEvents.length === 0;
  const newEvents = targetEvents.slice(baseEvents.length);
  const transactionSpecialEvent = newEvents.find((event) =>
    ["handover", "recovery", "custodian-rotation"].includes(event.eventKind)) ?? null;
  const transactionSpecialKind = transactionSpecialEvent?.eventKind ?? null;
  const transactionSpecialRoleRef = transactionSpecialEvent?.recordRef ?? null;
  const errors = [...immutablePrefixErrors(baseEvents, targetEvents), ...chainErrors(targetEvents)];
  const replay = new Map([...baseRecords].map(([id, record]) => [id, structuredClone(record)]));
  const preRecordsByEvent = new Map();
  const postRecordsByEvent = new Map();
  const transitionIndex = new Map();
  const lastEventByRecord = new Map();
  for (const event of baseEvents) lastEventByRecord.set(event.recordRef, event);
  const seenNewRecords = new Set();
  for (const event of newEvents) {
    if (seenNewRecords.has(event.recordRef)) errors.push(diag(event.id, "EVT-ONE-PER-RECORD", "multiple new events for one record"));
    seenNewRecords.add(event.recordRef);
    const before = replay.get(event.recordRef) ?? null;
    const after = targetRecords.get(event.recordRef) ?? null;
    preRecordsByEvent.set(event.id, new Map(
      [...replay].map(([id, record]) => [id, structuredClone(record)]),
    ));
    transitionIndex.set(`${event.recordRef}\0${event.toStatus}`, event);
    const previous = lastEventByRecord.get(event.recordRef) ?? null;
    if (!after) { errors.push(diag(event.id, "EVT-MISSING-RESULT", "target record missing")); continue; }
    errors.push(...evidenceBindingErrors(event, replay, isAncestor, { isGenesisImport }));
    errors.push(...actorPolicyErrors(event, before, after, replay,
      { isGenesisImport, pilotWasEverGreen, transactionSpecialKind,
        transactionSpecialRoleRef }));
    if (event.baseCommit !== baseCommit) errors.push(diag(event.id, "EVT-BASE-COMMIT", "event baseCommit does not equal transaction base"));
    if (event.fromStatus !== (before?.status ?? null)) errors.push(diag(event.id, "EVT-FROM-STATUS", "fromStatus does not match replay"));
    if (event.previousRecordSha256 !== (before ? recordSha256(before) : null)) errors.push(diag(event.id, "EVT-PREVIOUS-RECORD", "previous record digest mismatch"));
    if (event.resultingRecordSha256 !== recordSha256(after)) errors.push(diag(event.id, "EVT-RESULTING-RECORD", "resulting record digest mismatch"));
    if (previous && event.occurredAt <= previous.occurredAt) errors.push(diag(event.id, "EVT-TIME-RECORD", "record time is not strictly increasing"));
    const family = recordFamily(event.recordRef);
    const allowed = event.eventKind === "amend"
      ? before !== null && amendmentAllowed(family, before, after, expectedProvenanceByRecord.get(event.recordRef) ?? before.exceptionProvenanceRefs)
      : event.eventKind === "transition" && transitionAllowed(family, event.fromStatus, event.toStatus);
    if (!allowed && !["handover", "recovery", "custodian-rotation"].includes(event.eventKind)) errors.push(diag(event.id, "EVT-STATE-MACHINE", "operation is outside closed lifecycle policy"));
    if (event.toStatus !== after.status) errors.push(diag(event.id, "EVT-TO-STATUS", "toStatus does not match resulting record"));
    replay.set(event.recordRef, structuredClone(after));
    postRecordsByEvent.set(event.id, new Map(
      [...replay].map(([id, record]) => [id, structuredClone(record)]),
    ));
    lastEventByRecord.set(event.recordRef, event);
  }
  for (const [id, target] of targetRecords) {
    if (!replay.has(id) || !canonicalBytes(replay.get(id)).equals(canonicalBytes(target))) errors.push(diag(id, "EVT-UNEXPLAINED-RECORD", "target record is not explained by one new event"));
  }
  for (const id of replay.keys()) if (!targetRecords.has(id)) errors.push(diag(id, "EVT-UNEXPLAINED-DELETION", "base record disappeared without a valid successor event"));
  errors.push(...specialRoleBundleErrors(newEvents, baseRecords, targetRecords, pilotWasEverGreen));
  const lifecycleContext = Object.freeze({
    transitionFor: (recordRef, toStatus) => transitionIndex.get(`${recordRef}\0${toStatus}`) ?? null,
    recordBeforeEvent: (eventId, recordId) => structuredClone(
      preRecordsByEvent.get(eventId)?.get(recordId) ?? null,
    ),
    roleBeforeEvent: (eventId, roleId) => {
      if (!roleId.startsWith("ROLE-")) throw new TypeError(`not a ROLE ID: ${roleId}`);
      return structuredClone(preRecordsByEvent.get(eventId)?.get(roleId) ?? null);
    },
  });
  const orderedErrors = Object.freeze(errors.sort((a, b) =>
    compare(`${a.record}\0${a.rule}`, `${b.record}\0${b.rule}`)));
  const result = Object.freeze({ replay, lifecycleContext, errors: orderedErrors });
  if (orderedErrors.length === 0) {
    validatedReplayStates.set(result, Object.freeze({
      recordPrestateByEventId: immutableEventStateTable(preRecordsByEvent),
      recordPoststateByEventId: immutableEventStateTable(postRecordsByEvent),
    }));
  }
  return result;
}
```

`validateTransitionLedger(...)` is the stable validation export. Its
`lifecycleContext` addresses the concrete new EVT and the immutable full record
replay-state immediately before it. Plan 04 uses `roleBeforeEvent` for actor
snapshots and `recordBeforeEvent` for historical qualification EVID; neither
baseline nor epoch is a proxy for lifecycle position. Returned records are
structured clones, so callers cannot mutate replay history. Before Plan 04,
provenance must remain unchanged. Plan 04 passes its independently derived
exact `expectedProvenanceByRecord`; a claimed EXC prefix is never accepted. The
CLI never gains a mutating transaction command.

The successful-replay capability is separate from the ordinary diagnostic
result. `readValidatedLedgerReplay(result)` accepts only the exact result
object branded in the module-private `WeakMap` after a zero-error full replay;
it returns only deep-frozen, code-unit-ordered plain objects named
`recordPrestateByEventId` and `recordPoststateByEventId`. Add mutation and
forgery tests for a raw `Map`, a structured clone, a partial/error replay, and
a copied result. Add a source-boundary test over `scripts/**/*.mjs`: only
`bootstrap-validator-internal.mjs`, `bootstrap-validator.test.mjs`, and
`transition-ledger.test.mjs` may import `readValidatedLedgerReplay`. This is
the Plan-05 composition capability; no raw Map or caller boolean may stand in
for it.

- [ ] **Step 3: Add evidence-binding and special-bundle validators**

Add these concrete validators to the same file:

```js
export function evidenceBindingErrors(event, priorRecords, isAncestor = () => false,
  { isGenesisImport = false } = {}) {
  const exactGenesisEmptyEvidence = isGenesisImport && event.genesisAnchor !== null
    && event.evidenceRefs.length === 0 && (
      (event.id === "EVT-000001" && event.recordRef === "ROLE-OPERATOR"
        && event.fromStatus === null && event.toStatus === "assigned")
      || (event.id === "EVT-000002" && event.recordRef === "ROLE-ORCHESTRATOR"
        && event.fromStatus === null && event.toStatus === "assigned")
      || (event.id === "EVT-000003" && event.recordRef === "EVID-G0-DESIGN-COMMIT"
        && event.fromStatus === null && event.toStatus === "captured")
    );
  if (exactGenesisEmptyEvidence) return [];
  if (event.recordRef.startsWith("EVID-") && ["captured", "verified", "invalidated", "superseded"].includes(event.toStatus)) {
    return canonicalBytes(event.evidenceRefs).equals(canonicalBytes([event.recordRef])) ? [] : [diag(event.id, "EVT-EVID-SELF", "EVID lifecycle event must reference exactly itself")];
  }
  if (event.evidenceRefs.length === 0) return [diag(event.id, "EVT-EVIDENCE-MISSING", "transition requires prior evidence")];
  const scope = `governance-change:${event.recordRef}:${event.eventKind}:${event.previousRecordSha256 ?? "null"}:${event.resultingRecordSha256}`;
  return event.evidenceRefs.flatMap((id) => {
    const evidence = priorRecords.get(id);
    if (!evidence || !["captured", "verified"].includes(evidence.status)) return [diag(event.id, "EVT-EVIDENCE-STATE", `ineligible ${id}`)];
    if (evidence.scope !== scope || !evidence.governanceChangeDigests.includes(event.changeDigest)) return [diag(event.id, "EVT-EVIDENCE-SCOPE", `unbound ${id}`)];
    if (!(evidence.baselineCommit === event.baseCommit || isAncestor(evidence.baselineCommit, event.baseCommit))) return [diag(event.id, "EVT-EVIDENCE-BASELINE", `stale ${id}`)];
    return [];
  });
}

const sortedPurposes = (event) => event.authorizationAttestations
  .map((item) => item.attestationPurpose).sort(compare);
const purposeErrors = (event, expected) => canonicalBytes(sortedPurposes(event))
  .equals(canonicalBytes([...expected].sort(compare)))
  ? [] : [diag(event.id, "EVT-ATTESTATION-THRESHOLD",
    `expected exactly ${[...expected].sort(compare).join(",")}`)];

export function actorPolicyErrors(event, before, after, priorRecords,
  { isGenesisImport = false, pilotWasEverGreen = false,
    transactionSpecialKind = null, transactionSpecialRoleRef = null } = {}) {
  const errors = [];
  if (event.id === "EVT-000001" && event.genesisAnchor !== null) {
    if (event.recordRef !== "ROLE-OPERATOR" || event.actorRole !== "ROLE-OPERATOR" || event.actorAssigneeSnapshot !== "redshift-three67") errors.push(diag(event.id, "EVT-GENESIS-ACTOR", "invalid externally anchored first actor"));
    errors.push(...purposeErrors(event, ["actor", "recovery-root"]));
    return errors;
  }
  const actor = priorRecords.get(event.actorRole);
  if (!actor || actor.status !== "assigned" || actor.assigneeRef !== event.actorAssigneeSnapshot) errors.push(diag(event.id, "EVT-ACTOR-SNAPSHOT", "actor is not the replayed assigned role"));
  const family = recordFamily(event.recordRef);
  const custodians = new Set(["ROLE-RECOVERY-CUSTODIAN-A", "ROLE-RECOVERY-CUSTODIAN-B"]);
  let allowed = [];
  let expectedPurposes = ["actor"];
  if (family === "ROLE") {
    if (event.eventKind === "handover") {
      allowed = ["ROLE-OPERATOR"];
      expectedPurposes = ["actor", "recovery-root", "incoming-operator"];
    } else if (event.eventKind === "recovery") {
      allowed = ["ROLE-RECOVERY-ROOT"];
      expectedPurposes = ["recovery-root", "incoming-operator",
        ...(pilotWasEverGreen ? ["custodian-a", "custodian-b"] : [])];
    } else if (event.eventKind === "custodian-rotation") {
      allowed = ["ROLE-RECOVERY-ROOT"];
      expectedPurposes = event.recordRef.endsWith("-A")
        ? ["recovery-root", "custodian-b", "incoming-custodian-a"]
        : ["recovery-root", "custodian-a", "incoming-custodian-b"];
    } else if (before === null && after.status === "unassigned") {
      allowed = ["ROLE-ORCHESTRATOR", "ROLE-OPERATOR"];
    } else if (event.recordRef === "ROLE-RECOVERY-ROOT"
      && before === null && after.status === "assigned") {
      allowed = isGenesisImport ? ["ROLE-OPERATOR"] : [];
      expectedPurposes = ["actor", "recovery-root"];
    } else if (custodians.has(event.recordRef) && before?.status === "unassigned"
      && after.status === "assigned" && !pilotWasEverGreen) {
      allowed = ["ROLE-OPERATOR"];
      expectedPurposes = ["actor", "recovery-root",
        event.recordRef.endsWith("-A") ? "incoming-custodian-a" : "incoming-custodian-b"];
    } else {
      allowed = ["ROLE-OPERATOR"];
      if (event.recordRef === "ROLE-OPERATOR" || event.recordRef === "ROLE-RECOVERY-ROOT"
        || (pilotWasEverGreen && custodians.has(event.recordRef))) allowed = [];
    }
  } else if (family === "GATE") {
    if (after.status === "green") allowed = ["ROLE-OPERATOR"];
    else if (transactionSpecialKind === "handover") {
      allowed = ["ROLE-OPERATOR"];
      expectedPurposes = ["actor", "recovery-root"];
    } else if (transactionSpecialKind === "recovery") {
      allowed = ["ROLE-RECOVERY-ROOT"];
      expectedPurposes = ["recovery-root",
        ...(pilotWasEverGreen ? ["custodian-a", "custodian-b"] : [])];
    } else if (transactionSpecialKind === "custodian-rotation") {
      allowed = ["ROLE-RECOVERY-ROOT"];
      expectedPurposes = ["recovery-root",
        transactionSpecialRoleRef?.endsWith("-A") ? "custodian-b" : "custodian-a"];
    } else allowed = ["ROLE-OPERATOR", ...(after.verifierRoleRefs ?? [])];
  } else if (family === "REV") {
    allowed = ["approved", "changes-required"].includes(after.status)
      ? [after.reviewerRole] : ["ROLE-ORCHESTRATOR", "ROLE-OPERATOR"];
    if (after.approvedByRole && after.approvedByRole !== event.actorRole) expectedPurposes.push("approver");
  } else if (family === "EVID") {
    if (after.status === "captured") allowed = [after.producerRole];
    else if (["verified", "invalidated"].includes(after.status)) allowed = [after.verifiedByRole];
    else if (after.status === "superseded") allowed = ["ROLE-ORCHESTRATOR", before?.verifiedByRole].filter(Boolean);
    else allowed = [after.producerRole, "ROLE-ORCHESTRATOR", "ROLE-OPERATOR"].filter(Boolean);
    if (after.status === "captured" && after.evidenceType === "reasoning-approval") expectedPurposes.push("approver");
  } else if (family === "EXC") {
    allowed = ["approved", "revoked", "expired"].includes(after.status)
      ? ["ROLE-OPERATOR"] : ["ROLE-ORCHESTRATOR", "ROLE-OPERATOR"];
  } else if (family === "RISK") {
    allowed = after.status === "accepted" ? ["ROLE-OPERATOR"]
      : [after.ownerRole, "ROLE-ORCHESTRATOR", "ROLE-OPERATOR"].filter(Boolean);
  } else if (["REQ", "CTRL", "COMP", "PROFILE"].includes(family)) {
    allowed = ["approved", "active", "verified"].includes(after.status)
      ? ["ROLE-OPERATOR"] : [after.ownerRole, "ROLE-ORCHESTRATOR", "ROLE-OPERATOR"].filter(Boolean);
  } else if (["DATA", "FLOW"].includes(family)) {
    allowed = after.status === "active" ? ["ROLE-OPERATOR"]
      : [after.ownerRole, "ROLE-ORCHESTRATOR", "ROLE-OPERATOR"].filter(Boolean);
  }
  if (!allowed.includes(event.actorRole)) errors.push(diag(event.id, "EVT-ACTOR-MATRIX", "actor is outside the closed matrix"));
  errors.push(...purposeErrors(event, expectedPurposes));
  return errors;
}

export function specialRoleBundleErrors(newEvents, priorRecords, targetRecords, pilotWasEverGreen) {
  const special = newEvents.filter((event) => ["handover", "recovery", "custodian-rotation"].includes(event.eventKind));
  if (special.length === 0) return [];
  if (special.length !== 1 || special[0] !== newEvents.at(-1)) return [diag("TRANSACTION", "EVT-SPECIAL-ORDER", "exactly one special ROLE event must end the transaction")];
  const roleEvent = special[0];
  const permittedRefs = new Set([roleEvent.recordRef,
    ...[...priorRecords.values()].filter((record) => record.id?.startsWith("GATE-")
      && record.status === "green").map((record) => record.id)]);
  if (newEvents.some((event) => !permittedRefs.has(event.recordRef))) {
    return [diag("TRANSACTION", "EVT-SPECIAL-EXTRA-RECORD",
      "special transaction may contain only all green-gate resets and its final ROLE event")];
  }
  const greenGates = [...priorRecords.values()].filter((record) => record.id?.startsWith("GATE-") && record.status === "green").map((record) => record.id).sort(compare);
  const resets = newEvents.filter((event) => event.recordRef.startsWith("GATE-") && event.fromStatus === "green" && event.toStatus === "red").map((event) => event.recordRef).sort(compare);
  const errors = [];
  if (!canonicalBytes(greenGates).equals(canonicalBytes(resets))) errors.push(diag(roleEvent.id, "EVT-GATE-RESET-SET", "special transition must reset every green gate first"));
  const priorOperator = priorRecords.get("ROLE-OPERATOR");
  const priorRole = priorRecords.get(roleEvent.recordRef);
  const nextRole = targetRecords.get(roleEvent.recordRef);
  if (["handover", "recovery"].includes(roleEvent.eventKind) && roleEvent.operatorEpoch !== priorOperator.operatorEpoch + 1) errors.push(diag(roleEvent.id, "EVT-OPERATOR-EPOCH", "operator epoch must increase exactly once"));
  if (["handover", "recovery"].includes(roleEvent.eventKind)
    && (roleEvent.recordRef !== "ROLE-OPERATOR" || roleEvent.fromStatus !== "assigned"
      || roleEvent.toStatus !== "assigned")) errors.push(diag(roleEvent.id, "EVT-OPERATOR-SPECIAL-SHAPE", "handover/recovery applies only to assigned ROLE-OPERATOR"));
  if (roleEvent.eventKind === "custodian-rotation"
    && (!["ROLE-RECOVERY-CUSTODIAN-A", "ROLE-RECOVERY-CUSTODIAN-B"].includes(roleEvent.recordRef)
      || roleEvent.fromStatus !== "assigned" || roleEvent.toStatus !== "assigned")) errors.push(diag(roleEvent.id, "EVT-CUSTODIAN-ROTATION-SHAPE", "rotation applies to exactly one assigned Custodian"));
  if (nextRole && nextRole.assigneeRef === priorRole?.assigneeRef) errors.push(diag(roleEvent.id, "EVT-INCOMING-IDENTITY", "incoming identity must differ"));
  return errors;
}
```

The calls shown in `validateTransitionLedger` run before/after replay in the documented order. If any returns an error, do not use the replay output as an approved state. Tests exhaust actor matrix, all-green reset, epoch increment, pilot threshold derived from historical base events, distinct identities, attestation purpose sets, and operator/root lockout.

The Genesis empty-evidence exemption is exactly `EVT-000001..EVT-000003` as
shown in `exactGenesisEmptyEvidence`; there is no generic initial-status or
fourth record-specific exemption. The normalized EVID self-lifecycle is the
only other non-prior mechanism and cannot authorize a different record. Add a
cross-product regression proving empty evidence fails with
`EVT-EVIDENCE-MISSING` for every non-EVID transition to `proposed`,
`unassigned`, `red`, `catalogued`, `open`, `expected`, or `requested`, plus a
specific regression in which `EVT-000004` assigns `ROLE-RECOVERY-ROOT` with
empty evidence. The Plan-12 initial-manifest sequence must therefore create a
dedicated `null→captured` self-EVID before every remaining seed change and
order each consuming seed after it. For the Recovery Root it must:

1. finalize exactly `EVT-000001..EVT-000003` under the empty-evidence anchor;
2. create and move
   `EVID-G0-RECOVERY-ROOT-ASSIGNMENT-AUTH` to `captured` through its normal
   EVID self-lifecycle, with exact scope
   `governance-change:ROLE-RECOVERY-ROOT:transition:null:<resultingRecordSha256>`
   and the pending ROLE event's exact `changeDigest`;
3. only then finalize the `ROLE-RECOVERY-ROOT null→assigned` event,
   referencing exactly that already-captured EVID.

Test that positive ordering and mutations for a missing EVID, `expected`
rather than `captured`, wrong scope, wrong change digest, wrong baseline, and a
ROLE event ordered before its EVID. The normal EVID self-lifecycle rule is the
only non-Genesis mechanism for authorizing this change; no record-ID-specific
bypass is permitted.

- [ ] **Step 4: Run ledger tests**

Run `node --test scripts/governance/transition-ledger.test.mjs`.

Expected: all negative mutations fail with stable `EVT-*` rules; the positive multi-record transaction replays exactly to target.

- [ ] **Step 5: Commit the replay engine**

```powershell
git add scripts/governance/transition-ledger.mjs scripts/governance/transition-ledger.test.mjs
git commit -m "feat: replay append-only governance transitions"
```

### Task 6: Reject non-governance changes in a governance-event commit

**Files:**

- Modify: `scripts/governance/transition-ledger.mjs`
- Modify: `scripts/governance/transition-ledger.test.mjs`

- [ ] **Step 1: Add path/mode/blob mutation tests**

Test an event commit that also changes each forbidden class: `src/`, validator, schema, workflow, directive, test, package config, source docs, and every already-fixed `docs/governance/bootstrap/*.json`. Test allowed register, trust-root, detached attestation, manifest, and evidence paths only when their actual target bytes validate and have exactly one explanation in the new transaction. Add one separately branded exact Genesis-import replay that permits only the two previously absent fixed bootstrap JSON files as `100644` additions; an ordinary replay, caller boolean, copied result, later modification, extra bootstrap file, or delete/rename still fails. Reject deletion, rename, symlink, submodule, every executability/mode change, an orphan artifact, a false EVID hash, invalid JSON/schema, an unreferenced attestation, a manifest not bijective with one EVID, and every artifact-only commit with no new EVT. Also prove that a base record cannot change or disappear without exactly one matching new event.

- [ ] **Step 2: Add the exact closed path predicate**

```js
const GOVERNANCE_EVENT_PATH = /^(?:docs\/governance\/(?:traceability-register\.md|risk-register\.md|data-processing-inventory\.md|gate-register\.md|trust-roots\.json|attestations\/[A-Za-z0-9._-]+\.json|manifests\/[A-Za-z0-9._-]+\.json|evidence\/[A-Za-z0-9._/-]+))$/;
const GENESIS_BOOTSTRAP_PATHS = new Set([
  "docs/governance/bootstrap/final-design-approval.json",
  "docs/governance/bootstrap/pre-ledger-trust-bundle.json",
]);

export function governanceOnlyErrors(changedEntries, validatedLedgerResult,
  repositoryView) {
  const replay = validatedReplayStates.get(validatedLedgerResult);
  if (!replay) return [diag("COMMIT", "EVT-UNBRANDED-REPLAY", "validated ledger replay capability is required")];
  if (!replay.hasNewEvents && changedEntries.length !== 0) return [diag("COMMIT",
    "EVT-ARTIFACT-WITHOUT-EVENT", "Governance artifact changes require a new replayed Event")];
  const errors = changedEntries.flatMap((entry) => {
    if (GENESIS_BOOTSTRAP_PATHS.has(entry.path)) {
      if (replay.genesisImportVerified === true && entry.changeKind === "A"
        && entry.oldMode === "000000" && entry.newMode === "100644") return [];
      return [diag("COMMIT", "EVT-BOOTSTRAP-PATH-FIXED",
        `bootstrap path is add-only in the exact branded Genesis import: ${entry.path}`)];
    }
    if (!GOVERNANCE_EVENT_PATH.test(entry.path)) return [diag("COMMIT", "EVT-NON-GOVERNANCE-DIFF", `forbidden event-commit path: ${entry.path}`)];
    if (!["A", "M"].includes(entry.changeKind)) return [diag("COMMIT", "EVT-DESTRUCTIVE-PATH-CHANGE", `delete/copy/rename is forbidden: ${entry.path}`)];
    if (!(["000000", "100644"].includes(entry.oldMode) && entry.newMode === "100644")) return [diag("COMMIT", "EVT-UNSAFE-MODE", `only add/modify 100644 is allowed: ${entry.path}`)];
    if (/^docs\/governance\/(?:attestations|manifests|evidence)\//.test(entry.path)
      && entry.changeKind !== "A") return [diag("COMMIT", "EVT-IMMUTABLE-ARTIFACT",
        `attestation/manifest/evidence artifacts are add-only: ${entry.path}`)];
    return [];
  });
  if (errors.length) return errors;
  return validateGovernanceArtifactChanges({ changedEntries, replay,
    repositoryView });
}
```

`validateGovernanceArtifactChanges` is module-private and receives only the
concrete Plan-03 repository view used for the same adjacent target; it accepts
no callback and rereads each `newOid` as bytes. A fixed path-dispatch table does
the following: four registers must be the byte source already parsed into the
branded replay; `trust-roots.json` must pass its closed schema and its exact
delta must equal the new EVT delta; each detached attestation must be canonical
duplicate-key-free JSON, pass `event-attestation`, and be referenced exactly
once by one new EVT; each subject/input manifest must pass its fixed schema,
have exactly one target EVID path/hash reference, and hash the actual bytes;
each other evidence file must have exactly one non-`expected` target EVID whose
`artifactPathOrUri` equals the path and whose `sha256` equals the actual bytes;
and the two Genesis bootstrap files must pass their fixed schemas and the
separately branded Genesis pair verification. Every non-register changed path
must be consumed exactly once and every file path introduced by the new
transaction must appear exactly once in `changedEntries`. Missing, extra,
duplicated, wrong-schema, noncanonical, unreadable, OID-mismatched, or orphan
content is fatal. This structural byte/bijection gate complements Plan 04's
current-target EVID byte brand; it never makes a Gate effective.

`validateTransitionLedger` stores `hasNewEvents` and
`genesisImportVerified` in the same module-private WeakMap entry as the replay
states. The latter is derived, never passed: base records/Events are empty;
the target passes the exact Genesis anchor/order/exemption rules; every target
record has its one import Event; and `baseCommit` is the common full `I`.
This structural path capability does not verify bootstrap signatures and is
not Gate authority; Plans 05/11/12 still perform those independent checks.

- [ ] **Step 3: Run focused tests and commit**

Run `node --test --test-name-pattern="governance-only" scripts/governance/transition-ledger.test.mjs`.

Expected: all allowed cases pass; every forbidden companion change fails.

```powershell
git add scripts/governance/transition-ledger.mjs scripts/governance/transition-ledger.test.mjs
git commit -m "feat: isolate governance event commits"
```

### Task 7: Compose explicit base/head replay in the CLI

**Files:**

- Create: `scripts/governance/governance-mode-test-core.mjs`
- Modify: `scripts/governance-contract.mjs`
- Modify: `scripts/governance-contract.test.mjs`

- [ ] **Step 1: Add failing argument and non-writing tests**

Test the exact mode table below. `--pre-genesis` is the exclusive real-repository
authority-boundary check; it must deterministically reach validation rather
than fail argument parsing even though the four registers do not yet exist.
Explicit Working-Tree and commit preflight modes require `--external-pins` plus
`--local-preflight`; they return semantic exit 0 with `LOCAL-PREFLIGHT-ONLY`
but can never be gate-effective. Production replay
requires `--base`, `--head`, `--external-pins`, and `--remote-bundle`, and
requires one accepted receipt per adjacent commit. Reject a missing value,
duplicate flag, unknown flag, only one of base/head, head plus working-tree,
local-preflight plus remote-bundle, production working-tree, invalid ref, and a
base outside the Head's First-Parent chain.

Use these table tests verbatim:

```js
const LOCAL_PINS = "fixtures/external-pins.json";
const REMOTE = "fixtures/remote-bundle.json";
const parseCases = [
  [["--pre-genesis"], "pre-genesis-working-tree"],
  [["--base", "I", "--working-tree", "--external-pins", LOCAL_PINS, "--local-preflight"], "local-working-tree"],
  [["--base", "I", "--head", "G", "--external-pins", LOCAL_PINS, "--local-preflight"], "local-commit-range"],
  [["--base", "G", "--head", "C", "--external-pins", LOCAL_PINS, "--remote-bundle", REMOTE], "production-commit-range"],
];
for (const [argv, mode] of parseCases) {
  test(`argument mode ${mode}`, () => assert.equal(parseGovernanceArgs(argv).mode, mode));
}

for (const argv of [
  [],
  ["--pre-genesis", "--base", "I"],
  ["--pre-genesis", "--local-preflight"],
  ["--base", "I"],
  ["--base", "I", "--working-tree"],
  ["--base", "I", "--head", "G", "--external-pins", LOCAL_PINS],
  ["--base", "I", "--head", "G", "--working-tree", "--external-pins", LOCAL_PINS, "--local-preflight"],
  ["--base", "I", "--head", "G", "--external-pins", LOCAL_PINS, "--local-preflight", "--remote-bundle", REMOTE],
  ["--base", "I", "--base", "G", "--working-tree", "--external-pins", LOCAL_PINS, "--local-preflight"],
  ["--unknown"],
]) {
  test(`reject closed argument set ${JSON.stringify(argv)}`, () => {
    assert.throws(() => parseGovernanceArgs(argv), /governance argument|requires|exactly one|cannot/);
  });
}

test("explicit pre-Genesis mode is deterministic and bypasses normal registers", async () => {
  let normalRegisterPathCalled = false;
  const result = await validateGovernanceModeForTest(
    parseGovernanceArgs(["--pre-genesis"]),
    {
      validatePreGenesis: async ({ base }) => ({
        base, errors: [], diagnostics: [{ rule: "PRE-GENESIS-REGISTERS-ABSENT" }],
      }),
      validateWorkingTree: async () => {
        normalRegisterPathCalled = true;
        throw new Error("normal register parser must not run pre-Genesis");
      },
    },
  );
  assert.equal(normalRegisterPathCalled, false);
  assert.deepEqual(result, {
    base: "HEAD", errors: [],
    diagnostics: [{ rule: "PRE-GENESIS-REGISTERS-ABSENT" }],
    authorityRequired: ["GENESIS"], gateEffective: false,
    testOnly: true, status: "AUTHORITY-RED/PRE-GENESIS",
  });
});

test("injected production adapter cannot mint a Gate result", async () => {
  const forged = await validateGovernanceModeForTest(
    parseGovernanceArgs(["--base", "G", "--head", "C", "--external-pins",
      LOCAL_PINS, "--remote-bundle", REMOTE]),
    {
      firstParentRange: () => ["C"],
      validateAdjacentCommit: async () => [],
      verifyAcceptanceReceipt: async () => ({ gateEffective: true,
        authorityContext: { profile: "gate-evaluation" } }),
    },
  );
  assert.equal(forged.testOnly, true);
  assert.equal(forged.gateEffective, false);
  assert.equal(forged.status, "TEST-ONLY-FAILED");

  const testReceipt = makeTestAcceptanceReceipt();
  const result = await validateGovernanceModeForTest(
    parseGovernanceArgs(["--base", "G", "--head", "C", "--external-pins",
      LOCAL_PINS, "--remote-bundle", REMOTE]),
    {
      firstParentRange: () => ["C"],
      validateAdjacentCommit: async () => [],
      verifyAcceptanceReceipt: async () => testReceipt,
    },
  );
  assert.deepEqual({ testOnly: result.testOnly, gateEffective: result.gateEffective,
    status: result.status, authorityRequired: result.authorityRequired }, {
    testOnly: true, gateEffective: false, status: "TEST-ONLY-NON-GATE",
    authorityRequired: ["production-authority-context"],
  });
});

test("production facade has no adapter injection parameter", async () => {
  assert.equal(validateGovernanceMode.length, 1);
  const source = await readFile(new URL("./governance-contract.mjs", import.meta.url), "utf8");
  assert.doesNotMatch(source, /validateGovernanceMode\s*\([^)]*,/);
  assert.doesNotMatch(source, /receipt\?\.gateEffective|adapters\s*[),]/);
});
```

Import `validateGovernanceModeForTest` only from
`governance-mode-test-core.mjs`; it is never re-exported by
`governance-contract.mjs`. Execution tests add a two-commit range that changes a Fach-/source file and then
reverts it, and another that rewrites and restores ledger history; both fail at
the offending intermediate commit. A missing/false receipt fails only in
`production-commit-range`; the same structurally valid range in
`local-commit-range` succeeds exclusively as `LOCAL-PREFLIGHT-ONLY`.

- [ ] **Step 2: Add exact argument parsing**

```js
const VALUE_FLAGS = new Map([
  ["--base", "base"],
  ["--head", "head"],
  ["--external-pins", "externalPins"],
  ["--remote-bundle", "remoteBundle"],
]);
const BOOLEAN_FLAGS = new Map([
  ["--pre-genesis", "preGenesis"],
  ["--working-tree", "workingTree"],
  ["--local-preflight", "localPreflight"],
]);

export function parseGovernanceArgs(argv) {
  const parsed = {
    base: null, head: null, externalPins: null, remoteBundle: null,
    preGenesis: false, workingTree: false, localPreflight: false,
  };
  const seen = new Set();
  for (let i = 0; i < argv.length; i += 1) {
    const key = argv[i];
    if (seen.has(key)) throw new Error(`duplicate governance argument: ${key}`);
    seen.add(key);
    if (BOOLEAN_FLAGS.has(key)) {
      parsed[BOOLEAN_FLAGS.get(key)] = true;
      continue;
    }
    const field = VALUE_FLAGS.get(key);
    if (!field) throw new Error(`unknown governance argument: ${key}`);
    const value = argv[++i];
    if (!value || value.startsWith("--")) throw new Error(`${key} requires one value`);
    parsed[field] = value;
  }

  if (parsed.preGenesis) {
    if (argv.length !== 1) throw new Error("--pre-genesis cannot be combined with other governance arguments");
    return Object.freeze({ mode: "pre-genesis-working-tree", base: "HEAD",
      head: null, externalPins: null, remoteBundle: null,
      localPreflight: false });
  }
  if (!parsed.base || !parsed.externalPins) {
    throw new Error("explicit mode requires --base and --external-pins");
  }
  if (parsed.workingTree) {
    if (parsed.head || parsed.remoteBundle || !parsed.localPreflight) {
      throw new Error("working-tree mode requires --local-preflight and cannot use --head or --remote-bundle");
    }
    return Object.freeze({ mode: "local-working-tree", base: parsed.base,
      head: null, externalPins: parsed.externalPins, remoteBundle: null,
      localPreflight: true });
  }
  if (!parsed.head) throw new Error("commit-range mode requires --head");
  if (parsed.localPreflight === Boolean(parsed.remoteBundle)) {
    throw new Error("commit-range mode requires exactly one of --local-preflight or --remote-bundle");
  }
  return Object.freeze({
    mode: parsed.localPreflight ? "local-commit-range" : "production-commit-range",
    base: parsed.base, head: parsed.head, externalPins: parsed.externalPins,
    remoteBundle: parsed.remoteBundle, localPreflight: parsed.localPreflight,
  });
}
```

- [ ] **Step 3: Load base/target registers and call replay**

Use `createRepositoryView` to obtain `firstParentRange(base, head)` and validate
every adjacent parent/commit pair separately in oldest-first order. The
adapter's adjacency proof is mandatory; generic ancestry is insufficient. For
each commit reject a merge commit whose diff touches a register, parse
base/target register bytes, collect records, call `validateTransitionLedger`,
and call `governanceOnlyErrors(changedEntries, validatedLedgerResult,
repositoryView)` with the exact zero-error replay result and the same
target-bound repository view from that adjacent pair. Never pass a boolean,
caller artifact bytes, or a second view.

Put the injectable harness only in
`scripts/governance/governance-mode-test-core.mjs`. It is test support, is not
imported or re-exported by the production CLI, and is permanently incapable of
minting authority:

```js
const acceptedTestReceipts = new WeakSet();
export function makeTestAcceptanceReceipt() {
  const receipt = Object.freeze({ testOnly: true });
  acceptedTestReceipts.add(receipt);
  return receipt;
}

const freezeTestResult = (value) => Object.freeze({ ...value,
  testOnly: true, gateEffective: false });

export async function validateGovernanceModeForTest(options, adapters) {
  if (options.mode === "pre-genesis-working-tree") {
    const semantic = await adapters.validatePreGenesis({ base: "HEAD" });
    return freezeTestResult({ ...semantic, authorityRequired: ["GENESIS"],
      status: "AUTHORITY-RED/PRE-GENESIS" });
  }
  if (options.mode === "local-working-tree") {
    const semantic = await adapters.validateWorkingTree({
      base: options.base, externalPinsPath: options.externalPins,
    });
    return freezeTestResult({ ...semantic,
      authorityRequired: semantic.errors.length ? [] : ["REMOTE-ACCEPTANCE"],
      status: semantic.errors.length ? "TEST-ONLY-FAILED" : "LOCAL-PREFLIGHT-ONLY" });
  }

  const commits = adapters.firstParentRange(options.base, options.head);
  let parent = options.base;
  const errors = [];
  for (const commit of commits) {
    errors.push(...await adapters.validateAdjacentCommit({ parent, commit,
      externalPinsPath: options.externalPins }));
    if (options.mode === "production-commit-range") {
      const receipt = await adapters.verifyAcceptanceReceipt({
        parent, commit, remoteBundlePath: options.remoteBundle,
        externalPinsPath: options.externalPins,
      });
      if (!acceptedTestReceipts.has(receipt)) errors.push({
        rule: "AUTHORITY-RED/RECEIPT", record: commit,
        message: "adjacent commit lacks accepted test receipt",
      });
    }
    parent = commit;
  }
  return freezeTestResult({ errors,
    authorityRequired: options.mode === "local-commit-range"
      ? ["REMOTE-ACCEPTANCE"] : ["production-authority-context"],
    status: errors.length ? "TEST-ONLY-FAILED"
      : options.mode === "local-commit-range"
        ? "LOCAL-PREFLIGHT-ONLY" : "TEST-ONLY-NON-GATE",
  });
}
```

Implement `validatePreGenesisRepository`, `validateLocalWorkingTree`, and
`validateLocalCommitRange` as module-private concrete functions in
`scripts/governance-contract.mjs`; they close over `createRepositoryView`, the
Plan-02 parser/schema/reference exports, and the Plan-03 replay functions.
They accept only the frozen parsed options, never callbacks.
`validatePreGenesisRepository` returns exactly frozen
`{base,errors,diagnostics}`. Both local validators return exactly frozen
`{errors,headCommit,headTreeOid,externalPinsSha256}`; the commit-range
`headCommit` and `headTreeOid` are read from the target Git object, while the
Working-Tree result uses the resolved full `HEAD` and `headTreeOid:null` because
an uncommitted tree is deliberately not an authoritative Git Tree. `externalPinsSha256` is
the SHA-256 of the fatal-I-JSON/RFC-8785 canonical pin file named by the parsed
option. No caller field supplies any of those three outputs. At the Plan-03
boundary the production branch is explicitly authority-pending:

```js
async function productionAuthorityPending(options) {
  const semantic = await validateLocalCommitRange(options);
  return Object.freeze({ ...semantic,
    authorityRequired: ["production-authority-context"],
    gateEffective: false,
    status: semantic.errors.length ? "FAILED" : "AUTHORITY-RED/PRODUCTION-PENDING",
  });
}

export async function validateGovernanceMode(options) {
  if (options.mode === "pre-genesis-working-tree") {
    const semantic = await validatePreGenesisRepository({ base: "HEAD" });
    return Object.freeze({ ...semantic, authorityRequired: ["GENESIS"],
      gateEffective: false, status: "AUTHORITY-RED/PRE-GENESIS" });
  }
  if (options.mode === "local-working-tree") {
    const semantic = await validateLocalWorkingTree(options);
    return Object.freeze({ ...semantic,
      authorityRequired: semantic.errors.length ? [] : ["REMOTE-ACCEPTANCE"],
      gateEffective: false,
      status: semantic.errors.length ? "LOCAL-PREFLIGHT-FAILED" : "LOCAL-PREFLIGHT-ONLY" });
  }
  if (options.mode === "local-commit-range") {
    const semantic = await validateLocalCommitRange(options);
    return Object.freeze({ ...semantic,
      authorityRequired: semantic.errors.length ? [] : ["REMOTE-ACCEPTANCE"],
      gateEffective: false,
      status: semantic.errors.length ? "LOCAL-PREFLIGHT-FAILED" : "LOCAL-PREFLIGHT-ONLY" });
  }
  return productionAuthorityPending(options);
}
```

Plan 11 replaces only `productionAuthorityPending` with this exact closed
composition. `loadClosedRemoteAuthorityAggregate` parses the `--remote-bundle`
path as fatal UTF-8/duplicate-key-free I-JSON and rejects any key set other
than `profile`, `remoteAuthorityInputs`, `acceptanceReceiptPrefix`,
`initialBranchPolicyPin`, `productionArtifacts`, and `operatorAcceptance`; it never deserializes an
authority context or verifier result:

```js
import { readProductionAuthorityContext,
  requireProductionAuthorityResult, verifyProductionAuthorityContext }
  from "./governance/production-authority-context.mjs";

async function productionAuthorityPending(options) {
  const structural = await validateProductionCommitRangeStructure(options);
  if (structural.errors.length) return Object.freeze({ ...structural,
    authorityRequired: [], gateEffective: false, status: "FAILED" });

  const rawArtifacts = loadClosedRemoteAuthorityAggregate(options.remoteBundle);
  const verifiedResult = requireProductionAuthorityResult(
    verifyProductionAuthorityContext(rawArtifacts));
  const authority = readProductionAuthorityContext(verifiedResult.authorityContext);
  if (authority.profile !== "gate-evaluation" || authority.gateEffective !== true
    || authority.headCommit !== structural.headCommit
    || authority.headTreeOid !== structural.headTreeOid
    || authority.externalPinsSha256 !== structural.externalPinsSha256) {
    return Object.freeze({ ...structural, errors: [{
      rule: "AUTHORITY-RED/CONTEXT-BINDING", record: options.head,
      message: "branded production authority does not bind the replayed Head/Tree/pins",
    }], authorityRequired: ["production-authority-context"],
    gateEffective: false, status: "FAILED" });
  }
  const semantic = finalizeProductionGateEvaluation({
    structural, productionAuthorityContext: verifiedResult.authorityContext,
  });
  if (semantic.errors.length) return Object.freeze({ ...semantic,
    authorityRequired: [], gateEffective: false, status: "FAILED" });
  return Object.freeze({ ...semantic, authorityContext: verifiedResult.authorityContext,
    authorityRequired: [], gateEffective: true, status: "VERIFIED" });
}
```

`validateProductionCommitRangeStructure` is a module-private, non-exported
variant of the same immutable First-Parent/read/schema/reference/ledger/crypto
replay. It defers only green-Gate effectiveness and returns the already parsed
target records plus full target Commit/Tree in a module-private WeakMap; its
ordinary frozen diagnostic object is not a capability and cannot be supplied
by a caller. `verifyProductionAuthorityContext` independently validates the
same raw target artifacts and can never receive that private parse result.
Only after its target-bound context is minted does
`finalizeProductionGateEvaluation` retrieve the private structural replay and
call Plan 04 `gateEligibilityErrors` for every green Gate with that exact
context and target Head/Tree. This three-stage order is mandatory:

1. immutable structural/cryptographic replay with green effectiveness pending;
2. independent Plan-11 target Authority verification and branding;
3. Plan-04 effective Gate evaluation over the branded target context.

No stage trusts a boolean from another; a structural failure blocks minting,
and a Gate failure discards the context result. Add a regression for the sole
green G0 candidate proving that the old order (`validateLocalCommitRange`
before authority) fails while this closed order passes only with its exact
Operator Acceptance, and fails for swapped target Head/Tree, copied structural
result, all-red-base context, or missing inventory-domain head.

The production export therefore has the exact signature
`validateGovernanceMode(options)`: there is no adapter, receipt boolean,
callback, raw clock, pins object, or deserialized authority argument. A source
allowlist permits `governance-mode-test-core.mjs` imports only from
`governance-contract.test.mjs`; production source must not contain its module
specifier. Plan 11's module-branded aggregate is the only route from a valid
Receipt prefix to `gateEffective:true`. Local modes never call it and never
claim external acceptance. Never validate only the final range diff, because
an intermediate forbidden change followed by a revert remains fatal.

- [ ] **Step 4: Run CLI tests and commit**

```powershell
node --experimental-strip-types --test scripts/governance-contract.test.mjs
$governanceOutput = & npm run check:governance -- --pre-genesis 2>&1
$governanceExit = $LASTEXITCODE
if ($governanceExit -eq 0 -or ($governanceOutput -join "`n") -notmatch 'AUTHORITY-RED/PRE-GENESIS') {
  throw 'pre-Genesis governance authority boundary was not enforced'
}
git add scripts/governance-contract.mjs scripts/governance-contract.test.mjs
git commit -m "feat: validate governance ledgers by Git baseline"
```

Expected: the focused tests pass; all four valid modes match the frozen mode
table; every conflicting/duplicate flag fails. The real repository remains
explicitly `AUTHORITY-RED/PRE-GENESIS`. Explicit local modes used by Plans
12/13 return `LOCAL-PREFLIGHT-ONLY` and exit 0 only when structurally valid,
while `gateEffective` remains false. Production mode fails without a valid
receipt for every adjacent commit. No repository, remote, or server write
occurs.

### Task 8: Run Plan-03 sequential verification

**Files:** No intended changes.

- [ ] **Step 1: Run focused suites in dependency order**

```powershell
node --test scripts/governance/repository-view.test.mjs
node --test scripts/governance/record-hashes.test.mjs
node --test scripts/governance/status-transitions.test.mjs
node --test scripts/governance/transition-ledger.test.mjs
```

Expected: all exit 0; mutation tests cover prefix, hash, state, amendment, actor, epoch, and commit-boundary failures.

- [ ] **Step 2: Run repository gates**

```powershell
npm test
npm run typecheck:governance
npm run check:canon
$governanceOutput = & npm run check:governance -- --pre-genesis 2>&1
$governanceExit = $LASTEXITCODE
if ($governanceExit -eq 0 -or ($governanceOutput -join "`n") -notmatch 'AUTHORITY-RED/PRE-GENESIS') {
  throw 'pre-Genesis governance authority boundary was not enforced'
}
npm run typecheck
npm run lint
git diff --check
git status --short
```

Expected: all ordinary local gates pass. The captured production governance
check alone remains nonzero with `AUTHORITY-RED/PRE-GENESIS`; its explicit
assertion passes only for that fail-closed pre-Genesis state.

Expected: all commands exit 0. Only Plan-03 paths differ; no UI, `server/`, `migrations/`, GitHub, Chrome, or M-G1 state changed.

- [ ] **Step 3: Commit a gate-only correction if required, then stop**

```powershell
git add docs/governance/governance.schema.json scripts/governance scripts/governance-contract.mjs scripts/governance-contract.test.mjs
git commit -m "test: close transition ledger quality gates"
```

Do not generate or accept Genesis signatures, remote receipts, transparency checkpoints, or green gates in this plan.
