# AURELIA K1 Task-3 String/Type-Bypass Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close `K1-T3-P1-01-STRING-TYPE-BYPASS` without losing real credential findings, widening the TypeScript exception, or changing the scanner's public contract.

**Architecture:** Find named credential candidates in the unchanged raw text and attach exact UTF-16 positions. For `.ts` and `.tsx` only, suppress one candidate only when the existing TypeScript parser proves that the positions belong to an allowlisted `PropertySignature`; every loader, parser, syntax, or position ambiguity retains the raw finding.

**Tech Stack:** Node.js 22 ESM, Node Test Runner, existing TypeScript dependency, PowerShell, Git.

---

## 0. Fixed execution contract

This plan is documentation only until a separate operator authorization starts
implementation.

| Boundary | Required value |
|---|---|
| Branch | `codex/aurelia-konsolidierung` |
| Start checkpoint | `e930aab2643c376ddd9090a66be31c52d32f05ee` |
| Required ancestor | `8706186af01e10e4253e25abb31bf3577110dae4` |
| Design | `docs/superpowers/specs/2026-08-26-aurelia-k1-task3-string-type-bypass-design.md` |
| Design SHA-256 | `9c0e05adf870d40ff1686863fe866dd61e73ef6dbc63e680ffb363611f73323e` |
| Finding | `K1-T3-P1-01-STRING-TYPE-BYPASS` |
| Risk route | B — Critical Assurance |
| Data class | synthetic only |
| Push | forbidden |
| Server access | forbidden |
| History rewrite | forbidden |
| Task 4 | blocked until Task-3 Spec-PASS and Quality-PASS |

The implementation surface is exactly:

- `scripts/check-push-graph.test.mjs`
- `scripts/check-push-graph.mjs`

The following remain unchanged during implementation:

- `package.json`;
- `package-lock.json`;
- `docs/project-control/K1-STATUS.md`;
- V3 evidence and all analysis `source/` directories;
- product, server and Task-4 files;
- public exports, CLI arguments and exit semantics.

Any later `K1-STATUS.md` update is a separate, explicitly authorized evidence
action after both reviews PASS.

### Task 1: Verify the fixed baseline and design identity

**Files:**
- Read: `docs/superpowers/specs/2026-08-26-aurelia-k1-task3-string-type-bypass-design.md`
- Read: `scripts/check-push-graph.mjs`
- Test: `scripts/check-push-graph.test.mjs`

- [ ] **Step 1: Verify branch, clean state, ancestry and start checkpoint**

```powershell
$ErrorActionPreference = "Stop"

$branch = git branch --show-current
if ($LASTEXITCODE -ne 0 -or $branch -cne "codex/aurelia-konsolidierung") {
  throw "K1_T3_AST_BRANCH_MISMATCH"
}

$state = @(git status --porcelain=v1)
if ($LASTEXITCODE -ne 0 -or $state.Count -ne 0) {
  throw "K1_T3_AST_WORKTREE_NOT_CLEAN"
}

git merge-base --is-ancestor 8706186af01e10e4253e25abb31bf3577110dae4 HEAD
if ($LASTEXITCODE -ne 0) { throw "K1_T3_AST_REQUIRED_ANCESTOR_MISSING" }

git merge-base --is-ancestor e930aab2643c376ddd9090a66be31c52d32f05ee HEAD
if ($LASTEXITCODE -ne 0) { throw "K1_T3_AST_START_CHECKPOINT_MISSING" }

git ls-files --error-unmatch -- `
  docs/superpowers/specs/2026-08-26-aurelia-k1-task3-string-type-bypass-design.md `
  docs/superpowers/plans/2026-08-26-aurelia-k1-task3-string-type-bypass.md
if ($LASTEXITCODE -ne 0) { throw "K1_T3_AST_DOCUMENT_CHECKPOINT_MISSING" }
```

Expected: the branch is printed and all assertions exit 0. The documentation
must already have its own separately authorized local checkpoint; its future
commit ID is deliberately not predicted in this plan.

- [ ] **Step 2: Verify the approved design content, not a predicted commit hash**

```powershell
$design = "docs/superpowers/specs/2026-08-26-aurelia-k1-task3-string-type-bypass-design.md"
$digest = (Get-FileHash -Algorithm SHA256 -LiteralPath $design).Hash.ToLowerInvariant()
if ($digest -cne "9c0e05adf870d40ff1686863fe866dd61e73ef6dbc63e680ffb363611f73323e") {
  throw "K1_T3_AST_DESIGN_DIGEST_MISMATCH"
}
```

Expected: exit 0. A mismatch stops implementation for design reconciliation.

- [ ] **Step 3: Run the unchanged baseline**

```powershell
node --test scripts/check-push-graph.test.mjs
if ($LASTEXITCODE -ne 0) { throw "K1_T3_AST_BASELINE_TESTS_FAILED" }

npm run check:k1-control
if ($LASTEXITCODE -ne 0) { throw "K1_T3_AST_BASELINE_CONTROL_FAILED" }
```

Expected at `e930aab`: 19 scanner tests pass and K1 control exits 0.

### Task 2: Specify the bypass and all fail-closed boundaries as RED tests

**Files:**
- Modify: `scripts/check-push-graph.test.mjs`
- Test: `scripts/check-push-graph.test.mjs`

- [ ] **Step 1: Add one fixture builder with no literal credential assignment in test source**

Insert after `syntheticUnquotedPreviewSecret()`:

```javascript
function syntheticTypeShapedCredential() {
  const name = ["PREVIEW", "CLIENT", "SECRET"].join("_");
  const value = ["Synthetic", "Scanner", "Credential", "Value"].join("");
  const property = `${name}: ${value};`;
  const typeBlock = `type Config = { ${property} }`;
  const interfaceBlock = `interface Config { ${property} }`;
  return { name, value, property, typeBlock, interfaceBlock };
}

function credentialCategories(repositoryPath, content) {
  return classifyBlob(repositoryPath, Buffer.from(content)).map(
    (finding) => finding.category,
  );
}
```

- [ ] **Step 2: Add the reproduced string, template and comment bypass tests**

Insert after the existing TypeScript property-signature test:

```javascript
test("classifyBlob keeps type-shaped credentials visible in strings", () => {
  const { typeBlock, interfaceBlock, value } = syntheticTypeShapedCredential();
  const fixtures = [
    `const sample = ${JSON.stringify(typeBlock)};`,
    `const sample = '${interfaceBlock}';`,
    ["const sample = `", typeBlock, "`;"].join(""),
    ["const sample = `prefix ${", JSON.stringify("safe"), "} ", typeBlock, "`;"].join(""),
  ];

  for (const source of fixtures) {
    const findings = classifyBlob("src/string.ts", Buffer.from(source));
    assert.deepEqual(
      findings.map((finding) => finding.category),
      ["credential_like"],
    );
    assert.equal(JSON.stringify(findings).includes(value), false);
    assert.equal(JSON.stringify(findings).includes(source), false);
  }
});

test("classifyBlob keeps type-shaped credentials visible in comments", () => {
  const { typeBlock, interfaceBlock } = syntheticTypeShapedCredential();
  const fixtures = [
    `// ${typeBlock}`,
    `/* ${interfaceBlock} */`,
    `/* quoted \"${typeBlock}\" and braced { ${interfaceBlock} } */`,
  ];

  for (const source of fixtures) {
    assert.deepEqual(
      credentialCategories("src/comment.ts", source),
      ["credential_like"],
    );
  }
});
```

- [ ] **Step 3: Add exact safe-signature and mixed-context tests**

```javascript
test("classifyBlob suppresses only exact allowlisted property signatures", () => {
  const { name, value, property, typeBlock, interfaceBlock } =
    syntheticTypeShapedCredential();
  const qualified = ["Types", value].join(".");
  const fixtures = [
    typeBlock,
    interfaceBlock,
    `type Config = { ${name}: ${qualified}; }`,
    `type Outer = { nested: { ${property} }; }`,
  ];

  for (const source of fixtures) {
    assert.deepEqual(classifyBlob("src/types.ts", Buffer.from(source)), []);
  }
});

test("classifyBlob never suppresses runtime or ambiguous TypeScript contexts", () => {
  const { name, value, property, typeBlock } = syntheticTypeShapedCredential();
  const fixtures = [
    `const config = { ${name}: ${value}, };`,
    `class Config { ${property} }`,
    `function read(${name}: ${value}) { return true; }`,
    `${name} = ${value};`,
    `type Broken = { ${property}`,
    `type Literal = { ${name}: \"${value}\"; }`,
    `const sample = ${JSON.stringify(typeBlock)}; ${name}: ${value}`,
  ];

  for (const source of fixtures) {
    assert.ok(
      credentialCategories("src/runtime.ts", source).includes("credential_like"),
    );
  }
});
```

The class-field and parameter fixtures deliberately remain fail-closed even
when they resemble type syntax. Only `PropertySignature` under an interface or
type literal is allowlisted.

- [ ] **Step 4: Add extension, position and count boundaries**

```javascript
test("classifyBlob scopes AST suppression to ts and tsx", () => {
  const { typeBlock } = syntheticTypeShapedCredential();
  for (const path of [
    "src/types.js",
    "src/types.mjs",
    "src/types.mts",
    "src/types.cts",
    "notes/types.txt",
  ]) {
    assert.deepEqual(
      credentialCategories(path, typeBlock),
      ["credential_like"],
    );
  }
  assert.deepEqual(classifyBlob("src/types.ts", Buffer.from(typeBlock)), []);
  assert.deepEqual(classifyBlob("src/types.tsx", Buffer.from(typeBlock)), []);
});

test("classifyBlob maps each AST signature to only its exact candidate", () => {
  const { name, value, property, typeBlock } = syntheticTypeShapedCredential();
  const runtime = `${name}: ${value}`;
  const source = [
    "// unicode-prefix-ä",
    typeBlock,
    `const sample = ${JSON.stringify(typeBlock)};`,
    `const config = { ${runtime}, };`,
    `type Outer = { nested: { ${property} }; }`,
  ].join("\r\n");

  const findings = classifyBlob("src/mixed.ts", Buffer.from(source));
  assert.deepEqual(
    findings.map((finding) => [finding.category, finding.count]),
    [["credential_like", 2]],
  );
});
```

- [ ] **Step 5: Run the focused matrix and prove RED**

```powershell
node --test --test-name-pattern="type-shaped|allowlisted property|runtime or ambiguous|AST suppression|exact candidate" scripts/check-push-graph.test.mjs
```

Expected on `e930aab` with only the new tests applied:

- string and comment cases fail because raw fake type blocks are removed;
- mixed-context count fails for the same reason;
- already-supported simple property signatures may pass;
- the command exits nonzero for the intended missing behavior, not for syntax
  or fixture errors.

- [ ] **Step 6: Verify the RED diff and create a local test checkpoint only when separately authorized**

```powershell
git diff --check
if ($LASTEXITCODE -ne 0) { throw "K1_T3_AST_RED_DIFF_INVALID" }

git diff --name-only
```

Expected scope: only `scripts/check-push-graph.test.mjs`.

If a later authorization explicitly permits local implementation commits:

```powershell
git add -- scripts/check-push-graph.test.mjs
git diff --cached --check
if ($LASTEXITCODE -ne 0) { throw "K1_T3_AST_RED_INDEX_INVALID" }
git commit -m "test(security): reproduce scanner string type bypass"
```

No push is permitted.

### Task 3: Replace block masking with candidate positions

**Files:**
- Modify: `scripts/check-push-graph.mjs:1-55`
- Modify: `scripts/check-push-graph.mjs:117-133`
- Test: `scripts/check-push-graph.test.mjs`

- [ ] **Step 1: Add the synchronous lazy loader and candidate pattern**

Add the import and replace the named assignment entry in
`CREDENTIAL_PATTERNS` with a dedicated position-aware pattern:

```javascript
import { createRequire } from "node:module";

const requireModule = createRequire(import.meta.url);
const CREDENTIAL_NAME_PATTERN_SOURCE =
  "(?:api[_-]?key|access[_-]?token|client[_-]?secret|password|passwd|token|credential)";
const NAMED_CREDENTIAL_ASSIGNMENT_PATTERN = new RegExp(
  [
    "(?<![A-Za-z0-9_$-])",
    "(?<name>[A-Za-z0-9_$-]*",
    CREDENTIAL_NAME_PATTERN_SOURCE,
    "[A-Za-z0-9_$-]*)",
    "(?<beforeSeparator>\\s*)",
    "(?<separator>[=:])",
    "(?<afterSeparator>\\s*)",
    "(?:",
    "(?<quote>[\"'])",
    "(?<quotedValue>[A-Za-z0-9_./+=-]{16,255})",
    "\\k<quote>",
    "|",
    "(?<unquotedValue>[A-Za-z0-9_./+=-]{16,255})(?=$|[\\s;,#])",
    ")",
  ].join(""),
  "dgim",
);

let typeScriptLoadAttempted = false;
let cachedTypeScriptApi = null;

function loadTypeScriptApi() {
  if (typeScriptLoadAttempted) return cachedTypeScriptApi;
  typeScriptLoadAttempted = true;
  try {
    cachedTypeScriptApi = requireModule("typescript");
  } catch {
    cachedTypeScriptApi = null;
  }
  return cachedTypeScriptApi;
}
```

Keep the token, private-key and JWT patterns in `CREDENTIAL_PATTERNS`. Remove
`TYPESCRIPT_TYPE_BLOCK_PATTERN`, `TYPESCRIPT_CREDENTIAL_PROPERTY_PATTERN` and
`credentialScanText` completely.

- [ ] **Step 2: Add exact candidate extraction**

Insert after `countMatches`:

```javascript
function namedCredentialCandidates(text) {
  NAMED_CREDENTIAL_ASSIGNMENT_PATTERN.lastIndex = 0;
  const candidates = [];
  for (const match of text.matchAll(NAMED_CREDENTIAL_ASSIGNMENT_PATTERN)) {
    const groups = match.groups;
    const indices = match.indices?.groups;
    const valueIndices = indices?.quotedValue ?? indices?.unquotedValue;
    if (
      !groups ||
      !indices?.name ||
      !indices?.separator ||
      !valueIndices ||
      typeof match.index !== "number"
    ) {
      candidates.push({
        matchStart: match.index ?? 0,
        matchEnd: (match.index ?? 0) + match[0].length,
        nameStart: -1,
        nameEnd: -1,
        separator: groups?.separator === "=" ? "=" : ":",
        valueStart: -1,
        valueEnd: -1,
        quoted: Boolean(groups?.quote),
        positionsValid: false,
      });
      continue;
    }
    candidates.push({
      matchStart: match.index,
      matchEnd: match.index + match[0].length,
      nameStart: indices.name[0],
      nameEnd: indices.name[1],
      separator: groups.separator,
      valueStart: valueIndices[0],
      valueEnd: valueIndices[1],
      quoted: Boolean(groups.quote),
      positionsValid: true,
    });
  }
  NAMED_CREDENTIAL_ASSIGNMENT_PATTERN.lastIndex = 0;
  return candidates;
}
```

An invalid position record remains a countable raw candidate and can never be
suppressed.

- [ ] **Step 3: Run the focused tests and confirm they remain RED**

```powershell
node --test --test-name-pattern="type-shaped|allowlisted property|runtime or ambiguous|AST suppression|exact candidate" scripts/check-push-graph.test.mjs
```

Expected: bypass tests still fail because candidate adjudication is not yet
implemented. Existing assignment tests remain green.

### Task 4: Implement the narrow TypeScript AST adjudicator

**Files:**
- Modify: `scripts/check-push-graph.mjs`
- Test: `scripts/check-push-graph.test.mjs`

- [ ] **Step 1: Add path and type-reference guards**

```javascript
function typeScriptScriptKind(ts, path) {
  if (/\.tsx$/i.test(path)) return ts.ScriptKind.TSX;
  if (/\.ts$/i.test(path)) return ts.ScriptKind.TS;
  return null;
}

function isAllowlistedTypeReference(ts, sourceFile, node, candidate, text) {
  if (!ts.isTypeReferenceNode(node.type) || node.type.typeArguments?.length) {
    return false;
  }
  const typeStart = node.type.getStart(sourceFile);
  const typeEnd = node.type.end;
  if (candidate.valueStart !== typeStart || candidate.valueEnd !== typeEnd) {
    return false;
  }
  const typeName = node.type.typeName.getText(sourceFile);
  if (text.slice(candidate.valueStart, candidate.valueEnd) !== typeName) {
    return false;
  }
  return /^[$A-Z_a-z][$\w]*(?:\.[$A-Z_a-z][$\w]*)*$/.test(typeName);
}
```

Only a plain identifier or qualified TypeReference is allowlisted. Generics,
literal types and every ambiguous tail remain visible.

- [ ] **Step 2: Add the candidate-scoped AST traversal**

```javascript
function safeTypeSignatureCandidateStarts(path, text, candidates) {
  const relevant = candidates.filter(
    (candidate) =>
      candidate.positionsValid &&
      !candidate.quoted &&
      candidate.separator === ":",
  );
  if (relevant.length === 0) return new Set();

  const ts = loadTypeScriptApi();
  if (!ts) return new Set();
  const scriptKind = typeScriptScriptKind(ts, path);
  if (scriptKind === null) return new Set();

  try {
    const sourceFile = ts.createSourceFile(
      path,
      text,
      ts.ScriptTarget.Latest,
      true,
      scriptKind,
    );
    if (
      !Array.isArray(sourceFile.parseDiagnostics) ||
      sourceFile.parseDiagnostics.length !== 0
    ) {
      return new Set();
    }

    const candidatesByNameStart = new Map(
      relevant.map((candidate) => [candidate.nameStart, candidate]),
    );
    const safe = new Set();
    const stack = [sourceFile];
    while (stack.length > 0) {
      const node = stack.pop();
      if (
        ts.isPropertySignature(node) &&
        (ts.isInterfaceDeclaration(node.parent) ||
          ts.isTypeLiteralNode(node.parent)) &&
        ts.isIdentifier(node.name)
      ) {
        const nameStart = node.name.getStart(sourceFile);
        const candidate = candidatesByNameStart.get(nameStart);
        if (
          candidate &&
          node.name.end === candidate.nameEnd &&
          isAllowlistedTypeReference(ts, sourceFile, node, candidate, text) &&
          /^\s*;\s*$/.test(text.slice(node.type.end, node.end))
        ) {
          safe.add(candidate.matchStart);
        }
      }
      ts.forEachChild(node, (child) => stack.push(child));
    }
    return safe;
  } catch {
    return new Set();
  }
}
```

Do not broaden the parent types or accept parser recovery. Do not expose
parser errors.

- [ ] **Step 3: Count raw candidates minus only proven-safe positions**

Replace the credential counting block in `classifyBlob` with:

```javascript
const counts = new Map();
const namedCandidates = namedCredentialCandidates(text);
const safeTypeCandidates = safeTypeSignatureCandidateStarts(
  path,
  text,
  namedCandidates,
);
const namedCount = namedCandidates.filter(
  (candidate) => !safeTypeCandidates.has(candidate.matchStart),
).length;
if (namedCount > 0) counts.set("credential_like", namedCount);

for (const pattern of CREDENTIAL_PATTERNS) {
  const count = countMatches(text, pattern);
  if (count > 0) {
    counts.set("credential_like", (counts.get("credential_like") ?? 0) + count);
  }
}
```

All other content classification remains byte-for-byte unchanged.

- [ ] **Step 4: Run the focused suite and prove GREEN**

```powershell
node --test --test-name-pattern="unquoted PREVIEW_CLIENT_SECRET|type-shaped|allowlisted property|runtime or ambiguous|AST suppression|exact candidate" scripts/check-push-graph.test.mjs
if ($LASTEXITCODE -ne 0) { throw "K1_T3_AST_FOCUSED_GREEN_FAILED" }
```

Expected: all selected assignment, bypass, property, runtime, extension and
position tests pass.

- [ ] **Step 5: Run the complete scanner suite**

```powershell
node --test scripts/check-push-graph.test.mjs
if ($LASTEXITCODE -ne 0) { throw "K1_T3_AST_FULL_GREEN_FAILED" }
```

Expected: all prior 19 tests and all new tests pass with zero failures.

- [ ] **Step 6: Verify the exact two-file diff**

```powershell
$implementationFiles = @(
  "scripts/check-push-graph.mjs",
  "scripts/check-push-graph.test.mjs"
) | Sort-Object
$changedImplementationFiles = @(
  git diff --name-only e930aab..HEAD -- `
    scripts/check-push-graph.mjs `
    scripts/check-push-graph.test.mjs
) | Sort-Object -Unique
$implementationDifference = @(
  Compare-Object `
    -ReferenceObject $implementationFiles `
    -DifferenceObject $changedImplementationFiles
)
if ($implementationDifference.Count -ne 0) {
  throw "K1_T3_AST_IMPLEMENTATION_SCOPE_MISMATCH"
}

$allowedSinceStart = @(
  "docs/superpowers/plans/2026-08-26-aurelia-k1-task3-string-type-bypass.md",
  "docs/superpowers/specs/2026-08-26-aurelia-k1-task3-string-type-bypass-design.md",
  "docs/superpowers/plans/2026-08-26-aurelia-k1-task3-overlap-enumeration-correction.md",
  "docs/superpowers/specs/2026-08-26-aurelia-k1-task3-overlap-enumeration-correction-design.md",
  "docs/superpowers/specs/2026-08-27-aurelia-linux-workstation-migration-recovery-design.md",
  "scripts/check-push-graph.mjs",
  "scripts/check-push-graph.test.mjs"
) | Sort-Object
$changedSinceStart = @(git diff --name-only e930aab..HEAD) | Sort-Object -Unique
$branchDifference = @(
  Compare-Object -ReferenceObject $allowedSinceStart -DifferenceObject $changedSinceStart
)
if ($branchDifference.Count -ne 0) { throw "K1_T3_AST_BRANCH_SCOPE_MISMATCH" }

git diff --check e930aab..HEAD
if ($LASTEXITCODE -ne 0) { throw "K1_T3_AST_COMMITTED_DIFF_INVALID" }
git diff --cached --check
if ($LASTEXITCODE -ne 0) { throw "K1_T3_AST_INDEX_DIFF_INVALID" }
git diff --check
if ($LASTEXITCODE -ne 0) { throw "K1_T3_AST_WORKTREE_DIFF_INVALID" }
```

The allowlist covers only surfaces this plan may touch. Separately authorized
documentation checkpoints extend it; the implementation surface stays exactly
the two scanner files.

- [ ] **Step 7: Create the local GREEN checkpoint only under a separate authorization**

```powershell
git add -- scripts/check-push-graph.mjs scripts/check-push-graph.test.mjs
git diff --cached --check
if ($LASTEXITCODE -ne 0) { throw "K1_T3_AST_GREEN_INDEX_INVALID" }
git commit -m "fix(security): adjudicate scanner credentials with ast"
```

No push is permitted.

### Task 5: Run full fail-closed acceptance

**Files:**
- Test: `scripts/check-push-graph.test.mjs`
- Test: `scripts/check-project-control-k1.mjs`

- [ ] **Step 1: Run scanner and K1 control tests freshly**

```powershell
node --test scripts/check-push-graph.test.mjs
if ($LASTEXITCODE -ne 0) { throw "K1_T3_AST_ACCEPT_SCANNER_FAILED" }

npm run check:k1-control
if ($LASTEXITCODE -ne 0) { throw "K1_T3_AST_ACCEPT_CONTROL_FAILED" }
```

- [ ] **Step 2: Prove package and public control surfaces are unchanged**

```powershell
$allowedSinceStart = @(
  "docs/superpowers/plans/2026-08-26-aurelia-k1-task3-string-type-bypass.md",
  "docs/superpowers/specs/2026-08-26-aurelia-k1-task3-string-type-bypass-design.md",
  "docs/superpowers/plans/2026-08-26-aurelia-k1-task3-overlap-enumeration-correction.md",
  "docs/superpowers/specs/2026-08-26-aurelia-k1-task3-overlap-enumeration-correction-design.md",
  "docs/superpowers/specs/2026-08-27-aurelia-linux-workstation-migration-recovery-design.md",
  "scripts/check-push-graph.mjs",
  "scripts/check-push-graph.test.mjs"
) | Sort-Object
$changedSinceStart = @(git diff --name-only e930aab..HEAD) | Sort-Object -Unique
$scopeDifference = @(
  Compare-Object -ReferenceObject $allowedSinceStart -DifferenceObject $changedSinceStart
)
if ($scopeDifference.Count -ne 0) { throw "K1_T3_AST_FORBIDDEN_FILE_CHANGED" }

git diff --exit-code e930aab..HEAD -- package.json package-lock.json
if ($LASTEXITCODE -ne 0) { throw "K1_T3_AST_PACKAGE_MUTATION" }
```

The allowlist covers only surfaces this plan may touch. Separately authorized
documentation checkpoints extend it; package files, the status ledger and the
implementation surface are excluded from mutation by the assertions above.

- [ ] **Step 3: Run the real publication graph and assert its expected red state**

```powershell
node scripts/check-push-graph.mjs --base origin/codex/aurelia-vorbereitung --head HEAD --mode full
if ($LASTEXITCODE -ne 1) { throw "K1_T3_AST_REAL_GRAPH_EXIT_MISMATCH" }
```

Expected: Exit 1 while existing reachable findings remain. Every line contains
only `category`, `blob`, `path` and `count`; no values or parser details appear.

- [ ] **Step 4: Run all final diff and state checks**

```powershell
git diff --check e930aab..HEAD
if ($LASTEXITCODE -ne 0) { throw "K1_T3_AST_FINAL_COMMITTED_DIFF_INVALID" }
git diff --cached --check
if ($LASTEXITCODE -ne 0) { throw "K1_T3_AST_FINAL_INDEX_DIFF_INVALID" }
git diff --check
if ($LASTEXITCODE -ne 0) { throw "K1_T3_AST_FINAL_WORKTREE_DIFF_INVALID" }

$state = @(git status --porcelain=v1)
if ($LASTEXITCODE -ne 0 -or $state.Count -ne 0) {
  throw "K1_T3_AST_FINAL_WORKTREE_NOT_CLEAN"
}
```

### Task 6: Execute the focused Spec review

**Files:**
- Read: `docs/superpowers/specs/2026-08-26-aurelia-k1-task3-string-type-bypass-design.md`
- Read: `scripts/check-push-graph.mjs`
- Read: `scripts/check-push-graph.test.mjs`

- [ ] **Step 1: Build the sanitized review packet**

The packet contains only:

```powershell
git diff --no-ext-diff --unified=100 e930aab..HEAD -- `
  scripts/check-push-graph.mjs `
  scripts/check-push-graph.test.mjs
```

Add the approved design and fresh Task-5 command results. Do not include chat
history, raw analyses, secrets, unrelated product code or V3 source material.

- [ ] **Step 2: Use this exact Spec decision contract**

```text
Review only the supplied AURELIA String/Type-Bypass design, two-file diff and
fresh test evidence. Do not mutate anything or propose unrelated refactoring.
Verify raw-text candidate discovery, exact UTF-16 positions, full identifier
matching, synchronous lazy TypeScript loading, strict PropertySignature parent
and type allowlist, no suppression in strings/comments/runtime contexts,
raw-scan fallback for every loader/parser/diagnostic/position ambiguity,
non-leakage, unchanged public API/CLI/exit behavior, two-file scope and all
specified TDD boundaries. Treat missing evidence as FAIL.

Return exactly:
VERDICT: PASS or FAIL
FINDINGS:
- ID: stable identifier
  SEVERITY: P0, P1, or P2
  CONTRACT: exact violated design section
  EVIDENCE: exact file and line or missing test
  IMPACT: concrete failure mode
  CORRECTION: minimal required change

If there are no findings, return FINDINGS: none.
```

- [ ] **Step 3: Primary instance verifies every finding**

Only findings reproduced against code or missing contract evidence are
accepted. Opinion without a violated design clause does not block.

- [ ] **Step 4: Stop unless the Spec verdict is PASS**

On FAIL, return only to the affected RED/GREEN task. Do not start Quality
review, status updates or Task 4.

### Task 7: Execute the conditional Quality/Security review

**Files:**
- Read: same sanitized packet as Task 6

- [ ] **Step 1: Confirm the Spec-PASS precondition**

Required evidence is an explicit Spec `VERDICT: PASS` with no open P0-P2.
Without it, stop.

- [ ] **Step 2: Run one independent Sol xHigh review with this contract**

```text
Perform a focused AURELIA security and code-quality review of only the supplied
String/Type-Bypass scanner diff and fresh tests. Spec compliance has passed.
Look for any candidate that can be lost through AST parsing, parser recovery,
position mismatch, prefix-name matching, strings, comments, templates, TSX,
runtime contexts or loader failure. Check value leakage, regex backtracking,
1-MiB performance, cache behavior and tests that pass without proving the
claim. Do not review unrelated repository areas.

Return VERDICT: PASS or FAIL and only actionable P0-P2 findings with exact
file evidence, impact and minimal correction. Return FINDINGS: none when no
such finding exists.
```

- [ ] **Step 3: Primary instance reproduces every finding**

One normal correction loop is allowed. A remaining P0-P2 or a systemic new
finding stops for consolidation rather than launching recursive reviews.

- [ ] **Step 4: Keep Task 4 blocked until both reviews PASS**

Both explicit verdicts are required. Tests alone do not unblock Task 4.

### Task 8: Prepare a separately authorized status-evidence update

**Files:**
- Modify later only under separate authorization: `docs/project-control/K1-STATUS.md`

- [ ] **Step 1: Verify both PASS verdicts and final implementation commit**

Record exact commit IDs and command evidence. Do not predict or self-reference
a future documentation commit.

- [ ] **Step 2: Update only the Task-3 current status**

The later text must state:

- `K1-T3-P1-01-STRING-TYPE-BYPASS` closed by RED/GREEN evidence;
- candidates remain visible in strings, comments and runtime contexts;
- only exact AST `PropertySignature` candidates are suppressed;
- Spec and Quality/Security reviews PASS with their evidence identifiers;
- Task 4 is eligible to start but has not started;
- publication gate remains blocked and no push or server action is authorized.

- [ ] **Step 3: Re-run K1 control and diff checks before any status commit**

```powershell
npm run check:k1-control
if ($LASTEXITCODE -ne 0) { throw "K1_T3_AST_STATUS_CONTROL_FAILED" }
git diff --cached --check
if ($LASTEXITCODE -ne 0) { throw "K1_T3_AST_STATUS_INDEX_INVALID" }
git diff --check
if ($LASTEXITCODE -ne 0) { throw "K1_T3_AST_STATUS_WORKTREE_INVALID" }
```

No status commit or push is part of the present documentation authorization.

## Final stop condition

Completion of a later implementation run requires all of the following:

- the reproduced String/Type-Bypass is RED before production changes and GREEN
  afterwards;
- no raw text is removed or masked;
- only exact, allowlisted AST Property-Signature candidates are suppressed;
- all loader, parser, diagnostic and position ambiguity falls back to raw scan;
- full scanner and K1-control tests pass;
- the real graph remains correctly blocked with Exit 1;
- the implementation diff contains only scanner and scanner test;
- Spec and Quality/Security reviews both PASS;
- Task 4 is only unblocked, not implemented;
- no push, server action, history rewrite, package mutation, secret change or
  V3 mutation has occurred.
