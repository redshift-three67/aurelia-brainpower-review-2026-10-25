# AURELIA G0 11 Remote Governance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove read-only GitHub observability first, then implement offline verification of externally produced branch-control, acceptance-receipt, transparency, TCB, and witness evidence.

**Architecture:** The first task is a live, GET-only capability probe using a separately issued read-only GitHub App installation token; it is feasibility evidence, never gate evidence. If bypass actors are hidden, private-repository protection is unavailable, or any required field is unreadable, the live Remote-Acceptance/Gate path stops at `unknown/red` without requesting broader rights. Offline implementation and semantic verification in Tasks 2–6 may continue, but cannot mint a `gate-evaluation` production authority context or make a Gate green. The pure verifier consumes signed external bundles; the PR/head being checked never performs or attests its own authoritative remote observation.

The single module-private authority brand has exactly two closed profiles. `pre-genesis-ceremony` binds the exact local implementation commit `I`, its Tree, an independently signed complete phase-specific artifact inventory, independent external pins, production Trusted-Time, and the complete versioned Nonce prefix. It is always `gateEffective:false`, requires no Acceptance Receipt for `I` or `G`, and may be consumed only by Plan 12's pre-Genesis constructors. `gate-evaluation` additionally requires the externally accepted Head/Tree, branch-control evidence, the complete Acceptance-Receipt/checkpoint prefix, challenge-fresh Witness floors, and every Plans 05–10 production replay. An accepted all-red Head requires `operatorAcceptance:null`; the sole-green G0 Head is non-effective until its exact external full-commit Operator Acceptance, refreshed inventory/Nonce prefix, Receipt/checkpoint, and floors verify. Only a gate-effective instance of this second profile may be consumed by Plan 04's effective Gate engine. Both profiles are minted by the same sole issuer and stored in the same Plan-06 module-private WeakMap; no other authority brand or Nonce authority exists.

**Tech Stack:** GitHub REST API `2026-03-10` for the read-only probe, Node.js 22 ESM, `node:test`, RFC 8785, SHA-256, Ed25519, RFC 6962, existing transparency/TCB/recovery verifiers.

---

## Primary provider anchors

- REST API version pin: `https://docs.github.com/en/rest/about-the-rest-api/api-versions`.
- Protected-branch response and private-repository availability: `https://docs.github.com/en/rest/branches/branch-protection?apiVersion=2026-03-10` and `https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches`.
- Ruleset availability and rule semantics: `https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets`.
- The REST rules documentation states that `bypass_actors` is returned only with ruleset write access: `https://docs.github.com/en/rest/orgs/rules?apiVersion=2026-03-10`. The read-only probe therefore stops at `unknown/red` when it is hidden; it never broadens rights merely to observe it.
- GitHub GraphQL `updateRefs` specifies atomic multi-ref updates and `beforeOid` compare-and-swap semantics: `https://docs.github.com/en/graphql/reference/git#updaterefs`. Plan 07 uses that provider contract for the recovery pair; this plan only verifies evidence and performs no mutation.

These provider statements are design inputs, not live gate evidence. G0 effectiveness still requires the signed, externally pinned receipt/checkpoint/floor chain.

---

### Task 1: Run the strict read-only live-capability probe and STOP on uncertainty

**Files:** No repository files are created or modified. Probe output is written only to a dedicated operating-system temporary directory and is deleted by the operator after recording the verdict.

- [ ] **Step 1: Verify the authority boundary before any API call**

The operator must supply `AURELIA_GITHUB_READ_TOKEN` from a GitHub App installation whose declared repository permissions contain no `write` value. Do not use a classic PAT, the recovery gateway credential, a browser session cookie, or an operator token with administration write. Run locally without echoing the token:

```powershell
if (-not $env:AURELIA_GITHUB_READ_TOKEN) { throw 'AUTHORITY-RED: read-only GitHub App installation token absent' }
$env:GH_TOKEN = $env:AURELIA_GITHUB_READ_TOKEN
$probeParent = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath()).TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
$probePrefix = $probeParent + [System.IO.Path]::DirectorySeparatorChar
$probeRoot = Join-Path $probeParent ("aurelia-g0-github-read-capability-" + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Force -Path $probeRoot | Out-Null
function Stop-AureliaReadProbe([string]$reason) {
  Remove-Item Env:GH_TOKEN -ErrorAction SilentlyContinue
  Remove-Item Env:AURELIA_GITHUB_READ_TOKEN -ErrorAction SilentlyContinue
  if (Test-Path -LiteralPath $probeRoot) {
    $resolvedProbe = [System.IO.Path]::GetFullPath((Resolve-Path -LiteralPath $probeRoot).Path)
    if (-not $resolvedProbe.StartsWith($probePrefix, [System.StringComparison]::OrdinalIgnoreCase)) { throw 'Refusing to remove probe path outside temporary parent' }
    Remove-Item -LiteralPath $resolvedProbe -Recurse -Force
  }
  throw "AUTHORITY-RED: $reason"
}
```

Expected: the directory exists and no token value is printed. If the App permission declaration cannot be independently shown to be read-only, record `unknown/red` and stop this plan.

- [ ] **Step 2: Read repository and main-branch protection with GET only**

```powershell
gh api --method GET -H 'Accept: application/vnd.github+json' -H 'X-GitHub-Api-Version: 2026-03-10' /repos/redshift-three67/aurelia | Set-Content -Encoding utf8 (Join-Path $probeRoot 'repository.json')
gh api --method GET -H 'Accept: application/vnd.github+json' -H 'X-GitHub-Api-Version: 2026-03-10' /repos/redshift-three67/aurelia/branches/main/protection | Set-Content -Encoding utf8 (Join-Path $probeRoot 'main-protection.json')
gh api --method GET -H 'Accept: application/vnd.github+json' -H 'X-GitHub-Api-Version: 2026-03-10' /repos/redshift-three67/aurelia/branches/main/protection/required_signatures | Set-Content -Encoding utf8 (Join-Path $probeRoot 'required-signatures.json')
```

Expected: the three repository calls return HTTP 200; repository `private` is `true`; protection shows admin enforcement, required pull request review with CODEOWNERS, required checks, no force-push, and no deletion; required signatures are enabled. A 200 with the complete protection fields is practical read-only proof that protection is available on this repository. A 403, 404, unavailable feature, omitted protection field, or parse failure is ambiguous between configuration, tariff, and permission and is therefore `unknown/red`. No public User-API response is used as Billing-Evidence for an installation token. Separately protected Billing-Evidence may corroborate the prerequisite only after independent signature/hash/freshness verification; its absence never authorizes a write, subscription change, or broader token.

- [ ] **Step 3: Read complete ruleset details and prove bypass visibility**

```powershell
$rulesets = gh api --method GET -H 'Accept: application/vnd.github+json' -H 'X-GitHub-Api-Version: 2026-03-10' '/repos/redshift-three67/aurelia/rulesets?includes_parents=true' | ConvertFrom-Json
if (@($rulesets).Count -eq 0) { Stop-AureliaReadProbe 'no observable repository ruleset' }
foreach ($ruleset in @($rulesets)) {
  $detail = gh api --method GET -H 'Accept: application/vnd.github+json' -H 'X-GitHub-Api-Version: 2026-03-10' "/repos/redshift-three67/aurelia/rulesets/$($ruleset.id)" | ConvertFrom-Json
  if ($null -eq $detail.PSObject.Properties['bypass_actors']) { Stop-AureliaReadProbe "bypass_actors hidden for ruleset $($ruleset.id)" }
  $detail | ConvertTo-Json -Depth 100 | Set-Content -Encoding utf8 (Join-Path $probeRoot "ruleset-$($ruleset.id).json")
}
```

Expected: every relevant ruleset returns an explicit `bypass_actors` array, including an explicit empty array when no bypass exists. GitHub documentation warns that this property may be hidden without ruleset write access. If it is hidden under the approved read-only identity, stop at `unknown/red`; never request or grant write solely to make the probe pass.

- [ ] **Step 4: Read CODEOWNERS, commit verification, and marker refs**

```powershell
gh api --method GET -H 'Accept: application/vnd.github.raw+json' -H 'X-GitHub-Api-Version: 2026-03-10' '/repos/redshift-three67/aurelia/contents/.github/CODEOWNERS?ref=main' | Set-Content -Encoding utf8 (Join-Path $probeRoot 'CODEOWNERS')
gh api --method GET -H 'Accept: application/vnd.github+json' -H 'X-GitHub-Api-Version: 2026-03-10' '/repos/redshift-three67/aurelia/commits?sha=main&per_page=1' | Set-Content -Encoding utf8 (Join-Path $probeRoot 'main-head-commit.json')
$markerRefs = gh api --method GET -H 'Accept: application/vnd.github+json' -H 'X-GitHub-Api-Version: 2026-03-10' '/repos/redshift-three67/aurelia/git/matching-refs/heads/aurelia-recovery-markers/' | ConvertFrom-Json
@($markerRefs) | ConvertTo-Json -Depth 20 | Set-Content -Encoding utf8 (Join-Path $probeRoot 'marker-refs.json')
```

Expected: all requested resources are readable. An explicit empty marker array before Genesis is valid and expected; it does not prove namespace policy. Missing CODEOWNERS, unverifiable signature data, a hidden/non-enumerable marker response, or inability to distinguish an explicit empty array from authorization filtering is `unknown/red`. The create-only namespace policy must be observable from the ruleset details independently of current marker count.

- [ ] **Step 5: Record PASS or formal STOP without repository mutation**

PASS requires every preceding expectation plus explicit evidence that all requests used GET. Copy only a sanitized verdict containing endpoint names, HTTP status, field-presence booleans, and the final PASS/STOP code into the external execution record; never retain response bodies as gate evidence. Then securely remove the unique probe directory and token:

```powershell
Remove-Item Env:GH_TOKEN -ErrorAction SilentlyContinue
Remove-Item Env:AURELIA_GITHUB_READ_TOKEN -ErrorAction SilentlyContinue
if (Test-Path -LiteralPath $probeRoot) {
  $resolvedProbe = [System.IO.Path]::GetFullPath((Resolve-Path -LiteralPath $probeRoot).Path)
  if (-not $resolvedProbe.StartsWith($probePrefix, [System.StringComparison]::OrdinalIgnoreCase)) { throw 'Refusing to remove probe path outside temporary parent' }
  Remove-Item -LiteralPath $resolvedProbe -Recurse -Force
}
```

Expected: no repository diff. A STOP blocks every real Remote Acceptance-Receipt, `gate-evaluation` production authority context, Genesis acceptance, and green Gate until the design/authority problem is formally resolved. It does not block the offline implementation and test work in Tasks 2–6 or minting the deliberately non-gate `pre-genesis-ceremony` context; those paths must record `REMOTE-CAPABILITY-UNKNOWN` and remain non-gate-effective.

The operator additionally expires/revokes the short-lived GitHub App installation token at its issuer boundary. Removing both process variables is local hygiene, not proof of provider-side revocation; token values are never printed or copied into the verdict.

### Task 2: Capture the implementation base and define remote-input validation

**Files:**
- Create: `scripts/governance/remote-bundle.mjs`
- Create: `scripts/governance/remote-bundle.test.mjs`
- Create: `scripts/governance/schema-builders/remote-authority.mjs`
- Create: `docs/governance/schemas/external-pin-inventory.schema.json`
- Create: `docs/governance/schemas/trusted-time-attestation.schema.json`
- Create: `docs/governance/schemas/branch-control-attestation.schema.json`
- Create: `docs/governance/schemas/floor-challenge.schema.json`
- Create: `docs/governance/schemas/witness-floor-response.schema.json`
- Create: `docs/governance/schemas/initial-branch-policy-pin.schema.json`
- Create: `docs/governance/schemas/g0-operator-acceptance.schema.json`
- Create: `docs/governance/schemas/g0-gate-proposal-report.schema.json`
- Modify: `scripts/governance/nonce-replay.mjs`
- Modify: `scripts/governance/nonce-replay.test.mjs`
- Modify: `scripts/governance/schema-registry.test.mjs`
- Modify: `scripts/governance/production-authority-context.mjs`
- Modify: `scripts/governance/production-authority-context.test.mjs`
- Create: `scripts/fixtures/governance/remote/valid-remote-inputs.json`
- Create: `scripts/fixtures/governance/remote/missing-pin-inputs.json`

- [ ] **Step 1: Capture the exact pre-Plan-11 implementation base**

```powershell
$plan11BaseSha = git rev-parse HEAD
if ($plan11BaseSha -notmatch '^[0-9a-f]{40}$') { throw 'Plan 11 base is not a full commit SHA' }
$plan11BaseSha
```

Expected: a stable 40-character SHA. Record it as the immutable `plan11BaseSha` field in the external execution record. At each later verification step the orchestrator exports that exact value as `AURELIA_PLAN11_BASE_SHA`; do not create or move a Git ref.

- [ ] **Step 2: Write the failing closed-input test**

The module first exports a non-gate precursor verifier. Task 3 then extends Plan 06's central context module with the sole issuer `verifyProductionAuthorityContext` after Acceptance-Receipt replay exists:

```js
export function verifyRemoteAuthorityInputs({
  repositoryId,
  branch,
  headCommit,
  headTreeOid,
  transparencyBundle,
  externalPins,
  branchControlHistory,
  floorChallengeHistory,
  floorResponseHistory,
  trustedTimeHistory,
  nonceArtifacts,
  signedArtifactInventory,
}) {}
export function verifyPreGenesisCeremonyInputs({
  repositoryId,
  repositoryRoot,
  implementationCommit,
  signedArtifactInventory,
  ceremonyArtifacts,
  externalPins,
  trustedTimeHistory,
  nonceArtifacts,
}) {}
export function verifyTrustedTimeAttestation(trustedTimeAttestation, externalPins) {}
```

The four `*History` inputs are closed, nonempty, append-only chronological raw
artifact arrays, not verifier results or summaries. `floorResponseHistory` is
the complete chronological flattened response prefix and every response binds
exactly one member of `floorChallengeHistory`. Pre-Genesis uses the same
complete `trustedTimeHistory` ABI. The last Trusted-Time, Branch-Control, and
floor-challenge generation are the current controls; earlier elements remain
present even after expiry and can never be replaced by an inventory digest.

The two precursor exports above are implemented in
`production-authority-context.mjs`; `verifyTrustedTimeAttestation` is the fixed
low-level export from `remote-bundle.mjs` imported by that module. No CLI or
other production module calls a low-level function as authority.

Test exact repository `redshift-three67/aurelia`, branch `main`, full commit/tree OIDs, external pins for operator, recovery root, controller, recovery app, gateway, provider verifier, egress monitor, transparency instance, and every witness. Reject a pin sourced from the bundle itself, missing witness, duplicate failure domain, alias repository, stale time, or extra property.

`schema-builders/remote-authority.mjs` is the single writer for the eight
closed Draft-2020-12 schemas listed above. Every object and nested signature
sets `additionalProperties:false`; all canonical IDs, lower-case OIDs/hashes,
image digests, UTC timestamps, canonical Base64url values, array order, and
nonempty/count constraints are closed in schema and rechecked semantically.
The contracts are:

- `external-pin-inventory`: exact repository, sorted complete discriminated pin
  array, count/set digest/head, issuance/expiry, one `nonce`, and detached
  controller signature;
- `trusted-time-attestation`: pinned time-service identity/key/image/policy/time
  source, signed observed/valid interval, one `nonce`, and signature;
- `branch-control-attestation`: repository/branch/Head/Tree, complete visible
  branch/ruleset state including explicit bypass visibility, rules digest,
  observed/expiry times, one `nonce`, and validator signature;
- `floor-challenge`: repository/log/challenge/validator identity plus
  issued/expiry time, with the challenge value owned at `nonce`;
- `witness-floor-response`: response/witness/failure-domain identity, exact
  floor/checkpoint/tree-size binding, `challengeNonce` reference,
  `responseNonce` owner, response time, and Witness signature;
- `initial-branch-policy-pin`: repository/branch/epoch/rules digest/transition
  index, issuance/expiry, one `nonce`, and external controller signature;
- `g0-operator-acceptance`: exact fields
  `schemaVersion/acceptanceId/repositoryId/headCommit/headTreeOid/implementationCommit/designCommit/designSpecSha256/scope/pathManifestSha256/finalGateVectorSha256/finalLocalGateReportSha256/tcbStateSha256/branchPolicySha256/externalPinsSha256/priorNoncePrefixSha256/operatorIdentity/operatorRole/operatorEpoch/operatorKeyRef/operatorKeyFingerprint/trustedTimeAttestationSha256/approvedAt/nonce/signature`.
  Scope is exactly `AURELIA-G0-GOVERNANCE-ACCEPTANCE`; signature is closed to
  `algorithm:"Ed25519"/keyRef/value` and is excluded from the RFC-8785 signed
  core. No Receipt field or repository key may substitute this artifact.
- `g0-gate-proposal-report`: the exact non-effective committed/Working-Tree
  report contract from Task 5; target Commit/Tree are both full OIDs or both
  null, status is only `LOCAL-GATE-PROPOSAL-ONLY`, `gateEffective` is false,
  and the two authority requirements are fixed and ordered.

In the same sequential source edit, append exactly these entries to Plan 06's
single `GOVERNANCE_NONCE_PATHS` source literal and then freeze the completed
literal at module initialization: `external-pin-inventory` owns `nonce`;
`trusted-time-attestation` owns `nonce`; `branch-control-attestation` owns
`nonce`; `floor-challenge` owns `nonce`; `witness-floor-response` owns
`responseNonce` and references `challengeNonce`;
`initial-branch-policy-pin` owns `nonce`; and `g0-operator-acceptance` owns
`nonce`; `g0-gate-proposal-report` owns/references nothing. Use exactly `{owned:[string],references:[string]}` and the Plan-06
dot/`[]` grammar. Do not introduce `SCHEMA_NONCE_PATHS_V1`, JSONPath prefixes,
or runtime `Object.assign`. Registry/schema coverage and mutation tests must be
green in this commit.

- [ ] **Step 3: Run the test and record RED**

```powershell
node --test scripts/governance/remote-bundle.test.mjs
```

Expected: FAIL because `verifyRemoteAuthorityInputs` is missing.

- [ ] **Step 4: Implement pure remote-bundle composition**

Module ownership is exact before adding the code below.
`remote-bundle.mjs` owns only closed parsing and concrete low-level
cryptographic/semantic functions for pins, Trusted-Time, branch controls,
floors, transparency, and inventory bytes; callers cannot inject replacements.
It exports ordinary diagnostic results, never an authority brand or context.
The following WeakSets, descriptor collectors/binder, both precursor wrappers,
G0 Operator-Acceptance verifier, `verifyProductionAuthorityContext`, result
guard, and the one Plan-06 `PRODUCTION_AUTHORITY_CLAIMS.set` all live in
`production-authority-context.mjs`. That module imports the fixed low-level
functions, brands only their zero-error production results, and has no reverse
import from `remote-bundle.mjs`; therefore no private symbol crosses a module
boundary and no circular import exists. Tests import public top-level wrappers,
not WeakSets or partial constructors, and a source graph test freezes this
one-way edge.

```js
const PRODUCTION_PIN_RESULTS = new WeakSet();
const PRODUCTION_TRUSTED_TIMES = new WeakSet();
const PRODUCTION_TRUSTED_TIME_HISTORIES = new WeakSet();
const PRODUCTION_BRANCH_CONTROLS = new WeakSet();
const PRODUCTION_REMOTE_CONTROL_HISTORIES = new WeakSet();
const PRODUCTION_ARTIFACT_INVENTORIES = new WeakSet();
const REMOTE_AUTHORITY_PRECURSORS = new WeakSet();
const PRE_GENESIS_AUTHORITY_PRECURSORS = new WeakSet();
const PRODUCTION_PRE_GENESIS_INVENTORIES = new WeakSet();
const PRODUCTION_IMPLEMENTATION_TREES = new WeakSet();
const PRODUCTION_ARTIFACT_BINDINGS = new WeakSet();
const PRODUCTION_G0_OPERATOR_ACCEPTANCES = new WeakSet();

function verifySignedArtifactInventory({
  signedArtifactInventory,
  expectedPurpose,
  repositoryId,
  headCommit,
  headTreeOid,
  verifiedPins,
  verifiedTrustedTime,
}) {
  const errors = validateSchema("signed-artifact-inventory", signedArtifactInventory);
  if (!PRODUCTION_PIN_RESULTS.has(verifiedPins)) errors.push(diagnostic("inventory.signature.keyRef", "unverified external pin set"));
  if (!PRODUCTION_TRUSTED_TIMES.has(verifiedTrustedTime)) errors.push(diagnostic("inventory.issuedAt", "unverified trusted time"));
  const expectedBody = Object.freeze({
    purpose: expectedPurpose,
    inventoryId: signedArtifactInventory.inventoryId,
    repositoryId,
    headCommit,
    headTreeOid,
    artifactCount: signedArtifactInventory.artifactCount,
    artifactSetSha256: signedArtifactInventory.artifactSetSha256,
    governanceDomainState: signedArtifactInventory.governanceDomainState,
    issuedAt: signedArtifactInventory.issuedAt,
    expiresAt: signedArtifactInventory.expiresAt,
    nonce: signedArtifactInventory.nonce,
  });
  if (signedArtifactInventory.purpose !== expectedPurpose
    || signedArtifactInventory.repositoryId !== repositoryId
    || signedArtifactInventory.headCommit !== headCommit
    || signedArtifactInventory.headTreeOid !== headTreeOid) {
    errors.push(diagnostic("inventory", "purpose/repository/Head/Tree binding mismatch"));
  }
  const expectedPhase = expectedPurpose === "aurelia/gate-artifact-inventory/v1"
    ? "gate-evaluation" : null;
  if (expectedPhase !== null && signedArtifactInventory.governanceDomainState.phase !== expectedPhase) {
    errors.push(diagnostic("inventory.governanceDomainState.phase", "inventory phase/purpose mismatch"));
  }
  assertBase64urlBytesOrPush(errors, signedArtifactInventory.nonce, 32, "inventory.nonce");
  if (!Number.isSafeInteger(signedArtifactInventory.artifactCount)
    || signedArtifactInventory.artifactCount < 0
    || !/^[0-9a-f]{64}$/.test(signedArtifactInventory.artifactSetSha256)) {
    errors.push(diagnostic("inventory", "invalid artifact count or set digest"));
  }
  const nowMs = Date.parse(verifiedTrustedTime.now);
  const issuedMs = Date.parse(signedArtifactInventory.issuedAt);
  const expiresMs = Date.parse(signedArtifactInventory.expiresAt);
  if (![nowMs, issuedMs, expiresMs].every(Number.isFinite)
    || issuedMs > nowMs + 5 * 60_000 || nowMs > expiresMs || expiresMs > issuedMs + 24 * 60 * 60_000) {
    errors.push(diagnostic("inventory.issuedAt", "inventory is future-dated, expired, or exceeds 24-hour lifetime"));
  }
  const controllerKey = resolvePinnedPurposeKey(verifiedPins, {
    keyRef: signedArtifactInventory.signature.keyRef,
    purpose: "governance-artifact-inventory",
    at: signedArtifactInventory.issuedAt,
  });
  if (!controllerKey || signedArtifactInventory.signature.algorithm !== "Ed25519"
    || !verifyEd25519({
      publicKeyBase64url: controllerKey.publicKeyBase64url,
      payloadBytes: canonicalBytes(expectedBody),
      signatureBase64url: signedArtifactInventory.signature.value,
    })) {
    errors.push(diagnostic("inventory.signature", "invalid externally pinned controller signature"));
  }
  const result = Object.freeze({
    errors,
    authorityRequired: Object.freeze(["production-authority-context"]),
    cryptographicValid: errors.length === 0,
    gateEffective: false,
    inventoryId: signedArtifactInventory.inventoryId,
    artifactCount: signedArtifactInventory.artifactCount,
    artifactSetSha256: signedArtifactInventory.artifactSetSha256,
    signedInventorySha256: fullArtifactSha256(signedArtifactInventory),
    governanceDomainState: deepFreezePlainData(signedArtifactInventory.governanceDomainState),
  });
  if (errors.length === 0) PRODUCTION_ARTIFACT_INVENTORIES.add(result);
  return result;
}

function inventoryEnvelopeMatchesNonceStream(nonceArtifacts, inventory) {
  const envelopes = nonceArtifacts.filter((artifact) => artifact?.schemaName === "signed-artifact-inventory"
    && artifact.inventoryMember === false);
  return envelopes.length === 1
    && envelopes[0].artifactId === inventory.inventoryId
    && fullArtifactSha256(envelopes[0].value) === inventory.signedInventorySha256;
}

function derivePreAcceptanceNoncePrefixSha256(derivedArtifacts, errors) {
  const operatorIndexes = derivedArtifacts.flatMap((item, index) =>
    item.schemaName === "g0-operator-acceptance" ? [index] : []);
  if (operatorIndexes.length === 0) return null;
  if (operatorIndexes.length !== 1) {
    errors.push(diagnostic("operatorAcceptance", "exactly one operator acceptance is required when present"));
    return null;
  }
  const operatorIndex = operatorIndexes[0];
  const beforeOperator = derivedArtifacts.slice(0, operatorIndex);
  const currentInventories = derivedArtifacts.slice(operatorIndex + 1)
    .filter((item) => item.inventoryMember === false);
  const priorInventories = beforeOperator.filter((item) => item.schemaName === "signed-artifact-inventory"
    && item.inventoryMember !== false);
  if (beforeOperator.some((item) => item.inventoryMember === false)
    || currentInventories.length !== 1 || priorInventories.length === 0) {
    errors.push(diagnostic("operatorAcceptance.priorNoncePrefixSha256",
      "operator acceptance must follow an earlier complete prefix and precede the one current inventory"));
    return null;
  }
  const latestPrior = priorInventories.at(-1);
  const preAcceptanceDescriptors = beforeOperator
    .map((item) => item === latestPrior
      ? Object.freeze({ artifactId: item.artifactId, inventoryMember: false,
        schemaName: item.schemaName, value: item.value })
      : item);
  const replay = verifyGovernanceNoncePrefix({ artifacts: preAcceptanceDescriptors });
  errors.push(...replay.errors);
  return replay.cryptographicValid ? replay.noncePrefixSha256 : null;
}

const G0_DOMAIN_IDS = Object.freeze([
  "acceptance-receipts", "attestations", "authority-controls", "bootstrap",
  "collector", "design-approval", "events", "evidence", "external-model",
  "gates", "manifests", "operator-acceptance", "recovery", "register-records",
  "reviews", "tcb", "transparency-checkpoints", "trust-roots",
]);
const ARTIFACT_DOMAIN_BY_SCHEMA = Object.freeze({
  "final-design-approval": "design-approval",
  "pre-ledger-trust-bundle": "bootstrap",
  "signed-artifact-inventory": "authority-controls",
  "trust-roots": "trust-roots",
  "event-attestation": "attestations",
  "governance-event": "events",
  "governance-register-record": "register-records",
  "evidence-record": "evidence", "evidence-artifact": "evidence",
  "g0-gate-proposal-report": "evidence",
  "review-record": "reviews", "gate-record": "gates",
  "governance-manifest": "manifests",
  "acceptance-receipt": "acceptance-receipts",
  "branch-policy-transition": "authority-controls",
  "transparency-checkpoint": "transparency-checkpoints",
  "transparency-witness-floor": "transparency-checkpoints",
  "transparency-key-transition": "transparency-checkpoints",
  "transparency-equivocation-report": "transparency-checkpoints",
  "custodian-pin-transition": "recovery",
  "recovery-operation-lease": "recovery",
  "recovery-write-ahead-receipt": "recovery",
  "recovery-idempotency-tombstone": "recovery",
  "recovery-egress-intent": "recovery", "recovery-egress-closure": "recovery",
  "recovery-app-attestation": "recovery", "provider-ref-update-receipt": "recovery",
  "validator-promotion-request": "tcb", "validator-activation": "tcb",
  "validator-rollback-authorization": "tcb", "validator-activation-bundle": "tcb",
  "validator-rollback-record": "tcb",
  "emergency-tcb-recovery#authorized": "tcb",
  "emergency-tcb-recovery#completed": "tcb",
  "emergency-tcb-recovery#aborted": "tcb",
  "provider-due-diligence": "external-model", "sanitization-report": "external-model",
  "external-model-request-envelope": "external-model",
  "external-model-request-receipt": "external-model",
  "egress-transport-profile": "external-model",
  "network-enforcement-verification": "external-model",
  "egress-dispatcher-contract": "external-model",
  "egress-enforcement-lease": "external-model",
  "egress-dispatch-attestation": "external-model",
  "egress-transport-receipt": "external-model",
  "external-model-response-envelope": "external-model",
  "collector-contract": "collector", "collector-protected-state": "collector",
  "collector-sandbox-observation": "collector",
  "external-pin-inventory": "authority-controls",
  "trusted-time-attestation": "authority-controls",
  "branch-control-attestation": "authority-controls",
  "floor-challenge": "authority-controls", "witness-floor-response": "authority-controls",
  "initial-branch-policy-pin": "authority-controls",
  "g0-operator-acceptance": "operator-acceptance",
});

function deriveGovernanceDomainState(derivedArtifacts, expectedPhase, errors) {
  const state = new Map(G0_DOMAIN_IDS.map((domainId) =>
    [domainId, { domainId, artifactCount: 0, headSha256: null }]));
  for (const descriptor of derivedArtifacts) {
    if (descriptor.inventoryMember === false) continue;
    const domainId = ARTIFACT_DOMAIN_BY_SCHEMA[descriptor.schemaName];
    if (!domainId) {
      errors.push(diagnostic("governanceDomainState", `unmapped inventory subject schema ${descriptor.schemaName}`));
      continue;
    }
    const domain = state.get(domainId);
    domain.artifactCount += 1;
    domain.headSha256 = fullArtifactSha256(descriptor.value);
  }
  return Object.freeze({ phase: expectedPhase,
    domains: Object.freeze(G0_DOMAIN_IDS.map((domainId) => Object.freeze(state.get(domainId)))) });
}

function bindExactAuthorityArtifactDescriptors({ derivedArtifacts, suppliedArtifacts, inventory, expectedPhase }) {
  const errors = [];
  const sortDescriptors = (items) => [...items].sort((left, right) => {
    const a = `${left.schemaName}\u0000${left.artifactId}`;
    const b = `${right.schemaName}\u0000${right.artifactId}`;
    return a < b ? -1 : a > b ? 1 : 0;
  });
  const derivedComparison = sortDescriptors(derivedArtifacts);
  const suppliedComparison = sortDescriptors(suppliedArtifacts);
  if (!Buffer.from(canonicalBytes(derivedComparison)).equals(canonicalBytes(suppliedComparison))) {
    errors.push(diagnostic("nonceArtifacts", "supplied descriptor stream is not the exact derived raw-artifact bijection"));
  }
  const derived = [...derivedArtifacts];
  const noncePrefix = verifyGovernanceNoncePrefix({ artifacts: derived });
  errors.push(...noncePrefix.errors);
  const preAcceptanceNoncePrefixSha256 = derivePreAcceptanceNoncePrefixSha256(derived, errors);
  const derivedDomainState = deriveGovernanceDomainState(derived, expectedPhase, errors);
  if (!PRODUCTION_ARTIFACT_INVENTORIES.has(inventory)
    || inventory.artifactCount !== noncePrefix.artifactCount
    || inventory.artifactSetSha256 !== noncePrefix.artifactSetSha256
    || !inventoryEnvelopeMatchesNonceStream(derived, inventory)) {
    errors.push(diagnostic("signedArtifactInventory", "signed inventory does not bind the derived raw-artifact set"));
  }
  if (!Buffer.from(canonicalBytes(derivedDomainState))
    .equals(canonicalBytes(inventory.governanceDomainState))) {
    errors.push(diagnostic("signedArtifactInventory.governanceDomainState",
      "signed domain counts/heads do not equal the fixed derived artifact partition"));
  }
  const result = Object.freeze({ errors, noncePrefix, inventory, preAcceptanceNoncePrefixSha256,
    cryptographicValid: errors.length === 0, gateEffective: false,
    authorityRequired: Object.freeze(["production-authority-context"]) });
  if (errors.length === 0) PRODUCTION_ARTIFACT_BINDINGS.add(result);
  return result;
}

function verifyG0OperatorAcceptance(artifact, expected) {
  if (artifact === null) return Object.freeze({ present: false, errors: [], gateEffective: false });
  const errors = validateSchema("g0-operator-acceptance", artifact);
  if (errors.length !== 0) return Object.freeze({ present: true, errors,
    gateEffective: false, fullArtifactSha256: null, claims: null });
  const core = omit(artifact, ["signature"]);
  const { verifiedPins, verifiedTrustedTime, verifiedOperatorTrustedTime, ...bindings } = expected;
  for (const [field, value] of Object.entries(bindings)) {
    if (core[field] !== value) errors.push(diagnostic(`operatorAcceptance.${field}`, "operator acceptance binding mismatch"));
  }
  const key = resolvePinnedPurposeKey(verifiedPins, {
    keyRef: artifact.operatorKeyRef, purpose: "g0-governance-acceptance", at: artifact.approvedAt,
  });
  if (!key || artifact.operatorIdentity !== "redshift-three67"
    || artifact.operatorRole !== "ROLE-OPERATOR"
    || artifact.signature.algorithm !== "Ed25519"
    || artifact.signature.keyRef !== artifact.operatorKeyRef
    || artifact.operatorKeyFingerprint !== key.fingerprintSha256
    || !PRODUCTION_TRUSTED_TIMES.has(verifiedOperatorTrustedTime)
    || artifact.approvedAt !== verifiedOperatorTrustedTime.now
    || artifact.trustedTimeAttestationSha256 !== verifiedOperatorTrustedTime.attestationSha256
    || Date.parse(artifact.approvedAt) > Date.parse(verifiedTrustedTime.now)
    || Date.parse(verifiedTrustedTime.now) - Date.parse(artifact.approvedAt) > 24 * 60 * 60_000
    || !verifyEd25519({ publicKeyBase64url: key.publicKeyBase64url,
      payloadBytes: canonicalBytes(core), signatureBase64url: artifact.signature.value })) {
    errors.push(diagnostic("operatorAcceptance.signature", "operator acceptance identity/time/signature mismatch"));
  }
  const result = Object.freeze({ present: true, errors, gateEffective: false,
    fullArtifactSha256: fullArtifactSha256(artifact), claims: errors.length ? null : deepFreezePlainData(core) });
  if (errors.length === 0) PRODUCTION_G0_OPERATOR_ACCEPTANCES.add(result);
  return result;
}

export function verifyRemoteAuthorityInputs(input) {
  const shapeErrors = validateRemoteInputShape(input);
  if (shapeErrors.length) return Object.freeze({ errors: shapeErrors, authorityRequired: [], candidateValid: false, gateEffective: false });
  const pins = verifyExternalPinSet(input.externalPins);
  const controlHistory = verifyRemoteControlHistory({
    externalPins: input.externalPins,
    trustedTimeHistory: input.trustedTimeHistory,
    branchControlHistory: input.branchControlHistory,
    floorChallengeHistory: input.floorChallengeHistory,
    floorResponseHistory: input.floorResponseHistory,
    headCommit: input.headCommit,
    headTreeOid: input.headTreeOid,
  });
  const { currentTrustedTime: trustedTime, currentBranchControls: branchControls,
    currentFloorChallenge: floorChallenge, currentFloorResponses: floorResponses } = controlHistory;
  if (!PRODUCTION_PIN_RESULTS.has(pins) || !PRODUCTION_REMOTE_CONTROL_HISTORIES.has(controlHistory)) return combineAuthorityResults(pins, controlHistory);
  const transparency = verifyTransparencyBundle({
    bundle: input.transparencyBundle,
    externalPins: input.externalPins,
    verificationTime: trustedTime.now,
  });
  const floors = verifyFreshWitnessFloors({
    bundle: input.transparencyBundle,
    externalPins: input.externalPins,
    now: trustedTime.now,
    challenge: Object.freeze({ ...floorChallenge, responses: floorResponses }),
  });
  const noncePrefix = verifyGovernanceNoncePrefix({ artifacts: input.nonceArtifacts });
  const inventory = verifySignedArtifactInventory({
    signedArtifactInventory: input.signedArtifactInventory,
    expectedPurpose: "aurelia/gate-artifact-inventory/v1",
    repositoryId: input.repositoryId,
    headCommit: input.headCommit,
    headTreeOid: input.headTreeOid,
    verifiedPins: pins,
    verifiedTrustedTime: trustedTime,
  });
  const combined = combineAuthorityResults(pins, controlHistory, transparency, floors, branchControls, noncePrefix, inventory);
  const candidateValid = combined.errors.length === 0
    && combined.authorityRequired.every((item) => item === "production-authority-context")
    && PRODUCTION_BRANCH_CONTROLS.has(branchControls)
    && pins.externalPinsSha256 === sha256Hex(canonicalBytes(input.externalPins))
    && transparency.cryptographicValid === true
    && floors.cryptographicValid === true
    && noncePrefix.cryptographicValid === true
    && PRODUCTION_ARTIFACT_INVENTORIES.has(inventory)
    && inventory.artifactCount === noncePrefix.artifactCount
    && inventory.artifactSetSha256 === noncePrefix.artifactSetSha256
    && inventoryEnvelopeMatchesNonceStream(input.nonceArtifacts, inventory)
    && /^[0-9a-f]{64}$/.test(noncePrefix.noncePrefixSha256)
    && JSON.stringify(noncePrefix.occupiedNonces) === JSON.stringify([...noncePrefix.occupiedNonces].sort((a, b) => (a < b ? -1 : a > b ? 1 : 0)));
  const precursor = Object.freeze({
    errors: combined.errors,
    authorityRequired: Object.freeze(["acceptance-receipt-prefix"]),
    candidateValid,
    gateEffective: false,
    repositoryId: input.repositoryId,
    branch: input.branch,
    headCommit: input.headCommit,
    headTreeOid: input.headTreeOid,
    verifiedPins: pins,
    verifiedTrustedTime: trustedTime,
    verifiedControlHistory: controlHistory,
    verifiedTransparency: transparency,
    verifiedFloors: floors,
    verifiedBranchControls: branchControls,
    verifiedNoncePrefix: noncePrefix,
    verifiedInventory: inventory,
  });
  if (candidateValid) REMOTE_AUTHORITY_PRECURSORS.add(precursor);
  return precursor;
}

export function verifyPreGenesisCeremonyInputs(input) {
  const shapeErrors = validateClosedPreGenesisInput(input);
  if (shapeErrors.length) return Object.freeze({ errors: shapeErrors, authorityRequired: ["pre-genesis-ceremony"], candidateValid: false, gateEffective: false });
  const pins = verifyExternalPinSet(input.externalPins);
  const trustedTimeHistory = verifyTrustedTimeHistory({
    externalPins: input.externalPins,
    trustedTimeHistory: input.trustedTimeHistory,
  });
  const trustedTime = trustedTimeHistory.currentTrustedTime;
  if (!PRODUCTION_PIN_RESULTS.has(pins) || !PRODUCTION_TRUSTED_TIME_HISTORIES.has(trustedTimeHistory)) return combineAuthorityResults(pins, trustedTimeHistory);
  const implementationTree = verifyExactImplementationTree({
    repositoryRoot: input.repositoryRoot,
    repositoryId: input.repositoryId,
    implementationCommit: input.implementationCommit,
  });
  const verifiedInventoryEnvelope = verifySignedArtifactInventory({
    signedArtifactInventory: input.signedArtifactInventory,
    expectedPurpose: "aurelia/pre-genesis-artifact-inventory/v1",
    repositoryId: input.repositoryId,
    headCommit: implementationTree.commit,
    headTreeOid: implementationTree.treeOid,
    verifiedPins: pins,
    verifiedTrustedTime: trustedTime,
  });
  const inventory = verifySignedPreGenesisInventory({
    verifiedInventoryEnvelope,
    implementationTree,
  });
  const artifactBinding = bindExactAuthorityArtifactDescriptors({
    derivedArtifacts: collectPreGenesisAuthorityArtifacts(input),
    suppliedArtifacts: input.nonceArtifacts,
    inventory,
    expectedPhase: inventory.governanceDomainState.phase,
  });
  const noncePrefix = artifactBinding.noncePrefix;
  const combined = combineAuthorityResults(pins, trustedTimeHistory, implementationTree, verifiedInventoryEnvelope, inventory, artifactBinding);
  const candidateValid = combined.errors.length === 0
    && PRODUCTION_IMPLEMENTATION_TREES.has(implementationTree)
    && PRODUCTION_PRE_GENESIS_INVENTORIES.has(inventory)
    && PRODUCTION_ARTIFACT_BINDINGS.has(artifactBinding)
    && noncePrefix.cryptographicValid === true
    && inventory.preGenesisRepositoryStateVerified === true
    && inventory.artifactCount === noncePrefix.artifactCount
    && inventory.artifactSetSha256 === noncePrefix.artifactSetSha256
    && inventoryEnvelopeMatchesNonceStream(input.nonceArtifacts, inventory);
  const precursor = Object.freeze({
    errors: combined.errors,
    authorityRequired: Object.freeze(["genesis", "remote-acceptance"]),
    candidateValid,
    gateEffective: false,
    repositoryId: input.repositoryId,
    implementationCommit: implementationTree.commit,
    implementationTreeOid: implementationTree.treeOid,
    verifiedPins: pins,
    verifiedTrustedTime: trustedTime,
    verifiedTrustedTimeHistory: trustedTimeHistory,
    verifiedNoncePrefix: noncePrefix,
    verifiedInventory: inventory,
  });
  if (candidateValid) PRE_GENESIS_AUTHORITY_PRECURSORS.add(precursor);
  return precursor;
}

function combineAuthorityResults(...results) {
  const errors = results.flatMap((result) => result.errors ?? []);
  const authorityRequired = [...new Set(results.flatMap((result) => result.authorityRequired ?? []))];
  return Object.freeze({ errors, authorityRequired, candidateValid: false, gateEffective: false });
}
```

No function in this module imports `fetch`, `https`, `child_process`, `octokit`, `gh`, or a provider SDK. `verifyExternalPinSet`, `verifyTrustedTimeAttestation`, `verifyBranchControlEvidence`, and `verifySignedArtifactInventory` place successful production results in module-private WeakSets; a structurally identical plain object fails. Plan 06's closed `signed-artifact-inventory` schema allows exactly `purpose/inventoryId/repositoryId/headCommit/headTreeOid/artifactCount/artifactSetSha256/governanceDomainState/issuedAt/expiresAt/nonce/signature`, closes `signature` to `algorithm/keyRef/value`, and fixes the complete G0 domain list plus its closed phase discriminator; all OIDs, digests, timestamps, IDs, domain entries, and count bounds are schema-checked before the code above. `resolvePinnedPurposeKey` accepts only an independently pinned controller key valid for purpose `governance-artifact-inventory` at the signed issuance time. Every individual pin/time/transparency/floor/branch-control/Nonce/inventory result remains `gateEffective:false` with `authorityRequired:["production-authority-context"]`, even when it exposes `cryptographicValid:true`; only the final issuer may return gate-effective true. The pin verifier checks the independently signed complete pin inventory/count/head and exposes both frozen `pins` claims and `externalPinsSha256 = SHA256(RFC8785(all external pins))`; a partial or repository-derived pin set never brands. Trusted time exposes `now` only inside its branded result after service identity, key, image/policy/time-source digests, signed time, nonce, and validity window verify. No caller string becomes `now`. Each challenge is canonical 32-byte Base64url, every Witness response signs that challenge and the current floor, and replayed or pre-challenge responses fail.

`verifyTrustedTimeHistory` and `verifyRemoteControlHistory` are concrete,
non-injectable production functions in the same module. They require canonical
nonempty arrays in strictly increasing issuance/sequence order, reject
duplicate raw artifact hashes, and independently run schema, external-pin,
signature, identity, repository, branch, Head/Tree-at-observation,
challenge-reference, Witness failure-domain, and freshness-at-issuance checks
for every historical member. Historical members may be expired at the current
evaluation time; they must have been valid inside their own signed interval.
Only each array's tail must satisfy current expiry/freshness and bind the
evaluated Head/Tree/checkpoint. Every challenge has its exact nonempty response
group, groups are ordered by challenge position, and no response can migrate
between groups. Successful results enter only module-private
`PRODUCTION_TRUSTED_TIME_HISTORIES` and
`PRODUCTION_REMOTE_CONTROL_HISTORIES`; their current members are already
branded low-level results, not caller-selected values. The collectors consume
every raw member of the branded histories. Removing or reordering an old
member, retaining a later artifact while deleting its prerequisite, or reusing
any old Time/Floor/Branch-Control Nonce two waves later is fatal before
inventory binding.

`verifyGovernanceNoncePrefix` is the central Plan-06 raw replay over every versioned schema-declared nonce path. It deliberately cannot assert inventory completeness and always returns `inventoryBindingVerified:false,gateEffective:false`. Phase A independently verifies the signed inventory, compares its subject count/hash with the replay's `artifactCount/artifactSetSha256`, and proves that exactly the excluded `signed-artifact-inventory` descriptor contains the very same signed envelope by full hash and `inventoryId`. Its nonce remains in the global Nonce prefix, while its full hash is excluded from the set it signs, so there is no self-hash cycle. Omitted domains, unknown nonce-like fields, false-empty inventories, substituted inventory envelopes, count/hash drift, or reuse make `candidateValid:false`. Tests mutate every signed field, controller pin/purpose, validity boundary, descriptor identity, envelope hash, subject count/hash, excluded-member flag, and duplicate/absent envelope independently. A freely supplied clock exists only in a test helper with `gateEffective:false` and `TEST-ONLY-NON-GATE`; production verification has no time injection. Fixtures contain no private key: public RFC-8032 vectors test cryptography; test-only semantic injection cannot cross the production wrapper and cannot make the CLI exit gate-effective 0. The precursor is deliberately not a `ProductionAuthorityContext` and can never be used downstream.

`collectPreGenesisAuthorityArtifacts` and `collectGateAuthorityArtifacts` are
module-private fixed extractor tables, not generic recursion or caller
callbacks. They derive every descriptor's `schemaName`, canonical artifact ID,
actual parsed `value`, and full hash directly from the objects the production
verifiers consume. For `evidence-artifact`, the Gate collector accepts only
Plan 04's `readVerifiedEvidenceArtifactDescriptors` output from the current
module-branded artifact-set result. Its closed value binds EVID ID, exact path/
URI, actual byte hash/length, and immutable locator; a raw descriptor, EVID
claim, or signed-inventory entry cannot manufacture that brand. The extractor
requires exactly one such descriptor for every non-`expected` target EVID and
no descriptor for any other ID. The extractors merge all families into one signed append
order using schema-defined sequence/log positions and reject equal, missing,
regressing, or family-inconsistent positions. Lexical descriptor sorting is
used only for the redundant bijection comparison, never for Nonce replay or
reference resolution. Pre-Genesis extraction covers the exact external pin
inventory, every raw member of `trustedTimeHistory`, every actual `ceremonyArtifacts` value
(zero artifacts, then Final Approval, then Pre-Ledger and prior signed
inventories), and the current signed inventory envelope. Gate extraction covers
every raw member of the independently ordered `trustedTimeHistory`,
`branchControlHistory`, `floorChallengeHistory`, and `floorResponseHistory`
plus every actual Transparency entry, Acceptance Receipt,
initial policy pin, Plans-05–10 production artifact, optional G0 Operator
Acceptance, and every prior/current inventory envelope. For a sole-green
candidate it includes the accepted-base historical
`operatorTrustedTimeAttestation` and exact committed
`g0-gate-proposal-report` before the Operator Acceptance. The new current
Trusted-Time attestation, Receipt/checkpoint/floor claims, and current
inventory are sequence-checked after it;
for all-red heads `productionArtifacts.g0GateProposalReport` is literal null.
`productionArtifacts.operatorTrustedTimeAttestation` is also literal null.
No earlier control can be reconstructed from count/hash/head summaries: every
historical raw artifact remains mandatory. Only the current inventory descriptor has
`inventoryMember:false`; prior inventories are ordinary included subjects, so
their Nonces never disappear when the inventory refreshes.

For a sole-green candidate, `productionArtifacts` has the additional exact
field `operatorTrustedTimeAttestation`, containing the complete canonical
Trusted-Time artifact used by the accepted all-red base when the Operator core
was released. It is mandatory and non-null iff `g0GateRequested:true`; it is
literal `null` for every all-red Head. The proposal runner copies those exact
raw bytes from the accepted-base bundle into its protected signing-request
handoff and binds their full hash to
`trustedTimeAttestationSha256`. The final process reparses and independently
verifies that preserved artifact, requires byte/hash equality with the
accepted-base value, and brands it as `verifiedOperatorTrustedTime`. The
  separate current tail of `remoteAuthorityInputs.trustedTimeHistory` is freshly
issued after integration, occurs later in the descriptor stream, and may
never replace the historical artifact. Both are inventory subjects and have
globally unique Nonces. Current protected time must be no earlier than the
historical value and the approval age must be at most 24 hours.

The supplied `nonceArtifacts` file is only a redundant transport cross-check.
`bindExactAuthorityArtifactDescriptors` code-unit-sorts copies of both lists
and requires canonical byte equality, then passes the original derived append
order to `verifyGovernanceNoncePrefix`. Every consumed raw value therefore has
exactly one descriptor with identical
`schemaName/artifactId/fullArtifactSha256(value)`, and no descriptor may be
extra, omitted, duplicated, or point to alternate bytes. The signed inventory
must then equal the derived subject count/hash. `productionArtifacts` contains
the actual closed artifact values, never precomputed verifier results or free
hash references. Tests replace each raw family while retaining stream A,
replace stream A while retaining raw family B, duplicate and omit every family,
swap IDs/schemas, vary array order, and substitute a prior/current inventory;
all fail before a context can be minted. They also mutate, remove, and append
bytes behind every EVID artifact locator while retaining its record and
inventory descriptor; every case fails at Plan 04's byte binding before the
inventory bijection or authority issuer.

`ARTIFACT_DOMAIN_BY_SCHEMA` is the one closed, total partition of the same
schema names registered by Plan 06 and sequentially extended by Plans 07–11.
Its keys are artifact-dispatch keys. For the one discriminated
`emergency-tcb-recovery` file schema, the fixed collector validates that base
schema first and then derives exactly
`emergency-tcb-recovery#authorized|#completed|#aborted` from the closed
validated `phase`; callers and descriptor files cannot supply the suffix. The
artifact-schema dispatch registry exposes those three virtual keys, each
resolving to the same compiled base schema, so its key set remains exactly
equal to the Nonce and domain registries without weakening schema closure.
After chronological extraction, `deriveGovernanceDomainState` skips only the
current `inventoryMember:false` envelope, counts every included subject exactly
once, and sets each domain head to the last subject's full canonical hash in
append order. The expected phase is fixed by the verified profile; the complete
derived `{phase,domains}` must be byte-identical to the signed inventory field.
Registry tests prove exact key-set equality among the Nonce registry, domain
map, expanded artifact-schema dispatch registry, and collector dispatch table;
they also prove the three emergency virtual keys are exhaustive and reject an
unknown phase before descriptor construction. Per-schema movement to a
wrong domain, count drift, stale/non-last head, omitted empty domain, reordered
domain, and inclusion of the self-excluded current inventory all fail before
branding.

When `g0GateRequested:true`, `derivePreAcceptanceNoncePrefixSha256` takes the
exact chronological descriptor prefix before the one Operator Acceptance,
requires that its latest signed inventory is the last inventory in that prefix,
temporarily marks that earlier inventory as the sole excluded envelope, and
reruns the same Plan-06 replay. The preserved Operator Trusted-Time artifact
and committed proposal report occur in that prefix; the newly refreshed
current Trusted-Time artifact, Receipt/checkpoint/floor claims, and the one
refreshed current inventory occur after the Operator artifact. The resulting digest is the operator artifact's
exact `priorNoncePrefixSha256`. The final replay then adds exactly the
operator's one new owned Nonce, any later validator Receipt,
checkpoint/floor claims in signed order, and the refreshed current inventory
Nonce; it does not erase the prior inventory Nonce. The refreshed inventory's
`operator-acceptance` domain is exactly `{domainId:"operator-acceptance",artifactCount:1,headSha256:<full operator
artifact hash>}` and its subject set contains that artifact and every prior
inventory. The prior-prefix digest therefore never includes the Receipt that
is appended only after integration. For any all-red head the operator artifact must be literal `null`,
the domain is exactly `{domainId:"operator-acceptance",artifactCount:0,headSha256:null}`, and the pre-acceptance digest
is null. Tests mutate the selected prior inventory, append order,
operator Nonce, prior-prefix digest, domain count/head, current envelope, and
each one-new-claim expectation independently.

`validateClosedPreGenesisInput` rejects extra/missing keys and accepts only repository `redshift-three67/aurelia` plus a full 40-hex `implementationCommit` and the closed `ceremonyArtifacts` array. `verifyExactImplementationTree` uses Plan 03's read-only repository view at that full commit, resolves the Git Tree OID from the commit object, verifies repository identity and the complete forbidden pre-Genesis path scan with `git ls-tree`, and brands that immutable Commit/Tree pair. The Git Tree OID is the sole complete implementation-tree manifest; the Governance artifact inventory is not misused as a code-file list. The generic `verifySignedArtifactInventory` separately performs the detached Ed25519, purpose, pin, time, repository, Commit, Tree, Governance-subject count/hash, and Nonce verification. `verifySignedPreGenesisInventory` accepts only its module-branded result plus the module-branded immutable Tree result; it does not re-parse or re-trust the raw envelope. It proves that the four Governance registers, trust roots, seed attestations, evidence, reviews, gates, manifests, records, and Events are absent from immutable `I`. It then enforces the signed phase table: `before-final-approval` has design-approval/bootstrap counts `0/0`; `before-pre-ledger` has `1/0`; `before-genesis` has `1/1`; every other repository/ceremony domain remains zero/null, while `authority-controls` equals the exact internally derived pin/time/control set. Each nonzero phase head equals the verified full hash of its one subject artifact in the signed subject set. It returns the generic inventory claims plus `preGenesisRepositoryStateVerified:true` and adds that result to `PRODUCTION_PRE_GENESIS_INVENTORIES`. Thus a refreshed ceremony inventory may legitimately include the public final approval and then the public Pre-Ledger bundle without pretending either was already inside `I`. The helpers brand only after all checks pass and always return `gateEffective:false`; no boolean such as `complete`, caller-provided Tree, unsigned inventory, or repository-derived pin is authoritative. Tests mutate every phase transition, forbidden nonzero domain, subject head, absence, entry, count, signature, commit, Tree, pin, and inventory hash independently. The pre-Genesis precursor therefore breaks the I→Receipt→Genesis cycle without pretending that Genesis or Remote Acceptance already exists.

- [ ] **Step 5: Run tests and commit**

```powershell
node --test scripts/governance/remote-bundle.test.mjs scripts/governance/production-authority-context.test.mjs scripts/governance/nonce-replay.test.mjs scripts/governance/schema-registry.test.mjs
git add scripts/governance/remote-bundle.mjs scripts/governance/remote-bundle.test.mjs scripts/governance/schema-builders/remote-authority.mjs scripts/governance/production-authority-context.mjs scripts/governance/production-authority-context.test.mjs scripts/governance/nonce-replay.mjs scripts/governance/nonce-replay.test.mjs scripts/governance/schema-registry.test.mjs docs/governance/schemas/external-pin-inventory.schema.json docs/governance/schemas/trusted-time-attestation.schema.json docs/governance/schemas/branch-control-attestation.schema.json docs/governance/schemas/floor-challenge.schema.json docs/governance/schemas/witness-floor-response.schema.json docs/governance/schemas/initial-branch-policy-pin.schema.json docs/governance/schemas/g0-operator-acceptance.schema.json docs/governance/schemas/g0-gate-proposal-report.schema.json scripts/fixtures/governance/remote/valid-remote-inputs.json scripts/fixtures/governance/remote/missing-pin-inputs.json
git commit -m "feat: verify remote governance inputs offline"
```

Expected: tests pass; commit contains no live-probe output or token.

### Task 3: Verify acceptance receipts and branch-policy epochs

**Files:**
- Create: `scripts/governance/remote-receipts.mjs`
- Create: `scripts/governance/remote-receipts.test.mjs`
- Modify: `scripts/governance/remote-bundle.mjs`
- Modify: `scripts/governance/remote-bundle.test.mjs`
- Modify: `scripts/governance/production-authority-context.mjs`
- Modify: `scripts/governance/production-authority-context.test.mjs`
- Create: `scripts/fixtures/governance/remote/valid-receipt-prefix.json`
- Create: `scripts/fixtures/governance/remote/policy-transition-prefix.json`

- [ ] **Step 1: Write failing receipt and policy-transition tests**

Test exact event/attestation coverage, Head/Tree OIDs, validator image/policy/workflow/schema/trust-protocol digests, TCB epoch/id/hash, branch rules hash, policy epoch, OIDC tuple, and acceptance time. Then append one branch-policy transition and prove all earlier receipts in the old epoch become non-gate-effective, including three receipts with distinct heads. A later return to identical rule bytes must create another epoch and must not reactivate old receipts.

Also test both authority profiles. `pre-genesis-ceremony` accepts only the exact immutable `I` Tree plus the independently signed phase-correct complete artifact inventory, complete pins, production Trusted-Time, and full Nonce prefix; it returns an opaque readable context with `profile:"pre-genesis-ceremony"`, `gateEffective:false`, and no Receipt requirement. Any Gate consumer rejects it. `gate-evaluation` fails until every branded Phase-A Plan-05–10 candidate, complete Receipt/checkpoint/floor/branch-control prefix, accepted Head/Tree, external pin hash, and Nonce prefix is present. A copied context, swapped profile, raw subresult, semantic/test-only result, or second WeakMap/WeakSet authority must fail.

- [ ] **Step 2: Run and record RED**

```powershell
node --test scripts/governance/remote-receipts.test.mjs
```

Expected: FAIL because `verifyAcceptanceReceipts` and `deriveBranchPolicyState` are absent.

- [ ] **Step 3: Implement append-only receipt replay**

```js
const PRODUCTION_POLICY_PINS = new WeakSet();

export function deriveBranchPolicyState(entries, branch, initialBranchPolicyPin) {
  if (!PRODUCTION_POLICY_PINS.has(initialBranchPolicyPin) || initialBranchPolicyPin.branch !== branch || !Number.isInteger(initialBranchPolicyPin.epoch) || initialBranchPolicyPin.epoch < 1 || !/^[0-9a-f]{64}$/.test(initialBranchPolicyPin.rulesSha256)) throw contractFailure("initialBranchPolicyPin", "externally verified initial branch-policy pin required");
  return entries.reduce((state, entry) => {
    if (entry.entryKind !== "branch-policy-transition" || entry.branch !== branch) return state;
    if (entry.previousBranchPolicyEpoch !== state.epoch) throw contractFailure("branchPolicyEpoch", "nonlinear policy epoch");
    return Object.freeze({ epoch: entry.branchPolicyEpoch, rulesSha256: entry.observedBranchRulesSha256, transitionIndex: entry.transparencyLogIndex });
  }, Object.freeze({ epoch: initialBranchPolicyPin.epoch, rulesSha256: initialBranchPolicyPin.rulesSha256, transitionIndex: initialBranchPolicyPin.transitionIndex }));
}
```

`externallyVerified` is not a caller-trusted boolean: the production wrapper constructs and brands `initialBranchPolicyPin` only after its external signature, signer key/purpose, repository/branch, rules digest, epoch, observed time/freshness, and external pin match pass. A plain object is rejected. `verifyAcceptanceReceipts` must reject omitted/extra attestation nonces, stale TCB state, a first receipt not bound to that initial pin, receipt from a discarded epoch, incorrect actual Head/Tree, and any receipt not covered by the supplied full-prefix checkpoint.

After implementing that replay, extend Plan 06's `production-authority-context.mjs`. Plan 06 already owns the module-private WeakMap and `readProductionAuthorityContext(value)`; Plan 11 adds the single and only issuer `verifyProductionAuthorityContext(rawArtifacts)`. No other module may write to the WeakMap:

```js
// remote-receipts.mjs
const PRODUCTION_ACCEPTANCE_RESULTS = new WeakSet();

// The production replay adds its own zero-error/full-prefix result before return.
export function isProductionAcceptanceResult(result) {
  return PRODUCTION_ACCEPTANCE_RESULTS.has(result);
}

// production-authority-context.mjs; PRODUCTION_AUTHORITY_CLAIMS and
// readProductionAuthorityContext already exist from Plan 06.
const PRODUCTION_AUTHORITY_RESULTS = new WeakSet();

export function verifyProductionAuthorityContext(rawArtifacts) {
  const deepFreeze = (value, ancestors = new Set()) => {
    if (value === null || typeof value !== "object") {
      if (["function", "symbol", "undefined"].includes(typeof value)) throw new TypeError("non-data authority claim");
      return value;
    }
    if (ancestors.has(value) || value instanceof Map || value instanceof Set || value instanceof Date || ![null, Object.prototype, Array.prototype].includes(Object.getPrototypeOf(value))) throw new TypeError("non-plain or cyclic authority claim");
    if (Object.values(Object.getOwnPropertyDescriptors(value)).some((descriptor) => descriptor.get || descriptor.set)) throw new TypeError("authority claim accessor forbidden");
    ancestors.add(value);
    for (const item of Object.values(value)) deepFreeze(item, ancestors);
    ancestors.delete(value);
    return Object.freeze(value);
  };
  const asFrozenRecord = (map) => deepFreeze(Object.fromEntries(
    [...map.entries()].sort(([left], [right]) => (left < right ? -1 : left > right ? 1 : 0)),
  ));
  if (rawArtifacts?.profile === "pre-genesis-ceremony") {
    assertClosedObject(rawArtifacts, ["profile", "preGenesisInputs"], "productionAuthorityArtifacts");
    const precursor = verifyPreGenesisCeremonyInputs(rawArtifacts.preGenesisInputs);
    if (!PRE_GENESIS_AUTHORITY_PRECURSORS.has(precursor)) {
      return Object.freeze({ errors: precursor.errors, authorityRequired: ["pre-genesis-ceremony"], gateEffective: false, authorityContext: null });
    }
    return mintAuthorityContext("pre-genesis-ceremony", {
      repositoryId: precursor.repositoryId,
      implementationCommit: precursor.implementationCommit,
      implementationTreeOid: precursor.implementationTreeOid,
      pins: precursor.verifiedPins.pins,
      externalPinsSha256: precursor.verifiedPins.externalPinsSha256,
      trustedTime: { now: precursor.verifiedTrustedTime.now, attestationSha256: precursor.verifiedTrustedTime.attestationSha256 },
      artifactCount: precursor.verifiedInventory.artifactCount,
      artifactSetSha256: precursor.verifiedInventory.artifactSetSha256,
      signedInventorySha256: precursor.verifiedInventory.signedInventorySha256,
      governanceDomainState: precursor.verifiedInventory.governanceDomainState,
      noncePrefixSha256: precursor.verifiedNoncePrefix.noncePrefixSha256,
      occupiedNonces: [...precursor.verifiedNoncePrefix.occupiedNonces],
    }, { gateEffective: false, authorityRequired: ["genesis", "remote-acceptance"] });
  }
  assertClosedObject(rawArtifacts, ["profile", "remoteAuthorityInputs", "acceptanceReceiptPrefix", "initialBranchPolicyPin", "productionArtifacts", "operatorAcceptance"], "productionAuthorityArtifacts");
  if (rawArtifacts.profile !== "gate-evaluation") throw new TypeError("closed production-authority profile required");
  const authorityPrecursor = verifyRemoteAuthorityInputs(rawArtifacts.remoteAuthorityInputs);
  if (!REMOTE_AUTHORITY_PRECURSORS.has(authorityPrecursor)) {
    return Object.freeze({ errors: [diagnostic("authorityPrecursor", "unverified or forged precursor")], authorityRequired: ["production-authority-context"], gateEffective: false, authorityContext: null });
  }
  const artifactBinding = bindExactAuthorityArtifactDescriptors({
    derivedArtifacts: collectGateAuthorityArtifacts(rawArtifacts),
    suppliedArtifacts: rawArtifacts.remoteAuthorityInputs.nonceArtifacts,
    inventory: authorityPrecursor.verifiedInventory,
    expectedPhase: "gate-evaluation",
  });
  if (!PRODUCTION_ARTIFACT_BINDINGS.has(artifactBinding)) {
    return Object.freeze({ errors: artifactBinding.errors, authorityRequired: ["production-authority-context"], gateEffective: false, authorityContext: null });
  }
  const receipts = verifyAcceptanceReceipts({
    entries: rawArtifacts.acceptanceReceiptPrefix,
    branch: authorityPrecursor.branch,
    headCommit: authorityPrecursor.headCommit,
    headTreeOid: authorityPrecursor.headTreeOid,
    initialBranchPolicyPin: rawArtifacts.initialBranchPolicyPin,
    verifiedTransparency: authorityPrecursor.verifiedTransparency,
    verifiedBranchControls: authorityPrecursor.verifiedBranchControls,
    verifiedTrustedTime: authorityPrecursor.verifiedTrustedTime,
    verifiedNoncePrefix: artifactBinding.noncePrefix,
  });
  if (!isProductionAcceptanceResult(receipts)) {
    return Object.freeze({ errors: receipts.errors, authorityRequired: [...new Set([...(receipts.authorityRequired ?? []), "production-authority-context"])], gateEffective: false, authorityContext: null });
  }
  const productionCandidates = verifyProductionCandidateSet({
    artifacts: rawArtifacts.productionArtifacts,
    verifiedPins: authorityPrecursor.verifiedPins,
    verifiedTrustedTime: authorityPrecursor.verifiedTrustedTime,
    verifiedTransparency: authorityPrecursor.verifiedTransparency,
    verifiedFloors: authorityPrecursor.verifiedFloors,
    verifiedBranchControls: authorityPrecursor.verifiedBranchControls,
    verifiedNoncePrefix: artifactBinding.noncePrefix,
    verifiedArtifactBinding: artifactBinding,
    verifiedReceipts: receipts,
  });
  if (!isProductionCandidateSet(productionCandidates)) {
    return Object.freeze({ errors: productionCandidates.errors, authorityRequired: ["production-authority-context"], gateEffective: false, authorityContext: null });
  }
  const { g0GateRequested, ...operatorBindingCore } = productionCandidates.g0AcceptanceBindings;
  if (g0GateRequested !== true && rawArtifacts.operatorAcceptance !== null) {
    return Object.freeze({ errors: [diagnostic("operatorAcceptance", "operator acceptance is forbidden until GATE-G0 is the sole proposed green Gate")],
      authorityRequired: ["production-authority-context"], gateEffective: false, authorityContext: null });
  }
  const operatorAcceptance = verifyG0OperatorAcceptance(rawArtifacts.operatorAcceptance, {
    ...operatorBindingCore,
    repositoryId: authorityPrecursor.repositoryId,
    headCommit: authorityPrecursor.headCommit,
    headTreeOid: authorityPrecursor.headTreeOid,
    scope: "AURELIA-G0-GOVERNANCE-ACCEPTANCE",
    externalPinsSha256: authorityPrecursor.verifiedPins.externalPinsSha256,
    priorNoncePrefixSha256: artifactBinding.preAcceptanceNoncePrefixSha256,
    operatorIdentity: "redshift-three67",
    operatorRole: "ROLE-OPERATOR",
    operatorEpoch: operatorBindingCore.operatorEpoch,
    operatorKeyRef: operatorBindingCore.operatorKeyRef,
    operatorKeyFingerprint: operatorBindingCore.operatorKeyFingerprint,
    nonce: rawArtifacts.operatorAcceptance?.nonce,
    verifiedPins: authorityPrecursor.verifiedPins,
    verifiedTrustedTime: authorityPrecursor.verifiedTrustedTime,
    verifiedOperatorTrustedTime: productionCandidates.verifiedOperatorTrustedTime,
  });
  if (g0GateRequested === true && rawArtifacts.operatorAcceptance !== null
    && !PRODUCTION_G0_OPERATOR_ACCEPTANCES.has(operatorAcceptance)) {
    return Object.freeze({ errors: operatorAcceptance.errors, authorityRequired: ["g0-operator-acceptance"], gateEffective: false, authorityContext: null });
  }
  const claims = deepFreeze({
    repositoryId: authorityPrecursor.repositoryId,
    branch: authorityPrecursor.branch,
    headCommit: authorityPrecursor.headCommit,
    headTreeOid: authorityPrecursor.headTreeOid,
    pins: authorityPrecursor.verifiedPins.pins,
    externalPinsSha256: authorityPrecursor.verifiedPins.externalPinsSha256,
    trustedTime: {
      now: authorityPrecursor.verifiedTrustedTime.now,
      attestationSha256: authorityPrecursor.verifiedTrustedTime.attestationSha256,
    },
    transparency: {
      bundleSha256: authorityPrecursor.verifiedTransparency.bundleSha256,
      eventsByHash: asFrozenRecord(authorityPrecursor.verifiedTransparency.state.eventsByHash),
      evidenceById: asFrozenRecord(authorityPrecursor.verifiedTransparency.state.evidenceById),
      entriesByReceiptId: asFrozenRecord(authorityPrecursor.verifiedTransparency.state.entriesByReceiptId),
      checkpointsBySha256: asFrozenRecord(authorityPrecursor.verifiedTransparency.state.checkpointsBySha256),
      activeKeysByRef: asFrozenRecord(authorityPrecursor.verifiedTransparency.state.activeKeysByRef),
    },
    freshFloors: {
      challengeNonce: authorityPrecursor.verifiedFloors.challengeNonce,
      responsesSha256: authorityPrecursor.verifiedFloors.responsesSha256,
      minimumTreeSize: authorityPrecursor.verifiedFloors.minimumTreeSize,
      verifiedAt: authorityPrecursor.verifiedFloors.verifiedAt,
    },
    branchControls: authorityPrecursor.verifiedBranchControls.claims,
    acceptanceReceipts: {
      prefixSha256: receipts.prefixSha256,
      byId: asFrozenRecord(receipts.byId),
      acceptedRecordHashes: [...receipts.acceptedRecordHashes].sort((a, b) => (a < b ? -1 : a > b ? 1 : 0)),
      acceptedEventHashes: [...receipts.acceptedEventHashes].sort((a, b) => (a < b ? -1 : a > b ? 1 : 0)),
    },
    noncePrefixSha256: artifactBinding.noncePrefix.noncePrefixSha256,
    artifactCount: artifactBinding.inventory.artifactCount,
    artifactSetSha256: artifactBinding.inventory.artifactSetSha256,
    signedInventorySha256: artifactBinding.inventory.signedInventorySha256,
    governanceDomainState: artifactBinding.inventory.governanceDomainState,
    occupiedNonces: [...artifactBinding.noncePrefix.occupiedNonces],
    productionReplaySha256: productionCandidates.productionReplaySha256,
    g0AcceptanceBindings: operatorBindingCore,
    operatorAcceptance: operatorAcceptance.present ? operatorAcceptance.claims : null,
    operatorAcceptanceSha256: operatorAcceptance.present
      ? operatorAcceptance.fullArtifactSha256 : null,
  });
  return mintAuthorityContext("gate-evaluation", claims, g0GateRequested !== true || operatorAcceptance.present
    ? { gateEffective: true, authorityRequired: [] }
    : { gateEffective: false, authorityRequired: ["g0-operator-acceptance"] });

  function mintAuthorityContext(profile, profileClaims, status) {
    const authorityContext = Object.freeze(Object.create(null));
    PRODUCTION_AUTHORITY_CLAIMS.set(authorityContext, deepFreeze({
      ...profileClaims,
      profile,
      gateEffective: status.gateEffective,
      authorityRequired: [...status.authorityRequired],
    }));
    const result = Object.freeze({ errors: [], authorityRequired: Object.freeze([...status.authorityRequired]), gateEffective: status.gateEffective, authorityContext });
    if (profile === "gate-evaluation" && status.gateEffective === true) PRODUCTION_AUTHORITY_RESULTS.add(result);
    return result;
  }
}

export function requireProductionAuthorityResult(result) {
  if (!PRODUCTION_AUTHORITY_RESULTS.has(result) || !result.gateEffective) throw new TypeError("fully verified production-authority result required");
  return result;
}
```

`verifyAcceptanceReceipts` itself adds a result to `PRODUCTION_ACCEPTANCE_RESULTS` only after its non-injectable production replay has zero errors, `authorityRequired:["production-authority-context"]`, `cryptographicValid:true`, `fullPrefixVerified:true`, and `gateEffective:false`; the semantic facade never does so. The issuer consumes that expected pending authority together with the branded precursor and is the only code that removes it. A source-import allowlist permits `isProductionAcceptanceResult` only in `production-authority-context.mjs` and its test. `readProductionAuthorityContext` returns the frozen claims only for a WeakMap-branded context and throws for every other value. Add a source test proving that `verifyProductionAuthorityContext` is the only occurrence of `PRODUCTION_AUTHORITY_CLAIMS.set`. Add forgery tests for plain precursor, plain Receipt result, copied context, copied aggregate result, raw pins, raw time string, raw replay maps, omitted nonce domain, and a valid receipt from a noncurrent policy epoch.

`verifyProductionCandidateSet` is Phase A, not an authority shortcut. Inside the issuer it calls the non-injectable Plans 05–10 production wrappers on `productionArtifacts` and accepts only their module-private branded results with `cryptographicValid:true` and/or `semanticValid:true`, complete-prefix/inventory bindings, zero diagnostics, the expected `authorityRequired:["production-authority-context"]`, and `gateEffective:false`. It never accepts caller-supplied verifier results, replay maps, pins, `now`, booleans, callbacks, or a semantic test facade. The wrappers receive only the issuer's already branded pin/time/transparency/floor/branch/Nonce/Receipt subresults; none may independently become gate-effective. `isProductionCandidateSet` is module-private and brands the aggregate digest of the closed Plan-05, recovery, TCB, External-LLM/Egress, and Collector candidates and exposes one closed `g0AcceptanceBindings` record derived from those verified bytes. That record contains `g0GateRequested` plus exact `implementationCommit/designCommit/designSpecSha256/pathManifestSha256/finalGateVectorSha256/finalLocalGateReportSha256/tcbStateSha256/branchPolicySha256/operatorEpoch/operatorKeyRef/operatorKeyFingerprint/trustedTimeAttestationSha256/approvedAt`; it is never caller supplied. For a sole-green proposal, `verifiedOperatorTrustedTime` is produced only by re-running the non-injectable production Trusted-Time verifier on `productionArtifacts.operatorTrustedTimeAttestation`, checking its canonical full hash and bytes against the accepted-base artifact preserved by the proposal runner, and proving it precedes the Operator descriptor. For all-red candidates that field is null and no historical brand exists. `approvedAt` and its full hash come only from that brand. Final evaluation additionally proves that the independently verified current protected time is not earlier and approval age is at most 24 hours. `g0GateRequested:true` is valid only when `GATE-G0` is the sole proposed green Gate and the other eight equal the frozen red vector. Phase B executes exactly one WeakMap write through `mintAuthorityContext`: the pre-Genesis profile remains non-gate. A fully verified `gate-evaluation` candidate with `g0GateRequested:false` may be effective without a G0 operator artifact so Genesis and intermediate all-red heads can be remotely accepted. The sole-green G0 candidate is minted non-effective with `authorityRequired:["g0-operator-acceptance"]` until the exact operator artifact, refreshed inventory, Receipt/checkpoint, and floors verify; only then does the result enter `PRODUCTION_AUTHORITY_RESULTS`. Plan 04 needs only that aggregate context and must not rerun or trust any raw Phase-A state.

For `g0GateRequested:true`, Phase A also runs the non-injectable
`verifyCommittedG0ProposalReport`. It accepts only the actual
`productionArtifacts.g0GateProposalReport`, requires its committed form, and
recomputes from the immutable target Git object: repository ID, base and target
Commit/Tree, strict First-Parent ancestry, complete `I..target` code-unit-sorted
path/mode/blob manifest, its SHA-256, and the final register Gate vector. From
the verified Receipt/checkpoint prefix it locates the report's exact accepted
all-red base and recomputes `authoritySnapshotSha256`; from the report bytes it
computes `finalLocalGateReportSha256`. These derived values—not fields copied
from the report—populate `g0AcceptanceBindings`. The report must precede the
Operator Acceptance in the chronological descriptor prefix and be covered by
the refreshed signed inventory's `evidence` domain. All-red candidates require
the report field to be null. Mutation tests cover stale Working-Tree reports,
target/base swap, report reserialization, omitted path, mode/blob drift,
non-first-parent base, stale base Receipt/checkpoint, wrong final vector, and a
report absent from the inventory.

`deepFreeze` recursively freezes only closed plain objects/arrays and rejects Map, Set, Date, functions, accessors, prototypes other than `null|Object.prototype`, and cycles. Every verifier Map/Set is converted to a code-unit-sorted plain record/array before claims are stored. Thus downstream never receives a mutable raw replay state, verifier result, pin input, or receipt Set/Map. `externalPinsSha256`, `signedInventorySha256`, `artifactSetSha256`, `noncePrefixSha256`, `bundleSha256`, `prefixSha256`, Head, and Tree bind the complete authority snapshot. The claims include the issuer-controlled `gateEffective` and `authorityRequired`; callers cannot supply or override either field.

The cross-plan Operator claim ABI is flat and singular:
`claims.operatorAcceptance` is either null or the exact deep-frozen verified
unsigned core fields; `claims.operatorAcceptanceSha256` is either null or the
full signed artifact hash. It is never wrapped in a nested `claims` object.
Plan 04 consumes those exact two fields and also matches the signed inventory
domain head. A contract test runs the real Plan-04 GATE-G0 consumer against the
real Plan-11 issuer and rejects a nested-wrapper regression.

- [ ] **Step 4: Run tests and commit**

```powershell
node --test scripts/governance/remote-receipts.test.mjs scripts/governance/production-authority-context.test.mjs
git add scripts/governance/remote-receipts.mjs scripts/governance/remote-receipts.test.mjs scripts/governance/remote-bundle.mjs scripts/governance/remote-bundle.test.mjs scripts/governance/production-authority-context.mjs scripts/governance/production-authority-context.test.mjs scripts/fixtures/governance/remote/valid-receipt-prefix.json scripts/fixtures/governance/remote/policy-transition-prefix.json
git commit -m "feat: replay remote acceptance receipts"
```

Expected: PASS and a focused commit.

### Task 4: Enforce marker namespace and tombstone-backed replay safety

**Files:**
- Create: `scripts/governance/remote-recovery-controls.mjs`
- Create: `scripts/governance/remote-recovery-controls.test.mjs`
- Create: `scripts/fixtures/governance/remote/marker-policy-observation.json`
- Create: `scripts/fixtures/governance/remote/a-b-a-tombstone-prefix.json`

- [ ] **Step 1: Write failing recovery-control tests**

Accept only create-only marker refs matching `refs/heads/aurelia-recovery-markers/<64 lowercase hex>`, target equal to the recovery target OID, gateway-only create authority, and no update/delete/force/bypass. Prove that operation correlation ID, provider idempotency digest, marker ref, and provider request hash each have independent uniqueness in the external tombstone prefix. Delete and recreate the marker in the synthetic remote observation after A->B->A and assert a second egress remains rejected by the tombstone.

- [ ] **Step 2: Run and record RED**

```powershell
node --test scripts/governance/remote-recovery-controls.test.mjs
```

Expected: FAIL because `verifyMarkerPolicy` and `verifyTombstoneUniqueness` are absent.

- [ ] **Step 3: Implement fail-closed policy and prefix checks**

```js
export function verifyMarkerPolicy({ observation, authorityContext }) {
  const verified = readProductionAuthorityContext(authorityContext);
  const errors = [];
  if (observation.createActor !== verified.pins.recoveryWriteAheadGateway.serviceIdentity) errors.push(diagnostic("createActor", "marker creator is not externally pinned gateway"));
  if (observation.rulesSha256 !== verified.branchControls.rulesSha256 || observation.observedAt !== verified.branchControls.observedAt) errors.push(diagnostic("branchControls", "marker observation is not bound to verified branch-control bytes/time"));
  for (const field of ["updateAllowed", "deleteAllowed", "forceAllowed", "bypassAllowed"]) {
    if (observation[field] !== false) errors.push(diagnostic(field, "marker namespace is mutable or bypassable"));
  }
  return errors;
}
```

The production wrapper accepts only the module-private `ProductionAuthorityContext`, which already binds signed bytes, trusted-time freshness, complete visible bypass set, create-only namespace rules, repository/branch, externally pinned signer, full Nonce replay, and the current Acceptance-Receipt prefix. A plain object, raw pin set, raw branch-control result, or feasibility-probe verdict fails before field access. The remote snapshot never supplies the gateway pin or idempotency guarantee; only the capability and the full checkpointed tombstone log prefix can authorize the first and only egress.

- [ ] **Step 4: Run tests and commit**

```powershell
node --test scripts/governance/remote-recovery-controls.test.mjs
git add scripts/governance/remote-recovery-controls.mjs scripts/governance/remote-recovery-controls.test.mjs scripts/fixtures/governance/remote/marker-policy-observation.json scripts/fixtures/governance/remote/a-b-a-tombstone-prefix.json
git commit -m "feat: verify remote recovery controls"
```

Expected: PASS; hidden or absent bypass data remains an error rather than false.

### Task 5: Add the offline remote CLI without adding live I/O

**Files:**
- Create: `scripts/governance-remote-contract.mjs`
- Create: `scripts/governance-remote-contract.test.mjs`
- Create: `scripts/governance-g0-proposal.mjs`
- Create: `scripts/governance-g0-proposal.test.mjs`
- Modify: `scripts/governance-contract.mjs`
- Modify: `package.json`
- Create: `docs/governance/remote-validator-interface.md`

- [ ] **Step 1: Write a failing CLI test**

Invoke the CLI in explicit `--test-only` mode with semantic fixtures and a fixture Trusted-Time history supplied through the same `--trusted-time-history` flag; expect `TEST-ONLY-NON-GATE` and a non-gate success code distinct from production acceptance. `--test-now`, `--now`, `--trusted-time`, or any raw time string is an unknown argument. Invoke the production wrapper with dummy/synthetic signatures and expect exit 1. Also expect exit 1 for missing external pins, stale checkpoint/floors, hidden bypass data, incomplete Nonce replay, a missing Acceptance-Receipt prefix, an omitted/reordered historical control, a reused historical Time/Floor/Branch-Control Nonce, a sole-green G0 candidate without `--operator-acceptance` or `--operator-trusted-time`, an operator artifact or historical Operator Trusted-Time on an all-red head, historical/current substitution, accepted-base byte/hash drift, reversed Trusted-Time chronology, approval age over 24 hours, or an operator artifact absent from the refreshed inventory/Nonce stream. Assert that source imports contain none of `fetch(`, `https.request`, `child_process`, `octokit`, or `gh api`.

Test the separate G0 proposal CLI in both Working-Tree and committed-target forms. It requires exact `--base`, exactly one of `--working-tree|--head`, `--external-pins`, `--accepted-base-remote-bundle`, and optional external `--report-out`. The bundle must mint a gate-effective all-red context bound to the exact immutable base Commit/Tree with `operatorAcceptance:null`. It then runs Plan 03's structural replay and Plan 04's `validateG0GateProposal`, emits a canonical report, and always returns `LOCAL-GATE-PROPOSAL-ONLY`, `gateEffective:false`, with both external authorities pending. Reject a green base, non-G0 change, copied context/proposal result, base-bundle Head mismatch, extra field, Working-Tree report reused after commit, report path inside the repository, or any attempt to pass the result to an effective Gate guard.

- [ ] **Step 2: Run and record RED**

```powershell
node --test scripts/governance-remote-contract.test.mjs scripts/governance-g0-proposal.test.mjs
```

Expected: FAIL because both CLIs do not exist.

- [ ] **Step 3: Implement explicit file-input CLI**

Use this production invocation contract:

```text
node scripts/governance-remote-contract.mjs --profile gate-evaluation --bundle bundle.json --pins external-pins.json --branch-control-history branch-control-history.json --floor-challenge-history floor-challenge-history.json --floor-response-history floor-response-history.json --trusted-time-history trusted-time-history.json --acceptance-receipts acceptance-receipts.json --initial-branch-policy-pin initial-branch-policy-pin.json --signed-artifact-inventory signed-artifact-inventory.json --nonce-artifacts nonce-artifacts.json --production-artifacts production-artifacts.json --operator-trusted-time operator-signing-trusted-time-attestation.json --operator-acceptance g0-operator-acceptance.json --head 0123456789abcdef0123456789abcdef01234567 --tree 89abcdef0123456789abcdef0123456789abcdef
```

The OIDs shown above are parser-test examples only and always produce `gateEffective: false`; a real run passes the actual externally observed OIDs. The implementation must parse each flag exactly once, read only those files, call the sole issuer with the closed `profile:"gate-evaluation"` discriminant, require `requireProductionAuthorityResult`, print structured diagnostics, and never call the network. The assembled aggregate has exactly `profile/remoteAuthorityInputs/acceptanceReceiptPrefix/initialBranchPolicyPin/productionArtifacts/operatorAcceptance`. The four history flags each carry the corresponding complete raw append-only JSON array; the CLI rejects a singleton object, a history omitted after its first appearance, and any history whose tail is not the current control. `productionArtifacts` itself is a closed object whose exact Plan-05–10 fields are followed by `g0GateProposalReport` and `operatorTrustedTimeAttestation`; those last two are both non-null only for the sole-green G0 candidate and literal null for all-red Heads. `--operator-acceptance` and `--operator-trusted-time` are mandatory together only when the verified candidate has `GATE-G0` as its sole green Gate. The CLI parses the latter into `productionArtifacts.operatorTrustedTimeAttestation` and requires canonical byte equality with the corresponding already present historical member in `--trusted-time-history` and the same nested value already present in `--production-artifacts`; every earlier all-red Head maps both operator-specific fields to literal `null`, and passing either artifact there is rejected. The last `--trusted-time-history` member is always the independent current attestation. `--signed-artifact-inventory` is mandatory in both profiles and its exact envelope must also be the single `inventoryMember:false` descriptor in `--nonce-artifacts`. The separate `pre-genesis-ceremony` invocation requires only `--profile pre-genesis-ceremony --repository-root <path> --implementation-commit <full-sha> --signed-artifact-inventory <file> --ceremony-artifacts <file> --pins <file> --trusted-time-history <file> --nonce-artifacts <file>`; it must return exit 1/`AUTHORITY-PENDING` because its context is deliberately non-gate-effective, while remaining consumable in-process by Plan 12. `--ceremony-artifacts` is a closed JSON array and is never synthesized from the descriptor stream. Test mode uses `--test-only --trusted-time-history scripts/fixtures/governance/remote/test-trusted-time-history.json`; the semantic Trusted-Time history verifier marks it `TEST-ONLY-NON-GATE`, and no raw-clock flag exists. Add package script:

```json-fragment
"check:governance-remote": "node scripts/governance-remote-contract.mjs",
"check:governance-g0-proposal": "node scripts/governance-g0-proposal.mjs"
```

`governance-g0-proposal.mjs` is an offline, read-only proposal runner, not a
third authority profile or effective Gate mode. It calls the concrete Plan-11
issuer only for the already accepted all-red base, never for the Working Tree
or proposed target. The module-private Plan-03 proposal runner binds that
context to the base Commit/Tree, binds the target to either the current
Working-Tree path/hash manifest or the explicit target Commit/Tree, and calls
only Plan 04's non-effective proposal API. The committed-target report contains
exactly
`repositoryId/baseCommit/baseTreeOid/targetCommit/targetTreeOid/pathManifestSha256/finalGateVectorSha256/authoritySnapshotSha256/validatedAt/status/gateEffective/authorityRequired`;
the Working-Tree report has `targetCommit:null,targetTreeOid:null` and is never
signable. `validatedAt` comes from the accepted-base authority Trusted-Time,
not a local clock. The CLI writes only to an explicit `--report-out` path after
resolving that it is outside the repository root; otherwise it prints canonical
bytes to stdout. It never writes a repository file, signs, calls the network,
or mints an authority context. Plan 13 reruns the committed form after creating
the local candidate commit and uses that exact report hash in the Operator
signing request.

The same module owns private `COMMITTED_G0_PROPOSAL_REPORTS` and
`VERIFIED_PRE_ACCEPTANCE_PREFIXES` WeakSets and the only unsigned-core builder.
The Working-Tree form is never added. For the committed form, the runner takes
the verified accepted-base descriptor prefix, restores its latest inventory as
the sole excluded envelope, then appends every actual candidate record/Event,
detached Event Attestation, evidence/manifest artifact, and the committed
proposal report in canonical append order. It reruns Plan 06's verifier with
no Operator Acceptance and no refreshed current inventory, brands the resulting
zero-error prefix, and proves every new candidate Nonce is fresh relative to
the base. It also preserves the exact raw accepted-base Trusted-Time artifact,
proves its canonical full hash equals `base.trustedTime.attestationSha256`,
includes it before the Operator descriptor, and emits its bytes/hash in the
protected external signing-request handoff; it never substitutes a later
attestation. After both committed report and pre-acceptance prefix pass, the runner may accept an external
`--operator-input` file with exactly `acceptanceId` and one canonical 32-byte
Base64url `nonce`, plus an external
`--operator-signing-request-out` path. Both output paths must resolve outside
the repository. It then calls:

```js
export function buildG0OperatorAcceptanceCore({
  committedProposalResult, acceptedBaseAuthorityContext, operatorInput,
}) {
  if (!COMMITTED_G0_PROPOSAL_REPORTS.has(committedProposalResult))
    throw new TypeError("verified committed G0 proposal required");
  const base = readProductionAuthorityContext(acceptedBaseAuthorityContext);
  if (base.profile !== "gate-evaluation" || base.gateEffective !== true
    || base.operatorAcceptance !== null
    || base.headCommit !== committedProposalResult.report.baseCommit
    || base.headTreeOid !== committedProposalResult.report.baseTreeOid)
    throw new TypeError("exact accepted all-red base authority required");
  assertClosedObject(operatorInput, ["acceptanceId", "nonce"], "operatorInput");
  assertBase64urlBytes(operatorInput.nonce, 32, "operatorInput.nonce");
  const preAcceptance = committedProposalResult.verifiedPreAcceptancePrefix;
  if (!VERIFIED_PRE_ACCEPTANCE_PREFIXES.has(preAcceptance))
    throw new TypeError("verified complete pre-acceptance prefix required");
  if (preAcceptance.occupiedNonces.includes(operatorInput.nonce))
    throw new Error("operator acceptance nonce already occupied");
  const bindings = committedProposalResult.g0AcceptanceBindings;
  return Object.freeze({
    schemaVersion: "aurelia-governance-v1",
    acceptanceId: operatorInput.acceptanceId,
    repositoryId: "redshift-three67/aurelia",
    headCommit: committedProposalResult.report.targetCommit,
    headTreeOid: committedProposalResult.report.targetTreeOid,
    implementationCommit: bindings.implementationCommit,
    designCommit: bindings.designCommit,
    designSpecSha256: bindings.designSpecSha256,
    scope: "AURELIA-G0-GOVERNANCE-ACCEPTANCE",
    pathManifestSha256: committedProposalResult.report.pathManifestSha256,
    finalGateVectorSha256: committedProposalResult.report.finalGateVectorSha256,
    finalLocalGateReportSha256: fullArtifactSha256(committedProposalResult.report),
    tcbStateSha256: bindings.tcbStateSha256,
    branchPolicySha256: bindings.branchPolicySha256,
    externalPinsSha256: base.externalPinsSha256,
    priorNoncePrefixSha256: preAcceptance.noncePrefixSha256,
    operatorIdentity: "redshift-three67", operatorRole: "ROLE-OPERATOR",
    operatorEpoch: bindings.operatorEpoch, operatorKeyRef: bindings.operatorKeyRef,
    operatorKeyFingerprint: bindings.operatorKeyFingerprint,
    trustedTimeAttestationSha256: base.trustedTime.attestationSha256,
    approvedAt: base.trustedTime.now, nonce: operatorInput.nonce,
  });
}
```

The runner validates the returned core against `g0-operator-acceptance` with
only `signature` absent, emits exactly
`{core,payloadSha256,payloadBase64url,operatorTrustedTimeAttestation,operatorTrustedTimeAttestationSha256,status:"OPERATOR-SIGNATURE-PENDING",gateEffective:false}`,
and computes both encodings from `canonicalBytes(core)`. The final Plan-11
collector must derive a byte-identical pre-Operator replay digest and occupied
set before it can verify the returned signed artifact. It never generates a
Nonce, key, signature, time, acceptance ID, or authority. A second build from
the same inputs must be byte-identical. Tests mutate each report/base/core
binding, omit/swap a candidate Event or detached attestation, collide with the
GATE-G0 Event-attestation Nonce, use an occupied/reused Nonce, copied proposal/context, Working-Tree
result, nonexternal output path, or local clock; every case fails before bytes
are released.

`remote-validator-interface.md` states that the authoritative producer is an immutable validator outside the AURELIA PR/head, using externally pinned image/policy/workflow/schema/trust-protocol digests. It must explicitly distinguish Task-1 feasibility output from signed gate evidence.

This remote-only CLI does not introduce a fifth Governance mode. Its explicit component files are assembled into the exact closed `rawArtifacts` aggregate shown in Task 3 and passed directly to the sole issuer in the same process. Integration with `scripts/governance-contract.mjs` follows Plan 03's frozen discriminant exactly: only `production-commit-range` (`--base`, `--head`, `--external-pins`, `--remote-bundle`) may load a target aggregate with exactly `profile/remoteAuthorityInputs/acceptanceReceiptPrefix/initialBranchPolicyPin/productionArtifacts/operatorAcceptance`, rerun `verifyProductionAuthorityContext` in that CLI process, and consume claims via `readProductionAuthorityContext(result.authorityContext)` after `requireProductionAuthorityResult(result)`. A serialized context or result is never placed in `--remote-bundle` and cannot survive the WeakMap boundary. Pre-Genesis and the two ordinary local-preflight modes never call the issuer and remain non-gate-effective. The separate G0 proposal runner may mint only the exact accepted all-red **base** context, immediately confines it to `validateG0GateProposal`, and still returns no capability or Gate effect for its target. The adapter hashes the complete canonical pin file named by Plan 03's existing `--external-pins` argument and requires byte equality with `claims.externalPinsSha256` and the aggregate's embedded signed pin set; it never uses those raw pin values as authority. It accepts no callback, boolean, status string, raw time, or caller-supplied verifier result. Tests prove the explicit remote CLI and main Governance adapter produce the same authority snapshot digests from the same artifacts, reject every extra/missing aggregate field, and reject a copied/serialized authority object.

- [ ] **Step 4: Run CLI tests and commit**

```powershell
node --test scripts/governance-remote-contract.test.mjs scripts/governance-g0-proposal.test.mjs
git add scripts/governance-remote-contract.mjs scripts/governance-remote-contract.test.mjs scripts/governance-g0-proposal.mjs scripts/governance-g0-proposal.test.mjs scripts/governance-contract.mjs package.json docs/governance/remote-validator-interface.md
git commit -m "feat: add offline remote governance check"
```

Expected: PASS; source scan confirms no live I/O.

### Task 6: Review and close Plan 11

**Files:** No intended source changes.

- [ ] **Step 1: Run sequential local gates**

```powershell
npm run check:canon
npm run typecheck:governance
npm run typecheck
npm run lint
npm test
if ($env:AURELIA_PLAN11_BASE_SHA -notmatch '^[0-9a-f]{40}$') { throw 'AURELIA_PLAN11_BASE_SHA missing from execution record' }
git diff --check "$env:AURELIA_PLAN11_BASE_SHA..HEAD"
```

Expected: each listed command exits 0. `npm run check:governance` and `npm run check:governance-remote` cannot exit 0 against the real repository before Genesis and real externally signed inputs; they must report `AUTHORITY-RED` rather than consume fixtures.

- [ ] **Step 2: Perform independent Spec Review**

Review design sections 6.3, 6.4, 12.5, and 13. Expected: approved with no open P0-P2 and explicit confirmation that authoritative observation is outside the PR head.

- [ ] **Step 3: Perform independent Quality/Security Review**

Attack hidden bypass actors, unavailable private-repo controls, stale checkpoint/floors, split view, partial prefix, old policy epoch, fake external pin, marker delete/recreate, A->B->A replay, alias repository, and a network import added to the offline CLI. Expected: approved with no open P0-P2.

- [ ] **Step 4: Re-review corrections**

For every finding, write and run the focused RED test, implement the minimal correction, commit with `fix: close remote governance review finding`, and repeat both reviews for the affected scope.

- [ ] **Step 5: Record the remote boundary**

The handoff records the capability verdict separately. A PASS means only that required fields were observable read-only; it is not an Acceptance-Receipt. A STOP remains formal `unknown/red` and forbids Genesis/G0 green until resolved. No permissions, branch settings, refs, commits, or server state were changed by this plan.
