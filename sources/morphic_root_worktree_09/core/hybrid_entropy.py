"""
Hybrid-Entropie-Modus für Morphic Engine V1

Kombiniert mehrere Entropie-Quellen für höhere Qualität und Robustheit.
Statt eine Quelle auszuwählen, werden alle verfügbaren Quellen
parallel gesampled und intelligent kombiniert.
"""

import math
import time
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class EntropyReading:
    """Einzelne Entropie-Messung"""
    source: str
    h_level: float
    quality: float
    timestamp: float
    healthy: bool


@dataclass
class HybridEntropyResult:
    """Kombiniertes Entropie-Ergebnis"""
    combined_h_level: float
    quality_score: float
    sources_used: List[str]
    readings: List[EntropyReading]
    method: str


# Qualitäts-Gewichtung pro Quelle (höher = besser)
SOURCE_QUALITY_WEIGHTS: Dict[str, float] = {
    "truerng": 1.00,      # Hardware-RNG: beste Qualität
    "hid_sensor": 0.90,   # HID-Sensor: sehr gut
    "network": 0.70,      # Netzwerk-Timing: gut
    "cpu_timer": 0.50,    # CPU-Timer: akzeptabel
    "pseudo": 0.20,       # Pseudo-RNG: nur Fallback
}


def sample_all_sources() -> List[EntropyReading]:
    """
    Sampled alle verfügbaren Entropie-Quellen.
    
    Returns:
        Liste von EntropyReading für jede Quelle
    """
    readings = []
    timestamp = time.time()
    
    # Dynamischer Import um Zirkularität zu vermeiden
    try:
        from providers.hardware.entropy_sources import (
            TrueRngSource, HidSource, NetworkSource, CpuTimerSource
        )
        
        sources = [
            ("truerng", TrueRngSource),
            ("hid_sensor", HidSource),
            ("network", NetworkSource),
            ("cpu_timer", CpuTimerSource),
        ]
        
        for name, source_class in sources:
            try:
                source = source_class()
                is_healthy = source.healthy()
                h_level = source.sample_h_level() if is_healthy else 0.0
                quality = SOURCE_QUALITY_WEIGHTS.get(name, 0.5)
                
                readings.append(EntropyReading(
                    source=name,
                    h_level=h_level,
                    quality=quality if h_level > 0 else 0.0,
                    timestamp=timestamp,
                    healthy=is_healthy and h_level > 0
                ))
            except Exception:
                readings.append(EntropyReading(
                    source=name,
                    h_level=0.0,
                    quality=0.0,
                    timestamp=timestamp,
                    healthy=False
                ))
    
    except ImportError:
        # Fallback wenn Module nicht verfügbar
        pass
    
    return readings


def weighted_entropy_mix(readings: List[EntropyReading]) -> HybridEntropyResult:
    """
    Kombiniert Entropie-Readings mit gewichteter Mischung.
    
    Args:
        readings: Liste von EntropyReadings
    
    Returns:
        HybridEntropyResult mit kombiniertem h_level
    """
    # Filtere gesunde Quellen mit h_level > 0
    healthy_readings = [r for r in readings if r.healthy and r.h_level > 0]
    
    if not healthy_readings:
        # Kein gesunder Quelle: Pseudo-Fallback
        import random
        return HybridEntropyResult(
            combined_h_level=random.random() * 0.3,
            quality_score=0.2,
            sources_used=["pseudo_fallback"],
            readings=readings,
            method="fallback"
        )
    
    # Gewichtete Kombination
    total_weight = sum(r.quality for r in healthy_readings)
    weighted_sum = sum(r.h_level * r.quality for r in healthy_readings)
    
    combined = weighted_sum / total_weight
    
    # Qualitäts-Score: Durchschnitt der verwendeten Quellen-Qualitäten
    quality_score = sum(r.quality for r in healthy_readings) / len(healthy_readings)
    
    # Bonus für mehrere Quellen (Diversität)
    if len(healthy_readings) > 1:
        diversity_bonus = min(0.1, 0.03 * len(healthy_readings))
        quality_score = min(1.0, quality_score + diversity_bonus)
    
    return HybridEntropyResult(
        combined_h_level=combined,
        quality_score=quality_score,
        sources_used=[r.source for r in healthy_readings],
        readings=readings,
        method="weighted_mix"
    )


def xor_entropy_mix(readings: List[EntropyReading]) -> HybridEntropyResult:
    """
    Kombiniert Entropie mittels XOR-Operation für maximale Unvorhersagbarkeit.
    
    Args:
        readings: Liste von EntropyReadings
    
    Returns:
        HybridEntropyResult
    """
    healthy_readings = [r for r in readings if r.healthy and r.h_level > 0]
    
    if not healthy_readings:
        import random
        return HybridEntropyResult(
            combined_h_level=random.random() * 0.3,
            quality_score=0.2,
            sources_used=["pseudo_fallback"],
            readings=readings,
            method="xor_fallback"
        )
    
    # Konvertiere h_levels zu Integers für XOR
    def to_int(h: float) -> int:
        return int(h * 1_000_000_000)
    
    def from_int(i: int) -> float:
        return (i % 1_000_000_000) / 1_000_000_000
    
    # XOR alle Werte
    xor_result = 0
    for r in healthy_readings:
        xor_result ^= to_int(r.h_level)
    
    combined = from_int(xor_result)
    
    # Qualität basiert auf Anzahl der Quellen
    quality_score = min(1.0, 0.5 + 0.15 * len(healthy_readings))
    
    return HybridEntropyResult(
        combined_h_level=combined,
        quality_score=quality_score,
        sources_used=[r.source for r in healthy_readings],
        readings=readings,
        method="xor_mix"
    )


def get_hybrid_h_level(method: str = "weighted") -> Tuple[float, Dict]:
    """
    Hauptfunktion: Liefert hybriden h_level mit Metadaten.
    
    Args:
        method: "weighted" oder "xor"
    
    Returns:
        Tuple von (h_level, metadata_dict)
    """
    readings = sample_all_sources()
    
    if method == "xor":
        result = xor_entropy_mix(readings)
    else:
        result = weighted_entropy_mix(readings)
    
    metadata = {
        "h_level": result.combined_h_level,
        "quality": result.quality_score,
        "sources": result.sources_used,
        "method": result.method,
        "source_count": len(result.sources_used),
        "readings": [
            {"source": r.source, "h_level": r.h_level, "healthy": r.healthy}
            for r in result.readings
        ]
    }
    
    return result.combined_h_level, metadata


def format_hybrid_display(metadata: Dict) -> str:
    """
    Formatiert Hybrid-Entropie für Konsolen-Ausgabe.
    
    Args:
        metadata: Metadaten von get_hybrid_h_level
    
    Returns:
        Formatierte Zeichenkette
    """
    lines = [
        f"Hybrid-Entropie: {metadata['h_level']:.4f} "
        f"(Qualität: {metadata['quality']:.0%}, Methode: {metadata['method']})",
        f"  Aktive Quellen: {', '.join(metadata['sources'])}"
    ]
    
    for r in metadata.get('readings', []):
        status = "✓" if r['healthy'] else "✗"
        lines.append(f"    {status} {r['source']}: {r['h_level']:.4f}")
    
    return "\n".join(lines)
