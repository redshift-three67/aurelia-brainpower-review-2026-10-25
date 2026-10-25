# AURELIA — Tiefenanalyse V5: Ergänzende Innovationen

**Stand: 2026-08-28, 09:28 CEST · Nur-Lese-Analyse · Alle Vorschläge non-normativ (Verfassungsregel: externes Analysematerial ist erst nach Übernahme in freigegebene Spezifikation ausführbar)**

---

## Teil A — Bestehende Innovationen (Würdigung, bereits im Projekt)

| Innovation | Ort | Warum sie bemerkenswert ist |
|---|---|---|
| **Maschinell prüfbarer Projektkanon** (`canon-contract.mjs`, `check:canon`) | kanon-Branch | Verwandelt Verfassungsregeln in ausführbare invariant checks: exakte ID-Mengen, alleinige Statusautorität `CANONICAL_DECISION_LOCKS`, prohibited/required-Regexe — Statusdrift wird zum Buildfehler. Selten in Nicht-Code-Dokumentation. |
| **Fail-closed Push-Graph-Scanner** mit TS-AST-Adjudikation | konsolidierung-Branch | Scannt den **vollständigen erreichbaren Graphen** (nicht nur Deltas), klassifiziert Secrets/Identitäten/Hosts/Pfade, antwortet mit festen Diagnosecodes ohne Fundwerte, Exit 0/1/2 in jede Unsicherheitsrichtung. Die AST-Adjudikation (Unterdrückung nur echter Typsignaturen, fail-closed sonst) ist ungewöhnlich reif. |
| **Spur-A/B-Qualitätsrouting** | `QUALITY-ROUTING.md` | Skaliert Reviewtiefe nach Schadenspotenzial statt pauschal; unklare Risikoklasse = fail-closed Spur B. Verhindert Review-Stau ohne Sicherheitsverlust. |
| **G0-Governance-Design: RFC-8785 + Append-only-Ledger + Witness-Marker** | g0-governance-Branch (Spec, eingefroren) | Kanonisierte Signed-Cores (SHA-256 über exakte Payload), lückenlose Event-Kette mit Nonce-Einmaligkeit, GitHub-Marker als Replay-sicheres öffentliches Witness-Log (Certificate-Transparency-Stil), versiegelter Egress-Intent mit Idempotenz-Tombstonen — Governance-Buchführung auf Krypto-Datenbankniveau. |
| **Gate-Identity & SameSite-Sibling-Isolation** | `gate-identity.server.ts`, `isolation.server.ts` | Ed25519-JWT mit JWKS-Rotation und 10-min-Tokenalter; Fetch-Metadata-Guard gegen Cookie-Riding zwischen Preview-Nachbarn — präzise Bedrohungsmodellierung der eigenen Hosting-Umgebung. |
| **Verfassungsarchitektur des Projekts** | `AGENTS.project.md`, `docs/` | Verfassungsregeln (26), Stop-Gates, X-Katalog (bewusst Nicht-Baues), Wiedervorlage-Mechanik (WV), Heritage-Tabelle gegen Repo-Verwechslung — organisatorische Innovation, die Konsolidierungsprojekte normalerweise erst nach Schmerz einführen. |
| **Produktkonzepte mit Fail-closed-DNA** | `docs/04–24` | CopyGuard (Lexikon fail-closed + lokales Slim-LLM im RAM), Computation Passport mit `copyguard_digest`, Timer-Ledger (Postgres WAL + RAM, „keine erfundene Zeit"), Kernel-Flags dreistufig fail-closed, Emitter-Lease ≠ GPU-Lease. |

## Teil B — Neuvorschläge (verfassungskonform, Priorität A = schnell wirksam)

### Priorität A — direkt entlang des kritischen Pfads

| # | Vorschlag | Nutzen | Verfassungsbezug |
|---|---|---|---|
| N1 | **`data_class` fail-closed machen:** DB-CHECK-Constraint `data_class IN ('synthetic')` in Migration 0003 + Test, der einen Art.-9-ähnlichen Insert verweigert; plus Helferfunktion, die Insert-Objekte zwangsweise annotiert | Schließt L3.1; macht Verfassungsregel 21 maschinell statt konventionell | Regel 21, fail-closed-Grundsatz |
| N2 | **Gate-Status maschinell spiegeln:** `GATE-STATUS.md`-YAML + Gatefolge als maschinenlesbare Datei (`gates.json`) und Portal-Widget `/status` (Ampel je Gate, Stand, nächster Nachweis); Canon-Contract erweitert auf `docs/project-control/**` (schließt L2.6) | Gatezustand wird prüfbar und im Portal sichtbar; Statusdrift wie beim D-Kanon ausgeschlossen | Änderungspflicht des project-control-README |
| N3 | **Replikationskapsel sofort (Trockenübung für WV01):** das im Migrationsdesign beschriebene Layer-A/B/C-Verfahren bereits vor der Workstation-Migration einmal ausführen — Git-Bundle aller Refs + verschlüsselte Kapsel auf 2 Medien + verifizierter Restore in ein temporäres Verzeichnis | Beseitigt SPOF L2.3 **und** ist zugleich realistische Generalprobe für den geforderten externen Backup-/Restore-Nachweis (G0-SRV-0/WV01) — zwei Blocker mit einer Handlung | WV01, G0-SRV-0-Sinnbild |
| N4 | **Review-Eskalationsfenster:** in `QUALITY-ROUTING.md` §4 eine Zeitbox ergänzen (z. B. 5 Arbeitstage ohne Reviewtermin → Betreiber-Eskalation statt Stillstand); betrifft die K1-T3-Schnittstelle | Verhindert L5.2-Kaskade (11 Tasks warten auf 1 Review) | QUALITY-ROUTING §4 (eigenes Dokument) |

### Priorität B — Qualitäts-/Infrastrukturschärfe

| # | Vorschlag | Nutzen |
|---|---|---|
| N5 | **Windows-fester Testrunner:** Node-Test-Glob durch explizite Dateiliste ersetzen (K1-T12/13 vorziehen oder vorziehen lassen); Ziel: `npm test` findet auf Windows **alle** Suites | Schließt L3.4; Qualitätskette wird plattformunabhängig |
| N6 | **GitHub-CI bei nächstem sauberen Push:** Workflow mit `typecheck`, `test`, `check:auth`, `check:canon`, `check:push-graph` (read-only Gates) + Branch-Protection auf dem konsolidierten Kanon-Branch | Verlagerung der Gates auf die replizierte Plattform; PR-Pflicht = Zweitaugenprinzip |
| N7 | **ECC-Nachweis-Runbook als Erweiterung von G0-SRV-2:** IPMI-SEL-Monitoring + Memtest-Phase mit ECC-Verifikation, Ergebnis als EVID-Artefakt | Schließt L1.3 innerhalb der ohnehin fälligen Hardwareabnahme |
| N8 | **RLS-Grundschema in Migration 0003:** `ENABLE ROW LEVEL SECURITY` auf `tenants`/`memberships` mit `current_setting('app.user_id')`-Policies + negative Tests (fremder tenant_id-Zugriff muss leer/error) | Schließt L3.2; Datenbankebene wird zweite Verteidigungslinie (Arbeitspaket C vorziehen) |
| N9 | **Canon-Contract-Erweiterung um Gate-Matrix:** Textregeln für `GATE-STATUS.md` (z. B. `destructive_actions_allowed: false` pflichtig solange `G0-SRV-0` nicht bestanden) | Stop-Regel wird maschinell bewacht (L2.4/L2.6) |
| N10 | **Deterministische-Build-Evidenz:** `npm ci`-only, Build-Hash als Vorbereitung des späteren Computation Passports; heute schon: `package-lock.json` als geschützte Datei im Canon-Contract | Vorbereitung für Reproduzierbarkeitsregel 7 |

### Priorität C — Produktferne Zukunft (nur Konzeptnotiz, keine Arbeit)

| # | Vorschlag | Einordnung |
|---|---|---|
| N11 | **Phase-spezifische Abnahme-Skripte** (Playwright-Smoke je Phasenabschluss, Protokoll als EVID) | Ordnet sich Phasenabnahmen der Roadmap unter |
| N12 | **Axe-core-Accessibility-Gate** (WCAG 2.2 AA) in der Phase-1-Abnahme | Verfassungsregel 9 (WCAG 2.2 AA/BFSG) wird messbar |
| N13 | **Restore-Drill-Kadenz** (quartalsweise, aus G0-SRV-10 ableitbar, Protokollpflicht) | Betriebliche Fortschreibung von WV01 |
| N14 | **Gate-Dashboard auf M G1** (statisches, aus `gates.json` generiertes HTML im isolierten GNOME) | Betreiber sieht Gatefortschritt ohne Chat-Kontext (Änderungspflicht-Grundsatz des project-control-README) |

## Abschlussbetrachtung Teil B

Auffällig: Das Projekt hat seine wichtigsten Werkzeuge (canon-contract, push-graph, Qualitätsrouting) **bereits erfunden**; die Vorschläge N1–N10 bestehen fast ausschließlich daraus, diese Werkzeuge **auf die eigene Schwachstelle zurückzuwenden** — Datenklasse (N1), Gate-Dokumente (N2/N9), lokale Replikation (N3), Review-Fluss (N4), Testrunner (N5), GitHub (N6). Das ist die kostengünstigste Innovationsstufe: bestehende Invarianten konsistent anwenden.
