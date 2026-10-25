# AURELIA K1 Canon Consolidation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Den lokalen Branch `codex/aurelia-konsolidierung` ab `8706186` in einen widerspruchsfreien, fail-closed geprüften K1-Kanon überführen, ohne Push, Serverzugriff, Git-History-Änderung oder produktive Datenmutation.

**Architecture:** Eine einzige maschinenlesbare K1-Kanonmatrix wird von einem explizit auf aktive Quellen begrenzten Validator geprüft; historische Analysen, Specs und Governance-Artefakte bleiben unverändert und außerhalb des aktiven Scopes. Toolchain-, Publikations- und Plattformabhängigkeiten erhalten getrennte fail-closed Gates, damit ein externer Blocker niemals als grüner Produkttest maskiert wird.

**Tech Stack:** Node.js 22 ESM, TypeScript 5.7, React 19, TanStack Start, Node Test Runner, ESLint, Vite 8, Playwright, Git.

---

## 0. Verbindlicher Ausführungsrahmen

- Arbeitsverzeichnis: `.worktrees/aurelia-konsolidierung`
- Branch: `codex/aurelia-konsolidierung`
- zwingender Vorfahr: `8706186af01e10e4253e25abb31bf3577110dae4`
- freigegebenes Design: `7de43db7bdaf87132de6893daf6acdad46d9c9ba`
- historische Kanonreferenz: `b20ee873347c5fd767e2089c993f1cf93a625def`
- historisches Governance-Design: `a6a8e7dca456d14a6748b204b787b235fdedf9be`
- erlaubte Datenklasse: ausschließlich `synthetic`
- verboten: Push, Pull Request, Merge, Rebase, Reset, History-Rewrite, Serverzugriff, Datenbankmigration, `npm run build`, CUDA, USB, Art.-9-Klartext, `git add -f`.

Vor jeder Aufgabe prüft der Orchestrator Branch, Worktree und sauberen Ausgangsdiff. Für alle am 26. August 2026 noch nicht abgeschlossenen Arbeiten gilt die risikobasierte Direktive `docs/project-control/QUALITY-ROUTING.md`: Spur A wird primär und deterministisch verifiziert; Spur B erhält Vertrag, RED/GREEN, fokussiertes Spezifikationsreview und erst nach Spec-PASS ein separates Qualitäts-/Securityreview. Offene P0–P2-Befunde werden vor der nächsten Aufgabe geschlossen und gezielt erneut geprüft. Die historischen Reviews abgeschlossener Tasks bleiben unverändert.

## 1. Kanonmatrix

| Feld | Exakter K1-Wert |
|---|---|
| Phase 0 | `abgenommen` |
| Phase 1 | `Schale/Auth/Mandant technisch vorhanden; Produktarbeit pausiert` |
| Pause | bis dokumentiert bestandenem `G0-SRV-12` |
| aktuelles Servergate | `G0-SRV-0` |
| Destruktionsfreigabe | `false` |
| Auth | `on` |
| Datenbank | `on` |
| Datenklasse | `synthetic` |
| Betriebssystem | `Ubuntu Server 24.04.4 LTS amd64` plus minimales GNOME |
| Storage | `2×2 TB WD_BLACK SN850X`, geplant RAID1/LUKS2/LVM |
| Video/WebRTC | vollständig ausgeschlossen; Phase 9 gestrichen |
| CUDA/USB/Art. 9 | gesperrt |
| Governance | `GATE-GOV-0` als aktuelle Referenz auf historisches `GATE-G0` |
| Serverprogramm | eigenständig und vorgeschaltet: `G0-SRV-0…12` |

## 2. Dateiverantwortung

| Einheit | Verantwortliche Dateien |
|---|---|
| K1-Projektsteuerung | `docs/project-control/K1-STATUS.md`, `docs/project-control/README.md`, `scripts/check-project-control-k1.mjs` |
| Governance-Grenze | `docs/project-control/GATE-GOV-0-SUPPLEMENT.md` |
| Publikationsgrenze | `scripts/check-push-graph.mjs` |
| Produktkanon | `src/lib/concept/canon.ts`, aktive `docs/*.md`, `src/lib/concept/*.ts` |
| Kanonvertrag | `scripts/canon-contract.mjs`, `scripts/canon-contract.test.mjs` |
| Portalableitung | `src/components/concept/shell.tsx`, präsentierende `src/routes/*.tsx` |
| Testdiscovery | `scripts/test-runner.mjs`, `scripts/test-runner.test.mjs` |
| Vite-Portabilität | `scripts/with-app-env.mjs`, `scripts/with-app-env.test.mjs` |
| Auth-Abnahme | `scripts/check-auth-with-dev-server.mjs`, zugehöriger Test |
| Plattformassets | `scripts/platform-assets.mjs`, zugehöriger Test |
| Abschlussnachweis | `docs/project-control/K1-VERIFICATION.md` |

## 3. Modell- und Reviewzuordnung

| Aufgabentyp | Implementierung | Spezifikationsreview | Qualitätsreview |
|---|---|---|---|
| K1-Steuerung, Kanon, Governance ohne kritische Vertragsänderung | Sol 5.6 / medium oder Terra 5.6 / high | nur bei Spur-B-Eskalation | nur bei Spur-B-Eskalation |
| Security, Datenschutz, Migration, Publikations- oder Gatevertrag | Sol 5.6 / high | Sol 5.6 / high oder geeignetes externes Modell | Sol 5.6 / xHigh |
| isolierter Runner, Vite, Testfixtures, Lint | Terra 5.6 / high oder Sol 5.6 / medium | nur bei Spur-B-Eskalation | nur bei Spur-B-Eskalation |
| Browser-/Integrationsabnahme | Terra 5.6 / high | fokussiert bei Vertragsrisiko | Sol 5.6 / high bei Spur B |

Kein externer LLM-Output gilt als Abnahme. Ein externer Reviewer erhält später nur einen sanitisierten, eng begrenzten Diff und einen exakten Prüfauftrag; der Orchestrator verifiziert jeden Befund lokal.

Für die offene Task-3-Korrektur ist zusätzlich das Design `docs/superpowers/specs/2026-08-26-aurelia-k1-task3-correction-design.md` verbindlich. Es ändert weder Task 4 noch die Publikationsgrenzen dieses Plans.

### Task 1: K1-Projektsteuerung und V1/V2-Tip-Sanitisierung

**Historische Quelle:** K1-Design `7de43db`, V1/V2-Manifeste aus `8706186`.

**Files:**
- Create: `docs/project-control/K1-STATUS.md`
- Create: `scripts/check-project-control-k1.mjs`
- Create: `scripts/check-project-control-k1.test.mjs`
- Modify: `docs/project-control/README.md`
- Modify: `docs/project-control/external-analyses/2026-08-25_16-40-00_CEST_developer-analysis-01/MANIFEST.md:10`
- Modify: `docs/project-control/external-analyses/2026-08-25_17-22-13_CEST_developer-analysis-02/MANIFEST.md:10`
- Modify: `package.json`

- [ ] **Step 1: Branch- und Scope-Preflight ausführen**

```powershell
git status --short --branch
git merge-base --is-ancestor 8706186af01e10e4253e25abb31bf3577110dae4 HEAD
git diff --check 8706186af01e10e4253e25abb31bf3577110dae4...HEAD
```

Expected: Branch `codex/aurelia-konsolidierung`; Ancestor-Check Exit 0; kein unerwarteter Diff außer freigegebenem Design/Plan.

- [ ] **Step 2: Failing contract test schreiben**

Der Test importiert `k1ControlErrors(root, options)` und prüft mindestens:

```javascript
test("rejects local paths in V1 and V2 provenance", () => {
  const localPath = ["C:", "Users", "Operator", "Desktop", "analysis.txt"].join("\\");
  const root = makeFixture({ provenance: localPath });
  assert.match(k1ControlErrors(root).join("\n"), /local_path_in_manifest/);
});

test("requires the exact neutral provenance phrase", () => {
  const root = makeFixture({ provenance: "Lokaler Operator-Arbeitsbereich (Pfad nicht veröffentlicht)" });
  assert.deepEqual(k1ControlErrors(root), []);
});

test("requires K1 branch, base and mutation boundaries", () => {
  const root = makeFixture({ status: validStatus.replace("no_push: true", "no_push: false") });
  assert.match(k1ControlErrors(root).join("\n"), /no_push/);
});
```

- [ ] **Step 3: RED nachweisen**

Run: `node --test scripts/check-project-control-k1.test.mjs`

Expected: FAIL wegen fehlendem Modul oder fehlender exportierter `k1ControlErrors`-Funktion.

- [ ] **Step 4: Minimalen K1-Control-Validator implementieren**

Die öffentliche API lautet:

```javascript
export const K1_BASE = "8706186af01e10e4253e25abb31bf3577110dae4";
export const GOVERNANCE_BASE = "a6a8e7dca456d14a6748b204b787b235fdedf9be";
export const NEUTRAL_PROVENANCE = "Lokaler Operator-Arbeitsbereich (Pfad nicht veröffentlicht)";
```

Die vollständige öffentliche Schnittstelle ist:

```typescript
export declare function k1ControlErrors(
  root: string,
  options?: { branch?: string; head?: string; git?: typeof import("node:child_process").spawnSync },
): string[];
export declare function isMainModule(moduleUrl: string): boolean;
```

Der CLI-Modus gibt nur Regelname und Repositorypfad aus, niemals einen gefundenen sensitiven Wert. Exit 0 bedeutet keine Fehler; Exit 1 bedeutet Vertragsverletzung; Exit 2 bedeutet unentscheidbaren Git-/I/O-Zustand.

- [ ] **Step 5: V1/V2 exakt und minimal sanitisieren**

Nur das Herkunftsfeld in beiden Manifesten erhält:

```text
Lokaler Operator-Arbeitsbereich (Pfad nicht veröffentlicht)
```

Archive-ID, Zeitstempel, Dateiname, Bytes, Zeilen, Hashes, Reporttext und Remote-Feld bleiben unverändert.

- [ ] **Step 6: K1-Status mit exakten Grenzen anlegen**

`K1-STATUS.md` enthält maschinenlesbar:

```yaml
branch: codex/aurelia-konsolidierung
base: 8706186af01e10e4253e25abb31bf3577110dae4
design: 7de43db7bdaf87132de6893daf6acdad46d9c9ba
historical_governance: a6a8e7dca456d14a6748b204b787b235fdedf9be
remote_mutation: false
server_mutation: false
history_rewrite: false
push_authorized: false
sanitization_scope: V1/V2 branch-tip manifests only
server_gate_authority: docs/project-control/ground-zero/GATE-STATUS.md
```

Darunter wird ausdrücklich erklärt, dass alte Git-Objekte nicht gelöscht wurden und lokale Commits keine Publikationsfreigabe darstellen.

- [ ] **Step 7: Script und Package-Gate verdrahten**

```json
"check:k1-control": "node scripts/check-project-control-k1.mjs"
```

- [ ] **Step 8: GREEN und reale Kontrolle nachweisen**

```powershell
node --test scripts/check-project-control-k1.test.mjs
npm run check:k1-control
git diff --check
```

Expected: Tests und K1-Control grün; Diff-Check ohne Ausgabe.

- [ ] **Step 9: Commit erstellen**

```powershell
git add docs/project-control/K1-STATUS.md docs/project-control/README.md docs/project-control/external-analyses/2026-08-25_16-40-00_CEST_developer-analysis-01/MANIFEST.md docs/project-control/external-analyses/2026-08-25_17-22-13_CEST_developer-analysis-02/MANIFEST.md scripts/check-project-control-k1.mjs scripts/check-project-control-k1.test.mjs package.json
git commit -m "docs: sanitize V1/V2 provenance and record K1 status"
```

### Task 2: Nichtnormative Governance-Ergänzung

**Historische Quelle:** `a6a8e7d:docs/superpowers/specs/2026-08-24-aurelia-g0-governance-design.md`; erwarteter historischer Blob `0aad1cd64a8896a52df84e6c7918c8df3968ae83`.

**Files:**
- Create: `docs/project-control/GATE-GOV-0-SUPPLEMENT.md`
- Modify: `scripts/check-project-control-k1.test.mjs`
- Modify: `scripts/check-project-control-k1.mjs`

- [ ] **Step 1: Governance-Negativtests zuerst ergänzen**

```javascript
test("keeps governance and server gate namespaces distinct", () => {
  const root = makeFixture({ supplement: validSupplement.replace("GATE-GOV-0", "G0-SRV-0") });
  assert.match(k1ControlErrors(root).join("\n"), /governance_namespace/);
});

test("requires the supplement to remain non-normative", () => {
  const root = makeFixture({ supplement: validSupplement.replace("no_normative_effect: true", "no_normative_effect: false") });
  assert.match(k1ControlErrors(root).join("\n"), /no_normative_effect/);
});
```

- [ ] **Step 2: RED nachweisen**

Run: `node --test scripts/check-project-control-k1.test.mjs`

Expected: FAIL, weil Governance-Supplement und Regeln fehlen.

- [ ] **Step 3: Supplement mit unveränderlicher Grenzaussage anlegen**

Der normative Kern lautet exakt sinngleich zu:

```text
In current K1 project control, GATE-GOV-0 is the non-executable reference
name for the historical identifier GATE-G0 in governance design commit
a6a8e7d. It does not rename, amend, activate, or supersede that historical
Git object.

G0-SRV-0 through G0-SRV-12 are a separate, preceding infrastructure
programme. Their state and destructive-action prohibition are defined only
by docs/project-control/ground-zero/GATE-STATUS.md.

Debian-pilot and PROFILE-DEBIAN-PILOT statements in the historical design
are superseded as executable infrastructure guidance by Ubuntu Server
24.04.4 LTS. They remain historical evidence and authorize no server action.

This supplement has no normative effect until a new explicitly scoped
operator approval is recorded. It performs no governance genesis, creates
no authority, signs no record, permits no push and permits no server action.
```

Es wird nur festgehalten, dass 14 ungetrackte Governance-Planentwürfe in einem historischen Worktree existieren und nicht importiert/ausgeführt werden. Pfade, Inhalte und der separate HTML-Status werden nicht als K1-Evidenz übernommen.

- [ ] **Step 4: Historischen Blob fail-closed prüfen**

Der Validator ruft Git ohne Shell auf und vergleicht:

```text
a6a8e7dca456d14a6748b204b787b235fdedf9be:docs/superpowers/specs/2026-08-24-aurelia-g0-governance-design.md
0aad1cd64a8896a52df84e6c7918c8df3968ae83
```

Eine Abweichung ist Exit 1; eine nicht auflösbare Referenz Exit 2.

- [ ] **Step 5: GREEN nachweisen**

```powershell
node --test scripts/check-project-control-k1.test.mjs
npm run check:k1-control
git diff --check
```

- [ ] **Step 6: Commit erstellen**

```powershell
git add docs/project-control/GATE-GOV-0-SUPPLEMENT.md scripts/check-project-control-k1.mjs scripts/check-project-control-k1.test.mjs
git commit -m "docs: record non-normative governance boundary"
```

### Task 3: Fail-closed Publikationsgraph-Scanner

**Files:**
- Create: `scripts/check-push-graph.mjs`
- Create: `scripts/check-push-graph.test.mjs`
- Modify: `package.json`
- Modify: `docs/project-control/K1-STATUS.md`

- [ ] **Step 1: Synthetische Scanner-Tests schreiben**

Die Tests erzeugen temporäre Git-Repositories und prüfen jede Kategorie ohne echte Trefferwerte auszugeben:

```javascript
for (const [category, fixture] of [
  ["credential_like", ["PREVIEW", "CLIENT", "SECRET"].join("_") + "=example-not-a-secret"],
  ["absolute_user_path", ["C:", "Users", "Example", "file.txt"].join("\\")],
  ["unc_path", "\\\\" + ["internal-host", "share"].join("\\")],
  ["raw_source_tree", "docs/project-control/external-analyses/x/source/raw.txt"],
  ["env_or_key_material", ".env"],
]) {
  test(`reports ${category} without echoing content`, () => {
    const report = scanFixture(fixture);
    assert.equal(report.findings[0].category, category);
    assert.equal(report.output.includes(fixture), false);
  });
}

test("fails closed when base cannot be resolved", () => {
  const result = scanGraph({ base: "missing-ref", head: "HEAD" });
  assert.equal(result.exitCode, 2);
});
```

- [ ] **Step 2: RED nachweisen**

Run: `node --test scripts/check-push-graph.test.mjs`

Expected: FAIL wegen fehlendem Scanner.

- [ ] **Step 3: Scanner minimal implementieren**

Öffentliche API:

Die öffentliche Schnittstelle ist vollständig festgelegt als:

```typescript
export type GraphFinding = { category: string; blob: string; path: string; count: number };
export type GraphScan = { exitCode: 0 | 1 | 2; findings: GraphFinding[]; diagnostics: string[] };
export declare function classifyPath(path: string): string | null;
export declare function classifyBlob(path: string, bytes: Uint8Array): Omit<GraphFinding, "blob">[];
export declare function scanGraph(input: {
  root: string;
  base: string;
  head: string;
  mode?: "full";
}): GraphScan;
```

CLI:

```text
node scripts/check-push-graph.mjs --base origin/codex/aurelia-vorbereitung --head HEAD --mode full
```

Ausgabe je Befund nur: Kategorie, Blob-ID, Repositorypfad, Anzahl. Ein fehlender oder unauflösbarer Base-/Head-Ref ist Exit 2. Jeder Fund ist Exit 1. Nur ein vollständig sauberer Graph ist Exit 0.

- [ ] **Step 4: Package-Script ergänzen**

```json
"check:push-graph": "node scripts/check-push-graph.mjs"
```

Das nackte Package-Script bleibt absichtlich Exit 2, weil `--base` und `--head` zwingend sind.

- [ ] **Step 5: GREEN der synthetischen Tests nachweisen**

Run: `node --test scripts/check-push-graph.test.mjs`

Expected: alle Fixtures grün; keine Testausgabe enthält Fixture-Inhalte.

- [ ] **Step 6: Reales Gate gegen beabsichtigten Publikationsgraph ausführen**

```powershell
node scripts/check-push-graph.mjs --base origin/codex/aurelia-vorbereitung --head HEAD --mode full
```

Expected current status: Exit 1 mit kategorisierten Befunden, mindestens wegen des bekannten Credential-like Preview-Literals und operativer Identitätsmerkmale in versionierter V3-Evidenz. Kein gefundener Wert darf ausgegeben werden. K1 bleibt lokal fortsetzbar; Push bleibt gesperrt.

- [ ] **Step 7: Statusdokument um roten Publikationszustand ergänzen**

```yaml
publication_gate: blocked
publication_gate_reason_categories:
  - credential_like
  - operational_identity
```

Keine V3-Datei, kein Preview-Credential und kein alter Git-Commit wird in K1 verändert.

- [ ] **Step 8: Commit erstellen**

```powershell
git add scripts/check-push-graph.mjs scripts/check-push-graph.test.mjs package.json docs/project-control/K1-STATUS.md
git commit -m "chore(security): add fail-closed push graph gate"
```

### Task 4: Maschinenlesbare K1-Matrix und fail-closed Kanonvalidator

**Historische Quelle:** Strukturideen aus `b20ee87`, aber keine alten Phase-/Debian-/WebRTC-Regeln übernehmen.

**Files:**
- Create: `src/lib/concept/canon.ts`
- Create: `scripts/canon-contract.mjs`
- Create: `scripts/canon-contract.test.mjs`
- Modify: `package.json`

- [ ] **Step 1: Fixture-basierte Negativtests schreiben**

```javascript
test("rejects auth or database off", () => {
  assert.match(matrixErrors({ ...VALID_CANON, auth: "off" }).join("\n"), /auth/);
  assert.match(matrixErrors({ ...VALID_CANON, database: "off" }).join("\n"), /database/);
});

test("rejects active Debian, 2x1TB, WebRTC and unqualified phase wording", () => {
  const errors = activeTextErrors(makeActiveFixture([
    "Debian Bookworm",
    "2×1 TB",
    "WebRTC nachrangig",
    "Phase 1 läuft",
  ]));
  assert.match(errors.join("\n"), /debian_or_bookworm/);
  assert.match(errors.join("\n"), /two_by_one_tb/);
  assert.match(errors.join("\n"), /webrtc_or_video/);
  assert.match(errors.join("\n"), /unqualified_phase_1/);
});

test("excludes historical analyses and plans from active text rules", () => {
  const errors = activeTextErrors(makeHistoricalFixture("Debian Bookworm WebRTC nachrangig"));
  assert.deepEqual(errors, []);
});

test("rejects missing and duplicate IDs in every family", () => {
  const errors = idFamilyErrors(invalidFamilies());
  for (const family of ["D", "C", "X", "U", "K", "H", "O", "WV"]) {
    assert.match(errors.join("\n"), new RegExp(`${family}-ID`));
  }
});
```

- [ ] **Step 2: RED nachweisen**

Run: `node --experimental-strip-types --test scripts/canon-contract.test.mjs`

Expected: FAIL wegen fehlender Kanonmatrix/Validator-APIs.

- [ ] **Step 3: Exakte Kanonmatrix anlegen**

```typescript
export const K1_CANON = Object.freeze({
  phase0: "abgenommen",
  phase1: "shell_present_product_paused",
  pauseUntil: "G0-SRV-12",
  currentServerGate: "G0-SRV-0",
  destructiveActionsAllowed: false,
  auth: "on",
  database: "on",
  dataClass: "synthetic",
  os: "Ubuntu Server 24.04.4 LTS amd64",
  desktop: "minimal GNOME",
  storageDevices: 2,
  storageSizeTbEach: 2,
  storageModel: "WD_BLACK SN850X",
  storagePlan: ["RAID1", "LUKS2", "LVM"],
  video: "excluded",
  webrtc: "excluded",
  phase9: "deleted",
  cuda: "locked",
  usb: "locked",
  article9Plaintext: "locked",
  governanceGate: "GATE-GOV-0",
  serverGateRange: "G0-SRV-0…12",
} as const);
```

- [ ] **Step 4: Validator mit expliziter Active-Allowlist implementieren**

Öffentliche API:

```javascript
export const ACTIVE_FILES = Object.freeze([
  "AGENTS.project.md", "SECURITY.md", "docs/STATUS.md",
  "docs/00-index.md", "docs/01-vision.md", "docs/02-architecture.md",
  "docs/03-security-dsgvo.md", "docs/04-compute.md", "docs/05-data.md",
  "docs/06-kernel-abi.md", "docs/07-identity.md", "docs/08-ui-a11y.md",
  "docs/09-roadmap.md", "docs/10-decisions.md", "docs/11-llm-handoff.md",
  "docs/12-heritage.md", "docs/13-lovable.md", "docs/14-hardware.md",
  "docs/15-live.md", "docs/16-wellbeing.md", "docs/17-cuda.md",
  "docs/18-clipboard.md", "docs/19-kozyrev.md", "docs/20-freigabe.md",
  "docs/21-timer.md", "docs/22-kozyrev-labor.md", "docs/23-id-schema.md",
  "docs/24-standalone.md", "docs/25-offen.md", "docs/26-wiedervorlage.md",
  "docs/project-control/README.md", "docs/project-control/ground-zero/GATE-STATUS.md",
  "src/lib/concept/canon.ts", "src/lib/concept/decisions.ts",
  "src/lib/concept/freigabe.ts", "src/lib/concept/id-legend.ts",
  "src/lib/concept/kozyrev-labor.ts", "src/lib/concept/lovable-nutzen.ts",
  "src/lib/concept/nav.ts", "src/lib/concept/offen.ts",
  "src/lib/concept/standalone.ts", "src/lib/concept/wiedervorlage.ts",
  "src/components/concept/shell.tsx",
  "src/routes/architektur.tsx", "src/routes/compute.tsx", "src/routes/daten.tsx",
  "src/routes/entscheidungen.tsx", "src/routes/freigabe.tsx",
  "src/routes/gestaltung.tsx", "src/routes/hardware.tsx",
  "src/routes/identitaet.tsx", "src/routes/index.tsx", "src/routes/kozyrev.tsx",
  "src/routes/leitplanken.tsx", "src/routes/live.tsx", "src/routes/login.tsx",
  "src/routes/lovable.tsx", "src/routes/module.tsx", "src/routes/offen.tsx",
  "src/routes/praxis.tsx", "src/routes/repos.tsx", "src/routes/roadmap.tsx",
  "src/routes/sicherheit.tsx", "src/routes/timer.tsx",
  "src/routes/wellbeing.tsx", "src/routes/zwischenablage.tsx",
]);
export const EXCLUDED_PREFIXES = Object.freeze([
  "docs/project-control/external-analyses/",
  "docs/superpowers/specs/",
  "docs/superpowers/plans/",
]);
```

Die Validator-Schnittstelle ist:

```typescript
export declare function matrixErrors(canon: typeof K1_CANON): string[];
export declare function activeTextErrors(root: string, files?: readonly string[]): string[];
export declare function idFamilyErrors(families: Record<string, readonly { id: string }[]>): string[];
export declare function sourceBoundaryErrors(root: string): string[];
export declare function canonErrors(root: string): string[];
```

`ACTIVE_FILES` umfasst `AGENTS.project.md`, `SECURITY.md`, aktive `docs/00…26`, `docs/STATUS.md`, `docs/project-control/README.md`, `ground-zero/GATE-STATUS.md`, `src/lib/concept/*.ts`, `src/components/concept/shell.tsx` und präsentierende `src/routes/*.tsx`; technische API-Routen bleiben ausgeschlossen. Der Validator prüft zusätzlich die zwei Rohquellen-Regeln in `.gitignore`.

- [ ] **Step 5: Package-Gate ergänzen**

```json
"check:canon": "node --experimental-strip-types scripts/canon-contract.mjs"
```

- [ ] **Step 6: Validator-Unit-Tests grün, Repositoryvertrag erwartbar rot nachweisen**

```powershell
node --experimental-strip-types --test scripts/canon-contract.test.mjs
npm run check:canon
```

Expected: Fixture-/API-Tests grün; der reale Repositorycheck listet die noch nicht bereinigten aktiven Quellen und ist Exit 1. Das ist die RED-Evidenz für Tasks 5 und 6.

- [ ] **Step 7: Commit erstellen**

```powershell
git add src/lib/concept/canon.ts scripts/canon-contract.mjs scripts/canon-contract.test.mjs package.json
git commit -m "test: specify fail-closed K1 canon"
```

### Task 5: Aktive Dokumente und Konzeptdaten auf K1 konsolidieren

**Files:**
- Modify: `AGENTS.project.md`
- Modify: `docs/02-architecture.md`
- Modify: `docs/03-security-dsgvo.md`
- Modify: `docs/15-live.md`
- Modify: `docs/16-wellbeing.md`
- Modify: `docs/18-clipboard.md`
- Modify: `docs/20-freigabe.md`
- Modify: `docs/22-kozyrev-labor.md`
- Modify: `docs/23-id-schema.md`
- Modify: `docs/25-offen.md`
- Modify: `src/lib/concept/decisions.ts`
- Modify: `src/lib/concept/freigabe.ts`
- Modify: `src/lib/concept/id-legend.ts`
- Modify: `src/lib/concept/lovable-nutzen.ts`
- Modify: `src/lib/concept/nav.ts`
- Modify: `src/lib/concept/offen.ts`
- Modify: `src/lib/concept/standalone.ts`
- Modify: `src/lib/concept/wiedervorlage.ts`

- [ ] **Step 1: Aktuelle RED-Liste sichern**

Run: `npm run check:canon`

Expected: Exit 1 mit Pfad und Regel für jede aktive Abweichung; keine historische Analyse oder Spec erscheint als Textverstoß.

- [ ] **Step 2: Zentrale Decision-Locks konsolidieren**

`decisions.ts` erhält genau eine `CANONICAL_DECISION_LOCKS`-Map für D01–D24. `DECISIONS[].lock` wird ausschließlich daraus abgeleitet. D08/D10/D12 sind gesetzt; D09/D11 bleiben ausdrücklich Wiedervorlage/empfohlen gemäß freigegebenem Produktkanon. Keine Summary besitzt einen zweiten Lock.

```typescript
export const CANONICAL_DECISION_LOCKS = Object.freeze({
  D01: "gesetzt", D02: "gesetzt", D03: "gesetzt", D04: "gesetzt",
  D05: "gesetzt", D06: "gesetzt", D07: "gesetzt", D08: "gesetzt",
  D09: "empfohlen", D10: "gesetzt", D11: "empfohlen", D12: "gesetzt",
  D13: "gesetzt", D14: "gesetzt", D15: "gesetzt", D16: "gesetzt",
  D17: "gesetzt", D18: "gesetzt", D19: "gesetzt", D20: "gesetzt",
  D21: "gesetzt", D22: "gesetzt", D23: "gesetzt", D24: "gesetzt",
} as const);
```

- [ ] **Step 3: Veraltete aktive Aussagen durch feste K1-Aussagen ersetzen**

Jede aktive Quelle verwendet, ihrem Kontext entsprechend, diese Aussagen:

```text
Phase 0 ist abgenommen.
Die Phase-1-Schale einschließlich Authentifizierung und Mandantenbasis ist technisch vorhanden.
Weitere Produktarbeit ist bis zum dokumentiert bestandenen G0-SRV-12 pausiert.
Authentifizierung und Datenbank sind aktiv; verarbeitet werden ausschließlich synthetische Daten.
Zielsystem ist Ubuntu Server 24.04.4 LTS amd64 mit minimalem GNOME.
Geplant sind 2×2 TB WD_BLACK SN850X mit RAID1/LUKS2/LVM.
AURELIA enthält kein Video, kein WebRTC, kein TURN und keine Videoaufzeichnung; Phase 9 ist gestrichen.
CUDA, USB und Art.-9-Klartext bleiben gesperrt.
```

Kontextuell historische Supersession-Hinweise dürfen alte Begriffe nur mit `historisch`, `superseded` und `nicht ausführbar` nennen. Produkttexte und aktuelle Architektur dürfen sie nicht als Alternative anbieten.

- [ ] **Step 4: Begriffe/Typen neutralisieren, wenn sie aktuelle Debian-Bindung ausdrücken**

Wenn `standalone.ts` eine öffentliche Eigenschaft `mehrwertFuerDebian` besitzt, wird sie konsistent zu `mehrwertFuerOrigin` umbenannt und jeder Import/Consumer im selben Commit angepasst. Reine historische Zitate werden nicht umbenannt.

- [ ] **Step 5: ID- und Statusregeln grün nachweisen**

```powershell
node --experimental-strip-types --test scripts/canon-contract.test.mjs
npm run check:canon
npm run typecheck
```

Expected: Fixturetests grün; Repositoryvertrag darf nur noch Portalpfade aus Task 6 melden; Typecheck Exit 0.

- [ ] **Step 6: Commit erstellen**

```powershell
git add AGENTS.project.md docs/02-architecture.md docs/03-security-dsgvo.md docs/15-live.md docs/16-wellbeing.md docs/18-clipboard.md docs/20-freigabe.md docs/22-kozyrev-labor.md docs/23-id-schema.md docs/25-offen.md src/lib/concept/decisions.ts src/lib/concept/freigabe.ts src/lib/concept/id-legend.ts src/lib/concept/lovable-nutzen.ts src/lib/concept/nav.ts src/lib/concept/offen.ts src/lib/concept/standalone.ts src/lib/concept/wiedervorlage.ts
git commit -m "docs: reconcile active K1 product canon"
```

### Task 6: Portal und zentrale Schale auf K1 ableiten

**Files:**
- Modify: `src/components/concept/shell.tsx`
- Modify: `src/routes/index.tsx`
- Modify: `src/routes/architektur.tsx`
- Modify: `src/routes/daten.tsx`
- Modify: `src/routes/entscheidungen.tsx`
- Modify: `src/routes/freigabe.tsx`
- Modify: `src/routes/hardware.tsx`
- Modify: `src/routes/identitaet.tsx`
- Modify: `src/routes/kozyrev.tsx`
- Modify: `src/routes/leitplanken.tsx`
- Modify: `src/routes/live.tsx`
- Modify: `src/routes/lovable.tsx`
- Modify: `src/routes/offen.tsx`
- Modify: `src/routes/repos.tsx`
- Modify: `src/routes/roadmap.tsx`
- Modify: `src/routes/sicherheit.tsx`
- Modify: `src/routes/wellbeing.tsx`

- [ ] **Step 1: Route-RED aus Repositoryvertrag bestätigen**

Run: `npm run check:canon`

Expected: Exit 1 ausschließlich oder überwiegend mit Portal-/Shellabweichungen.

- [ ] **Step 2: Globalen Pausenhinweis in der Schale implementieren**

Die sichtbare Schale zeigt auf jeder Konzeptseite:

```text
Phase-1-Schale vorhanden · Produktarbeit pausiert bis G0-SRV-12
Nur synthetische Daten · keine Server-, CUDA-, USB- oder Art.-9-Aktivierung
```

Der Hinweis ist semantisch als Statusbereich (`role="status"`) markiert und auf Mobilansicht ohne horizontales Überlaufen lesbar.

- [ ] **Step 3: Alle abgeleiteten Portaltexte konsolidieren**

Insbesondere:

- `index.tsx`: Ubuntu 24.04.4, 2×2 TB, Pause statt Startfreigabe.
- `hardware.tsx`: 2×2 TB und geplanter, noch nicht ausgeführter RAID1/LUKS2/LVM-Pfad.
- `roadmap.tsx`: Budget `2/16/2`, Phase-1-Schale vorhanden und pausiert.
- `entscheidungen.tsx`: Auth nicht „aus“; D08/D10/D12 gesetzt, D09/D11 Wiedervorlage.
- `leitplanken.tsx`: kein Standardvideo, sondern absolutes No-Video/No-WebRTC.
- `live.tsx`: WebSocket-Fachkanal ohne WebRTC/TURN.
- `repos.tsx`: kein aktueller Debian-Root-Bezug.

- [ ] **Step 4: Kanon, Typecheck und fokussierten UI-Test grün nachweisen**

```powershell
npm run check:canon
npm run typecheck
```

Expected: Kanon und Typecheck Exit 0.

- [ ] **Step 5: Dev-Server erst nach Task 9 starten und Browserprüfung vormerken**

Keine visuelle Vollabnahme in diesem Task, solange der Windows-Vite-Wrapper noch nicht repariert ist. Die UI-Abnahme erfolgt in Task 13 gegen Dev und migrationsfreien Build.

- [ ] **Step 6: Commit erstellen**

```powershell
git add src/components/concept/shell.tsx src/routes/index.tsx src/routes/architektur.tsx src/routes/daten.tsx src/routes/entscheidungen.tsx src/routes/freigabe.tsx src/routes/hardware.tsx src/routes/identitaet.tsx src/routes/kozyrev.tsx src/routes/leitplanken.tsx src/routes/live.tsx src/routes/lovable.tsx src/routes/offen.tsx src/routes/repos.tsx src/routes/roadmap.tsx src/routes/sicherheit.tsx src/routes/wellbeing.tsx
git commit -m "fix: reconcile K1 concept portal"
```

### Task 7: Fail-closed plattformübergreifender Test-Runner

**Files:**
- Create: `scripts/test-runner.mjs`
- Create: `scripts/test-runner.test.mjs`
- Modify: `package.json`

- [ ] **Step 1: Runner-Tests zuerst schreiben**

```javascript
test("discovers and sorts both mandatory test groups", () => {
  const groups = discoverRequiredTestGroups(makeFixture());
  assert.deepEqual(groups.mjs, ["scripts/a.test.mjs", "scripts/z.test.mjs"]);
  assert.deepEqual(groups.typescript, [
    "src/lib/app-data/app-data.test.ts",
    "src/lib/auth/gate-identity.test.ts",
  ]);
});

test("fails before spawn when a mandatory group is empty", () => {
  assert.throws(() => assertNoEmptyGroups({ mjs: [], typescript: ["x.test.ts"] }), /mjs.*empty/i);
});

test("uses node directly and propagates exit or signal", () => {
  assert.equal(nodeTestCommand(["a.test.mjs"]).command, process.execPath);
  assert.equal(exitStatusFromChild(7, null), 7);
  assert.notEqual(exitStatusFromChild(null, "SIGTERM"), 0);
});
```

- [ ] **Step 2: RED nachweisen**

Run: `node --test scripts/test-runner.test.mjs`

Expected: FAIL wegen fehlendem Runner.

- [ ] **Step 3: Runner implementieren**

```javascript
export function nodeTestCommand(files) {
  return { command: process.execPath, args: ["--experimental-strip-types", "--test", ...files] };
}
```

Die vollständige Runner-Schnittstelle ist:

```typescript
export type TestGroups = { mjs: string[]; typescript: string[] };
export declare function discoverRequiredTestGroups(root: string): TestGroups;
export declare function assertNoEmptyGroups(groups: TestGroups): void;
export declare function nodeTestCommand(files: readonly string[]): { command: string; args: string[] };
export declare function exitStatusFromChild(code: number | null, signal: NodeJS.Signals | null): number;
```

Die Discovery ist lexikographisch sortiert, rekursiert nicht unkontrolliert und verwendet keine Shell. Der Runner startet einen einzigen Node-Testprozess für alle freigegebenen Dateien und propagiert dessen Status.

- [ ] **Step 4: Package-Script ersetzen**

```json
"test": "node scripts/test-runner.mjs"
```

- [ ] **Step 5: GREEN des Runners und ehrliche Suite-Exposition nachweisen**

```powershell
node --test scripts/test-runner.test.mjs
npm test
```

Expected: Runner-Tests grün. Die vollständige Suite entdeckt alle MJS- und TS-Tests und kann wegen der noch nicht reparierten Legacy-Verträge rot sein; `0 tests` mit Exit 0 ist verboten.

- [ ] **Step 6: Commit erstellen**

```powershell
git add scripts/test-runner.mjs scripts/test-runner.test.mjs package.json
git commit -m "test: add fail-closed cross-platform runner"
```

### Task 8: Auth-on-, Migration-, PWA-Fixture- und Windows-Testverträge

**Files:**
- Modify: `scripts/with-app-env.test.mjs`
- Modify: `scripts/check-auth-invariant.test.mjs`
- Modify: `scripts/migration-plan.test.mjs`
- Modify: `scripts/grok-pwa-plugin.test.mjs`
- Create: `scripts/test-support/symlink-capability.mjs`

- [ ] **Step 1: Auth-on- und Migrationserwartungen als neue RED-Verträge formulieren**

Die Tests müssen festschreiben:

```javascript
assert.deepEqual(readAppEnv(projectRoot()), {}); // fehlende Datei = kein Override
assert.equal(resolveAuthEnabled({}), true);      // kein Override = Auth an
assert.deepEqual(discoverRootMigrations(root), [
  "migrations/0001_auth.sql",
  "migrations/0002_tenants.sql",
]);
```

Die bytegleiche Auth-Schemaquelle unter `migrations/auth/0001_auth.sql` bleibt geprüft.

- [ ] **Step 2: Windows-Symlink-Capability explizit behandeln**

```javascript
export function directorySymlinkCapability(target, link) {
  try {
    symlinkSync(target, link, process.platform === "win32" ? "junction" : "dir");
    return { supported: true };
  } catch (error) {
    if (error?.code === "EPERM" || error?.code === "EACCES") return { supported: false, reason: error.code };
    throw error;
  }
}
```

Nur `EPERM`/`EACCES` dürfen zu einem capability-skip führen; alle anderen Fehler bleiben rot.

- [ ] **Step 3: RED nachweisen**

```powershell
node --test scripts/with-app-env.test.mjs scripts/check-auth-invariant.test.mjs scripts/migration-plan.test.mjs scripts/grok-pwa-plugin.test.mjs
```

Expected: definierte Abweichungen gegen alte Testannahmen oder fehlenden Capability-Helfer.

- [ ] **Step 4: Tests auf synthetische Fixtures und korrekten Auth-on-Kanon umstellen**

PWA-Tests injizieren temporäre `site.json`-Fixtures und behaupten nicht mehr, dass ignorierte Plattformassets im Git-Workspace vorhanden sein müssen. Produktionsverhalten wird nicht abgeschwächt; der reale Assetbestand wird in Task 12 separat fail-closed geprüft.

- [ ] **Step 5: GREEN der fokussierten Verträge nachweisen**

Run: `node --test scripts/with-app-env.test.mjs scripts/check-auth-invariant.test.mjs scripts/migration-plan.test.mjs scripts/grok-pwa-plugin.test.mjs`

Expected: alle Tests grün oder nur exakt capability-begründete Symlink-Skips.

- [ ] **Step 6: Vollständige Suite ausführen**

Run: `npm test`

Expected: alle entdeckten Tests grün; Gesamtzahl ist größer als die Ausgangsbasis und keine Pflichtgruppe meldet null Tests.

- [ ] **Step 7: Commit erstellen**

```powershell
git add scripts/with-app-env.test.mjs scripts/check-auth-invariant.test.mjs scripts/migration-plan.test.mjs scripts/grok-pwa-plugin.test.mjs scripts/test-support
git commit -m "test: align auth-on and platform test contracts"
```

### Task 9: Vite-CLI plattformübergreifend auflösen

**Historische Quelle:** Algorithmus aus `cfb06d3`/Test aus `3b3d22f`, fachlich neu gegen Auth-on getestet.

**Files:**
- Modify: `scripts/with-app-env.test.mjs`
- Modify: `scripts/with-app-env.mjs`

- [ ] **Step 1: Vite-Auflösungstest schreiben**

```javascript
test("Vite invocation uses the installed JavaScript CLI without a shell", () => {
  const invocation = resolveInvocation("vite", ["build"]);
  assert.equal(invocation.command, process.execPath);
  assert.ok(isAbsolute(invocation.args[0]));
  assert.match(invocation.args[0], /vite[\\/]bin[\\/]vite\.js$/i);
  assert.doesNotMatch(invocation.args[0], /\.cmd$/i);
});
```

- [ ] **Step 2: RED nachweisen**

Run: `node --test --test-name-pattern="Vite invocation" scripts/with-app-env.test.mjs`

Expected: FAIL, weil `resolveInvocation` fehlt oder `vite` unverändert zurückgegeben wird.

- [ ] **Step 3: Minimalen Resolver implementieren**

```javascript
export function resolveInvocation(command, args) {
  if (command !== "vite") return { command, args };
  const packagePath = fileURLToPath(import.meta.resolve("vite/package.json"));
  const packageJson = JSON.parse(readFileSync(packagePath, "utf8"));
  const cli = packageJson?.bin?.vite;
  if (typeof cli !== "string") throw new Error("vite/package.json does not define a vite CLI");
  return { command: process.execPath, args: [resolve(dirname(packagePath), cli), ...args] };
}
```

`main()` startet anschließend `invocation.command` mit `invocation.args`, `shell: false`, bestehender Env-Merge- und Signalbehandlung.

- [ ] **Step 4: GREEN und migrationsfreien Build nachweisen**

```powershell
node --test scripts/with-app-env.test.mjs
npm run build:dev
```

Expected: Test grün; `build:dev` Exit 0. `npm run build` wird nicht ausgeführt.

- [ ] **Step 5: Commit erstellen**

```powershell
git add scripts/with-app-env.mjs scripts/with-app-env.test.mjs
git commit -m "fix: resolve Vite CLI through installed package"
```

### Task 10: Selbsthostende Auth-Invariantenprüfung

**Files:**
- Create: `scripts/check-auth-with-dev-server.mjs`
- Create: `scripts/check-auth-with-dev-server.test.mjs`
- Modify: `package.json`

- [ ] **Step 1: Lifecycle-Tests mit injizierten Abhängigkeiten schreiben**

```javascript
test("waits for app-env, checks auth and terminates only its child", async () => {
  const result = await checkAuthWithDevServer({ spawn: fakeSpawn, fetch: readyFetch, timeoutMs: 1000 });
  assert.equal(result.status, "match");
  assert.equal(fakeChild.terminated, true);
});

test("terminates its child when readiness times out", async () => {
  await assert.rejects(
    checkAuthWithDevServer({ spawn: fakeSpawn, fetch: neverReady, timeoutMs: 10 }),
    /readiness timeout/i,
  );
  assert.equal(fakeChild.terminated, true);
});
```

- [ ] **Step 2: RED nachweisen**

Run: `node --test scripts/check-auth-with-dev-server.test.mjs`

Expected: FAIL wegen fehlender Implementierung.

- [ ] **Step 3: Wrapper implementieren**

```javascript
export const DEFAULT_AUTH_CHECK = Object.freeze({ timeoutMs: 30_000, port: 8080 });
```

Die vollständige Schnittstelle ist:

```typescript
export declare function checkAuthWithDevServer(options?: {
  spawnImpl?: typeof import("node:child_process").spawn;
  fetchImpl?: typeof fetch;
  timeoutMs?: number;
  port?: number;
}): Promise<{ status: "match"; devAuthEnabled: true; buildAuthEnabled: true }>;
```

Der reale Kindprozess wird ausschließlich als `process.execPath scripts/with-app-env.mjs vite dev --host 127.0.0.1 --port 8080` gestartet. Ein abweichender, ausschließlich in Tests injizierter Port wird als Dezimalzahl an dieselbe Argumentposition gesetzt. Der Wrapper wartet begrenzt auf `/__app-env`, verwendet die bestehenden reinen APIs `probeDevAuthEnabled` und `compareAuthInvariant` und beendet ausschließlich den selbst gestarteten Prozess im `finally`-Block.

- [ ] **Step 4: Package-Script umstellen**

```json
"check:auth": "node scripts/check-auth-with-dev-server.mjs"
```

- [ ] **Step 5: GREEN und reale Abnahme nachweisen**

```powershell
node --test scripts/check-auth-with-dev-server.test.mjs
npm run check:auth
```

Expected: Tests grün; reale Prüfung meldet Auth-on-Übereinstimmung und räumt den selbst gestarteten Dev-Prozess auf.

- [ ] **Step 6: Commit erstellen**

```powershell
git add scripts/check-auth-with-dev-server.mjs scripts/check-auth-with-dev-server.test.mjs package.json
git commit -m "test: make auth invariant check self-hosting"
```

### Task 11: Browser-Smoke sicher und worktree-portabel machen

**Files:**
- Modify: `scripts/browser-smoke.mjs`
- Modify: `scripts/browser-smoke-verdict.mjs`
- Modify: `scripts/browser-smoke-verdict.test.mjs`

- [ ] **Step 1: Pfadvertrags-Tests zuerst schreiben**

```javascript
test("derives the default smoke output below the supplied workspace", () => {
  const root = join(TEMPLATE_ROOT, "fixture-worktree");
  assert.equal(defaultSmokeOutput(root), join(root, "screenshots", "app-builder-preview.png"));
});

test("uses an injected default output without changing explicit CLI output", () => {
  const rootDefault = join(TEMPLATE_ROOT, "fixture-worktree", "screenshots", "default.png");
  assert.equal(parseSmokeArgs([], {}, { defaultOutPng: rootDefault }).outPng, rootDefault);
  assert.equal(parseSmokeArgs(["http://127.0.0.1:8080/", "screenshots/explicit.png"], {}, { defaultOutPng: rootDefault }).outPng, "screenshots/explicit.png");
});
```

- [ ] **Step 2: RED nachweisen**

Run: `node --test scripts/browser-smoke-verdict.test.mjs`

Expected: FAIL, weil `defaultSmokeOutput` und die Default-Option noch fehlen.

- [ ] **Step 3: Plattformneutralen Default implementieren**

```diff
 import { createHash } from "node:crypto";
+import { join } from "node:path";

+export function defaultSmokeOutput(root) {
+  return join(root, "screenshots", "app-builder-preview.png");
+}

-export function parseSmokeArgs(argv, env = {}) {
+export function parseSmokeArgs(argv, env = {}, defaults = {}) {
   const positional = [];
   let baseline = env.BROWSER_SMOKE_BASELINE || "";
   for (let i = 0; i < argv.length; i++) {
     const arg = argv[i];
     if (arg === "--baseline") {
       const value = argv[++i];
       if (!value) return { error: "--baseline requires a path to a prior verdict JSON" };
       baseline = value;
     } else if (arg.startsWith("--baseline=")) {
       const value = arg.slice("--baseline=".length);
       if (!value) return { error: "--baseline requires a path to a prior verdict JSON" };
       baseline = value;
     } else if (arg.startsWith("--")) {
       return { error: `unknown flag: ${arg}` };
     } else {
       positional.push(arg);
     }
   }
+  const defaultOutPng = defaults.defaultOutPng ?? "/workspace/screenshots/app-builder-preview.png";
   return {
     url: positional[0] || "http://127.0.0.1:8080/",
-    outPng: positional[1] || "/workspace/screenshots/app-builder-preview.png",
+    outPng: positional[1] || defaultOutPng,
     baseline,
   };
 }
```

Dies sind exakte Ersetzungen an Funktionssignatur und Rückgabeblock der bestehenden Parserfunktion; ihre vorhandene Flag-/Positional-Validierung bleibt bytegleich.

- [ ] **Step 4: Smoke-Script auf den realen Projektroot begrenzen**

`browser-smoke.mjs` ermittelt `projectRoot()` aus `with-app-env.mjs`, setzt `SCREENSHOT_ROOT = join(projectRoot(), "screenshots")`, übergibt `defaultSmokeOutput(projectRoot())` an `parseSmokeArgs` und erlaubt Ausgaben/Baselines ausschließlich unter `SCREENSHOT_ROOT`. Loopback-URL-Prüfung, `--no-sandbox`, Konsolenfehlerprüfung und beide Viewports bleiben unverändert.

- [ ] **Step 5: GREEN und Guard-Verhalten nachweisen**

```powershell
node --test scripts/browser-smoke-verdict.test.mjs
node scripts/browser-smoke.mjs http://127.0.0.1:9/ screenshots/k1-unreachable.png
```

Expected: Unit-Tests grün; der unerreichbare Loopback-Smoke ist Exit 1, schreibt sein Fehlerurteil ausschließlich unter `screenshots/` und schreibt nichts außerhalb des Worktrees.

- [ ] **Step 6: Commit erstellen**

```powershell
git add scripts/browser-smoke.mjs scripts/browser-smoke-verdict.mjs scripts/browser-smoke-verdict.test.mjs
git commit -m "test: make browser smoke worktree portable"
```

### Task 12: Explizites Gate für verwaltete Plattformassets

**Files:**
- Create: `scripts/platform-assets.mjs`
- Create: `scripts/platform-assets.test.mjs`
- Modify: `package.json`
- Modify: `docs/project-control/K1-STATUS.md`

- [ ] **Step 1: Fixture-Tests schreiben**

```javascript
test("reports every missing managed asset", () => {
  const report = inspectPlatformAssets(makeFixture(["icon-180.png"]));
  assert.equal(report.status, "platform_assets_unavailable");
  assert.ok(report.missing.includes("install/styles.css"));
});

test("accepts a complete synthetic managed-asset fixture", () => {
  assert.deepEqual(inspectPlatformAssets(makeCompleteFixture()).missing, []);
});
```

- [ ] **Step 2: RED nachweisen**

Run: `node --test scripts/platform-assets.test.mjs`

Expected: FAIL wegen fehlendem Prüfer.

- [ ] **Step 3: Vertrag implementieren**

```javascript
export const REQUIRED_PLATFORM_ASSETS = Object.freeze([
  "icon-180.png",
  "install/styles.css",
  "install/assets/homescreen/logo-grok.svg",
  "install/assets/homescreen/ob-phone.png",
  "install/assets/homescreen/ob-ipad.png",
  "install/assets/homescreen/glass-puzzle.svg",
  "install/assets/homescreen/glass-share.svg",
  "install/assets/homescreen/plus.svg",
]);
```

Die vollständige Schnittstelle ist:

```typescript
export declare function inspectPlatformAssets(publicGrokRoot: string): {
  status: "available" | "platform_assets_unavailable";
  missing: string[];
};
```

Realer Missing-Status ist Exit 2 und heißt `platform_assets_unavailable`. Es gibt keinen Skip, keine Assetgenerierung, kein Kopieren aus unbelegter Quelle und kein `git add -f`.

- [ ] **Step 4: Package-Script ergänzen**

```json
"check:platform-assets": "node scripts/platform-assets.mjs"
```

- [ ] **Step 5: GREEN der Unit-Tests und ehrliches rotes externes Gate nachweisen**

```powershell
node --test scripts/platform-assets.test.mjs
npm run check:platform-assets
```

Expected: Unit-Tests grün; reales Gate aktuell Exit 2 mit Liste fehlender Repositorypfade, ohne erfundene Assets.

- [ ] **Step 6: Status dokumentieren und committen**

```yaml
platform_asset_gate: external_blocker
platform_asset_status: platform_assets_unavailable
```

```powershell
git add scripts/platform-assets.mjs scripts/platform-assets.test.mjs package.json docs/project-control/K1-STATUS.md
git commit -m "test: report missing managed platform assets"
```

### Task 13: Verhaltensneutrale Lintbereinigung

**Files:**
- Modify: `src/lib/app-data/client.server.ts:214`
- Modify: `src/lib/auth/use-current-user.ts:59`
- Modify: `src/routes/daten.tsx:3`
- Modify: `src/routes/gestaltung.tsx:3`

- [ ] **Step 1: Ausgangsbefunde frisch bestätigen**

Run: `npm run lint`

Expected: 1 Fehler (`no-empty`) und 3 Warnungen (ungenutztes Disable, zwei ungenutzte `P`-Importe).

- [ ] **Step 2: Minimal und ohne Verhaltenseffekt bereinigen**

- Leerer Catch-Block erhält ausschließlich einen erklärenden Kommentar, sofern bewusstes Ignorieren die bestehende Semantik ist.
- Ungenutzte ESLint-Disable-Zeile wird entfernt.
- Nur die ungenutzten `P`-Imports werden entfernt.

Keine benachbarte Logik, Formatierung oder API wird verändert.

- [ ] **Step 3: Lint und relevante Tests grün nachweisen**

```powershell
npm run lint
npm test
npm run typecheck
```

Expected: Lint 0 Fehler/0 Warnungen; Tests und Typecheck Exit 0.

- [ ] **Step 4: Commit erstellen**

```powershell
git add src/lib/app-data/client.server.ts src/lib/auth/use-current-user.ts src/routes/daten.tsx src/routes/gestaltung.tsx
git commit -m "chore: clear baseline lint findings"
```

### Task 14: Lokale Integration, Browserabnahme und K1-Evidenz

**Files:**
- Create: `docs/project-control/K1-VERIFICATION.md`
- Modify: `docs/project-control/K1-STATUS.md`

- [ ] **Step 1: Commit- und Branchintegrität prüfen**

```powershell
git status --short --branch
git merge-base --is-ancestor 8706186af01e10e4253e25abb31bf3577110dae4 HEAD
git diff --check 8706186af01e10e4253e25abb31bf3577110dae4...HEAD
```

Expected: korrekter Branch, Ancestor Exit 0, Diff-Check ohne Ausgabe.

- [ ] **Step 2: Alle lokal freigegebenen ausführbaren Gates frisch ausführen**

```powershell
npm run check:k1-control
npm run check:canon
npm test
npm run typecheck
npm run lint
npm run check:auth
npm run build:dev
```

Expected: alle sieben Befehle Exit 0. `npm run build` wird nicht ausgeführt.

- [ ] **Step 3: Bekannte externe Gates getrennt ausführen**

```powershell
npm run check:platform-assets
node scripts/check-push-graph.mjs --base origin/codex/aurelia-vorbereitung --head HEAD --mode full
```

Expected current status: beide Befehle nicht grün, mit präzisen Kategorien/Repositorypfaden und ohne sensitive Werte. Plattformassets bleiben externer Providerblocker; Publikation bleibt wegen Credential-like/operativer Identität gesperrt.

- [ ] **Step 4: Dev-Browser-Smoke auf Desktop und Mobile durchführen**

Dev-Server ausschließlich über den Wrapper starten. Danach den Smoke ausführen:

```powershell
node scripts/browser-smoke.mjs http://127.0.0.1:8080/ screenshots/k1-dev.png
```

Anschließend `screenshots/k1-dev.png` und `screenshots/k1-dev-mobile.png` visuell prüfen:

- sichtbarer Inhalt;
- globaler Pausenbanner vorhanden;
- keine horizontale Überläufe bei etwa 390×844;
- keine Browser-Konsolenfehler;
- kein Debian/2×1-TB/optionales Video/WebRTC;
- Ubuntu 24.04.4, 2×2 TB, synthetische Daten und Pause bis G0-SRV-12 sichtbar an den relevanten Stellen.

- [ ] **Step 5: Gebaute Vorschau gegen Dev-Baseline prüfen**

Nach erfolgreichem `npm run build:dev` die gebaute Vorschau mit `npm run preview -- --host 127.0.0.1 --port 8081 --strictPort` starten und danach ausführen:

```powershell
node scripts/browser-smoke.mjs http://127.0.0.1:8081/ screenshots/k1-built.png --baseline screenshots/k1-dev.json
```

Bei Quelländerung wird vor dem Retest erneut gebaut und die alte Preview beendet.

Expected: keine Divergenz, keine Modul-MIME-Fehler, sichtbarer Inhalt und saubere Konsole auf Desktop/Mobile.

- [ ] **Step 6: Evidenzdokument ohne sensitive Werte anlegen**

`K1-VERIFICATION.md` dokumentiert pro Gate:

```text
timestamp_cest | commit | command | exit | tests_passed | tests_failed | classification
```

Klassifikationen sind nur `green`, `external_blocker`, `publication_blocked`. Es werden keine Secrets, IPs, Benutzernamen, UNC-Hosts oder lokale Benutzerpfade protokolliert.

- [ ] **Step 7: Gesamtdiff durch zwei unabhängige Reviewer prüfen**

Spezifikationsreview vergleicht jede Sektion des Designs `7de43db` mit `8706186...HEAD`. Qualitäts-/Securityreview prüft Fehlerverhalten, Pfadgrenzen, Geheimnisunterdrückung, Testaussagekraft und Browserbefunde. Jede P0–P2-Feststellung wird durch den zuständigen Implementierungsagenten behoben und erneut geprüft.

- [ ] **Step 8: Abschlusszustand dokumentieren**

`K1-STATUS.md` darf nur dann `local_implementation: verified` enthalten, wenn alle lokal kontrollierbaren Gates grün sind. Unabhängig davon bleiben:

```yaml
push_authorized: false
publication_gate: blocked
platform_asset_gate: external_blocker
server_mutation: false
```

- [ ] **Step 9: Abschlusscommit erstellen**

```powershell
git add docs/project-control/K1-STATUS.md docs/project-control/K1-VERIFICATION.md
git commit -m "docs: record K1 local verification"
```

- [ ] **Step 10: Abschluss-Preflight ohne Remoteänderung**

```powershell
git status --short --branch
git log --oneline 8706186af01e10e4253e25abb31bf3577110dae4..HEAD
git diff --stat 8706186af01e10e4253e25abb31bf3577110dae4...HEAD
git diff --check 8706186af01e10e4253e25abb31bf3577110dae4...HEAD
```

Expected: sauberer Worktree, nachvollziehbare kleine lokale Commits, kein Push und keine Änderung bestehender Remote-Refs.

## 4. Stop-Bedingungen während der Ausführung

Die Arbeit stoppt vor der betroffenen Mutation bei:

- abweichendem K1-Basisvorfahr oder unerwartetem Branch;
- erforderlichem Push, Force-Push, History-Rewrite, Merge oder Rebase;
- benötigtem Server-, IPMI-, SSH- oder Remotezugriff;
- erforderlicher realer DB-Migration oder nichtsynthetischen Daten;
- Versuch, `public/__grok` ohne autoritative Quelle zu erzeugen oder zu force-adden;
- Versuch, V3-Evidenz, Preview-Credential oder historische Objekte ohne neue Freigabe zu verändern;
- unklarer Quellenpriorität zwischen Betreiberfreigabe, Projektkonstitution und aktuellem Gate-Status;
- Teständerung, die nur durch Abschwächung der Anforderung grün wird;
- P0–P2-Befund, der nach Review offen bleibt.

## 5. Plan-Selbstprüfung gegen das freigegebene Design

| Designanforderung | Planabdeckung |
|---|---|
| selektive Neuübernahme statt Merge/Cherry-pick | Ausführungsrahmen; Tasks 4–6 und 9 |
| V1/V2-Tip-Sanitisierung | Task 1 |
| eindeutige K1-Projektsteuerung | Tasks 1–2 |
| Governance-G0/Server-G0 trennen | Task 2 |
| Credential-/Publikationsgrenze | Task 3 |
| Ubuntu/2×2 TB/Pause/Auth-on/Synthetic/No-Video | Tasks 4–6 |
| vollständige ID-Familien und fail-closed Validator | Task 4 |
| kein False-green bei null MJS-Tests | Task 7 |
| Auth-on-, Migration-, PWA- und Windows-Testursachen | Task 8 |
| Vite-Portabilität | Task 9 |
| Auth-Abnahme gegen kontrollierten Dev-Server | Task 10 |
| Desktop-/Mobile-Smoke im lokalen Worktree | Tasks 11 und 14 |
| fehlende Providerassets nicht erfinden | Task 12 |
| bekannte Lintbaseline isoliert bereinigen | Task 13 |
| frische lokale Abschlussverifikation | Task 14 |

Die Dateinamen und öffentlichen APIs sind taskübergreifend einheitlich: `K1_CANON`, `k1ControlErrors`, `scanGraph`, `canonErrors`, `discoverRequiredTestGroups`, `resolveInvocation`, `checkAuthWithDevServer`, `defaultSmokeOutput` und `inspectPlatformAssets`. Kein Task setzt eine nicht freigegebene Remote-, Server- oder Datenbankmutation voraus.

## 6. Abnahmegrenze

K1 kann lokal technisch verifiziert werden, obwohl zwei externe/gesondert freizugebende Gates rot bleiben. Das ist kein vollständiger Projektabschluss und keine Publikationsfreigabe. Ein späterer Push, eine V3-Sanitisierung, eine Credential-Entscheidung, die Bereitstellung autoritativer Plattformassets sowie jede Serverinstallation benötigen jeweils einen eigenen, explizit abgegrenzten Folgeschritt.
