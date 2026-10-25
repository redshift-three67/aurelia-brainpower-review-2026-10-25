"""Quick Synergy Test für Schwindel"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.quantum_synergy import QuantumSynergyEngine

print("="*70)
print("QUICK SYNERGY TEST - SCHWINDEL")
print("="*70)

# Simulierte Top-Items aus Scan
scan_results = {
    "Schwindel (vestibulär)": 8.5,
    "Schwindel (zentral)": 7.8,
    "HWS-Syndrom": 8.2,
    "Nackenschmerzen chronisch": 7.5,
    "Vitamin B12-Mangel": 7.8,
    "Eisen-Mangel (Anämie)": 7.2,
    "Magnesium-Mangel": 7.5,
    "Kreislauf-Dysregulation": 7.0,
}

engine = QuantumSynergyEngine()

print("\nFühre Quantum-Synergy Analyse durch...")
print("Fokus: Schwindel")
print("Items: 8 (simuliert)")
print()

results = engine.find_synergistic_triggers(
    focus="Schwindel",
    scan_results=scan_results,
    combination_size=3,
    top_n=3,
    prefilter_size=100,
    threshold=6.0
)

print("\n" + "="*70)
print(f"ERGEBNISSE: {len(results)} Kombinationen gefunden")
print("="*70)

for i, (items, score, details) in enumerate(results, 1):
    print(f"\n#{i} - Score: {score:.2f}/10.0")
    print("-"*70)
    for item in items:
        print(f"  • {item['label']}")
    print(f"\nKomponenten:")
    print(f"  Einzelwirkungen:  {details['individual_scores']:.2f}")
    print(f"  Resonanz:         {details['resonance']:.2f}")
    print(f"  Harmonie:         {details['harmony']:.2f}")
    print(f"  Relevanz:         {details['relevance']:.2f}")

print("\n" + "="*70)
print("TEST ABGESCHLOSSEN")
print("="*70)
