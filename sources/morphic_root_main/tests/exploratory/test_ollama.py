"""
Test-Script für Ollama LLM Integration.

Testet Beschreibungs-Generierung für verschiedene Items.
"""

from core.llm import get_ollama_client

def test_ollama():
    """Testet Ollama-Verbindung und Beschreibungs-Generierung."""
    
    print("=" * 60)
    print("OLLAMA LLM TEST")
    print("=" * 60)
    
    # Initialisiere Client
    client = get_ollama_client()
    
    if not client or not client.available:
        print("❌ Ollama nicht verfügbar!")
        print("\nBitte starte Ollama:")
        print("  1. Öffne PowerShell")
        print("  2. Führe aus: ollama serve")
        print("  3. In neuer PowerShell: ollama pull phi-3-mini:3.8b")
        return
    
    print(f"✓ Ollama verfügbar: {client.model}")
    print()
    
    # Test-Items
    test_items = [
        ("An Shen Wan", "tcm_rezepturen", [15.56, 30.56]),
        ("Chrom", "orthomolekular_mineralien", [15.05, 25.05]),
        ("L-Glutaminsäure", "orthomolekular_aminosauren", [15.05, 26.05]),
        ("Arnica montana", "homoeopathie_klassisch", [20.57, 26.57]),
        ("Nr. 11 Silicea", "schuessler_12", [18.55, 28.55]),
        ("Vitamin B5", "orthomolekular_vitamine", [18.24, 27.24]),
        ("Chestnut Bud", "bachblueten_38", [16.12, 31.12]),
        ("528 Hz (DNA-Reparatur)", "frequenz_solfeggio", [20.00, 30.00]),
        ("Staphylococcus aureus", "bakterien_fein", [24.07, 26.07]),
        ("Quecksilber", "schwermetalle_tox", [30.50, 45.50]),
    ]
    
    print("Generiere Beschreibungen für 10 Test-Items...")
    print("=" * 60)
    
    for i, (label, group, rates) in enumerate(test_items, 1):
        print(f"\n{i}. {label}")
        print(f"   Gruppe: {group}")
        print(f"   Raten: [{rates[0]:.2f} - {rates[1]:.2f}]")
        
        description = client.generate_description(label, group, rates)
        
        if description:
            print(f"   ✓ Beschreibung: {description}")
        else:
            print(f"   ❌ Keine Beschreibung generiert")
    
    print("\n" + "=" * 60)
    print("TEST ABGESCHLOSSEN")
    print("=" * 60)
    
    # Synergie-Test
    print("\nTeste Synergie-Erklärung...")
    explanation = client.generate_synergy_explanation(
        "An Shen Wan C200",
        "Chestnut Bud",
        [15.56, 30.56],
        [16.12, 31.12],
        0.99
    )
    
    if explanation:
        print(f"✓ Synergie-Erklärung: {explanation}")
    else:
        print("❌ Keine Synergie-Erklärung generiert")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_ollama()
