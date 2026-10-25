"""
Session-Management System
Speichert und verwaltet Klienten-Sessions für Verlaufsanalysen
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
import json


@dataclass
class ScanSession:
    """Einzelne Scan-Session"""
    
    session_id: str
    timestamp: str
    focus: str
    scan_type: str  # "full", "ultra", "quick"
    
    # Ergebnisse
    h_level: float
    morphic_field: float
    entropy: float
    top_items: Dict[str, float] = field(default_factory=dict)
    
    # Quantum-Synergy Ergebnisse (optional)
    synergy_combinations: List[Dict] = field(default_factory=list)
    
    # Dateien
    json_file: Optional[str] = None
    html_file: Optional[str] = None
    txt_file: Optional[str] = None
    
    # Notizen
    notes: str = ""
    therapist_notes: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ScanSession':
        return cls(**data)


@dataclass
class ClientSessionHistory:
    """Session-Historie eines Klienten"""
    
    client_folder: str
    sessions: List[ScanSession] = field(default_factory=list)
    scheduled_retests: List[Dict] = field(default_factory=list)
    
    def add_session(self, session: ScanSession):
        """Fügt neue Session hinzu"""
        self.sessions.append(session)
        self.sessions.sort(key=lambda s: s.timestamp, reverse=True)
    
    def get_latest_session(self) -> Optional[ScanSession]:
        """Gibt neueste Session zurück"""
        return self.sessions[0] if self.sessions else None
    
    def get_sessions_by_focus(self, focus: str) -> List[ScanSession]:
        """Gibt alle Sessions mit bestimmtem Fokus zurück"""
        return [s for s in self.sessions if s.focus.lower() == focus.lower()]
    
    def get_sessions_in_range(self, days: int) -> List[ScanSession]:
        """Gibt Sessions der letzten N Tage zurück"""
        cutoff = datetime.now() - timedelta(days=days)
        return [
            s for s in self.sessions
            if datetime.fromisoformat(s.timestamp) >= cutoff
        ]
    
    def schedule_retest(
        self,
        focus: str,
        scheduled_date: str,
        reason: str = "",
        auto_run: bool = False
    ):
        """Plant Nachtest"""
        retest = {
            'focus': focus,
            'scheduled_date': scheduled_date,
            'reason': reason,
            'auto_run': auto_run,
            'created_at': datetime.now().isoformat(),
            'completed': False
        }
        self.scheduled_retests.append(retest)
    
    def get_pending_retests(self) -> List[Dict]:
        """Gibt ausstehende Nachtests zurück"""
        today = datetime.now().date()
        pending = []
        
        for retest in self.scheduled_retests:
            if retest['completed']:
                continue
            
            scheduled = datetime.fromisoformat(retest['scheduled_date']).date()
            if scheduled <= today:
                pending.append(retest)
        
        return pending
    
    def mark_retest_completed(self, focus: str, scheduled_date: str):
        """Markiert Nachtest als abgeschlossen"""
        for retest in self.scheduled_retests:
            if (retest['focus'] == focus and 
                retest['scheduled_date'] == scheduled_date):
                retest['completed'] = True
                retest['completed_at'] = datetime.now().isoformat()
    
    def get_progress_analysis(self, focus: str) -> Dict:
        """Analysiert Fortschritt für bestimmten Fokus"""
        sessions = self.get_sessions_by_focus(focus)
        if len(sessions) < 2:
            return {'status': 'insufficient_data', 'sessions': len(sessions)}
        
        # Sortiere chronologisch
        sessions.sort(key=lambda s: s.timestamp)
        
        first = sessions[0]
        latest = sessions[-1]
        
        # Berechne Trends
        h_level_trend = latest.h_level - first.h_level
        morphic_trend = latest.morphic_field - first.morphic_field
        entropy_trend = latest.entropy - first.entropy
        
        # Vergleiche Top-Items
        first_items = set(first.top_items.keys())
        latest_items = set(latest.top_items.keys())
        
        resolved_items = first_items - latest_items
        new_items = latest_items - first_items
        persistent_items = first_items & latest_items
        
        return {
            'status': 'analyzed',
            'sessions_count': len(sessions),
            'timespan_days': (
                datetime.fromisoformat(latest.timestamp) -
                datetime.fromisoformat(first.timestamp)
            ).days,
            'trends': {
                'h_level': {
                    'first': first.h_level,
                    'latest': latest.h_level,
                    'change': h_level_trend,
                    'direction': 'improved' if h_level_trend < 0 else 'worsened'
                },
                'morphic_field': {
                    'first': first.morphic_field,
                    'latest': latest.morphic_field,
                    'change': morphic_trend
                },
                'entropy': {
                    'first': first.entropy,
                    'latest': latest.entropy,
                    'change': entropy_trend
                }
            },
            'items': {
                'resolved': list(resolved_items),
                'new': list(new_items),
                'persistent': list(persistent_items),
                'resolved_count': len(resolved_items),
                'new_count': len(new_items),
                'persistent_count': len(persistent_items)
            }
        }
    
    def to_dict(self) -> Dict:
        return {
            'client_folder': self.client_folder,
            'sessions': [s.to_dict() for s in self.sessions],
            'scheduled_retests': self.scheduled_retests
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ClientSessionHistory':
        return cls(
            client_folder=data['client_folder'],
            sessions=[ScanSession.from_dict(s) for s in data.get('sessions', [])],
            scheduled_retests=data.get('scheduled_retests', [])
        )
    
    def save(self, base_path: Path):
        """Speichert Session-Historie"""
        folder = base_path / self.client_folder
        folder.mkdir(parents=True, exist_ok=True)
        
        history_file = folder / "session_history.json"
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls, folder: Path) -> 'ClientSessionHistory':
        """Lädt Session-Historie"""
        history_file = folder / "session_history.json"
        
        if not history_file.exists():
            return cls(client_folder=folder.name)
        
        with open(history_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls.from_dict(data)


def create_session_from_scan(
    scan_data: Dict,
    scan_files: Dict[str, Path],
    synergy_results: Optional[List] = None
) -> ScanSession:
    """
    Erstellt Session aus Scan-Daten
    
    Args:
        scan_data: Scan-Ergebnisse (JSON)
        scan_files: Pfade zu generierten Dateien
        synergy_results: Optional - Quantum-Synergy Ergebnisse
    
    Returns:
        ScanSession-Objekt
    """
    timestamp = datetime.now().isoformat()
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Extrahiere Top-Items
    top_items = {}
    if 'analysis' in scan_data and 'resonance_map' in scan_data['analysis']:
        top_items = scan_data['analysis']['resonance_map'].copy()
    
    # Synergy-Kombinationen
    synergy_combos = []
    if synergy_results:
        for items, score, details in synergy_results:
            synergy_combos.append({
                'items': [item['label'] for item in items],
                'score': score,
                'components': {
                    'individual': details['individual_scores'],
                    'resonance': details['resonance'],
                    'harmony': details['harmony'],
                    'relevance': details['relevance']
                }
            })
    
    return ScanSession(
        session_id=session_id,
        timestamp=timestamp,
        focus=scan_data.get('focus', ''),
        scan_type=scan_data.get('scan_type', 'full'),
        h_level=scan_data.get('h_level', 0.0),
        morphic_field=scan_data.get('analysis', {}).get('morphic_field', 0.0),
        entropy=scan_data.get('analysis', {}).get('entropy_calibrated', 0.0),
        top_items=top_items,
        synergy_combinations=synergy_combos,
        json_file=str(scan_files.get('json', '')),
        html_file=str(scan_files.get('html', '')),
        txt_file=str(scan_files.get('txt', ''))
    )
