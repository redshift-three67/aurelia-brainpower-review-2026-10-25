# Phase 6 Teil 16 — Fast-Refresh-Warnings Stabilisierung

Datum: 2026-06-14
Projekt: `/opt/radithoms`
Ziel: verbleibende `react-refresh/only-export-components` Warnings nach Abschluss aller `no-explicit-any` Errors beseitigen.

## Ziel

Nach Phase 6 Teil 15 war der globale ESLint-Zustand:

```text
13 problems (0 errors, 13 warnings)
```

Die 13 verbleibenden Warnings waren ausschließlich Fast-Refresh-Warnings. Phase 6 Teil 16 sollte diese ohne fachliche Runtime-Änderung, ohne neue Patientendaten-Flows und ohne Build-/Routing-Vertragsänderungen beheben.

## Startzustand

Arbeitsverzeichnis und Zeitpunkt:

```text
/opt/radithoms
2026-06-14T12:43:30+02:00
```

Globaler Lint vor der Änderung:

```text
/opt/radithoms/src/components/anatomy/ChakraVisualization.tsx
  23:14  warning  Fast refresh only works when a file only exports components

/opt/radithoms/src/components/anatomy/DysregulationLegend.tsx
  14:14  warning  Fast refresh only works when a file only exports components
  22:17  warning  Fast refresh only works when a file only exports components
  30:17  warning  Fast refresh only works when a file only exports components

/opt/radithoms/src/components/anatomy/GLBModelLoader.tsx
   41:14  warning  Fast refresh only works when a file only exports components
  180:17  warning  Fast refresh only works when a file only exports components

/opt/radithoms/src/components/ui/badge.tsx
  29:17  warning  Fast refresh only works when a file only exports components

/opt/radithoms/src/components/ui/button.tsx
  53:18  warning  Fast refresh only works when a file only exports components

/opt/radithoms/src/components/ui/form.tsx
  129:10  warning  Fast refresh only works when a file only exports components

/opt/radithoms/src/components/ui/navigation-menu.tsx
  111:3  warning  Fast refresh only works when a file only exports components

/opt/radithoms/src/components/ui/sidebar.tsx
  636:3  warning  Fast refresh only works when a file only exports components

/opt/radithoms/src/components/ui/sonner.tsx
  27:19  warning  Fast refresh only works when a file only exports components

/opt/radithoms/src/components/ui/toggle.tsx
  37:18  warning  Fast refresh only works when a file only exports components

✖ 13 problems (0 errors, 13 warnings)
```

## Root Cause

Die betroffenen `.tsx`-Dateien exportierten neben React-Komponenten auch Konstanten, Helper-Funktionen, Variant-Factories oder Hooks. Das ist für `react-refresh/only-export-components` ungünstig, weil Fast Refresh Dateien bevorzugt, die ausschließlich Komponenten exportieren.

Klassifikation:

- Anatomy-Komponenten:
  - `ChakraVisualization.tsx`: exportierte `CHAKRAS` neben Komponente.
  - `DysregulationLegend.tsx`: exportierte `DYSREGULATION_LEVELS`, `getDysregulationColor`, `getDysregulationLevel` neben Komponente.
  - `GLBModelLoader.tsx`: exportierte `AVAILABLE_MODELS`, `preloadModels` neben Komponente.
- Shadcn/UI-Komponenten:
  - `button.tsx` und `toggle.tsx`: exportierten `*Variants` neben Komponenten, externe UI-Dateien nutzen diese Variant-Factories.
  - `badge.tsx`: exportierte `badgeVariants`, obwohl im Code kein externer Import gefunden wurde.
  - `form.tsx`: exportierte `useFormField`, obwohl im Code kein externer Import gefunden wurde.
  - `navigation-menu.tsx`: exportierte `navigationMenuTriggerStyle`, ohne externen Import.
  - `sidebar.tsx`: exportierte `useSidebar`, ohne externen Import.
  - `sonner.tsx`: re-exportierte `toast`, obwohl Projektcode `toast` direkt aus `sonner` importiert.

## Umsetzung

Minimaler Struktur-Fix: Nicht-Komponenten-Exports wurden aus `.tsx`-Komponentendateien entfernt oder in `.ts`-Hilfsdateien verschoben.

Neue Hilfsdateien:

```text
src/components/anatomy/chakra-data.ts
src/components/anatomy/dysregulation-utils.ts
src/components/anatomy/glb-model-utils.ts
src/components/ui/button-variants.ts
src/components/ui/toggle-variants.ts
```

Import-Anpassungen:

- `AnatomyResonanceViewer.tsx` importiert `AVAILABLE_MODELS` jetzt aus `glb-model-utils.ts` und Dysregulation-Helper aus `dysregulation-utils.ts`.
- `InteractiveMeridianPoints.tsx` importiert Dysregulation-Helper aus `dysregulation-utils.ts`.
- `alert-dialog.tsx`, `calendar.tsx`, `pagination.tsx` importieren `buttonVariants` aus `button-variants.ts`.
- `toggle-group.tsx` importiert `toggleVariants` aus `toggle-variants.ts`.

Direkt entfernte Nicht-Komponenten-Exports:

- `badgeVariants` aus `badge.tsx` nicht mehr exportiert.
- `useFormField` aus `form.tsx` nicht mehr exportiert.
- `navigationMenuTriggerStyle` aus `navigation-menu.tsx` nicht mehr exportiert.
- `useSidebar` aus `sidebar.tsx` nicht mehr exportiert.
- `toast` aus `sonner.tsx` nicht mehr re-exportiert.

Hinweis zu bereits vorhandenen lokalen Änderungen:

- `src/components/AnatomyResonanceViewer.tsx` war vor Phase 6 Teil 16 bereits modified.
- Die in dieser Phase neu hinzugefügten Änderungen in dieser Datei betreffen nur Importpfade für ausgelagerte Helper/Konstanten.
- Der bereits bestehende Hook-Fix im Diff (`setShowMeridians(prev => ...)` usw.) stammt aus einer früheren Phase und wurde nicht zurückgesetzt.

## Geändertes Verhalten

Beabsichtigt keine fachliche Runtime-Änderung.

Unverändert bleiben:

- Rendering der Chakra-Visualisierung.
- Dysregulations-Farb- und Level-Logik.
- GLB-Modellpfad `'/models/human-body.glb'`.
- GLB-Preload-Mechanik in der neuen Hilfsdatei.
- Shadcn Button/Toggle Varianten und Klassen.
- Form-, Navigation-, Sidebar-, Badge- und Sonner-Komponentenverhalten.
- Keine neuen Logs, Uploads, E-Mails oder Persistenzpfade für Patienten-/Anamnesedaten.

## Verifikation

### Target ESLint der ursprünglichen Warning-Dateien

```bash
npx eslint \
  src/components/anatomy/ChakraVisualization.tsx \
  src/components/anatomy/DysregulationLegend.tsx \
  src/components/anatomy/GLBModelLoader.tsx \
  src/components/ui/badge.tsx \
  src/components/ui/button.tsx \
  src/components/ui/form.tsx \
  src/components/ui/navigation-menu.tsx \
  src/components/ui/sidebar.tsx \
  src/components/ui/sonner.tsx \
  src/components/ui/toggle.tsx
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
✓ 3678 modules transformed.
dist/index.html                     1.13 kB │ gzip:   0.48 kB
dist/assets/index-Cd_dPJH4.css     89.15 kB │ gzip:  15.24 kB
dist/assets/index-7whr_dXj.js   2,962.36 kB │ gzip: 829.13 kB
✓ built in 5.62s
```

Bekannte, unveränderte Build-Hinweise:

```text
Browserslist data is 12 months old
Some chunks are larger than 500 kB after minification
```

### Gesamt-Lint nach Phase 6 Teil 16

```bash
npm run lint
```

Ergebnis:

```text
> vite_react_shadcn_ts@0.0.0 lint
> eslint .

LINT_EXIT=0
```

Vergleich zu Phase 6 Teil 15:

```text
Vorher: 13 problems (0 errors, 13 warnings)
Nachher: 0 problems (0 errors, 0 warnings)
Verbesserung: -13 warnings, 0 neue errors
```

## Browser-/Runtime-Smoke

Portprüfung vor Start:

```text
port 5173: FREE
port 5174: FREE
port 5175: FREE
port 4173: FREE
```

Erster Dev-Server-Start ohne PTY:

```text
VITE v5.4.21 ready in 170 ms
Local: http://127.0.0.1:5173/
process status: exited
exit_code: 0
```

Da der Prozess direkt sauber beendet wurde, wurde für den eigentlichen Smoke ein PTY-gestützter Dev-Server auf demselben vorher frei geprüften Port gestartet.

Dev Server für Smoke:

```bash
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

Server-Output:

```text
VITE v5.4.21 ready in 175 ms
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
URL-Aufruf: http://127.0.0.1:5173/login?phase6_16=fast-refresh
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

Finaler Port-Check:

```text
ss -ltn 'sport = :5173'
# keine Ausgabe, Port nicht mehr belegt
```

## Ergebnis

Phase 6 Teil 16 ist abgeschlossen.

- Alle 13 Fast-Refresh-Warnings entfernt.
- Global ESLint ist vollständig sauber: `0 problems`.
- TypeScript ist sauber.
- Production Build ist sauber.
- Browser-/Login-Smoke ohne Console-/JS-Fehler.
- Keine DSGVO-sensitiven Datenflüsse verändert oder ergänzt.

## Nächster empfohlener Schritt

Phase 6 Teil 17:

1. Vollständige Abschlusskonsolidierung der Phase-6-Stabilisierung.
2. Finalen Git-Diff reviewen, besonders neue Utility-Dateien und Importpfade.
3. Optional ergänzende Route-Smokes für eine geschützte/komplexere UI-Seite wie `/analyse` oder Dashboard, sofern lokale Auth-/Demo-Bedingungen das erlauben.
4. Danach erst mit expliziter Freigabe über Commit/Push sprechen.
