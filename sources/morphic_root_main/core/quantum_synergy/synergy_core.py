"""
Quantum-Synergy Core
Klassische Synergy-Score Berechnung
"""

from typing import List, Dict, Tuple, Optional
import math
import numpy as np

from ..subgroups.procedural_groups import SCHUMANN_F0, PHI
from ..focus_synonyms import expand_focus_keywords, get_canonical_focus
from ..adaptive_weights import get_adaptive_weights
from ..multi_focus import expand_multi_focus_keywords, get_multi_focus_weights


class SynergyCalculator:
    """Berechnet synergistische Wirkungen zwischen Items"""
    
    def __init__(self, use_adaptive_weights: bool = True):
        self.phi = PHI
        self.schumann = SCHUMANN_F0
        self.use_adaptive_weights = use_adaptive_weights
    
    def calculate_synergy_score(
        self,
        items: List[Dict],
        focus: str,
        scan_results: Dict[str, float] = None
    ) -> float:
        """
        Berechnet Synergy-Score für Item-Kombination
        
        Args:
            items: Liste von Items (Dicts mit 'label', 'rates', 'frequency')
            focus: Fokus-Thema (z.B. "Migräne", "Erschöpfung")
            scan_results: Optional - Scan-Ergebnisse {label: score}
        
        Returns:
            Synergy-Score (0.0 - 10.0)
        """
        if not items:
            return 0.0
        
        # Komponenten des Synergy-Scores
        individual_scores = self._calculate_individual_scores(items, scan_results)
        resonance = self._calculate_resonance_amplification(items)
        harmony = self._calculate_frequency_harmony(items)
        relevance = self._calculate_focus_relevance(items, focus)
        
        # Adaptive Gewichtung basierend auf Fokus-Kategorie
        if self.use_adaptive_weights and focus:
            weights = get_adaptive_weights(focus)
        else:
            # Standard-Gewichtung
            weights = {
                "individual": 0.25,
                "resonance": 0.25,
                "harmony": 0.20,
                "relevance": 0.30
            }
        
        synergy_score = (
            weights["individual"] * individual_scores +
            weights["resonance"] * resonance +
            weights["harmony"] * harmony +
            weights["relevance"] * relevance
        )
        
        return min(synergy_score, 10.0)
    
    def _calculate_individual_scores(
        self,
        items: List[Dict],
        scan_results: Dict[str, float] = None
    ) -> float:
        """
        Berechnet Summe der Einzelwirkungen
        
        Returns:
            Score 0.0 - 10.0
        """
        if not scan_results:
            # Fallback: Durchschnittliche Annahme
            return 5.0
        
        total_score = 0.0
        found_items = 0
        
        for item in items:
            label = item['label']
            if label in scan_results:
                total_score += scan_results[label]
                found_items += 1
        
        if found_items == 0:
            return 5.0
        
        # Normalisiere auf 0-10
        avg_score = total_score / found_items
        return min(avg_score, 10.0)
    
    def _calculate_resonance_amplification(self, items: List[Dict]) -> float:
        """
        Berechnet Resonanz-Verstärkung nach Bruce Copen
        
        Prinzip:
        - Ähnliche Frequenzen verstärken sich
        - Harmonische Verhältnisse (Oktaven, Quinten) verstärken sich
        - Phi-Verhältnisse verstärken sich besonders
        
        Returns:
            Score 0.0 - 10.0
        """
        if len(items) < 2:
            return 5.0
        
        frequencies = [item['frequency'] for item in items]
        amplification = 0.0
        comparisons = 0
        
        for i in range(len(frequencies)):
            for j in range(i + 1, len(frequencies)):
                f1, f2 = frequencies[i], frequencies[j]
                
                # Verhältnis berechnen
                ratio = max(f1, f2) / min(f1, f2) if min(f1, f2) > 0 else 1.0
                
                # Prüfe harmonische Verhältnisse
                amp = 0.0
                
                # Oktaven (2:1, 4:1, 8:1)
                for octave in [2.0, 4.0, 8.0]:
                    if abs(ratio - octave) < 0.1:
                        amp = max(amp, 8.0)
                
                # Quinten (3:2)
                if abs(ratio - 1.5) < 0.1:
                    amp = max(amp, 7.0)
                
                # Quarten (4:3)
                if abs(ratio - 1.333) < 0.1:
                    amp = max(amp, 6.0)
                
                # Phi-Verhältnis (1.618)
                if abs(ratio - self.phi) < 0.1:
                    amp = max(amp, 9.0)
                
                # Ähnliche Frequenzen (< 10% Unterschied)
                if abs(ratio - 1.0) < 0.1:
                    amp = max(amp, 7.0)
                
                # Basis-Resonanz (immer vorhanden)
                if amp == 0.0:
                    amp = 3.0
                
                amplification += amp
                comparisons += 1
        
        if comparisons == 0:
            return 5.0
        
        # Normalisiere
        avg_amplification = amplification / comparisons
        return min(avg_amplification, 10.0)
    
    def _calculate_frequency_harmony(self, items: List[Dict]) -> float:
        """
        Berechnet Frequenz-Harmonien (Phi, Schumann)
        
        Returns:
            Score 0.0 - 10.0
        """
        if not items:
            return 5.0
        
        frequencies = [item['frequency'] for item in items]
        harmony_score = 0.0
        
        for freq in frequencies:
            # Prüfe Nähe zu Schumann-Resonanz und Harmonischen
            schumann_harmonics = [
                self.schumann * (2 ** n) for n in range(-3, 10)
            ]
            
            min_distance = min(
                abs(freq - harmonic) / harmonic
                for harmonic in schumann_harmonics
                if harmonic > 0
            )
            
            # Score basierend auf Nähe (je näher, desto besser)
            if min_distance < 0.05:  # < 5% Abweichung
                harmony_score += 10.0
            elif min_distance < 0.1:  # < 10% Abweichung
                harmony_score += 8.0
            elif min_distance < 0.2:  # < 20% Abweichung
                harmony_score += 6.0
            else:
                harmony_score += 3.0
        
        # Normalisiere
        avg_harmony = harmony_score / len(frequencies)
        return min(avg_harmony, 10.0)
    
    def _calculate_focus_relevance(self, items: List[Dict], focus: str) -> float:
        """
        Berechnet Relevanz zum Fokus-Thema mit Synonym-Erweiterung und Multi-Fokus.
        
        Unterstützt:
        - Einzel-Fokus: "Migräne"
        - Multi-Fokus: "Migräne + Stress" oder "Verdauung, Müdigkeit"
        
        Returns:
            Score 0.0 - 10.0
        """
        if not focus:
            return 5.0
        
        # Multi-Fokus-Support: erweitert um alle Synonyme aller Fokus-Teile
        focus_keywords = expand_multi_focus_keywords(focus)
        canonical_focus = get_canonical_focus(focus).lower()
        
        relevance_score = 0.0
        
        for item in items:
            label_lower = item['label'].lower()
            group_lower = item['group'].lower()
            
            # Direkte Übereinstimmung mit kanonischem Begriff
            if canonical_focus in label_lower:
                relevance_score += 10.0
                continue
            
            # Übereinstimmung mit Synonymen (höher gewichtet)
            synonym_matches = sum(1 for kw in focus_keywords if kw.lower() in label_lower)
            if synonym_matches > 0:
                relevance_score += min(synonym_matches * 4.0, 10.0)
                continue
            
            # Gruppen-Relevanz (mit Synonymen)
            group_matches = sum(1 for kw in focus_keywords if kw.lower() in group_lower)
            if group_matches > 0:
                relevance_score += min(5.0 + group_matches, 8.0)
                continue
            
            # Basis-Relevanz
            relevance_score += 2.0
        
        # Normalisiere
        avg_relevance = relevance_score / len(items)
        return min(avg_relevance, 10.0)
    
    def _has_duplicates(self, items: List[Dict]) -> bool:
        """
        Prüft ob eine Kombination doppelte Items enthält
        
        Args:
            items: Liste von Items
        
        Returns:
            True wenn Duplikate vorhanden
        """
        labels = [item.get('label', '') for item in items]
        return len(labels) != len(set(labels))
    
    def rank_combinations(
        self,
        combinations: List[Tuple[List[Dict], float]],
        top_n: int = 5
    ) -> List[Tuple[List[Dict], float]]:
        """
        Rankt Kombinationen nach Score
        
        Args:
            combinations: Liste von (items, score) Tupeln
            top_n: Anzahl Top-Ergebnisse
        
        Returns:
            Top-N Kombinationen sortiert nach Score (ohne Duplikate)
        """
        # Filtere Kombinationen mit Duplikaten heraus
        unique_combinations = [
            (items, score) for items, score in combinations
            if not self._has_duplicates(items)
        ]
        
        # Sortiere nach Score (absteigend)
        sorted_combinations = sorted(
            unique_combinations,
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_combinations[:top_n]
