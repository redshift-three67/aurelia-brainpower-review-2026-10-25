# AURELIA Tiefenanalyse V6 — Ergänzende Innovationen

## Teil A — Vorhandene Innovationen (Würdigung, 7)

1. **Maschinell prüfbarer Projektkanon** (`canon-contract.mjs` + `check:canon`,
   Zweig `kanon-implementation`): exakte ID-Mengen, `CANONICAL_DECISION_LOCKS`,
   prohibited/required-Regexe — Statusdrift wird zum Buildfehler. Selten für
   Nicht-Code-Dokumentation.
2. **Fail-closed Push-Graph-Scanner mit TS-AST-Adjudikation** (K1-T3):
   vollständiger erreichbarer Graph (4096 Commits/100k Pfade), 7
   Diagnosekategorien ohne Fundwerte, Exit 0/1/2, Root-Bindung per
   realpath/dev/ino; die AST-Adjudikation unterdrückt nur echte
   `PropertySignature`-Typreferenzen, sonst fail-closed. Ungewöhnlich reif.
3. **Zwei-Spuren-Qualitätsrouting** (`QUALITY-ROUTING.md`): Spur A (Fast
   Assurance, deterministisch prüfbar, kein Reviewer zwingend) vs. Spur B
   (Critical Assurance, TDD + Spec-Review + Qualitätsreview); unklare
   Risikoklasse = fail-closed Spur B; Modell-/Reasoning-Routing inklusive.
4. **G0-Governance-Design** (3.968 Z., eingefroren): RFC-8785-Kanonisierung,
   Append-only-Transition-Ledger mit Hash-Kette + Nonce-Einmaligkeit,
   Witness-Marker mit CAS-Preconditions (A→B→A-Replay scheitert), versiegelte
   Egress-Intents mit Idempotenz-Tombstonen — Governance-Buchführung auf
   Krypto-Datenbankniveau.
5. **Gate-Identity & Sibling-Isolation**: Ed25519/EdDSA-JWT mit JWKS-Cache
   (5 min), `maxTokenAge` 10 min, Identity-Swap räumt Session + Cache;
   Fetch-Metadata-Sibling-Guard als Chokepoint.
6. **Verfassungsarchitektur**: 26 Hard rules, Stop-Gates, X-Katalog (bewusst
   nicht implementierte IDs bleiben sichtbar), WV-Mechanik, Heritage-Tabelle,
   Merge-/Rebase-Verbote für historische Zweige.
7. **Produktkonzepte mit Fail-closed-DNA**: CopyGuard (Lexikon fail-closed +
   lokales Slim-LLM im RAM, 0 GB VRAM), Computation Passport mit
   `copyguard_digest`, Timer-Ledger (Postgres WAL = Uhr, RAM = Ticks, „do not
   invent time"), Kernel-Flags dreistufig, Emitter-Lease ≠ GPU-Lease.

## Teil B — Neue Vorschläge (N1–N18)

### Priorität A — kritischer Pfad

| # | Vorschlag | Schließt |
|---|---|---|
| N1 | **[V6, neu]** Qualitätskette **jetzt** in einem Worktree ausführen (`npm test`, `typecheck`, `check:auth` in `.worktrees/aurelia-konsolidierung` oder `-kanon`) — ohne Installation, ohne Schreibzugriff aufs Repo möglich; Ergebnis als Evidenzpunkt dokumentieren | L3.4 sofort |
| N2 | **[V6, neu]** `gh auth login` (Account `radiquant`, Keyring-Token ungültig) → danach E2: PR-/Issue-/Protection-Evidenz beschaffbar | L4.2 |
| N3 | Replikationskapsel nach eigenem Migrationsdesign (Layer A/B/C) ausführen — Generalprobe für `G0-SRV-0`/WV01 **und** Beseitigung des SPOF mit einer Handlung | L2.1, Vorbereitung L1.1 |
| N4 | Review-Eskalationsfenster in `QUALITY-ROUTING.md` §4 (z. B. 5 Arbeitstage ohne Reviewtermin → Betreiber-Eskalation; Spur-B-Review-Paket ist minimal und kann delegiert werden) | L2.2, L5.2 |
| N5 | K1-Task-3-Spec-Review terminieren (fokussiertes Paket: Vertrag + Diff + frische Testausgabe) → danach Qualitätsreview → Tasks 4–14 | L2.2 |

### Priorität B — Durchsetzung und Härtung

| # | Vorschlag | Schließt |
|---|---|---|
| N6 | `data_class` fail-closed: CHECK-Constraint `data_class IN ('synthetic')` in Migration 0003 + negativer Test + Rollen-CHECK | L3.1 |
| N7 | Security-Header-Baseline (CSP mit `frame-ancestors`, `X-Content-Type-Options`, `Referrer-Policy`) an einer Stelle zentral (Nitro-Middleware) | L3.2 |
| N8 | RLS-Grundschema in Migration 0003 (`ENABLE ROW LEVEL SECURITY` + `current_setting`-Policies + negative Tests) | L3.1 |
| N9 | Windows-fester Testrunner: `npm test`-Glob durch explizite Dateiliste ersetzen (K1-T7 beschleunigen) + `browser-guard`-Pfade portabel | L3.4 |
| N10 | GitHub-CI beim nächsten sauberen Push: `typecheck`, `test`, `check:auth`, `check:canon` (nach T4), `check:push-graph` + Branch-Protection | L4.1 |
| N11 | Kanon-Contract auf Konsolidierungslinie heben und auf `docs/project-control/**` + Gate-Matrix erweitern (`destructive_actions_allowed: false` pflichtig solange `G0-SRV-0` nicht bestanden) | L2.6, L2.4 |
| N12 | Gate-Status maschinell spiegeln (`gates.json` + Portal-Widget `/status`) — eine Quelle für Docs, Portal und künftiges Dashboard | L2.4, L5.4 |
| N13 | ECC-Nachweis-Runbook als Erweiterung von G0-SRV-2 (Teilenummer, BIOS, EDAC/RAS, IPMI-SEL-Monitoring, Memtest mit ECC-Verifikation, EVID-Artefakt) | L1.3 |
| N14 | `.env.example` vollständig dokumentieren (alle gelesenen Variablen mit Zweck, ohne Werte) | L3.7 |

### Priorität C — Produktferne Zukunft (Konzeptnotiz)

| # | Vorschlag |
|---|---|
| N15 | Phase-spezifische Abnahme-Skripte (Playwright-Smoke je Phasenabschluss, Protokoll als EVID) |
| N16 | Axe-core-Accessibility-Gate (WCAG 2.2 AA/BFSG) in der Phase-1-Abnahme |
| N17 | Restore-Drill-Kadenz (quartalsweise, aus G0-SRV-10 ableitbar) |
| N18 | Gate-Dashboard auf M G1 (statisches HTML aus `gates.json` im isolierten GNOME) |

### Bewusst nicht vorgeschlagen

Serveränderungen vor `G0-SRV-0`-Bestehen · K6–K8-/H5–H8-Scaffolds ·
Video/WebRTC · Lovable-Publish · `/opt/radiquant4`-Schreibzugriff ·
Passkey-Produktivsetzung vor M G1 · Governance-Genesis ohne
`REV-G0-DESIGN-APPROVAL`.

## Abschlussbetrachtung

Das Projekt hat seine wichtigsten Werkzeuge (canon-contract, push-graph-scanner,
Qualitätsrouting, Migrationsdesign) **bereits erfunden**. Die Vorschläge
bestehen überwiegend daraus, diese Werkzeuge **auf die eigene Schwachstelle
zurückzuwenden** — N1 und N3 sind sogar am selben Tag noch möglich, ohne eine
einzige bestehende Regel zu verletzen.
