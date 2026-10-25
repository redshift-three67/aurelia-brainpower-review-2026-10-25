"""
Echtzeit-Streaming für Morphic Engine V1

Ermöglicht Live-Fortschritts-Updates während eines Scans:
- Callback-basiertes Streaming
- WebSocket-kompatible Events
- Inkrementeller Report-Aufbau
- Frühzeitiger Abbruch bei kritischen Funden
"""

import time
import json
from typing import Callable, Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from threading import Event


class StreamEventType(Enum):
    """Typen von Streaming-Events"""
    SCAN_START = "scan_start"
    GROUP_START = "group_start"
    GROUP_COMPLETE = "group_complete"
    ITEM_FOUND = "item_found"
    CRITICAL_FINDING = "critical_finding"
    PROGRESS_UPDATE = "progress_update"
    SYNERGY_CALCULATED = "synergy_calculated"
    SCAN_COMPLETE = "scan_complete"
    ERROR = "error"


@dataclass
class StreamEvent:
    """Einzelnes Streaming-Event"""
    event_type: StreamEventType
    timestamp: float
    data: Dict[str, Any]
    progress_percent: float = 0.0


@dataclass
class StreamingSession:
    """Session für Echtzeit-Streaming"""
    session_id: str
    client_name: str
    profile: str
    total_groups: int
    processed_groups: int = 0
    events: List[StreamEvent] = field(default_factory=list)
    top_items_live: List[Dict] = field(default_factory=list)
    critical_findings: List[Dict] = field(default_factory=list)
    abort_flag: Event = field(default_factory=Event)
    callbacks: List[Callable] = field(default_factory=list)


class RealtimeStreamManager:
    """Manager für Echtzeit-Scan-Streaming"""
    
    def __init__(self):
        self.active_sessions: Dict[str, StreamingSession] = {}
        self.critical_threshold: float = 0.8  # Score > 80% = kritisch
    
    def create_session(
        self,
        session_id: str,
        client_name: str,
        profile: str,
        total_groups: int
    ) -> StreamingSession:
        """
        Erstellt neue Streaming-Session.
        
        Args:
            session_id: Eindeutige Session-ID
            client_name: Klientenname
            profile: Scan-Profil
            total_groups: Anzahl der zu scannenden Gruppen
        
        Returns:
            StreamingSession
        """
        session = StreamingSession(
            session_id=session_id,
            client_name=client_name,
            profile=profile,
            total_groups=total_groups
        )
        self.active_sessions[session_id] = session
        
        # Start-Event
        self._emit_event(session, StreamEventType.SCAN_START, {
            "client": client_name,
            "profile": profile,
            "total_groups": total_groups
        })
        
        return session
    
    def register_callback(
        self,
        session_id: str,
        callback: Callable[[StreamEvent], None]
    ):
        """
        Registriert Callback für Live-Events.
        
        Args:
            session_id: Session-ID
            callback: Funktion die bei jedem Event aufgerufen wird
        """
        if session_id in self.active_sessions:
            self.active_sessions[session_id].callbacks.append(callback)
    
    def on_group_start(self, session_id: str, group_name: str, group_index: int):
        """Callback wenn Gruppe startet."""
        session = self.active_sessions.get(session_id)
        if not session:
            return
        
        if session.abort_flag.is_set():
            raise AbortScanException("Scan abgebrochen")
        
        progress = (group_index / session.total_groups) * 100
        
        self._emit_event(session, StreamEventType.GROUP_START, {
            "group": group_name,
            "index": group_index,
            "total": session.total_groups
        }, progress)
    
    def on_group_complete(
        self,
        session_id: str,
        group_name: str,
        items_found: int,
        top_items: List[Dict]
    ):
        """Callback wenn Gruppe abgeschlossen."""
        session = self.active_sessions.get(session_id)
        if not session:
            return
        
        session.processed_groups += 1
        progress = (session.processed_groups / session.total_groups) * 100
        
        # Aktualisiere Live-Top-Items
        for item in top_items:
            self._update_live_items(session, item)
        
        # Prüfe auf kritische Funde
        for item in top_items:
            if item.get('score', 0) > self.critical_threshold:
                self._handle_critical_finding(session, item, group_name)
        
        self._emit_event(session, StreamEventType.GROUP_COMPLETE, {
            "group": group_name,
            "items_found": items_found,
            "top_items": top_items[:3]
        }, progress)
    
    def on_item_found(self, session_id: str, item: Dict):
        """Callback wenn einzelnes Item gefunden."""
        session = self.active_sessions.get(session_id)
        if not session:
            return
        
        self._emit_event(session, StreamEventType.ITEM_FOUND, {
            "item": item
        })
    
    def on_synergy_calculated(self, session_id: str, synergy_data: Dict):
        """Callback wenn Synergy berechnet wurde."""
        session = self.active_sessions.get(session_id)
        if not session:
            return
        
        self._emit_event(session, StreamEventType.SYNERGY_CALCULATED, synergy_data)
    
    def complete_session(self, session_id: str, final_results: Dict):
        """Schließt Session ab."""
        session = self.active_sessions.get(session_id)
        if not session:
            return
        
        self._emit_event(session, StreamEventType.SCAN_COMPLETE, {
            "results": final_results,
            "critical_count": len(session.critical_findings),
            "duration_seconds": time.time() - session.events[0].timestamp if session.events else 0
        }, 100.0)
    
    def abort_session(self, session_id: str, reason: str = "User request"):
        """Bricht Session ab."""
        session = self.active_sessions.get(session_id)
        if session:
            session.abort_flag.set()
            self._emit_event(session, StreamEventType.ERROR, {
                "error": "Scan abgebrochen",
                "reason": reason
            })
    
    def get_live_status(self, session_id: str) -> Optional[Dict]:
        """Gibt aktuellen Live-Status zurück."""
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        return {
            "session_id": session_id,
            "client": session.client_name,
            "profile": session.profile,
            "progress": (session.processed_groups / session.total_groups * 100) if session.total_groups > 0 else 0,
            "processed_groups": session.processed_groups,
            "total_groups": session.total_groups,
            "top_items": session.top_items_live[:5],
            "critical_findings": session.critical_findings,
            "event_count": len(session.events)
        }
    
    def _emit_event(
        self,
        session: StreamingSession,
        event_type: StreamEventType,
        data: Dict,
        progress: float = 0.0
    ):
        """Sendet Event an alle registrierten Callbacks."""
        event = StreamEvent(
            event_type=event_type,
            timestamp=time.time(),
            data=data,
            progress_percent=progress
        )
        session.events.append(event)
        
        # Rufe alle Callbacks auf
        for callback in session.callbacks:
            try:
                callback(event)
            except Exception:
                pass  # Callback-Fehler ignorieren
    
    def _update_live_items(self, session: StreamingSession, item: Dict):
        """Aktualisiert Live-Top-Items Liste."""
        # Füge hinzu und sortiere
        session.top_items_live.append(item)
        session.top_items_live.sort(key=lambda x: x.get('score', 0), reverse=True)
        session.top_items_live = session.top_items_live[:20]  # Max 20
    
    def _handle_critical_finding(
        self,
        session: StreamingSession,
        item: Dict,
        group_name: str
    ):
        """Behandelt kritischen Fund."""
        finding = {
            "item": item,
            "group": group_name,
            "timestamp": time.time()
        }
        session.critical_findings.append(finding)
        
        self._emit_event(session, StreamEventType.CRITICAL_FINDING, finding)


class AbortScanException(Exception):
    """Exception für Scan-Abbruch"""
    pass


# Globale Manager-Instanz
_stream_manager: Optional[RealtimeStreamManager] = None


def get_stream_manager() -> RealtimeStreamManager:
    """Gibt globale Stream-Manager-Instanz zurück."""
    global _stream_manager
    if _stream_manager is None:
        _stream_manager = RealtimeStreamManager()
    return _stream_manager


def console_callback(event: StreamEvent):
    """Beispiel-Callback für Konsolen-Ausgabe."""
    timestamp = time.strftime("%H:%M:%S", time.localtime(event.timestamp))
    
    if event.event_type == StreamEventType.SCAN_START:
        print(f"\n[{timestamp}] 🚀 Scan gestartet: {event.data.get('profile')}")
        print(f"           Gruppen: {event.data.get('total_groups')}")
    
    elif event.event_type == StreamEventType.GROUP_START:
        print(f"[{timestamp}] 📂 Gruppe {event.data.get('index')+1}/{event.data.get('total')}: {event.data.get('group')}")
    
    elif event.event_type == StreamEventType.GROUP_COMPLETE:
        print(f"[{timestamp}] ✓ {event.data.get('group')}: {event.data.get('items_found')} Items [{event.progress_percent:.0f}%]")
    
    elif event.event_type == StreamEventType.CRITICAL_FINDING:
        item = event.data.get('item', {})
        print(f"[{timestamp}] ⚠️ KRITISCH: {item.get('label')} (Score: {item.get('score', 0):.2f})")
    
    elif event.event_type == StreamEventType.SCAN_COMPLETE:
        duration = event.data.get('duration_seconds', 0)
        print(f"\n[{timestamp}] ✅ Scan abgeschlossen in {duration:.1f}s")
        print(f"           Kritische Funde: {event.data.get('critical_count', 0)}")


def format_progress_bar(percent: float, width: int = 30) -> str:
    """Erstellt ASCII-Fortschrittsbalken."""
    filled = int(width * percent / 100)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {percent:.1f}%"
