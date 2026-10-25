# E6-Evidenz: Overlap-Enumeration-Umbau — vollständiger Lauf — 2026-08-28, Abend

**Diese Datei ist Ausführungs- und Review-Evidenz, keine Gate-Freigabe.**
Der Lauf wurde vom Betreiber namentlich freigegeben („Overlap-Lauf
freigegeben") und nach dem amendierten Plan
`2026-08-26-aurelia-k1-task3-overlap-enumeration-correction.md` ausgeführt.

## 1. Ergebnis in einem Satz

Der Scanner `scripts/check-push-graph.mjs` wurde auf die verbindliche
Head-first-Enumeration + bounded Value-Parser + wertfreie AST-Adjudikation
umgestellt; **Spec-Review PASS** (nach 1 Korrekturschleife, 2× P2) und
**Quality-/Security-Review PASS** (nach 2 Korrekturrunden, 1× P1 + 2× P2 + 1
Re-Open) — **52/52 Tests grün**, Performancevertrag O(n+c+a) gemessen
eingehalten. **Kein Commit** (Task 10 steht zur separaten Betreiberfreigabe).

## 2. Ablauf

| Phase | Ergebnis |
|---|---|
| Task 1 Baseline | ✓ Branch/Ancestors/Dirty=5, Design-Digest, Probe numeric=0/hyphen=0/overlap=1 exakt Planvorhersage |
| Task 2+3 RED | ✓ 7 Fehlschläge exakt die fehlende Verhaltensweise; Grenzmatrizen aufgenommen |
| Task 4+5 Implementierung | ✓ Scanner-Rewrite (Head-first, bounded Parser, wertfreie Candidates, fail-closed AST); 2 eigene Fehler korrigiert (Extension-Gate, Selbstauslösung → `namedCount`) |
| Task 4 Step 5 | **STOPP: systemischer Befund K1-T3-GRAMMAR-CONFLICT** — overlap=2 und invalid-head=1 unter einer Grammatik unvereinbar (`=` ist VALUE_CHAR → erster Wertlauf bis EOF). Empirisch belegt (Scratch-Probe) |
| Konsolidierung | Betreiber wählte **Option Y**: Greedy bleibt, Fixture-Erwartung 1→2 (fail-closed-Richtung), Design §8-Amendierung, **neuer Design-Digest `42ffc069…aa200`** |
| Task 6 Performance | ✓ 3 adversariale Tests mit 5-s-Timeouts → **46/46** |
| Task 7 Akzeptanz | ✓ K1-Control 0, Scope ⊆ 8 Dateien, Realgraph Exit 1, Paket/Status unberührt |
| Task 8 Spec-Review | FAIL (2× P2: 255-unquotiert-Quadrant + `+`-Boundary fehlten; Enumerationsfault- und Loader-Zweige ungetestet) → Korrektur (4 Tests + `loadModule`-Naht, 4 Zeilen, Default bitidentisch) → **Re-Review PASS** |
| Task 9 Quality-Review | Runde 1 FAIL: **QOV-01 P1** JWT-Rohmuster quadratisch (74/1122/4786/19583 ms; 1 MiB ≈ 19,6 s ≫ 5 s) · **QOV-02 P2** Blobcache ohne Pfad → fail-open Unterzählung (gleicher Blob a.ts+b.txt → exit 0 statt 1; Vorbestand) · **QOV-03 P2** §9.9-Stopp ungetestet. Alle drei primär reproduziert. |
| Korrektur Runde 1 | JWT-Segmente `{10,512}` + adversarialer Test + Doppelzuordnungstest → 52/52, **JWT 3/8/17/32 ms (~600×)** |
| Re-Review Runde 1 | QOV-03-Re-Open: mein Test-Fake fehlte `parseDiagnostics: []` → Test bestand aus falschem Grund (Wächter, nicht Stopp). Korrigiert + Kontrollassertion (1 Signatur → 0) |
| **Re-Review Runde 2** | **VERDICT: PASS, FINDINGS: none** — dynamisch belegt: Durchlauf betreten (5× isPropertySignature), Paar diskriminiert monoton, Regression 52/52, Hashes bestätigt |

## 3. Finale Zustände

- `scripts/check-push-graph.mjs` SHA-256 `34330a4e23bacb06eb94e0657cf9c1b0be5b41f163ea5a313b072efb96e0af41`
- `scripts/check-push-graph.test.mjs` SHA-256 `7213f5add6ad313704938ac2c92a44029410220e6a466154921ac29c3e2c2511`
- Correction-Design `42ffc0690caa40962a7e498f707b10fc53b705e2cb94d583d83b8c12730aa200` (amendiert, Option Y)
- Parent-Design `9c0e05adf870d40ff1686863fe866dd61e73ef6dbc63e680ffb363611f73323e` (unverändert)
- Suite 50→52 Tests, alle grün; Selfscan beider Quelldateien sauber
- Realgraph: Exit 1, 15 Records, byteidentische sichere Ausgabe (Gate bleibt blockiert und funktionsfähig)
- Working-Tree: 5 Dateien (2 Scanner + 3 K1-Dokumente), Staging leer, HEAD `0414146`, **nichts committed**

## 4. QOV-02-HANDOVER (Betreiberentscheidung, nicht blockierend)

**Befund:** Der Blobcache in `scanBlob` schlüsselt nur über `entry.blob`;
`classifyBlob` ist aber pfadsensitiv (AST-Suppression nur `.ts`/`.tsx`).
Messung (injiziertes git, gleicher Blob unter `same/a.ts` und `same/b.txt`):
`scanGraph` → `exitCode 0`, `findings []` — korrekt wäre `credential_like 1`
für `same/b.txt`. Die Erkennung hängt damit von der alphabetischen
Pfadreihenfolge ab (fail-open Unterzählung).

**Einordnung:** Cache UND Pfadsensitivität sind Vorbestand (committed,
String/Type-Bypass-Ära); der Overlap-Diff macht die Pfadsensitivität jedoch
tragend. Der Reviewer ordnete an: Fix (Cache-Schlüssel `blob\0pfad` oder
Text-Caching, ~3 Zeilen) berührt die eingefrorene Git-Enumerator-Region
(Design B §14) → braucht eigene Scope-Freigabe; sonst dokumentiertes
Restrisiko. **Beide Optionen stehen beim Betreiber offen.**

**Auflage des Reviewers für den späteren Commit:** Die Commit-Freigabe muss
diese Entscheidungsgrundlage (Befund, Messung, Design-B-§14-Bezug, beide
Optionen) oder einen eindeutigen Verweis auf diese E6 mit übernehmen.

## 5. Konsequenzen

1. **Beide PASS-Verdicts liegen vor** — nach Plan §14 ist Task 4 **eligible**
   (bleibt unaufgestartet bis zur Betreiberfreigabe).
2. Offen vor/bis zum ersten Task-4-Schritt:
   a. **Task 10 Commit-Freigabe** (Implementierungs-Checkpoint; Commit-Nachricht
      laut Plan Task 10 Step 2: „fix(security): enumerate overlapping credential
      candidates") inkl. QOV-02-Entscheidungsgrundlage,
   b. **K1-STATUS.md-Aktualisierung** (beide Verdicts + Evidenz-Bezeichnungen;
      Plan sieht dafür eine separate autorisierte Aktion vor),
   c. **Push-Entscheidung** für die neuen Commits (neue abgegrenzte Freigabe;
      Gate bleibt formal blocked — die 8-Bedingungs-Ausnahme des
      Migrationsdesigns war bereits einmal verbraucht),
   d. **QOV-02-Entscheidung** (i oder ii).
3. Kein Push, keine Serveraktion, kein History-Rewrite, keine
   Paket-/Status-/V3-Änderung ist erfolgt.
