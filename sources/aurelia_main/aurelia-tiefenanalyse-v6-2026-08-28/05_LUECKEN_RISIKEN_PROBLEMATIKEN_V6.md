# AURELIA Tiefenanalyse V6 — Lücken, Risiken, Problematiken

Schweregrade: 🔴 Blocker/Kritisch · 🟠 Hoch · 🟡 Mittel · 🔵 Niedrig/Kontext.
Neu in V6 gekennzeichnet mit **[V6]**, gegenüber V5 präzisiert mit **[korr.]**.

## L1 — Kritischer Pfad (G0-SRV)

| ID | Befund | Schwere |
|---|---|---|
| L1.1 | `G0-SRV-0`: externer Backup-/Restore-Nachweis fehlt weiter (seit 25.08.) — dominierender Blocker aller Produktphasen | 🔴 |
| L1.2 | 0/6 technische Abnahmen der Gate-Voraussetzungen — nur Betreiberbestätigungen | 🟠 |
| L1.3 | ECC-Status der 128 GB RAM unbewiesen (`Memory Error Correction Type: None`); erst Teilnummer-/BIOS-/EDAC-Nachweis macht ECC zur Tatsache | 🟠 |
| L1.4 | Altserver M G1 läuft unverändert mit V3/V4-Befunden weiter (Root-SSH-fähig, Altgeheimnisse, NVML-Mismatch, Crashloop); Stand 25.08., seither nicht erneut geprüft | 🟡 |
| L1.5 | SN850X ohne Enterprise-PLP; USV ersetzt keine PLP bei Netzteil-/Firmware-/Hostfehlern | 🟡 |

## L2 — Konsolidierung, Publikation, Replikation

| ID | Befund | Schwere |
|---|---|---|
| L2.1 | **Single Point of Failure:** 13 unpushed Commits + 17.091 Zeilen ungetrackte Governance-Pläne + 1.949 Zeilen ungetrackter Migrationsplan + 2 unstaged Scanner-Dateien — alles nur auf einer Workstation, die laut eigenem Design demnächst neu installiert wird | 🟠 |
| L2.2 | K1-Task-3-Review-Stau: erneutes Spec-Review ausstehend, Qualitätsreview blockiert, Tasks 4–14 gesperrt; kein Eskalationsfenster definiert | 🟠 |
| L2.3 | **[korr.]** Divergente Kanonlinien: `g0-governance`/`kanon-implementation` enthalten die Ground-Zero-/Analyse-Dokumente **nie** (V5 sprach fälschlich von „gelöscht" — verifiziert: hinzugefügt erst in `8706186`, kein Lösch-Commit). Praktisches Risiko bleibt: g0 trägt Debian-Kanon + „Phase 1 läuft" ohne Pause; Merge ohne Rebase auf `8706186` erzeugt Kanonkonflikte in `STATUS.md`/`AGENTS.project.md` | 🟡 |
| L2.4 | Zwei Gate-Vokabulare parallel (`G0-SRV-0…12` normativ vs. `GATE-G0/DATAFLOW/…` historisch); Kopplung nur über das nichtnormative `GATE-GOV-0-SUPPLEMENT` | 🟡 |
| L2.5 | Publikations-Gate formal `blocked` (5 Scanner-Records `credential_like`/`operational_identity`/… auch auf bereits veröffentlichten Branches); Push nur unter der 8-Bedingungs-Ausnahme des Migrationsdesigns | 🟡 |
| L2.6 | Kanon-Contract (`check:canon`) existiert nur auf `kanon-implementation`; Haupt-Checkout ohne maschinelle Kanonprüfung; `docs/project-control/**` nicht abgedeckt (K1-T4 blockiert) | 🟡 |
| L2.7 | **[V6]** Zwei Gate-Programme teilen einen Namensraum-Anfang („G0") — Verwechslungsgefahr für neue Mitwirkende; Lesepfad im Hauptbaum erwähnt das Governance-Programm nicht | 🔵 |

## L3 — Code- und Datenlücken

| ID | Befund | Schwere |
|---|---|---|
| L3.1 | Kein RLS, kein CHECK-Constraint: `data_class`/`role` freier Text (`migrations/0002_tenants.sql`); Isolation nur applikativ (3 Server-Functions); D04 nicht umgesetzt; keine negativen Isolationstests | 🟠 |
| L3.2 | Kein CSP/Security-Header nirgends (Vite, Nitro, Root) trotz Session-Cookie + iFrame-Preview | 🟠 |
| L3.3 | `x-forwarded-host`-Vertrauen in zwei Pfaden (`server/middleware/grok-pwa.ts:35`, `vite.config.ts:88`) — Branding-/OAuth-Redirect-Risiko, gemildert, aber nicht verifiziert | 🟡 |
| L3.4 | **[korr.]** Qualitätskette: Haupt-Checkout ohne `node_modules` → dort kein Gate ausführbar. **Aber:** alle 3 Worktrees haben vollständige Installationen → E1 ohne Freigabe möglich. Windows bleibt blockiert durch `npm test`-Glob (cmd.exe-Quoting) + `browser-guard`-Pfade (`/workspace`, `/tmp`) | 🟡 |
| L3.5 | 1.279 Zeilen toter Code (`app-data` 700, `multiplayer` 579); P2P widerspricht D10 im Baum | 🟡 |
| L3.6 | Portal-Textdrift: 9 dokumentierte Widersprüche (u. a. `roadmap.tsx:62` Budget 3/3/12/2 vs. C03 2/16/2; `index.tsx:17` Phase-1-Status; `nav.ts:115` WebRTC) | 🟡 |
| L3.7 | `.env.example` dokumentiert keine der gelesenen Variablen (`VITE_AUTH_ENABLED`, `GROK_AUTH_*`, `VITE_PUBLIC_HOSTNAME` …) | 🟡 |
| L3.8 | Duplikatmigration ohne Drift-Wächter (`migrations/auth/0001_auth.sql` ≡ `0001_auth.sql`, md5-identisch heute) | 🔵 |
| L3.9 | Preview-Client-Secret im Klartext im Repo (`preview.ts:19-21`, bewusst niederprivilegiert); E-Mail/Passwort hardcodiert an (`email-password.ts:7`); kein Rate-Limit sichtbar | 🟡 |
| L3.10 | Portal-Altverweise Debian/2×1 TB im Code — bewusst an AUDIT-02 gebunden | 🔵 |
| L3.11 | `ensurePrimaryTenant` ohne `ON CONFLICT`/Transaktion → Konkurrenz-Fehlerbild 500; `memberships.id serial` vs. clientseitige UUIDs (zwei ID-Strategien) | 🔵 |
| L3.12 | Install-Seite referenziert `/__grok/install/assets/**`, das kein Code im Repo bedient (nur Plattform-CDN) | 🔵 |

## L4 — Infrastruktur/Plattform

| ID | Befund | Schwere |
|---|---|---|
| L4.1 | **[V6, verifiziert]** Kein CI definiert (`.github/workflows` nie existent); 0 PRs, 0 Tags; Branch-Protection nicht beobachtbar → Qualitätskette nur lokal erzwingbar | 🟡 |
| L4.2 | **[V6]** `gh`-Keyring-Token ungültig (HTTP 401, Account `radiquant`) — API-Evidenz (Issues, CI, Protections) derzeit nicht beschaffbar; git selbst funktioniert (Credential Manager) | 🟡 |
| L4.3 | Vorabversions-Stack: `nitro 3.0.260610-beta`, Vite 8, Better Auth ~1.6.30, React 19.2 — Upgrade-/Bruchrisiko vor Phase 2 | 🟡 |
| L4.4 | 52 ignorierte Analyse-/Quelldateien (inkl. V3-Klartext-DB-Geheimnis) nur durch `.gitignore` + Disziplin geschützt; Migration Layer C sieht verschlüsselte Kopie vor, nicht erstellt | 🟡 |
| L4.5 | Historische Git-Objekte mit Befunden weiter erreichbar (Sanitisierung nur Branch-Tips V1/V2) | 🔵 |

## L5 — Prozess/Menschen

| ID | Befund | Schwere |
|---|---|---|
| L5.1 | Nicht delegierbare Betreiberfreigaben: `G0-SRV-0`-Nachweis, Gate-Entscheidungen, Destruktionsfreigabe, K1-Publikationsentscheidung, `REV-G0-DESIGN-APPROVAL` | 🟠 |
| L5.2 | Review-Kaskade kann sich selbst blockieren (T3-Spec → Qualität → T4–T14); QUALITY-ROUTING §4 sieht regulär eine Korrekturschleife vor, aber keinen Eskalations-/Timeout-Mechanismus | 🟡 |
| L5.3 | Externe Provider-Assets fehlen (K1-T12 `external_blocker`) — dürfen nicht erfunden werden; blockiert Konsolidierungsabschluss | 🔵 |
| L5.4 | Einstiegsdokumente (`README.md`, `llms.txt`, `copilot-instructions.md`, `00-index.md`, `25-offen.md`) nennen Pause/Gate nicht → neuer Mitwirkender liest veralteten Status | 🔵 |

## Risikomatrix (Auswirkung × Eintritt)

| | Eintritt hoch | mittel | niedrig |
|---|---|---|---|
| **Auswirkung hoch** | L2.1 (Arbeitsverlust), L1.1 (Stillstand) | L2.3 (Kanonbruch beim Merge), L3.1 (Isolationslücke) | L1.3 (ECC) |
| **Auswirkung mittel** | L3.4/L4.1 (Qualität unverankert) | L2.2 (Review-Stau), L2.4 (Doppelbuchführung), L3.2 (Header), L4.3 (Stack) | L3.3, L4.2 |
| **Auswirkung niedrig** | L5.3 | L3.6, L3.7, L4.4 | L3.8, L3.10–3.12, L4.5, L2.7, L5.4 |

## Fazit

Drei dominante Familien: **(1) Nachweislücken** (G0-SRV-0, Abnahmen, E1),
**(2) Konsolidierungslücken** (unpushed/untracked, Review-Stau, Kanonlinien),
**(3) Durchsetzungslücken** (RLS/Constraints, CSP, CI, Windows-Runner).
Es fehlt primär **Ausführung und Freigabe**, nicht Konzept.
