# E2-Evidenz: GitHub-Fernzustand — 2026-08-28 (Teil 1: ohne API-Token)

Ausführung im Rahmen der V6-Prioritätenkette, Stufe 2 (N2 → E2).
Ort: Haupt-Checkout `codex/aurelia-vorbereitung` @ `8706186`.
Nur Lese-/Prüfbefehle; kein Push, kein Fetch (Vergleich gegen frische
`ls-remote`-Hashes stattRemote-Tracking-Refs), nichts ins Repository
geschrieben. Diese Datei ist Analyse-Evidenz, keine Gate-Freigabe.

## Methode

1. `git ls-remote origin` — vollständige Ref-Inventur über den **Windows
   Credential Manager** (git-eigener Transport, unabhängig vom `gh`-Token).
2. Vergleich der lokalen Branch-Spitzen gegen die **frisch abgefragten
   Remote-Hashes** (nicht gegen evtl. veraltete `origin/*`-Tracking-Refs):
   `git rev-list --left-right --count <remote-hash>...<local-hash>`.
3. `gh auth status` (gh 2.83.2) — Zustand des Keyring-Tokens.
4. Untracked-Inventar je Worktree via `git status --porcelain
   --untracked-files=all`.

## Ergebnisse

| # | Prüfung | Ergebnis | Interpretation |
|---|---|---|---|
| 1 | `gh auth status` | **Exit 1** — Konto `radiquant`, „The token in keyring is invalid" | V6-Befund frisch bestätigt; Re-Auth nötig (`gh auth login -h github.com`) |
| 2 | `git ls-remote origin` | funktioniert (Exit 0) | git-Transport + Credential Manager unabhängig von `gh` intakt; Repo erreichbar |
| 3 | Remote-Ref-Inventur | `HEAD` → `main` @ `b858ccd`; **5 Branches**; **0 Tags**; **0 `refs/pull/*`** | V6 exakt bestätigt: kein CI-Trigger-Kontext, keine PR-Historie |
| 4 | Sync-Zustand je Zweig | `main`, `vorbereitung`, `g0-governance`, `kanon-implementation`: **identisch**; `konsolidierung`: **13 ahead / 0 behind** | Präzisierung zu V6: die 13 unpushed Commits liegen **ausschließlich** auf `konsolidierung`; 0 behind ⇒ **Fast-Forward-Push ohne Force** möglich |
| 5 | Untracked: g0-governance-Worktree | **15 Dateien, 16.931 Zeilen** (14 G0-Pläne 01–13 + Master-Plan + 1 Status-HTML) | V6-Zeilenangabe exakt bestätigt |
| 6 | Untracked: konsolidierung-Worktree | **1 Datei, 1.949 Zeilen** (Migrations-Recovery-Plan) + 2 Dirty-Scanner-Dateien (dokumentiertes Overlay) | V6-Zeilenangabe exakt bestätigt; Overlay unangetastet |
| 7 | Haupt-Checkout + kanon-Worktree | **sauber** (0 modifiziert, 0 untracked) | — |
| 8 | `.github/` lokal | nur `copilot-instructions.md`; **kein `workflows/`** | „kein CI definiert" lokal bestätigt; fernseitige Prüfung steht aus (Teil 2) |
| 9 | Konto-Split git vs. gh | git/Credential Manager: **`redshift-three67`** (Repo-Owner, funktionsfähig); gh-Keyring: nur **`radiquant`** mit ungültigem Token | **Neuer Befund (nicht in V6):** Zwei-Konten-Split erklärt, warum git funktioniert, gh aber nicht. Re-Auth muss als `redshift-three67` erfolgen (Zugriff auf privates Repo); Zugriffsberechtigung von `radiquant` ist mit ungültigem Token nicht prüfbar |

## Remote-Zweiginventar (frisch, 2026-08-28)

| Ref | Remote-Hash | Lokal | Sync |
|---|---|---|---|
| `main` (=`HEAD`) | `b858ccd` | `b858ccd` | identisch |
| `codex/aurelia-vorbereitung` | `8706186` | `8706186` | identisch |
| `codex/aurelia-g0-governance` | `a6a8e7d` | `a6a8e7d` | identisch |
| `codex/aurelia-kanon-implementation` | `b20ee87` | `b20ee87` | identisch |
| `codex/aurelia-konsolidierung` | `029bdce` | `aec827f` | **13 ahead / 0 behind** |

## Teil 2: API-Evidenz nach Re-Auth (2026-08-28, Nachmittag)

Re-Auth via OAuth-Device-Flow im Browser, abgeschlossen als
**`redshift-three67`** (aktiv), Scopes `gist, read:org, repo`.
`gh auth status`: aktives Konto gültig; der Gesamte-Exit bleibt 1 allein wegen
des alten, inaktiven, ungültigen `radiquant`-Keyring-Eintrags.

| # | Prüfung | Ergebnis | Interpretation |
|---|---|---|---|
| 10 | Repo-Metadaten | `aurelia` @ `redshift-three67`, **PRIVATE**, Default-Branch `main`, erstellt 2026-08-23T16:03Z, `pushedAt` 2026-08-26T07:23Z, 747 KB, 0 Forks, 0 Stars, Issues an, Wiki/Diskussionen aus | V6 „privat" bestätigt; `pushedAt` deckungsgleich mit Fern-Spitze `029bdce` (26.08., 09:00 +0200) — seither nichts mehr gepusht |
| 11 | Workflows (fern) | `total_count: 0` | „kein CI" nun **auch fernseitig** hart bestätigt (V6 kannte nur den Lokalbefund) |
| 12 | Workflow-Runs | 0 | nie ein Run ausgeführt |
| 13 | Pull Requests | `[]` (state=all) | **0 PRs in der gesamten Repo-Historie** — das Zweitaugenprinzip hat fernseitig nie stattgefunden |
| 14 | Tags / Releases | 0 / 0 | keine versionierten Fixpunkte |
| 15 | Branch-Protection (`main`, `vorbereitung`) | **HTTP 403**: „Upgrade to GitHub Pro or make this repository public to enable this feature." | **Neuer harter Befund (nicht in V6):** Branch-Protection ist auf privaten Repos **nicht ohne GitHub Pro verfügbar**. Die Empfehlung „Branch-Protection beim nächsten Push ergänzen" (N10–N12) ist auf dem freien Plan **nicht umsetzbar** — Alternativen: GitHub Pro, oder Durchsetzung über den eigenen K1-Push-Scanner (Pre-Push-Hook) + Disziplin |
| 16 | Collaborators | nur `redshift-three67` | **`radiquant` hat keinen Zugriff** auf das Repo — der Konto-Split (Zeile 9) war also kausal: mit `radiquant` wäre E2-Teil-2 leer ausgegangen (privates Repo ⇒ 404/403) |

## Folgerungen

1. **Stufe 2 der Prioritätenkette ist erfüllt** (`gh` re-authentifiziert als
   Repo-Owner; L4.2 entblockt). Restposten: Verwerfen des nutzlosen
   `radiquant`-Keyring-Eintrags (nur lokale Hygiene, nach Abstimmung mit dem
   Betreiber).
2. **Das Fern-Repo ist ein reiner Spiegel ohne Mechanik:** keine CI, keine
   PRs, keine Protection, keine Tags. Qualitätssicherung existiert bisher nur
   lokal (Scanner, Tests, Gates) — genau die SPOF-Konstellation, die das
   Migrationsdesign adressiert.
3. **N10–N12 müssen umgeschrieben werden:** Branch-Protection ist
   planbedingt blockiert (403). Gleichwertige Durchsetzung im freien Plan:
   `check-push-graph.mjs` als verpflichtender Pre-Push-Hook + kanonischer
   FF-only-Push-Workflow; GitHub Pro nur falls fernseitige Zweitaugen-
   Erzwingung gewünscht ist.

