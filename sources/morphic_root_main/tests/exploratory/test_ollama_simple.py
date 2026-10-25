"""Einfacher Ollama-Test."""

import sys
sys.path.insert(0, ".")

try:
    from core.llm import get_ollama_client
    
    print("=" * 60)
    print("OLLAMA TEST")
    print("=" * 60)
    
    client = get_ollama_client()
    
    if client and client.available:
        print(f"✓ Ollama verfügbar: {client.model}")
        
        # Test 1: Einfache Beschreibung
        print("\nTest 1: Beschreibung für 'An Shen Wan'")
        desc = client.generate_description("An Shen Wan", "tcm_rezepturen", [15.56, 30.56])
        print(f"Ergebnis: {desc}")
        
        # Test 2: Beschreibung für 'Chrom'
        print("\nTest 2: Beschreibung für 'Chrom'")
        desc = client.generate_description("Chrom", "orthomolekular_mineralien", [15.05, 25.05])
        print(f"Ergebnis: {desc}")
        
        print("\n✓ TEST ERFOLGREICH!")
    else:
        print("❌ Ollama nicht verfügbar")
        print("\nStarte Ollama:")
        print("  ollama serve")
        
except Exception as e:
    print(f"❌ Fehler: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
