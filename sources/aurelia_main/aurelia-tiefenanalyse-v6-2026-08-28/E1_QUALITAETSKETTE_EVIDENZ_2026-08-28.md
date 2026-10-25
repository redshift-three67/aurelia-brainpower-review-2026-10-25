# E1-Evidenz: Qualitätskette erstmals ausgeführt — 2026-08-28

Ausführung freigegeben durch den Betreiber (Schritt 1 der V6-Prioritätenkette).
Ort: `.worktrees/aurelia-konsolidierung` @ `aec827f` (node_modules vorhanden).
Nur Lese-/Prüfbefehle; nichts ins Repository geschrieben, kein Push, keine
Serveraktion. Diese Datei ist Analyse-Evidenz, keine Gate-Freigabe.

## Ergebnisse

| # | Befehl | Ergebnis | Interpretation |
|---|---|---|---|
| 1 | `npm test` (kanonisch) | Exit 0 — aber **0 von 9 Skript-Suiten geladen** (Glob unter cmd.exe-Script-Shell leer); nur 2 TS-Suiten: 24/24 PASS | **L3.4/K1-T7 empirisch bestätigt**: stille Nullabdeckung der 7 Skript-Suiten unter Windows; „grün" ist hier vacuous |
| 2 | Direkt: `node --test` über alle 9 `.test.mjs` | 214 Tests: **199 PASS / 15 FAIL** (Exit 1) | die echte Ausführung |
| 3 | Fehlschlag-Attribution | check-auth-invariant 2 · grok-pwa-plugin 9 · migration-plan 1 · with-app-env 2–3 | **alle 15 = Windows-Umgebungsartefakte** (EPERM bei `symlinkSync`, Pfad-/Spawn-Formate), keine Produktlogik |
| 4 | Task-3-Kern: `node --test scripts/check-push-graph.test.mjs scripts/check-project-control-k1.test.mjs` | **65/65 PASS, 0 FAIL** | K1-Task-3-Implementierung inkl. Dirty-Overlay testsaisonal grün |
| 5 | `npx tsc --noEmit` | **Exit 0, keine Fehler** | Typecheck erstmals mit frischer Evidenz **sauber** (V5: „nicht ausgeführt") |
| 6 | `npm run check:k1-control` | Exit 0, keine Befunde | K1-Steuerungsprüfung PASS |
| 7 | `git diff --check` (committed/index/worktree) | alle sauber | nur CRLF-Hinweis (`autocrlf`), kein Diff-Fehler |
| 8 | `node scripts/check-push-graph.mjs --base origin/codex/aurelia-vorbereitung --head HEAD --mode full` | **Exit 1** (dokumentiert erwartet), 15 Records: `absolute_user_path` 7 · `credential_like` 5 · `env_or_key_material` 1 · `operational_identity` 2 · `unscannable` 1 | deckungsgleich mit Migrationsdesign §3; **keine Fundwerte** in der Ausgabe — fail-closed-Diagnose live bestätigt |

## Folgerungen

1. **K1-Task 3 ist auf Testebene grün (65/65)** — der offene Schritt ist
   ausschließlich der dokumentierte Prozess: erneutes Spec-Review, danach
   Qualitätsreview. Keine Codeänderung ist durch diese Evidenz nötig.
2. **L3.4 wird präzisiert:** nicht „Tests schlagen fehl unter Windows",
   sondern gefährlicher: `npm test` läuft **grün mit 0 Skript-Tests**. Der
   K1-T7-Fix (explizite Dateiliste) ist damit prioritär belegt.
3. **Die 15 Windows-Fehlschläge** bilden die konkrete Aufgabenliste für
   K1-T7/T9 (Symlink-Ersatz, Pfadnormalisierung, Spawn-Shell) — alle in
   Test-Utilities, nicht in Produktmodulen.
4. **CRLF-Hinweis:** `core.autocrlf` ist auf der Workstation aktiv; die
   Dirty-Overlay-Dateien tragen aktuell LF. Das Migrationsdesign verbietet
   Normalisierung im Overlay — vor jedem `git add`/Checkout-Kontakt der zwei
   Scanner-Dateien ist der Hash-Vergleich Pflicht (SHA-256 laut Design §2).
5. **Scanner-Zählung live = Design-Dokumentation** (15 Records, identische
   Kategorienverteilung) — die Publikationsgrenze ist unverändert
   `blocked`; die 8-Bedingungs-Ausnahme des Migrationsdesigns bleibt der
   einzige autorisierte Pfad.
