# AURELIA K1 Task-3-Korrekturdesign

```yaml
date: 2026-08-26
branch: codex/aurelia-konsolidierung
base_checkpoint: 095e0a074eba55719c373207e980388c927f2240
risk_route: B-critical-assurance
design_state: operator-authorized-local-draft
implementation_state: not_started
push_authorized: false
server_mutation: false
history_rewrite: false
```

## 1. Ziel

Task 3 wird ausschließlich so korrigiert, dass die drei bestätigten Findings
`K1-T3-P1-01`, `K1-T3-P1-02` und `K1-T3-Q-01` geschlossen werden. Der
Publikationsgraph-Scanner bleibt fail-closed, gibt keine Fundwerte aus und
behält seine bestehende CLI sowie die Exitsemantik `0 | 1 | 2` bei.

Dieses Dokument ist noch keine Implementierungs- oder Publikationsfreigabe.

## 2. Maßgebliche Verträge

- `docs/project-control/K1-STATUS.md`
- `docs/superpowers/plans/2026-08-25-aurelia-k1-canon-consolidation.md`,
  insbesondere Task 3
- `scripts/check-push-graph.mjs`
- `scripts/check-push-graph.test.mjs`
- `docs/project-control/QUALITY-ROUTING.md`

Bei einem Konflikt gelten die offene Findingbeschreibung in `K1-STATUS.md`
und der öffentliche Task-3-Vertrag des K1-Plans. Historische Scanneraggregate
bleiben historische Evidenz.

## 3. Erlaubter Änderungsscope

| Datei | Zulässige Änderung |
|---|---|
| `scripts/check-push-graph.test.mjs` | RED-/Regressionstests für exakt die drei Findings |
| `scripts/check-push-graph.mjs` | minimaler GREEN-Fix ohne neue externe Abhängigkeit |
| `docs/project-control/K1-STATUS.md` | aktueller Task-3-/Reviewstatus und eindeutige historische Kategorienotiz |

`package.json` wird nur geändert, falls ein bereits vorhandener Abnahmebefehl
nachweislich nicht ausführbar ist. Erwartet wird keine Änderung.

Nicht erlaubt sind Änderungen an V3-Evidenz, Analyse-`source/`-Ordnern,
Credentials, historischen Git-Objekten, Task-4-Dateien, Serverdateien oder
produktiven Daten.

## 4. Öffentlicher Scannervertrag

Die bestehenden Exporte und CLI-Argumente bleiben erhalten:

```typescript
export type GraphFinding = {
  category: string;
  blob: string;
  path: string;
  count: number;
};

export type GraphScan = {
  exitCode: 0 | 1 | 2;
  findings: GraphFinding[];
  diagnostics: string[];
};
```

Die kanonischen Kategorien nach der Korrektur sind:

- `absolute_user_path`
- `credential_like`
- `env_or_key_material`
- `internal_host`
- `local_analysis_root`
- `operational_identity`
- `raw_source_tree`
- `unc_path`
- `unscannable`

Jede CLI-Befundzeile enthält weiterhin ausschließlich `category`, `blob`,
`path` und `count`. Weder Fundinhalt noch Git-Stderr, Credentialwert oder
Diagnosedetail darf ausgegeben werden.

## 5. K1-T3-P1-01 — unquotierte Credential-Zuweisung

### Erforderliches Verhalten

Ein synthetischer Blob mit einer unquotierten Zuweisung der Form
`PREVIEW_CLIENT_SECRET=<synthetischer-wert>` wird als `credential_like`
erkannt, wenn der Wert dem bereits erlaubten Credential-Zeichensatz entspricht
und 16 bis 255 Zeichen lang ist.

Die Findingbeschreibung „aus Fragmenten zusammengesetzt“ bezeichnet die
sichere Konstruktion der Testfixture. Der Scanner erhält nach der
Fixturekonstruktion normalen Blobtext. Er soll weder JavaScript ausführen noch
allgemeine Stringverkettungen semantisch auswerten.

### Begrenzung gegen Fehlalarme

- Der Bezeichner muss eine bekannte Credentialbezeichnung wie
  `client_secret` enthalten; Groß-/Kleinschreibung bleibt irrelevant.
- Zwischen Bezeichner, Trennzeichen und Wert ist nur Whitespace zulässig.
- Erlaubte Trennzeichen bleiben `=` und `:`.
- Der unquotierte Wert endet an Dateiende, Whitespace oder einem syntaktischen
  Trenner; der Trenner gehört nicht zum Fund.
- Typdeklarationen, leere Werte, Platzhalter unter 16 Zeichen und bloße
  Bezeichner ohne Zuweisung bleiben ohne Befund.
- Bereits erkannte gequotete Zuweisungen bleiben regressionsfrei.

### RED-Vertrag

Der Test konstruiert Bezeichner und Wert aus harmlosen Fragmenten, ruft
`classifyBlob` auf und verlangt genau eine Kategorie `credential_like`. Er
prüft zusätzlich, dass weder der vollständige Wert noch die vollständige
Zuweisung in `JSON.stringify(findings)` vorkommt. Negative Fixtures sichern
Typdeklaration, zu kurzen Wert und fehlende Zuweisung ab.

## 6. K1-T3-P1-02 — `diagnostics: string[]`

Alle Rückgabepfade von `scanGraph` liefern für `diagnostics` ausschließlich
Strings:

```javascript
const headCommit = "a".repeat(40);
const diagnosticExamples = [
  { exitCode: 2, findings: [], diagnostics: ["invalid_request"] },
  {
    exitCode: 1,
    findings: [{ category: "unscannable", blob: headCommit, path: ".", count: 1 }],
    diagnostics: ["commit_limit"],
  },
  {
    exitCode: 1,
    findings: [{ category: "unscannable", blob: headCommit, path: ".", count: 1 }],
    diagnostics: ["path_limit"],
  },
];
```

Dies gilt für sämtliche Exit-2-Pfade sowie Commit- und Pfadlimit. Diagnosecodes
bleiben feste, nicht sensitive Kennungen. Referenzen, Pfade, Git-Stderr und
Eingabewerte werden nicht in Diagnosestrings interpoliert.

### RED-Vertrag

- Ungültige Anfrage: exaktes Array `['invalid_request']`.
- Unauflösbarer Commit: exaktes Array `['commit_unresolved']`.
- Nicht-Vorfahr: exaktes Array `['base_not_ancestor']`.
- Commitlimit: exaktes Array `['commit_limit']`.
- Pfadlimit: exaktes Array `['path_limit']`.
- Für jeden Fall gilt `diagnostics.every(value => typeof value === 'string')`.

Die Limitfälle werden über die bereits vorhandene `git`-Dependency-Injection
simuliert. Die öffentliche Scanner-API und die Produktionslimits werden dafür
nicht verändert.

## 7. K1-T3-Q-01 — kanonische Identitätskategorie

Die technische Scanner- und Testausgabe wird ohne Alias auf
`operational_identity` vereinheitlicht. Eine neue Mapping-Schicht ist nicht
erforderlich und würde unnötig zwei aktive Namen erhalten.

Historische Tabellen in `K1-STATUS.md`, die einen früher tatsächlich
beobachteten Schlüssel `pii_or_operational_identity` wiedergeben, werden nicht
rückwirkend umetikettiert. Sie erhalten beziehungsweise behalten eine
eindeutige Notiz, dass dies der historische technische Name der heute
kanonischen Kategorie `operational_identity` war. Neue Scanner- und
Abnahmeausgaben verwenden nur den kanonischen Namen.

### RED-Vertrag

- E-Mail-, Operator- und IP-Fixtures erwarten `operational_identity`.
- Keine aktive Testassertion erwartet `pii_or_operational_identity`.
- Harmlos typisierte Identitätsfelder bleiben ohne Befund.
- Der Scanner- und Testquelltext bleibt für seine eigenen Inhaltsregeln sauber.

## 8. TDD- und Implementierungsreihenfolge

1. Bestehende Scanner-Tests unverändert als grüne Baseline ausführen.
2. RED-Tests für P1-01 ergänzen und das erwartete Fehlschlagen nachweisen.
3. Minimalen unquotierten Credentialfall implementieren; gezielten Test grün
   machen.
4. RED-Tests für P1-02 ergänzen und das erwartete Fehlschlagen nachweisen.
5. Alle Diagnoseobjekte minimal durch feste Strings ersetzen; Tests grün
   machen.
6. Erwartungen für Q-01 auf `operational_identity` umstellen und RED
   nachweisen.
7. Scannerkategorie minimal umbenennen; gezielte und vollständige Tests grün
   machen.
8. `K1-STATUS.md` erst nach grüner Implementierung aktualisieren.

Die drei Fixes werden nicht mit Refactoring des Git-Enumerators, der
Pfadklassifikation oder der CLI-Argumentverarbeitung verbunden.

## 9. Abnahme

Mindestens folgende Befehle müssen frisch ausgeführt werden:

```powershell
node --test scripts/check-push-graph.test.mjs
npm run check:k1-control
git diff --check
git diff --cached --check
node scripts/check-push-graph.mjs --base origin/codex/aurelia-vorbereitung --head HEAD --mode full
```

Erwartungen:

- Scanner-Tests: Exit 0.
- K1-Control: Exit 0.
- Diffprüfungen: Exit 0.
- Realer Vollgraph-Scanner: weiterhin Exit 1, solange bekannte historische
  Befunde erreichbar sind.
- Neue Identitätsbefunde heißen ausschließlich `operational_identity`.
- Ausgabe enthält Kategorien, Blob-IDs, Repositorypfade und Counts, aber keine
  Fundwerte.
- Der Diff enthält ausschließlich die in Abschnitt 3 erlaubten Dateien.

## 10. Reviewrouting und Gate

Task 3 verwendet Spur B:

1. Implementierung mit Sol `high` und vollständiger TDD-Evidenz.
2. Fokussiertes Spec-Review ausschließlich gegen dieses Design, den Task-3-Diff
   und die Abnahmeausgaben.
3. Nur nach Spec-PASS ein separates Qualitäts-/Securityreview mit Sol `xHigh`
   oder gleichwertiger unabhängiger Prüfung.
4. Jeder externe Reviewoutput wird von der primären AURELIA-Instanz gegen Code
   und Tests nachverifiziert.
5. Task 4 bleibt bis zu beiden PASS-Entscheidungen blockiert.

Kein Review legitimiert Push, Serverzugriff oder eine Änderung der
Git-Historie.
