# AURELIA — Tiefenanalyse V5: Executive Summary

**Stand: 2026-08-28, 09:28 CEST · Nur-Lese-Analyse · Ablage: `aurelia-tiefenanalyse-v5-2026-08-28/`**

---

## 1. Gesamturteil

AURELIA ist konzeptionell ausgereift und diszipliniert geführt: Verfassung, Entscheidungskanon (D/C/X/U/K/H/O/WV), Phasenplan mit Stop-Gates, synthetische Datenklasse, Wellbeing-Grenze (kein Medizinprodukt) — alles verankert und teilweise maschinell prüfbar. Die Codebasis ist sauber (React 19/TanStack Start, Better Auth, Kysely/Postgres, 175 Tests), die Phase-1-Schale (Auth, Mandanten, Rollen, Portal) ist technisch weitgehend vorhanden.

Das Projekt steht jedoch an **einer engen, zweifachen Flaschenhalsstelle**:

1. **Infrastruktur:** Gate `G0-SRV-0` (externer Backup-/Restore-Nachweis auf M G1) ist seit 25.08. unverändert offen. Null von 13 Servergates ist bestanden, null Serveränderung erlaubt/begonnen. **Alles Produktarbeit (AUDIT-02, Phase-1-Abnahme, Phasen ≥ 2) wartet dahinter.**
2. **Konsolidierung:** Vier parallele Branchlinien (`vorbereitung`, `kanon-implementation`, `g0-governance`, `konsolidierung`) tragen **divergente Kanäne** (u. a. Phase-1-Pause ja/nein, Debian vs. Ubuntu-Reste, gelöschte vs. gepflegte Ground-Zero-Dokumente). Die vorgesehene Lösung (K1-Kanonkonsolidierung) steckt bei **Task 3 von 14** fest: Implementierung zu ~80 %, aber Spec-Review ausstehend → Tasks 4–14 blockiert. 13 Commits sind **unpushed**, 15 G0-Governance-Plan-/Master-Dateien existieren **nur ungetrackt**, 2 Scanner-Dateien liegen als bewusstes Dirty-Overlay vor, 1 Migrationsplan ist ungetrackt — die gesamte jüngste Denkarbeit existiert **genau einmal, auf einer Windows-Workstation ohne Dependenz-Installation**.

**Rollup (modelliert, Methodik in 04):** Gesamtfortschritt ≈ **30–35 %**; Phase 0 = 100 %; G0-SRV ≈ 20 %; Phase 1 ≈ 65 % (Umsetzung ~75 %, Abnahme 0 %); Phasen 2–8/10 ≈ 18–22 % (nur Konzeption); K1 ≈ 16 %; Governance-Track ≈ 25 %.

## 2. Kernbefunde (Top 10)

| # | Befund | Evidenz | Schwere |
|---|---|---|---|
| 1 | `G0-SRV-0`: Backup-/Restore-Nachweis fehlt; Stop-Regel verhindert jede Serveränderung | `GATE-STATUS.md` (`awaiting-backup-and-restore-evidence`) | **Blocker** |
| 2 | Branchdivergenz: `g0-governance` hat G0-SRV-/Analysedokumente **gelöscht** und Phase-1-Pause aus Status/AGENTS entfernt; Haupt-Checkout pflegt sie weiter | `git log/diff` der Worktrees | **Hoch** |
| 3 | K1-Task 3 wartet auf erneutes Spec-Review; Qualitätsreview blockiert; Tasks 4–14 (Kanonmatrix, Validator, Produktdoku, Testrunner, Auth-Abnahme) danach blockiert | `docs/project-control/K1-STATUS.md` (Worktree) | **Hoch** |
| 4 | Nicht replizierte Arbeit: 13 unpushed Commits, 15 ungetrackte G0-Pläne (38–120 KB je Datei), 2 unstaged Scanner-Dateien, 1 ungetrackter Migrationsplan (1.949 Zeilen) | `git status` der Worktrees | **Hoch** |
| 5 | `data_class='synthetic'` nur per DB-Default und Konvention — kein CHECK-Constraint, kein Test → Fail-closed-Grundsatz hier durchbrochen | `migrations/0002_tenants.sql`, `memberships.ts` | Mittel/Hoch |
| 6 | Keine RLS, keine negativen Isolationstests (Arbeitspaket C der Spezifikation); Tenant-Scoping nur anwendungsseitig | `memberships.ts`, Spec Arbeitspaket C | Mittel |
| 7 | Windows-Testrunner-Lücke: `npm test`-Glob findet laut Plan ggf. 0 Skripttests; in dieser Workstation existiert zudem kein `node_modules` → **kein lokales Gate aktuell ausführbar** | K1-Plan Task 6/9; `Test-Path node_modules` = False | Mittel |
| 8 | Zwei Gate-Programme (G0-SRV-0…12 vs. GATE-G0-Governance) existieren parallel, ohne modellierte Kopplung; Governance-Pins/Rollen/Freigabe (Ed25519 `REV-G0-DESIGN-APPROVAL`) fehlen vollständig | G0-Governance-Spec §13/§16, Masterplan | Mittel |
| 9 | Canon-Contract deckt Konzept-/Portaldokumente, aber **nicht** die Ground-Zero-/Project-Control-Dokumente | `canon-contract.mjs` `activeTextRules` | Mittel |
| 10 | Altserver M G1 läuft unverändert mit den V3/V4-Befunden weiter (NVML-Mismatch, Crashloop, Altgeheimnisse); Stand heute **nicht erneut geprüft** (Nur-Lese-Gebot) | V4-Befund; GATE-STATUS `server_changes_started: false` | Kontext |

## 3. Was bereits umgesetzt ist (Kurzform)

- **Phase 0 (Konzept):** abgenommen; C01–C12 gesetzt, X-Katalog (X01–X20) akzeptiert, U01–U12 übernommen, D01–D08/D10/D12–D24 gesetzt.
- **Phase-1-Schale:** Auth (Better Auth + Gate-Identity Ed25519/JWKS + SameSite-Isolation), Mandanten/Mitgliedschaften (Migration 0002, 2-Mandanten-Isolationstest), Portal mit 23 Routen, Migrationsrunner, 175 Tests im Haupt-Checkout (185 auf Kanon-Branch).
- **Kanonmechanik (Kanon-Branch):** `check:canon` (388 Zeilen + 10 Tests), `CANONICAL_DECISION_LOCKS` als alleinige Statusautorität, U09-Verriegelung, Windows-Vite-Fix.
- **Governance-Design (G0-Governance-Branch):** 3.968 Zeilen Spec, eingefroren mit Byte-Hash: Krypto-, Ledger-, Recovery-, Egress-, Witness- und Authentifizierungsverträge.
- **Konsolidierungsmechanik (Konsolidierungs-Branch):** Push-Graph-Scanner fail-closed (Kategorien inkl. `credential_like`, `operational_identity`), K1-Steuerung, Spur-A/B-Qualitätsrouting, Linux-Migrationsdesign.

## 4. Was noch offen ist (Kurzform)

1. Externer Backup-/Restore-Nachweis (**WV01/G0-SRV-0**) → dann Gates G0-SRV-1…12.
2. K1-Reviews (T3) und K1-Tasks 4–14; danach **Kanon-Merge der vier Linien** (Merge-Konflikte in `STATUS.md`/`AGENTS.project.md` vorprogrammiert).
3. Replikation/Persistenz der lokalen Einzelinstanz (Linux-Migrationskapsel Layer A–C ausführen).
4. Phase-1-Abnahme (Isolationstest-Zeremonie, AUDIT-02-Fortsetzung) — pausiert bis G0-SRV-12.
5. Phasen 2–10 komplett; D09 (Preise) und D11 (Codecs) in Wiedervorlage; K6–K8, H5–H8, Video/WebRTC bewusst gesperrt.

## 5. Innovationsspiegel

**Bestehend (hochwertig):** maschinell prüfbarer Kanon-Contract; fail-closed Push-Graph-Scanner mit TypeScript-AST-Adjudikation; Spur-A/B-Qualitätsrouting; RFC-8785-Kanonisierung + Append-only-Ledger + Witness-Marker im CT-Stil; Gate-Identity mit JWKS-Rotation; Computation-Passport- und Timer-Ledger-Konzepte.
**Vorschlagswert (non-normativ, §06):** DB-CHECK für `data_class`; GitHub-CI/Branch-Schutz sobald sauberer Push; maschinenlesbarer Gate-Status als JSON/Portal-Widget; Offline-Replikations-Kadenz als G0-Trockenübung; ECC-Nachweis-Runbook; axe-core-Accessibility-Gate; deterministische-Build-Evidenz.

## 6. Schlusswort

Die Risikostruktur hat sich seit V4 **nicht** im Kern verschoben (weiterhin `G0-SRV-0` als dominierender Blocker), aber die **Metariskenebene hat sich dramatisch verbessert und gleichzeitig verlagert**: Verbessert — das Projekt besitzt jetzt Werkzeuge, die seinen eigenen Kanon maschinell erzwingen (canon-contract, push-graph, Qualitätsrouting). Verlagert — das größte Sachrisiko ist nicht mehr Code oder Konzept, sondern **unreplizierte, un-reviewte, ungemergte Konsolidierungsarbeit auf einer einzigen Workstation**. Die empfohlene Reihenfolge (§07): K1-Reviews abschließen → Kanon konsolidieren und pushen → lokale Replikationskapsel (Layer A–C) → erst dann `G0-SRV-0`-Nachweis und Gatefolge.
