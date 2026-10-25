# 02 — Projektanalyse von Null (Codebasis & Kanon, 2026-08-25 17:33 CEST)

---

## 1. Produktkanon — Neubewertung

### 1.1 Was die Verfassung (`AGENTS.project.md` + `docs/`) festlegt
- **Produktzweck:** Wellbeing-/Dokumentationssoftware für ausgebildete Praktiker; radionische Praxisorganisation mit versionierten Rechenkernen, serverautoritativen Timern, CopyGuard auf jedem sichtbaren Satz.
- **Nicht-Ziele (hart):** kein Medizinprodukt, keine Diagnose/Therapie/Heilversprechen, kein Video/WebRTC (D10), kein WebUSB (D14), kein Cloud-LLM über Akten (D13), kein MIG (X01), kein 3-Tier-KI (K6/X05), kein Lovable in der Laufzeit (H5–H8 gesperrt).
- **Hardware-Kanon:** RTX 4000 SFF Ada 20 GB als 2/16/2-VRAM-Job-Pool; CopyGuard 0 GB VRAM (RAM/NVMe, Phi-4-mini/Gemma-3 Q4); Postgres-WAL = dauerhafte Uhr; `(tenant_id, client_id, job_id)`-Isolation überall.
- **Governance:** Stop-Gates pro Phase; Wiedervorlage WV01–WV06 terminiert offene Fragen; X-Katalog „nicht still löschen, nicht bauen".

### 1.2 Frische Verifikation des Kanon-Zustands
| Prüfpunkt | Ergebnis |
|---|---|
| `src/lib/concept/decisions.ts`, `freigabe.ts`, `kozyrev-labor.ts`, `standalone.ts`, `wiedervorlage.ts`, `id-legend.ts`, `offen.ts`, `nav.ts` vorhanden und typisiert | ✅ |
| Rollenmodell, Abos, EEAT, WCAG 2.2 AA/BFSG als Pflicht dokumentiert | ✅ |
| `scripts/canon-contract.mjs` | ❌ **existiert nicht** — der freigegebene Bereinigungsplan (771 Zeilen, `docs/superpowers/plans/2026-08-24-…md`) ist **nicht ausgeführt** (alle Checkboxen offen) |
| Git-Historie | HEAD `a726346`; letzte Commits sind ausschließlich Doku/Plan („Plan Aurelia canon reconciliation", „Start Phase 1 shell") — **kein Funktionscode seit Phasenstart** |
| Neu aufgetaucht | `docs/project-control/external-analyses/` (Archivierung von V1/V2 durch den Entwickler — gutes Provenienz-Hygiene-Signal) |

---

## 2. Codebasis — Bestand und Qualität (frisch verifiziert)

### 2.1 Als akkurat befundene Bausteine
| Baustein | Nachweis | Urteil |
|---|---|---|
| Konzept-Kanon als Code | `src/lib/concept/*` | Exzellent — Governance ist maschinenlesbar |
| DB-Abstraktion | `src/lib/db.ts` (PGLite↔pg/Neon-Parität, `_migrations`-Tracking, OID-Normalisierung int8/date/interval) | Sehr gut; Preview verhält sich query-identisch zu Produktion |
| Auth-Middleware | `src/lib/auth/middleware.ts` (`assertSameSiteRequest` vor Datenzugriff, `requireUserId` fail-closed, Preview-Bearer-Brücke) | Akkurat gemäß Verfassungsregel „jede Query an verified userId" |
| Gate-Identity | `src/lib/auth/gate-identity.test.ts` — 15 Tests JWKS-Rotation/Fail-Closed | ✅ grün (verifiziert) |
| Phase-1-Schema | `migrations/0002_tenants.sql` (`tenants.data_class` default `synthetic`; `memberships` unique+Rollen) | Solide |
| Memberships-Serverfns | `src/lib/praxis/memberships.ts` (alles an `context.userId`, Zweitmandant gedeckelt) | Akkurat |
| Design-System | `src/styles.css` (Pergament/Tinte/Sage, Fraunces/Source Sans 3 selbst gehostet) | Akkurat, DSGVO-freundlich (kein CDN-Font) |

### 2.2 Verifizierte Defekte (live ausgeführt, 17:30 CEST)
| ID | Befund | Kommando/Ausgabe (Kern) | Wirkung |
|---|---|---|---|
| **DEF-01** | Test-Suite: 1/15 rot + Windows-Glob-Problem | `npm test` → `ERR_MODULE_NOT_FOUND: '@tanstack/react-start'` aus `client.server.ts`; `'scripts/**/*.test.mjs'` liefert 0 Tests unter Git-Bash | Qualitätswächser blind; Stop-Gates nicht automatisierbar |
| **DEF-02** | Typecheck rot | `npm run typecheck` → `TS5102 Option 'baseUrl' has been removed` + `TS2688 vite/client` | dto. |
| **DEF-03** | `check:auth` hängt am Dev-Server | ohne Server: exit 2 („could not read resolved VITE_AUTH_ENABLED") | Invariantenprüfung nicht CI-fähig |
| **DEF-04** | Kanonbereinigungsplan unausgeführt | `scripts/canon-contract.mjs` fehlt; Plan-Checkboxen offen | WebRTC-Resttexte aktiv; Kanon-Vertrag nicht einklagbar |

### 2.3 Soll-/Ist-Differenz der Substanzschichten
| Soll (Kanonquelle) | Ist | Δ |
|---|---|---|
| WebSocket-Fachkanal v:1 (C08, 18-clipboard) | nichts | 100 % offen |
| `aurelia-timerd` 50 ms/Checkpoint (D20, 21-timer) | nichts | 100 % offen |
| `aurelia-gpud` 16-GB-Pool + Stream-Isolation (C03, 17-cuda) | nichts | 100 % offen |
| `aurelia-emitterd` Lease-Protokoll (D14, 15-live) | nichts | 100 % offen |
| CopyGuard Lexikon + RAM-LLM (C02, 16-wellbeing) | nichts | 100 % offen |
| Kernel-Registry/ABI-Runtime (06-kernel-abi) | nur Konzepttypen | ~90 % offen |
| RLS + Envelope-Encryption (03-security) | keine RLS-Policies | 100 % offen (Phase 2) |
| AnalysisDraft/HarmonizationLane (D18) | nichts | offen |
| Computation Passport (04-compute) | nichts | offen |

**Lesart:** Das ist für „Phase 1 läuft" der **korrekte** Zustand — wichtig ist nur, ihn nicht mit Fortschritt zu verwechseln.
