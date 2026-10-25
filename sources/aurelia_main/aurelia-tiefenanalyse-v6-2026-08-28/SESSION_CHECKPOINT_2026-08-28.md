# Session-Checkpoint — 2026-08-28 (Fortsetzung nach Session-Abbruch)

Zweck: Bei erneutem Abbruch hier weiterlesen. Wird fortlaufend aktualisiert.

## Kontext

Vorbereitung-Session, V6-Prioritätenkette (`07_EMPFEHLUNGEN_UND_FAZIT_V6.md`).
Stufe 1 (E1 Qualitätskette) war vor dem Abbruch abgeschlossen
(`E1_QUALITAETSKETTE_EVIDENZ_2026-08-28.md`). Diese Session führt **Stufe 2**
aus: `gh` re-authentifizieren (N2) → GitHub-Evidenz (E2).

## Erledigt (diese Session)

1. **E2 Teil 1 fertig** — `E2_GITHUB_FERNZUSTAND_EVIDENZ_2026-08-28.md`:
   - `gh`-Keyring-Token frisch bestätigt ungültig (Konto `radiquant`).
   - `git ls-remote` intakt (Credential Manager); 5 Branches, 0 Tags, 0 PR-Refs.
   - Sync: nur `konsolidierung` 13 ahead / **0 behind** (FF-Push möglich);
     alle anderen Zweige identisch mit Remote.
   - Untracked: 15 Dateien/16.931 Z. (g0-governance-Worktree), 1 Datei/1.949 Z.
     (Migrationsplan, konsolidierung), 2 Dirty-Scanner-Dateien (Overlay, unangetastet).
   - `.github/` lokal ohne `workflows/`.

## In Arbeit

2. ~~`gh auth login` Device-Flow~~ — **ERLEDIGT (dritter Versuch,
   Task `bzlmqufd2`, Exit 0):** angemeldet als `redshift-three67` (aktiv,
   Scopes `gist, read:org, repo`). E2 Teil 2 komplett
   (`E2_GITHUB_FERNZUSTAND_EVIDENZ_2026-08-28.md`, Zeilen 10–16 + Folgerungen).
   **Stufe 2 der Prioritätenkette damit erfüllt.**

## Offene Restposten

- **`radiquant`-Keyring-Eintrag:** inaktiv, ungültig, und — neu belegt —
  **ohne Zugriff** auf das Repo (Collaborators = nur `redshift-three67`).
  Aufräumen mit `gh auth logout -h github.com -u radiquant` (nur lokale
  Hygiene) — wartet auf Bestätigung des Betreibers.
- **N10–N12 neu fassen:** Branch-Protection ist auf privaten Repos ohne
  GitHub Pro planbedingt blockiert (HTTP 403, E2 Zeile 15). Gleichwertiger
  Ersatz: K1-Push-Scanner als verpflichtender Pre-Push-Hook + FF-only-Regel.

## Später Abend: OVERLAP-TDD-LAUF — bei Task 4 Step 5 GESTOPPT (systemischer Befund)

- **Freigabe:** Betreiber gab den Overlap-Lauf namentlich frei.
- **Task 1** ✓ (Branch/Ancestors/Dirty=5 nach Mini-Amendierung von Step 1,
  Digest `c8a54422…`, Probe numeric=0/hyphen=0/overlap=1 exakt Plavorhersage).
- **Task 2 + 3** ✓ (Testdatei neu: Label-only-Helfer ohne Inhaltsleak,
  alle Call-Sites umgestellt, 8 neue Tests + Grenzmatrizen; **RED bewiesen:
  7 Fehlschläge** exakt die fehlende Verhaltensweise).
- **Task 4 + 5** (Scanner-Rewrite) implementiert: ASSIGNMENT_HEAD_PATTERN +
  CREDENTIAL_NAME_PATTERN, isCredentialValueCodeUnit (mit `:`),
  isUnquotedTerminator (amendierter Terminatorvorrat),
  parseBoundedCredentialValue (16..255, 256er-Kappe, Quoted-Branch),
  candidatePositionsValid, wertfreie Candidates (Object.freeze, .id),
  AST-Adjudikator auf Positionen + transienten Slices mit Vorab-
  Mehrdeutigkeitsablehnung und Doppelzuordnungs-Stopp. Zwei eigene Fehler
  dabei korrigiert: fehlende `.tsx?`-Extension-Gate (wiederhergestellt) und
  Selbstauslösung `namedCredentialCount=…` (→ `namedCount`, wie der Plan es
  vorschreibt).
- **Suite: 42/43 grün.** Einziges Rot: „an invalid earlier head never hides a
  later valid candidate" — **erwartet 1, gemessen 2**.
- **Systemischer Befund K1-T3-GRAMMAR-CONFLICT:** `=` ist Wertzeichen
  (Design §7), daher läuft der erste Wert in BEIDEN Fixtures bis EOF und wird
  gültig: overlap=2 ✓ (Planziel), invalid-head=2 ✗ (Planziel 1). Die beiden
  Plan-Erwartungen sind unter EINER Grammatik nicht gleichzeitig erfüllbar.
  Optionen vorbereitet (Y: Greedy bleibt, Test 1→2 fail-closed + Design-Notiz;
  A: scharfe Unquoted-Grenze an `= . /`, dafür `.Member`→sichtbar und
  unquoted-URL entfällt). → Betreiberentscheidung.
- **Kein Commit, keine Reviews (Task 8/9 gestoppt), Overlay-Disziplin gewahrt.**
- **Option Y vom Betreiber gewählt und vollzogen:** Design §8-Amendierung
  (Greedy-`=`-Wertläufe, Ketten zählen beide, Fixture-Erwartung verbindlich 2),
  Plan-Erwartung angepasst (Test umbenannt „a short earlier assignment and a
  later candidate are both counted", 2), **neuer Design-Digest
  `42ffc069…aa200`** (an 2 Stellen im Plan aktualisiert), Task-7-Allowlist um
  Migrationsplan ergänzt (8 Dateien). Testdatei angepasst.
- **Nach Konsolidierung: 43/43 grün.** Task 6 (3 Performance-Tests mit
  5-s-Timeouts + perf-Import): **46/46 grün.** Task 7 Akzeptanz PASS
  (k1-control 0, Scope ⊆ 8 erlaubte Dateien, Paket/Status unberührt,
  Diff/Index sauber, Realgraph Exit 1).
- **Neue Hashes:** Scanner `4e82c04b…bed3`, Test `e1f416f3…6213`. Working =
  5 Dateien (2 Scanner + 3 K1-Dokumente), Staging leer, HEAD `0414146`.
- **Task 8 Spec-Review: ERSTE RUNDE FAIL (2× P2, nur Testabdeckung),**
  Korrekturschleife ausgeführt (length-255-unquotiert + `+`-Boundary +
  Enumerations-Fault-Test via Symbol.matchAll-Override + Loader-Injektionsnaht
  `loadModule` (optional, Default bitidentisch, keine neuen Exporte) + 2
  Loader-Tests), **Re-Review: PASS, FINDINGS none.** Suite 50/50. Neue Hashes:
  Scanner `18314a91…b86ee`, Test `8ac3c008…32887`.
- **Task 9 Quality-Review: ERSTE RUNDE FAIL (1× P1 + 2× P2), primär reproduziert:**
  QOV-01 P1 JWT-Rohmuster quadratisch (74/1122/4786/19583 ms — `eyJ`-dichte
  punktfreie Blobs, `{10,}`-Segmente); QOV-02 P2 Blobcache nur über `blob`
  bei pfadsensitiver Klassifikation → gleicher Blob unter a.ts+b.txt = exit 0
  statt credential_like 1 (fail-open, VORBESTAND, Betreiberentscheidung);
  QOV-03 P2 §9.9-Doppelzuordnungsstop ungetestet.
  **Korrekturschleife:** JWT-Segmente `{10,}` → `{10,512}` (konsistent zu
  `{36,255}`/`{20,255}`) + adversarialer Test (punktlos eyJ-dicht 1 MiB,
  5-s-Timeout; JWT-Positivfall mit Punkten → 1) + Doppelzuordnungstest via
  loadModule-Fake (zwei positionsgleiche Signaturen → Suppression geleert →
  Raw-Count 1). **Danach: 52/52 grün, JWT 3/8/17/32 ms (linear, ~600×
  schneller), K1-Control 0, Realgraph Exit 1, Diff sauber.** Neue Hashes:
  Scanner `34330a4e…0af41`, Test `f5971cf6…e751`.
- **QOV-02 (Cache-Schlüssel) steht zur Betreiberentscheidung:** (i) Fix im
  Run (Cache-Schlüssel blob+pfad, ~3 Zeilen, fail-open-Schließung, aber
  eingefrorene Region → Amendierungsnotiz nötig) oder (ii) dokumentiertes
  Restrisiko für Folgelauf.
- **Re-Review Runde 2: PASS, FINDINGS none** — dynamisch belegt (Durchlauf
  betreten, 5× isPropertySignature; Paar-Assertionen monoton diskriminierend),
  Regression 52/52 frisch, Hashes bestätigt. **Alle drei QOV-Befunde
  geschlossen; beide PASS-Verdicts liegen vor. QOV-02 ist als Betreiber-
  entscheidung aus dem Lauf herausgereicht (nicht blockierend); Auflage für
  den Commit: Entscheidungsgrundlage oder E6-Verweis mit übernehmen.**
- **VOLLSTÄNDIGE EVIDENZ: `E6_OVERLAP_LAUF_2026-08-28.md`.** Finale Hashes:
  Scanner `34330a4e…0af41`, Test `7213f5ad…2511`, Design `42ffc069…aa200`,
  Parent `9c0e05ad…323e`. HEAD `0414146`, 5 Working-Tree-Dateien, Staging
  leer, kein Commit.
- **PUSH-VORBEREITE (Nacht):** QOV-02 gefixt (Cache-Schlüssel `blob\0pfad`,
  Regressionstest — 53/53 grün) · Design-QOV-02-Amendierung (Digest
  **`6adb7a71…b6c54`**, Plan an 2 Stellen aktualisiert) · K1-STATUS
  aktualisiert (Task 3 abgeschlossen, beiderseits PASS, Task 4 eligible) ·
  **4 Commits: `1a4a114` fix(scanner), `d902541` docs(Verträge),
  `66e7e57` docs(Status), `7fcd461` docs(Plan-Entschärfung)** · Working-Tree
  komplett sauber.
- **PUSH BLOCKIERT vom Gate (korrekt):** Graphvergleich base=`0414146`:
  **added_records=1** — credential_like auf dem Plan-Blob von `d902541`
  (Fixture-Literal `password=https://example.com/` in meinem Step-2b-Text;
  Spitze ist defused, aber der Vollgraph erreicht den alten Blob). Synthetic-
  harmlos (example.com = Dokumentationsdomain), aber formell ein neuer
  Record. **Optionen beim Betreiber:** (1) Neuaufbau der UNPUBLIZIERTEN
  lokalen Kette ab `0414146` (soft/mixed-Reset + saubere Recommit-Sequenz
  mit defused Plan — braucht ausdrückliche Reset-Ausnahme; Sicherheitsbranch
  zuerst) → added=0 ✓ [EMPFEHLUNG]; (2) Push mit +1 dokumentiertem Record
  (zweite Gate-Ausnahme — schlechter Präzedenz); (3) nicht pushen, lokal
  behalten (vollständig gesichert).
- **Nacht-Finale: PUSH 2 ERFOLGT** — Nach Gate-Block (added=1 durch Plan-
  Fixture-Blob in der d902541-Zwischenhistorie) autorisierte der Betreiber
  **Option 1 (Neuaufbau der unveröffentlichten Kette)**: Sicherheitsbranch
  `backup/pre-push-7fcd461` (bleibt bestehen — in künftige Branch-Set-
  Prüfungen aufnehmen!), mixed-Reset auf `0414146`, **Baum-Identität
  verifiziert (leerer Diff gegen 7fcd461)**, saubere Recommit-Sequenz:
  `4d258ae` fix(scanner) · `62dabb6` docs(Verträge, defused Plan) ·
  `e6f3089` docs(Status). **Graphvergleich: 15/15, added=0, removed=0 ✓ ·
  PUSH `0414146..e6f3089` (FF, 1 Ref, CAS-Hook `94e59f72…`, Beleg
  `383c6d31…`) ✓ · Post-Push: Working-Tree komplett sauber.**
- **K1 TASK 3 DAMIT VOLLSTÄNDIG ABGESCHLOSSEN** (beiderseits PASS,
  implementiert, committed, gepusht). **Task 4 ist eligible** (Betreiber-
  Freigabe für den Start erforderlich). QOV-02 ist GESCHLOSSEN (Fix im Lauf
  + Regressionstest + Design-Amendierung).
- Live-View aktualisiert (Nacht-Eintrag, K1-Zeile, Kette).

## Späterer Abend: E5 — verkürzter Migrationspfad + DER autorisierte Push (ERLEDIGT)

- **Betreiber-Klärungen:** Workstation = nur Dev; Debian-Server beim Provider,
  ausschließlich RDP/WinSCP, keine USB-Medien; lokale Sicherungen **vollständig
  inkl. `.git`** → Kapselaufgaben (Tasks 2–7, 10) per Plan-Amendierung
  entfallen; Memory `infrastruktur-topologie` angelegt.
- **Ausgeführt (alles pwsh 7.5.4, Skripte im Claude-Temp `mig/`):**
  - Task 1: Plan-Commit `2f86d6b` (4 Schritte grün)
  - Shortened-path-Amendierung: Commit `0414146` (nur Plan-Dokument)
  - Task 8 S1–S5: komplett PASS. Identität/privat ✓, Fetch nur konsolidierung,
    Remote `029bdce` unverändert, FF ✓, Dirty exakt 5, Scanner-Hashes ✓,
    G0 15 ✓, Branches 5 ✓, Worktrees 4 sauber, kein Stash, **Ignored frisch
    81/f7a77c7b…**, **Graphvergleich exakt Plavorhersage: 15/15, added=0,
    removed=0**
  - Task 9: **PUSH ERFOLGT — `029bdce..0414146`, Fast-Forward, genau 1 Ref,
    kein Force**; isolierter Pre-Push-CAS-Hook (`ebb28572…`), unabhängige
    Rücklesung ✓, Receipt (`2cac8441…`) im lokalen Temp, Post-Push-Prüfungen
    alle grün (Overlay 5 Dateien unverändert, G0 15, Ignored unverändert)
- **Bilanz:** 15 Commits auf GitHub (privat); konsolidierung lokal = remote
  `0414146`; Publikations-Gate weiter blocked & funktionsfähig (keine neuen
  Records); SPOF für committeten Zustand beseitigt; E5-Dokument + Live-View
  aktualisiert.
- **Nächster Schritt:** Betreiberfreigabe für den Overlap-TDD-Lauf; danach
  G0-SRV-0 remote-tauglich entwerfen.

## Abend ergänzt (Live-View + Stufe-5-Vorbereitung)

- **MIGRATION TASK 1 ERFÜLLT (28.08. Abend, freigegeben):** Plan-Dokument
  committed als `2f86d6b` („docs: plan Linux migration recovery checkpoint",
  Parent `aec827f`, exakt 1 Datei). Vier Schritte wortgetreu via pwsh 7.5.4
  (Skripte im Claude-Temp `mig/task1-step{1..4}.ps1`): Scope exakt
  (6 Arbeitsbaum-Einträge), kein Indexinhalt, `git diff --check` 0, keine
  Unvollständig-Marker, Scanner-Klassifikation des Plans `[]`, Post-Commit:
  Staging leer, Restschmutz = 5 autorisierte Dateien, Scanner-Hashes
  verifiziert. **Damit: `aec827f` ist Vorfahre von HEAD (2f86d6b) —
  Ausführungsvoraussetzung für Tasks 2–9 erfüllt.** Konsolidierungszweig nun
  **14 Commits unpushed**.
- **Vor Task 1 amendiert:** Task 1 Step 1 (erwarteter Arbeitsbaum um 3
  Overlap-Amendierungsdateien erweitert) und Step 4 (Restschmutz 2→5, Regex
  erweitert, Test-Hash `ce9e3a6d…`→`81607e33…`), mit Amendment-Notiz.

- **Live-View aktualisiert** (`aurelia-status-live.html`): Session-Verlauf
  E1–E4, KPI/K1/Risiko/Prioritätenkette auf Abendstand, neue Mermaid-
  Unterseiten verlinkt. **Stehende Arbeitsweise im Memory vermerkt**
  (`live-view-und-diagramme.md`): nach jedem Fortschritt akkurat nachziehen.
- **Neue Mermaid-Unterseiten** (Betreiberwunsch): `…-phasen.html`
  (Phasenlandkarte + Prioritätenkette), `…-gates.html` (G0-SRV-Folge +
  K1-Kette), `…-task3.html` (Review-Zustandsmaschine + Option-B-Begründung).
  Mermaid via CDN → Internet nötig.
- **Empfehlung ausgesprochen + vom Betreiber getragen:** Stufe 5
  (Replikationskapsel) VOR dem Overlap-TDD-Lauf.
- **Migrationsplan vorbereitet:** Required operator inputs gelesen — 2
  physisch unabhängige, verschlüsselte externe Medien (BitLocker
  `ProtectionStatus On` oder verifizierbares Äquivalent) + nicht-geheime
  Labels sind Betreibervorbedingung. Task 1 = Commit des Plans (nur
  Dokument), Tasks 2–9 in EINER durchgehenden PowerShell-7-Session
  (Orchestrator = primäre Instanz), Task 9 FF-Push separat freizugeben.
  **Amendierung vollzogen:** `scanner_test_sha256` `ce9e3a6d…` →
  `81607e33…` (Testdatei änderte sich durch E3-Korrekturschleife; Scanner
  unverändert `32c0b5b4…`); übrige Identitäten = Laufzeitverifikation gemäß
  Task 2/3 (Abweichung = Stop, keine Wertanpassung im Lauf).

## Danach (Kette)

3. **Stufe 3 LÄUFT (seit Nachmittag):** Fokussiertes Spec-Review K1-Task-3
   nach QUALITY-ROUTING Ablauf B und den Decision-Contracts der Pläne:
   - Vertragslage geklärt: Vertrag A = TDD-Korrektur P1-01/P1-02/Q-01
     (**committed** zwischen `b84b72a` und `e930aab`), Vertrag B =
     String/Type-Bypass-AST-Adjudikation (**uncommitted**, ist das Dirty-
     Overlay). Overlap-Enumeration-Korrektur (CRED-*) ist **nicht** Bestandteil
     — nur Plan, nicht implementiert; ihre „design-start hashes" stimmen
     bitidentisch mit den aktuellen Overlay-Hashes:
     `32c0b5b4…` (mjs) / `ce9e3a6d…` (test.mjs) — Overlay seit Planlegung
     unverändert.
   - Review-Diff-Basis: `git diff b84b72a -- <2 Scanner-Dateien> + K1-STATUS.md`.
   - Frische Evidenz (28.08., vor Reviewer-Start): Scanner-Suite **32/32
     PASS** (Exit 0), `check:k1-control` Exit 0, Real-Graph Exit 1 mit 15
     Records (nur category/blob/path/count, keine Werte), nackter CLI Exit 2,
     Staging leer, Dirty-Scope = genau 2 Dateien, Design-Digest B = `9c0e05ad…`
     stimmt mit Vertrag B überein.
   - **Spec-Review DURCHGEFÜHRT, Ergebnis: FAIL** (dokumentiert in
     `E3_K1_TASK3_SPEC_REVIEW_2026-08-28.md`): unabhängiger Reviewer + primäre
     Verifikation einig. 3 Findings, alle bestätigt:
     `K1-T3-NEW-01` (P1, gequotet+`=`-Erkennung hat keine Regression-Test-
     abdeckung; Vorgängerstand b84b72a war gequotet-only), `K1-T3-NEW-02`
     (P2, escaped-Quote-Strings und exakt-1-MiB-Normallfall ungetestet;
     Design B §10 Z. 262/277), `K1-T3-NEW-03` (P2, Plan-B-Scope-Assertion
     veraltet: 5 statt 4 Dateien seit e930aab wegen autorisierter Doc-
     Checkpoints — Prozessbefund, kein Codefehler).
   - **Nächster Schritt: Korrekturschleife** (vom Betreiber am 28.08.
     freigegeben) — **DURCHGEFÜHRT**, Working-Tree only, kein Commit:
     NEW-01: neuer Test „quoted equals-separated …" (gequotet + `=`, double/
     single, count 1, Non-Leakage). NEW-02: escaped-Quote- + Backslash-
     Fixtures im Strings/Templates-Test; `data/exact-limit.dat` exakt
     1_048_576 Bytes mit synth. Token, Assertionen „nicht unscannable +
     credential_like-Fund". NEW-03: beide `$allowedSinceStart`-Arrays in
     Plan B erweitert (3 autorisierte Docs) + Notizen NACH den Codeblöcken
     (erstes Einfügen hatte einen PowerShell-Block zerschnitten — repariert,
     Struktur verifiziert).
   - Frische Evidenz nach Korrektur: Suite **33/33 PASS**, K1-Control Exit 0,
     Realgraph Exit 1 / 15 Records / Shape-Audit 0 unsichere Zeilen
     (Hinweis: „credential_like 5" in E1 = Count-Summe inkl. server.ts
     count=2; Zeilenzahl ist 4 — kein Record verschwunden), `git diff
     --check` 0, Staging leer, mjs-Hash unverändert `32c0b5b4…`, test.mjs
     neu `81607e33…`.
   - Zähne-Beweis NEW-01: TEMP-Klon mit mutierter quoted-Alternative
     ({16,255}→{32,255}) → neuer Test schlägt fehl; echter Worktree grün.
     Temp-Klon gelöscht.
   - **Scoped Re-Review: PASS, FINDINGS none** (E3 §7 dokumentiert; primäre
     Instanz hat Kernbehauptungen gegen eigene Messungen bestätigt).
     **Spec-Review Task 3 = PASS nach einer Korrekturschleife.**
   - **Qualitäts-/Securityreview DURCHGEFÜHRT — nicht bestanden** (dokumentiert
     in `E4_K1_TASK3_QUALITY_REVIEW_2026-08-28.md`, Repro-Skript
     `repro_quality_findings_2026-08-28.mjs`): Reviewer meldete „PASS" mit
     4 Findings; P0–P2 blockieren aber (QUALITY-ROUTING §3.6). Primäre
     Reproduktion (Design B §13.4): **NEW-01 P1 bestätigt** (Terminatorklasse
     zu eng: Credential in Stringliteral/JSON/URL-Wert = 0 Befunde),
     **NEW-02 P2 bestätigt** (`--password=`-Form verloren; `x--password=` als
     Gegenprobe 1), **NEW-03 P2 bestätigt und gemessen** (quadratisches
     Backtracking: 64→512 KiB = 450 ms→28 907 ms, ×4 pro Verdopplung,
     1 MiB ≈ 2 min/Blob; GIT_TIMEOUT_MS erfasst classifyBlob nicht),
     **NEW-04 P2 WIDERLEGT** (`.Member`-Kandidat existiert — .txt-Probe=1 —
     und wird mit `;` echt per AST unterdrückt; Testfall beweist genau seine
     Aussage). Positiv: AST-Pfad fail-closed sauber, kein Value-Leak,
     typescript-Require sicher verankert.
   - **KONSOLIDIERUNGSSTOPP (QUALITY-ROUTING §4):** Alle 3 bestätigten
     Findings haben dieselbe Wurzel (Lookahead), den der geplante
     Overlap-Umbau ersetzen würde. NEUER VERTRAGSKONFLIKT: Das Overlap-Design
     testet trailing-quote/bracket/paren als erwartet 0 und nutzt dieselbe
     enge Terminatorklasse — kollidiert direkt mit NEW-01-Erwartung.
     **Betreiberentscheidung offen:** Option A (jetzt fixen + Overlap-Design
     amendieren) / Option B (Findings in Overlap-Umbau überführen, dessen
     Design VORab amendieren) / Option C (Stopp, nur Verträge konsolidieren).
     Task 4 bleibt in jeder Option gesperrt; kein Commit, kein Push;
     Publikationsgate weiter blockiert und funktioniert (Exit 1).
   - **Option B VOLLZOGEN (E4 §4):** Overlap-Design amendiert (§1.1, §7
     VALUE_CHAR + `:`, §7.2 erweiterter Terminatorvorrat, §12-Matrix-Flip,
     §11 Performance-Abnahme) — neuer Design-SHA-256
     `c8a54422e2c13a753404ef25f033b06038b741698f5174722816d69aaef89736`.
     Overlap-Plan amendiert (Digest, Run-Start-Hashes, HEAD-Ancestor statt
     Gleichheit, Task 2 Step 2b E4-Regressionstests, Task 3 Fixture-Flip,
     Task 7 Allowlist, Stopbedingung). Integrität geprüft: Fences gerade,
     Digest konsistent, K1-Control 0, diff --check 0, Staging leer.
   - **NÄCHSTER SCHRIFT (Betreiberfreigabe nötig):** TDD-Implementierungs-
     lauf des Overlap-Umbaus nach dem amendierten Plan (namentlich benennen!).
     Danach: fokussiertes Spec-Review + Quality-Review des Umbaus gemäß
     Plan Task 8/9; erst beide PASS → Task 4 eligible. Danach Stufe 5
     (Replikationskapsel — dringend, Linux-Neuinstallation geplant).

4. Frühere Stufe-3-Notiz: K1-Task-3 Spec-Review terminieren (danach
   Qualitätsreview; Eskalationsfenster in QUALITY-ROUTING ergänzen, N4).
4. Stufe 5-Vorbereitung: Replikationskapsel A→B→C (dringend wegen geplanter
   Linux-Neuinstallation; 16.931+1.949 Zeilen Pläne existieren nur einmal).

## Feste Regeln (nicht verhandeln)

- Nur lesend/prüfend; kein Push, kein Fetch, kein Merge, keine Serveraktion.
- Die 2 Dirty-Scanner-Dateien im konsolidierungs-Worktree sind das
  dokumentierte Overlay — **nicht** stagen, checkouten, normalisieren;
  vor jedem git-Kontakt Hash-Vergleich (SHA-256, Migrationsdesign §2).
- Evidenz nur in `aurelia-tiefenanalyse-v6-2026-08-28/` (gitignored), nicht
  ins Repository schreiben.
- Alles nur auf dieser Workstation (SPOF) — deshalb Checkpoint-Datei.
