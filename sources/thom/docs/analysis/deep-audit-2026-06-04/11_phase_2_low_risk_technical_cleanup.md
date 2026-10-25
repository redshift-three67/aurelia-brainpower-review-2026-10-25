# RadiThoms Phase 2 — Low-Risk Technical Cleanup

Created: 2026-06-08T23:50:15+02:00
Repository: `/opt/radithoms`
Branch state before commit: `main...origin/main` with local modifications

## Ziel

Phase 2 behebt bewusst nur kleine, risikoarme technische Befunde ohne fachliche Architektur-, Security- oder Echtzeitlogik umzubauen.

Priorität:

1. CSS-Build-Warnung `.dark @keyframes chreode-pulse` beseitigen.
2. Eindeutige ESLint-Fehlerklassen beheben, die keine Domänenentscheidung erfordern.
3. `npm ci`, Build, TypeScript, Lint und Audit erneut real verifizieren.

## Geänderte Bereiche

### CSS / Build-Warnung

Datei:

- `src/index.css`

Änderung:

- Ungültige CSS-Syntax `.dark @keyframes chreode-pulse` entfernt.
- `chreode-pulse` nutzt jetzt `hsl(var(--chreode) / ...)`, sodass Hell-/Dunkelmodus über bestehende Theme-CSS-Variablen statt über ungültig verschachtelte Keyframes abgebildet wird.

Ergebnis:

- Die bisherige Vite/CSS-Warnung zu `.dark @keyframes chreode-pulse` tritt im Build nicht mehr auf.

### ESLint: no-case-declarations

Dateien:

- `src/components/CuspSurface3D.tsx`
- `src/hooks/useServerHardwareMetrics.ts`
- `supabase/functions/hardware-metrics/index.ts`

Änderung:

- `case`-Blöcke mit lexikalischen Deklarationen wurden in `{ ... }` gekapselt.
- Keine fachliche Logik geändert.

### ESLint: no-empty

Dateien:

- `src/components/FrequencyOutputModule.tsx`
- `src/hooks/useTreatmentSequence.ts`
- `src/services/realtime/RealtimeHarmonizationService.ts`

Änderung:

- Leere `catch {}`-Blöcke wurden durch `catch (error) { void error; }` ersetzt.
- Die bisherige Absicht „Fehler beim Stoppen/Disconnect bewusst ignorieren“ bleibt erhalten.
- Keine fachliche Audio-/Realtime-Logik geändert.

### ESLint: prefer-const

Datei:

- `src/components/TCMTrendAnalytics.tsx`

Änderung:

- `let elementScores` zu `const elementScores`, da nur Objektfelder mutiert werden, nicht die Binding-Referenz.

### ESLint: no-async-promise-executor

Datei:

- `src/components/anatomy/ModelUpload.tsx`

Änderung:

- `new Promise(async (...))` durch nicht-async Promise-Executor plus innere async IIFE ersetzt.
- TUS Upload-Flow, Session-Check, Resume-Logik und Progress-Callbacks bleiben erhalten.

### ESLint: triple-slash-reference

Datei:

- `src/services/hardware/HardwareDiscoveryService.ts`

Änderung:

- Triple-slash Reference auf `src/types/webapis.d.ts` entfernt.
- Die Typdatei liegt weiterhin unter `src/` und ist durch `tsconfig.app.json` (`include: ["src"]`) im Projekt enthalten.

### ESLint: no-require-imports

Datei:

- `tailwind.config.ts`

Änderung:

- `require("tailwindcss-animate")` durch ESM-Import `import tailwindcssAnimate from "tailwindcss-animate"` ersetzt.

### ESLint: no-empty-object-type

Dateien:

- `src/components/ui/command.tsx`
- `src/components/ui/textarea.tsx`

Änderung:

- Leere Interface-Erweiterungen wurden in Type-Aliases überführt.

## Verifikation

Ausgeführt in `/opt/radithoms`:

```bash
npm ci
npm run build
npx tsc --noEmit
npm run lint
npm audit --omit=dev
```

### Ergebnis

| Check | Ergebnis | Bemerkung |
|---|---:|---|
| `npm ci` | PASS | Installiert 478 Pakete; npm meldet weiterhin Audit-Funde inkl. Dev-Abhängigkeiten. |
| `npm run build` | PASS | Build erfolgreich; CSS-Keyframes-Warnung behoben. |
| `npx tsc --noEmit` | PASS | Keine TypeScript-Ausgabe, Exit erfolgreich. |
| `npm run lint` | FAIL erwartet | Reduziert von 96 Problemen auf 76 Probleme. |
| `npm audit --omit=dev` | FAIL erwartet | Weiterhin 11 produktive Vulnerabilities: 7 high, 4 moderate. |

### Lint-Entwicklung

Vor Phase 2 bzw. nach Phase 1:

```text
96 problems: 71 errors, 25 warnings
```

Nach Phase 2:

```text
76 problems: 51 errors, 25 warnings
```

Damit wurden in Phase 2 insgesamt 20 ESLint-Fehler behoben, ohne die fachliche Modularchitektur zu verändern.

Verbleibende Lint-Regeln:

```text
51  @typescript-eslint/no-explicit-any
13  react-refresh/only-export-components
12  react-hooks/exhaustive-deps
```

Interpretation:

- `@typescript-eslint/no-explicit-any`: fachlich/typologisch zu prüfen; nicht pauschal ersetzen, um keine Scheinsicherheit einzubauen.
- `react-hooks/exhaustive-deps`: benötigt Komponentenverständnis, da naive Dependency-Ergänzungen Realtime-/Audio-/Hardware-Flows verändern können.
- `react-refresh/only-export-components`: Entwicklungs-/HMR-Thema; meist durch Auslagerung von Konstanten/Helpern lösbar, aber nicht produktionskritisch.

### Build-Warnungen nach Phase 2

Behoben:

```text
.dark @keyframes chreode-pulse
Unexpected "0%"
Unexpected "50%"
```

Weiterhin vorhanden:

```text
Browserslist: browsers data (caniuse-lite) is 12 months old.
Some chunks are larger than 500 kB after minification.
```

## Security-/Audit-Status nach Phase 2

`npm audit --omit=dev` meldet weiterhin:

```text
11 vulnerabilities (4 moderate, 7 high)
```

Betroffene Pakete laut Audit:

- `@remix-run/router` / `react-router` / `react-router-dom` — high, XSS/Open Redirect advisory
- `brace-expansion` — moderate
- `glob` — high
- `lodash` — high
- `minimatch` — high
- `picomatch` — high
- `postcss` — moderate
- `ws` — moderate
- `yaml` — moderate

Empfehlung: Phase 3 als separate Dependency-Security-Phase durchführen, nicht mit Phase-2-Code-Cleanup vermischen.

## Aktueller Git-Status nach Phase 2

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

## Nächste priorisierte Empfehlung

Phase 3: Dependency-Security-Update kontrolliert durchführen.

Vorgeschlagene Reihenfolge:

1. `npm audit fix --package-lock-only` oder gezielte Paketupdates in einer Testkopie prüfen.
2. React Router Update zuerst isolieren, weil produktive XSS/Open-Redirect-Relevanz.
3. PostCSS separat prüfen, da Build-Pipeline betroffen ist.
4. Danach erneut: `npm ci`, `npm run build`, `npx tsc --noEmit`, `npm run lint`, `npm audit --omit=dev`.
5. Erst nach erfolgreicher Phase erneut ShadowCopy erstellen.
