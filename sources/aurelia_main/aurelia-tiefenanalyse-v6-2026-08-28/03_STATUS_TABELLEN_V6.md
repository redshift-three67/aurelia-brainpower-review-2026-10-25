# AURELIA Tiefenanalyse V6 — Status-Tabellen

Legende: ✅ umgesetzt/abgenommen · ◐ teils/in Arbeit · ⬜ offen · 🔒 gesperrt ·
❌ gestrichen · ⏸ pausiert

## T1 — Produktphasen: umgesetzt vs. offen

| Phase | Name | Umgesetzt | Offen | Status |
|---|---|---|---|---|
| 0 | Konzept | Verfassung, C01–C12, X-Katalog, D-Register, Portal | — | ✅ abgenommen 23./24.08. |
| G0-SRV | Server Ground Zero | Design (426 Z.), Preflight-Plan (394 Z.), Gate-Matrix, ISO/SHA fixiert, read-only Hardwareinventur | `G0-SRV-0`-Nachweis, alle Gates 1–12, jede Serveränderung | ⏸ wartet auf `G0-SRV-0` |
| 1 | Gehäuse | Auth-Schale (an), Mandanten/Memberships, Portal (23 Routen), Migrationen 0001/0002, ~175 Testfälle | Isolationstest zwei Mandanten, RLS/CHECK, Passkeys (WV03), Kanonbereinigung im Code | ◐ ⏸ pausiert bis G0-SRV |
| 2 | Praxisorganisation | Konzept (Dokumente) | Klienten, Gruppen, Dienste, Einwilligungen, Zwischenablage; WV01 vor Art. 9 | ⬜ |
| 3 | Kernel-ABI + Raten | Konzept | Registry, gewrappte Prototypen | ⬜ |
| 4 | Analyse strikt | Konzept | CPU-Referenz, CUDA-Scheduler, Passport | ⬜ |
| 5 | Harmonisierung | Konzept | Timerd, parallele Kanäle | ⬜ |
| 6 | Archiv/Trend/Report | Konzept | Continuous Aggregates, PDF; WV06 Codecs | ⬜ |
| 7 | GPU-Härtung | Konzept | VRAM-Allocator, Attestation | ⬜ |
| 8 | Quantum opt-in | Konzept | cuQuantum hinter ABI | ⬜ |
| 9 | WebRTC + Medien | — | — | ❌ gestrichen (D10, O08) |
| 10 | Betrieb | Konzept | Abos; WV02/WV03/WV05 | ⬜ |

**Kein Prozentpunkt der Phasen ≥ 2 ist durch Umsetzung gedeckt** — gewollt und
verfassungskonform.

## T2 — G0-SRV-Gates im Detail

| Gate | Stop-Kriterium (Kurzform) | Status | Vorbereitung | Ausführung |
|---|---|---|---|---|
| G0-SRV-0 | kein nachgewiesener Restore | 🟡 wartet | ✅ Kriterien+Skriptebene im Plan | ⬜ 0 % |
| G0-SRV-1 | kein unabhängiger Recoveryzugang | 🟡 bestätigt, ungetestet | ◐ | ⬜ |
| G0-SRV-2 | unklare Geräte/defekter RAID-RAM-Status | 🟡 ~40 % | ◐ read-only Teilinventur (2× SN850X, RAID1 gesund, Secure Boot off, **ECC offen**) | ⬜ |
| G0-SRV-3 | Geräte-ID/Layout nicht zweifach bestätigt | 🔒 | ◐ LV-Matrix definiert | ⬜ |
| G0-SRV-4 | ein NVMe-/Recoverypfad nicht bootfähig | 🔒 | ◐ | ⬜ |
| G0-SRV-5 | Root-/Passwort-SSH, NOPASSWD, öffentliche Ports | 🔒 | ◐ Rollenmodell definiert | ⬜ |
| G0-SRV-6 | Codex erreicht Produktivdaten/sudo | 🔒 | ◐ | ⬜ |
| G0-SRV-7 | NVML-/Modulfehler, Desktop belegt RTX | 🔒 | ◐ Kriterienliste | ⬜ |
| G0-SRV-8 | AppArmor/Audit/Zeit nicht nachgewiesen | 🔒 | ◐ | ⬜ |
| G0-SRV-9 | unsicheres Netz, falsche Rechte, keine Checksums | 🔒 | ◐ | ⬜ |
| G0-SRV-10 | RPO/RTO nicht praktisch geprüft | 🔒 | ◐ P1-Ziele definiert (DB ≤15 min, Objekte ≤60 min, RTO ≤8 h) | ⬜ |
| G0-SRV-11 | Altservices/Altsecrets aktiviert | 🔒 | ◐ V3-Befunde als Abnahmetests übernommen (12-Punkte-Tabelle) | ⬜ |
| G0-SRV-12 | offene High/Critical, fehlende Soaktests | 🔒 | ◐ 18 Basiskriterien | ⬜ |

**Bilanz: 0/13 bestanden · 0/6 technische Abnahmen der Voraussetzungen ·
`server_changes_started: false` · `destructive_actions_allowed: false`**

## T3 — Gate-Voraussetzungen (Betreiberangabe vs. Abnahme)

| Voraussetzung | Betreiber | Technische Abnahme |
|---|---|---|
| IPMI/BMC-Webzugang | ✅ bestätigt | ⬜ |
| Remote-KVM | ✅ bestätigt | ⬜ |
| Virtual Media | ✅ bestätigt | ⬜ |
| Anbieter-USV | ✅ bestätigt | ⬜ Kapazitäts-/Shutdownnachweis |
| separates Backupsystem | ✅ bestätigt | ⬜ Backup-/Restore-Nachweis |
| Anbieter-DDoS-Schutz | ✅ bestätigt | ⬜ Leistungsumfang; Hostfirewall bleibt Pflicht |

## T4 — K1 Kanonkonsolidierung (14 Tasks)

| Task | Inhalt | Zustand | Abnahme |
|---|---|---|---|
| 1 | Steuerung + V1/V2-Tip-Sanitisierung | ✅ (`12f6c55`, `09eeddf`, `273e8c5`) | Spec+Qualität PASS |
| 2 | Governance-Grenze `GATE-GOV-0` | ✅ (`96f06d2`, `683c332`) | Spec+Qualität PASS |
| 3 | Fail-closed Push-Graph-Scanner | ◐ ~80 % — Korrekturen P1-01/P1-02/Q-01 implementiert (RED/GREEN), 13 Commits unpushed | ⬜ **erneutes Spec-Review ausstehend**, Qualität blockiert |
| 4 | Maschinenlesbare K1-Matrix + Kanonvalidator | 🔒 blockiert bis Task-3-PASS | ⬜ |
| 5 | Aktive Dokumente/Konzeptdaten auf K1 | ⬜ | ⬜ |
| 6 | Portal + zentrale Schale auf K1 | ⬜ | ⬜ |
| 7 | Plattformübergreifender Test-Runner (Windows-Glob-Fix) | ⬜ | ⬜ |
| 8 | Auth-on-, Migrations-, PWA-Fixture-, Windows-Testverträge | ⬜ | ⬜ |
| 9 | Vite-CLI plattformübergreifend | ⬜ | ⬜ |
| 10 | Selbsthostende Auth-Invariantenprüfung | ⬜ | ⬜ |
| 11 | Browser-Smoke worktree-portabel | ⬜ | ⬜ |
| 12 | Gate für verwaltete Plattformassets | ⬜ `external_blocker` | ⬜ |
| 13 | Verhaltensneutrale Lintbereinigung | ⬜ | ⬜ |
| 14 | Lokale Integration, Browserabnahme, `K1-VERIFICATION.md` | ⬜ | ⬜ |

**Bilanz: 2/14 abgenommen · 1 in Arbeit · 11 blockiert · 13 Commits unpushed**

## T5 — G0-Governance-Programm (historisch, nichtnormativ)

| Element | Zustand |
|---|---|
| Design-Spec (3.968 Z., `a6a8e7d`) | ✅ committet, **eingefroren**; `GATE-G0` bleibt **rot** ohne `REV-G0-DESIGN-APPROVAL` |
| `GATE-GOV-0-SUPPLEMENT` | ✅ nichtnormative Grenzziehung (K1) |
| 14 Planentwürfe + Status-HTML (17.091 Z.) | ⬜ **nur ungetrackt** im Worktree; nicht importiert, nicht Evidenz |
| Trust-Pins / signierte Approvals | ⬜ existieren nicht |
| Fach-/Custodian-Rollen | ⬜ unbesetzt (fail-closed rot) |

## T6 — Linux-Workstation-Migration (Design 27.08., approved)

| Schritt | Zustand |
|---|---|
| Verifizierte Ausgangsinventur (13 ahead, 2 Dirty-Dateien mit Hash, 15 untracked, 52 ignoriert, fsck sauber) | ✅ dokumentiert |
| Layer A: Fast-Forward-Push konsolidierung (8 Bedingungen) | ⬜ ausstehend (13 Commits noch lokal) |
| Layer B: verschlüsselte Recovery-Kapsel (Bundle + Patch + TAR + SHA256SUMS) | ⬜ |
| Layer C: verschlüsseltes Cold-Backup (2 Ziele, ≥1 offline; `.codex`, `.ssh`, 52 Dateien) | ⬜ |
| Restaurationsnachweis (13 Schritte, von externem Medium) | ⬜ |
| Ubuntu-24.04.4-Desktop-Wiederherstellung (Node 22.22.0/npm 11.18.0, LF, Exec-Bits) | ⬜ |
| Lösch-Gate Windows-Disk | 🔒 nur Betreiber |

## T7 — Codebereiche

| Bereich | Umsetzungsgrad | Kernbefund |
|---|---|---|
| Routing/Portal (23 Routen) | ✅ produktionsreif als Konzeptportal | keine Loader/Auth-Guards; Textdrift 5 Stellen |
| Auth (`lib/auth`) | ✅ funktionsfähig implementiert | Passkeys fehlen (WV03), kein Rate-Limit sichtbar, Preview-Secret im Repo (`preview.ts:19-21`) |
| Session-Handling | ✅ produktionsnah | `__Host-`-Cookies, Bearer-Fallback, beweisbarer Sign-out |
| Tenant-Isolation | ◐ applikativ korrekt, DB-seitig offen | **kein RLS** (D04 nicht umgesetzt), Guard nur an 3 Server-Functions, `ensurePrimaryTenant` ohne `ON CONFLICT` |
| App-Data | ⬜ toter Code (700 Z., 0 Importer) | Streichen/Auslagern |
| Multiplayer/P2P | ⬜ toter Code (579 Z.), **widerspricht D10** | Streichen |
| Konzeptdaten | ✅ sehr hoch | deprecated Aliase, unsortiertes OFFEN-Array |
| DB-Schicht (`db.ts`) | ✅ produktionsreif | PGLite in-memory → Flüchtigkeit by design |
| Preview-Bridge | ✅ produktionsreif, plattformgebunden | noop außerhalb des Grok-Hosts |
| Styles/Tokens | ✅ hoch | Error-Component bricht Token (zinc statt sage) |

## T8 — Skripte/Migrations-/Build-Werkzeuge

| Werkzeug | Art | Test |
|---|---|---|
| `migrate.mjs` + `migration-plan.mjs` | produktiv (Build-Pfad) | 7 Tests (nur Plan-Logik) |
| `check-auth-invariant.mjs` | CI-Wächter | 11 Tests |
| `with-app-env.mjs` + `app-env-plugin.mjs` | produktiv/dev | 12 Tests / ⬜ |
| `grok-pwa-plugin/-shared` + Middleware | produktiv | 40+ Tests (indirekt für shared) |
| `sign-out-plan.mjs` | produktiv (importiert) | 18 Tests |
| `browser-smoke/-verdict`, `brand-check`, `preview-thumbnail`, `browser-guard` | Agent-Werkzeuge | 40 / 14 / ⬜ / ⬜ |
| `canon-contract.mjs` (+ `check:canon`) | **nur auf kanon-Zweig** | 10 Tests (Zweig) |
| `check-push-graph.mjs` + `check-project-control-k1.mjs` | nur konsolidierung (Task 3/4) | Tests vorhanden, Dirty-Overlay |
| Migrations 0001/0002 | ✅ angewendet (Build-Pfad) | Duplikat ohne Drift-Wächter |

## T9 — Werkzeug-/Plattform-Abdeckung

| Aspekt | Zustand |
|---|---|
| CI (GitHub Actions) | ⬜ nie definiert |
| Branch-Protection / PR-Pflicht | ⬜ nicht beobachtbar; 0 PRs in der Historie |
| `gh`-CLI | ⬜ Keyring-Token ungültig (401) → Re-Auth nötig |
| Qualitätskette lokal (Haupt-Checkout) | ⬜ kein `node_modules` |
| Qualitätskette lokal (3 Worktrees) | ✅ **node_modules vorhanden** → lauffähig ohne Installation (neu in V6) |
| Windows-Testbarkeit | ◐ `npm test`-Glob + browser-guard-Pfade scheitern unter Windows (K1-T7/T9 fixen das) |
| Security-Header/CSP | ⬜ nirgends gesetzt |

## T10 — Dokumentationsstand

| Dokument | Stand |
|---|---|
| `AGENTS.project.md`, `docs/STATUS.md`, `GATE-STATUS.md`, Ground-Zero-Spec | ✅ aktuell (25.08.) |
| `docs/09-roadmap.md`, `20-freigabe.md`, `26-wiedervorlage.md`, `23-id-schema.md` | ◐ WV03/WV05-Namen uneinheitlich; D08–D12-Tabelle veraltet |
| `README.md`, `llms.txt`, `.github/copilot-instructions.md`, `docs/00-index.md`, `docs/25-offen.md` | ⬜ hinken hinter 25.08.-Stand her (Pause/Gate nicht genannt) |
| `docs/project-control/README.md` | ✅ aktuell, benennt Altverweise selbst |
| K1-Dokumente (`K1-STATUS`, `QUALITY-ROUTING`, Sync-Evidenz) | ✅ aktuell (26.08.) — **nur auf konsolidierung-Zweig** |
| Migrationsdesign | ✅ approved (27.08.) — Plan **ungetrackt** |
| Portalcode vs. Kanon | ⬜ 9 Widersprüche (§6 in `02_PROJEKTANALYSE_VON_NULL_V6.md`) |
