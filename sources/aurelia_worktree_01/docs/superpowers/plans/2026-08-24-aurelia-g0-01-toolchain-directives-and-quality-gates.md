# AURELIA G0 Toolchain, Directives, and Quality Gates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish a cross-platform, fail-closed G0 toolchain, pin the three validator dependencies, publish the approved developer directives, and expose local governance checks without touching GitHub, Chrome, or M-G1.

**Architecture:** A shell-free Node launcher discovers every MJS test recursively and refuses an empty suite. Small read-only governance modules validate directives and documentation; `scripts/governance-contract.mjs` is the stable CLI that later plans extend through exported error collectors. The project constitution remains the product source, while the new `GOVERNANCE.md` becomes the process source.

**Tech Stack:** Node.js 22 ESM, `node:test`, `node:assert/strict`, Ajv 8.20.0, ajv-formats 3.0.1, canonicalize 4.0.0, npm, Markdown.

---

## Scope and file map

This plan may change only the following repository surfaces:

- Create `scripts/run-mjs-tests.mjs`: deterministic, shell-free recursive MJS test launcher.
- Create `scripts/run-mjs-tests.test.mjs`: discovery, order, argument, and zero-test regression tests.
- Create `tsconfig.governance.json`: `checkJs`/`noEmit` contract for every governance MJS module.
- Create `scripts/governance/constants.mjs`: repository identity, canonical paths, and directive fragments.
- Create `scripts/governance/diagnostics.mjs`: stable machine- and human-readable failures.
- Create `scripts/governance/directives.mjs`: read-only directive and documentation checks.
- Create `scripts/governance/directives.test.mjs`: directive contract tests.
- Create `scripts/governance-contract.mjs`: local read-only CLI and exported composition API.
- Create `scripts/governance-contract.test.mjs`: CLI exit and no-write tests.
- Create `GOVERNANCE.md`: complete human process directive for G0.
- Modify `AGENTS.project.md`: compact binding pointer and source precedence.
- Modify `docs/00-index.md`: governance links and `docs/25-offen.md` link.
- Modify `docs/23-id-schema.md`: governance namespaces, complete WV, accepted X catalogue.
- Modify `docs/07-identity.md`: preview identity versus M-G1 passkeys under WV03.
- Modify `package.json` and `package-lock.json`: exact dependency pins and quality scripts.

Do not modify `src/`, `server/`, `migrations/`, `vite.config.ts`, `startup.sh`, the final design specification, or any remote/server state. A governance check in this plan validates only the surfaces introduced here; register and ledger checks are added by Plans 02–04.

Before the first Plan-01 edit, pin the immutable diff base in Git metadata:

```powershell
$basePath = git rev-parse --git-path aurelia-plan-01-base
$baseCommit = git rev-parse HEAD
if ($baseCommit -notmatch '^[0-9a-f]{40}$') { throw 'expected a full 40-character Plan-01 base SHA' }
Set-Content -LiteralPath $basePath -Value $baseCommit -NoNewline
Get-Content -LiteralPath $basePath
```

Expected: the exact full SHA captured before any Plan-01 change. Every final file-boundary check reads this file; it never substitutes `HEAD`, a branch name, or a moving merge base.

### Task 1: Replace the Windows-fragile MJS glob and forbid null suites

**Files:**

- Create: `scripts/run-mjs-tests.mjs`
- Create: `scripts/run-mjs-tests.test.mjs`
- Modify: `package.json:18`

- [ ] **Step 1: Write the failing discovery and null-suite tests**

Create `scripts/run-mjs-tests.test.mjs` with this complete content:

```js
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";
import {
  buildMjsTestArgs,
  discoverMjsTests,
  runMjsTests,
} from "./run-mjs-tests.mjs";

test("discovers nested MJS tests once in lexical order", () => {
  const root = mkdtempSync(join(tmpdir(), "aurelia-mjs-tests-"));
  try {
    mkdirSync(join(root, "nested"));
    writeFileSync(join(root, "z.test.mjs"), "export {};\n");
    writeFileSync(join(root, "nested", "a.test.mjs"), "export {};\n");
    writeFileSync(join(root, "nested", "a-copy.test.mjs"), "export {};\n");
    writeFileSync(join(root, "nested", "ignore.mjs"), "export {};\n");
    assert.deepEqual(discoverMjsTests(root), [
      join(root, "nested", "a-copy.test.mjs"),
      join(root, "nested", "a.test.mjs"),
      join(root, "z.test.mjs"),
    ]);
    assert.equal(new Set(discoverMjsTests(root)).size, discoverMjsTests(root).length);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test("refuses to report success when no MJS test exists", () => {
  assert.throws(
    () => buildMjsTestArgs([]),
    /refusing to report success with zero MJS tests/,
  );
});

test("passes explicit files to node without a shell glob", () => {
  assert.deepEqual(buildMjsTestArgs(["a.test.mjs", "b.test.mjs"]), [
    "--experimental-strip-types",
    "--test",
    "a.test.mjs",
    "b.test.mjs",
  ]);
});

test("propagates a failing child test exit code", () => {
  const root = mkdtempSync(join(tmpdir(), "aurelia-mjs-failure-"));
  try {
    const failing = join(root, "intentional-failure.test.mjs");
    writeFileSync(failing, 'import { test } from "node:test"; test("fails", () => { throw new Error("fixture failure"); });\n');
    assert.notEqual(runMjsTests([failing], { stdio: "pipe" }), 0);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test("the direct runner exits nonzero for an empty discovery root", () => {
  const root = mkdtempSync(join(tmpdir(), "aurelia-mjs-empty-"));
  try {
    const result = spawnSync(process.execPath, [
      join(import.meta.dirname, "run-mjs-tests.mjs"), "--root", root,
    ], { encoding: "utf8", shell: false });
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /zero MJS tests/);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test("executes every discovered fixture exactly once", () => {
  const root = mkdtempSync(join(tmpdir(), "aurelia-mjs-once-"));
  try {
    const files = ["one", "two"].map((name) => {
      const marker = join(root, `${name}.count`);
      const file = join(root, `${name}.test.mjs`);
      writeFileSync(file, `import { appendFileSync } from "node:fs"; import { test } from "node:test"; test("${name}", () => appendFileSync(${JSON.stringify(marker)}, "x"));\n`);
      return file;
    });
    assert.equal(runMjsTests(discoverMjsTests(root), { stdio: "pipe" }), 0);
    for (const name of ["one", "two"]) assert.equal(readFileSync(join(root, `${name}.count`), "utf8"), "x");
    assert.equal(files.length, discoverMjsTests(root).length);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test("fails closed for child signal/null status and spawn errors", () => {
  const root = mkdtempSync(join(tmpdir(), "aurelia-mjs-signal-"));
  try {
    const signalled = join(root, "signal.test.mjs");
    writeFileSync(signalled, 'process.kill(process.pid, "SIGTERM");\n');
    assert.notEqual(runMjsTests([signalled], { stdio: "pipe" }), 0);
    assert.throws(() => runMjsTests([signalled], { stdio: "pipe", executable: join(root, "missing-node") }));
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});
```

- [ ] **Step 2: Run the test to prove the runner is absent**

Run:

```powershell
node --test scripts/run-mjs-tests.test.mjs
```

Expected: FAIL with `ERR_MODULE_NOT_FOUND` for `scripts/run-mjs-tests.mjs`; zero passing tests is not acceptable evidence.

- [ ] **Step 3: Implement deterministic discovery and shell-free execution**

Create `scripts/run-mjs-tests.mjs` with this complete content:

```js
#!/usr/bin/env node
import { readdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));

export function discoverMjsTests(root = SCRIPT_DIR) {
  const discovered = [];
  const visit = (directory) => {
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      const absolute = join(directory, entry.name);
      if (entry.isDirectory()) visit(absolute);
      if (entry.isFile() && entry.name.endsWith(".test.mjs")) {
        discovered.push(absolute);
      }
    }
  };
  visit(resolve(root));
  return [...new Set(discovered)].sort((left, right) => left < right ? -1 : left > right ? 1 : 0);
}

export function buildMjsTestArgs(files) {
  if (files.length === 0) {
    throw new Error("refusing to report success with zero MJS tests");
  }
  return ["--experimental-strip-types", "--test", ...files];
}

export function runMjsTests(files = discoverMjsTests(), { stdio = "inherit", executable = process.execPath } = {}) {
  const result = spawnSync(executable, buildMjsTestArgs(files), {
    cwd: resolve(SCRIPT_DIR, ".."),
    env: process.env,
    shell: false,
    stdio,
  });
  if (result.error) throw result.error;
  return result.status ?? 1;
}

if (resolve(process.argv[1] ?? "") === fileURLToPath(import.meta.url)) {
  const rootIndex = process.argv.indexOf("--root");
  const root = rootIndex === -1 ? SCRIPT_DIR : process.argv[rootIndex + 1];
  if (!root) throw new Error("--root requires a directory");
  process.exitCode = runMjsTests(discoverMjsTests(root));
}
```

- [ ] **Step 4: Run the focused test and require three passes**

Run:

```powershell
node --test scripts/run-mjs-tests.test.mjs
```

Expected: `tests 7`, `pass 7`, `fail 0`. The deliberately failing/signalled children are captured by parent tests and prove nonzero propagation without failing the outer suite; both marker fixtures exist exactly once.

- [ ] **Step 5: Route the package test through the runner**

Replace the current `test` script in `package.json` and add `test:mjs` so the script block contains exactly:

```json-fragment
"test:mjs": "node scripts/run-mjs-tests.mjs",
"test": "npm run test:mjs && node --experimental-strip-types --test src/lib/app-data/app-data.test.ts src/lib/auth/gate-identity.test.ts"
```

- [ ] **Step 6: Run all MJS tests and inspect the reported count**

Run:

```powershell
npm run test:mjs
```

Expected: exit 0, more than zero tests, and the output includes tests from `scripts/run-mjs-tests.test.mjs` and `scripts/canon-contract.test.mjs`. Compare `discoverMjsTests()` with `Get-ChildItem scripts -Recurse -Filter *.test.mjs`: identical code-unit-sorted sets, no duplicate path, and the runner process itself never appears as a nested test invocation.

- [ ] **Step 7: Commit the runner fix**

```powershell
git add scripts/run-mjs-tests.mjs scripts/run-mjs-tests.test.mjs package.json
git commit -m "test: make MJS discovery cross-platform"
```

### Task 2: Pin the validator dependencies exactly

**Files:**

- Modify: `package.json:22-89`
- Modify: `package-lock.json`

- [ ] **Step 1: Add an exact-pin regression test**

Append this test to `scripts/run-mjs-tests.test.mjs`:

```js
test("governance dependencies are exact direct pins", async () => {
  const packageJson = JSON.parse(
    await import("node:fs/promises").then(({ readFile }) =>
      readFile(new URL("../package.json", import.meta.url), "utf8"),
    ),
  );
  assert.deepEqual(
    {
      ajv: packageJson.devDependencies.ajv,
      "ajv-formats": packageJson.devDependencies["ajv-formats"],
      canonicalize: packageJson.devDependencies.canonicalize,
    },
    {
      ajv: "8.20.0",
      "ajv-formats": "3.0.1",
      canonicalize: "4.0.0",
    },
  );
});
```

- [ ] **Step 2: Run the focused test and observe the missing pins**

Run:

```powershell
node --test scripts/run-mjs-tests.test.mjs
```

Expected: FAIL in `governance dependencies are exact direct pins`; the three actual values are `undefined`.

- [ ] **Step 3: Install the three exact development dependencies**

Run:

```powershell
npm install --save-dev --save-exact ajv@8.20.0 ajv-formats@3.0.1 canonicalize@4.0.0
```

Expected: exit 0; `package.json` contains no `^` or `~` for these three names and `package-lock.json` records their integrity data.

- [ ] **Step 4: Re-run the exact-pin test**

Run:

```powershell
node --test scripts/run-mjs-tests.test.mjs
```

Expected: `tests 8`, `pass 8`, `fail 0`.

- [ ] **Step 5: Prove npm resolves the requested versions directly**

Run:

```powershell
npm ls ajv@8.20.0 ajv-formats@3.0.1 canonicalize@4.0.0 --depth=0
```

Expected: all three packages appear directly under `app-builder-workspace`; no `invalid` or `extraneous` marker.

- [ ] **Step 6: Commit the dependency pins**

```powershell
git add package.json package-lock.json scripts/run-mjs-tests.test.mjs
git commit -m "build: pin governance validator dependencies"
```

### Task 2A: Type-check every governance MJS contract

**Files:**

- Create: `tsconfig.governance.json`
- Modify: `package.json`
- Modify: `scripts/run-mjs-tests.test.mjs`

- [ ] **Step 1: Add a failing package-contract assertion**

Append:

```js
test("package exposes the governance JavaScript typecheck", async () => {
  const packageJson = JSON.parse(
    await import("node:fs/promises").then(({ readFile }) =>
      readFile(new URL("../package.json", import.meta.url), "utf8"),
    ),
  );
  assert.equal(packageJson.scripts["typecheck:governance"], "tsc -p tsconfig.governance.json");
});
```

- [ ] **Step 2: Run the focused test and observe the missing script**

Run `node --test scripts/run-mjs-tests.test.mjs`.

Expected: FAIL only because `typecheck:governance` is `undefined`.

- [ ] **Step 3: Create the complete governance compiler contract**

Create `tsconfig.governance.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "allowJs": true,
    "checkJs": true,
    "noEmit": true,
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "types": ["node"],
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["scripts/**/*.mjs", "src/lib/concept/**/*.ts"],
  "exclude": ["node_modules", "dist", ".worktrees"]
}
```

This deliberately applies `checkJs` to every planned MJS validator while reusing the product-canon TypeScript types. It emits no files.

- [ ] **Step 4: Add and run the package entry point**

Add to `package.json`:

```json-fragment
"typecheck:governance": "tsc -p tsconfig.governance.json"
```

Run:

```powershell
npm run typecheck:governance
node --test scripts/run-mjs-tests.test.mjs
```

Expected: both exit 0; TypeScript emits no JavaScript and the focused suite includes the package-contract assertion.

- [ ] **Step 5: Commit the MJS type gate**

```powershell
git add tsconfig.governance.json package.json scripts/run-mjs-tests.test.mjs
git commit -m "build: typecheck governance JavaScript contracts"
```

### Task 3: Encode the stable repository constants and diagnostics

**Files:**

- Create: `scripts/governance/constants.mjs`
- Create: `scripts/governance/diagnostics.mjs`
- Test: `scripts/governance/directives.test.mjs`

- [ ] **Step 1: Write failing tests for constants and diagnostic order**

Create `scripts/governance/directives.test.mjs` with this content:

```js
import assert from "node:assert/strict";
import { test } from "node:test";
import {
  GOVERNANCE_REGISTER_PATHS,
  REPOSITORY_ID,
  SCHEMA_VERSION,
} from "./constants.mjs";
import { formatDiagnostics, sortDiagnostics } from "./diagnostics.mjs";

test("governance constants bind the one repository and four registers", () => {
  assert.equal(REPOSITORY_ID, "redshift-three67/aurelia");
  assert.equal(SCHEMA_VERSION, "aurelia-governance-v1");
  assert.deepEqual(GOVERNANCE_REGISTER_PATHS, [
    "docs/governance/data-processing-inventory.md",
    "docs/governance/gate-register.md",
    "docs/governance/risk-register.md",
    "docs/governance/traceability-register.md",
  ]);
});

test("diagnostics are stable and identify file, record, and rule", () => {
  assert.equal(
    formatDiagnostics([
      { file: "z.md", record: "REQ-002", rule: "R-2", message: "second" },
      { file: "Ä.md", record: "REQ-003", rule: "R-3", message: "accent" },
      { file: "a.md", record: "REQ-001", rule: "R-1", message: "first" },
    ]),
    "[governance] 3 violation(s)\n" +
      "- a.md :: REQ-001 :: R-1 :: first\n" +
      "- z.md :: REQ-002 :: R-2 :: second\n" +
      "- Ä.md :: REQ-003 :: R-3 :: accent",
  );
});

test("diagnostic order uses code units for NUL, case, and accents", () => {
  const rows = [
    { file: "a", record: "A", rule: "R", message: "upper" },
    { file: "a", record: "ä", rule: "R", message: "accent" },
    { file: "a", record: "a", rule: "R", message: "lower" },
    { file: "a", record: "\u0000", rule: "R", message: "nul" },
  ];
  assert.deepEqual(sortDiagnostics(rows).map((row) => row.message), ["nul", "upper", "lower", "accent"]);
});
```

- [ ] **Step 2: Run the test to verify both modules are absent**

Run:

```powershell
node --test scripts/governance/directives.test.mjs
```

Expected: FAIL with `ERR_MODULE_NOT_FOUND` for `scripts/governance/constants.mjs`.

- [ ] **Step 3: Create the immutable constants**

Create `scripts/governance/constants.mjs`:

```js
export const REPOSITORY_ID = "redshift-three67/aurelia";
export const SCHEMA_VERSION = "aurelia-governance-v1";
export const GOVERNANCE_REGISTER_PATHS = Object.freeze([
  "docs/governance/data-processing-inventory.md",
  "docs/governance/gate-register.md",
  "docs/governance/risk-register.md",
  "docs/governance/traceability-register.md",
]);
export const INITIAL_NO_WAIVER_GATES = Object.freeze([
  "GATE-24X7",
  "GATE-ART9",
  "GATE-CUDA",
  "GATE-DATAFLOW",
  "GATE-G0",
  "GATE-HARDWARE",
  "GATE-MODULE",
  "GATE-PILOT",
  "GATE-PROFILE",
]);
```

- [ ] **Step 4: Create deterministic diagnostics**

Create `scripts/governance/diagnostics.mjs`:

```js
export function sortDiagnostics(diagnostics) {
  const key = (value) => [value.file, value.record, value.rule, value.message].join("\u0000");
  return [...diagnostics].sort((left, right) => {
    const a = key(left);
    const b = key(right);
    return a < b ? -1 : a > b ? 1 : 0;
  });
}

export function formatDiagnostics(diagnostics) {
  const sorted = sortDiagnostics(diagnostics);
  return [
    `[governance] ${sorted.length} violation(s)`,
    ...sorted.map(
      ({ file, record, rule, message }) =>
        `- ${file} :: ${record} :: ${rule} :: ${message}`,
    ),
  ].join("\n");
}
```

- [ ] **Step 5: Re-run the focused test**

Run:

```powershell
node --test scripts/governance/directives.test.mjs
```

Expected: `tests 3`, `pass 3`, `fail 0`.

- [ ] **Step 6: Commit constants and diagnostics**

```powershell
git add scripts/governance/constants.mjs scripts/governance/diagnostics.mjs scripts/governance/directives.test.mjs
git commit -m "feat: add deterministic governance diagnostics"
```

### Task 4: Publish and verify the process constitution

**Files:**

- Create: `GOVERNANCE.md`
- Modify: `AGENTS.project.md:24-103`
- Create: `scripts/governance/directives.mjs`
- Modify: `scripts/governance/directives.test.mjs`

- [ ] **Step 1: Add a failing test for all binding directive clauses**

Append to `scripts/governance/directives.test.mjs`:

```js
import { directiveErrors } from "./directives.mjs";

test("the repository publishes every binding G0 directive", () => {
  assert.deepEqual(directiveErrors(), []);
});
```

- [ ] **Step 2: Run the test and observe the missing process constitution**

Run:

```powershell
node --test scripts/governance/directives.test.mjs
```

Expected: FAIL with `ERR_MODULE_NOT_FOUND` for `scripts/governance/directives.mjs`.

- [ ] **Step 3: Implement the read-only directive checker**

Create `scripts/governance/directives.mjs`:

```js
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const REQUIRED = Object.freeze({
  "AGENTS.project.md": [
    "GOVERNANCE.md",
    "GATE-G0",
    "Reasoning",
    "M-G1",
    "keine ungeprüfte externe Kontextweitergabe",
  ],
  "GOVERNANCE.md": [
    "## Quellenhierarchie",
    "## Funktionstrennung und Reviewfolge",
    "## Verbindliche Arbeitsstrategie",
    "## Reasoning-Eskalation",
    "## Tokenökonomie ohne Qualitätsabbau",
    "## Browser- und Live-Preview-Regel",
    "## Externe LLM-Zuarbeit",
    "## M-G1-Zugriff und In-place-Härtung",
    "## No-Waiver",
    "## Governance-Änderungsakte",
  ],
});

export function directiveErrors(root = ROOT) {
  const errors = [];
  for (const [file, fragments] of Object.entries(REQUIRED)) {
    let text;
    try {
      text = readFileSync(resolve(root, file), "utf8");
    } catch {
      errors.push({ file, record: "DIRECTIVE", rule: "DIR-FILE", message: "missing file" });
      continue;
    }
    for (const fragment of fragments) {
      if (!text.includes(fragment)) {
        errors.push({
          file,
          record: "DIRECTIVE",
          rule: "DIR-CLAUSE",
          message: `missing required fragment: ${fragment}`,
        });
      }
    }
  }
  return errors;
}
```

- [ ] **Step 4: Run the test and capture the exact missing clauses**

Run:

```powershell
node --test scripts/governance/directives.test.mjs
```

Expected: FAIL only in `the repository publishes every binding G0 directive`; diagnostics include missing `GOVERNANCE.md` and missing `AGENTS.project.md` clauses.

- [ ] **Step 5: Create the process constitution**

Create `GOVERNANCE.md` with these complete normative sections:

```markdown
# AURELIA Governance

This file is the process constitution. Product decisions remain in `AGENTS.project.md` and the canonical product sources. G0 does not authorize production data, M-G1 changes, releases, CUDA, USB, emitters, sensors, or external publication.

## Quellenhierarchie

Mandatory law, contracts, technical reality, and verified security evidence cannot be overridden by a repository file. Within this repository the order is: (1) immutable operator approval with REV ID, scope, and commit baseline; (2) `AGENTS.project.md` and this file; (3) machine-readable product and governance registers; (4) approved specifications and ADRs; (5) approved implementation plans; (6) implementation and executable tests; (7) derived Markdown, portal, and UI views. A conflict is never resolved silently: record it as REV or RISK, keep `GATE-G0` red, obtain the accountable decision, then update derived sources.

## Governance-Änderungsakte

Every governance change records affected IDs and baseline, reason and effect, reviewer and evidence, migration or rollback effect, and a new review date. Register history is append-only. Corrections use successor records and formal supersession; old reviews, evidence, events, and approvals remain verifiable.

## Funktionstrennung und Reviewfolge

Every implementation scope has a fresh implementer, an independent spec reviewer, a separate quality/security reviewer, and an independent final reviewer before operator approval. The order is approved specification and plan; TDD implementation and self-review; spec review until approved; quality/security review; correction followed by both affected reviews; sequential verification and evidence capture; final review; operator decision. One implementer owns a file surface at a time. Parallel work requires isolated worktrees and non-overlapping file ownership.

## Verbindliche Arbeitsstrategie

The orchestrator decomposes every approved scope into bounded file-ownership packages and assigns each package to a fresh task agent. The orchestrator integrates; a task agent never approves its own work. After implementation and self-review, a fresh spec reviewer verifies the approved design and acceptance criteria, then a different quality/security reviewer checks correctness, security, privacy, stability, maintainability, and negative cases. If any correction changes the reviewed surface or an acceptance claim, both the spec review and the quality/security review repeat on the corrected baseline before final review. Review evidence always records the exact commit, scope, role, assignee snapshot, and result.

## Reasoning-Eskalation

Reasoning follows impact. `xHigh` remains the approved level for the current G0 planning and every high-assurance implementation or review step derived from it. Before any later level change the orchestrator states in chat the previous and proposed level, affected step, concrete risk, and return point. Work starts only after operator confirmation; downgrades require the same confirmation. A running high-risk task is never downgraded to save tokens or time. REV records store model role, model name, confirmed intended level, scope, and outcome, never private reasoning.

## Tokenökonomie ohne Qualitätsabbau

Token savings are permitted only through bounded scope packages, fixed evidence summaries, small baseline-pinned diff reviews, and reuse of already verified artifacts whose digest and applicability still match. Token savings must never reduce test breadth, negative cases, review independence, required review repetitions, evidence depth, traceability, or gate strictness. If a reused artifact is stale, outside scope, from another baseline, or not independently verifiable, it is regenerated and reviewed.

## Browser- und Live-Preview-Regel

The governance/CLI-only G0 scope changes no user interface, so Chrome live preview adds no valid evidence and is not used. If a later approved scope changes portal text or UI, QA uses a local synthetic browser check against non-production fixtures, verifies desktop/mobile rendering and console errors, and captures no production, tenant, client, Article-9, credential, or server data.

## Externe LLM-Zuarbeit

External model output is untrusted evidence, never an actor, reviewer, approver, privacy, legal, penetration, hardware, or release decision. Before any non-public excerpt, verified provider due diligence and local sanitization are mandatory. Never transmit secrets, credentials, personal or Article-9 data, production-derived configuration, logs, topology, recovery material, server or tenant details, or the complete private repository. Send only the smallest public, synthetic, or sanitized non-production excerpt and verify every finding locally.

## M-G1-Zugriff und In-place-Härtung

G0 and early design use the local repository only and perform no server access. The existing partitioning remains unchanged unless a documented encryption, integrity, or mandatory-boundary finding, explicit operator approval, on-site specialist execution, backup, rollback, and recovery proof require otherwise. A later audit uses only the separately approved forced-command collector contract; an ordinary SSH or shell account is never called read-only. Cleanup, installation, service changes, and privileged commands require a separate signed change plan and are outside G0.

## No-Waiver

`GATE-G0`, `GATE-DATAFLOW`, `GATE-PROFILE`, `GATE-ART9`, `GATE-MODULE`, `GATE-CUDA`, `GATE-HARDWARE`, `GATE-PILOT`, and `GATE-24X7` are no-waiver gates. No direct exception, derived evidence, review, control, helper gate, or other transitive reference may make one green. Unknown, missing, expired, stale, conflicting, or unverifiable prerequisites fail closed and keep the affected gate red.

## Local versus remote proof

`check:governance` is a read-only local validator and never claims live GitHub state. Branch protection, bypass, signatures, CODEOWNERS, required checks, trusted time, external pins, transparency checkpoints, and witness floors require externally pinned evidence. Missing remote evidence is `unknown`, never green.
```

- [ ] **Step 6: Add the compact binding section to the product constitution**

Insert immediately before `## Hard rules` in `AGENTS.project.md`:

```markdown
## Governance directive

`GOVERNANCE.md` is the process constitution and is mandatory for every human or agent change. The source order is immutable operator approval, `AGENTS.project.md` plus `GOVERNANCE.md`, machine-readable registers, approved specifications/plans, implementation/tests, then derived views. Any conflict or unverifiable prerequisite keeps `GATE-G0` red.

Security-, privacy-, operations-, product-, or governance-relevant changes require traceability, independent implementer/spec/quality-security/final review roles, evidence, baseline, and operator approval. Announce and obtain confirmation before every Reasoning-level change. There is no unchecked external context sharing. During G0 there is no M-G1 access; later work preserves partitioning and follows signed, reversible in-place hardening and forced-command collector plans.

The binding work strategy is orchestrator plus fresh task agents, followed by fresh spec review and separate quality/security review; after any material correction both affected reviews repeat. `xHigh` remains approved for current G0 planning and high-assurance execution. Token economy is limited to bounded scope packages, fixed evidence summaries, small pinned diffs, and reuse of still-valid verified artifacts; it never reduces tests, negative cases, review independence, or evidence. Governance-only G0 has no Chrome live preview; later UI work uses only local synthetic browser checks without production data.
```

- [ ] **Step 7: Run the directive contract**

Run:

```powershell
node --test scripts/governance/directives.test.mjs
```

Expected: all tests pass; `directiveErrors()` returns `[]`.

- [ ] **Step 8: Commit the directives**

```powershell
git add GOVERNANCE.md AGENTS.project.md scripts/governance/directives.mjs scripts/governance/directives.test.mjs
git commit -m "docs: establish G0 governance directives"
```

### Task 5: Correct the governance-relevant documentation drift

**Files:**

- Modify: `docs/00-index.md`
- Modify: `docs/23-id-schema.md`
- Modify: `docs/07-identity.md`
- Modify: `scripts/governance/directives.mjs`
- Modify: `scripts/governance/directives.test.mjs`

- [ ] **Step 1: Add exact documentation requirements to the checker**

Extend the `REQUIRED` object in `scripts/governance/directives.mjs` with:

```js-fragment
"docs/00-index.md": [
  "GOVERNANCE.md",
  "governance/traceability-register.md",
  "governance/risk-register.md",
  "governance/data-processing-inventory.md",
  "governance/gate-register.md",
  "25-offen.md",
],
"docs/23-id-schema.md": ["WV01–WV06", "REQ", "CTRL", "RISK", "DATA", "FLOW", "GATE", "REV", "EXC", "EVID", "PROFILE", "ROLE", "COMP", "EVT", "KEY", "KEYREV", "RECEIPT", "POLICYTRANS", "X-Katalog akzeptiert"],
"docs/07-identity.md": ["Preview-Identität", "WV03", "M G1", "Passkeys"],
```

- [ ] **Step 2: Add the repository-level failing assertion**

Append to `scripts/governance/directives.test.mjs`:

```js
test("governance index, IDs, and identity boundary are current", () => {
  const errors = directiveErrors();
  assert.deepEqual(
    errors.filter(({ file }) => file.startsWith("docs/")),
    [],
  );
});
```

- [ ] **Step 3: Run and confirm only the three documentation files fail**

Run:

```powershell
node --test scripts/governance/directives.test.mjs
```

Expected: FAIL with `DIR-CLAUSE` diagnostics for `docs/00-index.md`, `docs/23-id-schema.md`, and `docs/07-identity.md`; directive files remain green.

- [ ] **Step 4: Add governance links to the documentation index**

Add these rows to `docs/00-index.md`:

```markdown
| [`../GOVERNANCE.md`](../GOVERNANCE.md) | Verbindliche Prozesskonstitution, Quellenhierarchie und Stop-Regeln |
| [governance/traceability-register.md](governance/traceability-register.md) | REQ, CTRL, PROFILE, ROLE und COMP |
| [governance/risk-register.md](governance/risk-register.md) | Risiken und Behandlungen |
| [governance/data-processing-inventory.md](governance/data-processing-inventory.md) | DATA und FLOW über Vertrauensgrenzen |
| [governance/gate-register.md](governance/gate-register.md) | Gates, Reviews, Evidenzen, Ausnahmen und Transitionen |
| [25-offen.md](25-offen.md) | Noch offene, nicht als Freigabe dargestellte Punkte |
```

- [ ] **Step 5: Replace the ID table in `docs/23-id-schema.md`**

Use this complete table and leave the existing D08–D12 section below it intact:

```markdown
| Präfix | Bedeutung | Bereich/Status |
|---|---|---|
| D, C, U | Produktentscheidungen und gesetzte Kataloge | D01–D24, C01–C12, U01–U12 |
| X | akzeptierter Nicht-Umsetzungs-/Nicht-Relevanz-Katalog | X01–X20; X-Katalog akzeptiert |
| K, L, H, O | Kozyrev, Lovable, Hybrid und offene Produktpunkte | K1–K8, L01–L09, H1–H8, O01–O10 |
| WV | Wiedervorlage mit späterem Trigger | WV01–WV06 |
| REQ, CTRL, RISK | Anforderung, Kontrolle, Risiko | Governance-ID gemäß `GOVERNANCE.md` |
| DATA, FLOW, COMP | Datenobjekt, Datenfluss, Komponente | Governance-ID gemäß `GOVERNANCE.md` |
| GATE, REV, EXC, EVID | Stop-Gate, Review, Ausnahme, Evidenz | Governance-ID gemäß `GOVERNANCE.md` |
| PROFILE, ROLE | Laufzeitprofil und Governance-Rolle | Governance-ID gemäß `GOVERNANCE.md` |
| EVT | append-only Zustandsübergang | EVT-000001 fortlaufend |
| KEY, KEYREV | öffentlicher Verifikationsschlüssel und Widerruf | keine privaten Schlüssel im Repository |
| RECEIPT, POLICYTRANS | externe Annahmequittung und Branch-Policy-Epochwechsel | append-only externe Kontrollfolge |
```

- [ ] **Step 6: Clarify preview and M-G1 identity in `docs/07-identity.md`**

Insert beneath `## Login (Phase 1+)`:

```markdown
### Preview-Identität und WV03

Die aktuelle Preview-Identität ist ausschließlich für synthetische Phase-1-Daten bestimmt und ist keine Produktionsidentität. Passkeys werden erst auf dem M G1 unter WV03 aktiviert, nachdem Debian-Profil, Schlüsselhaltung, Recovery und die zugehörigen Gates geprüft sind. Die Preview darf diese spätere M-G1-Freigabe weder simulieren noch ersetzen.
```

- [ ] **Step 7: Re-run the documentation and canon checks**

Run:

```powershell
node --test scripts/governance/directives.test.mjs
npm run check:canon
```

Expected: both commands exit 0; no product decision text changes.

- [ ] **Step 8: Commit the documentation corrections**

```powershell
git add docs/00-index.md docs/23-id-schema.md docs/07-identity.md scripts/governance/directives.mjs scripts/governance/directives.test.mjs
git commit -m "docs: align identity and ID governance canon"
```

### Task 6: Add the read-only governance CLI and quality script

**Files:**

- Create: `scripts/governance-contract.mjs`
- Create: `scripts/governance-contract.test.mjs`
- Modify: `package.json:9-20`

- [ ] **Step 1: Write failing API and CLI tests**

Create `scripts/governance-contract.test.mjs`:

```js
import assert from "node:assert/strict";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
import { test } from "node:test";
import { governanceErrors, validateGovernance } from "./governance-contract.mjs";

test("the real repository satisfies the Plan-01 governance contract", () => {
  assert.deepEqual(governanceErrors(), []);
  assert.deepEqual(validateGovernance(), { ok: true, errors: [] });
});

test("the CLI is read-only and exits zero on the real repository", () => {
  const scratch = mkdtempSync(join(tmpdir(), "aurelia-governance-cli-"));
  try {
    const result = spawnSync(
      process.execPath,
      ["--experimental-strip-types", "scripts/governance-contract.mjs"],
      { cwd: process.cwd(), encoding: "utf8", shell: false, env: { ...process.env, TMP: scratch, TEMP: scratch } },
    );
    assert.equal(result.status, 0, result.stderr);
    assert.match(result.stdout, /\[governance\] local contract passed/);
  } finally {
    rmSync(scratch, { recursive: true, force: true });
  }
});
```

- [ ] **Step 2: Run and prove the CLI module is absent**

Run:

```powershell
node --experimental-strip-types --test scripts/governance-contract.test.mjs
```

Expected: FAIL with `ERR_MODULE_NOT_FOUND` for `scripts/governance-contract.mjs`.

- [ ] **Step 3: Implement the stable composition API and CLI**

Create `scripts/governance-contract.mjs`:

```js
#!/usr/bin/env node
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { directiveErrors } from "./governance/directives.mjs";
import { formatDiagnostics } from "./governance/diagnostics.mjs";

export function governanceErrors() {
  return [...directiveErrors()];
}

export function validateGovernance() {
  const errors = governanceErrors();
  return { ok: errors.length === 0, errors };
}

if (resolve(process.argv[1] ?? "") === fileURLToPath(import.meta.url)) {
  const result = validateGovernance();
  if (result.ok) {
    console.log("[governance] local contract passed");
  } else {
    console.error(formatDiagnostics(result.errors));
    process.exitCode = 1;
  }
}
```

- [ ] **Step 4: Run the focused contract tests**

Run:

```powershell
node --experimental-strip-types --test scripts/governance-contract.test.mjs
```

Expected: `tests 2`, `pass 2`, `fail 0`.

- [ ] **Step 5: Add the package governance check**

Add this script to `package.json`:

```json-fragment
"check:governance": "node --experimental-strip-types scripts/governance-contract.mjs"
```

- [ ] **Step 6: Exercise the package entry point**

Run:

```powershell
npm run check:governance
```

Expected: exit 0 and exactly one success line: `[governance] local contract passed`.

- [ ] **Step 7: Commit the CLI**

```powershell
git add scripts/governance-contract.mjs scripts/governance-contract.test.mjs package.json
git commit -m "feat: add local governance contract CLI"
```

### Task 7: Run the Plan-01 sequential gates

**Files:** No intended source changes.

- [ ] **Step 1: Run all MJS and TypeScript tests**

Run:

```powershell
npm test
npm run typecheck:governance
```

Expected: both commands exit 0; the MJS phase reports more than zero tests and includes the new governance tests; both explicit TypeScript test files pass; every `scripts/**/*.mjs` contract is checked with `allowJs`, `checkJs`, and `noEmit`.

- [ ] **Step 2: Run canon and governance checks in order**

Run:

```powershell
npm run check:canon
npm run check:governance
```

Expected: both commands exit 0. The governance output makes no claim about live GitHub, external pins, or M-G1.

- [ ] **Step 3: Run compiler and lint gates**

Run:

```powershell
npm run typecheck
npm run typecheck:governance
npm run lint
```

Expected: all three commands exit 0; warnings are inspected and no warning originates from a file introduced in this plan.

- [ ] **Step 4: Prove the lockfile is synchronized**

Run:

```powershell
$lockSnapshot = Join-Path ([System.IO.Path]::GetTempPath()) ("aurelia-package-lock-" + [guid]::NewGuid().ToString("N") + ".json")
Copy-Item -LiteralPath package-lock.json -Destination $lockSnapshot
npm install --package-lock-only --ignore-scripts
git diff --no-index --exit-code -- $lockSnapshot package-lock.json
if ($LASTEXITCODE -ne 0) { throw "package-lock.json changed; snapshot retained at $lockSnapshot" }
Remove-Item -LiteralPath $lockSnapshot -Force
```

Expected: the install exits 0 and the no-index diff exits 0 with exactly no output, proving the reproducibility check did not silently rewrite the already planned lockfile. If the diff is nonzero, preserve both files for diagnosis, return to the dependency task, and do not remove or normalize the change blindly.

- [ ] **Step 5: Check whitespace and the planned file boundary**

Run:

```powershell
git diff --check
$basePath = git rev-parse --git-path aurelia-plan-01-base
$plan01Base = Get-Content -LiteralPath $basePath
if ($plan01Base -notmatch '^[0-9a-f]{40}$') { throw 'invalid Plan-01 base SHA' }
git diff --name-status $plan01Base --
git status --short
```

Expected: `git diff --check` exits 0. The name/status report is calculated from the exact SHA captured before Task 1 and contains only the Plan-01 file map, even when Plan-01 work used several commits. Status contains no `src/`, `server/`, `migrations/`, generated build output, remote artifacts, or server files.

- [ ] **Step 6: Commit any final test-only correction, then stop**

If and only if a gate required a correction within the Plan-01 file map:

```powershell
git add GOVERNANCE.md AGENTS.project.md docs/00-index.md docs/23-id-schema.md docs/07-identity.md scripts/governance scripts/governance-contract.mjs scripts/governance-contract.test.mjs scripts/run-mjs-tests.mjs scripts/run-mjs-tests.test.mjs package.json package-lock.json
git commit -m "test: close G0 foundation quality gates"
```

Do not start Plan 02, push, alter GitHub settings, open Chrome, or access M-G1 in this task.
