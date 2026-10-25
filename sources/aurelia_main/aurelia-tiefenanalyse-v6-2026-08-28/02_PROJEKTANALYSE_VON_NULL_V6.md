# AURELIA Tiefenanalyse V6 — Projektanalyse von Null

## 1. Was ist AURELIA

Wellbeing- und Dokumentationssoftware für **ausgebildete Praktiker** (radionische
Praxis: Zeugen, Sitzungen, versionierte Analyse-Kernel, serverautoritative
Harmonisierung, Archiv/Trend/Report). Modular, DSGVO-konform, serverautori­tativ.

**Ausdrücklich nicht:** Medizinprodukt, Diagnose, Heilversprechen, Physiknachweis,
Laien-Selbstbehandlung (Hard rule 1).

| Architektur-Grundsatz | Inhalt |
|---|---|
| Souveräner Kern | **ein** Originserver: GPU Server M G1 (EU), Ubuntu Server 24.04.4 LTS amd64 + minimales GNOME |
| Öffentliche Kante | Caddy aus demselben AURELIA-Baum; Lovable **nicht** in der Laufzeit (H1–H3, D24 gesetzt) |
| Hybrid-Entscheidung | H1 M G1 als Origin · H2 verschlüsseltes EU-Offsite-Backup · H3 Pflichtseiten aus dem Baum; H4 optional; H5–H8 gesperrt |
| Verträge > Libraries | Kernel-ABI, Computation Passport (`copyguard_digest`, `tenant_id`), WebSocket-Schema `v:1`, Emitter-Lease, AnalysisDraft, HarmonizationLane |
| Hardware M G1 | Ryzen 5 9600X · RTX 4000 SFF Ada 20 GB (kein MIG) · 128 GB DDR5 (aktiver ECC **unbewiesen**) · 2× 2 TB WD_BLACK SN850X RAID1 · Supermicro H13SAE-MF · IPMI/TPM2 |
| VRAM-Budget (C03) | 2 GB Runtime · 16 GB Jobs · 2 GB Reserve · CopyGuard = 0 GB VRAM |

## 2. ID-Systematik (verifiziert, 111 Produkt-IDs)

| Präfix | Bedeutung | Umfang | Stand |
|---|---|---:|---|
| D | Leitentscheidung | D01–D24 | 22 gesetzt (D01–D08, D10, D12–D24); D09/D11 empfohlen → WV02/WV06 |
| C | Betreiberbestätigung | C01–C12 | 12 gesetzt |
| X | „nicht umsetzbar/nicht relevant" | X01–X20 | 20 akzeptiert (24.08.) — nicht löschen, nicht implementieren |
| U | Unklar → Empfehlung übernommen | U01–U12 | 12 übernommen |
| K | Kozyrev-Katalog | K1–K8 | K1–K5 gesetzt, admin-togglebar (D22/D23); **K6–K8 gesperrt ohne Schalter** |
| H | Hybrid-Alternative | H1–H8 | H1–H3 gesetzt; H4 optional; H5–H8 gesperrt |
| L | Lovable-Flächenbewertung | L01–L09 | bewertet, nicht Runtime |
| O | Offen | O01–O10 | erledigt: O01, O02, O06, O08, O10; Rest → WV |
| WV | Wiedervorlage | WV01–WV06 | alle terminiert; WV01 identisch mit `G0-SRV-0` |
| G | Gates | G0-SRV-0…12 + GROUND-ZERO | 0 bestanden, 1 wartet, 2 teils, 10 gesperrt |
| docs/NN | Kapitel (kein Statusobjekt) | 00–26 + STATUS | 28 Dateien |

Kozyrev-Feinheit: zwei Personen getrennt (S. W. Kozyrev: p-adische Wavelets →
`kozyrev.padic.haar.v1`; N. A. Kozyrev: Zeitdichte → **kein** Nachweis, keine
UI-Behauptung). Flag-Kette **platform AND tenant AND session**, fail-closed,
auditiert; Admit prüft Flag vor VRAM-Zuteilung.

## 3. Phasenmodell (`docs/09-roadmap.md`)

0 → G0-SRV (eingeschoben) → 1–10, Phase 9 gestrichen. „Qualität vor Menge.
Nächste Phase nur bei ehrlicher Abnahme der vorigen." Details + Prozentwerte:
`04_PHASEN_UND_PROZENT_V6.md`.

## 4. Gate-Systeme

### 4.1 G0-SRV-0…12 (normativ, aktuell)

| Gate | Zweck | Status |
|---|---|---|
| G0-SRV-0 | Backup/Restore-Nachweis (≥2 externe Kopien, ≥1 offline/EU, SHA-256-Manifest, Git-Bundle, DB-Dumps, **echter Restore**, Protokoll) | **wartet auf Nachweis** |
| G0-SRV-1 | IPMI/KVM/Virtual Media Funktionstest | Betreiberzugang bestätigt, Funktionstest ausstehend |
| G0-SRV-2 | Hardware/Firmware/UEFI (inkl. Secure Boot Deployed Mode, ECC-Nachweis) | read-only Teilinventur, Abschluss ausstehend |
| G0-SRV-3 | RAID1/LUKS2/LVM-Installation | gesperrt |
| G0-SRV-4 | Boot/Encryption/Recovery (beide NVMe-Pfade) | gesperrt |
| G0-SRV-5 | Identitäten/SSH/VPN/Firewall | gesperrt |
| G0-SRV-6 | Minimales GNOME/Codex-Trennung | gesperrt |
| G0-SRV-7 | NVIDIA-Baseline (paketverwaltet, kein Runfile, kein CUDA) | gesperrt |
| G0-SRV-8 | Security/Logging/Updates (AppArmor, auditd, chrony) | gesperrt |
| G0-SRV-9 | PostgreSQL-16-Basis (intern, Checksums) | gesperrt |
| G0-SRV-10 | Offsite-Backup/Restore (RPO/RTO praktisch geprüft) | gesperrt |
| G0-SRV-11 | Selektiver Projekt-Restore (keine Altsecrets/Altservices) | gesperrt |
| G0-SRV-12 | Gesamtbaseline (`systemctl --failed` leer, Soak/Reboot-Tests) | gesperrt |

Stop-Regel: ohne `G0-SRV-0: bestanden` bleiben wipefs, Partitionierung,
`mdadm --create`, LUKS-Formatierung und OS-Installation **verboten**.

### 4.2 GATE-GOV-0 (historisch, nichtnormativ)

Das 3.968-Zeilen-Governance-Design auf `g0-governance` (RFC-8785-Signed Cores,
Append-only-Transition-Ledger, Witness-Marker, Trust-Roots, Lease-Kette,
Egress-Intents, Genesis-Manifest) ist laut `GATE-GOV-0-SUPPLEMENT.md` (K1)
**ausschließlich nichtnormativer Referenzname** für `GATE-G0`: keine Genesis,
keine Schlüssel/Signaturen autorisiert, `governance_genesis_authorized: false`.
Seine 14+1 Planentwürfe (17.091 Zeilen) sind **ungetrackt** und werden weder
importiert noch als Evidenz verwendet.

## 5. Codebasis

### 5.1 `src/` — 9.261 Zeilen

| Bereich | Zeilen | Bewertung |
|---|---:|---|
| `routes/` (23 Seitenrouten + `__root` + `api/auth/$`) | 2.553 | Konzeptportal produktionsreif (A11y: Skip-Link, aria-current, 44-px-Ziele); 20/23 Routen statisch |
| `lib/auth/` (16 Dateien) | 2.054 | **funktionsfähig implementiert**: Better Auth 1.6.30, `__Host-`-Cookies, Bearer-Fallback, Fetch-Metadata-Guard, beweisbarer Sign-out; Gate-Pfad (Ed25519/JWKS, 10-min-Token) dormant ohne `GROK_PROJECT_ID` |
| `lib/concept/` (9 Dateien) | 1.529 | ID-Systematik lückenlos, typisiert, konsistent; Textdrift an 5 Stellen (s. §6) |
| `lib/app-data/` (6 Dateien) | 700 | **toter Template-Code** (0 Importer außer Tests) |
| `lib/multiplayer/` (2 Dateien) | 579 | **toter Code** — voller WebRTC-Room-Client ohne Importer und ohne `/api/rtc`-Route; **widerspricht D10** |
| `components/` (4 Dateien) | 481 | Shell/UI produktionsreif; 2 von 4 Diagrammen ungenutzt |
| Rest (db, bridge, memberships, utils …) | 1.365 | `db.ts` produktionsreif (Neon/pg + PGLite, Parität, transaktionale Migrationen); `memberships.ts` = echter App-Kern (101 Z., 3 Server-Functions) |

Funktional echte App-Funktion: Anmeldung + bis zu 2 synthetische Mandanten +
Rollenlabel. **Kein RLS, kein Rollen-Enforcement, kein Step-up** — D04 ist
Anforderung, kein Zustand. PGLite ist in-memory: Sessions und Mandanten sind
per Design flüchtig.

### 5.2 `server/` + `migrations/` — 277 Zeilen

- `server/middleware/grok-pwa.ts` (111 Z.): Nitro-v3-Middleware, nur PWA-/OG-Head-
  Chrome (Manifest, iOS-Install-Tutorial, Streaming-Injection). Keine Geschäftslogik.
  Risiko: `x-forwarded-host ?? host` ungeprüft (Branding/Cache-Poisoning-Potenzial,
  gemildert durch `publicAppHost`-Filter und `VITE_PUBLIC_HOSTNAME`-Override).
- `migrations/0001_auth.sql` ≡ `migrations/auth/0001_auth.sql`: **byteidentisches
  Duplikat** (absichtlich, Basename-Keying verhindert Doppelausführung; kein
  Mechanik-Wächter für Drift).
- `migrations/0002_tenants.sql`: `tenants`/`memberships`, `data_class default
  'synthetic'` — **kein CHECK-Constraint, keine RLS**, `role` freier Text.
- **Kein echter HTTP-Server** (kein Express/Fastify/Hono): HTTP = Vite-Dev-Server +
  TanStack-Start-Server-Functions + Nitro (Vercel-Preset) im Build. Der
  Produktions-Originserver (PostgreSQL 16, systemd, timerd, emitterd, CopyGuard)
  existiert **ausschließlich als Dokumentation** — 0 Zeilen Code, absichtlich
  gate-gesteuert.

### 5.3 `scripts/` + `vite.config.ts` — 3.853 Zeilen

- 22 Skripte, ~1.662 Zeilen Tests in 7 `.test.mjs`; produktiv: Migrationskette
  (`migrate.mjs`/`migration-plan.mjs`), Auth-Invariante, PWA-/OG-Kette
  (`grok-pwa-*`), Sign-out-Plan; Agent-Werkzeuge: browser-smoke/-verdict,
  brand-check, preview-thumbnail, browser-guard.
- K1-Zweig zusätzlich: `check-push-graph.mjs` (531 Z., fail-closed Scanner,
  7 Kategorien, Exit 0/1/2, Limits 4096 Commits/100k Pfade, **TS-AST-Adjudikation**),
  `check-project-control-k1.mjs` (383 Z.) — beide mit Tests.
- `vite.config.ts`: Ports 8080 (dev, 0.0.0.0) / 8081 (preview); bewusst sortierte
  Plugin-Kette (pgliteBootstrap → authPopup → appEnv → PWA → tailwind →
  tanstackStart → nitro[Vercel] → react). **Kein CSP, keine Security-Header,
  kein Proxy-Block** im gesamten Repo.
- Windows-Portabilität: `npm test` (Glob in einfachen Quotes unter cmd.exe),
  `browser-guard` (`/workspace`, `/tmp`) und `preview-thumbnail` scheitern unter
  Windows; `startup.sh` ist POSIX-only.

### 5.4 Konfiguration

`.env.example` dokumentiert **keine** der tatsächlich gelesenen Variablen
(`VITE_AUTH_ENABLED`, `VITE_PUBLIC_HOSTNAME`, `GROK_AUTH_*` …) — echte Lücke.
`tsconfig.json` strict, `scripts/` nicht inkludiert. ESLint bewusst lax
(`no-explicit-any` off). `AGENTS.md` ist ein **fremder Host-Vertrag**
(Grok-Sandbox/Vercel-Modell), der der H1-Entscheidung entgegenläuft;
`AGENTS.project.md` erklärt den Vorrang, benennt den Konflikt aber nicht.

## 6. Dokumentation und Kanonwidersprüche

`docs/` = 6.202 Zeilen Markdown (28 Kapitel + project-control + superpowers).
Der ausführbare Kanonvertrag (`canon-contract.mjs`, `check:canon`) existiert
**nur auf `kanon-implementation`**, nicht im Haupt-Checkout — der Plan
`2026-08-24-aurelia-kanonbereinigung.md` ist im Hauptbaum nicht umgesetzt.

Dokumentierte Widersprüche Code↔Kanon (Haupt-Checkout):

| Stelle | Ist | Soll |
|---|---|---|
| `src/routes/roadmap.tsx:62` | Budget **3/3/12/2** | C03 = **2/16/2** |
| `src/routes/index.tsx:17` | „Phase 1 startet erst, wenn Sie es sagen" | Startwort 24.08., Phase 1 läuft (pausiert nur für G0-SRV) |
| `src/routes/leitplanken.tsx:57` | „keine Speicherung von Videos **im Standard**" | D10 absolut: keine Videogespräche |
| `src/lib/concept/nav.ts:25` | „X **zur Prüfung**" | „X **akzeptiert**" |
| `src/lib/concept/nav.ts:115` | „DSGVO, E2E, **WebRTC**" | „…, **kein Video**" |
| `src/lib/concept/standalone.ts:117` | „Ihr Wort zu X und Phase 1" (offen) | beides abgeschlossen |
| `docs/02-architecture.md:43` | „später optional WebRTC" | D10: kein WebRTC |
| `docs/03-security-dsgvo.md:30` | Video Phase 9 / WebRTC Insertable Streams | Phase 9 gestrichen |
| `docs/23-id-schema.md:17` | „D08–D12 empfohlen", „Auth ist aus" | D08/D10/D12 gesetzt, Auth an |

Dazu: Debian-/2×1-TB-Restbestände im Portalcode (`decisions.ts:32,38,184`,
`diagrams.tsx:8`, Feld `mehrwertFuerDebian` u. a.) — laut
`docs/project-control/README.md` bewusst an AUDIT-02 gebunden. Einstiegsdokumente
(`README.md`, `llms.txt`, `.github/copilot-instructions.md`, `docs/00-index.md`,
`docs/25-offen.md`) nennen die Phase-1-Pause/das G0-Gate nicht. WV03- und
WV05-Bezeichnungen sind zwischen `26-wiedervorlage.md`, `STATUS.md` und
`09-roadmap.md` uneinheitlich.

Konsistenz stark an den kritischen Stellen: Ziel-ISO/SHA-256, ECC-Status,
Destruktionssperre, VRAM 2/16/2, `data_class=synthetic` — überall identisch.

## 7. Git-Topologie und Worktrees

```text
b858ccd main (10)
  └─ 9a7be72 → e55ed59 → a726346          (vorbereitung-Basis)
        ├─ 8706186  codex/aurelia-vorbereitung (14) ← HAUPT-CHECKOUT  [Ground-Zero-Doku: 2.543 Zeilen in 29 Dateien]
        │     └─ codex/aurelia-konsolidierung (41 lokal / 28 remote, 13 unpushed) [K1 + Migration]
        └─ (a726346) codex/aurelia-kanon-implementation (27) [Kanon-Contract, +13]
              └─ codex/aurelia-g0-governance (45) [Governance-Design 3.968 Z., +18]
```

| Worktree | Branch | Status | Besonderheit |
|---|---|---|---|
| Hauptverzeichnis | vorbereitung `8706186` | sauber, **ohne node_modules** | verbindlicher Lesepfad |
| `.worktrees/aurelia-kanon` | kanon `b20ee87` | sauber | node_modules vorhanden; **einziger Träger des Kanon-Contracts** |
| `.worktrees/aurelia-g0-governance` | g0 `a6a8e7d` | **15 ungetrackte Dateien** (14 Pläne + Status-HTML, 17.091 Z.) | node_modules vorhanden |
| `.worktrees/aurelia-konsolidierung` | konsolidierung `aec827f` | 2 unstaged Scanner-Dateien (evidence-bearing) + 1 ungetrackter Migrationsplan (1.949 Z.) | node_modules vorhanden; **13 Commits unpushed** |

Kanon-Fakten (verifiziert): `g0-governance` und `kanon-implementation` enthalten
die Ground-Zero-Dokumente **nie** (hinzugefügt erst in `8706186`); kein
Lösch-Commit existiert. `g0-governance` trägt daher noch Debian-Kanon
(31 Debian-Treffer in docs/, „Debian Bookworm" als Ziel-OS in
`02-architecture.md`) und kennt die Phase-1-Pause nicht. Konsolidierung hat die
meisten Debian-Treffer (41) — als dokumentierte, nicht-executable Historie
(Sanitisierungs-/Supersession-Kontext). → Ein Merge der Nebenzweige ohne
Rebase auf `8706186` würde Kanonkonflikte in `STATUS.md`/`AGENTS.project.md`
erzeugen; `GATE-GOV-0-SUPPLEMENT` und K1 verhindern das currently durch
Merge-/Rebase-/Cherry-pick-Verbote.

## 8. GitHub-Fernzustand (verifiziert 28.08.)

| Aspekt | Befund |
|---|---|
| Repo | privat (anonym 404), `main` = `b858ccd` = HEAD |
| Branches remote | 5 (main, vorbereitung, kanon, g0, konsolidierung) — 4 synchron, konsolidierung **13 zurück** |
| Tags | 0 |
| PRs | 0 Refs (`refs/pull/*` leer) |
| CI | **kein Workflow definiert, nie gewesen** (`.github/workflows` fehlt; keine yml/yaml in der Historie) |
| Issues/Branch-Protection | nicht beobachtbar (gh **401**: Keyring-Token von Account `radiquant` ungültig) |
| Letzter Push | main 24.08. · konsolidierung 26.08. (`029bdce`, mit Evidenzdokument `K1-SYNC-EVIDENCE-2026-08-26.md`) |
| Publikations-Gate | formal `blocked` (Kategorien `credential_like`, `operational_identity`); einzige autorisierte Ausnahme: Fast-Forward-Push von konsolidierung unter 8 Bedingungen (Migrationsdesign §3) |

## 9. Lokale Geheimnis-/Evidenzlage

`.gitignore` hält `aurelia-tiefenanalyse*/`, `external-analyses/**/source/`,
`.env*`, `*.pem/key`, `secrets/`, `witness-samples/` fern. Die 52 ignorierten
Analyse-/Quelldateien (inkl. V3-Klartext-Datenbankgeheimnis) existieren nur
lokal und sind im Migrationsdesign als „separat verschlüsselt zu sichernde,
nicht zu veröffentlichende Masse" eingestuft. Historische Git-Objekte mit
Befunden bleiben erreichbar (Sanitisierung nur Branch-Tips V1/V2).

## 10. Gesamtimplikation

Der Projektzustand ist **konsistent und ehrlich dokumentiert**; es fehlt nicht
Konzept, sondern **Ausführung und Freigabe** an genau vier Stellen: Gate-Nachweis
(G0-SRV-0), Review-Freigabe (K1-Task 3), Replikation (Push/Kapsel) und
automatisierte Durchsetzung (CI/Protections/RLS/Constraints).
