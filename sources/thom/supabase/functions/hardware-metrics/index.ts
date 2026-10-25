// Hardware-Metrics Edge Function
// Streamt Server-seitige Hardware-Metriken (CPU, GPU, RAM, Temperaturen) via WebSocket

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

// Simulierte Server-Hardware-Konfiguration (Lovable Cloud Server)
const SERVER_CONFIG = {
  cpu: {
    model: 'AMD Ryzen 5 9600X',
    cores: 6,
    threads: 12,
    baseFrequency: 3.9,
    boostFrequency: 5.4,
  },
  gpu: {
    model: 'NVIDIA RTX 4000 SFF Ada',
    vram: 20,
    cudaCores: 6144,
  },
  ram: {
    total: 64,
    type: 'DDR5',
    speed: 5600,
  },
};

// Generiert realistische Hardware-Metriken mit natürlicher Varianz
function generateMetrics(): object {
  const now = Date.now();
  const timeVariance = Math.sin(now / 10000) * 0.15; // Langsame Oszillation
  const randomNoise = () => (Math.random() - 0.5) * 0.1;

  // CPU Metriken mit realistischer Last-Simulation
  const cpuBase = 15 + Math.abs(Math.sin(now / 5000)) * 25;
  const cpuUsage = Math.min(100, Math.max(5, cpuBase + timeVariance * 30 + randomNoise() * 10));
  const cpuTemp = 35 + cpuUsage * 0.45 + randomNoise() * 3;

  // GPU Metriken (CUDA-Berechnungen)
  const gpuBase = 10 + Math.abs(Math.cos(now / 7000)) * 35;
  const gpuUsage = Math.min(100, Math.max(3, gpuBase + timeVariance * 25 + randomNoise() * 8));
  const gpuTemp = 38 + gpuUsage * 0.5 + randomNoise() * 4;
  const gpuMemory = 2.5 + gpuUsage * 0.15 + randomNoise() * 0.5;

  // RAM Metriken
  const ramBase = 18 + Math.abs(Math.sin(now / 15000)) * 12;
  const ramUsed = Math.min(60, Math.max(12, ramBase + randomNoise() * 3));

  // Netzwerk-Latenz
  const latencyBase = 2 + Math.abs(Math.sin(now / 3000)) * 3;
  const networkLatency = Math.max(0.5, latencyBase + randomNoise() * 1.5);

  return {
    timestamp: now,
    server: SERVER_CONFIG,
    metrics: {
      cpu: {
        usage: Math.round(cpuUsage * 10) / 10,
        temperature: Math.round(cpuTemp * 10) / 10,
        frequency: SERVER_CONFIG.cpu.baseFrequency + (cpuUsage / 100) * (SERVER_CONFIG.cpu.boostFrequency - SERVER_CONFIG.cpu.baseFrequency),
        threads: SERVER_CONFIG.cpu.threads,
      },
      gpu: {
        usage: Math.round(gpuUsage * 10) / 10,
        temperature: Math.round(gpuTemp * 10) / 10,
        memoryUsed: Math.round(gpuMemory * 100) / 100,
        memoryTotal: SERVER_CONFIG.gpu.vram,
        cudaUtilization: Math.round(gpuUsage * 0.85 * 10) / 10,
      },
      ram: {
        used: Math.round(ramUsed * 10) / 10,
        total: SERVER_CONFIG.ram.total,
        percentage: Math.round((ramUsed / SERVER_CONFIG.ram.total) * 1000) / 10,
      },
      network: {
        latency: Math.round(networkLatency * 100) / 100,
        throughput: Math.round((100 - networkLatency * 5) * 10) / 10,
      },
    },
    entropy: {
      // Entropie-Werte für Klienten-Vektor-Berechnung
      cpuEntropy: Math.round(cpuUsage * cpuTemp * 0.01 * 1000) / 1000,
      gpuEntropy: Math.round(gpuUsage * gpuTemp * 0.01 * 1000) / 1000,
      ramEntropy: Math.round(ramUsed * 0.1 * 1000) / 1000,
      latencyEntropy: Math.round(networkLatency * 10 * 1000) / 1000,
      combined: Math.round((cpuUsage * 0.3 + gpuUsage * 0.3 + ramUsed * 0.2 + networkLatency * 2) * 100) / 100,
    },
  };
}

// Aktive WebSocket-Verbindungen
const connections = new Map<string, { socket: WebSocket; interval: number | null }>();

serve(async (req) => {
  const { headers, method } = req;

  // CORS preflight
  if (method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  const upgradeHeader = headers.get("upgrade") || "";

  // REST-Endpoint für einmalige Abfrage
  if (upgradeHeader.toLowerCase() !== "websocket") {
    const url = new URL(req.url);
    
    if (url.pathname.endsWith('/metrics')) {
      return new Response(JSON.stringify(generateMetrics()), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    if (url.pathname.endsWith('/config')) {
      return new Response(JSON.stringify({ server: SERVER_CONFIG }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    return new Response(JSON.stringify({
      error: 'Use WebSocket for real-time streaming or /metrics for single request',
      endpoints: ['/metrics', '/config'],
    }), {
      status: 400,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }

  // WebSocket-Upgrade
  const { socket, response } = Deno.upgradeWebSocket(req);
  const clientId = `hw-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

  socket.onopen = () => {
    console.log(`[hardware-metrics] Client connected: ${clientId}`);
    
    // Initiale Konfiguration senden
    socket.send(JSON.stringify({
      type: 'config',
      clientId,
      server: SERVER_CONFIG,
      timestamp: Date.now(),
    }));

    // Starte Metrik-Streaming alle 500ms
    const interval = setInterval(() => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
          type: 'metrics',
          ...generateMetrics(),
        }));
      }
    }, 500);

    connections.set(clientId, { socket, interval });
  };

  socket.onmessage = (event) => {
    try {
      const message = JSON.parse(event.data);
      
      switch (message.type) {
        case 'ping':
          socket.send(JSON.stringify({
            type: 'pong',
            clientTimestamp: message.timestamp,
            serverTimestamp: Date.now(),
          }));
          break;
          
        case 'get_metrics':
          socket.send(JSON.stringify({
            type: 'metrics',
            ...generateMetrics(),
          }));
          break;

        case 'set_interval': {
          // Erlaubt Änderung des Streaming-Intervalls (min 100ms, max 5000ms)
          const conn = connections.get(clientId);
          if (conn && conn.interval) {
            clearInterval(conn.interval);
            const newInterval = Math.max(100, Math.min(5000, message.intervalMs || 500));
            conn.interval = setInterval(() => {
              if (socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({
                  type: 'metrics',
                  ...generateMetrics(),
                }));
              }
            }, newInterval);
            connections.set(clientId, conn);
            socket.send(JSON.stringify({
              type: 'interval_updated',
              intervalMs: newInterval,
            }));
          }
          break;
        }

        default:
          console.log(`[hardware-metrics] Unknown message type: ${message.type}`);
      }
    } catch (error) {
      console.error(`[hardware-metrics] Error:`, error);
    }
  };

  socket.onclose = () => {
    console.log(`[hardware-metrics] Client disconnected: ${clientId}`);
    const conn = connections.get(clientId);
    if (conn?.interval) {
      clearInterval(conn.interval);
    }
    connections.delete(clientId);
  };

  socket.onerror = (error) => {
    console.error(`[hardware-metrics] Error for ${clientId}:`, error);
    const conn = connections.get(clientId);
    if (conn?.interval) {
      clearInterval(conn.interval);
    }
    connections.delete(clientId);
  };

  return response;
});
