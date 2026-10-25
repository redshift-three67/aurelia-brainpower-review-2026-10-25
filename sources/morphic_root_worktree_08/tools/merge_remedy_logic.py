"""
Heel Logic Fusion Tool
Verbindet die saubere Produktliste mit dem therapeutischen Index.
Erstellt die finale Import-Struktur mit "Hidden Logic".
"""

import sys
from pathlib import Path
import json
import re

def normalize_name(name):
    """Normalisiert Namen für den Vergleich (klein, ohne Leerzeichen/Bindestriche)."""
    return re.sub(r'[^a-z0-9]', '', name.lower())

def merge_logic(product_file, index_file, json_details_file):
    print(f"\n🧬 FUSIONIERE LOGIK...")
    print("=" * 70)
    
    # 1. Lade Produkte
    with open(product_file, 'r', encoding='utf-8') as f:
        products = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    print(f"📦 {len(products)} Produkte geladen.")
    
    # 2. Lade Index
    with open(index_file, 'r', encoding='utf-8') as f:
        index_data = json.load(f)
    print(f"📚 {len(index_data)} Indikations-Gruppen geladen.")
    
    # 3. Lade Details (aus Extract-Schritt 1)
    details_map = {}
    if Path(json_details_file).exists():
        with open(json_details_file, 'r', encoding='utf-8') as f:
            raw_details = json.load(f)
            for item in raw_details:
                norm = normalize_name(item['label'])
                details_map[norm] = item['internal_logic']
    print(f"📝 {len(details_map)} Detail-Infos geladen.")

    # 4. Fusion
    final_data = []
    
    for product_name in products:
        norm_name = normalize_name(product_name)
        found_indications = set()
        
        # Suche im Index (Reverse Lookup)
        for indication, remedies in index_data.items():
            # Ignoriere Indikationen, die wie Mittelnamen aussehen oder Müll sind
            if len(indication) < 4 or "Injeele" in indication or "Therapie" in indication:
                continue
                
            for remedy in remedies:
                rem_name = remedy['name']
                # Fuzzy Match: Wenn der Index-Name im Produktnamen enthalten ist oder andersrum
                # Aber Vorsicht: "Traumeel" matcht "Traumeel S", aber "Heel" matcht alles mit Heel.
                
                # Wir vergleichen normalisiert
                norm_rem = normalize_name(rem_name)
                
                # Striker Match: 
                if norm_rem == norm_name:
                    found_indications.add(indication)
                # Fallback: "Traumeel" in Index -> "Traumeel S" in Liste
                elif norm_rem in norm_name and len(norm_rem) > 4:
                     found_indications.add(indication)
                     
        # Details aus Extraktion holen
        logic = details_map.get(norm_name, {"usage": "", "composition": ""})
        
        # Kombiniere alles
        # Wir packen Indikationen in 'usage' dazu, damit die Vektor-Suche sie findet
        # Aber wir markieren sie als INTERN
        
        final_entry = {
            "label": product_name,
            "category": "homotoxikologie_heel",
            "manufacturer": "Heel",
            "source_ref": "Antihomotoxikologie.pdf",
            "internal_logic": {
                "extracted_usage": logic.get('usage', ''),
                "composition": logic.get('composition', ''),
                "index_indications": list(found_indications)
            }
        }
        final_data.append(final_entry)
        
    # Zeige Statistik
    with_indications = sum(1 for p in final_data if p['internal_logic']['index_indications'])
    print(f"✅ {with_indications} von {len(final_data)} Produkten haben Indikationen aus dem Index gefunden.")
    
    # Speichern
    out_file = Path("heel_import_ready.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
        
    print(f"💾 Bereit für Import: {out_file}")

if __name__ == "__main__":
    merge_logic("heel_products_clean.txt", "heel_index_debug.json", "heel_products_debug.json")
