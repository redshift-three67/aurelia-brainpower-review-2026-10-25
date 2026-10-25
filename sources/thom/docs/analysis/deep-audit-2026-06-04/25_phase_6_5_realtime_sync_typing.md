# Phase 6 Teil 5 — realtime-sync Edge Function Typ-Stabilisierung

Datum: 2026-06-14
Projekt: `/opt/radithoms`
Datei: `supabase/functions/realtime-sync/index.ts`

## Ziel

Fortsetzung von Phase 6: systematischer Abbau der verbleibenden `no-explicit-any` Errors nach Runtime-/Datenfluss-Risiko.

Priorisierter Kandidat war die Supabase Edge Function `realtime-sync`, weil sie an der WebSocket-/Realtime-Grenze liegt und folgende Echtzeit-Nachrichtentypen verteilt:

- `vector_update`
- `frequency_sync`
- `hardware_status`
- `session_event`
- `ping`/`pong`

## Ausgangsbefund

Gezielte ESLint-Prüfung vor der Änderung:

```text
/opt/radithoms/supabase/functions/realtime-sync/index.ts
  41:68  error  Unexpected any. Specify a different type
  63:69  error  Unexpected any. Specify a different type
  77:70  error  Unexpected any. Specify a different type
  90:68  error  Unexpected any. Specify a different type

✖ 4 problems (4 errors, 0 warnings)
```

## Root Cause

Die Handler für externe WebSocket-Payloads nutzten `any` für `data`:

```ts
function handleVectorUpdate(ws: WebSocket, clientId: string, data: any)
function handleFrequencySync(ws: WebSocket, clientId: string, data: any)
function handleHardwareStatus(ws: WebSocket, clientId: string, data: any)
function handleSessionEvent(ws: WebSocket, clientId: string, data: any)
```

Das verdeckte die lokale Nutzungsform der Nachrichtenfelder. Die Edge Function validiert die Payloads fachlich noch nicht streng, sondern leitet ausgewählte Felder als Realtime-Broadcast weiter. Deshalb war der sichere Minimalfix: schmale Payload-Interfaces an der Handler-Grenze ergänzen und JSON.parse als `RealtimeMessage` typisieren, ohne das Runtime-Verhalten zu verändern.

## Umsetzung

Ergänzte schmale Payload-Typen:

```ts
interface RealtimeMessage {
  type?: string;
  timestamp?: number;
  data?: unknown;
}

interface VectorUpdatePayload {
  vectorId?: unknown;
  dimensions?: unknown;
  trajectory?: unknown;
}

interface FrequencySyncPayload {
  frequency?: unknown;
  amplitude?: unknown;
  waveform?: unknown;
}

interface HardwareStatusPayload {
  devices?: { length?: number };
  metrics?: unknown;
}

interface SessionEventPayload {
  event?: unknown;
  sessionId?: unknown;
  payload?: unknown;
}
```

Handler-Signaturen wurden typisiert:

```ts
function handleVectorUpdate(ws: WebSocket, clientId: string, data: VectorUpdatePayload)
function handleFrequencySync(ws: WebSocket, clientId: string, data: FrequencySyncPayload)
function handleHardwareStatus(ws: WebSocket, clientId: string, data: HardwareStatusPayload)
function handleSessionEvent(ws: WebSocket, clientId: string, data: SessionEventPayload)
```

`JSON.parse` wurde an der Eingangsgrenze schmal typisiert:

```ts
const message = JSON.parse(event.data) as RealtimeMessage;
```

Die Switch-Dispatches casten auf den jeweils passenden Payload-Typ:

```ts
handleVectorUpdate(socket, clientId, message.data as VectorUpdatePayload);
handleFrequencySync(socket, clientId, message.data as FrequencySyncPayload);
handleHardwareStatus(socket, clientId, message.data as HardwareStatusPayload);
handleSessionEvent(socket, clientId, message.data as SessionEventPayload);
```

## Geändertes Verhalten

Beabsichtigt keine fachliche Runtime-Änderung.

Unverändert bleiben:

- CORS-Header.
- WebSocket-Upgrade-Verhalten.
- REST-Fallback `/status`.
- Client-ID-Generierung.
- `connected`, `client_joined`, `client_left` Broadcasts.
- `ping`/`pong` Latenzmessung.
- Broadcast-Felder und Payload-Struktur für alle bestehenden Eventtypen.
- Fehlerantwort bei unbekanntem Message-Typ.
- Fehlerantwort bei ungültigem JSON.

Wichtig: Es wurde bewusst keine neue strenge Payload-Validierung ergänzt, um keine bestehenden Clients zu brechen. Die Typisierung dokumentiert nur die aktuell konsumierten Felder.

## Verifikation

### Ziel-ESLint

```bash
npx eslint supabase/functions/realtime-sync/index.ts
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

### Deno/Supabase-CLI-Prüfung

```text
DENO_NOT_INSTALLED
SUPABASE_CLI_NOT_INSTALLED
```

Einordnung: Deno/Supabase CLI sind in dieser lokalen Umgebung nicht installiert. Deshalb wurde die Edge-Function-spezifische Prüfung über vorhandene Projekt-Gates (`eslint`, `tsc`, Build) durchgeführt. Es wurde keine erfolgreiche Deno-Ausführung behauptet.

### Production Build

```bash
npm run build
```

Ergebnis:

```text
✓ 3674 modules transformed.
✓ built in 5.53s
```

Bekannte, unveränderte Build-Hinweise:

```text
Browserslist data is 12 months old
Some chunks are larger than 500 kB after minification
```

### Gesamt-Lint nach Phase 6 Teil 5

```text
✖ 37 problems (24 errors, 13 warnings)
```

Vergleich zu Phase 6 Teil 4:

```text
Vorher: 41 problems (28 errors, 13 warnings)
Nachher: 37 problems (24 errors, 13 warnings)
Verbesserung: -4 errors, 0 neue warnings/errors
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

```text
VITE v5.4.21 ready in 171 ms
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
URL-Aufruf: http://127.0.0.1:5173/analyse?phase6_5=realtime-sync-edge-function
Redirect/Ziel: http://127.0.0.1:5173/login
Login-/Auth-Seite sichtbar
Console messages: []
JS errors: []
total_errors: 0
```

Der direkte Analysepfad ist erwartbar durch Auth/ProtectedRoute geschützt. Ohne Login wurde der geschützte Zugriff und die fehlerfreie Frontend-Runtime-Initialisierung geprüft.

## Ergebnis

Phase 6 Teil 5 ist abgeschlossen.

- `supabase/functions/realtime-sync/index.ts`: gezielter ESLint sauber.
- 4 `no-explicit-any` Errors entfernt.
- TypeScript sauber.
- Production Build sauber.
- Gesamt-Lint von 41 auf 37 Probleme verbessert.
- Browser-Smoke ohne Console-/JS-Fehler.
- Deno/Supabase CLI nicht verfügbar, daher nicht als ausgeführt behauptet.

## Nächster empfohlener Schritt

Weiter mit Phase 6 Teil 6 nach Runtime-/Datenfluss-Risiko:

1. `src/hooks/useRemedyDatabase.ts`
   - 5 `no-explicit-any` Errors.
   - Remedy-/Datenbank-Hook.

Danach:

2. `src/pages/KlientDashboard.tsx`
   - 5 `no-explicit-any` Errors.
   - Dashboard-/Client-Visualisierungsdatenfluss.

3. `src/hooks/useChreodeTracking.ts`
   - 3 `no-explicit-any` Errors.
   - Chreode-/Tracking-Hook.
