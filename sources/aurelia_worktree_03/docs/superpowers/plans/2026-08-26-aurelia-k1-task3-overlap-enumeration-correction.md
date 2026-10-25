# AURELIA K1 Task-3 Overlap-Enumeration Correction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close `CRED-NAME-LEADING-GRAMMAR` and `CRED-CANDIDATE-OVERLAP` without weakening the raw credential scan, the narrow TypeScript AST exception, the public scanner contract, or the linear performance bound.

**Architecture:** Enumerate maximal assignment heads without consuming values, filter their complete ASCII names for credential fragments, and parse each bound value independently with a 256-code-unit cap. Preserve candidate-specific UTF-16 positions and permit AST suppression only for one exact, valid TypeScript property-signature candidate; every enumeration, parser, mapping, or position fault remains blocking.

**Tech Stack:** Node.js 22 ESM, Node Test Runner, existing TypeScript dependency, PowerShell, Git.

---

## 0. Fixed execution contract

| Boundary | Required value |
|---|---|
| Branch | `codex/aurelia-konsolidierung` |
| Amended | 2026-08-28 — Betreiberoption B: Quality-Review-Findings übernommen (E4) |
| Active documentation checkpoint | `f1082f9d5a04ca32eaa8f79b1b9188e740622904` (Vorfahre; siehe Task 1 Step 1) |
| Required implementation-base ancestor | `73ea21ce8031714174d2b7cc922478a1dc0103af` |
| Parent design | `docs/superpowers/specs/2026-08-26-aurelia-k1-task3-string-type-bypass-design.md` |
| Correction design | `docs/superpowers/specs/2026-08-26-aurelia-k1-task3-overlap-enumeration-correction-design.md` |
| Correction-design SHA-256 | `6adb7a71a6021bc1828c7606118af8eec3d7c40c9ad55b563445bdf5047b6c54` |
| Findings | `CRED-NAME-LEADING-GRAMMAR`, `CRED-CANDIDATE-OVERLAP`, `K1-T3-Q-NEW-01`, `K1-T3-Q-NEW-02`, `K1-T3-Q-NEW-03` |
| Data | synthetic only |
| Push | forbidden |
| Server access | forbidden |
| History rewrite | forbidden |
| Task 4 | blocked until Spec-PASS and Quality/Security-PASS |

The future implementation surface is exactly:

- `scripts/check-push-graph.test.mjs`;
- `scripts/check-push-graph.mjs`.

The current worktree already contains an uncommitted two-file implementation
attempt. Its run-start hashes are (Amendierung 2026-08-28: der Scanner ist
seit Designlegung unverändert; der Test trägt die durch die
Spec-Review-Korrekturschleife freigegebenen Ergänzungen, E3 §6):

```text
scripts/check-push-graph.mjs      32c0b5b4ec3fdf5083bc399c5525e11281d7f6301e86e5670840cca9bca1abef
scripts/check-push-graph.test.mjs 81607e3362addb7ea160bf423934b1e043e42242a3917790ce23f361d76cbd63
```

No implementation worker may start unless a new operator authorization
explicitly names this correction plan. No commit is authorized merely by
executing the plan. A local implementation commit requires both reviews,
fresh final gates, and a separate explicit authorization.

### Task 1: Verify the correction baseline and document identity

**Files:**
- Read: `docs/superpowers/specs/2026-08-26-aurelia-k1-task3-overlap-enumeration-correction-design.md`
- Read: `scripts/check-push-graph.mjs`
- Read: `scripts/check-push-graph.test.mjs`

- [ ] **Step 1: Verify branch, HEAD, ancestry, and exact dirty scope**

```powershell
$ErrorActionPreference = "Stop"

if ((git branch --show-current) -cne "codex/aurelia-konsolidierung") {
  throw "K1_T3_OVERLAP_BRANCH_MISMATCH"
}
git merge-base --is-ancestor f1082f9d5a04ca32eaa8f79b1b9188e740622904 HEAD
if ($LASTEXITCODE -ne 0) { throw "K1_T3_OVERLAP_DOC_CHECKPOINT_MISSING" }
git merge-base --is-ancestor 73ea21ce8031714174d2b7cc922478a1dc0103af HEAD
if ($LASTEXITCODE -ne 0) { throw "K1_T3_OVERLAP_IMPLEMENTATION_BASE_ANCESTOR_MISSING" }
git merge-base --is-ancestor e930aab2643c376ddd9090a66be31c52d32f05ee HEAD
if ($LASTEXITCODE -ne 0) { throw "K1_T3_OVERLAP_ANCESTOR_MISSING" }

$expectedDirty = @(
  "scripts/check-push-graph.mjs",
  "scripts/check-push-graph.test.mjs",
  "docs/superpowers/plans/2026-08-26-aurelia-k1-task3-overlap-enumeration-correction.md",
  "docs/superpowers/plans/2026-08-26-aurelia-k1-task3-string-type-bypass.md",
  "docs/superpowers/specs/2026-08-26-aurelia-k1-task3-overlap-enumeration-correction-design.md"
) | Sort-Object
$actualDirty = @(git diff --name-only) | Sort-Object -Unique
if (@(Compare-Object $expectedDirty $actualDirty).Count -ne 0) {
  throw "K1_T3_OVERLAP_DIRTY_SCOPE_MISMATCH"
}
if (@(git diff --cached --name-only).Count -ne 0) {
  throw "K1_T3_OVERLAP_INDEX_NOT_EMPTY"
}
```

Expected: all assertions exit 0; nothing is staged.

Amendierung 2026-08-28: Die ursprüngliche HEAD-Gleichheitsprüfung mit
`f1082f9` war bei separat autorisierten Dokumentations-Checkpoints
(`85017ba`, `aec827f` und spätere autorisierte Dokument-Commits) nicht mehr
erfüllbar; die Vorfahren-Prüfung bewahrt die Absicht.

- [ ] **Step 2: Verify the approved correction design by digest**

```powershell
$design = "docs/superpowers/specs/2026-08-26-aurelia-k1-task3-overlap-enumeration-correction-design.md"
$digest = (Get-FileHash -Algorithm SHA256 -LiteralPath $design).Hash.ToLowerInvariant()
if ($digest -cne "6adb7a71a6021bc1828c7606118af8eec3d7c40c9ad55b563445bdf5047b6c54") {
  throw "K1_T3_OVERLAP_DESIGN_DIGEST_MISMATCH"
}
```

- [ ] **Step 3: Reproduce the current P1 state without printing values**

Run a synthetic one-line module probe that prints only IDs and counts.
Expected current counts are `numeric=0`, `hyphen=0`, and `overlap=1`.
The later GREEN expectation is `1`, `1`, and `2`.

### Task 2: Add the focused P1 regression tests and prove RED

**Files:**
- Modify: `scripts/check-push-graph.test.mjs`
- Test: `scripts/check-push-graph.test.mjs`

- [ ] **Step 1: Remove content-bearing assertion messages**

Replace the current helper with a label-only contract:

```javascript
function assertCredentialLikeCount(label, path, content, expectedCount) {
  const findings = classifyBlob(path, Buffer.from(content));
  const finding = findings.find((item) => item.category === "credential_like");
  assert.equal(finding?.count ?? 0, expectedCount, label);

  const rendered = JSON.stringify(findings);
  const { name, value } = syntheticNamedSecretShape();
  assert.equal(rendered.includes(name), false, `${label}: name leaked`);
  assert.equal(rendered.includes(value), false, `${label}: value leaked`);
  assert.equal(rendered.includes(content), false, `${label}: source leaked`);
}
```

Update every existing call to pass a stable harmless label as the first
argument. Do not put the candidate name, value, assignment, or source in a
label.

- [ ] **Step 2: Add leading-name and true-overlap RED tests**

```javascript
test("head-first candidates include leading digits and hyphens", () => {
  const { name, value } = syntheticNamedSecretShape();
  const suffixName = [name, "ARCHIVE"].join("_");
  const fixtures = [
    ["numeric-leading", "9", suffixName],
    ["hyphen-leading", "-", suffixName],
  ];

  for (const [label, prefix, completeName] of fixtures) {
    assertCredentialLikeCount(
      label,
      "notes/leading-name.txt",
      [prefix, completeName, "=", value].join(""),
      1,
    );
  }
});

test("head-first candidates count each valid overlap independently", () => {
  const { name, value } = syntheticNamedSecretShape();
  const first = ["PASS", "WORD"].join("");
  const fixtures = [
    ["dot-overlap", "."],
    ["slash-overlap", "/"],
  ];

  for (const [label, delimiter] of fixtures) {
    const content = [
      first,
      "=",
      "A".repeat(16),
      delimiter,
      name,
      "=",
      value,
    ].join("");
    assertCredentialLikeCount(label, "notes/overlap.txt", content, 2);
  }
});

test("a short earlier assignment and a later candidate are both counted", () => {
  const { name, value } = syntheticNamedSecretShape();
  const content = [
    ["PASS", "WORD"].join(""),
    "=short.",
    name,
    "=",
    value,
  ].join("");
  assertCredentialLikeCount(
    "short-head-before-valid",
    "notes/invalid-overlap.txt",
    content,
    2,
  );
});
```

Amendment 2026-08-28 (Option Y, K1-T3-GRAMMAR-CONFLICT): `=` ist VALUE_CHAR;
der frühere Wertlauf (`short.PREVIEW_CLIENT_SECRET=…`) läuft bis EOF und ist
damit selbst gültig — beide Zuweisungen zählen (fail-closed, nichts wird
verborgen). Die bisherige Erwartung 1 war unter der verbindlichen Grammatik
nicht erfüllbar; Begründung in der Design-Amendierung §8.

- [ ] **Step 2b: Add the E4 quality-review regression tests (Amendierung 2026-08-28)**

Add these tests next to the P1 tests, labels only, no candidate name, value,
assignment, or source in any assertion message:

```javascript
test("a value inside a double-quoted string literal counts", () => {
  const { name, value } = syntheticNamedSecretShape();
  const content = ["const sample = \"", name, "=", value, "\";"].join("");
  assertCredentialLikeCount("notes/string-literal.txt", content, 1);
});

test("a value before a JSON closing brace counts", () => {
  const { name, value } = syntheticNamedSecretShape();
  const content = ["{ \"key\": \"x\", ", name, "=", value, "}"].join("");
  assertCredentialLikeCount("notes/json-close.txt", content, 1);
});

test("CLI flag names with leading hyphens count", () => {
  const { name, value } = syntheticNamedSecretShape();
  for (const flag of ["--password", "--client-secret"]) {
    assertCredentialLikeCount(
      "notes/cli-flag.txt",
      [flag, "=", value].join(""),
      1,
    );
  }
});

test("a URL value with colons counts", () => {
  const content = [
    "password=ht",
    "tps://",
    "example",
    ".com/",
    "A".repeat(24),
  ].join("");
  assertCredentialLikeCount(
    "url-value",
    "notes/url-value.txt",
    content,
    1,
  );
});

test("an opening bracket stays a non-terminator", () => {
  const { name, value } = syntheticNamedSecretShape();
  const content = [name, "=", "A".repeat(16), "["].join("");
  assertCredentialLikeCount("notes/open-bracket.txt", content, 0);
});
```

Prove RED for the string-literal, brace, flag, and URL cases on the run-start
state and record the exit code and count differences in the implementer
report. Do not create a RED commit.

- [ ] **Step 3: Prove focused RED before scanner changes**

```powershell
node --test --test-name-pattern="head-first candidates" scripts/check-push-graph.test.mjs
```

Expected on the current scanner implementation:

- leading digit: `0` instead of `1`;
- leading hyphen: `0` instead of `1`;
- dot and slash overlap: `1` instead of `2`;
- command exits 1 because behavior is missing, not because of syntax or fixture
  errors.

Capture the command, exit code, failing test names and count differences in the
implementer report. Do not create a RED commit.

### Task 3: Lock the bounded value grammar as tests

**Files:**
- Modify: `scripts/check-push-graph.test.mjs`
- Test: `scripts/check-push-graph.test.mjs`

- [ ] **Step 1: Add quoted and unquoted boundary matrices**

```javascript
test("head-first value parser enforces exact quoted boundaries", () => {
  const { name } = syntheticNamedSecretShape();
  const fixtures = [
    ["single-16", `'${"A".repeat(16)}'`, 1],
    ["double-255", `"${"A".repeat(255)}"`, 1],
    ["quoted-15", `"${"A".repeat(15)}"`, 0],
    ["quoted-256", `"${"A".repeat(256)}"`, 0],
    ["unclosed", `"${"A".repeat(16)}`, 0],
    ["mismatched", `"${"A".repeat(16)}'`, 0],
  ];

  for (const [label, encodedValue, expected] of fixtures) {
    assertCredentialLikeCount(
      label,
      "notes/quoted.txt",
      [name, "=", encodedValue].join(""),
      expected,
    );
  }
});

test("head-first value parser enforces exact unquoted boundaries", () => {
  const { name } = syntheticNamedSecretShape();
  const validTerminators = ["", " ", "\r\n", ";", ",", "#", "\u2003"];
  for (const [index, terminator] of validTerminators.entries()) {
    assertCredentialLikeCount(
      `valid-terminator-${index}`,
      "notes/unquoted.txt",
      [name, "=", "A".repeat(16), terminator].join(""),
      1,
    );
  }

  const closing = [
    ["right-bracket", `${"A".repeat(16)}]`],
    ["right-paren", `${"A".repeat(16)})`],
    ["trailing-quote", `${"A".repeat(16)}"`],
    ["trailing-single-quote", `${"A".repeat(16)}'`],
    ["backtick", `${"A".repeat(16)}\``],
    ["closing-brace", `${"A".repeat(16)}}`],
    ["greater-than", `${"A".repeat(16)}>`],
  ];
  for (const [label, encodedValue] of closing) {
    assertCredentialLikeCount(
      label,
      "notes/unquoted-closing.txt",
      [name, "=", encodedValue].join(""),
      1,
    );
  }

  const invalid = [
    ["length-15", "A".repeat(15)],
    ["length-256", "A".repeat(256)],
    ["open-bracket", `${"A".repeat(16)}[`],
    ["open-paren", `${"A".repeat(16)}(`],
  ];
  for (const [label, encodedValue] of invalid) {
    assertCredentialLikeCount(
      label,
      "notes/unquoted-invalid.txt",
      [name, "=", encodedValue].join(""),
      0,
    );
  }
});
```

- [ ] **Step 2: Run only the value-boundary tests**

```powershell
node --test --test-name-pattern="head-first value parser" scripts/check-push-graph.test.mjs
```

Record which cases are already green and which fail. Production code remains
unchanged during this step.

### Task 4: Replace full-assignment matching with head-first enumeration

**Files:**
- Modify: `scripts/check-push-graph.mjs`
- Test: `scripts/check-push-graph.test.mjs`

- [ ] **Step 1: Replace the consuming candidate pattern**

Use one maximal general head pattern and one non-global credential filter:

```javascript
const ASSIGNMENT_HEAD_PATTERN = new RegExp(
  [
    "(?<![A-Za-z0-9_$-])",
    "(?<name>[A-Za-z0-9_$-]+)",
    "(?<optional>\\?)?",
    "(?<beforeSeparator>\\s*)",
    "(?<separator>[=:])",
    "(?<afterSeparator>\\s*)",
  ].join(""),
  "dgi",
);
const CREDENTIAL_NAME_PATTERN = new RegExp(CREDENTIAL_NAME_PATTERN_SOURCE, "i");
```

Delete the full-assignment candidate regex and every lookahead that repeats
`NAME* CREDENTIAL NAME*`.

- [ ] **Step 2: Add an ASCII code-unit predicate and bounded value parser**

```javascript
function isCredentialValueCodeUnit(code) {
  return (
    (code >= 48 && code <= 57) ||
    (code >= 65 && code <= 90) ||
    (code >= 97 && code <= 122) ||
    code === 43 ||
    code === 45 ||
    code === 46 ||
    code === 47 ||
    code === 61 ||
    code === 95
  );
}

function isUnquotedTerminator(text, index) {
  return (
    index === text.length ||
    text[index] === ";" ||
    text[index] === "," ||
    text[index] === "#" ||
    /\s/u.test(text[index])
  );
}

function parseBoundedCredentialValue(text, headEnd) {
  if (!Number.isInteger(headEnd) || headEnd < 0 || headEnd > text.length) {
    return { ok: false, fault: true };
  }

  const openingQuote = text[headEnd];
  const quoted = openingQuote === "'" || openingQuote === '"';
  const valueStart = quoted ? headEnd + 1 : headEnd;
  let valueEnd = valueStart;
  while (
    valueEnd < text.length &&
    valueEnd - valueStart <= 255 &&
    isCredentialValueCodeUnit(text.charCodeAt(valueEnd))
  ) {
    valueEnd += 1;
  }

  const length = valueEnd - valueStart;
  if (length < 16 || length > 255) return { ok: false, fault: false };

  if (quoted) {
    if (text[valueEnd] !== openingQuote) return { ok: false, fault: false };
    return {
      ok: true,
      fault: false,
      quoted: true,
      quote: openingQuote,
      quoteStart: headEnd,
      quoteEnd: valueEnd,
      valueStart,
      valueEnd,
      matchEnd: valueEnd + 1,
    };
  }

  if (!isUnquotedTerminator(text, valueEnd)) {
    return { ok: false, fault: false };
  }
  return {
    ok: true,
    fault: false,
    quoted: false,
    quote: null,
    quoteStart: null,
    quoteEnd: null,
    valueStart,
    valueEnd,
    matchEnd: valueEnd,
  };
}
```

The loop deliberately reaches a 256th allowed code unit so that a 255-prefix
cannot be accepted from a longer value.

- [ ] **Step 3: Enumerate heads and create value-free Candidates**

```javascript
function namedCredentialCandidates(text) {
  try {
    const candidates = [];
    ASSIGNMENT_HEAD_PATTERN.lastIndex = 0;
    for (const match of text.matchAll(ASSIGNMENT_HEAD_PATTERN)) {
      const groups = match.groups;
      const indices = match.indices?.groups;
      const name = groups?.name;
      if (typeof name !== "string" || !CREDENTIAL_NAME_PATTERN.test(name)) {
        continue;
      }

      const fallbackStart = match.index;
      const fallbackHeadEnd =
        typeof fallbackStart === "number" ? fallbackStart + match[0].length : -1;
      const headEnd = indices?.afterSeparator?.[1] ?? fallbackHeadEnd;
      const value = parseBoundedCredentialValue(text, headEnd);
      if (value.fault) return { ok: false, candidates: [] };
      if (!value.ok) continue;

      const candidate = {
        id: candidates.length,
        matchStart: indices?.name?.[0] ?? fallbackStart ?? -1,
        matchEnd: value.matchEnd,
        headEnd,
        nameStart: indices?.name?.[0] ?? -1,
        nameEnd: indices?.name?.[1] ?? -1,
        optional: typeof groups?.optional === "string",
        questionStart: indices?.optional?.[0] ?? null,
        questionEnd: indices?.optional?.[1] ?? null,
        separator: groups?.separator === "=" ? "=" : ":",
        separatorStart: indices?.separator?.[0] ?? -1,
        separatorEnd: indices?.separator?.[1] ?? -1,
        quoted: value.quoted,
        quote: value.quote,
        quoteStart: value.quoteStart,
        quoteEnd: value.quoteEnd,
        valueStart: value.valueStart,
        valueEnd: value.valueEnd,
        positionsValid: false,
      };
      candidate.positionsValid = candidatePositionsValid(text, candidate);
      candidates.push(Object.freeze(candidate));
    }
    ASSIGNMENT_HEAD_PATTERN.lastIndex = 0;
    return { ok: true, candidates };
  } catch {
    ASSIGNMENT_HEAD_PATTERN.lastIndex = 0;
    return { ok: false, candidates: [] };
  }
}
```

`candidatePositionsValid` must implement every invariant from correction-design
section 6, including the exact question-token range and left boundary. It must
compare text slices transiently and must not add `name` or `value` fields to the
Candidate.

Use this complete validator:

```javascript
function validRange(start, end, textLength) {
  return (
    Number.isInteger(start) &&
    Number.isInteger(end) &&
    start >= 0 &&
    end >= start &&
    end <= textLength
  );
}

function isCredentialNameCodeUnit(code) {
  return (
    (code >= 48 && code <= 57) ||
    (code >= 65 && code <= 90) ||
    (code >= 97 && code <= 122) ||
    code === 36 ||
    code === 45 ||
    code === 95
  );
}

function candidatePositionsValid(text, candidate) {
  const ranges = [
    [candidate.matchStart, candidate.matchEnd],
    [candidate.nameStart, candidate.nameEnd],
    [candidate.separatorStart, candidate.separatorEnd],
    [candidate.valueStart, candidate.valueEnd],
  ];
  if (ranges.some(([start, end]) => !validRange(start, end, text.length))) {
    return false;
  }
  if (
    !Number.isInteger(candidate.headEnd) ||
    candidate.headEnd < candidate.separatorEnd ||
    candidate.headEnd > candidate.valueStart ||
    candidate.matchStart !== candidate.nameStart ||
    candidate.separatorEnd !== candidate.separatorStart + 1 ||
    candidate.valueEnd - candidate.valueStart < 16 ||
    candidate.valueEnd - candidate.valueStart > 255
  ) {
    return false;
  }

  const name = text.slice(candidate.nameStart, candidate.nameEnd);
  if (
    name.length === 0 ||
    [...name].some((character) =>
      !isCredentialNameCodeUnit(character.charCodeAt(0))) ||
    !CREDENTIAL_NAME_PATTERN.test(name) ||
    (candidate.nameStart > 0 &&
      isCredentialNameCodeUnit(text.charCodeAt(candidate.nameStart - 1)))
  ) {
    return false;
  }

  const questionBoundary = candidate.optional
    ? candidate.questionEnd
    : candidate.nameEnd;
  if (candidate.optional) {
    if (
      !validRange(candidate.questionStart, candidate.questionEnd, text.length) ||
      candidate.questionStart !== candidate.nameEnd ||
      candidate.questionEnd !== candidate.questionStart + 1 ||
      text[candidate.questionStart] !== "?"
    ) {
      return false;
    }
  } else if (
    candidate.questionStart !== null ||
    candidate.questionEnd !== null
  ) {
    return false;
  }

  if (
    !/^\s*$/u.test(text.slice(questionBoundary, candidate.separatorStart)) ||
    text.slice(candidate.separatorStart, candidate.separatorEnd) !==
      candidate.separator ||
    !/^\s*$/u.test(text.slice(candidate.separatorEnd, candidate.headEnd))
  ) {
    return false;
  }

  if (candidate.quoted) {
    return (
      (candidate.quote === "'" || candidate.quote === '"') &&
      candidate.quoteStart === candidate.headEnd &&
      candidate.valueStart === candidate.quoteStart + 1 &&
      candidate.valueEnd === candidate.quoteEnd &&
      candidate.matchEnd === candidate.quoteEnd + 1 &&
      text[candidate.quoteStart] === candidate.quote &&
      text[candidate.quoteEnd] === candidate.quote
    );
  }

  return (
    candidate.quote === null &&
    candidate.quoteStart === null &&
    candidate.quoteEnd === null &&
    candidate.headEnd === candidate.valueStart &&
    candidate.matchEnd === candidate.valueEnd
  );
}
```

- [ ] **Step 4: Fail closed on an enumeration fault**

At the credential stage in `classifyBlob`:

```javascript
const namedResult = namedCredentialCandidates(text);
if (!namedResult.ok) {
  return [{ category: "unscannable", path, count: 1 }];
}
const namedCandidates = namedResult.candidates;
```

Do not convert a normal grammar miss into `unscannable`. Only an unexpected
enumeration/metadata fault takes this route.

- [ ] **Step 5: Prove the focused P1 matrix GREEN**

```powershell
node --test --test-name-pattern="head-first candidates" scripts/check-push-graph.test.mjs
if ($LASTEXITCODE -ne 0) { throw "K1_T3_HEAD_FIRST_GREEN_FAILED" }
```

Expected: all leading-name, true-overlap, decoy, and invalid-earlier-head tests
pass with exact counts.

### Task 5: Tighten AST mapping to the value-free Candidate

**Files:**
- Modify: `scripts/check-push-graph.mjs`
- Test: `scripts/check-push-graph.test.mjs`

- [ ] **Step 1: Remove stored name and value fields from AST validation**

Use only positions and transient slices:

```javascript
const candidateName = text.slice(candidate.nameStart, candidate.nameEnd);
const candidateType = text.slice(candidate.valueStart, candidate.valueEnd);
if (
  node.name.getStart(sourceFile, false) !== candidate.nameStart ||
  node.name.end !== candidate.nameEnd ||
  node.type.getStart(sourceFile, false) !== candidate.valueStart ||
  node.type.end !== candidate.valueEnd ||
  node.name.getText(sourceFile) !== candidateName ||
  node.type.typeName.getText(sourceFile) !== candidateType
) {
  continue;
}
```

- [ ] **Step 2: Require exact optional-question positions**

```javascript
const questionStart = node.questionToken?.getStart(sourceFile, false) ?? null;
const questionEnd = node.questionToken?.end ?? null;
if (
  questionStart !== candidate.questionStart ||
  questionEnd !== candidate.questionEnd
) {
  continue;
}
```

- [ ] **Step 3: Make all mapping ambiguity globally fail closed**

Before parsing, reject AST suppression if any relevant Candidate has invalid
positions or if any `nameStart` occurs more than once. During traversal, track
both matched `candidate.id` and the matched PropertySignature start. If either
is assigned twice, return a new empty Set. Do not remove the Raw-Candidates.

- [ ] **Step 4: Run all AST and overlap combinations**

```powershell
node --test --test-name-pattern="TypeScript AST credential suppression|head-first candidates" scripts/check-push-graph.test.mjs
if ($LASTEXITCODE -ne 0) { throw "K1_T3_AST_OVERLAP_GREEN_FAILED" }
```

Expected: true property signatures alone suppress exactly their Candidates;
overlaps inside string, template, comment, or runtime code remain counted.

### Task 6: Add performance and non-leakage acceptance tests

**Files:**
- Modify: `scripts/check-push-graph.test.mjs`
- Test: `scripts/check-push-graph.test.mjs`

- [ ] **Step 1: Add three adversarial tests with five-second timeouts**

Add this import:

```javascript
import { performance } from "node:perf_hooks";
```

Add the helper and three executable fixtures:

```javascript
function assertCompletesWithinFiveSeconds(label, operation) {
  const started = performance.now();
  const result = operation();
  const elapsed = performance.now() - started;
  assert.ok(elapsed < 5_000, `${label}: exceeded five seconds`);
  return result;
}

test("head-first enumeration stays bounded on a maximal name run", {
  timeout: 5_000,
}, () => {
  const fragment = ["to", "ken", "_safe_"].join("");
  const content = fragment.repeat(
    Math.floor((1024 * 1024 - 64) / fragment.length),
  );
  const findings = assertCompletesWithinFiveSeconds(
    "maximal-name-run",
    () => classifyBlob("notes/maximal-name.txt", Buffer.from(content)),
  );
  assert.deepEqual(findings, []);
});

test("head-first enumeration stays bounded on dense true overlaps", {
  timeout: 5_000,
}, () => {
  const first = ["PASS", "WORD"].join("");
  const second = ["PREVIEW", "CLIENT", "SECRET"].join("_");
  const value = ["Synthetic", "Scanner", "Fixture", "Value"].join("");
  const segment = [
    first,
    "=",
    "A".repeat(16),
    ".",
    second,
    "=",
    value,
    ";",
  ].join("");
  const repetitions = 4_000;
  const findings = assertCompletesWithinFiveSeconds(
    "dense-overlaps",
    () => classifyBlob(
      "notes/dense-overlap.txt",
      Buffer.from(segment.repeat(repetitions)),
    ),
  );
  assert.deepEqual(
    findings.map(({ category, count }) => [category, count]),
    [["credential_like", repetitions * 2]],
  );
});

test("head-first AST adjudication stays bounded near the blob limit", {
  timeout: 5_000,
}, () => {
  const name = ["PREVIEW", "CLIENT", "SECRET"].join("_");
  const typeName = ["Synthetic", "Scanner", "Fixture", "Value"].join("");
  const property = ["interface Config { ", name, ": ", typeName, "; }\n"].join("");
  const statement = "const safeValue = 0;\n";
  const repetitions = Math.floor(
    (1024 * 1024 - property.length - 64) / statement.length,
  );
  const content = property + statement.repeat(repetitions);
  assert.ok(Buffer.byteLength(content) <= 1024 * 1024);
  const findings = assertCompletesWithinFiveSeconds(
    "near-limit-typescript",
    () => classifyBlob("src/near-limit.ts", Buffer.from(content)),
  );
  assert.deepEqual(findings, []);
});
```

The fixtures are synthetic and assertion messages contain no candidate name,
value, assignment, or source.

- [ ] **Step 2: Re-run selfscan and the complete scanner suite**

```powershell
node --test --test-name-pattern="scanner and test source are clean fixtures for their own content rules" scripts/check-push-graph.test.mjs
if ($LASTEXITCODE -ne 0) { throw "K1_T3_SELFSCAN_FAILED" }

node --test scripts/check-push-graph.test.mjs
if ($LASTEXITCODE -ne 0) { throw "K1_T3_FULL_SCANNER_FAILED" }
```

### Task 7: Run full repository acceptance

**Files:**
- Test: `scripts/check-push-graph.test.mjs`
- Test: `scripts/check-project-control-k1.mjs`

- [ ] **Step 1: Run K1 control and exact diff checks**

```powershell
npm run check:k1-control
if ($LASTEXITCODE -ne 0) { throw "K1_T3_CONTROL_FAILED" }

$allowed = @(
  "docs/superpowers/plans/2026-08-26-aurelia-k1-task3-overlap-enumeration-correction.md",
  "docs/superpowers/plans/2026-08-26-aurelia-k1-task3-string-type-bypass.md",
  "docs/superpowers/specs/2026-08-26-aurelia-k1-task3-overlap-enumeration-correction-design.md",
  "docs/superpowers/specs/2026-08-26-aurelia-k1-task3-string-type-bypass-design.md",
  "docs/superpowers/specs/2026-08-27-aurelia-linux-workstation-migration-recovery-design.md",
  "docs/superpowers/plans/2026-08-27-aurelia-linux-workstation-migration-recovery.md",
  "scripts/check-push-graph.mjs",
  "scripts/check-push-graph.test.mjs"
) | Sort-Object
$committedSinceStart = @(git diff --name-only e930aab..HEAD) | Sort-Object -Unique
$working = @(
  git diff --name-only
  git ls-files --others --exclude-standard
) | Sort-Object -Unique
$forbiddenCommitted = @($committedSinceStart | Where-Object { $_ -notin $allowed })
$forbiddenWorking = @($working | Where-Object { $_ -notin $allowed })
if ($forbiddenCommitted.Count -ne 0 -or $forbiddenWorking.Count -ne 0) {
  throw "K1_T3_SCOPE_MISMATCH"
}

git diff --exit-code HEAD -- package.json package-lock.json docs/project-control/K1-STATUS.md
if ($LASTEXITCODE -ne 0) { throw "K1_T3_FORBIDDEN_SURFACE_CHANGED" }
git diff --check
if ($LASTEXITCODE -ne 0) { throw "K1_T3_WORKTREE_DIFF_INVALID" }
git diff --cached --check
if ($LASTEXITCODE -ne 0) { throw "K1_T3_INDEX_DIFF_INVALID" }
```

Before an implementation commit, the working diff may contain the two
uncommitted implementation files plus the separately approved correction
documents. Staging must remain empty until a later explicit commit
authorization defines the exact staged subset.

- [ ] **Step 2: Run the real publication graph**

```powershell
node scripts/check-push-graph.mjs --base origin/codex/aurelia-vorbereitung --head HEAD --mode full
if ($LASTEXITCODE -ne 1) { throw "K1_T3_REAL_GRAPH_EXIT_MISMATCH" }
```

Expected: exit 1 because historical reachable findings remain. Every emitted
line contains only `category`, `blob`, `path`, and `count`.

### Task 8: Execute focused Spec review

**Files:**
- Read: both Task-3 designs and both implementation files

- [ ] **Step 1: Create a sanitized review packet**

Provide only both approved designs, the exact two-file implementation diff,
the RED/GREEN evidence, performance results, real-graph safe output shape, and
scope checks. Exclude chat history, raw analyses, secrets, V3 source material,
and unrelated product code.

- [ ] **Step 2: Apply this decision contract**

```text
Review only the supplied AURELIA Task-3 correction designs, two-file scanner
diff and fresh evidence. Verify maximal full-name grammar, head-only
enumeration, independent bounded value parsing, exact UTF-16 positions,
overlap counts, value-free Candidates, fail-closed enumeration and AST errors,
no content leakage, O(n+c+a), unchanged public contracts and exact scope.
Treat missing evidence as FAIL. Return VERDICT PASS or FAIL and only actionable
P0-P2 findings with contract, file evidence, impact and minimal correction.
```

On FAIL, do not start Quality/Security review or commit. One correction loop is
allowed; a remaining or systemic P0-P2 stops for consolidation.

### Task 9: Execute conditional Sol-xHigh Quality/Security review

**Files:**
- Read: same sanitized packet as Task 8

- [ ] **Step 1: Confirm explicit Spec-PASS with no open P0-P2**

Without this precondition, stop.

- [ ] **Step 2: Review adversarial safety and implementation quality**

```text
Perform an independent AURELIA security and code-quality review of only the
Task-3 head-first enumeration and AST-adjudication diff. Spec compliance has
passed. Search for lost or duplicate candidates, boundary and 255/256 errors,
quoted/unquoted inconsistencies, Unicode-position mistakes, parser recovery,
AST cross-suppression, value leakage, catastrophic regex behavior, excess
memory and tests that pass without proving their claim. Return VERDICT PASS or
FAIL with exact actionable P0-P2 evidence; FINDINGS none when clean.
```

The primary instance reproduces every finding. A remaining P0-P2 stops.

### Task 10: Prepare a conditional local implementation checkpoint

**Files:**
- Stage only when separately authorized:
  - `scripts/check-push-graph.mjs`
  - `scripts/check-push-graph.test.mjs`

- [ ] **Step 1: Re-run all gates immediately before staging**

```powershell
node --test scripts/check-push-graph.test.mjs
if ($LASTEXITCODE -ne 0) { throw "K1_T3_PRECOMMIT_SCANNER_FAILED" }
npm run check:k1-control
if ($LASTEXITCODE -ne 0) { throw "K1_T3_PRECOMMIT_CONTROL_FAILED" }
git diff --check
if ($LASTEXITCODE -ne 0) { throw "K1_T3_PRECOMMIT_DIFF_INVALID" }
```

- [ ] **Step 2: Stop unless a new authorization permits the exact commit**

When and only when separately authorized:

```powershell
git add -- scripts/check-push-graph.mjs scripts/check-push-graph.test.mjs
git diff --cached --check
if ($LASTEXITCODE -ne 0) { throw "K1_T3_PRECOMMIT_INDEX_INVALID" }
$staged = @(git diff --cached --name-only) | Sort-Object
$expected = @(
  "scripts/check-push-graph.mjs",
  "scripts/check-push-graph.test.mjs"
) | Sort-Object
if (@(Compare-Object $expected $staged).Count -ne 0) {
  throw "K1_T3_PRECOMMIT_SCOPE_MISMATCH"
}
git commit -m "fix(security): enumerate overlapping credential candidates"
```

No push is permitted.

## Final stop condition

The future correction run is complete only when:

- the E4 quality-review findings `K1-T3-Q-NEW-01`, `K1-T3-Q-NEW-02` and
  `K1-T3-Q-NEW-03` are closed by this run's RED/GREEN tests and the amended
  design grammar (§1.1, §7, §11, §12 of the amended design; Amendierung
  2026-08-28) — `K1-T3-Q-NEW-04` is rejected and requires no change;
- the three known P1 reproductions are visibly RED before correction and GREEN
  afterward with exact counts `1`, `1`, and `2`;
- every value is parsed independently with exact 16/255 bounds and a 256 cap;
- all valid overlapping Heads remain independently counted;
- Candidates contain positions but no name or value strings;
- AST suppression remains exact and every ambiguity falls to Raw-Count;
- all scanner, K1, performance, non-leakage, real-graph, diff and scope gates
  pass freshly;
- Spec and independent Sol-xHigh Quality/Security verdicts are both PASS;
- Task 4 is only eligible, not started;
- no unauthorized commit, push, status, package, server, V3, credential or
  history action occurred.
