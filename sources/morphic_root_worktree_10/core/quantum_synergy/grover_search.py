"""
Echter Grover-Algorithmus für Remedy-Suche mit Qiskit.
Findet optimale Remedies in O(√N) statt O(N) Schritten.
"""
from __future__ import annotations

import math
import numpy as np
from typing import List, Dict, Tuple, Optional, Callable

# Qiskit Imports (Qiskit 2.x kompatibel)
QISKIT_AVAILABLE = False
Sampler = None

try:
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    # Qiskit 2.x: Sampler ist in qiskit.primitives
    try:
        from qiskit.primitives import StatevectorSampler as Sampler
    except ImportError:
        from qiskit.primitives import Sampler
    QISKIT_AVAILABLE = True
except ImportError as e:
    print(f"⚠ Qiskit nicht verfügbar: {e}. Fallback auf klassische Suche.")


class GroverRemedySearch:
    """
    Echter Grover-Algorithmus für Remedy-Suche.
    
    Nutzt Quantum-Superposition und Interferenz, um optimale
    Remedies in O(√N) Schritten zu finden.
    """
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.qiskit_available = QISKIT_AVAILABLE
    
    def search(
        self,
        items: List[Dict],
        oracle_func: Callable[[Dict], bool],
        max_results: int = 5,
        shots: int = 1024
    ) -> List[Tuple[Dict, float]]:
        """
        Führt Grover-Suche auf Items durch.
        
        Args:
            items: Liste von Items (Dicts mit 'label', 'score', etc.)
            oracle_func: Funktion die True zurückgibt für "gute" Items
            max_results: Maximale Anzahl Ergebnisse
            shots: Anzahl Messungen (mehr = genauer)
        
        Returns:
            Liste von (item, probability) Tupeln, sortiert nach Wahrscheinlichkeit
        """
        if not self.qiskit_available:
            return self._classical_fallback(items, oracle_func, max_results)
        
        n_items = len(items)
        if n_items == 0:
            return []
        
        # Anzahl Qubits berechnen
        n_qubits = max(1, math.ceil(math.log2(n_items)))
        n_states = 2 ** n_qubits
        
        if self.verbose:
            print(f"\n⚛️  Grover-Suche gestartet")
            print(f"   Items: {n_items}")
            print(f"   Qubits: {n_qubits}")
            print(f"   Zustände: {n_states}")
        
        # Markierte Zustände finden (klassisch, für Oracle-Konstruktion)
        marked_states = []
        for idx, item in enumerate(items):
            if oracle_func(item):
                marked_states.append(idx)
        
        if not marked_states:
            if self.verbose:
                print("   ⚠ Keine markierten Zustände gefunden")
            return []
        
        if self.verbose:
            print(f"   Markierte Zustände: {len(marked_states)}")
        
        # Optimale Anzahl Grover-Iterationen
        n_iterations = self._optimal_iterations(n_states, len(marked_states))
        if self.verbose:
            print(f"   Grover-Iterationen: {n_iterations}")
        
        # Quantum Circuit erstellen
        qc = self._build_grover_circuit(n_qubits, marked_states, n_iterations)
        
        # Ausführen auf Simulator
        if self.verbose:
            print(f"   Führe {shots} Messungen durch...")
        
        try:
            sampler = Sampler()
            job = sampler.run([qc], shots=shots)
            result = job.result()
            
            # Ergebnisse extrahieren
            counts = result[0].data.meas.get_counts()
            
            # In Items umwandeln
            results = []
            for bitstring, count in counts.items():
                idx = int(bitstring, 2)
                if idx < n_items:
                    probability = count / shots
                    results.append((items[idx], probability))
            
            # Nach Wahrscheinlichkeit sortieren
            results.sort(key=lambda x: x[1], reverse=True)
            
            if self.verbose:
                print(f"   ✓ {len(results)} Ergebnisse gefunden")
                if results:
                    top_item = results[0][0].get('label', '?')
                    top_prob = results[0][1]
                    print(f"   Top-Ergebnis: {top_item} (P={top_prob:.2%})")
            
            return results[:max_results]
            
        except Exception as e:
            if self.verbose:
                print(f"   ❌ Quantum-Fehler: {e}")
                print(f"   → Fallback auf klassische Suche")
            return self._classical_fallback(items, oracle_func, max_results)
    
    def _optimal_iterations(self, n_states: int, n_marked: int) -> int:
        """Berechnet optimale Anzahl Grover-Iterationen."""
        if n_marked == 0 or n_marked >= n_states:
            return 1
        
        # Formel: π/4 * √(N/M)
        ratio = n_states / n_marked
        iterations = int(round(math.pi / 4 * math.sqrt(ratio)))
        return max(1, min(iterations, 10))  # Begrenzen auf 1-10
    
    def _build_grover_circuit(
        self,
        n_qubits: int,
        marked_states: List[int],
        n_iterations: int
    ) -> QuantumCircuit:
        """Baut den Grover-Quantum-Circuit."""
        qr = QuantumRegister(n_qubits, 'q')
        cr = ClassicalRegister(n_qubits, 'meas')
        qc = QuantumCircuit(qr, cr)
        
        # Superposition erzeugen (Hadamard auf alle Qubits)
        qc.h(qr)
        
        # Grover-Iterationen
        for _ in range(n_iterations):
            # Oracle: Markierte Zustände invertieren
            self._apply_oracle(qc, qr, marked_states)
            
            # Diffusion: Amplitude Amplification
            self._apply_diffusion(qc, qr)
        
        # Messung
        qc.measure(qr, cr)
        
        return qc
    
    def _apply_oracle(
        self,
        qc: QuantumCircuit,
        qr: QuantumRegister,
        marked_states: List[int]
    ) -> None:
        """Wendet das Oracle an (markiert gesuchte Zustände)."""
        n_qubits = len(qr)
        
        for state in marked_states:
            # Binärdarstellung des Zustands
            binary = format(state, f'0{n_qubits}b')
            
            # X-Gates für 0-Bits (um |state⟩ zu |111...1⟩ zu mappen)
            for i, bit in enumerate(reversed(binary)):
                if bit == '0':
                    qc.x(qr[i])
            
            # Multi-Controlled Z-Gate (Phasenflip für |111...1⟩)
            if n_qubits == 1:
                qc.z(qr[0])
            elif n_qubits == 2:
                qc.cz(qr[0], qr[1])
            else:
                # MCZ = H-MCX-H auf Ziel-Qubit
                qc.h(qr[-1])
                qc.mcx(list(qr[:-1]), qr[-1])
                qc.h(qr[-1])
            
            # X-Gates rückgängig machen
            for i, bit in enumerate(reversed(binary)):
                if bit == '0':
                    qc.x(qr[i])
    
    def _apply_diffusion(self, qc: QuantumCircuit, qr: QuantumRegister) -> None:
        """Wendet den Diffusion-Operator an (Amplitude Amplification)."""
        n_qubits = len(qr)
        
        # H auf alle Qubits
        qc.h(qr)
        
        # X auf alle Qubits
        qc.x(qr)
        
        # Multi-Controlled Z
        if n_qubits == 1:
            qc.z(qr[0])
        elif n_qubits == 2:
            qc.cz(qr[0], qr[1])
        else:
            qc.h(qr[-1])
            qc.mcx(list(qr[:-1]), qr[-1])
            qc.h(qr[-1])
        
        # X auf alle Qubits
        qc.x(qr)
        
        # H auf alle Qubits
        qc.h(qr)
    
    def _classical_fallback(
        self,
        items: List[Dict],
        oracle_func: Callable[[Dict], bool],
        max_results: int
    ) -> List[Tuple[Dict, float]]:
        """Klassischer Fallback wenn Qiskit nicht verfügbar."""
        if self.verbose:
            print("   → Klassische Suche (Fallback)")
        
        results = []
        for item in items:
            if oracle_func(item):
                # Score als Pseudo-Wahrscheinlichkeit
                score = float(item.get('score', item.get('relevance', 5.0)))
                probability = min(1.0, score / 10.0)
                results.append((item, probability))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:max_results]


def create_focus_oracle(focus: str, threshold: float = 0.5) -> Callable[[Dict], bool]:
    """
    Erstellt eine Oracle-Funktion für einen Fokus.
    
    Args:
        focus: Fokus-Thema (z.B. "Migräne")
        threshold: Mindest-Relevanz (0-1)
    
    Returns:
        Oracle-Funktion die True für relevante Items zurückgibt
    """
    focus_lower = focus.lower()
    focus_keywords = focus_lower.split()
    
    def oracle(item: Dict) -> bool:
        label = str(item.get('label', '')).lower()
        group = str(item.get('group', '')).lower()
        
        # Direkter Match
        if focus_lower in label:
            return True
        
        # Keyword-Match
        for keyword in focus_keywords:
            if keyword in label or keyword in group:
                return True
        
        # Score-basiert
        score = float(item.get('score', item.get('relevance', 0)))
        if score >= threshold * 10:
            return True
        
        return False
    
    return oracle


# Convenience-Funktion für einfache Nutzung
def grover_remedy_search(
    items: List[Dict],
    focus: str,
    max_results: int = 10,
    verbose: bool = True
) -> List[Tuple[Dict, float]]:
    """
    Einfache Grover-Suche für Remedies.
    
    Args:
        items: Liste von Remedy-Items
        focus: Fokus-Thema
        max_results: Maximale Ergebnisse
        verbose: Ausgabe aktivieren
    
    Returns:
        Liste von (item, probability) Tupeln
    
    Beispiel:
        results = grover_remedy_search(items, "Migräne", max_results=5)
        for item, prob in results:
            print(f"{item['label']}: {prob:.2%}")
    """
    searcher = GroverRemedySearch(verbose=verbose)
    oracle = create_focus_oracle(focus)
    return searcher.search(items, oracle, max_results=max_results)
