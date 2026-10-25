# Phase 4 — Lokale Laufzeit-/Browser-Smoke-Verifikation

Datum: 2026-06-12T22:03:19+02:00
Projekt: `/opt/radithoms`
Branch: `main...origin/main`
Dev-Port: `127.0.0.1:5173`

## Ziel

Nach Phase 1–3 wurde die lokale Laufzeitfähigkeit der RadiThoms-Frontend-App unter einem explizit geprüften freien Port verifiziert. Zusätzlich wurde ein beim Browser-Smoke-Test entdeckter React-Runtime-Loop systematisch bis zur Root Cause nachverfolgt, minimal behoben und erneut verifiziert.

## Startzustand

Vor dem Dev-Server-Start waren die relevanten Ports frei:

```text
5173 FREE
5174 FREE
5175 FREE
4173 FREE
```

Der Dev-Server wurde bewusst auf Port 5173 mit Strict-Port gestartet:

```bash
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

HTTP-Readiness war erfolgreich:

```text
HTTP_STATUS 200
CONTENT_TYPE text/html
```

## Erstbefund im Browser-Smoke-Test

Die App lud grundsätzlich und zeigte die Startseite:

```text
Title: Feldengine – Morphogenese & Katastrophentheorie | René Thom
URL: http://127.0.0.1:5173/
```

Der erste Console-Check zeigte jedoch wiederholt:

```text
Warning: Maximum update depth exceeded.
This can happen when a component calls setState inside useEffect,
but useEffect either doesn't have a dependency array,
or one of the dependencies changes on every render.

at SystemStatusDashboard
```

Zusätzlich wurden massenhaft Start-/Stop-Logs ausgegeben:

```text
[SystemMonitor] Starting with interval: 1000 ms
[SystemMonitor] Stopped
```

## Root Cause

Datei:

```text
src/components/SystemStatusDashboard.tsx
```

Ursprünglicher Effekt:

```tsx
useEffect(() => {
  if (!isMonitoring) {
    startMonitoring(1000);
  }
  return () => stopMonitoring();
}, [isMonitoring, startMonitoring, stopMonitoring]);
```

Ursache:

- Der Effekt hing von `isMonitoring` ab.
- `startMonitoring()` setzt `isMonitoring` auf `true`.
- Durch diese Dependency-Änderung wurde der Effekt neu ausgeführt.
- Beim Re-Run wurde vorher das Cleanup ausgeführt.
- Das Cleanup rief `stopMonitoring()` auf und setzte `isMonitoring` wieder auf `false`.
- Dadurch entstand ein Start-/Stop-Render-Zyklus mit React-Warnung `Maximum update depth exceeded`.

Klassifikation:

```text
Runtime-/Hook-Dependency-Bug im Auto-Start des System-Monitorings.
Kein Build-/TypeScript-Problem.
Kein Dependency-Security-Problem.
Keine Schema- oder API-Contract-Änderung.
```

## Minimaler Fix

Der Auto-Start-Effekt wurde so angepasst, dass der Lifecycle an Mount/Unmount gebunden ist und nicht an den daraus resultierenden Monitoring-State:

```tsx
useEffect(() => {
  startMonitoring(1000);
  return () => stopMonitoring();
}, [startMonitoring, stopMonitoring]);
```

Diff:

```diff
-  useEffect(() => {
-    if (!isMonitoring) {
-      startMonitoring(1000);
-    }
-    return () => stopMonitoring();
-  }, [isMonitoring, startMonitoring, stopMonitoring]);
+  useEffect(() => {
+    startMonitoring(1000);
+    return () => stopMonitoring();
+  }, [startMonitoring, stopMonitoring]);
```

## Nachverifikation

### Build

```bash
npm run build
```

Ergebnis:

```text
✓ built in 9.57s
```

Hinweis: Der bekannte Chunk-Size-Hinweis bleibt bestehen, ist aber kein Build-Fehler.

### TypeScript

```bash
npx tsc --noEmit
```

Ergebnis:

```text
PASS, exit_code 0
```

### Browser nach Fix

Navigation erfolgreich:

```text
URL: http://127.0.0.1:5173/?phase4=postfix
readyState: complete
Title: Feldengine – Morphogenese & Katastrophentheorie | René Thom
```

Smoke-Interaktionen erfolgreich ohne Console-Fehler:

```text
- Theme umschalten
- Szenario Button: Bistabil
- Szenario Button: Monostabil
- 3D Button: Pfad anzeigen
```

Console nach Fix:

```text
console_messages: []
js_errors: []
total_messages: 0
total_errors: 0
```

### Lint

```bash
npm run lint
```

Ergebnis bleibt erwartbar rot und entspricht dem bereits bekannten Restbestand:

```text
✖ 76 problems (51 errors, 25 warnings)
```

Der Phase-4-Fix hat keine neue Lint-Regression sichtbar gemacht. Die verbleibenden Lint-Klassen bleiben in separaten Phasen abzuarbeiten.

## Bewertung

| Bereich | Status | Kommentar |
|---|---:|---|
| Dev-Port-Prüfung | PASS | Port 5173 war frei und wurde explizit genutzt |
| Dev-Server HTTP | PASS | HTTP 200, `text/html` |
| Startseite lädt | PASS | Titel und Hauptinhalt vorhanden |
| Browser-Console vor Fix | FAIL | React Maximum-update-depth im SystemStatusDashboard |
| Root Cause verstanden | PASS | `isMonitoring` als Effekt-Dependency erzeugte Start-/Stop-Zyklus |
| Minimalfix umgesetzt | PASS | Lifecycle-Effekt hängt nur an stabilen Callback-Dependencies |
| Browser-Console nach Fix | PASS | Keine Console-Meldungen/JS-Errors nach Reload und Interaktionen |
| Build | PASS | `npm run build` grün |
| TypeScript | PASS | `npx tsc --noEmit` grün |
| Lint | KNOWN FAIL | Bekannter Restbestand 76 Problems |

## Geänderte Datei in Phase 4

```text
src/components/SystemStatusDashboard.tsx
```

## Nächste priorisierte Schritte

1. Phase 5: Lint-Restbestand weiter reduzieren, priorisiert nach Risiko:
   - zuerst `react-hooks/exhaustive-deps` mit Runtime-Relevanz,
   - danach `@typescript-eslint/no-explicit-any`,
   - danach Fast-Refresh-Strukturwarnungen.
2. Danach erneute Gates:
   - `npm run build`
   - `npx tsc --noEmit`
   - `npm run lint`
   - Browser-Smoke-Test
3. Erst nach lokal stabiler Phase Commit-/Push-Vorbereitung.
