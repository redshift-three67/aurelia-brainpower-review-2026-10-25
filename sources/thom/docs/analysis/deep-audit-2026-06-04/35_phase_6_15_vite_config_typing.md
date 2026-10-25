# Phase 6 Teil 15 — Vite Config Typ-Stabilisierung

Datum: 2026-06-14
Projekt: `/opt/radithoms`
Datei: `vite.config.ts`

## Ziel

Fortsetzung von Phase 6: Abbau der letzten beiden `@typescript-eslint/no-explicit-any` Errors vor dem späteren Fast-Refresh-Warning-Sweep.

Priorisierter Kandidat war `vite.config.ts`, weil dort die verbleibenden globalen ESLint-Errors lagen und die Datei Build-/Dev-Server-Pluginlogik für die WHO-Meridian-Exports enthält.

## Startzustand

Arbeitsverzeichnis und Zeitpunkt:

```text
/opt/radithoms
2026-06-14T12:28:14+02:00
```

Ziel-Datei war vor Phase 6 Teil 15 nicht modified:

```text
git status --short -- vite.config.ts
# keine Ausgabe
```

Ziel-Diff vor Phase 6 Teil 15:

```text
git diff -- vite.config.ts
# keine Ausgabe
```

Gezielte ESLint-Prüfung vor der Änderung:

```text
/opt/radithoms/vite.config.ts
  23:54  error  Unexpected any. Specify a different type  @typescript-eslint/no-explicit-any
  45:16  error  Unexpected any. Specify a different type  @typescript-eslint/no-explicit-any

✖ 2 problems (2 errors, 0 warnings)
```

Gesamt-Lint-Baseline vor Phase 6 Teil 15 laut letzter verifizierter Prüfung:

```text
15 problems (2 errors, 13 warnings)
```

## Root Cause

Die beiden `any`-Stellen lagen an der dynamischen Build-/Import-Grenze des Vite-Plugins:

```ts
async function loadPointsFromTypescript(): Promise<any[]> {
  // ... esbuild bundle ...
  const mod: any = await import(dataUrl);
  return mod.COMPLETE_ACUPUNCTURE_DATABASE;
}
```

Der Code bündelt `src/utils/meridianPoints/index.ts` mit esbuild und importiert das Ergebnis via `data:` URL. Die fachliche Export-Struktur ist aber bereits im Projekt typisiert: `COMPLETE_ACUPUNCTURE_DATABASE` besteht aus `AcupuncturePoint[]` aus `src/utils/meridianPointsDatabase.ts`.

## Umsetzung

Minimaler Typ-Fix ohne Änderung an Build-, Dev-Server-, Plugin-, CSV-, JSON- oder Exportlogik:

```ts
import type { AcupuncturePoint } from "./src/utils/meridianPointsDatabase";

type MeridianPointsModule = {
  COMPLETE_ACUPUNCTURE_DATABASE: AcupuncturePoint[];
};
```

Anschließend wurde die Loader-Signatur und der dynamische Import typisiert:

```ts
async function loadPointsFromTypescript(): Promise<AcupuncturePoint[]> {
  // ...
  const mod = (await import(dataUrl)) as MeridianPointsModule;
  return mod.COMPLETE_ACUPUNCTURE_DATABASE;
}
```

## Geändertes Verhalten

Beabsichtigt keine fachliche Runtime-Änderung.

Unverändert bleiben:

- esbuild-Bundling von `src/utils/meridianPoints/index.ts`.
- dynamischer Import via `data:text/javascript;base64,...`.
- JSON-Export nach `public/exports/who-meridian-points.json`.
- CSV-Export nach `public/exports/who-meridian-points.csv`.
- Dev-/Preview-Erzeugung über `configureServer`.
- Production-Build-Erzeugung über `buildStart`.
- Non-fatal Warnverhalten bei Export-Generierungsfehlern.
- Keine neuen Logs, Uploads, E-Mails oder Persistenzpfade für Patienten-/Anamnesedaten.

## Verifikation

### Ziel-ESLint

```bash
npx eslint vite.config.ts
```

Ergebnis:

```text
PASS, exit_code 0
```

### TypeScript

```bash
npx tsc --noEmit
```

Ergebnis:

```text
PASS, exit_code 0
```

### Production Build

```bash
npm run build
```

Ergebnis:

```text
vite v5.4.21 building for production...
[plugin generate-who-meridian-exports] Generated WHO meridian exports: public/exports/who-meridian-points.json and public/exports/who-meridian-points.csv (296 points)
✓ 3674 modules transformed.
dist/index.html                     1.13 kB │ gzip:   0.48 kB
dist/assets/index-Cd_dPJH4.css     89.15 kB │ gzip:  15.24 kB
dist/assets/index-BVH35FDS.js   2,962.35 kB │ gzip: 829.13 kB
✓ built in 5.56s
```

Bekannte, unveränderte Build-Hinweise:

```text
Browserslist data is 12 months old
Some chunks are larger than 500 kB after minification
```

### Gesamt-Lint nach Phase 6 Teil 15

```bash
npm run lint || true
```

Ergebnis:

```text
✖ 13 problems (0 errors, 13 warnings)
```

Verbleibende Warnungen:

```text
src/components/anatomy/ChakraVisualization.tsx      1 warning
src/components/anatomy/DysregulationLegend.tsx      3 warnings
src/components/anatomy/GLBModelLoader.tsx           2 warnings
src/components/ui/badge.tsx                         1 warning
src/components/ui/button.tsx                        1 warning
src/components/ui/form.tsx                          1 warning
src/components/ui/navigation-menu.tsx               1 warning
src/components/ui/sidebar.tsx                       1 warning
src/components/ui/sonner.tsx                        1 warning
src/components/ui/toggle.tsx                        1 warning
```

Vergleich zu Phase 6 Teil 14:

```text
Vorher: 15 problems (2 errors, 13 warnings)
Nachher: 13 problems (0 errors, 13 warnings)
Verbesserung: -2 errors, 0 neue warnings/errors
```

## Browser-/Runtime-Smoke

Portprüfung vor Start:

```text
port 5173: FREE
port 5174: FREE
port 5175: FREE
port 4173: FREE
```

Dev Server:

```bash
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

Server-Output:

```text
VITE v5.4.21 ready in 170 ms
Local: http://127.0.0.1:5173/
Generated WHO meridian exports: public/exports/who-meridian-points.json and public/exports/who-meridian-points.csv (296 points)
```

HTTP-Smoke:

```text
HTTP/1.1 200 OK
Content-Type: text/html
```

Browser-Smoke:

```text
URL-Aufruf: http://127.0.0.1:5173/login
Login-/Auth-Seite sichtbar: Feldengine, Tabs Anmelden/Registrieren, Felder E-Mail/Passwort
JS errors: []
total_errors: 0
```

Console-Hinweise im Dev-Modus:

```text
[vite] connecting...
[vite] connected.
Download the React DevTools for a better development experience
React Router Future Flag Warning: v7_startTransition
React Router Future Flag Warning: v7_relativeSplatPath
```

Diese Hinweise sind keine JS-Fehler; `total_errors` war 0.

Dev-Server wurde kontrolliert beendet:

```text
process status: exited
exit_code: -15
```

## Ergebnis

Phase 6 Teil 15 ist abgeschlossen.

- `vite.config.ts`: gezielter ESLint sauber.
- 2 `no-explicit-any` Errors entfernt.
- TypeScript sauber.
- Production Build sauber.
- Gesamt-Lint von 15 auf 13 Probleme verbessert.
- Gesamt-Lint hat jetzt 0 errors und 13 bekannte Fast-Refresh-Warnings.
- Browser-/Login-Smoke ohne Console-/JS-Fehler.

## Nächster empfohlener Schritt

Weiter mit Phase 6 Teil 16:

1. Fast-Refresh-Warnings systematisch klassifizieren.
2. Zuerst prüfen, ob einzelne Dateien Constants/Helper aus Component-Dateien exportieren.
3. Minimal und phasengegated vorgehen, um keine UI-/Routing-/Shadcn-Verträge zu verändern.
