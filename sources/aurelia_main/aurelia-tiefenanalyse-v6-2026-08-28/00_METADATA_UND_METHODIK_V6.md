# AURELIA Tiefenanalyse V6 — Metadaten und Methodik

```yaml
analyse: aurelia-tiefenanalyse-v6
version: 6
erstellt: 2026-08-28, 10:44–10:55 CEST (Europe/Berlin)
vorgaenger: aurelia-tiefenanalyse-v5-2026-08-28 (09:28–10:18 CEST)
auftrag: Neue Tiefenanalyse von Grund auf, strikt lesend (lokal + GitHub),
         getrennte Ablage mit neuem Zeitstempel, Status-Tabellen,
         Prozentangaben je Phase/Schritt, Differenzenvergleich zu V5
repo: redshift-three67/aurelia (privat)
hauptcheckout: C:/Users/Hubert111/Documents/ChatGPT/Aurelia
branch_haupt: codex/aurelia-vorbereitung @ 8706186af01e10e4253e25abb31bf3577110dae4
branch_juengste_lokal: codex/aurelia-konsolidierung @ aec827f829a2a716201cf21ac2574defb3e24c9a (13 unpushed)
remote_heads_verifiziert: 2026-08-28, ~10:20 CEST (git ls-remote)
serverzugriff: keiner (kein SSH, kein IPMI, keine Servermutation)
schreibzugriffe: nur dieses Analyseverzeichnis (gitignored via /aurelia-tiefenanalyse*/)
```

## 1. Nur-Lese-Einhaltung (Regelprüfung)

| Prüfung | Ergebnis |
|---|---|
| Dateien geändert/erstellt außerhalb des Analyseordners | **nein** |
| `npm test` / `typecheck` / `build` / `lint` / `db:migrate` ausgeführt | **nein** (Nur-Lese-Gebot; `node_modules` fehlt im Haupt-Checkout) |
| `git fetch` (schreibend auf Refs) | nein; nur `git ls-remote` und `git fetch --dry-run` |
| GitHub-Schreibzugriff (Push, PR, Issue) | nein |
| Server M G1 berührt | nein |
| Ignorierte Analyse-`source/`-Ordner gelesen (52 Dateien, V3-Klartext-Geheimnis) | nein — nur Dateinamen, keine Inhalte |

## 2. Methodik

1. **Eigene Verifikation** (Haupt-Auditor): Git-Topologie aller 5 Branches,
   Ancestor-/Merge-Basis-Prüfung, Remote-Abgleich, Worktree-Inventare,
   `.gitignore`-Politik, LOC-Messungen, Gate- und Statusdokumente im Volltext.
2. **Fünf parallele Lese-Deep-Dives** (Subagenten, ausschließlich lesend):
   GitHub-Fernzustand · `server/`+`migrations/`+`scripts/`+`vite.config.ts` ·
   `src/` (Routing/Auth/Isolation/Dead-Code) · Planungs- und Governance-Dokumente ·
   V5-Volltextextraktion (9 Dateien, 727 Zeilen).
3. **Differenzenvergleich** jedes V6-Befunds gegen den V5-Wortlaut
   (Ergebnis in `08_DIFFERENZEN_ZU_V5_V6.md`).

## 3. Ausgewertete Quellblöcke

| Quellblock | Methode | Umfang |
|---|---|---|
| Konstitution (`AGENTS.project.md`), `docs/STATUS.md`, `GATE-STATUS.md` | Volllesung | 100 % |
| Roadmap, Offen, Wiedervorlage, Freigabe, ID-Schema, Fachkapitel (`docs/00–26`) | Volllesung/Struktur | ~100 % |
| Ground-Zero-Serverdesign (426 Z.), Preflight-Plan (394 Z.), K1-Plan (1.323 Z.) | Volllesung/Struktur | 100 % |
| G0-Governance-Design (3.968 Z., Branch `g0-governance`) | Struktur + Kernabschnitte | ~100 % |
| Linux-Migrationsdesign ( approved, 325 Z.) + ungetrackter Plan (1.949 Z.) | Volllesung/Kopf | 100 % |
| `src/` — 9.261 Zeilen | Vollinventar + Schlüsseldateien im Volltext | 100 % Struktur |
| `scripts/` — 3.670 Zeilen (22 Dateien) | Vollinventar + Funktionsanalyse | 100 % Struktur |
| `migrations/`, `server/`, `vite.config.ts`, Root-Konfiguration | Volllesung | 100 % |
| Worktrees `aurelia-kanon`, `aurelia-g0-governance`, `aurelia-konsolidierung` | Git-Baum + Status + Kernartefakte | 100 % Inventar |
| GitHub `redshift-three67/aurelia` | `git ls-remote`, `fetch --dry-run`; `gh` **401** (Keyring-Token ungültig), anonym **404** (privat) | Branch-Heads 100 %, PRs/CI/Protections nicht beobachtbar |
| Build-/Testgates | **nicht ausgeführt** | Evidenz nur dokumentiert/quelltextbasiert |

## 4. Zählgrundlagen (V6-Verifikation)

| Metrik | Wert | Basis |
|---|---|---|
| Commits `main` | 10 | `git rev-list --count` |
| Commits `codex/aurelia-vorbereitung` | 14 (+4 ggü. main) | dito |
| Commits `codex/aurelia-kanon-implementation` | 27 (+13, Abzweig `a726346`) | dito |
| Commits `codex/aurelia-g0-governance` | 45 (+18, Abzweig `b20ee87`) | dito |
| Commits `codex/aurelia-konsolidierung` lokal/remote | 41 / 28 (**13 unpushed**) | dito |
| `src/` | 9.261 Zeilen | Vollinventar (25 Routendateien, 16 Auth-, 9 Concept-Dateien u. a.) |
| `scripts/` | 3.670 Zeilen, davon ~1.662 Tests | `wc -l` |
| `docs/` (Hauptbaum, getrackt) | 6.202 Zeilen Markdown | `wc -l` über alle `docs/**.md` |
| `migrations/` | 153 Zeilen (3 Dateien, 2 byteidentisch, md5 `0bb43ef6…`) | diff/md5 |
| `server/` | 124 Zeilen (2 Dateien) | `wc -l` |
| Ungetrackte G0-Governance-Pläne | 15 Dateien, **17.091 Zeilen** | `wc -l` |
| Ungetrackter Migrationsplan | 1 Datei, **1.949 Zeilen** | `wc -l` |
| Testdateien Haupt-Checkout | 9 (7 `.test.mjs` + 2 `.test.ts`), ~175 Testfälle laut V5-Zählung, hier **nicht ausgeführt** | Inventar |
| `node_modules` Haupt-Checkout | **fehlt** | Verzeichnisprüfung |
| `node_modules` in den 3 Worktrees | **vorhanden** (je ~253 Pakete, installiert 24.–25.08.2026) | Verzeichnisprüfung — **neu in V6** |

## 5. Evidenzstufen

- **E0 erbracht:** statisches Lesen, Git-/Remote-Reads, Worktree-Inventare.
- **E1 (größter Nachholwert, jetzt ohne Installationsfreigabe möglich):**
  Ausführung der Qualitätskette (`npm test`, `typecheck`, `check:auth`) in einem
  der drei Worktrees — dort ist `node_modules` vorhanden (V5 ging noch von
  „kein lokales Gate ausführbar" aus; das gilt nur für den Haupt-Checkout).
- **E2:** read-only GitHub-Token → PRs/CI/Branch-Protection; vorher Re-Auth von
  `gh` (`gh auth login -h github.com`, Account `radiquant`, Token ungültig).
- **E3:** read-only SSH auf M G1 → Aktualisierung der Altserverbefunde (Stand 25.08.).
- Priorität: **E1 > E2 > E3**. Prozentmodell ändert sich durch E1–E3 nicht
  (Evidenzqualität ≠ Fortschritt).

## 6. Normativer Rahmen

Diese Analyse ist **Evidenz und Entscheidungsinput, kein automatisch
freigegebener Masterplan**. Sie ersetzt weder Betreiberfreigaben noch
Gate-Entscheidungen. Alle Prozentsätze sind **modelliert** (Formel in
`04_PHASEN_UND_PROZENT_V6.md`), nicht gemessene Produktivität. Serveränderungen,
Destruktion und Publikation bleiben durch die dokumentierten Gates gesperrt
(`destructive_actions_allowed: false`, `publication_gate: blocked`).
