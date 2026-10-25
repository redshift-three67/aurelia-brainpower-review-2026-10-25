# AURELIA K1 Task-3 Overlap-Enumeration Korrekturdesign

```yaml
date: 2026-08-26
amended: 2026-08-28
amendment_trigger: quality-review K1-T3-Q-NEW-01, K1-T3-Q-NEW-02, K1-T3-Q-NEW-03 (E4)
amendment_decision: operator option B — findings folded into this rebuild
branch: codex/aurelia-konsolidierung
source_checkpoint: 73ea21ce8031714174d2b7cc922478a1dc0103af
finding_parent: K1-T3-P1-01-STRING-TYPE-BYPASS
findings:
  - CRED-NAME-LEADING-GRAMMAR
  - CRED-CANDIDATE-OVERLAP
  - K1-T3-Q-NEW-01
  - K1-T3-Q-NEW-02
  - K1-T3-Q-NEW-03
risk_route: B-critical-assurance
decision: maximal-head-enumeration-with-bounded-value-parser
design_state: local-correction-document-amended-2026-08-28
implementation_state: stopped-after-spec-fail
data_class: synthetic-only
push_authorized: false
server_mutation: false
history_rewrite: false
```

## 1. Zweck, Rang und Grenzen

Dieses Dokument konsolidiert ausschließlich die zwei P1-Befunde, die nach der
ersten Ansatz-C-Implementierung im Spec-Review verblieben sind:

1. vollständige Credential-Namen mit einer führenden Ziffer oder einem
   führenden Bindestrich werden nicht erkannt;
2. ein gültiger Assignment-Head innerhalb des Wertbereichs eines früheren
   gültigen Candidates wird durch den konsumierenden Vollassignment-Regex
   übersprungen.

### 1.1 Amendierung 2026-08-28 (Übernahme der Quality-Review-Findings)

Auf Betreiberentscheidung (Option B) übernimmt diese Amendierung die drei im
Qualitäts-/Securityreview bestätigten Findings als Eingangsbefunde dieses
Umbaus; alle drei sind dort dynamisch reproduziert bzw. gemessen
(`aurelia-tiefenanalyse-v6-2026-08-28/E4_K1_TASK3_QUALITY_REVIEW_2026-08-28.md`):

1. `K1-T3-Q-NEW-01` (P1): Die unquotierte Terminatorklasse des Ist-Stands
   (`$`, `\s`, `;`, `,`, `#`) ist zu eng; ein Credential vor schließendem
   Quote, vor `}`, `)`, `]`, `>` oder mit URL-Wert (`:` im Wert) wird
   verloren. → §7 und §12 sind verbindlich geändert.
2. `K1-T3-Q-NEW-02` (P2): CLI-Flag-Form (`--password=…`). Die Grammatik
   dieses Umbaus deckt sie strukturell bereits ab (NAME-Run inklusive `-`,
   §5); §12 erhält verbindliche Testzeilen.
3. `K1-T3-Q-NEW-03` (P2): Quadratisches Backtracking des Ist-Regex
   (gemessen: Laufzeit ×4 pro Blobverdopplung; 512 KiB ≈ 29 s; 1 MiB ≈
   2 min/Blob; `GIT_TIMEOUT_MS` erfasst `classifyBlob` nicht). Der
   Performancevertrag in §11 wird dadurch zum direkten Abnahmegegenstand
   dieser Amendierung.

Zurückgewiesen und nicht Bestandteil: `K1-T3-Q-NEW-04` — durch primäre
Reproduktion widerlegt (der `.Member`-Kandidat existiert und wird per
AST-Adjudikation unterdrückt; E4 §2).

Für Namens- und Candidate-Enumeration ersetzt dieses Dokument die Abschnitte
6.2, 7, 8.2, 10 und 11 des
[`2026-08-26-aurelia-k1-task3-string-type-bypass-design.md`](2026-08-26-aurelia-k1-task3-string-type-bypass-design.md),
soweit sie widersprechen. Die dort festgelegte kandidatenbezogene
TypeScript-AST-Adjudikation, der Rohscan-Fallback, die öffentlichen Verträge,
die 1-MiB-Grenze und alle Nichtziele bleiben verbindlich.

Dieses Dokument erteilt keine Freigabe für Produktionscode, Commit, Push,
Serverzugriff, History-Rewrite, Statusfortschreibung oder Task 4.

## 2. Eingefrorene Ausgangslage

Der Ausgangs-HEAD ist `73ea21ce8031714174d2b7cc922478a1dc0103af`.
Im Worktree liegen zwei uncommittete, nicht gestagte Implementierungsdateien,
die ausschließlich als lesende Befundgrundlage gelten:

| Datei | SHA-256 am Designstart |
|---|---|
| `scripts/check-push-graph.mjs` | `32c0b5b4ec3fdf5083bc399c5525e11281d7f6301e86e5670840cca9bca1abef` |
| `scripts/check-push-graph.test.mjs` | `ce9e3a6d88e01a5d935212d848141d29f82aa282848f0d749d1427bd9b4a44b9` |

Die vorhandene Suite ist mit diesem Zwischenstand zwar `32/32` grün. Das ist
kein Freigabenachweis, weil die folgenden reproduzierten Fälle fehlen:

| Reproduktion | Ist | Soll |
|---|---:|---:|
| führende Ziffer plus Credential-Suffix | 0 | 1 |
| führender Bindestrich plus Credential-Suffix | 0 | 1 |
| zwei echte überlappende Credential-Candidates | 1 | 2 |

## 3. Bestätigte Ursachen

### 3.1 Inkonsistente Namensgrammatik

Der aktuelle Lookahead erlaubt `[A-Za-z0-9_$-]`, die eigentliche
Capture-Gruppe beginnt aber mit `[A-Za-z_$]`. Dadurch widersprechen Prüfung
und Erfassung einander. Für den rohen Repository-Scanner ist ein Candidate-Name
kein JavaScript-Identifier. Auch Schlüssel aus Text-, Env-, YAML- oder anderen
Konfigurationsformaten müssen nach der freigegebenen ASCII-Grammatik erkannt
werden.

### 3.2 Der Wertverbrauch steuert fälschlich die Enumeration

Der globale Regex erfasst Head und Wert als einen konsumierenden Match. Nach
einem Treffer setzt `/g` hinter dessen Wert fort. Beginnt ein weiterer
gültiger Head innerhalb dieses Wertbereichs, wird seine Startposition nie als
Suchposition betrachtet. Candidate-Discovery und Value-Parsing sind dadurch
unzulässig gekoppelt.

Die Korrektur muss diese Verantwortlichkeiten trennen:

- Head-Enumeration entscheidet, **wo** eine Assignment-Form beginnt;
- der gebundene Value-Parser entscheidet unabhängig, **ob** an diesem Head ein
  gültiger Wert vorliegt;
- AST-Adjudikation entscheidet anschließend nur, **ob genau dieser Candidate**
  als harmlose TypeScript-Property-Signatur bewiesen ist.

## 4. Bewertete Korrekturansätze

| Ansatz | Sicherheits- und Laufzeitbewertung | Entscheidung |
|---|---|---|
| Maximalen Head ohne Wert global enumerieren; Wert je Head begrenzt parsen | Exakte UTF-16-Positionen; spätere Heads bleiben auffindbar; höchstens 256 Value-Schritte pro credentialhaltigem Head; kleiner und auditierbarer Diff. | **verbindlich gewählt** |
| Vollständiger Einpass-DFA für Namen, Separatoren und Werte | Formal linear und präzise, aber deutlich mehr eigener Lexer-Code und größere neue Angriffsoberfläche. | verworfen |
| Vollassignment in Zero-width-Lookahead oder `lastIndex = match.index + 1` | Findet Overlaps, kann bei dichten Fragmenten jedoch wiederholt dieselben Suffixe prüfen und adversarial quadratisch werden. | verworfen |

Ein Head-Regex, der mit mehreren Sternen zugleich nach
`NAME* CREDENTIAL NAME*` sucht, ist ebenfalls verworfen. Bei langen Namen mit
vielen `token`-Fragmenten und fehlendem Separator wäre seine
Backtracking-Oberfläche unnötig schwer beweisbar.

## 5. Verbindliche Grammatik

```text
NAME_CHAR := [A-Za-z0-9_$-]
NAME      := maximaler, nichtleerer Run aus NAME_CHAR

CREDENTIAL :=
  api[_-]?key |
  access[_-]?token |
  client[_-]?secret |
  password |
  passwd |
  token |
  credential

LEFT_BOUNDARY := BOF | vorherige UTF-16-Code-Unit ist kein NAME_CHAR
OPTIONAL      := "?" | leer
SEPARATOR     := "=" | ":"
HEAD          := LEFT_BOUNDARY NAME OPTIONAL WHITESPACE* SEPARATOR WHITESPACE*
```

Der grobe Head-Enumerator darf diese Form verwenden:

```regex
(?<![A-Za-z0-9_$-])(?<name>[A-Za-z0-9_$-]+)(?<optional>\?)?(?<beforeSeparator>\s*)(?<separator>[=:])(?<afterSeparator>\s*)
```

Verbindliche Eigenschaften:

- Flags sind `dgi`; `m` ist nicht erforderlich.
- `name` ist der vollständige maximale ASCII-Run, einschließlich führender
  Ziffer oder führendem Bindestrich.
- Der Enumerator konsumiert höchstens bis `headEnd`, niemals Quote oder Wert.
- Der vollständige Name wird anschließend einmal mit einem separaten,
  case-insensitiven Credential-Teilmuster geprüft.
- Nicht-Credential-Heads dürfen grob enumeriert werden, werden aber vor dem
  Value-Parser verworfen.
- Weil ein Match unmittelbar vor dem Wert endet, beginnt die globale Suche
  innerhalb dieses Werts erneut. Ein späterer Head kann daher nicht durch den
  früheren Wertverbrauch verloren gehen.

## 6. Candidate-Datenvertrag

Weder Werttext noch vollständiger Quelltext werden im Candidate gespeichert.

```typescript
type NamedCredentialCandidate = Readonly<{
  id: number;
  matchStart: number;
  matchEnd: number;
  headEnd: number;
  nameStart: number;
  nameEnd: number;
  optional: boolean;
  questionStart: number | null;
  questionEnd: number | null;
  separator: "=" | ":";
  separatorStart: number;
  separatorEnd: number;
  quoted: boolean;
  quote: "'" | '"' | null;
  quoteStart: number | null;
  quoteEnd: number | null;
  valueStart: number;
  valueEnd: number;
  positionsValid: boolean;
}>;
```

Alle Positionen sind halboffene UTF-16-Code-Unit-Indizes desselben dekodierten
JavaScript-Strings. Für `positionsValid: true` gelten vollständig:

1. alle Indizes sind ganzzahlig, monoton und innerhalb `0..text.length`;
2. `matchStart === nameStart`;
3. `text.slice(nameStart, nameEnd)` ist der maximale vollständige Name;
4. die vorherige Code-Unit ist BOF oder kein `NAME_CHAR`;
5. Separatorbereich und Separatortext sind exakt eine Code-Unit;
6. `16 <= valueEnd - valueStart <= 255`;
7. bei ungequotiertem Wert sind alle Quote-Felder `null`,
   `headEnd === valueStart` und `matchEnd === valueEnd`;
8. bei quotiertem Wert gilt `headEnd === quoteStart`,
   `valueStart === quoteStart + 1`, `valueEnd === quoteEnd`,
   `matchEnd === quoteEnd + 1`, und beide Quotes stimmen überein;
9. `id` folgt strikt der aufsteigenden `nameStart`-Reihenfolge.

Fehlende oder inkonsistente `d`-Indizes machen einen grammatisch erkannten
Candidate unsuppressierbar. Sie dürfen ihn nicht aus dem Raw-Count entfernen.

## 7. Deterministischer Value-Parser

Jeder credentialhaltige Head wird unabhängig ab `headEnd` geprüft. Der Parser
liest höchstens 256 zulässige Value-Code-Units und verwendet unverändert:

```text
VALUE_CHAR := [A-Za-z0-9_./+=:-]
VALUE_LENGTH := 16..255 UTF-16-Code-Units
```

Amendierung 2026-08-28 (K1-T3-Q-NEW-01): `:` ist in `VALUE_CHAR` aufgenommen,
damit URL-Werte (`password=https://…`) erfasst werden. Die Separator-Erkennung
ist davon unberührt: der Separator wird vor dem Wert konsumiert; innerhalb des
Werts ist `:` ein gewöhnliches Value-Zeichen.

### 7.1 Quotierter Zweig

Wenn an `headEnd` `'` oder `"` steht, wird ausschließlich der quotierte Zweig
verwendet:

1. Quote nicht zum Wert zählen;
2. maximalen `VALUE_CHAR`-Run lesen;
3. unmittelbar danach dasselbe schließende Quote verlangen;
4. bei falschem oder fehlendem Quote, Escape/Backslash, weniger als 16 oder
   mehr als 255 Value-Code-Units keinen Candidate erzeugen.

Nach dem schließenden Quote ist wie bisher kein zusätzlicher Lookahead nötig.

### 7.2 Unquotierter Zweig

Andernfalls wird ausschließlich unquotiert geparst:

1. maximalen `VALUE_CHAR`-Run ab `headEnd` lesen;
2. danach EOF oder exakt eine Code-Unit aus dem Terminatorvorrat verlangen
   (Amendierung 2026-08-28, K1-T3-Q-NEW-01);
3. Terminator nicht konsumieren;
4. Terminatorvorrat ist `[\s;,#]` ergänzt um die schließenden syntaktischen
   Trenner `"` , `'`, Backtick, `}`, `)` , `]` und `>`. Öffnende Trenner
   (`[`, `(`) und alle übrigen Zeichen bleiben Nichtterminatoren und führen
   zur Ablehnung;
5. bei 256 zulässigen Code-Units ablehnen; ein 255-Zeichen-Präfix darf nicht
   als Treffer abgeschnitten werden.

Ein ungültiger früher Head beendet die Enumeration nicht. Spätere Heads in
seinem Textbereich werden unabhängig geprüft.

## 8. Overlap-, Duplikat- und Count-Semantik

- Genau ein Candidate entsteht pro erfolgreich geparstem credentialhaltigem
  Head.
- Unterschiedliche `nameStart` bedeuten unterschiedliche Candidates, auch bei
  identischem Namen, identischem Wert oder überlappenden Bereichen.
- Candidate-Bereiche werden niemals vereinigt, abgeschnitten, longest-first
  ausgewählt oder nach Inhalt dedupliziert.
- Der frühere Candidate behält seinen maximalen zulässigen Wertbereich.
- Ein späterer Head wird unabhängig ab seinem eigenen `headEnd` ausgewertet.
- `PASSWORD=<16+ Zeichen>.PREVIEW_CLIENT_SECRET=<16+ Zeichen>` zählt daher
  exakt zwei benannte Candidates, sofern beide gebundenen Value-Parserläufe
  gültig sind.
- Ein Decoy-Head erzeugt keinen Candidate und darf einen späteren gültigen Head
  nicht beeinflussen.
- Identische `nameStart` sind konstruktiv unzulässig. Treten sie dennoch auf,
  bleiben alle Raw-Candidates sichtbar und die gesamte AST-Suppression des
  Blobs ist leer.
- `namedCount = candidates.length - exactSuppressions.size`.

Amendierung 2026-08-28 (Option Y, K1-T3-GRAMMAR-CONFLICT): `=` ist und bleibt
`VALUE_CHAR`; ein unquotierter Wertlauf, der `=` enthält, läuft daher bis zum
nächsten Nicht-Wertzeichen und endet an EOF, Whitespace oder einem Terminator.
Zwei Credential-Zuweisungen in einer solchen Kette zählen **beide** — z. B.
zählt `PASSWORD=short.PREVIEW_CLIENT_SECRET=<16+ Zeichen>` genau **2**
(früherer Lauf bis EOF gültig, späterer Head zusätzlich; nichts wird
verborgen, Abweichung nur in fail-closed-Richtung). „Ungültige frühere Heads"
sind im Sinn dieses Vertrags Längenverletzungen (15/256), fehlende
Terminatoren und Nicht-Credential-Namen; auch sie verbergen keine späteren
Heads. Die Count-Erwartung des zugehörigen Plan-Fixtures ist damit
verbindlich 2 (zuvor 1).

Amendierung 2026-08-28 (QOV-02, Betreiberentscheidung „Fix im Lauf"): Der
Blobcache in `scanBlob` schlüsselt jetzt über `blob\0pfad` statt nur `blob`.
Grundlage: `classifyBlob` ist pfadsensitiv (AST-Suppression nur `.ts`/`.tsx`),
der Blobcache war aber pfadblind — derselbe Blob unter `same/a.ts` und
`same/b.txt` lief `exitCode 0, findings []` statt `credential_like 1` für
`same/b.txt` (gemessen mit injiziertem Git). Das war ein fail-open
Unterzählen in Abhängigkeit von der alphabetischen Pfadreihenfolge. Der
Mangel ist Vorbestand (String/Type-Bypass-Ära); der Umbau machte die
Pfadsensitivität jedoch tragend, und der Betreiber hat die Scope-Erweiterung
der eingefrorenen Region (Design B §14, Git-Enumerator — der Fix ändert keine
Git-Aufrufsemantik, nur den Cache-Schlüssel) ausdrücklich autorisiert.
Regressionstest: „the blob cache never shares classifications across
different paths". Kosten: Blobs an mehreren Pfaden werden je Pfad
klassifiziert (blocking-relevant, nicht timing-kritisch). Zusätzlich
umgesetzt aus dem Quality-Review: JWT-Rohmuster auf `{10,512}` je Segment
begrenzt (Adversarial-Test: punktloses, `eyJ`-dichtes 1-MiB-Blob ≤ 5 s;
gemessen 32 ms) sowie §9.9-Doppelzuordnungsstopp und
Enumerationsfault-/Loader-Zweige regressionstestet.
- Unabhängige Token-, Key-, JWT- und Private-Key-Muster bleiben additiv und
  unverändert auf dem Rohtext.

## 9. AST-Adjudikation mit überlappenden Candidates

Die bereits entworfene Ansatz-C-Adjudikation bleibt eng. Zusätzlich gilt:

1. nur `.ts`/`.tsx`, ungequotiert und Separator `:`;
2. alle relevanten Positionsinvarianten müssen vor dem Parse gültig sein;
3. `nameStart` ist eindeutig, Candidates werden nach `nameStart` indiziert;
4. `questionToken` muss Abwesenheit oder exakte Question-Position bestätigen;
5. `node.name`, `node.type.getStart()` und `node.type.end` müssen exakt die
   Candidate-Bereiche treffen;
6. nur `PropertySignature` unter `InterfaceDeclaration` oder
   `TypeLiteralNode`, argumentloser `TypeReferenceNode`, Identifier oder
   QualifiedName, kein Initializer und exakt ein Semikolon-Tail;
7. Suppression erfolgt ausschließlich über `candidate.id`;
8. ein früherer Candidate, dessen Wertbereich einen späteren enthält, darf
   dessen AST-Zuordnung nicht beeinflussen;
9. Mehrfachzuordnung eines Candidates oder Zuordnung eines AST-Knotens zu
   mehreren Candidates leert die gesamte Suppressionsmenge.

Loaderfehler, inkompatible API, Parseexception, nichtleere oder unlesbare
`parseDiagnostics`, AST- oder Positionsambiguität führen zu null
Suppressions. Candidate-, Wert-, AST- und Parserinhalte verlassen
`classifyBlob` nicht.

## 10. Fehler- und fail-closed-Verhalten

| Zustand | Verbindliches Verhalten |
|---|---|
| Head ist kein Credential-Name | ohne Value-Parsing fortfahren |
| credentialhaltiger Head hat ungültigen Wert | kein Candidate; Enumeration läuft weiter |
| Candidate-Indizes fehlen oder widersprechen Text | Raw-Candidate zählen; keine Suppression |
| Candidate-IDs oder `nameStart` sind mehrdeutig | Raw-Candidates zählen; keine Suppression im Blob |
| Loader, Parser, Diagnostics oder AST-Zuordnung unklar | Raw-Candidates zählen; keine Suppression |
| unerwartete Exception in Head- oder Value-Enumeration | Blob als `unscannable` blockieren; niemals leere Fundmenge |

Für interne Fehler werden ausschließlich konstante, sichere Codes verwendet.
Findings und Diagnostics enthalten weder Namen, Werte, Assignments, Quelltext
noch Exceptiontexte.

## 11. Performancevertrag

- Vor jeder Enumeration gilt die bestehende 1-MiB-Blobgrenze.
- Head-Enumeration über disjunkte maximale Namen: `O(n)`.
- Credential-Filter: einmal pro grobem Head.
- Value-Parser: höchstens 256 Schritte pro credentialhaltigem Head.
- Candidate-Map: `O(c)`.
- TypeScript: höchstens ein Parse und ein iterativer AST-Durchlauf `O(a)` pro
  relevantem Blob.
- Gesamt: `O(n + c + a)`, zusätzlicher Speicher `O(c + a)`.
- Keine neuen Subprozesse, Datei-I/O-, Netzwerk- oder unbeschränkten
  Backtrackingpfade.

Amendierung 2026-08-28 (K1-T3-Q-NEW-03): Dieser Vertrag ist durch das
Qualitätsreview gegen den Ist-Stand als verletzt belegt (gemessen ×4 Laufzeit
pro Blobverdopplung; 512 KiB ≈ 29 s; `GIT_TIMEOUT_MS` erfasst `classifyBlob`
nicht). Die Einhaltung ist in der Abnahme über die drei adversarialen
§12-Läufe mit ihren 5-Sekunden-Timeouts hinaus für den Worst Case
„nahezu 1 MiB Identifier-Run mit vielen Credentialfragmenten" explizit
nachzuweisen.

Adversarial nachzuweisen sind ein nahezu 1 MiB langer Name-Run mit vielen
Credentialfragmenten ohne Separator, eine dichte Folge überlappender Heads und
eine relevante nahezu 1 MiB große TS-Datei. Jeder Lauf erhält ein
5-Sekunden-Testtimeout.

## 12. Verbindliche TDD-Matrix

| Gruppe | Erwartung |
|---|---|
| führende Ziffer und führender Bindestrich, jeweils mit Suffix | je Count 1 |
| vollständiger Prefix-/Suffix-Name | Count 1; kein Teilname |
| linke Boundary mit Name-Char gegenüber `.`, `/`, `+`, `=` | maximale Namensgrenze korrekt |
| zwei echte Dot- und Slash-Overlaps | je Count 2 |
| Decoy plus Candidate | Count 1 |
| ungültiger früher Credential-Head plus späterer gültiger Candidate | späterer Candidate Count 1 |
| Single-/Double-Quote | je Count 1 |
| unclosed/mismatched Quote | Count 0 |
| unquoted EOF und `\s`, `;`, `,`, `#` | je Count 1 |
| unquoted Abschluss durch `"`, `'`, Backtick, `}`, `)`, `]`, `>` — Stringliteral, JSON-Ende, Closing-Delimiter | je Count 1 (Amendierung 2026-08-28, K1-T3-Q-NEW-01) |
| unquoted `[` oder `(` als Folgezeichen | Count 0 |
| CLI-Flag-Form `--client-secret=<16+>` und `--password=<16+>` am Zeilenanfang | je Count 1 (K1-T3-Q-NEW-02) |
| URL-Wert `password=https://example.com/<16+>` | Count 1 (K1-T3-Q-NEW-01) |
| Credential in Stringliteral `"NAME=VALUE";` und vor `}` (JSON) | je Count 1 (K1-T3-Q-NEW-01) |
| Längen 15, 16, 255 und 256, quoted/unquoted | 0, 1, 1, 0 |
| optionales `?` an echter Property-Signatur | exakt unterdrückt |
| Strings, Templates, Kommentare und Runtimekontexte | Raw-Candidate sichtbar |
| einfache und QualifiedName-Property-Signaturen | exakt unterdrückt |
| komplexe oder malforme Typen und Parse-Diagnostic | fail-closed sichtbar |
| echte Signatur plus zwei Overlaps in String oder Kommentar | Count 2; nur Signatur unterdrückt |
| CRLF, BMP-Zeichen und astrales Emoji vor identischem Candidate | exakte Position und Count |
| `.js/.mjs/.mts/.cts/.txt` | keine AST-Suppression |
| TypeScript-Loader fehlt oder ist inkompatibel | Raw-Count unverändert |
| exakt 1 MiB / 1 MiB plus 1 Byte | normaler Scan / `unscannable` |
| Findings, ScanGraph, CLI und interne Fehler | keine Inhalte oder Exceptiondetails |
| Scanner- und Testquelle | Selbstscan sauber |

Alle Credentialnamen und Werte werden in Tests aus harmlosen Fragmenten
zusammengesetzt. Assertionmeldungen dürfen nicht den vollständigen Testinhalt
interpolieren.

## 13. Späterer Implementierungsscope

Eine separat freizugebende Korrektur darf ausschließlich ändern:

- `scripts/check-push-graph.test.mjs`;
- `scripts/check-push-graph.mjs`.

Nicht erlaubt sind Dokument-, Status-, Paket-, Lockfile-, V3-, Produkt-,
Server-, Credential-, Task-4- oder Git-History-Änderungen.

## 14. Abnahme-, Review- und Stoppregeln

Eine spätere Implementierung ist erst abnahmefähig, wenn gemeinsam gilt:

1. alle drei reproduzierten P1-Fälle sind vor der Korrektur RED und danach mit
   Counts `1`, `1` und `2` GREEN;
2. Dot- und Slash-Overlap zählen jeweils exakt 2;
3. vollständige Scanner-Suite und `npm run check:k1-control` sind grün;
4. adversariale Laufzeittests bleiben innerhalb der Timeouts;
5. der reale Publikationsgraph bleibt erwartungsgemäß Exit 1 und gibt nur
   sichere Felder aus;
6. Diff und Index umfassen ausschließlich Scanner und Scanner-Test;
7. `package.json`, `package-lock.json` und `docs/project-control/K1-STATUS.md`
   bleiben unverändert;
8. fokussiertes Spec-Review ist explizit PASS;
9. erst danach ist ein unabhängiges Sol-xHigh-Quality/Security-Review zulässig
   und ebenfalls explizit PASS;
10. die Primärinstanz reproduziert jedes P0-P2-Finding;
11. ein Korrekturlauf ist zulässig; ein danach verbleibender oder systemischer
    P0-P2-Befund stoppt erneut zur Konsolidierung;
12. Task 4 bleibt bis zu beiden PASS-Verdikten gesperrt.

Commit, Push, Serverzugriff, History-Rewrite und Statusfortschreibung benötigen
jeweils eine eigene ausdrückliche Freigabe.

## 15. Restrisiken

- Die geforderte überlappende Interpretation kann Counts bewusst erhöhen. Das
  ist fail-closed und Teil des Abnahmevertrags.
- Off-by-one-Fehler an 255/256, Quote-Ende, EOF und Unicode-Positionen sind die
  wahrscheinlichsten Implementierungsfehler und werden deshalb separat RED
  nachgewiesen.
- `\s` umfasst Unicode-Whitespace. Dieses bestehende Verhalten bleibt erhalten
  und wird explizit getestet.
- TypeScript-Upgrades bleiben vertrauensrelevant und müssen die gesamte
  Positionsmatrix erneut durchlaufen.

## 16. Abschlussbedingung des Designs

Das Korrekturdesign ist erfüllt, wenn Head-Enumeration und Value-Parsing
getrennt sind, alle vollständigen Namen nach der exakten ASCII-Grammatik
erfasst werden, jeder gültige überlappende Head unabhängig gezählt wird, nur
positionsgleiche Property-Signatures unterdrückt werden und jeder Fehler auf
einen blockierenden Raw- oder `unscannable`-Zustand fällt.
