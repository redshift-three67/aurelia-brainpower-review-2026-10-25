# RadiThoms Phase 3 — Dependency Security Hardening

Created: 2026-06-12T21:37:24+02:00
Repository: `/opt/radithoms`

## Ziel

Phase 3 behebt die produktiv relevanten npm-Audit-Funde kontrolliert und minimal, ohne ein riskantes Major-Upgrade der Build-Toolchain zu erzwingen.

Priorität:

1. Produktive High-Severity-Funde beseitigen.
2. `package-lock.json` konsistent halten.
3. Keine unnötigen Major-Upgrades oder fachlichen Codeänderungen in dieser Phase.
4. Real verifizieren: `npm ci`, Build, TypeScript, Lint, Audit.

## Ausgangslage vor Phase 3

`npm audit --omit=dev` meldete:

```text
11 vulnerabilities
4 moderate
7 high
```

Betroffene Bereiche:

- `@remix-run/router` / `react-router` / `react-router-dom` — high, XSS/Open-Redirect
- `postcss` — moderate, CSS stringify/XSS advisory
- `glob`, `minimatch`, `brace-expansion`, `picomatch`
- `lodash`
- `ws`
- `yaml`

## Durchgeführte Änderung

Ausgeführt:

```bash
npm audit fix
```

Wichtig:

- Kein `--force` verwendet.
- Kein bewusstes Major-Upgrade auf Vite 8 durchgeführt.
- `package.json` blieb unverändert.
- Die Sicherheitsupdates wurden innerhalb vorhandener semver-Ranges im Lockfile aufgelöst.

## Relevante aktualisierte Lockfile-Versionen

Nach `npm audit fix`:

```text
react-router-dom lock=6.30.4
react-router lock=6.30.4
@remix-run/router lock=1.23.3
postcss lock=8.5.15
vite lock=5.4.21
esbuild lock=0.21.5
glob lock=10.5.0
lodash lock=4.18.1
picomatch lock=2.3.2
ws lock=8.21.0
yaml lock=2.9.0
```

## Verifikation

Ausgeführt in `/opt/radithoms`:

```bash
npm ci
npm run build
npx tsc --noEmit
npm run lint
npm audit --omit=dev
npm audit
```

### Ergebnis

| Check | Ergebnis | Bemerkung |
|---|---:|---|
| `npm ci` | PASS | 478 Pakete installiert; Full-Audit meldet nur noch Dev-Toolchain-Funde. |
| `npm run build` | PASS | Vite 5.4.21, Build erfolgreich. |
| `npx tsc --noEmit` | PASS | Keine TypeScript-Ausgabe, Exit erfolgreich. |
| `npm run lint` | FAIL erwartet | Unverändert 76 Probleme: 51 errors, 25 warnings. |
| `npm audit --omit=dev` | PASS | `found 0 vulnerabilities`. |
| `npm audit` | FAIL erwartet | 2 moderate Dev-Vulnerabilities über Vite/esbuild; Fix erfordert `npm audit fix --force` auf Vite 8. |

## Wichtigster Fortschritt

Produktiver Audit-Status:

Vor Phase 3:

```text
npm audit --omit=dev: 11 vulnerabilities (4 moderate, 7 high)
```

Nach Phase 3:

```text
npm audit --omit=dev: found 0 vulnerabilities
```

Damit sind die produktiv relevanten npm-Audit-Funde in dieser Phase geschlossen.

## Bewusst nicht durchgeführt

Nicht ausgeführt:

```bash
npm audit fix --force
```

Grund:

`npm audit` meldet verbleibend:

```text
esbuild <=0.24.2
vite <=6.4.1
fix available via npm audit fix --force
Will install vite@8.0.16, which is a breaking change
```

Bewertung:

- Der verbleibende Fund betrifft die Dev-Toolchain (`vite`/`esbuild`) und den Entwicklungsserver.
- `npm audit --omit=dev` ist sauber.
- Ein forcierter Sprung von Vite 5 auf Vite 8 ist ein separates Major-Upgrade mit höherem Regressionsrisiko und sollte nicht ungetestet in die Security-Lockfile-Phase gemischt werden.

Empfehlung: Vite/esbuild als eigene Phase mit dedizierter Build-/Preview-/Browser-Verifikation planen.

## Weiterhin bekannte offene technische Themen

### Lint

Unverändert nach Phase 3:

```text
76 problems (51 errors, 25 warnings)
```

Verbleibende Regelklassen:

```text
51  @typescript-eslint/no-explicit-any
13  react-refresh/only-export-components
12  react-hooks/exhaustive-deps
```

Interpretation:

- `no-explicit-any` benötigt echte Domänentypen statt pauschaler Ersetzungen.
- `react-hooks/exhaustive-deps` darf nicht mechanisch gefixt werden, weil Audio-/Realtime-/Hardware-Flows betroffen sein können.
- `react-refresh/only-export-components` ist primär Entwicklungs-/HMR-Sauberkeit.

### Build-Warnungen

Weiterhin vorhanden:

```text
Browserslist/caniuse-lite ist veraltet
Some chunks are larger than 500 kB after minification
```

## Aktueller Git-Status nach Phase 3

```text
 M package-lock.json
 M src/components/CuspSurface3D.tsx
 M src/components/FrequencyOutputModule.tsx
 M src/components/TCMTrendAnalytics.tsx
 M src/components/anatomy/ModelUpload.tsx
 M src/components/ui/command.tsx
 M src/components/ui/textarea.tsx
 M src/hooks/useServerHardwareMetrics.ts
 M src/hooks/useTreatmentSequence.ts
 M src/index.css
 M src/services/hardware/HardwareDiscoveryService.ts
 M src/services/realtime/RealtimeHarmonizationService.ts
 M supabase/functions/hardware-metrics/index.ts
 M tailwind.config.ts
?? docs/analysis/
```

`package.json` wurde durch Phase 3 nicht verändert.

## Nächste priorisierte Empfehlung

Phase 4 sollte nicht mehr produktive npm-Audit-Funde behandeln, da diese jetzt geschlossen sind. Die nächsten sinnvollen Optionen sind:

1. Lokale App-Laufprüfung im Browser auf einem freien Port mit Console-/Runtime-Check.
2. Danach Commit/Push-Vorbereitung für Phase 1–3, falls gewünscht.
3. Separat: Vite/esbuild Major-Upgrade-Probe in isolierter Phase oder Branch.
4. Danach: gezielte Typisierungsphase für `@typescript-eslint/no-explicit-any`.

Empfohlener direkter nächster Schritt: lokale Browser-Smoke-Verifikation der App nach den Dependency-Updates, weil sie die Änderungen aus Phase 1–3 real zur Laufzeit absichert.
