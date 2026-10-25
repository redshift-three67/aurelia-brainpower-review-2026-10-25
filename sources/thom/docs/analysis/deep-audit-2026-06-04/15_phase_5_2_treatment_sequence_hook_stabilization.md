# Phase 5 Teil 2 — useTreatmentSequence Hook-Stabilisierung

Datum: 2026-06-12
Projekt: `/opt/radithoms`
Datei: `src/hooks/useTreatmentSequence.ts`

## Ziel

Runtime-relevante React-Hook-Warnungen im Behandlungssequenz-Hook stabilisieren, ohne die fachliche Audio-, AM-Modulations-, Sequenz-, Retest- oder Continuous-Mode-Logik zu verändern.

## Ausgangsbefund

Gezielte ESLint-Prüfung vor der Änderung:

```text
/opt/radithoms/src/hooks/useTreatmentSequence.ts
  149:6  warning  React Hook useEffect has a missing dependency: 'stopOscillator'. Either include it or remove the dependency array
  365:6  warning  React Hook useCallback has a missing dependency: 'stopOscillator'. Either include it or remove the dependency array

✖ 2 problems (0 errors, 2 warnings)
```

## Root Cause

`stopOscillator` wird an zwei kritischen Stellen verwendet:

1. im Unmount-Cleanup-Effect für Audio- und Intervall-Aufräumarbeiten,
2. innerhalb von `startOscillator`, wenn zwischen AM-Modus und Standard-Oszillator gewechselt oder ein bestehender Oszillator gestoppt werden muss.

Die Funktion war jedoch unterhalb von `startOscillator` deklariert. Ein einfaches Ergänzen von `[stopOscillator]` im oberen `useEffect` hätte wegen der Auswertungsreihenfolge der Dependency-Liste ein Temporal-Dead-Zone-/Initialisierungsrisiko erzeugt. Deshalb war ein reines Dependency-Array-Patch nicht stabil genug.

## Umsetzung

Minimaler Struktur-Fix:

- `stopOscillator` wurde oberhalb des ersten `useEffect` und oberhalb von `startOscillator` positioniert.
- Der Unmount-Cleanup-Effect verwendet nun `[stopOscillator]` als Dependency.
- `startOscillator` verwendet nun `[stopOscillator]` als Dependency.
- Keine fachliche Änderung an Frequenzen, AudioContext-Erzeugung, AM-Modulation, Retest-Logik, Sequenzfortschritt oder Treatment-State.

## Geändertes Verhalten

Kein fachliches Verhalten wurde beabsichtigt geändert.

Stabilisiert wurde ausschließlich die React-Hook-Abhängigkeitsstruktur, damit Cleanup und Oszillatorwechsel immer die aktuelle stabile Callback-Referenz verwenden.

## Verifikation

### Ziel-ESLint

```bash
npx eslint src/hooks/useTreatmentSequence.ts
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
✓ built in 5.57s
```

Bekannte, unveränderte Build-Hinweise:

```text
Browserslist data is 12 months old
Some chunks are larger than 500 kB after minification
```

### Gesamt-Lint nach Phase 5 Teil 2

```bash
npm run lint
```

Ergebnis:

```text
✖ 70 problems (51 errors, 19 warnings)
```

Vergleich zu Phase 5 Teil 1:

```text
Vorher: 72 problems (51 errors, 21 warnings)
Nachher: 70 problems (51 errors, 19 warnings)
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
VITE v5.4.21 ready in 176 ms
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
http://127.0.0.1:5173/analyse?phase5_2=treatment-sequence
Redirect: http://127.0.0.1:5173/login
Console: []
js_errors: []
total_errors: 0
```

Der direkte Analysepfad ist erwartbar durch Auth/ProtectedRoute geschützt. Ohne Login wurde daher nur der geschützte Redirect und die fehlerfreie Runtime-Initialisierung geprüft.

## Ergebnis

Phase 5 Teil 2 ist abgeschlossen.

- `src/hooks/useTreatmentSequence.ts`: gezielter ESLint sauber.
- TypeScript sauber.
- Production Build sauber.
- Gesamt-Lint von 72 auf 70 Probleme verbessert.
- Browser-Smoke ohne Console-/JS-Fehler.
- Keine Änderung an patientenbezogenen Datenflüssen oder Persistenz.

## Nächster empfohlener Schritt

Phase 5 Teil 3 sollte mit dem nächsten runtime-relevanten Hook-Kandidaten fortfahren:

1. `src/components/ClientVectorInterface.tsx`
   - Hardware-Entropie, manuelles Override, Auswahl-Callback.
   - Aktuelle Warnungen betreffen `captureHardwareEntropy`, `manualOverride`, `onClientSelected`.

2. Danach `src/hooks/useMeridianDiagnosis.ts`
   - KI-/Behandlungsempfehlungsfluss.

3. Danach `src/hooks/useAnatomyModels.ts`
   - Modell-Ladezyklus.
