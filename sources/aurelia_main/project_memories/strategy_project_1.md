# AURELIA — Strategischer Optimierungsplan / Strategic Optimization Plan

> Review mode: passive, static, read-only architecture review. No project source, configuration, migration, dependency, test, or Git-history artifact was modified. This document is the sole review-created artifact.
>
> Audit snapshot: `HEAD=8706186af01e10e4253e25abb31bf3577110dae4`, branch `codex/aurelia-vorbereitung`. Initial source-manifest fingerprint: `a6095738594d696b32e828a8444398bf931a51fe6f4afacb6cd139456c88fa01`. Initial exhaustive-status fingerprint: `dd34840574086511cc907809a911d76ad9c5f3966dea20f2eef334d0389f0659`.

```json
{
  "document": "project_memories/strategy_project_1.md",
  "review_mode": "static_read_only_except_requested_report",
  "snapshot": {
    "head": "8706186af01e10e4253e25abb31bf3577110dae4",
    "branch": "codex/aurelia-vorbereitung",
    "source_manifest_sha256": "a6095738594d696b32e828a8444398bf931a51fe6f4afacb6cd139456c88fa01",
    "status_sha256": "dd34840574086511cc907809a911d76ad9c5f3966dea20f2eef334d0389f0659"
  },
  "scope": {
    "reviewed": ["src/", "server/", "scripts/", "migrations/", "docs/", "package.json", "vite.config.ts", "startup.sh", "AGENTS.project.md", "SECURITY.md"],
    "not_executed": ["tests", "build", "typecheck", "dev_server", "database", "network_calls", "browser"],
    "excluded_for_privacy": [".env*", ".grok/", "aurelia-tiefenanalyse*/", "docs/project-control/external-analyses/**/source/"],
    "reason": "Excluded locations are ignored or explicitly documented as possible secret, credential, or confidential operational-evidence stores."
  }
}
```

## 1. Management summary / Management-Zusammenfassung

AURELIA ist gegenwärtig keine Compute-, Timer-, Emitter- oder medizinische Anwendung. Der implementierte Produktkern ist eine TanStack Start/React Phase-1-Shell mit Authentifizierung, synthetischen Mandanten und einer umfangreichen, statisch gerenderten Produktverfassung. Die Server-Zielarchitektur ist normativ detailliert dokumentiert, aber noch nicht als Laufzeit implementiert.

Die stärksten vorhandenen Eigenschaften sind: klarer Sicherheits- und Produktkanon, eine zentralisierte Concept-Datenbasis, serverseitige Auth-Middleware für die wenigen produktiven Datenzugriffe, eine portable PGLite/Neon-Abstraktion sowie gute Plattform-/Preview-Absicherung.

Die vorrangigen Risiken sind: (1) die sichtbare Verfassung driftet an mehreren Stellen vom verbindlichen Ubuntu-/2×2-TB-/16-GB-Kanon ab; (2) ein ungenutztes, aber exportierbares WebRTC-P2P-Modul widerspricht D10; (3) die aktuelle Mandantenanlage ist nicht atomar und kann bei Parallelaufrufen verwaiste Tenant-Zeilen erzeugen; (4) die produktive Phase-1-Sicherheits- und Rollenpolitik ist nur teilweise modelliert; und (5) der dokumentierte Zielbetrieb ist erheblich umfangreicher als die implementierte Anwendung.

**Empfohlene Steuerungsentscheidung:** Keine funktionale Erweiterung vor dem weiterhin offenen Gate `G0-SRV-0` und einer anschließenden, hashgebundenen Kanon- und Sicherheitskonsolidierung. Danach ausschließlich additive, testgetriebene, kleine Gates.

```json
{
  "current_product_reality": "Phase-1 identity shell plus static concept portal",
  "normative_status": "phase-1-paused-for-g0-server-ground-zero",
  "active_infrastructure_gate": "G0-SRV-GROUND-ZERO",
  "highest_priority_findings": ["F-01", "F-02", "F-03", "F-04", "F-05"],
  "strategic_decision": "Do not expand product behavior before G0-SRV-0 evidence and canon/security reconciliation."
}
```

## 2. Core invariants / Kerninvarianten

### 2.1 Product and safety invariants

| ID | English technical invariant | Deutsche Steuerungsaussage | Authority |
|---|---|---|---|
| INV-01 | AURELIA is wellbeing/documentation software, not a medical device; diagnosis, cure, therapy, and clinical-efficacy claims are prohibited. | Jede neue sichtbare Formulierung benötigt vor Freigabe einen nachweisbaren CopyGuard-Pfad. | `AGENTS.project.md:27-33,48-54`; `src/lib/concept/decisions.ts:17-29` |
| INV-02 | Phase 1 permits authentication, synthetic tenants, and roles only; no real clients, CUDA, USB, or Art. 9 plaintext. | Phase-1-Umfang darf nicht durch Demo- oder Infrastrukturattrappen erweitert werden. | `AGENTS.project.md:108-112`; `docs/STATUS.md:56-63` |
| INV-03 | Product target is Ubuntu Server 24.04.4 LTS amd64 with minimal GNOME; two physical 2-TB NVMe drives are canonical. | Historische Debian/Bookworm- und 2×1-TB-Texte sind redaktionell zu entfernen oder klar als historische Referenz zu markieren. | `AGENTS.project.md:21-25,82-84`; server design `:22-33` |
| INV-04 | The server is the authority for time, computation, and emitter control; browser is a rendering client. | Kein Browserzustand darf eine fachliche Uhr, einen Lease oder eine Emission autorisieren. | `AGENTS.project.md:55-60`; `decisions.ts:70-80,261-273` |
| INV-05 | Every future data query and CUDA buffer must be scoped by `(tenant_id, client_id, job_id)`; client role is fail-closed. | Tenant-Isolation muss vor fachlichem Ausbau als überprüfbarer Vertrag stehen. | `AGENTS.project.md:58-60`; `decisions.ts:57-68` |
| INV-06 | Compute defaults to strict reproducibility; stochastic and quantum modes are explicit; computation passports include tenant and CopyGuard provenance. | Reproduzierbarkeit und Provenienz sind Abnahmekriterien, keine Report-Politur. | `AGENTS.project.md:56-58`; `decisions.ts:83-93` |
| INV-07 | CopyGuard must be local RAM/NVMe, fail closed, and applied to every visible sentence including drafts. | Ein künftiger CopyGuard-Bypass ist ein Stop-the-line-Befund. | `AGENTS.project.md:50-54`; `decisions.ts:170-180` |
| INV-08 | WebSocket is the intended analysis/harmonisation channel; video/WebRTC is excluded. | Exportierbare WebRTC-Artefakte müssen entfernt oder bis dahin technisch unexportierbar und unreferenzierbar sein. | `AGENTS.project.md:65,73-76`; `decisions.ts:135-144` |
| INV-09 | Emitter control requires `lease → arming → ACK`; emitter lease and GPU-job lease are independent. | Hardware-APIs bleiben bis zum expliziten Hardware-Gate deklarativ und nicht aktivierbar. | `AGENTS.project.md:61-66`; `decisions.ts:183-193` |
| INV-10 | Ground Zero requires externally evidenced backup/restore before destructive server work. | Keine Server- oder Datenexpansion darf G0-SRV-0 überspringen. | `AGENTS.project.md:82-89`; server design `:304-328,352-399` |

### 2.2 Implemented-runtime invariants

| ID | English technical invariant | Deutsche Steuerungsaussage | Evidence |
|---|---|---|---|
| R-01 | `getRouter()` is a named TanStack Start router factory and supplies `AppErrorComponent`. | Routervertrag nicht in eine alternative Startstruktur umbauen. | `src/router.tsx:1-7` |
| R-02 | Root mounts `PreviewHostBridge` and `AuthProvider`; platform PWA injection remains in Vite/Nitro middleware. | Plattformbrücke und Branding-Injektor dürfen nicht entfernt werden. | `src/routes/__root.tsx:1-42`; `vite.config.ts:145-183`; `server/middleware/grok-pwa.ts:1-111` |
| R-03 | Database resolution is `DATABASE_URL → pg Pool`, otherwise one global in-memory PGLite instance; both use non-recursive root migrations. | Jede Migration muss mit beiden Backends und dem Basename-Bookkeeping kompatibel sein. | `src/lib/db.ts:3-238`; `scripts/migrate.mjs:1-90`; `scripts/migration-plan.mjs:1-46` |
| R-04 | All existing app data server functions use `authMiddleware`, which performs request isolation then verified-user resolution. | Neue serverseitige Datenfunktionen müssen Middleware und Scope-Vertrag vor ihrer Geschäftslogik erhalten. | `src/lib/auth/middleware.ts:28-47`; `src/lib/praxis/memberships.ts:24-101` |
| R-05 | Current persisted Phase-1 domain is only `tenants` and `memberships`; no client, timer, compute, emitter, CopyGuard, audit, or passport tables exist. | Planungsbegriffe dürfen nicht als implementierte Datenmodelle ausgegeben werden. | `migrations/0002_tenants.sql:1-19`; source-wide `getSql` call map |
| R-06 | Default local auth behavior is determined by `VITE_AUTH_ENABLED`; absence means enabled, while the ignored platform app-env is expected by tests to set it false for the shipped sandbox. | Auth-Status muss vor Release aus der tatsächlich injizierten Umgebung geprüft werden, nicht nur aus Doku abgeleitet werden. | `src/lib/auth/client.ts:31-38`; `scripts/with-app-env.mjs:1-130`; `scripts/check-auth-invariant.test.mjs:93-96` |

```json
{
  "enforced_runtime_dependencies": [
    {"from":"src/routes/__root.tsx","to":"src/components/preview-host-bridge.tsx","role":"platform preview bridge"},
    {"from":"src/routes/__root.tsx","to":"src/lib/auth/provider.tsx","role":"root auth mount point"},
    {"from":"src/lib/praxis/memberships.ts","to":"src/lib/auth/middleware.ts","role":"verified request context"},
    {"from":"src/lib/praxis/memberships.ts","to":"src/lib/db.ts","role":"server-only SQL"},
    {"from":"src/lib/db.ts","to":"scripts/migration-plan.mjs","role":"shared migration ordering"},
    {"from":"vite.config.ts","to":"server/middleware/grok-pwa.ts","role":"production PWA/OG middleware"}
  ],
  "not_implemented_but_normatively_required": ["CopyGuard runtime", "Postgres RLS", "Kernel ABI", "computation passport", "timerd", "WebSocket protocol", "GPU scheduler", "emitter daemon", "audit ledger", "backup restore automation"]
}
```

## 3. Architecture map / Technische Architekturabbildung

```text
Browser
  ├─ TanStack Start route tree (24 UI routes + /api/auth/$)
  │   ├─ ConceptShell + static concept datasets
  │   ├─ /login → Better Auth React client
  │   └─ /praxis → authenticated tenant server functions
  ├─ PreviewHostBridge (allowlisted postMessage parent)
  └─ PWA install/manifest/head tags

TanStack Start server
  ├─ Better Auth route handler: /api/auth/*
  ├─ authMiddleware → Fetch-Metadata isolation → verified user
  ├─ membership server functions
  └─ SQL abstraction
       ├─ pg/Neon when DATABASE_URL exists
       └─ PGLite fallback otherwise
            └─ root migrations/*.sql

Deployment/tooling
  ├─ scripts/with-app-env.mjs
  ├─ Vite plugins: PGLite bootstrap, auth popup, app-env, PWA, Start, Nitro/Vercel
  └─ Nitro PWA middleware

Future-only normative architecture
  └─ M G1: reverse proxy, PostgreSQL, CopyGuard, timerd, gpud, emitterd, optional compute
```

### 3.1 Route and boundary map

| Boundary | English API/contract | Deutsche Bewertung |
|---|---|---|
| `GET/POST /api/auth/$` | Direct Better Auth adapter handler. Session can derive from same-origin cookie or preview bearer token. | Einzige echte HTTP-API im Produktkern; geschützt durch Better Auth, aber nicht durch eine AURELIA-Rollenpolitik. |
| `listMemberships()` | Authenticated GET server function. Returns only rows joined through `memberships.user_id = context.userId`. | Korrekte lesende User-Scoping-Basis. |
| `ensurePrimaryTenant()` | Authenticated POST server function. Returns existing memberships or creates synthetic tenant plus `tenant_admin` membership. | Produktiv, aber nicht atomar; Parallelaufruf muss vor weiterer Nutzung geschlossen werden. |
| `addSecondTenant()` | Authenticated POST server function. Caps memberships at two, then creates a synthetic tenant plus membership. | Demonstrations-/Isolationstestfunktion, keine generische Mandantenverwaltung. |
| `PreviewHostBridge` | Strict origin/source/channel/version/path checks for preview-chrome navigation. | Gut eingegrenzt; als Plattformabhängigkeit behandeln. |
| `P2PRoom` | Exported browser full-mesh WebRTC client requiring an unimplemented `/api/rtc` signalling relay. | Tote, jedoch exportierbare WebRTC-Oberfläche; verletzt Produktkanon D10. |
| `app-data/client.server.ts` | Generic external connector gateway with a POST, header-token, host-resolution, same-site check, and short-lived failure memo. | Exportierbare Plattformbibliothek ohne aktuelle Fachnutzung; nicht in Phase-1-Produktmodell integrieren. |

```json
{
  "routes": {
    "ui": ["/","/architektur","/compute","/daten","/entscheidungen","/freigabe","/gestaltung","/hardware","/identitaet","/kozyrev","/leitplanken","/live","/login","/lovable","/module","/offen","/praxis","/repos","/roadmap","/sicherheit","/timer","/wellbeing","/zwischenablage"],
    "server": ["/api/auth/$"],
    "declared_but_not_implemented": ["/api/rtc"]
  },
  "data_schema": {
    "migrations_root": ["migrations/0001_auth.sql", "migrations/0002_tenants.sql"],
    "optional_source_copy": ["migrations/auth/0001_auth.sql"],
    "tables": {
      "user": ["id","name","email","emailVerified","image","createdAt","updatedAt"],
      "session": ["id","expiresAt","token","createdAt","updatedAt","ipAddress","userAgent","userId"],
      "account": ["id","accountId","providerId","userId","accessToken","refreshToken","idToken","accessTokenExpiresAt","refreshTokenExpiresAt","scope","password","createdAt","updatedAt"],
      "verification": ["id","identifier","value","expiresAt","createdAt","updatedAt"],
      "tenants": ["id","name","data_class","created_at"],
      "memberships": ["id","user_id","tenant_id","role","created_at"]
    },
    "constraints": ["tenants.id primary key", "memberships.tenant_id foreign key", "unique(memberships.user_id,memberships.tenant_id)"]
  }
}
```

## 4. Exportable dependencies / Exportierbare Abhängigkeiten

### 4.1 Internal modules that form reusable contracts

| Module | English exported contract | Deutsche Einordnung |
|---|---|---|
| `src/lib/db.ts` | `DbSource`, `Sql`, `dbSource`, `getSql`, `getPglite`, `ensureDbReady` | Kritischer Infrastrukturvertrag; nur serverseitig verwenden. |
| `src/lib/auth/middleware.ts` | `authMiddleware` providing `context.userId` | Pflichtbaustein für alle per-user Serverfunktionen. |
| `src/lib/auth/verify.server.ts` | verified session resolution, `UnauthorizedError`, `requireUserId`, `DEV_USER_ID` | Fail-closed bei echter DB und ausgeschalteter Auth; nur bewusstes Local-Preview-Fallback. |
| `src/lib/praxis/memberships.ts` | row type, role label, three server functions | Einziger implementierter AURELIA-Domain-Service. |
| `src/lib/concept/*.ts` | typed canonical concept datasets (`DECISIONS`, `C_GESETZT`, `X_KATALOG`, `KOZYREV_*`, etc.) | Der sichtbare Produktkanon ist derzeit mehrfach verteilt, nicht durch eine formale Aggregatprüfung geschützt. |
| `src/lib/app-data/*` | connector types, client-safe result helpers, server-only `callTool` | Plattformadapter, aktuell ohne AURELIA-Produkt-Consumer. |
| `src/lib/multiplayer/*` | WebRTC P2P types and `P2PRoom` | Nicht in den Produktkanon passend; als Entfernen/Quarantäne-Gate behandeln. |
| `scripts/migration-plan.mjs` | migration basename, filter, deterministic ordering | Shared production/preview migration contract. |
| `scripts/browser-*` | loopback-only browser capture and baseline-verdict utilities | Gute QA-Basis; im strikten Review bewusst nicht ausgeführt. |

### 4.2 External package dependency groups

```json
{
  "runtime_dependencies": {
    "framework": ["@tanstack/react-start", "@tanstack/react-router", "react", "react-dom", "vite", "nitro"],
    "auth_security": ["better-auth", "jose", "pg", "kysely", "@electric-sql/pglite", "zod"],
    "ui": ["tailwindcss", "@tailwindcss/vite", "@radix-ui/react-dialog", "lucide-react", "@fontsource-variable/fraunces", "@fontsource-variable/source-sans-3"],
    "available_but_not_core_product_used": ["zustand", "recharts", "@tanstack/react-query", "@tanstack/react-table", "react-hook-form", "date-fns", "cmdk"],
    "qa_tooling": ["playwright", "eslint", "prettier", "typescript"]
  },
  "platform_dependencies": ["Grok preview host bridge", "Grok PWA/OG injector", "Grok auth broker/gate identity", "Vercel Nitro preset"],
  "future_infrastructure_not_node_dependencies": ["Ubuntu 24.04.4", "PostgreSQL 16", "Caddy", "LUKS2", "mdraid1", "systemd", "CopyGuard local model", "aurelia-timerd", "aurelia-gpud", "aurelia-emitterd"]
}
```

## 5. Finding register / Befundregister

Severity is strategic risk, not a claim of exploitability. All findings are static-source inferences because no code was executed.

| ID | Severity | English technical finding | Deutsche Maßnahme | Evidence |
|---|---|---|---|---|
| F-01 | hoch | Canonical target is Ubuntu 24.04.4/2×2 TB/16-GB job pool, yet active portal code still states Debian/Bookworm, 2×1 TB, 3/3/12/2, or an old phase state. | Erst einen maschinenprüfbaren Kanon-Index etablieren, dann jede sichtbare Abweichung redaktionell und testbar konsolidieren. | `src/routes/index.tsx:17,34,50`; `hardware.tsx:29-31`; `roadmap.tsx:22,62`; `module.tsx:31,105`; `AGENTS.project.md:21-25,82-84` |
| F-02 | hoch | `src/lib/multiplayer/p2p.ts` exports a complete browser WebRTC mesh client and default public STUN servers; no product consumer or signalling endpoint exists. This conflicts with D10's no-WebRTC/no-video invariant even though it is dead code. | WebRTC-Modul in einem isolierten, freigegebenen Kanon-Gate entfernen oder technisch vollständig aus dem Produkt-Exportpfad sperren; keine `/api/rtc`-Implementierung ergänzen. | `src/lib/multiplayer/p2p.ts:1-95,98-570`; `src/lib/multiplayer/index.ts:1-10`; no external usage found; `decisions.ts:135-144` |
| F-03 | hoch | `ensurePrimaryTenant` and `addSecondTenant` use read-then-insert sequences with independent inserts and no transaction/tenant ownership uniqueness. Concurrent requests can create orphan tenants and can exceed intended semantics. | Vor jeder Erweiterung der Praxisverwaltung einen atomaren Tenant-Provisioning-Vertrag mit DB-Constraints, Transaktion und Paralleltest definieren. | `src/lib/praxis/memberships.ts:37-67,69-101`; `migrations/0002_tenants.sql:1-19` |
| F-04 | hoch | The implemented DB schema has memberships but no check constraint/foreign key to users, no role enum/check, no RLS, no tenant ownership metadata, and no authorization policy beyond current-user membership filtering. It does not yet satisfy normative role/isolation claims. | Phase 1 nicht als vollständige RBAC-/Mandantenisolation bezeichnen; additive RLS/RBAC-Designphase nach G0 starten. | `migrations/0002_tenants.sql:1-19`; `src/routes/identitaet.tsx:24-100`; `AGENTS.project.md:58-60` |
| F-05 | hoch | `src/lib/auth/preview.ts` contains an embedded preview credential material value in tracked source, while repository policy forbids secrets. Its low-privilege/platform intent does not remove rotation and supply-chain exposure risk. | Geheimnis in einem separaten Security-Gate rotieren und aus getracktem Quelltext in plattformseitige Injektion oder eine nicht-committete Runtime-Autorität verlagern; keine Wertwiedergabe in Reviews oder Commits. | `src/lib/auth/preview.ts:1-32`; `SECURITY.md:1-14`; `.gitignore:13-22` |
| F-06 | mittel | Documentation and source disagree on whether auth is “on”, the shipped sandbox is auth-off, and missing `VITE_AUTH_ENABLED` means auth-on. The ignored `.grok/app-env.json` was unavailable to this review, so the actual local runtime flag was intentionally not inferred. | Einen expliziten Environment-Statusvertrag und Release-Check definieren: dokumentierter Default, sandbox actual, deployed actual, fail-closed behavior. | `AGENTS.project.md:16`; `docs/STATUS.md:9`; `src/lib/auth/client.ts:31-38`; `scripts/with-app-env.mjs:10-17`; test `:93-96` |
| F-07 | mittel | Product concept data is spread across Markdown, `AGENTS.project.md`, many `src/lib/concept/*.ts` arrays, and literal route prose. There is no current repository-wide canonical consistency validator in the visible scripts. | Kanon erst als versioniertes, maschinenlesbares Aggregat definieren und dann aus ihm Portal-/Dokumentationsprüfungen ableiten. | Concept files; 47 stale-term matches; `docs/project-control/README.md:58-64` |
| F-08 | mittel | The app-data connector client is a generic platform module with sensitive token transport and external host resolution, but no current product consumer or domain policy. It enlarges the deployable attack and maintenance surface. | Bis zu einem expliziten Connector-Produktgate keine AURELIA-Fachfunktion daran koppeln; Besitz, auth model, audit model und data classification vorher definieren. | `src/lib/app-data/client.server.ts:1-369`; no consumer found in reviewed routes |
| F-09 | mittel | `migrations/0001_auth.sql` exists at the migration root, therefore auth schema is applied by both production migrator and PGLite even though comments/tests describe a staged optional-copy model. The implementation may be intentional Phase-1 auth-on, but documentation says otherwise in several places. | Auth-Migrationsstrategie als einzelne Entscheidung klären: permanent Phase-1 required versus copied-on-enable; Dokumentation, tests and deploy behavior must match. | `migrations/0001_auth.sql:1-67`; `migrations/auth/0001_auth.sql:1-67`; `scripts/migration-plan.test.mjs:18-74` |
| F-10 | mittel | The app uses PGLite in-memory fallback. It is suitable for preview but resets on process restart and cannot prove Neon/Postgres operational semantics, RLS, persistence, or concurrency. | PGLite ausschließlich als Preview-Fallback kennzeichnen; reale DB-Gates erst auf dem freigegebenen Server mit isolierten Testdaten durchführen. | `src/lib/db.ts:108-168,197-238` |
| F-11 | mittel | Current test inventory focuses platform glue, auth gate identity, migration ordering, and browser-smoke utilities. There are no reviewed tests for membership provisioning races, role authorization, RLS, concept consistency, CopyGuard, or future product invariants. | Teststrategie nach Schichten aufbauen: erst Kanon und Tenant-Provisioning, dann Authorization/RLS, erst später compute/timer/emitter contracts. | `package.json:17-19`; reviewed test files; absence of domain test files |
| F-12 | niedrig | Portal localStorage decision votes are client-local and are not an approval workflow, audit ledger, or authoritative decision state. | Nutzeroberfläche als persönliche Notizfunktion labeln; formale Entscheidungen nur aus kontrollierten Dokument-/Gateartefakten ableiten. | `src/routes/entscheidungen.tsx:30-64` |
| F-13 | niedrig | Static architecture pages contain several aspirational concrete services (FastAPI, mTLS, Redis, MinIO, Timescale, gRPC/NATS, ML/quantum tools) that do not exist in this repository. | Implementiert, geplant und gesperrt in jeder Architekturansicht klar markieren; keine Infrastruktur als vorhanden ausgeben. | `src/routes/architektur.tsx:49-81`; `compute.tsx:28-105`; `daten.tsx:18-93` |
| F-14 | niedrig | The repository’s ignored confidential-analysis roots cannot safely be covered by a general LLM architecture review. | Diese Quellen nur lokal, mit einem geheimnisbereinigten Manifest und gezielter Betreiberfreigabe überprüfen. | `.gitignore:24-28`; `docs/project-control/README.md:47-56` |

```json
{
  "findings": [
    {"id":"F-01","severity":"high","category":"canon-drift","files":["src/routes/index.tsx","src/routes/hardware.tsx","src/routes/roadmap.tsx","src/routes/module.tsx"]},
    {"id":"F-02","severity":"high","category":"forbidden-exported-webRTC","files":["src/lib/multiplayer/p2p.ts","src/lib/multiplayer/index.ts"]},
    {"id":"F-03","severity":"high","category":"tenant-provisioning-atomicity","files":["src/lib/praxis/memberships.ts","migrations/0002_tenants.sql"]},
    {"id":"F-04","severity":"high","category":"incomplete-tenant-authorization","files":["migrations/0002_tenants.sql","src/routes/identitaet.tsx"]},
    {"id":"F-05","severity":"high","category":"tracked-preview-credential-material","files":["src/lib/auth/preview.ts"]},
    {"id":"F-06","severity":"medium","category":"auth-environment-drift","files":["src/lib/auth/client.ts","scripts/with-app-env.mjs","docs/STATUS.md"]},
    {"id":"F-07","severity":"medium","category":"distributed-concept-authority","files":["AGENTS.project.md","docs/","src/lib/concept/","src/routes/"]},
    {"id":"F-08","severity":"medium","category":"unused-connector-surface","files":["src/lib/app-data/client.server.ts"]},
    {"id":"F-09","severity":"medium","category":"auth-migration-policy-drift","files":["migrations/0001_auth.sql","migrations/auth/0001_auth.sql","scripts/migration-plan.test.mjs"]},
    {"id":"F-10","severity":"medium","category":"preview-production-parity-limit","files":["src/lib/db.ts"]},
    {"id":"F-11","severity":"medium","category":"domain-test-gap","files":["package.json","src/lib/praxis/memberships.ts"]},
    {"id":"F-12","severity":"low","category":"non-authoritative-local-votes","files":["src/routes/entscheidungen.tsx"]},
    {"id":"F-13","severity":"low","category":"aspirational-runtime-documentation","files":["src/routes/architektur.tsx","src/routes/compute.tsx","src/routes/daten.tsx"]},
    {"id":"F-14","severity":"low","category":"confidential-scope-boundary","files":[".gitignore","docs/project-control/README.md"]}
  ]
}
```

## 6. Strategic gate plan / Strategischer Gate-Plan

No gate is approved for execution by this document. Gates preserve the project’s active `G0-SRV-GROUND-ZERO` dependency and must be separately approved.

### Gate 0 — External backup and restore proof

**Ziel:** `G0-SRV-0` mit extern belegtem Restore schließen, ohne Server- oder Produktcodeänderung.

**Technical contract (English):** Follow `docs/superpowers/plans/2026-08-25-aurelia-ground-zero-preflight.md`. Produce external, privacy-preserving evidence of two copies, encrypted offline/EU copy, repository restore, relevant DB-dump restore or documented non-applicability, representative byte-identical file restore, and a sanitized gate statement. No destructive operation is authorized by this gate alone.

**Acceptance:** Only external evidence can move the gate; do not manufacture server evidence from repository docs.

### Gate 1 — Freeze and canon authority reconciliation

**Ziel:** Den verbindlichen Produktkanon in einem maschinenlesbaren, versionierten Aggregat fixieren und sichtbare Drift vollständig erfassen.

**Technical contract (English):** Establish one typed canonical data model containing target OS, storage, phase status, allowed/forbidden capability IDs, VRAM budget, active infrastructure gate, and deferred items. Add a static validator that enumerates all active concept routes and canonical docs, reports every forbidden stale token with file/line, and has no dependency on browser or server startup.

**Maps to:** F-01, F-06, F-07, F-09, F-13.

**Acceptance:** Canonical-document data, concept exports, and active presentation texts have zero unresolved contradictions; historical references are explicitly annotated rather than silently rewritten.

### Gate 2 — Remove or quarantine forbidden WebRTC surface

**Ziel:** D10 technisch schließen, nicht nur textlich behaupten.

**Technical contract (English):** Delete or quarantine `src/lib/multiplayer/{p2p,index}.ts` from the application build/export graph. Add a static negative test over tracked production source that rejects `RTCPeerConnection`, `RTCDataChannel`, STUN/TURN URLs, `/api/rtc`, and WebRTC-related exports, with narrowly documented exemptions only if independently approved.

**Maps to:** F-02.

**Acceptance:** No importable production WebRTC API, no signalling endpoint, no external STUN dependency, and negative test passes.

### Gate 3 — Preview credential containment

**Ziel:** Getracktes Preview-Credential-Material aus dem Quellcode entfernen und die Rotation nachweisbar vorbereiten.

**Technical contract (English):** Replace embedded credential material with a platform-controlled, runtime-injected authority. Define missing-value behavior, preview host allowlist, deployment behavior, rotation owner, revocation procedure, and tests that prove no source contains the credential class. Do not expose the old value in issues, logs, reports, fixtures, or commit messages.

**Maps to:** F-05.

**Acceptance:** No credential material in tracked source; preview auth behavior fails safely when the platform authority is unavailable; rotation is independently confirmed by the credential owner.

### Gate 4 — Atomic tenant provisioning contract

**Ziel:** Aus der Demo-Mandantenanlage eine atomare, idempotente Phase-1-Provisionierung machen.

**Technical contract (English):** Define one user-to-primary-tenant ownership invariant. Enforce it with schema constraints and one transaction that creates/gets the primary tenant and membership together. Use database-native upsert/locking semantics. Return a stable typed result. Prevent orphan tenants and provide a concurrency test with two simultaneous requests.

**Maps to:** F-03, F-11.

**Acceptance:** Parallel provisioning produces exactly one primary tenant/membership result per policy; no orphan tenant; retry behavior is deterministic in PGLite and PostgreSQL test matrices.

### Gate 5 — Tenant authorization foundation

**Ziel:** Rollen, Mitgliedschaft und künftige Datenzugriffe formal trennen.

**Technical contract (English):** Introduce typed role vocabulary, DB validation, member lifecycle state, and policy functions. Before real-client data exists, model the tenancy policy on synthetic records. Design PostgreSQL RLS separately from application-layer checks; every future table must include tenant identity and an explicit access path. Do not claim CUDA isolation proof from database-only tests.

**Maps to:** F-04, F-10, F-11.

**Acceptance:** Role-policy matrix exists; negative cross-tenant tests are green; client is fail-closed; RLS migration design is approved before implementation.

### Gate 6 — Auth environment truth table

**Ziel:** Auth-Verhalten je Umgebung ohne Doku-Interpretation beweisen.

**Technical contract (English):** Specify sandbox, local, deployment, and DB-present/auth-disabled states. Validate `VITE_AUTH_ENABLED`, `DATABASE_URL`, gate identity, Better Auth provider availability, and redirect/cookie/bearer behavior. Preserve the existing fail-closed production behavior when auth is disabled with a real DB.

**Maps to:** F-06, F-09.

**Acceptance:** One matrix with exact input env and expected behavior; automated contract tests; release smoke validates resolved env rather than assumed defaults.

### Gate 7 — Concept publication pipeline

**Ziel:** Sichtbaren Kanon, Markdown und UI aus einer nachvollziehbaren Autorität ableiten.

**Technical contract (English):** Keep narrative prose possible, but establish a canonical structured source for IDs, lock states, statuses, and technical constants. Derive validation artifacts rather than necessarily generating all prose. Cross-link every D/C/X/K/U/WV/H identifier to its authority and reject missing/duplicate/contradictory entries.

**Maps to:** F-01, F-07, F-12, F-13.

**Acceptance:** ID inventory is bijective where intended; stale surface report is zero; local vote UI is explicitly non-authoritative or removed from decision semantics.

### Gate 8 — CopyGuard boundary, before any domain expansion

**Ziel:** Den wichtigsten Safety-Invariant als reale, testbare Schnittstelle vor Analyse-, Draft- oder Reportfunktionen implementieren.

**Technical contract (English):** Define `CopyGuardInput`, `CopyGuardDecision`, `reason_code`, immutable digest scope, fail-closed failure behavior, and permitted rendering/persistence transitions. Start with synthetic corpus fixtures. No model download, CUDA use, client data, or cloud inference belongs in this first gate.

**Maps to:** INV-01, INV-07, F-11.

**Acceptance:** Negative prohibited-claim corpus blocks visibility/persistence; allow/rewrite/block contracts are deterministic; no fallback silently allows unreviewed text.

### Gate 9 — Domain-schema preflight for future artifacts

**Ziel:** AnalysisDraft, passport, timer, kernel and audit requirements als additive Datenverträge planen, nicht vorzeitig implementieren.

**Technical contract (English):** Define versioned schemas for `AnalysisDraft`, `ComputationPassport`, `HarmonizationLane`, `RunEvent`, and kernel manifests. All carry tenant/client/job identity where applicable. Separate authoritative state, append-only evidence, display projection, and future worker transport. Keep tables/migrations out until Gate 0–8 pass and a separate implementation approval exists.

**Maps to:** INV-04–INV-09, F-04, F-10, F-13.

**Acceptance:** Complete lifecycle/state transition matrix; no ambiguous “measured” fallback; no future field lacks ownership, retention, or audit semantics.

### Gate 10 — Server baseline and production parity

**Ziel:** Nach G0 nur die freigegebene Ubuntu-Basis und echte PostgreSQL-Produktionsparität prüfen.

**Technical contract (English):** Implement no CUDA/USB/business runtime here. Verify OS, RAID/LUKS, network separation, identities, NVIDIA baseline without CUDA toolkit, PostgreSQL internal-only with checksums, logging, and restore. Re-run application migration and auth contracts against the actual target DB using synthetic data only.

**Maps to:** INV-02, INV-03, INV-10, F-10.

**Acceptance:** `G0-SRV-GROUND-ZERO` completed according to the existing 13-gate sequence; no product feature activation is implied.

### Gate 11 — Timer/compute/emitter contracts, strictly after foundations

**Ziel:** Zuerst deterministische Verträge und negative Sicherheitsproben, erst danach Daemons oder Hardware.

**Technical contract (English):** Build CPU reference contracts, timer state-machine transitions, checkpoint/recovery semantics, per-scope resource admission, GPU/worker isolation interfaces, and emitter lease separation. Default all hardware/capability flags to false. Do not create WebRTC, browser hardware control, fake telemetry, or medical claims.

**Maps to:** INV-04–INV-09.

**Acceptance:** Synthetic deterministic tests first; explicit fail-closed flags; no physical device call before a dedicated hardware gate.

### Gate 12 — Final release evidence

**Ziel:** Erst nach jedem vorigen Gate einen reproduzierbaren Freigabepunkt herstellen.

**Technical contract (English):** Freeze exact source hashes, run test/typecheck/lint/build/browser verification as approved, perform two independent current-revision reviews, resolve every P0–P3 finding, regenerate manifests after any patch, and create the required verified external post-state shadow copy before GO.

**Acceptance:** The user’s dual-review and external-shadow-copy requirements are met on the exact final hash; no stale review is treated as approval.

```json
{
  "ordered_gates": [
    {"id":"G0","name":"external-backup-restore-proof","depends_on":[],"findings":[],"mutation":"external-operator-evidence-only"},
    {"id":"G1","name":"freeze-and-canon-authority-reconciliation","depends_on":["G0"],"findings":["F-01","F-06","F-07","F-09","F-13"]},
    {"id":"G2","name":"remove-or-quarantine-forbidden-webrtc","depends_on":["G1"],"findings":["F-02"]},
    {"id":"G3","name":"preview-credential-containment","depends_on":["G1"],"findings":["F-05"]},
    {"id":"G4","name":"atomic-tenant-provisioning","depends_on":["G1"],"findings":["F-03","F-11"]},
    {"id":"G5","name":"tenant-authorization-foundation","depends_on":["G4"],"findings":["F-04","F-10","F-11"]},
    {"id":"G6","name":"auth-environment-truth-table","depends_on":["G1","G3"],"findings":["F-06","F-09"]},
    {"id":"G7","name":"concept-publication-pipeline","depends_on":["G1"],"findings":["F-01","F-07","F-12","F-13"]},
    {"id":"G8","name":"copyguard-boundary","depends_on":["G4","G5","G6","G7"],"findings":["F-11"]},
    {"id":"G9","name":"future-domain-schema-preflight","depends_on":["G8"],"findings":["F-04","F-10","F-13"]},
    {"id":"G10","name":"server-baseline-production-parity","depends_on":["G0","G6"],"findings":["F-10"]},
    {"id":"G11","name":"timer-compute-emitter-contracts","depends_on":["G9","G10"],"findings":[]},
    {"id":"G12","name":"final-release-evidence","depends_on":["G2","G3","G5","G6","G7","G8","G9","G10","G11"],"findings":["F-01","F-02","F-03","F-04","F-05","F-06","F-07","F-08","F-09","F-10","F-11","F-12","F-13","F-14"]}
  ]
}
```

## 7. Explicit non-go boundaries / Explizite Nicht-Ziele

- Kein Serverzugriff, keine Neuinstallation, keine Partitionierung und keine Wiederherstellung ohne externen `G0-SRV-0`-Nachweis und neue Betreiberfreigabe.
- Kein CUDA, USB, Emitter, echte Klientendaten, Art.-9-Klartext, WebRTC/Video oder Cloud-LLM über Akten.
- Keine Ergänzung eines `/api/rtc`-Relays oder Aktivierung des vorhandenen P2P-Moduls.
- Keine Behauptung, dass FastAPI, PostgreSQL-RLS, Timescale, Redis, MinIO, NATS, Timerd, gpud, emitterd, Kernel-ABI oder CopyGuard bereits implementiert seien.
- Keine Veröffentlichung, kein Push, kein Commit und keine Historienoperation als Folge dieses Dokuments.

```json
{
  "hard_no_go": [
    "destructive_server_actions_before_G0-SRV-0",
    "real_client_or_article_9_data",
    "CUDA_or_USB_activation",
    "WebRTC_or_video",
    "browser_hardware_control",
    "cloud_LLM_on_case_text",
    "fake_measurement_or_telemetry",
    "unapproved_commit_push_merge_reset"
  ]
}
```

## 8. Review limits / Prüfgrenzen

- This was a static review. No test, build, typecheck, import, dev server, migration, database connection, browser, or network endpoint was executed.
- Therefore buildability, runtime behavior, browser accessibility, actual auth flag resolution, external service reachability, and database concurrency remain unverified.
- Confidential/ignored analysis sources were intentionally excluded. Their existence is recorded as a security boundary, not treated as absent.
- The project entered the review with unrelated untracked documentation directories. They are not attributed to this review.

## 9. Approval checkpoint / Freigabepunkt

**Status: NO-GO for implementation.**

Der nächste zulässige Schritt ist ausschließlich Ihre Freigabe eines abgegrenzten ersten Gates. Empfohlen ist `G0` falls der externe Restore-Nachweis noch offen ist; andernfalls `G1` als reine Kanon- und Konsolidierungsarbeit. No code change, commit, or external operation is authorized by this plan.
