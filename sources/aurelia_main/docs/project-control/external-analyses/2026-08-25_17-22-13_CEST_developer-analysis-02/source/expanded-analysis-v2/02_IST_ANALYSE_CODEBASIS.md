# 02 — Ist-Analyse Codebasis (2026-08-25)

---

## 1. Was akkurat umgesetzt ist (mit Nachweis)

| Bereich | Nachweis (Datei) | Beurteilung |
|---|---|---|
| Entscheidungs-Kanon als ausführbarer Code | `src/lib/concept/decisions.ts` (D01–D24 mit Status `gesetzt`/`empfohlen`) | Exzellent. Der Kanon ist nicht nur Text, sondern typisiert und UI-gerendert — Widersprüche werden sichtbar. |
| Freigabe-/Ausschlussmatrix | `src/lib/concept/freigabe.ts` (C01–C12 gesetzt, X01–X20 akzeptiert, U01–U12) | Akkurat. X-Einträge sind bewusst *nicht implementiert und nicht gelöscht* — genau der verlangte Zustand. |
| Kozyrev-Katalog mit Sperren | `src/lib/concept/kozyrev-labor.ts` (K1–K5 schaltbar, K6–K8 ohne ID/Flag) | Akkurat und regulatorisch klug. |
| ID-Legende | `src/lib/concept/id-legend.ts` (D ≠ docs/NN — definiert das Namenssystem) | Akkurat; verhindert die klassische Verwechslung von Entscheidungs-IDs und Kapitelnummern. |
| Wiedervorlage-System | `src/lib/concept/wiedervorlage.ts` (WV01–WV06 an Phasen gebunden) | Akkurat. Offene Fragen gehen nicht verloren, sondern sind terminiert. |
| Datenbank-Abstraktion | `src/lib/db.ts`: PGLite (Preview) vs. pg/Neon (produktiv), identische `Sql`-Oberfläche, Migrations-Tracking in `_migrations`, Typnormalisierung (int8/date/interval) | Sehr gut durchdacht; Preview- und Produktionsverhalten sind query-identisch. |
| Auth-Middleware | `src/lib/auth/middleware.ts`: `assertSameSiteRequest()` vor Datenzugriff, `requireUserId()` fail-closed, Bearer-Token-Brücke nur für Preview | Akkurat gemäß Regel „jede Query scoped by verified userId". |
| Tenant-Schema Phase 1 | `migrations/0002_tenants.sql`: `tenants` (data_class default `synthetic`), `memberships` (unique user+tenant, Rollen) | Solide Basis; `data_class='synthetic'` ist als Default korrekt verankert. |
| Membership-Serverfunktionen | `src/lib/praxis/memberships.ts`: alle Queries an `context.userId` gebunden, zweiter Mandant gedeckelt (Isolationstest-Vorbereitung) | Akkurat; Abfrage-Scope stimmt mit Regel 8 der Verfassung überein. |
| Design-Tokens | `src/styles.css` + `docs/08-ui-a11y.md`: Pergament/Tinte/Sage, Fraunces + Source Sans 3, selbst gehostet | Akkurat umgesetzt; keine Fremd-CDN-Abhängigkeit (DSGVO-relevant). |
| Gate-Identity-Tests | `src/lib/auth/gate-identity.test.ts`: 15 Tests, JWKS-Rotation, Fail-Closed ohne Env | Verifiziert grün (einziger grüner Testblock). |

---

## 2. Verifizierte Defekte (diese Session ausgeführt)

### DEF-01: `npm test` rot — Modulauflösung
```
Error [ERR_MODULE_NOT_FOUND]: Cannot find package '@tanstack/react-start'
  from src/lib/app-data/client.server.ts
```
- **Ursache:** Node-Test-Runner (ohne Vite-Resolver) kann `@tanstack/react-start` aus `client.server.ts` im Pure-Node-Kontext nicht auflösen; zudem scheitert `'scripts/**/*.test.mjs'` unter Git-Bash/Windows am Globbing (0 Tests).
- **Wirkung:** Der zentrale Qualitätswächser ist blind. Alle Stop-Gates stehen auf Sand.
- **Fix-Richtung:** Tests auf `vitest` (oder `tsx --test`) migrieren; Server-Only-Module in Tests mocken; Glob portabel schreiben (`node --test scripts/` mit Explorer oder `find`-Liste).

### DEF-02: `npm run typecheck` rot — tsconfig-Inkompatibilität
```
error TS2688: Cannot find type definition file for 'vite/client'
tsconfig.json(24,5): error TS5102: Option 'baseUrl' has been removed
```
- **Ursache:** Installiertes TypeScript (5.7+ in `package.json`, effektiv neuer) akzeptiert `baseUrl` nicht mehr und findet `vite/client` nicht (node_modules unvollständig oder Typescript-Version vor Node-Modul-Auflösung).
- **Fix-Richtung:** `tsconfig.json` modernisieren (`paths` ohne `baseUrl`, `"types": ["vite/client"]` prüfen oder `vite-env.d.ts` referenzieren); ggf. `npm install` frisch ausführen.

### DEF-03: `npm run check:auth` — harte Abhängigkeit vom Dev-Server
```
[auth-invariant] could not read the dev server's resolved VITE_AUTH_ENABLED  (exit 2)
```
- **Ursache:** Das Skript fragt den laufenden Dev-Server ab; ohne Server kein Urteil.
- **Fix-Richtung:** Skript statisch gegen `.grok/app-env.json` / Build-Artefakte prüfen lassen oder explizit „Server nicht erreichbar → SKIP (nicht FAIL)" unterscheiden.

### DEF-04: Kanonbereinigungs-Plan noch nicht ausgeführt
- Der freigegebene Plan (`docs/superpowers/plans/2026-08-24-aurelia-kanonbereinigung.md`, 771 Zeilen, Task 1–8) existiert vollständig, ist aber laut Plan-Checkboxen noch nicht abgearbeitet; `scripts/canon-contract.mjs` existiert noch nicht im Repo (verifiziert: nicht in `scripts/` vorhanden).
- **Wirkung:** Rest-WebRTC-Formulierungen in Docs/UI sind noch aktiv; der Kanon-Vertrag ist noch nicht einklagbar.

---

## 3. Noch nicht vorhandene Schichten (Soll aus Kanon, Ist aus Code)

| Soll (Quelle) | Ist-Zustand Code | Differenz |
|---|---|---|
| WebSocket-Fachkanal v:1 (C08, D05, 18-clipboard) | nichts | komplett offen |
| `aurelia-timerd` 50 ms/Checkpoints (D20, 21-timer) | nichts | komplett offen |
| `aurelia-gpud` 16-GB-Pool + Stream-Isolation (C03, D17, 17-cuda) | nichts | komplett offen |
| `aurelia-emitterd` Lease→Arming→ACK (D14, 15-live) | nichts | komplett offen |
| CopyGuard Lexikon + RAM-LLM (C02, D13, 16-wellbeing) | nichts | komplett offen |
| Kernel-ABI-Registry + Hash-Validierung (06-kernel-abi) | nur Konzept-Typen | Registry/Runtime offen |
| RLS + Envelope-Encryption Art. 9 (03-security) | keine RLS-Policies in Migrationen | offen (Phase 2) |
| AnalysisDraft/HarmonizationLane (D18, 18-clipboard) | nichts | offen (Phase 2/5) |
| Computation Passport (04-compute) | nichts | offen (Phase 4) |

**Fazit Codebasis:** Das Gerüst ist qualitativ hochwertig, trägt aber erst ~25 % der verfassungsgeforderten Substanz. Das ist für „Phase 1 läuft" korrekt — es darf nur nicht mit „das System ist fast fertig" verwechselt werden.
