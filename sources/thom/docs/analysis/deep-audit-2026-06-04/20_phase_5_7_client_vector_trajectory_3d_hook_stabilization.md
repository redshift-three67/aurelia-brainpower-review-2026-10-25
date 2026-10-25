# Phase 5 Teil 7 — ClientVectorTrajectory3D Hook-Stabilisierung

Datum: 2026-06-13
Projekt: `/opt/radithoms`
Datei: `src/components/ClientVectorTrajectory3D.tsx`

## Ziel

Letzten verbliebenen `react-hooks/exhaustive-deps`-Kandidaten im 3D-Trajektorien-Viewer stabilisieren, ohne fachliche Änderungen an Cusp-Surface, Client-Punkt, Attraktor-Linie, OrbitControls, Animationslogik oder Feldengine-Vektorabbildung vorzunehmen.

## Ausgangsbefund

Gezielte ESLint-Prüfung vor der Änderung:

```text
/opt/radithoms/src/components/ClientVectorTrajectory3D.tsx
  202:9  warning  The 'pos3D' array makes the dependencies of useMemo Hook (at line 221) change on every render. Move it inside the useMemo callback. Alternatively, wrap the initialization of 'pos3D' in its own useMemo() Hook

✖ 1 problem (0 errors, 1 warning)
```

## Root Cause

`ConnectionLine` berechnete `pos3D` als neues Array bei jedem Render und verwendete dieses Array anschließend als Dependency des `points`-`useMemo`.

Dadurch wurde die Memoisierung der Verbindungslinie praktisch instabil, weil die Array-Identität von `pos3D` bei jedem Render neu war, selbst wenn die Werte gleich blieben.

Zusätzlich war der Default-Wert von `attractorPosition` als Inline-Array (`[0, 0, 0]`) im Funktionsparameter definiert. Zur Stabilisierung wurde dieser Default ebenfalls auf eine Module-Scope-Konstante verschoben.

## Umsetzung

Minimaler Struktur-Fix:

- `DEFAULT_ATTRACTOR_POSITION` auf Modulebene ergänzt.
- `pos3D` aus dem Render-Scope in das `useMemo` verschoben.
- Dependency-Liste von `points` auf die echten Eingaben gesetzt:
  - `clientPosition`
  - `attractorPosition`

Relevanter Zielzustand:

```tsx
const DEFAULT_ATTRACTOR_POSITION: [number, number, number] = [0, 0, 0];
```

```tsx
function ConnectionLine({
  clientPosition,
  attractorPosition = DEFAULT_ATTRACTOR_POSITION
}: {
  clientPosition: number[];
  attractorPosition?: number[];
}) {
  const points = useMemo(() => {
    const pos3D: [number, number, number] = [
      clientPosition[0] * 1.5 || 0,
      clientPosition[1] * 1.5 || 0,
      clientPosition[2] * 1.5 || 0
    ];
    // curve calculation unchanged
  }, [clientPosition, attractorPosition]);
}
```

## Geändertes Verhalten

Beabsichtigt keine fachliche Änderung.

Stabilisiert wurde ausschließlich die Memoisierung:

- Die Verbindungslinie wird nicht mehr wegen einer neu erzeugten `pos3D`-Array-Identität invalidiert.
- Die Kurvenpunkte hängen weiterhin korrekt von `clientPosition` und `attractorPosition` ab.
- Die 5D-zu-3D-Abbildung bleibt unverändert:
  - `clientPosition[0] * 1.5`
  - `clientPosition[1] * 1.5`
  - `clientPosition[2] * 1.5`

Keine Änderung an:

- Cusp-Surface-Berechnung,
- Trail-Update des Client-Punkts,
- Attraktor-Visualisierung,
- Phasen-/Risiko-Farben,
- OrbitControls,
- Feldengine-Datenvertrag,
- Auth-/Patientendatenflüssen.

## Verifikation

### Ziel-ESLint

```bash
npx eslint src/components/ClientVectorTrajectory3D.tsx
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
✓ 3674 modules transformed.
✓ built in 5.49s
```

Bekannte, unveränderte Build-Hinweise:

```text
Browserslist data is 12 months old
Some chunks are larger than 500 kB after minification
```

### Gesamt-Lint nach Phase 5 Teil 7

```bash
npm run lint
```

Ergebnis:

```text
✖ 63 problems (50 errors, 13 warnings)
```

Vergleich zu Phase 5 Teil 6:

```text
Vorher: 64 problems (50 errors, 14 warnings)
Nachher: 63 problems (50 errors, 13 warnings)
Verbesserung: -1 Hook-Warnung, 0 neue Errors
```

### Browser-/Runtime-Smoke

Vor Start wurde Port 5173 geprüft:

```text
5173 free
5174 free
5175 free
4173 free
```

Dev Server:

```bash
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

Serverausgabe:

```text
VITE v5.4.21 ready in 174 ms
Local: http://127.0.0.1:5173/
```

HTTP-Smoke:

```text
HTTP_STATUS 200
CONTENT_TYPE text/html
BYTES 1285
```

Browser-Smoke:

```text
http://127.0.0.1:5173/analyse?phase5_7=client-vector-trajectory-3d
Redirect: http://127.0.0.1:5173/login
Console: []
js_errors: []
total_errors: 0
```

Der direkte Analysepfad ist erwartbar durch Auth/ProtectedRoute geschützt. Ohne Login wurde der geschützte Zugriff und die fehlerfreie Runtime-Initialisierung geprüft.

## Ergebnis

Phase 5 Teil 7 ist abgeschlossen.

- `src/components/ClientVectorTrajectory3D.tsx`: gezielter ESLint sauber.
- TypeScript sauber.
- Production Build sauber.
- Gesamt-Lint von 64 auf 63 Probleme verbessert.
- Browser-Smoke ohne Console-/JS-Fehler.
- Damit ist der priorisierte `react-hooks/exhaustive-deps`-Block in Phase 5 fachlich abgearbeitet.

## Nächster empfohlener Schritt

Nach Abschluss des Hook-Blocks sollte Phase 5 auf systematischen Abbau der verbleibenden `no-explicit-any` Errors umschalten, priorisiert nach Runtime-/Datenfluss-Risiko.

Empfohlene nächste Kandidaten:

1. `src/services/realtime/RealtimeHarmonizationService.ts`
   - Realtime-/Streaming-/Harmonization-Service.
   - 7 `no-explicit-any` Errors.
   - Höchste Runtime-Relevanz.

2. `src/components/TCMTrendAnalytics.tsx`
   - Analyse-/Trenddatenfluss.
   - 4 `no-explicit-any` Errors.

3. `src/components/SessionReportGenerator.tsx`
   - Report-/Export-Datenstruktur.
   - 4 `no-explicit-any` Errors.

Fast-Refresh-Warnungen bleiben bewusst nachrangig, weil sie primär Developer-Experience betreffen und weniger Runtime-/Datenfluss-Risiko tragen.
