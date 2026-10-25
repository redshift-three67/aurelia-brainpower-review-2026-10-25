/**
 * Hook für Server-seitige Hardware-Metriken via WebSocket
 * Empfängt CPU/GPU-Auslastung und Temperaturen vom Cloud Server
 */
import { useState, useEffect, useCallback, useRef } from 'react';

export interface ServerHardwareMetrics {
  cpu: {
    usage: number;
    temperature: number;
    frequency: number;
    threads: number;
  };
  gpu: {
    usage: number;
    temperature: number;
    memoryUsed: number;
    memoryTotal: number;
    cudaUtilization: number;
  };
  ram: {
    used: number;
    total: number;
    percentage: number;
  };
  network: {
    latency: number;
    throughput: number;
  };
}

export interface EntropyData {
  cpuEntropy: number;
  gpuEntropy: number;
  ramEntropy: number;
  latencyEntropy: number;
  combined: number;
}

export interface ServerConfig {
  cpu: {
    model: string;
    cores: number;
    threads: number;
    baseFrequency: number;
    boostFrequency: number;
  };
  gpu: {
    model: string;
    vram: number;
    cudaCores: number;
  };
  ram: {
    total: number;
    type: string;
    speed: number;
  };
}

interface UseServerHardwareMetricsReturn {
  isConnected: boolean;
  metrics: ServerHardwareMetrics | null;
  entropy: EntropyData | null;
  serverConfig: ServerConfig | null;
  latency: number;
  connect: () => void;
  disconnect: () => void;
  getLatestMetrics: () => ServerHardwareMetrics | null;
  getLatestEntropy: () => EntropyData | null;
}

const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL;

export function useServerHardwareMetrics(): UseServerHardwareMetricsReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [metrics, setMetrics] = useState<ServerHardwareMetrics | null>(null);
  const [entropy, setEntropy] = useState<EntropyData | null>(null);
  const [serverConfig, setServerConfig] = useState<ServerConfig | null>(null);
  const [latency, setLatency] = useState(0);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const latestMetricsRef = useRef<ServerHardwareMetrics | null>(null);
  const latestEntropyRef = useRef<EntropyData | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    try {
      // WebSocket-URL konstruieren
      const wsUrl = SUPABASE_URL
        .replace('https://', 'wss://')
        .replace('http://', 'ws://');
      
      const ws = new WebSocket(`${wsUrl}/functions/v1/hardware-metrics`);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('[ServerMetrics] Connected to hardware-metrics');
        setIsConnected(true);
        
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          switch (data.type) {
            case 'config':
              setServerConfig(data.server);
              break;
              
            case 'metrics':
              setMetrics(data.metrics);
              setEntropy(data.entropy);
              latestMetricsRef.current = data.metrics;
              latestEntropyRef.current = data.entropy;
              break;
              
            case 'pong': {
              const now = Date.now();
              setLatency(now - data.clientTimestamp);
              break;
            }
          }
        } catch (error) {
          console.error('[ServerMetrics] Parse error:', error);
        }
      };

      ws.onclose = () => {
        console.log('[ServerMetrics] Disconnected');
        setIsConnected(false);
        wsRef.current = null;
        
        // Automatische Wiederverbindung nach 3 Sekunden
        reconnectTimeoutRef.current = window.setTimeout(() => {
          connect();
        }, 3000);
      };

      ws.onerror = (error) => {
        console.error('[ServerMetrics] WebSocket error:', error);
      };

    } catch (error) {
      console.error('[ServerMetrics] Connection error:', error);
    }
  }, []);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setIsConnected(false);
  }, []);

  const getLatestMetrics = useCallback(() => {
    return latestMetricsRef.current;
  }, []);

  const getLatestEntropy = useCallback(() => {
    return latestEntropyRef.current;
  }, []);

  // Ping für Latenz-Messung alle 5 Sekunden
  useEffect(() => {
    if (!isConnected) return;

    const pingInterval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'ping',
          timestamp: Date.now(),
        }));
      }
    }, 5000);

    return () => clearInterval(pingInterval);
  }, [isConnected]);

  // Cleanup
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    isConnected,
    metrics,
    entropy,
    serverConfig,
    latency,
    connect,
    disconnect,
    getLatestMetrics,
    getLatestEntropy,
  };
}

export default useServerHardwareMetrics;
