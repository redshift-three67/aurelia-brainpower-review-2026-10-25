"""
WebSocket-Server für Morphic Engine V1 Echtzeit-Streaming

Ermöglicht Live-Updates während Scans über WebSocket-Verbindungen:
- Real-time Progress Updates
- Live Item Discovery
- Critical Findings Alerts
- Multi-Client Support
"""

import asyncio
import json
import time
from typing import Dict, Set, Optional
from dataclasses import dataclass, asdict
import logging

# WebSocket Support (optional import)
try:
    import websockets
    from websockets.server import WebSocketServerProtocol
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    WebSocketServerProtocol = object

from core.realtime_streaming import (
    RealtimeStreamManager,
    StreamEvent,
    StreamEventType,
    get_stream_manager,
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MorphicWS")


@dataclass
class WebSocketMessage:
    """Standard-Nachrichtenformat für WebSocket"""
    type: str
    session_id: str
    timestamp: float
    data: dict
    progress: float = 0.0


class MorphicWebSocketServer:
    """WebSocket Server für Morphic Engine Streaming"""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Set[WebSocketServerProtocol] = set()
        self.session_clients: Dict[str, Set[WebSocketServerProtocol]] = {}
        self.stream_manager = get_stream_manager()
        self.running = False
    
    async def register(self, websocket: WebSocketServerProtocol, session_id: str = None):
        """Registriert neuen Client"""
        self.clients.add(websocket)
        if session_id:
            if session_id not in self.session_clients:
                self.session_clients[session_id] = set()
            self.session_clients[session_id].add(websocket)
        logger.info(f"Client connected. Total: {len(self.clients)}")
    
    async def unregister(self, websocket: WebSocketServerProtocol):
        """Entfernt Client"""
        self.clients.discard(websocket)
        for session_id, clients in self.session_clients.items():
            clients.discard(websocket)
        logger.info(f"Client disconnected. Total: {len(self.clients)}")
    
    async def broadcast(self, message: WebSocketMessage, session_id: str = None):
        """Sendet Nachricht an alle (oder Session-spezifische) Clients"""
        msg_json = json.dumps(asdict(message), ensure_ascii=False)
        
        if session_id and session_id in self.session_clients:
            targets = self.session_clients[session_id]
        else:
            targets = self.clients
        
        if targets:
            await asyncio.gather(
                *[client.send(msg_json) for client in targets],
                return_exceptions=True
            )
    
    def create_stream_callback(self, session_id: str):
        """Erstellt Callback für StreamManager → WebSocket Bridge"""
        async def async_callback(event: StreamEvent):
            message = WebSocketMessage(
                type=event.event_type.value,
                session_id=session_id,
                timestamp=event.timestamp,
                data=event.data,
                progress=event.progress_percent
            )
            await self.broadcast(message, session_id)
        
        def sync_callback(event: StreamEvent):
            # Sync-to-Async Bridge
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(async_callback(event))
                else:
                    loop.run_until_complete(async_callback(event))
            except RuntimeError:
                # Fallback: Neue Event Loop
                asyncio.run(async_callback(event))
        
        return sync_callback
    
    async def handle_message(self, websocket: WebSocketServerProtocol, message: str):
        """Verarbeitet eingehende Client-Nachrichten"""
        try:
            data = json.loads(message)
            action = data.get("action", "")
            session_id = data.get("session_id", "")
            
            if action == "subscribe":
                # Client abonniert Session-Updates
                await self.register(websocket, session_id)
                await websocket.send(json.dumps({
                    "type": "subscribed",
                    "session_id": session_id,
                    "timestamp": time.time()
                }))
            
            elif action == "unsubscribe":
                # Client beendet Abo
                if session_id in self.session_clients:
                    self.session_clients[session_id].discard(websocket)
            
            elif action == "get_status":
                # Aktueller Status einer Session
                status = self.stream_manager.get_live_status(session_id)
                await websocket.send(json.dumps({
                    "type": "status",
                    "session_id": session_id,
                    "data": status or {"error": "Session not found"},
                    "timestamp": time.time()
                }))
            
            elif action == "abort":
                # Scan abbrechen
                self.stream_manager.abort_session(session_id, "Client request")
                await websocket.send(json.dumps({
                    "type": "aborted",
                    "session_id": session_id,
                    "timestamp": time.time()
                }))
            
            elif action == "ping":
                # Keep-Alive
                await websocket.send(json.dumps({
                    "type": "pong",
                    "timestamp": time.time()
                }))
            
        except json.JSONDecodeError:
            await websocket.send(json.dumps({
                "type": "error",
                "message": "Invalid JSON",
                "timestamp": time.time()
            }))
    
    async def handler(self, websocket: WebSocketServerProtocol, path: str = "/"):
        """Haupt-Handler für WebSocket-Verbindungen"""
        await self.register(websocket)
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            await self.unregister(websocket)
    
    async def start(self):
        """Startet den WebSocket-Server"""
        if not WEBSOCKETS_AVAILABLE:
            logger.error("websockets library not installed. Run: pip install websockets")
            return
        
        self.running = True
        logger.info(f"Starting WebSocket server on ws://{self.host}:{self.port}")
        
        async with websockets.serve(self.handler, self.host, self.port):
            await asyncio.Future()  # Run forever
    
    def stop(self):
        """Stoppt den Server"""
        self.running = False


# HTTP API für REST-Fallback (ohne WebSocket)
class SimpleHTTPStreamAPI:
    """Einfache HTTP-basierte Alternative zu WebSocket"""
    
    def __init__(self):
        self.stream_manager = get_stream_manager()
        self.event_queues: Dict[str, list] = {}
    
    def get_events(self, session_id: str, since_index: int = 0) -> dict:
        """Polling-Endpoint für Events"""
        status = self.stream_manager.get_live_status(session_id)
        if not status:
            return {"error": "Session not found"}
        
        session = self.stream_manager.active_sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        
        events = session.events[since_index:]
        return {
            "session_id": session_id,
            "status": status,
            "new_events": [
                {
                    "type": e.event_type.value,
                    "timestamp": e.timestamp,
                    "data": e.data,
                    "progress": e.progress_percent
                }
                for e in events
            ],
            "next_index": len(session.events)
        }


# Standalone Server
def run_server(host: str = "localhost", port: int = 8765):
    """Startet WebSocket-Server standalone"""
    if not WEBSOCKETS_AVAILABLE:
        print("❌ websockets library not installed")
        print("   Run: pip install websockets")
        return
    
    server = MorphicWebSocketServer(host, port)
    print(f"🚀 Morphic WebSocket Server")
    print(f"   URL: ws://{host}:{port}")
    print(f"   Press Ctrl+C to stop")
    
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("\n⏹️ Server stopped")


# Client-seitige Helper (JavaScript-Code für Browser)
JS_CLIENT_CODE = '''
// Morphic Engine WebSocket Client
class MorphicStreamClient {
    constructor(url = 'ws://localhost:8765') {
        this.url = url;
        this.ws = null;
        this.callbacks = {
            onConnect: () => {},
            onProgress: () => {},
            onItemFound: () => {},
            onCritical: () => {},
            onComplete: () => {},
            onError: () => {}
        };
    }
    
    connect() {
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
            console.log('Connected to Morphic Server');
            this.callbacks.onConnect();
        };
        
        this.ws.onmessage = (event) => {
            const msg = JSON.parse(event.data);
            this.handleMessage(msg);
        };
        
        this.ws.onerror = (error) => {
            this.callbacks.onError(error);
        };
    }
    
    subscribe(sessionId) {
        this.ws.send(JSON.stringify({
            action: 'subscribe',
            session_id: sessionId
        }));
    }
    
    getStatus(sessionId) {
        this.ws.send(JSON.stringify({
            action: 'get_status',
            session_id: sessionId
        }));
    }
    
    abort(sessionId) {
        this.ws.send(JSON.stringify({
            action: 'abort',
            session_id: sessionId
        }));
    }
    
    handleMessage(msg) {
        switch(msg.type) {
            case 'progress_update':
            case 'group_complete':
                this.callbacks.onProgress(msg.progress, msg.data);
                break;
            case 'item_found':
                this.callbacks.onItemFound(msg.data.item);
                break;
            case 'critical_finding':
                this.callbacks.onCritical(msg.data);
                break;
            case 'scan_complete':
                this.callbacks.onComplete(msg.data);
                break;
            case 'error':
                this.callbacks.onError(msg);
                break;
        }
    }
    
    on(event, callback) {
        if (this.callbacks.hasOwnProperty('on' + event.charAt(0).toUpperCase() + event.slice(1))) {
            this.callbacks['on' + event.charAt(0).toUpperCase() + event.slice(1)] = callback;
        }
    }
}

// Usage:
// const client = new MorphicStreamClient();
// client.on('progress', (progress, data) => console.log(`${progress}%`));
// client.on('critical', (finding) => alert('Critical: ' + finding.item.label));
// client.connect();
// client.subscribe('session-123');
'''


if __name__ == "__main__":
    import sys
    host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8765
    run_server(host, port)
