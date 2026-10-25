import assert from "node:assert/strict";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { test } from "node:test";
import * as canonContract from "./canon-contract.mjs";
import {
  ACTIVE_TEXT_RULES,
  activeTextErrors,
  canonErrors,
  decisionContractErrors,
  decisionSummaryErrors,
} from "./canon-contract.mjs";

test("the ID-family contract validator is exported", () => {
  assert.equal(typeof canonContract.idFamilyContractErrors, "function");
});

function numberedRows(prefix, count, width, extra = {}) {
  return Array.from({ length: count }, (_, index) => ({
    id: `${prefix}${String(index + 1).padStart(width, "0")}`,
    ...extra,
  }));
}

function validIDFamilies() {
  return {
    cGesetzt: numberedRows("C", 12, 2),
    xKatalog: numberedRows("X", 20, 2, { kategorie: "nicht relevant" }),
    xStatus: { stand: "akzeptiert" },
    uGesetzt: numberedRows("U", 12, 2),
    kozyrevOptional: numberedRows("K", 8, 1, { lock: "gesetzt" }),
    hybridAlternativen: numberedRows("H", 8, 1, { lock: "optional" }),
    offen: numberedRows("O", 10, 2, { lage: "gesetzt" }),
    wiedervorlage: numberedRows("WV", 6, 2),
  };
}

test("ID families reject duplicate and missing IDs", () => {
  const families = validIDFamilies();
  families.cGesetzt[11] = { id: "C11" };
  families.xKatalog.pop();
  families.uGesetzt[11] = { id: "U11" };
  families.kozyrevOptional.pop();
  families.hybridAlternativen[7] = { id: "H7", lock: "optional" };
  families.offen.pop();
  families.wiedervorlage[5] = { id: "WV05" };

  const errors = canonContract.idFamilyContractErrors(families);
  for (const family of ["C", "U", "H", "WV"]) {
    assert.ok(errors.includes(`${family}-IDs must be unique`));
  }
  for (const family of ["C", "X", "U", "K", "H", "O", "WV"]) {
    assert.ok(
      errors.some((error) => error.startsWith(`${family}-ID set differs:`)),
      `${family} must reject a missing ID`,
    );
  }
});

test("ID families reject invalid X, K, H, and O status values", () => {
  const families = validIDFamilies();
  families.xStatus = { stand: "Prüfungskatalog" };
  families.xKatalog[0] = { id: "X01", kategorie: "unklar" };
  families.kozyrevOptional[0] = { id: "K1", lock: "optional" };
  families.hybridAlternativen[0] = { id: "H1", lock: "empfohlen" };
  families.offen[0] = { id: "O01", lage: "zur-bestaetigung" };

  const errors = canonContract.idFamilyContractErrors(families);
  assert.ok(errors.includes("X-status must be akzeptiert; got Prüfungskatalog"));
  assert.ok(errors.includes("X01: invalid X category unklar"));
  assert.ok(errors.includes("K1: invalid K lock optional"));
  assert.ok(errors.includes("H1: invalid H lock empfohlen"));
  assert.ok(errors.includes("O01: invalid O lage zur-bestaetigung"));
});

test("the real repository has one consistent active canon", () => {
  const newlyCoveredSources = [
    "docs/15-live.md",
    "docs/16-wellbeing.md",
    "docs/18-clipboard.md",
    "docs/20-freigabe.md",
    "docs/22-kozyrev-labor.md",
    "src/routes/kozyrev.tsx",
    "src/routes/live.tsx",
    "src/routes/lovable.tsx",
    "src/routes/wellbeing.tsx",
  ];
  const coveredSources = new Set(ACTIVE_TEXT_RULES.map((rule) => rule.file));
  for (const source of newlyCoveredSources) {
    assert.ok(coveredSources.has(source), `${source} must be covered`);
  }
  assert.deepEqual(canonErrors(), []);
});

test("duplicate or incomplete decision IDs fail closed", () => {
  const decisions = Array.from({ length: 24 }, (_, index) => ({
    id: index === 23 ? "D23" : `D${String(index + 1).padStart(2, "0")}`,
    lock: "gesetzt",
  }));
  const errors = decisionContractErrors(decisions);
  assert.ok(errors.includes("D-IDs must be unique"));
  assert.ok(errors.some((error) => error.includes("D-ID set differs")));
});

test("decision locks derive exclusively from the canonical map", () => {
  const ids = Array.from(
    { length: 24 },
    (_, index) => `D${String(index + 1).padStart(2, "0")}`,
  );
  const decisions = ids.map((id) => ({ id, lock: "gesetzt" }));
  const canonicalLocks = Object.fromEntries(ids.map((id) => [id, "gesetzt"]));

  const missing = { ...canonicalLocks };
  delete missing.D24;
  assert.ok(
    decisionContractErrors(decisions, missing).includes(
      "D24: missing canonical lock",
    ),
  );

  assert.ok(
    decisionContractErrors(decisions, {
      ...canonicalLocks,
      D01: "empfohlen",
    }).includes("D01: expected empfohlen; got gesetzt"),
  );

  const unsettledDecisions = decisions.map((decision) =>
    decision.id === "D01"
      ? { ...decision, lock: "zur-bestaetigung" }
      : decision,
  );
  assert.ok(
    decisionContractErrors(unsettledDecisions, {
      ...canonicalLocks,
      D01: "zur-bestaetigung",
    }).includes("D01: active canon cannot remain zur-bestaetigung"),
  );

  assert.ok(
    decisionContractErrors(decisions, {
      ...canonicalLocks,
      D25: "gesetzt",
    }).some((error) => error.startsWith("Canonical D-ID set differs:")),
  );
});

test("canonical concept sources contain no stale active wording", () => {
  const conceptFiles = new Set([
    "src/lib/concept/decisions.ts",
    "src/lib/concept/nav.ts",
    "src/lib/concept/standalone.ts",
  ]);
  const conceptRules = ACTIVE_TEXT_RULES.filter((rule) =>
    conceptFiles.has(rule.file),
  );
  assert.deepEqual(activeTextErrors(undefined, conceptRules), []);
});

test("stale active wording is reported exactly with its file", () => {
  const root = mkdtempSync(join(tmpdir(), "aurelia-canon-"));
  const rules = [
    {
      file: "docs/02-architecture.md",
      prohibited: [/später optional WebRTC/i],
      required: [/WebSocket-Fachkanal.*kein WebRTC/i],
    },
  ];
  try {
    const rule = rules[0];
    const target = join(root, rule.file);
    mkdirSync(dirname(target), { recursive: true });
    writeFileSync(target, "Realtime | WebSocket-Fachkanal; kein WebRTC");
    assert.deepEqual(activeTextErrors(root, rules), []);

    writeFileSync(
      target,
      "Realtime | WebSocket-Fachkanal; kein WebRTC\nspäter optional WebRTC",
    );
    assert.deepEqual(activeTextErrors(root, rules), [
      "docs/02-architecture.md: prohibited /später optional WebRTC/i",
    ]);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test("regex checks are deterministic across repeated scans", () => {
  const root = mkdtempSync(join(tmpdir(), "aurelia-canon-regex-"));
  const rules = [
    {
      file: "docs/02-architecture.md",
      prohibited: [/später optional WebRTC/gi],
      required: [/WebSocket-Fachkanal.*kein WebRTC/gi],
    },
  ];
  try {
    const target = join(root, rules[0].file);
    mkdirSync(dirname(target), { recursive: true });
    writeFileSync(target, "Realtime | WebSocket-Fachkanal; kein WebRTC");
    assert.deepEqual(activeTextErrors(root, rules), []);
    assert.deepEqual(activeTextErrors(root, rules), []);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test("D08-D12 summaries are complete, unique, and lock-free", () => {
  assert.deepEqual(decisionSummaryErrors(), []);
  const invalid = [
    { id: "D08", titel: "A", kern: "A", statusGrund: "A", lock: "gesetzt" },
    { id: "D09", titel: "B", kern: "B", statusGrund: "B" },
    { id: "D10", titel: "C", kern: "C", statusGrund: "C" },
    { id: "D11", titel: "D", kern: "D", statusGrund: "D" },
    { id: "D11", titel: "E", kern: "E", statusGrund: "" },
  ];
  const errors = decisionSummaryErrors(invalid);
  assert.ok(errors.includes("D08: summary must not own lock"));
  assert.ok(errors.includes("D-summary IDs must be unique"));
  assert.ok(errors.some((error) => error.startsWith("D-summary ID set differs:")));
  assert.ok(errors.includes("D11: statusGrund must be a non-empty string"));
});
