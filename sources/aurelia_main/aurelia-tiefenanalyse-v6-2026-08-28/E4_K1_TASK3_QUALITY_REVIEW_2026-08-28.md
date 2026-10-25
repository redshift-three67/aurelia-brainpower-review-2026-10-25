# E4-Evidenz: K1 Task-3 Qualitäts-/Securityreview — 2026-08-28

Verfahren nach `QUALITY-ROUTING.md` Ablauf B Schritt 5 und Plan B Task 7;
Vorbedingung Spec-PASS (E3 §7) erfüllt. Reviewer: frische, unabhängige
Instanz mit dem wörtlichen Adversarial-Contract aus Plan B Task 7 Step 2.
Primäre Instanz hat **jedes Finding dynamisch reproduziert** (Design B §13.4)
— Skript: `repro_quality_findings_2026-08-28.mjs` (synthetische Fixtures,
keine Fundwerte in der Ausgabe).

**Diese Datei ist Review-Evidenz, keine Gate-Freigabe und kein Commit.**

## 1. Urteil

- Reviewer-Meldung: „VERDICT: PASS" — **aber mit 4 offenen Findings
  (P1 + 3× P2).** Nach QUALITY-ROUTING §3.6 blockieren P0–P2; ein PASS mit
  offenen blockierenden Findings ist für die Gate-Entscheidung **nicht
  bestanden**. Maßgebliches Ergebnis: **Qualitätsreview nicht bestanden,
  eine Korrekturschleife offen.**
- Positiv verifiziert (nicht blockierend, vom Reviewer + primär bestätigt):
  AST-Adjudikation ohne Fail-open-Lücke (nur positionsgleiche unquotete
  `:`-Kandidaten, `matchStart===nameStart` garantiert, Diagnostik-/Loader-
  Fehler fallen auf Rohscan), kein Wertaufrtritt über die Vertragsfelder
  hinaus, `require("typescript")` sicher vom Scannerstandort verankert
  (kein Laden eines im Zielrepo eingeschleusten `node_modules/typescript`),
  alle vier Abnahmeläufe frisch grün bzw. vertragsgemäß (33/33, Control 0,
  Realgraph Exit 1 mit 15 sicheren Zeilen, nackter CLI Exit 2).

## 2. Findings und primäre Reproduktion

### K1-T3-Q-NEW-01 · P1 · BESTÄTIGT (dynamisch)

Terminatorklasse unquotierter Werte (`mjs:31`, `(?=$|[\s;,#])`) zu eng;
Design A §5 verspricht „endet an Dateiende, Whitespace oder einem
syntaktischen Trenner".

| Fixture | Ergebnis |
|---|---|
| `PREVIEW_CLIENT_SECRET=…` in Stringliteral (`"…";`) | **credential_like=0 — verloren** |
| `PREVIEW_CLIENT_SECRET=…}` (JSON-Ende) | **0 — verloren** |
| `password=https://example.com/aaaaaaaaaaaaaaaa` | **0 — verloren** (Wert-Charset ohne `:`) |
| Gegenprobe: nackter Wert am Zeilenende | 1 — funktioniert |

### K1-T3-Q-NEW-02 · P2 · BESTÄTIGT (dynamisch)

Lookbehind (`mjs:17`) verbietet vorangehenden `-`, Identifiergruppe darf
nicht mit `-` beginnen ⇒ CLI-Flag-Form verloren.

| Fixture | Ergebnis |
|---|---|
| `--password=SyntheticScannerFixtureValue` | **0 — verloren** |
| Gegenprobe `x--password=…` | 1 (Match startet am `x`) — exakt die Reviewer-Diagnose |

### K1-T3-Q-NEW-03 · P2 · BESTÄTIGT (gemessen, quadratisch)

Geschachtelte gierige Quantoren im Lookahead (`mjs:18-20`) über
Identifier-Runs; `GIT_TIMEOUT_MS` (`mjs:10`) erfasst nur Git-Subprozesse,
nicht `classifyBlob`. Gemessen an `"token".repeat(n)`:

| Blobgröße | Laufzeit | Wachstum |
|---|---|---|
| 64 KiB | 450 ms | — |
| 128 KiB | 1 787 ms | ×3,97 |
| 256 KiB | 7 190 ms | ×4,02 |
| 512 KiB | 28 907 ms | ×4,02 |

Perfektes Quadrat; Extrapolation 1 MiB ≈ **~2 Minuten pro Blob**. Ein
adversarialer Blob hängt den Pre-Push-Gate praktisch auf (Ergebnis bleibt
fail-closed, aber die Liveness ist verloren).

### K1-T3-Q-NEW-04 · P2 · ZURÜCKGEWIESEN (dynamisch widerlegt)

Reviewer-Behauptung: Beim Testfall `…: PreviewClientSecretType.Member; }`
entstehe **gar kein** Kandidat (Wert am `.` abgeschnitten), der Test beweise
also nichts, und nach NEW-01-Fix kippe er auf count 1.

Primäre Diskriminierung:

| Probe | Ergebnis | Schluss |
|---|---|---|
| `.Member`-Inhalt auf `.txt` (AST aus) | credential_like=**1** | Kandidat existiert (Charset enthält `.`) |
| derselbe in TS ohne `;`-Tail | 1 | fail-closed Raw-Zählung ⇒ Kandidat da |
| derselbe in TS mit `;` | [] | AST-Adjudikation unterdrückt den QualifiedName echt |

Der Testfall beweist also **genau** die behauptete QualifiedName-Unterdrückung
mit Positionsgleichheit; die Kipp-Prognose ist falsch (nach einem
NEW-01-Fix bliebe er unterdrückt). Finding abgelehnt. Residuum als nicht
blockierende Anmerkung: ein **expliziter** zweiter QualifiedName-Testfall
(mit `;`) würde die Matrixzeile noch lesbarer machen — optional, keine Pflicht.

## 3. Strukturbefund und KONSOLIDIERUNGSSTopp

Alle drei bestätigten Findings haben dieselbe Wurzel: der
Lookahead-Mechanismus in `NAMED_CREDENTIAL_ASSIGNMENT_PATTERN`. Der bereits
geplante Overlap-Enumeration-Umbau (Plan + Design liegen committed vor)
ersetzt genau diesen Mechanismus durch lineare head-first-Enumeration mit
JS-seitiger Namensprüfung.

**Aber — neuer Vertragskonflikt (Konsolidierungspunkt):** Das
Overlap-Design testet in Task 3 Step 1 absichtlich `right-bracket`,
`right-paren`, `trailing-quote` als **erwartet 0** und definiert
`isUnquotedTerminator` mit derselben engen Klasse (`$`, Whitespace, `;`, `,`,
`#`). Das steht im direkten Gegensatz zur NEW-01-Erwartung des
Qualitätsreviews (Credential in Stringliteral/JSON muss gefunden werden).
Die beiden Verträge sind ohne Designentscheidung nicht gleichzeitig erfüllbar.

Nach QUALITY-ROUTING §4 („Bleibt ein P0–P2-Befund offen oder entsteht ein
systemischer Befund, **stoppt die Arbeit zur Konsolidierung**") und Plan B
Task 7 Step 3 ist der korrekte nächste Schritt daher **keine** weitere
ad-hoc-Korrektur, sondern eine Betreiberentscheidung:

- **Option A:** Korrekturschleife im jetzigen Architekturstand (Terminatoren
  erweitern, Bindestrich-Präfix zulassen, Lookahead entfernen → lineare
  JS-Prüfung) **plus** entsprechende Amendierung der Overlap-Design-Matrix
  (dort müssten trailing-quote/bracket/paren-Erwartungen auf 1 gehen).
- **Option B:** Die drei Findings als Eingangsbefunde in den geplanten
  Overlap-Umbau überführen und dessen Design **vor** Implementation um die
  NEW-01-Terminator-Grammatik und NEW-02-Präfixregel erweitern (Designämenderung
  mit neuem Digest, danach TDD-Run wie geplant).
- **Option C:** Vollständiger Stopp und Konsolidierung der Verträge ohne
  Codeänderung (alles bleibt im dokumentierten Zustand, Review-Evidenz E3/E4).

Beide Reviews sind damit prozessual sauber dokumentiert: Spec-PASS (E3),
Qualität nicht bestanden mit 3 bestätigten blockierenden Findings (E4),
1 Finding durch primäre Reproduktion widerlegt. Task 4 bleibt in jeder
Option gesperrt; kein Commit, kein Push, Publikationsgate weiter blockiert
und funktioniert (Exit 1).

## 4. Vollzogene Amendierung (28.08., Betreiberoption B)

Der Betreiber hat Option B gewählt. Vollzogen (nur Dokumente, kein Code):

- **Design amendiert**
  (`…overlap-enumeration-correction-design.md`): YAML-Header (amended/
  trigger/decision, 3 neue Findings), neuer Abschnitt §1.1 (Übernahme der
  drei Findings, NEW-04 ausdrücklich zurückgewiesen), §7 `VALUE_CHAR` um
  `:` erweitert (URL-Werte), §7.2 Terminatorvorrat um schließende
  syntaktische Trenner (`"` `'` Backtick `}` `)` `]` `>`) erweitert,
  öffnende Trenner explizit Nichtterminatoren, §12-Matrixzeilen geflippt
  bzw. ergänzt (CLI-Flag, URL, Stringliteral, JSON-Ende, `[`/`(` → 0),
  §11 Performancevertrag als Abnahmegegenstand mit Messbaseline bestätigt.
  **Neuer Design-SHA-256: `c8a54422e2c13a753404ef25f033b06038b741698f5174722816d69aaef89736`.**
- **Plan amendiert** (`…overlap-enumeration-correction.md`): §0-Tabelle
  (Amendierungszeile, neuer Digest, erweiterte Findingsliste), Run-Start-
  Hashes aktualisiert (test.mjs `81607e33…`, Scanner unverändert
  `32c0b5b4…`), Task 1 Step 1: HEAD-Gleichheit → Vorfahren-Prüfung
  (Notiz nach dem Block), Task 1 Step 2: neuer Digest, Task 2 Step 2b:
  fünf E4-Regressionstests (Stringliteral, JSON-Ende, CLI-Flags, URL-Wert,
  öffnende Klammer → 0) mit RED-Nachweis-Pflicht, Task 3 Step 1: Fixture-
  Flip (schließende Trenner → erwartet 1; öffnende → 0), Task 7 Step 1:
  Allowlist um Migrationsdesign ergänzt, Final stop condition um E4-
  Abschluss erweitert.
- **Integrität nach Amendierung:** Fence-Balance beider Dokumente gerade,
  Digest-Konsistenz Design↔Plan an beiden Stellen geprüft, K1-Control
  Exit 0, `git diff --check` Exit 0, Staging leer, Scanner-Hash
  unverändert.

Damit ist der Overlap-Umbau vertragsseitig bereit. Der TDD-Implementierungs-
lauf selbst braucht gemäß Design §1/Plan §0 eine neue, diesen Plan
namentlich benennende Betreiberfreigabe.
