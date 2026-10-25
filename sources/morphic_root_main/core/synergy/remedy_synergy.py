#!/usr/bin/env python3
"""
Synergie-System für Remedy-Kombinationen (Grover-like Ansatz).
Findet optimale Kombinationen von Remedies basierend auf NLS-Scores und Synergie-Regeln.
"""

import numpy as np
from typing import List, Dict, Tuple, Set, Optional
from itertools import combinations
import math

class RemedySynergyAnalyzer:
    """Analysiert und findet synergetische Remedy-Kombinationen."""
    
    def __init__(self):
        # Synergie-Regeln basierend auf traditionellen Kombinationen
        self.synergy_rules = {
            # Homöopathische Synergie-Paare
            ("Bryonia", "Rhus toxicodendron"): 1.3,  # Bewegungsmodalitäten
            ("Arnica", "Belladonna"): 1.2,  # Trauma + Entzündung
            ("Nux vomica", "Lycopodium"): 1.25,  # Verdauung + Leber
            ("Pulsatilla", "Phosphorus"): 1.15,  # Sensibilität + Nervensystem
            ("Calcarea carbonica", "Sulphur"): 1.2,  # Konstitution + Entgiftung
            
            # TCM Synergie-Kombinationen
            ("Liu Wei Di Huang Wan", "Bu Zhong Yi Qi Tang"): 1.4,  # Nieren + Milz stärken
            ("Xiao Yao San", "Gan Mai Da Zao Tang"): 1.3,  # Leber-Qi + Emotionen
            ("An Shen Ding Zhi Wan", "Ding Zhi Wan"): 1.25,  # Geist beruhigen
            
            # Spagyrik Synergie-Triaden
            ("Sulfur", "Mercurius", "Sal"): 1.5,  # Klassische Trias
            ("Cuprum", "Ferrum", "Antimonium"): 1.3,  # Metall-Kombination
            
            # Meridian-Chakra Synergien
            ("Herz", "Herzchakra"): 1.4,  # Direkte Entsprechung
            ("Lunge", "Kehlchakra"): 1.3,  # Atmung + Ausdruck
            ("Leber", "Solarplexus"): 1.25,  # Entgiftung + Macht
            ("Niere", "Wurzelchakra"): 1.35,  # Grundkonstitution
            
            # Edelstein-Chakra Synergien
            ("Amethyst", "Kronenchakra"): 1.4,
            ("Rosenquarz", "Herzchakra"): 1.35,
            ("Citrin", "Solarplexus"): 1.3,
            ("Bergkristall", "Stirnchakra"): 1.25,
        }
        
        # Anti-Synergie (Kombinationen die sich schwächen)
        self.anti_synergy_rules = {
            ("Bryonia", "Rhus toxicodendron"): 0.7,  # Gegensätzliche Bewegungsmodalitäten
            ("Nux vomica", "Pulsatilla"): 0.8,  # Gegensätzliche Temperamente
            ("Belladonna", "Calcarea carbonica"): 0.75,  # Hitze vs. Kälte
        }
        
        # Gruppen-Synergien (Elemente aus derselben Kategorie verstärken sich)
        self.group_synergies = {
            "meridiane": 1.1,
            "chakren": 1.15,
            "homoeopathie_klassisch": 1.05,
            "tcm_rezepturen": 1.2,
            "spagyrik": 1.25,
            "edelsteine": 1.1,
            "farbtherapie": 1.1,
        }
    
    def calculate_synergy_score(self, items: List[Dict[str, object]]) -> float:
        """
        Berechnet den Synergie-Score für eine Kombination von Items.
        
        Args:
            items: Liste von Items mit 'label', 'score', 'group' etc.
            
        Returns:
            Synergie-Score (1.0 = neutral, >1.0 = synergetisch, <1.0 = antagonistisch)
        """
        if len(items) < 2:
            return 1.0
        
        labels = [str(item.get("label", "")) for item in items]
        groups = [str(item.get("group", "")) for item in items]
        base_scores = [float(item.get("score", 0.0)) for item in items]
        
        synergy_factor = 1.0
        
        # 1. Paarweise Synergien prüfen
        for i, j in combinations(range(len(labels)), 2):
            label_pair = tuple(sorted([labels[i], labels[j]]))
            
            # Direkte Synergie-Regel
            if label_pair in self.synergy_rules:
                synergy_factor *= self.synergy_rules[label_pair]
            
            # Anti-Synergie-Regel
            elif label_pair in self.anti_synergy_rules:
                synergy_factor *= self.anti_synergy_rules[label_pair]
        
        # 2. Gruppen-Synergien
        group_counts = {}
        for group in groups:
            if group:
                group_counts[group] = group_counts.get(group, 0) + 1
        
        for group, count in group_counts.items():
            if count > 1 and group in self.group_synergies:
                # Synergie steigt mit Anzahl der Elemente aus derselben Gruppe
                group_factor = self.group_synergies[group] ** (count - 1)
                synergy_factor *= group_factor
        
        # 3. Score-basierte Synergie (höhere Scores verstärken sich)
        if len(base_scores) > 1:
            avg_score = np.mean(base_scores)
            if avg_score > 1.0:  # Nur bei relevanten Scores
                score_factor = 1.0 + (avg_score - 1.0) * 0.1  # Moderate Verstärkung
                synergy_factor *= score_factor
        
        return synergy_factor
    
    def find_synergistic_combinations(self, 
                                    items: List[Dict[str, object]], 
                                    max_combinations: int = 20,
                                    min_combo_size: int = 2,
                                    max_combo_size: int = 4) -> List[Dict[str, object]]:
        """
        Findet die besten synergetischen Kombinationen.
        
        Args:
            items: Liste aller verfügbaren Items
            max_combinations: Maximale Anzahl zurückzugebender Kombinationen
            min_combo_size: Minimale Kombinationsgröße
            max_combo_size: Maximale Kombinationsgröße
            
        Returns:
            Liste der besten Kombinationen mit Synergie-Scores
        """
        if len(items) < min_combo_size:
            return []
        
        # Nur Items mit relevanten Scores berücksichtigen
        relevant_items = [item for item in items if float(item.get("score", 0.0)) > 0.1]
        
        if len(relevant_items) < min_combo_size:
            return []
        
        combinations_with_scores = []
        
        # Alle möglichen Kombinationen testen
        for combo_size in range(min_combo_size, min(max_combo_size + 1, len(relevant_items) + 1)):
            for combo_indices in combinations(range(len(relevant_items)), combo_size):
                combo_items = [relevant_items[i] for i in combo_indices]
                
                # Synergie-Score berechnen
                synergy_score = self.calculate_synergy_score(combo_items)
                
                # Kombinierter Score (Basis-Scores * Synergie)
                base_score_sum = sum(float(item.get("score", 0.0)) for item in combo_items)
                combined_score = base_score_sum * synergy_score
                
                # Diversitäts-Bonus (verschiedene Gruppen)
                groups = set(str(item.get("group", "")) for item in combo_items if item.get("group"))
                diversity_bonus = 1.0 + len(groups) * 0.05  # 5% pro verschiedene Gruppe
                
                final_score = combined_score * diversity_bonus
                
                combination_result = {
                    "items": combo_items,
                    "synergy_score": synergy_score,
                    "base_score_sum": base_score_sum,
                    "combined_score": combined_score,
                    "final_score": final_score,
                    "diversity": len(groups),
                    "size": len(combo_items),
                    "labels": [str(item.get("label", "")) for item in combo_items],
                    "groups": list(groups),
                }
                
                combinations_with_scores.append(combination_result)
        
        # Nach final_score sortieren
        combinations_with_scores.sort(key=lambda x: x["final_score"], reverse=True)
        
        return combinations_with_scores[:max_combinations]
    
    def explain_synergy(self, combination: Dict[str, object]) -> str:
        """
        Erklärt warum eine Kombination synergetisch ist.
        
        Args:
            combination: Kombination aus find_synergistic_combinations
            
        Returns:
            Erklärungstext
        """
        items = combination["items"]
        labels = [str(item.get("label", "")) for item in items]
        groups = [str(item.get("group", "")) for item in items]
        
        explanations = []
        
        # Paarweise Synergien erklären
        for i, j in combinations(range(len(labels)), 2):
            label_pair = tuple(sorted([labels[i], labels[j]]))
            
            if label_pair in self.synergy_rules:
                factor = self.synergy_rules[label_pair]
                explanations.append(f"{labels[i]} + {labels[j]}: Traditionelle Synergie (Faktor {factor:.2f})")
            
            elif label_pair in self.anti_synergy_rules:
                factor = self.anti_synergy_rules[label_pair]
                explanations.append(f"{labels[i]} + {labels[j]}: Mögliche Interferenz (Faktor {factor:.2f})")
        
        # Gruppen-Synergien erklären
        group_counts = {}
        for group in groups:
            if group:
                group_counts[group] = group_counts.get(group, 0) + 1
        
        for group, count in group_counts.items():
            if count > 1 and group in self.group_synergies:
                factor = self.group_synergies[group]
                explanations.append(f"Gruppe '{group}': {count} Elemente verstärken sich (Faktor {factor:.2f})")
        
        # Diversität erklären
        unique_groups = len(set(groups))
        if unique_groups > 1:
            explanations.append(f"Diversität: {unique_groups} verschiedene Gruppen für ganzheitliche Wirkung")
        
        if not explanations:
            explanations.append("Synergie basiert auf kombinierten Basis-Scores")
        
        return " | ".join(explanations)

def analyze_remedy_synergies(items: List[Dict[str, object]], 
                           max_results: int = 10) -> List[Dict[str, object]]:
    """
    Convenience-Funktion für Synergie-Analyse.
    
    Args:
        items: Liste von Items mit NLS-Scores
        max_results: Maximale Anzahl Ergebnisse
        
    Returns:
        Liste der besten synergetischen Kombinationen
    """
    analyzer = RemedySynergyAnalyzer()
    combinations = analyzer.find_synergistic_combinations(items, max_results)
    
    # Erklärungen hinzufügen
    for combo in combinations:
        combo["explanation"] = analyzer.explain_synergy(combo)
    
    return combinations
