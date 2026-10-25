# E8 — K1 Task 6 Concept-Shell-Vertrag

**Zeitstempel:** 2026-08-31, 12:06 CEST  
**Letzte Aktualisierung:** 2026-08-31, 18:28 CEST  
**Status:** `TASK6_COMMITTED_TASK7_AUTHORIZED_NOT_STARTED`  
**Task:** K1 Task 6 — Portal und zentrale Schale auf K1 ableiten  
**Basis:** Branch `codex/aurelia-konsolidierung`, HEAD `c00fd83cdea707d5ed6587d5703b35cef0460fe6`, Pflichtvorfahr `8706186af01e10e4253e25abb31bf3577110dae4`  
**Freigabegrenze:** lokale Task-6-Bearbeitung freigegeben; kein Staging, Commit oder Push

## 1. Read-only Preflight

| Prüfung | Ergebnis |
|---|---|
| `git status --short --branch` | sauber; Branch zwei Commits vor Tracking-Ref |
| `git rev-parse HEAD` | exakt `c00fd83cdea707d5ed6587d5703b35cef0460fe6` |
| Pflichtvorfahr | vorhanden, Exit 0 |
| `git rev-list --left-right --count origin/codex/aurelia-konsolidierung...HEAD` | `0 2` |
| Diff gegen HEAD | sauber, Exit 0 |
| `git diff --check` | sauber, Exit 0 |
| `npm run check:canon` | Exit 0 |

Der grüne Ausgangslauf von `check:canon` ist für den noch fehlenden globalen Statusbereich ein **False-green-Baselinebefund**: Der bestehende Vertrag prüft die Task-6-Anforderung noch nicht. Er ist keine Task-6-Abnahme und wird nicht künstlich durch veraltete Routentexte rot gemacht.

E8 und alle vier Status-Live-Dateien wurden mit `git check-ignore -v` unter der bestehenden Regel `/aurelia-tiefenanalyse*/` als ignoriert bestätigt.

## 2. Exakter sichtbarer Vertrag

`ConceptShell` muss auf jeder Konzeptseite genau einen unbedingten Statusbereich zeigen. Der Bereich enthält genau zwei direkte sichtbare Absatzzeilen mit diesen unabhängigen, exakten Literalen:

```text
Phase-1-Schale vorhanden · Produktarbeit pausiert bis G0-SRV-12
Nur synthetische Daten · keine Server-, CUDA-, USB- oder Art.-9-Aktivierung
```

„Zwei Zeilen“ bezeichnet genau zwei direkte semantische Statuszeilen. Auf schmalen Viewports dürfen diese Zeilen natürlich umbrechen; ein erzwungenes physisches Einzeilenlayout wäre mit der mobilen Overflow-Grenze unvereinbar.

## 3. Struktur- und Semantikvertrag

Der Statusbereich muss:

1. genau einmal innerhalb der exportierten Funktion `ConceptShell` vorkommen;
2. das literale Attribut `role="status"` tragen;
3. direkt in `<main id="inhalt">` stehen;
4. vor dem direkten `{children}`-Ausdruck stehen;
5. genau zwei direkte sichtbare `<p>`-Kinder und kein drittes sichtbares Kind besitzen;
6. beide Texte als statische JSX-Literale tragen;
7. unbedingt gerendert werden — keine Bedingung, Schleife, Hilfsfunktion, Fragmentprojektion oder versteckte Kopie;
8. sichtbar bleiben — kein `hidden`, `aria-hidden`, `sr-only`, `invisible`, `opacity-0` oder äquivalenter Verdeckungsweg.

Kommentar-, Dead-String- oder sonstige Quelltextvorkommen erfüllen den Vertrag nicht.

## 4. Mobiler Overflow-Vertrag

Der gemeinsame Statuscontainer muss mindestens die äquivalenten Tailwind-Eigenschaften tragen:

- `box-border`
- `w-full`
- `min-w-0`
- `max-w-full`
- `whitespace-normal`
- `break-words`

Im Statusunterbaum sind insbesondere verboten:

- `whitespace-nowrap`
- `w-max`, `min-w-max` oder andere Max-Content-Erzwingung
- `overflow-x-auto`, `overflow-x-scroll` oder horizontale Scrollflächen
- sichtbarkeitsunterdrückende Klassen oder Attribute

Der fokussierte Test prüft zusätzlich offline bei 320×568 und 390×844, dass Dokument und Statusbereich nicht horizontal überlaufen und beide Absatzgrenzen innerhalb des Statusbereichs bleiben. Die vollständige Anwendung/CSS-Browserabnahme bleibt planmäßig Task 14 vorbehalten.

## 5. Fail-closed Regeln

`conceptShellStatusErrors(root)` muss mit stabiler Regel-ID und ausschließlich dem Repositorypfad fehlschlagen bei:

- fehlender oder unlesbarer `src/components/concept/shell.tsx`;
- syntaktisch fehlerhafter/malformter TSX;
- fehlendem, dupliziertem oder bedingtem Statusbereich;
- fehlendem, nichtliteralem oder abweichendem `role`;
- falschem Parent, falscher Reihenfolge zu `{children}` oder zusätzlichem sichtbarem Kind;
- fehlender, geänderter, duplizierter, dynamischer oder versteckter Textzeile;
- fehlenden mobilen Pflichtklassen;
- verbotenen Overflow-/Nowrap-/Hidden-Klassen oder -Attributen.

Die Prüfung verwendet den TypeScript-Compiler-AST; breite Regexe dürfen Kommentare, Strings oder tote Ausdrücke nicht als gültiges JSX akzeptieren. Diagnosen dürfen keinen gefundenen Quelltext ausgeben.

## 6. Exakter Scope

Erlaubte tracked Task-6-Dateien:

1. `scripts/canon-contract.mjs`
2. `scripts/canon-contract.test.mjs`
3. `scripts/concept-shell-status.test.mjs`
4. `src/components/concept/shell.tsx`

Nichtziele:

- keine Änderung unter `src/routes/`, insbesondere nicht `src/routes/kozyrev.tsx`;
- keine Änderung an `package.json`;
- keine Neubearbeitung oder Rücknahme von Task 5;
- keine Änderung an K1-STATUS, Masterplan, Specs, historischer E7-/V3-Evidenz, Credentials oder Referenzzweigen;
- kein Dev-Server, Build, Preview, Migration, Serverzugriff oder nichtsynthetischer Datenzugriff;
- kein Staging, Commit oder Push.

## 7. RED/GREEN- und Reviewfolge

1. Vertrags-/Fixturetests zuerst; initiales RED ausschließlich wegen fehlender Task-6-Validator-API.
2. Validator implementieren, Shell unverändert lassen; Fixture-GREEN.
3. Reales Repository-RED: `check:canon` und fokussierter UI-Test ausschließlich wegen fehlendem Shell-Statusbereich.
4. Minimalen Shell-Status implementieren.
5. GREEN: fokussierter UI-Test, vollständige Canon-Tests, `check:canon`, Typecheck, K1-Control, fokussiertes ESLint, Diff-Check und Scope-/Route-Diff-Nachweis.
6. Fokussiertes Spec-Review; offene P0–P2 blockieren.
7. Erst nach Spec-PASS und separater Betreiberbestätigung für Reasoning `Extra High`: frisches Quality-/Securityreview; jeder P0–P2-Befund wird primär reproduziert und test-first eng geschlossen.
8. Beide Reviews PASS → vollständige Task-6-Gates frisch wiederholen; erst dann lokaler, uncommitteter Task-6-PASS.

## 8. Stop-Bedingungen

Sofort stoppen, wenn Preflight/Basis abweicht, der alte Baseline-Canon unerwartet rot wird, der neue Vertrag außer der Shell weitere reale Befunde meldet, Route-/Packageänderungen nötig werden, Chromium eine Installation/einen Download erfordert, mobiler Overflow bleibt, ein fremder Gatefehler auftritt, Evidenz nicht ignoriert bleibt oder ein P0–P2-Befund offen bleibt.

## 9. Test-first RED — fehlende Validator-API

Um 12:20 CEST wurden ausschließlich die erlaubten Testflächen verändert:

- `scripts/canon-contract.test.mjs`: synthetischer Task-6-Vertrag mit gültiger Kontrolle und Negativfällen für Struktur, Text, Sichtbarkeit, Bedingtheit, AST-Spoofing, Klassen und Aggregation;
- `scripts/concept-shell-status.test.mjs`: fokussierter realer Shell-/Routenvertrag plus offline Mobile-Fragment für 320×568 und 390×844.

RED-Nachweis:

| Befehl | Ergebnis |
|---|---|
| `node --experimental-strip-types --test --test-name-pattern="Task 6 concept-shell contract" scripts/canon-contract.test.mjs` | **0/1, erwartetes RED** — `conceptShellStatusErrors(root)` ist `undefined` |
| `node --experimental-strip-types --test scripts/concept-shell-status.test.mjs` | **0/1, erwartetes RED** — dieselbe fehlende API; Chromium wurde vor der Assertion nicht gestartet |

Die Fehlerursache ist ausschließlich der noch fehlende Validatorvertrag. Es trat kein fremder Testfehler auf. Ein zunächst vom Ausführungs-Classifier beanstandetes unsicheres Chromium-Flag wurde aus dem neuen Test entfernt; der Test startet Browser künftig ohne `--no-sandbox`.

## 10. Validator-GREEN und echtes Repository-RED

Um 12:32 CEST wurde `conceptShellStatusErrors(root)` minimal mit TypeScript-Compiler-AST implementiert und unter `conceptShellStatus` in `canonCheckResults` fail-closed verdrahtet. Diagnosen enthalten nur `src/components/concept/shell.tsx` und stabile Regel-IDs.

| Prüfung | Ergebnis |
|---|---|
| fokussierter synthetischer Task-6-Vertrag | **1/1 PASS** |
| vollständige Canon-Fixturesuite | **32/32 PASS** |
| `npm run check:canon` | **erwartetes RED**, exakt `src/components/concept/shell.tsx: shell_status_region_count` |
| fokussierter realer UI-Test | **0/1 erwartetes RED**, exakt derselbe Shell-Befund; Browser noch nicht gestartet |

Damit ist die ursprüngliche False-green-Lücke geschlossen: Der Vertrag ist grün, das reale Repository ist ausschließlich wegen des tatsächlich fehlenden globalen Shell-Statusbereichs rot. Keine Route und kein Task-5-Inhalt wurde als Abweichung gemeldet.

## 11. Minimaler Shell-GREEN und lokale Gates

Um 12:41 CEST wurde ausschließlich am Anfang von `main#inhalt` ein zentraler, unbedingter `role="status"`-Bereich ergänzt. Er besitzt genau zwei direkte Absätze mit den Vertragsliteralen, die geforderten Breiten-/Wrapping-Klassen und eine bestehendem Portalstil entsprechende Border-/Elevated-Darstellung. Es wurde weder `aria-live` noch eine horizontale Scroll-/Nowrap-Klasse ergänzt.

Frische GREEN-Sequenz:

| Prüfung | Ergebnis |
|---|---|
| `node --experimental-strip-types --test scripts/concept-shell-status.test.mjs` | **1/1 PASS**; Chromium offline bei 320×568 und 390×844 ausgeführt und geschlossen |
| `node --experimental-strip-types --test scripts/canon-contract.test.mjs` | **32/32 PASS** |
| `npm run check:canon` | Exit 0 |
| `npm run typecheck` | Exit 0 |
| `npm run check:k1-control` | Exit 0 |
| fokussiertes ESLint auf vier Task-6-Dateien | Exit 0, keine Ausgabe |
| `git diff --check` | Exit 0; nur bekannte LF/CRLF-Hinweise |
| `git diff -- src/routes` | leer |
| Scope | exakt drei modifizierte + eine neue erlaubte tracked Task-6-Datei |

Tracked Scope nach GREEN:

```text
 M scripts/canon-contract.mjs
 M scripts/canon-contract.test.mjs
 M src/components/concept/shell.tsx
?? scripts/concept-shell-status.test.mjs
```

Kein Dev-Server, Build, Preview, `npm test`, Serverzugriff, Staging, Commit oder Push wurde ausgeführt.

## 12. Fokussiertes Spec-Review — FAIL, P2 primär reproduziert

Das frische, ausschließlich auf Task 6 begrenzte Spec-Review meldete einen P2-Vertragsbefund: Die Sichtbarkeitsprüfung war nicht fail-closed gegen Tailwind-Important-Klassen wie `!hidden` und gegen JSX-Spread-Attribute, die `hidden` oder `style` einschleusen können.

Primäre Reproduktion vor jeder Korrektur:

1. Negativfixture `className="… !hidden"` ergänzt → fokussierter Vertrag **0/1 RED**, tatsächliche Fehlerliste leer statt `shell_status_hidden`.
2. Negativfixture `{...{ hidden: true }}` ergänzt und separat zuerst ausgeführt → fokussierter Vertrag **0/1 RED**, tatsächliche Fehlerliste leer statt `shell_status_hidden`.

Beide vom Reviewer beschriebenen Bypässe sind damit unabhängig bestätigt. Der frühere lokale GREEN-Stand ist aufgehoben; Spec bleibt FAIL und Quality/Security bleibt gesperrt. Keine Shell- oder Routenänderung wurde für die Reproduktion vorgenommen.

## 13. Enge P2-Korrektur — GREEN

Um 12:58 CEST wurde ausschließlich der reproduzierte P2 korrigiert:

- Hidden-Klassenmatcher akzeptiert nun Tailwind-Important-Formen mit führendem oder abschließendem `!`, einschließlich Variantenpräfixen;
- jedes `JsxSpreadAttribute` im Statusunterbaum führt fail-closed zu `shell_status_hidden`.

Die beiden Negativfixtures bleiben als Regressionen erhalten. Frische Gates nach Korrektur:

| Prüfung | Ergebnis |
|---|---|
| fokussierter Task-6-Vertrag | **1/1 PASS**, beide neuen Regressionen eingeschlossen |
| fokussierter UI-Test | **1/1 PASS** |
| vollständige Canon-Suite | **32/32 PASS** |
| Canon / Typecheck / K1-Control | jeweils Exit 0 |
| fokussiertes ESLint | Exit 0 |
| Diff-Check | Exit 0; nur bekannte LF/CRLF-Hinweise |
| Route-Diff | leer |
| Scope | unverändert exakt vier tracked Task-6-Pfade |

## 14. Scoped Spec-Re-Review — PASS

Um 13:04 CEST bestätigte dieselbe scoped Spec-Reviewstufe die enge P2-Schließung:

- Tailwind-Important-Sichtbarkeitsformen werden erkannt;
- jedes JSX-Spread im Statusunterbaum fail-closed abgelehnt;
- beide Primärreproduktionen bleiben als fokussierte Regressionen erhalten;
- keine offenen P0–P2-Spezifikationsbefunde.

**Ergebnis: SPEC-PASS.**

## 15. Extra-High Quality-/Securityreview — FAIL, vier P2 primär reproduziert

Nach ausdrücklicher Extra-High-Bestätigung lief ein separates, adversariales Review ausschließlich über die vier Task-6-Dateien. Ergebnis: **QUALITY-FAIL** mit vier P2-Gruppen.

Alle Befunde wurden vor jeder Korrektur in der Primärsession test-first reproduziert:

| P2-Gruppe | Primärreproduktion | Ergebnis |
|---|---|---|
| dynamische Descendant-Sichtbarkeit + versteckter Ancestor | `className={true ? "hidden" : ""}` am Statusabsatz; `hidden` auf `main#inhalt` | beide Validator-Fehlerlisten leer statt `shell_status_hidden` |
| Important-/arbiträre Mobile-Konflikte | `!whitespace-nowrap`; `!min-w-[1000px]` am Statuscontainer | beide Validator-Fehlerlisten leer statt `shell_status_mobile_forbidden` |
| früher Komponenten-Return | `if (children === null) return null;` vor dem Shell-Return | Validator-Fehlerliste leer statt `shell_status_conditional` |
| Route-Regex zählt tote Vorkommen | Kommentar und String mit `<ConceptShell>` bei realem `<section />` | alter Zähler liefert `2` statt `0` |

Fokussierter Validatorlauf: **0/5 RED**, jeder der fünf Validatorbypässe unabhängig bestätigt.  
Fokussierter Route-Test: **0/1 RED**, Dead-Text-Bypass bestätigt.

Der frühere GREEN-/Spec-PASS-Stand bleibt als Spec-Evidenz erhalten, genügt aber nicht für Quality-PASS. Task 6 ist blockiert; kein Commit/Push.

## 16. Enge Quality-P2-Korrektur — GREEN

Um 14:52 CEST wurden ausschließlich die sechs roten Regressionen geschlossen:

1. Nichtliterales `className` im Statusunterbaum ist fail-closed `shell_status_hidden`.
2. Die JSX-Ancestorkette bis zur Komponentenrückgabe wird auf Spreads, `hidden`, `aria-hidden`, `style`, dynamische Klassen und concealment utilities geprüft.
3. Tailwind-Utilities werden varianten-/klammerbewusst normalisiert; führende/abschließende Important-Modifikatoren sowie widersprechende Standard-/arbiträre Width-, Min-/Max-Width-, Whitespace- und Overflow-X-Utilities führen zu `shell_status_mobile_forbidden`.
4. Die Komponente muss exakt einen direkten Top-Level-Return besitzen; ein früher oder verschachtelter Return führt zu `shell_status_conditional`.
5. Route-Vererbung wird per TypeScript-TSX-AST geprüft: autoritativer `ConceptShell`-Import, `Route`-Komponentenreferenz, genau ein direkter Return und `ConceptShell` als reale Root-JSX-Struktur. Kommentare/Strings zählen nicht.
6. Die Browserprüfung ist ausdrücklich nur ein offline Standalone-Nachweis für intrinsisches Textlayout bei zwei Viewports. Die realen Shell-Klassen und Konfliktmutationen werden durch den AST-Vertrag geprüft; eine vollständige App-/CSS-Abnahme wird nicht behauptet und bleibt Task 14.

Frische Gates:

| Prüfung | Ergebnis |
|---|---|
| fünf fokussierte Validatorregressionen | **5/5 PASS** |
| fokussierte Route-Regression | **1/1 PASS** |
| vollständiger fokussierter UI-/Route-Test | **2/2 PASS** |
| vollständige Canon-Suite | **37/37 PASS** |
| Canon / Typecheck / K1-Control | jeweils Exit 0 |
| fokussiertes ESLint | Exit 0 |
| Diff-Check | Exit 0; nur bekannte LF/CRLF-Hinweise |
| Route-Diff | leer |
| Scope | unverändert exakt vier tracked Task-6-Pfade |

## 17. Scoped Extra-High Quality-/Security-Re-Review — PASS

Nach einem folgenlosen API-Transportabbruch wurde dieselbe read-only Reviewstufe ohne Dateiänderung fortgesetzt. Um 15:03 CEST bestätigte sie:

- dynamische Descendant-Klassen und versteckte Ancestors fail-closed;
- Varianten-/Klammer-/Important-Normalisierung sowie Standard-/arbiträre Mobile-Konflikte geschlossen;
- Single-Return-Vertrag und Early-Return-Regression geschlossen;
- AST-basierte reale Route-Vererbung statt Kommentar-/Stringtreffern;
- Browseraussage korrekt auf Standalone-Intrinsik begrenzt;
- keine korrekturinduzierten P0–P2.

**Ergebnis: QUALITY-PASS.**

## 18. Frisches Abschlussgate — lokaler Task-6-PASS

Um 15:13 CEST wurde nach Spec-PASS und Quality-PASS die vollständige Sequenz erneut frisch ausgeführt:

| Prüfung | Ergebnis |
|---|---|
| fokussierter UI-/Route-Test | **2/2 PASS** |
| vollständige Canon-Suite | **37/37 PASS** |
| `npm run check:canon` | Exit 0 |
| `npm run typecheck` | Exit 0 |
| `npm run check:k1-control` | Exit 0 |
| fokussiertes ESLint | Exit 0 |
| `git diff --check` | Exit 0; nur bekannte LF/CRLF-Hinweise |
| Route-Diff | leer |
| tracked Scope | exakt vier autorisierte Task-6-Pfade |
| Branch / HEAD | `codex/aurelia-konsolidierung`, `c00fd83cdea707d5ed6587d5703b35cef0460fe6` |
| Divergenz | `0 2` gegen Tracking-Ref |
| Pflichtvorfahr | vorhanden, Exit 0 |

**K1 Task 6 ist lokal PASS und bleibt uncommittet.**

Absichtlich vorhandener tracked Worktree-Stand:

```text
 M scripts/canon-contract.mjs
 M scripts/canon-contract.test.mjs
 M src/components/concept/shell.tsx
?? scripts/concept-shell-status.test.mjs
```

Kein Staging, Commit, Amend oder Push. Das Publikations-Gate bleibt blocked; Servergates und `server_changes_started: false` bleiben unverändert.

## 19. Separat autorisierter Task-6-Commit

Um 18:28 CEST wurde nach ausdrücklicher Betreiberfreigabe ausschließlich die verifizierte Vier-Dateien-Fläche gestaged. `git diff --cached --check` war sauber; der staged Stat betrug 869 Einfügungen in exakt vier Dateien.

- Commit: `1185a68ed984b525686764f995513355701929e3`
- Nachricht: `fix: reconcile K1 concept portal`
- Co-Author-Zeile: vorhanden
- Parent: `c00fd83cdea707d5ed6587d5703b35cef0460fe6`
- Post-Commit-Worktree und Index: sauber
- Branch: drei Commits vor Tracking-Ref
- Push: nicht autorisiert und nicht erfolgt

## 20. Exakter nächster Entscheidungsrand

Task 7 ist vom Betreiber auf Reasoning `High` freigegeben, aber zu diesem Zeitpunkt noch nicht begonnen. Als Nächstes: frischer Task-7-Preflight, vollständige Lektüre des Task-7-Abschnitts und test-first Planung. Ein späterer Task-7-Commit und jeder Push benötigen getrennte Freigaben.
