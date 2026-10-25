# Phase 5 Teil 6 — AnatomyResonanceViewer Hook-Stabilisierung

Datum: 2026-06-12
Projekt: `/opt/radithoms`
Datei: `src/components/AnatomyResonanceViewer.tsx`

## Ziel

Runtime-relevante React-Hook-Warnung im anatomischen Resonanzviewer stabilisieren, ohne fachliche Änderungen an Modell-Layer-Fähigkeiten, 3D-/GLB-Rendering, NLS-Scan, Meridian-, Chakra-, Resonanzpunkt- oder Organ-Scan-Steuerung vorzunehmen.

## Ausgangsbefund

Gezielte ESLint-Prüfung vor der Änderung:

```text
/opt/radithoms/src/components/AnatomyResonanceViewer.tsx
  1256:6  warning  React Hook useEffect has missing dependencies: 'showChakras', 'showMeridians', 'showOrganScan', and 'showResonancePoints'. Either include them or remove the dependency array

✖ 1 problem (0 errors, 1 warning)
```

## Root Cause

Der Effekt für die model-aware Layer-Sichtbarkeit las die aktuellen UI-State-Werte:

- `showMeridians`
- `showChakras`
- `showResonancePoints`
- `showOrganScan`

Die Dependency-Liste enthielt jedoch nur die berechneten Capability-Flags:

- `canShowMeridians`
- `canShowChakras`
- `canShowResonancePoints`
- `canShowNLS`

Ein naives Ergänzen der `show*` States hätte den Effekt bei jeder Toggle-Änderung erneut ausgeführt. Das wäre zwar vermutlich korrekt, aber nicht optimal, weil der Effekt fachlich nur die Reaktion auf geänderte Modell-Fähigkeiten braucht.

## Umsetzung

Minimaler Struktur-Fix:

- Direkte State-Lesungen im Effekt entfernt.
- Layer-Abschaltung auf funktionale State-Updates umgestellt.
- Dependency-Liste bleibt dadurch fachlich auf den Modell-Capability-Flags begrenzt.

Vorher:

```tsx
if (!canShowMeridians && showMeridians) setShowMeridians(false);
if (!canShowChakras && showChakras) setShowChakras(false);
if (!canShowResonancePoints && showResonancePoints) setShowResonancePoints(false);
if (!canShowNLS && showOrganScan) setShowOrganScan(false);
```

Nachher:

```tsx
setShowMeridians(prev => (canShowMeridians ? prev : false));
setShowChakras(prev => (canShowChakras ? prev : false));
setShowResonancePoints(prev => (canShowResonancePoints ? prev : false));
setShowOrganScan(prev => (canShowNLS ? prev : false));
```

## Geändertes Verhalten

Beabsichtigt keine fachliche Änderung.

Stabilisiert wurde ausschließlich die Hook-Struktur:

- Wenn das aktive Modell einen Layer unterstützt, bleibt der aktuelle Toggle-State unverändert.
- Wenn das aktive Modell einen Layer nicht unterstützt, wird der Toggle-State auf `false` gesetzt.
- Keine unnötige Abhängigkeit von den aktuell gelesenen Toggle-States im Effect.

Keine Änderung an:

- GLB-/Fallback-Modell-Auswahl,
- Anatomie-Modell-Layer-Vertrag,
- Mermaid-/Meridian-/Chakra-/NLS-Renderpfaden,
- Scan-Konfiguration,
- Organ-/Landmark-Filtering,
- Patientendaten-/Auth-Flüssen.

## Verifikation

### Ziel-ESLint

```bash
npx eslint src/components/AnatomyResonanceViewer.tsx
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
✓ built in 5.47s
```

Bekannte, unveränderte Build-Hinweise:

```text
Browserslist data is 12 months old
Some chunks are larger than 500 kB after minification
```

### Gesamt-Lint nach Phase 5 Teil 6

```bash
npm run lint
```

Ergebnis:

```text
✖ 64 problems (50 errors, 14 warnings)
```

Vergleich zu Phase 5 Teil 5:

```text
Vorher: 65 problems (50 errors, 15 warnings)
Nachher: 64 problems (50 errors, 14 warnings)
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
VITE v5.4.21 ready in 177 ms
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
http://127.0.0.1:5173/analyse?phase5_6=anatomy-resonance-viewer
Redirect: http://127.0.0.1:5173/login
Console: []
js_errors: []
total_errors: 0
```

Der direkte Analysepfad ist erwartbar durch Auth/ProtectedRoute geschützt. Ohne Login wurde der geschützte Zugriff und die fehlerfreie Runtime-Initialisierung geprüft.

## Ergebnis

Phase 5 Teil 6 ist abgeschlossen.

- `src/components/AnatomyResonanceViewer.tsx`: gezielter ESLint sauber.
- TypeScript sauber.
- Production Build sauber.
- Gesamt-Lint von 65 auf 64 Probleme verbessert.
- Browser-Smoke ohne Console-/JS-Fehler.
- Keine Änderung an Patientendatenflüssen, Auth-Grenzen oder Persistenzschema.

## Nächster empfohlener Schritt

Phase 5 Teil 7 sollte mit dem letzten verbliebenen `react-hooks/exhaustive-deps`-Kandidaten fortfahren:

1. `src/components/ClientVectorTrajectory3D.tsx`
   - Memoisierung des `pos3D` Arrays.
   - Aktuelle Warnung: `pos3D` Array macht die Dependencies eines `useMemo` instabil.

Danach sollte Phase 5 fachlich umschalten:

2. Entscheidung: verbleibende Fast-Refresh-Warnungen oder systematischer Abbau der `no-explicit-any` Errors.
