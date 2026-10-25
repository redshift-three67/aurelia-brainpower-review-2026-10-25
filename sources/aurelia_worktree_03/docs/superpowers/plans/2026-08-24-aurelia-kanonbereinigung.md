# AURELIA Canon and Status Reconciliation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make AURELIA's active documentation and concept portal agree with the approved product canon, and prevent the same contradictions from returning.

**Architecture:** `src/lib/concept/decisions.ts` remains the canonical D-status source. A small read-only validation script imports that source, checks the derived D08–D12 presentation, and scans explicitly enumerated active documents and UI sources for prohibited stale claims. Documentation and UI wording are corrected without changing authentication, data, compute, hardware, or deployment behavior.

**Tech Stack:** Node.js 22 test runner, TypeScript concept data, React/TanStack Start concept routes, Markdown, Chrome live preview.

---

## Scope and file map

This is the first executable sub-plan of the approved preparation design. It
implements work package A only. Security architecture, Debian deployment,
operations, CI hardening, module intake, and Art.-9 processing receive separate
designs and plans after this gate passes.

**Create:**

- `scripts/canon-contract.mjs` — one read-only validator for decision locks and
  stale active wording.
- `scripts/canon-contract.test.mjs` — regression tests for the validator and the
  repository's real canon.

**Modify:**

- `package.json` — expose `check:canon`; do not change dependency versions.
- `docs/superpowers/specs/2026-08-24-aurelia-vorbereitungsphase-design.md` —
  record operator approval.
- `src/lib/concept/decisions.ts` — remove the stale WebRTC recommendation in
  D05; D10 remains the canonical prohibition.
- `src/lib/concept/id-legend.ts` — represent D08–D12 as mixed statuses rather
  than a uniformly recommended block.
- `src/lib/concept/nav.ts` — show accepted X catalogue and remove WebRTC from
  the security blurb.
- `src/lib/concept/standalone.ts` — remove already-resolved X/Phase-1 wording.
- `docs/02-architecture.md`, `docs/03-security-dsgvo.md`, `docs/15-live.md`,
  `docs/23-id-schema.md` — reconcile active architecture and status wording.
- `src/routes/index.tsx`, `src/routes/leitplanken.tsx`,
  `src/routes/roadmap.tsx`, `src/routes/entscheidungen.tsx`,
  `src/routes/sicherheit.tsx` — reconcile the rendered concept portal.

**Do not modify:** migrations, authentication implementation, runtime data,
CUDA/USB behavior, server configuration, `src/routeTree.gen.ts`, or any remote.

### Task 1: Record the approved preparation design

**Files:**

- Modify: `docs/superpowers/specs/2026-08-24-aurelia-vorbereitungsphase-design.md`

- [ ] **Step 1: Change the review status to the exact approved state**

The metadata must read:

```markdown
Status: vom Betreiber freigegeben

Freigabe: 2026-08-24 im Codex-Chat (Wortlaut: „freigeben“)
```

- [ ] **Step 2: Verify the approval metadata**

Run:

```powershell
rg -n "Status: vom Betreiber freigegeben|Freigabe: 2026-08-24" docs/superpowers/specs/2026-08-24-aurelia-vorbereitungsphase-design.md
```

Expected: exactly two matching lines and no file changes outside the spec and
this plan at this point.

- [ ] **Step 3: Commit the approval record and plan**

```powershell
git add docs/superpowers/specs/2026-08-24-aurelia-vorbereitungsphase-design.md docs/superpowers/plans/2026-08-24-aurelia-kanonbereinigung.md
git commit -m "Plan Aurelia canon reconciliation"
```

### Task 2: Add a failing executable canon contract

**Files:**

- Create: `scripts/canon-contract.mjs`
- Create: `scripts/canon-contract.test.mjs`
- Modify: `package.json`

- [ ] **Step 1: Write the validator**

Create `scripts/canon-contract.mjs` with this complete implementation:

```js
#!/usr/bin/env node
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { DECISIONS } from "../src/lib/concept/decisions.ts";
import { D08_D12_STATUS } from "../src/lib/concept/id-legend.ts";

const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));
export const PROJECT_ROOT = resolve(SCRIPT_DIR, "..");

export const EXPECTED_D_LOCKS = Object.freeze({
  D01: "gesetzt",
  D02: "gesetzt",
  D03: "gesetzt",
  D04: "gesetzt",
  D05: "gesetzt",
  D06: "gesetzt",
  D07: "gesetzt",
  D08: "gesetzt",
  D09: "empfohlen",
  D10: "gesetzt",
  D11: "empfohlen",
  D12: "gesetzt",
  D13: "gesetzt",
  D14: "gesetzt",
  D15: "gesetzt",
  D16: "gesetzt",
  D17: "gesetzt",
  D18: "gesetzt",
  D19: "gesetzt",
  D20: "gesetzt",
  D21: "gesetzt",
  D22: "gesetzt",
  D23: "gesetzt",
  D24: "gesetzt",
});

export const ACTIVE_TEXT_RULES = Object.freeze([
  {
    file: "src/lib/concept/decisions.ts",
    prohibited: [/WebRTC bleibt nachrangig/i],
    required: [/Kein Video zwischen Therapeut und Klient\. Kein WebRTC/i],
  },
  {
    file: "docs/02-architecture.md",
    prohibited: [/später optional WebRTC/i],
    required: [/WebSocket-Fachkanal.*kein WebRTC/i],
  },
  {
    file: "docs/03-security-dsgvo.md",
    prohibited: [/Video \(Phase 9\): WebRTC/i],
    required: [/D10.*kein Video.*kein WebRTC/i],
  },
  {
    file: "docs/15-live.md",
    prohibited: [/WebRTC nachrangig/i],
    required: [/D10.*kein Video.*kein WebRTC/i],
  },
  {
    file: "docs/23-id-schema.md",
    prohibited: [
      /D08–D12 \(empfohlen/i,
      /Auth ist aus/i,
      /WebRTC optional/i,
    ],
    required: [/D08, D10 und D12.*gesetzt/i, /D09 und D11.*Wiedervorlage/i],
  },
  {
    file: "src/lib/concept/nav.ts",
    prohibited: [/X zur Prüfung/i, /DSGVO, E2E, WebRTC/i],
    required: [/X akzeptiert/i, /DSGVO, E2E, kein Video/i],
  },
  {
    file: "src/lib/concept/standalone.ts",
    prohibited: [/Ihr Wort zu X und Phase 1/i],
    required: [/Offen bleiben die Backup-SKU und das optionale H4/i],
  },
  {
    file: "src/routes/index.tsx",
    prohibited: [/Phase 1 startet erst, wenn Sie es sagen/i],
    required: [/Phase 1 läuft ausschließlich synthetisch/i],
  },
  {
    file: "src/routes/leitplanken.tsx",
    prohibited: [/Keine Speicherung von Videogesprächen im Standard/i],
    required: [/Keine Videogespräche in AURELIA/i],
  },
  {
    file: "src/routes/roadmap.tsx",
    prohibited: [/Budget 3\/3\/12\/2/i, /Empfohlene Karten \(D08–D12\)/i],
    required: [/Budget 2\/16\/2/i, /D08, D10 und D12 sind gesetzt/i],
  },
  {
    file: "src/routes/entscheidungen.tsx",
    prohibited: [
      /D08–D12 empfohlen/i,
      /Warum noch empfohlen/i,
      /weil Auth noch aus ist/i,
    ],
    required: [/Status D08–D12/i, /Statusgrund/i],
  },
]);

function textAt(root, relativePath) {
  return readFileSync(resolve(root, relativePath), "utf8");
}

export function decisionLockErrors(
  decisions = DECISIONS,
  summaries = D08_D12_STATUS,
) {
  const errors = [];
  const actual = Object.fromEntries(decisions.map((decision) => [decision.id, decision.lock]));
  const expectedIds = Object.keys(EXPECTED_D_LOCKS);
  const actualIds = Object.keys(actual).sort();
  if (JSON.stringify(actualIds) !== JSON.stringify(expectedIds)) {
    errors.push(`D-ID set differs: expected ${expectedIds.join(", ")}; got ${actualIds.join(", ")}`);
  }
  for (const [id, expectedLock] of Object.entries(EXPECTED_D_LOCKS)) {
    if (actual[id] !== expectedLock) {
      errors.push(`${id}: expected ${expectedLock}; got ${String(actual[id])}`);
    }
  }
  for (const summary of summaries) {
    const expectedLock = EXPECTED_D_LOCKS[summary.id];
    if (summary.lock !== expectedLock) {
      errors.push(`${summary.id} summary: expected ${expectedLock}; got ${summary.lock}`);
    }
  }
  return errors;
}

export function activeTextErrors(root = PROJECT_ROOT) {
  const errors = [];
  for (const rule of ACTIVE_TEXT_RULES) {
    const text = textAt(root, rule.file);
    for (const pattern of rule.prohibited) {
      if (pattern.test(text)) errors.push(`${rule.file}: prohibited ${pattern}`);
    }
    for (const pattern of rule.required) {
      if (!pattern.test(text)) errors.push(`${rule.file}: missing ${pattern}`);
    }
  }
  return errors;
}

export function canonErrors(root = PROJECT_ROOT) {
  return [...decisionLockErrors(), ...activeTextErrors(root)];
}

const invokedPath = process.argv[1] ? resolve(process.argv[1]) : "";
if (invokedPath === fileURLToPath(import.meta.url)) {
  const errors = canonErrors();
  if (errors.length > 0) {
    console.error(`[canon] ${errors.length} contradiction(s)`);
    for (const error of errors) console.error(`- ${error}`);
    process.exit(1);
  }
  console.log("[canon] decision locks and active wording agree");
}
```

- [ ] **Step 2: Write the regression tests**

Create `scripts/canon-contract.test.mjs`:

```js
import assert from "node:assert/strict";
import { mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { test } from "node:test";
import {
  ACTIVE_TEXT_RULES,
  activeTextErrors,
  canonErrors,
  decisionLockErrors,
} from "./canon-contract.mjs";

test("the real repository has one consistent active canon", () => {
  assert.deepEqual(canonErrors(), []);
});

test("decision status mismatches fail closed", () => {
  const decisions = [{ id: "D01", lock: "empfohlen" }];
  const errors = decisionLockErrors(decisions, []);
  assert.ok(errors.some((error) => error.includes("D01: expected gesetzt")));
  assert.ok(errors.some((error) => error.includes("D-ID set differs")));
});

test("stale active wording is reported with its file", () => {
  const root = mkdtempSync(join(tmpdir(), "aurelia-canon-"));
  for (const rule of ACTIVE_TEXT_RULES) {
    const target = join(root, rule.file);
    mkdirSync(dirname(target), { recursive: true });
    writeFileSync(target, rule.required.map((pattern) => pattern.source).join("\n"));
  }
  const architecture = join(root, "docs/02-architecture.md");
  writeFileSync(architecture, "Realtime: später optional WebRTC");
  const errors = activeTextErrors(root);
  assert.ok(errors.some((error) => error.includes("docs/02-architecture.md")));
  assert.ok(errors.some((error) => error.includes("prohibited")));
});
```

- [ ] **Step 3: Add the package command**

Add this entry after `check:auth` in `package.json`:

```json
"check:canon": "node --experimental-strip-types scripts/canon-contract.mjs",
```

- [ ] **Step 4: Run the targeted test and prove it fails before corrections**

Run:

```powershell
node --experimental-strip-types --test scripts/canon-contract.test.mjs
```

Expected: FAIL in `the real repository has one consistent active canon`, with
the currently stale WebRTC, D08–D12, VRAM, X, or Phase-1 wording listed. The two
validator-behavior tests must pass.

- [ ] **Step 5: Commit the failing contract**

```powershell
git add package.json scripts/canon-contract.mjs scripts/canon-contract.test.mjs
git commit -m "test: define Aurelia canon contract"
```

### Task 3: Correct the canonical concept sources

**Files:**

- Modify: `src/lib/concept/decisions.ts`
- Modify: `src/lib/concept/id-legend.ts`
- Modify: `src/lib/concept/nav.ts`
- Modify: `src/lib/concept/standalone.ts`

- [ ] **Step 1: Remove the stale D05 WebRTC recommendation**

In D05, replace the recommendation with:

```ts
recommendation:
  "aurelia-timerd (CPU, RAM-Arbeitsspeicher) + Postgres als dauerhafte Uhr + aurelia-gpud + aurelia-emitterd. UI nur aus RunEvents. Commands (start/pause/stop) client→server, ACK zurück. Kein WebRTC und kein WebUSB. HRV-Ohrclip: eigener Sensorpfad (D21).",
```

- [ ] **Step 2: Make the D08–D12 derived table status-explicit**

In `src/lib/concept/id-legend.ts`, replace `D08_D12` with this complete export:

```ts
export type DecisionStatusSummary = {
  id: "D08" | "D09" | "D10" | "D11" | "D12";
  titel: string;
  lock: "gesetzt" | "empfohlen";
  kern: string;
  statusGrund: string;
};

export const D08_D12_STATUS: DecisionStatusSummary[] = [
  {
    id: "D08",
    titel: "Identität: Passkeys auf Debian, E-Mail/Passwort in der Vorschau",
    lock: "gesetzt",
    kern: "Gesetzt. Kein Social-Login als Produktpfad.",
    statusGrund: "WV03 terminiert die Aktivierung der Passkeys auf M G1.",
  },
  {
    id: "D09",
    titel: "Abos: Quotas an VRAM, Timer-Kanälen, Emittern",
    lock: "empfohlen",
    kern: "Technische Quotas gesetzt. Euro-Beträge offen.",
    statusGrund: "Wiedervorlage WV02 in Phase 10.",
  },
  {
    id: "D10",
    titel: "Kein Video",
    lock: "gesetzt",
    kern: "Gesetzt. Kein WebRTC, keine Aufnahme.",
    statusGrund: "O08 ist entschieden; Phase 9 ist gestrichen.",
  },
  {
    id: "D11",
    titel: "Medien: AVIF/Opus/zstd — Zeugen nie ins CDN",
    lock: "empfohlen",
    kern: "CDN-Verbot gesetzt. Codec-Familie später.",
    statusGrund: "Wiedervorlage WV06 in Phase 6.",
  },
  {
    id: "D12",
    titel: "Barrierefreiheit und EEAT sind Muss",
    lock: "gesetzt",
    kern: "Gesetzt. WCAG 2.2 AA / BFSG / CopyGuard.",
    statusGrund: "O10 ist entschieden und bindet alle Produktoberflächen.",
  },
];
```

- [ ] **Step 3: Correct navigation summaries**

Use these exact blurbs in `src/lib/concept/nav.ts`:

```ts
blurb: "C gesetzt, X akzeptiert, U übernommen",
```

and:

```ts
blurb: "DSGVO, E2E, kein Video",
```

- [ ] **Step 4: Remove resolved decisions from the standalone verdict**

Replace `STANDALONE_URTEIL.lang` with:

```ts
lang: "H1–H3 sind gesetzt. Die Ada ist der Origin. Backup ist Pflicht, nicht Kür. Pflichtseiten kommen aus diesem Baum. Lovable, Cloud-Auth, Cloud-GPU und Cloud-LLM sind gesperrt. Offen bleiben die Backup-SKU und das optionale H4.",
```

- [ ] **Step 5: Run the decision-lock portion of the test**

```powershell
node --experimental-strip-types --test --test-name-pattern="decision status" scripts/canon-contract.test.mjs
```

Expected: PASS.

- [ ] **Step 6: Commit the canonical source corrections**

```powershell
git add src/lib/concept/decisions.ts src/lib/concept/id-legend.ts src/lib/concept/nav.ts src/lib/concept/standalone.ts
git commit -m "fix: reconcile Aurelia decision sources"
```

### Task 4: Correct active Markdown documentation

**Files:**

- Modify: `docs/02-architecture.md`
- Modify: `docs/03-security-dsgvo.md`
- Modify: `docs/15-live.md`
- Modify: `docs/23-id-schema.md`

- [ ] **Step 1: Make the realtime architecture explicitly WebSocket-only**

In `docs/02-architecture.md`, replace the realtime row with:

```markdown
| Realtime | WebSocket-Fachkanal; kein WebRTC | Analyse + Harmonisierung, Server ist Uhr |
```

- [ ] **Step 2: Replace the obsolete video encryption layer**

In `docs/03-security-dsgvo.md`, replace item 5 of the staged protection list:

```markdown
5. Live: WebSocket-Fachkanal ohne Zeugenklartext. D10: kein Video, kein WebRTC.
```

- [ ] **Step 3: Close the live document with the settled D10 rule**

In `docs/15-live.md`, replace the obsolete WebRTC paragraph with:

```markdown
D10 / O08: kein Video und kein WebRTC. Externe Videokonferenzen sind kein Teil
von AURELIA. Der produktinterne Live-Kanal bleibt WebSocket.
```

- [ ] **Step 4: Rewrite the D08–D12 status section**

Replace the D08–D12 section of `docs/23-id-schema.md` with:

```markdown
## Status D08–D12

D08, D10 und D12 sind gesetzt. D09 und D11 bleiben Wiedervorlage; ihre bereits
gesetzten technischen Grenzen gelten weiter.

| ID | Status | Inhalt | Statusgrund |
|---|---|---|---|
| D08 | gesetzt | Passkeys + TOTP, kein Social-Login | Produktregel gesetzt; Aktivierung auf M G1 unter WV03. |
| D09 | empfohlen | Abos an VRAM/Kanäle/Emitter | Technische Quotas gesetzt; Preise unter WV02. |
| D10 | gesetzt | Kein Video, kein WebRTC, keine Aufnahme | O08 entschieden; Phase 9 gestrichen. |
| D11 | empfohlen | AVIF/Opus/zstd, Zeugen nie im CDN | CDN-Verbot gesetzt; Codecwahl unter WV06. |
| D12 | gesetzt | WCAG 2.2 AA / BFSG / EEAT | O10 entschieden; bindet alle Oberflächen. |

Gesetzt bindet den nächsten Slice. Empfohlen bezeichnet eine Wiedervorlage mit
gesetzten technischen Grenzen, nicht eine unklare Produktentscheidung.
```

- [ ] **Step 5: Run Markdown-oriented canon validation**

```powershell
npm run check:canon
```

Expected: it may still FAIL only on remaining UI source rules. None of the four
Markdown files may appear in the error list.

- [ ] **Step 6: Commit the documentation corrections**

```powershell
git add docs/02-architecture.md docs/03-security-dsgvo.md docs/15-live.md docs/23-id-schema.md
git commit -m "docs: remove obsolete Aurelia status claims"
```

### Task 5: Correct the rendered concept portal

**Files:**

- Modify: `src/routes/index.tsx`
- Modify: `src/routes/leitplanken.tsx`
- Modify: `src/routes/roadmap.tsx`
- Modify: `src/routes/entscheidungen.tsx`
- Modify: `src/routes/sicherheit.tsx`

- [ ] **Step 1: Make the home-page Phase-1 statement current**

In `src/routes/index.tsx`, replace the stale end of the lead so the complete
lead reads:

```tsx
lead="AURELIA bleibt Wellbeing-Software auf dem GPU Server M G1. Virtuelle Harmonisierungstimer sind viele und klein. Nach einem Reset zählt Postgres, nicht VRAM. CopyGuard sitzt im RAM. Phase 1 läuft ausschließlich synthetisch."
```

- [ ] **Step 2: Make the video exclusion absolute**

In `src/routes/leitplanken.tsx`, use:

```tsx
"Keine Videogespräche in AURELIA; D10 schließt Video und WebRTC aus.",
```

- [ ] **Step 3: Correct the roadmap VRAM budget and decision callout**

Use this Phase-7 item:

```tsx
items: ["Budget 2/16/2, Attestation, Queue-Policy zwischen Abo-Stufen."],
```

Replace the final decision callout body with:

```tsx
D08, D10 und D12 sind gesetzt. D09 und D11 bleiben Wiedervorlage.
Gesetzte Karten ändern wir nur durch eine neue dokumentierte Betreiberentscheidung.
Wo später noch Entscheidungen anstehen: {" "}
<Link to="/offen" className="underline decoration-from-font">
  Offen
</Link>
.
```

- [ ] **Step 4: Render the D08–D12 mixed status accurately**

In `src/routes/entscheidungen.tsx`:

1. Import `D08_D12_STATUS` instead of `D08_D12`.
2. Replace the explanatory paragraph with:

```tsx
D08, D10 und D12 sind gesetzt. D09 und D11 sind terminierte
Wiedervorlagen; ihre technischen Grenzen gelten bereits.
```

3. Configure the table exactly as follows:

```tsx
<DataTable
  caption="Status D08–D12"
  headers={["ID", "Titel", "Status", "Kern", "Statusgrund"]}
  rows={D08_D12_STATUS.map((d) => ({
    key: d.id,
    cells: [d.id, d.titel, d.lock, d.kern, d.statusGrund],
  }))}
/>
```

4. Replace the `Gesetzt vs. empfohlen` callout text with:

```tsx
Gesetzt bindet den nächsten Slice. Empfohlen markiert hier eine terminierte
Wiedervorlage, nicht eine offene Grundsatzentscheidung. H1–H3 und D24 sind gesetzt.
Wo später noch Entscheidungen anstehen: {" "}
```

- [ ] **Step 5: Remove the duplicated MLS bullet**

In `src/routes/sicherheit.tsx`, keep exactly one MLS entry and one separate
video exclusion:

```tsx
"Nachrichten Therapeut–Klient: MLS (RFC 9420) — der Server reicht Ciphertexte.",
"D10: kein Video, kein WebRTC und keine Aufnahme in AURELIA.",
```

- [ ] **Step 6: Run the full canon contract**

```powershell
npm run check:canon
node --experimental-strip-types --test scripts/canon-contract.test.mjs
```

Expected:

```text
[canon] decision locks and active wording agree
# pass 3
# fail 0
```

- [ ] **Step 7: Commit the portal corrections**

```powershell
git add src/routes/index.tsx src/routes/leitplanken.tsx src/routes/roadmap.tsx src/routes/entscheidungen.tsx src/routes/sicherheit.tsx
git commit -m "fix: align Aurelia concept portal with canon"
```

### Task 6: Run repository quality gates

**Files:** No intended source changes. `node_modules` and generated build output
remain untracked.

- [ ] **Step 1: Install the locked dependency graph if absent**

Run only after normal tool approval for the networked installation:

```powershell
npm ci
```

Expected: exit code 0 and `package-lock.json` unchanged.

- [ ] **Step 2: Run the targeted canon gates again**

```powershell
npm run check:canon
node --experimental-strip-types --test scripts/canon-contract.test.mjs
```

Expected: both commands exit 0.

- [ ] **Step 3: Run existing static and test gates**

```powershell
npm run typecheck
npm run lint
npm test
```

Expected: each command exits 0. If `npm test` again discovers zero
`scripts/**/*.test.mjs` tests on Windows, record that as a separate quality-
infrastructure defect; do not claim the full test suite passed and do not widen
this canon-fix commit to repair the runner.

- [ ] **Step 4: Build without applying production migrations**

```powershell
npm run build:dev
```

Expected: exit 0. Do not use `npm run build`, because that command invokes
`db:migrate` and this work does not authorize a database mutation.

### Task 7: Perform Chrome live-preview acceptance

**Files:** No intended source changes.

- [ ] **Step 1: Start the existing development entrypoint**

Run:

```powershell
npm run dev
```

Expected: the app listens on `http://127.0.0.1:8080` with authentication and
synthetic data only. Leave the process running for the browser checks.

- [ ] **Step 2: Open a dedicated Chrome preview tab**

Use the already connected Chrome extension and navigate an agent-created tab
to:

```text
http://127.0.0.1:8080/
```

Do not claim or reuse an unrelated personal tab. Mark the final preview tab as
deliverable so it remains open for the operator.

- [ ] **Step 3: Check the affected routes at desktop width**

Inspect these routes in order:

```text
/
/architektur
/sicherheit
/live
/roadmap
/entscheidungen
```

For every route verify visible content, no horizontal overflow, no contradictory
WebRTC/decision text, a working chapter navigation, and no uncaught console
errors.

- [ ] **Step 4: Check responsive presentation**

Set the temporary viewport to `390 × 844` and repeat `/roadmap` and
`/entscheidungen`. Verify the five-column status table remains usable through
the application's intended responsive behavior, tap targets remain at least
44 px, and the menu can be opened and closed. Reset the viewport override after
the check.

- [ ] **Step 5: Check keyboard and reduced-motion essentials**

Use keyboard navigation on `/entscheidungen` to confirm the skip link, menu,
links, and decision buttons receive a visible focus indicator. Emulate or use
the browser's reduced-motion preference only if the connected Chrome capability
supports it; otherwise record that automated reduced-motion verification is
deferred to the later accessibility plan.

- [ ] **Step 6: Keep the approved preview visible**

Return the deliverable Chrome tab to `/entscheidungen`, where the mixed status
of D08–D12 is visible. Do not submit votes or write browser local state during
this acceptance pass.

### Task 8: Final verification and handoff

**Files:** No further changes unless a preceding gate found a defect.

- [ ] **Step 1: Verify repository scope and whitespace**

```powershell
git diff --check origin/main...HEAD
git diff --name-status origin/main...HEAD
git status --short --branch
```

Expected: only the spec approval, this plan, validator/test, package command,
and listed canon/UI files differ. No migration, auth, runtime-data, server, or
generated-route changes are present. The working tree is clean.

- [ ] **Step 2: Re-run the final non-mutating gates**

```powershell
npm run check:canon
node --experimental-strip-types --test scripts/canon-contract.test.mjs
npm run typecheck
npm run lint
```

Expected: all exit 0. Report `npm test` and `build:dev` separately using their
actual verified results from Task 6.

- [ ] **Step 3: Commit any verification-only correction, if required**

If and only if Task 8 required a source correction:

```powershell
git add package.json scripts/canon-contract.mjs scripts/canon-contract.test.mjs src/lib/concept/decisions.ts src/lib/concept/id-legend.ts src/lib/concept/nav.ts src/lib/concept/standalone.ts docs/02-architecture.md docs/03-security-dsgvo.md docs/15-live.md docs/23-id-schema.md src/routes/index.tsx src/routes/leitplanken.tsx src/routes/roadmap.tsx src/routes/entscheidungen.tsx src/routes/sicherheit.tsx
git commit -m "fix: complete Aurelia canon verification"
```

- [ ] **Step 4: Hand off without remote mutation**

Report the branch, commit list, exact gate results, any remaining defect, and
the open Chrome preview. Do not push, merge, open a pull request, or access M G1
without a new explicit instruction.
