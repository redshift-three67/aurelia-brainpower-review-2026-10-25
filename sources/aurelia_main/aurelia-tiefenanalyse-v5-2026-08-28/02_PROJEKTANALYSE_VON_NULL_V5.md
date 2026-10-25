# AURELIA — Tiefenanalyse V5: Projektanalyse von Grund auf

**Stand: 2026-08-28, 09:28 CEST · Nur-Lese-Analyse**

---

## 1. Identität und Verfassung des Projekts

| Attribut | Wert (Quelle: `AGENTS.project.md`, `docs/STATUS.md`) |
|---|---|
| Produkt | AURELIA — Wellbeing-/Dokumentationssoftware für geschulte Praktiker; **kein Medizinprodukt**, keine Diagnose/Therapie |
| Phase | 1 „Gehäuse" — Status `phase-1-paused-for-g0-server-ground-zero` |
| Aktives Gate | `G0-SRV-GROUND-ZERO`, aktuelles Teilgate `G0-SRV-0` = externer Backup-/Restore-Nachweis (ausstehend) |
| Auth / DB | ON / ON; Datenklasse ausschließlich `synthetic` |
| Zielsystem | GPU Server M G1 (Ryzen 5 9600X, RTX 4000 SFF Ada 20 GB, 128 GB DDR5, 2×2 TB WD_BLACK SN850X RAID1), Ubuntu Server 24.04.4 LTS amd64 + minimales GNOME |
| VRAM-Budget (C03) | 2 GB Runtime · 16 GB Jobs · 2 GB Reserve; CopyGuard = 0 GB VRAM (RAM/NVMe) |
| Repo | `redshift-three67/aurelia` (privat), Sprache UI: Deutsch |
| Verfassungsregeln | 26 Hard Rules (u. a. CopyGuard auf jedem sichtbaren Satz, Server als Uhr, Kernel-Versionierung Radi144→Works→Morphic→Blohm→Thoms→Copen, Computation Passport mit `copyguard_digest`/`tenant_id`, WCAG 2.2 AA/BFSG, Spooky2 nur via `aurelia-emitterd` mit Lease→Arming→ACK, Kozyrev K1–K5 admin-togglebar / K6–K8 ohne Kernel-ID, X-Katalog akzeptiert ohne Implementierung, kein Video/WebRTC, `destructive_actions_allowed: false`) |

**Locked vs. pending (Verfassung):** Gesetzt D01–D08, D10, D12–D24, C01–C12, X-Katalog, K1–K5, H1–H3, Phase 1 · Empfohlen/Wiedervorlage D09 (Preise), D11 (Codecs), WV01–WV06 · Gesperrt K6–K8, H5–H8, Video/WebRTC.

## 2. Repository-Topologie (verifiziert am 28.08.2026, 09:2x CEST)

### 2.1 Branches und Remote-Heads

| Branch | Lokal | Remote (`ls-remote`) | Delta | Rolle |
|---|---|---|---|---|
| `main` | `b858ccd` | `b858ccd` | synchron | Ursprung „Start Phase 1 shell" |
| `codex/aurelia-vorbereitung` (Haupt-Checkout) | `8706186` | `8706186` | synchron | Kanon + Project-Control + Ground-Zero-Planung (4 Commits > main) |
| `codex/aurelia-kanon-implementation` (Worktree `aurelia-kanon`) | `b20ee87` | `b20ee87` | synchron | Kanonbereinigung, 14 Commits > Vorbereitung (Abzweig `a726346`) |
| `codex/aurelia-g0-governance` (Worktree `aurelia-g0-governance`) | `a6a8e7d` | `a6a8e7d` | synchron | Kanon + Governance-Design, 32 Commits > Vorbereitung |
| `codex/aurelia-konsolidierung` (Worktree `aurelia-konsolidierung`) | `aec827f` | `029bdce` | **lokal 13 Commits voraus** | K1-Konsolidierung + Security-Scanner, 27 Commits > Vorbereitung |

### 2.2 Arbeitsbauminventar

| Ort | Zustand |
|---|---|
| Haupt-Checkout | sauber (0 uncommittete Änderungen), **ohne `node_modules`** → Build-/Test-/Typecheck-Gates hier nicht ausführbar |
| `.worktrees/aurelia-kanon` | sauber |
| `.worktrees/aurelia-g0-governance` | **15 ungetrackte Dateien**: Masterplan + Teilpläne `2026-08-24-aurelia-g0-01…13-*.md` (38–120 KB je Datei) + Status-HTML — der gesamte Implementierungsfahrplan der Governance existiert nur lokal |
| `.worktrees/aurelia-konsolidierung` | **2 unstaged Dateien** (`scripts/check-push-graph.mjs`/`.test.mjs`, ±445 Zeilen, „evidence-bearing dirty overlay") + **1 ungetrackter Plan** (`2026-08-27-aurelia-linux-workstation-migration-recovery.md`, 1.949 Zeilen) |
| Analysarchive | `aurelia-tiefenanalyse{,-2026-08-25,-v3…,-v4…}` (Root), `docs/project-control/external-analyses/` (V1–V3 verifiziert; `source/`-Unterordner durch `.gitignore` von GitHub ausgeschlossen — V3-Quelle enthält Klartext-DB-Geheimnis) |

## 3. Codebasis (Haupt-Checkout, 161 getrackte Dateien, `src/` 8.572 Zeilen)

### 3.1 Anwendung / Portal (Phase-1-Schale)

| Bereich | Dateien (Auswahl) | Befund |
|---|---|---|
| Router/Shell | `src/router.tsx`, `src/routes/__root.tsx`, `src/routeTree.gen.ts`, `src/styles.css` | TanStack Start; Fehlerkomponente gebunden; Cursor-Basisregel |
| Portalrouten (23) | `index`, `architektur`, `compute`, `daten`, `entscheidungen`, `freigabe`, `gestaltung`, `hardware`, `identitaet`, `kozyrev`, `leitplanken`, `live`, `lovable`, `module`, `offen`, `praxis`, `repos`, `roadmap`, `sicherheit`, `timer`, `wellbeing`, `zwischenablage`, `login` | Konzeptportal mit Sage/Parchment-Tokens; Diagramme in `src/components/concept/` |
| Konzeptdaten | `src/lib/concept/{decisions,freigabe,id-legend,kozyrev-labor,standalone,offen,wiedervorlage,nav,lovable-nutzen}.ts` | ID-Familien D/C/X/U/K/H/O/WV als TS-Quellen des Kanons |
| Auth | `gate-identity.server.ts` (Ed25519/EdDSA-JWT, JWKS-Cache TTL 5 min, `maxTokenAge` 10 min, Audience `app:<GROK_PROJECT_ID>`), `gate-session.server.ts`, `middleware.ts` (`authMiddleware` → `requireUserId` → `context.userId` als Chokepoint), `isolation.server.ts` (Fetch-Metadata-Sibling-Isolation, 403 bei Cross-Site), `server.ts` (Better Auth 1.6.30), `login.tsx`, `api/auth/$.ts` | funktionsfähig implementiert; Passkeys auf Ubuntu = WV03 später |
| Mandanten | `migrations/0002_tenants.sql` (`tenants` mit `data_class default 'synthetic'`, `memberships` UNIQUE(user_id, tenant_id)), `src/lib/praxis/memberships.ts` (`ensurePrimaryTenant`, `addSecondTenant` max. 2, alles server-side scoped), `praxis.tsx` (Mandanten-UI + Isolationstest-Button) | implementiert; **kein DB-CHECK auf `data_class`, keine RLS** |
| App-Data-Gate | `src/lib/app-data/client.server.ts` (Bearer-Gate, 401→Login-Redirect, 5-s-Failure-Memo keyed by Token-Identität, POST-only, Cross-Site-Guard) | implementiert |
| Plattform | `scripts/with-app-env.mjs` (App-Env-Wrapper; auf Kanon-Branch: direkte Vite-JS-CLI-Invocation — Windows-`.cmd`-Fix), `check-auth-invariant.mjs`, `grok-pwa-*`, `browser-smoke*`, `brand-check`, `sign-out-plan`, `migration-plan`, `migrate.mjs` | Dev-/QA-Infrastruktur vorhanden |
| Status | In dieser Workstation **nicht lauffähig ohne Installation** (kein `node_modules`) — kein Befund gegen die Codebasis, aber Einschränkung der lokalen Qualitätskette |

### 3.2 Testinventar (statisch gezählt; Ausführung in V5 nicht erfolgt)

| Suite | Haupt-Checkout | Kanon-Branch |
|---|---|---|
| `grok-pwa-plugin.test.mjs` | 47 | 47 |
| `browser-smoke-verdict.test.mjs` | 40 | 40 |
| `sign-out-plan.test.mjs` | 18 | 18 |
| `brand-check.test.mjs` | 14 | 14 |
| `with-app-env.test.mjs` | 14 | 14 |
| `check-auth-invariant.test.mjs` | 11 | 11 |
| `migration-plan.test.mjs` | 7 | 7 |
| `gate-identity.test.ts` | 14 | 14 |
| `app-data.test.ts` | 10 | 10 |
| `canon-contract.test.mjs` | — | **10** |
| **Summe** | **175** | **185** |

Bekannter, dokumentierter Defekt: der `scripts/**/*.test.mjs`-Glob des Node-Testrunners findet auf Windows ggf. **0** Skripttests (K1-Plan Task 6/9) — Qualitätsinfrastruktur-Lücke, behoben erst in K1 Task 12/13.

### 3.3 Neue Security-/Governance-Mechanik (Branches)

| Mechanismus | Branch | Funktionsweise (Kurzform) |
|---|---|---|
| **Canon-Contract** `scripts/canon-contract.mjs` (+10 Tests, `npm run check:canon`) | kanon / g0-governance | Schreibgeschützter Validator: exakte D-Menge gegen `CANONICAL_DECISION_LOCKS` (alleinige Statusautorität), ID-Familien C/X/U/K/H/O/WV strukturell, ~20 prohibited/required-Regexe über aktive Docs/Routen; deterministische global/sticky-Regexe; U09-Verriegelung („Phase 1 Gehäuse gestartet" pflicht, „kein Phase 1" verboten) |
| **Push-Graph-Scanner** `scripts/check-push-graph.mjs` (+ `check:push-graph`; 4 Security-Fixes) | konsolidierung | Fail-closed Vollgraph-Scan (`rev-list --topo-order` + `ls-tree -r`, Limits 4096 Commits/100k Pfade, Root-Bindung per realpath/dev/ino); Kategorien `credential_like`, `env_or_key_material`, `absolute_user_path`, `unc_path`, `internal_host`, `operational_identity`, `raw_source_tree`, `unscannable`; Exit 0/1/2, Diagnosecodes ohne Fundwerte; TS-AST-Adjudikation unterdrückt nur echte PropertySignature-Typreferenzen (fail-closed sonst) |
| **K1-Steuerung** `scripts/check-project-control-k1.mjs` (`check:k1-control`) | konsolidierung | Branch-, Basis-Ancestry-, Manifest-Provenienz-, Namensraum- und History-Schrankenprüfung |
| **Qualitätsrouting** `docs/project-control/QUALITY-ROUTING.md` | konsolidierung | Spur A (Fast Assurance, deterministisch/reversibel/nicht-sicherheitsrelevant) vs. Spur B (Critical Assurance: Auth, Secrets, Krypto, Migrationen, Gates, Publikation → Spec-Review, dann Qualitätsreview, P0–P2 blockieren); unklare Risikoklasse = fail-closed Spur B |
| **G0-Governance-Spec** (3.968 Zeilen, eingefroren, Byte-Hash) | g0-governance | RFC-8785-Kanonisierung (Signed Cores), Append-only Transition-Ledger mit `previousEventHash`-Kette + Nonce-Einmaligkeit, zweistufige externe Trust-Aktivierung, `trust-roots.json` append-only, Lease-Kette Claim→Accepted→Dispatch→Settled, versiegelter Egress-Intent + Idempotenz-Tombstone + One-Shot-Token, GitHub-Marker `refs/heads/aurelia-recovery-markers/<sha>` mit CAS-Preconditions (A→B→A-Replay scheitert), Ed25519-Attestations mit geschlossenen Purposes, Genesis-Manifest, 10-Punkte-Abnahme |
| **Linux-Migrationsdesign** `2026-08-27-…-migration-recovery-design.md` | konsolidierung | 3-Schichten-Architektur: A privater GitHub-Push (nur committete, freigegebene Doku, enge Ausnahmebedingungen), B verschlüsselte Recovery-Kapsel (Git-Bundle aller Refs + Dirty-Patch + TAR der G0-Pläne + SHA256SUMS), C verschlüsseltes Cold-Backup (2 Ziele, ≥1 offline, `.codex`/`.ssh`/Recovery-Codes/52 ignorierte Dateien); Restaurationsnachweis in 13 Schritten; Lösch-Gate nur durch Betreiber |

## 4. Gate- und Phasensystematik

**Serverprogramm G0-SRV-0…12** (Haupt-Repo, `GATE-STATUS.md` + Serverdesign §11): 0 Backup/Restore (**wartet auf Nachweis**) → 1 IPMI/KVM/VirtualMedia (Betreiber bestätigt, Funktionstest ausstehend) → 2 Hardware/Firmware/UEFI (read-only Teilinventur vorhanden) → 3 RAID1/LUKS2/LVM-Installation (gesperrt) → 4 Boot/Encryption/Recovery → 5 Identitäten/SSH/VPN/Firewall → 6 minimales GNOME/Codex → 7 NVIDIA-Baseline ohne CUDA → 8 Security/Logging/Updates → 9 PostgreSQL-16-Basis → 10 Offsite-Backup/Restore → 11 selektiver Projekt-Restore → 12 Gesamtbaseline. Stop-Regel: ohne `G0-SRV-0: bestanden` bleiben `wipefs`, Partitionierung, `mdadm --create`, LUKS, OS-Installation verboten. Voraussetzungstabelle: 6/6 Betreiberbestätigungen, 0/6 technische Abnahmen.

**Governance-Stop-Gates** (G0-Governance-Spec §13): `GATE-G0`, `GATE-DATAFLOW`, `GATE-PROFILE`, `GATE-ART9`, `GATE-MODULE`, `GATE-CUDA`, `GATE-HARDWARE`, `GATE-PILOT`, `GATE-24X7` — konzeptionell gestaffelt, **noch nicht mit dem G0-SRV-Programm verknüpft**.

**K1-Kanonkonsolidierung** (konsolidierung): Task 1 Steuerung/Provenienz ✅ · Task 2 Governance-Grenze `GATE-GOV-0` ✅ · Task 3 Push-Graph-Scanner 🟡 (4 Fixes committet, Overlap-Korrektur uncommittet, Spec-Review ausstehend, Qualitätsreview blockiert) · Tasks 4–14 ⬜ blockiert (Kanonmatrix, Kanonvalidator, Produktdoku, Testrunner-Glob-Fix, Auth-Abnahme, Lint, `K1-VERIFICATION.md` erst in Task 14).

## 5. GitHub-Seite (nur lesend)

- Private Repo → anonyme API 404; beobachtbar waren ausschließlich die fünf Branch-Heads via `ls-remote`.
- Auffällig: `codex/aurelia-konsolidierung` remote hinkt um 13 Commits hinterher; kein PR-/CI-Mechanismus aus der Ferne verifizierbar (die Governance-Dokumente markieren GitHub-Branchschutz-Evidenz selbst als „unknown/red" — konsistent mit dieser Beobachtung).
- Historie: einmaliger, abgegrenzter Push am 26.08. mit Evidenzdokument (`K1-SYNC-EVIDENCE-2026-08-26.md`); `publication_gate` bleibt formal `blocked` (Kategorien `credential_like`, `operational_identity`).

## 6. Dokumentationsbestand

27 nummerierte Kapiteldateien (`docs/00–26`) + `STATUS.md` + `project-control/` (README, `ground-zero/GATE-STATUS.md`, K1-Status/-Evidenz/-Routing auf Branch, externe Analysen V1–V3 verifiziert) + `superpowers/` Specs/Pläne (Vorbereitungsdesign, Kanonbereinigung, Ground-Zero-Serverdesign + Preflight, G0-Governance-Design, K1-Design/Plan, Task-3-Korrekturkette, Linux-Migration) — insgesamt 5.177 Zeilen nur in `docs/`. Bekannt: bewusst nicht bereinigte Altverweise (Debian/Bookworm, 2×1 TB) im Portal, bereinigt erst im wiederaufgenommenen AUDIT-02.
