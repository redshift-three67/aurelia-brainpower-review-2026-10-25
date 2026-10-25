# Echtzeit-Hardware-Architektur – Technische Dokumentation

> **Stand:** 2026-03-06 | **Version:** 1.0  
> **Zielgruppe:** Entwickler mit Erfahrung in WebSocket, WebAudio, WebUSB/WebSerial

---

## Inhaltsverzeichnis

1. [Architektur-Übersicht](#1-architektur-übersicht)
2. [Schicht 1: Edge Functions (Server-Backend)](#2-schicht-1-edge-functions-server-backend)
3. [Schicht 2: Client-Services (Singleton-Pattern)](#3-schicht-2-client-services-singleton-pattern)
4. [Schicht 3: React Hooks (State-Binding)](#4-schicht-3-react-hooks-state-binding)
5. [Schicht 4: UI-Komponenten](#5-schicht-4-ui-komponenten)
6. [Datenfluss-Diagramme](#6-datenfluss-diagramme)
7. [Hardware-Entropie → Klienten-Vektor Pipeline](#7-hardware-entropie--klienten-vektor-pipeline)
8. [Externe Hardware (WebUSB / WebSerial)](#8-externe-hardware-webusb--webserial)
9. [Latenz-Messung & Monitoring](#9-latenz-messung--monitoring)
10. [Konfiguration & Umgebungsmodi](#10-konfiguration--umgebungsmodi)
11. [Dateiverzeichnis & Abhängigkeitsgraph](#11-dateiverzeichnis--abhängigkeitsgraph)

---

## 1. Architektur-Übersicht

Das System nutzt eine **dreistufige Echtzeit-Pipeline**:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Lovable Cloud (Deno Edge Functions)              │
│  ┌──────────────────────┐    ┌────────────────────────────┐        │
│  │  hardware-metrics    │    │  realtime-sync              │        │
│  │  (WebSocket Server)  │    │  (WebSocket Server)         │        │
│  │  Port: /functions/v1 │    │  Port: /functions/v1        │        │
│  │                      │    │                              │        │
│  │  • Metrik-Streaming  │    │  • Client-Registry           │        │
│  │  • Entropie-Berechn. │    │  • Broadcast (Vektor/Freq)   │        │
│  │  • Ping/Pong-Latenz  │    │  • Session-Events            │        │
│  │  • Konfig. REST-API  │    │  • Ping/Pong-Latenz          │        │
│  └──────────┬───────────┘    └──────────────┬───────────────┘        │
└─────────────┼───────────────────────────────┼───────────────────────┘
              │ WSS                           │ WSS
              ▼                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Browser Client (React/TypeScript)                │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Service-Schicht (Singletons)                               │    │
│  │  ┌─────────────────┐ ┌──────────────────────────────────┐   │    │
│  │  │SystemMonitorSvc │ │RealtimeSyncService               │   │    │
│  │  │(simulierte      │ │(WSS→realtime-sync Edge Fn)       │   │    │
│  │  │ Metriken)       │ │                                  │   │    │
│  │  └────────┬────────┘ └──────────────┬───────────────────┘   │    │
│  │           │           ┌──────────────┴───────────────────┐   │    │
│  │           │           │RealtimeHarmonizationService      │   │    │
│  │           │           │(WebAudio + AudioWorklet + WSS)   │   │    │
│  │           │           └──────────────┬───────────────────┘   │    │
│  │  ┌────────┴────────┐ ┌──────────────┴───────────────────┐   │    │
│  │  │HardwareDiscover │ │useServerHardwareMetrics (Hook)   │   │    │
│  │  │(WebUSB/Serial)  │ │(WSS→hardware-metrics Edge Fn)   │   │    │
│  │  └─────────────────┘ └──────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Hook-Schicht (React State)                                 │    │
│  │  useSystemMonitor │ useRealtimeSync │ useRealtimeHarmoniz.  │    │
│  │  useHardwareDiscovery │ useServerHardwareMetrics             │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  UI-Schicht                                                  │    │
│  │  SystemStatusDashboard │ RealtimeStatusWidget                │    │
│  │  ClientVectorInterface │ FrequencyOutputModule               │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Schicht 1: Edge Functions (Server-Backend)

### 2.1 `hardware-metrics` Edge Function

**Pfad:** `supabase/functions/hardware-metrics/index.ts`  
**Protokoll:** WebSocket (WSS) + REST-Fallback  
**JWT:** `verify_jwt = false` (in `supabase/config.toml`)

#### Zweck
Streamt simulierte Server-Hardware-Metriken (CPU, GPU, RAM, Netzwerk) und berechnet **Entropie-Werte** für die Klienten-Vektor-Ableitung.

#### Server-Konfiguration (hardcodiert)
```typescript
const SERVER_CONFIG = {
  cpu: { model: 'AMD Ryzen 5 9600X', cores: 6, threads: 12, baseFrequency: 3.9, boostFrequency: 5.4 },
  gpu: { model: 'NVIDIA RTX 4000 SFF Ada', vram: 20, cudaCores: 6144 },
  ram: { total: 64, type: 'DDR5', speed: 5600 },
};
```

#### WebSocket-Nachrichten (Server → Client)

| `type` | Payload | Intervall |
|--------|---------|-----------|
| `config` | `{ clientId, server: SERVER_CONFIG }` | Einmalig bei `onopen` |
| `metrics` | `{ metrics: { cpu, gpu, ram, network }, entropy: { cpuEntropy, gpuEntropy, ramEntropy, latencyEntropy, combined } }` | **500ms** (konfigurierbar 100–5000ms) |
| `pong` | `{ clientTimestamp, serverTimestamp }` | Auf `ping`-Request |
| `interval_updated` | `{ intervalMs }` | Auf `set_interval`-Request |

#### WebSocket-Nachrichten (Client → Server)

| `type` | Payload | Zweck |
|--------|---------|-------|
| `ping` | `{ timestamp }` | Latenz-Messung |
| `get_metrics` | – | Einmalige Metrik-Abfrage |
| `set_interval` | `{ intervalMs }` | Streaming-Intervall ändern |

#### Entropie-Berechnung
```typescript
entropy: {
  cpuEntropy:     cpuUsage * cpuTemp * 0.01,     // Dimensionslos
  gpuEntropy:     gpuUsage * gpuTemp * 0.01,
  ramEntropy:     ramUsed * 0.1,
  latencyEntropy: networkLatency * 10,
  combined:       cpuUsage * 0.3 + gpuUsage * 0.3 + ramUsed * 0.2 + networkLatency * 2,
}
```

#### REST-Endpunkte (Fallback)
- `GET .../hardware-metrics/metrics` → Einmalige JSON-Antwort mit Metriken
- `GET .../hardware-metrics/config` → Server-Konfiguration

#### Metrik-Simulation
Die Metriken nutzen **deterministische Oszillationen** (`Math.sin(Date.now() / T)`) überlagert mit Rauschen für realistische Varianz. In Produktion würden echte `/proc/stat`, `nvidia-smi` etc. ausgelesen.

---

### 2.2 `realtime-sync` Edge Function

**Pfad:** `supabase/functions/realtime-sync/index.ts`  
**Protokoll:** WebSocket (WSS) + REST-Fallback  
**JWT:** `verify_jwt = false`

#### Zweck
Multi-Client-Broadcast-Hub für Echtzeit-Synchronisation von Vektor-Updates, Frequenz-Konfigurationen, Hardware-Status und Session-Events.

#### Verbindungs-Registry
```typescript
const connections = new Map<string, WebSocket>();
// Client-ID Format: `client-${Date.now()}-${random9chars}`
```

#### WebSocket-Nachrichten (Server → Client)

| `type` | Payload | Trigger |
|--------|---------|---------|
| `connected` | `{ clientId, serverTime, connectedClients }` | Bei `onopen` |
| `client_joined` | `{ clientId, totalClients }` | Broadcast bei neuem Client |
| `client_left` | `{ clientId, totalClients }` | Broadcast bei Disconnect |
| `pong` | `{ clientId, clientTimestamp, serverTimestamp, latency }` | Auf `ping` |
| `vector_update` | `{ clientId, vectorId, dimensions, trajectory }` | Broadcast (excl. Sender) |
| `vector_update_ack` | `{ vectorId, timestamp }` | Bestätigung an Sender |
| `frequency_sync` | `{ clientId, frequency, amplitude, waveform }` | Broadcast |
| `hardware_status` | `{ clientId, devices, metrics }` | Broadcast |
| `session_event` | `{ clientId, event, sessionId, payload }` | Broadcast |
| `error` | `{ message }` | Bei ungültigen Nachrichten |

#### WebSocket-Nachrichten (Client → Server)

| `type` | `data`-Payload |
|--------|----------------|
| `ping` | `{ timestamp }` |
| `vector_update` | `{ vectorId, dimensions, trajectory, metadata }` |
| `frequency_sync` | `{ frequency, amplitude, waveform }` |
| `hardware_status` | `{ devices: [{id,name,type,status}], metrics: {cpu,gpu,memory,latency} }` |
| `session_event` | `{ event, sessionId, payload }` |

#### REST-Fallback
- `GET .../realtime-sync/status` → `{ status: 'online', connections: N, timestamp }`

---

## 3. Schicht 2: Client-Services (Singleton-Pattern)

Alle Services sind als **Singleton-Klassen** implementiert und werden einmalig instanziiert.

### 3.1 `RealtimeSyncService`

**Pfad:** `src/services/realtime/RealtimeSyncService.ts`  
**Export:** `realtimeSync` (Singleton)

#### Verbindungsmanagement
```typescript
private readonly wsUrl = 'wss://yoryyvfuscyfumeseour.supabase.co/functions/v1/realtime-sync';
```

- **Auto-Reconnect:** Exponentielles Backoff, max 5 Versuche (`delay * 2^(attempt-1)`, Start: 1000ms)
- **Connection Timeout:** 10 Sekunden
- **Ping-Intervall:** Alle 2 Sekunden

#### Latenz-Statistiken
```typescript
interface LatencyStats {
  current: number;  // Aktuelle One-Way-Latenz (RTT/2)
  min: number;
  max: number;
  avg: number;      // Gleitender Durchschnitt
  samples: number[]; // Letzte 50 Samples
}
```

#### API-Methoden
| Methode | Signatur | Beschreibung |
|---------|----------|--------------|
| `connect()` | `Promise<void>` | WSS-Verbindung herstellen |
| `disconnect()` | `void` | Verbindung trennen (Code 1000) |
| `sendVectorUpdate()` | `(vector: ClientVector) → boolean` | 5D-Vektor broadcasten |
| `sendFrequencySync()` | `(config: FrequencyOutput) → boolean` | Frequenz-Konfig broadcasten |
| `sendHardwareStatus()` | `(devices, metrics) → boolean` | Hardware-Status broadcasten |
| `sendSessionEvent()` | `(event, sessionId, payload?) → boolean` | Session-Event broadcasten |
| `addEventListener()` | `(cb: RealtimeEventCallback) → void` | Event-Listener registrieren |
| `removeEventListener()` | `(cb) → void` | Event-Listener entfernen |

---

### 3.2 `RealtimeHarmonizationService`

**Pfad:** `src/services/realtime/RealtimeHarmonizationService.ts`  
**Export:** `RealtimeHarmonizationService` (Singleton)

#### Audio-Pipeline
```
AudioWorkletNode("frequency-generator")
    │
    ├── GainNode (Lautstärke + Fade In/Out 100ms)
    │       │
    │       ├── AnalyserNode (FFT: 2048, für Visualisierung)
    │       │       │
    │       │       └── AudioContext.destination (Speaker)
    │       │
    └── [Fallback: OscillatorNode wenn AudioWorklet nicht verfügbar]
```

#### AudioWorklet-Prozessor (`FrequencyGeneratorProcessor`)
- **Sample Rate:** 48000 Hz
- **Latency Hint:** `interactive`
- **Wellenformen:** `sine`, `square`, `triangle`, `sawtooth`, `harmonic`
- **FM-Modulation:** Konfigurierbare Modulationsfrequenz und -tiefe
- **Harmonische Reihe:** Konfigurierbare Amplitude-Koeffizienten `[1, 0.5, 0.25, 0.125]`

#### Kommunikation mit AudioWorklet
```typescript
// Parameter-Update via MessagePort (latenzarm)
workletNode.port.postMessage({
  frequency: 432.0,
  amplitude: 0.7,
  waveform: 'harmonic',
  harmonics: [1, 0.5, 0.25, 0.125, 0.0625],
  modulationFreq: 7.83,    // Schumann-Resonanz
  modulationDepth: 0.1,
});
```

#### Server-Verbindung (innerhalb des Service)
Öffnet eine **zweite, eigenständige WebSocket-Verbindung** zu `realtime-sync`:
```typescript
const wsUrl = `${VITE_SUPABASE_URL.replace('https', 'wss')}/functions/v1/realtime-sync`;
```

**Empfängt:**
- `hardware_status` → Updates zu `serverStatus` (CPU/GPU/Latenz)
- `frequency_calculated` → GPU-berechnete Frequenzen werden direkt an den AudioWorklet weitergeleitet

**Sendet:**
- `frequency_sync` → Aktuelle Frequenzkonfiguration
- `gpu_calculation_request` → GPU-beschleunigte Harmonik-Berechnung

#### GPU-Berechnung (Request/Response via WSS)
```typescript
async requestGPUCalculation(params: {
  baseFrequency: number;
  targetFrequency: number;
  harmonicCount: number;
  calculationType: 'harmonic_series' | 'resonance_field' | 'cusp_trajectory';
}): Promise<number[] | null>
```

**Fallback** (lokal, wenn Server nicht verbunden):
- `harmonic_series`: `baseFreq * i` (i = 1..N)
- `resonance_field`: `baseFreq * φ^(i-1)` (φ = 1.618, Golden Ratio)
- `cusp_trajectory`: `baseFreq * fib[i]` (Fibonacci-Sequenz)

#### Frequenz-Historie
- Max 1000 Einträge: `{ timestamp, frequency, amplitude }[]`
- Abrufbar via `getFrequencyHistory()`

---

### 3.3 `SystemMonitorService`

**Pfad:** `src/services/hardware/SystemMonitorService.ts`  
**Export:** `systemMonitor` (Singleton)

#### Zwei Umgebungsmodi

| Modus | CPU | GPU | RAM | Netzwerk |
|-------|-----|-----|-----|----------|
| `development` | AMD Ryzen 9 8945HS (8C/16T) | AMD Radeon 780M (370MB shared) | 16 GB DDR5-7500 | WiFi 6E 1 Gbit |
| `production` | AMD Ryzen 5 9600X (6C/12T) | NVIDIA RTX 4000 SFF Ada (20GB, 6144 CUDA, 192 Tensor) | 128 GB DDR5-5600 | 2x 1 Gbit Ethernet |

#### Metrik-Simulation (Browser-seitig)
Die Metriken werden **im Browser simuliert** (nicht vom Server gestreamt). Die Methoden `simulateUsage()`, `simulateTemperature()` etc. generieren realistische Schwankungen um einen Basewert herum.

```typescript
// Beispiel: CPU-Auslastung
simulateUsage(min: 15, max: 45): number {
  const base = (min + max) / 2;
  const variation = (max - min) / 4;
  return Math.round(base + (Math.random() - 0.5) * variation * 2);
}
```

**Browser Performance API Integration:**
```typescript
const performanceMemory = (performance as any).memory;
// Nutzt echte JS-Heap-Größe wenn verfügbar (nur Chrome)
```

#### Echte Latenz-Messungen
```typescript
measureWebSocketLatency(wsUrl: string): Promise<number>  // Öffnet WS, misst bis onopen
measureNetworkLatency(endpoint: string): Promise<number>  // fetch HEAD, no-cors
```

---

### 3.4 `HardwareDiscoveryService`

**Pfad:** `src/services/hardware/HardwareDiscoveryService.ts`  
**Export:** `hardwareDiscovery` (Singleton)

#### Unterstützte Browser-APIs
- **WebUSB** (`navigator.usb`) — für USB-DACs (Audio-Ausgabe)
- **WebSerial** (`navigator.serial`) — für Frequenzgeneratoren (z.B. Spooky2), Mikrocontroller

#### Geräte-Registry
```typescript
private devices: Map<string, ExternalDevice> = new Map();
private usbDevices: Map<string, USBDevice> = new Map();
private serialPorts: Map<string, SerialPort> = new Map();
```

#### Device-ID-Generierung
```typescript
USB:    `usb-${vendorId.hex}-${productId.hex}-${serialNumber}`
Serial: `serial-${usbVendorId.hex}-${usbProductId.hex}`
```

#### Geräte-Erkennung
Import aus `deviceProfiles.ts`:
```typescript
identifyDevice(vendorId, productId): DeviceProfile | null  // Bekannte Geräte
guessDeviceType(vendorId): DeviceType                       // Heuristik nach Vendor
```

#### Vordefinierte USB-Filter (aus `deviceProfiles.ts`)
- `USB_DAC_FILTERS` — Audio-DAC-Geräte
- `FREQUENCY_GENERATOR_FILTERS` — Frequenzgeneratoren
- `MICROCONTROLLER_FILTERS` — Arduino, ESP32 etc.

#### Auto-Scan
- **Intervall:** 5 Sekunden
- **Aktion:** `lastSeen`-Timestamp aktualisieren
- Event-Listener auf `navigator.usb` (`connect`/`disconnect`) und `navigator.serial` (`connect`/`disconnect`)

#### Geräte-Anforderung (User-Geste erforderlich)
```typescript
requestUSBDAC(): Promise<ExternalDevice | null>           // USB-DAC auswählen
requestFrequencyGenerator(): Promise<ExternalDevice | null> // Serial Freq-Generator
requestMicrocontroller(): Promise<ExternalDevice | null>   // Serial µController
requestAnyUSBDevice(): Promise<ExternalDevice | null>      // Beliebiges USB-Gerät
requestAnySerialPort(): Promise<ExternalDevice | null>     // Beliebiger Serial-Port
```

#### Port/Device-Öffnung
```typescript
openUSBDevice(deviceId): Promise<USBDevice | null>
openSerialPort(deviceId, options?: SerialOptions): Promise<SerialPort | null>
// Default: { baudRate: 115200 }
```

---

## 4. Schicht 3: React Hooks (State-Binding)

### 4.1 `useServerHardwareMetrics`

**Pfad:** `src/hooks/useServerHardwareMetrics.ts`

Direkte WebSocket-Verbindung zu `hardware-metrics` Edge Function.

```typescript
interface UseServerHardwareMetricsReturn {
  isConnected: boolean;
  metrics: ServerHardwareMetrics | null;  // CPU/GPU/RAM/Network
  entropy: EntropyData | null;            // cpuEntropy, gpuEntropy, combined...
  serverConfig: ServerConfig | null;      // Statische Server-Specs
  latency: number;                        // Ping-Pong RTT
  connect: () => void;
  disconnect: () => void;
  getLatestMetrics: () => ServerHardwareMetrics | null;   // Ref-basiert (kein Re-Render)
  getLatestEntropy: () => EntropyData | null;             // Ref-basiert
}
```

**WebSocket-URL-Konstruktion:**
```typescript
const wsUrl = VITE_SUPABASE_URL.replace('https://', 'wss://').replace('http://', 'ws://');
new WebSocket(`${wsUrl}/functions/v1/hardware-metrics`);
```

**Auto-Reconnect:** 3 Sekunden nach `onclose`  
**Ping-Intervall:** 5 Sekunden

---

### 4.2 `useRealtimeSync`

**Pfad:** `src/hooks/useRealtimeSync.ts`

Wrapper um `RealtimeSyncService` Singleton.

```typescript
interface UseRealtimeSyncReturn {
  isConnected: boolean;
  clientId: string | null;
  latency: LatencyStats;           // { current, min, max, avg, samples[] }
  connectedClients: number;
  lastEvent: RealtimeEvent | null;
  connect: () => Promise<void>;
  disconnect: () => void;
  sendVectorUpdate: (vector: ClientVector) => boolean;
  sendFrequencySync: (config: FrequencyOutput) => boolean;
  sendHardwareStatus: (devices, metrics) => boolean;
  sendSessionEvent: (event, sessionId, payload?) => boolean;
}
```

---

### 4.3 `useRealtimeHarmonization`

**Pfad:** `src/hooks/useRealtimeHarmonization.ts`

Wrapper um `RealtimeHarmonizationService` Singleton.

```typescript
interface RealtimeHarmonizationState {
  isInitialized: boolean;
  isPlaying: boolean;
  currentFrequency: number;
  currentAmplitude: number;
  serverStatus: ServerHardwareStatus;  // { cpuUsage, gpuUsage, hardwareType }
  frequencySpectrum: Uint8Array;       // FFT-Daten (requestAnimationFrame-Loop)
  waveform: Uint8Array;               // Time-Domain-Daten
}
```

**Visualisierungs-Loop:** Läuft via `requestAnimationFrame` solange `isPlaying === true`.

---

### 4.4 `useSystemMonitor`

**Pfad:** `src/hooks/useSystemMonitor.ts`

Wrapper um `SystemMonitorService` Singleton.

```typescript
interface UseSystemMonitorReturn {
  serverConfig: ServerHardware;          // Statische Konfiguration
  currentMetrics: SystemMetrics | null;  // CPU/GPU/RAM/Latenz
  isMonitoring: boolean;
  environmentMode: EnvironmentMode;      // 'development' | 'production'
  setEnvironmentMode: (mode) => void;
  startMonitoring: (intervalMs?) => void;  // Default: 1000ms
  stopMonitoring: () => void;
  measureWebSocketLatency: (wsUrl) => Promise<number>;
  measureNetworkLatency: (endpoint) => Promise<number>;
}
```

---

### 4.5 `useHardwareDiscovery`

**Pfad:** `src/hooks/useHardwareDiscovery.ts`

Wrapper um `HardwareDiscoveryService` Singleton.

---

## 5. Schicht 4: UI-Komponenten

### 5.1 `SystemStatusDashboard`

**Pfad:** `src/components/SystemStatusDashboard.tsx`

Verwendet: `useSystemMonitor` + `useHardwareDiscovery`

**Layout:** 2-Spalten Grid
- **Links:** Server-Hardware (CPU/GPU/RAM/Storage/Network) mit Echtzeit-Metriken, Fortschrittsbalken, Temperaturanzeige
- **Rechts:** Hardware-Discovery (WebUSB/WebSerial-Status, Geräte-Buttons, verbundene Geräte-Liste)

**Auto-Start:** Monitoring startet bei Mount mit 1000ms Intervall.

---

### 5.2 `RealtimeStatusWidget`

**Pfad:** `src/components/RealtimeStatusWidget.tsx`

Verwendet: `useRealtimeSync`

**Position:** Fixed, bottom-right (`fixed bottom-4 right-4 z-50`)  
**Auto-Connect:** Bei Mount  
**Anzeige:** Verbindungsstatus, aktuelle Latenz (farbcodiert), Min/Avg/Max Statistiken, Anzahl verbundener Clients, Client-ID (letzte 8 Zeichen)

**Latenz-Farbcodierung:**
| Latenz | Farbe |
|--------|-------|
| < 5ms | 🟢 Grün |
| < 20ms | 🟡 Gelb |
| < 50ms | 🟠 Orange |
| ≥ 50ms | 🔴 Rot |

---

### 5.3 `ClientVectorInterface`

**Pfad:** `src/components/ClientVectorInterface.tsx`

Verwendet: `useRealtimeHarmonization` + `useClientDatabase`

**Entropie-Integration:** Die 5D-Zustandsdimensionen (`physical`, `emotional`, `mental`, `energy`, `stress`) werden automatisch aus der Server-Hardware-Entropie abgeleitet. Manuelle Slider ermöglichen optionale Überschreibung.

---

## 6. Datenfluss-Diagramme

### 6.1 Hardware-Metriken-Streaming

```
hardware-metrics Edge Fn (Deno)
  │  [WebSocket, 500ms Intervall]
  │  { type: 'metrics', metrics: {...}, entropy: {...} }
  ▼
useServerHardwareMetrics (Hook)
  │  setMetrics(data.metrics)
  │  setEntropy(data.entropy)
  ▼
ClientVectorInterface (Komponente)
  │  entropy.combined → Dimension-Mapping
  │  physical  = f(cpuEntropy)
  │  emotional = f(gpuEntropy)
  │  mental    = f(ramEntropy)
  │  energy    = f(combined)
  │  stress    = f(latencyEntropy)
  ▼
ThomVectorEngine.analyzeVector(dimensions)
  │  → VectorAnalysis { cusp, attractor, trajectory, frequencies }
  ▼
MeridianDiagnosisPanel → Behandlung → Harmonisierung
```

### 6.2 Realtime-Sync Broadcast

```
Client A                    realtime-sync Edge Fn              Client B
  │                                │                              │
  │── vector_update ──────────────►│                              │
  │                                │── vector_update ────────────►│
  │◄── vector_update_ack ─────────│                              │
  │                                │                              │
  │── frequency_sync ─────────────►│                              │
  │                                │── frequency_sync ───────────►│
  │                                │                              │
  │── ping ────────────────────────►│                              │
  │◄── pong (mit Latenzmessung) ──│                              │
```

### 6.3 Audio-Harmonisierung

```
RealtimeHarmonizationService
  │
  ├── WebSocket → realtime-sync (Frequenz-Sync + GPU-Requests)
  │       │
  │       └── GPU-berechnete Harmonics → AudioWorklet.port.postMessage()
  │
  ├── AudioContext (48kHz, interactive latency)
  │       │
  │       ├── AudioWorkletNode("frequency-generator")
  │       │       │  • Wellenform-Generierung (sine/square/triangle/sawtooth/harmonic)
  │       │       │  • FM-Modulation
  │       │       │  • 128 Samples pro Process-Block
  │       │       │
  │       │       └──► GainNode (Amplitude + Fade)
  │       │               │
  │       │               ├──► AnalyserNode (FFT 2048)
  │       │               │       │
  │       │               │       └──► getFrequencyData() / getWaveformData()
  │       │               │           (requestAnimationFrame Loop für UI)
  │       │               │
  │       │               └──► AudioContext.destination (Lautsprecher)
  │       │
  │       └── [Fallback: OscillatorNode wenn Worklet fehlschlägt]
  │
  └── Frequenz-Historie (max 1000 Einträge)
```

---

## 7. Hardware-Entropie → Klienten-Vektor Pipeline

### Datenfluss

```
Edge Function (hardware-metrics)
  │  Generiert: cpuEntropy, gpuEntropy, ramEntropy, latencyEntropy, combined
  ▼
useServerHardwareMetrics Hook
  │  entropy: EntropyData
  ▼
ClientVectorInterface
  │  Mapping-Funktion (alle 2s via useEffect):
  │
  │  physical  = normalize(cpuEntropy,     0, 50) * 100   // CPU-Last → Körperlicher Zustand
  │  emotional = normalize(gpuEntropy,     0, 50) * 100   // GPU-Last → Emotionaler Zustand
  │  mental    = normalize(ramEntropy,     0, 10) * 100   // RAM-Nutzung → Mentaler Zustand
  │  energy    = normalize(combined,       0, 80) * 100   // Gesamt-Entropie → Energieniveau
  │  stress    = normalize(latencyEntropy, 0, 50) * 100   // Latenz → Stressniveau
  │
  ▼
ThomVectorEngine.analyzeVector([physical, emotional, mental, energy, stress])
  │  → VectorAnalysis:
  │     cusp: CuspType
  │     trajectory: VectorTrajectory
  │     attractorDistance: number
  │     recommendedFrequencies: RecommendedFrequency[]
```

### Manueller Override
Der Therapeut kann den automatischen Modus deaktivieren (`manualOverride = true`) und die 5 Dimensionen über Slider (0–100) direkt setzen.

---

## 8. Externe Hardware (WebUSB / WebSerial)

### Unterstützte Geräte-Typen

| Typ | API | Beispielgeräte |
|-----|-----|----------------|
| `usb-dac` | WebUSB | USB Audio DACs |
| `frequency-generator` | WebSerial | Spooky2, Rife-Generatoren |
| `microcontroller` | WebSerial | Arduino, ESP32 |
| `biosensor` | WebUSB/Serial | HRV/GSR-Sensoren |

### Lebenszyklus eines externen Geräts

```
1. Browser prüft API-Verfügbarkeit (navigator.usb / navigator.serial)
2. Autorisierte Geräte werden bei Init gelesen (getDevices() / getPorts())
3. User-Geste → requestDevice() / requestPort() → Browser-Picker
4. Gerät wird registriert: devices.set(id, ExternalDevice)
5. Geräte-Events werden emittiert (connect/disconnect)
6. Port/Device öffnen: openSerialPort(id, {baudRate: 115200})
7. Auto-Scan alle 5s aktualisiert lastSeen-Timestamps
8. Bei Disconnect: Event + Cleanup
```

### Browser-Kompatibilität
- **WebUSB:** Chrome 61+, Edge 79+, Opera 48+ (kein Firefox/Safari)
- **WebSerial:** Chrome 89+, Edge 89+, Opera 75+ (kein Firefox/Safari)

---

## 9. Latenz-Messung & Monitoring

### Drei unabhängige Latenz-Messmethoden

| Methode | Service | Intervall | Messung |
|---------|---------|-----------|---------|
| Realtime-Sync Ping | `RealtimeSyncService` | 2s | RTT/2 (one-way estimate) |
| Hardware-Metrics Ping | `useServerHardwareMetrics` | 5s | Client→Server→Client RTT |
| SystemMonitor | `SystemMonitorService` | On-demand | WS-open Latenz / fetch HEAD |

### Realtime-Sync Latenz-Berechnung (detailliert)
```typescript
// Client sendet:
{ type: 'ping', timestamp: Date.now() }

// Server antwortet:
{ type: 'pong', clientTimestamp, serverTimestamp, latency: serverTimestamp - clientTimestamp }

// Client berechnet:
const roundTrip = Date.now() - message.clientTimestamp;
const oneWay = roundTrip / 2;

// Statistiken:
latencyStats.current = oneWay;
latencyStats.min = Math.min(latencyStats.min, oneWay);
latencyStats.max = Math.max(latencyStats.max, oneWay);
latencyStats.samples.push(oneWay);  // Max 50 Samples
latencyStats.avg = samples.reduce((a, b) => a + b, 0) / samples.length;
```

---

## 10. Konfiguration & Umgebungsmodi

### `supabase/config.toml`
```toml
[functions.realtime-sync]
verify_jwt = false

[functions.hardware-metrics]
verify_jwt = false
```

### Environment Variables
```env
VITE_SUPABASE_URL=https://yoryyvfuscyfumeseour.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=eyJhbG...
VITE_SUPABASE_PROJECT_ID=yoryyvfuscyfumeseour
```

### SystemMonitor Modi
- **`development`**: Nutzt ASUS Vivobook S 16 Specs (Ryzen 9 8945HS, Radeon 780M, 16GB)
- **`production`**: Nutzt GPU Server M G1 Specs (Ryzen 5 9600X, RTX 4000, 128GB)
- Umschaltbar via `useSystemMonitor().setEnvironmentMode('production')`

---

## 11. Dateiverzeichnis & Abhängigkeitsgraph

### Dateien

```
src/
├── types/
│   ├── hardware.ts                          # Alle Hardware-Interfaces
│   └── webapis.d.ts                         # WebUSB/WebSerial TypeScript-Deklarationen
│
├── services/
│   ├── hardware/
│   │   ├── index.ts                         # Barrel Export
│   │   ├── HardwareDiscoveryService.ts      # WebUSB/WebSerial Singleton
│   │   ├── SystemMonitorService.ts          # Browser-Metriken Singleton
│   │   └── deviceProfiles.ts               # Bekannte USB-Vendor/Product-IDs
│   │
│   └── realtime/
│       ├── RealtimeSyncService.ts           # WSS Client Singleton (→ realtime-sync EF)
│       └── RealtimeHarmonizationService.ts  # WebAudio + WSS Singleton
│
├── hooks/
│   ├── useSystemMonitor.ts                  # → SystemMonitorService
│   ├── useHardwareDiscovery.ts              # → HardwareDiscoveryService
│   ├── useRealtimeSync.ts                   # → RealtimeSyncService
│   ├── useRealtimeHarmonization.ts          # → RealtimeHarmonizationService
│   └── useServerHardwareMetrics.ts          # Eigener WSS Client (→ hardware-metrics EF)
│
├── components/
│   ├── SystemStatusDashboard.tsx            # Server-Hardware + Device-Discovery UI
│   ├── RealtimeStatusWidget.tsx             # Latenz-Widget (fixed, bottom-right)
│   ├── ClientVectorInterface.tsx            # Entropie → Vektor-Mapping + UI
│   └── FrequencyOutputModule.tsx            # Frequenz-Ausgabe-Steuerung
│
supabase/
├── config.toml                              # JWT-Settings für Edge Functions
└── functions/
    ├── hardware-metrics/index.ts            # Metrik-Streaming Edge Function
    └── realtime-sync/index.ts               # Multi-Client-Broadcast Edge Function
```

### Abhängigkeitsgraph

```
types/hardware.ts
  ▲
  │ import
  ├── services/hardware/SystemMonitorService.ts
  ├── services/hardware/HardwareDiscoveryService.ts
  ├── services/realtime/RealtimeSyncService.ts
  ├── services/realtime/RealtimeHarmonizationService.ts
  │       ▲
  │       │ import
  │       └── hooks/useRealtimeHarmonization.ts
  │               ▲
  │               └── components/ClientVectorInterface.tsx
  │
  ├── hooks/useSystemMonitor.ts
  │       ▲
  │       └── components/SystemStatusDashboard.tsx
  │
  ├── hooks/useRealtimeSync.ts
  │       ▲
  │       └── components/RealtimeStatusWidget.tsx
  │
  └── hooks/useServerHardwareMetrics.ts (standalone WSS)
          ▲
          └── components/ClientVectorInterface.tsx
```

---

## Bekannte Einschränkungen

1. **Metriken sind simuliert:** Sowohl `hardware-metrics` Edge Function als auch `SystemMonitorService` generieren simulierte Werte. In Produktion müssten echte OS-Level-Metriken (`/proc/stat`, `nvidia-smi`) über einen nativen Agent bereitgestellt werden.

2. **GPU-Berechnung via WSS nicht implementiert:** Die `gpu_calculation_request`-Nachricht wird vom `realtime-sync` Edge Function nicht verarbeitet (fällt in `default` → Error). Der lokale Fallback (`calculateHarmonicsLocally`) wird immer genutzt.

3. **Doppelte WebSocket-Verbindungen:** `RealtimeHarmonizationService` öffnet eine eigenständige Verbindung zu `realtime-sync`, unabhängig von `RealtimeSyncService`. Bei gleichzeitiger Nutzung existieren zwei parallele WSS-Verbindungen zur selben Edge Function.

4. **WebUSB/WebSerial nur Chromium:** Firefox und Safari unterstützen weder WebUSB noch WebSerial.

5. **Kein echtes Server-Side-Rendering:** Die `useServerHardwareMetrics` Hook-URL ist hardcodiert via `VITE_SUPABASE_URL`.
