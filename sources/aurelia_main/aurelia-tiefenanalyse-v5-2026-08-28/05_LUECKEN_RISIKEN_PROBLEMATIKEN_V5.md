# AURELIA — Tiefenanalyse V5: Lücken, Risiken und Problematiken

**Stand: 2026-08-28, 09:28 CEST · Nur-Lese-Analyse**
**Schweregrade:** 🔴 Blocker/Kritisch · 🟠 Hoch · 🟡 Mittel · 🔵 Niedrig/Kontext
**Normativer Hinweis:** Diese Liste ist Entscheidungsinput; wirksam wird sie erst durch Übernahme in eine freigegebene AURELIA-Spezifikation.

---

## L1 — Kritischer Pfad (direkt gates-relevant)

| # | Befund | Evidenz | Schwere | Wirkung |
|---|---|---|---|---|
| L1.1 | `G0-SRV-0`: externer Backup-/Restore-Nachweis fehlt seit Freigabe (25.08.) weiter aus | `GATE-STATUS.md`: `awaiting-backup-and-restore-evidence` | 🔴 | Blockiert G0-SRV-1…12, AUDIT-02, Phase-1-Abnahme, alle Phasen ≥ 2 |
| L1.2 | 0/6 technische Abnahmen der Gate-Voraussetzungen (IPMI, KVM, Virtual Media, USV-Kapazitätsnachweis, Backup-Nachweis, DDoS-Umfang) — nur Betreiberbestätigungen | `GATE-STATUS.md` Voraussetzungstabelle | 🟠 | Gates ruhen auf unbelegter Betreiberangabe |
| L1.3 | ECC-Status der 128 GB RAM weiterhin unbewiesen (`memory_ecc: hardware-capable-but-active-ecc-not-yet-proven`) | `AGENTS.project.md`, GATE-STATUS | 🟠 | Speicherzuverlässigkeit für Timer-Ledger/CopyGuard-RAM nicht belegt |
| L1.4 | Altserver M G1 läuft unverändert mit V3/V4-Befunden weiter (NVML-Mismatch, `radiquant4-web`-Crashloop, Altgeheimnisse, öffentliche Ports); heutige Session hat ihn **bewusst nicht berührt** | V4, `GATE-STATUS.md` | 🟡 | Restrisikofenster bleibt bestehen bis Ground Zero |

## L2 — Konsolidierungs-/Branchrisiken (neu in V5 im Zentrum)

| # | Befund | Evidenz | Schwere | Wirkung |
|---|---|---|---|---|
| L2.1 | Vier Branchlinien mit divergentem Kanon: `g0-governance` hat Ground-Zero-/Analysedokumente **gelöscht** und die Phase-1-Pause aus `AGENTS.project.md`/`STATUS.md` entfernt; `kanon-implementation` enthält die Project-Control-Dokumente nie; Haupt-Checkout pflegt beide | Worktree-Diffs, Branch-Matrix T6 (03-Datei) | 🟠 |_merge/rebase-Konflikte in `STATUS.md`, `AGENTS.project.md`, Portalrouten vorprogrammiert; bis zur K1-Konsolidierung existiert **kein** einheitlicher Wahrheitsbranch |
| L2.2 | K1-Task 3 blockiert: erneutes Spec-Review ausstehend, Qualitätsreview dadurch blockiert, Tasks 4–14 folgen erst danach | `K1-STATUS.md` Task-Ledger | 🟠 | Der gesamte Konsolidierungsfahrplan ruht an **einer** Review-Schnittstelle |
| L2.3 | 13 unpushed Commits (`konsolidierung`) + 15 ungetrackte G0-Plan-/Masterdateien (38–120 KB je) + 2 unstaged Scanner-Dateien + 1 ungetrackter Migrationsplan (1.949 Zeilen) | `git status`/`branch -vv` der Worktrees | 🟠 | **Single Point of Failure Windows-Workstation**: jüngste Denkarbeit existiert genau einmal, unverschlüsselt auf einer Platte, während das eigene Migrationsdesign die Lösung bereits beschreibt (Ausführung offen) |
| L2.4 | Zwei Gate-Programme parallel ohne Kopplung: G0-SRV-0…12 (Server) vs. GATE-G0/DATAFLOW/… (Governance); Governance-Design modelliert den Backup-Nachweis nicht als EVID-Input | G0-Governance-Spec §13 vs. `GATE-STATUS.md` | 🟡 | Doppelte Buchführung; Gefahr inkonsistenter Gateentscheidungen |
| L2.5 | Governance-Freigabeformalitäten fehlen: `REV-G0-DESIGN-APPROVAL` (Ed25519, Designcommit + Byte-Hash) nicht erbracht, Trust-Pins existieren nicht, Fach-/Custodian-Rollen unbesetzt | Spec §10–16, Masterplan | 🟡 | GATE-G0 bleibt formal `red`, unabhängig von Qualität des Designs |
| L2.6 | Canon-Contract deckt Konzept-/Portaldocs, aber **nicht** `docs/project-control/**` und Ground-Zero-Docs | `canon-contract.mjs` `activeTextRules` | 🟡 | Gerade die dokumentsensible Gate-Ebene ist textlich ungeschützt |

## L3 — Code-/Datenlücken (Phase 1)

| # | Befund | Evidenz | Schwere | Wirkung |
|---|---|---|---|---|
| L3.1 | `data_class='synthetic'` nur DB-Default + Konvention — kein CHECK-Constraint, kein Test, kein Fail-closed | `migrations/0002_tenants.sql`, `memberships.ts` | 🟠 | Prinzip „Art.-9-Daten unmöglich machen" ist aktuell nur Konvention; ein Insert mit echtem Datensatz würde still durchgehen |
| L3.2 | Keine Row-Level-Security, keine negativen Isolationstests; Tenant-Scoping nur anwendungsseitig (`authMiddleware` → `context.userId`) | Arbeitspaket C der Spezifikation (geplant) | 🟡 | Datenbankseitige Verteidigungslinie fehlt |
| L3.3 | Keine Unit-Tests für `memberships.ts`/Praxis-Route; Chrome-Acceptance-Evidenz (Kanon-Plan Task 7) fehlt im Commitverlauf; Ganz-Branch-Review (Task 9 Step 5) nicht belegt | Kanon-Plan/Commitliste | 🟡 | Abnahmeevidenz der Phase-1-Schale unvollständig |
| L3.4 | Windows-Testrunner-Glob-Lücke (`npm test` findet ggf. 0 Skripttests); zusätzlich: Haupt-Checkout ohne `node_modules` → **kein** lokales Gate aktuell ausführbar (auch `typecheck` nicht) | K1-Plan Task 6/9; `Test-Path node_modules` = False | 🟡 | Qualitätskette ist dokumentiert, aber auf dieser Workstation de facto nicht aktivierbar ohne Installation |
| L3.5 | Portal-Altverweise (Debian/Bookworm, 2×1 TB) — bewusst auf AUDIT-02 verschoben | `project-control/README.md` §Altverweise | 🔵 | Dokumentiert, kein Widerspruch zum Kanon (Ausnahme explizit) |

## L4 — Infrastruktur/Plattform

| # | Befund | Evidenz | Schwere | Wirkung |
|---|---|---|---|---|
| L4.1 | GitHub: privat, keine authentifizierbare PR-/CI-/Branchschutz-Evidenz; `publication_gate` formal `blocked` | `ls-remote`, K1-Evidenz | 🟡 | Zusammenarbeit/Replikation über GitHub aktuell kein wirksamer Schutzschirm |
| L4.2 | Stack mit Vorabversionen: `nitro 3.0.260610-beta`, Vite 8, Better Auth ~1.6.30, React 19.2 | `package.json` | 🟡 | Upgrade-/Bruchrisiko im Build-Gate später |
| L4.3 | Sensible lokale Analysarchive (`source/`-Ordner inkl. Klartext-DB-Geheimnis V3) nur durch `.gitignore` geschützt; vom Migrationsdesign als Layer-C-Pflicht adressiert | `project-control/README.md` Sicherheitsgrenze | 🟡 | Ein lokal unverschlüsseltes Geheimnis bleibt bis zur Kapselausführung Risiko |
| L4.4 | Historische Git-Objekte mit Findings weiterhin erreichbar (Sanitisierung nur Branch-Tips V1/V2) | Push-Graph-Design | 🔵 | Bekannt und im Scanner-Design benannt |

## L5 — Prozess/Menschen

| # | Befund | Schwere | Wirkung |
|---|---|---|---|
| L5.1 | Nicht delegierbare externe Freigaben (Betreiber): G0-SRV-0-Nachweis, Gateentscheidungen, Destruktionsfreigaben, Operator-Freigabe Governance-Design | 🟠 | Projektgeschwindigkeit = Verfügbarkeit des Betreibers; Skripting kann das nicht ersetzen (gewollt) |
| L5.2 | Review-Kaskade kann sich selbst blockieren (K1: Spec-Review wartet → Qualitätsreview wartet → T4–T14 warten); QUALITY-ROUTING §4 kennt Stopp-Regel, aber kein Eskalationsfenster | 🟡 | Ein einziger ausstehender Reviewtermin hält 11 Tasks an |
| L5.3 | Externe Provider-Assets fehlen (`platform_asset_gate: external_blocker`, T12) — dürfen nicht erfunden werden | 🔵 | K1-Ende hängt an Drittleistung |

## Risikomatrix (Auswirkung × Eintrittswahrscheinlichkeit, qualitativ)

| | Eintritt hoch | Eintritt mittel | Eintritt niedrig |
|---|---|---|---|
| **Auswirkung hoch** | L2.3 (Arbeitsverlust lokal), L1.1 (weiterer Stillstand) | L2.1 (Kanonbruch beim Merge), L3.1 (synthetic-Verletzung) | L1.3 (ECC-Versagen) |
| **Auswirkung mittel** | L3.4 (Qualitätskette inaktiv) | L2.2 (Review-Stau), L2.4 (Gate-Doppelbuchführung) | L4.2 (Stack-Bruch) |
| **Auswirkung niedrig** | L5.3 | L3.5, L4.4 | L4.3 (nach Kapsel) |

## Fazit der Lückenanalyse

Drei Familien dominieren: **(1) Nachweislücken** (G0-SRV-0, technische Abnahmen, ECC), **(2) Konsolidierungslücken** (Branchdivergenz, Review-Stau, Replikationsdefizit), **(3) Durchsetzungslücken** (synthetic-Constraint, RLS, Canon-Deckung der Gate-Dokumente). Alle drei sind durch dokumentierte, projektkonforme Maßnahmen bereits adressierbar — es fehlt primär **Ausführung und Freigabe**, nicht Konzept.
