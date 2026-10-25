# 05 Verifikation, Tests, Build, Tool-Ausgaben

## Repository-Clone und Token-Sicherheit

Ausgeführt:

```bash
git -c "http.https://github.com/.extraheader=$AUTH_HEADER" \
  clone https://github.com/radiquant/morpho-field-nexus.git /opt/radithoms
```

Ergebnis:

```text
Cloning into '/opt/radithoms'...
remote-url: https://github.com/radiquant/morpho-field-nexus.git
branch-status:
## main...origin/main
head: 64b9a38
OK: remote URL contains no token/credential
```

Hinweis:

- `/opt/radithoms` war initial `root:root`; ich habe per passwordless sudo die Ownership auf `klaus999:klaus999` gesetzt, damit der Clone in den vom Nutzer gewünschten Ordner möglich ist.
- Der GitHub Token wurde nicht in `origin` persistiert.

## Git-Zustand

Ausgeführt:

```bash
git status --short --branch
git log --oneline -5
git remote -v
```

Ergebnis:

```text
## main...origin/main
64b9a38 Synchronize GitHub repo
79e3842 Work in progress
5587d7d Dokumentation & Export erstellt
ddc00ff Dokumentation erstellt
cd47e57 Erstellte Projektdokumentation
origin https://github.com/radiquant/morpho-field-nexus.git (fetch)
origin https://github.com/radiquant/morpho-field-nexus.git (push)
```

Nach Install/Build blieb der Working Tree vor Berichtserstellung sauber. Die Berichtserstellung erzeugt neue Markdown-Dateien unter `docs/analysis/deep-audit-2026-06-04/`.

## System-/Tool-Versionen

Ausgeführt:

```bash
node --version
npm --version
git --version
gh --version
```

Ergebnis:

```text
node v20.20.0
npm 10.8.2
git version 2.39.5
gh version 2.87.3
```

## Codebase-Metrik

Ausgeführt:

```bash
pygount --format=summary \
  --folders-to-skip='.git,node_modules,dist,build,.cache,coverage' .
```

Ergebnis zusammengefasst:

```text
TSX           101 files  15425 code
TypeScript     67 files  12150 code
JSON            6 files   5289 code
Transact-SQL   19 files    633 code
CSS+Lasso       2 files    248 code
JavaScript      2 files     22 code
Markdown       12 files   2651 comment
Sum            221 files 33796 code 4685 comment
```

## Installation

### `npm ci`

Ausgeführt:

```bash
npm ci
```

Ergebnis: fehlgeschlagen, Exit Code 1.

Fehlerauszug:

```text
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync.
npm error Missing: tus-js-client@4.3.1 from lock file
npm error Missing: buffer-from@1.1.2 from lock file
npm error Missing: combine-errors@3.0.3 from lock file
...
```

Bewertung:

- `package.json` und `package-lock.json` sind nicht synchron.
- CI/CD mit `npm ci` ist aktuell gebrochen.
- Ursache ist wahrscheinlich hinzugefügte Dependency `tus-js-client` ohne aktualisierten npm Lockfile.

### `npm install --no-package-lock`

Ausgeführt, um ohne Lockfile-Änderung lokal testen zu können:

```bash
npm install --no-package-lock
```

Ergebnis: erfolgreich, Exit Code 0.

Auszug:

```text
added 458 packages, and audited 459 packages in 21s
2 moderate severity vulnerabilities
```

Hinweis:

- Diese Installation wurde nur für lokale Verifikation genutzt.
- `package-lock.json` wurde dabei nicht verändert.

## Build

Ausgeführt:

```bash
npm run build
```

Ergebnis: erfolgreich, Exit Code 0.

Auszug:

```text
vite v5.4.21 building for production...
[plugin generate-who-meridian-exports] Generated WHO meridian exports: public/exports/who-meridian-points.json and public/exports/who-meridian-points.csv (296 points)
✓ 3694 modules transformed.
dist/index.html                     1.13 kB │ gzip:   0.48 kB
dist/assets/index-O2R7VM1Q.css     88.95 kB │ gzip:  15.26 kB
dist/assets/index-D6qWOvty.js   3,019.11 kB │ gzip: 844.62 kB
✓ built in 5.74s
```

Warnungen:

```text
Unexpected "@keyframes"
.dark @keyframes chreode-pulse
Unexpected "0%"
Unexpected "50%"
Some chunks are larger than 500 kB after minification.
```

Bewertung:

- Produktivbuild funktioniert.
- CSS-Syntaxproblem sollte behoben werden.
- Hauptbundle ist groß; Code Splitting empfohlen.

## TypeScript

Ausgeführt:

```bash
npx tsc --noEmit
```

Ergebnis: erfolgreich, Exit Code 0, keine Ausgabe.

Bewertung:

- TypeScript-Kompilation ist grün.
- Das ist ein sehr wichtiger Positivbefund, trotz Lint-Problemen.

## ESLint

Ausgeführt:

```bash
npm run lint
```

Ergebnis: fehlgeschlagen, Exit Code 1.

Zusammenfassung:

```text
✖ 95 problems (71 errors, 24 warnings)
```

Häufige Fehlerklassen:

- `@typescript-eslint/no-explicit-any`
- `no-empty`
- `no-case-declarations`
- `@typescript-eslint/no-empty-object-type`
- `@typescript-eslint/no-require-imports`
- `@typescript-eslint/triple-slash-reference`
- React Hook Dependency Warnings
- React Refresh only-export-components Warnings

Beispiele:

```text
src/components/CuspSurface3D.tsx
  71:9  error  Unexpected lexical declaration in case block  no-case-declarations

src/components/FrequencyOutputModule.tsx
  418:51  error  Empty block statement  no-empty

src/components/SessionReportGenerator.tsx
  68:64  error  Unexpected any. Specify a different type

src/hooks/useServerHardwareMetrics.ts
  125:15  error  Unexpected lexical declaration in case block

supabase/functions/realtime-sync/index.ts
  41:68  error  Unexpected any. Specify a different type
```

Bewertung:

- Lint-Gate ist rot.
- Viele Fehler sind technisch leicht lösbar, aber einige Hook-Warnings können echte Realtime-/State-Bugs verursachen.
- Für Produktiv-/CI-Reife muss Lint grün werden oder bewusst in Baseline/Severity-Klassen getrennt werden.

## Dependency Audit

Ausgeführt:

```bash
npm audit --omit=dev --json
```

Ergebnis: Exit Code 1, produktive Vulnerabilities vorhanden.

Metadaten:

```json
"vulnerabilities": {
  "moderate": 4,
  "high": 7,
  "critical": 0,
  "total": 11
}
```

Wichtige Treffer:

| Paket | Severity | Thema |
|---|---|---|
| `react-router-dom` / `react-router` / `@remix-run/router` | high/moderate | XSS/Open Redirect Klassen. |
| `postcss` | moderate | XSS via CSS Stringify. |
| `lodash` | high/moderate | Code Injection / Prototype Pollution advisories. |
| `glob` | high | Command Injection advisory. |
| `minimatch` | high | ReDoS advisories. |
| `picomatch` | high/moderate | ReDoS / method injection. |
| `ws` | moderate | Uninitialized memory disclosure. |
| `yaml` | moderate | Stack overflow nested YAML. |

Bewertung:

- Für ein Gesundheits-/Klientendatenprojekt ist das nicht akzeptabel.
- Updates müssen kontrolliert durchgeführt und anschließend Build/Lint/Browser getestet werden.

## Browser Smoke Test

### Dev Server

Ausgeführt:

```bash
npm run dev -- --host 127.0.0.1 --port 5174 --strictPort
curl -I http://127.0.0.1:5174
```

Ergebnis:

```text
HTTP/1.1 200 OK
Vary: Origin
Content-Type: text/html
Cache-Control: no-cache
```

### `/`

Browser-Navigation:

```text
http://127.0.0.1:5174/
```

Ergebnis:

- Landingpage rendert.
- Sichtbare Überschrift: `Feld Engine`.
- Browser Console: 0 messages, 0 JS errors im initialen Snapshot.

### `/analyse`

Browser-Navigation:

```text
http://127.0.0.1:5174/analyse
```

Ergebnis:

- Redirect auf `http://127.0.0.1:5174/login`.
- Login UI sichtbar:
  - `Feldengine`
  - `Zugang zur Therapie-Plattform`
  - Tabs `Anmelden`, `Registrieren`
  - Felder `E-Mail`, `Passwort`
- Browser Console: 0 messages, 0 JS errors im initialen Snapshot.

Bewertung:

- Basic UX funktioniert unauthentifiziert.
- Authentifizierte Workflows wurden mangels Testaccount nicht Ende-zu-Ende geprüft.

## Supabase-/Realtime-Live-Tests

Nicht durchgeführt:

- Kein Login-Test mit echtem Supabase User.
- Keine Live-Datenbankmutation.
- Kein Edge Function Live Call mit echten Patientendaten.
- Kein WebSocket-Multi-Client-Test.
- Kein Hardware-in-the-loop-Test.

Grund:

- Auftrag war Tiefenanalyse ohne Code-/Datenänderungen.
- Patientendaten-/Realtime-/KI-Flows sollten ohne explizite Freigabe und Datenschutzklärung nicht mit Echtdaten getestet werden.

## Dokumentationsdrift

Beobachtung:

- README ist weiterhin Lovable-Template mit `REPLACE_WITH_PROJECT_ID`.
- Docs beschreiben teils vollständige Realtime-/Hardware-/GPU-Architektur.
- Code implementiert viele Konzepte, aber mehrere Hardware-/GPU-Metriken sind Simulationen.
- Build/TypeScript sind besser als Lint/CI-Zustand.

Bewertung:

- Dokumentation ist umfangreich, aber nicht klar genug zwischen geplant, simuliert, prototypisch und produktionsreif getrennt.

## Verifikationsfazit

| Check | Ergebnis |
|---|---|
| Clone | Grün |
| Token nicht persistiert | Grün |
| npm ci | Rot |
| npm install --no-package-lock | Grün |
| Build | Grün mit Warnungen |
| TypeScript | Grün |
| Lint | Rot |
| npm audit prod | Rot |
| Browser `/` | Grün |
| Browser `/analyse` unauth redirect | Grün |
| Authenticated E2E | Nicht getestet |
| Hardware E2E | Nicht getestet |
| Supabase Edge Auth | Konfiguration Rot |
