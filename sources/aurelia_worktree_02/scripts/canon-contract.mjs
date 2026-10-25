#!/usr/bin/env node
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import {
  CANONICAL_DECISION_LOCKS,
  DECISIONS,
} from "../src/lib/concept/decisions.ts";
import {
  C_GESETZT,
  U_GESETZT,
  X_KATALOG,
  X_STATUS,
} from "../src/lib/concept/freigabe.ts";
import { D08_D12_SUMMARIES } from "../src/lib/concept/id-legend.ts";
import { KOZYREV_OPTIONAL } from "../src/lib/concept/kozyrev-labor.ts";
import { OFFEN } from "../src/lib/concept/offen.ts";
import { HYBRID_ALTERNATIVEN } from "../src/lib/concept/standalone.ts";
import { WIEDERVORLAGE } from "../src/lib/concept/wiedervorlage.ts";

const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));
export const PROJECT_ROOT = resolve(SCRIPT_DIR, "..");

const EXPECTED_D_IDS = Object.freeze(
  Array.from(
    { length: 24 },
    (_, index) => `D${String(index + 1).padStart(2, "0")}`,
  ),
);

const EXPECTED_D_SUMMARY_IDS = Object.freeze([
  "D08",
  "D09",
  "D10",
  "D11",
  "D12",
]);

export const ACTIVE_TEXT_RULES = Object.freeze([
  {
    file: "src/lib/concept/decisions.ts",
    prohibited: [
      /WebRTC bleibt nachrangig/i,
      /\block:\s*"(?:gesetzt|empfohlen|zur-bestaetigung)"/,
    ],
    required: [
      /export const CANONICAL_DECISION_LOCKS/,
      /Kein Video zwischen Therapeut und Klient\. Kein WebRTC/i,
    ],
  },
  {
    file: "src/lib/concept/id-legend.ts",
    prohibited: [/export const D08_D12 =/, /warumEmpfohlen/],
    required: [/export const D08_D12_SUMMARIES/, /statusGrund/],
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
    prohibited: [/WebRTC nachrangig/i, /zur Bestätigung C08 \/ D05 \/ D15/i],
    required: [/D10.*kein Video.*kein WebRTC/i, /Gesetzt: C08, D05 und D15\./i],
  },
  {
    file: "docs/16-wellbeing.md",
    prohibited: [/zur Bestätigung C02 \/ D13/i],
    required: [/Gesetzt: C02 und D13\./i],
  },
  {
    file: "docs/18-clipboard.md",
    prohibited: [/D18, zur Bestätigung/i],
    required: [/D18, gesetzt/i],
  },
  {
    file: "docs/20-freigabe.md",
    prohibited: [
      /U09 kein Phase 1/i,
      /U11 D08–D12 empfohlen/i,
      /Empfohlen: D08–D12/i,
      /X bleibt Prüfungskatalog/i,
    ],
    required: [
      /U09 Phase 1 Gehäuse gestartet/i,
      /U11 D08\/D10\/D12 gesetzt\. D09 Preise und D11 Codecs Wiedervorlage\./i,
      /Gesetzt: D01–D08, D10, D12–D24\./i,
      /Empfohlen\/Wiedervorlage: D09 und D11\./i,
      /X-Katalog akzeptiert\./i,
    ],
  },
  {
    file: "docs/22-kozyrev-labor.md",
    prohibited: [/Lovable unberührt — Ihre offene Entscheidung\./i],
    required: [
      /Lovable unberührt — D03\/D24 gesetzt; Disconnect bleibt WV04 optional\./i,
    ],
  },
  {
    file: "docs/23-id-schema.md",
    prohibited: [/D08–D12 \(empfohlen/i, /Auth ist aus/i, /WebRTC optional/i],
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
    file: "src/routes/lovable.tsx",
    prohibited: [
      /Backup-SKU, optionales H4, X-Katalog, das Wort Phase 1, Heritage-Disconnect/i,
    ],
    required: [
      /Offen bleiben nur die Backup-SKU, das optionale H4 und der\s+Heritage-Disconnect \(WV04\)\./i,
      /X-Katalog akzeptiert; Phase 1 gestartet\./i,
    ],
  },
  {
    file: "src/routes/live.tsx",
    prohibited: [/Zur Bestätigung: C08, D05, D15/i],
    required: [/Gesetzt: C08, D05 und D15\./i],
  },
  {
    file: "src/routes/kozyrev.tsx",
    prohibited: [/Lovable entscheiden Sie noch/i, /X-Katalog bleibt Ihre Pause/i],
    required: [
      /D03 und D24 sind gesetzt/i,
      /Lovable bleibt Preview\/Heritage außerhalb der\s+AURELIA-Laufzeit/i,
      /X-Katalog ist akzeptiert/i,
      /K6–K8 sind gesperrt/i,
    ],
  },
  {
    file: "src/routes/roadmap.tsx",
    prohibited: [/Budget 3\/3\/12\/2/i, /Empfohlene Karten \(D08–D12\)/i],
    required: [/Budget 2\/16\/2/i, /D08, D10 und D12 sind gesetzt/i],
  },
  {
    file: "src/routes/entscheidungen.tsx",
    prohibited: [/D08–D12 empfohlen/i, /Warum noch empfohlen/i, /weil Auth noch aus ist/i],
    required: [/Status D08–D12/i, /Statusgrund/i],
  },
  {
    file: "src/routes/sicherheit.tsx",
    prohibited: [
      /Nachrichten Therapeut–Klient: MLS \(RFC 9420\).*Kein Video\./i,
    ],
    required: [/D10: kein Video, kein WebRTC und keine Aufnahme in AURELIA\./i],
  },
  {
    file: "src/routes/wellbeing.tsx",
    prohibited: [/Zur Bestätigung: C02, D13/i],
    required: [/Gesetzt: C02 und D13\./i],
  },
]);

function textAt(root, relativePath) {
  return readFileSync(resolve(root, relativePath), "utf8");
}

function patternMatches(pattern, text) {
  if (pattern.global || pattern.sticky) pattern.lastIndex = 0;
  const matches = pattern.test(text);
  if (pattern.global || pattern.sticky) pattern.lastIndex = 0;
  return matches;
}

export function decisionContractErrors(
  decisions = DECISIONS,
  canonicalLocks = CANONICAL_DECISION_LOCKS,
) {
  const errors = [];
  const ids = decisions.map((decision) => decision.id);
  const uniqueIds = [...new Set(ids)].sort();
  const canonicalIds = Object.keys(canonicalLocks).sort();
  if (decisions.length !== EXPECTED_D_IDS.length) {
    errors.push(
      `D-count differs: expected ${EXPECTED_D_IDS.length}; got ${decisions.length}`,
    );
  }
  if (uniqueIds.length !== ids.length) {
    errors.push("D-IDs must be unique");
  }
  if (JSON.stringify(uniqueIds) !== JSON.stringify(EXPECTED_D_IDS)) {
    errors.push(
      `D-ID set differs: expected ${EXPECTED_D_IDS.join(", ")}; got ${uniqueIds.join(", ")}`,
    );
  }
  if (JSON.stringify(canonicalIds) !== JSON.stringify(EXPECTED_D_IDS)) {
    errors.push(
      `Canonical D-ID set differs: expected ${EXPECTED_D_IDS.join(", ")}; got ${canonicalIds.join(", ")}`,
    );
  }
  for (const decision of decisions) {
    if (!Object.hasOwn(canonicalLocks, decision.id)) {
      errors.push(`${decision.id}: missing canonical lock`);
    } else if (decision.lock !== canonicalLocks[decision.id]) {
      errors.push(
        `${decision.id}: expected ${canonicalLocks[decision.id]}; got ${String(decision.lock)}`,
      );
    }
    if (decision.lock !== "gesetzt" && decision.lock !== "empfohlen") {
      errors.push(
        `${decision.id}: active canon cannot remain ${String(decision.lock)}`,
      );
    }
  }
  return errors;
}

export function activeTextErrors(root = PROJECT_ROOT, rules = ACTIVE_TEXT_RULES) {
  const errors = [];
  for (const rule of rules) {
    const text = textAt(root, rule.file);
    for (const pattern of rule.prohibited) {
      if (patternMatches(pattern, text)) {
        errors.push(`${rule.file}: prohibited ${pattern}`);
      }
    }
    for (const pattern of rule.required) {
      if (!patternMatches(pattern, text)) {
        errors.push(`${rule.file}: missing ${pattern}`);
      }
    }
  }
  return errors;
}

export function decisionSummaryErrors(summaries = D08_D12_SUMMARIES) {
  const errors = [];
  const ids = summaries.map((summary) => summary.id);
  const uniqueIds = [...new Set(ids)].sort();

  if (summaries.length !== EXPECTED_D_SUMMARY_IDS.length) {
    errors.push(
      `D-summary count differs: expected ${EXPECTED_D_SUMMARY_IDS.length}; got ${summaries.length}`,
    );
  }
  if (uniqueIds.length !== ids.length) {
    errors.push("D-summary IDs must be unique");
  }
  if (JSON.stringify(uniqueIds) !== JSON.stringify(EXPECTED_D_SUMMARY_IDS)) {
    errors.push(
      `D-summary ID set differs: expected ${EXPECTED_D_SUMMARY_IDS.join(", ")}; got ${uniqueIds.join(", ")}`,
    );
  }

  for (const summary of summaries) {
    for (const field of ["titel", "kern", "statusGrund"]) {
      if (typeof summary[field] !== "string" || summary[field].trim() === "") {
        errors.push(`${summary.id}: ${field} must be a non-empty string`);
      }
    }
    if (Object.hasOwn(summary, "lock")) {
      errors.push(`${summary.id}: summary must not own lock`);
    }
  }

  return errors;
}

function expectedIDs(prefix, count, width) {
  return Array.from(
    { length: count },
    (_, index) => `${prefix}${String(index + 1).padStart(width, "0")}`,
  );
}

function idSetErrors(family, rows, expected) {
  const errors = [];
  const ids = rows.map((row) => row.id);
  const uniqueIds = [...new Set(ids)].sort();
  const expectedSorted = [...expected].sort();
  if (rows.length !== expected.length) {
    errors.push(
      `${family}-count differs: expected ${expected.length}; got ${rows.length}`,
    );
  }
  if (uniqueIds.length !== ids.length) {
    errors.push(`${family}-IDs must be unique`);
  }
  if (JSON.stringify(uniqueIds) !== JSON.stringify(expectedSorted)) {
    errors.push(
      `${family}-ID set differs: expected ${expectedSorted.join(", ")}; got ${uniqueIds.join(", ")}`,
    );
  }
  return errors;
}

export function idFamilyContractErrors({
  cGesetzt = C_GESETZT,
  xKatalog = X_KATALOG,
  xStatus = X_STATUS,
  uGesetzt = U_GESETZT,
  kozyrevOptional = KOZYREV_OPTIONAL,
  hybridAlternativen = HYBRID_ALTERNATIVEN,
  offen = OFFEN,
  wiedervorlage = WIEDERVORLAGE,
} = {}) {
  const errors = [
    ...idSetErrors("C", cGesetzt, expectedIDs("C", 12, 2)),
    ...idSetErrors("X", xKatalog, expectedIDs("X", 20, 2)),
    ...idSetErrors("U", uGesetzt, expectedIDs("U", 12, 2)),
    ...idSetErrors("K", kozyrevOptional, expectedIDs("K", 8, 1)),
    ...idSetErrors("H", hybridAlternativen, expectedIDs("H", 8, 1)),
    ...idSetErrors("O", offen, expectedIDs("O", 10, 2)),
    ...idSetErrors("WV", wiedervorlage, expectedIDs("WV", 6, 2)),
  ];

  if (xStatus.stand !== "akzeptiert") {
    errors.push(`X-status must be akzeptiert; got ${String(xStatus.stand)}`);
  }
  for (const row of xKatalog) {
    if (
      row.kategorie !== "nicht umsetzbar" &&
      row.kategorie !== "nicht relevant"
    ) {
      errors.push(`${row.id}: invalid X category ${String(row.kategorie)}`);
    }
  }
  for (const row of kozyrevOptional) {
    if (row.lock !== "gesetzt" && row.lock !== "gesperrt") {
      errors.push(`${row.id}: invalid K lock ${String(row.lock)}`);
    }
  }
  for (const row of hybridAlternativen) {
    if (
      row.lock !== "gesetzt" &&
      row.lock !== "optional" &&
      row.lock !== "gesperrt"
    ) {
      errors.push(`${row.id}: invalid H lock ${String(row.lock)}`);
    }
  }
  for (const row of offen) {
    if (
      row.lage !== "gesetzt" &&
      row.lage !== "Entscheidung später" &&
      row.lage !== "Optional — Default: nein" &&
      row.lage !== "Keine Entscheidung — Empfehlung gilt"
    ) {
      errors.push(`${row.id}: invalid O lage ${String(row.lage)}`);
    }
  }

  return errors;
}

export function canonErrors(root = PROJECT_ROOT) {
  return [
    ...decisionContractErrors(),
    ...decisionSummaryErrors(),
    ...idFamilyContractErrors(),
    ...activeTextErrors(root),
  ];
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
