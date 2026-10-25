# AURELIA — Tiefenanalyse V5: Metadaten & Methodik

**Zeitstempel der Erstellung:** 2026-08-28, 09:28 CEST (Analysefenster 09:16–09:55 CEST)
**Version:** 5.0 — vollständige Neuanalyse von Grund auf
**Ablageort:** `aurelia-tiefenanalyse-v5-2026-08-28/` (gesondert gegenüber V1–V4)
**Analysegegenstand:** Projekt AURELIA — Konstitution, Dokumentation, Codebasis, alle vier Branchlinien inkl. drei Worktrees, GitHub-Remote-Zustand, Gate-/Konsolidierungsprogramme
**Vorgängerversionen:** V1 (16:40), V2 (17:22), V3 (17:33), V4 (19:39) — alle 2026-08-25, archiviert in `aurelia-tiefenanalyse*/` und `docs/project-control/external-analyses/`

---

## 1. Auftrag und Einhaltung

Der Auftrag lautete: akkurate, präzise, stabile, vollständig detaillierte Tiefenanalyse von Grund auf; gesonderte Ablage mit neuem Zeitstempel; strukturierte tabellarische Statusansicht (umgesetzt/offen); Lücken, Problematiken und Innovationen; prozentuale Angaben je Phase und Schritt; **strikt nur lesend lokal wie auch auf GitHub**.

| Regel | Einhaltung |
|---|---|
| Keine Dateiänderung am Projektbestand | ✅ eingehalten — einzige Schreibaktion ist diese Analyseablage (ausdrücklich angefordert) |
| Kein Git-Schreibzugriff (add/commit/push/branch) | ✅ nur lesende Git-Befehle (`status`, `log`, `ls-remote`, `worktree list`, `rev-list`) |
| Kein `git fetch` | ✅ Remotevergleich ausschließlich via `git ls-remote` (schreibt nichts) |
| Kein Schreibzugriff auf GitHub (kein Push, kein PR, keine Issue-Aktion) | ✅ |
| Keine Serverberührung (M G1 / 185.242.115.210) | ✅ kein SSH, keine SSH-Referenz verwendet |
| Keine nicht-destruktiven, aber artefaktbildenden Ausführungen | ✅ `npm run typecheck` / `npm test` / `npm run build` wurden **nicht** ausgeführt, weil `node_modules` im Windows-Checkout nicht existiert und eine Installation das Nur-Lese-Gebot verletzen würde — siehe §3 |

## 2. Erhebungsmethodik (Volllesung, statisch)

| Quellblock | Methode | Umfang |
|---|---|---|
| Konstitution & Status (`AGENTS.project.md`, `docs/STATUS.md`, `docs/project-control/README.md`, `ground-zero/GATE-STATUS.md`) | Volllesung | 100 % |
| Roadmap, Offenpunkte, Wiedervorlage (`docs/09`, `25`, `26`) | Volllesung | 100 % |
| Codebasis `src/` (60 Dateien, 8.572 Zeilen), `scripts/`, `migrations/`, `server/` | Strukturinventar + Schlüsseldateien (auth, memberships, app-data, migrations) | ~100 % Struktur, Kerndateien voll |
| Git-Topologie: 5 lokale Branches, 3 Worktrees, Remote-Heads | `git log --graph --all`, `branch -vv`, `worktree list`, `ls-remote`, `rev-list --count` | 100 % |
| Worktree `aurelia-kanon` (`codex/aurelia-kanon-implementation`, 14 Commits > Vorbereitung) | Deep-Dive-Subagent, Nur-Lesen | 100 % Inventar |
| Worktree `aurelia-g0-governance` (`codex/aurelia-g0-governance`, 32 Commits > Vorbereitung) | Deep-Dive-Subagent, Nur-Lesen | 100 % Inventar |
| Worktree `aurelia-konsolidierung` (`codex/aurelia-konsolidierung`, 27 Commits > Vorbereitung, 13 unpushed) | Deep-Dive-Subagent, Nur-Lesen | 100 % Inventar |
| GitHub `redshift-three67/aurelia` | `git ls-remote` (Branch-Heads); API-Abfragen ohne Token → 404 (privates Repo) | Branch-Heads 100 %, PRs/Protections nicht beobachtbar |
| Build-/Testgates (`npm test`, `typecheck`, `lint`, `check:canon`, `check:push-graph`) | **nicht ausgeführt** (Nur-Lese-Gebot, `node_modules` fehlt) | Werte aus dokumentierter Evidenz + Canon-Quellen, als solche gekennzeichnet |

**Bewertungs-/Zählgrundlage:** 161 getrackte Dateien; `src/` 8.572 Zeilen; `docs/` 5.177 Zeilen; Testinventar 175 Tests im Haupt-Checkout (11 Dateien) bzw. 185 auf dem Kanon-Branch (+10 Canon-Contract-Tests).

## 3. Methodische Abgrenzung zu V1–V4

- **V1–V3** (2026-08-25): Erst-/Zweit-/Drittanalyse inkl. read-only Serverinventur des Altsystems; V3-Befunde wurden 1:1 als Abnahmekriterien des Ground-Zero-Serverdesigns übernommen.
- **V4** (2026-08-25, 19:39): Neuanalyse nach der Kanon-Wende (Ubuntu statt Debian, 2×2 TB, Phase-1-Pause am Gate `G0-SRV-GROUND-ZERO`); enthielt **Live-Serverinventur per SSH** sowie Live-Ausführung von `npm test`/`typecheck`.
- **V5 (diese Analyse):** Erste Analyse der **vier parallelen Branchlinien samt Worktrees** als eigenständiger Analysegegenstand (Kanon-Contract, G0-Governance-Design, K1-Konsolidierung, Qualitätsrouting, Linux-Migrationsdesign entstanden alle nach V4 bzw. waren V4 unbekannt). Dafür **keine Serverberührung** und **keine Build-/Testausführung** — alle Laufzeitgates werden als „in dieser Session nicht ausgeführt (Nur-Lese-Gebot)" ausgewiesen, nie als bestanden behauptet.

## 4. Neu seit V4 (Entscheidungswendepunkte dieser Analyse)

1. **`codex/aurelia-kanon-implementation`** (14 Commits): maschinell prüfbarer Kanon-Contract (`scripts/canon-contract.mjs`, `check:canon`), `CANONICAL_DECISION_LOCKS`, U-System verriegelt, U09 „Phase 1 Gehäuse gestartet" per Textregel gesperrt, Windows-Vite-Start gefixt.
2. **`codex/aurelia-g0-governance`** (32 Commits): eingefrorenes Governance-Design (Spec, 3.968 Zeilen, Byte-Hash fixiert): RFC-8785-Kanonisierung, Append-only Transition-Ledger, Witness/Egress-State-Machines, Ed25519-Governance-Authentifizierung, Signed Cores, Genesis-Manifest; **dort wurden die G0-SRV-/Ground-Zero-Dokumente gelöscht** — divergentes Weltbild zum Haupt-Checkout. 15 Plan-/Master-Dateien (Pläne 01–13) existieren **nur ungetrackt lokal**.
3. **`codex/aurelia-konsolidierung`** (27 Commits, **13 unpushed**): K1-Kanonkonsolidierung (Tasks 1–14; T1/T2 abgenommen, T3 in Spur-B-Korrektur, T4–T14 blockiert), fail-closed Push-Graph-Scanner (`check:push-graph`) mit vier Security-Fixes und AST-Adjudikation, Spur-A/B-Qualitätsrouting, Linux-Workstation-Migrationsdesign (3-Schichten-Architektur A/B/C, Restaurationsnachweis 13 Schritte).
4. **Kein Fortschritt am kritischen Pfad:** `G0-SRV-0` wartet unverändert auf den externen Backup-/Restore-Nachweis; `server_changes_started: false`.

## 5. Dokumentenstruktur V5

| Datei | Inhalt |
|---|---|
| `00_METADATA_UND_METHODIK_V5.md` | Diese Datei — Auftrag, Methodik, Delta zu V1–V4 |
| `01_EXECUTIVE_SUMMARY_V5.md` | Gesamturteil, Kernbefunde, kritischer Pfad |
| `02_PROJEKTANALYSE_VON_NULL_V5.md` | Konstitution, Codebasis, Branch-/Worktree-Topologie, Security-Mechaniken, Testinventar |
| `03_STATUS_TABELLEN_V5.md` | **Strukturierte Tabellarische Gesamtansicht**: Phasen, Gates, K1-Tasks, ID-Familien, Branch-Matrix, GitHub — je Zeile Status umgesetzt/teilweise/offen |
| `04_PHASEN_UND_PROZENT_V5.md` | **Prozentrollup** je Phase und Schritt inkl. Methodik/Formel |
| `05_LUECKEN_RISIKEN_PROBLEMATIKEN_V5.md` | Konsolidierte Lücken-/Risikomatrix mit Schweregraden |
| `06_ERGAENZENDE_INNOVATIONEN_V5.md` | Bestehende Innovationen (Würdigung) + verfassungskonforme Neuvorschläge |
| `07_EMPFEHLUNGEN_UND_FAZIT_V5.md` | Prioritätenkette, Nächste Schritte, Schlussurteil |
| `08_NACHTRAG_EVIDENZSTUFEN_UND_NACHVOLLZIEHBARKEIT_V5.md` | **Nachtrag (~09:50 CEST):** Evidenzstufen-Modell E0–E3 (was fehlt, was es schließt, Trade-offs), bewusst nicht angeforderte Zugriffe, **Claim→Quelle→Evidenztyp-Traceability-Tabelle** für Entwickler, Aktualisierungspflicht für V6 |

## 6. Normativer Hinweis

Diese Analyse ist **Evidenz und Entscheidungsinput, kein automatisch freigegebener Masterplan** (entspricht `docs/project-control/README.md`): Anweisungen hierin werden erst wirksam, wenn der Betreiber sie in eine freigegebene AURELIA-Spezifikation übernimmt. Alle Prozentsätze sind modelliert (Methodik in `04`), nicht gemessene Produktivität.
