// Realtime-Sync Edge Function für NLS-Feldengine
// WebSocket-basierte Echtzeit-Kommunikation mit < 5ms Latenz

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

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

// Verbindungs-Registry für aktive Clients
const connections = new Map<string, WebSocket>();

// Broadcast an alle verbundenen Clients
function broadcast(message: object, excludeId?: string) {
  const payload = JSON.stringify(message);
  connections.forEach((ws, id) => {
    if (id !== excludeId && ws.readyState === WebSocket.OPEN) {
      ws.send(payload);
    }
  });
}

// Ping-Handler für Latenz-Messung
function handlePing(ws: WebSocket, clientId: string, timestamp: number) {
  const serverTimestamp = Date.now();
  const latency = serverTimestamp - timestamp;
  
  ws.send(JSON.stringify({
    type: 'pong',
    clientId,
    clientTimestamp: timestamp,
    serverTimestamp,
    latency,
  }));
  
  console.log(`[realtime-sync] Ping from ${clientId}: ${latency}ms`);
}

// Vektor-Update Handler
function handleVectorUpdate(ws: WebSocket, clientId: string, data: VectorUpdatePayload) {
  console.log(`[realtime-sync] Vector update from ${clientId}:`, data.vectorId);
  
  // Broadcast an alle anderen Clients
  broadcast({
    type: 'vector_update',
    clientId,
    vectorId: data.vectorId,
    dimensions: data.dimensions,
    trajectory: data.trajectory,
    timestamp: Date.now(),
  }, clientId);
  
  // Bestätigung an Sender
  ws.send(JSON.stringify({
    type: 'vector_update_ack',
    vectorId: data.vectorId,
    timestamp: Date.now(),
  }));
}

// Frequenz-Sync Handler
function handleFrequencySync(ws: WebSocket, clientId: string, data: FrequencySyncPayload) {
  console.log(`[realtime-sync] Frequency sync from ${clientId}:`, data.frequency);
  
  broadcast({
    type: 'frequency_sync',
    clientId,
    frequency: data.frequency,
    amplitude: data.amplitude,
    waveform: data.waveform,
    timestamp: Date.now(),
  }, clientId);
}

// Hardware-Status Handler
function handleHardwareStatus(ws: WebSocket, clientId: string, data: HardwareStatusPayload) {
  console.log(`[realtime-sync] Hardware status from ${clientId}:`, data.devices?.length || 0, 'devices');
  
  broadcast({
    type: 'hardware_status',
    clientId,
    devices: data.devices,
    metrics: data.metrics,
    timestamp: Date.now(),
  }, clientId);
}

// Session-Event Handler
function handleSessionEvent(ws: WebSocket, clientId: string, data: SessionEventPayload) {
  console.log(`[realtime-sync] Session event from ${clientId}:`, data.event);
  
  broadcast({
    type: 'session_event',
    clientId,
    event: data.event,
    sessionId: data.sessionId,
    payload: data.payload,
    timestamp: Date.now(),
  }, clientId);
}

serve(async (req) => {
  const { headers, method } = req;
  
  // CORS preflight
  if (method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }
  
  // WebSocket Upgrade prüfen
  const upgradeHeader = headers.get("upgrade") || "";
  
  if (upgradeHeader.toLowerCase() !== "websocket") {
    // REST-Fallback für Status-Abfragen
    const url = new URL(req.url);
    
    if (url.pathname.endsWith('/status')) {
      return new Response(JSON.stringify({
        status: 'online',
        connections: connections.size,
        timestamp: Date.now(),
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }
    
    return new Response(JSON.stringify({
      error: 'WebSocket connection required',
      hint: 'Use WebSocket protocol to connect',
    }), {
      status: 400,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
  
  // WebSocket-Verbindung upgraden
  const { socket, response } = Deno.upgradeWebSocket(req);
  
  // Einzigartige Client-ID generieren
  const clientId = `client-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  
  socket.onopen = () => {
    console.log(`[realtime-sync] Client connected: ${clientId}`);
    connections.set(clientId, socket);
    
    // Willkommens-Nachricht mit Client-ID
    socket.send(JSON.stringify({
      type: 'connected',
      clientId,
      serverTime: Date.now(),
      connectedClients: connections.size,
    }));
    
    // Broadcast: Neuer Client verbunden
    broadcast({
      type: 'client_joined',
      clientId,
      totalClients: connections.size,
      timestamp: Date.now(),
    }, clientId);
  };
  
  socket.onmessage = (event) => {
    try {
      const message = JSON.parse(event.data) as RealtimeMessage;
      const timestamp = Date.now();
      
      console.log(`[realtime-sync] Message from ${clientId}:`, message.type);
      
      switch (message.type) {
        case 'ping':
          handlePing(socket, clientId, message.timestamp || timestamp);
          break;
          
        case 'vector_update':
          handleVectorUpdate(socket, clientId, message.data as VectorUpdatePayload);
          break;
          
        case 'frequency_sync':
          handleFrequencySync(socket, clientId, message.data as FrequencySyncPayload);
          break;
          
        case 'hardware_status':
          handleHardwareStatus(socket, clientId, message.data as HardwareStatusPayload);
          break;
          
        case 'session_event':
          handleSessionEvent(socket, clientId, message.data as SessionEventPayload);
          break;
          
        default:
          console.log(`[realtime-sync] Unknown message type: ${message.type}`);
          socket.send(JSON.stringify({
            type: 'error',
            message: `Unknown message type: ${message.type}`,
            timestamp,
          }));
      }
    } catch (error) {
      console.error(`[realtime-sync] Error processing message:`, error);
      socket.send(JSON.stringify({
        type: 'error',
        message: 'Invalid message format',
        timestamp: Date.now(),
      }));
    }
  };
  
  socket.onclose = () => {
    console.log(`[realtime-sync] Client disconnected: ${clientId}`);
    connections.delete(clientId);
    
    // Broadcast: Client getrennt
    broadcast({
      type: 'client_left',
      clientId,
      totalClients: connections.size,
      timestamp: Date.now(),
    });
  };
  
  socket.onerror = (error) => {
    console.error(`[realtime-sync] WebSocket error for ${clientId}:`, error);
    connections.delete(clientId);
  };
  
  return response;
});
