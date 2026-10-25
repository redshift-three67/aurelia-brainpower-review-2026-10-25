"""
Fügt Burbur-Pinella manuell zur nutramedix_import_ready.json hinzu.
"""

import json
from pathlib import Path

def add_burbur_pinella():
    json_file = Path("nutramedix_import_ready.json")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Prüfe, ob Burbur-Pinella schon existiert
    existing_names = [item['label'] for item in data]
    if "Burbur-Pinella" in existing_names:
        print("✅ Burbur-Pinella existiert bereits!")
        return
    
    # Erstelle Eintrag
    burbur_pinella = {
        "label": "Burbur-Pinella",
        "category": "phytotherapie_nutramedix",
        "manufacturer": "Nutramedix",
        "source_ref": "NUTRAMEDIX-Kompakt.pdf",
        "internal_logic": {
            "index_indications": [
                "Entgiftung von",
                "Herxheimer-Reaktionen",
                "anti-allergisch",
                "anti-anaphylaktisch",
                "anti-asthmatisch",
                "anti-mikrobiell",
                "anti-parasitär",
                "krampflösend",
                "entzündungshemmend",
                "tumorhemmend",
                "antiviral",
                "harntreibend",
                "entschlackend",
                "entgiftend",
                "verdauungsfördernd"
            ],
            "base_description": "Ist eine Kombination aus zwei Extrakten: BURBUR wird aus den Blättern von Desmodium molliculum, PINELLA wird aus Pimpinella anisum, bekannt als Anis, extrahiert"
        }
    }
    
    # Füge hinzu
    data.append(burbur_pinella)
    
    # Sortiere alphabetisch
    data.sort(key=lambda x: x['label'])
    
    # Speichere
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Burbur-Pinella hinzugefügt! Gesamt: {len(data)} Produkte")

if __name__ == "__main__":
    add_burbur_pinella()
