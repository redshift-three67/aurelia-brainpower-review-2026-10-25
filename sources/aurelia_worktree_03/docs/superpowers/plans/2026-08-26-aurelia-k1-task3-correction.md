# AURELIA K1 Task-3 Correction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close `K1-T3-P1-01`, `K1-T3-P1-02`, and `K1-T3-Q-01` without weakening the fail-closed publication graph scanner or widening any publication, server, or history boundary.

**Architecture:** Keep the existing scanner API and Git enumeration unchanged. Add three narrow RED/GREEN corrections: recognize safe synthetic unquoted credential assignments, normalize every diagnostic to a string, and emit the single canonical identity category `operational_identity`; then update only the K1 status and run sequential critical-assurance reviews.

**Tech Stack:** Node.js 22 ESM, Node Test Runner, PowerShell, Git.

---

## 0. Fixed execution contract

Implementation starts only after this plan has its own explicitly authorized
local documentation checkpoint and the worktree is clean.

| Boundary | Required value |
|---|---|
| Branch | `codex/aurelia-konsolidierung` |
| Approved strategy/design checkpoint | `b84b72a` |
| Required ancestor | `8706186af01e10e4253e25abb31bf3577110dae4` |
| Task-3 implementation checkpoint | `e33c84be8ad9e74a083c8917f66e9cd7112d4252` |
| Risk route | B — Critical Assurance |
| Data class | synthetic only |
| Push | forbidden |
| Server access | forbidden |
| History rewrite | forbidden |
| Task 4 | blocked until Spec-PASS and Quality-PASS |

The implementation surface is exactly:

- `scripts/check-push-graph.test.mjs`
- `scripts/check-push-graph.mjs`
- `docs/project-control/K1-STATUS.md`

No dependency, package script, V3 evidence, credential, analysis source,
historical object, Task-4 file, server file, or product source is changed.

### Task 1: Establish a clean, reproducible baseline

**Files:**
- Read: `docs/project-control/QUALITY-ROUTING.md`
- Read: `docs/superpowers/specs/2026-08-26-aurelia-k1-task3-correction-design.md`
- Read: `docs/project-control/K1-STATUS.md`
- Read: `scripts/check-push-graph.mjs`
- Test: `scripts/check-push-graph.test.mjs`

- [ ] **Step 1: Verify branch, clean worktree, and required ancestry**

```powershell
$ErrorActionPreference = "Stop"

$branch = git branch --show-current
if ($LASTEXITCODE -ne 0 -or $branch -cne "codex/aurelia-konsolidierung") {
  throw "K1_T3_BRANCH_MISMATCH"
}

$state = @(git status --porcelain=v1)
if ($LASTEXITCODE -ne 0 -or $state.Count -ne 0) {
  throw "K1_T3_WORKTREE_NOT_CLEAN"
}

git merge-base --is-ancestor b84b72a HEAD
if ($LASTEXITCODE -ne 0) { throw "K1_T3_STRATEGY_BASE_MISSING" }

git merge-base --is-ancestor e33c84be8ad9e74a083c8917f66e9cd7112d4252 HEAD
if ($LASTEXITCODE -ne 0) { throw "K1_T3_CHECKPOINT_MISSING" }
```

Expected: no output after the branch read and exit 0.

- [ ] **Step 2: Run the unchanged scanner baseline**

```powershell
node --test scripts/check-push-graph.test.mjs
if ($LASTEXITCODE -ne 0) { throw "K1_T3_BASELINE_TESTS_FAILED" }
```

Expected: 13 tests pass, 0 fail.

- [ ] **Step 3: Run the unchanged K1 control baseline**

```powershell
npm run check:k1-control
if ($LASTEXITCODE -ne 0) { throw "K1_T3_BASELINE_CONTROL_FAILED" }
```

Expected: exit 0.

### Task 2: Close K1-T3-P1-01 with RED/GREEN

**Files:**
- Modify: `scripts/check-push-graph.test.mjs`
- Modify: `scripts/check-push-graph.mjs:12-28`
- Test: `scripts/check-push-graph.test.mjs`

- [ ] **Step 1: Add the synthetic fixture helper**

Insert after `syntheticIdentity()` in
`scripts/check-push-graph.test.mjs`:

```javascript
function syntheticUnquotedPreviewSecret() {
  const name = ["PREVIEW", "CLIENT", "SECRET"].join("_");
  const value = ["synthetic", "scanner", "fixture", "123456"].join("-");
  return { assignment: `${name}=${value}`, value };
}
```

- [ ] **Step 2: Add the positive non-leakage test**

Insert after the existing content-category test:

```javascript
test("classifyBlob recognizes an unquoted PREVIEW_CLIENT_SECRET without values", () => {
  const { assignment, value } = syntheticUnquotedPreviewSecret();
  const findings = classifyBlob("notes/credential.txt", Buffer.from(assignment));

  assert.deepEqual(
    findings.map((finding) => finding.category),
    ["credential_like"],
  );
  const rendered = JSON.stringify(findings);
  assert.equal(rendered.includes(value), false);
  assert.equal(rendered.includes(assignment), false);
});
```

- [ ] **Step 3: Add exact negative-boundary tests**

```javascript
test("classifyBlob ignores incomplete unquoted credential assignments", () => {
  const harmless = [
    "const PREVIEW_CLIENT_SECRET;",
    "PREVIEW_CLIENT_SECRET=short",
    "PREVIEW_CLIENT_SECRET=",
  ].join("\n");

  assert.deepEqual(
    classifyBlob("src/credential-shape.ts", Buffer.from(harmless)),
    [],
  );
});
```

- [ ] **Step 4: Run the focused test and prove RED**

```powershell
node --test --test-name-pattern="unquoted PREVIEW_CLIENT_SECRET|incomplete unquoted" scripts/check-push-graph.test.mjs
```

Expected: the positive test fails because the current credential regex requires
matching quotes; the negative test passes.

- [ ] **Step 5: Extend only the generic assignment pattern**

In `CREDENTIAL_PATTERNS`, replace the current quoted-assignment `RegExp` with:

```javascript
new RegExp(
  [
    "(?:api[_-]?key|access[_-]?token|client[_-]?secret|password|passwd|token|credential)",
    "\\s*[=:]\\s*",
    "(?:",
    "([\"'])",
    "[A-Za-z0-9_./+=-]{16,255}",
    "\\1",
    "|",
    "[A-Za-z0-9_./+=-]{16,255}(?=$|[\\s;,#])",
    ")",
  ].join(""),
  "gim",
),
```

Do not add source evaluation, string-expression parsing, or a new scanner API.

- [ ] **Step 6: Run the focused test and prove GREEN**

```powershell
node --test --test-name-pattern="unquoted PREVIEW_CLIENT_SECRET|incomplete unquoted" scripts/check-push-graph.test.mjs
if ($LASTEXITCODE -ne 0) { throw "K1_T3_P1_01_GREEN_FAILED" }
```

Expected: 2 tests pass, 0 fail.

- [ ] **Step 7: Run the complete scanner suite**

```powershell
node --test scripts/check-push-graph.test.mjs
if ($LASTEXITCODE -ne 0) { throw "K1_T3_P1_01_REGRESSION_FAILED" }
```

Expected: all baseline tests plus the two new tests pass.

- [ ] **Step 8: Create the isolated local checkpoint**

Execute only under an explicit implementation authorization that permits local
commits and still forbids push:

```powershell
git add -- scripts/check-push-graph.mjs scripts/check-push-graph.test.mjs
git diff --cached --check
if ($LASTEXITCODE -ne 0) { throw "K1_T3_P1_01_INDEX_INVALID" }
git commit -m "fix(security): detect unquoted scanner credentials"
```

Expected: one local commit containing only the two scanner files.

### Task 3: Close K1-T3-P1-02 with RED/GREEN

**Files:**
- Modify: `scripts/check-push-graph.test.mjs`
- Modify: `scripts/check-push-graph.mjs:330-436`
- Test: `scripts/check-push-graph.test.mjs`

- [ ] **Step 1: Strengthen the existing unresolved-commit assertions**

Replace the three exit-only assertions in
`scanGraph returns exit 2 when either commit is missing or unresolved` with:

```javascript
const invalidRequest = scanGraph({ root, head, mode: "full" });
assert.equal(invalidRequest.exitCode, 2);
assert.deepEqual(invalidRequest.diagnostics, ["invalid_request"]);

const unresolvedBase = scanGraph({
  root,
  base: "missing-ref",
  head,
  mode: "full",
});
assert.equal(unresolvedBase.exitCode, 2);
assert.deepEqual(unresolvedBase.diagnostics, ["commit_unresolved"]);

const unresolvedHead = scanGraph({
  root,
  base: head,
  head: "missing-ref",
  mode: "full",
});
assert.equal(unresolvedHead.exitCode, 2);
assert.deepEqual(unresolvedHead.diagnostics, ["commit_unresolved"]);
```

- [ ] **Step 2: Strengthen the non-ancestor assertion**

Append to the existing non-ancestor test:

```javascript
assert.deepEqual(result.diagnostics, ["base_not_ancestor"]);
assert.ok(result.diagnostics.every((value) => typeof value === "string"));
```

- [ ] **Step 3: Add the commit-limit diagnostic test**

```javascript
test("scanGraph returns string diagnostics for the commit limit", (t) => {
  const root = createRepository(t);
  writeFixture(root, "README.md", "Root.\n");
  const head = commitAll(root, "base");
  const commits = Array.from(
    { length: 4097 },
    (_, index) => (index + 1).toString(16).padStart(40, "0"),
  ).join("\n");
  const injectedGit = (command, args, options) => {
    if (args[0] === "rev-list") {
      return { status: 0, signal: null, stdout: `${commits}\n`, stderr: "" };
    }
    return spawnSync(command, args, options);
  };

  const result = scanGraph({
    root,
    base: head,
    head,
    mode: "full",
    git: injectedGit,
  });

  assert.equal(result.exitCode, 1);
  assert.deepEqual(result.diagnostics, ["commit_limit"]);
  assert.ok(result.diagnostics.every((value) => typeof value === "string"));
});
```

- [ ] **Step 4: Add the path-limit diagnostic test**

```javascript
test("scanGraph returns string diagnostics for the path limit", (t) => {
  const root = createRepository(t);
  writeFixture(root, "README.md", "Root.\n");
  const head = commitAll(root, "base");
  const tree = Array.from({ length: 100001 }, (_, index) => {
    const blob = (index + 1).toString(16).padStart(40, "0");
    return `100644 blob ${blob}\tpaths/${index}.txt\0`;
  }).join("");
  const injectedGit = (command, args, options) => {
    if (args[0] === "rev-list") {
      return { status: 0, signal: null, stdout: `${head}\n`, stderr: "" };
    }
    if (args[0] === "ls-tree") {
      return { status: 0, signal: null, stdout: tree, stderr: "" };
    }
    return spawnSync(command, args, options);
  };

  const result = scanGraph({
    root,
    base: head,
    head,
    mode: "full",
    git: injectedGit,
  });

  assert.equal(result.exitCode, 1);
  assert.deepEqual(result.diagnostics, ["path_limit"]);
  assert.ok(result.diagnostics.every((value) => typeof value === "string"));
});
```

- [ ] **Step 5: Run the diagnostic tests and prove RED**

```powershell
node --test --test-name-pattern="missing or unresolved|not an ancestor|commit limit|path limit" scripts/check-push-graph.test.mjs
```

Expected: tests fail because current diagnostics contain objects.

- [ ] **Step 6: Normalize the three production return sites**

Apply these exact replacements in `scripts/check-push-graph.mjs`:

```javascript
const fail = (code) => ({
  exitCode: 2,
  findings: [],
  diagnostics: [code],
});
```

```javascript
return {
  exitCode: 1,
  findings: [unscannable(headCommit, ".")],
  diagnostics: ["commit_limit"],
};
```

```javascript
return {
  exitCode: 1,
  findings: [unscannable(headCommit, ".")],
  diagnostics: ["path_limit"],
};
```

- [ ] **Step 7: Run the diagnostic tests and prove GREEN**

```powershell
node --test --test-name-pattern="missing or unresolved|not an ancestor|commit limit|path limit" scripts/check-push-graph.test.mjs
if ($LASTEXITCODE -ne 0) { throw "K1_T3_P1_02_GREEN_FAILED" }
```

Expected: all selected tests pass and every diagnostic is a string.

- [ ] **Step 8: Run the complete scanner suite**

```powershell
node --test scripts/check-push-graph.test.mjs
if ($LASTEXITCODE -ne 0) { throw "K1_T3_P1_02_REGRESSION_FAILED" }
```

- [ ] **Step 9: Create the isolated local checkpoint**

```powershell
git add -- scripts/check-push-graph.mjs scripts/check-push-graph.test.mjs
git diff --cached --check
if ($LASTEXITCODE -ne 0) { throw "K1_T3_P1_02_INDEX_INVALID" }
git commit -m "fix(security): normalize scanner diagnostics"
```

Expected: one local commit, no push.

### Task 4: Close K1-T3-Q-01 with RED/GREEN

**Files:**
- Modify: `scripts/check-push-graph.test.mjs:96-139`
- Modify: `scripts/check-push-graph.mjs:198-200`
- Test: `scripts/check-push-graph.test.mjs`

- [ ] **Step 1: Change the active category expectation**

In the content-category fixture map, replace
`pii_or_operational_identity` with `operational_identity`.

- [ ] **Step 2: Replace the single operator assertion with three explicit fixtures**

Replace the current `syntheticUser` assertion with:

```javascript
const operationalIdentities = [
  ["operator_email=", syntheticIdentity()].join(""),
  ["operator_", "user=", "\"build.runner\""].join(""),
  ["10", "24", "8", "7"].join("."),
];
for (const content of operationalIdentities) {
  assert.ok(
    categories(classifyBlob("notes/identity.txt", Buffer.from(content))).has(
      "operational_identity",
    ),
  );
}
```

- [ ] **Step 3: Run the identity tests and prove RED**

```powershell
node --test --test-name-pattern="content-only blocking category|harmless typed identity" scripts/check-push-graph.test.mjs
```

Expected: the content-category test fails because production still emits
`pii_or_operational_identity`.

- [ ] **Step 4: Rename the production category once**

Replace the active scanner line with:

```javascript
if (identityCount > 0) counts.set("operational_identity", identityCount);
```

Do not add an alias or mapping layer.

- [ ] **Step 5: Run the identity tests and prove GREEN**

```powershell
node --test --test-name-pattern="content-only blocking category|harmless typed identity" scripts/check-push-graph.test.mjs
if ($LASTEXITCODE -ne 0) { throw "K1_T3_Q_01_GREEN_FAILED" }
```

- [ ] **Step 6: Prove no active test expectation uses the retired name**

```powershell
$activeOldNames = @(rg -n "pii_or_operational_identity" scripts/check-push-graph.mjs scripts/check-push-graph.test.mjs)
if ($LASTEXITCODE -notin 0,1) { throw "K1_T3_Q_01_SCAN_FAILED" }
if ($activeOldNames.Count -ne 0) { throw "K1_T3_Q_01_OLD_NAME_REMAINS" }
```

Expected: zero matches.

- [ ] **Step 7: Run the complete scanner suite**

```powershell
node --test scripts/check-push-graph.test.mjs
if ($LASTEXITCODE -ne 0) { throw "K1_T3_Q_01_REGRESSION_FAILED" }
```

- [ ] **Step 8: Create the isolated local checkpoint**

```powershell
git add -- scripts/check-push-graph.mjs scripts/check-push-graph.test.mjs
git diff --cached --check
if ($LASTEXITCODE -ne 0) { throw "K1_T3_Q_01_INDEX_INVALID" }
git commit -m "fix(security): canonicalize operational identity"
```

Expected: one local commit, no push.

### Task 5: Record the corrected implementation state and run full acceptance

**Files:**
- Modify: `docs/project-control/K1-STATUS.md:47-80`
- Test: `scripts/check-push-graph.test.mjs`
- Test: `scripts/check-project-control-k1.mjs`

- [ ] **Step 1: Update only the Task-3 ledger row**

Use this exact state until reviews finish:

```markdown
| 3 | `e33c84b` plus lokale Korrekturcommits | TDD-Korrektur für P1-01, P1-02 und Q-01 implementiert | erneutes Spec-Review ausstehend; Qualitätsreview bis Spec-PASS blockiert |
```

- [ ] **Step 2: Replace the open-finding headings with implementation status**

```markdown
### Implementierte Task-3-Korrekturen, Review ausstehend

- `K1-T3-P1-01`: RED/GREEN für unquotierte synthetische
  `PREVIEW_CLIENT_SECRET`-Zuweisung implementiert; Fundwerte bleiben
  unterdrückt. Spec-Review ausstehend.
- `K1-T3-P1-02`: Alle Exit-2- und Limitdiagnosen sind Strings; RED/GREEN
  implementiert. Spec-Review ausstehend.
- `K1-T3-Q-01`: Aktive Scanner- und Testausgabe verwendet ausschließlich
  `operational_identity`. Qualitätsreview bleibt bis Spec-PASS blockiert.
```

Do not rewrite the historical aggregate tables. Preserve their explanation of
the formerly observed technical name `pii_or_operational_identity`.

- [ ] **Step 3: Run scanner and K1 control tests**

```powershell
node --test scripts/check-push-graph.test.mjs
if ($LASTEXITCODE -ne 0) { throw "K1_T3_FULL_SCANNER_TESTS_FAILED" }

npm run check:k1-control
if ($LASTEXITCODE -ne 0) { throw "K1_T3_FULL_CONTROL_FAILED" }
```

Expected: all scanner tests and K1 control pass.

- [ ] **Step 4: Run all three diff checks**

```powershell
git diff --check b84b72a..HEAD -- scripts/check-push-graph.mjs scripts/check-push-graph.test.mjs docs/project-control/K1-STATUS.md
if ($LASTEXITCODE -ne 0) { throw "K1_T3_COMMITTED_DIFF_INVALID" }

git diff --cached --check
if ($LASTEXITCODE -ne 0) { throw "K1_T3_INDEX_DIFF_INVALID" }

git diff --check
if ($LASTEXITCODE -ne 0) { throw "K1_T3_WORKTREE_DIFF_INVALID" }
```

- [ ] **Step 5: Run the real full-graph gate and assert the expected red state**

```powershell
node scripts/check-push-graph.mjs --base origin/codex/aurelia-vorbereitung --head HEAD --mode full
if ($LASTEXITCODE -ne 1) { throw "K1_T3_REAL_GRAPH_EXIT_MISMATCH" }
```

Expected: Exit 1 with only safe fields. Identity findings use
`operational_identity`; existing reachable findings keep publication blocked.

- [ ] **Step 6: Assert the exact implementation file scope**

```powershell
$allowed = @(
  "docs/project-control/K1-STATUS.md",
  "scripts/check-push-graph.mjs",
  "scripts/check-push-graph.test.mjs"
) | Sort-Object
$changed = @(
  git diff --name-only b84b72a..HEAD -- `
    docs/project-control/K1-STATUS.md `
    scripts/check-push-graph.mjs `
    scripts/check-push-graph.test.mjs
) | Sort-Object
$scopeDifference = @(Compare-Object -ReferenceObject $allowed -DifferenceObject $changed)
if ($scopeDifference.Count -ne 0) { throw "K1_T3_IMPLEMENTATION_SCOPE_MISMATCH" }
```

- [ ] **Step 7: Commit the implementation-status evidence locally**

```powershell
git add -- docs/project-control/K1-STATUS.md
git diff --cached --check
if ($LASTEXITCODE -ne 0) { throw "K1_T3_STATUS_INDEX_INVALID" }
git commit -m "docs: record task 3 correction checkpoint"
```

Expected: local commit only; branch remains unpushed.

### Task 6: Execute the focused Spec review

**Files:**
- Read: `docs/superpowers/specs/2026-08-26-aurelia-k1-task3-correction-design.md`
- Read: `scripts/check-push-graph.mjs`
- Read: `scripts/check-push-graph.test.mjs`
- Read: `docs/project-control/K1-STATUS.md`

- [ ] **Step 1: Build the sanitized review packet**

The packet contains only:

```powershell
git diff --no-ext-diff --unified=80 b84b72a..HEAD -- `
  scripts/check-push-graph.mjs `
  scripts/check-push-graph.test.mjs `
  docs/project-control/K1-STATUS.md
```

Add the Task-3 correction design and the fresh command results from Task 5.
Do not include raw analysis sources, secrets, the full chat, unrelated product
code, or historical V3 source material.

- [ ] **Step 2: Give the reviewer this exact decision contract**

```text
Review only the supplied AURELIA Task-3 correction design, scoped diff, and
test evidence. Do not propose unrelated refactoring and do not execute any
mutation. Verify every requirement for K1-T3-P1-01 and K1-T3-P1-02, including
negative boundaries, non-leakage, exact diagnostics string arrays, unchanged
public API, fail-closed exit behavior, and the three-file implementation
scope. Treat missing evidence as FAIL.

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

- [ ] **Step 3: Primary instance verifies every finding locally**

Expected: only code- and test-backed findings are accepted. Reviewer opinion
without contract evidence does not block.

- [ ] **Step 4: Stop unless the Spec verdict is PASS**

If FAIL, return only to the affected RED/GREEN task and rerun the scoped review.
Do not start Quality review or Task 4.

### Task 7: Execute the conditional Quality/Security review

**Files:**
- Read: same scoped packet as Task 6

- [ ] **Step 1: Confirm the Spec-PASS precondition**

```text
Required evidence: explicit Task-3 Spec VERDICT: PASS with no open P0-P2
findings.
```

Without that evidence, stop.

- [ ] **Step 2: Run one independent Sol xHigh Quality/Security review**

Use this exact decision contract:

```text
Perform a focused AURELIA security and code-quality review of only the supplied
Task-3 scanner diff and fresh tests. Spec compliance has already passed.
Look for credential-value leakage, regex overmatch or bypass, unsafe diagnostic
content, incorrect fail-closed exit behavior, performance or memory regressions
in limit tests, category inconsistencies, and tests that pass without proving
the claimed behavior. Do not review unrelated repository areas.

Return VERDICT: PASS or FAIL and only actionable P0-P2 findings with exact
file evidence, impact, and minimal correction. Return FINDINGS: none when no
such finding exists.
```

- [ ] **Step 3: Primary instance reproduces and verifies every finding**

One normal correction loop is allowed. A remaining P0-P2 or a new systemic
finding stops Task 3 for consolidation instead of starting recursive reviews.

- [ ] **Step 4: Record final review status only after both PASS verdicts**

Update the Task-3 ledger in `docs/project-control/K1-STATUS.md` to state both
PASS verdicts and that Task 4 is now eligible to start but not started. Run
`npm run check:k1-control` and `git diff --check` before any separately
authorized local documentation commit.

## Final stop condition

Completion of this plan means:

- all three Task-3 findings are closed by RED/GREEN evidence;
- full scanner and K1-control tests pass;
- the real publication graph remains correctly blocked with Exit 1;
- Spec review and Quality/Security review both PASS;
- Task 4 is only unblocked, not implemented;
- no push, server action, history rewrite, secret change, or V3 mutation has
  occurred.
