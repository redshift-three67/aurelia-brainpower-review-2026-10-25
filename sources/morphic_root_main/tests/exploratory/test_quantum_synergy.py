"""
Test-Script für Quantum-Synergy
Demonstriert Verwendung und testet Funktionalität
"""

import sys
from pathlib import Path

# Füge Projektverzeichnis zum Path hinzu
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.quantum_synergy import QuantumSynergyEngine


def print_results(results, focus):
    """Gibt Ergebnisse formatiert aus"""
    print(f"\n{'='*70}")
    print(f"TOP-{len(results)} SYNERGISTISCHE KOMBINATIONEN")
    print(f"Fokus: {focus}")
    print(f"{'='*70}\n")
    
    for i, (items, score, details) in enumerate(results, 1):
        print(f"#{i} - Score: {score:.2f}/10.0")
        print(f"{'─'*70}")
        
        # Items
        print(f"Items:")
        for item in items:
            print(f"  • {item['label']} ({item['group']})")
        
        # Details
        print(f"\nKomponenten:")
        print(f"  • Einzelwirkungen:     {details['individual_scores']:.2f}/10.0")
        print(f"  • Resonanz-Verstärkung: {details['resonance']:.2f}/10.0")
        print(f"  • Frequenz-Harmonien:   {details['harmony']:.2f}/10.0")
        print(f"  • Fokus-Relevanz:       {details['relevance']:.2f}/10.0")
        
        # Frequenzen
        print(f"\nFrequenzen:")
        for item, freq in zip(items, details['frequencies']):
            print(f"  • {item['label'][:40]:40s} {freq:8.2f} Hz")
        
        print(f"\n{'='*70}\n")


def test_migraine():
    """Test: Migräne"""
    print("\n" + "="*70)
    print("TEST 1: MIGRÄNE")
    print("="*70)
    
    engine = QuantumSynergyEngine()
    
    # Simulierte Scan-Ergebnisse
    scan_results = {
        "Kopfschmerzen (Stirn)": 8.5,
        "Kopfschmerzen (Schläfen)": 9.2,
        "Migräne (mit Aura)": 7.8,
        "Übelkeit": 6.5,
        "Lichtempfindlichkeit": 7.2,
        "Magnesium-Mangel": 8.0,
        "Vitamin B2-Mangel": 7.5,
    }
    
    results = engine.find_synergistic_triggers(
        focus="Migräne",
        scan_results=scan_results,
        combination_size=3,
        top_n=3,
        threshold=6.5
    )
    
    print_results(results, "Migräne")


def test_exhaustion():
    """Test: Erschöpfung"""
    print("\n" + "="*70)
    print("TEST 2: ERSCHÖPFUNG")
    print("="*70)
    
    engine = QuantumSynergyEngine()
    
    # Simulierte Scan-Ergebnisse
    scan_results = {
        "Müdigkeit (chronisch)": 9.0,
        "Erschöpfung (chronisch)": 8.8,
        "Burnout": 7.5,
        "Nebennierenschwäche": 8.2,
        "Cortisol erniedrigt": 7.8,
        "Vitamin B12-Mangel": 8.5,
        "Eisen-Mangel (Anämie)": 7.2,
        "Mitochondrien-Dysfunktion (EMF)": 6.8,
    }
    
    results = engine.find_synergistic_triggers(
        focus="Erschöpfung Burnout",
        scan_results=scan_results,
        combination_size=3,
        top_n=3,
        threshold=6.5
    )
    
    print_results(results, "Erschöpfung / Burnout")


def test_digestion():
    """Test: Verdauung"""
    print("\n" + "="*70)
    print("TEST 3: VERDAUUNGSPROBLEME")
    print("="*70)
    
    engine = QuantumSynergyEngine()
    
    # Simulierte Scan-Ergebnisse
    scan_results = {
        "Blähungen (Meteorismus)": 8.5,
        "Reizdarm-Syndrom (IBS-M)": 7.8,
        "Bauchschmerzen (Unterbauch)": 7.2,
        "SIBO (Small Intestinal Bacterial Overgrowth)": 8.0,
        "Leaky Gut Syndrom": 7.5,
        "Candida albicans": 6.8,
        "Histaminintoleranz": 7.0,
    }
    
    results = engine.find_synergistic_triggers(
        focus="Verdauung Reizdarm",
        scan_results=scan_results,
        combination_size=3,
        top_n=3,
        threshold=6.5
    )
    
    print_results(results, "Verdauungsprobleme / Reizdarm")


def test_statistics():
    """Zeigt Datenbank-Statistiken"""
    print("\n" + "="*70)
    print("DATENBANK-STATISTIKEN")
    print("="*70 + "\n")
    
    engine = QuantumSynergyEngine()
    stats = engine.get_statistics()
    
    print(f"Gesamt-Items:           {stats['total_items']:,}")
    print(f"Gesamt-Gruppen:         {stats['total_groups']}")
    print(f"Ø Items pro Gruppe:     {stats['avg_items_per_group']:.1f}")
    print(f"\nBeispiel-Gruppen:")
    for group in sorted(stats['groups'])[:10]:
        print(f"  • {group}")
    if len(stats['groups']) > 10:
        print(f"  ... und {len(stats['groups']) - 10} weitere")
    
    print(f"\n{'='*70}\n")


def main():
    """Führt alle Tests aus"""
    print("\n" + "="*70)
    print("QUANTUM-SYNERGY TEST SUITE")
    print("="*70)
    
    try:
        # Statistiken
        test_statistics()
        
        # Tests
        test_migraine()
        test_exhaustion()
        test_digestion()
        
        print("\n" + "="*70)
        print("ALLE TESTS ERFOLGREICH ABGESCHLOSSEN!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ FEHLER: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
