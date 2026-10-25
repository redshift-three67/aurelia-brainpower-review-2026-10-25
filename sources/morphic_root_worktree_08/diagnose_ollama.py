"""
Ollama Diagnose-Script.
Prüft Ollama-Installation und verfügbare Modelle.
"""

import requests
import json

def diagnose_ollama():
    """Diagnostiziert Ollama-Setup."""
    
    print("=" * 70)
    print("OLLAMA DIAGNOSE")
    print("=" * 70)
    
    base_url = "http://localhost:11434"
    
    # 1. Prüfe Ollama-Server
    print("\n1. Prüfe Ollama-Server...")
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=2)
        if response.status_code == 200:
            print("   ✓ Ollama-Server läuft")
            
            # Zeige verfügbare Modelle
            data = response.json()
            models = data.get("models", [])
            
            if models:
                print(f"\n   Verfügbare Modelle ({len(models)}):")
                for model in models:
                    name = model.get("name", "unknown")
                    size = model.get("size", 0) / (1024**3)  # GB
                    print(f"   - {name} ({size:.2f} GB)")
            else:
                print("   ⚠ Keine Modelle installiert!")
                print("\n   Installiere ein Modell:")
                print("   ollama pull phi-3-mini:3.8b")
        else:
            print(f"   ❌ Ollama-Server antwortet mit Status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Ollama-Server nicht erreichbar!")
        print("\n   Starte Ollama:")
        print("   1. Öffne neue PowerShell")
        print("   2. Führe aus: ollama serve")
        return
    except Exception as e:
        print(f"   ❌ Fehler: {e}")
        return
    
    # 2. Teste API-Endpunkt
    print("\n2. Teste API-Endpunkt...")
    
    # Prüfe, welches Modell verfügbar ist
    if models:
        test_model = models[0].get("name", "")
        print(f"   Teste mit Modell: {test_model}")
        
        try:
            payload = {
                "model": test_model,
                "prompt": "Hallo",
                "stream": False,
                "options": {
                    "num_predict": 10
                }
            }
            
            response = requests.post(
                f"{base_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                generated = result.get("response", "").strip()
                print(f"   ✓ API funktioniert!")
                print(f"   Antwort: {generated[:50]}...")
            else:
                print(f"   ❌ API-Fehler: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"   ❌ API-Test fehlgeschlagen: {e}")
    else:
        print("   ⚠ Kein Modell zum Testen verfügbar")
    
    # 3. Empfohlene Modelle
    print("\n3. Empfohlene Modelle für Morphic Engine:")
    print("   Entwicklungs-Laptop (4 GB RAM):")
    print("   - phi-3-mini:3.8b (3.5 GB) ⭐⭐⭐ EMPFOHLEN")
    print("   - gemma:2b (2 GB)")
    print("   - tinyllama:1.1b (1 GB)")
    print("\n   Linux Server (RTX 4000, 20 GB VRAM):")
    print("   - meditron:70b (40 GB) ⭐⭐⭐⭐⭐ BESTE WAHL")
    print("   - llama3.1:70b (40 GB)")
    print("   - mixtral:8x7b (26 GB)")
    
    print("\n" + "=" * 70)
    print("DIAGNOSE ABGESCHLOSSEN")
    print("=" * 70)


if __name__ == "__main__":
    diagnose_ollama()
