"""
Konfidenz-Intervalle für Morphic Engine V1

Berechnet Unsicherheits-Schätzungen für Scan-Ergebnisse basierend auf:
- Entropie-Qualität (h_level)
- Stichprobengröße (k_total)
- Score-Varianz
- Hardware-Quelle
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ConfidenceResult:
    """Ergebnis mit Konfidenz-Informationen"""
    score: float
    lower_bound: float
    upper_bound: float
    confidence_level: float  # 0.0 - 1.0
    confidence_grade: str    # A, B, C, D, F
    factors: Dict[str, float]


# Konfidenz-Faktoren für verschiedene Entropie-Quellen
ENTROPY_SOURCE_CONFIDENCE: Dict[str, float] = {
    "truerng": 0.95,      # Hardware-RNG: höchste Konfidenz
    "hid_sensor": 0.90,   # HID-Sensor: sehr gut
    "network": 0.75,      # Netzwerk-Timing: gut
    "cpu_timer": 0.60,    # CPU-Timer: akzeptabel
    "pseudo": 0.40,       # Pseudo-RNG: niedrig
    "unknown": 0.50       # Unbekannt: mittel
}


def calculate_confidence(
    score: float,
    h_level: float,
    entropy_source: str,
    k_total: int,
    score_variance: Optional[float] = None
) -> ConfidenceResult:
    """
    Berechnet Konfidenz-Intervall für einen Score.
    
    Args:
        score: Der berechnete Score
        h_level: Entropie-Level (0.0 - 1.0)
        entropy_source: Name der Entropie-Quelle
        k_total: Anzahl der getesteten Items
        score_variance: Optionale Varianz der Scores
    
    Returns:
        ConfidenceResult mit Intervall und Bewertung
    """
    # Basis-Faktoren
    source_factor = ENTROPY_SOURCE_CONFIDENCE.get(
        entropy_source.lower().replace(" ", "_"),
        ENTROPY_SOURCE_CONFIDENCE["unknown"]
    )
    
    # H-Level-Faktor (0.0-1.0 → 0.5-1.0)
    h_factor = 0.5 + (h_level * 0.5)
    
    # Sample-Size-Faktor (mehr Samples → höhere Konfidenz)
    # Logarithmische Skalierung
    sample_factor = min(1.0, math.log10(max(10, k_total)) / 3.0)
    
    # Varianz-Faktor (niedrigere Varianz → höhere Konfidenz)
    if score_variance is not None and score_variance > 0:
        variance_factor = 1.0 / (1.0 + math.sqrt(score_variance))
    else:
        variance_factor = 0.7  # Default bei unbekannter Varianz
    
    # Kombinierte Konfidenz
    confidence_level = (
        source_factor * 0.30 +
        h_factor * 0.25 +
        sample_factor * 0.25 +
        variance_factor * 0.20
    )
    
    # Intervall-Breite (inverse zur Konfidenz)
    interval_width = score * (1.0 - confidence_level) * 0.5
    
    # Bounds
    lower_bound = max(0.0, score - interval_width)
    upper_bound = score + interval_width
    
    # Grade
    if confidence_level >= 0.85:
        grade = "A"
    elif confidence_level >= 0.70:
        grade = "B"
    elif confidence_level >= 0.55:
        grade = "C"
    elif confidence_level >= 0.40:
        grade = "D"
    else:
        grade = "F"
    
    return ConfidenceResult(
        score=score,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
        confidence_level=confidence_level,
        confidence_grade=grade,
        factors={
            "entropy_source": source_factor,
            "h_level": h_factor,
            "sample_size": sample_factor,
            "variance": variance_factor
        }
    )


def calculate_batch_confidence(
    items: List[Dict],
    h_level: float,
    entropy_source: str,
    k_total: int
) -> List[Dict]:
    """
    Berechnet Konfidenz für eine Liste von Items.
    
    Args:
        items: Liste von Scan-Items mit 'score' Key
        h_level: Entropie-Level
        entropy_source: Entropie-Quelle
        k_total: Sample-Größe
    
    Returns:
        Items mit hinzugefügten Konfidenz-Informationen
    """
    if not items:
        return items
    
    # Berechne Varianz
    scores = [item.get('score', 0) for item in items]
    mean_score = sum(scores) / len(scores)
    variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
    
    result = []
    for item in items:
        score = item.get('score', 0)
        conf = calculate_confidence(
            score=score,
            h_level=h_level,
            entropy_source=entropy_source,
            k_total=k_total,
            score_variance=variance
        )
        
        enhanced_item = dict(item)
        enhanced_item['confidence'] = {
            'level': round(conf.confidence_level, 3),
            'grade': conf.confidence_grade,
            'lower': round(conf.lower_bound, 4),
            'upper': round(conf.upper_bound, 4)
        }
        result.append(enhanced_item)
    
    return result


def format_confidence_display(conf: ConfidenceResult) -> str:
    """
    Formatiert Konfidenz für Anzeige.
    
    Args:
        conf: ConfidenceResult
    
    Returns:
        Formatierte Zeichenkette
    """
    return (
        f"{conf.score:.4f} "
        f"[{conf.lower_bound:.4f} - {conf.upper_bound:.4f}] "
        f"Konfidenz: {conf.confidence_level:.1%} ({conf.confidence_grade})"
    )


def get_overall_scan_confidence(
    h_level: float,
    entropy_source: str,
    k_total: int,
    groups_count: int
) -> Dict[str, any]:
    """
    Berechnet Gesamt-Konfidenz eines Scans.
    
    Args:
        h_level: Entropie-Level
        entropy_source: Entropie-Quelle
        k_total: Sample-Größe
        groups_count: Anzahl der Gruppen
    
    Returns:
        Dict mit Gesamt-Konfidenz-Informationen
    """
    source_factor = ENTROPY_SOURCE_CONFIDENCE.get(
        entropy_source.lower().replace(" ", "_"),
        ENTROPY_SOURCE_CONFIDENCE["unknown"]
    )
    
    h_factor = 0.5 + (h_level * 0.5)
    sample_factor = min(1.0, math.log10(max(10, k_total)) / 3.0)
    coverage_factor = min(1.0, groups_count / 10.0)  # 10+ Gruppen = voll
    
    overall = (
        source_factor * 0.35 +
        h_factor * 0.30 +
        sample_factor * 0.20 +
        coverage_factor * 0.15
    )
    
    if overall >= 0.85:
        grade = "A"
        desc = "Sehr hohe Zuverlässigkeit"
    elif overall >= 0.70:
        grade = "B"
        desc = "Gute Zuverlässigkeit"
    elif overall >= 0.55:
        grade = "C"
        desc = "Mittlere Zuverlässigkeit"
    elif overall >= 0.40:
        grade = "D"
        desc = "Eingeschränkte Zuverlässigkeit"
    else:
        grade = "F"
        desc = "Niedrige Zuverlässigkeit"
    
    return {
        "overall": round(overall, 3),
        "grade": grade,
        "description": desc,
        "factors": {
            "entropy_source": f"{entropy_source} ({source_factor:.0%})",
            "h_level": f"{h_level:.3f} ({h_factor:.0%})",
            "sample_size": f"{k_total} ({sample_factor:.0%})",
            "coverage": f"{groups_count} Gruppen ({coverage_factor:.0%})"
        }
    }
