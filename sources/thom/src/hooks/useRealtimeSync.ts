// React Hook für Realtime-Sync
import { useState, useEffect, useCallback } from 'react';
import { realtimeSync, type RealtimeEvent, type LatencyStats } from '@/services/realtime/RealtimeSyncService';
import type { ClientVector, FrequencyOutput, ExternalDevice, SystemMetrics } from '@/types/hardware';

interface UseRealtimeSyncReturn {
  isConnected: boolean;
  clientId: string | null;
  latency: LatencyStats;
  connectedClients: number;
  lastEvent: RealtimeEvent | null;
  connect: () => Promise<void>;
  disconnect: () => void;
  sendVectorUpdate: (vector: ClientVector) => boolean;
  sendFrequencySync: (config: FrequencyOutput) => boolean;
  sendHardwareStatus: (devices: ExternalDevice[], metrics: SystemMetrics | null) => boolean;
  sendSessionEvent: (event: string, sessionId: string, payload?: object) => boolean;
}

export function useRealtimeSync(): UseRealtimeSyncReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [clientId, setClientId] = useState<string | null>(null);
  const [latency, setLatency] = useState<LatencyStats>({
    current: 0,
    min: Infinity,
    max: 0,
    avg: 0,
    samples: [],
  });
  const [connectedClients, setConnectedClients] = useState(0);
  const [lastEvent, setLastEvent] = useState<RealtimeEvent | null>(null);

  // Event-Handler
  const handleEvent = useCallback((event: RealtimeEvent) => {
    setLastEvent(event);

    switch (event.type) {
      case 'connected':
        setIsConnected(true);
        setClientId(event.clientId || null);
        if (event.data && typeof event.data === 'object' && 'connectedClients' in event.data) {
          setConnectedClients((event.data as { connectedClients: number }).connectedClients);
        }
        break;

      case 'disconnected':
        setIsConnected(false);
        setClientId(null);
        break;

      case 'pong':
        if (event.data && typeof event.data === 'object' && 'stats' in event.data) {
          setLatency((event.data as { stats: LatencyStats }).stats);
        }
        break;

      case 'client_joined':
      case 'client_left':
        if (event.data && typeof event.data === 'object' && 'totalClients' in event.data) {
          setConnectedClients((event.data as { totalClients: number }).totalClients);
        }
        break;
    }
  }, []);

  // Event-Listener registrieren
  useEffect(() => {
    realtimeSync.addEventListener(handleEvent);

    return () => {
      realtimeSync.removeEventListener(handleEvent);
    };
  }, [handleEvent]);

  // Verbindung herstellen
  const connect = useCallback(async () => {
    await realtimeSync.connect();
  }, []);

  // Verbindung trennen
  const disconnect = useCallback(() => {
    realtimeSync.disconnect();
  }, []);

  // Vektor-Update senden
  const sendVectorUpdate = useCallback((vector: ClientVector): boolean => {
    return realtimeSync.sendVectorUpdate(vector);
  }, []);

  // Frequenz-Sync senden
  const sendFrequencySync = useCallback((config: FrequencyOutput): boolean => {
    return realtimeSync.sendFrequencySync(config);
  }, []);

  // Hardware-Status senden
  const sendHardwareStatus = useCallback((devices: ExternalDevice[], metrics: SystemMetrics | null): boolean => {
    return realtimeSync.sendHardwareStatus(devices, metrics);
  }, []);

  // Session-Event senden
  const sendSessionEvent = useCallback((event: string, sessionId: string, payload?: object): boolean => {
    return realtimeSync.sendSessionEvent(event, sessionId, payload);
  }, []);

  return {
    isConnected,
    clientId,
    latency,
    connectedClients,
    lastEvent,
    connect,
    disconnect,
    sendVectorUpdate,
    sendFrequencySync,
    sendHardwareStatus,
    sendSessionEvent,
  };
}
