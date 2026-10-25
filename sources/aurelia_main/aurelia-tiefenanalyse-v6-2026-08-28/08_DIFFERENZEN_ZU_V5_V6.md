# AURELIA Tiefenanalyse V6 — Differenzenvergleich zu V5

Vergleichsgegenstand: `aurelia-tiefenanalyse-v5-2026-08-28/` (9 Dateien, 727
Zeilen, erstellt 09:28–10:18 CEST) gegen die V6-Befunde (erstellt 10:44–10:55
CEST, gleiche Repo-Basis — keine Mutation dazwischen, letzter Commit `aec827f`
vom 27.08., 09:24).

## 1. Bestätigt (V5 = V6)

| Befund | V5-Wert | V6-Verifikation |
|---|---|---|
| Branch-Heads lokal/remote | main `b858ccd`, vorbereitung `8706186`, kanon `b20ee87`, g0 `a6a8e7d` synchron; konsolidierung lokal `aec827f` vs. remote `029bdce`, **13 ahead** | ✅ identisch (ls-remote + rev-list) |
| Kritischer Pfad | `G0-SRV-0` wartet auf Backup-/Restore-Nachweis; 0/13 Gates; `server_changes_started: false` | ✅ identisch (GATE-STATUS.md) |
| K1-Stand | T1/T2 abgenommen, T3 ~80 % in TDD-Korrektur, Review ausstehend, T4–T14 blockiert | ✅ identisch (K1-STATUS.md + Worktree-Status) |
| Ungetrackte Masse | 15 G0-Dateien, 1.949-Zeilen-Migrationsplan, 2 Dirty-Scanner-Dateien | ✅ identisch (17.091 Zeilen G0-Pläne via wc -l) |
| Gate-Voraussetzungen | 6/6 Betreiberbestätigungen, 0/6 technische Abnahmen | ✅ identisch |
| Prozentmodell | Gesamt ≈ 30–35 %, alle Blockwerte | ✅ **alle 15 Werte identisch** (Stabilität bestätigt) |
| Blocker-Hierarchie | Nachweis- → Konsolidierungs- → Durchsetzungslücken | ✅ identisch |
| Konzept-/ID-Systematik | D22 gesetzt, C12, X20, U12, K5+K3s, H3, WV6, L9, O10 | ✅ identisch |
| Portalnatur | ~90 % Konzeptportal, Auth funktionsfähig, kein RLS | ✅ identisch (V6 zusätzlich: 1.279 Z. Dead Code, 9 Textdrift-Stellen) |

## 2. Korrigiert gegenüber V5 (3 Präzisierungen)

### K1 — L2.1/V5: „g0-governance **löschte** die G0-SRV-/Ground-Zero-Dokumente"

- **V5-Behauptung:** Der Zweig habe die Dokumente gelöscht und die Phase-1-Pause
  entfernt („divergentes Weltbild durch Löschung").
- **V6-Befund (Git-Archäologie):** Die Ground-Zero-/Analyse-/GATE-STATUS-Dokumente
  wurden **erst in `8706186` hinzugefügt** (25.08., 18:49; 29 Dateien, 2.543
  Zeilen). `g0-governance` zweigt bei `a726346` ab (24.08.) und enthält `8706186`
  **nicht** → die Dokumente waren dort **nie vorhanden**. `git log
  --diff-filter=D` über den Zweig: **kein einziger Lösch-Commit**.
- **Konsequenz:** Die praktische Warnung bleibt valide (Debian-Kanon 31 Treffer,
  „Phase 1 läuft" ohne Pause, Merge-Konfliktrisiko in `STATUS.md`/
  `AGENTS.project.md`), aber die Ursache ist Abzweig-Vorlauf, keine aktive
  Löschung. Schwere von 🟠 auf 🟡 herabgesetzt (L2.3 in V6).

### K2 — L3.4/V5: „kein node_modules → kein lokales Gate ausführbar"

- **V5-Behauptung:** In dieser Workstation nicht lauffähig; E1 erfordert
  Installationsfreigabe.
- **V6-Befund:** Der **Haupt-Checkout** hat kein `node_modules` — aber **alle
  drei Worktrees haben vollständige Installationen** (~253 Pakete je; installiert
  24.08. 10:40 / 24.08. 14:45 / 25.08. 20:13; `typescript` inkl. `.bin`).
  Node v22.22.0 / npm 11.18.0 (exakt die im Migrationsdesign gepinnten
  Toolchain-Versionen).
- **Konsequenz:** E1 (Qualitätskette mit frischer Evidenz) ist **ohne jede
  Installation sofort möglich** (z. B. in `.worktrees/aurelia-konsolidierung`).
  Verbleibende Windows-Risiken: `npm test`-Glob-Quoting (cmd.exe) und
  `browser-guard`-Pfade (`/workspace`, `/tmp`) — K1-T7/T9 fixen beide.
  Vorschlag N1 (neu) macht daraus eine Sofortmaßnahme.

### K3 — T6/V5: „g0-governance: Debian-Reste entfernt"

- **V5-Behauptung:** Auf `g0-governance` seien Debian-Reste beseitigt.
- **V6-Befund:** Umgekehrt — der Zweig **trägt** den alten Debian-Kanon:
  31 Debian-Treffer in `docs/`+`AGENTS.project.md` (vorbereitung: 23, kanon: 21,
  konsolidierung: 41 als dokumentierte Historie); `docs/02-architecture.md` nennt
  dort „GPU Server M G1 (Debian Bookworm)" und „Control Plane · Debian EU";
  `STATUS.md` sagt „D08 gesetzt (Debian Passkeys)".
- **Konsequenz:** Kanon-Bereinigung ist konsolidierungsseitig (K1) und
  AUDIT-02-seitig zu führen, nicht g0-seitig.

## 3. Neu in V6 (über V5 hinausgehend)

| # | Neuer Befund | Evidenz |
|---|---|---|
| 1 | **Kein CI definiert, nie gewesen** (`.github/workflows` fehlt; `git log --all -- .github/workflows` leer; keine yml/yaml in irgendeiner Revision) | Git-Historie |
| 2 | `gh`-Keyring-Token ungültig (HTTP 401, Account `radiquant`); Repo anonym 404 (privat); git funktioniert via Windows Credential Manager | gh/curl-Reads |
| 3 | 0 Tags, 0 PR-Refs (`refs/pull/*` leer) in der gesamten Historie | `git ls-remote` |
| 4 | Worktree-node_modules-Datierung (24.–25.08.) → passt zur Node/npm-Pinierung des Migrationsdesigns | Dateisystem |
| 5 | Duplikatmigration byteidentisch (md5 `0bb43ef6…`), Basename-Keying als Sicherheit, aber ohne Drift-Wächter | diff/md5 |
| 6 | Kein echter HTTP-Server im Repo (kein Express/Fastify/Hono); HTTP = Vite + Server-Functions + Nitro/Vercel | Grep + Konfiguration |
| 7 | Windows-Portabilitätslücken konkretisiert: `npm test`-Glob-Quoting, `browser-guard` (`/workspace`, `/tmp`), `startup.sh` POSIX-only | Quelltext |
| 8 | `.env.example` dokumentiert 0 der real gelesenen Variablen | Abgleich |
| 9 | Neue Vorschläge N1 (Worktree-Qualitätskette jetzt), N2 (gh re-auth), N7 (Security-Header), N12 (gates.json-Spiegel), N14 (.env-Doku) | — |
| 10 | Risikomatrix um L2.3 (herabgestuft), L3.2 (CSP), L4.2 (gh), L3.11 (ON CONFLICT), L3.12 (Install-Assets) erweitert | — |

## 4. Kleinere Zählabweichungen (ohne Befundwert)

| Metrik | V5 | V6 | Anmerkung |
|---|---|---|---|
| `src/`-Zeilen | 8.572 | 9.261 | Zählbasis (inkl. `routeTree.gen.ts`, Tests, alle .ts/.tsx) |
| `docs/`-Zeilen | 5.177 | 6.202 | V6 zählt alle `.md` inkl. `superpowers/`+`project-control/` |
| Testdateien Haupt-Checkout | 11 | 9 | V6 zählt `scripts/*.test.mjs` (7) + 2 `.test.ts`; V5-Umfang unklar |
| Testfälle | ~175 (Haupt) | nicht neu gezählt | V6 nicht ausgeführt; Suite-Inventar bestätigt |
| G0-Pläne | „15 Plan-/Masterdateien" + HTML separat | 15 Dateien = 14 Pläne + 1 HTML (17.091 Z.) | deckungsgleich mit `GATE-GOV-0-SUPPLEMENT` („genau 14 + separater HTML-Status") |

## 5. Ergebnis des Abgleichs

- **Substanz:** V5 und V6 sind **vollständig konform** — gleiche Blocker, gleiche
  Prozentwerte, gleiche Prioritätenlogik.
- **Korrekturen:** 3 Präzisierungen (K1–K3), davon 2 faktische Korrekturen
  (Löschung → nie enthalten; node_modules-Reichweite) und 1 Umkehrung
  (Debian-Reste) — jeweils mit Git-/Dateisystem-Evidenz.
- **Zuwachs:** harter CI-/GitHub-Fernzustand, Windows-Portabilitätsdetails,
  5 neue Vorschläge.
- **Fazit:** Die V5-Einschätzung „Stabilität hoch, Risiko unverändert
  (`G0-SRV-0`), Metarisko unreplizierte Arbeit" wird von V6 **bestätigt und
  verschärft** (Migrationsdesign macht die Replikation jetzt selbst zum
  nächsten geplanten Schritt).
