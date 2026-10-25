# E3-Evidenz: K1 Task-3 fokussiertes Spec-Review — 2026-08-28

Verfahren nach `QUALITY-ROUTING.md` Ablauf B (Spur B — Critical Assurance) und
den Decision-Contracts der Pläne `2026-08-26-aurelia-k1-task3-correction.md`
(Vertrag A) bzw. `2026-08-26-aurelia-k1-task3-string-type-bypass.md` (Vertrag B).
Review-Gegenstand ist der Korrekturzustand von Task 3: committed (A: P1-01,
P1-02, Q-01, zwischen `b84b72a` und `e930aab`) plus uncommitted Working-Tree
(B: String/Type-Bypass-AST, das dokumentierte Dirty-Overlay).

**Diese Datei ist Review-Evidenz, keine Gate-Freigabe und kein Commit.**

## 1. Reviewpaket (sanitisiert, §4 QUALITY-ROUTING)

- Verträge: Plan A + Design A, Plan B + Design B (Design-B-SHA-256
  `9c0e05ad…323e` — stimmt mit dem in Plan B fixierten Wert überein)
- Diff: `git diff --no-ext-diff --unified=100 b84b72a -- scripts/check-push-graph.mjs
  scripts/check-push-graph.test.mjs docs/project-control/K1-STATUS.md`
  (Working-Tree inklusive, da B uncommitted ist)
- Frische Abnahmeläufe (primäre Instanz, vor Reviewerstart; Reviewer wiederholte
  alle vier mit identischem Ergebnis)
- Nicht enthalten: Chatverlauf, `source/`-Ordner, Secrets, fremder Produktcode

## 2. Frische Abnahmeevidenz (beide Instanzen unabhängig, ergebnisidentisch)

| Befehl | Ergebnis |
|---|---|
| `node --test scripts/check-push-graph.test.mjs` | Exit 0, **32/32 PASS** |
| `npm run check:k1-control` | Exit 0 |
| Real-Graph `--base origin/codex/aurelia-vorbereitung --head HEAD --mode full` | Exit 1, 15 Records, Regex-Audit 15/15 Zeilen nur `category`/`blob`/`path`/`count`, keine Fundwerte |
| Nackter CLI-Aufruf | Exit 2 |
| Scope | Staging leer; Dirty = exakt die 2 Scanner-Dateien; 3-Dateien-Diff vs. `b84b72a` ok; Overlay-Hashes bitidentisch zu Plan-Notierung (`32c0b5b4…`/`ce9e3a6d…`) |

## 3. Urteil des unabhängigen Reviewers (frische Instanz ohne Chatverlauf)

**VERDICT: FAIL** (Vertrag A: FAIL · Vertrag B: FAIL) — 3 Findings.
Alle übrigen Vertragspunkte wurden vom Reviewer als erfüllt verifiziert
(u. a. P1-01-Positiv/Negativgrenzen, P1-02-Stringdiagnostiken exakt getestet,
Q-01 grep-Nullbefund, Non-Leakage, kompletter AST-Pfad, Blockmaskierung
vollständig entfernt, öffentlicher Vertrag/CLI/Exit unverändert).

## 4. Findings und primäre Verifikation (Ablauf B Schritt 8)

Alle drei Befunde wurden von der primären Instanz lokal reproduziert und
**akzeptiert**:

### K1-T3-NEW-01 · P1 · Bestätigt

- **Vertrag:** Design A §5 („Bereits erkannte gequotete Zuweisungen bleiben
  regressionsfrei"); Design B §10 („Gequotete und unquotierte `:`-/`=`-Werte |
  bestehende Erkennung regressionsfrei"); Plan A Task 2 Step 5.
- **Evidenz:** Alle gequoteten Wert-Fixtures der Suite verwenden ausschließlich
  `:` (doubleText/singleText/`interface Literal { n: 'v'; }`/komplexer Typ).
  Quotiert + `=` existiert in **keiner** Assertion. Nur unquotiert wird mit
  `=` getestet (Test `syntheticUnquotedPreviewSecret()`).
- **Reproduktion der Relevanz:** `git show b84b72a:scripts/check-push-graph.mjs`
  zeigt: vor der Korrektur war die gequotete Form (`["']` + `\1`-Backreference)
  die **einzige** benannte Credential-Erkennung. Die häufigste Realform
  (`NAME="…"`) könnte also regressieren, ohne dass ein Test rot würde.
- **Korrektur:** 1–2 Assertions ergänzen (gequotet + `=`, double/single),
  danach volle Suite + Realgraph.

### K1-T3-NEW-02 · P2 · Bestätigt

- **Vertrag:** Design B §10, Zeile 262 („Strings mit escaped Quote, Backslash,
  Backtick oder `${...}` | Kandidat bleibt sichtbar") und Zeile 277 („Exakt
  1 MiB und 1 MiB plus 1 Byte | normaler Scan beziehungsweise `unscannable`").
- **Evidenz:** Backtick/`${...}` abgedeckt (Testzeilen ~206–215); escaped
  Quote/Backslash im Stringinhalt fehlt. Blobgrenze: nur `1_048_577` →
  `unscannable` (Testzeile 606); exakt `MAX_BLOB_BYTES` (1_048_576,
  `buffer.length > MAX_BLOB_BYTES`, mjs:377) als Normallfall ungetestet.
- **Korrektur:** je eine Minimal-Fixture (String mit Escape-Quote/Backslash;
  Blob exakt 1_048_576 Bytes → normale Klassifikation).

### K1-T3-NEW-03 · P2 · Bestätigt

- **Vertrag:** Plan B Task 4 Step 6 (`K1_T3_AST_BRANCH_SCOPE_MISMATCH`, exakt
  4 Dateien seit `e930aab`) und Task 5 Step 2.
- **Evidenz:** `git diff --name-only e930aab..HEAD` liefert aktuell **5**
  Dokumente — zusätzlich die separat autorisierten Doc-Checkpoints
  (`f1082f9` Overlap-Plan/Design, `85017ba`/`aec827f` Migrationsdesign). Die
  Scope-Assertion des Plans würde beim aktuellen, legitimen Zustand auslösen.
- **Bewertung:** Prozessbefund (veraltete Plan-Assertion), **kein** Code- oder
  Implementierungsflächendefekt — die zwei Implementierungsdateien sind
  exakt konform.
- **Korrektur:** Plan-allowlist um die autorisierten Dokumente ergänzen oder
  Assertion auf die zwei Implementierungsdateien beschränken (Doc-Änderung).

## 5. Konsequenzen (nach Plan B Task 6 Step 4 / QUALITY-ROUTING)

1. **Spec-Review: FAIL** → Qualitätsreview startet **nicht**; Task 4 bleibt
   blockiert; keine K1-STATUS-Aktualisierung; kein Commit.
2. Vorgesehene **eine Korrekturschleife**: Zurück zu den betroffenen
   RED/GREEN-Flächen (NEW-01, NEW-02 als Testergänzungen im Working-Tree;
   NEW-03 als reine Plan-Dokumentkorrektur). Danach nur der betroffene
   Reviewumfang plus Regression erneut (kein Vollreview nötig).
3. **Kein Befund stellt die Scannerfunktion in Frage:** alle frischen
   Abnahmeläufe grün bzw. vertragsgemäß rot (Realgraph Exit 1, Gate blockiert).
   NEW-01 ist eine **Abdeckungslücke**, kein nachgewiesener Fehler.
4. Implementierung der Korrekturschleife braucht gemäß Plan B §0 eine
   ausdrückliche Betreiberfreigabe, die diese Korrektur benennt.

## 6. Korrekturschleife (28.08., vom Betreiber für Schritte 1–3 freigegeben)

Alle drei Findings wurden im Working-Tree geschlossen (kein Commit):

- **NEW-01:** Test „classifyBlob recognizes quoted equals-separated credential
  assignments without values" (gequotet + `=`, double/single, count 1,
  Non-Leakage).
- **NEW-02:** escaped-Quote- und Backslash-Fixtures im Strings/Templates-Test;
  `data/exact-limit.dat` exakt 1_048_576 Bytes mit synthetischem Token;
  Assertionen: nicht `unscannable` UND `credential_like`-Fund für genau
  diesen Pfad.
- **NEW-03:** beide `$allowedSinceStart`-Arrays in Plan B um die drei
  separat autorisierten Dokumente erweitert, Notizen nach den Codeblöcken.
  (Zwischenvorfall: erste Notiz landete inside eines PowerShell-Blocks,
  sofort erkannt, revertiert und korrekt nach dem Fence platziert.)

**Zähne-Beweis NEW-01:** TEMP-Klon mit mutierter quoted-Alternative
(`{16,255}`→`{32,255}`) → neuer Test schlägt fehl; echter Worktree grün.
Der Scanner selbst wurde nicht berührt (SHA-256 weiterhin `32c0b5b4…`);
test.mjs neu `81607e33…`.

**Frische Evidenz nach Korrektur:** Suite 33/33 PASS · K1-Control Exit 0 ·
Realgraph Exit 1, 15 Records, Shape-Audit 0 unsichere Zeilen ·
`git diff --check` 0 · Staging leer · Kategorien-Zeilen identisch zum
Vorher-Lauf (Hinweis: die in E1 berichtete „credential_like 5" ist die
Count-Summe inkl. `server.ts count=2`; die Zeilenzahl ist 4 — kein Record
verschwunden).

## 7. Scoped Re-Review (Ablauf B Schritt 7) — PASS

Durchführung durch dieselbe unabhängige Instanz, nur betroffener Umfang +
Regression, frische eigene Läufe. **VERDICT: PASS, FINDINGS: none.**
Wesentliche Re-Review-Befunde (von der primären Instanz gegen eigene
Messungen bestätigt):

- NEW-01 geschlossen; die Design-B-§10-Matrix Gequotet/Unquotet × `:`/`=` ist
  vollständig; der count kann strukturell nur aus der gequoteten-`=`-Verzweigung
  stammen (`.txt`-Pfad ⇒ AST-Pfad inaktiv, keine RAW_CREDENTIAL_PATTERN matcht).
- NEW-02 geschlossen; §10-Zeilen „escaped Quote, Backslash, Backtick,
  `${...}`" und „Exakt 1 MiB und 1 MiB plus 1 Byte" vollständig belegt.
- NEW-03 sauber: `git diff HEAD -- <Plan>` ausschließlich additions; beide
  PowerShell-Blöcke intakt; drei Einträge = exakt die Differenz von
  `git diff --name-only e930aab..HEAD`.
- Integrität: mjs-Hash unverändert und Regeneratediff vs. Erstprüfung
  0 Delta-Zeilen; Design-B-SHA weiterhin `9c0e05ad…`; package.json/
  package-lock.json unverändert; HEAD `aec827f`, Staging leer, kein Commit.

**Ergebnis: Spec-Review Task 3 = PASS (nach einer Korrekturschleife).**
Damit ist die Vorbedingung des Qualitäts-/Securityreviews (Plan B Task 7
Step 1) erfüllt. K1-STATUS-Aktualisierung und Commit bleiben davon unberührt
und brauchen weiterhin separate Betreiberfreigaben.
