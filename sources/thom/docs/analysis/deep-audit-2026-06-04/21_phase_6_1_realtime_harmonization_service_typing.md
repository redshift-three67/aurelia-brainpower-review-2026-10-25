# Phase 6 Teil 1 — RealtimeHarmonizationService Typ-Stabilisierung

Datum: 2026-06-13
Projekt: `/opt/radithoms`
Datei: `src/services/realtime/RealtimeHarmonizationService.ts`

## Ziel

Start von Phase 6: systematischer Abbau der verbleibenden `no-explicit-any` Errors nach Runtime-/Datenfluss-Risiko.

Priorisierter Kandidat war der Echtzeit-Harmonisierungs-Service, weil er AudioWorklet, WebAudio-Fallback, WebSocket-Synchronisation, Frequenzhistorie und GPU-/Server-Fallback-Flüsse verbindet.

## Ausgangsbefund

Gezielte ESLint-Prüfung vor der Änderung:

```text
/opt/radithoms/src/services/realtime/RealtimeHarmonizationService.ts
  298:18  error  Unexpected any. Specify a different type  @typescript-eslint/no-explicit-any
  369:20  error  Unexpected any. Specify a different type  @typescript-eslint/no-explicit-any
  371:20  error  Unexpected any. Specify a different type  @typescript-eslint/no-explicit-any
  372:20  error  Unexpected any. Specify a different type  @typescript-eslint/no-explicit-any
  376:18  error  Unexpected any. Specify a different type  @typescript-eslint/no-explicit-any
  392:18  error  Unexpected any. Specify a different type  @typescript-eslint/no-explicit-any
  393:16  error  Unexpected any. Specify a different type  @typescript-eslint/no-explicit-any

✖ 7 problems (7 errors, 0 warnings)
```

## Root Cause

Der Service speicherte den lokalen WebAudio-Fallback-Oszillator dynamisch auf der Service-Instanz:

```ts
(this as any)._fallbackOscillator = oscillator;
```

Anschließend wurde derselbe dynamische Slot über weitere `this as any` Zugriffe gelesen, gestoppt, disconnected, geleert und bei Frequenzänderungen aktualisiert.

Das war funktional nachvollziehbar, aber typseitig instabil:

- kein deklarierter Klassenvertrag für den Fallback-Oszillator,
- kein Typ für die `frequency`-Automation im Fallback-Pfad,
- mehrere `any`-Casts auf einer runtime-relevanten Service-Instanz.

## Umsetzung

Minimaler Typ-Fix ohne Runtime-Logikänderung:

- Private Klassen-Property ergänzt:

```ts
private fallbackOscillator: OscillatorNode | null = null;
```

- Dynamische Instanzablage ersetzt:

```ts
this.fallbackOscillator = oscillator;
```

- Stop-/Disconnect-Pfad typisiert:

```ts
if (this.fallbackOscillator) {
  try {
    this.fallbackOscillator.stop();
    this.fallbackOscillator.disconnect();
  } catch (error) {
    void error;
  }
  this.fallbackOscillator = null;
}
```

- Echtzeit-Frequenzänderung im Fallback-Pfad typisiert:

```ts
if (this.fallbackOscillator && this.audioContext) {
  this.fallbackOscillator.frequency.setValueAtTime(
    frequency,
    this.audioContext.currentTime
  );
}
```

## Geändertes Verhalten

Beabsichtigt keine fachliche Runtime-Änderung.

Stabilisiert wurde ausschließlich der interne Typvertrag:

- Fallback-Oszillator bleibt weiterhin derselbe WebAudio-`OscillatorNode`.
- Stop-/Disconnect-Reihenfolge bleibt gleich.
- Frequenzautomation bleibt gleich.
- AudioWorklet-Pfad bleibt unverändert.
- WebSocket-/Server-/GPU-Synchronisation bleibt unverändert.
- Supabase-/Edge-Function-/Patientendatenflüsse bleiben unverändert.

## Verifikation

### Ziel-ESLint

```bash
npx eslint src/services/realtime/RealtimeHarmonizationService.ts
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
✓ built in 5.46s
```

Bekannte, unveränderte Build-Hinweise:

```text
Browserslist data is 12 months old
Some chunks are larger than 500 kB after minification
```

### Gesamt-Lint nach Phase 6 Teil 1

```bash
npm run lint
```

Ergebnis:

```text
✖ 56 problems (43 errors, 13 warnings)
```

Vergleich zu Phase 5 Teil 7:

```text
Vorher: 63 problems (50 errors, 13 warnings)
Nachher: 56 problems (43 errors, 13 warnings)
Verbesserung: -7 errors, 0 neue warnings/errors
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
VITE v5.4.21 ready in 170 ms
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
http://127.0.0.1:5173/analyse?phase6_1=realtime-harmonization-service
Login-/Auth-Seite sichtbar
Console: []
js_errors: []
total_errors: 0
```

Der direkte Analysepfad ist erwartbar durch Auth/ProtectedRoute geschützt. Ohne Login wurde der geschützte Zugriff und die fehlerfreie Runtime-Initialisierung geprüft.

## Ergebnis

Phase 6 Teil 1 ist abgeschlossen.

- `src/services/realtime/RealtimeHarmonizationService.ts`: gezielter ESLint sauber.
- 7 `no-explicit-any` Errors entfernt.
- TypeScript sauber.
- Production Build sauber.
- Gesamt-Lint von 63 auf 56 Probleme verbessert.
- Browser-Smoke ohne Console-/JS-Fehler.

## Nächster empfohlener Schritt

Weiter mit Phase 6 Teil 2 nach Runtime-/Datenfluss-Risiko:

1. `src/components/TCMTrendAnalytics.tsx`
   - 4 `no-explicit-any` Errors.
   - Analyse-/Trenddatenfluss und Visualisierungsnähe.

Danach:

2. `src/components/SessionReportGenerator.tsx`
   - 4 `no-explicit-any` Errors.
   - Report-/Export-Datenstruktur.

3. `src/components/WordEnergyDBManager.tsx`
   - 7 `no-explicit-any` Errors.
   - Datenbank-/Import-/Mapping-nahe Struktur.
