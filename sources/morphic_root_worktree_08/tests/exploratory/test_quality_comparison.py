"""
Qualitätstest: Vergleicht Beschreibungen von verschiedenen Modellen.

Testet 30 repräsentative Items aus verschiedenen Gruppen.
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent))

from core.llm import OllamaClient


# 30 Test-Items aus verschiedenen Gruppen
TEST_ITEMS = [
    # Homöopathie
    ("Arnica montana", "homoeopathie_klassisch", [15.5, 25.5]),
    ("Belladonna", "homoeopathie_klassisch", [20.3, 30.3]),
    ("Nux vomica", "homoeopathie_klassisch", [18.7, 28.7]),
    
    # TCM
    ("An Shen Wan", "tcm_rezepturen", [15.56, 30.56]),
    ("Liu Wei Di Huang Wan", "tcm_rezepturen", [22.4, 35.4]),
    ("Xiao Yao San", "tcm_rezepturen", [18.9, 32.1]),
    
    # Schüssler
    ("Nr. 7 Magnesium phosphoricum", "schuessler", [25.8, 35.8]),
    ("Nr. 11 Silicea", "schuessler", [30.2, 40.2]),
    ("Nr. 5 Kalium phosphoricum", "schuessler", [22.5, 32.5]),
    
    # Mineralien
    ("Magnesium", "orthomolekular_mineralien", [26.58, 41.58]),
    ("Zink", "orthomolekular_mineralien", [28.3, 38.3]),
    ("Selen", "orthomolekular_mineralien", [65.21, 69.21]),
    
    # Vitamine
    ("Vitamin B12", "orthomolekular_vitamine", [35.4, 45.4]),
    ("Vitamin D3", "orthomolekular_vitamine", [28.9, 38.9]),
    ("Vitamin C", "orthomolekular_vitamine", [32.1, 42.1]),
    
    # Aminosäuren
    ("L-Glutaminsäure", "aminosaeuren_detailliert", [15.05, 26.05]),
    ("L-Carnitin", "aminosaeuren_detailliert", [26.01, 29.01]),
    ("L-Arginin", "aminosaeuren_detailliert", [68.81, 79.81]),
    
    # Bakterien
    ("Staphylococcus aureus", "bakterien", [45.2, 55.2]),
    ("Escherichia coli", "bakterien", [38.7, 48.7]),
    ("Helicobacter pylori", "bakterien", [42.3, 52.3]),
    
    # Viren
    ("Epstein-Barr-Virus", "viren", [52.8, 62.8]),
    ("Herpes simplex", "viren", [48.5, 58.5]),
    
    # Meridiane
    ("Leber-Meridian", "meridiane", [12.5, 22.5]),
    ("Nieren-Meridian", "meridiane", [18.3, 28.3]),
    
    # Chakren
    ("Wurzelchakra", "chakren", [8.5, 18.5]),
    ("Herzchakra", "chakren", [15.2, 25.2]),
    
    # Frequenzen
    ("528 Hz (DNA-Reparatur)", "frequenzen_solfeggio", [528.0, 528.0]),
    ("432 Hz (Erdresonanz)", "frequenzen_solfeggio", [432.0, 432.0]),
    
    # Metalle
    ("Quecksilber", "metalle_toxisch", [55.8, 65.8]),
]


def test_model_quality(model_name: str):
    """
    Testet Qualität eines Modells.
    
    Args:
        model_name: Name des Ollama-Modells
    """
    print("=" * 80)
    print(f"QUALITÄTSTEST: {model_name.upper()}")
    print("=" * 80)
    
    # Initialisiere Client
    client = OllamaClient(model=model_name)
    
    if not client.available:
        print(f"\n❌ Modell '{model_name}' nicht verfügbar!")
        print(f"\nInstalliere mit: ollama pull {model_name}")
        return
    
    print(f"\n✓ Modell: {client.model}")
    print(f"✓ Test-Items: {len(TEST_ITEMS)}\n")
    
    results = []
    total_time = 0
    
    for i, (label, group, rates) in enumerate(TEST_ITEMS, 1):
        print(f"[{i}/{len(TEST_ITEMS)}] {label} ({group})")
        
        start = time.time()
        description = client.generate_description(label, group, rates)
        elapsed = time.time() - start
        total_time += elapsed
        
        if description and description != "-":
            print(f"  ✓ ({elapsed:.2f}s) {description}")
            results.append({
                "label": label,
                "group": group,
                "description": description,
                "time": elapsed,
                "length": len(description)
            })
        else:
            print(f"  ❌ Keine Beschreibung generiert")
        
        print()
    
    # Statistiken
    print("=" * 80)
    print("STATISTIKEN")
    print("=" * 80)
    print(f"\nErfolgreich: {len(results)}/{len(TEST_ITEMS)}")
    print(f"Gesamtzeit: {total_time:.1f}s")
    print(f"Durchschnitt: {total_time/len(TEST_ITEMS):.2f}s pro Item")
    
    if results:
        avg_length = sum(r["length"] for r in results) / len(results)
        min_length = min(r["length"] for r in results)
        max_length = max(r["length"] for r in results)
        
        print(f"\nBeschreibungs-Länge:")
        print(f"  Durchschnitt: {avg_length:.0f} Zeichen")
        print(f"  Min: {min_length} Zeichen")
        print(f"  Max: {max_length} Zeichen")
    
    return results


def compare_models():
    """Vergleicht mehrere Modelle."""
    print("\n" + "=" * 80)
    print("MODELL-VERGLEICH")
    print("=" * 80)
    print("\nVerfügbare Modelle werden getestet...\n")
    
    models_to_test = [
        ("tinyllama", "Sehr schnell, einfache Beschreibungen"),
        ("qwen2.5:1.5b", "Schnell + präzise, gute Balance"),
        ("qwen2.5:3b", "Beste Balance Geschwindigkeit/Qualität"),
        ("phi3:latest", "Hohe Qualität, langsamer"),
    ]
    
    all_results = {}
    
    for model_name, description in models_to_test:
        print(f"\n{'='*80}")
        print(f"TEST: {model_name}")
        print(f"Info: {description}")
        print(f"{'='*80}\n")
        
        input("Drücke Enter um zu starten...")
        
        results = test_model_quality(model_name)
        all_results[model_name] = results
        
        print("\n" + "="*80)
        input("Drücke Enter für nächstes Modell...")
    
    # Vergleich
    print("\n" + "=" * 80)
    print("VERGLEICHS-ZUSAMMENFASSUNG")
    print("=" * 80)
    
    for model_name, results in all_results.items():
        if results:
            avg_time = sum(r["time"] for r in results) / len(results)
            avg_length = sum(r["length"] for r in results) / len(results)
            print(f"\n{model_name}:")
            print(f"  Geschwindigkeit: {avg_time:.2f}s pro Item")
            print(f"  Beschreibungs-Länge: {avg_length:.0f} Zeichen")
            print(f"  Erfolgsrate: {len(results)}/{len(TEST_ITEMS)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Qualitätstest für LLM-Modelle")
    parser.add_argument(
        "--model",
        type=str,
        help="Einzelnes Modell testen (z.B. tinyllama, phi3:latest)"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Mehrere Modelle vergleichen"
    )
    
    args = parser.parse_args()
    
    if args.model:
        test_model_quality(args.model)
    elif args.compare:
        compare_models()
    else:
        # Standard: Vergleich
        compare_models()
