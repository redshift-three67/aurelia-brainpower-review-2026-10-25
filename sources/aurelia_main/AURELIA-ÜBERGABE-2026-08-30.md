# AURELIA — Session-Übergabe

**Zeitstempel:** 2026-08-30, 17:39 CEST
**Zweck:** Exakte Fortsetzung der K1-Kanonkonsolidierung an der Stelle „Task 4 abgeschlossen, Task 5 als nächster Schritt".
**Nutzung:** Diesen Wortlaut als erste Nachricht in die neue Session geben (oder die neue Session diese Datei lesen lassen). Ergänzend lädt die Session das projektpersistente Memory (`aurelia-projektstand`, `infrastruktur-topologie`, `live-view-und-diagramme`).

---

## Kickoff-Wortlaut (zum Einfügen in die neue Session)

> Lies zunächst `AURELIA-ÜBERGABE-2026-08-30.md` im Projektroot vollständig und setze das Projekt exakt an der dort beschriebenen Stelle fort: K1 Task 4 ist abgeschlossen (Commit `1257283`, ungepusht), nächster Schritt ist **Task 5 (Aktive Dokumente und Konzeptdaten auf K1 konsolidieren)** nach Masterplan `docs/superpowers/plans/2026-08-25-aurelia-k1-canon-consolidation.md` ab Zeile 538. Arbeite im Worktree `.worktrees/aurelia-konsolidierung`, Branch `codex/aurelia-konsolidierung`, akkurat, präzise und stabil nach den dort festgelegten Disziplinen (Spur B, TDD, kein Push/Reset/Rewrite ohne meine ausdrückliche Freigabe). Alle Grundlagen, Offenpunkte und Regeln stehen in der Übergabedatei.

---

## 1. Ort, Branch, exakter Zustand

- **Projektroot:** `C:\Users\Hubert111\Documents\ChatGPT\Aurelia`
- **Arbeitsverzeichnis für alle K1-Arbeiten:** `C:\Users\Hubert111\Documents\ChatGPT\Aurelia\.worktrees\aurelia-konsolidierung`
- **Branch:** `codex/aurelia-konsolidierung`
- **Lokaler HEAD:** `1257283` („test: specify fail-closed K1 canon") — **1 Commit ungepusht**
- **Remote `origin/codex/aurelia-konsolidierung`:** `e6f3089` (Stand nach Push 2 am 28.08.)
- **Working-Tree:** sauber; **erwarteter einziger ungetrackter Eintrag:** diese Übergabedatei (lokale Ignore via `.git/info/exclude` — Eintrag `/AURELIA-ÜBERGABE-*.md`; falls `git status` sie trotzdem zeigt: `git check-ignore -v` prüfen)
- **Sicherheitsbranch:** `backup/pre-push-7fcd461` — **bewusst vorhanden, nicht löschen**; in künftige Branch-Set-Prüfungen aufnehmen
- **Vorfahr-Regel:** `8706186af01e10e4253e25abb31bf3577110dae4` muss Vorfahre von HEAD sein

## 2. Verifizierte Gates (Stand der Übergabe)

| Gate | Zustand |
|---|---|
| `node --experimental-strip-types --test scripts/canon-contract.test.mjs` | 8/8 PASS |
| `node --test scripts/check-push-graph.test.mjs` | 53/53 PASS |
| `npm run check:canon` | **Exit 1 — vertraglich korrekt** (RED-Evidenz für Task 5/6, s. §4) |
| `npm run check:k1-control` | Exit 0 |
| `npm run typecheck` | Exit 0 |
| `node scripts/check-push-graph.mjs --base origin/codex/aurelia-vorbereitung --head HEAD --mode full` | Exit 1, 15 Records, nur `category/blob/path/count` — **Publikations-Gate formal blocked und funktionsfähig** |

## 3. Was abgeschlossen ist (Kurzhistorie mit Evidenz)

Alle Evidenz im gitignorierten Ordner `aurelia-tiefenanalyse-v6-2026-08-28/`:
`00…08_*_V6.md` (V6-Analyse), `E1…E6_*.md` (Ausführungs-/Review-Evidenz),
`SESSION_CHECKPOINT_2026-08-28.md` + `SESSION_CHECKPOINT_2026-08-29.md`
(Vortages-/Vortag-Nachweise), `aurelia-status-live.html` (Chrome-Live-View,
**nach jedem Fortschritt aktualisieren — stehende Arbeitsweise**) samt drei
Mermaid-Unterseiten (`…-phasen.html`, `…-gates.html`, `…-task3.html`),
`repro_quality_findings_2026-08-28.mjs`.

- **28.08.:** E1 Qualitätskette · E2 gh-Re-Auth (Konto `redshift-three67`; Achtung Konto-Split, alte `radiquant`-Reste vom Betreiber entfernt) · E3/E4 Task-3-Reviews des Altbestands · E5 Replikation verkürzt: **Push 1 `029bdce..e6f3089`** (CAS-Hook, added=0) · E6 Overlap-Lauf: Scanner-Rewrite (Head-first-Enumeration, bounded Value-Parser, wertfreie AST-Adjudikation), GRAMMAR-CONFLICT → **Option Y** (Greedy-`=`-Wertläufe, Ketten zählen beide), Spec- + Quality-Review je FAIL→Korrektur→**PASS**, JWT-Quadratik gefixt (`{10,512}`; 19,6 s → 32 ms/1 MiB), QOV-02 gefixt (Cache-Schlüssel `blob\0pfad`) · Gate-Block durch Plan-Fixture-Blob → **Option 1: unveröffentlichte Kette neu aufgebaut** (Baum-Identität verifiziert; Sicherheitsbranch) → **Push 2 `0414146..e6f3089`, added=0** ✓
- **29.08.:** **K1 Task 4** abgeschlossen (Commit `1257283`): `src/lib/concept/canon.ts` (K1_CANON), `scripts/canon-contract.mjs` (Validator + ACTIVE_FILES 64 + EXCLUDED_PREFIXES + Pflichtfamilien D,C,X,U,K,H,O,WV), `scripts/canon-contract.test.mjs` (8 Tests), `package.json` (`check:canon`). RED→GREEN 8/8; Real-Check vertragsgemäß Exit 1.

## 4. NÄCHSTER SCHRITT: Task 5 — Aktive Dokumente und Konzeptdaten auf K1 konsolidieren

**Vertrag:** Masterplan, Abschnitt „### Task 5: Aktive Dokumente und Konzeptdaten auf K1 konsolidieren" (ab Zeile 538 der Datei `docs/superpowers/plans/2026-08-25-aurelia-k1-canon-consolidation.md`) — vor Beginn vollständig lesen.
**Ziel:** `npm run check:canon` muss am Ende von Task 5 **Exit 0** erreichen (Task 6 leitet das Portal ab; Task 14 macht die Gesamtverifikation).

**Konkrete offene Befundliste (`npm run check:canon`, Stand der Übergabe):**

1. **10 aktive Textverletzungen** (alle in `src/routes/*.tsx`):
   - `debian_or_bookworm` ×6: `identitaet.tsx`, `index.tsx`, `live.tsx`, `repos.tsx`, `roadmap.tsx`, `sicherheit.tsx`
   - `webrtc_or_video` ×3: `live.tsx`, `roadmap.tsx`, `sicherheit.tsx`
   - `two_by_one_tb` ×1: `index.tsx`
   - `unqualified_phase_1` ×1: `offen.tsx`
   Bereinigung = Canon-konforme Umformulierung (Betriebssystem ist `Ubuntu Server 24.04.4 LTS amd64`; Storage `2×2 TB WD_BLACK SN850X`; WebRTC/Video `excluded`; Phase-1-Formulierung qualifizieren). Erst prüfen, ob `src/routes/…` tatsächlich aktive Präsentationstexte sind, dann editorial säubern — keine sinnentstellenden Streichungen.
2. **ID-Dopplungen:** `D08–D12 doppelt`, `K1–K5 doppelt` — Ursache: die Extraktion (`\bid:\s*"([A-Z]+)(\d+)"` über alle aktiven `.ts/.tsx`) zählt Wiederholungen derselben ID (z. B. Zusammenfassung + Liste). **In Task 5 klären:** Duplikate in den Daten auflösen ODER Extraktion verfeinern (z. B. Deduplizierung pro Familie — Vertragsauslegung dokumentieren).
3. **H-ID fehlt (fail-closed):** Der Vertrag fordert H als Pflichtfamilie; die `ID_FAMILIEN`-Legende (`src/lib/concept/id-legend.ts`) kennt stattdessen `L` (Lovable). **Klärung nötig:** H-Definition ergänzen (was ist H? vermutlich „Harmonisierung" — im Design `7de43db`/§23-id-schema nachlesen) oder Legende/Vertrag anpassen — Entscheidung dokumentieren.

**Review-Disziplin (Spur B, nach Masterplan §3 gilt für Kanon-Aufgaben Reviews bei Spur-B-Eskalation):** Task 5 ist redaktionell, berührt aber den Produktkanon → konservativ: nach GREEN + `check:canon` Exit 0 ein fokussiertes Spec-Review + Qualitätsreview durch frische Instanzen (Muster aus E3/E6), bevor committet wird.

## 5. Danach (Kette, Masterplan)

Task 6 (Portal/Schale auf K1 ableiten) → Task 7 (fail-closed Test-Runner) → Task 8 (Auth-/Migration-/PWA-/Windows-Testverträge) → Task 9 (Vite-CLI) → Task 10 (Auth-Invarianten) → Task 11 (Browser-Smoke) → Task 12 (Plattform-Assets, external_blocker) → Task 13 (Lint) → Task 14 (Integration, Browserabnahme, `K1-VERIFICATION.md`, Gesamt-Diff durch zwei unabhängige Reviewer).
**Parallel/anschließend:** `G0-SRV-0`-Nachweis **remote-tauglich** entwerfen (Debian-Server beim Provider, ausschließlich RDP + WinSCP, keine USB-Medien; lokale verschlüsselte Medien + WinSCP-Pull als Restaurationsweg).

## 6. Feste Disziplinen (nicht verhandeln)

1. **Nur synthetische Daten.** Kein Push, kein Merge/Rebase/Reset/History-Rewrite, kein `git add -f`, kein Serverzugriff, kein `npm run build`, keine Force-Operationen — alles nur mit separater ausdrücklicher Betreiberfreigabe. **Auch Commits brauchen die Freigabe** (etabliertes Muster: Freigabe je Arbeitspaket).
2. **Spur B für Kanon-/Sicherheitsflächen:** Vertrag schriftlich, TDD RED/GREEN, fokussiertes Spec-Review + separates Quality-Review durch frische Instanzen mit wörtlichem Decision-Contract; primäre Instanz reproduziert jeden Befund dynamisch (Minimalprobe + Messung), bevor er akzeptiert wird.
3. **Fail-closed überall:** fehlende Evidenz ist FAIL; unklare Risikoklasse → Spur B; Arbeit stoppt zur Konsolidierung bei systemischen Befunden (QUALITY-ROUTING §4).
4. **Publikations-Gate:** bleibt formal **blocked** (15 Records, keine neuen). Jeder Push braucht eine neue abgegrenzte Freigabe + Disziplin: Graphvergleich (`added_records=0 && removed_records=0`), isolierter Pre-Push-CAS-Hook, ein Ref, kein Force, Rücklesung, Beleg. Muster: E5/E6.
5. **Historische Flächen unangetastet:** V3-Evidenz, Preview-Credential, `external-analyses/**/source/`, historische Zweige (`g0-governance`, `kanon-implementation` sind Referenzen, keine Merge-Ziele).
6. **Evidenz nur** in `aurelia-tiefenanalyse-v6-2026-08-28/` (gitignored) — **nichts Analysisches ins Repository.**
7. **Live-View pflegen:** nach jedem Fortschritt `aurelia-status-live.html` + Mermaid-Unterseiten aktualisieren (stehende Betreibervorgabe).

## 7. Schlüsselreferenzen

| Objekt | Wert/Pfad |
|---|---|
| Lokaler HEAD | `1257283` (ungepusht; Remote `e6f3089`) |
| Sicherheitsbranch | `backup/pre-push-7fcd461` |
| Overlap-Korrekturdesign (amendiert) | SHA-256 `6adb7a71a6021bc1828c7606118af8eec3d7c40c9ad55b563445bdf5047b6c54` |
| Parent-Design (String/Type-Bypass) | SHA-256 `9c0e05adf870d40ff1686863fe866dd61e73ef6dbc63e680ffb363611f73323e` |
| Scanner / Test | `34330a4e…0af41` / `7213f5ad…2511` (Stand E6; QOV-02-Fix + Kanon-Ära nicht darin enthalten — neue Hashes bei Bedarf frisch messen) |
| Masterplan | `docs/superpowers/plans/2026-08-25-aurelia-k1-canon-consolidation.md` (§0 Rahmen, §1 Matrix, §3 Review-Zuordnung, Tasks 4 ab Z. 385, Task 5 ab Z. 538) |
| QUALITY-ROUTING | `docs/project-control/QUALITY-ROUTING.md` |
| Status-Ledger | `docs/project-control/K1-STATUS.md` (Task 3 abgeschlossen; Task 4-Abschluss noch NICHT eingetragen — mit dem nächsten Dokument-Commit nachziehen) |
| Gate-Statusautorität | `docs/project-control/ground-zero/GATE-STATUS.md` (0/13, `G0-SRV-0` offen) |
| Offene Übertragungsaufgabe | QOV-02-Entscheidungsgrundlage ist in den Commits/E6 dokumentiert; E6-Referenz bei künftigen Commits mitführen |

## 8. Bekannte Restposten (keine Blocker für Task 5)

1. Commit `1257283` ist ungepusht — Push-Entscheidung beim nächsten abgegrenzten Push mit vollem Gate-Disciplin-Paket.
2. K1-STATUS: Task-4-Abschlusszeile nachziehen (mit dem nächsten Dokument-Commit).
3. `backup/pre-push-7fcd461` in zukünftige Branch-Set-Prüfungen einplanen.
4. H/L-Familienfrage (§4.3) — in Task 5 entscheiden und dokumentieren.
5. `radiquant`-gh-Aufräumarbeiten: vom Betreiber erledigt (Stand 28.08.).
