# Phase 5 — FrequencyOutputModule Hook-Stabilisierung

Datum: 2026-06-12T22:10:35+02:00
Projekt: `/opt/radithoms`
Schwerpunkt: `src/components/FrequencyOutputModule.tsx`

## Ziel

Phase 5 startete mit dem bewusst priorisierten Runtime-/Hook-Bereich `FrequencyOutputModule.tsx`, weil diese Komponente AudioWorklet, Oszillator-Fallback, Timer, WebSerial und Frequenz-Output-Logik enthält. Die Lint-Warnungen in diesem Bereich waren funktional riskanter als reine `any`-Typ-Restbestände.

## Ausgangsbefund

Gezielte ESLint-Prüfung vor der Änderung:

```text
/opt/radithoms/src/components/FrequencyOutputModule.tsx
  162:6  warning  React Hook useEffect has missing dependencies: 'disconnectSerial' and 'stopAudio'
  247:6  warning  React Hook useCallback has a missing dependency: 'WORKLET_CODE'
  280:6  warning  React Hook useEffect has a missing dependency: 'stopAudio'
  349:6  warning  React Hook useCallback has a missing dependency: 'startOscillatorFallback'

✖ 4 problems (0 errors, 4 warnings)
```

## Root Cause

Die Warnungen hatten unterschiedliche Ursachen:

1. `WORKLET_CODE` war innerhalb der Komponente deklariert und wurde dadurch bei jedem Render neu erzeugt.
2. `startAudio` nutzte `startOscillatorFallback`, ohne diesen Callback in der Dependency-Liste zu führen.
3. Timer- und Cleanup-Effekte nutzten `stopAudio`, ohne die stabile Callback-Abhängigkeit anzugeben.
4. Der Unmount-Cleanup nutzte zusätzlich `disconnectSerial`, ebenfalls ohne Dependency.
5. Einige Funktionsdeklarationen lagen in einer Reihenfolge, bei der ein naives Hinzufügen der Dependencies zu Temporal-Dead-Zone-/Initialisierungsproblemen geführt hätte.

## Minimaler stabiler Fix

Umgesetzt wurde keine Verhaltensänderung der Audio-/Serial-Logik, sondern eine strukturelle Stabilisierung der Hook-Abhängigkeiten:

- `WORKLET_CODE` auf Modulebene verschoben, damit der AudioWorklet-Code nicht pro Render neu erzeugt wird.
- `stopAudio` vor den Timer-Effekt verschoben, damit `stopAudio` korrekt in den Dependencies geführt werden kann.
- `startOscillatorFallback` vor `startAudio` verschoben, damit `startAudio` den Fallback korrekt als Dependency führen kann.
- Unmount-Cleanup hinter `disconnectSerial` verschoben.
- Cleanup-Effekt auf explizite Dependencies gesetzt:

```tsx
useEffect(() => {
  return () => {
    stopAudio();
    void disconnectSerial();
  };
}, [stopAudio, disconnectSerial]);
```

- Timer-Effekt ergänzt:

```tsx
}, [isPlaying, isTimerEnabled, duration, frequency, stopAudio]);
```

- `startAudio` ergänzt:

```tsx
}, [
  frequency,
  amplitude,
  waveform,
  modulationEnabled,
  modulationFreq,
  modulationDepth,
  isMuted,
  emOutputEnabled,
  initAudio,
  onFrequencyChange,
  currentModeConfig,
  workletReady,
  startOscillatorFallback,
]);
```

## Nachverifikation

### Ziel-Lint für FrequencyOutputModule

```bash
npx eslint src/components/FrequencyOutputModule.tsx
```

Ergebnis:

```text
PASS, exit_code 0
```

Damit wurden alle 4 FrequencyOutputModule-Hook-Warnungen entfernt.

### TypeScript

```bash
npx tsc --noEmit
```

Ergebnis:

```text
PASS, exit_code 0
```

### Build

```bash
npm run build
```

Ergebnis:

```text
✓ built in 5.46s
```

Bekannter Hinweis bleibt bestehen:

```text
Some chunks are larger than 500 kB after minification.
```

### Gesamt-Lint

```bash
npm run lint
```

Vor Phase 5:

```text
✖ 76 problems (51 errors, 25 warnings)
```

Nach Phase 5:

```text
✖ 72 problems (51 errors, 21 warnings)
```

Verbesserung:

```text
-4 warnings
0 neue errors
```

### Browser-Smoke

Dev Server:

```bash
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

HTTP-Readiness:

```text
HTTP_STATUS 200
CONTENT_TYPE text/html
```

Browser-Check:

```text
URL: http://127.0.0.1:5173/analyse?phase5=frequency-output
Ergebnis: ProtectedRoute leitete erwartbar auf Login/Access-Seite weiter.
Console: leer
js_errors: []
total_errors: 0
```

Hinweis: Ein direkter UI-Test der `FrequencyOutputModule`-Controls war ohne Authentifizierung nicht erreichbar. Die Komponente wurde aber über TypeScript, Production-Build und gezielten ESLint erfolgreich verifiziert.

## Bewertung

| Bereich | Status | Kommentar |
|---|---:|---|
| FrequencyOutputModule Ziel-Lint | PASS | 4/4 Hook-Warnungen entfernt |
| TypeScript | PASS | `npx tsc --noEmit` grün |
| Production Build | PASS | `npm run build` grün |
| Gesamt-Lint | PARTIAL PASS | von 76 auf 72 Probleme reduziert |
| Browser Auth-Route | PASS | `/analyse` ProtectedRoute ohne Console-Fehler |
| Direkter Frequency-UI-Test | BLOCKED | Ohne Login/Auth nicht erreichbar |

## Geänderte Datei in dieser Teilphase

```text
src/components/FrequencyOutputModule.tsx
```

## Nächste priorisierte Schritte

1. Weiter mit verbleibenden `react-hooks/exhaustive-deps` Warnungen mit Runtime-Relevanz:
   - `src/hooks/useTreatmentSequence.ts`
   - `src/components/ClientVectorInterface.tsx`
   - `src/hooks/useMeridianDiagnosis.ts`
   - `src/hooks/useAnatomyModels.ts`
2. Danach erneut:
   - Ziel-Lint pro Datei
   - `npx tsc --noEmit`
   - `npm run build`
   - `npm run lint`
3. Erst danach die `any`-Typbestände in separaten, kontrollierten Blöcken reduzieren.
