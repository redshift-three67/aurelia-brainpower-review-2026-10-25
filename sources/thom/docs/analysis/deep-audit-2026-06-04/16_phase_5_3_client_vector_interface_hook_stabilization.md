# Phase 5 Teil 3 — ClientVectorInterface Hook-Stabilisierung

Datum: 2026-06-12
Projekt: `/opt/radithoms`
Datei: `src/components/ClientVectorInterface.tsx`

## Ziel

Runtime-relevante React-Hook-Warnungen im Klienten-Vektor-Interface stabilisieren, ohne fachliche Änderungen an biometrischer Eingabe, Hardware-Entropie, Klienten-Auswahl, Analyseberechnung oder Persistenz vorzunehmen.

## Ausgangsbefund

Gezielte ESLint-Prüfung vor der Änderung:

```text
/opt/radithoms/src/components/ClientVectorInterface.tsx
  195:6  warning  React Hook useEffect has missing dependencies: 'captureHardwareEntropy' and 'manualOverride'. Either include them or remove the dependency array
  414:6  warning  React Hook useCallback has a missing dependency: 'onClientSelected'. Either include it or remove the dependency array

✖ 2 problems (0 errors, 2 warnings)
```

## Root Cause

### Initiale Hardware-Entropie

Der Initial-Effect rief `captureHardwareEntropy()` mit leerem Dependency-Array auf. `captureHardwareEntropy` hängt jedoch bewusst von `hardwareState.serverStatus` und `manualOverride` ab.

Ein naives Ergänzen von `[manualOverride, captureHardwareEntropy]` hätte durch wechselnde Hardware-State-Referenzen potenziell mehrfach initiale Entropie-Erfassungen ausgelöst, obwohl die Funktion nur initialisieren sollte.

### Klienten-Auswahl nach Speichern

`saveToDatabase` ruft nach dem Erzeugen eines neuen Klienten `onClientSelected?.(newClient.id)` auf, hatte `onClientSelected` aber nicht im Dependency-Array. Der Parent (`Analyse.tsx`) liefert diesen Callback über `useCallback`, daher ist das Ergänzen als Dependency korrekt und stabil.

## Umsetzung

Minimaler Struktur-Fix:

- `hasCapturedInitialEntropyRef` ergänzt.
- Initiale Entropie-Erfassung läuft weiterhin nur einmal, solange `manualOverride` nicht aktiv ist.
- Der Initial-Effect besitzt nun vollständige Dependencies: `[manualOverride, captureHardwareEntropy]`.
- `saveToDatabase` besitzt nun `onClientSelected` in der Dependency-Liste.
- Keine fachliche Änderung an Hardware-Entropie-Konvertierung, Analyseberechnung, Client-Speicherung oder Upload-Logik.

## Geändertes Verhalten

Beabsichtigt keine fachliche Änderung.

Stabilisiert wurde ausschließlich:

1. die initiale Hook-Abhängigkeitsstruktur,
2. der Schutz gegen Mehrfach-Initialisierung durch Hardware-State-Änderungen,
3. die Callback-Frische bei `onClientSelected` nach neuem Client-Save.

## Verifikation

### Ziel-ESLint

```bash
npx eslint src/components/ClientVectorInterface.tsx
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
✓ built in 5.54s
```

Bekannte, unveränderte Build-Hinweise:

```text
Browserslist data is 12 months old
Some chunks are larger than 500 kB after minification
```

### Gesamt-Lint nach Phase 5 Teil 3

```bash
npm run lint
```

Ergebnis:

```text
✖ 68 problems (51 errors, 17 warnings)
```

Vergleich zu Phase 5 Teil 2:

```text
Vorher: 70 problems (51 errors, 19 warnings)
Nachher: 68 problems (51 errors, 17 warnings)
Verbesserung: -2 Hook-Warnungen, 0 neue Errors
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
VITE v5.4.21 ready in 179 ms
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
http://127.0.0.1:5173/analyse?phase5_3=client-vector-interface
Redirect: http://127.0.0.1:5173/login
Console: []
js_errors: []
total_errors: 0
```

Der direkte Analysepfad ist erwartbar durch Auth/ProtectedRoute geschützt. Ohne Login wurde der geschützte Redirect und die fehlerfreie Runtime-Initialisierung geprüft.

## Ergebnis

Phase 5 Teil 3 ist abgeschlossen.

- `src/components/ClientVectorInterface.tsx`: gezielter ESLint sauber.
- TypeScript sauber.
- Production Build sauber.
- Gesamt-Lint von 70 auf 68 Probleme verbessert.
- Browser-Smoke ohne Console-/JS-Fehler.
- Keine Änderung an patientenbezogenen Datenflüssen, Speicherschema oder Auth-Grenzen.

## Nächster empfohlener Schritt

Phase 5 Teil 4 sollte mit dem nächsten runtime-relevanten Hook-Kandidaten fortfahren:

1. `src/hooks/useMeridianDiagnosis.ts`
   - KI-/Behandlungsempfehlungsfluss.
   - Aktuelle Warnung betrifft `fetchAIRecommendation`.

2. Danach `src/hooks/useAnatomyModels.ts`
   - Modell-Ladezyklus.

3. Danach `src/components/AnatomyResonanceViewer.tsx`
   - Sichtbarkeits-/Rendering-State im anatomischen Resonanzviewer.
