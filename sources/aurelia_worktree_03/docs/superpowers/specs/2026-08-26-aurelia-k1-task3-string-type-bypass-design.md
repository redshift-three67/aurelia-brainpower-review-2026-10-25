# AURELIA K1 Task-3 String/Type-Bypass Sicherheitsdesign

```yaml
date: 2026-08-26
branch: codex/aurelia-konsolidierung
source_checkpoint: e930aab2643c376ddd9090a66be31c52d32f05ee
finding: K1-T3-P1-01-STRING-TYPE-BYPASS
risk_route: B-critical-assurance
decision: candidate-scoped-typescript-ast-adjudication
design_state: operator-approved-local-document
implementation_state: not_started
data_class: synthetic-only
push_authorized: false
server_mutation: false
history_rewrite: false
```

## 1. Zweck und Geltung

Dieses Design schließt ausschließlich den nach `e930aab` verbliebenen
String/Type-Bypass des fail-closed Publikationsgraph-Scanners. Es präzisiert
Abschnitt 5 des
[`2026-08-26-aurelia-k1-task3-correction-design.md`](2026-08-26-aurelia-k1-task3-correction-design.md),
soweit dort echte TypeScript-Property-Signaturen von unquotierten
Credential-Zuweisungen abgegrenzt werden.

Bei einem Konflikt über diese Abgrenzung gilt dieses Dokument. Die bereits
grünen Verträge für `diagnostics: string[]`, `operational_identity`, CLI,
Exitcodes und Git-Enumeration bleiben unverändert.

Das Dokument erteilt keine Implementierungs-, Commit-, Push-, Server- oder
History-Freigabe.

## 2. Bestätigte Ursache

Der Stand `e930aab` verändert vor der Credential-Suche rohe `.ts`- und
`.tsx`-Textblöcke anhand von regulären Ausdrücken. Die Transformation kann
nicht beweisen, dass ein textuell wie `type` oder `interface` aussehender
Bereich tatsächlich TypeScript-Syntax ist. Dadurch wird auch
credential-artiger Text innerhalb von String- und Kommentarinhalten entfernt.

Die folgende aus synthetischen Fragmenten konstruierte Form reproduziert den
Fehler deterministisch:

```javascript
const name = ["PREVIEW", "CLIENT", "SECRET"].join("_");
const value = ["Synthetic", "Scanner", "Credential", "Value"].join("");
const fakeType = `type Config = { ${name}: ${value}; }`;
const source = `const sample = ${JSON.stringify(fakeType)};`;
```

`classifyBlob("src/string.ts", Buffer.from(source))` liefert auf `e930aab`
keinen Befund. Erwartet wird genau ein `credential_like`-Befund ohne Ausgabe
von `value`, `source` oder der vollständigen Zuweisung.

Die Ursache ist nicht die Credential-Regel selbst, sondern eine zu breite
Vorverarbeitung: Ein vollständiger Textbereich wird entfernt, obwohl nur ein
einzelner Kandidat als harmlose TypeScript-Property-Signatur bewiesen werden
müsste.

## 3. Bewertete Ansätze und Entscheidung

| Ansatz | Sicherheitsbewertung | Entscheidung |
|---|---|---|
| Eigener JS-/TS-Lexer mit Signaturautomat | Dependency-frei, aber Strings, Kommentare, Templates, Regex-Literale, TSX und Recovery müssten als eigene Security-Grammatik korrekt implementiert werden. | verworfen |
| Zeilen- oder Positionsfilter | Für mehrzeilige, verschachtelte und generische Syntax nicht ausreichend; optimistische Regeln öffnen Bypässe. | verworfen |
| Kandidatenbezogene TypeScript-AST-Prüfung | Trennt Property-Signaturen syntaktisch von Strings, Kommentaren und Laufzeitkontexten; jeder Fehler kann konservativ auf den Rohscan zurückfallen. | **verbindlich gewählt** |

TypeScript ist bereits direkte Dev-Abhängigkeit des Repositorys. Diese
Entscheidung fügt keine Abhängigkeit hinzu und ändert weder `package.json` noch
`package-lock.json`.

## 4. Erlaubter späterer Implementierungsscope

Die isolierte Korrektur darf ausschließlich diese Dateien verändern:

| Datei | Erlaubte Änderung |
|---|---|
| `scripts/check-push-graph.test.mjs` | RED-/Grenz-/Regressionstests für den String/Type-Bypass |
| `scripts/check-push-graph.mjs` | kandidatenbezogene AST-Adjudikation und Entfernung der unsicheren Blockmaskierung |

Eine spätere Statusfortschreibung in
`docs/project-control/K1-STATUS.md` ist eine getrennte Aktion. Sie ist erst
nach grüner Implementierung und den vorgeschriebenen Reviews zulässig.

Nicht erlaubt sind Änderungen an Abhängigkeiten, Paketdateien, V3-Evidenz,
Analyse-`source/`-Ordnern, Credentials, Git-Objekten, Task-4-Dateien,
Produktcode oder Serverdateien.

## 5. Unveränderte öffentliche Verträge

Die vorhandenen Exporte und die synchrone API bleiben erhalten:

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

- `classifyBlob` bleibt synchron.
- `classifyPath`, `scanGraph` und `runCli` behalten Signaturen und Verhalten.
- CLI-Argumente und Exitsemantik bleiben `0 | 1 | 2`.
- Jede CLI-Befundzeile enthält nur `category`, `blob`, `path` und `count`.
- Parserfehler, Parserdiagnosen, Quelltext und Fundwerte werden nicht
  ausgegeben.
- Die Blobgrenze bleibt 1 MiB. Größere, binäre oder ungültig UTF-8-dekodierbare
  Blobs bleiben `unscannable`.

## 6. Verbindliche Verarbeitungspipeline

### 6.1 Rohtext bleibt maßgeblich

Der Scanner sucht alle Credential-Muster im unveränderten dekodierten Text.
Die bisherige Funktion, die vollständige TypeScript-Type-Blöcke aus dem Text
entfernt, wird vollständig entfernt.

Token-, Private-Key-, JWT- und alle anderen unabhängigen Credential-Muster
werden niemals durch TypeScript-Syntax beeinflusst.

### 6.2 Benannte Zuweisungen werden zu Kandidaten

Nur das Muster für benannte Zuweisungen wie `client_secret`, `access_token`
oder `password` wird einzeln iteriert. Jeder Treffer erzeugt ausschließlich
intern einen Kandidaten mit UTF-16-Positionen:

```typescript
type NamedCredentialCandidate = {
  matchStart: number;
  matchEnd: number;
  nameStart: number;
  nameEnd: number;
  separator: "=" | ":";
  valueStart: number;
  valueEnd: number;
  quoted: boolean;
};
```

Der vollständige Bezeichner wird erfasst. Bei
`PREVIEW_CLIENT_SECRET` darf nicht nur die Teilzeichenfolge `CLIENT_SECRET`
als Name gelten. Regex- und AST-Positionen beziehen sich auf denselben
JavaScript-String und damit auf UTF-16-Code-Units.

Die Positionsbestimmung verwendet Match-Indizes des Node-22-RegExp-Flags
`d`. Es werden keine Fundwerte in Findings oder Diagnostics übernommen.

### 6.3 Parser wird nur bei Bedarf geladen

Da `classifyBlob` synchron bleibt, wird TypeScript nicht per asynchronem
`import()` geladen. Die Implementierung verwendet `createRequire` aus
`node:module` und lädt `typescript` nur, wenn alle Bedingungen erfüllt sind:

1. Repositorypfad endet auf `.ts` oder `.tsx`;
2. mindestens ein benannter Credential-Kandidat ist vorhanden;
3. mindestens ein Kandidat ist ungequotiert und verwendet `:`.

Der erfolgreiche oder fehlgeschlagene Ladevorgang darf pro Prozess gecacht
werden. Ein Ladefehler erzeugt keine Ausgabe und keine Ausnahme nach außen;
er erlaubt lediglich keine Unterdrückung.

### 6.4 Ein Parse pro relevantem Blob

Der Parser verwendet:

- `ScriptTarget.Latest`;
- `ScriptKind.TS` für `.ts`;
- `ScriptKind.TSX` für `.tsx`;
- `setParentNodes: true`, damit der direkte Parent geprüft werden kann.

Bei Parserexception, fehlender API, nichtleeren `parseDiagnostics` oder
ungültigen Positionsbeziehungen ist die Menge sicherer
Unterdrückungskandidaten leer. Der Rohscan bleibt dann vollständig wirksam.

## 7. Enger AST-Unterdrückungsnachweis

Ein benannter Kandidat darf genau dann nicht als `credential_like` gezählt
werden, wenn **alle** folgenden Bedingungen bewiesen sind:

1. Pfad ist `.ts` oder `.tsx`.
2. Kandidat ist ungequotiert.
3. Kandidat verwendet exakt `:`; `=` wird niemals unterdrückt.
4. Der Parserlauf war fehlerfrei und besitzt keine Parse-Diagnostics.
5. Der AST-Knoten ist `PropertySignature`.
6. Der direkte Parent ist `InterfaceDeclaration` oder `TypeLiteralNode`.
7. `node.name` ist ein ungequoteter `Identifier`.
8. `node.name.getStart(sourceFile)` und `node.name.end` stimmen exakt mit
   `nameStart` und `nameEnd` des Kandidaten überein.
9. Zwischen Name, optionalem `?`, Doppelpunkt und Type-Start liegt nur die
   syntaktisch erwartete Property-Signature-Struktur.
10. `valueStart` stimmt exakt mit `node.type.getStart(sourceFile)` überein.
11. Der gematchte Wert endet exakt am Ende eines einfachen
    Type-Reference-Pfads. Erlaubt sind ein Identifier oder ein QualifiedName
    wie `Namespace.Type`.
12. Zwischen `node.type.end` und Memberende stehen nur Trivia und genau ein
    Semikolon.
13. Es existiert kein Initializer, kein `=`, kein Ausdruck und kein
    Parser-Recovery-Rest.

Die Allowlist ist absichtlich enger als die vollständige TypeScript-Grammatik.
Generics, Arrays, Unions, Intersections, Conditional Types, Literaltypen,
Mapped Types und verschachtelte Type-Literale werden nur dann nicht als
Credential-Kandidat sichtbar, wenn das Credential-RegExp gar keinen
abgeschlossenen Wertkandidaten erzeugt. Sie erhalten keine breitere
AST-Ausnahme. Ambiguität führt zu einem sichtbaren, fail-closed Kandidaten.

Optionales `?` an einer echten Property-Signatur ist zulässig. Wenn das
Credential-RegExp wegen `?` keinen Zuweisungskandidaten erzeugt, ist keine
Unterdrückung erforderlich.

## 8. Fail-closed Invarianten

1. Es wird nie Quelltext entfernt oder maskiert.
2. Unterdrückt wird höchstens ein konkreter benannter Kandidat.
3. Strings, Kommentare und Template-Inhalte bleiben immer scanbarer Rohtext.
4. Ein AST-Knoten darf nur den positionsgleichen Kandidaten beeinflussen.
5. Objektliterale, Klassenfelder, Parameter, Labels und sonstige
   Laufzeitkontexte erhalten keine Type-Ausnahme.
6. Gequotete Werte und `=`-Zuweisungen werden niemals unterdrückt.
7. Parser- oder Loaderfehler reduzieren die Fundmenge nicht.
8. Unbekannte oder nicht eindeutig unterstützte TypeScript-Syntax reduziert
   die Fundmenge nicht.
9. Die Anzahl der ausgegebenen Findings beruht ausschließlich auf nicht
   unterdrückten Rohtexttreffern.
10. Weder Kandidateninhalte noch AST-Texte verlassen `classifyBlob`.

False Positives bei nicht eindeutig bewiesenen Type-Konstrukten sind eine
bewusste Sicherheitsentscheidung. Ein False Negative durch Parser-Recovery,
Textmaskierung oder mehrdeutige Positionen ist unzulässig.

## 9. Fehlerbehandlung

| Fehler | Verhalten |
|---|---|
| `typescript` nicht ladbar oder inkompatibel | keine Unterdrückung; Rohscan |
| `createSourceFile` wirft | keine Unterdrückung; Rohscan |
| `parseDiagnostics` nicht leer oder nicht lesbar | keine Unterdrückung; Rohscan |
| AST-Wanderung wirft oder liefert ungültige Positionen | keine Unterdrückung; Rohscan |
| Kandidat kann keinem eindeutigen Property-Knoten zugeordnet werden | Kandidat bleibt Finding |
| Kandidaten überschneiden sich oder Indizes sind inkonsistent | betroffene Kandidaten bleiben Findings |

Der Scanner fügt für diese internen Fälle keine neuen Diagnosecodes hinzu.
Die vorhandene CLI gibt weiterhin nur sichere Befundfelder aus.

## 10. TDD-Abdeckungsmatrix

Alle Credentialnamen und synthetischen Werte werden in Tests aus harmlosen
Fragmenten zusammengesetzt, damit Scanner- und Testquelle ihre eigene
Inhaltsprüfung weiterhin bestehen.

| Testgruppe | Verbindliche Erwartung |
|---|---|
| Double-, Single- und Template-String mit Fake-`type`/`interface` | je genau ein `credential_like` |
| Strings mit escaped Quote, Backslash, Backtick oder `${...}` | Kandidat bleibt sichtbar |
| Zeilen- und Blockkommentar mit Fake-Type | Kandidat bleibt sichtbar |
| Einfache echte `type`- und `interface`-Property-Signatur | kein Finding |
| Optionales Property `?` | kein Kandidat oder eindeutig keine Fehlklassifikation |
| Identifier- und QualifiedName-Type-Reference | kein Finding bei exakter Positionsgleichheit |
| Generic, Array, Union, Intersection, Literal- und verschachtelter Typ | keine breite Ausnahme; Ambiguität bleibt fail-closed |
| Objektliteral mit Doppelpunkt | Finding |
| Equals-Zuweisung | Finding |
| Klassenfeld, Parameter und Label | Finding, sofern das Rohmuster einen Kandidaten erzeugt |
| String-Fake-Type plus echte Signatur im selben Blob | genau ein Finding |
| Echte Signatur plus Laufzeitzuweisung in derselben Zeile | genau ein Finding |
| Identischer Text in `.js`, `.mjs`, `.mts`, `.cts` und `.txt` | Finding; keine AST-Ausnahme |
| Malforme TS-Syntax oder Parser-Diagnostics | Kandidat bleibt Finding |
| Mehrere Kandidaten, CRLF, Unicode-Präfix, BOL und EOF | korrekte Counts und Positionszuordnung |
| Gequotierte und unquotierte `:`-/`=`-Werte | bestehende Erkennung regressionsfrei |
| Exakt 1 MiB und 1 MiB plus 1 Byte | normaler Scan beziehungsweise `unscannable` |
| Alle positiven Fälle | kein Wert und keine vollständige Zuweisung in serialisierten Findings |
| Scanner- und Testquelldatei | weiterhin selbstscan-sauber |

## 11. Performancegrenzen

- Vor jedem Parseraufruf gilt weiterhin die 1-MiB-Blobgrenze.
- TypeScript wird nur für `.ts`/`.tsx` mit relevantem ungequotiertem
  Doppelpunktkandidaten geladen.
- Pro relevantem Blob ist höchstens ein Parse und ein iterativer AST-Durchlauf
  erlaubt.
- Der vorhandene Blobcache von `scanGraph` verhindert Wiederholung pro
  Git-Blob.
- Es entstehen keine neuen Subprozesse, Netzwerkzugriffe oder Datei-I/O-Pfade.
- Zielkomplexität ist `O(n + c + a)` für Textlänge `n`, Kandidatenzahl `c` und
  besuchte AST-Knoten `a`.
- Kandidaten werden für die AST-Zuordnung nach `nameStart` indiziert; eine
  unbeschränkte Kandidat-mal-Knoten-Suche ist nicht zulässig.

## 12. Abnahmevertrag

Mindestens folgende Befehle sind nach einer später freigegebenen
Implementierung frisch auszuführen:

```powershell
node --test scripts/check-push-graph.test.mjs
npm run check:k1-control
git diff --check
git diff --cached --check
node scripts/check-push-graph.mjs --base origin/codex/aurelia-vorbereitung --head HEAD --mode full
```

Zusätzlich sind nachzuweisen:

- fokussierter RED-Lauf reproduziert den String/Type-Bypass auf `e930aab`;
- fokussierter GREEN-Lauf schließt ihn ohne Verlust echter
  Property-Signatur-Negativfälle;
- vollständige Scanner-Suite ist grün;
- der reale Vollgraph bleibt wegen erreichbarer historischer Befunde Exit 1;
- alle CLI-Zeilen besitzen ausschließlich sichere Felder;
- Implementierungsdiff umfasst ausschließlich Scanner und Scanner-Test;
- `package.json` und `package-lock.json` sind unverändert;
- Worktree und Index bestehen ihre eigenen Diffprüfungen.

## 13. Review- und Stoppregeln

Die Korrektur bleibt Spur B:

1. Implementierung mit Sol `high` und vollständiger RED/GREEN-Evidenz.
2. Fokussiertes Spec-Review gegen dieses Design, den Zwei-Dateien-Diff und
   frische Abnahmeausgaben.
3. Nur nach Spec-PASS folgt ein unabhängiges Quality/Security-Review mit Sol
   `xHigh`.
4. Die primäre AURELIA-Instanz reproduziert jedes P0-P2-Finding.
5. Eine normale Korrekturschleife ist zulässig. Ein danach verbleibender oder
   systemischer P0-P2-Befund stoppt erneut zur Konsolidierung.
6. Task 4 bleibt bis zu explizitem Spec-PASS und Quality-PASS gesperrt.

Kein Review autorisiert Push, Serverzugriff, History-Rewrite oder eine
Erweiterung des Dateiscopes.

## 14. Nichtziele

- kein Typechecker und keine semantische Codeausführung;
- kein allgemeiner JavaScript-/TypeScript-Parserersatz;
- keine Stringverkettungs-, Entropie- oder Secretwertauswertung;
- keine Erweiterung des Credential-Zeichensatzes;
- keine AST-Ausnahme für JavaScript, `.mts` oder `.cts`;
- keine Änderung anderer Scannerkategorien;
- keine Änderung des Git-Enumerators oder der Limitlogik;
- keine neue Dependency oder Paketmutation;
- keine Task-4-, Server- oder Produktimplementierung.

## 15. Bekannte Restrisiken

- Der vorhandene TypeScript-Parser wird Teil des vertrauensrelevanten
  Unterdrückungspfads. Die enge Allowlist und der Rohscan-Fallback begrenzen
  dieses Risiko.
- TypeScript-Upgrades können AST-Grenzen verändern. Die Positions- und
  Syntaxmatrix muss bei jedem Lockfile-Upgrade erneut laufen.
- Gültige, aber nicht erlaubte komplexe Property-Typen können fail-closed
  blockieren. Dies ist akzeptabel und sicherer als eine breite Ausnahme.
- Parser-Recovery darf niemals als sicher gelten; nichtleere oder unklare
  Diagnostics verhindern jede Unterdrückung.

## 16. Abschlussbedingung

Dieses Design ist erfüllt, wenn der reproduzierte String/Type-Bypass per TDD
geschlossen ist, echte eng definierte Property-Signaturen ohne Fehlbefund
bleiben, alle Ambiguitäten auf den Rohscan zurückfallen, beide Reviewstufen
PASS sind und weder Push noch Server-, History- oder Task-4-Aktion erfolgt ist.
