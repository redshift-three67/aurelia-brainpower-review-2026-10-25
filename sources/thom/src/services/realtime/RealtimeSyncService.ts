// Realtime-Sync Client Service für NLS-Feldengine
// WebSocket-basierte Echtzeit-Kommunikation

import type { ClientVector, SystemMetrics, FrequencyOutput, ExternalDevice } from '@/types/hardware';

export type RealtimeEventType = 
  | 'connected'
  | 'disconnected'
  | 'pong'
  | 'vector_update'
  | 'vector_update_ack'
  | 'frequency_sync'
  | 'hardware_status'
  | 'session_event'
  | 'client_joined'
  | 'client_left'
  | 'error';

export interface RealtimeEvent {
  type: RealtimeEventType;
  clientId?: string;
  timestamp: number;
  data?: unknown;
}

export interface LatencyStats {
  current: number;
  min: number;
  max: number;
  avg: number;
  samples: number[];
}

type RealtimeEventCallback = (event: RealtimeEvent) => void;

class RealtimeSyncService {
  private ws: WebSocket | null = null;
  private clientId: string | null = null;
  private listeners: Set<RealtimeEventCallback> = new Set();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private pingInterval: ReturnType<typeof setInterval> | null = null;
  private latencyStats: LatencyStats = {
    current: 0,
    min: Infinity,
    max: 0,
    avg: 0,
    samples: [],
  };
  private isConnecting = false;
  
  // Supabase Edge Function URL
  private readonly wsUrl = 'wss://yoryyvfuscyfumeseour.supabase.co/functions/v1/realtime-sync';

  // Verbindungsstatus
  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  get currentClientId(): string | null {
    return this.clientId;
  }

  get latency(): LatencyStats {
    return { ...this.latencyStats };
  }

  // Event-Listener
  addEventListener(callback: RealtimeEventCallback): void {
    this.listeners.add(callback);
  }

  removeEventListener(callback: RealtimeEventCallback): void {
    this.listeners.delete(callback);
  }

  private emit(event: RealtimeEvent): void {
    this.listeners.forEach(callback => callback(event));
  }

  // Verbindung herstellen
  async connect(): Promise<void> {
    if (this.isConnected || this.isConnecting) {
      console.log('[RealtimeSync] Already connected or connecting');
      return;
    }

    this.isConnecting = true;
    console.log('[RealtimeSync] Connecting to:', this.wsUrl);

    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.wsUrl);

        this.ws.onopen = () => {
          console.log('[RealtimeSync] WebSocket connected');
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          this.startPingInterval();
          resolve();
        };

        this.ws.onmessage = (event) => {
          this.handleMessage(event.data);
        };

        this.ws.onclose = (event) => {
          console.log('[RealtimeSync] WebSocket closed:', event.code, event.reason);
          this.handleDisconnect();
        };

        this.ws.onerror = (error) => {
          console.error('[RealtimeSync] WebSocket error:', error);
          this.isConnecting = false;
          reject(error);
        };

        // Timeout für Verbindung
        setTimeout(() => {
          if (this.isConnecting) {
            this.isConnecting = false;
            this.ws?.close();
            reject(new Error('Connection timeout'));
          }
        }, 10000);

      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  // Verbindung trennen
  disconnect(): void {
    this.stopPingInterval();
    
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    
    this.clientId = null;
    this.emit({ type: 'disconnected', timestamp: Date.now() });
  }

  // Nachricht verarbeiten
  private handleMessage(data: string): void {
    try {
      const message = JSON.parse(data);
      const timestamp = Date.now();

      console.log('[RealtimeSync] Received:', message.type);

      switch (message.type) {
        case 'connected':
          this.clientId = message.clientId;
          this.emit({
            type: 'connected',
            clientId: message.clientId,
            timestamp,
            data: {
              serverTime: message.serverTime,
              connectedClients: message.connectedClients,
            },
          });
          break;

        case 'pong':
          this.handlePong(message);
          break;

        case 'vector_update':
        case 'vector_update_ack':
        case 'frequency_sync':
        case 'hardware_status':
        case 'session_event':
        case 'client_joined':
        case 'client_left':
        case 'error':
          this.emit({
            type: message.type,
            clientId: message.clientId,
            timestamp: message.timestamp || timestamp,
            data: message,
          });
          break;

        default:
          console.log('[RealtimeSync] Unknown message type:', message.type);
      }
    } catch (error) {
      console.error('[RealtimeSync] Error parsing message:', error);
    }
  }

  // Disconnect behandeln
  private handleDisconnect(): void {
    this.stopPingInterval();
    this.clientId = null;
    
    this.emit({ type: 'disconnected', timestamp: Date.now() });

    // Auto-Reconnect
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
      
      console.log(`[RealtimeSync] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        this.connect().catch(console.error);
      }, delay);
    }
  }

  // Ping-Interval starten
  private startPingInterval(): void {
    this.stopPingInterval();
    
    // Ping alle 2 Sekunden für Latenz-Messung
    this.pingInterval = setInterval(() => {
      this.sendPing();
    }, 2000);

    // Initialer Ping
    this.sendPing();
  }

  private stopPingInterval(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  // Ping senden
  private sendPing(): void {
    if (!this.isConnected) return;

    this.send({
      type: 'ping',
      timestamp: Date.now(),
    });
  }

  // Pong verarbeiten und Latenz berechnen
  private handlePong(message: { clientTimestamp: number; serverTimestamp: number; latency: number }): void {
    const now = Date.now();
    const roundTrip = now - message.clientTimestamp;
    const oneWay = roundTrip / 2;

    // Latenz-Statistiken aktualisieren
    this.latencyStats.current = oneWay;
    this.latencyStats.min = Math.min(this.latencyStats.min, oneWay);
    this.latencyStats.max = Math.max(this.latencyStats.max, oneWay);
    
    // Samples begrenzen (letzte 50)
    this.latencyStats.samples.push(oneWay);
    if (this.latencyStats.samples.length > 50) {
      this.latencyStats.samples.shift();
    }
    
    // Durchschnitt berechnen
    this.latencyStats.avg = this.latencyStats.samples.reduce((a, b) => a + b, 0) / this.latencyStats.samples.length;

    this.emit({
      type: 'pong',
      timestamp: now,
      data: {
        latency: oneWay,
        roundTrip,
        stats: { ...this.latencyStats },
      },
    });
  }

  // Nachricht senden
  private send(message: object): boolean {
    if (!this.isConnected) {
      console.warn('[RealtimeSync] Cannot send - not connected');
      return false;
    }

    try {
      this.ws!.send(JSON.stringify(message));
      return true;
    } catch (error) {
      console.error('[RealtimeSync] Send error:', error);
      return false;
    }
  }

  // Vektor-Update senden
  sendVectorUpdate(vector: ClientVector): boolean {
    return this.send({
      type: 'vector_update',
      data: {
        vectorId: vector.id,
        dimensions: vector.dimensions,
        trajectory: vector.trajectory,
        metadata: vector.metadata,
      },
    });
  }

  // Frequenz-Sync senden
  sendFrequencySync(config: FrequencyOutput): boolean {
    return this.send({
      type: 'frequency_sync',
      data: {
        frequency: config.frequency,
        amplitude: config.amplitude,
        waveform: config.waveform,
        modulation: config.modulation,
      },
    });
  }

  // Hardware-Status senden
  sendHardwareStatus(devices: ExternalDevice[], metrics: SystemMetrics | null): boolean {
    return this.send({
      type: 'hardware_status',
      data: {
        devices: devices.map(d => ({
          id: d.id,
          name: d.name,
          type: d.type,
          status: d.status,
        })),
        metrics: metrics ? {
          cpu: metrics.cpu,
          gpu: metrics.gpu,
          memory: metrics.memory,
          latency: metrics.latency,
        } : null,
      },
    });
  }

  // Session-Event senden
  sendSessionEvent(event: string, sessionId: string, payload?: object): boolean {
    return this.send({
      type: 'session_event',
      data: {
        event,
        sessionId,
        payload,
      },
    });
  }

  // Service beenden
  destroy(): void {
    this.disconnect();
    this.listeners.clear();
  }
}

// Singleton-Instanz
export const realtimeSync = new RealtimeSyncService();
