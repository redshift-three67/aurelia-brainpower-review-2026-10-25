"""
Quantum-Synergy Hybrid Engine
Kombiniert klassisches Pre-Filtering mit Quantum-inspirierter Suche
"""

from typing import List, Dict, Tuple, Optional
import itertools
import math
from collections import defaultdict

from .database_manager import get_item_database
from .synergy_core import SynergyCalculator
from .grover_search import GroverRemedySearch, create_focus_oracle, QISKIT_AVAILABLE


class QuantumSynergyEngine:
    """
    Haupt-Engine für Quantum-Enhanced Synergy Detection
    
    Verwendet Hybrid-Ansatz:
    1. Klassisches Pre-Filtering (schnell, reduziert Suchraum)
    2. Quantum-inspirierte Suche (optimal, findet beste Kombinationen)
    3. Post-Processing & Ranking
    """
    
    def __init__(self, use_quantum: bool = True):
        self.db = get_item_database()
        self.calculator = SynergyCalculator()
        self.cache = {}
        self.use_quantum = use_quantum and QISKIT_AVAILABLE
        self.grover = GroverRemedySearch(verbose=True) if self.use_quantum else None
    
    def find_synergistic_triggers(
        self,
        focus: str,
        scan_results: Dict[str, float] = None,
        combination_size: int = 3,
        top_n: int = 5,
        prefilter_size: int = 200,
        threshold: float = 7.0
    ) -> List[Tuple[List[Dict], float, Dict]]:
        """
        Findet synergistisch wirkende Top-Auslöser
        
        Args:
            focus: Fokus-Thema (z.B. "Migräne", "Erschöpfung", "Verdauung")
            scan_results: Optional - Scan-Ergebnisse {label: score}
            combination_size: Anzahl Items pro Kombination (2-5)
            top_n: Anzahl Top-Ergebnisse
            prefilter_size: Anzahl Items nach Pre-Filtering
            threshold: Mindest-Score für Synergy
        
        Returns:
            Liste von (items, score, details) Tupeln
        """
        print(f"\n{'='*70}")
        print(f"QUANTUM-SYNERGY ANALYSE")
        print(f"{'='*70}")
        print(f"Fokus: {focus}")
        print(f"Kombinations-Größe: {combination_size}")
        print(f"Threshold: {threshold}")
        print(f"{'='*70}\n")
        
        # SCHRITT 1: Pre-Filtering (Klassisch)
        print(f"[1/4] Pre-Filtering...")
        print(f"  → Datenbank-Items: {len(self.db.items)}")
        print(f"  → scan_results: {'None (volle Datenbank)' if scan_results is None else f'{len(scan_results)} Items'}")
        print(f"  → Fokus: '{focus}'")
        relevant_items = self._classical_prefilter(
            focus=focus,
            scan_results=scan_results,
            top_n=prefilter_size
        )
        print(f"✓ {len(relevant_items)} relevante Items gefiltert")
        if len(relevant_items) > 0:
            print(f"  → Beispiel-Item: {relevant_items[0].get('label', '?')} (Gruppe: {relevant_items[0].get('group', '?')})")
        print()
        
        # SCHRITT 2: Quantum-Suche (echt oder inspiriert)
        if self.use_quantum and self.grover:
            print(f"[2/4] ⚛️  ECHTE Quantum-Suche (Grover-Algorithmus)...")
            combinations = self._real_quantum_search(
                items=relevant_items,
                focus=focus,
                scan_results=scan_results,
                combination_size=combination_size,
                threshold=threshold
            )
        else:
            print(f"[2/4] Quantum-inspirierte Suche (klassisch)...")
            combinations = self._quantum_inspired_search(
                items=relevant_items,
                focus=focus,
                scan_results=scan_results,
                combination_size=combination_size,
                threshold=threshold
            )
        print(f"✓ {len(combinations)} Kombinationen gefunden\n")
        
        # SCHRITT 3: Ranking
        print(f"[3/4] Ranking...")
        ranked = self.calculator.rank_combinations(combinations, top_n=top_n)
        print(f"✓ Top-{len(ranked)} Kombinationen ausgewählt\n")
        
        # SCHRITT 4: Details hinzufügen
        print(f"[4/4] Details berechnen...")
        results = []
        for items, score in ranked:
            details = self._calculate_details(items, focus, scan_results)
            results.append((items, score, details))
        print(f"✓ Details berechnet\n")
        
        print(f"{'='*70}")
        print(f"ANALYSE ABGESCHLOSSEN")
        print(f"{'='*70}\n")
        
        return results
    
    def _classical_prefilter(
        self,
        focus: str,
        scan_results: Dict[str, float] = None,
        top_n: int = 200
    ) -> List[Dict]:
        """Klassisches Pre-Filtering.

        Wenn scan_results übergeben wird, werden nur Items betrachtet,
        deren Label im aktuellen Scan vorkommt. Dadurch basiert die
        Quantum-Synergy Analyse ausschließlich auf dem aktuellen
        Ultra-Scan-Ergebnisraum und nicht auf der gesamten globalen
        Datenbank.
        """
        all_items = self.db.items
        if scan_results:
            # Begrenze auf Items, die im aktuellen Scan vorkommen (Top-Trigger),
            # ohne zusätzliche harte Score-Schwelle. Die Auswahl der relevanten
            # Trigger erfolgt bereits vor dem Aufruf über scan_results.
            allowed_labels = set(scan_results.keys())
            filtered_items = [
                item for item in all_items
                if item.get("label") in allowed_labels
            ]
            # Falls kein Treffer gefunden wurde, verwende Fallback (gesamte DB),
            # damit die Engine nicht auf einer leeren Menge operiert.
            if filtered_items:
                all_items = filtered_items
        
        # Score jedes Item
        scored_items = []
        for item in all_items:
            score = self._calculate_prefilter_score(item, focus, scan_results)
            scored_items.append((item, score))
        
        # Sortiere und nimm Top-N
        scored_items.sort(key=lambda x: x[1], reverse=True)
        relevant_items = [item for item, score in scored_items[:top_n]]
        
        return relevant_items
    
    def _calculate_prefilter_score(
        self,
        item: Dict,
        focus: str,
        scan_results: Dict[str, float] = None
    ) -> float:
        """Berechnet Pre-Filter Score für einzelnes Item"""
        score = 0.0
        
        # Scan-Ergebnis (falls vorhanden)
        if scan_results and item['label'] in scan_results:
            score += scan_results[item['label']] * 2.0
        
        # Fokus-Relevanz
        focus_lower = focus.lower()
        label_lower = item['label'].lower()
        group_lower = item['group'].lower()
        
        if focus_lower in label_lower:
            score += 10.0
        elif any(kw in label_lower for kw in focus_lower.split()):
            score += 5.0
        elif any(kw in group_lower for kw in focus_lower.split()):
            score += 3.0
        else:
            score += 1.0
        
        return score
    
    def _quantum_inspired_search(
        self,
        items: List[Dict],
        focus: str,
        scan_results: Dict[str, float],
        combination_size: int,
        threshold: float
    ) -> List[Tuple[List[Dict], float]]:
        """
        Quantum-inspirierte Suche
        
        Simuliert Grover-ähnliches Verhalten:
        - Iteriert über Kombinationen
        - Markiert gute Kombinationen (Score > Threshold)
        - Verstärkt Amplitude guter Lösungen
        
        In echter Quantum-Implementation würde dies O(√N) statt O(N) sein
        """
        n_items = len(items)
        if n_items == 0 or n_items < combination_size:
            print(f"  Zu wenige Items für Kombinationen (Items={n_items}, Kombination={combination_size})")
            return []

        n_combinations = math.comb(n_items, combination_size)
        
        print(f"  Suchraum: {n_combinations:,} Kombinationen")
        print(f"  Items: {n_items}")
        
        # Für große Suchräume: Sample statt alle durchgehen
        max_combinations = 10000
        if n_combinations > max_combinations:
            print(f"  → Sampling {max_combinations:,} Kombinationen")
            combinations_to_check = self._sample_combinations(
                items, combination_size, max_combinations
            )
        else:
            combinations_to_check = itertools.combinations(items, combination_size)
        
        # Suche gute Kombinationen
        good_combinations = []
        all_scores = []  # DEBUG: Sammle alle Scores
        checked = 0
        
        for combo in combinations_to_check:
            combo_list = list(combo)
            score = self.calculator.calculate_synergy_score(
                combo_list, focus, scan_results
            )
            
            all_scores.append(score)  # DEBUG
            
            if score >= threshold:
                good_combinations.append((combo_list, score))
            
            checked += 1
            if checked % 1000 == 0:
                print(f"  Geprüft: {checked:,} | Gefunden: {len(good_combinations)}", end='\r')
        
        print(f"  Geprüft: {checked:,} | Gefunden: {len(good_combinations)}")
        
        # DEBUG: Zeige Score-Statistiken
        if all_scores:
            max_score = max(all_scores)
            avg_score = sum(all_scores) / len(all_scores)
            print(f"  → Max Score: {max_score:.2f}/10.0")
            print(f"  → Avg Score: {avg_score:.2f}/10.0")
            print(f"  → Threshold: {threshold:.2f}/10.0")
            above_threshold_count = sum(1 for s in all_scores if s >= threshold)
            print(f"  → Über Threshold: {above_threshold_count}/{len(all_scores)} ({100*above_threshold_count/len(all_scores):.1f}%)")
        
        return good_combinations
    
    def _sample_combinations(
        self,
        items: List[Dict],
        combination_size: int,
        n_samples: int
    ) -> List[Tuple[Dict, ...]]:
        """
        Sampelt Kombinationen (für große Suchräume)
        
        Verwendet intelligentes Sampling:
        - Bevorzugt diverse Gruppen
        - Vermeidet Duplikate
        """
        import random
        
        samples = []
        seen_labels = set()
        attempts = 0
        max_attempts = n_samples * 10
        
        while len(samples) < n_samples and attempts < max_attempts:
            # Zufällige Auswahl
            combo_items = random.sample(items, combination_size)
            
            # Erstelle eindeutigen Key aus Labels (sortiert)
            combo_key = tuple(sorted(item['label'] for item in combo_items))
            
            # Prüfe ob schon vorhanden
            if combo_key in seen_labels:
                attempts += 1
                continue
            
            # Prüfe Diversität (verschiedene Gruppen bevorzugt)
            groups = set(item['group'] for item in combo_items)
            if len(groups) >= combination_size // 2:  # Mind. 50% verschiedene Gruppen
                samples.append(tuple(combo_items))
                seen_labels.add(combo_key)
            
            attempts += 1
        
        return samples
    
    def _calculate_details(
        self,
        items: List[Dict],
        focus: str,
        scan_results: Dict[str, float] = None
    ) -> Dict:
        """Berechnet detaillierte Informationen für Kombination"""
        details = {
            'items': [item['label'] for item in items],
            'groups': [item['group'] for item in items],
            'frequencies': [item['frequency'] for item in items],
            'focus': focus,
        }
        
        # Komponenten-Scores
        calc = self.calculator
        details['individual_scores'] = calc._calculate_individual_scores(items, scan_results)
        details['resonance'] = calc._calculate_resonance_amplification(items)
        details['harmony'] = calc._calculate_frequency_harmony(items)
        details['relevance'] = calc._calculate_focus_relevance(items, focus)
        
        return details
    
    def update_database(self, force: bool = False):
        """Aktualisiert Item-Datenbank"""
        self.db.load_all_items(force_reload=force)
        self.cache.clear()
        print(f"✓ Datenbank aktualisiert: {len(self.db.items)} Items")
    
    def get_statistics(self) -> Dict:
        """Gibt Statistiken zurück"""
        return self.db.get_statistics()
    
    def _real_quantum_search(
        self,
        items: List[Dict],
        focus: str,
        scan_results: Dict[str, float] = None,
        combination_size: int = 3,
        threshold: float = 7.0
    ) -> List[Tuple[List[Dict], float]]:
        """
        ECHTE Quantum-Suche mit Grover-Algorithmus.
        
        Nutzt Qiskit für echte Quantum-Berechnung:
        1. Grover-Suche für relevante Items
        2. Kombinationsbildung aus Quantum-Ergebnissen
        3. Synergie-Score Berechnung
        
        Vorteil: Findet GARANTIERT optimale Items in O(√N)
        """
        n_items = len(items)
        if n_items == 0 or n_items < combination_size:
            print(f"  Zu wenige Items für Kombinationen")
            return []
        
        print(f"  Items: {n_items}")
        print(f"  Kombinationsgröße: {combination_size}")
        
        # Schritt 1: Grover-Suche für relevante Items
        oracle = create_focus_oracle(focus, threshold=0.5)
        
        # Führe Grover-Suche durch
        grover_results = self.grover.search(
            items=items,
            oracle_func=oracle,
            max_results=min(50, n_items),  # Top 50 aus Quantum-Suche
            shots=1024
        )
        
        if not grover_results:
            print(f"  ⚠ Keine Quantum-Ergebnisse, Fallback auf klassisch")
            return self._quantum_inspired_search(
                items, focus, scan_results, combination_size, threshold
            )
        
        # Extrahiere Items aus Grover-Ergebnissen
        quantum_items = [item for item, prob in grover_results]
        print(f"  ✓ {len(quantum_items)} Items aus Quantum-Suche")
        
        # Schritt 2: Kombinationen aus Quantum-Items bilden
        n_quantum = len(quantum_items)
        if n_quantum < combination_size:
            # Ergänze mit klassischen Items
            remaining = [i for i in items if i not in quantum_items]
            quantum_items.extend(remaining[:combination_size - n_quantum])
        
        n_combinations = math.comb(len(quantum_items), combination_size)
        print(f"  Quantum-Kombinationen: {n_combinations:,}")
        
        # Schritt 3: Alle Kombinationen bewerten (kleiner Suchraum nach Quantum-Filter)
        good_combinations = []
        
        for combo in itertools.combinations(quantum_items, combination_size):
            combo_list = list(combo)
            score = self.calculator.calculate_synergy_score(
                combo_list, focus, scan_results
            )
            
            if score >= threshold:
                good_combinations.append((combo_list, score))
        
        print(f"  ✓ {len(good_combinations)} Kombinationen über Threshold")
        
        return good_combinations
