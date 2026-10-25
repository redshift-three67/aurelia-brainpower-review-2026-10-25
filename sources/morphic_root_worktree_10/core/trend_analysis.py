"""
Trend-Analyse für Morphic Engine V1

Analysiert historische Scan-Daten eines Klienten:
- Zeitreihen-Vergleiche über mehrere Scans
- Automatische Erkennung von Verbesserung/Verschlechterung
- Therapie-Erfolgsmonitoring
- Wiederkehrende Muster erkennen
"""

import os
import json
import glob
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ScanSnapshot:
    """Einzelner Scan-Snapshot für Trend-Analyse"""
    timestamp: datetime
    profile: str
    focus: str
    h_level: float
    morphic_field: float
    top_items: List[Dict]
    file_path: str


@dataclass
class TrendResult:
    """Ergebnis einer Trend-Analyse"""
    client_name: str
    scan_count: int
    date_range: Tuple[datetime, datetime]
    improving_items: List[Dict]    # Items mit sinkenden Scores (gut)
    worsening_items: List[Dict]    # Items mit steigenden Scores (Achtung)
    stable_items: List[Dict]       # Konstante Items
    recurring_items: List[Dict]    # In mehreren Scans aufgetaucht
    overall_trend: str             # "improving", "stable", "worsening"
    confidence: float


def load_client_scans(archive_path: str, client_pattern: str) -> List[ScanSnapshot]:
    """
    Lädt alle Scans eines Klienten aus dem Archiv.
    
    Args:
        archive_path: Pfad zum Benutzer_Archive Ordner
        client_pattern: Muster für Klientenordner (z.B. "Müller*" oder "Final*")
    
    Returns:
        Liste von ScanSnapshots, sortiert nach Datum
    """
    snapshots = []
    
    # Finde alle passenden Klientenordner
    search_pattern = os.path.join(archive_path, client_pattern)
    client_folders = glob.glob(search_pattern)
    
    for folder in client_folders:
        if not os.path.isdir(folder):
            continue
        
        # Finde alle JSON-Scan-Dateien, auch in Top-N-Session-Unterordnern.
        json_files = glob.glob(os.path.join(folder, "**", "*_multiplex_scan.json"), recursive=True)
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Parse Timestamp aus Dateiname (YYYYMMDD_HHMMSS)
                filename = os.path.basename(json_file)
                date_str = filename[:15]  # "20251126_152929"
                try:
                    timestamp = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
                except ValueError:
                    timestamp = datetime.now()
                
                top_items = _extract_top_items(data)[:20]

                # Extrahiere relevante Daten
                snapshot = ScanSnapshot(
                    timestamp=timestamp,
                    profile=data.get('profile', 'unknown'),
                    focus=data.get('focus', ''),
                    h_level=data.get('h_level', 0.0),
                    morphic_field=data.get('morphic_field', 0.0),
                    top_items=top_items,
                    file_path=json_file
                )
                snapshots.append(snapshot)
                
            except (json.JSONDecodeError, IOError):
                continue
    
    # Sortiere nach Timestamp
    snapshots.sort(key=lambda s: s.timestamp)
    return snapshots


def _extract_top_items(scan_data: Dict) -> List[Dict]:
    """Return top items from legacy and current scan export schemas."""
    top_items = scan_data.get("top_items")
    if isinstance(top_items, list):
        return [item for item in top_items if isinstance(item, dict)]

    sub_results = scan_data.get("sub_results") or {}
    if isinstance(sub_results, dict) and isinstance(sub_results.get("top"), list):
        return [item for item in sub_results["top"] if isinstance(item, dict)]

    top_scores = scan_data.get("top_scores")
    if isinstance(top_scores, list):
        return [item for item in top_scores if isinstance(item, dict)]

    return []


def analyze_item_trends(snapshots: List[ScanSnapshot]) -> Dict[str, List[float]]:
    """
    Analysiert Score-Trends für jedes Item über alle Snapshots.
    
    Args:
        snapshots: Liste von ScanSnapshots
    
    Returns:
        Dict: item_label → Liste von Scores (chronologisch)
    """
    item_scores: Dict[str, List[float]] = {}
    
    for snapshot in snapshots:
        for item in snapshot.top_items:
            label = item.get('label', '')
            score = item.get('score', 0.0)
            
            if label not in item_scores:
                item_scores[label] = []
            item_scores[label].append(score)
    
    return item_scores


def calculate_trend_direction(scores: List[float]) -> Tuple[str, float]:
    """
    Berechnet Trend-Richtung aus Score-Liste.
    
    Args:
        scores: Liste von Scores (chronologisch)
    
    Returns:
        Tuple: (direction, change_percent)
    """
    if len(scores) < 2:
        return ("stable", 0.0)
    
    first_avg = sum(scores[:len(scores)//2]) / max(1, len(scores)//2)
    last_avg = sum(scores[len(scores)//2:]) / max(1, len(scores) - len(scores)//2)
    
    if first_avg == 0:
        return ("stable", 0.0)
    
    change = (last_avg - first_avg) / first_avg * 100
    
    if change < -15:
        return ("improving", change)  # Score sinkt = Item weniger belastet
    elif change > 15:
        return ("worsening", change)  # Score steigt = Item mehr belastet
    else:
        return ("stable", change)


def analyze_trends(
    archive_path: str,
    client_pattern: str,
    min_scans: int = 2
) -> Optional[TrendResult]:
    """
    Hauptfunktion: Führt vollständige Trend-Analyse durch.
    
    Args:
        archive_path: Pfad zum Benutzer_Archive Ordner
        client_pattern: Muster für Klientenordner
        min_scans: Minimum benötigte Scans
    
    Returns:
        TrendResult oder None wenn nicht genug Daten
    """
    snapshots = load_client_scans(archive_path, client_pattern)
    
    if len(snapshots) < min_scans:
        return None
    
    # Analysiere Item-Trends
    item_scores = analyze_item_trends(snapshots)
    
    improving = []
    worsening = []
    stable = []
    recurring = []
    
    for label, scores in item_scores.items():
        direction, change = calculate_trend_direction(scores)
        
        item_info = {
            "label": label,
            "occurrences": len(scores),
            "first_score": scores[0],
            "last_score": scores[-1],
            "change_percent": round(change, 1),
            "direction": direction
        }
        
        # Kategorisiere
        if len(scores) >= 2:
            recurring.append(item_info)
        
        if direction == "improving":
            improving.append(item_info)
        elif direction == "worsening":
            worsening.append(item_info)
        else:
            stable.append(item_info)
    
    # Sortiere nach Änderungsstärke
    improving.sort(key=lambda x: x["change_percent"])
    worsening.sort(key=lambda x: x["change_percent"], reverse=True)
    recurring.sort(key=lambda x: x["occurrences"], reverse=True)
    
    # Bestimme Gesamt-Trend
    if len(improving) > len(worsening) * 1.5:
        overall = "improving"
    elif len(worsening) > len(improving) * 1.5:
        overall = "worsening"
    else:
        overall = "stable"
    
    # Berechne Konfidenz basierend auf Datenmenge
    confidence = min(1.0, len(snapshots) / 10.0)
    
    return TrendResult(
        client_name=client_pattern,
        scan_count=len(snapshots),
        date_range=(snapshots[0].timestamp, snapshots[-1].timestamp),
        improving_items=improving[:10],
        worsening_items=worsening[:10],
        stable_items=stable[:10],
        recurring_items=recurring[:10],
        overall_trend=overall,
        confidence=confidence
    )


def format_trend_report(result: TrendResult) -> str:
    """
    Formatiert Trend-Analyse für Konsolen-Ausgabe.
    
    Args:
        result: TrendResult
    
    Returns:
        Formatierter Report
    """
    lines = [
        f"═══════════════════════════════════════════════════════════════",
        f"  TREND-ANALYSE: {result.client_name}",
        f"═══════════════════════════════════════════════════════════════",
        f"  Scans: {result.scan_count}",
        f"  Zeitraum: {result.date_range[0].strftime('%d.%m.%Y')} - {result.date_range[1].strftime('%d.%m.%Y')}",
        f"  Gesamt-Trend: {result.overall_trend.upper()}",
        f"  Konfidenz: {result.confidence:.0%}",
        f"",
    ]
    
    if result.improving_items:
        lines.append("  ✅ VERBESSERUNG (Score sinkend):")
        for item in result.improving_items[:5]:
            lines.append(f"     - {item['label']}: {item['change_percent']:+.1f}%")
        lines.append("")
    
    if result.worsening_items:
        lines.append("  ⚠️ VERSCHLECHTERUNG (Score steigend):")
        for item in result.worsening_items[:5]:
            lines.append(f"     - {item['label']}: {item['change_percent']:+.1f}%")
        lines.append("")
    
    if result.recurring_items:
        lines.append("  🔄 WIEDERKEHREND (in mehreren Scans):")
        for item in result.recurring_items[:5]:
            lines.append(f"     - {item['label']}: {item['occurrences']}x gefunden")
        lines.append("")
    
    lines.append("═══════════════════════════════════════════════════════════════")
    
    return "\n".join(lines)


def compare_two_scans(scan1_path: str, scan2_path: str) -> Dict:
    """
    Vergleicht zwei spezifische Scans direkt.
    
    Args:
        scan1_path: Pfad zum ersten Scan (älter)
        scan2_path: Pfad zum zweiten Scan (neuer)
    
    Returns:
        Vergleichs-Dict
    """
    try:
        with open(scan1_path, 'r', encoding='utf-8') as f:
            scan1 = json.load(f)
        with open(scan2_path, 'r', encoding='utf-8') as f:
            scan2 = json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        return {"error": str(e)}
    
    # Extrahiere Items aus Legacy- und aktuellen Export-Schemata.
    items1 = {item['label']: item['score'] for item in _extract_top_items(scan1) if item.get("label")}
    items2 = {item['label']: item['score'] for item in _extract_top_items(scan2) if item.get("label")}
    
    # Vergleiche
    new_items = [k for k in items2 if k not in items1]
    resolved_items = [k for k in items1 if k not in items2]
    
    changed_items = []
    for label in items1:
        if label in items2:
            change = ((items2[label] - items1[label]) / items1[label] * 100) if items1[label] > 0 else 0
            if abs(change) > 10:
                changed_items.append({
                    "label": label,
                    "old_score": items1[label],
                    "new_score": items2[label],
                    "change_percent": round(change, 1)
                })
    
    return {
        "scan1_date": os.path.basename(scan1_path)[:15],
        "scan2_date": os.path.basename(scan2_path)[:15],
        "new_items": new_items[:10],
        "resolved_items": resolved_items[:10],
        "changed_items": sorted(changed_items, key=lambda x: abs(x["change_percent"]), reverse=True)[:10]
    }
