# AURELIA — Tiefenanalyse V5: Status-Tabellen (Gesamtansicht)

**Stand: 2026-08-28, 09:28 CEST · Nur-Lese-Analyse**
**Legende:** ✅ umgesetzt/abgenommen · 🟡 teilweise · ⬜ offen/nicht begonnen · ⏸ pausiert (bewusst) · 🔒 gesperrt (Verfassung) · ❌ gestrichen
**Prozent:** Modellwerte nach Methodik in `04_PHASEN_UND_PROZENT_V5.md` (Planung/Umsetzung/Abnahme 30/50/20) — nicht gemessene Produktivität.

---

## T1 — Phasen-Gesamtübersicht (Roadmap `docs/09-roadmap.md` + Querschnittsprogramme)

| Phase | Name | Umfang (Kurzform) | Planung | Umsetzung | Abnahme | **Gesamt %** | Status |
|---|---|---|---|---|---|---|---|
| 0 | Konzept | Verfassung, C gesetzt, X-Katalog | 100 % | 100 % | 100 % | **100 %** | ✅ abgenommen 2026-08-23/24 |
| G0-SRV | Server Ground Zero | Backup/Restore, Ubuntu 24.04.4, RAID1/LUKS2/LVM, Härtung, GNOME/Codex, NVIDIA ohne CUDA | 90 % (→ effektiv 60 %, da 35 % der Pläne uncommitted) | 5 % (nur read-only Inventur, ISO-Hash) | 0 % (0/13 Gates) | **≈ 20 %** | ⏸ `G0-SRV-0` wartet auf Nachweis |
| 1 | Gehäuse | Mandant, Rollen, Anmeldung, leere App-Schale | 95 % | 75 % | 0 % | **≈ 65 %** | ⏸ pausiert bis G0-SRV |
| 2 | Praxisorganisation | Klienten, Gruppen, Dienste, Einwilligungen, Zwischenablage; WV01 vor Art. 9 | 75 % | 0 % | 0 % | **≈ 22 %** | ⬜ Konzept vorhanden |
| 3 | Kernel-ABI + Raten | Registry, gewrappte Prototypen im Labor | 70 % | 0 % | 0 % | **≈ 21 %** | ⬜ |
| 4 | Analyse strikt | CPU-Referenz, CUDA-Scheduler, Passport | 70 % | 0 % | 0 % | **≈ 21 %** | ⬜ |
| 5 | Harmonisierung | Timerd, parallele Kanäle, Spur-Zustände | 70 % | 0 % | 0 % | **≈ 21 %** | ⬜ |
| 6 | Archiv / Trend / Report | Continuous Aggregates, PDF; WV06 Codecs | 60 % | 0 % | 0 % | **≈ 18 %** | ⬜ |
| 7 | GPU-Härtung | VRAM-Allocator, Attestation, Queue-Policy | 65 % | 0 % | 0 % | **≈ 20 %** | ⬜ |
| 8 | Quantum opt-in | cuQuantum hinter ABI | 60 % | 0 % | 0 % | **≈ 18 %** | ⬜ |
| 9 | ~~WebRTC + Medien~~ | — | — | — | — | **N/A** | ❌ gestrichen (D10, O08) |
| 10 | Betrieb | Abos scharf; WV02 Preise, WV03 Passkeys, WV05 Mini-VPS | 60 % | 0 % | 0 % | **≈ 18 %** | ⬜ |
| **Querschnitt K1** | Kanonkonsolidierung (14 Tasks) | widerspruchsfreier Kanon über alle Linien, ohne Merge/Rebase | 100 % (Design/Plan) | 18 % (T1–T3) | 14 % (2/14 Tasks abgenommen) | **≈ 16 %** | 🟡 blockiert an Task-3-Review |
| **Querschnitt GATE-G0** | Governance-Programm | Trust, Ledger, Recovery, Egress, Authentifizierung | 100 % Design (eingefroren) · Pläne nur lokal | 0 % (kein Code/Register/Pins) | 0 % | **≈ 25 %** | 🟡 wartet auf Operator-Freigabe + Commits |
| **Querschnitt Migration** | Linux-Workstation-Migration | Replikation des lokalen Gesamtstands vor Workstation-Neuinstall | 100 % Design (approved) · Plan ungetrackt | 0 % | 0 % | **≈ 35 %** | 🟡 Ausführung offen |

**Modellierter Gesamtfortschritt des Projekts: ≈ 30–35 %** (gewichtetes Rollup; Detailherleitung in 04).

---

## T2 — G0-SRV-Gatefolge (13 Gates; Quelle: `GATE-STATUS.md`, Serverdesign §11)

| Gate | Ziel | Vorbereitung | Ausführung | Abnahme | Status |
|---|---|---|---|---|---|
| G0-SRV-0 | Externes Backup + Restore-Nachweis (≥2 Kopien, ≥1 verschlüsselt EU-Offsite, SHA-256-Manifest, echtes Restore) | ✅ Design + Pflichten §9 | ⬜ 0 % | ⬜ | **wartet auf Nachweis** (Blocker) |
| G0-SRV-1 | IPMI/BMC, Remote-KVM, Virtual Media | ✅ | ⬜ | ⬜ (Betreiberbestätigung ja, Funktionstest nein) | 🟡 |
| G0-SRV-2 | Hardware/Firmware/UEFI-Inventur | ✅ | 🟡 read-only Teilinventur (2×2 TB SN850X, RAID1 gesund, Secure Boot off; ECC unbewiesen) | ⬜ | 🟡 ≈ 40 % |
| G0-SRV-3 | RAID1/LUKS2/LVM-Installation | ✅ Plan | ⬜ (gesperrt bis 0–2) | ⬜ | ⏸ |
| G0-SRV-4 | Boot/Encryption/Recovery | ✅ Plan | ⬜ | ⬜ | ⏸ |
| G0-SRV-5 | Identitäten/SSH/VPN/Firewall | ✅ Plan | ⬜ | ⬜ | ⏸ |
| G0-SRV-6 | minimales GNOME + isolierter Codex-Nutzer | ✅ Plan | ⬜ | ⬜ | ⏸ |
| G0-SRV-7 | NVIDIA-Baseline (kein CUDA) | ✅ Plan | ⬜ | ⬜ | ⏸ |
| G0-SRV-8 | Security/Logging/Updates | ✅ Plan | ⬜ | ⬜ | ⏸ |
| G0-SRV-9 | PostgreSQL-16-Basis | ✅ Plan | ⬜ | ⬜ | ⏸ |
| G0-SRV-10 | Offsite-Backup/Restore (RPO ≤ 15 min DB / ≤ 60 min Objekte, RTO ≤ 8 h) | ✅ Plan | ⬜ | ⬜ | ⏸ |
| G0-SRV-11 | Selektiver Projekt-Restore ohne Altsecrets | ✅ Plan | ⬜ | ⬜ | ⏸ |
| G0-SRV-12 | Gesamtbaseline (High/Critical-frei, Reboot-/Soaktests) | ✅ Plan | ⬜ | ⬜ | ⏸ |
| **Summe** | | | | **0 / 13 bestanden** | |

Voraussetzungen (`GATE-STATUS.md`): IPMI, KVM, Virtual Media, USV, Backupsystem, DDoS-Schutz = 6/6 **Betreiberbestätigung** · 0/6 **technische Abnahme**. `server_changes_started: false` · `destructive_actions_allowed: false`.

## T3 — K1-Kanonkonsolidierung (14 Tasks; Quelle: `K1-STATUS.md` im Konsolidierungs-Worktree)

| Task | Inhalt | Status | Abnahme |
|---|---|---|---|
| T1 | K1-Steuerung + V1/V2-Provenienz-Sanitisierung | ✅ | Spec-Review PASS · Qualitätsreview PASS |
| T2 | Nichtnormative Governance-Grenze `GATE-GOV-0` | ✅ | beide Reviews PASS |
| T3 | Fail-closed Push-Graph-Scanner | 🟡 ~80 % (4 Security-Fixes committet; Overlap-Korrektur uncommittet) | **erneutes Spec-Review AUSSTEHEND** → Qualitätsreview blockiert |
| T4 | K1-Kanonmatrix + Kanonvalidator | ⬜ | blockiert bis T3-Doppel-PASS |
| T5–T11 | Produktdoku, Portal, Testrunner-Glob-Fix, Auth-Abnahme, Lint-Basis … | ⬜ | blockiert |
| T12 | Plattform-Assets | ⬜ `external_blocker` (fehlende Provider-Assets; dürfen nicht erfunden werden) | blockiert |
| T13 | Lint-/Qualitätsabschluss | ⬜ | blockiert |
| T14 | `K1-VERIFICATION.md` + Abschluss | ⬜ | blockiert |
| **Summe** | | **2/14 abgenommen · 1 in Arbeit · 11 blockiert** | **≈ 16 %** |

## T4 — Governance-Track (GATE-G0; Quelle: G0-Governance-Spec + Masterplan, nur lokal)

| Baustein | Design | Umsetzung | Abnahme |
|---|---|---|---|
| Governance-Spec (3.968 Zeilen, Krypto-/Ledger-/Recovery-/Egress-/Auth-Verträge) | ✅ eingefroren (Byte-Hash fixiert) | — | ⬜ Operator-Freigabe als Ed25519 `REV-G0-DESIGN-APPROVAL` fehlt |
| Masterplan + Teilpläne 01–13 | ✅ ausformuliert | ⬜ **ungetrackt** (nicht committet) | ⬜ |
| Register (Traceability/Risk/DPIA/Gate), Schemas, Validator, Zeremonie-CLI | definiert (Format) | ⬜ 0 % | ⬜ |
| Externe Trust-Pins, Schlüsselzeremonie D→I→G, Custodian-/Fachrollen | definiert | ⬜ Pins existieren nicht; Rollen unbesetzt | ⬜ |
| M-G1-Collector-Vertrag (Plan 10) | ✅ | ⬜ kein Code | ⬜ |

## T5 — Entscheidungskanon: ID-Familien (Status je Item)

### T5.1 Leitentscheidungen D01–D24 — Kanon: `src/lib/concept/decisions.ts` (`CANONICAL_DECISION_LOCKS`)

| IDs | Status | Anmerkung |
|---|---|---|
| D01–D04, D06, D07 | ✅ gesetzt | Details in `decisions.ts` (alleinige Statusautorität) |
| D05 | ✅ gesetzt | WebRTC-Restbestand im Kanon entfernt |
| D08 | ✅ gesetzt | Passkeys (Ziel Ubuntu; Vorschau E-Mail/Passwort); Umsetzung WV03 |
| D10, D12 | ✅ gesetzt | kein Video/WebRTC (mit O08) |
| D09 | 🟡 empfohlen | Preise → **WV02** |
| D11 | 🟡 empfohlen | Codecs → **WV06** |
| D13–D19 | ✅ gesetzt | |
| D20 | ✅ gesetzt | virtuelle Timer viele/cheap, kein Overcommit |
| D21 | ✅ gesetzt | HRV-Ohrclip `hrv.earclip`, kein EEG |
| D22, D23 | ✅ gesetzt | Kozyrev K1–K5 admin-togglebar; `kozyrev.lab.*` `executable:false` |
| D24 | ✅ gesetzt | |

### T5.2 Betreiberbestätigungen C01–C12 — ✅ alle gesetzt (u. a. C03 VRAM-Budget, C05 Zahl-20-Präzisierung, C10 REG `simulated`, C12 Klient-Edits nur über Praktiker)

### T5.3 X-Katalog X01–X20 — ✅ akzeptiert (2026-08-24); nicht umsetzbar/nicht relevant; bewusst **keine** Implementierung

### T5.4 U01–U12 (Unklar → Empfehlung übernommen; alle gelöst) — ✅

| ID | Ergebnis (Kurzform) |
|---|---|
| U01 | Zahl 20 = Beispielzahl gleichzeitiger Klienten (via C05, D20) |
| U02 | Klient-Edits nur `client_editable_fields`, Promote durch Praktiker (C12) |
| U03 | Mehrere Spuren pro Klient bis Quota; Emitter max. 1 global |
| U04 | v1 nur p=2 (Haar); p>2 Labor-Mandant |
| U05 | REG-Modul getrennt, Quelle `simulated` (C10) |
| U06 | cuQuantum im selben 16-GB-Pool, opt-in, nie CopyGuard-RAM |
| U07 | CopyGuard-Gewichte auf beiden NVMe, Gemma-3-1B-Fallback |
| U08 | Tick 50 ms aus timerd-RAM; Checkpoint 500–1000 ms Postgres; Analyse 200 ms |
| U09 | **Phase 1 „Gehäuse" gestartet** (Startwort 2026-08-24) — per Canon-Textregel verriegelt |
| U10 | Draft-TTL 7 Tage, Archiv-Vorschlag, kein Auto-Delete |
| U11 | D08/D10/D12 gesetzt; D09/D11 Wiedervorlage |
| U12 | HRV-Ohrclip; kein WebUSB für Spooky2; Art. 9 gilt für RR-Reihe |

### T5.5 Kozyrev K1–K8 — K1–K5 ✅ gesetzt, admin-togglebar · K6–K8 🔒 gesperrt (kein Kernel-ID, kein Flag, kein 3-Tier-Scaffold)

### T5.6 Hybrid H1–H8 — H1–H3 ✅ gesetzt · H4 🟡 optional (WV05-Kontext) · H5–H8 🔒 gesperrt

### T5.7 Offen O01–O10 — ✅ erledigt: O01, O02 (Phase-1-Start), O06, O08 (kein Video), O10 · → Wiedervorlage: O04→WV01, O03→WV04, O05→WV05, O07→WV02, O09→WV06

### T5.8 Wiedervorlage WV01–WV06

| ID | Thema | Geplant | Status |
|---|---|---|---|
| WV01 | Externes Backup + Restore-Nachweis | vor Ground Zero; erneut vor Art. 9 | ⬜ **aktiv — identisch mit G0-SRV-0** |
| WV02 | Abo-Preise | Phase 10 | ⬜ |
| WV03 | Passkeys auf Ubuntu | nach G0-Baseline | ⬜ |
| WV04 | Lovable disconnect | nur auf Wunsch | ⬜ |
| WV05 | Mini-VPS | Phase 10, falls Website ≠ GPU-Uptime | ⬜ |
| WV06 | Codecs | Phase 6 | ⬜ |

## T6 — Branch-Matrix (Divergenzansicht; Kern des Konsolidierungsproblems)

| Thema | `vorbereitung` (Haupt) | `kanon-implementation` | `g0-governance` | `konsolidierung` | Zielbild (K1-Matrix) |
|---|---|---|---|---|---|
| Phase-1-Status | ⏸ pausiert (G0-SRV) | Phase 1 gestartet (U09-Lock, ohne Pause-Marker) | Phase 1 aktiv (**Pause entfernt**) | ⏸ pausiert bis G0-SRV-12 | ⏸ pausiert bis G0-SRV-12 |
| Ziel-OS | Ubuntu 24.04.4 | Restaltverweise möglich | Debian-Reste entfernt (Kanon) | Ubuntu verankert | Ubuntu 24.04.4 |
| G0-SRV-/Analysedocs | ✅ gepflegt | ⬜ fehlen (nie enthalten) | ❌ **gelöscht** | ✅ gepflegt | ✅ erhalten + Governance-Track verknüpft |
| Kanon-Contract (`check:canon`) | ⬜ | ✅ | ✅ | geplant (T4) | ✅ inkl. Ground-Zero-Docs |
| Governance-Design | ⬜ | ⬜ | ✅ eingefroren | Grenze `GATE-GOV-0` ✅ | ✅ eingebunden |
| Push-Graph-Scanner | ⬜ | ⬜ | ⬜ | ✅ (+4 Fixes) | ✅ |
| Commits vs. `vorbereitung` | 0 | +14 | +32 | +27 (**13 unpushed**) | — |

## T7 — Qualitäts-/Sicherheitsgates (Ausführbarkeit)

| Gate | Kommando | Haupt-Checkout | Kanon-Branch | Konsolidierung | V5-Ausführung |
|---|---|---|---|---|---|
| Tests | `npm test` | 175 Tests vorhanden, aber Windows-Glob-Risiko + kein `node_modules` | 185 Tests | +Scanner-Tests | **nicht ausgeführt** (Nur-Lese-Gebot) |
| Typecheck | `npm run typecheck` | vorhanden | vorhanden | vorhanden | **nicht ausgeführt** |
| Auth-Invarianz | `npm run check:auth` | ✅ | ✅ | ✅ | nicht ausgeführt |
| Canon | `npm run check:canon` | ⬜ fehlt | ✅ | geplant T4 | nicht ausgeführt |
| K1-Control | `npm run check:k1-control` | ⬜ | ⬜ | ✅ | nicht ausgeführt |
| Push-Graph | `npm run check:push-graph` | ⬜ | ⬜ | ✅ (Exit 2 ohne Argumente = fail-closed by design) | nicht ausgeführt |
| Lint/Format | `npm run lint` / `format` | ✅ | ✅ (Baseline bereinigt) | ✅ | nicht ausgeführt |
| DB-Migration | `npm run db:migrate` | ✅ 0001_auth + 0002_tenants | identisch | identisch | **nicht ausgeführt** (schreibend) |

## T8 — GitHub-Fernzustand (rein `ls-remote`, privat → API 404)

| Beobachtung | Wert |
|---|---|
| Branches remote | main `b858ccd` · vorbereitung `8706186` · kanon `b20ee87` · g0-governance `a6a8e7d` · konsolidierung `029bdce` |
| Push-Rückstand | konsolidierung lokal +13 Commits; alle anderen synchron |
| PRs/Issues/CI/Branch-Protection | **nicht beobachtbar** ohne Authentifizierung; Governance-Dokumente führen Branchschutz-Evidenz selbst als „unknown/red" |
| Publikationsgate (Projektintern) | `blocked` (Kategorien `credential_like`, `operational_identity`) — letzter abgegrenzter Push 26.08. mit Evidenz |
